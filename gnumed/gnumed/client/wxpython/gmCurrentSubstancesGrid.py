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
	_ = lambda x:x
else:
	try:
		_
	except NameError:
		from Gnumed.pycommon import gmI18N
		gmI18N.activate_locale()
		gmI18N.install_domain()
from Gnumed.pycommon import gmDispatcher
from Gnumed.pycommon import gmCfgDB
from Gnumed.pycommon import gmCfgINI
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmNetworkTools

from Gnumed.business import gmPraxis
from Gnumed.business import gmMedication

from Gnumed.wxpython import gmAllergyWidgets
from Gnumed.wxpython import gmSubstanceMgmtWidgets
from Gnumed.wxpython import gmSubstanceIntakeWidgets
from Gnumed.wxpython import gmMedicationWorkflows


_log = logging.getLogger('gm.ui')

_cfg = gmCfgINI.gmCfgData()

#============================================================
class cCurrentSubstancesGrid(wx.grid.Grid):
	"""A grid class for displaying current substance intake.

	- does NOT listen to the currently active patient
	- thereby it can display any patient at any time
	"""
	def __init__(self, *args, **kwargs):

		wx.grid.Grid.__init__(self, *args, **kwargs)

		self.__patient = None
		self.__row_data = {}
		self.__prev_tooltip_row = None
		self.__grouping_mode = 'issue'
		self.__filter_show_discontinued = False
		self.__sort_col_idx = 0

		self.__COL_LABELS = [
			_('Substance##tx: active ingredient'),
			_('Strength'),
			_('Schedule'),
			_('Timeframe'),
			_('Hints##tx: notes on substance intake for patient/providers/ourselves in grid view'),
			_('Problem')
		]

		self.__SORTABLE_COLS = [0, 3, 5]
		self.__sort_col_idx2order_by_clauses = {
			0: 'substance, started DESC, episode',
			3: 'started DESC, substance, episode',		# sort timeframe by "started"
			5: 'pk_health_issue NULLS FIRST, episode, substance, started DESC'
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
	def __populate_cells_by_substance(self, meds:list, emr):
		for row_idx in range(len(meds)):
			med = meds[row_idx]
			self.__row_data[row_idx] = med
			if med['discontinued']:
				attr = self.GetOrCreateCellAttr(row_idx, 0)
				attr.SetTextColour('grey')
				self.SetRowAttr(row_idx, attr)
			else:
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
			self.SetCellValue(row_idx, 0, med['substance'])
			if med['amount']:
				amount = '%s %s' % (med['amount'], med['unit'])
			else:
				amount = ''
			self.SetCellValue(row_idx, 1, amount)
			self.SetCellValue(row_idx, 2, gmTools.coalesce(med['schedule'], ''))
			self.SetCellValue(row_idx, 3, gmTools.wrap(med.medically_formatted_timerange, width = 40))
			notes_lines = []
			if med['notes4patient']:
				notes_lines.append(_('Patient: %s') % med['notes4patient'].strip())
			if med['notes4provider']:
				notes_lines.append(_('Provider: %s') % med['notes4provider'].strip())
			if med['notes4us']:
				notes_lines.append(_('Internal: %s') % med['notes4us'].strip())
			if notes_lines:
				txt = '\n'.join([ gmTools.wrap(text = nl, width = 55, subsequent_indent = '  ') for nl in notes_lines ])
				self.SetCellValue(row_idx, 4, txt)
			txt = '%s%s' % (
				med['episode'],
				gmTools.coalesce(med['health_issue'], '', ' (%s)')
			)
			self.SetCellValue(row_idx, 5, gmTools.wrap(text = txt, width = 45))
		return True

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
	def repopulate_grid(self):
		self.empty_grid()
		if self.__patient is None:
			return

		emr = self.__patient.emr
		meds = emr.get_intakes (
			#order_by = self.__grouping2order_by_clauses[self.__grouping_mode],
			order_by = self.__sort_col_idx2order_by_clauses[self.__sort_col_idx],
			include_inactive = self.__filter_show_discontinued,
			exclude_medications = False,
			exclude_potential_abuses = True
		)
		if not meds:
			return

		self.BeginBatch()
		self.AppendCols(numCols = len(self.__COL_LABELS))
		for col_idx in range(len(self.__COL_LABELS)):
			self.SetColLabelValue(col_idx, self.__COL_LABELS[col_idx])
		sort_col_label = '%s%s' % (gmTools.u_updown_arrow, self.__COL_LABELS[self.__sort_col_idx])
		self.SetColLabelValue(self.__sort_col_idx, sort_col_label)
		self.AppendRows(numRows = len(meds))
		self.__row_data = {}
		self.__populate_cells_by_substance(meds, emr)
		self.AutoSize()
		self.EndBatch()

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
		drug_db.show_info_on_substance(substance_intake = intake)

	#----------------------------------------------------------------
	def show_pregnancy_info(self):
		search_term = None
		if self.__row_data:
			sel_rows = self.get_selected_rows()
			if len(sel_rows) == 1:
				search_term = self.get_selected_data()[0]
		urls = gmMedication.generate_pregnancy_information_urls(search_term = search_term)
		gmNetworkTools.open_urls_in_browser(urls = urls)

	#----------------------------------------------------------------
	def show_pulmological_info(self):
		search_term = None
		if self.__row_data:
			sel_rows = self.get_selected_rows()
			if len(sel_rows) == 1:
				search_term = self.get_selected_data()[0]
		urls = gmMedication.generate_pulmonary_information_urls(search_term = search_term)
		gmNetworkTools.open_urls_in_browser(urls = urls)

	#----------------------------------------------------------------
	def show_cardiological_info(self):
		gmNetworkTools.open_url_in_browser(url = gmMedication.URL_long_qt)

	#----------------------------------------------------------------
	def show_nephrological_info(self):
		search_term = None
		if self.__row_data:
			sel_rows = self.get_selected_rows()
			if len(sel_rows) == 1:
				search_term = self.get_selected_data()[0]
		gmNetworkTools.open_urls_in_browser(urls = gmMedication.generate_renal_insufficiency_urls(search_term = search_term))

	#------------------------------------------------------------
	def report_ADR(self):
		url = gmCfgDB.get4user (
			option = 'external.urls.report_ADR',
			workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
			default = gmMedication.URL_drug_ADR_german_default
		)
		gmNetworkTools.open_url_in_browser(url = url)

	#------------------------------------------------------------
	def prescribe(self):
		gmMedicationWorkflows.prescribe_drugs (
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

		return
#		if len(self.get_selected_rows()) > 1:
#			drug_db.check_interactions(substance_intakes = self.get_selected_data())
#		else:
#			drug_db.check_interactions(substance_intakes = self.__row_data.values())
	#------------------------------------------------------------
	def add_substance(self):
		gmSubstanceIntakeWidgets.edit_intake_with_regimen(parent = self, intake_with_regimen = None)

	#------------------------------------------------------------
	def edit_substance(self):
		rows = self.get_selected_rows()
		if len(rows) == 0:
			return

		if len(rows) > 1:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot edit more than one substance at once.'), beep = True)
			return

		subst = self.get_selected_data()[0]
		gmSubstanceIntakeWidgets.edit_intake_with_regimen(parent = self, intake_with_regimen = subst)

	#------------------------------------------------------------
	def delete_intake(self):
		rows = self.get_selected_rows()
		if len(rows) == 0:
			return

		if len(rows) > 1:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot delete more than one substance at once.'), beep = True)
			return

		intake = self.get_selected_data()[0]
		gmSubstanceIntakeWidgets.delete_intake_with_regimen(parent = self, intake = intake)

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
		gmMedicationWorkflows.print_medication_list(parent = self)

	#------------------------------------------------------------
	def get_row_tooltip(self, row=None):
		try:
			intake_w_regimen = self.__row_data[row]
		except KeyError:
			return '?'

		emr = self.__patient.emr
		atcs = []
		if intake_w_regimen['atc_substance']:
			atcs.append(intake_w_regimen['atc_substance'])
		allg = emr.is_allergic_to(atcs = atcs, inns = [intake_w_regimen['substance']])
		tt = intake_w_regimen.format_maximum_information(allergy = allg)
		return '\n'.join(tt)

	#------------------------------------------------------------
	# internal helpers
	#------------------------------------------------------------
	def __init_ui(self):
		self.CreateGrid(0, 1)
		self.EnableEditing(0)
		self.EnableDragGridSize(1)
		self.SetSelectionMode(wx.grid.Grid.GridSelectRows)
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
		# clicking column label for sorting)
		self.Bind(wx.grid.EVT_GRID_COL_SORT, self.__on_header_clicked)

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
		gmSubstanceIntakeWidgets.edit_intake_with_regimen(parent = self, intake_with_regimen = data)

	#------------------------------------------------------------
	def __on_header_clicked(self, evt):
		if evt.Col == self.__sort_col_idx:
			return

		if evt.Col not in self.__SORTABLE_COLS:
			return

		self.__sort_col_idx = evt.Col
		self.repopulate_grid()

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
	gmI18N.install_domain('gnumed', prefer_local_catalog = True)

	from Gnumed.wxpython import gmGuiTest

	from Gnumed.pycommon import gmLog2
	gmLog2.print_logfile_name()
	#----------------------------------------
	def test_grid():
		main_frame = gmGuiTest.setup_widget_test_env(patient = 12)#-1
		the_grid = cCurrentSubstancesGrid(main_frame)
		the_grid.patient = gmGuiTest.get_patient()
		wx.GetApp().MainLoop()

	#----------------------------------------
	test_grid()
