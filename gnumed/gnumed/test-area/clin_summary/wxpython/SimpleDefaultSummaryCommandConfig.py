
from SimpleSummaryMap import *
from SimpleSummaryUI import *
from SimpleGenericNewCommand import *
from SimpleGenericEditCommand import *
from SimpleRecordPanel import *
from SimpleHorizontalDialogFactory import *
from SimpleListCtrlRefreshCommand import *
from SimpleGenericMultiCommand import *
from SimpleGenericDeleteCommand import *
class DefaultSummaryCommandConfig:

	def configure(self, summaryUI ):
		mapper = SimpleSummaryMap()

		map = mapper.getMap()  # this map contains a list of fields for each part of the patient history
		scripts = mapper.getScriptMap() # this map contains the sql query for the view per patient id

		print map
		
		#print "****ph=", map['phx']

		cmdMap = {}
		for x in map.keys():
			cmdMap[x] = {}
			cmdMap[x]["new"] = SimpleGenericNewCommand( map[x] )
                	cmdMap[x]["new"].setFactory( SimpleHorizontalDialogFactory() )
			cmdMap[x]["edit"] = SimpleGenericEditCommand( map[x] )
                	cmdMap[x]["edit"].setFactory( SimpleHorizontalDialogFactory() )
			cmdMap[x]["delete"] = SimpleGenericDeleteCommand( map[x] )
			cmdMap[x]["new"].setNextCommand( SimpleGenericMultiCommand(map[x], x, "insert", mapper))
			cmdMap[x]["edit"].setNextCommand( SimpleGenericMultiCommand(map[x], x, "edit", mapper) )
			cmdMap[x]["delete"].setNextCommand( SimpleGenericMultiCommand(map[x], x, "delete", mapper) )


		for x in scripts.keys():
			cmdMap[x]["refresh"] = SimpleListCtrlRefreshCommand( scripts[x] )

		summaryUI.setCommandMap( cmdMap)
		
