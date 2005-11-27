#=====================================================
# GNUmed scan and index plugin
#=====================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gui/gmScanIdxMedDocsPlugin.py,v $
__version__ = "$Revision: 1.4 $"
__author__ = "Sebastian Hilbert <Sebastian.Hilbert@gmx.net>\
              Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL"

try:
    import wxversion
    import wx
except ImportError:
    from wxPython import wx

from Gnumed.wxpython import gmPlugin, gmMedDocWidgets
from Gnumed.pycommon import gmLog
_log = gmLog.gmDefLog

#====================================
class gmScanIdxMedDocsPlugin(gmPlugin.cNotebookPlugin):
	"""Plugin to encapsulate patient scan index documents window."""

	tab_name = _('Import Documents')

	def name(self):
		return gmScanIdxMedDocsPlugin.tab_name

	def GetWidget(self, parent):
		self._widget = gmMedDocWidgets.cScanIdxDocsPnl(parent, -1)
		return self._widget

	def MenuInfo(self):
		return ('patient', _('import documents'))

	def can_receive_focus(self):
		# need patient
		if not self._verify_patient_avail():
			return None
		return 1
#======================================================================
# $Log: gmScanIdxMedDocsPlugin.py,v $
# Revision 1.4  2005-11-27 12:46:42  ncq
# - cleanup
#
#
