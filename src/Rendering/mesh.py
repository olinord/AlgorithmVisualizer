from point import Point

def AddIfNotInList(objectToBeAdded, listToAddTo):
    if objectToBeAdded not in listToAddTo:
        listToAddTo.append(objectToBeAdded)

class Mesh(object):

    def __init__(self):
        self.triangles = []
        self.edges = []
        self.points = []
        self.position = Point(0.0, 0.0, 0.0)

    def GetPosition(self):
        return self.position

    def SetPosition(self, x, y, z=0.0):
        self.position.x = x
        self.position.y = y
        self.position.z = z

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
        mx = self.position.x
        my = self.position.y
        mz = self.position.z
        for triangle in self.triangles:
            yield triangle.GetPointA().x + mx
            yield triangle.GetPointA().y + my
            yield triangle.GetPointA().z + mz

            yield triangle.GetPointB().x + mx
            yield triangle.GetPointB().y + my
            yield triangle.GetPointB().z + mz

            yield triangle.GetPointC().x + mx
            yield triangle.GetPointC().y + my
            yield triangle.GetPointC().z + mz

    def GetTriangleColorGenerator(self):
        for triangle in self.triangles:
            for i in range(3):
                yield triangle.GetColor().red
                yield triangle.GetColor().blue
                yield triangle.GetColor().green
                yield triangle.GetColor().alpha

    def GetEdgeVertexGenerator(self):
        mx = self.position.x
        my = self.position.y
        mz = self.position.z
        for edge in self.edges:
            yield edge.GetStart().x + mx
            yield edge.GetStart().y + my
            yield edge.GetStart().z + mz

            yield edge.GetEnd().x + mx
            yield edge.GetEnd().y + my
            yield edge.GetEnd().z + mz

    def GetEdgeColorGenerator(self):
        for edge in self.edges:
            for i in range(2):
                yield edge.GetColor().red
                yield edge.GetColor().blue
                yield edge.GetColor().green
                yield edge.GetColor().alpha

    def GetPointVertexGenerator(self):
        mx = self.position.x
        my = self.position.y
        mz = self.position.z
        for point in self.points:
            yield point.x + mx
            yield point.y + my
            yield point.z + mz

    def GetPointColorGenerator(self):
        for point in self.points:
            yield point.color.red
            yield point.color.blue
            yield point.color.green
            yield point.color.alpha

    def SetColor(self, color):
        for renderable in self.triangles + self.edges + self.points:
            renderable.SetColor(color)
