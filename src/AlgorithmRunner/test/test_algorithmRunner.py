import time
import unittest

from AlgorithmRunner.algorithmInterface import Algorithm
from AlgorithmRunner.algorithmRunner import AlgorithmRunner
from AlgorithmRunner.algorithmRunner import NotAnAlgorithmException
AlgorithmRunnerfrom . import StepCountingAlgorithm


class AlgorithmWithoutEndCondition(Algorithm):
    pass                
         

class AlgorithmWithoutStep(Algorithm):
    def endCondition(self):
        return False
    
class AlgorthmWithSleep(StepCountingAlgorithm):
    def step(self):
        StepCountingAlgorithm.step(self)
        time.sleep(0.05)
       

class AlgorithmVisualizerUnitTest(unittest.TestCase):

    def setUp(self):
        self.algorithmRunner = AlgorithmRunner()
        
    def runAlgorithmUntilEnd(self):
        while self.algorithmRunner.isRunning():
            pass
    
    def test_SettingAnAlgorithmThatIsNotAnAlgorithmType_RaisesAnException(self):
        algorithm = "fake algorithm"
        with self.assertRaises(NotAnAlgorithmException) as e:
            self.algorithmRunner.SetAlgorithm(algorithm)
        
        self.assertEquals(str(e.exception), "<type 'str'>: is not an algorithm")
        
    def test_SettingAnAlgorithmThatIsAnAlgorithmType_DoesNotRaiseAnException(self):
        self.algorithmRunner.SetAlgorithm(StepCountingAlgorithm(10))
        
    def test_AlgorithmMustDefineAnEndConditionFunction(self):
        invalidAlgorithm = AlgorithmWithoutEndCondition()
        self.algorithmRunner.SetAlgorithm(invalidAlgorithm)
        
        self.algorithmRunner.run()        
        self.runAlgorithmUntilEnd()
        
        algorithmException = self.algorithmRunner.getThreadException()
        self.assertEqual(str(algorithmException), "%s: does not implement the 'endCondition' function" % type(invalidAlgorithm))
    
    def test_AlgorithmMustDefineAnStepFunction(self):
        
        invalidAlgorithm = AlgorithmWithoutStep()
        self.algorithmRunner.SetAlgorithm(invalidAlgorithm)
        
        self.algorithmRunner.run()        
        self.runAlgorithmUntilEnd()
        
        algorithmException = self.algorithmRunner.getThreadException()
        self.assertEqual(str(algorithmException), "%s: does not implement the 'step' function" % type(invalidAlgorithm))
    
    def test_AlgorithmCanBeRunUntilEndConditionIsMet(self):
        stepCount = 10
        algorithm = StepCountingAlgorithm(stepCount) 
        self.algorithmRunner.SetAlgorithm(algorithm)
        
        self.algorithmRunner.run()
        self.runAlgorithmUntilEnd()
        
        self.assertEqual(algorithm.currentStep, stepCount)
    
    def test_AlgorithmCanBeStepped(self):
        stepCount = 10
        algorithm = StepCountingAlgorithm(stepCount) 
        self.algorithmRunner.SetAlgorithm(algorithm)
        
        self.algorithmRunner.step()
        
        self.assertEqual(algorithm.currentStep, 1)
    
    def test_AlgorithmCanBeStoppedWhileItIsRunning(self):
        stepCount = 10000
        algorithm = AlgorthmWithSleep(stepCount)
        
        self.algorithmRunner.SetAlgorithm(algorithm)
        
        self.algorithmRunner.run()
        self.algorithmRunner.stop()
        
        self.assertNotEqual(algorithm.currentStep, stepCount)


if __name__ == '__main__':
    unittest.main()
