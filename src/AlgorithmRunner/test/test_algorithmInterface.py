from unittest import TestCase

from . import StepCountingAlgorithm


class AlgorithmVisualizerUnitTest(TestCase):
        
    def test_algorithmStepContextSetsTheContextInsideTheContextManager(self):
        algorithm = StepCountingAlgorithm(10)
        with algorithm.stepContext("testContext"):
            self.assertEqual("testContext", algorithm.context)
        self.assertEqual("", algorithm.context)
        
        