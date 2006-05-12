"""GnuMed immunisation/vaccination widgets.

Modelled after Richard Terry's design document.

copyright: authors
"""
#======================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmVaccWidgets.py,v $
# $Id: gmVaccWidgets.py,v 1.26 2006-05-12 12:18:11 ncq Exp $
__version__ = "$Revision: 1.26 $"
__author__ = "R.Terry, S.J.Tan, K.Hilbert"
__license__ = "GPL (details at http://www.gnu.org)"

import sys, time

try:
	import wxversion
	import wx
except ImportError:
	from wxPython import wx

import mx.DateTime as mxDT

from Gnumed.wxpython import gmEditArea, gmPhraseWheel, gmTerryGuiParts, gmRegetMixin, gmGuiHelpers
from Gnumed.business import gmPerson, gmVaccination
from Gnumed.pycommon import gmLog, gmDispatcher, gmSignals, gmExceptions, gmMatchProvider

_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)
#======================================================================
class cVaccinationEditArea(gmEditArea.cEditArea2):
	"""
	- warn on apparent duplicates
	- ask if "missing" (= previous, non-recorded) vaccinations
	  should be estimated and saved (add note "auto-generated")
	"""
	def __init__(self, parent, id, pos, size, style, data_sink=None):
		gmEditArea.cEditArea2.__init__(self, parent, id, pos, size, style)
		self.__data_sink = data_sink
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
				pk,
				trade_name
			from
				vaccine
			where
				short_name || ' ' || trade_name %(fragment_condition)s
			limit 25"""
		mp = gmMatchProvider.cMatchProvider_SQL2('historica', [query])
		mp.setThresholds(aWord=2, aSubstring=4)
		self.fld_vaccine = gmPhraseWheel.cPhraseWheel(
			parent = parent
			, id = -1
			, aMatchProvider = mp
			, style = wx.SIMPLE_BORDER
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
		mp = gmMatchProvider.cMatchProvider_SQL2('historica', [query])
		mp.setThresholds(aWord=1, aSubstring=3)
		self.fld_site_given = gmPhraseWheel.cPhraseWheel(
			parent = parent
			, id = -1
			, aMatchProvider = mp
			, style = wx.SIMPLE_BORDER
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
		mp = gmMatchProvider.cMatchProvider_SQL2('historica', [query])
		mp.setThresholds(aWord=3, aSubstring=5)
		self.fld_progress_note = gmPhraseWheel.cPhraseWheel(
			parent = parent
			, id = -1
			, aMatchProvider = mp
			, style = wx.SIMPLE_BORDER
		)
		gmEditArea._decorate_editarea_field(self.fld_progress_note)
		self._add_field(
			line = 5,
			pos = 1,
			widget = self.fld_progress_note,
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
	#----------------------------------------------------
	def _save_new_entry(self, episode):
		# FIXME: validation ?
		if self.__data_sink is None:
			# save directly into database
			emr = self._patient.get_emr()
			# create new vaccination
			successfull, data = emr.add_vaccination(vaccine=self.fld_vaccine.GetValue(), episode=episode)
			if not successfull:
				gmGuiHelpers.gm_beep_statustext(_('Cannot save vaccination: %s') % data)
				return False
			# update it with known data
			data['pk_provider'] = gmPerson.gmCurrentProvider()['pk_staff']
			data['date'] = self.fld_date_given.GetValue()
			data['narrative'] = self.fld_progress_note.GetValue()
			data['site'] = self.fld_site_given.GetValue()
			data['batch_no'] = self.fld_batch_no.GetValue()
			successful, err = data.save_payload()
			if not successful:
				gmGuiHelpers.gm_beep_statustext(_('Cannot save new vaccination: %s') % err)
				return False
			gmGuiHelpers.gm_beep_statustext(_('Vaccination saved.'))
			self.data = data
			return True
		else:
			# pump into data sink
			data = {
				'vaccine': self.fld_vaccine.GetValue(),
				'pk_provider': gmPerson.gmCurrentProvider()['pk_staff'],
				'date': self.fld_date_given.GetValue(),
				'narrative': self.fld_progress_note.GetValue(),
				'site': self.fld_site_given.GetValue(),
				'batch_no': self.fld_batch_no.GetValue()
			}
			# FIXME: old_desc
			successful = self.__data_sink (
				popup_type = 'vaccination',
				data = data,
				desc = _('shot: %s, %s, %s') % (data['date'], data['vaccine'], data['site'])
			)
			if not successful:
				gmGuiHelpers.gm_beep_statustext(_('Cannot queue new vaccination.'))
				return False
			gmGuiHelpers.gm_beep_statustext(_('Vaccination queued for saving.'))
			return True
	#----------------------------------------------------
	def _save_modified_entry(self):
		"""Update vaccination object and persist to backend.
		"""
		self.data['vaccine'] = self.fld_vaccine.GetValue()
		self.data['batch_no'] = self.fld_batch_no.GetValue()
		self.data['date'] = self.fld_date_given.GetValue()
		self.data['site'] = self.fld_site_given.GetValue()
		self.data['narrative'] = self.fld_progress_note.GetValue()
		successfull, data = self.data.save_payload()
		if not successfull:
			gmGuiHelpers.gm_beep_statustext(_('Cannot update vaccination: %s') % err)
			return False
		gmGuiHelpers.gm_beep_statustext(_('Vaccination updated.'))
		return True
	#----------------------------------------------------
	def save_data(self, episode=None):
		if self.data is None:
			return self._save_new_entry(episode=episode)
		else:
			return self._save_modified_entry()
	#----------------------------------------------------
	def set_data(self, aVacc = None):
		"""Set edit area fields with vaccination object data.

		- set defaults if no object is passed in, this will
		  result in a new object being created upon saving
		"""
		# no vaccination passed in
		if aVacc is None:
			self.data = None
			self.fld_vaccine.SetValue('')
			self.fld_batch_no.SetValue('')
			self.fld_date_given.SetValue((time.strftime('%Y-%m-%d', time.localtime())))
			self.fld_site_given.SetValue(_('left/right deltoid'))
			self.fld_progress_note.SetValue('')
			return True

		# previous vaccination for modification ?
		if isinstance(aVacc, gmVaccination.cVaccination):
			self.data = aVacc
			self.fld_vaccine.SetValue(aVacc['vaccine'])
			self.fld_batch_no.SetValue(aVacc['batch_no'])
			self.fld_date_given.SetValue(aVacc['date'].Format('%Y-%m-%d'))
			self.fld_site_given.SetValue(aVacc['site'])
			self.fld_progress_note.SetValue(aVacc['narrative'])
			return True

		# vaccination selected from list of missing ones
		if isinstance(aVacc, gmVaccination.cMissingVaccination):
			self.data = None
			# FIXME: check for gap in seq_idx and offer filling in missing ones ?
			self.fld_vaccine.SetValue('')
			self.fld_batch_no.SetValue('')
			self.fld_date_given.SetValue((time.strftime('%Y-%m-%d', time.localtime())))
			# FIXME: use previously used value from table ?
			self.fld_site_given.SetValue(_('left/right deltoid'))
			if aVacc['overdue']:
				self.fld_progress_note.SetValue(_('was due: %s, delayed because:') % aVacc['latest_due'].Format('%Y-%m-%d'))
			else:
				self.fld_progress_note.SetValue('')
			return True

		# booster selected from list of missing ones
		if isinstance(aVacc, gmVaccination.cMissingBooster):
			self.data = None
			self.fld_vaccine.SetValue('')
			self.fld_batch_no.SetValue('')
			self.fld_date_given.SetValue((time.strftime('%Y-%m-%d', time.localtime())))
			# FIXME: use previously used value from table ?
			self.fld_site_given.SetValue(_('left/right deltoid'))
			if aVacc['overdue']:
				self.fld_progress_note.SetValue(_('booster: was due: %s, delayed because:') % aVacc['latest_due'].Format('%Y-%m-%d'))
			else:
				self.fld_progress_note.SetValue(_('booster'))
			return True

		_log.Log(gmLog.lErr, 'do not know how to handle [%s:%s]' % (type(aVacc), str(aVacc)))
		return False
#======================================================================
class cImmunisationsPanel(wx.Panel, gmRegetMixin.cRegetOnPaintMixin):

	def __init__(self, parent, id):
		wx.Panel.__init__(self, parent, id, wx.DefaultPosition, wx.DefaultSize, wx.RAISED_BORDER)
		gmRegetMixin.cRegetOnPaintMixin.__init__(self)
		self.__pat = gmPerson.gmCurrentPatient()
		# do this here so "import cImmunisationsPanel from gmVaccWidgets" works
		self.ID_VaccinatedIndicationsList = wx.NewId()
		self.ID_VaccinationsPerRegimeList = wx.NewId()
		self.ID_MissingShots = wx.NewId()
		self.ID_ActiveSchedules = wx.NewId()
		self.__do_layout()
		self.__register_interests()
		self.__reset_ui_content()
	#----------------------------------------------------
	def __do_layout(self):
		#-----------------------------------------------
		# top part
		#-----------------------------------------------
		pnl_UpperCaption = gmTerryGuiParts.cHeadingCaption(self, -1, _("  IMMUNISATIONS  "))
		self.editarea = cVaccinationEditArea(self, -1, wx.DefaultPosition, wx.DefaultSize, wx.NO_BORDER)

		#-----------------------------------------------
		# middle part
		#-----------------------------------------------
		# divider headings below editing area
		indications_heading = gmTerryGuiParts.cDividerCaption(self, -1, _("Indications"))
		vaccinations_heading = gmTerryGuiParts.cDividerCaption(self, -1, _("Vaccinations"))
		schedules_heading = gmTerryGuiParts.cDividerCaption(self, -1, _("Active Schedules"))
		szr_MiddleCap = wx.BoxSizer(wx.HORIZONTAL)
		szr_MiddleCap.Add(indications_heading, 4, wx.EXPAND)
		szr_MiddleCap.Add(vaccinations_heading, 6, wx.EXPAND)
		szr_MiddleCap.Add(schedules_heading, 10, wx.EXPAND)

		# left list: indications for which vaccinations have been given
		self.LBOX_vaccinated_indications = wx.ListBox(
			parent = self,
			id = self.ID_VaccinatedIndicationsList,
			choices = [],
			style = wx.LB_HSCROLL | wx.LB_NEEDED_SB | wx.SUNKEN_BORDER
		)
		self.LBOX_vaccinated_indications.SetFont(wx.Font(12,wx.SWISS, wx.NORMAL, wx.NORMAL, False, ''))

		# right list: when an indication has been selected on the left
		# display the corresponding vaccinations on the right
		self.LBOX_given_shots = wx.ListBox(
			parent = self,
			id = self.ID_VaccinationsPerRegimeList,
			choices = [],
			style = wx.LB_HSCROLL | wx.LB_NEEDED_SB | wx.SUNKEN_BORDER
		)
		self.LBOX_given_shots.SetFont(wx.Font(12,wx.SWISS, wx.NORMAL, wx.NORMAL, False, ''))

		self.LBOX_active_schedules = wx.ListBox (
			parent = self,
			id = self.ID_ActiveSchedules,
			choices = [],
			style = wx.LB_HSCROLL | wx.LB_NEEDED_SB | wx.SUNKEN_BORDER
		)
		self.LBOX_active_schedules.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.NORMAL, False, ''))

		szr_MiddleLists = wx.BoxSizer(wx.HORIZONTAL)
		szr_MiddleLists.Add(self.LBOX_vaccinated_indications, 4, wx.EXPAND)
		szr_MiddleLists.Add(self.LBOX_given_shots, 6, wx.EXPAND)
		szr_MiddleLists.Add(self.LBOX_active_schedules, 10, wx.EXPAND)

		#---------------------------------------------
		# bottom part
		#---------------------------------------------
		missing_heading = gmTerryGuiParts.cDividerCaption(self, -1, _("Missing Immunisations"))
		szr_BottomCap = wx.BoxSizer(wx.HORIZONTAL)
		szr_BottomCap.Add(missing_heading, 1, wx.EXPAND)

		self.LBOX_missing_shots = wx.ListBox (
			parent = self,
			id = self.ID_MissingShots,
			choices = [],
			style = wx.LB_HSCROLL | wx.LB_NEEDED_SB | wx.SUNKEN_BORDER
		)
		self.LBOX_missing_shots.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.NORMAL, False, ''))

		szr_BottomLists = wx.BoxSizer(wx.HORIZONTAL)
		szr_BottomLists.Add(self.LBOX_missing_shots, 1, wx.EXPAND)

		# alert caption
		pnl_AlertCaption = gmTerryGuiParts.cAlertCaption(self, -1, _('  Alerts  '))

		#---------------------------------------------
		# add all elements to the main background sizer
		#---------------------------------------------
		self.mainsizer = wx.BoxSizer(wx.VERTICAL)
		self.mainsizer.Add(pnl_UpperCaption, 0, wx.EXPAND)
		self.mainsizer.Add(self.editarea, 6, wx.EXPAND)
		self.mainsizer.Add(szr_MiddleCap, 0, wx.EXPAND)
		self.mainsizer.Add(szr_MiddleLists, 4, wx.EXPAND)
		self.mainsizer.Add(szr_BottomCap, 0, wx.EXPAND)
		self.mainsizer.Add(szr_BottomLists, 4, wx.EXPAND)
		self.mainsizer.Add(pnl_AlertCaption, 0, wx.EXPAND)

		self.SetAutoLayout(True)
		self.SetSizer(self.mainsizer)
		self.mainsizer.Fit(self)
	#----------------------------------------------------
	def __register_interests(self):
		# wxPython events
		wx.EVT_SIZE(self, self.OnSize)
		wx.EVT_LISTBOX(self, self.ID_VaccinatedIndicationsList, self._on_vaccinated_indication_selected)
		wx.EVT_LISTBOX_DCLICK(self, self.ID_VaccinationsPerRegimeList, self._on_given_shot_selected)
		wx.EVT_LISTBOX_DCLICK(self, self.ID_MissingShots, self._on_missing_shot_selected)
#		wx.EVT_RIGHT_UP(self.lb1, self.EvtRightButton)

		# client internal signals
		gmDispatcher.connect(signal=gmSignals.patient_selected(), receiver=self._schedule_data_reget)
		gmDispatcher.connect(signal=gmSignals.vaccinations_updated(), receiver=self._schedule_data_reget)
	#----------------------------------------------------
	# event handlers
	#----------------------------------------------------
	def OnSize (self, event):
		w, h = event.GetSize()
		self.mainsizer.SetDimension (0, 0, w, h)
	#----------------------------------------------------
	def _on_given_shot_selected(self, event):
		"""Paste previously given shot into edit area.
		"""
		self.editarea.set_data(aVacc=event.GetClientData())
	#----------------------------------------------------
	def _on_missing_shot_selected(self, event):
		self.editarea.set_data(aVacc = event.GetClientData())
	#----------------------------------------------------
	def _on_vaccinated_indication_selected(self, event):
		"""Update right hand middle list to show vaccinations given for selected indication."""
		ind_list = event.GetEventObject()
		selected_item = ind_list.GetSelection()
		ind = ind_list.GetClientData(selected_item)
		# clear list
		self.LBOX_given_shots.Set([])
		emr = self.__pat.get_emr()
		shots = emr.get_vaccinations(indications = [ind])
		# FIXME: use Set() for entire array (but problem with client_data)
		for shot in shots:
			if shot['is_booster']:
				marker = 'B'
			else:
				marker = '#%s' % shot['seq_no']
			label = '%s - %s: %s' % (marker, shot['date'].Format('%m/%Y'), shot['vaccine'])
			self.LBOX_given_shots.Append(label, shot)
	#----------------------------------------------------
	def __reset_ui_content(self):
		# clear edit area
		self.editarea.set_data()
		# clear lists
		self.LBOX_vaccinated_indications.Clear()
		self.LBOX_given_shots.Clear()
		self.LBOX_active_schedules.Clear()
		self.LBOX_missing_shots.Clear()
	#----------------------------------------------------
	def _populate_with_data(self):
		# clear lists
		self.LBOX_vaccinated_indications.Clear()
		self.LBOX_given_shots.Clear()
		self.LBOX_active_schedules.Clear()
		self.LBOX_missing_shots.Clear()

		emr = self.__pat.get_emr()

		t1 = time.time()
		# populate vaccinated-indications list
		# FIXME: consider adding virtual indication "most recent" to
		# FIXME: display most recent of all indications as suggested by Syan
		status, indications = emr.get_vaccinated_indications()
		# FIXME: would be faster to use Set() but can't
		# use Set(labels, client_data), and have to know
		# line position in SetClientData :-(
		for indication in indications:
			self.LBOX_vaccinated_indications.Append(indication[1], indication[0])
#		self.LBOX_vaccinated_indications.Set(lines)
#		self.LBOX_vaccinated_indications.SetClientData(data)
		print "vaccinated indications took", time.time()-t1, "seconds"

		t1 = time.time()
		# populate active schedules list
		scheds = emr.get_scheduled_vaccination_regimes()
		if scheds is None:
			label = _('ERROR: cannot retrieve active vaccination schedules')
			self.LBOX_active_schedules.Append(label)
		elif len(scheds) == 0:
			label = _('no active vaccination schedules')
			self.LBOX_active_schedules.Append(label)
		else:
			for sched in scheds:
				label = _('%s for %s (%s shots): %s') % (sched['regime'], sched['l10n_indication'], sched['shots'], sched['comment'])
				self.LBOX_active_schedules.Append(label)
		print "active schedules took", time.time()-t1, "seconds"

		t1 = time.time()
		# populate missing-shots list
		missing_shots = emr.get_missing_vaccinations()
		print "getting missing shots took", time.time()-t1, "seconds"
		if missing_shots is None:
			label = _('ERROR: cannot retrieve due/overdue vaccinations')
			self.LBOX_missing_shots.Append(label, None)
			return True
		# due
		due_template = _('%.0d weeks left: shot %s for %s in %s, due %s (%s)')
		overdue_template = _('overdue %.0dyrs %.0dwks: shot %s for %s in schedule "%s" (%s)')
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
				self.LBOX_missing_shots.Append(label, shot)
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
				self.LBOX_missing_shots.Append(label, shot)
		# booster
		lbl_template = _('due now: booster for %s in schedule "%s" (%s)')
		for shot in missing_shots['boosters']:
			# indication, regime, vacc_comment
			label = lbl_template % (
				shot['l10n_indication'],
				shot['regime'],
				shot['vacc_comment']
			)
			self.LBOX_missing_shots.Append(label, shot)
		print "displaying missing shots took", time.time()-t1, "seconds"

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
# Revision 1.26  2006-05-12 12:18:11  ncq
# - whoami -> whereami cleanup
# - use gmCurrentProvider()
#
# Revision 1.25  2006/05/04 09:49:20  ncq
# - get_clinical_record() -> get_emr()
# - adjust to changes in set_active_patient()
# - need explicit set_active_patient() after ask_for_patient() if wanted
#
# Revision 1.24  2005/12/29 21:54:35  ncq
# - adjust to schema changes
#
# Revision 1.23  2005/10/21 09:27:11  ncq
# - propagate new way of popup data saving
#
# Revision 1.22  2005/09/28 21:27:30  ncq
# - a lot of wx2.6-ification
#
# Revision 1.21  2005/09/28 15:57:48  ncq
# - a whole bunch of wx.Foo -> wx.Foo
#
# Revision 1.20  2005/09/26 18:01:51  ncq
# - use proper way to import wx26 vs wx2.4
# - note: THIS WILL BREAK RUNNING THE CLIENT IN SOME PLACES
# - time for fixup
#
# Revision 1.19  2005/09/26 04:30:33  ihaywood
# allow problem to be passed to vaccs popup
# use the same popup method as for cHealthIssue
# get rid of the second set of OK/Cancel buttons
#
# Revision 1.18  2005/09/24 09:17:29  ncq
# - some wx2.6 compatibility fixes
#
# Revision 1.17  2005/06/10 23:22:43  ncq
# - SQL2 match provider now requires query *list*
#
# Revision 1.16  2005/04/20 22:23:36  ncq
# - cNewVaccinationPopup
#
# Revision 1.15  2005/04/18 19:26:43  ncq
# - inherit vaccinations edit area from cEditArea2
#
# Revision 1.14  2005/03/08 16:46:55  ncq
# - add FIXME for virtual indication suggestion by Syan
#
# Revision 1.13  2005/01/31 10:37:26  ncq
# - gmPatient.py -> gmPerson.py
#
# Revision 1.12  2004/12/15 22:14:21  ncq
# - convert to new style edit area
#
# Revision 1.11  2004/10/27 12:16:54  ncq
# - make wxNewId() call internal to classes so that
#   "import <a class> from <us>" works properly
# - cleanup, properly use helpers
# - properly deal with save_payload/add_vaccination results
# - rearrange middle panel to include active schedules
#
# Revision 1.10  2004/10/11 20:11:32  ncq
# - cleanup
# - attach vacc VOs directly to list items
# - add editing (eg. adding) missing vaccination
#
# Revision 1.9  2004/10/01 11:50:45  ncq
# - cleanup
#
# Revision 1.8  2004/09/18 13:55:28  ncq
# - cleanup
#
# Revision 1.7  2004/09/13 19:19:41  ncq
# - improved missing booster string
#
# Revision 1.6  2004/09/13 09:28:26  ncq
# - improve strings
#
# Revision 1.5  2004/08/18 08:30:25  ncq
# - what used to be v_vacc_regimes now is v_vacc_defs4reg
#
# Revision 1.4  2004/07/28 15:40:53  ncq
# - convert to wx.EVT_PAINT framework
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
