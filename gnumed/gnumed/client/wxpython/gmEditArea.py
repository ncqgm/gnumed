#====================================================================
# GnuMed
# GPL
#====================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmEditArea.py,v $
# $Id: gmEditArea.py,v 1.56 2004-01-26 18:25:07 ncq Exp $
__version__ = "$Revision: 1.56 $"
__author__ = "R.Terry, K.Hilbert"

# TODO: standard SOAP edit area
#====================================================================
import sys, traceback, time

if __name__ == "__main__":
	sys.path.append('.')
	sys.path.append ("../python-common/")
	sys.path.append ("../business/")

import gmLog
_log = gmLog.gmDefLog

if __name__ == "__main__":
	import gmI18N

import gmExceptions, gmDateTimeInput, gmDispatcher, gmSignals, gmPatient, gmGuiBroker, gmMatchProvider, gmPhraseWheel

_gb = gmGuiBroker.GuiBroker()

from wxPython.wx import *

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

wxID_BTN_OK = wxNewId()
wxID_BTN_Clear = wxNewId()

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
	widget.SetFont(wxFont(12, wxSWISS, wxNORMAL, wxBOLD, false, ''))

#====================================================================
#text control class to be later replaced by the gmPhraseWheel
#--------------------------------------------------------------------
class cEditAreaField(wxTextCtrl):
	def __init__ (self, parent, id = -1, pos = wxDefaultPosition, size=wxDefaultSize):
		wxTextCtrl.__init__(self,parent,id,"",pos, size ,wxSIMPLE_BORDER)
		_decorate_editarea_field(self)
#====================================================================
#====================================================================
class gmEditArea(wxPanel):
	def __init__(self, parent, id, aType = None):
		# sanity checks
		if aType not in _known_edit_area_types:
			_log.Log(gmLog.lErr, 'unknown edit area type: [%s]' % aType)
			raise gmExceptions.ConstructorError, 'unknown edit area type: [%s]' % aType
		self._type = aType

		# init main background panel
		wxPanel.__init__(self, parent, id, style = wxNO_BORDER | wxTAB_TRAVERSAL)
		self.SetBackgroundColour(wxColor(222,222,222))

		self.fields = {}
		self.prompts = {}
		self.__do_layout()

		self.input_fields = {}
#		szr_prompts = self.__make_prompts(_prompt_defs[self._type])
#		self.szr_editing_area = self.__make_editing_area()
		# stack prompts and fields horizontally
#		self.szr_main_panels = wxBoxSizer(wxHORIZONTAL)
#		self.szr_main_panels.Add(szr_prompts, 11, wxEXPAND)
#		self.szr_main_panels.Add(5, 0, 0, wxEXPAND)
#		self.szr_main_panels.Add(self.szr_editing_area, 90, wxEXPAND)

		# use sizer for border around everything plus a little gap
		# FIXME: fold into szr_main_panels ?
#		self.szr_central_container = wxBoxSizer(wxHORIZONTAL)
#		self.szr_central_container.Add(self.szr_main_panels, 1, wxEXPAND | wxALL, 5)

#		self.SetSizer(self.szr_central_container)
#		self.szr_central_container.Fit(self)
#		self.SetAutoLayout(true)

		self._postInit()
		self.old_data = {} 

		self.data_ID = None
		self.patient = gmPatient.gmCurrentPatient()
		self.__register_events()
		self.Show(true)
	#----------------------------------------------------------------
	# internal helpers
	#----------------------------------------------------------------
	def __do_layout(self):
		# define prompts and fields
		self._define_prompts()
		fields_pnl = wxPanel(self, -1, style = wxRAISED_BORDER | wxTAB_TRAVERSAL)
		self._define_fields(parent = fields_pnl)
		# and generate edit area from it
		szr_prompts = self.__generate_prompts()
		szr_fields = self.__generate_fields(parent = fields_pnl)

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
		self.SetSizer(self.szr_central_container)
		self.szr_central_container.Fit(self)
		self.SetAutoLayout(true)
	#----------------------------------------------------------------
	def __generate_prompts(self):
		if len(self.fields) != len(self.prompts):
			_log.Log(gmLog.lErr, '[%s]: #fields != #prompts' % self.__class__.__name__)
			return None
		# prompts live on a panel
		prompt_pnl = wxPanel(self, -1, wxDefaultPosition, wxDefaultSize, wxSIMPLE_BORDER)
		prompt_pnl.SetBackgroundColour(richards_light_gray)
		# make them
		gszr = wxGridSizer (len(self.fields), 1, 2, 2)
		color = richards_aqua
		lines = self.prompts.keys()
		lines.sort()
		for line in lines:
			label, color = self.prompts[line]
			prompt = self.__make_prompt(prompt_pnl, "%s " % label, color)
			gszr.Add(prompt, 0, wxEXPAND | wxALIGN_RIGHT)
		# put sizer on panel
		prompt_pnl.SetSizer(gszr)
		gszr.Fit(prompt_pnl)
		prompt_pnl.SetAutoLayout(true)

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
	def __generate_fields(self, parent):
		parent.SetBackgroundColour(wxColor(222,222,222))
		# rows, cols, hgap, vgap
		gszr = wxGridSizer(len(self.fields), 1, 2, 2)

		lines = self.fields.keys()
		lines.sort()
		for line in lines:
			szr_line = wxBoxSizer(wxHORIZONTAL)
			positions = self.fields[line].keys()
			positions.sort()
			for pos in positions:
				field, weight = self.fields[line][pos]
				szr_line.Add(field, weight, wxEXPAND)
			gszr.Add(szr_line, 0, flag = wxEXPAND | wxALIGN_LEFT)
		# put them on the panel
		parent.SetSizer(gszr)
		gszr.Fit(parent)
		parent.SetAutoLayout(true)

		# make shadow below edit fields in gray
		shadow_below_edit_fields = wxWindow(self, -1, wxDefaultPosition, wxDefaultSize, 0)
		shadow_below_edit_fields.SetBackgroundColour(richards_coloured_gray)
		szr_shadow_below_edit_fields = wxBoxSizer(wxHORIZONTAL)
		szr_shadow_below_edit_fields.Add(5, 0, 0, wxEXPAND)
		szr_shadow_below_edit_fields.Add(shadow_below_edit_fields, 12, wxEXPAND)

		# stack edit fields and shadow vertically
		vszr_edit_fields = wxBoxSizer(wxVERTICAL)
		vszr_edit_fields.Add(parent, 92, wxEXPAND)
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
	#----------------------------------------------------------------
	def __make_prompt(self, parent, aLabel, aColor):
		# FIXME: style for centering in vertical direction ?
		prompt = wxStaticText(
			parent,
			-1,
			aLabel,
			style = wxALIGN_RIGHT | wxST_NO_AUTORESIZE
		)
		prompt.SetFont(wxFont(10, wxSWISS, wxNORMAL, wxBOLD, false, ''))
		prompt.SetForegroundColour(aColor)
		return prompt
	#----------------------------------------------------------------
	# intra-class API
	#----------------------------------------------------------------
	def _add_prompt(self, line=None, label=None, color=richards_blue):
		if None in (line, label):
			_log.Log(gmLog.lErr, 'argument error in [%s]: line=%s, label=%s' % (self.__class__.__name__, line, prompt))
		if not self.prompts.has_key(line):
			self.prompts[line] = {}
		self.prompts[line] = (label, color)
	#----------------------------------------------------------------
	def _add_field(self, line=None, pos=None, widget=None, weight=0):
		if None in (line, pos, widget):
			_log.Log(gmLog.lErr, 'argument error in [%s]: line=%s, pos=%s, widget=%s' % (self.__class__.__name__, line, pos, widget))
		if not self.fields.has_key(line):
			self.fields[line] = {}
		self.fields[line][pos] = (widget, weight)
	#----------------------------------------------------------------
	def _define_fields(self, parent):
		_log.Log(gmLog.lErr, 'missing override in [%s]' % self.__class__.__name__)
	#----------------------------------------------------------------
	def _define_prompts(self):
		_log.Log(gmLog.lErr, 'missing override in [%s]' % self.__class__.__name__)
	#----------------------------------------------------------------
	def _make_standard_buttons(self, parent):
		self.btn_OK = wxButton(parent, wxID_BTN_OK, _("OK"))
		self.btn_OK.SetToolTipString(_('save entry into medical record'))
		self.btn_Clear = wxButton(parent, wxID_BTN_Clear, _("Clear"))
		self.btn_Clear.SetToolTipString(_('initialize input fields for new entry'))

		szr_buttons = wxBoxSizer(wxHORIZONTAL)
		szr_buttons.Add(self.btn_OK, 1, wxEXPAND | wxALL, 1)
		szr_buttons.Add(5, 0, 0)
		szr_buttons.Add(self.btn_Clear, 1, wxEXPAND | wxALL, 1)

		return szr_buttons
	#----------------------------------------------------------------
	# to be obsoleted
	#----------------------------------------------------------------
	def __make_prompts(self, prompt_labels):
		# prompts live on a panel
		prompt_pnl = wxPanel(self, -1, wxDefaultPosition, wxDefaultSize, wxSIMPLE_BORDER)
		prompt_pnl.SetBackgroundColour(richards_light_gray)
		# make them
		gszr = wxGridSizer (len(prompt_labels)+1, 1, 2, 2)
		color = richards_aqua
		for prompt in prompt_labels:
			label = self.__make_prompt(prompt_pnl, "%s " % prompt, color)
			gszr.Add(label, 0, wxEXPAND | wxALIGN_RIGHT)
			color = richards_blue
		# put sizer on panel
		prompt_pnl.SetSizer(gszr)
		gszr.Fit(prompt_pnl)
		prompt_pnl.SetAutoLayout(true)

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
		fields_pnl.SetAutoLayout(true)

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
	#--------------------------------------------------------
	# event handling
	#--------------------------------------------------------
	def __register_events(self):
		# connect standard buttons
		EVT_BUTTON(self.btn_OK, wxID_BTN_OK, self._on_OK_btn_pressed)
		EVT_BUTTON(self.btn_Clear, wxID_BTN_Clear, self._on_clear_btn_pressed)
		#self._register_dirty_editarea_listener()

		# client internal signals
		gmDispatcher.connect(signal = gmSignals.activating_patient(), receiver = self._check_unsaved_data)
		gmDispatcher.connect(signal = gmSignals.application_closing(), receiver = self._check_unsaved_data)
		gmDispatcher.connect(signal = gmSignals.patient_selected(), receiver = self.on_patient_selected)

		return 1
	#--------------------------------------------------------
	# handlers
	#--------------------------------------------------------
	def _on_OK_btn_pressed(self, event):
		event.Skip()
		if self.data_ID is None:
			print "must be new entry"
			self._save_new_entry()
		else:
			print "must be modified entry"
			self._save_modified_entry()
#		self._pre_save_data()
	#--------------------------------------------------------
	def _on_clear_btn_pressed(self, event):
		# FIXME: check for unsaved data
		self.set_data()
		event.Skip()
	#--------------------------------------------------------
	def on_patient_selected( self, **kwds):
		# - check if patient is connected
		# - check if we've got data to save
		# - save it
		pass
#		self._updateUI()
#		self._init_fields()




#-------NOT USED , obsolete dirty check mechanism
#-------------------------------------------------------------------------------------------------------------

	def _register_dirty_editarea_listener(self):   # a different way of check dirty is to save the input field values
		self.monitoring_dirty = 1
		import inspect
		for k, widget in self.input_fields.items():
			#classes = inspect.getmro(widget)  # doesn't work because wx classes doesn't use mro scheme.
			
			#for c in classes:
			#	if c.__name__ == 'wxTextCtrl':

			if widget.__class__.__name__ in ['wxTextCtrl', 'cEditAreaField']:
					EVT_TEXT( widget, widget.GetId(), self._mark_dirty)
			if widget.__class__.__name__ in ['wxRadioButton']:
					EVT_RADIOBUTTON(widget, widget.GetId(), self._mark_dirty)
			if widget.__class__.__name__ in ['wxCheckBox' ]:
					EVT_CHECKBOX(widget, widget.GetId(), self._mark_dirty)

			
	
	def _mark_dirty(self, event):
		event.Skip()
		if self.monitoring_dirty:
			self.dirty = 1
		else:
			pass

#----------DIRTY DATA CHECK: checks original loaded data with current input values , and sets dirty if any changes
#----------------------------------------------------------------------------------------------------------------------			

	def _check_unsaved_data(self, **kwds):
		if not self.patient.is_connected():
			return 1
		try:
			self._pre_save_data()
			self._init_fields()
		except StandardError:
			_log.LogException('[%s] lossage' % self.__class__.__name__, verbose=0)
			return None
		return 1

	def _pre_save_data(self):
		#if not self.__dict__.has_key('dirty') or self.dirty == 0:
		if not self.is_dirty():
			return
		self._save_data()

	
	def set_old_data( self, map):
		self.old_data = map
	
	def is_dirty(self):
		map = self.getInputFieldValues()
		dirty = 0
		for k,v in map.items():
			if self.old_data.get(k, None) <>  v:
				dirty = 1
				break
		return dirty	

	def _default_init_fields(self):
		#self.dirty = 0  #this flag is for patient_activating event to save any unsaved entries
		self.setInputFieldValues( self._get_init_values())
		self.data_ID = None

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
	
	#--------------------------------------------------------
	
	def _save_data(self):
		_log.Log(gmLog.lErr, 'programmer forgot to define _save_data() for [%s] (%s)' % (self._type, self.__class__.__name__))
		_log.Log(gmLog.lInfo, 'child classes of gmEditArea *must* override this function')
		raise AttributeError
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
		return self.data_ID 

	def setDataId(self, id):
		self.data_ID = id
	

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
		try:
			gmEditArea.__init__(self, parent, id, aType = 'past history')
		except gmExceptions.ConstructorError:
			_log.LogExceptions('cannot instantiate past Hx edit area', sys.exc_info())
			raise
	#----------------------------------------------------------------
	def _make_edit_lines(self, parent):
		_log.Log(gmLog.lData, "making past Hx lines")
		lines = []
		#self.gszr = wxGridSizer( 8, 1, 2, 2)
		self.txt_condition = cEditAreaField(parent, PHX_CONDITION,wxDefaultPosition,wxDefaultSize)
	#@	self.rb_laterality = wxRadioBox( parent, -1,   "Side", wxDefaultPosition, wxDefaultSize,  [ _("Left"), _("Right"), _("Both")]  )



		self.rb_sidenone= wxRadioButton(parent, -1,  _("None"), wxDefaultPosition,wxDefaultSize)
		self.rb_sideleft = wxRadioButton(parent, PHX_LEFT, _("(L)"), wxDefaultPosition,wxDefaultSize)
		self.rb_sideright = wxRadioButton(parent,  PHX_RIGHT, _("(R)"), wxDefaultPosition,wxDefaultSize,wxSUNKEN_BORDER)
		self.rb_sideboth = wxRadioButton(parent,  PHX_BOTH, _("Both"), wxDefaultPosition,wxDefaultSize)
		rbsizer = wxBoxSizer(wxHORIZONTAL)
		rbsizer.Add(self.rb_sidenone,1,wxEXPAND)
		rbsizer.Add(self.rb_sideleft,1,wxEXPAND)
		rbsizer.Add(self.rb_sideright,1,wxEXPAND) 
		rbsizer.Add(self.rb_sideboth,1,wxEXPAND)
		szr1 = wxBoxSizer(wxHORIZONTAL)
		szr1.Add(self.txt_condition, 4, wxEXPAND)
		szr1.Add(rbsizer, 3, wxEXPAND)
		#szr1.Add(self.rb_laterality, 3, wxEXPAND)
		lines.append(szr1)
#			self.sizer_line1.Add(self.rb_sideleft,1,wxEXPAND|wxALL,2)
#			self.sizer_line1.Add(self.rb_sideright,1,wxEXPAND|wxALL,2)
#			self.sizer_line1.Add(self.rb_sideboth,1,wxEXPAND|wxALL,2)
		# line 2A
		
		self.txt_notes1 = cEditAreaField(parent, PHX_NOTES,wxDefaultPosition,wxDefaultSize)
		lines.append(self.txt_notes1)
		# line 3
		self.txt_notes2= cEditAreaField(parent, PHX_NOTES2,wxDefaultPosition,wxDefaultSize)
		lines.append(self.txt_notes2)
		# line 4
		self.txt_agenoted = cEditAreaField(parent,  PHX_AGE, wxDefaultPosition, wxDefaultSize)
		szr4 = wxBoxSizer(wxHORIZONTAL)
		szr4.Add(self.txt_agenoted, 1, wxEXPAND)
		szr4.Add(5, 0, 5)
		lines.append(szr4)
		# line 5
		self.txt_yearnoted  = cEditAreaField(parent, PHX_YEAR,wxDefaultPosition,wxDefaultSize)
		szr5 = wxBoxSizer(wxHORIZONTAL)
		szr5.Add(self.txt_yearnoted, 1, wxEXPAND)
		szr5.Add(5, 0, 5)
		lines.append(szr5)
		# line 6
		self.cb_active = wxCheckBox(parent,  PHX_ACTIVE, _("Active"), wxDefaultPosition,wxDefaultSize, wxNO_BORDER)
		self.cb_operation = wxCheckBox(parent,  PHX_OPERATION, _("Operation"), wxDefaultPosition,wxDefaultSize, wxNO_BORDER)
		self.cb_confidential = wxCheckBox(parent,  PHX_CONFIDENTIAL , _("Confidential"), wxDefaultPosition,wxDefaultSize, wxNO_BORDER)
		self.cb_significant = wxCheckBox(parent,  PHX_SIGNIFICANT, _("Significant"), wxDefaultPosition,wxDefaultSize, wxNO_BORDER)
		szr6 = wxBoxSizer(wxHORIZONTAL)
		szr6.Add(self.cb_active, 1, wxEXPAND)
		szr6.Add(self.cb_operation, 1, wxEXPAND)
		szr6.Add(self.cb_confidential, 1, wxEXPAND)
		szr6.Add(self.cb_significant, 1, wxEXPAND)
		lines.append(szr6)
		# line 7
		self.txt_progressnotes  = cEditAreaField(parent, PHX_PROGRESSNOTES ,wxDefaultPosition,wxDefaultSize)
		lines.append(self.txt_progressnotes)
		# line 8
		szr8 = wxBoxSizer(wxHORIZONTAL)
		szr8.Add(5, 0, 6)
		szr8.Add(self._make_standard_buttons(parent), 0, wxEXPAND)
		lines.append(szr8)


		self.input_fields = {
			"condition": self.txt_condition,
			"notes1": self.txt_notes1,
			"notes2": self.txt_notes2,
			"age": self.txt_agenoted,
			"year": self.txt_yearnoted,
			"progress": self.txt_progressnotes,
			"active": self.cb_active,
			"operation": self.cb_operation,
			"confidential": self.cb_confidential,
			"significant": self.cb_significant,
			"both": self.rb_sideboth,
			"left": self.rb_sideleft,
			"right": self.rb_sideright,
			"none": self.rb_sidenone
		}

		return lines


	def  _postInit(self):
		#handling of auto age or year filling.
		EVT_KILL_FOCUS( self.input_fields['age'], self._ageKillFocus)
		EVT_KILL_FOCUS( self.input_fields['year'], self._yearKillFocus)

	def _ageKillFocus( self, event):	
		# skip first, else later failure later in block causes widget to be unfocusable
		event.Skip()	
		try :
			year = self._getBirthYear() + int(self.input_fields['age'].GetValue().strip() )
			self.input_fields['year'].SetValue( str (year) )
		except:
			pass

	def _getBirthYear(self):
		try:
			birthyear = int(str(self.patient.get_demographic_record().getDOB()).split('-')[0]) 
		except:
			birthyear = time.localtime()[0]
		
		return birthyear
		
	def _yearKillFocus( self, event):	
		event.Skip()	
		try:
			age = int(self.input_fields['year'].GetValue().strip() ) - self._getBirthYear() 
			self.input_fields['age'].SetValue( str (age) )
		except:
			pass

	def get_fields_formatting_values(self):
		fields = [	"condition", 
				"notes1", 
				"notes2", 
				"age", 
				"year", 
				"progress", 
				"active", 
				"operation", 
				"confidential", 
				"significant", 
				"both", 
				"left", 
				"right", 
				"none"  ]
				
		values = self.getInputFieldValues(fields)
		values['clin_history_id'] = self.getDataId()
		s= "'%s'"
		n = "%d"
		formatting = {	"condition":s,
				"notes1":s, 
				"notes2":s, 
				"age":s, 
				"year":s, 
				"progress":s, 
				"active":n, 
				"operation":n, 
				"confidential":n, 
				"significant":n, 
				"both":n, 
				"left":n, 
				"right":n, 
				"none":n  }

		return fields,  formatting, values
		

	

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
			return	time.localtime()[0] - self.patient.get_demographic_record().getBirthYear()
		except:
			return 0

	def _get_init_values(self):
		values = gmPastHistoryEditArea.__init_values
		values["age"] = str( self._getDefaultAge())
		return values 
		
		
	def _save_data(self):
		clinical = self.patient.get_clinical_record().get_past_history()
		if self.getDataId() == None:
			id = clinical.create_history( self.get_fields_formatting_values() )
			self.setDataId(id)
			return

		clinical.update_history( self.get_fields_formatting_values(), self.getDataId() )

#========================================================
class gmAllergyEditArea(gmEditArea):

	def __init__(self, parent, id):
		try:
			gmEditArea.__init__(self, parent, id, aType = 'allergy')
		except gmExceptions.ConstructorError:
			_log.LogException('cannot instantiate allergy edit area', sys.exc_info(), verbose=1)
			raise
	#----------------------------------------------------
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
			weight = 1
		)
		# line 2
		self.fld_substance = cEditAreaField(parent)
		self._add_field(
			line = 2,
			pos = 1,
			widget = self.fld_substance,
			weight = 1
		)
		# line 3
		self.fld_generic = cEditAreaField(parent)
		self._add_field(
			line = 3,
			pos = 1,
			widget = self.fld_generic,
			weight = 6
		)
		self.fld_generic_specific = wxCheckBox(
			parent,
			-1,
			_("generics specific"),
			style = wxNO_BORDER
		)
		self._add_field(
			line = 3,
			pos = 2,
			widget = self.fld_generic_specific,
			weight = 0
		)
		# line 4
		self.fld_drug_class = cEditAreaField(parent)
		self._add_field(
			line = 4,
			pos = 1,
			widget = self.fld_drug_class,
			weight = 0
		)
		# line 5
		# FIXME: add allergene, atc_code ?
		self.fld_reaction = cEditAreaField(parent)
		self._add_field(
			line = 5,
			pos = 1,
			widget = self.fld_reaction,
			weight = 1
		)
		# line 6
		self.fld_progress_note = cEditAreaField(parent)
		self._add_field(
			line = 6,
			pos = 1,
			widget = self.fld_progress_note,
			weight = 1
		)
		# line 7
		self.fld_is_allergy = wxRadioButton(parent, -1, _("Allergy"))
		self._add_field(
			line = 7,
			pos = 1,
			widget = self.fld_is_allergy,
			weight = 2
		)
		self.fld_is_sensitivity = wxRadioButton(parent, -1, _("Sensitivity"))
		self._add_field(
			line = 7,
			pos = 2,
			widget = self.fld_is_sensitivity,
			weight = 2
		)
		self.fld_is_definite_allergy = wxCheckBox(
			parent,
			-1,
			_("Definite"),
			style = wxNO_BORDER
		)
		self._add_field(
			line = 7,
			pos = 3,
			widget = self.fld_is_definite_allergy,
			weight = 2
		)
		self._add_field(
			line = 7,
			pos = 4,
			widget = self._make_standard_buttons(parent),
			weight = 1
		)
	#----------------------------------------------------
	def _define_prompts(self):
		self._add_prompt(line = 1, label = _("Date Noted"))
		self._add_prompt(line = 2, label = _("Brand/Substance"))
		self._add_prompt(line = 3, label = _("Generic"))
		self._add_prompt(line = 4, label = _("Drug Class"))
		self._add_prompt(line = 5, label = _("Reaction"))
		self._add_prompt(line = 6, label = _("Progress Note"))
		self._add_prompt(line = 7, label = '')
	#----------------------------------------------------
	def _save_new_entry(self):
		allergy = {}
		allergy['date noted'] = self.fld_date_noted.GetValue()
		allergy['substance'] = self.fld_substance.GetValue()
		allergy['generic'] = self.fld_generic.GetValue()
		allergy['is generic specific'] = self.fld_generic_specific.GetValue()
		allergy['drug class'] = self.fld_drug_class.GetValue()
		allergy['reaction'] = self.fld_reaction.GetValue()
		allergy['progress note'] = self.fld_progress_note.GetValue()
		allergy['is allergy'] = self.fld_is_allergy.GetValue()
		allergy['is sensitivity'] = self.fld_is_sensitivity.GetValue()
		allergy['is definite'] = self.fld_is_definite_allergy.GetValue()
		# FIXME: validation
		epr = self.patient.get_clinical_record()
		status, data = epr.add_allergy(allergy)
		if status is None:
			wxBell()
			_gb['main.statustext'](_('Cannot save allergy.'))
			return None
		_gb['main.statustext'](_('Allergy saved.'))
		self.data_ID = data
		return 1
	#----------------------------------------------------
	def set_data(self, allergy = None):
		try:
			self.data_ID = allergy['ID']
		except KeyError:
			_log.LogException('must have ID in allergy', sys.exc_info(), verbose=0)
			return None
		# defaults
		if allergy is None:
			self.fld_date_noted.SetValue((time.strftime('%Y-%m-%d', time.localtime())))
			self.fld_substance.SetValue('')
			self.fld_generic.SetValue('')
			self.fld_generic_specific.SetValue(0)
			self.fld_drug_class.SetValue('')
			self.fld_reaction.SetValue('')
			self.fld_progress_note.SetValue('')
			self.fld_is_allergy.SetValue(1)
			self.fld_is_sensitivity.SetValue(0)
			self.fld_is_definite_allergy.SetValue(1)
			return 1
		# or data
		try: self.fld_date_noted.SetValue(allergy['date noted'])
		except KeyError: pass
		try: self.fld_substance.SetValue(allergy['substance'])
		except KeyError: pass

		try: self.fld_progress_note.SetValue(allergy['progress note'])
		except KeyError: pass


		try:
			if allergy['is booster']:
				self.fld_is_booster.SetValue(1)
			else:
				self.fld_is_booster.SetValue(0)
		except KeyError: pass

		return 1
#========================================================
class gmVaccinationEditArea(gmEditArea):
	"""
	- warn on apparent duplicates
	- ask if "missing" (= previous, non-recorded) vaccinations
	  should be estimated and saved (add note "auto-generated")
	"""
	def __init__(self, parent, id):
		try:
			gmEditArea.__init__(self, parent, id, aType = 'vaccination')
		except gmExceptions.ConstructorError:
			_log.LogException('cannot instantiate vaccination edit area', sys.exc_info(), verbose=1)
			raise
	#----------------------------------------------------
	def _define_fields(self, parent):
#		# regime/disease
#		query = """
#			select distinct on (regime)
#				pk_regime,
#				regime || ' - ' || _(indication)
#			from
#				v_vacc_regimes
#			where
#				regime || ' ' || _(indication) %(fragment_condition)s
#			limit 25"""

		# vaccine
		# FIXME: move to gmClinicalRecord or gmVaccination
		query = """
			select
				id,
				trade_name
			from
				vaccine
			where
				short_name || ' ' || trade_name %(fragment_condition)s
			limit 25"""
		mp = gmMatchProvider.cMatchProvider_SQL2('historica', query)
		mp.setThresholds(aWord=2, aSubstring=4)
		self.fld_vaccine = gmPhraseWheel.cPhraseWheel(
			parent = parent
			, id = -1
			, aMatchProvider = mp
			, style = wxSIMPLE_BORDER
		)
		_decorate_editarea_field(self.fld_vaccine)
		self._add_field(
			line = 1,
			pos = 1,
			widget = self.fld_vaccine,
			weight = 3
		)

		# FIXME: gmDateTimeInput
		self.fld_date_given = cEditAreaField(parent)
		self._add_field(
			line = 2,
			pos = 1,
			widget = self.fld_date_given,
			weight = 2
		)

		# Batch No (http://www.fao.org/docrep/003/v9952E12.htm)
		self.fld_batch_no_lbl = wxStaticText(
			parent,
			-1,
			_("  Serial # "),
			style = wxALIGN_CENTER_VERTICAL
		)
		self._add_field(
			line = 3,
			pos = 1,
			widget = self.fld_batch_no_lbl,
			weight = 0
		)
		self.fld_batch_no = cEditAreaField(parent)
		self._add_field(
			line = 3,
			pos = 2,
			widget = self.fld_batch_no,
			weight = 1
		)

		# site given
		# FIXME: context -> vaccine
		query = """
			select distinct on (tmp.site)
				tmp.id, tmp.site
			from (
				select id, site
				from vaccination
				group by id, site
				order by count(site)
			) as tmp
			where
				tmp.site %(fragment_condition)s
			limit 10"""
		mp = gmMatchProvider.cMatchProvider_SQL2('historica', query)
		mp.setThresholds(aWord=1, aSubstring=3)
		self.fld_site_given = gmPhraseWheel.cPhraseWheel(
			parent = parent
			, id = -1
			, aMatchProvider = mp
			, style = wxSIMPLE_BORDER
		)
		_decorate_editarea_field(self.fld_site_given)
		self._add_field(
			line = 4,
			pos = 1,
			widget = self.fld_site_given,
			weight = 1
		)

		# progress note
		query = """
			select distinct on (narrative)
				id, narrative
			from
				vaccination
			where
				narrative %(fragment_condition)s
			limit 30"""
		mp = gmMatchProvider.cMatchProvider_SQL2('historica', query)
		mp.setThresholds(aWord=3, aSubstring=5)
		self.fld_progress_note = gmPhraseWheel.cPhraseWheel(
			parent = parent
			, id = -1
			, aMatchProvider = mp
			, style = wxSIMPLE_BORDER
		)
		_decorate_editarea_field(self.fld_progress_note)
		self._add_field(
			line = 5,
			pos = 1,
			widget = self.fld_progress_note,
			weight = 1
		)

		self._add_field(
			line = 6,
			pos = 1,
			widget = self._make_standard_buttons(parent),
			weight = 1
		)
		return 1
	#----------------------------------------------------
	def _define_prompts(self):
		self._add_prompt(line = 1, label = _("Vaccine"))
		self._add_prompt(line = 2, label = _("Date given"))
		self._add_prompt(line = 3, label = _("Serial #"))
		self._add_prompt(line = 4, label = _("Site injected"))
		self._add_prompt(line = 5, label = _("Progress Note"))
		self._add_prompt(line = 6, label = '')
	#----------------------------------------------------
	def _save_new_entry(self):
		vacc = {}
		vacc['vaccine'] = self.fld_vaccine.GetValue()
		vacc['batch no'] = self.fld_batch_no.GetValue()
		vacc['date given'] = self.fld_date_given.GetValue()
		vacc['site given'] = self.fld_site_given.GetValue()
		vacc['progress note'] = self.fld_progress_note.GetValue()
		# FIXME: validation
		epr = self.patient.get_clinical_record()
		status, data = epr.add_vaccination(vacc)
		if status is None:
			wxBell()
			_gb['main.statustext'](_('Cannot save vaccination: %s') % data)
			return None
		_gb['main.statustext'](_('Vaccination saved.'))
		self.data_ID = data
		return 1
	#----------------------------------------------------
	def _save_modified_entry(self):
		vacc = {}
		vacc['ID'] = self.data_ID
		vacc['vaccine'] = self.fld_vaccine.GetValue()
		vacc['batch no'] = self.fld_batch_no.GetValue()
		vacc['date given'] = self.fld_date_given.GetValue()
		vacc['site given'] = self.fld_site_given.GetValue()
		vacc['progress note'] = self.fld_progress_note.GetValue()
		# FIXME: validation
		epr = self.patient.get_clinical_record()
		status, data = epr.update_vaccination(vacc)
		if status is None:
			wxBell()
			_gb['main.statustext'](_('Cannot update vaccination: %s') % data)
			return None
		_gb['main.statustext'](_('Vaccination updated.'))
		return 1
	#----------------------------------------------------
	def set_data(self, aVacc = None):
		# defaults
		self.data_ID = None
		if aVacc is None:
			self.fld_vaccine.SetValue('')
			self.fld_batch_no.SetValue('')
			self.fld_date_given.SetValue((time.strftime('%Y-%m-%d', time.localtime())))
			self.fld_site_given.SetValue(_('left/right deltoid'))
			self.fld_progress_note.SetValue('')
			return 1
		# or data
		try: self.data_ID = aVacc['ID']
		except KeyError:
			_log.LogException('must have ID in aVacc', sys.exc_info(), verbose=0)
			return None
		try: self.fld_vaccine.SetValue(aVacc['vaccine'])
		except KeyError: pass
		try: self.fld_batch_no.SetValue(aVacc['batch no'])
		except KeyError: pass
		try: self.fld_date_given.SetValue(aVacc['date given'])
		except KeyError: pass
		try: self.fld_site_given.SetValue(aVacc['site given'])
		except KeyError: pass
		try: self.fld_progress_note.SetValue(aVacc['progress note'])
		except KeyError: pass
		return 1
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
class gmReferralEditArea(gmEditArea):
	extraColumns = [referralColumn2]
		
	def __init__(self, parent, id):
		try:
			gmEditArea.__init__(self, parent, id, aType = 'referral')
		except gmExceptions.ConstructorError:
			stacktrace()

			_log.LogExceptions('cannot instantiate referral edit area', sys.exc_info(),4)
			raise

	
	def _getCheckBoxSizer(self,  list):
		szr = wxBoxSizer(wxHORIZONTAL)
		for x in list:
			szr.Add( x, 1, 0)
		
		return szr

	#----------------------------------------------------------------
	def _make_edit_lines(self, parent):
		_log.Log(gmLog.lData, "making referral lines")
		lines = []
		self.txt_who = cEditAreaField(parent)
		self.txt_org = cEditAreaField(parent)
		self.txt_street1 = cEditAreaField(parent)
		self.txt_street2 = cEditAreaField(parent)
		self.txt_suburb= cEditAreaField(parent)
		self.txt_postcode= cEditAreaField(parent)
		self.txt_for = cEditAreaField(parent)
		#self.txt_copyto = cEditAreaField(parent)

		cb_med = self._makeCheckBox( parent, "medications") 
		cb_fhx = self._makeCheckBox( parent, "family history")
		cb_active = self._makeCheckBox(parent, "active problems")
		cb_past = self._makeCheckBox( parent, "past problems")
		cb_social = self._makeCheckBox(parent, "social history")
		cb_habits = self._makeCheckBox( parent, "habits")
		lines.append(self.txt_who)
		lines.append(self.txt_org)
		lines.append(self.txt_street1)
		lines.append(self.txt_street2)
		lines.append(self.txt_suburb)
		lines.append(self.txt_postcode)
		lines.append(self.txt_for)
		lines.append(self._getCheckBoxSizer( [ cb_med, cb_fhx, cb_social]) )
		lines.append(self._getCheckBoxSizer( [ cb_active, cb_past, cb_habits]) )

		#lines.append(self.txt_progress)
		lines.append(self._make_standard_buttons(parent))
		self.input_fields = {
			"name": self.txt_who,
			"org" : self.txt_org,
			"street1": self.txt_street1,
			"street2": self.txt_street2,
			"suburb": self.txt_suburb,
			"postcode" : self.txt_postcode,
			"for": self.txt_for,
			"include Meds": cb_med,
			"include Family Hx" : cb_fhx,
			"include Active Problems": cb_active,
			"include Past Problems" : cb_past,
			"include Social Hx": cb_social,
			"include Habits": cb_habits
		}
		#return lines
		return self._makeExtraColumns( parent, lines)

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
		self.SetFont(wxFont(10, wxSWISS, wxNORMAL, wxBOLD, false, ''))
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
		self.SetAutoLayout(true)
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
		elif section == gmSECTION_REFERRALS:
			pass
		elif section == gmSECTION_RECALLS:
			pass
		else:
			pass

		self.SetSizer(self.gszr)
		self.gszr.Fit(self)

		self.SetAutoLayout(true)
		self.Show(true)
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
		self.SetAutoLayout(true)
		self.Show(true)

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
#		      self.combo_measurement_type.SetFont(wxFont(12,wxSWISS,wxNORMAL, wxBOLD,false,''))
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
#		      self.combo_tosee.SetFont(wxFont(12,wxSWISS,wxNORMAL, wxBOLD,false,''))
#		      self.combo_tosee.SetForegroundColour(wxColor(255,0,0))
		      #FIXME defaults need to be loaded from database
#		      self.combo_recall_method = wxComboBox(self, ID_RECALLS_CONTACTMETHOD, "", wxDefaultPosition,wxDefaultSize, ['Letter','Telephone','Email','Carrier pigeon'], wxCB_READONLY )
#		      self.combo_recall_method.SetFont(wxFont(12,wxSWISS,wxNORMAL, wxBOLD,false,''))
#		      self.combo_recall_method.SetForegroundColour(wxColor(255,0,0))
		      #FIXME defaults need to be loaded from database
 #                     self.combo_apptlength = wxComboBox(self, ID_RECALLS_APPNTLENGTH, "", wxDefaultPosition,wxDefaultSize, ['brief','standard','long','prolonged'], wxCB_READONLY )
#		      self.combo_apptlength.SetFont(wxFont(12,wxSWISS,wxNORMAL, wxBOLD,false,''))
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
	app = wxPyWidgetTester(size = (400, 200))
	app.SetWidget(gmVaccinationEditArea, -1)
	app.MainLoop()
#	app = wxPyWidgetTester(size = (400, 200))
#	app.SetWidget(gmFamilyHxEditArea, -1)
#	app.MainLoop()
#	app = wxPyWidgetTester(size = (400, 200))
#	app.SetWidget(gmPastHistoryEditArea, -1)
#	app.MainLoop()
#====================================================================
# $Log: gmEditArea.py,v $
# Revision 1.56  2004-01-26 18:25:07  ncq
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
