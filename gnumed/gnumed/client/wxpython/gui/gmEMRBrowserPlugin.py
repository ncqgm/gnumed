#======================================================================
# GnuMed patient EMR browser plugin
# ----------------------------------------------
#
# this plugin holds patient EMR tree
#
# @copyright: author
#======================================================================
__version__ = "$Revision: 1.16 $"
__author__ = "Carlos Moro"
__license__ = 'GPL (details at http://www.gnu.org)'

import logging


from Gnumed.wxpython import gmPlugin, gmEMRBrowser
from Gnumed.pycommon import gmI18N

_log = logging.getLogger('gm.ui')
_log.info(__version__)

#======================================================================
class gmEMRBrowserPlugin(gmPlugin.cNotebookPlugin):
	"""Plugin to encapsulate patient EMR browser window."""

	tab_name = _('EMR tree')

	def name(self):
		return gmEMRBrowserPlugin.tab_name
	#-------------------------------------------------
	def GetWidget(self, parent):
		self._widget = gmEMRBrowser.cSplittedEMRTreeBrowserPnl(parent, -1)
#		self._widget = gmEMRBrowser.cEMRBrowserPanel(parent, -1)
#		self._widget = gmEMRBrowser.cScrolledEMRTreePnl(parent, -1)
#		from Gnumed.wxpython import gmMedDocWidgets
#		self._widget = gmMedDocWidgets.cSelectablySortedDocTreePnl(parent, -1)
		return self._widget
	#-------------------------------------------------
	def MenuInfo(self):
		return ('emr_show', _('tree view'))
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

    from Gnumed.exporters import gmPatientExporter
    from Gnumed.business import gmPerson

    _log.info("starting emr browser plugin...")

    try:
        # obtain patient
        patient = gmPerson.ask_for_patient()
        if patient is None:
            print "None patient. Exiting gracefully..."
            sys.exit(0)
        gmPerson.set_active_patient(patient=patient)
                    
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
        _log.exception("unhandled exception caught !")
        # but re-raise them
        raise

    _log.info("closing emr browser plugin...")

#======================================================================
# $Log: gmEMRBrowserPlugin.py,v $
# Revision 1.16  2008-03-06 18:32:30  ncq
# - standard lib logging only
#
# Revision 1.15  2008/01/27 21:21:59  ncq
# - no more gmCfg
#
# Revision 1.14  2007/10/12 07:28:24  ncq
# - lots of import related cleanup
#
# Revision 1.13  2006/10/31 16:06:19  ncq
# - no more gmPG
#
# Revision 1.12  2006/10/25 07:23:30  ncq
# - no gmPG no more
#
# Revision 1.11  2006/05/28 16:18:52  ncq
# - use new splitter plugin class
#
# Revision 1.10  2006/05/04 09:49:20  ncq
# - get_clinical_record() -> get_emr()
# - adjust to changes in set_active_patient()
# - need explicit set_active_patient() after ask_for_patient() if wanted
#
# Revision 1.9  2005/12/27 19:05:36  ncq
# - use gmI18N
#
# Revision 1.8  2005/09/28 21:38:11  ncq
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
