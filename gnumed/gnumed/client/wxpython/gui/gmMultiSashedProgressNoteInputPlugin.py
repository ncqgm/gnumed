#======================================================================
# GnuMed multisash based progress note input plugin
# -------------------------------------------------
#
# this plugin displays the list of patient problems
# toghether whith a multisash container for progress notes
#
# @copyright: author
#======================================================================
__version__ = "$Revision: 1.8 $"
__author__ = "Carlos Moro, Karsten Hilbert"
__license__ = 'GPL (details at http://www.gnu.org)'

from Gnumed.wxpython import gmPlugin, gmSOAPWidgets
from Gnumed.pycommon import gmLog

_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)

#======================================================================
class gmMultiSashedProgressNoteInputPlugin(gmPlugin.cNotebookPlugin):
	"""Plugin to encapsulate multisash based progress note input window."""

	tab_name = _('progress notes (sash)')

	def name (self):
		return gmMultiSashedProgressNoteInputPlugin.tab_name

	def GetWidget (self, parent):
		self._widget = gmSOAPWidgets.cMultiSashedProgressNoteInputPanel(parent, -1)
		return self._widget

	def MenuInfo (self):
		return ('tools', _('progress notes'))

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
    from Gnumed.business import gmPerson

    _cfg = gmCfg.gmDefCfgFile	
	
    _log.Log (gmLog.lInfo, "starting multisashed progress notes input plugin...")

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
                    
        # display standalone multisash progress notes input
        application = wx.wxPyWidgetTester(size=(800,600))
        multisash_notes = gmSOAPWidgets.cMultiSashedProgressNoteInputPanel(application.frame, -1)
        
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

    _log.Log (gmLog.lInfo, "closing multisashed progress notes input plugin...")

#======================================================================
# $Log: gmMultiSashedProgressNoteInputPlugin.py,v $
# Revision 1.8  2006-05-04 09:49:20  ncq
# - get_clinical_record() -> get_emr()
# - adjust to changes in set_active_patient()
# - need explicit set_active_patient() after ask_for_patient() if wanted
#
# Revision 1.7  2005/09/26 18:01:52  ncq
# - use proper way to import wx26 vs wx2.4
# - note: THIS WILL BREAK RUNNING THE CLIENT IN SOME PLACES
# - time for fixup
#
# Revision 1.6  2005/05/12 15:13:28  ncq
# - cleanup
#
# Revision 1.5  2005/05/08 21:44:08  ncq
# - cleanup
#
# Revision 1.4  2005/03/29 07:34:20  ncq
# - improve naming
#
# Revision 1.3  2005/03/18 16:48:42  cfmoro
# Fixes to integrate multisash notes input plugin in wxclient
#
# Revision 1.2  2005/03/16 18:37:57  cfmoro
# Log cvs history
#
