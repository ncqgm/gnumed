#!/usr/bin/python
#############################################################################
#
# gmGuiElement_DividerCaptionPanel:
# ----------------------------------
#
# This panel consists of one or more headings on a horizontal panel and is
# used to divide/head sections of the screenel There are user defined foreground
# and background colours. The captions are centred in the available space. The
# default colours are purple panel with white bold text
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
#	- implement muti column headers (currently one only)
#       - someone smart to fix the code (simplify for same result)
#       - add font size/style as option
# 
############################################################################
from wxPython.wx import *

class DividerCaptionPanel(wxPanel):
    #   def __init__(self, parent, id, title, bg_red, bg_blue, bg_green,fg_red, fg_blue, fg_green):
    #   this to be used once the rgb thingy is fixed
    def __init__(self, parent, id, title):
    	wxPanel.__init__(self, parent, id, wxDefaultPosition, wxDefaultSize, 0 )	
	sizer = wxBoxSizer(wxHORIZONTAL)	
	self.SetBackgroundColour(wxColour(197,194,255))                            #set panel background to light purple!
	#SetCaptionBackgroundColor()                                               #set panel background colour  rgb
        caption = wxStaticText(self,-1, title,style = wxALIGN_CENTRE)              #static text control for the caption
        caption.SetForegroundColour(wxWHITE)	                                   #white foreground text colour
         #SetCaptionForegroundColor()                                              #set caption text colour to rgb
	caption.SetFont(wxFont(13,wxSWISS,wxBOLD,wxBOLD,false,'xselfont'))         #TODO implement font size parameter 
        sizer.Add(caption,1,wxEXPAND)                                      #add caption to the sizer
	self.SetSizer(sizer)                                               #set the sizer 
	sizer.Fit(self)                                                    #set to minimum size as calculated by sizer
        self.SetAutoLayout(true)                                           #tell frame to use the sizer
        #self.Show(true)                                                    #show the panel   
	
    def SetCaptionBackgroundColor(self, bg_red, bg_blue, bg_green):
	self.SetBackgroundColour(wxColour(bg_red,bg_blue,bg_green))
			  
    def SetCaptionForegroundColor(self, fg_red, fg_blue, fg_green):
	self.caption.SetForegroundColour(wxColour(fg_red,fg_blue,fg_green))
	return
if __name__ == "__main__":
	app = wxPyWidgetTester(size = (200, 20))
	app.SetWidget(DividerCaptionPanel, -1," This is the heading on a divider caption panel ")
	app.MainLoop()
 
