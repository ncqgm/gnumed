#!/usr/bin/python
#############################################################################
#
# gmDrugDisplay_RT  Feedback: anything which is incorrect or ambiguous please
#                   mailto rterry@gnumed.net
# ---------------------------------------------------------------------------
#
# @author: Dr. Richard Terry
# @author: Dr. Herb Horst
# @acknowledgments: Gui screen Design taken with permission from
#                   DrsDesk MimsAnnual @ DrsDesk Software 1995-2002
#                   and @ Dr.R Terry
#                   Basic skeleton of this code written by Dr. H Horst
#                   heavily commented for learning purposes by Dr. R Terry
# @copyright: authors
# @license: GPL (details at http://www.gnu.org)
# @dependencies: wxPython (>= version 2.3.1)
# @change log:
#       04.12.2001 hherb initial implementation, untested, uncomplete
#	08.12.2001 rterry minor revisions to screen design, commenting
#	05.09.2002 hherb DB-API 2.0 compliance
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
import string
from wxPython.lib.splashscreen import SplashScreen
import keyword
import time
import gmPG
import pdb
import gmLog
darkblue = '#00006C'
darkgreen = '#0106D0A'
darkbrown = '#841310'
#=========================================
# Constants for the MimsAnnual data fields
#=========================================

querytext = ''
pitext=''
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
ID_LISTBOX_DRUGCHOICE = wxNewId()
ID_BUTTON_PRESCRIBE = wxNewId()
ID_BUTTON_DISPLAY = wxNewId()
ID_BUTTON_PRINT = wxNewId()
ID_BUTTON_BOOKMARK = wxNewId()

MODE_BRAND = 0
MODE_GENERIC = 1
MODE_INDICATION = 2
MODE_ANY = 3

#=============================================================================
# The frame is the window which pops up and contains the whole demo. Here I
# have called if MyFrame, but you can call it what you want. Note that it has
# 6 'parameters' when it is initialised (self,parent,ID,title,pos,size). These
# must also be included when you reference the MyFrame on the last lines of
# this file in the MyApp routine (see end of this file)
#=============================================================================
class DrugDisplay(wxPanel):
	"displays drug information in a convenience widget"
	def __init__(self, parent, id,
		pos = wxPyDefaultPosition, size = wxPyDefaultSize,
		style = wxTAB_TRAVERSAL ):
		wxPanel.__init__(self, parent, id, pos, size, style)
		self.mancode = None
		self.mode = MODE_BRAND
		self.printer = wxHtmlEasyPrinting()          #printer object to print html page
		#-------------------------------------------------------------
		# These things build the physical window that you see when
		# the program boots. They each refer to a subroutine that
		# is listed below by the same name eg def Menus_Create(self)
		#-------------------------------------------------------------
		self.GuiElements_Init()				#add main gui elements
		self.inDisplay_PI = 0
		self.db = gmPG.ConnectionPool().GetConnection('pharmaceutica')
		self.GetDrugIssue()
		#--------------------------------------------------------------
		# handler declarations for DrugDisplay
		# note handlers for menu in Menus_Create()
		#--------------------------------------------------------------
		EVT_BUTTON(self, ID_BUTTON_PRINT, self.OnPrint)
		EVT_BUTTON(self, ID_BUTTON_DISPLAY, self.OnDisplay)
		EVT_BUTTON(self, ID_BUTTON_PRESCRIBE, self.OnPrescribe)
		EVT_LISTBOX_DCLICK(self, ID_LISTBOX_JUMPTO, self.OnJumpToDblClick)
		EVT_LISTBOX(self, ID_LISTBOX_JUMPTO, self.OnJumpToSelected)
		EVT_LISTBOX(self, ID_LISTBOX_DRUGCHOICE, self.OnDrugChoiceDblClick)
		EVT_LISTBOX_DCLICK(self, ID_LISTBOX_JUMPTO, self.OnDrugChoiceDblClick)
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
	def OnDrugChoiceDblClick(self,event):
		mode, code = self.listbox_drugchoice.GetClientData (self.listbox_drugchoice.GetSelection ())
		if mode == MODE_BRAND:
			self.ToggleWidget ()
			self.Display_PI (code)
		elif mode == MODE_GENERIC:
			self.Display_Generic (code)
		elif mode == MODE_INDICATION:
			pass
		return
	
	def GetDrugIssue(self):
		cursor = self.db.cursor()
		try:
			cursor.execute('select * from issue')
		except:
			return
		result = cursor.fetchall()
		for row in result:
				insertstring =''
				for field in row:
					#insertstring = "%s\t%s", %(insertstring, str(field))
					insertstring = str(field)
										#append it as a new line in your scrolling multiline WTextCtrl
				#self.SetStatusText(insertstring, 1)
		gmLog.gmDefLog.Log (gmLog.lData, "got the issue date")
		return true

	def GuiElements_Init(self):
		#--------------------------------------------------
		# create the controls for left hand side of screen
		# 1)create the label 'Find' and the combo box the
		#   user will type the name of drug into
		#--------------------------------------------------
		finddrug = wxStaticText( self, -1, _("   Find   "), wxDefaultPosition, wxDefaultSize, 0 )
		finddrug.SetFont( wxFont( 14, wxSWISS, wxNORMAL, wxNORMAL ) )
		self.comboProduct = wxComboBox( self, ID_COMBO_PRODUCT, "", wxDefaultPosition, wxSize(130,-1),[] , wxCB_DROPDOWN )
		self.comboProduct.SetToolTip( wxToolTip(_("Enter the name of the drug you are interested in")) )
		self.btnBookmark = wxButton( self, ID_BUTTON_BOOKMARK, _("&Bookmark"), wxDefaultPosition, wxDefaultSize, 0 )
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
		self.listbox_drugchoice=None
		self.html_viewer=None
		self.whichWidget = "html_viewer"
		self.ToggleWidget()
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
		# 4) create a listbox and populate with labels to jump to within the
		#    mimsannual text and add to the vertical side bar
		#--------------------------------------------------------------------------
		self.listbox_jumpto = wxListBox( self, ID_LISTBOX_JUMPTO, wxDefaultPosition, wxSize(150,100),
			[_("Actions"), _("Adverse reactions"),_("Composition"),_("Contraindications"),_("Description"),
			_("Dose & administration"), _("Indications"), _("Interactions"), _("Precautions"), _("Presentation"),  _("Storage")] , wxLB_SINGLE )
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
	def OnBookmark(self,event):
		pass
	
	def Display_Generic (self, gencode):
		#pdb.set_trace ()
		querytext = "select manxxdat.product, manxxdat.mancode from manxxdat, gmman where gmman.gencode=%d and gmman.mancode = manxxdat.mancode" % gencode
		cursor = self.db.cursor()
		cursor.execute(querytext)
		result = query.fetchall ()
		# one brand, so display PI
		#pdb.set_trace ()
		if len (result) == 1:
			if self.whichWidget == 'listbox_drugchoice':
				self.ToggleWidget ()
			self.Display_PI (result[0][1])
		else:
			# multiple brands, display list
			if self.whichWidget == 'html_viewer':
				self.ToggleWidget ()
			row_no = 0
			self.listbox_drugchoice.Clear ()
			for row in result:
				self.listbox_drugchoice.Append (row[0] + '\n')
				self.listbox_drugchoice.SetClientData (row_no, (MODE_BRAND, row[1])) # set data as type and database ID
				row_no += 1
					
	
#-----------------------------------------------------------------------------------------------------------------------------
	def Drug_Find(self):
		#--------------------------------------------------------
		# using text in listbox_drugchoice find any similar drugs
		#--------------------------------------------------------
		
		drugtofind = string.lower(self.comboProduct.GetValue())
		#pdb.set_trace ()
		result = []
		if self.mode == MODE_BRAND or self.mode == MODE_ANY:
			querytext = "select %d, product, mancode from manxxdat where lower(product) like '%s%%' order by product ASC" % (MODE_BRAND, drugtofind)
		elif self.mode == MODE_GENERIC or self.mode == MODE_ANY:
			querytext = "select %d, tfgeneric, gencode from genman where lower (tfgeneric) like '%s%%' order by tfgeneric ASC" % (MODE_GENERIC, drugtofind)
			#result.extend(query.getresult ())
		elif self.mode == MODE_INDICATION or self.mode == MODE_ANY:
			# it is not obvious how to do this!
			pass
		cursor=self.db.cursor()
		cursor.execute(querytext)
		result = cursor.fetchall()
		if len (result) == 0:
			if self.whichWidget == 'html_viewer':
				self.ToggleWidget ()
			self.listbox_drugchoice.Clear ()
			self.listbox_drugchoice.Append ('No matching drugs funod!')
		elif len (result) == 1:
			type = result[0][0]
			name = result[0][1]
			code = result[0][2]
			if type == MODE_BRAND:
				if self.whichWidget == 'listbox_drugchoice':
					self.ToggleWidget ()
					self.Display_PI (code)
				elif self.mancode <> code: # don't change unless different drug
					self.Display_PI (code)
					self.mancode = code
			elif type == MODE_GENERIC:
				# find brands for this generic
				self.Display_Generic (code)
			elif type == MODE_INDICATION:
				pass

		# have more than one result
		else:
			if self.whichWidget == 'html_viewer':
				self.ToggleWidget ()
			self.listbox_drugchoice.Clear ()
			row_no = 0
			for row in result:
				self.listbox_drugchoice.Append (row[1] + '\n')
				self.listbox_drugchoice.SetClientData (row_no, (row[0], row[2])) # set data as type and datbase ID
				row_no += 1
		return true
#---------------------------------------------------------------------------------------------------------------------------
	def ToggleWidget(self):
		if self.whichWidget == "listbox_drugchoice":
			if self.html_viewer is not None:
				return
			if self.listbox_drugchoice is not None:
				self.sizer_left.Remove(self.listbox_drugchoice)
				self.listbox_drugchoice = None
			self.html_viewer = wxHtmlWindow(self, -1, size=(400, 200))			
			self.sizer_left.AddWindow( self.html_viewer, 1, wxGROW|wxALIGN_CENTER_HORIZONTAL, 5 )
			self.sizer_left.Layout()
			self.whichWidget="html_viewer"
		else:
			if self.listbox_drugchoice is not None:
				return
			if self.html_viewer is not None:
				self.sizer_left.Remove(self.html_viewer)
				self.html_viewer = None
			self.listbox_drugchoice = wxListBox(self, ID_LISTBOX_DRUGCHOICE, wxDefaultPosition, wxSize(400,200), [], wxLB_SINGLE )
			#self.listbox_drugchoice.SetBackgroundColour("WHITE")
			#self.listbox_drugchoice.SetForegroundColour("BLACK")
			
			#self.listbox_drugchoice = wxListBox( self, ID_listbox_drugchoice, wxDefaultPosition, wxSize(150,100),
			#	[_("Drug A"), _("DrugB"), _("DrugC")] , wxLB_SINGLE )
			self.sizer_left.AddWindow( self.listbox_drugchoice, 1, wxGROW|wxALIGN_CENTER_HORIZONTAL, 5 )
			self.sizer_left.Layout()
			self.whichWidget="listbox_drugchoice"
	
#-----------------------------------------------------------------------------------------------------------------------------

	def Display_PI(self, mancode):
		#-----------------------------------------------------------------
		# Queries MimsAnnual database using the mancode to get all the
		# fields needed to format a HTML output of the product information
		#-----------------------------------------------------------------
		querytext = "Select DISTINCT * from manxxdat where mancode = " + str(mancode)
		#gmLog.gmDefLog.Log (gmLog.lData,  'starting to read database.....')
		#gmLog.gmDefLog.Log (gmLog.lData,  'sending query.....')
		gmLog.gmDefLog.Log (gmLog.lData,  querytext)
		cursor=self.db.cursor()
		cursor.execute(querytext)
		result = cursor.fetchall()
		gmLog.gmDefLog.Log (gmLog.lData,  'results obtained')
		#----------------------------------------------------------------------
		# Set this drug name to the combobox text, and add it to the combo list
		#----------------------------------------------------------------------
		#self.comboProduct.Append(drugname)
		# this is to stop recursion!
		self.inDisplay_PI = 1
		self.mancode = mancode
		self.comboProduct.SetValue(result[0]['product'])
		self.inDisplay_PI = 0
		#pdb.set_trace ()
		#----------------------------------------------------------------------
		# Start construction the html file to display
		# First put up the header of the html file
		# to put in hyperlink
		# This stuff is just whilst I'm learning HTML I made a few notes
		# <a href="#composition">Composition</a> viewed as hyperlink in browser
		# to put a tag which will be jumped to
		# <name="#composition">  
		# to jump into a file http://www.drsref.com.au/medical.html#composition
		# table simple <TABLE><TR> <TD bgcolor=blue>a</TD> <TD>b </TD> </TR>  <TR> <TD>c </TD> <TD> d</TD> </TR> </TABLE> ' doesnot show unless
		# something is in the cells this will be left aligned  ab and under this CD (standard 5 pixel spacing)
		# if want this over whole screen in first <TABLE width = 100% cellpadding=20 cellspacing=10 border = 1 bgcolor = 'gray' >
		# will stretch over full width or can do pixel eg Width = 840
		# if first data screen = 40%   <TABLE width = 100%> <TD width = 40%> , second TD tag <TD width = 60%> and the ones
		# below will align with the ones above.
		# cell padding is the width between whatever is in the cell and the border around it
		# cell spacing is width between the outlines of each cell
		# BORDER = 1 pixel or more eg 2 etc.
		#<TR> <TD colspan=2> d</TD> </TR> says wrap this under the two columns above.
		#----------------------------------------------------------------------
		pitext="<HTML><HEAD></HEAD><BODY BGCOLOR='#FFFFFF8'> <FONT SIZE=-1>" #FACE='fontname,font2,font3'>"
		#--------------------------------------------------------
		# For each field which is not null put a heading <B> </B>
		# note the not null code is missing  - to do
		# first put up the heading for composition of the drug
		#--------------------------------------------------------
		#pitext = pitext + "<FONT  SIZE=4 COLOR='" + darkblue + "'><B><name='#Composition'>Composition</B></FONT>"
		pitext = pitext + "<FONT  SIZE=4 COLOR='" + darkblue + "'><B><A NAME='Composition'>Composition</A></B></FONT><BR>"
		#-----------------------------------------------------------------------------
		#if there is no 'active' or 'inactive heading, insert carriage return to place
		#text underneth the composition heading
		#-----------------------------------------------------------------------------
		# Richard, I just can't understand this at all.
		# this if statement blocked 90% of the drugs from displaying at all! (Ian)
		#if string.find(str(result[0]['co']),'active') == -1:
		pitext = pitext + str(result[0]['co'])
		pitext = pitext +  "<A NAME=\"Description\"></A><BR><FONT  SIZE=4 COLOR='" + darkblue + "'><B>Description</B></FONT><BR>"
		pitext = pitext +  str(result[0]['des']) 
		pitext = pitext +  "<A NAME=\"Actions\"></A><BR><FONT  SIZE=5 COLOR='" + darkblue + "'><B>Actions</B></FONT><BR>"
		pitext = pitext + str(result[0]['ac'])
		pitext = pitext +  "<A NAME=\"Indications\"></A><BR><FONT  SIZE=5 COLOR='" + darkblue + "'><B>Indications</B></FONT><BR>"
		pitext = pitext + str(result[0]['ind'])
		pitext = pitext +  "<A NAME=\"Contraindications\"></A><BR><FONT  SIZE=5 COLOR='" + darkblue + "'><B>Contraindications</B></FONT><BR>"
		pitext = pitext + str(result[0]['ci'])
		pitext = pitext +  "<BR><FONT  SIZE=5 COLOR='" + darkblue + "'><B>Warnings</B></FONT><BR>"
		pitext = pitext + str(result[0]['wa'])
		pitext = pitext +  "<A NAME=\"Precautions\"></A><BR><FONT  SIZE=5 COLOR='" + darkblue + "'><B>Precautions</B></FONT><BR>"
		pitext = pitext + str(result[0]['pr'])
		pitext = pitext +  "<A NAME=\"Adverse reactions\"></A><BR><BR><FONT  SIZE=5 COLOR='" + darkblue + "'><B>Adverse Reactions</B></FONT><BR>"
		pitext = pitext + str(result[0]['ar'])
		pitext = pitext +  "<A NAME=\"Interactions\"></A><BR><FONT  SIZE=5 COLOR='" + darkblue + "'><B>Interactions</B></FONT><BR>"
		pitext = pitext + str(result[0]['ir'])
		pitext = pitext +  "<A NAME=\"Dose & administration\"></A><BR><FONT  SIZE=5 COLOR='" + darkblue + "'><B>Dose and Administration</B></FONT><BR>"
		pitext = pitext + str(result[0]['da'])
		pitext = pitext +  "<A NAME=\"Presentation\"></A><BR><FONT  SIZE=5 COLOR='" + darkblue + "'><B>Presentation</B></FONT><BR>"
		pitext = pitext + str(result[0]['prn'])
		pitext = pitext +  "<A NAME=\"Storage\"></A><BR><FONT  SIZE=5 COLOR='" + darkblue + "'><B>Storage</B></FONT><BR>"
		pitext = pitext + str(result[0]['str'])
		#--------------------------------------------------------------------
		# Now replace MIMS tags with html tags according to following regime:
		# <HD2> = subheading <H2> end subheading
		# <HD4> = subsubheading <H4> end subsubheading
		# <D> = end of italic
		#--------------------------------------------------------------------
		pitext = string.replace(pitext,"<HD2>","<FONT  SIZE=3 COLOR='" + darkbrown + "'><B>")
		pitext = string.replace(pitext,"<T2>","</B></FONT><BR>")
		pitext = string.replace(pitext,"<HD4>","<FONT SIZE=3  COLOR='" + darkgreen + "'><B>")
		pitext = string.replace(pitext,"<T4>","<BR></B></FONT>")
		pitext = string.replace(pitext,"<D>","</I>")
		#pitext = string.replace(pitext,"<H4>","<BR>")
		#pitext = string.replace(pitext,"<H2>","<BR><BR>")
		pitext = pitext + "</FONT></BODY></HTML>"
		self.html_viewer.SetPage(pitext)	
		return true
#--------------------------------------------------------------------------------------------------------------------------------------------------
	def TransferDataToWindow(self):
		gmLog.gmDefLog.Log (gmLog.lData,  "Transfer data to Window")
		return true

	def TransferDataFromWindow(self):
		return true


	# handler implementations for DrugDisplay

	def OnPrint (self, event):
		#this code does not work properly
		self.printer.PrintText(pitext)
		print "printing frame"
		return true

	
	def OnDisplay(self, event):
#		self.ToggleWidget()

		self.Display_PI()
		pass

	def OnPrescribe(self, event):
		
		pass

	def OnJumpToDblClick(self, event):
		pass

	def OnJumpToSelected(self, event):
		# can't figure out how to get this to work!
		gmLog.gmDef.Log (gmLog.lData, "selection made")
		tagname = self.listbox_jumpto.GetString(self.listbox_jumpto.GetSelection())
		print  tagname
		self.html_viewer.LoadPage('#' + tagname)
		pass

	def OnSearchByIndication(self, event):
		self.mode = MODE_INDICATION

	def OnSearchByGeneric(self, event):
		self.mode = MODE_GENERIC

	def OnSearchByBrand(self, event):
		self.mode = MODE_BRAND

	def OnSearchByAny(self, event):
		self.mode = MODE_ANY

	# Rewrote this
	def OnProductKeyPressed(self, event):
		# first, do not recur when setting the box ourselves!
		if not self.inDisplay_PI:
			if self.comboProduct.GetValue () <> '':
				self.Drug_Find ()


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


#==================================================
# Shall we just test this module?
if __name__ == "__main__":
	_ = lambda x:x
	app = wxPyWidgetTester(size = (400, 300))
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
			return "MIMS"

		def MenuInfo (self):
			return ("view", "&MIMS")

		def GetWidget (self, parent):
			return DrugDisplay (parent, -1)







