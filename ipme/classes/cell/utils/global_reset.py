import threading
from functools import partial

class GlobalReset:

    def __init__(self):
        pass

    @staticmethod
    def global_reset_callback(grid, event):
        grid.ic.reset_sel_var_inds()
        grid.ic.reset_sel_space()
        grid.ic.reset_sel_var_idx_dims_values()
        grid.ic.reset_var_x_range()
        grid.ic.set_global_update(True)
        for sp in grid.spaces:
            grid.ic.add_space_threads(threading.Thread(target = partial(GlobalReset._global_reset_thread, grid.ic, sp), daemon = True))
        grid.ic.space_threads_join()
        grid.ic.set_global_update(False)

    @staticmethod
    def _global_reset_thread(ic, space):
        ic.reset_sample_inds(space)
        ic.selection_threads_join(space)
