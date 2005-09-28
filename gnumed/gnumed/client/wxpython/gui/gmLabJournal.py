"""This plugin lets you manage laboratory requests
 - add requests
 - keep track of pending requests
 - see import errors
 - review newly imported lab results
"""
#============================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gui/gmLabJournal.py,v $
# $Id: gmLabJournal.py,v 1.38 2005-09-28 21:27:30 ncq Exp $
__version__ = "$Revision: 1.38 $"
__author__ = "Sebastian Hilbert <Sebastian.Hilbert@gmx.net>"

try:
	import wxversion
	import wx
except ImportError:
	from wxPython import wx

from Gnumed.pycommon import gmLog, gmI18N
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
	print "do not run standalone like this"
#================================================================
# $Log: gmLabJournal.py,v $
# Revision 1.38  2005-09-28 21:27:30  ncq
# - a lot of wx2.6-ification
#
# Revision 1.37  2005/09/26 18:01:52  ncq
# - use proper way to import wx26 vs wx2.4
# - note: THIS WILL BREAK RUNNING THE CLIENT IN SOME PLACES
# - time for fixup
#
# Revision 1.36  2004/08/04 17:16:02  ncq
# - wx.NotebookPlugin -> cNotebookPlugin
# - derive cNotebookPluginOld from cNotebookPlugin
# - make cNotebookPluginOld warn on use and implement old
#   explicit "main.notebook.raised_plugin"/ReceiveFocus behaviour
# - ReceiveFocus() -> receive_focus()
#
# Revision 1.35  2004/07/15 15:18:53  ncq
# - factored out everything that wasn't strictly notebook plugin
#   related, see wxpython/gmLabWidgets.py
#
# Revision 1.34  2004/07/15 14:47:15  ncq
# - revert back to notebook plugin
#
# Revision 1.32  2004/06/30 07:05:31  shilbert
# - 'clin_when' -> 'sampled_when'
# - more fk/pk changes
#
# Revision 1.31  2004/06/26 23:45:50  ncq
# - cleanup, id_* -> fk/pk_*
#
# Revision 1.30  2004/06/26 07:33:55  ncq
# - id_episode -> fk/pk_episode
#
# Revision 1.29  2004/06/20 16:50:51  ncq
# - carefully fool epydoc
#
# Revision 1.28  2004/06/20 13:48:02  shilbert
# - GUI polished
#
# Revision 1.27  2004/06/20 06:49:21  ihaywood
# changes required due to Epydoc's OCD
#
# Revision 1.26  2004/06/13 22:31:49  ncq
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
# Revision 1.25  2004/06/05 11:31:54  shilbert
# - GUI cleanup as per ncq's request
# - request reviewed via single-click, double-click, <SPACE> implemented
#
# Revision 1.24  2004/06/02 00:02:32  ncq
# - cleanup, indentation fixes
#
# Revision 1.23  2004/05/30 21:19:01  shilbert
# - completely redone review panel
#
# Revision 1.22  2004/05/29 20:20:30  shilbert
# - review stuff finally works
#
# Revision 1.21  2004/05/29 10:22:10  ncq
# - looking good, just some cleanup/comments as usual
#
# Revision 1.20  2004/05/28 21:11:56  shilbert
# - basically keep up with API changes
#
# Revision 1.19  2004/05/28 07:12:11  shilbert
# - finally real artwork
# - switched to new import regimen for artwork
#
# Revision 1.18  2004/05/27 08:47:35  shilbert
# - listctrl item insertion bugfix
#
# Revision 1.17  2004/05/26 14:05:21  ncq
# - cleanup
#
# Revision 1.16  2004/05/26 13:31:00  shilbert
# - cleanup, gui enhancements
#
# Revision 1.15  2004/05/26 11:07:04  shilbert
# - gui layout changes
#
# Revision 1.14  2004/05/25 13:26:49  ncq
# - cleanup
#
# Revision 1.13  2004/05/25 08:15:20  shilbert
# - make use of gmPathLab for db querries
# - introduce limit for user visible list items
#
# Revision 1.12  2004/05/22 23:29:09  shilbert
# - gui updates (import error context , ctrl labels )
#
# Revision 1.11  2004/05/18 20:43:17  ncq
# - check get_clinical_record() return status
#
# Revision 1.10  2004/05/18 19:38:54  shilbert
# - gui enhancements (wxExpand)
#
# Revision 1.9  2004/05/08 17:43:55  ncq
# - cleanup here and there
#
# Revision 1.8  2004/05/06 23:32:45  shilbert
# - now features a tab with unreviewed lab results
#
# Revision 1.7  2004/05/04 09:26:55  shilbert
# - handle more errors
#
# Revision 1.6  2004/05/04 08:42:04  shilbert
# - first working version, needs testing
#
# Revision 1.5  2004/05/04 07:19:34  shilbert
# - kind of works, still a bug in create_request()
#
# Revision 1.4  2004/05/01 10:29:46  shilbert
# - custom event handlig code removed, pending lab ids input almost completed
#
# Revision 1.3  2004/04/29 21:05:19  shilbert
# - some more work on auto update of id field
#
# Revision 1.2  2004/04/28 16:12:02  ncq
# - cleanups, as usual
#
# Revision 1.1  2004/04/28 07:20:00  shilbert
# - initial release after name change, lacks features
#
