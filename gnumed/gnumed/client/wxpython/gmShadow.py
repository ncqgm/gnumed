"""
A module to add shadowing to an arbitrary widget
"""

from wxPython.wx import *
import gmConf

class Shadow (wxPanel):
    def __init__(self, parent, id):
        wxPanel.__init__ (self, parent, id)
        self.shadow_width = gmConf.config['main.shadow.width']
        EVT_SIZE (self, self.OnSize)
        EVT_PAINT (self, self.OnPaint)

    def SetContents (self, widget):
        """
        Widget MUST have parent=Shadow widget, and pos=(0,0)
        """
        self.contents = widget

    def OnSize (self, event):
        w, h = self.GetClientSizeTuple ()
        sw = (self.shadow_width*w)/100
        sh = (self.shadow_width*h)/100
        self.contents.SetClientSizeWH (w-sw, h-sh)

    def OnPaint (self, event):
        dc = wxPaintDC (self)
        w, h = self.GetClientSizeTuple ()
        sw = (self.shadow_width*w)/100 # set height and width by percentage
        sh = (self.shadow_width*h)/100   
        dc.SetPen (wxTRANSPARENT_PEN)
        dc.SetBrush (wxWHITE_BRUSH)
        # draw white bars
        dc.DrawRectangle (0, h-sh, w, sh)
        dc.DrawRectangle (w-sw, 0, sw, h)
        r, g, b = gmConf.config['main.shadow.colour']
        dc.SetBrush (wxBrush (wxColour (r, g, b), wxSOLID))
        # draw grey bars half as thick
        dc.DrawRectangle (sw/2, h-sh, w-sw, sh/2)
        dc.DrawRectangle (w-sw, sh/2, sw/2, h-sh-sh/2)
