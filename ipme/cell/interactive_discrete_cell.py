from ..interfaces.variable_cell import VariableCell

class InteractiveDiscreteCell(VariableCell):
    def __init__(self, name, control):
        """
            Parameters:
            --------
                name            A String within the set {"<variableName>"}.
                control         A Control object
        """
        self._clear_selection = {}
        VariableCell.__init__(self, name, control)
