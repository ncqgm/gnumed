"""
	GnuMed notes input panel
"""
#================================================================
__version__ = "$Revision: 1.1 $"
__author__ = "cfmoro1976@yahoo.es"
__license__ = "GPL"

import os.path, sys

from wxPython import wx

from Gnumed.pycommon import gmLog, gmI18N, gmDispatcher, gmSignals, gmWhoAmI, gmExceptions
from Gnumed.wxpython import gmRegetMixin, gmResizingWidgets
from Gnumed.pycommon.gmPyCompat import *
from Gnumed.pycommon.gmMatchProvider import cMatchProvider_FixedList

_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)


# FIXME attribute encapsulation and private methods
# FIXME i18n	
def create_widget_on_test_kwd1(*args, **kwargs):
	print "test keyword must have been typed..."
	print "actually this would have to return a suitable wxWindow subclass instance"
	print "args:", args
	print "kwd args:"
	for key in kwargs.keys():
		print key, "->", kwargs[key]
#================================================================
def create_widget_on_test_kwd2(*args, **kwargs):
	msg = (
		"test keyword must have been typed...\n"
		"actually this would have to return a suitable wxWindow subclass instance\n"
	)
	for arg in args:
		msg = msg + "\narg ==> %s" % arg
	for key in kwargs.keys():
		msg = msg + "\n%s ==> %s" % (key, kwargs[key])
	gmGuiHelpers.gm_show_info (
		aMessage = msg,
		aTitle = 'msg box on create_widget from test_keyword'
	)
#================================================================
class cSoapWin (gmResizingWidgets.cResizingWindow):
	
	def __init__(self, parent, size, input_cats):
		"""
		Create a new instance of progress note input editor.
		Note's labels and categories are customizable.
		
		@param input_cats: note's labels and categories
		@type input_cats: dictionary of pairs of input label:category 
		"""		
		if input_cats is None or len(input_cats) == 0:
			raise gmExceptions.ConstructorError, 'cannot contruct note with input categories [%s]' % (input_cats)
		self.input_cats = input_cats
		
		gmResizingWidgets.cResizingWindow.__init__(self, parent, id= -1, size=size)
		
	#--------------------------------------------------------
	def DoLayout(self):
		"""
		Visually display input note, according to user defined labels
		"""
		
		# temporal cache of input fields
		input_fields =[]
		# add fields to edit widget
		for input_label in self.input_cats.values():
			input_field = gmResizingWidgets.cResizingSTC(self, -1)
			self.AddWidget (widget=input_field, label=input_label)
			self.Newline()
			input_fields.append(input_field)

		# tab navigation between input fields				
		for cont in range(len(input_fields)):			
			try:
				input_fields[cont].prev_in_tab_order = input_fields[cont-1]
			except IndexError:
				input_fields[cont].prev_in_tab_order = None
			try:
				input_fields[cont].next_in_tab_order = input_fields[cont+1]
			except IndexError:
				input_fields[cont].next_in_tab_order = None

		# PENDING keywords set up
		#kwds = {}
		#kwds['$test_keyword'] = {'widget_factory': create_widget_on_test_kwd2}
		#self.input2.set_keywords(popup_keywords=kwds)		
			
#============================================================
class cSoapPanel(wx.wxPanel):
	"""
	Basic note panel. It provides gmResizingWindows based  editor
	and a staticText that displays the which issue is current note related to.
	"""
	
	#--------------------------------------------------------
	def __init__(self, parent):
		"""
		Construct a new SOAP input widget
		
		@param parent: the parent widget		
		"""
		
		# panel initialization
		wx.wxPanel.__init__ (self,
			parent,
			-1,
			wx.wxPyDefaultPosition,
			wx.wxPyDefaultSize,
			wx.wxNO_BORDER
		)
		
		# soap's health issue staticText heading
		self.__soap_label = wx.wxStaticText(self, -1, "Select issue and press 'New'")
		# related health issue
		self.__health_issue = None
		print "...creating new soap input widget"
		# flag indicating saved state
		self.is_saved = False
				
		# soap rich and smart text editor
		# FIXME obtain cats from user preferences
		self.__soap_text_editor = cSoapWin (self, size = wx.wxSize (300, 150),
		input_cats = {'Subjective':'s', 'Objective':'o', 'Assessment':'a',
		'Plan':'p'})

		# sizers for widgets
		self.__soap_control_sizer = wx.wxBoxSizer(wx.wxVERTICAL)
		self.__soap_control_sizer.Add(self.__soap_label)		   
		self.__soap_control_sizer.Add(self.__soap_text_editor)
		
		# do layout
		self.SetSizerAndFit(self.__soap_control_sizer)				
		
	#--------------------------------------------------------
	def SetHealthIssue(self, selected_issue):
		"""
		Set the related health issue for this SOAP input widget.
		Update heading label with health issue data.
		
		@type selected_issue: gmEMRStructItems.cHealthIssue
		@param selected_issue: SOAP input widget's related health issue
		"""
		self.__health_issue = selected_issue
		if self.__health_issue is None or len(self.__health_issue) == 0:
			self.__soap_label.SetLabel("Select issue and press 'New'")
		else:
			txt = '%s# %s'%(self.__health_issue[0]+1,self.__health_issue[1]['description'])
			# update staticText content and recalculate sizer internal values
			self.__SetHeading(txt)
		self.ShowContents()
			
	#--------------------------------------------------------
	def GetHealthIssue(self):
		"""
		Retrieve the related health issue for this SOAP input widget.
		"""
		return self.__health_issue
	
	#--------------------------------------------------------
	def GetSOAP(self):
		"""
		Retrieves widget's SOAP text editor
		"""
		return self.__soap_text_editor
	
	#--------------------------------------------------------
	def ClearSOAP(self):
		"""
		Clear any entries in widget's SOAP text editor
		"""
		self.__soap_text_editor.Clear()

	#--------------------------------------------------------
	def HideContents(self):
		"""
		Hide widget's components (health issue heading and SOAP text editor)
		"""
		self.__soap_label.Hide()
		self.__soap_text_editor.Hide()
	
	#--------------------------------------------------------	
	def ShowContents(self):
		"""
		Show widget's components (health issue heading and SOAP text editor)
		"""
		self.__soap_label.Show(True)
		self.__soap_text_editor.Show(True)

	#--------------------------------------------------------
	def IsContentShown(self):
		"""
		Check if contents are being shown
		"""
		return self.__soap_label.IsShown()
		
	#--------------------------------------------------------	
	def SetSaved(self, is_saved):
		"""
		Set SOAP input widget saved (dumped to backend) state
		
		@param is_saved: Flag indicating wether the SOAP has been dumped to
						 persistent backend
		@type is_saved: boolean
		"""
		self.is_saved = is_saved
		if is_saved:
			self.__SetHeading(self.__soap_label.GetLabel() + '. SAVED')

	#--------------------------------------------------------	
	def IsSaved(self):
		"""
		Check  SOAP input widget saved (dumped to backend) state
		
		"""
		return self.is_saved
			
	#--------------------------------------------------------	
	def __SetHeading(self, txt):
		"""
		Configure SOAP widget's heading title
		
		@param txt: New widget's heading title to set
		@type txt: string
		"""
		self.__soap_label.SetLabel(txt)
		size = self.__soap_label.GetBestSize()
		self.__soap_control_sizer.SetItemMinSize(self.__soap_label, size.width, size.height)
		self.Layout()
		
	#--------------------------------------------------------	
	def ResetAndHide(self):
		"""
		Reset all data and hide contents
		
		"""		
		self.SetHealthIssue(None)			
		self.SetSaved(False)
		self.ClearSOAP()		
		self.HideContents()
					
#================================================================
# MAIN
#----------------------------------------------------------------
if __name__ == '__main__':

	_log.SetAllLogLevels(gmLog.lData)
	_log.Log (gmLog.lInfo, "starting SOAP input panel...")

	try:

		# display standalone browser
		application = wx.wxPyWidgetTester(size=(800,600))
		soap_input = cSoapPanel(application.frame)		
		
		application.frame.Show(True)
		application.MainLoop()
		
	except StandardError:
		_log.LogException("unhandled exception caught !", sys.exc_info(), 1)
		# but re-raise them
		raise

	_log.Log (gmLog.lInfo, "closing soap widgets...")
