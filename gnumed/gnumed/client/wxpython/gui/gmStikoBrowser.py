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
# - this actually belongs into guid-de
# - but really we should build a more generic yet more
#   specialized "medical content browser"
#
#==============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gui/Attic/gmStikoBrowser.py,v $
__version__ = "$Revision: 1.2 $"
__license__ = "GPL"
__author__ =	"Sebastian Hilbert <Sebastian.Hilbert@gmx.net>"

import sys, os, os.path

from   wxPython.wx         import *
from   wxPython.html       import *
import wxPython.lib.wxpTag
import gmGuiBroker, gmPlugin, gmLog

stiko_path = os.path.join("doc", "medical_knowledge", "de", "STIKO", "STI_NEU.htm")

import images_for_gnumed_browser16_16
import images_gnuMedGP_Toolbar

ID_STIKOCONTENTS = wxNewId()
ID_STIKOBACK = wxNewId()
ID_STIKOFORWARD = wxNewId()
ID_STIKOHOME = wxNewId()
ID_STIKOBABELFISH = wxNewId()
ID_STIKOPRINTER  = wxNewId()
ID_STIKOOPENFILE = wxNewId()
ID_STIKOBOOKMARKS = wxNewId()
ID_STIKOADDBOOKMARK = wxNewId()
ID_STIKOVIEWSOURCE = wxNewId()
ID_STIKORELOAD = wxNewId()
ID_VIEWSOURCE  = wxNewId()

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
        self.SetAutoLayout(true)

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
        from wxPython.lib.dialogs import wxScrolledMessageDialog
        source = self.html.GetParser().GetSource()
        dlg = wxScrolledMessageDialog(self, source, _('HTML Source'))
        dlg.ShowModal()
        dlg.Destroy()


    def OnPrint(self, event):
        self.printer.PrintFile(self.html.GetOpenedPage())


class gmStikoBrowser (gmPlugin.wxNotebookPlugin):
    """
    Plugin to encapsulate the STIKO window
    """
    def name (self):
        return 'StIKo'

    def MenuInfo (self):
        return ('reference', '&StIKo')

    def GetWidget (self, parent):
        return StikoHtmlPanel (parent, self.gb['main.frame'])

    def DoToolbar (self, tb, widget):
		tool1 = tb.AddTool(
			ID_STIKOCONTENTS,
			images_for_gnumed_browser16_16.getcontentsBitmap(),
			shortHelpString=_("Table of Content"),
			isToggle=true
		)
		EVT_TOOL (tb, ID_STIKOCONTENTS, widget.OnShowDefault)

		tool1 = tb.AddTool(
			ID_STIKOOPENFILE, 
			images_for_gnumed_browser16_16.getfileopenBitmap(),
			shortHelpString=_("Open File"),
			isToggle=true
		)
		EVT_TOOL (tb, ID_STIKOOPENFILE, widget.OnLoadFile)

		tool1 = tb.AddTool(
			ID_STIKOBACK, 
			images_for_gnumed_browser16_16.get1leftarrowBitmap(),
			shortHelpString=_("Back"),
			isToggle=false
		)
		EVT_TOOL (tb, ID_STIKOBACK, widget.OnBack)

		tool1 = tb.AddTool(
			ID_STIKOFORWARD, 
			images_for_gnumed_browser16_16.get1rightarrowBitmap(),
			shortHelpString=_("Forward"),
			isToggle=true
		)
		EVT_TOOL (tb, ID_STIKOFORWARD, widget.OnForward)

		tool1 = tb.AddTool(
			ID_STIKORELOAD, 
			images_for_gnumed_browser16_16.getreloadBitmap(),	
			shortHelpString=_("Reload"),
			isToggle=true
		)

		tb.AddSeparator()

		tool1 = tb.AddTool(
			ID_STIKOHOME,
			images_for_gnumed_browser16_16.getgohomeBitmap(),	
			shortHelpString=_("Home"),
			isToggle=true
		)
		EVT_TOOL (tb, ID_STIKOHOME, widget.OnShowDefault)

		tb.AddSeparator()

		tool1 = tb.AddTool(
			ID_STIKOBABELFISH, 
			images_for_gnumed_browser16_16.getbabelfishBitmap(),
			shortHelpString=_("Translate text"), 
			isToggle=false
		)
		#EVT_TOOL (tb, ID_STIKOBABELFISH, widget.OnBabelFish )
		
		tb.AddSeparator()

		tool1 = tb.AddTool(
			ID_STIKOBOOKMARKS, 
			images_for_gnumed_browser16_16.getbookmarkBitmap(),
			shortHelpString=_("Bookmarks"), 
			isToggle=true
		)
		#EVT_TOOL (tb, ID_STIKOBOOKMARKS, widget.OnBookmarks)

		tool1 = tb.AddTool(
			ID_STIKOADDBOOKMARK, 
			images_for_gnumed_browser16_16.getbookmark_addBitmap(),
			shortHelpString=_("Add Bookmark"), 
			isToggle=true
		)
		#EVT_TOOL (tb, ID_STIKOADDBOOKMARK, widget.OnAddBookmark)

		tool1 = tb.AddTool(
			ID_VIEWSOURCE, 
			images_for_gnumed_browser16_16.getviewsourceBitmap(),
			shortHelpString=_("View Source"), 
			isToggle=true
		)
		EVT_TOOL (tb, ID_VIEWSOURCE, widget.OnViewSource)

		tool1 = tb.AddTool(
			ID_STIKOPRINTER, 
			images_for_gnumed_browser16_16.getprinterBitmap(),
			shortHelpString=_("Print Page"), 
			isToggle=true
		)
		EVT_TOOL (tb, ID_STIKOPRINTER, widget.OnPrint)
