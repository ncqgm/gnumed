#!/usr/bin/python
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
# @dependencies: wxPython (>= version 2.3.1)
#
#
# @TODO: all testing and review by hhorst
#	 decision of drug data source
#	 decision of text display wigit
#        why won't opening frame size be recognised
#        put in testing for null field in Display_PI
#        so as not to display a null field heading
#        Need config file with:
#        HTML font options for heading, subheading, subsubheading etc
############################################################################

#===========================================================================
# firstly in wxPython you have to import any modules we want to use, here
# we import the 'lot' from wxPython and some specific ones from Python ie
# time,
#===========================================================================
from wxPython.wx import *
from wxPython.stc import *
from wxPython.html import *
import wxPython.lib.wxpTag
from wxPython.lib.splashscreen import SplashScreen

import string
import keyword
import time
import pdb
import re
import os.path

# location of our modules
if __name__ == "__main__":
	sys.path.append(os.path.join('.', 'modules'))

import gmLog
_log = gmLog.gmDefLog
if __name__ == "__main__":
	# FIXME: standalone means diagnostics for now,
	# later on, when AmisBrowser is one foot in the door
	# to German doctors we'll change this again
	_log.SetAllLogLevels(gmLog.lData)

import gmPG, gmDrugView
import gmCfg
_cfg = gmCfg.gmDefCfgFile

#============================================================
# These constants are used when referring to menu items below
#============================================================
ID_ABOUT = wxNewId()
ID_CONTENTS = wxNewId()
ID_EXIT  =  wxNewId()
ID_OPEN= wxNewId()
ID_HELP =  wxNewId()
ID_TEXTCTRL =  wxNewId()
ID_TEXT = wxNewId()
ID_COMBO_PRODUCT = wxNewId()
ID_RADIOBUTTON_BYANY = wxNewId()
ID_RADIOBUTTON_BYBRAND = wxNewId()
ID_RADIOBUTTON_BYGENERIC = wxNewId()
ID_RADIOBUTTON_BYINDICATION = wxNewId()
ID_LISTBOX_JUMPTO = wxNewId()
ID_LISTCTRL_DRUGCHOICE = wxNewId()
ID_BUTTON_PRESCRIBE = wxNewId()
ID_BUTTON_DISPLAY = wxNewId()
ID_BUTTON_PRINT = wxNewId()
ID_BUTTON_BOOKMARK = wxNewId()

MODE_BRAND = 0
MODE_GENERIC = 1
MODE_INDICATION = 2
MODE_ANY = 3	# search for brand name and generic name 


class DrugDisplay(wxPanel):
	"displays drug information in a convenience widget"

	NoDrugFoundMessageHTML	= "<HTML><HEAD></HEAD><BODY BGCOLOR='#FFFFFF8'> <FONT SIZE=3>" +     _("No matching drug found.") + "</FONT></BODY></HTML>"
	WelcomeMessageHTML 		= "<HTML><HEAD></HEAD><BODY BGCOLOR='#FFFFFF8'> <FONT SIZE=3>" +     _("Please enter at least three digits of the drug name.") + "</FONT></BODY></HTML>"

	def __init__(self, parent, id, pos = wxPyDefaultPosition, 
				 size = wxPyDefaultSize, style = wxTAB_TRAVERSAL):

		wxPanel.__init__(self, parent, id, pos, size, style)
		
		self.dbName = _cfg.get('DrugReferenceBrowser', 'drugDBname')
		if self.dbName is None:
			_log.Log(gmLog.lPanic,"No drug database specified. Aborting drug browser.")
			# FIXME: we shouldn't directly call Close() on the parent
			parent.Close()
			return None
                    
		self.mDrugView=gmDrugView.DrugView(self.dbName)

		self.mode = MODE_BRAND
		self.previousMode = MODE_BRAND
		self.printer = wxHtmlEasyPrinting()		#printer object to print html page
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
		EVT_BUTTON(self, ID_BUTTON_PRINT, self.OnPrint)
		EVT_BUTTON(self, ID_BUTTON_DISPLAY, self.OnDisplay)
		EVT_BUTTON(self, ID_BUTTON_PRESCRIBE, self.OnPrescribe)
		EVT_LISTBOX_DCLICK(self, ID_LISTBOX_JUMPTO, self.OnJumpToDblClick)
		EVT_LISTBOX(self, ID_LISTBOX_JUMPTO, self.OnJumpToSelected)
		EVT_LIST_ITEM_ACTIVATED(self, ID_LISTCTRL_DRUGCHOICE, self.OnDrugChoiceDblClick)
		EVT_RADIOBUTTON(self, ID_RADIOBUTTON_BYINDICATION, self.OnSearchByIndication)
		EVT_RADIOBUTTON(self, ID_RADIOBUTTON_BYGENERIC, self.OnSearchByGeneric)
		EVT_RADIOBUTTON(self, ID_RADIOBUTTON_BYBRAND, self.OnSearchByBrand)
		EVT_RADIOBUTTON(self, ID_RADIOBUTTON_BYANY, self.OnSearchByAny)
		EVT_TEXT(self, ID_COMBO_PRODUCT, self.OnProductKeyPressed)
		EVT_COMBOBOX(self, ID_COMBO_PRODUCT, self.OnProductSelected)
		EVT_BUTTON(self, wxID_OK, self.OnOk)
		EVT_BUTTON(self, wxID_CANCEL, self.OnCancel)
		EVT_BUTTON(self,ID_BUTTON_BOOKMARK, self.OnBookmark)
#-----------------------------------------------------------------------------------------------------------------------

	def GuiElements_Init(self):
		#--------------------------------------------------
		# create the controls for left hand side of screen
		# 1)create the label 'Find' and the combo box the
		#   user will type the name of drug into
		#--------------------------------------------------
		finddrug = wxStaticText( self, -1, _("   Find   "), wxDefaultPosition, wxDefaultSize, 0 )
		finddrug.SetFont( wxFont( 14, wxSWISS, wxNORMAL, wxNORMAL ) )
		
		self.comboProduct = wxComboBox(
			self,
			ID_COMBO_PRODUCT, 
			"", 
			wxDefaultPosition, 
			wxSize(130,-1),
			[] , 
			wxCB_DROPDOWN 
		)
		self.comboProduct.SetToolTip( wxToolTip(_("Enter the name of the drug you are interested in")) )
		self.btnBookmark = wxButton( 
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
		self.sizertopleft = wxBoxSizer(wxHORIZONTAL)
		self.sizertopleft.AddWindow( finddrug, 0, wxALIGN_CENTER_VERTICAL, 5 )
		self.sizertopleft.AddWindow( self.comboProduct, 1, wxGROW|wxALIGN_CENTER_VERTICAL, 5 )
		self.sizertopleft.AddWindow( self.btnBookmark, 0, wxALIGN_CENTER_VERTICAL, 5 )
		#---------------------------------------------------------------
		# next create the left sizer which will hold the drug list box 
		# and the html viewer
		#---------------------------------------------------------------
		self.sizer_left = wxBoxSizer( wxVERTICAL )
		self.sizer_left.AddSpacer( 30, 10, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxALL, 1 )
		self.sizer_left.AddSizer( self.sizertopleft, 0, wxGROW|wxALIGN_CENTER_VERTICAL, 5)
		self.sizer_left.AddSpacer( 1, 1, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxALL, 1 )
		self.listctrl_drugchoice=None
		self.html_viewer=None
		self.whichWidget = "listctrl_drugchoice"
		self.ToggleWidget()
		self.html_viewer.SetPage(self.WelcomeMessageHTML)
        
		#------------------------------------------------------------------------
		# the search by option buttons sit on a wxStaticBoxSizer with wxVertical
		# 1) create a wxStaticBox = bordered box with title search by
		# 2) add this to the sizerSearchBy sizer
		# 3) Add four radio buttons to this sizer
		#------------------------------------------------------------------------
		sboxSearchBy = wxStaticBox( self, -1, _("Search by") )
		self.sizerSearchBy = wxStaticBoxSizer( sboxSearchBy, wxVERTICAL )
		sboxSearchBy.SetFont( wxFont( 10, wxSWISS, wxNORMAL, wxNORMAL ) )
		
		self.rbtnSearchAny = wxRadioButton( self, ID_RADIOBUTTON_BYANY, _("Any"), wxDefaultPosition, wxDefaultSize, 0 )
		self.sizerSearchBy.AddWindow( self.rbtnSearchAny, 0, wxGROW|wxALIGN_CENTER_VERTICAL, 1 )
		self.rbtnSearchBrand = wxRadioButton( self, ID_RADIOBUTTON_BYBRAND, _("Brand name"), wxDefaultPosition, wxDefaultSize, 0 )
		self.sizerSearchBy.AddWindow( self.rbtnSearchBrand, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxTOP, 1 )
		self.rbtnSearchGeneric = wxRadioButton( self, ID_RADIOBUTTON_BYGENERIC, _("Generic name"), wxDefaultPosition, wxDefaultSize, 0 )
		self.sizerSearchBy.AddWindow( self.rbtnSearchGeneric, 0, wxGROW|wxALIGN_CENTER_VERTICAL, 1 )
		self.rbtnSearchIndication = wxRadioButton( self, ID_RADIOBUTTON_BYINDICATION, _("Indication"), wxDefaultPosition, wxDefaultSize, 0 )
		self.sizerSearchBy.AddWindow( self.rbtnSearchIndication, 0, wxGROW|wxALIGN_CENTER_VERTICAL, 1 )
		#-------------------------------------------------------------------------
		# and the right hand side vertical side bar sizer
		# 1) add a space at top to make the static text box even with the top
		#    of the main drug data display box
		# 2) add the searchby static box with the radio buttons which is stuck on
		#    to its own sizer
		# 3) add a spacer below this and above the list box underneath
		#-------------------------------------------------------------------------
		self.sizerVInteractionSidebar = wxBoxSizer( wxVERTICAL )
		self.sizerVInteractionSidebar.AddSpacer( 30, 10, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxALL, 12 )
		self.sizerVInteractionSidebar.AddSizer( self.sizerSearchBy, 0, wxGROW|wxALIGN_CENTER_VERTICAL, 5 )
		self.sizerVInteractionSidebar.AddSpacer( 30, 10, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxALL, 1 )
		#--------------------------------------------------------------------------
		# 4) create a listbox that will be populated with labels to jump to within the
		#    product info text and add to the vertical side bar
		#--------------------------------------------------------------------------
		self.listbox_jumpto = wxListBox( self, ID_LISTBOX_JUMPTO, wxDefaultPosition, wxSize(150,100),
			[] , wxLB_SINGLE )
		self.sizerVInteractionSidebar.AddWindow( self.listbox_jumpto, 1, wxGROW|wxALIGN_CENTER_VERTICAL, 10 )
		#--------------------------------------------------------------------------
		# 5) Add another spacer underneath this listbox
		#--------------------------------------------------------------------------
		self.sizerVInteractionSidebar.AddSpacer( 20, 10, 0, wxALIGN_CENTRE|wxALL, 1 )
		self.btnPrescribe = wxButton( self, ID_BUTTON_PRESCRIBE, _("&Prescribe"), wxDefaultPosition, wxDefaultSize, 0 )
		self.sizerVInteractionSidebar.AddWindow( self.btnPrescribe, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxALL, 1 )
		self.btnDisplay = wxButton( self, ID_BUTTON_DISPLAY, _("&Display"), wxDefaultPosition, wxDefaultSize, 0 )
		self.sizerVInteractionSidebar.AddWindow( self.btnDisplay, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxALL, 1 )
		self.btnPrint = wxButton( self, ID_BUTTON_PRINT, _("&Print"), wxDefaultPosition, wxDefaultSize, 0 )
		self.sizerVInteractionSidebar.AddWindow( self.btnPrint, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxALL, 1 )
		#-----------------------------------------------
		# finally create the main sizer to hold the rest
		# and all the sizers to the main sizer
		#---------------------------------------------
		self.sizermain = wxBoxSizer(wxHORIZONTAL)
		self.sizermain.AddSizer(self.sizer_left, 1, wxGROW|wxALIGN_CENTER_HORIZONTAL|wxALL, 7)
		self.sizermain.AddSizer(self.sizerVInteractionSidebar, 0, wxGROW|wxALIGN_LEFT|wxALL, 8)
		self.SetAutoLayout( true )
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
		gmLog.gmDefLog.Log (gmLog.lData,  "mode %s ,text code: %s" % (mode,code) )
		# show detailed info
		if mode == MODE_BRAND:
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
		return true


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
			self.html_viewer = wxHtmlWindow(self, -1, size=(400, 200))			
			self.sizer_left.AddWindow( self.html_viewer, 1, wxGROW|wxALIGN_CENTER_HORIZONTAL, 5 )
			self.sizer_left.Layout()
			self.whichWidget="html_viewer"
		else:
			if self.listctrl_drugchoice is not None:
				return
			if self.html_viewer is not None:
				self.sizer_left.Remove(self.html_viewer)
				self.html_viewer = None
			self.listctrl_drugchoice = wxListCtrl(self, ID_LISTCTRL_DRUGCHOICE, wxDefaultPosition, wxSize(400,200), style=wxLC_SINGLE_SEL | wxLC_REPORT )
			self.sizer_left.AddWindow( self.listctrl_drugchoice, 1, wxGROW|wxALIGN_CENTER_HORIZONTAL, 5 )
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
		# on brand/generic/indication 
		# expect a dictionary containing at least name & ID 
        # type will be set by radiobuttons
		# type and ID form (virtually) a unique ID that can be used to access other data in the db
		type = self.mode
		result = self.mDrugView.SearchIndex(self.mode,drugtofind,searchmode)
		numOfRows = len(result['id'])		
		# no drug found for this name
		if result == None or  numOfRows < 1:
			# tell everybody that we find a match
			self.mId = None
			self.drugProductInfo = None            
			# display message
			if self.whichWidget == 'listctrl_drugchoice':
				self.ToggleWidget ()
			self.html_viewer.SetPage(self.NoDrugFoundMessageHTML)

	   	# found exactly one drug
		elif numOfRows == 1:
			seld.mId = result['id']
			# if we found a brand *product*, show the product info
			if type == MODE_BRAND:
				if self.whichWidget == 'listctrl_drugchoice':
					self.ToggleWidget ()
					self.Display_PI (self.mId)
				elif self.mId <> self.mLastId: # don't change unless different drug
					self.Display_PI (self.mId)
					self.mLastId = self.mId
			# if we found a generic substance name, show all brands
			# containing this generic
			elif type == MODE_GENERIC:
				self.Display_Generic (self.mId)
			# if we are browsing indications, show all generics + brands
			# that match. Display Indication 
			elif type == MODE_INDICATION:
				self.Display_Indication(self.mId)

		# we have more than one result
		# -> display a list of all matching names
		else:
			if self.whichWidget == 'html_viewer':
				self.ToggleWidget ()
			# show list
			self.BuildListCtrl(result,type)
			return true

	#---------------------------------------------------------------------------------------------------------------------------
	def Display_Generic (self, aId):
		"""
		Find all brand products that contain a certain generic substance and 
        display them
		"""
		brandsList=self.mDrugView.getBrandsForGeneric(aId)
		type = MODE_BRAND
		# no brand - should be an error, but AMIS allows that :(
		if brandsList is None or len (brandsList['name']) == 0:
			gmLog.gmDefLog.Log (gmLog.lWarn,  "No brand product available containing generic ID: %s" % str(aId) )
			if self.whichWidget == 'listctrl_drugchoice':
				self.ToggleWidget ()
			self.html_viewer.SetPage(self.NoDrugFoundMessageHTML)
			return None        	
		# one brand, so display product information
		if len (brandsList['name']) == 1:
			if self.whichWidget == 'listctrl_drugchoice':
				self.ToggleWidget ()
			self.Display_PI (brandsList['id'])
		else:
			# multiple brands, display list
			if self.whichWidget == 'html_viewer':
				self.ToggleWidget ()
			# show list
			self.BuildListCtrl(brandsList,type)

			return true

	#-----------------------------------------------------------------
	def BuildListCtrl(self, aDataDict=None, type=None):
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

		# get column names from aDataDict key names
        # remove 'id' and display name at leftmost position
		columns = aDataDict.keys()
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
					item=self.listctrl_drugchoice.InsertStringItem (row,item_text)
					self.listctrl_drugchoice.SetItemData(item,item)
					id = aDataDict['id'][row]
			    	# set data as type and database ID
					self.__mListCtrlItems[item]=(type,id)			
				else:
					self.listctrl_drugchoice.SetStringItem(row,col_no,item_text)
				col_no += 1
		# finally set column widths to AUTOSIZE
		for i in range(0,len(columns)):
			self.listctrl_drugchoice.SetColumnWidth(i, wxLIST_AUTOSIZE)
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
		return true

#--------------------------------------------------------------------------------------------------------------------------------------------------
	def TransferDataToWindow(self):
		gmLog.gmDefLog.Log (gmLog.lData,  "Transfer data to Window")
		return true

	def TransferDataFromWindow(self):
		return true

	# handler implementations for DrugDisplay

	def OnPrint (self, event):
		"""
		If product info is available, print it.
		"""
		if not self.drugProductInfo is None:
			self.printer.PrintText(self.drugProductInfo)
		return true

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

	def OnSearchByBrand(self, event):
		self.mode = MODE_BRAND
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
		event.Skip(true)

	def OnCancel(self, event):
		event.Skip(true)

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
	_ = lambda x:x
	app = wxPyWidgetTester(size = (640, 400))
	app.SetWidget(DrugDisplay, -1)
	app.MainLoop()

else:
	#=================================================
	# make this into GNUMed plugin

	import gmPlugin
	import gmPG
	import gmI18N

	class gmDrugDisplay (gmPlugin.wxNotebookPlugin):

		def name (self):
			return _("DrugBrowser")

		def MenuInfo (self):
			return ("view", _("&DrugBrowser"))

		def GetWidget (self, parent):
			return DrugDisplay (parent, -1)

# @change log:
#       04.12.2001 hherb initial implementation, untested, uncomplete
#	08.12.2001 rterry minor revisions to screen design, commenting
#	05.09.2002 hherb DB-API 2.0 compliance

# $Log: gmDrugDisplay.py,v $
# Revision 1.6  2002-11-17 16:44:23  hinnef
# fixed some bugs regarding display of non-string items and list entries in PI
#
# Revision 1.5  2002/11/09 15:09:03  hinnef
# new items in product list, ListCtrl instead of ListBox
#
# Revision 1.4  2002/10/31 23:13:06  hinnef
# added generic substance support, further improvements
#
