"""GnuMed SOAP related widgets.

The code in here is independant of gmPG.
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmSOAPWidgets.py,v $
# $Id: gmSOAPWidgets.py,v 1.6 2005-01-13 14:28:07 ncq Exp $
__version__ = "$Revision: 1.6 $"
__author__ = "Carlos Moro <cfmoro1976@yahoo.es>, K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL"

# 3rd party
from wxPython import wx

# GnuMed
from Gnumed.pycommon import gmDispatcher, gmSignals, gmI18N, gmLog, gmExceptions
from Gnumed.pycommon.gmPyCompat import *
from Gnumed.wxpython import gmResizingWidgets
from Gnumed.business import gmPatient

_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)

# FIXME attribute encapsulation and private methods
# FIXME i18n
#============================================================
class cResizingSoapWin (gmResizingWidgets.cResizingWindow):

	def __init__(self, parent, size, input_defs=None):
		"""Resizing SOAP note input editor.

		Labels and categories are customizable.

		@param input_defs: note's labels and categories
		@type input_defs: dictionary of pairs of input label:category
		"""
		if input_defs is None or len(input_defs) == 0:
			raise gmExceptions.ConstructorError, 'cannot generate note with field defs [%s]' % (input_defs)
		self.__input_defs = input_defs

		gmResizingWidgets.cResizingWindow.__init__(self, parent, id= -1, size=size)
	#--------------------------------------------------------
	def DoLayout(self):
		"""Visually display input note, according to user defined labels.
		"""
		input_fields = []			# temporary cache of input fields
		# add fields to edit widget
		for input_label in self.__input_defs.keys():
			input_field = gmResizingWidgets.cResizingSTC(self, -1, data = self.__input_defs[input_label])
			self.AddWidget (widget=input_field, label=input_label)
			self.Newline()
			input_fields.append(input_field)
		# setup tab navigation between input fields
		for field_idx in range(len(input_fields)):
			# previous
			try:
				input_fields[field_idx].prev_in_tab_order = input_fields[field_idx-1]
			except IndexError:
				input_fields[field_idx].prev_in_tab_order = None
			# next
			try:
				input_fields[field_idx].next_in_tab_order = input_fields[field_idx+1]
			except IndexError:
				input_fields[field_idx].next_in_tab_order = None
		# FIXME: PENDING keywords set up
		#kwds = {}
		#kwds['$test_keyword'] = {'widget_factory': create_widget_on_test_kwd2}
		#self.input2.set_keywords(popup_keywords=kwds)
		# FIXME: pending matcher setup

#============================================================
class cResizingSoapPanel(wx.wxPanel):
	"""
	Basic note panel. It provides gmResizingWindows based editor
	and a staticText that displays which problem its current note is related to.
	"""
	#--------------------------------------------------------
	def __init__(self, parent, problem=None):
		"""Construct a new SOAP input widget

		@param parent: the parent widget
		problem:
			health problem name, may be issue or episode name,
			for clarity let's assume there cannot be a SOAP editor w/o a problem
		"""
		if problem is None or len(problem) == 0:
			raise gmExceptions.ConstructorError, 'invalid health problem [%s]' % str(problem)
		self.__problem = problem
		# do layout
		wx.wxPanel.__init__ (self,
			parent,
			-1,
			wx.wxPyDefaultPosition,
			wx.wxPyDefaultSize,
			wx.wxNO_BORDER
		)
		self.__soap_heading = wx.wxStaticText(self, -1, 'error: no problem given')
		self.__soap_text_editor = cResizingSoapWin (
			self,
			size = wx.wxSize (300, 150),
			# FIXME obtain cats from user preferences
			input_defs = {
				'Subjective':'s',
				'Objective':'o',
				'Assessment':'a',
				'Plan':'p'
			}
		)
		self.__soap_control_sizer = wx.wxBoxSizer(wx.wxVERTICAL)
		self.__soap_control_sizer.Add(self.__soap_heading)
		self.__soap_control_sizer.Add(self.__soap_text_editor)
		self.SetSizerAndFit(self.__soap_control_sizer)

		# display health problem
		txt = '#%s: %s'%(self.__problem[0]+1, self.__problem[1]['description'])
		self.__set_heading(txt)

		# flag indicating saved state
		self.__is_saved = False
	#--------------------------------------------------------
	# public API
	#--------------------------------------------------------
#	def SetHealthIssue(self, selected_issue):
#		"""
#		Set the related health issue for this SOAP input widget.
#		Update heading label with health issue data.
#		
#		@type selected_issue: gmEMRStructItems.cHealthIssue
#		@param selected_issue: SOAP input widget's related health issue
#		"""
#		self.__problem = selected_issue
#		if self.__problem is None or len(self.__problem) == 0:
#			self.__soap_heading.SetLabel("Select issue and press 'New'")
#		else:
#			txt = '%s# %s'%(self.__problem[0]+1,self.__problem[1]['description'])
#			# update staticText content and recalculate sizer internal values
#			self.__set_heading(txt)
#		self.ShowContents()
	#--------------------------------------------------------
	def GetProblem(self):
		"""
		Retrieve the related health problem for this SOAP input widget.
		"""
		return self.__problem
	#--------------------------------------------------------
	def GetSOAP(self):
		"""
		Retrieves widget's SOAP text editor
		"""
		return self.__soap_text_editor
	#--------------------------------------------------------
	def Clear(self):
		"""Clear any entries in widget's SOAP text editor
		"""
		self.__soap_text_editor.Clear()
	#--------------------------------------------------------
	# FIXME: what is this used for ?
	def HideContents(self):
		"""
		Hide widget's components (health problem heading and SOAP text editor)
		"""
		self.__soap_heading.Hide()
		self.__soap_text_editor.Hide()
	#--------------------------------------------------------
	def ShowContents(self):
		"""
		Show widget's components (health problem heading and SOAP text editor)
		"""
		self.__soap_heading.Show(True)
		self.__soap_text_editor.Show(True)
	#--------------------------------------------------------
	def IsContentShown(self):
		"""
		Check if contents are being shown
		"""
		return self.__soap_heading.IsShown()
	#--------------------------------------------------------
	def SetSaved(self, is_saved):
		"""
		Set SOAP input widget saved (dumped to backend) state

		@param is_saved: Flag indicating wether the SOAP has been dumped to
						 persistent backend
		@type is_saved: boolean
		"""
		self.__is_saved = is_saved
		if is_saved:
			self.__set_heading(self.__soap_heading.GetLabel() + '. SAVED')
	#--------------------------------------------------------
	def IsSaved(self):
		"""
		Check  SOAP input widget saved (dumped to backend) state
		"""
		return self.__is_saved
	#--------------------------------------------------------
	# FIXME: what is this used for ?
	def ResetAndHide(self):
		"""
		Reset all data and hide contents
		"""
#		self.SetHealthIssue(None)
		self.SetSaved(False)
		self.ClearSOAP()		
		self.HideContents()
	#--------------------------------------------------------
	# internal API
	#--------------------------------------------------------
	def __set_heading(self, txt):
		"""Configure SOAP widget's heading title

		@param txt: New widget's heading title to set
		@type txt: string
		"""
		self.__soap_heading.SetLabel(txt)
		size = self.__soap_heading.GetBestSize()
		self.__soap_control_sizer.SetItemMinSize(self.__soap_heading, size.width, size.height)
		self.Layout()

#============================================================
#============================================================
class cSingleBoxSOAP(wx.wxTextCtrl):
	"""if we separate it out like this it can transparently gain features"""
	def __init__(self, *args, **kwargs):
		wx.wxTextCtrl.__init__(self, *args, **kwargs)
#============================================================
class cSingleBoxSOAPPanel(wx.wxPanel):
	"""Single Box free text SOAP input.

	This widget was suggested by David Guest on the mailing
	list. All it does is provide a single multi-line textbox
	for typing free-text clinical notes which are stored as
	Subjective.
	"""
	def __init__(self, *args, **kwargs):
		wx.wxPanel.__init__(self, *args, **kwargs)
		self.__do_layout()
		self.__pat = gmPatient.gmCurrentPatient()
		if not self.__register_events():
			raise gmExceptions.ConstructorError, 'cannot register interests'
	#--------------------------------------------------------
	def __do_layout(self):
		# large box for free-text clinical notes
		self.__soap_box = cSingleBoxSOAP (
			self,
			-1,
			'',
			style = wx.wxTE_MULTILINE
		)
		# buttons below that
		self.__BTN_save = wx.wxButton(self, wx.wxNewId(), _("save"))
		self.__BTN_save.SetToolTipString(_('save clinical note in EMR'))
		self.__BTN_discard = wx.wxButton(self, wx.wxNewId(), _("discard"))
		self.__BTN_discard.SetToolTipString(_('discard clinical note'))
		szr_btns = wx.wxBoxSizer(wx.wxHORIZONTAL)
		szr_btns.Add(self.__BTN_save, 1, wx.wxALIGN_CENTER_HORIZONTAL, 0)
		szr_btns.Add(self.__BTN_discard, 1, wx.wxALIGN_CENTER_HORIZONTAL, 0)
		# arrange widgets
		szr_outer = wx.wxStaticBoxSizer(wx.wxStaticBox(self, -1, _("SOAP clinical notes")), wx.wxVERTICAL)
		szr_outer.Add(self.__soap_box, 1, wx.wxEXPAND, 0)
		szr_outer.Add(szr_btns, 0, wx.wxEXPAND, 0)
		# and do layout
		self.SetAutoLayout(1)
		self.SetSizer(szr_outer)
		szr_outer.Fit(self)
		szr_outer.SetSizeHints(self)
		self.Layout()
	#--------------------------------------------------------
	def __register_events(self):
		# wxPython events
		wx.EVT_BUTTON(self.__BTN_save, self.__BTN_save.GetId(), self._on_save_note)
		wx.EVT_BUTTON(self.__BTN_discard, self.__BTN_discard.GetId(), self._on_discard_note)

		# client internal signals
		gmDispatcher.connect(signal = gmSignals.activating_patient(), receiver = self._save_note)
		gmDispatcher.connect(signal = gmSignals.application_closing(), receiver = self._save_note)

		return True
	#--------------------------------------------------------
	# event handlers
	#--------------------------------------------------------
	def _on_save_note(self, event):
		self.__save_note()
		#event.Skip()
	#--------------------------------------------------------
	def _on_discard_note(self, event):
		# FIXME: maybe ask for confirmation ?
		self.__soap_box.SetValue('')
		#event.Skip()
	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def _save_note(self):
		wx.wxCallAfter(self.__save_note)
	#--------------------------------------------------------
	def __save_note(self):
		# sanity checks
		if self.__pat is None:
			return True
		if not self.__pat.is_connected():
			return True
		if not self.__soap_box.IsModified():
			return True
		note = self.__soap_box.GetValue()
		if note.strip() == '':
			return True
		# now save note
		emr = self.__pat.get_clinical_record()
		if emr is None:
			_log.Log(gmLog.lErr, 'cannot access clinical record of patient')
			return False
		if not emr.add_clin_narrative(note, soap_cat='s'):
			_log.Log(gmLog.lErr, 'error saving clinical note')
			return False
		self.__soap_box.SetValue('')
		return True
#============================================================
# main
#------------------------------------------------------------
if __name__ == "__main__":

	import sys

	def create_widget_on_test_kwd1(*args, **kwargs):
		print "test keyword must have been typed..."
		print "actually this would have to return a suitable wxWindow subclass instance"
		print "args:", args
		print "kwd args:"
		for key in kwargs.keys():
			print key, "->", kwargs[key]

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

	_log.SetAllLogLevels(gmLog.lData)

	try:
		app = wx.wxPyWidgetTester(size=(300,300))
		app.SetWidget(cResizingSoapPanel, (0, {'description': 'cold/cough'}))
		app.MainLoop()
		del app

		app = wx.wxPyWidgetTester(size=(600,600))
		app.SetWidget(cSingleBoxSOAPPanel, -1)
		app.MainLoop()
	except StandardError:
		_log.LogException("unhandled exception caught !", sys.exc_info(), 1)
		# but re-raise them
		raise

#============================================================
# $Log: gmSOAPWidgets.py,v $
# Revision 1.6  2005-01-13 14:28:07  ncq
# - cleanup
#
# Revision 1.5  2005/01/11 08:12:39  ncq
# - fix a whole bunch of bugs from moving to main trunk
#
# Revision 1.4  2005/01/10 20:14:02  cfmoro
# Import sys
#
# Revision 1.3  2005/01/10 17:50:36  ncq
# - carry over last bits and pieces from test-area
#
# Revision 1.2  2005/01/10 17:48:03  ncq
# - all of test_area/cfmoro/soap_input/gmSoapWidgets.py moved here
#
# Revision 1.1  2005/01/10 16:14:35  ncq
# - soap widgets independant of the backend (gmPG) live in here
#
# Revision 1.13	 2004/06/30 20:33:41  ncq
# - add_clinical_note() -> add_clin_narrative()
#
# Revision 1.12	 2004/03/09 07:54:32  ncq
# - can call __save_note() from button press handler directly
#
# Revision 1.11	 2004/03/08 23:35:10  shilbert
# - adapt to new API from Gnumed.foo import bar
#
# Revision 1.10	 2004/02/25 09:46:22  ncq
# - import from pycommon now, not python-common
#
# Revision 1.9	2004/02/05 23:49:52	 ncq
# - use wxCallAfter()
#
# Revision 1.8	2003/11/09 14:29:11	 ncq
# - new API style in clinical record
#
# Revision 1.7	2003/10/26 01:36:13	 ncq
# - gmTmpPatient -> gmPatient
#
# Revision 1.6	2003/07/05 12:57:23	 ncq
# - catch one more error on saving note
#
# Revision 1.5	2003/06/26 22:26:04	 ncq
# - streamlined _save_note()
#
# Revision 1.4	2003/06/25 22:51:24	 ncq
# - now also handle signale application_closing()
#
# Revision 1.3	2003/06/24 12:57:05	 ncq
# - actually connect to backend
# - save note on patient change and on explicit save request
#
# Revision 1.2	2003/06/22 16:20:33	 ncq
# - start backend connection
#
# Revision 1.1	2003/06/19 16:50:32	 ncq
# - let's make something simple but functional first
#
#
