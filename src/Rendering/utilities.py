'''
Created on Aug 10, 2014

    Defines a few utility method to draw common shapes

@author: oli
'''

from mesh import Mesh
from point import Point
from triangle import Triangle
from color import COLOR_WHITE


def UnitCube(size=1.0):
    halfSize = size / 2.0

    minMaxCoordinates = [-halfSize, halfSize]

    mesh = Mesh()

    points = [ Point(x, y, z) for z in minMaxCoordinates for y in minMaxCoordinates for x in minMaxCoordinates ]

    # Front
    mesh.AddTriangle(Triangle(points[0], points[2], points[1]))
    mesh.AddTriangle(Triangle(points[1], points[2], points[3]))

    # Back
    mesh.AddTriangle(Triangle(points[5], points[4], points[7]))
    mesh.AddTriangle(Triangle(points[7], points[4], points[6]))

    # Right
    mesh.AddTriangle(Triangle(points[4], points[0], points[6]))
    mesh.AddTriangle(Triangle(points[6], points[0], points[2]))

    # Left
    mesh.AddTriangle(Triangle(points[1], points[5], points[3]))
    mesh.AddTriangle(Triangle(points[3], points[5], points[7]))

    # Top
    mesh.AddTriangle(Triangle(points[4], points[5], points[0]))
    mesh.AddTriangle(Triangle(points[0], points[5], points[1]))

    # Bottom
    mesh.AddTriangle(Triangle(points[2], points[3], points[6]))
    mesh.AddTriangle(Triangle(points[6], points[3], points[7]))

    return mesh

def GenerateRectangle(width, height, color=COLOR_WHITE):
    points = [ Point(x, y) for x in (0, width) for y in (0, height) ]

    mesh = Mesh()
    mesh.AddTriangle(Triangle(points[0], points[2], points[1], color))
    mesh.AddTriangle(Triangle(points[1], points[2], points[3], color))

    return mesh
