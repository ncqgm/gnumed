"""GNUmed substance intake handling widgets."""

#================================================================
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL v2 or later"

import logging
import sys


import wx


if __name__ == '__main__':
	sys.path.insert(0, '../../')

from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmDateTime
from Gnumed.pycommon import gmNetworkTools
from Gnumed.pycommon import gmPG2

from Gnumed.business import gmPerson
from Gnumed.business import gmMedication
from Gnumed.business import gmLOINC
from Gnumed.business import gmClinicalCalculator

from Gnumed.wxpython import gmGuiHelpers
from Gnumed.wxpython import gmEditArea
from Gnumed.wxpython import gmListWidgets
from Gnumed.wxpython import gmAllergyWidgets

_log = logging.getLogger('gm.ui')

#============================================================
# current substance intake widgets
#------------------------------------------------------------
def manage_substance_intakes(parent=None, emr=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	if emr is None:
		emr = gmPerson.gmCurrentPatient().emr
#	#------------------------------------------------------------
#	def add_from_db(substance):
#		drug_db = gmSubstanceMgmtWidgets.get_drug_database(parent = parent, patient = gmPerson.gmCurrentPatient())
#		if drug_db is None:
#			return False
#		drug_db.import_drugs()
#		return True

	#------------------------------------------------------------
	def edit(intake=None):
		return edit_intake_of_substance(parent = parent, intake = intake, single_entry = True)

	#------------------------------------------------------------
	def delete(intake):
		do_delete = gmGuiHelpers.gm_show_question (
			title = _('Deleting substance intake'),
			question = _('Really delete substance intake ?')
		)
		if not do_delete:
			return False

		#if intake['pk_intake_regimen']:
		return gmMedication.delete_substance_intake(pk_intake = intake['pk_intake'], delete_regimen = False)

	#------------------------------------------------------------
	def get_tooltip(intake=None):
		return intake.format(single_line = False, show_all_product_components = True)

	#------------------------------------------------------------
	def refresh(lctrl):
		intakes = emr.get_current_medications (
			include_inactive = False,
			order_by = 'substance, started'
		)
		items = []
		for i in intakes:
			started = i.medically_formatted_start
			items.append ([
				'%s%s %s %s %s' % (
					i['substance'],
					gmTools.coalesce(i['drug_product'], '', ' (%s)'),
					gmTools.coalesce(i['amount'], '', ' %s'),
					gmMedication.format_units (
						i['unit'],
						i['dose_unit'],
						preparation = i['l10n_preparation'],
						short = True
					),
					gmTools.coalesce(i['external_code'], '', ' [%s::%s]' % (i['external_code_type'], i['external_code']))
				),
				'%s: %s%s %s' % (
					started,
					gmTools.coalesce(i['schedule'], '', ' %s'),
					gmTools.coalesce(i['planned_duration'], '', _(' for %s')),
					gmTools.u_arrow2right
				)
			])
		lctrl.set_string_items(items)
		lctrl.set_data(intakes)

	#------------------------------------------------------------
	return gmListWidgets.get_choices_from_list (
		parent = parent,
		caption = _('Substances consumed by the patient'),
		columns = [ _('Intake'), _('Application'), _('Status') ],
		single_selection = False,
		new_callback = edit,
		edit_callback = edit,
		delete_callback = delete,
		refresh_callback = refresh,
		list_tooltip_callback = get_tooltip
#		,left_extra_button = (_('Import'), _('Import consumable substances from a drug database.'), add_from_db)
	)

#------------------------------------------------------------
def edit_intake_of_substance(parent = None, intake=None, single_entry=False):
	ea = cSubstanceIntakeEAPnl(parent, -1, intake = intake)
	dlg = gmEditArea.cGenericEditAreaDlg2(parent, -1, edit_area = ea, single_entry = single_entry)
	dlg.SetTitle(gmTools.coalesce(intake, _('Adding substance intake'), _('Editing substance intake')))
	dlg.left_extra_button = (
		_('Allergy'),
		_('Document an allergy against this substance.'),
		ea.turn_into_allergy
	)
	dlg.SetSize((650,750))
	if dlg.ShowModal() == wx.ID_OK:
		dlg.DestroyLater()
		return True

	dlg.DestroyLater()
	return False

#------------------------------------------------------------
def delete_substance_intake(parent=None, intake=None):

	comps = intake.containing_drug.components
	if len(comps) > 1:
		msg = _(
			'This intake is part of a multi-component drug product:\n'
			'\n'
			' %s\n'
			'\n'
			'Really delete all intakes related to this drug product ?'
		) % '\n '.join (
			[ '%s %s%s' % (c['substance'], c['amount'], c.formatted_units) for c in comps ]
		)
		delete_all = gmGuiHelpers.gm_show_question (
			title = _('Deleting medication / substance intake'),
			question = msg
		)
		if not delete_all:
			return

	msg = _(
		'\n'
		'[%s]\n'
		'\n'
		'It may be prudent to edit (before deletion) the details\n'
		'of this substance intake entry so as to leave behind\n'
		'some indication of why it was deleted.\n'
	) % intake.format()

	dlg = gmGuiHelpers.c3ButtonQuestionDlg (
		parent,
		-1,
		caption = _('Deleting medication / substance intake'),
		question = msg,
		button_defs = [
			{'label': _('&Edit'), 'tooltip': _('Allow editing of substance intake entry before deletion.'), 'default': True},
			{'label': _('&Delete'), 'tooltip': _('Delete immediately without editing first.')},
			{'label': _('&Cancel'), 'tooltip': _('Abort. Do not delete or edit substance intake entry.')}
		]
	)

	edit_first = dlg.ShowModal()
	dlg.DestroyLater()

	if edit_first == wx.ID_CANCEL:
		return

	if edit_first == wx.ID_YES:
		edit_intake_of_substance(parent = parent, intake = intake)
		delete_it = gmGuiHelpers.gm_show_question (
			aMessage = _('Now delete substance intake entry ?'),
			aTitle = _('Deleting medication / substance intake')
		)
	else:
		delete_it = True

	if not delete_it:
		return

	gmMedication.delete_substance_intake(pk_intake = intake['pk_intake'], delete_siblings = True)

#============================================================
from Gnumed.wxGladeWidgets import wxgSubstanceIntakeEAPnl

class cSubstanceIntakeEAPnl(wxgSubstanceIntakeEAPnl.wxgSubstanceIntakeEAPnl, gmEditArea.cGenericEditAreaMixin):
	"""Enter or edit intake with regiment of a substance."""
	def __init__(self, *args, **kwargs):
		try:
			data = kwargs['intake']
			del kwargs['intake']
		except KeyError:
			data = None
		assert not data or isinstance(data, gmMedication.cInstakeWithRegimen), '<intake> must be of type "gmMedication.cInstakeWithRegimen" if given'

		self.calc = gmClinicalCalculator.cClinicalCalculator()

		wxgSubstanceIntakeEAPnl.wxgSubstanceIntakeEAPnl.__init__(self, *args, **kwargs)
		gmEditArea.cGenericEditAreaMixin.__init__(self)

		self.mode = 'new'
		self.data = data
		if data:
			self.mode = 'edit'
		self.__init_ui()

	#----------------------------------------------------------------
	def __init_ui(self):
		self._PRW_substance.selection_only = False
		self._PRW_substance.add_callback_on_lose_focus(callback = self._on_leave_substance)
		self._PRW_duration.display_accuracy = gmDateTime.acc_days
		self._PRW_patient_notes.add_callback_on_set_focus(callback = self._on_enter_notes4patient)
		self._DP_discontinued.add_callback_on_selection(callback = self._on_discontinued_date_changed)
		self._LCTRL_regimen.set_resize_column()
		#self._LCTRL_regimen.set_column_widths([wx.LIST_AUTOSIZE])
		self._LCTRL_regimen.select_callback = self._on_regimen_selected
		self.Layout()

	#----------------------------------------------------------------
	def __refresh_precautions(self):

		curr_pat = gmPerson.gmCurrentPatient()
		emr = curr_pat.emr
		msg_lines = []
		tt_lines = []

		# allergies
		state = emr.allergy_state
		if state['last_confirmed'] is None:
			confirmed = _('never')
		else:
			confirmed = gmDateTime.pydt_strftime(state['last_confirmed'], '%Y %b %d')
		msg_lines.append(_('%s, last confirmed %s') % (state.state_string, confirmed))
		if state['comment']:
			msg_lines.append(_('Comment (%s): %%s') % (state['comment'], state['modified_by']))
		allgs = emr.get_allergies()
		for allergy in allgs:
			msg_lines.append(' %s: %s (%s)' % (
				allergy['descriptor'],
				allergy['l10n_type'],
				gmTools.bool2subst(allergy['definite'], _('definite'), _('suspected'), '?')
			))
			tt_lines.append('%s: %s' % (
				allergy['descriptor'],
				gmTools.coalesce(allergy['reaction'], _('reaction not recorded'))
			))
		if allgs:
			msg_lines.append('')
			tt_lines.append('')
		del allgs

		# history of substance abuse
		abuses = emr.abused_substances
		for abuse in abuses:
			#tt_lines.append(abuse.format(single_line = False, include_metadata = False))
			tt_lines.append('MISUSE FORMATTING is missing')
			tt_lines.append('')
			if abuse['use_type'] in [None, 0]:
				continue
			#msg_lines.append(abuse.format(single_line = True))
			msg_lines.append('MISUSE FORMATTING is missing')
		if abuses:
			msg_lines.append('')
			tt_lines.append('')
		del abuses

		# kidney function
		gfrs = emr.get_most_recent_results_in_loinc_group(loincs = gmLOINC.LOINC_gfr_quantity, max_no_of_results = 1)
		if len(gfrs) == 0:
			self.calc.patient = curr_pat
			gfr = self.calc.eGFR
			if gfr.numeric_value is None:
				msg_lines.append(_('GFR: unknown'))
			else:
				msg_lines.append(gfr.message)
				egfrs = self.calc.eGFRs
				for egfr in egfrs:
					if egfr.numeric_value is None:
						continue
					tt_lines.append(egfr.format (
						left_margin = 0,
						width = 50,
						with_formula = False,
						with_warnings = True,
						with_variables = False,
						with_sub_results = False,
						return_list = True
					))
		else:
			gfr = gfrs[0]
			msg_lines.append('%s: %s %s (%s)\n' % (
				gfr['unified_abbrev'],
				gfr['unified_val'],
				gmTools.coalesce(gfr['abnormality_indicator'], '', ' (%s)'),
				gmDateTime.pydt_strftime (
					gfr['clin_when'],
					format = '%Y %b %d'
				)
			))
			tt_lines.append(_('GFR reported by path lab'))

		# pregnancy
		edc = emr.EDC
		if edc is not None:
			msg_lines.append('')
			msg_lines.append('')
			if emr.EDC_is_fishy:
				msg_lines.append(_('EDC (!?!): %s') % gmDateTime.pydt_strftime(edc, format = '%Y %b %d'))
				tt_lines.append(_(
					'The Expected Date of Confinement is rather questionable.\n'
					'\n'
					'Please check patient age, patient gender, time until/since EDC.'
				))
			else:
				msg_lines.append(_('EDC: %s') % gmDateTime.pydt_strftime(edc, format = '%Y %b %d'))

		self._LBL_information.SetLabel('\n'.join(msg_lines))
		self._LBL_information.SetToolTip('\n'.join(tt_lines))
		self.Layout()

	#----------------------------------------------------------------
	def __refresh_regimens(self):
		if not self.data:
			self._LCTRL_regimen.set_string_items()
			return

		items = []
		data = []
		for regimen in self.data.regimens_for_substance:
			items.append(regimen.format(single_line = True))
			data.append(regimen)
		self._LCTRL_regimen.set_columns([_('Existing treatment regimens for this substance')])
		self._LCTRL_regimen.set_string_items(items)
		self._LCTRL_regimen.set_data(data)
		self._LCTRL_regimen.set_column_widths()

	#----------------------------------------------------------------
	def __refresh_regimens_from_substance(self):
		if not self._PRW_substance.GetData():
			self._LCTRL_regimen.set_string_items()
			return

		pk_subst, pk_dose = self._PRW_substance.GetData()
		items = []
		data = []
		for regimen in gmMedication.get_intake_regimens(pk_substance = pk_subst, pk_patient = gmPerson.gmCurrentPatient().ID):
			items.append(regimen.format(single_line = True, terse = False))
			data.append(regimen)
		self._LCTRL_regimen.set_columns([_('Existing treatment regimens')])
		self._LCTRL_regimen.set_string_items(items)
		self._LCTRL_regimen.set_data(data)
		self._LCTRL_regimen.set_column_widths()

	#----------------------------------------------------------------
	# generic Edit Area mixin API
	#----------------------------------------------------------------
	def _validate_amount_and_unit(self, dose=None) -> bool:
		if not dose:
			dose = self._PRW_substance.GetData(as_instance = True)
		if isinstance(dose, gmMedication.cSubstanceDose):
			self._TCTRL_amount.display_as_valid()
			self._TCTRL_unit.display_as_valid()
			return True

		if self._TCTRL_amount.Value.strip() == '':
			self._TCTRL_amount.display_as_valid()
			# if unit is not '' then it is not strictly valid but will not be considered during save
			self._TCTRL_unit.display_as_valid()
			return True

		amount_is_num, amount = gmTools.input2decimal(self._TCTRL_amount.Value)
		if not amount_is_num:
			self.StatusText = _('Amount: must be a number, if given')
			self._TCTRL_amount.display_as_valid(False)
			self._TCTRL_amount.SetFocus()
			return False

		self._TCTRL_amount.display_as_valid()
		if self._TCTRL_unit.Value.strip() != '':
			self._TCTRL_unit.display_as_valid()
			return True

		self.StatusText = _('Unit: must be set when amount is given')
		self._TCTRL_unit.display_as_valid(False)
		self._TCTRL_unit.SetFocus()
		return False

	#----------------------------------------------------------------
	def _validate_schedule(self, dose=None) -> bool:
		if self._PRW_schedule.GetValue().strip() != '':
			# any schedule is fine
			self._PRW_schedule.display_as_valid()
			return True

		# if no amount given (IOW, not a dose) then schedule is not required
		if self._TCTRL_amount.Value.strip() == '':
			self._PRW_schedule.display_as_valid()
			return True

		self.StatusText = _('Schedule: must be set when amount is given')
		self._PRW_schedule.display_as_valid(False)
		self._PRW_schedule.SetFocus()
		return False

	#----------------------------------------------------------------
	def _validate_discontinued(self, started) -> bool:
		"""discontinued: must be "< now()" AND "> started" if at all"""
		discontinued = self._DP_discontinued.GetData()
		if not discontinued:
			self._DP_discontinued.display_as_valid()
			return True

		now = gmDateTime.pydt_now_here().replace(hour = 23, minute = 59, second = 59, microsecond = 111111)
		if discontinued > now:
			self.StatusText = _('Discontinued (%s) in the future (now: %s)') % (discontinued, now)
			self._DP_discontinued.display_as_valid(False)
			self._DP_discontinued.SetFocus()
			return False

		if not started:
			self._DP_discontinued.display_as_valid()
			return True

		started = started.replace(hour = 0, minute = 0, second = 0, microsecond = 1)
		if started > discontinued:
			self.StatusText = _('Discontinued (%s) before started (%s)') % (discontinued, started)
			self._DP_started.display_as_valid(False)
			self._DP_discontinued.display_as_valid(False)
			self._DP_discontinued.SetFocus()
			return False

		self._DP_discontinued.display_as_valid()
		return True

	#----------------------------------------------------------------
	def _validate_duration(self) -> bool:
		if self._PRW_duration.GetValue().strip() in ['', gmTools.u_infinity]:
			self._PRW_duration.display_as_valid()
			return True

		if self._PRW_duration.GetData():
			self._PRW_duration.display_as_valid()
			return True

		# no data ...
		if gmDateTime.str2interval(self._PRW_duration.GetValue()):
			self._PRW_duration.display_as_valid()
			return True

		self.StatusText = _('Duration: must be an interval')
		self._PRW_duration.display_as_valid(False)
		self._PRW_duration.SetFocus()
		return False

	#----------------------------------------------------------------
	def _validate_substance_or_dose(self) -> bool:
		if self.mode == 'edit':
			# no validation needed, substance/dose cannot be edited
			return True

		if self._PRW_substance.GetData():
			pk_subst, pk_dose = self._PRW_substance.GetData()
			if gmMedication.substance_intake_exists (
				pk_identity = gmPerson.gmCurrentPatient().ID,
				pk_substance = pk_subst
			):
				self.StatusText = _('Cannot add duplicate of (maybe inactive) substance intake.')
				self._PRW_substance.display_as_valid(False)
				self._PRW_substance.SetFocus()
				gmGuiHelpers.gm_show_warning (
					aTitle = _('Adding substance intake'),
					aMessage = _('This substance is already being taken by the patient.')
				)
				return False	# might switch to editing upon asking

			self._PRW_substance.display_as_valid()
			return True

		if self._PRW_substance.Value.strip() == '':
			self.StatusText = _('Required: substance/dose')
			self._PRW_substance.display_as_valid(False)
			self._PRW_substance.SetFocus()
			return False

		self._PRW_substance.display_as_valid()
		return True

	#----------------------------------------------------------------
	def _valid_for_save(self) -> bool:
		if self.mode != 'new':
			self.StatusText = 'only NEW so far'
			return False

		self.StatusText = ''
		is_valid = True

		if self.mode == 'new':
			is_valid = is_valid and self._validate_substance_or_dose()
			is_valid = is_valid and self._validate_amount_and_unit()
			is_valid = is_valid and self._validate_schedule()
			# started
			started = None
			if self._CHBOX_start_unknown.IsChecked() is False:
				started = self._DP_started.GetData()
				if started is None:
					self.StatusText = _('Started: enter date or checkmark "Unknown"')
					self._DP_started.display_as_valid(False)
					self._DP_started.SetFocus()
					is_valid = False
				else:
					self._DP_started.display_as_valid()
			# duration
			is_valid = is_valid and self._validate_duration()
			is_valid = is_valid and self._validate_discontinued(started)

		return is_valid

	#----------------------------------------------------------------
	def _save_as_new(self) -> bool:
		conn4tx = gmPG2.get_connection(readonly = False)
		pk_epi = self._PRW_episode.GetData(as_instance = False)
		if pk_epi is None:
			if self._PRW_episode.Value.strip() == '':
				self._PRW_episode.SetValue(gmMedication.DEFAULT_MEDICATION_HISTORY_EPISODE)
				is_open = False
			else:
				is_open = True		# Jim wants new episode to auto-open
			pk_epi = self._PRW_episode.GetData (
				can_create = True,
				is_open = is_open,
				as_instance = False, link_obj = conn4tx
			)
		subst_or_dose = self._PRW_substance.GetData(as_instance = True)
		if not subst_or_dose:
			subst_or_dose = gmMedication.create_substance (
				substance = self._PRW_substance.Value.strip(),
				link_obj = conn4tx
			)
		if isinstance(subst_or_dose, gmMedication.cSubstance):
			if self._TCTRL_amount.Value.strip():
				subst_or_dose = gmMedication.create_substance_dose (
					link_obj = conn4tx,
					pk_substance = subst_or_dose['pk_substance'],
					amount = self._TCTRL_amount.Value.strip(),
					unit = self._TCTRL_unit.Value.strip()
				)
		intake = gmMedication.create_substance_intake (
			pk_encounter = gmPerson.gmCurrentPatient().emr.current_encounter['pk_encounter'],
			pk_episode = pk_epi,
			pk_substance = subst_or_dose['pk_substance'],
			link_obj = conn4tx
		)
		intake['notes4patient'] = self._PRW_patient_notes.Value
		intake['notes4provider'] = self._PRW_provider_notes.Value
		intake.save(conn = conn4tx)
		if self._PRW_schedule.Value.strip() == '':
			conn4tx.commit()
			conn4tx.close()
			data = gmMedication.cIntakeWithRegimen(aPK_obj = {
				'pk_intake': intake['pk_intake'],
				'pk_intake_regimen': None
			})
			self.data = data
			return True

		regimen = gmMedication.create_intake_regimen (
			pk_intake = intake['pk_intake'],
			started = self._DP_started.GetData(),
			pk_encounter = intake['pk_encounter'],
			pk_episode = intake['pk_episode'],
			schedule = self._PRW_schedule.Value.strip(),
			discontinued = self._DP_discontinued.GetData(),
			link_obj = conn4tx
		)
		if self._CHBOX_start_unknown.IsChecked():
			regimen['comment_on_start'] = gmMedication.COMMENT_FOR_UNKNOWN_START
		else:
			regimen['comment_on_start'] = self._PRW_start_certainty.Value.strip()
		if regimen['discontinued']:
			regimen['discontinue_reason'] = self._PRW_discontinue_reason.Value.strip()
		if self._PRW_duration.Value.strip() in ['', gmTools.u_infinity]:
			regimen['planned_duration'] = None
		else:
			if self._PRW_duration.GetData():
				regimen['planned_duration'] = self._PRW_duration.GetData()
			else:
				regimen['planned_duration'] = gmDateTime.str2interval(self._PRW_duration.Value.strip())
		if isinstance(subst_or_dose, gmMedication.cSubstanceDose):
			regimen['pk_dose'] = subst_or_dose['pk_dose']
		regimen.save(conn = conn4tx)
		conn4tx.commit()
		conn4tx.close()
		#intake.refetch_payload()	# a regimen has been added, so refetch
		# now get instake_with_regimen
		data = cIntakeWithRegimen(aPK_obj = {
			'pk_intake': intake['pk_intake'],
			'pk_intake_regimen': regimen['pk_intake_regimen']
		})
		self.data = data
		return True

	#----------------------------------------------------------------
	def _save_as_update(self):

		self.data['notes4patient'] = self._PRW_patient_notes.GetValue()
		self.data['notes4provider'] = self._PRW_provider_notes.GetValue()
		epi = self._PRW_episode.GetData()
		if epi is None:
			# create new episode, Jim wants it to auto-open
			epi = self._PRW_episode.GetData(can_create = True, is_open = True)
		self.data['pk_episode'] = epi

		self.data['started'] = self._DP_started.GetData()
		if self._CHBOX_start_unknown.IsChecked():
			self.data['comment_on_start'] = gmMedication.COMMENT_FOR_UNKNOWN_START
		else:
			self.data['comment_on_start'] = self._PRW_start_certainty.GetValue().strip()
		self.data['discontinued'] = self._DP_discontinued.GetData()
		if self.data['discontinued'] is None:
			self.data['discontinue_reason'] = None
		else:
			self.data['discontinue_reason'] = self._PRW_discontinue_reason.GetValue().strip()
		self.data['schedule'] = self._PRW_schedule.GetValue()
		if self._PRW_duration.GetValue().strip() in ['', gmTools.u_infinity]:
			self.data['planned_duration'] = None
		else:
			if self._PRW_duration.GetData() is None:
				self.data['planned_duration'] = gmDateTime.str2interval(self._PRW_duration.GetValue())
			else:
				self.data['planned_duration'] = self._PRW_duration.GetData()

		self.data.save()
		return True

	#----------------------------------------------------------------
	def _refresh_as_new(self):
		self._PRW_substance.SetText('', None)
		self._PRW_substance.Enable()
		self._PRW_episode.SetText('', None)
		self._PRW_patient_notes.SetText('', None)
		self._PRW_provider_notes.SetText('', None)
		# regimen fields
		self._BTN_edit_regimen.Disable()
		self._BTN_delete_regimen.Disable()
		self._BTN_add_regimen.Disable()
		self._TCTRL_amount.SetValue('')
		self._TCTRL_amount.Disable()
		self._TCTRL_unit.SetValue('')
		self._TCTRL_unit.Disable()
		self._PRW_schedule.SetText('', None)
		self._PRW_schedule.Disable()
		self._CHBOX_start_unknown.SetValue(False)
		self._CHBOX_start_unknown.Disable()
		self._DP_started.SetData(gmDateTime.pydt_now_here())
		self._DP_started.Disable()
		self._PRW_start_certainty.SetText('', None)
		self._PRW_start_certainty.Disable()
		self._PRW_duration.SetText('', None)
		self._PRW_duration.Disable()
		self._DP_discontinued.SetData(None)
		self._DP_discontinued.Disable()
		self._PRW_discontinue_reason.SetValue('')
		self._PRW_discontinue_reason.Disable()
		self.__refresh_regimens()
		self.__refresh_precautions()
		self._PRW_substance.SetFocus()

	#----------------------------------------------------------------
	def _refresh_from_existing(self):
		self._refresh_as_new()
		assert isinstance(self.data, gmMedication.cIntakeWithRegimen), '<intake> must be of type "gmMedication.cIntakeWithRegimen" if given'

		self._PRW_substance.SetText (
			value = self.data['substance'],
			data = (self.data['pk_substance'], self.data['pk_dose'])
		)
		self._PRW_substance.Disable()
		self._PRW_episode.SetData(self.data['pk_episode'])
		self._PRW_patient_notes.SetText(self.data['notes4patient'], None, suppress_smarts = True)
		self._PRW_provider_notes.SetText(self.data['notes4provider'], None, suppress_smarts = True)

		self._TCTRL_amount.Disable()
		self._TCTRL_unit.Disable()
		self._PRW_schedule.Disable()
		self._CHBOX_start_unknown.Disable()
		self._DP_started.Disable()
		self._PRW_start_certainty.Disable()
		self._PRW_duration.Disable()
		self._DP_discontinued.Disable()
		self._PRW_discontinue_reason.Disable()

		self.__refresh_regimens()
		self.__refresh_precautions()
		self._LCTRL_regimen.SetFocus()

	#----------------------------------------------------------------
	def _refresh_as_new_from_existing(self):
		self._refresh_as_new()
		self._PRW_episode.SetData(self.data['pk_episode'])
		self._DP_started.SetData(self.data['started'])
		self._PRW_drug.SetFocus()

	#----------------------------------------------------------------
	# event handlers
	#----------------------------------------------------------------
	def _on_regimen_selected(self, event):
		regimen = self._LCTRL_regimen.get_selected_item_data(only_one = True)
		if not regimen:
			return

		self._TCTRL_amount.SetValue(str(regimen['amount']))
		self._TCTRL_unit.SetValue(regimen['unit'])
		self._PRW_schedule.SetText(regimen['schedule'], regimen['schedule'])
		if regimen.start_is_unknown:
			self._CHBOX_start_unknown.Value = True
			self._DP_started.Value = None
		else:
			self._CHBOX_start_unknown.Value = False
			self._DP_started.SetValue(regimen['started'])
		self._PRW_start_certainty.SetValue(gmTools.coalesce(regimen['comment_on_start'], ''))
		self._PRW_duration.SetValue(regimen['planned_duration'])
		self._DP_discontinued.SetValue(regimen['discontinued'])
		self._PRW_discontinue_reason.SetValue(gmTools.coalesce(regimen['discontinue_reason'], ''))

	#----------------------------------------------------------------
	def _on_leave_substance(self):
		self.__refresh_regimens_from_substance()
		if self.mode == 'new':
			if self._PRW_substance.Value.strip() == '':
				self._PRW_substance.display_as_valid(False)
				self._TCTRL_amount.Disable()
				self._TCTRL_unit.Disable()
				self._PRW_schedule.Disable()
				return

			self._PRW_substance.display_as_valid()
			self._PRW_schedule.Enable()
			if self._PRW_substance.has_dose:
				dose = self._PRW_substance.GetData(as_instance = True)
				self._TCTRL_amount.SetValue(str(dose['amount']))
				self._TCTRL_amount.display_as_valid()
				self._TCTRL_amount.Disable()
				self._TCTRL_unit.SetValue(dose['unit'])
				self._TCTRL_unit.display_as_valid()
				self._TCTRL_unit.Disable()
				return

			self._TCTRL_amount.Enable()
			self._TCTRL_unit.Enable()
			self._PRW_schedule.Enable()
		return

#		if self.mode == 'edit':
#			self._PRW_substance.display_as_valid()
#			self._TCTRL_amount.Disable()
#			self._TCTRL_unit.Disable()
#			self._PRW_schedule.Disable()
#			self._CHBOX_start_unknown.Disable()
#			self._DP_started.Disable()
#			self._PRW_start_certainty.Disable()
#			self._PRW_duration.Disable()
#			self._DP_discontinued.Disable()
#			return
#
#		self._PRW_substance.display_as_valid(False)

	#----------------------------------------------------------------
	def _on_enter_notes4patient(self):
		dose = self._PRW_substance.GetData(as_instance = True)
		if dose is None:
			self._PRW_patient_notes.unset_context(context = 'substance')
			return
		# do not set to self._PRW_drug.GetValue() as that will contain all
		# sorts of additional info, rather set to the canonical drug['substance']
		self._PRW_patient_notes.set_context(context = 'substance', val = dose['substance'])

	#----------------------------------------------------------------
	def _on_discontinued_date_changed(self, event):
		if self._DP_discontinued.GetData() is None:
			self._PRW_discontinue_reason.Disable()
		else:
			self._PRW_discontinue_reason.Enable()

#	#----------------------------------------------------------------
#	def _on_manage_components_button_pressed(self, event):
#		gmSubstanceMgmtWidgets.manage_drug_components()

#	#----------------------------------------------------------------
#	def _on_manage_substances_button_pressed(self, event):
#		gmSubstanceMgmtWidgets.manage_substances()

#	#----------------------------------------------------------------
#	def _on_manage_drug_products_button_pressed(self, event):
#		gmSubstanceMgmtWidgets.manage_drug_products(parent = self, ignore_OK_button = True)

#	#----------------------------------------------------------------
#	def _on_manage_doses_button_pressed(self, event):
#		gmSubstanceMgmtWidgets.manage_substance_doses(parent = self)

	#----------------------------------------------------------------
	def _on_heart_button_pressed(self, event):
		gmNetworkTools.open_url_in_browser(url = gmMedication.URL_long_qt)

	#----------------------------------------------------------------
	def _on_kidneys_button_pressed(self, event):
		if self._PRW_substance.GetData() is None:
			search_term = self._PRW_substance.GetValue().strip()
		else:
			search_term = self._PRW_substance.GetData(as_instance = True)
		gmNetworkTools.open_url_in_browser(url = gmMedication.drug2renal_insufficiency_url(search_term = search_term))

	#----------------------------------------------------------------
	def _on_discontinued_as_planned_button_pressed(self, event):

		self.__refresh_precautions()
		if self.data is None:
			return

		now = gmDateTime.pydt_now_here()
		# do we have a (full) plan ?
		#if None not in [self.data['started'], self.data['planned_duration']]:
		if self.data['started'] and self.data['planned_duration']:
			planned_end = self.data['started'] + self.data['planned_duration']
			# the plan hasn't ended so [Per plan] can't apply ;-)
			if planned_end > now:
				text = _('Discontinuation in the future (%s + %s -> %s). Not discontinuing.') % (
					self.data['started'].strftime('%x'),
					gmDateTime.format_interval_medically(self.data['planned_duration']),
					planned_end.strftime('%x')
				)
				self.StatusText = text
				return

			self._DP_discontinued.SetData(planned_end)
			self._PRW_discontinue_reason.Enable()
			self._PRW_discontinue_reason.SetValue('')
			return

		# we know started but not duration: apparently the plan is to stop today
		if self.data['started']:
			# but we haven't started yet so we can't stop
			if self.data['started'] > now:
				self.StatusText = _('Not started yet. Cannot discontinue as of today.')
				return

		self._DP_discontinued.SetData(now)
		self._PRW_discontinue_reason.Enable()
		self._PRW_discontinue_reason.SetValue('')

	#----------------------------------------------------------------
	def _on_start_unknown_checked(self, event):
		event.Skip()
		if self._CHBOX_start_unknown.IsChecked() is True:
			self._DP_started.Disable()
			self._PRW_start_certainty.Disable()
		else:
			self._DP_started.Enable()
			self._PRW_start_certainty.Enable()
		self.__refresh_precautions()

	#----------------------------------------------------------------
	def turn_into_allergy(self, data=None):
		if not self.save():
			return False

		return gmAllergyWidgets.turn_substance_intake_into_allergy (
			parent = self,
			intake = self.data,
			emr = gmPerson.gmCurrentPatient().emr
		)

	#----------------------------------------------------------------
	def _on_edit_regimen_button_pressed(self, event):  # wxGlade: wxgSubstanceIntakeEAPnl.<event_handler>
		print("Event handler '_on_edit_regimen_button_pressed' not implemented!")
		event.Skip()

	def _on_delete_regimen_button_pressed(self, event):  # wxGlade: wxgSubstanceIntakeEAPnl.<event_handler>
		print("Event handler '_on_delete_regimen_button_pressed' not implemented!")
		event.Skip()

	def _on_new_regimen_button_pressed(self, event):  # wxGlade: wxgSubstanceIntakeEAPnl.<event_handler>
		print("Event handler '_on_new_regimen_button_pressed' not implemented!")
		event.Skip()

#============================================================
# main
#------------------------------------------------------------
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	from Gnumed.wxpython import gmGuiTest

	#----------------------------------------
	#gmGuiTest.test_widget(cSubstanceIntakeEAPnl)

	frame = gmGuiTest.setup_widget_test_env(patient = 12)
	#manage_substance_intakes()
	#cSubstanceIntakeEAPnl(frame, intake = gmMedication.cSubstanceIntakeEntry(1))
	#cSubstanceIntakeEAPnl(frame)
	#wx.CallLater(4000, edit_intake_of_substance, parent = frame, intake = gmMedication.cSubstanceIntakeEntry(1), single_entry = True)
	wx.CallLater(4000, edit_intake_of_substance, parent = frame, single_entry = True)
	#wx.CallLater(4000, manage_substance_intakes, parent = frame)
	wx.GetApp().MainLoop()
