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
from wxPython.lib.splashscreen import SplashScreen
import wxPython.lib.wxpTag

import gmPG, gmGuiBroker

import keyword, time, pg, string
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
		self.printer = wxHtmlEasyPrinting()          #printer object to print html page
		#-------------------------------------------------------------
		# These things build the physical window that you see when
		# the program boots. They each refer to a subroutine that
		# is listed below by the same name eg def Menus_Create(self)
		#-------------------------------------------------------------
		self.GuiElements_Init()				#add main gui elements
		self.db = pg.connect(dbname='mimsannual',
					host = '',
					port =5432,
					opt = '',
					tty = '',
					user = 'ian',
					passwd ='')
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
		print self.listbox_drugchoice.GetString(self.listbox_drugchoice.GetSelection())
		self.comboProduct.SetValue(self.listbox_drugchoice.GetString(self.listbox_drugchoice.GetSelection()))
		return
	
	def GetDrugIssue(self):
		query = self.db.query('select * from issue')
		result = query.getresult()
		for row in result:
				insertstring =''
				for field in row:
					#insertstring = "%s\t%s", %(insertstring, str(field))
					insertstring = str(field)
										#append it as a new line in your scrolling multiline WTextCtrl
				#self.SetStatusText(insertstring, 1)
		print "got the issue date"
		return true

	def GuiElements_Init(self):
		#--------------------------------------------------
		# create the controls for left hand side of screen
		# 1)create the label 'Find' and the combo box the
		#   user will type the name of drug into
		#--------------------------------------------------
		finddrug = wxStaticText( self, -1, "   Find   ", wxDefaultPosition, wxDefaultSize, 0 )
		finddrug.SetFont( wxFont( 14, wxSWISS, wxNORMAL, wxNORMAL ) )
		self.comboProduct = wxComboBox( self, ID_COMBO_PRODUCT, "", wxDefaultPosition, wxSize(130,-1),
			["Tenormin","Inderal"] , wxCB_DROPDOWN )
		self.comboProduct.SetToolTip( wxToolTip("Enter the name of the drug you are interested in") )
		self.btnBookmark = wxButton( self, ID_BUTTON_BOOKMARK, "&Bookmark", wxDefaultPosition, wxDefaultSize, 0 )
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
		sboxSearchBy = wxStaticBox( self, -1, "Search by" )
		self.sizerSearchBy = wxStaticBoxSizer( sboxSearchBy, wxVERTICAL )
		sboxSearchBy.SetFont( wxFont( 10, wxSWISS, wxNORMAL, wxNORMAL ) )
		self.rbtnSearchAny = wxRadioButton( self, ID_RADIOBUTTON_BYANY, "Any", wxDefaultPosition, wxDefaultSize, 0 )
		self.sizerSearchBy.AddWindow( self.rbtnSearchAny, 0, wxGROW|wxALIGN_CENTER_VERTICAL, 1 )
		self.rbtnSearchBrand = wxRadioButton( self, ID_RADIOBUTTON_BYBRAND, "Brand name", wxDefaultPosition, wxDefaultSize, 0 )
		self.sizerSearchBy.AddWindow( self.rbtnSearchBrand, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxTOP, 1 )
		self.rbtnSearchGeneric = wxRadioButton( self, ID_RADIOBUTTON_BYGENERIC, "Generic name", wxDefaultPosition, wxDefaultSize, 0 )
		self.sizerSearchBy.AddWindow( self.rbtnSearchGeneric, 0, wxGROW|wxALIGN_CENTER_VERTICAL, 1 )
		self.rbtnSearchIndication = wxRadioButton( self, ID_RADIOBUTTON_BYINDICATION, "Indication", wxDefaultPosition, wxDefaultSize, 0 )
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
			["Actions", "Adverse reactions","Composition","Contraindications","Description",
			"Dose & administration", "Indications", "Interactions", "Lactation",
			"Overdose","Poisons Schedule", "Precautions", "Presentation",  "Storage"] , wxLB_SINGLE )
		self.sizerVInteractionSidebar.AddWindow( self.listbox_jumpto, 1, wxGROW|wxALIGN_CENTER_VERTICAL, 10 )
		#--------------------------------------------------------------------------
		# 5) Add another spacer underneath this listbox
		#--------------------------------------------------------------------------
		self.sizerVInteractionSidebar.AddSpacer( 20, 10, 0, wxALIGN_CENTRE|wxALL, 1 )
		self.btnPrescribe = wxButton( self, ID_BUTTON_PRESCRIBE, "&Prescribe", wxDefaultPosition, wxDefaultSize, 0 )
		self.sizerVInteractionSidebar.AddWindow( self.btnPrescribe, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxALL, 1 )
		self.btnDisplay = wxButton( self, ID_BUTTON_DISPLAY, "&Display", wxDefaultPosition, wxDefaultSize, 0 )
		self.sizerVInteractionSidebar.AddWindow( self.btnDisplay, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxALL, 1 )
		self.btnPrint = wxButton( self, ID_BUTTON_PRINT, "&Print", wxDefaultPosition, wxDefaultSize, 0 )
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
		self.listbox_drugchoice.Clear()
		print 'starting to find brandname'
		drugtofind = self.comboProduct.GetValue()
		querytext = "select product, mancode from manxxdat where lower(product) like '" + drugtofind + "%'"  + " order by product ASC"
		print drugtofind
		query = self.db.query(querytext)
		result = query.getresult()
		for row in result:
			insertstring =''
			column = 0
			for field in row:
				insertstring = str(field)
				if column == 0:
					self.listbox_drugchoice.Append(insertstring+'\n')
				elif column == 1:
					self.mancode = field
					print self.mancode
				column = column + 1
		#self.Display_PI()
	
		return true
	
#-----------------------------------------------------------------------------------------------------------------------------
	def Drug_Find(self):
		#--------------------------------------------------------
		# using text in listbox_drugchoice find any similar drugs
		#--------------------------------------------------------
		
		print 'starting to find brandname'
		drugtofind = string.lower(self.comboProduct.GetValue())
		querytext = "select product, mancode from manxxdat where lower(product) like '" + drugtofind + "%'"  + " order by product ASC"
		print drugtofind
		query = self.db.query(querytext)
		result = query.getresult()
		for row in result:
			insertstring =''
			column = 0
			for field in row:
				insertstring = str(field)
				if column == 0:
					drugname =  insertstring
					self.listbox_drugchoice.Append(insertstring+'\n')
				elif column == 1:
					#self.listbox_drugchoice.Append(drugname)
					self.mancode = field
					print self.mancode
					print drugname
				column = column + 1
		#-----------------------------------------------------------------
		# if there is only one drug in the list, automatically show the PI
		#-----------------------------------------------------------------
		if self.listbox_drugchoice.Number() == 1:
			self.Display_PI()
			
				
	
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

	def Display_PI(self):
		#------------------------------------------------------------------
		# If the listbox listing drugs is visible, display PI if clicked or
		# if only one row exists in the listbox
		#------------------------------------------------------------------
		if self.whichWidget ==  "listbox_drugchoice":
			#-----------------------------------------------------------------
			# Queries MimsAnnual database using the mancode to get all the
			# fields needed to format a HTML output of the product information
			#-----------------------------------------------------------------
			querytext = "Select DISTINCT * from manxxdat where mancode = " + str(self.mancode)
			print 'starting to read database.....'
			print 'sending query.....'
			print querytext
			query = self.db.query(querytext)
			result = query.dictresult()
			print 'results obtained'
			drugname  =  self.listbox_drugchoice.GetString(0)
			drugcode = self.mancode	
			#----------------------------------------------------------------------
			# Set this drug name to the combobox text, and add it to the combo list
			#----------------------------------------------------------------------
			#self.comboProduct.Append(drugname)
			self.comboProduct.SetValue(drugname)
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
			pitext = pitext + "<FONT  SIZE=4 COLOR='" + darkblue + "'><B><A NAME='Composition'>Composition</A></B></FONT>"
			#-----------------------------------------------------------------------------
			#if there is no 'active' or 'inactive heading, insert carriage return to place
			#text underneth the composition heading
			#-----------------------------------------------------------------------------
			if string.find(str(result[0]['co']),'active') == -1:
				pitext = pitext + "<BR>"
				pitext = pitext + str(result[0]['co'])
				pitext = pitext +  "<BR><FONT  SIZE=4 COLOR='" + darkblue + "'><B>Description</B></FONT><BR>"
				pitext = pitext +  str(result[0]['des']) 
				pitext = pitext +  "<BR><FONT  SIZE=5 COLOR='" + darkblue + "'><B>Actions</B></FONT><BR>"
				pitext = pitext + str(result[0]['ac'])
				pitext = pitext +  "<BR><FONT  SIZE=5 COLOR='" + darkblue + "'><B>Indications</B></FONT><BR>"
				pitext = pitext + str(result[0]['ind'])
				pitext = pitext +  "<BR><FONT  SIZE=5 COLOR='" + darkblue + "'><B>Contraindications</B></FONT><BR>"
				pitext = pitext + str(result[0]['ci'])
				pitext = pitext +  "<BR><FONT  SIZE=5 COLOR='" + darkblue + "'><B>Warnings</B></FONT><BR>"
				pitext = pitext + str(result[0]['wa'])
				pitext = pitext +  "<BR><FONT  SIZE=5 COLOR='" + darkblue + "'><B>Precautions</B></FONT><BR>"
				pitext = pitext + str(result[0]['pr'])
				pitext = pitext +  "<BR><BR><FONT  SIZE=5 COLOR='" + darkblue + "'><B>Adverse Reactions</B></FONT><BR>"
				pitext = pitext + str(result[0]['ar'])
				pitext = pitext +  "<BR><FONT  SIZE=5 COLOR='" + darkblue + "'><B>Interactions</B></FONT><BR>"
				pitext = pitext + str(result[0]['ir'])
				pitext = pitext +  "<BR><FONT  SIZE=5 COLOR='" + darkblue + "'><B>Dose and Administration</B></FONT><BR>"
				pitext = pitext + str(result[0]['da'])
				pitext = pitext +  "<BR><FONT  SIZE=5 COLOR='" + darkblue + "'><B>Presentation</B></FONT><BR>"
				pitext = pitext + str(result[0]['prn'])
				pitext = pitext +  "<BR><FONT  SIZE=5 COLOR='" + darkblue + "'><B>Storage</B></FONT><BR>"
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
				self.ToggleWidget()
				self.html_viewer.SetPage(pitext)

				
			return true
#--------------------------------------------------------------------------------------------------------------------------------------------------
	def TransferDataToWindow(self):
		print "Transfer data to Window"
		return true

	def TransferDataFromWindow(self):
		return true


	# handler implementations for DrugDisplay

	def OnPrint(self, event):
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
		print "selection made"
		tagname = self.listbox_jumpto.GetString(self.listbox_jumpto.GetSelection())
		print  tagname
		self.html_viewer.LoadPage(tagname)
		pass

	def OnSearchByIndication(self, event):
		pass

	def OnSearchByGeneric(self, event):
		pass

	def OnSearchByBrand(self, event):
		pass

	def OnSearchByAny(self, event):
		pass

	def OnProductKeyPressed(self, event):
		#-------------------------------------------------------------------
		# if there is text in the combobox, search for corresponding entries
		#-------------------------------------------------------------------
		if self.comboProduct.GetValue() <> '':
			if self.whichWidget <> "html_viewer":
				self.listbox_drugchoice.Clear()
			self.Drug_Find()
			print "keypressed in combobox"
		else:
			#------------------------------------------------------------
			# othwise, if combo text just cleared, if the html is showing
			# remove this and reshow the listbox
			#------------------------------------------------------------
			if self.whichWidget == "html_viewer":
				self.ToggleWidget()
				
		pass

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

if __name__ == "__main__":
	import gmI18N
	app = wxPyWidgetTester(size = (400, 300))
	app.SetWidget(DrugDisplay, -1)
	app.MainLoop()
