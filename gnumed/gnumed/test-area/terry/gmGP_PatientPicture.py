from wxPython.wx import *

#--------------------------------
#embryonic gmGP_PatientPicture.py
#--------------------------------

class PatientPicture(wxPanel):
    def __init__(self, parent, id):
    	wxPanel.__init__(self, parent, id, wxDefaultPosition, wxDefaultSize, wxSUNKEN_BORDER )	
	
	self.sizer = wxBoxSizer(wxVERTICAL)
	#AT A BITMAP FOR PATIENT PICTURE
	wxImage_AddHandler(wxPNGHandler())
	bitmap = "any_body2.png"
	png = wxImage(bitmap, wxBITMAP_TYPE_PNG).ConvertToBitmap()
	bmp = wxStaticBitmap(self, -1, png, wxPoint(0, 0), wxSize(png.GetWidth(), png.GetHeight()))
	self.sizer.Add(bmp, 0, wxGROW|wxALIGN_CENTER_VERTICAL) # |wxALL, 10)
        self.SetSizer(self.sizer)  #set the sizer 
	self.sizer.Fit(self)             #set to minimum size as calculated by sizer
        self.SetAutoLayout(true)                 #tell frame to use the sizer
        self.Show(true)
	

     
if __name__ == "__main__":
	app = wxPyWidgetTester(size = (200, 200))
	app.SetWidget(PatientPicture, -1)
	app.MainLoop()
           
 