"""GNUmed immunisation/vaccination widgets.

Modelled after Richard Terry's design document.

copyright: authors
"""
#======================================================================
__version__ = "$Revision: 1.36 $"
__author__ = "R.Terry, S.J.Tan, K.Hilbert"
__license__ = "GPL (details at http://www.gnu.org)"

import sys, time, logging


import wx
import mx.DateTime as mxDT


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmDispatcher, gmMatchProvider, gmTools, gmI18N
from Gnumed.business import gmPerson, gmVaccination
from Gnumed.wxpython import gmPhraseWheel, gmTerryGuiParts, gmRegetMixin, gmGuiHelpers
from Gnumed.wxpython import gmEditArea, gmListWidgets


_log = logging.getLogger('gm.vaccination')
_log.info(__version__)
#======================================================================
# vaccines related widgets
#----------------------------------------------------------------------
def manage_vaccines(parent=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()
	#------------------------------------------------------------
	def refresh(lctrl):
		vaccines = gmVaccination.get_vaccines(order_by = 'vaccine')

		items = [ [
			u'%s (#%s%s)' % (
				v['vaccine'],
				v['pk_brand'],
				gmTools.bool2subst (
					v['is_fake_vaccine'],
					u', %s' % _('fake'),
					u''
				)
			),
			v['preparation'],
			u'%s (%s)' % (v['route_abbreviation'], v['route_description']),
			gmTools.bool2subst(v['is_live'], gmTools.u_checkmark_thin, u''),
			gmTools.coalesce(v['atc_code'], u''),
			u'%s%s' % (
				gmTools.coalesce(v['min_age'], u'?'),
				gmTools.coalesce(v['max_age'], u'?', u' - %s'),
			),
			v['comment']
		] for v in vaccines ]
		lctrl.set_string_items(items)
		lctrl.set_data(vaccines)
	#------------------------------------------------------------
	gmListWidgets.get_choices_from_list (
		parent = parent,
		msg = _('\nThe vaccines currently known to GNUmed.\n'),
		caption = _('Showing vaccines.'),
		columns = [ u'Brand', _('Preparation'), _(u'Route'), _('Live'), _('ATC'), _('Age range'), _('Comment') ],
		single_selection = True,
		refresh_callback = refresh
	)
#======================================================================
# vaccination related widgets
#----------------------------------------------------------------------
def manage_vaccinations(parent=None):

	pat = gmPerson.gmCurrentPatient()
	emr = pat.get_emr()

	if parent is None:
		parent = wx.GetApp().GetTopWindow()
	#------------------------------------------------------------
	def refresh(lctrl):

		vaccs = emr.get_vaccinations(order_by = 'date_given DESC, pk_vaccination')

		items = [ [
			v['date_given'].strftime('%Y %B %d').decode(gmI18N.get_encoding()),
			v['vaccine'],
			u', '.join(v['indications']),
			v['batch_no'],
			gmTools.coalesce(v['site'], u''),
			gmTools.coalesce(v['reaction'], u''),
			gmTools.coalesce(v['comment'], u'')
		] for v in vaccs ]

		lctrl.set_string_items(items)
		lctrl.set_data(vaccs)
	#------------------------------------------------------------
	gmListWidgets.get_choices_from_list (
		parent = parent,
		msg = _('\nComplete vaccination history for this patient.\n'),
		caption = _('Showing vaccinations.'),
		columns = [ u'Date', _('Vaccine'), _(u'Indications'), _('Batch'), _('Site'), _('Reaction'), _('Comment') ],
		single_selection = True,
		refresh_callback = refresh
	)
#----------------------------------------------------------------------
from Gnumed.wxGladeWidgets import wxgVaccinationEAPnl

class cVaccinationEAPnl(wxgVaccinationEAPnl.wxgVaccinationEAPnl, gmEditArea.cGenericEditAreaMixin):

	def __init__(self, *args, **kwargs):

		try:
			data = kwargs['vaccination']
			del kwargs['vaccination']
		except KeyError:
			data = None

		wxgVaccinationEAPnl.wxgVaccinationEAPnl.__init__(self, *args, **kwargs)
		gmEditArea.cGenericEditAreaMixin.__init__(self)

		# Code using this mixin should set mode and data
		# after instantiating the class:
		self.mode = 'new'
		self.data = data
		if data is not None:
			self.mode = 'edit'

		#self.__init_ui()
	#----------------------------------------------------------------
#	def __init_ui(self):
#		# adjust phrasewheels etc
	#----------------------------------------------------------------
	# generic Edit Area mixin API
	#----------------------------------------------------------------
	def _valid_for_save(self):
		return False
		return True
	#----------------------------------------------------------------
	def _save_as_new(self):
		# save the data as a new instance
		data = 1

		data[''] = 1
		data[''] = 1

		data.save()

		# must be done very late or else the property access
		# will refresh the display such that later field
		# access will return empty values
		self.data = data
		return False
		return True
	#----------------------------------------------------------------
	def _save_as_update(self):
		# update self.data and save the changes
		self.data[''] = 1
		self.data[''] = 1
		self.data[''] = 1
		self.data.save()
		return True
	#----------------------------------------------------------------
	def _refresh_as_new(self):
		pass
	#----------------------------------------------------------------
	def _refresh_from_existing(self):
		pass
	#----------------------------------------------------------------
	def _refresh_as_new_from_existing(self):
		pass
	#----------------------------------------------------------------




#======================================================================
class cVaccinationEditAreaOld(gmEditArea.cEditArea2):
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
		mp = gmMatchProvider.cMatchProvider_SQL2([query])
		mp.setThresholds(aWord=2, aSubstring=4)
		self.fld_vaccine = gmPhraseWheel.cPhraseWheel(
			parent = parent
			, id = -1
			, style = wx.SIMPLE_BORDER
		)
		self.fld_vaccine.matcher = mp
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
		mp = gmMatchProvider.cMatchProvider_SQL2([query])
		mp.setThresholds(aWord=1, aSubstring=3)
		self.fld_site_given = gmPhraseWheel.cPhraseWheel(
			parent = parent
			, id = -1
			, style = wx.SIMPLE_BORDER
		)
		self.fld_site_given.matcher = mp
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
		mp = gmMatchProvider.cMatchProvider_SQL2([query])
		mp.setThresholds(aWord=3, aSubstring=5)
		self.fld_progress_note = gmPhraseWheel.cPhraseWheel(
			parent = parent
			, id = -1
			, style = wx.SIMPLE_BORDER
		)
		self.fld_progress_note = mp
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
				gmDispatcher.send(signal = 'statustext', msg =_('Cannot save vaccination: %s') % data)
				return False
			# update it with known data
			data['pk_provider'] = gmPerson.gmCurrentProvider()['pk_staff']
			data['date'] = self.fld_date_given.GetValue()
			data['narrative'] = self.fld_progress_note.GetValue()
			data['site'] = self.fld_site_given.GetValue()
			data['batch_no'] = self.fld_batch_no.GetValue()
			successful, err = data.save_payload()
			if not successful:
				gmDispatcher.send(signal = 'statustext', msg =_('Cannot save new vaccination: %s') % err)
				return False
			gmDispatcher.send(signal = 'statustext', msg =_('Vaccination saved.'))
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
				gmDispatcher.send(signal = 'statustext', msg =_('Cannot queue new vaccination.'))
				return False
			gmDispatcher.send(signal = 'statustext', msg =_('Vaccination queued for saving.'))
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
			gmDispatcher.send(signal = 'statustext', msg =_('Cannot update vaccination: %s') % err)
			return False
		gmDispatcher.send(signal = 'statustext', msg =_('Vaccination updated.'))
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
			self.fld_date_given.SetValue(aVacc['date'].strftime('%Y-%m-%d'))
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
				self.fld_progress_note.SetValue(_('was due: %s, delayed because:') % aVacc['latest_due'].strftime('%x'))
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
				self.fld_progress_note.SetValue(_('booster: was due: %s, delayed because:') % aVacc['latest_due'].strftime('%Y-%m-%d'))
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
		gmDispatcher.connect(signal= u'post_patient_selection', receiver=self._schedule_data_reget)
		gmDispatcher.connect(signal= u'vaccinations_updated', receiver=self._schedule_data_reget)
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
			label = '%s - %s: %s' % (marker, shot['date'].strftime('%m/%Y'), shot['vaccine'])
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
					shot['latest_due'].strftime('%m/%Y'),
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
	def _on_post_patient_selection(self, **kwargs):
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

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != u'test':
		sys.exit()

	app = wxPyWidgetTester(size = (600, 600))
	app.SetWidget(cImmunisationsPanel, -1)
	app.MainLoop()
#======================================================================

