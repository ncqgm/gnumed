#!/usr/bin/python
#############################################################################
#
# gmPersonDetails - dialog elements for personal details like name and adddress
# ---------------------------------------------------------------------------
#
# @author: Dr. Horst Herb
# @copyright: author
# @license: GPL (details at http://www.gnu.org)
# @dependencies: nil
# @change log:
#	10.03.2002 hherb first draft, largely untested
#
# @TODO: Almost everything
############################################################################

from wxPython.wx import *
import gettext
_ = gettext.gettext



ID_COMBO_TITLE = wxNewId()
ID_TEXTCTRL_GIVENNAMES = wxNewId()
ID_TEXTCTRL_SURNAMES = wxNewId()
ID_TEXTCTRL = wxNewId()
ID_CHOICE_PREFNAME = wxNewId()
ID_CHOICE_GENDER = wxNewId()
ID_TEXTCTRL_DOB = wxNewId()
ID_COMBO_COB = wxNewId()
ID_BUTTON_PREVNAMES = wxNewId()
ID_BUTTON_PHOTOS = wxNewId()
ID_COMBO_ADDRAT = wxNewId()
ID_BUTTON_ADDADDR = wxNewId()
ID_TEXTCTRL_ADDRESS1 = wxNewId()
ID_TEXTCTRL_STREET = wxNewId()
ID_TEXTCTRL_STREETNO = wxNewId()
ID_TEXTCTRL_CITY = wxNewId()
ID_TEXTCTRL_POSTCODE = wxNewId()
ID_CHOICE_COUNTRY = wxNewId()
ID_COMBO_PHONEFOR = wxNewId()
ID_TEXTCTRL_PHONENUMBER = wxNewId()
ID_TEXTCTRL_PHONECOMMENT = wxNewId()
ID_BUTTON_ADDPHONE = wxNewId()
ID_COMBO_EMAILFOR = wxNewId()
ID_TEXTCTRL_URL = wxNewId()
ID_BUTTON_ADDURL = wxNewId()


#a few helper functions for less typing & better code readability

def CaptionSizer(parent, caption):
	"return a vertical sizer with a left aligned caption"
	szr = wxBoxSizer( wxVERTICAL )
	txt = wxStaticText( parent, -1, caption, wxDefaultPosition, wxDefaultSize, 0 )
    	szr.AddWindow( txt, 0, wxALIGN_CENTER_VERTICAL, 5 )
	return szr

def ButtonInVSizer(parent, id, caption):
	"return a button in a vertical sizer with a spacer taking the place of a caption"
	szr = wxBoxSizer( wxVERTICAL )
	szr.AddSpacer( 20, 10, 0, wxALIGN_CENTRE|wxBOTTOM, 5 )
	btn = wxButton( parent, id, caption, wxDefaultPosition, wxDefaultSize, 0 )
	szr.AddWindow( btn , 0, wxALIGN_CENTRE, 5 )
	return btn, szr



def PersonDetailsFunc( parent, call_fit = true, set_sizer = true ):
	"dialog elements for displaying, adding and editing personal details"

	#a vertical box sizer to contain them all
	parent.szrTop = wxBoxSizer( wxVERTICAL )

	#a container for the person's names
	parent.szrHBoxNames = wxBoxSizer( wxHORIZONTAL )

	#title
	szr = CaptionSizer(parent, _("title"))
	parent.comboTitle = wxComboBox( parent, ID_COMBO_TITLE, "", wxDefaultPosition, wxSize(70,-1),
		[_("Ms."),_("Mrs."),_("Mr."),_("Dr."),_("Prof.")] , wxCB_DROPDOWN )
	szr.AddWindow( parent.comboTitle, 0, wxALIGN_CENTER_VERTICAL, 5 )
	parent.szrHBoxNames.AddSizer( szr, 0, wxALIGN_CENTRE|wxLEFT|wxRIGHT, 5 )

	#given names
	szr = CaptionSizer(parent, _("given name(s)"))
	parent.tcGivenNames = wxTextCtrl( parent, ID_TEXTCTRL_GIVENNAMES, "", wxDefaultPosition, wxSize(120,-1), 0 )
	szr.AddWindow( parent.tcGivenNames, 1, wxGROW|wxALIGN_CENTER_VERTICAL, 5 )
	parent.szrHBoxNames.AddSizer( szr, 1, wxALIGN_CENTRE|wxLEFT|wxRIGHT, 5 )

	#surnames
	szr = CaptionSizer(parent,_("surname(s)"))
	parent.tcSurnames = wxTextCtrl( parent, ID_TEXTCTRL_SURNAMES, "", wxDefaultPosition, wxSize(130,-1), 0 )
	szr.AddWindow( parent.tcSurnames, 0, wxGROW|wxALIGN_CENTER_VERTICAL, 5 )
	parent.szrHBoxNames.AddSizer( szr, 1, wxALIGN_CENTRE|wxALL, 5 )

	#also known as (a.k.a.)
	szr = CaptionSizer(parent,_("a.k.a."))
	parent.tcAka = wxTextCtrl( parent, ID_TEXTCTRL, "", wxDefaultPosition, wxSize(80,-1), 0 )
	szr.AddWindow( parent.tcAka, 1, wxGROW|wxALIGN_CENTER_VERTICAL, 5 )
	parent.szrHBoxNames.AddSizer( szr, 0, wxALIGN_CENTRE|wxALL, 5 )

	#preferred name
	szr = CaptionSizer(parent,_("preferred"))
	parent.chPreferredName = wxChoice( parent, ID_CHOICE_PREFNAME, wxDefaultPosition, wxSize(90,-1), [], 0 )
	szr.AddWindow( parent.chPreferredName, 0, wxALIGN_CENTRE, 5 )
	parent.szrHBoxNames.AddSizer( szr, 0, wxALIGN_CENTRE|wxALL, 5 )

	#add the "names" row sizer to the main vertical sizer
	parent.szrTop.AddSizer( parent.szrHBoxNames, 0, wxGROW|wxALIGN_CENTER_VERTICAL, 5 )

	#another row sizer, this one for gender, date and country of birth etc.
	parent.szrHBoxDates = wxBoxSizer( wxHORIZONTAL )

	#gender
	szr = CaptionSizer(parent,_("gender"))
	parent.chGender = wxChoice( parent, ID_CHOICE_GENDER, wxDefaultPosition, wxSize(70,-1),
		[_("?"),_("male"),_("female"),_("hermaphr."),_("pmgf"),_("pfgm")] , 0 )
	szr.AddWindow( parent.chGender, 0, wxALIGN_CENTER_VERTICAL, 5 )
	parent.szrHBoxDates.AddSizer( szr, 0, wxALIGN_CENTRE|wxALL, 5 )

	#date of birth
	szr = CaptionSizer(parent,_("d.o.b"))
	parent.tcDob = wxTextCtrl( parent, ID_TEXTCTRL_DOB, "", wxDefaultPosition, wxSize(90,-1), 0 )
	szr.AddWindow( parent.tcDob, 0, wxGROW|wxALIGN_CENTER_VERTICAL, 5 )
	parent.szrHBoxDates.AddSizer( szr, 1, wxALIGN_CENTRE|wxALL, 5 )

	#country of birth
	szr = CaptionSizer(parent,_("c.o.b"))
	parent.cbCob = wxComboBox( parent, ID_COMBO_COB, "", wxDefaultPosition, wxSize(100,-1), [], wxCB_DROPDOWN )
	szr.AddWindow( parent.cbCob, 0, wxGROW|wxALIGN_CENTER_VERTICAL, 5 )
	parent.szrHBoxDates.AddSizer( szr, 1, wxALIGN_CENTRE|wxALL, 5 )

	#this button pops up a list of previous names
	parent.btnPrevNames, szr = ButtonInVSizer(parent, ID_BUTTON_PREVNAMES, _("pre&v. names"))
	parent.szrHBoxDates.AddSizer( szr, 0, wxALIGN_CENTRE|wxALL, 5 )

	#this button pops up a photo related dialog (view, add)
	parent.btnPhotos, szr = ButtonInVSizer(parent, ID_BUTTON_PHOTOS, _("pho&tos"))
	parent.szrHBoxDates.AddSizer( szr, 0, wxALIGN_CENTRE|wxALL, 5 )

	#add the row with the dates, previous names and photos to the main vertical box sizer
	parent.szrTop.AddSizer( parent.szrHBoxDates, 0, wxGROW|wxALIGN_CENTER_VERTICAL, 5 )

	#separate the name details from the address details a bit
	line = wxStaticLine( parent, -1, wxDefaultPosition, wxDefaultSize, wxLI_HORIZONTAL )
	parent.szrTop.AddWindow( line, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxALL, 5 )

	#we need a selector for the type of address (home, work, parents, holidays ...)
	#a row sizer for this
	parent.szrAdddressCategory = wxBoxSizer( wxHORIZONTAL )

	txt = wxStaticText( parent, -1, _("Address at"), wxDefaultPosition, wxDefaultSize, 0 )
	parent.szrAdddressCategory.AddWindow( txt, 0, wxALIGN_CENTRE, 5 )

	parent.cbAddressAt = wxComboBox( parent, ID_COMBO_ADDRAT, "", wxDefaultPosition, wxSize(210,-1),
		[_("home")] , wxCB_DROPDOWN )
	parent.cbAddressAt.SetToolTip( wxToolTip(_("Categorize this address (i.e. \"home\", \"work\", \"holidays\")")) )
	parent.szrAdddressCategory.AddWindow( parent.cbAddressAt, 0, wxALIGN_CENTRE|wxALL, 5 )

	parent.btAddAddress = wxButton( parent, ID_BUTTON_ADDADDR, _("&Add"), wxDefaultPosition, wxDefaultSize, 0 )
	parent.szrAdddressCategory.AddWindow( parent.btAddAddress, 0, wxALIGN_CENTRE|wxALL, 5 )

	parent.szrTop.AddSizer( parent.szrAdddressCategory, 0, wxALIGN_CENTRE, 5 )

	#the first address line(s), whatever you need between name and street number and street
	parent.szrAddress1 = wxBoxSizer( wxHORIZONTAL )
	# amultiline edit control for this
	szr = CaptionSizer(parent,_("address"))
	parent.tcAddress1 = wxTextCtrl( parent, ID_TEXTCTRL_ADDRESS1, "", wxDefaultPosition, wxSize(80,40), wxTE_MULTILINE )
	szr.AddWindow(parent.tcAddress1 , 0, wxGROW|wxALIGN_CENTER_VERTICAL, 5 )
	parent.szrAddress1.AddSizer( szr, 1, wxALIGN_CENTRE, 5 )
	parent.szrTop.AddSizer( parent.szrAddress1, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxLEFT|wxRIGHT, 5 )

	#street and stree number:
	parent.szrStreet = wxBoxSizer( wxHORIZONTAL )

	#street number first
	szr = CaptionSizer(parent,_("no."))
	parent.tcStreetNo = wxTextCtrl( parent, ID_TEXTCTRL_STREETNO, "", wxDefaultPosition, wxSize(60,-1), 0 )
	szr.AddWindow( parent.tcStreetNo, 0, wxALIGN_CENTRE, 5 )
	parent.szrStreet.AddSizer( szr, 0, wxALIGN_CENTRE, 5 )

	#then street name
	szr = CaptionSizer(parent,_("street"))
	parent.tcStreet = wxTextCtrl( parent, ID_TEXTCTRL_STREET, "", wxDefaultPosition, wxSize(80,-1), 0 )
	szr.AddWindow( parent.tcStreet, 0, wxGROW|wxALIGN_CENTER_VERTICAL, 5 )
	parent.szrStreet.AddSizer( szr, 1, wxALIGN_CENTRE, 5 )

	parent.szrTop.AddSizer( parent.szrStreet, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxLEFT|wxRIGHT, 5 )

	#city and postcode
	parent.szrCity = wxBoxSizer( wxHORIZONTAL )

	#city first
	szr = CaptionSizer(parent,_("city/town"))
	parent.tcCity = wxTextCtrl( parent, ID_TEXTCTRL_CITY, "", wxDefaultPosition, wxSize(80,-1), 0 )
	szr.AddWindow( parent.tcCity, 0, wxGROW|wxALIGN_CENTER_VERTICAL, 5 )
	parent.szrCity.AddSizer( szr, 1, wxALIGN_CENTRE, 5 )

	#then the postcode
	szr = CaptionSizer(parent,_("postcode"))
	parent.tcPostcode = wxTextCtrl( parent, ID_TEXTCTRL_POSTCODE, "", wxDefaultPosition, wxSize(80,-1), 0 )
	szr.AddWindow( parent.tcPostcode, 0, wxALIGN_CENTRE, 5 )
	parent.szrCity.AddSizer( szr, 0, wxALIGN_CENTRE, 5 )

	#then the country code
	szr = CaptionSizer(parent,_("country"))
	parent.chCountry = wxChoice( parent, ID_CHOICE_COUNTRY, wxDefaultPosition, wxSize(90,-1), [], 0 )
	szr.AddWindow( parent.chCountry, 0, wxALIGN_CENTRE, 5 )
	parent.szrCity.AddSizer( szr, 0, wxALIGN_CENTRE, 5 )

	parent.szrTop.AddSizer( parent.szrCity, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxLEFT|wxRIGHT, 5 )

	#a line to spearate address from phone numbers and URLS
	line = wxStaticLine( parent, -1, wxDefaultPosition, wxDefaultSize, wxLI_HORIZONTAL )
	parent.szrTop.AddWindow( line, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxALL, 5 )

	#phone numbers of all sorts
	parent.szrPhone = wxBoxSizer( wxHORIZONTAL )

	#category of phone number
	szr = CaptionSizer(parent,_("phone at"))
	parent.cbPhoneFor = wxComboBox( parent, ID_COMBO_PHONEFOR, "", wxDefaultPosition, wxSize(100,-1),
		[_("home")] , wxCB_DROPDOWN )
	parent.cbPhoneFor.SetToolTip( wxToolTip(_("different phone numbers like \"home\", \"work\" \"fax home\", ...")) )
	szr.AddWindow( parent.cbPhoneFor, 0, wxALIGN_CENTRE, 5 )
	parent.szrPhone.AddSizer( szr, 0, wxALIGN_CENTRE, 5 )

	#area code
	szr = CaptionSizer(parent,_("areacode"))
	parent.tcAreacode = wxTextCtrl( parent, ID_TEXTCTRL, "", wxDefaultPosition, wxSize(50,-1), 0 )
	szr.AddWindow( parent.tcAreacode, 0, wxALIGN_CENTRE, 5 )
	parent.szrPhone.AddSizer( szr, 0, wxALIGN_CENTRE|wxLEFT|wxRIGHT, 5 )

	#phone number
	szr = CaptionSizer(parent,_("number"))
	parent.tcPhonenumber = wxTextCtrl( parent, ID_TEXTCTRL_PHONENUMBER, "", wxDefaultPosition, wxSize(130,-1), 0 )
	szr.AddWindow( parent.tcPhonenumber, 0, wxGROW|wxALIGN_CENTER_VERTICAL, 5 )
	parent.szrPhone.AddSizer( szr, 1, wxALIGN_CENTRE|wxLEFT|wxRIGHT, 5 )

	#comment for the phone number
	szr = CaptionSizer(parent,_("comment"))
	parent.tcPhoneComment = wxTextCtrl( parent, ID_TEXTCTRL_PHONECOMMENT, "", wxDefaultPosition, wxSize(90,-1), 0 )
	szr.AddWindow( parent.tcPhoneComment, 0, wxGROW|wxALIGN_CENTER_VERTICAL, 5 )
	parent.szrPhone.AddSizer( szr, 1, wxALIGN_CENTRE|wxALL, 5 )

	#a button to add more phone numbers
	parent.btnAddPhone, szr = ButtonInVSizer(parent, ID_BUTTON_ADDPHONE, _("A&dd"))
	parent.btnAddPhone.SetToolTip( wxToolTip(_("Add another phone number")) )
	parent.szrPhone.AddSizer( szr, 0, wxALIGN_CENTRE, 5 )

	parent.szrTop.AddSizer( parent.szrPhone, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxLEFT|wxRIGHT, 5 )

	#email addresses and other URLs
	parent.szrURL = wxBoxSizer( wxHORIZONTAL )

	#URL category
	szr = CaptionSizer(parent,_("email / URL for"))
	parent.cbUrlCategory = wxComboBox( parent, ID_COMBO_EMAILFOR, "", wxDefaultPosition, wxSize(100,-1),
		[_("private")] , wxCB_DROPDOWN )
	szr.AddWindow( parent.cbUrlCategory, 0, wxALIGN_CENTRE, 5 )
	parent.szrURL.AddSizer( szr, 0, wxALIGN_CENTRE, 5 )

	#the URL
	szr = CaptionSizer(parent,_("URL"))
	parent.tcURL = wxTextCtrl( parent, ID_TEXTCTRL_URL, "", wxDefaultPosition, wxSize(80,-1), 0 )
	parent.tcURL.SetToolTip( wxToolTip(_("an email address, web address, etc.")) )
	szr.AddWindow( parent.tcURL, 0, wxGROW|wxALIGN_CENTER_VERTICAL, 5 )
	parent.szrURL.AddSizer( szr, 1, wxALIGN_CENTRE|wxALL, 5 )


	#a button to add further URLs
	parent.btnAddPhone, szr = ButtonInVSizer(parent, ID_BUTTON_ADDURL, _("A&dd"))
	parent.szrURL.AddSizer( szr, 0, wxALIGN_CENTRE|wxALL, 5 )

	parent.szrTop.AddSizer( parent.szrURL, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxLEFT|wxRIGHT|wxBOTTOM, 5 )

	if set_sizer == true:
		parent.SetAutoLayout( true )
		parent.SetSizer( parent.szrTop )
		if call_fit == true:
			parent.szrTop.Fit( parent )
			parent.szrTop.SetSizeHints( parent )

	return parent.szrTop


class PnlPersonDetails(wxPanel):
	def __init__(self, parent, id, pos = wxPyDefaultPosition, size = wxPyDefaultSize, style = wxTAB_TRAVERSAL):
		wxPanel.__init__(self, parent, id, pos, size, style)
		szr = PersonDetailsFunc(self)
		parent.SetSizer( szr )
		szr.Fit( parent )
		szr.SetSizeHints( parent )



#################################################################################

if __name__ == "__main__":
	app = wxPyWidgetTester(size = (400, 500))
	app.SetWidget(PnlPersonDetails, -1)
	app.MainLoop()