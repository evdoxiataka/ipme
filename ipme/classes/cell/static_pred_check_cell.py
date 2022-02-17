from ipme.interfaces.predictive_check_cell import PredictiveCheckCell
from .utils.cell_pred_check_handler import CellPredCheckHandler
from ..cell.utils.cell_widgets import CellWidgets

class StaticPredCheckCell(PredictiveCheckCell):
    def __init__(self, vars, control, function = 'min'):
        """
            Parameters:
            --------
                vars            A List of variableNames of the model.
                control         A Control object
                function        A String in {"min","max","mean","std"}.
        """
        self.func = function
        PredictiveCheckCell.__init__(self, vars, control)

    def initialize_cds(self, space):        
        CellPredCheckHandler.initialize_cds_static(self, space)

    def initialize_fig(self, space):
        CellPredCheckHandler.initialize_fig_static(self, space)

    def initialize_glyphs(self, space):
        CellPredCheckHandler.initialize_glyphs_static(self, space)

    def widget_callback(self, attr, old, new, w_title, space):
        CellWidgets.widget_callback_static(self, attr, old, new, w_title, space)

    def update_cds(self, space):
        CellPredCheckHandler.update_cds_static(self, space)

