from ...utils.functions import get_dim_names_options, get_w2_w1_val_mapping

from functools import partial
from bokeh.models.widgets import Select

class CellWidgets():

    @staticmethod
    def initialize_widgets(cell):
        for space in cell._spaces:
            cell._widgets[space] = {}
            for _, d_dim in cell._idx_dims.items():
                n1, n2, opt1, opt2 = get_dim_names_options(d_dim)
                cell._widgets[space][n1] = Select(title = n1, value = opt1[0], options = opt1)
                cell._widgets[space][n1].on_change("value", partial(cell._widget_callback, w_title = n1, space = space))
                if n1 not in cell._cur_idx_dims_values:
                    inds = [i for i,v in enumerate(d_dim.values) if v == opt1[0]]
                    cell._cur_idx_dims_values[n1] = inds
                if n2:
                    cell._widgets[space][n2] = Select(title = n2, value = opt2[0], options=opt2)
                    cell._widgets[space][n2].on_change("value", partial(cell._widget_callback, w_title = n2, space = space))
                    cell._ic._idx_widgets_mapping(space, d_dim, n1, n2)
                    if n2 not in cell._cur_idx_dims_values:
                        cell._cur_idx_dims_values[n2] = [0]

    @staticmethod
    def widget_callback(variableCell, attr, old, new, w_title, space):
        inds = -1
        w2_title = ""
        values = []
        w1_w2_idx_mapping = variableCell._control._get_w1_w2_idx_mapping()
        w2_w1_val_mapping = variableCell._control._get_w2_w1_val_mapping()
        w2_w1_idx_mapping = variableCell._control._get_w2_w1_idx_mapping()
        widgets = variableCell._widgets[space]
        if space in w1_w2_idx_mapping and w_title in w1_w2_idx_mapping[space]:
            for w2_title in w1_w2_idx_mapping[space][w_title]:
                name = w_title+"_idx_"+w2_title
                if name in variableCell._idx_dims:
                    values = variableCell._idx_dims[name].values
        elif w_title in variableCell._idx_dims:
            values = variableCell._idx_dims[w_title].values
        elif space in w2_w1_idx_mapping and w_title in w2_w1_idx_mapping[space]:
            for w1_idx in w2_w1_idx_mapping[space][w_title]:
                w1_value = widgets[w1_idx].value
                values = w2_w1_val_mapping[space][w_title][w1_value]
        inds = [i for i,v in enumerate(values) if v == new]
        if inds == -1 or len(inds) == 0:
            return
        variableCell._cur_idx_dims_values[w_title] = inds
        if w2_title and w2_title in variableCell._cur_idx_dims_values:
            variableCell._cur_idx_dims_values[w2_title] = [0]

    @staticmethod
    def widget_callback_interactive(variableCell, attr, old, new, w_title, space):
        CellWidgets.widget_callback(variableCell, attr, old, new, w_title, space)
        variableCell._update_source_cds(space)
        variableCell._ic._set_global_update(True)
        variableCell._update_cds(space)

    @staticmethod
    def widget_callback_static(variableCell, attr, old, new, w_title, space):
        CellWidgets.widget_callback(variableCell, attr, old, new, w_title, space)
        variableCell._update_cds(space)
