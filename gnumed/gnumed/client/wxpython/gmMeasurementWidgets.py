"""GNUmed measurement widgets.
"""
#================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmMeasurementWidgets.py,v $
# $Id: gmMeasurementWidgets.py,v 1.2 2008-03-17 14:55:41 ncq Exp $
__version__ = "$Revision: 1.2 $"
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL"


import sys, logging


import wx, wx.grid


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmTools
#from Gnumed.wxpython import gmGuiHelpers
from Gnumed.wxGladeWidgets import wxgMeasurementsGridPnl


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
	# FIXME: improve result tooltip: health issue, episode, panel, request details, review status
	def __init__(self, *args, **kwargs):

		wx.grid.Grid.__init__(self, *args, **kwargs)

		self.__patient = None
		self.__tooltips = {}
		self.__prev_row = None
		self.__prev_col = None
		self.__date_format = (_('lab_grid_date_format::%Y\n%b %d')).lstrip('lab_grid_date_format::')

		self.__init_ui()
		self.__register_events()
	#------------------------------------------------------------
	# external API
	#------------------------------------------------------------
	def repopulate_grid(self):

		self.empty_grid()
		if self.__patient is None:
			return

		emr = self.__patient.get_emr()
		tests = [ u'%s (%s)' % (test[1], test[0]) for test in emr.get_test_types_for_results() ]
		if len(tests) == 0:
			return
		dates = [ date[0].strftime(self.__date_format) for date in emr.get_dates_for_results() ]
		results, idx = emr.get_measurements_by_date()

		self.BeginBatch()

		self.AppendRows(numRows = len(tests))
		for row_idx in range(len(tests)):
			#self.SetCellValue(row_idx, 0, u'%s (%s)' % (tests[row_idx][0], tests[row_idx][1]))
			self.SetCellValue(row_idx, 0, tests[row_idx])
			#self.SetRowLabelValue(row_idx, tests[row_idx])

		self.AppendCols(numCols = len(dates))
		for date_idx in range(len(dates)):
			#self.SetColLabelValue(date_idx + 1, dates[date_idx][0].strftime('%y/%b/%d'))
			self.SetColLabelValue(date_idx + 1, dates[date_idx])

		for result in results:
			row = tests.index(u'%s (%s)' % (result[idx['unified_code']], result[idx['unified_name']]))
			col = dates.index(result[idx['clin_when']].strftime(self.__date_format)) + 1

			self.SetCellValue(row, col, result[idx['unified_val']])
			self.SetCellAlignment(row, col, horiz = wx.ALIGN_RIGHT, vert = wx.ALIGN_CENTRE)
			try:
				self.__tooltips[col]
			except KeyError:
				self.__tooltips[col] = {}
			self.__tooltips[col][row] = _(
				'Measurement details from %(clin_when)s:                \n'
				' Type: "%(name)s" (%(code)s)\n'
				' Result: %(val)s%(unit)s%(ind)s\n'
				' Material: %(material)s\n'
				' Details: %(mat_detail)s\n'
				' Doc: %(comment_doc)s\n'
				' Lab: %(comment_lab)s\n'	# note provider
				'\n'
				' Standard normal range: %(norm_min)s - %(norm_max)s%(norm_range)s  \n'
				' Reference group: %(ref_group)s\n'
				' Clinical target range: %(clin_min)s - %(clin_max)s%(clin_range)s  \n'
				'\n'
				'Last modified %(mod_when)s by %(mod_by)s  \n'
				'\n'
				'Test type details:\n'
				' Grouped under "%(name_unified)s" (%(code_unified)s)  \n'
				' Type comment: %(comment_type)s\n'
				' Group comment: %(comment_type_unified)s\n'
			) % ({
				'clin_when': result[idx['clin_when']].strftime('%c'),
				'code': result[idx['code_tt']],
				'name': result[idx['name_tt']],
				'val': result[idx['unified_val']],
				'unit': gmTools.coalesce(result[idx['val_unit']], u'', u' %s'),
				'ind': gmTools.coalesce(result[idx['abnormality_indicator']], u'', u' (%s)'),
				'material': gmTools.coalesce(result[idx['material']], u''),
				'mat_detail': gmTools.coalesce(result[idx['material_detail']], u''),
				'comment_doc': u'\n Doc: '.join(gmTools.coalesce(result[idx['comment']], u'').split('\n')),
				'comment_lab': u'\n Lab: '.join(gmTools.coalesce(result[idx['comment']], u'').split('\n')),
				'norm_min': gmTools.coalesce(result[idx['val_normal_min']], u'?'),
				'norm_max': gmTools.coalesce(result[idx['val_normal_max']], u'?'),
				'norm_range': gmTools.coalesce(result[idx['val_normal_range']], u'', u' / %s'),
				'ref_group': gmTools.coalesce(result[idx['norm_ref_group']], u''),
				'clin_min': gmTools.coalesce(result[idx['val_target_min']], u'?'),
				'clin_max': gmTools.coalesce(result[idx['val_target_max']], u'?'),
				'clin_range': gmTools.coalesce(result[idx['val_target_range']], u'', u' / %s'),
				'mod_when': result[idx['modified_when']].strftime('%c'),
				'mod_by': result[idx['modified_by']],
				'comment_type': u'\n Type comment:'.join(gmTools.coalesce(result[idx['comment_tt']], u'').split('\n')),
				'name_unified': result[idx['name_unified']],
				'code_unified': result[idx['code_unified']],
				'comment_type_unified': u'\n Group comment: '.join(gmTools.coalesce(result[idx['comment_unified']], u'').split('\n'))
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
	#------------------------------------------------------------
	def __register_events(self):
		self.GetGridWindow().Bind(wx.EVT_MOTION, self.__on_mouse_over)
	#------------------------------------------------------------
	def __on_mouse_over(self, evt):
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
			tt = self.__tooltips[col][row]
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
class cMeasurementsGridPnl(wxgMeasurementsGridPnl.wxgMeasurementsGridPnl):

	def __init__(self, *args, **kwargs):

		wxgMeasurementsGridPnl.wxgMeasurementsGridPnl.__init__(self, *args, **kwargs)

		self.patient = None

		# hide line numbers
		self.grid_data.SetColSize(0, 0)
	#------------------------------------------
	def populate_grid(self, patient=None):
		pass
	#------------------------------------------

#================================================================
# main
#----------------------------------------------------------------
if __name__ == '__main__':

	from Gnumed.pycommon import gmLog2, gmI18N, gmDateTime
	from Gnumed.business import gmPerson

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
# Revision 1.2  2008-03-17 14:55:41  ncq
# - add lots of TODOs
# - better layout
# - set grid cell tooltips
#
# Revision 1.1  2008/03/16 11:57:47  ncq
# - first iteration
#
#
