from wxPython.wx import *
import gmPlugin, gmShadow, gmConf

scratchpaddata = {
1 : ("01/12/2001", "check BP next visit"),
2 : ("01/12/2001", "daughter requests dementia screen"),
}
recalldata = {
1 : ("Annual Checkup", "due in 1 month"),
2 : ("PAP smear", "overdue 6 months"),
}
class ScratchPadRecalls(wxPanel):
    def __init__(self, parent,id):
	wxPanel.__init__(self,parent,id,wxDefaultPosition,wxDefaultSize,style = wxRAISED_BORDER)
	#add a label which is the heading for the text data entry 'Scratchpad' 	
	scratchpad_lbl = wxStaticText(self,-1, "Scratch Pad",style = wxALIGN_CENTRE) #add static text control for the capion
	scratchpad_lbl.SetForegroundColour(wxColor(0,0,131))               #set caption text colour 
	scratchpad_lbl.SetFont(wxFont(12,wxSWISS,wxBOLD,wxBOLD,false,'xselfont'))
	#Add a text control under that
	scratchpad_txt = wxTextCtrl(self,-1,"",wxDefaultPosition,wxDefaultSize,0)
	#Add a label for the recalls/reviews list
	recalls_lbl = wxStaticText(self,-1, "Recalls/Reviews",style = wxALIGN_CENTRE) #add static text control for the capion
	recalls_lbl.SetForegroundColour(wxColor(0,0,131))               #set caption text colour 
	recalls_lbl.SetFont(wxFont(12,wxSWISS,wxBOLD,wxBOLD,false,'xselfont'))

        #------------------------------------------------------------------------------
	#Add a simple listcontrol under that for scratchpad items and insert dummy data
	#------------------------------------------------------------------------------
	list_scratchpad = wxListCtrl(self, -1,  wxDefaultPosition, wxDefaultSize,wxLC_REPORT|wxLC_NO_HEADER|wxSUNKEN_BORDER)
	list_scratchpad.SetForegroundColour(wxColor(255,0,0))
	list_scratchpad.InsertColumn(0, "Logged")
	list_scratchpad.InsertColumn(1, "", wxLIST_FORMAT_LEFT)
	#-------------------------------------------------------------
	#loop through the scriptdata array and add to the list control
	#note the different syntax for the first coloum of each row
	#i.e. here > self.List_Script.InsertStringItem(x, data[0])!!
	#-------------------------------------------------------------
	items = scratchpaddata.items()
	for x in range(len(items)):
            key, data = items[x]
	    print items[x]
	    #print x, data[0],data[1]
	    list_scratchpad.InsertStringItem(x, data[0])
            list_scratchpad.SetStringItem(x, 1, data[1])
            list_scratchpad.SetItemData(x, key)
	list_scratchpad.SetColumnWidth(0, wxLIST_AUTOSIZE)
        list_scratchpad.SetColumnWidth(1, 200)
	#--------------------------------------------------------------------------
	#Add a simple listcontrol under that for recall items and insert dummy data
	#--------------------------------------------------------------------------
	list_recalls = wxListCtrl(self, -1,  wxDefaultPosition, wxDefaultSize,wxLC_REPORT|wxLC_NO_HEADER|wxSUNKEN_BORDER)
	list_recalls.SetForegroundColour(wxColor(255,0,0))
	list_recalls.InsertColumn(0, "Recall or Review")
	list_recalls.InsertColumn(1, "Status", wxLIST_FORMAT_LEFT)
	
	#-------------------------------------------------------------
	#loop through the scriptdata array and add to the list control
	#note the different syntax for the first coloum of each row
	#i.e. here > self.List_Script.InsertStringItem(x, data[0])!!
	#-------------------------------------------------------------
	items = recalldata.items()
	for x in range(len(items)):
            key, data = items[x]
	    print items[x]
	    #print x, data[0],data[1]
	    list_recalls.InsertStringItem(x, data[0])
            list_recalls.SetStringItem(x, 1, data[1])
            list_recalls.SetItemData(x, key)
	list_recalls.SetColumnWidth(0, wxLIST_AUTOSIZE)
        list_recalls.SetColumnWidth(1, 200)

        sizer= wxBoxSizer(wxVERTICAL)
	sizer.Add(scratchpad_lbl,0,wxEXPAND)
	sizer.Add(scratchpad_txt,0,wxEXPAND)
	#sizer.Add(10,10,0,wxEXPAND)
        sizer.Add(list_scratchpad,30,wxEXPAND) 
	sizer.Add(recalls_lbl,0, wxEXPAND)
	#sizer.Add(5,5,0,wxEXPAND)
	sizer.Add(list_recalls,70,wxEXPAND)
	self.SetSizer(sizer)  #set the sizer 
	sizer.Fit(self)             #set to minimum size as calculated by sizer
        self.SetAutoLayout(true)                 #tell frame to use the sizer
        self.Show(true) 



class gmGP_ScratchPadRecalls (gmPlugin.wxBasePlugin):
    """
    Plugin to encapsulate the scratch pad and recalls
    """
    def name (self):
        return 'ScratchPadRecallsPlugin'

    def register (self):
        mwm = self.gb['main.manager']
        if gmConf.config['main.shadow']:
            shadow = gmShadow.Shadow (mwm, -1)
            spr = ScratchPadRecalls (shadow, -1)
            shadow.SetContents (spr)
            mwm.RegisterRightSide ('scratchpad_recalls', shadow, position=2)
        else:
            mwm.RegisterRightSide ('scratchpad_recalls', ScratchPadRecalls
                                   (mwm, -1), position=2)

    
if __name__ == "__main__":
	app = wxPyWidgetTester(size = (400, 500))
	app.SetWidget(ScratchPadRecalls, -1)
	app.MainLoop()




