"""GnuMed single box SOAP notes plugin.
"""
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gui/Attic/gmSingleBoxSoapPlugin.py,v $
__version__ = "$Revision: 1.3 $"
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
#================================================================
#import os.path, sys, os, re

import gmLog, gmPG, gmTmpPatient, gmPlugin, gmCfg
from gmSingleBoxSOAP import gmSingleBoxSOAPPanel
from gmExceptions import ConstructorError

_log = gmLog.gmDefLog
_log.Log(gmLog.lData, __version__)
_cfg = gmCfg.gmDefCfgFile

from wxPython.wx import *
#================================================================
class gmSingleBoxSoapPlugin(gmPlugin.wxNotebookPlugin):
	tab_name = _("David's SOAP")

	def name (self):
		return gmSingleBoxSoapPlugin.tab_name

	def GetWidget (self, parent):
		self.panel = gmSingleBoxSOAPPanel(parent, -1)
		return self.panel

	def MenuInfo (self):
		return ('tools', _("David's single box SOAP entry"))

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
	if _cfg is None:
		_log.Log(gmLog.lErr, "Cannot run without config file.")
		sys.exit("Cannot run without config file.")

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
# $Log: gmSingleBoxSoapPlugin.py,v $
# Revision 1.3  2003-06-29 15:21:22  ncq
# - add can_receive_focus() on patient not selected
#
# Revision 1.2  2003/06/26 21:41:51  ncq
# - fatal->verbose
#
# Revision 1.1  2003/06/19 16:48:57  ncq
# - this is what David wanted
#
