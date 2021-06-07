from ...utils.functions import get_w2_w1_val_mapping

from bokeh.models import ColumnDataSource

import numpy as np
import threading

class IC:
    def __init__(self, data_obj):
        """
            This class regulates the interaction control of the tool.
            Parameters:
            --------
                data_obj                A Data object.
            Sets:
            --------
            _w1_w2_idx_mapping      A Dict {<space>: Dict {<w_name1>:(w_name2,widgets_idx)}}.
            _w2_w1_idx_mapping      A Dict {<space>: Dict {<w_name2>:(w_name1,widgets_idx)}}.
            _w2_w1_val_mapping      A Dict {<space>: Dict {<w_name2>:{<w1_value>: A List of <w_name2> values for <w1_value>}}.
        """
        self.data = data_obj
        self.num_cells = 0
        self.widgets_interactions = 0
        self.selection_interactions = 0
        ##threads lists
        self._selection_threads = {}
        self._space_threads = []
        self._widget_threads = []
        ##locks
        self._sel_lock = threading.Lock()
        self._widget_lock = threading.Lock()
        self._sample_inds_lock = threading.Lock()
        self._sample_inds_update_lock = threading.Lock()
        self._sel_var_inds_lock = threading.Lock()
        self._sel_space_lock = threading.Lock()
        self._sel_var_idx_dims_values_lock = threading.Lock()
        self._var_x_range_lock = threading.Lock()
        self._global_update_lock = threading.Lock()
        self._space_lock = threading.Lock()
        self._w1_w2_idx_mapping_lock = threading.Lock()
        self._w2_w1_idx_mapping_lock = threading.Lock()
        self._w2_w1_val_mapping_lock = threading.Lock()
        self._widgets_interactions_lock = threading.Lock()
        self._selection_interactions_lock = threading.Lock()
        ##events
        self.sel_lock_event = threading.Event()
        self.widget_lock_event = threading.Event()
        ##idx_widgets
        self._w1_w2_idx_mapping = {}
        self._w2_w1_idx_mapping = {}
        self._w2_w1_val_mapping = {}
        ##Interaction-related variables
        self.sample_inds = dict(prior = ColumnDataSource(data = dict(inds = [])), posterior = ColumnDataSource(data = dict(inds=[])))
        self.sample_inds_update = dict(prior = ColumnDataSource(data = dict(updated = [False])), posterior = ColumnDataSource(data = dict(updated = [False])))
        self._sel_var_inds = {}
        self._sel_space = ""
        self.sel_var_idx_dims_values = {}
        self.var_x_range = {}
        self._global_update = False

    def idx_widgets_mapping(self, space, d_dim, w1_title, w2_title):
        if space in self._w1_w2_idx_mapping:
            if w1_title in self._w1_w2_idx_mapping[space]:
                if w2_title not in self._w1_w2_idx_mapping[space][w1_title]:
                    self._w1_w2_idx_mapping[space][w1_title].append(w2_title)
            else:
                self._w1_w2_idx_mapping[space][w1_title] = [w2_title]
            if w2_title in self._w2_w1_idx_mapping[space]:
                if w1_title not in  self._w2_w1_idx_mapping[space][w2_title]:
                    self._w2_w1_idx_mapping[space][w2_title].append(w1_title)
            else:
                self._w2_w1_idx_mapping[space][w2_title] = [w1_title]
            if w2_title not in self._w2_w1_val_mapping[space]:
                self._w2_w1_val_mapping[space][w2_title] = get_w2_w1_val_mapping(d_dim)
        else:
            self._w1_w2_idx_mapping[space] = {}
            self._w1_w2_idx_mapping[space][w1_title] = [w2_title]
            self._w2_w1_idx_mapping[space] = {}
            self._w2_w1_idx_mapping[space][w2_title] = [w1_title]
            self._w2_w1_val_mapping[space] = {}
            self._w2_w1_val_mapping[space][w2_title] = get_w2_w1_val_mapping(d_dim)

    def set_coordinates(self, grid, dim, options, value):
        if isinstance(options, list) and len(options) and dim in grid.cells_widgets:
            spaces = list(grid.cells_widgets[dim].keys())
            # set value and options of all dim widgets
            # of variables manually, because jslink
            # is not automatically triggered in this case
            for s_i, sp in enumerate(spaces[::-1]):
                w_list = grid.cells_widgets[dim][sp]
                for c_i, c_id in enumerate(w_list[::-1]):
                    if c_id >= 0 and len(grid.cells):
                        cell = grid.cells[c_id]
                        widget = cell.get_widget(sp, dim)
                        if s_i == 0 and c_i == 0:
                            if value == widget.value:
                                if options == widget.options:
                                    return
                            else:
                                self.decrease_widgets_interactions()
                        widget.options = options
                        widget.value = value

    def _idx_widget_update(self, grid, new, w1_dim, space):
        w1_w2_idx_mapping = self.get_w1_w2_idx_mapping()
        w2_w1_val_mapping = self.get_w2_w1_val_mapping()
        if space in w1_w2_idx_mapping and w1_dim in w1_w2_idx_mapping[space]:
            for w2_dim in w1_w2_idx_mapping[space][w1_dim]:
                w2_options = w2_w1_val_mapping[space][w2_dim][new]
                self.set_coordinates(grid, w2_dim, w2_options, w2_options[0])

    def menu_item_click_callback(self, grid, space, w_id, attr, old, new):
        if old == new:
            return
        self.increase_widgets_interactions()
        num_widg = 0
        if w_id in grid.cells_widgets:
            for sp in grid.cells_widgets[w_id]:
                num_widg += len(grid.cells_widgets[w_id][sp])
        num_widg_threads = 0
        while num_widg_threads < num_widg:
            self.widget_lock_event.wait()
            self.widget_lock_event.clear()
            self._widget_lock.acquire()
            num_widg_threads = len(self._widget_threads)
            self._widget_lock.release()
        self._widget_lock.acquire()
        t_sel = self._widget_threads
        self._widget_lock.release()
        for t in t_sel:
            t.start()
        for t in t_sel:
            t.join()
        self._widget_lock.acquire()
        self._widget_threads.clear()
        self._widget_lock.release()
        self._idx_widget_update(grid, new, w_id, space)

    def space_threads_join(self):
        self._space_lock.acquire()
        for i,_ in enumerate(self._space_threads):
            self._space_threads[i].start()
        for i,_ in enumerate(self._space_threads):
            self._space_threads[i].join()
        self._space_threads.clear()
        self._space_lock.release()

    def selection_threads_join(self, space):
        num_sel_threads = 0
        while num_sel_threads < self.num_cells:
            self.sel_lock_event.wait()
            self.sel_lock_event.clear()
            self._sel_lock.acquire()
            if space in self._selection_threads:
                num_sel_threads = len(self._selection_threads[space])
            self._sel_lock.release()
        self._sel_lock.acquire()
        t_sel = self._selection_threads[space]
        self._sel_lock.release()
        for t in t_sel:
            t.start()
        for t in t_sel:
            t.join()
        self._sel_lock.acquire()
        del self._selection_threads[space]
        self._sel_lock.release()

    def set_selection(self, var_name, space, x_range, cur_idx_dims_values):
        """
            Sets user selection
        """
        self._set_sel_space(space)
        self.set_var_x_range(space, var_name, dict(xmin = np.asarray([x_range[0]]), xmax = np.asarray([x_range[1]])))
        self._set_sel_var_idx_dims_values(var_name, dict(cur_idx_dims_values))

    def add_selection_threads(self, space, t):
        self._sel_lock.acquire()
        if space in self._selection_threads:
            self._selection_threads[space].append(t)
        else:
            self._selection_threads[space] = [t]
        self._sel_lock.release()

    def _get_selection_threads(self, space):
        sel_t = []
        self._sel_lock.acquire()
        if space in self._selection_threads:
            sel_t = self._selection_threads[space]
        self._sel_lock.release()
        return sel_t

    def add_space_threads(self, t):
        self._space_lock.acquire()
        self._space_threads.append(t)
        self._space_lock.release()

    def _get_space_threads(self):
        sp_t = []
        self._space_lock.acquire()
        sp_t = self._space_threads
        self._space_lock.release()
        return sp_t

    def get_w1_w2_idx_mapping(self):
        w1_w2_idx_mapping = {}
        self._w1_w2_idx_mapping_lock.acquire()
        w1_w2_idx_mapping = self._w1_w2_idx_mapping
        self._w1_w2_idx_mapping_lock.release()
        return w1_w2_idx_mapping

    def get_w2_w1_idx_mapping(self):
        w2_w1_idx_mapping = {}
        self._w2_w1_idx_mapping_lock.acquire()
        w2_w1_idx_mapping = self._w2_w1_idx_mapping
        self._w2_w1_idx_mapping_lock.release()
        return w2_w1_idx_mapping

    def get_w2_w1_val_mapping(self):
        w2_w1_val_mapping = {}
        self._w2_w1_val_mapping_lock.acquire()
        w2_w1_val_mapping = self._w2_w1_val_mapping
        self._w2_w1_val_mapping_lock.release()
        return w2_w1_val_mapping

    def add_widget_threads(self, t):
        self._widget_lock.acquire()
        self._widget_threads.append(t)
        self._widget_lock.release()

    def set_sample_inds(self, space, dict_data):
        self._sample_inds_lock.acquire()
        if space in self.sample_inds:
            self.sample_inds[space].data = dict_data
        self._sample_inds_lock.release()
        isup = self._get_sample_inds_update(space)
        self._set_sample_inds_update(space, dict(updated = [not isup]))

    def reset_sample_inds(self, space):
        self._sample_inds_lock.acquire()
        self.sample_inds[space].data = dict(inds=[])
        self._sample_inds_lock.release()
        isup = self._get_sample_inds_update(space)
        self._set_sample_inds_update(space, dict(updated = [not isup]))

    def get_sample_inds(self, space = None):
        inds = []
        self._sample_inds_lock.acquire()
        if space in self.sample_inds:
            inds = self.sample_inds[space].data['inds']
        else:
            inds = self.sample_inds
        self._sample_inds_lock.release()
        return inds

    def _set_sample_inds_update(self, space, dict_data):
        self._sample_inds_update_lock.acquire()
        if space in self.sample_inds_update:
            self.sample_inds_update[space].data = dict_data
        self._sample_inds_update_lock.release()

    def _get_sample_inds_update(self, space=None):
        isUpdated = False
        self._sample_inds_update_lock.acquire()
        if space in self.sample_inds_update:
            isUpdated = self.sample_inds_update[space].data['updated'][0]
        else:
            isUpdated = self.sample_inds_update
        self._sample_inds_update_lock.release()
        return isUpdated

    def set_sel_var_inds(self, space, var_name, inds):
        self._sel_var_inds_lock.acquire()
        self._sel_var_inds[(space,var_name)] = inds
        self._sel_var_inds_lock.release()

    def reset_sel_var_inds(self):
        self._sel_var_inds_lock.acquire()
        self._sel_var_inds = {}
        self._sel_var_inds_lock.release()

    def get_sel_var_inds(self, space=None, var_name=None):
        inds = []
        self._sel_var_inds_lock.acquire()
        if (space,var_name) in self._sel_var_inds:
            inds =  self._sel_var_inds[(space,var_name)]
        else:
            inds =  self._sel_var_inds
        self._sel_var_inds_lock.release()
        return inds

    def delete_sel_var_inds(self, space, var_name):
        self._sel_var_inds_lock.acquire()
        if (space,var_name) in self._sel_var_inds:
            del self._sel_var_inds[(space,var_name)]
        self._sel_var_inds_lock.release()

    def _set_sel_space(self, space):
        self._sel_space_lock.acquire()
        self._sel_space = space
        self._sel_space_lock.release()

    def reset_sel_space(self):
        self._sel_space_lock.acquire()
        self._sel_space = ""
        self._sel_space_lock.release()

    def get_sel_space(self):
        sel_space = ""
        self._sel_space_lock.acquire()
        sel_space = self._sel_space
        self._sel_space_lock.release()
        return sel_space

    def _set_sel_var_idx_dims_values(self, var_name, dict_data):
        self._sel_var_idx_dims_values_lock.acquire()
        self.sel_var_idx_dims_values[var_name] = dict_data
        self._sel_var_idx_dims_values_lock.release()

    def reset_sel_var_idx_dims_values(self):
        self._sel_var_idx_dims_values_lock.acquire()
        self.sel_var_idx_dims_values = {}
        self._sel_var_idx_dims_values_lock.release()

    def get_sel_var_idx_dims_values(self, var_name=None):
        idx_v = {}
        self._sel_var_idx_dims_values_lock.acquire()
        if var_name in self.sel_var_idx_dims_values:
            idx_v = self.sel_var_idx_dims_values[var_name]
        else:
            idx_v = self.sel_var_idx_dims_values
        self._sel_var_idx_dims_values_lock.release()
        return idx_v

    def delete_sel_var_idx_dims_values(self, var_name):
        self._sel_var_idx_dims_values_lock.acquire()
        if var_name in self.sel_var_idx_dims_values:
            del self.sel_var_idx_dims_values[var_name]
        self._sel_var_idx_dims_values_lock.release()

    def set_var_x_range(self, space, var_name, dict_data):
        self._var_x_range_lock.acquire()
        if (space,var_name) in self.var_x_range:
            self.var_x_range[(space, var_name)].data = dict_data
        self._var_x_range_lock.release()

    def reset_var_x_range(self):
        self._var_x_range_lock.acquire()
        for sp, var in self.var_x_range:
            self.var_x_range[(sp, var)].data = dict(xmin=[], xmax=[])
        self._var_x_range_lock.release()

    def get_var_x_range(self, space=None, var_name=None):
        x_range = {}
        self._var_x_range_lock.acquire()
        if (space,var_name) in self.var_x_range:
            x_range = self.var_x_range[(space, var_name)].data
        else:
            x_range = self.var_x_range
        self._var_x_range_lock.release()
        return x_range

    def set_global_update(self, global_update):
        self._global_update_lock.acquire()
        self._global_update = global_update
        self._global_update_lock.release()

    def get_global_update(self):
        global_update = False
        self._global_update_lock.acquire()
        global_update = self._global_update
        self._global_update_lock.release()
        return global_update

    def increase_widgets_interactions(self):
        self._widgets_interactions_lock.acquire()
        self.widgets_interactions = self.widgets_interactions + 1
        self._widgets_interactions_lock.release()

    def decrease_widgets_interactions(self):
        self._widgets_interactions_lock.acquire()
        self.widgets_interactions = self.widgets_interactions - 1
        self._widgets_interactions_lock.release()

    def get_widgets_interactions(self):
        w_inters = -1
        self._widgets_interactions_lock.acquire()
        w_inters = self.widgets_interactions
        self._widgets_interactions_lock.release()
        return w_inters

    def increase_selection_interactions(self):
        self._selection_interactions_lock.acquire()
        self.selection_interactions = self.selection_interactions + 1
        self._selection_interactions_lock.release()

    def get_selection_interactions(self):
        s_inters = -1
        self._selection_interactions_lock.acquire()
        s_inters = self.selection_interactions
        self._selection_interactions_lock.release()
        return s_inters
