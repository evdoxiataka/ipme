from ipme.classes.cell.utils.cell_clear_selection import CellClearSelection

from ipme.utils.constants import  COLORS, BORDER_COLORS, PLOT_HEIGHT, PLOT_WIDTH, SIZING_MODE, RUG_DIST_RATIO, DATA_SIZE
from ipme.utils.stats import pmf
from ipme.utils.functions import find_indices

from bokeh.models import ColumnDataSource, BoxSelectTool, HoverTool

from bokeh import events
from bokeh.plotting import figure

import numpy as np
import threading
from functools import partial

class CellDiscreteHandler:

    def __init__(self):
        pass

    @staticmethod
    def initialize_glyphs_interactive(variableCell, space):
        hover_renderer = []
        so_seg = variableCell.plot[space].segment(x0 = 'x', y0 ='y0', x1 = 'x', y1 = 'y', source = variableCell.source[space], line_alpha = 1.0, color = COLORS[0], line_width = 1, selection_color = COLORS[0], \
                                                  nonselection_color = COLORS[0], nonselection_line_alpha = 1.0)
        variableCell.plot[space].scatter('x', 'y', source = variableCell.source[space], size = 4, fill_color = COLORS[0], fill_alpha = 1.0, line_color = COLORS[0], selection_fill_color = COLORS[0], \
                                         nonselection_fill_color = COLORS[0], nonselection_fill_alpha = 1.0, nonselection_line_color = COLORS[0])
        variableCell.plot[space].segment(x0 = 'x', y0 ='y0', x1 = 'x', y1 = 'y', source = variableCell.selection[space], line_alpha = 0.7, color = COLORS[2], line_width = 1)
        variableCell.plot[space].scatter('x', 'y', source = variableCell.selection[space], size = 4, fill_color = COLORS[2], fill_alpha = 0.7, line_color = COLORS[2])
        rec = variableCell.plot[space].segment(x0 = 'x', y0 ='y0', x1 = 'x', y1 = 'y', source = variableCell.reconstructed[space], line_alpha = 0.5, color = COLORS[1], line_width = 1)
        variableCell.plot[space].scatter('x', 'y', source = variableCell.reconstructed[space], size = 4, fill_color = COLORS[1], fill_alpha = 0.5, line_color = COLORS[1])
        hover_renderer.append(so_seg)
        hover_renderer.append(rec)
        if space in variableCell.data:
            dat = variableCell.plot[space].asterisk('x', 'y', size = DATA_SIZE, line_color = COLORS[3], source = variableCell.data[space])
            hover_renderer.append(dat)
        ##Add BoxSelectTool
        variableCell.plot[space].add_tools(BoxSelectTool(dimensions = 'width', renderers = [so_seg]))
        ##Tooltips
        TOOLTIPS = [("x", "@x"), ("y","@y"),]
        hover = HoverTool( tooltips = TOOLTIPS, renderers = hover_renderer, mode = 'mouse')
        variableCell.plot[space].tools.append(hover)

    @staticmethod
    def initialize_glyphs_static(variableCell, space):
        hover_renderer = []
        so_seg = variableCell.plot[space].segment(x0 = 'x', y0 ='y0', x1 = 'x', y1 = 'y', source = variableCell.source[space], line_alpha = 1.0, color = COLORS[0], line_width = 1, selection_color = COLORS[0], \
                                                  nonselection_color = COLORS[0], nonselection_line_alpha = 1.0)
        variableCell.plot[space].scatter('x', 'y', source = variableCell.source[space], size = 4, fill_color = COLORS[0], fill_alpha = 1.0, line_color = COLORS[0], selection_fill_color = COLORS[0], \
                                         nonselection_fill_color = COLORS[0], nonselection_fill_alpha = 1.0, nonselection_line_color = COLORS[0])
        hover_renderer.append(so_seg)
        if space in variableCell.data:
            dat = variableCell.plot[space].asterisk('x', 'y', size = DATA_SIZE, line_color = COLORS[3], source = variableCell.data[space])
            hover_renderer.append(dat)
        ##Tooltips
        TOOLTIPS = [("x", "@x"), ("y","@y"),]
        hover = HoverTool( tooltips = TOOLTIPS, renderers = hover_renderer, mode = 'mouse')
        variableCell.plot[space].tools.append(hover)

    @staticmethod
    def initialize_fig(variableCell, space):
        variableCell.plot[space] = figure( x_range = variableCell.x_range[variableCell.name][space], tools = "wheel_zoom,reset,box_zoom", toolbar_location = 'right',
                                            plot_width = PLOT_WIDTH, plot_height = PLOT_HEIGHT, sizing_mode = SIZING_MODE)
        variableCell.plot[space].border_fill_color = BORDER_COLORS[0]
        variableCell.plot[space].xaxis.axis_label = variableCell.name
        variableCell.plot[space].yaxis.visible = False
        variableCell.plot[space].toolbar.logo = None
        variableCell.plot[space].xaxis[0].ticker.desired_num_ticks = 3

    @staticmethod
    def initialize_fig_interactive(variableCell, space):
        CellDiscreteHandler.initialize_fig(variableCell, space)
        ##Events
        variableCell.plot[space].on_event(events.Tap, partial(CellDiscreteHandler.clear_selection_callback, variableCell, space))
        variableCell.plot[space].on_event(events.SelectionGeometry, partial(CellDiscreteHandler.selectionbox_callback, variableCell, space))
        ##on_change
        variableCell.ic.sample_inds_update[space].on_change('data', partial(variableCell.sample_inds_callback, space))

    @staticmethod
    def initialize_fig_static(variableCell, space):
        CellDiscreteHandler.initialize_fig(variableCell, space)
        ##on_change
        variableCell.ic.sample_inds_update[space].on_change('data', partial(variableCell.sample_inds_callback, space))

    @staticmethod
    def initialize_cds(variableCell, space):
        samples = variableCell.get_samples_for_cur_idx_dims_values(variableCell.name, space)
        variableCell.source[space] = ColumnDataSource(data = pmf(samples))
        variableCell.samples[space] = ColumnDataSource(data = dict(x = samples))
        # data cds
        data = variableCell.get_data_for_cur_idx_dims_values(variableCell.name)
        if data is not None:
            max_v = variableCell.source[space].data['y'].max()
            variableCell.data[space] =  ColumnDataSource(data = dict(x = data, y = np.asarray([-1*max_v/RUG_DIST_RATIO]*len(data))))
        # initialize sample inds
        variableCell.ic.initialize_sample_inds(space, dict(inds = [False]*len(variableCell.samples[space].data['x'])), dict(non_inds = [True]*len(variableCell.samples[space].data['x'])))

    @staticmethod
    def initialize_cds_interactive(variableCell, space):
        CellDiscreteHandler.initialize_cds(variableCell, space)
        variableCell.selection[space] = ColumnDataSource(data = dict(x = np.array([]), y = np.array([]), y0 = np.array([])))
        variableCell.reconstructed[space] = ColumnDataSource(data = dict(x = np.array([]), y = np.array([]), y0 = np.array([])))
        variableCell.clear_selection[space] = ColumnDataSource(data = dict(x = [], y = [], isIn = []))
        variableCell.ic.var_x_range[(space, variableCell.name)] = ColumnDataSource(data = dict(xmin = np.array([]), xmax = np.array([])))
  
    @staticmethod
    def initialize_cds_static(variableCell, space):
        CellDiscreteHandler.initialize_cds(variableCell, space)
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
            cur_idx_dims_values = {}
            if variableCell.name in variableCell.cur_idx_dims_values:
                cur_idx_dims_values = variableCell.cur_idx_dims_values[variableCell.name]
            if variableCell.name in sel_var_idx_dims_values and space == sel_space and cur_idx_dims_values == sel_var_idx_dims_values[variableCell.name]:
                variableCell.update_selection_cds(space, var_x_range[(space, variableCell.name)].data['xmin'][0], var_x_range[(space, variableCell.name)].data['xmax'][0])
            else:
                variableCell.selection[space].data = dict(x = np.array([]), y = np.array([]), y0 = np.array([]))
        variableCell.update_reconstructed_cds(space)
        CellClearSelection.update_clear_selection_cds(variableCell, space)

    @staticmethod
    def update_cds_static(variableCell, space):
        """
            Update source & samples cds in the static mode
        """
        samples = variableCell.get_samples_for_cur_idx_dims_values(variableCell.name, space)
        inds,_ = variableCell.ic.get_sample_inds(space)
        if True in inds:
            sel_sample = samples[inds]
            variableCell.source[space].data = pmf(sel_sample)
            variableCell.samples[space].data = dict( x = sel_sample)
        else:
            variableCell.source[space].data = pmf(samples)
            variableCell.samples[space].data = dict( x = samples)
        # data cds
        data = variableCell.get_data_for_cur_idx_dims_values(variableCell.name)
        if data is not None:
            max_v = variableCell.get_max_prob(space)
            variableCell.data[space] =  ColumnDataSource(data = dict(x = data, y = np.asarray([-1*max_v/RUG_DIST_RATIO]*len(data))))

    ## ONLY FOR INTERACTIVE CASE
    @staticmethod
    def selectionbox_callback(variableCell, space, event):
        """
            Callback called when selection box is drawn.
        """
        xmin = event.geometry['x0']
        xmax = event.geometry['x1']
        cur_idx_dims_values = {}
        if variableCell.name in variableCell.cur_idx_dims_values:
            cur_idx_dims_values = variableCell.cur_idx_dims_values[variableCell.name]
        variableCell.ic.set_selection(variableCell.name, space, (xmin, xmax), cur_idx_dims_values)
        for sp in variableCell.spaces:
            samples = variableCell.samples[sp].data['x']
            variableCell.ic.add_space_threads(threading.Thread(target = partial(CellDiscreteHandler._selectionbox_space_thread, variableCell, sp, samples, xmin, xmax), daemon = True))
        variableCell.ic.space_threads_join()

    @staticmethod
    def _selectionbox_space_thread(variableCell, space, samples, xmin, xmax):
        x_range = variableCell.ic.get_var_x_range(space, variableCell.name)
        xmin_list = x_range['xmin']
        xmax_list = x_range['xmax']
        if len(xmin_list):
            variableCell.update_selection_cds(space, xmin_list[0], xmax_list[0])
        else:
            variableCell.selection[space].data = dict(x = np.array([]), y = np.array([]), y0 = np.array([]))
        inds = find_indices(samples, lambda e: xmin <= e <= xmax, xmin, xmax)
        variableCell.ic.set_sel_var_inds(space, variableCell.name, inds)
        variableCell.compute_intersection_of_samples(space)
        variableCell.ic.selection_threads_join(space)

    @staticmethod
    def update_source_cds_interactive(variableCell, space):
        """
            Updates source ColumnDataSource (cds).
        """
        samples = variableCell.get_samples_for_cur_idx_dims_values(variableCell.name, space)
        variableCell.source[space].data = pmf(samples)
        variableCell.samples[space].data = dict( x = samples)

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
            variableCell.selection[space].data = dict(x = np.array([]), y = np.array([]), y0 = np.array([]))
            return
        data['x'] = variableCell.source[space].data['x'][kde_indices]
        data['y'] = variableCell.source[space].data['y'][kde_indices]
        data['y0'] = np.asarray(len(data['x'])*[0])
        variableCell.selection[space].data = data

    @staticmethod
    def update_reconstructed_cds_interactive(variableCell, space):
        """
            Updates reconstructed ColumnDataSource (cds).
        """
        samples = variableCell.samples[space].data['x']
        inds,_ = variableCell.ic.get_sample_inds(space)
        # if Tulen(inds):
        sel_sample = samples[inds]
        variableCell.reconstructed[space].data = pmf(sel_sample)
        # data cds
        data = variableCell.get_data_for_cur_idx_dims_values(variableCell.name)
        if data is not None:
            max_v = variableCell.get_max_prob(space)
            variableCell.data[space] =  ColumnDataSource(data = dict(x = data, y = np.asarray([-1*max_v/RUG_DIST_RATIO]*len(data))))
        # else:
        #     variableCell.reconstructed[space].data = dict(x = np.array([]), y = np.array([]), y0 = np.array([]))
        ##########TEST###################to be deleted
        # max_v = variableCell.get_max_prob(space)
        # if max_v!=-1:
        #     variableCell.samples[space].data['y'] = np.asarray([-1*max_v/RUG_DIST_RATIO]*len(variableCell.samples[space].data['x']))

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
                variableCell.ic.add_space_threads(threading.Thread(target = partial(CellDiscreteHandler._clear_selection_cds_update, variableCell, sp), daemon = True))
        variableCell.ic.space_threads_join()

    @staticmethod
    def _clear_selection_cds_update(variableCell, space):
        x_range = variableCell.ic.get_var_x_range(space, variableCell.name)
        xmin_list = x_range['xmin']
        xmax_list = x_range['xmax']
        if len(xmin_list):
            variableCell.update_selection_cds(space, xmin_list[0], xmax_list[0])
        else:
            variableCell.selection[space].data = dict(x = np.array([]), y = np.array([]), y0 = np.array([]))
        variableCell.ic.delete_sel_var_inds(space, variableCell.name)
        variableCell.compute_intersection_of_samples(space)
        variableCell.ic.selection_threads_join(space)
