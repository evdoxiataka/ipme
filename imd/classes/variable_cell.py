from ..interfaces.cell import Cell
from ..utils.functions import * 
from ..utils.stats import kde, pmf
from ..utils.js_code import HOVER_CODE
from ..utils.constants import COLORS, BORDER_COLORS, PLOT_HEIGHT, PLOT_WIDTH, SIZING_MODE, RUG_DIST_RATIO, RUG_SIZE

from functools import partial

from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, BoxSelectTool, HoverTool,  CustomJS
from bokeh import events

class VariableCell(Cell):   
    def __init__(self, name):
        """
            Parameters:
            --------
                name            A String within the set {"<variableName>"}.
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
        Cell.__init__(self, name)  
                
    def _get_data_for_cur_idx_dims_values(self, space):
        """
            Returns a numpy.ndarray of the MCMC samples of the <name>  
            parameter for current index dimensions values.

            Returns:
            --------
                A numpy.ndarray.
        """ 
        if Cell._data.get_var_type(self._name) == "observed":
            if space == "posterior" and "posterior_predictive" in Cell._data.get_spaces():
                space="posterior_predictive"
            elif space == "prior" and "prior_predictive" in Cell._data.get_spaces():
                space="prior_predictive"
        data = Cell._data.get_samples(self._name,space) 
        data = data.T       
        for dim_name,dim_value in self._cur_idx_dims_values.items():
            data = data[dim_value]
        return np.squeeze(data).T
    
    def initialize_fig(self,space):
        self._plot[space]=figure( tools="wheel_zoom,reset", toolbar_location='right', 
                            plot_width=PLOT_WIDTH, plot_height=PLOT_HEIGHT,  sizing_mode=SIZING_MODE)            
        self._plot[space].border_fill_color = BORDER_COLORS[0]    
        self._plot[space].xaxis.axis_label = ""
        self._plot[space].yaxis.visible = False            
        self._plot[space].toolbar.logo = None
        self._plot[space].y_range.only_visible = True
        self._plot[space].x_range.only_visible = True
        self._plot[space].xaxis[0].ticker.desired_num_ticks = 3         
        ##Events
        self._plot[space].on_event(events.Tap, partial(self._clear_selection_callback,space))             
        self._plot[space].on_event(events.SelectionGeometry, partial(self._selectionbox_callback,space))   
        ##on_change         
        Cell._sample_inds[space].on_change('data',partial(self._sample_inds_callback, space))
        Cell._var_x_range[(space,self._name)].on_change('data',partial(self._var_x_range_callback, space))

    def initialize_cds(self,space):
        samples=self._get_data_for_cur_idx_dims_values(space)  
        if self._type == "Discrete":
            self._source[space] = ColumnDataSource(data = pmf(samples))
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
        ##Add BoxSelectTool
        self._plot[space].add_tools(BoxSelectTool(dimensions='width',renderers=[so_seg,so_scat]))

    def initialize_glyphs_continuous(self,space):
        so=self._plot[space].line('x', 'y', line_color = COLORS[0], line_width = 2, source=self._source[space])       
        self._plot[space].line('x', 'y', line_color = COLORS[1], line_width = 2, source=self._reconstructed[space])        
        self._plot[space].line('x', 'y', line_color = COLORS[2], line_width = 2, source=self._selection[space])
        self._plot[space].dash('x','y', size='size',angle=90.0, angle_units='deg', line_color = COLORS[0], \
                                        source=self._samples[space])
        self._plot[space].dash('x','y', size='size',angle=90.0, angle_units='deg', line_color = COLORS[1], \
                                        source=self._sel_samples[space])
        ##Add BoxSelectTool
        self._plot[space].add_tools(BoxSelectTool(dimensions='width',renderers=[so]))

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
            self.initialize_cds(space)
            self.initialize_fig(space)
            self.initialize_glyphs(space)   

    ## Callback called when x_range is set
    def _var_x_range_callback(self, space, attr, old, new):
        xmin_list=Cell._var_x_range[(space,self._name)].data['xmin']
        xmax_list=Cell._var_x_range[(space,self._name)].data['xmax']
        if len(xmin_list):
            self._update_selection_cds(space, xmin_list[0], xmax_list[0])
        else:
            if self._type == "Discrete":
                self._selection[space].data=dict(x=np.array([]),y=np.array([]),y0=np.array([]))
            else:
                self._selection[space].data=dict(x=np.array([]),y=np.array([]))

    ## Update plots when indexing dimensions widgets are used
    def _widget_callback(self, attr, old, new, w_title, space):  
        inds = -1
        w2_title = ""   
        values = []                     
        if space in self._w1_w2_idx_mapping and \
            w_title in self._w1_w2_idx_mapping[space]:
            w2_title, _  = self._w1_w2_idx_mapping[space][w_title]
            name = w_title+"_idx_"+w2_title
            if name in self._idx_dims:
                values = self._idx_dims[name].values
        elif w_title in self._idx_dims:
            values = self._idx_dims[w_title].values  
        elif space in self._w2_w1_idx_mapping and \
            w_title in self._w2_w1_idx_mapping[space]:
            _, w1_idx = self._w2_w1_idx_mapping[space][w_title]
            w1_value = self._widgets[space][w1_idx].value
            values = self._w2_w1_val_mapping[space][w_title][w1_value]
        inds = [i for i,v in enumerate(values) if v == new]
        if inds == -1 or len(inds) == 0:
            return
        self._cur_idx_dims_values[w_title] = inds
        if w2_title and w2_title in self._cur_idx_dims_values:
            self._cur_idx_dims_values[w2_title] = [0]
        self._update_source_cds(space)
        Cell._global_update = True
        self._update_cds(space)

    ## Callback when clear selection glyph is clicked
    def _clear_selection_callback(self,space,event):
        isIn=self._clear_selection[space].data['isIn']
        if 1 in isIn:
            Cell._var_x_range[(space,self._name)].data=dict(xmin=np.array([]),xmax=np.array([]))
            del Cell._sel_var_idx_dims_values[self._name]
            for sp in self._spaces:                
                del Cell._sel_var_inds[(sp,self._name)]   
                self._compute_intersection_of_samples(sp)

    ## Update selection-related ColumnDataSources
    def _update_cds(self,space):
        if(Cell._global_update):
            Cell._global_update=False
            if (self._name in Cell._sel_var_idx_dims_values and space == Cell._sel_space and 
                self._cur_idx_dims_values == Cell._sel_var_idx_dims_values[self._name]):
                self._update_selection_cds(space, Cell._var_x_range[(space,self._name)].data['xmin'][0],\
                                            Cell._var_x_range[(space,self._name)].data['xmax'][0])
            else:
                if self._type == "Discrete":
                    self._selection[space].data=dict(x=np.array([]),y=np.array([]),y0=np.array([]))
                else:
                    self._selection[space].data=dict(x=np.array([]),y=np.array([]))
        self._update_reconstructed_cds(space) 
        self._update_clear_selection_cds(space)

    ## Update plots when indices of selected samples are updated
    def _sample_inds_callback(self, space, attr, old, new):
        self._update_cds(space)       

    ## Callback when selection box is drawn
    def _selectionbox_callback(self, space, event):
        xmin=event.geometry['x0']
        xmax=event.geometry['x1']
        Cell._sel_space=space
        Cell._var_x_range[(space,self._name)].data=dict(xmin=np.asarray([xmin]),xmax=np.asarray([xmax]))             
        Cell._sel_var_idx_dims_values[self._name]=dict(self._cur_idx_dims_values)
        for sp in self._spaces:
            samples = self._get_data_for_cur_idx_dims_values(sp)
            Cell._sel_var_inds[(sp,self._name)] = find_indices(samples, lambda e: e >= xmin and e<= xmax)    
            self._compute_intersection_of_samples(sp)

    ## Compute intersection of sample points based on user's restrictions per parameter
    def _compute_intersection_of_samples(self,space): 
        sp_keys=[k for k in Cell._sel_var_inds.keys() if k[0]==space]
        if len(sp_keys):
            set1=set(Cell._sel_var_inds[sp_keys[0]])
            for i in range(1, len(sp_keys)):
                set2=set(Cell._sel_var_inds[sp_keys[i]])
                set1=set1.intersection(set2) 
            Cell._sample_inds[space].data['inds'] = list(set1)
        else:
            Cell._sample_inds[space].data['inds'] = [] 

    ## Update source ColumnDataSource
    def _update_source_cds(self,space):
        samples = self._get_data_for_cur_idx_dims_values(space)    
        if self._type == "Discrete":
            self._source[space].data = pmf(samples)
        else:
            self._source[space].data = kde(samples) 
            max_v = self._get_max_prob(space)
            self._samples[space].data = dict(x=samples,y=np.asarray([-max_v/RUG_DIST_RATIO]*len(samples)),\
                                            size=np.asarray([RUG_SIZE]*len(samples)))

    ## Update selection ColumnDataSource
    def _update_selection_cds(self,space,xmin,xmax):
        # Get kde points within [xmin,xmax]
        data={}
        data['x'] = np.array([])
        data['y'] = np.array([])
        kde_indices = find_indices(self._source[space].data['x'], lambda e: e >= xmin and e<= xmax)  
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

    ## Update reconstructed ColumnDataSource
    def _update_reconstructed_cds(self,space):
        samples = self._get_data_for_cur_idx_dims_values(space)
        inds = Cell._sample_inds[space].data['inds']
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

    ## Get max point of cdss
    def _get_max_prob(self,space): 
        max_sv = -1
        max_rv = -1
        if self._source[space].data['y'].size:  
            max_sv = self._source[space].data['y'].max()
        if self._reconstructed[space].data['y'].size:
            max_rv = self._reconstructed[space].data['y'].max()
        return max([max_sv,max_rv])
             

    ## Update clear_selection ColumnDataSource
    def _update_clear_selection_cds(self,space):             
        if (self._name in Cell._sel_var_idx_dims_values and space == Cell._sel_space and 
            self._cur_idx_dims_values == Cell._sel_var_idx_dims_values[self._name]):
            min_x_range = Cell._var_x_range[(space,self._name)].data['xmin'][0]
            max_x_range = Cell._var_x_range[(space,self._name)].data['xmax'][0]
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

    


    