#====================================================================
# GnuMed
# GPL
#====================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmEditArea.py,v $
# $Id: gmEditArea.py,v 1.36 2003-10-22 21:33:12 hinnef Exp $
__version__ = "$Revision: 1.36 $"
__author__ = "R.Terry, K.Hilbert"

# TODO: standard SOAP edit area
#====================================================================
import sys, traceback

if __name__ == "__main__":
	sys.path.append ("../python-common/")
	sys.path.append ("../business/")

import gmLog
_log = gmLog.gmDefLog

if __name__ == "__main__":
	import gmI18N

import gmExceptions, gmDateTimeInput, gmDispatcher, gmSignals

from wxPython.wx import *

ID_PROGRESSNOTES = wxNewId()
gmSECTION_SUMMARY = 1
gmSECTION_DEMOGRAPHICS = 2
gmSECTION_CLINICALNOTES = 3
gmSECTION_FAMILYHISTORY = 4
gmSECTION_PASTHISTORY = 5
gmSECTION_VACCINATION = 6
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
ID_BTN_CLEAR = wxNewId()
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

wxID_BTN_Save = wxNewId()
wxID_BTN_Clear = wxNewId()

richards_blue = wxColour(0,0,131)
richards_aqua = wxColour(0,194,197)
richards_dark_gray = wxColor(131,129,131)
richards_light_gray = wxColor(255,255,255)
richards_coloured_gray = wxColor(131,129,131)

_known_edit_area_types = [
	'allergy',
	'family history',
	'past history'
]

_prompt_defs = {
	'allergy': [
		_("Date"),
		_("Drug/Subst."),
		_("Generics"),
		_("Drug class"),
		_("Reaction"),
		_("Type")
	],
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
}


#====================================================================
#text control class to be later replaced by the gmPhraseWheel
#--------------------------------------------------------------------
class cEditAreaField(wxTextCtrl):
	def __init__ (self, parent, id, wxDefaultPostion, wxDefaultSize):
		wxTextCtrl.__init__(self,parent,id,"",wxDefaultPostion, wxDefaultSize,wxSIMPLE_BORDER)
		#self.SetBackgroundColour(wxColor(255, 194, 197))
		self.SetForegroundColour(wxColor(255, 0, 0))
		self.SetFont(wxFont(12, wxSWISS, wxNORMAL, wxBOLD, false, ''))
#====================================================================
#====================================================================
class gmEditArea( wxPanel):
	def __init__(self, parent, id, aType = None):
		# sanity checks
		if aType not in _known_edit_area_types:
			_log.Log(gmLog.lErr, 'unknown edit area type: [%s]' % aType)
			raise gmExceptions.ConstructorError, 'unknown edit area type: [%s]' % aType
		self._type = aType

		# init background panel
		wxPanel.__init__(
			self,
			parent,
			id,
			wxDefaultPosition,
			wxDefaultSize,
			style = wxNO_BORDER | wxTAB_TRAVERSAL
		)
		self.SetName(self._type)
#		self.SetBackgroundColour(wxColor(222,222,222))

		self.input_fields = {}

		szr_prompts = self.__make_prompts(_prompt_defs[self._type])
		self.szr_editing_area = self.__make_editing_area()
		# stack prompts and fields horizontally
		self.szr_main_panels = wxBoxSizer(wxHORIZONTAL)
		self.szr_main_panels.Add(szr_prompts, 11, wxEXPAND)
		self.szr_main_panels.Add(5, 0, 0, wxEXPAND)
		self.szr_main_panels.Add(self.szr_editing_area, 90, wxEXPAND)

		# use sizer for border around everything plus a little gap
		# FIXME: fold into szr_main_panels ?
		self.szr_central_container = wxBoxSizer(wxHORIZONTAL)
		self.szr_central_container.Add(self.szr_main_panels, 1, wxEXPAND | wxALL, 5)
		self.SetSizer(self.szr_central_container)
		self.szr_central_container.Fit(self)
		self.SetAutoLayout(true)

		self.__register_events()

		self.Show(true)
	#----------------------------------------------------------------
	def _make_prompt(self, parent, aLabel, aColor):
		# FIXME: style for centering in vertical direction ?
		prompt = wxStaticText(
			parent,
			-1,
			aLabel,
			wxDefaultPosition,
			wxDefaultSize,
			wxALIGN_RIGHT | wxST_NO_AUTORESIZE
		)
		prompt.SetFont(wxFont(10, wxSWISS, wxNORMAL, wxBOLD, false, ''))
		prompt.SetForegroundColour(aColor)
		return prompt
	#----------------------------------------------------------------
	def __make_prompts(self, prompt_labels):
		# prompts live on a panel
		prompt_pnl = wxPanel(self, -1, wxDefaultPosition, wxDefaultSize, wxSIMPLE_BORDER)
		prompt_pnl.SetBackgroundColour(richards_light_gray)
		# make them
		gszr = wxGridSizer (len(prompt_labels)+1, 1, 2, 2)
		color = richards_aqua
		for prompt in prompt_labels:
			label = self._make_prompt(prompt_pnl, "%s " % prompt, color)
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
	def _make_standard_buttons(self, parent):
		self.btn_Save = wxButton(parent, wxID_BTN_Save, _("Save"))
		self.btn_Clear = wxButton(parent, wxID_BTN_Clear, _("Clear"))

		# back pointers for panel type identification
		# FIXME: you mean, like, for finding out what type of edit area ?
		# why can't we use self._type for that ?
		self.btn_Save.owner = self
		self.btn_Clear.owner = self
		
		szr_buttons = wxBoxSizer(wxHORIZONTAL)
		szr_buttons.Add(self.btn_Save, 1, wxEXPAND | wxALL, 1)
		szr_buttons.Add(5, 0, 0)
		szr_buttons.Add(self.btn_Clear, 1, wxEXPAND | wxALL, 1)

		return szr_buttons
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
		EVT_BUTTON(self.btn_Save, wxID_BTN_Save, self._on_save_btn_pressed)
		EVT_BUTTON(self.btn_Clear, wxID_BTN_Clear, self._on_clear_btn_pressed)

		# client internal signals
		gmDispatcher.connect(signal = gmSignals.activating_patient(), receiver = self._save_data)
		gmDispatcher.connect(signal = gmSignals.application_closing(), receiver = self._save_data)

		return 1
	#--------------------------------------------------------
	# handlers
	#--------------------------------------------------------
	def _on_save_btn_pressed(self, event):
		print "SAVE button pressed"
		self._save_data()
		event.Skip()
	#--------------------------------------------------------
	def _save_data(self):
		_log.Log(gmLog.lErr, 'programmer forgot to define _save_data() for [%s]' % self._type)
		_log.Log(gmLog.lInfo, 'child classes of gmEditArea *must* override this function')
		raise AttributeError
	#--------------------------------------------------------
	def _on_clear_btn_pressed(self, event):
		print "CLEAR button pressed"
		self._init_fields()
		event.Skip()
	#--------------------------------------------------------
	def _init_fields(self):
		_log.Log(gmLog.lErr, 'programmer forgot to define _init_fields() for [%s]' % self._type)
		_log.Log(gmLog.lInfo, 'child classes of gmEditArea *must* override this function')
		raise AttributeError
#====================================================================
class gmAllergyEditArea(gmEditArea):
	def __init__(self, parent, id):
		try:
			gmEditArea.__init__(self, parent, id, aType = 'allergy')
		except gmExceptions.ConstructorError:
			_log.LogExceptions('cannot instantiate allergies edit area', sys.exc_info())
			raise
	#----------------------------------------------------------------
	def _make_edit_lines(self, parent):
		_log.Log(gmLog.lData, "making allergy lines")
		lines = []
		# line 1
		self.input_fields['date recorded'] = gmDateTimeInput.gmDateInput(
			parent = parent,
			id = -1,
			size = wxPyDefaultSize,
			pos = wxPyDefaultPosition,
			style = wxSIMPLE_BORDER
		)
		lines.append(self.input_fields['date recorded'])
		# line 2
		self.input_fields['substance'] = cEditAreaField(parent, -1, wxDefaultPosition, wxDefaultSize)
		lines.append(self.input_fields['substance'])
		# FIXME: add substance_code
		# line 3
		self.input_fields['generic'] = cEditAreaField(parent, -1, wxDefaultPosition, wxDefaultSize)
		self.cb_generic_specific = wxCheckBox(parent, -1, _("generics specific"), wxDefaultPosition, wxDefaultSize, wxNO_BORDER)
		szr = wxBoxSizer(wxHORIZONTAL)
		szr.Add(self.input_fields['generic'], 6, wxEXPAND)
		szr.Add(self.cb_generic_specific, 0, wxEXPAND)
		lines.append(szr)
		# line 4
		self.input_fields['allergy class'] = cEditAreaField(parent, -1, wxDefaultPosition, wxDefaultSize)
		lines.append(self.input_fields['allergy class'])
		# line 5
		self.input_fields['reaction'] = cEditAreaField(parent, -1, wxDefaultPosition, wxDefaultSize)
		lines.append(self.input_fields['reaction'])
		# FIXME: add allergene, atc_code
		# line 6
		self.RBtn_is_allergy = wxRadioButton(parent, -1, _("Allergy"), wxDefaultPosition,wxDefaultSize)
		self.RBtn_is_sensitivity = wxRadioButton(parent, -1, _("Sensitivity"), wxDefaultPosition,wxDefaultSize)
		self.cb_is_definite_allergy = wxCheckBox(parent, -1, _("Definite"), wxDefaultPosition,wxDefaultSize, wxNO_BORDER)

		self.input_fields['definite'] = self.cb_is_definite_allergy
		szr = wxBoxSizer(wxHORIZONTAL)
		szr.Add(5, 0, 0)
		szr.Add(self.RBtn_is_allergy, 2, wxEXPAND)
		szr.Add(self.RBtn_is_sensitivity, 2, wxEXPAND)
		szr.Add(self.cb_is_definite_allergy, 2, wxEXPAND)
		szr.Add(self._make_standard_buttons(parent), 0, wxEXPAND)
		lines.append(szr)

		return lines
	#--------------------------------------------------------
	def _save_data(self):
		print "saving allergy data"
		return 1
	#--------------------------------------------------------
	def _init_fields(self):
		print "initializing allergy input fields"
		return 1
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
		print "saving family history"
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



		self.rb_sideleft = wxRadioButton(parent, PHX_LEFT, _(" (L) "), wxDefaultPosition,wxDefaultSize)
		self.rb_sideright = wxRadioButton(parent,  PHX_RIGHT, _("(R)"), wxDefaultPosition,wxDefaultSize,wxSUNKEN_BORDER)
		self.rb_sideboth = wxRadioButton(parent,  PHX_BOTH, _("Both"), wxDefaultPosition,wxDefaultSize)
		rbsizer = wxBoxSizer(wxHORIZONTAL)
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
			"significant": self.cb_significant
		}

		return lines

	def _save_data(self):
		print "saving past history"
		return 1		

#====================================================================
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

		elif section == gmSECTION_VACCINATION:
			pass
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
		self.btn_Save = wxButton(self, -1, _("Ok"))
		self.btn_Clear = wxButton(self, -1, _("Clear"))
		szr_buttons = wxBoxSizer(wxHORIZONTAL)
		szr_buttons.Add(self.btn_Save, 1, wxEXPAND, wxALL, 1)
		szr_buttons.Add(5, 0, 0)
		szr_buttons.Add(self.btn_Clear, 1, wxEXPAND, wxALL, 1)
		return szr_buttons
	#----------------------------------------------------------------
	def __make_allergy_lines(self):
		lines = []
		self.input_fields = {}
		# line 1
		self.input_fields['date recorded'] = cEditAreaField(self, -1, wxDefaultPosition, wxDefaultSize)
		lines.append(self.input_fields['date recorded'])
		# line 2
		self.input_fields['substance'] = cEditAreaField(self, -1, wxDefaultPosition, wxDefaultSize)
		lines.append(self.input_fields['substance'])
		# FIXME: add substance_code
		# line 3
		self.input_fields['generic'] = cEditAreaField(self, -1, wxDefaultPosition, wxDefaultSize)
		self.cb_generic_specific = wxCheckBox(self, -1, _("generics specific"), wxDefaultPosition, wxDefaultSize, wxNO_BORDER)
		szr = wxBoxSizer(wxHORIZONTAL)
		szr.Add(self.input_fields['generic'], 6, wxEXPAND)
		szr.Add(self.cb_generic_specific, 0, wxEXPAND)
		lines.append(szr)
		# line 4
		self.input_fields['allergy class'] = cEditAreaField(self, -1, wxDefaultPosition, wxDefaultSize)
		lines.append(self.input_fields['allergy class'])
		# line 5
		self.input_fields['reaction'] = cEditAreaField(self, -1, wxDefaultPosition, wxDefaultSize)
		lines.append(self.input_fields['reaction'])
		# FIXME: add allergene, atc_code
		# line 6
		self.RBtn_is_allergy = wxRadioButton(self, -1, _("Allergy"), wxDefaultPosition,wxDefaultSize)
		self.RBtn_is_sensitivity = wxRadioButton(self, -1, _("Sensitivity"), wxDefaultPosition,wxDefaultSize)
		self.cb_is_definite_allergy = wxCheckBox(self, -1, _("Definate"), wxDefaultPosition,wxDefaultSize, wxNO_BORDER)
		szr = wxBoxSizer(wxHORIZONTAL)
		szr.Add(5, 0, 0)
		szr.Add(self.RBtn_is_allergy, 2, wxEXPAND)
		szr.Add(self.RBtn_is_sensitivity, 2, wxEXPAND)
		szr.Add(self.cb_is_definite_allergy, 2, wxEXPAND)
		szr.Add(self._make_standard_buttons(), 0, wxEXPAND)
		lines.append(szr)

		return lines
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


#		elif section == gmSECTION_VACCINATION:
#		      self.txt_targetdisease = cEditAreaField(self,-1,wxDefaultPosition,wxDefaultSize)
#		      self.txt_vaccine = cEditAreaField(self,-1,wxDefaultPosition,wxDefaultSize)
#		      self.txt_dategiven= cEditAreaField(self,-1,wxDefaultPosition,wxDefaultSize)
#		      self.txt_serialno = cEditAreaField(self,-1,wxDefaultPosition,wxDefaultSize)
#		      self.txt_sitegiven  = cEditAreaField(self,-1,wxDefaultPosition,wxDefaultSize)
#	              self.txt_progressnotes  = cEditAreaField(self,-1,wxDefaultPosition,wxDefaultSize)
#	              self.gszr.Add(self.txt_targetdisease,0,wxEXPAND)
#		      self.gszr.Add(self.txt_vaccine,0,wxEXPAND)
#		      self.gszr.Add(self.txt_dategiven,0,wxEXPAND)
#		      self.gszr.Add(self.txt_serialno,0,wxEXPAND)
#		      self.gszr.Add(self.txt_sitegiven,0,wxEXPAND)
#		      self.gszr.Add(self.txt_progressnotes,0,wxEXPAND)
#		      self.sizer_line6.Add(5,0,6)
#		      self.sizer_line6.Add(self.btn_Save,1,wxEXPAND|wxALL,2)
#	              self.sizer_line6.Add(self.btn_Clear,1,wxEXPAND|wxALL,2)    
#		      self.gszr.Add(self.sizer_line6,1,wxEXPAND)


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
#		      self.sizer_line8.Add(self.btn_Save,1,wxEXPAND|wxALL,2)
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
		      #self.sizer_line10.Add(self.btn_Save,1,wxEXPAND|wxALL,1)
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
#		      self.sizer_line8.Add(self.btn_Save,1,wxEXPAND|wxALL,2)
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
#		      self.sizer_line8.Add(self.btn_Save,1,wxEXPAND|wxALL,2)
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
#		      self.sizer_line8.Add(self.btn_Save,1,wxEXPAND|wxALL,2)
#	              self.sizer_line8.Add(self.btn_Clear,1,wxEXPAND|wxALL,2)    
#		      self.gszr.Add(self.sizer_line8,1,wxEXPAND)
#		else:
#		      pass

#====================================================================
# main
#--------------------------------------------------------------------
if __name__ == "__main__":
	app = wxPyWidgetTester(size = (400, 200))
	app.SetWidget(gmAllergyEditArea, -1)
	app.MainLoop()
#	app = wxPyWidgetTester(size = (400, 200))
#	app.SetWidget(gmFamilyHxEditArea, -1)
#	app.MainLoop()
#	app = wxPyWidgetTester(size = (400, 200))
#	app.SetWidget(gmPastHistoryEditArea, -1)
#	app.MainLoop()
#====================================================================
# $Log: gmEditArea.py,v $
# Revision 1.36  2003-10-22 21:33:12  hinnef
# added _save_data() to FxHistory and PastHistory to prevent crash on exit
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
