#======================================================================
# GNUmed patient EMR Journal plugin
#======================================================================
__author__ = "Karsten Hilbert"
__license__ = 'GPL v2 or later (details at http://www.gnu.org)'

import logging


from Gnumed.pycommon import gmI18N
from Gnumed.wxpython import gmPlugin
from Gnumed.wxpython import gmEMRBrowser
from Gnumed.wxpython import gmAccessPermissionWidgets

_log = logging.getLogger('gm.ui')

#======================================================================
class gmEMRJournalPlugin(gmPlugin.cNotebookPlugin):
	"""Plugin to encapsulate patient EMR Journal window."""

	tab_name = _('EMR journal')
	required_minimum_role = 'doctor'

	def name (self):
		return gmEMRJournalPlugin.tab_name

	@gmAccessPermissionWidgets.verify_minimum_required_role (
		required_minimum_role,
		activity = _('loading plugin <%s>') % tab_name,
		return_value_on_failure = False,
		fail_silently = False
	)
	def register(self):
		gmPlugin.cNotebookPlugin.register(self)
	#-------------------------------------------------
	def GetWidget (self, parent):
		self._widget = gmEMRBrowser.cEMRJournalPluginPnl(parent, -1)
		return self._widget

	def MenuInfo (self):
		return ('emr', _('EMR &Journal (chronological)'))

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

    from Gnumed.exporters import gmPatientExporter
    from Gnumed.business import gmPersonSearch

    _log.info("starting emr journal plugin...")

    try:
        # obtain patient
        patient = gmPersonSearch.ask_for_patient()
        if patient is None:
            print "None patient. Exiting gracefully..."
            sys.exit(0)
        gmPatSearchWidgets.set_active_patient(patient=patient)

        # display standalone browser
        application = wx.wxPyWidgetTester(size=(800,600))
        emr_journal = gmEMRBrowser.cEMRJournalPluginPnl(application.frame, -1)
        emr_journal.refresh_journal()

        application.frame.Show(True)
        application.MainLoop()

        # clean up
        if patient is not None:
            try:
                patient.cleanup()
            except:
                print "error cleaning up patient"
    except StandardError:
        _log.exception("unhandled exception caught !")
        # but re-raise them
        raise

    _log.info("closing emr journal plugin...")

#======================================================================
