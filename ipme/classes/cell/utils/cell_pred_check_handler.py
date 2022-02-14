from ipme.utils.constants import COLORS, BORDER_COLORS, PLOT_HEIGHT, PLOT_WIDTH, SIZING_MODE
from ipme.utils.functions import get_finite_samples, get_samples_for_pred_check, get_hist_bins_range
from ipme.utils.stats import hist

import numpy as np

from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, HoverTool, Legend
from bokeh import events

from functools import partial

class CellPredCheckHandler:

    def __init__(self):
        pass

    @staticmethod
    def initialize_glyphs_interactive(predcheckCell, space):
        q = predcheckCell.plot[space].quad(top='top', bottom='bottom', left='left', right='right', source=predcheckCell.source[space], \
                                  fill_color=COLORS[0], line_color="white", fill_alpha=1.0, name="full")
        seg = predcheckCell.plot[space].segment(x0 ='x0', y0 ='y0', x1='x1', y1='y1', source=predcheckCell.seg[space], \
                                       color="black", line_width=2, name="seg")
        q_sel = predcheckCell.plot[space].quad(top='top', bottom='bottom', left='left', right='right', source=predcheckCell.reconstructed[space], \
                                      fill_color=COLORS[1], line_color="white", fill_alpha=0.7, name="sel")
        ## Add Legends
        data = predcheckCell.seg[space].data['x0']
        pvalue = predcheckCell.pvalue[space].data["pv"]
        if len(data) and len(pvalue):
            legend = Legend(items=[ (predcheckCell.func + "(obs) = " + format(data[0], '.2f'), [seg]),
                                    ("p-value = "+format(pvalue[0],'.4f'), [q]),
                                    ], location="top_left")
            predcheckCell.plot[space].add_layout(legend, 'above')
        ## Add Tooltips for hist
        #####TODO:Correct overlap of tooltips#####
        TOOLTIPS = [
            ("top", "@top"),
            ("right","@right"),
            ("left","@left"),
            ]
        hover = HoverTool( tooltips=TOOLTIPS,renderers=[q,q_sel])
        predcheckCell.plot[space].tools.append(hover)

    @staticmethod
    def initialize_glyphs_static(predcheckCell, space):
        q = predcheckCell.plot[space].quad(top='top', bottom='bottom', left='left', right='right', source=predcheckCell.source[space], \
                                  fill_color=COLORS[0], line_color="white", fill_alpha=1.0, name="full")
        seg = predcheckCell.plot[space].segment(x0 ='x0', y0 ='y0', x1='x1', y1='y1', source=predcheckCell.seg[space], \
                                       color="black", line_width=2, name="seg")
        ## Add Legends
        data = predcheckCell.seg[space].data['x0']
        pvalue = predcheckCell.pvalue[space].data["pv"]
        if len(data) and len(pvalue):
            legend = Legend(items=[ (predcheckCell.func + "(obs) = " + format(data[0], '.2f'), [seg]),
                                    ("p-value = "+format(pvalue[0],'.4f'), [q]),
                                    ], location="top_left")
            predcheckCell.plot[space].add_layout(legend, 'above')
        ## Add Tooltips for hist
        #####TODO:Correct overlap of tooltips#####
        TOOLTIPS = [
            ("top", "@top"),
            ("right","@right"),
            ("left","@left"),
            ]
        hover = HoverTool( tooltips=TOOLTIPS,renderers=[q])
        predcheckCell.plot[space].tools.append(hover)

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
        data, samples = predcheckCell.get_samples_for_cur_idx_dims_values(space)
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
        predcheckCell.ic.initialize_sample_inds(space, dict(inds = [False]*len(predcheckCell.samples[space].data['x'])), dict(non_inds = [True]*len(predcheckCell.samples[space].data['x'])))

    @staticmethod
    def initialize_cds_interactive(predcheckCell, space):
        CellPredCheckHandler.initialize_cds(predcheckCell, space)
        ## ColumnDataSource for restricted sample set
        predcheckCell.pvalue_rec[space] = ColumnDataSource(data=dict(pv=[]))
        predcheckCell.pvalue_rec[space].on_change('data', partial(predcheckCell.update_legends, space))
        predcheckCell.reconstructed[space] = ColumnDataSource(data=dict(left=[], top=[], right=[], bottom=[]))

    @staticmethod
    def initialize_cds_static(predcheckCell, space):
        CellPredCheckHandler.initialize_cds(predcheckCell, space)

    @staticmethod
    def update_cds_interactive(predcheckCell, space):
        """
            Updates interaction-related ColumnDataSources (cds).
        """
        predcheckCell.update_sel_samples_cds(space)

    @staticmethod
    def update_cds_static(predcheckCell, space):
        """
            Update samples cds in the static mode
        """
        ## ColumnDataSource for full sample set
        data, samples = predcheckCell.get_samples_for_cur_idx_dims_values(space)
        inds, _ = predcheckCell.ic.get_sample_inds(space)
        if True in inds:
            samples = samples[inds]
        predcheckCell.samples[space].data = dict(x=samples)
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
            predcheckCell.pvalue[space].data = dict(pv=[pv])
            predcheckCell.source[space].data = dict(left=edges[:-1], top=his, right=edges[1:], bottom=np.zeros(len(his)))
            predcheckCell.seg[space].data = dict(x0=[data_func], x1=[data_func], y0=[0], y1=[his.max() + 0.1 * his.max()])
        else:
            predcheckCell.pvalue[space].data = dict(pv=[])
            predcheckCell.source[space].data = dict(left=[], top=[], right=[], bottom=[])
            predcheckCell.seg[space].data = dict(x0=[], x1=[], y0=[], y1=[])

    ## ONLY FOR INTERACTIVE CASE
    @staticmethod
    def update_source_cds_interactive(predcheckCell, space):
        """
            Updates samples ColumnDataSource (cds).
        """
        ## ColumnDataSource for full sample set
        data, samples = predcheckCell.get_samples_for_cur_idx_dims_values(space)
        predcheckCell.samples[space].data = dict(x=samples)
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
            predcheckCell.pvalue[space].data = dict(pv=[pv])
            predcheckCell.source[space].data = dict(left=edges[:-1], top=his, right=edges[1:], bottom=np.zeros(len(his)))
            predcheckCell.seg[space].data = dict(x0=[data_func], x1=[data_func], y0=[0], y1=[his.max() + 0.1 * his.max()])
        else:
            predcheckCell.pvalue[space].data = data=dict(pv=[])
            predcheckCell.source[space].data = dict(left=[], top=[], right=[], bottom=[])
            predcheckCell.seg[space].data = dict(x0=[], x1=[], y0=[], y1=[])

    @staticmethod
    def update_sel_samples_cds_interactive(predcheckCell, space):
        """
            Updates reconstructed ColumnDataSource (cds).
        """
        samples = predcheckCell.samples[space].data['x']
        max_full_hist = predcheckCell.source[space].data['top'].max()
        if samples.size:
            inds,_ = predcheckCell.ic.get_sample_inds(space)
            if True in inds:
                sel_sample = samples[inds]
                if ~np.isfinite(sel_sample).all():
                    sel_sample = get_finite_samples(sel_sample)
                sel_sample_func = get_samples_for_pred_check(sel_sample, predcheckCell.func)
                #data func
                data_func = predcheckCell.seg[space].data['x0'][0]
                #pvalue in restricted space
                sel_pv = np.count_nonzero(sel_sample_func >= data_func) / len(sel_sample_func)
                #compute updated histogram
                min_p = predcheckCell.source[space].data['left'][0]
                max_p = predcheckCell.source[space].data['right'][-1]
                min_c = sel_sample_func.min()
                max_c = sel_sample_func.max()
                if  min_c < min_p or max_c > max_p:
                    ref_len = predcheckCell.source[space].data['right'][0] - min_p
                    bins, range = get_hist_bins_range(sel_sample_func, predcheckCell.func, predcheckCell._type, ref_length=ref_len)
                else:
                    range = (min_p,max_p)
                    bins = len(predcheckCell.source[space].data['right'])
                his, edges = hist(sel_sample_func, bins=bins, range=range)
                ##max selected hist
                max_sel_hist = his.max()
                #update reconstructed cds
                predcheckCell.pvalue_rec[space].data = dict(pv=[sel_pv])
                predcheckCell.reconstructed[space].data = dict(left=edges[:-1], top=his, right =edges[1:], bottom=np.zeros(len(his)))
                predcheckCell.seg[space].data['y1'] = [max_sel_hist + 0.1 * max_sel_hist]
            else:
                predcheckCell.pvalue_rec[space].data = dict(pv=[])
                predcheckCell.reconstructed[space].data = dict(left=[], top=[], right=[], bottom=[])
                predcheckCell.seg[space].data['y1'] = [max_full_hist + 0.1 * max_full_hist]
        else:
            predcheckCell.pvalue_rec[space].data = dict(pv=[])
            predcheckCell.reconstructed[space].data = dict(left=[], top=[], right=[], bottom=[])
            predcheckCell.seg[space].data['y1'] = [max_full_hist + 0.1 * max_full_hist]
        

