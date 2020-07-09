from ..interfaces.grid import Grid
from .predictive_ckecks_cell import PredictiveChecksCell
from ..utils.constants import MAX_NUM_OF_COLS_PER_ROW, MAX_NUM_OF_VARS_PER_ROW, COLS_PER_VAR
import panel as pn

class PredictiveChecks(Grid):
    def __init__(self, data_obj, predictive_ckecks = []):
        """
            Parameters:
            --------
                data_obj                A Data object.       
                predictive_ckecks       A List of observed variables to plot predictive checks.    
            Sets:
            --------
                _data                   A Data object.                
                _grids                  A Dict of pn.GridSpec objects: 
                                        {<var_name>:{<space>:pn.GridSpec}}
                _cells                  A Dict {<pred_check>:Cell object},
                                        where pred_check in {'min','max','mean','std'}.
                _cells_widgets          A Dict dict1 of the form (key1,value1) = (<widget_name>, dict2)
                                        dict2 of the form (key1,value1) = (<space>, List of tuples (<cell_id>,<widget_id>)
                                        of the widgets with same name).
                _plotted_widgets        A List of widget objects to be plotted.
        """
        self._pred_checks = predictive_ckecks
        Grid.__init__(self, data_obj)

    def _create_grids(self): 
        """
            Creates a 2x2 grid of the prior and posterior predictive checks
            for min, max, mean and std function.

            Sets:
            --------
            _grids      A Dict of pn.GridSpec objects: 
                        {<var_name>:{<space>:pn.GridSpec}}
        """ 
        for var in self._pred_checks:
            if self._data.is_observed_variable(var):
                c_min = PredictiveChecksCell(var,"min")
                c_max = PredictiveChecksCell(var,"max")
                c_mean = PredictiveChecksCell(var,"mean")
                c_std = PredictiveChecksCell(var,"std")
                self._cells['min'] = c_min 
                self._cells['max'] = c_max
                self._cells['mean'] = c_mean
                self._cells['std'] = c_std
                ##Add to grid
                cell_spaces = c_min.get_spaces()
                self._grids[var] = {}
                for space in cell_spaces:
                    if space not in self._grids[var]:
                        self._grids[var][space] = pn.GridSpec(sizing_mode='stretch_both')
                    for row in [0,1]:
                        for i in [0,1]:
                            col = int((MAX_NUM_OF_COLS_PER_ROW - 2.*COLS_PER_VAR) / 2.)
                            start_point = ( row, int(col + i*COLS_PER_VAR) )  
                            end_point = ( row+1, int(col + (i+1)*COLS_PER_VAR) )
                            if row == 0 and i == 0:
                                self._grids[var][space][ start_point[0]:end_point[0], start_point[1]:end_point[1] ] = \
                                                pn.Column(c_min.get_plot(space,add_info=False), width=220, height=220)
                            elif row == 0 and i == 1:
                                self._grids[var][space][ start_point[0]:end_point[0], start_point[1]:end_point[1] ] = \
                                                pn.Column(c_max.get_plot(space,add_info=False), width=220, height=220)
                            elif row == 1 and i == 0:
                                self._grids[var][space][ start_point[0]:end_point[0], start_point[1]:end_point[1] ] = \
                                                pn.Column(c_mean.get_plot(space,add_info=False), width=220, height=220)
                            elif row == 1 and i == 1:
                                self._grids[var][space][ start_point[0]:end_point[0], start_point[1]:end_point[1] ] = \
                                                pn.Column(c_std.get_plot(space,add_info=False), width=220, height=220)