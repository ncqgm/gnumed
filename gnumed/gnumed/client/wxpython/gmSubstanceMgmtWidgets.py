# -*- coding: utf-8 -*-

"""GNUmed drug / substance reference widgets."""

#================================================================
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL v2 or later"

import logging
import sys
import os.path
import decimal


import wx


if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x

from Gnumed.pycommon import gmDispatcher
from Gnumed.pycommon import gmCfgDB
from Gnumed.pycommon import gmShellAPI
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmMatchProvider

from Gnumed.business import gmPerson
from Gnumed.business import gmPraxis
from Gnumed.business import gmMedication
from Gnumed.business import gmDrugDataSources
from Gnumed.business import gmATC

from Gnumed.wxpython import gmGuiHelpers
from Gnumed.wxpython import gmEditArea
from Gnumed.wxpython import gmCfgWidgets
from Gnumed.wxpython import gmListWidgets
from Gnumed.wxpython import gmPhraseWheel


_log = logging.getLogger('gm.ui')

#============================================================
# generic drug database access
#------------------------------------------------------------
def configure_drug_data_source(parent=None):
	gmCfgWidgets.configure_string_from_list_option (
		parent = parent,
		message = _(
			'\n'
			'Please select the default drug data source from the list below.\n'
			'\n'
			'Note that to actually use it you need to have the database installed, too.'
		),
		option = 'external.drug_data.default_source',
		bias = 'user',
		default_value = None,
		choices = list(gmDrugDataSources.drug_data_source_interfaces),
		columns = [_('Drug data source')],
		data = list(gmDrugDataSources.drug_data_source_interfaces),
		caption = _('Configuring default drug data source')
	)

#============================================================
def get_drug_database(parent=None, patient=None):
	opt = 'external.drug_data.default_source'
	wp = gmPraxis.gmCurrentPraxisBranch().active_workplace
	# load from option
	default_db = gmCfgDB.get4workplace(option = opt, workplace = wp)
	# not configured -> try to configure
	if default_db is None:
		gmDispatcher.send('statustext', msg = _('No default drug database configured.'), beep = True)
		configure_drug_data_source(parent = parent)
		default_db = gmCfgDB.get4workplace(option = opt, workplace = wp)
		# still not configured -> return
		if default_db is None:
			gmGuiHelpers.gm_show_error (
				error = _('There is no default drug database configured.'),
				title = _('Jumping to drug database')
			)
			return None

	# now it MUST be configured (either newly or previously)
	# but also *validly* ?
	try:
		drug_db = gmDrugDataSources.drug_data_source_interfaces[default_db]()
	except KeyError:
		# not valid
		_log.error('faulty default drug data source configuration: %s', default_db)
		# try to configure
		configure_drug_data_source(parent = parent)
		default_db = gmCfgDB.get4workplace(option = opt, workplace = wp)
		# deconfigured or aborted (and thusly still misconfigured) ?
		try:
			drug_db = gmDrugDataSources.drug_data_source_interfaces[default_db]()
		except KeyError:
			_log.error('still faulty default drug data source configuration: %s', default_db)
			return None

	if patient is not None:
		drug_db.patient = patient

	return drug_db

#============================================================
def jump_to_drug_database(patient=None):
	drug_db = get_drug_database(patient = patient)
	if drug_db is None:
		return
	drug_db.switch_to_frontend(blocking = False)

#============================================================
def jump_to_ifap_deprecated(import_drugs=False, emr=None):

	if import_drugs and (emr is None):
		gmDispatcher.send('statustext', msg = _('Cannot import drugs from IFAP into chart without chart.'))
		return False

	ifap_cmd = gmCfgDB.get4workplace (
		option = 'external.ifap-win.shell_command',
		workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
		default = 'wine "C:\Ifapwin\WIAMDB.EXE"'
	)
	found, binary = gmShellAPI.detect_external_binary(ifap_cmd)
	if not found:
		gmDispatcher.send('statustext', msg = _('Cannot call IFAP via [%s].') % ifap_cmd)
		return False
	ifap_cmd = binary

	if import_drugs:
		transfer_file = os.path.expanduser(gmCfgDB.get4workplace (
			option = 'external.ifap-win.transfer_file',
			workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
			default = '~/.wine/drive_c/Ifapwin/ifap2gnumed.csv'
		))
		# file must exist for Ifap to write into it
		try:
			open(transfer_file, mode = 'wt').close()
		except IOError:
			_log.exception('Cannot create IFAP <-> GNUmed transfer file [%s]', transfer_file)
			gmDispatcher.send('statustext', msg = _('Cannot create IFAP <-> GNUmed transfer file [%s].') % transfer_file)
			return False

	wx.BeginBusyCursor()
	gmShellAPI.run_command_in_shell(command = ifap_cmd, blocking = import_drugs)
	wx.EndBusyCursor()

	if import_drugs:
		# COMMENT: this file must exist PRIOR to invoking IFAP
		# COMMENT: or else IFAP will not write data into it ...
		try:
			csv_file = open(transfer_file, mode = 'rt', encoding = 'latin1')						# FIXME: encoding unknown
		except Exception:
			_log.exception('cannot access [%s]', transfer_file)
			csv_file = None

		if csv_file is not None:
			import csv
			csv_lines = csv.DictReader (
				csv_file,
				fieldnames = 'PZN Handelsname Form Abpackungsmenge Einheit Preis1 Hersteller Preis2 rezeptpflichtig Festbetrag Packungszahl Packungsgr\xf6\xdfe'.split(),
				delimiter = ';'
			)
			# dummy episode for now
			epi = emr.add_episode(episode_name = _('Current medication'))
			for line in csv_lines:
				narr = '%sx %s %s %s (\u2258 %s %s) von %s (%s)' % (
					line['Packungszahl'].strip(),
					line['Handelsname'].strip(),
					line['Form'].strip(),
					line['Packungsgr\xf6\xdfe'].strip(),
					line['Abpackungsmenge'].strip(),
					line['Einheit'].strip(),
					line['Hersteller'].strip(),
					line['PZN'].strip()
				)
				emr.add_clin_narrative(note = narr, soap_cat = 's', episode = epi)
			csv_file.close()

	return True

#============================================================
# substances widgets
#------------------------------------------------------------
def edit_substance(parent=None, substance=None, single_entry=False):

	if substance is not None:
		if substance.is_in_use_by_patients:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot edit this substance. It is in use.'), beep = True)
			return False

	ea = cSubstanceEAPnl(parent, -1)
	ea.data = substance
	ea.mode = gmTools.coalesce(substance, 'new', 'edit')
	dlg = gmEditArea.cGenericEditAreaDlg2(parent, -1, edit_area = ea, single_entry = single_entry)
	dlg.SetTitle(gmTools.coalesce(substance, _('Adding new substance'), _('Editing substance')))
	if dlg.ShowModal() == wx.ID_OK:
		dlg.DestroyLater()
		return True
	dlg.DestroyLater()
	return False

#------------------------------------------------------------
def manage_substances(parent=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	#------------------------------------------------------------
	def add_from_db(substance):
		drug_db = get_drug_database(parent = parent)
		if drug_db is None:
			return False
		drug_db.import_drugs()
		return True

	#------------------------------------------------------------
	def edit(substance=None):
		return edit_substance(parent = parent, substance = substance, single_entry = (substance is not None))

	#------------------------------------------------------------
	def delete(substance):
		if substance.is_in_use_by_patients:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot delete this substance. It is in use.'), beep = True)
			return False
		return gmMedication.delete_substance(pk_substance = substance['pk_substance'])

	#------------------------------------------------------------
	def get_item_tooltip(substance):
		if not isinstance(substance, gmMedication.cSubstance):
			return None
		return substance.format()

	#------------------------------------------------------------
	def refresh(lctrl):
		substs = gmMedication.get_substances(order_by = 'substance')
		items = [ [
			s['substance'],
			gmTools.coalesce(s['atc'], ''),
			gmTools.coalesce(s['intake_instructions'], ''),
			s['pk_substance']
		] for s in substs ]
		lctrl.set_string_items(items)
		lctrl.set_data(substs)

	#------------------------------------------------------------
	gmListWidgets.get_choices_from_list (
		parent = parent,
		caption = _('Substances registered with GNUmed.'),
		columns = [_('Substance'), 'ATC', _('Instructions'), '#'],
		single_selection = True,
		new_callback = edit,
		edit_callback = edit,
		delete_callback = delete,
		refresh_callback = refresh,
		left_extra_button = (_('Import'), _('Import substances from a drug database.'), add_from_db),
		list_tooltip_callback = get_item_tooltip
	)

#------------------------------------------------------------
from Gnumed.wxGladeWidgets import wxgSubstanceEAPnl

class cSubstanceEAPnl(wxgSubstanceEAPnl.wxgSubstanceEAPnl, gmEditArea.cGenericEditAreaMixin):

	def __init__(self, *args, **kwargs):

		try:
			data = kwargs['substance']
			del kwargs['substance']
		except KeyError:
			data = None

		wxgSubstanceEAPnl.wxgSubstanceEAPnl.__init__(self, *args, **kwargs)
		gmEditArea.cGenericEditAreaMixin.__init__(self)

		# Code using this mixin should set mode and data
		# after instantiating the class:
		self.mode = 'new'
		self.data = data
		if data is not None:
			self.mode = 'edit'

		self.__init_ui()

	#----------------------------------------------------------------
	def __init_ui(self):
		self._LCTRL_loincs.set_columns([_('LOINC'), _('Interval'), _('Comment')])

	#----------------------------------------------------------------
	# generic Edit Area mixin API
	#----------------------------------------------------------------
	def _valid_for_save(self):

		validity = True

		if self._TCTRL_substance.GetValue().strip() == '':
			validity = False
			self.display_tctrl_as_valid(tctrl = self._TCTRL_substance, valid = False)
			self._TCTRL_substance.SetFocus()
		else:
			self.display_tctrl_as_valid(tctrl = self._TCTRL_substance, valid = True)

		if validity is False:
			self.StatusText = _('Cannot save: Substance name missing.')

		return validity

	#----------------------------------------------------------------
	def _save_as_new(self):
		subst = gmMedication.create_substance (
			substance = self._TCTRL_substance.GetValue().strip(),
			atc = self._PRW_atc.GetData()
		)
		subst['intake_instructions'] = self._TCTRL_instructions.GetValue().strip()
		success, data = subst.save()
		if not success:
			err, msg = data
			_log.error(err)
			_log.error(msg)
			self.StatusText = _('Error saving substance. %s') % msg
			return False

		loincs = self._LCTRL_loincs.item_data
		if loincs is not None:
			if len(loincs) > 0:
				subst.loincs = loincs

		self.data = subst
		return True

	#----------------------------------------------------------------
	def _save_as_update(self):
		self.data['substance'] = self._TCTRL_substance.GetValue().strip()
		self.data['atc'] = self._PRW_atc.GetData()
		self.data['intake_instructions'] = self._TCTRL_instructions.GetValue().strip()
		success, data = self.data.save()
		if not success:
			err, msg = data
			_log.error(err)
			_log.error(msg)
			self.StatusText = _('Error saving substance. %s') % msg
			return False

		loincs = self._LCTRL_loincs.item_data
		if loincs is not None:
			if len(loincs) > 0:
				self.data.loincs = loincs

		return True

	#----------------------------------------------------------------
	def _refresh_as_new(self):
		self._TCTRL_substance.SetValue('')
		self._PRW_atc.SetText('', None)
		self._TCTRL_instructions.SetValue('')
		self._PRW_loinc.SetText('', None)
		self._LCTRL_loincs.set_string_items()

		self._TCTRL_substance.SetFocus()

	#----------------------------------------------------------------
	def _refresh_from_existing(self):
		self._TCTRL_substance.SetValue(self.data['substance'])
		self._PRW_atc.SetText(gmTools.coalesce(self.data['atc'], ''), self.data['atc'])
		self._TCTRL_instructions.SetValue(gmTools.coalesce(self.data['intake_instructions'], ''))
		self._PRW_loinc.SetText('', None)
		if len(self.data['loincs']) == 0:
			self._LCTRL_loincs.set_string_items()
		else:
			self._LCTRL_loincs.set_string_items([ [l['loinc'], gmTools.coalesce(l['max_age_str'], ''), gmTools.coalesce(l['comment'], '')] for l in self.data['loincs' ]])
			self._LCTRL_loincs.set_data([ l['loinc'] for l in self.data['loincs'] ])

		self._TCTRL_substance.SetFocus()

	#----------------------------------------------------------------
	def _refresh_as_new_from_existing(self):
		self._refresh_as_new()

	#----------------------------------------------------------------
	# event handlers
	#----------------------------------------------------------------
	def _on_add_loinc_button_pressed(self, event):
		event.Skip()
		if (self._PRW_loinc.GetData() is None) and (self._PRW_loinc.GetValue().strip() == ''):
			return

		if self._PRW_loinc.GetData() is None:
			data = self._PRW_loinc.GetValue().strip().split(':')[0]
			item = [data, '', '']
		else:
			data = self._PRW_loinc.GetData()
			item = [data, '', '']
		self._LCTRL_loincs.append_string_items_and_data([item], new_data = [data], allow_dupes = False)

	#----------------------------------------------------------------
	def _on_remove_loincs_button_pressed(self, event):
		event.Skip()

#------------------------------------------------------------
class cSubstancePhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):

		gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)
		query = """
			SELECT DISTINCT ON (list_label)
				list_label,
				field_label,
				data
			FROM (
				SELECT
					description AS list_label,
					description AS field_label,
					pk AS data
				FROM ref.substance
				WHERE
					description %(fragment_condition)s

				UNION ALL

				SELECT
					term AS list_label,
					term AS field_label,
					NULL::integer AS data
				FROM ref.atc
				WHERE
					term %(fragment_condition)s

			) AS candidates
			ORDER BY list_label
			LIMIT 50
		"""
		mp = gmMatchProvider.cMatchProvider_SQL2(queries = query)
		mp.setThresholds(1, 2, 4)
#		mp.word_separators = '[ \t=+&:@]+'
		self.SetToolTip(_('The substance name.'))
		self.matcher = mp
		self.selection_only = False
		self.phrase_separators = None

	#--------------------------------------------------------
	def _data2instance(self, link_obj=None):
		return gmMedication.cSubstance(aPK_obj = self.GetData(as_instance = False, can_create = False))

#============================================================
# substance dose widgets
#------------------------------------------------------------
def edit_substance_dose(parent=None, substance_dose=None, single_entry=False):

	if substance_dose is not None:
		if substance_dose.is_in_use_by_patients:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot edit this substance. It is in use.'), beep = True)
			return False

	ea = cSubstanceDoseEAPnl(parent, -1)
	ea.data = substance_dose
	ea.mode = gmTools.coalesce(substance_dose, 'new', 'edit')
	dlg = gmEditArea.cGenericEditAreaDlg2(parent, -1, edit_area = ea, single_entry = single_entry)
	dlg.SetTitle(gmTools.coalesce(substance_dose, _('Adding new substance dose'), _('Editing substance dose')))
	if dlg.ShowModal() == wx.ID_OK:
		dlg.DestroyLater()
		return True
	dlg.DestroyLater()
	return False

#------------------------------------------------------------
def manage_substance_doses(parent=None, vaccine_indications_only=False):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	#------------------------------------------------------------
	def add_from_db(substance):
		drug_db = get_drug_database(parent = parent)
		if drug_db is None:
			return False
		drug_db.import_drugs()
		return True

	#------------------------------------------------------------
	def edit(substance_dose=None):
		return edit_substance_dose(parent = parent, substance_dose = substance_dose, single_entry = (substance_dose is not None))

	#------------------------------------------------------------
	def delete(substance_dose):
		if substance_dose.is_in_use_by_patients:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot delete this substance. It is in use.'), beep = True)
			return False
		return gmMedication.delete_substance_dose(pk_dose = substance_dose['pk_dose'])

	#------------------------------------------------------------
	def refresh(lctrl):
		if vaccine_indications_only:
			substs = [ s for s in gmMedication.get_substance_doses(order_by = 'substance') if gmTools.coalesce(s['atc_substance'], '').startswith('J07') ]
		else:
			substs = gmMedication.get_substance_doses(order_by = 'substance')
		items = [ [
			s['substance'],
			s['amount'],
			s.formatted_units,
			gmTools.coalesce(s['atc_substance'], ''),
			gmTools.coalesce(s['intake_instructions'], ''),
			s['pk_dose']
		] for s in substs ]
		lctrl.set_string_items(items)
		lctrl.set_data(substs)

	#------------------------------------------------------------
	def get_item_tooltip(substance_dose):
		if not isinstance(substance_dose, gmMedication.cSubstanceDose):
			return None
		return substance_dose.format(include_loincs = True)

	#------------------------------------------------------------
	return gmListWidgets.get_choices_from_list (
		parent = parent,
		caption = _('Substance doses registered with GNUmed.'),
		columns = [_('Substance'), _('Amount'), _('Unit'), 'ATC', _('Instructions'), '#'],
		single_selection = False,
		can_return_empty = False,
		new_callback = edit,
		edit_callback = edit,
		delete_callback = delete,
		refresh_callback = refresh,
		left_extra_button = (_('Import'), _('Import substance doses from a drug database.'), add_from_db),
		list_tooltip_callback = get_item_tooltip
	)

#------------------------------------------------------------
from Gnumed.wxGladeWidgets import wxgSubstanceDoseEAPnl

class cSubstanceDoseEAPnl(wxgSubstanceDoseEAPnl.wxgSubstanceDoseEAPnl, gmEditArea.cGenericEditAreaMixin):

	def __init__(self, *args, **kwargs):

		try:
			data = kwargs['substance']
			del kwargs['substance']
		except KeyError:
			data = None

		wxgSubstanceDoseEAPnl.wxgSubstanceDoseEAPnl.__init__(self, *args, **kwargs)
		gmEditArea.cGenericEditAreaMixin.__init__(self)

		# Code using this mixin should set mode and data
		# after instantiating the class:
		self.mode = 'new'
		self.data = data
		if data is not None:
			self.mode = 'edit'

		self.__init_ui()

	#----------------------------------------------------------------
	def __init_ui(self):
		self._PRW_substance.add_callback_on_modified(callback = self.__refresh_info)
		self._PRW_substance.add_callback_on_selection(callback = self.__refresh_info)
		self._TCTRL_amount.add_callback_on_modified(callback = self.__refresh_info)
		self._PRW_unit.add_callback_on_modified(callback = self.__refresh_info)
		self._PRW_unit.add_callback_on_selection(callback = self.__refresh_info)
		self._PRW_dose_unit.add_callback_on_modified(callback = self.__refresh_info)
		self._PRW_dose_unit.add_callback_on_selection(callback = self.__refresh_info)

	#----------------------------------------------------------------
	def __refresh_info(self, change='dummy'):
		subst = self._PRW_substance.GetValue().strip()
		if subst == '':
			subst = '?'
		amount = self._TCTRL_amount.GetValue().strip()
		if amount == '':
			amount = '?'
		unit = self._PRW_unit.GetValue().strip()
		if unit == '':
			unit = '?'
		dose_unit = self._PRW_dose_unit.GetValue().strip()
		if dose_unit == '':
			dose_unit = _('<delivery unit>')
		self._LBL_info.SetLabel('%s %s %s / %s' % (subst, amount, unit, dose_unit))
		self.Refresh()

	#----------------------------------------------------------------
	# generic Edit Area mixin API
	#----------------------------------------------------------------
	def _valid_for_save(self):

		validity = True

		if self._PRW_substance.GetValue().strip() == '':
			validity = False
			self._PRW_substance.display_as_valid(valid = False)
			self._PRW_substance.SetFocus()
		else:
			self._PRW_substance.display_as_valid(valid = True)

		try:
			decimal.Decimal(self._TCTRL_amount.GetValue().strip().replace(',', '.'))
			self.display_tctrl_as_valid(tctrl = self._TCTRL_amount, valid = True)
		except (TypeError, decimal.InvalidOperation):
			validity = False
			self.display_tctrl_as_valid(tctrl = self._TCTRL_amount, valid = False)
			self._TCTRL_amount.SetFocus()

		if self._PRW_unit.GetValue().strip() == '':
			validity = False
			self._PRW_unit.display_as_valid(valid = False)
			self._PRW_unit.SetFocus()
		else:
			self._PRW_unit.display_as_valid(valid = True)

		if validity is False:
			self.StatusText = _('Cannot save substance dose. Missing essential input.')

		return validity

	#----------------------------------------------------------------
	def _save_as_new(self):
		pk_subst = self._PRW_substance.GetData()
		dose = gmMedication.create_substance_dose (
			pk_substance = pk_subst,
			substance = self._PRW_substance.GetValue().strip() if (pk_subst is None) else None,
			amount = decimal.Decimal(self._TCTRL_amount.GetValue().strip().replace(',', '.')),
			unit = gmTools.coalesce(self._PRW_unit.GetData(), self._PRW_unit.GetValue().strip(), function4value = ('strip', None)),
			dose_unit = gmTools.coalesce(self._PRW_dose_unit.GetData(), self._PRW_dose_unit.GetValue().strip(), function4value = ('strip', None))
		)
		success, data = dose.save()
		if not success:
			err, msg = data
			_log.error(err)
			_log.error(msg)
			self.StatusText = _('Cannot create substance dose. %s') % msg
			return False

		self.data = dose
		return True

	#----------------------------------------------------------------
	def _save_as_update(self):
		#self.data['pk_substance'] = self._PRW_substance.GetData()
		self.data['amount'] = decimal.Decimal(self._TCTRL_amount.GetValue().strip().replace(',', '.'))
		self.data['unit'] = gmTools.coalesce(self._PRW_unit.GetData(), self._PRW_unit.GetValue().strip(), function4value = ('strip', None))
		self.data['dose_unit'] = gmTools.coalesce(self._PRW_dose_unit.GetData(), self._PRW_dose_unit.GetValue().strip(), function4value = ('strip', None))
		success, data = self.data.save()

		if not success:
			err, msg = data
			_log.error(err)
			_log.error(msg)
			self.StatusText = _('Cannot save substance dose. %s') % msg
			return False

		return True

	#----------------------------------------------------------------
	def _refresh_as_new(self):
		self._PRW_substance.SetText('', None)
		self._TCTRL_amount.SetValue('')
		self._PRW_unit.SetText('', None)
		self._PRW_dose_unit.SetText('', None)
		self._LBL_info.SetLabel('')

		self._PRW_substance.SetFocus()

	#----------------------------------------------------------------
	def _refresh_from_existing(self):
		self._PRW_substance.SetText(self.data['substance'], self.data['pk_substance'])
		self._PRW_substance.Disable()
		self._TCTRL_amount.SetValue('%s' % self.data['amount'])
		self._PRW_unit.SetText(self.data['unit'], self.data['unit'])
		self._PRW_dose_unit.SetText(gmTools.coalesce(self.data['dose_unit'], ''), self.data['dose_unit'])

		self._PRW_substance.SetFocus()

	#----------------------------------------------------------------
	def _refresh_as_new_from_existing(self):
		self._refresh_as_new()

#============================================================
# drug component widgets
#------------------------------------------------------------
def manage_drug_components(parent=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	#------------------------------------------------------------
	def edit(component=None):
		substance_dose = gmMedication.cSubstanceDose(aPK_obj = component['pk_dose'])
		return edit_substance_dose(parent = parent, substance_dose = substance_dose, single_entry = True)

	#------------------------------------------------------------
	def delete(component):
		if component.is_in_use_by_patients:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot remove this component from the drug. It is in use.'), beep = True)
			return False
		return component.containing_drug.remove_component(pk_component = component['pk_component'])

	#------------------------------------------------------------
	def refresh(lctrl):
		comps = gmMedication.get_drug_components()
		items = [ [
			'%s%s' % (c['substance'], gmTools.coalesce(c['atc_substance'], '', ' [%s]')),
			'%s %s' % (c['amount'], c.formatted_units),
			'%s%s' % (c['drug_product'], gmTools.coalesce(c['atc_drug'], '', ' [%s]')),
			c['l10n_preparation'],
			gmTools.coalesce(c['external_code'], '', '%%s [%s]' % c['external_code_type']),
			c['pk_component']
		] for c in comps ]
		lctrl.set_string_items(items)
		lctrl.set_data(comps)

	#------------------------------------------------------------
	def get_item_tooltip(component):
		if not isinstance(component, gmMedication.cDrugComponent):
			return None
		return component.format(include_loincs = True)

	#------------------------------------------------------------
	gmListWidgets.get_choices_from_list (
		parent = parent,
		caption = _('Drug components currently known to GNUmed'),
		columns = [_('Component'), _('Strength'), _('Product name'), _('Preparation'), _('Code'), '#'],
		single_selection = True,
		#new_callback = edit,
		edit_callback = edit,
		delete_callback = delete,
		refresh_callback = refresh,
		list_tooltip_callback = get_item_tooltip
	)

#------------------------------------------------------------
def edit_drug_component(parent=None, drug_component=None, single_entry=False):
	ea = cDrugComponentEAPnl(parent, -1)
	ea.data = drug_component
	ea.mode = gmTools.coalesce(drug_component, 'new', 'edit')
	dlg = gmEditArea.cGenericEditAreaDlg2(parent, -1, edit_area = ea, single_entry = single_entry)
	dlg.SetTitle(gmTools.coalesce(drug_component, _('Adding new drug component'), _('Editing drug component')))
	if dlg.ShowModal() == wx.ID_OK:
		dlg.DestroyLater()
		return True
	dlg.DestroyLater()
	return False

#------------------------------------------------------------
from Gnumed.wxGladeWidgets import wxgDrugComponentEAPnl

class cDrugComponentEAPnl(wxgDrugComponentEAPnl.wxgDrugComponentEAPnl, gmEditArea.cGenericEditAreaMixin):

	def __init__(self, *args, **kwargs):

		try:
			data = kwargs['component']
			del kwargs['component']
		except KeyError:
			data = None

		wxgDrugComponentEAPnl.wxgDrugComponentEAPnl.__init__(self, *args, **kwargs)
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
		if self.data is not None:
			if self.data['is_in_use']:
				self.StatusText = _('Cannot edit drug component. It is in use.')
				return False

		validity = True

		if self._PRW_substance.GetData() is None:
			validity = False
			self._PRW_substance.display_as_valid(False)
		else:
			self._PRW_substance.display_as_valid(True)

		val = self._TCTRL_amount.GetValue().strip().replace(',', '.', 1)
		try:
			decimal.Decimal(val)
			self.display_tctrl_as_valid(tctrl = self._TCTRL_amount, valid = True)
		except Exception:
			validity = False
			self.display_tctrl_as_valid(tctrl = self._TCTRL_amount, valid = False)

		if self._PRW_unit.GetValue().strip() == '':
			validity = False
			self._PRW_unit.display_as_valid(False)
		else:
			self._PRW_unit.display_as_valid(True)

		if validity is False:
			self.StatusText = _('Cannot save drug component. Invalid or missing essential input.')

		return validity
	#----------------------------------------------------------------
	def _save_as_new(self):
		# save the data as a new instance
		data = {}
		data[''] = 1
		data[''] = 1
#		data.save()

		# must be done very late or else the property access
		# will refresh the display such that later field
		# access will return empty values
#		self.data = data
		return False
		return True
	#----------------------------------------------------------------
	def _save_as_update(self):
		self.data['pk_dose'] = self._PRW_substance.GetData()
		self.data['amount'] = decimal.Decimal(self._TCTRL_amount.GetValue().strip().replace(',', '.', 1))
		self.data['unit'] = self._PRW_unit.GetValue().strip()
		return self.data.save()

	#----------------------------------------------------------------
	def _refresh_as_new(self):
		self._TCTRL_product_name.SetValue('')
		self._TCTRL_components.SetValue('')
		self._TCTRL_codes.SetValue('')
		self._PRW_substance.SetText('', None)
		self._TCTRL_amount.SetValue('')
		self._PRW_unit.SetText('', None)

		self._PRW_substance.SetFocus()

	#----------------------------------------------------------------
	def _refresh_from_existing(self):
		self._TCTRL_product_name.SetValue('%s (%s)' % (self.data['drug_product'], self.data['l10n_preparation']))
		self._TCTRL_components.SetValue(' / '.join(self.data.containing_drug['components']))
		details = []
		if self.data['atc_drug'] is not None:
			details.append('ATC: %s' % self.data['atc_drug'])
		if self.data['external_code_product'] is not None:
			details.append('%s: %s' % (self.data['external_code_type_product'], self.data['external_code_product']))
		self._TCTRL_codes.SetValue('; '.join(details))

		self._PRW_substance.SetText(self.data['substance'], self.data['pk_dose'])
		self._TCTRL_amount.SetValue('%s' % self.data['amount'])
		self._PRW_unit.SetText(self.data['unit'], self.data['unit'])

		self._PRW_substance.SetFocus()

	#----------------------------------------------------------------
	def _refresh_as_new_from_existing(self):
		#self._PRW_drug_product.SetText(u'', None)
		#self._TCTRL_prep.SetValue(u'')
		#self._TCTRL_product_name_details.SetValue(u'')
		self._PRW_substance.SetText('', None)
		self._TCTRL_amount.SetValue('')
		self._PRW_unit.SetText('', None)

		self._PRW_substance.SetFocus()

#------------------------------------------------------------
class cDrugComponentPhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):

		mp = gmMedication.cDrugComponentMatchProvider()
		mp.setThresholds(2, 3, 4)
		gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)
		self.SetToolTip(_('A drug component with optional strength.'))
		self.matcher = mp
		self.selection_only = False
	#--------------------------------------------------------
	def _data2instance(self, link_obj=None):
		return gmMedication.cDrugComponent(aPK_obj = self.GetData(as_instance = False, can_create = False))

#============================================================
# drug products widgets
#------------------------------------------------------------
def edit_drug_product(parent=None, drug_product=None, single_entry=False):

	if drug_product is not None:
		if drug_product.is_in_use:
			gmGuiHelpers.gm_show_info (
				title = _('Editing drug'),
				info = _(
					'Cannot edit the drug product\n'
					'\n'
					' "%s" (%s)\n'
					'\n'
					'because it is currently taken by patients.\n'
				) % (drug_product['drug_product'], drug_product['l10n_preparation'])
			)
			return False

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	#--------------------------------------------
	def manage_substances(drug):
		manage_substance_doses(parent = parent)

	#--------------------------------------------
	ea = cDrugProductEAPnl(parent, -1)
	ea.data = drug_product
	ea.mode = gmTools.coalesce(drug_product, 'new', 'edit')
	dlg = gmEditArea.cGenericEditAreaDlg2(parent, -1, edit_area = ea, single_entry = single_entry)
	dlg.SetTitle(gmTools.coalesce(drug_product, _('Adding new drug product'), _('Editing drug product')))
	dlg.left_extra_button = (
		_('Substances'),
		_('Manage substances'),
		manage_substances
	)
	if dlg.ShowModal() == wx.ID_OK:
		dlg.DestroyLater()
		return True
	dlg.DestroyLater()
	return False

#------------------------------------------------------------
def manage_drug_products(parent=None, ignore_OK_button=False):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	#------------------------------------------------------------
	def add_from_db(drug):
		drug_db = get_drug_database(parent = parent)
		if drug_db is None:
			return False
		drug_db.import_drugs()
		return True

	#------------------------------------------------------------
	def get_tooltip(product=None):
		return product.format(include_component_details = True)

	#------------------------------------------------------------
	def edit(product):
		if product is not None:
			if product.is_in_use_as_vaccine:
				gmGuiHelpers.gm_show_info (
					title = _('Editing medication'),
					info = _(
						'Cannot edit the vaccine product\n'
						'\n'
						' "%s" (%s)\n'
						'\n'
						'because it is in use.'
					) % (product['drug_product'], product['l10n_preparation'])
				)
				return False

		return edit_drug_product(parent = parent, drug_product = product, single_entry = True)

	#------------------------------------------------------------
	def delete(product):
		if not product.delete_associated_vaccine():
			gmGuiHelpers.gm_show_info (
				title = _('Deleting vaccine'),
				info = _(
					'Cannot delete the vaccine product\n'
					'\n'
					' "%s" (%s)\n'
					'\n'
					'because it is in use.'
				) % (product['drug_product'], product['l10n_preparation'])
			)
			return False

		gmMedication.delete_drug_product(pk_drug_product = product['pk_drug_product'])
		return True

	#------------------------------------------------------------
	def new():
		return edit_drug_product(parent = parent, drug_product = None, single_entry = False)

	#------------------------------------------------------------
	def refresh(lctrl):
		drugs = gmMedication.get_drug_products()
		items = [ [
			'%s%s' % (
				d['drug_product'],
				gmTools.bool2subst(d['is_fake_product'], ' (%s)' % _('fake'), '')
			),
			d['l10n_preparation'],
			gmTools.coalesce(d['atc'], ''),
			'; '.join([ '%s %s%s' % (
				c['substance'],
				c['amount'],
				gmMedication.format_units(c['unit'], c['dose_unit'])
			) for c in d['components']]),
			gmTools.coalesce(d['external_code'], '', '%%s [%s]' % d['external_code_type']),
			d['pk_drug_product']
		] for d in drugs ]
		lctrl.set_string_items(items)
		lctrl.set_data(drugs)

	#------------------------------------------------------------
	gmListWidgets.get_choices_from_list (
		parent = parent,
		caption = _('Drug products currently known to GNUmed.'),
		columns = [_('Name'), _('Preparation'), _('ATC'), _('Components'), _('Code'), '#'],
		single_selection = True,
		ignore_OK_button = ignore_OK_button,
		refresh_callback = refresh,
		new_callback = new,
		edit_callback = edit,
		delete_callback = delete,
		list_tooltip_callback = get_tooltip,
		left_extra_button = (_('Import'), _('Import substances and products from a drug database.'), add_from_db)
		#, middle_extra_button = (_('Clone'), _('Clone selected drug into a new entry for editing.'), clone_from_existing)
		#, right_extra_button = (_('Reassign'), _('Reassign all patients taking the selected drug to another drug.'), reassign_patients)
	)

#------------------------------------------------------------
def manage_components_of_drug_product(parent=None, product=None):

	if product is not None:
		if product.is_in_use:
			gmGuiHelpers.gm_show_info (
				title = _('Managing components of a drug'),
				info = _(
					'Cannot manage the components of the drug product\n'
					'\n'
					' "%s" (%s)\n'
					'\n'
					'because it is currently taken by patients.\n'
				) % (product['drug_product'], product['l10n_preparation'])
			)
			return False

	#--------------------------------------------------------
	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	#--------------------------------------------------------
#	def manage_substances():
#		pass

	#--------------------------------------------------------
	if product is None:
		msg = _('Pick the substance doses which are components of this drug.')
		right_col = _('Components of drug')
		comp_doses = []
	else:
		right_col = '%s (%s)' % (product['drug_product'], product['l10n_preparation'])
		msg = _(
			'Adjust the components of "%s"\n'
			'\n'
			'The drug must contain at least one component. Any given\n'
			'substance can only be included once per drug.'
		) % right_col
		comp_doses = [ comp.substance_dose for comp in product.components ]

	doses = gmMedication.get_substance_doses(order_by = 'substance')
	choices = [ '%s %s %s' % (d['substance'], d['amount'], d.formatted_units) for d in doses ]
	picks = [ '%s %s %s' % (d['substance'], d['amount'], d.formatted_units) for d in comp_doses ]

	picker = gmListWidgets.cItemPickerDlg (
		parent,
		-1,
		title = _('Managing components of a drug ...'),
		msg = msg
	)
	picker.set_columns(['Substance doses'], [right_col])
	picker.set_choices(choices = choices, data = doses)
	picker.set_picks(picks = picks, data = comp_doses)
#	picker.extra_button = (
#		_('Substances'),
#		_('Manage list of substances'),
#		manage_substances
#	)

	btn_pressed = picker.ShowModal()
	doses2set = picker.get_picks()
	picker.DestroyLater()

	if btn_pressed != wx.ID_OK:
		return (False, None)

	if product is not None:
		product.set_substance_doses_as_components(substance_doses = doses2set)

	return (True, doses2set)

#------------------------------------------------------------
from Gnumed.wxGladeWidgets import wxgDrugProductEAPnl

class cDrugProductEAPnl(wxgDrugProductEAPnl.wxgDrugProductEAPnl, gmEditArea.cGenericEditAreaMixin):

	def __init__(self, *args, **kwargs):
		try:
			data = kwargs['drug']
			del kwargs['drug']
		except KeyError:
			data = None

		wxgDrugProductEAPnl.wxgDrugProductEAPnl.__init__(self, *args, **kwargs)
		gmEditArea.cGenericEditAreaMixin.__init__(self)

		self.__component_doses = []

		self.mode = 'new'
		self.data = data
		if data is not None:
			self.mode = 'edit'
			self.__component_doses = data.components_as_doses

		#self.__init_ui()
	#----------------------------------------------------------------
#	def __init_ui(self):
		# adjust external type PRW
	#----------------------------------------------------------------
	# generic Edit Area mixin API
	#----------------------------------------------------------------
	def _valid_for_save(self):

		if self.data is not None:
			if self.data.is_in_use:
				self.StatusText = _('Cannot edit drug product. It is in use.')
				return False

		validity = True

		product_name = self._PRW_product_name.GetValue().strip()
		if product_name == '':
			validity = False
			self._PRW_product_name.display_as_valid(False)
		else:
			self._PRW_product_name.display_as_valid(True)

		preparation = self._PRW_preparation.GetValue().strip()
		if preparation == '':
			validity = False
			self._PRW_preparation.display_as_valid(False)
		else:
			self._PRW_preparation.display_as_valid(True)

		if validity is True:
			# dupe ?
			drug = gmMedication.get_drug_by_name(product_name = product_name, preparation = preparation)
			if drug is not None:
				if self.mode != 'edit':
					validity = False
					self._PRW_product_name.display_as_valid(False)
					self._PRW_preparation.display_as_valid(False)
					gmGuiHelpers.gm_show_error (
						title = _('Checking product data'),
						error = _(
							'The information you entered:\n'
							'\n'
							' [%s %s]\n'
							'\n'
							'already exists as a drug product.'
						) % (product_name, preparation)
					)
			else:
				# lacking components ?
				self._TCTRL_components.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_BACKGROUND))
				if len(self.__component_doses) == 0:
					wants_empty = gmGuiHelpers.gm_show_question (
						title = _('Checking product data'),
						question = _(
							'You have not selected any substances\n'
							'as drug components.\n'
							'\n'
							'Without components you will not be able to\n'
							'use this drug for documenting patient care.\n'
							'\n'
							'Are you sure you want to save\n'
							'it without components ?'
						)
					)
					if not wants_empty:
						validity = False
						self.display_ctrl_as_valid(ctrl = self._TCTRL_components, valid = False)

		if validity is False:
			self.StatusText = _('Cannot save drug product. Invalid or missing essential input.')

		return validity

	#----------------------------------------------------------------
	def _save_as_new(self):
		drug = gmMedication.create_drug_product (
			product_name = self._PRW_product_name.GetValue().strip(),
			preparation = gmTools.coalesce (
				self._PRW_preparation.GetData(),
				self._PRW_preparation.GetValue()
			).strip(),
			doses = self.__component_doses if (len(self.__component_doses) > 0) else None,
			return_existing = True
		)
		drug['is_fake_product'] = self._CHBOX_is_fake.GetValue()
		drug['atc'] = self._PRW_atc.GetData()
		code = self._TCTRL_external_code.GetValue().strip()
		if code != '':
			drug['external_code'] = code
			drug['external_code_type'] = self._PRW_external_code_type.GetData().strip()
		drug.save()
		self.data = drug
		return True

	#----------------------------------------------------------------
	def _save_as_update(self):
		self.data['drug_product'] = self._PRW_product_name.GetValue().strip()
		self.data['preparation'] = gmTools.coalesce (
			self._PRW_preparation.GetData(),
			self._PRW_preparation.GetValue()
		).strip()
		self.data['is_fake_product'] = self._CHBOX_is_fake.GetValue()
		self.data['atc'] = self._PRW_atc.GetData()
		code = self._TCTRL_external_code.GetValue().strip()
		if code != '':
			self.data['external_code'] = code
			self.data['external_code_type'] = self._PRW_external_code_type.GetData().strip()
		success, data = self.data.save()
		if not success:
			err, msg = data
			_log.error('problem saving')
			_log.error('%s', err)
			_log.error('%s', msg)
		return (success is True)

	#----------------------------------------------------------------
	def _refresh_as_new(self):
		self._PRW_product_name.SetText('', None)
		self._PRW_preparation.SetText('', None)
		self._CHBOX_is_fake.SetValue(False)
		self._TCTRL_components.SetValue('')
		self._PRW_atc.SetText('', None)
		self._TCTRL_external_code.SetValue('')
		self._PRW_external_code_type.SetText('', None)

		self._PRW_product_name.SetFocus()

		self.__component_doses = []

	#----------------------------------------------------------------
	def _refresh_as_new_from_existing(self):
		self._refresh_as_new()

	#----------------------------------------------------------------
	def _refresh_from_existing(self):
		self._PRW_product_name.SetText(self.data['drug_product'], self.data['pk_drug_product'])
		self._PRW_preparation.SetText(self.data['preparation'], self.data['preparation'])
		self._CHBOX_is_fake.SetValue(self.data['is_fake_product'])
		comp_str = ''
		if len(self.data['components']) > 0:
			comp_str = '- %s' % '\n- '.join([ '%s %s%s' % (c['substance'], c['amount'], gmMedication.format_units(c['unit'], c['dose_unit'])) for c in self.data['components'] ])
		self._TCTRL_components.SetValue(comp_str)
		self._PRW_atc.SetText(gmTools.coalesce(self.data['atc'], ''), self.data['atc'])
		self._TCTRL_external_code.SetValue(gmTools.coalesce(self.data['external_code'], ''))
		t = gmTools.coalesce(self.data['external_code_type'], '')
		self._PRW_external_code_type.SetText(t, t)

		self._PRW_product_name.SetFocus()

		self.__component_doses = self.data.components_as_doses

	#----------------------------------------------------------------
	# event handler
	#----------------------------------------------------------------
	def _on_manage_components_button_pressed(self, event):
		event.Skip()
		if self.mode == 'new_from_existing':
			product = None
		else:
			product = self.data
		OKed, doses = manage_components_of_drug_product(parent = self, product = product)
		if OKed is True:
			self.__component_doses = doses
			comp_str = ''
			if len(doses) > 0:
				comp_str = '- %s' % '\n- '.join([ '%s %s%s' % (d['substance'], d['amount'], gmMedication.format_units(d['unit'], d['dose_unit'])) for d in doses ])
			self._TCTRL_components.SetValue(comp_str)

#------------------------------------------------------------
class cDrugProductPhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):

		query = """
			SELECT
				pk
					AS data,
				(description || ' (' || preparation || ')' || coalesce(' [' || atc_code || ']', ''))
					AS list_label,
				(description || ' (' || preparation || ')' || coalesce(' [' || atc_code || ']', ''))
					AS field_label
			FROM ref.drug_product
			WHERE description %(fragment_condition)s
			ORDER BY list_label
			LIMIT 50"""

		mp = gmMatchProvider.cMatchProvider_SQL2(queries = query)
		mp.setThresholds(2, 3, 4)
		gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)
		self.SetToolTip(_(
			'Product name of the drug.\n'
			'\n'
			'Note: a product name will need to be linked to\n'
			'one or more components before it can be used,\n'
			'except in the case of vaccines.'
		))
		self.matcher = mp
		self.selection_only = False

#============================================================
# single-component generic drugs
# drug name is forced to substance + amount + unit + dose_unit
#------------------------------------------------------------
def edit_single_component_generic_drug(parent=None, drug=None, single_entry=False, fields=None, return_drug=False):

#	if drug is not None:
#		if drug.is_in_use:
#			gmGuiHelpers.gm_show_info (
#				title = _('Editing single-component generic drug'),
#				info = _(
#					'Cannot edit the single-component generic drug\n'
#					'\n'
#					' "%s" (%s)\n'
#					'\n'
#					'because it is currently taken by patients.\n'
#				) % (drug['drug_product'], drug['l10n_preparation'])
#			)
#			return False

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

#	#--------------------------------------------
#	def manage_substances(drug):
#		manage_substance_doses(parent = parent)

	#--------------------------------------------
	ea = cSingleComponentGenericDrugEAPnl(parent, -1)
	ea.data = drug
	ea.mode = gmTools.coalesce(drug, 'new', 'edit')
	dlg = gmEditArea.cGenericEditAreaDlg2(parent, -1, edit_area = ea, single_entry = single_entry)
	if fields is not None:
		ea.set_fields(fields)
	dlg.SetTitle(gmTools.coalesce(drug, _('Adding new single-component generic drug'), _('Editing single-component generic drug')))
#	dlg.left_extra_button = (
#		_('Substances'),
#		_('Manage substances'),
#		manage_substances
#	)
	if dlg.ShowModal() == wx.ID_OK:
		drug = ea.data
		dlg.DestroyLater()
		if return_drug:
			return drug
		return True
	dlg.DestroyLater()
	if return_drug:
		return None
	return False

#------------------------------------------------------------
def manage_single_component_generic_drugs(parent=None, ignore_OK_button=False):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	#------------------------------------------------------------
	def add_from_db(drug):
		drug_db = get_drug_database(parent = parent)
		if drug_db is None:
			return False
		drug_db.import_drugs()
		return True

	#------------------------------------------------------------
	def get_tooltip(product=None):
		return product.format(include_component_details = True)

	#------------------------------------------------------------
	def edit(product):
		if product is not None:
			if product.is_vaccine:
				gmGuiHelpers.gm_show_info (
					title = _('Editing medication'),
					info = _(
						'Cannot edit the medication\n'
						'\n'
						' "%s" (%s)\n'
						'\n'
						'because it is a vaccine. Please edit it\n'
						'from the vaccine management section !\n'
					) % (product['drug_product'], product['l10n_preparation'])
				)
				return False

		return edit_drug_product(parent = parent, drug_product = product, single_entry = True)

	#------------------------------------------------------------
	def delete(product):
		if product.is_vaccine:
			gmGuiHelpers.gm_show_info (
				title = _('Deleting medication'),
				info = _(
					'Cannot delete the medication\n'
					'\n'
					' "%s" (%s)\n'
					'\n'
					'because it is a vaccine. Please delete it\n'
					'from the vaccine management section !\n'
				) % (product['drug_product'], product['l10n_preparation'])
			)
			return False
		gmMedication.delete_drug_product(pk_drug_product = product['pk_drug_product'])
		return True

	#------------------------------------------------------------
	def new():
		return edit_drug_product(parent = parent, drug_product = None, single_entry = False)

	#------------------------------------------------------------
	def refresh(lctrl):
		drugs = gmMedication.get_drug_products()
		items = [ [
			'%s%s' % (
				d['drug_product'],
				gmTools.bool2subst(d['is_fake_product'], ' (%s)' % _('fake'), '')
			),
			d['l10n_preparation'],
			gmTools.coalesce(d['atc'], ''),
			'; '.join([ '%s %s%s' % (
				c['substance'],
				c['amount'],
				gmMedication.format_units(c['unit'], c['dose_unit'])
			) for c in d['components']]),
			gmTools.coalesce(d['external_code'], '', '%%s [%s]' % d['external_code_type']),
			d['pk_drug_product']
		] for d in drugs ]
		lctrl.set_string_items(items)
		lctrl.set_data(drugs)

	#------------------------------------------------------------
	gmListWidgets.get_choices_from_list (
		parent = parent,
		caption = _('Drug products currently known to GNUmed.'),
		columns = [_('Name'), _('Preparation'), _('ATC'), _('Components'), _('Code'), '#'],
		single_selection = True,
		ignore_OK_button = ignore_OK_button,
		refresh_callback = refresh,
		new_callback = new,
		edit_callback = edit,
		delete_callback = delete,
		list_tooltip_callback = get_tooltip,
		#left_extra_button = (_('Import'), _('Import substances and products from a drug database.'), add_from_db)
		#, middle_extra_button = (_('Clone'), _('Clone selected drug into a new entry for editing.'), clone_from_existing)
		#, right_extra_button = (_('Reassign'), _('Reassign all patients taking the selected drug to another drug.'), reassign_patients)
	)

#------------------------------------------------------------
from Gnumed.wxGladeWidgets import wxgSingleComponentGenericDrugEAPnl

class cSingleComponentGenericDrugEAPnl(wxgSingleComponentGenericDrugEAPnl.wxgSingleComponentGenericDrugEAPnl, gmEditArea.cGenericEditAreaMixin):

	def __init__(self, *args, **kwargs):

		try:
			data = kwargs['drug']
			del kwargs['drug']
		except KeyError:
			data = None

		wxgSingleComponentGenericDrugEAPnl.wxgSingleComponentGenericDrugEAPnl.__init__(self, *args, **kwargs)
		gmEditArea.cGenericEditAreaMixin.__init__(self)

		self.mode = 'new'
		self.data = data
		if data is not None:
			self.mode = 'edit'

		self.__init_ui()

	#----------------------------------------------------------------
	def __init_ui(self):
		self._PRW_substance.add_callback_on_modified(callback = self._on_name_field_modified)
		self._PRW_substance.add_callback_on_selection(callback = self._on_name_field_modified)
		self._TCTRL_amount.add_callback_on_modified(callback = self._on_name_field_modified)
		self._PRW_unit.add_callback_on_modified(callback = self._on_name_field_modified)
		self._PRW_unit.add_callback_on_selection(callback = self._on_name_field_modified)
		self._PRW_dose_unit.add_callback_on_modified(callback = self._on_name_field_modified)
		self._PRW_dose_unit.add_callback_on_selection(callback = self._on_name_field_modified)

	#----------------------------------------------------------------
	# generic Edit Area mixin API
	#----------------------------------------------------------------
	def _valid_for_save(self):

		validity = True

		if self._PRW_preparation.Value.strip() == '':
			validity = False
			self._PRW_preparation.display_as_valid(False)
			self.StatusText = _('Drug form is missing.')
			self._PRW_preparation.SetFocus()
		else:
			self._PRW_preparation.display_as_valid(True)

		if self._PRW_unit.GetData() is None:
			validity = False
			self._PRW_unit.display_as_valid(False)
			self.StatusText = _('Unit for amount is missing.')
			self._PRW_unit.SetFocus()
		else:
			self._PRW_unit.display_as_valid(True)

		if self._TCTRL_amount.GetValue().strip() == '':
			validity = False
			self.display_tctrl_as_valid(tctrl = self._TCTRL_amount, valid = False)
			self.StatusText = _('Amount is missing.')
			self._TCTRL_amount.SetFocus()
		else:
			converted, amount = gmTools.input2decimal(self._TCTRL_amount.Value.strip())
			if converted:
				self.display_tctrl_as_valid(tctrl = self._TCTRL_amount, valid = True)
			else:
				validity = False
				self.display_tctrl_as_valid(tctrl = self._TCTRL_amount, valid = False)
				self.StatusText = _('Amount must be a number.')
				self._TCTRL_amount.SetFocus()

		if self._PRW_substance.GetData() is None:
			val = self._PRW_substance.Value.strip()
			if val != '' and gmATC.exists_as_atc(val):
				subst = gmMedication.create_substance(substance = val)
				self._PRW_substance.SetText(subst['substance'], subst['pk_substance'])
				self._PRW_substance.display_as_valid(True)
			else:
				validity = False
				self._PRW_substance.display_as_valid(False)
				self.StatusText = _('Substance is missing.')
				self._PRW_substance.SetFocus()
		else:
			self._PRW_substance.display_as_valid(True)

		return validity

	#----------------------------------------------------------------
	def _save_as_new(self):
		dose = gmMedication.create_substance_dose (
			pk_substance = self._PRW_substance.GetData(),
			amount = self._TCTRL_amount.Value.strip(),
			unit = self._PRW_unit.GetData(),
			dose_unit = self._PRW_dose_unit.GetData()
		)
		dose_unit = self._PRW_dose_unit.GetValue().strip()
		if dose_unit != '':
			dose_unit = '/' + dose_unit
		name = '%s %s%s%s' % (
			self._PRW_substance.GetValue().strip(),
			self._TCTRL_amount.Value.strip(),
			self._PRW_unit.GetValue().strip(),
			dose_unit
		)
		drug = gmMedication.create_drug_product (
			product_name = name,
			preparation = self._PRW_preparation.GetValue().strip(),
			return_existing = True,
			doses = [dose]
		)
		drug['is_fake_product'] = True
		drug.save()
		self.data = drug
		return True

	#----------------------------------------------------------------
	def _save_as_update(self):
		return False
#		self.data[''] = self._CHBOX_xxx.GetValue()
#		self.data.save()
#		return True

	#----------------------------------------------------------------
	def _refresh_as_new(self):
		self._LBL_drug_name.SetLabel('')
		self._PRW_substance.SetText('', None)
		self._TCTRL_amount.SetValue('')
		self._PRW_unit.SetText('', None)
		self._PRW_dose_unit.SetText('', None)
		self._PRW_preparation.SetText('', None)

	#----------------------------------------------------------------
	def _refresh_as_new_from_existing(self):
		self._refresh_as_new()

	#----------------------------------------------------------------
	def _refresh_from_existing(self):
		pass

	#----------------------------------------------------------------
	def set_fields(self, fields):
		try:
			self._PRW_substance.SetText(fields['substance']['value'], fields['substance']['data'])
		except KeyError:
			_log.error('cannot set field [substance] from <%s>', fields)

	#----------------------------------------------------------------
	def _on_name_field_modified(self, data=None):
		dose_unit = self._PRW_dose_unit.GetValue().strip()
		if dose_unit != '':
			dose_unit = '/' + dose_unit
		name = '%s %s%s%s' % (
			self._PRW_substance.GetValue().strip(),
			self._TCTRL_amount.Value.strip(),
			self._PRW_unit.GetValue().strip(),
			dose_unit
		)
		self._LBL_drug_name.SetLabel('"%s"' % name.strip())

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
	app.SetWidget(cSubstancePhraseWheel, -1)
	app.MainLoop()
	edit_single_component_generic_drug (
		single_entry = True,
		fields = {'substance': {'value': 'Ibuprofen', 'data': None}},
		return_drug = True
	)
