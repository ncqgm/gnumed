#====================================================================
# GnuMed
# GPL
#====================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmEditArea.py,v $
# $Id: gmEditArea.py,v 1.18 2003-05-21 14:11:26 ncq Exp $
__version__ = "$Revision: 1.18 $"
__author__ = "R.Terry, K.HIlbert"
#====================================================================
import sys

if __name__ == "__main__":
	sys.path.append ("../python-common/")

import gmLog
_log = gmLog.gmDefLog

if __name__ == "__main__":
	import gmI18N

import gmExceptions

from wxPython.wx import *

ID_PROGRESSNOTES = wxNewId()
gmSECTION_SUMMARY = 1
gmSECTION_DEMOGRAPHICS = 2
gmSECTION_CLINICALNOTES = 3
gmSECTION_FAMILYHISTORY = 4
gmSECTION_PASTHISTORY = 5
gmSECTION_VACCINATION = 6
gmSECTION_ALLERGIES = 7
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

richards_blue = wxColour(0,0,131)
richards_aqua = wxColour(0,194,197)
richards_dark_gray = wxColor(131,129,131)
richards_light_gray = wxColor(255,255,255)
richards_coloured_gray = wxColor(131,129,131)

_known_edit_area_types = [
	'allergy',
	'family history'
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
	]
}

familyhistoryprompts = {

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
class gmEditArea(wxPanel):
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
#		self.SetBackgroundColour(wxColor(222,222,222))

		# make prompts
		szr_prompts = self.__make_prompts(_prompt_defs[self._type])

		# make editing area
		szr_editing_area = self.__make_editing_area()

		# stack prompts and fields horizontally
		self.szr_main_panels = wxBoxSizer(wxHORIZONTAL)
		self.szr_main_panels.Add(szr_prompts, 11, wxEXPAND)
		self.szr_main_panels.Add(5, 0, 0, wxEXPAND)
		self.szr_main_panels.Add(szr_editing_area, 90, wxEXPAND)

		# use sizer for border around everything plus a little gap
		# FIXME: fold into szr_main_panels ?
		self.szr_central_container = wxBoxSizer(wxHORIZONTAL)
		self.szr_central_container.Add(self.szr_main_panels, 1, wxEXPAND | wxALL, 5)
		self.SetSizer(self.szr_central_container)
		self.szr_central_container.Fit(self)
		self.SetAutoLayout(true)
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
		self.btn_OK = wxButton(parent, -1, _("Ok"))
		self.btn_Clear = wxButton(parent, -1, _("Clear"))
		szr_buttons = wxBoxSizer(wxHORIZONTAL)
		szr_buttons.Add(self.btn_OK, 1, wxEXPAND | wxALL, 1)
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
		self.TBOX_list = {}
		# line 1
		self.TBOX_list['date recorded'] = cEditAreaField(parent, -1, wxDefaultPosition, wxDefaultSize)
		lines.append(self.TBOX_list['date recorded'])
		# line 2
		self.TBOX_list['substance'] = cEditAreaField(parent, -1, wxDefaultPosition, wxDefaultSize)
		lines.append(self.TBOX_list['substance'])
		# FIXME: add substance_code
		# line 3
		self.TBOX_list['generic'] = cEditAreaField(parent, -1, wxDefaultPosition, wxDefaultSize)
		self.ChBOX_generic_specific = wxCheckBox(parent, -1, _("generics specific"), wxDefaultPosition, wxDefaultSize, wxNO_BORDER)
		szr = wxBoxSizer(wxHORIZONTAL)
		szr.Add(self.TBOX_list['generic'], 6, wxEXPAND)
		szr.Add(self.ChBOX_generic_specific, 0, wxEXPAND)
		lines.append(szr)
		# line 4
		self.TBOX_list['allergy class'] = cEditAreaField(parent, -1, wxDefaultPosition, wxDefaultSize)
		lines.append(self.TBOX_list['allergy class'])
		# line 5
		self.TBOX_list['reaction'] = cEditAreaField(parent, -1, wxDefaultPosition, wxDefaultSize)
		lines.append(self.TBOX_list['reaction'])
		# FIXME: add allergene, atc_code
		# line 6
		self.RBtn_is_allergy = wxRadioButton(parent, -1, _("Allergy"), wxDefaultPosition,wxDefaultSize)
		self.RBtn_is_sensitivity = wxRadioButton(parent, -1, _("Sensitivity"), wxDefaultPosition,wxDefaultSize)
		self.ChBOX_is_definite_allergy = wxCheckBox(parent, -1, _("Definate"), wxDefaultPosition,wxDefaultSize, wxNO_BORDER)
		szr = wxBoxSizer(wxHORIZONTAL)
		szr.Add(5, 0, 0)
		szr.Add(self.RBtn_is_allergy, 2, wxEXPAND)
		szr.Add(self.RBtn_is_sensitivity, 2, wxEXPAND)
		szr.Add(self.ChBOX_is_definite_allergy, 2, wxEXPAND)
		szr.Add(self._make_standard_buttons(parent), 0, wxEXPAND)
		lines.append(szr)

		return lines
#====================================================================
class gmFamilyHxEditArea(gmEditArea):
	def __init__(self, parent, id):
		try:
			gmEditArea.__init__(self, parent, id, aType = 'family history')
		except gmExceptions.ConstructorError:
			_log.LogExceptions('cannot instantiate family Hx edit area', sys.exc_info())
			raise
	#----------------------------------------------------------------
	def _make_edit_lines(self, parent):
		_log.Log(gmLog.lData, "making family Hx lines")
		lines = []
		self.TBOX_list = {}
		# line 1
		# FIXME: put patient search widget here, too ...
		# add button "make active patient"
		self.TBOX_list['name'] = cEditAreaField(parent, -1, wxDefaultPosition, wxDefaultSize)
		self.TBOX_list['DOB'] = cEditAreaField(parent, -1, wxDefaultPosition, wxDefaultSize)
		lbl_dob = self._make_prompt(parent, _(" Date of Birth "), richards_blue)
		szr = wxBoxSizer(wxHORIZONTAL)
		szr.Add(self.TBOX_list['name'], 4, wxEXPAND)
		szr.Add(lbl_dob, 2, wxEXPAND)
		szr.Add(self.TBOX_list['DOB'], 4, wxEXPAND)
		lines.append(szr)
		# line 2
		# FIXME: keep relationship attachments permamently ! (may need to make new patient ...)
		# FIXME: learning phrasewheel attached to list loaded from backend
		self.TBOX_list['relationship'] = cEditAreaField(parent, -1, wxDefaultPosition, wxDefaultSize)
		szr = wxBoxSizer(wxHORIZONTAL)
		szr.Add(self.TBOX_list['relationship'], 4, wxEXPAND)
		lines.append(szr)
		# line 3
		self.TBOX_list['condition'] = cEditAreaField(parent, -1, wxDefaultPosition, wxDefaultSize)
		self.ChBOX_condition_confidential = wxCheckBox(parent, -1, _("confidental"), wxDefaultPosition, wxDefaultSize, wxNO_BORDER)
		szr = wxBoxSizer(wxHORIZONTAL)
		szr.Add(self.TBOX_list['condition'], 6, wxEXPAND)
		szr.Add(self.ChBOX_condition_confidential, 0, wxEXPAND)
		lines.append(szr)
		# line 4
		self.TBOX_list['comment'] = cEditAreaField(parent, -1, wxDefaultPosition, wxDefaultSize)
		lines.append(self.TBOX_list['comment'])
		# line 5
		lbl_onset = self._make_prompt(parent, _(" age onset "), richards_blue)
		self.TBOX_list['age onset'] = cEditAreaField(parent, -1, wxDefaultPosition, wxDefaultSize)
		#    FIXME: combo box ...
		lbl_caused_death = self._make_prompt(parent, _(" caused death "), richards_blue)
		self.TBOX_list['caused death'] = cEditAreaField(parent, -1, wxDefaultPosition, wxDefaultSize)
		lbl_aod = self._make_prompt(parent, _(" age died "), richards_blue)
		self.TBOX_list['AOD'] = cEditAreaField(parent, -1, wxDefaultPosition, wxDefaultSize)
		szr = wxBoxSizer(wxHORIZONTAL)
		szr.Add(lbl_onset, 0, wxEXPAND)
		szr.Add(self.TBOX_list['age onset'], 1,wxEXPAND)
		szr.Add(lbl_caused_death, 0, wxEXPAND)
		szr.Add(self.TBOX_list['caused death'], 2,wxEXPAND)
		szr.Add(lbl_aod, 0, wxEXPAND)
		szr.Add(self.TBOX_list['AOD'], 1, wxEXPAND)
		szr.Add(2, 2, 8)
		lines.append(szr)
		# line 6
		self.TBOX_list['progress notes'] = cEditAreaField(parent, -1, wxDefaultPosition, wxDefaultSize)
		lines.append(self.TBOX_list['progress notes'])
		# line 8
		self.Btn_next_condition = wxButton(parent, -1, _("Next Condition"))
		szr = wxBoxSizer(wxHORIZONTAL)
		szr.AddSpacer(10, 0, 0)
		szr.Add(self.Btn_next_condition, 0, wxEXPAND | wxALL, 1)
		szr.Add(2, 1, 5)
		szr.Add(self._make_standard_buttons(parent), 0, wxEXPAND)
		lines.append(szr)

		return lines
#====================================================================
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
		elif section == gmSECTION_ALLERGIES:
			lines = self.__make_allergy_lines()
			for line in lines:
				self.gszr.Add(line, 0, wxEXPAND | wxALIGN_RIGHT)
		else:
			pass

		self.SetSizer(self.gszr)
		self.gszr.Fit(self)

		self.SetAutoLayout(true)
		self.Show(true)
	#----------------------------------------------------------------
	def _make_standard_buttons():
		self.btn_OK = wxButton(self, -1, _("Ok"))
		self.btn_Clear = wxButton(self, -1, _("Clear"))
		szr_buttons = wxBoxSizer(wxHORIZONTAL)
		szr_buttons.Add(self.btn_OK, 1, wxEXPAND, wxALL, 1)
		szr_buttons.Add(5, 0, 0)
		szr_buttons.Add(self.btn_Clear, 1, wxEXPAND, wxALL, 1)
		return szr_buttons
	#----------------------------------------------------------------
	def __make_allergy_lines():
		lines = []
		self.TBOX_list = {}
		# line 1
		self.TBOX_list['date recorded'] = cEditAreaField(self, -1, wxDefaultPosition, wxDefaultSize)
		lines.append(self.TBOX_list['date recorded'])
		# line 2
		self.TBOX_list['substance'] = cEditAreaField(self, -1, wxDefaultPosition, wxDefaultSize)
		lines.append(self.TBOX_list['substance'])
		# FIXME: add substance_code
		# line 3
		self.TBOX_list['generic'] = cEditAreaField(self, -1, wxDefaultPosition, wxDefaultSize)
		self.ChBOX_generic_specific = wxCheckBox(self, -1, _("generics specific"), wxDefaultPosition, wxDefaultSize, wxNO_BORDER)
		szr = wxBoxSizer(wxHORIZONTAL)
		szr.Add(self.TBOX_list['generic'], 6, wxEXPAND)
		szr.Add(self.ChBOX_generic_specific, 0, wxEXPAND)
		lines.append(szr)
		# line 4
		self.TBOX_list['allergy class'] = cEditAreaField(self, -1, wxDefaultPosition, wxDefaultSize)
		lines.append(self.TBOX_list['allergy class'])
		# line 5
		self.TBOX_list['reaction'] = cEditAreaField(self, -1, wxDefaultPosition, wxDefaultSize)
		lines.append(self.TBOX_list['reaction'])
		# FIXME: add allergene, atc_code
		# line 6
		self.RBtn_is_allergy = wxRadioButton(self, -1, _("Allergy"), wxDefaultPosition,wxDefaultSize)
		self.RBtn_is_sensitivity = wxRadioButton(self, -1, _("Sensitivity"), wxDefaultPosition,wxDefaultSize)
		self.ChBOX_is_definite_allergy = wxCheckBox(self, -1, _("Definate"), wxDefaultPosition,wxDefaultSize, wxNO_BORDER)
		szr = wxBoxSizer(wxHORIZONTAL)
		szr.Add(5, 0, 0)
		szr.Add(self.RBtn_is_allergy, 2, wxEXPAND)
		szr.Add(self.RBtn_is_sensitivity, 2, wxEXPAND)
		szr.Add(self.ChBOX_is_definite_allergy, 2, wxEXPAND)
		szr.Add(self._make_standard_buttons(), 0, wxEXPAND)
		lines.append(szr)

		return lines
#====================================================================
class EditArea(wxPanel):
	def __init__(self, parent, id, line_labels, section):
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
# main
#--------------------------------------------------------------------
if __name__ == "__main__":
	app = wxPyWidgetTester(size = (400, 200))
	app.SetWidget(gmAllergyEditArea, -1)
	app.MainLoop()
	app = wxPyWidgetTester(size = (400, 200))
	app.SetWidget(gmFamilyHxEditArea, -1)
	app.MainLoop()
#====================================================================

# $Log: gmEditArea.py,v $
# Revision 1.18  2003-05-21 14:11:26  ncq
# - much needed rewrite/cleanup of gmEditArea
# - allergies/family history edit area adapted to new gmEditArea code
# - old code still there for non-converted edit areas
#
# Revision 1.17  2003/02/14 01:24:54  ncq
# - cvs metadata keywords
#
