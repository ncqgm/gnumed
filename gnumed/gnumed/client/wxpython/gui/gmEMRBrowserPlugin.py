# -*- coding: utf-8 -*-

"""GNUmed patient EMR browser plugin

this plugin holds patient EMR tree"""

#======================================================================
__author__ = "Carlos Moro"
__license__ = 'GPL v2 or later (details at https://www.gnu.org)'

import logging


from Gnumed.wxpython import gmPlugin
from Gnumed.wxpython import gmEMRBrowser
from Gnumed.wxpython import gmAccessPermissionWidgets

_log = logging.getLogger('gm.ui')
if __name__ == '__main__':
	_ = lambda x:x

#======================================================================
class gmEMRBrowserPlugin(gmPlugin.cNotebookPlugin):
	"""Plugin to encapsulate patient EMR browser window."""

	tab_name = _('EMR Tree')
	required_minimum_role = 'full clinical access'

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
		return gmEMRBrowserPlugin.tab_name
	#-------------------------------------------------
	def GetWidget(self, parent):
		self._widget = gmEMRBrowser.cSplittedEMRTreeBrowserPnl(parent, -1)
		return self._widget
	#-------------------------------------------------
	def MenuInfo(self):
		return ('emr', _('EMR &Tree'))
	#-------------------------------------------------
	def can_receive_focus(self):
		# need patient
		if not self._verify_patient_avail():
			return None
		return 1

#======================================================================
# main
#----------------------------------------------------------------------
if __name__ == "__main__":

    import sys

    import wx

    from Gnumed.business import gmPersonSearch
    from Gnumed.wxpython import gmPatSearchWidgets

    _log.info("starting emr browser plugin...")

    # obtain patient
    patient = gmPersonSearch.ask_for_patient()
    if patient is None:
        print("None patient. Exiting gracefully...")
        sys.exit(0)
    gmPatSearchWidgets.set_active_patient(patient=patient)

    # display standalone browser
    application = wx.wxPyWidgetTester(size=(800,600))
    emr_browser = gmEMRBrowser.cEMRBrowserPanel(application.frame, -1)
    emr_browser.refresh_tree()

    application.frame.Show(True)
    application.MainLoop()

    # clean up
    if patient is not None:
        try:
            patient.cleanup()
        except Exception:
            print("error cleaning up patient")

    _log.info("closing emr browser plugin...")

#======================================================================
