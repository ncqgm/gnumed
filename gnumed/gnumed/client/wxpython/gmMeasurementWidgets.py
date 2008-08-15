"""GNUmed measurement widgets.
"""
#================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmMeasurementWidgets.py,v $
# $Id: gmMeasurementWidgets.py,v 1.28 2008-08-15 15:57:10 ncq Exp $
__version__ = "$Revision: 1.28 $"
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL"


import sys, logging, datetime as pyDT


import wx, wx.grid


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.business import gmPerson, gmPathLab
from Gnumed.pycommon import gmTools, gmDispatcher, gmMatchProvider, gmDateTime
from Gnumed.wxpython import gmRegetMixin, gmPhraseWheel, gmEditArea, gmGuiHelpers, gmListWidgets
from Gnumed.wxGladeWidgets import wxgMeasurementsPnl, wxgMeasurementsReviewDlg
from Gnumed.wxGladeWidgets import wxgMeasurementEditAreaPnl


_log = logging.getLogger('gm.ui')
_log.info(__version__)
#================================================================
# convenience functions
#================================================================
def edit_measurement(parent=None, measurement=None):
	ea = cMeasurementEditAreaPnl(parent = parent, id = -1)
	ea.data = measurement
	ea.mode = gmTools.coalesce(measurement, 'new', 'edit')
	dlg = gmEditArea.cGenericEditAreaDlg2(parent = parent, id = -1, edit_area = ea)
	dlg.SetTitle(gmTools.coalesce(measurement, _('Adding new measurement'), _('Editing measurement')))
	if dlg.ShowModal() == wx.ID_OK:
		return True
	return False
#================================================================
# display widgets
#================================================================
class cMeasurementsGrid(wx.grid.Grid):
	"""A grid class for displaying measurment results.

	- does NOT listen to the currently active patient
	- thereby it can display any patient at any time
	"""
	# FIXME: sort-by-battery
	# FIXME: filter-by-battery
	# FIXME: filter out empty
	# FIXME: filter by tests of a selected date
	# FIXME: dates DESC/ASC
	# FIXME: mouse over column header: display date info
	# FIXME: mouse over row header: display test info (unified, which tests are grouped, which panels they belong to
	# FIXME: improve result tooltip: panel, request details
	def __init__(self, *args, **kwargs):

		wx.grid.Grid.__init__(self, *args, **kwargs)

		self.__patient = None
		self.__cell_tooltips = {}
		self.__cell_data = {}
		self.__prev_row = None
		self.__prev_col = None
		self.__date_format = str((_('lab_grid_date_format::%Y\n%b %d')).lstrip('lab_grid_date_format::'))

		self.__init_ui()
		self.__register_events()
	#------------------------------------------------------------
	# external API
	#------------------------------------------------------------
	def delete_current_selection(self):
		if not self.IsSelection():
			gmDispatcher.send(signal = u'statustext', msg = _('No results selected for deletion.'))
			return True

		selected_cells = self.get_selected_cells()
		if len(selected_cells) > 20:
			results = None
			msg = _(
				'There are %s results marked for deletion.\n'
				'\n'
				'Are you sure you want to delete these results ?'
			) % len(selected_cells)
		else:
			results = self.__cells_to_data(cells = selected_cells, exclude_multi_cells = False)
			txt = u'\n'.join([ '%s %s (%s): %s %s%s' % (
					r['clin_when'].strftime('%Y-%m-%d %H:%M'),
					r['unified_code'],
					r['unified_name'],
					r['unified_val'],
					r['val_unit'],
					gmTools.coalesce(r['abnormality_indicator'], u'', u' (%s)')
				) for r in results
			])
			msg = _(
				'The following results are marked for deletion:\n'
				'\n'
				'%s\n'
				'\n'
				'Are you sure you want to delete these results ?'
			) % txt

		dlg = gmGuiHelpers.c2ButtonQuestionDlg (
			self,
			-1,
			caption = _('Deleting test results'),
			question = msg,
			button_defs = [
				{'label': _('Delete'), 'tooltip': _('Yes, delete all the results.'), 'default': False},
				{'label': _('Cancel'), 'tooltip': _('No, do NOT delete any results.'), 'default': True}
			]
		)
		decision = dlg.ShowModal()

		if decision == wx.ID_YES:
			if results is None:
				results = self.__cells_to_data(cells = selected_cells, exclude_multi_cells = False)
			for result in results:
				gmPathLab.delete_test_result(result)
	#------------------------------------------------------------
	def sign_current_selection(self):
		if not self.IsSelection():
			gmDispatcher.send(signal = u'statustext', msg = _('Cannot sign results. No results selected.'))
			return True

		selected_cells = self.get_selected_cells()
		if len(selected_cells) > 10:
			test_count = len(selected_cells)
			tests = None
		else:
			test_count = None
			tests = self.__cells_to_data(cells = selected_cells, exclude_multi_cells = False)

		dlg = cMeasurementsReviewDlg (
			self,
			-1,
			tests = tests,
			test_count = test_count
		)
		decision = dlg.ShowModal()

		if decision == wx.ID_APPLY:
			wx.BeginBusyCursor()

			if dlg._RBTN_confirm_abnormal.GetValue():
				abnormal = None
			elif dlg._RBTN_results_normal.GetValue():
				abnormal = False
			else:
				abnormal = True

			if dlg._RBTN_confirm_relevance.GetValue():
				relevant = None
			elif dlg._RBTN_results_not_relevant.GetValue():
				relevant = False
			else:
				relevant = True

			if tests is None:
				tests = self.__cells_to_data(cells = selected_cells, exclude_multi_cells = False)

			comment = None
			if len(tests) == 1:
				comment = dlg._TCTRL_comment.GetValue()

			for test in tests:
				test.set_review (
					technically_abnormal = abnormal,
					clinically_relevant = relevant,
					comment = comment,
					make_me_responsible = dlg._CHBOX_responsible.IsChecked()
				)

			wx.EndBusyCursor()

		dlg.Destroy()
	#------------------------------------------------------------
	def get_selected_cells(self):

		sel_block_top_left = self.GetSelectionBlockTopLeft()
		sel_block_bottom_right = self.GetSelectionBlockBottomRight()
		sel_cols = self.GetSelectedCols()
		sel_rows = self.GetSelectedRows()
		sel_cells = self.GetSelectedCells()

		selected_cells = []

		for block_idx in range(len(sel_block_top_left)):
			row_left = sel_block_bottom_right[block_idx][0] - sel_block_top_left[block_idx][0]
			row_right = sel_block_bottom_right[block_idx][0]
			col_top = sel_block_bottom_right[block_idx][1] - sel_block_top_left[block_idx][1]
			col_bottom = sel_block_bottom_right[block_idx][1]
			selected_cells.extend([ (r, c) for r in range(row_left, row_right+1) for c in range(col_top, col_bottom+1) ])

		if len(sel_rows) > 0:
			selected_cells.extend([ (r, c) for r in sel_rows for c in range(self.GetNumberCols()) ])

		if len(sel_cols) > 0:
			selected_cells.extend([ (r, c) for r in range(self.GetNumberRows()) for c in sel_cols ])

		if len(sel_cells) > 0:
			selected_cells.extend(sel_cells)

#		if not ret:
#			cell = (self.GetGridCursorRow(), self.GetGridCursorCol())
#			ret = [(cell, cell)]

		return set(selected_cells)
	#------------------------------------------------------------
	def select_cells(self, unsigned_only=False, accountables_only=False, keep_preselections=False):
		"""Select a range of cells according to criteria.

		unsigned_only: include only those which are not signed at all yet
		accountable_only: include only those for which the current user is responsible
		keep_preselections: broaden (rather than replace) the range of selected cells

		Combinations are powerful !
		"""
		wx.BeginBusyCursor()
		self.BeginBatch()

		if not keep_preselections:
			self.ClearSelection()

		for col_idx in self.__cell_data.keys():
			for row_idx in self.__cell_data[col_idx].keys():
				if unsigned_only:
					if self.__cell_data[col_idx][row_idx]['reviewed']:
						continue
				if accountables_only:
					if not self.__cell_data[col_idx][row_idx]['you_are_responsible']:
						continue
				self.SelectBlock(row_idx, col_idx, row_idx, col_idx, addToSelected = True)

		self.EndBatch()
		wx.EndBusyCursor()
	#------------------------------------------------------------
	def repopulate_grid(self):

		self.empty_grid()
		if self.__patient is None:
			return

		emr = self.__patient.get_emr()

		test_type_labels = [ u'%s (%s)' % (test[1], test[0]) for test in emr.get_test_types_for_results() ]
		if len(test_type_labels) == 0:
			return

#		test_details, td_idx = emr.get_test_types_details()
		test_date_labels = [ date[0].strftime(self.__date_format) for date in emr.get_dates_for_results() ]
		results = emr.get_test_results_by_date()

		self.BeginBatch()

		self.AppendRows(numRows = len(test_type_labels))
		self.AppendCols(numCols = len(test_date_labels) + 1)

		# column labels:
		self.SetColLabelValue(0, _("Test"))
		for date_idx in range(len(test_date_labels)):
			self.SetColLabelValue(date_idx + 1, test_date_labels[date_idx])

		# row "labels" (= cell values in column 0)
		for row_idx in range(len(test_type_labels)):
			self.SetCellValue(row_idx, 0, test_type_labels[row_idx])
			self.SetCellBackgroundColour(row_idx, 0, self.GetLabelBackgroundColour())
#			font = self.GetCellFont(row_idx, 0)
#			font.SetWeight(wx.FONTWEIGHT_BOLD)
#			self.SetCellFont(row_idx, 0, font)
#			self.__cell_tooltips[0] = {}
#			self.__cell_tooltips[0][row_idx] = _('test type tooltip row %s') % row_idx

		# cell values (list of test results)
		for result in results:
			row = test_type_labels.index(u'%s (%s)' % (result['unified_code'], result['unified_name']))
			col = test_date_labels.index(result['clin_when'].strftime(self.__date_format)) + 1

			try:
				self.__cell_data[col]
			except KeyError:
				self.__cell_data[col] = {}

			rebuild_tooltip = False
			if self.__cell_data[col].has_key(row):
				if result['clin_when'] < self.__cell_data[col][row][0]['clin_when']:
					rebuild_tooltip = True
				self.__cell_data[col][row].append(result)
				self.__cell_data[col][row].sort(key = lambda x: x['clin_when'], reverse = True)
			else:
				self.__cell_data[col][row] = [result]
				rebuild_tooltip = True

			# rebuild cell display string
			vals2display = []
			for result in self.__cell_data[col][row]:

				# is the result technically abnormal ?
				ind = gmTools.coalesce(result['abnormality_indicator'], u'').strip()
				if ind != u'':
					lab_abnormality_indicator = u' (%s)' % ind[:3]
				else:
					lab_abnormality_indicator = u''
				# - if noone reviewed - use what the lab thinks
				if result['is_technically_abnormal'] is None:
					abnormality_indicator = lab_abnormality_indicator
				# - if someone reviewed and decreed normality - use that
				elif result['is_technically_abnormal'] is False:
					abnormality_indicator = u''
				# - if someone reviewed and decreed abnormality ...
				else:
					# ... invent indicator if the lab did't use one
					if lab_abnormality_indicator == u'':
						# FIXME: calculate from min/max/range
						abnormality_indicator = u' (\u00B1)'
					# ... else use indicator the lab used
					else:
						abnormality_indicator = lab_abnormality_indicator

				# is the result relevant clinically ?
				# FIXME: take into account primary_GP once we support that
				result_relevant = result['is_clinically_relevant']
				if result_relevant is None:
					# FIXME: calculate from clinical range
					result_relevant = False

				missing_review = False
				# warn on missing review if
				# a) no review at all exists or
				if not result['reviewed']:
					missing_review = True
				# b) there is a review but
				else:
					# current user is reviewer and hasn't reviewed
					if result['you_are_responsible'] and not result['review_by_you']:
						missing_review = True

				# can we display the full result information ?
				has_result_comment = gmTools.coalesce (
					gmTools.coalesce(result['note_test_org'], result['comment']),
					u''
				).strip() != u''

				# no - display ... and truncate to 7 chars
				if (len(result['unified_val']) > 8) or (has_result_comment):
					tmp = u'%.7s%s%.6s%.2s' % (
						result['unified_val'][:7],
						gmTools.u_ellipsis,
						abnormality_indicator,
						gmTools.bool2subst(missing_review, u' ' + gmTools.u_writing_hand, u'')
					)
				# yes - display fully up to 8 chars
				else:
					tmp = u'%.8s%.6s%.2s' % (
						result['unified_val'][:8],
						abnormality_indicator,
						gmTools.bool2subst(missing_review, u' ' + gmTools.u_writing_hand, u'')
					)
				if len(self.__cell_data[col][row]) > 1:
					tmp = '%s %s' % (result['clin_when'].strftime('%H:%M'), tmp)
				vals2display.append(tmp)

			self.SetCellValue(row, col, '\n'.join(vals2display))
			self.SetCellAlignment(row, col, horiz = wx.ALIGN_RIGHT, vert = wx.ALIGN_CENTRE)
#			font = self.GetCellFont(row, col)
#			if not font.IsFixedWidth():
#				font.SetFamily(family = wx.FONTFAMILY_MODERN)
			if result_relevant:
				font = self.GetCellFont(row, col)
				self.SetCellTextColour(row, col, 'firebrick')
				font.SetWeight(wx.FONTWEIGHT_BOLD)
				self.SetCellFont(row, col, font)
#			self.SetCellFont(row, col, font)

			# tooltip
			if rebuild_tooltip:
				has_normal_min_or_max = (result['val_normal_min'] is not None) or (result['val_normal_max'] is not None)
				if has_normal_min_or_max:
					normal_min_max = u'%s - %s' % (
						gmTools.coalesce(result['val_normal_min'], u'?'),
						gmTools.coalesce(result['val_normal_max'], u'?')
					)
				else:
					normal_min_max = u''

				has_clinical_min_or_max = (result['val_target_min'] is not None) or (result['val_target_max'] is not None)
				if has_clinical_min_or_max:
					clinical_min_max = u'%s - %s' % (
						gmTools.coalesce(result['val_target_min'], u'?'),
						gmTools.coalesce(result['val_target_max'], u'?')
					)
				else:
					clinical_min_max = u''

				if result['reviewed']:
					review_status = result['last_reviewed'].strftime('%c')
				else:
					review_status = _('not yet')

				try:
					self.__cell_tooltips[col]
				except KeyError:
					self.__cell_tooltips[col] = {}
				self.__cell_tooltips[col][row] = _(
					'Measurement details of most recent result:               \n'
					' Date: %(clin_when)s\n'
					' Type: "%(name)s" (%(code)s)\n'
					' Result: %(val)s%(unit)s%(ind)s\n'
					' Standard normal range: %(norm_min_max)s%(norm_range)s  \n'
					' Reference group: %(ref_group)s\n'
					' Clinical target range: %(clin_min_max)s%(clin_range)s  \n'
					' Doc: %(comment_doc)s\n'
					' Lab: %(comment_lab)s\n'	# note_test_org
					' Episode: %(epi)s\n'
					' Issue: %(issue)s\n'
					' Material: %(material)s\n'
					' Details: %(mat_detail)s\n'
					'\n'
					'Signed (%(sig_hand)s): %(reviewed)s\n'
					' Last reviewer: %(reviewer)s\n'
					'  Technically abnormal: %(abnormal)s\n'
					'  Clinically relevant: %(relevant)s\n'
					'  Comment: %(rev_comment)s\n'
					' Responsible clinician: %(responsible_reviewer)s\n'
					'\n'
					'Test type details:\n'
					' Grouped under "%(name_unified)s" (%(code_unified)s)  \n'
					' Type comment: %(comment_type)s\n'
					' Group comment: %(comment_type_unified)s\n'
					'\n'
					'Revisions: %(row_ver)s, last %(mod_when)s by %(mod_by)s.'
				) % ({
					'clin_when': result['clin_when'].strftime('%c'),
					'code': result['code_tt'],
					'name': result['name_tt'],
					'val': result['unified_val'],
					'unit': gmTools.coalesce(result['val_unit'], u'', u' %s'),
					'ind': gmTools.coalesce(result['abnormality_indicator'], u'', u' (%s)'),
					'norm_min_max': normal_min_max,
					'norm_range': gmTools.coalesce (
						result['val_normal_range'],
						u'',
						gmTools.bool2subst (
							has_normal_min_or_max,
							u' / %s',
							u'%s'
						)
					),
					'ref_group': gmTools.coalesce(result['norm_ref_group'], u''),
					'clin_min_max': clinical_min_max,
					'clin_range': gmTools.coalesce (
						result['val_target_range'],
						u'',
						gmTools.bool2subst (
							has_clinical_min_or_max,
							u' / %s',
							u'%s'
						)
					),
					'comment_doc': u'\n Doc: '.join(gmTools.coalesce(result['comment'], u'').split('\n')),
					'comment_lab': u'\n Lab: '.join(gmTools.coalesce(result['note_test_org'], u'').split('\n')),
					'epi': result['episode'],
					'issue': gmTools.coalesce(result['health_issue'], u''),
					'material': gmTools.coalesce(result['material'], u''),
					'mat_detail': gmTools.coalesce(result['material_detail'], u''),

					'reviewed': review_status,
					'reviewer': gmTools.bool2subst(result['review_by_you'], _('you'), gmTools.coalesce(result['last_reviewer'], u'')),
					'abnormal': gmTools.bool2subst(result['is_technically_abnormal'], _('yes'), _('no'), u''),
					'relevant': gmTools.bool2subst(result['is_clinically_relevant'], _('yes'), _('no'), u''),
					'rev_comment': gmTools.coalesce(result['review_comment'], u''),
					'responsible_reviewer': gmTools.bool2subst(result['you_are_responsible'], _('you'), result['responsible_reviewer']),

					'comment_type': u'\n Type comment:'.join(gmTools.coalesce(result['comment_tt'], u'').split('\n')),
					'name_unified': gmTools.coalesce(result['name_unified'], u''),
					'code_unified': gmTools.coalesce(result['code_unified'], u''),
					'comment_type_unified': u'\n Group comment: '.join(gmTools.coalesce(result['comment_unified'], u'').split('\n')),

					'mod_when': result['modified_when'].strftime('%c'),
					'mod_by': result['modified_by'],
					'row_ver': result['row_version'],

					'sig_hand': gmTools.u_writing_hand
				})

		self.AutoSize()

		self.EndBatch()
	#------------------------------------------------------------
	def empty_grid(self):
		self.BeginBatch()
		self.ClearGrid()
		self.DeleteRows(pos = 0, numRows = self.GetNumberRows())
		self.DeleteCols(pos = 0, numCols = self.GetNumberCols())
		self.EndBatch()
		self.__cell_tooltips = {}
		self.__cell_data = {}
	#------------------------------------------------------------
	# internal helpers
	#------------------------------------------------------------
	def __init_ui(self):
		self.CreateGrid(0, 1)
		self.EnableEditing(0)
		self.EnableDragGridSize(0)
		self.SetRowLabelSize(20)
		self.SetRowLabelAlignment(horiz = wx.ALIGN_LEFT, vert = wx.ALIGN_CENTRE)
	#------------------------------------------------------------
	def __cells_to_data(self, cells=None, exclude_multi_cells=False):
		"""List of <cells> must be in row / col order."""
		data = []
		for row, col in cells:
			# weed out row labels in col 0
			if col == 0:
				continue

			try:
				# cell data is stored col / row
				data_list = self.__cell_data[col][row]
			except KeyError:
				continue

			if len(data_list) == 1:
				data.append(data_list[0])
				continue

			if exclude_multi_cells:
				gmDispatcher.send(signal = u'statustext', msg = _('Excluding multi-result field from further processing.'))
				continue

			data_to_include = self.__get_choices_from_multi_cell(cell_data = data_list)

			if data_to_include is None:
				continue

			data.extend(data_to_include)

		return data
	#------------------------------------------------------------
	def __get_choices_from_multi_cell(self, cell_data=None, single_selection=False):
		data = gmListWidgets.get_choices_from_list (
			parent = self,
			msg = _(
				'Your selection includes a field with multiple results.\n'
				'\n'
				'Please select the individual results you want to work on:'
			),
			caption = _('Selecting test results'),
			choices = [ [d['clin_when'], d['unified_code'], d['unified_name'], d['unified_val']] for d in cell_data ],
			columns = [_('Date / Time'), _('Code'), _('Test'), _('Result')],
			data = cell_data,
			single_selection = single_selection
		)
		return data
	#------------------------------------------------------------
	# event handling
	#------------------------------------------------------------
	def __register_events(self):
		# dynamic tooltips: GridWindow, GridRowLabelWindow, GridColLabelWindow, GridCornerLabelWindow
		self.GetGridWindow().Bind(wx.EVT_MOTION, self.__on_mouse_over_cells)
		#self.GetGridRowLabelWindow().Bind(wx.EVT_MOTION, self.__on_mouse_over_row_labels)

		self.Bind(wx.grid.EVT_GRID_CELL_LEFT_DCLICK, self.__on_cell_left_dclicked)
	#------------------------------------------------------------
	def __on_cell_left_dclicked(self, evt):
		col = evt.GetCol()
		row = evt.GetRow()
		if col == 0:
			# FIXME: invoke (unified) test type editor
			return

		if len(self.__cell_data[col][row]) > 1:
			data = self.__get_choices_from_multi_cell(cell_data = self.__cell_data[col][row], single_selection = True)
		else:
			data = self.__cell_data[col][row][0]

		if data is None:
			return

		edit_measurement(parent = self, measurement = data)
	#------------------------------------------------------------
	def __on_mouse_over_row_labels(self, evt):
		x, y = self.CalcUnscrolledPosition(evt.GetX(), evt.GetY())
		label_row = self.YToRow(y)
		if self.__prev_label_row == label_row:
			return
		self.__prev_label_row == label_row
		try:
			tt = self.__row_tooltips[col][row]
		except KeyError:
			tt = u''
		evt.GetEventObject().SetToolTipString(tt)
	#------------------------------------------------------------
	def __on_mouse_over_cells(self, evt):
		"""Calculate where the mouse is and set the tooltip dynamically."""
		# Use CalcUnscrolledPosition() to get the mouse position within the
		# entire grid including what's offscreen
		x, y = self.CalcUnscrolledPosition(evt.GetX(), evt.GetY())
		row, col = self.XYToCell(x, y)
		if (row == self.__prev_row) and (col == self.__prev_col):
			return
		self.__prev_row = row
		self.__prev_col = col
		try:
			tt = self.__cell_tooltips[col][row]
		except KeyError:
			tt = u''
		evt.GetEventObject().SetToolTipString(tt)
	#------------------------------------------------------------
	# properties
	#------------------------------------------------------------
	def _set_patient(self, patient):
		self.__patient = patient
		self.repopulate_grid()

	patient = property(lambda x:x, _set_patient)
#================================================================
class cMeasurementsPnl(wxgMeasurementsPnl.wxgMeasurementsPnl, gmRegetMixin.cRegetOnPaintMixin):

	"""Panel holding a grid with lab data. Used as notebook page."""

	def __init__(self, *args, **kwargs):

		wxgMeasurementsPnl.wxgMeasurementsPnl.__init__(self, *args, **kwargs)
		gmRegetMixin.cRegetOnPaintMixin.__init__(self)
		self.__init_ui()
		self.__register_interests()
	#--------------------------------------------------------
	# event handling
	#--------------------------------------------------------
	def __register_interests(self):
		gmDispatcher.connect(signal = u'pre_patient_selection', receiver = self._on_pre_patient_selection)
		gmDispatcher.connect(signal = u'post_patient_selection', receiver = self._schedule_data_reget)
		gmDispatcher.connect(signal = u'test_result_mod_db', receiver = self._schedule_data_reget)
		gmDispatcher.connect(signal = u'reviewed_test_results_mod_db', receiver = self._schedule_data_reget)
	#--------------------------------------------------------
	def _on_pre_patient_selection(self):
		wx.CallAfter(self.__on_pre_patient_selection)
	#--------------------------------------------------------
	def __on_pre_patient_selection(self):
		self.data_grid.patient = None
	#--------------------------------------------------------
	def _on_review_button_pressed(self, evt):
		self.PopupMenu(self.__action_button_popup)
	#--------------------------------------------------------
	def _on_select_button_pressed(self, evt):
		if self._RBTN_my_unsigned.GetValue() is True:
			self.data_grid.select_cells(unsigned_only = True, accountables_only = True, keep_preselections = False)
		elif self._RBTN_all_unsigned.GetValue() is True:
			self.data_grid.select_cells(unsigned_only = True, accountables_only = False, keep_preselections = False)
	#--------------------------------------------------------
	def __on_sign_current_selection(self, evt):
		self.data_grid.sign_current_selection()
	#--------------------------------------------------------
	def __on_delete_current_selection(self, evt):
		self.data_grid.delete_current_selection()
	#--------------------------------------------------------
	# internal API
	#--------------------------------------------------------
	def __init_ui(self):
		self.__action_button_popup = wx.Menu(title = _('Act on selected results'))

		menu_id = wx.NewId()
		self.__action_button_popup.AppendItem(wx.MenuItem(self.__action_button_popup, menu_id, _('Review and &sign')))
		wx.EVT_MENU(self.__action_button_popup, menu_id, self.__on_sign_current_selection)

		menu_id = wx.NewId()
		self.__action_button_popup.AppendItem(wx.MenuItem(self.__action_button_popup, menu_id, _('Export to &file')))
		#wx.EVT_MENU(self.__action_button_popup, menu_id, self.data_grid.current_selection_to_file)
		self.__action_button_popup.Enable(id = menu_id, enable = False)

		menu_id = wx.NewId()
		self.__action_button_popup.AppendItem(wx.MenuItem(self.__action_button_popup, menu_id, _('Export to &clipboard')))
		#wx.EVT_MENU(self.__action_button_popup, menu_id, self.data_grid.current_selection_to_clipboard)
		self.__action_button_popup.Enable(id = menu_id, enable = False)

		menu_id = wx.NewId()
		self.__action_button_popup.AppendItem(wx.MenuItem(self.__action_button_popup, menu_id, _('&Delete')))
		wx.EVT_MENU(self.__action_button_popup, menu_id, self.__on_delete_current_selection)
	#--------------------------------------------------------
	# reget mixin API
	#--------------------------------------------------------
	def _populate_with_data(self):
		"""Populate fields in pages with data from model."""
		pat = gmPerson.gmCurrentPatient()
		if pat.connected:
			self.data_grid.patient = pat
		else:
			self.data_grid.patient = None
		return True
#================================================================
# editing widgets
#================================================================
class cMeasurementsReviewDlg(wxgMeasurementsReviewDlg.wxgMeasurementsReviewDlg):

	def __init__(self, *args, **kwargs):

		try:
			tests = kwargs['tests']
			del kwargs['tests']
			test_count = len(tests)
			try: del kwargs['test_count']
			except KeyError: pass
		except KeyError:
			tests = None
			test_count = kwargs['test_count']
			del kwargs['test_count']

		wxgMeasurementsReviewDlg.wxgMeasurementsReviewDlg.__init__(self, *args, **kwargs)

		if tests is None:
			msg = _('%s results selected. Too many to list individually.') % test_count
		else:
			msg = ' // '.join (
				[	u'%s: %s %s (%s)' % (
						t['unified_code'],
						t['unified_val'],
						t['val_unit'],
						t['clin_when'].strftime('%Y-%m-%d')
					) for t in tests
				]
			)

		self._LBL_tests.SetLabel(msg)

		if test_count == 1:
			self._TCTRL_comment.Enable(True)
			self._TCTRL_comment.SetValue(gmTools.coalesce(tests[0]['review_comment'], u''))
			if tests[0]['you_are_responsible']:
				self._CHBOX_responsible.Enable(False)

		self.Fit()
	#--------------------------------------------------------
	# event handling
	#--------------------------------------------------------
	def _on_signoff_button_pressed(self, evt):
		if self.IsModal():
			self.EndModal(wx.ID_APPLY)
		else:
			self.Close()
#================================================================
class cMeasurementEditAreaPnl(wxgMeasurementEditAreaPnl.wxgMeasurementEditAreaPnl, gmEditArea.cGenericEditAreaMixin):
	"""This edit area saves *new* measurements into the active patient only."""

	def __init__(self, *args, **kwargs):

		try:
			self.__default_date = kwargs['date']
			del kwargs['date']
		except KeyError:
			self.__default_date = None

		wxgMeasurementEditAreaPnl.wxgMeasurementEditAreaPnl.__init__(self, *args, **kwargs)
		gmEditArea.cGenericEditAreaMixin.__init__(self)

		self.__register_interests()
	#--------------------------------------------------------
	# generic edit area mixin API
	#--------------------------------------------------------
	def _refresh_as_new(self):
		self._PRW_test.SetText(u'', None, True)
		self._TCTRL_result.SetValue(u'')
		self._PRW_units.SetText(u'', None, True)
		self._PRW_abnormality_indicator.SetText(u'', None, True)
		if self.__default_date is None:
			self._DPRW_evaluated.SetData(data = pyDT.datetime.now(tz = gmDateTime.gmCurrentLocalTimezone))
		else:
			self._DPRW_evaluated.SetData(data =	None)
		self._TCTRL_note_test_org.SetValue(u'')
		self._PRW_intended_reviewer.SetData()
		self._PRW_problem.SetData()
		self._TCTRL_narrative.SetValue(u'')
		self._CHBOX_review.SetValue(False)
		self._CHBOX_abnormal.SetValue(False)
		self._CHBOX_relevant.SetValue(False)
		self._CHBOX_abnormal.Enable(False)
		self._CHBOX_relevant.Enable(False)
		self._TCTRL_review_comment.SetValue(u'')
		self._TCTRL_normal_min.SetValue(u'')
		self._TCTRL_normal_max.SetValue(u'')
		self._TCTRL_normal_range.SetValue(u'')
		self._TCTRL_target_min.SetValue(u'')
		self._TCTRL_target_max.SetValue(u'')
		self._TCTRL_target_range.SetValue(u'')
		self._TCTRL_norm_ref_group.SetValue(u'')

		self._PRW_test.SetFocus()
	#--------------------------------------------------------
	def _refresh_from_existing(self):
		self._PRW_test.SetData(data = self.data['pk_test_type'])
		self._TCTRL_result.SetValue(self.data['unified_val'])
		self._PRW_units.SetText(self.data['val_unit'], self.data['val_unit'], True)
		self._PRW_abnormality_indicator.SetText (
			gmTools.coalesce(self.data['abnormality_indicator'], u''),
			gmTools.coalesce(self.data['abnormality_indicator'], u''),
			True
		)
		self._DPRW_evaluated.SetData(data = self.data['clin_when'])
		self._TCTRL_note_test_org.SetValue(gmTools.coalesce(self.data['note_test_org'], u''))
		self._PRW_intended_reviewer.SetData(self.data['pk_intended_reviewer'])
		self._PRW_problem.SetData(self.data['pk_episode'])
		self._TCTRL_narrative.SetValue(gmTools.coalesce(self.data['comment'], u''))
		self._CHBOX_review.SetValue(False)
		self._CHBOX_abnormal.SetValue(gmTools.coalesce(self.data['is_technically_abnormal'], False))
		self._CHBOX_relevant.SetValue(gmTools.coalesce(self.data['is_clinically_relevant'], False))
		self._CHBOX_abnormal.Enable(False)
		self._CHBOX_relevant.Enable(False)
		self._TCTRL_review_comment.SetValue(gmTools.coalesce(self.data['review_comment'], u''))
		self._TCTRL_normal_min.SetValue(gmTools.coalesce(self.data['val_normal_min'], u''))
		self._TCTRL_normal_max.SetValue(gmTools.coalesce(self.data['val_normal_max'], u''))
		self._TCTRL_normal_range.SetValue(gmTools.coalesce(self.data['val_normal_range'], u''))
		self._TCTRL_target_min.SetValue(gmTools.coalesce(self.data['val_target_min'], u''))
		self._TCTRL_target_max.SetValue(gmTools.coalesce(self.data['val_target_max'], u''))
		self._TCTRL_target_range.SetValue(gmTools.coalesce(self.data['val_target_range'], u''))
		self._TCTRL_norm_ref_group.SetValue(gmTools.coalesce(self.data['norm_ref_group'], u''))

		self._TCTRL_result.SetFocus()
	#--------------------------------------------------------
	def _refresh_as_new_from_existing(self):
		self._refresh_from_existing()

		self._TCTRL_result.SetValue(u'')
		self._PRW_abnormality_indicator.SetText(u'', None, True)
		self._TCTRL_note_test_org.SetValue(u'')
		self._TCTRL_narrative.SetValue(u'')
		self._CHBOX_review.SetValue(False)
		self._CHBOX_abnormal.SetValue(False)
		self._CHBOX_relevant.SetValue(False)
		self._CHBOX_abnormal.Enable(False)
		self._CHBOX_relevant.Enable(False)
		self._TCTRL_review_comment.SetValue(u'')

		self._TCTRL_result.SetFocus()
	#--------------------------------------------------------
	def _valid_for_save(self):

		validity = True

		if not self._DPRW_evaluated.is_valid_timestamp():
			self._DPRW_evaluated.display_as_valid(False)
			validity = False
		else:
			self._DPRW_evaluated.display_as_valid(True)

		if self._TCTRL_result.GetValue().strip() == u'':
			self._TCTRL_result.SetBackgroundColour(gmPhraseWheel.color_prw_invalid)
			validity = False
		else:
			self._TCTRL_result.SetBackgroundColour(gmPhraseWheel.color_prw_valid)

		if self._PRW_problem.GetValue().strip() == u'':
			self._PRW_problem.display_as_valid(False)
		else:
			self._PRW_problem.display_as_valid(True)

		if self._PRW_test.GetValue().strip() == u'':
			self._PRW_test.display_as_valid(False)
			validity = False
		else:
			self._PRW_test.display_as_valid(True)

		if self._PRW_intended_reviewer.GetData() is None:
			self._PRW_intended_reviewer.display_as_valid(False)
			validity = False
		else:
			self._PRW_intended_reviewer.display_as_valid(True)

		if self._PRW_units.GetValue().strip() == u'':
			self._PRW_units.display_as_valid(False)
			validity = False
		else:
			self._PRW_units.display_as_valid(True)

		ctrls = [self._TCTRL_normal_min, self._TCTRL_normal_max, self._TCTRL_target_min, self._TCTRL_target_max]
		for widget in ctrls:
			val = widget.GetValue().strip()
			if val == u'':
				continue
			try:
				int(val)
				widget.SetBackgroundColour(gmPhraseWheel.color_prw_valid)
			except:
				widget.SetBackgroundColour(gmPhraseWheel.color_prw_invalid)
				validity = False

		if validity is False:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot save result. Missing essential input.'))

		return validity
	#--------------------------------------------------------
	def _save_as_new(self):

		emr = gmPerson.gmCurrentPatient().get_emr()

		try:
			v_num = int(self._TCTRL_result.GetValue().strip())
			v_al = None
		except:
			v_num = None
			v_al = self._TCTRL_result.GetValue().strip()

		pk_type = self._PRW_test.GetData()
		if pk_type is None:
			tt = gmPathLab.create_test_type (
				lab = None,
				code = self._PRW_test.GetValue().strip(),
				unit = gmTools.none_if(self._PRW_units.GetValue().strip(), u''),
				name = self._PRW_test.GetValue().strip()
			)
			pk_type = tt['pk']

		tr = emr.add_test_result (
			episode = self._PRW_problem.GetData(can_create=True, is_open=False),
			type = pk_type,
			intended_reviewer = self._PRW_intended_reviewer.GetData(),
			val_num = v_num,
			val_alpha = v_al,
			unit = self._PRW_units.GetValue()
		)

		tr['clin_when'] = self._DPRW_evaluated.GetData().get_pydt()

		ctrls = [
			('abnormality_indicator', self._PRW_abnormality_indicator),
			('note_test_org', self._TCTRL_note_test_org),
			('comment', self._TCTRL_narrative),
			('val_normal_min', self._TCTRL_normal_min),
			('val_normal_max', self._TCTRL_normal_max),
			('val_normal_range', self._TCTRL_normal_range),
			('val_target_min', self._TCTRL_target_min),
			('val_target_max', self._TCTRL_target_max),
			('val_target_range', self._TCTRL_target_range),
			('norm_ref_group', self._TCTRL_norm_ref_group)
		]
		for field, widget in ctrls:
			val = widget.GetValue().strip()
			if val != u'':
				tr[field] = val

		tr.save_payload()

		if self._CHBOX_review.GetValue() is True:
			tr.set_review (
				technically_abnormal = self._CHBOX_abnormal.GetValue(),
				clinically_relevant = self._CHBOX_relevant.GetValue(),
				comment = gmTools.none_if(self._TCTRL_review_comment.GetValue().strip(), u''),
				make_me_responsible = False
			)

		self.data = tr

		return True
	#--------------------------------------------------------
	def _save_as_update(self):

		try:
			v_num = int(self._TCTRL_result.GetValue().strip())
			v_al = None
		except:
			v_num = None
			v_al = self._TCTRL_result.GetValue().strip()

		pk_type = self._PRW_test.GetData()
		if pk_type is None:
			tt = gmPathLab.create_test_type (
				lab = None,
				code = self._PRW_test.GetValue().strip(),
				unit = gmTools.none_if(self._PRW_units.GetValue().strip(), u''),
				name = self._PRW_test.GetValue().strip()
			)
			pk_type = tt['pk']

		tr = self.data

		tr['pk_episode'] = self._PRW_problem.GetData(can_create=True, is_open=False)
		tr['pk_test_type'] = pk_type
		tr['pk_intended_reviewer'] = self._PRW_intended_reviewer.GetData()
		tr['val_num'] = v_num
		tr['val_alpha'] = v_al
		tr['val_unit'] = self._PRW_units.GetValue()
		tr['clin_when'] = self._DPRW_evaluated.GetData().get_pydt()

		ctrls = [
			('abnormality_indicator', self._PRW_abnormality_indicator),
			('note_test_org', self._TCTRL_note_test_org),
			('comment', self._TCTRL_narrative),
			('val_normal_min', self._TCTRL_normal_min),
			('val_normal_max', self._TCTRL_normal_max),
			('val_normal_range', self._TCTRL_normal_range),
			('val_target_min', self._TCTRL_target_min),
			('val_target_max', self._TCTRL_target_max),
			('val_target_range', self._TCTRL_target_range),
			('norm_ref_group', self._TCTRL_norm_ref_group)
		]
		for field, widget in ctrls:
			val = widget.GetValue().strip()
			if val != u'':
				tr[field] = val

		tr.save_payload()

		if self._CHBOX_review.GetValue() is True:
			tr.set_review (
				technically_abnormal = self._CHBOX_abnormal.GetValue(),
				clinically_relevant = self._CHBOX_relevant.GetValue(),
				comment = gmTools.none_if(self._TCTRL_review_comment.GetValue().strip(), u''),
				make_me_responsible = False
			)

		return True
	#--------------------------------------------------------
	# event handling
	#--------------------------------------------------------
	def __register_interests(self):
		self._PRW_test.add_callback_on_lose_focus(self._on_leave_test_prw)
		self._PRW_abnormality_indicator.add_callback_on_lose_focus(self._on_leave_indicator_prw)
	#--------------------------------------------------------
	def _on_leave_test_prw(self):
		pk_type = self._PRW_test.GetData()
		# units context
		if pk_type is None:
			self._PRW_units.unset_context(context = u'pk_type')
		else:
			self._PRW_units.set_context(context = u'pk_type', val = pk_type)
	#--------------------------------------------------------
	def _on_leave_indicator_prw(self):
		# if the user hasn't explicitely enabled reviewing
		if not self._CHBOX_review.GetValue():
			self._CHBOX_abnormal.SetValue(self._PRW_abnormality_indicator.GetValue().strip() != u'')
	#--------------------------------------------------------
	def _on_review_box_checked(self, evt):
		self._CHBOX_abnormal.Enable(self._CHBOX_review.GetValue())
		self._CHBOX_relevant.Enable(self._CHBOX_review.GetValue())
		self._TCTRL_review_comment.Enable(self._CHBOX_review.GetValue())
#================================================================
# convenience widgets
#================================================================
class cMeasurementTypePhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):

		query = u"""
	(
select
	pk_test_type,
	name_tt
		|| ' ('
		|| coalesce (
			(select internal_name from clin.test_org cto where cto.pk = vcutt.pk_test_org),
			'%(in_house)s'
			)
		|| ')'
	as name
from clin.v_unified_test_types vcutt
where
	name_unified %%(fragment_condition)s

) union (

select
	pk_test_type,
	name_tt
		|| ' ('
		|| coalesce (
			(select internal_name from clin.test_org cto where cto.pk = vcutt.pk_test_org),
			'%(in_house)s'
			)
		|| ')'
	as name
from clin.v_unified_test_types vcutt
where
	name_tt %%(fragment_condition)s

) union (

select
	pk_test_type,
	name_tt
		|| ' ('
		|| coalesce (
			(select internal_name from clin.test_org cto where cto.pk = vcutt.pk_test_org),
			'%(in_house)s'
			)
		|| ')'
	as name
from clin.v_unified_test_types vcutt
where
	code_unified %%(fragment_condition)s

) union (

select
	pk_test_type,
	name_tt
		|| ' ('
		|| coalesce (
			(select internal_name from clin.test_org cto where cto.pk = vcutt.pk_test_org),
			'%(in_house)s'
			)
		|| ')'
	as name
from clin.v_unified_test_types vcutt
where
	code_tt %%(fragment_condition)s
)

order by name
limit 50""" % {'in_house': _('in house lab')}

		mp = gmMatchProvider.cMatchProvider_SQL2(queries=query)
		mp.setThresholds(1, 2, 4)
		gmPhraseWheel.cPhraseWheel.__init__ (
			self,
			*args,
			**kwargs
		)
		self.matcher = mp
		self.SetToolTipString(_('Select the type of measurement.'))
		self.selection_only = False
#================================================================
class cUnitPhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):

		query = u"""
select distinct val_unit,
	val_unit, val_unit
from clin.v_test_results
where
	(
		val_unit %(fragment_condition)s
			or
		conversion_unit %(fragment_condition)s
	)
	%(ctxt_test_name)s
	%(ctxt_test_pk)s
order by val_unit
limit 25"""

		ctxt = {
			'ctxt_test_name': {
				'where_part': u'and %(test)s in (name_tt, name_unified, code_tt, code_unified)',
				'placeholder': u'test'
			},
			'ctxt_test_pk': {
				'where_part': u'and pk_test_type = %(pk_type)s',
				'placeholder': u'pk_type'
			}
		}

		mp = gmMatchProvider.cMatchProvider_SQL2(queries=query, context=ctxt)
		mp.setThresholds(1, 2, 4)
		gmPhraseWheel.cPhraseWheel.__init__ (
			self,
			*args,
			**kwargs
		)
		self.matcher = mp
		self.SetToolTipString(_('Select the unit of the test result.'))
		self.selection_only = False

#================================================================

#================================================================
class cTestResultIndicatorPhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):

		query = u"""
select distinct abnormality_indicator,
	abnormality_indicator, abnormality_indicator
from clin.v_test_results
where
	abnormality_indicator %(fragment_condition)s
order by abnormality_indicator
limit 25"""

		mp = gmMatchProvider.cMatchProvider_SQL2(queries=query)
		mp.setThresholds(1, 1, 2)
		mp.ignored_chars = "[.'\\\[\]#$%_]+" + '"'
		mp.word_separators = '[ \t&:]+'
		gmPhraseWheel.cPhraseWheel.__init__ (
			self,
			*args,
			**kwargs
		)
		self.matcher = mp
		self.SetToolTipString(_('Select an indicator for the level of abnormality.'))
		self.selection_only = False
#================================================================
# main
#----------------------------------------------------------------
if __name__ == '__main__':

	from Gnumed.pycommon import gmLog2, gmI18N

	gmI18N.activate_locale()
	gmI18N.install_domain()
	gmDateTime.init()

	#------------------------------------------------------------
	def test_grid():
		pat = gmPerson.ask_for_patient()
		app = wx.PyWidgetTester(size = (500, 300))
		lab_grid = cMeasurementsGrid(parent = app.frame, id = -1)
		lab_grid.patient = pat
		app.frame.Show()
		app.MainLoop()
	#------------------------------------------------------------
	def test_test_ea_pnl():
		pat = gmPerson.ask_for_patient()
		gmPerson.set_active_patient(patient=pat)
		app = wx.PyWidgetTester(size = (500, 300))
		ea = cMeasurementEditAreaPnl(parent = app.frame, id = -1)
		app.frame.Show()
		app.MainLoop()
	#------------------------------------------------------------
	if (len(sys.argv) > 1) and (sys.argv[1] == 'test'):
		#test_grid()
		test_test_ea_pnl()

#================================================================
# $Log: gmMeasurementWidgets.py,v $
# Revision 1.28  2008-08-15 15:57:10  ncq
# - indicate data revisions in tooltip
#
# Revision 1.27  2008/08/08 13:31:58  ncq
# - better results layout
#
# Revision 1.26  2008/08/05 16:21:30  ncq
# - support multiple values per cell
#
# Revision 1.25  2008/07/17 21:41:36  ncq
# - cleanup
#
# Revision 1.24  2008/07/14 13:47:36  ncq
# - explicitely set focus after refresh per user request
#
# Revision 1.23  2008/07/13 16:13:33  ncq
# - add_new_measurement -> edit_measurement
# - use cGenericEditAreaMixin on results edit area
# - invoked results edit area via double-click on result in grid
#
# Revision 1.22  2008/07/07 13:43:17  ncq
# - current patient .connected
#
# Revision 1.21  2008/06/24 14:00:09  ncq
# - action button popup menu
# - handle result deletion
#
# Revision 1.20  2008/06/23 21:50:26  ncq
# - create test types on the fly
#
# Revision 1.19  2008/06/22 17:32:39  ncq
# - implement refresh on measurement ea so "Next" will work in dialog
#
# Revision 1.18  2008/06/19 15:26:09  ncq
# - finish saving test result from edit area
# - fix a few oversights in the result tooltip
#
# Revision 1.17  2008/06/18 15:49:22  ncq
# - improve save validity check on edit area
#
# Revision 1.16  2008/06/16 15:03:20  ncq
# - first cut at saving test results
#
# Revision 1.15  2008/06/15 20:43:31  ncq
# - add test result indicator phrasewheel
#
# Revision 1.14  2008/06/09 15:36:04  ncq
# - reordered for clarity
# - add_new_measurement
# - edit area start
# - phrasewheels
#
# Revision 1.13  2008/05/14 15:01:43  ncq
# - remove spurious evt argument in _on_pre_patient_selection()
#
# Revision 1.12  2008/04/26 21:40:58  ncq
# - eventually support selecting certain ranges of cells
#
# Revision 1.11  2008/04/26 10:05:32  ncq
# - in review dialog when user is already responsible
#   disable make_me_responsible checkbox
#
# Revision 1.10  2008/04/22 21:18:49  ncq
# - implement signing
# - improved tooltip
# - properly clear grid when active patient changes
#
# Revision 1.9  2008/04/16 20:39:39  ncq
# - working versions of the wxGlade code and use it, too
# - show client version in login dialog
#
# Revision 1.8  2008/04/11 23:12:23  ncq
# - improve docs
#
# Revision 1.7  2008/04/04 13:09:45  ncq
# - use +/- as abnormality indicator where not available
# - more complete calculation of "more result data available"
#
# Revision 1.6  2008/04/02 10:48:33  ncq
# - cleanup, review -> sign
# - support test_count in review widget
# - better results formatting as per list discussion
#
# Revision 1.5  2008/03/29 16:19:57  ncq
# - review_current_selection()
# - get_selected_cells()
# - bold test names
# - display abnormality indicator and clinical relevance
# - improve tooltip
# - cMeasurementsReviewDialog()
# - listen to test result database changes
#
# Revision 1.4  2008/03/25 19:36:30  ncq
# - fix imports
# - better docs
# - str() wants non-u''
# - cMeasurementsPnl()
#
# Revision 1.3  2008/03/20 15:31:40  ncq
# - improve cell tooltips with review status and issue/episode information
# - start row labels tooltips
#
# Revision 1.2  2008/03/17 14:55:41  ncq
# - add lots of TODOs
# - better layout
# - set grid cell tooltips
#
# Revision 1.1  2008/03/16 11:57:47  ncq
# - first iteration
#
#
