'''
Created on Jul 19, 2014

@author: oli
'''
from contextlib import contextmanager

class Algorithm(object):
    '''
    An algorithm for the visualizer
    '''
    DIMENSIONS = 2 # or 3

    # Color description to color values
    # For example:
    # "Selected": (0.0, 1.0, 0.0, 1.0)
    # "Ignored": (0.0, 1.0, 0.0, 1.0)
    COLORS = {}

    def __init__(self):
        self.context = ""
        self.data = []

    def setData(self, data):
        self.data = data

    def getRenderData(self):
        raise NotImplementedError("%s: does not implement the 'getRenderData' function" % type(self))

    def step(self):
        raise NotImplementedError("%s: does not implement the 'step' function" % type(self))

    def endCondition(self):
        raise NotImplementedError("%s: does not implement the 'endCondition' function" % type(self))

    @contextmanager
    def stepContext(self, contextName):
        oldContext = self.context
        self.context = contextName

        yield

        self.context = oldContext
