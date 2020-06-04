from .data import Data
from ..interfaces.grid import Cell
from .graph import Graph
from .predictive_ckecks import PredictiveChecks

import panel as pn

class Diagram():
    def __init__(self, data_path, predictive_checks = []):
        """
            Parameters:
            --------
                data_path               A String of the zip file with the inference data.           
                predictive_checks       A List of observed variables to plot predictive checks.
            Sets:
            --------
                _data                   A Data object.
                _plotted_widgets        A List of widget objects to be plotted.
                _plot                   A plot object to visualize grid.
        """
        self._data = Data(data_path) 
        self._pred_checks = predictive_checks
        Cell._data = self._data
        self._plot = None
        self._create_plot()

    def _create_plot(self):
        """
            Creates one Tab per space and extra user-defined plots.

            Sets:
            --------
                - "self._plot" (bokeh) visualization object.
        """ 
        tabs = pn.Tabs(sizing_mode='stretch_both')#sizing_mode='stretch_both'
        ## Tabs for prior-posterior graph
        g = Graph(self._data)
        g_grids = g.get_grids()
        g_plotted_widgets = g.get_plotted_widgets()
        for space in g_grids:
            g_col = pn.Column(g_grids[space])
            if space in g_plotted_widgets:
                w_col = pn.Column(pn.WidgetBox(*g_plotted_widgets[space], sizing_mode='scale_both'),width_policy='max', max_width=300, width=250)
                tabs.append((space, pn.Row(w_col, g_col)))#, height_policy='max', max_height=800
            else:
                tabs.append((space, pn.Row(g_col)))
        ## Tabs for predictive checks
        if self._pred_checks:
            pc_grids = PredictiveChecks(self._data,self._pred_checks).get_grids()
            for var in pc_grids:
                for space in pc_grids[var]:
                    g_col = pn.Column(pc_grids[var][space])
                    tabs.append((var+'_'+space+'_predictive_checks', pn.Row(g_col)))
        #tabs.append((space+'_predictive_checks', pn.Row(c.get_plot(space,add_info=False), sizing_mode='stretch_both')))
        self._plot = tabs

    def get_plot(self):
        return self._plot