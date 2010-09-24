"""GNUmed EMR structure editors

	This module contains widgets to create and edit EMR structural
	elements (issues, enconters, episodes).

	This is based on initial work and ideas by Syan <kittylitter@swiftdsl.com.au>
	and Karsten <Karsten.Hilbert@gmx.net>.
"""
#================================================================
__version__ = "$Revision: 1.114 $"
__author__ = "cfmoro1976@yahoo.es, karsten.hilbert@gmx.net"
__license__ = "GPL"

# stdlib
import sys, re, datetime as pydt, logging, time


# 3rd party
import wx
import wx.lib.pubsub as wxps


# GNUmed
if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmI18N, gmMatchProvider, gmDispatcher, gmTools, gmDateTime, gmCfg, gmExceptions
from Gnumed.business import gmEMRStructItems, gmPerson, gmSOAPimporter, gmSurgery, gmPersonSearch
from Gnumed.wxpython import gmPhraseWheel, gmGuiHelpers, gmListWidgets, gmEditArea, gmPatSearchWidgets
from Gnumed.wxGladeWidgets import wxgIssueSelectionDlg, wxgMoveNarrativeDlg
from Gnumed.wxGladeWidgets import wxgEncounterEditAreaPnl, wxgEncounterEditAreaDlg
from Gnumed.wxGladeWidgets import wxgEncounterTypeEditAreaPnl


_log = logging.getLogger('gm.ui')
_log.info(__version__)
#================================================================
# performed procedure related widgets/functions
#----------------------------------------------------------------
def manage_performed_procedures(parent=None):

	pat = gmPerson.gmCurrentPatient()
	emr = pat.get_emr()

	if parent is None:
		parent = wx.GetApp().GetTopWindow()
	#-----------------------------------------
	def edit(procedure=None):
		return edit_procedure(parent = parent, procedure = procedure)
	#-----------------------------------------
	def delete(procedure=None):
		if gmEMRStructItems.delete_performed_procedure(procedure = procedure['pk_procedure']):
			return True

		gmDispatcher.send (
			signal = u'statustext',
			msg = _('Cannot delete performed procedure.'),
			beep = True
		)
		return False
	#-----------------------------------------
	def refresh(lctrl):
		procs = emr.get_performed_procedures()

		items = [
			[
				p['clin_when'].strftime('%Y-%m-%d'),
				p['clin_where'],
				p['episode'],
				p['performed_procedure']
			] for p in procs
		]
		lctrl.set_string_items(items = items)
		lctrl.set_data(data = procs)
	#-----------------------------------------
	gmListWidgets.get_choices_from_list (
		parent = parent,
		msg = _('\nSelect the procedure you want to edit !\n'),
		caption = _('Editing performed procedures ...'),
		columns = [_('When'), _('Where'), _('Episode'), _('Procedure')],
		single_selection = True,
		edit_callback = edit,
		new_callback = edit,
		delete_callback = delete,
		refresh_callback = refresh
	)
#----------------------------------------------------------------
def edit_procedure(parent=None, procedure=None):
	ea = cProcedureEAPnl(parent = parent, id = -1)
	ea.data = procedure
	ea.mode = gmTools.coalesce(procedure, 'new', 'edit')
	dlg = gmEditArea.cGenericEditAreaDlg2(parent = parent, id = -1, edit_area = ea, single_entry = True)
	dlg.SetTitle(gmTools.coalesce(procedure, _('Adding a procedure'), _('Editing a procedure')))
	if dlg.ShowModal() == wx.ID_OK:
		dlg.Destroy()
		return True
	dlg.Destroy()
	return False
#----------------------------------------------------------------
from Gnumed.wxGladeWidgets import wxgProcedureEAPnl

class cProcedureEAPnl(wxgProcedureEAPnl.wxgProcedureEAPnl, gmEditArea.cGenericEditAreaMixin):

	def __init__(self, *args, **kwargs):
		wxgProcedureEAPnl.wxgProcedureEAPnl.__init__(self, *args, **kwargs)
		gmEditArea.cGenericEditAreaMixin.__init__(self)

		self.mode = 'new'
		self.data = None

		self.__init_ui()
	#----------------------------------------------------------------
	def __init_ui(self):
		self._PRW_hospital_stay.add_callback_on_lose_focus(callback = self._on_hospital_stay_lost_focus)
		self._PRW_location.add_callback_on_lose_focus(callback = self._on_location_lost_focus)

		# location
		mp = gmMatchProvider.cMatchProvider_SQL2 (
			queries = [
u"""
select distinct on (clin_where) clin_where, clin_where
from clin.procedure
where clin_where %(fragment_condition)s
order by clin_where
limit 25
"""			]
		)
		mp.setThresholds(2, 4, 6)
		self._PRW_location.matcher = mp

		# procedure
		mp = gmMatchProvider.cMatchProvider_SQL2 (
			queries = [
u"""
select distinct on (narrative) narrative, narrative
from clin.procedure
where narrative %(fragment_condition)s
order by narrative
limit 25
"""			]
		)
		mp.setThresholds(2, 4, 6)
		self._PRW_procedure.matcher = mp
	#----------------------------------------------------------------
	def _on_hospital_stay_lost_focus(self):
		if self._PRW_hospital_stay.GetData() is None:
			self._PRW_hospital_stay.SetText()
			self._PRW_location.Enable(True)
			self._PRW_episode.Enable(True)
		else:
			self._PRW_location.SetText()
			self._PRW_location.Enable(False)
			self._PRW_episode.SetText()
			self._PRW_episode.Enable(False)
	#----------------------------------------------------------------
	def _on_location_lost_focus(self):
		if self._PRW_location.GetValue().strip() == u'':
			self._PRW_hospital_stay.Enable(True)
#			self._PRW_episode.Enable(False)
		else:
			self._PRW_hospital_stay.SetText()
			self._PRW_hospital_stay.Enable(False)
#			self._PRW_episode.Enable(True)
	#----------------------------------------------------------------
	# generic Edit Area mixin API
	#----------------------------------------------------------------
	def _valid_for_save(self):

		has_errors = False

		if not self._DPRW_date.is_valid_timestamp():
			self._DPRW_date.display_as_valid(False)
			has_errors = True
		else:
			self._DPRW_date.display_as_valid(True)

		if self._PRW_hospital_stay.GetData() is None:
			if self._PRW_episode.GetData() is None:
				self._PRW_episode.display_as_valid(False)
				has_errors = True
			else:
				self._PRW_episode.display_as_valid(True)
		else:
			self._PRW_episode.display_as_valid(True)

		if (self._PRW_procedure.GetValue() is None) or (self._PRW_procedure.GetValue().strip() == u''):
			self._PRW_procedure.display_as_valid(False)
			has_errors = True
		else:
			self._PRW_procedure.display_as_valid(True)

		invalid_location = (
			(self._PRW_hospital_stay.GetData() is None) and (self._PRW_location.GetValue().strip() == u'')
				or
			(self._PRW_hospital_stay.GetData() is not None) and (self._PRW_location.GetValue().strip() != u'')
		)
		if invalid_location:
			self._PRW_hospital_stay.display_as_valid(False)
			self._PRW_location.display_as_valid(False)
			has_errors = True
		else:
			self._PRW_hospital_stay.display_as_valid(True)
			self._PRW_location.display_as_valid(True)

		wxps.Publisher().sendMessage (
			topic = 'statustext',
			data = {'msg': _('Cannot save procedure.'), 'beep': True}
		)

		return (has_errors is False)
	#----------------------------------------------------------------
	def _save_as_new(self):

		pat = gmPerson.gmCurrentPatient()
		emr = pat.get_emr()

		if self._PRW_hospital_stay.GetData() is None:
			stay = None
			epi = self._PRW_episode.GetData()
			loc = self._PRW_location.GetValue().strip()
		else:
			stay = self._PRW_hospital_stay.GetData()
			epi = gmEMRStructItems.cHospitalStay(aPK_obj = stay)['pk_episode']
			loc = None

		proc = emr.add_performed_procedure (
			episode = epi,
			location = loc,
			hospital_stay = stay,
			procedure = self._PRW_procedure.GetValue().strip()
		)
		proc['clin_when'] = self._DPRW_date.data.get_pydt()
		proc.save()

		self.data = proc

		return True
	#----------------------------------------------------------------
	def _save_as_update(self):
		self.data['clin_when'] = self._DPRW_date.data.get_pydt()

		if self._PRW_hospital_stay.GetData() is None:
			self.data['pk_hospital_stay'] = None
			self.data['clin_where'] = self._PRW_location.GetValue().strip()
			self.data['pk_episode'] = self._PRW_episode.GetData()
		else:
			self.data['pk_hospital_stay'] = self._PRW_hospital_stay.GetData()
			self.data['clin_where'] = None
			stay = gmEMRStructItems.cHospitalStay(aPK_obj = self._PRW_hospital_stay.GetData())
			self.data['pk_episode'] = stay['pk_episode']

		self.data['performed_procedure'] = self._PRW_procedure.GetValue().strip()

		self.data.save()
		return True
	#----------------------------------------------------------------
	def _refresh_as_new(self):
		self._DPRW_date.SetText()
		self._PRW_hospital_stay.SetText()
		self._PRW_location.SetText()
		self._PRW_episode.SetText()
		self._PRW_procedure.SetText()

		self._DPRW_date.SetFocus()
	#----------------------------------------------------------------
	def _refresh_from_existing(self):
		self._DPRW_date.SetData(data = self.data['clin_when'])
		self._PRW_episode.SetText(value = self.data['episode'], data = self.data['pk_episode'])
		self._PRW_procedure.SetText(value = self.data['performed_procedure'], data = self.data['performed_procedure'])

		if self.data['pk_hospital_stay'] is None:
			self._PRW_hospital_stay.SetText()
			self._PRW_location.SetText(value = self.data['clin_where'], data = self.data['clin_where'])
		else:
			self._PRW_hospital_stay.SetText(value = self.data['clin_where'], data = self.data['pk_hospital_stay'])
			self._PRW_location.SetText()

		self._DPRW_date.SetFocus()
	#----------------------------------------------------------------
	def _refresh_as_new_from_existing(self):
		self._refresh_as_new()
		self._PRW_episode.SetText(value = self.data['episode'], data = self.data['pk_episode'])
		if self.data['pk_hospital_stay'] is None:
			self._PRW_hospital_stay.SetText()
			self._PRW_location.SetText(value = self.data['clin_where'], data = self.data['clin_where'])
		else:
			self._PRW_hospital_stay.SetText(value = self.data['clin_where'], data = self.data['pk_hospital_stay'])
			self._PRW_location.SetText()

		self._DPRW_date.SetFocus()
	#----------------------------------------------------------------
	def _on_add_hospital_stay_button_pressed(self, evt):
		edit_hospital_stay(parent = self.GetParent())
		evt.Skip()
#================================================================
# hospital stay related widgets/functions
#----------------------------------------------------------------
def manage_hospital_stays(parent=None):

	pat = gmPerson.gmCurrentPatient()
	emr = pat.get_emr()

	if parent is None:
		parent = wx.GetApp().GetTopWindow()
	#-----------------------------------------
	def edit(stay=None):
		return edit_hospital_stay(parent = parent, hospital_stay = stay)
	#-----------------------------------------
	def delete(stay=None):
		if gmEMRStructItems.delete_hospital_stay(stay = stay['pk_hospital_stay']):
			return True
		gmDispatcher.send (
			signal = u'statustext',
			msg = _('Cannot delete hospital stay.'),
			beep = True
		)
		return False
	#-----------------------------------------
	def refresh(lctrl):
		stays = emr.get_hospital_stays()
		items = [
			[
				s['admission'].strftime('%Y-%m-%d'),
				gmTools.coalesce(s['discharge'], u''),
				s['episode'],
				gmTools.coalesce(s['hospital'], u'')
			] for s in stays
		]
		lctrl.set_string_items(items = items)
		lctrl.set_data(data = stays)
	#-----------------------------------------
	gmListWidgets.get_choices_from_list (
		parent = parent,
		msg = _('\nSelect the hospital stay you want to edit !\n'),
		caption = _('Editing hospital stays ...'),
		columns = [_('Admission'), _('Discharge'), _('Reason'), _('Hospital')],
		single_selection = True,
		edit_callback = edit,
		new_callback = edit,
		delete_callback = delete,
		refresh_callback = refresh
	)

#----------------------------------------------------------------
def edit_hospital_stay(parent=None, hospital_stay=None):
	ea = cHospitalStayEditAreaPnl(parent = parent, id = -1)
	ea.data = hospital_stay
	ea.mode = gmTools.coalesce(hospital_stay, 'new', 'edit')
	dlg = gmEditArea.cGenericEditAreaDlg2(parent = parent, id = -1, edit_area = ea, single_entry = True)
	dlg.SetTitle(gmTools.coalesce(hospital_stay, _('Adding a hospital stay'), _('Editing a hospital stay')))
	if dlg.ShowModal() == wx.ID_OK:
		dlg.Destroy()
		return True
	dlg.Destroy()
	return False
#----------------------------------------------------------------
class cHospitalStayPhraseWheel(gmPhraseWheel.cPhraseWheel):
	"""Phrasewheel to allow selection of a hospital stay.
	"""
	def __init__(self, *args, **kwargs):

		gmPhraseWheel.cPhraseWheel.__init__ (self, *args, **kwargs)

		ctxt = {'ctxt_pat': {'where_part': u'pk_patient = %(pat)s and', 'placeholder': u'pat'}}

		mp = gmMatchProvider.cMatchProvider_SQL2 (
			queries = [
u"""
select
	pk_hospital_stay,
	descr
from (
	select distinct on (pk_hospital_stay)
		pk_hospital_stay,
		descr
	from
		(select
			pk_hospital_stay,
			(
				to_char(admission, 'YYYY-Mon-DD')
				|| coalesce((' (' || hospital || '):'), ': ')
				|| episode
				|| coalesce((' (' || health_issue || ')'), '')
			) as descr
		 from
		 	clin.v_pat_hospital_stays
		 where
			%(ctxt_pat)s

			hospital %(fragment_condition)s
				or
			episode %(fragment_condition)s
				or
			health_issue %(fragment_condition)s
		) as the_stays
) as distinct_stays
order by descr
limit 25
"""			],
			context = ctxt
		)
		mp.setThresholds(3, 4, 6)
		mp.set_context('pat', gmPerson.gmCurrentPatient().ID)

		self.matcher = mp
		self.selection_only = True
#----------------------------------------------------------------
from Gnumed.wxGladeWidgets import wxgHospitalStayEditAreaPnl

class cHospitalStayEditAreaPnl(wxgHospitalStayEditAreaPnl.wxgHospitalStayEditAreaPnl, gmEditArea.cGenericEditAreaMixin):

	def __init__(self, *args, **kwargs):
		wxgHospitalStayEditAreaPnl.wxgHospitalStayEditAreaPnl.__init__(self, *args, **kwargs)
		gmEditArea.cGenericEditAreaMixin.__init__(self)
	#----------------------------------------------------------------
	# generic Edit Area mixin API
	#----------------------------------------------------------------
	def _valid_for_save(self):
		if not self._DP_admission.GetValue().IsValid():
			self._DP_admission.SetBackgroundColour(gmPhraseWheel.color_prw_invalid)
			wxps.Publisher().sendMessage (
				topic = 'statustext',
				data = {'msg': _('Missing admission data. Cannot save hospital stay.'), 'beep': True}
			)
			return False
		else:
			self._DP_admission.SetBackgroundColour(gmPhraseWheel.color_prw_valid)

		if self._DP_discharge.GetValue().IsValid():
			if not self._DP_discharge.GetValue().IsLaterThan(self._DP_admission.GetValue()):
				self._DP_discharge.SetBackgroundColour(gmPhraseWheel.color_prw_invalid)
				wxps.Publisher().sendMessage (
					topic = 'statustext',
					data = {'msg': _('Discharge date must be empty or later than admission. Cannot save hospital stay.'), 'beep': True}
				)
				return False

		if self._PRW_episode.GetValue().strip() == u'':
			self._PRW_episode.display_as_valid(False)
			wxps.Publisher().sendMessage (
				topic = 'statustext',
				data = {'msg': _('Must select an episode or enter a name for a new one. Cannot save hospital stay.'), 'beep': True}
			)
			return False

		return True
	#----------------------------------------------------------------
	def _save_as_new(self):

		pat = gmPerson.gmCurrentPatient()
		emr = pat.get_emr()

		stay = gmEMRStructItems.create_hospital_stay (
			encounter = emr.active_encounter['pk_encounter'],
			episode = self._PRW_episode.GetData(can_create = True)
		)
		stay['hospital'] = gmTools.none_if(self._PRW_hospital.GetValue().strip(), u'')
		stay['admission'] = gmDateTime.wxDate2py_dt(wxDate = self._DP_admission.GetValue())
		if self._DP_discharge.GetValue().IsValid():
			stay['discharge'] = gmDateTime.wxDate2py_dt(wxDate = self._DP_discharge.GetValue())
		stay.save_payload()

		self.data = stay
		return True
	#----------------------------------------------------------------
	def _save_as_update(self):

		self.data['pk_episode'] = self._PRW_episode.GetData(can_create = True)
		self.data['hospital'] = gmTools.none_if(self._PRW_hospital.GetValue().strip(), u'')
		self.data['admission'] = gmDateTime.wxDate2py_dt(wxDate = self._DP_admission.GetValue())
		if self._DP_discharge.GetValue().IsValid():
			self.data['discharge'] = gmDateTime.wxDate2py_dt(wxDate = self._DP_discharge.GetValue())
		self.data.save_payload()

		return True
	#----------------------------------------------------------------
	def _refresh_as_new(self):
		self._PRW_hospital.SetText(value = u'')
		self._PRW_episode.SetText(value = u'')
		self._DP_admission.SetValue(dt = wx.DateTime.UNow())
		#self._DP_discharge.SetValue(dt = None)
	#----------------------------------------------------------------
	def _refresh_from_existing(self):
		if self.data['hospital'] is not None:
			self._PRW_hospital.SetText(value = self.data['hospital'])

		if self.data['pk_episode'] is not None:
			self._PRW_episode.SetText(value = self.data['episode'], data = self.data['pk_episode'])

		self._DP_admission.SetValue(gmDateTime.py_dt2wxDate(py_dt = self.data['admission'], wx = wx))

		if self.data['discharge'] is not None:
			self._DP_discharge.SetValue(gmDateTime.py_dt2wxDate(py_dt = self.data['discharge'], wx = wx))
	#----------------------------------------------------------------
	def _refresh_as_new_from_existing(self):
		print "this was not expected to be used in this edit area"
#================================================================
# encounter related widgets/functions
#----------------------------------------------------------------
def start_new_encounter(emr=None):
	emr.start_new_encounter()
	gmDispatcher.send(signal = 'statustext', msg = _('Started a new encounter for the active patient.'), beep = True)
	time.sleep(0.5)
	gmGuiHelpers.gm_show_info (
		_('\nA new encounter was started for the active patient.\n'),
		_('Start of new encounter')
	)
#----------------------------------------------------------------
def edit_encounter(parent=None, encounter=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	# FIXME: use generic dialog 2
	dlg = cEncounterEditAreaDlg(parent = parent, encounter = encounter)
	dlg.ShowModal()
#----------------------------------------------------------------
def select_encounters(parent=None, patient=None, single_selection=True, encounters=None):

	if patient is None:
		patient = gmPerson.gmCurrentPatient()

	if not patient.connected:
		gmDispatcher.send(signal = 'statustext', msg = _('Cannot list encounters. No active patient.'))
		return False

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	emr = patient.get_emr()

	#--------------------
	def refresh(lctrl):
		if encounters is not None:
			encs = encounters
		else:
			encs = emr.get_encounters()

		items = [
			[
				e['started'].strftime('%x %H:%M'),
				e['last_affirmed'].strftime('%H:%M'),
				e['l10n_type'],
				gmTools.coalesce(e['reason_for_encounter'], u''),
				gmTools.coalesce(e['assessment_of_encounter'], u''),
				gmTools.bool2subst(e.has_clinical_data(), u'', gmTools.u_checkmark_thin),
				e['pk_encounter']
			] for e in encs
		]

		lctrl.set_string_items(items = items)
		lctrl.set_data(data = encs)
	#--------------------
	def edit(enc = None):
		return edit_encounter(parent = parent, encounter = enc)
	#--------------------
	return gmListWidgets.get_choices_from_list (
		parent = parent,
		msg = _('\nBelow find the relevant encounters of the patient.\n'),
		caption = _('Encounters ...'),
		columns = [_('Started'), _('Ended'), _('Type'), _('Reason for Encounter'), _('Assessment of Encounter'), _('Empty'), '#'],
		can_return_empty = True,
		single_selection = single_selection,
		refresh_callback = refresh,
		edit_callback = edit
	)
#----------------------------------------------------------------
def ask_for_encounter_continuation(msg=None, caption=None, encounter=None, parent=None):
	"""This is used as the callback when the EMR detects that the
	   patient was here rather recently and wants to ask the
	   provider whether to continue the recent encounter.
	"""
	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	dlg = gmGuiHelpers.c2ButtonQuestionDlg (
		parent = None,
		id = -1,
		caption = caption,
		question = msg,
		button_defs = [
			{'label': _('Continue'), 'tooltip': _('Continue the existing recent encounter.'), 'default': False},
			{'label': _('Start new'), 'tooltip': _('Start a new encounter. The existing one will be closed.'), 'default': True}
		],
		show_checkbox = False
	)

	result = dlg.ShowModal()
	dlg.Destroy()

	if result == wx.ID_YES:
		return True

	return False
#----------------------------------------------------------------
def manage_encounter_types(parent=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	#--------------------
	def edit(enc_type=None):
		return edit_encounter_type(parent = parent, encounter_type = enc_type)
	#--------------------
	def delete(enc_type=None):
		if gmEMRStructItems.delete_encounter_type(description = enc_type['description']):
			return True
		gmDispatcher.send (
			signal = u'statustext',
			msg = _('Cannot delete encounter type [%s]. It is in use.') % enc_type['l10n_description'],
			beep = True
		)
		return False
	#--------------------
	def refresh(lctrl):
		enc_types = gmEMRStructItems.get_encounter_types()
		lctrl.set_string_items(items = enc_types)
	#--------------------
	gmListWidgets.get_choices_from_list (
		parent = parent,
		msg = _('\nSelect the encounter type you want to edit !\n'),
		caption = _('Managing encounter types ...'),
		columns = [_('Local name'), _('Encounter type')],
		single_selection = True,
		edit_callback = edit,
		new_callback = edit,
		delete_callback = delete,
		refresh_callback = refresh
	)
#----------------------------------------------------------------
def edit_encounter_type(parent=None, encounter_type=None):
	ea = cEncounterTypeEditAreaPnl(parent = parent, id = -1)
	ea.data = encounter_type
	ea.mode = gmTools.coalesce(encounter_type, 'new', 'edit')
	dlg = gmEditArea.cGenericEditAreaDlg2(parent = parent, id = -1, edit_area = ea)
	dlg.SetTitle(gmTools.coalesce(encounter_type, _('Adding new encounter type'), _('Editing local encounter type name')))
	if dlg.ShowModal() == wx.ID_OK:
		return True
	return False
#----------------------------------------------------------------
class cEncounterTypePhraseWheel(gmPhraseWheel.cPhraseWheel):
	"""Phrasewheel to allow selection of encounter type.

	- user input interpreted as encounter type in English or local language
	- data returned is pk of corresponding encounter type or None
	"""
	def __init__(self, *args, **kwargs):

		gmPhraseWheel.cPhraseWheel.__init__ (self, *args, **kwargs)

		mp = gmMatchProvider.cMatchProvider_SQL2 (
			queries = [
u"""
select pk, l10n_description from (
	select distinct on (pk) * from (
		(select
			pk,
			_(description) as l10n_description,
			1 as rank
		from
			clin.encounter_type
		where
			_(description) %(fragment_condition)s

		) union all (

		select
			pk,
			_(description) as l10n_description,
			2 as rank
		from
			clin.encounter_type
		where
			description %(fragment_condition)s
		)
	) as q_distinct_pk
) as q_ordered order by rank, l10n_description
"""			]
		)
		mp.setThresholds(2, 4, 6)

		self.matcher = mp
		self.selection_only = True
		self.picklist_delay = 50
#----------------------------------------------------------------
class cEncounterTypeEditAreaPnl(wxgEncounterTypeEditAreaPnl.wxgEncounterTypeEditAreaPnl, gmEditArea.cGenericEditAreaMixin):

	def __init__(self, *args, **kwargs):

		wxgEncounterTypeEditAreaPnl.wxgEncounterTypeEditAreaPnl.__init__(self, *args, **kwargs)
		gmEditArea.cGenericEditAreaMixin.__init__(self)

#		self.__register_interests()
	#-------------------------------------------------------
	# generic edit area API
	#-------------------------------------------------------
	def _valid_for_save(self):
		if self.mode == 'edit':
			if self._TCTRL_l10n_name.GetValue().strip() == u'':
				self.display_tctrl_as_valid(tctrl = self._TCTRL_l10n_name, valid = False)
				return False
			self.display_tctrl_as_valid(tctrl = self._TCTRL_l10n_name, valid = True)
			return True

		no_errors = True

		if self._TCTRL_l10n_name.GetValue().strip() == u'':
			if self._TCTRL_name.GetValue().strip() == u'':
				self.display_tctrl_as_valid(tctrl = self._TCTRL_l10n_name, valid = False)
				no_errors = False
			else:
				self.display_tctrl_as_valid(tctrl = self._TCTRL_l10n_name, valid = True)
		else:
			self.display_tctrl_as_valid(tctrl = self._TCTRL_l10n_name, valid = True)

		if self._TCTRL_name.GetValue().strip() == u'':
			if self._TCTRL_l10n_name.GetValue().strip() == u'':
				self.display_tctrl_as_valid(tctrl = self._TCTRL_name, valid = False)
				no_errors = False
			else:
				self.display_tctrl_as_valid(tctrl = self._TCTRL_name, valid = True)
		else:
			self.display_tctrl_as_valid(tctrl = self._TCTRL_name, valid = True)

		return no_errors
	#-------------------------------------------------------
	def _save_as_new(self):
		enc_type = gmEMRStructItems.create_encounter_type (
			description = gmTools.none_if(self._TCTRL_name.GetValue().strip(), u''),
			l10n_description = gmTools.coalesce (
				gmTools.none_if(self._TCTRL_l10n_name.GetValue().strip(), u''),
				self._TCTRL_name.GetValue().strip()
			)
		)
		if enc_type is None:
			return False
		self.data = enc_type
		return True
	#-------------------------------------------------------
	def _save_as_update(self):
		enc_type = gmEMRStructItems.update_encounter_type (
			description = self._TCTRL_name.GetValue().strip(),
			l10n_description = self._TCTRL_l10n_name.GetValue().strip()
		)
		if enc_type is None:
			return False
		self.data = enc_type
		return True
	#-------------------------------------------------------
	def _refresh_as_new(self):
		self._TCTRL_l10n_name.SetValue(u'')
		self._TCTRL_name.SetValue(u'')
		self._TCTRL_name.Enable(True)
	#-------------------------------------------------------
	def _refresh_from_existing(self):
		self._TCTRL_l10n_name.SetValue(self.data['l10n_description'])
		self._TCTRL_name.SetValue(self.data['description'])
		# disallow changing type on all encounters by editing system name
		self._TCTRL_name.Enable(False)
	#-------------------------------------------------------
	def _refresh_as_new_from_existing(self):
		self._TCTRL_l10n_name.SetValue(self.data['l10n_description'])
		self._TCTRL_name.SetValue(self.data['description'])
		self._TCTRL_name.Enable(True)
	#-------------------------------------------------------
	# internal API
	#-------------------------------------------------------
#	def __register_interests(self):
#		return
#----------------------------------------------------------------
class cEncounterEditAreaPnl(wxgEncounterEditAreaPnl.wxgEncounterEditAreaPnl):

	def __init__(self, *args, **kwargs):
		try:
			self.__encounter = kwargs['encounter']
			del kwargs['encounter']
		except KeyError:
			self.__encounter = None

		try:
			msg = kwargs['msg']
			del kwargs['msg']
		except KeyError:
			msg = None

		wxgEncounterEditAreaPnl.wxgEncounterEditAreaPnl.__init__(self, *args, **kwargs)

		self.refresh(msg = msg)
	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def refresh(self, encounter=None, msg=None):

		if msg is not None:
			self._LBL_instructions.SetLabel(msg)

		if encounter is not None:
			self.__encounter = encounter

		if self.__encounter is None:
			return True

		# getting the patient via the encounter allows us to act
		# on any encounter regardless of the currently active patient
		pat = gmPerson.cPatient(aPK_obj = self.__encounter['pk_patient'])
		self._LBL_patient.SetLabel(pat.get_description_gender())

		self._PRW_encounter_type.SetText(self.__encounter['l10n_type'], data=self.__encounter['pk_type'])

		fts = gmDateTime.cFuzzyTimestamp (
			timestamp = self.__encounter['started'],
			accuracy = gmDateTime.acc_minutes
		)
		self._PRW_start.SetText(fts.format_accurately(), data=fts)

		fts = gmDateTime.cFuzzyTimestamp (
			timestamp = self.__encounter['last_affirmed'],
			accuracy = gmDateTime.acc_minutes
		)
		self._PRW_end.SetText(fts.format_accurately(), data=fts)

		self._TCTRL_rfe.SetValue(gmTools.coalesce(self.__encounter['reason_for_encounter'], ''))
		self._TCTRL_aoe.SetValue(gmTools.coalesce(self.__encounter['assessment_of_encounter'], ''))

		if self.__encounter['last_affirmed'] == self.__encounter['started']:
			self._PRW_end.SetFocus()
		else:
			self._TCTRL_aoe.SetFocus()

		return True
	#--------------------------------------------------------
	def __is_valid_for_save(self):

		if self._PRW_encounter_type.GetData() is None:
			self._PRW_encounter_type.SetBackgroundColour('pink')
			self._PRW_encounter_type.Refresh()
			self._PRW_encounter_type.SetFocus()
			return False
		self._PRW_encounter_type.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
		self._PRW_encounter_type.Refresh()

		if not self._PRW_start.is_valid_timestamp():
			self._PRW_start.SetFocus()
			return False

		if not self._PRW_end.is_valid_timestamp():
			self._PRW_end.SetFocus()
			return False

		return True
	#--------------------------------------------------------
	def save(self):
		if not self.__is_valid_for_save():
			return False

		self.__encounter['pk_type'] = self._PRW_encounter_type.GetData()
		self.__encounter['started'] = self._PRW_start.GetData().get_pydt()
		self.__encounter['last_affirmed'] = self._PRW_end.GetData().get_pydt()
		self.__encounter['reason_for_encounter'] = gmTools.none_if(self._TCTRL_rfe.GetValue().strip(), u'')
		self.__encounter['assessment_of_encounter'] = gmTools.none_if(self._TCTRL_aoe.GetValue().strip(), u'')
		self.__encounter.save_payload()			# FIXME: error checking

		return True
#----------------------------------------------------------------
# FIXME: use generic dialog 2
class cEncounterEditAreaDlg(wxgEncounterEditAreaDlg.wxgEncounterEditAreaDlg):

	def __init__(self, *args, **kwargs):
		encounter = kwargs['encounter']
		del kwargs['encounter']

		try:
			button_defs = kwargs['button_defs']
			del kwargs['button_defs']
		except KeyError:
			button_defs = None

		try:
			msg = kwargs['msg']
			del kwargs['msg']
		except KeyError:
			msg = None

		wxgEncounterEditAreaDlg.wxgEncounterEditAreaDlg.__init__(self, *args, **kwargs)
		self.SetSize((450, 280))
		self.SetMinSize((450, 280))

		if button_defs is not None:
			self._BTN_save.SetLabel(button_defs[0][0])
			self._BTN_save.SetToolTipString(button_defs[0][1])
			self._BTN_close.SetLabel(button_defs[1][0])
			self._BTN_close.SetToolTipString(button_defs[1][1])
			self.Refresh()

		self._PNL_edit_area.refresh(encounter = encounter, msg = msg)

		self.Fit()
	#--------------------------------------------------------
	def _on_save_button_pressed(self, evt):
		if self._PNL_edit_area.save():
			if self.IsModal():
				self.EndModal(wx.ID_OK)
			else:
				self.Close()
#================================================================
# episode related widgets/functions
#----------------------------------------------------------------
def edit_episode(parent=None, episode=None):
	ea = cEpisodeEditAreaPnl(parent = parent, id = -1)
	ea.data = episode
	ea.mode = gmTools.coalesce(episode, 'new', 'edit')
	dlg = gmEditArea.cGenericEditAreaDlg2(parent = parent, id = -1, edit_area = ea, single_entry = True)
	dlg.SetTitle(gmTools.coalesce(episode, _('Adding a new episode'), _('Editing an episode')))
	if dlg.ShowModal() == wx.ID_OK:
		return True
	return False
#----------------------------------------------------------------
def promote_episode_to_issue(parent=None, episode=None, emr=None):

	created_new_issue = False

	try:
		issue = gmEMRStructItems.cHealthIssue(name = episode['description'], patient = episode['pk_patient'])
	except gmExceptions.NoSuchBusinessObjectError:
		issue = None

	if issue is None:
		issue = emr.add_health_issue(issue_name = episode['description'])
		created_new_issue = True
	else:
		# issue exists already, so ask user
		dlg = gmGuiHelpers.c3ButtonQuestionDlg (
			parent,
			-1,
			caption = _('Promoting episode to health issue'),
			question = _(
				'There already is a health issue\n'
				'\n'
				' %s\n'
				'\n'
				'What do you want to do ?'
			) % issue['description'],
			button_defs = [
				{'label': _('Use existing'), 'tooltip': _('Move episode into existing health issue'), 'default': False},
				{'label': _('Create new'), 'tooltip': _('Create a new health issue with another name'), 'default': True}
			]
		)
		use_existing = dlg.ShowModal()
		dlg.Destroy()

		if use_existing == wx.ID_CANCEL:
			return

		# user wants to create new issue with alternate name
		if use_existing == wx.ID_NO:
			# loop until name modified but non-empty or cancelled
			issue_name = episode['description']
			while issue_name == episode['description']:
				dlg = wx.TextEntryDialog (
					parent = parent,
					message = _('Enter a short descriptive name for the new health issue:'),
					caption = _('Creating a new health issue ...'),
					defaultValue = issue_name,
					style = wx.OK | wx.CANCEL | wx.CENTRE
				)
				decision = dlg.ShowModal()
				if decision != wx.ID_OK:
					dlg.Destroy()
					return
				issue_name = dlg.GetValue().strip()
				dlg.Destroy()
				if issue_name == u'':
					issue_name = episode['description']

			issue = emr.add_health_issue(issue_name = issue_name)
			created_new_issue = True

	# eventually move the episode to the issue
	if not move_episode_to_issue(episode = episode, target_issue = issue, save_to_backend = True):
		# user cancelled the move so delete just-created issue
		if created_new_issue:
			# shouldn't fail as it is completely new
			gmEMRStructItems.delete_health_issue(health_issue = issue)
		return

	return
#----------------------------------------------------------------
def move_episode_to_issue(episode=None, target_issue=None, save_to_backend=False):
	"""Prepare changing health issue for an episode.

	Checks for two-open-episodes conflict. When this
	function succeeds, the pk_health_issue has been set
	on the episode instance and the episode should - for
	all practical purposes - be ready for save_payload().
	"""
	# episode is closed: should always work
	if not episode['episode_open']:
		episode['pk_health_issue'] = target_issue['pk_health_issue']
		if save_to_backend:
			episode.save_payload()
		return True

	# un-associate: should always work, too
	if target_issue is None:
		episode['pk_health_issue'] = None
		if save_to_backend:
			episode.save_payload()
		return True

	# try closing possibly expired episode on target issue if any
	db_cfg = gmCfg.cCfgSQL()
	epi_ttl = int(db_cfg.get2 (
		option = u'episode.ttl',
		workplace = gmSurgery.gmCurrentPractice().active_workplace,
		bias = 'user',
		default = 60				# 2 months
	))
	if target_issue.close_expired_episode(ttl=epi_ttl) is True:
		gmDispatcher.send(signal='statustext', msg=_('Closed episodes older than %s days on health issue [%s]') % (epi_ttl, target_issue['description']))
	existing_epi = target_issue.get_open_episode()

	# no more open episode on target issue: should work now
	if existing_epi is None:
		episode['pk_health_issue'] = target_issue['pk_health_issue']
		if save_to_backend:
			episode.save_payload()
		return True

	# don't conflict on SELF ;-)
	if existing_epi['pk_episode'] == episode['pk_episode']:
		episode['pk_health_issue'] = target_issue['pk_health_issue']
		if save_to_backend:
			episode.save_payload()
		return True

	# we got two open episodes at once, ask user
	move_range = episode.get_access_range()
	exist_range = existing_epi.get_access_range()
	question = _(
		'You want to associate the running episode:\n\n'
		' "%(new_epi_name)s" (%(new_epi_start)s - %(new_epi_end)s)\n\n'
		'with the health issue:\n\n'
		' "%(issue_name)s"\n\n'
		'There already is another episode running\n'
		'for this health issue:\n\n'
		' "%(old_epi_name)s" (%(old_epi_start)s - %(old_epi_end)s)\n\n'
		'However, there can only be one running\n'
		'episode per health issue.\n\n'
		'Which episode do you want to close ?'
	) % {
		'new_epi_name': episode['description'],
		'new_epi_start': move_range[0].strftime('%m/%y'),
		'new_epi_end': move_range[1].strftime('%m/%y'),
		'issue_name': target_issue['description'],
		'old_epi_name': existing_epi['description'],
		'old_epi_start': exist_range[0].strftime('%m/%y'),
		'old_epi_end': exist_range[1].strftime('%m/%y')
	}
	dlg = gmGuiHelpers.c3ButtonQuestionDlg (
		parent = None,
		id = -1,
		caption = _('Resolving two-running-episodes conflict'),
		question = question,
		button_defs = [
			{'label': _('old episode'), 'default': True, 'tooltip': _('close existing episode "%s"') % existing_epi['description']},
			{'label': _('new episode'), 'default': False, 'tooltip': _('close moving (new) episode "%s"') % episode['description']}
		]
	)
	decision = dlg.ShowModal()

	if decision == wx.ID_CANCEL:
		# button 3: move cancelled by user
		return False

	elif decision == wx.ID_YES:
		# button 1: close old episode
		existing_epi['episode_open'] = False
		existing_epi.save_payload()

	elif decision == wx.ID_NO:
		# button 2: close new episode
		episode['episode_open'] = False

	else:
		raise ValueError('invalid result from c3ButtonQuestionDlg: [%s]' % decision)

	episode['pk_health_issue'] = target_issue['pk_health_issue']
	if save_to_backend:
		episode.save_payload()
	return True
#----------------------------------------------------------------
class cEpisodeListSelectorDlg(gmListWidgets.cGenericListSelectorDlg):

	# FIXME: support pre-selection

	def __init__(self, *args, **kwargs):

		episodes = kwargs['episodes']
		del kwargs['episodes']

		gmListWidgets.cGenericListSelectorDlg.__init__(self, *args, **kwargs)

		self.SetTitle(_('Select the episodes you are interested in ...'))
		self._LCTRL_items.set_columns([_('Episode'), _('Status'), _('Health Issue')])
		self._LCTRL_items.set_string_items (
			items = [ 
				[	epi['description'], 
					gmTools.bool2str(epi['episode_open'], _('ongoing'), u''), 
					gmTools.coalesce(epi['health_issue'], u'')
				]
				for epi in episodes ]
		)
		self._LCTRL_items.set_column_widths()
		self._LCTRL_items.set_data(data = episodes)
#----------------------------------------------------------------
class cEpisodeDescriptionPhraseWheel(gmPhraseWheel.cPhraseWheel):
	"""Let user select an episode *description*.

	The user can select an episode description from the previously
	used descriptions across all episodes across all patients.

	Selection is done with a phrasewheel so the user can
	type the episode name and matches will be shown. Typing
	"*" will show the entire list of episodes.

	If the user types a description not existing yet a
	new episode description will be returned.
	"""
	def __init__(self, *args, **kwargs):

		mp = gmMatchProvider.cMatchProvider_SQL2 (
			queries = [u"""
				select distinct on (description) description, description, 1
				from clin.episode
				where description %(fragment_condition)s
				order by description
				limit 30"""
			]
		)
		gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)
		self.matcher = mp
#----------------------------------------------------------------
class cEpisodeSelectionPhraseWheel(gmPhraseWheel.cPhraseWheel):
	"""Let user select an episode.

	The user can select an episode from the existing episodes of a
	patient. Selection is done with a phrasewheel so the user
	can type the episode name and matches will be shown. Typing
	"*" will show the entire list of episodes. Closed episodes
	will be marked as such. If the user types an episode name not
	in the list of existing episodes a new episode can be created
	from it if the programmer activated that feature.

	If keyword <patient_id> is set to None or left out the control
	will listen to patient change signals and therefore act on
	gmPerson.gmCurrentPatient() changes.
	"""
	def __init__(self, *args, **kwargs):

		ctxt = {'ctxt_pat': {'where_part': u'and pk_patient = %(pat)s', 'placeholder': u'pat'}}

		mp = gmMatchProvider.cMatchProvider_SQL2 (
			queries = [
u"""(

select
	pk_episode,
	coalesce (
		description || ' - ' || health_issue,
		description
	) as description,
	1 as rank
from
  	clin.v_pat_episodes
where
	episode_open is true and
	description %(fragment_condition)s
	%(ctxt_pat)s

) union all (

select
	pk_episode,
	coalesce (
		description || _(' (closed)') || ' - ' || health_issue,
		description || _(' (closed)')
	) as description,
	2 as rank
from
	clin.v_pat_episodes
where
	description %(fragment_condition)s and
	episode_open is false
	%(ctxt_pat)s

)
order by rank, description
limit 30"""
],
			context = ctxt
		)

		try:
			kwargs['patient_id']
		except KeyError:
			kwargs['patient_id'] = None

		if kwargs['patient_id'] is None:
			self.use_current_patient = True
			self.__register_patient_change_signals()
			pat = gmPerson.gmCurrentPatient()
			if pat.connected:
				mp.set_context('pat', pat.ID)
		else:
			self.use_current_patient = False
			self.__patient_id = int(kwargs['patient_id'])
			mp.set_context('pat', self.__patient_id)

		del kwargs['patient_id']

		gmPhraseWheel.cPhraseWheel.__init__ (
			self,
			*args,
			**kwargs
		)
		self.matcher = mp
	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def set_patient(self, patient_id=None):
		if self.use_current_patient:
			return False
		self.__patient_id = int(patient_id)
		self.set_context('pat', self.__patient_id)
		return True
	#--------------------------------------------------------
	def GetData(self, can_create=False, as_instance=False, is_open=False):
		self.__is_open_for_create_data = is_open		# used (only) in _create_data()
		gmPhraseWheel.cPhraseWheel.GetData(self, can_create = can_create, as_instance = as_instance)
		return self.data
	#--------------------------------------------------------
	def _create_data(self):

		epi_name = self.GetValue().strip()
		if epi_name == u'':
			gmDispatcher.send(signal = u'statustext', msg = _('Cannot create episode without name.'), beep = True)
			_log.debug('cannot create episode without name')
			return

		if self.use_current_patient:
			pat = gmPerson.gmCurrentPatient()
		else:
			pat = gmPerson.cPatient(aPK_obj = self.__patient_id)

		emr = pat.get_emr()
		epi = emr.add_episode(episode_name = epi_name, is_open = self.__is_open_for_create_data)
		if epi is None:
			self.data = None
		else:
			self.data = epi['pk_episode']
	#--------------------------------------------------------
	def _data2instance(self):
		return gmEMRStructItems.cEpisode(aPK_obj = self.data)
	#--------------------------------------------------------
	# internal API
	#--------------------------------------------------------
	def __register_patient_change_signals(self):
		gmDispatcher.connect(self._pre_patient_selection, u'pre_patient_selection')
		gmDispatcher.connect(self._post_patient_selection, u'post_patient_selection')
	#--------------------------------------------------------
	def _pre_patient_selection(self):
		return True
	#--------------------------------------------------------
	def _post_patient_selection(self):
		if self.use_current_patient:
			patient = gmPerson.gmCurrentPatient()
			self.set_context('pat', patient.ID)
		return True
#----------------------------------------------------------------
from Gnumed.wxGladeWidgets import wxgEpisodeEditAreaPnl

class cEpisodeEditAreaPnl(gmEditArea.cGenericEditAreaMixin, wxgEpisodeEditAreaPnl.wxgEpisodeEditAreaPnl):

	def __init__(self, *args, **kwargs):

		try:
			episode = kwargs['episode']
			del kwargs['episode']
		except KeyError:
			episode = None

		wxgEpisodeEditAreaPnl.wxgEpisodeEditAreaPnl.__init__(self, *args, **kwargs)
		gmEditArea.cGenericEditAreaMixin.__init__(self)

		self.data = episode
	#----------------------------------------------------------------
	# generic Edit Area mixin API
	#----------------------------------------------------------------
	def _valid_for_save(self):

		errors = False

		if len(self._PRW_description.GetValue().strip()) == 0:
			errors = True
			self._PRW_description.display_as_valid(False)
			self._PRW_description.SetFocus()
		else:
			self._PRW_description.display_as_valid(True)
		self._PRW_description.Refresh()

		return not errors
	#----------------------------------------------------------------
	def _save_as_new(self):

		pat = gmPerson.gmCurrentPatient()
		emr = pat.get_emr()

		epi = emr.add_episode(episode_name = self._PRW_description.GetValue().strip())
		epi['summary'] = self._TCTRL_summary.GetValue().strip()
		epi['episode_open'] = not self._CHBOX_closed.IsChecked()
		epi['diagnostic_certainty_classification'] = self._PRW_classification.GetData()

		issue_name = self._PRW_issue.GetValue().strip()
		if len(issue_name) != 0:
			epi['pk_health_issue'] = self._PRW_issue.GetData(can_create = True)
			issue = gmEMRStructItems.cHealthIssue(aPK_obj = epi['pk_health_issue'])

			if not move_episode_to_issue(episode = epi, target_issue = issue, save_to_backend = False):
				gmDispatcher.send (
					signal = 'statustext',
					msg = _('Cannot attach episode [%s] to health issue [%s] because it already has a running episode.') % (
						epi['description'],
						issue['description']
					)
				)
				gmEMRStructItems.delete_episode(episode = epi)
				return False

		epi.save()

		self.data = epi
		return True
	#----------------------------------------------------------------
	def _save_as_update(self):

		self.data['description'] = self._PRW_description.GetValue().strip()
		self.data['summary'] = self._TCTRL_summary.GetValue().strip()
		self.data['episode_open'] = not self._CHBOX_closed.IsChecked()
		self.data['diagnostic_certainty_classification'] = self._PRW_classification.GetData()

		issue_name = self._PRW_issue.GetValue().strip()
		if len(issue_name) != 0:
			self.data['pk_health_issue'] = self._PRW_issue.GetData(can_create = True)
			issue = gmEMRStructItems.cHealthIssue(aPK_obj = self.data['pk_health_issue'])

			if not move_episode_to_issue(episode = self.data, target_issue = issue, save_to_backend = False):
				gmDispatcher.send (
					signal = 'statustext',
					msg = _('Cannot attach episode [%s] to health issue [%s] because it already has a running episode.') % (
						self.data['description'],
						issue['description']
					)
				)
				return False

		self.data.save()
		return True
	#----------------------------------------------------------------
	def _refresh_as_new(self):
		if self.data is None:
			ident = gmPerson.gmCurrentPatient()
		else:
			ident = gmPerson.cIdentity(aPK_obj = self.data['pk_patient'])
		self._TCTRL_patient.SetValue(ident.get_description_gender())
		self._PRW_issue.SetText()
		self._PRW_description.SetText()
		self._TCTRL_summary.SetValue(u'')
		self._PRW_classification.SetText()
		self._CHBOX_closed.SetValue(False)
	#----------------------------------------------------------------
	def _refresh_from_existing(self):
		ident = gmPerson.cIdentity(aPK_obj = self.data['pk_patient'])
		self._TCTRL_patient.SetValue(ident.get_description_gender())

		if self.data['pk_health_issue'] is not None:
			self._PRW_issue.SetText(self.data['health_issue'], data=self.data['pk_health_issue'])

		self._PRW_description.SetText(self.data['description'], data=self.data['description'])

		self._TCTRL_summary.SetValue(gmTools.coalesce(self.data['summary'], u''))

		if self.data['diagnostic_certainty_classification'] is not None:
			self._PRW_classification.SetData(data = self.data['diagnostic_certainty_classification'])

		self._CHBOX_closed.SetValue(not self.data['episode_open'])
	#----------------------------------------------------------------
	def _refresh_as_new_from_existing(self):
		self._refresh_as_new()
#================================================================
# health issue related widgets/functions
#----------------------------------------------------------------
def edit_health_issue(parent=None, issue=None):
	ea = cHealthIssueEditAreaPnl(parent = parent, id = -1)
	ea.data = issue
	ea.mode = gmTools.coalesce(issue, 'new', 'edit')
	dlg = gmEditArea.cGenericEditAreaDlg2(parent = parent, id = -1, edit_area = ea, single_entry = (issue is not None))
	dlg.SetTitle(gmTools.coalesce(issue, _('Adding a new health issue'), _('Editing a health issue')))
	if dlg.ShowModal() == wx.ID_OK:
		return True
	return False
#----------------------------------------------------------------
class cIssueListSelectorDlg(gmListWidgets.cGenericListSelectorDlg):

	# FIXME: support pre-selection

	def __init__(self, *args, **kwargs):

		issues = kwargs['issues']
		del kwargs['issues']

		gmListWidgets.cGenericListSelectorDlg.__init__(self, *args, **kwargs)

		self.SetTitle(_('Select the health issues you are interested in ...'))
		self._LCTRL_items.set_columns([u'', _('Health Issue'), u'', u'', u''])

		for issue in issues:
			if issue['is_confidential']:
				row_num = self._LCTRL_items.InsertStringItem(sys.maxint, label = _('confidential'))
				self._LCTRL_items.SetItemTextColour(row_num, col=wx.NamedColour('RED'))
			else:
				row_num = self._LCTRL_items.InsertStringItem(sys.maxint, label = u'')

			self._LCTRL_items.SetStringItem(index = row_num, col = 1, label = issue['description'])
			if issue['clinically_relevant']:
				self._LCTRL_items.SetStringItem(index = row_num, col = 2, label = _('relevant'))
			if issue['is_active']:
				self._LCTRL_items.SetStringItem(index = row_num, col = 3, label = _('active'))
			if issue['is_cause_of_death']:
				self._LCTRL_items.SetStringItem(index = row_num, col = 4, label = _('fatal'))

		self._LCTRL_items.set_column_widths()
		self._LCTRL_items.set_data(data = issues)
#----------------------------------------------------------------
class cIssueSelectionPhraseWheel(gmPhraseWheel.cPhraseWheel):
	"""Let the user select a health issue.

	The user can select a health issue from the existing issues
	of a patient. Selection is done with a phrasewheel so the user
	can type the issue name and matches will be shown. Typing
	"*" will show the entire list of issues. Inactive issues
	will be marked as such. If the user types an issue name not
	in the list of existing issues a new issue can be created
	from it if the programmer activated that feature.

	If keyword <patient_id> is set to None or left out the control
	will listen to patient change signals and therefore act on
	gmPerson.gmCurrentPatient() changes.
	"""
	def __init__(self, *args, **kwargs):

		ctxt = {'ctxt_pat': {'where_part': u'pk_patient=%(pat)s', 'placeholder': u'pat'}}

		mp = gmMatchProvider.cMatchProvider_SQL2 (
			# FIXME: consider clin.health_issue.clinically_relevant
			queries = [u"""
(select pk_health_issue, description, 1
	from clin.v_health_issues where
		is_active is true and
		description %(fragment_condition)s and
		%(ctxt_pat)s
	order by description)

union

(select pk_health_issue, description || _(' (inactive)'), 2
	from clin.v_health_issues where
		is_active is false and
		description %(fragment_condition)s and
		%(ctxt_pat)s
	order by description)"""
			],
			context = ctxt
		)

		try: kwargs['patient_id']
		except KeyError: kwargs['patient_id'] = None

		if kwargs['patient_id'] is None:
			self.use_current_patient = True
			self.__register_patient_change_signals()
			pat = gmPerson.gmCurrentPatient()
			if pat.connected:
				mp.set_context('pat', pat.ID)
		else:
			self.use_current_patient = False
			self.__patient_id = int(kwargs['patient_id'])
			mp.set_context('pat', self.__patient_id)

		del kwargs['patient_id']

		gmPhraseWheel.cPhraseWheel.__init__ (
			self,
			*args,
			**kwargs
		)
		self.matcher = mp
	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def set_patient(self, patient_id=None):
		if self.use_current_patient:
			return False
		self.__patient_id = int(patient_id)
		self.set_context('pat', self.__patient_id)
		return True
	#--------------------------------------------------------
	def GetData(self, can_create=False, is_open=False):
		if self.data is None:
			if can_create:
				issue_name = self.GetValue().strip()

				if self.use_current_patient:
					pat = gmPerson.gmCurrentPatient()
				else:
					pat = gmPerson.cPatient(aPK_obj=self.__patient_id)
				emr = pat.get_emr()

				issue = emr.add_health_issue(issue_name = issue_name)
				if issue is None:
					self.data = None
				else:
					self.data = issue['pk_health_issue']

		return gmPhraseWheel.cPhraseWheel.GetData(self)
	#--------------------------------------------------------
	# internal API
	#--------------------------------------------------------
	def __register_patient_change_signals(self):
		gmDispatcher.connect(self._pre_patient_selection, u'pre_patient_selection')
		gmDispatcher.connect(self._post_patient_selection, u'post_patient_selection')
	#--------------------------------------------------------
	def _pre_patient_selection(self):
		return True
	#--------------------------------------------------------
	def _post_patient_selection(self):
		if self.use_current_patient:
			patient = gmPerson.gmCurrentPatient()
			self.set_context('pat', patient.ID)
		return True
#------------------------------------------------------------
class cIssueSelectionDlg(wxgIssueSelectionDlg.wxgIssueSelectionDlg):

	def __init__(self, *args, **kwargs):
		try:
			msg = kwargs['message']
		except KeyError:
			msg = None
		del kwargs['message']
		wxgIssueSelectionDlg.wxgIssueSelectionDlg.__init__(self, *args, **kwargs)
		if msg is not None:
			self._lbl_message.SetLabel(label=msg)
	#--------------------------------------------------------
	def _on_OK_button_pressed(self, event):
		event.Skip()
		pk_issue = self._PhWheel_issue.GetData(can_create=True)
		if pk_issue is None:
			gmGuiHelpers.gm_show_error (
				_('Cannot create new health issue:\n [%(issue)s]') % {'issue': self._PhWheel_issue.GetValue().strip()},
				_('Selecting health issue')
			)
			return False
		return True
#------------------------------------------------------------
from Gnumed.wxGladeWidgets import wxgHealthIssueEditAreaPnl

class cHealthIssueEditAreaPnl(gmEditArea.cGenericEditAreaMixin, wxgHealthIssueEditAreaPnl.wxgHealthIssueEditAreaPnl):
	"""Panel encapsulating health issue edit area functionality."""

	def __init__(self, *args, **kwargs):

		try:
			issue = kwargs['issue']
		except KeyError:
			 issue = None

		wxgHealthIssueEditAreaPnl.wxgHealthIssueEditAreaPnl.__init__(self, *args, **kwargs)

		gmEditArea.cGenericEditAreaMixin.__init__(self)

		# FIXME: include more sources: coding systems/other database columns
		mp = gmMatchProvider.cMatchProvider_SQL2 (
			queries = [u"SELECT DISTINCT ON (description) description, description FROM clin.health_issue WHERE description %(fragment_condition)s LIMIT 50"]
		)
		mp.setThresholds(1, 3, 5)
		self._PRW_condition.matcher = mp

		mp = gmMatchProvider.cMatchProvider_SQL2 (
			queries = [u"""
select distinct on (grouping) grouping, grouping from (

	select rank, grouping from ((

		select
			grouping,
			1 as rank
		from
			clin.health_issue
		where
			grouping %%(fragment_condition)s
				and
			(select True from clin.encounter where fk_patient = %s and pk = clin.health_issue.fk_encounter)

	) union (

		select
			grouping,
			2 as rank
		from
			clin.health_issue
		where
			grouping %%(fragment_condition)s

	)) as union_result

	order by rank

) as order_result

limit 50""" % gmPerson.gmCurrentPatient().ID
			]
		)
		mp.setThresholds(1, 3, 5)
		self._PRW_grouping.matcher = mp

		self._PRW_age_noted.add_callback_on_lose_focus(self._on_leave_age_noted)
		self._PRW_year_noted.add_callback_on_lose_focus(self._on_leave_year_noted)

		self._PRW_age_noted.add_callback_on_modified(self._on_modified_age_noted)
		self._PRW_year_noted.add_callback_on_modified(self._on_modified_year_noted)

		self._PRW_year_noted.Enable(True)

		self.data = issue
	#----------------------------------------------------------------
	# generic Edit Area mixin API
	#----------------------------------------------------------------
	def _valid_for_save(self):

		if self._PRW_condition.GetValue().strip() == '':
			self._PRW_condition.display_as_valid(False)
			self._PRW_condition.SetFocus()
			return False
		self._PRW_condition.display_as_valid(True)
		self._PRW_condition.Refresh()

		# FIXME: sanity check age/year diagnosed
		age_noted = self._PRW_age_noted.GetValue().strip()
		if age_noted != '':
			if gmDateTime.str2interval(str_interval = age_noted) is None:
				self._PRW_age_noted.display_as_valid(False)
				self._PRW_age_noted.SetFocus()
				return False
		self._PRW_age_noted.display_as_valid(True)

		return True
	#----------------------------------------------------------------
	def _save_as_new(self):
		pat = gmPerson.gmCurrentPatient()
		emr = pat.get_emr()

		issue = emr.add_health_issue(issue_name = self._PRW_condition.GetValue().strip())

		side = u''
		if self._ChBOX_left.GetValue():
			side += u's'
		if self._ChBOX_right.GetValue():
			side += u'd'
		issue['laterality'] = side

		issue['summary'] = self._TCTRL_summary.GetValue().strip()
		issue['diagnostic_certainty_classification'] = self._PRW_classification.GetData()
		issue['grouping'] = self._PRW_grouping.GetValue().strip()
		issue['is_active'] = self._ChBOX_active.GetValue()
		issue['clinically_relevant'] = self._ChBOX_relevant.GetValue()
		issue['is_confidential'] = self._ChBOX_confidential.GetValue()
		issue['is_cause_of_death'] = self._ChBOX_caused_death.GetValue()

		age_noted = self._PRW_age_noted.GetData()
		if age_noted is not None:
			issue['age_noted'] = age_noted

		issue.save()

		self.data = issue
		return True
	#----------------------------------------------------------------
	def _save_as_update(self):

		self.data['description'] = self._PRW_condition.GetValue().strip()

		side = u''
		if self._ChBOX_left.GetValue():
			side += u's'
		if self._ChBOX_right.GetValue():
			side += u'd'
		self.data['laterality'] = side

		self.data['summary'] = self._TCTRL_summary.GetValue().strip()
		self.data['diagnostic_certainty_classification'] = self._PRW_classification.GetData()
		self.data['grouping'] = self._PRW_grouping.GetValue().strip()
		self.data['is_active'] = bool(self._ChBOX_active.GetValue())
		self.data['clinically_relevant'] = bool(self._ChBOX_relevant.GetValue())
		self.data['is_confidential'] = bool(self._ChBOX_confidential.GetValue())
		self.data['is_cause_of_death'] = bool(self._ChBOX_caused_death.GetValue())

		age_noted = self._PRW_age_noted.GetData()
		if age_noted is not None:
			self.data['age_noted'] = age_noted

		self.data.save()

		# FIXME: handle is_operation
		return True
	#----------------------------------------------------------------
	def _refresh_as_new(self):
		self._PRW_condition.SetText()
		self._ChBOX_left.SetValue(0)
		self._ChBOX_right.SetValue(0)
		self._PRW_classification.SetText()
		self._PRW_grouping.SetText()
		self._TCTRL_summary.SetValue(u'')
		self._PRW_age_noted.SetText()
		self._PRW_year_noted.SetText()
		self._ChBOX_active.SetValue(0)
		self._ChBOX_relevant.SetValue(1)
		self._ChBOX_is_operation.SetValue(0)
		self._ChBOX_confidential.SetValue(0)
		self._ChBOX_caused_death.SetValue(0)

		return True
	#----------------------------------------------------------------
	def _refresh_from_existing(self):
		self._PRW_condition.SetText(self.data['description'])

		lat = gmTools.coalesce(self.data['laterality'], '')
		if lat.find('s') == -1:
			self._ChBOX_left.SetValue(0)
		else:
			self._ChBOX_left.SetValue(1)
		if lat.find('d') == -1:
			self._ChBOX_right.SetValue(0)
		else:
			self._ChBOX_right.SetValue(1)

		self._PRW_classification.SetData(data = self.data['diagnostic_certainty_classification'])
		self._PRW_grouping.SetText(gmTools.coalesce(self.data['grouping'], u''))
		self._TCTRL_summary.SetValue(gmTools.coalesce(self.data['summary'], u''))

		if self.data['age_noted'] is None:
			self._PRW_age_noted.SetText()
		else:
			self._PRW_age_noted.SetText (
				value = '%sd' % self.data['age_noted'].days,
				data = self.data['age_noted']
			)

		self._ChBOX_active.SetValue(self.data['is_active'])
		self._ChBOX_relevant.SetValue(self.data['clinically_relevant'])
		self._ChBOX_is_operation.SetValue(0)		# FIXME
		self._ChBOX_confidential.SetValue(self.data['is_confidential'])
		self._ChBOX_caused_death.SetValue(self.data['is_cause_of_death'])

		# this dance should assure self._PRW_year_noted gets set -- but it doesn't ...
#		self._PRW_age_noted.SetFocus()
#		self._PRW_condition.SetFocus()

		return True
	#----------------------------------------------------------------
	def _refresh_as_new_from_existing(self):
		return self._refresh_as_new()
	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def _on_leave_age_noted(self, *args, **kwargs):

		if not self._PRW_age_noted.IsModified():
			return True

		str_age = self._PRW_age_noted.GetValue().strip()

		if str_age == u'':
			wx.CallAfter(self._PRW_year_noted.SetText, u'', None, True)
			return True

		age = gmDateTime.str2interval(str_interval = str_age)

		if age is None:
			gmDispatcher.send(signal='statustext', msg=_('Cannot parse [%s] into valid interval.') % str_age)
			self._PRW_age_noted.SetBackgroundColour('pink')
			self._PRW_age_noted.Refresh()
			wx.CallAfter(self._PRW_year_noted.SetText, u'', None, True)
			return True

		pat = gmPerson.gmCurrentPatient()
		if pat['dob'] is not None:
			max_age = pydt.datetime.now(tz=pat['dob'].tzinfo) - pat['dob']

			if age >= max_age:
				gmDispatcher.send (
					signal = 'statustext',
					msg = _(
						'Health issue cannot have been noted at age %s. Patient is only %s old.'
					) % (age, pat.get_medical_age())
				)
				self._PRW_age_noted.SetBackgroundColour('pink')
				self._PRW_age_noted.Refresh()
				wx.CallAfter(self._PRW_year_noted.SetText, u'', None, True)
				return True

		self._PRW_age_noted.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
		self._PRW_age_noted.Refresh()
		self._PRW_age_noted.SetData(data=age)

		if pat['dob'] is not None:
			fts = gmDateTime.cFuzzyTimestamp (
				timestamp = pat['dob'] + age,
				accuracy = gmDateTime.acc_months
			)
			wx.CallAfter(self._PRW_year_noted.SetText, str(fts), fts)
			# if we do this we will *always* navigate there, regardless of TAB vs ALT-TAB
			#wx.CallAfter(self._ChBOX_active.SetFocus)
			# if we do the following instead it will take us to the save/update button ...
			#wx.CallAfter(self.Navigate)

		return True
	#--------------------------------------------------------
	def _on_leave_year_noted(self, *args, **kwargs):

		if not self._PRW_year_noted.IsModified():
			return True

		year_noted = self._PRW_year_noted.GetData()

		if year_noted is None:
			if self._PRW_year_noted.GetValue().strip() == u'':
				wx.CallAfter(self._PRW_age_noted.SetText, u'', None, True)
				return True
			self._PRW_year_noted.SetBackgroundColour('pink')
			self._PRW_year_noted.Refresh()
			wx.CallAfter(self._PRW_age_noted.SetText, u'', None, True)
			return True

		year_noted = year_noted.get_pydt()

		if year_noted >= pydt.datetime.now(tz=year_noted.tzinfo):
			gmDispatcher.send(signal='statustext', msg=_('Condition diagnosed in the future.'))
			self._PRW_year_noted.SetBackgroundColour('pink')
			self._PRW_year_noted.Refresh()
			wx.CallAfter(self._PRW_age_noted.SetText, u'', None, True)
			return True

		self._PRW_year_noted.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
		self._PRW_year_noted.Refresh()

		pat = gmPerson.gmCurrentPatient()
		if pat['dob'] is not None:
			issue_age = year_noted - pat['dob']
			str_age = gmDateTime.format_interval_medically(interval = issue_age)
			wx.CallAfter(self._PRW_age_noted.SetText, str_age, issue_age)

		return True
	#--------------------------------------------------------
	def _on_modified_age_noted(self, *args, **kwargs):
		wx.CallAfter(self._PRW_year_noted.SetText, u'', None, True)
		return True
	#--------------------------------------------------------
	def _on_modified_year_noted(self, *args, **kwargs):
		wx.CallAfter(self._PRW_age_noted.SetText, u'', None, True)
		return True
#================================================================
# diagnostic certainty related widgets/functions
#----------------------------------------------------------------
class cDiagnosticCertaintyClassificationPhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):

		gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)

		self.selection_only = False			# can be NULL, too

		mp = gmMatchProvider.cMatchProvider_FixedList (
			aSeq = [
				{'data': u'A', 'label': gmEMRStructItems.diagnostic_certainty_classification2str(u'A'), 'weight': 1},
				{'data': u'B', 'label': gmEMRStructItems.diagnostic_certainty_classification2str(u'B'), 'weight': 1},
				{'data': u'C', 'label': gmEMRStructItems.diagnostic_certainty_classification2str(u'C'), 'weight': 1},
				{'data': u'D', 'label': gmEMRStructItems.diagnostic_certainty_classification2str(u'D'), 'weight': 1}
			]
		)
		mp.setThresholds(1, 2, 4)
		self.matcher = mp

		self.SetToolTipString(_(
			"The diagnostic classification or grading of this assessment.\n"
			"\n"
			"This documents how certain one is about this being a true diagnosis."
		))
#================================================================
# MAIN
#----------------------------------------------------------------
if __name__ == '__main__':

	#================================================================	
	class testapp (wx.App):
			"""
			Test application for testing EMR struct widgets
			"""			
			#--------------------------------------------------------
			def OnInit (self):
				"""
				Create test application UI
				"""
				frame = wx.Frame (
							None,
							-4,
							'Testing EMR struct widgets',
							size=wx.Size(600, 400),
							style=wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE
						)
				filemenu= wx.Menu()
				filemenu.AppendSeparator()
				filemenu.Append(ID_EXIT,"E&xit"," Terminate test application")

				# Creating the menubar.	
				menuBar = wx.MenuBar()
				menuBar.Append(filemenu,"&File")

				frame.SetMenuBar(menuBar)

				txt = wx.StaticText( frame, -1, _("Select desired test option from the 'File' menu"),
				wx.DefaultPosition, wx.DefaultSize, 0 )

				# event handlers
				wx.EVT_MENU(frame, ID_EXIT, self.OnCloseWindow)

				# patient EMR
				self.__pat = gmPerson.gmCurrentPatient()

				frame.Show(1)
				return 1
			#--------------------------------------------------------
			def OnCloseWindow (self, e):
				"""
				Close test aplication
				"""
				self.ExitMainLoop ()
	#----------------------------------------------------------------
	def test_encounter_edit_area_panel():
		app = wx.PyWidgetTester(size = (200, 300))
		emr = pat.get_emr()
		enc = emr.active_encounter
		#enc = gmEMRStructItems.cEncounter(1)
		pnl = cEncounterEditAreaPnl(app.frame, -1, encounter=enc)
		app.frame.Show(True)
		app.MainLoop()
		return
	#----------------------------------------------------------------
	def test_encounter_edit_area_dialog():
		app = wx.PyWidgetTester(size = (200, 300))
		emr = pat.get_emr()
		enc = emr.active_encounter
		#enc = gmEMRStructItems.cEncounter(1)

		dlg = cEncounterEditAreaDlg(parent=app.frame, id=-1, size = (400,400), encounter=enc)
		dlg.ShowModal()

#		pnl = cEncounterEditAreaDlg(app.frame, -1, encounter=enc)
#		app.frame.Show(True)
#		app.MainLoop()
	#----------------------------------------------------------------
	def test_epsiode_edit_area_pnl():
		app = wx.PyWidgetTester(size = (200, 300))
		emr = pat.get_emr()
		epi = emr.get_episodes()[0]
		pnl = cEpisodeEditAreaPnl(app.frame, -1, episode=epi)
		app.frame.Show(True)
		app.MainLoop()
	#----------------------------------------------------------------
	def test_episode_edit_area_dialog():
		app = wx.PyWidgetTester(size = (200, 300))
		emr = pat.get_emr()
		epi = emr.get_episodes()[0]
		edit_episode(parent=app.frame, episode=epi)
	#----------------------------------------------------------------
	def test_hospital_stay_prw():
		app = wx.PyWidgetTester(size = (400, 40))
		app.SetWidget(cHospitalStayPhraseWheel, id=-1, size=(180,20), pos=(10,20))
		app.MainLoop()
	#----------------------------------------------------------------
	def test_episode_selection_prw():
		app = wx.PyWidgetTester(size = (400, 40))
		app.SetWidget(cEpisodeSelectionPhraseWheel, id=-1, size=(180,20), pos=(10,20))
#		app.SetWidget(cEpisodeSelectionPhraseWheel, id=-1, size=(350,20), pos=(10,20), patient_id=pat.ID)
		app.MainLoop()
	#----------------------------------------------------------------
	def test_health_issue_edit_area_dlg():
		app = wx.PyWidgetTester(size = (200, 300))
		edit_health_issue(parent=app.frame, issue=None)
	#----------------------------------------------------------------
	def test_health_issue_edit_area_pnl():
		app = wx.PyWidgetTester(size = (200, 300))
		app.SetWidget(cHealthIssueEditAreaPnl, id=-1, size = (400,400))
		app.MainLoop()
	#----------------------------------------------------------------
	def test_edit_procedure():
		app = wx.PyWidgetTester(size = (200, 300))
		edit_procedure(parent=app.frame)
	#================================================================

	if (len(sys.argv) > 1) and (sys.argv[1] == 'test'):

		gmI18N.activate_locale()
		gmI18N.install_domain()
		gmDateTime.init()

		# obtain patient
		pat = gmPersonSearch.ask_for_patient()
		if pat is None:
			print "No patient. Exiting gracefully..."
			sys.exit(0)
		gmPatSearchWidgets.set_active_patient(patient=pat)

#	try:
		# lauch emr dialogs test application
#		app = testapp(0)
#		app.MainLoop()
#	except StandardError:
#		_log.exception("unhandled exception caught !")
		# but re-raise them
#		raise

		#test_encounter_edit_area_panel()
		#test_encounter_edit_area_dialog()
		#test_epsiode_edit_area_pnl()
		#test_episode_edit_area_dialog()
		#test_health_issue_edit_area_dlg()
		#test_episode_selection_prw()
		#test_hospital_stay_prw()
		test_edit_procedure()

#================================================================
