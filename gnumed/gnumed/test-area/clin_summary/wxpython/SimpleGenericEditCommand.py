from SimpleChainedCommand import *
import SimpleRecordPanel 
from SimpleFactoryOwner import *
from SimpleDefaultNameMapper import *
from SimpleGenericDataMapCommand import *

# this command maps the selected table row to a map with the db field names as keys
# then uses the map to set the 'value' entry of a list of entries ('name','size','value')
# then passes this to SimpleRecordPanel for user interaction (no validation)
# any changes to the values in the entries are returned in a map of ui names - value.
# this is then passed to a storage command, which is configured in SimpleDefaultCommandMap
# to be SimpleEditPersonStoreCommand
# after this, the gmSelectDialog is refreshed to update the list view ( unnecessary if
# there are intermediate objects being displayed , but for now, gmSQLSimpleSearch will
# display database results directy ).

class SimpleGenericEditCommand(SimpleGenericDataMapCommand, SimpleChainedCommand,  SimpleFactoryOwner):

	def __init__(self, list = [] , mapper = SimpleDefaultNameMapper()):
		self.fieldList = list
		self.mapper = mapper

	def execute( self, event, id):
		SimpleGenericDataMapCommand.execute(self,event,id)
			
		print "SimpleEditPersonCommand found ", self.getDataMap() 
		uiAndValueList = self.mapper.createSimpleDialogData( self.fieldList, self.getDataMap())
		"*** before ", self.getDataMap()
		dataMap  = SimpleRecordPanel.doSimpleDialog( event.GetEventObject(), uiAndValueList, factory = self.getFactory() )
		dataMap['id'] = id
		dataMap['clin_id'] = self.getDataMap()['clin_id']
                print" *** after , data = ", dataMap
                self.data = dataMap
		SimpleChainedCommand.execute(self,  event, dataMap)

