# -*- coding: utf-8 -*-

#from __future__ import print_function

__doc__ = """GNUmed drug / substance reference widgets."""

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
	from Gnumed.pycommon import gmI18N
	gmI18N.activate_locale()
	gmI18N.install_domain(domain = 'gnumed')

from Gnumed.pycommon import gmDispatcher
from Gnumed.pycommon import gmCfg
from Gnumed.pycommon import gmShellAPI
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmMatchProvider

from Gnumed.business import gmPerson
from Gnumed.business import gmATC
from Gnumed.business import gmPraxis
from Gnumed.business import gmMedication

from Gnumed.wxpython import gmGuiHelpers
from Gnumed.wxpython import gmAuthWidgets
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
		choices = gmMedication.drug_data_source_interfaces.keys(),
		columns = [_('Drug data source')],
		data = gmMedication.drug_data_source_interfaces.keys(),
		caption = _('Configuring default drug data source')
	)

#============================================================
def get_drug_database(parent=None, patient=None):
	dbcfg = gmCfg.cCfgSQL()

	# load from option
	default_db = dbcfg.get2 (
		option = 'external.drug_data.default_source',
		workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
		bias = 'workplace'
	)

	# not configured -> try to configure
	if default_db is None:
		gmDispatcher.send('statustext', msg = _('No default drug database configured.'), beep = True)
		configure_drug_data_source(parent = parent)
		default_db = dbcfg.get2 (
			option = 'external.drug_data.default_source',
			workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
			bias = 'workplace'
		)
		# still not configured -> return
		if default_db is None:
			gmGuiHelpers.gm_show_error (
				aMessage = _('There is no default drug database configured.'),
				aTitle = _('Jumping to drug database')
			)
			return None

	# now it MUST be configured (either newly or previously)
	# but also *validly* ?
	try:
		drug_db = gmMedication.drug_data_source_interfaces[default_db]()
	except KeyError:
		# not valid
		_log.error('faulty default drug data source configuration: %s', default_db)
		# try to configure
		configure_drug_data_source(parent = parent)
		default_db = dbcfg.get2 (
			option = 'external.drug_data.default_source',
			workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
			bias = 'workplace'
		)
		# deconfigured or aborted (and thusly still misconfigured) ?
		try:
			drug_db = gmMedication.drug_data_source_interfaces[default_db]()
		except KeyError:
			_log.error('still faulty default drug data source configuration: %s', default_db)
			return None

	if patient is not None:
		drug_db.patient = pat

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

	dbcfg = gmCfg.cCfgSQL()

	ifap_cmd = dbcfg.get2 (
		option = 'external.ifap-win.shell_command',
		workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
		bias = 'workplace',
		default = 'wine "C:\Ifapwin\WIAMDB.EXE"'
	)
	found, binary = gmShellAPI.detect_external_binary(ifap_cmd)
	if not found:
		gmDispatcher.send('statustext', msg = _('Cannot call IFAP via [%s].') % ifap_cmd)
		return False
	ifap_cmd = binary

	if import_drugs:
		transfer_file = os.path.expanduser(dbcfg.get2 (
			option = 'external.ifap-win.transfer_file',
			workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
			bias = 'workplace',
			default = '~/.wine/drive_c/Ifapwin/ifap2gnumed.csv'
		))
		# file must exist for Ifap to write into it
		try:
			f = io.open(transfer_file, mode = 'wt').close()
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
			csv_file = io.open(transfer_file, mode = 'rt', encoding = 'latin1')						# FIXME: encoding unknown
		except:
			_log.exception('cannot access [%s]', fname)
			csv_file = None

		if csv_file is not None:
			import csv
			csv_lines = csv.DictReader (
				csv_file,
				fieldnames = u'PZN Handelsname Form Abpackungsmenge Einheit Preis1 Hersteller Preis2 rezeptpflichtig Festbetrag Packungszahl Packungsgr\xf6\xdfe'.split(),
				delimiter = ';'
			)
			# dummy episode for now
			epi = emr.add_episode(episode_name = _('Current medication'))
			for line in csv_lines:
				narr = u'%sx %s %s %s (\u2258 %s %s) von %s (%s)' % (
					line['Packungszahl'].strip(),
					line['Handelsname'].strip(),
					line['Form'].strip(),
					line[u'Packungsgr\xf6\xdfe'].strip(),
					line['Abpackungsmenge'].strip(),
					line['Einheit'].strip(),
					line['Hersteller'].strip(),
					line['PZN'].strip()
				)
				emr.add_clin_narrative(note = narr, soap_cat = 's', episode = epi)
			csv_file.close()

	return True

#============================================================
# ATC related widgets
#------------------------------------------------------------
def browse_atc_reference_deprecated(parent=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()
	#------------------------------------------------------------
	def refresh(lctrl):
		atcs = gmATC.get_reference_atcs()

		items = [ [
			a['atc'],
			a['term'],
			gmTools.coalesce(a['unit'], u''),
			gmTools.coalesce(a['administrative_route'], u''),
			gmTools.coalesce(a['comment'], u''),
			a['version'],
			a['lang']
		] for a in atcs ]
		lctrl.set_string_items(items)
		lctrl.set_data(atcs)
	#------------------------------------------------------------
	gmListWidgets.get_choices_from_list (
		parent = parent,
		msg = _('\nThe ATC codes as known to GNUmed.\n'),
		caption = _('Showing ATC codes.'),
		columns = [ u'ATC', _('Term'), _('Unit'), _(u'Route'), _('Comment'), _('Version'), _('Language') ],
		single_selection = True,
		refresh_callback = refresh
	)

#============================================================
def update_atc_reference_data():

	dlg = wx.FileDialog (
		parent = None,
		message = _('Choose an ATC import config file'),
		defaultDir = os.path.expanduser(os.path.join('~', 'gnumed')),
		defaultFile = '',
		wildcard = "%s (*.conf)|*.conf|%s (*)|*" % (_('config files'), _('all files')),
		style = wx.OPEN | wx.FILE_MUST_EXIST
	)

	result = dlg.ShowModal()
	if result == wx.ID_CANCEL:
		return

	cfg_file = dlg.GetPath()
	dlg.Destroy()

	conn = gmAuthWidgets.get_dbowner_connection(procedure = _('importing ATC reference data'))
	if conn is None:
		return False

	wx.BeginBusyCursor()

	if gmATC.atc_import(cfg_fname = cfg_file, conn = conn):
		gmDispatcher.send(signal = 'statustext', msg = _('Successfully imported ATC reference data.'))
	else:
		gmDispatcher.send(signal = 'statustext', msg = _('Importing ATC reference data failed.'), beep = True)

	wx.EndBusyCursor()
	return True

#============================================================
class cATCPhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):

		gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)
		query = u"""

			SELECT DISTINCT ON (label)
				atc_code,
				label
			FROM (

				SELECT
					code as atc_code,
					(code || ': ' || term)
						AS label
				FROM ref.atc
				WHERE
					term %(fragment_condition)s
						OR
					code %(fragment_condition)s

				UNION ALL

				SELECT
					atc_code,
					(atc_code || ': ' || description)
						AS label
				FROM ref.consumable_substance
				WHERE
					description %(fragment_condition)s
						OR
					atc_code %(fragment_condition)s

				UNION ALL

				SELECT
					atc_code,
					(atc_code || ': ' || description || ' (' || preparation || ')')
						AS label
				FROM ref.branded_drug
				WHERE
					description %(fragment_condition)s
						OR
					atc_code %(fragment_condition)s

				-- it would be nice to be able to include clin.vacc_indication but that's hard to do in SQL

			) AS candidates
			WHERE atc_code IS NOT NULL
			ORDER BY label
			LIMIT 50"""

		mp = gmMatchProvider.cMatchProvider_SQL2(queries = query)
		mp.setThresholds(1, 2, 4)
#		mp.word_separators = '[ \t=+&:@]+'
		self.SetToolTipString(_('Select an ATC (Anatomical-Therapeutic-Chemical) code.'))
		self.matcher = mp
		self.selection_only = True

#============================================================
# consumable substances widgets
#------------------------------------------------------------
def edit_consumable_substance(parent=None, substance=None, single_entry=False):

	if substance is not None:
		if substance.is_in_use_by_patients:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot edit this substance. It is in use.'), beep = True)
			return False

	ea = cConsumableSubstanceEAPnl(parent = parent, id = -1)
	ea.data = substance
	ea.mode = gmTools.coalesce(substance, 'new', 'edit')
	dlg = gmEditArea.cGenericEditAreaDlg2(parent = parent, id = -1, edit_area = ea, single_entry = single_entry)
	dlg.SetTitle(gmTools.coalesce(substance, _('Adding new consumable substance'), _('Editing consumable substance')))
	if dlg.ShowModal() == wx.ID_OK:
		dlg.Destroy()
		return True
	dlg.Destroy()
	return False

#------------------------------------------------------------
def manage_consumable_substances(parent=None):

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
		return edit_consumable_substance(parent = parent, substance = substance, single_entry = (substance is not None))
	#------------------------------------------------------------
	def delete(substance):
		if substance.is_in_use_by_patients:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot delete this substance. It is in use.'), beep = True)
			return False

		xxxxxxx
		return gmMedication.delete_consumable_substance(substance = substance['pk'])
	#------------------------------------------------------------
	def refresh(lctrl):
		xxxxxxx
		substs = gmMedication.get_consumable_substances(order_by = 'description')
		items = [ [
			s['description'],
			s['amount'],
			s['unit'],
			gmTools.coalesce(s['atc_code'], u''),
			s['pk']
		] for s in substs ]
		lctrl.set_string_items(items)
		lctrl.set_data(substs)
	#------------------------------------------------------------
	msg = _('\nThese are the consumable substances registered with GNUmed.\n')

	gmListWidgets.get_choices_from_list (
		parent = parent,
		msg = msg,
		caption = _('Showing consumable substances.'),
		columns = [_('Substance'), _('Amount'), _('Unit'), 'ATC', u'#'],
		single_selection = True,
		new_callback = edit,
		edit_callback = edit,
		delete_callback = delete,
		refresh_callback = refresh,
		left_extra_button = (_('Import'), _('Import consumable substances from a drug database.'), add_from_db)
	)

#------------------------------------------------------------
from Gnumed.wxGladeWidgets import wxgConsumableSubstanceEAPnl

class cConsumableSubstanceEAPnl(wxgConsumableSubstanceEAPnl.wxgConsumableSubstanceEAPnl, gmEditArea.cGenericEditAreaMixin):

	def __init__(self, *args, **kwargs):

		try:
			data = kwargs['substance']
			del kwargs['substance']
		except KeyError:
			data = None

		wxgConsumableSubstanceEAPnl.wxgConsumableSubstanceEAPnl.__init__(self, *args, **kwargs)
		gmEditArea.cGenericEditAreaMixin.__init__(self)

		# Code using this mixin should set mode and data
		# after instantiating the class:
		self.mode = 'new'
		self.data = data
		if data is not None:
			self.mode = 'edit'

#		self.__init_ui()
	#----------------------------------------------------------------
#	def __init_ui(self):
#		self._PRW_atc.selection_only = False
	#----------------------------------------------------------------
	# generic Edit Area mixin API
	#----------------------------------------------------------------
	def _valid_for_save(self):

		validity = True

		if self._TCTRL_substance.GetValue().strip() == u'':
			validity = False
			self.display_tctrl_as_valid(tctrl = self._TCTRL_substance, valid = False)
			self._TCTRL_substance.SetFocus()
		else:
			self.display_tctrl_as_valid(tctrl = self._TCTRL_substance, valid = True)

		try:
			decimal.Decimal(self._TCTRL_amount.GetValue().strip().replace(',', '.'))
			self.display_tctrl_as_valid(tctrl = self._TCTRL_amount, valid = True)
		except (TypeError, decimal.InvalidOperation):
			validity = False
			self.display_tctrl_as_valid(tctrl = self._TCTRL_amount, valid = False)
			self._TCTRL_amount.SetFocus()

		if self._PRW_unit.GetValue().strip() == u'':
			validity = False
			self._PRW_unit.display_as_valid(valid = False)
			self._TCTRL_substance.SetFocus()
		else:
			self._PRW_unit.display_as_valid(valid = True)

		if validity is False:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot save consumable substance. Missing essential input.'))

		return validity

	#----------------------------------------------------------------
	def _save_as_new(self):
		xxxxxxxxx
		subst = gmMedication.create_consumable_substance (
			substance = self._TCTRL_substance.GetValue().strip(),
			atc = self._PRW_atc.GetData(),
			amount = decimal.Decimal(self._TCTRL_amount.GetValue().strip().replace(',', '.')),
			unit = gmTools.coalesce(self._PRW_unit.GetData(), self._PRW_unit.GetValue().strip(), function_initial = ('strip', None))
		)
		success, data = subst.save()
		if not success:
			err, msg = data
			_log.error(err)
			_log.error(msg)
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot save consumable substance. %s') % msg, beep = True)
			return False

		self.data = subst
		return True

	#----------------------------------------------------------------
	def _save_as_update(self):
		self.data['description'] = self._TCTRL_substance.GetValue().strip()
		self.data['atc_code'] = self._PRW_atc.GetData()
		self.data['amount'] = decimal.Decimal(self._TCTRL_amount.GetValue().strip().replace(',', '.'))
		self.data['unit'] = gmTools.coalesce(self._PRW_unit.GetData(), self._PRW_unit.GetValue().strip(), function_initial = ('strip', None))
		success, data = self.data.save()

		if not success:
			err, msg = data
			_log.error(err)
			_log.error(msg)
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot save consumable substance. %s') % msg, beep = True)
			return False

		return True

	#----------------------------------------------------------------
	def _refresh_as_new(self):
		self._TCTRL_substance.SetValue(u'')
		self._TCTRL_amount.SetValue(u'')
		self._PRW_unit.SetText(u'', None)
		self._PRW_atc.SetText(u'', None)

		self._TCTRL_substance.SetFocus()

	#----------------------------------------------------------------
	def _refresh_from_existing(self):
		self._TCTRL_substance.SetValue(self.data['description'])
		self._TCTRL_amount.SetValue(u'%s' % self.data['amount'])
		self._PRW_unit.SetText(self.data['unit'], self.data['unit'])
		self._PRW_atc.SetText(gmTools.coalesce(self.data['atc_code'], u''), self.data['atc_code'])

		self._TCTRL_substance.SetFocus()

	#----------------------------------------------------------------
	def _refresh_as_new_from_existing(self):
		self._refresh_as_new()

#------------------------------------------------------------
class cSubstancePhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):

		mp = gmMedication.cSubstanceMatchProvider()
		mp.setThresholds(1, 2, 4)
		gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)
		self.SetToolTipString(_('The substance with optional strength.'))
		self.matcher = mp
		self.selection_only = False
		self.phrase_separators = None

	#--------------------------------------------------------
	def _data2instance(self):
		return gmMedication.cConsumableSubstance(aPK_obj = self.GetData(as_instance = False, can_create = False))

#============================================================
# drug component widgets
#------------------------------------------------------------
def manage_drug_components(parent=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	#------------------------------------------------------------
	def edit(component=None):
		substance = gmMedication.cConsumableSubstance(aPK_obj = component['pk_consumable_substance'])
		return edit_consumable_substance(parent = parent, substance = substance, single_entry = True)
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
			u'%s%s' % (c['brand'], gmTools.coalesce(c['atc_brand'], u'', u' [%s]')),
			u'%s%s' % (c['substance'], gmTools.coalesce(c['atc_substance'], u'', u' [%s]')),
			u'%s %s' % (c['amount'], c['unit']),
			c['preparation'],
			gmTools.coalesce(c['external_code_brand'], u'', u'%%s [%s]' % c['external_code_type_brand']),
			c['pk_component']
		] for c in comps ]
		lctrl.set_string_items(items)
		lctrl.set_data(comps)
	#------------------------------------------------------------
	msg = _('\nThese are the components in the drug brands known to GNUmed.\n')

	gmListWidgets.get_choices_from_list (
		parent = parent,
		msg = msg,
		caption = _('Showing drug brand components.'),
		columns = [_('Brand'), _('Substance'), _('Strength'), _('Preparation'), _('Code'), u'#'],
		single_selection = True,
		#new_callback = edit,
		edit_callback = edit,
		delete_callback = delete,
		refresh_callback = refresh
	)

#------------------------------------------------------------
def edit_drug_component(parent=None, drug_component=None, single_entry=False):
	ea = cDrugComponentEAPnl(parent = parent, id = -1)
	ea.data = drug_component
	ea.mode = gmTools.coalesce(drug_component, 'new', 'edit')
	dlg = gmEditArea.cGenericEditAreaDlg2(parent = parent, id = -1, edit_area = ea, single_entry = single_entry)
	dlg.SetTitle(gmTools.coalesce(drug_component, _('Adding new drug component'), _('Editing drug component')))
	if dlg.ShowModal() == wx.ID_OK:
		dlg.Destroy()
		return True
	dlg.Destroy()
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
				gmDispatcher.send(signal = 'statustext', msg = _('Cannot edit drug component. It is in use.'), beep = True)
				return False

		validity = True

		if self._PRW_substance.GetData() is None:
			validity = False
			self._PRW_substance.display_as_valid(False)
		else:
			self._PRW_substance.display_as_valid(True)

		val = self._TCTRL_amount.GetValue().strip().replace(',', u'.', 1)
		try:
			decimal.Decimal(val)
			self.display_tctrl_as_valid(tctrl = self._TCTRL_amount, valid = True)
		except:
			validity = False
			self.display_tctrl_as_valid(tctrl = self._TCTRL_amount, valid = False)

		if self._PRW_unit.GetValue().strip() == u'':
			validity = False
			self._PRW_unit.display_as_valid(False)
		else:
			self._PRW_unit.display_as_valid(True)

		if validity is False:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot save drug component. Invalid or missing essential input.'))

		return validity
	#----------------------------------------------------------------
	def _save_as_new(self):
		# save the data as a new instance
		data = 1
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
		self.data['pk_consumable_substance'] = self._PRW_substance.GetData()
		self.data['amount'] = decimal.Decimal(self._TCTRL_amount.GetValue().strip().replace(',', u'.', 1))
		self.data['unit'] = self._PRW_unit.GetValue().strip()
		return self.data.save()
	#----------------------------------------------------------------
	def _refresh_as_new(self):
		self._TCTRL_brand.SetValue(u'')
		self._TCTRL_components.SetValue(u'')
		self._TCTRL_codes.SetValue(u'')
		self._PRW_substance.SetText(u'', None)
		self._TCTRL_amount.SetValue(u'')
		self._PRW_unit.SetText(u'', None)

		self._PRW_substance.SetFocus()
	#----------------------------------------------------------------
	def _refresh_from_existing(self):
		self._TCTRL_brand.SetValue(u'%s (%s)' % (self.data['brand'], self.data['preparation']))
		self._TCTRL_components.SetValue(u' / '.join(self.data.containing_drug['components']))
		details = []
		if self.data['atc_brand'] is not None:
			details.append(u'ATC: %s' % self.data['atc_brand'])
		if self.data['external_code_brand'] is not None:
			details.append(u'%s: %s' % (self.data['external_code_type_brand'], self.data['external_code_brand']))
		self._TCTRL_codes.SetValue(u'; '.join(details))

		self._PRW_substance.SetText(self.data['substance'], self.data['pk_consumable_substance'])
		self._TCTRL_amount.SetValue(u'%s' % self.data['amount'])
		self._PRW_unit.SetText(self.data['unit'], self.data['unit'])

		self._PRW_substance.SetFocus()
	#----------------------------------------------------------------
	def _refresh_as_new_from_existing(self):
		#self._PRW_brand.SetText(u'', None)
		#self._TCTRL_prep.SetValue(u'')
		#self._TCTRL_brand_details.SetValue(u'')
		self._PRW_substance.SetText(u'', None)
		self._TCTRL_amount.SetValue(u'')
		self._PRW_unit.SetText(u'', None)

		self._PRW_substance.SetFocus()

#------------------------------------------------------------
class cDrugComponentPhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):

		mp = gmMedication.cDrugComponentMatchProvider()
		mp.setThresholds(2, 3, 4)
		gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)
		self.SetToolTipString(_('A drug component with optional strength.'))
		self.matcher = mp
		self.selection_only = False
	#--------------------------------------------------------
	def _data2instance(self):
		return gmMedication.cDrugComponent(aPK_obj = self.GetData(as_instance = False, can_create = False))

#============================================================
# branded drugs widgets
#------------------------------------------------------------
def edit_branded_drug(parent=None, branded_drug=None, single_entry=False):

	if branded_drug is not None:
		if branded_drug.is_in_use_by_patients:
			gmGuiHelpers.gm_show_info (
				aTitle = _('Editing drug'),
				aMessage = _(
					'Cannot edit the branded drug product\n'
					'\n'
					' "%s" (%s)\n'
					'\n'
					'because it is currently taken by patients.\n'
				) % (branded_drug['brand'], branded_drug['preparation'])
			)
			return False

	if parent is None:
		parent = wx.GetApp().GetTopWindow()
	#--------------------------------------------
	def manage_substances(drug):
		manage_consumable_substances(parent = parent)
	#--------------------------------------------
	ea = cBrandedDrugEAPnl(parent = parent, id = -1)
	ea.data = branded_drug
	ea.mode = gmTools.coalesce(branded_drug, 'new', 'edit')
	dlg = gmEditArea.cGenericEditAreaDlg2(parent = parent, id = -1, edit_area = ea, single_entry = single_entry)
	dlg.SetTitle(gmTools.coalesce(branded_drug, _('Adding new drug brand'), _('Editing drug brand')))
	dlg.left_extra_button = (
		_('Substances'),
		_('Manage consumable substances'),
		manage_substances
	)
	if dlg.ShowModal() == wx.ID_OK:
		dlg.Destroy()
		return True
	dlg.Destroy()
	return False

#------------------------------------------------------------
def manage_branded_drugs(parent=None, ignore_OK_button=False):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()
	#------------------------------------------------------------
	def add_from_db(brand):
		drug_db = get_drug_database(parent = parent)
		if drug_db is None:
			return False
		drug_db.import_drugs()
		return True
	#------------------------------------------------------------
	def get_tooltip(brand=None):
		tt = u'%s %s\n' % (brand['brand'], brand['preparation'])
		tt += u'\n'
		tt += u'%s%s%s\n' % (
			gmTools.bool2subst(brand.is_vaccine, u'%s, ' % _('Vaccine'), u''),
			u'%s, ' % gmTools.bool2subst(brand.is_in_use_by_patients, _('in use'), _('not in use')),
			gmTools.bool2subst(brand['is_fake_brand'], _('fake'), u'')
		)
		tt += gmTools.coalesce(brand['atc'], u'', _('ATC: %s\n'))
		tt += gmTools.coalesce(brand['external_code'], u'', u'%s: %%s\n' % brand['external_code_type'])
		if brand['components'] is not None:
			tt += u'- %s' % u'\n- '.join(brand['components'])
		return tt
	#------------------------------------------------------------
	def edit(brand):
		if brand is not None:
			if brand.is_vaccine:
				gmGuiHelpers.gm_show_info (
					aTitle = _('Editing medication'),
					aMessage = _(
						'Cannot edit the medication\n'
						'\n'
						' "%s" (%s)\n'
						'\n'
						'because it is a vaccine. Please edit it\n'
						'from the vaccine management section !\n'
					) % (brand['brand'], brand['preparation'])
				)
				return False

		return edit_branded_drug(parent = parent, branded_drug = brand, single_entry = True)
	#------------------------------------------------------------
	def delete(brand):
		if brand.is_vaccine:
			gmGuiHelpers.gm_show_info (
				aTitle = _('Deleting medication'),
				aMessage = _(
					'Cannot delete the medication\n'
					'\n'
					' "%s" (%s)\n'
					'\n'
					'because it is a vaccine. Please delete it\n'
					'from the vaccine management section !\n'
				) % (brand['brand'], brand['preparation'])
			)
			return False
		gmMedication.delete_branded_drug(pk_brand = brand['pk_brand'])
		return True
	#------------------------------------------------------------
	def new():
		return edit_branded_drug(parent = parent, branded_drug = None, single_entry = False)
	#------------------------------------------------------------
	def refresh(lctrl):
		drugs = gmMedication.get_branded_drugs()
		items = [ [
			u'%s%s' % (
				d['brand'],
				gmTools.bool2subst(d['is_fake_brand'], ' (%s)' % _('fake'), u'')
			),
			d['preparation'],
			gmTools.coalesce(d['atc'], u''),
			gmTools.coalesce(d['components'], u''),
			gmTools.coalesce(d['external_code'], u'', u'%%s [%s]' % d['external_code_type']),
			d['pk_brand']
		] for d in drugs ]
		lctrl.set_string_items(items)
		lctrl.set_data(drugs)
	#------------------------------------------------------------
	msg = _('\nThese are the drug brands known to GNUmed.\n')

	gmListWidgets.get_choices_from_list (
		parent = parent,
		msg = msg,
		caption = _('Showing branded drugs.'),
		columns = [_('Name'), _('Preparation'), _('ATC'), _('Components'), _('Code'), u'#'],
		single_selection = True,
		ignore_OK_button = ignore_OK_button,
		refresh_callback = refresh,
		new_callback = new,
		edit_callback = edit,
		delete_callback = delete,
		list_tooltip_callback = get_tooltip,
		left_extra_button = (_('Import'), _('Import substances and brands from a drug database.'), add_from_db)
		#, middle_extra_button = (_('Clone'), _('Clone selected drug into a new entry for editing.'), clone_from_existing)
		#, right_extra_button = (_('Reassign'), _('Reassign all patients taking the selected drug to another drug.'), reassign_patients)
	)

#------------------------------------------------------------
def manage_components_of_branded_drug(parent=None, brand=None):

	if brand is not None:
		if brand.is_in_use_by_patients:
			gmGuiHelpers.gm_show_info (
				aTitle = _('Managing components of a drug'),
				aMessage = _(
					'Cannot manage the components of the branded drug product\n'
					'\n'
					' "%s" (%s)\n'
					'\n'
					'because it is currently taken by patients.\n'
				) % (brand['brand'], brand['preparation'])
			)
			return False
	#--------------------------------------------------------
	if parent is None:
		parent = wx.GetApp().GetTopWindow()
	#--------------------------------------------------------
#	def manage_substances():
#		pass
	#--------------------------------------------------------
	if brand is None:
		msg = _('Pick the substances which are components of this drug.')
		right_col = _('Components of drug')
		comp_substs = []
	else:
		right_col = u'%s (%s)' % (brand['brand'], brand['preparation'])
		msg = _(
			'Adjust the components of "%s"\n'
			'\n'
			'The drug must contain at least one component. Any given\n'
			'substance can only be included once per drug.'
		) % right_col
		comp_substs = [ c.substance for c in brand.components ]

	xxxxxxx
	substs = gmMedication.get_consumable_substances(order_by = 'description')
	choices = [ u'%s %s %s' % (s['description'], s['amount'], s['unit']) for s in substs ]
	picks = [ u'%s %s %s' % (c['description'], c['amount'], c['unit']) for c in comp_substs ]

	picker = gmListWidgets.cItemPickerDlg (
		parent,
		-1,
		title = _('Managing components of a drug ...'),
		msg = msg
	)
	picker.set_columns(['Substances'], [right_col])
	picker.set_choices(choices = choices, data = substs)
	picker.set_picks(picks = picks, data = comp_substs)
#	picker.extra_button = (
#		_('Substances'),
#		_('Manage list of consumable substances'),
#		manage_substances
#	)

	btn_pressed = picker.ShowModal()
	substs = picker.get_picks()
	picker.Destroy()

	if btn_pressed != wx.ID_OK:
		return (False, None)

	if brand is not None:
		brand.set_substance_doses_as_components(substance_doses = xxxx_substs)		xxxxxxxxx

	return (True, substs)

#------------------------------------------------------------
from Gnumed.wxGladeWidgets import wxgBrandedDrugEAPnl

class cBrandedDrugEAPnl(wxgBrandedDrugEAPnl.wxgBrandedDrugEAPnl, gmEditArea.cGenericEditAreaMixin):

	def __init__(self, *args, **kwargs):

		try:
			data = kwargs['drug']
			del kwargs['drug']
		except KeyError:
			data = None

		wxgBrandedDrugEAPnl.wxgBrandedDrugEAPnl.__init__(self, *args, **kwargs)
		gmEditArea.cGenericEditAreaMixin.__init__(self)

		self.mode = 'new'
		self.data = data
		if data is not None:
			self.mode = 'edit'
			xxxxxxxxxx
			self.__component_substances = data.components_as_substances

		#self.__init_ui()
	#----------------------------------------------------------------
#	def __init_ui(self):
		# adjust external type PRW
	#----------------------------------------------------------------
	# generic Edit Area mixin API
	#----------------------------------------------------------------
	def _valid_for_save(self):

		if self.data is not None:
			if self.data.is_in_use_by_patients:
				gmDispatcher.send(signal = 'statustext', msg = _('Cannot edit drug brand. It is in use.'), beep = True)
				return False

		validity = True

		brand_name = self._PRW_brand.GetValue().strip()
		if brand_name == u'':
			validity = False
			self._PRW_brand.display_as_valid(False)
		else:
			self._PRW_brand.display_as_valid(True)

		preparation = self._PRW_preparation.GetValue().strip()
		if preparation == u'':
			validity = False
			self._PRW_preparation.display_as_valid(False)
		else:
			self._PRW_preparation.display_as_valid(True)

		if validity is True:
			# dupe ?
			drug = gmMedication.get_drug_by_brand(brand_name = brand_name, preparation = preparation)
			if drug is not None:
				validity = False
				self._PRW_brand.display_as_valid(False)
				self._PRW_preparation.display_as_valid(False)
				gmGuiHelpers.gm_show_error (
					title = _('Checking brand data'),
					error = _(
						'The brand information you entered:\n'
						'\n'
						' [%s %s]\n'
						'\n'
						'already exists as a drug product.'
					) % (brand_name, preparation)
				)

			else:
				# lacking components ?
				self._TCTRL_components.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_BACKGROUND))
				if len(self.__component_substances) == 0:
					wants_empty = gmGuiHelpers.gm_show_question (
						title = _('Checking brand data'),
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
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot save branded drug. Invalid or missing essential input.'))

		return validity
	#----------------------------------------------------------------
	def _save_as_new(self):

		drug = gmMedication.create_branded_drug (
			brand_name = self._PRW_brand.GetValue().strip(),
			preparation = gmTools.coalesce (
				self._PRW_preparation.GetData(),
				self._PRW_preparation.GetValue()
			).strip(),
			return_existing = True
		)
		drug['is_fake_brand'] = self._CHBOX_is_fake.GetValue()
		drug['atc'] = self._PRW_atc.GetData()
		code = self._TCTRL_external_code.GetValue().strip()
		if code != u'':
			drug['external_code'] = code
			drug['external_code_type'] = self._PRW_external_code_type.GetData().strip()

		drug.save()

		if len(self.__component_substances) > 0:
			drug.set_substance_doses_as_components(substance_doses = xxx_self.__component_substances)			xxxxxxx

		self.data = drug

		return True
	#----------------------------------------------------------------
	def _save_as_update(self):
		self.data['brand'] = self._PRW_brand.GetValue().strip()
		self.data['preparation'] = gmTools.coalesce (
			self._PRW_preparation.GetData(),
			self._PRW_preparation.GetValue()
		).strip()
		self.data['is_fake_brand'] = self._CHBOX_is_fake.GetValue()
		self.data['atc'] = self._PRW_atc.GetData()
		code = self._TCTRL_external_code.GetValue().strip()
		if code != u'':
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
		self._PRW_brand.SetText(u'', None)
		self._PRW_preparation.SetText(u'', None)
		self._CHBOX_is_fake.SetValue(False)
		self._TCTRL_components.SetValue(u'')
		self._PRW_atc.SetText(u'', None)
		self._TCTRL_external_code.SetValue(u'')
		self._PRW_external_code_type.SetText(u'', None)

		self._PRW_brand.SetFocus()

		self.__component_substances = []

	#----------------------------------------------------------------
	def _refresh_as_new_from_existing(self):
		self._refresh_as_new()

	#----------------------------------------------------------------
	def _refresh_from_existing(self):
		self._PRW_brand.SetText(self.data['brand'], self.data['pk_brand'])
		self._PRW_preparation.SetText(self.data['preparation'], self.data['preparation'])
		self._CHBOX_is_fake.SetValue(self.data['is_fake_brand'])
		comps = u''
		if self.data['components'] is not None:
			comps = u'- %s' % u'\n- '.join(self.data['components'])
		self._TCTRL_components.SetValue(comps)
		self._PRW_atc.SetText(gmTools.coalesce(self.data['atc'], u''), self.data['atc'])
		self._TCTRL_external_code.SetValue(gmTools.coalesce(self.data['external_code'], u''))
		t = gmTools.coalesce(self.data['external_code_type'], u'')
		self._PRW_external_code_type.SetText(t, t)

		self._PRW_brand.SetFocus()

		xxxxxxxxxxxxxxxx
		self.__component_substances = self.data.components_as_substances

	#----------------------------------------------------------------
	# event handler
	#----------------------------------------------------------------
	def _on_manage_components_button_pressed(self, event):
		event.Skip()
		if self.mode == 'new_from_existing':
			brand = None
		else:
			brand = self.data
		OKed, substs = manage_components_of_branded_drug(parent = self, brand = brand)
		if OKed is True:
			self.__component_substances = substs
			comps = u''
			if len(substs) > 0:
				comps = u'- %s' % u'\n- '.join([ u'%s %s %s' % (s['description'], s['amount'], s['unit']) for s in substs ])
			self._TCTRL_components.SetValue(comps)

#------------------------------------------------------------
class cBrandedDrugPhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):

		query = u"""
			SELECT
				pk
					AS data,
				(description || ' (' || preparation || ')' || coalesce(' [' || atc_code || ']', ''))
					AS list_label,
				(description || ' (' || preparation || ')' || coalesce(' [' || atc_code || ']', ''))
					AS field_label
			FROM ref.branded_drug
			WHERE description %(fragment_condition)s
			ORDER BY list_label
			LIMIT 50"""

		mp = gmMatchProvider.cMatchProvider_SQL2(queries = query)
		mp.setThresholds(2, 3, 4)
		gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)
		self.SetToolTipString(_(
			'The brand name of the drug.\n'
			'\n'
			'Note: a brand name will need to be linked to\n'
			'one or more components before it can be used,\n'
			'except in the case of fake (generic) vaccines.'
		))
		self.matcher = mp
		self.selection_only = False

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
#	#app.SetWidget(cATCPhraseWheel, -1)
	#app.SetWidget(cSubstancePhraseWheel, -1)
	app.SetWidget(cBrandOrSubstancePhraseWheel, -1)
	app.MainLoop()
	#manage_substance_intakes()
