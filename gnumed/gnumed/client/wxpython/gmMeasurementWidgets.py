"""GNUmed measurement widgets.
"""
#================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmMeasurementWidgets.py,v $
# $Id: gmMeasurementWidgets.py,v 1.9 2008-04-16 20:39:39 ncq Exp $
__version__ = "$Revision: 1.9 $"
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL"


import sys, logging


import wx, wx.grid


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.business import gmPerson
from Gnumed.pycommon import gmTools, gmDispatcher
from Gnumed.wxpython import gmRegetMixin
from Gnumed.wxGladeWidgets import wxgMeasurementsPnl, wxgMeasurementsReviewDlg


_log = logging.getLogger('gm.ui')
_log.info(__version__)
#================================================================
class cMeasurementsGrid(wx.grid.Grid):
	"""A grid class for displaying measurment results.

	- does NOT listen to the currently active patient
	- thereby it can display any patient at any time
	"""
	# FIXME: sort-by-panels
	# FIXME: filter-by-panels
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
			tests = [ self.__cell_data[c[1]][c[0]] for c in selected_cells if c[1] != 0 ]

		dlg = cMeasurementsReviewDlg (
			self,
#			wx.GetTopLevelParent(self),
			-1,
			tests = tests,
			test_count = test_count
		)
		dlg.ShowModal()
		dlg.Destroy()
	#------------------------------------------------------------
	def get_selected_cells(self):

		sel_block_top_left = self.GetSelectionBlockTopLeft()
		sel_block_bottom_right = self.GetSelectionBlockBottomRight()
		sel_cols = self.GetSelectedCols()
		sel_rows = self.GetSelectedRows()
		sel_cells = self.GetSelectedCells()

		selected_cells = []

		if (len(sel_block_top_left) > 1) and (len(sel_block_bottom_right) > 0):
			rl = sel_block_bottom_right[0] - sel_block_top_left[0]
			rr = sel_block_bottom_right[0]
			ct = sel_block_bottom_right[1] - sel_block_top_left[1]
			cb = sel_block_bottom_right[1]
			selected_cells.extend([ (r, c) for r in range(rl, rr+1) for c in range(ct, cb+1) ])

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
	def repopulate_grid(self):

		self.empty_grid()
		if self.__patient is None:
			return

		emr = self.__patient.get_emr()
		tests = [ u'%s (%s)' % (test[1], test[0]) for test in emr.get_test_types_for_results() ]
		if len(tests) == 0:
			return
		test_details, td_idx = emr.get_test_types_details()
		dates = [ date[0].strftime(self.__date_format) for date in emr.get_dates_for_results() ]
		results, idx = emr.get_measurements_by_date()

		self.BeginBatch()

		# row labels in column 0 (test names)
		self.AppendRows(numRows = len(tests))
		for row_idx in range(len(tests)):
			self.SetCellValue(row_idx, 0, tests[row_idx])
			self.SetCellBackgroundColour(row_idx, 0, self.GetLabelBackgroundColour())
#			font = self.GetCellFont(row_idx, 0)
#			font.SetWeight(wx.FONTWEIGHT_BOLD)
#			self.SetCellFont(row_idx, 0, font)
#			self.__cell_tooltips[0] = {}
#			self.__cell_tooltips[0][row_idx] = _('test type tooltip row %s') % row_idx

		# column labels (test dates)
		self.AppendCols(numCols = len(dates))
		for date_idx in range(len(dates)):
			self.SetColLabelValue(date_idx + 1, dates[date_idx])

		# cell values (test results)
		for result in results:
			row = tests.index(u'%s (%s)' % (result[idx['unified_code']], result[idx['unified_name']]))
			col = dates.index(result[idx['clin_when']].strftime(self.__date_format)) + 1

			try:
				self.__cell_data[col]
			except KeyError:
				self.__cell_data[col] = {}
			self.__cell_data[col][row] = result

			# is the result technically abnormal ?
			ind = result['abnormality_indicator']
			if (ind is not None) and (ind.strip() != u''):
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
				# FIXME: take into account other review if there's only one
				# FIMXE: take into account most recent review if there's more than one
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
				val2display = u'%7.7s\u2026%6.6s%1.1s' % (
					result[idx['unified_val']][:7],
					abnormality_indicator,
					gmTools.bool2subst(missing_review, u'\u270D', u'')
				)
			# yes - display fully up to 8 chars
			else:
				val2display = u'%8.8s%6.6s%1.1s' % (
					result[idx['unified_val']][:8],
					abnormality_indicator,
					gmTools.bool2subst(missing_review, u'\u270D', u'')
				)

			self.SetCellValue(row, col, val2display)
			self.SetCellAlignment(row, col, horiz = wx.ALIGN_RIGHT, vert = wx.ALIGN_CENTRE)
#			font = self.GetCellFont(row, col)
#			if not font.IsFixedWidth():
#			font.SetFamily(family = wx.FONTFAMILY_MODERN)
			if result_relevant:
				font = self.GetCellFont(row, col)
				self.SetCellTextColour(row, col, 'firebrick')
				font.SetWeight(wx.FONTWEIGHT_BOLD)
				self.SetCellFont(row, col, font)
#			self.SetCellFont(row, col, font)

			try:
				self.__cell_tooltips[col]
			except KeyError:
				self.__cell_tooltips[col] = {}
			self.__cell_tooltips[col][row] = _(
				'Measurement details:                                     \n'
				' Date: %(clin_when)s\n'
				' Type: "%(name)s" (%(code)s)\n'
				' Result: %(val)s%(unit)s%(ind)s\n'
				' Standard normal range: %(norm_min)s - %(norm_max)s%(norm_range)s  \n'
				' Reference group: %(ref_group)s\n'
				' Clinical target range: %(clin_min)s - %(clin_max)s%(clin_range)s  \n'
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
				'Last modified %(mod_when)s by %(mod_by)s.'
			) % ({
				'clin_when': result[idx['clin_when']].strftime('%c'),
				'code': result[idx['code_tt']],
				'name': result[idx['name_tt']],
				'val': result[idx['unified_val']],
				'unit': gmTools.coalesce(result[idx['val_unit']], u'', u' %s'),
				'ind': gmTools.coalesce(result[idx['abnormality_indicator']], u'', u' (%s)'),
				'norm_min': gmTools.coalesce(result[idx['val_normal_min']], u'?'),
				'norm_max': gmTools.coalesce(result[idx['val_normal_max']], u'?'),
				'norm_range': gmTools.coalesce(result[idx['val_normal_range']], u'', u' / %s'),
				'ref_group': gmTools.coalesce(result[idx['norm_ref_group']], u''),
				'clin_min': gmTools.coalesce(result[idx['val_target_min']], u'?'),
				'clin_max': gmTools.coalesce(result[idx['val_target_max']], u'?'),
				'clin_range': gmTools.coalesce(result[idx['val_target_range']], u'', u' / %s'),
				'comment_doc': u'\n Doc: '.join(gmTools.coalesce(result[idx['comment']], u'').split('\n')),
				'comment_lab': u'\n Lab: '.join(gmTools.coalesce(result[idx['comment']], u'').split('\n')),
				'epi': result[idx['episode']],
				'issue': gmTools.coalesce(result[idx['health_issue']], u''),
				'material': gmTools.coalesce(result[idx['material']], u''),
				'mat_detail': gmTools.coalesce(result[idx['material_detail']], u''),

				'reviewed': gmTools.bool2str(result[idx['reviewed']], result[idx['last_reviewed']], _('not yet')),
				'reviewer': gmTools.bool2subst(result[idx['review_by_you']], _('you'), gmTools.coalesce(result[idx['last_reviewer']], u'')),
				'abnormal': gmTools.coalesce(result[idx['is_technically_abnormal']], u''),
				'relevant': gmTools.coalesce(result[idx['is_clinically_relevant']], u''),
				'rev_comment': gmTools.coalesce(result[idx['review_comment']], u''),
				'responsible_reviewer': gmTools.bool2subst(result[idx['you_are_responsible']], _('you'), result[idx['responsible_reviewer']]),

				'comment_type': u'\n Type comment:'.join(gmTools.coalesce(result[idx['comment_tt']], u'').split('\n')),
				'name_unified': result[idx['name_unified']],
				'code_unified': result[idx['code_unified']],
				'comment_type_unified': u'\n Group comment: '.join(gmTools.coalesce(result[idx['comment_unified']], u'').split('\n')),

				'mod_when': result[idx['modified_when']].strftime('%c'),
				'mod_by': result[idx['modified_by']],

				'sig_hand': u'\u270D'
			})

		self.AutoSize()

		self.EndBatch()
	#------------------------------------------------------------
	def empty_grid(self):
		self.BeginBatch()
		self.DeleteCols(pos = 2, numCols = (self.GetNumberCols() - 2))
		self.EndBatch()
	#------------------------------------------------------------
	# internal helpers
	#------------------------------------------------------------
	def __init_ui(self):
		self.CreateGrid(0, 1)
		self.EnableEditing(0)
		self.EnableDragGridSize(0)
		self.SetColLabelValue(0, _("Test"))
		self.SetRowLabelSize(20)
		self.SetRowLabelAlignment(horiz = wx.ALIGN_LEFT, vert = wx.ALIGN_CENTRE)
		# set background/font/... on test type pseudo-column
	#------------------------------------------------------------
	# event handling
	#------------------------------------------------------------
	def __register_events(self):
		# GridWindow, GridRowLabelWindow, GridColLabelWindow, GridCornerLabelWindow
		self.GetGridWindow().Bind(wx.EVT_MOTION, self.__on_mouse_over_cells)
		#self.GetGridRowLabelWindow().Bind(wx.EVT_MOTION, self.__on_mouse_over_row_labels)
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
class cMeasurementsReviewDlg(wxgMeasurementsReviewDlg.wxgMeasurementsReviewDlg):

	def __init__(self, *args, **kwargs):

		try:
			tests = kwargs['tests']
			del kwargs['tests']
			test_count = len(tests)
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

		self.Fit()
	#--------------------------------------------------------
	# event handling
	#--------------------------------------------------------
	def _on_signoff_button_pressed(self, evt):
		print "signing off"
#================================================================
class cMeasurementsPnl(wxgMeasurementsPnl.wxgMeasurementsPnl, gmRegetMixin.cRegetOnPaintMixin):

	def __init__(self, *args, **kwargs):

		wxgMeasurementsPnl.wxgMeasurementsPnl.__init__(self, *args, **kwargs)
		gmRegetMixin.cRegetOnPaintMixin.__init__(self)
		self.__register_interests()
	#--------------------------------------------------------
	# event handling
	#--------------------------------------------------------
	def __register_interests(self):
		gmDispatcher.connect(signal = u'pre_patient_selection', receiver = self._schedule_data_reget)
		gmDispatcher.connect(signal = u'post_patient_selection', receiver = self._schedule_data_reget)
		gmDispatcher.connect(signal = u'test_result_mod_db', receiver = self._schedule_data_reget)
		# FIXME: listen for review changes, too
	#--------------------------------------------------------
	def _on_review_button_pressed(self, evt):
		self.data_grid.sign_current_selection()
	#--------------------------------------------------------
	# reget mixin API
	#--------------------------------------------------------
	def _populate_with_data(self):
		"""Populate fields in pages with data from model."""
		pat = gmPerson.gmCurrentPatient()
		if pat.is_connected():
			self.data_grid.patient = pat
		else:
			self.data_grid.patient = None
		return True
#================================================================
# main
#----------------------------------------------------------------
if __name__ == '__main__':

	from Gnumed.pycommon import gmLog2, gmI18N, gmDateTime

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
	if (len(sys.argv) > 1) and (sys.argv[1] == 'test'):
		test_grid()

#================================================================
# $Log: gmMeasurementWidgets.py,v $
# Revision 1.9  2008-04-16 20:39:39  ncq
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
