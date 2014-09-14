'''
Created on Aug 31, 2014

@author: oli
'''


class AlgorithmLoader(object):
    '''
    Makes algorithms from the algorithms.yaml file accessible and loadable from the main application
    '''

    def __init__(self, algorithmDefinitions):
        '''
        Initializes the AlgorithmLoader
        '''
        self.algorithmDefinitions = algorithmDefinitions
        self.algorithms = {}

        for algorithmID, algorithmDefinition in self.algorithmDefinitions.iteritems():
            self.SetupAlgorithm(algorithmID, algorithmDefinition)

    def SetupAlgorithm(self, algorithmID, algorithmDefinition):
        self.algorithms[algorithmID] = algorithmDefinition