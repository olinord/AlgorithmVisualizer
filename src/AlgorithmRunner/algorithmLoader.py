'''
Created on Aug 31, 2014

@author: oli
'''
import os
import sys
import importlib

from fileUtils import AbsJoin
from algorithmConst import VALID_ALGORITHM_VALUE_TYPES, VALID_ALGORITHM_RENDER_TYPES

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
            algorithmName:
            {
                code_path: algorithm import statement relative to the algorithms directory
                value_type: one of (value_sorting, 2d_render, 3d_render)
                render_types: any of [triangles, lines, points]
            }
        }
        '''
        self.algorithmDefinitions = algorithmDefinitions
        self.algorithms = {}
        self.validateAlgorithms()

        # add the algorithms directory to the path
        curDir = os.path.dirname(os.path.realpath(__file__))
        sys.path.append(AbsJoin(curDir, "..", "..", "algorithms"))

    def validateAlgorithms(self):
        for algorithmName, algorithmDefinition in self.algorithmDefinitions.iteritems():
            valueType = algorithmDefinition.get("value_type", None)
            if valueType not in VALID_ALGORITHM_VALUE_TYPES:
                raise RuntimeError("Algorithm '%s' has incorrect 'value_type' value '%s', should be one of %s" % (algorithmName, valueType, VALID_ALGORITHM_VALUE_TYPES))
            renderTypes = algorithmDefinition.get("render_types", None)
            if isinstance(renderTypes, list):
                for renderType in renderTypes:
                    if renderType not in VALID_ALGORITHM_RENDER_TYPES:
                        raise RuntimeError("Algorithm '%s' has incorrect 'render_types' value '%s', should one of %s" % (algorithmName, renderType, VALID_ALGORITHM_RENDER_TYPES))
            else:
                if renderTypes is None:
                    raise RuntimeError("Algorithm '%s' has no 'render_types' specified, should be a variation of %s" % (algorithmName, VALID_ALGORITHM_RENDER_TYPES))
                else:
                    raise RuntimeError("Algorithm '%s' has an incorrect type for 'render_types' it is '%s', should be a list" % (algorithmName, type(renderTypes)))

    def GetAllAlgorithmNames(self):
        return [name for name in self.algorithmDefinitions.keys()]

    def GetAlgorithmValueType(self, algorithmName):
        return self.algorithmDefinitions[algorithmName]["value_type"]

    def GetAlgorithmRenderTypes(self, algorithmName):
        return self.algorithmDefinitions[algorithmName]["render_types"]

    def GetAlgorithmInstance(self, algorithmName):
        return self.__CreateAlgorithm(algorithmName)

    def __CreateAlgorithm(self, algorithmName):
        algorithm = self.algorithmDefinitions[algorithmName]
        code_path = algorithm["code_path"]
        try:
            exec "from %s import %s as algorithm" % tuple(code_path.split("."))
            return algorithm()
        except ImportError:
            raise AlgorithmLoadingException(algorithmName, code_path)
