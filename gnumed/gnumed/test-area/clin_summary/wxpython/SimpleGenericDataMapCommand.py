from SimpleCommand import *

class SimpleGenericDataMapCommand( Command):


	def setDataMap(self, map):
		self.dataMap = map
		print "data map = ", map
	
	def getDataMap(self):
		return self.dataMap

	def execute(self, event, id):
		listUI = event.GetEventObject()
                oldList = listUI.GetSelectedRow()
                labels =  listUI.GetLabels()
		map = {}
		for x in range(0, len(labels)):
			map[labels[x]] = oldList[x]
		map['id'] = id
		self.setDataMap(map)	 
