'''
Created on Aug 16, 2014

@author: oli
'''
import unittest
import euclid
from Rendering.camera import Camera


class CameraTest(unittest.TestCase):


    def testGeneratedForward_IsCorrectAfterInitialization(self):
        camera = Camera([0.0, 0.0, 1.0], [0.0, 0.0, 0.0], [0.0, 1.0, 0.0])
        self.assertEqual([0.0, 0.0, -1.0], camera.GenerateForward())
        
        
    def testGeneratedRightVector_IsCorrectAfterInitialization(self):
        camera = Camera([0.0, 0.0, 1.0], [0.0, 0.0, 0.0], [0.0, 1.0, 0.0])
        self.assertEqual([-1.0, 0.0, 0.0], camera.GenerateRightVector())   
        
    def testPositionIsUnchangedAfterInitialization(self):
        position = [0.0, 0.0, 1.0]
        camera = Camera(position, [0.0, 0.0, 0.0], [0.0, 1.0, 0.0])
        self.assertEqual(euclid.Vector3(position[0], position[1], position[2]), camera.position)
                
    def testRightVectorIsUnchangedAfterMouseMovementInYDirection(self):
        camera = Camera([0.0, 0.0, 1.0], [0.0, 0.0, 0.0], [0.0, 1.0, 0.0])
        right = camera.right
        camera.MouseMotion(0.0, 1.0)
        self.assertEqual(right, camera.right)

    def testUpVectorIsUnchangedAfterMouseMovementInYDirection(self):
        camera = Camera([0.0, 0.0, 1.0], [0.0, 0.0, 0.0], [0.0, 1.0, 0.0])
        up = camera.up
        camera.MouseMotion(1.0, 0.0)
        self.assertEqual(up, camera.up)


if __name__ == "__main__":
    unittest.main()
