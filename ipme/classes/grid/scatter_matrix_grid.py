from ...interfaces.grid import Grid
from ipme.classes.cell.interactive_scatter_cell import InteractiveScatterCell
from ipme.classes.cell.static_scatter_cell import StaticScatterCell
from ipme.classes.cell.interactive_continuous_cell import InteractiveContinuousCell
from ipme.classes.cell.interactive_discrete_cell import InteractiveDiscreteCell
from ipme.classes.cell.static_continuous_cell import  StaticContinuousCell
from ipme.classes.cell.static_discrete_cell import StaticDiscreteCell

from ...utils.constants import COLS_PER_VAR
import panel as pn

class ScatterMatrixGrid(Grid):
    def _create_grids(self):
        """
            Creates one Cell object per variable. Cell object is the smallest
            visualization unit in the grid. Moreover, it creates one Panel GridSpec
            object per space.

            Sets:
            --------
                _cells      A Dict {<var_name>:Cell object}.
                _grids      A Dict of pn.GridSpec objects:
                            {<space>:pn.GridSpec}
        """
        for row in range(len(self._vars)):
            for col in range(len(self._vars)):
                if col > row:
                    break
                start_point = ( row, int(col*COLS_PER_VAR) )
                end_point = ( row+1, int((col+1)*COLS_PER_VAR) )
                if col == row:
                    ##plot VariableCell
                    var_name = self._vars[col]                    
                    if self._mode == "i":
                        if self._data.get_var_dist_type(var_name) == "Continuous":
                            c = InteractiveContinuousCell(var_name, self.ic)
                        else:
                            c = InteractiveDiscreteCell(var_name, self.ic)
                    elif self._mode == "s":
                        if self._data.get_var_dist_type(var_name) == "Continuous":
                            c = StaticContinuousCell(var_name, self.ic)
                        else:
                            c = StaticDiscreteCell(var_name, self.ic)
                else:
                    ##plot pair scatter
                    var1 = self._vars[row] 
                    var2 = self._vars[col] 
                    if self._mode == "i":
                        c = InteractiveScatterCell([var1, var2], self.ic)
                    elif self._mode == "s":
                        c = StaticScatterCell([var1, var2], self.ic)
                self.cells.append(c)
                ##Add to grid
                cell_spaces = c.get_spaces()
                for space in cell_spaces:
                    if space not in self.spaces:
                        self.spaces.append(space)
                    if space not in self._grids:
                        self._grids[space] = pn.GridSpec(sizing_mode = 'stretch_both')
                    self._grids[space][ start_point[0]:end_point[0], start_point[1]:end_point[1] ] = pn.Column(c.get_plot(space), width=220, height=220)
