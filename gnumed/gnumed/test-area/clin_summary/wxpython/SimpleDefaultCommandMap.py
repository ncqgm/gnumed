from SimpleNewPersonCommand import *
from SimpleNewPersonStoreCommand import *
from SimpleSearchPersonCommand import *
#from SimpleSearchPersonImplCommand import *

from SimpleEditPersonCommand import *
from SimpleEditPersonStoreCommand import *
from SimpleEnterNotesCommand import *
from SimplePersonViewMapper import *
from SimplePersonView2Map import *
import gmGuiBroker
class SimpleDefaultCommandMap:


	def __init__(self):
		self.map = {}
		mapper = SimplePersonViewMapper()
		if mapper.getMapping() == None:
			mapper.setMapping(SimplePersonView2Map())

	def setParent(self, parentUI):
		self.parentUI = parentUI
	
	def getMap(self):
	#configurating for notebook
	 	self.guibroker = gmGuiBroker.GuiBroker()
		self.notebook = None

		try:
			self.notebook = self.guibroker['main.notebook']
			print "main.notebook = ", self.notebook	
		except Exception ,errorstr:
			print "exception in guibroker", errorstr

		try:
			
			self.map["selectPerson"] = self.getEnterNotesCommand()
			self.map["newPerson"] = self.getNewPersonCommand() 

			self.map["searchPerson"] = self.getSearchPersonCommand()
	
			self.map["editPerson"] = self.getEditPersonCommand()
			
			self.map["enterNotes"] = self.getEnterNotesCommand()
		except Exception , errormsg:
			print errormsg	

		return self.map

	def getNewPersonCommand(self):
        	command = NewPersonCommand()
                try:
                        command.setNextCommand( NewPersonStoreCommand())
                except Exception ,errormsg:
                        print errormsg
                print "command = ", command
                return command

	def getSearchPersonCommand(self):
		command =  SimpleSearchPersonCommand()
	#	command.setNextCommand( SimpleSearchPersonImplCommand())

		return command

	def getEditPersonCommand(self):
		command = SimpleEditPersonCommand()
		command.setNextCommand( SimpleEditPersonStoreCommand())
		return command

	def getEnterNotesCommand(self):
		print "**** ENTER NOTES GETS ",self.notebook
		command = SimpleEnterNotesCommand(self.notebook)
		return command

