#!/usr/bin/python
#=====================================================
#
#=====================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gui/gmScanIdxMedDocsPlugin.py,v $
__version__ = "$Revision: 1.3 $"
__author__ = "Sebastian Hilbert <Sebastian.Hilbert@gmx.net>\
              Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL"

try:
    import wxversion
    import wx
except ImportError:
    from wxPython import wx

import os, time, shutil, os.path

from Gnumed.pycommon import gmLog
_log = gmLog.gmDefLog
if __name__ == '__main__':
    _log.SetAllLogLevels(gmLog.lData)

from Gnumed.wxpython import gmPlugin, gmMedDocWidgets
#====================================

class gmScanIdxMedDocsPlugin(gmPlugin.cNotebookPlugin):
	"""Plugin to encapsulate patient scan index documents window."""

	tab_name = _('Associate Documents')

	def name(self):
		return gmScanIdxMedDocsPlugin.tab_name

	def GetWidget(self, parent):
		self._widget = gmMedDocWidgets.cScanIdxDocsPnl(parent, -1)
		return self._widget

	def MenuInfo(self):
		return ('patient', _('associate documents'))

	def can_receive_focus(self):
		# need patient
		if not self._verify_patient_avail():
			return None
		return 1
#======================================================================
# $Log:
# Revision 
