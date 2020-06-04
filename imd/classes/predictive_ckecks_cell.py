from ..interfaces.grid import Cell
from ..utils.stats import hist
from ..utils.functions import get_finite_samples, get_samples_for_pred_check, get_hist_bins_range

import numpy as np
from functools import partial

from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, HoverTool, Legend, LegendItem

class PredictiveChecksCell(Cell):
    def __init__(self, name, function='min'):
        """
            Parameters:
            --------
                name            A String within the set {"<variableName>"}.
                function        A String in {"min","max","mean","std"}.
            Sets:
            --------
                _func
                _source
                _reconstructed
                _seg

        """   
        self._func=function       
        self._source={} 
        self._reconstructed={} 
        self._seg={}
        self._pvalue = {} 
        self._pvalue_rec = {}        
        Cell.__init__(self, name) 

    def _get_data_for_cur_idx_dims_values(self,space):
        """
            Returns the x-,y-coordinates of the data for current index dimensions values.

            Returns:
            --------
                A Tuple (x,y) of the x-,y-coordinates of the data.
        """ 
        data = Cell._data.get_samples(self._name,'observed_data')
        if Cell._data.get_var_type(self._name) == "observed":
            if space == "posterior" and "posterior_predictive" in Cell._data.get_spaces():
                space="posterior_predictive"
            elif space == "prior" and "prior_predictive" in Cell._data.get_spaces():
                space="prior_predictive"
        samples = Cell._data.get_samples(self._name,space)            
        return (data,samples)     

    def initialize_fig(self,space):        
        self._plot[space] = figure(tools="wheel_zoom,reset", toolbar_location='right', plot_width=Cell._PLOT_WIDTH, 
                                    plot_height=Cell._PLOT_HEIGHT, sizing_mode=Cell._SIZING_MODE)        
        self._plot[space].toolbar.logo = None  
        self._plot[space].xaxis.axis_label = self._func+"("+self._name+")"
        self._plot[space].border_fill_color = Cell._BORDER_COLORS[0]
        self._plot[space].xaxis[0].ticker.desired_num_ticks = 3
        Cell._sample_inds[space].on_change('data',partial(self._sample_inds_callback, space))
    
    def initialize_cds(self,space):
        ## ColumnDataSource for full sample set
        data, samples = self._get_data_for_cur_idx_dims_values(space) 
        #data func
        if ~np.isfinite(data).all():
            data = get_finite_samples(data)
        data_func = get_samples_for_pred_check(data, self._func)
        #samples func
        if ~np.isfinite(samples).all():
            samples = get_finite_samples(samples)
        samples_func = get_samples_for_pred_check(samples, self._func)
        samples = samples.flatten()        
        if samples.size:
            #pvalue            
            pv = np.count_nonzero(samples_func>=data_func) / len(samples_func)               
            #histogram     
            bins, range = get_hist_bins_range(samples, self._type)
            his, edges = hist(samples_func, bins=bins, range=range, density=True)
            #cds
            self._pvalue[space] = ColumnDataSource(data=dict(pv=[pv]))
            self._source[space] = ColumnDataSource(data=dict(left=edges[:-1],top=his,right=edges[1:], bottom=np.zeros(len(his))))
            self._seg[space] = ColumnDataSource(data=dict(x0=[data_func],x1=[data_func],y0=[0],y1=[his.max()+0.1*his.max()]))
        else:
            self._pvalue[space] = ColumnDataSource(data=dict(pv=[]))
            self._source[space] = ColumnDataSource(data=dict(left=[],top=[],right=[], bottom=[]))
            self._seg[space] = ColumnDataSource(data=dict(x0=[],x1=[],y0=[],y1=[]))

        ## ColumnDataSource for restricted sample set
        self._pvalue_rec[space] = ColumnDataSource(data=dict(pv=[]))
        self._pvalue_rec[space].on_change('data',partial(self._update_legends, space))
        self._reconstructed[space] = ColumnDataSource(data=dict(left=[],top=[],right=[], bottom=[]))        

    def initialize_glyphs(self,space):        
        q = self._plot[space].quad(top='top', bottom='bottom', left='left', right='right', source=self._source[space], \
                                fill_color=Cell._COLORS[0], line_color="white", fill_alpha=1.0,name="full")
        seg = self._plot[space].segment(x0 = 'x0', y0 ='y0', x1='x1',y1='y1', source=self._seg[space], \
                                 color="black", line_width=2,name="seg")
        q_sel = self._plot[space].quad(top='top', bottom='bottom', left='left', right='right', source=self._reconstructed[space], \
                                    fill_color=Cell._COLORS[1], line_color="white", fill_alpha=0.7,name="sel")
        ## Add Legends
        data = self._seg[space].data['x0']
        pvalue = self._pvalue[space].data["pv"]
        if len(data) and len(pvalue):
            legend = Legend(items=[ (self._func+"(obs) = "+format(data[0],'.2f'), [seg]),
                                    ("p-value = "+format(pvalue[0],'.4f'), [q]),
                                    ], location="top_left")
            self._plot[space].add_layout(legend, 'above')
        ## Add Tooltips for hist
        #####TODO:Correct overlap of tooltips#####
        TOOLTIPS = [
            ("top", "@top"),
            ("right","@right"),
            ("left","@left"),
            ]
        hover = HoverTool( tooltips=TOOLTIPS,renderers=[q,q_sel])
        self._plot[space].tools.append(hover)

    def _initialize_plot(self):
        for space in self._spaces:
            self.initialize_cds(space)
            self.initialize_fig(space)
            self.initialize_glyphs(space)            

    ## Update legends when data in _pvalue_rec cds is updated
    def _update_legends(self, space, attr, old, new):
        if len(self._plot[space].legend.items) == 3:
            self._plot[space].legend.items.pop()
        r = self._plot[space].select(name="sel")
        pvalue = self._pvalue_rec[space].data["pv"]
        if len(r) and len(pvalue):
            self._plot[space].legend.items.append(LegendItem(label="p-value = "+format(pvalue[0],'.4f'), \
                                                                renderers=[r[0]]))

    ## Update plots when indices of selected samples are updated
    def _sample_inds_callback(self, space, attr, old, new):
        _, samples = self._get_data_for_cur_idx_dims_values(space)        
        if samples.size:            
            inds=Cell._sample_inds[space].data['inds']
            if len(inds):
                sel_sample = samples[inds]
                #sel_sample func
                if ~np.isfinite(sel_sample).all():
                    sel_sample = get_finite_samples(sel_sample)
                sel_sample_func = get_samples_for_pred_check(sel_sample, self._func)
                sel_sample = sel_sample.flatten()
                #data func
                data_func = self._seg[space].data['x0'][0]
                #pvalue in restricted space
                sel_pv = np.count_nonzero(sel_sample_func >= data_func) / len(sel_sample_func)                 
                #compute updated histogram
                bins, range = get_hist_bins_range(sel_sample, self._type)
                his, edges = hist(sel_sample_func, bins=bins, range=range)
                #update reconstructed cds
                self._pvalue_rec[space].data = dict(pv=[sel_pv])
                self._reconstructed[space].data = dict(left=edges[:-1],top=his, right = edges[1:], bottom=np.zeros(len(his)))
            else:
                self._pvalue_rec[space].data = dict(pv=[])
                self._reconstructed[space].data = dict(left=[],top=[],right=[], bottom=[])
        else:
            self._pvalue_rec[space].data = dict(pv=[])
            self._reconstructed[space].data = dict(left=[],top=[],right=[], bottom=[])  

    def _update_plot(self,space):
        pass

    def _widget_callback(self, attr, old, new, w_title, space):
        inds = Cell._data.get_indx_for_idx_dim(self._name, w_title, new)
        if inds==-1:
            return
        self._cur_idx_dims_values[w_title]=inds
        self._update_plot(space)