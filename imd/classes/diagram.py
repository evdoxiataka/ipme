from .data import Data
from ..interfaces.cell import Cell
from .graph import Graph
from .predictive_ckecks import PredictiveChecks

import panel as pn

class Diagram():
    def __init__(self, data_path, mode = "i", predictive_checks = []):
        """
            Parameters:
            --------
                data_path               A String of the zip file with the inference data.  
                mode                    A String in {'i','s'}: defines the type of diagram 
                                        (interactive or static).         
                predictive_checks       A List of observed variables to plot predictive checks.
            Sets:
            --------
                _data                   A Data object.
                _mode                   A String in {"i","s"}, "i":interactive, "s":static.
                _plotted_widgets        A List of widget objects to be plotted.
                _diagram                A Panel component object to visualize diagram.
        """
        self._data = Data(data_path) 
        if mode not in ["s","i"]:
            raise ValueError("ValueError: mode should take a value in {'i','s'}")
        self._mode = mode
        self._pred_checks = predictive_checks
        Cell._data = self._data
        self._graph = self._create_graph()
        self._predictive_checks_grid = self._create_pred_checks_grid()
        self._diagram = self._create_diagram()     
        

    def _create_graph(self):
        """
            Creates a Graph object representing the model as a 
            collection of Panel grids (one per space) and a 
            collection of plotted widges.

            Sets:
            --------
                _graph      A Graph object.
        """ 
        return Graph(self._data, self._mode)

    def _create_pred_checks_grid(self):
        """
            Creates a PredictiveChecks object representing the model's 
            predictive checks for min, max, mean, std of predictions as a 
            collection of Panel grids (one per space) and a 
            collection of plotted widges.

            Sets:
            --------
                _predictive_checks_grid      A PredictiveChecks object.
        """ 
        return PredictiveChecks(self._data, self._mode, self._pred_checks)

    def _create_diagram(self):
        """
            Creates one Tab per space presenting the space interactive diagram.

            Sets:
            --------
                _diagram (Panel) visualization object.
        """ 
        tabs = pn.Tabs(sizing_mode='stretch_both')#sizing_mode='stretch_both'
        ## Tabs for prior-posterior graph
        g_grids = self._graph.get_grids()
        g_plotted_widgets = self._graph.get_plotted_widgets()
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

    def get_diagram(self):
        return self._diagram

    def get_graph(self):
        return self._graph

    def get_pred_checks_grid(self):
        return self._create_pred_checks_grid