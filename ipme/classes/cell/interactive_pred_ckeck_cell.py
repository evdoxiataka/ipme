from ipme.interfaces.predictive_check_cell import PredictiveCheckCell
from .utils.cell_pred_check_handler import CellPredCheckHandler
from ..cell.utils.cell_widgets import CellWidgets

# from ipme.utils.stats import hist
# from ipme.utils.functions import get_finite_samples, get_samples_for_pred_check, get_hist_bins_range
# from ipme.utils.constants import COLORS

# import numpy as np
from bokeh.models import LegendItem

# import threading
# from abc import abstractmethod

class InteractivePredCheckCell(PredictiveCheckCell):
    def __init__(self, name, control, function = 'min'):
        """
            Parameters:
            --------
                name            A String within the set {"<variableName>"}.
                function        A String in {"min","max","mean","std"}.
            Sets:
            --------
                func
                source
                reconstructed
                samples
                seg
        """
        self.func = function
        PredictiveCheckCell.__init__(self, name, control)

    def initialize_cds(self, space):
        CellPredCheckHandler.initialize_cds_interactive(self, space)

    def initialize_fig(self, space):
        CellPredCheckHandler.initialize_fig_interactive(self, space)

    def initialize_glyphs(self, space):
        CellPredCheckHandler.initialize_glyphs_interactive(self, space)

    def widget_callback(self, attr, old, new, w_title, space):
        CellWidgets.widget_callback_interactive(self, attr, old, new, w_title, space)

    def update_cds(self, space):
        CellPredCheckHandler.update_cds_interactive(self, space)

    ## ONLY FOR INTERACTIVE CASE
    def update_source_cds(self, space):
        CellPredCheckHandler.update_source_cds_interactive(self, space)

    def update_sel_samples_cds(self, space):
        CellPredCheckHandler.update_sel_samples_cds_interactive(self, space)

    # def initialize_glyphs(self,space):
    #     q = self.plot[space].quad(top='top', bottom='bottom', left='left', right='right', source=self.source[space], \
    #                               fill_color=COLORS[0], line_color="white", fill_alpha=1.0, name="full")
    #     seg = self.plot[space].segment(x0 ='x0', y0 ='y0', x1='x1', y1='y1', source=self.seg[space], \
    #                                    color="black", line_width=2, name="seg")
    #     q_sel = self.plot[space].quad(top='top', bottom='bottom', left='left', right='right', source=self.reconstructed[space], \
    #                                   fill_color=COLORS[1], line_color="white", fill_alpha=0.7, name="sel")
    #     ## Add Legends
    #     data = self.seg[space].data['x0']
    #     pvalue = self.pvalue[space].data["pv"]
    #     if len(data) and len(pvalue):
    #         legend = Legend(items=[ (self.func + "(obs) = " + format(data[0], '.2f'), [seg]),
    #                                 ("p-value = "+format(pvalue[0],'.4f'), [q]),
    #                                 ], location="top_left")
    #         self.plot[space].add_layout(legend, 'above')
    #     ## Add Tooltips for hist
    #     #####TODO:Correct overlap of tooltips#####
    #     TOOLTIPS = [
    #         ("top", "@top"),
    #         ("right","@right"),
    #         ("left","@left"),
    #         ]
    #     hover = HoverTool( tooltips=TOOLTIPS,renderers=[q,q_sel])
    #     self.plot[space].tools.append(hover)

    ## Update legends when data in _pvalue_rec cds is updated
    def update_legends(self, space, attr, old, new):
        if len(self.plot[space].legend.items) == 3:
            self.plot[space].legend.items.pop()
        r = self.plot[space].select(name="sel")
        pvalue = self.pvalue_rec[space].data["pv"]
        if len(r) and len(pvalue):
            self.plot[space].legend.items.append(LegendItem(label="p-value = " + format(pvalue[0], '.4f'), \
                                                            renderers=[r[0]]))

    # def widget_callback(self, attr, old, new, w_title, space):
    #     inds = self.ic.data.get_indx_for_idx_dim(self.name, w_title, new)
    #     if inds==-1:
    #         return
    #     self.cur_idx_dims_values[self.name][w_title] = inds
    #     self._update_plot(space)

    # def _update_plot(self, space):
    #     pass

    # def initialize_cds(self, space):
    #     CellPredCheckHandler.initialize_cds_interactive(self, space)
    #     # ## ColumnDataSource for full sample set
    #     # data, samples = self.get_data_for_cur_idx_dims_values(space)
    #     # self.samples[space] = ColumnDataSource(data=dict(x=samples))
    #     # #data func
    #     # if ~np.isfinite(data).all():
    #     #     data = get_finite_samples(data)
    #     # data_func = get_samples_for_pred_check(data, self.func)
    #     # #samples func
    #     # if ~np.isfinite(samples).all():
    #     #     samples = get_finite_samples(samples)
    #     # samples_func = get_samples_for_pred_check(samples, self.func)
    #     # if samples_func.size:
    #     #     #pvalue
    #     #     pv = np.count_nonzero(samples_func>=data_func) / len(samples_func)
    #     #     #histogram     
    #     #     type =  self._data.get_var_dist_type(self.name)          
    #     #     if type == "Continuous":
    #     #         bins, range = get_hist_bins_range(samples_func, self.func, type)
    #     #     else:
    #     #         bins, range = get_hist_bins_range(samples_func, self.func, type, ref_length = None, ref_values=np.unique(samples.flatten()))

    #     #     his, edges = hist(samples_func, bins=bins, range=range, density=True)
    #     #     #cds
    #     #     self.pvalue[space] = ColumnDataSource(data=dict(pv=[pv]))
    #     #     self.source[space] = ColumnDataSource(data=dict(left=edges[:-1], top=his, right=edges[1:], bottom=np.zeros(len(his))))
    #     #     self.seg[space] = ColumnDataSource(data=dict(x0=[data_func], x1=[data_func], y0=[0], y1=[his.max() + 0.1 * his.max()]))
    #     # else:
    #     #     self.pvalue[space] = ColumnDataSource(data=dict(pv=[]))
    #     #     self.source[space] = ColumnDataSource(data=dict(left=[], top=[], right=[], bottom=[]))
    #     #     self.seg[space] = ColumnDataSource(data=dict(x0=[], x1=[], y0=[], y1=[]))

    #     # ## ColumnDataSource for restricted sample set
    #     # self.pvalue_rec[space] = ColumnDataSource(data=dict(pv=[]))
    #     # self.pvalue_rec[space].on_change('data', partial(self._update_legends, space))
    #     # self.reconstructed[space] = ColumnDataSource(data=dict(left=[], top=[], right=[], bottom=[]))

    # ## Update plots when indices of selected samples are updated
    # def sample_inds_callback(self, space, attr, old, new):
    #     # _, samples = self._get_data_for_cur_idx_dims_values(space)
    #     samples = self.samples[space].data['x']
    #     max_full_hist = self.source[space].data['top'].max()
    #     if samples.size:
    #         inds=self.ic.sample_inds[space].data['inds']
    #         if len(inds):
    #             sel_sample = samples[inds]
    #             if ~np.isfinite(sel_sample).all():
    #                 sel_sample = get_finite_samples(sel_sample)
    #             sel_sample_func = get_samples_for_pred_check(sel_sample, self.func)
    #             #data func
    #             data_func = self.seg[space].data['x0'][0]
    #             #pvalue in restricted space
    #             sel_pv = np.count_nonzero(sel_sample_func >= data_func) / len(sel_sample_func)
    #             #compute updated histogram
    #             min_p = self.source[space].data['left'][0]
    #             max_p = self.source[space].data['right'][-1]
    #             min_c = sel_sample_func.min()
    #             max_c = sel_sample_func.max()
    #             if  min_c < min_p or max_c > max_p:
    #                 ref_len = self.source[space].data['right'][0] - min_p
    #                 bins, range = get_hist_bins_range(sel_sample_func, self.func, self._type, ref_length=ref_len)
    #             else:
    #                 range = (min_p,max_p)
    #                 bins = len(self.source[space].data['right'])
    #             his, edges = hist(sel_sample_func, bins=bins, range=range)
    #             ##max selected hist
    #             max_sel_hist = his.max()
    #             #update reconstructed cds
    #             self.pvalue_rec[space].data = dict(pv=[sel_pv])
    #             self.reconstructed[space].data = dict(left=edges[:-1], top=his, right =edges[1:], bottom=np.zeros(len(his)))
    #             self.seg[space].data['y1'] = [max_sel_hist + 0.1 * max_sel_hist]
    #         else:
    #             self.pvalue_rec[space].data = dict(pv=[])
    #             self.reconstructed[space].data = dict(left=[], top=[], right=[], bottom=[])
    #             self.seg[space].data['y1'] = [max_full_hist + 0.1 * max_full_hist]
    #     else:
    #         self.pvalue_rec[space].data = dict(pv=[])
    #         self.reconstructed[space].data = dict(left=[], top=[], right=[], bottom=[])
    #         self.seg[space].data['y1'] = [max_full_hist + 0.1 * max_full_hist]
