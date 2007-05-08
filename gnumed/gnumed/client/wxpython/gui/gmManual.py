# a simple wrapper for the Manual class

"""GNUMed manuals in a HTML browser window

A very basic HTML browser with back/forward history buttons
with  the main pourpose of browsing the gnumed manuals
The manuals should reside where the manual_path points to.

@copyright: GPL
@thanks: this code has been heavily "borrowed" from
		 Robin Dunn's extraordinary wxPython sample
"""
#===========================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gui/gmManual.py,v $
# $Id: gmManual.py,v 1.40 2007-05-08 11:17:09 ncq Exp $
__version__ = "$Revision: 1.40 $"
__author__ = "H.Herb, I.Haywood, H.Berger, K.Hilbert"

import os, sys, os.path

import wx
import wx.html

from Gnumed.pycommon import gmLog, gmTools
from Gnumed.wxpython import gmPlugin, images_for_gnumed_browser16_16, images_gnuMedGP_Toolbar

_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)

ID_MANUALCONTENTS = wx.NewId()
ID_MANUALBACK = wx.NewId()
ID_MANUALFORWARD = wx.NewId()
ID_MANUALHOME = wx.NewId()
ID_MANUALBABELFISH = wx.NewId()
ID_MANUALPRINTER  = wx.NewId()
ID_MANUALOPENFILE = wx.NewId()
ID_MANUALBOOKMARKS = wx.NewId()
ID_MANUALADDBOOKMARK = wx.NewId()
ID_MANUALVIEWSOURCE = wx.NewId()
ID_MANUALRELOAD = wx.NewId()
ID_VIEWSOURCE  = wx.NewId()
#===========================================================
class ManualHtmlWindow(wx.html.HtmlWindow):
	def __init__(self, parent, id):
		wx.html.HtmlWindow.__init__(self, parent, id)
		self.parent = parent

	def OnSetTitle(self, title):
		self.parent.ShowTitle(title)
#===========================================================
class ManualHtmlPanel(wx.Panel):
	def __init__(self, parent, frame):
		wx.Panel.__init__(self, parent, -1)
		self.frame = frame

		# get base directory for manuals from broker
		paths = gmTools.cPaths(app_name = 'gnumed', wx = wx)
		candidates = [
			os.path.join(paths.local_base_dir, 'doc', 'user-manual'),
			'/usr/share/doc/gnumed/user-manual/',
			os.path.join(paths.system_app_data_dir, 'doc', 'user-manual')
		]
		for self.docdir in candidates:
			if os.access(self.docdir, os.R_OK):
				break

		self.box = wx.BoxSizer(wx.VERTICAL)

		infobox = wx.BoxSizer(wx.HORIZONTAL)
		n = wx.NewId()
		self.infoline = wx.TextCtrl(self, n, style=wx.TE_READONLY)
		self.infoline.SetBackgroundColour(wx.LIGHT_GREY)
		infobox.Add(self.infoline, 1, wx.GROW|wx.ALL)
		self.box.Add(infobox, 0, wx.GROW)

		self.html = ManualHtmlWindow(self, -1)
		self.html.SetRelatedFrame(frame, "")
		self.html.SetRelatedStatusBar(0)
		self.box.Add(self.html, 1, wx.GROW)

		self.SetSizer(self.box)
		self.SetAutoLayout(True)

		self.already_loaded = None
	#--------------------------------------------------------
	def FirstLoad(self):
		if not self.already_loaded:
			self.already_loaded = 1
			self.OnShowDefault(None)
	#--------------------------------------------------------
	def ShowTitle(self, title):
		self.infoline.Clear()
		self.infoline.WriteText(title)
	#--------------------------------------------------------
	def OnShowDefault(self, event):
		name = os.path.join(self.docdir, 'index.html')
		if os.access (name, os.F_OK):
			self.html.LoadPage(name)
		else:
			_log.Log (gmLog.lErr, "cannot load local document %s" % name)
			self.html.LoadPage('http://wiki.gnumed.de/bin/view/Gnumed/GnumedManual?template=viewprint')
	#--------------------------------------------------------
	def OnLoadFile(self, event):
		dlg = wx.FileDialog(self, wildcard = '*.htm*', style=wx.OPEN)
		if dlg.ShowModal():
			path = dlg.GetPath()
			self.html.LoadPage(path)
		dlg.Destroy()
	#--------------------------------------------------------
	def OnBack(self, event):
		if not self.html.HistoryBack():
			_log.Log (gmLog.lInfo, _("ManualHtmlWindow: No more items in history!\n"))
	#--------------------------------------------------------
	def OnForward(self, event):
		if not self.html.HistoryForward():
			_log.Log (gmLog.lInfo, _("ManualHtmlWindow: No more items in history!\n"))
	#--------------------------------------------------------
	def OnViewSource(self, event):
		return 1
		# FIXME:
		#from wxPython.lib.dialogs import wx.ScrolledMessageDialog
		source = self.html.GetParser().GetSource()
		dlg = wx.ScrolledMessageDialog(self, source, _('HTML Source'))
		dlg.ShowModal()
		dlg.Destroy()
	#--------------------------------------------------------
	def OnPrint(self, event):
		self.printer.PrintFile(self.html.GetOpenedPage())
#===========================================================
class gmManual (gmPlugin.cNotebookPlugin):
	"""Plugin to encapsulate the manual window."""

	tab_name = _('Manual')
	#--------------------------------------------------------
	def name (self):
		return gmManual.tab_name
	#--------------------------------------------------------
	def GetWidget (self, parent):
		self._widget = ManualHtmlPanel (parent, self.gb['main.frame'])
		return self._widget
	#--------------------------------------------------------
	def MenuInfo (self):
		return ('help', '&Manual')
	#--------------------------------------------------------
	def receive_focus(self):
		self._widget.FirstLoad()
		return True
	#--------------------------------------------------------
	def can_receive_focus(self):
		return True
	#--------------------------------------------------------
	def populate_toolbar (self, tb, widget):
		tool1 = tb.AddTool(
			ID_MANUALCONTENTS,
			images_for_gnumed_browser16_16.getcontentsBitmap(),
			shortHelpString=_("GNUmed manual contents"),
			isToggle=False
		)
		wx.EVT_TOOL (tb, ID_MANUALCONTENTS, widget.OnShowDefault)

#		tool1 = tb.AddTool(
#			ID_MANUALOPENFILE,
#			images_for_gnumed_browser16_16.getfileopenBitmap(),
#			shortHelpString="Open File",
#			isToggle=True
#		)
#		wx.EVT_TOOL (tb, ID_MANUALOPENFILE, widget.OnLoadFile)

		tool1 = tb.AddTool(
			ID_MANUALBACK,
			images_for_gnumed_browser16_16.get1leftarrowBitmap(),
			shortHelpString=_("Back"),
			isToggle=False
		)
		wx.EVT_TOOL (tb, ID_MANUALBACK, widget.OnBack)

		tool1 = tb.AddTool(
			ID_MANUALFORWARD,
			images_for_gnumed_browser16_16.get1rightarrowBitmap(),
			shortHelpString=_("Forward"),
			isToggle=False
		)
		wx.EVT_TOOL (tb, ID_MANUALFORWARD, widget.OnForward)

		#tool1 = tb.AddTool(
		#	ID_MANUALRELOAD,
		#	images_for_gnumed_browser16_16.getreloadBitmap(),
		#	shortHelpString=_("Reload"),
		#	isToggle=True
		#)
		
		#tb.AddSeparator()

		#tool1 = tb.AddTool(
		#	ID_MANUALHOME,
		#	images_for_gnumed_browser16_16.getgohomeBitmap(),
		#	shortHelpString=_("Home"),
		#	isToggle=True
		#)
		#wx.EVT_TOOL (tb, ID_MANUALHOME, widget.OnShowDefault)

		#tb.AddSeparator()

		#tool1 = tb.AddTool(
		#	ID_MANUALBABELFISH,
		#	images_for_gnumed_browser16_16.getbabelfishBitmap(),
		#	shortHelpString=_("Translate text"),
		#	isToggle=False
		#)
		#wx.EVT_TOOL (tb, ID_MANUALBABELFISH, widget.OnBabelFish )

		#tb.AddSeparator()

		#tool1 = tb.AddTool(
		#	ID_MANUALBOOKMARKS,
		#	images_for_gnumed_browser16_16.getbookmarkBitmap(),
		#	shortHelpString=_("Bookmarks"),
		#	isToggle=True
		#)
		#wx.EVT_TOOL (tb, ID_MANUALBOOKMARKS, widget.OnBookmarks)

		#tool1 = tb.AddTool(
		#	ID_MANUALADDBOOKMARK,
		#	images_for_gnumed_browser16_16.getbookmark_addBitmap(),
		#	shortHelpString=_("Add Bookmark"),
		#	isToggle=True
		#)
		#wx.EVT_TOOL (tb, ID_MANUALADDBOOKMARK, widget.OnAddBookmark)

#		tool1 = tb.AddTool(
#			ID_VIEWSOURCE,
#			images_for_gnumed_browser16_16.getviewsourceBitmap(),
#			shortHelpString="View Source",
#			isToggle=True
#		)
#		wx.EVT_TOOL (tb, ID_VIEWSOURCE, widget.OnViewSource)

		tool1 = tb.AddTool(
			ID_MANUALPRINTER,
			images_for_gnumed_browser16_16.getprinterBitmap(),
			shortHelpString = _("Print manual page"),
			isToggle=False
		)
		wx.EVT_TOOL (tb, ID_MANUALPRINTER, widget.OnPrint) 
#===========================================================
# $Log: gmManual.py,v $
# Revision 1.40  2007-05-08 11:17:09  ncq
# - need to import gmTools
#
# Revision 1.39  2007/05/07 12:35:20  ncq
# - improve use of gmTools.cPaths()
#
# Revision 1.38  2007/04/11 20:47:34  ncq
# - nore more 'resource dir'
#
# Revision 1.37  2007/02/19 17:21:18  ncq
# - docs are in /usr/share/doc/gnumed/
#
# Revision 1.36  2006/11/26 17:46:42  ncq
# - if loading from the web use template viewprint for better results
#
# Revision 1.35  2006/07/24 14:58:07  ncq
# - acceptably smart access to user manual
#
# Revision 1.34  2006/05/20 18:56:03  ncq
# - use receive_focus() interface
#
# Revision 1.33  2006/05/15 13:40:02  ncq
# - turn into new-style notebook plugin
#
# Revision 1.32  2005/10/27 21:55:09  shilbert
# wxHTMLEasyPrinting caused gmManual to hang
# needs to be reimplemented
#
# Revision 1.31  2005/10/03 13:49:21  sjtan
# using new wx. temporary debugging to stdout(easier to read). where is rfe ?
#
# Revision 1.30  2005/09/28 21:27:30  ncq
# - a lot of wx2.6-ification
#
# Revision 1.29  2005/09/26 18:01:52  ncq
# - use proper way to import wx26 vs wx2.4
# - note: THIS WILL BREAK RUNNING THE CLIENT IN SOME PLACES
# - time for fixup
#
# Revision 1.28  2005/07/23 14:20:15  shilbert
# - fix path so docs will be found when using MS Windows
#
# Revision 1.27  2005/07/15 20:56:07  ncq
# - load User Manual from proper location (breaks loading from CVS tree copy for now)
#
# Revision 1.26  2005/06/30 10:24:00  cfmoro
# String corrections
#
# Revision 1.25  2005/06/29 12:38:42  cfmoro
# Keep only functional really buttons
#
# Revision 1.24  2004/12/27 18:42:05  shilbert
# - added some missing _() for i18n
#
# Revision 1.23  2004/08/04 17:16:02  ncq
# - wx.NotebookPlugin -> cNotebookPlugin
# - derive cNotebookPluginOld from cNotebookPlugin
# - make cNotebookPluginOld warn on use and implement old
#   explicit "main.notebook.raised_plugin"/ReceiveFocus behaviour
# - ReceiveFocus() -> receive_focus()
#
# Revision 1.22  2004/07/18 20:30:54  ncq
# - wxPython.true/false -> Python.True/False as Python tells us to do
#
# Revision 1.21  2004/06/25 12:37:21  ncq
# - eventually fix the import gmI18N issue
#
# Revision 1.20  2004/06/20 16:50:51  ncq
# - carefully fool epydoc
#
# Revision 1.19  2004/06/20 06:49:21  ihaywood
# changes required due to Epydoc's OCD
#
# Revision 1.18  2004/06/13 22:31:49  ncq
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
# Revision 1.17  2004/03/18 09:43:02  ncq
# - import gmI18N if standalone
#
# Revision 1.16  2004/03/12 13:25:15  ncq
# - import, cleanup
#
# Revision 1.15  2004/03/02 10:21:10  ihaywood
# gmDemographics now supports comm channels, occupation,
# country of birth and martial status
#
# Revision 1.14  2004/02/25 09:46:22  ncq
# - import from pycommon now, not python-common
#
# Revision 1.13  2003/11/17 10:56:40  sjtan
#
# synced and commiting.
#
# Revision 1.1  2003/10/23 06:02:40  sjtan
#
# manual edit areas modelled after r.terry's specs.
#
# Revision 1.12  2003/04/28 12:11:30  ncq
# - refactor name() to not directly return _(<name>)
#
# Revision 1.11  2003/02/15 14:55:55  ncq
# - whitespace fixup, dynamic loading sped up
#
# Revision 1.10	 2003/02/15 14:39:59  ncq
# - cleanup
# - comment out a few "un-needed" buttons
#
# Revision 1.9	2003/02/15 14:21:49	 ncq
# - on demand loading of Manual
# - further pluginization of showmeddocs
#
# Revision 1.8	2003/02/13 17:38:35	 ncq
# - cvs keywords, cleanup
#
