#!/usr/bin/python
#############################################################################
#
# gmDrugDisplay - displays drug information in a convenience widget
# ---------------------------------------------------------------------------
# @author: Dr. Horst Herb
# @copyright: author
# @license: GPL (details at http://www.gnu.org)
# @dependencies: wxPython (>= version 2.3.1)
# @change log:
#	04.12.2001 hherb initial implementation, untested, uncomplete
#
# @TODO:
#	- virtually everything
############################################################################
"displays drug information in a convenience widget"

from wxPython.wx import *

import gettext
_ = gettext.gettext


ID_TEXTCTRL = wxNewId()
ID_TEXT = wxNewId()
ID_COMBO_PRODUCT = wxNewId()
ID_RADIOBUTTON_BYANY = wxNewId()
ID_RADIOBUTTON_BYBRAND = wxNewId()
ID_RADIOBUTTON_BYGENERIC = wxNewId()
ID_RADIOBUTTON_BYINDICATION = wxNewId()
ID_LISTBOX = wxNewId()
ID_BUTTON_PRESCRIBE = wxNewId()
ID_BUTTON_DISPLAY = wxNewId()
ID_BUTTON_PRINT = wxNewId()
ID_BUTTON_BOOKMARK = wxNewId()

class DrugDisplay(wxPanel):
	"displays drug information in a convenience widget"
	def __init__(self, parent, id,
		pos = wxPyDefaultPosition, size = wxPyDefaultSize,
		style = wxTAB_TRAVERSAL ):
		wxPanel.__init__(self, parent, id, pos, size, style)
		print "Initializing GUI elements"
		self.InitGuiElements()

		# handler declarations for DrugDisplay
		EVT_BUTTON(self, ID_BUTTON_PRINT, self.OnPrint)
		EVT_BUTTON(self, ID_BUTTON_DISPLAY, self.OnDisplay)
		EVT_BUTTON(self, ID_BUTTON_PRESCRIBE, self.OnPrescribe)
		EVT_LISTBOX_DCLICK(self, ID_LISTBOX, self.OnJumpToDblClick)
		EVT_LISTBOX(self, ID_LISTBOX, self.OnJumpToSelected)
		EVT_RADIOBUTTON(self, ID_RADIOBUTTON_BYINDICATION, self.OnSearchByIndication)
		EVT_RADIOBUTTON(self, ID_RADIOBUTTON_BYGENERIC, self.OnSearchByGeneric)
		EVT_RADIOBUTTON(self, ID_RADIOBUTTON_BYBRAND, self.OnSearchByBrand)
		EVT_RADIOBUTTON(self, ID_RADIOBUTTON_BYANY, self.OnSearchByAny)
		EVT_TEXT(self, ID_COMBO_PRODUCT, self.OnProductKeyPressed)
		EVT_COMBOBOX(self, ID_COMBO_PRODUCT, self.OnProductSelected)
		EVT_BUTTON(self, wxID_OK, self.OnOk)
		EVT_BUTTON(self, wxID_CANCEL, self.OnCancel)

	# methods for DrugDisplay

	def TransferDataToWindow(self):
		print "Transfer data to Window"
		return true

	def TransferDataFromWindow(self):
		return true

	# handler implementations for DrugDisplay

	def OnPrint(self, event):
		pass

	def OnDisplay(self, event):
		pass

	def OnPrescribe(self, event):
		pass

	def OnJumpToDblClick(self, event):
		pass

	def OnJumpToSelected(self, event):
		print "selection made"
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
		pass

	def OnProductSelected(self, event):
		pass

	def OnOk(self, event):
		event.Skip(true)

	def OnCancel(self, event):
		event.Skip(true)


	def InitGuiElements(self):

		self.szrVTop = wxBoxSizer( wxVERTICAL )

		sboxProduct = wxStaticBox( self, -1, _("Product") )
		sboxProduct.SetFont( wxFont( 8, wxSWISS, wxNORMAL, wxNORMAL ) )
		self.szrProduct = wxStaticBoxSizer( sboxProduct, wxHORIZONTAL )

		self.comboProduct = wxComboBox( self, ID_COMBO_PRODUCT, "", wxDefaultPosition, wxSize(130,-1),
			[_("Drug A"),_("Drug B")] , wxCB_DROPDOWN )
		self.comboProduct.SetToolTip( wxToolTip(_("Enter the name of the drug you are interested in")) )
		self.szrProduct.AddWindow( self.comboProduct, 1, wxGROW|wxALIGN_CENTER_VERTICAL, 5 )

		self.btnBookmark = wxButton( self, ID_BUTTON_BOOKMARK, _("&Bookmark"), wxDefaultPosition, wxDefaultSize, 0 )
		self.szrProduct.AddWindow( self.btnBookmark, 0, wxALIGN_CENTER_VERTICAL|wxALL, 1 )

		self.szrVTop.AddSizer( self.szrProduct, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxALL, 5 )

		self.szrHTop = wxBoxSizer( wxHORIZONTAL )

		self.mltxtMims = wxTextCtrl( self, ID_TEXTCTRL, "", wxDefaultPosition, wxSize(80,40), wxTE_MULTILINE )
		self.szrHTop.AddWindow( self.mltxtMims, 1, wxGROW|wxALIGN_CENTER_HORIZONTAL, 5 )

		self.szrHTop.AddSpacer( 10, 10, 0, wxALIGN_CENTRE|wxALL, 1 )

		self.szrVInteractionSidebar = wxBoxSizer( wxVERTICAL )

		sboxSearchBy = wxStaticBox( self, -1, _("Search by") )
		sboxSearchBy.SetFont( wxFont( 8, wxSWISS, wxNORMAL, wxNORMAL ) )
		self.szrSearchBy = wxStaticBoxSizer( sboxSearchBy, wxVERTICAL )

		self.rbtnSearchAny = wxRadioButton( self, ID_RADIOBUTTON_BYANY, _("Any"), wxDefaultPosition, wxDefaultSize, 0 )
		self.szrSearchBy.AddWindow( self.rbtnSearchAny, 0, wxGROW|wxALIGN_CENTER_VERTICAL, 1 )

		self.rbtnSearchBrand = wxRadioButton( self, ID_RADIOBUTTON_BYBRAND, _("Brand name"), wxDefaultPosition, wxDefaultSize, 0 )
		self.szrSearchBy.AddWindow( self.rbtnSearchBrand, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxTOP, 1 )

		self.rbtnSearchGeneric = wxRadioButton( self, ID_RADIOBUTTON_BYGENERIC, _("Generic name"), wxDefaultPosition, wxDefaultSize, 0 )
		self.szrSearchBy.AddWindow( self.rbtnSearchGeneric, 0, wxGROW|wxALIGN_CENTER_VERTICAL, 1 )

		self.rbtnSearchIndication = wxRadioButton( self, ID_RADIOBUTTON_BYINDICATION, _("Indication"), wxDefaultPosition, wxDefaultSize, 0 )
		self.szrSearchBy.AddWindow( self.rbtnSearchIndication, 0, wxGROW|wxALIGN_CENTER_VERTICAL, 1 )

		self.szrVInteractionSidebar.AddSizer( self.szrSearchBy, 0, wxGROW|wxALIGN_CENTER_VERTICAL, 5 )

		self.szrVInteractionSidebar.AddSpacer( 30, 10, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxALL, 5 )

		stxtJumpTo = wxStaticText( self, ID_TEXT, _("jump to"), wxDefaultPosition, wxDefaultSize, 0 )
		stxtJumpTo.SetFont( wxFont( 8, wxSWISS, wxNORMAL, wxNORMAL ) )
		self.szrVInteractionSidebar.AddWindow( stxtJumpTo, 0, wxALIGN_CENTER_VERTICAL, 5 )

		self.lboxJumpTo = wxListBox( self, ID_LISTBOX, wxDefaultPosition, wxSize(150,100),
			[_("Indications"), _("Pharmacology"), _("Dosage")] , wxLB_SINGLE )
		self.szrVInteractionSidebar.AddWindow( self.lboxJumpTo, 1, wxGROW|wxALIGN_CENTER_VERTICAL, 10 )

		self.szrVInteractionSidebar.AddSpacer( 20, 10, 0, wxALIGN_CENTRE|wxALL, 1 )

		self.btnPrescribe = wxButton( self, ID_BUTTON_PRESCRIBE, _("&Prescribe"), wxDefaultPosition, wxDefaultSize, 0 )
		self.szrVInteractionSidebar.AddWindow( self.btnPrescribe, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxALL, 1 )

		self.btnDisplay = wxButton( self, ID_BUTTON_DISPLAY, _("&Display"), wxDefaultPosition, wxDefaultSize, 0 )
		self.szrVInteractionSidebar.AddWindow( self.btnDisplay, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxALL, 1 )

		self.btnPrint = wxButton( self, ID_BUTTON_PRINT, _("&Print"), wxDefaultPosition, wxDefaultSize, 0 )
		self.szrVInteractionSidebar.AddWindow( self.btnPrint, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxALL, 1 )

		self.szrHTop.AddSizer( self.szrVInteractionSidebar, 0, wxGROW|wxALIGN_CENTER_HORIZONTAL|wxALL, 5 )

		self.szrVTop.AddSizer( self.szrHTop, 1, wxGROW|wxALIGN_CENTER_VERTICAL|wxALL, 5 )

		self.SetAutoLayout( true )
		self.SetSizer( self.szrVTop )
		self.szrVTop.Fit( self )
		self.szrVTop.SetSizeHints( self )


if __name__ == "__main__":
	app = wxPyWidgetTester(size = (600, 450))
	app.SetWidget(DrugDisplay, -1)
	app.MainLoop()
