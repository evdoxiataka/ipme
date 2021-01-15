from ipme.utils.constants import COLORS, BORDER_COLORS, PLOT_HEIGHT, PLOT_WIDTH, SIZING_MODE

from bokeh.plotting import figure

from functools import partial

class CellPredCheckHandler:

    def __init__(self):
        pass

    @staticmethod
    def initialize_glyphs(predcheckCell, space):
        pass

    @staticmethod
    def initialize_glyphs_interactive(predcheckCell, space):
        pass

    @staticmethod
    def initialize_glyphs_static(predcheckCell, space):
        pass

    @staticmethod
    def initialize_fig(predcheckCell, space):
        predcheckCell.plot[space] = figure(tools = "wheel_zoom,reset", toolbar_location = 'right', plot_width = PLOT_WIDTH, plot_height = PLOT_HEIGHT, sizing_mode = SIZING_MODE)
        predcheckCell.plot[space].toolbar.logo = None
        predcheckCell.plot[space].yaxis.visible = False
        predcheckCell.plot[space].xaxis.axis_label = predcheckCell.func + "(" + predcheckCell.name + ")"
        predcheckCell.plot[space].border_fill_color = BORDER_COLORS[0]
        predcheckCell.plot[space].xaxis[0].ticker.desired_num_ticks = 3

    @staticmethod
    def initialize_fig_interactive(predcheckCell, space):
        CellPredCheckHandler.initialize_fig(predcheckCell, space)
        predcheckCell.ic.sample_inds[space].on_change('data', partial(predcheckCell.sample_inds_callback, space))

    @staticmethod
    def initialize_fig_static(predcheckCell, space):
        CellPredCheckHandler.initialize_fig(predcheckCell, space)

    @staticmethod
    def initialize_cds(predcheckCell, space):
        pass

    @staticmethod
    def initialize_cds_interactive(predcheckCell, space):
        pass

    @staticmethod
    def initialize_cds_static(predcheckCell, space):
        pass
