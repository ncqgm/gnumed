#!/usr/bin/python
#############################################################################
#
# gmLoginDialog - This module provides a login dialog to GNUMed
# ---------------------------------------------------------------------------
# It features combo boxes which "remember" any number of previously entered settings
#
# @author: Dr. Horst Herb
# @copyright: author
# @license: GPL (details at http://www.gnu.org)
# @dependencies: wxPython (>= version 2.3.1)
# @change log:
#	10.10.2001 hherb initial implementation, untested
#	24.10.2001 hherb comments added
#	24.10.2001 hherb LoginDialog class added,
#	24.10.2001 hherb persistent changes across multiple processes enabled
#	25.10.2001 hherb more flexible configuration options, more commenting
#	07.02.2002 hherb saved parameters now showing corectly in combo boxes
#
# @TODO:
############################################################################

"""gmLoginDialog - This module provides a login dialog to GNUMed
It features combo boxes which "remember" any number of previously entered settings
"""

from wxPython.wx import *
import os.path
import gmLoginInfo, gmGuiMain, gmGuiBroker, gmCfg
_cfg = gmCfg.gmDefCfgFile

#############################################################################
#
#############################################################################
#def StringToList(str, separator='|'):
#	"""converts a character separated string items into a list"""
#	return string.split(str, separator)
#############################################################################
# converts a list of strings into a character separated string of string items
#############################################################################

#def ListToString(strlist, separator='|'):
#	"""converts a list of strings into a character separated string of string items"""

#	try:
#		str = strlist[0]
#	except:
#		return None
#	for setting in strlist[1:]:
#		str = "%s%s%s" % (str, separator, setting)
#	return str


#############################################################################
# returns a distinct merger of all items contained in origstr and newstr
# and takes care of placing the most recent items at the beginnig of the
# list
#############################################################################

#def AppendSettings(origstr, newstr, maxitems=0, separator='|'):
#	"returns a distinct merger of all items contained in origstr and newstr"
#	origlist = StringToList(origstr, separator)
#	newlist = StringToList(newstr, separator)
#	newlist.reverse()
#	for item in newlist:
#		if item not in origlist:
			#if we care how many items should be in our list
#			if maxitems>0:
				#remove the last item if we have exceeded the quota
#				if len(origlist)>=maxitems:
#					origlist = origlist[:-1]
			#if it is a new item, insert it at the beginnig of the list
#			origlist.insert(0,item)
#		else:
			#move this item to the beginning of the list
#			origlist.remove(item)
#			origlist.insert(0,item)
#	return ListToString(origlist)

#############################################################################
# returns all items in a combo box as list; the value of the text box as first item.
#############################################################################

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


#############################################################################
# dummy class, to be used as a structure for login parameters
#############################################################################

class LoginParameters:
	"""dummy class, to be used as a structure for login parameters"""

	def __init__(self):
		self.userlist = ['gnumed', 'guest']
		self.password = ''
		self.databaselist = ['gnumed', 'demograph', 'gis', 'pharma']
		self.hostlist=['localhost']
		self.portlist = ['5432']
		self.backendoptionlist = ['']


#############################################################################
# GUI panel class that gets interactively Postgres login parameters
#############################################################################

class LoginPanel(wxPanel):
	"GUI panel class that gets interactively Postgres login parameters"

	# constructor parameters:
	#	loginparams: to override default login parameters and configuration file.
	#	             see class "LoginParameters" in this module
	#	isDialog: if this panel is the main panel of a dialog, the panel will
	#	          resize the dialog automatically to display everything neatly
	#	          if isDialog is set to true
	#	configroot: where to load and store saved settings; allows to have multiple
	#	          login dialogs with different settings within the same application
	#	          which is neccessary when working with distributed servers
	#	configfilename: name of configuration file. It is NOT neccessary to include
	#	          a path or extension here, as wxConfig will choose automatically
	#	          whatever is convention on the current platform
	#	maxitems: maximum number of items "remembered" in the comboboxes

	def __init__(self, parent, id, pos = wxPyDefaultPosition, size = wxPyDefaultSize, style = wxTAB_TRAVERSAL,
		loginparams = None,
		isDialog = 0,
		configroot = '/login' ,
		configfilename = 'gnumed',
		maxitems = 8):

		wxPanel.__init__(self, parent, id, pos, size, style)
		self.parent = parent

		#file name of configuration file - wxConfig takes care of path, extension etc.
		self.confname = configfilename
		self.gb = gmGuiBroker.GuiBroker ()
		#root of setings in the configuration file for this particular dialog
		self.configroot = configroot

		#true if dialog was cancelled by user
		self.cancelled = false

		#true if this panel is displayed within a dialog (will resize the dialog automatically then)
		self.isDialog = isDialog

		#the number of items we allow to be stored in the comboboxes "history"
		self.maxitems = maxitems

		#get some default login parameter settings in case the configuration file is empty
		self.loginparams = loginparams or LoginParameters()
		#if we didn't override the standard parameters, load them from the configuration file
		if loginparams==None:
			self.LoadSettings()

		self.topsizer = wxBoxSizer(wxVERTICAL)

		bitmap = os.path.join (self.gb['gnumed_dir'], 'bitmaps', 'gnumedlogo.png')
		try:
			wxImage_AddHandler(wxPNGHandler())
			png = wxImage(bitmap, wxBITMAP_TYPE_PNG).ConvertToBitmap()
			bmp = wxStaticBitmap(self, -1, png, wxPoint(10, 10), wxSize(png.GetWidth(), png.GetHeight()))
			self.topsizer.Add(bmp, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxALL, 10)
		except:
			self.topsizer.Add(wxStaticText (self, -1, "Cannot find image" + bitmap, style=wxALIGN_CENTRE), 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxALL, 10)

		self.paramsbox = wxStaticBox( self, -1, _("Login Parameters"))
		self.paramsboxsizer = wxStaticBoxSizer( self.paramsbox, wxVERTICAL )

		self.pboxgrid = wxFlexGridSizer( 4, 2, 5, 5 )
		self.pboxgrid.AddGrowableCol( 1 )

		#USER NAME COMBO
		label = wxStaticText( self, -1, _("user"), wxDefaultPosition, wxDefaultSize, 0 )
		self.pboxgrid.AddWindow( label, 0, wxALIGN_CENTER_VERTICAL|wxALL, 5 )
		self.usercombo = wxComboBox(
			self,
			-1,
			self.loginparams.userlist[0],
			wxDefaultPosition,
			wxSize(150,-1),
			self.loginparams.userlist,
			wxCB_DROPDOWN
		)
		self.pboxgrid.AddWindow( self.usercombo, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxALL, 5 )

		#PASSWORD TEXT ENTRY
		label = wxStaticText( self, -1, _("password"), wxDefaultPosition, wxDefaultSize, 0 )
		self.pboxgrid.AddWindow( label, 0, wxALIGN_CENTER_VERTICAL|wxALL, 5 )
		self.pwdentry = wxTextCtrl( self, 1, '', wxDefaultPosition, wxSize(80,-1), wxTE_PASSWORD )
		self.pboxgrid.AddWindow( self.pwdentry, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxALL, 5 )

		#DATABASE COMBO
		label = wxStaticText( self, -1, _("database"), wxDefaultPosition, wxDefaultSize, 0 )
		self.pboxgrid.AddWindow( label, 0, wxALIGN_CENTER_VERTICAL|wxALL, 5 )
		self.dbcombo = wxComboBox( self, -1, self.loginparams.databaselist[0], wxDefaultPosition, wxSize(100,-1),
			self.loginparams.databaselist , wxCB_DROPDOWN )
		self.pboxgrid.AddWindow( self.dbcombo, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxALL, 5 )

		#HOST NAME / IP NUMBER COMBO
		label = wxStaticText( self, -1, _("host"), wxDefaultPosition, wxDefaultSize, 0 )
		self.pboxgrid.AddWindow( label, 0, wxALIGN_CENTER_VERTICAL|wxALL, 5 )
		self.hostcombo = wxComboBox( self, -1, self.loginparams.hostlist[0], wxDefaultPosition, wxSize(100,-1),
			self.loginparams.hostlist , wxCB_DROPDOWN )
		self.pboxgrid.AddWindow( self.hostcombo, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxALL, 5 )

		#PORT NUMBER COMBO
		label = wxStaticText( self, -1, _("port"), wxDefaultPosition, wxDefaultSize, 0 )
		self.pboxgrid.AddWindow( label, 0, wxALIGN_CENTER_VERTICAL|wxALL, 5 )
		self.portcombo = wxComboBox( self, -1, self.loginparams.portlist[0], wxDefaultPosition, wxSize(100,-1),
			self.loginparams.portlist , wxCB_DROPDOWN )
		self.pboxgrid.AddWindow( self.portcombo, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxALL, 5 )

		#DATABASE BACKEND OPTIONS COMBO
		label = wxStaticText( self, -1, _("backend options"), wxDefaultPosition, wxDefaultSize, 0 )
		self.pboxgrid.AddWindow( label, 0, wxALIGN_CENTER_VERTICAL|wxALL, 5 )
		self.beoptioncombo= wxComboBox( self, -1, self.loginparams.backendoptionlist[0], wxDefaultPosition, wxSize(100,-1),
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
		if self.isDialog:
			self.topsizer.SetSizeHints( parent )

		EVT_BUTTON(self, ID_BUTTON_HELP, self.OnHelp)
		EVT_BUTTON(self, ID_BUTTON_SAVECONF, self.OnSaveConfiguration)
		EVT_BUTTON(self, ID_BUTTON_LOGIN, self.OnLogin)
		EVT_BUTTON(self, ID_BUTTON_CANCEL, self.OnCancel)


#############################################################################
# Initialize dialog widget settings from configuration file
#############################################################################
	def LoadSettings(self):
		"""Load parameter settings from standard configuration file"""

		self.loginparams.userlist = _cfg.get('backend', 'logins')
		if not self.loginparams.userlist:
			self.loginparams.userlist = ['guest']

		self.loginparams.password = ''

		self.loginparams.databaselist = _cfg.get('backend', 'databases')
		if not self.loginparams.databaselist:
			self.loginparams.databaselist = ['gnumed']

		self.loginparams.hostlist = _cfg.get('backend', 'hosts')
		if not self.loginparams.hostlist:
			self.loginparams.hostlist = ['localhost']

		self.loginparams.portlist = _cfg.get('backend', 'ports')
		if not self.loginparams.portlist:
			self.loginparams.portlist = ['5432']

		self.loginparams.backendoptionlist = _cfg.get('backend', 'options')
		if not self.loginparams.backendoptionlist:
			self.loginparams.backendoptionlist = ['']

#		conf = wxFileConfig(self.confname, style=wxCONFIG_USE_LOCAL_FILE)
#		self.loginparams.userlist = StringToList(conf.Read("/login/user"))
#		self.loginparams.password = ''
#		self.loginparams.databaselist = StringToList(conf.Read("login/database"))
#		self.loginparams.hostlist = StringToList(conf.Read("/login/host"))
#		self.loginparams.portlist = StringToList(conf.Read("/login/port"))
#		self.loginparams.backendoptionlist = StringToList(conf.Read("/login/backendoption"))

#############################################################################
# Save all settings to the configuration file
#############################################################################

#	def SaveSettingsFor(self, conf, key, setting):
		"""Append items not already existing in the configuration file
		and make sure that changes already committed by other processes
		using the same configuration file don't get overwritten"""

#		conf.Write(key, AppendSettings(conf.Read(key), setting, self.maxitems))

	def SaveSettings(self):
		"""Save parameter settings to standard configuration file"""

		_cfg.set('backend', 'logins', ComboBoxItems(self.usercombo))
		_cfg.set('backend', 'databases', ComboBoxItems(self.dbcombo))
		_cfg.set('backend', 'hosts', ComboBoxItems(self.hostcombo))
		_cfg.set('backend', 'ports', ComboBoxItems(self.portcombo))
		_cfg.set('backend', 'options', ComboBoxItems(self.beoptioncombo))

		_cfg.store()

		# set the location of the configuration file in a platform independent way
#		conf = wxFileConfig(self.confname, style=wxCONFIG_USE_LOCAL_FILE)
#		self.SaveSettingsFor(conf, "/login/user", ListToString(ComboBoxItems(self.usercombo)))
#		self.SaveSettingsFor(conf, "/login/database", ListToString(ComboBoxItems(self.dbcombo)))
#		self.SaveSettingsFor(conf, "/login/host", ListToString(ComboBoxItems(self.hostcombo)))
#		self.SaveSettingsFor(conf, "/login/port", ListToString(ComboBoxItems(self.portcombo)))
#		self.SaveSettingsFor(conf, "/login/backendoption", ListToString(ComboBoxItems(self.beoptioncombo)))
		# make sure changes are written to disk immediately
#		conf.Flush()

#############################################################################
# Retrieve current settings from user interface widgets
#############################################################################

	def GetLoginParams(self):
		"Fetch login parameters from dialog widgets - return None if the user pressed the 'Cancel' button"
		if not self.cancelled:
			self.loginparams.userlist = ComboBoxItems(self.usercombo)
			self.loginparams.password = self.GetPassword()
			self.loginparams.databaselist = ComboBoxItems(self.dbcombo)
			self.loginparams.hostlist = ComboBoxItems(self.hostcombo)
			self.loginparams.portlist = ComboBoxItems(self.portcombo)
			self.loginparams.backendoptionlist = ComboBoxItems(self.beoptioncombo)
			return self.loginparams
		else:
			return None

	def GetLoginInfo(self):
		if not self.cancelled:
			"convenience function for compatibility with gmLoginInfo.LoginInfo"
			login = gmLoginInfo.LoginInfo(self.GetUser(), self.GetPassword())
			login.SetDatabase(self.GetDatabase())
			login.SetHost(self.GetHost())
			login.SetPort(self.GetPort())
			login.SetOptions(self.GetBackendOptions())
			return login
		else:
			return None

#############################################################################
# Functions to get and set values in user interface widgets
#############################################################################

	def GetUser(self):
		"Get the selected user name from the text entry section of the user combo box"
		return self.usercombo.GetValue()

	def SetUser(self, user):
		"Set the selected user name from the text entry section of the user combo box"
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

#############################################################################
# GUI action functions from here on
#############################################################################

	def OnHelp(self, event):
		wxMessageBox(_("Sorry, not implemented yet!"))


	def OnSaveConfiguration(self, event):
		self.SaveSettings()

	def OnLogin(self, event):
		self.cancelled = false
		self.parent.Close()


	def OnCancel(self, event):
		self.cancelled = true
		self.parent.Close()



class LoginDialog(wxDialog):
	def __init__(self, parent, id, title=_("Login")):
		wxDialog.__init__(self, parent, id, title)
		self.panel = LoginPanel(self, -1, isDialog=1)
		self.Fit () # needed for Windoze.
		self.Centre()



#############################################################################
# test function for this module: simply run the module as "main"
#############################################################################

if __name__ == '__main__':
	import gmI18N

	app = wxPyWidgetTester(size = (400, 500))
	#show the login panel in a main window
	app.SetWidget(LoginPanel, -1)
	#and pop the login dialog up modally
	dlg = LoginDialog(NULL, -1, png_bitmap = 'bitmaps/gnumedlogo.png')
	dlg.ShowModal()
	#demonstration how to access the login dialog values
	lp = dlg.panel.GetLoginParams()
	if lp is None:
		wxMessageBox(_("Dialog was cancelled by user"))
	else:
		wxMessageBox(_("You tried to log in as [%s] with password [%s].") % (lp.userlist[0], lp.password))
	dlg.Destroy()
	app.MainLoop()
