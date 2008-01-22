#=====================================================
# GNUmed scan and index plugin
#=====================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gui/gmScanIdxMedDocsPlugin.py,v $
__version__ = "$Revision: 1.6 $"
__author__ = "Sebastian Hilbert <Sebastian.Hilbert@gmx.net>\
              Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL"

from Gnumed.wxpython import gmPlugin, gmMedDocWidgets

#====================================
class gmScanIdxMedDocsPlugin(gmPlugin.cNotebookPlugin):
	"""Plugin to encapsulate patient scan index documents window."""

	tab_name = _('Import documents')

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
# Revision 1.6  2008-01-22 12:26:24  ncq
# - better tab names
#
# Revision 1.5  2007/10/12 07:28:25  ncq
# - lots of import related cleanup
#
# Revision 1.4  2005/11/27 12:46:42  ncq
# - cleanup
#
#
