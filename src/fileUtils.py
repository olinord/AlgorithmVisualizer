
import os
import yaml

def AbsJoin(*path):
    return os.path.abspath( os.path.join( *path ) )

def LoadYamlFromRoot(yamlFilePathFromRoot):
	with open(AbsJoin(APP_ROOT, yamlFilePathFromRoot)) as yamlFile:
		return yaml.load(yamlFile)


APP_ROOT = AbsJoin( os.path.dirname( __file__ ), "..")
