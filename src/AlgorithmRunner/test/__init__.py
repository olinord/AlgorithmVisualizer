from AlgorithmRunner.algorithmInterface import Algorithm

class StepCountingAlgorithm(Algorithm):
    
    def __init__(self, stepCount):
        Algorithm.__init__(self)
        self.stepCount = stepCount
        self.currentStep = 0
    
    def step(self):
        self.currentStep += 1
        
    def endCondition(self):
        return self.currentStep == self.stepCount