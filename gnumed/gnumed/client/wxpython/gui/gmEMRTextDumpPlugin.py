"""GnuMed simple EMR text dump plugin
"""
#================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gui/Attic/gmEMRTextDumpPlugin.py,v $
__version__ = "$Revision: 1.5 $"
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"

from Gnumed.pycommon import gmLog
from Gnumed.wxpython import gmEMRTextDump, gmPlugin

from wxPython.wx import *

_log = gmLog.gmDefLog
_log.Log(gmLog.lData, __version__)
#================================================================
class gmEMRTextDumpPlugin(gmPlugin.wxNotebookPlugin):
	tab_name = _("EMR dump")

	def name (self):
		return gmEMRTextDumpPlugin.tab_name

	def GetWidget (self, parent):
		self.panel = gmEMRTextDump.gmEMRDumpPanel(parent, -1)
		return self.panel

	def MenuInfo (self):
		return ('tools', _("simple EMR text viewer"))

	def ReceiveFocus(self):
		pass

	def can_receive_focus(self):
		# need patient
		if not self._verify_patient_avail():
			return None
		return 1
#================================================================
# MAIN
#----------------------------------------------------------------
if __name__ == '__main__':
	# catch all remaining exceptions
	try:
		application = wxPyWidgetTester(size=(640,480))
		application.SetWidget(cStandalonePanel,-1)
		application.MainLoop()
	except StandardError:
		_log.LogException("unhandled exception caught !", sys.exc_info(), verbose=1)
		# but re-raise them
		raise

#================================================================
# $Log: gmEMRTextDumpPlugin.py,v $
# Revision 1.5  2004-03-09 10:53:14  ncq
# - cleanup
#
# Revision 1.4  2004/03/09 10:12:01  shilbert
# - adapt to new API from Gnumed.foo import bar
#
# Revision 1.3  2003/11/17 10:56:40  sjtan
#
# synced and commiting.
#
# Revision 1.1  2003/10/23 06:02:40  sjtan
#
# manual edit areas modelled after r.terry's specs.
#
# Revision 1.2  2003/07/19 20:22:22  ncq
# - use panel now, not scrolled window anymore
#
# Revision 1.1  2003/07/03 15:26:26  ncq
# - first checkin
#
