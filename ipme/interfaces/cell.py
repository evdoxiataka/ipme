from abc import ABC, abstractmethod

from ..cell.utils.cell_widgets import CellWidgets
from ..utils.constants import BORDER_COLORS

from bokeh.models import  Toggle, Div
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

        self._toggle = {}
        self._div = {}
        self._initialize_toggle_div()

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

    def _initialize_toggle_div(self):
        for space in self.spaces:
            width = self.plot[space].plot_width
            height = 40
            sizing_mode = self.plot[space].sizing_mode
            label = self.name + " ~ " + self._data.get_var_dist(self.name)
            text = """parents: %s <br>dims: %s"""%(self._data.get_var_parents(self.name), list(self._data.get_idx_dimensions(self.name)))
            if sizing_mode == 'fixed':
                self._toggle[space] = Toggle(label = label,  active = False,
                width = width, height = height, sizing_mode = sizing_mode, margin = (0,0,0,0))
                self._div[space] = Div(text = text,
                width = width, height = height, sizing_mode = sizing_mode, margin = (0,0,0,0), background = BORDER_COLORS[0] )
            elif sizing_mode == 'scale_width' or sizing_mode == 'stretch_width':
                self._toggle[space] = Toggle(label = label,  active = False,
                height = height, sizing_mode = sizing_mode, margin = (0,0,0,0))
                self._div[space] = Div(text = text,
                height = height, sizing_mode = sizing_mode, margin = (0,0,0,0), background = BORDER_COLORS[0] )
            elif sizing_mode == 'scale_height' or sizing_mode == 'stretch_height':
                self._toggle[space] = Toggle(label = label,  active = False,
                width = width, sizing_mode = sizing_mode, margin = (0,0,0,0))
                self._div[space] = Div(text = text,
                width = width, sizing_mode = sizing_mode, margin = (0,0,0,0), background = BORDER_COLORS[0] )
            else:
                self._toggle[space] = Toggle(label = label,  active = False,
                sizing_mode = sizing_mode, margin = (0,0,0,0))
                self._div[space] = Div(text = text, sizing_mode = sizing_mode, margin = (0,0,0,0), background = BORDER_COLORS[0] )
            self._toggle[space].js_link('active', self.plot[space], 'visible')

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
