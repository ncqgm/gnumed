# -*- coding: utf-8 -*-
"""This plugin lets you manage laboratory requests
 - add requests
 - keep track of pending requests
 - see import errors
 - review newly imported lab results
"""
#============================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gui/gmLabJournal.py,v $
# $Id: gmLabJournal.py,v 1.40 2008-03-06 18:32:31 ncq Exp $
__version__ = "$Revision: 1.40 $"
__author__ = "Sebastian Hilbert <Sebastian.Hilbert@gmx.net>"

import wx

from Gnumed.pycommon import gmI18N
from Gnumed.wxpython import gmLabWidgets, gmPlugin

_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)

#============================================================
class cPluginPanel(wx.Panel):
	def __init__(self, parent, id):
		# set up widgets
		wx.Panel.__init__(self, parent, id, wxDefaultPosition, wxDefaultSize)

		# make lab notebook
		self.nb = gmLabWidgets.cLabJournalNB(self, -1)

		# just one vertical sizer
		sizer = wx.BoxSizer(wx.VERTICAL)
		szr_nb = wx.NotebookSizer( self.nb )

		sizer.Add(szr_nb, 1, wxEXPAND, 0)
		self.SetAutoLayout(1)
		self.SetSizer(sizer)
		sizer.Fit(self)
		self.Layout()

#------------------------------------------------------------
class gmLabJournal(gmPlugin.cNotebookPluginOld):
	tab_name = _("lab journal")

	def name (self):
		return gmLabJournal.tab_name

	def GetWidget (self, parent):
		self._widget = cPluginPanel(parent, -1)
		return self._widget

	def MenuInfo (self):
		return ('tools', _('Show &lab journal'))

	def populate_with_data(self):
		# no use reloading if invisible
		if self.gb['main.notebook.raised_plugin'] != self.__class__.__name__:
			return 1
		if self._widget.nb.update() is None:
			_log.Log(gmLog.lErr, "cannot update lab journal with data")
			return None
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
	print("do not run standalone like this")
#================================================================
