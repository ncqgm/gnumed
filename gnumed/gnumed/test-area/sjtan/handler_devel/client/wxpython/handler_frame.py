from  wxPython.wx import *
import re

		


class ListFrame( wxFrame):
	def __init__(self, parent, id, title = "list"):
		wxFrame.__init__(self, parent,  id, title, style= wxFRAME_FLOAT_ON_PARENT |wxFRAME_TOOL_WINDOW |wxMINIMIZE_BOX |wxMAXIMIZE_BOX  )
		self.is_filter = 0
		self.index = 0
		self.listbox_selector  = wxListBox( self, wxNewId())
		self.list_getter = None		
		self.selection_filter = None
		self.pre_filter_sink = None
		self.set_control(parent)	 

	def get_listbox(self):
		return self.listbox_selector

	def set_list_getter(self, getter):
		self.list_getter = getter

	def set_pre_filter_sink( self, sink):
		self.pre_filter_sink = sink

	def set_selection_filter( self, filter):
		self.selection_filter = filter

	def update_list(self, keyEvent):
		if self.list_getter <> None:
			self.set_list( self.list_getter(keyEvent) )
	
	def set_list(self, list):	
		self.selection_list = list
		self.set_ui_list( list)
		
	def set_ui_list(self, list):	
		self.listbox_selector.Clear()
		for x in list:
			self.listbox_selector.Append(x)
			print "added to list box:", x
			

	def set_list_listener( self, listener):
		id =self.listbox_selector.GetId()
		EVT_LISTBOX( self.listbox_selector, id, listener)


	def set_control(self, control):
		self.control = control
	
		EVT_RIGHT_DOWN( self.control, self.show_frame)
		EVT_KILL_FOCUS( self. control, self.hide_frame)
		EVT_CHAR( self.control, self.check_for_activate_and_navigate_keys)
		EVT_LISTBOX( self.listbox_selector, self.listbox_selector.GetId(), self.transfer_selection_to_control)

		control.SetToolTipString('right-click for selection')

#---------------
	def check_for_activate_and_navigate_keys(self, keyEvent):
		"""handle key events in 2 states. When Showing,
	 		handle list selection keys;
			 when not showing, handle activation of listbox_selector """


		if not self.IsShown():
			self.check_for_activation_key_press(keyEvent) 
			return

		self.check_for_scroll_list_up(keyEvent)
		self.check_for_scroll_list_down(keyEvent)
		self.check_for_keyed_make_selection(keyEvent)
		self.check_for_keyed_abandon_selection(keyEvent)		
	
		keyEvent.Skip()

#-----------------------------
	def check_for_activation_key_press( self, keyEvent):
		if keyEvent.GetKeyCode() == WXK_SPACE and keyEvent.ControlDown():
			self.show_frame(keyEvent)
			self.index = -1
		keyEvent.Skip()

	def check_for_scroll_list_up( self, keyEvent):
		if  keyEvent.GetKeyCode() == WXK_UP and self.index >= 0 :
			self.index = self.index - 1
			self.listbox_selector.SetSelection(self.index)
			self.adjust_scroll_listbox()

	
	def check_for_scroll_list_down( self, keyEvent):
		if keyEvent.GetKeyCode() == WXK_DOWN and self.index < self.listbox_selector.GetCount():
			self.index = self.index + 1
			self.listbox_selector.SetSelection(self.index)
			self.adjust_scroll_listbox()
		
	def  check_for_keyed_abandon_selection(self, keyEvent):
		if (keyEvent.GetKeyCode() == WXK_ESCAPE):
			self.Show(0)

	def check_for_keyed_make_selection( self, keyEvent):
		if  keyEvent.GetKeyCode() == WXK_RETURN  \
		or keyEvent.GetKeyCode() == WXK_SPACE \
				 :
			print "selected", self.index
			event = wxCommandEvent(wxEVT_COMMAND_LISTBOX_SELECTED, self.listbox_selector.GetId() )
			event.SetEventObject(self.listbox_selector)
			event.SetString(self.listbox_selector.GetString(self.index))
			self.listbox_selector.ProcessEvent(event)
			self.Show(0)
					



#-----------------
	def adjust_scroll_listbox(self):
		"""unable to find a way of getting at scrolling attributes of listbox"""		

		lb = self.listbox_selector
		
		if lb.GetCount() == 0:
			return

		# not useful , the following has been tried
		#sz = self.GetVirtualSize()
		#vsz = lb.GetVirtualSize()
		#print "ClientSize", self.GetClientSize(),lb.GetClientSize()
		#print "GetScrollPos", lb.GetScrollPos(wxVERTICAL)
		#page = self.index / lb.GetCount()  * pages

	#	#print "page vs pages = ", page, pages

	

	def set_is_filtering(self, is_filter):
		self.is_filter = is_filter
		if is_filter:
			self.control.SetToolTipString(\
			" right-click for selection for text completion")

	def get_filter_list(self, filter):
		list = []
		for x in self.selection_list:
			if x.lower().startswith(filter.lower()):
				list.append(x)
		return list

#----------------
	def restrict_list_to_strings_starting_with(self, prefix):
		list =  self.get_filter_list(prefix) 
		if list == []:
			self.SetTitle('Nothing beginning with'+ prefix )
		self.set_ui_list(list)
		
#----------------
	def show_frame(self, event):
		self.update_list(event)
		if self.is_filter :
			self.restrict_list_to_strings_starting_with(event.GetEventObject().GetValue() ) 
		
		sz = self.listbox_selector.GetAdjustedBestSize()
		if sz.width > 800:
			sz.width = 800
		self.SetSize( ( sz.width + 10, sz.height + 10) )
		pos = self.control.ClientToScreen((0,0))
		self.CentreOnParent()
	
		
		self.Show(1)

#----------------
	def hide_frame( self, event):
		self.Show(0)
		event.Skip()

#----------------	
	def transfer_selection_to_control(self, event):
		text = event.GetString()
		if self.pre_filter_sink <> None:
			self.pre_filter_sink(event)
		if self.selection_filter <> None:
			text = self.selection_filter(event)
		self.control.SetValue( text)
		
		#try:
		#	self.control.SetSelection(0, len(event.GetString() ) )
		#except:
		#	print "error with SetSelection"
		self.Show(0)
	

class MyFrame(wxFrame):
    def __init__(self, *args, **kwds):
        # begin wxGlade: MyFrame.__init__
        kwds["style"] = wxDEFAULT_FRAME_STYLE
        wxFrame.__init__(self, *args, **kwds)
	self.text_ctrl_1 = wxTextCtrl( self, 4, "text")

        self.__set_properties()
        self.__do_layout()
        # end wxGlade

    def __set_properties(self):
        # begin wxGlade: MyFrame.__set_properties
        self.SetTitle("frame_1")
        # end wxGlade


    def __do_layout(self):
        # begin wxGlade: MyFrame.__do_layout
        sizer_1 = wxBoxSizer(wxVERTICAL)
        sizer_1.Add(self.text_ctrl_1, 1, wxEXPAND, 0)
        self.SetAutoLayout(1)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        sizer_1.SetSizeHints(self)
        self.Layout()
        # end wxGlade
	list = ListFrame(self, 4)
	list.set_list ( ['penicillin', 'bactrim'])
	list.set_control( self.text_ctrl_1)
	list.set_is_filtering(1)
	

# end of class MyFrame:wq


class MyApp( wxApp) :
        def OnInit(self):

                wxInitAllImageHandlers()
                frame = MyFrame( None, -1, "Harry")
	#	e = EventHandle( frame.panel_1)
		frame.SetSize((300,300)	)
                self.SetTopWindow(frame)
                frame.Show()
                return true

def main():
        app = MyApp(0)
        app.MainLoop()

if __name__ == '__main__':
        main()

	
	
	
