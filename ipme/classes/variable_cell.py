from ..interfaces.cell import Cell
from ..utils.functions import * 
from ..utils.stats import kde, pmf, find_x_range
from ..utils.js_code import HOVER_CODE
from ..utils.constants import COLORS, BORDER_COLORS, PLOT_HEIGHT, PLOT_WIDTH, SIZING_MODE, RUG_DIST_RATIO, RUG_SIZE

from functools import partial
import threading

from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, BoxSelectTool, HoverTool,  CustomJS
from bokeh import events

class VariableCell(Cell):   
    def __init__(self, name, mode):
        """
            Parameters:
            --------
                name            A String within the set {"<variableName>"}.
                mode            A String in {"i","s"}, "i":interactive, "s":static.
            Sets:
            --------
                _source
                _selection
                _reconstructed
                _samples
        """         
        self._source = {} 
        self._selection = {} 
        self._reconstructed = {} 
        self._samples = {}
        self._sel_samples = {}
        self._clear_selection = {}  
        self._all_samples = {}
        self._x_range = {}
        Cell.__init__(self, name, mode) 

    def _get_samples(self, space): 
        """
            Retrieves MCMC samples of <space> into a numpy.ndarray and 
            sets an entry into self._all_samples Dict.
        """
        space_gsam = space
        if Cell._data.get_var_type(self._name) == "observed":
            if space == "posterior" and "posterior_predictive" in Cell._data.get_spaces():
                space_gsam="posterior_predictive"
            elif space == "prior" and "prior_predictive" in Cell._data.get_spaces():
                space_gsam="prior_predictive"
        self._all_samples[space] = Cell._data.get_samples(self._name, space_gsam).T
        # compute x_range
        self._x_range[space] = find_x_range(self._all_samples[space])
                
    def _get_data_for_cur_idx_dims_values(self, space):
        """
            Returns a numpy.ndarray of the MCMC samples of the <name>  
            parameter for current index dimensions values.

            Returns:
            --------
                A numpy.ndarray.
        """ 
        if space in self._all_samples:
            data =  self._all_samples[space] 
        else:
            raise ValueError   
        for dim_name,dim_value in self._cur_idx_dims_values.items():
            data = data[dim_value]
        return np.squeeze(data).T
    
    def initialize_fig(self,space):
        self._plot[space]=figure( x_range = self._x_range[space], tools="wheel_zoom,reset,box_zoom", toolbar_location='right', 
                            plot_width=PLOT_WIDTH, plot_height=PLOT_HEIGHT,  sizing_mode=SIZING_MODE)            
        self._plot[space].border_fill_color = BORDER_COLORS[0]    
        self._plot[space].xaxis.axis_label = ""
        self._plot[space].yaxis.visible = False            
        self._plot[space].toolbar.logo = None
        # self._plot[space].y_range.only_visible = True
        # self._plot[space].x_range.only_visible = True
        self._plot[space].xaxis[0].ticker.desired_num_ticks = 3    
        if self._mode == "i":    
            ##Events
            self._plot[space].on_event(events.Tap, partial(self._clear_selection_callback,space))             
            self._plot[space].on_event(events.SelectionGeometry, partial(self._selectionbox_callback,space))   
            ##on_change  
            # Cell._var_x_range[(space,self._name)].on_change('data',partial(self._var_x_range_callback, space))       
        # Cell._sample_inds[space].on_change('data',partial(self._sample_inds_callback, space))
        Cell._sample_inds_update[space].on_change('data',partial(self._sample_inds_callback, space))
        
    def initialize_cds(self,space):
        samples = self._get_data_for_cur_idx_dims_values(space)  
        if self._type == "Discrete":
            self._source[space] = ColumnDataSource(data = pmf(samples))
            self._samples[space] = ColumnDataSource(data = dict(x=samples))
            self._selection[space] = ColumnDataSource(data=dict(x=np.array([]), y=np.array([]), y0=np.array([]))) 
            self._reconstructed[space] = ColumnDataSource(data=dict(x=np.array([]), y=np.array([]), y0=np.array([]))) 
        else:            
            self._source[space] = ColumnDataSource(data = kde(samples)) 
            max_v = self._source[space].data['y'].max()
            self._samples[space] = ColumnDataSource(data = dict(x=samples, y=np.asarray([-max_v/RUG_DIST_RATIO]*len(samples)),\
                                                                size=np.asarray([RUG_SIZE]*len(samples))))  
            self._sel_samples[space] = ColumnDataSource(data = dict(x=np.array([]), y=np.array([]),\
                                                                    size=np.array([])))   
            self._selection[space] = ColumnDataSource(data=dict(x=np.array([]),y=np.array([]))) 
            self._reconstructed[space] = ColumnDataSource(data=dict(x=np.array([]),y=np.array([])))    
        self._clear_selection[space] = ColumnDataSource(data=dict(x=[],y=[],isIn=[])) 
        Cell._var_x_range[(space,self._name)] = ColumnDataSource(data=dict(xmin=np.array([]),xmax=np.array([])))

    def initialize_glyphs(self,space):
        if self._type == "Discrete":
            self.initialize_glyphs_discrete(space)             
        else:
            self.initialize_glyphs_continuous(space)
        if self._mode == "i":
            self.initialize_glyphs_x_button(space)

    def initialize_glyphs_discrete(self,space):
        so_seg=self._plot[space].segment(x0 = 'x', y0 ='y0', x1='x', y1='y', source=self._source[space], \
                                        line_alpha=1.0, color = COLORS[0], line_width=1, selection_color=COLORS[0],
                                        nonselection_color=COLORS[0], nonselection_line_alpha=1.0)
        so_scat=self._plot[space].scatter('x', 'y', source=self._source[space], size=4, fill_color=COLORS[0], \
                                          fill_alpha=1.0, line_color=COLORS[0], selection_fill_color=COLORS[0], \
                                          nonselection_fill_color=COLORS[0], nonselection_fill_alpha=1.0, \
                                          nonselection_line_color=COLORS[0])   
        self._plot[space].segment(x0 = 'x', y0 ='y0', x1='x', y1='y', source=self._selection[space], \
                                  line_alpha=0.7, color = COLORS[2], line_width=1)
        self._plot[space].scatter('x', 'y', source=self._selection[space], size=4, fill_color=COLORS[2], \
                                  fill_alpha=0.7, line_color=COLORS[2])
        self._plot[space].segment(x0 = 'x', y0 ='y0', x1='x', y1='y', source=self._reconstructed[space], \
                                  line_alpha=0.5, color = COLORS[1], line_width=1)
        self._plot[space].scatter('x', 'y', source=self._reconstructed[space], size=4, fill_color=COLORS[1], \
                                  fill_alpha=0.5, line_color=COLORS[1])
        if self._mode == "i":
            ##Add BoxSelectTool
            self._plot[space].add_tools(BoxSelectTool(dimensions='width',renderers=[so_seg,so_scat]))

    def initialize_glyphs_continuous(self,space):
        so=self._plot[space].line('x', 'y', line_color = COLORS[0], line_width = 2, source=self._source[space])       
        re=self._plot[space].line('x', 'y', line_color = COLORS[1], line_width = 2, source=self._reconstructed[space])        
        self._plot[space].line('x', 'y', line_color = COLORS[2], line_width = 2, source=self._selection[space])
        self._plot[space].dash('x','y', size='size',angle=90.0, angle_units='deg', line_color = COLORS[0], \
                                        source=self._samples[space])
        self._plot[space].dash('x','y', size='size',angle=90.0, angle_units='deg', line_color = COLORS[1], \
                                        source=self._sel_samples[space])
        if self._mode == "i":
            ##Add BoxSelectTool
            self._plot[space].add_tools(BoxSelectTool(dimensions='width',renderers=[so]))
            TOOLTIPS = [
            ("x", "@x"),
            ("y","@y"),
            ]
            hover = HoverTool( tooltips=TOOLTIPS,renderers=[so,re], mode='mouse')
            self._plot[space].tools.append(hover)

    def initialize_glyphs_x_button(self,space):
        ## x-button to clear selection
        sq_x=self._plot[space].scatter('x', 'y', marker="square_x", size=10, fill_color="grey", hover_fill_color="firebrick", \
                                        fill_alpha=0.5, hover_alpha=1.0, line_color="grey", hover_line_color="white", \
                                        source=self._clear_selection[space], name='clear_selection')
        ## Add HoverTool for x-button
        self._plot[space].add_tools(HoverTool(tooltips="Clear Selection", renderers=[sq_x], mode='mouse', show_arrow=False, 
                                        callback=CustomJS(args=dict(source=self._clear_selection[space]), code=HOVER_CODE)))

    def _initialize_plot(self):         
        for space in self._spaces: 
            self._get_samples(space)
            self.initialize_cds(space)
            self.initialize_fig(space)
            self.initialize_glyphs(space)   

    def _widget_callback(self, attr, old, new, w_title, space): 
        """
            Callback called when an indexing dimension is set to 
            a new coordinate (e.g through indexing dimensions widgets).
        """         
        print("ald",old,"new",new)
        if old == new:
            return        
        Cell._add_widget_threads(threading.Thread(target=partial(self._widget_callback_thread,new,w_title,space), daemon=True))
        Cell._widget_lock_event.set()
        
    def _widget_callback_thread(self, new, w_title, space):
        print("_widg_call")
        inds = -1
        w2_title = ""   
        values = []          
        w1_w2_idx_mapping = self._w1_w2_idx_mapping
        w2_w1_idx_mapping = self._w2_w1_idx_mapping
        w2_w1_val_mapping = self._w2_w1_val_mapping
        widgets = self._widgets[space]       
        if space in w1_w2_idx_mapping and \
            w_title in w1_w2_idx_mapping[space]:
            w2_title  = w1_w2_idx_mapping[space][w_title]
            name = w_title+"_idx_"+w2_title
            if name in self._idx_dims:
                values = self._idx_dims[name].values
        elif w_title in self._idx_dims:
            values = self._idx_dims[w_title].values  
        elif space in w2_w1_idx_mapping and \
            w_title in w2_w1_idx_mapping[space]:
            w1_idx = w2_w1_idx_mapping[space][w_title]
            w1_value = widgets[w1_idx].value
            values = w2_w1_val_mapping[space][w_title][w1_value]
        inds = [i for i,v in enumerate(values) if v == new]
        if inds == -1 or len(inds) == 0:
            return
        self._cur_idx_dims_values[w_title] = inds
        if w2_title and w2_title in self._cur_idx_dims_values:
            self._cur_idx_dims_values[w2_title] = [0]        
        if self._mode == 'i':
            self._update_source_cds(space)
            Cell._set_global_update(True)
            self._update_cds_interactive(space)
        elif self._mode == 's':
            self._update_cds_static(space)

    def _clear_selection_callback(self,space,event):
        """
            Callback called when clear selection glyph is clicked.
        """
        isIn = self._clear_selection[space].data['isIn']
        if 1 in isIn:
            Cell._set_var_x_range(space,self._name,dict(xmin=np.array([]),xmax=np.array([])))
            Cell._delete_sel_var_idx_dims_values(self._name)
            for sp in self._spaces:  
                Cell._add_space_threads(threading.Thread(target=partial(self._clear_selection_thread,sp), daemon=True)) 
        Cell._space_threads_join()

    def _clear_selection_thread(self,space):
        x_range = Cell._get_var_x_range(space,self._name)
        xmin_list = x_range['xmin']
        xmax_list = x_range['xmax']
        if len(xmin_list):
            self._update_selection_cds(space, xmin_list[0], xmax_list[0])
        else:
            if self._type == "Discrete":
                self._selection[space].data=dict(x=np.array([]),y=np.array([]),y0=np.array([]))
            else:
                self._selection[space].data=dict(x=np.array([]),y=np.array([]))
        Cell._delete_sel_var_inds(space,self._name)
        self._compute_intersection_of_samples(space)
        Cell._selection_threads_join(space)

    def _update_cds_interactive(self,space):
        """
            Updates interaction-related ColumnDataSources (cds).
        """
        sel_var_idx_dims_values = Cell._get_sel_var_idx_dims_values()
        sel_space = Cell._get_sel_space()
        var_x_range = Cell._get_var_x_range()
        global_update = Cell._get_global_update()
        if(global_update):
            if (self._name in sel_var_idx_dims_values and space == sel_space and 
                self._cur_idx_dims_values == sel_var_idx_dims_values[self._name]):
                self._update_selection_cds(space, var_x_range[(space,self._name)].data['xmin'][0],\
                                            var_x_range[(space,self._name)].data['xmax'][0])
            else:
                if self._type == "Discrete":
                    self._selection[space].data=dict(x=np.array([]),y=np.array([]),y0=np.array([]))
                else:
                    self._selection[space].data=dict(x=np.array([]),y=np.array([]))
        self._update_reconstructed_cds(space) 
        self._update_clear_selection_cds(space)

    def _sample_inds_callback(self, space, attr, old, new):
        """
            Updates cds when indices of selected samples -- Cell._sample_inds--
            are updated.
        """
        Cell._add_selection_threads(space,threading.Thread(target=self._sample_inds_thread, args=(space,), daemon=True))
        Cell._sel_lock_event.set()

    def _sample_inds_thread(self,space):
        if self._mode == 'i':
            self._update_cds_interactive(space)  
        elif self._mode == 's':
            self._update_cds_static(space)

    def _update_cds_static(self,space):
        """
            Update source & samples cds in the static mode
        """
        samples = self._get_data_for_cur_idx_dims_values(space) 
        inds = Cell._get_sample_inds(space)
        if len(inds):
            sel_sample = samples[inds]   
            if self._type == "Discrete":
                self._source[space].data = pmf(sel_sample)       
            else:    
                self._source[space].data = kde(sel_sample)  
                max_v = self._get_max_prob(space)
                self._samples[space].data = dict(x=sel_sample,y=np.asarray([-max_v/RUG_DIST_RATIO]*len(sel_sample)),\
                                                    size=np.asarray([RUG_SIZE]*len(sel_sample)))           
        else:
            if self._type == "Discrete":
                self._source[space].data = pmf(samples) 
            else:
                self._source[space].data = kde(samples)  
                max_v = self._get_max_prob(space)
                self._samples[space].data = dict(x=samples,y=np.asarray([-max_v/RUG_DIST_RATIO]*len(samples)),\
                                                    size=np.asarray([RUG_SIZE]*len(samples)))

    def set_stratum(self, space, stratum = 0):
        """
            Sets selection by spliting the ordered sample set 
            in 4 equal-sized subsets.
        """
        samples = self._get_data_for_cur_idx_dims_values(space) 
        xmin,xmax = get_stratum_range(samples,stratum)
        if self._mode == 'i':
            Cell._sel_space=space
            Cell._var_x_range[(space,self._name)].data=dict(xmin=np.asarray([xmin]),xmax=np.asarray([xmax]))             
            Cell._sel_var_idx_dims_values[self._name]=dict(self._cur_idx_dims_values)   
        inds = find_indices(samples, lambda e: e >= xmin and e<= xmax,xmin,xmax)  
        self._set_sel_var_inds(space, self._name, inds)     
        self._compute_intersection_of_samples(space)
        return (xmin,xmax)

    def _selectionbox_callback(self, space, event):
        """
            Callback called when selection box is drawn.
        """
        xmin=event.geometry['x0']
        xmax=event.geometry['x1']
        Cell._set_sel_space(space)
        Cell._set_var_x_range(space,self._name,dict(xmin=np.asarray([xmin]),xmax=np.asarray([xmax])))
        Cell._set_sel_var_idx_dims_values(self._name,dict(self._cur_idx_dims_values))  
        for sp in self._spaces:
            samples = self._samples[sp].data['x']
            Cell._add_space_threads(threading.Thread(target=partial(self._selectionbox_space_thread,sp,samples, xmin, xmax), daemon=True)) 
        Cell._space_threads_join()

    def _selectionbox_space_thread(self, space, samples, xmin, xmax):
        x_range = Cell._get_var_x_range(space,self._name)
        xmin_list = x_range['xmin']
        xmax_list = x_range['xmax']
        if len(xmin_list):
            self._update_selection_cds(space, xmin_list[0], xmax_list[0])
        else:
            if self._type == "Discrete":
                self._selection[space].data=dict(x=np.array([]),y=np.array([]),y0=np.array([]))
            else:
                self._selection[space].data=dict(x=np.array([]),y=np.array([]))
        inds = find_indices(samples, lambda e: e >= xmin and e<= xmax,xmin,xmax) 
        Cell._set_sel_var_inds(space, self._name, inds)
        self._compute_intersection_of_samples(space)
        Cell._selection_threads_join(space)       

    def _compute_intersection_of_samples(self,space):  
        """
            Computes intersection of sample points based on user's 
            restrictions per parameter.
        """
        sel_var_inds = self._get_sel_var_inds()  
        sp_keys=[k for k in sel_var_inds if k[0]==space]
        if len(sp_keys)>1:
            sets=[]
            for i in range(0, len(sp_keys)):
                sets.append(set(sel_var_inds[sp_keys[i]]))
            union=set.intersection(*sorted(sets, key=len))
            self._set_sample_inds(space,dict(inds=list(union)))
        elif len(sp_keys)==1:
            self._set_sample_inds(space,dict(inds=sel_var_inds[sp_keys[0]]))
        else:
            self._set_sample_inds(space,dict(inds=[]))        

    def _update_source_cds(self,space):
        """
            Updates source ColumnDataSource (cds).
        """
        samples = self._get_data_for_cur_idx_dims_values(space)    
        if self._type == "Discrete":
            self._source[space].data = pmf(samples)
        else:
            self._source[space].data = kde(samples) 
            max_v = self._get_max_prob(space)
            self._samples[space].data = dict(x=samples,y=np.asarray([-max_v/RUG_DIST_RATIO]*len(samples)),\
                                            size=np.asarray([RUG_SIZE]*len(samples)))

    def _update_selection_cds(self,space,xmin,xmax):
        """
            Updates selection ColumnDataSource (cds).
        """
        # Get kde points within [xmin,xmax]
        data={}
        data['x'] = np.array([])
        data['y'] = np.array([])
        kde_indices = find_indices(self._source[space].data['x'], lambda e: e >= xmin and e<= xmax,xmin,xmax)  
        if len(kde_indices) == 0:
            if self._type == "Discrete":
                self._selection[space].data = dict(x=np.array([]),y=np.array([]),y0=np.array([]))
            else:
                self._selection[space].data = dict(x=np.array([]),y=np.array([]))
            return
        data['x'] = self._source[space].data['x'][kde_indices] 
        data['y'] = self._source[space].data['y'][kde_indices] 

        if self._type == "Discrete":
            data['y0'] = np.asarray(len(data['x'])*[0])
        else:
            # Add interpolated points at xmin, xmax
            xmin_inds = find_inds_before_after(self._source[space].data['x'], xmin)
            if -1 not in xmin_inds:       
                xmin_l=self._source[space].data['x'][xmin_inds[0]]
                xmin_h=self._source[space].data['x'][xmin_inds[1]]        
                ymin_l=self._source[space].data['y'][xmin_inds[0]]
                ymin_h=self._source[space].data['y'][xmin_inds[1]]        
                ymin = ((ymin_h-ymin_l)/(xmin_h-xmin_l))*(xmin-xmin_l) + ymin_l
                data['x'] = np.insert(data['x'],0,xmin)
                data['y'] = np.insert(data['y'],0,ymin)       

            xmax_inds = find_inds_before_after(self._source[space].data['x'], xmax)
            if -1 not in xmax_inds: 
                xmax_l=self._source[space].data['x'][xmax_inds[0]]
                xmax_h=self._source[space].data['x'][xmax_inds[1]]
                ymax_l=self._source[space].data['y'][xmax_inds[0]]
                ymax_h=self._source[space].data['y'][xmax_inds[1]]
                ymax= ((ymax_h-ymax_l)/(xmax_h-xmax_l))*(xmax-xmax_l) + ymax_l
                data['x'] = np.append(data['x'],xmax)
                data['y'] = np.append(data['y'],ymax)        

            # Append and prepend zeros 
            data['y'] = np.insert(data['y'],0,0)
            data['y'] = np.append(data['y'],0)
            data['x'] = np.insert(data['x'],0,data['x'][0])
            data['x'] = np.append(data['x'],data['x'][-1])
        self._selection[space].data = data

    def _update_reconstructed_cds(self,space):
        """
            Updates reconstructed ColumnDataSource (cds).
        """
        samples = self._samples[space].data['x']
        inds = Cell._get_sample_inds(space)
        if len(inds):
            sel_sample = samples[inds]   
            if self._type == "Discrete":
                self._reconstructed[space].data = pmf(sel_sample)       
            else:    
                self._reconstructed[space].data = kde(sel_sample)  
                max_v = self._get_max_prob(space)
                self._sel_samples[space].data = dict(x=sel_sample,y=np.asarray([-max_v/RUG_DIST_RATIO]*len(sel_sample)),\
                                                    size=np.asarray([RUG_SIZE]*len(sel_sample)))           
        else:
            if self._type == "Discrete":
                self._reconstructed[space].data = dict(x=np.array([]),y=np.array([]),y0=np.array([]))  
            else:
                self._reconstructed[space].data = dict(x=np.array([]),y=np.array([]))  
                self._sel_samples[space].data =  dict(x=np.array([]),y=np.array([]), size=np.array([]))
        max_v = self._get_max_prob(space)
        if max_v!=-1:
            self._samples[space].data['y'] = np.asarray([-max_v/RUG_DIST_RATIO]*len(self._samples[space].data['x']))

    def _get_max_prob(self,space): 
        """
            Gets highest point --max probability-- of cds
        """
        max_sv = -1
        max_rv = -1
        if self._source[space].data['y'].size:  
            max_sv = self._source[space].data['y'].max()
        if self._reconstructed[space].data['y'].size:
            max_rv = self._reconstructed[space].data['y'].max()
        return max([max_sv,max_rv])

    def _update_clear_selection_cds(self,space):  
        """
            Updates clear_selection ColumnDataSource (cds).
        """   
        sel_var_idx_dims_values = self._get_sel_var_idx_dims_values()
        sel_space = self._get_sel_space()
        var_x_range = self._get_var_x_range()        
        if (self._name in sel_var_idx_dims_values and space == sel_space and 
            self._cur_idx_dims_values == sel_var_idx_dims_values[self._name]):
            min_x_range = var_x_range[(space,self._name)].data['xmin'][0]
            max_x_range = var_x_range[(space,self._name)].data['xmax'][0]
            hp = find_highest_point(self._reconstructed[space].data['x'],self._reconstructed[space].data['y'])
            if not hp:
                hp=find_highest_point(self._selection[space].data['x'],self._selection[space].data['y'])
                if not hp:
                    hp=find_highest_point(self._source[space].data['x'],self._source[space].data['y'])
                    if not hp:
                        hp=(0,0)
            self._clear_selection[space].data = dict(x=[(max_x_range + min_x_range) / 2.],\
                                                   y=[hp[1]+hp[1]*0.1],isIn=[0])            
        else:
            self._clear_selection[space].data=dict(x=[],y=[],isIn=[])

    


    