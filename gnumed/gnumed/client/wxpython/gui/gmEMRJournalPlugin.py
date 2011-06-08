#======================================================================
# GNUmed patient EMR Journal plugin
# ----------------------------------------------
#
# @copyright: author
#======================================================================
__version__ = "$Revision: 1.15 $"
__author__ = "Karsten Hilbert"
__license__ = 'GPL v2 or later (details at http://www.gnu.org)'

import logging


from Gnumed.wxpython import gmPlugin, gmEMRBrowser
from Gnumed.pycommon import gmI18N

_log = logging.getLogger('gm.ui')
_log.info(__version__)

#======================================================================
class gmEMRJournalPlugin(gmPlugin.cNotebookPlugin):
	"""Plugin to encapsulate patient EMR Journal window."""

	tab_name = _('EMR journal')

	def name (self):
		return gmEMRJournalPlugin.tab_name

	def GetWidget (self, parent):
		self._widget = gmEMRBrowser.cEMRJournalPanel(parent, -1)
		return self._widget

	def MenuInfo (self):
		#return ('emr_show', _('Chronological &journal'))
		return ('emr', _('Chronological &journal'))

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
        emr_journal = gmEMRBrowser.cEMRJournalPanel(application.frame, -1)
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
