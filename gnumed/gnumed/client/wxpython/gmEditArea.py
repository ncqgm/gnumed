#====================================================================
# GnuMed
# GPL
#====================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmEditArea.py,v $
# $Id: gmEditArea.py,v 1.88 2005-04-25 17:43:55 ncq Exp $
__version__ = "$Revision: 1.88 $"
__author__ = "R.Terry, K.Hilbert"

#======================================================================

import sys, traceback, time

from wxPython.wx import *
from wxPython import wx

from Gnumed.pycommon import gmLog, gmGuiBroker, gmMatchProvider, gmDispatcher, gmSignals, gmExceptions, gmWhoAmI, gmI18N
from Gnumed.business import gmPerson, gmDemographicRecord, gmForms
from Gnumed.wxpython import gmDateTimeInput, gmPhraseWheel, gmGuiHelpers

_log = gmLog.gmDefLog
_gb = gmGuiBroker.GuiBroker()
_whoami = gmWhoAmI.cWhoAmI()

ID_PROGRESSNOTES = wxNewId()
gmSECTION_SUMMARY = 1
gmSECTION_DEMOGRAPHICS = 2
gmSECTION_CLINICALNOTES = 3
gmSECTION_FAMILYHISTORY = 4
gmSECTION_PASTHISTORY = 5
gmSECTION_SCRIPT = 8

#--------------------------------------------
gmSECTION_REQUESTS = 9
ID_REQUEST_TYPE = wxNewId()
ID_REQUEST_COMPANY  = wxNewId()
ID_REQUEST_STREET  = wxNewId()
ID_REQUEST_SUBURB  = wxNewId()
ID_REQUEST_PHONE  = wxNewId()
ID_REQUEST_REQUESTS  = wxNewId()
ID_REQUEST_FORMNOTES = wxNewId()
ID_REQUEST_MEDICATIONS = wxNewId()
ID_REQUEST_INCLUDEALLMEDICATIONS  = wxNewId()
ID_REQUEST_COPYTO = wxNewId()
ID_REQUEST_BILL_BB = wxNewId()
ID_REQUEST_BILL_PRIVATE = wxNewId()
ID_REQUEST_BILL_wcover = wxNewId()
ID_REQUEST_BILL_REBATE  = wxNewId()
#---------------------------------------------
gmSECTION_MEASUREMENTS = 10
ID_MEASUREMENT_TYPE = wxNewId()
ID_MEASUREMENT_VALUE = wxNewId()
ID_MEASUREMENT_DATE = wxNewId()
ID_MEASUREMENT_COMMENT = wxNewId()
ID_MEASUREMENT_NEXTVALUE = wxNewId()
ID_MEASUREMENT_GRAPH   = wxNewId()
#---------------------------------------------
gmSECTION_REFERRALS = 11
ID_REFERRAL_CATEGORY        = wxNewId()
ID_REFERRAL_NAME        = wxNewId()
ID_REFERRAL_USEFIRSTNAME        = wxNewId()
ID_REFERRAL_ORGANISATION        = wxNewId()
ID_REFERRAL_HEADOFFICE        = wxNewId()
ID_REFERRAL_STREET1       = wxNewId()
ID_REFERRAL_STREET2        = wxNewId()
ID_REFERRAL_STREET3       = wxNewId()
ID_REFERRAL_SUBURB        = wxNewId()
ID_REFERRAL_POSTCODE        = wxNewId()
ID_REFERRAL_FOR        = wxNewId()
ID_REFERRAL_WPHONE        = wxNewId()
ID_REFERRAL_WFAX        = wxNewId()
ID_REFERRAL_WEMAIL        = wxNewId()
ID_REFERRAL_INCLUDE_MEDICATIONS        = wxNewId()
ID_REFERRAL_INCLUDE_SOCIALHISTORY       = wxNewId()
ID_REFERRAL_INCLUDE_FAMILYHISTORY        = wxNewId()
ID_REFERRAL_INCLUDE_PASTPROBLEMS        = wxNewId()
ID_REFERRAL_ACTIVEPROBLEMS       = wxNewId()
ID_REFERRAL_HABITS        = wxNewId()
ID_REFERRAL_INCLUDEALL        = wxNewId()
ID_BTN_PREVIEW = wxNewId()
ID_REFERRAL_COPYTO = wxNewId()
#----------------------------------------
gmSECTION_RECALLS = 12
ID_RECALLS_TOSEE  = wxNewId()
ID_RECALLS_TXT_FOR  = wxNewId()
ID_RECALLS_TXT_DATEDUE  = wxNewId()
ID_RECALLS_CONTACTMETHOD = wxNewId()
ID_RECALLS_APPNTLENGTH = wxNewId()
ID_RECALLS_TXT_ADDTEXT  = wxNewId()
ID_RECALLS_TXT_INCLUDEFORMS = wxNewId()
ID_RECALLS_TOSEE  = wxNewId()
ID_RECALLS_TXT_FOR  = wxNewId()
ID_RECALLS_TXT_DATEDUE  = wxNewId()
ID_RECALLS_CONTACTMETHOD = wxNewId()
ID_RECALLS_APPNTLENGTH = wxNewId()
ID_RECALLS_TXT_ADDTEXT  = wxNewId()
ID_RECALLS_TXT_INCLUDEFORMS = wxNewId()



PHX_CONDITION=wxNewId()
PHX_NOTES=wxNewId()
PHX_NOTES2=wxNewId()
PHX_LEFT=wxNewId()
PHX_RIGHT=wxNewId()
PHX_BOTH=wxNewId()
PHX_AGE=wxNewId()
PHX_YEAR=wxNewId()
PHX_ACTIVE=wxNewId()
PHX_OPERATION=wxNewId()
PHX_CONFIDENTIAL=wxNewId()
PHX_SIGNIFICANT=wxNewId()
PHX_PROGRESSNOTES=wxNewId()

richards_blue = wxColour(0,0,131)
richards_aqua = wxColour(0,194,197)
richards_dark_gray = wxColor(131,129,131)
richards_light_gray = wxColor(255,255,255)
richards_coloured_gray = wxColor(131,129,131)


CONTROLS_WITHOUT_LABELS =['wxTextCtrl', 'cEditAreaField', 'wxSpinCtrl', 'gmPhraseWheel', 'wxComboBox'] 

basicPrescriptionExtra = [
	None,
	None,
	None,
	("qty", _("Quantity"), wxTextCtrl),
	("rpts", _("Repeats"), wxTextCtrl) ,
	("usual", _("Usual"), wxCheckBox)
	]	

auPrescriptionExtra = [
	None, 
	("vet", _("Veteran"), wxCheckBox) ,
	("reg24", _("Reg 24"), wxCheckBox) ,
	("qty", _("Quantity"), wxSpinCtrl),
	("rpts", _("Repeats"), wxSpinCtrl) ,
	("usual", _("Usual"), wxCheckBox)
	]



auBillingChoices =  [_("bulk bill"), _("private"),  _("concession"), _("workcover") ] 


referralColumn2 = [
	("isByFirstname", _("chums"), wxCheckBox),
	("isHeadOffice", _("head office"), wxCheckBox),
	("W Phone", _("W Phone"), wxTextCtrl),
	("W Fax", _("W Fax  "), wxTextCtrl),
	("W Email", _("W Email"), wxTextCtrl),
	None 
	] 


recallColumn2 = [
	None,
	None,
	None,
	("appt", _("Appointment Type"), wxComboBox),
	("for", _("request for"), wxTextCtrl)
	 ]

requestColumn2 = [
	None,	None, None,
	("phone", _("Phone"), wxTextCtrl ),
	None, None,
	("all meds", _("Include All Meds"), wxCheckBox)
	]


_prompt_defs = {
	'vaccination': [],
	'allergy': [],

	'family history': [
		_("Name"),
		_("Relationship"),
		_("Condition"),
		_("Comment"),
		_("Significance"),
		_("Progress Notes"),
		""
	],
	'past history': [
		_("Condition"),
		_("Notes"),
		_("More Notes"),
		_("Age"),
		_("Year"),
		"" ,
		_("Progress Notes") ,
		""
	]
	,'measurement': [
		_("Type"),
		_("Date"),
		_("Value"),
		_("Comment"),
		_("Progress Notes"), ""
	]
	,"prescription": [
		_("Condition"),
		_("Class"),
		_("Generic"),
		_("Brand"),
		_("Strength"),
		_("Directions"),
		_("For"),
		_("Progress Notes"),
		""
	]
	, "referral": [
		_("Name"),
		_("Organization"),
		_("Street1"),
		_("Street2"),
		_("Suburb"),
		_("Postcode"),
		_("For"),
		_("Include"),
		"",
		""
	]
	, "recall" : [
		_("To See"),
		_("For"),
		_("Date"),
		_("Contact By"),
		_("Include"),
		"",
		_("Include List"),
		_("Instructions"),
		_("Progress Notes"),
		""
	]
	, "request" : [
		_("Type"),
		_("Company"),
		_("Street"),
		_("Suburb"),
		_("Request"),
		_("Notes on form"),
		_("Medications"),
		_("Copy To"),
		_("Progress Notes")	,
		""
	]
}

_known_edit_area_types = []
_known_edit_area_types.extend(_prompt_defs.keys())

def _decorate_editarea_field(widget):
	widget.SetForegroundColour(wxColor(255, 0, 0))
	widget.SetFont(wxFont(12, wxSWISS, wxNORMAL, wxBOLD, False, ''))

#====================================================================
class cEditAreaPopup(wx.wxDialog):
	def __init__ (self, parent, id, title, pos, size, style, name, edit_area = None):
		if not isinstance(edit_area, cEditArea2):
			raise gmExceptions.ConstructorError, '<edit_area> must be of type cEditArea2 but is <%s>' % type(edit_area)
		wx.wxDialog.__init__(self, parent, id, title, pos, size, style, name)
		self.__wxID_BTN_SAVE = wx.wxNewId()
		self.__wxID_BTN_RESET = wx.wxNewId()
		self.__editarea = edit_area
		self.__do_layout()
		self.__register_events()
	#--------------------------------------------------------
	# public API
	#--------------------------------------------------------
	def get_summary(self):
		return self.__editarea.get_summary()
	#--------------------------------------------------------
	def __do_layout(self):
		self.__editarea.Reparent(self)

		self.__btn_SAVE = wx.wxButton(self, self.__wxID_BTN_SAVE, _("Save"))
		self.__btn_SAVE.SetToolTipString(_('save entry into medical record'))
		self.__btn_RESET = wx.wxButton(self, self.__wxID_BTN_RESET, _("Reset"))
		self.__btn_RESET.SetToolTipString(_('reset entry'))
		self.__btn_CANCEL = wx.wxButton(self, wx.wxID_CANCEL, _("Cancel"))
		self.__btn_CANCEL.SetToolTipString(_('discard entry and cancel'))

		szr_buttons = wx.wxBoxSizer(wx.wxHORIZONTAL)
		szr_buttons.Add(self.__btn_SAVE, 1, wx.wxEXPAND | wx.wxALL, 1)
		szr_buttons.Add(self.__btn_RESET, 1, wx.wxEXPAND | wx.wxALL, 1)
		szr_buttons.Add(self.__btn_CANCEL, 1, wx.wxEXPAND | wx.wxALL, 1)

		szr_main = wx.wxBoxSizer(wx.wxVERTICAL)
		szr_main.Add(self.__editarea, 1, wx.wxEXPAND)
		szr_main.Add(szr_buttons, 0, wx.wxEXPAND)

		self.SetSizerAndFit(szr_main)
	#--------------------------------------------------------
	# event handling
	#--------------------------------------------------------
	def __register_events(self):
		# connect standard buttons
		wx.EVT_BUTTON(self.__btn_SAVE, self.__wxID_BTN_SAVE, self._on_SAVE_btn_pressed)
		wx.EVT_BUTTON(self.__btn_RESET, self.__wxID_BTN_RESET, self._on_RESET_btn_pressed)
		wx.EVT_BUTTON(self.__btn_CANCEL, wx.wxID_CANCEL, self._on_CANCEL_btn_pressed)

		wx.EVT_CLOSE(self, self._on_CANCEL_btn_pressed)

		# client internal signals
#		gmDispatcher.connect(signal = gmSignals.activating_patient(), receiver = self._on_activating_patient)
#		gmDispatcher.connect(signal = gmSignals.application_closing(), receiver = self._on_application_closing)
#		gmDispatcher.connect(signal = gmSignals.patient_selected(), receiver = self.on_patient_selected)

		return 1
	#--------------------------------------------------------
	def _on_SAVE_btn_pressed(self, evt):
		if self.__editarea.save_data():
			self.EndModal(wx.wxID_OK)
			return
		short_err = self.__editarea.get_short_error()
		long_err = self.__editarea.get_long_error()
		if (short_err is None) and (long_err is None):
			long_err = _(
				'Unspecified error saving data in edit area.\n\n'
				'Programmer forgot to specify proper error\n'
				'message in [%s].'
			) % self.__editarea.__class__.__name__
		if short_err is not None:
			gmGuiHelpers.gm_beep_statustext(short_err, gmLog.lErr)
		if long_err is not None:
			gmGuiHelpers.gm_show_error(long_err, _('saving clinical data'), gmLog.lErr)
	#--------------------------------------------------------
	def _on_CANCEL_btn_pressed(self, evt):
		self.EndModal(wx.wxID_CANCEL)
	#--------------------------------------------------------
	def _on_RESET_btn_pressed(self, evt):
		self.__editarea.reset_ui()
#====================================================================
class cEditArea2(wxPanel):
	def __init__(self, parent, id, pos, size, style):
		# init main background panel
		wxPanel.__init__ (
			self,
			parent,
			id,
			pos = pos,
			size = size,
			style = style | wxTAB_TRAVERSAL
		)
		self.SetBackgroundColour(wxColor(222,222,222))

		self.data = None		# a placeholder for opaque data
		self.fields = {}
		self.prompts = {}
		self._short_error = None
		self._long_error = None
		self._summary = None

		self._wxID_BTN_OK = wxNewId()
		self._wxID_BTN_Clear = wxNewId()
		self.__do_layout()
		self.__register_events()
		self.Show()
	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def save_data(self):
		self._long_error = _(
			'Cannot save data from edit area.\n\n'
			'Programmer forgot to override method:\n'
			'  <%s.save_data>'
		) % self.__class__.__name__
		return False
	#--------------------------------------------------------
	def reset_ui(self):
		msg = _(
			'Cannot reset fields in edit area.\n\n'
			'Programmer forgot to override method:\n'
			'  <%s.reset_ui>'
		) % self.__class__.__name__
		gmGuiHelpers.gm_show_error(msg, aLogLevel = gmLog.lErr)
	#--------------------------------------------------------
	def get_short_error(self):
		tmp = self._short_error
		self._short_error = None
		return tmp
	#--------------------------------------------------------
	def get_long_error(self):
		tmp = self._long_error
		self._long_error = None
		return tmp
	#--------------------------------------------------------
	def get_summary(self):
		return _('<No embed string for [%s]>') % self.__class__.__name__
	#--------------------------------------------------------
	# event handling
	#--------------------------------------------------------
	def __register_events(self):
		# client internal signals
		gmDispatcher.connect(signal = gmSignals.activating_patient(), receiver = self._on_activating_patient)
		gmDispatcher.connect(signal = gmSignals.application_closing(), receiver = self._on_application_closing)
		gmDispatcher.connect(signal = gmSignals.patient_selected(), receiver = self.on_patient_selected)

		return 1
	#--------------------------------------------------------
	# handlers
	#--------------------------------------------------------
	def _on_OK_btn_pressed(self, event):
		# FIXME: this try: except: block seems to large
		try:
			event.Skip()
			if self.data is None:
				self._save_new_entry()
				self.set_data()
			else:
				self._save_modified_entry()
				self.set_data()
		except gmExceptions.InvalidInputError, err:
			# nasty evil popup dialogue box
			# but for invalid input we want to interrupt user
			try:
				gmGuiHelpers.gm_show_error (err, _("Invalid Input"))
			except:
				_log.LogException ('', sys.exc_info (), verbose = 0)
		except:
			gmLog.gmDefLog.LogException( "save data  problem in [%s]" % self.__class__.__name__, sys.exc_info(), verbose=0)
	#--------------------------------------------------------
	def _on_clear_btn_pressed(self, event):
		# FIXME: check for unsaved data
		self.set_data()
		event.Skip()
	#--------------------------------------------------------
	def on_patient_selected( self, **kwds):
		# remember to use wxCallAfter()
		self.set_data()
	#--------------------------------------------------------
	def _on_application_closing(self, **kwds):
		# remember wxCallAfter
		if not self._patient.is_connected():
			return True
		if self._save_data():
			return True
		_log.Log(gmLog.lErr, '[%s] lossage' % self.__class__.__name__)
		return False
	#--------------------------------------------------------
	def _on_activating_patient(self, **kwds):
		# remember wxCallAfter
		if not self._patient.is_connected():
			return True
		if self._save_data():
			return True
		_log.Log(gmLog.lErr, '[%s] lossage' % self.__class__.__name__)
		return False
	#----------------------------------------------------------------
	# internal helpers
	#----------------------------------------------------------------
	def __do_layout(self):

		# define prompts and fields
		self._define_prompts()
		self._define_fields(parent = self)
		if len(self.fields) != len(self.prompts):
			_log.Log(gmLog.lErr, '[%s]: #fields != #prompts' % self.__class__.__name__)
			return None

		# and generate edit area from it
		szr_main_fgrid = wxFlexGridSizer(rows = len(self.prompts), cols=2)
		color = richards_aqua
		lines = self.prompts.keys()
		lines.sort()
		for line in lines:
			# 1) prompt
			label, color, weight = self.prompts[line]
			# FIXME: style for centering in vertical direction ?
			prompt = wxStaticText (
				parent = self,
				id = -1,
				label = label,
				style = wxALIGN_CENTRE
			)
			# FIXME: resolution dependant
			prompt.SetFont(wxFont(10, wxSWISS, wxNORMAL, wxBOLD, False, ''))
			prompt.SetForegroundColour(color)
			prompt.SetBackgroundColour(richards_light_gray)
			szr_main_fgrid.Add(prompt, flag=wxEXPAND | wxALIGN_RIGHT)

			# 2) widget(s) for line
			szr_line = wxBoxSizer(wxHORIZONTAL)
			positions = self.fields[line].keys()
			positions.sort()
			for pos in positions:
				field, weight = self.fields[line][pos]
#				field.SetBackgroundColour(wxColor(222,222,222))
				szr_line.Add(field, weight, wxEXPAND)
			szr_main_fgrid.Add(szr_line, flag=wxGROW | wxALIGN_LEFT)

		# grid can grow column 1 only, not column 0
		szr_main_fgrid.AddGrowableCol(1)

#		# use sizer for border around everything plus a little gap
#		# FIXME: fold into szr_main_panels ?
#		self.szr_central_container = wxBoxSizer(wxHORIZONTAL)
#		self.szr_central_container.Add(self.szr_main_panels, 1, wxEXPAND | wxALL, 5)

		# and do the layouting
		self.SetSizerAndFit(szr_main_fgrid)
#		self.FitInside()
	#----------------------------------------------------------------
	# intra-class API
	#----------------------------------------------------------------
	def _define_prompts(self):
		"""Child classes override this to define their prompts using _add_prompt()"""
		_log.Log(gmLog.lErr, 'missing override in [%s]' % self.__class__.__name__)
	#----------------------------------------------------------------
	def _add_prompt(self, line, label='missing label', color=richards_blue, weight=0):
		"""Add a new prompt line.

		To be used from _define_fields in child classes.

		- label, the label text
		- color
		- weight, the weight given in sizing the various rows. 0 means the row
		  always has minimum size 
		"""
		self.prompts[line] = (label, color, weight)
	#----------------------------------------------------------------
	def _define_fields(self, parent):
		"""Defines the fields.

		- override in child classes
		- mostly uses _add_field()
		"""
		_log.Log(gmLog.lErr, 'missing override in [%s]' % self.__class__.__name__)
	#----------------------------------------------------------------
	def _add_field(self, line=None, pos=None, widget=None, weight=0):
		if None in (line, pos, widget):
			_log.Log(gmLog.lErr, 'argument error in [%s]: line=%s, pos=%s, widget=%s' % (self.__class__.__name__, line, pos, widget))
		if not self.fields.has_key(line):
			self.fields[line] = {}
		self.fields[line][pos] = (widget, weight)
	#----------------------------------------------------------------
	def _make_standard_buttons(self, parent):
		"""Generates OK/CLEAR buttons for edit area."""
		self.btn_OK = wxButton(parent, self._wxID_BTN_OK, _("OK"))
		self.btn_OK.SetToolTipString(_('save entry into medical record'))
		self.btn_Clear = wxButton(parent, self._wxID_BTN_Clear, _("Clear"))
		self.btn_Clear.SetToolTipString(_('initialize input fields for new entry'))

		szr_buttons = wxBoxSizer(wxHORIZONTAL)
		szr_buttons.Add(self.btn_OK, 1, wxEXPAND | wxALL, 1)
		szr_buttons.Add(5, 0, 0)
		szr_buttons.Add(self.btn_Clear, 1, wxEXPAND | wxALL, 1)

		# connect standard buttons
		EVT_BUTTON(self.btn_OK, self._wxID_BTN_OK, self._on_OK_btn_pressed)
		EVT_BUTTON(self.btn_Clear, self._wxID_BTN_Clear, self._on_clear_btn_pressed)

		return szr_buttons
#====================================================================
#====================================================================
#text control class to be later replaced by the gmPhraseWheel
#--------------------------------------------------------------------
class cEditAreaField(wxTextCtrl):
	def __init__ (self, parent, id = -1, pos = wxDefaultPosition, size=wxDefaultSize):
		wxTextCtrl.__init__(self,parent,id,"",pos, size ,wxSIMPLE_BORDER)
		_decorate_editarea_field(self)
#====================================================================
class cEditArea(wxPanel):
	def __init__(self, parent, id, pos, size, style):

		print "class [%s] is deprecated, use cEditArea2 instead" % self.__class__.__name__

		# init main background panel
		wxPanel.__init__(self, parent, id, pos=pos, size=size, style=wxNO_BORDER | wxTAB_TRAVERSAL)
		self.SetBackgroundColour(wxColor(222,222,222))

		self.data = None
		self.fields = {}
		self.prompts = {}

		self._wxID_BTN_OK = wxNewId()
		self._wxID_BTN_Clear = wxNewId()

		self.__do_layout()

#		self.input_fields = {}

#		self._postInit()
#		self.old_data = {}

		self._patient = gmPerson.gmCurrentPatient()
		self.__register_events()
		self.Show(True)
	#----------------------------------------------------------------
	# internal helpers
	#----------------------------------------------------------------
	def __do_layout(self):
		# define prompts and fields
		self._define_prompts()
		self.fields_pnl = wxPanel(self, -1, style = wxRAISED_BORDER | wxTAB_TRAVERSAL)
		self._define_fields(parent = self.fields_pnl)
		# and generate edit area from it
		szr_prompts = self.__generate_prompts()
		szr_fields = self.__generate_fields()

		# stack prompts and fields horizontally
		self.szr_main_panels = wxBoxSizer(wxHORIZONTAL)
		self.szr_main_panels.Add(szr_prompts, 11, wxEXPAND)
		self.szr_main_panels.Add(5, 0, 0, wxEXPAND)
		self.szr_main_panels.Add(szr_fields, 90, wxEXPAND)

		# use sizer for border around everything plus a little gap
		# FIXME: fold into szr_main_panels ?
		self.szr_central_container = wxBoxSizer(wxHORIZONTAL)
		self.szr_central_container.Add(self.szr_main_panels, 1, wxEXPAND | wxALL, 5)

		# and do the layouting
		self.SetAutoLayout(True)
		self.SetSizer(self.szr_central_container)
		self.szr_central_container.Fit(self)
	#----------------------------------------------------------------
	def __generate_prompts(self):
		if len(self.fields) != len(self.prompts):
			_log.Log(gmLog.lErr, '[%s]: #fields != #prompts' % self.__class__.__name__)
			return None
		# prompts live on a panel
		prompt_pnl = wxPanel(self, -1, wxDefaultPosition, wxDefaultSize, wxSIMPLE_BORDER)
		prompt_pnl.SetBackgroundColour(richards_light_gray)
		# make them
		color = richards_aqua
		lines = self.prompts.keys()
		lines.sort()
		self.prompt_widget = {}
		for line in lines:
			label, color, weight = self.prompts[line]
			self.prompt_widget[line] = self.__make_prompt(prompt_pnl, "%s " % label, color)
		# make shadow below prompts in gray
		shadow_below_prompts = wxWindow(self, -1, wxDefaultPosition, wxDefaultSize, 0)
		shadow_below_prompts.SetBackgroundColour(richards_dark_gray)
		szr_shadow_below_prompts = wxBoxSizer (wxHORIZONTAL)
		szr_shadow_below_prompts.Add(5, 0, 0, wxEXPAND)
		szr_shadow_below_prompts.Add(shadow_below_prompts, 10, wxEXPAND)

		# stack prompt panel and shadow vertically
		vszr_prompts = wxBoxSizer(wxVERTICAL)
		vszr_prompts.Add(prompt_pnl, 97, wxEXPAND)
		vszr_prompts.Add(szr_shadow_below_prompts, 5, wxEXPAND)

		# make shadow to the right of the prompts
		shadow_rightof_prompts = wxWindow(self, -1, wxDefaultPosition, wxDefaultSize, 0)
		shadow_rightof_prompts.SetBackgroundColour(richards_dark_gray)
		szr_shadow_rightof_prompts = wxBoxSizer(wxVERTICAL)
		szr_shadow_rightof_prompts.Add(0,5,0,wxEXPAND)
		szr_shadow_rightof_prompts.Add(shadow_rightof_prompts, 1, wxEXPAND)

		# stack vertical prompt sizer and shadow horizontally
		hszr_prompts = wxBoxSizer(wxHORIZONTAL)
		hszr_prompts.Add(vszr_prompts, 10, wxEXPAND)
		hszr_prompts.Add(szr_shadow_rightof_prompts, 1, wxEXPAND)

		return hszr_prompts
	#----------------------------------------------------------------
	def __generate_fields(self):
		self.fields_pnl.SetBackgroundColour(wxColor(222,222,222))
		# rows, cols, hgap, vgap
		vszr = wxBoxSizer(wxVERTICAL)
		lines = self.fields.keys()
		lines.sort()
		self.field_line_szr = {}
		for line in lines:
			self.field_line_szr[line] = wxBoxSizer(wxHORIZONTAL)
			positions = self.fields[line].keys()
			positions.sort()
			for pos in positions:
				field, weight = self.fields[line][pos]
				self.field_line_szr[line].Add(field, weight, wxEXPAND)
			try:
				vszr.Add(self.field_line_szr[line], self.prompts[line][2], flag = wxEXPAND) # use same lineweight as prompts
			except KeyError:
				_log.Log(gmLog.lErr, "Error with line=%s, self.field_line_szr has key:%s; self.prompts has key: %s" % (line, self.field_line_szr.has_key(line), self.prompts.has_key(line) ) )
		# put them on the panel
		self.fields_pnl.SetSizer(vszr)
		vszr.Fit(self.fields_pnl)

		# make shadow below edit fields in gray
		shadow_below_edit_fields = wxWindow(self, -1, wxDefaultPosition, wxDefaultSize, 0)
		shadow_below_edit_fields.SetBackgroundColour(richards_coloured_gray)
		szr_shadow_below_edit_fields = wxBoxSizer(wxHORIZONTAL)
		szr_shadow_below_edit_fields.Add(5, 0, 0, wxEXPAND)
		szr_shadow_below_edit_fields.Add(shadow_below_edit_fields, 12, wxEXPAND)

		# stack edit fields and shadow vertically
		vszr_edit_fields = wxBoxSizer(wxVERTICAL)
		vszr_edit_fields.Add(self.fields_pnl, 92, wxEXPAND)
		vszr_edit_fields.Add(szr_shadow_below_edit_fields, 5, wxEXPAND)

		# make shadow to the right of the edit area
		shadow_rightof_edit_fields = wxWindow(self, -1, wxDefaultPosition, wxDefaultSize, 0)
		shadow_rightof_edit_fields.SetBackgroundColour(richards_coloured_gray)
		szr_shadow_rightof_edit_fields = wxBoxSizer(wxVERTICAL)
		szr_shadow_rightof_edit_fields.Add(0, 5, 0, wxEXPAND)
		szr_shadow_rightof_edit_fields.Add(shadow_rightof_edit_fields, 1, wxEXPAND)

		# stack vertical edit fields sizer and shadow horizontally
		hszr_edit_fields = wxBoxSizer(wxHORIZONTAL)
		hszr_edit_fields.Add(vszr_edit_fields, 89, wxEXPAND)
		hszr_edit_fields.Add(szr_shadow_rightof_edit_fields, 1, wxEXPAND)

		return hszr_edit_fields
	#---------------------------------------------------------------
	def __make_prompt(self, parent, aLabel, aColor):
		# FIXME: style for centering in vertical direction ?
		prompt = wxStaticText(
			parent,
			-1,
			aLabel,
			style = wxALIGN_RIGHT
		)
		prompt.SetFont(wxFont(10, wxSWISS, wxNORMAL, wxBOLD, False, ''))
		prompt.SetForegroundColour(aColor)
		return prompt
	#----------------------------------------------------------------
	# intra-class API
	#----------------------------------------------------------------
	def _add_prompt(self, line, label='missing label', color=richards_blue, weight=0):
		"""Add a new prompt line.

		To be used from _define_fields in child classes.

		- label, the label text
		- color
		- weight, the weight given in sizing the various rows. 0 means the rwo
		  always has minimum size 
		"""
		self.prompts[line] = (label, color, weight)
	#----------------------------------------------------------------
	def _add_field(self, line=None, pos=None, widget=None, weight=0):
		if None in (line, pos, widget):
			_log.Log(gmLog.lErr, 'argument error in [%s]: line=%s, pos=%s, widget=%s' % (self.__class__.__name__, line, pos, widget))
		if not self.fields.has_key(line):
			self.fields[line] = {}
		self.fields[line][pos] = (widget, weight)
	#----------------------------------------------------------------
	def _define_fields(self, parent):
		"""Defines the fields.

		- override in child classes
		- mostly uses _add_field()
		"""
		_log.Log(gmLog.lErr, 'missing override in [%s]' % self.__class__.__name__)
	#----------------------------------------------------------------
	def _define_prompts(self):
		_log.Log(gmLog.lErr, 'missing override in [%s]' % self.__class__.__name__)
	#----------------------------------------------------------------
	def _make_standard_buttons(self, parent):
		"""Generates OK/CLEAR buttons for edit area."""
		self.btn_OK = wxButton(parent, self._wxID_BTN_OK, _("OK"))
		self.btn_OK.SetToolTipString(_('save entry into medical record'))
		self.btn_Clear = wxButton(parent, self._wxID_BTN_Clear, _("Clear"))
		self.btn_Clear.SetToolTipString(_('initialize input fields for new entry'))

		szr_buttons = wxBoxSizer(wxHORIZONTAL)
		szr_buttons.Add(self.btn_OK, 1, wxEXPAND | wxALL, 1)
		szr_buttons.Add(5, 0, 0)
		szr_buttons.Add(self.btn_Clear, 1, wxEXPAND | wxALL, 1)

		return szr_buttons
	#--------------------------------------------------------
	def _pre_save_data(self):
		pass
	#--------------------------------------------------------
	def _save_data(self):
		_log.Log(gmLog.lErr, '[%s] programmer forgot to define _save_data()' % self.__class__.__name__)
		_log.Log(gmLog.lInfo, 'child classes of cEditArea *must* override this function')
		return False
	#--------------------------------------------------------
	# event handling
	#--------------------------------------------------------
	def __register_events(self):
		# connect standard buttons
		EVT_BUTTON(self.btn_OK, self._wxID_BTN_OK, self._on_OK_btn_pressed)
		EVT_BUTTON(self.btn_Clear, self._wxID_BTN_Clear, self._on_clear_btn_pressed)

		EVT_SIZE (self.fields_pnl, self._on_resize_fields)

		# client internal signals
		gmDispatcher.connect(signal = gmSignals.activating_patient(), receiver = self._on_activating_patient)
		gmDispatcher.connect(signal = gmSignals.application_closing(), receiver = self._on_application_closing)
		gmDispatcher.connect(signal = gmSignals.patient_selected(), receiver = self.on_patient_selected)

		return 1
	#--------------------------------------------------------
	# handlers
	#--------------------------------------------------------
	def _on_OK_btn_pressed(self, event):
		# FIXME: this try: except: block seems to large
		try:
			event.Skip()
			if self.data is None:
				self._save_new_entry()
				self.set_data()
			else:
				self._save_modified_entry()
				self.set_data()
		except gmExceptions.InvalidInputError, err:
			# nasty evil popup dialogue box
			# but for invalid input we want to interrupt user
			try:
				gmGuiHelpers.gm_show_error (err, _("Invalid Input"))
			except:
				_log.LogException ('', sys.exc_info (), verbose = 0)
		except:
			gmLog.gmDefLog.LogException( "save data  problem in [%s]" % self.__class__.__name__, sys.exc_info(), verbose=0)
	#--------------------------------------------------------
	def _on_clear_btn_pressed(self, event):
		# FIXME: check for unsaved data
		self.set_data()
		event.Skip()
	#--------------------------------------------------------
	def on_patient_selected( self, **kwds):
		# remember to use wxCallAfter()
		self.set_data()
	#--------------------------------------------------------
	def _on_application_closing(self, **kwds):
		# remember wxCallAfter
		if not self._patient.is_connected():
			return True
		if self._save_data():
			return True
		_log.Log(gmLog.lErr, '[%s] lossage' % self.__class__.__name__)
		return False
	#--------------------------------------------------------
	def _on_activating_patient(self, **kwds):
		# remember wxCallAfter
		if not self._patient.is_connected():
			return True
		if self._save_data():
			return True
		_log.Log(gmLog.lErr, '[%s] lossage' % self.__class__.__name__)
		return False
	#--------------------------------------------------------
	def _on_resize_fields (self, event):
		self.fields_pnl.Layout()
		# resize the prompts accordingly
		for i in self.field_line_szr.keys():
			# query the BoxSizer to find where the field line is
			pos = self.field_line_szr[i].GetPosition()
			# and set the prompt lable to the same Y position
			self.prompt_widget[i].SetPosition((0, pos.y))
#====================================================================
class gmEditArea(cEditArea):
	def __init__(self, parent, id, aType = None):

		print "class [%s] is deprecated, use cEditArea2 instead" % self.__class__.__name__

		# sanity checks
		if aType not in _known_edit_area_types:
			_log.Log(gmLog.lErr, 'unknown edit area type: [%s]' % aType)
			raise gmExceptions.ConstructorError, 'unknown edit area type: [%s]' % aType
		self._type = aType

		# init main background panel
		cEditArea.__init__(self, parent, id)

		self.input_fields = {}

		self._postInit()
		self.old_data = {}

		self._patient = gmPerson.gmCurrentPatient()
		self.Show(True)
	#----------------------------------------------------------------
	# internal helpers
	#----------------------------------------------------------------
	#----------------------------------------------------------------
	# to be obsoleted
	#----------------------------------------------------------------
	def __make_prompts(self, prompt_labels):
		# prompts live on a panel
		prompt_pnl = wxPanel(self, -1, wxDefaultPosition, wxDefaultSize, wxSIMPLE_BORDER)
		prompt_pnl.SetBackgroundColour(richards_light_gray)
		# make them
		gszr = wxFlexGridSizer (len(prompt_labels)+1, 1, 2, 2)
		color = richards_aqua
		for prompt in prompt_labels:
			label = self.__make_prompt(prompt_pnl, "%s " % prompt, color)
			gszr.Add(label, 0, wxEXPAND | wxALIGN_RIGHT)
			color = richards_blue
			gszr.RemoveGrowableRow (line-1)
		# put sizer on panel
		prompt_pnl.SetSizer(gszr)
		gszr.Fit(prompt_pnl)
		prompt_pnl.SetAutoLayout(True)

		# make shadow below prompts in gray
		shadow_below_prompts = wxWindow(self, -1, wxDefaultPosition, wxDefaultSize, 0)
		shadow_below_prompts.SetBackgroundColour(richards_dark_gray)
		szr_shadow_below_prompts = wxBoxSizer (wxHORIZONTAL)
		szr_shadow_below_prompts.Add(5, 0, 0, wxEXPAND)
		szr_shadow_below_prompts.Add(shadow_below_prompts, 10, wxEXPAND)

		# stack prompt panel and shadow vertically
		vszr_prompts = wxBoxSizer(wxVERTICAL)
		vszr_prompts.Add(prompt_pnl, 97, wxEXPAND)
		vszr_prompts.Add(szr_shadow_below_prompts, 5, wxEXPAND)

		# make shadow to the right of the prompts
		shadow_rightof_prompts = wxWindow(self, -1, wxDefaultPosition, wxDefaultSize, 0)
		shadow_rightof_prompts.SetBackgroundColour(richards_dark_gray)
		szr_shadow_rightof_prompts = wxBoxSizer(wxVERTICAL)
		szr_shadow_rightof_prompts.Add(0,5,0,wxEXPAND)
		szr_shadow_rightof_prompts.Add(shadow_rightof_prompts,1,wxEXPAND)

		# stack vertical prompt sizer and shadow horizontally
		hszr_prompts = wxBoxSizer(wxHORIZONTAL)
		hszr_prompts.Add(vszr_prompts, 10, wxEXPAND)
		hszr_prompts.Add(szr_shadow_rightof_prompts, 1, wxEXPAND)

		return hszr_prompts
	#----------------------------------------------------------------
	def _make_edit_lines(self, parent):
		_log.Log(gmLog.lErr, 'programmer forgot to define edit area lines for [%s]' % self._type)
		_log.Log(gmLog.lInfo, 'child classes of gmEditArea *must* override this function')
		return []
	#----------------------------------------------------------------
	def __make_editing_area(self):
		# make edit fields
		fields_pnl = wxPanel(self, -1, wxDefaultPosition, wxDefaultSize, style = wxRAISED_BORDER | wxTAB_TRAVERSAL)
		fields_pnl.SetBackgroundColour(wxColor(222,222,222))
		# rows, cols, hgap, vgap
		gszr = wxGridSizer(len(_prompt_defs[self._type]), 1, 2, 2)

		# get lines
		lines = self._make_edit_lines(parent = fields_pnl)

		self.lines = lines
		if len(lines) != len(_prompt_defs[self._type]):
			_log.Log(gmLog.lErr, '#(edit lines) not equal #(prompts) for [%s], something is fishy' % self._type)
		for line in lines:
			gszr.Add(line, 0, wxEXPAND | wxALIGN_LEFT)
		# put them on the panel
		fields_pnl.SetSizer(gszr)
		gszr.Fit(fields_pnl)
		fields_pnl.SetAutoLayout(True)

		# make shadow below edit fields in gray
		shadow_below_edit_fields = wxWindow(self, -1, wxDefaultPosition, wxDefaultSize, 0)
		shadow_below_edit_fields.SetBackgroundColour(richards_coloured_gray)
		szr_shadow_below_edit_fields = wxBoxSizer(wxHORIZONTAL)
		szr_shadow_below_edit_fields.Add(5, 0, 0, wxEXPAND)
		szr_shadow_below_edit_fields.Add(shadow_below_edit_fields, 12, wxEXPAND)

		# stack edit fields and shadow vertically
		vszr_edit_fields = wxBoxSizer(wxVERTICAL)
		vszr_edit_fields.Add(fields_pnl, 92, wxEXPAND)
		vszr_edit_fields.Add(szr_shadow_below_edit_fields, 5, wxEXPAND)

		# make shadow to the right of the edit area
		shadow_rightof_edit_fields = wxWindow(self, -1, wxDefaultPosition, wxDefaultSize, 0)
		shadow_rightof_edit_fields.SetBackgroundColour(richards_coloured_gray)
		szr_shadow_rightof_edit_fields = wxBoxSizer(wxVERTICAL)
		szr_shadow_rightof_edit_fields.Add(0, 5, 0, wxEXPAND)
		szr_shadow_rightof_edit_fields.Add(shadow_rightof_edit_fields, 1, wxEXPAND)

		# stack vertical edit fields sizer and shadow horizontally
		hszr_edit_fields = wxBoxSizer(wxHORIZONTAL)
		hszr_edit_fields.Add(vszr_edit_fields, 89, wxEXPAND)
		hszr_edit_fields.Add(szr_shadow_rightof_edit_fields, 1, wxEXPAND)

		return hszr_edit_fields

	def set_old_data( self, map):
		self.old_data = map

	def _default_init_fields(self):
		#self.dirty = 0  #this flag is for patient_activating event to save any unsaved entries
		self.setInputFieldValues( self._get_init_values())
		self.data = None

	def _get_init_values(self):
		map = {}
		for k in self.input_fields.keys():
			map[k] = ''
		return map	

	#--------------------------------------------------------
	def _init_fields(self):
		self._default_init_fields()

	#	_log.Log(gmLog.lErr, 'programmer forgot to define _init_fields() for [%s]' % self._type)
	#	_log.Log(gmLog.lInfo, 'child classes of gmEditArea *must* override this function')
	#	raise AttributeError
#-------------------------------------------------------------------------------------------------------------
	def _updateUI(self):
		_log.Log(gmLog.lWarn, "you may want to override _updateUI for [%s]" % self.__class__.__name__)


	def _postInit(self):
		"""override for further control setup"""
		pass


	def _makeLineSizer(self,  widget, weight, spacerWeight):
		szr = wxBoxSizer(wxHORIZONTAL)
		szr.Add( widget, weight, wxEXPAND)
		szr.Add( 0,0, spacerWeight, wxEXPAND)
		return szr

	def _makeCheckBox(self, parent, title):
		
		cb =  wxCheckBox( parent, -1, _(title))
		cb.SetForegroundColour( richards_blue)
		return cb


	
	def _makeExtraColumns(self , parent, lines, weightMap = {} ):
		"""this is a utlity method to add extra columns"""
		#add an extra column if the class has attribute "extraColumns"
		if self.__class__.__dict__.has_key("extraColumns"):
			for x in self.__class__.extraColumns:
				lines = self._addColumn(parent, lines, x, weightMap)
		return lines
	


	def _addColumn(self, parent, lines, extra, weightMap = {}, existingWeight = 5 , extraWeight = 2):
		"""
		# add ia extra column in the edit area. 
		# preconditions: 
		#	parent is fields_pnl (weak);  
		#	self.input_fields exists (required); 
		# 	; extra is a list  of tuples of  format -
			# (	key for input_fields, widget label , widget class to instantiate ) 
		"""
		
		newlines = []
		i = 0
		for x in lines:
			# adjust weight if line has specific weightings.
			if weightMap.has_key( x):
				(existingWeight, extraWeight) = weightMap[x]

			szr = wxBoxSizer(wxHORIZONTAL)
			szr.Add( x, existingWeight, wxEXPAND)
			if i < len(extra) and  extra[i] <> None:
				
				(inputKey, widgetLabel, aclass) = extra[i]
				if aclass.__name__ in CONTROLS_WITHOUT_LABELS:
					szr.Add( self._make_prompt(parent,  widgetLabel, richards_blue)  )
					widgetLabel = ""

					
				w = aclass( parent, -1, widgetLabel)
				if not aclass.__name__ in CONTROLS_WITHOUT_LABELS:
					w.SetForegroundColour(richards_blue)
				
				szr.Add(w, extraWeight , wxEXPAND)

				# make sure the widget is locatable via input_fields
				self.input_fields[inputKey] = w
				
			newlines.append(szr)
			i += 1
		return newlines	

	def setInputFieldValues(self, map, id = None ):
		#self.monitoring_dirty = 0
		for k,v in map.items():
			field = self.input_fields.get(k, None)
			if field == None:
				continue
			try:
				field.SetValue( str(v) )
			except:
				try:
					if type(v) == type(''):
						v = 0

					field.SetValue( v)
				except:
					pass
		self.setDataId(id)
		#self.monitoring_dirty = 1
		self.set_old_data(self.getInputFieldValues())
	
	def getDataId(self):
		return self.data 

	def setDataId(self, id):
		self.data = id
	

	def _getInputFieldValues(self):
		values = {}
		for k,v  in self.input_fields.items():
			values[k] = v.GetValue()
		return values	

	def getInputFieldValues(self, fields = None):
		if fields == None:
			fields = self.input_fields.keys()
		values = {}
		for f in fields:
			try:
				values[f] = self.input_fields[f].GetValue()
			except:
				pass
		return values		
#====================================================================
class gmFamilyHxEditArea(gmEditArea):
	def __init__(self, parent, id):
		try:
			gmEditArea.__init__(self, parent, id, aType = 'family history')
		except gmExceptions.ConstructorError:
			_log.LogExceptions('cannot instantiate family Hx edit area', sys.exc_info(),4)
			raise
	#----------------------------------------------------------------
	def _make_edit_lines(self, parent):
		_log.Log(gmLog.lData, "making family Hx lines")
		lines = []
		self.input_fields = {}
		# line 1
		# FIXME: put patient search widget here, too ...
		# add button "make active patient"
		self.input_fields['name'] = cEditAreaField(parent, -1, wxDefaultPosition, wxDefaultSize)
		self.input_fields['DOB'] = cEditAreaField(parent, -1, wxDefaultPosition, wxDefaultSize)
		lbl_dob = self._make_prompt(parent, _(" Date of Birth "), richards_blue)
		szr = wxBoxSizer(wxHORIZONTAL)
		szr.Add(self.input_fields['name'], 4, wxEXPAND)
		szr.Add(lbl_dob, 2, wxEXPAND)
		szr.Add(self.input_fields['DOB'], 4, wxEXPAND)
		lines.append(szr)
		# line 2
		# FIXME: keep relationship attachments permamently ! (may need to make new patient ...)
		# FIXME: learning phrasewheel attached to list loaded from backend
		self.input_fields['relationship'] = cEditAreaField(parent, -1, wxDefaultPosition, wxDefaultSize)
		szr = wxBoxSizer(wxHORIZONTAL)
		szr.Add(self.input_fields['relationship'], 4, wxEXPAND)
		lines.append(szr)
		# line 3
		self.input_fields['condition'] = cEditAreaField(parent, -1, wxDefaultPosition, wxDefaultSize)
		self.cb_condition_confidential = wxCheckBox(parent, -1, _("confidental"), wxDefaultPosition, wxDefaultSize, wxNO_BORDER)
		szr = wxBoxSizer(wxHORIZONTAL)
		szr.Add(self.input_fields['condition'], 6, wxEXPAND)
		szr.Add(self.cb_condition_confidential, 0, wxEXPAND)
		lines.append(szr)
		# line 4
		self.input_fields['comment'] = cEditAreaField(parent, -1, wxDefaultPosition, wxDefaultSize)
		lines.append(self.input_fields['comment'])
		# line 5
		lbl_onset = self._make_prompt(parent, _(" age onset "), richards_blue)
		self.input_fields['age onset'] = cEditAreaField(parent, -1, wxDefaultPosition, wxDefaultSize)
		#    FIXME: combo box ...
		lbl_caused_death = self._make_prompt(parent, _(" caused death "), richards_blue)
		self.input_fields['caused death'] = cEditAreaField(parent, -1, wxDefaultPosition, wxDefaultSize)
		lbl_aod = self._make_prompt(parent, _(" age died "), richards_blue)
		self.input_fields['AOD'] = cEditAreaField(parent, -1, wxDefaultPosition, wxDefaultSize)
		szr = wxBoxSizer(wxHORIZONTAL)
		szr.Add(lbl_onset, 0, wxEXPAND)
		szr.Add(self.input_fields['age onset'], 1,wxEXPAND)
		szr.Add(lbl_caused_death, 0, wxEXPAND)
		szr.Add(self.input_fields['caused death'], 2,wxEXPAND)
		szr.Add(lbl_aod, 0, wxEXPAND)
		szr.Add(self.input_fields['AOD'], 1, wxEXPAND)
		szr.Add(2, 2, 8)
		lines.append(szr)
		# line 6
		self.input_fields['progress notes'] = cEditAreaField(parent, -1, wxDefaultPosition, wxDefaultSize)
		lines.append(self.input_fields['progress notes'])
		# line 8
		self.Btn_next_condition = wxButton(parent, -1, _("Next Condition"))
		szr = wxBoxSizer(wxHORIZONTAL)
		szr.AddSpacer(10, 0, 0)
		szr.Add(self.Btn_next_condition, 0, wxEXPAND | wxALL, 1)
		szr.Add(2, 1, 5)
		szr.Add(self._make_standard_buttons(parent), 0, wxEXPAND)
		lines.append(szr)

		return lines

	def _save_data(self):
		return 1

#====================================================================
class gmPastHistoryEditArea(gmEditArea):

	def __init__(self, parent, id):
		gmEditArea.__init__(self, parent, id, aType = 'past history')

	def _define_prompts(self):
		self._add_prompt(line = 1, label = _("When Noted"))
		self._add_prompt(line = 2, label = _("Laterality"))
		self._add_prompt(line = 3, label = _("Condition"))
		self._add_prompt(line = 4, label = _("Notes"))
		self._add_prompt(line = 6, label = _("Status"))
		self._add_prompt(line = 7, label = _("Progress Note"))
		self._add_prompt(line = 8, label = '')
	#--------------------------------------------------------
	def _define_fields(self, parent):
		# line 1
		self.fld_date_noted = gmDateTimeInput.gmDateInput(
			parent = parent,
			id = -1,
			style = wxSIMPLE_BORDER
		)
		self._add_field(
			line = 1,
			pos = 1,
			widget = self.fld_date_noted,
			weight = 2
		)
		self._add_field(
			line = 1, 
			pos = 2,
			widget = cPrompt_edit_area(parent,-1, _("Age")),
			weight = 0)

		self.fld_age_noted = cEditAreaField(parent)	
		self._add_field(
			line = 1,
			pos = 3,
			widget = self.fld_age_noted,
			weight = 2
		)
		
		# line 2
		self.fld_laterality_none= wxRadioButton(parent, -1, _("N/A"))
		self.fld_laterality_left= wxRadioButton(parent, -1, _("L"))
		self.fld_laterality_right= wxRadioButton(parent, -1, _("R"))
		self.fld_laterality_both= wxRadioButton(parent, -1, _("both"))
		self._add_field(
			line = 2,
			pos = 1,
			widget = self.fld_laterality_none,
			weight = 0
		)
		self._add_field(
			line = 2,
			pos = 2,
			widget = self.fld_laterality_left,
			weight = 0
		)
		self._add_field(
			line = 2,
			pos = 3,
			widget = self.fld_laterality_right,
			weight = 1
		)
		self._add_field(
			line = 2,
			pos = 4,
			widget = self.fld_laterality_both,
			weight = 1
		)
		# line 3
		self.fld_condition= cEditAreaField(parent)
		self._add_field(
			line = 3,
			pos = 1,
			widget = self.fld_condition,
			weight = 6
		)
		# line 4
		self.fld_notes= cEditAreaField(parent)
		self._add_field(
			line = 4,
			pos = 1,
			widget = self.fld_notes,
			weight = 6
		)
		# line 5
		self.fld_significant= wxCheckBox(
			parent,
			-1,
			_("significant"),
			style = wxNO_BORDER
		)
		self.fld_active= wxCheckBox(
			parent,
			-1,
			_("active"),
			style = wxNO_BORDER
		)

		self._add_field(
			line = 5,
			pos = 1,
			widget = self.fld_significant,
			weight = 0
		)
		self._add_field(
			line = 5,
			pos = 2,
			widget = self.fld_active,
			weight = 0
		)
		#line 6
		self.fld_progress= cEditAreaField(parent)
		self._add_field(
			line = 6,
			pos = 1,
			widget = self.fld_progress,
			weight = 6
		)

		#line 7
		self._add_field(
			line = 7,
			pos = 4,
			widget = self._make_standard_buttons(parent),
			weight = 2
		)
	#--------------------------------------------------------
	def  _postInit(self):
		return
		#handling of auto age or year filling.
		EVT_KILL_FOCUS( self.fld_age_noted, self._ageKillFocus)
		EVT_KILL_FOCUS( self.fld_date_noted, self._yearKillFocus)
	#--------------------------------------------------------
	def _ageKillFocus( self, event):	
		# skip first, else later failure later in block causes widget to be unfocusable
		event.Skip()	
		try :
			year = self._getBirthYear() + int(self.fld_age_noted.GetValue().strip() )
			self.fld_date_noted.SetValue( str (year) )
		except:
			pass

	def _getBirthYear(self):
		try:
			birthyear = int(str(self._patient.get_identity().getDOB()).split('-')[0]) 
		except:
			birthyear = time.localtime()[0]
		
		return birthyear
		
	def _yearKillFocus( self, event):	
		event.Skip()	
		try:
			age = int(self.fld_date_noted.GetValue().strip() ) - self._getBirthYear() 
			self.fld_age_noted.SetValue( str (age) )
		except:
			pass

	__init_values = {
			"condition": "",
			"notes1": "",
			"notes2": "",
			"age": "",
			"year": str(time.localtime()[0]),
			"progress": "",
			"active": 1,
			"operation": 0,
			"confidential": 0,
			"significant": 1,
			"both": 0,
			"left": 0,
			"right": 0,
			"none" : 1
			}

	def _getDefaultAge(self):
		try:
			return	time.localtime()[0] - self._patient.get_identity().getBirthYear()
		except:
			return 0

	def _get_init_values(self):
		values = gmPastHistoryEditArea.__init_values
		values["age"] = str( self._getDefaultAge())
		return values 
		
		
	def _save_data(self):
		clinical = self._patient.get_clinical_record().get_past_history()
		if self.getDataId() is None:
			id = clinical.create_history( self.get_fields_formatting_values() )
			self.setDataId(id)
			return

		clinical.update_history( self.get_fields_formatting_values(), self.getDataId() )

#====================================================================
class gmReferralEditArea(gmEditArea):
		
	def __init__(self, parent, id): 
		try:
			gmEditArea.__init__(self, parent, id, aType = 'referral')
		except gmExceptions.ConstructorError:
			_log.LogException('cannot instantiate referral edit area', sys.exc_info(), verbose=0)
		self.data = None # we don't use this in this widget
		self.recipient = None

	def _define_prompts(self):
		self._add_prompt (line = 1, label = _ ("Specialty"))
		self._add_prompt (line = 2, label = _ ("Name"))
		self._add_prompt (line = 3, label = _ ("Address"))
		self._add_prompt (line = 4, label = _ ("Options"))
		self._add_prompt (line = 5, label = _("Text"), weight =6)
		self._add_prompt (line = 6, label = "")

	def _define_fields (self, parent):
		self.fld_specialty = gmPhraseWheel.cPhraseWheel (
			parent = parent,
			id = -1,
			aMatchProvider = gmDemographicRecord.OccupationMP (),
			style = wxSIMPLE_BORDER
			)
		#_decorate_editarea_field (self.fld_specialty)
		self._add_field (
			line = 1,
			pos = 1,
			widget = self.fld_specialty,
			weight = 1
			)
		self.fld_name = gmPhraseWheel.cPhraseWheel (
			parent = parent,
			id = -1,
			aMatchProvider = gmDemographicRecord.NameMP (),
			style = wxSIMPLE_BORDER
			)
		#_decorate_editarea_field (self.fld_name)
		self._add_field (
			line = 2,
			pos = 1,
			widget = self.fld_name,
			weight = 1
			)
		self.fld_address = wxComboBox (parent, -1, style = wxCB_READONLY)
		#_decorate_editarea_field (self.fld_address)
		self._add_field (
			line = 3,
			pos = 1,
			widget = self.fld_address,
			weight = 1
			)
		self.fld_specialty.setDependent (self.fld_name, "occupation")
		self.fld_name.addCallback (self.setAddresses)
		# flags line
		self.fld_med = wxCheckBox (parent, -1, _("Meds"), style=wxNO_BORDER)
		self._add_field (
			line = 4,
			pos = 1,
			widget = self.fld_med,
			weight = 1
			)
		self.fld_past = wxCheckBox (parent, -1, _("Past Hx"), style=wxNO_BORDER)
		self._add_field (
			line = 4,
			pos = 4,
			widget = self.fld_past,
			weight = 1
			)
		self.fld_text = wxTextCtrl (parent, -1, style= wxTE_MULTILINE)
		self._add_field (
			line = 5,
			pos = 1,
			widget = self.fld_text,
			weight = 1)
		# final line
		self._add_field(
			line = 6,
			pos = 1,
			widget = self._make_standard_buttons(parent),
			weight = 1
		)
		return 1

	def set_data (self):
		"""
		Doesn't accept any value as this doesn't make sense for this edit area
		"""
		self.fld_specialty.SetValue ('')
		self.fld_name.SetValue ('')
		self.fld_address.Clear ()
		self.fld_address.SetValue ('')
		self.fld_med.SetValue (0)
		self.fld_past.SetValue (0)
		self.fld_text.SetValue ('')
		self.recipient = None

	def setAddresses (self, id):
		"""
		Set the available addresses for the selected identity
		"""
		if id is None:
			self.recipient = None
			self.fld_address.Clear ()
			self.fld_address.SetValue ('')
		else:
			self.recipient = gmDemographicRecord.cDemographicRecord_SQL (id)
			self.fld_address.Clear ()
			self.addr = self.recipient.getAddresses ('work')
			for i in self.addr:
				self.fld_address.Append (_("%(number)s %(street)s, %(urb)s %(postcode)s") % i, ('post', i))
			fax = self.recipient.getCommChannel (gmDemographicRecord.FAX)
			email  = self.recipient.getCommChannel (gmDemographicRecord.EMAIL)
			if fax:
				self.fld_address.Append ("%s: %s" % (_("FAX"), fax), ('fax', fax))
			if email:
				self.fld_address.Append ("%s: %s" % (_("E-MAIL"), email), ('email', email))

	def _save_new_entry(self):
		"""
		We are always saving a "new entry" here because data_ID is always None
		"""
		if not self.recipient:
			raise gmExceptions.InvalidInputError(_('must have a recipient'))
		if self.fld_address.GetSelection() == -1:
			raise gmExceptions.InvalidInputError(_('must select address'))
		channel, addr = self.fld_address.GetClientData (self.fld_address.GetSelection())
		text = self.fld_text.GetValue()
		flags = {}
		flags['meds'] = self.fld_med.GetValue()
		flags['pasthx'] = self.fld_past.GetValue()
		if not gmReferral.create_referral (self._patient, self.recipient, channel, addr, text, flags):
			raise gmExceptions.InvalidInputError('error sending form')

#====================================================================
#====================================================================
# unconverted edit areas below
#====================================================================
class gmMeasurementEditArea(gmEditArea):

	T= 'type'
	D= 'date'
	V= 'value'
	C= 'comment'
	P= 'progress_notes'
	def __init__(self, parent, id):
		try:
			gmEditArea.__init__(self, parent, id, aType = 'measurement')
		except gmExceptions.ConstructorError:
			stacktrace()

			_log.LogExceptions('cannot instantiate measurement edit area', sys.exc_info(),4)
			raise


	#----------------------------------------------------------------
	def _make_edit_lines(self, parent):
		_log.Log(gmLog.lData, "making measurement lines")
		lines = []
		self.txt_type = cEditAreaField(parent)
		self.txt_date = cEditAreaField(parent)
		self.txt_value = cEditAreaField(parent)
		self.txt_comment = cEditAreaField(parent)
		self.txt_progressnotes= cEditAreaField(parent)
		
		lines.append(self.txt_type)
		lines.append(self.txt_date)
		lines.append(self.txt_value)
		lines.append(self.txt_comment)
		lines.append(self.txt_progressnotes)
		lines.append(self._make_standard_buttons(parent))

		c = gmMeasurementEditArea
		self.input_fields = {
			c.T : self.txt_type,
			c.D : self.txt_date ,
			c.V : self.txt_value,
			c.C : self.txt_comment,
			c.P : self.txt_progressnotes
		}

		return lines

	def get_field_formatting_values(self):
		c = gmMeasurementEditArea
		fields = [ c.T, c.D, c.V, c.C, c.P , 'id_measurement']
		values = self.getInputFieldValues(fields)
		s , n = "'%s'", "%d"
		formatting =  { c.T:s, c.D:s, c.V:n, c.C:s, c.P:s }
		values['id_measurement'] = self.getDataId()
		return fields, formatting, values

	def _save_data(self):
		return 1


#====================================================================
class gmPrescriptionEditArea(gmEditArea):
	def __init__(self, parent, id):
		try:
			gmEditArea.__init__(self, parent, id, aType = 'prescription')
		except gmExceptions.ConstructorError:
			stacktrace()

			_log.LogExceptions('cannot instantiate prescription edit area', sys.exc_info(),4)
			raise


	#----------------------------------------------------------------
	def _make_edit_lines(self, parent):
		_log.Log(gmLog.lData, "making prescription lines")
		lines = []
		self.txt_problem = cEditAreaField(parent)
		self.txt_class = cEditAreaField(parent)
		self.txt_generic = cEditAreaField(parent)
		self.txt_brand = cEditAreaField(parent)
		self.txt_strength= cEditAreaField(parent)
		self.txt_directions= cEditAreaField(parent)
		self.txt_for = cEditAreaField(parent)
		self.txt_progress = cEditAreaField(parent)
		
		lines.append(self.txt_problem)
		lines.append(self.txt_class)
		lines.append(self.txt_generic)
		lines.append(self.txt_brand)
		lines.append(self.txt_strength)
		lines.append(self.txt_directions)
		lines.append(self.txt_for)
		lines.append(self.txt_progress)
		lines.append(self._make_standard_buttons(parent))
		self.input_fields = {
			"problem": self.txt_problem,
			"class" : self.txt_class,
			"generic" : self.txt_generic,
			"brand" : self.txt_brand,
			"strength": self.txt_strength,
			"directions": self.txt_directions,
			"for" : self.txt_for,
			"progress": self.txt_progress

		}

		return self._makeExtraColumns( parent, lines)


# This makes gmPrescriptionEditArea more adaptable to different nationalities special requirements.
# ( well, it could be.)
# to change at runtime, do 

#             gmPrescriptionEditArea.extraColumns  = [ one or more columnListInfo ]  

#    each columnListInfo  element describes one column,
#    where columnListInfo is    a  list of 
#  		tuples of 	[ inputMap name,  widget label, widget class to instantiate from]

#gmPrescriptionEditArea.extraColumns = [  basicPrescriptionExtra ]
#gmPrescriptionEditArea.extraColumns = [  auPrescriptionExtra ]
	
	
	def _save_data(self):
		return 1

#====================================================================
class gmRecallEditArea(gmEditArea):
	extraColumns = [recallColumn2	]
	def __init__(self, parent, id):
		try:
			gmEditArea.__init__(self, parent, id, aType = 'recall')
		except gmExceptions.ConstructorError:
			stacktrace()

			_log.LogExceptions('cannot instantiate recall edit area', sys.exc_info(),4)
			raise
	
	

	#----------------------------------------------------------------
	def _make_edit_lines(self, parent):
		_log.Log(gmLog.lData, "making recall lines")
		lines = []
		self.txt_tosee = cEditAreaField(parent)
		self.txt_for = cEditAreaField(parent)
		self.txt_date = cEditAreaField(parent)
		self.txt_contactBy = wxComboBox(parent, -1)
		self.txt_testType= wxComboBox(parent , -1)
		self.txt_includeList = cEditAreaField(parent)
		self.txt_instructions = cEditAreaField(parent)
		self.txt_progress = cEditAreaField(parent)
		buttonAddTest = wxButton(parent, -1, _("add tests") )
		buttonDelTest = wxButton(parent, -1, _("delete tests") )
		lines.append(self.txt_tosee)
		lines.append(self.txt_for)
		lines.append(self.txt_date)
		lines.append(self.txt_contactBy)
		lines.append(self.txt_testType)

		szr = wxBoxSizer(wxHORIZONTAL)
		szr.Add( buttonAddTest, 0, 0)
		szr.Add( buttonDelTest, 0, 0)
		lines.append( szr)
		
		lines.append(self.txt_includeList)
		lines.append(self.txt_instructions)
		lines.append(self.txt_progress)
		lines.append(self._make_standard_buttons(parent))
		self.input_fields = {
		        "providers": self.txt_tosee
			,"for"	 :self.txt_for
			, "date"	: self.txt_date
			,"contact": self.txt_contactBy
			, "testType": self.txt_testType
			, "addTest" : buttonAddTest
			, "delTest" : buttonDelTest
			, "includeList": self.txt_includeList
			, "instructions": self.txt_instructions
			, "progress" : self.txt_progress

		}

		weightMap = {self.txt_testType : ( 1, 2) }

		return self._makeExtraColumns( parent, lines, weightMap)

	def _save_data(self):
		return 1


class gmRequestEditArea(gmEditArea):
	extraColumns = [requestColumn2	]

	def __init__(self, parent, id):
		try:
			gmEditArea.__init__(self, parent, id, aType = 'request')
		except gmExceptions.ConstructorError:
			stacktrace()

			_log.LogExceptions('cannot instantiate request edit area', sys.exc_info(),4)
			raise

	def _makeRadioButtons( self, parent, choices):
		szr = wxBoxSizer(wxHORIZONTAL)
		
		for x in choices:
			w = wxRadioButton(parent, -1, x)
			szr.Add(w)
			self.input_fields[x] = w
		return szr	

	#----------------------------------------------------------------
	def _make_edit_lines(self, parent):
		_log.Log(gmLog.lData, "making request lines")
		lines = []
		atype = cEditAreaField(parent)
		company = cEditAreaField(parent)
		street = cEditAreaField(parent)
		urb = cEditAreaField(parent)
		#phone = cEditAreaField(parent)
		request = cEditAreaField(parent)
		notes = cEditAreaField(parent)
		meds = cEditAreaField(parent)
		#all_meds = self._makeCheckBox(parent,"Include All Meds")
		copyto = cEditAreaField(parent)
		progress = cEditAreaField(parent)
		if not self.__class__.__dict__.has_key('billingChoices'):
			self.__class__.__dict__['billingChoices'] = auBillingChoices
		billings = self._makeRadioButtons( parent,  choices = self.__class__.billingChoices)
		#lines.append(self.fld_disease_sched)

		
		lines.append(atype)

		lines.append(company)
		lines.append(street)
 		lines.append(urb)

		lines.append(request)
		lines.append(notes)
		

		lines.append(meds)
		lines.append(copyto)
		lines.append(progress)
		#lines.append(billings)
		szr = wxBoxSizer(wxHORIZONTAL)
		szr.Add(billings, 2, wxEXPAND)
		
		szr.Add(self._make_standard_buttons(parent), 1, wxEXPAND)
		lines.append(szr)
		#lines.append(self._make_standard_buttons(parent))
		self.input_fields = {
			"type":  atype,
			"company":company,
			"street": street,
			"urb": urb,
			"request": request,
			"notes": notes,
			"meds" : meds,
			"copyto" : copyto,
			"progress" : progress
		}

		return self._makeExtraColumns( parent, lines )

#gmRequestEditArea.billingChoices = auBillingChoices
	
	
	def _save_data(self):
		return 1

#====================================================================
# old style stuff below
#====================================================================
#Class which shows a blue bold label left justified
#--------------------------------------------------------------------
class cPrompt_edit_area(wxStaticText):
	def __init__(self, parent, id, prompt, aColor = richards_blue):
		wxStaticText.__init__(self, parent, id, prompt, wxDefaultPosition, wxDefaultSize, wxALIGN_LEFT)
		self.SetFont(wxFont(10, wxSWISS, wxNORMAL, wxBOLD, False, ''))
		self.SetForegroundColour(aColor)
#====================================================================
# create the editorprompts class which expects a dictionary of labels
# passed to it with prompts relevant to the editing area.
# remove the if else from this once the edit area labelling is fixed
#--------------------------------------------------------------------
class gmPnlEditAreaPrompts(wxPanel):
	def __init__(self, parent, id, prompt_labels):
		wxPanel.__init__(self, parent, id, wxDefaultPosition, wxDefaultSize, wxSIMPLE_BORDER)
		self.SetBackgroundColour(richards_light_gray)
		gszr = wxGridSizer (len(prompt_labels)+1, 1, 2, 2)
		color = richards_aqua
		for prompt_key in prompt_labels.keys():
			label = cPrompt_edit_area(self, -1, " %s" % prompt_labels[prompt_key], aColor = color)
			gszr.Add(label, 0, wxEXPAND | wxALIGN_RIGHT)
			color = richards_blue
		self.SetSizer(gszr)
		gszr.Fit(self)
		self.SetAutoLayout(True)
#====================================================================
#Class central to gnumed data input
#allows data entry of multiple different types.e.g scripts,
#referrals, measurements, recalls etc
#@TODO : just about everything
#section = calling section eg allergies, script
#----------------------------------------------------------
class EditTextBoxes(wxPanel):
	def __init__(self, parent, id, editareaprompts, section):
		wxPanel.__init__(self, parent, id, wxDefaultPosition, wxDefaultSize,style = wxRAISED_BORDER | wxTAB_TRAVERSAL)
		self.SetBackgroundColour(wxColor(222,222,222))
		self.parent = parent
		# rows, cols, hgap, vgap
		self.gszr = wxGridSizer(len(editareaprompts), 1, 2, 2)

		if section == gmSECTION_SUMMARY:
			pass
		elif section == gmSECTION_DEMOGRAPHICS:
			pass
		elif section == gmSECTION_CLINICALNOTES:
			pass
		elif section == gmSECTION_FAMILYHISTORY:
			pass
		elif section == gmSECTION_PASTHISTORY:
			pass
			# line 1
			
			self.txt_condition = cEditAreaField(self,PHX_CONDITION,wxDefaultPosition,wxDefaultSize)
			self.rb_sideleft = wxRadioButton(self,PHX_LEFT, _(" (L) "), wxDefaultPosition,wxDefaultSize)
			self.rb_sideright = wxRadioButton(self, PHX_RIGHT, _("(R)"), wxDefaultPosition,wxDefaultSize,wxSUNKEN_BORDER)
			self.rb_sideboth = wxRadioButton(self, PHX_BOTH, _("Both"), wxDefaultPosition,wxDefaultSize)
			rbsizer = wxBoxSizer(wxHORIZONTAL)
			rbsizer.Add(self.rb_sideleft,1,wxEXPAND)
			rbsizer.Add(self.rb_sideright,1,wxEXPAND) 
			rbsizer.Add(self.rb_sideboth,1,wxEXPAND)
			szr1 = wxBoxSizer(wxHORIZONTAL)
			szr1.Add(self.txt_condition, 4, wxEXPAND)
			szr1.Add(rbsizer, 3, wxEXPAND)
#			self.sizer_line1.Add(self.rb_sideleft,1,wxEXPAND|wxALL,2)
#			self.sizer_line1.Add(self.rb_sideright,1,wxEXPAND|wxALL,2)
#			self.sizer_line1.Add(self.rb_sideboth,1,wxEXPAND|wxALL,2)
			# line 2
			self.txt_notes1 = cEditAreaField(self,PHX_NOTES,wxDefaultPosition,wxDefaultSize)
			# line 3
			self.txt_notes2= cEditAreaField(self,PHX_NOTES2,wxDefaultPosition,wxDefaultSize)
			# line 4
			self.txt_agenoted = cEditAreaField(self, PHX_AGE, wxDefaultPosition, wxDefaultSize)
			szr4 = wxBoxSizer(wxHORIZONTAL)
			szr4.Add(self.txt_agenoted, 1, wxEXPAND)
			szr4.Add(5, 0, 5)
			# line 5
			self.txt_yearnoted  = cEditAreaField(self,PHX_YEAR,wxDefaultPosition,wxDefaultSize)
			szr5 = wxBoxSizer(wxHORIZONTAL)
			szr5.Add(self.txt_yearnoted, 1, wxEXPAND)
			szr5.Add(5, 0, 5)
			# line 6
			self.parent.cb_active = wxCheckBox(self, PHX_ACTIVE, _("Active"), wxDefaultPosition,wxDefaultSize, wxNO_BORDER)
			self.parent.cb_operation = wxCheckBox(self, PHX_OPERATION, _("Operation"), wxDefaultPosition,wxDefaultSize, wxNO_BORDER)
			self.parent.cb_confidential = wxCheckBox(self, PHX_CONFIDENTIAL , _("Confidential"), wxDefaultPosition,wxDefaultSize, wxNO_BORDER)
			self.parent.cb_significant = wxCheckBox(self, PHX_SIGNIFICANT, _("Significant"), wxDefaultPosition,wxDefaultSize, wxNO_BORDER)
			szr6 = wxBoxSizer(wxHORIZONTAL)
			szr6.Add(self.parent.cb_active, 1, wxEXPAND)
			szr6.Add(self.parent.cb_operation, 1, wxEXPAND)
			szr6.Add(self.parent.cb_confidential, 1, wxEXPAND)
			szr6.Add(self.parent.cb_significant, 1, wxEXPAND)
			# line 7
			self.txt_progressnotes  = cEditAreaField(self,PHX_PROGRESSNOTES ,wxDefaultPosition,wxDefaultSize)
			# line 8
			szr8 = wxBoxSizer(wxHORIZONTAL)
			szr8.Add(5, 0, 6)
			szr8.Add(self._make_standard_buttons(), 0, wxEXPAND)

			self.gszr.Add(szr1,0,wxEXPAND)
			self.gszr.Add(self.txt_notes1,0,wxEXPAND)
			self.gszr.Add(self.txt_notes2,0,wxEXPAND)
			self.gszr.Add(szr4,0,wxEXPAND)
			self.gszr.Add(szr5,0,wxEXPAND)
			self.gszr.Add(szr6,0,wxEXPAND)
			self.gszr.Add(self.txt_progressnotes,0,wxEXPAND)
			self.gszr.Add(szr8,0,wxEXPAND)
			#self.anylist = wxListCtrl(self, -1,  wxDefaultPosition,wxDefaultSize,wxLC_REPORT|wxLC_LIST|wxSUNKEN_BORDER)

		elif section == gmSECTION_SCRIPT:
			pass
		elif section == gmSECTION_REQUESTS:
			pass
		elif section == gmSECTION_MEASUREMENTS:
			pass
		elif section == gmSECTION_RECALLS:
			pass
		else:
			pass

		self.SetSizer(self.gszr)
		self.gszr.Fit(self)

		self.SetAutoLayout(True)
		self.Show(True)
	#----------------------------------------------------------------
	def _make_standard_buttons(self):
		self.btn_OK = wxButton(self, -1, _("Ok"))
		self.btn_Clear = wxButton(self, -1, _("Clear"))
		szr_buttons = wxBoxSizer(wxHORIZONTAL)
		szr_buttons.Add(self.btn_OK, 1, wxEXPAND, wxALL, 1)
		szr_buttons.Add(5, 0, 0)
		szr_buttons.Add(self.btn_Clear, 1, wxEXPAND, wxALL, 1)
		return szr_buttons
#====================================================================
class EditArea(wxPanel):
	def __init__(self, parent, id, line_labels, section):
		_log.Log(gmLog.lWarn, '***** old style EditArea instantiated, please convert *****')

		wxPanel.__init__(self, parent, id, wxDefaultPosition, wxDefaultSize, style = wxNO_BORDER)
		self.SetBackgroundColour(wxColor(222,222,222))

		# make prompts
		prompts = gmPnlEditAreaPrompts(self, -1, line_labels)
		# and shadow below prompts in ...
		shadow_below_prompts = wxWindow(self, -1, wxDefaultPosition, wxDefaultSize, 0)
		# ... gray
		shadow_below_prompts.SetBackgroundColour(richards_dark_gray)
		szr_shadow_below_prompts = wxBoxSizer (wxHORIZONTAL)
		szr_shadow_below_prompts.Add(5,0,0,wxEXPAND)
		szr_shadow_below_prompts.Add(shadow_below_prompts, 10, wxEXPAND)
		# stack prompts and shadow vertically
		szr_prompts = wxBoxSizer(wxVERTICAL)
		szr_prompts.Add(prompts, 97, wxEXPAND)
		szr_prompts.Add(szr_shadow_below_prompts, 5, wxEXPAND)

		# make edit fields
		edit_fields = EditTextBoxes(self, -1, line_labels, section)
		# make shadow below edit area ...
		shadow_below_editarea = wxWindow(self, -1, wxDefaultPosition, wxDefaultSize, 0)
		# ... gray
		shadow_below_editarea.SetBackgroundColour(richards_coloured_gray)
		szr_shadow_below_editarea = wxBoxSizer(wxHORIZONTAL)
		szr_shadow_below_editarea.Add(5,0,0,wxEXPAND)
		szr_shadow_below_editarea.Add(shadow_below_editarea, 12, wxEXPAND)
		# stack edit fields and shadow vertically
		szr_editarea = wxBoxSizer(wxVERTICAL)
		szr_editarea.Add(edit_fields, 92, wxEXPAND)
		szr_editarea.Add(szr_shadow_below_editarea, 5, wxEXPAND)

		# make shadows to the right of ...
		# ... the prompts ...
		shadow_rightof_prompts = wxWindow(self, -1, wxDefaultPosition, wxDefaultSize, 0)
		shadow_rightof_prompts.SetBackgroundColour(richards_dark_gray)
		szr_shadow_rightof_prompts = wxBoxSizer(wxVERTICAL)
		szr_shadow_rightof_prompts.Add(0,5,0,wxEXPAND)
		szr_shadow_rightof_prompts.Add(shadow_rightof_prompts,1,wxEXPAND)
		# ... and the edit area
		shadow_rightof_editarea = wxWindow(self, -1, wxDefaultPosition, wxDefaultSize, 0)
		shadow_rightof_editarea.SetBackgroundColour(richards_coloured_gray)
		szr_shadow_rightof_editarea = wxBoxSizer(wxVERTICAL)
		szr_shadow_rightof_editarea.Add(0, 5, 0, wxEXPAND)
		szr_shadow_rightof_editarea.Add(shadow_rightof_editarea, 1, wxEXPAND)

		# stack prompts, shadows and fields horizontally
		self.szr_main_panels = wxBoxSizer(wxHORIZONTAL)
		self.szr_main_panels.Add(szr_prompts, 10, wxEXPAND)
		self.szr_main_panels.Add(szr_shadow_rightof_prompts, 1, wxEXPAND)
		self.szr_main_panels.Add(5, 0, 0, wxEXPAND)
		self.szr_main_panels.Add(szr_editarea, 89, wxEXPAND)
		self.szr_main_panels.Add(szr_shadow_rightof_editarea, 1, wxEXPAND)

		# use sizer for border around everything plus a little gap
		# FIXME: fold into szr_main_panels ?
		self.szr_central_container = wxBoxSizer(wxHORIZONTAL)
		self.szr_central_container.Add(self.szr_main_panels, 1, wxEXPAND | wxALL, 5)
		self.SetSizer(self.szr_central_container)
		self.szr_central_container.Fit(self)
		self.SetAutoLayout(True)
		self.Show(True)


#====================================================================
# old stuff still needed for conversion
#--------------------------------------------------------------------
#====================================================================

#====================================================================

#		elif section == gmSECTION_SCRIPT:
#		      gmLog.gmDefLog.Log (gmLog.lData, "in script section now")
#		      self.text1_prescription_reason = cEditAreaField(self,-1,wxDefaultPosition,wxDefaultSize)
#		      self.text2_drug_class = cEditAreaField(self,-1,wxDefaultPosition,wxDefaultSize)
#		      self.text3_generic_drug = cEditAreaField(self,-1,wxDefaultPosition,wxDefaultSize)
#		      self.text4_brand_drug = cEditAreaField(self,-1,wxDefaultPosition,wxDefaultSize)
#		      self.text5_strength = cEditAreaField(self,-1,wxDefaultPosition,wxDefaultSize)
#		      self.text6_directions = cEditAreaField(self,-1,wxDefaultPosition,wxDefaultSize)
#		      self.text7_for_duration = cEditAreaField(self,-1,wxDefaultPosition,wxDefaultSize)
#		      self.text8_prescription_progress_notes = cEditAreaField(self,-1,wxDefaultPosition,wxDefaultSize)
#		      self.text9_quantity = cEditAreaField(self,-1,wxDefaultPosition,wxDefaultSize)
#		      lbl_veterans = cPrompt_edit_area(self,-1,"  Veteran  ")
#		      lbl_reg24 = cPrompt_edit_area(self,-1,"  Reg 24  ")
#		      lbl_quantity = cPrompt_edit_area(self,-1,"  Quantity  ")
#		      lbl_repeats = cPrompt_edit_area(self,-1,"  Repeats  ")
#		      lbl_usualmed = cPrompt_edit_area(self,-1,"  Usual  ")
#		      self.cb_veteran  = wxCheckBox(self, -1, " Yes ", wxDefaultPosition,wxDefaultSize, wxNO_BORDER)
#		      self.cb_reg24 = wxCheckBox(self, -1, " Yes ", wxDefaultPosition,wxDefaultSize, wxNO_BORDER)
#		      self.cb_usualmed = wxCheckBox(self, -1, " Yes ", wxDefaultPosition,wxDefaultSize, wxNO_BORDER)
#		      self.sizer_auth_PI = wxBoxSizer(wxHORIZONTAL)
#		      self.btn_authority = wxButton(self,-1,">Authority")     #create authority script
#		      self.btn_briefPI   = wxButton(self,-1,"Brief PI")       #show brief drug product information
#		      self.sizer_auth_PI.Add(self.btn_authority,1,wxEXPAND|wxALL,2)  #put authority button and PI button
#		      self.sizer_auth_PI.Add(self.btn_briefPI,1,wxEXPAND|wxALL,2)    #on same sizer
#		      self.text10_repeats  = cEditAreaField(self,-1,wxDefaultPosition,wxDefaultSize)
#		      self.sizer_line3.Add(self.text3_generic_drug,5,wxEXPAND)
#		      self.sizer_line3.Add(lbl_veterans,1,wxEXPAND)
 #       	      self.sizer_line3.Add(self.cb_veteran,1,wxEXPAND)
#		      self.sizer_line4.Add(self.text4_brand_drug,5,wxEXPAND)
#		      self.sizer_line4.Add(lbl_reg24,1,wxEXPAND)
 #       	      self.sizer_line4.Add(self.cb_reg24,1,wxEXPAND)
#		      self.sizer_line5.Add(self.text5_strength,5,wxEXPAND)
#		      self.sizer_line5.Add(lbl_quantity,1,wxEXPAND)
 #       	      self.sizer_line5.Add(self.text9_quantity,1,wxEXPAND)
#		      self.sizer_line6.Add(self.text6_directions,5,wxEXPAND)
#		      self.sizer_line6.Add(lbl_repeats,1,wxEXPAND)
 #       	      self.sizer_line6.Add(self.text10_repeats,1,wxEXPAND)
#		      self.sizer_line7.Add(self.text7_for_duration,5,wxEXPAND)
#		      self.sizer_line7.Add(lbl_usualmed,1,wxEXPAND)
 #       	      self.sizer_line7.Add(self.cb_usualmed,1,wxEXPAND)
#		      self.sizer_line8.Add(5,0,0)
#		      self.sizer_line8.Add(self.sizer_auth_PI,2,wxEXPAND)
#		      self.sizer_line8.Add(5,0,2)
#		      self.sizer_line8.Add(self.btn_OK,1,wxEXPAND|wxALL,2)
#		      self.sizer_line8.Add(self.btn_Clear,1,wxEXPAND|wxALL,2)
#		      self.gszr.Add(self.text1_prescription_reason,1,wxEXPAND) #prescribe for
#		      self.gszr.Add(self.text2_drug_class,1,wxEXPAND) #prescribe by class
#		      self.gszr.Add(self.sizer_line3,1,wxEXPAND) #prescribe by generic, lbl_veterans, cb_veteran
#		      self.gszr.Add(self.sizer_line4,1,wxEXPAND) #prescribe by brand, lbl_reg24, cb_reg24
#		      self.gszr.Add(self.sizer_line5,1,wxEXPAND) #drug strength, lbl_quantity, text_quantity 
#		      self.gszr.Add(self.sizer_line6,1,wxEXPAND) #txt_directions, lbl_repeats, text_repeats 
#		      self.gszr.Add(self.sizer_line7,1,wxEXPAND) #text_for,lbl_usual,chk_usual
#		      self.gszr.Add(self.text8_prescription_progress_notes,1,wxEXPAND)            #text_progressNotes
#		      self.gszr.Add(self.sizer_line8,1,wxEXPAND)
		      
		      
#	        elif section == gmSECTION_REQUESTS:
#		      #----------------------------------------------------------------------------- 	
	              #editing area for general requests e.g pathology, radiology, physiotherapy etc
		      #create textboxes, radiobuttons etc
		      #-----------------------------------------------------------------------------
#		      self.txt_request_type = cEditAreaField(self,ID_REQUEST_TYPE,wxDefaultPosition,wxDefaultSize)
#		      self.txt_request_company = cEditAreaField(self,ID_REQUEST_COMPANY,wxDefaultPosition,wxDefaultSize)
#		      self.txt_request_street = cEditAreaField(self,ID_REQUEST_STREET,wxDefaultPosition,wxDefaultSize)
#		      self.txt_request_suburb = cEditAreaField(self,ID_REQUEST_SUBURB,wxDefaultPosition,wxDefaultSize)
#		      self.txt_request_phone= cEditAreaField(self,ID_REQUEST_PHONE,wxDefaultPosition,wxDefaultSize)
#		      self.txt_request_requests = cEditAreaField(self,ID_REQUEST_REQUESTS,wxDefaultPosition,wxDefaultSize)
#		      self.txt_request_notes = cEditAreaField(self,ID_REQUEST_FORMNOTES,wxDefaultPosition,wxDefaultSize)
#		      self.txt_request_medications = cEditAreaField(self,ID_REQUEST_MEDICATIONS,wxDefaultPosition,wxDefaultSize)
#		      self.txt_request_copyto = cEditAreaField(self,ID_REQUEST_COPYTO,wxDefaultPosition,wxDefaultSize)
#		      self.txt_request_progressnotes = cEditAreaField(self,ID_PROGRESSNOTES,wxDefaultPosition,wxDefaultSize)
#		      self.lbl_companyphone = cPrompt_edit_area(self,-1,"  Phone  ")
#		      self.cb_includeallmedications = wxCheckBox(self, -1, " Include all medications ", wxDefaultPosition,wxDefaultSize, wxNO_BORDER)
#		      self.rb_request_bill_bb = wxRadioButton(self, ID_REQUEST_BILL_BB, "Bulk Bill ", wxDefaultPosition,wxDefaultSize)
#	              self.rb_request_bill_private = wxRadioButton(self, ID_REQUEST_BILL_PRIVATE, "Private", wxDefaultPosition,wxDefaultSize,wxSUNKEN_BORDER)
#		      self.rb_request_bill_rebate = wxRadioButton(self, ID_REQUEST_BILL_REBATE, "Rebate", wxDefaultPosition,wxDefaultSize)
#		      self.rb_request_bill_wcover = wxRadioButton(self, ID_REQUEST_BILL_wcover, "w/cover", wxDefaultPosition,wxDefaultSize)
		      #--------------------------------------------------------------
                     #add controls to sizers where multiple controls per editor line
		      #--------------------------------------------------------------
#                      self.sizer_request_optionbuttons = wxBoxSizer(wxHORIZONTAL)
#		      self.sizer_request_optionbuttons.Add(self.rb_request_bill_bb,1,wxEXPAND)
#		      self.sizer_request_optionbuttons.Add(self.rb_request_bill_private ,1,wxEXPAND)
#                      self.sizer_request_optionbuttons.Add(self.rb_request_bill_rebate  ,1,wxEXPAND)
#                      self.sizer_request_optionbuttons.Add(self.rb_request_bill_wcover  ,1,wxEXPAND)
#		      self.sizer_line4.Add(self.txt_request_suburb,4,wxEXPAND)
#		      self.sizer_line4.Add(self.lbl_companyphone,1,wxEXPAND)
#		      self.sizer_line4.Add(self.txt_request_phone,2,wxEXPAND)
#		      self.sizer_line7.Add(self.txt_request_medications, 4,wxEXPAND)
#		      self.sizer_line7.Add(self.cb_includeallmedications,3,wxEXPAND)
#		      self.sizer_line10.AddSizer(self.sizer_request_optionbuttons,3,wxEXPAND)
#		      self.sizer_line10.AddSizer(self.szr_buttons,1,wxEXPAND)
		      #self.sizer_line10.Add(self.btn_OK,1,wxEXPAND|wxALL,1)
	              #self.sizer_line10.Add(self.btn_Clear,1,wxEXPAND|wxALL,1)  
		      #------------------------------------------------------------------
		      #add either controls or sizers with controls to vertical grid sizer
		      #------------------------------------------------------------------
#                      self.gszr.Add(self.txt_request_type,0,wxEXPAND)                   #e.g Pathology
#		      self.gszr.Add(self.txt_request_company,0,wxEXPAND)                #e.g Douglas Hanly Moir
#		      self.gszr.Add(self.txt_request_street,0,wxEXPAND)                 #e.g 120 Big Street  
#		      self.gszr.AddSizer(self.sizer_line4,0,wxEXPAND)                   #e.g RYDE NSW Phone 02 1800 222 365
#		      self.gszr.Add(self.txt_request_requests,0,wxEXPAND)               #e.g FBC;ESR;UEC;LFTS
#		      self.gszr.Add(self.txt_request_notes,0,wxEXPAND)                  #e.g generally tired;weight loss;
#		      self.gszr.AddSizer(self.sizer_line7,0,wxEXPAND)                   #e.g Lipitor;losec;zyprexa
#		      self.gszr.Add(self.txt_request_copyto,0,wxEXPAND)                 #e.g Dr I'm All Heart, 120 Big Street Smallville
#		      self.gszr.Add(self.txt_request_progressnotes,0,wxEXPAND)          #emphasised to patient must return for results 
 #                     self.sizer_line8.Add(5,0,6)
#		      self.sizer_line8.Add(self.btn_OK,1,wxEXPAND|wxALL,2)
#	              self.sizer_line8.Add(self.btn_Clear,1,wxEXPAND|wxALL,2)   
#		      self.gszr.Add(self.sizer_line10,0,wxEXPAND)                       #options:b/bill private, rebate,w/cover btnok,btnclear

		      
#	        elif section == gmSECTION_MEASUREMENTS:
#		      self.combo_measurement_type = wxComboBox(self, ID_MEASUREMENT_TYPE, "", wxDefaultPosition,wxDefaultSize, ['Blood pressure','INR','Height','Weight','Whatever other measurement you want to put in here'], wxCB_DROPDOWN)
#		      self.combo_measurement_type.SetFont(wxFont(12,wxSWISS,wxNORMAL, wxBOLD,False,''))
#		      self.combo_measurement_type.SetForegroundColour(wxColor(255,0,0))
#		      self.txt_measurement_value = cEditAreaField(self,ID_MEASUREMENT_VALUE,wxDefaultPosition,wxDefaultSize)
#		      self.txt_txt_measurement_date = cEditAreaField(self,ID_MEASUREMENT_DATE,wxDefaultPosition,wxDefaultSize)
#		      self.txt_txt_measurement_comment = cEditAreaField(self,ID_MEASUREMENT_COMMENT,wxDefaultPosition,wxDefaultSize)
#		      self.txt_txt_measurement_progressnote = cEditAreaField(self,ID_PROGRESSNOTES,wxDefaultPosition,wxDefaultSize)
#		      self.sizer_graphnextbtn = wxBoxSizer(wxHORIZONTAL)
#		      self.btn_nextvalue = wxButton(self,ID_MEASUREMENT_NEXTVALUE,"   Next Value   ")                 #clear fields except type
#		      self.btn_graph   = wxButton(self,ID_MEASUREMENT_GRAPH," Graph ")                        #graph all values of this type
#		      self.sizer_graphnextbtn.Add(self.btn_nextvalue,1,wxEXPAND|wxALL,2)  #put next and graph button
#		      self.sizer_graphnextbtn.Add(self.btn_graph,1,wxEXPAND|wxALL,2)      #on same sizer	
#		      self.gszr.Add(self.combo_measurement_type,0,wxEXPAND)              #e.g Blood pressure
#		      self.gszr.Add(self.txt_measurement_value,0,wxEXPAND)               #e.g 120.70
#		      self.gszr.Add(self.txt_txt_measurement_date,0,wxEXPAND)            #e.g 10/12/2001
#		      self.gszr.Add(self.txt_txt_measurement_comment,0,wxEXPAND)         #e.g sitting, right arm
#		      self.gszr.Add(self.txt_txt_measurement_progressnote,0,wxEXPAND)    #e.g given home BP montitor, see 1 week
#		      self.sizer_line8.Add(5,0,0)
#		      self.sizer_line8.Add(self.sizer_graphnextbtn,2,wxEXPAND)
#		      self.sizer_line8.Add(5,0,2)
#		      self.sizer_line8.Add(self.btn_OK,1,wxEXPAND|wxALL,2)
#		      self.sizer_line8.Add(self.btn_Clear,1,wxEXPAND|wxALL,2)
#		      self.gszr.AddSizer(self.sizer_line8,0,wxEXPAND)
		      

#	        elif section == gmSECTION_REFERRALS:
#		      self.btnpreview = wxButton(self,-1,"Preview")
#		      self.sizer_btnpreviewok = wxBoxSizer(wxHORIZONTAL)
		      #--------------------------------------------------------
	              #editing area for referral letters, insurance letters etc
		      #create textboxes, checkboxes etc
		      #--------------------------------------------------------
#		      self.txt_referralcategory = cEditAreaField(self,ID_REFERRAL_CATEGORY,wxDefaultPosition,wxDefaultSize)
#		      self.txt_referralname = cEditAreaField(self,ID_REFERRAL_NAME,wxDefaultPosition,wxDefaultSize)
#		      self.txt_referralorganisation = cEditAreaField(self,ID_REFERRAL_ORGANISATION,wxDefaultPosition,wxDefaultSize)
#		      self.txt_referralstreet1 = cEditAreaField(self,ID_REFERRAL_STREET1,wxDefaultPosition,wxDefaultSize)
#		      self.txt_referralstreet2 = cEditAreaField(self,ID_REFERRAL_STREET2,wxDefaultPosition,wxDefaultSize)
#		      self.txt_referralstreet3 = cEditAreaField(self,ID_REFERRAL_STREET3,wxDefaultPosition,wxDefaultSize)
#		      self.txt_referralsuburb = cEditAreaField(self,ID_REFERRAL_SUBURB,wxDefaultPosition,wxDefaultSize)
#		      self.txt_referralpostcode = cEditAreaField(self,ID_REFERRAL_POSTCODE,wxDefaultPosition,wxDefaultSize)
#		      self.txt_referralfor = cEditAreaField(self,ID_REFERRAL_FOR,wxDefaultPosition,wxDefaultSize)
#		      self.txt_referralwphone= cEditAreaField(self,ID_REFERRAL_WPHONE,wxDefaultPosition,wxDefaultSize)
#		      self.txt_referralwfax= cEditAreaField(self,ID_REFERRAL_WFAX,wxDefaultPosition,wxDefaultSize)
#		      self.txt_referralwemail= cEditAreaField(self,ID_REFERRAL_WEMAIL,wxDefaultPosition,wxDefaultSize)
		      #self.txt_referralrequests = cEditAreaField(self,ID_REFERRAL_REQUESTS,wxDefaultPosition,wxDefaultSize)
		      #self.txt_referralnotes = cEditAreaField(self,ID_REFERRAL_FORMNOTES,wxDefaultPosition,wxDefaultSize)
		      #self.txt_referralmedications = cEditAreaField(self,ID_REFERRAL_MEDICATIONS,wxDefaultPosition,wxDefaultSize)
#		      self.txt_referralcopyto = cEditAreaField(self,ID_REFERRAL_COPYTO,wxDefaultPosition,wxDefaultSize)
#		      self.txt_referralprogressnotes = cEditAreaField(self,ID_PROGRESSNOTES,wxDefaultPosition,wxDefaultSize)
#		      self.lbl_referralwphone = cPrompt_edit_area(self,-1,"  W Phone  ")
#		      self.lbl_referralwfax = cPrompt_edit_area(self,-1,"  W Fax  ")
#		      self.lbl_referralwemail = cPrompt_edit_area(self,-1,"  W Email  ")
#		      self.lbl_referralpostcode = cPrompt_edit_area(self,-1,"  Postcode  ")
#		      self.chkbox_referral_usefirstname = wxCheckBox(self, -1, " Use Firstname ", wxDefaultPosition,wxDefaultSize, wxNO_BORDER)
#		      self.chkbox_referral_headoffice = wxCheckBox(self, -1, " Head Office ", wxDefaultPosition,wxDefaultSize, wxNO_BORDER)
#		      self.chkbox_referral_medications = wxCheckBox(self, -1, " Medications ", wxDefaultPosition,wxDefaultSize, wxNO_BORDER)
#		      self.chkbox_referral_socialhistory = wxCheckBox(self, -1, " Social History ", wxDefaultPosition,wxDefaultSize, wxNO_BORDER)
#		      self.chkbox_referral_familyhistory = wxCheckBox(self, -1, " Family History ", wxDefaultPosition,wxDefaultSize, wxNO_BORDER)
#		      self.chkbox_referral_pastproblems = wxCheckBox(self, -1, " Past Problems ", wxDefaultPosition,wxDefaultSize, wxNO_BORDER)
#		      self.chkbox_referral_activeproblems = wxCheckBox(self, -1, " Active Problems ", wxDefaultPosition,wxDefaultSize, wxNO_BORDER)
#		      self.chkbox_referral_habits = wxCheckBox(self, -1, " Habits ", wxDefaultPosition,wxDefaultSize, wxNO_BORDER)
		      #self.chkbox_referral_Includeall = wxCheckBox(self, -1, " Include all of the above ", wxDefaultPosition,wxDefaultSize, wxNO_BORDER)
		      #--------------------------------------------------------------
                      #add controls to sizers where multiple controls per editor line
		      #--------------------------------------------------------------
#		      self.sizer_line2.Add(self.txt_referralname,2,wxEXPAND) 
#		      self.sizer_line2.Add(self.chkbox_referral_usefirstname,2,wxEXPAND)
#		      self.sizer_line3.Add(self.txt_referralorganisation,2,wxEXPAND)
#		      self.sizer_line3.Add(self.chkbox_referral_headoffice,2, wxEXPAND)
#		      self.sizer_line4.Add(self.txt_referralstreet1,2,wxEXPAND)
#		      self.sizer_line4.Add(self.lbl_referralwphone,1,wxEXPAND)
#		      self.sizer_line4.Add(self.txt_referralwphone,1,wxEXPAND)
#		      self.sizer_line5.Add(self.txt_referralstreet2,2,wxEXPAND)
#		      self.sizer_line5.Add(self.lbl_referralwfax,1,wxEXPAND)
#		      self.sizer_line5.Add(self.txt_referralwfax,1,wxEXPAND)
#		      self.sizer_line6.Add(self.txt_referralstreet3,2,wxEXPAND)
#		      self.sizer_line6.Add(self.lbl_referralwemail,1,wxEXPAND)
#		      self.sizer_line6.Add(self.txt_referralwemail,1,wxEXPAND)
#		      self.sizer_line7.Add(self.txt_referralsuburb,2,wxEXPAND)
#		      self.sizer_line7.Add(self.lbl_referralpostcode,1,wxEXPAND)
#		      self.sizer_line7.Add(self.txt_referralpostcode,1,wxEXPAND)
#		      self.sizer_line10.Add(self.chkbox_referral_medications,1,wxEXPAND)
#	              self.sizer_line10.Add(self.chkbox_referral_socialhistory,1,wxEXPAND)
#		      self.sizer_line10.Add(self.chkbox_referral_familyhistory,1,wxEXPAND)
#		      self.sizer_line11.Add(self.chkbox_referral_pastproblems  ,1,wxEXPAND)
#		      self.sizer_line11.Add(self.chkbox_referral_activeproblems  ,1,wxEXPAND)
#		      self.sizer_line11.Add(self.chkbox_referral_habits  ,1,wxEXPAND)
#		      self.sizer_btnpreviewok.Add(self.btnpreview,0,wxEXPAND)
#		      self.szr_buttons.Add(self.btn_Clear,0, wxEXPAND)		      
		      #------------------------------------------------------------------
		      #add either controls or sizers with controls to vertical grid sizer
		      #------------------------------------------------------------------
 #                     self.gszr.Add(self.txt_referralcategory,0,wxEXPAND)               #e.g Othopaedic surgeon
#		      self.gszr.Add(self.sizer_line2,0,wxEXPAND)                        #e.g Dr B Breaker
#		      self.gszr.Add(self.sizer_line3,0,wxEXPAND)                        #e.g General Orthopaedic servies
#		      self.gszr.Add(self.sizer_line4,0,wxEXPAND)                        #e.g street1
#		      self.gszr.Add(self.sizer_line5,0,wxEXPAND)                        #e.g street2
#		      self.gszr.Add(self.sizer_line6,0,wxEXPAND)                        #e.g street3
#		      self.gszr.Add(self.sizer_line7,0,wxEXPAND)                        #e.g suburb and postcode
#		      self.gszr.Add(self.txt_referralfor,0,wxEXPAND)                    #e.g Referral for an opinion
#		      self.gszr.Add(self.txt_referralcopyto,0,wxEXPAND)                 #e.g Dr I'm All Heart, 120 Big Street Smallville
#		      self.gszr.Add(self.txt_referralprogressnotes,0,wxEXPAND)          #emphasised to patient must return for results 
#		      self.gszr.AddSizer(self.sizer_line10,0,wxEXPAND)                   #e.g check boxes to include medications etc
#		      self.gszr.Add(self.sizer_line11,0,wxEXPAND)                       #e.g check boxes to include active problems etc
		      #self.spacer = wxWindow(self,-1,wxDefaultPosition,wxDefaultSize)
		      #self.spacer.SetBackgroundColour(wxColor(255,255,255))
#		      self.sizer_line12.Add(5,0,6)
		      #self.sizer_line12.Add(self.spacer,6,wxEXPAND)
#		      self.sizer_line12.Add(self.btnpreview,1,wxEXPAND|wxALL,2)
#	              self.sizer_line12.Add(self.btn_Clear,1,wxEXPAND|wxALL,2)    
#	              self.gszr.Add(self.sizer_line12,0,wxEXPAND)                       #btnpreview and btn clear
		      

#		elif section == gmSECTION_RECALLS:
		      #FIXME remove present options in this combo box	  #FIXME defaults need to be loaded from database	  
#		      self.combo_tosee = wxComboBox(self, ID_RECALLS_TOSEE, "", wxDefaultPosition,wxDefaultSize, ['Doctor1','Doctor2','Nurse1','Dietition'], wxCB_READONLY ) #wxCB_DROPDOWN)
#		      self.combo_tosee.SetFont(wxFont(12,wxSWISS,wxNORMAL, wxBOLD,False,''))
#		      self.combo_tosee.SetForegroundColour(wxColor(255,0,0))
		      #FIXME defaults need to be loaded from database
#		      self.combo_recall_method = wxComboBox(self, ID_RECALLS_CONTACTMETHOD, "", wxDefaultPosition,wxDefaultSize, ['Letter','Telephone','Email','Carrier pigeon'], wxCB_READONLY )
#		      self.combo_recall_method.SetFont(wxFont(12,wxSWISS,wxNORMAL, wxBOLD,False,''))
#		      self.combo_recall_method.SetForegroundColour(wxColor(255,0,0))
		      #FIXME defaults need to be loaded from database
 #                     self.combo_apptlength = wxComboBox(self, ID_RECALLS_APPNTLENGTH, "", wxDefaultPosition,wxDefaultSize, ['brief','standard','long','prolonged'], wxCB_READONLY )
#		      self.combo_apptlength.SetFont(wxFont(12,wxSWISS,wxNORMAL, wxBOLD,False,''))
#		      self.combo_apptlength.SetForegroundColour(wxColor(255,0,0))
#		      self.txt_recall_for = cEditAreaField(self,ID_RECALLS_TXT_FOR, wxDefaultPosition,wxDefaultSize)
#		      self.txt_recall_due = cEditAreaField(self,ID_RECALLS_TXT_DATEDUE, wxDefaultPosition,wxDefaultSize)
#		      self.txt_recall_addtext = cEditAreaField(self,ID_RECALLS_TXT_ADDTEXT,wxDefaultPosition,wxDefaultSize)
#		      self.txt_recall_include = cEditAreaField(self,ID_RECALLS_TXT_INCLUDEFORMS,wxDefaultPosition,wxDefaultSize)
#		      self.txt_recall_progressnotes = cEditAreaField(self,ID_PROGRESSNOTES,wxDefaultPosition,wxDefaultSize)
#		      self.lbl_recall_consultlength = cPrompt_edit_area(self,-1,"  Appointment length  ")
		      #sizer_lkine1 has the method of recall and the appointment length
#		      self.sizer_line1.Add(self.combo_recall_method,1,wxEXPAND)
#		      self.sizer_line1.Add(self.lbl_recall_consultlength,1,wxEXPAND)
#		      self.sizer_line1.Add(self.combo_apptlength,1,wxEXPAND)
		      #Now add the controls to the grid sizer
 #                     self.gszr.Add(self.combo_tosee,1,wxEXPAND)                       #list of personel for patient to see
#		      self.gszr.Add(self.txt_recall_for,1,wxEXPAND)                    #the actual recall may be free text or word wheel  
#		      self.gszr.Add(self.txt_recall_due,1,wxEXPAND)                    #date of future recall 
#		      self.gszr.Add(self.txt_recall_addtext,1,wxEXPAND)                #added explanation e.g 'come fasting' 
#		      self.gszr.Add(self.txt_recall_include,1,wxEXPAND)                #any forms to be sent out first eg FBC
#		      self.gszr.AddSizer(self.sizer_line1,1,wxEXPAND)                        #the contact method, appointment length
#		      self.gszr.Add(self.txt_recall_progressnotes,1,wxEXPAND)          #add any progress notes for consultation
#		      self.sizer_line8.Add(5,0,6)
#		      self.sizer_line8.Add(self.btn_OK,1,wxEXPAND|wxALL,2)
#	              self.sizer_line8.Add(self.btn_Clear,1,wxEXPAND|wxALL,2)    
#		      self.gszr.Add(self.sizer_line8,1,wxEXPAND)
#		else:
#		      pass

#====================================================================
# main
#--------------------------------------------------------------------
if __name__ == "__main__":

	#================================================================
	class cTestEditArea(cEditArea):
		def __init__(self, parent):
			cEditArea.__init__(self, parent, -1)
		def _define_prompts(self):
			self._add_prompt(line=1, label='line 1')
			self._add_prompt(line=2, label='buttons')
		def _define_fields(self, parent):
			# line 1
			self.fld_substance = cEditAreaField(parent)
			self._add_field(
				line = 1,
				pos = 1,
				widget = self.fld_substance,
				weight = 1
			)
			# line 2
			self._add_field(
				line = 2,
				pos = 1,
				widget = self._make_standard_buttons(parent),
				weight = 1
			)
	#================================================================
	app = wxPyWidgetTester(size = (400, 200))
	app.SetWidget(cTestEditArea)
	app.MainLoop()
#	app = wxPyWidgetTester(size = (400, 200))
#	app.SetWidget(gmFamilyHxEditArea, -1)
#	app.MainLoop()
#	app = wxPyWidgetTester(size = (400, 200))
#	app.SetWidget(gmPastHistoryEditArea, -1)
#	app.MainLoop()
#====================================================================
# $Log: gmEditArea.py,v $
# Revision 1.88  2005-04-25 17:43:55  ncq
# - smooth changeover to from wxPython import wx
#
# Revision 1.87  2005/04/24 14:47:14  ncq
# - add generic edit area popup dialog
# - improve cEditArea2
#
# Revision 1.86  2005/04/20 22:19:01  ncq
# - move std button event registration to after definition of buttons
#
# Revision 1.85  2005/04/18 19:21:57  ncq
# - added cEditArea2 which - being based on a wxFlexGridSizer - is a lot
#   simpler (hence easier to debug) but lacks some eye candy (shadows and
#   separate prompt panel)
#
# Revision 1.84  2005/03/20 17:50:15  ncq
# - catch another exception on doing the layout
#
# Revision 1.83  2005/02/03 20:19:16  ncq
# - get_demographic_record() -> get_identity()
#
# Revision 1.82  2005/01/31 10:37:26  ncq
# - gmPatient.py -> gmPerson.py
#
# Revision 1.81  2005/01/31 06:27:18  ncq
# - silly cleanup
#
# Revision 1.80  2004/12/15 22:00:12  ncq
# - cleaned up/improved version of edit area
# - old version still works and emits a conversion incentive
#
# Revision 1.79  2004/10/11 19:54:38  ncq
# - cleanup
#
# Revision 1.78  2004/07/18 20:30:53  ncq
# - wxPython.true/false -> Python.True/False as Python tells us to do
#
# Revision 1.77  2004/07/17 21:16:39  ncq
# - cleanup/refactor allergy widgets:
#   - Horst space plugin added
#   - Richard space plugin separated out
#   - plugin independant GUI code aggregated
#   - allergies edit area factor out from generic edit area file
#
# Revision 1.76  2004/07/15 23:28:04  ncq
# - vaccinations edit area factored out
#
# Revision 1.75  2004/06/20 15:48:06  ncq
# - better please epydoc
#
# Revision 1.74  2004/06/20 06:49:21  ihaywood
# changes required due to Epydoc's OCD
#
# Revision 1.73  2004/05/27 13:40:22  ihaywood
# more work on referrals, still not there yet
#
# Revision 1.72  2004/05/18 20:43:17  ncq
# - check get_clinical_record() return status
#
# Revision 1.71  2004/05/16 14:32:51  ncq
# - cleanup
#
# Revision 1.70  2004/04/27 18:43:03  ncq
# - fix _check_unsaved_data()
#
# Revision 1.69  2004/04/24 12:59:17  ncq
# - all shiny and new, vastly improved vaccinations
#   handling via clinical item objects
# - mainly thanks to Carlos Moro
#
# Revision 1.68  2004/04/11 10:10:56  ncq
# - cleanup
#
# Revision 1.67  2004/04/10 01:48:31  ihaywood
# can generate referral letters, output to xdvi at present
#
# Revision 1.66  2004/03/28 11:09:04  ncq
# - some cleanup
#
# Revision 1.65  2004/03/28 04:09:31  ihaywood
# referrals can now select an address from pick list.
#
# Revision 1.64  2004/03/10 12:56:01  ihaywood
# fixed sudden loss of main.shadow
# more work on referrals,
#
# Revision 1.63  2004/03/09 13:46:54  ihaywood
# edit area now has resizable lines
# referrals loads with this feature
# BUG: the first line is bigger than the rest: why??
#
# Revision 1.61  2004/02/25 09:46:22  ncq
# - import from pycommon now, not python-common
#
# Revision 1.60  2004/02/05 23:49:52  ncq
# - use wxCallAfter()
#
# Revision 1.59  2004/02/05 00:26:47  sjtan
#
# converting gmPastHistory to _define.., _generate.. style.
#
# Revision 1.58  2004/02/02 22:28:23  ncq
# - OK now inits the edit area as per Richard's specs
#
# Revision 1.57  2004/01/26 22:15:32  ncq
# - don't duplicate "Serial #" label
#
# Revision 1.56  2004/01/26 18:25:07  ncq
# - some attribute names changed in the backend
#
# Revision 1.55  2004/01/24 10:24:17  ncq
# - method rename for consistency
#
# Revision 1.54  2004/01/22 23:42:19  ncq
# - follow Richard's GUI specs more closely on standard buttons
#
# Revision 1.53  2004/01/21 14:00:09  ncq
# - no delete button as per Richards order :-)
#
# Revision 1.52  2004/01/18 21:51:36  ncq
# - better tooltips on standard buttons
# - simplify vaccination edit area
# - vaccination - _save_modified_entry()
#
# Revision 1.51  2004/01/12 16:23:29  ncq
# - SetValueStyle() -> _decorate_editarea_field()
# - add phrase wheels to vaccination edit area
#
# Revision 1.50  2003/12/29 16:48:14  uid66147
# - try to merge the "good" concepts so far
# - overridden _define_fields|prompts() now use generic _add_field|prompt()
#   helpers to define the layout
# - generic do_layout() actually creates the layout
# - generic _on_*_button_pressed() now call overridden _save_new|updated_entry()
# - apply concepts to vaccination and allergy edit areas
# - vaccination edit area actually saves new entries by way of gmClinicalRecord.add_vaccination()
# - other edit areas still broken
#
# Revision 1.49  2003/12/02 02:03:35  ncq
# - improve logging
#
# Revision 1.48  2003/12/02 02:01:24  ncq
# - cleanup
#
# Revision 1.47  2003/12/01 01:04:01  ncq
# - remove excess verbosity
#
# Revision 1.46  2003/11/30 01:08:25  ncq
# - removed dead yaml code
#
# Revision 1.45  2003/11/29 01:32:55  ncq
# - fix no-exit-without-patient error
# - start cleaning up the worst mess
#
# Revision 1.44  2003/11/28 16:20:31  hinnef
# - commented out all yaml code; this code should be removed lateron
#
# Revision 1.43  2003/11/25 16:38:46  hinnef
# - adjust field sizes in requests, measurements and vaccinations
#
# Revision 1.42  2003/11/22 02:02:53  ihaywood
# fixed syntax errors
#
# Revision 1.41  2003/11/20 22:43:24  hinnef
# added save_data() methods to prevent hanging up on exit
#
# Revision 1.40  2003/11/20 01:37:09  ncq
# - no code in gmEditArea has any business of calling
#   gmCurrentPatient() with an explicit ID
#
# Revision 1.39  2003/11/19 23:23:53  sjtan
#
# extract birthyear from gmDateTime object returned by gmDemographicRecord.getDOB() locally.
#
# Revision 1.38  2003/11/19 13:55:57  ncq
# - Syans forgot to accept kw arg list in _check_unsaved_data()
#
# Revision 1.37  2003/11/17 10:56:37  sjtan
#
# synced and commiting.
#
# Revision 1.6  2003/10/26 00:58:53  sjtan
#
# use pre-existing signalling
#
# Revision 1.5  2003/10/25 16:13:26  sjtan
#
# past history , can add  after selecting patient.
#
# Revision 1.4  2003/10/25 08:29:40  sjtan
#
# uses gmDispatcher to send new currentPatient objects to toplevel gmGP_ widgets. Proprosal to use
# yaml serializer to store editarea data in  narrative text field of clin_root_item until
# clin_root_item schema stabilizes.
#
# Revision 1.3  2003/10/24 04:20:17  sjtan
#
# yaml side-effect code; remove later if not useful.
#
# Revision 1.2  2003/10/24 03:50:36  sjtan
#
# make sure smaller widgets such as checkboxes and radiobuttons on input_fields;
# "pastable" yaml input_field maps output from print statements.
#
# Revision 1.1  2003/10/23 06:02:39  sjtan
#
# manual edit areas modelled after r.terry's specs.
#
# Revision 1.35  2003/10/19 12:16:48  ncq
# - cleanup
# - add event handlers to standard buttons
# - fix gmDateInput args breakage
#
# Revision 1.34  2003/09/21 00:24:19  sjtan
#
# rollback.
#
# Revision 1.32  2003/06/24 12:58:15  ncq
# - added TODO item
#
# Revision 1.31  2003/06/01 01:47:33  sjtan
#
# starting allergy connections.
#
# Revision 1.30  2003/05/27 16:02:03  ncq
# - some comments, some cleanup; I like the direction we are heading
#
# Revision 1.29  2003/05/27 14:08:51  sjtan
#
# read the gmLog now.
#
# Revision 1.28  2003/05/27 14:04:42  sjtan
#
# test events mapping field values on ok button press: K + I were right,
# this is a lot more direct than handler scripting; just needed the additional
# programming done on the ui (per K).
#
# Revision 1.27  2003/05/27 13:18:54  ncq
# - coding style, as usual...
#
# Revision 1.26  2003/05/27 13:00:41  sjtan
#
# removed redundant property support, read directly from __dict__
#
# Revision 1.25  2003/05/26 15:42:52  ncq
# - some minor coding style cleanup here and there, hopefully don't break Syan's work
#
# Revision 1.24  2003/05/26 15:14:36  sjtan
#
# ok , following the class style of gmEditArea refactoring.
#
# Revision 1.23  2003/05/26 14:16:16  sjtan
#
# now trying to use the global capitalized ID  to differentiate fields through one
# checkbox, text control , button event handlers. Any controls without ID need
# to have one defined. Propose to save the fields as a simple list on root item,
# until the subclass tables of root_item catch up. Slow work because manual, but
# seems to be what the doctor(s) ordered.
#
# Revision 1.22  2003/05/25 04:43:15  sjtan
#
# PropertySupport misuse for notifying Configurator objects during gui construction,
# more debugging info
#
# Revision 1.21  2003/05/23 14:39:35  ncq
# - use gmDateInput widget in gmAllergyEditArea
#
# Revision 1.20  2003/05/21 15:09:18  ncq
# - log warning on use of old style edit area
#
# Revision 1.19  2003/05/21 14:24:29  ncq
# - re-added old lines generating code for reference during conversion
#
# Revision 1.18  2003/05/21 14:11:26  ncq
# - much needed rewrite/cleanup of gmEditArea
# - allergies/family history edit area adapted to new gmEditArea code
# - old code still there for non-converted edit areas
#
# Revision 1.17  2003/02/14 01:24:54  ncq
# - cvs metadata keywords
#
