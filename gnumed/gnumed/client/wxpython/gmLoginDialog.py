"""gmLoginDialog - This module provides a login dialog to GNUMed.

It features combo boxes which "remember" any number of
previously entered settings.

copyright: authors
"""
#============================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/Attic/gmLoginDialog.py,v $
# $Id: gmLoginDialog.py,v 1.64 2005-09-27 20:44:59 ncq Exp $
__version__ = "$Revision: 1.64 $"
__author__ = "H.Herb, H.Berger, R.Terry, K.Hilbert"
__license__ = 'GPL (details at http://www.gnu.org)'

import os.path, time, cPickle, zlib, types

try:
	import wxversion
	import wx
except ImportError:
	from wxPython import wx

from Gnumed.pycommon import gmLoginInfo, gmGuiBroker, gmCfg, gmLog, gmWhoAmI, gmI18N, gmNull
from Gnumed.wxpython import gmGuiHelpers

_log = gmLog.gmDefLog
_log.Log(gmLog.lData, __version__)
_cfg = gmCfg.gmDefCfgFile
_whoami = gmWhoAmI.cWhoAmI()

#====================================================
class cLoginParamChoices:
	"""dummy class, structure for login parameters"""
	def __init__(self):
		"""init parmeters with reasonable defaults"""
		self.userlist = ['any-doc']
		self.password = ''
		self.profilelist = [_('default fallback: public GNUmed database')]
		self.profiles = {
			_('default fallback: public GNUmed database'): {'host': 'salaam.homeunix.com', 'port': 5432, 'database': 'gnumed_v1'}
		}

#====================================================
class LoginPanel(wx.Panel):
	"""GUI panel class that interactively gets Postgres login parameters"""

	def __init__(self, parent, id,
		pos = wx.DefaultPosition,
		size = wx.DefaultSize,
		style = wx.TAB_TRAVERSAL,
		loginparams = None,
		isDialog = 0
		):
		"""Create login panel.

		loginparams:	to override default login parameters and configuration file.
						see class "LoginParameters" in this module
		isDialog:	if this panel is the main panel of a dialog, the panel will
					resize the dialog automatically to display everything neatly
					if isDialog is set to True
		"""
		wx.Panel.__init__(self, parent, id, pos, size, style)
		self.parent = parent

		self.gb = gmGuiBroker.GuiBroker()

		#True if dialog was cancelled by user 
		#if the dialog is closed manually, login should be cancelled
		self.cancelled = True

		# True if this panel is displayed within a dialog (will resize the dialog automatically then)
		self.isDialog = isDialog

		# if no login params supplied get default ones or from config file
		if loginparams is None:
			self.__load_login_param_choices()
		else:
			self.loginparams = loginparams

		self.topsizer = wx.BoxSizer(wx.VERTICAL)

		bitmap = os.path.join (self.gb['gnumed_dir'], 'bitmaps', 'gnumedlogo.png')
		try:
			wx.Image_AddHandler(wx.PNGHandler())
			png = wx.Image(bitmap, wx.BITMAP_TYPE_PNG).ConvertToBitmap()
			bmp = wx.StaticBitmap(self, -1, png, wx.Point(10, 10), wx.Size(png.GetWidth(), png.GetHeight()))
			self.topsizer.Add(bmp, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 10)
		except:
			self.topsizer.Add(wx.StaticText (self, -1, _("Cannot find image") + bitmap, style=wx.ALIGN_CENTRE), 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 10)

		if self.gb.has_key('main.slave_mode') and self.gb['main.slave_mode']:
			paramsbox_caption = _("Slave Login - %s" % _whoami.get_workplace())
		else:
			paramsbox_caption = _("Login - %s" % _whoami.get_workplace())

		# FIXME: why doesn't this align in the centre ?
		self.paramsbox = wx.StaticBox( self, -1, paramsbox_caption, style = wx.ALIGN_CENTRE_HORIZONTAL)
		self.paramsboxsizer = wx.StaticBoxSizer( self.paramsbox, wx.VERTICAL )
		self.paramsbox.SetForegroundColour(wx.Colour(35, 35, 142))
		# FIXME: can we get around this ugly IFDEF ?
		if wx.Platform == '__WXMAC__':
			# on wxMac there seems to be no faceName option so don't use it
			self.paramsbox.SetFont(wx.Font(
				pointSize = 12,
				family = wx.SWISS,
				style = wx.NORMAL,
				weight = wx.BOLD,
				underline = False
			))
		else:
			self.paramsbox.SetFont(wx.Font(
				pointSize = 12,
				family = wx.SWISS,
				style = wx.NORMAL,
				weight = wx.BOLD,
				underline = False,
				faceName = ''
			))
		self.pboxgrid = wx.FlexGridSizer( 4, 2, 5, 5 )
		self.pboxgrid.AddGrowableCol( 1 )

		# PROFILE COMBO
		label = wx.StaticText( self, -1, _("Profile"), wx.DefaultPosition, wx.DefaultSize, 0 )
		label.SetForegroundColour(wx.Colour(35, 35, 142))
		self.pboxgrid.Add(label, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
		self.profilecombo = wx.ComboBox(
			self,
			-1,
			self.loginparams.profilelist[0],
			wx.DefaultPosition,
			wx.Size(150,-1),
			self.loginparams.profilelist,
			wx.CB_READONLY
		)
		self.pboxgrid.Add (self.profilecombo, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

		# USER NAME COMBO
		label = wx.StaticText( self, -1, _("Username"), wx.DefaultPosition, wx.DefaultSize, 0 )
		label.SetForegroundColour(wx.Colour(35, 35, 142))
		self.pboxgrid.Add( label, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
		self.usercombo = wx.ComboBox(
			self,
			-1,
			self.loginparams.userlist[0],
			wx.DefaultPosition,
			wx.Size(150,-1),
			self.loginparams.userlist,
			wx.CB_DROPDOWN
		)
		self.pboxgrid.Add( self.usercombo, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

		#PASSWORD TEXT ENTRY
		label = wx.StaticText( self, -1, _("Password"), wx.DefaultPosition, wx.DefaultSize, 0 )
		label.SetForegroundColour(wx.Colour(35, 35, 142))
		self.pboxgrid.Add( label, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
		self.pwdentry = wx.TextCtrl( self, 1, '', wx.DefaultPosition, wx.Size(80,-1), wx.TE_PASSWORD )
		# set focus on password entry
		self.pwdentry.SetFocus()
		self.pboxgrid.Add( self.pwdentry, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
		
		
		#----------------------------------------------------------------------
		#new button code inserted rterry 06Sept02
		#button order re-arraged to make it consistant with usual dialog format
		#in most operating systems ie  btns ok and cancel are standard and 
		#in that order
		#ie Order is now help, ok and cancel
		#The order of creation is the tab order
		#login-ok button automatically is the default when tabbing (or <enter>)
		#from password
		#this eliminates the heavy border when you use the default 
		#?is the default word needed for any other reason?
		#----------------------------------------------------------------------
		self.button_gridsizer = wx.GridSizer(1,3,0,0)
		#---------------------
		#3:create login ok button
		#---------------------
		ID_BUTTON_LOGIN = wx.NewId()
		button_login_ok = wx.Button(self, ID_BUTTON_LOGIN, _("&Ok"), wx.DefaultPosition, wx.DefaultSize, 0 )
		button_login_ok.SetToolTip(wx.ToolTip(_("Proceed with login.")) )
		button_login_ok.SetDefault()

		#---------------------
		#3:create cancel button
		#---------------------
		ID_BUTTON_CANCEL = wx.NewId()
		button_cancel = wx.Button(self, ID_BUTTON_CANCEL, _("&Cancel"), wx.DefaultPosition, wx.DefaultSize, 0 )
		button_cancel.SetToolTip(wx.ToolTip(_("Cancel Login.")) )
		#---------------------
		#2:create Help button
		#---------------------
		ID_BUTTON_HELP = wx.NewId()
		button_help = wx.Button(self, ID_BUTTON_HELP, _("&Help"), wx.DefaultPosition, wx.DefaultSize, 0 )
		button_help.SetToolTip(wx.ToolTip(_("Help for login screen")) )
		#----------------------------
		#Add buttons to the gridsizer
		#----------------------------
		self.button_gridsizer.Add (button_help,0,wx.EXPAND|wx.ALL,5)
		self.button_gridsizer.Add (button_login_ok,0,wx.EXPAND|wx.ALL,5)
		self.button_gridsizer.Add (button_cancel,0,wx.EXPAND|wx.ALL,5)
		
		self.paramsboxsizer.Add(self.pboxgrid, 1, wx.GROW|wx.ALL, 10)
		self.topsizer.Add(self.paramsboxsizer, 1, wx.GROW|wx.ALL, 10)
		self.topsizer.Add( self.button_gridsizer, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

		self.SetAutoLayout(True)
		self.SetSizer( self.topsizer)
		self.topsizer.Fit( self )
		if self.isDialog:
			self.topsizer.SetSizeHints(parent)

		wx.EVT_BUTTON(self, ID_BUTTON_HELP, self.OnHelp)
		wx.EVT_BUTTON(self, ID_BUTTON_LOGIN, self.OnLogin)
		wx.EVT_BUTTON(self, ID_BUTTON_CANCEL, self.OnCancel)

	#----------------------------
	# internal helper methods
	#----------------------------
	def __load_login_param_choices(self):
		"""Load parameter settings from standard configuration file"""
		# initialize login parameters
		self.loginparams = cLoginParamChoices()

		# check if there is a non-empty config file
		if isinstance(_cfg, gmNull.cNull):
			# this will probably never happen as gmCfg creates a
			# default config-file when none was found, nevertheless
			# fall back to default values
			msg = _(
				"Cannot find the configuration file:\n\n"
				"%s"
				"Your setup procedure may not have completed or your\n"
				"configuration file may be damaged.\n\n"
				"You can find an example configuration file included with\n"
				"the GNUmed documentation which you may use to fix things.\n\n"
				"Falling back to default profile using public server."
			) % _cfg.cfgName
			gmGuiHelpers.gm_show_error(msg, _('Configuration Error'), gmLog.lErr)
			return self.loginparams

		# read login options from config file
		# - database account names
		tmp = _cfg.get('backend', 'logins')
		if type(tmp) is types.ListType and len(tmp) > 0:
			self.loginparams.userlist = tmp
		else:
			_log.Log(gmLog.lWarn, 'malformed/missing "logins" list in config file, using defaults')

		# - profile names
		tmp = _cfg.get('backend', 'profiles')
		if type(tmp) is types.ListType and len(tmp) > 0:
			self.loginparams.profilelist = tmp
		else:
			_log.Log(gmLog.lErr, 'malformed/missing "profiles" list in config file, using defaults')
			# fall back to default values
			msg = _(
				"Cannot find server profiles in the configuration file.\n"
				"Your setup procedure may not have completed or your\n"
				"configuration file may be damaged.\n\n"
				"You can find an example configuration file included with\n"
				"the GNUmed documentation which you may use to fix\n"
				"[%s].\n\n"
				"Falling back to default profile using public server."
			) % _cfg.cfgName
			gmGuiHelpers.gm_show_error(msg, _('Configuration Error'), gmLog.lErr)
			_log.Log(gmLog.lData, str(tmp))
			return self.loginparams

		# - details for each profile
		for profile in self.loginparams.profilelist:
			database = None
			host = None
			port = None

			# profile sections are denoted by leading "profile "
			profile_label = "profile %s" % profile
			if profile_label not in _cfg.getGroups():
				_log.Log(gmLog.lWarn, _("section [%s] not found in config file") % profile_label)
				del self.loginparams.profilelist[self.loginparams.profilelist.index(profile)]
				continue
			# database name, errors will show up visually and in failing connections
			database = str(_cfg.get(profile_label, 'database'))
			# host
			host = str(_cfg.get(profile_label, 'host'))
			# port
			tmp = _cfg.get(profile_label, 'port')
			try:
				port = int(tmp)
				if port < 1024:
					raise ValueError
			except TypeError, ValueError:
				_log.Log(gmLog.lWarn, _("port definition [%s] invalid in profile [%s]") % (str(tmp), profile_label))
				del self.loginparams.profilelist[self.loginparams.profilelist.index(profile)]
				continue
			# set profile details
			self.loginparams.profiles[profile] = {
				'host': host,
				'database': database,
				'port': port
			}

		# any profiles left ?
		if self.loginparams.profilelist == []:
			_log.Log(gmLog.lErr, 'no valid profile information in config file, using builtin defaults')
			# fallback to default, ignores all login information in the config file
			self.loginparams = cLoginParamChoices()
			msg = _(
				"No valid profile information found in configuration file.\n\n"
				"Please refer to the example configuration file (included\n"
				"with the GNUmed documentation) for information on how\n"
				"profiles are to be specified.\n\n"
				"Falling back to default profile using local server."
			)
			gmGuiHelpers.gm_show_error(msg, _('Configuration Error'), gmLog.lErr)

		return self.loginparams
	#----------------------------
	def save_settings(self):
		"""Save parameter settings to standard configuration file"""

		_cfg.set('backend', 'logins', self.__cbox_to_list(self.usercombo))
		_cfg.set('backend', 'profiles', self.__cbox_to_list(self.profilecombo))

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

	def GetLoginInfo(self):
		"""convenience function for compatibility with gmLoginInfo.LoginInfo"""
		if not self.cancelled:			
			login = gmLoginInfo.LoginInfo(user=self.GetUser(), passwd=self.GetPassword(), host=self.GetHost())
			login.SetDatabase(self.GetDatabase())
			login.SetPort(self.GetPort())
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
		return self.loginparams.profiles[self.GetProfile()]['database']

	def GetHost(self):
		return self.loginparams.profiles[self.GetProfile()]['host']

	def GetPort(self):
		return self.loginparams.profiles[self.GetProfile()]['port']

	def GetProfile(self):
		return self.loginparams.profilelist[0]
		
	#----------------------------
	# event handlers
	#----------------------------
	def OnHelp(self, event):
		tmp = _cfg.get('workplace', 'help desk')
		if tmp is None:
			print _("You need to set the option [workplace] -> <help desk> in the config file !")
			tmp = "http://www.gnumed.org"

		wx.MessageBox(_(
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
	def OnLogin(self, event):
		self.loginparams.profilelist=self.__cbox_to_list(self.profilecombo)
		self.loginparams.userlist = self.__cbox_to_list(self.usercombo)
		self.loginparams.password = self.GetPassword()
		self.cancelled = False
		self.parent.Close()
	#----------------------------
	def OnCancel(self, event):
		self.cancelled = True
		self.parent.Close()

#====================================================
class LoginDialog(wx.Dialog):
	"""LoginDialog - window holding LoginPanel"""

	icon_serpent='x\xdae\x8f\xb1\x0e\x83 \x10\x86w\x9f\xe2\x92\x1blb\xf2\x07\x96\xeaH:0\xd6\
\xc1\x85\xd5\x98N5\xa5\xef?\xf5N\xd0\x8a\xdcA\xc2\xf7qw\x84\xdb\xfa\xb5\xcd\
\xd4\xda;\xc9\x1a\xc8\xb6\xcd<\xb5\xa0\x85\x1e\xeb\xbc\xbc7b!\xf6\xdeHl\x1c\
\x94\x073\xec<*\xf7\xbe\xf7\x99\x9d\xb21~\xe7.\xf5\x1f\x1c\xd3\xbdVlL\xc2\
\xcf\xf8ye\xd0\x00\x90\x0etH \x84\x80B\xaa\x8a\x88\x85\xc4(U\x9d$\xfeR;\xc5J\
\xa6\x01\xbbt9\xceR\xc8\x81e_$\x98\xb9\x9c\xa9\x8d,y\xa9t\xc8\xcf\x152\xe0x\
\xe9$\xf5\x07\x95\x0cD\x95t:\xb1\x92\xae\x9cI\xa8~\x84\x1f\xe0\xa3ec'

	def __init__(self, parent, id, title=_("Welcome to the")):
		wx.Dialog.__init__(self, parent, id, title)
		self.panel = LoginPanel(self, -1, isDialog=1)
		self.Fit () # needed for Windoze.
		self.Centre()

		# set window icon
		icon_bmp_data = wx.BitmapFromXPMData(cPickle.loads(zlib.decompress(self.icon_serpent)))
		icon = wx.EmptyIcon()
		icon.CopyFromBitmap(icon_bmp_data)
		self.SetIcon(icon)



#====================================================
# main
#----------------------------------------------------
if __name__ == '__main__':
	gb = gmGuiBroker.GuiBroker()	
	gb['gnumed_dir'] = os.curdir+'/..'

	app = wx.PyWidgetTester(size = (300,400))
	#show the login panel in a main window
#	app.SetWidget(LoginPanel, -1)
	#and pop the login dialog up modally
	dlg = LoginDialog(None, -1) #, png_bitmap = 'bitmaps/gnumedlogo.png')
	dlg.ShowModal()
	#demonstration how to access the login dialog values
	lp = dlg.panel.GetLoginInfo()
	if lp is None:
		wx.MessageBox(_("Dialog was cancelled by user"))
	else:
		wx.MessageBox(_("You tried to log in as [%s] with password [%s].\nHost:%s, DB: %s, Port: %s") % (lp.GetUser(),lp.GetPassword(),lp.GetHost(),lp.GetDatabase(),lp.GetPort()))
	dlg.Destroy()
#	app.MainLoop()


#############################################################################
# $Log: gmLoginDialog.py,v $
# Revision 1.64  2005-09-27 20:44:59  ncq
# - wx.wx* -> wx.*
#
# Revision 1.63  2005/09/26 18:01:51  ncq
# - use proper way to import wx26 vs wx2.4
# - note: THIS WILL BREAK RUNNING THE CLIENT IN SOME PLACES
# - time for fixup
#
# Revision 1.62  2005/09/24 09:17:29  ncq
# - some wx2.6 compatibility fixes
#
# Revision 1.61  2005/08/15 15:15:25  ncq
# - improved error message
#
# Revision 1.60  2005/08/14 15:22:04  ncq
# - need to import gmNull
#
# Revision 1.59  2005/08/14 14:31:53  ncq
# - better handling of missing/malformed config file
#
# Revision 1.58  2005/06/10 16:09:36  shilbert
# foo.AddSizer()-> foo.Add() such that wx2.5 works
#
# Revision 1.57  2005/03/06 14:54:19  ncq
# - szr.AddWindow() -> Add() such that wx2.5 works
# - 'demographic record' -> get_identity()
#
# Revision 1.56  2005/01/22 22:26:06  ncq
# - a bunch of cleanups
# - i18n
#
# Revision 1.55  2005/01/20 21:37:40  hinnef
# - added error dialog when no profiles specified
#
# Revision 1.54  2004/11/24 21:16:33  hinnef
# - fixed issue with missing profiles when writing to empty gnumed.conf. This lead to a crash when trying to load the invalid gnumed.conf. Now we just ignore this and fall back to defaults.
#
# Revision 1.53  2004/11/22 19:32:36  hinnef
# new login dialog with profiles
#
# Revision 1.52  2004/09/13 08:57:33  ncq
# - losts of cleanup
# - opt/tty not used in DSN anymore
# - --slave -> gb['main.slave_mode']
#
# Revision 1.51  2004/07/18 20:30:54  ncq
# - wxPython.true/false -> Python.True/False as Python tells us to do
#
# Revision 1.50  2004/07/18 18:44:27  ncq
# - use Python True, not wxPython true
#
# Revision 1.49  2004/06/20 16:01:05  ncq
# - please epydoc more carefully
#
# Revision 1.48  2004/06/20 06:49:21  ihaywood
# changes required due to Epydoc's OCD
#
# Revision 1.47  2004/05/28 13:06:41  ncq
# - improve faceName/Mac OSX fix
#
# Revision 1.46  2004/05/28 09:09:34  shilbert
# - remove faceName option from wxFont on wxMac or else no go
#
# Revision 1.45  2004/05/26 20:35:23  ncq
# - don't inherit from LoginDialog in OptionWindow, it barks on MacOSX
#
# Revision 1.44  2004/04/24 12:46:35  ncq
# - logininfo() needs host=
#
# Revision 1.43  2004/03/04 19:47:06  ncq
# - switch to package based import: from Gnumed.foo import bar
#
# Revision 1.42  2003/12/29 16:58:52  uid66147
# - use whoami
#
# Revision 1.41  2003/11/17 10:56:38  sjtan
#
# synced and commiting.
#
# Revision 1.1  2003/10/23 06:02:39  sjtan
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
