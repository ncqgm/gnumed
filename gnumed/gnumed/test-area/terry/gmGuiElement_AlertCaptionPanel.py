#!/usr/bin/python
#############################################################################
#
# gmGuiElement_AlertCaptionPanel:
# ----------------------------------
#
# This panel consists constructs a simple heading to be used at the bottom
# of the screen, in the form of capitalised word on user defined foreground
# and background colours. The heading is left justified curently. The
# default colours are black text on intermediate grey so as to not make it
# too intrusive. The alert text will appear in flashing red text
#
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
#	- implement flashing text on the rest of the panel!
#       - someone smart to fix the code (simplify for same result)
#       - add font size/style as option
############################################################################
from wxPython.wx import *


class AlertCaptionPanel(wxPanel):
#   def __init__(self, parent, id, title, bg_red, bg_blue, bg_green,fg_red, fg_blue, fg_green):
#   this to be used once the rgb thingy is fixed
	def __init__(self, parent, id, title):
		wxPanel.__init__(self, parent, id, wxDefaultPosition, wxDefaultSize, 0 )
		self.SetBackgroundColour(wxColour(222,222,222))                            #set main panel background color
		sizer  = wxBoxSizer(wxHORIZONTAL)
		#SetCaptionBackgroundColor()                                               #set background colour with rgb  TODO
		#-----------------------------------------------
		#create a panel which will hold the caption
		#add the title to it, set the colours
		#stick it on a sizer with a cap above and below
		#----------------------------------------------
		captionpanel = wxPanel(self,-1,size = (400,10))
		captionpanel.SetBackgroundColour(wxColour(197,194,197))                    #intermediate gray
		caption = wxStaticText(captionpanel,-1, title,style = wxALIGN_CENTRE_VERTICAL)   # static text for the caption
		caption.SetForegroundColour(wxColour(0,0,0))	                           #black as... 
		#SetCaptionForegroundColor()                                               #set caption text colour rgb TODO
		caption.SetFont(wxFont(10,wxSWISS,wxBOLD,wxBOLD,false,'xselfont'))
		sizer.Add(captionpanel,1,wxEXPAND|wxALL,2)
                sizer.Add(0,9,6)
		self.SetSizer(sizer)                                               #set the sizer 
		sizer.Fit(self)                                                    #set to minimum size as calculated by sizer
		self.SetAutoLayout(true)                                           #tell frame to use the sizer
		#self.Show(true) #showing done by manager!                                                    #show the panel   
		
	def SetCaptionBackgroundColor(self, bg_red, bg_blue, bg_green):
		self.SetBackgroundColour(wxColour(bg_red,bg_blue,bg_green))
		return		  
	def SetCaptionForegroundColor(self, fg_red, fg_blue, fg_green):
		self.caption.SetForegroundColour(wxColour(fg_red,fg_blue,fg_green))
		return
	
if __name__ == "__main__":
		app = wxPyWidgetTester(size = (50, 20))
		app.SetWidget(AlertCaptionPanel, -1,"  Alerts  ")
		app.MainLoop()
	
