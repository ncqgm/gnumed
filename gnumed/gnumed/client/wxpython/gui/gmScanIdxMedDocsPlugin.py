#=====================================================
# GNUmed scan and index plugin
#=====================================================
__version__ = "$Revision: 1.8 $"
__author__ = "Sebastian Hilbert <Sebastian.Hilbert@gmx.net>\
              Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL"

from Gnumed.wxpython import gmPlugin, gmDocumentWidgets

#====================================
class gmScanIdxMedDocsPlugin(gmPlugin.cNotebookPlugin):
	"""Plugin to encapsulate patient scan index documents window."""

	tab_name = _('Attach documents')

	def name(self):
		return gmScanIdxMedDocsPlugin.tab_name

	def GetWidget(self, parent):
		self._widget = gmDocumentWidgets.cScanIdxDocsPnl(parent, -1)
		return self._widget

	def MenuInfo(self):
		return ('emr', _('&Attach documents'))

	def can_receive_focus(self):
		# need patient
		if not self._verify_patient_avail():
			return None
		return 1
#======================================================================
