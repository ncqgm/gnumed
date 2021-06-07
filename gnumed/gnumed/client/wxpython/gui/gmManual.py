# -*- coding: utf-8 -*-
# a simple wrapper for the Manual class

"""GNUMed manuals in a HTML browser window

A very basic HTML browser with back/forward history buttons
with  the main pourpose of browsing the gnumed manuals
The manuals should reside where the manual_path points to.

@copyright: GPL v2 or later
@thanks: this code has been heavily "borrowed" from
		 Robin Dunn's extraordinary wxPython sample
"""
#===========================================================
__author__ = "H.Herb, I.Haywood, H.Berger, K.Hilbert"

import os, os.path, logging

import wx
import wx.html

from Gnumed.pycommon import gmTools
from Gnumed.wxpython import gmPlugin

_log = logging.getLogger('gm.ui')

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

if __name__ == '__main__':
	_ = lambda x:x

#===========================================================
class ManualHtmlWindow(wx.html.HtmlWindow):
	def __init__(self, parent, id):
		wx.html.HtmlWindow.__init__(self, parent, id)
		self.parent = parent

	def OnSetTitle(self, title=''):
		self.parent.ShowTitle(title)
#===========================================================
class ManualHtmlPanel(wx.Panel):
	def __init__(self, parent, frame):
		wx.Panel.__init__(self, parent, -1)
		self.frame = frame

		# get base directory for manuals from broker
		paths = gmTools.gmPaths(app_name = 'gnumed', wx = wx)
		candidates = [
			os.path.join(paths.local_base_dir, 'doc', 'user-manual'),
			'/usr/share/doc/gnumed/user-manual/',
			os.path.join(paths.system_app_data_dir, 'doc', 'user-manual')
		]
		for self.docdir in candidates:
			if os.access(self.docdir, os.R_OK):
				_log.info('found Manual path [%s]', self.docdir)
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
	def ShowTitle(self, title=''):
		self.infoline.Clear()
		self.infoline.WriteText(title)
	#--------------------------------------------------------
	def OnShowDefault(self, event):
		name = os.path.join(self.docdir, 'index.html')
		if os.access (name, os.F_OK):
			self.html.LoadPage(name)
		else:
			_log.error("cannot load local document %s", name)
			self.html.LoadPage('https://www.gnumed.de/documentation/')
	#--------------------------------------------------------
	def OnLoadFile(self, event):
		dlg = wx.FileDialog(self, wildcard = '*.htm*', style=wx.FD_OPEN)
		if dlg.ShowModal():
			path = dlg.GetPath()
			self.html.LoadPage(path)
		dlg.DestroyLater()
	#--------------------------------------------------------
	def OnBack(self, event):
		self.html.HistoryBack()
	#--------------------------------------------------------
	def OnForward(self, event):
		self.html.HistoryForward()
	#--------------------------------------------------------
	def OnViewSource(self, event):
		return 1
		# FIXME:
		#from wxPython.lib.dialogs import wx.ScrolledMessageDialog
		source = self.html.GetParser().GetSource()
		dlg = wx.ScrolledMessageDialog(self, source, _('HTML Source'))
		dlg.ShowModal()
		dlg.DestroyLater()
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
		#self._widget = ManualHtmlPanel (parent, ...)
		self._widget = wx.Panel(parent, -1)
		return self._widget
	#--------------------------------------------------------
	def MenuInfo (self):
		return ('help', _('User &manual (local)'))
	#--------------------------------------------------------
	def receive_focus(self):
		self._widget.FirstLoad()
		return True
	#--------------------------------------------------------
	def can_receive_focus(self):
		return True
	#--------------------------------------------------------
	#def populate_toolbar (self, tb, widget):
		#tool1 = tb.AddTool(
		#	ID_MANUALCONTENTS,
		#	images_for_gnumed_browser16_16.getcontentsBitmap(),
		#	shortHelpString=_("GNUmed manual contents"),
		#	isToggle=False
		#)
		#wx.EVT_TOOL (tb, ID_MANUALCONTENTS, widget.OnShowDefault)

#		tool1 = tb.AddTool(
#			ID_MANUALOPENFILE,
#			images_for_gnumed_browser16_16.getfileopenBitmap(),
#			shortHelpString="Open File",
#			isToggle=True
#		)
#		wx.EVT_TOOL (tb, ID_MANUALOPENFILE, widget.OnLoadFile)

		#tool1 = tb.AddTool(
		#	ID_MANUALBACK,
		#	images_for_gnumed_browser16_16.get1leftarrowBitmap(),
		#	shortHelpString=_("Back"),
		#	isToggle=False
		#)
		#wx.EVT_TOOL (tb, ID_MANUALBACK, widget.OnBack)

		#tool1 = tb.AddTool(
		#	ID_MANUALFORWARD,
		#	images_for_gnumed_browser16_16.get1rightarrowBitmap(),
		#	shortHelpString=_("Forward"),
		#	isToggle=False
		#)
		#wx.EVT_TOOL (tb, ID_MANUALFORWARD, widget.OnForward)

#		#tool1 = tb.AddTool(
#		#	ID_MANUALRELOAD,
#		#	images_for_gnumed_browser16_16.getreloadBitmap(),
#		#	shortHelpString=_("Reload"),
#		#	isToggle=True
#		#)
		
#		#tb.AddSeparator()

#		#tool1 = tb.AddTool(
#		#	ID_MANUALHOME,
#		#	images_for_gnumed_browser16_16.getgohomeBitmap(),
#		#	shortHelpString=_("Home"),
#		#	isToggle=True
#		#)
#		#wx.EVT_TOOL (tb, ID_MANUALHOME, widget.OnShowDefault)

#		#tb.AddSeparator()

#		#tool1 = tb.AddTool(
#		#	ID_MANUALBABELFISH,
#		#	images_for_gnumed_browser16_16.getbabelfishBitmap(),
#		#	shortHelpString=_("Translate text"),
#		#	isToggle=False
#		#)
#		#wx.EVT_TOOL (tb, ID_MANUALBABELFISH, widget.OnBabelFish )

#		#tb.AddSeparator()

#		#tool1 = tb.AddTool(
#		#	ID_MANUALBOOKMARKS,
#		#	images_for_gnumed_browser16_16.getbookmarkBitmap(),
#		#	shortHelpString=_("Bookmarks"),
#		#	isToggle=True
#		#)
#		#wx.EVT_TOOL (tb, ID_MANUALBOOKMARKS, widget.OnBookmarks)

#		#tool1 = tb.AddTool(
#		#	ID_MANUALADDBOOKMARK,
#		#	images_for_gnumed_browser16_16.getbookmark_addBitmap(),
#		#	shortHelpString=_("Add Bookmark"),
#		#	isToggle=True
#		#)
#		#wx.EVT_TOOL (tb, ID_MANUALADDBOOKMARK, widget.OnAddBookmark)

#		tool1 = tb.AddTool(
#			ID_VIEWSOURCE,
#			images_for_gnumed_browser16_16.getviewsourceBitmap(),
#			shortHelpString="View Source",
#			isToggle=True
#		)
#		wx.EVT_TOOL (tb, ID_VIEWSOURCE, widget.OnViewSource)

		#tool1 = tb.AddTool(
		#	ID_MANUALPRINTER,
		#	images_for_gnumed_browser16_16.getprinterBitmap(),
		#	shortHelpString = _("Print manual page"),
		#	isToggle=False
		#)
		#wx.EVT_TOOL (tb, ID_MANUALPRINTER, widget.OnPrint) 
#===========================================================
