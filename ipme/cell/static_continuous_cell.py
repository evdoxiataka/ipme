from ..interfaces.variable_cell import VariableCell

class StaticContinuousCell(VariableCell):
    def __init__(self, name, control):
        """
            Parameters:
            --------
                name            A String within the set {"<variableName>"}.
                control         A Control object
        """
        VariableCell.__init__(self, name, control)

    def set_stratum(self, space, stratum = 0):
        pass
