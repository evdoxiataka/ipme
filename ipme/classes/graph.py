from .data.data import Data
from .grid.graph_grid import GraphGrid
from .grid.predictive_ckecks_grid import PredictiveChecksGrid
from .interaction_control.interaction_control import IC

import panel as pn

class Graph():
    def __init__(self, data_path, mode = "i", vars = 'all', predictive_checks = []):
        """
            Parameters:
            --------
                data_path               A String of the zip file with the inference data.
                mode                    A String in {'i','s'}: defines the type of diagram
                                        (interactive or static).
                vars                    A List of variables to be presented in the graph
                predictive_checks       A List of observed variables to plot predictive checks.
            Sets:
            --------
                _mode                   A String in {"i","s"}, "i":interactive, "s":static.
                _graph                  A Panel component object to visualize model's graoh.
        """
        self.ic = IC(Data(data_path))
        if mode not in ["s","i"]:
            raise ValueError("ValueError: mode should take a value in {'i','s'}")
        self._mode = mode
        self._vars = vars
        self._pred_checks = predictive_checks
        self._graph_grid = self._create_graph_grid()
        self._predictive_checks_grid = self._create_pred_checks_grid()
        self._graph = self._create_graph()

    def _create_graph_grid(self):
        """
            Creates a GraphGrid object representing the model as a
            collection of Panel grids (one per space) and a
            collection of plotted widges.
        """
        return GraphGrid(self.ic, self._mode, self._vars)

    def _create_pred_checks_grid(self):
        """
            Creates a PredictiveChecks object representing the model's
            predictive checks for min, max, mean, std of predictions as a
            collection of Panel grids (one per space) and a
            collection of plotted widges.
        """
        return PredictiveChecksGrid(self.ic, self._mode, self._pred_checks)

    def _create_graph(self):
        """
            Creates one Tab per space (posterior, prior) presenting the graph.
        """
        tabs = pn.Tabs(sizing_mode='stretch_both')#sizing_mode='stretch_both'
        ## Tabs for prior-posterior graph
        g_grids = self._graph_grid.get_grids()
        g_plotted_widgets = self._graph_grid.get_plotted_widgets()
        for space in g_grids:
            g_col = pn.Column(g_grids[space])
            if space in g_plotted_widgets:
                widgetBox = pn.WidgetBox(*list(g_plotted_widgets[space].values()),sizing_mode = 'scale_both')
                w_col = pn.Column(widgetBox, width_policy='max', max_width=300, width=250)
                tabs.append((space, pn.Row(w_col, g_col)))#, height_policy='max', max_height=800
            else:
                tabs.append((space, pn.Row(g_col)))
        ## Tabs for predictive checks
        if self._pred_checks:
            pc_grids = self._predictive_checks_grid.get_grids()
            for var in pc_grids:
                for space in pc_grids[var]:
                    g_col = pn.Column(pc_grids[var][space])
                    tabs.append((var+'_'+space+'_predictive_checks', pn.Row(g_col)))
        #tabs.append((space+'_predictive_checks', pn.Row(c.get_plot(space,add_info=False), sizing_mode='stretch_both')))
        return tabs

    def set_coordinates(self, dim, options, value):
        self.ic.set_coordinates(self._graph_grid, dim, options, value)
            # try:
            #     if coord_name in self.cells_widgets:
            #         # space_widgets = self.cells_widgets[coord_name]
            #         for space in self.cells_widgets[coord_name]:
            #             c_id_list = self.cells_widgets[coord_name][space]
            #             for c_id in c_id_list:
            #                 w = self.cells[c_id].get_widget(space, coord_name)
            #                 # old_v = w.value
            #                 w.value = new_val
            #                 w.trigger('value', new_val, new_val)
            # except IndexError:
            #     raise IndexError()

    def get_selection_interactions(self):
        return self.ic.get_selection_interactions()

    def get_widgets_interactions(self):
        return self.ic.get_widgets_interactions()

    def get_graph(self):
        return self._graph

    def get_graph_grid(self):
        return self._graph_grid

    def get_pred_checks_grid(self):
        return self._create_pred_checks_grid
