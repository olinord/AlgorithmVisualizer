'''
Created on Aug 10, 2014

@author: oli
'''
import unittest

from Rendering.edge import Edge
from Rendering.mesh import Mesh
from Rendering.point import Point
from Rendering.triangle import Triangle


class TestMesh(unittest.TestCase):


    def setUp(self):
        self.mesh = Mesh()


    def tearDown(self):
        pass


    def test_whenMeshIsInitialized_itContainsNoTrianglesEdgesOrPoints(self):
        self.assertListEqual(self.mesh.GetTriangles(), [], "Newly initialized mesh contains some triangles")
        self.assertListEqual(self.mesh.GetEdges(), [], "Newly initialized mesh contains some edges")
        self.assertListEqual(self.mesh.GetPoints(), [], "Newly initialized mesh contains some points")
            
    def test_whenTriangleIsAddedToMesh_edgesAndPointsAreAutomaticallyAdded(self):
        p0 = Point(0.0, 0.0, 0.0)
        p1 = Point(1.0, 0.0, 0.0)
        p2 = Point(0.0, 1.0, 0.0)
        
        t = Triangle(p0, p1, p2)
        self.mesh.AddTriangle(t)
        
        self.assertIn(t, self.mesh.GetTriangles(), "Newly added triangle is not contained in the mesh")
        
        self.assertIn(t.GetEdgeAB(), self.mesh.GetEdges(), "Newly added triangle edge is not contained in the mesh")
        self.assertIn(t.GetEdgeBC(), self.mesh.GetEdges(), "Newly added triangle edge is not contained in the mesh")
        self.assertIn(t.GetEdgeCA(), self.mesh.GetEdges(), "Newly added triangle edge is not contained in the mesh")
        
        self.assertIn(p0, self.mesh.GetPoints(), "Newly added triangle point is not contained in the mesh")
        self.assertIn(p1, self.mesh.GetPoints(), "Newly added triangle point is not contained in the mesh")
        self.assertIn(p2, self.mesh.GetPoints(), "Newly added triangle point is not contained in the mesh")
        
    def test_whenTriangleIsAddedToMesh_edgesAndPointsAlreadnMeshAreNotAdded(self):
        p0 = Point(0.0, 0.0, 0.0)
        p1 = Point(1.0, 0.0, 0.0)
        p2 = Point(0.0, 1.0, 0.0)
        p3 = Point(0.0, 0.0, 1.0)
        
        t = Triangle(p0, p1, p2)        
        t2 = Triangle(p1, p2, p3)
        self.mesh.AddTriangle(t)
        self.mesh.AddTriangle(t2)
                
        self.assertEqual(len(self.mesh.GetTriangles()), 2, "There should be 2 triangles in the mesh, there are %d triangles" % len(self.mesh.GetTriangles()))        
        self.assertEqual(len(self.mesh.GetEdges()), 5, "There should be 5 edges in the mesh, there are %d edges" % len(self.mesh.GetEdges()))                
        self.assertEqual(len(self.mesh.GetPoints()), 4, "There should be 4 points in the mesh, there are %d points" % len(self.mesh.GetPoints()))
        
    def test_BoundingBoxIsCalculatedCorrectlyForMesh(self):
        p0 = Point(0.0, 1.0, 0.0)
        p1 = Point(1.0, 0.0, 0.0)
        p2 = Point(1.0, 0.0, 1.0)
        p3 = Point(0.0, 0.0, 1.0)
        
        t = Triangle(p0, p1, p2)        
        t2 = Triangle(p1, p2, p3)
        self.mesh.AddTriangle(t)
        self.mesh.AddTriangle(t2)
        
        expectedBoundingBox = [ Point(x, y, z) for x in [0, 1] for y in [0, 1] for z in [0, 1] ]
        calculatedBoundingBox = self.mesh.GetBoundingBox()
        
        for p in expectedBoundingBox:
            self.assertIn(p, calculatedBoundingBox)
        for p in calculatedBoundingBox:
            self.assertIn(p, expectedBoundingBox)
        
        
if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
