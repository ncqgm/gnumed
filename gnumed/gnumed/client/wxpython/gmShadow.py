"""
A module to add shadowing to an arbitrary widget
"""

from wxPython.wx import *
import gmConf

class Shadow (wxPanel):
    def __init__(self, parent, id):
        wxPanel.__init__ (self, parent, id)
        self.sw = gmConf.config['main.shadow.width']
        EVT_SIZE (self, self.OnSize)
        EVT_PAINT (self, self.OnPaint)

    def SetContents (self, widget):
        """
        Widget MUST have parent=Shadow widget, and pos=(0,0)
        """
        self.contents = widget

    def OnSize (self, event):
        w, h = self.GetClientSizeTuple ()
        self.contents.SetClientSizeWH (w-self.sw, h-self.sw)

    def OnPaint (self, event):
        dc = wxPaintDC (self)
        w, h = self.GetClientSizeTuple ()
        dc.SetPen (wxTRANSPARENT_PEN)
        #dc.SetBrush (wxWHITE_BRUSH)
        dc.SetBrush (wxBrush (wxColour (240, 240, 240), wxSOLID))
        # draw white bars
        dc.DrawRectangle (0, h-self.sw, w, self.sw)
        dc.DrawRectangle (w-self.sw, 0, self.sw, h)
        r, g, b = gmConf.config['main.shadow.colour']
        dc.SetBrush (wxBrush (wxColour (r, g, b), wxSOLID))
        # draw grey bars half as thick
        dc.DrawRectangle (self.sw/2, h-self.sw, w-self.sw, self.sw/2)
        dc.DrawRectangle (w-self.sw, self.sw/2, self.sw/2, h-self.sw-self.sw/2)
