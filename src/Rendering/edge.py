
from color import COLOR_BLACK, Color

EDGE_ALPHA = 0.8

class Edge(object):
    def __init__(self, edgeStartPoint, edgeEndPoint):
        self.start = edgeStartPoint
        self.end = edgeEndPoint
        self.color = COLOR_BLACK

    def id(self):
        return "%s%s" % (self.start.id(), self.end.id())

    def __eq__(self, otherEdge):
        return isinstance(otherEdge, type(self)) and hasattr(otherEdge, "id") and self.id() == otherEdge.id()

    def SetColor(self, color):
        if not isinstance(color, Color):
            raise RuntimeError("Edge color needs to be an instance of Color")

        self.color = color
        self.color.alpha = EDGE_ALPHA

    def GetColor(self):
        return self.color

    def GetStart(self):
        return self.start

    def GetEnd(self):
        return self.end
