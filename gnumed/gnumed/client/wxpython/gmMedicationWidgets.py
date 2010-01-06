"""GNUmed medication/substances handling widgets.
"""
#================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmMedicationWidgets.py,v $
# $Id: gmMedicationWidgets.py,v 1.29 2010-01-06 14:42:20 ncq Exp $
__version__ = "$Revision: 1.29 $"
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"

import logging, sys, os.path


import wx, wx.grid


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmDispatcher, gmCfg, gmShellAPI, gmTools, gmDateTime
from Gnumed.pycommon import gmMatchProvider, gmI18N, gmPrinting, gmCfg2
from Gnumed.business import gmPerson, gmATC, gmSurgery, gmMedication, gmForms
from Gnumed.wxpython import gmGuiHelpers, gmRegetMixin, gmAuthWidgets, gmEditArea, gmMacro
from Gnumed.wxpython import gmCfgWidgets, gmListWidgets, gmPhraseWheel, gmFormWidgets


_log = logging.getLogger('gm.ui')
_log.info(__version__)
#============================================================
def manage_substances_in_brands(parent=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	#------------------------------------------------------------
	def delete(component):
		gmMedication.delete_component_from_branded_drug (
			brand = component['pk_brand'],
			component = component['pk_substance_in_brand']
		)
		return True
	#------------------------------------------------------------
	def refresh(lctrl):
		substs = gmMedication.get_substances_in_brands()
		items = [ [
			u'%s%s' % (s['brand'], gmTools.coalesce(s['atc_brand'], u'', u' (%s)')),
			s['substance'],
			gmTools.coalesce(s['atc_substance'], u''),
			s['preparation'],
			gmTools.coalesce(s['external_code_brand'], u''),
			s['pk_substance_in_brand']
		] for s in substs ]
		lctrl.set_string_items(items)
		lctrl.set_data(substs)
	#------------------------------------------------------------
	msg = _('\nThese are the substances in the drug brands known to GNUmed.\n')

	gmListWidgets.get_choices_from_list (
		parent = parent,
		msg = msg,
		caption = _('Showing drug brand components (substances).'),
		columns = [_('Brand'), _('Substance'), u'ATC', _('Preparation'), _('Code'), u'#'],
		single_selection = True,
		#new_callback = new,
		#edit_callback = edit,
		delete_callback = delete,
		refresh_callback = refresh
	)
#============================================================
def manage_branded_drugs(parent=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()
	#------------------------------------------------------------
	def delete(brand):
		gmMedication.delete_branded_drug(brand = brand['pk'])
		return True
	#------------------------------------------------------------
	def new():
		drug_db = get_drug_database(parent = parent)

		if drug_db is None:
			return False

		drug_db.import_drugs()

		return True
	#------------------------------------------------------------
	def refresh(lctrl):
		drugs = gmMedication.get_branded_drugs()
		items = [ [
			d['description'],
			d['preparation'],
			gmTools.coalesce(d['atc_code'], u''),
			gmTools.coalesce(d['external_code'], u''),
			d['pk']
		] for d in drugs ]
		lctrl.set_string_items(items)
		lctrl.set_data(drugs)
	#------------------------------------------------------------
	msg = _('\nThese are the drug brands known to GNUmed.\n')

	gmListWidgets.get_choices_from_list (
		parent = parent,
		msg = msg,
		caption = _('Showing branded drugs.'),
		columns = [_('Name'), _('Preparation'), _('ATC'), _('Code'), u'#'],
		single_selection = True,
		refresh_callback = refresh,
		new_callback = new,
		#edit_callback = edit,
		delete_callback = delete
	)
#============================================================
def manage_substances_in_use(parent=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()
	#------------------------------------------------------------
	def delete(substance):
		gmMedication.delete_used_substance(substance = substance['pk'])
		return True
	#------------------------------------------------------------
	def new():
		drug_db = get_drug_database(parent = parent)

		if drug_db is None:
			return False

		drug_db.import_drugs()

		return True
	#------------------------------------------------------------
	def refresh(lctrl):
		substs = gmMedication.get_substances_in_use()
		items = [ [
			s['description'],
			gmTools.coalesce(s['atc_code'], u''),
			s['pk']
		] for s in substs ]
		lctrl.set_string_items(items)
		lctrl.set_data(substs)
	#------------------------------------------------------------
	msg = _('\nThese are the substances currently or previously\nconsumed across all patients.\n')

	gmListWidgets.get_choices_from_list (
		parent = parent,
		msg = msg,
		caption = _('Showing consumed substances.'),
		columns = [_('Name'), _('ATC'), u'#'],
		single_selection = True,
		refresh_callback = refresh,
		new_callback = new,
		#edit_callback = edit,
		delete_callback = delete
	)
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

	default_db = dbcfg.get2 (
		option = 'external.drug_data.default_source',
		workplace = gmSurgery.gmCurrentPractice().active_workplace,
		bias = 'workplace'
	)

	if default_db is None:
		gmDispatcher.send('statustext', msg = _('No default drug database configured.'), beep = True)
		configure_drug_data_source(parent = parent)
		default_db = dbcfg.get2 (
			option = 'external.drug_data.default_source',
			workplace = gmSurgery.gmCurrentPractice().active_workplace,
			bias = 'workplace'
		)
		if default_db is None:
			gmGuiHelpers.gm_show_error (
				aMessage = _('There is no default drug database configured.'),
				aTitle = _('Jumping to drug database')
			)
			return None

	try:
		return gmMedication.drug_data_source_interfaces[default_db]()
	except KeyError:
		_log.error('faulty default drug data source configuration: %s', default_db)
		return None
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
		workplace = gmSurgery.gmCurrentPractice().active_workplace,
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
			workplace = gmSurgery.gmCurrentPractice().active_workplace,
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
def update_atc_reference_data():

	dlg = wx.FileDialog (
		parent = None,
		message = _('Choose an ATC import config file'),
		defaultDir = os.path.expanduser(os.path.join('~', 'gnumed')),
		defaultFile = '',
		wildcard = "%s (*.conf)|*.conf|%s (*)|*" % (_('config files'), _('all files')),
		style = wx.OPEN | wx.HIDE_READONLY | wx.FILE_MUST_EXIST
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
# current medication widgets
#============================================================
class cSubstancePhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):

		query = u"""
(
	SELECT pk, (coalesce(atc_code || ': ', '') || description) as subst
	FROM clin.consumed_substance
	WHERE description %(fragment_condition)s
) union (
	SELECT NULL, (coalesce(atc_code || ': ', '') || description) as subst
	FROM ref.substance_in_brand
	WHERE description %(fragment_condition)s
)
order by subst
limit 50"""

		mp = gmMatchProvider.cMatchProvider_SQL2(queries = query)
		mp.setThresholds(1, 2, 4)
		gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)
		self.SetToolTipString(_('The INN / substance the patient is taking.'))
		self.matcher = mp
		self.selection_only = False
#============================================================
class cBrandedDrugPhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):

		query = u"""
			SELECT pk, (coalesce(atc_code || ': ', '') || description || ' (' || preparation || ')') as brand
			FROM ref.branded_drug
			WHERE description %(fragment_condition)s
			ORDER BY brand
			LIMIT 50"""

		mp = gmMatchProvider.cMatchProvider_SQL2(queries = query)
		mp.setThresholds(2, 3, 4)
		gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)
		self.SetToolTipString(_('The brand name of the drug the patient is taking.'))
		self.matcher = mp
		self.selection_only = False

#============================================================
from Gnumed.wxGladeWidgets import wxgCurrentMedicationEAPnl

class cCurrentMedicationEAPnl(wxgCurrentMedicationEAPnl.wxgCurrentMedicationEAPnl, gmEditArea.cGenericEditAreaMixin):

	def __init__(self, *args, **kwargs):

		try:
			data = kwargs['substance']
			del kwargs['substance']
		except KeyError:
			data = None

		wxgCurrentMedicationEAPnl.wxgCurrentMedicationEAPnl.__init__(self, *args, **kwargs)
		gmEditArea.cGenericEditAreaMixin.__init__(self)
		self.mode = 'new'
		self.data = data
		if data is not None:
			self.mode = 'edit'

		self.__init_ui()
	#----------------------------------------------------------------
	def __init_ui(self):

		# adjust phrasewheels

		self._PRW_brand.add_callback_on_lose_focus(callback = self._on_leave_brand)

	#----------------------------------------------------------------
	# generic Edit Area mixin API
	#----------------------------------------------------------------
	def _valid_for_save(self):

		validity = True

		if self._PRW_substance.GetValue().strip() == u'':
			self._PRW_substance.display_as_valid(False)
			validity = False
		else:
			self._PRW_substance.display_as_valid(True)

		if self._PRW_preparation.GetValue().strip() == u'':
			self._PRW_preparation.display_as_valid(False)
			validity = False
		else:
			self._PRW_preparation.display_as_valid(True)

		if self._CHBOX_approved.IsChecked():
			if self._PRW_episode.GetValue().strip() == u'':
				self._PRW_episode.display_as_valid(False)
				validity = False
			else:
				self._PRW_episode.display_as_valid(True)

		if self._CHBOX_approved.IsChecked() is True:
			self._PRW_duration.display_as_valid(True)
		else:
			if self._PRW_duration.GetValue().strip() in [u'', gmTools.u_infinity]:
				self._PRW_duration.display_as_valid(True)
			else:
				if gmDateTime.str2interval(self._PRW_duration.GetValue()) is None:
					self._PRW_duration.display_as_valid(False)
					validity = False
				else:
					self._PRW_duration.display_as_valid(True)

		if validity is False:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot save substance intake. Invalid or missing essential input.'))

		return validity
	#----------------------------------------------------------------
	def _save_as_new(self):

		emr = gmPerson.gmCurrentPatient().get_emr()

		# 1) create substance intake entry
		if self._PRW_substance.GetData() is None:
			subst = self._PRW_substance.GetValue().strip()
		else:
			# normalize, do not simply re-use name from phrasewheel
			subst = gmMedication.get_substance_by_pk(pk = self._PRW_substance.GetData())['description']

		intake = emr.add_substance_intake (
			substance = subst,
			episode = self._PRW_episode.GetData(can_create = True),
			preparation = self._PRW_preparation.GetValue()
		)

		intake['strength'] = self._PRW_strength.GetValue()
		intake['started'] = gmDateTime.wxDate2py_dt(wxDate = self._DP_started.GetValue())
		intake['schedule'] = self._PRW_schedule.GetValue()
		intake['aim'] = self._PRW_aim.GetValue()
		intake['notes'] = self._PRW_notes.GetValue()
		intake['is_long_term'] = self._CHBOX_long_term.IsChecked()
		intake['intake_is_approved_of'] = self._CHBOX_approved.IsChecked()

		if self._PRW_duration.GetValue().strip() in [u'', gmTools.u_infinity]:
			intake['duration'] = None
		else:
			intake['duration'] = gmDateTime.str2interval(self._PRW_duration.GetValue())

		# 2) create or retrieve brand
		brand = None
		pk_brand = self._PRW_brand.GetData()

		# brand pre-selected ?
		if pk_brand is None:
			# no, so ...
			desc = self._PRW_brand.GetValue().strip()
			if desc != u'':
				# ... create or get it
				brand = gmMedication.create_branded_drug (
					brand_name = desc,
					preparation = self._PRW_preparation.GetValue().strip(),
					return_existing = True
				)
				pk_brand = brand['pk']
		else:
			# yes, so get it
			brand = gmMedication.cBrandedDrug(aPK_obj = pk_brand)

		# 3) link brand, if available
		intake['pk_brand'] = pk_brand
		intake.save()

		# brand neither creatable nor pre-selected
		if brand is None:
			self.data = intake
			return True

		# 4) add substance to brand as component (because
		#    that's effectively what we are saying here)
		# FIXME: we may want to ask the user here
		# FIXME: or only do it if there are no components yet
		if self._PRW_substance.GetData() is None:
			brand.add_component(substance = self._PRW_substance.GetValue().strip())
		else:
			# normalize substance name
			subst = gmMedication.get_substance_by_pk(pk = self._PRW_substance.GetData())
			if subst is not None:
				brand.add_component(substance = subst['description'])

		self.data = intake
		return True
	#----------------------------------------------------------------
	def _save_as_update(self):

		if self._PRW_substance.GetData() is None:
			self.data['pk_substance'] = gmMedication.create_used_substance (
				substance = self._PRW_substance.GetValue().strip()
			)['pk']
		else:
			self.data['pk_substance'] = self._PRW_substance.GetData()

		self.data['started'] = gmDateTime.wxDate2py_dt(wxDate = self._DP_started.GetValue())
		self.data['preparation'] = self._PRW_preparation.GetValue()
		self.data['strength'] = self._PRW_strength.GetValue()
		self.data['schedule'] = self._PRW_schedule.GetValue()
		self.data['aim'] = self._PRW_aim.GetValue()
		self.data['notes'] = self._PRW_notes.GetValue()
		self.data['is_long_term'] = self._CHBOX_long_term.IsChecked()
		self.data['intake_is_approved_of'] = self._CHBOX_approved.IsChecked()
		self.data['pk_episode'] = self._PRW_episode.GetData(can_create = True)

		if self._PRW_duration.GetValue().strip() in [u'', gmTools.u_infinity]:
			self.data['duration'] = None
		else:
			self.data['duration'] = gmDateTime.str2interval(self._PRW_duration.GetValue())

		if self._PRW_brand.GetData() is None:
			desc = self._PRW_brand.GetValue().strip()
			if desc != u'':
				# create or get brand
				self.data['pk_brand'] = gmMedication.create_branded_drug (
					brand_name = desc,
					preparation = self._PRW_preparation.GetValue().strip(),
					return_existing = True
				)['pk']
		else:
			self.data['pk_brand'] = self._PRW_brand.GetData()

		self.data.save()
		return True
	#----------------------------------------------------------------
	def _refresh_as_new(self):
		self._PRW_substance.SetText(u'', None)
		self._PRW_strength.SetText(u'', None)
		self._PRW_preparation.SetText(u'', None)
		self._PRW_schedule.SetText(u'', None)
		self._PRW_duration.SetText(u'', None)
		self._PRW_aim.SetText(u'', None)
		self._PRW_notes.SetText(u'', None)
		self._PRW_episode.SetData(None)

		self._CHBOX_long_term.SetValue(False)
		self._CHBOX_approved.SetValue(True)

		self._DP_started.SetValue(dt = gmDateTime.py_dt2wxDate(py_dt = gmDateTime.pydt_now_here(), wx = wx))

		self._PRW_brand.SetText(u'', None)
		self._TCTRL_brand_ingredients.SetValue(u'')

		self._PRW_substance.SetFocus()
	#----------------------------------------------------------------
	def _refresh_from_existing(self):

		self._PRW_substance.SetText(self.data['substance'], self.data['pk_substance'])
		self._PRW_strength.SetText(gmTools.coalesce(self.data['strength'], u''), self.data['strength'])
		self._PRW_preparation.SetText(gmTools.coalesce(self.data['preparation'], u''), self.data['preparation'])
		if self.data['is_long_term']:
	 		self._CHBOX_long_term.SetValue(True)
			self._PRW_duration.Enable(False)
			self._PRW_duration.SetText(gmTools.u_infinity, None)
		else:
			self._CHBOX_long_term.SetValue(False)
			self._PRW_duration.Enable(True)
			if self.data['duration'] is None:
				self._PRW_duration.SetText(u'', None)
			else:
				self._PRW_duration.SetText(gmDateTime.format_interval(self.data['duration'], gmDateTime.acc_days), self.data['duration'])
		self._PRW_aim.SetText(gmTools.coalesce(self.data['aim'], u''), self.data['aim'])
		self._PRW_notes.SetText(gmTools.coalesce(self.data['notes'], u''), self.data['notes'])
		self._PRW_episode.SetData(self.data['pk_episode'])
		self._PRW_schedule.SetText(gmTools.coalesce(self.data['schedule'], u''), self.data['schedule'])

		self._CHBOX_approved.SetValue(self.data['intake_is_approved_of'])

		self._DP_started.SetValue(gmDateTime.py_dt2wxDate(py_dt = self.data['started'], wx = wx))

		self._PRW_brand.SetText(u'', None)
		self._TCTRL_brand_ingredients.SetValue(u'')
		if self.data['pk_brand'] is not None:
			brand = gmMedication.cBrandedDrug(aPK_obj = self.data['pk_brand'])
			self._PRW_brand.SetText(brand['description'], self.data['pk_brand'])
			comps = brand.components
			if comps is not None:
				comps = u' / '.join([ u'%s%s' % (c['description'], gmTools.coalesce(c['atc_code'], u'', u' (%s)')) for c in comps ])
				self._TCTRL_brand_ingredients.SetValue(comps)

		self._PRW_substance.SetFocus()
	#----------------------------------------------------------------
	def _refresh_as_new_from_existing(self):
		self._refresh_as_new()

		self._PRW_substance.SetText(u'', None)
		self._PRW_strength.SetText(u'', None)
		self._PRW_notes.SetText(u'', None)

		self._PRW_substance.SetFocus()
	#----------------------------------------------------------------
	# event handlers
	#----------------------------------------------------------------
	def _on_leave_brand(self):
		self._TCTRL_brand_ingredients.SetValue(u'')

		pk_brand = self._PRW_brand.GetData()
		if pk_brand is None:
			return

		brand = gmMedication.cBrandedDrug(aPK_obj = pk_brand)
		self._PRW_preparation.SetText(brand['preparation'], None)

		comps = brand.components
		if comps is None:
			return
		comps = u' / '.join([ u'%s%s' % (c['description'], gmTools.coalesce(c['atc_code'], u'', u' (%s)')) for c in comps ])
		self._TCTRL_brand_ingredients.SetValue(comps)
	#----------------------------------------------------------------
	def _on_get_substance_button_pressed(self, event):
		drug_db = get_drug_database()
		if drug_db is None:
			return
		result = drug_db.import_drugs()
		if result is None:
			return
		new_drugs, new_substances = result
		if len(new_substances) == 0:
			return
		# FIXME: could usefully
		# FIXME: a) ask which to post-process
		# FIXME: b) remember the others for post-processing
		first = new_substances[0]
		self._PRW_substance.SetText(first['description'], first['pk'])
	#----------------------------------------------------------------
	def _on_get_brand_button_pressed(self, event):
		drug_db = get_drug_database()
		if drug_db is None:
			return
		result = drug_db.import_drugs()
		if result is None:
			return
		new_drugs, new_substances = result
		if len(new_drugs) == 0:
			return
		# FIXME: could usefully
		# FIXME: a) ask which to post-process
		# FIXME: b) remember the others for post-processing
		first = new_drugs[0]
		self._PRW_brand.SetText(first['description'], first['pk'])
	#----------------------------------------------------------------
	def _on_chbox_long_term_checked(self, event):
		if self._CHBOX_long_term.IsChecked() is True:
			self._PRW_duration.Enable(False)
		else:
			self._PRW_duration.Enable(True)
#============================================================
def delete_substance_intake(parent=None, substance=None):
	delete_it = gmGuiHelpers.gm_show_question (
		aMessage = _(
			'Do you really want to remove this substance intake ?\n'
			'\n'
			'It may be prudent to edit the details first so as to\n'
			'leave behind some indication of why it was deleted.\n'
		),
		aTitle = _('Deleting medication / substance intake')
	)
	if not delete_it:
		return

	gmMedication.delete_substance_intake(substance = substance)
#------------------------------------------------------------
def edit_intake_of_substance(parent = None, substance=None):
	ea = cCurrentMedicationEAPnl(parent = parent, id = -1, substance = substance)
	dlg = gmEditArea.cGenericEditAreaDlg2(parent = parent, id = -1, edit_area = ea, single_entry = (substance is not None))
	dlg.SetTitle(gmTools.coalesce(substance, _('Adding substance intake'), _('Editing substance intake')))
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

	template = gmFormWidgets.manage_form_templates(parent = parent)
	option = u'form_templates.medication_list'

	if template is None:
		gmDispatcher.send(signal = 'statustext', msg = _('No medication list template configured.'), beep = True)
		return None

	dbcfg = gmCfg.cCfgSQL()
	dbcfg.set (
		workplace = gmSurgery.gmCurrentPractice().active_workplace,
		option = option,
		value = u'%s - %s' % (template['name_long'], template['external_version'])
	)

	return template
#------------------------------------------------------------
def print_medication_list(parent=None, cleanup=True):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	# 1) get template
	dbcfg = gmCfg.cCfgSQL()
	option = u'form_templates.medication_list'

	template = dbcfg.get2 (
		option = option,
		workplace = gmSurgery.gmCurrentPractice().active_workplace,
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

	# 2) process template
	meds_list = template.instantiate()
	ph = gmMacro.gmPlaceholderHandler()
	#ph.debug = True
	meds_list.substitute_placeholders(data_source = ph)
	pdf_name = meds_list.generate_output(cleanup = cleanup)
	if cleanup:
		meds_list.cleanup()
	if pdf_name is None:
		gmGuiHelpers.gm_show_error (
			aMessage = _('Error generating the medication list.'),
			aTitle = _('Printing medication list')
		)
		return False

	# 3) print template
	printed = gmPrinting.print_file_by_shellscript(filename = pdf_name, jobtype = 'medication_list')
	if not printed:
		gmGuiHelpers.gm_show_error (
			aMessage = _('Error printing the medication list.'),
			aTitle = _('Printing medication list')
		)
		return False

	pat = gmPerson.gmCurrentPatient()
	emr = pat.get_emr()
	epi = emr.add_episode(episode_name = 'administration', is_open = False)
	emr.add_clin_narrative (
		soap_cat = None,
		note = _('medication list printed from template [%s - %s]') % (template['name_long'], template['external_version']),
		episode = epi
	)

	return True
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
		self.__row_tooltips = {}
		self.__prev_row = None
		self.__prev_tooltip_row = None
		self.__prev_cell_0 = None
		self.__grouping_mode = u'episode'
		self.__filter_show_unapproved = False
		self.__filter_show_inactive = False

		self.__grouping2col_labels = {
			u'episode': [
				_('Episode'),
				_('Substance'),
				_('Dose'),
				_('Schedule'),
				_('Started'),
				_('Duration'),
				_('Brand')
			],
			u'brand': [
				_('Brand'),
				_('Schedule'),
				_('Substance'),
				_('Dose'),
				_('Started'),
				_('Duration'),
				_('Episode')
			]
		}

		self.__grouping2order_by_clauses = {
			u'episode': u'pk_health_issue nulls first, episode, substance, started',
			u'brand': u'brand nulls last, substance, started'
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
		meds = emr.get_current_substance_intake (
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
			self.SetColLabelValue(len(labels), u'OK?')
			self.SetColSize(len(labels), 40)

		self.AppendRows(numRows = len(meds))

		# loop over data
		for row_idx in range(len(meds)):
			med = meds[row_idx]
			self.__row_data[row_idx] = med

			if med['is_currently_active'] is not True:
				attr = self.GetOrCreateCellAttr(row_idx, 0)
				attr.SetTextColour('grey')
				self.SetRowAttr(row_idx, attr)

			if self.__grouping_mode == u'episode':
				if med['pk_episode'] is None:
					self.__prev_cell_0 = None
					self.SetCellValue(row_idx, 0, gmTools.u_diameter)
				else:
					if self.__prev_cell_0 != med['episode']:
						self.__prev_cell_0 = med['episode']
						self.SetCellValue(row_idx, 0, gmTools.coalesce(med['episode'], u''))

				self.SetCellValue(row_idx, 1, med['substance'])
				self.SetCellValue(row_idx, 2, gmTools.coalesce(med['strength'], u''))
				self.SetCellValue(row_idx, 3, gmTools.coalesce(med['schedule'], u''))
				self.SetCellValue(row_idx, 4, med['started'].strftime('%Y-%m-%d'))

				if med['is_long_term']:
					self.SetCellValue(row_idx, 5, gmTools.u_infinity)
				else:
					if med['duration'] is None:
						self.SetCellValue(row_idx, 5, u'')
					else:
						self.SetCellValue(row_idx, 5, gmDateTime.format_interval(med['duration'], gmDateTime.acc_days))

				if med['pk_brand'] is None:
					self.SetCellValue(row_idx, 6, gmTools.coalesce(med['brand'], u''))
				else:
					if med['fake_brand']:
						self.SetCellValue(row_idx, 6, gmTools.coalesce(med['brand'], u'', _('%s (fake)')))
					else:
						self.SetCellValue(row_idx, 6, gmTools.coalesce(med['brand'], u''))

			elif self.__grouping_mode == u'brand':

				if med['pk_brand'] is None:
					self.__prev_cell_0 = None
					self.SetCellValue(row_idx, 0, gmTools.u_diameter)
				else:
					if self.__prev_cell_0 != med['brand']:
						self.__prev_cell_0 = med['brand']
						if med['fake_brand']:
							self.SetCellValue(row_idx, 0, gmTools.coalesce(med['brand'], u'', _('%s (fake)')))
						else:
							self.SetCellValue(row_idx, 0, gmTools.coalesce(med['brand'], u''))

				self.SetCellValue(row_idx, 1, gmTools.coalesce(med['schedule'], u''))
				self.SetCellValue(row_idx, 2, med['substance'])
				self.SetCellValue(row_idx, 3, gmTools.coalesce(med['strength'], u''))
				self.SetCellValue(row_idx, 4, med['started'].strftime('%Y-%m-%d'))

				if med['is_long_term']:
					self.SetCellValue(row_idx, 5, gmTools.u_infinity)
				else:
					if med['duration'] is None:
						self.SetCellValue(row_idx, 5, u'')
					else:
						self.SetCellValue(row_idx, 5, gmDateTime.format_interval(med['duration'], gmDateTime.acc_days))

				if med['pk_episode'] is None:
					self.SetCellValue(row_idx, 6, u'')
				else:
					self.SetCellValue(row_idx, 6, gmTools.coalesce(med['episode'], u''))

			else:
				raise ValueError('unknown grouping mode [%s]' % self.__grouping_mode)

			if self.__filter_show_unapproved:
				self.SetCellValue (
					row_idx,
					len(labels),
					gmTools.bool2subst(med['intake_is_approved_of'], gmTools.u_checkmark_thin, u'', u'?')
				)

			#self.SetCellAlignment(row, col, horiz = wx.ALIGN_RIGHT, vert = wx.ALIGN_CENTRE)

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

		drug_db.show_info_on_substance(substance = self.get_selected_data()[0])
	#------------------------------------------------------------
	def check_interactions(self):

		if len(self.__row_data) == 0:
			return

		drug_db = get_drug_database()
		if drug_db is None:
			return

		if len(self.get_selected_rows()) > 1:
			drug_db.check_drug_interactions(substances = self.get_selected_data())
		else:
			drug_db.check_drug_interactions(substances = self.__row_data.values())
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
	def print_medication_list(self):
		# there could be some filtering/user interaction going on here
		_cfg = gmCfg2.gmCfgData()
		print_medication_list(parent = self, cleanup = _cfg.get(option = 'debug'))
	#------------------------------------------------------------
	def get_row_tooltip(self, row=None):

		entry = self.__row_data[row]

		tt = _('Substance intake entry (%s, %s)   [#%s]                     \n') % (
			gmTools.bool2subst(entry['is_currently_active'], _('active'), _('inactive')),
			gmTools.bool2subst(entry['intake_is_approved_of'], _('approved'), _('unapproved')),
			entry['pk_substance_intake']
		)

		tt += u' ' + _('Substance name: %s   [#%s]\n') % (entry['substance'], entry['pk_substance'])
		tt += u' ' + _('Preparation: %s\n') % entry['preparation']
		tt += gmTools.coalesce(entry['strength'], u'', _(' Amount per dose: %s\n'))
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
			entry['started'].strftime('%Y %B %d').decode(gmI18N.get_encoding()),
			duration,
			gmTools.bool2subst(entry['is_long_term'], _(' (long-term)'), _(' (short-term)'), u'')
		)

		tt += u'\n'

		tt += gmTools.coalesce(entry['aim'], u'', _(' Aim: %s\n'))
		tt += gmTools.coalesce(entry['episode'], u'', _(' Episode: %s\n'))
		tt += gmTools.coalesce(entry['notes'], u'', _(' Notes: %s\n'))

		tt += u'\n'

#		tt += _(u'Revisions: %(row_ver)s, last %(mod_when)s by %(mod_by)s.') % ({
		tt += _(u'Revisions: Last modified %(mod_when)s by %(mod_by)s.') % ({
			#'row_ver': entry['row_version'],
			'mod_when': entry['modified_when'].strftime('%c').decode(gmI18N.get_encoding()),
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
from Gnumed.wxGladeWidgets import wxgCurrentSubstancesPnl

class cCurrentSubstancesPnl(wxgCurrentSubstancesPnl.wxgCurrentSubstancesPnl, gmRegetMixin.cRegetOnPaintMixin):

	"""Panel holding a grid with current substances. Used as notebook page."""

	def __init__(self, *args, **kwargs):

		wxgCurrentSubstancesPnl.wxgCurrentSubstancesPnl.__init__(self, *args, **kwargs)
		gmRegetMixin.cRegetOnPaintMixin.__init__(self)

		self.__register_interests()
	#-----------------------------------------------------
	# reget-on-paint mixin API
	#-----------------------------------------------------
	def _populate_with_data(self):
		"""Populate cells with data from model."""
		pat = gmPerson.gmCurrentPatient()
		if pat.connected:
			self._grid_substances.patient = pat
		else:
			self._grid_substances.patient = None
		return True
	#--------------------------------------------------------
	# event handling
	#--------------------------------------------------------
	def __register_interests(self):
		gmDispatcher.connect(signal = u'pre_patient_selection', receiver = self._on_pre_patient_selection)
		gmDispatcher.connect(signal = u'post_patient_selection', receiver = self._schedule_data_reget)
		gmDispatcher.connect(signal = u'substance_intake_mod_db', receiver = self._schedule_data_reget)
		# active_substance_mod_db
		# substance_brand_mod_db
	#--------------------------------------------------------
	def _on_pre_patient_selection(self):
		wx.CallAfter(self.__on_pre_patient_selection)
	#--------------------------------------------------------
	def __on_pre_patient_selection(self):
		self._grid_substances.patient = None
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
	def _on_episode_grouping_selected(self, event):
		self._grid_substances.grouping_mode = 'episode'
	#--------------------------------------------------------
	def _on_brand_grouping_selected(self, event):
		self._grid_substances.grouping_mode = 'brand'
	#--------------------------------------------------------
	def _on_show_unapproved_checked(self, event):
		self._grid_substances.filter_show_unapproved = self._CHBOX_show_unapproved.GetValue()
	#--------------------------------------------------------
	def _on_show_inactive_checked(self, event):
		self._grid_substances.filter_show_inactive = self._CHBOX_show_inactive.GetValue()
	#--------------------------------------------------------
	def _on_print_button_pressed(self, event):
		self._grid_substances.print_medication_list()
#============================================================
# main
#------------------------------------------------------------
if __name__ == '__main__':

	from Gnumed.pycommon import gmI18N

	gmI18N.activate_locale()
	gmI18N.install_domain(domain = 'gnumed')

	#----------------------------------------
	#----------------------------------------
	if (len(sys.argv) > 1) and (sys.argv[1] == 'test'):
#		test_*()
		pass

#============================================================
# $Log: gmMedicationWidgets.py,v $
# Revision 1.29  2010-01-06 14:42:20  ncq
# - medication list printing:
# 	- tie cleanup to --debug
# 	- better error detection
#
# Revision 1.28  2010/01/01 21:48:15  ncq
# - remove confusing status message
#
# Revision 1.27  2009/12/26 19:08:38  ncq
# - document printing of medication list in EMR
#
# Revision 1.26  2009/12/25 22:07:17  ncq
# - cleanup
# - configure-medication-list-template
# - print-medication-list
# - show-info-on-entry
# - tooltips on substance entry rows
#
# Revision 1.25  2009/12/22 12:02:57  ncq
# - cleanup
#
# Revision 1.24  2009/12/03 17:51:11  ncq
# - explicit ATC col in brand component list
#
# Revision 1.23  2009/12/02 16:50:44  ncq
# - enable brand component deletion
# - normalize substance name before adding as component
#
# Revision 1.22  2009/12/01 21:55:24  ncq
# - branded drug phrasewheel
# - much improved substance intake EA implementation
#
# Revision 1.21  2009/11/30 13:15:20  ncq
# - better meds grid column ordering as per list
#
# Revision 1.20  2009/11/29 20:01:46  ncq
# - substance phrasewheel
#
# Revision 1.19  2009/11/29 16:05:41  ncq
# - must set self.data *late* in _save-as-new or else !
# - properly enable/disable duration PRW
# - grid business logic moved into grid so no need to access self._grid_substances anymore
#
# Revision 1.18  2009/11/28 18:31:30  ncq
# - implement drug brand management
# - implement drug brand component management
#
# Revision 1.17  2009/11/24 20:59:59  ncq
# - use import-drugs rather than import-drugs-as-substances
# - improved grid layout as per list
# - fix get-selected-data
# - make grid wrapper do less
#
# Revision 1.16  2009/11/19 14:44:25  ncq
# - improved plugin
#
# Revision 1.15  2009/11/15 01:09:07  ncq
# - implement grouping/filtering
# - mark unapproved vs approved if showing all substances
#
# Revision 1.14  2009/11/08 20:49:20  ncq
# - implement deletion
# - start grouping/filtering/ row tooltips
#
# Revision 1.13  2009/11/06 15:19:25  ncq
# - implement saving as new substance intake
#
# Revision 1.12  2009/10/29 17:23:24  ncq
# - consolidate get-drug-database
# - much improved substance intake EA
# - better naming and adjust to such
#
# Revision 1.11  2009/10/28 21:48:55  ncq
# - further improved substances grid
#
# Revision 1.10  2009/10/28 16:43:42  ncq
# - start implementing substances edit area
# - enhance grid to allow actual substances management
#
# Revision 1.9  2009/10/26 22:30:58  ncq
# - implement deletion of INN
#
# Revision 1.8  2009/10/21 20:41:53  ncq
# - access MMI from substance management via NEW button
#
# Revision 1.7  2009/10/21 09:21:13  ncq
# - manage substances
# - jump to drug database
#
# Revision 1.6  2009/10/20 10:27:35  ncq
# - implement configuration of drug data source
#
# Revision 1.5  2009/09/01 22:36:08  ncq
# - add jump-to-mmi
#
# Revision 1.4  2009/06/20 12:46:04  ncq
# - move IFAP handling here
#
# Revision 1.3  2009/06/10 21:02:34  ncq
# - update-atc-reference-data
#
# Revision 1.2  2009/05/13 12:20:59  ncq
# - improve and streamline
#
# Revision 1.1  2009/05/12 12:04:01  ncq
# - substance intake handling
#
#