from ..interfaces.cell import Cell
from ..utils.functions import find_indices
from ..utils.stats import find_x_range

import threading
from functools import partial

class VariableCell(Cell):
    def __init__(self, name, control):
        """
            Parameters:
            --------
                name            A String within the set {"<variableName>"}.
                control         A Control object
        """
        self.source = {}
        self.selection = {}
        self.sel_samples = {}
        self.reconstructed = {}
        self.samples = {}
        self._all_samples = {}
        self.x_range = {}
        Cell.__init__(self, name, control)

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

    ## SELECTIONBOX INTERACTION
    def sample_inds_callback(self, space, attr, old, new):
        """
            Updates cds when indices of selected samples -- Cell._sample_inds--
            are updated.
        """
        self.ic.add_selection_threads(space, threading.Thread(target = self._sample_inds_thread, args = (space,), daemon = True))
        self.ic.sel_lock_event.set()

    def _sample_inds_thread(self, space):
    #     if self._mode == 'i':
    #         self._update_cds_interactive(space)
    #     elif self._mode == 's':
    #         self._update_cds_static(space)
        self.update_cds(space)

    ## Selection Box drawn
    def selectionbox_callback(self, space, event):
        """
            Callback called when selection box is drawn.
        """
        xmin = event.geometry['x0']
        xmax = event.geometry['x1']
        self.ic._set_selection(self.name, space, (xmin, xmax), self.cur_idx_dims_values)
        for sp in self.spaces:
            samples = self.samples[sp].data['x']
            # self._selectionbox_space_thread(sp, samples, xmin, xmax)
            self.ic.add_space_threads(threading.Thread(target = partial(self._selectionbox_space_thread, sp, samples, xmin, xmax), daemon = True))
        self.ic.space_threads_join()

    def _selectionbox_space_thread(self, space, samples, xmin, xmax):
        x_range = self.ic.get_var_x_range(space, self.name)
        if len(x_range):
            self._update_selection_cds(space, x_range[0], x_range[1])
        else:
            if self._type == "Discrete":
                self.selection[space].data = dict(x = np.array([]), y = np.array([]), y0 = np.array([]))
            else:
                self.selection[space].data = dict(x = np.array([]), y = np.array([]))
        inds = find_indices(samples, lambda e: xmin <= e <= xmax, xmin, xmax)
        self.ic.set_sel_var_inds(space, self.name, inds)
        self.compute_intersection_of_samples(space)
        # self._ic._selection_threads_join(space)

    ##
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

    def get_max_prob(self, space):
        """
            Gets highest point --max probability-- of cds
        """
        max_sv = -1
        max_rv = -1
        if self.source[space].data['y'].size:
            max_sv = self.source[space].data['y'].max()
        if self.reconstructed[space].data['y'].size:
            max_rv = self.reconstructed[space].data['y'].max()
        return max([max_sv,max_rv])

