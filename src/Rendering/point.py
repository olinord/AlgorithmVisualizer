
from color import COLOR_WHITE, Color

POINT_ALPHA = 1.0

class Point(object):
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.color = COLOR_WHITE
    
    def id(self):
        return "%f%f%f" % (self.x, self.y, self.z)
    
    def __eq__(self, otherPoint):
        return isinstance(otherPoint, type(self)) and hasattr(otherPoint, "id") and self.id() == otherPoint.id()
    
    def SetColor(self, color):
        if not isinstance(color, Color):
            raise RuntimeError("Point color needs to be an instance of Color")
        
        self.color = color
        self.color.alpha = POINT_ALPHA
        
    def GetColor(self):
        return self.color