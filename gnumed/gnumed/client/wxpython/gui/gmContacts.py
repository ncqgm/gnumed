#############################################################################
# This panel is a contact manager to display and allow the
# use to add/delete/edit organisations,branches, persons
#
# If you don't like it - change this code
#
#	contains dummy data only
#	implemented for gui presentation only
##############################################################################
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gui/gmContacts.py,v $
__version__ = "$Revision: 1.48 $"
__author__ = "Dr. Richard Terry, \
			Sebastian Hilbert <Sebastian.Hilbert@gmx.net>"
__license__ = "GPL (details at http://www.gnu.org)"

from Gnumed.pycommon import gmLog, gmI18N

try:
	import wxversion
	import wx
except ImportError:
	from wxPython import wx

from Gnumed.wxpython import gmPlugin, images_contacts_toolbar16_16
from Gnumed.wxpython.gmPhraseWheel import cPhraseWheel
from Gnumed.business import gmDemographicRecord
from Gnumed.business.gmDemographicRecord import OrgCategoryMP
from Gnumed.business.gmOrganization import cOrgHelperImpl1,  cOrgHelperImpl2, cOrgHelperImpl3, cCatFinder, setPostcodeWidgetFromUrbId  

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

[
ID_ORGANISATIONSLIST,
ID_ALL_MENU,
ID_COMBOTYPE,
ID_SAVESQL,
ID_SEARCHGLOBAL,
ID_ORGANISATIONDISPLAY,
ID_GENERALPRACTICESDISPLAY,
ID_DOCTORSDISPLAY,
ID_PERSONSDISPLAY,
ID_ORGANISATIONADD,
ID_BRANCHDEPTADD,
ID_EMPLOYEEADD,
ID_PERSONADD,
ID_RELOAD,
ID_SEARCHSPECIFIC,
ID_SORTA_Z,
ID_SORTZ_A,
ID_SENDEMAIL,
ID_LINKINTERNET,
ID_INSTANTREPORT,
ID_REPORTS,
ID_SAVE,
ID_ORGPERSON_SELECTED

] = map(lambda _init_ctrls: wx.wx.NewId(), range(23))

divisionTypes = [_('Head Office'),_('Branch'),_('Department')]


#--------------------------------------------------
#Class which shows a blue bold label left justified
#--------------------------------------------------
class BlueLabel(wx.wxStaticText):
	def __init__(self, parent, id, prompt):
		wx.wxStaticText.__init__(self,parent, id,prompt, wx.wxDefaultPosition, wx.wxDefaultSize, wx.wxALIGN_LEFT)
		self.SetFont(wx.wxFont(12, wx.wxSWISS, wx.wx.NORMAL, wx.wx.BOLD,False,''))
		self.SetForegroundColour(wx.wxColour(0,0,131))

class DarkBlueHeading(wx.wxStaticText):
	def __init__(self, parent, id, prompt):
		wx.wxStaticText.__init__(self,parent, id,prompt, wx.wxDefaultPosition, wx.wxDefaultSize, wx.wxALIGN_CENTER)
		self.SetFont(wx.wxFont(
			pointSize = 12,
			family = wx.wxSWISS,
			style = wx.wx.NORMAL,
			weight = wx.wx.BOLD,
			underline = False
			)
		)
		self.SetForegroundColour(wx.wxColour(0,0,255))
#------------------------------------------------------------
#text control class to be later replaced by the gmPhraseWheel
#------------------------------------------------------------
class TextBox_RedBold(wx.wx.TextCtrl):
	def __init__ (self, parent, id): #, wx.wxDefaultPostion, wx.wxDefaultSize):
		wx.wx.TextCtrl.__init__(self,parent,id,"", wx.wxDefaultPosition, wx.wxDefaultSize, wx.wxSIMPLE_BORDER)
		self.SetForegroundColour(wx.wxColor(255,0,0))
		self.SetFont(wx.wxFont(12, wx.wxSWISS, wx.wx.NORMAL, wx.wx.BOLD,False,''))
class TextBox_BlackNormal(wx.wx.TextCtrl):
	def __init__ (self, parent, id): #, wx.wxDefaultPostion, wx.wxDefaultSize):
		wx.wx.TextCtrl.__init__(self,parent,id,"", wx.wxDefaultPosition, wx.wxDefaultSize, wx.wxSIMPLE_BORDER)
		self.SetForegroundColour(wx.wxColor(0,0,0))
		self.SetFont(wx.wxFont(12, wx.wxSWISS, wx.wx.NORMAL, wx.wx.BOLD,False,''))

class cContactsPanel(wx.wx.Panel):
	def __init__(self, parent,id):
		wx.wx.Panel.__init__(self, parent, id, wx.wxDefaultPosition, wx.wxDefaultSize, wx.wx.NO_BORDER| wx.wx.TAB_TRAVERSAL)
		#-----------------------------------------------------------------
		#create top list box which will show organisations, employees, etc
		#-----------------------------------------------------------------
		self.list_organisations = wx.wx.ListCtrl(self, ID_ORGANISATIONSLIST,  wx.wxDefaultPosition, wx.wxDefaultSize, wx.wx.LC_REPORT| wx.wx.LC_NO_HEADER| wx.wxSUNKEN_BORDER)
		self.list_organisations.SetForegroundColour(wx.wxColor(74,76,74))
		self.list_organisations.SetFont(wx.wxFont(10, wx.wxSWISS, wx.wx.NORMAL, wx.wx.NORMAL, False, ''))
		#----------------------------------------
		# add some dummy data to the allergy list
		self.list_organisations.InsertColumn(0,_( "Organisation"))
		self.list_organisations.InsertColumn(1,_( "Employees"))
		self.list_organisations.InsertColumn(2,_( "Address"))
		self.list_organisations.InsertColumn(3,_( "Category/Email"))
		self.list_organisations.InsertColumn(4,_( "Phone"))
	
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
		self.list_organisations.SetColumnWidth(0, wx.wx.LIST_AUTOSIZE)
		self.list_organisations.SetColumnWidth(1, wx.wx.LIST_AUTOSIZE)
		self.list_organisations.SetColumnWidth(2, wx.wx.LIST_AUTOSIZE)
		self.list_organisations.SetColumnWidth(3, wx.wx.LIST_AUTOSIZE)
		self.list_organisations.SetColumnWidth(4, wx.wx.LIST_AUTOSIZE)
	
		#--------------------
		#create static labels
		#--------------------
		self.lbl_heading = DarkBlueHeading(self,-1,_("Organisation"))
		self.lbl_org_name = BlueLabel(self,-1,_("Name"))
		self.lbl_Type = BlueLabel(self,-1,_("Office"))
		self.lbl_org_street = BlueLabel(self,-1,("Street"))
		self.lbl_org_suburb = BlueLabel(self,-1,_("Suburb"))
		self.lbl_org_state = BlueLabel(self,-1,_("State"))                   #eg NSW
		self.lbl_org_zip = wx.wxStaticText(self,id,_("Zip"), wx.wxDefaultPosition, wx.wxDefaultSize, wx.wxALIGN_CENTRE)
		self.lbl_org_zip.SetFont(wx.wxFont(12, wx.wxSWISS, wx.wx.NORMAL, wx.wx.BOLD,False,''))
		self.lbl_org_zip.SetForegroundColour(wx.wxColour(0,0,131))
		#self.lbl_org_zip = BlueLabel(self,-1,"Zip")
		self.lbl_org_category = BlueLabel(self,-1,_("Category"))
		#self.lbl_pers_occupation =  BlueLabel(self,-1,"Occupation")
		self.lbl_org_user1 = BlueLabel(self,-1,_("User1"))
		self.lbl_org_user2 = BlueLabel(self,-1,_("User2"))
		self.lbl_org_user3 = BlueLabel(self,-1,_("User3"))
		self.lbl_org_phone = BlueLabel(self,-1,_("Phone"))
		self.lbl_org_fax = BlueLabel(self,-1,_("Fax"))
		self.lbl_org_email = BlueLabel(self,-1,_("Email"))
		self.lbl_org_internet = BlueLabel(self,-1,_("Internet"))
		self.lbl_org_mobile = BlueLabel(self,-1,_("Mobile"))
		self.lbl_org_memo = BlueLabel(self,-1,_("Memo"))
	
		#--------------------
		#create the textboxes
		#--------------------
		self.txt_org_name = TextBox_RedBold(self,-1)
		self.txt_org_type = TextBox_RedBold(self,-1)       #head office, branch or department
		#self.txt_org_number = TextBox_RedBold(self, -1)
#		self.txt_org_street = cPhraseWheel( parent = self,id = -1 , aMatchProvider= StreetMP(),  pos = wx.wxDefaultPosition, size= wx.wxDefaultSize )
#		self.txt_org_street.SetFont(wx.wxFont(12, wx.wxSWISS, wx.wx.NORMAL, wx.wx.NORMAL, False, ''))
#		self.txt_org_suburb = cPhraseWheel( parent = self,id = -1 , aMatchProvider= MP_urb_by_zip(), selection_only = 1)
#		self.txt_org_suburb.add_callback_on_selection(self.__urb_selected)
#		self.txt_org_zip  = cPhraseWheel( parent = self,id = -1 , aMatchProvider= PostcodeMP(), selection_only = 1,  pos = wx.wxDefaultPosition, size= wx.wxDefaultSize)
		# FIXME: replace with set_callback_on_*
#		self.txt_org_zip.setDependent (self.txt_org_suburb, 'postcode')
	
		#self.txt_org_street = wx.wx.TextCtrl(self, 30,"", wx.wxDefaultPosition, wx.wxDefaultSize, style= wx.wx.TE_MULTILINE| wx.wx.NO_3D| wx.wxSIMPLE_BORDER)
	
		#self.txt_org_street.SetForegroundColour(wx.wxColor(255,0,0))
		#self.txt_org_street.SetFont(wx.wxFont(12, wx.wxSWISS, wx.wx.NORMAL, wx.wx.BOLD,False,''))
		#self.txt_org_suburb = TextBox_RedBold(self,-1)
		#self.txt_org_zip = TextBox_RedBold(self,-1)
		self.txt_org_state = TextBox_RedBold(self,-1) #for user defined fields later
		self.txt_org_user1 = TextBox_BlackNormal(self,-1)
		self.txt_org_user2 = TextBox_BlackNormal(self,-1)
		self.txt_org_user3 = TextBox_BlackNormal(self,-1)
#		self.txt_org_category = cPhraseWheel(parent = self, id = -1, aMatchProvider = OrgCategoryMP(), selection_only = 1, pos = wx.wxDefaultPosition, size= wx.wxDefaultSize)
		#self.txt_pers_occupation = TextBox_BlackNormal(self,-1)
		self.txt_org_phone = TextBox_BlackNormal(self,-1)
		self.txt_org_fax = TextBox_BlackNormal(self,-1)
		self.txt_org_mobile = TextBox_BlackNormal(self,-1)
		self.txt_org_email = TextBox_BlackNormal(self,-1)
		self.txt_org_internet = TextBox_BlackNormal(self,-1)
		self.txt_org_memo = wx.wx.TextCtrl(self, 30,
				"This company never pays its bills \n"
				"Insist on pre-payment before sending report",
				wx.wxDefaultPosition, wx.wxDefaultSize, style= wx.wx.TE_MULTILINE| wx.wx.NO_3D| wx.wxSIMPLE_BORDER)
		self.txt_org_memo.SetInsertionPoint(0)
		self.txt_org_memo.SetFont(wx.wxFont(12, wx.wxSWISS, wx.wx.NORMAL, wx.wx.NORMAL, False, ''))
		self.combo_type = wx.wxComboBox(self, ID_COMBOTYPE, "", wx.wxDefaultPosition, wx.wxDefaultSize,  divisionTypes , wx.wxCB_READONLY ) # wx.wxCB_DROPDOWN)
		self.combo_type.SetForegroundColour(wx.wxColor(255,0,0))
		self.combo_type.SetFont(wx.wxFont(12, wx.wxSWISS, wx.wx.NORMAL, wx.wx.BOLD,False,''))
		#----------------------
		#create the check boxes
		#----------------------
		self.chbx_postaladdress = wx.wxCheckBox(self, -1,_( " Postal Address "), wx.wxDefaultPosition, wx.wxDefaultSize, wx.wx.NO_BORDER)
	
		self.input_fields = {
			'name': self.txt_org_name,
			'office': self.txt_org_type,
			'category': self.txt_org_category,
			'subtype': self.combo_type,
			'street': self.txt_org_street,
			'urb': self.txt_org_suburb,
			'postcode' : self.txt_org_zip,
			'memo': self.txt_org_memo,
			'phone' : self.txt_org_phone,
			'fax' : self.txt_org_fax,
			'mobile': self.txt_org_mobile,
			'email': self.txt_org_email,
			'jabber': self.txt_org_internet }
		
	
		self._set_controller()	
	
		#-------------------------------------------
		#create the sizers for each line of controls
		#-------------------------------------------
		self.sizer_line0 = wx.wx.BoxSizer(wx.wx.HORIZONTAL)
		self.sizer_line1 = wx.wx.BoxSizer(wx.wx.HORIZONTAL)
		self.sizer_line1a = wx.wx.BoxSizer(wx.wx.HORIZONTAL)
		self.sizer_line2 = wx.wx.BoxSizer(wx.wx.HORIZONTAL)
		self.sizer_line3 = wx.wx.BoxSizer(wx.wx.HORIZONTAL)
		self.sizer_line4 = wx.wx.BoxSizer(wx.wx.HORIZONTAL)
		self.sizer_line5 = wx.wx.BoxSizer(wx.wx.HORIZONTAL)
		self.sizer_line6 = wx.wx.BoxSizer(wx.wx.HORIZONTAL)
		self.sizer_line7 = wx.wx.BoxSizer(wx.wx.HORIZONTAL)
		self.sizer_line8 = wx.wx.BoxSizer(wx.wx.HORIZONTAL)
		self.sizer_line9 = wx.wx.BoxSizer(wx.wx.HORIZONTAL)
		self.sizer_line10 = wx.wx.BoxSizer(wx.wx.HORIZONTAL)
		self.sizer_line11 = wx.wx.BoxSizer(wx.wx.HORIZONTAL)
		self.sizer_line0.Add((0,10),1)
		#--------------------------------------
		#Heading at top of the left hand column
		#--------------------------------------
		if wx.wxPlatform == '__WXMAC__':
			self.sizer_line0.Add((0,0),4)
		else:	
			self.sizer_line0.Add(0,0,4)
		
		self.sizer_line0.Add(self.lbl_heading,40, wx.wxEXPAND| wx.wxALIGN_CENTER)
		
		if wx.wxPlatform == '__WXMAC__':
			self.sizer_line0.Add((0,0),48)
		else:
			self.sizer_line0.Add(0,0,48)
		#---------------------------------------------
		#line one:surname, organisation name, category
		#---------------------------------------------
		self.sizer_line1.Add(self.lbl_org_name,4, wx.wxALIGN_CENTER_VERTICAL,5)
		self.sizer_line1.Add(self.txt_org_name,40, wx.wxEXPAND)
		self.sizer_line1.Add(0,0,4)
		self.sizer_line1.Add(self.lbl_org_category,8, wx.wxALIGN_CENTER_VERTICAL, 5)
		self.sizer_line1.Add(self.txt_org_category,36, wx.wxEXPAND)
		#--------------------------------------------------------------
		#line onea:type of organisation:headoffice,branch of department
		#--------------------------------------------------------------
	
		#self.sizer_line1a.Add(0,0,4)
		self.sizer_line1a.Add(self.lbl_Type,4, wx.wxALIGN_LEFT,5)
		self.sizer_line1a.Add(self.combo_type,20, wx.wxEXPAND)
		self.sizer_line1a.Add(self.txt_org_type,20, wx.wxEXPAND)
		if wx.wxPlatform == '__WXMAC__':
			self.sizer_line1a.Add((0,0),4)
		else:
			self.sizer_line1a.Add(0,0,4)
		if DISPLAYPERSON == 1:
			self.sizer_line1a.Add(self.lbl_pers_occupation,8, wx.wxALIGN_CENTER_VERTICAL, 5)
			self.sizer_line1a.Add(self.txt_pers_occupation,36, wx.wxEXPAND)
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
		self.sizer_line2_rightside = wx.wx.BoxSizer(wx.wx.VERTICAL)
		self.sizer_line2_forphone = wx.wx.BoxSizer(wx.wx.HORIZONTAL)
		self.sizer_line2_forphone.Add(self.lbl_org_phone,8, wx.wxGROW, wx.wxALIGN_CENTER_VERTICAL,5)
		self.sizer_line2_forphone.Add(self.txt_org_phone,36, wx.wxEXPAND)
		self.sizer_line2_forfax = wx.wx.BoxSizer(wx.wx.HORIZONTAL)
		self.sizer_line2_forfax.Add(self.lbl_org_fax,8, wx.wxGROW, wx.wxALIGN_CENTER_VERTICAL,5)
		self.sizer_line2_forfax.Add(self.txt_org_fax,36, wx.wxEXPAND)
		self.sizer_line2_rightside.AddSizer(self.sizer_line2_forphone,2, wx.wxEXPAND)
		self.sizer_line2_rightside.AddSizer(self.sizer_line2_forfax,2, wx.wxEXPAND)
		self.sizer_line2.Add(self.lbl_org_street,4, wx.wxGROW| wx.wxALIGN_CENTER_VERTICAL,5)
		self.sizer_line2.Add(self.txt_org_street,40, wx.wxEXPAND)
		if wx.wxPlatform == '__WXMAC__':
			self.sizer_line2.Add((0,0),4)
		else:
			self.sizer_line2.Add(0,0,4)
		self.sizer_line2.AddSizer(self.sizer_line2_rightside,44, wx.wxEXPAND)
		#----------------------------------------------------
		#line three:suburb, state, zip code, organisation fax
		#----------------------------------------------------
		self.sizer_line3.Add(self.lbl_org_suburb,4, wx.wxEXPAND| wx.wxALIGN_CENTER_VERTICAL)
		self.sizer_line3.Add(self.txt_org_suburb,40, wx.wxEXPAND)
		if wx.wxPlatform == '__WXMAC__':
			self.sizer_line3.Add((0,0),4)
		else:
			self.sizer_line3.Add(0,0,4)
		self.sizer_line3.Add(self.lbl_org_email,8, wx.wxGROW| wx.wxALIGN_CENTER_VERTICAL)
		self.sizer_line3.Add(self.txt_org_email,36, wx.wxEXPAND)
		#-----------------------------------------------
		#line four: head office checkbox, email text box
		#-----------------------------------------------
		self.sizer_line4.Add(self.lbl_org_state,4, wx.wxEXPAND| wx.wxALIGN_CENTER)
		self.sizer_line4.Add(self.txt_org_state,20, wx.wxEXPAND)
		self.sizer_line4.Add(self.lbl_org_zip,10, wx.wxGROW| wx.wx.TOP,5)
		self.sizer_line4.Add(self.txt_org_zip,10, wx.wxEXPAND)
		if wx.wxPlatform == '__WXMAC__':
			self.sizer_line4.Add((0,0),4)
		else:
			self.sizer_line4.Add(0,0,4)
		self.sizer_line4.Add(self.lbl_org_internet,8, wx.wxGROW| wx.wxALIGN_CENTER_VERTICAL,5)
		self.sizer_line4.Add(self.txt_org_internet,36, wx.wxEXPAND)
		#-----------------------------------------------
		#line five: postal address checkbox, internet
		#-----------------------------------------------
		if wx.wxPlatform == '__WXMAC__':
			self.sizer_line5.Add((0,0),4)
		else:
			self.sizer_line5.Add(0,0,4)
		self.sizer_line5.Add(self.chbx_postaladdress,40, wx.wxEXPAND)
		if wx.wxPlatform == '__WXMAC__':
			self.sizer_line5.Add((0,0),4)
		else:
			self.sizer_line5.Add(0,0,4)
		self.sizer_line5.Add(self.lbl_org_mobile,8, wx.wxGROW| wx.wxALIGN_CENTER_VERTICAL,5)
		self.sizer_line5.Add(self.txt_org_mobile,36, wx.wxEXPAND)
		#-----------------------------------------------
		#line six: checkbox branch mobile phone number
		#-----------------------------------------------
		if wx.wxPlatform == '__WXMAC__':
			self.sizer_line6.Add((0,20),96)
		else:
			self.sizer_line6.Add(0,20,96)
		#-----------------------------------------------
		#line seven: user1
		#-----------------------------------------------
		self.sizer_line7_user1 = wx.wx.BoxSizer(wx.wx.HORIZONTAL)
		self.sizer_line7_user1.Add(self.lbl_org_user1,4, wx.wxGROW| wx.wxALIGN_CENTER_VERTICAL,5)
		self.sizer_line7_user1.Add(self.txt_org_user1,18, wx.wxEXPAND)
		self.sizer_line7_user2 = wx.wx.BoxSizer(wx.wx.HORIZONTAL)
		self.sizer_line7_user2.Add(self.lbl_org_user2,4, wx.wxGROW| wx.wxALIGN_CENTER_VERTICAL,5)
		self.sizer_line7_user2.Add(self.txt_org_user2,18, wx.wxEXPAND)
		self.sizer_line7_user3 = wx.wx.BoxSizer(wx.wx.HORIZONTAL)
		self.sizer_line7_user3.Add(self.lbl_org_user3,4, wx.wxGROW| wx.wxALIGN_CENTER_VERTICAL,5)
		self.sizer_line7_user3.Add(self.txt_org_user3,18, wx.wxEXPAND)
		self.sizer_line7_right = wx.wx.BoxSizer(wx.wx.VERTICAL)
		self.sizer_line7_right.AddSizer(self.sizer_line7_user1,0, wx.wxEXPAND)
		self.sizer_line7_right.AddSizer(self.sizer_line7_user2,0, wx.wxEXPAND)
		self.sizer_line7_right.AddSizer(self.sizer_line7_user3,0, wx.wxEXPAND)
	
	
		self.sizer_line7.Add(self.lbl_org_memo,4, wx.wxEXPAND| wx.wxALIGN_CENTER_VERTICAL,5)
		self.sizer_line7.Add(self.txt_org_memo,40, wx.wxEXPAND)
		if wx.wxPlatform == '__WXMAC__':
			self.sizer_line7.Add((0,0),4)
		else:
			self.sizer_line7.Add(0,0,4)
		self.sizer_line7.AddSizer(self.sizer_line7_right,44, wx.wxEXPAND)
		self.nextsizer=  wx.wx.BoxSizer(wx.wx.VERTICAL)
		self.nextsizer.Add(self.list_organisations,3, wx.wxEXPAND)
		if wx.wxPlatform == '__WXMAC__':
			self.nextsizer.Add((0,10),0)
		else:
			self.nextsizer.Add(0,10,0)
		self.nextsizer.Add(self.sizer_line0,0, wx.wxEXPAND)
		self.nextsizer.Add(self.sizer_line1,0, wx.wxEXPAND)
		self.nextsizer.Add(self.sizer_line1a,0, wx.wxEXPAND)
		self.nextsizer.Add(self.sizer_line2,0, wx.wxEXPAND)
		self.nextsizer.Add(self.sizer_line3,0, wx.wxEXPAND)
		self.nextsizer.Add(self.sizer_line4,0, wx.wxEXPAND)
		self.nextsizer.Add(self.sizer_line5,0, wx.wxEXPAND)
		self.nextsizer.Add(self.sizer_line6,0, wx.wxEXPAND)
		self.nextsizer.Add(self.sizer_line7,0, wx.wxEXPAND)
		self.mainsizer = wx.wx.BoxSizer(wx.wx.VERTICAL)
		self.mainsizer.AddSizer(self.nextsizer,1, wx.wxEXPAND| wx.wxALL,10)
		self.SetSizer(self.mainsizer)
		self.mainsizer.Fit
		self.SetAutoLayout(True)
		self.Show(True)

	def _set_controller(self, helper = cOrgHelperImpl3() ):
		"""Initialises the controller for this widget.
		_helper is the orgHelper() that creates org instances, and finds many orgs.
		_current is the current org being edited, or the parent of the current person.
		_currentPerson is the current person being edited, or None.
		_isPersonIndex is used by the list control selection handler to determine
		if a row selected returns the id of a org, or an id of a person. Since
		org and person are stored on different tables, the id itself cannot distinguish the item, and list data only stores an integer . Therefore the row position in the 
		list control maps to a person if it is a key in _isPersonIndex, and 
		the mapped object  is a OrgDemographicAdapter instance , which is 
		a cDemographicRecord wrapped in cOrg clothing, the intention being
		to minimize re-write of gmContact's controller code.
		self._tmpPerson maps the persons found in _isPersonIndex, so that
		the person objects can be re-used when list_all_orgs is called, and
		substituted for persons followed from org.getPersonMap() ,
		for each org retrieved by _helper.findAllOrganizations().
		( orgHelperImpl2 will return orgs in parent/child order).
		( orgHelperImpl3 extends orgHelperImpl2 to provides creation of 
		person OrgDemographicAdapter,
		and type testing a cOrg to see if it is a cPerson ).
		
		"""

		self._connect_list()
		self._helper = helper 
		self._current = None

		self._isPersonIndex = {}
		self._tmpPerson = {}
		self._currentPerson = None
		self._cutPerson = None

		self._connectCutPaste()
		
		self._lastSelected = None # for internal cut and paste

		self._lastItemIndex = 0
		
		self._connectDrag()
		

	def getLastSelected(self):
		return self._lastSelected

	def setLastSelected(self, obj):
		self._lastSelected = obj


	def _connectDrag(self):
		wx.wx.EVT_LIST_BEGIN_DRAG(self.list_organisations, self.list_organisations.GetId(), self._doDrag)
	
	def _doDrag(self, event):
		dragSource = wx.wxDropSource(self)
		text = self._getClipDragTextDataObject()
		if text:
			dragSource.SetData(text)
			
			result = dragSource.DoDragDrop(True)
			if result == wx.wxDragCopy: print "drag copy action"
			elif result == wx.wxDragMove: print "drag move action"
		

	def _connectCutPaste(self):
		wx.wx.EVT_KEY_DOWN(self.list_organisations, self._checkForCutPaste)

	def _checkForCutPaste(self, keyEvent):
		#print "control down is ", keyEvent.ControlDown()
		#print "keyCode is ", keyEvent.GetKeyCode()
		c = keyEvent.GetKeyCode()
		if keyEvent.ControlDown():
			print c
			if c == 88 : # ascii('x')
				print "cut"
				self._cutPerson = self.getLastSelected()
				self._doCopyToClipboard() # experiment with wx.wxClipboard
			elif c == 86: # ascii('v')
				print "paste"
				self.doPaste()
		keyEvent.Skip()
		
	def doPaste(self):			
		if self.getCurrent() <> None and self._cutPerson <> None:
			p = self._cutPerson
			o = p.getParent()
			o.unlinkPerson(p.getDemographicRecord() )
			self.getCurrent().linkPerson(p.getDemographicRecord())
			p.setParent(self.getCurrent())

			self.load_all_orgs()

			self._cutPerson = None
			self.setLastSelected(None)


	def _doCopyToClipboard(self):
		
		board = wx.wx.TheClipboard
		if not board.Open():
			print "unable to get ownership of clipboard yet."
			return False
		text = self._getClipDragTextDataObject()
		if text:
			board.SetData(text )
		board.Close()

	def _getClipDragTextDataObject(self):	
		p = self.getLastSelected()
		if p is None:
			p = self.getCurrent()
			if p is None:
				#<DEBUG>
				print "No current org or person to copy to clipboard"
				#</DEBUG>
				return None		
		return wx.wx.TextDataObject( p.getHelper().getClipboardText(p) )

	def _connect_list(self):
		"""allow list selection to update the org edit area"""
		wx.wx.EVT_LIST_ITEM_SELECTED(self.list_organisations, self.list_organisations.GetId(), self._orgperson_selected)

	def __urb_selected(self, id):
		self.input_field['postcode'].SetValue (gmOrganization.getPostcodeForUrbId(id))
		self.input_field['postcode'].input_was_selected= 1

	def get_address_values(self):
		"""from the street urb, postcode field, return number, street, urb, postcode list"""
		f = self.input_fields
		vals = [ f[n].GetValue() for n in ['street', 'urb', 'postcode'] ]
		# split the street value into 2 parts, number and street. ? Have a separate number field instead.
		addr = [ vals[0].split(' ')[0] , ' '.join( vals[0].split(' ')[1:] ) ] + vals[1:] + [None,None]
		# [None, None] is state and country at the moment
		return addr 
	
	def get_org_values(self):
		"""returns a dictionary of the widget controls contents"""
		f = self.input_fields
		
		m =dict(  [ (n,f[n].GetValue()) for n in ['name','office', 'subtype', 'memo', 'category', 'phone', 'fax', 'email', 'mobile'] ] )
		return m 

	
	def add_org(self, org, showPersons = True):
		"""display an org in the list control, and show any dependent persons if
		necessary."""
		key, data = self.getOrgKeyData(org)
		if key is None:
			return
		x = self.list_organisations.GetItemCount()
		self._insert_org_data( x, key, data)
		
		if showPersons:
			m = org.getPersonMap(reload=False)
			# create _isPersonIndex, which maps a row index to
			# a tuple of a person and a person's parent org.
			# 
			for id, demRecord in m.items():
				if self._tmpPerson.has_key(demRecord.getID()):
					person = self._tmpPerson[demRecord.getID()]
				else:  
					person = self._helper.createOrgPerson()
					person.setDemographicRecord(demRecord)
				
				key, data = self.getOrgKeyData(person)
				ix = self.list_organisations.GetItemCount()
				self._insert_org_data(ix, key, data)
				person.setParent(org)
				self._isPersonIndex[ix] = person

			
			


	def update_org(self, org):
		"""displays an org without reloading it. It is added to the end of a display list, currently, without attention to it's position in a contact tree. Use load_all_orgs()
		is preferable, as it uses org's cached in the orgHelper, and person's cached
		in self._tmpPerson.
		"""
			
		key, data = self.getOrgKeyData(org)
		if key is None:
			return
	
		l = self.list_organisations
		max = l.GetItemCount()
	
		for n in xrange( 0, max):
			isPerson = self._helper.isPerson(org) 
			if l.GetItemData(n) == key and (
			(not isPerson and not self._isPersonIndex.has_key(n) )
				or (isPerson and self._isPersonIndex.has_key(n) )  ):
				break

		if n == max:
			self._insert_org_data(n, key, data)
		else:
			self._update_org_data(n, key, data)
	
	
	def getOrgKeyData(self, org):
		"""Converts org to data items for displaying in list control.
		Rules are specific , and defined in original example gmContacts data
		"""	
		try:     
			key = int(org.getId())
		except:
			print "org has no key. ? Failure in saving org ? non-existent org category"
			print "if testing, try insert org_category(description) values('hospital')"
			print "in a admin psql session, substitute 'hospital' for whatever category"
	
			gmLog.gmDefLog.LogException("failed to save org %s with id %s" %(org['name'], str(org.getId()) ) , sys.exc_info() )
			return None, None 
	
	
		o = org.get()
	
		
		phone_fax = '/fax '.join([ o.get('phone', '') , o.get('fax', '')]  )
		address_str = org.getHelper().getAddressStr(org)
	
		# display for person
		if org.getHelper().isPerson(org):
			return key, ["", "- " + o['name'], o['subtype'], o.get('email',''), phone_fax]
		
		# display for top level org
		elif org.getParent() is None:
			return key, [o['name'], '', address_str,  o['category'], phone_fax]
	
		# display  branch, department , division
		return key, ["", ' '.join([o.get('name',''), o.get('subtype','')]),address_str, o.get('email',''), phone_fax]
				
	
	
	def _insert_org_data(self, n, key, data): 	  
		self.list_organisations.InsertStringItem(n, data[0])
		self.list_organisations.SetStringItem(n, 1, data[1])
		self.list_organisations.SetStringItem(n, 2, data[2])
		self.list_organisations.SetStringItem(n, 3, data[3])
		self.list_organisations.SetStringItem(n, 4, data[4])
		self.list_organisations.SetItemData(n, key)
	
	
	def _update_org_data( self, n, key, data):
		l = self.list_organisations
		for i in xrange(0, 4):
			l.SetStringItem(i, data[i])
		l.SetItemData(n, key)
	

	def load_all_orgs(self):
		"""clears the list control, displays the example data, and then 
		the real data, from _helper.findAllOrganizations() """
		#pos = self.list_organisations.GetScrollPos(wx.wx.VERTICAL)
		self.list_organisations.DeleteAllItems()
		#self._insert_example_data()   , removing this as it is confusing
		if self._isPersonIndex <> {}:
			self._tmpPerson = {}
			for person  in self._isPersonIndex.values():
				self._tmpPerson[person.getId()] = person
			self._isPersonIndex = {}
		
		orgs = self.getOrgHelper().findAllOrganizations()
		for org in orgs:
			self.add_org(org)
			
		#self.list_organisations.SetScrollPos(wx.wx.VERTICAL, pos)
		#self.list_organisations.Refresh()
		self._ensureCurrentVisible()
	
	def _ensureCurrentVisible(self):
		l = self.list_organisations
		person = self._currentPerson or self._cutPerson
		print "person ", person, "self._cutPerson", self._cutPerson
	
		if person:
			key = person.getId()
			for i, p in self._isPersonIndex.items():
				if p.getId() == person.getId():
					break
		elif self.getCurrent() is None:
				return
		else:
			
			c = l.GetItemCount()
			key = self.getCurrent().getId()
			i , nexti = 0, -1
			while  nexti <> i and (i < l.GetItemCount()  or self._isPersonIndex.has_key(i)):
				i = nexti
				nexti = l.FindItemData(i, key)
				
				#print i
	
		for j in xrange(0, 2):	  
			if i + 1 < l.GetItemCount():
				i += 1
	
		l.EnsureVisible(i)
		
	def _insert_example_data(self):
		items = organisationsdata.items()
		for i in xrange(0,len(items)):
			key, data = items[i]
			self._insert_org_data(i, key, data)

	def _orgperson_selected(self, event):
		"""handle list control selection event, passing to _person_selected(row index)
		if it is a person displayed at the row index, or using self._helper.getFromCache
		to retrieve the previously cached org by the key stored in the list item data."""
	
		ix = event.GetIndex()
		key = self.list_organisations.GetItemData(ix)
	
		self.setLastSelected(None)  # clear the last selected person.
		
		if self._isPersonIndex.has_key(ix):
			self._person_selected( self._isPersonIndex[ix])
			return
		else:
			self._currentPerson = None
		
		org = self._helper.getFromCache(key)
		self.clearForm()
		if org == None:
			"""this block is mainly used to parse the example data.
			It is probably not needed, in usage , as all data from the
			database will be in the helper cache.
			"""
			org = self._helper.create()
			data = [ self.list_organisations.GetItem(ix,n).GetText() for n in xrange(0,5) ]
			
			org['name'] = data[0].strip()
			org['subtype'] = data[1].strip()
			j = 1
			while org['name'] == '' and j <= ix:
				org['name'] = self.list_organisations.GetItem(ix-j, 0).GetText().strip()
				j += 1
	
			if org['subtype'] <> '':
				org.setParent( org.getHelper().findOrgsByName(org['name'])[0] )
			
			#TODO remove this test filter
			if  data[3].lower().find('hospital') >= 0:  data[3] = 'hospital'
	
			org['category'] = data[3]
			
			org['phone'] = data[4]
		
			try:
	
				l = data[2].split(' ')
				
				# if no numerals in first token assume no address number
				if l[0].isalpha():
					l = [''] + l
				# if no numerals in last token asssume no postcode 	
				if l[-1].isalpha():
					l.append('')
				
				urb_start_idx = -2
			
				# scan back , UPPERCASE words assumed to be part of suburb name
				while urb_start_idx > -len(l) and l[urb_start_idx-1].isupper():
					urb_start_idx -= 1
				if len (l) >= 4:
					number , street, urb, postcode = l[0], ' '.join(l[1:urb_start_idx]), ' '.join(l[urb_start_idx:-1]), l[-1]
					org.setAddress( number, street, urb, postcode, None, None )
			except:
				gmLog.gmDefLog.LogException("Unable to parse address", sys.exc_info() )
				print "unable to parse address"
				
		self.setCurrent(org)
		self.checkEnabledFields()
		self.loadCurrentValues(org)	

	def loadCurrentValues(self, org):
		"""parse an org into the edit widgets of gmContact"""
		f = self.input_fields
		for n in ['name','subtype', 'category', 'phone', 'email', 'fax', 'mobile']:
			v = org[n]
			if v == None: v = ''
			f[n].SetValue(v.strip())
	
		a = org.getAddress()
		s = a.get('number','').strip() + ' ' + a.get('street','').strip()
		f['street'] .SetValue(s.strip())
		f['urb'] .SetValue(a.get('urb','').strip() )
		f['postcode'] .SetValue( str(a.get('postcode','')).strip())
	


	def setCurrent(self, org):
		self._current = org
	

	def getCurrent(self):
		return self._current

	def getOrgHelper(self):
		return  self._helper

	def newOrg(self, parent = None):
		self._currentPerson = None
		self.setCurrent(self._helper.create())
		self.getCurrent().setParent(parent)
		self.newForm()

	def newForm(self):
		self.clearForm()
		self.checkEnabledFields()

	def clearForm(self):
		for k,f in self.input_fields.items():
			f.SetValue('')

	def checkEnabledFields(self):
		"""configure the edit widgets according to the type of org/person object"""
		if not self._currentPerson is None:
			self.lbl_Type.SetLabel(_('occupation'))
			self._loadOccupations()
			parent = self.getCurrent()
			self.input_fields['name'].SetToolTip(wx.wx.ToolTip(_("'Title. first LAST-IN-CAPITAL',   or \n'Title. Last, first' \n- the dot is required to separate title; comma indicates the order of the names is last names, first names.")) )
		else:
			self.lbl_Type.SetLabel(_('subdivision'))
			self._loadDivisionTypes()
			parent = self.getCurrent().getParent()
			self.input_fields['name'].SetToolTip(wx.wx.ToolTip(_("The organization's name.") ) )
		
	
		dependent = not parent is None
		if dependent:
			self.input_fields['category'].SetValue(parent['category'])
		self.input_fields['category'].Enable(not dependent)
	
	def _loadOccupations(self):
		f = self.input_fields['subtype']
		f.Clear()
		cats = cCatFinder('occupation', 'id','name').getCategories('occupation')
		for x in cats:
			f.Append(x)
		
	def _loadDivisionTypes(self):
		f = self.input_fields['subtype']
		f.Clear()
		for n in divisionTypes:
			f.Append(n)
	

	def saveOrg(self):
		"""transfer the widget's edit controls to a org/person object, and
		call its save() function, then reload all the orgs, and their persons, from the cache.
		The save() function will update the cache if this is  a newly created
		org/person."""
		
		if  not self._currentPerson is None:
			org = self._currentPerson
			org.setParent(self.getCurrent()) # work out how to reference parents
							# within org cache
		else:	
			org= self.getCurrent()

		if org is None:
			"""this block is unlikely, but there must be an org to work on."""
			org = self.getOrgHelper().create()
			self.setCurrent(org)
		
			
		o = self.get_org_values()
		a = self.get_address_values()
		org.set(*[],**o)
		#<DEBUG>
		print "setting address with ", a
		#</DEBUG>
		org.setAddress(*a)
		
		isNew = org.getId() is None
		org.save()
		self.load_all_orgs()

		#if isNew:
		#	self.add_org(org)
		#else:
		#		self.update_org(org) # refresh after saving

			

	def isPersonCurrent(self):
		return not self._currentPerson is None

	def newPerson(self):
		if self.getCurrent() is None or self.getCurrent().getId() is None:
			print "Org must exist to add a person"
			return False
		self._currentPerson =  self.getOrgHelper().createOrgPerson()
		self._currentPerson.setParent(self.getCurrent() )
		self.newForm()
		return True

	def _person_selected(self, person):
		"""set the widget's state for person editing"""
		self.clearForm()
		self.setCurrent(person.getParent() )
		self._currentPerson = person 
		self.checkEnabledFields()
		self.loadCurrentValues(person)		
		
		self.setLastSelected(person)


			
class gmContacts (gmPlugin.cNotebookPluginOld):
	tab_name = _("Contacts")

	def name (self):
		return gmContacts.tab_name

	def GetWidget (self, parent):
		self._last_widget = cContactsPanel (parent, -1)
		return self._last_widget

	def MenuInfo (self):
		return ('view', _('&Contacts'))

	def populate_toolbar (self, tb, widget):
		tool1 = tb.AddTool(ID_SEARCHGLOBAL, images_contacts_toolbar16_16.getfind_globalBitmap(),
					shortHelpString=_("Global Search Of Contacts Database"), isToggle=False)
		tb.AddControl(wx.wx.TextCtrl(tb, ID_SEARCHGLOBAL, name =_("txtGlobalSearch"),size =(100,-1),style = 0, value = ''))
		tool1 = tb.AddTool(ID_ORGANISATIONDISPLAY, images_contacts_toolbar16_16.getorganisationBitmap(),
					shortHelpString=_("Display Organisations"),)
		tool1 = tb.AddTool(ID_GENERALPRACTICESDISPLAY, images_contacts_toolbar16_16.getgeneralpracticesBitmap(),
					shortHelpString=_("Display General Practices"),)
		tool1 = tb.AddTool(ID_DOCTORSDISPLAY, images_contacts_toolbar16_16.getdoctorBitmap(),
					shortHelpString=_("Display Doctors"),)
		tool1 = tb.AddTool(ID_PERSONSDISPLAY, images_contacts_toolbar16_16.getpersonBitmap(),
					shortHelpString=_("Display Persons"), isToggle=False)
		tool1 = tb.AddTool(ID_ORGANISATIONADD, images_contacts_toolbar16_16.getorganisation_addBitmap(),
					shortHelpString=_("Add an Organisation"),)
	
		tool1 = tb.AddTool(ID_SAVE, images_contacts_toolbar16_16.getsaveBitmap(),
					shortHelpString=_("Save Record"),)
		tool1 = tb.AddTool(ID_BRANCHDEPTADD, images_contacts_toolbar16_16.getbranch_addBitmap(),
					shortHelpString=_("Add Branch or Department"),)
		tool1 = tb.AddTool(ID_EMPLOYEEADD, images_contacts_toolbar16_16.getemployeesBitmap(),
					shortHelpString=_("Add an Employee"),)
		tool1 = tb.AddTool(ID_PERSONADD, images_contacts_toolbar16_16.getperson_addBitmap(),
					shortHelpString=_("Add Person"),)
		#tb.AddControl(wx.wxStaticBitmap(tb, -1, images_contacts_toolbar16_16.getvertical_separator_thinBitmap(), wx.wxDefaultPosition, wx.wxDefaultSize))
	
	
		tb.AddControl(wx.wxStaticBitmap(tb, -1, images_contacts_toolbar16_16.getvertical_separator_thinBitmap(), wx.wxDefaultPosition, wx.wxDefaultSize))
		
		tool1 = tb.AddTool(ID_RELOAD, images_contacts_toolbar16_16.getreloadBitmap(),
					shortHelpString=_("Refresh Display"),)
		
		tb.AddControl(wx.wxStaticBitmap(tb, -1, images_contacts_toolbar16_16.getvertical_separator_thinBitmap(), wx.wxDefaultPosition, wx.wxDefaultSize))
		
		tool1 = tb.AddTool(ID_SEARCHSPECIFIC, images_contacts_toolbar16_16.getfind_specificBitmap(),
					shortHelpString=_("Find Specific Records in Contacts Database"),)
		tool1 = tb.AddTool(ID_SORTA_Z, images_contacts_toolbar16_16.getsort_A_ZBitmap(),
					shortHelpString=_("Sort A to Z"),)
		tool1 = tb.AddTool(ID_SORTZ_A, images_contacts_toolbar16_16.getsort_Z_ABitmap(),
					shortHelpString=_("Sort Z to A"),)
		tool1 = tb.AddTool(ID_SENDEMAIL, images_contacts_toolbar16_16.getsendemailBitmap(),
					shortHelpString=_("Send Email"),)
		tool1 = tb.AddTool(ID_LINKINTERNET, images_contacts_toolbar16_16.getearthBitmap(),
					shortHelpString=_("Load Web Address"),)
		tool1 = tb.AddTool(ID_INSTANTREPORT, images_contacts_toolbar16_16.getlighteningBitmap(),
					shortHelpString=_("Instant Report from Grid"),)
		tool1 = tb.AddTool(ID_REPORTS, images_contacts_toolbar16_16.getreportsBitmap(),
					shortHelpString=_("Pre-formatted reports"),)
	
		self.__connect_commands(tb)

	def __connect_commands(self, toolbar):
		wx.wx.EVT_TOOL(toolbar, ID_ORGANISATIONADD , self.addOrg)
		wx.wx.EVT_TOOL(toolbar, ID_EMPLOYEEADD, self.addEmployee)
		wx.wx.EVT_TOOL(toolbar ,ID_BRANCHDEPTADD , self.addBranchDept)
		wx.wx.EVT_TOOL(toolbar, ID_ORGANISATIONDISPLAY, self.displayOrg)
		wx.wx.EVT_TOOL(toolbar, ID_SAVE, self.saveOrg)

	def addEmployee(self, event):
		print "doEmployeeAdd"
		w = self._last_widget
		w.newPerson()

	def addOrg(self, event):
		print "doOrgAdd"
		w = self._last_widget		  
		w.newOrg()
		
		
	def saveOrg(self, event):
		w = self._last_widget
		w.saveOrg()


		
	def addBranchDept(self, event):
		print "doBranchDeptAdd"
		w = self._last_widget
		parent = w.getCurrent()
		if parent is None:
			print "No parent org for sub org"
			return
		
		if parent.getId() is None:
			print "Please save parent org first"
			return
		
		if not parent.getParent() is None:	
			print "Only one level of sub-org implemented"
			return
		
		w.newOrg(parent)
		


		

	def displayOrg(self, event):
		w = self._last_widget
		w.load_all_orgs()
		


if __name__ == "__main__":
	app = wx.wxPyWidgetTester(size = (800, 600))
	app.SetWidget(cContactsPanel, -1)
	app.MainLoop()

#======================================================
# $Log: gmContacts.py,v $
# Revision 1.48  2007-02-05 12:15:23  ncq
# - no more aMatchProvider/selection_only in cPhraseWheel.__init__()
#
# Revision 1.47  2007/01/20 22:53:32  ncq
# - .KeyCode -> .GetKeyCode()
#
# Revision 1.46  2007/01/18 22:09:18  ncq
# - wx2.8ification
#
# Revision 1.45  2006/10/25 07:22:43  ncq
# - remove outdated phrasewheels
#
# Revision 1.44  2006/07/01 15:22:50  ncq
# - add comment on deprecated setDependant()
#
# Revision 1.43  2006/06/05 21:37:28  ncq
# - id_callback argument not used anymore
#
# Revision 1.42  2005/09/28 21:27:30  ncq
# - a lot of wx2.6-ification
#
# Revision 1.41  2005/09/26 18:01:52  ncq
# - use proper way to import wx26 vs wx2.4
# - note: THIS WILL BREAK RUNNING THE CLIENT IN SOME PLACES
# - time for fixup
#
# Revision 1.40  2004/08/04 17:16:02  ncq
# - wx.NotebookPlugin -> cNotebookPlugin
# - derive cNotebookPluginOld from cNotebookPlugin
# - make cNotebookPluginOld warn on use and implement old
#   explicit "main.notebook.raised_plugin"/ReceiveFocus behaviour
# - ReceiveFocus() -> receive_focus()
#
# Revision 1.39  2004/07/24 17:02:35  ncq
# - some more wx.wx* fixes
#
# Revision 1.38  2004/07/24 16:11:52  ncq
# - normalize wx import for use in 2.4 and 2.5
# 	from wxPython import wx
# 	sth = wx.wxSomething() etc.
#
# Revision 1.37  2004/07/18 20:30:54  ncq
# - wxPython.true/false -> Python.True/False as Python tells us to do
#
# Revision 1.36  2004/06/30 16:06:43  shilbert
# - u guessed it - more wxMAC fixes
#
# Revision 1.35  2004/06/29 22:41:53  shilbert
# - indentation fixes that hopefully didn't break everything
# - wxMAC fixes all over the place
#
# Revision 1.34  2004/06/25 12:37:21  ncq
# - eventually fix the import gmI18N issue
#
# Revision 1.33  2004/06/21 14:48:26  sjtan
#
# restored some methods that gmContacts depends on, after they were booted
# out from gmDemographicRecord with no home to go , works again ;
# removed cCatFinder('occupation') instantiating in main module scope
# which was a source of complaint , as it still will lazy load anyway.
#
# Revision 1.32  2004/06/17 11:43:16  ihaywood
# Some minor bugfixes.
# My first experiments with wxGlade
# changed gmPhraseWheel so the match provider can be added after instantiation
# (as wxGlade can't do this itself)
#
# Revision 1.31  2004/06/13 22:31:48  ncq
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
# Revision 1.30  2004/06/01 15:11:59  sjtan
#
# cut ctrl-x and paste ctrl-v, works through clipboard, so can paste name/address info onto
# text editors (oowriter, kwrite tried out). Drag and drop doesn't work to outside apps.
# List displays at last updated position after load_all_orgs() called. removed
# old display data listing on list org display button press, because cutting and pasting
# persons to these items loses  persons. Only saves top-level orgs if there is a valid
# category value in category field.
#
# Revision 1.29  2004/06/01 07:18:36  ncq
# - simple Mac fix
#
# Revision 1.28  2004/05/31 14:24:19  sjtan
#
# intra-list cut and paste implemented. Not using wxClipboard ( could paste textified person
# into clipboard ). Now the GP can be moved out of the Engineering department , but he may not be happy ;)
#
# Revision 1.27  2004/05/30 10:57:31  sjtan
#
# some code review, commenting, tooltips.
#
# Revision 1.26  2004/05/30 09:06:28  sjtan
#
# avoiding object reload if possible.
#
# Revision 1.25  2004/05/30 03:50:41  sjtan
#
# gmContacts can create/update org, one level of sub-org, org persons, sub-org persons.
# pre-alpha or alpha ? Needs cache tune-up .
#
# Revision 1.24  2004/05/29 12:03:46  sjtan
#
# OrgCategoryMP for gmContact's category field
#
# Revision 1.23  2004/05/28 15:20:41  sjtan
#
# add department and branch, but only onto saved top level orgs (i.e. hospitals
# in the test case/ don't mistake the original dummy rows for saved orgs).
#
# Revision 1.22  2004/05/28 10:06:03  shilbert
# - workaround for wxMac
#
# Revision 1.21  2004/05/28 04:29:55  sjtan
#
# gui test case option; should setup/teardown ok if correct logins.
#
# Revision 1.20  2004/05/28 01:23:44  sjtan
#
# strip whitespace for org list display; update list when org edited and saved; move save button temporarily so visible in default client gui size.
#
# Revision 1.19  2004/05/26 18:21:38  sjtan
#
# add org , save  toolbar buttons linked,  list select linked, needs testing,
# must have 'hospital' if table org_category.
#
# Revision 1.18  2004/05/25 17:56:50  sjtan
#
# first steps at activating gmContacts. Will need a manually inserted
# org_category that matches the category name entered in the category field.
#
# Revision 1.17  2004/05/25 16:18:13  sjtan
#
# move methods for postcode -> urb interaction to gmDemographics so gmContacts can use it.
#
# Revision 1.16  2004/05/25 16:00:34  sjtan
#
# move common urb/postcode collaboration  to business class.
#
# Revision 1.15  2004/05/25 14:51:23  sjtan
#
# savepoint, enable urb and postcode phrasewheels.
#
# Revision 1.14  2004/03/18 09:43:02  ncq
# - import gmI18N if standalone
#
# Revision 1.13  2004/03/09 07:58:26  ncq
# - cleanup
#
# Revision 1.12  2004/03/08 23:55:40  shilbert
# - adapt to new API from Gnumed.foo import bar
#
# Revision 1.11  2004/02/25 09:46:22  ncq
# - import from pycommon now, not python-common
#
# Revision 1.10  2004/02/18 06:30:30  ihaywood
# Demographics editor now can delete addresses
# Contacts back up on screen.
#
# Revision 1.9  2003/11/30 23:42:05  ncq
# - never _('') !!
# - don't use 'xsel' in font defs
#
# Revision 1.8  2003/11/07 22:29:46  shilbert
# - added _() for i18n where necessary
#
# @change log:
# - 02.07.2002 rterry initial implementation, untested
