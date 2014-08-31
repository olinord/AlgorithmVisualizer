from point import Point

def AddIfNotInList(objectToBeAdded, listToAddTo):
    if objectToBeAdded not in listToAddTo:
        listToAddTo.append(objectToBeAdded)

class Mesh(object):
    
    def __init__(self):
        self.triangles = []
        self.edges = []
        self.points = []
    
    def GetTriangles(self):
        return self.triangles
    
    
    def GetEdges(self):
        return self.edges
    
    
    def GetPoints(self):
        return self.points
    
    def GetBoundingBox(self):
        xBounds = [self.points[0].x, self.points[0].x]
        yBounds = [self.points[0].y, self.points[0].y]
        zBounds = [self.points[0].z, self.points[0].z]
        
        for point in self.points:
            xBounds = [min(xBounds[0], point.x), max(xBounds[1], point.x)]
            yBounds = [min(yBounds[0], point.y), max(yBounds[1], point.y)]
            zBounds = [min(zBounds[0], point.z), max(zBounds[1], point.z)]
            
        return [Point(x, y, z) for x in xBounds for y in yBounds for z in zBounds]
                
    
    def AddTriangle(self, triangle):        
        self.triangles.append(triangle)
        
        AddIfNotInList(triangle.GetEdgeAB(), self.edges)
        AddIfNotInList(triangle.GetEdgeBC(), self.edges)
        AddIfNotInList(triangle.GetEdgeCA(), self.edges)
                
        AddIfNotInList(triangle.GetPointA(), self.points)
        AddIfNotInList(triangle.GetPointB(), self.points)
        AddIfNotInList(triangle.GetPointC(), self.points)
        
    def GetTriangleVertexGenerator(self):
        for triangle in self.triangles:
            yield triangle.GetPointA().x
            yield triangle.GetPointA().y
            yield triangle.GetPointA().z
            
            yield triangle.GetPointB().x
            yield triangle.GetPointB().y
            yield triangle.GetPointB().z
            
            yield triangle.GetPointC().x
            yield triangle.GetPointC().y
            yield triangle.GetPointC().z
            
    def GetTriangleColorGenerator(self):
        for triangle in self.triangles:
            for i in range(3):
                yield triangle.GetColor().red
                yield triangle.GetColor().blue
                yield triangle.GetColor().green
                yield triangle.GetColor().alpha
            
    def GetEdgeVertexGenerator(self):
        for edge in self.edges:
            yield edge.GetStart().x
            yield edge.GetStart().y
            yield edge.GetStart().z
            
            yield edge.GetEnd().x
            yield edge.GetEnd().y
            yield edge.GetEnd().z
            
    def GetEdgeColorGenerator(self):
        for edge in self.edges:
            for i in range(2):
                yield edge.GetColor().red
                yield edge.GetColor().blue
                yield edge.GetColor().green
                yield edge.GetColor().alpha
            
