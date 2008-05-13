"""GNUmed authentication widgets.

This module contains widgets and GUI
functions for authenticating users.
"""
#================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmAuthWidgets.py,v $
# $Id: gmAuthWidgets.py,v 1.20 2008-05-13 14:10:35 ncq Exp $
__version__ = "$Revision: 1.20 $"
__author__ = "karsten.hilbert@gmx.net, H.Herb, H.Berger, R.Terry"
__license__ = "GPL (details at http://www.gnu.org)"


# stdlib
import sys, os.path, cPickle, zlib, logging


# 3rd party
import wx


# GNUmed
if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmLoginInfo, gmPG2, gmBackendListener, gmTools, gmCfg2, gmI18N
from Gnumed.business import gmSurgery
from Gnumed.wxpython import gmGuiHelpers, gmExceptionHandlingWidgets


_log = logging.getLogger('gm.ui')
_log.info(__version__)
_cfg = gmCfg2.gmCfgData()

try:
	_('do-not-translate-but-make-epydoc-happy')
except NameError:
	_ = lambda x:x

msg_generic = _("""
GNUmed database version mismatch.

This database version cannot be used with this client:

 client version: %s
 database version detected: %s
 database version needed: %s

Currently connected to database:

 host: %s
 database: %s
 user: %s
""")

msg_time_skew_fail = _("""\
The server and client clocks are off
by more than %s minutes !

You must fix the time settings before
you can use this database with this
client.

You may have to contact your
administrator for help.""")

msg_time_skew_warn = _("""\
The server and client clocks are off
by more than %s minutes !

You should fix the time settings.
Otherwise clinical data may appear to
have been entered at the wrong time.

You may have to contact your
administrator for help.""")

msg_insanity = _("""
There is a serious problem with the database settings:

%s

You may have to contact your administrator for help.""")

msg_fail = _("""
You must connect to a different database in order
to use the GNUmed client. You may have to contact
your administrator for help.""")

msg_override = _("""
The client will, however, continue to start up because
you are running a development/test version of GNUmed.

There may be schema related errors. Please report and/or
fix them. Do not rely on this database to work properly
in all cases !""")

current_db_name = 'gnumed_v9'
#================================================================
# convenience functions
#----------------------------------------------------------------
def connect_to_database(max_attempts=3, expected_version=None, require_version=True, client_version=u'*** unknown ***'):
	"""Display the login dialog and try to log into the backend.

	- up to max_attempts times
	- returns True/False
	"""
	# force programmer to set a valid expected_version
	expected_hash = gmPG2.known_schema_hashes[expected_version]

	attempt = 0

	dlg = cLoginDialog(None, -1, client_version = client_version)
	dlg.Centre(wx.BOTH)

	while attempt < max_attempts:

		connected = False

		dlg.ShowModal()
		login = dlg.panel.GetLoginInfo()
		if login is None:
			_log.info("user cancelled login dialog")
			break

		# try getting a connection to verify the DSN works
		dsn = gmPG2.make_psycopg2_dsn (
			database = login.database,
			host = login.host,
			port = login.port,
			user = login.user,
			password = login.password
		)
		try:
			conn = gmPG2.get_raw_connection(dsn = dsn, verbose = True, readonly = True)
			connected = True
		except gmPG2.cAuthenticationError, e:
			attempt += 1
			_log.error(u"login attempt %s/%s failed: %s", attempt, max_attempts, e)
			_log.debug(u'retrying')
			if attempt < max_attempts:
				gmGuiHelpers.gm_show_error (_(
						"Unable to connect to database:\n\n"
						"%s\n\n"
						"Please retry or cancel !"
					) % e,
					_('Connecting to backend')
				)
			continue
		except gmPG2.dbapi.OperationalError, e:
			_log.error(u"login attempt %s/%s failed", attempt+1, max_attempts)
			_log.debug('useless to retry')
#			gmLog2.log_stack_trace()
#			break
			raise

		# connect was successful:
		gmPG2.set_default_login(login = login)
		gmPG2.set_default_client_encoding(encoding = dlg.panel.backend_profile.encoding)

		compatible = gmPG2.database_schema_compatible(version = expected_version)
		if compatible or not require_version:
			dlg.panel.save_state()

		if not compatible:
			connected_db_version = gmPG2.get_schema_version()
			msg = msg_generic % (client_version, connected_db_version, expected_version, login.host, login.database, login.user)
			if require_version:
				gmGuiHelpers.gm_show_error(msg + msg_fail, _('Verifying database version'))
				continue
			gmGuiHelpers.gm_show_info(msg + msg_override, _('Verifying database version'))

		# FIXME: make configurable
		max_skew = 1		# minutes
		if _cfg.get(option = 'debug'):
			max_skew = 10
		if not gmPG2.sanity_check_time_skew(tolerance = (max_skew * 60)):
			if _cfg.get(option = 'debug'):
				gmGuiHelpers.gm_show_warning(msg_time_skew_warn % max_skew, _('Verifying database settings'))
			else:
				gmGuiHelpers.gm_show_error(msg_time_skew_fail % max_skew, _('Verifying database settings'))
				continue

		sanity_level, message = gmPG2.sanity_check_database_settings()
		if sanity_level != 0:
			gmGuiHelpers.gm_show_error((msg_insanity % message), _('Verifying database settings'))
			if sanity_level == 2:
				continue

		gmExceptionHandlingWidgets.set_is_public_database(login.public_db)
		gmExceptionHandlingWidgets.set_database_helpdesk(login.helpdesk)

		listener = gmBackendListener.gmBackendListener(conn=conn)
		break

	dlg.Destroy()

	return connected
#================================================================
def get_dbowner_connection(procedure=None, dbo_password=None):
	if procedure is None:
		procedure = _('<restricted procedure>')

	# 1) get password for gm-dbo
	if dbo_password is None:
		pwd_gm_dbo = wx.GetPasswordFromUser (
			message = _("""
 [%s]

This is a restricted procedure. We need the
password for the GNUmed database owner.

Please enter the password for <gm-dbo>:""") % procedure,
			caption = procedure
		)
		if pwd_gm_dbo == '':
			return None
	else:
		pwd_gm_dbo = dbo_password

	# 2) connect as gm-dbo
	login = gmPG2.get_default_login()
	dsn = gmPG2.make_psycopg2_dsn(database=login.database, host=login.host, port=login.port, user='gm-dbo', password=pwd_gm_dbo)
	try:
		conn = gmPG2.get_connection(dsn=dsn, readonly=False, verbose=True, pooled=False)
	except:
		_log.exception('cannot connect')
		gmGuiHelpers.gm_show_error (
			aMessage = _('Cannot connect as the GNUmed database owner <gm-dbo>.'),
			aTitle = procedure
		)
		return None

	return conn
#================================================================
class cBackendProfile:
	pass
#================================================================
class cLoginDialog(wx.Dialog):
	"""cLoginDialog - window holding cLoginPanel"""

	icon_serpent='x\xdae\x8f\xb1\x0e\x83 \x10\x86w\x9f\xe2\x92\x1blb\xf2\x07\x96\xeaH:0\xd6\
\xc1\x85\xd5\x98N5\xa5\xef?\xf5N\xd0\x8a\xdcA\xc2\xf7qw\x84\xdb\xfa\xb5\xcd\
\xd4\xda;\xc9\x1a\xc8\xb6\xcd<\xb5\xa0\x85\x1e\xeb\xbc\xbc7b!\xf6\xdeHl\x1c\
\x94\x073\xec<*\xf7\xbe\xf7\x99\x9d\xb21~\xe7.\xf5\x1f\x1c\xd3\xbdVlL\xc2\
\xcf\xf8ye\xd0\x00\x90\x0etH \x84\x80B\xaa\x8a\x88\x85\xc4(U\x9d$\xfeR;\xc5J\
\xa6\x01\xbbt9\xceR\xc8\x81e_$\x98\xb9\x9c\xa9\x8d,y\xa9t\xc8\xcf\x152\xe0x\
\xe9$\xf5\x07\x95\x0cD\x95t:\xb1\x92\xae\x9cI\xa8~\x84\x1f\xe0\xa3ec'

	def __init__(self, parent, id, title=_("Welcome to the"), client_version=u'*** unknown ***'):
		wx.Dialog.__init__(self, parent, id, title)
		self.panel = cLoginPanel(self, -1, isDialog=1, client_version = client_version)
		self.Fit() # needed for Windoze.
		self.Centre()

		# set window icon
		icon_bmp_data = wx.BitmapFromXPMData(cPickle.loads(zlib.decompress(self.icon_serpent)))
		icon = wx.EmptyIcon()
		icon.CopyFromBitmap(icon_bmp_data)
		self.SetIcon(icon)
#================================================================
class cLoginPanel(wx.Panel):
	"""GUI panel class that interactively gets Postgres login parameters.

		It features combo boxes which "remember" any number of
		previously entered settings.
	"""
	def __init__(self, parent, id,
					pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.TAB_TRAVERSAL,
					isDialog = 0, client_version = u'*** unknown ***'):
		"""Create login panel.

		isDialog:	if this panel is the main panel of a dialog, the panel will
					resize the dialog automatically to display everything neatly
					if isDialog is set to True
		"""
		wx.Panel.__init__(self, parent, id, pos, size, style)
		self.parent = parent

		#True if dialog was cancelled by user 
		#if the dialog is closed manually, login should be cancelled
		self.cancelled = True

		# True if this panel is displayed within a dialog (will resize the dialog automatically then)
		self.isDialog = isDialog

		self.topsizer = wx.BoxSizer(wx.VERTICAL)

		# find bitmap
		paths = gmTools.gmPaths()
		bitmap = os.path.join(paths.system_app_data_dir, 'bitmaps', 'gnumedlogo.png')
		try:
			png = wx.Image(bitmap, wx.BITMAP_TYPE_PNG).ConvertToBitmap()
			bmp = wx.StaticBitmap(self, -1, png, wx.Point(10, 10), wx.Size(png.GetWidth(), png.GetHeight()))
			self.topsizer.Add (
				bmp,
				proportion = 0,
				flag = wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL,
				border = 10
			)
		except:
			self.topsizer.Add (
				wx.StaticText (
					self,
					-1,
					label = _("Cannot find image") + bitmap,
					style = wx.ALIGN_CENTRE
				),
				proportion = 0,
				flag = wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL,
				border = 10
			)

		paramsbox_caption = _('"%s" (version %s)') % (gmSurgery.gmCurrentPractice().active_workplace, client_version)

		# FIXME: why doesn't this align in the centre ?
		self.paramsbox = wx.StaticBox( self, -1, paramsbox_caption, style = wx.ALIGN_CENTRE_HORIZONTAL)
		self.paramsboxsizer = wx.StaticBoxSizer( self.paramsbox, wx.VERTICAL )
		self.paramsbox.SetForegroundColour(wx.Colour(35, 35, 142))
		self.paramsbox.SetFont(wx.Font(
			pointSize = 12,
			family = wx.SWISS,
			style = wx.NORMAL,
			weight = wx.BOLD,
			underline = False
		))
		self.pboxgrid = wx.FlexGridSizer(5, 2, 5, 5)
		self.pboxgrid.AddGrowableCol(1)

		# PROFILE COMBO
		label = wx.StaticText( self, -1, _('Backend'), wx.DefaultPosition, wx.DefaultSize, 0)
		label.SetForegroundColour(wx.Colour(35, 35, 142))
		self.pboxgrid.Add(label, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
		self.__backend_profiles = self.__get_backend_profiles()
		self._CBOX_profile = wx.ComboBox (
			self,
			-1,
			self.__backend_profiles.keys()[0],
			wx.DefaultPosition,
			size = wx.Size(150,-1),
			choices = self.__backend_profiles.keys(),
			style = wx.CB_READONLY
		)
		self.pboxgrid.Add (self._CBOX_profile, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

		# USER NAME COMBO
		label = wx.StaticText( self, -1, _("Username"), wx.DefaultPosition, wx.DefaultSize, 0 )
		label.SetForegroundColour(wx.Colour(35, 35, 142))
		self.pboxgrid.Add(label, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
		self.__previously_used_accounts = self.__get_previously_used_accounts()
		self._CBOX_user = wx.ComboBox (
			self,
			-1,
			self.__previously_used_accounts[0],
			wx.DefaultPosition,
			wx.Size(150,-1),
			self.__previously_used_accounts,
			wx.CB_DROPDOWN
		)
		self.pboxgrid.Add( self._CBOX_user, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

		#PASSWORD TEXT ENTRY
		label = wx.StaticText( self, -1, _("Password"), wx.DefaultPosition, wx.DefaultSize, 0 )
		label.SetForegroundColour(wx.Colour(35, 35, 142))
		self.pboxgrid.Add( label, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
		self.pwdentry = wx.TextCtrl( self, 1, '', wx.DefaultPosition, wx.Size(80,-1), wx.TE_PASSWORD )
		# set focus on password entry
		self.pwdentry.SetFocus()
		self.pboxgrid.Add( self.pwdentry, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

		# --debug checkbox
		label = wx.StaticText(self, -1, _('Options'), wx.DefaultPosition, wx.DefaultSize, 0)
		label.SetForegroundColour(wx.Colour(35, 35, 142))
		self.pboxgrid.Add(label, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
		self._CHBOX_debug = wx.CheckBox(self, -1, _('debug mode'))
		self._CHBOX_debug.SetToolTipString(_('Check this to run GNUmed client in debugging mode.'))
		self.pboxgrid.Add(self._CHBOX_debug, 0, wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

		# --slave checkbox
		label = wx.StaticText(self, -1, '', wx.DefaultPosition, wx.DefaultSize, 0)
		label.SetForegroundColour(wx.Colour(35, 35, 142))
		self.pboxgrid.Add(label, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
		self._CHBOX_slave = wx.CheckBox(self, -1, _('enable remote control'))
		self._CHBOX_slave.SetToolTipString(_('Check this to run GNUmed client in slave mode for remote control.'))
		self.pboxgrid.Add(self._CHBOX_slave, 0, wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

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
		button_help.SetToolTip(wx.ToolTip(_("Help for login screen")))
		#----------------------------
		#Add buttons to the gridsizer
		#----------------------------
		self.button_gridsizer.Add (button_help,0,wx.EXPAND|wx.ALL,5)
		self.button_gridsizer.Add (button_login_ok,0,wx.EXPAND|wx.ALL,5)
		self.button_gridsizer.Add (button_cancel,0,wx.EXPAND|wx.ALL,5)
		
		self.paramsboxsizer.Add(self.pboxgrid, 1, wx.GROW|wx.ALL, 10)
		self.topsizer.Add(self.paramsboxsizer, 1, wx.GROW|wx.ALL, 10)
		self.topsizer.Add( self.button_gridsizer, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

		self.__load_state()

		self.SetAutoLayout(True)
		self.SetSizer( self.topsizer)
		self.topsizer.Fit( self )
		if self.isDialog:
			self.topsizer.SetSizeHints(parent)

		wx.EVT_BUTTON(self, ID_BUTTON_HELP, self.OnHelp)
		wx.EVT_BUTTON(self, ID_BUTTON_LOGIN, self.__on_login_button_pressed)
		wx.EVT_BUTTON(self, ID_BUTTON_CANCEL, self.OnCancel)

	#----------------------------------------------------------
	# internal helper methods
	#----------------------------------------------------------
	def __get_previously_used_accounts(self):

		accounts = gmTools.coalesce (
			_cfg.get (
				group = u'backend',
				option = u'logins',
				source_order = [
					(u'explicit', u'return'),
					(u'user', u'append'),
					(u'workbase', u'append')
				]
			),
			[]
		)

		return accounts
	#----------------------------------------------------
	def __get_backend_profiles(self):
		"""Get server profiles from the configuration files.

		1) from system-wide file
		2) from user file

		Profiles in the user file which have the same name
		as a profile in the system file will override the
		system file.
		"""
		src_order = [
			(u'explicit', u'return'),
			(u'system', u'append'),
			(u'user', u'append'),
			(u'workbase', u'append')
		]

		profile_names = gmTools.coalesce (
			_cfg.get(group = u'backend', option = u'profiles', source_order = src_order),
			[]
		)

		profiles = {}

		for profile_name in profile_names:
			# FIXME: once the profile has been found always use the corresponding source !
			profile = cBackendProfile()
			profile.name = profile_name
			profile_section = 'profile %s' % profile_name
			profile.host = gmTools.coalesce(_cfg.get(profile_section, u'host', src_order), u'').strip()
			port = gmTools.coalesce(_cfg.get(profile_section, u'port', src_order), 5432)
			try:
				profile.port = int(port)
				if profile.port < 1024:
					raise ValueError('refusing to use priviledged port (< 1024)')
			except ValueError:
				_log.warning('invalid port definition: [%s], skipping profile [%s]', port, profile_name)
				continue
			profile.database = gmTools.coalesce(_cfg.get(profile_section, u'database', src_order), u'').strip()
			if profile.database == u'':
				_log.warning('database name not specified, skipping profile [%s]', profile_name)
				continue
			profile.encoding = gmTools.coalesce(_cfg.get(profile_section, u'encoding', src_order), u'UTF8')
			profile.public_db = bool(_cfg.get(profile_section, u'public/open access', src_order))
			profile.helpdesk = _cfg.get(profile_section, u'help desk', src_order)
			profiles[profile_name] = profile

		if len(profiles) == 0:
			host = u'salaam.homeunix.com'
			label = u'public GNUmed database (%s@%s)' % (current_db_name, host)
			profiles[label] = cBackendProfile()
			profiles[label].name = label
			profiles[label].host = host
			profiles[label].port = 5432
			profiles[label].database = current_db_name
			profiles[label].encoding = u'UTF8'
			profiles[label].public_db = True
		return profiles
	#----------------------------------------------------------
	def __load_state(self):

		src_order = [
			(u'explicit', u'return'),
			(u'workbase', u'return'),
			(u'user', u'return'),
		]

		self._CBOX_user.SetValue (
			gmTools.coalesce (
				_cfg.get(u'preferences', u'login', src_order),
				self.__previously_used_accounts[0]
			)
		)

		prefs_profile = _cfg.get(u'preferences', u'profile', src_order)
		try:
			self._CBOX_profile.SetValue(self.__backend_profiles[prefs_profile].name)
		except KeyError:
			self._CBOX_profile.SetValue(self.__backend_profiles[self.__backend_profiles.keys()[0]].name)

		self._CHBOX_debug.SetValue(_cfg.get(option = 'debug'))
		self._CHBOX_slave.SetValue(_cfg.get(option = 'slave'))
	#----------------------------------------------------
	def save_state(self):
		"""Save parameter settings to standard configuration file"""
		prefs_name = _cfg.get(option = 'user_preferences_file')
		_log.debug(u'saving login choices in [%s]', prefs_name)

		gmCfg2.set_option_in_INI_file (
			filename = prefs_name,
			group = 'preferences',
			option = 'login',
			value = self._CBOX_user.GetValue()
		)

		gmCfg2.set_option_in_INI_file (
			filename = prefs_name,
			group = 'preferences',
			option = 'profile',
			value = self._CBOX_profile.GetValue()
		)
	#############################################################################
	# Retrieve current settings from user interface widgets
	#############################################################################
	def GetLoginInfo(self):
		"""convenience function for compatibility with gmLoginInfo.LoginInfo"""
		if not self.cancelled:
			# FIXME: do not assume conf file is latin1 !
			profile = self.__backend_profiles[self._CBOX_profile.GetValue().encode('latin1').strip()]
			login = gmLoginInfo.LoginInfo (
				user = self._CBOX_user.GetValue(),
				password = self.pwdentry.GetValue(),
				host = profile.host,
				database = profile.database,
				port = profile.port
			)
			login.public_db = profile.public_db
			login.helpdesk = profile.helpdesk
			return login

		return None
	#----------------------------
	# event handlers
	#----------------------------
	def OnHelp(self, event):
		praxis = gmSurgery.gmCurrentPractice()
		wx.MessageBox(_(
"""GNUmed main login screen

USER:
 name of the GNUmed user
PASSWORD
 password for this user

button OK:
 proceed with login
button OPTIONS:
 set advanced options
button CANCEL:
 abort login and quit GNUmed client
button HELP:
 this help screen

For assistance on using GNUmed please contact:
 %s""") % praxis.helpdesk)

	#----------------------------
	def __on_login_button_pressed(self, event):

		root_logger = logging.getLogger()
		if self._CHBOX_debug.GetValue():
			_log.info('debug mode enabled')
			_cfg.set_option(option = 'debug', value = True)
			root_logger.setLevel(logging.DEBUG)
		else:
			_log.info('debug mode disabled')
			_cfg.set_option(option = 'debug', value = False)
			if _cfg.get(option = '--quiet', source_order = [('cli', 'return')]):
				root_logger.setLevel(logging.ERROR)
			else:
				root_logger.setLevel(logging.WARNING)

		if self._CHBOX_slave.GetValue():
			_log.info('slave mode enabled')
			_cfg.set_option(option = 'slave', value = True)
		else:
			_log.info('slave mode disabled')
			_cfg.set_option(option = 'slave', value = False)

		self.backend_profile = self.__backend_profiles[self._CBOX_profile.GetValue().encode('latin1').strip()]
#		self.user = self._CBOX_user.GetValue().strip()
#		self.password = self.GetPassword()
		self.cancelled = False
		self.parent.Close()
	#----------------------------
	def OnCancel(self, event):
		self.cancelled = True
		self.parent.Close()

#================================================================
# main
#----------------------------------------------------------------
if __name__ == "__main__":

	from Gnumed.pycommon import gmI18N

	logging.basicConfig(level = logging.DEBUG)

	gmI18N.activate_locale()
	gmI18N.install_domain(domain='gnumed')
	#-----------------------------------------------
	#-----------------------------------------------
	def test():
		app = wx.PyWidgetTester(size = (300,400))
		#show the login panel in a main window
#		app.SetWidget(cLoginPanel, -1)
		#and pop the login dialog up modally
		dlg = cLoginDialog(None, -1) #, png_bitmap = 'bitmaps/gnumedlogo.png')
		dlg.ShowModal()
		#demonstration how to access the login dialog values
		lp = dlg.panel.GetLoginInfo()
		if lp is None:
			wx.MessageBox(_("Dialog was cancelled by user"))
		else:
			wx.MessageBox(_("You tried to log in as [%s] with password [%s].\nHost:%s, DB: %s, Port: %s") % (lp.GetUser(),lp.GetPassword(),lp.GetHost(),lp.GetDatabase(),lp.GetPort()))
		dlg.Destroy()
#		app.MainLoop()
	#-----------------------------------------------
	if len(sys.argv) > 1 and sys.argv[1] == 'test':
		print "no regression tests yet"

#================================================================
# $Log: gmAuthWidgets.py,v $
# Revision 1.20  2008-05-13 14:10:35  ncq
# - be more permissive in time skew check
# - handle per-profile public-db/helpdesk options
#
# Revision 1.19  2008/04/16 20:39:39  ncq
# - working versions of the wxGlade code and use it, too
# - show client version in login dialog
#
# Revision 1.18  2008/03/20 15:30:21  ncq
# - use gmPG2.sanity_check_time_skew()
#
# Revision 1.17  2008/03/11 17:00:49  ncq
# - explicitely request readonly raw connection
#
# Revision 1.16  2008/03/06 18:29:29  ncq
# - standard lib logging only
#
# Revision 1.15  2008/03/05 22:26:52  ncq
# - spelling
#
# Revision 1.14  2008/02/25 17:33:16  ncq
# - use improved db sanity checks
#
# Revision 1.13  2008/01/30 14:07:02  ncq
# - protect against faulty backend profile in preferences
#
# Revision 1.12  2008/01/27 21:13:17  ncq
# - no more gmCfg
#
# Revision 1.11  2008/01/14 20:33:06  ncq
# - cleanup
# - properly detect connection errors
#
# Revision 1.10  2008/01/13 01:16:52  ncq
# - log DSN on any connect errors
#
# Revision 1.9  2008/01/07 19:51:54  ncq
# - bump db version
# - we still need gmCfg
#
# Revision 1.8  2007/12/26 23:22:27  ncq
# - fix invalid variable access
#
# Revision 1.7  2007/12/26 22:44:31  ncq
# - missing import of logging
# - use std lib logger
# - cleanup
#
# Revision 1.6  2007/12/26 22:01:25  shilbert
# - cleanup
#
# Revision 1.5  2007/12/23 22:02:56  ncq
# - no more gmCLI
#
# Revision 1.4  2007/12/23 20:26:31  ncq
# - cleanup
#
# Revision 1.3  2007/12/23 12:07:40  ncq
# - cleanup
# - use gmCfg2
#
# Revision 1.2  2007/12/04 16:14:52  ncq
# - get_dbowner_connection()
#
# Revision 1.1  2007/12/04 16:03:43  ncq
# - merger of gmLogin and gmLoginDialog
#
#

#----------------------------------------------------------------
# old logs
#----------------------------------------------------------------
# Log: gmLogin.py,v
# Revision 1.37  2007/12/04 15:23:14  ncq
# - reorder connect_to_database()
# - check server settings sanity
#
# Revision 1.36  2007/11/09 14:40:33  ncq
# - gmPG2 dumps schema by itself now on hash mismatch
#
# Revision 1.35  2007/10/23 21:24:39  ncq
# - start backend listener on login
#
# Revision 1.34  2007/06/11 20:25:18  ncq
# - better logging
#
# Revision 1.33  2007/04/27 13:29:31  ncq
# - log schema dump on version conflict
#
# Revision 1.32  2007/03/18 14:10:07  ncq
# - do show schema mismatch warning even if --override-schema-check
#
# Revision 1.31  2007/03/08 11:41:55  ncq
# - set default client encoding from here
# - save state when --override-schema-check == True, too
#
# Revision 1.30  2006/12/15 15:27:01  ncq
# - move database schema version check here
#
# Revision 1.29  2006/10/25 07:46:44  ncq
# - Format() -> strftime() since datetime.datetime does not have .Format()
#
# Revision 1.28  2006/10/25 07:21:57  ncq
# - no more gmPG
#
# Revision 1.27  2006/10/24 13:25:19  ncq
# - Login() -> connect_to_database()
# - make gmPG2 main connection provider, piggyback gmPG onto it for now
#
# Revision 1.26  2006/10/08 11:04:45  ncq
# - simplify wx import
# - piggyback gmPG2 until gmPG is pruned
#
# Revision 1.25  2006/01/03 12:12:03  ncq
# - make epydoc happy re _()
#
# Revision 1.24  2005/09/27 20:44:59  ncq
# - wx.wx* -> wx.*
#
# Revision 1.23  2005/09/26 18:01:51  ncq
# - use proper way to import wx26 vs wx2.4
# - note: THIS WILL BREAK RUNNING THE CLIENT IN SOME PLACES
# - time for fixup
#
# Revision 1.22  2004/09/13 08:54:49  ncq
# - cleanup
# - use gmGuiHelpers
#
# Revision 1.21  2004/07/18 20:30:54  ncq
# - wxPython.true/false -> Python.True/False as Python tells us to do
#
# Revision 1.20  2004/06/20 16:01:05  ncq
# - please epydoc more carefully
#
# Revision 1.19  2004/06/20 06:49:21  ihaywood
# changes required due to Epydoc's OCD
#
# Revision 1.18  2004/03/04 19:47:06  ncq
# - switch to package based import: from Gnumed.foo import bar
#
# Revision 1.17  2003/11/17 10:56:38  sjtan
#
# synced and commiting.
#
# Revision 1.1  2003/10/23 06:02:39  sjtan
#
# manual edit areas modelled after r.terry's specs.
#
# Revision 1.16  2003/06/26 21:40:29  ncq
# - fatal->verbose
#
# Revision 1.15  2003/02/07 14:28:05  ncq
# - cleanup, cvs keywords
#
# @change log:
#	29.10.2001 hherb first draft, untested
#
#----------------------------------------------------------------
# Log: gmLoginDialog.py,v
# Revision 1.90  2007/10/22 12:38:32  ncq
# - default db change
#
# Revision 1.89  2007/10/07 12:32:41  ncq
# - workplace property now on gmSurgery.gmCurrentPractice() borg
#
# Revision 1.88  2007/09/20 19:07:38  ncq
# - port 5432 on salaam again
#
# Revision 1.87  2007/09/04 23:30:28  ncq
# - support --slave and slave mode checkbox
#
# Revision 1.86  2007/08/07 21:42:40  ncq
# - cPaths -> gmPaths
#
# Revision 1.85  2007/06/14 21:55:49  ncq
# - try to fix wx2.8 problem with size
#
# Revision 1.84  2007/06/11 20:25:55  ncq
# - bump database version
#
# Revision 1.83  2007/06/10 10:17:54  ncq
# - fix when no --debug
#
# Revision 1.82  2007/05/22 13:35:11  ncq
# - default port 5433 now on salaam
#
# Revision 1.81  2007/05/08 11:16:10  ncq
# - set debugging flag based on user checkbox selection
#
# Revision 1.80  2007/05/07 12:33:31  ncq
# - use gmTools.cPaths
# - support debug mode checkbox
#
# Revision 1.79  2007/04/11 20:45:01  ncq
# - no more 'resource dir'
#
# Revision 1.78  2007/04/02 15:15:19  ncq
# - v5 -> v6
#
# Revision 1.77  2007/03/08 16:20:50  ncq
# - need to reference proper cfg file
#
# Revision 1.76  2007/03/08 11:46:23  ncq
# - restructured
#   - cleanup
#   - no more cLoginParamChoices
#   - no more loginparams keyword
#   - properly set user preferences file
#   - backend profile now can contain per-profile default encoding
#   - support system-wide profile pre-defs in /etc/gnumed/gnumed-client.conf
#
# Revision 1.75  2007/02/17 14:13:11  ncq
# - gmPerson.gmCurrentProvider().workplace now property
#
# Revision 1.74  2007/01/30 17:40:22  ncq
# - cleanup, get rid of wxMAC IFDEF
# - use user preferences file for storing login preferences
#
# Revision 1.73  2006/12/21 16:54:32  ncq
# - inage handlers already inited
#
# Revision 1.72  2006/12/15 15:27:28  ncq
# - cleanup
#
# Revision 1.71  2006/10/25 07:21:57  ncq
# - no more gmPG
#
# Revision 1.70  2006/09/01 14:45:03  ncq
# - assume conf file is latin1 ... FIX later !
#
# Revision 1.69  2006/07/30 17:50:03  ncq
# - properly load bitmaps
#
# Revision 1.68  2006/05/15 07:05:07  ncq
# - must import gmPerson now
#
# Revision 1.67  2006/05/14 21:44:22  ncq
# - add get_workplace() to gmPerson.gmCurrentProvider and make use thereof
# - remove use of gmWhoAmI.py
#
# Revision 1.66  2006/05/12 12:18:11  ncq
# - whoami -> whereami cleanup
# - use gmCurrentProvider()
#
# Revision 1.65  2005/09/28 21:27:30  ncq
# - a lot of wx2.6-ification
#
# Revision 1.64  2005/09/27 20:44:59  ncq
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
# - fixed issue with missing profiles when writing to empty gnumed.conf.
# This lead to a crash when trying to load the invalid gnumed.conf.
# Now we just ignore this and fall back to defaults.
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
# - remove faceName option from wx.Font on wxMac or else no go
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
