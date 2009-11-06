"""GNUmed medication/substances handling widgets.
"""
#================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmMedicationWidgets.py,v $
# $Id: gmMedicationWidgets.py,v 1.13 2009-11-06 15:19:25 ncq Exp $
__version__ = "$Revision: 1.13 $"
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"

import logging, sys, os.path


import wx, wx.grid


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmDispatcher, gmCfg, gmShellAPI, gmTools, gmDateTime
#, gmPG2, gmMimeLib, gmExceptions, gmMatchProvider, gmHooks
from Gnumed.business import gmPerson, gmATC, gmSurgery, gmMedication
from Gnumed.wxpython import gmGuiHelpers, gmRegetMixin, gmAuthWidgets, gmCfgWidgets, gmListWidgets, gmEditArea


_log = logging.getLogger('gm.ui')
_log.info(__version__)

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

		dbcfg = gmCfg.cCfgSQL()

		drug_db = get_drug_database(parent = parent)

		if drug_db is None:
			return False

		drug_db.import_drugs_as_substances()

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
	msg = _('\nThese are the substances currently consumed across all patients.\n')

	gmListWidgets.get_choices_from_list (
		parent = parent,
		msg = msg,
		caption = _('Showing consumed substances.'),
		columns = [_('Name'), _('ATC'), u'#'],
		single_selection = True,
		refresh_callback = refresh,
		#edit_callback = edit,
		#new_callback = edit,
		delete_callback = delete,
		new_callback = new
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
		pass
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

		if self._CHBOX_approved.GetValue() is True:
			if self._PRW_episode.GetValue().strip() == u'':
				self._PRW_episode.display_as_valid(False)
				validity = False
			else:
				self._PRW_episode.display_as_valid(True)

		if self._CHBOX_approved.GetValue() is True:
			self._PRW_duration.display_as_valid(True)
		else:
			if self._PRW_duration.GetValue().strip() == u'':
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

		self.data = emr.add_substance_intake (
			substance = self._PRW_substance.GetValue().strip(),
			episode = self._PRW_episode.GetData(),
			preparation = self._PRW_preparation.GetValue()
		)
		self.data['started'] = gmDateTime.wxDate2py_dt(wxDate = self._DP_started.GetValue())
		self.data['strength'] = self._PRW_strength.GetValue()
		self.data['schedule'] = self._PRW_schedule.GetValue()
		self.data['aim'] = self._PRW_aim.GetValue()
		self.data['notes'] = self._PRW_notes.GetValue()
		self.data['is_long_term'] = self._CHBOX_long_term.GetValue()
		self.data['intake_is_approved_of'] = self._CHBOX_approved.GetValue()

		if self._PRW_duration.GetValue().strip() == u'':
			self.data['duration'] = None
		else:
			self.data['duration'] = gmDateTime.str2interval(self._PRW_duration.GetValue())

		self.data.save()

		return True
	#----------------------------------------------------------------
	def _save_as_update(self):

		self.data['started'] = gmDateTime.wxDate2py_dt(wxDate = self._DP_started.GetValue())
		self.data['preparation'] = self._PRW_preparation.GetValue()
		self.data['strength'] = self._PRW_strength.GetValue()
		self.data['schedule'] = self._PRW_schedule.GetValue()
		self.data['aim'] = self._PRW_aim.GetValue()
		self.data['notes'] = self._PRW_notes.GetValue()
		self.data['is_long_term'] = self._CHBOX_long_term.GetValue()
		self.data['intake_is_approved_of'] = self._CHBOX_approved.GetValue()
		self.data['pk_substance'] = self._PRW_substance.GetData()
		self.data['pk_episode'] = self._PRW_episode.GetData(can_create = True)

		if self._PRW_duration.GetValue().strip() == u'':
			self.data['duration'] = None
		else:
			self.data['duration'] = gmDateTime.str2interval(self._PRW_duration.GetValue())

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

		self._PRW_substance.SetFocus()
	#----------------------------------------------------------------
	def _refresh_from_existing(self):

		self._PRW_substance.SetText(self.data['substance'], self.data['pk_substance'])
		self._PRW_strength.SetText(gmTools.coalesce(self.data['strength'], u''), self.data['strength'])
		self._PRW_preparation.SetText(gmTools.coalesce(self.data['preparation'], u''), self.data['preparation'])
		if self.data['is_long_term']:
			# maybe need to disable PRW_duration
			self._CHBOX_long_term.SetValue(True)
			self._PRW_duration.SetText(gmTools.u_infinity, None)
		else:
			# maybe need to enable PRW_duration
			self._CHBOX_long_term.SetValue(False)
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

		self._PRW_substance.SetFocus()
	#----------------------------------------------------------------
	def _refresh_as_new_from_existing(self):
		self._refresh_as_new()
	#----------------------------------------------------------------
	# event handlers
	#----------------------------------------------------------------
	def _on_database_button_pressed(self, event):
		drug_db = get_drug_database()
		if drug_db is None:
			return
		new_substances = drug_db.import_drugs_as_substances()
		if new_substances is None:
			return
		if len(new_substances) == 0:
			return
		# FIXME: could usefully
		# FIXME: a) ask which
		# FIXME: b) remember the others for post-processing
		first = new_substances[0]
		self._PRW_substance.SetText(first['description'], first['pk'])
	#----------------------------------------------------------------
	def _on_chbox_long_term_checked(self, event):
		if self._CHBOX_long_term.GetValue() is True:
			self._PRW_duration.Enable(False)
		else:
			self._PRW_duration.Enable(True)
#============================================================
def delete_substance_intake(parent=None, substance=None):
	# reconfirm telling user that it may be prudent to
	# edit the details first

	# delete
	pass
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
class cCurrentSubstancesGrid(wx.grid.Grid):
	"""A grid class for displaying current substance intake.

	- does NOT listen to the currently active patient
	- thereby it can display any patient at any time
	"""
	def __init__(self, *args, **kwargs):

		wx.grid.Grid.__init__(self, *args, **kwargs)

		self.__patient = None
		self.__group_mode = 'episode'
		self.__col_labels = [
			_('Substance'),
			_('Dose'),
			_('Schedule'),
			_('Started'),
			_('Duration'),
			_('Episode'),
			_('Brand')
		]
		self.__row_data = {}
#		self.__cell_tooltips = {}
#		self.__prev_row = None
#		self.__prev_col = None

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
	#------------------------------------------------------------
	def repopulate_grid(self):

		self.empty_grid()

		if self.__patient is None:
			return

		emr = self.__patient.get_emr()
		meds = emr.get_current_substance_intake()
		if not meds:
			return

		self.AppendRows(numRows = len(meds))

		for row_idx in range(len(meds)):
			med = meds[row_idx]
			self.__row_data[row_idx] = med

			self.SetCellValue(row_idx, 0, med['substance'])
			self.SetCellValue(row_idx, 1, gmTools.coalesce(med['strength'], u''))
			self.SetCellValue(row_idx, 2, gmTools.coalesce(med['schedule'], u''))
			self.SetCellValue(row_idx, 3, med['started'].strftime('%x'))

			if med['is_long_term']:
				self.SetCellValue(row_idx, 4, gmTools.u_infinity)
			else:
				if med['duration'] is None:
					self.SetCellValue(row_idx, 4, u'')
				else:
					self.SetCellValue(row_idx, 4, gmDateTime.format_interval(med['duration'], gmDateTime.acc_days))

			if med['pk_episode'] is None:
				self.SetCellValue(row_idx, 5, u'')
			else:
				self.SetCellValue(row_idx, 5, gmTools.coalesce(med['episode'], u''))
			if med['pk_brand'] is None:
				self.SetCellValue(row_idx, 6, gmTools.coalesce(med['brand'], u''))
			else:
				if med['fake_brand']:
					self.SetCellValue(row_idx, 6, gmTools.coalesce(med['brand'], u'', _('%s (fake)')))
				else:
					self.SetCellValue(row_idx, 6, gmTools.coalesce(med['brand'], u''))

			#self.SetCellAlignment(row, col, horiz = wx.ALIGN_RIGHT, vert = wx.ALIGN_CENTRE)
	#------------------------------------------------------------
	def empty_grid(self):
		self.BeginBatch()
		self.ClearGrid()
		# Windows cannot do "nothing", it rather decides to assert()
		# on thinking it is supposed to do nothing
		if self.GetNumberRows() > 0:
			self.DeleteRows(pos = 0, numRows = self.GetNumberRows())
		self.EndBatch()
		#self.__cell_tooltips = {}
		self.__row_data = {}
	#------------------------------------------------------------
	# internal helpers
	#------------------------------------------------------------
	def __init_ui(self):
		self.CreateGrid(0, 1)
		self.EnableEditing(0)
		self.EnableDragGridSize(1)
		self.SetSelectionMode(wx.grid.Grid.wxGridSelectRows)

		# setting this screws up the labels: they are cut off and displaced
		#self.SetColLabelAlignment(wx.ALIGN_CENTER, wx.ALIGN_BOTTOM)
		self.SetColLabelAlignment(wx.ALIGN_LEFT, wx.ALIGN_CENTER)

		#self.SetRowLabelSize(wx.GRID_AUTOSIZE)		# starting with 2.8.8
		self.SetRowLabelSize(0)
		self.SetRowLabelAlignment(horiz = wx.ALIGN_RIGHT, vert = wx.ALIGN_CENTRE)

		# columns
		self.AppendCols(numCols = len(self.__col_labels) - 1)
		for col_idx in range(len(self.__col_labels)):
			self.SetColLabelValue(col_idx, self.__col_labels[col_idx])
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
	# group_mode
	#------------------------------------------------------------
	# event handling
	#------------------------------------------------------------
	def __register_events(self):
		# dynamic tooltips: GridWindow, GridRowLabelWindow, GridColLabelWindow, GridCornerLabelWindow
#		self.GetGridWindow().Bind(wx.EVT_MOTION, self.__on_mouse_over_cells)
		#self.GetGridRowLabelWindow().Bind(wx.EVT_MOTION, self.__on_mouse_over_row_labels)
		#self.GetGridColLabelWindow().Bind(wx.EVT_MOTION, self.__on_mouse_over_col_labels)

		# editing cells
		self.Bind(wx.grid.EVT_GRID_CELL_LEFT_DCLICK, self.__on_cell_left_dclicked)
	#------------------------------------------------------------
	def __on_cell_left_dclicked(self, evt):
		row = evt.GetRow()
		data = self.__row_data[row]
		edit_intake_of_substance(parent = self, substance = data)
	#------------------------------------------------------------

#============================================================
from Gnumed.wxGladeWidgets import wxgCurrentSubstancesPnl

class cCurrentSubstancesPnl(wxgCurrentSubstancesPnl.wxgCurrentSubstancesPnl, gmRegetMixin.cRegetOnPaintMixin):

	"""Panel holding a grid with current substances. Used as notebook page."""

	def __init__(self, *args, **kwargs):

		wxgCurrentSubstancesPnl.wxgCurrentSubstancesPnl.__init__(self, *args, **kwargs)
		gmRegetMixin.cRegetOnPaintMixin.__init__(self)

#		self.__init_ui()
		self.__register_interests()
	#-----------------------------------------------------
	# reget-on-paint mixin API
	#-----------------------------------------------------
	# remember to call
	#	self._schedule_data_reget()
	# whenever you learn of data changes from database listener
	# threads, dispatcher signals etc.
	def _populate_with_data(self):
		"""Populate cells with data from model."""
		pat = gmPerson.gmCurrentPatient()
		if pat.connected:
			self._grid_substances.patient = pat
		else:
			self._grid_substances.patient = None
		return True
	#-----------------------------------------------------

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
		edit_intake_of_substance(parent = self, substance = None)
	#--------------------------------------------------------
	def _on_delete_button_pressed(self, event):
		substs = self._grid_substances.get_selected_rows().get_data_from_selection()
		delete_substance_intake(parent=self, substance = 1)
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
# Revision 1.13  2009-11-06 15:19:25  ncq
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