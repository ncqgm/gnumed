from wxPython.wx import *
import gmPlugin, gmShadow, gmLog, gmDispatcher, gmSignals, gmPG

scratchpaddata = {}
recalldata = {}

query_scratchpad = "select id, timestamp, text, author from scratchpad where id_identity=%s"
query_recalls = "select id, timestamp, reason from recalls where id_identity=%s"

class ScratchPadRecalls(wxPanel):
	def __init__(self, parent,id=-1):
		self.patientID=None
		wxPanel.__init__(self,parent,id,wxDefaultPosition,wxDefaultSize,style = wxRAISED_BORDER)
		self.parent=parent
		self.create_widgets()
		self.layout_widgets()
		self.register_interests()
		self._con = gmPG.ConnectionPool()



	def create_widgets(self):
		self.lbl_fgcolour = wxColor(0,0,131)
		self.list_fgcolour = wxColor(255,0,0)
		self.lbl_font = wxFont(12,wxSWISS,wxBOLD,wxBOLD,false,'')
		#add a label which is the heading for the text data entry 'Scratchpad'
		self.scratchpad_lbl = wxStaticText(self,-1, _("Scratch Pad"),style = wxALIGN_CENTRE) #add static text control for the capion
		self.scratchpad_lbl.SetForegroundColour(self.lbl_fgcolour)               #set caption text colour
		self.scratchpad_lbl.SetFont(self.lbl_font)
		#Add a text control under that
		self.scratchpad_txt = wxTextCtrl(self,-1,"",wxDefaultPosition,wxDefaultSize,0)
		#Add a label for the recalls/reviews list
		self.recalls_lbl = wxStaticText(self,-1, _("Recalls/Reviews"),style = wxALIGN_CENTRE) #add static text control for the capion
		self.recalls_lbl.SetForegroundColour(self.lbl_fgcolour)               #set caption text colour
		self.recalls_lbl.SetFont(self.lbl_font)

		#------------------------------------------------------------------------------
		#Add a simple listcontrol under that for scratchpad items
		#------------------------------------------------------------------------------
		self.list_scratchpad = wxListCtrl(self, -1,  wxDefaultPosition, wxDefaultSize,wxLC_REPORT|wxLC_NO_HEADER|wxSUNKEN_BORDER)
		self.list_scratchpad.SetForegroundColour(self.list_fgcolour)
		self.list_scratchpad.InsertColumn(0, _("Logged"))
		self.list_scratchpad.InsertColumn(1, "", wxLIST_FORMAT_LEFT)

		#--------------------------------------------------------------------------
		#Add a simple listcontrol under that for recall items
		#--------------------------------------------------------------------------
		self.list_recalls = wxListCtrl(self, -1,  wxDefaultPosition, wxDefaultSize,wxLC_REPORT|wxLC_NO_HEADER|wxSUNKEN_BORDER)
		self.list_recalls.SetForegroundColour(self.list_fgcolour)
		self.list_recalls.InsertColumn(0, _("Recall or Review"))
		self.list_recalls.InsertColumn(1, _("Status"), wxLIST_FORMAT_LEFT)

	def layout_widgets(self):
		self.sizer= wxBoxSizer(wxVERTICAL)
		self.sizer.Add(self.scratchpad_lbl,0,wxEXPAND)
		self.sizer.Add(self.scratchpad_txt,0,wxEXPAND)
		#sizer.Add(10,10,0,wxEXPAND)
		self.sizer.Add(self.list_scratchpad,30,wxEXPAND)
		self.sizer.Add(self.recalls_lbl,0, wxEXPAND)
		#sizer.Add(5,5,0,wxEXPAND)
		self.sizer.Add(self.list_recalls,70,wxEXPAND)
		self.SetSizer(self.sizer)  #set the sizer
		self.sizer.Fit(self)             #set to minimum size as calculated by sizer
		self.SetAutoLayout(true)                 #tell frame to use the sizer
		self.Show(true)

	def register_interests(self):
		gmDispatcher.connect(self.OnPatientID, gmSignals.patient_selected())


	def UpdateRecalls(self, patid):
		self.list_scratchpad.DeleteAllItems()
		if patid is None:
			return
		db = self._con.GetConnection('clinical')
		cur = db.cursor()
		cur.execute(query_recalls % str(patid))
		fetched = cur.fetchall()
		for index in range(len(fetched)):
			row=fetched[index]
			id=row[0]
			#date=row[1].strftime("%d.%m.%y")
			date=str(row[1])[:10]
			text=row[2]
			self.list_recalls.InsertStringItem(index, date )
			self.list_recalls.SetStringItem(index, 1, text)
			self.list_recalls.SetItemData(index, id)
		self.list_recalls.SetColumnWidth(0, wxLIST_AUTOSIZE)
		self.list_recalls.SetColumnWidth(1, 200)


	def UpdateScratchpad(self, patid):
		self.list_scratchpad.DeleteAllItems()
		self.scratchpad_txt.SetValue("")
		if patid is None:
			return
		db = self._con.GetConnection('clinical')
		cur = db.cursor()
		cur.execute(query_scratchpad % str(patid))
		fetched = cur.fetchall()
		for index in range(len(fetched)):
			row=fetched[index]
			id=row[0]
			#date=row[1].strftime("%d.%m.%y")
			date=str(row[1])[:10]
			reason=row[2]
			self.list_scratchpad.InsertStringItem(index, date)
			self.list_scratchpad.SetStringItem(index, 1, reason)
			self.list_scratchpad.SetItemData(index, id)
		self.list_scratchpad.SetColumnWidth(0, wxLIST_AUTOSIZE)
		self.list_scratchpad.SetColumnWidth(1, 200)


	def OnPatientID(self, **kwargs):
		"must be executed when the current patient changes. Updates all widgets accordingly"
		if kwargs is None:
			#new patient, blank widgets
			self.UpdateRecalls(None)
			self.UpdateSCratchpad(None)
			return

		kwds = kwargs['kwds']
		patid = kwds['ID']
		self.UpdateRecalls(patid)
		self.UpdateScratchpad(patid)




class gmGP_ScratchPadRecalls (gmPlugin.wxBasePlugin):
    """
    Plugin to encapsulate the scratch pad and recalls
    """
    def name (self):
        return 'ScratchPadRecallsPlugin'

    def register (self):
        mwm = self.gb['patient.manager']
        mwm.RegisterRightSide ('scratchpad_recalls', ScratchPadRecalls
                                   (mwm.righthalfpanel, -1), position=2)

    def unregister (self):
        self.gb['patient.manager'].Unregister ('scratchpad_recalls')
    
if __name__ == "__main__":
	app = wxPyWidgetTester(size = (400, 500))
	app.SetWidget(ScratchPadRecalls, -1)
	app.MainLoop()
