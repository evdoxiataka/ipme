from abc import ABC, abstractmethod
from bokeh.models.widgets import Button
from bokeh import events
import threading
from functools import partial
#import pyautogui

class Grid(ABC): 
    def __init__(self, inter_contr, mode):
        """
            Parameters:
            --------
                inter_contr             A IC object.      
                mode                    A String in {"i","s"}, "i":interactive, "s":static.     
            Sets:
            --------
                _ic
                _data                    
                _mode                                 
                _grids                  A Dict of pn.GridSpec objects 
                                        Either {<var_name>:{<space>:pn.GridSpec}}
                                        Or {<space>:pn.GridSpec}
                _cells                  A Dict either {<var_name>:Cell object} or {<pred_check>:Cell object},
                                        where pred_check in {'min','max','mean','std'}.
                _spaces                 A List of available spaces in this grid. Elements in {'prior','posterior'}
                _cells_widgets          A Dict dict1 of the form (key1,value1) = (<widget_name>, dict2)
                                        dict2 of the form (key1,value1) = (<space>, List of <cell_name>).
                _plotted_widgets        A Dict of the form {<space>: List of widget objects to be plotted} .
        """ 
        self._ic = inter_contr
        self._data = inter_contr._data 
        self._mode = mode
        self._grids = {}
        self._cells = {}
        self._spaces = []
        self._create_grids()          

        self._cells_widgets = {}        
        self._plotted_widgets = {}        
        self._add_widgets() 

    def _add_widgets(self):
        self._link_cells_widgets()
        self._set_plotted_widgets()

    def _link_cells_widgets(self):
        for c_id, cell in self._cells.items():
            cell_spaces = cell.get_spaces()
            for space in cell_spaces:
                for w_id, w in cell.get_widgets_in_space(space).items():
                    if w_id in self._cells_widgets:
                        if space in self._cells_widgets[w_id]:
                            self._cells_widgets[w_id][space].append(c_id)
                        else:
                            self._cells_widgets[w_id][space] = [c_id]
                        # Cell._num_widgets[w_id] = Cell._num_widgets[w_id] + 1
                        ## Every new widget is linked to the corresponding widget (of same name) 
                        ## of the 1st space in self._cells_widgets[w_id]
                        ## Find target cell to link with current cell
                        f_space = list(self._cells_widgets[w_id].keys())[0]
                        self._link_widget_to_target(w, w_id, f_space)                         
                    else:
                        self._cells_widgets[w_id] = {}
                        self._cells_widgets[w_id][space] = [c_id]
                        f_space = list(self._cells_widgets[w_id].keys())[0]
                        if f_space != space: 
                            self._link_widget_to_target(w, w_id, f_space) 
                        else:
                            w = self._cells[c_id].get_widget(space,w_id)
                            w.on_change('value', partial(self._ic._menu_item_click_callback, self._cells, self._cells_widgets, space, w_id))

    def _link_widget_to_target(self, w, w_id, f_space):
        if len(self._cells_widgets[w_id][f_space]):
            t_c_id = self._cells_widgets[w_id][f_space][0]
            t_w = self._cells[t_c_id].get_widget(f_space,w_id)
            if t_w is not None and hasattr(t_w,'js_link'):
                t_w.js_link('value', w, 'value')

    def _set_plotted_widgets(self):
        self._plotted_widgets = {}                      
        for w_id, space_widgets_dict in self._cells_widgets.items():
            w_spaces = list(space_widgets_dict.keys())
            if len(w_spaces):
                f_space = w_spaces[0]
                f_w_list = space_widgets_dict[f_space]
                if len(f_w_list):
                    c_id = f_w_list[0]
                    for space in w_spaces:
                        if space not in self._plotted_widgets:
                            self._plotted_widgets[space] = {}                   
                        self._plotted_widgets[space][w_id] = self._cells[c_id].get_widget(f_space,w_id)
        b = Button(label='Reset Diagram', button_type="primary")
        b.on_click(self._global_reset_callback)
        for space in self._spaces:  
            if space not in self._plotted_widgets:
                self._plotted_widgets[space] = {}  
            self._plotted_widgets[space]["resetButton"] = b

    def _global_reset_callback(self, event):
        self._ic._reset_sel_var_inds()
        self._ic._reset_sel_space()  
        self._ic._reset_sel_var_idx_dims_values()
        self._ic._reset_var_x_range() 
        self._ic._set_global_update(True)     
        for sp in self._spaces:  
            self._ic._add_space_threads(threading.Thread(target=partial(self._global_reset_thread,sp), daemon=True)) 
        self._ic._space_threads_join()
        self._ic._set_global_update(False) 

    def _global_reset_thread(self,space):
        self._ic._reset_sample_inds(space)
        self._ic._selection_threads_join(space)

    @abstractmethod
    def _create_grids(self):
        pass

    def get_grids(self):
        return self._grids

    def set_coordinate(self,coord_name,new_val):
        try:
            if coord_name in self._cells_widgets:
                space_widgets = self._cells_widgets[coord_name]
                for space in self._cells_widgets[coord_name]:
                    c_id_list = self._cells_widgets[coord_name][space]
                    for c_id in c_id_list:
                        w = self._cells[c_id].get_widget(space,coord_name)
                        old_v = w.value
                        w.value = new_val
                        w.trigger('value',new_val,new_val)
        except IndexError:
            raise IndexError()

    def get_plotted_widgets(self):
        return self._plotted_widgets
    
    def get_cells(self):
        return self._cells
            
