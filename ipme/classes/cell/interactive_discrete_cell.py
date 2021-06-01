from ipme.interfaces.variable_cell import VariableCell
from .utils.cell_discrete_handler import CellDiscreteHandler
from .utils.cell_clear_selection import CellClearSelection
from ..cell.utils.cell_widgets import CellWidgets

class InteractiveDiscreteCell(VariableCell):
    def __init__(self, name, control):
        """
            Parameters:
            --------
                name            A String within the set {"<variableName>"}.
                control         A Control object
        """
        self.selection = {}
        self.sel_samples = {}
        self.reconstructed = {}
        self.clear_selection = {}
        VariableCell.__init__(self, name, control)

    def initialize_cds(self, space):
        CellDiscreteHandler.initialize_cds_interactive(self, space)

    def initialize_fig(self, space):
        CellDiscreteHandler.initialize_fig_interactive(self, space)

    def initialize_glyphs(self, space):
        CellDiscreteHandler.initialize_glyphs_interactive(self, space)
        CellClearSelection.initialize_glyphs_x_button(self, space)

    def widget_callback(self, attr, old, new, w_title, space):
        CellWidgets.widget_callback_interactive(self, attr, old, new, w_title, space)

    def update_cds(self, space):
        CellDiscreteHandler.update_cds_interactive(self, space)

    ## ONLY FOR INTERACTIVE CASE
    def update_source_cds(self, space):
        CellDiscreteHandler.update_source_cds_interactive(self, space)

    def update_selection_cds(self, space, xmin, xmax):
        CellDiscreteHandler.update_selection_cds_interactive(self, space, xmin, xmax)

    def update_reconstructed_cds(self, space):
        CellDiscreteHandler.update_reconstructed_cds_interactive(self, space)
