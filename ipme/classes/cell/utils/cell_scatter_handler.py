from ipme.utils.constants import  COLORS, BORDER_COLORS, PLOT_HEIGHT, PLOT_WIDTH, SIZING_MODE

from bokeh.models import ColumnDataSource, HoverTool
from bokeh.plotting import figure

import arviz as az
from functools import partial

class CellScatterHandler:

    def __init__(self):
        pass

    @staticmethod
    def initialize_glyphs_interactive(scatterCell, space):
        so = scatterCell.plot[space].circle(x="x", y="y", source = scatterCell.non_sel_samples[space], size=7, color=COLORS[0], line_color=None, fill_alpha = 0.1)
        re = scatterCell.plot[space].circle(x="x", y="y", source = scatterCell.sel_samples[space], size=7, color=COLORS[1], line_color=None, fill_alpha = 0.1)
        scatterCell.plot[space].patches(xs="x", ys="y", source = scatterCell.contours[space], line_color="line_color", fill_alpha="fill_alpha")
        # {"line_color":"black", "line_alpha":1},
        #     contourf_kwargs={"fill_alpha": 0, "cmap": "viridis"},
        ##Tooltips
        TOOLTIPS = [("x", "@x"), ("y","@y"),]
        hover = HoverTool( tooltips = TOOLTIPS, renderers = [so,re], mode = 'mouse')
        scatterCell.plot[space].tools.append(hover)

    @staticmethod
    def initialize_glyphs_static(scatterCell, space):
        so = scatterCell.plot[space].circle(x="x", y="y", source = scatterCell.samples[space], size=7, color=COLORS[0], line_color=None, fill_alpha = 0.1)
        scatterCell.plot[space].patches(xs="x", ys="y", source = scatterCell.contours[space], line_color="line_color", fill_alpha="fill_alpha")
        ##Tooltips
        TOOLTIPS = [("x", "@x"), ("y","@y"),]
        hover = HoverTool( tooltips = TOOLTIPS, renderers = [so], mode = 'mouse')
        scatterCell.plot[space].tools.append(hover)

    @staticmethod
    def initialize_fig(scatterCell, space):
        var1 = scatterCell.vars[0]
        var2 = scatterCell.vars[1]
        scatterCell.plot[space] = figure(x_range = scatterCell.x_range[var2][space], y_range = scatterCell.x_range[var1][space],tools = "wheel_zoom,reset,box_zoom", toolbar_location = 'right',
                                    plot_width = PLOT_WIDTH, plot_height = PLOT_HEIGHT, sizing_mode = SIZING_MODE)
        scatterCell.plot[space].border_fill_color = BORDER_COLORS[0]
        scatterCell.plot[space].xaxis.axis_label = var2
        scatterCell.plot[space].yaxis.axis_label = var1
        # scatterCell.plot[space].yaxis.visible = False
        scatterCell.plot[space].toolbar.logo = None
        scatterCell.plot[space].xaxis[0].ticker.desired_num_ticks = 3

    @staticmethod
    def initialize_fig_interactive(scatterCell, space):
        CellScatterHandler.initialize_fig(scatterCell, space)
        ##on_change
        scatterCell.ic.sample_inds_update[space].on_change('data', partial(scatterCell.sample_inds_callback, space))

    @staticmethod
    def initialize_fig_static(scatterCell, space):
        CellScatterHandler.initialize_fig(scatterCell, space)
        ##on_change
        scatterCell.ic.sample_inds_update[space].on_change('data', partial(scatterCell.sample_inds_callback, space))

    @staticmethod
    def initialize_cds(scatterCell, space):
        var1 = scatterCell.vars[0]
        var2 = scatterCell.vars[1]
        samples1 = scatterCell.get_data_for_cur_idx_dims_values(var1, space)
        samples2 = scatterCell.get_data_for_cur_idx_dims_values(var2, space)
        scatterCell.samples[space] = ColumnDataSource(data = dict(x = samples2, y = samples1))
        patch_x, patch_y = CellScatterHandler.get_contours(samples2, samples1)
        scatterCell.contours[space] = ColumnDataSource(data = dict(x = patch_x, y = patch_y, line_color=["black"]*len(patch_x), fill_alpha=[0]*len(patch_x)))
        scatterCell.ic.initialize_sample_inds(space, dict(inds = [False]*len(scatterCell.samples[space].data['x'])), dict(non_inds = [True]*len(scatterCell.samples[space].data['x'])))
  
    @staticmethod
    def initialize_cds_interactive(scatterCell, space):
        CellScatterHandler.initialize_cds(scatterCell, space)
        inds, non_inds = scatterCell.ic.get_sample_inds(space)
        sel_y = scatterCell.samples[space].data['y'][inds]
        non_sel_y = scatterCell.samples[space].data['y'][non_inds]
        sel_samples = scatterCell.samples[space].data['x'][inds]
        non_sel_samples = scatterCell.samples[space].data['x'][non_inds]
        scatterCell.sel_samples[space] = ColumnDataSource(data = dict( x = sel_samples, y = sel_y))
        scatterCell.non_sel_samples[space] = ColumnDataSource(data = dict( x = non_sel_samples, y = non_sel_y))
        
    @staticmethod
    def initialize_cds_static(scatterCell, space):
        CellScatterHandler.initialize_cds(scatterCell, space)
        #########TEST###########

    @staticmethod
    def update_cds_interactive(scatterCell, space):
        """
            Updates interaction-related ColumnDataSources (cds).
        """
        scatterCell.update_sel_samples_cds(space)

    @staticmethod
    def update_cds_static(scatterCell, space):
        """
            Update samples cds in the static mode
        """
        var1 = scatterCell.vars[0]
        var2 = scatterCell.vars[1]
        samples1 = scatterCell.get_data_for_cur_idx_dims_values(var1, space)
        samples2 = scatterCell.get_data_for_cur_idx_dims_values(var2, space)
        inds, _ = scatterCell.ic.get_sample_inds(space)
        if True in inds:
            sel_sample1 = samples1[inds]
            sel_sample2 = samples2[inds]
            scatterCell.samples[space].data = dict(x=sel_sample2, y=sel_sample1)
            patch_x, patch_y = CellScatterHandler.get_contours(sel_sample2, sel_sample1)
            scatterCell.contours[space].data = dict(x = patch_x, y = patch_y, line_color=["black"]*len(patch_x), fill_alpha=[0]*len(patch_x))
        else:
            scatterCell.samples[space].data = dict(x=samples2, y=samples1)
            patch_x, patch_y = CellScatterHandler.get_contours(samples2, samples1)
            scatterCell.contours[space].data = dict(x = patch_x, y = patch_y, line_color=["black"]*len(patch_x), fill_alpha=[0]*len(patch_x))
            
    ## ONLY FOR INTERACTIVE CASE
    @staticmethod
    def update_source_cds_interactive(scatterCell, space):
        """
            Updates samples ColumnDataSource (cds).
        """
        var1 = scatterCell.vars[0]
        var2 = scatterCell.vars[1]
        samples1 = scatterCell.get_data_for_cur_idx_dims_values(var1, space)
        samples2 = scatterCell.get_data_for_cur_idx_dims_values(var2, space)
        scatterCell.samples[space].data = dict(x=samples2, y=samples1)
        patch_x, patch_y = CellScatterHandler.get_contours(samples2, samples1)
        scatterCell.contours[space].data = dict(x = patch_x, y = patch_y, line_color=[COLORS[0]]*len(patch_x), fill_alpha=[0]*len(patch_x))

    @staticmethod
    def update_sel_samples_cds_interactive(scatterCell, space):
        """
            Updates reconstructed ColumnDataSource (cds).
        """
        samples1 = scatterCell.samples[space].data['x']
        samples2 = scatterCell.samples[space].data['y']
        inds, non_inds = scatterCell.ic.get_sample_inds(space)
        sel_sample1 = samples1[inds]
        sel_sample2 = samples2[inds]
        scatterCell.sel_samples[space].data = dict(x=sel_sample1, y=sel_sample2)
        non_sel_sample1 = samples1[non_inds]
        non_sel_sample2 = samples2[non_inds]
        scatterCell.non_sel_samples[space].data = dict(x=non_sel_sample1, y=non_sel_sample2)

    @staticmethod
    def get_contours(x, y):
        _, contour_glyphs = az.plot_kde(x, y,
        #     hdi_probs=[0.393, 0.865, 0.989],  # 1, 2 and 3 sigma contours
            contour_kwargs={"line_color":"black", "line_alpha":1},
            contourf_kwargs={"fill_alpha": 0, "cmap": "viridis"},
            backend="bokeh", return_glyph = True, show = False )
        patch_x = []
        patch_y = []
        for renderer in contour_glyphs:
            patch_x.append(renderer.data_source.data['x'].tolist())
            patch_y.append(renderer.data_source.data['y'].tolist())
        return patch_x, patch_y