"""gmDemographics

 This panel will hold all the patients details

 @copyright: authors
 @dependencies: wxPython (>= version 2.3.1)
	28.07.2004 rterry gui-rewrite to include upper patient window
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/Attic/gmDemographics.py,v $
# $Id: gmDemographics.py,v 1.49 2004-12-18 13:45:51 sjtan Exp $
__version__ = "$Revision: 1.49 $"
__author__ = "R.Terry, SJ Tan"
__license__ = 'GPL (details at http://www.gnu.org)'

# standard library
import cPickle, zlib, shutil, time, string

# 3rd party
from mx import DateTime
from wxPython import wx
from wxPython.lib.mixins.listctrl import wxColumnSorterMixin, wxListCtrlAutoWidthMixin

# GnuMed specific
from Gnumed.wxpython import gmPlugin, gmPatientHolder, images_patient_demographics, images_contacts_toolbar16_16, gmPhraseWheel, gmCharacterValidator
from Gnumed.pycommon import  gmGuiBroker, gmLog, gmDispatcher, gmSignals, gmCfg, gmWhoAmI, gmI18N
from Gnumed.business import gmDemographicRecord, gmPatient

# constant defs
_log = gmLog.gmDefLog
_whoami = gmWhoAmI.cWhoAmI()
_cfg = gmCfg.gmDefCfgFile

ID_Popup_SaveDisplayLayout = wx.wxNewId()
ID_Popup_AddPerson = wx.wxNewId()
ID_Popup_AddAddressForPerson = wx.wxNewId()
ID_Popup_AddFamilyMember = wx.wxNewId()
ID_Popup_DeletePerson = wx.wxNewId()
ID_Popup_DeleteAddressForPerson = wx.wxNewId()
ID_Popup_UndoDelete = wx.wxNewId()
ID_Popup_SortA_Z = wx.wxNewId()
ID_Popup_SortZ_A = wx.wxNewId()
ID_Popup_ChangeFont = wx.wxNewId()
ID_Popup_SaveDisplayLayout = wx.wxNewId()
ID_Popup_BuildSQL= wx.wxNewId()
ID_Popup_Help = wx.wxNewId()
#ID_Popup_AddPerson 3 = wx.wxNewId()
#ID_Popup_AddPerson 4 = wx.wxNewId()


ID_PATIENT = wx.wxNewId()
ID_PATIENTSLIST = wx.wxNewId()
ID_ALL_MENU  = wx.wxNewId()
ID_ADDRESSLIST = wx.wxNewId()
ID_NAMESLIST = wx.wxNewId()
ID_CURRENTADDRESS = wx.wxNewId()
ID_COMBOTITLE = wx.wxNewId()
ID_COMBOSEX = wx.wxNewId()
ID_COMBOMARITALSTATUS = wx.wxNewId()
ID_COMBONOKRELATIONSHIP = wx.wxNewId()
ID_TXTSURNAME = wx.wxNewId()
ID_TXTFIRSTNAME = wx.wxNewId()
ID_TXTSALUTATION = wx.wxNewId()
ID_TXTSTREET = wx.wxNewId()
ID_TXTSUBURB = wx.wxNewId()
ID_TXTSTATE = wx.wxNewId()
ID_TXTPOSTCODE = wx.wxNewId()
ID_TXTBIRTHDATE = wx.wxNewId()
ID_TXTCOUNTRYOFBIRTH = wx.wxNewId()
ID_TXTOCCUPATION = wx.wxNewId()
ID_TXTNOKADDRESS = wx.wxNewId()
ID_TXTHOMEPHONE = wx.wxNewId()
ID_TXTWORKPHONE = wx.wxNewId()
ID_TXTFAX = wx.wxNewId()
ID_TXTEMAIL = wx.wxNewId()
ID_TXTINTERNET = wx.wxNewId()
ID_TXTMOBILE = wx.wxNewId()
ID_TXTMEMO = wx.wxNewId()
ID_LISTADDRESSES = wx.wxNewId()
ID_BUTTONBROWSENOK = wx.wxNewId()
ID_BUTTONAQUIRE = wx.wxNewId()
ID_BUTTONPHOTOEXPORT = wx.wxNewId()
ID_BUTTONPHOTOIMPORT = wx.wxNewId()
ID_BUTTONPHOTODELETE = wx.wxNewId()
ID_CHKBOXRESIDENCE = wx.wxNewId()
ID_CHKBOXPOSTAL = wx.wxNewId()
ID_CHKBOXPREFERREDALIAS = wx.wxNewId()
ID_BUTTONFINDPATIENT = wx.wxNewId()
ID_TXTPATIENTFIND = wx.wxNewId()
ID_TXTPATIENTAGE = wx.wxNewId()
ID_TXTPATIENTALLERGIES  = wx.wxNewId()
ID_TXTNOK =wx.wxNewId()

ID_CHECK_SPLIT=wx.wxNewId()

# PatientData = {
# 1 : ("Macks", "Jennifer","Flat9/128 Brook Rd","NEW LAMBTON HEIGHTS", "2302","19/01/2003","M"," 02 49 5678890"),
# 2 : ("Smith","Michelle", "Flat9/128 Brook Rd","ELERMORE VALE", "2302","23/02/1973","F", "02 49564320"),
# 3 : ("Smitt", "Francis","29 Willandra Crescent", "WINDALE"," 2280","18/08/1952","M","02 7819292"),
# 4 : ("Smythe-Briggs", "Elizabeth","129 Flat Rd", "SMITHS LAKE","2425","04/12/1918","F","02 4322222"),
# }

#-----------------------------------------------------------
#text control class to be later replaced by the gmPhraseWheel
#------------------------------------------------------------
class TextBox_RedBold(wx.wxTextCtrl):
	def __init__ (self, parent, id): #, wx.wxPyDefaultPostion, wx.wxPyDefaultSize):
		wx.wxTextCtrl.__init__(self,parent,id,"",wx.wxPyDefaultPosition, wx.wxPyDefaultSize,wx.wxSIMPLE_BORDER)
		self.SetForegroundColour(wx.wxColor(255,0,0))
		self.SetFont(wx.wxFont(12,wx.wxSWISS,wx.wxNORMAL, wx.wxBOLD,False,''))

class BlueLabel_Normal(wx.wxStaticText):
	def __init__(self, parent, id, prompt, text_alignment):
		wx.wxStaticText.__init__(self,parent, id,prompt,wx.wxPyDefaultPosition,wx.wxPyDefaultSize,text_alignment)
		self.SetFont(wx.wxFont(12,wx.wxSWISS,wx.wxNORMAL,wx.wxNORMAL,False,''))
		self.SetForegroundColour(wx.wxColour(0,0,131))

class BlueLabel_Bold(wx.wxStaticText):
	def __init__(self, parent, id, prompt, text_alignment):
		wx.wxStaticText.__init__ (
			self,
			parent,
			id,
			prompt,
			wx.wxPyDefaultPosition,
			wx.wxPyDefaultSize,
			text_alignment
		)
		self.SetFont(wx.wxFont(12, wx.wxSWISS, wx.wxNORMAL, wx.wxBOLD, False, ''))
		#self.SetForegroundColour(wx.wxColour(0,0,131))
		self.SetForegroundColour (wx.wxColour(0,0,255))

class TextBox_BlackNormal(wx.wxTextCtrl):
	def __init__ (self, parent, id): #, wx.wxPyDefaultPosition, wx.wxPyDefaultSize):
		wx.wxTextCtrl.__init__(self,parent,id,"",wx.wxPyDefaultPosition, wx.wxPyDefaultSize,wx.wxSIMPLE_BORDER)
		self.SetForegroundColour(wx.wxColor(0,0,0))
		#self.SetFont(wx.wxFont(12,wx.wxSWISS,wx.wxNORMAL, wx.wxBOLD,False,''))
		self.SetFont(wx.wxFont(12,wx.wxSWISS,wx.wxNORMAL,wx.wxNORMAL,False,''))

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

	def _on_add (self, event):
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

	def _on_del (self, event):
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
#		- This sits on a wx.wxBoxSizer(wx.wxHORIZONTAL) self.sizer_for_patientlist
#	Underneath this all the textboxes for data entry
#		- These are loaded into a gridsizer self.gs
#	Both these sizers sit on self.sizer_main.
#		- self.sizer_for_patientlist expands vertically and horizontally
#		- self.gs expands horizontally but not vertically
#---------------------------------------------------------------------------------------------------------
class PatientsPanel(wx.wxPanel):

	def __init__(self, parent, id= -1):
		wx.wxPanel.__init__ (
			self,
			parent,
			id,
			wx.wxPyDefaultPosition,
			wx.wxPyDefaultSize,
			wx.wxNO_BORDER | wx.wxTAB_TRAVERSAL
		)
		self.gb = gmGuiBroker.GuiBroker()
		self.__createdemographicgui()									#draw the user interface
#		self.__add_character_validators()
 		#self._updateUI()

	def  __createdemographicgui(self):
		#-----------------------------------------------------------
		#   top level page layout:
		#  --------------------------------------
		# | patient search multiple results list |
		# |--------------------------------------
		# |      patient data entry are          |
		#  --------------------------------------
		self.main_splitWindow = wx.wxSplitterWindow( self, -1, point = wx.wxDefaultPosition,  size = wx.wxDefaultSize, style=wx.wxSP_3DSASH)
		self.patientListWin = PatientListWindow(self.main_splitWindow)
		self.patientDetailWin = PatientDetailWindow(self.main_splitWindow)

		self.main_splitWindow.SplitHorizontally( self.patientListWin, self.patientDetailWin)
		self.sizer_main = wx.wxBoxSizer(wx.wxVERTICAL)
		self.sizer_main.Add(self.main_splitWindow, 1, wx.wxEXPAND | wx.wxALL)
#		self.sizer_main.Add (sizer_top_patientlist, 1, wx.wxEXPAND | wx.wxALL, 20)
#		self.sizer_main.Add(sizer_bottom_patient_dataentry, 0, wx.wxEXPAND | wx.wxBOTTOM, 20)
#		self.sizer_main.Add(sizer_top_patientlist, 1, wx.wxEXPAND | wx.wxALL, 2)
#		self.sizer_main.Add(sizer_bottom_patient_dataentry, 0, wx.wxEXPAND | wx.wxALL, 2)

		# adjust layout
		self.SetSizer(self.sizer_main)
#		self.SetSizer( self.main_splitWindow)
		self.SetAutoLayout(True)
		self.sizer_main.Fit(self)
	
		self.inList = 0
		self.preferredListSashPos = 0.8
		self.preferredDetailSashPos = 0.3

		


	#-----------------------------------------------------------

class PatientListWindow(wx.wxPanel):		
#E	, gmPatientHolder.PatientHolder):
#		# FIXME: remove
#		gmPatientHolder.PatientHolder.__init__(self)

	def __init__(self, parent, id= -1):
		wx.wxPanel.__init__ (
			self,
			parent,
			id,
			wx.wxPyDefaultPosition,
			wx.wxPyDefaultSize,
			wx.wxNO_BORDER | wx.wxTAB_TRAVERSAL
		)
		# FIXME: remove
		self.gb = gmGuiBroker.GuiBroker()

		self.__createdemographicgui()

	#-----------------------------------------------------------
	def  __createdemographicgui(self):
		#------------------------------------------------------------------------
		#create patient list, add column headers and data
		#-----------------------------------------------------------------------
		patientlist_ID = wx.wxNewId()
		self.patientlist = wx.wxListCtrl (
			self,
			patientlist_ID,
			wx.wxPyDefaultPosition,
			size=(400,10),
			style = wx.wxLC_REPORT | wx.wxSUNKEN_BORDER | wx.wxLC_VRULES | wx.wxLC_HRULES
		)
		self.patientlist.InsertColumn(0, _("Name"))
		self.patientlist.InsertColumn(1, "")
		self.patientlist.InsertColumn(2, _("Street"))
		self.patientlist.InsertColumn(4, _("Place"))
		self.patientlist.InsertColumn(5, _("Postcode"), wx.wxLIST_FORMAT_CENTRE)
		self.patientlist.InsertColumn(6, _("Date of Birth"), wx.wxLIST_FORMAT_CENTRE)
		self.patientlist.InsertColumn(7, _("Sex"), wx.wxLIST_FORMAT_CENTRE)
		self.patientlist.InsertColumn(8, _("Home Phone"), wx.wxLIST_FORMAT_CENTRE)

		opt_val, set = gmCfg.getDBParam(
			workplace = _whoami.get_workplace(),
			option="widgets.demographics.patientlist.column_sizes"
		)
		if not opt_val or len(opt_val) == 0:
			print 'patient list column sizes: using defaults'
			self.patientcolumnslist = ['100','100','250','200','60','100','50','100']
		else:
			self.patientcolumnslist = opt_val
		print self.patientcolumnslist
		# set column widths
		for i in range (0,8):
			self.patientlist.SetColumnWidth(i,int(self.patientcolumnslist[i]))
# 		#-------------------------------------------------------------
# 		#loop through the PatientData array and add to the list control
# 		#note the different syntax for the first coloum of each row
# 		#i.e. here > self.patientlist.InsertStringItem(x, data[0])!!
# 		#-------------------------------------------------------------
# 		items = PatientData.items()
# 		for x in range(len(items)):
# 			key, data = items[x]
# 			print x, data[0],data[1],data[2],data[3],data[4],data[5]
# 			self.patientlist.InsertStringItem(x, data[0])
# 			self.patientlist.SetStringItem(x, 1, data[1])
# 			self.patientlist.SetStringItem(x, 2, data[2])
# 			self.patientlist.SetStringItem(x, 3, data[3])
# 			self.patientlist.SetStringItem(x, 4, data[4])
# 			self.patientlist.SetStringItem(x, 5, data[5])
# 			self.patientlist.SetStringItem(x, 6, data[6])
# 			self.patientlist.SetStringItem(x, 7, data[7])
# 			self.patientlist.SetItemData(x, key)
# 		#--------------------------------------------------------
# 		#note the number passed to the wx.wxColumnSorterMixin must be
# 		#the 1 based count of columns
# 		#--------------------------------------------------------
# 		self.itemDataMap = PatientData

		sizer_top_patientlist = wx.wxBoxSizer(wx.wxHORIZONTAL)
		sizer_top_patientlist.Add(
			self.patientlist,
			5,						#any non-zero value = make vertically stretchable
			wx.wxEXPAND				#make grow as sizer grows (vertical + horizontal)
			| wx.wxTOP | wx.wxLEFT | wx.wxBOTTOM,	# edges
			2						# by a 10 pixel border
		)
		# adjust layout
		self.SetSizer(sizer_top_patientlist)
#		self.SetSizer( self.main_splitWindow)
		self.SetAutoLayout(True)
		sizer_top_patientlist.Fit(self)
		self.__register_events()

	def __register_events(self):
		# patient list popup menu
		wx.EVT_RIGHT_UP(self.patientlist, self._on_RightClick_patientlist)
		wx.EVT_MENU(self, ID_Popup_SaveDisplayLayout, self._on_PopupSaveDisplayLayout)
		wx.EVT_MENU(self, ID_Popup_AddPerson , self._on_Popup_AddPerson)
		wx.EVT_MENU(self, ID_Popup_AddAddressForPerson, self._on_Popup_AddAddressForPerson)
		wx.EVT_MENU(self, ID_Popup_AddFamilyMember, self._on_Popup_AddFamilyMember)
		wx.EVT_MENU(self, ID_Popup_DeletePerson, self._on_Popup_DeletePerson)
		wx.EVT_MENU(self, ID_Popup_DeleteAddressForPerson, self._on_Popup_DeleteAddressForPerson)
		wx.EVT_MENU(self, ID_Popup_UndoDelete, self._on_Popup_UndoDelete)
		wx.EVT_MENU(self, ID_Popup_SortA_Z, self._on_Popup_SortA_Z)
		wx.EVT_MENU(self, ID_Popup_SortZ_A, self._on_PopupEight_SortZ_A)
		wx.EVT_MENU(self, ID_Popup_ChangeFont, self._on_SelectFontPatientList)
		wx.EVT_MENU(self, ID_Popup_SaveDisplayLayout, self._on_PopupSaveDisplayLayout)
		wx.EVT_MENU(self, ID_Popup_BuildSQL, self._on_Popup_BuildSQL)
		wx.EVT_MENU(self, ID_Popup_Help, self._on_PopupHelp)
		#wx.EVT_MENU(self, ID_Popup_AddPerson 3, self._on_PopupThirteen)
		#wx.EVT_MENU(self, ID_Popup_AddPerson 4, self._on_Popup_DeletePersonteen)

	def _on_RightClick_patientlist(self, event):
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

		#-----------------------------------------------------------------
		# make a menu to popup over the patient list
		#-----------------------------------------------------------------
		self.menu_patientlist = wx.wxMenu()
		#Trigger routine to clear all textboxes to add entirely new person
		item = wx.wxMenuItem(self.menu_patientlist, ID_Popup_AddPerson ,"Add Person")
		item.SetBitmap(images_patient_demographics.getperson_addBitmap())
		self.menu_patientlist.AppendItem(item)

		#Trigger routine to clear all address textboxes only to add another address
		item = wx.wxMenuItem(self.menu_patientlist, ID_Popup_AddAddressForPerson, "Add Address for person")
		item.SetBitmap(images_patient_demographics.getbranch_addBitmap())
		self.menu_patientlist.AppendItem(item)
		#Trigger routine to clear person details, leave address, home phone
		item = wx.wxMenuItem(self.menu_patientlist, ID_Popup_AddFamilyMember,"Add Family Member")
		item.SetBitmap(images_patient_demographics.getemployeesBitmap())
		self.menu_patientlist.AppendItem(item)
		self.menu_patientlist.AppendSeparator()
		#Trigger routine to delete a person
		item = wx.wxMenuItem(self.menu_patientlist, ID_Popup_DeletePerson,"Delete Person")
		item.SetBitmap(images_patient_demographics.getcutBitmap())
		self.menu_patientlist.AppendItem(item)

		#Trigger routine to delete an address (if > 1) for a person
		self.menu_patientlist.Append(ID_Popup_DeleteAddressForPerson, "Delete Address for person")
		self.menu_patientlist.AppendSeparator()

		#Trigger nested undo-deletes
		self.menu_patientlist.Append(ID_Popup_UndoDelete, "Undo Delete")
		#self.menu_patientlist.AppendItem(item)
		self.menu_patientlist.AppendSeparator()
		#trigger routine to sort visible patient lists by surname A_Z
		item = wx.wxMenuItem(self.menu_patientlist, ID_Popup_SortA_Z,"Sort A_Z")
		item.SetBitmap(images_patient_demographics.getsort_A_ZBitmap())
		self.menu_patientlist.AppendItem(item)

		item = wx.wxMenuItem(self.menu_patientlist, ID_Popup_SortZ_A,"Sort Z_A")
		item.SetBitmap(images_patient_demographics.getsort_Z_ABitmap())
		self.menu_patientlist.AppendItem(item)
		self.menu_patientlist.AppendSeparator()

		self.menu_patientlist.Append(ID_Popup_ChangeFont, "Change Font")

		self.menu_patientlist.Append(ID_Popup_SaveDisplayLayout, "Save Display Layout")
		#self.menu_patientlist.AppendItem(item)
		self.menu_patientlist.AppendSeparator()
		#Save search query to database as user defined query
		item = wx.wxMenuItem(self.menu_patientlist,ID_Popup_BuildSQL, "Build SQL")
		item.SetBitmap(images_patient_demographics.getsqlBitmap())
		self.menu_patientlist.AppendItem(item)
		self.menu_patientlist.AppendSeparator()
		#Jump to help for patients_list
		item = wx.wxMenuItem(self.menu_patientlist, ID_Popup_Help,  "Help")
		item.SetBitmap(images_patient_demographics.gethelpBitmap())
		self.menu_patientlist.AppendItem(item)
		self.menu_patientlist.AppendSeparator()


		# Popup the menu.  If an item is selected then its handler
		# will be called before PopupMenu returns.
		self.PopupMenu(self.menu_patientlist, event.GetPosition())
		self.menu_patientlist.Destroy()


	def _on_Popup_AddPerson(self, event):
	       print 'I\'m adding a person.....'
		#self.log.WriteText("Popup one\n")

	def _on_Popup_AddAddressForPerson(self, event):
		print 'I\'m adding a new address for a person.....'

	def _on_Popup_AddFamilyMember(self, event):
		print 'I\'m adding a family member.....'


	def _on_Popup_DeletePerson(self, event):
		print 'I\'m deleting a person....'

	def _on_Popup_DeleteAddressForPerson(self, event):
		print 'I\'m deleting an address for a person...'

	def _on_Popup_UndoDelete(self, event):
		print 'I\'m undoing the last delete....'

	def _on_Popup_SortA_Z(self, event):
		print 'I\'m sorting A to Z..'

	def _on_PopupEight_SortZ_A(self,event):
		print 'I\'m sorting Z_A...'
	def _on_Popup_BuildSQL(self, event):
		print '\'m saving the sql of this search'

	def _on_PopupHelp(self, event):
		print 'I\'m popping up help'


	def UpdateFontPatientListI(self):
		self.patientlist.SetFont(self.curFont)
	# 			self.ps.SetLabel(str(self.curFont.GetPointSize()))
	# 			self.family.SetLabel(self.curFont.GetFamilyString())
	# 			self.style.SetLabel(self.curFont.GetStyleString())
	# 			self.weight.SetLabel(self.curFont.GetWeightString())
	# 			self.face.SetLabel(self.curFont.GetFaceName())
	# 			self.nfi.SetLabel(self.curFont.GetNativeFontInfo().ToString())
		self.Layout()

	def _on_SelectFontPatientList(self, evt):
		self.curFont = self.patientlist.GetFont()
        	self.curClr = wx.wxBLACK
		print 'Selecting font list'
		data = wx.wxFontData()
		data.EnableEffects(True)
		data.SetColour(self.curClr)         # set colour
		data.SetInitialFont(self.curFont)

		dlg = wx.wxFontDialog(self, data)
		if dlg.ShowModal() == wx.wxID_OK:
			data = dlg.GetFontData()
			font = data.GetChosenFont()
			colour = data.GetColour()
# 			self.log.WriteText('You selected: "%s", %d points, color %s\n' %
# 					(font.GetFaceName(), font.GetPointSize(),
# 						colour.Get()))
			self.curFont = font
			self.curClr = colour
			self.UpdateFontPatientListI()
		dlg.Destroy()
	#----------------------------------------------------------
	def _on_PopupSaveDisplayLayout(self, event):
		wx.wxBeginBusyCursor()
		pat_cols_widths = []										#create empty list
		for col in range (0, self.patientlist.GetColumnCount()): 			# get widths of columns
			pat_cols_widths.append(self.patientlist.GetColumnWidth(col))		# add to the list
		gmCfg.setDBParam (										# set the value for the current user/workplace
			workplace = _whoami.get_workplace(),
			option = "widgets.demographics.patientlist.column_sizes",
			value = pat_cols_widths
		)
		wx.wxEndBusyCursor()
	#----------------------------------------------------------
	def _on_PopupEleven(self, event):
		self.log.WriteText("Popup nine\n")

	def _on_PopupTwelve(self, event):
		self.log.WriteText("Popup nine\n")

	def _on_PopupThirteen(self, event):
		self.log.WriteText("Popup nine\n")

	def _on_Popup_DeletePersonteen(self, event):
		self.log.WriteText("Popup nine\n")

	def _on_PopupFifteen(self, event):
		self.log.WriteText("Popup nine\n")

	def _on_Popup_UndoDeleteteen(self, event):
		self.log.WriteText("Popup nine\n")

	
class PatientDetailWindow(wx.wxPanel):		
	def __init__(self, parent, id= -1):
		wx.wxPanel.__init__ (
			self,
			parent,
			id,
			wx.wxPyDefaultPosition,
			wx.wxPyDefaultSize,
			wx.wxNO_BORDER | wx.wxTAB_TRAVERSAL
		)
		# FIXME: remove
		self.gb = gmGuiBroker.GuiBroker()
		try:
			self.mwm = self.gb['clinical.manager']
		except:
			self.mwm = {}
		self.to_delete = []
		self.addr_cache = []
		self.comm_channel_names = gmDemographicRecord.getCommChannelTypes()
		self.gendermap = {
			'm': _('Male'),
			'f': _("Female"),
			'?': _("Unknown"),
			'tm': _('Trans. Male'),
			'tf': _('Trans. Female'),
			'h':_('Hermaphrodite')
		}
		self.__createdemographicgui()
		self.__create_input_field_map()

		
	def  __createdemographicgui(self):
		lbl_space = BlueLabel_Normal(self,-1,"",wx.wxLEFT) #This lbl_space is used as a spacer between label


		#-------------------------------------------------------------------
		#Add surname, firstname, title, sex, salutation
		#-------------------------------------------------------------------
		lbl_surname = BlueLabel_Normal(self,-1, _("Surname"), wx.wxLEFT)
		self.txt_surname = TextBox_RedBold(self,-1)
		lbl_title = BlueLabel_Normal(self,-1, _("Title"), wx.wxALIGN_CENTRE)
		# FIXME: load from database
		titlelist = ['Mr', 'Mrs', 'Miss', 'Mst', 'Ms', 'Dr', 'Prof']
		# FIXME: ID cannot be hard-coded
		self.combo_title = wx.wxComboBox (
			self,
			500,
			"",
			wx.wxPyDefaultPosition,
			wx.wxPyDefaultSize,
			titlelist,
			wx.wxCB_DROPDOWN
		)
		sizer_line1 = wx.wxBoxSizer(wx.wxHORIZONTAL)  		 #holds surname label + textbox, title label and combobox
		sizer_line1.Add(lbl_surname,3,wx.wxEXPAND|wx.wxTOP|wx.wxBOTTOM,1)
		sizer_line1.Add(self.txt_surname,5,wx.wxEXPAND|wx.wxTOP|wx.wxBOTTOM,1)
		sizer_line1.Add(lbl_title,3,wx.wxEXPAND|wx.wxTOP|wx.wxBOTTOM,1)
		sizer_line1.Add(self.combo_title,5,wx.wxEXPAND|wx.wxTOP|wx.wxBOTTOM,1)

		lbl_firstname = BlueLabel_Normal(self,-1, _("Firstname"), wx.wxLEFT)
		self.txt_firstname = TextBox_RedBold(self,-1)
		lbl_sex = BlueLabel_Normal(self,-1, _("Sex"), wx.wxALIGN_CENTRE)
		self.combo_sex = wx.wxComboBox (
			self,
			500,
			"",
			wx.wxPyDefaultPosition,
			wx.wxPyDefaultSize,
			self.gendermap.values(),
			wx.wxCB_DROPDOWN
		)
		lbl_preferredname =  BlueLabel_Normal(self,-1, _("Salutation"), wx.wxLEFT)
		self.txt_preferredname = TextBox_RedBold(self,-1)
		sizer_line2 = wx.wxBoxSizer(wx.wxHORIZONTAL)  		#holds firstname label + textbox, sex label + combobox
		sizer_line2.Add(lbl_firstname,3,wx.wxEXPAND|wx.wxTOP|wx.wxBOTTOM,1)
		sizer_line2.Add(self.txt_firstname,5,wx.wxEXPAND|wx.wxTOP|wx.wxBOTTOM,1)
		sizer_line2.Add(lbl_sex,3,wx.wxEXPAND|wx.wxTOP|wx.wxBOTTOM,1)

		#-----------------------------------------------------------------------------------
		#now add gui-elements to sizers for surname to salutation
		#each line has several (up to 4 elements
		# e.g surname <textbox> title <textbox> etc
		#-----------------------------------------------------------------------------------

		sizer_line2.Add(self.combo_sex,5,wx.wxEXPAND|wx.wxTOP|wx.wxBOTTOM,1)
		sizer_line3 = wx.wxBoxSizer(wx.wxHORIZONTAL)		#holds preferredname label and textbox
		sizer_line3.Add(lbl_preferredname,3,wx.wxEXPAND|wx.wxTOP|wx.wxBOTTOM,1)
		sizer_line3.Add(self.txt_preferredname,5,wx.wxEXPAND|wx.wxTOP|wx.wxBOTTOM,1)
		sizer_line3.Add(lbl_space,8,wx.wxEXPAND|wx.wxTOP|wx.wxBOTTOM,1)
		#--------------------------------------------------------------------------
		#The heading for 'Address, sits on its own box sizer
		#--------------------------------------------------------------------------
		lbl_heading_address = BlueLabel_Bold(self,-1, _("Address"), wx.wxALIGN_CENTRE)
		self.sizer_lbl_heading_address = wx.wxBoxSizer(wx.wxHORIZONTAL)   #holds address heading
		self.sizer_lbl_heading_address.Add(lbl_space,1,wx.wxEXPAND|wx.wxTOP|wx.wxBOTTOM,1)
	#	self.sizer_lbl_heading_address.Add(lbl_space,1,wx.wxEXPAND|wx.wxTOP|wx.wxBOTTOM,1)
		self.sizer_lbl_heading_address.Add(lbl_heading_address,1,wx.wxEXPAND|wx.wxTOP|wx.wxBOTTOM,1)
		lbl_space2 = BlueLabel_Normal(self,-1,"",wx.wxLEFT) #This lbl_space is used as a spacer between label
		self.sizer_lbl_heading_address.Add(lbl_space2,1,wx.wxEXPAND|wx.wxTOP|wx.wxBOTTOM,1)
		#------------------------------------------------------------------------------
		#Next add street label + 3 line size textbox for street
		#------------------------------------------------------------------------------
		self.sizer_street = wx.wxBoxSizer(wx.wxHORIZONTAL)
		lbl_street = BlueLabel_Normal(self,-1, _("Street"), wx.wxLEFT)
		self.txt_street = wx.wxTextCtrl(self, 30, "",wx.wxPyDefaultPosition, size=(1,50),style=wx.wxTE_MULTILINE)
		self.sizer_street.Add(lbl_street,3,wx.wxEXPAND)
		self.sizer_street.Add(self.txt_street,13, wx.wxEXPAND)
		#------------------------------------------------
		#suburb on one line
		#------------------------------------------------
		self.sizer_suburb = wx.wxBoxSizer(wx.wxHORIZONTAL)
		lbl_suburb = BlueLabel_Normal(self,-1, _("Municipality"), wx.wxLEFT)
		self.txt_suburb = gmPhraseWheel.cPhraseWheel (
			parent = self,
			id = -1,
			aMatchProvider = gmDemographicRecord.MP_urb_by_zip(),
			selection_only = 1,
			pos = wx.wxPyDefaultPosition,
			size=wx.wxPyDefaultSize,
			id_callback= self.__urb_selected
		)
		self.sizer_suburb.Add(lbl_suburb,3,wx.wxEXPAND|wx.wxTOP|wx.wxBOTTOM,1)
		self.sizer_suburb.Add(self.txt_suburb,13,wx.wxEXPAND|wx.wxTOP|wx.wxBOTTOM,1)
		self.sizer_stateandpostcode = wx.wxBoxSizer(wx.wxHORIZONTAL)
		#-----------------------------------------------------------
		#state and postcode on next line on sizer
		#-----------------------------------------------------------
		lbl_state = BlueLabel_Normal(self,-1, _("State"), wx.wxLEFT)
		self.txt_state = TextBox_BlackNormal(self,-1)
		lbl_postcode = BlueLabel_Normal(self,-1, _("Postcode"), wx.wxALIGN_CENTRE)
  		self.txt_postcode  = gmPhraseWheel.cPhraseWheel (
			parent = self,
			id = -1,
			aMatchProvider = gmDemographicRecord.PostcodeMP(),
			selection_only = 1,
			pos = wx.wxPyDefaultPosition,
			size=wx.wxPyDefaultSize
		)
		self.txt_postcode.setDependent (self.txt_suburb, _('postcode'))
		self.sizer_stateandpostcode.Add(lbl_state,3,wx.wxEXPAND|wx.wxTOP|wx.wxBOTTOM,1)
		self.sizer_stateandpostcode.Add(self.txt_state,5,wx.wxEXPAND|wx.wxTOP|wx.wxBOTTOM,1)
		self.sizer_stateandpostcode.Add(lbl_postcode,3,wx.wxEXPAND|wx.wxTOP|wx.wxBOTTOM,1)
		self.sizer_stateandpostcode.Add(self.txt_postcode,5,wx.wxEXPAND|wx.wxTOP|wx.wxBOTTOM,1)
		#Next line = Type of address (e.g home, work, parents - any one of which could be a 'postal address'
		self.sizer_addresstype_chkpostal = wx.wxBoxSizer(wx.wxHORIZONTAL)
		lbl_addresstype = BlueLabel_Normal(self,-1, _("Type"), wx.wxLEFT)
		# FIXME: get from database
		self.combo_address_types = ['Home', 'Work', 'Parents','Post Office Box']
		self.combo_address_type = wx.wxComboBox (
			self,
			-1,
			"",
			wx.wxPyDefaultPosition,
			wx.wxPyDefaultSize,
			self.combo_address_types,
			wx.wxCB_DROPDOWN | wx.wxCB_READONLY
		)
		self.chk_addresspostal = wx.wxCheckBox(
			self,
			-1,
			_("Postal Address"),
			wx.wxPyDefaultPosition,
			wx.wxPyDefaultSize, 
			wx.wxNO_BORDER
		)
		self.chk_addresspostal.SetForegroundColour(wx.wxColour(0,0,131))
		self.sizer_addresstype_chkpostal.Add(lbl_addresstype,3,wx.wxEXPAND|wx.wxTOP|wx.wxBOTTOM,1)
		self.sizer_addresstype_chkpostal.Add(self.combo_address_type,5,wx.wxEXPAND|wx.wxTOP|wx.wxBOTTOM,1)
		self.sizer_addresstype_chkpostal.Add(lbl_space,3,wx.wxEXPAND|wx.wxTOP|wx.wxBOTTOM,1)
		self.sizer_addresstype_chkpostal.Add(self.chk_addresspostal,5,wx.wxEXPAND|wx.wxBOTTOM,1)
		#----------------------------------------------------------------------------------------------------------------------
		#Contact details - phone work, home,fax,mobile,internet and email
		#-----------------------------------------------------------------------------------------------------------------------
		self.sizer_contacts_line1 = wx.wxBoxSizer(wx.wxHORIZONTAL)
		self.sizer_contacts_line2 = wx.wxBoxSizer(wx.wxHORIZONTAL)
		self.sizer_contacts_line3 = wx.wxBoxSizer(wx.wxHORIZONTAL)
		self.sizer_contacts_line4 = wx.wxBoxSizer(wx.wxHORIZONTAL)
		lbl_contact_heading = BlueLabel_Bold(self,-1, _("Contact Details"), wx.wxLEFT)
		lbl_homephone = BlueLabel_Normal(self,-1, _("Home Phone"), wx.wxLEFT)
		lbl_workphone = BlueLabel_Normal(self,-1, _("Work Phone"), wx.wxLEFT)
		lbl_mobile = BlueLabel_Normal(self,-1, _("Mobile"), wx.wxLEFT)
		lbl_fax = BlueLabel_Normal(self,-1, _("Fax"), wx.wxALIGN_CENTRE)
		lbl_email = BlueLabel_Normal(self,-1, _("Email"), wx.wxALIGN_CENTRE)
		lbl_web = BlueLabel_Normal(self,-1, _("Web"), wx.wxALIGN_CENTRE)
		self.txt_homephone = TextBox_BlackNormal(self,-1)
		self.txt_workphone = TextBox_BlackNormal(self,-1)
		self.txt_mobile = TextBox_BlackNormal(self,-1)
		self.txt_fax = TextBox_BlackNormal(self,-1)
		self.txt_email = TextBox_BlackNormal(self,-1)
		self.txt_web = TextBox_BlackNormal(self,-1)

		lbl_space = BlueLabel_Normal(self,-1,"",wx.wxLEFT) #This lbl_space is used as a spacer between label
		self.sizer_contacts_line1 .Add(lbl_space,1,wx.wxEXPAND|wx.wxTOP|wx.wxBOTTOM,1)
		lbl_space = BlueLabel_Normal(self,-1,"",wx.wxLEFT) #This lbl_space is used as a spacer between label
		self.sizer_contacts_line1 .Add(lbl_space,1,wx.wxEXPAND)
		self.sizer_contacts_line1 .Add(lbl_contact_heading,1,wx.wxEXPAND|wx.wxTOP|wx.wxBOTTOM,1)
		lbl_space = BlueLabel_Normal(self,-1,"",wx.wxLEFT) #This lbl_space is used as a spacer between label
		self.sizer_contacts_line1 .Add(lbl_space,1,wx.wxEXPAND|wx.wxTOP|wx.wxBOTTOM,1)
		self.sizer_contacts_line2 .Add(lbl_homephone,3,wx.wxEXPAND|wx.wxTOP|wx.wxBOTTOM,1)
		self.sizer_contacts_line2 .Add(self.txt_homephone,5,wx.wxEXPAND|wx.wxTOP|wx.wxBOTTOM,1)
		self.sizer_contacts_line2 .Add(lbl_fax,3,wx.wxEXPAND|wx.wxTOP|wx.wxBOTTOM,1)
		self.sizer_contacts_line2 .Add(self.txt_fax,5,wx.wxEXPAND|wx.wxTOP|wx.wxBOTTOM,1)
		self.sizer_contacts_line3 .Add(lbl_workphone,3,wx.wxEXPAND|wx.wxTOP|wx.wxBOTTOM,1)
		self.sizer_contacts_line3 .Add(self.txt_workphone,5,wx.wxEXPAND|wx.wxTOP|wx.wxBOTTOM,1)
		self.sizer_contacts_line3 .Add(lbl_email,3,wx.wxEXPAND|wx.wxTOP|wx.wxBOTTOM,1)
		self.sizer_contacts_line3 .Add(self.txt_email,5,wx.wxEXPAND|wx.wxTOP|wx.wxBOTTOM,1)
		self.sizer_contacts_line4 .Add(lbl_mobile,3,wx.wxEXPAND|wx.wxTOP|wx.wxBOTTOM,1)
		self.sizer_contacts_line4 .Add(self.txt_mobile,5,wx.wxEXPAND|wx.wxTOP|wx.wxBOTTOM,1)
		self.sizer_contacts_line4 .Add(lbl_web,3,wx.wxEXPAND|wx.wxTOP|wx.wxBOTTOM,1)
		self.sizer_contacts_line4 .Add(self.txt_web,5,wx.wxEXPAND|wx.wxTOP|wx.wxBOTTOM,1)
		self.sizer_contacts =wx.wxBoxSizer(wx.wxVERTICAL)

		#------------------------------------------------------------------------------------------------------------------------
		#Now add all the lines for the left side of the screen on their sizers to sizer_leftside
		#i.e Patient Names through to their contact details
		#------------------------------------------------------------------------------------------------------------------------
		sizer_leftside = wx.wxBoxSizer(wx.wxVERTICAL)
#		sizer_leftside.Add(0,10,0)
#		sizer_leftside.Add(sizer_line1,0,wx.wxEXPAND|wx.wxLEFT|wx.wxRIGHT,20)
		sizer_leftside.Add(sizer_line1, 0, wx.wxEXPAND)
#		sizer_leftside.Add(sizer_line2,0,wx.wxEXPAND|wx.wxLEFT|wx.wxRIGHT,20)
		sizer_leftside.Add(sizer_line2, 0, wx.wxEXPAND)
#		sizer_leftside.Add(sizer_line3,0,wx.wxEXPAND|wx.wxLEFT|wx.wxRIGHT,20)
		sizer_leftside.Add(sizer_line3, 0, wx.wxEXPAND)
#		sizer_leftside.Add(self.sizer_lbl_heading_address,0,wx.wxEXPAND|wx.wxLEFT|wx.wxRIGHT,20)
		sizer_leftside.Add(self.sizer_lbl_heading_address, 0, wx.wxEXPAND)
#		sizer_leftside.Add(self.sizer_street  ,0,wx.wxEXPAND|wx.wxLEFT|wx.wxRIGHT,20)
		sizer_leftside.Add(self.sizer_street, 0, wx.wxEXPAND)
#		sizer_leftside.Add(self.sizer_suburb  ,0,wx.wxEXPAND|wx.wxLEFT|wx.wxRIGHT,20)
		sizer_leftside.Add(self.sizer_suburb, 0, wx.wxEXPAND)
#		sizer_leftside.Add(self.sizer_stateandpostcode,0,wx.wxEXPAND|wx.wxLEFT|wx.wxRIGHT,20)
		sizer_leftside.Add(self.sizer_stateandpostcode, 0, wx.wxEXPAND)
#		sizer_leftside.Add(self.sizer_addresstype_chkpostal,0,wx.wxEXPAND|wx.wxLEFT|wx.wxRIGHT,20)
		sizer_leftside.Add(self.sizer_addresstype_chkpostal, 0, wx.wxEXPAND)
#		sizer_leftside.Add(self.sizer_contacts_line1,0,wx.wxEXPAND|wx.wxLEFT|wx.wxRIGHT,20)
		sizer_leftside.Add(self.sizer_contacts_line1, 0, wx.wxEXPAND)
#		sizer_leftside.Add(self.sizer_contacts_line2,0,wx.wxEXPAND|wx.wxLEFT|wx.wxRIGHT,20)
		sizer_leftside.Add(self.sizer_contacts_line2, 0, wx.wxEXPAND)
#		sizer_leftside.Add(self.sizer_contacts_line3,0,wx.wxEXPAND|wx.wxLEFT|wx.wxRIGHT,20)
		sizer_leftside.Add(self.sizer_contacts_line3, 0, wx.wxEXPAND)
#		sizer_leftside.Add(self.sizer_contacts_line4,0,wx.wxEXPAND|wx.wxLEFT|wx.wxRIGHT,20)
		sizer_leftside.Add(self.sizer_contacts_line4, 0, wx.wxEXPAND)

		#-----------------------------------------------------------
		#   right-hand size of bottom half:
		#  ----------------------------------------------
		# | DOB: __________  marital status: ___________ |
		# | occupation: ________________________________ |
		# | country of birth: __________________________ |
		# |           Next Of Kin                        |
		# | details: ___________________________________ |
		# |          ___________________________________ |
		# | relationship: ______________________________ |
		# |       .-------------------.                  |
		# |       | browse DB for NOK |                  |
		# |       `-------------------'                  |
		# |         External IDs                         |
		# |                                              |
		#  ----------------------------------------------
		#-----------------------------------------------------------

		# dob | marital status
		lbl_dob = BlueLabel_Normal(self,-1, _("Birthdate"), wx.wxLEFT)
		self.txt_dob = TextBox_BlackNormal(self,-1)
		lbl_maritalstatus = BlueLabel_Normal(self,-1, _("Marital Status"), wx.wxALIGN_CENTER)
		# FIXME: need to get from database
#		gmDemographicRecord.getMaritalStatusTypes()
		marital_status_types = ['Married', 'Single', 'Defacto']
		# FIXME: ID cannot be hardcoded
		self.combo_maritalstatus = wx.wxComboBox (
			self,
			500,
			"",
			wx.wxPyDefaultPosition,
			wx.wxPyDefaultSize,
			marital_status_types,
			wx.wxCB_DROPDOWN | wx.wxCB_READONLY
		)
		sizer_dob_marital = wx.wxBoxSizer(wx.wxHORIZONTAL)
		sizer_dob_marital.Add(lbl_dob, 3, wx.wxEXPAND)
		sizer_dob_marital.Add(self.txt_dob, 5, wx.wxEXPAND)
		sizer_dob_marital.Add(lbl_maritalstatus, 3, wx.wxEXPAND)
		sizer_dob_marital.Add(self.combo_maritalstatus, 5, wx.wxEXPAND)

		# occupation
		lbl_job = BlueLabel_Normal(self, -1, _("Occupation"), wx.wxLEFT)
		self.txt_job = gmPhraseWheel.cPhraseWheel (
			parent = self,
			id = -1,
			aMatchProvider = gmDemographicRecord.OccupationMP(),
			pos = wx.wxPyDefaultPosition,
			size = wx.wxPyDefaultSize
		)
		sizer_job = wx.wxBoxSizer(wx.wxHORIZONTAL)
		sizer_job.Add(lbl_job, 3, wx.wxEXPAND)
		sizer_job.Add(self.txt_job, 13, wx.wxEXPAND)

  		# country of birth
		lbl_countryofbirth = BlueLabel_Normal(self, -1, _("Born In"), wx.wxLEFT)
		self.txt_countryofbirth = gmPhraseWheel.cPhraseWheel (
			parent = self,
			id = -1,
			aMatchProvider = gmDemographicRecord.CountryMP(),
			pos = wx.wxPyDefaultPosition,
			size = wx.wxPyDefaultSize
		)
		sizer_countryofbirth = wx.wxBoxSizer(wx.wxHORIZONTAL)
		sizer_countryofbirth.Add(lbl_countryofbirth, 3, wx.wxEXPAND)
		sizer_countryofbirth.Add(self.txt_countryofbirth, 13, wx.wxEXPAND)

		# NOK
		lbl_nok_heading = BlueLabel_Bold(self, -1, _("Next of Kin"), wx.wxALIGN_CENTER)
		# I see no reason for the extra sizer
#		sizer_heading_nok = wx.wxBoxSizer(wx.wxHORIZONTAL)   #holds address heading
#		sizer_heading_nok.Add(lbl_space,1,wx.wxEXPAND)
#		sizer_heading_nok.Add(lbl_space,1,wx.wxEXPAND)
#		sizer_heading_nok.Add(lbl_nok_heading, 1, wx.wxEXPAND | wx.wxTOP | wx.wxBOTTOM, 1)
#		sizer_heading_nok.Add(lbl_space,1,wx.wxEXPAND)

		# NOK name/address
		lbl_nok_details = BlueLabel_Normal(self, -1, _("NOK Details"), wx.wxLEFT)
		self.txt_nok_name_addr = wx.wxTextCtrl (
			self,
			ID_TXTNOK,
			"",
			wx.wxPyDefaultPosition,
			size=(1,50),				 # note 1=arbitary,  50 needed to allow it to expand, otherwise is small
			style = wx.wxTE_MULTILINE | wx.wxTE_READONLY
		)
		sizer_nok_name_addr = wx.wxBoxSizer(wx.wxHORIZONTAL)
		sizer_nok_name_addr.Add(lbl_nok_details, 3, wx.wxEXPAND)
		sizer_nok_name_addr.Add(self.txt_nok_name_addr, 13, wx.wxEXPAND)

		# NOK relationship/phone
		lbl_relationshipNOK = BlueLabel_Normal(self, -1, _("Relationship"), wx.wxLEFT)
		# FIXME: get from database
		self.cmb_relationshipNOK = wx.wxComboBox(
			self,
			-1,
			"",
			wx.wxPyDefaultPosition,
			wx.wxPyDefaultSize,
			['Father','Mother','Daughter','Son','Aunt','Uncle','Unknown'],
			wx.wxCB_DROPDOWN
		)
		sizer_nok_relationship = wx.wxBoxSizer(wx.wxHORIZONTAL)
		sizer_nok_relationship.Add(lbl_relationshipNOK, 3, wx.wxEXPAND)
		sizer_nok_relationship.Add(self.cmb_relationshipNOK, 13, wx.wxEXPAND)

		# NOK browse DB
		self.btn_nok_search = wx.wxButton(self, -1, _("Browse for Next Of Kin Details"))
		sizer_search_nok = wx.wxBoxSizer(wx.wxHORIZONTAL)
		sizer_search_nok.Add(lbl_space, 3, wx.wxEXPAND)
		sizer_search_nok.Add(self.btn_nok_search, 13, wx.wxEXPAND)

		#-----------------------------------------------------------------------------
		# undecided - in AU example need medicare/repatriation/pharmaceutical benefits
		# Liz Dodd says: DVA-Gold DVA-White(specified illness) DVA-RED/ORANGE (medications only)
		#	Health care card/Seniors Health Care Card Pension Card Pharmaceutical Benefits Safety Net Number
		#-----------------------------------------------------------------------------
		lbl_id_numbers = BlueLabel_Bold(self, -1, _("Cards etc"), wx.wxALIGN_CENTER)
#		self.sizer_idnumbers_line1 = wx.wxBoxSizer(wx.wxHORIZONTAL)
#		self.sizer_idnumbers_line1.Add(lbl_space,1,wx.wxEXPAND|wx.wxTOP|wx.wxBOTTOM,1)
#		self.sizer_idnumbers_line1.Add(lbl_space,1,wx.wxEXPAND)
#		self.sizer_idnumbers_line1.Add(lbl_id_numbers,1,wx.wxEXPAND|wx.wxTOP|wx.wxBOTTOM,1)
#		self.sizer_idnumbers_line1.Add(lbl_space,1,wx.wxEXPAND|wx.wxTOP|wx.wxBOTTOM,1)

#		self.ext_id_panel = ExtIDPanel (self, self.gs)

		# stack lines atop each other
		sizer_rightside = wx.wxBoxSizer(wx.wxVERTICAL)
#		sizer_rightside.Add(0,10,0)
		sizer_rightside.Add(sizer_dob_marital, 0, wx.wxEXPAND)
		sizer_rightside.Add(sizer_job, 0, wx.wxEXPAND)
		sizer_rightside.Add(sizer_countryofbirth, 0, wx.wxEXPAND)
		sizer_rightside.Add(lbl_nok_heading, 0, wx.wxEXPAND)
		sizer_rightside.Add(sizer_nok_name_addr, 0, wx.wxEXPAND)
		sizer_rightside.Add(sizer_nok_relationship, 0, wx.wxEXPAND)
		sizer_rightside.Add(sizer_search_nok, 0, wx.wxEXPAND)
		sizer_rightside.Add(lbl_id_numbers, 0, wx.wxEXPAND)

		#-----------------------------------------------------------
		#   bottom half of screen:
		#  ------------------------
		# | demographics | details |
		#  ------------------------
		sizer_bottom_patient_dataentry = wx.wxBoxSizer(wx.wxHORIZONTAL)
		sizer_bottom_patient_dataentry.Add(sizer_leftside, 1, wx.wxEXPAND | wx.wxRIGHT, 5)
		sizer_bottom_patient_dataentry.Add(sizer_rightside, 1, wx.wxEXPAND)

		self.SetSizer(sizer_bottom_patient_dataentry)
		self.SetAutoLayout(True)
		sizer_bottom_patient_dataentry.Fit(self)

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
# 		wx.EVT_BUTTON(b, b.GetId() , self._add_address_pressed)
# 		b = self.btn_del_address
# 		wx.EVT_BUTTON(b, b.GetId() ,  self._del_address_pressed)
#
# 		b = self.btn_save
# 		wx.EVT_BUTTON(b, b.GetId(), self._save_btn_pressed)
# 		wx.EVT_BUTTON(self.btn_del, self.btn_del.GetId (), self._del_button_pressed)
# 		wx.EVT_BUTTON(self.btn_new, self.btn_new.GetId (), self._new_button_pressed)
#
# 		l = self.addresslist
# 		wx.EVT_LISTBOX_DCLICK(l, l.GetId(), self._address_selected)
#
# 		wx.EVT_BUTTON(self.btn_photo_import, self.btn_photo_import.GetId (), self._photo_import)
# 		wx.EVT_BUTTON(self.btn_photo_export, self.btn_photo_export.GetId (), self._photo_export)

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
		print myPatient
		pass
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
	app = wx.wxPyWidgetTester(size = (800, 600))
	app.SetWidget(PatientsPanel, -1)
	app.MainLoop()
#============================================================
# $Log: gmDemographics.py,v $
# Revision 1.49  2004-12-18 13:45:51  sjtan
#
# removed timer.
#
# Revision 1.48  2004/10/20 11:20:10  sjtan
# restore imports.
#
# Revision 1.47  2004/10/19 21:34:25  sjtan
# dir is direction, and this is checked
#
# Revision 1.46  2004/10/19 21:29:25  sjtan
# remove division by zero problem, statement occurs later after check for non-zero.
#
# Revision 1.45  2004/10/17 23:49:21  sjtan
#
# the timer autoscroll idea.
#
# Revision 1.44  2004/10/17 22:26:42  sjtan
#
# split window new look Richard's demographics ( his eye for gui design is better
# than most of ours). Rollback if vote no.
#
# Revision 1.43  2004/10/16 22:42:12  sjtan
#
# script for unitesting; guard for unit tests where unit uses gmPhraseWheel; fixup where version of wxPython doesn't allow
# a child widget to be multiply inserted (gmDemographics) ; try block for later versions of wxWidgets that might fail
# the Add (.. w,h, ... ) because expecting Add(.. (w,h) ...)
#
# Revision 1.42  2004/09/10 10:51:14  ncq
# - improve previous checkin comment
#
# Revision 1.41  2004/09/10 10:41:38  ncq
# - remove dead import
# - lots of cleanup (whitespace, indention, style, local vars instead of instance globals)
# - remove an extra sizer, waste less space
# - translate strings
# - from wxPython.wx import * -> from wxPython import wx
#   Why ? Because we can then do a simple replace wx.wx -> wx for 2.5 code.
#
# Revision 1.40  2004/08/24 14:29:58  ncq
# - some cleanup, not there yet, though
#
# Revision 1.39  2004/08/23 10:25:36  ncq
# - Richards work, removed pat photo, store column sizes
#
# Revision 1.38  2004/08/20 13:34:48  ncq
# - getFirstMatchingDBSet() -> getDBParam()
#
# Revision 1.37  2004/08/18 08:15:21  ncq
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
