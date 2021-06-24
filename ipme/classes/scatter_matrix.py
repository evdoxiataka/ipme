from .data.data import Data
from .grid.scatter_matrix_grid import ScatterMatrixGrid
from .interaction_control.interaction_control import IC

import panel as pn

class ScatterMatrix():
    def __init__(self, data_path, mode = "i", vars = [], spaces = 'all'):
        """
            Parameters:
            --------
                data_path               A String of the zip file with the inference data.
                mode                    A String in {'i','s'}: defines the type of diagram
                                        (interactive or static).
                vars                    A List of model variables to be included in the plot.
                spaces                  A List of spaces to be included in graph
            Sets:
            --------
                _mode                   A String in {"i","s"}, "i":interactive, "s":static.
                _scatter_matrix         A Panel component object to visualize model's scatter matrix.
        """
        self.ic = IC(Data(data_path))
        if mode not in ["s","i"]:
            raise ValueError("ValueError: mode should take a value in {'i','s'}")
        self._mode = mode
        self._vars = vars
        self._spaces = spaces
        self._scatter_matrix_grid = self._create_scatter_matrix_grid()
        self._scatter_matrix = self._create_scatter_matrix()

    def _create_scatter_matrix_grid(self):
        """
            Creates a ScatterMatrixGrid object representing the model as a
            collection of Panel grids (one per space) and a
            collection of plotted widges.
        """
        return ScatterMatrixGrid(self.ic, self._mode, self._vars, self._spaces)

    def _create_scatter_matrix(self):
        """
            Creates one Tab per space (posterior, prior) presenting the scatter matrix.
        """
        tabs = pn.Tabs(sizing_mode='stretch_both')#sizing_mode='stretch_both'
        ## Tabs for prior-posterior scatter matrix
        g_grids = self._scatter_matrix_grid.get_grids()
        g_plotted_widgets = self._scatter_matrix_grid.get_plotted_widgets()
        for space in g_grids:
            g_col = pn.Column(g_grids[space])
            if space in g_plotted_widgets:
                widgetBox = pn.WidgetBox(*list(g_plotted_widgets[space].values()),sizing_mode = 'scale_both')
                w_col = pn.Column(widgetBox, width_policy='max', max_width=300, width=250)
                tabs.append((space, pn.Row(w_col, g_col)))#, height_policy='max', max_height=800
            else:
                tabs.append((space, pn.Row(g_col)))
        return tabs

    def set_coordinates(self, dim, options, value):
        self.ic.set_coordinates(self._scatter_matrix_grid, dim, options, value)

    def get_selection_interactions(self):
        return self.ic.get_selection_interactions()

    def get_widgets_interactions(self):
        return self.ic.get_widgets_interactions()

    def get_scatter_matrix(self):
        return self._scatter_matrix

    def get_scatter_matrix_grid(self):
        return self._scatter_matrix_grid

    # def get_pred_checks_grid(self):
    #     return self._create_pred_checks_grid
