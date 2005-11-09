"""
A base class for a debulked version of syan's new edit area
It knows zero about the backend, just placement and initalisation of
the database
"""

__version__ = "$ Id: $ "
__author__ = "Syan Tan, Ian Haywood"

import re, string

from wxPython.wx import *

TBx = 1		#TextBox
CHBx = 2	#CheckBox	
RBn = 3		#RadioButton
CMBx =4		#ComboBox
LAB = 5		#Label

#this does make this module dependent on a lot of other modules
if __name__ == "__main__":
	sys.path.append ("../pycommon/")
	sys.path.append ("../../client/pycommon/")
        
from gmDateTimeInput import *

GMDI = 6	#gmDateInput	
PWh = 7		#gmPhraseWheel


class EditArea (wxPanel):
	def __init__(self, parent, id, defaultLabelWeight = 1):
		self.defaultLabelWeight = defaultLabelWeight
		self.nextId = 1
		self.rowCount = 0
                self.rowItems = 0
		self.widgets= {}
		self.types = {}
		self.groups = {}
		self.mapping = {}
		self.statements = {}

		self.statementsList = []  # need this for ordered creation

		self.narrowOn= {}
		self.narrowFrom= {}
		self.oldText = ""
		self.disableTextChange = 0

		self.widgetConfig = []
                self.lines = []
                self.line = []
                self.parent = parent
                wxPanel.__init__ (self, parent, id)




	def add(self, propName,  type=TBx ,weight=1,  displayName = None,  newline = 0, constrained = 1):
		""" sets the default display Name to the property name,
		    capitalizes the display name,
		    creates the widget of the selected type, the default 
		    widget is a textbox,
		    adds the widget at the given weight, adjust if last
		    widget on line ( does this really do anything?),
		    add the line to the sizer if a newline and 
		    start a newline.
		    	parameters:
				propName -the widgetName, the name which it will be mapped.
				type     -the type of widget, as at the top of script. CMBx, PWh , TBx, LAB, CHBx, RBn
				weight   -the weighting inside the FlexGridSizer.
				displayName  -a different displayName to the widgetName. Not used as a key.
				newline   - last widget on the line
				constrained - whether the widget is subject to reference consistency checks, when a parent
					       or child widget changes.

				
		    """

		self.widgetConfig.append( ( propName, type, weight, displayName, newline, constrained) )
		self.types[propName] = type

        def makeWidgetLines(self):
	   for definition in self.widgetConfig:
               self.createWidget(self.parent, definition)	


        def getTextWidgetCount( self, lineDefs):
	        count = 0
	       	for (propName, type, weight,displayName, newline, constrained ) in lineDefs:
		       if type in [TBx, GMDI, CMBx, PWh]:
			       count += 1
		return count

        def createWidget(self, parent, definition):	
		( propName, type, weight,displayName, newline, constrained)= definition

		if displayName == None:
			displayName = propName.capitalize()
				
		if type == TBx:
			widget = wxTextCtrl(parent, -1 )

		if type == RBn:
			widget = wxRadioButton(parent, -1, displayName)
		
		if type == CHBx:
			widget = wxCheckBox(parent, -1, displayName)
			
		if type == CMBx:
			widget = wxComboBox(parent, -1)
		
		if type == LAB:
			widget = wxStaticText(parent, -1, displayName, style=wxALIGN_RIGHT)

		if type == GMDI:
			widget = gmDateTimeInput.gmDateInput(parent =parent,id = -1, size= wxDefaultSize, pos = wxDefaultPosition)

		if type == PWh:
			widget = gmPhraseWheel.cPhraseWheel( parent =parent, id = -1, size = wxDefaultSize, pos = wxDefaultPosition)
		
		if newline and self.rowItems   < 1:
			aproportion =  2 + 2 * self.defaultLabelWeight #for single line of label and field, this proportion makes it space out
			aflag = wxEXPAND
		else:
			aproportion = weight 
			aflag =  wxALIGN_LEFT | wxEXPAND
                if type in [ TBx, GMDI, CMBx, PWh] :
				aproportion += 2
				if displayName == None:
					displayName = propName
				self.createWidget (parent, (str(wxNewId ()), LAB , self.defaultLabelWeight, displayName, 0, 0))
		self.line.append ( (widget, aproportion, aflag))
		self.rowItems += 1
	
		if type != LAB:
			self.widgets[propName] = widget
			widget.SetName(propName)

		if newline:
			self.rowCount += 1
			self.lines.append(line)
			self.line = []
			#self.topSizer.Add(self.lineSizer,1,  flag= wxGROW)
			#self.lineSizer = wxBoxSizer(wxHORIZONTAL)
			self.rowItems = 0

        def __getitem__ (self, prop):
            return self.widgets[prop]

        def __len__(self):
            return len(self.widgetConfig)

            
	def layout(self):
            self.topSizer = wxFlexGridSizer(0,1,0,0)
            self.topSizer.AddGrowableCol(0)
            
            for line in self.lines:
                lineSizer = wxBoxSizer(wxHORIZONTAL)
                for (widget, weight, style) in line:
                    lineSizer.Add( widget, weight, style)
                    self.topSizer.Add( lineSizer,6,  wxEXPAND)
                    
            self.SetSizer(self.topSizer)
            self.SetAutoLayout(True)
            self.topSizer.Fit(self)
            self.topSizer.SetSizeHints(self)
            self.Layout()


class MedicationEditArea(EditArea):
	
	def __init__(self, parent, id):
		EditArea.__init__(self, parent, id)
		self.add("classes", PWh, newline = 1)
		self.add("generic", PWh, weight = 1)
		self.add("veteran", CHBx,newline=1)
		self.add("drug", CMBx,  weight = 1)
		self.add("reg 24", CHBx, newline=1)
		self.add("quantity", CMBx, constrained = 2)
		self.add("repeats",   newline=1)
		self.add("direction", weight = 2, newline=1)
		self.add("for", PWh, weight = 2, newline = 1)
		self.add("date", GMDI)
		self.add("usual", CHBx, newline=1)
		self.add("progress notes", weight = 2, newline = 1)
                self.makeWidgetLines ()
                self.layout ()
                self.Show ()


if __name__ == '__main__':
    app = wxPyWidgetTester(size=(500,300) )
    app.SetWidget( MedicationEditArea, -1)
    app.MainLoop()
