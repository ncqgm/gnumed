from SimpleGenericDataMapCommand import *
from SimpleDefaultNameMapper import *
from SimpleChainedCommand import *
from SimpleSummaryMap import *
from wxPython.wx import *

class SimpleGenericDeleteCommand( SimpleGenericDataMapCommand, SimpleChainedCommand ):

	def __init__(self, list  ,  mapper = SimpleDefaultNameMapper() ):  
		
		self.nameList = list
		self.mapper = mapper
	def execute ( self, event, id):
		if  wxMessageDialog( event.GetEventObject(), "Are you sure you want to delete this record ?", "CONFIRMATION",
					style = wxYES_NO).ShowModal() != wxID_YES : 
			return
		SimpleGenericDataMapCommand.execute(self, event, id)
		dialogNameMap = self.mapper.mapKeysToDialogNames( self.getDataMap(), self.nameList)
		dialogNameMap['id'] = id
                dialogNameMap['clin_id'] = self.getDataMap()['clin_id']

		SimpleChainedCommand.execute( self, event, dialogNameMap)
		event.GetEventObject().update()			
		
		
