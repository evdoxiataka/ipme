from abc import ABC, abstractmethod

from ipme.classes.cell.utils.cell_widgets import CellWidgets

from bokeh.layouts import layout
from bokeh.io.export import get_screenshot_as_png

class Cell(ABC):
    def __init__(self, name, control):
        """
            Each cell will occupy a certain number of grid columns and will lie on a certain grid row.
            Parameters:
            --------
                name                    A String within the set {"<variableName>"}.
                control                 An IC object
            Sets:
            --------
                name
                ic
                spaces                 A List of Strings in {"prior","posterior"}.
                idx_dims
                cur_idx_dims_values    A Dict {<idx_dim_name>: Integer of current value index of <idx_dim_name>}.

                plot                   A Dict {<space>: (bokeh) plot object}.
                widgets                A Dict {<space>: {<widget_title>: A (bokeh) widget object} }.
                _w1_w2_idx_mapping      A Dict {<space>: Dict {<w_name1>:(w_name2,widgets_idx)}}.
                _w2_w1_idx_mapping      A Dict {<space>: Dict {<w_name2>:(w_name1,widgets_idx)}}.
                _w2_w1_val_mapping      A Dict {<space>: Dict {<w_name2>:{<w1_value>: A List of <w_name2> values for <w1_value>}}.
                _toggle                 A Dict {<space>: (bokeh) toggle button for visibility of figure}.
                _div                    A Dict {<space>: (bokeh) div parameter-related information}.
        """
        self.name = name
        self.ic = control
        self._data = control.data
        self.spaces = self._define_spaces()
        # self._type = self._data.get_var_dist_type(self.name)##to be deleted

        #idx_dims-related variables
        self.idx_dims = self._data.get_idx_dimensions(self.name)
        self.cur_idx_dims_values = {}

        self.plot = {}
        self.widgets = {}
        self._initialize_widgets()
        self._initialize_plot()

    def _define_spaces(self):
        data_spaces = self._data.get_spaces()
        spaces = []
        if "prior" in data_spaces:
            spaces.append("prior")
        if "posterior" in data_spaces:
            spaces.append("posterior")
        return spaces

    def _initialize_widgets(self):
        CellWidgets.initialize_widgets(self)

    @abstractmethod
    def widget_callback(self, attr, old, new, w_title, space):
        pass

    @abstractmethod
    def _initialize_plot(self):
        pass

    ## GETTERS
    def get_widgets(self):
        return self.widgets

    def get_widgets_in_space(self, space):
        if space in self.widgets:
            return self.widgets[space]
        else:
            return []

    def get_widget(self, space, id):
        try:
            return self.widgets[space][id]
        except IndexError:
            return None

    def get_plot(self, space, add_info = True):
        if space in self.plot:
            if add_info and space in self._toggle and space in self._div:
                return layout([self._toggle[space]], [self._div[space]], [self.plot[space]])
            else:
                return self.plot[space]
        else:
            return None

    def get_screenshot(self, space, add_info=True):
        if space in self.plot:
            if add_info and space in self._toggle and space in self._div:
                return get_screenshot_as_png(layout([self._toggle[space]], [self._div[space]], [self.plot[space]]))
            else:
                return get_screenshot_as_png(self.plot[space])
        else:
            return None

    def get_spaces(self):
        return self.spaces
