#!/usr/bin/python
#############################################################################
#
# gmGuiElement_HeadingCaptionPanel:
# ----------------------------------
#
# This panel consists constructs a simple heading to be used at the top
# of a panel, in the form of capitalised word on user defined foreground
# and background colours. The heading is left justified curently. The
# default colours are purple panel, orange label with yellow capitalised
# words (sounds yuk doesn't it - but I like it and it works well!!!!!
# If you don't like it - change this code see @TODO!
#
# @author: Dr. Richard Terry
# @copyright: author
# @license: GPL (details at http://www.gnu.org)
# @dependencies: wxPython (>= version 2.3.1)
# @change log:
#	10.06.2002 rterry initial implementation, untested
#
# @TODO:
#	- implement user defined rgb colours
#	- implement left, right or centre justification
#       - someone smart to fix the code (simplify for same result)
#       - add font size/style as option
#       - find out why the caption text doesn't align in centre
############################################################################
from wxPython.wx import *


class HeadingCaptionPanel(wxPanel):

    def __init__ (self, parent, id, text, bgC = wxColour (197,194,255), hdrC = wxColour (255, 129, 131), txtC = wxColour (255, 255, 0)):
        self.text = text
        self.bgC = bgC
        self.hdrC = hdrC
        self.txtC = txtC
        wxPanel.__init__(self, parent, id)
        EVT_PAINT (self, self.OnPaint)
        EVT_SIZE (self, self.OnSize)
        self.w = 0
        self.h = 0

    def OnPaint (self, event):
        self.redraw (wxPaintDC (self))

    def OnSize (self, event):
        self.w, self.h = self.GetClientSizeTuple ()

    def redraw (self, dc):
        dc.SetBrush (wxBrush (self.bgC, wxSOLID))
        dc.SetPen (wxTRANSPARENT_PEN)
        dc.DrawRectangle (0, 0, self.w, self.h)
        dc.SetTextBackground (self.hdrC)
        dc.SetFont (wxFont (12, wxSWISS, wxNORMAL, wxBOLD))
        dc.SetTextForeground (self.txtC)
        txtw, txth = dc.GetTextExtent (self.text)
        bufx = txtw / 10 # buffer to left of text
        if bufx + txtw > self.w:
            bufx = 0
        bufy = (self.h - txth)/2
        if bufy < 0:
            bufy = 0
        dc.SetBrush (wxBrush (self.hdrC, wxSOLID))
        dc.DrawRectangle (bufx, bufy, txtw, txth)
        dc.DrawText (self.text, bufx, bufy) 
        
                                                  #show the panel   
	
    def SetCaptionBackgroundColor(self, bgC):
        self.bgC = bgC
        self.redraw (wxClientDC (self))
    
    def SetCaptionForegroundColor(self, hdrC):
	self.hdrC = hdrC
        self.redraw (wxClientDC (self))
    
if __name__ == "__main__":
	app = wxPyWidgetTester(size = (200, 20))
	app.SetWidget(HeadingCaptionPanel, -1,"  PAST HISTORY  ")
	app.MainLoop()
 

