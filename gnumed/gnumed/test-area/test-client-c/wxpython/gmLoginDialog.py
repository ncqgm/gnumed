"""gmLoginDialog - This module provides a login dialog to GNUMed

It features combo boxes which "remember" any number of previously entered settings
"""
#############################################################################
#
# gmLoginDialog - This module provides a login dialog to GNUMed
# ---------------------------------------------------------------------------
# It features combo boxes which "remember" any number of previously entered settings
#
# @copyright: author
# @license: GPL (details at http://www.gnu.org)
# @dependencies: wxPython (>= version 2.3.1)
############################################################################
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/test-area/test-client-c/wxpython/Attic/gmLoginDialog.py,v $
# $Id: gmLoginDialog.py,v 1.1 2003-10-23 06:02:39 sjtan Exp $
__version__ = "$Revision: 1.1 $"
__author__ = "H.Herb, H.Berger, R.Terry, K.Hilbert"

import os.path, time, cPickle, zlib,types
from wxPython.wx import *
import gmLoginInfo, gmGuiMain, gmGuiBroker, gmCfg, gmLog
_cfg = gmCfg.gmDefCfgFile
_log = gmLog.gmDefLog

#====================================================
class cLoginParamChoices:
	"""dummy class, structure for login parameters"""
	def __init__(self):
		self.userlist = ['test-doc']
		self.password = ''
		self.databaselist = ['gnumed', 'gm-archive', 'gnumed-public']
		self.hostlist= ['localhost', '127.0.0.1']
		self.portlist = ['5432']
		self.backendoptionlist = ['']

#====================================================
class LoginPanel(wxPanel):
	"""GUI panel class that interactively gets Postgres login parameters"""

	def __init__(self, parent, id,
		pos = wxPyDefaultPosition,
		size = wxPyDefaultSize,
		style = wxTAB_TRAVERSAL,
		loginparams = None,
		isDialog = 0
		):
		"""Create login panel.

		loginparams:	to override default login parameters and configuration file.
						see class "LoginParameters" in this module
		isDialog:	if this panel is the main panel of a dialog, the panel will
					resize the dialog automatically to display everything neatly
					if isDialog is set to true
		"""
		wxPanel.__init__(self, parent, id, pos, size, style)
		self.parent = parent

		self.gb = gmGuiBroker.GuiBroker()

		#true if dialog was cancelled by user 
		#if the dialog is closed manually, login should be cancelled
		self.cancelled = true

		# true if this panel is displayed within a dialog (will resize the dialog automatically then)
		self.isDialog = isDialog

		# if no login params supplied get default ones or from config file
		if loginparams is None:
			self.__load_login_param_choices()
		else:
			self.loginparams = loginparams

		self.topsizer = wxBoxSizer(wxVERTICAL)

		bitmap = os.path.join (self.gb['gnumed_dir'], 'bitmaps', 'gnumedlogo.png')
		try:
			wxImage_AddHandler(wxPNGHandler())
			png = wxImage(bitmap, wxBITMAP_TYPE_PNG).ConvertToBitmap()
			bmp = wxStaticBitmap(self, -1, png, wxPoint(10, 10), wxSize(png.GetWidth(), png.GetHeight()))
			self.topsizer.Add(bmp, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxALL, 10)
		except:
			self.topsizer.Add(wxStaticText (self, -1, _("Cannot find image") + bitmap, style=wxALIGN_CENTRE), 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxALL, 10)

		tmp = _cfg.get('workplace', 'name')
		if tmp is None:
			print _('You should name this workplace to better identify the machine !\nTo do this set the option "name" in the group [workplace] in the config file !')
			tmp = _("<no workplace name set in config file>")
			self.gb['workplace_name'] = '__default__'
		else:
			self.gb['workplace_name'] = tmp

		paramsbox_caption = _("Login - %s" % tmp)
		#why doesn't this align in the centre ?
		self.paramsbox = wxStaticBox( self, -1, paramsbox_caption, style=wxALIGN_CENTRE_HORIZONTAL)
		self.paramsboxsizer = wxStaticBoxSizer( self.paramsbox, wxVERTICAL )
		self.paramsbox.SetForegroundColour(wxColour(35, 35, 142))
		self.paramsbox.SetFont(wxFont(
			pointSize = 12,
			family = wxSWISS,
			style = wxNORMAL,
			weight = wxBOLD,
			underline = false,
			faceName = ''
		))
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
		
		#----------------------------------------------------------------------
		#new button code inserted rterry 06Sept02
		#button order re-arraged to make it consistant with usual dialog format
		#in most operating systems ie  btns ok and cancel are standard and 
		#in that order
		#ie Order is now Options, help, ok and cancel
		#The order of creation is the tab order
		#login-ok button automatically is the default when tabbing (or <enter>)
		#from password
		#this eliminates the heavy border when you use the default 
		#?is the default word needed for any other reason?
		#----------------------------------------------------------------------
		self.button_gridsizer = wxGridSizer(1,4,0,0)
		#---------------------
		#3:create login ok button
		#---------------------
		ID_BUTTON_LOGIN = wxNewId()
		button_login_ok = wxButton(self, ID_BUTTON_LOGIN, _("&Ok"), wxDefaultPosition, wxDefaultSize, 0 )
		button_login_ok.SetToolTip(wxToolTip(_("Proceed with login.")) )
		#---------------------
		#3:create cancel button
		#---------------------
		ID_BUTTON_CANCEL = wxNewId()
		button_cancel = wxButton(self, ID_BUTTON_CANCEL, _("&Cancel"), wxDefaultPosition, wxDefaultSize, 0 )
		button_cancel.SetToolTip(wxToolTip(_("Cancel Login.")) )
		#-------------------
		#1:create option button
		#-------------------
		ID_BUTTON_OPTIONS = wxNewId()
		button_option = wxButton(self, ID_BUTTON_OPTIONS, _("&Options"), wxDefaultPosition, wxDefaultSize, 0 )
		button_option.SetToolTip( wxToolTip(_("Set advanced options like database, host, port etc.")) )
		#---------------------
		#2:create Help button
		#---------------------
		ID_BUTTON_HELP = wxNewId()
		button_help = wxButton(self, ID_BUTTON_HELP, _("&Help"), wxDefaultPosition, wxDefaultSize, 0 )
		button_help.SetToolTip(wxToolTip(_("Help for login screen")) )
		#----------------------------
		#Add buttons to the gridsizer
		#----------------------------
		self.button_gridsizer.Add (button_option,0,wxEXPAND|wxALL,5)
		self.button_gridsizer.Add (button_help,0,wxEXPAND|wxALL,5)
		self.button_gridsizer.Add (button_login_ok,0,wxEXPAND|wxALL,5)
		self.button_gridsizer.Add (button_cancel,0,wxEXPAND|wxALL,5)
               
		self.paramsboxsizer.AddSizer(self.pboxgrid, 1, wxGROW|wxALL, 10)
		self.topsizer.AddSizer(self.paramsboxsizer, 1, wxGROW|wxALL, 10)
		#old code:self.topsizer.AddSizer(self.infoboxsizer, 0,wxGROW|wxALL, 10)
		self.topsizer.AddSizer( self.button_gridsizer, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxALL, 5 )

		self.SetAutoLayout( true )
		self.SetSizer( self.topsizer)
		self.topsizer.Fit( self )
		if self.isDialog:
			self.topsizer.SetSizeHints(parent)

		EVT_BUTTON(self, ID_BUTTON_HELP, self.OnHelp)
		EVT_BUTTON(self, ID_BUTTON_OPTIONS, self.OnOptions)
		EVT_BUTTON(self, ID_BUTTON_LOGIN, self.OnLogin)
		EVT_BUTTON(self, ID_BUTTON_CANCEL, self.OnCancel)

	#----------------------------
	# internal helper methods
	#----------------------------
	def __load_login_param_choices(self):
		"""Load parameter settings from standard configuration file"""
		self.loginparams = cLoginParamChoices()

		tmp = _cfg.get('backend', 'logins')
		if type(tmp) is types.ListType and len(tmp) > 0:
			self.loginparams.userlist = tmp

		tmp = _cfg.get('backend', 'databases')
		if type(tmp) is types.ListType and len(tmp) > 0:
			self.loginparams.databaselist = tmp

		tmp = _cfg.get('backend', 'hosts')
		if type(tmp) is types.ListType and len(tmp) > 0:
			self.loginparams.hostlist = tmp

		tmp = _cfg.get('backend', 'ports')
		if type(tmp) is types.ListType and len(tmp) > 0:
			self.loginparams.portlist = tmp

		tmp = _cfg.get('backend', 'options')
		if type(tmp) is types.ListType and len(tmp) > 0:
			self.loginparams.backendoptionlist = tmp
	#----------------------------
	def save_settings(self):
		"""Save parameter settings to standard configuration file"""

		_cfg.set('backend', 'logins', self.__cbox_to_list(self.usercombo))
		_cfg.set('backend', 'databases', self.loginparams.databaselist)
		_cfg.set('backend', 'hosts', self.loginparams.hostlist)
		_cfg.set('backend', 'ports', self.loginparams.portlist)
		_cfg.set('backend', 'options', self.loginparams.backendoptionlist)

		_cfg.store()
	#----------------------------
	def __cbox_to_list(self, aComboBox):
		"""returns all items in a combo box as list; the value of the text box as first item."""

		# get the current items in the text box first
		tmp = [ aComboBox.GetValue() ]
		for idx in range(aComboBox.GetCount()):
			s = aComboBox.GetString(idx)
			# weed out duplicates and empty strings
			if s not in [None, ''] and s not in tmp:
				tmp.append(s)
		return tmp

#############################################################################
# Retrieve current settings from user interface widgets
#############################################################################

	def GetLoginParams(self):
		"""Fetch login parameters from dialog widgets - return None if the user pressed the 'Cancel' button"""
		if not self.cancelled:
			self.loginparams.userlist = self.__cbox_to_list(self.usercombo)
			self.loginparams.password = self.GetPassword()
			# database, host, port and backend lists are updated by OptionWindow and should be up to date
			return self.loginparams
		else:
			return None

	def GetLoginInfo(self):
		"""convenience function for compatibility with gmLoginInfo.LoginInfo"""
		if not self.cancelled:
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
		"""Get the selected user name from the text entry section of the user combo box"""
		return self.usercombo.GetValue()

	def SetUser(self, user):
		"Set the selected user name from the text entry section of the user combo box"
		self.usercombo.SetValue(user)

	def GetPassword(self):
		return self.pwdentry.GetValue()

	def SetPassword(self, pwd):
		self.pwdentry.SetValue(pwd)

	def GetDatabase(self):
		return self.loginparams.databaselist[0]

	def SetDatabase(self, db):
		self.loginparams.databaselist[0]

	def GetHost(self):
		return self.loginparams.hostlist[0]

	def SetHost(self, host):
		self.loginparams.hostlist[0]

	def GetBackendOptions(self):
		return self.loginparams.backendoptionlist[0]

	def SetBackendOptions(self, opt):
		self.loginparams.backendoptionlist[0]

	def GetPort(self):
		return self.loginparams.portlist[0]

	def SetPort(self, port):
		self.loginparams.portlist[0]

	#----------------------------
	# event handlers
	#----------------------------
	def OnHelp(self, event):
		tmp = _cfg.get('workplace', 'help desk')
		if tmp is None:
			print _("You need to set the option [workplace] -> <help desk> in the config file !")
			tmp = "http://www.gnumed.org"

		wxMessageBox(_(
"""GnuMed main login screen

USER:
 name of the GnuMed user
PASSWORD
 password for this user

button OK:
 proceed with login
button OPTIONS:
 set advanced options
button CANCEL:
 abort login and quit GnuMed client
button HELP:
 this help screen

For assistance on using GnuMed please contact:
 %s""") % tmp)
	#----------------------------
	def OnOptions(self, event):
		self.optionwindow = OptionWindow(self,wxNewId(),loginparams=self.loginparams)
		self.optionwindow.ShowModal()
		if not self.optionwindow.panel.cancelled: 
		    self.loginparams.databaselist = self.__cbox_to_list(self.optionwindow.panel.dbcombo)
		    self.loginparams.hostlist = self.__cbox_to_list(self.optionwindow.panel.hostcombo)
		    self.loginparams.portlist = self.__cbox_to_list(self.optionwindow.panel.portcombo)
		    self.loginparams.backendoptionlist = self.__cbox_to_list(self.optionwindow.panel.beoptioncombo)
	#----------------------------		
	def OnLogin(self, event):
		self.cancelled = false
		self.parent.Close()
	#----------------------------
	def OnCancel(self, event):
		self.cancelled = true
		self.parent.Close()

#====================================================
class LoginDialog(wxDialog):
	"""LoginDialog - window holding LoginPanel"""

	icon_serpent='x\xdae\x8f\xb1\x0e\x83 \x10\x86w\x9f\xe2\x92\x1blb\xf2\x07\x96\xeaH:0\xd6\
\xc1\x85\xd5\x98N5\xa5\xef?\xf5N\xd0\x8a\xdcA\xc2\xf7qw\x84\xdb\xfa\xb5\xcd\
\xd4\xda;\xc9\x1a\xc8\xb6\xcd<\xb5\xa0\x85\x1e\xeb\xbc\xbc7b!\xf6\xdeHl\x1c\
\x94\x073\xec<*\xf7\xbe\xf7\x99\x9d\xb21~\xe7.\xf5\x1f\x1c\xd3\xbdVlL\xc2\
\xcf\xf8ye\xd0\x00\x90\x0etH \x84\x80B\xaa\x8a\x88\x85\xc4(U\x9d$\xfeR;\xc5J\
\xa6\x01\xbbt9\xceR\xc8\x81e_$\x98\xb9\x9c\xa9\x8d,y\xa9t\xc8\xcf\x152\xe0x\
\xe9$\xf5\x07\x95\x0cD\x95t:\xb1\x92\xae\x9cI\xa8~\x84\x1f\xe0\xa3ec'

	def __init__(self, parent, id, title=_("Welcome to the")):
		wxDialog.__init__(self, parent, id, title)
		self.panel = LoginPanel(self, -1, isDialog=1)
		self.Fit () # needed for Windoze.
		self.Centre()

		# set window icon
		icon_bmp_data = wxBitmapFromXPMData(cPickle.loads(zlib.decompress(self.icon_serpent)))
		icon = wxEmptyIcon()
		icon.CopyFromBitmap(icon_bmp_data)
		self.SetIcon(icon)

#====================================================
class OptionWindow(wxDialog, LoginDialog):
	"""Advanced options window"""
	def __init__(self, parent, id=wxNewId(), title=_("Advanced login options"),loginparams=None):
		wxDialog.__init__(self, parent, id, title)
		self.panel = OptionPanel(self, -1, isDialog=1,loginparams=loginparams)
		self.Fit () # needed for Windoze.
		self.Centre()
		
		# set window icon
		icon_bmp_data = wxBitmapFromXPMData(cPickle.loads(zlib.decompress(self.icon_serpent)))
		icon = wxEmptyIcon()
		icon.CopyFromBitmap(icon_bmp_data)
		self.SetIcon(icon)

#====================================================
class OptionPanel(wxPanel):
	"""GUI panel class that gets interactively advanced login parameters

	# constructor parameters:
	#	loginparams: to override default login parameters 
	#	             see class "LoginParameters" in this module
	#	isDialog: if this panel is the main panel of a dialog, the panel will
	#	          resize the dialog automatically to display everything neatly
	#	          if isDialog is set to true
	"""
	def __init__(self, parent, id, pos = wxPyDefaultPosition, size = wxPyDefaultSize, style = wxTAB_TRAVERSAL,
		loginparams = None,
		isDialog = 0
	):

		wxPanel.__init__(self, parent, id, pos, size, style)
		self.parent = parent

		#true if dialog was cancelled by user
		self.cancelled = false

		#true if this panel is displayed within a dialog (will resize the dialog automatically then)
		self.isDialog = isDialog

		#login parameter settings should have been initialized by the parent window
		self.loginparams = loginparams

		self.topsizer = wxBoxSizer(wxVERTICAL)

		# FIXME: either no title as in "" or a title with i_18_n as in _("a title")
		# BUT NOT no title with i_18_n as in _("")
		self.paramsbox = wxStaticBox( self, -1, "")
		self.paramsboxsizer = wxStaticBoxSizer( self.paramsbox, wxVERTICAL )

		self.pboxgrid = wxFlexGridSizer( 4, 2, 5, 0 )
		self.pboxgrid.AddGrowableCol( 1 )

		#DATABASE COMBO
		label_db = wxStaticText( self, -1, _("database"), wxDefaultPosition, wxDefaultSize, 0 )
		self.pboxgrid.AddWindow( label_db, 0, wxALIGN_CENTER_VERTICAL|wxALL, 5 )
		self.dbcombo = wxComboBox( 
		    	self, 
			-1, 
			self.loginparams.databaselist[0],
			wxDefaultPosition,
			wxSize(100,-1),
			self.loginparams.databaselist ,
			wxCB_DROPDOWN )
		self.pboxgrid.AddWindow( self.dbcombo, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxALL, 5 )

		#HOST NAME / IP NUMBER COMBO
		label_host = wxStaticText( self, -1, _("host"), wxDefaultPosition, wxDefaultSize, 0 )
		self.pboxgrid.AddWindow( label_host, 0, wxALIGN_CENTER_VERTICAL|wxALL, 5 )
		self.hostcombo = wxComboBox( 
		    	self, 
			-1, 
			self.loginparams.hostlist[0], 
			wxDefaultPosition, wxSize(100,-1),
			self.loginparams.hostlist , 
			wxCB_DROPDOWN 
		)
		self.pboxgrid.AddWindow( self.hostcombo, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxALL, 5 )

		#PORT NUMBER COMBO
		label_port = wxStaticText( self, -1, _("port"), wxDefaultPosition, wxDefaultSize, 0 )
		self.pboxgrid.AddWindow( label_port, 0, wxALIGN_CENTER_VERTICAL|wxALL, 5 )
		self.portcombo = wxComboBox( 
		    	self, 
			-1, 
			self.loginparams.portlist[0], 
			wxDefaultPosition, 
			wxSize(100,-1),
			self.loginparams.portlist , 
			wxCB_DROPDOWN 
		)
		self.pboxgrid.AddWindow( self.portcombo, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxALL, 5 )

		#DATABASE BACKEND OPTIONS COMBO
		label_dboptions = wxStaticText( self, -1, _("backend options"), wxDefaultPosition, wxDefaultSize, 0 )
		self.pboxgrid.AddWindow( label_dboptions, 0, wxALIGN_CENTER_VERTICAL|wxALL, 5 )
		self.beoptioncombo= wxComboBox( 
		    	self, 
			-1, 
			self.loginparams.backendoptionlist[0], 
			wxDefaultPosition, 
			wxSize(100,-1),
			self.loginparams.backendoptionlist ,
			wxCB_DROPDOWN 
		)
		self.pboxgrid.AddWindow( self.beoptioncombo, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxALL, 5 )

		self.button_gridsizer = wxGridSizer(1,3,0,0)

		#---------------------
		# create options ok button
		#---------------------
		ID_BUTTON_OK = wxNewId()
		button_ok = wxButton( self, ID_BUTTON_OK, _("&Ok"), wxDefaultPosition, wxDefaultSize, 0 )
#		button_ok.SetDefault()
		#---------------------
		# create options help button
		#---------------------
		ID_BUTTON_HELP = wxNewId()
		button_help = wxButton( self, ID_BUTTON_HELP, _("&Help"), wxDefaultPosition, wxDefaultSize, 0 )
		#---------------------
		# create options cancel button
		#---------------------
		ID_BUTTON_CANCEL = wxNewId()
		button_cancel = wxButton( self, ID_BUTTON_CANCEL, _("&Cancel"), wxDefaultPosition, wxDefaultSize, 0 )

		#----------------------------
		#Add buttons to the gridsizer
		#----------------------------
		self.button_gridsizer.AddWindow( button_help, 0, wxALIGN_CENTRE|wxALL, 5 )
		self.button_gridsizer.AddWindow( button_ok, 0, wxALIGN_CENTRE|wxALL, 5 )
		self.button_gridsizer.AddWindow( button_cancel, 0, wxALIGN_CENTRE|wxALL, 5 )

    	    	# add all sub-sizers to the topsizer
		self.paramsboxsizer.AddSizer(self.pboxgrid, 1, wxGROW|wxALL, 10)
		self.topsizer.AddSizer(self.paramsboxsizer, 1, wxGROW|wxALL, 10)
		self.topsizer.AddSizer( self.button_gridsizer, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxALL, 5 )

		self.SetAutoLayout( true )
		self.SetSizer( self.topsizer)
		self.topsizer.Fit( self )
		if self.isDialog:
			self.topsizer.SetSizeHints( parent )

		EVT_BUTTON(self, ID_BUTTON_HELP, self.OnHelp)
		EVT_BUTTON(self, ID_BUTTON_OK, self.OnOK)
		EVT_BUTTON(self, ID_BUTTON_CANCEL, self.OnCancel)


#############################################################################
# GUI action functions from here on
#############################################################################

	def OnCancel(self, event):
		self.cancelled = true
		self.parent.Close()

	def OnHelp(self, event):
		wxMessageBox(_("\
Advanced backend options: \n\
\n\
Database: name of GnuMed database\n\
Host: name of database server\n\
Port: port number of database server\n\
Backend options: options passed through unparsed to the backend\n"))
		
	def OnOK(self, event):
		self.cancelled = false
		self.parent.Close()

#====================================================
# main
#----------------------------------------------------
if __name__ == '__main__':
	gb = gmGuiBroker.GuiBroker()	
	gb['gnumed_dir'] = os.curdir+'/..'

	app = wxPyWidgetTester(size = (300,400))
	#show the login panel in a main window
	app.SetWidget(LoginPanel, -1)
	#and pop the login dialog up modally
	dlg = LoginDialog(NULL, -1) #, png_bitmap = 'bitmaps/gnumedlogo.png')
	dlg.ShowModal()
	#demonstration how to access the login dialog values
	lp = dlg.panel.GetLoginParams()
	if lp is None:
		wxMessageBox(_("Dialog was cancelled by user"))
	else:
		wxMessageBox(_("You tried to log in as [%s] with password [%s].") % (lp.userlist[0], lp.password))
	dlg.Destroy()
	app.MainLoop()

#############################################################################
# $Log: gmLoginDialog.py,v $
# Revision 1.1  2003-10-23 06:02:39  sjtan
#
# manual edit areas modelled after r.terry's specs.
#
# Revision 1.40  2003/06/17 19:27:44  ncq
# - cleanup
# - only use cfg file login params if not empty list
#
# Revision 1.39  2003/05/17 17:30:36  ncq
# - just some cleanup
#
# Revision 1.38  2003/05/12 09:01:45  ncq
# - 1) type(tmp) is types.ListType implies tmp != None
# - 2) check for ListType, not StringType
#
# Revision 1.37  2003/05/10 18:48:09  hinnef
# - added stricter type checks when reading from cfg-file
#
# Revision 1.36  2003/04/05 00:37:46  ncq
# - renamed a few variables to reflect reality
#
# Revision 1.35  2003/03/31 00:18:34  ncq
# - or so I thought
#
# Revision 1.34  2003/03/31 00:17:43  ncq
# - started cleanup/clarification
# - made saving of values work again
#
# Revision 1.33  2003/02/09 18:55:47  ncq
# - make comment less angry
#
# Revision 1.32  2003/02/08 00:32:30  ncq
# - fixed failure to detect config file
#
# Revision 1.31  2003/02/08 00:15:17  ncq
# - cvs metadata keywords
#
# Revision 1.30  2003/02/07 21:06:02  sjtan
#
# refactored edit_area_gen_handler to handler_generator and handler_gen_editarea. New handler for gmSelectPerson
#
# Revision 1.29  2003/02/02 07:38:29  michaelb
# set serpent as window icon - login dialog & option dialog
#
# Revision 1.28  2003/01/16 09:22:28  ncq
# - changed default workplace name to "__default__" to play better with the database
#
# Revision 1.27  2003/01/07 10:22:52  ncq
# - fixed font definition
#
# Revision 1.26  2002/09/21 14:49:22  ncq
# - cleanup related to gmi18n
#
# Revision 1.25  2002/09/12 23:19:27  ncq
# - cleanup in preparation of cleansing
#
# Revision 1.24  2002/09/10 08:54:35  ncq
# - remember workplace name once loaded
#
# Revision 1.23  2002/09/09 01:05:16  ncq
# - fixed i18n glitch
# - added note that _("") is invalid !!
#
# @change log:
#	10.10.2001 hherb initial implementation, untested
#	24.10.2001 hherb comments added
#	24.10.2001 hherb LoginDialog class added,
#	24.10.2001 hherb persistent changes across multiple processes enabled
#	25.10.2001 hherb more flexible configuration options, more commenting
#	07.02.2002 hherb saved parameters now showing corectly in combo boxes
#   	05.09.2002 hberger moved options to own dialog
#       06.09.2002 rterry simplified gui
#                  -duplication and visual clutter removed
#                   removed duplication of information in display
#                   login gone from title bar , occurs once only now
#                   visually highlighted in dark blue
#                   login button title now 'ok' to conform to usual defaults of 
#                   ok, cancel in most operating systems
#                   reference to help removed (have help button for that)
#                   date removed - can't see use of this in login - clutters
#   	06.09.2002 hberger removed old code, fixed "login on close window" bug
#       07.09.2002 rterry removed duplicated heading in advanced login options
