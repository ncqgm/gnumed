# -*- coding: utf-8 -*-
#############################################################################
#
# gmDrugDisplay_RT  Feedback: anything which is incorrect or ambiguous please
#                   mailto rterry@gnumed.net
# ---------------------------------------------------------------------------
#
# @author: Dr. Richard Terry
# @author: Dr. Herb Horst
# @author: Hilmar Berger
# @acknowledgments: Gui screen Design taken with permission from
#                   DrsDesk MimsAnnual @ DrsDesk Software 1995-2002
#                   and @ Dr.R Terry
#                   Basic skeleton of this code written by Dr. H Horst
#                   heavily commented for learning purposes by Dr. R Terry
# @copyright: authors
# @license: GPL v2 or later (details at http://www.gnu.org)
#
# @TODO:
#	 decision of text display wigit
#        why won't opening frame size be recognised
#        put in testing for null field in Display_PI
#        so as not to display a null field heading
#        Need config file with:
#        HTML font options for heading, subheading, subsubheading etc
############################################################################
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gui/gmDrugDisplay.py,v $
__version__ = "$Revision: 1.34 $"
__author__ = "H.Herb, R.Terry, H.Berger"

import string


import wx


_log = logging.getLogger('gm.ui')
if __name__ == "__main__":
	# FIXME: standalone means diagnostics for now,
	# later on, when AmisBrowser is one foot in the door
	# to German doctors we'll change this again
	_log.SetAllLogLevels(gmLog.lData)
	from Gnumed.pycommon import gmI18N


from Gnumed.pycommon import gmDrugView, gmCfg, gmExceptions
from Gnumed.wxpython import gmGuiHelpers
from Gnumed.business import gmPraxis

_cfg = gmCfg.gmDefCfgFile
#============================================================
# These constants are used when referring to menu items below
#============================================================
ID_ABOUT = wx.NewId()
ID_CONTENTS = wx.NewId()
ID_EXIT  =  wx.NewId()
ID_OPEN= wx.NewId()
ID_HELP =  wx.NewId()
ID_TEXTCTRL =  wx.NewId()
ID_TEXT = wx.NewId()
ID_COMBO_PRODUCT = wx.NewId()
ID_RADIOBUTTON_BYANY = wx.NewId()
ID_RADIOBUTTON_BYPRODUCT = wx.NewId()
ID_RADIOBUTTON_BYGENERIC = wx.NewId()
ID_RADIOBUTTON_BYINDICATION = wx.NewId()
ID_LISTBOX_JUMPTO = wx.NewId()
ID_LISTCTRL_DRUGCHOICE = wx.NewId()
ID_BUTTON_PRESCRIBE = wx.NewId()
ID_BUTTON_DISPLAY = wx.NewId()
ID_BUTTON_PRINT = wx.NewId()
ID_BUTTON_BOOKMARK = wx.NewId()

MODE_PRODUCT = 0
MODE_GENERIC = 1
MODE_INDICATION = 2
MODE_ANY = 3	# search for product name and generic name

#============================================================
class DrugDisplay(wx.Panel):
	"""displays drug information in a convenience widget"""

	NoDrugFoundMessageHTML	= "<HTML><HEAD></HEAD><BODY BGCOLOR='#FFFFFF8'> <FONT SIZE=3>" +     _("No matching drug found.") + "</FONT></BODY></HTML>"
	WelcomeMessageHTML 	= "<HTML><HEAD></HEAD><BODY BGCOLOR='#FFFFFF8'> <FONT SIZE=3>" +     _("Please enter at least three digits of the drug name.") + "</FONT></BODY></HTML>"

	def __init__(self, parent, id, pos = wxDefaultPosition, 
				 size = wxDefaultSize, style = wx.TAB_TRAVERSAL):

		wx.Panel.__init__(self, parent, id, pos, size, style)

		# if we are not inside gnumed we won't get a definite answer on
		# who and where we are. in this case try to get config source 
		# from main config file (see gmCfg on how the name of this file
		# is determined
		# this is necessary to enable stand alone use of the drug browser
		currworkplace = gmPraxis.gmCurrentPraxisBranch().active_workplace
		if currworkplace is None:
			# assume we are outside gnumed
			self.dbName = _cfg.get('DrugReferenceBrowser', 'drugDBname')
		else:
			self.dbName, match = gmCfg.getDBParam(
				currworkplace,
				option="DrugReferenceBrowser.drugDBName"
			)

		if self.dbName is None:
			if __name__ == '__main__':
				title = _('Starting drug data browser')
				msg = _('Cannot start the drug data browser.\n\n'
						'There is no drug database specified in the configuration.')
				gmGuiHelpers.gm_show_error(msg, title)
			_log.Log(gmLog.lErr, "No drug database specified. Aborting drug browser.")
			# FIXME: we shouldn't directly call Close() on the parent
#			parent.Close()
			raise gmExceptions.ConstructorError("No drug database specified")

                # initialize interface to drug database.
		# this will fail if backend or config files are not available
		try:    
			self.mDrugView=gmDrugView.DrugView(self.dbName)
		except Exception:
			_log.LogException("Unhandled exception during DrugView API init.", sys.exc_info(), verbose = 0)
			raise gmExceptions.ConstructorError("Couldn't initialize DrugView API")
#			return None

		self.mode = MODE_PRODUCT
		self.previousMode = MODE_PRODUCT
		self.printer = wx.HtmlEasyPrinting()		#printer object to print html page
		self.mId = None
		self.drugProductInfo = None            
		self.__mListCtrlItems = {}		# array holding data on every row in the list
        
		#-------------------------------------------------------------
		# These things build the physical window that you see when
		# the program boots. They each refer to a subroutine that
		# is listed below by the same name eg def Menus_Create(self)
		#-------------------------------------------------------------
		self.GuiElements_Init()	    # add main gui elements
		self.inDisplay_PI = 0	    # first we display a drug list, not product info
		self.GetDrugIssue() 	    # ?

		#--------------------------------------------------------------
		# handler declarations for DrugDisplay
		# note handlers for menu in Menus_Create()
		#--------------------------------------------------------------
		wx.EVT_BUTTON(self, ID_BUTTON_PRINT, self.OnPrint)
		wx.EVT_BUTTON(self, ID_BUTTON_DISPLAY, self.OnDisplay)
		wx.EVT_BUTTON(self, ID_BUTTON_PRESCRIBE, self.OnPrescribe)
		wx.EVT_LISTBOX_DCLICK(self, ID_LISTBOX_JUMPTO, self.OnJumpToDblClick)
		wx.EVT_LISTBOX(self, ID_LISTBOX_JUMPTO, self.OnJumpToSelected)
		wx.EVT_LIST_ITEM_ACTIVATED(self, ID_LISTCTRL_DRUGCHOICE, self.OnDrugChoiceDblClick)
		wx.EVT_RADIOBUTTON(self, ID_RADIOBUTTON_BYINDICATION, self.OnSearchByIndication)
		wx.EVT_RADIOBUTTON(self, ID_RADIOBUTTON_BYGENERIC, self.OnSearchByGeneric)
		wx.EVT_RADIOBUTTON(self, ID_RADIOBUTTON_BYPRODUCT, self.OnSearchByProduct)
		wx.EVT_RADIOBUTTON(self, ID_RADIOBUTTON_BYANY, self.OnSearchByAny)
		wx.EVT_TEXT(self, ID_COMBO_PRODUCT, self.OnProductKeyPressed)
		wx.EVT_COMBOBOX(self, ID_COMBO_PRODUCT, self.OnProductSelected)
		wx.EVT_BUTTON(self, wxID_OK, self.OnOk)
		wx.EVT_BUTTON(self, wxID_CANCEL, self.OnCancel)
		wx.EVT_BUTTON(self,ID_BUTTON_BOOKMARK, self.OnBookmark)
#-----------------------------------------------------------------------------------------------------------------------

	def GuiElements_Init(self):
		#--------------------------------------------------
		# create the controls for left hand side of screen
		# 1)create the label 'Find' and the combo box the
		#   user will type the name of drug into
		#--------------------------------------------------
		finddrug = wxStaticText( self, -1, _("   Find   "), wxDefaultPosition, wxDefaultSize, 0 )
		finddrug.SetFont( wxFont( 14, wxSWISS, wx.NORMAL, wx.NORMAL ) )
		
		self.comboProduct = wxComboBox(
			self,
			ID_COMBO_PRODUCT, 
			"", 
			wxDefaultPosition, 
			wxSize(130,-1),
			[] , 
			wxCB_DROPDOWN 
		)
		self.comboProduct.SetToolTip( wx.ToolTip(_("Enter the name of the drug you are interested in")) )
		self.btnBookmark = wx.Button( 
			self, 
			ID_BUTTON_BOOKMARK, 
			_("&Bookmark"), 
			wxDefaultPosition, 
			wxDefaultSize, 
			0 
		)
		#-----------------------------------------------------------
		# create a sizer at topleft of screen to hold these controls
		# and add them to it
		#-----------------------------------------------------------
		self.sizertopleft = wx.BoxSizer(wx.HORIZONTAL)
		self.sizertopleft.Add( finddrug, 0, wxALIGN_CENTER_VERTICAL, 5 )
		self.sizertopleft.Add( self.comboProduct, 1, wxGROW|wxALIGN_CENTER_VERTICAL, 5 )
		self.sizertopleft.Add( self.btnBookmark, 0, wxALIGN_CENTER_VERTICAL, 5 )
		#---------------------------------------------------------------
		# next create the left sizer which will hold the drug list box 
		# and the html viewer
		#---------------------------------------------------------------
		self.sizer_left = wx.BoxSizer( wx.VERTICAL )
		self.sizer_left.AddSpacer( 30, 10, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxALL, 1 )
		self.sizer_left.AddSizer( self.sizertopleft, 0, wxGROW|wxALIGN_CENTER_VERTICAL, 5)
		self.sizer_left.AddSpacer( 1, 1, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxALL, 1 )
		self.listctrl_drugchoice=None
		self.html_viewer=None
		self.whichWidget = "listctrl_drugchoice"
		self.ToggleWidget()
		self.html_viewer.SetPage(self.WelcomeMessageHTML)
        
		#------------------------------------------------------------------------
		# the search by option buttons sit on a wxStaticBoxSizer with wx.Vertical
		# 1) create a wxStaticBox = bordered box with title search by
		# 2) add this to the sizerSearchBy sizer
		# 3) Add four radio buttons to this sizer
		#------------------------------------------------------------------------
		sboxSearchBy = wxStaticBox( self, -1, _("Search by") )
		self.sizerSearchBy = wxStaticBoxSizer( sboxSearchBy, wx.VERTICAL )
		sboxSearchBy.SetFont( wxFont( 10, wxSWISS, wx.NORMAL, wx.NORMAL ) )
		
		self.rbtnSearchAny = wxRadioButton( self, ID_RADIOBUTTON_BYANY, _("Any"), wxDefaultPosition, wxDefaultSize, 0 )
		self.sizerSearchBy.Add( self.rbtnSearchAny, 0, wxGROW|wxALIGN_CENTER_VERTICAL, 1 )
		self.rbtnSearchProduct = wxRadioButton( self, ID_RADIOBUTTON_BYPRODUCT, _("Product name"), wxDefaultPosition, wxDefaultSize, 0 )
		self.sizerSearchBy.Add( self.rbtnSearchProduct, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wx.TOP, 1 )
		self.rbtnSearchGeneric = wxRadioButton( self, ID_RADIOBUTTON_BYGENERIC, _("Generic name"), wxDefaultPosition, wxDefaultSize, 0 )
		self.sizerSearchBy.Add( self.rbtnSearchGeneric, 0, wxGROW|wxALIGN_CENTER_VERTICAL, 1 )
		self.rbtnSearchIndication = wxRadioButton( self, ID_RADIOBUTTON_BYINDICATION, _("Indication"), wxDefaultPosition, wxDefaultSize, 0 )
		self.sizerSearchBy.Add( self.rbtnSearchIndication, 0, wxGROW|wxALIGN_CENTER_VERTICAL, 1 )
		#-------------------------------------------------------------------------
		# and the right hand side vertical side bar sizer
		# 1) add a space at top to make the static text box even with the top
		#    of the main drug data display box
		# 2) add the searchby static box with the radio buttons which is stuck on
		#    to its own sizer
		# 3) add a spacer below this and above the list box underneath
		#-------------------------------------------------------------------------
		self.sizerVInteractionSidebar = wx.BoxSizer( wx.VERTICAL )
		self.sizerVInteractionSidebar.AddSpacer( 30, 10, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxALL, 12 )
		self.sizerVInteractionSidebar.AddSizer( self.sizerSearchBy, 0, wxGROW|wxALIGN_CENTER_VERTICAL, 5 )
		self.sizerVInteractionSidebar.AddSpacer( 30, 10, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxALL, 1 )
		#--------------------------------------------------------------------------
		# 4) create a listbox that will be populated with labels to jump to within the
		#    product info text and add to the vertical side bar
		#--------------------------------------------------------------------------
		self.listbox_jumpto = wx.ListBox( self, ID_LISTBOX_JUMPTO, wxDefaultPosition, wxSize(150,100),
			[] , wx.LB_SINGLE )
		self.sizerVInteractionSidebar.Add( self.listbox_jumpto, 1, wxGROW|wxALIGN_CENTER_VERTICAL, 10 )
		#--------------------------------------------------------------------------
		# 5) Add another spacer underneath this listbox
		#--------------------------------------------------------------------------
		self.sizerVInteractionSidebar.AddSpacer( 20, 10, 0, wxALIGN_CENTRE|wxALL, 1 )
		self.btnPrescribe = wx.Button( self, ID_BUTTON_PRESCRIBE, _("&Prescribe"), wxDefaultPosition, wxDefaultSize, 0 )
		self.sizerVInteractionSidebar.Add( self.btnPrescribe, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxALL, 1 )
		self.btnDisplay = wx.Button( self, ID_BUTTON_DISPLAY, _("&Display"), wxDefaultPosition, wxDefaultSize, 0 )
		self.sizerVInteractionSidebar.Add( self.btnDisplay, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxALL, 1 )
		self.btnPrint = wx.Button( self, ID_BUTTON_PRINT, _("&Print"), wxDefaultPosition, wxDefaultSize, 0 )
		self.sizerVInteractionSidebar.Add( self.btnPrint, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxALL, 1 )
		#-----------------------------------------------
		# finally create the main sizer to hold the rest
		# and all the sizers to the main sizer
		#---------------------------------------------
		self.sizermain = wx.BoxSizer(wx.HORIZONTAL)
		self.sizermain.AddSizer(self.sizer_left, 1, wxGROW|wxALIGN_CENTER_HORIZONTAL|wxALL, 7)
		self.sizermain.AddSizer(self.sizerVInteractionSidebar, 0, wxGROW|wxALIGN_LEFT|wxALL, 8)
		self.SetAutoLayout( True )
		self.SetSizer( self.sizermain )
		self.sizermain.Fit( self )
		self.sizermain.SetSizeHints( self )

#----------------------------------------------------------------------------------------------------------------------
	#--------------------------------
	# methods for DrugDisplay
	#--------------------------------

	def OnDrugChoiceDblClick(self,event):
		"""
		handle double clicks in list of drugs / substances.
		"""
		# get row of selected event
		item = event.GetData()
		# get drug id and query mode
		mode, code = self.__mListCtrlItems[item]
#		gmLog.gmDefLog.Log (gmLog.lData,  "mode %s ,text code: %s" % (mode,code) )
		# show detailed info
		if mode == MODE_PRODUCT:
			self.ToggleWidget ()
			self.Display_PI (code)
		elif mode == MODE_GENERIC:
			self.Display_Generic (code)
		elif mode == MODE_INDICATION:
			pass
		return
	
	#----------------------------------------------------------------------------------------------------------------------
	def GetDrugIssue(self):
		# display some info on what database we are currently using
		self.SetTitle(self.dbName)
#		gmLog.gmDefLog.Log (gmLog.lData, "got the issue date")
		return True


	#----------------------------------------------------------------------------------------------------------------------
	def OnBookmark(self,event):
		pass

	#-----------------------------------------------------------------------------------------------------------------------------
	def ToggleWidget(self):
		"""
		Swaps listctrl to HTML viewer widget and vice versa.
		"""
		if self.whichWidget == "listctrl_drugchoice":
			if self.html_viewer is not None:
				return
			if self.listctrl_drugchoice is not None:
				self.sizer_left.Remove(self.listctrl_drugchoice)
				self.listctrl_drugchoice = None
			self.html_viewer = wx.HtmlWindow(self, -1, size=(400, 200))			
			self.sizer_left.Add( self.html_viewer, 1, wxGROW|wxALIGN_CENTER_HORIZONTAL, 5 )
			self.sizer_left.Layout()
			self.whichWidget="html_viewer"
		else:
			if self.listctrl_drugchoice is not None:
				return
			if self.html_viewer is not None:
				self.sizer_left.Remove(self.html_viewer)
				self.html_viewer = None
			self.listctrl_drugchoice = wx.ListCtrl(self, ID_LISTCTRL_DRUGCHOICE, wxDefaultPosition, wxSize(400,200), style=wx.LC_SINGLE_SEL | wx.LC_REPORT )
			self.sizer_left.Add( self.listctrl_drugchoice, 1, wxGROW|wxALIGN_CENTER_HORIZONTAL, 5 )
			self.sizer_left.Layout()
			self.whichWidget="listctrl_drugchoice"
	
	#-----------------------------------------------------------------------------------------------------------------------------
	def Drug_Find(self):
		#--------------------------------------------------------
		# using text in listctrl_drugchoice to find any similar drugs
		#--------------------------------------------------------
		self.mId = None
		drugtofind = string.lower(self.comboProduct.GetValue())
		# if we entered *, show all entries found in index (that might take time)
		searchmode = 'exact'
		if drugtofind == '***':
			searchmode = 'complete'

		# tell the DrugView abstraction layer to do an index search 
		# on product/generic/indication 
		# expect a dictionary containing at least name & ID 
		# qtype will be set by radiobuttons
		# qtype and ID form (virtually) a unique ID that can be used to access other data in the db

		qtype = self.mode
		result = self.mDrugView.SearchIndex(self.mode,drugtofind,searchmode)

		# no drug found for this name
		if result is None or len(result['id']) < 1:
			# tell everybody that we didn't find a match
			self.mId = None
			self.drugProductInfo = None            
			# display message
			if self.whichWidget == 'listctrl_drugchoice':
				self.ToggleWidget ()
			self.html_viewer.SetPage(self.NoDrugFoundMessageHTML)
			return 

		numOfRows = len(result['id'])		
	   	# found exactly one drug
		if numOfRows == 1:
			seld.mId = result['id']
			# if we found a drug *product*, show the product info
			if qtype == MODE_PRODUCT:
				if self.whichWidget == 'listctrl_drugchoice':
					self.ToggleWidget ()
					self.Display_PI (self.mId)
				elif self.mId != self.mLastId: # don't change unless different drug
					self.Display_PI (self.mId)
					self.mLastId = self.mId
			# if we found a generic substance name, show all products
			# containing this generic
			elif qtype == MODE_GENERIC:
				self.Display_Generic (self.mId)
			# if we are browsing indications, show all generics + products
			# that match. Display Indication 
			elif qtype == MODE_INDICATION:
				self.Display_Indication(self.mId)

		# we have more than one result
		# -> display a list of all matching names
		else:
			if self.whichWidget == 'html_viewer':
				self.ToggleWidget ()
			# show list
			self.BuildListCtrl(result,qtype)

	#---------------------------------------------------------------------------------------------------------------------------
	def Display_Generic (self, aId):
		"""
		Find all drug products that contain a certain generic substance and 
        display them
		"""
		productsList=self.mDrugView.getProductsForGeneric(aId)

		if type(productsList['name']) == type([]):
			res_num=len (productsList['name'])
		else:
			res_num = 1
		
		qtype = MODE_PRODUCT
		# no product - should be an error, but AMIS allows that :(
		if productsList is None or res_num == 0:
			gmLog.gmDefLog.Log (gmLog.lWarn,  "No drug product available containing generic ID: %s" % str(aId) )
			if self.whichWidget == 'listctrl_drugchoice':
				self.ToggleWidget ()
			self.html_viewer.SetPage(self.NoDrugFoundMessageHTML)
			return None        	
		# one product, so display product information
		if res_num == 1:
			if self.whichWidget == 'listctrl_drugchoice':
				self.ToggleWidget ()
			self.Display_PI (productsList['id'])
		else:
			# multiple products, display list
			if self.whichWidget == 'html_viewer':
				self.ToggleWidget ()
			# show list
			self.BuildListCtrl(productsList,qtype)

			return True

	#-----------------------------------------------------------------
	def BuildListCtrl(self, aDataDict=None, dtype=None):
		"""
		Sets all the ListCtrl widget to display the items found in 
		a database search. 
		The DataDict must at least have the keys 'id' and 'name', all 
		additional columns will be displayed in alphabetical order.
		Column names will be derived from key names.
		"""
		# clear old data
		self.listctrl_drugchoice.ClearAll ()
		self.__mListCtrlItems = {}

		if aDataDict is None or not ('id' in aDataDict & 'name' in aDataDict):
			_log.Log(gmLog.lWarn, "No data to build list control.")
			return None
		#print "1:", aDataDict['id']
		# get column names from aDataDict key names
		# remove 'id' and display name at leftmost position
		columns = list(aDataDict)
		columns.remove('id')
		columns.remove('name')
		columns.insert(0,'name')
		
		# number of rows (products, drugs, substances etc.) found
		numOfRows = len(aDataDict['id'])
			
		# set column names			
		# add columns for each parameter fetched
		col_no = 0
		for col in columns:
			self.listctrl_drugchoice.InsertColumn(col_no, col)
			col_no += 1
		# hide ListCtrl for performance reasons
		self.listctrl_drugchoice.Hide()
		# loop through all products (rows)
		for row in range(0,numOfRows):
			col_no = 0
		# for each product, display all parameters available 
        	# code taken from gmSQLListCtrl.py
			for col in columns:
				# item text
				item_text = str(aDataDict[col][row])
		
				# if first column, insert new column and
				# and store pointer to item data (type,id)
				if col_no == 0:
					item=self.listctrl_drugchoice.InsertItem (row,item_text)
					self.listctrl_drugchoice.SetItemData(item,item)
					id = aDataDict['id'][row]
			    	# set data as type and database ID
					self.__mListCtrlItems[item]=(dtype,id)
				else:
					self.listctrl_drugchoice.SetItem(row,col_no,item_text)
				col_no += 1
		# finally set column widths to AUTOSIZE
		for i in range(0,len(columns)):
			self.listctrl_drugchoice.SetColumnWidth(i, wx.LIST_AUTOSIZE)
		# set focus to first item
		firstItemState=self.listctrl_drugchoice.GetItemState(0,wx.LIST_STATE_FOCUSED | wx.LIST_STATE_SELECTED)
		self.listctrl_drugchoice.SetItemState(0,wx.LIST_STATE_FOCUSED | wx.LIST_STATE_SELECTED, wx.LIST_STATE_FOCUSED | wx.LIST_STATE_SELECTED)
		# show the listctrl
		self.listctrl_drugchoice.Show()
		# save data for further use 
		self.LastDataDict = aDataDict
		return
					
	#-----------------------------------------------------------------------------------------------------------------------------
	def Display_PI(self, aId=None):
		"""
		Shows product information on a drug specified by aID.
		"""	
		# this is to stop recursion! 
		self.inDisplay_PI = 1
		# if no aId has been specified, return
		if aId == None:
			return None
		# remember Id for further use (display refresh etc.)
		self.mId = aId
		# getProductInfo returns a HTML-formatted page 
		(self.drugProductInfo,self.drugPIHeaders)=self.mDrugView.getProductInfo(aId)
#		self.comboProduct.SetValue(result[0]['product'])
		self.inDisplay_PI = 0
		# show info page
		self.html_viewer.SetPage(self.drugProductInfo)
		# set jumpbox items
		self.listbox_jumpto.Clear()
		self.listbox_jumpto.InsertItems(self.drugPIHeaders,0)
		return True

#--------------------------------------------------------------------------------------------------------------------------------------------------
	def TransferDataToWindow(self):
		gmLog.gmDefLog.Log (gmLog.lData,  "Transfer data to Window")
		return True

	def TransferDataFromWindow(self):
		return True

	# handler implementations for DrugDisplay

	def OnPrint(self, event):
		"""
		If product info is available, print it.
		"""
		if not self.drugProductInfo is None:
			self.printer.PrintText(self.drugProductInfo)
		return True

	def OnDisplay(self, event):
		"""
		Redisplay product info.
		"""
		if not self.mId is None:
			self.Display_PI(self.mId)
		pass

	def OnPrescribe(self, event):		
		pass

	def OnJumpToDblClick(self, event):
		pass

	def OnJumpToSelected(self, event):
		"""
		Jump to product info section selected by double-clicking a line in jumpbox.
		"""
		tagname = self.listbox_jumpto.GetString(self.listbox_jumpto.GetSelection())
		self.html_viewer.LoadPage('#' + tagname)

	#--------------- handler for query mode radiobuttons --------------------
	def OnSearchByIndication(self, event):
		self.mode = MODE_INDICATION
		self.ClearInfo()
        
	def OnSearchByGeneric(self, event):
		self.mode = MODE_GENERIC
		self.ClearInfo()

	def OnSearchByProduct(self, event):
		self.mode = MODE_PRODUCT
		self.ClearInfo()

	def OnSearchByAny(self, event):
		self.mode = MODE_ANY
		self.ClearInfo()

	# Rewrote this
	def OnProductKeyPressed(self, event):
		# first, do not recur when setting the box ourselves!
		if not self.inDisplay_PI:
			entry_string = self.comboProduct.GetValue()
			# wait until at least 3 letters has been entered 
		# to reduce result set
			if len(entry_string) > 2:
				self.Drug_Find()


	def OnProductSelected(self, event):
		#----------------------------------------------
		# get product information for drug in the combo
		#----------------------------------------------
		#self.comboProduct.SetValue(self.comboProduct.GetString(1))
		#self.Drug_Find()
		pass

	def OnOk(self, event):
		event.Skip(True)

	def OnCancel(self, event):
		event.Skip(True)

	def ClearInfo(self):
		"""clears the search result list and jumpbox when query mode changed."""		
		if self.mode == self.previousMode:
			return
		self.previousMode = self.mode
		if self.listctrl_drugchoice is not None:
			self.listctrl_drugchoice.ClearAll()
		else:
			self.ToggleWidget()
		self.listbox_jumpto.Clear()
		self.comboProduct.SetValue("")
		# display welcome message
		self.whichWidget = "listctrl_drugchoice"
		self.ToggleWidget()
		self.html_viewer.SetPage(self.WelcomeMessageHTML)
        
#==================================================
# Shall we just test this module?
if __name__ == "__main__":
	app = wxPyWidgetTester(size = (640, 400))
	app.SetWidget(DrugDisplay, -1)
	app.MainLoop()
else:
	#=================================================
	# make this into GNUMed plugin

	from Gnumed.pycommon import gmI18N
	from Gnumed.wxpython import gmPlugin

	class gmDrugDisplay (gmPlugin.cNotebookPlugin):
	
		def name (self):
			return _("DrugBrowser")

		def MenuInfo (self):
			return ("view", _("&DrugBrowser"))

		def GetWidget (self, parent):
			return DrugDisplay (parent, -1)

#==================================================
