from SimpleChainedCommand import *
from SimplePersonViewMapper import *
import SimpleRecordPanel 

# this command maps the selected table row to a map with the db field names as keys
# then uses the map to set the 'value' entry of a list of entries ('name','size','value')
# then passes this to SimpleRecordPanel for user interaction (no validation)
# any changes to the values in the entries are returned in a map of ui names - value.
# this is then passed to a storage command, which is configured in SimpleDefaultCommandMap
# to be SimpleEditPersonStoreCommand
# after this, the gmSelectDialog is refreshed to update the list view ( unnecessary if
# there are intermediate objects being displayed , but for now, gmSQLSimpleSearch will
# display database results directy ).

class SimpleEditPersonCommand(SimpleChainedCommand):

	def execute( self, event , params):

		selectPersonDialog = event.GetEventObject() 

		mapper = SimplePersonViewMapper().getMapping()

		oldList = selectPersonDialog.GetSelectedRow()
		labels =  selectPersonDialog.GetLabels()
		oldData = {}
		print "old list and labels = ", oldList, labels
		for i in range(0,len(labels)):
			oldData[labels[i]] = oldList[i]
		print "old map = ", oldData
			
		
		print "SimpleEditPersonCommand found ", oldData 
		uiList = []
		entries = mapper.getEntries()	
		
		for x  in entries :
			name = x['name'] 
			entry = {'name': name }
			try:
				size = x['size'] 
				entry['size'] = size
			except:
				print 'no size for ', name
				pass
			try:
				entry['value'] = oldData[x['dbname']]
			except:
				print 'no value for ', name, 'has dbname ', x['dbname']
				pass

			uiList.append(entry)
				
		print "before", uiList				
		dataList  = SimpleRecordPanel.doSimpleDialog( selectPersonDialog, uiList)

	# map back to db field names		
		dataList = mapper.mapKeysToFieldNames( dataList)

                print" *** after , dataList = ", dataList

                self.data = dataList
		SimpleChainedCommand.execute(self,  oldData, dataList)
		selectPersonDialog.updateList()

			
		
		
		

				
	

