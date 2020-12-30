from ..interfaces.cell import Cell
from ..utils.functions import *
from ..utils.stats import find_x_range
from ..utils.constants import COLORS, BORDER_COLORS, PLOT_HEIGHT, PLOT_WIDTH, SIZING_MODE

from functools import partial
import threading

from bokeh.plotting import figure

class VariableCell(Cell):
    def __init__(self, name, mode, control):
        """
            Parameters:
            --------
                name            A String within the set {"<variableName>"}.
                mode            A String in {"i","s"}, "i":interactive, "s":static.
                control         A Control object
            Sets:
            --------
                _source
                _selection
                _reconstructed
                _samples
        """
        self._source = {}
        self._selection = {}
        self._reconstructed = {}
        self._samples = {}
        self._all_samples = {}
        self._x_range = {}
        Cell.__init__(self, name, mode, control)

    def _get_samples(self, space):
        """
            Retrieves MCMC samples of <space> into a numpy.ndarray and
            sets an entry into self._all_samples Dict.
        """
        space_gsam = space
        if self._data.get_var_type(self._name) == "observed":
            if space == "posterior" and "posterior_predictive" in self._data.get_spaces():
                space_gsam = "posterior_predictive"
            elif space == "prior" and "prior_predictive" in self._data.get_spaces():
                space_gsam = "prior_predictive"
        self._all_samples[space] = self._data.get_samples(self._name, space_gsam).T
        # compute x_range
        self._x_range[space] = find_x_range(self._all_samples[space])

    def _get_data_for_cur_idx_dims_values(self, space):
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
        for dim_name,dim_value in self._cur_idx_dims_values.items():
            data = data[dim_value]
        return np.squeeze(data).T

    def _register_events(self, space):
        pass

    def _widgets_update(self, space):
        pass

    def initialize_fig(self, space):
        pass

    def initialize_cds(self, space):
        pass

    def initialize_glyphs(self, space):
        pass

    def _initialize_plot(self):
        for space in self._spaces:
            self._get_samples(space)
            self.initialize_cds(space)
            self.initialize_fig(space)
            self.initialize_glyphs(space)

    def _widget_callback(self, attr, old, new, w_title, space):
        pass

        ## Update samples indeces
    def _sample_inds_callback(self, space, attr, old, new):
        """
            Updates cds when indices of selected samples -- Cell._sample_inds--
            are updated.
        """
    #     # self._control._add_selection_threads(space,threading.Thread(target=self._sample_inds_thread, args=(space,), daemon=True))
    #     # self._control._sel_lock_event.set()

    # # def _sample_inds_thread(self,space):
    #     if self._mode == 'i':
    #         self._update_cds_interactive(space)
    #     elif self._mode == 's':
    #         self._update_cds_static(space)
    self._update_cds(space)

    ## Selection Box drawn
    def _selectionbox_callback(self, space, event):
        """
            Callback called when selection box is drawn.
        """
        xmin = event.geometry['x0']
        xmax = event.geometry['x1']
        self._control._set_selection(self._name, space, (xmin,xmax), self._cur_idx_dims_values)
        for sp in self._spaces:
            samples = self._samples[sp].data['x']
            self._selectionbox_space_thread(sp, samples, xmin, xmax)
            # self._control._add_space_threads(threading.Thread(target = partial(self._selectionbox_space_thread, sp, samples, xmin, xmax), daemon=True))
        # self._control._space_threads_join()

    def _selectionbox_space_thread(self, space, samples, xmin, xmax):
        x_range = self._control._get_var_x_range(space, self._name)
        if len(x_range):
            self._update_selection_cds(space, x_range[0], x_range[1])
        else:
            if self._type == "Discrete":
                self._selection[space].data = dict(x = np.array([]), y = np.array([]), y0 = np.array([]))
            else:
                self._selection[space].data=dict(x=np.array([]), y = np.array([]))
        inds = find_indices(samples, lambda e: e >= xmin and e<= xmax, xmin, xmax)
        self._control._set_sel_var_inds(space, self._name, inds)
        self._compute_intersection_of_samples(space)
        # self._control._selection_threads_join(space)

    ##
    def _compute_intersection_of_samples(self,space):
        """
            Computes intersection of sample points based on user's
            restrictions per parameter.
        """
        sel_var_inds = self._control._get_sel_var_inds()
        sp_keys = [k for k in sel_var_inds if k[0]==space]
        if len(sp_keys)>1:
            sets = []
            for i in range(0, len(sp_keys)):
                sets.append(set(sel_var_inds[sp_keys[i]]))
            union = set.intersection(*sorted(sets, key=len))
            self._control._set_sample_inds(space, dict(inds=list(union)))
        elif len(sp_keys) == 1:
            self._control._set_sample_inds(space, dict(inds = sel_var_inds[sp_keys[0]]))
        else:
            self._control._set_sample_inds(space, dict(inds=[]))

    def _get_max_prob(self, space):
        """
            Gets highest point --max probability-- of cds
        """
        max_sv = -1
        max_rv = -1
        if self._source[space].data['y'].size:
            max_sv = self._source[space].data['y'].max()
        if self._reconstructed[space].data['y'].size:
            max_rv = self._reconstructed[space].data['y'].max()
        return max([max_sv,max_rv])

    ## Update CDS
    def _update_cds(self, space):
        pass

    def _update_source_cds(self, space):
        pass

    def _update_selection_cds(self, space, xmin, xmax):
        pass

    def _update_reconstructed_cds(self, space):
        pass
