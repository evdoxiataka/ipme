from ..interfaces.cell import Cell
from ..utils.stats import find_x_range

import numpy as np
import threading
from abc import abstractmethod

class ScatterCell(Cell):
    def __init__(self, vars, control):
        """
            Parameters:
            --------
                vars            A List of variableNames of the model.
                control         A Control object
            Sets:
            -----
                x_range         Figures axes x_range
        """
        self.samples = {}
        self.contours = {}
        self._all_samples = {}
        self.x_range = {}
        Cell.__init__(self, vars, control)

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
            # compute x_range
            self.x_range[var] = {}
            # self.x_range[var][space] = find_x_range(self._all_samples[var][space])
            self.x_range[var][space] = find_x_range(self.get_samples_for_cur_idx_dims_values(var, space))

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

