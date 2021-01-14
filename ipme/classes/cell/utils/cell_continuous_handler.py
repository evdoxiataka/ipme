from .cell_clear_selection import CellClearSelection

from ipme.utils.constants import  COLORS, BORDER_COLORS, PLOT_HEIGHT, PLOT_WIDTH, SIZING_MODE, RUG_DIST_RATIO, RUG_SIZE
from ipme.utils.stats import kde
from ipme.utils.functions import find_inds_before_after, find_indices

from bokeh.models import BoxSelectTool, HoverTool
from bokeh.models import ColumnDataSource
from bokeh import events
from bokeh.plotting import figure

import threading
from functools import partial

class CellContinuousHandler:

    def __init__(self):
        pass

    @staticmethod
    def initialize_glyphs(variableCell, space):
        so = variableCell.plot[space].line('x', 'y', line_color = COLORS[0], line_width = 2, source = variableCell.source[space])
        re = variableCell.plot[space].line('x', 'y', line_color = COLORS[1], line_width = 2, source = variableCell.reconstructed[space])
        variableCell.plot[space].line('x', 'y', line_color = COLORS[2], line_width = 2, source = variableCell.selection[space])
        variableCell.plot[space].dash('x', 'y', size='size', angle = 90.0, angle_units = 'deg', line_color = COLORS[0], source = variableCell.samples[space])
        variableCell.plot[space].dash('x', 'y', size='size', angle = 90.0, angle_units = 'deg', line_color = COLORS[1], source = variableCell.sel_samples[space])
        #########TEST#######
        ##Tooltips
        TOOLTIPS = [("x", "@x"), ("y","@y"),]
        hover = HoverTool( tooltips = TOOLTIPS, renderers = [so,re], mode = 'mouse')
        variableCell.plot[space].tools.append(hover)
        return (so,re)

    @staticmethod
    def initialize_glyphs_interactive(variableCell, space):
        so,re = CellContinuousHandler.initialize_glyphs(variableCell, space)
        ##Add BoxSelectTool
        variableCell.plot[space].add_tools(BoxSelectTool(dimensions = 'width', renderers = [so]))
        # ##Tooltips
        # TOOLTIPS = [("x", "@x"), ("y","@y"),]
        # hover = HoverTool( tooltips = TOOLTIPS, renderers = [so,re], mode = 'mouse')
        # variableCell.plot[space].tools.append(hover)

    @staticmethod
    def initialize_glyphs_static(variableCell, space):
        so,re = CellContinuousHandler.initialize_glyphs(variableCell, space)

    @staticmethod
    def initialize_fig(variableCell, space):
        variableCell.plot[space] = figure( x_range = variableCell.x_range[space], tools = "wheel_zoom,reset,box_zoom", toolbar_location = 'right',
                                    plot_width = PLOT_WIDTH, plot_height = PLOT_HEIGHT, sizing_mode = SIZING_MODE)
        variableCell.plot[space].border_fill_color = BORDER_COLORS[0]
        variableCell.plot[space].xaxis.axis_label = ""
        variableCell.plot[space].yaxis.visible = False
        variableCell.plot[space].toolbar.logo = None
        variableCell.plot[space].xaxis[0].ticker.desired_num_ticks = 3

    @staticmethod
    def initialize_fig_interactive(variableCell, space):
        CellContinuousHandler.initialize_fig(variableCell, space)
        ##Events
        variableCell.plot[space].on_event(events.Tap, partial(CellClearSelection.clear_selection_callback, space))
        variableCell.plot[space].on_event(events.SelectionGeometry, partial(CellContinuousHandler.selectionbox_callback, space))
        ##on_change
        variableCell.ic.sample_inds_update[space].on_change('data', partial(variableCell.sample_inds_callback, space))

    @staticmethod
    def initialize_fig_static(variableCell, space):
        CellContinuousHandler.initialize_fig(variableCell, space)
        ##on_change
        variableCell.ic.sample_inds_update[space].on_change('data', partial(variableCell.sample_inds_callback, space))

    @staticmethod
    def initialize_cds(variableCell, space):
        samples = variableCell.get_data_for_cur_idx_dims_values(space)
        variableCell.source[space] = ColumnDataSource(data = kde(samples))
        max_v = variableCell.source[space].data['y'].max()
        variableCell.samples[space] = ColumnDataSource(data = dict( x = samples, y = np.asarray([-max_v/RUG_DIST_RATIO]*len(samples)), size = np.asarray([RUG_SIZE]*len(samples))))

    @staticmethod
    def initialize_cds_interactive(variableCell, space):
        CellContinuousHandler.initialize_cds(variableCell, space)
        variableCell.sel_samples[space] = ColumnDataSource(data = dict(x = np.array([]), y = np.array([]), size = np.array([])))
        variableCell.selection[space] = ColumnDataSource(data = dict(x = np.array([]), y = np.array([])))
        variableCell.reconstructed[space] = ColumnDataSource(data = dict(x = np.array([]), y = np.array([])))
        variableCell.clear_selection[space] = ColumnDataSource(data = dict(x = [], y = [], isIn = []))
        variableCell.ic.var_x_range[(space, variableCell.name)] = ColumnDataSource(data = dict(xmin = np.array([]), xmax = np.array([])))

    @staticmethod
    def initialize_cds_static(variableCell, space):
        CellContinuousHandler.initialize_cds(variableCell, space)
        #########TEST###########

    @staticmethod
    def update_cds_interactive(variableCell, space):
        """
            Updates interaction-related ColumnDataSources (cds).
        """
        sel_var_idx_dims_values = variableCell.ic.get_sel_var_idx_dims_values()
        sel_space = variableCell.ic.get_sel_space()
        var_x_range = variableCell.ic.get_var_x_range()
        global_update = variableCell.ic.get_global_update()
        if global_update:
            if variableCell.name in sel_var_idx_dims_values and space == sel_space and variableCell.cur_idx_dims_values == sel_var_idx_dims_values[variableCell.name]:
                variableCell.update_selection_cds(space, var_x_range[(space, variableCell.name)].data['xmin'][0], var_x_range[(space, variableCell.name)].data['xmax'][0])
            else:
                variableCell.selection[space].data = dict( x = np.array([]), y = np.array([]))
        variableCell.update_reconstructed_cds(space)
        CellClearSelection.update_clear_selection_cds(variableCell, space)

    @staticmethod
    def update_cds_static(variableCell, space):
        """
            Update source & samples cds in the static mode
        """
        samples = variableCell.get_data_for_cur_idx_dims_values(space)
        inds = variableCell.ic.get_sample_inds(space)
        if len(inds):
            sel_sample = samples[inds]
            variableCell.source[space].data = kde(sel_sample)
            max_v = variableCell.get_max_prob(space)
            variableCell.samples[space].data = dict( x = sel_sample, y = np.asarray([-max_v/RUG_DIST_RATIO]*len(sel_sample)), size = np.asarray([RUG_SIZE]*len(sel_sample)))
        else:
            variableCell.source[space].data = kde(samples)
            max_v = variableCell.get_max_prob(space)
            variableCell.samples[space].data = dict( x = samples, y = np.asarray([-max_v/RUG_DIST_RATIO]*len(samples)), size = np.asarray([RUG_SIZE]*len(samples)))

    ## ONLY FOR INTERACTIVE CASE
    @staticmethod
    def selectionbox_callback(variableCell, space, event):
        """
            Callback called when selection box is drawn.
        """
        xmin = event.geometry['x0']
        xmax = event.geometry['x1']
        variableCell.ic._set_selection(variableCell.name, space, (xmin, xmax), variableCell.cur_idx_dims_values)
        for sp in variableCell.spaces:
            samples = variableCell.samples[sp].data['x']
            variableCell.ic.add_space_threads(threading.Thread(target = partial(CellContinuousHandler._selectionbox_space_thread, variableCell, sp, samples, xmin, xmax), daemon = True))
        variableCell.ic.space_threads_join()

    @staticmethod
    def _selectionbox_space_thread(variableCell, space, samples, xmin, xmax):
        x_range = variableCell.ic.get_var_x_range(space, variableCell.name)
        if len(x_range):
            variableCell.update_selection_cds(space, x_range[0], x_range[1])
        else:
            variableCell.selection[space].data = dict(x = np.array([]), y = np.array([]))
        inds = find_indices(samples, lambda e: xmin <= e <= xmax, xmin, xmax)
        variableCell.ic.set_sel_var_inds(space, variableCell.name, inds)
        variableCell.compute_intersection_of_samples(space)
        variableCell.ic.selection_threads_join(space)

    @staticmethod
    def update_source_cds_interactive(variableCell, space):
        """
            Updates source ColumnDataSource (cds).
        """
        samples = variableCell.get_data_for_cur_idx_dims_values(space)
        variableCell.source[space].data = kde(samples)
        max_v = variableCell.get_max_prob(space)
        variableCell.samples[space].data = dict( x = samples, y = np.asarray([-max_v/RUG_DIST_RATIO]*len(samples)), size = np.asarray([RUG_SIZE]*len(samples)))

    @staticmethod
    def update_selection_cds_interactive(variableCell, space, xmin, xmax):
        """
            Updates selection ColumnDataSource (cds).
        """
        # Get kde points within [xmin,xmax]
        data = {}
        data['x'] = np.array([])
        data['y'] = np.array([])
        kde_indices = find_indices(variableCell.source[space].data['x'], lambda e: xmin <= e <= xmax, xmin, xmax)
        if len(kde_indices) == 0:
            variableCell.selection[space].data = dict( x = np.array([]), y = np.array([]))
            return
        data['x'] = variableCell.source[space].data['x'][kde_indices]
        data['y'] = variableCell.source[space].data['y'][kde_indices]

        # Add interpolated points at xmin, xmax
        xmin_inds = find_inds_before_after(variableCell.source[space].data['x'], xmin)
        if -1 not in xmin_inds:
            xmin_l = variableCell.source[space].data['x'][xmin_inds[0]]
            xmin_h = variableCell.source[space].data['x'][xmin_inds[1]]
            ymin_l = variableCell.source[space].data['y'][xmin_inds[0]]
            ymin_h = variableCell.source[space].data['y'][xmin_inds[1]]
            ymin = ((ymin_h-ymin_l)/(xmin_h-xmin_l))*(xmin-xmin_l) + ymin_l
            data['x'] = np.insert(data['x'], 0, xmin)
            data['y'] = np.insert(data['y'], 0, ymin)

        xmax_inds = find_inds_before_after(variableCell.source[space].data['x'], xmax)
        if -1 not in xmax_inds:
            xmax_l = variableCell.source[space].data['x'][xmax_inds[0]]
            xmax_h = variableCell.source[space].data['x'][xmax_inds[1]]
            ymax_l = variableCell.source[space].data['y'][xmax_inds[0]]
            ymax_h = variableCell.source[space].data['y'][xmax_inds[1]]
            ymax = ((ymax_h-ymax_l)/(xmax_h-xmax_l))*(xmax-xmax_l) + ymax_l
            data['x'] = np.append(data['x'], xmax)
            data['y'] = np.append(data['y'], ymax)

        # Append and prepend zeros
        data['y'] = np.insert(data['y'], 0, 0)
        data['y'] = np.append(data['y'], 0)
        data['x'] = np.insert(data['x'], 0, data['x'][0])
        data['x'] = np.append(data['x'], data['x'][-1])
        variableCell.selection[space].data = data

    @staticmethod
    def update_reconstructed_cds_interactive(variableCell, space):
        """
            Updates reconstructed ColumnDataSource (cds).
        """
        samples = variableCell.samples[space].data['x']
        inds = variableCell.ic.get_sample_inds(space)
        if len(inds):
            sel_sample = samples[inds]
            variableCell.reconstructed[space].data = kde(sel_sample)
            max_v = variableCell.get_max_prob(space)
            variableCell.sel_samples[space].data = dict( x = sel_sample, y = np.asarray([-max_v/RUG_DIST_RATIO]*len(sel_sample)), size = np.asarray([RUG_SIZE]*len(sel_sample)))
        else:
            variableCell.reconstructed[space].data = dict( x = np.array([]), y = np.array([]))
            variableCell.sel_samples[space].data = dict( x = np.array([]), y = np.array([]), size = np.array([]))
        max_v = variableCell.get_max_prob(space)
        if max_v!=-1:
            variableCell.samples[space].data['y'] = np.asarray([-max_v/RUG_DIST_RATIO]*len(variableCell.samples[space].data['x']))

    @staticmethod
    def clear_selection_callback(variableCell, space, event):
        """
            Callback called when clear selection glyph is clicked.
        """
        isIn = variableCell.clear_selection[space].data['isIn']
        if 1 in isIn:
            variableCell.ic.set_var_x_range(space, variableCell.name, dict(xmin = np.array([]), xmax = np.array([])))
            variableCell.ic.delete_sel_var_idx_dims_values(variableCell.name)
            for sp in variableCell.spaces:
                variableCell.ic.add_space_threads(threading.Thread(target = partial(CellContinuousHandler._clear_selection_cds_update, variableCell, sp), daemon = True))
        variableCell.ic.space_threads_join()

    @staticmethod
    def _clear_selection_cds_update(variableCell, space):
        x_range = variableCell.ic.get_var_x_range(space, variableCell.name)
        xmin_list = x_range['xmin']
        xmax_list = x_range['xmax']
        if len(xmin_list):
            variableCell.update_selection_cds(space, xmin_list[0], xmax_list[0])
        else:
            variableCell.selection[space].data = dict(x = np.array([]), y = np.array([]))
        variableCell.ic.delete_sel_var_inds(space, variableCell.name)
        variableCell.compute_intersection_of_samples(space)
        variableCell.ic.selection_threads_join(space)

