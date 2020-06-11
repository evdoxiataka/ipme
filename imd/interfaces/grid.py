from abc import ABC, abstractmethod
from bokeh.models import ColumnDataSource, Toggle, Div
from bokeh.layouts import layout
from functools import partial
from bokeh.models.widgets import Select, Slider, Button

from ..utils.functions import get_dim_names_options, get_w2_w1_val_mapping
#import pyautogui

class Grid(ABC):
    _COLORS=['#d8d8d8','#f6f6f6']
    ##
    _MAX_NUM_OF_COLS_PER_ROW = 12
    _COLS_PER_VAR = 2
    _MAX_NUM_OF_VARS_PER_ROW = 5
    
    def __init__(self, data_obj):
        """
            Parameters:
            --------
                data_obj                A Data object.           
            Sets:
            --------
                _data                   A Data object.                
                _grids                  A Dict of pn.GridSpec objects 
                                        Either {<var_name>:{<space>:pn.GridSpec}}
                                        Or {<space>:pn.GridSpec}
                _cells                  A List of Cell objects.
                _cells_widgets          A Dict dict1 of the form (key1,value1) = (<widget_name>, dict2)
                                        dict2 of the form (key1,value1) = (<space>, List of tuples (<cell_id>,<widget_id>)
                                        of the widgets with same name).
                _plotted_widgets        A List of widget objects to be plotted.
        """
        self._data = data_obj  
        self._grids = {}
        self._cells=[]
        self._create_grids()          

        self._cells_widgets = {}        
        self._plotted_widgets = {}        
        self._add_widgets() 

    def _add_widgets(self):
        self._link_cells_widgets()
        self._set_plotted_widgets()

    def _link_cells_widgets(self):
        for c_id, cell in enumerate(self._cells):
            cell_spaces = cell.get_spaces()
            for space in cell_spaces:
                for w_id, w in enumerate(cell.get_widgets_in_space(space)):
                    if w.title in self._cells_widgets:
                        if space in self._cells_widgets[w.title]:
                            self._cells_widgets[w.title][space].append((c_id,w_id))
                        else:
                            self._cells_widgets[w.title][space] = [(c_id,w_id)]
                        ## Every new widget is linked to the corresponding widget (of same name) 
                        ## of the 1st space in self._cells_widgets[w.title]
                        ## Find target cell to link with current cell
                        f_space = list(self._cells_widgets[w.title].keys())[0]
                        self._link_widget_to_target(w, f_space)                         
                    else:
                        self._cells_widgets[w.title] = {}
                        self._cells_widgets[w.title][space] = [(c_id,w_id)]
                        f_space = list(self._cells_widgets[w.title].keys())[0]
                        if f_space != space: 
                            self._link_widget_to_target(w, f_space) 

    def _link_widget_to_target(self, w, f_space):
        if len(self._cells_widgets[w.title][f_space]):
            t_c_id,t_w_id = self._cells_widgets[w.title][f_space][0]
            t_w = self._cells[t_c_id].get_widget(f_space,t_w_id)
            if t_w is not None and hasattr(t_w,'js_link'):
                t_w.js_link('value', w, 'value')

    def _set_plotted_widgets(self):
        self._plotted_widgets = {}                      
        for _, space_widgets_dict in self._cells_widgets.items():
            w_spaces = list(space_widgets_dict.keys())
            if len(w_spaces):
                f_space = w_spaces[0]
                f_w_list = space_widgets_dict[f_space]
                if len(f_w_list):
                    c_id,w_id = f_w_list[0]
                    for space in w_spaces:
                        if space not in self._plotted_widgets:
                            self._plotted_widgets[space] = []
                        self._plotted_widgets[space].append(self._cells[c_id].get_widget(f_space,w_id))
        b = Button(label='Reset Diagram', button_type="primary")
        b.on_click(self._global_reset)
        for space in self._plotted_widgets:    
            self._plotted_widgets[space].append(b)

    def _global_reset(self, event):
        Cell._sel_var_inds={}
        Cell._sel_space=""
        Cell._sel_var_idx_dims_values={}
        for sp, var in Cell._var_x_range:
            Cell._var_x_range[(sp, var)].data=dict(xmin=[],xmax=[])
        for sp in Cell._sample_inds:     
            Cell._sample_inds[sp].data=dict(inds=[])

    @abstractmethod
    def _create_grids(self):
        pass

    def get_grids(self):
        return self._grids

    def get_plotted_widgets(self):
        return self._plotted_widgets

class Cell(ABC):
    _data = None
    ##Plot-related variables
    _BORDER_COLORS=['#d8d8d8','#FFFFFF']
    _COLORS=['#008080','#403F6F','#800080']
    _PLOT_WIDTH = 220
    _PLOT_HEIGHT = 220
    _SIZING_MODE = "fixed"
    ##Interaction-related variables
    _sample_inds=dict(prior=ColumnDataSource(data=dict(inds=[])), posterior=ColumnDataSource(data=dict(inds=[])))
    _sel_var_inds={}
    _sel_space=""
    _sel_var_idx_dims_values={}
    _var_x_range={}
    _global_update = False
    
    def __init__(self, name):
        """
            Each cell will occupy a certain number of grid columns and will lie on a certain grid row.
            Parameters:
            --------
                name                    A String within the set {"<variableName>"}.
            Sets:
            --------
                _name
                _spaces                 A List of Strings in {"prior","posterior"}.   
                _type                   A String in {"Discrete","Continuous",""}.             
                _idx_dims
                _cur_idx_dims_values    A Dict {<idx_dim_name>: Integer of current value index of <idx_dim_name>}.
                
                _plot                   A Dict {<space>: (bokeh) plot object}.
                _widgets                A Dict {<space>: List of (bokeh) widget objects}.
                _w1_w2_idx_mapping      A Dict {<space>: Dict {<w_name1>:(w_name2,widgets_idx)}}.
                _w2_w1_idx_mapping      A Dict {<space>: Dict {<w_name2>:(w_name1,widgets_idx)}}.
                _w2_w1_val_mapping      A Dict {<space>: Dict {<w_name2>:{<w1_value>: A List of <w_name2> values for <w1_value>}}.
                _toggle                 A Dict {<space>: (bokeh) toggle button for visibility of figure}.
                _div                    A Dict {<space>: (bokeh) div parameter-related information}.
        """
        self._name = name
        self._spaces = self._define_spaces()   
        self._type = Cell._data.get_var_dist_type(self._name)    

        #idx_dims-related variables
        self._idx_dims = Cell._data.get_idx_dimensions(self._name)
        self._cur_idx_dims_values = {}             

        self._plot = {}
        self._widgets = {}
        self._w1_w2_idx_mapping = {}
        self._w2_w1_idx_mapping = {}
        self._w2_w1_val_mapping = {}

        self._initialize_widgets()
        self._initialize_plot()

        self._toggle = {}
        self._div ={}
        self._initialize_toggle_div()
        
    def _define_spaces(self):
        data_spaces = Cell._data.get_spaces()
        spaces = []
        if "prior" in data_spaces:
            spaces.append("prior")
        if "posterior" in data_spaces:
            spaces.append("posterior")        
        return spaces

    def _initialize_widgets(self):
        for space in self._spaces:
            self._widgets[space]=[]
            for _, d_dim in self._idx_dims.items():
                n1, n2, opt1, opt2 = get_dim_names_options(d_dim)               
                self._widgets[space].append(Select(title=n1, value=opt1[0], options=opt1))
                self._widgets[space][-1].on_change("value", partial(self._widget_callback, w_title=n1, space=space))
                self._widgets[space][-1].on_change("value", partial(self._idx_widget_callback, w_title=n1, space=space))
                if n1 not in self._cur_idx_dims_values:
                    inds=[i for i,v in enumerate(d_dim.values) if v == opt1[0]]
                    self._cur_idx_dims_values[n1] = inds
                if n2:                  
                    self._widgets[space].append(Select(title=n2, value=opt2[0], options=opt2))
                    self._widgets[space][-1].on_change("value", partial(self._widget_callback, w_title=n2, space=space)) 
                    self._w1_w2_idx_mapping[space] = {}
                    self._w1_w2_idx_mapping[space][n1] = (n2,len(self._widgets[space])-1)
                    self._w2_w1_idx_mapping[space] = {}
                    self._w2_w1_idx_mapping[space][n2] = (n1,len(self._widgets[space])-2)
                    self._w2_w1_val_mapping[space] = {}
                    self._w2_w1_val_mapping[space][n2] = get_w2_w1_val_mapping(d_dim)
                    if n2 not in self._cur_idx_dims_values:
                        self._cur_idx_dims_values[n2] = [0]  

    def _idx_widget_callback(self, attr, old, new, w_title, space):
        if space in self._w1_w2_idx_mapping and \
            w_title in self._w1_w2_idx_mapping[space]:
            w2_n, w2_idx = self._w1_w2_idx_mapping[space][w_title]
            opt2 = self._w2_w1_val_mapping[space][w2_n][new]
            self._widgets[space][w2_idx].value = opt2[0]
            self._widgets[space][w2_idx].options = opt2

    def _initialize_toggle_div(self):
        for space in self._spaces:            
            width = self._plot[space].plot_width
            height = 40
            sizing_mode = self._plot[space].sizing_mode
            label = self._name+" ~ "+Cell._data.get_var_dist(self._name)
            text = """parents: %s <br>dims: %s"""%(Cell._data.get_var_parents(self._name),list(Cell._data.get_idx_dimensions(self._name)))
            if sizing_mode == 'fixed':
                self._toggle[space] = Toggle(label = label,  active = False, 
                width = width, height = height, sizing_mode = sizing_mode, margin = (0,0,0,0))
                self._div[space] = Div(text = text,
                width = width, height = height, sizing_mode = sizing_mode, margin = (0,0,0,0), background=Cell._BORDER_COLORS[0] )
            elif sizing_mode == 'scale_width' or sizing_mode == 'stretch_width':
                self._toggle[space] = Toggle(label = label,  active = False, 
                height = height, sizing_mode = sizing_mode, margin = (0,0,0,0))   
                self._div[space] = Div(text = text,
                height = height, sizing_mode = sizing_mode, margin = (0,0,0,0), background=Cell._BORDER_COLORS[0] )         
            elif sizing_mode == 'scale_height' or sizing_mode == 'stretch_height':
                self._toggle[space] = Toggle(label = label,  active = False, 
                width = width, sizing_mode = sizing_mode, margin = (0,0,0,0)) 
                self._div[space] = Div(text = text,
                width = width, sizing_mode = sizing_mode, margin = (0,0,0,0), background=Cell._BORDER_COLORS[0] )
            else:
                self._toggle[space] = Toggle(label = label,  active = False, 
                sizing_mode = sizing_mode, margin = (0,0,0,0)) 
                self._div[space] = Div(text = text, sizing_mode = sizing_mode, margin = (0,0,0,0), background=Cell._BORDER_COLORS[0] )
            self._toggle[space].js_link('active', self._plot[space], 'visible')

    @abstractmethod
    def _widget_callback(self, attr, old, new, w_title, space):
        pass

    @abstractmethod
    def _initialize_plot(self):
        pass

    def get_widgets(self):
        return self._widgets

    def get_widgets_in_space(self, space):
        if space in self._widgets:
            return self._widgets[space]
        else:
            return []

    def get_widget(self,space,id):
        try:
            return self._widgets[space][id]
        except IndexError:
            return None

    def get_start_point(self):
        return self._start_point

    def get_end_point(self):
        return self._end_point

    def get_plot(self,space, add_info=True):
        if space in self._plot:
            if add_info and space in self._toggle and space in self._div:
                return layout([self._toggle[space]],[self._div[space]],[self._plot[space]])
            else:
                return self._plot[space]
        else:
            return None

    def has_dim(self,dim_name):
        if dim_name in [dim.name for dim in self._idx_dims]:
            return True
        else:
            return False

    def get_spaces(self):
        return self._spaces

    def get_grid_bgrd_col(self):
        return self._grid_bgrd_col
            
