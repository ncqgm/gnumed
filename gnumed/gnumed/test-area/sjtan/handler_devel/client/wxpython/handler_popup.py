from wxPython.wx import *

class handler_popup ( wxPopupTransientWindow):
	def __init__(self, parent, message):
		wxPopupTransientWindow.__init__(self, parent, wxSIMPLE_BORDER)
	
		panel = wxPanel(self, -1)
		st = wxStaticText(panel, -1, message)
		sz = st.GetBestSize()
		panel.SetSize((sz.width + 20, sz.height + 20))		
		self.SetSize( (sz.width+20, sz.height + 20) )
		offsets = parent.GetSize()
		pos = parent.ClientToScreen( (0,0))
		self.Position( pos, (0, sz.height) )
		self.Popup()
		
