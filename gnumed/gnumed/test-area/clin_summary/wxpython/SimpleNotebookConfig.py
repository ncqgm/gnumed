from SimpleSelectPersonDialogFactory import *

class NBConfig:
	config = None
	def __init__(self, config = None):
		NBConfig.config =config 
	
	def getConfig(self):

		if NBConfig.config == None:
			NBConfig.config = DefaultNBConfig()
		return NBConfig.config
	
class DefaultNBConfig:
	def __init__(self):
		pass
	
	def getFactoryMap(self):
		self.map = {}
		self.map['selectPersonDialogFactory'] = SelectPersonTestFactory()
		return self.map


def getConfig():
	try:
		if nb_config != None:
			return nb_config

	except Exception, errormsg:
		print errormsg 
	
	nb_config = DefaultNBConfig()
	
	return nb_config
		
