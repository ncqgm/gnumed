"""GnuMed immunisation/vaccination widgets.

Modelled after Richard Terry's design document.

copyright: authors
"""
#======================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmVaccWidgets.py,v $
# $Id: gmVaccWidgets.py,v 1.7 2004-09-13 19:19:41 ncq Exp $
__version__ = "$Revision: 1.7 $"
__author__ = "R.Terry, S.J.Tan, K.Hilbert"
__license__ = "GPL (details at http://www.gnu.org)"

import sys, time

from wxPython.wx import *
import mx.DateTime as mxDT

from Gnumed.wxpython import gmEditArea, gmPhraseWheel, gmTerryGuiParts, gmRegetMixin
from Gnumed.business import gmPatient
from Gnumed.pycommon import gmLog, gmDispatcher, gmSignals, gmExceptions, gmMatchProvider

_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)

ID_VaccinatedIndicationsList = wxNewId()
ID_VaccinationsPerRegimeList = wxNewId()
ID_MissingShots = wxNewId()

#======================================================================
class cVaccinationEditArea(gmEditArea.gmEditArea):
	"""
	- warn on apparent duplicates
	- ask if "missing" (= previous, non-recorded) vaccinations
	  should be estimated and saved (add note "auto-generated")
	"""
	def __init__(self, parent, id):
		try:
			gmEditArea.gmEditArea.__init__(self, parent, id, aType = 'vaccination')
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
#				v_vacc_defs4reg
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
		gmEditArea._decorate_editarea_field(self.fld_vaccine)
		self._add_field(
			line = 1,
			pos = 1,
			widget = self.fld_vaccine,
			weight = 3
		)

		# FIXME: gmDateTimeInput
		self.fld_date_given = gmEditArea.cEditAreaField(parent)
		self._add_field(
			line = 2,
			pos = 1,
			widget = self.fld_date_given,
			weight = 2
		)

		# Batch No (http://www.fao.org/docrep/003/v9952E12.htm)
		self.fld_batch_no = gmEditArea.cEditAreaField(parent)
		self._add_field(
			line = 3,
			pos = 1,
			widget = self.fld_batch_no,
			weight = 1
		)

		# site given
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
		gmEditArea._decorate_editarea_field(self.fld_site_given)
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
		gmEditArea._decorate_editarea_field(self.fld_progress_note)
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
		# FIXME: validation ?
		emr = self.patient.get_clinical_record()
		if emr is None:
			# FIXME: badder error message
			wxBell()
			_gb['main.statustext'](_('Cannot save vaccination: %s') % data)
			return None
		# create new vaccination
		status, data = emr.add_vaccination(self.fld_vaccine.GetValue())
		if status is None:
			wxBell()
			_gb['main.statustext'](_('Cannot save vaccination: %s') % data)
			return None
		# update it with known data
		data['pk_provider'] = _whoami.get_staff_ID()
		data['date'] = self.fld_date_given.GetValue()
		data['narrative'] = self.fld_progress_note.GetValue()
		data['site'] = self.fld_site_given.GetValue()
		data['batch_no'] = self.fld_batch_no.GetValue()
		status, err = data.save_payload()
		if status is None:
			wxBell()
			_gb['main.statustext'](_('Cannot save vaccination: %s') % err)
			return None
		_gb['main.statustext'](_('Vaccination saved.'))
		self.data = data
		return 1
	#----------------------------------------------------
	def _save_modified_entry(self):
		"""Update vaccination object and persist to backend.
		"""
		self.data['vaccine'] = self.fld_vaccine.GetValue()
		self.data['batch_no'] = self.fld_batch_no.GetValue()
		self.data['date'] = self.fld_date_given.GetValue()
		self.data['site'] = self.fld_site_given.GetValue()
		self.data['narrative'] = self.fld_progress_note.GetValue()
		status, data = self.data.save_payload()
		if status is None:
			wxBell()
			_gb['main.statustext'](_('Cannot update vaccination: %s') % data)
			return False
		_gb['main.statustext'](_('Vaccination updated.'))
		return True
	#----------------------------------------------------
	def set_data(self, aVacc = None):
		"""Set edit area fields with vaccination object data.

		- set defaults if no object is passed in, this will
		  result in a new object being created upon saving
		"""
		self.data = None
		if aVacc is None:
			self.fld_vaccine.SetValue('')
			self.fld_batch_no.SetValue('')
			self.fld_date_given.SetValue((time.strftime('%Y-%m-%d', time.localtime())))
			self.fld_site_given.SetValue(_('left/right deltoid'))
			self.fld_progress_note.SetValue('')
			return 1
		self.data = aVacc
		self.fld_vaccine.SetValue(aVacc['vaccine'])
		self.fld_batch_no.SetValue(aVacc['batch_no'])
		self.fld_date_given.SetValue(aVacc['date'])
		self.fld_site_given.SetValue(aVacc['site'])
		self.fld_progress_note.SetValue(aVacc['narrative'])
		return 1
#======================================================================
class cImmunisationsPanel(wxPanel, gmRegetMixin.cRegetOnPaintMixin):

	def __init__(self, parent,id):
		wxPanel.__init__(self, parent, id, wxPyDefaultPosition, wxPyDefaultSize, wxRAISED_BORDER)
		gmRegetMixin.cRegetOnPaintMixin.__init__(self)

		self.__pat = gmPatient.gmCurrentPatient()

		#-----------------------------------------------
		# top part
		#-----------------------------------------------
		pnl_UpperCaption = gmTerryGuiParts.cHeadingCaption(self, -1, _("  IMMUNISATIONS  "))
		self.editarea = cVaccinationEditArea(self, -1)

		#-----------------------------------------------
		# middle part
		#-----------------------------------------------
		# divider headings below editing area
		indications_heading = gmTerryGuiParts.cDividerCaption(self, -1, _("Indications"))
		vaccinations_heading = gmTerryGuiParts.cDividerCaption(self, -1, _("Vaccinations"))
		szr_MiddleCap = wxBoxSizer(wxHORIZONTAL)
		szr_MiddleCap.Add(indications_heading, 1, wxEXPAND)
		szr_MiddleCap.Add(vaccinations_heading, 1, wxEXPAND)

		# left list: indications for which vaccinations have been given
		self.LBOX_vaccinated_indications = wxListBox(
			parent = self,
			id = ID_VaccinatedIndicationsList,
			choices = [],
			style = wxLB_HSCROLL | wxLB_NEEDED_SB | wxSUNKEN_BORDER
		)
		self.LBOX_vaccinated_indications.SetFont(wxFont(12,wxSWISS, wxNORMAL, wxNORMAL, False, ''))

		# right list: when an indication has been selected on the left
		# display the corresponding vaccinations on the right
		self.LBOX_given_shots = wxListBox(
			parent = self,
			id = ID_VaccinationsPerRegimeList,
			choices = [],
			style = wxLB_HSCROLL | wxLB_NEEDED_SB | wxSUNKEN_BORDER
		)
		self.LBOX_given_shots.SetFont(wxFont(12,wxSWISS, wxNORMAL, wxNORMAL, False, ''))

		szr_MiddleLists = wxBoxSizer(wxHORIZONTAL)
		szr_MiddleLists.Add(self.LBOX_vaccinated_indications, 4,wxEXPAND)
		szr_MiddleLists.Add(self.LBOX_given_shots, 6, wxEXPAND)

		#---------------------------------------------
		# bottom part
		#---------------------------------------------
		pnl_MiddleCaption3 = gmTerryGuiParts.cDividerCaption(self, -1, _("Missing Immunisations"))
		self.LBOX_missing_shots = wxListBox(
			parent = self,
			id = ID_MissingShots,
			size=(200, 100),
			choices= [],
			style = wxLB_HSCROLL | wxLB_NEEDED_SB | wxSUNKEN_BORDER
		)
		self.LBOX_missing_shots.SetFont(wxFont(12,wxSWISS,wxNORMAL,wxNORMAL,False,''))
		# alert caption
		pnl_BottomCaption = gmTerryGuiParts.cAlertCaption(self, -1, _('  Alerts  '))

		#---------------------------------------------
		# add all elements to the main background sizer
		#---------------------------------------------
		self.mainsizer = wxBoxSizer(wxVERTICAL)
		self.mainsizer.Add(pnl_UpperCaption, 0, wxEXPAND)
		self.mainsizer.Add(self.editarea, 6, wxEXPAND)
		self.mainsizer.Add(szr_MiddleCap, 0, wxEXPAND)
		self.mainsizer.Add(szr_MiddleLists, 4, wxEXPAND)
		self.mainsizer.Add(pnl_MiddleCaption3, 0, wxEXPAND)
		self.mainsizer.Add(self.LBOX_missing_shots, 4, wxEXPAND)
		self.mainsizer.Add(pnl_BottomCaption, 0, wxEXPAND)

		self.SetSizer(self.mainsizer)
		self.mainsizer.Fit(self)
		self.SetAutoLayout(True)

		self.__register_interests()

		self.__reset_ui_content()
	#----------------------------------------------------
	def __register_interests(self):
		# wxPython events
		EVT_SIZE(self, self.OnSize)
		EVT_LISTBOX(self, ID_VaccinatedIndicationsList, self.on_vaccinated_indication_selected)
		EVT_LISTBOX_DCLICK(self, ID_VaccinationsPerRegimeList, self.on_given_shot_selected)
		EVT_LISTBOX_DCLICK(self, ID_MissingShots, self.on_missing_shot_selected)
#		EVT_RIGHT_UP(self.lb1, self.EvtRightButton)

		# client internal signals
#		gmDispatcher.connect(signal=gmSignals.patient_selected(), receiver=self._on_patient_selected)
		# behaves just like patient_selected, really
#		gmDispatcher.connect(signal=gmSignals.vaccinations_updated(), receiver=self._on_vaccinations_updated)
		# test
		gmDispatcher.connect(signal=gmSignals.patient_selected(), receiver=self._schedule_data_reget)
		gmDispatcher.connect(signal=gmSignals.vaccinations_updated(), receiver=self._schedule_data_reget)
	#----------------------------------------------------
	# event handlers
	#----------------------------------------------------
	def OnSize (self, event):
		w, h = event.GetSize()
		self.mainsizer.SetDimension (0, 0, w, h)
	#----------------------------------------------------
	def on_given_shot_selected(self, event):
		"""
			Retrieve vaccination item object for a selected vaccinated indication
			and display in GUI
		"""
		id_vacc = event.GetClientData()
		emr = self.__pat.get_clinical_record()
		if emr is None:
			# FIXME: error message
			return None
		self.editarea.set_data(emr.get_vaccinations(ID = id_vacc))
	#----------------------------------------------------
	def on_missing_shot_selected(self, event):
		print "now editing missing shot:", event.GetSelection(), event.GetString(), event.IsSelection(), event.GetClientData()
		id_vacc = event.GetClientData()
#		emr = self.__pat.get_clinical_record()
	#----------------------------------------------------
	def on_vaccinated_indication_selected(self, event):
		"""Update right hand middle list to show vaccinations given for selected indication."""
		ind_list = event.GetEventObject()
		selected_item = ind_list.GetSelection()
		ind = ind_list.GetClientData(selected_item)
		# clear list
		self.LBOX_given_shots.Set([])
		emr = self.__pat.get_clinical_record()
		if emr is None:
			# FIXME: error message
			return None
		shots = emr.get_vaccinations(indications = [ind])
		# FIXME: use Set() for entire array (but problem with client_data)
		for shot in shots:
			label = '%s: %s' % (shot['date'].Format('%m/%Y'), shot['vaccine'])
			data = shot['pk_vaccination']
			self.LBOX_given_shots.Append(label, data)
	#----------------------------------------------------
	def __reset_ui_content(self):
		# clear edit area
		self.editarea.set_data()
		# clear lists
		self.LBOX_vaccinated_indications.Clear()
		self.LBOX_given_shots.Clear()
		self.LBOX_missing_shots.Clear()
	#----------------------------------------------------
	def _populate_with_data(self):
		print "_populate_with_data() start"
		# clear lists
		self.LBOX_vaccinated_indications.Clear()
		self.LBOX_given_shots.Clear()
		self.LBOX_missing_shots.Clear()
		# populate vaccinated-indications list
		emr = self.__pat.get_clinical_record()
		if emr is None:
			# FIXME: error message
			return False
		status, indications = emr.get_vaccinated_indications()
		# FIXME: would be faster to use Set() but can't
		# use Set(labels, client_data), and have to know
		# line position in SetClientData :-(
		for indication in indications:
			self.LBOX_vaccinated_indications.Append(indication[1], indication[0])
#		self.LBOX_vaccinated_indications.Set(lines)
#		self.LBOX_vaccinated_indications.SetClientData(data)
		print "updated indications"

		# populate missing-shots list
		missing_shots = emr.get_missing_vaccinations()
		if missing_shots is None:
			label = _('ERROR: cannot retrieve due/overdue vaccinations')
			self.LBOX_missing_shots.Append(label, None)
			return True
		# due
		due_template = _('%.0d weeks left: shot %s for %s in %s, due %s (%s)')
		overdue_template = _('overdue %.0dyrs %.0dwks: shot %s for %s in schedule "%s (%s)"')
		for shot in missing_shots['due']:
			if shot['overdue']:
				years, days_left = divmod(shot['amount_overdue'].days, 364.25)
				weeks = days_left / 7
				# amount_overdue, seq_no, indication, regime, vacc_comment
				label = overdue_template % (
					years,
					weeks,
					shot['seq_no'],
					shot['l10n_indication'],
					shot['regime'],
					shot['vacc_comment']
				)
				self.LBOX_missing_shots.Append(label, None)	# pk_vacc_def
			else:
				# time_left, seq_no, regime, latest_due, vacc_comment
				label = due_template % (
					shot['time_left'].days / 7,
					shot['seq_no'],
					shot['indication'],
					shot['regime'],
					shot['latest_due'].Format('%m/%Y'),
					shot['vacc_comment']
				)
				self.LBOX_missing_shots.Append(label, None)	# pk_vacc_def
		# booster
		lbl_template = _('due now: booster for %s in schedule "%s (%s)"')
		for shot in missing_shots['boosters']:
			# indication, regime, vacc_comment
			label = lbl_template % (
				shot['l10n_indication'],
				shot['regime'],
				shot['vacc_comment']
			)
			self.LBOX_missing_shots.Append(label, None)	# pk_vacc_def
		return True
	#----------------------------------------------------
	def _on_patient_selected(self, **kwargs):
		return 1
		# FIXME:
#		if has_focus:
#			wxCallAfter(self.__reset_ui_content)
#		else:
#			return 1
	#----------------------------------------------------
	def _on_vaccinations_updated(self, **kwargs):
		return 1
		# FIXME:
#		if has_focus:
#			wxCallAfter(self.__reset_ui_content)
#		else:
#			is_stale == True
#			return 1
#======================================================================
# main
#----------------------------------------------------------------------
if __name__ == "__main__":
	_log.SetAllLogLevels(gmLog.lData)
	app = wxPyWidgetTester(size = (600, 600))
	app.SetWidget(cImmunisationsPanel, -1)
	app.MainLoop()
#======================================================================
# $Log: gmVaccWidgets.py,v $
# Revision 1.7  2004-09-13 19:19:41  ncq
# - improved missing booster string
#
# Revision 1.6  2004/09/13 09:28:26  ncq
# - improve strings
#
# Revision 1.5  2004/08/18 08:30:25  ncq
# - what used to be v_vacc_regimes now is v_vacc_defs4reg
#
# Revision 1.4  2004/07/28 15:40:53  ncq
# - convert to EVT_PAINT framework
#
# Revision 1.3  2004/07/18 20:12:03  ncq
# - vacc business object primary key is named pk_vaccination in view
#
# Revision 1.2  2004/07/17 21:11:47  ncq
# - use gmTerryGuiParts
#
# Revision 1.1  2004/07/15 23:16:20  ncq
# - refactor vaccinations GUI code into
#   - gmVaccWidgets.py: layout manager independant widgets
#   - gui/gmVaccinationsPlugins.py: Horst space notebook plugin
#   - patient/gmPG_Immunisation.py: erstwhile Richard space patient plugin
#
