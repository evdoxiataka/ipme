from ..interfaces.grid import Grid
from .predictive_ckecks_cell import PredictiveChecksCell

import panel as pn

class PredictiveChecks(Grid):
    def _create_grids(self): 
        """
            Creates a 2x2 grid of the prior and posterior predictive checks
            for min, max, mean and std function.

            Sets:
            --------
                - "self._grids" Dict
        """ 
        for var in self._pred_checks:
            if self._data.is_observed_variable(var):
                c_min = PredictiveChecksCell(var,"min")
                c_max = PredictiveChecksCell(var,"max")
                c_mean = PredictiveChecksCell(var,"mean")
                c_std = PredictiveChecksCell(var,"std")
                ##Add to grid
                cell_spaces = c_min.get_spaces()
                self._grids[var] = {}
                for space in cell_spaces:
                    if space not in self._grids[var]:
                        self._grids[var][space] = pn.GridSpec(sizing_mode='stretch_both')
                    for row in [0,1]:
                        for i in [0,1]:
                            col = int((Grid._MAX_NUM_OF_COLS_PER_ROW - 2.*Grid._COLS_PER_VAR) / 2.)
                            start_point = ( row, int(col + i*Grid._COLS_PER_VAR) )  
                            end_point = ( row+1, int(col + (i+1)*Grid._COLS_PER_VAR) )
                            if row == 0 and i == 0:
                                self._predictive_grids_grids[var][space][ start_point[0]:end_point[0], start_point[1]:end_point[1] ] = \
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