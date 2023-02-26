"""GNUmed current medication display widgets."""

#================================================================
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "SPDX-License-Identifier: GPL-2.0-or-later"


import logging
import sys


import wx
import wx.grid


if __name__ == '__main__':
	sys.path.insert(0, '../../')

from Gnumed.pycommon import gmDispatcher
from Gnumed.pycommon import gmCfgDB
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmDateTime
from Gnumed.pycommon import gmNetworkTools

from Gnumed.business import gmPraxis
from Gnumed.business import gmMedication
from Gnumed.business import gmForms
from Gnumed.business import gmStaff

from Gnumed.wxpython import gmGuiHelpers
from Gnumed.wxpython import gmFormWidgets
from Gnumed.wxpython import gmListWidgets
from Gnumed.wxpython import gmAllergyWidgets
from Gnumed.wxpython import gmSubstanceMgmtWidgets
from Gnumed.wxpython import gmSubstanceIntakeWidgets


_log = logging.getLogger('gm.ui')

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

#================================================================
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
		self.__filter_show_discontinued = False

		self.__grouping2col_labels = {
			'issue': [
				_('Health issue'),
				_('Substance'),
				_('Strength'),
				_('Schedule'),
				_('Timeframe'),
				_('Product'),
				_('Notes')
			],
			'drug_product': [
				_('Product'),
				_('Schedule'),
				_('Substance'),
				_('Strength'),
				_('Timeframe'),
				_('Health issue'),
				_('Notes')
			],
			'episode': [
				_('Episode'),
				_('Substance'),
				_('Strength'),
				_('Schedule'),
				_('Timeframe'),
				_('Product'),
				_('Notes')
			],
			'start': [
				_('Episode'),
				_('Substance'),
				_('Strength'),
				_('Schedule'),
				_('Timeframe'),
				_('Product'),
				_('Notes')
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
		meds = emr.get_intakes (
			order_by = self.__grouping2order_by_clauses[self.__grouping_mode],
			include_inactive = self.__filter_show_discontinued,
			exclude_medications = False,
			exclude_potential_abuses = True
		)
		if not meds:
			return

		self.BeginBatch()

		# columns
		labels = self.__grouping2col_labels[self.__grouping_mode]
		self.AppendCols(numCols = len(labels))
		for col_idx in range(len(labels)):
			self.SetColLabelValue(col_idx, labels[col_idx])

		self.AppendRows(numRows = len(meds))

		# loop over data
		for row_idx in range(len(meds)):
			med = meds[row_idx]
			self.__row_data[row_idx] = med

			if not med['discontinued']:
				atcs = []
				if med['atc_substance'] is not None:
					atcs.append(med['atc_substance'])
				allg = emr.is_allergic_to(atcs = atcs, inns = [med['substance']])
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

			notes_lines = []
			if med['notes4patient']:
				notes_lines.append(_('Patient: %s') % med['notes4patient'])
			if med['notes4provider']:
				notes_lines.append(_('Provider: %s') % med['notes4provider'])
			if notes_lines:
				self.SetCellValue(row_idx, 6, gmTools.wrap(text = '\n'.join(notes_lines), width = 50))

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
		gmSubstanceIntakeWidgets.edit_intake_of_substance(parent = self, intake = None)

	#------------------------------------------------------------
	def edit_substance(self):
		rows = self.get_selected_rows()
		if len(rows) == 0:
			return

		if len(rows) > 1:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot edit more than one substance at once.'), beep = True)
			return

		subst = self.get_selected_data()[0]
		gmSubstanceIntakeWidgets.edit_intake_of_substance(parent = self, intake = subst)

	#------------------------------------------------------------
	def delete_intake(self):
		rows = self.get_selected_rows()
		if len(rows) == 0:
			return

		if len(rows) > 1:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot delete more than one substance at once.'), beep = True)
			return

		intake = self.get_selected_data()[0]
		gmSubstanceIntakeWidgets.delete_substance_intake(parent = self, intake = intake)

	#------------------------------------------------------------
	def create_allergy_from_substance(self):
		rows = self.get_selected_rows()
		if len(rows) == 0:
			return

		if len(rows) > 1:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot create allergy from more than one substance at once.'), beep = True)
			return

		return gmAllergyWidgets.turn_substance_intake_into_allergy (
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
			intake_w_regimen = self.__row_data[row]
		except KeyError:
			return '?'

		emr = self.__patient.emr
		tt = []
		try:
			tt.append(_('Substance intake (%s)   [#%s]                     \n') % (
				gmTools.bool2subst (
					boolean = intake_w_regimen.is_ongoing,
					true_return = _('active'),
					false_return = _('inactive')
				),
				intake_w_regimen['pk_intake']
			))
			atcs = []
			if intake_w_regimen['atc_substance'] is not None:
				atcs.append(intake_w_regimen['atc_substance'])
			if intake_w_regimen['atc_drug_product']:
				atcs.append(intake_w_regimen['atc_drug_product'])
			allg = emr.is_allergic_to(atcs = atcs, inns = [intake_w_regimen['substance']])
			if allg:
				certainty = gmTools.bool2subst(allg['definite'], _('definite'), _('suspected'))
				tt.append('')
				tt.append(' !! ---- Cave ---- !!')
				tt.append(' %s (%s): %s (%s)' % (
					allg['l10n_type'],
					certainty,
					allg['descriptor'],
					gmTools.coalesce(allg['reaction'], '')[:40]
				))
				tt.append('')
			tt.append(' ' + _('Substance: %s   [#%s]') % (intake_w_regimen['substance'], intake_w_regimen['pk_substance']))
			tt.append(' ' + _('Preparation: %s') % intake_w_regimen['l10n_preparation'])
			tt.append(' ' + _('Amount per dose: %s %s') % (intake_w_regimen['amount'], intake_w_regimen['unit']))
			if intake_w_regimen['atc_substance']:
				tt.append(' ' + _('ATC (substance): %s') % intake_w_regimen['atc_substance'])
			tt.append('')
			if intake_w_regimen['drug_product']:
				tt.append(' ' + _('Product name: %s   [#%s]') % (intake_w_regimen['drug_product'], intake_w_regimen['pk_drug_product']))
			if intake_w_regimen['atc_drug_product']:
				tt.append(' ' + _('ATC (drug): %s') % intake_w_regimen['atc_drug'])
			tt.append('')
			if intake_w_regimen['schedule']:
				tt.append(' ' + _('Regimen: %s') % intake_w_regimen['schedule'])
			if intake_w_regimen['planned_duration']:
				duration = ' %s %s' % (gmTools.u_arrow2right, gmDateTime.format_interval(intake_w_regimen['planned_duration'], gmDateTime.acc_days))
			else:
				duration = ''
			tt.append(' ' + _('Started %s%s') % (
				intake_w_regimen.medically_formatted_start,
				duration
			))
			if intake_w_regimen['discontinued']:
				tt.append(' ' + _('Discontinued %s') % gmDateTime.pydt_strftime(intake_w_regimen['discontinued'], '%Y %b %d'))
			if intake_w_regimen['discontinue_reason']:
				tt.append(' ' + _('Reason: %s') % intake_w_regimen['discontinue_reason'])
			tt.append('')
			if intake_w_regimen['notes4patient']:
				tt.append(' ' + _('Patient: %s') % intake_w_regimen['notes4patient'])
			if intake_w_regimen['notes4provider']:
				tt.append(' ' + _('Provider: %s') % intake_w_regimen['notes4provider'])
			tt.append(' ' + _('Episode: %s') % intake_w_regimen['episode'])
			tt.append(' ' + _('Health issue: %s') % intake_w_regimen['health_issue'])
			tt.append('')
			tt.append(_('Revision: #%(row_ver)s, %(mod_when)s by %(mod_by)s.') % ({
				'row_ver': intake_w_regimen['row_version__regimen'],
				'mod_when': gmDateTime.pydt_strftime (
					gmTools.coalesce(intake_w_regimen['modified_when__regimen'], intake_w_regimen['modified_when__intake']),
					'%Y %b %d  %H:%M:%S'
				),
				'mod_by': gmTools.coalesce(intake_w_regimen['modified_by__regimen'], intake_w_regimen['modified_by__intake'])
			}))
		except Exception:
			_log.exception('tooltip error')
			tt.append('tooltip error')
		return '\n'.join(tt)

	#------------------------------------------------------------
	# internal helpers
	#------------------------------------------------------------
	def __init_ui(self):
		self.CreateGrid(0, 1)
		self.EnableEditing(0)
		self.EnableDragGridSize(1)
		self.SetSelectionMode(wx.grid.Grid.wxGridSelectRows)

		self.SetColLabelAlignment(wx.ALIGN_LEFT, wx.ALIGN_CENTRE)

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
	def _get_filter_show_discontinued(self):
		return self.__filter_show_discontinued

	def _set_filter_show_discontinued(self, val):
		self.__filter_show_discontinued = val
		self.repopulate_grid()

	filter_show_discontinued = property(_get_filter_show_discontinued, _set_filter_show_discontinued)

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
		gmSubstanceIntakeWidgets.edit_intake_of_substance(parent = self, intake = data)

#============================================================
# main
#------------------------------------------------------------
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	from Gnumed.business import gmPerson
	from Gnumed.wxpython import gmGuiTest

	#----------------------------------------
	#gmGuiTest.test_widget(cCurrentSubstancesGrid, patient = 12)

	main_frame = gmGuiTest.setup_widget_test_env(patient = 12)
	my_widget = cCurrentSubstancesGrid(main_frame)
	my_widget.patient = gmPerson.gmCurrentPatient()
	wx.GetApp().MainLoop()
