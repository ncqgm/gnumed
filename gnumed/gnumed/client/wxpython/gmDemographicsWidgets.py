"""gmDemographics

Widgets dealing with patient demographics.

 @copyright: authors
 @dependencies: wxPython (>= version 2.3.1)
	28.07.2004 rterry gui-rewrite to include upper patient window
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmDemographicsWidgets.py,v $
# $Id: gmDemographicsWidgets.py,v 1.89 2006-06-12 18:31:31 ncq Exp $
__version__ = "$Revision: 1.89 $"
__author__ = "R.Terry, SJ Tan, I Haywood, Carlos Moro <cfmoro1976@yahoo.es>"
__license__ = 'GPL (details at http://www.gnu.org)'

# standard library
import time, string, sys, os

# 3rd party
import mx.DateTime as mxDT

try:
	import wxversion
	import wx
	import wx.wizard
except ImportError:
	from wxPython import wx
	#from wxPython.lib.mixins.listctrl import wxColumnSorterMixin, wx.ListCtrlAutoWidthMixin
	from wxPython import wizard

# GnuMed specific
from Gnumed.wxpython import gmPlugin, gmPatientHolder, images_patient_demographics, images_contacts_toolbar16_16, gmPhraseWheel, gmCharacterValidator, gmGuiHelpers, gmDateTimeInput, gmRegetMixin
from Gnumed.pycommon import  gmGuiBroker,  gmLog, gmDispatcher, gmSignals, gmCfg, gmI18N, gmMatchProvider, gmPG
from Gnumed.business import gmDemographicRecord, gmPerson

# constant defs
_log = gmLog.gmDefLog
_cfg = gmCfg.gmDefCfgFile
_name_gender_map = None

DATE_FORMAT = '%Y-%m-%d'

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


class cSmartCombo (wx.ComboBox):
	"""
	This Combobox implementation is designed to deal with
	list choices in the form of dictionaries of pairs code-string
	"""
	def __init__ (self, parent, _map):
		"""
		Instantiate a new smart combo give the dictionary of data.
		@param _map The dictionary of pairs code-string
		@type A DictType instance
		"""
		wx.ComboBox.__init__ (
			self,
			parent = parent,
			id = -1,
			value = "",
			pos = wx.DefaultPosition,
			size = wx.DefaultSize,
			choices = [],
			style = wx.CB_DROPDOWN
		)
		self.RefreshContents(_map)

	def RefreshContents(self, _map):
		"""
		Update the contents of the combo with new data.
		@param _map The dictionary of pairs code-string
		@type A DictType instance		
		"""
		# FIXME: rework this strange reverse() business
		pam = dict ([(str(y),x) for x, y in _map.items()])
		options = []
		options.extend(pam.keys())
		options.sort()
		cont = 0
		self.Clear()
		for option in options:
			self.Append(options[cont])
			self.SetClientData(cont, pam[options[cont]])
			#print "%s - %s" %(options[cont],pam[options[cont]])
			cont = cont + 1
			
	def GetData(self, value):
		return self.GetClientData(self.FindString(value))

	#def SetValue (self, value):
	#	if not value:
	#		wx.ComboBox.SetValue (self, '')
	#	else:
	#		print self.FindString(value)
	#		self.SetSelection(self.FindString(value))

	#def GetData (self):
		# Call parent class method (avoid recursive loop using validator)
		# and return empty string when no option was selected
	#	txt = wx.ComboBox.GetValue(self)
	#	print "Value: %s" % txt
	#	result = self.pam.get(txt,'')
	#	print "Data: %s" % result
	#	return result		

		
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
		opt_val, set = gmCfg.getDBParam (
			workplace = gmPerson.gmCurrentProvider().get_workplace(),
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
			gmPatient.set_active_patient(patient=patient)
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
			workplace = gmPerson.gmCurrentProvider().get_workplace(),
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
			gmDispatcher.connect (self._on_post_patient_selection, gmSignals.post_patient_selection ())

		
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
		self.gender = cSmartCombo (self, self.gendermap)
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
		self.pk_marital_status = cSmartCombo (self, gmDemographicRecord.getMaritalStatusTypes())
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
		self.combo_relationshipNOK = cSmartCombo (self, gmDemographicRecord.getRelationshipTypes ())
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
		state, postcode = gmDemographicRecord.getUrb (id_urb)
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


	def _on_post_patient_selection (self, **kwargs):
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
#============================================================
#============================================================
# new patient wizard classes
#============================================================
class cBasicPatDetailsPage(wx.wizard.WizardPageSimple):
	"""
	Wizard page for entering patient's basic demographic information
	"""
	
	form_fields = (
			'firstnames', 'lastnames', 'nick', 'dob', 'gender', 'title', 'occupation',
			'address_number', 'zip_code', 'street', 'town', 'state', 'country', 'phone'
	)
	
	def __init__(self, parent, title):
		"""
		Creates a new instance of BasicPatDetailsPage
		@param parent - The parent widget
		@type parent - A wx.Window instance
		@param tile - The title of the page
		@type title - A StringType instance				
		"""
		wx.wizard.WizardPageSimple.__init__(self, parent) #, bitmap = gmGuiHelpers.gm_icon(_('oneperson'))
		self.__title = title
		genders, idx = gmPerson.get_gender_list()
		self.__gender_map = {}
		for gender in genders:
			self.__gender_map[gender[idx['tag']]] = {
				'data': gender[idx['tag']],
				'label': gender[idx['l10n_label']],
				'weight': gender[idx['sort_weight']]
			}
		self.__do_layout()
		self.__register_interests()
	#--------------------------------------------------------
	def __do_layout(self):
		# main panel (required for a correct propagation of validator calls)
		PNL_form = wx.Panel(self, -1)

		# FIXME: improve cTextObjectValidator to accept regexp (gender, telephones, etc).

		# last name
		STT_lastname = wx.StaticText(PNL_form, -1, _('Last name'))
		STT_lastname.SetForegroundColour('red')
		queries = []
		queries.append("select distinct lastnames, lastnames from dem.names where lastnames %(fragment_condition)s")
		mp = gmMatchProvider.cMatchProvider_SQL2('demographics', queries)
		mp.setThresholds(3, 5, 15)
		self.PRW_lastname = gmPhraseWheel.cPhraseWheel (
			parent = PNL_form,
			id = -1,
			aMatchProvider = mp,
			validator = gmGuiHelpers.cTextObjectValidator(required = True, only_digits = False)
		)
		self.PRW_lastname.SetToolTipString(_("required: last name, family name"))

		# first name
		STT_firstname = wx.StaticText(PNL_form, -1, _('First name'))
		STT_firstname.SetForegroundColour('red')
		queries = []
		cmd = """
			select distinct firstnames, firstnames from dem.names where firstnames %(fragment_condition)s
				union
			select distinct name, name from dem.name_gender_map where name %(fragment_condition)s"""
		queries.append(cmd)
		mp = gmMatchProvider.cMatchProvider_SQL2('demographics', queries)
		mp.setThresholds(3, 5, 15)
		self.PRW_firstname = gmPhraseWheel.cPhraseWheel (
			parent = PNL_form,
			id = -1,
			aMatchProvider = mp,
			validator = gmGuiHelpers.cTextObjectValidator(required = True, only_digits = False)
		)
		self.PRW_firstname.SetToolTipString(_("required: surname/given name/first name"))

		# nickname
		STT_nick = wx.StaticText(PNL_form, -1, _('Nick name'))
		queries = []
		cmd = """
			select distinct preferred, preferred from dem.names where preferred %(fragment_condition)s
				union
			select distinct firstnames, firstnames from dem.names where firstnames %(fragment_condition)s"""
		queries.append(cmd)
		mp = gmMatchProvider.cMatchProvider_SQL2('demographics', queries)
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
		self.TTC_dob = gmDateTimeInput.cFuzzyTimestampInput (
			parent = PNL_form,
			id = -1
		)
		self.TTC_dob.SetToolTipString(_("required: date of birth, if unknown or aliasing wanted then invent one (yyyy-mm-dd)"))

		# gender
		STT_gender = wx.StaticText(PNL_form, -1, _('Gender'))
		STT_gender.SetForegroundColour('red')
		mp = gmMatchProvider.cMatchProvider_FixedList(aSeq = self.__gender_map.values())
		mp.setThresholds(1, 1, 3)
		self.PRW_gender = gmPhraseWheel.cPhraseWheel (
			parent = PNL_form,
			id = -1,
			aMatchProvider = mp,
			validator = gmGuiHelpers.cTextObjectValidator(required = True, only_digits = False),
			aDelay = 50,
			selection_only = True
		)
		self.PRW_gender.SetToolTipString(_("required: gender of patient"))

		# title
		STT_title = wx.StaticText(PNL_form, -1, _('Title'))
		queries = []
		queries.append("select distinct title, title from dem.identity where title %(fragment_condition)s")
		mp = gmMatchProvider.cMatchProvider_SQL2('demographics', queries)
		mp.setThresholds(1, 3, 15)
		self.PRW_title = gmPhraseWheel.cPhraseWheel(
			parent = PNL_form,
			id = -1,
			aMatchProvider = mp
		)
		self.PRW_title.SetToolTipString(_("title of patient"))

		# zip code
		STT_zip_code = wx.StaticText(PNL_form, -1, _('Zip code'))
		queries = []
		queries.append("select distinct postcode, postcode from dem.street where postcode %(fragment_condition)s")
		mp = gmMatchProvider.cMatchProvider_SQL2('demographics', queries)
		mp.setThresholds(3, 5, 15)				
		self.PRW_zip_code = gmPhraseWheel.cPhraseWheel (
			parent = PNL_form,
			id = -1,
			aMatchProvider = mp
		)
		self.PRW_zip_code.SetToolTipString(_("primary/home address: zip code/postcode"))

		# street
		STT_street = wx.StaticText(PNL_form, -1, _('Street'))
		queries = []
		queries.append ("""
		select distinct on (s1,s2) s1, s2 from (
			select * from (
				select street as s1, street as s2, 1 as rank from dem.v_zip2data where street %(fragment_condition)s and zip ilike %%(zip)s
					union
				select name as s1, name as s2, 2 as rank from dem.street where name %(fragment_condition)s
			) as q1 order by rank, s1
		) as q2
		""")
		mp = gmMatchProvider.cMatchProvider_SQL2('demographics', queries)
		mp.setThresholds(3, 5, 15)				
		self.PRW_street = gmPhraseWheel.cPhraseWheel (
			parent = PNL_form,
			id = -1,
			aMatchProvider = mp
		)
		self.PRW_street.set_context(context='zip', val='%')
		self.PRW_street.SetToolTipString(_("primary/home address: name of street"))

		# address number
		STT_address_number = wx.StaticText(PNL_form, -1, _('Number'))
		self.TTC_address_number = wx.TextCtrl(PNL_form, -1)
		self.TTC_address_number.SetToolTipString(_("primary/home address: address number"))

		# town
		STT_town = wx.StaticText(PNL_form, -1, _('Town'))
		queries = []
		queries.append("""
		select distinct on (u1,u2) u1, u2 from (
			select * from (		
				select urb as u1, urb as u2, 1 as rank from dem.v_zip2data where urb %(fragment_condition)s and zip ilike %%(zip)s
					union
				select name as u1, name as u2, 2 as rank from dem.urb where name %(fragment_condition)s
			) as t1 order by rank, u1
		) as q2
		""")
		mp = gmMatchProvider.cMatchProvider_SQL2('demographics', queries)
		mp.setThresholds(3, 5, 6)
		self.PRW_town = gmPhraseWheel.cPhraseWheel (
			parent = PNL_form,
			id = -1,
			aMatchProvider = mp
		)
		self.PRW_town.set_context(context='zip', val='%')		
		self.PRW_town.SetToolTipString(_("primary/home address: town/village/dwelling/city/etc."))

		# state
		# FIXME: default in config
		STT_state = wx.StaticText(PNL_form, -1, _('State'))
		STT_state.SetForegroundColour('red')
		queries = []
		queries.append("""
		select distinct on (code, name) code, name from (
			select * from (
					-- context: state name, country, zip
					select
						code_state as code, state as name, 1 as rank
					from dem.v_zip2data
					where
						state %(fragment_condition)s and l10n_country ilike %%(country)s and zip ilike %%(zip)s
				union
					-- context: state name and country
					select
						code as code, name as name, 2 as rank
					from dem.state
					where
						name %(fragment_condition)s and country in (select code from dem.country where name ilike %%(country)s)
				union
					-- context: state code, country, zip
					select
						code_state as code, state as name, 3 as rank
					from dem.v_zip2data
					where
						code_state %(fragment_condition)s and l10n_country ilike %%(country)s and zip ilike %%(zip)s
				union
					-- context: state code, country
					select
						code as code, name as name, 3 as rank
					from dem.state
					where
						code %(fragment_condition)s and country in (select code from dem.country where name ilike %%(country)s)
			) as q2 order by rank, name
		) as q1""")
		mp = gmMatchProvider.cMatchProvider_SQL2 ('demographics', queries)
		mp.setThresholds(2, 5, 6)
		self.PRW_state = gmPhraseWheel.cPhraseWheel (
			parent = PNL_form,
			id = -1,
			aMatchProvider = mp,
			selection_only = True
		)
		self.PRW_state.set_context(context='zip', val='%')
		self.PRW_state.set_context(context='country', val='%')
		self.PRW_state.SetToolTipString(_("primary/home address: state"))

		# country
		# FIXME: default in config
		STT_country = wx.StaticText(PNL_form, -1, _('Country'))
		queries = []
		queries.append("""
		select distinct on (code, name) code, name from (
			select * from (
				-- localized to user
				select code_country as code, l10n_country as name, 1 as rank from dem.v_zip2data where l10n_country %(fragment_condition)s and zip ilike %%(zip)s
					union
				select code as code, _(name) as name, 2 as rank from dem.country where _(name) %(fragment_condition)s
					union
				-- non-localized
				select code_country as code, country as name, 3 as rank from dem.v_zip2data where country %(fragment_condition)s and zip ilike %%(zip)s
					union
				select code as code, name as name, 4 as rank from dem.country where name %(fragment_condition)s
			) as q2 order by rank, name
		) as q1""")
		mp = gmMatchProvider.cMatchProvider_SQL2('demographics', queries)
		mp.setThresholds(2, 5, 15)
		self.PRW_country = gmPhraseWheel.cPhraseWheel (
			parent = PNL_form,
			id = -1,
			aMatchProvider = mp,
			selection_only = True
		)
		self.PRW_country.set_context(context='zip', val='%')
		self.PRW_country.SetToolTipString(_("primary/home address: country"))

		# phone
		STT_phone = wx.StaticText(PNL_form, -1, _('Phone'))
		self.TTC_phone = wx.TextCtrl(PNL_form, -1)
		self.TTC_phone.SetToolTipString(_("phone number at home"))

		# occupation
		STT_occupation = wx.StaticText(PNL_form, -1, _('Occupation'))
		queries = []
		queries.append("select distinct name, name from dem.occupation where name %(fragment_condition)s")
		mp = gmMatchProvider.cMatchProvider_SQL2('demographics', queries)
		mp.setThresholds(3, 5, 15)		
		self.PRW_occupation = gmPhraseWheel.cPhraseWheel (
			parent = PNL_form,
			id = -1,
			aMatchProvider = mp
		)
		self.PRW_occupation.SetToolTipString(_("primary occupation of the patient"))

		# form main validator
		self.form_DTD = cFormDTD(fields = self.__class__.form_fields)
		PNL_form.SetValidator(cBasicPatDetailsPageValidator(dtd = self.form_DTD))
				
		# layout input widgets
		SZR_input = wx.FlexGridSizer(cols = 2, rows = 15, vgap = 4, hgap = 4)
		SZR_input.AddGrowableCol(1)
		SZR_input.Add(STT_lastname, 0, wx.SHAPED)
		SZR_input.Add(self.PRW_lastname, 1, wx.EXPAND)
		SZR_input.Add(STT_firstname, 0, wx.SHAPED)
		SZR_input.Add(self.PRW_firstname, 1, wx.EXPAND)
		SZR_input.Add(STT_nick, 0, wx.SHAPED)
		SZR_input.Add(self.PRW_nick, 1, wx.EXPAND)
		SZR_input.Add(STT_dob, 0, wx.SHAPED)
		SZR_input.Add(self.TTC_dob, 1, wx.EXPAND)
		SZR_input.Add(STT_gender, 0, wx.SHAPED)
		SZR_input.Add(self.PRW_gender, 1, wx.EXPAND)
		SZR_input.Add(STT_title, 0, wx.SHAPED)
		SZR_input.Add(self.PRW_title, 1, wx.EXPAND)
		SZR_input.Add(STT_zip_code, 0, wx.SHAPED)
		SZR_input.Add(self.PRW_zip_code, 1, wx.EXPAND)
		SZR_input.Add(STT_street, 0, wx.SHAPED)
		SZR_input.Add(self.PRW_street, 1, wx.EXPAND)
		SZR_input.Add(STT_address_number, 0, wx.SHAPED)
		SZR_input.Add(self.TTC_address_number, 1, wx.EXPAND)
		SZR_input.Add(STT_town, 0, wx.SHAPED)
		SZR_input.Add(self.PRW_town, 1, wx.EXPAND)
		SZR_input.Add(STT_state, 0, wx.SHAPED)
		SZR_input.Add(self.PRW_state, 1, wx.EXPAND)
		SZR_input.Add(STT_country, 0, wx.SHAPED)
		SZR_input.Add(self.PRW_country, 1, wx.EXPAND)
		SZR_input.Add(STT_phone, 0, wx.SHAPED)
		SZR_input.Add(self.TTC_phone, 1, wx.EXPAND)
		SZR_input.Add(STT_occupation, 0, wx.SHAPED)
		SZR_input.Add(self.PRW_occupation, 1, wx.EXPAND)

		PNL_form.SetSizerAndFit(SZR_input)

		# layout page
		SZR_main = gmGuiHelpers.makePageTitle(self, self.__title)
		SZR_main.Add(PNL_form, 1, wx.EXPAND)
	#--------------------------------------------------------
	# event handling
	#--------------------------------------------------------
	def __register_interests(self):
		"""
		Configure enabled event signals
		"""
		# custom
		self.PRW_firstname.add_callback_on_lose_focus(self.on_name_set)
		self.PRW_country.add_callback_on_selection(self.on_country_selected)
		self.PRW_zip_code.add_callback_on_lose_focus(self.on_zip_set)
	#--------------------------------------------------------
	def on_country_selected(self, data):
		"""
		Set the states according to entered country.
		"""
		self.PRW_state.set_context(context='country', val=data)
		return True
	#--------------------------------------------------------
	def on_name_set(self):
		"""
		Set the gender according to entered firstname.
		Matches are fetched from existing records in backend.
		"""
		firstname = self.PRW_firstname.GetValue()
		cmd = "select gender from dem.name_gender_map where name ilike %s"
		rows = gmPG.run_ro_query('personalia', cmd, False, firstname)
		if rows is None:
			_log.Log(gmLog.lErr, 'error retrieving gender for [%s]' % firstname)
			return False
		if len(rows) == 0:
			return True
		gender = self.__gender_map[rows[0][0]]['label']
		wx.CallAfter(self.PRW_gender.SetValue, gender)
		return True
	#--------------------------------------------------------
	def on_zip_set(self):
		"""
		Set the street, town, state and country according to entered zip code.
		"""
		zip_code = self.PRW_zip_code.GetValue()
		self.PRW_street.set_context(context='zip', val=zip_code)
		self.PRW_town.set_context(context='zip', val=zip_code)
		self.PRW_state.set_context(context='zip', val=zip_code)
		self.PRW_country.set_context(context='zip', val=zip_code)
		return True				
#============================================================
class cNewPatientWizard(wx.wizard.Wizard):
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
	def __init__(self, parent, title = _('Register new patient'), subtitle = _('Basic patient details') ):
		"""
		Creates a new instance of NewPatientWizard
		@param parent - The parent widget
		@type parent - A wx.Window instance
		"""
		id_wiz = wx.NewId()
		wx.wizard.Wizard.__init__(self, parent, id_wiz, title) #images.getWizTest1Bitmap()
		self.SetExtraStyle(wx.WS_EX_VALIDATE_RECURSIVELY)
		self.__subtitle = subtitle
		self.__do_layout()
	#--------------------------------------------------------
	def RunWizard(self, activate=False):
		"""Create new patient.

		activate, too, if told to do so (and patient successfully created
		"""
		if not wx.wizard.Wizard.RunWizard(self, self.basic_pat_details):
			return False

		# retrieve DTD and create patient
		ident = create_identity_from_dtd(dtd = self.basic_pat_details.form_DTD)
		update_identity_from_dtd(identity = ident, dtd = self.basic_pat_details.form_DTD)
		link_contacts_from_dtd(identity = ident, dtd = self.basic_pat_details.form_DTD)
		link_occupation_from_dtd(identity = ident, dtd = self.basic_pat_details.form_DTD)

		if activate:
			pat = gmPerson.cPatient(identity = ident)
			gmPerson.gmCurrentPatient(patient = pat)

		return ident
	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def __do_layout(self):
		"""Arrange widgets.
		"""
		# Create the wizard pages
		self.basic_pat_details = cBasicPatDetailsPage(self, self.__subtitle )
		self.FitToPage(self.basic_pat_details)
#============================================================
class cBasicPatDetailsPageValidator(wx.PyValidator):
	"""
	This validator is used to ensure that the user has entered all
	the required conditional values in the page (eg., to properly
	create an address, all the related fields mut be filled).
	"""
	#--------------------------------------------------------
	def __init__(self, dtd):
		"""
		Validator initialization.
		@param dtd The object containing the data model.
		@type dtd A cFormDTD instance
		"""
		# initialize parent class
		wx.PyValidator.__init__(self)
		
		# validator's storage object
		self.form_DTD = dtd
	#--------------------------------------------------------
	def Clone(self):
		"""
		Standard cloner.
		Note that every validator must implement the Clone() method.
		"""
		return cBasicPatDetailsPageValidator(dtd = self.form_DTD)		# FIXME: probably need new instance of DTD ?
	#--------------------------------------------------------
	def Validate(self, parent = None):
		"""
		Validate the contents of the given text control.
		"""
		pageCtrl = self.GetWindow().GetParent()
		# dob validation
		if not pageCtrl.TTC_dob.is_valid_timestamp():
			msg = _('Cannot parse <%s> into proper timestamp.')
			gmGuiHelpers.gm_show_error(msg, _('Invalid date'), gmLog.lErr)
			pageCtrl.TTC_dob.SetBackgroundColour('pink')
			pageCtrl.TTC_dob.Refresh()
			pageCtrl.TTC_dob.SetFocus()
			return False
		pageCtrl.TTC_dob.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
		pageCtrl.TTC_dob.Refresh()
						
		# address		
		address_fields = (
			pageCtrl.TTC_address_number,
			pageCtrl.PRW_zip_code,
			pageCtrl.PRW_street,
			pageCtrl.PRW_town,
			pageCtrl.PRW_state,
			pageCtrl.PRW_country
		)
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
		"""
		Transfer data from validator to window.
		The default implementation returns False, indicating that an error
		occurred.  We simply return True, as we don't do any data transfer.
		"""
		pageCtrl = self.GetWindow().GetParent()
		# fill in controls with values from self.form_DTD
		pageCtrl.PRW_gender.SetValue(self.form_DTD['gender'])
		pageCtrl.TTC_dob.SetValue(self.form_DTD['dob'])
		pageCtrl.PRW_lastname.SetValue(self.form_DTD['lastnames'])
		pageCtrl.PRW_firstname.SetValue(self.form_DTD['firstnames'])
		pageCtrl.PRW_title.SetValue(self.form_DTD['title'])
		pageCtrl.PRW_nick.SetValue(self.form_DTD['nick'])
		pageCtrl.PRW_occupation.SetValue(self.form_DTD['occupation'])
		pageCtrl.TTC_address_number.SetValue(self.form_DTD['address_number'])
		pageCtrl.PRW_street.SetValue(self.form_DTD['street'])
		pageCtrl.PRW_zip_code.SetValue(self.form_DTD['zip_code'])
		pageCtrl.PRW_town.SetValue(self.form_DTD['town'])
		pageCtrl.PRW_state.SetValue(self.form_DTD['state'])
		pageCtrl.PRW_country.SetValue(self.form_DTD['country'])
		pageCtrl.TTC_phone.SetValue(self.form_DTD['phone'])
		return True # Prevent wxDialog from complaining.	
	#--------------------------------------------------------
	def TransferFromWindow(self):
		"""
		Transfer data from window to validator.
		The default implementation returns False, indicating that an error
		occurred.  We simply return True, as we don't do any data transfer.
		"""
		# FIXME: should be called automatically
		if not self.GetWindow().GetParent().Validate():
			return False
		try:
			pageCtrl = self.GetWindow().GetParent()
			# fill in self.form_DTD with values from controls
			self.form_DTD['gender'] = pageCtrl.PRW_gender.GetData()
			self.form_DTD['dob'] = mxDT.strptime(pageCtrl.TTC_dob.GetValue(), DATE_FORMAT)
			self.form_DTD['dob'] = pageCtrl.TTC_dob.GetData()
			self.form_DTD['lastnames'] = pageCtrl.PRW_lastname.GetValue()
			self.form_DTD['firstnames'] = pageCtrl.PRW_firstname.GetValue()
			self.form_DTD['title'] = pageCtrl.PRW_title.GetValue()
			self.form_DTD['nick'] = pageCtrl.PRW_nick.GetValue()
			self.form_DTD['occupation'] = pageCtrl.PRW_occupation.GetValue()
			self.form_DTD['address_number'] = pageCtrl.TTC_address_number.GetValue()
			self.form_DTD['street'] = pageCtrl.PRW_street.GetValue()
			self.form_DTD['zip_code'] = pageCtrl.PRW_zip_code.GetValue()
			self.form_DTD['town'] = pageCtrl.PRW_town.GetValue()
			self.form_DTD['state'] = pageCtrl.PRW_state.GetData()
			self.form_DTD['country'] = pageCtrl.PRW_country.GetData()
			self.form_DTD['phone'] = pageCtrl.TTC_phone.GetValue()
		except:
			return False
		return True
#============================================================
class cFormDTD:
	"""
	Simple Data Transfer Dictionary class to make easy the trasfer of
	data between the form (view) and the business logic.

	Maybe later consider turning this into a standard dict by
	{}.fromkeys([key, key, ...], default) when it becomes clear that
	we really don't need the added potential of a full-fledged class.
	"""
	def __init__(self, fields):		
		"""
		Initialize the DTD with the supplied field names.
		@param fields The names of the fields.
		@type fields A TupleType instance.
		"""
		self.data = {}		
		for a_field in fields:
			self.data[a_field] = ''
		
	def __getitem__(self, attribute):
		"""
		Retrieve the value of the given attribute (key)
		@param attribute The attribute (key) to retrieve its value for.
		@type attribute a StringType instance.
		"""
		if not self.data[attribute]:
			return ''
		return self.data[attribute]

	def __setitem__(self, attribute, value):
		"""
		Set the value of a given attribute (key).
		@param attribute The attribute (key) to set its value for.
		@type attribute a StringType instance.		
		@param avaluee The value to set.
		@rtpe attribute a StringType instance.
		"""
		self.data[attribute] = value
	
	def __str__(self):
		"""
		Print string representation of the DTD object.
		"""
		return str(self.data)
#============================================================
# patient demographics editing classes
#============================================================
class cPatEditionNotebook(wx.Notebook):
	"""Notebook style widget displaying patient edition pages:

		-Identity
		-Contacts (addresses, phone numbers, etc)
		-Occupations
		...
	0.1: Basic set of fields (those in new patient wizard) structured in
	a notebook widget.
	Post 0.1: Improve the notebook patient edition widget supporting
	aditional (insurance, relatives, etc), complex and multiple elements
	(differet types of addresses, phones, etc).
	"""
	
	# fields in every page/form/validator
	ident_form_fields = (
			'firstnames', 'lastnames', 'nick', 'dob', 'gender', 'title'
	)
	contacts_form_fields = (
			'address_number', 'zip_code', 'street', 'town', 'state', 'country', 'phone'
	)
	occupations_form_fields = (
			'occupation',
	)
	#--------------------------------------------------------
	def __init__(self, parent, id, pos=wx.DefaultPosition, size=wx.DefaultSize):

		wx.Notebook.__init__ (
			self,
			parent = parent,
			id = id,
			pos = pos,
			size = size,
			style = wx.NB_TOP | wx.NB_MULTILINE | wx.NO_BORDER | wx.VSCROLL | wx.HSCROLL,
			name = self.__class__.__name__
		)
		self.SetExtraStyle(wx.WS_EX_VALIDATE_RECURSIVELY)

		self.ident_form_DTD = cFormDTD(fields = self.__class__.ident_form_fields)
		self.contacts_form_DTD = cFormDTD(fields = self.__class__.contacts_form_fields)		
		self.occupations_form_DTD = cFormDTD(fields = self.__class__.occupations_form_fields)
		# genders
		genders, idx = gmPerson.get_gender_list()
		self.__genders = []
		for gender in genders:
			self.__genders.append ({
				'data': gender[idx['tag']],
				'label': gender[idx['l10n_label']],
				'weight': gender[idx['sort_weight']]
			})
		self.__pat = gmPerson.gmCurrentPatient()
		self.__do_layout()
		self.__register_interests()
		self.SetSelection(0)
	#--------------------------------------------------------
	# public API
	#--------------------------------------------------------
	def save(self):
		for page_idx in range(self.GetPageCount()):
			page = self.GetPage(page_idx)
			page.save()
	#--------------------------------------------------------
	def refresh(self):
		"""
		Populate fields in pages with data from model.
		"""
		
		identity = self.__pat.get_identity()
		# refresh identity reference in pages
		for page_idx in range(self.GetPageCount()):
			page = self.GetPage(page_idx)
			page.set_identity(identity)

		# business class -> identity DTD
		txt = identity['gender']
		for gender in self.__genders:
			if gender['data'] == txt:
				txt = gender['label']
				break
		self.ident_form_DTD['gender'] = txt
#xxxxxxxxxxxxxxxxx
#check source of identity['dob'] == string
#xxxxxxxxxxxxxxxxx
		self.ident_form_DTD['dob'] = identity['dob']
		txt = ''
		if not identity['title'] is None:
			txt = identity['title']
		self.ident_form_DTD['title'] = txt
		
		# names
		active_name = identity.get_active_name()		
		self.ident_form_DTD['lastnames'] = active_name['last']
		self.ident_form_DTD['firstnames'] = active_name['first']		
		txt = ''
		if not active_name['preferred'] is None:
			txt = active_name['preferred']
		self.ident_form_DTD['nick'] = txt		

		# business class -> contacts DTD
		addresses = identity['addresses']
		if len(addresses) > 0:
			last_idx = len(addresses)-1
			self.contacts_form_DTD['address_number'] = addresses[last_idx]['number']
			self.contacts_form_DTD['street'] = addresses[last_idx]['street']
			self.contacts_form_DTD['zip_code'] = addresses[last_idx]['postcode']
			self.contacts_form_DTD['town'] = addresses[last_idx]['urb']
			self.contacts_form_DTD['state'] = addresses[last_idx]['state']
			self.contacts_form_DTD['country'] = addresses[last_idx]['country']
		else:
			self.contacts_form_DTD['address_number'] = ''
			self.contacts_form_DTD['street'] = ''
			self.contacts_form_DTD['zip_code'] = ''
			self.contacts_form_DTD['town'] = ''
			self.contacts_form_DTD['state'] = ''
			self.contacts_form_DTD['country'] = ''
		comms = identity['comms']
		if len(comms) > 0:
			for a_comm in comms:
				if a_comm['type'] == 'homephone':
					self.contacts_form_DTD['phone'] = a_comm['url']
					break
		else:
			self.contacts_form_DTD['phone'] = ''

		# business class -> occupations DTD
		occupations = identity['occupations']
		if len(occupations) > 0:
			last_idx = len(occupations)-1
			self.occupations_form_DTD['occupation'] = occupations[last_idx]['occupation']
		else:
			self.occupations_form_DTD['occupation'] = ''

		# Recursively calls TransferDataToWindow in notebook
		# children, thanks to wx.WS_EX_VALIDATE_RECURSIVELY
		self.TransferDataToWindow()

		return True
	#--------------------------------------------------------
	# internal API
	#--------------------------------------------------------
	def __do_layout(self):
		"""
		Build patient edition notebook pages.
		"""
		ident = self.__pat.get_identity()
		# identity page
		new_page = cPatIdentityPanel (
			parent = self,
			id = -1,
			dtd = self.ident_form_DTD,
			ident = ident
		)
		self.AddPage (
			page = new_page,
			text = _('Identity'),
			select = True
		)
		# contacts page
		label = _('Contacts')		
		new_page = cPatContactsPanel (
			parent = self,
			id = -1,
			dtd = self.contacts_form_DTD,
			ident = ident
		)
		self.AddPage (
			page = new_page,
			text = label,
			select = False
		)
		# occupations page
		label = _('Occupations')
		new_page = cPatOccupationsPanel (
			parent = self,
			id = -1,
			dtd = self.occupations_form_DTD,
			ident = ident
		)
		self.AddPage (
			page = new_page,
			text = label,
			select = False
		)
	#--------------------------------------------------------
	# event handling
	#--------------------------------------------------------
	def __register_interests(self):
		"""
		Configure enabled event signals
		"""
		# client internal signals
		gmDispatcher.connect(signal=gmSignals.pre_patient_selection(), receiver=self._on_pre_patient_selection)
		gmDispatcher.connect(signal=gmSignals.application_closing(), receiver=self._on_application_closing)
	#--------------------------------------------------------
	def _on_pre_patient_selection(self):
		"""Another patient is about to be activated."""
#		print "[%s]: another patient is about to become active" % self.__class__.__name__
#		print "need code to ask user about unsaved patient details"
		pass
	#--------------------------------------------------------
	def _on_application_closing(self):
#		print "[%s]: the application is closing down" % self.__class__.__name__
#		print "need code to  ask user about unsaved patient details"
		pass
#============================================================
class cPatIdentityPanel(wx.Panel):
	"""
	Page containing patient identity edition fields.
	"""
	def __init__(self, parent, id, dtd=None, ident=None):
		"""
		Creates a new instance of cPatIdentityPanel
		@param parent - The parent widget
		@type parent - A wx.Window instance
		@param id - The widget id
		@type id - An integer
		@param dtd The object containing the data model.
		@type dtd A cFormDTD instance
		"""
		wx.Panel.__init__(self, parent, id)
		self.__dtd = dtd
		self.__ident = ident
		genders, idx = gmPerson.get_gender_list()
		self.__gender_map = {}
		for gender in genders:
			self.__gender_map[gender[idx['tag']]] = {
				'data': gender[idx['tag']],
				'label': gender[idx['l10n_label']],
				'weight': gender[idx['sort_weight']]
			}
		self.__do_layout()
		self.__register_interests()
	#--------------------------------------------------------
	def __do_layout(self):

		# FIXME: main panel, required for a correct propagation of validator calls.
		# If this panel doesn't exists and the validator is set
		# direclty to self, calling self.transferDataFromWindow
		# just returns true without the method in validator being
		# called. It seems that works for the children of self.
		PNL_form = wx.Panel(self, -1)

		# last name
		STT_lastname = wx.StaticText(PNL_form, -1, _('Last name'))
		STT_lastname.SetForegroundColour('red')
		queries = []
		queries.append("select distinct lastnames, lastnames from dem.names where lastnames %(fragment_condition)s")
		mp = gmMatchProvider.cMatchProvider_SQL2('demographics', queries)
		mp.setThresholds(3, 5, 15)
		self.PRW_lastname = gmPhraseWheel.cPhraseWheel (
			parent = PNL_form,
			id = -1,
			aMatchProvider = mp,
			validator = gmGuiHelpers.cTextObjectValidator(required = True, only_digits = False)
		)
		self.PRW_lastname.SetToolTipString(_("required: last name, family name"))

		# first name
		STT_firstname = wx.StaticText(PNL_form, -1, _('First name'))
		STT_firstname.SetForegroundColour('red')
		queries = []
		cmd = """
			select distinct firstnames, firstnames from dem.names where firstnames %(fragment_condition)s
				union
			select distinct name, name from dem.name_gender_map where name %(fragment_condition)s"""
		queries.append(cmd)
		mp = gmMatchProvider.cMatchProvider_SQL2('demographics', queries=queries)
		mp.setThresholds(3, 5, 15)
		self.PRW_firstname = gmPhraseWheel.cPhraseWheel (
			parent = PNL_form,
			id = -1,
			aMatchProvider = mp,
			validator = gmGuiHelpers.cTextObjectValidator(required = True, only_digits = False)
		)
		self.PRW_firstname.SetToolTipString(_("required: surname/given name/first name"))

		# nickname
		STT_nick = wx.StaticText(PNL_form, -1, _('Nick name'))
		queries = []
		cmd = """
			select distinct preferred, preferred from dem.names where preferred %(fragment_condition)s
				union
			select distinct firstnames, firstnames from dem.names where firstnames %(fragment_condition)s"""
		queries.append(cmd)
		mp = gmMatchProvider.cMatchProvider_SQL2('demographics', queries=queries)
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
		self.TTC_dob = gmDateTimeInput.cFuzzyTimestampInput (
			parent = PNL_form,
			id = -1
#			, validator = gmGuiHelpers.cTextObjectValidator(required = True, only_digits = False)
		)
		self.TTC_dob.SetToolTipString(_("required: date of birth, if unknown or aliasing wanted then invent one (Y-m-d)"))

		# gender
		STT_gender = wx.StaticText(PNL_form, -1, _('Gender'))
		STT_gender.SetForegroundColour('red')
		mp = gmMatchProvider.cMatchProvider_FixedList(aSeq = self.__gender_map.values())
		mp.setThresholds(1, 1, 3)
		self.PRW_gender = gmPhraseWheel.cPhraseWheel (
			parent = PNL_form,
			id = -1,
			aMatchProvider = mp,
			validator = gmGuiHelpers.cTextObjectValidator(required = True, only_digits = False),
			aDelay = 50,
			selection_only = True
		)
		self.PRW_gender.SetToolTipString(_("required: gender of patient"))

		# title
		STT_title = wx.StaticText(PNL_form, -1, _('Title'))
		queries = []
		queries.append("select distinct title, title from dem.identity where title %(fragment_condition)s")
		mp = gmMatchProvider.cMatchProvider_SQL2('demographics', queries=queries)
		mp.setThresholds(1, 3, 15)
		self.PRW_title = gmPhraseWheel.cPhraseWheel (
			parent = PNL_form,
			id = -1,
			aMatchProvider = mp
		)
		self.PRW_title.SetToolTipString(_("title of patient"))

		# Set validator for identity form
		PNL_form.SetValidator(cPatIdentityPanelValidator(dtd = self.__dtd))
		
		# layout input widgets
		SZR_input = wx.FlexGridSizer(cols = 2, rows = 15, vgap = 4, hgap = 4)
		SZR_input.AddGrowableCol(1)
		SZR_input.Add(STT_lastname, 0, wx.SHAPED)
		SZR_input.Add(self.PRW_lastname, 1, wx.EXPAND)
		SZR_input.Add(STT_firstname, 0, wx.SHAPED)
		SZR_input.Add(self.PRW_firstname, 1, wx.EXPAND)
		SZR_input.Add(STT_nick, 0, wx.SHAPED)
		SZR_input.Add(self.PRW_nick, 1, wx.EXPAND)
		SZR_input.Add(STT_dob, 0, wx.SHAPED)
		SZR_input.Add(self.TTC_dob, 1, wx.EXPAND)
		SZR_input.Add(STT_gender, 0, wx.SHAPED)
		SZR_input.Add(self.PRW_gender, 1, wx.EXPAND)
		SZR_input.Add(STT_title, 0, wx.SHAPED)
		SZR_input.Add(self.PRW_title, 1, wx.EXPAND)
		PNL_form.SetSizerAndFit(SZR_input)
		# layout page
		SZR_main = wx.BoxSizer(wx.VERTICAL)
		SZR_main.Add(PNL_form, 1, wx.EXPAND)
		self.SetSizer(SZR_main)
	#--------------------------------------------------------
	# event handling
	#--------------------------------------------------------
	def __register_interests(self):
		"""
		Configure enabled event signals
		"""
		# custom
		self.PRW_firstname.add_callback_on_lose_focus(self.on_name_set)
	#--------------------------------------------------------
	def on_name_set(self):
		"""
		Set the gender according to entered firstname.
		Matches are fetched from existing records in backend.
		"""
		firstname = self.PRW_firstname.GetValue()
		cmd = "select gender from dem.name_gender_map where name ilike %s"
		rows = gmPG.run_ro_query('personalia', cmd, False, firstname)
		if rows is None:
			_log.Log(gmLog.lErr, 'error retrieving gender for [%s]' % firstname)
			return False
		if len(rows) == 0:
			return True
		gender = self.__gender_map[rows[0][0]]['label']
		wx.CallAfter(self.PRW_gender.SetValue, gender)
		return True
	#--------------------------------------------------------
	# public API
	#--------------------------------------------------------		
	def set_identity(self, identity):
		self.__ident = identity
		
	def save(self):
		msg = _("Data in Identity section can't be saved.\nPlease, correct any invalid input.")
		if not self.Validate():
			gmGuiHelpers.gm_show_error(msg, _('Identity invalid input'), gmLog.lErr)
			return False
		if not self.TransferDataFromWindow():
			gmGuiHelpers.gm_show_error(msg, _('Identity invalid input'), gmLog.lErr)					
			return False
		if not update_identity_from_dtd(identity = self.__ident, dtd = self.__dtd):
			msg = _("An error happened while saving Identity section.\nPlease, refresh and check all the data.")
			gmGuiHelpers.gm_show_error(msg, _('Identity saving error'), gmLog.lErr)
			return False
		return True
#============================================================		
class cPatIdentityPanelValidator(wx.PyValidator):
	"""
	This validator is used to ensure that the user has entered all
	the required conditional values in patient identity page.
	"""
	#--------------------------------------------------------
	def __init__(self, dtd):
		"""
		Validator initialization.
		@param dtd The object containing the data model.
		@type dtd A cFormDTD instance
		"""
		wx.PyValidator.__init__(self)
		self.__dtd = dtd
	#--------------------------------------------------------
	def Clone(self):
		"""
		Standard cloner.
		Note that every validator must implement the Clone() method.
		"""
		return cPatIdentityPanelValidator(dtd = self.__dtd)		# FIXME: probably need new instance of DTD ?
	#--------------------------------------------------------
	def TransferToWindow(self):
		"""
		Transfer data from validator to window.
		The default implementation returns False, indicating that an error
		occurred.  We simply return True, as we don't do any data transfer.
		"""
		try:
			pageCtrl = self.GetWindow().GetParent()
			pageCtrl.PRW_gender.SetValue(self.__dtd['gender'])
			pageCtrl.TTC_dob.SetValue(self.__dtd['dob'].Format(DATE_FORMAT))
			pageCtrl.PRW_lastname.SetValue(self.__dtd['lastnames'])
			pageCtrl.PRW_firstname.SetValue(self.__dtd['firstnames'])
			pageCtrl.PRW_title.SetValue(self.__dtd['title'])
			pageCtrl.PRW_nick.SetValue(self.__dtd['nick'])
		except:
			_log.LogException('cannot transfer dtd to form', sys.exc_info(), verbose=0)
			return False
		return True
	#--------------------------------------------------------
	def Validate(self, parent = None):
		"""Validate the contents of the given text control.
		"""
		pageCtrl = self.GetWindow().GetParent()
		# dob validation
		if not pageCtrl.TTC_dob.is_valid_timestamp():
			msg = _('Cannot parse <%s> into proper timestamp.')
			gmGuiHelpers.gm_show_error(msg, _('Invalid date'), gmLog.lErr)
			pageCtrl.TTC_dob.SetBackgroundColour('pink')
			pageCtrl.TTC_dob.Refresh()
			pageCtrl.TTC_dob.SetFocus()
			return False
		pageCtrl.TTC_dob.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
		pageCtrl.TTC_dob.Refresh()

		return True
	#--------------------------------------------------------
	def TransferFromWindow(self):
		"""
		Transfer data from window to validator.
		The default implementation returns False, indicating that an error
		occurred.  We simply return True, as we don't do any data transfer.
		"""
		try:
			pageCtrl = self.GetWindow().GetParent()
			# fill in self.__dtd with values from controls
			self.__dtd['gender'] = pageCtrl.PRW_gender.GetData()
#			self.__dtd['dob'] = mxDT.strptime(pageCtrl.TTC_dob.GetValue(), DATE_FORMAT)
			self.__dtd['dob'] = pageCtrl.TTC_dob.GetData()
			self.__dtd['lastnames'] = pageCtrl.PRW_lastname.GetValue()
			self.__dtd['firstnames'] = pageCtrl.PRW_firstname.GetValue()
			self.__dtd['title'] = pageCtrl.PRW_title.GetValue()
			self.__dtd['nick'] = pageCtrl.PRW_nick.GetValue()
		except:
			return False
		return True
#============================================================
class cPatContactsPanel(wx.Panel):
	"""
	Page containing patient contacts edition fields.
	"""
		
	def __init__(self, parent, id, dtd=None, ident=None):
		"""
		Creates a new instance of BasicPatDetailsPanel
		@param parent - The parent widget
		@type parent - A wx.Window instance
		@param id - The widget id
		@type id - An integer
		@param dtd The object containing the data model.
		@type dtd A cFormDTD instance
		"""
		wx.Panel.__init__(self, parent, id)		
		self.__dtd = dtd
		self.__ident = ident
		if os.environ.has_key ("LANG"):
			self.locale = os.environ['LANG']
		else:
			self.locale = 'unknown'
		self.__do_layout()
		self.__register_interests()
	#--------------------------------------------------------
	def __do_number (self):
		
		# address number
		STT_address_number = wx.StaticText(self.PNL_form, -1, _('Number'))
		self.TTC_address_number = wx.TextCtrl(self.PNL_form, -1)
		self.TTC_address_number.SetToolTipString(_("primary/home address: address number"))
		self.SZR_input.Add(STT_address_number, 0, wx.SHAPED)
		self.SZR_input.Add(self.TTC_address_number, 1, wx.EXPAND)

	def __do_zip (self):
			
		# zip code
		STT_zip_code = wx.StaticText(self.PNL_form, -1, _('Zip code'))
		queries = []
		queries.append("select distinct postcode, postcode from dem.street where postcode %(fragment_condition)s")
		mp = gmMatchProvider.cMatchProvider_SQL2('demographics', queries=queries)
		mp.setThresholds(3, 5, 15)				
		self.PRW_zip_code = gmPhraseWheel.cPhraseWheel (
			parent = self.PNL_form,
			id = -1,
			aMatchProvider = mp
		)
		self.PRW_zip_code.SetToolTipString(_("primary/home address: zip code/postcode"))
		self.SZR_input.Add(STT_zip_code, 0, wx.SHAPED)
		self.SZR_input.Add(self.PRW_zip_code, 1, wx.EXPAND)

	def __do_street (self):
				
		# street
		STT_street = wx.StaticText(self.PNL_form, -1, _('Street'))
		queries = []
		queries.append("""
		select distinct on (s1,s2) s1, s2 from (
			select * from (
				select street as s1, street as s2, 1 as rank from dem.v_zip2data where street %(fragment_condition)s and zip ilike %%(zip)s
					union
				select name as s1, name as s2, 2 as rank from dem.street where name %(fragment_condition)s
			) as q1 order by rank, s1
		) as q2
		""")
		mp = gmMatchProvider.cMatchProvider_SQL2('demographics', queries=queries)
		mp.setThresholds(3, 5, 15)				
		self.PRW_street = gmPhraseWheel.cPhraseWheel (
			parent = self.PNL_form,
			id = -1,
			aMatchProvider = mp
		)
		self.PRW_street.set_context(context='zip', val='%')
		self.PRW_street.SetToolTipString(_("primary/home address: name of street"))
		self.SZR_input.Add(STT_street, 0, wx.SHAPED)
		self.SZR_input.Add(self.PRW_street, 1, wx.EXPAND)


	def __do_town (self):
		
		# town
		STT_town = wx.StaticText(self.PNL_form, -1, _('Town'))
		queries = []
		queries.append("""
		select distinct on (u1,u2) u1, u2 from (
			select * from (		
				select urb as u1, urb as u2, 1 as rank from dem.v_zip2data where urb %(fragment_condition)s and zip ilike %%(zip)s
					union
				select name as u1, name as u2, 2 as rank from dem.urb where name %(fragment_condition)s
			) as t1 order by rank, u1
		) as q2
		""")
		mp = gmMatchProvider.cMatchProvider_SQL2('demographics', queries=queries)
		mp.setThresholds(3, 5, 6)
		self.PRW_town = gmPhraseWheel.cPhraseWheel (
			parent = self.PNL_form,
			id = -1,
			aMatchProvider = mp
		)
		self.PRW_town.set_context(context='zip', val='%')
		self.PRW_town.SetToolTipString(_("primary/home address: town/village/dwelling/city/etc."))
		
		self.SZR_input.Add(STT_town, 0, wx.SHAPED)
		self.SZR_input.Add(self.PRW_town, 1, wx.EXPAND)

	def __do_state_country (self):
		# state
		# FIXME: default in config
		STT_state = wx.StaticText(self.PNL_form, -1, _('State'))
		STT_state.SetForegroundColour('red')
		queries = []
		queries.append("""
		select distinct on (code,name) code, name from (
			select * from (				
				select code_state as code, state as name, 1 as rank from dem.v_zip2data where state %(fragment_condition)s and l10n_country ilike %%(country)s and zip ilike %%(zip)s
					union
				select
					code as code, name as name, 2 as rank
				from dem.state
				where
					name %(fragment_condition)s and country in (select code from dem.country where name ilike %%(country)s)
			) as q1 order by rank, name
		) as q2				
		""")
		mp = gmMatchProvider.cMatchProvider_SQL2 ('demographics', queries)
		mp.setThresholds(3, 5, 6)
		self.PRW_state = gmPhraseWheel.cPhraseWheel (
			parent = self.PNL_form,
			id = -1,
			aMatchProvider = mp,
			selection_only = True
		)
		self.PRW_state.set_context(context='zip', val='%')
		self.PRW_state.set_context(context='country', val='%')
		self.PRW_state.SetToolTipString(_("primary/home address: state"))

		# country
		# FIXME: default in config
		STT_country = wx.StaticText(self.PNL_form, -1, _('Country'))
		queries = []
		queries.append("""
		select distinct on (code,name) code, name from (
			select * from (						
				select code_country as code, l10n_country as name, 1 as rank from dem.v_zip2data where l10n_country %(fragment_condition)s and zip ilike %%(zip)s
					union
				select code as code, _(name) as name, 2 as rank from dem.country where _(name) %(fragment_condition)s
			) as q1 order by rank, name
		) as q2								
		""")
		mp = gmMatchProvider.cMatchProvider_SQL2('demographics', queries)
		mp.setThresholds(2, 5, 15)
		self.PRW_country = gmPhraseWheel.cPhraseWheel (
			parent = self.PNL_form,
			id = -1,
			aMatchProvider = mp,
			selection_only = True
		)
		self.PRW_country.set_context(context='zip', val='%')
		self.PRW_country.SetToolTipString(_("primary/home address: country"))
		self.SZR_input.Add(STT_state, 0, wx.SHAPED)
		self.SZR_input.Add(self.PRW_state, 1, wx.EXPAND)
		self.SZR_input.Add(STT_country, 0, wx.SHAPED)
		self.SZR_input.Add(self.PRW_country, 1, wx.EXPAND)

	def __do_phones (self):
		
		# phone
		STT_phone = wx.StaticText(self.PNL_form, -1, _('Phone'))
		self.TTC_phone = wx.TextCtrl(self.PNL_form, -1)
		self.TTC_phone.SetToolTipString(_("phone number at home"))
		self.SZR_input.Add(STT_phone, 0, wx.SHAPED)
		self.SZR_input.Add(self.TTC_phone, 1, wx.EXPAND)

	def __do_layout(self):
		# FIXME: main panel, required for a correct propagation of validator calls.
		# If this panel doesn't exists and the validator is set
		# direclty to self, calling self.transferDataFromWindow
		# just returns true without the method in validator being
		# called. It seems that works for the children of self.

		self.PNL_form = wx.Panel(self, -1)
		# layout input widgets
		self.SZR_input = wx.FlexGridSizer(cols = 2, rows = 15, vgap = 4, hgap = 4)
		self.SZR_input.AddGrowableCol(1)
		if self.locale[:5] == 'en_AU':
			self.__do_number ()
			self.__do_street ()
			self.__do_town ()
			self.__do_zip ()
			self.__do_state_country ()
			self.__do_phones ()
		else:
			self.__do_zip ()
			self.__do_street ()
			self.__do_number ()
			self.__do_town ()
			self.__do_state_country ()
			self.__do_phones ()
		# Set validator for identity form
		self.PNL_form.SetValidator(cPatContactsPanelValidator(dtd = self.__dtd))
		
		self.PNL_form.SetSizerAndFit(self.SZR_input)
		
		# layout page
		SZR_main = wx.BoxSizer(wx.VERTICAL)
		SZR_main.Add(self.PNL_form, 1, wx.EXPAND)
		self.SetSizer(SZR_main)
	#--------------------------------------------------------
	# event handling
	#--------------------------------------------------------
	def __register_interests(self):
		"""
		Configure enabled event signals
		"""
		# custom
		if self.locale[:5] == 'en_AU':
			self.PRW_town.add_callback_on_selection (self.on_town_set)
		else:
			self.PRW_country.add_callback_on_selection(self.on_country_selected)
			self.PRW_zip_code.add_callback_on_lose_focus(self.on_zip_set)
	#--------------------------------------------------------
	def on_country_selected(self, data):
		"""
		Set the states according to entered country.
		"""
		if data is None:
			data = '%'
		self.PRW_state.set_context(context='country', val=data)
		return True
	#--------------------------------------------------------
	def on_zip_set(self):
		"""
		Set the street, town, state and country according to entered zip code.
		"""
		zip_code = self.PRW_zip_code.GetValue()
		self.PRW_street.set_context(context='zip', val=zip_code)
		self.PRW_town.set_context(context='zip', val=zip_code)
		self.PRW_state.set_context(context='zip', val=zip_code)
		self.PRW_country.set_context(context='zip', val=zip_code)
		return True
	#--------------------------------------------------------
	def on_town_set (self, data):
		"""
		Set postcode, country and state in accordance with the town
		"""
		zip, state_id, state, country_id, country = gmDemographicRecord.get_town_data (self.PRW_town.GetValue ())
		if zip:
			self.PRW_state.SetValue (state, state_id)
			self.PRW_zip_code.SetValue (zip)
			self.PRW_country.SetValue (country, country_id)
			self.TTC_phone.SetFocus ()
	#--------------------------------------------------------
	# public API
	#--------------------------------------------------------			
	def set_identity(self, identity):
		self.__ident = identity
			
	def save(self):
		msg = _("Data in Contacts section can't be saved.\nPlease, correct any invalid input.")
		if not self.Validate():
			gmGuiHelpers.gm_show_error(msg, _('Contacts invalid input'), gmLog.lErr)
			return False
		if not self.TransferDataFromWindow():
			gmGuiHelpers.gm_show_error(msg, _('Contacts invalid input'), gmLog.lErr)			
			return False
		if not link_contacts_from_dtd(identity = self.__ident, dtd = self.__dtd):
			msg = _("An error happened while saving Contacts section.\nPlease, refresh and check all the data.")
			gmGuiHelpers.gm_show_error(msg, _('Contacts saving error'), gmLog.lErr)
			return False
		return True		
#============================================================		
class cPatContactsPanelValidator(wx.PyValidator):
	"""
	This validator is used to ensure that the user has entered all
	the required conditional values in patietn contacts page.
	"""
	#--------------------------------------------------------
	def __init__(self, dtd):
		"""
		Validator initialization.
		@param dtd The object containing the data model.
		@type dtd A cFormDTD instance
		"""
		# initialize parent class
		wx.PyValidator.__init__(self)
		
		# validator's storage object
		self.form_DTD = dtd
	#--------------------------------------------------------
	def Clone(self):
		"""
		Standard cloner.
		Note that every validator must implement the Clone() method.
		"""
		return cPatContactsPanelValidator(dtd = self.form_DTD)		# FIXME: probably need new instance of DTD ?
	#--------------------------------------------------------
	def Validate(self, parent = None):
		"""
		Validate the contents of the given text control.
		"""
		pageCtrl = self.GetWindow().GetParent()
		address_fields = (
			pageCtrl.TTC_address_number,
			pageCtrl.PRW_zip_code,
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
		"""
		Transfer data from validator to window.
		The default implementation returns False, indicating that an error
		occurred.  We simply return True, as we don't do any data transfer.
		"""
		pageCtrl = self.GetWindow().GetParent()
		# fill in controls with values from self.form_DTD
		pageCtrl.TTC_address_number.SetValue(self.form_DTD['address_number'])
		pageCtrl.PRW_street.SetValue(self.form_DTD['street'])
		pageCtrl.PRW_zip_code.SetValue(self.form_DTD['zip_code'])
		pageCtrl.PRW_town.SetValue(self.form_DTD['town'])
		pageCtrl.PRW_country.SetValue(self.form_DTD['country'])
		pageCtrl.PRW_state.SetValue(self.form_DTD['state'])
		pageCtrl.TTC_phone.SetValue(self.form_DTD['phone'])
		return True # Prevent wxDialog from complaining.	
	#--------------------------------------------------------
	def TransferFromWindow(self):
		"""
		Transfer data from window to validator.
		The default implementation returns False, indicating that an error
		occurred.  We simply return True, as we don't do any data transfer.
		"""
		try:
			pageCtrl = self.GetWindow().GetParent()
			# fill in self.form_DTD with values from controls
			self.form_DTD['address_number'] = pageCtrl.TTC_address_number.GetValue()
			self.form_DTD['street'] = pageCtrl.PRW_street.GetValue()
			self.form_DTD['zip_code'] = pageCtrl.PRW_zip_code.GetValue()
			self.form_DTD['town'] = pageCtrl.PRW_town.GetValue()
			if not pageCtrl.PRW_state.GetData() is None:
				self.form_DTD['state'] = pageCtrl.PRW_state.GetData()
			if not pageCtrl.PRW_country.GetData() is None:
				self.form_DTD['country'] = pageCtrl.PRW_country.GetData()
			self.form_DTD['phone'] = pageCtrl.TTC_phone.GetValue()
		except:
			return False
		return True
#============================================================
class cPatOccupationsPanel(wx.Panel):
	"""
	Page containing patient occupations edition fields.
	"""
	def __init__(self, parent, id, dtd=None, ident=None):
		"""
		Creates a new instance of BasicPatDetailsPage
		@param parent - The parent widget
		@type parent - A wx.Window instance
		@param id - The widget id
		@type id - An integer
		@param dtd The object containing the data model.
		@type dtd A cFormDTD instance
		"""
		wx.Panel.__init__(self, parent, id)
		self.__dtd = dtd
		self.__ident = ident
		self.__do_layout()
	#--------------------------------------------------------
	def __do_layout(self):
		# FIXME: main panel, required for a correct propagation of validator calls.
		# If this panel doesn't exists and the validator is set
		# direclty to self, calling self.transferDataFromWindow
		# just returns true without the method in validator being
		# called. It seems that works for the children of self.
		PNL_form = wx.Panel(self, -1)		
		# occupation
		STT_occupation = wx.StaticText(PNL_form, -1, _('Occupation'))
		queries = []
		queries.append("select distinct name, name from dem.occupation where name %(fragment_condition)s")
		mp = gmMatchProvider.cMatchProvider_SQL2('demographics', queries=queries)
		mp.setThresholds(3, 5, 15)		
		self.PRW_occupation = gmPhraseWheel.cPhraseWheel (
			parent = PNL_form,
			id = -1,
			aMatchProvider = mp
		)
		self.PRW_occupation.SetToolTipString(_("primary occupation of the patient"))

		# Set validator for identity form
		PNL_form.SetValidator(cPatOccupationsPanelValidator(dtd = self.__dtd))

		# layout input widgets
		SZR_input = wx.FlexGridSizer(cols = 2, rows = 15, vgap = 4, hgap = 4)
		SZR_input.AddGrowableCol(1)				
		SZR_input.Add(STT_occupation, 0, wx.SHAPED)
		SZR_input.Add(self.PRW_occupation, 1, wx.EXPAND)
		PNL_form.SetSizerAndFit(SZR_input)
		
		# layout page
		SZR_main = wx.BoxSizer(wx.VERTICAL)
		SZR_main.Add(PNL_form, 1, wx.EXPAND)
		self.SetSizer(SZR_main)				
	#--------------------------------------------------------
	def set_identity(self, identity):
		self.__ident = identity
			
	def save(self):
		msg = _("Data in Occupations section can't be saved.\nPlease, correct any invalid input.")
		if not self.Validate():
			gmGuiHelpers.gm_show_error(msg, _('Occupations invalid input'), gmLog.lErr)			
			return False		
		if not self.TransferDataFromWindow():
			gmGuiHelpers.gm_show_error(msg, _('Occupations invalid input'), gmLog.lErr)			
			return False
		if not link_occupation_from_dtd(identity = self.__ident, dtd = self.__dtd):
			msg = _("An error happened while saving Occupations section.\nPlease, refresh and check all the data.")
			gmGuiHelpers.gm_show_error(msg, _('Occupations saving error'), gmLog.lErr)
			return False
		return True		
#============================================================		
class cPatOccupationsPanelValidator(wx.PyValidator):
	"""
	This validator is used to ensure that the user has entered all
	the required conditional values in patient occupations page.
	"""
	#--------------------------------------------------------
	def __init__(self, dtd):
		"""
		Validator initialization.
		@param dtd The object containing the data model.
		@type dtd A cFormDTD instance
		"""
		wx.PyValidator.__init__(self)
		self.form_DTD = dtd
	#--------------------------------------------------------
	def Clone(self):
		"""
		Standard cloner.
		Note that every validator must implement the Clone() method.
		"""
		return cPatOccupationsPanelValidator(dtd = self.form_DTD)		# FIXME: probably need new instance of DTD ?
	#--------------------------------------------------------
	def Validate(self, parent = None):
		"""Validate the contents of the given text control.
		"""
		return True
	#--------------------------------------------------------
	def TransferToWindow(self):
		"""
		Transfer data from validator to window.
		The default implementation returns False, indicating that an error
		occurred.  We simply return True, as we don't do any data transfer.
		"""
		pageCtrl = self.GetWindow().GetParent()
		# fill in controls with values from self.form_DTD		
		pageCtrl.PRW_occupation.SetValue(self.form_DTD['occupation'])
		return True # Prevent wxDialog from complaining.	
	#--------------------------------------------------------
	def TransferFromWindow(self):
		"""
		Transfer data from window to validator.
		The default implementation returns False, indicating that an error
		occurred.  We simply return True, as we don't do any data transfer.
		"""
		try:
			pageCtrl = self.GetWindow().GetParent()
			# fill in self.form_DTD with values from controls
			self.form_DTD['occupation'] = pageCtrl.PRW_occupation.GetValue()
		except:
			return False
		return True
#============================================================
class cNotebookedPatEditionPanel(wx.Panel, gmRegetMixin.cRegetOnPaintMixin):
	"""
	Notebook based patient edition panel.
	Composed of: notebooked patient details; restore and save buttons
	"""
	#--------------------------------------------------------
	def __init__(self, parent, id):
		"""
		Contructs a new instance of patient edition panel

		@param parent: Wx parent widget
		@param id: Wx widget id
		"""
		# Call parents constructors
		wx.Panel.__init__ (
			self,
			parent = parent,
			id = id,
			pos = wx.DefaultPosition,
			size = wx.DefaultSize,
			style = wx.NO_BORDER
		)
		gmRegetMixin.cRegetOnPaintMixin.__init__(self)
		self.__pat = gmPerson.gmCurrentPatient()
		# ui construction and event handling set up
		self.__do_layout()
		self.__register_interests()
	#--------------------------------------------------------
	# public API
	#--------------------------------------------------------
	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def __do_layout(self):
		"""
		Arrange widgets.
		"""

		# - patient edition notebook
		self.__patient_notebook = cPatEditionNotebook(self, -1)
		# - buttons
		self.__BTN_restore = wx.Button(self, -1, _('&Restore'))
		self.__BTN_restore.SetToolTipString(_('restore fields with current values from backend'))

		self.__BTN_save = wx.Button(self, -1, _('&Save'))
		self.__BTN_save.SetToolTipString(_('save patient information'))

		# - arrange
		szr_btns = wx.BoxSizer(wx.HORIZONTAL)
		szr_btns.Add(self.__BTN_restore, 0, wx.SHAPED)
		szr_btns.Add(self.__BTN_save, 0, wx.SHAPED)

		szr_main = wx.BoxSizer(wx.VERTICAL)
		szr_main.Add(self.__patient_notebook, 1, wx.EXPAND)
		szr_main.Add(szr_btns)
		self.SetSizerAndFit(szr_main)
	#--------------------------------------------------------
	# event handling
	#--------------------------------------------------------
	def __register_interests(self):
		"""Configure enabled event signals
		"""
		# wxPython events
		wx.EVT_BUTTON(self.__BTN_save, self.__BTN_save.GetId(), self._on_save)
		wx.EVT_BUTTON(self.__BTN_restore, self.__BTN_restore.GetId(), self._on_restore)
		# internal signals
		gmDispatcher.connect(signal=gmSignals.post_patient_selection(), receiver=self._on_post_patient_selection)
	#--------------------------------------------------------
	def _on_post_patient_selection(self):
		"""Patient changed."""
		self._schedule_data_reget()
	#--------------------------------------------------------
	def _on_save(self, event):
		"""Save data to backend and close editor.
		"""		
		# FIXME 0.1: Refresh values from backend rather than from the
		# original version of the DTD, so data integrity
		# can be assured. Currenlty, pat.get_identity() is
		# returning its version before save_payload().
		# FIXME post 0.1: internal signal
		if not self.__patient_notebook.save():
			#self.__patient_notebook.refresh()
			return False

		#self.__patient_notebook.refresh()
		return True
	#--------------------------------------------------------
	def _on_restore(self, event):
		"""
		Restore patient edition form with values originally
		fetched from backed, prior to any modification by
		the user.
		"""
		self.__patient_notebook.refresh()
		return True
	#--------------------------------------------------------
	# reget mixin API
	#--------------------------------------------------------
	def _populate_with_data(self):
		"""
		Populate fields in pages with data from model.
		"""
		if self.__patient_notebook.refresh():
			return True
		return False
#============================================================				
def create_identity_from_dtd(dtd=None):
	"""
	Register a new patient, given the data supplied in the 
	Data Transfer Dictionary object.

	@param basic_details_DTD Data Transfer Dictionary encapsulating all the
	supplied data.
	@type basic_details_DTD A cFormDTD instance.
	"""
	new_identity = gmPerson.create_identity (
		gender = dtd['gender'],
		dob = dtd['dob'].timestamp,
		lastnames = capitalize_first(dtd['lastnames']),
		firstnames = capitalize_first(dtd['firstnames'])
	)
	if new_identity is None:
		_log.Log(gmLog.lErr, 'cannot create identity from %s' % str(dtd))
		return None
	_log.Log(gmLog.lData, 'identity created: %s' % new_identity)
	
	return new_identity
#============================================================				
def update_identity_from_dtd(identity, dtd=None):
	"""
	Update patient details with data supplied by
	Data Transfer Dictionary object.

	@param basic_details_DTD Data Transfer Dictionary encapsulating all the
	supplied data.
	@type basic_details_DTD A cFormDTD instance.
	"""
	# identity
	if identity['gender'] != dtd['gender']:
		identity['gender'] = dtd['gender']
	if identity['dob'] != dtd['dob']:
		identity['dob'] = dtd['dob']
	if len(dtd['title']) > 0 and identity['title'] != capitalize_first(dtd['title']):
		identity['title'] = capitalize_first(dtd['title'])
	# FIXME: error checking
	# FIXME: we need a trigger to update the values of the
	# view, identity['keys'], eg. lastnames and firstnames
	# are not refreshed.
	identity.save_payload()
	# names
	# FIXME: proper handling of "active"
	if identity['firstnames'] != capitalize_first(dtd['firstnames']) or identity['lastnames'] != capitalize_first(dtd['lastnames']):
		identity.add_name(firstnames = capitalize_first(dtd['firstnames']), lastnames = capitalize_first(dtd['lastnames']), active = True, nickname = None)
	# nickname
	if len(dtd['nick']) > 0 and identity['preferred'] != capitalize_first(dtd['nick']):
		identity.set_nickname(nickname = capitalize_first(dtd['nick']))

	return True
#============================================================				
def link_contacts_from_dtd(identity, dtd=None):
	"""
	Update patient details with data supplied by
	Data Transfer Dictionary object.

	@param basic_details_DTD Data Transfer Dictionary encapsulating all the
	supplied data.
	@type basic_details_DTD A cFormDTD instance.
	"""

	# current addresses in backend
	addresses = identity['addresses']
	last_idx = -1
	if len(addresses) > 0:
		last_idx = len(addresses) - 1

	# form addresses
	input_number = dtd['address_number']
	input_street = capitalize_first(dtd['street'])
	input_postcode = dtd['zip_code']
	input_urb = capitalize_first(dtd['town'])
	input_state = dtd['state']
	input_country = dtd['country']
	if len(input_number) > 0 and len(input_street) > 0 and len(input_postcode) > 0 and len (input_state) > 0 and \
	 len(input_country) > 0 and len(input_urb) > 0 and (last_idx == -1 or (input_number != addresses[last_idx]['number'] or input_street != addresses[last_idx]['street'] or
	 input_postcode != addresses[last_idx]['postcode'] or input_urb  != addresses[last_idx]['urb'] or
	 input_state != addresses[last_idx]['state_code'] or input_country != addresses[last_idx]['country_code'])):
		identity.link_address (
			number = input_number,
			street = input_street,
			postcode = input_postcode,
			urb = input_urb,
			state = input_state,
			country = input_country
		)

	input_phone = dtd['phone']
	if len(input_phone) > 0:
		identity.link_communication (
			comm_medium = 'homephone',
			url = input_phone,
			is_confidential = False
		)

	# FIXME: error checking
	identity.save_payload()
	return True
#============================================================				
def link_occupation_from_dtd(identity, dtd=None):
	"""
	Update patient details with data supplied by
	Data Transfer Dictionary object.

	@param basic_details_DTD Data Transfer Dictionary encapsulating all the
	supplied data.
	@type basic_details_DTD A cFormDTD instance.
	"""

	occupations = identity['occupations']
	last_idx = -1
	if len(occupations) > 0:
		last_idx = len(occupations) -1
	input_occupation = dtd['occupation']
	if len(input_occupation) > 0 and (last_idx == -1 or occupations[last_idx]['occupation'] !=input_occupation):
		identity.link_occupation(occupation = input_occupation)
	return True	
#============================================================
def get_name_gender_map():
	"""
	Build from backend a cached dictionary of pairs 'firstname' : gender_tag
	"""	
	global _name_gender_map
	if _name_gender_map is None:
		#cmd = "select lower(name), gender from dem.name_gender_map"
		cmd = "select name, gender from dem.name_gender_map"
		rows = gmPG.run_ro_query('personalia', cmd, False)
		if rows is None:
			_log.Log(gmLog.lPanic, 'cannot retrieve name-gender map from database')
			return {}
		_name_gender_map = {}
		for row in rows:
			_name_gender_map[row[0].lower()] = row[1]
	return _name_gender_map
#============================================================
def capitalize_first(txt):
	txt_lst = txt.split(' ')
	if len(txt_lst) > 0:
		txt_lst[0] = txt_lst[0].capitalize()
		txt = ' '.join(txt_lst)
	return txt
#============================================================
class TestWizardPanel(wx.Panel):   
	"""
	Utility class to test the new patient wizard.
	"""
	#--------------------------------------------------------
	def __init__(self, parent, id):
		"""
		Create a new instance of TestPanel.
		@param parent The parent widget
		@type parent A wx.Window instance
		"""
		wx.Panel.__init__(self, parent, id)
		wizard = cNewPatientWizard(self)
		print wizard.RunWizard()
#============================================================
if __name__ == "__main__":
	
	try:
		
		# obtain patient
		patient = gmPerson.ask_for_patient()
		if patient is None:
			print "No patient. Exiting gracefully..."
			sys.exit(0)
		gmPerson.set_active_patient(patient=patient)
	
		a = cFormDTD(fields = cBasicPatDetailsPage.form_fields)
		
		app1 = wx.PyWidgetTester(size = (800, 600))
		app1.SetWidget(cNotebookedPatEditionPanel, -1)
		#app1.SetWidget(TestWizardPanel, -1)
		app1.MainLoop()
	
	except StandardError:
		_log.LogException("unhandled exception caught !", sys.exc_info(), 1)
		# but re-raise them
		raise
	
#	app2 = wx.PyWidgetTester(size = (800, 600))
#	app2.SetWidget(DemographicDetailWindow, -1)
#	app2.MainLoop()
#============================================================
# $Log: gmDemographicsWidgets.py,v $
# Revision 1.89  2006-06-12 18:31:31  ncq
# - must create *patient* not person from new patient wizard
#   if to be activated as patient :-)
#
# Revision 1.88  2006/06/09 14:40:24  ncq
# - use fuzzy.timestamp for create_identity()
#
# Revision 1.87  2006/06/05 21:33:03  ncq
# - Sebastian is too good at finding bugs, so fix them:
#   - proper queries for new-patient wizard phrasewheels
#   - properly validate timestamps
#
# Revision 1.86  2006/06/04 22:23:03  ncq
# - consistently use l10n_country
#
# Revision 1.85  2006/06/04 21:38:49  ncq
# - make state red as it's mandatory
#
# Revision 1.84  2006/06/04 21:31:44  ncq
# - allow characters in phone URL
#
# Revision 1.83  2006/06/04 21:16:27  ncq
# - fix missing dem. prefixes
#
# Revision 1.82  2006/05/28 20:49:44  ncq
# - gmDateInput -> cFuzzyTimestampInput
#
# Revision 1.81  2006/05/15 13:35:59  ncq
# - signal cleanup:
#   - activating_patient -> pre_patient_selection
#   - patient_selected -> post_patient_selection
#
# Revision 1.80  2006/05/14 21:44:22  ncq
# - add get_workplace() to gmPerson.gmCurrentProvider and make use thereof
# - remove use of gmWhoAmI.py
#
# Revision 1.79  2006/05/12 12:18:11  ncq
# - whoami -> whereami cleanup
# - use gmCurrentProvider()
#
# Revision 1.78  2006/05/04 09:49:20  ncq
# - get_clinical_record() -> get_emr()
# - adjust to changes in set_active_patient()
# - need explicit set_active_patient() after ask_for_patient() if wanted
#
# Revision 1.77  2006/01/18 14:14:39  sjtan
#
# make reusable
#
# Revision 1.76  2006/01/10 14:22:24  sjtan
#
# movement to schema dem
#
# Revision 1.75  2006/01/09 10:46:18  ncq
# - yet more schema quals
#
# Revision 1.74  2006/01/07 17:52:38  ncq
# - several schema qualifications
#
# Revision 1.73  2005/10/19 09:12:40  ncq
# - cleanup
#
# Revision 1.72  2005/10/09 08:10:22  ihaywood
# ok, re-order the address widgets "the hard way" so tab-traversal works correctly.
#
# minor bugfixes so saving address actually works now
#
# Revision 1.71  2005/10/09 02:19:40  ihaywood
# the address widget now has the appropriate widget order and behaviour for australia
# when os.environ["LANG"] == 'en_AU' (is their a more graceful way of doing this?)
#
# Remember our postcodes work very differently.
#
# Revision 1.70  2005/09/28 21:27:30  ncq
# - a lot of wx2.6-ification
#
# Revision 1.69  2005/09/28 19:47:01  ncq
# - runs until login dialog
#
# Revision 1.68  2005/09/28 15:57:48  ncq
# - a whole bunch of wx.Foo -> wx.Foo
#
# Revision 1.67  2005/09/27 20:44:58  ncq
# - wx.wx* -> wx.*
#
# Revision 1.66  2005/09/26 18:01:50  ncq
# - use proper way to import wx26 vs wx2.4
# - note: THIS WILL BREAK RUNNING THE CLIENT IN SOME PLACES
# - time for fixup
#
# Revision 1.65  2005/09/25 17:30:58  ncq
# - revert back to wx2.4 style import awaiting "proper" wx2.6 importing
#
# Revision 1.64  2005/09/25 01:00:47  ihaywood
# bugfixes
#
# remember 2.6 uses "import wx" not "from wxPython import wx"
# removed not null constraint on clin_encounter.rfe as has no value on instantiation
# client doesn't try to set clin_encounter.description as it doesn't exist anymore
#
# Revision 1.63  2005/09/24 09:17:27  ncq
# - some wx2.6 compatibility fixes
#
# Revision 1.62  2005/09/12 15:09:00  ncq
# - make first tab display first in demographics editor
#
# Revision 1.61  2005/09/04 07:29:53  ncq
# - allow phrasewheeling states by abbreviation in new-patient wizard
#
# Revision 1.60  2005/08/14 15:36:54  ncq
# - fix phrasewheel queries for country matching
#
# Revision 1.59  2005/08/08 08:08:35  ncq
# - cleanup
#
# Revision 1.58  2005/07/31 14:48:44  ncq
# - catch exceptions in TransferToWindow
#
# Revision 1.57  2005/07/24 18:54:18  ncq
# - cleanup
#
# Revision 1.56  2005/07/04 11:26:50  ncq
# - re-enable auto-setting gender from firstname, and speed it up, too
#
# Revision 1.55  2005/07/02 18:20:22  ncq
# - allow English input of country as well, regardless of locale
#
# Revision 1.54  2005/06/29 15:03:32  ncq
# - some cleanup
#
# Revision 1.53  2005/06/28 14:38:21  cfmoro
# Integration fixes
#
# Revision 1.52  2005/06/28 14:12:55  cfmoro
# Integration in space fixes
#
# Revision 1.51  2005/06/28 13:11:05  cfmoro
# Fixed bug: when updating patient details the dob was converted from date to str type
#
# Revision 1.50  2005/06/14 19:51:27  cfmoro
# auto zip in patient wizard and minor cleanups
#
# Revision 1.49  2005/06/14 00:34:14  cfmoro
# Matcher provider queries revisited
#
# Revision 1.48  2005/06/13 01:18:24  cfmoro
# Improved input system support by zip, country
#
# Revision 1.47  2005/06/12 22:12:35  ncq
# - prepare for staged (constrained) queries in demographics
#
# Revision 1.46  2005/06/10 23:22:43  ncq
# - SQL2 match provider now requires query *list*
#
# Revision 1.45  2005/06/09 01:56:41  cfmoro
# Initial code on zip -> (auto) address
#
# Revision 1.44  2005/06/09 00:26:07  cfmoro
# PhraseWheels in patient editor. Tons of cleanups and validator fixes
#
# Revision 1.43  2005/06/08 22:03:02  cfmoro
# Restored phrasewheel gender in wizard
#
# Revision 1.42  2005/06/08 01:25:42  cfmoro
# PRW in wizards state and country. Validator fixes
#
# Revision 1.41  2005/06/04 10:17:51  ncq
# - cleanup, cSmartCombo, some comments
#
# Revision 1.40  2005/06/03 15:50:38  cfmoro
# State and country combos y patient edition
#
# Revision 1.39  2005/06/03 13:37:45  cfmoro
# States and country combo selection. SmartCombo revamped. Passing country and state codes instead of names
#
# Revision 1.38  2005/06/03 00:56:19  cfmoro
# Validate dob in patient wizard
#
# Revision 1.37  2005/06/03 00:37:33  cfmoro
# Validate dob in patient identity page
#
# Revision 1.36  2005/06/03 00:01:41  cfmoro
# Key fixes in new patient wizard
#
# Revision 1.35  2005/06/02 23:49:21  cfmoro
# Gender use SmartCombo, several fixes
#
# Revision 1.34  2005/06/02 23:26:41  cfmoro
# Name auto-selection in new patient wizard
#
# Revision 1.33  2005/06/02 12:17:25  cfmoro
# Auto select gender according to firstname
#
# Revision 1.32  2005/05/28 12:18:01  cfmoro
# Capitalize name, street, etc
#
# Revision 1.31  2005/05/28 12:00:53  cfmoro
# Trigger FIXME to reflect changes in v_basic_person
#
# Revision 1.30  2005/05/28 11:45:19  cfmoro
# Retrieve names from identity cache, so refreshing will be reflected
#
# Revision 1.29  2005/05/25 23:03:02  cfmoro
# Minor fixes
#
# Revision 1.28  2005/05/24 19:57:14  ncq
# - cleanup
# - make cNotebookedPatEditionPanel a gmRegetMixin child instead of cPatEditionNotebook
#
# Revision 1.27  2005/05/23 12:01:08  cfmoro
# Create/update comms
#
# Revision 1.26  2005/05/23 11:16:18  cfmoro
# More cleanups and test functional fixes
#
# Revision 1.25  2005/05/23 09:20:37  cfmoro
# More cleaning up
#
# Revision 1.24  2005/05/22 22:12:06  ncq
# - cleaning up patient edition notebook
#
# Revision 1.23  2005/05/19 16:06:50  ncq
# - just silly cleanup, as usual
#
# Revision 1.22  2005/05/19 15:25:53  cfmoro
# Initial logic to update patient details. Needs fixing.
#
# Revision 1.21  2005/05/17 15:09:28  cfmoro
# Reloading values from backend in repopulate to properly reflect patient activated
#
# Revision 1.20  2005/05/17 14:56:02  cfmoro
# Restore values from model to window action function
#
# Revision 1.19  2005/05/17 14:41:36  cfmoro
# Notebooked patient editor initial code
#
# Revision 1.18  2005/05/17 08:04:28  ncq
# - some cleanup
#
# Revision 1.17  2005/05/14 14:56:41  ncq
# - add Carlos' DTD code
# - numerous fixes/robustification
# move occupation down based on user feedback
#
# Revision 1.16  2005/05/05 06:25:56  ncq
# - cleanup, remove _() in log statements
# - re-ordering in new patient wizard due to user feedback
# - add <activate> to RunWizard(): if true activate patient after creation
#
# Revision 1.15  2005/04/30 20:31:03  ncq
# - first-/lastname were switched around when saving identity into backend
#
# Revision 1.14  2005/04/28 19:21:18  cfmoro
# zip code streamlining
#
# Revision 1.13  2005/04/28 16:58:45  cfmoro
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
#   Why ? Because we can then do a simple replace wx. -> wx. for 2.5 code.
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
# wx.BasePlugin is unnecessarily specific.
#
# Revision 1.17  2003/02/09 11:57:42  ncq
# - cleanup, cvs keywords
#
# old change log:
#	10.06.2002 rterry initial implementation, untested
#	30.07.2002 rterry images put in file
