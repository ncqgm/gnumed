

class SimplePersonViewMapper:
	mapping = None
	def __init__(self, mapping = None ):
		if mapping != None:
			setMapping(mapping)

	def setMapping( self, mapping):
		SimplePersonViewMapper.mapping = mapping

	def getMapping(self):
		return SimplePersonViewMapper.mapping
