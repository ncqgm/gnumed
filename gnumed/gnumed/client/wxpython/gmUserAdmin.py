#!/usr/bin/python
##############################################################################
#
# gmUserAdmin - a front end for user administration.  In its current state,
#               this represents a prototype for the user admin window.
#
# @author: Steven Duffy 
# @dependencies: wxPython
# @change log:
#     $Log: gmUserAdmin.py,v $
#     Revision 1.3  2002-07-10 19:43:36  ncq
#     - new i18n
#
#     Revision 1.2  2001/12/05 13:57:02  sduffy
#     Not all text was processed through gettext.  Changed this.
#
#     Revision 1.1  2001/12/04 20:35:57  sduffy
#     Initial Revision
#
#
# @TODO:
#  -this is currently standalone, integrate w/main GUI
#  -when database is ready, complete the backend
#  -fix so you don't have to enter the one and zero vals manually in grid
#
##############################################################################

from wxPython.wx import *
from wxPython.grid import *

class MyFrame(wxFrame):
	def __init__(self, parent, ID, title):
		wxFrame.__init__( self, parent, ID, title,
				wxPyDefaultPosition, wxSize( 450, 500)  )

		# Create main sizer
		self.mainSizer = wxBoxSizer( wxVERTICAL )

		# Put dialogs in static boxes
		self.staticUserBox = wxStaticBox( self, -1, _("User's Login") )
		self.staticInfoBox = wxStaticBox( self, -1, _("User's Info") )
		self.staticPermsBox = wxStaticBox( self, -1, 
				_("User's Permissions") )

		# Put the static boxes in static box sizers
		self.staticUserBoxS = wxStaticBoxSizer( self.staticUserBox, 
				wxHORIZONTAL )
		self.staticInfoBoxS = wxStaticBoxSizer( self.staticInfoBox, 
				wxVERTICAL )
		self.staticPermsBoxS = wxStaticBoxSizer( self.staticPermsBox, 
				wxHORIZONTAL )
		
		#
		# Add a combo box to UserBox
		self.staticUserBoxS.Add( wxComboBox( self, -1, "" ), 0, wxALL, 10 )
		self.staticUserBoxS.Add( wxButton( self, -1, _("Select") ), 0,
				wxALL, 10)

		#
		# Add User information to InfoBox (it will be in rows)
		self.userInfoRow1 = wxBoxSizer( wxHORIZONTAL )
		self.userInfoRow1a = wxBoxSizer( wxHORIZONTAL )
		self.userInfoRow1b = wxBoxSizer( wxHORIZONTAL )

		self.userInfoRow1a.Add( wxStaticText( self, -1, _("First Name: ") ) )
		self.userInfoRow1a.Add( wxTextCtrl( self, -1, "" ) )
		self.userInfoRow1b.Add( wxStaticText( self, -1, _("Last Name: ") ) )
		self.userInfoRow1b.Add( wxTextCtrl( self, -1, "" ) )

		self.userInfoRow1.AddSizer( self.userInfoRow1a, 1, wxALIGN_CENTER,10 )
		self.userInfoRow1.AddSizer( self.userInfoRow1b, 1, wxALIGN_CENTER,10 )

		self.userInfoRow2 = wxBoxSizer( wxHORIZONTAL )
		self.userInfoRow2.Add( wxStaticText( self, -1, _("Password: ") ) )
		self.userInfoRow2.Add( wxTextCtrl( self, -1, "" ) )

		self.userInfoRow3 = wxBoxSizer( wxHORIZONTAL )
		self.userInfoRow3.Add( wxStaticText( self, -1, 
				"Other user information from database..." ) )

		self.staticInfoBoxS.AddSizer( self.userInfoRow1, 1, 
				wxGROW|wxALL, 10 )
		self.staticInfoBoxS.AddSizer( self.userInfoRow2, 1, 
				wxGROW|wxALL, 10 )
		self.staticInfoBoxS.AddSizer( self.userInfoRow3, 1, 
				wxGROW|wxALL, 10 )

		#
		# Now for the permissions, these are in the form of a wxGrid
		self.grid = wxGrid( self, -1 )
				
		self.grid.CreateGrid( 4, 4 )

		self.grid.SetColLabelValue( 0, _("Read") )		# SELECT
		self.grid.SetColLabelValue( 1, _("Add") )		# INSERT
		self.grid.SetColLabelValue( 2, _("Change") )	# UPDATE
		self.grid.SetColLabelValue( 3, _("Delete") )	# DELETE

		self.grid.SetRowLabelValue( 0, "Service 1" )
		self.grid.SetRowLabelValue( 1, "Service 2" )
		self.grid.SetRowLabelValue( 2, "Service 3" )
		self.grid.SetRowLabelValue( 3, "Service 4" )

		self.grid.SetColFormatBool( 0 )
		self.grid.SetColFormatBool( 1 )
		self.grid.SetColFormatBool( 2 )
		self.grid.SetColFormatBool( 3 )

		self.staticPermsBoxS.Add( self.grid, 1, wxGROW|wxCENTER|wxALL, 10 )

		#
		# Add static boxes to mainsizer
		self.mainSizer.AddSizer( self.staticUserBoxS, 0, 
				wxGROW|wxALL, 5 )
		self.mainSizer.AddSizer( self.staticInfoBoxS, 0, 
				wxGROW|wxALL, 5 )
		self.mainSizer.AddSizer( self.staticPermsBoxS, 1, 
				wxGROW|wxALL, 5 )

		self.mainSizer.Add( wxButton( self, -1, _("Commit Changes") ), 0,
				wxALIGN_CENTER|wxALL, 10 )

		#
		# Now make the sizer active
		self.SetAutoLayout( true )
		self.SetSizer( self.mainSizer )
		self.mainSizer.SetSizeHints( self )


class MyApp(wxApp):
	def OnInit(self):
		frame = MyFrame(NULL, -1, _("User Administration") )
		frame.Show(true)
		self.SetTopWindow(frame)
		return true

if __name__ == '__main__':
	_ = lambda x:x
	app = MyApp(0)
	app.MainLoop()

