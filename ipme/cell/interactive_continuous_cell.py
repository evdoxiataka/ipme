from ..interfaces.variable_cell import VariableCell
from .utils.cell_continuous_handler import CellContinuousHandler
from .utils.cell_clear_selection import CellClearSelection
from ..cell.utils.cell_widgets import CellWidgets

class InteractiveContinuousCell(VariableCell):
    def __init__(self, name, control):
        """
            Parameters:
            --------
                name            A String within the set {"<variableName>"}.
                control         A Control object
        """
        self.clear_selection = {}
        VariableCell.__init__(self, name, control)

    def initialize_cds(self, space):
        CellContinuousHandler.initialize_cds_interactive(self, space)

    def initialize_fig(self, space):
        CellContinuousHandler.initialize_fig_interactive(self, space)

    def initialize_glyphs(self, space):
        CellContinuousHandler.initialize_glyphs_interactive(self, space)
        CellClearSelection.initialize_glyphs_x_button(self, space)

    def widget_callback(self, attr, old, new, w_title, space):
        CellWidgets.widget_callback_interactive(self, attr, old, new, w_title, space)

    def update_cds(self, space):
        CellContinuousHandler.update_cds_interactive(self, space)

    ## ONLY FOR INTERACTIVE CASE
    def update_source_cds(self, space):
        CellContinuousHandler.update_source_cds_interactive(self, space)

    def update_selection_cds(self, space, xmin, xmax):
        CellContinuousHandler.update_selection_cds_interactive(self, space, xmin, xmax)

    def update_reconstructed_cds(self, space):
        CellContinuousHandler.update_reconstructed_cds_interactive(self, space)
