from abc import ABC, abstractmethod
from bokeh.models import ColumnDataSource, Toggle, Div
from bokeh.layouts import layout
from bokeh.io.export import get_screenshot_as_png
from functools import partial
from bokeh.models.widgets import Select

import threading

from ..utils.functions import get_dim_names_options, get_w2_w1_val_mapping
from ..utils.constants import BORDER_COLORS

class Cell(ABC):
    _data = None   
    _num_cells = 0
    _idx_widget_flag = False
    ##threads lists    
    _selection_threads = {}
    _space_threads = []
    _widget_threads = []
    ##locks
    _sel_lock = threading.Lock()
    _widget_lock = threading.Lock()
    _sample_inds_lock = threading.Lock()
    _sample_inds_update_lock = threading.Lock()
    _sel_var_inds_lock = threading.Lock()
    _sel_space_lock = threading.Lock()
    _sel_var_idx_dims_values_lock = threading.Lock()
    _var_x_range_lock = threading.Lock()
    _global_update_lock = threading.Lock()
    _space_lock = threading.Lock()
    _w1_w2_idx_mapping_lock = threading.Lock()
    _w2_w1_idx_mapping_lock = threading.Lock()
    _w2_w1_val_mapping_lock = threading.Lock()
    ##events
    _sel_lock_event = threading.Event()    
    _widget_lock_event = threading.Event()
    ##idx_widgets
    _w1_w2_idx_mapping = {}
    _w2_w1_idx_mapping = {}
    _w2_w1_val_mapping = {}  
    ##Interaction-related variables 
    _sample_inds = dict(prior=ColumnDataSource(data=dict(inds=[])), posterior=ColumnDataSource(data=dict(inds=[])))
    _sample_inds_update = dict(prior=ColumnDataSource(data=dict(updated=[False])), posterior=ColumnDataSource(data=dict(updated=[False])))
    _sel_var_inds = {}
    _sel_space = ""
    _sel_var_idx_dims_values = {}
    _var_x_range = {}
    _global_update = False
    
    def __init__(self, name, mode):
        """
            Each cell will occupy a certain number of grid columns and will lie on a certain grid row.
            Parameters:
            --------
                name                    A String within the set {"<variableName>"}.
                mode                    A String in {"i","s"}, "i":interactive, "s":static.
            Sets:
            --------
                _name
                _mode
                _spaces                 A List of Strings in {"prior","posterior"}.   
                _type                   A String in {"Discrete","Continuous",""}.             
                _idx_dims
                _cur_idx_dims_values    A Dict {<idx_dim_name>: Integer of current value index of <idx_dim_name>}.
                
                _plot                   A Dict {<space>: (bokeh) plot object}.
                _widgets                A Dict {<space>: {<widget_title>: A (bokeh) widget object} }.
                _w1_w2_idx_mapping      A Dict {<space>: Dict {<w_name1>:(w_name2,widgets_idx)}}.
                _w2_w1_idx_mapping      A Dict {<space>: Dict {<w_name2>:(w_name1,widgets_idx)}}.
                _w2_w1_val_mapping      A Dict {<space>: Dict {<w_name2>:{<w1_value>: A List of <w_name2> values for <w1_value>}}.
                _toggle                 A Dict {<space>: (bokeh) toggle button for visibility of figure}.
                _div                    A Dict {<space>: (bokeh) div parameter-related information}.
        """
        self._name = name
        self._mode = mode
        self._spaces = self._define_spaces()   
        self._type = Cell._data.get_var_dist_type(self._name)    

        #idx_dims-related variables
        self._idx_dims = Cell._data.get_idx_dimensions(self._name)
        self._cur_idx_dims_values = {}             

        self._plot = {}
        self._widgets = {}

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
            self._widgets[space]={}
            for _, d_dim in self._idx_dims.items():
                n1, n2, opt1, opt2 = get_dim_names_options(d_dim)               
                self._widgets[space][n1] = Select(title=n1, value=opt1[0], options=opt1)                
                self._widgets[space][n1].on_change("value", partial(self._widget_callback, w_title=n1, space=space))
                if n1 not in self._cur_idx_dims_values:
                    inds=[i for i,v in enumerate(d_dim.values) if v == opt1[0]]
                    self._cur_idx_dims_values[n1] = inds
                if n2:                  
                    self._widgets[space][n2] = Select(title=n2, value=opt2[0], options=opt2)
                    self._widgets[space][n2].on_change("value", partial(self._widget_callback, w_title=n2, space=space)) 
                    Cell._idx_widgets_mapping(space, d_dim, n1, n2)
                    if n2 not in self._cur_idx_dims_values:
                        self._cur_idx_dims_values[n2] = [0]  
    @staticmethod
    def _idx_widgets_mapping(space, d_dim, w1_title, w2_title):
        if space in Cell._w1_w2_idx_mapping:
            if w1_title in Cell._w1_w2_idx_mapping[space]:
                if w2_title not in Cell._w1_w2_idx_mapping[space][w1_title]:
                    Cell._w1_w2_idx_mapping[space][w1_title].append(w2_title)
            else:
                Cell._w1_w2_idx_mapping[space][w1_title] = [w2_title]
            if w2_title in Cell._w2_w1_idx_mapping[space]:
                if w1_title not in  Cell._w2_w1_idx_mapping[space][w2_title]:
                    Cell._w2_w1_idx_mapping[space][w2_title].append(w1_title)
            else:
                Cell._w2_w1_idx_mapping[space][w2_title] = [w1_title]
            if w2_title not in Cell._w2_w1_val_mapping[space]:
                Cell._w2_w1_val_mapping[space][w2_title] = get_w2_w1_val_mapping(d_dim)
        else:
            Cell._w1_w2_idx_mapping[space] = {}
            Cell._w1_w2_idx_mapping[space][w1_title] = [w2_title]
            Cell._w2_w1_idx_mapping[space] = {}
            Cell._w2_w1_idx_mapping[space][w2_title] = [w1_title]
            Cell._w2_w1_val_mapping[space] = {}
            Cell._w2_w1_val_mapping[space][w2_title] = get_w2_w1_val_mapping(d_dim)

    @staticmethod
    def _idx_widget_update(cells, cells_widgets, new, w_title, space):
        w1_w2_idx_mapping = Cell._get_w1_w2_idx_mapping()
        w2_w1_val_mapping = Cell._get_w2_w1_val_mapping()
        if space in w1_w2_idx_mapping and w_title in w1_w2_idx_mapping[space]:
            for w2_n in w1_w2_idx_mapping[space][w_title]:
                opt2 = w2_w1_val_mapping[space][w2_n][new]
                if w2_n in cells_widgets:
                    for sp in cells_widgets[w2_n]:
                        if len(cells_widgets[w2_n][sp]):
                            c_id = cells_widgets[w2_n][sp][0]
                            if c_id in cells:
                                w = cells[c_id].get_widget(sp,w2_n)
                                w.options = opt2
                                Cell._idx_widget_flag=True
                                w.value = opt2[0]
                        break                

    @staticmethod
    def _menu_item_click_callback(cells, cells_widgets, space, w_id, attr, old, new):
        if old == new:
            return
        flag = Cell._idx_widget_flag
        if flag:
            Cell._idx_widget_flag = False
            Cell._widget_lock.acquire()
            Cell._widget_threads.clear()
            Cell._widget_lock.release()
            return
        num_widg = 0
        if w_id in cells_widgets:
            for sp in cells_widgets[w_id]:
                num_widg += len(cells_widgets[w_id][sp])
        num_widg_threads = 0        
        while num_widg_threads < num_widg:
            Cell._widget_lock_event.wait()
            Cell._widget_lock_event.clear()
            Cell._widget_lock.acquire()
            num_widg_threads = len(Cell._widget_threads)            
            Cell._widget_lock.release()        
        Cell._widget_lock.acquire()
        t_sel = Cell._widget_threads
        Cell._widget_lock.release()
        for t in t_sel:
            t.start()
        for t in t_sel:
            t.join()
        Cell._widget_lock.acquire()
        Cell._widget_threads.clear()
        Cell._widget_lock.release()
        Cell._idx_widget_update(cells, cells_widgets, new, w_id, space)

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
                width = width, height = height, sizing_mode = sizing_mode, margin = (0,0,0,0), background=BORDER_COLORS[0] )
            elif sizing_mode == 'scale_width' or sizing_mode == 'stretch_width':
                self._toggle[space] = Toggle(label = label,  active = False, 
                height = height, sizing_mode = sizing_mode, margin = (0,0,0,0))   
                self._div[space] = Div(text = text,
                height = height, sizing_mode = sizing_mode, margin = (0,0,0,0), background=BORDER_COLORS[0] )         
            elif sizing_mode == 'scale_height' or sizing_mode == 'stretch_height':
                self._toggle[space] = Toggle(label = label,  active = False, 
                width = width, sizing_mode = sizing_mode, margin = (0,0,0,0)) 
                self._div[space] = Div(text = text,
                width = width, sizing_mode = sizing_mode, margin = (0,0,0,0), background=BORDER_COLORS[0] )
            else:
                self._toggle[space] = Toggle(label = label,  active = False, 
                sizing_mode = sizing_mode, margin = (0,0,0,0)) 
                self._div[space] = Div(text = text, sizing_mode = sizing_mode, margin = (0,0,0,0), background=BORDER_COLORS[0] )
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

    def get_plot(self,space, add_info=True):
        if space in self._plot:
            if add_info and space in self._toggle and space in self._div:
                return layout([self._toggle[space]],[self._div[space]],[self._plot[space]])
            else:
                return self._plot[space]
        else:
            return None

    def get_screenshot(self, space, add_info=True):
        if space in self._plot:
            if add_info and space in self._toggle and space in self._div:
                return get_screenshot_as_png(layout([self._toggle[space]],[self._div[space]],[self._plot[space]]))
            else:
                return get_screenshot_as_png(self._plot[space])
        else:
            return None

    @abstractmethod
    def set_stratum(self, space, stratum = 0):
        pass

    def get_spaces(self):
        return self._spaces

    ##Threads-related methods
    @staticmethod
    def _space_threads_join():
        Cell._space_lock.acquire()
        for i,_ in enumerate(Cell._space_threads):
            Cell._space_threads[i].start()
        for i,_ in enumerate(Cell._space_threads):
            Cell._space_threads[i].join()
        Cell._space_threads.clear()
        Cell._space_lock.release()

    @staticmethod
    def _selection_threads_join(space):
        num_sel_threads = 0
        while num_sel_threads < Cell._num_cells:
            Cell._sel_lock_event.wait()
            Cell._sel_lock_event.clear()
            Cell._sel_lock.acquire()
            if space in Cell._selection_threads:
                num_sel_threads = len(Cell._selection_threads[space])
            Cell._sel_lock.release()
        Cell._sel_lock.acquire()
        t_sel = Cell._selection_threads[space]
        Cell._sel_lock.release()
        for t in t_sel:
            t.start()
        for t in t_sel:
            t.join()
        Cell._sel_lock.acquire()
        del Cell._selection_threads[space]
        Cell._sel_lock.release()

    @staticmethod
    def _add_selection_threads(space, t):
        Cell._sel_lock.acquire()
        if space in Cell._selection_threads:            
            Cell._selection_threads[space].append(t)
        else:
            Cell._selection_threads[space] = [t]
        Cell._sel_lock.release()

    @staticmethod
    def _get_selection_threads(space):
        sel_t = []
        Cell._sel_lock.acquire()
        if space in Cell._selection_threads:            
            sel_t = Cell._selection_threads[space]
        Cell._sel_lock.release()
        return sel_t

    @staticmethod
    def _add_space_threads(t):
        Cell._space_lock.acquire()
        Cell._space_threads.append(t)
        Cell._space_lock.release()

    @staticmethod
    def _get_space_threads():
        sp_t = []
        Cell._space_lock.acquire()
        sp_t = Cell._space_threads
        Cell._space_lock.release()   
        return sp_t

    @staticmethod
    def _get_w1_w2_idx_mapping():
        w1_w2_idx_mapping = {}
        Cell._w1_w2_idx_mapping_lock.acquire()
        w1_w2_idx_mapping = Cell._w1_w2_idx_mapping
        Cell._w1_w2_idx_mapping_lock.release()
        return w1_w2_idx_mapping

    @staticmethod
    def _get_w2_w1_idx_mapping():
        w2_w1_idx_mapping = {}
        Cell._w2_w1_idx_mapping_lock.acquire()
        w2_w1_idx_mapping = Cell._w2_w1_idx_mapping
        Cell._w2_w1_idx_mapping_lock.release()
        return w2_w1_idx_mapping

    @staticmethod
    def _get_w2_w1_val_mapping():
        w2_w1_val_mapping = {}
        Cell._w2_w1_val_mapping_lock.acquire()
        w2_w1_val_mapping = Cell._w2_w1_val_mapping
        Cell._w2_w1_val_mapping_lock.release()
        return w2_w1_val_mapping

    @staticmethod
    def _add_widget_threads(t):
        Cell._widget_lock.acquire()    
        Cell._widget_threads.append(t)
        Cell._widget_lock.release()

    @staticmethod
    def _set_sample_inds(space, dict_data):
        Cell._sample_inds_lock.acquire()
        if space in Cell._sample_inds:
            Cell._sample_inds[space].data = dict_data
        Cell._sample_inds_lock.release()
        isup = Cell._get_sample_inds_update(space)
        Cell._set_sample_inds_update(space,dict(updated = [not isup]))

    @staticmethod
    def _reset_sample_inds(space):
        Cell._sample_inds_lock.acquire()
        Cell._sample_inds[space].data = dict(inds=[])
        print("reset_sample_inds")
        Cell._sample_inds_lock.release()
        isup = Cell._get_sample_inds_update(space)
        Cell._set_sample_inds_update(space,dict(updated = [not isup]))

    @staticmethod
    def _get_sample_inds(space=None):
        inds = []
        Cell._sample_inds_lock.acquire()
        if space in Cell._sample_inds:
            inds = Cell._sample_inds[space].data['inds']
        else:
            inds = Cell._sample_inds
        Cell._sample_inds_lock.release()
        return inds

    @staticmethod
    def _set_sample_inds_update(space, dict_data):
        Cell._sample_inds_update_lock.acquire()
        if space in Cell._sample_inds_update:
            Cell._sample_inds_update[space].data = dict_data
        Cell._sample_inds_update_lock.release()

    @staticmethod
    def _get_sample_inds_update(space=None):
        isUpdated = False
        Cell._sample_inds_update_lock.acquire()
        if space in Cell._sample_inds_update:
            isUpdated = Cell._sample_inds_update[space].data['updated'][0]
        else:
            isUpdated = Cell._sample_inds_update
        Cell._sample_inds_update_lock.release()
        return isUpdated

    @staticmethod
    def _set_sel_var_inds(space, var_name, inds):
        Cell._sel_var_inds_lock.acquire()
        Cell._sel_var_inds[(space,var_name)] = inds
        Cell._sel_var_inds_lock.release()
    
    @staticmethod
    def _reset_sel_var_inds():
        Cell._sel_var_inds_lock.acquire()
        Cell._sel_var_inds = {}
        Cell._sel_var_inds_lock.release()

    @staticmethod
    def _get_sel_var_inds(space=None, var_name=None):
        inds = []
        Cell._sel_var_inds_lock.acquire()
        if (space,var_name) in Cell._sel_var_inds:
            inds =  Cell._sel_var_inds[(space,var_name)]
        else:
            inds =  Cell._sel_var_inds
        Cell._sel_var_inds_lock.release()
        return inds

    @staticmethod
    def _delete_sel_var_inds(space, var_name):
        Cell._sel_var_inds_lock.acquire()
        if (space,var_name) in Cell._sel_var_inds:
            del Cell._sel_var_inds[(space,var_name)]
        Cell._sel_var_inds_lock.release()
    
    @staticmethod
    def _set_sel_space(space):
        Cell._sel_space_lock.acquire()
        Cell._sel_space = space
        Cell._sel_space_lock.release() 

    @staticmethod
    def _reset_sel_space():
        Cell._sel_space_lock.acquire()
        Cell._sel_space = ""
        Cell._sel_space_lock.release()

    @staticmethod
    def _get_sel_space():
        sel_space = ""
        Cell._sel_space_lock.acquire()
        sel_space = Cell._sel_space 
        Cell._sel_space_lock.release() 
        return sel_space

    @staticmethod
    def _set_sel_var_idx_dims_values(var_name, dict_data):
        Cell._sel_var_idx_dims_values_lock.acquire()
        Cell._sel_var_idx_dims_values[var_name] = dict_data
        Cell._sel_var_idx_dims_values_lock.release() 

    @staticmethod
    def _reset_sel_var_idx_dims_values():
        Cell._sel_var_idx_dims_values_lock.acquire()
        Cell._sel_var_idx_dims_values = {}
        Cell._sel_var_idx_dims_values_lock.release() 

    @staticmethod
    def _get_sel_var_idx_dims_values(var_name=None):
        idx_v = {}
        Cell._sel_var_idx_dims_values_lock.acquire()
        if var_name in Cell._sel_var_idx_dims_values:
            idx_v = Cell._sel_var_idx_dims_values[var_name] 
        else:
            idx_v = Cell._sel_var_idx_dims_values
        Cell._sel_var_idx_dims_values_lock.release() 
        return idx_v

    @staticmethod
    def _delete_sel_var_idx_dims_values(var_name):
        Cell._sel_var_idx_dims_values_lock.acquire()
        if var_name in Cell._sel_var_idx_dims_values:
            del Cell._sel_var_idx_dims_values[var_name]
        Cell._sel_var_idx_dims_values_lock.release()

    @staticmethod
    def _set_var_x_range(space, var_name, dict_data):
        Cell._var_x_range_lock.acquire()
        if (space,var_name) in Cell._var_x_range:
            Cell._var_x_range[(space,var_name)].data = dict_data
        Cell._var_x_range_lock.release() 

    @staticmethod
    def _reset_var_x_range():
        Cell._var_x_range_lock.acquire()
        for sp, var in Cell._var_x_range:
            Cell._var_x_range[(sp,var)].data = dict(xmin=[],xmax=[])
        Cell._var_x_range_lock.release() 

    @staticmethod
    def _get_var_x_range(space=None, var_name=None):
        x_range = {}
        Cell._var_x_range_lock.acquire()
        if (space,var_name) in Cell._var_x_range:
            x_range = Cell._var_x_range[(space,var_name)].data
        else:
            x_range = Cell._var_x_range
        Cell._var_x_range_lock.release() 
        return x_range

    @staticmethod
    def _set_global_update(global_update):
        Cell._global_update_lock.acquire()
        Cell._global_update = global_update
        Cell._global_update_lock.release() 

    @staticmethod
    def _get_global_update():
        global_update = False
        Cell._global_update_lock.acquire()
        global_update = Cell._global_update 
        Cell._global_update_lock.release() 
        return global_update