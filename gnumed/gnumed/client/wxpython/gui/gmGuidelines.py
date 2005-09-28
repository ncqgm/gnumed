# a simple wrapper for the Manual class

"""Browser window for the various guidelines

A very basic HTML browser with back/forward history buttons
with  the main pourpose of browsing the gnumed manuals
The manuals should reside where the manual_path points to

@author: Dr. Horst Herb
@version: 0.2
@copyright: GPL
@thanks: this code has been heavily "borrowed" from
         Robin Dunn's extraordinary wxPython sample
"""
import os, sys

if __name__ == '__main__':
	print "this is not currently fit to run standalone"
	sys.exit(1)

from   wxPython.wx         import *
from   wxPython.html       import *
import wxPython.lib.wxpTag

from Gnumed.wxpython import gmPlugin
from Gnumed.pycommon import gmLog, gmGuiBroker, gmI18N

#----------------------------------------------------------------------
class GuidelinesHtmlWindow(wx.HtmlWindow):
    def __init__(self, parent, id):
        wx.HtmlWindow.__init__(self, parent, id)
        self.parent = parent

    def OnSetTitle(self, title):
        self.parent.ShowTitle(title)


class GuidelinesHtmlPanel(wx.Panel):
    def __init__(self, parent, frame):
        wx.Panel.__init__(self, parent, -1)
        self.frame = frame
        # CHANGED CODE Haywood 26/2/02
        # get base directory for manuals from broker
        # Ideally this should be something like "/usr/doc/gnumed/"
        self.docdir = gmGuiBroker.GuiBroker ()['gnumed_dir']
        self.printer = wx.HtmlEasyPrinting()

        self.box = wx.BoxSizer(wx.VERTICAL)

        infobox = wx.BoxSizer(wx.HORIZONTAL)
        n = wx.NewId()
        self.infoline = wx.TextCtrl(self, n, style=wx.TE_READONLY)
        self.infoline.SetBackgroundColour(wx.LIGHT_GREY)
        infobox.Add(self.infoline, 1, wxGROW|wxALL)
        self.box.Add(infobox, 0, wxGROW)

        self.html = GuidelinesHtmlWindow(self, -1)
        self.html.SetRelatedFrame(frame, "")
        self.html.SetRelatedStatusBar(0)
        self.box.Add(self.html, 1, wxGROW)

        subbox = wx.BoxSizer(wx.HORIZONTAL)
        n = wx.NewId()
        btn = wx.Button(self, n, _("?button?"))
        wx.EVT_BUTTON(self, n, self.OnShowDefault)
        subbox.Add(btn, 1, wxGROW | wxALL, 2)

        n = wx.NewId()
        btn = wx.Button(self, n, _("Load File"))
        wx.EVT_BUTTON(self, n, self.OnLoadFile)
        subbox.Add(btn, 1, wxGROW | wxALL, 2)

        n = wx.NewId()
        btn = wx.Button(self, n, _("Back"))
        wx.EVT_BUTTON(self, n, self.OnBack)
        subbox.Add(btn, 1, wxGROW | wxALL, 2)

        n = wx.NewId()
        btn = wx.Button(self, n, _("Forward"))
        wx.EVT_BUTTON(self, n, self.OnForward)
        subbox.Add(btn, 1, wxGROW | wxALL, 2)

        n = wx.NewId()
        btn = wx.Button(self, n, _("Print"))
        wx.EVT_BUTTON(self, n, self.OnPrint)
        subbox.Add(btn, 1, wxGROW | wxALL, 2)

        n = wx.NewId()
        btn = wx.Button(self, n, _("View Source"))
        wx.EVT_BUTTON(self, n, self.OnViewSource)
        subbox.Add(btn, 1, wxGROW | wxALL, 2)

        self.box.Add(subbox, 0, wxGROW)

        self.SetSizer(self.box)
        self.SetAutoLayout(True)

        self.OnShowDefault(None)

##     def __del__(self):
##         print 'ManualHtmlPanel.__del__'

    def ShowTitle(self, title):
        self.infoline.Clear()
        self.infoline.WriteText(title)

    def OnShowDefault(self, event):
        # temporary
        name = '/home/ian/therapy/tgentry.htm'
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
            gmLog.gmDefLog.Log (gmLog.lInfo, "ManualHtmlWindow: No more items in history!\n")


    def OnForward(self, event):
        if not self.html.HistoryForward():
            gmLog.gmDefLog.Log (gmLog.lInfo, "ManualHtmlWindow: No more items in history!\n")


    def OnViewSource(self, event):
		xxxxx
		#FIXME:
        from wxPython.lib.dialogs import wxScrolledMessageDialog
        source = self.html.GetParser().GetSource()
        dlg = wxScrolledMessageDialog(self, source, _('HTML Source'))
        dlg.ShowModal()
        dlg.Destroy()


    def OnPrint(self, event):
        self.printer.PrintFile(self.html.GetOpenedPage())


class gmGuidelines (gmPlugin.cNotebookPluginOld):
    """
    Plugin to encapsulate the manual window
    """
    tab_name = _('Guidelines')

    def name (self):
        return gmGuidelines.tab_name

    def MenuInfo (self):
        return ('reference', _('&Guidelines'))

    def GetWidget (self, parent):
        return GuidelinesHtmlPanel (parent, self.gb['main.frame'])
