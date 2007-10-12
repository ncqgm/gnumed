#======================================================================
# GnuMed patient EMR Journal plugin
# ----------------------------------------------
#
# @copyright: author
#======================================================================
__version__ = "$Revision: 1.9 $"
__author__ = "Karsten Hilbert"
__license__ = 'GPL (details at http://www.gnu.org)'

from Gnumed.wxpython import gmPlugin, gmEMRBrowser
from Gnumed.pycommon import gmLog, gmI18N

_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)

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
		return ('emr_show', _('chronological journal'))

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

    from Gnumed.pycommon import gmCfg
    from Gnumed.exporters import gmPatientExporter
    from Gnumed.business import gmPerson

    _cfg = gmCfg.gmDefCfgFile	
	
    _log.Log (gmLog.lInfo, "starting emr journal plugin...")

    if _cfg is None:
        _log.Log(gmLog.lErr, "Cannot run without config file.")
        sys.exit("Cannot run without config file.")

    try:
        # obtain patient
        patient = gmPerson.ask_for_patient()
        if patient is None:
            print "None patient. Exiting gracefully..."
            sys.exit(0)
        gmPerson.set_active_patient(patient=patient)
                    
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
        _log.LogException("unhandled exception caught !", sys.exc_info(), 1)
        # but re-raise them
        raise

    _log.Log (gmLog.lInfo, "closing emr journal plugin...")

#======================================================================
# $Log: gmEMRJournalPlugin.py,v $
# Revision 1.9  2007-10-12 07:28:24  ncq
# - lots of import related cleanup
#
# Revision 1.8  2006/10/31 16:06:19  ncq
# - no more gmPG
#
# Revision 1.7  2006/10/25 07:23:30  ncq
# - no gmPG no more
#
# Revision 1.6  2006/05/04 09:49:20  ncq
# - get_clinical_record() -> get_emr()
# - adjust to changes in set_active_patient()
# - need explicit set_active_patient() after ask_for_patient() if wanted
#
# Revision 1.5  2005/12/27 19:05:36  ncq
# - use gmI18N
#
# Revision 1.4  2005/10/03 13:59:59  sjtan
# indentation errors
#
# Revision 1.3  2005/09/26 18:01:52  ncq
# - use proper way to import wx26 vs wx2.4
# - note: THIS WILL BREAK RUNNING THE CLIENT IN SOME PLACES
# - time for fixup
#
# Revision 1.2  2005/06/07 20:56:56  ncq
# - take advantage of improved EMR menu
#
# Revision 1.1  2005/04/12 16:26:33  ncq
# - added Journal style EMR display plugin
#
