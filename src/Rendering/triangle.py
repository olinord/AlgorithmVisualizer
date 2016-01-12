
from color import COLOR_WHITE
from edge import Edge

TRIANGLE_ALPHA = 0.4

class Triangle(object):

    def __init__(self, pointA, pointB, pointC, color=COLOR_WHITE):
        self.color = color

        self.a = pointA
        self.a.SetColor(color)

        self.b = pointB
        self.b.SetColor(color)

        self.c = pointC
        self.c.SetColor(color)

        self.ab = Edge(pointA, pointB)
        self.ab.SetColor(color)

        self.bc = Edge(pointB, pointC)
        self.bc.SetColor(color)

        self.ca = Edge(pointC, pointA)
        self.ca.SetColor(color)

        self.color.alpha = TRIANGLE_ALPHA

    def GetPointA(self):
        return self.a

    def GetPointB(self):
        return self.b

    def GetPointC(self):
        return self.c

    def GetEdgeAB(self):
        return self.ab

    def GetEdgeBC(self):
        return self.bc

    def GetEdgeCA(self):
        return self.ca

    def GetColor(self):
        return self.color

    def SetColor(self, color):
        self.color = color
        self.color.alpha = TRIANGLE_ALPHA

        self.a.SetColor(color)
        self.b.SetColor(color)
        self.c.SetColor(color)

        self.ab.SetColor(color)
        self.bc.SetColor(color)
        self.ca.SetColor(color)
