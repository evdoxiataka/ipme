from ipme.interfaces.variable_cell import VariableCell
from .utils.cell_discrete_handler import CellDiscreteHandler
from ..cell.utils.cell_widgets import CellWidgets

from ipme.utils.functions import get_stratum_range, find_indices

class StaticDiscreteCell(VariableCell):
    def __init__(self, name, control):
        """
            Parameters:
            --------
                name            A String within the set {"<variableName>"}.
                control         A Control object
        """
        VariableCell.__init__(self, name, control)

    def initialize_cds(self, space):
        CellDiscreteHandler.initialize_cds_static(self, space)

    def initialize_fig(self, space):
        CellDiscreteHandler.initialize_fig_static(self, space)

    def initialize_glyphs(self, space):
        CellDiscreteHandler.initialize_glyphs_static(self, space)

    def widget_callback(self, attr, old, new, w_title, space):
        CellWidgets.widget_callback_static(self, attr, old, new, w_title, space)

    def update_cds(self, space):
        CellDiscreteHandler.update_cds_static(self, space)

    ## ONLY FOR STATIC CASE
    def set_stratum(self, space, stratum = 0):
        """
            Sets selection by spliting the ordered sample set
            in 4 equal-sized subsets.
        """
        samples = self.get_samples_for_cur_idx_dims_values(space)
        xmin,xmax = get_stratum_range(samples, stratum)
        inds = find_indices(samples, lambda e: xmin <= e <= xmax, xmin, xmax)
        self.ic.set_sel_var_inds(space, self.name, inds)
        self.compute_intersection_of_samples(space)
        return (xmin,xmax)
