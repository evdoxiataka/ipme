from ipme.interfaces.scatter_cell import ScatterCell
from .utils.cell_scatter_handler import CellScatterHandler
from ..cell.utils.cell_widgets import CellWidgets

class InteractiveScatterCell(ScatterCell):
    def __init__(self, vars, control):
        """
            Parameters:
            --------
                name            A String within the set {"<variableName>"}.
                control         A Control object
        """
        self.sel_samples_view = {}
        self.non_sel_samples_view = {}
        ScatterCell.__init__(self, vars, control)

    def initialize_cds(self, space):
        CellScatterHandler.initialize_cds_interactive(self, space)

    def initialize_fig(self, space):
        CellScatterHandler.initialize_fig_interactive(self, space)

    def initialize_glyphs(self, space):
        CellScatterHandler.initialize_glyphs_interactive(self, space)

    def widget_callback(self, attr, old, new, w_title, space):
        CellWidgets.widget_callback_interactive(self, attr, old, new, w_title, space)

    def update_cds(self, space):
        CellScatterHandler.update_cds_interactive(self, space)

    ## ONLY FOR INTERACTIVE CASE
    def update_source_cds(self, space):
        CellScatterHandler.update_source_cds_interactive(self, space)

    def update_sel_samples_cds(self, space):
        CellScatterHandler.update_sel_samples_cds_interactive(self, space)
