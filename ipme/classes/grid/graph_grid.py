from ...interfaces.grid import Grid
from ipme.classes.cell.interactive_continuous_cell import InteractiveContinuousCell
from ipme.classes.cell.interactive_discrete_cell import InteractiveDiscreteCell
from ipme.classes.cell.static_continuous_cell import  StaticContinuousCell
from ipme.classes.cell.static_discrete_cell import StaticDiscreteCell

from ...utils.constants import MAX_NUM_OF_COLS_PER_ROW, MAX_NUM_OF_VARS_PER_ROW, COLS_PER_VAR
import panel as pn

class GraphGrid(Grid):
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
        graph_grid_map = self._create_graph_grid_mapping()
        for row, map_data in graph_grid_map.items():
            level = map_data[0]
            vars_list = map_data[1]
            level_previous = -1
            if (row-1) in graph_grid_map:
                level_previous = graph_grid_map[row-1][0]
            if level != level_previous:
                col = int((MAX_NUM_OF_COLS_PER_ROW - len(vars_list)*COLS_PER_VAR) / 2.)
            else:
                col = int((MAX_NUM_OF_COLS_PER_ROW - MAX_NUM_OF_VARS_PER_ROW*COLS_PER_VAR) / 2.)
            for i,var_name in enumerate(vars_list):
                start_point = ( row, int(col + i*COLS_PER_VAR) )
                end_point = ( row+1, int(col + (i+1)*COLS_PER_VAR) )
                #col_l = int(col_f + (i+1)*COLS_PER_VAR)
                # grid_bgrd_col = level
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
                self.cells.append(c)
                ##Add to grid
                cell_spaces = c.get_spaces()
                for space in cell_spaces:
                    if space not in self.spaces:
                        self.spaces.append(space)
                    if space not in self._grids:
                        self._grids[space] = pn.GridSpec(sizing_mode = 'stretch_both')
                    self._grids[space][ start_point[0]:end_point[0], start_point[1]:end_point[1] ] = pn.Column(c.get_plot(space), width=220, height=220)
        self.ic.num_cells = len(self.cells)

    def _create_graph_grid_mapping(self):
        """
            Maps the graph levels and the variables to Panel GridSpec rows/cols.
            Both <grid_row>=0 and <graph_level>=0 correspond to higher row/level.

            Returns:
            --------
                A Dict {<grid_row>: (<graph_level>, List of varnames) }
        """
        _varnames_per_graph_level = self._data.get_varnames_per_graph_level()
        num_of_vars_per_graph_level = [len(_varnames_per_graph_level[k]) for k in sorted(_varnames_per_graph_level)]
        graph_grid_map = {}
        for level, num_vars in enumerate(num_of_vars_per_graph_level):
            row = level
            indx = 0
            while num_vars > MAX_NUM_OF_VARS_PER_ROW:
                while row in graph_grid_map:
                    row+=1
                graph_grid_map[row] = (level,_varnames_per_graph_level[level][indx:indx+MAX_NUM_OF_VARS_PER_ROW])
                row += 1
                indx += MAX_NUM_OF_VARS_PER_ROW
                num_vars -= MAX_NUM_OF_VARS_PER_ROW
            while row in graph_grid_map:
                row+=1
            graph_grid_map[row] = (level,_varnames_per_graph_level[level][indx:indx+num_vars])
        return graph_grid_map
