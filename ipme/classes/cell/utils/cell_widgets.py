from ipme.utils.functions import get_dim_names_options
from .global_reset import GlobalReset

from bokeh.models.widgets import Select, Button

from functools import partial

class CellWidgets:

    def __init__(self):
        pass

    @staticmethod
    def initialize_widgets(cell):
        for space in cell.spaces:
            cell.widgets[space] = {}
            for _, d_dim in cell.idx_dims.items():
                n1, n2, opt1, opt2 = get_dim_names_options(d_dim)
                cell.widgets[space][n1] = Select(title = n1, value = opt1[0], options = opt1)
                cell.widgets[space][n1].on_change("value", partial(cell.widget_callback, w_title = n1, space = space))
                if n1 not in cell.cur_idx_dims_values:
                    inds = [i for i,v in enumerate(d_dim.values) if v == opt1[0]]
                    cell.cur_idx_dims_values[n1] = inds
                if n2:
                    cell.widgets[space][n2] = Select(title = n2, value = opt2[0], options=opt2)
                    cell.widgets[space][n2].on_change("value", partial(cell.widget_callback, w_title = n2, space = space))
                    cell.ic.idx_widgets_mapping(space, d_dim, n1, n2)
                    if n2 not in cell.cur_idx_dims_values:
                        cell.cur_idx_dims_values[n2] = [0]

    @staticmethod
    def widget_callback(variableCell, attr, old, new, w_title, space):
        inds = -1
        w2_title = ""
        values = []
        w1_w2_idx_mapping = variableCell.ic.get_w1_w2_idx_mapping()
        w2_w1_val_mapping = variableCell.ic.get_w2_w1_val_mapping()
        w2_w1_idx_mapping = variableCell.ic.get_w2_w1_idx_mapping()
        widgets = variableCell.widgets[space]
        if space in w1_w2_idx_mapping and w_title in w1_w2_idx_mapping[space]:
            for w2_title in w1_w2_idx_mapping[space][w_title]:
                name = w_title+"_idx_"+w2_title
                if name in variableCell.idx_dims:
                    values = variableCell.idx_dims[name].values
        elif w_title in variableCell.idx_dims:
            values = variableCell.idx_dims[w_title].values
        elif space in w2_w1_idx_mapping and w_title in w2_w1_idx_mapping[space]:
            for w1_idx in w2_w1_idx_mapping[space][w_title]:
                w1_value = widgets[w1_idx].value
                values = w2_w1_val_mapping[space][w_title][w1_value]
        inds = [i for i,v in enumerate(values) if v == new]
        if inds == -1 or len(inds) == 0:
            return
        variableCell.cur_idx_dims_values[w_title] = inds
        if w2_title and w2_title in variableCell.cur_idx_dims_values:
            variableCell.cur_idx_dims_values[w2_title] = [0]

    @staticmethod
    def widget_callback_interactive(variableCell, attr, old, new, w_title, space):
        CellWidgets.widget_callback(variableCell, attr, old, new, w_title, space)
        print(variableCell.name, "before", variableCell.source[space].data['x'][0])
        variableCell.update_source_cds(space)
        print(variableCell.name, "after func ret", variableCell.source[space].data['x'][0])
        variableCell.ic.set_global_update(True)
        variableCell.update_cds(space)

    @staticmethod
    def widget_callback_static(variableCell, attr, old, new, w_title, space):
        CellWidgets.widget_callback(variableCell, attr, old, new, w_title, space)
        variableCell.update_cds(space)

    @staticmethod
    def link_cells_widgets(grid):
        for c_id, cell in grid.cells.items():
            cell_spaces = cell.get_spaces()
            for space in cell_spaces:
                for w_id, w in cell.get_widgets_in_space(space).items():
                    if w_id in grid.cells_widgets:
                        if space in grid.cells_widgets[w_id]:
                            grid.cells_widgets[w_id][space].append(c_id)
                        else:
                            grid.cells_widgets[w_id][space] = [c_id]
                        # Cell._num_widgets[w_id] = Cell._num_widgets[w_id] + 1
                        ## Every new widget is linked to the corresponding widget (of same name)
                        ## of the 1st space in grid.cells_widgets[w_id]
                        ## Find target cell to link with current cell
                        f_space = list(grid.cells_widgets[w_id].keys())[0]
                        CellWidgets._link_widget_to_target(grid, w, w_id, f_space)
                    else:
                        grid.cells_widgets[w_id] = {}
                        grid.cells_widgets[w_id][space] = [c_id]
                        f_space = list(grid.cells_widgets[w_id].keys())[0]
                        if f_space != space:
                            CellWidgets._link_widget_to_target(grid, w, w_id, f_space)
                        else:
                            w = grid.cells[c_id].get_widget(space, w_id)
                            w.on_change('value', partial(grid.ic.menu_item_click_callback, grid.cells, grid.cells_widgets, space, w_id))

    @staticmethod
    def _link_widget_to_target(grid, w, w_id, f_space):
        if len(grid.cells_widgets[w_id][f_space]):
            t_c_id = grid.cells_widgets[w_id][f_space][0]
            t_w = grid.cells[t_c_id].get_widget(f_space, w_id)
            if t_w is not None and hasattr(t_w,'js_link'):
                t_w.js_link('value', w, 'value')

    @staticmethod
    def set_plotted_widgets(grid):
        grid.plotted_widgets = {}
        for w_id, space_widgets_dict in grid.cells_widgets.items():
            w_spaces = list(space_widgets_dict.keys())
            if len(w_spaces):
                f_space = w_spaces[0]
                f_w_list = space_widgets_dict[f_space]
                if len(f_w_list):
                    c_id = f_w_list[0]
                    for space in w_spaces:
                        if space not in grid.plotted_widgets:
                            grid.plotted_widgets[space] = {}
                        grid.plotted_widgets[space][w_id] = grid.cells[c_id].get_widget(f_space, w_id)
        b = Button(label='Reset Diagram', button_type="primary")
        b.on_click(partial(GlobalReset.global_reset_callback, grid))
        for space in grid.spaces:
            if space not in grid.plotted_widgets:
                grid.plotted_widgets[space] = {}
            grid.plotted_widgets[space]["resetButton"] = b
