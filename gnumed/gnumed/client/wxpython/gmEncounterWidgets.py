"""GNUmed encounter related widgets.

This module contains widgets to manage encounters."""
#================================================================
__author__ = "cfmoro1976@yahoo.es, karsten.hilbert@gmx.net"
__license__ = "GPL v2 or later"

# stdlib
import sys
import time
import logging
import datetime as pydt


# 3rd party
import wx


# GNUmed
if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x
from Gnumed.pycommon import gmCfgDB
from Gnumed.pycommon import gmDateTime
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmDispatcher
from Gnumed.pycommon import gmMatchProvider

from Gnumed.business import gmEncounter
from Gnumed.business import gmPraxis
from Gnumed.business import gmPerson
from Gnumed.business import gmStaff

from Gnumed.wxpython import gmPhraseWheel
from Gnumed.wxpython import gmGuiHelpers
from Gnumed.wxpython import gmListWidgets
from Gnumed.wxpython import gmEditArea


_log = logging.getLogger('gm.ui')

#================================================================
# encounter related widgets/functions
#----------------------------------------------------------------
def _ask_for_encounter_continuation(new_encounter=None, fairly_recent_encounter=None):
	"""This is used as the callback when the EMR detects that the
	   patient was here rather recently and wants to ask the
	   provider whether to continue the recent encounter.
	"""
	# better safe than sorry
	if new_encounter['pk_patient'] != fairly_recent_encounter['pk_patient']:
		raise ValueError('pk_patient values on new (enc=%s pat=%s) and fairly-recent (enc=%s pat=%s) encounter do not match' % (
			new_encounter['pk_encounter'],
			new_encounter['pk_patient'],
			fairly_recent_encounter['pk_encounter'],
			fairly_recent_encounter['pk_patient']
		))

	# only pester user if current patient is concerned
	curr_pat = gmPerson.gmCurrentPatient()
	if new_encounter['pk_patient'] != curr_pat.ID:
		return

	# ask user
	msg = _(
		'%s, %s  [#%s]\n'
		'\n'
		"This patient's chart was worked on only recently:\n"
		'\n'
		' %s'
		'\n'
		'Do you want to continue that consultation ?\n'
		' (If not a new one will be used.)\n'
	) % (
		curr_pat.get_description_gender(with_nickname = False),
		curr_pat.get_formatted_dob('%Y %b %d'),
		curr_pat.ID,
		fairly_recent_encounter.format (
			episodes = None,
			with_soap = False,
			left_margin = 1,
			patient = None,
			issues = None,
			with_docs = False,
			with_tests = False,
			fancy_header = False,
			with_vaccinations = False,
			with_rfe_aoe = True,
			with_family_history = False,
			with_co_encountlet_hints = False,
			by_episode = False
		)
	)
	dlg = gmGuiHelpers.c2ButtonQuestionDlg (
		parent = None,
		id = -1,
		caption = _('Pulling chart'),
		question = msg,
		button_defs = [
			{'label': _('Continue recent'), 'tooltip': _('Continue the existing recent encounter.'), 'default': False},
			{'label': _('Start new'), 'tooltip': _('Start a new encounter. The existing one will be closed.'), 'default': True}
		],
		show_checkbox = False
	)
	result = dlg.ShowModal()
	dlg.DestroyLater()

	# switch encounters
	if result == wx.ID_YES:
		_log.info('user wants to continue fairly-recent encounter')
		curr_pat.emr.active_encounter = fairly_recent_encounter
		if new_encounter.transfer_all_data_to_another_encounter(pk_target_encounter = fairly_recent_encounter['pk_encounter']):
			if not gmEncounter.delete_encounter(pk_encounter = new_encounter['pk_encounter']):
				gmGuiHelpers.gm_show_info (
					_('Properly switched to fairly recent encounter but unable to delete newly-created encounter.'),
					_('Pulling chart')
				)
		else:
			gmGuiHelpers.gm_show_info (
				_('Unable to transfer the data from newly-created to fairly recent encounter.'),
				_('Pulling chart')
			)
		return

	_log.debug('stayed with newly created encounter')

#----------------------------------------------------------------
def __ask_for_encounter_continuation(**kwargs):
	try:
		del kwargs['signal']
		del kwargs['sender']
	except KeyError:
		pass
	wx.CallAfter(_ask_for_encounter_continuation, **kwargs)

#----------------------------------------------------------------
# listen for encounter continuation inquiry requests
gmDispatcher.connect(signal = 'ask_for_encounter_continuation', receiver = __ask_for_encounter_continuation)

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
def sanity_check_encounter_of_active_patient(parent=None, msg=None):

	# FIXME: should consult a centralized security provider
	# secretaries cannot edit encounters
	if gmStaff.gmCurrentProvider()['role'] == 'secretary':
		return True

	pat = gmPerson.gmCurrentPatient()
	if not pat.connected:
		return True

	check_enc = gmCfgDB.get4user (
		option = 'encounter.show_editor_before_patient_change',
		workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
		default = True					# True: if needed, not always unconditionally
	)

	if not check_enc:
		return True

	emr = pat.emr
	enc = emr.active_encounter
	# did we add anything to the EMR ?
	has_narr = enc.has_narrative()
	has_docs = enc.has_documents()
	if (not has_narr) and (not has_docs):
		return True

	empty_aoe = (gmTools.coalesce(enc['assessment_of_encounter'], '').strip() == '')
	zero_duration = (enc['last_affirmed'] == enc['started'])
	# all is well anyway
	if (not empty_aoe) and (not zero_duration):
		return True

	if zero_duration:
		enc['last_affirmed'] = pydt.datetime.now(tz = gmDateTime.gmCurrentLocalTimezone)
	# no narrative, presumably only import of docs and done
	if not has_narr:
		if empty_aoe:
			enc['assessment_of_encounter'] = _('only documents added')
		enc['pk_type'] = gmEncounter.get_encounter_type(description = 'chart review')[0]['pk']
		# "last_affirmed" should be latest modified_at of relevant docs but that's a lot more involved
		enc.save_payload()
		return True

	# does have narrative
	if empty_aoe:
		# - work out suitable default
		epis = emr.get_episodes_by_encounter()
		if len(epis) > 0:
			enc['assessment_of_encounter'] = '; '.join([ e['description'] for e in epis ])
	enc.save_payload()
	if msg is None:
		msg = _('Edit the encounter details of the active patient before moving on:')
	if parent is None:
		parent = wx.GetApp().GetTopWindow()
	_log.debug('sanity-check editing encounter [%s] for patient [%s]', enc['pk_encounter'], enc['pk_patient'])
	edit_encounter(parent = parent, encounter = enc, msg = msg)
	return True

#----------------------------------------------------------------
def edit_encounter(parent=None, encounter=None, msg=None, single_entry=False):
	if parent is None:
		parent = wx.GetApp().GetTopWindow()
	# FIXME: use generic dialog 2
	dlg = cEncounterEditAreaDlg(parent = parent, encounter = encounter, msg = msg)
	if dlg.ShowModal() == wx.ID_OK:
		dlg.DestroyLater()
		return True

	dlg.DestroyLater()
	return False

#----------------------------------------------------------------
def manage_encounters(**kwargs):
	return select_encounters(**kwargs)

def select_encounters(parent=None, patient=None, single_selection=True, encounters=None, ignore_OK_button=False):

	if patient is None:
		patient = gmPerson.gmCurrentPatient()

	if not patient.connected:
		gmDispatcher.send(signal = 'statustext', msg = _('Cannot list encounters. No active patient.'))
		return False

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	emr = patient.emr

	#--------------------
	def new():
		enc_type = gmCfgDB.get4user (
			option = 'encounter.default_type',
			workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace
		)
		if enc_type is None:
			enc_type = gmEncounter.get_most_commonly_used_encounter_type()
		if enc_type is None:
			enc_type = 'in surgery'
		enc = gmEncounter.create_encounter(fk_patient = patient.ID, enc_type = enc_type)
		saved = edit_encounter(parent = parent, encounter = enc)
		if saved:
			return True
		gmEncounter.delete_encounter(pk_encounter = enc['pk_encounter'])
		return False
	#--------------------
	def edit(enc=None):
		if enc is None:
			return False
		return edit_encounter(parent = parent, encounter = enc)
	#--------------------
	def edit_active(enc=None):
		return edit_encounter(parent = parent, encounter = emr.active_encounter)
	#--------------------
	def start_new(enc=None):
		start_new_encounter(emr = emr)
		return True
	#--------------------
	def delete(enc=None):
		if enc is None:
			return False
		question = _(
			'Really delete encounter [%s] ?\n'
			'\n'
			'Once deletion succeeds it cannot be undone.\n'
			'\n'
			'Note that it will only succeed if there\n'
			'is no data attached to the encounter.'
		) % enc['pk_encounter']
		delete_it = gmGuiHelpers.gm_show_question (
			question = question,
			title = _('Deleting encounter'),
			cancel_button = False
		)
		if not delete_it:
			return False
		if gmEncounter.delete_encounter(pk_encounter = enc['pk_encounter']):
			return True
		gmDispatcher.send (
			signal = 'statustext',
			msg = _('Cannot delete encounter [%s]. It is probably in use.') % enc['pk_encounter'],
			beep = True
		)
		return False
	#--------------------
	def get_tooltip(data):
		if data is None:
			return None
		return data.format (
			patient = patient,
			with_soap = False,
			with_docs = False,
			with_tests = False,
			with_vaccinations = False,
			with_rfe_aoe = True,
			with_family_history = False,
			by_episode=False,
			fancy_header = True,
		)
	#--------------------
	def refresh(lctrl):
		if encounters is None:
			encs = emr.get_encounters()
		else:
			encs = encounters

		items = [
			[
				'%s - %s' % (
					e['started'].strftime('%Y %b %d  %H:%M'),
					e['last_affirmed'].strftime('%H:%M')
				),
				e['l10n_type'],
				gmTools.coalesce(e['praxis_branch'], ''),
				gmTools.coalesce(e['reason_for_encounter'], ''),
				gmTools.coalesce(e['assessment_of_encounter'], ''),
				gmTools.bool2subst(e.has_clinical_data(), '', gmTools.u_checkmark_thin),
				e['pk_encounter']
			] for e in encs
		]
		lctrl.set_string_items(items = items)
		lctrl.set_data(data = encs)
		active_pk = emr.active_encounter['pk_encounter']
		for idx in range(len(encs)):
			e = encs[idx]
			if e['pk_encounter'] == active_pk:
				lctrl.SetItemTextColour(idx, wx.Colour('RED'))
	#--------------------
	return gmListWidgets.get_choices_from_list (
		parent = parent,
		msg = _("The patient's encounters.\n"),
		caption = _('Encounters ...'),
		columns = [_('When'), _('Type'), _('Where'), _('Reason for Encounter'), _('Assessment of Encounter'), _('Empty'), '#'],
		can_return_empty = False,
		single_selection = single_selection,
		refresh_callback = refresh,
		edit_callback = edit,
		new_callback = new,
		delete_callback = delete,
		list_tooltip_callback = get_tooltip,
		ignore_OK_button = ignore_OK_button,
		left_extra_button = (_('Edit active'), _('Edit the active encounter'), edit_active),
		middle_extra_button = (_('Start new'), _('Start new active encounter for the current patient.'), start_new)
	)

#----------------------------------------------------------------
class cEncounterPhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):
		gmPhraseWheel.cPhraseWheel.__init__ (self, *args, **kwargs)

		cmd = """
			SELECT DISTINCT ON (list_label)
				pk_encounter
					AS data,
				to_char(started, 'YYYY Mon DD (HH24:MI)') || ': ' || l10n_type || ' [#' || pk_encounter || ']'
					AS list_label,
				to_char(started, 'YYYY Mon DD') || ': ' || l10n_type
					AS field_label
			FROM
				clin.v_pat_encounters
			WHERE
				(
					to_char(started, 'YYYY-MM-DD') %(fragment_condition)s
						OR
					l10n_type %(fragment_condition)s
						OR
					type %(fragment_condition)s
				)	%(ctxt_patient)s
			ORDER BY
				list_label
			LIMIT
				30
		"""
		context = {'ctxt_patient': {
			'where_part': 'AND pk_patient = %(patient)s',
			'placeholder': 'patient'
		}}

		self.matcher = gmMatchProvider.cMatchProvider_SQL2(queries = [cmd], context = context)
		self.matcher._SQL_data2match = """
			SELECT
				pk_encounter
					AS data,
				to_char(started, 'YYYY Mon DD (HH24:MI)') || ': ' || l10n_type
					AS list_label,
				to_char(started, 'YYYY Mon DD') || ': ' || l10n_type
					AS field_label
			FROM
				clin.v_pat_encounters
			WHERE
				pk_encounter = %(pk)s
		"""
		self.matcher.setThresholds(1, 3, 5)
		#self.matcher.print_queries = True
		self.selection_only = True
		# outside code MUST bind this to a patient
		self.set_context(context = 'patient', val = None)
	#--------------------------------------------------------
	def set_from_instance(self, instance):
		val = '%s: %s' % (
			instance['started'].strftime('%Y %b %d'),
			instance['l10n_type']
		)
		self.SetText(value = val, data = instance['pk_encounter'])
	#------------------------------------------------------------
	def _get_data_tooltip(self):
		if self.GetData() is None:
			return None
		enc = gmEncounter.cEncounter(aPK_obj = list(self._data.values())[0]['data'])
		return enc.format (
			with_docs = False,
			with_tests = False,
			with_vaccinations = False,
			with_family_history = False
		)

#----------------------------------------------------------------
from Gnumed.wxGladeWidgets import wxgEncounterEditAreaPnl

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
		self._LBL_patient.SetLabel(pat.get_description_gender().strip())
		curr_pat = gmPerson.gmCurrentPatient()
		if curr_pat.connected:
			if curr_pat.ID == self.__encounter['pk_patient']:
				self._LBL_patient.SetForegroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOWTEXT))
			else:
				self._LBL_patient.SetForegroundColour('red')

		self._PRW_encounter_type.SetText(self.__encounter['l10n_type'], data = self.__encounter['pk_type'])
		self._PRW_location.Enable(True)
		branch = self.__encounter.praxis_branch
		if branch is None:		# None or old entry because praxis has been re-configured
			unit = self.__encounter.org_unit
			if unit is None:							# None
				self._PRW_location.SetText('', data = None)
			else:										# old entry
				self._PRW_location.Enable(False)
				self._PRW_location.SetText(_('old praxis branch: %s (%s)') % (unit['unit'], unit['organization']), data = None)
		else:
			self._PRW_location.SetText(self.__encounter['praxis_branch'], data = branch['pk_praxis_branch'])

		fts = gmDateTime.cFuzzyTimestamp (
			timestamp = self.__encounter['started'],
			accuracy = gmDateTime.ACC_MINUTES
		)
		self._PRW_start.SetText(fts.format_accurately(), data=fts)

		fts = gmDateTime.cFuzzyTimestamp (
			timestamp = self.__encounter['last_affirmed'],
			accuracy = gmDateTime.ACC_MINUTES
		)
		self._PRW_end.SetText(fts.format_accurately(), data=fts)

		# RFE
		self._TCTRL_rfe.SetValue(gmTools.coalesce(self.__encounter['reason_for_encounter'], ''))
		val, data = self._PRW_rfe_codes.generic_linked_codes2item_dict(self.__encounter.generic_codes_rfe)
		self._PRW_rfe_codes.SetText(val, data)

		# AOE
		self._TCTRL_aoe.SetValue(gmTools.coalesce(self.__encounter['assessment_of_encounter'], ''))
		val, data = self._PRW_aoe_codes.generic_linked_codes2item_dict(self.__encounter.generic_codes_aoe)
		self._PRW_aoe_codes.SetText(val, data)

		# last affirmed
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
		self._PRW_encounter_type.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))
		self._PRW_encounter_type.Refresh()

		# start
		if self._PRW_start.GetValue().strip() == '':
			self._PRW_start.SetBackgroundColour('pink')
			self._PRW_start.Refresh()
			self._PRW_start.SetFocus()
			return False
		if not self._PRW_start.is_valid_timestamp(empty_is_valid = False):
			self._PRW_start.SetBackgroundColour('pink')
			self._PRW_start.Refresh()
			self._PRW_start.SetFocus()
			return False
		self._PRW_start.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))
		self._PRW_start.Refresh()

		# last_affirmed
#		if self._PRW_end.GetValue().strip() == u'':
#			self._PRW_end.SetBackgroundColour('pink')
#			self._PRW_end.Refresh()
#			self._PRW_end.SetFocus()
#			return False
		if not self._PRW_end.is_valid_timestamp(empty_is_valid = False):
			self._PRW_end.SetBackgroundColour('pink')
			self._PRW_end.Refresh()
			self._PRW_end.SetFocus()
			return False
		self._PRW_end.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))
		self._PRW_end.Refresh()

		return True
	#--------------------------------------------------------
	def save(self):
		if not self.__is_valid_for_save():
			return False

		self.__encounter['pk_type'] = self._PRW_encounter_type.GetData()
		self.__encounter['started'] = self._PRW_start.GetData().get_pydt()
		self.__encounter['last_affirmed'] = self._PRW_end.GetData().get_pydt()
		self.__encounter['reason_for_encounter'] = gmTools.none_if(self._TCTRL_rfe.GetValue().strip(), '')
		self.__encounter['assessment_of_encounter'] = gmTools.none_if(self._TCTRL_aoe.GetValue().strip(), '')
		self.__encounter.save_payload()			# FIXME: error checking

		self.__encounter.generic_codes_rfe = [ c['data'] for c in self._PRW_rfe_codes.GetData() ]
		self.__encounter.generic_codes_aoe = [ c['data'] for c in self._PRW_aoe_codes.GetData() ]

		return True

#----------------------------------------------------------------
from Gnumed.wxGladeWidgets import wxgEncounterEditAreaDlg

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
			self._BTN_save.SetToolTip(button_defs[0][1])
			self._BTN_close.SetLabel(button_defs[1][0])
			self._BTN_close.SetToolTip(button_defs[1][1])
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
	#--------------------------------------------------------
	def _on_encounter_start_lost_focus(self):
		start = self._PRW_encounter_start.GetData()
		if start is None:
			return
		start = start.get_pydt()

		end = self._PRW_encounter_end.GetData()
		if end is None:
			fts = gmDateTime.cFuzzyTimestamp (
				timestamp = start,
				accuracy = gmDateTime.ACC_MINUTES
			)
			self._PRW_encounter_end.SetText(fts.format_accurately(), data = fts)
			return
		end = end.get_pydt()

		if start > end:
			end = end.replace (
				year = start.year,
				month = start.month,
				day = start.day
			)
			fts = gmDateTime.cFuzzyTimestamp (
				timestamp = end,
				accuracy = gmDateTime.ACC_MINUTES
			)
			self._PRW_encounter_end.SetText(fts.format_accurately(), data = fts)
			return

		emr = self.__pat.emr
		if start != emr.active_encounter['started']:
			end = end.replace (
				year = start.year,
				month = start.month,
				day = start.day
			)
			fts = gmDateTime.cFuzzyTimestamp (
				timestamp = end,
				accuracy = gmDateTime.ACC_MINUTES
			)
			self._PRW_encounter_end.SetText(fts.format_accurately(), data = fts)
			return

		return

#----------------------------------------------------------------
from Gnumed.wxGladeWidgets import wxgActiveEncounterPnl

class cActiveEncounterPnl(wxgActiveEncounterPnl.wxgActiveEncounterPnl):

	def __init__(self, *args, **kwargs):
		wxgActiveEncounterPnl.wxgActiveEncounterPnl.__init__(self, *args, **kwargs)
		self.__register_events()
		self.refresh()

	#------------------------------------------------------------
	def clear(self):
		self._TCTRL_encounter.SetValue('')
		self._TCTRL_encounter.SetToolTip('')
		self._BTN_new.Enable(False)
		self._BTN_list.Enable(False)

	#------------------------------------------------------------
	def refresh(self):
		self.clear()

		pat = gmPerson.gmCurrentPatient()
		if not pat.connected:
			return

		wx.CallAfter(self.__refresh)

	#------------------------------------------------------------
	def __refresh(self):
		enc = gmPerson.gmCurrentPatient().emr.active_encounter
		self._TCTRL_encounter.SetValue(enc.format (
			with_docs = False,
			with_tests = False,
			fancy_header = False,
			with_vaccinations = False,
			with_family_history = False).strip('\n')
		)
		self._TCTRL_encounter.SetToolTip (
			_('The active encounter of the current patient:\n\n%s') % enc.format(
				with_docs = False,
				with_tests = False,
				fancy_header = True,
				with_vaccinations = False,
				with_rfe_aoe = True,
				with_family_history = False).strip('\n')
		)
		self._BTN_new.Enable(True)
		self._BTN_list.Enable(True)

	#------------------------------------------------------------
	def __register_events(self):
		self._TCTRL_encounter.Bind(wx.EVT_LEFT_DCLICK, self._on_ldclick)

		gmDispatcher.connect(signal = 'pre_patient_unselection', receiver = self._on_pre_patient_unselection)
		# this would throw an exception due to concurrency issues:
		#gmDispatcher.connect(signal = u'post_patient_selection', receiver = self.refresh)
		gmDispatcher.connect(signal = 'clin.episode_mod_db', receiver = self.refresh)
		gmDispatcher.connect(signal = 'current_encounter_modified', receiver = self.refresh)
		gmDispatcher.connect(signal = 'current_encounter_switched', receiver = self.refresh)

	#------------------------------------------------------------
	# event handler
	#------------------------------------------------------------
	def _on_pre_patient_unselection(self):
		self.clear()

	#------------------------------------------------------------
	def _on_ldclick(self, event):
		pat = gmPerson.gmCurrentPatient()
		if not pat.connected:
			return
		edit_encounter(encounter = pat.emr.active_encounter)

	#------------------------------------------------------------
	def _on_new_button_pressed(self, event):
		pat = gmPerson.gmCurrentPatient()
		if not pat.connected:
			return
		start_new_encounter(emr = pat.emr)

	#------------------------------------------------------------
	def _on_list_button_pressed(self, event):
		if not gmPerson.gmCurrentPatient().connected:
			return
		select_encounters()

#================================================================
# encounter TYPE related widgets
#----------------------------------------------------------------
def edit_encounter_type(parent=None, encounter_type=None):
	ea = cEncounterTypeEditAreaPnl(parent, -1)
	ea.data = encounter_type
	ea.mode = gmTools.coalesce(encounter_type, 'new', 'edit')
	dlg = gmEditArea.cGenericEditAreaDlg2(parent, -1, edit_area = ea)
	dlg.SetTitle(gmTools.coalesce(encounter_type, _('Adding new encounter type'), _('Editing local encounter type name')))
	if dlg.ShowModal() == wx.ID_OK:
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
		if gmEncounter.delete_encounter_type(description = enc_type['description']):
			return True
		gmDispatcher.send (
			signal = 'statustext',
			msg = _('Cannot delete encounter type [%s]. It is in use.') % enc_type['l10n_description'],
			beep = True
		)
		return False
	#--------------------
	def refresh(lctrl):
		enc_types = gmEncounter.get_encounter_types()
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
from Gnumed.wxGladeWidgets import wxgEncounterTypeEditAreaPnl

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
			if self._TCTRL_l10n_name.GetValue().strip() == '':
				self.display_tctrl_as_valid(tctrl = self._TCTRL_l10n_name, valid = False)
				return False
			self.display_tctrl_as_valid(tctrl = self._TCTRL_l10n_name, valid = True)
			return True

		no_errors = True

		if self._TCTRL_l10n_name.GetValue().strip() == '':
			if self._TCTRL_name.GetValue().strip() == '':
				self.display_tctrl_as_valid(tctrl = self._TCTRL_l10n_name, valid = False)
				no_errors = False
			else:
				self.display_tctrl_as_valid(tctrl = self._TCTRL_l10n_name, valid = True)
		else:
			self.display_tctrl_as_valid(tctrl = self._TCTRL_l10n_name, valid = True)

		if self._TCTRL_name.GetValue().strip() == '':
			if self._TCTRL_l10n_name.GetValue().strip() == '':
				self.display_tctrl_as_valid(tctrl = self._TCTRL_name, valid = False)
				no_errors = False
			else:
				self.display_tctrl_as_valid(tctrl = self._TCTRL_name, valid = True)
		else:
			self.display_tctrl_as_valid(tctrl = self._TCTRL_name, valid = True)

		return no_errors
	#-------------------------------------------------------
	def _save_as_new(self):
		enc_type = gmEncounter.create_encounter_type (
			description = gmTools.none_if(self._TCTRL_name.GetValue().strip(), ''),
			l10n_description = gmTools.coalesce (
				gmTools.none_if(self._TCTRL_l10n_name.GetValue().strip(), ''),
				self._TCTRL_name.GetValue().strip()
			)
		)
		if enc_type is None:
			return False
		self.data = enc_type
		return True
	#-------------------------------------------------------
	def _save_as_update(self):
		enc_type = gmEncounter.update_encounter_type (
			description = self._TCTRL_name.GetValue().strip(),
			l10n_description = self._TCTRL_l10n_name.GetValue().strip()
		)
		if enc_type is None:
			return False
		self.data = enc_type
		return True
	#-------------------------------------------------------
	def _refresh_as_new(self):
		self._TCTRL_l10n_name.SetValue('')
		self._TCTRL_name.SetValue('')
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
class cEncounterTypePhraseWheel(gmPhraseWheel.cPhraseWheel):
	"""Phrasewheel to allow selection of encounter type.

	- user input interpreted as encounter type in English or local language
	- data returned is pk of corresponding encounter type or None
	"""
	def __init__(self, *args, **kwargs):

		gmPhraseWheel.cPhraseWheel.__init__ (self, *args, **kwargs)

		mp = gmMatchProvider.cMatchProvider_SQL2 (
			queries = [
"""
SELECT
	data,
	field_label,
	list_label
FROM (
	SELECT DISTINCT ON (data) *
	FROM (
		SELECT
			pk AS data,
			_(description) AS field_label,
			case
				when _(description) = description then _(description)
				else _(description) || ' (' || description || ')'
			end AS list_label
		FROM
			clin.encounter_type
		WHERE
			_(description) %(fragment_condition)s
				OR
			description %(fragment_condition)s
	) AS q_distinct_pk
) AS q_ordered
ORDER BY
	list_label
"""			]
		)
		mp.setThresholds(2, 4, 6)

		self.matcher = mp
		self.selection_only = True
		self.picklist_delay = 50

#================================================================
# main
#----------------------------------------------------------------
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	from Gnumed.pycommon import gmI18N
	gmI18N.activate_locale()
	gmI18N.install_domain()

	#----------------------------------------------------------------
#	def test_encounter_edit_area_panel():
		#app = wx.PyWidgetTester(size = (200, 300))
		#emr = pat.emr
		#enc = emr.active_encounter
		#enc = gmEncounter.cEncounter(1)
		#pnl = 
		#cEncounterEditAreaPnl(app.frame, -1, encounter=enc)
		#app.frame.Show(True)
		#app.MainLoop()

	#----------------------------------------------------------------
#	def test_encounter_edit_area_dialog():
		#app = wx.PyWidgetTester(size = (200, 300))
		#emr = pat.emr
		#enc = emr.active_encounter
#		enc = gmEncounter.cEncounter(1)
		#dlg = cEncounterEditAreaDlg(parent=app.frame, id=-1, size = (400,400), encounter=enc)
		#dlg.ShowModal()
#		pnl = cEncounterEditAreaDlg(app.frame, -1, encounter=enc)
#		app.frame.Show(True)
#		app.MainLoop()

	#----------------------------------------------------------------
	#test_encounter_edit_area_panel()
	#test_encounter_edit_area_dialog()
