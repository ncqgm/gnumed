"""GnuMed demographics editor plugin
"""
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gui/Attic/gmDemographicsEditor.py,v $
__version__ = "$Revision: 1.8 $"
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
#================================================================
import sys

from Gnumed.pycommon import gmLog
from Gnumed.wxpython import gmPlugin, gmDemographics
from Gnumed.business import gmDemographicRecord

gmLog.gmDefLog.Log(gmLog.lData, __version__)

from wxPython.wx import *

if __name__ == '__main__':
	_ = lambda x:x
#================================================================
class gmDemographicsEditor(gmPlugin.wxNotebookPlugin):
	tab_name = _("Patient Details")

	def name (self):
		return gmDemographicsEditor.tab_name

	def GetWidget (self, parent):
		try:
			self._widget = gmDemographics.PatientsPanel( parent, -1)
		except:
			gmLog.gmDefLog.LogException("failed to instantiate gmDemographics.PatientsPanel", sys.exc_info(), verbose=1)
			return None
		return self._widget

	def MenuInfo (self):
		return ('tools', _("editor for demographics"))

	def can_receive_focus(self):
		# need patient (unless we use this as a first-off patient input widget)
	#	if not self._verify_patient_avail():
	#		return None
		return 1

	# FIXME: I can't see why we'd need this ?
#	def newPatient(self):
#		self._widget.newPatient()

#================================================================
# MAIN
#----------------------------------------------------------------
if __name__ == '__main__':
	# catch all remaining exceptions
	try:
		application = wxPyWidgetTester(gmDemographicsEditorPlugin, (640,400))
		application.MainLoop()
	except StandardError:
		_log.LogException("unhandled exception caught !", sys.exc_info(), verbose=1)
		# but re-raise them
		raise

#================================================================

# $Log: gmDemographicsEditor.py,v $
# Revision 1.8  2004-06-20 16:50:51  ncq
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
# Revision 1.5  2004/03/07 22:05:08  ncq
# - some cleanup
#
# Revision 1.4  2004/03/07 13:19:18  ihaywood
# more work on forms
#
# Revision 1.3  2004/02/25 09:46:22  ncq
# - import from pycommon now, not python-common
#
# Revision 1.2  2004/02/18 06:30:30  ihaywood
# Demographics editor now can delete addresses
# Contacts back up on screen.
#
# Revision 1.1  2003/11/17 11:04:34  sjtan
#
# added.
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
