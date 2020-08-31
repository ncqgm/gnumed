# -*- coding: utf-8 -*-

"""GNUmed scan and index plugin"""

#=====================================================
__author__ = "Sebastian Hilbert <Sebastian.Hilbert@gmx.net>\
              Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL"

from Gnumed.wxpython import gmPlugin, gmDocumentWidgets
from Gnumed.wxpython import gmAccessPermissionWidgets

if __name__ == '__main__':
	_ = lambda x:x
#====================================
class gmScanIdxMedDocsPlugin(gmPlugin.cNotebookPlugin):
	"""Plugin to encapsulate patient scan index documents window."""

	tab_name = _('Attach documents')
	required_minimum_role = 'non-clinical access'

	@gmAccessPermissionWidgets.verify_minimum_required_role (
		required_minimum_role,
		activity = _('loading plugin <%s>') % tab_name,
		return_value_on_failure = False,
		fail_silently = False
	)
	def register(self):
		gmPlugin.cNotebookPlugin.register(self)
	#-------------------------------------------------

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
