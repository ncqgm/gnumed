#!/usr/bin/python
#############################################################################
#
# gmContacts.py
# ----------------------------------
#
# This panel is a contact manager to display and allow the
# use to add/delete/edit organisations,branches, persons
#
# If you don't like it - change this code see @TODO!
#
# @author Dr. Richard Terry
# @copyright: authorcd
# @license: GPL (details at http://www.gnu.org)
# @dependencies: wxPython (>= version 2.3.1)
# @change log:
#	    02.07.2002 rterry initial implementation, untested
#
# @TODO:almost everything
#       contains dummy data only
#	implemented for gui presentation only
#      
############################################################################

from wxPython.wx import *
import gmPlugin
import images_contacts_toolbar16_16
ID_ORGANISATIONSLIST = wxNewId()
ID_ALL_MENU  = wxNewId()
ID_COMBOTYPE = wxNewId()
DISPLAYPERSON = 0
organisationsdata = {
1 : ("John Hunter Hospital","", "Lookout Rd NEW LAMBTON HEIGHTS","Public Hospital","02 49213000"),
2 : (" ","Cardiovascular Department", "","", "49214200"),
3 : ( " ","- Dr L Smith","Cardiologist","lsmith@cardiology.jhh.com.au", "0148 222 222"),
4 : (" ","Department of Surgery", "","", "49214200"),
5 : ( " ","- Dr No Brains","Colorectal surgeon","nobrainer@surgery.jhh.com.au", "0148 111 111"),	
6 : ("Belmont District Hospital","", "Lake Rd BELMONT","Public Hospital","02 49421111"),
7 : (" ","Physiotherapy", "","", "49423567"),
8 : ( " ","- P Lang","Sports Physiotherapist","plang@jphysio.bdh.com.au", "494223568"),		     
9 : ( " ","- L Short","Physiotherapist","lshort@jphysio.bdh.com.au", "494223568"),	
}

ID_SAVESQL = wxNewId()
ID_SEARCHGLOBAL= wxNewId()
ID_ORGANISATIONDISPLAY = wxNewId()
ID_GENERALPRACTICESDISPLAY = wxNewId()
ID_DOCTORSDISPLAY = wxNewId()
ID_PERSONSDISPLAY = wxNewId()
ID_ORGANISATIONADD = wxNewId()
ID_BRANCHDEPTADD = wxNewId()
ID_EMPLOYEEADD = wxNewId()
ID_PERSONADD = wxNewId()
ID_RELOAD = wxNewId()
ID_SEARCHSPECIFIC = wxNewId()
ID_SORTA_Z = wxNewId()
ID_SORTZ_A = wxNewId()
ID_SENDEMAIL = wxNewId()
ID_LINKINTERNET = wxNewId()
ID_INSTANTREPORT = wxNewId()
ID_REPORTS = wxNewId()
ID_SAVE = wxNewId()

#--------------------------------------------------
#Class which shows a blue bold label left justified
#--------------------------------------------------
class BlueLabel(wxStaticText):
	def __init__(self, parent, id, prompt):
		wxStaticText.__init__(self,parent, id,prompt,wxDefaultPosition,wxDefaultSize,wxALIGN_LEFT) 
		self.SetFont(wxFont(12,wxSWISS,wxBOLD,wxNORMAL,false,''))
		self.SetForegroundColour(wxColour(0,0,131))
class DarkBlueHeading(wxStaticText):
       def __init__(self, parent, id, prompt):
	        wxStaticText.__init__(self,parent, id,prompt,wxDefaultPosition,wxDefaultSize,wxALIGN_CENTER) 
		self.SetFont(wxFont(12,wxSWISS,wxBOLD,wxBOLD,false,''))
		self.SetForegroundColour(wxColour(0,0,255))
#------------------------------------------------------------
#text control class to be later replaced by the gmPhraseWheel
#------------------------------------------------------------
class TextBox_RedBold(wxTextCtrl):
	def __init__ (self, parent, id): #, wxDefaultPostion, wxDefaultSize):
		wxTextCtrl.__init__(self,parent,id,"",wxDefaultPosition, wxDefaultSize,wxSIMPLE_BORDER)
		self.SetForegroundColour(wxColor(255,0,0))
		self.SetFont(wxFont(12,wxSWISS,wxBOLD,wxBOLD,false,''))
class TextBox_BlackNormal(wxTextCtrl):
	def __init__ (self, parent, id): #, wxDefaultPostion, wxDefaultSize):
		wxTextCtrl.__init__(self,parent,id,"",wxDefaultPosition, wxDefaultSize,wxSIMPLE_BORDER)
		self.SetForegroundColour(wxColor(0,0,0))
		self.SetFont(wxFont(12,wxSWISS,wxBOLD,wxBOLD,false,''))

class ContactsPanel(wxPanel):
       def __init__(self, parent,id):
	  wxPanel.__init__(self, parent, id,wxDefaultPosition,wxDefaultSize,wxRAISED_BORDER)                     
          #-----------------------------------------------------------------
          #create top list box which will show organisations, employees, etc
	  #-----------------------------------------------------------------
	  self.list_organisations = wxListCtrl(self, ID_ORGANISATIONSLIST,  wxDefaultPosition, wxDefaultSize,wxLC_REPORT|wxLC_NO_HEADER|wxSUNKEN_BORDER)
          self.list_organisations.SetForegroundColour(wxColor(74,76,74))
	  self.list_organisations.SetFont(wxFont(10,wxSWISS, wxNORMAL, wxNORMAL, false, 'xselfont'))
          #----------------------------------------	  
          # add some dummy data to the allergy list
	  self.list_organisations.InsertColumn(0, "Organisation")
	  self.list_organisations.InsertColumn(1, "Employees")
	  self.list_organisations.InsertColumn(2, "")
	  self.list_organisations.InsertColumn(3, "Category/Email")
	  self.list_organisations.InsertColumn(4, "Phone")
     
	  #-------------------------------------------------------------
	  #loop through the scriptdata array and add to the list control
	  #note the different syntax for the first coloum of each row
	  #i.e. here > self.list_organisations.InsertStringItem(x, data[0])!!
	  #-------------------------------------------------------------
	  items = organisationsdata.items()
	  for x in range(len(items)):
	      key, data = items[x]
	      #print items[x]
	      #print x, data[0],data[1],data[2]
	      self.list_organisations.InsertStringItem(x, data[0])
	      self.list_organisations.SetStringItem(x, 1, data[1])
	      self.list_organisations.SetStringItem(x, 2, data[2])
	      self.list_organisations.SetStringItem(x, 3, data[3])
	      self.list_organisations.SetStringItem(x, 4, data[4])
	      self.list_organisations.SetItemData(x, key)
	  self.list_organisations.SetColumnWidth(0, wxLIST_AUTOSIZE)
          self.list_organisations.SetColumnWidth(1, wxLIST_AUTOSIZE)
	  self.list_organisations.SetColumnWidth(2, wxLIST_AUTOSIZE)
	  self.list_organisations.SetColumnWidth(3, wxLIST_AUTOSIZE)
	  self.list_organisations.SetColumnWidth(4, wxLIST_AUTOSIZE)

      	  #--------------------
          #create static labels
	  #--------------------
	  self.lbl_heading = DarkBlueHeading(self,-1,"Organisation")
	  self.lbl_org_name = BlueLabel(self,-1,"Name")
	  self.lbl_Type = BlueLabel(self,-1,"Office")
	  self.lbl_org_street = BlueLabel(self,-1,"Street")
	  self.lbl_org_suburb = BlueLabel(self,-1,"Suburb")
	  self.lbl_org_state = BlueLabel(self,-1,"State")                   #eg NSW
	  self.lbl_org_zip = wxStaticText(self,id,"Zip",wxDefaultPosition,wxDefaultSize,wxALIGN_CENTRE) 
	  self.lbl_org_zip.SetFont(wxFont(12,wxSWISS,wxBOLD,wxNORMAL,false,''))
	  self.lbl_org_zip.SetForegroundColour(wxColour(0,0,131))
	  #self.lbl_org_zip = BlueLabel(self,-1,"Zip")
	  self.lbl_org_category = BlueLabel(self,-1,"Category")
	  #self.lbl_pers_occupation =  BlueLabel(self,-1,"Occupation")
	  self.lbl_org_user1 = BlueLabel(self,-1,"User1")
	  self.lbl_org_user2 = BlueLabel(self,-1,"User2")
	  self.lbl_org_user3 = BlueLabel(self,-1,"User3")
	  self.lbl_org_phone = BlueLabel(self,-1,"Phone")
	  self.lbl_org_fax = BlueLabel(self,-1,"Fax")
          self.lbl_org_email = BlueLabel(self,-1,"Email")	 
          self.lbl_org_internet = BlueLabel(self,-1,"Internet")
	  self.lbl_org_mobile = BlueLabel(self,-1,"Mobile")
          self.lbl_org_memo = BlueLabel(self,-1,"Memo")
          	  
          #--------------------
	  #create the textboxes
          #--------------------
	  self.txt_org_name = TextBox_RedBold(self,-1)
	  self.txt_org_type = TextBox_RedBold(self,-1)          #head office, branch or department
	  self.txt_org_street = wxTextCtrl(self, 30,"",wxDefaultPosition,wxDefaultSize, style=wxTE_MULTILINE|wxNO_3D|wxSIMPLE_BORDER)
	  self.txt_org_street.SetForegroundColour(wxColor(255,0,0))
	  self.txt_org_street.SetFont(wxFont(12,wxSWISS,wxBOLD,wxBOLD,false,''))
	  self.txt_org_suburb = TextBox_RedBold(self,-1)
	  self.txt_org_zip = TextBox_RedBold(self,-1)
	  self.txt_org_state = TextBox_RedBold(self,-1) #for user defined fields later
	  self.txt_org_user1 = TextBox_BlackNormal(self,-1)
	  self.txt_org_user2 = TextBox_BlackNormal(self,-1)
	  self.txt_org_user3 = TextBox_BlackNormal(self,-1)
	  self.txt_org_category = TextBox_BlackNormal(self,-1)
	  #self.txt_pers_occupation = TextBox_BlackNormal(self,-1)
	  self.txt_org_phone = TextBox_BlackNormal(self,-1)
	  self.txt_org_fax = TextBox_BlackNormal(self,-1)
	  self.txt_org_mobile = TextBox_BlackNormal(self,-1)
	  self.txt_org_email = TextBox_BlackNormal(self,-1)
	  self.txt_org_internet = TextBox_BlackNormal(self,-1)
	  self.txt_org_memo = wxTextCtrl(self, 30,
                        "This company never pays its bills \n"
                        "Insist on pre-payment before sending report",
                         wxDefaultPosition,wxDefaultSize, style=wxTE_MULTILINE|wxNO_3D|wxSIMPLE_BORDER)
          self.txt_org_memo.SetInsertionPoint(0)
	  self.txt_org_memo.SetFont(wxFont(12,wxSWISS, wxNORMAL, wxNORMAL, false, ''))
          self.combo_type = wxComboBox(self, ID_COMBOTYPE, "", wxDefaultPosition,wxDefaultSize, ['Head Office','Branch','Department'], wxCB_READONLY ) #wxCB_DROPDOWN)
          self.combo_type.SetForegroundColour(wxColor(255,0,0))
	  self.combo_type.SetFont(wxFont(12,wxSWISS,wxBOLD,wxBOLD,false,''))
	  #----------------------
	  #create the check boxes
	  #----------------------
	  #self.chbx_headoffice = wxCheckBox(self, -1, " Head Office ", wxDefaultPosition,wxDefaultSize, wxNO_BORDER)
	  self.chbx_postaladdress = wxCheckBox(self, -1, " Postal Address ", wxDefaultPosition,wxDefaultSize, wxNO_BORDER)
	  #self.chbx_branch_department = wxCheckBox(self, -1, " Branch/Department ", wxDefaultPosition,wxDefaultSize, wxNO_BORDER)
          #-------------------------------------------
	  #create the sizers for each line of controls
	  #-------------------------------------------
	  self.sizer_line0 = wxBoxSizer(wxHORIZONTAL)
	  self.sizer_line1 = wxBoxSizer(wxHORIZONTAL)
	  self.sizer_line1a = wxBoxSizer(wxHORIZONTAL)
	  self.sizer_line2 = wxBoxSizer(wxHORIZONTAL)
	  self.sizer_line3 = wxBoxSizer(wxHORIZONTAL)
	  self.sizer_line4 = wxBoxSizer(wxHORIZONTAL)
	  self.sizer_line5 = wxBoxSizer(wxHORIZONTAL)
	  self.sizer_line6 = wxBoxSizer(wxHORIZONTAL)
	  self.sizer_line7 = wxBoxSizer(wxHORIZONTAL)
	  self.sizer_line8 = wxBoxSizer(wxHORIZONTAL)
	  self.sizer_line9 = wxBoxSizer(wxHORIZONTAL)
	  self.sizer_line10 = wxBoxSizer(wxHORIZONTAL)
	  self.sizer_line11 = wxBoxSizer(wxHORIZONTAL)
	  self.sizer_line0.Add(0,10,1)
	  #--------------------------------------
	  #Heading at top of the left hand column
	  #--------------------------------------
	  self.sizer_line0.Add(0,0,4)
	  self.sizer_line0.Add(self.lbl_heading,40,wxEXPAND|wxALIGN_CENTER)
	  self.sizer_line0.Add(0,0,48)
	  #---------------------------------------------
	  #line one:surname, organisation name, category
	  #---------------------------------------------
	  self.sizer_line1.Add(self.lbl_org_name,4, wxALIGN_CENTER_VERTICAL,5)
          self.sizer_line1.Add(self.txt_org_name,40,wxEXPAND)
	  self.sizer_line1.Add(0,0,4)
	  self.sizer_line1.Add(self.lbl_org_category,8,wxALIGN_CENTER_VERTICAL, 5)
	  self.sizer_line1.Add(self.txt_org_category,36,wxEXPAND)
	  #--------------------------------------------------------------
	  #line onea:type of organisation:headoffice,branch of department
	  #--------------------------------------------------------------
	  
	  #self.sizer_line1a.Add(0,0,4)
	  self.sizer_line1a.Add(self.lbl_Type,4, wxALIGN_LEFT,5)
	  self.sizer_line1a.Add(self.combo_type,20,wxEXPAND)
	  self.sizer_line1a.Add(self.txt_org_type,20,wxEXPAND)
	  
	  self.sizer_line1a.Add(0,0,4)
	  if DISPLAYPERSON == 1:
		  self.sizer_line1a.Add(self.lbl_pers_occupation,8,wxALIGN_CENTER_VERTICAL, 5)
		  self.sizer_line1a.Add(self.txt_pers_occupation,36,wxEXPAND)
	  else:
	          self.sizer_line1a.Add(0,0,44)
		  #self.lbl_pers_occupation.Hide
		  #self.txt_pers_occupation.Hide
		  
	  #--------------------------------------------
	  #line two:street, + blank line under category
	  #design of sizer_line2_forphone: (Horizontal box sizer)
	  #                           |lbl_org_phone + txt_org_phone   |
	  #
	  #this is then added to:
	  #design of sizer_line2_rightside (verticalbox sizer)
	  #                           |blank line                      |
	  #                           |sizer_line2_forphone            |   
	  #
	  #sizer_line2_rightside is then added to sizerline2:
	  # -----------------------------------------------------------
	  # street stuff on sizerline2 | spacer | sizer_line2_rightside|
	  #------------------------------------------------------------
	  self.sizer_line2_rightside = wxBoxSizer(wxVERTICAL)
          self.sizer_line2_forphone = wxBoxSizer(wxHORIZONTAL)
	  self.sizer_line2_forphone.Add(self.lbl_org_phone,8,wxGROW,wxALIGN_CENTER_VERTICAL,5)
	  self.sizer_line2_forphone.Add(self.txt_org_phone,36,wxEXPAND)
	  self.sizer_line2_forfax = wxBoxSizer(wxHORIZONTAL)
	  self.sizer_line2_forfax.Add(self.lbl_org_fax,8,wxGROW,wxALIGN_CENTER_VERTICAL,5)
	  self.sizer_line2_forfax.Add(self.txt_org_fax,36,wxEXPAND)
	  self.sizer_line2_rightside.AddSizer(self.sizer_line2_forphone,2,wxEXPAND)
	  self.sizer_line2_rightside.AddSizer(self.sizer_line2_forfax,2,wxEXPAND)
	  self.sizer_line2.Add(self.lbl_org_street,4,wxGROW|wxALIGN_CENTER_VERTICAL,5)
	  self.sizer_line2.Add(self.txt_org_street,40,wxEXPAND)
	  self.sizer_line2.Add(0,0,4)
	  self.sizer_line2.AddSizer(self.sizer_line2_rightside,44,wxEXPAND)
	  #----------------------------------------------------
	  #line three:suburb, state, zip code, organisation fax 
	  #----------------------------------------------------
          self.sizer_line3.Add(self.lbl_org_suburb,4,wxEXPAND|wxALIGN_CENTER_VERTICAL)
	  self.sizer_line3.Add(self.txt_org_suburb,40,wxEXPAND)
	  self.sizer_line3.Add(0,0,4)
	  self.sizer_line3.Add(self.lbl_org_email,8,wxGROW|wxALIGN_CENTER_VERTICAL)
	  self.sizer_line3.Add(self.txt_org_email,36,wxEXPAND)
	  
	 

	  #-----------------------------------------------
	  #line four: head office checkbox, email text box
	  #-----------------------------------------------
	  self.sizer_line4.Add(self.lbl_org_state,4,wxEXPAND|wxALIGN_CENTER)
	  self.sizer_line4.Add(self.txt_org_state,20,wxEXPAND)
	  self.sizer_line4.Add(self.lbl_org_zip,10,wxGROW|wxTOP,5)
	  self.sizer_line4.Add(self.txt_org_zip,10,wxEXPAND)
	  self.sizer_line4.Add(0,0,4)
	  self.sizer_line4.Add(self.lbl_org_internet,8,wxGROW|wxALIGN_CENTER_VERTICAL,5)
	  self.sizer_line4.Add(self.txt_org_internet,36,wxEXPAND)
          #-----------------------------------------------
	  #line five: postal address checkbox, internet
	  #-----------------------------------------------
	  self.sizer_line5.Add(0,0,4)
	  self.sizer_line5.Add(self.chbx_postaladdress,40,wxEXPAND)
	  self.sizer_line5.Add(0,0,4)
	  self.sizer_line5.Add(self.lbl_org_mobile,8,wxGROW|wxALIGN_CENTER_VERTICAL,5)
	  self.sizer_line5.Add(self.txt_org_mobile,36,wxEXPAND)
          #-----------------------------------------------
	  #line six: checkbox branch mobile phone number
	  #-----------------------------------------------
	  self.sizer_line6.Add(0,20,96)
	  #-----------------------------------------------
	  #line seven: user1
	  #-----------------------------------------------
	  self.sizer_line7_user1 = wxBoxSizer(wxHORIZONTAL)
	  self.sizer_line7_user1.Add(self.lbl_org_user1,4,wxGROW|wxALIGN_CENTER_VERTICAL,5)
	  self.sizer_line7_user1.Add(self.txt_org_user1,18,wxEXPAND)
	  self.sizer_line7_user2 = wxBoxSizer(wxHORIZONTAL)
	  self.sizer_line7_user2.Add(self.lbl_org_user2,4,wxGROW|wxALIGN_CENTER_VERTICAL,5)
          self.sizer_line7_user2.Add(self.txt_org_user2,18,wxEXPAND)
	  self.sizer_line7_user3 = wxBoxSizer(wxHORIZONTAL)
          self.sizer_line7_user3.Add(self.lbl_org_user3,4,wxGROW|wxALIGN_CENTER_VERTICAL,5)
          self.sizer_line7_user3.Add(self.txt_org_user3,18,wxEXPAND)
	  self.sizer_line7_right = wxBoxSizer(wxVERTICAL)
	  self.sizer_line7_right.AddSizer(self.sizer_line7_user1,0,wxEXPAND) 
	  self.sizer_line7_right.AddSizer(self.sizer_line7_user2,0,wxEXPAND) 
	  self.sizer_line7_right.AddSizer(self.sizer_line7_user3,0,wxEXPAND) 
          
	  
	  self.sizer_line7.Add(self.lbl_org_memo,4,wxEXPAND|wxALIGN_CENTER_VERTICAL,5)
	  self.sizer_line7.Add(self.txt_org_memo,40,wxEXPAND)
	  self.sizer_line7.Add(0,0,4)
	  self.sizer_line7.AddSizer(self.sizer_line7_right,44,wxEXPAND)
	  self.nextsizer=  wxBoxSizer(wxVERTICAL)
	  self.nextsizer.Add(self.list_organisations,3,wxEXPAND)
	  self.nextsizer.Add(0,10,0)
	  self.nextsizer.Add(self.sizer_line0,0,wxEXPAND)
	  self.nextsizer.Add(self.sizer_line1,0,wxEXPAND)
	  self.nextsizer.Add(self.sizer_line1a,0,wxEXPAND)
	  self.nextsizer.Add(self.sizer_line2,0,wxEXPAND)
	  self.nextsizer.Add(self.sizer_line3,0,wxEXPAND)
	  self.nextsizer.Add(self.sizer_line4,0,wxEXPAND)
	  self.nextsizer.Add(self.sizer_line5,0,wxEXPAND)
	  self.nextsizer.Add(self.sizer_line6,0,wxEXPAND)
	  self.nextsizer.Add(self.sizer_line7,0,wxEXPAND)

	  self.mainsizer = wxBoxSizer(wxVERTICAL)
	  self.mainsizer.AddSizer(self.nextsizer,1,wxEXPAND|wxALL,10)
	  self.SetSizer(self.mainsizer)
          self.mainsizer.Fit
          self.SetAutoLayout(true)
          self.Show(true)
      
class gmContacts (gmPlugin.wxNotebookPlugin):
	def name (self):
		return "Contacts"

	def GetWidget (self, parent):
		return ContactsPanel (parent, -1)

	def MenuInfo (self):
		return ('view', '&Contacts')

	def DoToolbar (self, tb, widget):
	      tool1 = tb.AddTool(ID_SEARCHGLOBAL, images_contacts_toolbar16_16.getfind_globalBitmap(),
				shortHelpString="Global Search Of Contacts Database", isToggle=false)
	      tb.AddControl(wxTextCtrl(tb, ID_SEARCHGLOBAL, name ="txtGlobalSearch",size =(100,-1),style = 0, value = ''))
	      tool1 = tb.AddTool(ID_ORGANISATIONDISPLAY, images_contacts_toolbar16_16.getorganisationBitmap(),
				shortHelpString="Display Organisations", isToggle=true)
	      tool1 = tb.AddTool(ID_GENERALPRACTICESDISPLAY, images_contacts_toolbar16_16.getgeneralpracticesBitmap(),
				shortHelpString="Display General Practices", isToggle=true)
	      tool1 = tb.AddTool(ID_DOCTORSDISPLAY, images_contacts_toolbar16_16.getdoctorBitmap(),
				shortHelpString="Display Doctors", isToggle=true)
	      tool1 = tb.AddTool(ID_PERSONSDISPLAY, images_contacts_toolbar16_16.getpersonBitmap(),
				shortHelpString="Display Persons", isToggle=false)
	      #tb.AddControl(wxStaticBitmap(tb, -1, images_contacts_toolbar16_16.getvertical_separator_thinBitmap(), wxDefaultPosition, wxDefaultSize))
	      tool1 = tb.AddTool(ID_ORGANISATIONADD, images_contacts_toolbar16_16.getorganisation_addBitmap(),
				shortHelpString="Add an Organisation", isToggle=true)
	      tool1 = tb.AddTool(ID_BRANCHDEPTADD, images_contacts_toolbar16_16.getbranch_addBitmap(),
				shortHelpString="Add Branch or Department", isToggle=true)
	      tool1 = tb.AddTool(ID_EMPLOYEEADD, images_contacts_toolbar16_16.getemployeesBitmap(),
				shortHelpString="Add an Employee", isToggle=true)
	      tool1 = tb.AddTool(ID_PERSONADD, images_contacts_toolbar16_16.getperson_addBitmap(),
				shortHelpString="Add Person", isToggle=true)
              tb.AddControl(wxStaticBitmap(tb, -1, images_contacts_toolbar16_16.getvertical_separator_thinBitmap(), wxDefaultPosition, wxDefaultSize))
              tool1 = tb.AddTool(ID_RELOAD, images_contacts_toolbar16_16.getreloadBitmap(),
				shortHelpString="Refresh Display", isToggle=true)
              tb.AddControl(wxStaticBitmap(tb, -1, images_contacts_toolbar16_16.getvertical_separator_thinBitmap(), wxDefaultPosition, wxDefaultSize))
              tool1 = tb.AddTool(ID_SEARCHSPECIFIC, images_contacts_toolbar16_16.getfind_specificBitmap(),
				shortHelpString="Find Specific Records in Contacts Database", isToggle=true)
              tool1 = tb.AddTool(ID_SORTA_Z, images_contacts_toolbar16_16.getsort_A_ZBitmap(),
				shortHelpString="Sort A to Z", isToggle=true)
              tool1 = tb.AddTool(ID_SORTZ_A, images_contacts_toolbar16_16.getsort_Z_ABitmap(),
				shortHelpString="Sort Z to A", isToggle=true)
	      tool1 = tb.AddTool(ID_SENDEMAIL, images_contacts_toolbar16_16.getsendemailBitmap(),
				shortHelpString="Send Email", isToggle=true)
	      tool1 = tb.AddTool(ID_LINKINTERNET, images_contacts_toolbar16_16.getearthBitmap(),
				shortHelpString="Load Web Address", isToggle=true)
	      tool1 = tb.AddTool(ID_INSTANTREPORT, images_contacts_toolbar16_16.getlighteningBitmap(),
				shortHelpString="Instant Report from Grid", isToggle=true)
	      tool1 = tb.AddTool(ID_REPORTS, images_contacts_toolbar16_16.getreportsBitmap(),
				shortHelpString="Pre-formatted reports", isToggle=true)
	      tb.AddControl(wxStaticBitmap(tb, -1, images_contacts_toolbar16_16.getvertical_separator_thinBitmap(), wxDefaultPosition, wxDefaultSize))
	      tool1 = tb.AddTool(ID_SAVE, images_contacts_toolbar16_16.getsaveBitmap(),
				shortHelpString="Save Record", isToggle=true)		
          

if __name__ == "__main__":
	app = wxPyWidgetTester(size = (800, 600))
	app.SetWidget(ContactsPanel, -1)
	app.MainLoop()
