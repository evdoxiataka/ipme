from .cell_clear_selection import CellClearSelection

from bokeh.models import BoxSelectTool, HoverTool

from ...utils.constants import  COLORS,  RUG_DIST_RATIO, RUG_SIZE
from ...utils.stats import kde
from ...utils.functions import find_inds_before_after, find_indices

class CellContinuousHandler():

    @staticmethod
    def initialize_glyphs(variableCell, space):
        so=variableCell._plot[space].line('x', 'y', line_color = COLORS[0], line_width = 2, source = variableCell._source[space])
        re=variableCell._plot[space].line('x', 'y', line_color = COLORS[1], line_width = 2, source = variableCell._reconstructed[space])
        variableCell._plot[space].line('x', 'y', line_color = COLORS[2], line_width = 2, source = variableCell._selection[space])
        variableCell._plot[space].dash('x', 'y', size='size', angle = 90.0, angle_units = 'deg', line_color = COLORS[0], source = variableCell._samples[space])
        variableCell._plot[space].dash('x', 'y', size='size', angle = 90.0, angle_units = 'deg', line_color = COLORS[1], source = variableCell._sel_samples[space])
        return (so,re)

    @staticmethod
    def initialize_glyphs_interactive_continuous(variableCell, space):
        so,re = CellContinuousHandler.initialize_glyphs(variableCell, space)
        ##Add BoxSelectTool
        variableCell._plot[space].add_tools(BoxSelectTool(dimensions='width', renderers=[so]))
        TOOLTIPS = [("x", "@x"), ("y","@y"),]
        hover = HoverTool( tooltips = TOOLTIPS, renderers = [so,re], mode = 'mouse')
        variableCell._plot[space].tools.append(hover)

    @staticmethod
    def initialize_glyphs_static_continuous(variableCell, space):
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
            if (variableCell._name in sel_var_idx_dims_values and space == sel_space and variableCell._cur_idx_dims_values == sel_var_idx_dims_values[variableCell._name]):
                variableCell._update_selection_cds(space, var_x_range[(space, variableCell._name)].data['xmin'][0], var_x_range[(space, variableCell._name)].data['xmax'][0])
            else:
                variableCell._selection[space].data = dict( x = np.array([]), y = np.array([]))
        variableCell._update_reconstructed_cds(space)
        CellClearSelection.update_clear_selection_cds(variableCell, space)

    @staticmethod
    def update_cds_static_continuous(variableCell, space):
        """
            Update source & samples cds in the static mode
        """
        samples = variableCell._get_data_for_cur_idx_dims_values(space)
        inds = variableCell._ic._get_sample_inds(space)
        if len(inds):
            sel_sample = samples[inds]
            variableCell._source[space].data = kde(sel_sample)
            max_v = variableCell._get_max_prob(space)
            variableCell._samples[space].data = dict( x = sel_sample, y = np.asarray([-max_v/RUG_DIST_RATIO]*len(sel_sample)), size = np.asarray([RUG_SIZE]*len(sel_sample)))
        else:
            variableCell._source[space].data = kde(samples)
            max_v = variableCell._get_max_prob(space)
            variableCell._samples[space].data = dict( x = samples, y = np.asarray([-max_v/RUG_DIST_RATIO]*len(samples)), size = np.asarray([RUG_SIZE]*len(samples)))

    ## ONLY FOR INTERACTIVE CASE
    @staticmethod
    def update_source_cds_interactive_continuous(variableCell, space):
        """
            Updates source ColumnDataSource (cds).
        """
        samples = variableCell._get_data_for_cur_idx_dims_values(space)
        variableCell._source[space].data = kde(samples)
        max_v = variableCell._get_max_prob(space)
        variableCell._samples[space].data = dict( x = samples, y = np.asarray([-max_v/RUG_DIST_RATIO]*len(samples)), size = np.asarray([RUG_SIZE]*len(samples)))

    @staticmethod
    def update_selection_cds_interactive_continuous(variableCell, space, xmin, xmax):
        """
            Updates selection ColumnDataSource (cds).
        """
        # Get kde points within [xmin,xmax]
        data = {}
        data['x'] = np.array([])
        data['y'] = np.array([])
        kde_indices = find_indices(variableCell._source[space].data['x'], lambda e: e >= xmin and e<= xmax,xmin,xmax)
        if len(kde_indices) == 0:
            variableCell._selection[space].data = dict( x = np.array([]), y = np.array([]))
            return
        data['x'] = variableCell._source[space].data['x'][kde_indices]
        data['y'] = variableCell._source[space].data['y'][kde_indices]

        # Add interpolated points at xmin, xmax
        xmin_inds = find_inds_before_after(variableCell._source[space].data['x'], xmin)
        if -1 not in xmin_inds:
            xmin_l = variableCell._source[space].data['x'][xmin_inds[0]]
            xmin_h = variableCell._source[space].data['x'][xmin_inds[1]]
            ymin_l = variableCell._source[space].data['y'][xmin_inds[0]]
            ymin_h = variableCell._source[space].data['y'][xmin_inds[1]]
            ymin = ((ymin_h-ymin_l)/(xmin_h-xmin_l))*(xmin-xmin_l) + ymin_l
            data['x'] = np.insert(data['x'], 0, xmin)
            data['y'] = np.insert(data['y'], 0, ymin)

        xmax_inds = find_inds_before_after(variableCell._source[space].data['x'], xmax)
        if -1 not in xmax_inds:
            xmax_l = variableCell._source[space].data['x'][xmax_inds[0]]
            xmax_h = variableCell._source[space].data['x'][xmax_inds[1]]
            ymax_l = variableCell._source[space].data['y'][xmax_inds[0]]
            ymax_h = variableCell._source[space].data['y'][xmax_inds[1]]
            ymax = ((ymax_h-ymax_l)/(xmax_h-xmax_l))*(xmax-xmax_l) + ymax_l
            data['x'] = np.append(data['x'], xmax)
            data['y'] = np.append(data['y'], ymax)

        # Append and prepend zeros
        data['y'] = np.insert(data['y'], 0, 0)
        data['y'] = np.append(data['y'], 0)
        data['x'] = np.insert(data['x'], 0, data['x'][0])
        data['x'] = np.append(data['x'], data['x'][-1])
        variableCell._selection[space].data = data

    @staticmethod
    def update_reconstructed_cds_interactive_continuous(variableCell, space):
        """
            Updates reconstructed ColumnDataSource (cds).
        """
        samples = variableCell._samples[space].data['x']
        inds = variableCell._ic._get_sample_inds(space)
        if len(inds):
            sel_sample = samples[inds]
            variableCell._reconstructed[space].data = kde(sel_sample)
            max_v = variableCell._get_max_prob(space)
            variableCell._sel_samples[space].data = dict( x = sel_sample, y = np.asarray([-max_v/RUG_DIST_RATIO]*len(sel_sample)), size = np.asarray([RUG_SIZE]*len(sel_sample)))
        else:
            variableCell._reconstructed[space].data = dict( x = np.array([]), y = np.array([]))
            variableCell._sel_samples[space].data = dict( x = np.array([]), y = np.array([]), size = np.array([]))
        max_v = variableCell._get_max_prob(space)
        if max_v!=-1:
            variableCell._samples[space].data['y'] = np.asarray([-max_v/RUG_DIST_RATIO]*len(variableCell._samples[space].data['x']))

