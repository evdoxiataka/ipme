from abc import ABC, abstractmethod

from ipme.classes.cell.utils.cell_widgets import CellWidgets
from bokeh.io.export import get_screenshot_as_png

class Cell(ABC):
    def __init__(self, vars, control):
        """
            Each cell will occupy a certain number of grid columns and will lie on a certain grid row.
            Parameters:
            --------
                vars                    A List of variableNames of the model.
                control                 An IC object
            Sets:
            --------
                vars
                ic
                spaces                 A List of Strings in {"prior","posterior"}.
                idx_dims               A Dict {<var_name>:{<dim_name>:Dimension obj}}.
                cur_idx_dims_values    A Dict {<var_name>:{<dim_name>: Current value of <dim_name>}}.

                plot                   A Dict {<space>: (bokeh) plot object}.
                widgets                A Dict {<space>: {<widget_title>: A (bokeh) widget object} }.
        """
        self.vars = vars
        self.ic = control
        self._data = control.data
        self.spaces = self._define_spaces()

        #idx_dims-related variables
        self.idx_dims = self._data.get_idx_dimensions(self.vars)
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

    def get_plot(self, space):
        if space in self.plot:
            return self.plot[space]
        else:
            return None

    def get_screenshot(self, space):
        if space in self.plot:
            return get_screenshot_as_png(self.plot[space])
        else:
            return None

    def get_spaces(self):
        return self.spaces
