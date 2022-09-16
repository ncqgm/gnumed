"""GNUmed medication handling widgets."""

#================================================================
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL v2 or later"

import logging
import sys
import urllib
import datetime as pydt


import wx
import wx.grid


if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x

from Gnumed.pycommon import gmDispatcher
from Gnumed.pycommon import gmCfgDB
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmDateTime
from Gnumed.pycommon import gmMatchProvider
from Gnumed.pycommon import gmNetworkTools

from Gnumed.business import gmPerson
from Gnumed.business import gmPraxis
from Gnumed.business import gmMedication
from Gnumed.business import gmForms
from Gnumed.business import gmStaff
from Gnumed.business import gmLOINC
from Gnumed.business import gmClinicalCalculator
from Gnumed.business import gmPathLab

from Gnumed.wxpython import gmGuiHelpers
from Gnumed.wxpython import gmRegetMixin
from Gnumed.wxpython import gmEditArea
from Gnumed.wxpython import gmCfgWidgets
from Gnumed.wxpython import gmListWidgets
from Gnumed.wxpython import gmPhraseWheel
from Gnumed.wxpython import gmFormWidgets
from Gnumed.wxpython import gmAllergyWidgets
from Gnumed.wxpython import gmSubstanceMgmtWidgets


_log = logging.getLogger('gm.ui')

#============================================================
# perhaps leave this here:
#============================================================
class cSubstancePreparationPhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):

		query = """
SELECT DISTINCT ON (list_label)
	preparation AS data,
	preparation AS list_label,
	preparation AS field_label
FROM ref.drug_product
WHERE preparation %(fragment_condition)s
ORDER BY list_label
LIMIT 30"""
		mp = gmMatchProvider.cMatchProvider_SQL2(queries = query)
		mp.setThresholds(1, 2, 4)
		gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)
		self.SetToolTip(_('The preparation (form) of the substance or product.'))
		self.matcher = mp
		self.selection_only = False

#============================================================
# current substance intake widgets
#------------------------------------------------------------
class cSubstanceIntakeObjectPhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):
		mp = gmMedication.cSubstanceIntakeObjectMatchProvider()
		mp.setThresholds(1, 2, 4)
		gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)
		self.SetToolTip(_('A drug product.'))
		self.matcher = mp
		self.selection_only = True
		self.phrase_separators = None

	#--------------------------------------------------------
	def _data2instance(self):
		pk = self.GetData(as_instance = False, can_create = False)
		if pk is None:
			return None
		return gmMedication.cDrugProduct(aPK_obj = pk)

#------------------------------------------------------------
class cProductOrSubstancePhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):

		mp = gmMedication.cProductOrSubstanceMatchProvider()
		mp.setThresholds(1, 2, 4)
		gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)
		self.SetToolTip(_('A substance with optional strength or a drug product.'))
		self.matcher = mp
		self.selection_only = False
		self.phrase_separators = None
		self.IS_PRODUCT = 1
		self.IS_SUBSTANCE = 2
		self.IS_COMPONENT = 3

	#--------------------------------------------------------
	def _data2instance(self):
		entry_type, pk = self.GetData(as_instance = False, can_create = False)
		if entry_type == 1:
			return gmMedication.cDrugProduct(aPK_obj = pk)
		if entry_type == 2:
			return gmMedication.cConsumableSubstance(aPK_obj = pk)
		if entry_type == 3:
			return gmMedication.cDrugComponent(aPK_obj = pk)
		raise ValueError('entry type must be 1=drug product or 2=substance or 3=component')

#============================================================
class cSubstanceSchedulePhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):

		query = """
			SELECT DISTINCT ON (sched)
				schedule as sched,
				schedule
			FROM clin.substance_intake
			WHERE schedule %(fragment_condition)s
			ORDER BY sched
			LIMIT 50"""

		mp = gmMatchProvider.cMatchProvider_SQL2(queries = query)
		mp.setThresholds(1, 2, 4)
		mp.word_separators = '[ \t=+&:@]+'
		gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)
		self.SetToolTip(_('The schedule for taking this substance.'))
		self.matcher = mp
		self.selection_only = False

#============================================================
class cSubstanceAimPhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):

		query = """
(
	SELECT DISTINCT ON (field_label)
		aim
			AS data,
		aim || ' (' || substance || ' ' || amount || ' ' || unit || ')'
			AS list_label,
		aim
			AS field_label
	FROM clin.v_intakes
	WHERE
		aim %(fragment_condition)s
		%(ctxt_substance)s
) UNION (
	SELECT DISTINCT ON (field_label)
		aim
			AS data,
		aim || ' (' || substance || ' ' || amount || ' ' || unit || ')'
			AS list_label,
		aim
			AS field_label
	FROM clin.v_intakes
	WHERE
		aim %(fragment_condition)s
)
ORDER BY list_label
LIMIT 30"""

		context = {'ctxt_substance': {
			'where_part': 'AND substance = %(substance)s',
			'placeholder': 'substance'
		}}

		mp = gmMatchProvider.cMatchProvider_SQL2(queries = query, context = context)
		mp.setThresholds(1, 2, 4)
		#mp.word_separators = '[ \t=+&:@]+'
		gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)
		self.SetToolTip(_('The medical aim for consuming this substance.'))
		self.matcher = mp
		self.selection_only = False

#============================================================
def turn_substance_intake_into_allergy(parent=None, intake=None, emr=None):

	if intake['is_currently_active']:
		intake['discontinued'] = gmDateTime.pydt_now_here()
	if intake['discontinue_reason'] is None:
		intake['discontinue_reason'] = '%s %s' % (_('not tolerated:'), _('discontinued due to allergy or intolerance'))
	else:
		if not intake['discontinue_reason'].startswith(_('not tolerated:')):
			intake['discontinue_reason'] = '%s %s' % (_('not tolerated:'), intake['discontinue_reason'])
	if not intake.save():
		return False

	intake.turn_into_allergy(encounter_id = emr.active_encounter['pk_encounter'])
	drug = intake.containing_drug
	comps = [ c['substance'] for c in drug.components ]
	if len(comps) > 1:
		gmGuiHelpers.gm_show_info (
			aTitle = _('Documented an allergy'),
			aMessage = _(
				'An allergy was documented against the substance:\n'
				'\n'
				'  [%s]\n'
				'\n'
				'This substance was taken with the multi-component drug product:\n'
				'\n'
				'  [%s (%s)]\n'
				'\n'
				'Note that ALL components of this product were discontinued.'
			) % (
				intake['substance'],
				intake['drug_product'],
				' & '.join(comps)
			)
		)
	if parent is None:
		parent = wx.GetApp().GetTopWindow()
	dlg = gmAllergyWidgets.cAllergyManagerDlg(parent, -1)
	dlg.ShowModal()
	return True

#============================================================
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
#	#------------------------------------------------------------
#	def edit(substance=None):
#		return gmSubstanceMgmtWidgets.edit_substance(parent = parent, substance = substance, single_entry = (substance is not None))
#	#------------------------------------------------------------
#	def delete(substance):
#		if substance.is_in_use_by_patients:
#			gmDispatcher.send(signal = 'statustext', msg = _('Cannot delete this substance. It is in use.'), beep = True)
#			return False
#
#		xxxxx -> substance_dose
#		return gmMedication.delete_xsubstance(substance = substance['pk'])
	#------------------------------------------------------------
	def get_tooltip(intake=None):
		return intake.format(single_line = False, show_all_product_components = True)
	#------------------------------------------------------------
	def refresh(lctrl):
		intakes = emr.get_current_medications (
			include_inactive = False,
			order_by = 'substance, product, started'
		)
		items = []
		for i in intakes:
			started = i.medically_formatted_start
			items.append ([
				'%s%s %s %s %s %s' % (
					i['substance'],
					gmTools.coalesce(i['drug_product'], '', ' (%s)'),
					i['amount'],
					i['unit'],
					i['l10n_preparation'],
					gmTools.coalesce(i['external_code_product'], '', ' [%s::%s]' % (i['external_code_type_product'], i['external_code_product']))
				),
				'%s%s%s' % (
					started,
					gmTools.coalesce(i['schedule'], '', ' %%s %s' % gmTools.u_arrow2right),
					gmTools.coalesce(i['planned_duration'], '', ' %s')
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
#		new_callback = edit,
#		edit_callback = edit,
#		delete_callback = delete,
		refresh_callback = refresh,
		list_tooltip_callback = get_tooltip
#		,left_extra_button = (_('Import'), _('Import consumable substances from a drug database.'), add_from_db)
	)

#============================================================
from Gnumed.wxGladeWidgets import wxgCurrentMedicationEAPnl

class cSubstanceIntakeEAPnl(wxgCurrentMedicationEAPnl.wxgCurrentMedicationEAPnl, gmEditArea.cGenericEditAreaMixin):

	def __init__(self, *args, **kwargs):

		try:
			data = kwargs['substance']
			del kwargs['substance']
		except KeyError:
			data = None

		self.calc = gmClinicalCalculator.cClinicalCalculator()

		wxgCurrentMedicationEAPnl.wxgCurrentMedicationEAPnl.__init__(self, *args, **kwargs)
		gmEditArea.cGenericEditAreaMixin.__init__(self)

		self.mode = 'new'
		self.data = data
		if data is not None:
			self.mode = 'edit'

		self.__init_ui()

	#----------------------------------------------------------------
	def __init_ui(self):

		self._PRW_drug.add_callback_on_lose_focus(callback = self._on_leave_drug)
		self._PRW_drug.selection_only = True

		self._PRW_duration.display_accuracy = gmDateTime.acc_days

		# this we want to adjust later
		self._PRW_aim.add_callback_on_set_focus(callback = self._on_enter_aim)

		self._DP_discontinued.add_callback_on_selection(callback = self._on_discontinued_date_changed)

	#----------------------------------------------------------------
	def __refresh_precautions(self):

		curr_pat = gmPerson.gmCurrentPatient()
		emr = curr_pat.emr

		# allergies
		state = emr.allergy_state
		if state['last_confirmed'] is None:
			confirmed = _('never')
		else:
			confirmed = gmDateTime.pydt_strftime(state['last_confirmed'], '%Y %b %d')
		msg = _('%s, last confirmed %s\n') % (state.state_string, confirmed)
		msg += gmTools.coalesce(state['comment'], '', _('Comment (%s): %%s\n') % state['modified_by'])
		tooltip = ''
		allgs = emr.get_allergies()
		if len(allgs) > 0:
			msg += '\n'
		for allergy in allgs:
			msg += '%s: %s (%s)\n' % (
				allergy['descriptor'],
				allergy['l10n_type'],
				gmTools.bool2subst(allergy['definite'], _('definite'), _('suspected'), '?')
			)
			tooltip += '%s: %s\n' % (
				allergy['descriptor'],
				gmTools.coalesce(allergy['reaction'], _('reaction not recorded'))
			)
		if len(allgs) > 0:
			msg += '\n'
			tooltip += '\n'
		del allgs

		# history of substance abuse
		abuses = emr.abused_substances
		for abuse in abuses:
			tooltip += abuse.format(single_line = False, include_metadata = False)
			tooltip += '\n'
			if abuse['use_type'] in [None, 0]:
				continue
			msg += abuse.format(single_line = True)
			msg += '\n'
		if len(abuses) > 0:
			msg += '\n'
			tooltip += '\n'
		del abuses

		# kidney function
		gfrs = emr.get_most_recent_results_in_loinc_group(loincs = gmLOINC.LOINC_gfr_quantity, max_no_of_results = 1)
		if len(gfrs) == 0:
			self.calc.patient = curr_pat
			gfr = self.calc.eGFR
			if gfr.numeric_value is None:
				msg += _('GFR: unknown')
			else:
				msg += gfr.message
				egfrs = self.calc.eGFRs
				tts = []
				for egfr in egfrs:
					if egfr.numeric_value is None:
						continue
					tts.append(egfr.format (
						left_margin = 0,
						width = 50,
						eol = '\n',
						with_formula = False,
						with_warnings = True,
						with_variables = False,
						with_sub_results = False,
						return_list = False
					))
				tooltip += '\n'.join(tts)
		else:
			gfr = gfrs[0]
			msg += '%s: %s %s (%s)\n' % (
				gfr['unified_abbrev'],
				gfr['unified_val'],
				gmTools.coalesce(gfr['abnormality_indicator'], '', ' (%s)'),
				gmDateTime.pydt_strftime (
					gfr['clin_when'],
					format = '%Y %b %d'
				)
			)
			tooltip += _('GFR reported by path lab')

		# pregnancy
		edc = emr.EDC
		if edc is not None:
			msg += '\n\n'
			if emr.EDC_is_fishy:
				msg += _('EDC (!?!): %s') % gmDateTime.pydt_strftime(edc, format = '%Y %b %d')
				tooltip += _(
					'The Expected Date of Confinement is rather questionable.\n'
					'\n'
					'Please check patient age, patient gender, time until/since EDC.'
				)
			else:
				msg += _('EDC: %s') % gmDateTime.pydt_strftime(edc, format = '%Y %b %d')

		self._LBL_allergies.SetLabel(msg)
		self._LBL_allergies.SetToolTip(tooltip)

	#----------------------------------------------------------------
	def __refresh_drug_details(self):

		drug = self._PRW_drug.GetData(as_instance = True)
		if drug is None:
			self._LBL_drug_details.SetLabel('')
			self._LBL_drug_details.SetToolTip('')
			self.Layout()
			return

		if len(drug['components']) == 0:
			comps = _('<no components>')
		else:
			comps = '\n'.join ([
				' %s %s%s%s' % (
					c['substance'],
					c['amount'],
					c['unit'],
					gmTools.coalesce(c['dose_unit'], '', '/%s')
				)
				for c in drug['components']
			])
		self._LBL_drug_details.SetLabel('%s\n%s' % (drug['drug_product'], comps))
		self._LBL_drug_details.SetToolTip(drug.format())
		self.Layout()
		return

	#----------------------------------------------------------------
	# generic Edit Area mixin API
	#----------------------------------------------------------------
	def _check_drug_is_valid(self):

		self._PRW_drug.display_as_valid(True)

		# if we are editing the drug SHOULD exist so don't error
		if self.mode == 'edit':
			return True

		selected_drug = self._PRW_drug.GetData(as_instance = True)

		# no drug selected
		if selected_drug is None:
			val = self._PRW_drug.GetValue().strip()
			if val == '':
				self._PRW_drug.display_as_valid(False)
				self._PRW_drug.SetFocus()
				return False
			# create as a generic, single-substance drug if that does not exist
			drug = gmSubstanceMgmtWidgets.edit_single_component_generic_drug (
				parent = self,
				drug = None,
				single_entry = True,
				fields = {'substance': {'value': val, 'data': None}},
				return_drug = True
			)
			if drug is None:
				self._PRW_drug.display_as_valid(False)
				self._PRW_drug.SetFocus()
				return False
			comp = drug.components[0]
			self._PRW_drug.SetText (
				_('%s w/ %s%s%s of %s') % (
					comp['drug_product'],
					comp['amount'],
					comp['unit'],
					gmTools.coalesce(comp['dose_unit'], '', '/%s'),
					comp['substance']
				),
				drug['pk_drug_product']
			)
			selected_drug = drug
			self.__refresh_drug_details()
			self._PRW_drug.display_as_valid(True)
			self._PRW_drug.SetFocus()
			# return False despite there's now a drug such
			# that the user has another chance to inspect
			# the edit area data after creating a new drug
			return False

		# drug already exists as intake
		if selected_drug.exists_as_intake(pk_patient = gmPerson.gmCurrentPatient().ID):
			title = _('Adding substance intake entry')
			msg = _(
				'The patient is already taking\n'
				'\n'
				' %s\n'
				'\n'
				'You will want to adjust the schedule\n'
				'rather than document the intake twice.'
			) % self._PRW_drug.GetValue().strip()
			gmGuiHelpers.gm_show_warning(aTitle = title, aMessage = msg)
			self._PRW_drug.display_as_valid(False)
			self._PRW_drug.SetFocus()
			return False

		self._PRW_drug.display_as_valid(True)
		return True

	#----------------------------------------------------------------
	def _valid_for_save(self):

		validity = self._check_drug_is_valid()

		# episode must be set if intake is to be approved of
		if self._CHBOX_approved.IsChecked():
			if self._PRW_episode.GetValue().strip() == '':
				self._PRW_episode.display_as_valid(False)
				validity = False
			else:
				self._PRW_episode.display_as_valid(True)

		if self._PRW_duration.GetValue().strip() in ['', gmTools.u_infinity]:
			self._PRW_duration.display_as_valid(True)
		else:
			if self._PRW_duration.GetData() is None:
				# no data ...
				if gmDateTime.str2interval(self._PRW_duration.GetValue()) is None:
					self._PRW_duration.display_as_valid(False)
					validity = False
				# ... but valid string
				else:
					self._PRW_duration.display_as_valid(True)
			# has data
			else:
				self._PRW_duration.display_as_valid(True)

		# started must exist or be unknown
		started = None
		if self._CHBOX_start_unknown.IsChecked() is False:
			started = self._DP_started.GetData()
			if started is None:
				self._DP_started.display_as_valid(False)
				self._DP_started.SetFocus()
				validity = False
			else:
				self._DP_started.display_as_valid(True)

		if validity is False:
			self.StatusText = _('Input incomplete/invalid for saving as substance intake.')

		# discontinued must be "< now()" AND "> started" if at all
		discontinued = self._DP_discontinued.GetData()
		if discontinued is not None:
			now = gmDateTime.pydt_now_here().replace (
				hour = 23,
				minute = 59,
				second = 59,
				microsecond = 111111
			)
			# not in the future
			if discontinued > now:
				self._DP_discontinued.display_as_valid(False)
				validity = False
				self.StatusText = _('Discontinued (%s) in the future (now: %s)!') % (discontinued, now)
			else:
				if started is not None:
					started = started.replace (
						hour = 0,
						minute = 0,
						second = 0,
						microsecond = 1
					)
					# and not before it was started
					if started > discontinued:
						self._DP_started.display_as_valid(False)
						self._DP_discontinued.display_as_valid(False)
						validity = False
						self.StatusText = _('Discontinued (%s) before started (%s) !') % (discontinued, started)
					else:
						self._DP_started.display_as_valid(True)
						self._DP_discontinued.display_as_valid(True)

		return validity

	#----------------------------------------------------------------
	def _save_as_new(self):

		epi = self._PRW_episode.GetData()
		if epi is None:
			# create new episode, Jim wants it to auto-open
			epi = self._PRW_episode.GetData(can_create = True, is_open = True)

		selected_drug = self._PRW_drug.GetData(as_instance = True)
		intake = selected_drug.turn_into_intake (
			encounter = gmPerson.gmCurrentPatient().emr.current_encounter['pk_encounter'],
			episode = epi
		)

		if intake is None:
			self.StatusText = _('Cannot add duplicate of (maybe inactive) substance intake.')
			return False

		intake['started'] = self._DP_started.GetData()
		if self._CHBOX_start_unknown.IsChecked():
			intake['comment_on_start'] = '?'
		else:
			intake['comment_on_start'] = self._PRW_start_certainty.GetValue().strip()
		intake['discontinued'] = self._DP_discontinued.GetData()
		if intake['discontinued'] is None:
			intake['discontinue_reason'] = None
		else:
			intake['discontinue_reason'] = self._PRW_discontinue_reason.GetValue().strip()
		intake['schedule'] = self._PRW_schedule.GetValue().strip()
		intake['aim'] = self._PRW_aim.GetValue().strip()
		intake['notes'] = self._PRW_notes.GetValue().strip()
		if self._PRW_duration.GetValue().strip() in ['', gmTools.u_infinity]:
			intake['planned_duration'] = None
		else:
			if self._PRW_duration.GetData() is None:
				intake['planned_duration'] = gmDateTime.str2interval(self._PRW_duration.GetValue())
			else:
				intake['planned_duration'] = self._PRW_duration.GetData()
		intake.save()

		self.data = intake

		return True

	#----------------------------------------------------------------
	def _save_as_update(self):

		# auto-applies to all components of a multi-component drug if any:
		self.data['started'] = self._DP_started.GetData()
		if self._CHBOX_start_unknown.IsChecked():
			self.data['comment_on_start'] = '?'
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

		# per-component
		self.data['aim'] = self._PRW_aim.GetValue()
		self.data['notes'] = self._PRW_notes.GetValue()
		epi = self._PRW_episode.GetData()
		if epi is None:
			# create new episode, Jim wants it to auto-open
			epi = self._PRW_episode.GetData(can_create = True, is_open = True)
		self.data['pk_episode'] = epi

		self.data.save()

		return True

	#----------------------------------------------------------------
	def _refresh_as_new(self):
		self._PRW_drug.SetText('', None)

		self._PRW_schedule.SetText('', None)
		self._PRW_duration.SetText('', None)
		self._PRW_aim.SetText('', None)
		self._PRW_notes.SetText('', None)
		self._PRW_episode.SetText('', None)

		self._CHBOX_long_term.SetValue(False)
		self._CHBOX_approved.SetValue(True)

		self._CHBOX_start_unknown.SetValue(False)
		self._DP_started.SetData(gmDateTime.pydt_now_here())
		self._DP_started.Enable(True)
		self._PRW_start_certainty.SetText('', None)
		self._PRW_start_certainty.Enable(True)
		self._DP_discontinued.SetData(None)
		self._PRW_discontinue_reason.SetValue('')
		self._PRW_discontinue_reason.Enable(False)

		self.__refresh_drug_details()
		self.__refresh_precautions()

		self._PRW_drug.SetFocus()

	#----------------------------------------------------------------
	def _refresh_from_existing(self):

		self._PRW_drug.SetText (
			_('%s w/ %s%s%s of %s') % (
				self.data['drug_product'],
				self.data['amount'],
				self.data['unit'],
				gmTools.coalesce(self.data['dose_unit'], '', '/%s'),
				self.data['substance']
			),
			self.data['pk_drug_product']
		)

		self._PRW_drug.Disable()

#		if self.data['is _long_term']:
#			self._PRW_duration.Enable(False)
#			self._PRW_duration.SetText(gmTools.u_infinity, None)
#			self._BTN_discontinued_as_planned.Enable(False)
#		else:
#			self._PRW_duration.Enable(True)
#			self._BTN_discontinued_as_planned.Enable(True)
#			self._PRW_duration.SetData(self.data['planned_duration'])
		self._PRW_aim.SetText(gmTools.coalesce(self.data['aim'], ''), self.data['aim'])
		self._PRW_notes.SetText(gmTools.coalesce(self.data['notes'], ''), self.data['notes'])
		self._PRW_episode.SetData(self.data['pk_episode'])
		self._PRW_schedule.SetText(gmTools.coalesce(self.data['schedule'], ''), self.data['schedule'])

		self._DP_started.SetData(self.data['started'])
		self._PRW_start_certainty.SetText(self.data['comment_on_start'], None)
		if self.data['start_is_unknown']:
			self._CHBOX_start_unknown.SetValue(True)
			self._DP_started.Enable(False)
			self._PRW_start_certainty.Enable(False)
		else:
			self._CHBOX_start_unknown.SetValue(False)
			self._DP_started.Enable(True)
			self._PRW_start_certainty.Enable(True)

		self._DP_discontinued.SetData(self.data['discontinued'])
		self._PRW_discontinue_reason.SetValue(gmTools.coalesce(self.data['discontinue_reason'], ''))
		if self.data['discontinued'] is not None:
			self._PRW_discontinue_reason.Enable()

		self.__refresh_drug_details()
		self.__refresh_precautions()

		self._PRW_schedule.SetFocus()

	#----------------------------------------------------------------
	def _refresh_as_new_from_existing(self):
		self._refresh_as_new()

		self._PRW_episode.SetData(self.data['pk_episode'])
		self._DP_started.SetData(self.data['started'])

		self._PRW_drug.SetFocus()

	#----------------------------------------------------------------
	# event handlers
	#----------------------------------------------------------------
	def _on_leave_drug(self):
		self.__refresh_drug_details()

	#----------------------------------------------------------------
	def _on_enter_aim(self):
		drug = self._PRW_drug.GetData(as_instance = True)
		if drug is None:
			self._PRW_aim.unset_context(context = 'substance')
			return
		# do not set to self._PRW_drug.GetValue() as that will contain all
		# sorts of additional info, rather set to the canonical drug['substance']
#		self._PRW_aim.set_context(context = u'substance', val = drug['substance'])

	#----------------------------------------------------------------
	def _on_discontinued_date_changed(self, event):
		if self._DP_discontinued.GetData() is None:
			self._PRW_discontinue_reason.Enable(False)
		else:
			self._PRW_discontinue_reason.Enable(True)

	#----------------------------------------------------------------
	def _on_manage_components_button_pressed(self, event):
		gmSubstanceMgmtWidgets.manage_drug_components()

	#----------------------------------------------------------------
	def _on_manage_substances_button_pressed(self, event):
		gmSubstanceMgmtWidgets.manage_substances()

	#----------------------------------------------------------------
	def _on_manage_drug_products_button_pressed(self, event):
		gmSubstanceMgmtWidgets.manage_drug_products(parent = self, ignore_OK_button = True)

	#----------------------------------------------------------------
	def _on_manage_doses_button_pressed(self, event):
		gmSubstanceMgmtWidgets.manage_substance_doses(parent = self)

	#----------------------------------------------------------------
	def _on_heart_button_pressed(self, event):
		gmNetworkTools.open_url_in_browser(url = gmMedication.URL_long_qt)

	#----------------------------------------------------------------
	def _on_kidneys_button_pressed(self, event):
		if self._PRW_drug.GetData() is None:
			search_term = self._PRW_drug.GetValue().strip()
		else:
			search_term = self._PRW_drug.GetData(as_instance = True)

		gmNetworkTools.open_url_in_browser(url = gmMedication.drug2renal_insufficiency_url(search_term = search_term))

	#----------------------------------------------------------------
	def _on_discontinued_as_planned_button_pressed(self, event):

		now = gmDateTime.pydt_now_here()

		self.__refresh_precautions()

		if self.data is None:
			return

		# do we have a (full) plan ?
		if None not in [self.data['started'], self.data['planned_duration']]:
			planned_end = self.data['started'] + self.data['planned_duration']
			# the plan hasn't ended so [Per plan] can't apply ;-)
			if planned_end > now:
				return
			self._DP_discontinued.SetData(planned_end)
			self._PRW_discontinue_reason.Enable(True)
			self._PRW_discontinue_reason.SetValue('')
			return

		# we know started but not duration: apparently the plan is to stop today
		if self.data['started'] is not None:
			# but we haven't started yet so we can't stop
			if self.data['started'] > now:
				return

		self._DP_discontinued.SetData(now)
		self._PRW_discontinue_reason.Enable(True)
		self._PRW_discontinue_reason.SetValue('')

	#----------------------------------------------------------------
	def _on_chbox_long_term_checked(self, event):
		if self._CHBOX_long_term.IsChecked() is True:
			self._PRW_duration.Enable(False)
			self._BTN_discontinued_as_planned.Enable(False)
			self._PRW_discontinue_reason.Enable(False)
		else:
			self._PRW_duration.Enable(True)
			self._BTN_discontinued_as_planned.Enable(True)
			self._PRW_discontinue_reason.Enable(True)

		self.__refresh_precautions()

	#----------------------------------------------------------------
	def _on_start_unknown_checked(self, event):
		event.Skip()
		if self._CHBOX_start_unknown.IsChecked() is True:
			self._DP_started.Enable(False)
			self._PRW_start_certainty.Enable(False)
		else:
			self._DP_started.Enable(True)
			self._PRW_start_certainty.Enable(True)

		self.__refresh_precautions()

	#----------------------------------------------------------------
	def turn_into_allergy(self, data=None):
		if not self.save():
			return False

		return turn_substance_intake_into_allergy (
			parent = self,
			intake = self.data,
			emr = gmPerson.gmCurrentPatient().emr
		)

#============================================================
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
		edit_intake_of_substance(parent = parent, substance = intake)
		delete_it = gmGuiHelpers.gm_show_question (
			aMessage = _('Now delete substance intake entry ?'),
			aTitle = _('Deleting medication / substance intake')
		)
	else:
		delete_it = True

	if not delete_it:
		return

	gmMedication.delete_substance_intake(pk_intake = intake['pk_intake'], delete_siblings = True)

#------------------------------------------------------------
def edit_intake_of_substance(parent = None, substance=None, single_entry=False):
	ea = cSubstanceIntakeEAPnl(parent, -1, substance = substance)
	dlg = gmEditArea.cGenericEditAreaDlg2(parent, -1, edit_area = ea, single_entry = single_entry)
	dlg.SetTitle(gmTools.coalesce(substance, _('Adding medication/non-medication substance intake'), _('Editing medication/non-medication substance intake')))
	dlg.left_extra_button = (
		_('Allergy'),
		_('Document an allergy against this substance.'),
		ea.turn_into_allergy
	)
	dlg.SetSize((650,500))
	if dlg.ShowModal() == wx.ID_OK:
		dlg.DestroyLater()
		return True
	dlg.DestroyLater()
	return False

#============================================================
# current substances grid
#------------------------------------------------------------
def configure_medication_list_template(parent=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	template = gmFormWidgets.manage_form_templates (
		parent = parent,
		template_types = ['current medication list']
	)
	option = 'form_templates.medication_list'

	if template is None:
		gmDispatcher.send(signal = 'statustext', msg = _('No medication list template configured.'), beep = True)
		return None

	if template['engine'] not in ['L', 'X', 'T']:
		gmDispatcher.send(signal = 'statustext', msg = _('No medication list template configured.'), beep = True)
		return None

	gmCfgDB.set (
		workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
		option = option,
		value = '%s - %s' % (template['name_long'], template['external_version'])
	)
	return template

#------------------------------------------------------------
def print_medication_list(parent=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	# 1) get template
	option = 'form_templates.medication_list'
	template = gmCfgDB.get4user (
		option = option,
		workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
	)
	if template is None:
		template = configure_medication_list_template(parent = parent)
		if template is None:
			gmGuiHelpers.gm_show_error (
				aMessage = _('There is no medication list template configured.'),
				aTitle = _('Printing medication list')
			)
			return False

	else:
		try:
			name, ver = template.split(' - ')
		except Exception:
			_log.exception('problem splitting medication list template name [%s]', template)
			gmDispatcher.send(signal = 'statustext', msg = _('Problem loading medication list template.'), beep = True)
			return False
		template = gmForms.get_form_template(name_long = name, external_version = ver)
		if template is None:
			gmGuiHelpers.gm_show_error (
				aMessage = _('Cannot load medication list template [%s - %s]') % (name, ver),
				aTitle = _('Printing medication list')
			)
			return False

	# 2) process template
	meds_list = gmFormWidgets.generate_form_from_template (
		parent = parent,
		template = template,
		edit = False
	)
	if meds_list is None:
		return False

	# 3) print template
	return gmFormWidgets.act_on_generated_forms (
		parent = parent,
		forms = [meds_list],
		jobtype = 'medication_list',
		#episode_name = u'administrative',
		episode_name = gmMedication.DEFAULT_MEDICATION_HISTORY_EPISODE,
		progress_note = _('generated medication list document'),
		review_copy_as_normal = True
	)

#------------------------------------------------------------
def configure_prescription_template(parent=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	template = gmFormWidgets.manage_form_templates (
		parent = parent,
		msg = _('Select the default prescription template:'),
		template_types = ['prescription', 'current medication list']
	)

	if template is None:
		gmDispatcher.send(signal = 'statustext', msg = _('No prescription template configured.'), beep = True)
		return None

	if template['engine'] not in ['L', 'X', 'T']:
		gmDispatcher.send(signal = 'statustext', msg = _('No prescription template configured.'), beep = True)
		return None

	option = 'form_templates.prescription'
	gmCfgDB.set (
		workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
		option = option,
		value = '%s - %s' % (template['name_long'], template['external_version'])
	)

	return template

#------------------------------------------------------------
def get_prescription_template(parent=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	option = 'form_templates.prescription'
	template_name = gmCfgDB.get4user (
		option = option,
		workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace
	)

	if template_name is None:
		template = configure_prescription_template(parent = parent)
		if template is None:
			gmGuiHelpers.gm_show_error (
				aMessage = _('There is no prescription template configured.'),
				aTitle = _('Printing prescription')
			)
			return None
		return template

	try:
		name, ver = template_name.split(' - ')
	except Exception:
		_log.exception('problem splitting prescription template name [%s]', template_name)
		gmDispatcher.send(signal = 'statustext', msg = _('Problem loading prescription template.'), beep = True)
		return False
	template = gmForms.get_form_template(name_long = name, external_version = ver)
	if template is None:
		gmGuiHelpers.gm_show_error (
			aMessage = _('Cannot load prescription template [%s - %s]') % (name, ver),
			aTitle = _('Printing prescription')
		)
		return None
	return template

#------------------------------------------------------------
def print_prescription(parent=None, emr=None):

	# 1) get template
	rx_template = get_prescription_template(parent = parent)
	if rx_template is None:
		return False

	# 2) process template
	rx = gmFormWidgets.generate_form_from_template (
		parent = parent,
		template = rx_template,
		edit = False
	)
	if rx is None:
		return False

	# 3) print template
	return gmFormWidgets.act_on_generated_forms (
		parent = parent,
		forms = [rx],
		jobtype = 'prescription',
		#episode_name = u'administrative',
		episode_name = gmMedication.DEFAULT_MEDICATION_HISTORY_EPISODE,
		progress_note = _('generated prescription'),
		review_copy_as_normal = True
	)

#------------------------------------------------------------
def prescribe_drugs(parent=None, emr=None):
	rx_mode = gmCfgDB.get4user (
		option = 'horst_space.default_prescription_mode',
		workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
		default = 'form'			# set to 'database' to access database
	)

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	if rx_mode == 'form':
		return print_prescription(parent = parent, emr = emr)

	if rx_mode == 'database':
		drug_db = gmSubstanceMgmtWidgets.get_drug_database()		#gmPerson.gmCurrentPatient() xxxxxxx ?
		if drug_db is None:
			return
		drug_db.reviewer = gmStaff.gmCurrentProvider()
		prescribed_drugs = drug_db.prescribe()
		update_substance_intake_list_from_prescription (
			parent = parent,
			prescribed_drugs = prescribed_drugs,
			emr = emr
		)

#------------------------------------------------------------
def update_substance_intake_list_from_prescription(parent=None, prescribed_drugs=None, emr=None):

	if len(prescribed_drugs) == 0:
		return

	curr_meds =  [ i['pk_drug_product'] for i in emr.get_current_medications() if i['pk_drug_product'] is not None ]
	new_drugs = []
	for drug in prescribed_drugs:
		if drug['pk_drug_product'] not in curr_meds:
			new_drugs.append(drug)

	if len(new_drugs) == 0:
		return

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	picker = gmListWidgets.cItemPickerDlg (
		parent,
		-1,
		msg = _(
			'These products have been prescribed but are not listed\n'
			'in the current medication list of this patient.\n'
			'\n'
			'Please select those you want added to the medication list.'
		)
	)
	picker.set_columns (
		columns = [_('Newly prescribed drugs')],
		columns_right = [_('Add to medication list')]
	)
	choices = [ ('%s %s (%s)' % (d['drug_product'], d['l10n_preparation'], '; '.join(d['components']))) for d in new_drugs ]
	picker.set_choices (
		choices = choices,
		data = new_drugs
	)
	picker.ShowModal()
	drugs2add = picker.get_picks()
	picker.DestroyLater()

	if drugs2add is None:
		return

	if len(drugs2add) == 0:
		return

	for drug in drugs2add:
		# only add first component since all other components get added by a trigger ...
		intake = emr.add_substance_intake(pk_component = drug['components'][0]['pk_component'])
		if intake is None:
			continue
		intake.save()

	return

#------------------------------------------------------------
class cCurrentSubstancesGrid(wx.grid.Grid):
	"""A grid class for displaying current substance intake.

	- does NOT listen to the currently active patient
	- thereby it can display any patient at any time
	"""
	def __init__(self, *args, **kwargs):

		wx.grid.Grid.__init__(self, *args, **kwargs)

		self.__patient = None
		self.__row_data = {}
		self.__prev_row = None
		self.__prev_tooltip_row = None
		self.__prev_cell_0 = None
		self.__grouping_mode = 'issue'
		self.__filter_show_unapproved = True
		self.__filter_show_inactive = True

		self.__grouping2col_labels = {
			'issue': [
				_('Health issue'),
				_('Substance'),
				_('Strength'),
				_('Schedule'),
				_('Timeframe'),
				_('Product'),
				_('Advice')
			],
			'drug_product': [
				_('Product'),
				_('Schedule'),
				_('Substance'),
				_('Strength'),
				_('Timeframe'),
				_('Health issue'),
				_('Advice')
			],
			'episode': [
				_('Episode'),
				_('Substance'),
				_('Strength'),
				_('Schedule'),
				_('Timeframe'),
				_('Product'),
				_('Advice')
			],
			'start': [
				_('Episode'),
				_('Substance'),
				_('Strength'),
				_('Schedule'),
				_('Timeframe'),
				_('Product'),
				_('Advice')
			],
		}

		self.__grouping2order_by_clauses = {
			'issue': 'pk_health_issue NULLS FIRST, substance, started',
			'episode': 'pk_health_issue NULLS FIRST, episode, substance, started',
			'drug_product': 'product NULLS LAST, substance, started',
			'start': 'started DESC, substance, episode'
		}

		self.__init_ui()
		self.__register_events()

	#------------------------------------------------------------
	# external API
	#------------------------------------------------------------
	def get_selected_cells(self):

		#sel_block_top_left = self.GetSelectionBlockTopLeft()
		#sel_block_bottom_right = self.GetSelectionBlockBottomRight()
		sel_cols = self.GetSelectedCols()
		sel_rows = self.GetSelectedRows()

		selected_cells = []

		# individually selected cells (ctrl-click)
		selected_cells += self.GetSelectedCells()

		# selected rows
		selected_cells += list (
			(row, col)
				for row in sel_rows
				for col in range(self.GetNumberCols())
		)

		# selected columns
		selected_cells += list (
			(row, col)
				for row in range(self.GetNumberRows())
				for col in sel_cols
		)

		# selection blocks
		for top_left, bottom_right in zip(self.GetSelectionBlockTopLeft(), self.GetSelectionBlockBottomRight()):
			selected_cells += [
				(row, col)
					for row in range(top_left[0], bottom_right[0] + 1)
					for col in range(top_left[1], bottom_right[1] + 1)
			]

		return set(selected_cells)

	#------------------------------------------------------------
	def get_selected_rows(self):
		rows = {}
		for row, col in self.get_selected_cells():
			rows[row] = True
		return list(rows)

	#------------------------------------------------------------
	def get_selected_data(self):
		return [ self.__row_data[row] for row in self.get_selected_rows() ]

	#------------------------------------------------------------
	def get_row_data(self):
		return self.__row_data.values()

	#------------------------------------------------------------
	def repopulate_grid(self):

		self.empty_grid()

		if self.__patient is None:
			return

		emr = self.__patient.emr
		meds = emr.get_current_medications (
			order_by = self.__grouping2order_by_clauses[self.__grouping_mode],
			# FIXME field does not exist anymore   xxxxxxxxxxxxxxxxxxxxxx
			#include_unapproved = self.__filter_show_unapproved,
			include_inactive = self.__filter_show_inactive
		)
		if not meds:
			return

		self.BeginBatch()

		# columns
		labels = self.__grouping2col_labels[self.__grouping_mode]
		if self.__filter_show_unapproved:
			self.AppendCols(numCols = len(labels) + 1)
		else:
			self.AppendCols(numCols = len(labels))
		for col_idx in range(len(labels)):
			self.SetColLabelValue(col_idx, labels[col_idx])
		if self.__filter_show_unapproved:
			#self.SetColLabelValue(len(labels), u'OK?')
			self.SetColLabelValue(len(labels), '')
			self.SetColSize(len(labels), 40)

		self.AppendRows(numRows = len(meds))

		# loop over data
		for row_idx in range(len(meds)):
			med = meds[row_idx]
			self.__row_data[row_idx] = med

			if med['is_currently_active'] is True:
				atcs = []
				if med['atc_substance'] is not None:
					atcs.append(med['atc_substance'])
				allg = emr.is_allergic_to(atcs = atcs, inns = (med['substance'],))
				if allg not in [None, False]:
					attr = self.GetOrCreateCellAttr(row_idx, 0)
					if allg['type'] == 'allergy':
						attr.SetTextColour('red')
					else:
						#attr.SetTextColour('yellow')		# too light
						#attr.SetTextColour('pink')			# too light
						#attr.SetTextColour('dark orange')	# slightly better
						attr.SetTextColour('magenta')
					self.SetRowAttr(row_idx, attr)
			else:
				attr = self.GetOrCreateCellAttr(row_idx, 0)
				attr.SetTextColour('grey')
				self.SetRowAttr(row_idx, attr)

			if self.__grouping_mode in ['episode', 'start']:
				if med['pk_episode'] is None:
					self.__prev_cell_0 = None
					epi = gmTools.u_diameter
				else:
					if self.__prev_cell_0 == med['episode']:
						epi = ''
					else:
						self.__prev_cell_0 = med['episode']
						epi = gmTools.coalesce(med['episode'], '')
				self.SetCellValue(row_idx, 0, gmTools.wrap(text = epi, width = 40))

				self.SetCellValue(row_idx, 1, med['substance'])
				self.SetCellValue(row_idx, 2, '%s %s' % (med['amount'], med['unit']))
				self.SetCellValue(row_idx, 3, gmTools.coalesce(med['schedule'], ''))
				self.SetCellValue(row_idx, 4, med.medically_formatted_start_end)

				if med['pk_drug_product'] is None:
					product = '%s (%s)' % (gmTools.u_diameter, med['l10n_preparation'])
				else:
					if med['is_fake_product']:
						product = '%s (%s)' % (
							gmTools.coalesce(med['drug_product'], '', _('%s <fake>')),
							med['l10n_preparation']
						)
					else:
						product = '%s (%s)' % (
							gmTools.coalesce(med['drug_product'], ''),
							med['l10n_preparation']
						)
				self.SetCellValue(row_idx, 5, gmTools.wrap(text = product, width = 35))

			elif self.__grouping_mode == 'issue':
				if med['pk_health_issue'] is None:
					self.__prev_cell_0 = None
					issue = '%s%s' % (
						gmTools.u_diameter,
						gmTools.coalesce(med['episode'], '', ' (%s)')
					)
				else:
					if self.__prev_cell_0 == med['health_issue']:
						issue = ''
					else:
						self.__prev_cell_0 = med['health_issue']
						issue = med['health_issue']
				self.SetCellValue(row_idx, 0, gmTools.wrap(text = issue, width = 40))

				self.SetCellValue(row_idx, 1, med['substance'])
				self.SetCellValue(row_idx, 2, '%s %s' % (med['amount'], med['unit']))
				self.SetCellValue(row_idx, 3, gmTools.coalesce(med['schedule'], ''))
				self.SetCellValue(row_idx, 4, med.medically_formatted_start_end)

				if med['pk_drug_product'] is None:
					product = '%s (%s)' % (gmTools.u_diameter, med['l10n_preparation'])
				else:
					if med['is_fake_product']:
						product = '%s (%s)' % (
							gmTools.coalesce(med['drug_product'], '', _('%s <fake>')),
							med['l10n_preparation']
						)
					else:
						product = '%s (%s)' % (
							gmTools.coalesce(med['drug_product'], ''),
							med['l10n_preparation']
						)
				self.SetCellValue(row_idx, 5, gmTools.wrap(text = product, width = 35))

			elif self.__grouping_mode == 'drug_product':

				if med['pk_drug_product'] is None:
					self.__prev_cell_0 = None
					product =  '%s (%s)' % (
						gmTools.u_diameter,
						med['l10n_preparation']
					)
				else:
					if self.__prev_cell_0 == med['drug_product']:
						product = ''
					else:
						self.__prev_cell_0 = med['drug_product']
						if med['is_fake_product']:
							product = '%s (%s)' % (
								gmTools.coalesce(med['drug_product'], '', _('%s <fake>')),
								med['l10n_preparation']
							)
						else:
							product = '%s (%s)' % (
								gmTools.coalesce(med['drug_product'], ''),
								med['l10n_preparation']
							)
				self.SetCellValue(row_idx, 0, gmTools.wrap(text = product, width = 35))

				self.SetCellValue(row_idx, 1, gmTools.coalesce(med['schedule'], ''))
				self.SetCellValue(row_idx, 2, med['substance'])
				self.SetCellValue(row_idx, 3, '%s %s' % (med['amount'], med['unit']))
				self.SetCellValue(row_idx, 4, med.medically_formatted_start_end)

				if med['pk_health_issue'] is None:
					issue = '%s%s' % (
						gmTools.u_diameter,
						gmTools.coalesce(med['episode'], '', ' (%s)')
					)
				else:
					issue = gmTools.coalesce(med['health_issue'], '')
				self.SetCellValue(row_idx, 5, gmTools.wrap(text = issue, width = 40))

			else:
				raise ValueError('unknown grouping mode [%s]' % self.__grouping_mode)

			if med['notes'] is not None:
				self.SetCellValue(row_idx, 6, gmTools.wrap(text = med['notes'], width = 50))

#			if self.__filter_show_unapproved:
#				self.SetCellValue (
#					row_idx,
#					len(labels),
#					gmTools.bool2subst(med['intake_ is_approved_of'], gmTools.u_checkmark_thin, gmTools.u_frowning_face, '?')
#				)
#				font = self.GetCellFont(row_idx, len(labels))
#				font.SetPointSize(font.GetPointSize() + 2)
#				self.SetCellFont(row_idx, len(labels), font)

			#self.SetCellAlignment(row, col, horiz = wx.ALIGN_RIGHT, vert = wx.ALIGN_CENTRE)

		self.AutoSize()
		self.EndBatch()
	#------------------------------------------------------------
	def empty_grid(self):
		self.BeginBatch()
		self.ClearGrid()
		# Windows cannot do "nothing", it rather decides to assert()
		# on thinking it is supposed to do nothing
		if self.GetNumberRows() > 0:
			self.DeleteRows(pos = 0, numRows = self.GetNumberRows())
		if self.GetNumberCols() > 0:
			self.DeleteCols(pos = 0, numCols = self.GetNumberCols())
		self.EndBatch()
		self.__row_data = {}
		self.__prev_cell_0 = None

	#------------------------------------------------------------
	def show_info_on_entry(self):

		if len(self.__row_data) == 0:
			return

		sel_rows = self.get_selected_rows()
		if len(sel_rows) != 1:
			return

		drug_db = gmSubstanceMgmtWidgets.get_drug_database(patient = self.__patient)
		if drug_db is None:
			return

		intake = self.get_selected_data()[0]		# just in case
		if intake['drug_product'] is None:
			drug_db.show_info_on_substance(substance_intake = intake)
		else:
			drug_db.show_info_on_drug(substance_intake = intake)

	#------------------------------------------------------------
	def show_renal_insufficiency_info(self):
		search_term = None
		if len(self.__row_data) > 0:
			sel_rows = self.get_selected_rows()
			if len(sel_rows) == 1:
				search_term = self.get_selected_data()[0]
		gmNetworkTools.open_url_in_browser(url = gmMedication.drug2renal_insufficiency_url(search_term = search_term))

	#------------------------------------------------------------
	def show_cardiac_info(self):
		gmNetworkTools.open_url_in_browser(url = gmMedication.URL_long_qt)

	#------------------------------------------------------------
	def report_ADR(self):
		url = gmCfgDB.get4user (
			option = 'external.urls.report_ADR',
			workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
			default = gmMedication.URL_drug_adr_german_default
		)
		gmNetworkTools.open_url_in_browser(url = url)

	#------------------------------------------------------------
	def prescribe(self):
		prescribe_drugs (
			parent = self,
			emr = self.__patient.emr
		)
	#------------------------------------------------------------
	def check_interactions(self):

		if len(self.__row_data) == 0:
			return

		drug_db = gmSubstanceMgmtWidgets.get_drug_database(patient = self.__patient)
		if drug_db is None:
			return

		if len(self.get_selected_rows()) > 1:
			drug_db.check_interactions(substance_intakes = self.get_selected_data())
		else:
			drug_db.check_interactions(substance_intakes = self.__row_data.values())
	#------------------------------------------------------------
	def add_substance(self):
		edit_intake_of_substance(parent = self, substance = None)
	#------------------------------------------------------------
	def edit_substance(self):

		rows = self.get_selected_rows()

		if len(rows) == 0:
			return

		if len(rows) > 1:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot edit more than one substance at once.'), beep = True)
			return

		subst = self.get_selected_data()[0]
		edit_intake_of_substance(parent = self, substance = subst)

	#------------------------------------------------------------
	def delete_intake(self):

		rows = self.get_selected_rows()

		if len(rows) == 0:
			return

		if len(rows) > 1:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot delete more than one substance at once.'), beep = True)
			return

		intake = self.get_selected_data()[0]
		delete_substance_intake(parent = self, intake = intake)

	#------------------------------------------------------------
	def create_allergy_from_substance(self):
		rows = self.get_selected_rows()

		if len(rows) == 0:
			return

		if len(rows) > 1:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot create allergy from more than one substance at once.'), beep = True)
			return

		return turn_substance_intake_into_allergy (
			parent = self,
			intake = self.get_selected_data()[0],
			emr = self.__patient.emr
		)
	#------------------------------------------------------------
	def print_medication_list(self):
		# there could be some filtering/user interaction going on here
		print_medication_list(parent = self)
	#------------------------------------------------------------
	def get_row_tooltip(self, row=None):

		try:
			entry = self.__row_data[row]
		except KeyError:
			return ' '

		emr = self.__patient.emr
		atcs = []
		if entry['atc_substance'] is not None:
			atcs.append(entry['atc_substance'])
#		if entry['atc_drug'] is not None:
#			atcs.append(entry['atc_drug'])
#		allg = emr.is_allergic_to(atcs = atcs, inns = (entry['substance'],), product_name = entry['drug_product'])
		allg = emr.is_allergic_to(atcs = atcs, inns = (entry['substance'],))

		tt = _('Substance intake entry (%s)   [#%s]                     \n') % (
			gmTools.bool2subst (
				boolean = entry['is_currently_active'],
				true_return = gmTools.bool2subst (
					boolean = entry['seems_inactive'],
					true_return = _('active, needs check'),
					false_return = _('active'),
					none_return = _('assumed active')
				),
				false_return = _('inactive')
			),
			entry['pk_intake']
		)

		if allg not in [None, False]:
			certainty = gmTools.bool2subst(allg['definite'], _('definite'), _('suspected'))
			tt += '\n'
			tt += ' !! ---- Cave ---- !!\n'
			tt += ' %s (%s): %s (%s)\n' % (
				allg['l10n_type'],
				certainty,
				allg['descriptor'],
				gmTools.coalesce(allg['reaction'], '')[:40]
			)
			tt += '\n'

		tt += ' ' + _('Substance: %s   [#%s]\n') % (entry['substance'], entry['pk_substance'])
		tt += ' ' + _('Preparation: %s\n') % entry['l10n_preparation']
		tt += ' ' + _('Amount per dose: %s %s') % (entry['amount'], entry['unit'])
		tt += '\n'
		tt += gmTools.coalesce(entry['atc_substance'], '', _(' ATC (substance): %s\n'))

		tt += '\n'

		tt += gmTools.coalesce (
			entry['drug_product'],
			'',
			_(' Product name: %%s   [#%s]\n') % entry['pk_drug_product']
		)
		tt += gmTools.coalesce(entry['atc_drug'], '', _(' ATC (drug): %s\n'))

		tt += '\n'

		tt += gmTools.coalesce(entry['schedule'], '', _(' Regimen: %s\n'))

		if entry['planned_duration'] is None:
			duration = ''
		else:
			duration = ' %s %s' % (gmTools.u_arrow2right, gmDateTime.format_interval(entry['planned_duration'], gmDateTime.acc_days))

		tt += _(' Started %s%s\n') % (
			entry.medically_formatted_start,
			duration
		)

		if entry['discontinued'] is not None:
			tt += _(' Discontinued %s\n') % gmDateTime.pydt_strftime(entry['discontinued'], '%Y %b %d')
			tt += gmTools.coalesce(entry['discontinue_reason'], '', _(' Reason: %s\n'))

		tt += '\n'

		tt += gmTools.coalesce(entry['aim'], '', _(' Aim: %s\n'))
		tt += gmTools.coalesce(entry['episode'], '', _(' Episode: %s\n'))
		tt += gmTools.coalesce(entry['health_issue'], '', _(' Health issue: %s\n'))
		tt += gmTools.coalesce(entry['notes'], '', _(' Advice: %s\n'))

		tt += '\n'

		tt += _('Revision: #%(row_ver)s, %(mod_when)s by %(mod_by)s.') % ({
			'row_ver': entry['row_version'],
			'mod_when': gmDateTime.pydt_strftime(entry['modified_when'], '%Y %b %d  %H:%M:%S'),
			'mod_by': entry['modified_by']
		})

		return tt

	#------------------------------------------------------------
	# internal helpers
	#------------------------------------------------------------
	def __init_ui(self):
		self.CreateGrid(0, 1)
		self.EnableEditing(0)
		self.EnableDragGridSize(1)
		self.SetSelectionMode(wx.grid.Grid.wxGridSelectRows)

		self.SetColLabelAlignment(wx.ALIGN_LEFT, wx.ALIGN_CENTER)

		self.SetRowLabelSize(0)
		self.SetRowLabelAlignment(horiz = wx.ALIGN_RIGHT, vert = wx.ALIGN_CENTRE)

	#------------------------------------------------------------
	# properties
	#------------------------------------------------------------
	def _get_patient(self):
		return self.__patient

	def _set_patient(self, patient):
		self.__patient = patient
		self.repopulate_grid()

	patient = property(_get_patient, _set_patient)
	#------------------------------------------------------------
	def _get_grouping_mode(self):
		return self.__grouping_mode

	def _set_grouping_mode(self, mode):
		self.__grouping_mode = mode
		self.repopulate_grid()

	grouping_mode = property(_get_grouping_mode, _set_grouping_mode)
	#------------------------------------------------------------
	def _get_filter_show_unapproved(self):
		return self.__filter_show_unapproved

	def _set_filter_show_unapproved(self, val):
		self.__filter_show_unapproved = val
		self.repopulate_grid()

	filter_show_unapproved = property(_get_filter_show_unapproved, _set_filter_show_unapproved)
	#------------------------------------------------------------
	def _get_filter_show_inactive(self):
		return self.__filter_show_inactive

	def _set_filter_show_inactive(self, val):
		self.__filter_show_inactive = val
		self.repopulate_grid()

	filter_show_inactive = property(_get_filter_show_inactive, _set_filter_show_inactive)
	#------------------------------------------------------------
	# event handling
	#------------------------------------------------------------
	def __register_events(self):
		# dynamic tooltips: GridWindow, GridRowLabelWindow, GridColLabelWindow, GridCornerLabelWindow
		self.GetGridWindow().Bind(wx.EVT_MOTION, self.__on_mouse_over_cells)
		#self.GetGridRowLabelWindow().Bind(wx.EVT_MOTION, self.__on_mouse_over_row_labels)
		#self.GetGridColLabelWindow().Bind(wx.EVT_MOTION, self.__on_mouse_over_col_labels)

		# editing cells
		self.Bind(wx.grid.EVT_GRID_CELL_LEFT_DCLICK, self.__on_cell_left_dclicked)
	#------------------------------------------------------------
	def __on_mouse_over_cells(self, evt):
		"""Calculate where the mouse is and set the tooltip dynamically."""

		# Use CalcUnscrolledPosition() to get the mouse position within the
		# entire grid including what's offscreen
		x, y = self.CalcUnscrolledPosition(evt.GetX(), evt.GetY())

		# use this logic to prevent tooltips outside the actual cells
		# apply to GetRowSize, too
#        tot = 0
#        for col in range(self.NumberCols):
#            tot += self.GetColSize(col)
#            if xpos <= tot:
#                self.tool_tip.Tip = 'Tool tip for Column %s' % (
#                    self.GetColLabelValue(col))
#                break
#            else:  # mouse is in label area beyond the right-most column
#            self.tool_tip.Tip = ''

		row, col = self.XYToCell(x, y)

		if row == self.__prev_tooltip_row:
			return

		self.__prev_tooltip_row = row

		try:
			evt.GetEventObject().SetToolTip(self.get_row_tooltip(row = row))
		except KeyError:
			pass
	#------------------------------------------------------------
	def __on_cell_left_dclicked(self, evt):
		row = evt.GetRow()
		data = self.__row_data[row]
		edit_intake_of_substance(parent = self, substance = data)

#============================================================
def configure_default_medications_lab_panel(parent=None):

	panels = gmPathLab.get_test_panels(order_by = 'description')
	gmCfgWidgets.configure_string_from_list_option (
		parent = parent,
		message = _(
			'\n'
			'Select the measurements panel to show in the medications plugin.'
			'\n'
		),
		option = 'horstspace.medications_plugin.lab_panel',
		bias = 'user',
		default_value = None,
		choices = [ '%s%s' % (p['description'], gmTools.coalesce(p['comment'], '', ' (%s)')) for p in panels ],
		columns = [_('Measurements panel')],
		data = [ p['pk_test_panel'] for p in panels ],
		caption = _('Configuring medications plugin measurements panel')
	)

#============================================================
def configure_adr_url():

	def is_valid(value):
		value = value.strip()
		if value == '':
			return True, gmMedication.URL_drug_adr_german_default
		try:
			urllib.request.urlopen(value)
			return True, value
		except Exception:
			return True, value

	gmCfgWidgets.configure_string_option (
		message = _(
			'GNUmed will use this URL to access a website which lets\n'
			'you report an adverse drug reaction (ADR).\n'
			'\n'
			'If you leave this empty it will fall back\n'
			'to an URL for reporting ADRs in Germany.'
		),
		option = 'external.urls.report_ADR',
		bias = 'user',
		default_value = gmMedication.URL_drug_adr_german_default,
		validator = is_valid
	)

#============================================================
from Gnumed.wxGladeWidgets import wxgCurrentSubstancesPnl

class cCurrentSubstancesPnl(wxgCurrentSubstancesPnl.wxgCurrentSubstancesPnl, gmRegetMixin.cRegetOnPaintMixin):

	"""Panel holding a grid with current substances. Used as notebook page."""

	def __init__(self, *args, **kwargs):

		wxgCurrentSubstancesPnl.wxgCurrentSubstancesPnl.__init__(self, *args, **kwargs)
		gmRegetMixin.cRegetOnPaintMixin.__init__(self)

		self.__grouping_choice_labels = [
			{'label': _('Health issue'), 'data': 'issue'} ,
			{'label': _('Drug product'), 'data': 'drug_product'},
			{'label': _('Episode'), 'data': 'episode'},
			{'label': _('Started'), 'data': 'start'}
		]
		self.__lab_panel = None

		self.__init_ui()
		self.__register_interests()

	#-----------------------------------------------------
	def __init_ui(self):
		self._CHCE_grouping.Clear()
		for option in self.__grouping_choice_labels:
			self._CHCE_grouping.Append(option['label'], option['data'])
		self._CHCE_grouping.SetSelection(0)

		tt = self._BTN_heart.GetToolTipText()
		try:
			self._BTN_heart.SetToolTip(tt % gmMedication.URL_long_qt)
		except TypeError:
			_log.exception('translation error: %s', tt)

		tt = self._BTN_kidneys.GetToolTipText()
		try:
			self._BTN_kidneys.SetToolTip(tt % gmMedication.URL_renal_insufficiency)
		except TypeError:
			_log.exception('translation error: %s', tt)

	#-----------------------------------------------------
	# reget-on-paint mixin API
	#-----------------------------------------------------
	def _populate_with_data(self):
		"""Populate cells with data from model."""
		pat = gmPerson.gmCurrentPatient()
		if pat.connected:
			self._grid_substances.patient = pat
			self.__refresh_gfr(pat)
			self.__refresh_lab(patient = pat)
		else:
			self._grid_substances.patient = None
			self.__clear_gfr()
			self.__refresh_lab(patient = None)
		return True

	#--------------------------------------------------------
	def __refresh_lab(self, patient):

		self._GSZR_lab.Clear(True)		# also delete child windows
		self._HLINE_lab.Hide()

		if patient is None:
			self.Layout()
			return

		emr = patient.emr
		most_recent_results = {}

		# get most recent results for "LOINCs to monitor"
		loincs2monitor = set()
		loincs2monitor_data = {}
		loinc_max_age = {}
		loinc_max_age_str = {}
		for intake in self._grid_substances.get_row_data():
			for l in intake['loincs']:
				loincs2monitor.add(l['loinc'])
				loincs2monitor_data[l['loinc']] = {
					'substance': intake['substance'],
					'comment': l['comment']
				}
				if l['max_age_in_secs'] is not None:
					try:
						if loinc_max_age[l['loinc']] > l['max_age_in_secs']:
							loinc_max_age[l['loinc']] = l['max_age_in_secs']
							loinc_max_age_str[l['loinc']] = l['max_age_str']
					except KeyError:
						loinc_max_age[l['loinc']] = l['max_age_in_secs']
						loinc_max_age_str[l['loinc']] = l['max_age_str']
		loincs2monitor_missing = loincs2monitor.copy()
		for loinc in loincs2monitor:
			results = emr.get_most_recent_results_in_loinc_group(loincs = [loinc], max_no_of_results = 1)
			if len(results) == 0:
				continue
			loincs2monitor_missing.remove(loinc)
			# make unique
			result = results[0]
			most_recent_results[result['pk_test_result']] = result

		# get most recent results for "general medication monitoring lab panel"
		if self.__lab_panel is not None:
			for result in self.__lab_panel.get_most_recent_results (
				pk_patient = patient.ID,
				order_by = 'unified_abbrev',
				group_by_meta_type = True
			):
				try: loincs2monitor_missing.remove(result['loinc_tt'])
				except KeyError: pass
				try: loincs2monitor_missing.remove(result['loinc_meta'])
				except KeyError: pass
				# make unique
				most_recent_results[result['pk_test_result']] = result

		# those need special treatment
		gfrs = emr.get_most_recent_results_in_loinc_group(loincs = gmLOINC.LOINC_gfr_quantity, max_no_of_results = 1)
		gfr = gfrs[0] if len(gfrs) > 0 else None
		creas = emr.get_most_recent_results_in_loinc_group(loincs = gmLOINC.LOINC_creatinine_quantity, max_no_of_results = 1)
		crea = creas[0] if len(creas) > 0 else None
		edc = emr.EDC

		# display EDC
		if edc is not None:
			if emr.EDC_is_fishy:
				lbl = wx.StaticText(self, -1, _('EDC (!?!):'))
				val = wx.StaticText(self, -1, gmDateTime.pydt_strftime(edc, format = '%Y %b %d'))
			else:
				lbl = wx.StaticText(self, -1, _('EDC:'))
				val = wx.StaticText(self, -1, gmDateTime.pydt_strftime(edc, format = '%Y %b %d'))
			lbl.SetForegroundColour('blue')
			szr = wx.BoxSizer(wx.HORIZONTAL)
			szr.Add(lbl, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 3)
			szr.Add(val, 1, wx.ALIGN_CENTER_VERTICAL)
			self._GSZR_lab.Add(szr)

		# decide which among Crea or GFR to show
		if crea is None:
			gfr_3_months_older_than_crea = False
			if gfr is not None:
				most_recent_results = [gfr] + most_recent_results
		elif gfr is None:
			gfr_3_months_older_than_crea = True
		else:
			three_months = pydt.timedelta(weeks = 14)
			gfr_3_months_older_than_crea = (crea['clin_when'] - gfr['clin_when']) > three_months
			if not gfr_3_months_older_than_crea:
				most_recent_results = [gfr] + most_recent_results

		# if GFR not found in most_recent_results or old, then calculate
		now = gmDateTime.pydt_now_here()
		if gfr_3_months_older_than_crea:
			calc = gmClinicalCalculator.cClinicalCalculator()
			calc.patient = patient
			gfr = calc.eGFR
			if gfr.numeric_value is None:
				gfr_msg = '?'
			else:
				gfr_msg = _('%.1f (%s ago)') % (
					gfr.numeric_value,
					gmDateTime.format_interval_medically(now - gfr.date_valid)
				)
			lbl = wx.StaticText(self, -1, _('eGFR:'))
			lbl.SetForegroundColour('blue')
			val = wx.StaticText(self, -1, gfr_msg)
			tts = []
			for egfr in calc.eGFRs:
				if egfr.numeric_value is None:
					continue
				tts.append(egfr.format (
					left_margin = 0,
					width = 50,
					eol = '\n',
					with_formula = False,
					with_warnings = True,
					with_variables = False,
					with_sub_results = False,
					return_list = False
				))
			val.SetToolTip('\n'.join(tts))
			szr = wx.BoxSizer(wx.HORIZONTAL)
			szr.Add(lbl, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 3)
			szr.Add(val, 1, wx.ALIGN_CENTER_VERTICAL)
			self._GSZR_lab.Add(szr)

		# eventually add most-recent results from monitoring panel and substances monitoring
		for pk_result in most_recent_results:
			result = most_recent_results[pk_result]
			# test type
			lbl = wx.StaticText(self, -1, '%s:' % result['unified_abbrev'])
			lbl.SetForegroundColour('blue')
			# calculate test result
			indicate_attention = False
			if result.is_considered_abnormal:
				indicate_attention = True
			# calculate tooltip data
			max_age = None
			try:
				max_age = loinc_max_age[result['loinc_tt']]
				max_age_str = loinc_max_age_str[result['loinc_tt']]
			except KeyError:
				try:
					max_age = loinc_max_age[result['loinc_meta']]
					max_age_str = loinc_max_age_str[result['loinc_meta']]
				except KeyError:
					pass
			subst2monitor = None
			try:
				subst2monitor = loincs2monitor_data[result['loinc_tt']]['substance']
			except KeyError:
				try:
					subst2monitor = loincs2monitor_data[result['loinc_meta']]['substance']
				except KeyError:
					pass
			monitor_comment = None
			try:
				monitor_comment = loincs2monitor_data[result['loinc_tt']]['comment']
			except KeyError:
				try:
					monitor_comment = loincs2monitor_data[result['loinc_meta']]['comment']
				except KeyError:
					pass
			result_age = now - result['clin_when']
			unhappy_reasons = []
			if result.is_considered_abnormal:
				indicator = result.formatted_abnormality_indicator
				if indicator == '':
					unhappy_reasons.append(_(' - abnormal'))
				else:
					unhappy_reasons.append(_(' - abnormal: %s') % indicator)
			if max_age is not None:
				if result_age.total_seconds() > max_age:
					unhappy_reasons.append(_(' - too old: %s ago (max: %s)') % (
						gmDateTime.format_interval_medically(result_age),
						max_age_str
					))
			# generate tooltip
			tt = [_('Most recent: %s ago') % gmDateTime.format_interval_medically(result_age)]
			if subst2monitor is not None:
				tt.append(_('Why monitor: %s') % subst2monitor)
			if monitor_comment is not None:
				tt.append(' %s' % monitor_comment)
			if len(unhappy_reasons) > 0:
				indicate_attention = True
				tt.append(_('Problems:'))
				tt.extend(unhappy_reasons)
			tt = '%s\n\n%s' % (
				'\n'.join(tt),
				result.format()
			)
			# set test result and tooltip
			val = wx.StaticText(self, -1, '%s%s%s' % (
				result['unified_val'],
				gmTools.coalesce(result['val_unit'], '', ' %s'),
				gmTools.bool2subst(indicate_attention, gmTools.u_frowning_face, '', '')
			))
			val.SetToolTip(tt)
			if result.is_considered_abnormal:
				val.SetForegroundColour('red')
			szr = wx.BoxSizer(wx.HORIZONTAL)
			szr.Add(lbl, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 3)
			szr.Add(val, 1, wx.ALIGN_CENTER_VERTICAL)
			self._GSZR_lab.Add(szr)

		# hint at missing, but required results (set to be
		# monitored under intakes based on LOINCs):
		for loinc in loincs2monitor_missing:
			#szr.Add(lbl, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 3)
			loinc_data = gmLOINC.loinc2data(loinc)
			if loinc_data is None:
				loinc_str = loinc
			else:
				loinc_str = loinc_data['term']
			val = wx.StaticText(self, -1, '%s!' % loinc_str)
			tt = [
				_('No test result for: %s (%s)') % (loinc_str, loinc),
				'',
				_('Why monitor: %s' % loincs2monitor_data[loinc]['substance'])
			]
			try:
				tt.append(' %s' % loincs2monitor_data[loinc]['comment'])
			except KeyError:
				pass
			val.SetToolTip('\n'.join(tt))
			val.SetForegroundColour('orange')
			szr = wx.BoxSizer(wx.HORIZONTAL)
			szr.Add(val, 1, wx.ALIGN_CENTER_VERTICAL)
			self._GSZR_lab.Add(szr)

		self._HLINE_lab.Show()
		self.Layout()

	#--------------------------------------------------------
	def __refresh_gfr(self, patient):
		gfrs = patient.emr.get_most_recent_results_in_loinc_group(loincs = gmLOINC.LOINC_gfr_quantity, max_no_of_results = 1)
		if len(gfrs) == 0:
			calc = gmClinicalCalculator.cClinicalCalculator()
			calc.patient = patient
			gfr = calc.eGFR
			if gfr.numeric_value is None:
				msg = _('GFR: ?')
				tt = gfr.message
			else:
				msg = _('eGFR: %.1f (%s)') % (
					gfr.numeric_value,
					gmDateTime.pydt_strftime (
						gfr.date_valid,
						format = '%b %Y'
					)
				)
				egfrs = calc.eGFRs
				tts = []
				for egfr in egfrs:
					if egfr.numeric_value is None:
						continue
					tts.append(egfr.format (
						left_margin = 0,
						width = 50,
						eol = '\n',
						with_formula = False,
						with_warnings = True,
						with_variables = False,
						with_sub_results = False,
						return_list = False
					))
				tt = '\n'.join(tts)
		else:
			gfr = gfrs[0]
			msg = '%s: %s %s (%s)\n' % (
				gfr['unified_abbrev'],
				gfr['unified_val'],
				gmTools.coalesce(gfr['abnormality_indicator'], '', ' (%s)'),
				gmDateTime.pydt_strftime (
					gfr['clin_when'],
					format = '%b %Y'
				)
			)
			tt = _('GFR reported by path lab')

		self._LBL_gfr.SetLabel(msg)
		self._LBL_gfr.SetToolTip(tt)
		self._LBL_gfr.Refresh()
		self.Layout()

	#--------------------------------------------------------
	def __clear_gfr(self):
		self._LBL_gfr.SetLabel(_('GFR: ?'))
		self._LBL_gfr.Refresh()
		self.Layout()

	#--------------------------------------------------------
	# event handling
	#--------------------------------------------------------
	def __register_interests(self):
		gmDispatcher.connect(signal = 'pre_patient_unselection', receiver = self._on_pre_patient_unselection)
		gmDispatcher.connect(signal = 'post_patient_selection', receiver = self._on_post_patient_selection)
		gmDispatcher.connect(signal = 'clin.substance_intake_mod_db', receiver = self._schedule_data_reget)
		gmDispatcher.connect(signal = 'clin.test_result_mod_db', receiver = self._on_test_result_mod)

	#--------------------------------------------------------
	def _on_test_result_mod(self):
		self.__refresh_lab(patient = self._grid_substances.patient)

	#--------------------------------------------------------
	def _on_pre_patient_unselection(self):
		pk_panel = gmCfgDB.get4user (
			option = 'horstspace.medications_plugin.lab_panel',
			workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace
		)
		if pk_panel is None:
			self.__lab_panel = None
		else:
			self.__lab_panel = gmPathLab.cTestPanel(aPK_obj = pk_panel)
		self._grid_substances.patient = None
		self.__refresh_lab(patient = None)
	#--------------------------------------------------------
	def _on_post_patient_selection(self):
		self._schedule_data_reget()
	#--------------------------------------------------------
	def _on_add_button_pressed(self, event):
		self._grid_substances.add_substance()
	#--------------------------------------------------------
	def _on_edit_button_pressed(self, event):
		self._grid_substances.edit_substance()
	#--------------------------------------------------------
	def _on_delete_button_pressed(self, event):
		self._grid_substances.delete_intake()
	#--------------------------------------------------------
	def _on_info_button_pressed(self, event):
		self._grid_substances.show_info_on_entry()
	#--------------------------------------------------------
	def _on_interactions_button_pressed(self, event):
		self._grid_substances.check_interactions()
	#--------------------------------------------------------
	def _on_grouping_selected(self, event):
		event.Skip()
		selected_item_idx = self._CHCE_grouping.GetSelection()
		if selected_item_idx is wx.NOT_FOUND:
			return
		self._grid_substances.grouping_mode = self._CHCE_grouping.GetClientData(selected_item_idx)
	#--------------------------------------------------------
	def _on_show_unapproved_checked(self, event):
		self._grid_substances.filter_show_unapproved = self._CHBOX_show_unapproved.GetValue()
	#--------------------------------------------------------
	def _on_show_inactive_checked(self, event):
		self._grid_substances.filter_show_inactive = self._CHBOX_show_inactive.GetValue()
	#--------------------------------------------------------
	def _on_print_button_pressed(self, event):
		self._grid_substances.print_medication_list()
	#--------------------------------------------------------
	def _on_allergy_button_pressed(self, event):
		self._grid_substances.create_allergy_from_substance()
	#--------------------------------------------------------
	def _on_button_kidneys_pressed(self, event):
		self._grid_substances.show_renal_insufficiency_info()
	#--------------------------------------------------------
	def _on_button_heart_pressed(self, event):
		self._grid_substances.show_cardiac_info()
	#--------------------------------------------------------
	def _on_adr_button_pressed(self, event):
		self._grid_substances.report_ADR()
	#--------------------------------------------------------
	def _on_rx_button_pressed(self, event):
		self._grid_substances.prescribe()

#============================================================
# main
#------------------------------------------------------------
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	from Gnumed.business import gmPersonSearch

	pat = gmPersonSearch.ask_for_patient()
	if pat is None:
		sys.exit()
	gmPerson.set_active_patient(patient = pat)

	#----------------------------------------
	app = wx.PyWidgetTester(size = (600, 300))
	app.SetWidget(cSubstanceIntakeObjectPhraseWheel, -1)
	app.MainLoop()
	#manage_substance_intakes()
