"""GnuMed SOAP related widgets.

The code in here is independant of gmPG.
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmSOAPWidgets.py,v $
# $Id: gmSOAPWidgets.py,v 1.14 2005-03-04 19:44:28 cfmoro Exp $
__version__ = "$Revision: 1.14 $"
__author__ = "Carlos Moro <cfmoro1976@yahoo.es>, K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL"

# 3rd party
from wxPython import wx

# GnuMed
from Gnumed.pycommon import gmDispatcher, gmSignals, gmI18N, gmLog, gmExceptions
from Gnumed.pycommon.gmPyCompat import *
from Gnumed.wxpython import gmResizingWidgets
from Gnumed.business import gmPerson, gmEMRStructItems, gmSOAPimporter

_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)

# FIXME attribute encapsulation and private methods
# FIXME i18n
#============================================================
class cSOAPLineDef:
	def __init__(self):
		self.label = _('label missing')
		self.text = ''
		self.data = {
			'soap_cat': _('soap cat missing'),
			'narrative instance': None
		}
#============================================================
class cResizingSoapWin (gmResizingWidgets.cResizingWindow):

	def __init__(self, parent, size, input_defs=None):
		"""Resizing SOAP note input editor.

		Labels and categories are customizable.

		@param input_defs: note's labels and categories
		@type input_defs: list of cSOAPLineDef instances
		"""
		if input_defs is None or len(input_defs) == 0:
			raise gmExceptions.ConstructorError, 'cannot generate note with field defs [%s]' % (input_defs)
		self.__input_defs = input_defs
		gmResizingWidgets.cResizingWindow.__init__(self, parent, id= -1, size=size)
	#--------------------------------------------------------
	def DoLayout(self):
		"""Visually display input note according to user defined labels.
		"""
		input_fields = []
		# add fields to edit widget
		# note: this may produce identically labelled lines
		for line_def in self.__input_defs:
			input_field = gmResizingWidgets.cResizingSTC(self, -1, data = line_def.data)
			input_field.SetText(line_def.text)
			self.AddWidget(widget=input_field, label=line_def.label)
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
	and a staticText that displays which health problem its current note is related to.
	"""
	#--------------------------------------------------------
	def __init__(self, parent, problem=None, input_defs=None, default_labels = None):
		"""Construct a new SOAP input widget

		@param parent: the parent widget

		@param problem: the problem to create the SOAP editor for.
		For clarity let's assume there cannot be a SOAP editor w/o
		a health problem.
		@type problem gmEMRStructItems.cProblem instance

		@param input_defs: can be either the input lines definitions
		(dictionary) or the encounter (instance) from which they
		will be retrieved.
		@type input_defs: either a dictionary or a
		gmEMRStructItems.cEncounter instance.

		@param default_labels: The user customized labels for each of
		soap categories.
		@type default_labels: A dictionary instance the keys of which
		are soap categories.
		"""
		# sanity check
		if not isinstance(problem, gmEMRStructItems.cProblem):
			raise gmExceptions.ConstructorError, 'cannot make progress note editor for health problem [%s]' % str(problem)
		self.__problem = problem

		# if encounter given, obtain input lines definitions from it
		if isinstance(input_defs, gmEMRStructItems.cEncounter):
			if default_labels is None:
				default_labels = {
					's': _('History Taken'),
					'o': _('Findings'),
					'a': _('Assessment'),
					'p': _('Plan')
			}
			input_defs = self.__get_narrative(encounter = input_defs, default_labels = default_labels)

		# do layout
		wx.wxPanel.__init__ (self,
			parent,
			-1,
			wx.wxPyDefaultPosition,
			wx.wxPyDefaultSize,
			wx.wxNO_BORDER
		)
		# - heading
		self.__soap_heading = wx.wxStaticText(self, -1, 'error: no problem given')
		# - editor
		if input_defs is None:
			soap_lines = []
			# make Richard the default ;-)
			line = cSOAPLineDef()
			line.label = _('Patient Request')
			line.data['soap_cat'] = 's'
			soap_lines.append(line)

			line = cSOAPLineDef()
			line.label = _('History Taken')
			line.data['soap_cat'] = 's'
			soap_lines.append(line)

			line = cSOAPLineDef()
			line.label = _('Findings')
			line.data['soap_cat'] = 'o'
			soap_lines.append(line)

			line = cSOAPLineDef()
			line.label = _('Assessment')
			line.data['soap_cat'] = 'a'
			soap_lines.append(line)

			line = cSOAPLineDef()
			line.label = _('Plan')
			line.data['soap_cat'] = 'p'
			soap_lines.append(line)
		else:
			soap_lines = input_defs
		self.__soap_text_editor = cResizingSoapWin (
			self,
			size = wx.wxSize(300, 150),
			input_defs = soap_lines
		)
		# - arrange
		self.__szr_main = wx.wxBoxSizer(wx.wxVERTICAL)
		self.__szr_main.Add(self.__soap_heading)
		self.__szr_main.Add(self.__soap_text_editor)
		self.SetSizerAndFit(self.__szr_main)

		self.SetProblem(problem) # display health problem
	#--------------------------------------------------------
	# public API
	#--------------------------------------------------------
	def SetProblem(self, problem):
		"""
		Set the related problem for this SOAP input widget.
		Update heading label with episode descriptive text.
		
		@param problem: SOAP input widget's related episode
		@type problem: gmEMRStructItems.cEpisode		
		"""
		self.__problem = problem
		# display health problem
		txt = 'problem: %s' % self.__problem['problem']
		self.__set_heading(txt)
		# flag indicating saved state
		self.__is_saved = False		
	#--------------------------------------------------------
	def GetProblem(self):
		"""
		Retrieve the related health problem for this SOAP input widget.
		"""
		return self.__problem
	#--------------------------------------------------------
	def get_editor(self):
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
	def SetSaved(self, is_saved):
		"""
		Set SOAP input widget saved (dumped to backend) state

		@param is_saved: Flag indicating wether the SOAP has been dumped to
						 persistent backend
		@type is_saved: boolean
		"""
		self.__is_saved = is_saved
		self.__set_heading('')
		self.Clear()
		self.__problem = None
	#--------------------------------------------------------
	def IsSaved(self):
		"""
		Check  SOAP input widget saved (dumped to backend) state
		"""
		return self.__is_saved
	#--------------------------------------------------------
	# internal API
	#--------------------------------------------------------
	def __get_narrative(self, encounter=None, default_labels=None):
		"""
		Retrieve the soap editor input lines definitions built from
		all the narratives for the given problem along a specific
		encounter.

		@param encounter The encounter to obtain the narrative for.
		@type A gmEMRStructItems.cEncounter instance.

		@param default_labels: The user customized labels for each
		soap category.
		@type default_labels: A dictionary instance which keys are
		soap categories.
		"""
		pat = gmPerson.gmCurrentPatient()
		emr = pat.get_clinical_record()
		soap_lines = []
		# for each soap cat
		for soap_cat in gmSOAPimporter.soap_bundle_SOAP_CATS:
			# retrieve narrative for given problem/encounter
			narr_items =  emr.get_clin_narrative (
				encounters = [encounter['pk_encounter']],
				issues = [self.__problem['pk_health_issue']],
				soap_cats = [soap_cat]
			)
			for narrative in narr_items:
				try:
					# FIXME: add more data such as doctor sig
					label_txt = default_labels[narrative['soap_cat']]
				except:
					label_txt = narrative['soap_cat']				
				line = cSOAPLineDef()
				line.label = label_txt
				line.text = narrative['narrative']
				line.data['narrative instance'] = narrative
				soap_lines.append(line)
		return soap_lines
	#--------------------------------------------------------	
	def __set_heading(self, txt):
		"""Configure SOAP widget's heading title

		@param txt: New widget's heading title to set
		@type txt: string
		"""
		self.__soap_heading.SetLabel(txt)
		size = self.__soap_heading.GetBestSize()
		self.__szr_main.SetItemMinSize(self.__soap_heading, size.width, size.height)
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
		self.__pat = gmPerson.gmCurrentPatient()
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
		szr_outer = wx.wxStaticBoxSizer(wx.wxStaticBox(self, -1, _("clinical progress note")), wx.wxVERTICAL)
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
	_log = gmLog.gmDefLog
	_log.SetAllLogLevels(gmLog.lData)
	from Gnumed.pycommon import gmPG
	gmPG.set_default_client_encoding('latin1')

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
		# obtain patient
		patient = gmPerson.ask_for_patient()
		if patient is None:
			print "No patient. Exiting gracefully..."
			sys.exit(0)
		
		problem = gmEMRStructItems.cProblem(aPK_obj={'pk_patient': 12, 'pk_health_issue': 1, 'pk_episode': 1})
		encounter = gmEMRStructItems.cEncounter(aPK_obj=1)		
		default_labels = {'s':'Subjective', 'o':'Objective', 'a':'Assesment', 'p':'Plan'}
		app = wx.wxPyWidgetTester(size=(300,500))
		app.SetWidget(cResizingSoapPanel, problem, encounter, default_labels)
		app.MainLoop()
		del app		
		
		app = wx.wxPyWidgetTester(size=(300,300))
		app.SetWidget(cResizingSoapPanel, problem)
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
# Revision 1.14  2005-03-04 19:44:28  cfmoro
# Minor fixes from unit test
#
# Revision 1.13  2005/03/03 21:12:49  ncq
# - some cleanups, switch to using data transfer classes
#   instead of complex and unwieldy dictionaries
#
# Revision 1.12  2005/02/23 03:20:44  cfmoro
# Restores SetProblem function. Clean ups
#
# Revision 1.11  2005/02/21 19:07:42  ncq
# - some cleanup
#
# Revision 1.10  2005/01/31 10:37:26  ncq
# - gmPatient.py -> gmPerson.py
#
# Revision 1.9  2005/01/28 18:35:42  cfmoro
# Removed problem idx number
#
# Revision 1.8  2005/01/18 13:38:24  ncq
# - cleanup
# - input_defs needs to be list as dict does not guarantee order
# - make Richard-SOAP the default
#
# Revision 1.7  2005/01/17 19:55:28  cfmoro
# Adapted to receive cProblem instances for SOAP edition
#
# Revision 1.6  2005/01/13 14:28:07  ncq
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
