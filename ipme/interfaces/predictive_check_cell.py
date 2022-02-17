from ..interfaces.cell import Cell

import threading
from abc import abstractmethod

class PredictiveCheckCell(Cell):
    def __init__(self, name, control):
        """
            Parameters:
            --------
                name            A String within the set {"<variableName>"}.
                control         An InteractiveControl object
            Sets:
            --------
                _func
                _source
                _reconstructed
                _samples
                _seg

        """
        self.name = name
        self.source = {}
        self.reconstructed = {}
        self.samples = {}
        self.seg = {}
        self.pvalue = {}
        self.pvalue_rec = {}
        Cell.__init__(self, [name], control)

    ## DATA
    def get_samples_for_cur_idx_dims_values(self, space):
        """
            Returns the observed data and predictive samples of the observed variable
            <self._name> in space <space>.

            Returns:
            --------
                A Tuple (data,samples): data-> observed data and samples-> predictive samples.
        """
        data = self.ic.data.get_samples(self.name, 'observed_data')
        if self.ic.data.get_var_type(self.name) == "observed":
            if space == "posterior" and "posterior_predictive" in self.ic.data.get_spaces():
                space="posterior_predictive"
            elif space == "prior" and "prior_predictive" in self.ic.data.get_spaces():
                space="prior_predictive"
        samples = self.ic.data.get_samples(self.name, space)
        return data, samples

    ## INITIALIZATIONS
    def _initialize_plot(self):
        for space in self.spaces:
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
