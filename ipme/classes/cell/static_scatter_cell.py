from ipme.interfaces.scatter_cell import ScatterCell
from .utils.cell_scatter_handler import CellScatterHandler
from ..cell.utils.cell_widgets import CellWidgets

class StaticScatterCell(ScatterCell):
    def __init__(self, vars, control):
        """
            Parameters:
            --------
                vars            A List of variableNames of the model.
                control         A Control object
        """
        ScatterCell.__init__(self, vars, control)

    def initialize_cds(self, space):
        CellScatterHandler.initialize_cds_static(self, space)

    def initialize_fig(self, space):
        CellScatterHandler.initialize_fig_static(self, space)

    def initialize_glyphs(self, space):
        CellScatterHandler.initialize_glyphs_static(self, space)

    def widget_callback(self, attr, old, new, w_title, space):
        CellWidgets.widget_callback_static(self, attr, old, new, w_title, space)

    def update_cds(self, space):
        CellScatterHandler.update_cds_static(self, space)

