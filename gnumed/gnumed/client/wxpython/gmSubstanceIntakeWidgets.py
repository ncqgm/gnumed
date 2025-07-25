"""GNUmed substance intake handling widgets."""

#================================================================
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL v2 or later"

import logging
import sys


import wx


if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x
else:
	try:
		_
	except NameError:
		from Gnumed.pycommon import gmI18N
		gmI18N.activate_locale()
		gmI18N.install_domain()

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
def manage_substance_intakes(parent=None, emr=None, include_inactive:bool=True):

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
		return edit_intake_with_regimen(parent = parent, intake_with_regimen = intake, single_entry = True)

	#------------------------------------------------------------
	def delete(intake):
		do_delete = gmGuiHelpers.gm_show_question (
			title = _('Deleting substance intake'),
			question = _('Really delete substance intake ?\n\n%s') % intake.format(single_line = True, terse = False)
		)
		if not do_delete:
			return False

		conn = gmPG2.get_connection(readonly = False)
		result = gmMedication.delete_intake_with_regimen(pk_intake_regimen = intake['pk_intake_regimen'], pk_intake = intake['pk_intake'], link_obj = conn)
		conn.commit()
		return result

	#------------------------------------------------------------
	def get_tooltip(intake_with_regimen=None):
		return intake_with_regimen.format(single_line = False, include_metadata = True)

	#------------------------------------------------------------
	def refresh(lctrl):
		intakes = emr.get_intakes (
			include_inactive = include_inactive,
			exclude_potential_abuses = True,
			order_by = 'substance, discontinued IS DISTINCT FROM NULL, started DESC'
		)
		items = []
		for i in intakes:
			status = '' if i.is_ongoing else ' (%s)' % _('old')
			schedule = ''
			if i['schedule']:
				lines = i['schedule'].split('\n')
				schedule = ': %s' % lines[0].strip()
				if len(lines) > 1:
					schedule += '¹'
			items.append ([
				'%s%s%s%s%s' % (
					i['substance'],
					gmTools.coalesce(i['amount'], '', ' %s'),
					gmTools.coalesce(i['unit'], '', '%s'),
					schedule,
					status
				),
				i.medically_formatted_timerange
			])
		lctrl.set_string_items(items)
		lctrl.set_data(intakes)

	#------------------------------------------------------------
	return gmListWidgets.get_choices_from_list (
		parent = parent,
		caption = _('Substances consumed by the patient'),
		columns = [ _('Intake'), _('Time range')],
		single_selection = False,
		new_callback = edit,
		edit_callback = edit,
		delete_callback = delete,
		refresh_callback = refresh,
		list_tooltip_callback = get_tooltip
#		,left_extra_button = (_('Import'), _('Import consumable substances from a drug database.'), add_from_db)
	)

#------------------------------------------------------------
def edit_intake_with_regimen(parent=None, intake_with_regimen=None, single_entry:bool=False):
	ea = cSubstanceIntakeEAPnl(parent, -1, intake = intake_with_regimen)
	ea.mode = gmTools.coalesce(intake_with_regimen, 'new', 'edit')
	dlg = gmEditArea.cGenericEditAreaDlg2(parent, -1, edit_area = ea, single_entry = True)
	dlg.SetTitle(gmTools.coalesce(intake_with_regimen, _('Adding substance intake'), _('Editing substance intake')))
	dlg.left_extra_button = (
		_('Allergy'),
		_('Document an allergy against this substance.'),
		ea.turn_into_allergy
	)
	dlg.SetSize((700,750))
	if dlg.ShowModal() != wx.ID_OK:
		dlg.DestroyLater()
		return False

	dlg.DestroyLater()
	return True

#------------------------------------------------------------
def delete_intake_with_regimen(parent=None, intake=None):
	msg = _(
		'\n'
		'[%s]\n'
		'\n'
		'It may be prudent to edit (before deletion) the details\n'
		'of this substance intake entry so as to leave behind\n'
		'some indication of why it was deleted.\n'
	) % intake.format(single_line = True)
	dlg = gmGuiHelpers.c3ButtonQuestionDlg (
		parent,
		-1,
		caption = _('Deleting medication'),
		question = msg,
		button_defs = [
			{'label': _('&Edit'), 'tooltip': _('Allow editing of intake before deletion.'), 'default': True},
			{'label': _('&Delete'), 'tooltip': _('Delete immediately without editing first.')},
			{'label': _('&Cancel'), 'tooltip': _('Abort. Do not delete or edit intake.')}
		]
	)
	edit_first = dlg.ShowModal()
	dlg.DestroyLater()
	if edit_first == wx.ID_CANCEL:
		return False

	if edit_first == wx.ID_YES:
		edit_intake_with_regimen(parent = parent, intake_with_regimen = intake)
		delete_it = gmGuiHelpers.gm_show_question (
			question = _('Now delete substance intake entry ?'),
			title = _('Deleting medication / substance intake')
		)
	else:
		delete_it = True
	if not delete_it:
		return False

	conn = gmPG2.get_connection(readonly = False)
	gmMedication.delete_intake_with_regimen(pk_intake = intake['pk_intake'], pk_intake_regimen = intake['pk_intake_regimen'], link_obj = conn)
	conn.commit()
	return True

#============================================================
from Gnumed.wxGladeWidgets import wxgSubstanceIntakeEAPnl

class cSubstanceIntakeEAPnl(wxgSubstanceIntakeEAPnl.wxgSubstanceIntakeEAPnl, gmEditArea.cGenericEditAreaMixin):
	"""Enter or edit intake with regimen of a substance."""
	def __init__(self, *args, **kwargs):
		try:
			data = kwargs['intake']
			del kwargs['intake']
			assert ((data is None) or isinstance(data, gmMedication.cIntakeWithRegimen)), '<intake> must be of type "gmMedication.cIntakeWithRegimen" if given'

		except KeyError:
			data = None

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
		self._PRW_substance.add_callback_on_selection(callback = self._on_substance_selected)
		#self._PRW_duration.display_accuracy = gmDateTime.ACC_DAYS
		self._DPRW_discontinued.add_callback_on_selection(callback = self._on_discontinued_date_changed)
		self._LCTRL_regimen.set_resize_column()
		#self._LCTRL_regimen.set_column_widths([wx.LIST_AUTOSIZE])
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
			confirmed = state['last_confirmed'].strftime('%Y %b %d')
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
			tt_lines.extend(abuse.format(single_line = False, eol = None))
			tt_lines.append('')
			if abuse['use_type'] in [gmMedication.USE_TYPE_MEDICATION, gmMedication.USE_TYPE_NON_HARMFUL]:
				continue
			msg_lines.append(abuse.format(single_line = True))
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
					tt_lines.extend(egfr.format (
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
				gfr['clin_when'].strftime('%Y %b %d')
			))
			tt_lines.append(_('GFR reported by path lab'))

		# pregnancy
		edc = emr.EDC
		if edc:
			msg_lines.append('')
			msg_lines.append('')
			if emr.EDC_is_fishy:
				msg_lines.append(_('EDC (!?!): %s') % edc.strftime('%Y %b %d'))
				tt_lines.append(_(
					'The Expected Date of Confinement is rather questionable.\n'
					'\n'
					'Please check patient age, patient gender, time until/since EDC.'
				))
			else:
				msg_lines.append(_('EDC: %s') % edc.strftime('%Y %b %d'))
		self._LBL_information.SetLabel('\n'.join(msg_lines))
		self._LBL_information.SetToolTip('\n'.join(tt_lines))
		self.Layout()

	#----------------------------------------------------------------
	def __refresh_regimens(self):
		if not self._PRW_substance.GetData():
			self._LCTRL_regimen.set_string_items()
			return

		pk_subst, pk_dose = self._PRW_substance.GetData()
		items = []
		data = []
		intakes = gmMedication.get_intakes_with_regimens (
			pk_patient = gmPerson.gmCurrentPatient().ID,
			pk_substance = pk_subst,
			include_inactive = True,
			order_by = 'discontinued IS DISTINCT FROM NULL, started DESC'
		)
		for regimen in intakes:
			if regimen['discontinued']:
				tag = _('old')
			else:
				tag = _('active')
			items.append('%s: %s' % (tag, regimen.format(single_line = True)))
			data.append(regimen)
		self._LCTRL_regimen.set_columns([_('Existing treatment regimens for %s') % self._PRW_substance.Value])
		self._LCTRL_regimen.set_string_items(items)
		self._LCTRL_regimen.set_data(data)
		self._LCTRL_regimen.set_column_widths()

	#----------------------------------------------------------------
	# internal halpers
	#----------------------------------------------------------------
	def __validate_amount_and_unit(self, dose=None) -> bool:
		amount = self._TCTRL_amount.Value.strip()
		unit = self._PRW_unit.Value.strip()
		if not unit:
			self.StatusText = _('Required: unit.')
			self._PRW_unit.display_as_valid(False)
			self._PRW_unit.SetFocus()
		if not amount:
			self.StatusText = _('Required: amount.')
			self._TCTRL_amount.display_as_valid(False)
			self._TCTRL_amount.SetFocus()
		if not amount or not unit:
			return False

		self._PRW_unit.display_as_valid()
		amount_is_num, amount = gmTools.input2decimal(amount)
		if not amount_is_num:
			self.StatusText = _('Amount: must be a number.')
			self._TCTRL_amount.display_as_valid(False)
			self._TCTRL_amount.SetFocus()
			return False

		if not amount > 0:
			self.StatusText = _('Amount: must be larger than zero.')
			self._TCTRL_amount.display_as_valid(False)
			self._TCTRL_amount.SetFocus()
			return False

		self._TCTRL_amount.display_as_valid()
		return True

	#----------------------------------------------------------------
	def __validate_schedule(self) -> bool:
		if self._TCTRL_schedule.Value.strip() == '':
			self.StatusText = _('Required: schedule')
			self._TCTRL_schedule.display_as_valid(False)
			self._TCTRL_schedule.SetFocus()
			return False

		# any schedule is fine
		self._TCTRL_schedule.display_as_valid()
		return True

	#----------------------------------------------------------------
	def __validate_start(self) -> bool:
		if self._CHBOX_start_unknown.IsChecked():
			return True

		if self._DPRW_started.date:
			return True

		self.StatusText = _('Required: start of intake (you may select [Unknown]')
		self._DPRW_started.display_as_valid(False)
		self._DPRW_started.SetFocus()
		return False

	#----------------------------------------------------------------
	def __validate_discontinued(self, started) -> bool:
		"""discontinued: must be "< now()" AND "> started" if at all"""
		discontinued = self._DPRW_discontinued.GetData()
		if not discontinued:
			self._DPRW_discontinued.display_as_valid()
			return True

		now = gmDateTime.pydt_now_here().replace(hour = 23, minute = 59, second = 59, microsecond = 111111)
		if discontinued > now:
			self.StatusText = _('Discontinued (%s) in the future (now: %s)') % (discontinued, now)
			self._DPRW_discontinued.display_as_valid(False)
			self._DPRW_discontinued.SetFocus()
			return False

		if not started:
			self._DPRW_discontinued.display_as_valid()
			return True

		started = started.replace(hour = 0, minute = 0, second = 0, microsecond = 1)
		if started > discontinued:
			self.StatusText = _('Discontinued (%s) before started (%s)') % (discontinued, started)
			self._DPRW_started.display_as_valid(False)
			self._DPRW_discontinued.display_as_valid(False)
			self._DPRW_discontinued.SetFocus()
			return False

		self._DPRW_discontinued.display_as_valid()
		return True

	#----------------------------------------------------------------
#	def _validate_duration(self) -> bool:
#		if self._PRW_duration.GetValue().strip() in ['', gmTools.u_infinity]:
#			self._PRW_duration.display_as_valid()
#			return True
#
#		if self._PRW_duration.GetData():
#			self._PRW_duration.display_as_valid()
#			return True
#
#		# no data ...
#		if gmDateTime.str2interval(self._PRW_duration.GetValue()):
#			self._PRW_duration.display_as_valid()
#			return True
#
#		self.StatusText = _('Duration: must be an interval')
#		self._PRW_duration.display_as_valid(False)
#		self._PRW_duration.SetFocus()
#		return False

	#----------------------------------------------------------------
	def __validate_episode_for_update(self) -> bool:
		pk_epi = self._PRW_episode.GetData(as_instance = False)
		if not pk_epi:
			self.StatusText = _('Required: episode')
			self._PRW_episode.display_as_valid(False)
			self._PRW_episode.SetFocus()
			return False

		self._PRW_episode.display_as_valid()
		return True

	#----------------------------------------------------------------
	def __validate_substance_for_new_intake(self) -> bool:
		entered_subst = self._PRW_substance.Value.strip()
		if not entered_subst:
			self.StatusText = _('Required: substance')
			self._PRW_substance.display_as_valid(False)
			self._PRW_substance.SetFocus()
			return False

		if not gmPerson.gmCurrentPatient().emr.substance_intake_exists(substance = entered_subst):
			self._PRW_substance.display_as_valid()
			return True

		if not self._a_regimen_field_is_filled_in():
			self.StatusText = _('Patient already takes/took "%s". You may add a new regimen though.') % entered_subst
			self._PRW_substance.display_as_valid(False)
			self._PRW_substance.SetFocus()
			return False

		if not self.__validate_regimen_fields():
			self._PRW_substance.display_as_valid(False)
			return False

		return True

	#----------------------------------------------------------------
	def _a_regimen_field_is_filled_in(self) -> bool:
		if self._TCTRL_amount.Value.strip() != '':
			return True

		if self._PRW_unit.Value.strip() != '':
			return True

		if self._TCTRL_schedule.Value.strip() != '':
			return True

		if self._TCTRL_comment_on_start.Value.strip() != '':
			return True

		if self._DPRW_started.Value.strip() != '':
			return True

		if self._DPRW_discontinued.Value.strip() != '':
			return True

		if self._TCTRL_discontinue_reason.Value.strip() != '':
			return True

		return False

	#----------------------------------------------------------------
	def __validate_regimen_fields(self) -> bool:
		is_valid = self.__validate_amount_and_unit()
		is_valid = is_valid and self.__validate_schedule()
		is_valid = is_valid and self.__validate_start()
		is_valid = is_valid and self.__validate_discontinued(self._DPRW_started.date)
		return is_valid

	#----------------------------------------------------------------
	def _valid_for_save(self) -> bool:
		self.StatusText = ''
		if self.mode == 'new':
			is_valid = self.__validate_substance_for_new_intake()
			if self._a_regimen_field_is_filled_in():
				is_valid = is_valid and self.__validate_regimen_fields()
			return is_valid

		# edit of existing intake, mode = 'edit'
		is_valid = self.__validate_episode_for_update()
		# intake with existing regimen
		if self.data['pk_intake_regimen']:
			# must have regimen data; removal of existing regimen not allowed
			is_valid = is_valid and self.__validate_regimen_fields()
			return is_valid

		# intake without a regimen so far: need not have regimen data
		if self._a_regimen_field_is_filled_in():
			is_valid = is_valid and self.__validate_regimen_fields()
		return is_valid

	#----------------------------------------------------------------
	# generic Edit Area mixin API
	#----------------------------------------------------------------
	def _save_as_new(self) -> bool:
		conn4tx = gmPG2.get_connection(readonly = False)
		pk_epi = self._PRW_episode.GetData(as_instance = False, link_obj = conn4tx)
		if pk_epi is None:
			if self._PRW_episode.Value.strip() == '':
				self._PRW_episode.SetValue(gmMedication.DEFAULT_MEDICATION_HISTORY_EPISODE)
				is_open = False
			else:
				is_open = True		# Jim wants new episode to auto-open
			pk_epi = self._PRW_episode.GetData (
				can_create = True,
				is_open = is_open,
				as_instance = False,
				link_obj = conn4tx
			)
		pk_subst, pk_dose = self._PRW_substance.GetData(as_instance = False, can_create = True, link_obj = conn4tx)
		pat_notes = []
		if self._TCTRL_patient_notes.Value.strip():
			pat_notes.append(self._TCTRL_patient_notes.Value.strip())
		doc_notes = []
		if self._TCTRL_patient_notes.Value.strip():
			doc_notes.append(self._TCTRL_patient_notes.Value.strip())
		our_notes = []
		if self._TCTRL_our_notes.Value.strip():
			our_notes.append(self._TCTRL_our_notes.Value.strip())
		intakes = gmMedication.get_substance_intakes (
			pk_patient = gmPerson.gmCurrentPatient().ID,
			return_pks = False,
			pk_substances = [pk_subst]
		)
		if intakes:
			intake = intakes[0]
			if intake['notes4patient']:
				pat_notes.append(intake['notes4patient'])
			if intake['notes4provider']:
				doc_notes.append(intake['notes4provider'])
			if intake['notes4us']:
				our_notes.append(intake['notes4us'])
		else:
			intake = gmMedication.create_substance_intake (
				pk_encounter = gmPerson.gmCurrentPatient().emr.current_encounter['pk_encounter'],
				pk_episode = pk_epi,
				pk_substance = pk_subst,
				link_obj = conn4tx
			)
		intake['notes4patient'] = '\n'.join(pat_notes)
		intake['notes4provider'] = '\n'.join(doc_notes)
		intake['notes4us'] = '\n'.join(our_notes)
		if self._TCTRL_schedule.Value.strip() == '':
			# no schedule means there cannot be regimen data because of prior validation
			intake['pk_episode'] = pk_epi
			intake.save(conn = conn4tx)
			conn4tx.commit()
			conn4tx.close()
			data = gmMedication.cIntakeWithRegimen(aPK_obj = {
				'pk_intake': intake['pk_intake'],
				'pk_intake_regimen': None
			})
			self.data = data
			return True

		intake.save(conn = conn4tx)
		if self._CHBOX_start_unknown.IsChecked():
			started = gmDateTime.pydt_now_here()
		else:
			started = self._DPRW_started.date
		amount_is_num, amount = gmTools.input2decimal(self._TCTRL_amount.Value.strip())
		regimen = gmMedication.create_intake_regimen (
			pk_intake = intake['pk_intake'],
			started = started,
			pk_encounter = intake['pk_encounter'],
			pk_episode = intake['pk_episode'],
			schedule = self._TCTRL_schedule.Value.strip(),
			amount = amount,
			unit = self._PRW_unit.Value.strip(),
			discontinued = self._DPRW_discontinued.date,
			link_obj = conn4tx
		)
		regimen['start_is_unknown'] = self._CHBOX_start_unknown.IsChecked()
		regimen['comment_on_start'] = self._TCTRL_comment_on_start.Value.strip()
		if regimen['discontinued']:
			regimen['discontinue_reason'] = self._TCTRL_discontinue_reason.Value.strip()
#		if self._PRW_duration.Value.strip() in ['', gmTools.u_infinity]:
#			regimen['planned_duration'] = None
#		else:
#			if self._PRW_duration.GetData():
#				regimen['planned_duration'] = self._PRW_duration.GetData()
#			else:
#				regimen['planned_duration'] = gmDateTime.str2interval(self._PRW_duration.Value.strip())
		regimen.save(conn = conn4tx)
		conn4tx.commit()
		conn4tx.close()
		data = gmMedication.cIntakeWithRegimen(aPK_obj = {
			'pk_intake': regimen['pk_intake'],
			'pk_intake_regimen': regimen['pk_intake_regimen']
		})
		self.data = data
		return True

	#----------------------------------------------------------------
	def _save_as_update(self):
		conn4tx = gmPG2.get_connection(readonly = False)
		# intake fields
		pk_epi = self._PRW_episode.GetData(as_instance = False, link_obj = conn4tx)
		self.data['pk_episode'] = pk_epi
		self.data['notes4patient'] = self._TCTRL_patient_notes.Value.strip()
		self.data['notes4provider'] = self._TCTRL_provider_notes.Value.strip()
		self.data['notes4us'] = self._TCTRL_our_notes.Value.strip()

		# no regimen fields
		if not self._a_regimen_field_is_filled_in():
			# should not happen due to prior validation
			if self.data['pk_intake_regimen']:
				conn4tx.rollback()
				conn4tx.close()
				return False

			# intake w/o regimen
			if not self.data['pk_intake_regimen']:
				self.data.save(conn = conn4tx)
				conn4tx.commit()
				conn4tx.close()
				return True

		# regimen fields
		comment = self._TCTRL_comment_on_start.Value.strip()
		if self._CHBOX_start_unknown.IsChecked():
			started = gmDateTime.pydt_now_here()
		else:
			started = self._DPRW_started.date
		if not self.data['pk_intake_regimen']:
			self.data.save(conn = conn4tx)
			# no regimen as yet
			amount_is_num, amount = gmTools.input2decimal(self._TCTRL_amount.Value.strip())
			regimen = gmMedication.create_intake_regimen (
				pk_intake = self.data['pk_intake'],
				started = started,
				pk_encounter = self.data['pk_encounter'],
				pk_episode = pk_epi,
				schedule = self._TCTRL_schedule.Value.strip(),
				amount = amount,
				unit = self._PRW_unit.Value.strip(),
				discontinued = self._DPRW_discontinued.date,
				link_obj = conn4tx
			)
			regimen['start_is_unknown'] = self._CHBOX_start_unknown.IsChecked()
			regimen['comment_on_start'] = comment
			regimen['discontinued'] = self._DPRW_discontinued.date
			regimen['discontinue_reason'] = self._TCTRL_discontinue_reason.Value.strip()
			#regimen['planned_duration'] = self._PRW_duration.GetData()
			regimen.save(conn = conn4tx)
			conn4tx.commit()
			conn4tx.close()
			data = gmMedication.cIntakeWithRegimen(aPK_obj = {
				'pk_intake': regimen['pk_intake'],
				'pk_intake_regimen': regimen['pk_intake_regimen']
			})
			self.data = data
			return True

		# existing regimen
		self.data['started'] = started
		self.data['start_is_unknown'] = self._CHBOX_start_unknown.IsChecked()
		self.data['comment_on_start'] = comment
		self.data['discontinued'] = self._DPRW_discontinued.date
		self.data['discontinue_reason'] = self._TCTRL_discontinue_reason.Value.strip()
#		if self._PRW_duration.Value.strip() in ['', gmTools.u_infinity]:
#			regimen['planned_duration'] = None
#		else:
#			if self._PRW_duration.GetData():
#				regimen['planned_duration'] = self._PRW_duration.GetData()
#			else:
#				regimen['planned_duration'] = gmDateTime.str2interval(self._PRW_duration.Value.strip())
		self.data.save(conn = conn4tx)
		conn4tx.commit()
		conn4tx.close()
		return True

	#----------------------------------------------------------------
	def _refresh_as_new(self):
		self._PRW_substance.SetText('', None)
		self._PRW_substance.Enable()
		self._PRW_episode.SetText('', None)
		self._TCTRL_patient_notes.Value = ''
		self._TCTRL_provider_notes.Value = ''
		self._TCTRL_our_notes.Value = ''
		# regimen fields
		self._TCTRL_amount.SetValue('')
		self._TCTRL_amount.Enable()
		self._PRW_unit.SetValue('')
		self._PRW_unit.Enable()
		self._TCTRL_schedule.Value = ''
		self._TCTRL_schedule.Enable()
		self._TCTRL_comment_on_start.Value = ''
#		self._PRW_duration.SetText('', None)
#		self._PRW_duration.Disable()
		self._DPRW_discontinued.SetData(None)
		self._TCTRL_discontinue_reason.SetValue('')
		self._TCTRL_discontinue_reason.Disable()
		self.__refresh_regimens()
		self.__refresh_precautions()
		self._PRW_substance.SetFocus()

	#----------------------------------------------------------------
	def _refresh_from_existing(self):
		assert isinstance(self.data, gmMedication.cIntakeWithRegimen), '<intake> must be of type "gmMedication.cIntakeWithRegimen" if given'

		self._refresh_as_new()
		self._PRW_substance.SetText (
			value = self.data['substance'],
			data = [self.data['pk_substance'], None]
		)
		self._PRW_substance.Disable()
		self._PRW_episode.SetData(self.data['pk_episode'])
		self._TCTRL_patient_notes.Value = gmTools.coalesce(self.data['notes4patient'], '')
		self._TCTRL_provider_notes.Value = gmTools.coalesce(self.data['notes4provider'], '')
		self._TCTRL_our_notes.Value = gmTools.coalesce(self.data['notes4us'], '')
		if self.data['pk_intake_regimen']:
			self._TCTRL_amount.Value = str(self.data['amount'])
			self._TCTRL_amount.Disable()
			self._PRW_unit.SetText(value = self.data['unit'], data = self.data['unit'])
			self._PRW_unit.Disable()
			self._TCTRL_schedule.Value = self.data['schedule']
			self._TCTRL_schedule.Disable()
			self._DPRW_started.SetText(data = self.data['started'])
			self._TCTRL_comment_on_start.Value = gmTools.coalesce(self.data['comment_on_start'], '')
			if self.data['start_is_unknown']:
				self._CHBOX_start_unknown.Value = True
				self._DPRW_started.Disable()
			else:
				self._CHBOX_start_unknown.Value = False
				self._DPRW_started.Enable()
			if self.data['discontinued']:
				self._DPRW_discontinued.SetData(data = self.data['discontinued'])
				self._TCTRL_discontinue_reason.Value = gmTools.coalesce(self.data['discontinue_reason'], '')
				self._TCTRL_discontinue_reason.Enable()
		else:
			self._TCTRL_amount.Enable()
			self._PRW_unit.Enable()
			self._TCTRL_schedule.Enable()
			self._CHBOX_start_unknown.Value = True
			self._DPRW_started.Disable()
			self._DPRW_discontinued.SetData(None)
			self._TCTRL_discontinue_reason.Value = ''
		self.__refresh_regimens()
		self.__refresh_precautions()
		self._TCTRL_patient_notes.SetFocus()

	#----------------------------------------------------------------
	def _refresh_as_new_from_existing(self):
		self._refresh_as_new()
		self._PRW_episode.SetData(self.data['pk_episode'])
		self._PRW_substance.SetFocus()

	#----------------------------------------------------------------
	# event handlers
	#----------------------------------------------------------------
	def _on_leave_substance(self):
		self.__refresh_regimens()
		if self.mode == 'edit':
			# nothing to do
			return

		entered_substance = self._PRW_substance.Value.strip()
		if not entered_substance:
			self._PRW_substance.display_as_valid(False)
			self.StatusText = _('Substance required.')
			return

		self._PRW_substance.display_as_valid()
		self.StatusText = ''
		pks_subst = gmMedication.get_substances(return_pks = True, substance = entered_substance)
		if not pks_subst:
			# new substance, patient *can not* have intake yet
			return

		intakes = gmMedication.get_substance_intakes (
			pk_patient = gmPerson.gmCurrentPatient().ID,
			pk_substances = pks_subst
		)
		if not intakes:
			# no intakes documented
			return

		self._PRW_substance.display_as_valid(False)
		self.StatusText = _('Intake of %s already documented. You may add a new regimen though') % entered_substance
		return

	#----------------------------------------------------------------
	def _on_substance_selected(self, substance):
		self.__refresh_regimens()
		if not substance:
			return

		if self.mode != 'new':
			return

		pk_subst, pk_dose = self._PRW_substance.GetData()
		if not pk_subst:
			self._PRW_substance.display_as_valid(False)
			return

		if pk_dose:
			subst, dose = self._PRW_substance.GetData(as_instance = True)
			self._TCTRL_amount.Value = str(dose['amount'])
			self._PRW_unit.Value = dose['unit']

	#----------------------------------------------------------------
	def _on_started_today_button_pressed(self, event):
		self._DPRW_started.SetText(data = gmDateTime.pydt_now_here())
		self._DPRW_started.Enable()
		self._CHBOX_start_unknown.Value = False

	#----------------------------------------------------------------
	def _on_start_unknown_checkbox_toggled(self, event):
		if self._CHBOX_start_unknown.IsChecked():
			self._DPRW_started.Disable()
		else:
			self._DPRW_started.Enable()

	#----------------------------------------------------------------
	def _on_discontinued_today_button_pressed(self, event):
		self._DPRW_discontinued.SetText(data = gmDateTime.pydt_now_here())
		self._TCTRL_discontinue_reason.Enable()

	#----------------------------------------------------------------
	def _on_discontinued_date_changed(self, event):
		if self._DPRW_discontinued.date:
			self._TCTRL_discontinue_reason.Enable()
		else:
			self._TCTRL_discontinue_reason.Disable()

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
	def _on_pregnancy_button_pressed(self, event):
		subst, dose = self._PRW_substance.GetData(as_instance = True)
		if not subst:
			subst = self._PRW_substance.Value.strip()
		urls = gmMedication.generate_pregnancy_information_urls(search_term = subst)
		gmNetworkTools.open_urls_in_browser(urls = urls)

	#----------------------------------------------------------------
	def _on_lungs_button_pressed(self, event):
		subst, dose = self._PRW_substance.GetData(as_instance = True)
		if not subst:
			subst = self._PRW_substance.Value.strip()
		urls = gmMedication.generate_pulmonary_information_urls(search_term = subst)
		gmNetworkTools.open_urls_in_browser(urls = urls)

	#----------------------------------------------------------------
	def _on_heart_button_pressed(self, event):
		gmNetworkTools.open_url_in_browser(url = gmMedication.URL_long_qt)

	#----------------------------------------------------------------
	def _on_kidneys_button_pressed(self, event):
		subst, dose = self._PRW_substance.GetData(as_instance = True)
		if not subst:
			subst = self._PRW_substance.Value.strip()
		gmNetworkTools.open_urls_in_browser(urls = gmMedication.generate_renal_insufficiency_urls(search_term = subst))

#	#----------------------------------------------------------------
#	def _on_discontinued_as_planned_button_pressed(self, event):
#
#		self.__refresh_precautions()
#		if self.data is None:
#			return
#
#		now = gmDateTime.pydt_now_here()
#		# do we have a (full) plan ?
#		#if None not in [self.data['started'], self.data['planned_duration']]:
#		if self.data['started'] and self.data['planned_duration']:
#			planned_end = self.data['started'] + self.data['planned_duration']
#			# the plan hasn't ended so [Per plan] can't apply ;-)
#			if planned_end > now:
#				text = _('Discontinuation in the future (%s + %s -> %s). Not discontinuing.') % (
#					self.data['started'].strftime('%x'),
#					gmDateTime.format_interval_medically(self.data['planned_duration']),
#					planned_end.strftime('%x')
#				)
#				self.StatusText = text
#				return
#
#			self._DPRW_discontinued.SetData(planned_end)
#			self._TCTRL_discontinue_reason.Enable()
#			self._TCTRL_discontinue_reason.SetValue('')
#			return
#
#		# we know started but not duration: apparently the plan is to stop today
#		if self.data['started']:
#			# but we haven't started yet so we can't stop
#			if self.data['started'] > now:
#				self.StatusText = _('Not started yet. Cannot discontinue as of today.')
#				return
#
#		self._DPRW_discontinued.SetData(now)
#		self._TCTRL_discontinue_reason.Enable()
#		self._TCTRL_discontinue_reason.SetValue('')

	#----------------------------------------------------------------
	def turn_into_allergy(self, data=None):
		if not self.save():
			return False

		return gmAllergyWidgets.turn_substance_intake_into_allergy (
			parent = self,
			intake = self.data,
			emr = gmPerson.gmCurrentPatient().emr
		)

#============================================================
# main
#------------------------------------------------------------
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	del _
	from Gnumed.pycommon import gmI18N
	gmI18N.activate_locale()
	gmI18N.install_domain('gnumed')

	from Gnumed.wxpython import gmGuiTest
	#----------------------------------------
	def test_substance_intake_ea_pnl():
		gmGuiTest.test_widget(cSubstanceIntakeEAPnl, patient = -1)

	#----------------------------------------
	def test_edit_intake_with_regimen():
		frame = gmGuiTest.setup_widget_test_env(patient = 12)
		wx.CallLater(2000, edit_intake_with_regimen, parent = frame, single_entry = True)
		wx.GetApp().MainLoop()

	#----------------------------------------
	def test_manage_substance_intakes():
		frame = gmGuiTest.setup_widget_test_env(patient = 12)
		wx.CallLater(2000, manage_substance_intakes, parent = frame)
		wx.GetApp().MainLoop()

	#----------------------------------------
	#test_substance_intake_ea_pnl()
	#test_edit_intake_with_regimen()
	test_manage_substance_intakes()

	#frame = gmGuiTest.setup_widget_test_env(patient = 12)
	#manage_substance_intakes()
	#cSubstanceIntakeEAPnl(frame, intake = gmMedication.cSubstanceIntakeEntry(1))
	#cSubstanceIntakeEAPnl(frame)
	#wx.CallLater(4000, edit_intake_with_regimen, parent = frame, intake = gmMedication.cSubstanceIntakeEntry(1), single_entry = True)
	#wx.GetApp().MainLoop()
