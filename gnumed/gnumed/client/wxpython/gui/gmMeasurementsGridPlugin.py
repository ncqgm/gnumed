#======================================================================
# GNUmed patient measurements plugin
#
# @copyright: author
#======================================================================
__version__ = "$Revision: 1.2 $"
__author__ = "Karsten Hilbert"
__license__ = 'GPL (details at http://www.gnu.org)'

import logging


from Gnumed.wxpython import gmPlugin, gmMeasurementWidgets
from Gnumed.pycommon import gmI18N


_log = logging.getLogger('gm.ui')
_log.info(__version__)
#======================================================================
class gmMeasurementsGridPlugin(gmPlugin.cNotebookPlugin):
	"""Plugin to encapsulate patient measurements."""

	tab_name = _('Measurements')

	def name (self):
		return gmMeasurementsGridPlugin.tab_name

	def GetWidget (self, parent):
		self._widget = gmMeasurementWidgets.cMeasurementsPnl(parent, -1)
		return self._widget

	def MenuInfo (self):
		return ('emr', _('&Measurements overview'))

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
# $Log: gmMeasurementsGridPlugin.py,v $
# Revision 1.2  2008-06-24 14:01:02  ncq
# - improved menu item label
#
# Revision 1.1  2008/03/25 19:33:15  ncq
# - new plugin
#
#