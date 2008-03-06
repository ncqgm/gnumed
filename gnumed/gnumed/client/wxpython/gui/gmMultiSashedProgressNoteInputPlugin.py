#======================================================================
# GnuMed multisash based progress note input plugin
# -------------------------------------------------
#
# this plugin displays the list of patient problems
# toghether whith a multisash container for progress notes
#
# @copyright: author
#======================================================================
__version__ = "$Revision: 1.13 $"
__author__ = "Carlos Moro, Karsten Hilbert"
__license__ = 'GPL (details at http://www.gnu.org)'

import logging


from Gnumed.wxpython import gmPlugin, gmSOAPWidgets


_log = logging.getLogger('gm.ui')
_log.info(__version__)
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

	import wx

    from Gnumed.business import gmPerson

    _log.info("starting multisashed progress notes input plugin...")

    try:
        # make sure we have a db connection
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
        _log.exception("unhandled exception caught !")
        # but re-raise them
        raise
    try:
        pool.StopListeners()
    except:
        _log.exception('unhandled exception caught')
        raise

    _log.info("closing multisashed progress notes input plugin...")

#======================================================================
# $Log: gmMultiSashedProgressNoteInputPlugin.py,v $
# Revision 1.13  2008-03-06 18:32:31  ncq
# - standard lib logging only
#
# Revision 1.12  2008/01/27 21:21:59  ncq
# - no more gmCfg
#
# Revision 1.11  2007/10/12 07:28:25  ncq
# - lots of import related cleanup
#
# Revision 1.10  2007/03/08 11:54:44  ncq
# - cleanup
#
# Revision 1.9  2006/10/25 07:23:30  ncq
# - no gmPG no more
#
# Revision 1.8  2006/05/04 09:49:20  ncq
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
