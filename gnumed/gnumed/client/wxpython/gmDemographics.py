#############################################################################
# gmDemographics
# ----------------------------------
#
# This panel will hold all the patients details
#
# If you don't like it - change this code see @TODO!
#
# @copyright: authorcd
# @license: GPL (details at http://www.gnu.org)
# @dependencies: wxPython (>= version 2.3.1)
# @change log:
#	    10.06.2002 rterry initial implementation, untested
#           30.07.2002 rterry images put in file
# @TODO:
############################################################################
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/Attic/gmDemographics.py,v $
# $Id: gmDemographics.py,v 1.1 2003-11-17 11:04:34 sjtan Exp $
__version__ = "$Revision: 1.1 $"
__author__ = "R.Terry, SJ Tan"

if __name__ == "__main__":
	import sys
	sys.path.extend( [ '../python-common', '../business'] )

from wxPython.wx import *
from mx import DateTime
import gmPlugin
import gmGuiBroker
import gmPatientNameQuery
import gmLog, gmDispatcher, gmSignals
import gmSQLListControl, gmDataPanelMixin
from wxPython.wx import wxBitmapFromXPMData, wxImageFromBitmap
import cPickle, zlib
from string import *
import gmGP_PatientPicture

import gmPatientHolder
import time

from gmPhraseWheel import cPhraseWheel
from gmDemographicRecord import UrbMP , PostcodeMP, StreetMP

ID_PATIENT = wxNewId()
ID_PATIENTSLIST = wxNewId()
ID_ALL_MENU  = wxNewId()
ID_ADDRESSLIST = wxNewId()
ID_NAMESLIST = wxNewId()
ID_CURRENTADDRESS = wxNewId()
gmSECTION_PATIENT = 5
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
ID_BUTTONPHOTOAQUIRE = wxNewId()
ID_BUTTONPHOTOEXPORT = wxNewId()
ID_BUTTONPHOTOIMPORT = wxNewId()
ID_CHKBOXRESIDENCE = wxNewId()
ID_CHKBOXPOSTAL = wxNewId()
ID_CHKBOXPREFERREDALIAS = wxNewId()
ID_BUTTONFINDPATIENT = wxNewId()
ID_TXTPATIENTFIND = wxNewId()
ID_TXTPATIENTAGE = wxNewId()
ID_TXTPATIENTALLERGIES  = wxNewId()

#------------------------------------
#Dummy data to simulate allergy items
#------------------------------------
aliasdata = {
1 : ("Peter Patient"),
2 : ("Bruce Dag"),
}
namelistdata = [
	'Smith Adan 129 Box Hill Road BOX HILL etc....',
	'Smith Jean 52 WhereEver Street CANBERRA etc.....',
	'Smith Michael 99 Longbeach Rd MANLYVALE  etc........'
]

addressdata = ['129 Afred Street WARNERS BAY 2280', '99 Wolfe Street NEWCASTLE 2301']

#--------------------------------------------------
#Class which shows a blue bold label left justified
#--------------------------------------------------
class BlueLabel(wxStaticText):
	def __init__(self, parent, id, prompt):
		wxStaticText.__init__(self,parent, id,prompt,wxDefaultPosition,wxDefaultSize,wxALIGN_LEFT)
		self.SetFont(wxFont(12,wxSWISS,wxNORMAL,wxBOLD,false,''))
		self.SetForegroundColour(wxColour(0,0,131))
#------------------------------------------------------------
#text control class to be later replaced by the gmPhraseWheel
#------------------------------------------------------------
class TextBox_RedBold(wxTextCtrl):
	def __init__ (self, parent, id): #, wxDefaultPostion, wxDefaultSize):
		wxTextCtrl.__init__(self,parent,id,"",wxDefaultPosition, wxDefaultSize,wxSIMPLE_BORDER)
		self.SetForegroundColour(wxColor(255,0,0))
		self.SetFont(wxFont(12,wxSWISS,wxNORMAL, wxBOLD,false,''))
class TextBox_BlackNormal(wxTextCtrl):
	def __init__ (self, parent, id): #, wxDefaultPostion, wxDefaultSize):
		wxTextCtrl.__init__(self,parent,id,"",wxDefaultPosition, wxDefaultSize,wxSIMPLE_BORDER)
		self.SetForegroundColour(wxColor(0,0,0))
		self.SetFont(wxFont(12,wxSWISS,wxNORMAL, wxBOLD,false,''))
#--------------------------------------------------------------------------------





#------------------------------------------------------------
class PatientsPanel(wxPanel, gmDataPanelMixin.DataPanelMixin, gmPatientHolder.PatientHolder):
	#def __init__(self, parent, plugin, id=wxNewId ()):
	def __init__(self, parent, id= -1):
		wxPanel.__init__(self, parent, id ,wxDefaultPosition,wxDefaultSize,wxRAISED_BORDER|wxTAB_TRAVERSAL)
		gmDataPanelMixin.DataPanelMixin.__init__(self)
		gmPatientHolder.PatientHolder.__init__(self)
		self.gb = gmGuiBroker.GuiBroker ()
		try:
			self.mwm = self.gb['clinical.manager']
		except:
			self.mwm = {}
	#	self.plugin = plugin
		# controls on the top toolbar are available via plugin.foo
		self.addresslist = wxListBox(self,ID_NAMESLIST,wxDefaultPosition,wxDefaultSize,addressdata,wxLB_SINGLE)
		self.addresslist.SetFont(wxFont(12,wxSWISS, wxNORMAL, wxNORMAL, false, '')) #first list with patient names
		self.addresslist.SetForegroundColour(wxColor(180,182,180))
		# code to link up SQLListControl
		self.patientslist = gmSQLListControl.SQLListControl (self, ID_PATIENTSLIST, hideid=true, style= wxLC_REPORT|wxLC_NO_HEADER|wxSUNKEN_BORDER)
		self.patientslist.SetFont(wxFont(12,wxSWISS, wxNORMAL, wxNORMAL, false, '')) #first list with patient names
		EVT_LIST_ITEM_SELECTED (self.patientslist, ID_PATIENTSLIST, self.OnPatient)
		self.lbl_surname = BlueLabel(self,-1,"Surname")
		self.lbl_firstname = BlueLabel(self,-1,"Firstname")
		self.lbl_preferredname = BlueLabel(self,-1,"Salutation")
		self.lbl_title = BlueLabel(self,-1,"Title")
		self.lbl_sex = BlueLabel(self,-1,"Sex ")
		self.lbl_street = BlueLabel(self,-1,"Street")
		self.lbl_suburb = BlueLabel(self,-1,"Suburb")
		self.lbl_zip = BlueLabel(self,-1,"Postcode")
		self.lbl_address_s = BlueLabel(self,-1,"Address(s)")
		self.lbl_birthdate = BlueLabel(self,-1,"Birthdate")
		self.lbl_maritalstatus = BlueLabel(self,-1,"  Marital Status")
		self.lbl_occupation = BlueLabel(self,-1,"Occupation")
		self.lbl_birthplace = BlueLabel(self,-1,"Born In")
		self.lbl_nextofkin = BlueLabel(self,-1,"")
		self.lbl_addressNOK = BlueLabel(self,-1,"Next of Kin")
		self.lbl_relationship = BlueLabel(self,-1,"  Relationship  ")
		self.lbl_homephone = BlueLabel(self,-1,"Home Phone")
		self.lbl_workphone = BlueLabel(self,-1,"Work Phone")
		self.lbl_fax = BlueLabel(self,-1,"Fax")
		self.lbl_mobile = BlueLabel(self,-1,"Mobile")
		self.lbl_email = BlueLabel(self,-1,"Email")
		self.lbl_web = BlueLabel(self,-1,"Web")
		self.lbl_mobile = BlueLabel(self,-1,"Mobile")
		self.lbl_line6gap = BlueLabel(self,-1,"")
		self.titlelist = ['Mr', 'Mrs', 'Miss', 'Mst', 'Ms', 'Dr', 'Prof']
          	self.combo_relationship = wxComboBox(self, 500, "", wxDefaultPosition,wxDefaultSize, ['Father','Mother'], wxCB_DROPDOWN)
		self.txt_surname = TextBox_RedBold(self,-1)
		self.combo_title = wxComboBox(self, 500, "", wxDefaultPosition,wxDefaultSize,self.titlelist, wxCB_DROPDOWN)
		self.txt_firstname = TextBox_RedBold(self,-1)
		self.combo_sex = wxComboBox(self, 500, "", wxDefaultPosition,wxDefaultSize, ['M','F'], wxCB_DROPDOWN)
		self.cb_preferredname = wxCheckBox(self, -1, _("Preferred Name"), wxDefaultPosition,wxDefaultSize, wxNO_BORDER)
		self.txt_preferred = TextBox_RedBold(self,-1)
		#self.txt_address = wxTextCtrl(self, 30, "",
		#			      wxDefaultPosition,wxDefaultSize, style=wxTE_MULTILINE|wxNO_3D|wxSIMPLE_BORDER)
		#self.txt_address.SetInsertionPoint(0)
		#self.txt_address.SetFont(wxFont(12,wxSWISS, wxNORMAL, wxNORMAL, false, ''))
		
		self.txt_no= wxTextCtrl( self, 30, "")
		self.txt_no.SetFont(wxFont(12,wxSWISS, wxNORMAL, wxNORMAL, false, ''))
		self.txt_street = cPhraseWheel( parent = self,id = -1 , aMatchProvider= StreetMP(),  pos = wxDefaultPosition, size=wxDefaultSize )
		self.txt_street.SetFont(wxFont(12,wxSWISS, wxNORMAL, wxNORMAL, false, ''))

		self.txt_suburb = cPhraseWheel( parent = self,id = -1 , aMatchProvider= UrbMP(), selectionOnly = 1, pos = wxDefaultPosition, size=wxDefaultSize , id_callback= self.__urb_selected)

		self.txt_zip  = cPhraseWheel( parent = self,id = -1 , aMatchProvider= PostcodeMP(), selectionOnly = 1,  pos = wxDefaultPosition, size=wxDefaultSize )

		self.txt_birthdate = TextBox_BlackNormal(self,-1)
		self.combo_maritalstatus = wxComboBox(self, 500, "", wxDefaultPosition,wxDefaultSize,
						      ['single','married'], wxCB_DROPDOWN)
		self.txt_occupation = TextBox_BlackNormal(self,-1)
		self.txt_countryofbirth = TextBox_BlackNormal(self,-1)
		self.btn_browseNOK = wxButton(self,-1,"Browse NOK") #browse database to pick next of Kin
	#	self.txt_nameNOK = wxTextCtrl(self, 30,
	#				      "Peter Smith \n"
	#				      "22 Lakes Way \n"
	#				      "Valentine 2280",
	#				      wxDefaultPosition,wxDefaultSize, style=wxTE_MULTILINE|wxNO_3D|wxSIMPLE_BORDER)
	#	self.txt_nameNOK.SetInsertionPoint(0)
	#	self.txt_nameNOK.SetFont(wxFont(12,wxSWISS, wxNORMAL, wxNORMAL, false, ''))
		self.txt_nameNOK = wxListBox( self, 30)
		self.txt_homephone = TextBox_BlackNormal(self,-1)
		self.txt_workphone = TextBox_BlackNormal(self,-1)
		self.txt_fax = TextBox_BlackNormal(self,-1)

		self.txt_email = TextBox_BlackNormal(self,-1)
		self.txt_web = TextBox_BlackNormal(self,-1)
		self.txt_mobile = TextBox_BlackNormal(self,-1)

                #----------------------
		#create the check boxes
		#----------------------
		self.cb_addressresidence = wxCheckBox(self, -1, " Residence ", wxDefaultPosition,wxDefaultSize, wxNO_BORDER)
		self.cb_addresspostal = wxCheckBox(self, -1, " Postal ", wxDefaultPosition,wxDefaultSize, wxNO_BORDER)
		#--------------------
		# create the buttons
		#--------------------
		self.btn_photo_import= wxButton(self,-1,"Import")
		self.btn_photo_export = wxButton(self,-1,"Export")
		self.btn_photo_aquire = wxButton(self,-1,"Acquire")

		
		#-------------------------------------------------------
		#Add the each line of controls to a horizontal box sizer
		#-------------------------------------------------------
		self.sizer_line0_left = wxBoxSizer(wxHORIZONTAL)
		#line one:surname, title
		self.sizer_line1_left = wxBoxSizer(wxHORIZONTAL)
		self.sizer_line1_left.Add(self.lbl_surname,3, wxGROW|wxALIGN_CENTER_VERTICAL,5)
		self.sizer_line1_left.Add(self.txt_surname,7,wxEXPAND)
		self.sizer_line1_left.Add(0,0,1)
		self.sizer_line1_left.Add(self.lbl_title,2,wxALIGN_CENTER_VERTICAL, 5)
		self.sizer_line1_left.Add(self.combo_title,4,wxEXPAND)
		#line two:firstname, sex
		self.sizer_line2_left = wxBoxSizer(wxHORIZONTAL)
		self.sizer_line2_left.Add(self.lbl_firstname,3,wxGROW|wxALIGN_CENTER_VERTICAL,5)
		self.sizer_line2_left.Add(self.txt_firstname,7,wxEXPAND)
		self.sizer_line2_left.Add(0,0,1)
		self.sizer_line2_left.Add(self.lbl_sex,2,wxGROW|wxALIGN_CENTER_VERTICAL,5)
		self.sizer_line2_left.Add(self.combo_sex,4,wxEXPAND)
		#line three:preferred salutation
		self.sizer_line3_left = wxBoxSizer(wxHORIZONTAL)
		self.sizer_line3_left.Add(self.lbl_preferredname,3,wxGROW|wxALIGN_CENTER_VERTICAL,5)
		self.sizer_line3_left.Add(self.txt_preferred,7,wxEXPAND)
		self.sizer_line3_left.Add(1,0,7)
		#line four: preferred alias
		self.sizer_line4_left = wxBoxSizer(wxHORIZONTAL)
		self.sizer_line4_left.Add(1,0,3)
		self.sizer_line4_left.Add(self.cb_preferredname,7,wxEXPAND)
		self.sizer_line4_left.Add(1,0,7)
		#line6 on this left side is blank
		self.sizer_line6_left = wxBoxSizer(wxHORIZONTAL)
		self.sizer_line6_left.Add(self.lbl_line6gap,1,wxEXPAND)
		#----------------
		#3:street details
		#a) the label
		sizer_lblstreet = wxBoxSizer(wxVERTICAL)
		sizer_lblstreet.Add(self.lbl_street,0, wxEXPAND)
		#--------------------
		#3:street details
		#b) multiline textbox
		#-------------------
		self.sizer_line7_left = wxBoxSizer(wxHORIZONTAL)
		#self.sizer_line7_left.Add(0,0,1)
		#------------------------------
		#3:street details
		#c) residence or postal address
		#------------------------------
		sizer_respostal = wxBoxSizer(wxHORIZONTAL)
		sizer_respostal.Add(self.cb_addressresidence,1,wxEXPAND)
		sizer_respostal.Add(self.cb_addresspostal,1,wxEXPAND)

		#sizer_respostal.Add(1,0,1)
		self.sizer_line7_left = wxBoxSizer(wxHORIZONTAL)
		self.sizer_line7_left.Add(sizer_lblstreet,3,wxALIGN_CENTER_VERTICAL,5)
		self.sizer_line7_left.Add(self.txt_no,2,wxEXPAND)
		self.sizer_line7_left.Add(0,0,1)
		self.sizer_line7_left.Add(self.txt_street,4,wxEXPAND)
		self.sizer_line7_left.Add(sizer_respostal,6,wxEXPAND)
		#--------------------------
		# create the suburb details
		#--------------------------
		self.sizer_line8_left = wxBoxSizer(wxHORIZONTAL)
		self.sizer_line8_left.Add(self.lbl_suburb,3,wxALIGN_CENTER_VERTICAL,5)
		self.sizer_line8_left.Add(self.txt_suburb,7,wxEXPAND)
		self.sizer_line8_left.Add(0,0,1)
		self.sizer_line8_left.Add(self.lbl_zip,3,wxALIGN_CENTER_VERTICAL,5)
		self.sizer_line8_left.Add(self.txt_zip,3,wxEXPAND)

		#--------------------------
		# create address editing
		#-------------------------
		sizer_line8b_left = wxBoxSizer(wxHORIZONTAL)
		label_addr_type = BlueLabel( self, -1, _('address type') ) 
		self.combo_address_type = wxComboBox(self, -1)
		sizer_line8b_left.Add(label_addr_type, 0, wxALIGN_CENTER_VERTICAL, 5)
		sizer_line8b_left.Add(self.combo_address_type, 2, wxEXPAND)
		self.btn_add_address = wxButton(self, -1, _('add address'))
		self.btn_del_address= wxButton(self, -1, _('delete'))
		sizer_line8b_left.Add( self.btn_add_address, 1, wxEXPAND)
		sizer_line8b_left.Add( self.btn_del_address, 1, wxEXPAND)
		#--------------------------------
		# create the multiple address box
		#--------------------------------
		self.sizer_line9_left = wxBoxSizer(wxHORIZONTAL)
		self.sizer_line9_left.Add(self.lbl_address_s,3,wxALIGN_CENTER_VERTICAL,5)
		self.sizer_line9_left.Add(self.addresslist,14,wxEXPAND)
		#-------------------------------------------------------------------------
		#now add all the left hand line sizers to the one left hand vertical sizer
		#-------------------------------------------------------------------------
		self.leftside = wxBoxSizer(wxVERTICAL)
		self.leftside.Add(self.sizer_line1_left,0,wxEXPAND|wxALL,1)
		self.leftside.Add(self.sizer_line2_left,0,wxEXPAND|wxALL,1)
		self.leftside.Add(self.sizer_line3_left,0,wxEXPAND|wxALL,1)
		self.leftside.Add(self.sizer_line4_left,0,wxEXPAND|wxALL,1)
		self.leftside.Add(self.sizer_line6_left,0,wxEXPAND|wxALL,1)
		self.leftside.Add(self.sizer_line7_left,0,wxEXPAND|wxALL,1)
		self.leftside.Add(self.sizer_line8_left,0,wxEXPAND|wxALL,1)
		self.leftside.Add(sizer_line8b_left,0,wxEXPAND|wxALL,1)
		self.leftside.Add(self.sizer_line9_left,0,wxEXPAND|wxALL,1)
		#---------------------------------------------------
		#now add textboxes etc to the right hand line sizers
		#---------------------------------------------------
		self.sizer_line0_right = wxBoxSizer(wxHORIZONTAL)
		self.sizer_line1_right = wxBoxSizer(wxHORIZONTAL)
		self.sizer_line2_right = wxBoxSizer(wxHORIZONTAL)
		self.sizer_line3_right = wxBoxSizer(wxHORIZONTAL)
		self.sizer_line4_right = wxBoxSizer(wxHORIZONTAL)
		self.sizer_line5_right = wxBoxSizer(wxHORIZONTAL)
		self.sizer_line6_right = wxBoxSizer(wxHORIZONTAL)
		self.sizer_line7_right = wxBoxSizer(wxHORIZONTAL)
		self.sizer_line8_right = wxBoxSizer(wxHORIZONTAL)
		self.sizer_line9_right = wxBoxSizer(wxHORIZONTAL)
		self.sizer_line10_right = wxBoxSizer(wxHORIZONTAL)
		self.sizer_line11_right = wxBoxSizer(wxHORIZONTAL)
		#line1 _ birthdate, maritial status
		self.sizer_line1_right.Add(self.lbl_birthdate,2,wxALIGN_CENTER_VERTICAL,0)
		self.sizer_line1_right.Add(self.txt_birthdate,2,wxALIGN_LEFT)
		self.sizer_line1_right.Add(self.lbl_maritalstatus,2,wxALIGN_CENTRE,0)
		self.sizer_line1_right.Add(self.combo_maritalstatus, 2, wxALIGN_CENTER_VERTICAL,0)
		#line2 - occupation (use word wheel later in place of text box)
		self.sizer_line2_right.Add(self.lbl_occupation,2,wxALIGN_CENTER_VERTICAL,0)
		self.sizer_line2_right.Add(self.txt_occupation,6,wxEXPAND)
		#line3 - country of birth (use word wheel later)
		self.sizer_line3_right.Add(self.lbl_birthplace,2,wxALIGN_CENTER_VERTICAL,0)
		self.sizer_line3_right.Add(self.txt_countryofbirth,6,wxEXPAND)
		#line 4 - next of kin + browse for next of kin
		self.sizer_line4_right.Add(self.lbl_nextofkin, 2,wxALIGN_CENTER_VERTICAL,0)
		self.sizer_line4_right.Add(self.btn_browseNOK,2, wxALIGN_CENTER_VERTICAL)
		#self.sizer_line4_right.Add(0,0,1)
		self.sizer_line4_right.Add(self.lbl_relationship,2, wxALIGN_CENTER_VERTICAL,0)
		self.sizer_line4_right.Add(self.combo_relationship,2,wxEXPAND)
		#name of next of kin
		self.sizer_gap_vertical =wxBoxSizer(wxVERTICAL)
		self.sizer_gap_vertical.Add(1,47,1)
		self.sizer_line5_right.Add(self.lbl_addressNOK,2,wxEXPAND)
		self.sizer_line5_right.Add(self.txt_nameNOK, 6,wxEXPAND)
		self.sizer_line5_right.AddSizer(self.sizer_gap_vertical)
		#----------------------------------------------------------------------------
		# Contact numbers are on their own separate vertical sizer as the photo sits
		# next to this
		#----------------------------------------------------------------------------
		self.sizer_contacts = wxBoxSizer(wxVERTICAL)
		self.sizer_line6_right.Add(self.lbl_homephone, 3,wxALIGN_CENTRE,0)
		self.sizer_line6_right.Add(self.txt_homephone, 5,wxEXPAND)
		self.sizer_line6_right.Add(0,0,1)
		self.sizer_contacts.Add(self.sizer_line6_right,0,wxEXPAND)
		self.sizer_line7_right.Add(self.lbl_workphone,3,wxALIGN_CENTRE,0)
		self.sizer_line7_right.Add(self.txt_workphone, 5,wxEXPAND)
		self.sizer_line7_right.Add(0,0,1)
		self.sizer_contacts.Add(self.sizer_line7_right,0,wxEXPAND)
		self.sizer_line8_right.Add(self.lbl_fax,3,wxALIGN_CENTRE,0)
		self.sizer_line8_right.Add(self.txt_fax, 5,wxEXPAND)
		self.sizer_line8_right.Add(0,0,1)
		self.sizer_contacts.Add(self.sizer_line8_right,0,wxEXPAND)
		self.sizer_line9_right.Add(self.lbl_email,3,wxALIGN_CENTRE,0)
		self.sizer_line9_right.Add(self.txt_email, 5,wxEXPAND)
		self.sizer_line9_right.Add(0,0,1)
		self.sizer_contacts.Add(self.sizer_line9_right,0,wxEXPAND)
		self.sizer_line10_right.Add(self.lbl_web,3,wxALIGN_CENTRE,0)
		self.sizer_line10_right.Add(self.txt_web, 5,wxEXPAND)
		self.sizer_line10_right.Add(0,0,1)
		self.sizer_contacts.Add(self.sizer_line10_right,0,wxEXPAND)
		self.sizer_line11_right.Add(self.lbl_mobile,3,wxALIGN_CENTRE,0)
		self.sizer_line11_right.Add(self.txt_mobile, 5,wxEXPAND)
		self.sizer_line11_right.Add(0,0,1)
		self.sizer_contacts.Add(self.sizer_line11_right,0,wxEXPAND)
		self.sizer_photo = wxBoxSizer(wxVERTICAL)
		self.patientpicture = gmGP_PatientPicture.cPatientPicture(self, -1)
		self.sizer_photo.Add(self.patientpicture,3,wxALIGN_CENTER_HORIZONTAL,0)
		self.sizer_photo.Add(self.btn_photo_aquire,1,wxALIGN_CENTER_HORIZONTAL,0)
		self.sizer_photo.Add(self.btn_photo_export,1,wxALIGN_CENTER_HORIZONTAL,0)
		self.sizer_photo.Add(self.btn_photo_import,1,wxALIGN_CENTER_HORIZONTAL,0)
		self.sizer_contactsandphoto  = wxBoxSizer(wxHORIZONTAL)
		self.sizer_contactsandphoto.AddSizer(self.sizer_contacts,6,wxALIGN_CENTER_VERTICAL,0)
		self.sizer_contactsandphoto.AddSizer(self.sizer_photo,2,wxALIGN_CENTER_VERTICAL,0)
		self.rightside = wxBoxSizer(wxVERTICAL)
		self.rightside.Add(self.sizer_line1_right,0,wxEXPAND|wxALL,1)
		self.rightside.Add(self.sizer_line2_right,0,wxEXPAND|wxALL,1)
		self.rightside.Add(self.sizer_line3_right,0,wxEXPAND|wxALL,1)
		self.rightside.Add(self.sizer_line4_right,0,wxEXPAND|wxALL,1)
		self.rightside.Add(self.sizer_line5_right,0,wxEXPAND|wxALL,1)
		self.rightside.Add(self.sizer_contactsandphoto,0,wxEXPAND|wxALL,1)
		self.mainsizer = wxBoxSizer(wxVERTICAL)
		self.topsizer = wxBoxSizer(wxHORIZONTAL)
		self.sizerunder = wxBoxSizer(wxHORIZONTAL)
		self.sizerunder.AddSizer(self.leftside,10,wxEXPAND|wxALL,5)
		self.sizerunder.Add(1,0,1)
		self.sizerunder.AddSizer(self.rightside,10,wxEXPAND|wxALL,5)
		self.mainsizer.Add(self.patientslist,3,wxEXPAND)
		self.mainsizer.Add(self.sizerunder,0,wxEXPAND|wxALL,10)

		sizer_control = wxBoxSizer(wxHORIZONTAL)
		b1 = wxButton( self, -1, _("SAVE"))
		b2 = wxButton( self, -1, _("CANCEL"))
		sizer_control.Add( b1, 0, wxEXPAND)
		sizer_control.Add( b2, 0, wxEXPAND)
		self.btn_save , self.btn_del = b1, b2
		self.mainsizer.Add(sizer_control)	
		
		self.SetSizer(self.mainsizer)
		self.SetAutoLayout(true)
		#self.Show(false)

		self.__create_input_field_map()

		self.__connect_commands()


	
	def __connect_commands(self):
		b = self.btn_add_address
		EVT_BUTTON(b, b.GetId() , self._add_address_pressed)
		b = self.btn_del_address
		EVT_BUTTON(b, b.GetId() ,  self._del_address_pressed)

		b = self.btn_save
		EVT_BUTTON(b, b.GetId(), self._save_btn_pressed)

		l = self.addresslist
		EVT_LISTBOX_DCLICK(l, l.GetId(), self._address_selected) 

	def __urb_selected(self, id):
		print id
		myPatient = self.get_demographic_record()
		self.input_fields['zip'].SetValue( myPatient.getPostcodeForUrbId(id )  )



	def _address_selected( self, event):
		self._update_address_fields_on_selection()

	def _update_address_fields_on_selection(self):	
		i = self.addresslist.GetSelection()
		atype,data = self.addr_cache.items()[i]
		m = self.input_fields
		m['address_type'].SetValue(atype)
		for k,v in data.items():
			try:
				m[k].SetValue(v)
			except:
				pass

	def _save_addresses(self):
		myPatient = self.get_demographic_record()
		for key, data in self.addr_cache.items():
			if data.has_key('dirty'):
				myPatient.linkNewAddress( key, data['no'], data['street'], data['suburb'], data['zip'] )	
				
	def _save_btn_pressed(self, event):
		self._save_data()

	def setNewPatient(self, isNew):
		self.newPatient = isNew

	def newPatient(self):
		self.setNewPatient(1)
		self.__init_data()
		import gmPatient
		id = gmPatient.create_dummy_identity()
		print "id = ", id
		self.patient = gmPatient.gmCurrentPatient(id)
		

	
	def __init_data(self):
		for k, w in self.input_fields.items():
			try:
				w.SetValue('')
			except:
				try:
					w.SetValue(0)
				except:
					print "no cleared value for ", w
					pass
		
		self.__update_address_types()

	def get_input_value_map(self):
		m = {}
		for k, v in self.input_fields.items():
			try:
				m[k] = v.GetValue()
			except:
				print sys.exc_info()[0]

		return m	


	def validate_fields(self):
		m = self.get_input_value_map()
		nameFields = [ m['firstname'].strip() , m['surname'].strip() ]
		if "" in nameFields or "?" in nameFields:
			raise Error("firstname and surname are required fields for identity")





	
	def _save_data(self):
		try:
			self.validate_fields()
		except:
			print sys.exc_info()[0]
			return	
	

		self._save_addresses()
	
		m = self.get_input_value_map()
			
		myPatient = self.get_demographic_record()

		myPatient.setActiveName(m['firstname'].strip(), m['surname'].strip())		
		myPatient.setGender( m['sex'] )
		myPatient.setDOB( m['birthdate'])
		myPatient.setTitle( m['title'])

		self.setNewPatient(0)
		gmDispatcher.send( gmSignals.patient_selected(), { 'id':  myPatient.getID() } )



	

	def _add_address_pressed(self, event):
		key, data = self._get_address_data()
		self._set_local_address(key, data)


	def _del_address_pressed(self, event):
		key, data = self._get_address_data()
		self._del_local_address(key)

	def _get_address_data(self):	
		m = self.input_fields
		data = {}
		for f in ['no', 'street', 'suburb', 'zip']:
		 	data[f] = m[f].GetValue()

		
		print "address data ", data	
		return m['address_type'].GetValue(), data
	
	def _set_local_address(self, key, data):
		if not self.__dict__.has_key('addr_cache'):
			self.addr_cache = {}
		
		self.addr_cache[key] = data
		data['dirty'] = 1	
		print "address cache = ", self.addr_cache

		self._update_address_list_display()

	
	def _del_local_address(self, key):
		try:
			del self.addr_cache[key]
		except:
			pass

		self._update_address_list_display()

	def _update_address_list_display(self):
		self.addresslist.Clear()
		for atype, data in self.addr_cache.items():
			s = '%-10s - %s,%s,%s,%s' % ( atype,  data['no'], data['street'], data['suburb'], data['zip'] )
			self.addresslist.Append(s)
		
		

		


	def __create_input_field_map(self):
		prefixes = [ 'txt_', 'cb_', 'combo_' ]
		map = {}
		for k,v in self.__dict__.items():
			for prefix in prefixes:
				if k[:len(prefix)] == prefix:
					#print k," is a widget"
					map[ k[len(prefix):] ] = v
		
		#print "INPUT MAP FOR ", self, " = " , map

		self.input_fields = map

	
	def __get_address_types(self):
		import gmDemographicRecord
		return gmDemographicRecord.getAddressTypes()

	def __update_address_types(self):
		m = self.input_fields
		m['address_type'].Clear()

		l = self.__get_address_types()

		for x in l:
			m['address_type'].Append(x)
			
	
	def __update_addresses(self):
		myPatient = self.get_demographic_record()
		self.orig_address = {}
		for x in myPatient.getAddressTypes():
			address = myPatient.getAddress(x)
			if address == None:
				continue
			self.orig_address[x] = self._store_to_input_addr(address[0])
			
		self.addr_cache = self.orig_address
		self._update_address_list_display()


	def __update_nok(self):
		myPatient = self.get_patient()
		l = myPatient.get_relative_list()
		l2 = []
		from gmDemographicRecord import get_time_tuple
		for m in l:
			s = """%-12s   - %s %s, %s, %s %s""" % (m['description'], m['firstnames'], m['lastnames'], m['gender'], _('born'), time.strftime('%d/%m/%Y', get_time_tuple(m['dob']) )  )
			l2.append( {'str':s, 'id':m['id'] } )
		
		f = self.input_fields
		f['nameNOK'].Clear()
		for data in l2:	
			f['nameNOK'].Append( data['str'], data['id'] )

	def _store_to_input_addr(self, address):
			map = {}
			map['no'] = address['number']
			map['street'] = address['street']
			map['suburb'] = address['urb']
			map['zip'] = address['postcode']
			map['id'] = address['ID']
			return map

	def _input_to_store_addr(self, input):
		m = self.input_fields
		map = { 'no': 'number', 'street': 'street', 'suburb': 'urb', 'zip': 'postcode' }
		data = {}
		for k,v in map:
			if input.has_key[k]:
				data[v] = input[k] 
		return data	
	
	def _updateUI(self):
		"""on patient_selected() signal handler , inherited from gmPatientHolder.PatientHolder"""
		myPatient = self.get_demographic_record()
		
		print self, "GOT THIS"
		print "ID       ", myPatient.getID ()
                print "name     ", myPatient.getActiveName ()
                print "title    ", myPatient.getTitle ()
                print "dob      ", myPatient.getDOB (aFormat = 'DD.MM.YYYY')
                print "med age  ", myPatient.getMedicalAge()
                adr_types = myPatient.getAddressTypes()
                print "adr types", adr_types
                for type_name in adr_types:
                        print "adr (%s)" % type_name, myPatient.getAddress (type_name)

		try:
			print "relations ", self.get_patient().get_relative_list()	
		except:
			gmLog.gmDefLog.LogException("relations ", sys.exc_info(), verbose= 1)
			pass
                print "--------------------------------------"

		m = self.input_fields

		m['firstname'].SetValue( myPatient.getActiveName()['first'] )
		m['surname'].SetValue( myPatient.getActiveName()['last'] )
		m['title'].SetValue( myPatient.getTitle() )
		m['birthdate'].SetValue(time.strftime('%d/%m/%Y', myPatient.getDOBTimeTuple() ) )
		m['sex'].SetValue( myPatient.getGender() )

		self.__update_address_types()

		self.__update_addresses()
		
		self._update_address_fields_on_selection()

		self.__update_nok()


	def OnPatient (self, event):
		pat_id = event.GetData ()
		index = event.GetIndex ()
		gmLog.gmDefLog.Log (gmLog.lInfo, "selected patient ID %s" % pat_id)
		pat_title = self.patientslist.GetItem (index, 0).GetText ()
		pat_fname = self.patientslist.GetItem (index, 1).GetText ()
		pat_lname = self.patientslist.GetItem (index, 2).GetText ()
		pat_dob = self.patientslist.GetItem (index, 3).GetText ()
		# load the demographic text controls
		# send a signal to other objects
		kwds = {'title':pat_title, 'firstnames':pat_fname, 'lastnames':pat_lname, 'dob':pat_dob, 'ID':pat_id}
		gmDispatcher.send (gmSignals.patient_selected (), sender='Terry Patient Selector', kwds=kwds )

	def FindPatient (self, name):
		self.patientslist.SetQueryStr (gmPatientNameQuery.MakeQuery (name), service='personalia')
		self.patientslist.RunQuery ()

#============================================================
class gmDemographics(gmPlugin.wxBasePlugin):
	"""A plugin for searching the patient database by name.

	Required the gmPatientWindowPlugin to be loaded.
	CANNOT BE UNLOADED
	"""
	def name (self):
		return 'Patient Search'
	#--------------------------------------------------------
	def register (self):
		# first, set up the widgets on the top line of the toolbar
		top_panel = self.gb['main.toolbar']

		# and register ourselves as a widget
		self.gb['modules.patient'][self.internal_name()] = self
		self.mwm = self.gb['clinical.manager']
		self.widget = PatientsPanel (self.mwm, self)
		self.mwm.RegisterWholeScreen(self.internal_name(), self.widget)
		self.set_widget_reference(self.widget)
		self.RegisterInterests ()
	#--------------------------------------------------------		
	def OnTool (self, event):
		pass
#		self.mwm.Display (self.internal_name ())
#		print "OnTool"
#		self.gb['modules.gui']['Patient'].Raise()

	def RegisterInterests(self):
		pass
#		gmDispatcher.connect(self.OnSelected, gmSignals.patient_selected())

	def OnSelected (self, **kwargs):
		pass
#		kwds = kwargs['kwds']
#		names = "%(title)s %(firstnames)s %(lastnames)s" % kwds
#		self.txt_findpatient.SetValue(names)
#		age = kwds['dob']
#		age = age.strip ()
		# FIXME:
#		try:
#			dmy = DateTime.strptime(age, "%d/%m/%y")
#		except:
#			dmy = DateTime.strptime(age, "%d/%m/%Y")
#		years = DateTime.Age(DateTime.now(), dmy).years
#		years = 20
#		self.txt_age.SetValue(str(years))

#----------------------------------------------------------------------
def getToolbar_FindPatientData():
   return cPickle.loads(zlib.decompress(
'x\xdam\x8e\xb1\n\xc4 \x0c\x86\xf7>\x85p\x83\x07\x01\xb9.\xa7\xb3\x16W\x87.]\
K\xc7+x\xef?]L\xa2\xb5r!D\xbe\x9f/\xc1\xe7\xf9\x9d\xa7U\xcfo\x85\x8dCO\xfb\
\xaaA\x1d\xca\x9f\xfb\xf1!RH\x8f\x17\x96u\xc4\xa9\xb0u6\x08\x9b\xc2\x8b[\xc2\
\xc2\x9c\x0bG\x17Cd\xde\n{\xe7\x83wr\xef*\x83\xc5\xe1\xa6Z_\xe1_3\xb7\xea\
\xc3\x94\xa4\x07\x13\x00h\xdcL\xc8\x90\x12\x8e\xd1\xa4\xeaM\xa0\x94\xf7\x9bI\
\x92\xa8\xf5\x9f$\x19\xd69\xc43rp\x08\xb3\xac\xe7!4\xf5\xed\xd7M}kx+\x0c\xcd\
\x0fE\x94aS' ))

def getToolbar_FindPatientBitmap():
    return wxBitmapFromXPMData(getToolbar_FindPatientData())

def getToolbar_FindPatientImage():
    return wxImageFromBitmap(getToolbar_FindPatientBitmap())

#----------------------------------------------------------------------

if __name__ == "__main__":
	import gmGuiBroker
	app = wxPyWidgetTester(size = (800, 600))
	app.SetWidget(PatientsPanel, -1)
	app.MainLoop()
#----------------------------------------------------------------------
# $Log: gmDemographics.py,v $
# Revision 1.1  2003-11-17 11:04:34  sjtan
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
