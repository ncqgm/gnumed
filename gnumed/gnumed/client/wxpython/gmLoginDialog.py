"""gmLoginDialog - This module provides a login dialog to GNUMed

It features combo boxes which "remember" any number of previously entered settings

author: Dr. Horst Herb
license: GPL (details at http://www.gnu.org)

dependencies: wxPython

change log:
	10.10.2001 initial implementation, untested
"""

from wxPython.wx import *
import gettext
_ = gettext.gettext


def ListToString(strlist, separator='|'):
	"""converts a list of strings into a character separated string of string items"""

	try:
		str = strlist[0]
	except:
		return None
	for setting in strlist[1:]:
		str = "%s%s%s" % (str, separator, setting)
	return str


def StringToList(str, separator='|'):
	"""converts a character separated string items into a list"""

	return string.split(str, separator)


def ComboBoxItems(combobox):
	"""returns all items in a combo box as list; the value of the text box as first item."""

	#get the current item in the text box first
	li = [combobox.GetValue()]
	for index in range(0, combobox.Number()):
		s = combobox.GetString(index)
		#weed out duplicates and empty strings
		if s is not None and s != '' and s not in li:
			li.append(s)
	return li


class LoginParameters:
	"""dummy class, to be used as a structure for login parameters"""

	def __init__(self):
		self.userlist = ['gnumed', 'guest']
		self.password = ''
		self.databaselist = ['gnumed', 'demographica']
		self.hostlist=['localhost']
		self.portlist = ['5432']
		self.backendoptionlist = ['']



class LoginPanel(wxPanel):

	def __init__(self, parent, id,
                  pos = wxPyDefaultPosition, size = wxPyDefaultSize,
                  style = wxTAB_TRAVERSAL, loginparams=None ):

		wxPanel.__init__(self, parent, id, pos, size, style)
		self.parent=parent
		self.cancelled=false

		self.conf = wxFileConfig("gnumed", style=wxCONFIG_USE_LOCAL_FILE)

		self.loginparams = loginparams or LoginParameters()
		self.LoadSettings()

		self.topsizer = wxBoxSizer(wxVERTICAL)
		self.paramsbox = wxStaticBox( self, -1, _("Login Parameters"))
		self.paramsboxsizer = wxStaticBoxSizer( self.paramsbox, wxVERTICAL )

		self.pboxgrid = wxFlexGridSizer( 4, 2, 5, 5 )
		self.pboxgrid.AddGrowableCol( 1 )

		label = wxStaticText( self, -1, _("user"), wxDefaultPosition, wxDefaultSize, 0 )
		self.pboxgrid.AddWindow( label, 0, wxALIGN_CENTER_VERTICAL|wxALL, 5 )
		self.usercombo = wxComboBox( self, -1, "", wxDefaultPosition, wxSize(150,-1),
			self.loginparams.userlist , wxCB_DROPDOWN )
		self.pboxgrid.AddWindow( self.usercombo, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxALL, 5 )

		label = wxStaticText( self, -1, _("password"), wxDefaultPosition, wxDefaultSize, 0 )
		self.pboxgrid.AddWindow( label, 0, wxALIGN_CENTER_VERTICAL|wxALL, 5 )
		self.pwdentry = wxTextCtrl( self, 1, '', wxDefaultPosition, wxSize(80,-1), wxTE_PASSWORD )
		self.pboxgrid.AddWindow( self.pwdentry, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxALL, 5 )

		label = wxStaticText( self, -1, _("database"), wxDefaultPosition, wxDefaultSize, 0 )
		self.pboxgrid.AddWindow( label, 0, wxALIGN_CENTER_VERTICAL|wxALL, 5 )
		self.dbcombo = wxComboBox( self, -1, '', wxDefaultPosition, wxSize(100,-1),
			self.loginparams.databaselist , wxCB_DROPDOWN )
		self.pboxgrid.AddWindow( self.dbcombo, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxALL, 5 )

		label = wxStaticText( self, -1, _("host"), wxDefaultPosition, wxDefaultSize, 0 )
		self.pboxgrid.AddWindow( label, 0, wxALIGN_CENTER_VERTICAL|wxALL, 5 )
		self.hostcombo = wxComboBox( self, -1, "", wxDefaultPosition, wxSize(100,-1),
			self.loginparams.hostlist , wxCB_DROPDOWN )
		self.pboxgrid.AddWindow( self.hostcombo, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxALL, 5 )

		label = wxStaticText( self, -1, _("port"), wxDefaultPosition, wxDefaultSize, 0 )
		self.pboxgrid.AddWindow( label, 0, wxALIGN_CENTER_VERTICAL|wxALL, 5 )
		self.portcombo = wxComboBox( self, -1, "", wxDefaultPosition, wxSize(100,-1),
			self.loginparams.portlist , wxCB_DROPDOWN )
		self.pboxgrid.AddWindow( self.portcombo, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxALL, 5 )

		label = wxStaticText( self, -1, _("backend options"), wxDefaultPosition, wxDefaultSize, 0 )
		self.pboxgrid.AddWindow( label, 0, wxALIGN_CENTER_VERTICAL|wxALL, 5 )
		self.beoptioncombo= wxComboBox( self, -1, "", wxDefaultPosition, wxSize(100,-1),
			self.loginparams.backendoptionlist , wxCB_DROPDOWN )
		self.pboxgrid.AddWindow( self.beoptioncombo, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxALL, 5 )

		self.buttonsizer = wxBoxSizer( wxHORIZONTAL )

		ID_BUTTON_LOGIN = wxNewId()
		button = wxButton( self, ID_BUTTON_LOGIN, _("&Login"), wxDefaultPosition, wxDefaultSize, 0 )
		button.SetDefault()
		self.buttonsizer.AddWindow( button, 0, wxALIGN_CENTRE|wxALL, 5 )

		ID_BUTTON_SAVECONF = wxNewId()
		button = wxButton( self, ID_BUTTON_SAVECONF, _("&Save conf."), wxDefaultPosition, wxDefaultSize, 0 )
		button.SetToolTip( wxToolTip(_("Save current entries in configuration file")) )
		self.buttonsizer.AddWindow( button, 0, wxALIGN_CENTRE|wxALL, 5 )

		self.buttonsizer.AddSpacer( 10, 20, 0, wxALIGN_CENTRE|wxALL, 5 )

		ID_BUTTON_HELP = wxNewId()
		button = wxButton( self, ID_BUTTON_HELP, _("&Help"), wxDefaultPosition, wxDefaultSize, 0 )
		self.buttonsizer.AddWindow( button, 0, wxALIGN_CENTRE|wxALL, 5 )

		self.buttonsizer.AddSpacer( 10, 20, 1, wxALIGN_CENTRE|wxALL, 5 )

		ID_BUTTON_CANCEL = wxNewId()
		button = wxButton( self, ID_BUTTON_CANCEL, _("&Cancel"), wxDefaultPosition, wxDefaultSize, 0 )
		self.buttonsizer.AddWindow( button, 0, wxALIGN_CENTRE|wxALL, 5 )

		self.paramsboxsizer.AddSizer(self.pboxgrid, 1, wxGROW|wxALL, 10)
		self.topsizer.AddSizer(self.paramsboxsizer, 1, wxGROW|wxALL, 10)
		self.topsizer.AddSizer( self.buttonsizer, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxALL, 5 )

		self.SetAutoLayout( true )
		self.SetSizer( self.topsizer)
		self.topsizer.Fit( self )
		#self.topsizer.SetSizeHints( self )

		EVT_BUTTON(self, ID_BUTTON_HELP, self.OnHelp)
		EVT_BUTTON(self, ID_BUTTON_SAVECONF, self.OnSaveConfiguration)
		EVT_BUTTON(self, ID_BUTTON_LOGIN, self.OnLogin)
		EVT_BUTTON(self, ID_BUTTON_CANCEL, self.OnCancel)


	def LoadSettings(self):
		self.loginparams.userlist = StringToList(self.conf.Read("/login/user"))
		self.loginparams.password = ''
		self.loginparams.databaselist = StringToList(self.conf.Read("login/database"))
		self.loginparams.hostlist = StringToList(self.conf.Read("/login/host"))
		self.loginparams.portlist = StringToList(self.conf.Read("/login/port"))
		self.loginparams.backendoptionlist = StringToList(self.conf.Read("/login/backendoption"))

	def SaveSettings(self):
		print ListToString(self.loginparams.userlist)
		self.conf.Write("/login/user", ListToString(ComboBoxItems(self.usercombo)))
		self.conf.Write("/login/database", ListToString(ComboBoxItems(self.dbcombo)))
		self.conf.Write("/login/host", ListToString(ComboBoxItems(self.hostcombo)))
		self.conf.Write("/login/port", ListToString(ComboBoxItems(self.portcombo)))
		self.conf.Write("/login/backendoption", ListToString(ComboBoxItems(self.beoptioncombo)))


	def GetLoginParams(self):
		if not self.cancelled:
			self.loginparams.userlist = ComboBoxItems(self.usercombo)
			self.loginparams.password = self.GetPassword()
			self.loginparams.databaselist = ComboBoxItems(self.dbcombo)
			self.loginparams.hostlist = ComboBoxItems(self.hostcombo)
			self.loginparams.portlist = ComboBoxItems(self.portcombo)
			self.loginparams.backendoptionlist = ComboBoxItems(self.beoptioncombo)
		return self.loginparams

	def GetUser(self):
		return self.usercombo.GetValue()

	def SetUser(self, user):
		self.usercombo.SetValue(user)

	def GetPassword(self):
		return self.pwdentry.GetValue()

	def SetPassword(self, pwd):
		self.pwdentry.SetValue(pwd)

	def GetDatabase(self):
		return self.dbcombo.GetValue()

	def SetDatabase(self, db):
		self.dbcombo.SetValue(db)

	def GetHost(self):
		return self.hostcombo.GetValue()

	def SetHost(self, host):
		self.dbcombo.SetValue(host)

	def GetBackendOptions(self):
		return self.beoptioncombo.GetValue()

	def SetBackendOptions(self, opt):
		self.beoptioncombo.SetValue(opt)

	def GetPort(self):
		return self.portcombo.GetValue()

	def SetPort(self, port):
		self.portcombo.SetValue(port)



	def OnHelp(self, event):
		wxMessageBox("Sorry, not implemented yet!")


	def OnSaveConfiguration(self, event):
		self.SaveSettings()

	def OnLogin(self, event):
		self.cancelled = false
		self.parent.Close()


	def OnCancel(self, event):
		self.cancelled = true
		self.parent.Close()



if __name__ == '__main__':
	app = wxPyWidgetTester(size = (400, 400))
	app.SetWidget(LoginPanel, -1)
	app.MainLoop()


