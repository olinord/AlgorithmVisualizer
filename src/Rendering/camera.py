'''
Created on Aug 16, 2014

@author: oli
'''
import math
from euclid import Quaternion, Vector3, Matrix4


class Camera(object):
    '''
    Defines the camera used by the Algorithm Visualizer
    '''
    MODE_PERSPECTIVE = 0
    MODE_ORTHOGONAL = 1
    def __init__(self, position, pointOfInterest, upVector, mode=MODE_ORTHOGONAL):
        '''
        Sets the camera to the position and points it in the direction of the forward vector
        '''
        self.nearPlane = 0.1
        self.farPlane = 1000.0
        self.width = 800
        self.height = 600

        self.zoomWidth = 800
        self.zoomHeight = 600

        self.viewMatrix, self.projectionMatrix = Matrix4(), Matrix4()

        self.mode = mode
        self.position = Vector3(position[0], position[1], position[2])
        self.pointOfInterest = Vector3(pointOfInterest[0], pointOfInterest[1], pointOfInterest[2])
        self.up = Vector3(upVector[0], upVector[1], upVector[2])

        self.forward = self.GenerateForward()

        self.right = self.forward.cross(self.up)

        self.distFromInterest = (self.position - self.pointOfInterest).magnitude()
        self.GenerateCameraMatrix()

    def SetProjectionInfo(self, width, height):

        self.zoomWidth = self.zoomWidth * width / self.width
        self.zoomHeight = self.zoomHeight * height / self.height

        self.width = width
        self.height = height
        if self.mode == self.MODE_PERSPECTIVE:
            self.projectionMatrix = Matrix4.new_perspective(math.pi / 2.0,
                                                    max(width, 1.0) / max(height, 1.0),
                                                    self.nearPlane, self.farPlane)
        else:
            self.SetOrthogonalInfo(self.zoomWidth, self.zoomHeight)
        self.projectionMatrix.transpose()

    def SetOrthogonalInfo(self, width, height):
        self.projectionMatrix = Matrix4()
        self.projectionMatrix.a = 2.0 / width
        self.projectionMatrix.f = 2.0 / height
        self.projectionMatrix.k = 1.0 / (self.farPlane - self.nearPlane)
        self.projectionMatrix.l = -self.nearPlane / (self.farPlane - self.nearPlane)
        self.projectionMatrix.p = 1.0

    def SetOrthogonalMode(self):
        self.__setCameraMode(self.MODE_PERSPECTIVE)
        self.position.y -= self.height * 0.5
        self.pointOfInterest = self.position
        self.pointOfInterest.z -= 10

    def SetPerspectiveMode(self):
        self.__setCameraMode(self.MODE_PERSPECTIVE)

    def __setCameraMode(self, mode):
        if self.mode == mode:
            return
        else:
            self.mode = mode
            self.SetPerspectiveInfo(self.width, self.height)

    def Focus(self, minX, maxX, minY, maxY):
        if self.mode == self.MODE_ORTHOGONAL:
            width = maxX - minX
            height = maxY - minY

            if width > self.width:
                aspect = self.width / self.height
                self.width = width
                self.height = self.width / aspect
            elif height > self.height:
                aspect = self.width / self.height
                self.height = height
                self.width = aspect / self.height

            self.zoomWidth = self.width
            self.zoomHeight = self.height
            self.SetOrthogonalInfo(self.width, self.height)
            self.position.x = self.width * 0.5
            self.position.y = self.height * 0.5
            self.pointOfInterest.x = self.position.x
            self.pointOfInterest.y = self.position.y
            self.GenerateCameraMatrix()

    def GenerateCameraMatrix(self):
        self.forward = self.GenerateForward()
        self.right = self.up.cross(self.forward).normalized()
        self.up = self.forward.cross(self.right).normalized()

        self.position = self.forward * (-self.distFromInterest)

        self.matrix = Matrix4()
        self.matrix.a, self.matrix.e, self.matrix.i = self.right.x, self.right.y, self.right.z
        self.matrix.b, self.matrix.f, self.matrix.j = self.up.x, self.up.y, self.up.z
        self.matrix.c, self.matrix.g, self.matrix.k = self.forward.x, self.forward.y, self.forward.z
        self.matrix.m, self.matrix.n, self.matrix.o = self.right.dot(self.position), self.up.dot(self.position), self.forward.dot(self.position)

    def GenerateForward(self):
        return (self.pointOfInterest - self.position).normalized()

    def GenerateRightVector(self):
        return self.up.cross(self.forward).normalized()

    def Zoom(self, delta):
        if self.mode == self.MODE_PERSPECTIVE:
            self.distFromInterest -= delta
            self.GenerateCameraMatrix()
        else:
            direction = delta / abs(delta)
            self.zoomWidth += 5.0 * direction
            self.zoomHeight += 5.0 * direction
            self.SetOrthogonalInfo(self.zoomWidth, self.zoomHeight)

    def MouseMotion(self, deltaX, deltaY):
        if self.mode == self.MODE_ORTHOGONAL:
            return
        sideMovement = self.right * 0.05 * deltaX
        upMovement = self.up * 0.05 * deltaY

        self.position += sideMovement
        self.GenerateCameraMatrix()
        self.position -= upMovement
        self.GenerateCameraMatrix()
