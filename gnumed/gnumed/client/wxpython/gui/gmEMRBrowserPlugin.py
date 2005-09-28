#======================================================================
# GnuMed patient EMR browser plugin
# ----------------------------------------------
#
# this plugin holds patient EMR tree
#
# @copyright: author
#======================================================================
__version__ = "$Revision: 1.8 $"
__author__ = "Carlos Moro"
__license__ = 'GPL (details at http://www.gnu.org)'

from Gnumed.wxpython import gmPlugin, gmEMRBrowser
from Gnumed.pycommon import gmLog

_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)

#======================================================================
class gmEMRBrowserPlugin(gmPlugin.cNotebookPlugin):
	"""Plugin to encapsulate patient EMR browser window."""

	tab_name = _('EMR tree')

	def name(self):
		return gmEMRBrowserPlugin.tab_name

	def GetWidget(self, parent):
		self._widget = gmEMRBrowser.cEMRBrowserPanel(parent, -1)
		return self._widget

	def MenuInfo(self):
		return ('emr_show', _('tree view'))

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

    try:
        import wxversion
        import wx
    except ImportError:
        from wxPython import wx

    from Gnumed.pycommon import gmPG, gmCfg
    from Gnumed.exporters import gmPatientExporter
    from Gnumed.business import gmPerson

    _cfg = gmCfg.gmDefCfgFile	
	
    _log.Log (gmLog.lInfo, "starting emr browser plugin...")

    if _cfg is None:
        _log.Log(gmLog.lErr, "Cannot run without config file.")
        sys.exit("Cannot run without config file.")

    try:
        # make sure we have a db connection
        gmPG.set_default_client_encoding('latin1')
        pool = gmPG.ConnectionPool()
        
        # obtain patient
        patient = gmPerson.ask_for_patient()
        if patient is None:
            print "None patient. Exiting gracefully..."
            sys.exit(0)
                    
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
            except:
                print "error cleaning up patient"
    except StandardError:
        _log.LogException("unhandled exception caught !", sys.exc_info(), 1)
        # but re-raise them
        raise
    try:
        pool.StopListeners()
    except:
        _log.LogException('unhandled exception caught', sys.exc_info(), verbose=1)
        raise

    _log.Log (gmLog.lInfo, "closing emr browser plugin...")

#======================================================================
# $Log: gmEMRBrowserPlugin.py,v $
# Revision 1.8  2005-09-28 21:38:11  ncq
# - more 2.6-ification
#
# Revision 1.7  2005/09/26 18:01:52  ncq
# - use proper way to import wx26 vs wx2.4
# - note: THIS WILL BREAK RUNNING THE CLIENT IN SOME PLACES
# - time for fixup
#
# Revision 1.6  2005/06/07 20:56:56  ncq
# - take advantage of improved EMR menu
#
# Revision 1.5  2005/03/29 07:33:47  ncq
# - fix naming
#
# Revision 1.4  2005/03/11 22:53:37  ncq
# - ask_for_patient() is now in gmPerson
#
# Revision 1.3  2004/10/31 00:35:40  cfmoro
# Fixed some method names. Added sys import. Refesh browser at startup in standalone mode
#
# Revision 1.2  2004/09/25 13:12:15  ncq
# - switch to from wxPython import wx
#
# Revision 1.1  2004/09/06 18:59:18  ncq
# - Carlos wrote a plugin wrapper for us
#
