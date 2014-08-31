'''
Created on Jul 19, 2014

@author: oli
'''
from contextlib import contextmanager

class Algorithm(object):
    '''
    An algorithm for the visualizer
    '''
    
    def __init__(self):
        self.initialVertices = []
        self.vertices = []
        self.context = ""
        self.algorithmName = "algorithmName"
        
    def getName(self):
        return self.algorithmName
        
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
        
    
