
import testschema5 as testschema
from wxPython.wx import *


class FormBuilder:

	def __init__(self):
		self.forms = {}
		self.formName = ''
		self.formStack = []
		self.forms = {}

	def addAttribute(self, node, name):
		print "adding attr",(len(self.formStack)+ 1) * '  ',self.formName," : ", node, ".", name
		self.forms[node] = self.forms.get(node, [])
		self.forms[node].append(name)
	
	def addSubForm(self, subFormName, level):
		print len(self.formStack) * '  ', "  adding subForm", subFormName
		self.setCurrentForm(subFormName)
	
	def popForm(self):
		print '\t' * 4, "End Form", self.formName
		self.formName = self.formStack[-1]
		self.formStack = self.formStack[:-1]
	
	def setCurrentForm(self, node):
		#print "Setting Form For ", node
		self.formStack.append(self.formName)
		self.formName = node

class ColumnSizerFactory:

	def __init__(self, columns):
		
		self.columns = columns
		self.vSizers = [wxBoxSizer(wxVERTICAL) for i in range(0,columns)]

		self.currentCol = 0
		
	def Add(self,  widgetSizerOrWidth, proportion, flag, border=5):
		print "adding to ColumnSizer column ", self.currentCol
		self.vSizers[self.currentCol].Add( widgetSizerOrWidth, proportion, flag, border)
		self.currentCol += 1
		if self.currentCol >= self.columns:
			self.currentCol = 0

	def getSizer(self):
		print "CALLED ", self, "getSizer()"
		sizer = wxBoxSizer(wxHORIZONTAL)
		for sz in self.vSizers:
			sizer.Add(sz, 1, wxEXPAND, 20)
		
		return sizer
		
	


class wxPanelAndListFormBuilder1(FormBuilder):

	def __init__(self, parent, schema, tabbed_levels = [1]):
		"""parent - a wxWindow , the topmost container. It should have a sizer already set"""
		FormBuilder.__init__(self)
		self.schema = schema
		self.parent = parent
		self.parentSizer = parent.GetSizer()
		self.containers = []
		self.wxIds = {}
		self.boxes = [] 
		self.box = None
		self.currentNode = ""
		self.controls = {}
		self.tabbed_levels = tabbed_levels
		self.notebookPageSizers = { 'default': (ColumnSizerFactory,[2]) , 'clin_health_issue' : (wxBoxSizer, [wxVERTICAL] ) } 
		self.notebook = {}
		self.largeFields = ['narrative', 'text', 'comment' ]
		self.largeFieldDefaultHeight = {'narrative': 50 ,'text':  50, 'comment':20 }
		self.lineSizer = None
		self.lineWidgetNumber = 3 
		self.lineWidgetCount = 0

	def addAttribute(self, node, name):
		FormBuilder.addAttribute(self,node, name)
		if node <> self.currentNode:
			if self.box <> None and self.nodeAttrCount > 0:
				self.boxes.append( self.box)
				#self.sizer.Fit(self.box)
			self.currentNode = node
			self.nodeAttrCount = 0
		#if len(name) >= 2 and name[0:2] in ['id', 'pk']:
		#	return

		if self.nodeAttrCount == 0:
			#print "creating static box with parent", self.parent, "node", node
			#self.box = wxPanel(self.parent, wxNewId(),wxDefaultPosition,wxDefaultSize)
			#self.sizer = wx
			
			#print "adding sizer"
				
			#textBox= wxStaticBox(self.box, wxNewId(), node)
			textBox= wxStaticText(self.parent, wxNewId(), node)
			font = textBox.GetFont()
			font.SetStyle(wxITALIC)
			font.SetUnderlined(True)
			textBox.SetFont(font)
			
			#self.sizer = wxStaticBoxSizer(textBox, wxHORIZONTAL)
			self.sizer = wxBoxSizer(wxVERTICAL)
			self.box = self.sizer		
			#self.box.SetSizer(self.sizer)
			self.sizer.Add(textBox, 0, wxEXPAND)
			#self.sizer.Add(0, 0, 0)
			#self.sizer.Add(0, 0, 0)
			self.addLineSizer()
		self.nodeAttrCount += 1	
		self.controls[node] = self.controls.get(node, {})
		if name in self.largeFields:
			
				
			#sizer = wxBoxSizer(wxHORIZONTAL)
			self.sizer.Add(wxStaticText(self.parent, -1, name), 1, wxALIGN_BOTTOM )
			self.controls[node][name] = self.getControl(node, name, self.parent)
			self.sizer.Add( self.controls[node][name], 3, wxEXPAND)
			#self.sizer.Add( sizer, 3, wxEXPAND)
			#self.sizer.Add(0,0,0)
			#self.sizer.Add(0,0,0)
			
		else:		
			#sizer = wxBoxSizer(wxHORIZONTAL)
			#print "adding attribute static text and control"
			self.lineSizer.Add(wxStaticText(self.parent, -1, name), 0, 0)
			self.controls[node][name] = self.getControl(node, name, self.parent)
			self.lineSizer.Add( self.controls[node][name], 1, wxRIGHT)
			self.lineWidgetCount += 1
			if self.lineWidgetCount == self.lineWidgetNumber:
				self.addLineSizer()
				self.lineWidgetCount = 0
			#self.sizer.Add(sizer, 0, 0)
	
	def addLineSizer( self):
		self.fillLineSizer()
		self.lineSizer = wxBoxSizer(wxHORIZONTAL)	
		self.sizer.Add(self.lineSizer, 0, wxTOP)
		
	
	def fillLineSizer(self):
		if not self.lineSizer is None:
			for i in range ( self.lineWidgetNumber  -  self.lineWidgetCount):
				self.lineSizer.Add(0,0,0)


	def getControl(self, node, name, parent):
		"""check type of node.name for different controls"""
		id = wxNewId()
		self.wxIds[node+'.'+name] = id
		if name in self.largeFields:
			ctl = wxTextCtrl( parent, id,'', wxDefaultPosition,(80,self.largeFieldDefaultHeight[name] ), wxTE_MULTILINE)
			return ctl


		if self.isBoolean(node, name):
			return wxCheckBox(parent, id,'')

		return wxTextCtrl( parent , id)
		
	def isBoolean(self, node, name):
		if name[0:2] == 'is':
			return True
		"""add a schema check here."""
		if self.schema.get_attribute_type(node, name) in ['bool']:
			return True
		return False
				
	def addSubForm(self, subFormName, level):
		FormBuilder.addSubForm(self, subFormName, level)

		self.insertBoxes()
		self.level = level
		if level in  self.tabbed_levels:
			if self.notebook.get(level,None)  == None:
				print "creating new notebook at ", subFormName
				notebook = wxNotebook(self.parent, wxNewId() )
				sizer = wxNotebookSizer(notebook)
				notebook.SetSizer(sizer)
			
				#self.parent.GetSizer().Add(wxStaticText(self.parent,-1,''),1,0)
				#self.fillLineSizer()
				#self.sizer.Add(wxStaticText(self.parent, -1,'***'),1,wxEXPAND)
				self.parentSizer.Add(sizer, 5, wxEXPAND)
				self.notebook[level] = (notebook, sizer)
				
			self.containers.append((self.parent, self.parentSizer))
			(self.parent, self.parentSizer) = self.notebook[level]
		
			
		if not self.notebook.get(self.level, None):
			#nextContainer = self.parent
			#pass
			nextContainer = wxPanel(self.parent, wxNewId())
			#nextContainer.SetAutoLayout(True)
			self.parentSizer.Add(nextContainer, 2, wxEXPAND)
			sizer = wxBoxSizer(wxVERTICAL)
			sz = sizer
			#box = wxStaticBox(nextContainer, wxNewId(), subFormName)
			#nextContainer.SetSizer(wxStaticBoxSizer(box, wxVERTICAL))
		else:
			scrollWin = wxScrolledWindow( self.parent, wxNewId())
			scrollWin.SetVirtualSize( (2000, 1000))
			scrollWin.SetScrollRate(40, 40)
			scrollWin.EnableScrolling(True, True)
			sizerClass, params = self.notebookPageSizers.get(subFormName, self.notebookPageSizers['default']) 
			if 'Factory' in sizerClass.__name__:
				sizer = sizerClass(*params)
				sz = sizer.getSizer()
			else:
				sizer = sizerClass(*params)
				sz = sizer
				
			nextContainer = scrollWin
			self.notebook[self.level][0].AddPage( nextContainer, subFormName)
		nextContainer.SetSizer(sz)	
		self.containers.append((self.parent, self.parentSizer) )
		self.parent = nextContainer
		self.parentSizer = sizer
		self.currentNode = None
		
	def insertBoxes(self):
		if self.box <> None:
			self.boxes.append(self.box)
		for x in self.boxes:
			# the parent for GetSuize()
			#print x, x.__dict__
			self.parentSizer.Add(x, 0 ,wxEXPAND)

		self.boxes = []
		self.box = None

	def popForm(self):
		self.insertBoxes()
		FormBuilder.popForm(self)
		#self.parentSizer.Fit(self.parent)
		(self.parent, self.parentSizer) =  self.containers[-1]
		self.containers = self.containers[:-1]
		self.level -= 1
			
		


	def setCurrentForm(self, node):
		FormBuilder.setCurrentForm(self, node)

	
	

	
def printForm( formContentList, builder , level = 0 ):
	
	for k, attr in formContentList:
		
		builder.addSubForm(k, level )
		for x in attr:
			if type(x) <> type([]):
				builder.addAttribute(*x.split('.'))
			else:
				printForm(x, builder, level + 1)
		builder.popForm()		
			

def printAim(schema, builder, root):
	forms= schema.get_forms(0)
	print
	print '-' * 60
	print "For root ", root , " the following forms will be generated"
	printForm( forms[root], builder)		

class TestApp(wxApp):

	def __init__(self, frame ):
		self.frame = frame 
		wxApp.__init__(self)

	
	def getFrame(self):
		return self.frame
		
	def OnInit(self):
		self.SetTopWindow(self.frame)
		self.frame.Fit()
		return True
			


if __name__=="__main__":
	config = testschema.config.split('\n')
	cfgObj = testschema.Config(config)
	s = testschema.SchemaParser(cfgObj)
	frame = wxFrame( None, -1, 'TestForm')
	frame.SetSizer( wxBoxSizer(wxVERTICAL) )
	notebook = wxNotebook( frame, -1)
	sizer = wxNotebookSizer(notebook)
	notebook.SetSizer(sizer)
	frame.GetSizer().Add(notebook, 1, wxEXPAND)
	tabbed_levels = [ [1,4], [1,3] ]
	names = [ 'xlnk_identity', 'identity' ]
	panel = [None, None]
	for i in range(2):
		panel[i] = wxPanel(notebook, -1)
		panel[i].SetSizer(wxBoxSizer(wxVERTICAL))
		notebook.AddPage(panel[i], names[i])
		builder = wxPanelAndListFormBuilder1(panel[i], s, tabbed_levels[i])
		printAim(s, builder, names[i])

	#builder = wxPanelAndListFormBuilder1(frame, [1,  4  ])
	#printAim(s, builder, 'xlnk_identity')
	#frame.SetAutoLayout(True)
	#frame.GetSizer().Fit(frame)
	#app = TestApp(frame)
	#app.frame.Show(1)
	#app.MainLoop()

	#frame.Dispose()
	#frame = wxFrame(None, -1, 'TestForm2')
	#frame.SetSizer( wxBoxSizer(wxVERTICAL) )
	#print "constructing builder"
	#builder = wxPanelAndListFormBuilder1(frame, [1,3])
	#	print sys.exc_info()[2]
	#printAim(s, builder, 'identity')
	app = TestApp(frame)
	frame.GetSizer().Fit(frame)
	app.frame.Show(1)
	app.MainLoop()
	

	
		

