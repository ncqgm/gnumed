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
############################################################################
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/Attic/gmDemographics.py,v $
# $Id: gmDemographics.py,v 1.25 2004-06-13 22:31:48 ncq Exp $
__version__ = "$Revision: 1.25 $"
__author__ = "R.Terry, SJ Tan"

from Gnumed.wxpython import gmPlugin, gmGP_PatientPicture, gmPatientHolder
from Gnumed.pycommon import  gmGuiBroker, gmLog, gmDispatcher, gmSignals
from Gnumed.business import gmDemographicRecord, gmPatient

from mx import DateTime
from wxPython.wx import *

import cPickle, zlib, shutil, time
from string import *

from Gnumed.wxpython.gmPhraseWheel import cPhraseWheel
from Gnumed.business.gmDemographicRecord import MP_urb_by_zip , PostcodeMP, StreetMP, OccupationMP, CountryMP 

_log = gmLog.gmDefLog

if __name__ == '__main__':
	from Gnumed.pycommon import gmI18N

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
	def __init__ (self, parent, id): #, wxDefaultPosition, wxDefaultSize):
		wxTextCtrl.__init__(self,parent,id,"",wxDefaultPosition, wxDefaultSize,wxSIMPLE_BORDER)
		self.SetForegroundColour(wxColor(0,0,0))
		self.SetFont(wxFont(12,wxSWISS,wxNORMAL, wxBOLD,false,''))
#--------------------------------------------------------------------------------


class ExtIDPanel:
	def __init__ (self, parent, sizer, context = 'p'):
		self.combo_type = wxComboBox(parent, 500, "", wxDefaultPosition,wxDefaultSize, [], wxCB_READONLY)
		self.map = {}
		for code, name in gmDemographicRecord.getExtIDTypes (context):
			self.combo_type.Append (name, code)
			self.map[code] = name
		self.txt_ext_id = TextBox_BlackNormal (parent, -1)
		self.txt_comment = TextBox_BlackNormal (parent, -1)
		self.btn_add = wxButton (parent, -1, _("Add"))
		self.btn_del = wxButton (parent, -1, _("Del"))
		self.list = wxListBox (parent, -1, size=wxDefaultSize, style=wxLB_SINGLE)
		#self.list.InsertColumn (0, _("Type"))
		#self.list.InsertColumn (1, _("ID"))
		#self.list.InsertColumn (2, _("Comment"))
		
		sizer1 = wxBoxSizer (wxHORIZONTAL)
		sizer1.Add (self.combo_type, 2, wxEXPAND)
		sizer1.Add (self.txt_ext_id, 2, wxEXPAND)
		sizer1.Add (self.txt_comment, 2, wxEXPAND)
		sizer2 = wxBoxSizer (wxHORIZONTAL)
		sizer2.Add (self.btn_add, 2, wxEXPAND)
		sizer2.Add (self.btn_del, 2, wxEXPAND)
		sizer.Add (sizer1, 0, wxEXPAND|wxALL, 1)
		sizer.Add (sizer2, 0, wxEXPAND|wxALL, 1)
		sizer.Add (self.list, 1, wxEXPAND|wxALL, 1)

		self.demo = None

		EVT_BUTTON (self.btn_add, self.btn_add.GetId (), self.on_add)
		EVT_BUTTON (self.btn_del, self.btn_del.GetId (), self.on_del)

	def Clear (self):
		self.list.Clear ()
		self.txt_ext_id.SetValue ('')
		self.txt_comment.SetValue ('')
		self.combo_type.SetSelection (0)

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
		
#------------------------------------------------------------
class PatientsPanel(wxPanel, gmPatientHolder.PatientHolder):
	#def __init__(self, parent, plugin, id=wxNewId ()):
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
		self.gendermap = {'m':_('Male'), 'f':_("Female"), '?':_("Unknown"), 'tm':_('Trans. Male'), 'tf':_('Trans. Female'), 'h':_('Hermaphrodite')}
		self.comm_channel_names = gmDemographicRecord.getCommChannelTypes ()
		self.marital_status_types = gmDemographicRecord.getMaritalStatusTypes ()
		self.addresslist = wxListBox(self,ID_NAMESLIST,wxDefaultPosition,wxDefaultSize,[],wxLB_SINGLE)
		self.addresslist.SetFont(wxFont(12,wxSWISS, wxNORMAL, wxNORMAL, false, ''))
		self.addresslist.SetForegroundColour(wxColor(180,182,180))
		self.lbl_surname = BlueLabel(self,-1,"Surname")
		self.lbl_firstname = BlueLabel(self,-1,"Firstname")
		self.lbl_preferredname = BlueLabel(self,-1,"Salutation")
		self.lbl_title = BlueLabel(self,-1,"Title")
		self.lbl_sex = BlueLabel(self,-1,"Sex")
		self.lbl_street = BlueLabel(self,-1,"Street")
		self.lbl_urb = BlueLabel(self,-1,"Suburb")
		self.lbl_postcode = BlueLabel(self,-1,"Postcode")
		self.lbl_address_s = BlueLabel(self,-1,"Address")
		self.lbl_birthdate = BlueLabel(self,-1,"Birthdate")
		self.lbl_maritalstatus = BlueLabel(self,-1,"Marital Status")
		self.lbl_occupation = BlueLabel(self,-1,"Occupation")
		self.lbl_birthplace = BlueLabel(self,-1,"Born In")
		self.lbl_nextofkin = BlueLabel(self,-1,"")
		self.lbl_addressNOK = BlueLabel(self,-1,"Next of Kin")
		self.lbl_relationship = BlueLabel(self,-1,"Relationship")
		self.lbl_homephone = BlueLabel(self,-1,self.comm_channel_names[gmDemographicRecord.HOME_PHONE])
		self.lbl_workphone = BlueLabel(self,-1,self.comm_channel_names[gmDemographicRecord.WORK_PHONE])
		self.lbl_fax = BlueLabel(self,-1,self.comm_channel_names[gmDemographicRecord.FAX])
		self.lbl_email = BlueLabel(self,-1,self.comm_channel_names[gmDemographicRecord.EMAIL])
		self.lbl_web = BlueLabel(self,-1,self.comm_channel_names[gmDemographicRecord.WEB])
		self.lbl_mobile = BlueLabel(self,-1, self.comm_channel_names[gmDemographicRecord.MOBILE])
		self.lbl_line6gap = BlueLabel(self,-1,"")
		self.titlelist = ['Mr', 'Mrs', 'Miss', 'Mst', 'Ms', 'Dr', 'Prof']
          	self.combo_relationship = wxComboBox(self, 500, "", wxDefaultPosition,wxDefaultSize, ['Father','Mother'], wxCB_DROPDOWN)
		self.txt_surname = TextBox_RedBold(self,-1)
		self.combo_title = wxComboBox(self, 500, "", wxDefaultPosition,wxDefaultSize,self.titlelist, wxCB_DROPDOWN)
		self.txt_firstname = TextBox_RedBold(self,-1)
		self.combo_sex = wxComboBox(self, 500, "", wxDefaultPosition,wxDefaultSize, self.gendermap.values (), wxCB_DROPDOWN)
		self.cb_preferredname = wxCheckBox(self, -1, _("Preferred Name"), wxDefaultPosition,wxDefaultSize, wxNO_BORDER)
		self.txt_preferred = TextBox_RedBold(self,-1)
		#self.txt_address = wxTextCtrl(self, 30, "",
		#			      wxDefaultPosition,wxDefaultSize, style=wxTE_MULTILINE|wxNO_3D|wxSIMPLE_BORDER)
		#self.txt_address.SetInsertionPoint(0)
		#self.txt_address.SetFont(wxFont(12,wxSWISS, wxNORMAL, wxNORMAL, false, ''))
		
		self.txt_number= wxTextCtrl( self, 30, "")
		self.txt_number.SetFont(wxFont(12,wxSWISS, wxNORMAL, wxNORMAL, false, ''))
		self.txt_street = cPhraseWheel( parent = self,id = -1 , aMatchProvider= StreetMP(),  pos = wxDefaultPosition, size=wxDefaultSize )
		self.txt_street.SetFont(wxFont(12,wxSWISS, wxNORMAL, wxNORMAL, false, ''))

		self.txt_urb = cPhraseWheel( parent = self,id = -1 , aMatchProvider= MP_urb_by_zip(), selection_only = 1, pos = wxDefaultPosition, size=wxDefaultSize , id_callback= self.__urb_selected)

		self.txt_postcode  = cPhraseWheel( parent = self,id = -1 , aMatchProvider= PostcodeMP(), selection_only = 1,  pos = wxDefaultPosition, size=wxDefaultSize , id_callback =self.__postcode_selected)

		self.txt_birthdate = TextBox_BlackNormal(self,-1)
		self.combo_maritalstatus = wxComboBox(self, 500, "", wxDefaultPosition,wxDefaultSize,
						      self.marital_status_types, wxCB_DROPDOWN | wxCB_READONLY)
		self.txt_occupation = cPhraseWheel (parent=self, id = -1, aMatchProvider = OccupationMP (), pos = wxDefaultPosition, size=wxDefaultSize)
		self.txt_country = cPhraseWheel (parent=self, id = -1, aMatchProvider = CountryMP (), pos = wxDefaultPosition, size=wxDefaultSize)
		self.btn_browseNOK = wxButton(self,-1,"Browse NOK") #browse database to pick next of Kin
		self.lb_nameNOK = wxListBox( self, 30)
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
		#self.btn_photo_acquire = wxButton(self,-1,"Acquire")

		
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
		#c) residence or postal address
		#------------------------------
		sizer_respostal = wxBoxSizer(wxHORIZONTAL)
		sizer_respostal.Add(self.cb_addressresidence,1,wxEXPAND)
		sizer_respostal.Add(self.cb_addresspostal,1,wxEXPAND)

		self.sizer_line7_left = wxBoxSizer(wxHORIZONTAL)
		self.sizer_line7_left.Add(self.lbl_street,3,wxALIGN_CENTER_VERTICAL,5)
		self.sizer_line7_left.Add(self.txt_number,2,wxEXPAND)
		self.sizer_line7_left.Add(0,0,1)
		self.sizer_line7_left.Add(self.txt_street,4,wxEXPAND)
		self.sizer_line7_left.Add(sizer_respostal,6,wxEXPAND)
		#--------------------------
		# create the suburb details
		#--------------------------
		self.sizer_line8_left = wxBoxSizer(wxHORIZONTAL)
		self.sizer_line8_left.Add(self.lbl_urb,3,wxALIGN_CENTER_VERTICAL,5)
		self.sizer_line8_left.Add(self.txt_urb,7,wxEXPAND)
		self.sizer_line8_left.Add(0,0,1)
		self.sizer_line8_left.Add(self.lbl_postcode,3,wxALIGN_CENTER_VERTICAL,5)
		self.sizer_line8_left.Add(self.txt_postcode,3,wxEXPAND)

		#--------------------------
		# create address editing
		#-------------------------
		sizer_line8b_left = wxBoxSizer(wxHORIZONTAL)
		label_addr_type = BlueLabel( self, -1, _('address type') )
		self.combo_address_type = wxComboBox(self, -1, choices=gmDemographicRecord.getAddressTypes (), style=wxCB_READONLY)
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
		self.sizer_line3_right.Add(self.txt_country,6,wxEXPAND)
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
		self.sizer_line5_right.Add(self.lb_nameNOK, 6,wxEXPAND)
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
		#self.sizer_photo.Add(self.btn_photo_acquire,1,wxALIGN_CENTER_HORIZONTAL,0)
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
		self.ext_id_panel = ExtIDPanel (self, self.rightside)
		sizer_control = wxBoxSizer(wxHORIZONTAL)
		b1 = wxButton( self, -1, _("SAVE"))
		b2 = wxButton( self, -1, _("CANCEL"))
		b3 = wxButton( self, -1, _("NEW"))
		sizer_control.Add( b1, 0, wxEXPAND)
		sizer_control.Add( b2, 0, wxEXPAND)
		sizer_control.Add( b3, 0, wxEXPAND)
		self.btn_save = b1
		self.btn_del = b2
		self.btn_new = b3
		self.leftside.Add (1,0,1)
		self.leftside.Add(sizer_control)	

		self.mainsizer = wxBoxSizer(wxHORIZONTAL)
		self.mainsizer.AddSizer(self.leftside,10,wxEXPAND|wxALL,5)
		self.mainsizer.Add(1,0,1)
		self.mainsizer.AddSizer(self.rightside,10,wxEXPAND|wxALL,5)
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
		EVT_BUTTON(self.btn_del, self.btn_del.GetId (), self._del_button_pressed)
		EVT_BUTTON(self.btn_new, self.btn_new.GetId (), self._new_button_pressed)

		l = self.addresslist
		EVT_LISTBOX_DCLICK(l, l.GetId(), self._address_selected)

		EVT_BUTTON(self.btn_photo_import, self.btn_photo_import.GetId (), self._photo_import)
		EVT_BUTTON(self.btn_photo_export, self.btn_photo_export.GetId (), self._photo_export)

	def __urb_selected(self, id):
		gmDemographicRecord.setPostcodeWidgetFromUrbId( self.input_fields['postcode'], id)
		#	print "failed to set postcode widget from urb_id"



	def __postcode_selected(self, postcode):
		gmDemographicRecord.setUrbPhraseWheelFromPostcode( self.input_fields['urb'], postcode)

	def _address_selected( self, event):
		self._update_address_fields_on_selection()

	def _update_address_fields_on_selection(self):
		i = self.addresslist.GetSelection()
		data = self.addr_cache[i]
		m = self.input_fields
		m['address_type'].SetValue(data['type'])
		for k,v in data.items():
			if not k in ['dirty', 'type', 'ID']:
				m[k].SetValue(v)

	def _save_addresses(self):
		myPatient = self.patient.get_demographic_record()
		for data in self.addr_cache:
			if data.has_key('dirty'):
				myPatient.linkNewAddress( data['type'], data['number'], data['street'], data['urb'], data['postcode'] )
		for ID in self.to_delete:
			myPatient.unlinkAddress (ID)

	def _save_btn_pressed(self, event):
		try:
			self._save_data()
		except:
			_log.LogException ('failed on save data', sys.exc_info (), verbose=0)

	def _photo_import (self, event):
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
		try:
			dialogue = wxFileDialog (self, style=wxSAVE)
			if dialogue.ShowModal () == wxID_OK:
				shutil.copyfile (self.patientpicture.getPhoto (), dialogue.GetPath ())
		except:
			_log.LogException ('failed to export photo', sys.exc_info (), verbose= 0)

	def setNewPatient(self, isNew):
		self._newPatient = isNew

	def _new_button_pressed(self, event):
		self.setNewPatient(1)
		self.__init_data()
		id = gmPatient.create_dummy_identity()
		gmPatient.gmCurrentPatient(id)
	
	def __init_data(self):
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
		m = {}
		for k, v in self.input_fields.items():
			m[k] = v.GetValue()
		return m	

	def validate_fields(self):
		nameFields = [ self.value_map['firstname'].strip() , self.value_map['surname'].strip() ]
		if "" in nameFields or "?" in nameFields:
			raise Error("firstname and surname are required fields for identity")

	
	def _save_data(self):
		m = self.input_fields
		self.value_map = self.get_input_value_map ()
		self.validate_fields()
		self._save_addresses()
		myPatient = self.patient.get_demographic_record()
		if m['firstname'].IsModified () or m['surname'].IsModified ():
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
		# do we really want this?
		pass
	

	def _add_address_pressed(self, event):
		try:
			data = self._get_address_data()
			data['dirty'] = 1
			self.addr_cache.append (data)	
			self._update_address_list_display()
		except:
			_log.LogException ('failed on add address', sys.exc_info (), verbose=0)
			
	def _del_address_pressed(self, event):
		try:
			i = self.addresslist.GetSelection ()
			if self.addr_cache[i].has_key('ID'):
				self.to_delete.append (self.addr_cache[i]['ID'])
			del self.addr_cache[i]
			self._update_address_list_display()
		except:
			_log.LogException ('failed on delete address', sys.exc_info (), verbose=0)
		
	def _get_address_data(self):	
		m = self.input_fields
		data = {}
		for f in ['number', 'street', 'urb', 'postcode']:
		 	data[f] = m[f].GetValue()
		data['type'] = m['address_type'].GetValue ()
		return data

	def _update_address_list_display(self):
		self.addresslist.Clear()
		for data in self.addr_cache:
			s = '%-10s - %s,%s,%s' % ( data['type'],  data['number'], data['street'], data['urb'])
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
			
	
	def __update_addresses(self):
		myPatient = self.patient.get_demographic_record()
		try: 
			self.addr_cache = myPatient.getAddresses (None)
		except:
			_log.LogException ('failed to get addresses', sys.exc_info (), verbose=0)
		if self.addr_cache:
			self._update_address_list_display()
		else: # we have no addresses
			self.addresslist.Clear ()
		self.txt_number.Clear ()
		self.txt_street.Clear ()
		self.txt_postcode.Clear ()
		self.txt_urb.Clear ()
		self.combo_address_type.SetValue ('')
		
			

	def __update_nok(self):
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
		top_panel = self.gb['main.top_panel']

		# and register ourselves as a widget
		self.gb['modules.patient'][self.__class__.__name__] = self
		self.mwm = self.gb['clinical.manager']
		self.widget = PatientsPanel (self.mwm, self)
		self.mwm.RegisterWholeScreen(self.__class__.__name__, self.widget)
		self.RegisterInterests ()
	#--------------------------------------------------------		
	def OnTool (self, event):
		pass
#		self.mwm.Display (self.__class__.__name__)
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
# Revision 1.25  2004-06-13 22:31:48  ncq
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
