"""GNUmed measurement widgets.
"""
#================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmMeasurementWidgets.py,v $
# $Id: gmMeasurementWidgets.py,v 1.1 2008-03-16 11:57:47 ncq Exp $
__version__ = "$Revision: 1.1 $"
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL"


import sys, logging


import wx, wx.grid


if __name__ == '__main__':
	sys.path.insert(0, '../../')
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
	# FIXME: add sort modes
	def __init__(self, *args, **kwargs):

		wx.grid.Grid.__init__(self, *args, **kwargs)

		self.__init_ui()
		self.__patient = None
		self.date_format = (_('lab_grid_date_format::%Y\n%b %d')).lstrip('lab_grid_date_format::')
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
		dates = [ date[0].strftime(self.date_format) for date in emr.get_dates_for_results() ]
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
			col = dates.index(result[idx['clin_when']].strftime(self.date_format)) + 1
			self.SetCellValue(row, col, result[idx['unified_val']])
			self.SetCellAlignment(row, col, horiz = wx.ALIGN_RIGHT, vert = wx.ALIGN_CENTRE)

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
# Revision 1.1  2008-03-16 11:57:47  ncq
# - first iteration
#
#
