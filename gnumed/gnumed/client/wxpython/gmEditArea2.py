

from wxPython.wx import *


TBx = 1
CHBx = 2
RBn = 3
CMBx =4
LAB = 5



class EditArea2(wxPanel):
	"""A no frills version for prototyping and programming more easily.
	"""

	def __init__(self, parent, id):
		wxPanel.__init__(self, parent, id, wxDefaultPosition, wxDefaultSize, style = wxNO_BORDER | wxTAB_TRAVERSAL)

		self.topSizer = wxFlexGridSizer(0, 1,0,0)
		self.topSizer. AddGrowableCol(0)
		self.lineSizer = wxBoxSizer(wxHORIZONTAL)
		self.nextId = 1
		self.rowItems = 0
		self.widgets= {}
	
	def add(self, propName,  type=TBx ,weight=1,  displayName = None,  newline = 0):
		""" sets the default display Name to the property name,
		    capitalizes the display name,
		    creates the widget of the selected type, the default 
		    widget is a textbox,
		    adds the widget at the given weight, adjust if last
		    widget on line ( does this really do anything?),
		    add the line to the sizer if a newline and 
		    start a newline.
		    """

		if displayName == None:
			displayName = propName.capitalize()
			
			
		label = None
		if type == TBx:
			label =  wxStaticText(self, -1, displayName)
			widget = wxTextCtrl(self, -1 )

		if type == RBn:
			widget = wxRadioButton(self, -1, displayName)
		
		if type == CHBx:
			widget = wxCheckBox(self, -1, displayName)
			
		if type == CMBx:
			label= wxStaticText(self, -1, displayName)
			widget = wxComboBox(self, -1)
		
		if type == LAB:
			widget = wxStaticText(self, -1, displayName)

		if label <> None:
			self.lineSizer.Add(label, 1, flag=wxALIGN_RIGHT)
		if newline and self.rowItems == 0:
			aproportion = 4
			aflag = wxEXPAND
		else:
			aproportion = weight 
			aflag =  wxALIGN_LEFT
		self.lineSizer.Add(widget, aproportion, aflag)
		self.rowItems += 1
		
		self.widgets[propName] = widget

		if newline:
			self.topSizer.Add(self.lineSizer, flag= wxEXPAND)
			self.lineSizer = wxBoxSizer(wxHORIZONTAL)
			self.rowItems =0
			
	def finish(self):
		self.topSizer.Add(self.lineSizer, wxEXPAND)
		self.SetSizer(self.topSizer)
		self.topSizer.Fit(self)
		self.SetAutoLayout(true)

	def getWidgetByName(name):
		"""yes, you can get back the widget by name !!(duh, but what do I do with it?)"""
		if not self.widgets.has_key(name):
			return None
		return self.widgets[name]
		

class MedicationEditArea(EditArea2):
	
	def __init__(self, parent, id):
		EditArea2.__init__(self, parent, id)
		self.add("classes", newline = 1)
		self.add("generic", weight = 3)
		self.add("veteran", CHBx,newline=1)
		self.add("drug", weight = 3)
		self.add("reg 24", CHBx, newline=1)
		self.add("strength", weight = 2)
		self.add("quantity",  newline=1)
		self.add("direction", weight = 2)
		self.add("repeats",  newline=1)
		self.add("for", weight = 3)
		self.add("usual", CHBx, newline=1)
		self.add("progress notes", weight = 6)
		self.finish()


class PastHistoryEditArea(EditArea2):
	def __init__(self, parent, id):
		EditArea2.__init__(self, parent, id)
		self.add("condition" )
		self.add("left",  RBn)
		self.add("right", RBn)
		self.add("both",  RBn, newline = 1)
		self.add("notes",  newline = 1)
		self.add("age onset" )
		self.add("year onset",  newline = 1)
		self.add("active", CHBx)
		self.add("operation", CHBx)
		self.add("confidential", CHBx)
		self.add("significant", CHBx)
		self.finish()


class RecallEditArea(EditArea2):
	def __init__(self, parent, id):
		EditArea2.__init__(self, parent, id)
		self.add("to see", newline = 1)
		self.add("recall for", newline =1 )
		self.add("date", newline = 1)
		self.add("contact by", CMBx, weight=1)
		self.add("appointment type", newline = 1, weight = 2)
		self.add("include", CMBx , weight = 1)
		self.add("for", newline=1, weight = 2)
		self.add("instructions", newline = 1)
		self.add("progress notes", newline = 1)
		self.finish()
		
class ReferralEditArea(EditArea2):
	def __init__(self, parent, id):
		EditArea2.__init__(self, parent, id)
		self.add("Pers Category", newline = 1)
		self.add("name", weight = 3)
		self.add("use firstname", CHBx, newline=1)
		self.add("organization", weight = 3)
		self.add("head office", CHBx, newline = 1)
		self.add("street1", weight=2)
		self.add("w phone", newline = 1)
		self.add("street2", weight=2)
		self.add("w fax", newline=1)
		self.add("street3", weight=2)
		self.add("w email", newline=1)
		self.add("suburb", weight=2)
		self.add("postcode", newline=1)
		self.add("for", newline=1)
		self.add("include", LAB)
		self.add("medications", CHBx)
		self.add("social history", CHBx)
		self.add("family history", CHBx, newline = 1)
		self.add("", LAB)
		self.add("past problems", CHBx)
		self.add("active problems", CHBx)
		self.add("habits", CHBx, newline = 1)
		self.finish()
		

class RequestEditArea(EditArea2):
	def __init__(self, parent, id):
		EditArea2.__init__(self, parent, id)
		self.add("type", newline =1 )
		self.add("company", newline = 1)
		self.add("street", newline = 1)
		self.add("suburb", weight = 2)
		self.add("phone", weight = 2,newline = 1)
		self.add("request", newline = 1)
		self.add("notes on form", newline = 1)
		self.add("medications", weight=3)
		self.add("include all meds", CHBx, newline = 1)
		self.add("copy to", newline = 1)
		self.add("progress notes", newline = 1)
		self.add("billing", LAB)
		self.add("bulk bill", RBn)
		self.add("private", RBn)
		self.add("rebate", RBn)
		self.add("wcover", RBn, newline = 1)
		self.add("", LAB)
		self.finish()

class VaccinationEditArea(EditArea2):
	def __init__(self, parent, id):
		EditArea2.__init__(self, parent, id)
		self.add("target disease", CMBx, weight = 2)
		self.add("schedule age", CMBx,  newline = 1)
		self.add("vaccine", CMBx, newline = 1)
		self.add("date given", newline = 1)
		self.add("serial no", newline = 1)
		self.add("route", CMBx)
		self.add("site injected", CMBx)
		self.finish()
		




if __name__=="__main__":
	app = wxPyWidgetTester(size=(400,300) )
	app.SetWidget( PastHistoryEditArea, -1)
	app.MainLoop()

	app = wxPyWidgetTester(size=(400,300) )
	app.SetWidget( MedicationEditArea, -1)
	app.MainLoop()
	
	app = wxPyWidgetTester( size=(400, 300) )
	app.SetWidget( RecallEditArea, -1)
	app.MainLoop()

	
	app = wxPyWidgetTester( size=(400, 300) )
	app.SetWidget( ReferralEditArea, -1)
	app.MainLoop()
	
	app = wxPyWidgetTester( size=(400, 300) )
	app.SetWidget( RequestEditArea, -1)
	app.MainLoop()
	
		
	app = wxPyWidgetTester( size=(400, 200) )
	app.SetWidget( VaccinationEditArea, -1)
	app.MainLoop()

			
			
		

	

		

