from ipme.utils.constants import COLORS, BORDER_COLORS, PLOT_HEIGHT, PLOT_WIDTH, SIZING_MODE
from ipme.utils.functions import get_finite_samples, get_samples_for_pred_check, get_hist_bins_range
from ipme.utils.stats import hist

import numpy as np

from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, BoxSelectTool, HoverTool
from bokeh import events

from functools import partial

class CellPredCheckHandler:

    def __init__(self):
        pass

    @staticmethod
    def initialize_glyphs(predcheckCell, space):
        pass

    @staticmethod
    def initialize_glyphs_interactive(predcheckCell, space):
        pass

    @staticmethod
    def initialize_glyphs_static(predcheckCell, space):
        pass

    @staticmethod
    def initialize_fig(predcheckCell, space):
        predcheckCell.plot[space] = figure(tools = "wheel_zoom,reset", toolbar_location = 'right', plot_width = PLOT_WIDTH, plot_height = PLOT_HEIGHT, sizing_mode = SIZING_MODE)
        predcheckCell.plot[space].toolbar.logo = None
        predcheckCell.plot[space].yaxis.visible = False
        predcheckCell.plot[space].xaxis.axis_label = predcheckCell.func + "(" + predcheckCell.name + ")"
        predcheckCell.plot[space].border_fill_color = BORDER_COLORS[0]
        predcheckCell.plot[space].xaxis[0].ticker.desired_num_ticks = 3

    @staticmethod
    def initialize_fig_interactive(predcheckCell, space):
        CellPredCheckHandler.initialize_fig(predcheckCell, space)
        predcheckCell.ic.sample_inds[space].on_change('data', partial(predcheckCell.sample_inds_callback, space))

    @staticmethod
    def initialize_fig_static(predcheckCell, space):
        CellPredCheckHandler.initialize_fig(predcheckCell, space)

    @staticmethod
    def initialize_cds(predcheckCell, space):
        ## ColumnDataSource for full sample set
        data, samples = predcheckCell.get_data_for_cur_idx_dims_values(space)
        predcheckCell.samples[space] = ColumnDataSource(data=dict(x=samples))
        #data func
        if ~np.isfinite(data).all():
            data = get_finite_samples(data)
        data_func = get_samples_for_pred_check(data, predcheckCell.func)
        #samples func
        if ~np.isfinite(samples).all():
            samples = get_finite_samples(samples)
        samples_func = get_samples_for_pred_check(samples, predcheckCell.func)
        if samples_func.size:
            #pvalue
            pv = np.count_nonzero(samples_func>=data_func) / len(samples_func)
            #histogram     
            type =  predcheckCell._data.get_var_dist_type(predcheckCell.name)          
            if type == "Continuous":
                bins, range = get_hist_bins_range(samples_func, predcheckCell.func, type)
            else:
                bins, range = get_hist_bins_range(samples_func, predcheckCell.func, type, ref_length = None, ref_values=np.unique(samples.flatten()))

            his, edges = hist(samples_func, bins=bins, range=range, density = True)
            #cds
            predcheckCell.pvalue[space] = ColumnDataSource(data=dict(pv=[pv]))
            predcheckCell.source[space] = ColumnDataSource(data=dict(left=edges[:-1], top=his, right=edges[1:], bottom=np.zeros(len(his))))
            predcheckCell.seg[space] = ColumnDataSource(data=dict(x0=[data_func], x1=[data_func], y0=[0], y1=[his.max() + 0.1 * his.max()]))
        else:
            predcheckCell.pvalue[space] = ColumnDataSource(data=dict(pv=[]))
            predcheckCell.source[space] = ColumnDataSource(data=dict(left=[], top=[], right=[], bottom=[]))
            predcheckCell.seg[space] = ColumnDataSource(data=dict(x0=[], x1=[], y0=[], y1=[]))

    @staticmethod
    def initialize_cds_interactive(predcheckCell, space):
        CellPredCheckHandler.initialize_cds(predcheckCell, space)
        ## ColumnDataSource for restricted sample set
        predcheckCell.pvalue_rec[space] = ColumnDataSource(data=dict(pv=[]))
        predcheckCell.pvalue_rec[space].on_change('data', partial(predcheckCell._update_legends, space))
        predcheckCell.reconstructed[space] = ColumnDataSource(data=dict(left=[], top=[], right=[], bottom=[]))

    @staticmethod
    def initialize_cds_static(predcheckCell, space):
        CellPredCheckHandler.initialize_cds(predcheckCell, space)
