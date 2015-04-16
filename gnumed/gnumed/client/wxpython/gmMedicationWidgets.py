"""GNUmed medication/substances handling widgets."""

#================================================================
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL v2 or later"

import logging
import sys
import os.path
import decimal
import datetime as pydt


import wx
import wx.grid


if __name__ == '__main__':
	sys.path.insert(0, '../../')
	from Gnumed.pycommon import gmI18N
	gmI18N.activate_locale()
	gmI18N.install_domain(domain = 'gnumed')

from Gnumed.pycommon import gmDispatcher
from Gnumed.pycommon import gmCfg
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmDateTime
from Gnumed.pycommon import gmMatchProvider
from Gnumed.pycommon import gmI18N
from Gnumed.pycommon import gmPrinting
from Gnumed.pycommon import gmCfg2
from Gnumed.pycommon import gmNetworkTools

from Gnumed.business import gmPerson
from Gnumed.business import gmATC
from Gnumed.business import gmPraxis
from Gnumed.business import gmMedication
from Gnumed.business import gmForms
from Gnumed.business import gmStaff
from Gnumed.business import gmDocuments
from Gnumed.business import gmLOINC
from Gnumed.business import gmClinicalRecord
from Gnumed.business import gmClinicalCalculator
from Gnumed.business import gmPathLab

from Gnumed.wxpython import gmGuiHelpers
from Gnumed.wxpython import gmRegetMixin
from Gnumed.wxpython import gmAuthWidgets
from Gnumed.wxpython import gmEditArea
from Gnumed.wxpython import gmMacro
from Gnumed.wxpython import gmCfgWidgets
from Gnumed.wxpython import gmListWidgets
from Gnumed.wxpython import gmPhraseWheel
from Gnumed.wxpython import gmFormWidgets
from Gnumed.wxpython import gmAllergyWidgets
from Gnumed.wxpython import gmDocumentWidgets


_log = logging.getLogger('gm.ui')

#============================================================
# generic drug database access
#============================================================
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
def get_drug_database(parent = None):
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

	pat = gmPerson.gmCurrentPatient()
	if pat.connected:
		drug_db.patient = pat

	return drug_db
#============================================================
def jump_to_drug_database():
	dbcfg = gmCfg.cCfgSQL()
	drug_db = get_drug_database()
	if drug_db is None:
		return
	drug_db.switch_to_frontend(blocking = False)

#============================================================
def jump_to_ifap(import_drugs=False):

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
			f = open(transfer_file, 'w+b').close()
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
			csv_file = open(transfer_file, 'rb')						# FIXME: encoding
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
			pat = gmPerson.gmCurrentPatient()
			emr = pat.get_emr()
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
#============================================================

def browse_atc_reference(parent=None):

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

		return gmMedication.delete_consumable_substance(substance = substance['pk'])
	#------------------------------------------------------------
	def refresh(lctrl):
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

#============================================================
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

		return component.containing_drug.remove_component(substance = component['pk_component'])
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

#============================================================
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

#============================================================
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
#============================================================
class cSubstancePreparationPhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):

		query = u"""
(
	SELECT DISTINCT ON (list_label)
		preparation AS data,
		preparation AS list_label,
		preparation AS field_label
	FROM ref.branded_drug
	WHERE preparation %(fragment_condition)s
) UNION (
	SELECT DISTINCT ON (list_label)
		preparation AS data,
		preparation AS list_label,
		preparation AS field_label
	FROM clin.substance_intake
	WHERE preparation %(fragment_condition)s
)
ORDER BY list_label
LIMIT 30"""

		mp = gmMatchProvider.cMatchProvider_SQL2(queries = query)
		mp.setThresholds(1, 2, 4)
		gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)
		self.SetToolTipString(_('The preparation (form) of the substance or brand.'))
		self.matcher = mp
		self.selection_only = False

#============================================================
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
# branded drugs widgets
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
		brand.set_substances_as_components(substances = substs)

	return (True, substs)

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
		gmMedication.delete_branded_drug(brand = brand['pk_brand'])
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

#============================================================
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
			drug.set_substances_as_components(substances = self.__component_substances)

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

#============================================================
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
# current substance intake widgets
#------------------------------------------------------------
class cBrandOrSubstancePhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):

		mp = gmMedication.cBrandOrSubstanceMatchProvider()
		mp.setThresholds(1, 2, 4)
		gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)
		self.SetToolTipString(_('A substance with optional strength or a brand.'))
		self.matcher = mp
		self.selection_only = False
		self.phrase_separators = None
		self.IS_BRAND = 1
		self.IS_SUBSTANCE = 2
		self.IS_COMPONENT = 3

	#--------------------------------------------------------
	def _data2instance(self):
		entry_type, pk = self.GetData(as_instance = False, can_create = False)
		if entry_type == 1:
			return gmMedication.cBrandedDrug(aPK_obj = pk)
		if entry_type == 2:
			return gmMedication.cConsumableSubstance(aPK_obj = pk)
		if entry_type == 3:
			return gmMedication.cDrugComponent(aPK_obj = pk)
		raise ValueError('entry type must be 1=brand or 2=substance or 3=component')

#============================================================
class cSubstanceSchedulePhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):

		query = u"""
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
		self.SetToolTipString(_('The schedule for taking this substance.'))
		self.matcher = mp
		self.selection_only = False

#============================================================
class cSubstanceAimPhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):

		query = u"""
(
	SELECT DISTINCT ON (field_label)
		aim
			AS data,
		aim || ' (' || substance || ' ' || amount || ' ' || unit || ')'
			AS list_label,
		aim
			AS field_label
	FROM clin.v_substance_intakes
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
	FROM clin.v_substance_intakes
	WHERE
		aim %(fragment_condition)s
)
ORDER BY list_label
LIMIT 30"""

		context = {'ctxt_substance': {
			'where_part': u'AND substance = %(substance)s',
			'placeholder': u'substance'
		}}

		mp = gmMatchProvider.cMatchProvider_SQL2(queries = query, context = context)
		mp.setThresholds(1, 2, 4)
		#mp.word_separators = '[ \t=+&:@]+'
		gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)
		self.SetToolTipString(_('The medical aim for consuming this substance.'))
		self.matcher = mp
		self.selection_only = False

#============================================================
def turn_substance_intake_into_allergy(parent=None, intake=None, emr=None):

	if intake['is_currently_active']:
		intake['discontinued'] = gmDateTime.pydt_now_here()
	if intake['discontinue_reason'] is None:
		intake['discontinue_reason'] = u'%s %s' % (_('not tolerated:'), _('discontinued due to allergy or intolerance'))
	else:
		if not intake['discontinue_reason'].startswith(_('not tolerated:')):
			intake['discontinue_reason'] = u'%s %s' % (_('not tolerated:'), intake['discontinue_reason'])
	if not intake.save():
		return False

	allg = intake.turn_into_allergy(encounter_id = emr.active_encounter['pk_encounter'])

	brand = intake.containing_drug
	if brand is not None:
		comps = [ c['substance'] for c in brand.components ]
		if len(comps) > 1:
			gmGuiHelpers.gm_show_info (
				aTitle = _(u'Documented an allergy'),
				aMessage = _(
					u'An allergy was documented against the substance:\n'
					u'\n'
					u'  [%s]\n'
					u'\n'
					u'This substance was taken with the multi-component brand:\n'
					u'\n'
					u'  [%s (%s)]\n'
					u'\n'
					u'Note that ALL components of this brand were discontinued.'
				) % (
					intake['substance'],
					intake['brand'],
					u' & '.join(comps)
				)
			)

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	dlg = gmAllergyWidgets.cAllergyManagerDlg(parent = parent, id = -1)
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
#		drug_db = get_drug_database(parent = parent)
#		if drug_db is None:
#			return False
#		drug_db.import_drugs()
#		return True
#	#------------------------------------------------------------
#	def edit(substance=None):
#		return edit_consumable_substance(parent = parent, substance = substance, single_entry = (substance is not None))
#	#------------------------------------------------------------
#	def delete(substance):
#		if substance.is_in_use_by_patients:
#			gmDispatcher.send(signal = 'statustext', msg = _('Cannot delete this substance. It is in use.'), beep = True)
#			return False
#
#		return gmMedication.delete_consumable_substance(substance = substance['pk'])
	#------------------------------------------------------------
	def get_tooltip(intake=None):
		return intake.format(one_line = False, show_all_brand_components = True)
	#------------------------------------------------------------
	def refresh(lctrl):
		intakes = emr.get_current_substance_intakes (
			include_inactive = False,
			include_unapproved = True,
			order_by = u'substance, brand, started'
		)
		items = []
		for i in intakes:
			started = i.medically_formatted_start
			items.append ([
				u'%s%s %s %s %s%s' % (
					i['substance'],
					gmTools.coalesce(i['brand'], u'', u' (%s)'),
					i['amount'],
					i['unit'],
					i['preparation'],
					gmTools.coalesce(i['external_code_brand'], u'', u' [%s::%s]' % (i['external_code_type_brand'], i['external_code_brand']))
				),
				u'%s%s%s' % (
					started,
					gmTools.coalesce(i['schedule'], u'', u' %%s %s' % gmTools.u_right_arrow),
					gmTools.coalesce(i['duration'], u'', u' %s')
				),
				u'%s' % (
					gmTools.bool2subst (
						i['intake_is_approved_of'],
						u'',
						_('disapproved')
					)
				)
			])
		lctrl.set_string_items(items)
		lctrl.set_data(intakes)
	#------------------------------------------------------------
	msg = _('Substances consumed by the patient:')

	return gmListWidgets.get_choices_from_list (
		parent = parent,
		msg = msg,
		caption = _('Showing consumable substances.'),
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

	#----------------------------------------------------------------
	def __refresh_allergies(self):
		curr_pat = gmPerson.gmCurrentPatient()
		emr = curr_pat.emr

		state = emr.allergy_state
		if state['last_confirmed'] is None:
			confirmed = _('never')
		else:
			confirmed = gmDateTime.pydt_strftime(state['last_confirmed'], '%Y %b %d')
		msg = _(u'%s, last confirmed %s\n') % (state.state_string, confirmed)
		msg += gmTools.coalesce(state['comment'], u'', _('Comment (%s): %%s\n') % state['modified_by'])

		tt = u''

		allgs = emr.get_allergies()
		if len(allgs) > 0:
			msg += u'\n'
		for allergy in allgs:
			msg += u'%s: %s (%s)\n' % (
				allergy['descriptor'],
				allergy['l10n_type'],
				gmTools.bool2subst(allergy['definite'], _('definite'), _('suspected'), u'?')
			)
			tt += u'%s: %s\n' % (
				allergy['descriptor'],
				gmTools.coalesce(allergy['reaction'], _('reaction not recorded'))
			)

		if len(allgs) > 0:
			msg += u'\n'
			tt += u'\n'

		gfr = emr.get_most_recent_results(loinc = gmLOINC.LOINC_gfr_quantity, no_of_results = 1)
		if gfr is None:
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
						eol = u'\n',
						with_formula = False,
						with_warnings = True,
						with_variables = False,
						with_sub_results = False,
						return_list = False
					))
				tt += u'\n'.join(tts)
		else:
			msg += u'%s: %s %s (%s)\n' % (
				gfr['unified_abbrev'],
				gfr['unified_val'],
				gmTools.coalesce(gfr['abnormality_indicator'], u'', u' (%s)'),
				gmDateTime.pydt_strftime (
					gfr['clin_when'],
					format = '%Y %b %d'
				)
			)
			tt += _('GFR reported by path lab')

		edc = emr.EDC
		if edc is not None:
			msg += u'\n\n'
			if emr.EDC_is_fishy:
				msg += _(u'EDC (!?!): %s') % gmDateTime.pydt_strftime(edc, format = '%Y %b %d')
				tt += _(
					u'The Expected Date of Confinement is rather questionable.\n'
					u'\n'
					u'Please check patient age, patient gender, time until/since EDC.'
				)
			else:
				msg += _(u'EDC: %s') % gmDateTime.pydt_strftime(edc, format = '%Y %b %d')

		self._LBL_allergies.SetLabel(msg)
		self._LBL_allergies.SetToolTipString(tt)
	#----------------------------------------------------------------
	def __refresh_drug_details(self):

		drug = self._PRW_drug.GetData(as_instance = True)
		if drug is None:
			self._TCTRL_drug_details.SetValue(u'')
			self._TCTRL_drug_details.SetToolTipString(u'')
			return

		entry_type, pk = self._PRW_drug.GetData(as_instance = False)

		if entry_type == self._PRW_drug.IS_SUBSTANCE:
			self._TCTRL_drug_details.SetValue (u'%s %s%s%s' % (
				drug['description'],
				drug['amount'],
				drug['unit'],
				gmTools.coalesce(drug['atc_code'], u'', u' [%s]')
			))
			self._TCTRL_drug_details.SetToolTipString(u'')
			return

		if entry_type == self._PRW_drug.IS_COMPONENT:
			component = drug
			drug = component.containing_drug
			self._TCTRL_drug_details.SetValue(u'%s: %s' % (
				drug['brand'],
				u'; '.join(drug['components'])
			))
			self._TCTRL_drug_details.SetToolTipString(component.format())
			return

		if entry_type == self._PRW_drug.IS_BRAND:
			self._TCTRL_drug_details.SetValue(u'%s: %s' % (
				drug['brand'],
				u'; '.join(drug['components'])
			))
			self._TCTRL_drug_details.SetToolTipString(drug.format())
			return

	#----------------------------------------------------------------
	# generic Edit Area mixin API
	#----------------------------------------------------------------
	def _check_drug_is_valid(self):

		self._PRW_drug.display_as_valid(True)

		# we aren't editing
		if self.mode != 'new':
			return True

		selected_drug = self._PRW_drug.GetData(as_instance = True)

		# no drug selected
		if selected_drug is None:
			self._PRW_drug.display_as_valid(False)
			self._PRW_drug.SetFocus()
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
			return False

		entry_type, pk = self._PRW_drug.GetData(as_instance = False)
		if entry_type in [self._PRW_drug.IS_COMPONENT, self._PRW_drug.IS_BRAND]:
			self._PRW_preparation.display_as_valid(True)
			return True

		if self._PRW_preparation.GetValue().strip() == u'':
			self._PRW_preparation.display_as_valid(False)
			return False

		return True

	#----------------------------------------------------------------
	def _valid_for_save(self):

		validity = self._check_drug_is_valid()

		# episode must be set if intake is to be approved of
		if self._CHBOX_approved.IsChecked():
			if self._PRW_episode.GetValue().strip() == u'':
				self._PRW_episode.display_as_valid(False)
				validity = False
			else:
				self._PRW_episode.display_as_valid(True)

		if self._PRW_duration.GetValue().strip() in [u'', gmTools.u_infinity]:
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
		if self._CHBOX_start_unknown.IsChecked() is False:
			started = self._DP_started.GetData()
			if started is None:
				self._DP_started.display_as_valid(False)
				self._DP_started.SetFocus()
				validity = False
			else:
				self._DP_started.display_as_valid(True)

		if validity is False:
			gmDispatcher.send(signal = 'statustext', msg = _('Input incomplete/invalid for saving as substance intake.'))

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
				gmDispatcher.send(signal = 'statustext', msg = _('Discontinued (%s) in the future (now: %s)!') % (discontinued, now))
			else:
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
					gmDispatcher.send(signal = 'statustext', msg = _('Discontinued (%s) before started (%s) !') % (discontinued, started))
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
			episode = epi,
			preparation = self._PRW_preparation.GetValue().strip()
		)

		if intake is None:
			gmDispatcher.send('statustext', msg = _('Cannot add duplicate of (maybe inactive) substance intake.'), beep = True)
			return False

		intake['started'] = self._DP_started.GetData()
		if self._CHBOX_start_unknown.IsChecked():
			intake['comment_on_start'] = u'?'
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
		intake['is_long_term'] = self._CHBOX_long_term.IsChecked()
		intake['intake_is_approved_of'] = self._CHBOX_approved.IsChecked()
		if self._PRW_duration.GetValue().strip() in [u'', gmTools.u_infinity]:
			intake['duration'] = None
		else:
			if self._PRW_duration.GetData() is None:
				intake['duration'] = gmDateTime.str2interval(self._PRW_duration.GetValue())
			else:
				intake['duration'] = self._PRW_duration.GetData()
		intake.save()

		self.data = intake

		return True
	#----------------------------------------------------------------
	def _save_as_update(self):

		# auto-applies to all components of a multi-component drug if any:
		self.data['started'] = self._DP_started.GetData()
		if self._CHBOX_start_unknown.IsChecked():
			self.data['comment_on_start'] = u'?'
		else:
			self.data['comment_on_start'] = self._PRW_start_certainty.GetValue().strip()
		self.data['discontinued'] = self._DP_discontinued.GetData()
		if self.data['discontinued'] is None:
			self.data['discontinue_reason'] = None
		else:
			self.data['discontinue_reason'] = self._PRW_discontinue_reason.GetValue().strip()
		self.data['schedule'] = self._PRW_schedule.GetValue()
		self.data['is_long_term'] = self._CHBOX_long_term.IsChecked()
		self.data['intake_is_approved_of'] = self._CHBOX_approved.IsChecked()
		if self._PRW_duration.GetValue().strip() in [u'', gmTools.u_infinity]:
			self.data['duration'] = None
		else:
			if self._PRW_duration.GetData() is None:
				self.data['duration'] = gmDateTime.str2interval(self._PRW_duration.GetValue())
			else:
				self.data['duration'] = self._PRW_duration.GetData()

		# applies to non-component substances only
		self.data['preparation'] = self._PRW_preparation.GetValue()

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
		self._PRW_drug.SetText(u'', None)

		self._PRW_preparation.SetText(u'', None)
		self._PRW_preparation.Enable(True)

		self._PRW_schedule.SetText(u'', None)
		self._PRW_duration.SetText(u'', None)
		self._PRW_aim.SetText(u'', None)
		self._PRW_notes.SetText(u'', None)
		self._PRW_episode.SetText(u'', None)

		self._CHBOX_long_term.SetValue(False)
		self._CHBOX_approved.SetValue(True)

		self._CHBOX_start_unknown.SetValue(False)
		self._DP_started.SetData(gmDateTime.pydt_now_here())
		self._DP_started.Enable(True)
		self._PRW_start_certainty.SetText(u'', None)
		self._PRW_start_certainty.Enable(True)
		self._DP_discontinued.SetData(None)
		self._PRW_discontinue_reason.SetValue(u'')

		self.__refresh_drug_details()
		self.__refresh_allergies()

		self._PRW_drug.SetFocus()
	#----------------------------------------------------------------
	def _refresh_from_existing(self):

		if self.data['pk_brand'] is None:
			self._PRW_drug.SetText (
				u'%s %s %s' % (self.data['substance'], self.data['amount'], self.data['unit'])
				[self._PRW_drug.IS_SUBSTANCE, self.data['pk_substance']]
			)
		else:
			self._PRW_drug.SetText (
				u'%s %s %s' % (self.data['substance'], self.data['amount'], self.data['unit']),
				[self._PRW_drug.IS_COMPONENT, self.data['pk_drug_component']]
			)

		self._PRW_drug.Disable()
		self._PRW_preparation.SetText(self.data['preparation'], self.data['preparation'])
		self._PRW_preparation.Disable()

		if self.data['is_long_term']:
	 		self._CHBOX_long_term.SetValue(True)
			self._PRW_duration.Enable(False)
			self._PRW_duration.SetText(gmTools.u_infinity, None)
			self._BTN_discontinued_as_planned.Enable(False)
		else:
			self._CHBOX_long_term.SetValue(False)
			self._PRW_duration.Enable(True)
			self._BTN_discontinued_as_planned.Enable(True)
			self._PRW_duration.SetData(self.data['duration'])
#			if self.data['duration'] is None:
#				self._PRW_duration.SetText(u'', None)
#			else:
#				self._PRW_duration.SetText(gmDateTime.format_interval(self.data['duration'], gmDateTime.acc_days), self.data['duration'])
		self._PRW_aim.SetText(gmTools.coalesce(self.data['aim'], u''), self.data['aim'])
		self._PRW_notes.SetText(gmTools.coalesce(self.data['notes'], u''), self.data['notes'])
		self._PRW_episode.SetData(self.data['pk_episode'])
		self._PRW_schedule.SetText(gmTools.coalesce(self.data['schedule'], u''), self.data['schedule'])

		self._CHBOX_approved.SetValue(self.data['intake_is_approved_of'])

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
		self._PRW_discontinue_reason.SetValue(gmTools.coalesce(self.data['discontinue_reason'], u''))
		if self.data['discontinued'] is not None:
			self._PRW_discontinue_reason.Enable()

		self.__refresh_drug_details()
		self.__refresh_allergies()

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

		drug = self._PRW_drug.GetData(as_instance = True)
		if drug is None:
			self._PRW_preparation.Enable(True)
			return

		if isinstance(drug, gmMedication.cConsumableSubstance):
			self._PRW_preparation.Enable(True)
			return

		if isinstance(drug, gmMedication.cBrandedDrug):
			self._PRW_preparation.SetValue(drug['preparation'])
			self._PRW_preparation.Enable(False)
			return

		if isinstance(drug, gmMedication.cDrugComponent):
			self._PRW_preparation.SetValue(drug['preparation'])
			self._PRW_preparation.Enable(False)
			return

	#----------------------------------------------------------------
	def _on_enter_aim(self):
		# when a drug component/substance is selected (that is, when .GetData()
		# returns not None) then we do not want to use the GetValue().strip()
		# result because that will also have amount and unit appended, hence
		# create the real component or substance instance and take the canonical
		# substance name from there
		drug = self._PRW_drug.GetData(as_instance = True)
		if drug is None:
			self._PRW_aim.unset_context(context = u'substance')
			return
		if isinstance(drug, gmMedication.cBrandedDrug):
			self._PRW_aim.unset_context(context = u'substance')
			return
		if isinstance(drug, gmMedication.cConsumableSubstance):
			self._PRW_aim.set_context(context = u'substance', val = drug['description'])
			return
		if isinstance(drug, gmMedication.cDrugComponent):
			self._PRW_aim.set_context(context = u'substance', val = drug['substance'])
			return

	#----------------------------------------------------------------
	def _on_discontinued_date_changed(self, event):
		if self._DP_discontinued.GetData() is None:
			self._PRW_discontinue_reason.Enable(False)
		else:
			self._PRW_discontinue_reason.Enable(True)

	#----------------------------------------------------------------
	def _on_manage_brands_button_pressed(self, event):
		manage_branded_drugs(parent = self, ignore_OK_button = True)

	#----------------------------------------------------------------
	def _on_manage_substances_button_pressed(self, event):
		manage_consumable_substances(parent = self)

	#----------------------------------------------------------------
	def _on_heart_button_pressed(self, event):
		gmNetworkTools.open_url_in_browser(url = u'http://www.qtsyndrome.ch/drugs.html')

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

		self.__refresh_allergies()

		if self.data is None:
			return

		# do we have a (full) plan ?
		if None not in [self.data['started'], self.data['duration']]:
			planned_end = self.data['started'] + self.data['duration']
			# the plan hasn't ended so [Per plan] can't apply ;-)
			if planned_end > now:
				return
			self._DP_discontinued.SetData(planned_end)
			self._PRW_discontinue_reason.Enable(True)
			self._PRW_discontinue_reason.SetValue(u'')
			return

		# we know started but not duration: apparently the plan is to stop today
		if self.data['started'] is not None:
			# but we haven't started yet so we can't stop
			if self.data['started'] > now:
				return

		self._DP_discontinued.SetData(now)
		self._PRW_discontinue_reason.Enable(True)
		self._PRW_discontinue_reason.SetValue(u'')

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

		self.__refresh_allergies()

	#----------------------------------------------------------------
	def _on_start_unknown_checked(self, event):
		event.Skip()
		if self._CHBOX_start_unknown.IsChecked() is True:
			self._DP_started.Enable(False)
			self._PRW_start_certainty.Enable(False)
		else:
			self._DP_started.Enable(True)
			self._PRW_start_certainty.Enable(True)

		self.__refresh_allergies()

	#----------------------------------------------------------------
	def turn_into_allergy(self, data=None):
		if not self.save():
			return False

		return turn_substance_intake_into_allergy (
			parent = self,
			intake = self.data,
			emr = gmPerson.gmCurrentPatient().get_emr()
		)

#============================================================
def delete_substance_intake(parent=None, substance=None):

	subst = gmMedication.cSubstanceIntakeEntry(aPK_obj = substance)
	msg = _(
		'\n'
		'[%s]\n'
		'\n'
		'It may be prudent to edit (before deletion) the details\n'
		'of this substance intake entry so as to leave behind\n'
		'some indication of why it was deleted.\n'
	) % subst.format()

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
	dlg.Destroy()

	if edit_first == wx.ID_CANCEL:
		return

	if edit_first == wx.ID_YES:
		edit_intake_of_substance(parent = parent, substance = subst)
		delete_it = gmGuiHelpers.gm_show_question (
			aMessage = _('Now delete substance intake entry ?'),
			aTitle = _('Deleting medication / substance intake')
		)
	else:
		delete_it = True

	if not delete_it:
		return

	gmMedication.delete_substance_intake(substance = substance)
#------------------------------------------------------------
def edit_intake_of_substance(parent = None, substance=None):
	ea = cSubstanceIntakeEAPnl(parent = parent, id = -1, substance = substance)
	dlg = gmEditArea.cGenericEditAreaDlg2(parent = parent, id = -1, edit_area = ea, single_entry = (substance is not None))
	dlg.SetTitle(gmTools.coalesce(substance, _('Adding medication/non-medication substance intake'), _('Editing medication/non-medication substance intake')))
	dlg.left_extra_button = (
		_('Allergy'),
		_('Document an allergy against this substance.'),
		ea.turn_into_allergy
	)
	if dlg.ShowModal() == wx.ID_OK:
		dlg.Destroy()
		return True
	dlg.Destroy()
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
	option = u'form_templates.medication_list'

	if template is None:
		gmDispatcher.send(signal = 'statustext', msg = _('No medication list template configured.'), beep = True)
		return None

	if template['engine'] not in [u'L', u'X', u'T']:
		gmDispatcher.send(signal = 'statustext', msg = _('No medication list template configured.'), beep = True)
		return None

	dbcfg = gmCfg.cCfgSQL()
	dbcfg.set (
		workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
		option = option,
		value = u'%s - %s' % (template['name_long'], template['external_version'])
	)

	return template
#------------------------------------------------------------
def print_medication_list(parent=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	# 1) get template
	dbcfg = gmCfg.cCfgSQL()
	option = u'form_templates.medication_list'

	template = dbcfg.get2 (
		option = option,
		workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
		bias = 'user'
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
			name, ver = template.split(u' - ')
		except:
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

	if template['engine'] not in [u'L', u'X', u'T']:
		gmDispatcher.send(signal = 'statustext', msg = _('No prescription template configured.'), beep = True)
		return None

	option = u'form_templates.prescription'
	dbcfg = gmCfg.cCfgSQL()
	dbcfg.set (
		workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
		option = option,
		value = u'%s - %s' % (template['name_long'], template['external_version'])
	)

	return template
#------------------------------------------------------------
def get_prescription_template(parent=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	dbcfg = gmCfg.cCfgSQL()
	option = u'form_templates.prescription'
	template_name = dbcfg.get2 (
		option = option,
		workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
		bias = 'user'
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
		name, ver = template_name.split(u' - ')
	except:
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
		jobtype = u'prescription',
		#episode_name = u'administrative',
		episode_name = gmMedication.DEFAULT_MEDICATION_HISTORY_EPISODE,
		progress_note = _('generated prescription'),
		review_copy_as_normal = True
	)

#------------------------------------------------------------
def prescribe_drugs(parent=None, emr=None):

	dbcfg = gmCfg.cCfgSQL()
	rx_mode = dbcfg.get2 (
		option = u'horst_space.default_prescription_mode',
		workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
		bias = u'user',
		default = u'form'			# set to 'database' to access database
	)

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	if rx_mode == 'form':
		return print_prescription(parent = parent, emr = emr)

	if rx_mode == 'database':
		drug_db = get_drug_database()
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

	curr_brands =  [ i['pk_brand'] for i in emr.get_current_substance_intakes() if i['pk_brand'] is not None ]
	new_drugs = []
	for drug in prescribed_drugs:
		if drug['pk_brand'] not in curr_brands:
			new_drugs.append(drug)

	if len(new_drugs) == 0:
		return

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	picker = gmListWidgets.cItemPickerDlg (
		parent,
		-1,
		msg = _(
			'These brands have been prescribed but are not listed\n'
			'in the current medication list of this patient.\n'
			'\n'
			'Please select those you want added to the medication list.'
		)
	)
	picker.set_columns (
		columns = [_('Newly prescribed drugs')],
		columns_right = [_('Add to medication list')]
	)
	choices = [ (u'%s %s (%s)' % (d['brand'], d['preparation'], u'; '.join(d['components']))) for d in new_drugs ]
	picker.set_choices (
		choices = choices,
		data = new_drugs
	)
	picker.ShowModal()
	drugs2add = picker.get_picks()
	picker.Destroy()

	if drugs2add is None:
		return

	if len(drugs2add) == 0:
		return

	for drug in drugs2add:
		# only add first component since all other components get added by a trigger ...
		intake = emr.add_substance_intake (
			pk_component = drug['pk_components'][0],
			episode = emr.add_episode(episode_name = gmMedication.DEFAULT_MEDICATION_HISTORY_EPISODE)['pk_episode'],
		)
		if intake is None:
			continue
		intake['intake_is_approved_of'] = True
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
		self.__grouping_mode = u'issue'
		self.__filter_show_unapproved = True
		self.__filter_show_inactive = True

		self.__grouping2col_labels = {
			u'issue': [
				_('Health issue'),
				_('Substance'),
				_('Strength'),
				_('Schedule'),
				_('Started'),
				_('Duration / Until'),
				_('Brand'),
				_('Advice')
			],
			u'brand': [
				_('Brand'),
				_('Schedule'),
				_('Substance'),
				_('Strength'),
				_('Started'),
				_('Duration / Until'),
				_('Health issue'),
				_('Advice')
			],
			u'episode': [
				_('Episode'),
				_('Substance'),
				_('Strength'),
				_('Schedule'),
				_('Started'),
				_('Duration / Until'),
				_('Brand'),
				_('Advice')
			],
			u'start': [
				_('Episode'),
				_('Substance'),
				_('Strength'),
				_('Schedule'),
				_('Started'),
				_('Duration / Until'),
				_('Brand'),
				_('Advice')
			],
		}

		self.__grouping2order_by_clauses = {
			u'issue': u'pk_health_issue nulls first, substance, started',
			u'episode': u'pk_health_issue nulls first, episode, substance, started',
			u'brand': u'brand nulls last, substance, started',
			u'start': u'started DESC, substance, episode'
		}

		self.__init_ui()
		self.__register_events()
	#------------------------------------------------------------
	# external API
	#------------------------------------------------------------
	def get_selected_cells(self):

		sel_block_top_left = self.GetSelectionBlockTopLeft()
		sel_block_bottom_right = self.GetSelectionBlockBottomRight()
		sel_cols = self.GetSelectedCols()
		sel_rows = self.GetSelectedRows()

		selected_cells = []

		# individually selected cells (ctrl-click)
		selected_cells += self.GetSelectedCells()

		# selected rows
		selected_cells += list (
			(row, col)
				for row in sel_rows
				for col in xrange(self.GetNumberCols())
		)

		# selected columns
		selected_cells += list (
			(row, col)
				for row in xrange(self.GetNumberRows())
				for col in sel_cols
		)

		# selection blocks
		for top_left, bottom_right in zip(self.GetSelectionBlockTopLeft(), self.GetSelectionBlockBottomRight()):
			selected_cells += [
				(row, col)
					for row in xrange(top_left[0], bottom_right[0] + 1)
					for col in xrange(top_left[1], bottom_right[1] + 1)
			]

		return set(selected_cells)
	#------------------------------------------------------------
	def get_selected_rows(self):
		rows = {}

		for row, col in self.get_selected_cells():
			rows[row] = True

		return rows.keys()
	#------------------------------------------------------------
	def get_selected_data(self):
		return [ self.__row_data[row] for row in self.get_selected_rows() ]
	#------------------------------------------------------------
	def repopulate_grid(self):

		self.empty_grid()

		if self.__patient is None:
			return

		emr = self.__patient.get_emr()
		meds = emr.get_current_substance_intakes (
			order_by = self.__grouping2order_by_clauses[self.__grouping_mode],
			include_unapproved = self.__filter_show_unapproved,
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
			self.SetColLabelValue(len(labels), u'')
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
#				if med['atc_brand'] is not None:
#					atcs.append(med['atc_brand'])
#				allg = emr.is_allergic_to(atcs = tuple(atcs), inns = (med['substance'],), brand = med['brand'])
				allg = emr.is_allergic_to(atcs = tuple(atcs), inns = (med['substance'],))
				if allg not in [None, False]:
					attr = self.GetOrCreateCellAttr(row_idx, 0)
					if allg['type'] == u'allergy':
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

			if self.__grouping_mode in [u'episode', u'start']:
				if med['pk_episode'] is None:
					self.__prev_cell_0 = None
					epi = gmTools.u_diameter
				else:
					if self.__prev_cell_0 == med['episode']:
						epi = u''
					else:
						self.__prev_cell_0 = med['episode']
						epi = gmTools.coalesce(med['episode'], u'')
				self.SetCellValue(row_idx, 0, gmTools.wrap(text = epi, width = 40))

				self.SetCellValue(row_idx, 1, med['substance'])
				self.SetCellValue(row_idx, 2, u'%s %s' % (med['amount'], med['unit']))
				self.SetCellValue(row_idx, 3, gmTools.coalesce(med['schedule'], u''))
				self.SetCellValue(row_idx, 4, med.medically_formatted_start)

				if med['is_long_term']:
					self.SetCellValue(row_idx, 5, gmTools.u_infinity)
				else:
					if med['discontinued'] is None:
						if med['duration'] is None:
							self.SetCellValue(row_idx, 5, u'')
						else:
							self.SetCellValue(row_idx, 5, gmDateTime.format_interval(med['duration'], gmDateTime.acc_days))
					else:
						self.SetCellValue(row_idx, 5, med['discontinued'].strftime('%Y-%m-%d'))

				if med['pk_brand'] is None:
					brand = u'%s (%s)' % (gmTools.u_diameter, med['preparation'])
				else:
					if med['fake_brand']:
						brand = u'%s (%s)' % (
							gmTools.coalesce(med['brand'], u'', _('%s <fake>')),
							med['preparation']
						)
					else:
						brand = u'%s (%s)' % (
							gmTools.coalesce(med['brand'], u''),
							med['preparation']
						)
				self.SetCellValue(row_idx, 6, gmTools.wrap(text = brand, width = 35))

			elif self.__grouping_mode == u'issue':
				if med['pk_health_issue'] is None:
					self.__prev_cell_0 = None
					issue = u'%s%s' % (
						gmTools.u_diameter,
						gmTools.coalesce(med['episode'], u'', u' (%s)')
					)
				else:
					if self.__prev_cell_0 == med['health_issue']:
						issue = u''
					else:
						self.__prev_cell_0 = med['health_issue']
						issue = med['health_issue']
				self.SetCellValue(row_idx, 0, gmTools.wrap(text = issue, width = 40))

				self.SetCellValue(row_idx, 1, med['substance'])
				self.SetCellValue(row_idx, 2, u'%s %s' % (med['amount'], med['unit']))
				self.SetCellValue(row_idx, 3, gmTools.coalesce(med['schedule'], u''))
				self.SetCellValue(row_idx, 4, med.medically_formatted_start)

				if med['is_long_term']:
					self.SetCellValue(row_idx, 5, gmTools.u_infinity)
				else:
					if med['discontinued'] is None:
						if med['duration'] is None:
							self.SetCellValue(row_idx, 5, u'')
						else:
							self.SetCellValue(row_idx, 5, gmDateTime.format_interval(med['duration'], gmDateTime.acc_days))
					else:
						self.SetCellValue(row_idx, 5, med['discontinued'].strftime('%Y-%m-%d'))

				if med['pk_brand'] is None:
					brand = u'%s (%s)' % (gmTools.u_diameter, med['preparation'])
				else:
					if med['fake_brand']:
						brand = u'%s (%s)' % (
							gmTools.coalesce(med['brand'], u'', _('%s <fake>')),
							med['preparation']
						)
					else:
						brand = u'%s (%s)' % (
							gmTools.coalesce(med['brand'], u''),
							med['preparation']
						)
				self.SetCellValue(row_idx, 6, gmTools.wrap(text = brand, width = 35))

			elif self.__grouping_mode == u'brand':

				if med['pk_brand'] is None:
					self.__prev_cell_0 = None
					brand =  u'%s (%s)' % (
						gmTools.u_diameter,
						med['preparation']
					)
				else:
					if self.__prev_cell_0 == med['brand']:
						brand = u''
					else:
						self.__prev_cell_0 = med['brand']
						if med['fake_brand']:
							brand = u'%s (%s)' % (
								gmTools.coalesce(med['brand'], u'', _('%s <fake>')),
								med['preparation']
							)
						else:
							brand = u'%s (%s)' % (
								gmTools.coalesce(med['brand'], u''),
								med['preparation']
							)
				self.SetCellValue(row_idx, 0, gmTools.wrap(text = brand, width = 35))

				self.SetCellValue(row_idx, 1, gmTools.coalesce(med['schedule'], u''))
				self.SetCellValue(row_idx, 2, med['substance'])
				self.SetCellValue(row_idx, 3, u'%s %s' % (med['amount'], med['unit']))
				self.SetCellValue(row_idx, 4, med.medically_formatted_start)

				if med['is_long_term']:
					self.SetCellValue(row_idx, 5, gmTools.u_infinity)
				else:
					if med['discontinued'] is None:
						if med['duration'] is None:
							self.SetCellValue(row_idx, 5, u'')
						else:
							self.SetCellValue(row_idx, 5, gmDateTime.format_interval(med['duration'], gmDateTime.acc_days))
					else:
						self.SetCellValue(row_idx, 5, med['discontinued'].strftime('%Y-%m-%d'))

				if med['pk_health_issue'] is None:
					issue = u'%s%s' % (
						gmTools.u_diameter,
						gmTools.coalesce(med['episode'], u'', u' (%s)')
					)
				else:
					issue = gmTools.coalesce(med['health_issue'], u'')
				self.SetCellValue(row_idx, 6, gmTools.wrap(text = issue, width = 40))

			else:
				raise ValueError('unknown grouping mode [%s]' % self.__grouping_mode)

			if med['notes'] is not None:
				self.SetCellValue(row_idx, 7, gmTools.wrap(text = med['notes'], width = 50))

			if self.__filter_show_unapproved:
				self.SetCellValue (
					row_idx,
					len(labels),
					#gmTools.bool2subst(med['intake_is_approved_of'], gmTools.u_checkmark_thin, u'', u'?')
					gmTools.bool2subst(med['intake_is_approved_of'], gmTools.u_checkmark_thin, gmTools.u_frowning_face, u'?')
				)
				font = self.GetCellFont(row_idx, len(labels))
				font.SetPointSize(font.GetPointSize() + 2)
				self.SetCellFont(row_idx, len(labels), font)

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

		drug_db = get_drug_database()
		if drug_db is None:
			return

		intake = self.get_selected_data()[0]		# just in case
		if intake['brand'] is None:
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
		gmNetworkTools.open_url_in_browser(url = u'http://www.qtsyndrome.ch/drugs.html')
	#------------------------------------------------------------
	def report_ADR(self):
		dbcfg = gmCfg.cCfgSQL()
		url = dbcfg.get2 (
			option = u'external.urls.report_ADR',
			workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
			bias = u'user',
			default = u'https://dcgma.org/uaw/meldung.php'		# http://www.akdae.de/Arzneimittelsicherheit/UAW-Meldung/UAW-Meldung-online.html
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

		drug_db = get_drug_database()
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
	def delete_substance(self):

		rows = self.get_selected_rows()

		if len(rows) == 0:
			return

		if len(rows) > 1:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot delete more than one substance at once.'), beep = True)
			return

		subst = self.get_selected_data()[0]
		delete_substance_intake(parent = self, substance = subst['pk_substance_intake'])
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
			emr = self.__patient.get_emr()
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
			return u' '

		emr = self.__patient.get_emr()
		atcs = []
		if entry['atc_substance'] is not None:
			atcs.append(entry['atc_substance'])
#		if entry['atc_brand'] is not None:
#			atcs.append(entry['atc_brand'])
#		allg = emr.is_allergic_to(atcs = tuple(atcs), inns = (entry['substance'],), brand = entry['brand'])
		allg = emr.is_allergic_to(atcs = tuple(atcs), inns = (entry['substance'],))

		tt = _('Substance intake entry (%s, %s)   [#%s]                     \n') % (
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
			gmTools.bool2subst (
				boolean = entry['intake_is_approved_of'],
				true_return = _('approved'),
				false_return = _('unapproved')
			),
			entry['pk_substance_intake']
		)

		if allg not in [None, False]:
			certainty = gmTools.bool2subst(allg['definite'], _('definite'), _('suspected'))
			tt += u'\n'
			tt += u' !! ---- Cave ---- !!\n'
			tt += u' %s (%s): %s (%s)\n' % (
				allg['l10n_type'],
				certainty,
				allg['descriptor'],
				gmTools.coalesce(allg['reaction'], u'')[:40]
			)
			tt += u'\n'

		tt += u' ' + _('Substance: %s   [#%s]\n') % (entry['substance'], entry['pk_substance'])
		tt += u' ' + _('Preparation: %s\n') % entry['preparation']
		tt += u' ' + _('Amount per dose: %s %s') % (entry['amount'], entry['unit'])
		tt += u'\n'
		tt += gmTools.coalesce(entry['atc_substance'], u'', _(' ATC (substance): %s\n'))

		tt += u'\n'

		tt += gmTools.coalesce (
			entry['brand'],
			u'',
			_(' Brand name: %%s   [#%s]\n') % entry['pk_brand']
		)
		tt += gmTools.coalesce(entry['atc_brand'], u'', _(' ATC (brand): %s\n'))

		tt += u'\n'

		tt += gmTools.coalesce(entry['schedule'], u'', _(' Regimen: %s\n'))

		if entry['is_long_term']:
			duration = u' %s %s' % (gmTools.u_right_arrow, gmTools.u_infinity)
		else:
			if entry['duration'] is None:
				duration = u''
			else:
				duration = u' %s %s' % (gmTools.u_right_arrow, gmDateTime.format_interval(entry['duration'], gmDateTime.acc_days))

		tt += _(' Started %s%s%s\n') % (
			entry.medically_formatted_start,
			duration,
			gmTools.bool2subst(entry['is_long_term'], _(' (long-term)'), _(' (short-term)'), u'')
		)

		if entry['discontinued'] is not None:
			tt += _(' Discontinued %s\n') % gmDateTime.pydt_strftime(entry['discontinued'], '%Y %b %d')
			tt += _(' Reason: %s\n') % entry['discontinue_reason']

		tt += u'\n'

		tt += gmTools.coalesce(entry['aim'], u'', _(' Aim: %s\n'))
		tt += gmTools.coalesce(entry['episode'], u'', _(' Episode: %s\n'))
		tt += gmTools.coalesce(entry['health_issue'], u'', _(' Health issue: %s\n'))
		tt += gmTools.coalesce(entry['notes'], u'', _(' Advice: %s\n'))

		tt += u'\n'

		tt += _(u'Revision: #%(row_ver)s, %(mod_when)s by %(mod_by)s.') % ({
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
#        for col in xrange(self.NumberCols):
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
			evt.GetEventObject().SetToolTipString(self.get_row_tooltip(row = row))
		except KeyError:
			pass
	#------------------------------------------------------------
	def __on_cell_left_dclicked(self, evt):
		row = evt.GetRow()
		data = self.__row_data[row]
		edit_intake_of_substance(parent = self, substance = data)

#============================================================
def configure_default_medications_lab_panel(parent=None):

	panels = gmPathLab.get_test_panels(order_by = u'description')
	gmCfgWidgets.configure_string_from_list_option (
		parent = parent,
		message = _(
			'\n'
			'Select the measurements panel to show in the medications plugin.'
			'\n'
		),
		option = u'horstspace.medications_plugin.lab_panel',
		bias = 'user',
		default_value = None,
		choices = [ u'%s%s' % (p['description'], gmTools.coalesce(p['comment'], u'', u' (%s)')) for p in panels ],
		columns = [_('Measurements panel')],
		data = [ p['pk_test_panel'] for p in panels ],
		caption = _('Configuring medications plugin measurements panel')
	)

#============================================================
from Gnumed.wxGladeWidgets import wxgCurrentSubstancesPnl

class cCurrentSubstancesPnl(wxgCurrentSubstancesPnl.wxgCurrentSubstancesPnl, gmRegetMixin.cRegetOnPaintMixin):

	"""Panel holding a grid with current substances. Used as notebook page."""

	def __init__(self, *args, **kwargs):

		wxgCurrentSubstancesPnl.wxgCurrentSubstancesPnl.__init__(self, *args, **kwargs)
		gmRegetMixin.cRegetOnPaintMixin.__init__(self)

		self.__grouping_choice_labels = [
			{u'label': _('Health issue'), u'data': u'issue'} ,
			{u'label': _('Brand'), u'data': u'brand'},
			{u'label': _('Episode'), u'data': u'episode'},
			{u'label': _('Started'), u'data': u'start'}
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

		if self.__lab_panel is None:
			self.Layout()
			return

		most_recent_results = self.__lab_panel.get_most_recent_results(pk_patient = patient.ID, order_by = u'unified_abbrev', group_by_meta_type = True)
		edc = patient.emr.EDC
		gfr = patient.emr.get_most_recent_results(loinc = gmLOINC.LOINC_gfr_quantity, no_of_results = 1)
		crea = patient.emr.get_most_recent_results(loinc = gmLOINC.LOINC_creatinine_quantity, no_of_results = 1)

		if (len(most_recent_results) == 0) and (edc is None) and (gfr is None) and (crea is None):
			self.Layout()
			return

		if edc is not None:
			if emr.EDC_is_fishy:
				lbl = wx.StaticText(self, -1, _(u'EDC (!?!):'))
				val = wx.StaticText(self, -1, gmDateTime.pydt_strftime(edc, format = '%Y %b %d'))
			else:
				lbl = wx.StaticText(self, -1, _(u'EDC:'))
				val = wx.StaticText(self, -1, gmDateTime.pydt_strftime(edc, format = '%Y %b %d'))
			lbl.SetForegroundColour('blue')
			szr = wx.BoxSizer(wx.HORIZONTAL)
			szr.Add(lbl, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 3)
			szr.Add(val, 1, wx.ALIGN_CENTER_VERTICAL)
			self._GSZR_lab.Add(szr)

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

		now = gmDateTime.pydt_now_here()

		# if GFR not found in most_recent_results or old, then calculate
		if gfr_3_months_older_than_crea:
			calc = gmClinicalCalculator.cClinicalCalculator()
			calc.patient = patient
			gfr = calc.eGFR
			if gfr.numeric_value is None:
				gfr_msg = u'?'
			else:
				gfr_msg = _(u'%.1f (%s ago)') % (
					gfr.numeric_value,
					gmDateTime.format_interval_medically(now - gfr.date_valid)
				)
			lbl = wx.StaticText(self, -1, _('eGFR:'))
			lbl.SetForegroundColour('blue')
			val = wx.StaticText(self, -1, gfr_msg)
			egfrs = calc.eGFRs
			tts = []
			for egfr in egfrs:
				if egfr.numeric_value is None:
					continue
				tts.append(egfr.format (
					left_margin = 0,
					width = 50,
					eol = u'\n',
					with_formula = False,
					with_warnings = True,
					with_variables = False,
					with_sub_results = False,
					return_list = False
				))
				tt = u'\n'.join(tts)
			val.SetToolTipString(tt)
			szr = wx.BoxSizer(wx.HORIZONTAL)
			szr.Add(lbl, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 3)
			szr.Add(val, 1, wx.ALIGN_CENTER_VERTICAL)
			self._GSZR_lab.Add(szr)

		for result in most_recent_results:
			lbl = wx.StaticText(self, -1, u'%s:' % result['unified_abbrev'])
			lbl.SetForegroundColour('blue')
			val = wx.StaticText(self, -1, _(u'%s%s%s (%s ago)') % (
				result['unified_val'],
				gmTools.coalesce(result['val_unit'], u'', u' %s'),
				gmTools.coalesce(result.formatted_abnormality_indicator, u'', u' %s'),
				gmDateTime.format_interval_medically(now - result['clin_when'])
			))
			val.SetToolTipString(result.format())
			if result.is_considered_abnormal:
				val.SetForegroundColour('red')
			szr = wx.BoxSizer(wx.HORIZONTAL)
			szr.Add(lbl, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 3)
			szr.Add(val, 1, wx.ALIGN_CENTER_VERTICAL)
			self._GSZR_lab.Add(szr)

		self._HLINE_lab.Show()
		self.Layout()
	#--------------------------------------------------------
	def __refresh_gfr(self, patient):
		gfr = patient.emr.get_most_recent_results(loinc = gmLOINC.LOINC_gfr_quantity, no_of_results = 1)
		if gfr is None:
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
						eol = u'\n',
						with_formula = False,
						with_warnings = True,
						with_variables = False,
						with_sub_results = False,
						return_list = False
					))
				tt = u'\n'.join(tts)
		else:
			msg = u'%s: %s %s (%s)\n' % (
				gfr['unified_abbrev'],
				gfr['unified_val'],
				gmTools.coalesce(gfr['abnormality_indicator'], u'', u' (%s)'),
				gmDateTime.pydt_strftime (
					gfr['clin_when'],
					format = '%b %Y'
				)
			)
			tt = _('GFR reported by path lab')

		self._LBL_gfr.SetLabel(msg)
		self._LBL_gfr.SetToolTipString(tt)
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
		gmDispatcher.connect(signal = u'pre_patient_unselection', receiver = self._on_pre_patient_unselection)
		gmDispatcher.connect(signal = u'post_patient_selection', receiver = self._on_post_patient_selection)
		gmDispatcher.connect(signal = u'clin.substance_intake_mod_db', receiver = self._schedule_data_reget)
		gmDispatcher.connect(signal = u'clin.test_result_mod_db', receiver = self._on_test_result_mod)
		# active_substance_mod_db
		# substance_brand_mod_db
	#--------------------------------------------------------
	def _on_test_result_mod(self):
		self.__refresh_lab(patient = self._grid_substances.patient)
	#--------------------------------------------------------
	def _on_pre_patient_unselection(self):
		dbcfg = gmCfg.cCfgSQL()
		pk_panel = dbcfg.get2 (
			option = u'horstspace.medications_plugin.lab_panel',
			workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
			bias = 'user'
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
		self._grid_substances.delete_substance()
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
#	#app.SetWidget(cATCPhraseWheel, -1)
	#app.SetWidget(cSubstancePhraseWheel, -1)
	app.SetWidget(cBrandOrSubstancePhraseWheel, -1)
	app.MainLoop()
	#manage_substance_intakes()

#============================================================
