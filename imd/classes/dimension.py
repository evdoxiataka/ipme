class Dimension:
    def __init__(self, name, label='', range=(None,None), step=0, unit='', values=[]):
        self.name=name        
        if label!='' and label is not None:
            self.label=label
        else:
            self.label=name
        self.range=range 
        self.step=step
        self.unit=unit
        self.values=values