#! /usr/bin/python
"""GNUMed manuals in a HTML browser window

A very basic HTML browser with back/forward history buttons
with  the main pourpose of browsing the gnumed manuals
The manuals should reside where the manual_path points to

@author: Dr. Horst Herb
@version: 0.2
@copyright: GPL
@thanks: this code has been heavily "borrowed" from
         Robin Dunn's extraordinary wxPython sample
"""

# text translation function for localization purposes
import gettext
_ = gettext.gettext

import sys, os

from   wxPython.wx         import *
from   wxPython.html       import *
import wxPython.lib.wxpTag
import gmGuiBroker

manual_path = 'manual/index.html'

#----------------------------------------------------------------------


class ManualHtmlWindow(wxHtmlWindow):
    def __init__(self, parent, id, log):
        wxHtmlWindow.__init__(self, parent, id)
        self.log = log
        self.parent = parent

    def OnSetTitle(self, title):
        self.parent.ShowTitle(title)


class ManualHtmlPanel(wxPanel):
    def __init__(self, parent, frame, log):
        wxPanel.__init__(self, parent, -1)
        self.log = log
        self.frame = frame
        # CHANGED CODE Haywood 26/2/02
        # get base directory for manuals from broker
        # Ideally this should be something like "/usr/doc/gnumed/"
        # for now just use the scripts directory
        self.docdir = gmGuiBroker.GuiBroker ()['gnumed_dir']
        self.printer = wxHtmlEasyPrinting()

        self.box = wxBoxSizer(wxVERTICAL)

        infobox = wxBoxSizer(wxHORIZONTAL)
        n = wxNewId()
        self.infoline = wxTextCtrl(self, n, style=wxTE_READONLY)
        self.infoline.SetBackgroundColour(wxLIGHT_GREY)
        infobox.Add(self.infoline, 1, wxGROW|wxALL)
        self.box.Add(infobox, 0, wxGROW)

        self.html = ManualHtmlWindow(self, -1, log)
        self.html.SetRelatedFrame(frame, "")
        self.html.SetRelatedStatusBar(0)
        self.box.Add(self.html, 1, wxGROW)

        subbox = wxBoxSizer(wxHORIZONTAL)
        n = wxNewId()
        btn = wxButton(self, n, _("&Manual"))
        EVT_BUTTON(self, n, self.OnShowDefault)
        subbox.Add(btn, 1, wxGROW | wxALL, 2)

        n = wxNewId()
        btn = wxButton(self, n, _("Load File"))
        EVT_BUTTON(self, n, self.OnLoadFile)
        subbox.Add(btn, 1, wxGROW | wxALL, 2)

        n = wxNewId()
        btn = wxButton(self, n, _("Back"))
        EVT_BUTTON(self, n, self.OnBack)
        subbox.Add(btn, 1, wxGROW | wxALL, 2)

        n = wxNewId()
        btn = wxButton(self, n, _("Forward"))
        EVT_BUTTON(self, n, self.OnForward)
        subbox.Add(btn, 1, wxGROW | wxALL, 2)

        n = wxNewId()
        btn = wxButton(self, n, _("Print"))
        EVT_BUTTON(self, n, self.OnPrint)
        subbox.Add(btn, 1, wxGROW | wxALL, 2)

        n = wxNewId()
        btn = wxButton(self, n, _("View Source"))
        EVT_BUTTON(self, n, self.OnViewSource)
        subbox.Add(btn, 1, wxGROW | wxALL, 2)

        self.box.Add(subbox, 0, wxGROW)

        self.SetSizer(self.box)
        self.SetAutoLayout(true)

        self.OnShowDefault(None)

##     def __del__(self):
##         print 'ManualHtmlPanel.__del__'

    def ShowTitle(self, title):
        self.infoline.Clear()
        self.infoline.WriteText(title)

    def OnShowDefault(self, event):
        name = os.path.join(self.docdir, manual_path)
        self.html.LoadPage(name)


    def OnLoadFile(self, event):
        dlg = wxFileDialog(self, wildcard = '*.htm*', style=wxOPEN)
        if dlg.ShowModal():
            path = dlg.GetPath()
            self.html.LoadPage(path)
        dlg.Destroy()


    def OnBack(self, event):
        if not self.html.HistoryBack():
            self.log.WriteText(_("ManualHtmlWindow: No more items in history!\n"))


    def OnForward(self, event):
        if not self.html.HistoryForward():
            self.log.WriteText(_("ManualHtmlWindow: No more items in history!\n"))


    def OnViewSource(self, event):
        from wxPython.lib.dialogs import wxScrolledMessageDialog
        source = self.html.GetParser().GetSource()
        dlg = wxScrolledMessageDialog(self, source, _('HTML Source'))
        dlg.ShowModal()
        dlg.Destroy()


    def OnPrint(self, event):
        self.printer.PrintFile(self.html.GetOpenedPage())
