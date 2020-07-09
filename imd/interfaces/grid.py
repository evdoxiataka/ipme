from abc import ABC, abstractmethod
from ..interfaces.cell import Cell
from bokeh.models.widgets import Button
#import pyautogui

class Grid(ABC): 
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
                _cells                  A Dict either {<var_name>:Cell object} or {<pred_check>:Cell object},
                                        where pred_check in {'min','max','mean','std'}.
                _spaces                 A List of available spaces in this grid. Elements in {'prior','posterior'}
                _cells_widgets          A Dict dict1 of the form (key1,value1) = (<widget_name>, dict2)
                                        dict2 of the form (key1,value1) = (<space>, List of tuples (<cell_id>,<widget_id>)
                                        of the widgets with same name).
                _plotted_widgets        A Dict of the form {<space>: List of widget objects to be plotted} .
        """
        self._data = data_obj  
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
        for space in self._spaces:  
            if space not in self._plotted_widgets:
                self._plotted_widgets[space] = []  
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
    
    def get_cells(self):
        return self._cells
            
