from  SimpleCommand import * 
from SimpleDefaultSummaryCommandConfig import *
from SimplePersonViewMapper import *

class SimpleEnterNotesCommand(Command):

	
	def 	__init__(self, notebook = None):
		self.notebook = notebook
		if notebook != None:
			self.win = self.createSummaryUI(notebook)
			self.index = -1
			
	
	def createSummaryUI( self, parent, personData = None):
			if personData ==None:
				personData = SimplePersonViewMapper().getMapping().getBlankData()
			print "creating SUMMARY panel with ", personData
		        win =  ClinNotesPanel( parent, personData)
                        DefaultSummaryCommandConfig().configure(win)
                        return win
		
			
	def execute( self, event, gmSelectPerson):
		personData = gmSelectPerson.GetSelectedList()
		if self.notebook == None:
			frame = wxFrame( None, -1, "Test Summary Sheet", size = (610, 600) )
			self.createSummaryUI(frame , personData )
			frame.Show()
		else:
			if self.index == -1:
				self.index = self.notebook.GetPageCount()
				self.notebook.AddPage(self.win, "Clinical Summary")	
			try:
				self.win.setPersonDetails( personData)
			except Exception, errorStr:
				print "in SimpleEnterNotes call to setPersonDetails", errorStr
			self.notebook.SetSelection(self.index)	
	
			
