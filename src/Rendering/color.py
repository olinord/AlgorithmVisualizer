'''
Created on Aug 10, 2014

@author: oli
'''

class Color(object):
    '''
    This class represents a color
    '''

    def __init__(self, red, blue, green, alpha):
        self.red = red
        self.blue = blue
        self.green = green
        self.alpha = alpha
        
COLOR_WHITE = Color(1.0, 1.0, 1.0, 1.0)
COLOR_BLACK = Color(0.0, 0.0, 0.0, 1.0)