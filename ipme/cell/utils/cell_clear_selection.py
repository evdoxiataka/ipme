from ...utils.functions import find_highest_point
from ...utils.js_code import HOVER_CODE

from bokeh.models import HoverTool, CustomJS

class CellClearSelection:

    def __init__(self):
        pass

    @staticmethod
    def initialize_glyphs_x_button(variableCell, space):
        ## x-button to clear selection
        sq_x = variableCell.plot[space].scatter('x', 'y', marker = "square_x", size = 10, fill_color = "grey", hover_fill_color = "firebrick", \
                                               fill_alpha = 0.5, hover_alpha = 1.0, line_color = "grey", hover_line_color = "white", \
                                               source = variableCell.clear_selection[space], name = 'clear_selection')
        ## Add HoverTool for x-button
        variableCell.plot[space].add_tools(HoverTool(tooltips = "Clear Selection", renderers = [sq_x], mode = 'mouse', show_arrow = False,
                                                      callback = CustomJS(args = dict(source = variableCell.clear_selection[space]), code = HOVER_CODE)))

    @staticmethod
    def update_clear_selection_cds(variableCell, space):
        """
            Updates clear_selection ColumnDataSource (cds).
        """
        sel_var_idx_dims_values = variableCell.ic.get_sel_var_idx_dims_values()
        sel_space = variableCell.ic.get_sel_space()
        var_x_range = variableCell.ic.get_var_x_range()
        if (variableCell.name in sel_var_idx_dims_values and space == sel_space and
            variableCell.cur_idx_dims_values == sel_var_idx_dims_values[variableCell.name]):
            min_x_range = var_x_range[(space, variableCell.name)].data['xmin'][0]
            max_x_range = var_x_range[(space, variableCell.name)].data['xmax'][0]
            hp = find_highest_point(variableCell.reconstructed[space].data['x'], variableCell.reconstructed[space].data['y'])
            if not hp:
                hp = find_highest_point(variableCell.selection[space].data['x'], variableCell.selection[space].data['y'])
                if not hp:
                    hp = find_highest_point(variableCell.source[space].data['x'], variableCell.source[space].data['y'])
                    if not hp:
                        hp = (0,0)
            variableCell.clear_selection[space].data = dict( x = [(max_x_range + min_x_range) / 2.], y = [hp[1]+hp[1]*0.1], isIn = [0])
        else:
            variableCell.clear_selection[space].data = dict( x = [], y = [], isIn = [])
