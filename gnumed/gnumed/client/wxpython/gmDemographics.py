"""gmDemographics

 This panel will hold all the patients details

 @copyright: authors
 @dependencies: wxPython (>= version 2.3.1)
	28.07.2004 rterry gui-rewrite to include upper patient window
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/Attic/gmDemographics.py,v $
# $Id: gmDemographics.py,v 1.37 2004-08-18 08:15:21 ncq Exp $
__version__ = "$Revision: 1.37 $"
__author__ = "R.Terry, SJ Tan"
__license__ = 'GPL (details at http://www.gnu.org)'

# standard library
import cPickle, zlib, shutil, time
from string import *			# FIXME

# 3rd party
from mx import DateTime
from wxPython.wx import *		# FIXME
from wxPython.lib.mixins.listctrl import wxColumnSorterMixin, wxListCtrlAutoWidthMixin

# GnuMed specific
from Gnumed.wxpython import gmPlugin, gmGP_PatientPicture, gmPatientHolder, images_patient_demographics, images_contacts_toolbar16_16, gmPhraseWheel
from Gnumed.pycommon import  gmGuiBroker, gmLog, gmDispatcher, gmSignals, gmCharacterValidator, gmCfg, gmWhoAmI, gmI18N
from Gnumed.business import gmDemographicRecord, gmPatient

# constant defs
_log = gmLog.gmDefLog
_whoami = gmWhoAmI.cWhoAmI()

gmSECTION_PATIENT = 5

ID_PATIENT = wxNewId()
ID_PATIENTSLIST = wxNewId()
ID_ALL_MENU  = wxNewId()
ID_ADDRESSLIST = wxNewId()
ID_NAMESLIST = wxNewId()
ID_CURRENTADDRESS = wxNewId()
ID_COMBOTITLE = wxNewId()
ID_COMBOSEX = wxNewId()
ID_COMBOMARITALSTATUS = wxNewId()
ID_COMBONOKRELATIONSHIP = wxNewId()
ID_TXTSURNAME = wxNewId()
ID_TXTFIRSTNAME = wxNewId()
ID_TXTSALUTATION = wxNewId()
ID_TXTSTREET = wxNewId()
ID_TXTSUBURB = wxNewId()
ID_TXTSTATE = wxNewId()
ID_TXTPOSTCODE = wxNewId()
ID_TXTBIRTHDATE = wxNewId()
ID_TXTCOUNTRYOFBIRTH = wxNewId()
ID_TXTOCCUPATION = wxNewId()
ID_TXTNOKADDRESS = wxNewId()
ID_TXTHOMEPHONE = wxNewId()
ID_TXTWORKPHONE = wxNewId()
ID_TXTFAX = wxNewId()
ID_TXTEMAIL = wxNewId()
ID_TXTINTERNET = wxNewId()
ID_TXTMOBILE = wxNewId()
ID_TXTMEMO = wxNewId()
ID_LISTADDRESSES = wxNewId()
ID_BUTTONBROWSENOK = wxNewId()
ID_BUTTONAQUIRE = wxNewId()
ID_BUTTONPHOTOEXPORT = wxNewId()
ID_BUTTONPHOTOIMPORT = wxNewId()
ID_BUTTONPHOTODELETE = wxNewId()
ID_CHKBOXRESIDENCE = wxNewId()
ID_CHKBOXPOSTAL = wxNewId()
ID_CHKBOXPREFERREDALIAS = wxNewId()
ID_BUTTONFINDPATIENT = wxNewId()
ID_TXTPATIENTFIND = wxNewId()
ID_TXTPATIENTAGE = wxNewId()
ID_TXTPATIENTALLERGIES  = wxNewId()
ID_TXTNOK =wxNewId()

ID_PUP_ITEM_SaveDisplayLayout = wxNewId()

PatientData = {
1 : ("Macks", "Jennifer","Flat9/128 Brook Rd","NEW LAMBTON HEIGHTS", "2302","19/01/2003","M"," 02 49 5678890"),
2 : ("Smith","Michelle", "Flat9/128 Brook Rd","ELERMORE VALE", "2302","23/02/1973","F", "02 49564320"),
3 : ("Smitt", "Francis","29 Willandra Crescent", "WINDALE"," 2280","18/08/1952","M","02 7819292"),
4 : ("Smythe-Briggs", "Elizabeth","129 Flat Rd", "SMITHS LAKE","2425","04/12/1918","F","02 4322222"),
}

#-----------------------------------------------------------
#text control class to be later replaced by the gmPhraseWheel
#------------------------------------------------------------
class TextBox_RedBold(wxTextCtrl):
	def __init__ (self, parent, id): #, wxDefaultPostion, wxDefaultSize):
		wxTextCtrl.__init__(self,parent,id,"",wxDefaultPosition, wxDefaultSize,wxSIMPLE_BORDER)
		self.SetForegroundColour(wxColor(255,0,0))
		self.SetFont(wxFont(12,wxSWISS,wxNORMAL, wxBOLD,False,''))
class BlueLabel_Normal(wxStaticText):
	def __init__(self, parent, id, prompt, text_alignment):
		wxStaticText.__init__(self,parent, id,prompt,wxDefaultPosition,wxDefaultSize,text_alignment)
		self.SetFont(wxFont(12,wxSWISS,wxNORMAL,wxNORMAL,False,''))
		self.SetForegroundColour(wxColour(0,0,131))
class BlueLabel_Bold(wxStaticText):
	def __init__(self, parent, id, prompt, text_alignment):
		wxStaticText.__init__(self,parent, id,prompt,wxDefaultPosition,wxDefaultSize,text_alignment)
		self.SetFont(wxFont(12,wxSWISS,wxNORMAL,wxBOLD,False,''))
		#self.SetForegroundColour(wxColour(0,0,131))
		self.SetForegroundColour (wxColour(0,0,255))
class TextBox_BlackNormal(wxTextCtrl):
	def __init__ (self, parent, id): #, wxDefaultPosition, wxDefaultSize):
		wxTextCtrl.__init__(self,parent,id,"",wxDefaultPosition, wxDefaultSize,wxSIMPLE_BORDER)
		self.SetForegroundColour(wxColor(0,0,0))
		#self.SetFont(wxFont(12,wxSWISS,wxNORMAL, wxBOLD,False,''))
		self.SetFont(wxFont(12,wxSWISS,wxNORMAL,wxNORMAL,False,''))

class ExtIDPanel:
	def __init__ (self, parent, sizer, context = 'p'):


		self.demo = None



	def setDemo (self, demo):
		"""
		Recieves a gmDemographicRecord-like object to populate the list control
		"""
		self.demo = demo
		self.Clear ()
		x = 0
		for r in demo.listExternalIDs ():
			o = self.map[r['origin']]
			e = r['external_id']
			c = r['comment']
			i = r['id']
			if c:
				self.list.Append ("%s - %s (%s)" % (o, e, c), i)
			else:
				self.list.Append ("%s - %s" % (o, e), i)

	def on_add (self, event):
		try:
			id_type = self.combo_type.GetClientData (self.combo_type.GetSelection ())
			if self.demo:
				d = self.demo.addExternalID (self.txt_ext_id.GetValue (), id_type, self.txt_comment.GetValue ())
				comment = self.txt_comment.GetValue ()
				if comment:
					self.list.Append ("%s - %s (%s)" % (self.map[id_type], self.txt_ext_id.GetValue (), comment), d)
				else:
					self.list.Append ("%s - %s" % (self.map[id_type], self.txt_ext_id.GetValue ()), d)
							 
				#print "adding list item %d, data %d" % (x, d)
				self.txt_ext_id.SetValue ('')
				self.txt_comment.SetValue ('')
				self.combo_type.SetSelection (0)
		except:
			_log.LogException ('failed to add ext. ID', sys.exc_info (), verbose= 0)

	def on_del (self, event):
		try:
			sel = self.list.GetSelection ()
			print sel
			if sel >=0:
				x = self.list.GetClientData (sel)
				self.demo.removeExternalID (x)
				self.list.Delete (sel)
		except:
			_log.LogException ('failed to delete ext. ID', sys.exc_info (), verbose= 0)
		
#-----------------------------------------------------------------------------------------------------------------------------------------------------------
# This visually consists of:
#
#	Upper listbox - self.patientslist containing one or more patient names and addresses
#	To the right of this panel containing patients photo, with aquire/delete/import/export buttons
#		- These two elements sit on a wxBoxSizer(wxHORIZONTAL) self.sizer_for_patientlist_and_photo
#	Underneath this all the textboxes for data entry
#		- These are loaded into a gridsizer self.gs
#	Both these sizers sit on self.sizer_main.
#		- self.sizer_for_patientlist_and_photo expands vertically and horizontally
#		- self.gs expands horizontally but not vertically
#-----------------------------------------------------------------------------------------------------------------------------------------------------------
class PatientsPanel(wxPanel, gmPatientHolder.PatientHolder):
	def __init__(self, parent, id= -1):
		wxPanel.__init__(self, parent, id ,wxDefaultPosition,wxDefaultSize,wxRAISED_BORDER|wxTAB_TRAVERSAL)
		gmPatientHolder.PatientHolder.__init__(self)
		self.gb = gmGuiBroker.GuiBroker ()
		try:
			self.mwm = self.gb['clinical.manager']
		except:
			self.mwm = {}
		self.to_delete = []
		self.addr_cache = []
		self.gendermap = {'m':_('Male'), 'f':_("Female"), '?':_("Unknown"), 'tm':_('Trans. Male'), 'tf':_('Trans. Female'), 									'h':_('Hermaphrodite')}
		self.comm_channel_names = gmDemographicRecord.getCommChannelTypes ()
		self.marital_status_types = gmDemographicRecord.getMaritalStatusTypes ()
		self._cfg = gmCfg.gmDefCfgFile
		#self.db = gmCfg.setDBParam()
		self._whoami = gmWhoAmI.cWhoAmI()
		#create the sizer to hold patient list and photo
		self.sizer_for_patientlist_and_photo = wxBoxSizer(wxHORIZONTAL)
		#------------------------------------------------------------------------
		#create patient list, add column headers and data
		#-----------------------------------------------------------------------
		patientlist_ID = wxNewId()
		self.patientlist = wxListCtrl(self,patientlist_ID,wxDefaultPosition,size=(400,10),style=wxLC_REPORT | wxSUNKEN_BORDER   | 					wxLC_VRULES|wxLC_HRULES)
		self.patientlist.InsertColumn(0, "Name")
		self.patientlist.InsertColumn(1, "")
		self.patientlist.InsertColumn(2, "Street")
		self.patientlist.InsertColumn(4, "Suburb")
		self.patientlist.InsertColumn(5, "Postcode",wxLIST_FORMAT_CENTRE)
		self.patientlist.InsertColumn(6, "Date of Birth", wxLIST_FORMAT_CENTRE)
		self.patientlist.InsertColumn(7, "Sex", wxLIST_FORMAT_CENTRE)
		self.patientlist.InsertColumn(8, "Home Phone", wxLIST_FORMAT_CENTRE)
		#-------------------------------------------------------------
		#loop through the PatientData array and add to the list control
		#note the different syntax for the first coloum of each row
		#i.e. here > self.patientlist.InsertStringItem(x, data[0])!!
		#-------------------------------------------------------------
		items = PatientData.items()
		for x in range(len(items)):
			key, data = items[x]
			print x, data[0],data[1],data[2],data[3],data[4],data[5]
			self.patientlist.InsertStringItem(x, data[0])
			self.patientlist.SetStringItem(x, 1, data[1])
			self.patientlist.SetStringItem(x, 2, data[2])
			self.patientlist.SetStringItem(x, 3, data[3])
			self.patientlist.SetStringItem(x, 4, data[4])
			self.patientlist.SetStringItem(x, 5, data[5])
			self.patientlist.SetStringItem(x, 6, data[6])
			self.patientlist.SetStringItem(x, 7, data[7])
			self.patientlist.SetItemData(x, key)
		#--------------------------------------------------------
		#note the number passed to the wxColumnSorterMixin must be
		#the 1 based count of columns
		#--------------------------------------------------------
		self.itemDataMap = PatientData
		# Try and get the user's column width from the databse
		pat_cols_list = gmCfg.getFirstMatchingDBSet(option="widgets.demographics.patientlist.column_sizes")

		if not pat_cols_list or len(pat_cols_list[0]) == 0:		# no values - use defaults
			self.patientlist.SetColumnWidth(0, 100)
			self.patientlist.SetColumnWidth(1, 100)
			self.patientlist.SetColumnWidth(2, 250)
			self.patientlist.SetColumnWidth(3, 200)
			self.patientlist.SetColumnWidth(4, 60)
			self.patientlist.SetColumnWidth(5, 100)
			self.patientlist.SetColumnWidth(6, 50)
			self.patientlist.SetColumnWidth(7,100)
			# FIXME: save defaults ?
		else:											# otherwise, set column widths
			print pat_cols_list
			for i in range (0,8):
				self.patientlist.SetColumnWidth(i,int(pat_cols_list[i]))
		#----------------------------------------------------------------------------------------------------------------
		#Now create the sizer to hold the patients photo and buttons. The photo will
		#not resize as the form resizes
		#---------------------------------------------------------------------------------------------------------------
		self.sizer_photo = wxBoxSizer(wxVERTICAL)
		self.lbl_photo = BlueLabel_Bold(self,-1,"Photo",wxALIGN_CENTRE)
		self.photopanel = wxPanel (self,-1,size= (100,100), style = wxSUNKEN_BORDER)
		self.sizer_photo.Add(self.lbl_photo,0,wxSHAPED|wxALIGN_CENTRE|wxALL,2)
		self.sizer_photo.Add(self.photopanel,0,wxSHAPED|wxALIGN_CENTRE|wxALL,2)
		self.sizer_photo.Add(0,5,0)
		self.sizer_photo.Add(0,0,1,wxEXPAND)
		self.sizer_for_patientlist_and_photo.Add(self.patientlist,
					5,						#any non-zero value = make vertically stretchable
					wxEXPAND				#make grow as sizer grows (vertical + horizontal)
					|wxTOP|wxLEFT|wxBOTTOM,	#the top, left, bottom edges
					2)						#by a 10 pixel border
		self.sizer_for_patientlist_and_photo.Add(self.sizer_photo,1,wxEXPAND|wxALL,5)

		self.lbl_space = BlueLabel_Normal(self,-1,"",wxLEFT) #This lbl_space is used as a spacer between label
		#-------------------------------------------------------------------
		#Add surname, firstname, title, sex, salutation
		#-------------------------------------------------------------------
		self.lbl_surname = BlueLabel_Normal(self,-1,"Surname",wxLEFT)
		self.txt_surname = TextBox_RedBold(self,-1)
		self.lbl_title = BlueLabel_Normal(self,-1,"Title",wxALIGN_CENTRE)
		self.titlelist = ['Mr', 'Mrs', 'Miss', 'Mst', 'Ms', 'Dr', 'Prof']
		self.combo_title = wxComboBox(self, 500, "", wxDefaultPosition,wxDefaultSize,self.titlelist, wxCB_DROPDOWN)
		self.lbl_firstname = BlueLabel_Normal(self,-1,"Firstname",wxLEFT)
		self.txt_firstname = TextBox_RedBold(self,-1)
		self.lbl_sex = BlueLabel_Normal(self,-1,"Sex",wxALIGN_CENTRE)
		self.combo_sex = wxComboBox(self, 500, "", wxDefaultPosition,wxDefaultSize, self.gendermap.values (), 	    									wxCB_DROPDOWN)
		self.lbl_preferredname =  BlueLabel_Normal(self,-1,"Salutation",wxLEFT)
		self.txt_preferredname = TextBox_RedBold(self,-1)
		#-----------------------------------------------------------------------------------
		#now add gui-elements to sizers for surname to salutation
		#each line has several (up to 4 elements
		# e.g surname <textbox> title <textbox> etc
		#-----------------------------------------------------------------------------------
		self.sizer_line1 = wxBoxSizer(wxHORIZONTAL)  		 #holds surname label + textbox, title label and combobox
		self.sizer_line1.Add(self.lbl_surname,3,wxEXPAND|wxTOP|wxBOTTOM,1)
		self.sizer_line1.Add(self.txt_surname,5,wxEXPAND|wxTOP|wxBOTTOM,1)
		self.sizer_line1.Add(self.lbl_title,3,wxEXPAND|wxTOP|wxBOTTOM,1)
		self.sizer_line1.Add(self.combo_title,5,wxEXPAND|wxTOP|wxBOTTOM,1)
		self.sizer_line2 = wxBoxSizer(wxHORIZONTAL)  		#holds firstname label + textbox, sex label + combobox
		self.sizer_line2.Add(self.lbl_firstname,3,wxEXPAND|wxTOP|wxBOTTOM,1)
		self.sizer_line2.Add(self.txt_firstname,5,wxEXPAND|wxTOP|wxBOTTOM,1)
		self.sizer_line2.Add(self.lbl_sex,3,wxEXPAND|wxTOP|wxBOTTOM,1)
		self.sizer_line2.Add(self.combo_sex,5,wxEXPAND|wxTOP|wxBOTTOM,1)
		self.sizer_line3 = wxBoxSizer(wxHORIZONTAL)		#holds preferredname label and textbox
		self.sizer_line3.Add(self.lbl_preferredname,3,wxEXPAND|wxTOP|wxBOTTOM,1)
		self.sizer_line3.Add(self.txt_preferredname,5,wxEXPAND|wxTOP|wxBOTTOM,1)
		self.sizer_line3.Add(self.lbl_space,8,wxEXPAND|wxTOP|wxBOTTOM,1)
		#--------------------------------------------------------------------------
		#The heading for 'Address, sits on its own box sizer
		#--------------------------------------------------------------------------
		self.lbl_heading_address = BlueLabel_Bold(self,-1,"Address",wxALIGN_CENTRE)
		self.sizer_lbl_heading_address = wxBoxSizer(wxHORIZONTAL)   #holds address heading
		self.sizer_lbl_heading_address.Add(self.lbl_space,1,wxEXPAND|wxTOP|wxBOTTOM,1)
		self.sizer_lbl_heading_address.Add(self.lbl_space,1,wxEXPAND|wxTOP|wxBOTTOM,1)
		self.sizer_lbl_heading_address.Add(self.lbl_heading_address,1,wxEXPAND|wxTOP|wxBOTTOM,1)
		self.sizer_lbl_heading_address.Add(self.lbl_space,1,wxEXPAND|wxTOP|wxBOTTOM,1)
		#------------------------------------------------------------------------------
		#Next add street label + 3 line size textbox for street
		#------------------------------------------------------------------------------
		self.sizer_street = wxBoxSizer(wxHORIZONTAL)
		self.lbl_street = BlueLabel_Normal(self,-1,"Street",wxLEFT)
		self.txt_street = wxTextCtrl(self, 30, "",wxDefaultPosition, size=(1,50),style=wxTE_MULTILINE)
		self.sizer_street.Add(self.lbl_street,3,wxEXPAND)
		self.sizer_street.Add(self.txt_street,13, wxEXPAND)
		#------------------------------------------------
		#suburb on one line
		#------------------------------------------------
		self.sizer_suburb = wxBoxSizer(wxHORIZONTAL)
		self.lbl_suburb = BlueLabel_Normal(self,-1,"Suburb",wxLEFT)
		self.txt_suburb = gmPhraseWheel.cPhraseWheel( parent = self,id = -1 , aMatchProvider= gmDemographicRecord.MP_urb_by_zip(), selection_only = 1, pos = 								wxDefaultPosition, size=wxDefaultSize , id_callback= self.__urb_selected)
		self.sizer_suburb.Add(self.lbl_suburb,3,wxEXPAND|wxTOP|wxBOTTOM,1)
		self.sizer_suburb.Add(self.txt_suburb,13,wxEXPAND|wxTOP|wxBOTTOM,1)
		self.sizer_stateandpostcode = wxBoxSizer(wxHORIZONTAL)
		#-----------------------------------------------------------
		#state and postcode on next line on sizer
		#-----------------------------------------------------------
		self.lbl_state = BlueLabel_Normal(self,-1,"State",wxLEFT)
		self.txt_state = TextBox_BlackNormal(self,-1)
		self.lbl_postcode = BlueLabel_Normal(self,-1,"Postcode",wxALIGN_CENTRE)
  		self.txt_postcode  = gmPhraseWheel.cPhraseWheel( parent = self,id = -1 , aMatchProvider= gmDemographicRecord.PostcodeMP(), selection_only = 1,  pos = 							wxDefaultPosition, size=wxDefaultSize)
		self.txt_postcode.setDependent (self.txt_suburb, 'postcode')
		self.sizer_stateandpostcode.Add(self.lbl_state,3,wxEXPAND|wxTOP|wxBOTTOM,1)
		self.sizer_stateandpostcode.Add(self.txt_state,5,wxEXPAND|wxTOP|wxBOTTOM,1)
		self.sizer_stateandpostcode.Add(self.lbl_postcode,3,wxEXPAND|wxTOP|wxBOTTOM,1)
		self.sizer_stateandpostcode.Add(self.txt_postcode,5,wxEXPAND|wxTOP|wxBOTTOM,1)
		#Next line = Type of address (e.g home, work, parents - any one of which could be a 'postal address'
		self.sizer_addresstype_chkpostal = wxBoxSizer(wxHORIZONTAL)
		self.lbl_addresstype = BlueLabel_Normal(self,-1,"Type",wxLEFT)
		self.combo_address_types = ['Home', 'Work', 'Parents','Post Office Box']
		self.combo_address_type = wxComboBox(self, -1, "",wxDefaultPosition,wxDefaultSize, self.combo_address_types,	 	     					wxCB_DROPDOWN |wxCB_READONLY)
		self.chk_addresspostal = wxCheckBox(self, -1, "Postal Address ", wxDefaultPosition,wxDefaultSize, wxNO_BORDER)
		self.chk_addresspostal.SetForegroundColour(wxColour(0,0,131))
		self.sizer_addresstype_chkpostal.Add(self.lbl_addresstype,3,wxEXPAND|wxTOP|wxBOTTOM,1)
		self.sizer_addresstype_chkpostal.Add(self.combo_address_type,5,wxEXPAND|wxTOP|wxBOTTOM,1)
		self.sizer_addresstype_chkpostal.Add(self.lbl_space,3,wxEXPAND|wxTOP|wxBOTTOM,1)
		self.sizer_addresstype_chkpostal.Add(self.chk_addresspostal,5,wxEXPAND|wxBOTTOM,1)
		#----------------------------------------------------------------------------------------------------------------------
		#Contact details - phone work, home,fax,mobile,internet and email
		#-----------------------------------------------------------------------------------------------------------------------
		self.sizer_contacts_line1 = wxBoxSizer(wxHORIZONTAL)
		self.sizer_contacts_line2 = wxBoxSizer(wxHORIZONTAL)
		self.sizer_contacts_line3 = wxBoxSizer(wxHORIZONTAL)
		self.sizer_contacts_line4 = wxBoxSizer(wxHORIZONTAL)
		self.lbl_contact_heading = BlueLabel_Bold(self,-1,"Contact Details",wxLEFT)
		self.lbl_homephone = BlueLabel_Normal(self,-1,"Home Phone",wxLEFT)
		self.lbl_workphone = BlueLabel_Normal(self,-1,"Work Phone",wxLEFT)
		self.lbl_mobile = BlueLabel_Normal(self,-1,"Mobile",wxLEFT)
		self.lbl_fax = BlueLabel_Normal(self,-1,"Fax",wxALIGN_CENTRE)
		self.lbl_email = BlueLabel_Normal(self,-1,"Email",wxALIGN_CENTRE)
		self.lbl_web = BlueLabel_Normal(self,-1,"Web",wxALIGN_CENTRE)
		self.txt_homephone = TextBox_BlackNormal(self,-1)
		self.txt_workphone = TextBox_BlackNormal(self,-1)
		self.txt_mobile = TextBox_BlackNormal(self,-1)
		self.txt_fax = TextBox_BlackNormal(self,-1)
		self.txt_email = TextBox_BlackNormal(self,-1)
		self.txt_web = TextBox_BlackNormal(self,-1)
		self.sizer_contacts_line1 .Add(self.lbl_space,1,wxEXPAND|wxTOP|wxBOTTOM,1)
		self.sizer_contacts_line1 .Add(self.lbl_space,1,wxEXPAND)
		self.sizer_contacts_line1 .Add(self.lbl_contact_heading,1,wxEXPAND|wxTOP|wxBOTTOM,1)
		self.sizer_contacts_line1 .Add(self.lbl_space,1,wxEXPAND|wxTOP|wxBOTTOM,1)
		self.sizer_contacts_line2 .Add(self.lbl_homephone,3,wxEXPAND|wxTOP|wxBOTTOM,1)
		self.sizer_contacts_line2 .Add(self.txt_homephone,5,wxEXPAND|wxTOP|wxBOTTOM,1)
		self.sizer_contacts_line2 .Add(self.lbl_fax,3,wxEXPAND|wxTOP|wxBOTTOM,1)
		self.sizer_contacts_line2 .Add(self.txt_fax,5,wxEXPAND|wxTOP|wxBOTTOM,1)
		self.sizer_contacts_line3 .Add(self.lbl_workphone,3,wxEXPAND|wxTOP|wxBOTTOM,1)
		self.sizer_contacts_line3 .Add(self.txt_workphone,5,wxEXPAND|wxTOP|wxBOTTOM,1)
		self.sizer_contacts_line3 .Add(self.lbl_email,3,wxEXPAND|wxTOP|wxBOTTOM,1)
		self.sizer_contacts_line3 .Add(self.txt_email,5,wxEXPAND|wxTOP|wxBOTTOM,1)
		self.sizer_contacts_line4 .Add(self.lbl_mobile,3,wxEXPAND|wxTOP|wxBOTTOM,1)
		self.sizer_contacts_line4 .Add(self.txt_mobile,5,wxEXPAND|wxTOP|wxBOTTOM,1)
		self.sizer_contacts_line4 .Add(self.lbl_web,3,wxEXPAND|wxTOP|wxBOTTOM,1)
		self.sizer_contacts_line4 .Add(self.txt_web,5,wxEXPAND|wxTOP|wxBOTTOM,1)
		self.sizer_contacts =wxBoxSizer(wxVERTICAL)
		#------------------------------------------------------
		#Design the right hand side of screen
		#Date of Birth, Marital Status
		#-----------------------------------------------------
		self.sizer_birthdatemarital = wxBoxSizer(wxHORIZONTAL)
		self.lbl_birthdate = BlueLabel_Normal(self,-1,"Birthdate",wxLEFT)
		self.txt_birthdate = TextBox_BlackNormal(self,-1)
		self.lbl_maritalstatus = BlueLabel_Normal(self,-1,"Marital Status",wxALIGN_CENTRE)
		self.marital_status_types = ['Married', 'Single', 'Defacto']
		self.combo_maritalstatus = wxComboBox(self, 500, "", wxDefaultPosition,wxDefaultSize,
						      self.marital_status_types, wxCB_DROPDOWN | wxCB_READONLY)
		self.sizer_birthdatemarital.Add(self.lbl_birthdate,3,wxEXPAND|wxTOP|wxBOTTOM,1)
		self.sizer_birthdatemarital.Add(self.txt_birthdate,5,wxEXPAND|wxTOP|wxBOTTOM,1)
		self.sizer_birthdatemarital.Add(self.lbl_maritalstatus,3,wxEXPAND|wxTOP|wxBOTTOM,1)
		self.sizer_birthdatemarital.Add(self.combo_maritalstatus,5,wxEXPAND|wxTOP|wxBOTTOM,1)
		#-----------------------------
		#Patients occupation
		#-----------------------------
		self.sizer_occupation = wxBoxSizer(wxHORIZONTAL)
		self.lbl_occupation = BlueLabel_Normal(self,-1,"Occupation",wxLEFT)
		self.txt_occupation = gmPhraseWheel.cPhraseWheel(
			parent=self,
			id = -1,
			aMatchProvider = gmDemographicRecord.OccupationMP(),
			pos = wxDefaultPosition,
			size=wxDefaultSize
		)
		self.sizer_occupation.Add(self.lbl_occupation,3,wxEXPAND|wxTOP|wxBOTTOM,1)
		self.sizer_occupation.Add(self.txt_occupation,13,wxEXPAND|wxTOP|wxBOTTOM,1)
		#-----------------------------------
		#patients country of birth
		#-----------------------------------
		self.sizer_countryofbirth = wxBoxSizer(wxHORIZONTAL)
		self.lbl_countryofbirth = BlueLabel_Normal(self,-1,"Born In",wxLEFT)
		self.txt_countryofbirth = gmPhraseWheel.cPhraseWheel (parent=self, id = -1, aMatchProvider = gmDemographicRecord.CountryMP (), pos = wxDefaultPosition, 						size=wxDefaultSize)
		self.sizer_countryofbirth.Add(self.lbl_countryofbirth,3,wxEXPAND|wxTOP|wxBOTTOM,1)
		self.sizer_countryofbirth.Add(self.txt_countryofbirth,13,wxEXPAND|wxTOP|wxBOTTOM,1)
		#-----------------------------------------------------------
		#Now add heading for next of kin section
		#-----------------------------------------------------------
		self.lbl_heading_nok = BlueLabel_Bold(self,-1,"Next of Kin",wxALIGN_CENTRE)
		self.sizer_heading_nok = wxBoxSizer(wxHORIZONTAL)   #holds address heading
		self.sizer_heading_nok.Add(self.lbl_space,1,wxEXPAND)
		self.sizer_heading_nok.Add(self.lbl_space,1,wxEXPAND)
		self.sizer_heading_nok.Add(self.lbl_heading_nok,1,wxEXPAND|wxTOP|wxBOTTOM,1)
		self.sizer_heading_nok.Add(self.lbl_space,1,wxEXPAND)
		#--------------------------------------------------------------------------------------------------------
		#Next of Kin Information in multi-line textbox(will include name/address)
		#--------------------------------------------------------------------------------------------------------
		self.sizer_patientnameaddressNOK= wxBoxSizer(wxHORIZONTAL)
		self.lbl_nextofkin = BlueLabel_Normal(self,-1,"Details",wxLEFT)
		self.txt_nameaddressnok = wxTextCtrl(self, ID_TXTNOK, ""
				,wxDefaultPosition
				, size=(1,50)				 # note 1=arbitary,  50 needed to allow it to expand, otherwise is small
				,style = wxTE_MULTILINE)
		self.sizer_patientnameaddressNOK.Add(self.lbl_nextofkin,3,wxEXPAND)
		self.sizer_patientnameaddressNOK.Add(self.txt_nameaddressnok,13,wxEXPAND)
		#----------------------------------------------------------------------------------------------------------------------
		#next of kin ancilliary information - relationship, contact phone, browse database
		#-----------------------------------------------------------------------------------------------------------------------
		self.sizer_nok_relationship =wxBoxSizer(wxHORIZONTAL)
		self.lbl_relationshipNOK = BlueLabel_Normal(self,-1,"Relationship",wxLEFT)
		self.cmb_relationshipNOK= wxComboBox(self, -1, "", wxDefaultPosition,wxDefaultSize,
		['Father','Mother','Daughter','Son','Aunt','Uncle','Unknown'], wxCB_DROPDOWN)
		self.sizer_nok_relationship.Add(self.lbl_relationshipNOK,3,wxEXPAND)
		self.sizer_nok_relationship.Add(self.cmb_relationshipNOK,13,wxEXPAND)
		self.sizer_search_nok  = wxBoxSizer(wxHORIZONTAL)
		self.btn_browseNOK = wxButton(self,-1,"Browse Database for Next Of Kin Details")
		self.sizer_search_nok.Add(self.lbl_space,3,wxEXPAND)
		self.sizer_search_nok.Add(self.btn_browseNOK,13, wxEXPAND|wxTOP,5)
		self.sizer_all_nokstuff = wxBoxSizer(wxVERTICAL)
		self.sizer_all_nokstuff.Add(self.sizer_nok_relationship,0,wxEXPAND)
		self.sizer_all_nokstuff.Add(self.sizer_search_nok,0,wxEXPAND|wxTOP|wxBOTTOM,5)
		#-----------------------------------------------------------------------------------------------------------------------------------------------------------
		#This section undecided - in AU example need medicare/repatriation/pharmaceutical benefits
		# Liz Dodd says: DVA-Gold DVA-White(specified illness) DVA-RED/ORANGE (medications only)
		#	Health care card/Seniors Health Care Card Pension Card Pharmaceutical Benefits Safety Net Number
		#-----------------------------------------------------------------------------------------------------------------------------------------------------------
		self.lbl_Identity_numbers =BlueLabel_Bold(self,-1,"Card Numbers",wxLEFT)
		self.sizer_idnumbers_line1 = wxBoxSizer(wxHORIZONTAL)
		self.sizer_idnumbers_line1.Add(self.lbl_space,1,wxEXPAND|wxTOP|wxBOTTOM,1)
		self.sizer_idnumbers_line1.Add(self.lbl_space,1,wxEXPAND)
		self.sizer_idnumbers_line1.Add(self.lbl_Identity_numbers,1,wxEXPAND|wxTOP|wxBOTTOM,1)
		self.sizer_idnumbers_line1.Add(self.lbl_space,1,wxEXPAND|wxTOP|wxBOTTOM,1)
		self.sizer_all_nokstuff.Add(self.sizer_idnumbers_line1,0,wxEXPAND|wxTOP|wxBOTTOM,1)
		#------------------------------------------------------------------------------------------------------------------------
		#Now add all the lines for the left side of the screen on their sizers to sizer_leftside
		#i.e Patient Names through to their contact details
		#------------------------------------------------------------------------------------------------------------------------
		self.sizer_leftside = wxBoxSizer(wxVERTICAL)
		self.sizer_leftside.Add(0,10,0)
		self.sizer_leftside.Add(self. sizer_line1,0,wxEXPAND|wxLEFT|wxRIGHT,20)
		self.sizer_leftside.Add(self.sizer_line2,0,wxEXPAND|wxLEFT|wxRIGHT,20)
		self.sizer_leftside.Add(self. sizer_line3,0,wxEXPAND|wxLEFT|wxRIGHT,20)
		self.sizer_leftside.Add(self. sizer_lbl_heading_address,0,wxEXPAND|wxLEFT|wxRIGHT,20)
		self.sizer_leftside.Add(self. sizer_street  ,0,wxEXPAND|wxLEFT|wxRIGHT,20)
		self.sizer_leftside.Add(self. sizer_suburb  ,0,wxEXPAND|wxLEFT|wxRIGHT,20)
		self.sizer_leftside.Add(self. sizer_stateandpostcode,0,wxEXPAND|wxLEFT|wxRIGHT,20)
		self.sizer_leftside.Add(self. sizer_addresstype_chkpostal,0,wxEXPAND|wxLEFT|wxRIGHT,20)
		self.sizer_leftside.Add(self. sizer_contacts_line1,0,wxEXPAND|wxLEFT|wxRIGHT,20)
		self.sizer_leftside.Add(self. sizer_contacts_line2,0,wxEXPAND|wxLEFT|wxRIGHT,20)
		self.sizer_leftside.Add(self. sizer_contacts_line3,0,wxEXPAND|wxLEFT|wxRIGHT,20)
		self.sizer_leftside.Add(self. sizer_contacts_line4,0,wxEXPAND|wxLEFT|wxRIGHT,20)
		#------------------------------------------------------------------------------------------------------------------------
		#Now add all the lines for the right side of the screen on their sizers to sizer_leftside
		#is Date of Birth through to card numbers
		#------------------------------------------------------------------------------------------------------------------------
		self.sizer_rightside = wxBoxSizer(wxVERTICAL)
		self.sizer_rightside.Add(0,10,0)
		self.sizer_rightside.Add(self.sizer_birthdatemarital,0,wxEXPAND|wxLEFT|wxRIGHT,20)
		self.sizer_rightside.Add(self.sizer_occupation ,0,wxEXPAND|wxLEFT|wxRIGHT,20)
		self.sizer_rightside.Add(self.sizer_countryofbirth ,0,wxEXPAND|wxLEFT|wxRIGHT,20)
		self.sizer_rightside.Add(self.sizer_heading_nok ,0,wxEXPAND|wxLEFT|wxRIGHT,20)
		self.sizer_rightside.Add(self.sizer_patientnameaddressNOK ,0,wxEXPAND|wxLEFT|wxRIGHT,20)
		self.sizer_rightside.Add(self.sizer_nok_relationship ,0,wxEXPAND|wxLEFT|wxRIGHT,20)
		self.sizer_rightside.Add(self.sizer_search_nok ,0,wxEXPAND|wxLEFT|wxRIGHT,20)
		self.sizer_rightside.Add(self.sizer_idnumbers_line1,0,wxEXPAND|wxLEFT|wxRIGHT,20)
		#---------------------------------------------------------------------------------------------------------------------------------------------------
		#Now add the left and right hand screen sizers to a container sizer (sizer_bottom_patient_dataentry)
		#---------------------------------------------------------------------------------------------------------------------------------------------------
		self.sizer_bottom_patient_dataentry = wxBoxSizer(wxHORIZONTAL)
		self.sizer_bottom_patient_dataentry.Add(self.sizer_leftside,1,wxEXPAND) #|wxLEFT|wxRIGHT,20)
		self.sizer_bottom_patient_dataentry.Add(self.sizer_rightside,1,wxEXPAND)# wxLEFT|wxRIGHT,20)
		#self.ext_id_panel = ExtIDPanel (self, self.gs)
		#------------------------------------------------------------------------------------------------------------------------------------------
		#add the top sizer with patient list + photo, and the bottom sizer with data-entry to main sizer
		#------------------------------------------------------------------------------------------------------------------------------------------
		self.sizer_main = wxBoxSizer(wxVERTICAL)
		self.sizer_main.Add (self.sizer_for_patientlist_and_photo,1,wxEXPAND)
		self.sizer_main.Add(self.sizer_bottom_patient_dataentry,0,wxEXPAND|wxBOTTOM,20)

		self.__create_input_field_map()
		self.__add_character_validators()
#		self.__connect_commands()
		self.__register_events()

		# adjust layout
		self.SetSizer(self.sizer_main)
		self.SetAutoLayout(True)
		self.sizer_main.Fit(self)
#		self.Show(True)

	def __register_events(self):
		# patient list popup menu
		EVT_RIGHT_UP(self.patientlist, self.OnRightClick_patientlist)
		EVT_MENU(self, ID_PUP_ITEM_SaveDisplayLayout, self.OnPopupSaveDisplayLayout)
		# patient photo
		EVT_RIGHT_UP(self.photopanel, self.OnRightClick_photo)

	def OnRightClick_photo(self, event):
		if not hasattr(self, "popupID15"):
			self.popupID15 = wxNewId()
			self.popupID16 = wxNewId()
			EVT_MENU(self, self.popupID15, self.OnPopupFifteen)
			EVT_MENU(self, self.popupID16, self.OnPopupSixteen)
		self.menu_patientphoto = wxMenu()
		self.menu_patientphoto.Append(self.popupID15, "Aquire Photo")
		self.menu_patientphoto.Append(self.popupID16, "Import Photo")
		self.menu_patientphoto.Append(self.popupID15, "Export Photo")
		self.menu_patientphoto.Append(self.popupID16, "Delete Photo")

		self.PopupMenu(self.menu_patientphoto, event.GetPosition())
		self.menu_patientphoto.Destroy()

	def OnRightClick_patientlist(self, event):
# 		Maximise Viewing Area
# 		Minimise Viewing Area
# 		---------------------
# 		Add Person
# 		Add Address for person
# 		Add Family Member
# 		--------------------------
# 		Delete Person
# 		Delete Address for person
# 		Undo Delete
# 		------------------------------------
# 		Sort A_Z
# 		Sort Z_A
# 		--------------
# 		Change Font
# 		Save Display Layout
# 		--------------------------
# 		Build SQL
# 		-------------------
# 		Help
# 		----------------
# 		Exit

		#self.log.WriteText("OnRightClick\n")

		# only do this part the first time so the events are only bound once
		if not hasattr(self, "popupID1"):
			self.popupID1 = wxNewId()
			self.popupID2 = wxNewId()
			self.popupID3 = wxNewId()
			self.popupID4 = wxNewId()
			self.popupID5 = wxNewId()
			self.popupID6 = wxNewId()
			self.popupID7 = wxNewId()
			self.popupID8 = wxNewId()
			self.popupID9 = wxNewId()
			self.popupID11 = wxNewId()
			self.popupID12 = wxNewId()
			self.popupID13 = wxNewId()
			self.popupID14 = wxNewId()

			EVT_MENU(self, self.popupID1, self.OnPopupOne)
			EVT_MENU(self, self.popupID2, self.OnPopupTwo)
			EVT_MENU(self, self.popupID3, self.OnPopupThree)
			EVT_MENU(self, self.popupID4, self.OnPopupFour)
			EVT_MENU(self, self.popupID5, self.OnPopupFive)
			EVT_MENU(self, self.popupID6, self.OnPopupSix)
			EVT_MENU(self, self.popupID7, self.OnPopupSeven)
			EVT_MENU(self, self.popupID8, self.OnPopupEIght)
			EVT_MENU(self, self.popupID9, self.OnPopupNine)
			EVT_MENU(self, self.popupID11, self.OnPopupEleven)
			EVT_MENU(self, self.popupID12, self.OnPopupTwelve)
			EVT_MENU(self, self.popupID13, self.OnPopupThirteen)
			EVT_MENU(self, self.popupID14, self.OnPopupFourteen)

		#-----------------------------------------------------------------
		# make a menu to popup over the patient list
		#-----------------------------------------------------------------


		self.menu_patientlist = wxMenu()
		#Trigger routine to clear all textboxes to add entirely new person
		item = wxMenuItem(self.menu_patientlist, self.popupID1,"Add Person")
		item.SetBitmap(images_patient_demographics.getperson_addBitmap())
		self.menu_patientlist.AppendItem(item)

		#Trigger routine to clear all address textboxes only to add another address
		item = wxMenuItem(self.menu_patientlist, self.popupID2, "Add Address for person")
		item.SetBitmap(images_patient_demographics.getbranch_addBitmap())
		self.menu_patientlist.AppendItem(item)
		#Trigger routine to clear person details, leave address, home phone
		item = wxMenuItem(self.menu_patientlist, self.popupID3,"Add Family Member")
		item.SetBitmap(images_patient_demographics.getemployeesBitmap())
		self.menu_patientlist.AppendItem(item)
		self.menu_patientlist.AppendSeparator()
		#Trigger routine to delete a person
		item = wxMenuItem(self.menu_patientlist, self.popupID4,"Delete Person")
		item.SetBitmap(images_patient_demographics.getcutBitmap())
		self.menu_patientlist.AppendItem(item)

		#Trigger routine to delete an address (if > 1) for a person
		self.menu_patientlist.Append(self.popupID5, "Delete Address for person")
		self.menu_patientlist.AppendSeparator()

		#Trigger nested undo-deletes
		self.menu_patientlist.Append(self.popupID6, "Undo Delete")
		#self.menu_patientlist.AppendItem(item)
		self.menu_patientlist.AppendSeparator()
		#trigger routine to sort visible patient lists by surname A_Z
		item = wxMenuItem(self.menu_patientlist, self.popupID7,"Sort A_Z")
		item.SetBitmap(images_patient_demographics.getsort_A_ZBitmap())
		self.menu_patientlist.AppendItem(item)

		item = wxMenuItem(self.menu_patientlist, self.popupID8,"Sort Z_A")
		item.SetBitmap(images_patient_demographics.getsort_Z_ABitmap())
		self.menu_patientlist.AppendItem(item)
		self.menu_patientlist.AppendSeparator()

		self.menu_patientlist.Append(self.popupID9, "Change Font")

		self.menu_patientlist.Append(ID_PUP_ITEM_SaveDisplayLayout, "Save Display Layout")
		#self.menu_patientlist.AppendItem(item)
		self.menu_patientlist.AppendSeparator()
		#Save search query to database as user defined query
		item = wxMenuItem(self.menu_patientlist, self.popupID11, "Build SQL")
		item.SetBitmap(images_patient_demographics.getsqlBitmap())
		self.menu_patientlist.AppendItem(item)
		self.menu_patientlist.AppendSeparator()
		#Jump to help for patients_list
		item = wxMenuItem(self.menu_patientlist, self.popupID12,  "Help")
		item.SetBitmap(images_patient_demographics.gethelpBitmap())
		self.menu_patientlist.AppendItem(item)
		self.menu_patientlist.AppendSeparator()


		# Popup the menu.  If an item is selected then its handler
		# will be called before PopupMenu returns.
		self.PopupMenu(self.menu_patientlist, event.GetPosition())
		self.menu_patientlist.Destroy()


	def OnPopupOne(self, event):
	       print self.patientlist.GetColumnWidth(0)
		#self.log.WriteText("Popup one\n")

	def OnPopupTwo(self, event):
		self.log.WriteText("Popup two\n")

	def OnPopupThree(self, event):
		self.log.WriteText("Popup three\n")

	def OnPopupFour(self, event):
		self.log.WriteText("Popup four\n")

	def OnPopupFive(self, event):
		self.log.WriteText("Popup five\n")

	def OnPopupSix(self, event):
		self.log.WriteText("Popup six\n")

	def OnPopupSeven(self, event):
		self.log.WriteText("Popup seven\n")

	def OnPopupEIght(self, event):
		self.log.WriteText("Popup eight\n")

	def OnPopupNine(self, event):
		self.log.WriteText("Popup nine\n")

	def OnPopupSaveDisplayLayout(self, event):
		pat_cols_list = []
		# get widths of columns
		for col in range (0,self.patientlist.GetColumnCount()):
			pat_cols_list.append(self.patientlist.GetColumnWidth(col))
		# set the value for the current user/workplace
		gmCfg.setDBParam (
			user = _whoami.get_db_account(),
			option = "widgets.demographics.patientlist.column_sizes",
			value = pat_cols_list
		)

	def OnPopupEleven(self, event):
		self.log.WriteText("Popup nine\n")

	def OnPopupTwelve(self, event):
		self.log.WriteText("Popup nine\n")

	def OnPopupThirteen(self, event):
		self.log.WriteText("Popup nine\n")

	def OnPopupFourteen(self, event):
		self.log.WriteText("Popup nine\n")

	def OnPopupFifteen(self, event):
		self.log.WriteText("Popup nine\n")

	def OnPopupSixteen(self, event):
		self.log.WriteText("Popup nine\n")
#
 	def __add_character_validators(self):
		return
 		 #IAN TO RECONNECT - this routine bombs on my machine- RT
# 		self.validator = gmCharacterValidator.CharValidator()
# 		m = self.input_fields
# 		for k in ['firstname', 'surname', 'preferred']:
# 			self.validator.setCapitalize(m[k])
# 		for k in ['urb', 'country']:
# 			self.validator.setUpperAlpha(m[k])
#
# 		for k in ['mobile', 'fax', 'homephone', 'workphone']: # in AU only ? , 'postcode']:
# 			self.validator.setDigits(m[k])
	


# 	def __connect_commands(self):
# 		return
	 #IAN TO RECONNECT TO TOP MENU/OR POPUP MENU OVER PATIENTSLIST
# 		b = self.btn_add_address
# 		EVT_BUTTON(b, b.GetId() , self._add_address_pressed)
# 		b = self.btn_del_address
# 		EVT_BUTTON(b, b.GetId() ,  self._del_address_pressed)
#
# 		b = self.btn_save
# 		EVT_BUTTON(b, b.GetId(), self._save_btn_pressed)
# 		EVT_BUTTON(self.btn_del, self.btn_del.GetId (), self._del_button_pressed)
# 		EVT_BUTTON(self.btn_new, self.btn_new.GetId (), self._new_button_pressed)
#
# 		l = self.addresslist
# 		EVT_LISTBOX_DCLICK(l, l.GetId(), self._address_selected)
#
# 		EVT_BUTTON(self.btn_photo_import, self.btn_photo_import.GetId (), self._photo_import)
# 		EVT_BUTTON(self.btn_photo_export, self.btn_photo_export.GetId (), self._photo_export)

	def __urb_selected(self, id):
		 #IAN TO RECONNECT
		if id:
			try:
				self.txt_postcode.SetValue (gmDemographicRecord.getPostcodeForUrbId(id))
				self.txt_postcode.input_was_selected= 1
			except:
				gmLog.gmDefLog.LogException( "select urb problem", sys.exc_info(), verbose=0)

	def _address_selected( self, event):
		 #IAN TO RECONNECT
 		self._update_address_fields_on_selection()

	def _update_address_fields_on_selection(self):
		#IAN TO RECONNECT
		i = self.addresslist.GetSelection()
		data = self.addr_cache[i]
		m = self.input_fields
		m['address_type'].SetValue(data['type'])
		for k,v in data.items():
			if not k in ['dirty', 'type', 'ID']:
				m[k].SetValue(v)

	def _save_addresses(self):
		 #IAN TO RECONNECT
		myPatient = self.patient.get_demographic_record()
		for data in self.addr_cache:
			if data.has_key('dirty'):
				myPatient.linkNewAddress( data['type'], data['number'], data['street'], data['urb'], data['postcode'] )
		for ID in self.to_delete:
			myPatient.unlinkAddress (ID)

	def _save_btn_pressed(self, event):
		 #IAN TO RECONNECT
		try:
			self._save_data()
		except:
			_log.LogException ('failed on save data', sys.exc_info (), verbose=0)

	def _photo_import (self, event):
		 #IAN TO RECONNECT
		try:
			dialogue = wxFileDialog (self, style=wxOPEN | wxFILE_MUST_EXIST, wildcard = "*.bmp|*.png|*.jpg|*.jpeg|*.pnm|*.xpm")
			if dialogue.ShowModal () == wxID_OK:
				photo = dialogue.GetPath ()
				self.patientpicture.setPhoto (photo)
				doc = gmMedDoc.create_document (self.patient.get_ID ())
				doc.update_metadata({'type ID':gmMedDoc.MUGSHOT})
				obj = gmMedDoc.create_object (doc)
				obj.update_data_from_file (photo)
		except:
			_log.LogException ('failed to import photo', sys.exc_info (), verbose= 0)

	def _photo_export (self, event):
		 #IAN TO RECONNECT
		try:
			dialogue = wxFileDialog (self, style=wxSAVE)
			if dialogue.ShowModal () == wxID_OK:
				shutil.copyfile (self.patientpicture.getPhoto (), dialogue.GetPath ())
		except:
			_log.LogException ('failed to export photo', sys.exc_info (), verbose= 0)

	def setNewPatient(self, isNew):
		#IAN TO RECONNECT
		self._newPatient = isNew

	def _new_button_pressed(self, event):
		 #IAN TO RECONNECT

		self.setNewPatient(1)
		self.__init_data()
		id = gmPatient.create_dummy_identity()
		gmPatient.gmCurrentPatient(id)
	
	def __init_data(self):
		 #IAN TO RECONNECT
		for k, w in self.input_fields.items():
			try:
				w.SetValue('') # just looking at this makes my eyes water (IH)
			except:
				try:
					w.SetValue(0)
				except:
					pass
		self.__update_address_types()
		self.to_delete = [] # list of addresses to unlink
		self.addr_cache = []
		self.ext_id_panel.Clear ()

	def get_input_value_map(self):
 		 #IAN TO RECONNECT
		m = {}
		for k, v in self.input_fields.items():
			m[k] = v.GetValue()
		return m

	def validate_fields(self):
		 #IAN TO RECONNECT

		nameFields = [ self.value_map['firstname'].strip() , self.value_map['surname'].strip() ]
		if "" in nameFields or "?" in nameFields:
			raise Error("firstname and surname are required fields for identity")

	
	def _save_data(self):
		 #IAN TO RECONNECT
		m = self.input_fields
		self.value_map = self.get_input_value_map ()
		self.validate_fields()
		self._save_addresses()
		myPatient = self.patient.get_demographic_record()
		if m['firstname'].IsModified () or m['surname'].IsModified ():
			print "name is modified"
			myPatient.addName(self.value_map['firstname'].strip(), self.value_map['surname'].strip(), activate=1)
		for key, value in self.gendermap.items (): # find the backend code for selected gender
			if value == self.value_map['sex'] and key != self.old_gender: # has it changed?
				myPatient.setGender(key)
		if m['occupation'].IsModified ():
			myPatient.setOccupation (self.value_map['occupation'])
		if self.old_status != self.value_map['maritalstatus']:
			myPatient.setMaritalStatus (self.value_map['maritalstatus'])
		if m['birthdate'].IsModified ():
			myPatient.setDOB( self.value_map['birthdate'])
		if m['country'].IsModified ():
			myPatient.setCOB (self.value_map['country'])
		if self.value_map['title'] != self.old_title:
			myPatient.setTitle( self.value_map['title'])
		for str, const in [('fax', gmDemographicRecord.FAX), ('homephone', gmDemographicRecord.HOME_PHONE), ('workphone', gmDemographicRecord.WORK_PHONE), ('mobile', gmDemographicRecord.MOBILE), ('web', gmDemographicRecord.WEB), ('email', gmDemographicRecord.EMAIL)]:
			if m[str].IsModified ():
				myPatient.linkCommChannel (const, self.value_map[str])
		self.setNewPatient(0)

	def _del_button_pressed (self, event):
		 #IAN TO RECONNECT
		# do we really want this?
		pass


	def _add_address_pressed(self, event):
		 #IAN TO RECONNECT
		try:
			data = self._get_address_data()
			data['dirty'] = 1
			self.addr_cache.append (data)
			self._update_address_list_display()
		except:
			_log.LogException ('failed on add address', sys.exc_info (), verbose=0)

	def _del_address_pressed(self, event):
		 #IAN TO RECONNECT
		try:
			i = self.addresslist.GetSelection ()
			if self.addr_cache[i].has_key('ID'):
				self.to_delete.append (self.addr_cache[i]['ID'])
			del self.addr_cache[i]
			self._update_address_list_display()
		except:
			_log.LogException ('failed on delete address', sys.exc_info (), verbose=0)

	def _get_address_data(self):
		 #IAN TO RECONNECT
 		m = self.input_fields
		data = {}
		for f in ['number', 'street', 'urb', 'postcode']:
		 	data[f] = m[f].GetValue()
		data['type'] = m['address_type'].GetValue ()
		return data

	def _update_address_list_display(self):
		#IAN TO RECONNECT
		self.addresslist.Clear()
		for data in self.addr_cache:
			s = '%-10s - %s,%s,%s' % ( data['type'],  data['number'], data['street'], data['urb'])
			self.addresslist.Append(s)


	def __create_input_field_map(self):
		 #IAN TO RECONNECT
		prefixes = [ 'txt_', 'cb_', 'combo_' ]
		map = {}
		for k,v in self.__dict__.items():
			for prefix in prefixes:
				if k[:len(prefix)] == prefix:
					#print k," is a widget"
					map[ k[len(prefix):] ] = v

		#print "INPUT MAP FOR ", self, " = " , map
		self.input_fields = map


	def __update_addresses(self):
		 #IAN TO RECONNECT
		myPatient = self.patient.get_demographic_record()
		try:
			self.addr_cache = myPatient.getAddresses (None)
		except:
			_log.LogException ('failed to get addresses', sys.exc_info (), verbose=0)
		if self.addr_cache:
			self._update_address_list_display()
		else: # we have no addresses
			self.addresslist.Clear ()
		#self.txt_number.Clear ()
		self.txt_street.Clear ()
		self.txt_postcode.Clear ()
		self.txt_suburb.Clear ()
		self.combo_address_type.SetValue ('')



	def __update_nok(self):
		 #IAN TO RECONNECT
		"""this function is disabled until further notice. see l = []"""
		myPatient = self.patient.get_demographic_record ()
		#l = myPatient.get_relatives()
		l = [] # disabled for the time being
		l2 = []
		for m in l:
			s = """%-12s   - %s %s, %s, %s %s""" % (m['description'], m['firstnames'], m['lastnames'], m['gender'], _('born'), time.strftime('%d/%m/%Y', get_time_tuple(m['dob']) )  )
			l2.append( {'str':s, 'id':m['id'] } )
		self.lb_nameNOK.Clear()
		for data in l2:
			self.lb_nameNOK.Append( data['str'], data['id'] )

	def _updateUI(self):
		 #IAN TO RECONNECT
		"""on patient_selected() signal handler , inherited from gmPatientHolder.PatientHolder"""
		myPatient = self.patient.get_demographic_record()
		m = self.input_fields
		m['firstname'].SetValue( myPatient.get_names()['first'] )
		m['surname'].SetValue( myPatient.get_names()['last'] )
		title = myPatient.getTitle()
		if title == None:
			title = ''
		m['title'].SetValue( title )
		self.old_title = title
		dob = myPatient.getDOB()
		#mx date time object will not convert to int() sometimes, but always printable,
		# so parse it as a string , and extract into a 9-sequence time value, and then convert
		# with strftime.
		t = [ int(x) for x in  str(dob).split(' ')[0].split('-') ] + [0,0,0, 0,0,0 ]
		t = time.strftime('%d/%m/%Y', t)
		m['birthdate'].SetValue(t)
		m['country'].SetValue (myPatient.getCOB () or '')
		self.old_status = myPatient.getMaritalStatus ()
		m['maritalstatus'].SetSelection (m['maritalstatus'].FindString (self.old_status))
		m['occupation'].SetValue (myPatient.getOccupation () or '')
		self.old_gender = myPatient.getGender ()
		m['sex'].SetSelection (m['sex'].FindString (self.gendermap[self.old_gender]))
		m['email'].SetValue (myPatient.getCommChannel (gmDemographicRecord.EMAIL) or '')
		m['fax'].SetValue (myPatient.getCommChannel (gmDemographicRecord.FAX) or '')
		m['homephone'].SetValue (myPatient.getCommChannel (gmDemographicRecord.HOME_PHONE) or '')
		m['workphone'].SetValue (myPatient.getCommChannel (gmDemographicRecord.WORK_PHONE) or '')
		m['web'].SetValue (myPatient.getCommChannel (gmDemographicRecord.WEB) or '')
		m['mobile'].SetValue (myPatient.getCommChannel (gmDemographicRecord.MOBILE) or '')
		self.ext_id_panel.setDemo (myPatient)
		self.__update_addresses()
		self.__update_nok()

#============================================================
if __name__ == "__main__":
	from Gnumed.pycommon import gmGuiBroker
	app = wxPyWidgetTester(size = (800, 600))
	app.SetWidget(PatientsPanel, -1)
	app.MainLoop()
#============================================================
# $Log: gmDemographics.py,v $
# Revision 1.37  2004-08-18 08:15:21  ncq
# - check if column size for patient list is missing
#
# Revision 1.36  2004/08/16 13:32:19  ncq
# - rework of GUI layout by R.Terry
# - save patient list column width from right click popup menu
#
# Revision 1.35  2004/07/30 13:43:33  sjtan
#
# update import
#
# Revision 1.34  2004/07/26 12:04:44  sjtan
#
# character level immediate validation , as per Richard's suggestions.
#
# Revision 1.33  2004/07/20 01:01:46  ihaywood
# changing a patients name works again.
# Name searching has been changed to query on names rather than v_basic_person.
# This is so the old (inactive) names are still visible to the search.
# This is so when Mary Smith gets married, we can still find her under Smith.
# [In Australia this odd tradition is still the norm, even female doctors
# have their medical registration documents updated]
#
# SOAPTextCtrl now has popups, but the cursor vanishes (?)
#
# Revision 1.32  2004/07/18 20:30:53  ncq
# - wxPython.true/false -> Python.True/False as Python tells us to do
#
# Revision 1.31  2004/06/30 15:09:47  shilbert
# - more wxMAC fixes
#
# Revision 1.30  2004/06/29 22:48:47  shilbert
# - one more wxMAC fix
#
# Revision 1.29  2004/06/27 13:42:26  ncq
# - further Mac fixes - maybe 2.5 issues ?
#
# Revision 1.28  2004/06/23 21:26:28  ncq
# - kill dead code, fixup for Mac
#
# Revision 1.27  2004/06/20 17:28:34  ncq
# - The Great Butchering begins
# - remove dead plugin code
# - rescue binoculars xpm to artworks/
#
# Revision 1.26  2004/06/17 11:43:12  ihaywood
# Some minor bugfixes.
# My first experiments with wxGlade
# changed gmPhraseWheel so the match provider can be added after instantiation
# (as wxGlade can't do this itself)
#
# Revision 1.25  2004/06/13 22:31:48  ncq
# - gb['main.toolbar'] -> gb['main.top_panel']
# - self.internal_name() -> self.__class__.__name__
# - remove set_widget_reference()
# - cleanup
# - fix lazy load in _on_patient_selected()
# - fix lazy load in ReceiveFocus()
# - use self._widget in self.GetWidget()
# - override populate_with_data()
# - use gb['main.notebook.raised_plugin']
#
# Revision 1.24  2004/05/27 13:40:22  ihaywood
# more work on referrals, still not there yet
#
# Revision 1.23  2004/05/25 16:18:12  sjtan
#
# move methods for postcode -> urb interaction to gmDemographics so gmContacts can use it.
#
# Revision 1.22  2004/05/25 16:00:34  sjtan
#
# move common urb/postcode collaboration  to business class.
#
# Revision 1.21  2004/05/23 11:13:59  sjtan
#
# some data fields not in self.input_fields , so exclude them
#
# Revision 1.20  2004/05/19 11:16:09  sjtan
#
# allow selecting the postcode for restricting the urb's picklist, and resetting
# the postcode for unrestricting the urb picklist.
#
# Revision 1.19  2004/03/27 04:37:01  ihaywood
# lnk_person2address now lnk_person_org_address
# sundry bugfixes
#
# Revision 1.18  2004/03/25 11:03:23  ncq
# - getActiveName -> get_names
#
# Revision 1.17  2004/03/15 15:43:17  ncq
# - cleanup imports
#
# Revision 1.16  2004/03/09 07:34:51  ihaywood
# reactivating plugins
#
# Revision 1.15  2004/03/04 11:19:05  ncq
# - put a comment as to where to handle result from setCOB
#
# Revision 1.14  2004/03/03 23:53:22  ihaywood
# GUI now supports external IDs,
# Demographics GUI now ALPHA (feature-complete w.r.t. version 1.0)
# but happy to consider cosmetic changes
#
# Revision 1.13  2004/03/03 05:24:01  ihaywood
# patient photograph support
#
# Revision 1.12  2004/03/02 23:57:59  ihaywood
# Support for full range of backend genders
#
# Revision 1.11  2004/03/02 10:21:10  ihaywood
# gmDemographics now supports comm channels, occupation,
# country of birth and martial status
#
# Revision 1.10  2004/02/25 09:46:21  ncq
# - import from pycommon now, not python-common
#
# Revision 1.9  2004/02/18 06:30:30  ihaywood
# Demographics editor now can delete addresses
# Contacts back up on screen.
#
# Revision 1.8  2004/01/18 21:49:18  ncq
# - comment out debugging code
#
# Revision 1.7  2004/01/04 09:33:32  ihaywood
# minor bugfixes, can now create new patients, but doesn't update properly
#
# Revision 1.6  2003/11/22 14:47:24  ncq
# - use addName instead of setActiveName
#
# Revision 1.5  2003/11/22 12:29:16  sjtan
#
# minor debugging; remove _newPatient flag attribute conflict with method name newPatient.
#
# Revision 1.4  2003/11/20 02:14:42  sjtan
#
# use global module function getPostcodeByUrbId() , and renamed MP_urb_by_zip.
#
# Revision 1.3  2003/11/19 23:11:58  sjtan
#
# using local time tuple conversion function; mxDateTime object sometimes can't convert to int.
# Changed to global module.getAddressTypes(). To decide: mechanism for postcode update when
# suburb selected ( not back via gmDemographicRecord.getPostcodeForUrbId(), ? via linked PhraseWheel matchers ?)
#
# Revision 1.2  2003/11/18 16:46:02  ncq
# - sync with method name changes
#
# Revision 1.1  2003/11/17 11:04:34  sjtan
#
# added.
#
# Revision 1.1  2003/10/23 06:02:40  sjtan
#
# manual edit areas modelled after r.terry's specs.
#
# Revision 1.26  2003/04/28 12:14:40  ncq
# - use .internal_name()
#
# Revision 1.25  2003/04/25 11:15:58  ncq
# cleanup
#
# Revision 1.24  2003/04/05 00:39:23  ncq
# - "patient" is now "clinical", changed all the references
#
# Revision 1.23  2003/04/04 20:52:44  ncq
# - start disentanglement with top pane:
#   - remove patient search/age/allergies/patient details
#
# Revision 1.22  2003/03/29 18:27:14  ncq
# - make age/allergies read-only, cleanup
#
# Revision 1.21  2003/03/29 13:50:09  ncq
# - adapt to new "top row" panel
#
# Revision 1.20  2003/03/28 16:43:12  ncq
# - some cleanup in preparation of inserting the patient searcher
#
# Revision 1.19  2003/02/09 23:42:50  ncq
# - date time conversion to age string does not work, set to 20 for now, fix soon
#
# Revision 1.18  2003/02/09 12:05:02  sjtan
#
#
# wxBasePlugin is unnecessarily specific.
#
# Revision 1.17  2003/02/09 11:57:42  ncq
# - cleanup, cvs keywords
#
# old change log:
#	10.06.2002 rterry initial implementation, untested
#	30.07.2002 rterry images put in file
