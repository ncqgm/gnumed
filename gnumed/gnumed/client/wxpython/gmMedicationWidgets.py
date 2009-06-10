"""GNUmed medication/substances handling widgets.
"""
#================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmMedicationWidgets.py,v $
# $Id: gmMedicationWidgets.py,v 1.3 2009-06-10 21:02:34 ncq Exp $
__version__ = "$Revision: 1.3 $"
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"

import logging, sys, os.path


import wx, wx.grid


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmDispatcher
#gmCfg, gmPG2, gmMimeLib, gmExceptions, gmMatchProvider, gmDateTime, gmTools, gmShellAPI, gmHooks
from Gnumed.business import gmPerson, gmATC
#, gmEMRStructItems, gmSurgery
from Gnumed.wxpython import gmGuiHelpers, gmRegetMixin, gmAuthWidgets


_log = logging.getLogger('gm.ui')
_log.info(__version__)

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
			_('Episode')
		]
#		self.__cell_tooltips = {}
#		self.__cell_data = {}
#		self.__prev_row = None
#		self.__prev_col = None
#		self.__date_format = str((_('lab_grid_date_format::%Y\n%b %d')).lstrip('lab_grid_date_format::'))

		self.__init_ui()
		#self.__register_events()
	#------------------------------------------------------------
	# external API
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
			# FIXME: check for None
			self.SetCellValue(row_idx, 0, med['substance'])
			self.SetCellValue(row_idx, 1, med['strength'])
			self.SetCellValue(row_idx, 2, med['schedule'])
			self.SetCellValue(row_idx, 3, med['started'].strftime('%x'))
			self.SetCellValue(row_idx, 4, unicode(med['duration']))
			#self.SetCellValue(row_idx, 0, med[''])

			#self.SetCellAlignment(row, col, horiz = wx.ALIGN_RIGHT, vert = wx.ALIGN_CENTRE)

	#------------------------------------------------------------
	def empty_grid(self):
		self.BeginBatch()
		self.ClearGrid()
		# Windows cannot do nothing, it rather decides to assert()
		# on thinking it is supposed to do nothing
		if self.GetNumberRows() > 0:
			self.DeleteRows(pos = 0, numRows = self.GetNumberRows())
		#if self.GetNumberCols() > 0:
		#	self.DeleteCols(pos = 0, numCols = self.GetNumberCols())
		self.EndBatch()
		#self.__cell_tooltips = {}
		#self.__cell_data = {}
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
# Revision 1.3  2009-06-10 21:02:34  ncq
# - update-atc-reference-data
#
# Revision 1.2  2009/05/13 12:20:59  ncq
# - improve and streamline
#
# Revision 1.1  2009/05/12 12:04:01  ncq
# - substance intake handling
#
#