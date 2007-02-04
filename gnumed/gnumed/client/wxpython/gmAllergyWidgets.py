"""GnuMed allergy related widgets.

"""
############################################################################
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmAllergyWidgets.py,v $
__version__ = "$Revision: 1.18 $"
__author__  = "R.Terry <rterry@gnumed.net>, H.Herb <hherb@gnumed.net>, K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = 'GPL (details at http://www.gnu.org)'

import sys, time

try:
	import wxversion
	import wx
except ImportError:
	from wxPython import wx

from Gnumed.pycommon import gmLog, gmDispatcher, gmSignals, gmExceptions, gmI18N
from Gnumed.wxpython import gmEditArea, gmDateTimeInput, gmTerryGuiParts, gmRegetMixin
from Gnumed.business import gmPerson, gmAllergy

_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)

ID_ALLERGY_LIST = wx.NewId()

try:
	_('do-not-translate-but-make-epydoc-happy')
except NameError:
	_ = lambda x:x
#======================================================================
class gmAllergyEditArea(gmEditArea.cEditArea):

	def __init__(self, parent, id):
		gmEditArea.cEditArea.__init__(self, parent, id)
	#----------------------------------------------------
	def _define_fields(self, parent):
		# line 1
		self.fld_date_noted = gmDateTimeInput.gmDateInput(
			parent = parent,
			id = -1,
			style = wx.SIMPLE_BORDER
		)
		self._add_field(
			line = 1,
			pos = 1,
			widget = self.fld_date_noted,
			weight = 1
		)
		# line 2
		self.fld_substance = gmEditArea.cEditAreaField(parent)
		self._add_field(
			line = 2,
			pos = 1,
			widget = self.fld_substance,
			weight = 1
		)
		# line 3
		self.fld_generic = gmEditArea.cEditAreaField(parent)
		self._add_field(
			line = 3,
			pos = 1,
			widget = self.fld_generic,
			weight = 6
		)
		self.fld_generic_specific = wx.CheckBox(
			parent,
			-1,
			_("generics specific"),
			style = wx.NO_BORDER
		)
		self._add_field(
			line = 3,
			pos = 2,
			widget = self.fld_generic_specific,
			weight = 0
		)
		# line 4
		self.fld_atc_drug_class = gmEditArea.cEditAreaField(parent)
		self._add_field(
			line = 4,
			pos = 1,
			widget = self.fld_atc_drug_class,
			weight = 0
		)
		# line 5
		# FIXME: add allergene, atc_code ?
		self.fld_reaction = gmEditArea.cEditAreaField(parent)
		self._add_field(
			line = 5,
			pos = 1,
			widget = self.fld_reaction,
			weight = 1
		)
		# line 6
		self.fld_is_allergy = wx.RadioButton(parent, -1, _("Allergy"))
		self._add_field(
			line = 6,
			pos = 1,
			widget = self.fld_is_allergy,
			weight = 2
		)
		self.fld_is_sensitivity = wx.RadioButton(parent, -1, _("Sensitivity"))
		self._add_field(
			line = 6,
			pos = 2,
			widget = self.fld_is_sensitivity,
			weight = 2
		)
		self.fld_is_definite_allergy = wx.CheckBox (
			parent,
			-1,
			_("Definite"),
			style = wx.NO_BORDER
		)
		self._add_field(
			line = 6,
			pos = 3,
			widget = self.fld_is_definite_allergy,
			weight = 2
		)
		self._add_field(
			line = 6,
			pos = 4,
			widget = self._make_standard_buttons(parent),
			weight = 1
		)
	#----------------------------------------------------
	def _define_prompts(self):
		self._add_prompt(line = 1, label = _("Date Noted"))
		self._add_prompt(line = 2, label = _("Brand/Substance"))
		self._add_prompt(line = 3, label = _("Generics"))
		self._add_prompt(line = 4, label = _("ATC/Drug Class"))
		self._add_prompt(line = 5, label = _("Reaction"))
		self._add_prompt(line = 6, label = '')
	#----------------------------------------------------
	def _save_new_entry(self):
		emr = self._patient.get_emr()
		if emr is None:
			wx.Bell()
			_gb['main.statustext'](_('Cannot create allergy: %s') % data)
			return False
		# create new allergy entry
		if self.fld_is_allergy.GetValue():
			allgtype = 'allergy'
		else:
			allgtype = 'sensitivity'
		allg = emr.add_allergy (
			substance = self.fld_substance.GetValue(),
			allg_type = allgtype
		)
		if allg is None:
			wx.Bell()
			_gb['main.statustext'](_('Cannot create allergy: %s') % data)
			return False
		# and update it with known data
		allg['date'] = self.fld_date_noted.GetValue()
		allg['substance'] = self.fld_substance.GetValue()
		allg['generics'] = self.fld_generic.GetValue()
		allg['atc_code'] = self.fld_atc_drug_class.GetValue()
		allg['generic_specific'] = (True and self.fld_generic_specific.GetValue())
		allg['definite'] = (True and self.fld_is_definite_allergy.GetValue())
		allg['reaction'] = self.fld_reaction.GetValue()
		successfull, err = allg.save_payload()
		if not successfull:
			wx.Bell()
			_gb['main.statustext'](_('Cannot update allergy: %s') % err)
			return False
		_gb['main.statustext'](_('Allergy saved.'))
		self.data = allg
		return True
	#----------------------------------------------------
	def set_data(self, allergy = None):
		"""Set edit area fields with allergy object data.

		- set defaults if no object is passed in, this will
		  result in a new object being created upon saving
		"""
		if allergy is None:
			self.data = None
			self.fld_date_noted.SetText((value=time.strftime('%Y-%m-%d', data=time.localtime())))
			self.fld_substance.SetValue('')
			self.fld_generic.SetValue('')
			self.fld_generic_specific.SetValue(0)
			self.fld_atc_drug_class.SetValue('')
			self.fld_reaction.SetValue('')
			self.fld_is_allergy.SetValue(1)
			self.fld_is_sensitivity.SetValue(0)
			self.fld_is_definite_allergy.SetValue(1)
			return True

		if isinstance(allergy, gmAllergy.cAllergy):
			self.data = allergy
			self.fld_date_noted.SetValue(allergy['date'].strftime('%Y-%m-%d'))
			self.fld_substance.SetValue(allergy['substance'])

			if allergy['generics'] is not None:
				self.fld_generic.SetValue(allergy['generics'])
			else:
				self.fld_generic.SetValue('')

			if allergy['generic_specific']:
				self.fld_generic_specific.SetValue(1)
			else:
				self.fld_generic_specific.SetValue(0)

			if allergy['atc_code'] is not None:
				self.fld_atc_drug_class.SetValue(allergy['atc_code'])
			else:
				self.fld_atc_drug_class.SetValue('')

			if allergy['reaction'] is not None:
				self.fld_reaction.SetValue(allergy['reaction'])
			else:
				self.fld_reaction.SetValue('')

			if allergy['type'] == 'allergy':
				self.fld_is_allergy.SetValue(1)
#				self.fld_is_sensitivity.SetValue(0)
			else:
				self.fld_is_allergy.SetValue(0)
#				self.fld_is_sensitivity.SetValue(1)

			if allergy['definite']:
				self.fld_is_definite_allergy.SetValue(1)
			else:
				self.fld_is_definite_allergy.SetValue(0)
			return True

		_log.Log(gmLog.lErr, 'cannot handle [%s:%s]' % (type(allergy), str(allergy)))
		return False
#========================================================
class cAllergyPanel(wx.Panel, gmRegetMixin.cRegetOnPaintMixin):
	"""Allergy details panel.

		This panel will hold all the allergy details and
		allow entry of those details via the editing area.
	"""
	#----------------------------------------------------
	def __init__(self, parent, id=-1):
		wx.Panel.__init__(self, parent, id, wx.DefaultPosition, wx.DefaultSize, wx.RAISED_BORDER)
		gmRegetMixin.cRegetOnPaintMixin.__init__(self)
		self.__do_layout()
		self.__pat = gmPerson.gmCurrentPatient()
		self.__register_interests()
		self.__reset_ui_content()
	#----------------------------------------------------
	def __do_layout(self):
		# -- top part --
		pnl_UpperCaption = gmTerryGuiParts.cHeadingCaption(self, -1, _("ALLERGIES"))
		self.editarea = gmAllergyEditArea(self, -1)

		# -- middle part --
		# divider headings below edit area
		pnl_MiddleCaption = gmTerryGuiParts.cDividerCaption(self, -1, _("Allergy and Sensitivity - Summary"))
#		self.sizer_divider_drug_generic = wx.BoxSizer(wxHORIZONTAL)
#		self.sizer_divider_drug_generic.Add(pnl_MiddleCaption, 1, wxEXPAND)
		self.LCTRL_allergies = wx.ListCtrl (
			parent = self,
			id = ID_ALLERGY_LIST,
			pos = wx.DefaultPosition,
			size = wx.DefaultSize,
			style = wx.LC_SINGLE_SEL | wx.LC_REPORT | wx.SUNKEN_BORDER | wx.LC_HRULES | wx.LC_VRULES | wx.VSCROLL
		)
		self.LCTRL_allergies.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.NORMAL, False, ''))
		self.LCTRL_allergies.InsertColumn(0, _("Type"))
		self.LCTRL_allergies.InsertColumn(1, _("Status"))
		self.LCTRL_allergies.InsertColumn(2, _("ATC/Class"))
		self.LCTRL_allergies.InsertColumn(3, _("Substance"))
		self.LCTRL_allergies.InsertColumn(4, _("Generics"))
		self.LCTRL_allergies.InsertColumn(5, _("Reaction"))

		# -- bottom part --
		pnl_LowerCaption = gmTerryGuiParts.cDividerCaption(self, -1, _('Class notes'))
		#add a richtext control or a wxTextCtrl multiline to display the class text information
		#e.g. would contain say information re the penicillins
		self.class_notes = wx.TextCtrl (
			self,
			-1,
			"A member of a new class of nonsteroidal anti-inflammatory agents (COX-2 selective NSAIDs) which have a mechanism of action that inhibits prostaglandin synthesis primarily by inhibition of cyclooxygenase 2 (COX-2). At therapeutic doses these have no effect on prostanoids synthesised by activation of COX-1 thereby not interfering with normal COX-1 related physiological processes in tissues, particularly the stomach, intestine and platelets.",
			size = (200, 100),
			style = wx.TE_MULTILINE | wx.TE_READONLY
		)
		self.class_notes.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.NORMAL, False, ''))

		# -- add elements to main background sizer --
		self.mainsizer = wx.BoxSizer(wx.VERTICAL)
		self.mainsizer.Add(pnl_UpperCaption, 0, wx.EXPAND)
		self.mainsizer.Add(self.editarea, 6, wx.EXPAND)
#		self.mainsizer.Add(self.sizer_divider_drug_generic,0,wxEXPAND)
		self.mainsizer.Add(pnl_MiddleCaption, 0, wx.EXPAND)
		self.mainsizer.Add(self.LCTRL_allergies, 5, wx.EXPAND)
		self.mainsizer.Add(pnl_LowerCaption, 0, wx.EXPAND)
		self.mainsizer.Add(self.class_notes, 4, wx.EXPAND)

		self.SetAutoLayout(True)
		self.SetSizer(self.mainsizer)
		self.mainsizer.Fit(self)
	#-----------------------------------------------
	def __register_interests(self):
		wx.EVT_LIST_ITEM_ACTIVATED(self, ID_ALLERGY_LIST, self._on_allergy_activated)

		# client internal signals
		gmDispatcher.connect(signal=gmSignals.post_patient_selection(), receiver=self._schedule_data_reget)
		gmDispatcher.connect(signal=gmSignals.vaccinations_updated(), receiver=self._schedule_data_reget)
	#-----------------------------------------------
	def __reset_ui_content(self):
		self.editarea.set_data()
		self.LCTRL_allergies.DeleteAllItems()
	#-----------------------------------------------
	def _populate_with_data(self):
		if not self.__pat.is_connected():
			return False

		self.LCTRL_allergies.DeleteAllItems()

		emr = self.__pat.get_emr()
		allergies = emr.get_allergies()
		if allergies is None:
			return False
		for list_line in range(len(allergies)):
			allg = allergies[list_line]
			list_line = self.LCTRL_allergies.InsertStringItem(list_line, allg['l10n_type'])
			# FIXME: check with Richard design specs
			if allg['definite']:
				self.LCTRL_allergies.SetStringItem(list_line, 1, _('definite'))
			else:
				self.LCTRL_allergies.SetStringItem(list_line, 1, _('likely'))
			if allg['atc_code'] is not None:
				self.LCTRL_allergies.SetStringItem(list_line, 2, allg['atc_code'])
			self.LCTRL_allergies.SetStringItem(list_line, 3, allg['substance'])
			if allg['generics'] is not None:
				self.LCTRL_allergies.SetStringItem(list_line, 4, allg['generics'])
			self.LCTRL_allergies.SetStringItem(list_line, 5, allg['reaction'])
			self.LCTRL_allergies.SetItemData(list_line, allg['pk_allergy'])
		for col in range(5):
			self.LCTRL_allergies.SetColumnWidth(col, wx.LIST_AUTOSIZE)
		# FIXME: resize event needed ?
		return True
	#-----------------------------------------------
	def _on_allergy_activated(self, evt):
		pk_allg = evt.GetData()
		emr = self.__pat.get_emr()
		allgs = emr.get_allergies(ID_list=[pk_allg])
		self.editarea.set_data(allergy = allgs[0])
#======================================================================
# main
#----------------------------------------------------------------------
if __name__ == "__main__":
	app = wxPyWidgetTester(size = (600, 600))
	app.SetWidget(cAllergyPanel, -1)
	app.MainLoop()
#======================================================================
# $Log: gmAllergyWidgets.py,v $
# Revision 1.18  2007-02-04 15:49:31  ncq
# - use SetText() on phrasewheel
#
# Revision 1.17  2006/10/25 07:46:44  ncq
# - Format() -> strftime() since datetime.datetime does not have .Format()
#
# Revision 1.16  2006/10/24 13:20:57  ncq
# - do not import gmPG
#
# Revision 1.15  2006/05/15 13:35:59  ncq
# - signal cleanup:
#   - activating_patient -> pre_patient_selection
#   - patient_selected -> post_patient_selection
#
# Revision 1.14  2006/05/04 09:49:20  ncq
# - get_clinical_record() -> get_emr()
# - adjust to changes in set_active_patient()
# - need explicit set_active_patient() after ask_for_patient() if wanted
#
# Revision 1.13  2006/01/03 12:12:03  ncq
# - make epydoc happy re _()
#
# Revision 1.12  2005/12/27 18:46:39  ncq
# - use gmI18N
#
# Revision 1.11  2005/09/28 21:27:30  ncq
# - a lot of wx2.6-ification
#
# Revision 1.10  2005/09/28 15:57:47  ncq
# - a whole bunch of wx.Foo -> wx.Foo
#
# Revision 1.9  2005/09/26 18:01:50  ncq
# - use proper way to import wx26 vs wx2.4
# - note: THIS WILL BREAK RUNNING THE CLIENT IN SOME PLACES
# - time for fixup
#
# Revision 1.8  2005/09/24 09:17:27  ncq
# - some wx2.6 compatibility fixes
#
# Revision 1.7  2005/03/20 17:49:11  ncq
# - default for id
#
# Revision 1.6  2005/01/31 10:37:26  ncq
# - gmPatient.py -> gmPerson.py
#
# Revision 1.5  2004/12/15 21:55:00  ncq
# - adapt to cleanly separated old/new style edit area
#
# Revision 1.4  2004/10/27 12:17:22  ncq
# - robustify should there not be an active patient
#
# Revision 1.3  2004/10/11 20:14:16  ncq
# - use RegetOnPaintMixin
# - attach to backend
# - cleanup, remove cruft
#
# Revision 1.2  2004/07/18 20:30:53  ncq
# - wxPython.true/false -> Python.True/False as Python tells us to do
#
# Revision 1.1  2004/07/17 21:16:38  ncq
# - cleanup/refactor allergy widgets:
#   - Horst space plugin added
#   - Richard space plugin separated out
#   - plugin independant GUI code aggregated
#   - allergies edit area factor out from generic edit area file
#
#
