"""GNUmed patient overview widgets.

copyright: authors
"""
#============================================================
__author__ = "K.Hilbert"
__license__ = "GPL v2 or later (details at http://www.gnu.org)"

import logging, sys


import wx


if __name__ == '__main__':
	sys.path.insert(0, '../../')
#from Gnumed.pycommon import gmTools
#from Gnumed.pycommon import gmMatchProvider
#from Gnumed.pycommon import gmDispatcher
#from Gnumed.business import gmOrganization
#from Gnumed.wxpython import gmListWidgets
#from Gnumed.wxpython import gmEditArea
#from Gnumed.wxpython import gmPhraseWheel
from Gnumed.wxpython import gmRegetMixin
#from Gnumed.wxpython import gmAddressWidgets
#from Gnumed.wxpython import gmGuiHelpers

_log = logging.getLogger('gm.patient')
#============================================================
from Gnumed.wxGladeWidgets import wxgPatientOverviewPnl

class cPatientOverviewPnl(wxgPatientOverviewPnl.wxgPatientOverviewPnl, gmRegetMixin.cRegetOnPaintMixin):

	def __init__(self, *args, **kwargs):
		wxgPatientOverviewPnl.wxgPatientOverviewPnl.__init__(self, *args, **kwargs)
		gmRegetMixin.cRegetOnPaintMixin.__init__(self)

	#-----------------------------------------------------
	# reget-on-paint mixin API
	#-----------------------------------------------------
	# remember to call
	#	self._schedule_data_reget()
	# whenever you learn of data changes from database listener
	# threads, dispatcher signals etc.
	def _populate_with_data(self):
		# fill the UI with data
		print "need to implement _populate_with_data"
		#return False
		return True
	#-----------------------------------------------------

#============================================================
# main
#------------------------------------------------------------
if __name__ == "__main__":

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != u'test':
		sys.exit()

#	from Gnumed.pycommon import gmPG2
#	from Gnumed.pycommon import gmI18N
#	gmI18N.activate_locale()
#	gmI18N.install_domain()

	#--------------------------------------------------------
	#test_org_unit_prw()
