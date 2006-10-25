#======================================================================
# GnuMed notebook based patient edition plugin
# ------------------------------------------------
#
# this plugin displays a notebook container for patient edition
# current pages (0.1): identity, contacts, occupation
#
# @copyright: author
#======================================================================
__version__ = "$Revision: 1.6 $"
__author__ = "Carlos Moro, Karsten Hilbert"
__license__ = 'GPL (details at http://www.gnu.org)'

from Gnumed.wxpython import gmPlugin, gmDemographicsWidgets
from Gnumed.pycommon import gmLog

_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)

#======================================================================
class gmNotebookedPatientEditionPlugin(gmPlugin.cNotebookPlugin):
	"""Plugin to encapsulate notebooked patient edition window."""

	tab_name = _('Patient Details')

	def name (self):
		return gmNotebookedPatientEditionPlugin.tab_name

	def GetWidget (self, parent):
		self._widget = gmDemographicsWidgets.cNotebookedPatEditionPanel(parent, -1)
		return self._widget

	def MenuInfo (self):
		return ('patient', _('Edit demographics'))

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

    from Gnumed.pycommon import gmCfg
    from Gnumed.business import gmPerson

    _cfg = gmCfg.gmDefCfgFile	
	
    _log.Log (gmLog.lInfo, "starting Notebooked patient edition plugin...")

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
        gmPerson.set_active_patient(patient=patient)
                    
        # display standalone notebooked patient editor
        application = wx.wxPyWidgetTester(size=(800,600))
        application.SetWidget(gmDemographicsWidgets.cNotebookedPatEditionPanel, -1)
        
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

    _log.Log (gmLog.lInfo, "closing Notebooked progress notes input plugin...")

#======================================================================
# $Log: gmNotebookedPatientEditionPlugin.py,v $
# Revision 1.6  2006-10-25 07:23:30  ncq
# - no gmPG no more
#
# Revision 1.5  2006/05/04 09:49:20  ncq
# - get_clinical_record() -> get_emr()
# - adjust to changes in set_active_patient()
# - need explicit set_active_patient() after ask_for_patient() if wanted
#
# Revision 1.4  2005/10/03 13:49:21  sjtan
# using new wx. temporary debugging to stdout(easier to read). where is rfe ?
#
# Revision 1.3  2005/09/26 18:01:52  ncq
# - use proper way to import wx26 vs wx2.4
# - note: THIS WILL BREAK RUNNING THE CLIENT IN SOME PLACES
# - time for fixup
#
# Revision 1.2  2005/05/26 15:57:03  ncq
# - slightly better strings
#
# Revision 1.1  2005/05/25 22:52:47  cfmoro
# Added notebooked patient edition plugin
#
