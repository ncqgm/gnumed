import SimpleRecordPanel
from SimpleChainedCommand import *
from SimplePersonViewMapper import *
class NewPersonCommand(SimpleChainedCommand):



	def getFieldList(self):
		
		list = [	
			 { "name":"first name" },
			{ "name":"last name" },
			{ "name":"birthdate" },
			{ "name":"sex" },
			{ "name":"address 1", "size": 150 },
			{ "name":"address 2", "size": 150 },
			{ "name":"phone ah", "size": 100 },
			{ "name":"phone bh" , "size": 100 },
			{ "name":"medicare no" }
			]

		print "*** before ", list 
		return SimplePersonViewMapper().getMapping().getEntries()
			
	#	return list 

	def execute( self, src, frame):

		list = self.getFieldList()
		
		dataList  = SimpleRecordPanel.doSimpleDialog( frame, list)

		print" *** after , dataList = ", dataList 

		self.data = dataList	
		
		SimpleChainedCommand.execute(self, src, self.data)	

if __name__ == "__main__":

	pass

	

