#======================================================================
# GNUmed current substances plugin
#
# @copyright: author
#======================================================================
__version__ = "$Revision: 1.1 $"
__author__ = "Karsten Hilbert"
__license__ = 'GPL (details at http://www.gnu.org)'

import logging


from Gnumed.wxpython import gmPlugin, gmMedicationWidgets
from Gnumed.pycommon import gmI18N


_log = logging.getLogger('gm.ui')
_log.info(__version__)
#======================================================================
class gmCurrentSubstancesPlugin(gmPlugin.cNotebookPlugin):
	"""Plugin to encapsulate patient current medication list."""

	tab_name = _('Substances')

	def name (self):
		return gmCurrentSubstancesPlugin.tab_name

	def GetWidget (self, parent):
		self._widget = gmMedicationWidgets.cCurrentSubstancesPnl(parent, -1)
		return self._widget

	def MenuInfo (self):
		return ('emr', _('Current medications'))

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
# Revision 1.1  2009-05-12 12:04:21  ncq
# - a plugin to show current medication
#
#