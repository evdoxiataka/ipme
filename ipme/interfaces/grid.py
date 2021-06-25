from abc import ABC, abstractmethod
from ..classes.cell.utils.cell_widgets import CellWidgets

class Grid(ABC):
    def __init__(self, control, mode, vars = 'all', spaces = 'all'):
        """
            Parameters:
            --------
                control                 A IC object.
                mode                    A String in {"i","s"}, "i":interactive, "s":static.
                vars                    A List of variables to be presented in the graph
                spaces                  A List of spaces to be included in graph
            Sets:
            --------
                ic
                _data
                _mode
                _grids                  A Dict of pn.GridSpec objects
                                        Either {<var_name>:{<space>:pn.GridSpec}}
                                        Or {<space>:pn.GridSpec}
                cells                  A Dict either {<var_name>:Cell object} or {<pred_check>:Cell object},
                                        where pred_check in {'min','max','mean','std'}.
                spaces                 A List of available spaces in this grid. Elements in {'prior','posterior'}
                cells_widgets          A Dict dict1 of the form (key1,value1) = (<widget_name>, dict2)
                                        dict2 of the form (key1,value1) = (<space>, List of <cell_name>).
                plotted_widgets        A Dict of the form {<space>: List of widget objects to be plotted} .
        """
        self.ic = control
        self._data = control.data
        self._mode = mode
        self._vars = vars
        # self._spaces_to_included = spaces
        self._grids = {}
        self.cells = {}
        self.spaces = spaces
        self._create_grids()

        self.cells_widgets = {}
        self.plotted_widgets = {}
        self._add_widgets()

    @abstractmethod
    def _create_grids(self):
        pass

    def _add_widgets(self):
        CellWidgets.link_cells_widgets(self)
        if self._mode == "i":
            CellWidgets.set_plotted_widgets_interactive(self)
        else:
            CellWidgets.set_plotted_widgets_static(self)

    ## GETTERS
    def get_grids(self):
        return self._grids

    def get_plotted_widgets(self):
        return self.plotted_widgets

    def get_cells(self):
        return self.cells

