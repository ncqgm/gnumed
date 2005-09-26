# GnuMed ...
# licnese: GPL

#===============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/patient/gmGP_ScratchPadRecalls.py,v $
# $Id: gmGP_ScratchPadRecalls.py,v 1.16 2005-09-26 18:01:53 ncq Exp $
__version__ = "$Revision: 1.16 $"

try:
	import wxversion
	import wx
except ImportError:
	from wxPython import wx

import gmPlugin, gmShadow, gmLog, gmDispatcher, gmSignals, gmPG
from  gmPatientHolder import PatientHolder
scratchpaddata = {}
recalldata = {}

query_scratchpad = "select id, timestamp, text, author from scratchpad where id_identity=%s"
query_recalls = "select id, timestamp, reason from recalls where id_identity=%s"

#===============================================================
class ScratchPadRecalls(wxPanel, PatientHolder):
	def __init__(self, parent,id=-1):
		self.patientID=None
		wxPanel.__init__(self,parent,id,wxDefaultPosition,wxDefaultSize,style = wxRAISED_BORDER)
		PatientHolder.__init__(self)
		self.parent=parent
		self.create_widgets()
		self.layout_widgets()
		self.register_interests()
		self._con = gmPG.ConnectionPool()



	def create_widgets(self):
		self.lbl_fgcolour = wxColor(0,0,131)
		self.list_fgcolour = wxColor(255,0,0)
		self.lbl_font = wxFont(12,wxSWISS,wxNORMAL, wxBOLD,False,'')
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
		self.SetAutoLayout(True)                 #tell frame to use the sizer
		self.Show(True)

	def register_interests(self):
		#gmDispatcher.connect(self.OnPatientID, gmSignals.patient_selected())
		pass

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

#===============================================================
class gmGP_ScratchPadRecalls (gmPlugin.wxBasePlugin):
    """
    Plugin to encapsulate the scratch pad and recalls
    """
    def name (self):
        return 'ScratchPadRecallsPlugin'

    def register (self):
        mwm = self.gb['clinical.manager']
        mwm.RegisterRightSide ('scratchpad_recalls', ScratchPadRecalls
                                   (mwm.righthalfpanel, -1), position=2)

    def unregister (self):
        self.gb['clinical.manager'].Unregister ('scratchpad_recalls')

#===============================================================    
# Main
#===============================================================
if __name__ == "__main__":
	app = wxPyWidgetTester(size = (400, 500))
	app.SetWidget(ScratchPadRecalls, -1)
	app.MainLoop()
#===============================================================
# $Log: gmGP_ScratchPadRecalls.py,v $
# Revision 1.16  2005-09-26 18:01:53  ncq
# - use proper way to import wx26 vs wx2.4
# - note: THIS WILL BREAK RUNNING THE CLIENT IN SOME PLACES
# - time for fixup
#
# Revision 1.15  2004/07/18 20:30:54  ncq
# - wxPython.true/false -> Python.True/False as Python tells us to do
#
# Revision 1.14  2003/11/17 10:56:42  sjtan
#
# synced and commiting.
#
# Revision 1.2  2003/10/25 08:29:40  sjtan
#
# uses gmDispatcher to send new currentPatient objects to toplevel gmGP_ widgets. Proprosal to use
# yaml serializer to store editarea data in  narrative text field of clin_root_item until
# clin_root_item schema stabilizes.
#
# Revision 1.1  2003/10/23 06:02:40  sjtan
#
# manual edit areas modelled after r.terry's specs.
#
# Revision 1.13  2003/04/05 00:39:23  ncq
# - "patient" is now "clinical", changed all the references
#
# Revision 1.12  2003/02/02 13:37:27  ncq
# - typo
#
# Revision 1.11  2003/02/02 13:36:52  ncq
# - cvs metadata keywords
#
