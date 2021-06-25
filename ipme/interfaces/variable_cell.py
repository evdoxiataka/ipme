from ..interfaces.cell import Cell
from ..utils.stats import find_x_range
from ..utils.constants import BORDER_COLORS

from bokeh.models import  Toggle, Div
from bokeh.layouts import layout
from bokeh.io.export import get_screenshot_as_png

import numpy as np
import threading
from abc import abstractmethod

class VariableCell(Cell):
    def __init__(self, name, control):
        """
            Parameters:
            --------
                name            A String within the set {"<variableName>"}.
                control         A Control object
            Sets:
            -----
                x_range         Figures axes x_range
                _toggle                 A Dict {<space>: (bokeh) toggle button for visibility of figure}.
                _div                    A Dict {<space>: (bokeh) div parameter-related information}.
        """
        self.name = name
        self.source = {}
        self.samples = {}
        self.data = {}
        self._all_samples = {}
        self._all_data = {}
        self.x_range = {}
        Cell.__init__(self, [name], control)
        self._toggle = {}
        self._div = {}
        self._initialize_toggle_div()

    ## DATA
    def get_samples(self, space):
        """
            Retrieves MCMC samples of <space> into a numpy.ndarray and
            sets an entry into self._all_samples Dict.
        """
        for var in self.vars:
            space_gsam = space
            if self._data.get_var_type(var) == "observed":
                if space == "posterior" and "posterior_predictive" in self._data.get_spaces():
                    space_gsam = "posterior_predictive"
                elif space == "prior" and "prior_predictive" in self._data.get_spaces():
                    space_gsam = "prior_predictive"
            if var not in self._all_samples:
                self._all_samples[var] = {}
            self._all_samples[var][space] = self._data.get_samples(var, space_gsam).T
            # get observed data
            data = self._data.get_observations(var)
            if data is not None:
                self._all_data[var] = data
            # compute x_range
            self.x_range[var] = {}
            self.x_range[var][space] = find_x_range(self._all_samples[var][space])

    def get_samples_for_cur_idx_dims_values(self, var_name, space):
        """
            Returns a numpy.ndarray of the MCMC samples of the <name>
            parameter for current index dimensions values.

            Returns:
            --------
                A numpy.ndarray.
        """
        if var_name in self._all_samples:
            data =  self._all_samples[var_name]
            if space in data:
                data = data[space]
            else:
                raise ValueError("cel {}-{}: space {} not in self._all_samples[{}].keys() {}".format(self.vars[0],self.vars[1],space,var_name,data.keys()))
        else:
            raise ValueError("var_name {} not in self._all_samples.keys() {}".format(var_name, self._all_samples.keys()))
        if var_name in self.cur_idx_dims_values:
            for _, dim_value in self.cur_idx_dims_values[var_name].items():
                data = data[dim_value]
        if data.shape == (1,)*len(data.shape):
            return data.flatten()
        else:
            return np.squeeze(data).T

    def get_data_for_cur_idx_dims_values(self, var_name):
        """
            Returns a numpy.ndarray of the observations of the <var_name>
            parameter for current index dimensions values.

            Returns:
            --------
                A numpy.ndarray.
        """
        if var_name in self._all_data:
            data =  self._all_data[var_name]
        else:
            return None
        if var_name in self.cur_idx_dims_values:
            for _, dim_value in self.cur_idx_dims_values[var_name].items():
                data = data[dim_value]
        if data.shape == (1,)*len(data.shape):
            return data.flatten()
        else:
            return np.squeeze(data).T

    ## INITIALIZATION
    def _initialize_plot(self):
        for space in self.spaces:
            self.get_samples(space)
            self.initialize_cds(space)
            self.initialize_fig(space)
            self.initialize_glyphs(space)

    @abstractmethod
    def initialize_fig(self, space):
        pass

    @abstractmethod
    def initialize_cds(self, space):
        pass

    @abstractmethod
    def initialize_glyphs(self, space):
        pass

    ## WIDGETS
    @abstractmethod
    def widget_callback(self, attr, old, new, w_title, space):
        pass

    ## UPDATE
    @abstractmethod
    def update_cds(self, space):
        pass

    def sample_inds_callback(self, space, attr, old, new):
        """
            Updates cds when indices of selected samples -- Cell._sample_inds--
            are updated.
        """
        self.ic.add_selection_threads(space, threading.Thread(target = self._sample_inds_thread, args = (space,), daemon = True))
        self.ic.sel_lock_event.set()

    def _sample_inds_thread(self, space):
        self.update_cds(space)

    def compute_intersection_of_samples(self, space):
        """
            Computes intersection of sample points based on user's
            restrictions per parameter.
        """
        sel_var_inds = self.ic.get_sel_var_inds(space = space)
        sp_keys = list(sel_var_inds.keys())
        inds_list = np.full((len(self.samples[space].data['x']),), False)
        if len(sp_keys)>1:
            sets = []
            for var in sp_keys:
                sets.append(set(sel_var_inds[var]))
            inds_set = set.intersection(*sorted(sets, key = len))
            inds_list[list(inds_set)] = True
        elif len(sp_keys) == 1:
            inds_list[sel_var_inds[sp_keys[0]]] = True
        non_inds_list = list(~inds_list)
        self.ic.set_sample_inds(space, dict(inds = list(inds_list)), dict(non_inds = non_inds_list))

    def _initialize_toggle_div(self):
        """"
            Creates the toggle headers of each variable node.
        """
        for space in self.spaces:
            width = self.plot[space].plot_width
            height = 40
            sizing_mode = self.plot[space].sizing_mode
            label = self.name + " ~ " + self._data.get_var_dist(self.name)
            text = """parents: %s <br>dims: %s"""%(self._data.get_var_parents(self.name), list(self._data.get_idx_dimensions(self.name)))
            if sizing_mode == 'fixed':
                self._toggle[space] = Toggle(label = label,  active = False,
                                             width = width, height = height, sizing_mode = sizing_mode, margin = (0,0,0,0))
                self._div[space] = Div(text = text,
                                       width = width, height = height, sizing_mode = sizing_mode, margin = (0,0,0,0), background = BORDER_COLORS[0] )
            elif sizing_mode == 'scale_width' or sizing_mode == 'stretch_width':
                self._toggle[space] = Toggle(label = label,  active = False,
                                             height = height, sizing_mode = sizing_mode, margin = (0,0,0,0))
                self._div[space] = Div(text = text,
                                       height = height, sizing_mode = sizing_mode, margin = (0,0,0,0), background = BORDER_COLORS[0] )
            elif sizing_mode == 'scale_height' or sizing_mode == 'stretch_height':
                self._toggle[space] = Toggle(label = label,  active = False,
                                             width = width, sizing_mode = sizing_mode, margin = (0,0,0,0))
                self._div[space] = Div(text = text,
                                       width = width, sizing_mode = sizing_mode, margin = (0,0,0,0), background = BORDER_COLORS[0] )
            else:
                self._toggle[space] = Toggle(label = label,  active = False,
                                             sizing_mode = sizing_mode, margin = (0,0,0,0))
                self._div[space] = Div(text = text, sizing_mode = sizing_mode, margin = (0,0,0,0), background = BORDER_COLORS[0] )
            self._toggle[space].js_link('active', self.plot[space], 'visible')

    def get_max_prob(self, space):
        """
            Gets highest point --max probability-- of cds
        """
        max_sv = -1
        max_rv = -1
        if self.source[space].data['y'].size:
            max_sv = self.source[space].data['y'].max()
        if hasattr(self,'reconstructed') and self.reconstructed[space].data['y'].size:
            max_rv = self.reconstructed[space].data['y'].max()
        max_v = max([max_sv,max_rv])
        return  max_v if max_v!=-1 else None

    def get_plot(self, space, add_info = False):
        if space in self.plot:
            if add_info and space in self._toggle and space in self._div:
                return layout([self._toggle[space]], [self._div[space]], [self.plot[space]])
            else:
                return self.plot[space]
        else:
            return None

    def get_screenshot(self, space, add_info=False):
        if space in self.plot:
            if add_info and space in self._toggle and space in self._div:
                return get_screenshot_as_png(layout([self._toggle[space]], [self._div[space]], [self.plot[space]]))
            else:
                return get_screenshot_as_png(self.plot[space])
        else:
            return None
