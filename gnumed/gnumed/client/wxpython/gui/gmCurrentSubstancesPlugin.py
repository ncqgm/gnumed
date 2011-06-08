#======================================================================
# GNUmed current substances plugin
#
# @copyright: author
#======================================================================
__version__ = "$Revision: 1.3 $"
__author__ = "Karsten Hilbert"
__license__ = 'GPL v2 or later (details at http://www.gnu.org)'

import logging


from Gnumed.wxpython import gmPlugin, gmMedicationWidgets
from Gnumed.pycommon import gmI18N


_log = logging.getLogger('gm.ui')
_log.info(__version__)
#======================================================================
class gmCurrentSubstancesPlugin(gmPlugin.cNotebookPlugin):
	"""Plugin to encapsulate patient current medication list."""

	tab_name = _('Medication')

	def name (self):
		return gmCurrentSubstancesPlugin.tab_name

	def GetWidget (self, parent):
		self._widget = gmMedicationWidgets.cCurrentSubstancesPnl(parent, -1)
		return self._widget

	def MenuInfo (self):
		return ('emr', _('Current &medication'))

	def can_receive_focus(self):
		if not self._verify_patient_avail():
			return None
		return 1
#======================================================================
# main
#----------------------------------------------------------------------
if __name__ == "__main__":
	print "no test code"

#======================================================================
# $Log: gmCurrentSubstancesPlugin.py,v $
# Revision 1.3  2009-12-25 22:08:24  ncq
# - rename to "Medication"
#
# Revision 1.2  2009/06/29 15:13:25  ncq
# - improved placement in menu hierarchy
# - add active letters
#
# Revision 1.1  2009/05/12 12:04:21  ncq
# - a plugin to show current medication
#
#