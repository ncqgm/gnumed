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
#   def __init__(self, parent, id, title, bg_red, bg_blue, bg_green,fg_red, fg_blue, fg_green):
#   this to be used once the rgb thingy is fixed
    def __init__(self, parent, id, title):
    	wxPanel.__init__(self, parent, id, wxDefaultPosition, wxDefaultSize, 0 )
	self.SetBackgroundColour(wxColour(197,194,255))                            #set main panel background color
	#SetCaptionBackgroundColor()                                               #set background colour with rgb  TODO
	#-----------------------------------------------
        #create a panel which will hold the caption
	#add the title to it, set the colours
	#stick it on a sizer with a cap above and below
	#----------------------------------------------
        captionpanel = wxPanel(self,-1)
	captionpanel.SetBackgroundColour(wxColour(255,129,131))                    #sort of pinky orange
        caption = wxStaticText(captionpanel,-1, title,style = wxALIGN_CENTRE_VERTICAL)      # static text for the caption
        caption.SetForegroundColour(wxColour(255,255,0))	
        #SetCaptionForegroundColor()                                               #set caption text colour rgb TODO
	caption.SetFont(wxFont(10,wxSWISS,wxBOLD,wxBOLD,false,'xselfont'))
        captionsizer = wxBoxSizer(wxVERTICAL)
        captionsizer.Add(0,0,1)                                           #(n,0,0) n= units of space)
	captionsizer.Add(captionpanel,5,wxEXPAND)
	captionsizer.Add(0,0,1)
        #----------------------------------------------------------------
	#create the main background sizer to stick the captionpanel on to
	#----------------------------------------------------------------
        sizer = wxBoxSizer(wxHORIZONTAL)                                   #background sizer
	sizer.Add(10,1,0)
        sizer.Add(captionsizer,1,wxEXPAND)                                 #add captionsizer with caption
	sizer.Add(0,0,4)
	self.SetSizer(sizer)                                               #set the sizer 
	sizer.Fit(self)                                                    #set to minimum size as calculated by sizer
        self.SetAutoLayout(true)                                           #tell frame to use the sizer
        self.Show(true)                                                    #show the panel   
	
    def SetCaptionBackgroundColor(self, bg_red, bg_blue, bg_green):
	self.SetBackgroundColour(wxColour(bg_red,bg_blue,bg_green))
	return		  
    def SetCaptionForegroundColor(self, fg_red, fg_blue, fg_green):
	self.caption.SetForegroundColour(wxColour(fg_red,fg_blue,fg_green))
	return
    
if __name__ == "__main__":
	app = wxPyWidgetTester(size = (200, 20))
	app.SetWidget(HeadingCaptionPanel, -1,"  PAST HISTORY  ")
	app.MainLoop()
 
