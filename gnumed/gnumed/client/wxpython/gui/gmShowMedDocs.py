"""A documents tree plugin."""

__version__ = "$Revision: 1.78 $"
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
#================================================================
import os.path, sys, logging


import wx


from Gnumed.wxpython import gmDocumentWidgets, gmPlugin


_log = logging.getLogger('gm.ui')
_log.info(__version__)
#================================================================
class gmShowMedDocs(gmPlugin.cNotebookPlugin):
	"""Plugin to encapsulate document tree."""

	tab_name = _("Documents")

	def name(self):
		return gmShowMedDocs.tab_name
	#--------------------------------------------------------
	def GetWidget(self, parent):
		self._widget = gmDocumentWidgets.cSelectablySortedDocTreePnl(parent, -1)
		return self._widget
	#--------------------------------------------------------
	def MenuInfo(self):
		return ('emr', _('&Documents'))
	#--------------------------------------------------------
	def can_receive_focus(self):
		# need patient
		if not self._verify_patient_avail():
			return None
		return 1
	#--------------------------------------------------------
	def _on_raise_by_signal(self, **kwds):
		if not gmPlugin.cNotebookPlugin._on_raise_by_signal(self, **kwds):
			return False

		try:
			if kwds['sort_mode'] == 'review':
				self._widget._on_sort_by_review_selected(None)
		except KeyError:
			pass

		return True
#================================================================
# MAIN
#----------------------------------------------------------------
if __name__ == '__main__':
	pass
#================================================================
