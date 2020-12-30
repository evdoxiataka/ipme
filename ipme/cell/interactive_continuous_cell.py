from ..interfaces.variable_cell import VariableCell
from .utils.cell_continuous_handler import CellContinuousHandler
from .utils.cell_clear_selection import CellClearSelection

from ..cell.utils.cell_widgets import CellWidgets

class InteractiveContinuousCell(VariableCell):

    def initialize_cds(self,space):
        samples = self._get_data_for_cur_idx_dims_values(space)
        self._source[space] = ColumnDataSource(data = kde(samples))
        max_v = self._source[space].data['y'].max()
        self._samples[space] = ColumnDataSource(data = dict(x=samples, y=np.asarray([-max_v/RUG_DIST_RATIO]*len(samples)), \
                                                            size=np.asarray([RUG_SIZE]*len(samples))))
        self._sel_samples[space] = ColumnDataSource(data = dict(x=np.array([]), y=np.array([]), \
                                                                size=np.array([])))
        self._selection[space] = ColumnDataSource(data=dict(x=np.array([]),y=np.array([])))
        self._reconstructed[space] = ColumnDataSource(data=dict(x=np.array([]),y=np.array([])))
        self._clear_selection[space] = ColumnDataSource(data=dict(x=[],y=[],isIn=[]))
        self._ic._var_x_range[(space,self._name)] = ColumnDataSource(data=dict(xmin=np.array([]),xmax=np.array([])))

    def initialize_fig(self,space):
        self._plot[space]=figure( x_range = self._x_range[space], tools="wheel_zoom,reset,box_zoom", toolbar_location='right',
                                  plot_width=PLOT_WIDTH, plot_height=PLOT_HEIGHT,  sizing_mode=SIZING_MODE)
        self._plot[space].border_fill_color = BORDER_COLORS[0]
        self._plot[space].xaxis.axis_label = ""
        self._plot[space].yaxis.visible = False
        self._plot[space].toolbar.logo = None
        self._plot[space].xaxis[0].ticker.desired_num_ticks = 3

        ##Events
        self._plot[space].on_event(events.Tap, partial(self._clear_selection_callback,space))
        self._plot[space].on_event(events.SelectionGeometry, partial(self._selectionbox_callback,space))
        ##on_change
        self._ic._sample_inds_update[space].on_change('data',partial(self._sample_inds_callback, space))


    def initialize_glyphs(self,space):
        CellContinuousHandler.initialize_glyphs_continuous(self, space)
        CellClearSelection.initialize_glyphs_x_button(self,space)


    def _widget_callback(self, attr, old, new, w_title, space):
        CellWidgets.widget_callback_interactive(self,attr, old, new, w_title, space)

    def _update_cds(self,space):
        CellContinuousHandler.update_cds_interactive_continuous(self, space)
