'''
Created on Aug 16, 2014

@author: oli
'''

from euclid import Quaternion, Vector3, Matrix4


class Camera(object):
    '''
    Defines the camera used by the Algorithm Visualizer
    '''

    def __init__(self, position, pointOfInterest, upVector):
        '''
        Sets the camera to the position and points it in the direction of the forward vector
        '''
        
        self.position = Vector3(position[0], position[1], position[2])
        self.pointOfInterest = Vector3(pointOfInterest[0], pointOfInterest[1], pointOfInterest[2])
        self.up = Vector3(upVector[0], upVector[1], upVector[2])
        
        self.forward = self.GenerateForward()
        
        self.right = self.forward.cross(self.up)
        
        self.distFromInterest = (self.position - self.pointOfInterest).magnitude()
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
        self.distFromInterest -= delta
        self.GenerateCameraMatrix()
        
    def MouseMotion(self, deltaX, deltaY):
        
        self.position += self.right * 0.05 * deltaX
        self.GenerateCameraMatrix()
        self.position -= self.up * 0.05 * deltaY 
        self.GenerateCameraMatrix()
        