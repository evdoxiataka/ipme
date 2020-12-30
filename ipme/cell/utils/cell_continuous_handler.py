from bokeh.models import BoxSelectTool, HoverTool
from ...utils.constants import COLORS
from .cell_clear_selection import CellClearSelection

class CellContinuousHandler():

    @staticmethod
    def initialize_glyphs(variableCell, space):
        so=variableCell._plot[space].line('x', 'y', line_color = COLORS[0], line_width = 2, source=variableCell._source[space])
        re=variableCell._plot[space].line('x', 'y', line_color = COLORS[1], line_width = 2, source=variableCell._reconstructed[space])
        variableCell._plot[space].line('x', 'y', line_color = COLORS[2], line_width = 2, source=variableCell._selection[space])
        variableCell._plot[space].dash('x', 'y', size='size', angle=90.0, angle_units='deg', line_color = COLORS[0], \
                                       source=variableCell._samples[space])
        variableCell._plot[space].dash('x', 'y', size='size', angle=90.0, angle_units='deg', line_color = COLORS[1], \
                                       source=variableCell._sel_samples[space])
        return (so,re)

    @staticmethod
    def initialize_glyphs_interactive_continuous(variableCell, space):
        so,re = CellContinuousHandler.initialize_glyphs(variableCell, space)
        ##Add BoxSelectTool
        variableCell._plot[space].add_tools(BoxSelectTool(dimensions='width', renderers=[so]))
        TOOLTIPS = [
            ("x", "@x"),
            ("y","@y"),
        ]
        hover = HoverTool( tooltips=TOOLTIPS,renderers=[so,re], mode='mouse')
        variableCell._plot[space].tools.append(hover)

    @staticmethod
    def initialize_glyphs_static_continuous(variableCell,space):
        so,re = CellContinuousHandler.initialize_glyphs(variableCell, space)

    @staticmethod
    def update_cds_interactive_continuous(variableCell, space):
        """
            Updates interaction-related ColumnDataSources (cds).
        """
        sel_var_idx_dims_values = variableCell._ic._get_sel_var_idx_dims_values()
        sel_space = variableCell._ic._get_sel_space()
        var_x_range = variableCell._ic._get_var_x_range()
        global_update = variableCell._ic._get_global_update()
        if(global_update):
            if (variableCell._name in sel_var_idx_dims_values and space == sel_space and
                variableCell._cur_idx_dims_values == sel_var_idx_dims_values[variableCell._name]):
                variableCell._update_selection_cds(space, var_x_range[(space, variableCell._name)].data['xmin'][0], \
                                                   var_x_range[(space, variableCell._name)].data['xmax'][0])
            else:
                variableCell._selection[space].data=dict(x=np.array([]), y=np.array([]))
        variableCell._update_reconstructed_cds(space)
        CellClearSelection.update_clear_selection_cds(variableCell,space)
