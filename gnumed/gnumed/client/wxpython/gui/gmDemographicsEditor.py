"""GnuMed simple EMR text dump plugin
"""
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gui/Attic/gmDemographicsEditor.py,v $
__version__ = "$Revision: 1.4 $"
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
#================================================================
import sys
if __name__ == "__main__":
	sys.path.append('../business')
	sys.path.append('../pycommon')
	sys.path.append('patient')

import Gnumed.pycommon.gmLog as gmLog
import Gnumed.wxpython.gmPlugin as gmPlugin
import Gnumed.business.gmDemographicRecord as gmDemographicRecord
import Gnumed.wxpython.gmDemographics as gmDemographics

gmLog.gmDefLog.Log(gmLog.lData, __version__)

from wxPython.wx import *
#================================================================
class gmDemographicsEditor(gmPlugin.wxNotebookPlugin):
	tab_name = _("Patient Details")

	def name (self):
		return gmDemographicsEditor.tab_name

	def GetWidget (self, parent):
	#	print "((((((((( gmDEMO"
		try:
			self.panel = gmDemographics.PatientsPanel( parent, -1)

		except:
	#		print "UNABLE TO GET gmDemographics instance"
			gmLog.gmDefLog.LogException("failed to instantiate gmDemographics.PatientsPanel", sys.exc_info(), verbose=1)
		return self.panel

	def MenuInfo (self):
		return ('tools', _("editor for demographics"))

	def ReceiveFocus(self):
		pass

	def can_receive_focus(self):
		# need patient
	#	if not self._verify_patient_avail():
	#		return None
		return 1

	def newPatient(self):
		self.panel.newPatient()

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
# Revision 1.4  2004-03-07 13:19:18  ihaywood
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
