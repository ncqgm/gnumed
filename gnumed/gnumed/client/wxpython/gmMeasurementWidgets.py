"""GNUmed measurement widgets.
"""
#================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmMeasurementWidgets.py,v $
# $Id: gmMeasurementWidgets.py,v 1.57 2009-08-11 10:49:23 ncq Exp $
__version__ = "$Revision: 1.57 $"
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL"


import sys, logging, datetime as pyDT, decimal


import wx, wx.grid, wx.lib.hyperlink


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.business import gmPerson, gmPathLab, gmSurgery, gmLOINC
from Gnumed.pycommon import gmTools, gmDispatcher, gmMatchProvider, gmDateTime, gmI18N, gmCfg, gmShellAPI
from Gnumed.wxpython import gmRegetMixin, gmPhraseWheel, gmEditArea, gmGuiHelpers, gmListWidgets, gmAuthWidgets, gmPatSearchWidgets
from Gnumed.wxGladeWidgets import wxgMeasurementsPnl, wxgMeasurementsReviewDlg
from Gnumed.wxGladeWidgets import wxgMeasurementEditAreaPnl


_log = logging.getLogger('gm.ui')
_log.info(__version__)
#================================================================
# LOINC related widgets
#================================================================
def update_loinc_reference_data():

	wx.BeginBusyCursor()

	gmDispatcher.send(signal = 'statustext', msg = _('Updating LOINC data can take quite a while...'), beep = True)

	# download
	downloaded = gmShellAPI.run_command_in_shell(command = 'gm-download_loinc', blocking = True)
	if not downloaded:
		wx.EndBusyCursor()
		gmGuiHelpers.gm_show_warning (
			aTitle = _('Downloading LOINC'),
			aMessage = _(
				'Running <gm-download_loinc> to retrieve\n'
				'the latest LOINC data failed.\n'
			)
		)
		return False

	# split and import
	data_fname, license_fname = gmLOINC.split_LOINCDBTXT(input_fname = '/tmp/LOINCDB.TXT')

	wx.EndBusyCursor()

	conn = gmAuthWidgets.get_dbowner_connection(procedure = _('importing LOINC reference data'))
	if conn is None:
		return False

	wx.BeginBusyCursor()

	if gmLOINC.loinc_import(data_fname = data_fname, license_fname = license_fname, conn = conn):
		gmDispatcher.send(signal = 'statustext', msg = _('Successfully imported LOINC reference data.'))
		try:
			os.remove(data_fname)
			os.remove(license_fname)
		except OSError:
			_log.error('unable to remove [%s] or [%s]', data_fname, license_fname)
	else:
		gmDispatcher.send(signal = 'statustext', msg = _('Importing LOINC reference data failed.'), beep = True)

	wx.EndBusyCursor()
	return True
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
		dlg.Destroy()
		return True
	dlg.Destroy()
	return False
#================================================================
#from Gnumed.wxGladeWidgets import wxgPrimaryCareVitalsInputPnl

# Taillenumfang: Mitte zwischen unterster Rippe und
# hoechstem Teil des Beckenkamms
# Maenner: maessig: 94-102, deutlich: > 102  .. erhoeht
# Frauen:  maessig: 80-88,  deutlich: > 88   .. erhoeht

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
	def __init__(self, *args, **kwargs):

		wx.grid.Grid.__init__(self, *args, **kwargs)

		self.__patient = None
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
			txt = u'\n'.join([ u'%s %s (%s): %s %s%s' % (
					r['clin_when'].strftime('%x %H:%M').decode(gmI18N.get_encoding()),
					r['unified_abbrev'],
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
				# loop over results in cell and only include
				# this multi-value cells that are not ambigous
				do_not_include = False
				for result in self.__cell_data[col_idx][row_idx]:
					if unsigned_only:
						if result['reviewed']:
							do_not_include = True
							break
					if accountables_only:
						if not result['you_are_responsible']:
							do_not_include = True
							break
				if do_not_include:
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

		self.__row_label_data = emr.get_test_types_for_results()
		test_type_labels = [ u'%s (%s)' % (test[1], test[0]) for test in self.__row_label_data ]
		if len(test_type_labels) == 0:
			return

#		test_details, td_idx = emr.get_test_types_details()
		test_date_labels = [ date[0].strftime(self.__date_format) for date in emr.get_dates_for_results() ]
		results = emr.get_test_results_by_date()

		self.BeginBatch()

		# rows
		self.AppendRows(numRows = len(test_type_labels))
		for row_idx in range(len(test_type_labels)):
			self.SetRowLabelValue(row_idx, test_type_labels[row_idx])

		# columns
		self.AppendCols(numCols = len(test_date_labels))
		for date_idx in range(len(test_date_labels)):
			self.SetColLabelValue(date_idx, test_date_labels[date_idx])

		# cell values (list of test results)
		for result in results:
			row = test_type_labels.index(u'%s (%s)' % (result['unified_abbrev'], result['unified_name']))
			col = test_date_labels.index(result['clin_when'].strftime(self.__date_format))

			try:
				self.__cell_data[col]
			except KeyError:
				self.__cell_data[col] = {}

			# the tooltip always shows the youngest sub result details
			if self.__cell_data[col].has_key(row):
				self.__cell_data[col][row].append(result)
				self.__cell_data[col][row].sort(key = lambda x: x['clin_when'], reverse = True)
			else:
				self.__cell_data[col][row] = [result]

			# rebuild cell display string
			vals2display = []
			for sub_result in self.__cell_data[col][row]:

				# is the sub_result technically abnormal ?
				ind = gmTools.coalesce(sub_result['abnormality_indicator'], u'').strip()
				if ind != u'':
					lab_abnormality_indicator = u' (%s)' % ind[:3]
				else:
					lab_abnormality_indicator = u''
				# - if noone reviewed - use what the lab thinks
				if sub_result['is_technically_abnormal'] is None:
					abnormality_indicator = lab_abnormality_indicator
				# - if someone reviewed and decreed normality - use that
				elif sub_result['is_technically_abnormal'] is False:
					abnormality_indicator = u''
				# - if someone reviewed and decreed abnormality ...
				else:
					# ... invent indicator if the lab did't use one
					if lab_abnormality_indicator == u'':
						# FIXME: calculate from min/max/range
						abnormality_indicator = u' (%s)' % gmTools.u_plus_minus
					# ... else use indicator the lab used
					else:
						abnormality_indicator = lab_abnormality_indicator

				# is the sub_result relevant clinically ?
				# FIXME: take into account primary_GP once we support that
				sub_result_relevant = sub_result['is_clinically_relevant']
				if sub_result_relevant is None:
					# FIXME: calculate from clinical range
					sub_result_relevant = False

				missing_review = False
				# warn on missing review if
				# a) no review at all exists or
				if not sub_result['reviewed']:
					missing_review = True
				# b) there is a review but
				else:
					# current user is reviewer and hasn't reviewed
					if sub_result['you_are_responsible'] and not sub_result['review_by_you']:
						missing_review = True

				# can we display the full sub_result length ?
				if len(sub_result['unified_val']) > 8:
					tmp = u'%.7s%s' % (sub_result['unified_val'][:7], gmTools.u_ellipsis)
				else:
					tmp = u'%.8s' % sub_result['unified_val'][:8]

				# abnormal ?
				tmp = u'%s%.6s' % (tmp, abnormality_indicator)

				# is there a comment ?
				has_sub_result_comment = gmTools.coalesce (
					gmTools.coalesce(sub_result['note_test_org'], sub_result['comment']),
					u''
				).strip() != u''
				if has_sub_result_comment:
					tmp = u'%s %s' % (tmp, gmTools.u_ellipsis)

				# lacking a review ?
				if missing_review:
					tmp = u'%s %s' % (tmp, gmTools.u_writing_hand)

				# part of a multi-result cell ?
				if len(self.__cell_data[col][row]) > 1:
					tmp = u'%s %s' % (sub_result['clin_when'].strftime('%H:%M'), tmp)

				vals2display.append(tmp)

			self.SetCellValue(row, col, u'\n'.join(vals2display))
			self.SetCellAlignment(row, col, horiz = wx.ALIGN_RIGHT, vert = wx.ALIGN_CENTRE)
#			font = self.GetCellFont(row, col)
#			if not font.IsFixedWidth():
#				font.SetFamily(family = wx.FONTFAMILY_MODERN)
			# FIXME: what about partial sub results being relevant ??
			if sub_result_relevant:
				font = self.GetCellFont(row, col)
				self.SetCellTextColour(row, col, 'firebrick')
				font.SetWeight(wx.FONTWEIGHT_BOLD)
				self.SetCellFont(row, col, font)
#			self.SetCellFont(row, col, font)

		self.AutoSize()
		self.EndBatch()
		return
	#------------------------------------------------------------
	def empty_grid(self):
		self.BeginBatch()
		self.ClearGrid()
		# Windows cannot do nothing, it rather decides to assert()
		# on thinking it is supposed to do nothing
		if self.GetNumberRows() > 0:
			self.DeleteRows(pos = 0, numRows = self.GetNumberRows())
		if self.GetNumberCols() > 0:
			self.DeleteCols(pos = 0, numCols = self.GetNumberCols())
		self.EndBatch()
		self.__cell_data = {}
	#------------------------------------------------------------
	def get_cell_tooltip(self, col=None, row=None):
		# FIXME: add panel/battery, request details

		try:
			d = self.__cell_data[col][row]
		except KeyError:
			d = None

		if d is None:
			return u''

		is_multi_cell = False
		if len(d) > 1:
			is_multi_cell = True

		d = d[0]

		has_normal_min_or_max = (d['val_normal_min'] is not None) or (d['val_normal_max'] is not None)
		if has_normal_min_or_max:
			normal_min_max = u'%s - %s' % (
				gmTools.coalesce(d['val_normal_min'], u'?'),
				gmTools.coalesce(d['val_normal_max'], u'?')
			)
		else:
			normal_min_max = u''

		has_clinical_min_or_max = (d['val_target_min'] is not None) or (d['val_target_max'] is not None)
		if has_clinical_min_or_max:
			clinical_min_max = u'%s - %s' % (
				gmTools.coalesce(d['val_target_min'], u'?'),
				gmTools.coalesce(d['val_target_max'], u'?')
			)
		else:
			clinical_min_max = u''

		# header
		if is_multi_cell:
			tt = _(u'Measurement details of most recent (topmost) result:               \n')
		else:
			tt = _(u'Measurement details:                                               \n')

		# basics
		tt += u' ' + _(u'Date: %s\n') % d['clin_when'].strftime('%c').decode(gmI18N.get_encoding())
		tt += u' ' + _(u'Type: "%(name)s" (%(code)s)  [#%(pk_type)s]\n') % ({
			'name': d['name_tt'],
			'code': d['code_tt'],
			'pk_type': d['pk_test_type']
		})
		tt += u' ' + _(u'Result: %(val)s%(unit)s%(ind)s  [#%(pk_result)s]\n') % ({
			'val': d['unified_val'],
			'unit': gmTools.coalesce(d['val_unit'], u'', u' %s'),
			'ind': gmTools.coalesce(d['abnormality_indicator'], u'', u' (%s)'),
			'pk_result': d['pk_test_result']
		})

		# clinical evaluation
		norm_eval = None
		if d['val_num'] is not None:
			# 1) normal range
			# lowered ?
			if (d['val_normal_min'] is not None) and (d['val_num'] < d['val_normal_min']):
				try:
					percent = (d['val_num'] * 100) / d['val_normal_min']
				except ZeroDivisionError:
					percent = None
				if percent is not None:
					if percent < 6:
						norm_eval = _(u'%.1f %% of the normal lower limit') % percent
					else:
						norm_eval = _(u'%.0f %% of the normal lower limit') % percent
			# raised ?
			if (d['val_normal_max'] is not None) and (d['val_num'] > d['val_normal_max']):
				try:
					x_times = d['val_num'] / d['val_normal_max']
				except ZeroDivisionError:
					x_times = None
				if x_times is not None:
					if x_times < 10:
						norm_eval = _(u'%.1f times the normal upper limit') % x_times
					else:
						norm_eval = _(u'%.0f times the normal upper limit') % x_times
			if norm_eval is not None:
				tt += u'  (%s)\n' % norm_eval
#			#-------------------------------------
#			# this idea was shot down on the list
#			#-------------------------------------
#			# bandwidth of deviation
#			if None not in [d['val_normal_min'], d['val_normal_max']]:
#				normal_width = d['val_normal_max'] - d['val_normal_min']
#				deviation_from_normal_range = None
#				# below ?
#				if d['val_num'] < d['val_normal_min']:
#					deviation_from_normal_range = d['val_normal_min'] - d['val_num']
#				# above ?
#				elif d['val_num'] > d['val_normal_max']:
#					deviation_from_normal_range = d['val_num'] - d['val_normal_max']
#				if deviation_from_normal_range is None:
#					try:
#						times_deviation = deviation_from_normal_range / normal_width
#					except ZeroDivisionError:
#						times_deviation = None
#					if times_deviation is not None:
#						if times_deviation < 10:
#							tt += u'  (%s)\n' % _(u'deviates by %.1f times of the normal range') % times_deviation
#						else:
#							tt += u'  (%s)\n' % _(u'deviates by %.0f times of the normal range') % times_deviation
#			#-------------------------------------

			# 2) clinical target range
			norm_eval = None
			# lowered ?
			if (d['val_target_min'] is not None) and (d['val_num'] < d['val_target_min']):
				try:
					percent = (d['val_num'] * 100) / d['val_target_min']
				except ZeroDivisionError:
					percent = None
				if percent is not None:
					if percent < 6:
						norm_eval = _(u'%.1f %% of the target lower limit') % percent
					else:
						norm_eval = _(u'%.0f %% of the target lower limit') % percent
			# raised ?
			if (d['val_target_max'] is not None) and (d['val_num'] > d['val_target_max']):
				try:
					x_times = d['val_num'] / d['val_target_max']
				except ZeroDivisionError:
					x_times = None
				if x_times is not None:
					if x_times < 10:
						norm_eval = _(u'%.1f times the target upper limit') % x_times
					else:
						norm_eval = _(u'%.0f times the target upper limit') % x_times
			if norm_eval is not None:
				tt += u' (%s)\n' % norm_eval
#			#-------------------------------------
#			# this idea was shot down on the list
#			#-------------------------------------
#			# bandwidth of deviation
#			if None not in [d['val_target_min'], d['val_target_max']]:
#				normal_width = d['val_target_max'] - d['val_target_min']
#				deviation_from_target_range = None
#				# below ?
#				if d['val_num'] < d['val_target_min']:
#					deviation_from_target_range = d['val_target_min'] - d['val_num']
#				# above ?
#				elif d['val_num'] > d['val_target_max']:
#					deviation_from_target_range = d['val_num'] - d['val_target_max']
#				if deviation_from_target_range is None:
#					try:
#						times_deviation = deviation_from_target_range / normal_width
#					except ZeroDivisionError:
#						times_deviation = None
#				if times_deviation is not None:
#					if times_deviation < 10:
#						tt += u'  (%s)\n' % _(u'deviates by %.1f times of the target range') % times_deviation
#					else:
#						tt += u'  (%s)\n' % _(u'deviates by %.0f times of the target range') % times_deviation
#			#-------------------------------------

		# ranges
		tt += u'\n'
		tt += u' ' + _(u'Standard normal range: %(norm_min_max)s%(norm_range)s  \n') % ({
			'norm_min_max': normal_min_max,
			'norm_range': gmTools.coalesce (
				d['val_normal_range'],
				u'',
				gmTools.bool2subst (
					has_normal_min_or_max,
					u' / %s',
					u'%s'
				)
			)
		})
		tt += u' ' + _(u'Reference group: %(ref_group)s\n') % ({'ref_group': gmTools.coalesce(d['norm_ref_group'], u'')})
		tt += u' ' + _(u'Clinical target range: %(clin_min_max)s%(clin_range)s  \n') % ({
			'clin_min_max': clinical_min_max,
			'clin_range': gmTools.coalesce (
				d['val_target_range'],
				u'',
				gmTools.bool2subst (
					has_clinical_min_or_max,
					u' / %s',
					u'%s'
				)
			)
		})

		# metadata
		tt += u' ' + _(u'Doc: %s\n') % _(u'\n Doc: ').join(gmTools.coalesce(d['comment'], u'').split(u'\n'))
		tt += u' ' + _(u'Lab: %s\n') % _(u'\n Lab: ').join(gmTools.coalesce(d['note_test_org'], u'').split(u'\n'))
		tt += u' ' + _(u'Episode: %s\n') % d['episode']
		tt += u' ' + _(u'Issue: %s\n') % gmTools.coalesce(d['health_issue'], u'')
		tt += u' ' + _(u'Material: %s\n') % gmTools.coalesce(d['material'], u'')
		tt += u' ' + _(u'Details: %s\n') % gmTools.coalesce(d['material_detail'], u'')
		tt += u'\n'

		# review
		if d['reviewed']:
			review = d['last_reviewed'].strftime('%c').decode(gmI18N.get_encoding())
		else:
			review = _('not yet')
		tt += _(u'Signed (%(sig_hand)s): %(reviewed)s\n') % ({
			'sig_hand': gmTools.u_writing_hand,
			'reviewed': review
		})
		tt += u' ' + _(u'Last reviewer: %(reviewer)s\n') % ({'reviewer': gmTools.bool2subst(d['review_by_you'], _('you'), gmTools.coalesce(d['last_reviewer'], u''))})
		tt += u' ' + _(u' Technically abnormal: %(abnormal)s\n') % ({'abnormal': gmTools.bool2subst(d['is_technically_abnormal'], _('yes'), _('no'), u'')})
		tt += u' ' + _(u' Clinically relevant: %(relevant)s\n') % ({'relevant': gmTools.bool2subst(d['is_clinically_relevant'], _('yes'), _('no'), u'')})
		tt += u' ' + _(u' Comment: %s\n') % gmTools.coalesce(d['review_comment'], u'')
		tt += u' ' + _(u'Responsible clinician: %s\n') % gmTools.bool2subst(d['you_are_responsible'], _('you'), d['responsible_reviewer'])
		tt += u'\n'

		# type
		tt += _(u'Test type details:\n')
		tt += u' ' + _(u'Grouped under "%(name_meta)s" (%(abbrev_meta)s)  [#%(pk_u_type)s]\n') % ({
			'name_meta': gmTools.coalesce(d['name_meta'], u''),
			'abbrev_meta': gmTools.coalesce(d['abbrev_meta'], u''),
			'pk_u_type': d['pk_meta_test_type']
		})
		tt += u' ' + _(u'Type comment: %s\n') % _(u'\n Type comment:').join(gmTools.coalesce(d['comment_tt'], u'').split(u'\n'))
		tt += u' ' + _(u'Group comment: %s\n') % _(u'\n Group comment: ').join(gmTools.coalesce(d['comment_meta'], u'').split(u'\n'))
		tt += u'\n'

		tt += _(u'Revisions: %(row_ver)s, last %(mod_when)s by %(mod_by)s.') % ({
			'row_ver': d['row_version'],
			'mod_when': d['modified_when'].strftime('%c').decode(gmI18N.get_encoding()),
			'mod_by': d['modified_by']
		})

		return tt
	#------------------------------------------------------------
	# internal helpers
	#------------------------------------------------------------
	def __init_ui(self):
		self.CreateGrid(0, 1)
		self.EnableEditing(0)
		self.EnableDragGridSize(0)

		# setting this screws up the labels: they are cut off and displaced
		#self.SetColLabelAlignment(wx.ALIGN_CENTER, wx.ALIGN_BOTTOM)

		#self.SetRowLabelSize(wx.GRID_AUTOSIZE)		# starting with 2.8.8
		self.SetRowLabelSize(100)
		self.SetRowLabelAlignment(horiz = wx.ALIGN_LEFT, vert = wx.ALIGN_CENTRE)

		# add link to left upper corner
		dbcfg = gmCfg.cCfgSQL()
		url = dbcfg.get2 (
			option = u'external.urls.measurements_encyclopedia',
			workplace = gmSurgery.gmCurrentPractice().active_workplace,
			bias = 'user',
			default = u'http://www.laborlexikon.de'
		)

		self.__WIN_corner = self.GetGridCornerLabelWindow()		# a wx.Window instance

		LNK_lab = wx.lib.hyperlink.HyperLinkCtrl (
			self.__WIN_corner,
			-1,
			label = _('Reference'),
			style = wx.HL_DEFAULT_STYLE			# wx.TE_READONLY|wx.TE_CENTRE| wx.NO_BORDER |
		)
		LNK_lab.SetURL(url)
		LNK_lab.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_BACKGROUND))
		LNK_lab.SetToolTipString(_(
			'Navigate to an encyclopedia of measurements\n'
			'and test methods on the web.\n'
			'\n'
			' <%s>'
		) % url)

		SZR_inner = wx.BoxSizer(wx.HORIZONTAL)
		SZR_inner.Add((20, 20), 1, wx.EXPAND, 0)		# spacer
		SZR_inner.Add(LNK_lab, 0, wx.ALIGN_CENTER_VERTICAL, 0)		#wx.ALIGN_CENTER wx.EXPAND
		SZR_inner.Add((20, 20), 1, wx.EXPAND, 0)		# spacer

		SZR_corner = wx.BoxSizer(wx.VERTICAL)
		SZR_corner.Add((20, 20), 1, wx.EXPAND, 0)		# spacer
		SZR_corner.AddWindow(SZR_inner, 0, wx.EXPAND)	# inner sizer with centered hyperlink
		SZR_corner.Add((20, 20), 1, wx.EXPAND, 0)		# spacer

		self.__WIN_corner.SetSizer(SZR_corner)
		SZR_corner.Fit(self.__WIN_corner)
	#------------------------------------------------------------
	def __resize_corner_window(self, evt):
		self.__WIN_corner.Layout()
	#------------------------------------------------------------
	def __cells_to_data(self, cells=None, exclude_multi_cells=False):
		"""List of <cells> must be in row / col order."""
		data = []
		for row, col in cells:
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
			choices = [ [d['clin_when'], d['unified_abbrev'], d['unified_name'], d['unified_val']] for d in cell_data ],
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
		#self.GetGridColLabelWindow().Bind(wx.EVT_MOTION, self.__on_mouse_over_col_labels)

		# sizing left upper corner window
		self.Bind(wx.EVT_SIZE, self.__resize_corner_window)

		# editing cells
		self.Bind(wx.grid.EVT_GRID_CELL_LEFT_DCLICK, self.__on_cell_left_dclicked)
	#------------------------------------------------------------
	def __on_cell_left_dclicked(self, evt):
		col = evt.GetCol()
		row = evt.GetRow()

		# empty cell, perhaps ?
		try:
			self.__cell_data[col][row]
		except KeyError:
			# FIXME: invoke editor for adding value for day of that column
			# FIMXE: and test of that row
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
#     def OnMouseMotionColLabel(self, evt):
#         x, y = self.CalcUnscrolledPosition(evt.GetPosition())
#         col = self.XToCol(x)
#         label = self.table().GetColHelpValue(col)
#         self.GetGridColLabelWindow().SetToolTipString(label or "")
#         evt.Skip()
#
#     def OnMouseMotionRowLabel(self, evt):
#         x, y = self.CalcUnscrolledPosition(evt.GetPosition())
#         row = self.YToRow(y)
#         label = self.table().GetRowHelpValue(row)
#         self.GetGridRowLabelWindow().SetToolTipString(label or "")
#         evt.Skip()
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

		evt.GetEventObject().SetToolTipString(self.get_cell_tooltip(col=col, row=row))
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
		gmDispatcher.connect(signal = u'post_patient_selection', receiver = self._on_post_patient_selection)
		gmDispatcher.connect(signal = u'test_result_mod_db', receiver = self._schedule_data_reget)
		gmDispatcher.connect(signal = u'reviewed_test_results_mod_db', receiver = self._schedule_data_reget)
	#--------------------------------------------------------
	def _on_post_patient_selection(self):
		wx.CallAfter(self.__on_post_patient_selection)
	#--------------------------------------------------------
	def __on_post_patient_selection(self):
		self._schedule_data_reget()
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
						t['unified_abbrev'],
						t['unified_val'],
						t['val_unit'],
						t['clin_when'].strftime('%x').decode(gmI18N.get_encoding())
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

		self.successful_save_msg = _('Successfully saved measurement.')
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
		self._TCTRL_normal_min.SetValue(unicode(gmTools.coalesce(self.data['val_normal_min'], u'')))
		self._TCTRL_normal_max.SetValue(unicode(gmTools.coalesce(self.data['val_normal_max'], u'')))
		self._TCTRL_normal_range.SetValue(gmTools.coalesce(self.data['val_normal_range'], u''))
		self._TCTRL_target_min.SetValue(unicode(gmTools.coalesce(self.data['val_target_min'], u'')))
		self._TCTRL_target_max.SetValue(unicode(gmTools.coalesce(self.data['val_target_max'], u'')))
		self._TCTRL_target_range.SetValue(gmTools.coalesce(self.data['val_target_range'], u''))
		self._TCTRL_norm_ref_group.SetValue(gmTools.coalesce(self.data['norm_ref_group'], u''))

		self._TCTRL_result.SetFocus()
	#--------------------------------------------------------
	def _refresh_as_new_from_existing(self):
		self._refresh_from_existing()

		self._PRW_test.SetText(u'', None, True)
		self._TCTRL_result.SetValue(u'')
		self._PRW_units.SetText(u'', None, True)
		self._PRW_abnormality_indicator.SetText(u'', None, True)
		# self._DPRW_evaluated
		self._TCTRL_note_test_org.SetValue(u'')
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
			validity = False
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
				decimal.Decimal(val.replace(',', u'.', 1))
				widget.SetBackgroundColour(gmPhraseWheel.color_prw_valid)
			except:
				widget.SetBackgroundColour(gmPhraseWheel.color_prw_invalid)
				validity = False

		if validity is False:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot save result. Invalid or missing essential input.'))

		return validity
	#--------------------------------------------------------
	def _save_as_new(self):

		emr = gmPerson.gmCurrentPatient().get_emr()

		try:
			v_num = decimal.Decimal(self._TCTRL_result.GetValue().strip().replace(',', '.', 1))
			v_al = None
		except:
			v_num = None
			v_al = self._TCTRL_result.GetValue().strip()

		pk_type = self._PRW_test.GetData()
		if pk_type is None:
			tt = gmPathLab.create_measurement_type (
				lab = None,
				abbrev = self._PRW_test.GetValue().strip(),
				name = self._PRW_test.GetValue().strip(),
				unit = gmTools.none_if(self._PRW_units.GetValue().strip(), u'')
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

		success, result = gmTools.input2decimal(self._TCTRL_result.GetValue())
		if success:
			v_num = result
			v_al = None
		else:
			v_num = None
			v_al = self._TCTRL_result.GetValue().strip()

		pk_type = self._PRW_test.GetData()
		if pk_type is None:
			tt = gmPathLab.create_measurement_type (
				lab = None,
				abbrev = self._PRW_test.GetValue().strip(),
				name = self._PRW_test.GetValue().strip(),
				unit = gmTools.none_if(self._PRW_units.GetValue().strip(), u'')
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
# measurement type handling
#================================================================
def manage_measurement_types(parent=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	#------------------------------------------------------------
	def edit(test_type=None):
		ea = cMeasurementTypeEAPnl(parent = parent, id = -1, type = test_type)
		dlg = gmEditArea.cGenericEditAreaDlg2 (
			parent = parent,
			id = -1,
			edit_area = ea,
			single_entry = gmTools.bool2subst((test_type is None), False, True)
		)
		dlg.SetTitle(gmTools.coalesce(test_type, _('Adding measurement type'), _('Editing measurement type')))

		if dlg.ShowModal() == wx.ID_OK:
			dlg.Destroy()
			return True

		dlg.Destroy()
		return False
	#------------------------------------------------------------
	def refresh(lctrl):
		mtypes = gmPathLab.get_measurement_types()
		items = [ [
			m['abbrev'],
			m['name'],
			gmTools.coalesce(m['loinc'], u''),
			gmTools.coalesce(m['conversion_unit'], u''),
			gmTools.coalesce(m['comment_type'], u''),
			gmTools.coalesce(m['internal_name_org'], _('in-house')),
			gmTools.coalesce(m['comment_org'], u''),
			m['pk_test_type']
		] for m in mtypes ]
		lctrl.set_string_items(items)
		lctrl.set_data(mtypes)
	#------------------------------------------------------------
	def delete(measurement_type):
		gmPathLab.delete_measurement_type(measurement_type = measurement_type['pk_test_type'])
		return True
	#------------------------------------------------------------
	msg = _(
		'\n'
		'These are the measurement types currently defined in GNUmed.\n'
		'\n'
	)

	gmListWidgets.get_choices_from_list (
		parent = parent,
		msg = msg,
		caption = _('Showing measurement types.'),
		columns = [_('Abbrev'), _('Name'), _('LOINC'), _('Base unit'), _('Comment'), _('Org'), _('Comment'), u'#'],
		single_selection = True,
		refresh_callback = refresh,
		edit_callback = edit,
		new_callback = edit,
		delete_callback = delete
	)
#----------------------------------------------------------------
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
	name_meta %%(fragment_condition)s

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
	abbrev_meta %%(fragment_condition)s

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
		mp.word_separators = '[ \t:@]+'
		gmPhraseWheel.cPhraseWheel.__init__ (
			self,
			*args,
			**kwargs
		)
		self.matcher = mp
		self.SetToolTipString(_('Select the type of measurement.'))
		self.selection_only = False
#----------------------------------------------------------------
from Gnumed.wxGladeWidgets import wxgMeasurementTypeEAPnl

class cMeasurementTypeEAPnl(wxgMeasurementTypeEAPnl.wxgMeasurementTypeEAPnl, gmEditArea.cGenericEditAreaMixin):

	def __init__(self, *args, **kwargs):

		try:
			data = kwargs['type']
			del kwargs['type']
		except KeyError:
			data = None

		wxgMeasurementTypeEAPnl.wxgMeasurementTypeEAPnl.__init__(self, *args, **kwargs)
		gmEditArea.cGenericEditAreaMixin.__init__(self)
		self.mode = 'new'
		self.data = data
		if data is not None:
			self.mode = 'edit'

		self.__init_ui()

	#----------------------------------------------------------------
	def __init_ui(self):

		# name phraseweel
		query = u"""
select distinct on (name)
	pk,
	name
from clin.test_type
where
	name %(fragment_condition)s
order by name
limit 50"""
		mp = gmMatchProvider.cMatchProvider_SQL2(queries=query)
		mp.setThresholds(1, 2, 4)
		self._PRW_name.matcher = mp
		self._PRW_name.selection_only = False

		# abbreviation
		query = u"""
select distinct on (abbrev)
	pk,
	abbrev
from clin.test_type
where
	abbrev %(fragment_condition)s
order by abbrev
limit 50"""
		mp = gmMatchProvider.cMatchProvider_SQL2(queries=query)
		mp.setThresholds(1, 2, 3)
		self._PRW_abbrev.matcher = mp
		self._PRW_abbrev.selection_only = False

		# unit
		# FIXME: use units from test_result
		query = u"""
select distinct on (conversion_unit)
	conversion_unit,
	conversion_unit
from clin.test_type
where
	conversion_unit %(fragment_condition)s
order by conversion_unit
limit 50"""
		mp = gmMatchProvider.cMatchProvider_SQL2(queries=query)
		mp.setThresholds(1, 2, 3)
		self._PRW_conversion_unit.matcher = mp
		self._PRW_conversion_unit.selection_only = False

		# loinc
		query = u"""
select distinct on (term)
	loinc,
	term
from ((
		select
			loinc,
			loinc as term
		from clin.test_type
		where loinc %(fragment_condition)s
	) union all (
		select
			code as loinc,
			(code || ': ' || term) as term
		from ref.v_coded_terms
		where
			coding_system = 'LOINC'
				and
			lang = i18n.get_curr_lang()
				and
			(code %(fragment_condition)s
				or
			term %(fragment_condition)s)
	) union all (
		select
			code as loinc,
			(code || ': ' || term) as term
		from ref.v_coded_terms
		where
			coding_system = 'LOINC'
				and
			lang = 'en_EN'
				and
			(code %(fragment_condition)s
				or
			term %(fragment_condition)s)
	) union all (
		select
			code as loinc,
			(code || ': ' || term) as term
		from ref.v_coded_terms
		where
			coding_system = 'LOINC'
				and
			(code %(fragment_condition)s
				or
			term %(fragment_condition)s)
	)
) as all_known_loinc
order by term
limit 50"""
		mp = gmMatchProvider.cMatchProvider_SQL2(queries = query)
		mp.setThresholds(1, 2, 4)
		self._PRW_loinc.matcher = mp
		self._PRW_loinc.selection_only = False
		self._PRW_loinc.add_callback_on_lose_focus(callback = self._on_loinc_lost_focus)

		# test org
		query = u"""
select distinct on (internal_name)
	pk,
	internal_name
from clin.test_org
where
	internal_name %(fragment_condition)s
order by internal_name
limit 50"""
		mp = gmMatchProvider.cMatchProvider_SQL2(queries=query)
		mp.setThresholds(1, 2, 4)
		self._PRW_test_org.matcher = mp
		self._PRW_test_org.selection_only = False
	#----------------------------------------------------------------
	def _on_loinc_lost_focus(self):
		loinc = self._PRW_loinc.GetData()

		if loinc is None:
			self._TCTRL_loinc_info.SetValue(u'')
			return

		info = gmLOINC.loinc2info(loinc = loinc)
		if len(info) == 0:
			self._TCTRL_loinc_info.SetValue(u'')
			return

		self._TCTRL_loinc_info.SetValue(info[0])
	#----------------------------------------------------------------
	# generic Edit Area mixin API
	#----------------------------------------------------------------
	def _valid_for_save(self):

		has_errors = False
		for field in [self._PRW_name, self._PRW_abbrev, self._PRW_conversion_unit]:
			if field.GetValue().strip() in [u'', None]:
				has_errors = True
				field.display_as_valid(valid = False)
			else:
				field.display_as_valid(valid = True)
			field.Refresh()

		return (not has_errors)
	#----------------------------------------------------------------
	def _save_as_new(self):

		pk_org = self._PRW_test_org.GetData()
		if pk_org is None:
			pk_org = gmPathLab.create_measurement_org (
				name = gmTools.none_if(self._PRW_test_org.GetValue().strip(), u''),
				comment = gmTools.none_if(self._TCTRL_comment_org.GetValue().strip(), u'')
			)

		tt = gmPathLab.create_measurement_type (
			lab = pk_org,
			abbrev = self._PRW_abbrev.GetValue().strip(),
			name = self._PRW_name.GetValue().strip(),
			unit = gmTools.none_if(self._PRW_conversion_unit.GetValue().strip(), u'')
		)
		tt['loinc'] = gmTools.none_if(self._PRW_loinc.GetValue().strip(), u'')
		tt['comment_type'] = gmTools.none_if(self._TCTRL_comment_type.GetValue().strip(), u'')
		tt.save()

		self.data = tt

		return True
	#----------------------------------------------------------------
	def _save_as_update(self):

		pk_org = self._PRW_test_org.GetData()
		if pk_org is None:
			pk_org = gmPathLab.create_measurement_org (
				name = gmTools.none_if(self._PRW_test_org.GetValue().strip(), u''),
				comment = gmTools.none_if(self._TCTRL_comment_org.GetValue().strip(), u'')
			)

		self.data['pk_test_org'] = pk_org
		self.data['abbrev'] = self._PRW_abbrev.GetValue().strip()
		self.data['name'] = self._PRW_name.GetValue().strip()
		self.data['conversion_unit'] = gmTools.none_if(self._PRW_conversion_unit.GetValue().strip(), u'')
		self.data['loinc'] = gmTools.none_if(self._PRW_loinc.GetValue().strip(), u'')
		self.data['comment_type'] = gmTools.none_if(self._TCTRL_comment_type.GetValue().strip(), u'')
		self.data.save()

		return True
	#----------------------------------------------------------------
	def _refresh_as_new(self):
		self._PRW_name.SetText(u'', None, True)
		self._PRW_abbrev.SetText(u'', None, True)
		self._PRW_conversion_unit.SetText(u'', None, True)
		self._PRW_loinc.SetText(u'', None, True)
		self._TCTRL_loinc_info.SetValue(u'')
		self._TCTRL_comment_type.SetValue(u'')
		self._PRW_test_org.SetText(u'', None, True)
		self._TCTRL_comment_org.SetValue(u'')
	#----------------------------------------------------------------
	def _refresh_from_existing(self):
		self._PRW_name.SetText(self.data['name'], self.data['name'], True)
		self._PRW_abbrev.SetText(self.data['abbrev'], self.data['abbrev'], True)
		self._PRW_conversion_unit.SetText (
			gmTools.coalesce(self.data['conversion_unit'], u''),
			self.data['conversion_unit'],
			True
		)
		self._PRW_loinc.SetText (
			gmTools.coalesce(self.data['loinc'], u''),
			self.data['loinc'],
			True
		)
		self._TCTRL_loinc_info.SetValue(u'')			# FIXME: properly set
		self._TCTRL_comment_type.SetValue(gmTools.coalesce(self.data['comment_type'], u''))
		self._PRW_test_org.SetText (
			gmTools.coalesce(self.data['pk_test_org'], u'', self.data['internal_name_org']),
			self.data['pk_test_org'],
			True
		)
		self._TCTRL_comment_org.SetValue(gmTools.coalesce(self.data['comment_org'], u''))
	#----------------------------------------------------------------
	def _refresh_as_new_from_existing(self):
		self._refresh_as_new()
		self._PRW_test_org.SetText (
			gmTools.coalesce(self.data['pk_test_org'], u'', self.data['internal_name_org']),
			self.data['pk_test_org'],
			True
		)
		self._TCTRL_comment_org.SetValue(gmTools.coalesce(self.data['comment_org'], u''))
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
				'where_part': u'and %(test)s in (name_tt, name_meta, code_tt, abbrev_meta)',
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
def manage_meta_test_types(parent=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	msg = _(
		'\n'
		'These are the meta test types currently defined in GNUmed.\n'
		'\n'
		'Meta test types allow you to aggregate several actual test types used\n'
		'by pathology labs into one logical type.\n'
		'\n'
		'This is useful for grouping together results of tests which come under\n'
		'different names but really are the same thing. This often happens when\n'
		'you switch labs or the lab starts using another test method.\n'
	)

	mtts = gmPathLab.get_meta_test_types()

	gmListWidgets.get_choices_from_list (
		parent = parent,
		msg = msg,
		caption = _('Showing meta test types.'),
		columns = [_('Abbrev'), _('Name'), _('LOINC'), _('Comment'), u'#'],
		choices = [ [
			m['abbrev'],
			m['name'],
			gmTools.coalesce(m['loinc'], u''),
			gmTools.coalesce(m['comment'], u''),
			m['pk']
		] for m in mtts ],
		data = mtts,
		single_selection = True,
		#edit_callback = edit,
		#new_callback = edit,
		#delete_callback = delete,
		#refresh_callback = refresh
	)
#================================================================
# main
#----------------------------------------------------------------
if __name__ == '__main__':

	from Gnumed.pycommon import gmLog2

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
		gmPatSearchWidgets.set_active_patient(patient=pat)
		app = wx.PyWidgetTester(size = (500, 300))
		ea = cMeasurementEditAreaPnl(parent = app.frame, id = -1)
		app.frame.Show()
		app.MainLoop()
	#------------------------------------------------------------
#	def test_primary_care_vitals_pnl():
#		app = wx.PyWidgetTester(size = (500, 300))
#		pnl = wxgPrimaryCareVitalsInputPnl.wxgPrimaryCareVitalsInputPnl(parent = app.frame, id = -1)
#		app.frame.Show()
#		app.MainLoop()
	#------------------------------------------------------------
	if (len(sys.argv) > 1) and (sys.argv[1] == 'test'):
		#test_grid()
		test_test_ea_pnl()
		#test_primary_care_vitals_pnl()

#================================================================
# $Log: gmMeasurementWidgets.py,v $
# Revision 1.57  2009-08-11 10:49:23  ncq
# - cleanup
# - remove LOINC files after import
# - row labels now "abbrev (desc)", again
# - Encyclopedia -> Reference
# - improved LOINC matcher and use loinc to set loinc info
#
# Revision 1.56  2009/08/08 12:18:12  ncq
# - setup phrasewheels in measurement type EA
#
# Revision 1.55  2009/08/03 20:50:48  ncq
# - properly support adding/editing measurement type
#
# Revision 1.54  2009/07/20 20:33:35  ncq
# - start implementing test type management
#
# Revision 1.53  2009/07/15 12:22:46  ncq
# - fix incomplete validity check for new-result problem
#
# Revision 1.52  2009/07/06 17:15:45  ncq
# - row labels only test name until proper support for abbrev is there
# - improved formatting of test result for display in cell
# - only remind of display being most-recent only if cell actually is multi-result in cell tooltip
# - use successful-save message on EA
# - safer refresh after save-and-next-value
#
# Revision 1.51  2009/07/02 20:54:05  ncq
# - fix bug where second patient didn't show measurements on patient change
#
# Revision 1.50  2009/06/22 09:26:49  ncq
# - people didn't like the bandwidth calculation
#
# Revision 1.49  2009/06/20 22:38:05  ncq
# - factor out cell tooltip creation and only do it on mouse over
#
# Revision 1.48  2009/06/11 12:37:25  ncq
# - much simplified initial setup of list ctrls
#
# Revision 1.47  2009/06/04 16:19:00  ncq
# - re-adjust to test table changes
# - update loinc
# - adjust to list widget changes (refresh)
#
# Revision 1.47  2009/05/28 10:53:40  ncq
# - adjust to test tables changes
#
# Revision 1.46  2009/05/24 16:29:14  ncq
# - support (meta) test types
#
# Revision 1.45  2009/04/24 12:05:20  ncq
# - properly display lab link in grid corner
#
# Revision 1.44  2009/04/21 17:01:12  ncq
# - try various other things to try to center the lab link
#
# Revision 1.43  2009/04/19 22:28:23  ncq
# - put hyperlink in upper left corner of lab grid
#
# Revision 1.42  2009/04/14 18:35:27  ncq
# - HCI screening revealed test types scroll off when
#   moving horizontall so fix that
#
# Revision 1.41  2009/04/03 09:50:21  ncq
# - comment
#
# Revision 1.40  2009/03/18 14:30:47  ncq
# - improved result tooltip
#
# Revision 1.39  2009/03/01 18:15:55  ncq
# - lots of missing u'', decode strftime results
# - adjust word separators in test type match provider
#
# Revision 1.38  2009/02/20 15:43:21  ncq
# - u''ify
#
# Revision 1.37  2009/02/17 17:47:31  ncq
# - comment out primary care vitals
#
# Revision 1.36  2009/02/12 16:23:39  ncq
# - start work on primary care vitals input
#
# Revision 1.35  2009/01/28 11:27:56  ncq
# - slightly better naming and comments
#
# Revision 1.34  2009/01/02 11:40:27  ncq
# - properly check for numericity of value/range input
#
# Revision 1.33  2008/10/22 12:21:57  ncq
# - use %x in strftime where appropriate
#
# Revision 1.32  2008/08/31 18:21:54  ncq
# - work around Windows' inability to do nothing when
#   there's nothing to do
#
# Revision 1.31  2008/08/31 18:04:30  ncq
# - properly handle cell data now being list in select_cells()
#
# Revision 1.30  2008/08/31 17:13:50  ncq
# - don't crash on double-clicking empty test results cell
#
# Revision 1.29  2008/08/31 17:04:17  ncq
# - need to cast val_normal/target_min/max to unicode before display
#
# Revision 1.28  2008/08/15 15:57:10  ncq
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
