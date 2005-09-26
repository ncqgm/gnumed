"""GnuMed simple EMR text dump plugin
"""
#================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gui/Attic/gmEMRTextDumpPlugin.py,v $
__version__ = "$Revision: 1.12 $"
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"

from Gnumed.pycommon import gmLog, gmI18N
from Gnumed.wxpython import gmEMRTextDump, gmPlugin

try:
	import wxversion
	import wx
except ImportError:
	from wxPython import wx

_log = gmLog.gmDefLog
_log.Log(gmLog.lData, __version__)
#================================================================
class gmEMRTextDumpPlugin(gmPlugin.cNotebookPluginOld):
	tab_name = _("EMR dump")

	def name (self):
		return gmEMRTextDumpPlugin.tab_name

	def GetWidget (self, parent):
		self._widget = gmEMRTextDump.gmEMRDumpPanel(parent, -1)
		return self._widget

	def MenuInfo (self):
		return ('tools', _("simple EMR text viewer"))

	def populate_with_data(self):
		# no use reloading if invisible
		if self.gb['main.notebook.raised_plugin'] != self.__class__.__name__:
			return 1
		self._widget.populate()
		return 1

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
# Revision 1.12  2005-09-26 18:01:52  ncq
# - use proper way to import wx26 vs wx2.4
# - note: THIS WILL BREAK RUNNING THE CLIENT IN SOME PLACES
# - time for fixup
#
# Revision 1.11  2004/08/04 17:16:02  ncq
# - wxNotebookPlugin -> cNotebookPlugin
# - derive cNotebookPluginOld from cNotebookPlugin
# - make cNotebookPluginOld warn on use and implement old
#   explicit "main.notebook.raised_plugin"/ReceiveFocus behaviour
# - ReceiveFocus() -> receive_focus()
#
# Revision 1.10  2004/07/15 14:40:05  ncq
# - cautiously move back to notebook plugin style
#
# Revision 1.8  2004/06/20 16:50:51  ncq
# - carefully fool epydoc
#
# Revision 1.7  2004/06/20 06:49:21  ihaywood
# changes required due to Epydoc's OCD
#
# Revision 1.6  2004/06/13 22:31:49  ncq
# - gb['main.toolbar'] -> gb['main.top_panel']
# - self.internal_name() -> self.__class__.__name__
# - remove set_widget_reference()
# - cleanup
# - fix lazy load in _on_patient_selected()
# - fix lazy load in ReceiveFocus()
# - use self._widget in self.GetWidget()
# - override populate_with_data()
# - use gb['main.notebook.raised_plugin']
#
# Revision 1.5  2004/03/09 10:53:14  ncq
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
