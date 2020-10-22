""" Cell Interface

    Colors-related constants:

    Same color palette used in arviz-darkgrid style: 
    https://arviz-devs.github.io/arviz/examples/matplotlib/mpl_styles.html

    Color-blind friendly cycle designed using https://colorcyclepicker.mpetroff.net/
"""
# COLORS=['#008080','#403F6F','#800080']
COLORS = ['#2a2eec', '#fa7c17', '#328c06', '#c10c90', '#933708', '#65e5f3', '#e6e135', '#1ccd6a', '#bd8ad5', '#b16b57']
BORDER_COLORS=['#d8d8d8','#FFFFFF']

## Plot sizing-related constants
PLOT_WIDTH = 220
PLOT_HEIGHT = 220
SIZING_MODE = "fixed"

## Rug plot
RUG_DIST_RATIO = 5.0
RUG_SIZE = 10 #in screen units

"""" Grid Interface

"""
##
MAX_NUM_OF_COLS_PER_ROW = 12
COLS_PER_VAR = 2
MAX_NUM_OF_VARS_PER_ROW = 5