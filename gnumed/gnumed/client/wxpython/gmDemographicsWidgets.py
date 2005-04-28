"""gmDemographics

 This panel will hold all the patients details

 @copyright: authors
 @dependencies: wxPython (>= version 2.3.1)
	28.07.2004 rterry gui-rewrite to include upper patient window
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmDemographicsWidgets.py,v $
# $Id: gmDemographicsWidgets.py,v 1.13 2005-04-28 16:58:45 cfmoro Exp $
__version__ = "$Revision: 1.13 $"
__author__ = "R.Terry, SJ Tan, I Haywood, Carlos Moro <cfmoro1976@yahoo.es>"
__license__ = 'GPL (details at http://www.gnu.org)'

# standard library
import cPickle, zlib, shutil, time, string, sys, os

# 3rd party
from mx import DateTime
import wx
from wxPython.lib.mixins.listctrl import wxColumnSorterMixin, wxListCtrlAutoWidthMixin
from wxPython import wizard

# GnuMed specific
from Gnumed.wxpython import gmPlugin, gmPatientHolder, images_patient_demographics, images_contacts_toolbar16_16, gmPhraseWheel, gmCharacterValidator, gmGuiHelpers, gmDateTimeInput
from Gnumed.pycommon import  gmGuiBroker,  gmLog, gmDispatcher, gmSignals, gmCfg, gmWhoAmI, gmI18N, gmMatchProvider
from Gnumed.business import gmDemographicRecord, gmPerson

# constant defs
_log = gmLog.gmDefLog
_whoami = gmWhoAmI.cWhoAmI()
_cfg = gmCfg.gmDefCfgFile

ID_Popup_OpenPatient = wx.NewId ()
ID_Popup_SaveDisplayLayout = wx.NewId()
ID_Popup_AddPerson = wx.NewId()
ID_Popup_AddAddressForPerson = wx.NewId()
ID_Popup_AddFamilyMember = wx.NewId()
ID_Popup_DeletePerson = wx.NewId()
ID_Popup_DeleteAddressForPerson = wx.NewId()
ID_Popup_UndoDelete = wx.NewId()
ID_Popup_SortA_Z = wx.NewId()
ID_Popup_SortZ_A = wx.NewId()
ID_Popup_ChangeFont = wx.NewId()
ID_Popup_SaveDisplayLayout = wx.NewId()
ID_Popup_BuildSQL= wx.NewId()
ID_Popup_Help = wx.NewId()
#ID_Popup_AddPerson 3 = wx.NewId()
#ID_Popup_AddPerson 4 = wx.NewId()


ID_PATIENT = wx.NewId()
ID_PATIENTSLIST = wx.NewId()
ID_ALL_MENU  = wx.NewId()
ID_ADDRESSLIST = wx.NewId()
ID_NAMESLIST = wx.NewId()
ID_CURRENTADDRESS = wx.NewId()
ID_COMBOTITLE = wx.NewId()
ID_COMBOSEX = wx.NewId()
ID_COMBOMARITALSTATUS = wx.NewId()
ID_COMBONOKRELATIONSHIP = wx.NewId()
ID_TXTSURNAME = wx.NewId()
ID_TXTFIRSTNAME = wx.NewId()
ID_TXTSALUTATION = wx.NewId()
ID_TXTSTREET = wx.NewId()
ID_TXTSUBURB = wx.NewId()
ID_TXTSTATE = wx.NewId()
ID_TXTPOSTCODE = wx.NewId()
ID_TXTBIRTHDATE = wx.NewId()
ID_TXTCOUNTRYOFBIRTH = wx.NewId()
ID_TXTOCCUPATION = wx.NewId()
ID_TXTNOKADDRESS = wx.NewId()
ID_TXTHOMEPHONE = wx.NewId()
ID_TXTWORKPHONE = wx.NewId()
ID_TXTFAX = wx.NewId()
ID_TXTEMAIL = wx.NewId()
ID_TXTINTERNET = wx.NewId()
ID_TXTMOBILE = wx.NewId()
ID_TXTMEMO = wx.NewId()
ID_LISTADDRESSES = wx.NewId()
ID_BUTTONBROWSENOK = wx.NewId()
ID_BUTTONAQUIRE = wx.NewId()
ID_BUTTONPHOTOEXPORT = wx.NewId()
ID_BUTTONPHOTOIMPORT = wx.NewId()
ID_BUTTONPHOTODELETE = wx.NewId()
ID_CHKBOXRESIDENCE = wx.NewId()
ID_CHKBOXPOSTAL = wx.NewId()
ID_CHKBOXPREFERREDALIAS = wx.NewId()
ID_BUTTONFINDPATIENT = wx.NewId()
ID_TXTPATIENTFIND = wx.NewId()
ID_TXTPATIENTAGE = wx.NewId()
ID_TXTPATIENTALLERGIES  = wx.NewId()
ID_TXTNOK =wx.NewId()
ID_TOOLBAR = wx.NewId ()
ID_TOOL_FIND = wx.NewId ()
ID_TOOL_NEW = wx.NewId ()
ID_TOOL_SAVE = wx.NewId ()
ID_CHECK_SPLIT=wx.NewId()
ID_TOOL_TEXT = wx.NewId ()
ID_LIST = wx.NewId ()
# PatientData = {
# 1 : ("Macks", "Jennifer","Flat9/128 Brook Rd","NEW LAMBTON HEIGHTS", "2302","19/01/2003","M"," 02 49 5678890"),
# 2 : ("Smith","Michelle", "Flat9/128 Brook Rd","ELERMORE VALE", "2302","23/02/1973","F", "02 49564320"),
# 3 : ("Smitt", "Francis","29 Willandra Crescent", "WINDALE"," 2280","18/08/1952","M","02 7819292"),
# 4 : ("Smythe-Briggs", "Elizabeth","129 Flat Rd", "SMITHS LAKE","2425","04/12/1918","F","02 4322222"),
# }

#-----------------------------------------------------------
#text control class to be later replaced by the gmPhraseWheel
#------------------------------------------------------------
class TextBox_RedBold(wx.TextCtrl):
	def __init__ (self, parent, id): #, wx.PyDefaultPostion, wx.DefaultSize):
		wx.TextCtrl.__init__(self,parent,id,"",wx.DefaultPosition, wx.DefaultSize,wx.SIMPLE_BORDER)
		self.SetForegroundColour(wx.Color(255,0,0))
		self.SetFont(wx.Font(12,wx.SWISS,wx.NORMAL, wx.BOLD,False,''))

class BlueLabel_Normal(wx.StaticText):
	def __init__(self, parent, id, prompt, text_alignment):
		wx.StaticText.__init__(self,parent, id,prompt,wx.DefaultPosition,wx.DefaultSize,text_alignment)
		self.SetFont(wx.Font(10,wx.SWISS,wx.NORMAL,wx.NORMAL,False,''))
		self.SetForegroundColour(wx.Colour(0,0,131))

class BlueLabel_Bold(wx.StaticText):
	def __init__(self, parent, id, prompt, text_alignment):
		wx.StaticText.__init__ (
			self,
			parent,
			id,
			prompt,
			wx.DefaultPosition,
			wx.DefaultSize,
			text_alignment
		)
		self.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD, False, ''))
		self.SetForegroundColour (wx.Colour(0,0,255))

class TextBox_BlackNormal(wx.TextCtrl):
	def __init__ (self, parent, id): #, wx.DefaultPosition, wx.DefaultSize):
		wx.TextCtrl.__init__(self,parent,id,"",wx.DefaultPosition, wx.DefaultSize,wx.SIMPLE_BORDER)
		self.SetForegroundColour(wx.Color(0,0,0))
		self.SetFont(wx.Font(12,wx.SWISS,wx.NORMAL,wx.NORMAL,False,''))


class SmartCombo (wx.ComboBox):
	def __init__ (self, parent, _map):
		self.map = _map
		self.pam = dict ([(str(y),x) for x, y in _map.items()])
		wx.ComboBox.__init__ (
			self,
			parent,
			-1,
			"",
			wx.DefaultPosition,
			wx.DefaultSize,
			self.pam.keys(),
			wx.CB_DROPDOWN
		)

	def SetValue (self, value):
		if not value:
			wx.ComboBox.SetValue (self, '')
		else:
			self.SetSelection (self.FindString (self.pam[value]))

	def GetValue (self):
		# Call parent class method (avoid recursive loop using validator)
		# and return empty string when no option was selected
		return self.map.get(wx.ComboBox.GetValue (self),'')

		
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
#		- This sits on a wx.BoxSizer(wx.HORIZONTAL) self.sizer_for_patientlist
#	Underneath this all the textboxes for data entry
#		- These are loaded into a gridsizer self.gs
#	Both these sizers sit on self.sizer_main.
#		- self.sizer_for_patientlist expands vertically and horizontally
#		- self.gs expands horizontally but not vertically
#---------------------------------------------------------------------------------------------------------
class Demographics(wx.Panel):

	def __init__(self, parent, id= -1):
		wx.Panel.__init__ (
			self,
			parent,
			id,
			wx.DefaultPosition,
			wx.DefaultSize,
			wx.NO_BORDER | wx.TAB_TRAVERSAL
		)
		self.gb = gmGuiBroker.GuiBroker()
		self.__createdemographicgui()	#draw the user interface
		self.__connect ()
		#self.__add_character_validators()
 		#self._updateUI()

	def  __createdemographicgui(self):
		#-----------------------------------------------------------
		#   top level page layout:
		#  --------------------------------------
		# | patient search multiple results list |
		# |--------------------------------------
		# |	  patient data entry are		  |
		#  --------------------------------------
		self.main_splitWindow = wx.SplitterWindow( self, -1, point = wx.DefaultPosition,  size = wx.DefaultSize, style=wx.SP_3DSASH)
		self.patientDetailWin = DemographicDetailWindow(self.main_splitWindow)
		self.patientListWin = PatientListWindow(self.main_splitWindow, self, ID_LIST, on_click=self.patientDetailWin.load_identity)
		self.main_splitWindow.SetMinimumPaneSize(20)
		self.main_splitWindow.SplitHorizontally( self.patientListWin, self.patientDetailWin, 80)

		self.main_splitWindow.SplitHorizontally( self.patientListWin, self.patientDetailWin)
		# toolbar
		self.toolbar = wx.ToolBar (self, ID_TOOLBAR, style=wx.TB_FLAT | wx.TB_DOCKABLE)
		self.id_search = wx.TextCtrl (self.toolbar, ID_TOOL_TEXT, style=wx.TE_PROCESS_ENTER )
		self.toolbar.AddControl (self.id_search)
		#  - details button
		self.toolbar.AddLabelTool (ID_TOOL_FIND, _("Find"), gmGuiHelpers.gm_icon (_('binoculars_form')), shortHelp = _("Find a person in the database"))
		self.toolbar.AddSeparator ()
		self.toolbar.AddLabelTool (ID_TOOL_NEW, _("New"), gmGuiHelpers.gm_icon (_('oneperson')), shortHelp = _("Create a new patient"))
		self.toolbar.AddLabelTool (ID_TOOL_SAVE, _("Save"), gmGuiHelpers.gm_icon (_('save')), shortHelp = _("Save the current patient"))
		# FIXME: add other toolbar items here
		self.sizer_main = wx.BoxSizer(wx.VERTICAL)
		self.sizer_main.Add (self.toolbar, 0, wx.EXPAND)
		self.sizer_main.Add(self.main_splitWindow, 10, wx.EXPAND | wx.ALL)

		# adjust layout
		self.SetSizer(self.sizer_main)
#		self.SetSizer( self.main_splitWindow)
		self.SetAutoLayout(True)
		self.sizer_main.Fit(self)
	
		self.inList = 0
		self.preferredListSashPos = 0.8
		self.preferredDetailSashPos = 0.3

	def __connect (self):	
		wx.EVT_TOOL (self.toolbar, ID_TOOL_FIND, self._on_search)
		wx.EVT_TEXT_ENTER (self.id_search, ID_TOOL_TEXT, self._on_search)
		wx.EVT_TOOL (self.toolbar, ID_TOOL_SAVE, self.patientDetailWin.on_save )
		wx.EVT_TOOL (self.toolbar, ID_TOOL_NEW, self.on_new )
		
	def _on_search (self, event):
		try:
			srcher = gmPerson.cPatientSearcher_SQL ()
			results = srcher.get_identities (self.id_search.GetValue ())
			self.patientListWin.ClearAll ()
			if not results:
				self.patientListWin.on_search_failed ()
			else:
				self.patientListWin.on_search (results)
		except:
			_log.LogException ("patient search", sys.exc_info (), verbose=0)
	#-----------------------------------------------------------
	def on_new (self, event):
		try:
			self.patientListWin.ClearAll ()
			self.id_search.Clear ()
			self.patientDetailWin.on_new ()
		except:
			_log.LogException ("patient new", sys.exc_info (), verbose=0)
		
class PatientListWindow(wx.ListCtrl):		
#E	, gmPatientHolder.PatientHolder):
#		# FIXME: remove
#		gmPatientHolder.PatientHolder.__init__(self)

	def __init__(self, parent, main_window, id= -1, on_click=None):
		wx.ListCtrl.__init__ (
			self, parent, id,
			pos = wx.DefaultPosition,
			size = wx.Size (400,10),
			style = wx.LC_REPORT | wx.SUNKEN_BORDER | wx.LC_VRULES | wx.LC_HRULES
		)
		opt_val, set = gmCfg.getDBParam(
			workplace = _whoami.get_workplace(),
			option="widgets.demographics.patientlist.column_sizes"
		)
		self.main_window = main_window
		self.patientcolumns = {_('Name'):100, _('Address'):250, _("Home Phone"):60, _("Sex"):50, _("Date of Birth"):60}
		if opt_val and len(opt_val):
			self.patientcolumns.update (dict ([i.split (':') for i in opt_val]))
		self.patientlist = self
		self.__register_events ()
		self.on_click = on_click

	def __register_events(self):
		# patient list popup menu
		wx.EVT_RIGHT_UP(self.patientlist, self._on_RightClick_patientlist)
		wx.EVT_LIST_ITEM_ACTIVATED (self.patientlist, self.GetId (), self._on_list_click)
		wx.EVT_MENU(self, ID_Popup_OpenPatient, self._on_Popup_OpenPatient)
		wx.EVT_MENU(self, ID_Popup_SaveDisplayLayout, self._on_PopupSaveDisplayLayout)
		wx.EVT_MENU(self, ID_Popup_AddPerson , self.main_window.on_new)
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

	def _on_RightClick_patientlist(self, event):
		"""
 		Maximise Viewing Area
 		Minimise Viewing Area
 		---------------------
 		Add Person
 		Add Address for person
 		Add Family Member
 		--------------------------
 		Delete Person
 		Delete Address for person
 		Undo Delete
 		------------------------------------
 		Sort A_Z
 		Sort Z_A
 		--------------
 		Change Font
 		Save Display Layout
 		--------------------------
 		Build SQL
 		-------------------
 		Help
 		----------------
 		Exit
		"""

		#-----------------------------------------------------------------
		# make a menu to popup over the patient list
		#-----------------------------------------------------------------
		self.menu_patientlist = wx.Menu()
		#Trigger routine to open new patient
		item = wx.MenuItem(self.menu_patientlist, ID_Popup_OpenPatient ,"Open As Patient")
		item.SetBitmap(images_patient_demographics.getperson_addBitmap())
		self.menu_patientlist.AppendItem(item)
		#Trigger routine to clear all textboxes to add entirely new person
		item = wx.MenuItem(self.menu_patientlist, ID_Popup_AddPerson ,"Add Person")
		item.SetBitmap(images_patient_demographics.getperson_addBitmap())
		self.menu_patientlist.AppendItem(item)

		#Trigger routine to clear all address textboxes only to add another address
		item = wx.MenuItem(self.menu_patientlist, ID_Popup_AddAddressForPerson, "Add Address for person")
		item.SetBitmap(images_patient_demographics.getbranch_addBitmap())
		self.menu_patientlist.AppendItem(item)
		#Trigger routine to clear person details, leave address, home phone
		item = wx.MenuItem(self.menu_patientlist, ID_Popup_AddFamilyMember,"Add Family Member")
		item.SetBitmap(images_patient_demographics.getemployeesBitmap())
		self.menu_patientlist.AppendItem(item)
		self.menu_patientlist.AppendSeparator()
		#Trigger routine to delete a person
		item = wx.MenuItem(self.menu_patientlist, ID_Popup_DeletePerson,"Delete Person")
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
		item = wx.MenuItem(self.menu_patientlist, ID_Popup_SortA_Z,"Sort A_Z")
		item.SetBitmap(images_patient_demographics.getsort_A_ZBitmap())
		self.menu_patientlist.AppendItem(item)

		item = wx.MenuItem(self.menu_patientlist, ID_Popup_SortZ_A,"Sort Z_A")
		item.SetBitmap(images_patient_demographics.getsort_Z_ABitmap())
		self.menu_patientlist.AppendItem(item)
		self.menu_patientlist.AppendSeparator()

		self.menu_patientlist.Append(ID_Popup_ChangeFont, "Change Font")

		self.menu_patientlist.Append(ID_Popup_SaveDisplayLayout, "Save Display Layout")
		#self.menu_patientlist.AppendItem(item)
		self.menu_patientlist.AppendSeparator()
		#Save search query to database as user defined query
		item = wx.MenuItem(self.menu_patientlist,ID_Popup_BuildSQL, "Build SQL")
		item.SetBitmap(images_patient_demographics.getsqlBitmap())
		self.menu_patientlist.AppendItem(item)
		self.menu_patientlist.AppendSeparator()
		#Jump to help for patients_list
		item = wx.MenuItem(self.menu_patientlist, ID_Popup_Help,  "Help")
		item.SetBitmap(images_patient_demographics.gethelpBitmap())
		self.menu_patientlist.AppendItem(item)
		self.menu_patientlist.AppendSeparator()
		# Popup the menu.  If an item is selected then its handler
		# will be called before PopupMenu returns.
		self.PopupMenu(self.menu_patientlist, event.GetPosition())
		self.menu_patientlist.Destroy()

	def _on_list_click (self, event):
		try:
			if self.on_click:
				self.on_click (self.ids_in_list[event.GetIndex ()])
		except:
			_log.LogException ("loading patient", sys.exc_info (), verbose=0)

	def _on_Popup_OpenPatient (self, event):
		sel = self.patientlist.GetNextItem (-1, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
		if sel > -1:
			self.__load_patient (self.ids_in_list[sel])

	def __load_patient (self, patient):
		wx.BeginBusyCursor ()
		try:
			gmPatient.set_active_patient (patient)
		except:
			_log.LogException ("loading patient %d" % patient['id'], sys.exc_info (), verbose=0)
		wx.EndBusyCursor ()

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
		self.curClr = wx.BLACK
		print 'Selecting font list'
		data = wx.FontData()
		data.EnableEffects(True)
		data.SetColour(self.curClr)		 # set colour
		data.SetInitialFont(self.curFont)

		dlg = wx.FontDialog(self, data)
		if dlg.ShowModal() == wx.ID_OK:
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
		wx.BeginBusyCursor()
		pat_cols_widths = []										#create empty list
		for col in range (0, self.patientlist.GetColumnCount()): 			# get widths of columns
			pat_cols_widths.append(self.patientlist.GetColumnWidth(col))		# add to the list
		gmCfg.setDBParam (										# set the value for the current user/workplace
			workplace = _whoami.get_workplace(),
			option = "widgets.demographics.patientlist.column_sizes",
			value = pat_cols_widths
		)
		wx.EndBusyCursor()
	#----------------------------------------------------------
	def on_search_failed (self):
		self.patientlist.ClearAll ()
		self.patientlist.InsertStringItem (0, _("no results found"))
	#----------------------------------------------------------
	def on_search (self, ids, display_fields = ['name', 'dob', 'home_address', 'gender', 'home_phone']):
		"""
		Receives a list of gmPerson.cIdentity objects to display
		"""
		n = 0
		self.patientlist.ClearAll ()
		trans = {'name':_('Name'), 'home_address':_('Address'), 'gender':_('Sex'), 'home_phone':_('Home Phone'), 'dob':_("Date of Birth")}
		for i in display_fields:
			if i in ['dob', 'gender', 'home_phone']:
				self.patientlist.InsertColumn (n, trans[i], wx.LIST_FORMAT_CENTRE)
			else:
				self.patientlist.InsertColumn (n, trans[i])
			self.patientlist.SetColumnWidth(n,int(self.patientcolumns[trans[i]]))
			n+=1
		try:
			for i in range (0, len (ids)):
				self.patientlist.InsertStringItem (i, getattr (self, '_form_%s' % display_fields[0]) (ids[i]))
				for j in range (1, len (display_fields)):
					self.patientlist.SetStringItem (i, j, getattr (self, '_form_%s' % display_fields[j]) (ids[i]))
		except:
			_log.LogException ("inserting into listbox", sys.exc_info (), verbose=0)
		self.ids_in_list = ids

	def _form_name (self, i):
		return "%(lastnames)s, %(firstnames)s" % i

	def _form_home_address (self, i):
		for a in i['addresses']:
			if a['type'] == _('home'):
				return _("%(number)s %(street)s %(addendum)s, %(city)s %(postcode)s") % a
		if i['addresses']:
			return _("%(number)s %(street)s %(addendum)s, %(city)s %(postcode)s") % i['addresses'][0]
		return _("[No address recorded]")

	def _form_gender (self, i):
		return i['gender']

	def _form_dob (self, i):
		return i['dob'].Format (_("%d/%m/%y"))

	def _form_home_phone (self, i):
		for c in i['comms']:
			if c['type'] == 'telephone':
				return c['url']
		return _("No telephone")
	
class DemographicDetailWindow(wx.Panel):
	"""
	A window showing demographic details
	"""
	def __init__(self, parent, id= -1, listen=False):
		"""
		@param listen: if True, this widget will respond to
		new patient event and load the new patient's demographic details
		"""
		wx.Panel.__init__ (
			self,
			parent,
			id,
			wx.DefaultPosition,
			wx.DefaultSize,
			wx.NO_BORDER | wx.TAB_TRAVERSAL
		)
		self.to_delete = []
		self.addr_cache = []
		self.comm_channel_names = gmDemographicRecord.getCommChannelTypes()
		self.gendermap = {
			_('Male'): 'm',
			_("Female"): 'f',
			_("Unknown"): '?',
			_('Transexual to Male'): 'tm',
			_('Transexual to Female'): 'tf',
			_('Hermaphrodite'): 'h'
		}
		self.__createdemographicgui()
		#self.__connect ()
		if listen:
			gmDispatcher.connect (self._on_patient_selected, gmSignals.patient_selected ())

		
	def  __createdemographicgui(self):
		lbl_space = BlueLabel_Normal(self,-1,"",wx.LEFT) #This lbl_space is used as a spacer between label


		#-------------------------------------------------------------------
		#Add surname, firstname, title, sex, salutation
		#-------------------------------------------------------------------
		lbl_surname = BlueLabel_Normal(self,-1, _("Surname"), wx.LEFT)
		lbl_title = BlueLabel_Normal(self,-1, _("Title"), wx.ALIGN_CENTRE)
		self.lastnames = TextBox_RedBold(self,-1)
		self.title = TextBox_RedBold (self, -1)
		sizer_line1 = wx.BoxSizer(wx.HORIZONTAL)  		 #holds surname label + textbox, title label and combobox
		sizer_line1.Add(lbl_surname,3,wx.EXPAND|wx.TOP|wx.BOTTOM,1)
		sizer_line1.Add(self.lastnames,5,wx.EXPAND|wx.TOP|wx.BOTTOM,1)
		sizer_line1.Add(lbl_title,3,wx.EXPAND|wx.TOP|wx.BOTTOM,1)
		sizer_line1.Add(self.title,5,wx.EXPAND|wx.TOP|wx.BOTTOM,1)

		lbl_firstname = BlueLabel_Normal(self,-1, _("Firstname"), wx.LEFT)
		self.firstnames = TextBox_RedBold(self,-1)
		lbl_sex = BlueLabel_Normal(self,-1, _("Sex"), wx.ALIGN_CENTRE)
		self.gender = SmartCombo (self, self.gendermap)
		lbl_preferredname =  BlueLabel_Normal(self,-1, _("Salutation"), wx.LEFT)
		self.preferred = TextBox_RedBold(self,-1)
		sizer_line2 = wx.BoxSizer(wx.HORIZONTAL)  		#holds firstname label + textbox, sex label + combobox
		sizer_line2.Add(lbl_firstname,3,wx.EXPAND|wx.TOP|wx.BOTTOM,1)
		sizer_line2.Add(self.firstnames,5,wx.EXPAND|wx.TOP|wx.BOTTOM,1)
		sizer_line2.Add(lbl_sex,3,wx.EXPAND|wx.TOP|wx.BOTTOM,1)

		#-----------------------------------------------------------------------------------
		#now add gui-elements to sizers for surname to salutation
		#each line has several (up to 4 elements
		# e.g surname <textbox> title <textbox> etc
		#-----------------------------------------------------------------------------------

		sizer_line2.Add(self.gender,5,wx.EXPAND|wx.TOP|wx.BOTTOM,1)
		sizer_line3 = wx.BoxSizer(wx.HORIZONTAL)		#holds preferredname label and textbox
		sizer_line3.Add(lbl_preferredname,3,wx.EXPAND|wx.TOP|wx.BOTTOM,1)
		sizer_line3.Add(self.preferred,5,wx.EXPAND|wx.TOP|wx.BOTTOM,1)
		sizer_line3.Add(lbl_space,8,wx.EXPAND|wx.TOP|wx.BOTTOM,1)
		#--------------------------------------------------------------------------
		#The heading for 'Address, sits on its own box sizer
		#--------------------------------------------------------------------------
		lbl_heading_address = BlueLabel_Bold(self,-1, _("Addresses"), wx.ALIGN_CENTRE)
		sizer_lbl_heading_address = wx.BoxSizer(wx.HORIZONTAL)   #holds address heading
		sizer_lbl_heading_address.Add(lbl_space,1,wx.EXPAND|wx.TOP|wx.BOTTOM,1)
		sizer_lbl_heading_address.Add(lbl_heading_address,1,wx.EXPAND|wx.TOP|wx.BOTTOM,1)
		lbl_space2 = BlueLabel_Normal(self,-1,"",wx.LEFT) #This lbl_space is used as a spacer between label
		sizer_lbl_heading_address.Add(lbl_space2,1,wx.EXPAND|wx.TOP|wx.BOTTOM,1)
		self.addresslist = wx.ListBox (self, -1, size= wx.Size (-1,100))
		sizer_addresslist = wx.BoxSizer (wx.HORIZONTAL)
		sizer_addresslist.Add (self.addresslist, 1, wx.EXPAND)
		self.btn_addr_add = wx.Button (self, -1, _("Add"))
		self.btn_addr_del = wx.Button (self, -1, _("Del"))
		sizer_addr_btn = wx.BoxSizer (wx.VERTICAL)
		sizer_addr_btn.Add (self.btn_addr_add, 0)
		sizer_addr_btn.Add ((0, 0), 2)
		sizer_addr_btn.Add (self.btn_addr_del, 0)
		sizer_addresslist.Add (sizer_addr_btn, 0, wx.EXPAND)
		#---------------------------------------------------------------------
		#Contact details - phone work, home,fax,mobile,internet and email
		#--------------------------------------------------------------------
		lbl_contact_heading = BlueLabel_Bold (self, -1, _("Contacts"), wx.LEFT)
		sizer_contacts_line1 = wx.BoxSizer (wx.HORIZONTAL)
		lbl_space = BlueLabel_Normal(self,-1,"",wx.LEFT) #This lbl_space is used as a spacer between label
		sizer_contacts_line1 .Add(lbl_space,1,wx.EXPAND|wx.TOP|wx.BOTTOM,1)
		lbl_space = BlueLabel_Normal(self,-1,"",wx.LEFT) #This lbl_space is used as a spacer between label
		sizer_contacts_line1 .Add(lbl_space,1,wx.EXPAND)
		sizer_contacts_line1 .Add(lbl_contact_heading,1,wx.EXPAND|wx.TOP|wx.BOTTOM,1)
		lbl_space = BlueLabel_Normal(self,-1,"",wx.LEFT) #This lbl_space is used as a spacer between label
		sizer_contacts_line1 .Add(lbl_space,1,wx.EXPAND|wx.TOP|wx.BOTTOM,1)

		#-----------------------------------------------------------------------
		#Now add all the lines for the left side of the screen on their sizers
		# to sizer_leftside
		#i.e Patient Names through to their contact details
		#--------------------------------------------------------------------
		sizer_leftside = wx.BoxSizer(wx.VERTICAL)
		sizer_leftside.Add(sizer_line1, 0, wx.EXPAND)
		sizer_leftside.Add(sizer_line2, 0, wx.EXPAND)
		sizer_leftside.Add(sizer_line3, 0, wx.EXPAND)
		sizer_leftside.Add(sizer_lbl_heading_address, 0, wx.EXPAND)
		sizer_leftside.Add(sizer_addresslist, 0, wx.EXPAND)
		sizer_leftside.Add(sizer_contacts_line1, 0, wx.EXPAND)

		self.contacts_map = gmDemographicRecord.getCommChannelTypes ()
		self.contacts_pam = dict([(y, x) for x, y in self.contacts_map.items ()])
		self.contacts_widgets = {}
		toggle = True
		l = self.contacts_pam.keys ()
		l.sort ()
		for i in l:
			if toggle:
				sizer_contacts_line = wx.BoxSizer(wx.HORIZONTAL)
			lbl = BlueLabel_Normal(self,-1, self.contacts_pam[i], wx.LEFT)
			self.contacts_widgets[i] = TextBox_BlackNormal(self,-1)
			sizer_contacts_line.Add(lbl,3,wx.EXPAND|wx.TOP|wx.BOTTOM,1)
			sizer_contacts_line.Add(self.contacts_widgets[i],5,wx.EXPAND|wx.TOP|wx.BOTTOM,1)
			if not toggle:
				sizer_leftside.Add(sizer_contacts_line, 0, wx.EXPAND)
			toggle = not toggle
		if not toggle:
			sizer_contacts_line.Add ((0,0), 8)
			sizer_leftside.Add(sizer_contacts_line, 0, wx.EXPAND)
		#-----------------------------------------------------------
		#   right-hand size of bottom half:
		#  ----------------------------------------------
		# | DOB: __________  marital status: ___________ |
		# | occupation: ________________________________ |
		# | country of birth: __________________________ |
		# |		   Next Of Kin						|
		# | details: ___________________________________ |
		# |		  ___________________________________ |
		# | relationship: ______________________________ |
		# |	   .-------------------.				  |
		# |	   | browse DB for NOK |				  |
		# |	   `-------------------'				  |
		# |		 External IDs						 |
		# |											  |
		#  ----------------------------------------------
		#-----------------------------------------------------------

		# dob | marital status
		lbl_dob = BlueLabel_Normal(self,-1, _("Birthdate"), wx.LEFT)
		self.txt_dob = TextBox_BlackNormal(self,-1)
		lbl_maritalstatus = BlueLabel_Normal(self,-1, _("Marital Status"), wx.ALIGN_CENTER)
		self.pk_marital_status = SmartCombo (self, gmDemographicRecord.getMaritalStatusTypes())
		sizer_dob_marital = wx.BoxSizer(wx.HORIZONTAL)
		sizer_dob_marital.Add(lbl_dob, 3, wx.EXPAND)
		sizer_dob_marital.Add(self.txt_dob, 5, wx.EXPAND)
		sizer_dob_marital.Add(lbl_maritalstatus, 3, wx.EXPAND)
		sizer_dob_marital.Add(self.pk_marital_status, 5, wx.EXPAND)

		# occupation
		lbl_job = BlueLabel_Normal(self, -1, _("Occupation"), wx.LEFT)
		self.occupation = gmPhraseWheel.cPhraseWheel (
			parent = self,
			id = -1,
			aMatchProvider = gmDemographicRecord.OccupationMP(),
			pos = wx.DefaultPosition,
			size = wx.DefaultSize
		)
		sizer_job = wx.BoxSizer(wx.HORIZONTAL)
		sizer_job.Add(lbl_job, 3, wx.EXPAND)
		sizer_job.Add(self.occupation, 13, wx.EXPAND)

  		# country of birth
		lbl_countryofbirth = BlueLabel_Normal(self, -1, _("Born In"), wx.LEFT)
		self.cob = gmPhraseWheel.cPhraseWheel (
			parent = self,
			id = -1,
			aMatchProvider = gmDemographicRecord.CountryMP(),
			selection_only = 1,
			pos = wx.DefaultPosition,
			size = wx.DefaultSize
		)
		sizer_countryofbirth = wx.BoxSizer(wx.HORIZONTAL)
		sizer_countryofbirth.Add(lbl_countryofbirth, 3, wx.EXPAND)
		sizer_countryofbirth.Add(self.cob, 13, wx.EXPAND)

		# NOK
		lbl_nok_heading = BlueLabel_Bold(self, -1, _("Next of Kin"), wx.ALIGN_CENTER)
		# NOK name/address
		lbl_nok_details = BlueLabel_Normal(self, -1, _("NOK Details"), wx.LEFT)
		self.lb_nok = wx.ListBox (
			self,
			ID_TXTNOK,
			size=(-1,50)
		)
		sizer_nok_name_addr = wx.BoxSizer(wx.HORIZONTAL)
		sizer_nok_name_addr.Add(lbl_nok_details, 3, wx.EXPAND)
		sizer_nok_name_addr.Add(self.lb_nok, 13, wx.EXPAND)

		# NOK relationship/phone
		lbl_relationshipNOK = BlueLabel_Normal(self, -1, _("Relationship"), wx.LEFT)
		# FIXME: get from database
		self.combo_relationshipNOK = SmartCombo (self, gmDemographicRecord.getRelationshipTypes ())
		sizer_nok_relationship = wx.BoxSizer(wx.HORIZONTAL)
		sizer_nok_relationship.Add(lbl_relationshipNOK, 3, wx.EXPAND)
		sizer_nok_relationship.Add(self.combo_relationshipNOK, 13, wx.EXPAND)

		# NOK browse DB
		self.btn_nok_search = wx.Button(self, -1, _("Browse for Next Of Kin Details"))
		sizer_search_nok = wx.BoxSizer(wx.HORIZONTAL)
		sizer_search_nok.Add(lbl_space, 3, wx.EXPAND)
		sizer_search_nok.Add(self.btn_nok_search, 13, wx.EXPAND)

		#-----------------------------------------------------------------------------
		# undecided - in AU example need medicare/repatriation/pharmaceutical benefits
		# Liz Dodd says: DVA-Gold DVA-White(specified illness) DVA-RED/ORANGE (medications only)
		#	Health care card/Seniors Health Care Card Pension Card Pharmaceutical Benefits Safety Net Number
		#-----------------------------------------------------------------------------
		lbl_id_numbers = BlueLabel_Bold(self, -1, _("Cards etc"), wx.ALIGN_CENTER)

		# stack lines atop each other
		sizer_rightside = wx.BoxSizer(wx.VERTICAL)
#		sizer_rightside.Add(0,10,0)
		sizer_rightside.Add(sizer_dob_marital, 0, wx.EXPAND)
		sizer_rightside.Add(sizer_job, 0, wx.EXPAND)
		sizer_rightside.Add(sizer_countryofbirth, 0, wx.EXPAND)
		sizer_rightside.Add(lbl_nok_heading, 0, wx.EXPAND)
		sizer_rightside.Add(sizer_nok_name_addr, 0, wx.EXPAND)
		sizer_rightside.Add(sizer_nok_relationship, 0, wx.EXPAND)
		sizer_rightside.Add(sizer_search_nok, 0, wx.EXPAND)
		sizer_rightside.Add(lbl_id_numbers, 0, wx.EXPAND)

		# external ID auto-generated widgets
		self.ext_id_map = gmDemographicRecord.getExtIDTypes ()
		self.ext_id_pam = dict([(y, x) for x, y in self.ext_id_map.items ()])
		self.ext_id_widgets = {}
		toggle = True
		l = self.ext_id_pam.keys ()
		l.sort ()
		for i in l:
			if toggle:
				sizer_ext_id_line = wx.BoxSizer(wx.HORIZONTAL)
			lbl = BlueLabel_Normal(self,-1, self.ext_id_pam[i], wx.LEFT)
			self.ext_id_widgets[i] = TextBox_BlackNormal(self,-1)
			sizer_ext_id_line.Add(lbl,3,wx.EXPAND|wx.TOP|wx.BOTTOM,1)
			sizer_ext_id_line.Add(self.ext_id_widgets[i],5,wx.EXPAND|wx.TOP|wx.BOTTOM,1)
			if not toggle:
				sizer_rightside.Add(sizer_ext_id_line, 0, wx.EXPAND)
			toggle = not toggle
		if not toggle:
			sizer_ext_id_line.Add((0,0), 8)
			sizer_rightside.Add(sizer_ext_id_line, 0, wx.EXPAND)
		#-----------------------------------------------------------
		#   bottom half of screen:
		#  ------------------------
		# | demographics | details |
		#  ------------------------
		sizer_bottom_patient_dataentry = wx.BoxSizer(wx.HORIZONTAL)
		sizer_bottom_patient_dataentry.Add(sizer_leftside, 1, wx.EXPAND | wx.RIGHT, 5)
		sizer_bottom_patient_dataentry.Add(sizer_rightside, 1, wx.EXPAND)

		self.SetSizer(sizer_bottom_patient_dataentry)
		self.SetAutoLayout(True)
		sizer_bottom_patient_dataentry.Fit(self)


 	def __connect (self):
 		b = self.btn_addr_add
 		wx.EVT_BUTTON(b, b.GetId() , self._add_address_pressed)
 		b = self.btn_addr_del
 		wx.EVT_BUTTON(b, b.GetId() ,  self._del_address_pressed)

 		l = self.addresslist
 		#wx.EVT_LISTBOX_DCLICK(l, l.GetId(), self._address_selected)

 		#wx.EVT_BUTTON(self.btn_photo_import, self.btn_photo_import.GetId (), self._photo_import)
 		#wx.EVT_BUTTON(self.btn_photo_export, self.btn_photo_export.GetId (), self._photo_export)



	def _address_selected( self, event):
		#IAN TO RECONNECT
 		self._update_address_fields_on_selection()

	def __urb_set (self, id_urb):
		state, postcode = gmDemographicRecord,getUrb (id_urb)
		self.txt_state.SetValue (state)
		self.txt_postcode.SetValue (postcode)

	def __street_set (self, id_street):
		state, postcode, urb = gmDemographicRecord (id_street)
		self.txt_state.SetValue (state)
		self.txt_postcode.SetValue (postcode)
		self.txt_suburb.SetValue (urb)
		
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
		myPatient = self.patient.get_identity()
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



	def on_new(self):
		self.identity = None
		for x in ['firstnames', 'lastnames', 'title', 'preferred', 'pk_marital_status', 'occupation', 'gender', 'cob', 'txt_dob']:
			getattr (self, x).SetValue ('')

		for i in self.ext_id_widgets.values ():
			i.SetValue ('')

		for c in self.contacts_widgets.values ():
			c.SetValue ('')

		self.addresslist.Clear ()
		self.lb_nok.Clear ()


	def on_save(self):
		 #IAN TO RECONNECT
		m = self.input_fields
		self.value_map = self.get_input_value_map ()
		self.validate_fields()
		self._save_addresses()
		myPatient = self.patient.get_identity()
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
		try:
			data = self._get_address_data()
			self.add_address (data)
			self._update_address_list_display()
		except:
			_log.LogException ('failed on add address', sys.exc_info (), verbose=0)

	def _del_address_pressed(self, event):
		try:
			i = self.addresslist.GetSelection ()
			self.identity.delete_address (self.identity['addresses'][i])
			self._update_address_list_display()
		except:
			_log.LogException ('failed on delete address', sys.exc_info (), verbose=0)

	def _get_address_data(self):
		m = {}
		m['type'] = self.combo_address_type.GetValue ()
		m['number'] = self.txt_number.GetValue ()
		m['street'] = self.txt_street.GetValue ()
		m['urb'] = self.txt_suburb.GetValue ()
		m['postcode'] = self.txt_postcode.GetValue ()
		return m
	
	def __update_addresses(self):
		try:
			self.identity['addresses']
		except:
			_log.LogException ('failed to get addresses', sys.exc_info (), verbose=0)
		self.addresslist.Clear()
		for data in self.identity['addresses']:
			s = '%-10s - %s,%s,%s' % ( data['type'],  data['number'], data['street'], data['urb'])
			self.addresslist.Append(s, data)



	def __update_nok(self):
		self.lb_nok.Clear()
		for r, i in self.identity['relatives']:
			s = """%-12s   - %s, %s %s""" % (r, i['description'], _('born'), time.strftime('%d/%m/%Y', gmDemographicRecord.get_time_tuple(i['dob'])))
			self.lb_nok.Append (s, i)


	def _on_patient_selected (self, **kwargs):
		self.load_identity (kwargs['patient'].get_identity ())
		
	def load_identity (self, identity):
		self.identity = identity
		for x in ['firstnames', 'lastnames', 'title', 'preferred', 'pk_marital_status', 'gender']:
			getattr (self, x).SetValue (identity[x] or '')
		t = time.strftime('%d/%m/%Y', gmDemographicRecord.get_time_tuple(identity['dob']))
		self.txt_dob.SetValue(t)
		self.occupation.SetValue (";".join (identity['occupations']))
		self.cob.SetValue (gmDemographicRecord.getCountry (identity['cob']))
		w = {}
		for c in identity['ext_ids']:
			if c['comment']:
				s = "%(external_id)s (%(comment)s)" % c
			else:
				s = c['external_id']
			if w.has_key (c['id_type']):
				w[c['id_type']].append (s)
			else:
				w[c['id_type']] = [s]
		for i in w.keys ():
			self.ext_id_widgets[i].SetValue (";".join (w[i]))

		for c in identity['comms']:
			self.contacts_widgets[c['id_type']].SetValue (c['url'])		   
		self.__update_addresses()
		self.__update_nok()
#============================================================
class cBasicPatDetailsPage(wizard.wxWizardPageSimple):
	"""
	Wizard page for entering patient's basic demographic information
	"""
	def __init__(self, parent, title):
		"""
		Creates a new instance of BasicPatDetailsPage
		@param parent - The parent widget
		@type parent - A wxWindow instance
		@param tile - The title of the page
		@type title - A StringType instance				
		"""
		wizard.wxWizardPageSimple.__init__(self, parent) #, bitmap = gmGuiHelpers.gm_icon(_('oneperson'))

		# main panel (required for a correct propagation of validator calls)
		PNL_form = wx.Panel(self, -1)
		PNL_form.SetValidator(cBasicPatDetailsPageValidator())

		# FIXME: improve cTextObjectValidator to accept regexp (gender, telephones, etc).

		# first name
		STT_firstname = wx.StaticText(PNL_form, -1, _('First name'))
		STT_firstname.SetForegroundColour('red')
		cmd = """
select distinct firstnames, firstnames from names where firstnames %(fragment_condition)s
	union
select distinct name, name from name_gender_map where name %(fragment_condition)s
"""
		mp = gmMatchProvider.cMatchProvider_SQL2('demographics', cmd)
		mp.setThresholds(3, 5, 15)
		self.PRW_firstname = gmPhraseWheel.cPhraseWheel (
			parent = PNL_form,
			id = -1,
			aMatchProvider = mp,
			validator = gmGuiHelpers.cTextObjectValidator(required = True, only_digits = False)
		)
		self.PRW_firstname.SetToolTipString(_("surname/given name/first name"))
		# last name
		STT_lastname = wx.StaticText(PNL_form, -1, _('Last name'))
		STT_lastname.SetForegroundColour('red')
		cmd = "select distinct lastnames, lastnames from names where lastnames %(fragment_condition)s"
		mp = gmMatchProvider.cMatchProvider_SQL2('demographics', cmd)
		mp.setThresholds(3, 5, 15)
		self.PRW_lastname = gmPhraseWheel.cPhraseWheel (
			parent = PNL_form,
			id = -1,
			aMatchProvider = mp,
			validator = gmGuiHelpers.cTextObjectValidator(required = True, only_digits = False)
		)
		self.PRW_lastname.SetToolTipString(_("last name, family name"))
		# nickname
		STT_nick = wx.StaticText(PNL_form, -1, _('Nick name'))
		cmd = """
select distinct preferred, preferred from names where preferred %(fragment_condition)s
	union
select distinct firstnames, firstnames from names where firstnames %(fragment_condition)s"""
		mp = gmMatchProvider.cMatchProvider_SQL2('demographics', cmd)
		mp.setThresholds(3, 5, 15)
		self.PRW_nick = gmPhraseWheel.cPhraseWheel (
			parent = PNL_form,
			id = -1,
			aMatchProvider = mp
		)
		self.PRW_nick.SetToolTipString(_("nick name, preferred name, call name, warrior name, artist name, alias"))
		# DOB
		STT_dob = wx.StaticText(PNL_form, -1, _('Date of birth'))
		STT_dob.SetForegroundColour('red')
		self.TTC_dob = gmDateTimeInput.gmDateInput (
			parent = PNL_form,
			id = -1,
			validator = gmGuiHelpers.cTextObjectValidator(required = True, only_digits = False)
		)
		self.TTC_dob.SetToolTipString(_("date of birth, if unknown or aliasing wanted then invent one"))
		# gender
		STT_gender = wx.StaticText(PNL_form, -1, _('Gender'))
		STT_gender.SetForegroundColour('red')
		genders, idx = gmPerson.get_gender_list()
		_genders = []
		for gender in genders:
			_genders.append({
				'data': gender[idx['tag']],
				'label': gender[idx['l10n_label']],
				'weight': gender[idx['sort_weight']]
			})
		mp = gmMatchProvider.cMatchProvider_FixedList(aSeq = _genders)
		mp.setThresholds(1, 1, 3)
		self.PRW_gender = gmPhraseWheel.cPhraseWheel (
			parent = PNL_form,
			id = -1,
			aMatchProvider = mp,
			validator = gmGuiHelpers.cTextObjectValidator(required = True, only_digits = False),
			aDelay = 100
		)
		self.PRW_gender.SetToolTipString(_("gender of patient"))
		# title
		STT_title = wx.StaticText(PNL_form, -1, _('Title'))
		cmd = "select distinct title, title from identity where title %(fragment_condition)s"
		mp = gmMatchProvider.cMatchProvider_SQL2('demographics', cmd)
		mp.setThresholds(1, 3, 15)
		self.PRW_title = gmPhraseWheel.cPhraseWheel(
			parent = PNL_form,
			id = -1,
			aMatchProvider = mp
		)
		self.PRW_title.SetToolTipString(_("The title of the patient"))
		# occupation
		STT_occupation = wx.StaticText(PNL_form, -1, _('Occupation'))
		cmd = "select distinct name, name from occupation where name %(fragment_condition)s"
		mp = gmMatchProvider.cMatchProvider_SQL2('demographics', cmd)
		mp.setThresholds(3, 5, 15)		
		self.PRW_occupation = gmPhraseWheel.cPhraseWheel(
			parent = PNL_form,
			id = -1,
			aMatchProvider = mp
		)
		self.PRW_occupation.SetToolTipString(_("The primary occupation of the patient"))
		# address number
		STT_address_number = wx.StaticText(PNL_form, -1, _('Number'))
		self.TTC_address_number = wx.TextCtrl(PNL_form, -1)
		self.TTC_address_number.SetToolTipString(_("primary/home address: address number"))		
		# street zip code
		STT_street_zip_code = wx.StaticText(PNL_form, -1, _('Zip code (street)'))
		self.TTC_street_zip_code = wx.TextCtrl(PNL_form, -1)
		self.TTC_street_zip_code.SetToolTipString(_("primary/home address: street zip code/postcode"))
		# street
		STT_street = wx.StaticText(PNL_form, -1, _('Street'))
		cmd = "select distinct name, name from street where name %(fragment_condition)s"
		mp = gmMatchProvider.cMatchProvider_SQL2('demographics', cmd)
		mp.setThresholds(3, 5, 15)				
		self.PRW_street = gmPhraseWheel.cPhraseWheel (
			parent = PNL_form,
			id = -1,
			aMatchProvider = mp
		)
		self.PRW_street.SetToolTipString(_("primary/home address: name of street"))
		# town zip code
		#STT_town_zip_code = wx.StaticText(PNL_form, -1, _('Zip code (town)'))
		#self.TTC_town_zip_code = wx.TextCtrl(PNL_form, -1)
		#self.TTC_town_zip_code.SetToolTipString(_("primary/home address: town/village/dwelling/city/etc. zip code/postcode"))		
		# town
		STT_town = wx.StaticText(PNL_form, -1, _('Town'))
		cmd = "select distinct name, name from urb where name %(fragment_condition)s"
		mp = gmMatchProvider.cMatchProvider_SQL2('demographics', cmd)
		mp.setThresholds(3, 5, 6)
		self.PRW_town = gmPhraseWheel.cPhraseWheel(
			parent = PNL_form,
			id = -1,
			aMatchProvider = mp
		)
		self.PRW_town.SetToolTipString(_("primary/home address: town/village/dwelling/city/etc."))
		# state
		# FIXME: default in config
		STT_state = wx.StaticText(PNL_form, -1, _('State'))
		cmd = "select distinct code, name from state where name %(fragment_condition)s"
		mp = gmMatchProvider.cMatchProvider_SQL2 ('demographics', cmd)
		mp.setThresholds(3, 5, 6)
		self.PRW_state = gmPhraseWheel.cPhraseWheel (
			parent = PNL_form,
			id = -1,
			aMatchProvider = mp
		)
		self.PRW_state.SetToolTipString(_("primary/home address: state"))
		# country
		# FIXME: default in config
		STT_country = wx.StaticText(PNL_form, -1, _('Country'))
		cmd = "select distinct code, name from country where name %(fragment_condition)s"
		mp = gmMatchProvider.cMatchProvider_SQL2('demographics', cmd)
		mp.setThresholds(2, 5, 15)
		self.PRW_country = gmPhraseWheel.cPhraseWheel (
			parent = PNL_form,
			id = -1,
			aMatchProvider = mp
		)
		self.PRW_country.SetToolTipString(_("primary/home address: country"))
		# phone
		STT_phone = wx.StaticText(PNL_form, -1, _('Phone'))
		self.TTC_phone = wx.TextCtrl(PNL_form, -1,
		validator = gmGuiHelpers.cTextObjectValidator(required = False, only_digits = True))
		self.TTC_phone.SetToolTipString(_("the primary/home phone number"))
				
		# layout input widgets
		SZR_input = wx.FlexGridSizer(cols = 2, rows = 15, vgap = 4, hgap = 4)
		SZR_input.AddGrowableCol(1)
		SZR_input.Add(STT_firstname, 0, wx.SHAPED)
		SZR_input.Add(self.PRW_firstname, 1, wx.EXPAND)
		SZR_input.Add(STT_lastname, 0, wx.SHAPED)
		SZR_input.Add(self.PRW_lastname, 1, wx.EXPAND)  
		SZR_input.Add(STT_nick, 0, wx.SHAPED)
		SZR_input.Add(self.PRW_nick, 1, wx.EXPAND)  		
		SZR_input.Add(STT_dob, 0, wx.SHAPED)
		SZR_input.Add(self.TTC_dob, 1, wx.EXPAND)	
		SZR_input.Add(STT_gender, 0, wx.SHAPED)
		SZR_input.Add(self.PRW_gender, 1, wx.EXPAND)
		SZR_input.Add(STT_title, 0, wx.SHAPED)
		SZR_input.Add(self.PRW_title, 1, wx.EXPAND)					
		SZR_input.Add(STT_occupation, 0, wx.SHAPED)
		SZR_input.Add(self.PRW_occupation, 1, wx.EXPAND)		
		SZR_input.Add(STT_address_number, 0, wx.SHAPED)
		SZR_input.Add(self.TTC_address_number, 1, wx.EXPAND)								
		SZR_input.Add(STT_street_zip_code, 0, wx.SHAPED)
		SZR_input.Add(self.TTC_street_zip_code, 1, wx.EXPAND)	
		SZR_input.Add(STT_street, 0, wx.SHAPED)
		SZR_input.Add(self.PRW_street, 1, wx.EXPAND)	
		#SZR_input.Add(STT_town_zip_code, 0, wx.SHAPED)
		#SZR_input.Add(self.TTC_town_zip_code, 1, wx.EXPAND)					
		SZR_input.Add(STT_town, 0, wx.SHAPED)
		SZR_input.Add(self.PRW_town, 1, wx.EXPAND)
		SZR_input.Add(STT_state, 0, wx.SHAPED)
		SZR_input.Add(self.PRW_state, 1, wx.EXPAND)	
		SZR_input.Add(STT_country, 0, wx.SHAPED)
		SZR_input.Add(self.PRW_country, 1, wx.EXPAND)
		SZR_input.Add(STT_phone, 0, wx.SHAPED)
		SZR_input.Add(self.TTC_phone, 1, wx.EXPAND)

		PNL_form.SetSizerAndFit(SZR_input)

		# layout page
		SZR_main = gmGuiHelpers.makePageTitle(self, title)
		SZR_main.Add(PNL_form, 1, wx.EXPAND)
#============================================================
class cNewPatientWizard(wizard.wxWizard):
	"""
	Wizard to create a new patient.

	TODO:
	- write pages for different "themes" of patient creation
	- make it configurable which pages are loaded
	- make available sets of pages that apply to a country
	- make loading of some pages depend upon values in earlier pages, eg
	  when the patient is female and older than 15 include a page about
	  "female" data (number of kids etc)
	"""
	#--------------------------------------------------------
	def __init__(self, parent):
		"""
		Creates a new instance of NewPatientWizard
		@param parent - The parent widget
		@type parent - A wxWindow instance
		"""
		id_wiz = wx.NewId()
		wizard.wxWizard.__init__(self, parent, id_wiz, _('Register new patient')) #images.getWizTest1Bitmap()
		self.SetExtraStyle(wx.WS_EX_VALIDATE_RECURSIVELY)

		self.__do_layout()
	#--------------------------------------------------------
	def RunWizard(self):
		if not wizard.wxWizard.RunWizard(self, self.basic_pat_details):
			return False

		# dump data to backend			
		# FIXME: replace gmPerson.link_XXX by subtables saving
		# FIXME: although the logger is defaulting to INFO, the logs won't be
		# logged unless set explicitely
#		_log.SetInfoLevel()

		genders, idx = gmPerson.get_gender_list()
		input_gender = None
		for gender in genders:
			if gender[idx['l10n_label']] == self.basic_pat_details.PRW_gender.GetValue():
				input_gender = gender[idx['tag']]
				break

		# create patient
		_log.Log(gmLog.lInfo, _('\n\nCreating identity... '))
		new_identity = gmPerson.create_identity (
			gender = input_gender,
			dob = self.basic_pat_details.TTC_dob.GetValue(),
			lastnames = self.basic_pat_details.PRW_firstname.GetValue(),
			firstnames = self.basic_pat_details.PRW_lastname.GetValue()
		)
		_log.Log(gmLog.lInfo, _('Identity created: %s') % new_identity)

		input_title = self.basic_pat_details.PRW_title.GetValue()
		if len(input_title) > 0:
			_log.Log(gmLog.lInfo, _('\nSetting title and gender...'))
			new_identity['title'] = input_title
			new_identity.save_payload()
			_log.Log(gmLog.lInfo, _('Refetching identity from db: %s') % gmPerson.cIdentity(aPK_obj=new_identity['pk_identity']))

		input_nickname = self.basic_pat_details.PRW_nick.GetValue()
		if len(input_nickname) > 0:
			_log.Log(gmLog.lInfo, _('\nGetting all names...'))
			for a_name in new_identity.get_all_names():
				_log.Log(gmLog.lInfo, '%s' % a_name)
			_log.Log(gmLog.lInfo, _('Active name: %s') % (new_identity.get_active_name()))
			_log.Log(gmLog.lInfo, _('Setting nickname...'))
			new_identity.set_nickname(nickname = input_nickname)
			_log.Log(gmLog.lInfo, _('Refetching all names...'))
			for a_name in new_identity.get_all_names():
				_log.Log(gmLog.lInfo, '%s' % a_name)

		input_occupation = self.basic_pat_details.PRW_occupation.GetValue()
		if len(input_occupation) > 0:
			_log.Log(gmLog.lInfo, _('\nIdentity occupations: %s') % new_identity['occupations'])
			_log.Log(gmLog.lInfo, _('Creating identity occupation...'))
			new_identity.link_occupation(occupation = input_occupation)
			_log.Log(gmLog.lInfo, _('Identity occupations: %s') % new_identity['occupations'])
			
		input_number = self.basic_pat_details.TTC_address_number.GetValue()
		input_street = self.basic_pat_details.PRW_street.GetValue()
		input_street_postcode = self.basic_pat_details.TTC_street_zip_code.GetValue()
		input_urb = self.basic_pat_details.PRW_town.GetValue()
		#input_urb_postcode = self.basic_pat_details.TTC_town_zip_code.GetValue()
		input_state = self.basic_pat_details.PRW_state.GetValue()
		input_country = self.basic_pat_details.PRW_country.GetValue()
		# FIXME improve by using validations in wizard page
		if len(input_number) > 0 and len(input_street) > 0 and len(input_street_postcode) > 0 and \
		len(input_state) > 0 and len(input_country) > 0:
			_log.Log(gmLog.lInfo, _('\nIdentity addresses: %s') % new_identity['addresses'])
			_log.Log(gmLog.lInfo, _('Creating identity address...'))
			# make sure the state exists in the backend
			new_identity.link_address(
				number = input_number,
				street = input_street,
				street_postcode = input_street_postcode,
				urb = input_urb,
				#urb_postcode = input_urb_postcode,
				state = input_state,
				country = input_country
			)
			_log.Log(gmLog.lInfo, _('Identity addresses: %s') % new_identity['addresses'])

		input_phone = self.basic_pat_details.TTC_phone.GetValue()
		if len(input_phone) > 0:
			_log.Log(gmLog.lInfo, _('\nIdentity communications: %s') % new_identity['comms'])
			_log.Log(gmLog.lInfo, _('Creating identity communication...'))
			new_identity.link_communication (
				comm_medium = 'homephone',
				url = input_phone,
				is_confidential = False
			)
			_log.Log(gmLog.lInfo, _('Identity communications: %s') % new_identity['comms'])

#	self.__wizard.Destroy()
	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def __do_layout(self):
		"""Arrange widgets.
		"""
		# Create the wizard pages
		self.basic_pat_details = cBasicPatDetailsPage(self, _('Basic patient details'))
		self.FitToPage(self.basic_pat_details)
#============================================================
class cBasicPatDetailsPageValidator(wx.PyValidator):
	"""
	This validator is used to ensure that the user has entered all
	the required conditional values in the page (eg., to properly
	create an address, all the related fields mut be filled).
	"""
	#--------------------------------------------------------
	def Clone(self):
		"""
		Standard cloner.
		Note that every validator must implement the Clone() method.
		"""
		return cBasicPatDetailsPageValidator()
	#--------------------------------------------------------
	def Validate(self):
		"""
		Validate the contents of the given text control.
		"""
		pageCtrl = self.GetWindow().GetParent()
		address_fields = (
			pageCtrl.TTC_address_number,
		#	pageCtrl.TTC_street_zip_code, ... optional
			pageCtrl.PRW_street,
			pageCtrl.PRW_town,
			pageCtrl.PRW_state,
			pageCtrl.PRW_country
		)
		# validate required fields
		is_any_field_filled = False
		for field in address_fields:
			if len(field.GetValue()) > 0:
				is_any_field_filled = True
				field.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
				field.Refresh()
				continue
			if is_any_field_filled:
				msg = _('To properly create an address, all the related fields must be filled in.')
				gmGuiHelpers.gm_show_error(msg, _('Required fields'), gmLog.lErr)
				field.SetBackgroundColour('pink')
				field.SetFocus()
				field.Refresh()
				return False
		return True
	#--------------------------------------------------------
	def TransferToWindow(self):
		""" Transfer data from validator to window.
		The default implementation returns False, indicating that an error
		occurred.  We simply return True, as we don't do any data transfer.
		"""
		return True # Prevent wxDialog from complaining.	
	#--------------------------------------------------------
	def TransferFromWindow(self):
		""" Transfer data from window to validator.
		The default implementation returns False, indicating that an error
		occurred.  We simply return True, as we don't do any data transfer.
		"""
		# FIXME: workaround for Validate to be called when clicking a wizard's
		# Finish button
		return self.Validate()
#============================================================
class TestPanel(wx.Panel):   
	"""
	Utility class to test the new patient wizard.
	"""
	#--------------------------------------------------------
	def __init__(self, parent, id):
		"""
		Create a new instance of TestPanel.
		@param parent The parent widget
		@type parent A wxWindow instance
		"""
		wx.Panel.__init__(self, parent, id)
		wizard = cNewPatientWizard(self)
		print wizard.RunWizard()
#============================================================
if __name__ == "__main__":
	from Gnumed.pycommon import gmPG
	db = gmPG.ConnectionPool()
	app1 = wx.PyWidgetTester(size = (800, 600))
	app1.SetWidget(TestPanel, -1)
	app1.MainLoop()
#	app2 = wx.PyWidgetTester(size = (800, 600))
#	app2.SetWidget(DemographicDetailWindow, -1)
#	app2.MainLoop()
#============================================================
# $Log: gmDemographicsWidgets.py,v $
# Revision 1.13  2005-04-28 16:58:45  cfmoro
# Removed fixme, was dued to log buffer
#
# Revision 1.12  2005/04/28 16:24:47  cfmoro
# Remove last references to town zip code
#
# Revision 1.11  2005/04/28 16:21:17  cfmoro
# Leave town zip code out and street zip code optional as in schema
#
# Revision 1.10  2005/04/25 21:22:17  ncq
# - some cleanup
# - make cNewPatientWizard inherit directly from wxWizard as it should IMO
#
# Revision 1.9  2005/04/25 16:59:11  cfmoro
# Implemented patient creation. Added conditional validator
#
# Revision 1.8  2005/04/25 08:29:24  ncq
# - combobox items must be strings
#
# Revision 1.7  2005/04/23 06:34:11  cfmoro
# Added address number and street zip code missing fields
#
# Revision 1.6  2005/04/18 19:19:54  ncq
# - wrong field order in some match providers
#
# Revision 1.5  2005/04/14 18:26:19  ncq
# - turn gender input into phrase wheel with fixed list
# - some cleanup
#
# Revision 1.4  2005/04/14 08:53:56  ncq
# - cIdentity moved
# - improved tooltips and phrasewheel thresholds
#
# Revision 1.3  2005/04/12 18:49:04  cfmoro
# Added missing fields and matcher providers
#
# Revision 1.2  2005/04/12 16:18:00  ncq
# - match firstnames against name_gender_map, too
#
# Revision 1.1  2005/04/11 18:09:55  ncq
# - offers demographic widgets
#
# Revision 1.62  2005/04/11 18:03:32  ncq
# - attach some match providers to first new-patient wizard page
#
# Revision 1.61  2005/04/10 12:09:17  cfmoro
# GUI implementation of the first-basic (wizard) page for patient details input
#
# Revision 1.60  2005/03/20 17:49:45  ncq
# - improve split window handling, cleanup
#
# Revision 1.59  2005/03/06 09:21:08  ihaywood
# stole a couple of icons from Richard's demo code
#
# Revision 1.58  2005/03/06 08:17:02  ihaywood
# forms: back to the old way, with support for LaTeX tables
#
# business objects now support generic linked tables, demographics
# uses them to the same functionality as before (loading, no saving)
# They may have no use outside of demographics, but saves much code already.
#
# Revision 1.57  2005/02/22 10:21:33  ihaywood
# new patient
#
# Revision 1.56  2005/02/20 10:45:49  sjtan
#
# kwargs syntax error.
#
# Revision 1.55  2005/02/20 10:15:16  ihaywood
# some tidying up
#
# Revision 1.54  2005/02/20 09:46:08  ihaywood
# demographics module with load a patient with no exceptions
#
# Revision 1.53  2005/02/18 11:16:41  ihaywood
# new demographics UI code won't crash the whole client now ;-)
# still needs much work
# RichardSpace working
#
# Revision 1.52  2005/02/03 20:19:16  ncq
# - get_demographic_record() -> get_identity()
#
# Revision 1.51  2005/02/01 10:16:07  ihaywood
# refactoring of gmDemographicRecord and follow-on changes as discussed.
#
# gmTopPanel moves to gmHorstSpace
# gmRichardSpace added -- example code at present, haven't even run it myself
# (waiting on some icon .pngs from Richard)
#
# Revision 1.50  2005/01/31 10:37:26  ncq
# - gmPatient.py -> gmPerson.py
#
# Revision 1.49  2004/12/18 13:45:51  sjtan
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
#   Why ? Because we can then do a simple replace wx.wx -> wx. for 2.5 code.
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
