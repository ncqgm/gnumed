from wxPython.wx import *

#---------------------------------------------------------------
#draws a panel according to the rgb values with caption on
#left hand side consisting of user defined background and
#foreground defaults to yellow on orange
#TODO implement the rgb values, currently only yellow/orange!
#why:cause I liked that colour
#---------------------------------------------------------------
class HeadingCaptionPanel(wxPanel):
    def __init__(self, parent, id, title):
    	wxPanel.__init__(self, parent, id, wxDefaultPosition, wxDefaultSize, 0 )	
	sizer = wxBoxSizer(wxVERTICAL)	
	self.SetBackgroundColour(wxColour(197,194,255))   
	#SetCaptionBackgroundColor()                                               #set background colour  
        caption = wxStaticText(self,-1, title,style = wxALIGN_CENTRE) #add static text control for the capion
        caption.SetForegroundColour(wxWHITE)	
         #SetCaptionForegroundColor()                                               #set caption text colour 
	caption.SetFont(wxFont(14,wxSWISS,wxBOLD,wxBOLD,false,'xselfont'))
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
	app.SetWidget(HeadingCaptionPanel, -1,"This a heading caption panel")
	app.MainLoop()
 
