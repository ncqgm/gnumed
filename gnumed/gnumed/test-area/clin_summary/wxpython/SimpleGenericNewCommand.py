import SimpleRecordPanel
from SimpleChainedCommand import *
from SimpleFactoryOwner import *
from SimpleRecordPanel import SimpleEntryException
from SimpleListOwner import *
class SimpleGenericNewCommand(SimpleChainedCommand, SimpleListOwner, SimpleFactoryOwner ):

	def __init__(self, list ):
		self.nameList = list	
	def execute( self, event, id):
		for x in range (1, 10):
			try:
				
				dataList  = SimpleRecordPanel.doSimpleDialog( event.GetEventObject(), self.nameList, factory = self.getFactory() )
				dataList['id'] = id
				print" *** after , dataList = ", dataList 

				self.data = dataList	
				
				SimpleChainedCommand.execute(self, event, self.data)	
				return 

			except SimpleEntryException:
				print "entry cancelled"
				return
	
			
			
					
			

if __name__ == "__main__":

	pass

	

