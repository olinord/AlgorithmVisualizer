'''
Created on Aug 31, 2014

@author: oli
'''
import os
import sys
import importlib

from fileUtils import AbsJoin


class AlgorithmLoadingException(Exception):
    def __init__(self, algorithmName, modulePath):
        self.algorithmName = algorithmName
        self.modulePath = modulePath

    def __str__(self):
        return "Could not import algorithm '%s' with path '%s'"%(self.algorithmName, self.modulePath)

class AlgorithmLoader(object):
    '''
    Makes algorithms from the algorithms.yaml file accessible and loadable from the main application
    '''

    def __init__(self, algorithmDefinitions):
        '''
        Initializes the AlgorithmLoader

        The algorithmDefinitions are a dictionary:
            {
                algorithmID: algorithmName
            }
        Were the algorithmID is the import statement relative to the algorithms
        directory
        '''
        self.algorithmDefinitions = algorithmDefinitions
        self.algorithms = {}

        # add the algorithms directory to the path
        curDir = os.path.dirname(os.path.realpath(__file__))
        sys.path.append(AbsJoin(curDir, "..", "..", "algorithms"))

    def GetAllAlgorithmNameAndIDs(self):
        return [(name, aID) for aID, name in self.algorithmDefinitions.iteritems()]

    def GetAlgorithmInstance(self, algorithmID):
        if algorithmID not in self.algorithms:
            algorithm = self.__CreateAlgorithm(algorithmID)
            self.algorithms[algorithmID] = algorithm
        return self.algorithms[algorithmID]

    def __CreateAlgorithm(self, algorithmID):
        try:
            exec "from %s import %s as algorithm" % tuple(algorithmID.split("."))
            return algorithm()
        except ImportError:
            raise AlgorithmLoadingException(self.algorithmDefinitions[algorithmID], algorithmID)
