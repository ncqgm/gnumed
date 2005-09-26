# a simple wrapper for the Manual class

"""German StIKo guidelines in a HTML browser window

@author: Sebastian Hilbert
@version: 0.1
@copyright: GPL
@thanks: this code has been heavily "borrowed" from
		 Robin Dunn's extraordinary wxPython sample
"""
#==============================================================
# NOTE
# - but really we should build a more generic yet more
#   specialized "medical content browser"
#==============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gui/Attic/gmStikoBrowser.py,v $
__version__ = "$Revision: 1.18 $"
__license__ = "GPL"
__author__ =    "Sebastian Hilbert <Sebastian.Hilbert@gmx.net>"

import sys, os, os.path

from   wxPython.wx         import *
from   wxPython.html       import *
import wxPython.lib.wxpTag

from Gnumed.pycommon import gmGuiBroker, gmLog, gmI18N
from Gnumed.wxpython import gmPlugin, images_for_gnumed_browser16_16, images_gnuMedGP_Toolbar

stiko_path = os.path.join("doc", "medical_knowledge", "de", "STIKO", "STI_NEU.htm")

[
ID_STIKOCONTENTS,
ID_STIKOBACK,
ID_STIKOFORWARD,
ID_STIKOHOME,
ID_STIKOBABELFISH,
ID_STIKOPRINTER,
ID_STIKOOPENFILE,
ID_STIKOBOOKMARKS,
ID_STIKOADDBOOKMARK,
ID_STIKOVIEWSOURCE,
ID_STIKORELOAD,
ID_VIEWSOURCE
] = map(lambda _init_ctrls: wxNewId(), range(12))

#----------------------------------------------------------------------


class StikoHtmlWindow(wxHtmlWindow):
	def __init__(self, parent, id):
		wxHtmlWindow.__init__(self, parent, id)
		self.parent = parent

	def OnSetTitle(self, title):
		self.parent.ShowTitle(title)


class StikoHtmlPanel(wxPanel):
	def __init__(self, parent, frame):
		wxPanel.__init__(self, parent, -1)
		self.frame = frame
		# CHANGED CODE Haywood 26/2/02
		# get base directory for manuals from broker
		# Ideally this should be something like "/usr/doc/gnumed/"
		self.docdir = gmGuiBroker.GuiBroker ()['gnumed_dir']
		self.printer = wxHtmlEasyPrinting()

		self.box = wxBoxSizer(wxVERTICAL)

		infobox = wxBoxSizer(wxHORIZONTAL)
		n = wxNewId()
		self.infoline = wxTextCtrl(self, n, style=wxTE_READONLY)
		self.infoline.SetBackgroundColour(wxLIGHT_GREY)
		infobox.Add(self.infoline, 1, wxGROW|wxALL)
		self.box.Add(infobox, 0, wxGROW)

		self.html = StikoHtmlWindow(self, -1)
		self.html.SetRelatedFrame(frame, "")
		self.html.SetRelatedStatusBar(0)
		self.box.Add(self.html, 1, wxGROW)

		self.SetSizer(self.box)
		self.SetAutoLayout(True)

		self.OnShowDefault(None)

##     def __del__(self):
##         print 'ManualHtmlPanel.__del__'

	def ShowTitle(self, title):
		self.infoline.Clear()
		self.infoline.WriteText(title)

	def OnShowDefault(self, event):
		name = os.path.join(self.docdir, stiko_path)
		if os.access (name, os.F_OK):
			self.html.LoadPage(name)
		else:
			gmLog.gmDefLog.Log (gmLog.lErr, "cannot load document %s" % name)


	def OnLoadFile(self, event):
		dlg = wxFileDialog(self, wildcard = '*.htm*', style=wxOPEN)
		if dlg.ShowModal():
			path = dlg.GetPath()
			self.html.LoadPage(path)
		dlg.Destroy()


	def OnBack(self, event):
		if not self.html.HistoryBack():
			gmLog.gmDefLog.Log (gmLog.lInfo, _("StikoHtmlWindow: No more items in history!\n"))


	def OnForward(self, event):
		if not self.html.HistoryForward():
			gmLog.gmDefLog.Log (gmLog.lInfo, _("StikoHtmlWindow: No more items in history!\n"))


	def OnViewSource(self, event):
		xxx
		# FIXME:
		#from wxPython.lib.dialogs import wxScrolledMessageDialog
		source = self.html.GetParser().GetSource()
		dlg = wxScrolledMessageDialog(self, source, _('HTML Source'))
		dlg.ShowModal()
		dlg.Destroy()


	def OnPrint(self, event):
		self.printer.PrintFile(self.html.GetOpenedPage())


class gmStikoBrowser (gmPlugin.cNotebookPluginOld):
	"""
	Plugin to encapsulate the STIKO window
	"""
	tab_name = _('StIKo')

	def name (self):
		return gmStikoBrowser.tab_name

	def MenuInfo (self):
		return ('reference', _('&StIKo'))

	def GetWidget (self, parent):
		return StikoHtmlPanel (parent, self.gb['main.frame'])

	def populate_toolbar (self, tb, widget):
		tool1 = tb.AddTool(
			ID_STIKOCONTENTS,
			images_for_gnumed_browser16_16.getcontentsBitmap(),
			shortHelpString=_("Table of Content"),
			isToggle=True
		)
		EVT_TOOL (tb, ID_STIKOCONTENTS, widget.OnShowDefault)

		tool1 = tb.AddTool(
			ID_STIKOOPENFILE, 
			images_for_gnumed_browser16_16.getfileopenBitmap(),
			shortHelpString=_("Open File"),
			isToggle=True
		)
		EVT_TOOL (tb, ID_STIKOOPENFILE, widget.OnLoadFile)

		tool1 = tb.AddTool(
			ID_STIKOBACK, 
			images_for_gnumed_browser16_16.get1leftarrowBitmap(),
			shortHelpString=_("Back"),
			isToggle=False
		)
		EVT_TOOL (tb, ID_STIKOBACK, widget.OnBack)

		tool1 = tb.AddTool(
			ID_STIKOFORWARD, 
			images_for_gnumed_browser16_16.get1rightarrowBitmap(),
			shortHelpString=_("Forward"),
			isToggle=True
		)
		EVT_TOOL (tb, ID_STIKOFORWARD, widget.OnForward)

		tool1 = tb.AddTool(
			ID_STIKORELOAD, 
			images_for_gnumed_browser16_16.getreloadBitmap(),   
			shortHelpString=_("Reload"),
			isToggle=True
		)

		tb.AddSeparator()

		tool1 = tb.AddTool(
			ID_STIKOHOME,
			images_for_gnumed_browser16_16.getgohomeBitmap(),   
			shortHelpString=_("Home"),
			isToggle=True
		)
		EVT_TOOL (tb, ID_STIKOHOME, widget.OnShowDefault)

		tb.AddSeparator()

		tool1 = tb.AddTool(
			ID_STIKOBABELFISH, 
			images_for_gnumed_browser16_16.getbabelfishBitmap(),
			shortHelpString=_("Translate text"), 
			isToggle=False
		)
		#EVT_TOOL (tb, ID_STIKOBABELFISH, widget.OnBabelFish )
		
		tb.AddSeparator()

		tool1 = tb.AddTool(
			ID_STIKOBOOKMARKS, 
			images_for_gnumed_browser16_16.getbookmarkBitmap(),
			shortHelpString=_("Bookmarks"), 
			isToggle=True
		)
		#EVT_TOOL (tb, ID_STIKOBOOKMARKS, widget.OnBookmarks)
		
		tool1 = tb.AddTool(
			ID_STIKOADDBOOKMARK, 
			images_for_gnumed_browser16_16.getbookmark_addBitmap(),
			shortHelpString=_("Add Bookmark"), 
			isToggle=True
		)
		#EVT_TOOL (tb, ID_STIKOADDBOOKMARK, widget.OnAddBookmark)

		tool1 = tb.AddTool(
			ID_VIEWSOURCE, 
			images_for_gnumed_browser16_16.getviewsourceBitmap(),
			shortHelpString=_("View Source"), 
			isToggle=True
		)
		EVT_TOOL (tb, ID_VIEWSOURCE, widget.OnViewSource)

		tool1 = tb.AddTool(
			ID_STIKOPRINTER, 
			images_for_gnumed_browser16_16.getprinterBitmap(),
			shortHelpString=_("Print Page"), 
			isToggle=True
		)
		EVT_TOOL (tb, ID_STIKOPRINTER, widget.OnPrint)

#======================================================
# $Log: gmStikoBrowser.py,v $
# Revision 1.18  2005-09-26 18:01:52  ncq
# - use proper way to import wx26 vs wx2.4
# - note: THIS WILL BREAK RUNNING THE CLIENT IN SOME PLACES
# - time for fixup
#
# Revision 1.17  2004/12/27 18:55:12  shilbert
# - I should have tested the last commit :-) shame on me
#
# Revision 1.16  2004/12/27 18:51:37  shilbert
# - converted spaces to tabs, hopefully this won't break it
#
# Revision 1.15  2004/08/04 17:16:02  ncq
# - wxNotebookPlugin -> cNotebookPlugin
# - derive cNotebookPluginOld from cNotebookPlugin
# - make cNotebookPluginOld warn on use and implement old
#   explicit "main.notebook.raised_plugin"/ReceiveFocus behaviour
# - ReceiveFocus() -> receive_focus()
#
# Revision 1.14  2004/07/18 20:30:54  ncq
# - wxPython.true/false -> Python.True/False as Python tells us to do
#
# Revision 1.13  2004/06/26 23:45:50  ncq
# - cleanup, id_* -> fk/pk_*
#
# Revision 1.12  2004/06/25 12:37:21  ncq
# - eventually fix the import gmI18N issue
#
# Revision 1.11  2004/06/20 16:50:52  ncq
# - carefully fool epydoc
#
# Revision 1.10  2004/06/20 06:49:21  ihaywood
# changes required due to Epydoc's OCD
#
# Revision 1.9  2004/06/13 22:31:49  ncq
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
# Revision 1.8  2004/03/18 09:43:02  ncq
# - import gmI18N if standalone
#
# Revision 1.7  2004/03/09 08:03:26  ncq
# - cleanup
#
# Revision 1.6  2004/03/08 23:17:29  shilbert
# - adapt to new API from Gnumed.foo import bar
#
# Revision 1.5  2003/11/17 10:56:41  sjtan
#
# synced and commiting.
#
# Revision 1.4  2003/11/07 23:19:54  shilbert
# - removed repetitive calls to wxNewId()
#
