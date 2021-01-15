from ..interfaces.cell import Cell
from ..utils.stats import find_x_range
from ..utils.constants import BORDER_COLORS

from bokeh.models import  Toggle, Div

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
        """
        self.source = {}
        self.samples = {}
        self._all_samples = {}
        Cell.__init__(self, name, control)
        self._toggle = {}
        self._div = {}
        self._initialize_toggle_div()

    ## DATA
    def get_samples(self, space):
        """
            Retrieves MCMC samples of <space> into a numpy.ndarray and
            sets an entry into self._all_samples Dict.
        """
        space_gsam = space
        if self._data.get_var_type(self.name) == "observed":
            if space == "posterior" and "posterior_predictive" in self._data.get_spaces():
                space_gsam = "posterior_predictive"
            elif space == "prior" and "prior_predictive" in self._data.get_spaces():
                space_gsam = "prior_predictive"
        self._all_samples[space] = self._data.get_samples(self.name, space_gsam).T
        # compute x_range
        self.x_range[space] = find_x_range(self._all_samples[space])

    def get_data_for_cur_idx_dims_values(self, space):
        """
            Returns a numpy.ndarray of the MCMC samples of the <name>
            parameter for current index dimensions values.

            Returns:
            --------
                A numpy.ndarray.
        """
        if space in self._all_samples:
            data =  self._all_samples[space]
        else:
            raise ValueError
        for dim_name, dim_value in self.cur_idx_dims_values.items():
            data = data[dim_value]
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

    @abstractmethod
    def update_source_cds(self, space):
        pass

    @abstractmethod
    def update_selection_cds(self, space, xmin, xmax):
        pass

    @abstractmethod
    def update_reconstructed_cds(self, space):
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
        sel_var_inds = self.ic.get_sel_var_inds()
        sp_keys = [k for k in sel_var_inds if k[0] == space]
        if len(sp_keys)>1:
            sets = []
            for i in range(0, len(sp_keys)):
                sets.append(set(sel_var_inds[sp_keys[i]]))
            union = set.intersection(*sorted(sets, key = len))
            self.ic.set_sample_inds(space, dict(inds = list(union)))
        elif len(sp_keys) == 1:
            self.ic.set_sample_inds(space, dict(inds = sel_var_inds[sp_keys[0]]))
        else:
            self.ic.set_sample_inds(space, dict(inds = []))

    def _initialize_toggle_div(self):
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
