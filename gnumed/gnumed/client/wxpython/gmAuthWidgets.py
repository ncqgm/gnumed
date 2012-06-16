"""GNUmed authentication widgets.

This module contains widgets and GUI
functions for authenticating users.
"""
#================================================================
__version__ = "$Revision: 1.45 $"
__author__ = "karsten.hilbert@gmx.net, H.Herb, H.Berger, R.Terry"
__license__ = "GPL v2 or later (details at http://www.gnu.org)"


# stdlib
import sys, os.path, logging, re as regex


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
	_('dummy-no-need-to-translate-but-make-epydoc-happy')
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

#================================================================
# convenience functions
#----------------------------------------------------------------
def connect_to_database(max_attempts=3, expected_version=None, require_version=True):
	"""Display the login dialog and try to log into the backend.

	- up to max_attempts times
	- returns True/False
	"""
	# force programmer to set a valid expected_version
	expected_hash = gmPG2.known_schema_hashes[expected_version]
	client_version = _cfg.get(option = u'client_version')
	global current_db_name
	current_db_name = u'gnumed_v%s' % expected_version

	attempt = 0

	dlg = cLoginDialog(None, -1, client_version = client_version)
	dlg.Centre(wx.BOTH)

	while attempt < max_attempts:

		_log.debug('login attempt %s of %s', (attempt+1), max_attempts)

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
			_log.error(u"login attempt failed: %s", e)
			if attempt < max_attempts:
				if (u'host=127.0.0.1' in (u'%s' % e)) or (u'host=' not in (u'%s' % e)):
					msg = _(
						'Unable to connect to database:\n\n'
						'%s\n\n'
						"Are you sure you have got a local database installed ?\n"
						'\n'
						"Please retry with proper credentials or cancel.\n"
						'\n'
						'You may also need to check the PostgreSQL client\n'
						'authentication configuration in pg_hba.conf. For\n'
						'details see:\n'
						'\n'
						'wiki.gnumed.de/bin/view/Gnumed/ConfigurePostgreSQL'
					)
				else:
					msg = _(
						"Unable to connect to database:\n\n"
						"%s\n\n"
						"Please retry with proper credentials or cancel.\n"
						"\n"
						'You may also need to check the PostgreSQL client\n'
						'authentication configuration in pg_hba.conf. For\n'
						'details see:\n'
						'\n'
						'wiki.gnumed.de/bin/view/Gnumed/ConfigurePostgreSQL'
					)
				msg = msg % e
				msg = regex.sub(r'password=[^\s]+', u'password=%s' % gmTools.u_replacement_character, msg)
				gmGuiHelpers.gm_show_error (
					msg,
					_('Connecting to backend')
				)
			del e
			continue

		except gmPG2.dbapi.OperationalError, e:
			_log.error(u"login attempt failed: %s", e)
			msg = _(
				"Unable to connect to database:\n\n"
				"%s\n\n"
				"Please retry another backend / user / password combination !\n"
			) % gmPG2.extract_msg_from_pg_exception(e)
			msg = regex.sub(r'password=[^\s]+', u'password=%s' % gmTools.u_replacement_character, msg)
			gmGuiHelpers.gm_show_error (
				msg,
				_('Connecting to backend')
			)
			del e
			continue

		# connect was successful
		gmPG2.set_default_login(login = login)
		gmPG2.set_default_client_encoding(encoding = dlg.panel.backend_profile.encoding)

		seems_bootstrapped = gmPG2.schema_exists(schema = 'gm')
		if not seems_bootstrapped:
			_log.error('schema [gm] does not exist - database not bootstrapped ?')
			msg = _(
				'The database you connected to does not seem\n'
				'to have been boostrapped properly.\n'
				'\n'
				'Make sure you have run the GNUmed database\n'
				'bootstrapper tool to create a new database.\n'
				'\n'
				'Further help can be found on the website at\n'
				'\n'
				'  http://wiki.gnumed.de\n'
				'\n'
				'or on the GNUmed mailing list.'
			)
			gmGuiHelpers.gm_show_error(msg, _('Verifying database'))
			connected = False
			break

		compatible = gmPG2.database_schema_compatible(version = expected_version)
		if compatible or not require_version:
			dlg.panel.save_state()

		if not compatible:
			connected_db_version = gmPG2.get_schema_version()
			msg = msg_generic % (
				client_version,
				connected_db_version,
				expected_version,
				gmTools.coalesce(login.host, '<localhost>'),
				login.database,
				login.user
			)
			if require_version:
				gmGuiHelpers.gm_show_error(msg + msg_fail, _('Verifying database version'))
				connected = False
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
				connected = False
				continue

		sanity_level, message = gmPG2.sanity_check_database_settings()
		if sanity_level != 0:
			gmGuiHelpers.gm_show_error((msg_insanity % message), _('Verifying database settings'))
			if sanity_level == 2:
				connected = False
				continue

		gmExceptionHandlingWidgets.set_is_public_database(login.public_db)
		gmExceptionHandlingWidgets.set_helpdesk(login.helpdesk)

		listener = gmBackendListener.gmBackendListener(conn = conn)
		break

	dlg.Destroy()

	return connected
#================================================================
def get_dbowner_connection(procedure=None, dbo_password=None, dbo_account=u'gm-dbo'):
	if procedure is None:
		procedure = _('<restricted procedure>')

	# 1) get password for gm-dbo
	if dbo_password is None:
		dbo_password = wx.GetPasswordFromUser (
			message = _("""
 [%s]

This is a restricted procedure. We need the
current password for the GNUmed database owner.

Please enter the current password for <%s>:""") % (
				procedure,
				dbo_account
			),
			caption = procedure
		)
		if dbo_password == '':
			return None

	# 2) connect as gm-dbo
	login = gmPG2.get_default_login()
	dsn = gmPG2.make_psycopg2_dsn (
		database = login.database,
		host = login.host,
		port = login.port,
		user = dbo_account,
		password = dbo_password
	)
	try:
		conn = gmPG2.get_connection (
			dsn = dsn,
			readonly = False,
			verbose = True,
			pooled = False
		)
	except:
		_log.exception('cannot connect')
		gmGuiHelpers.gm_show_error (
			aMessage = _('Cannot connect as the GNUmed database owner <%s>.') % dbo_account,
			aTitle = procedure
		)
		gmPG2.log_database_access(action = u'failed to connect as database owner for [%s]' % procedure)
		return None

	return conn
#================================================================
def change_gmdbowner_password():

	title = _(u'Changing GNUmed database owner password')

	dbo_account = wx.GetTextFromUser (
		message = _(u"Enter the account name of the GNUmed database owner:"),
		caption = title,
		default_value = u''
	)

	if dbo_account.strip() == u'':
		return False

	dbo_conn = get_dbowner_connection (
		procedure = title,
		dbo_account = dbo_account
	)
	if dbo_conn is None:
		return False

	dbo_pwd_new_1 = wx.GetPasswordFromUser (
		message = _(u"Enter the NEW password for the GNUmed database owner:"),
		caption = title
	)
	if dbo_pwd_new_1.strip() == u'':
		return False

	dbo_pwd_new_2 = wx.GetPasswordFromUser (
		message = _(u"""Enter the NEW password for the GNUmed database owner, again.

(This will protect you from typos.)
		"""),
		caption = title
	)
	if dbo_pwd_new_2.strip() == u'':
		return False

	if dbo_pwd_new_1 != dbo_pwd_new_2:
		return False

	cmd = u"""ALTER ROLE "%s" ENCRYPTED PASSWORD '%s';""" % (
		dbo_account,
		dbo_pwd_new_2
	)
	gmPG2.run_rw_queries(link_obj = dbo_conn, queries = [{'cmd': cmd}], end_tx = True)

	return True
#================================================================
class cBackendProfile:
	pass
#================================================================
class cLoginDialog(wx.Dialog):
	"""cLoginDialog - window holding cLoginPanel"""

	def __init__(self, parent, id, title=_("Welcome to the"), client_version=u'*** unknown ***'):
		wx.Dialog.__init__(self, parent, id, title)
		self.panel = cLoginPanel(self, -1, isDialog=1, client_version = client_version)
		self.Fit() # needed for Windoze.
		self.Centre()

		self.SetIcon(gmTools.get_icon(wx = wx))
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
		paths = gmTools.gmPaths(app_name = u'gnumed', wx = wx)
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
		label = wx.StaticText( self, -1, _('Log into'), wx.DefaultPosition, wx.DefaultSize, 0)
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
		self._CHBOX_debug = wx.CheckBox(self, -1, _('&Debug mode'))
		self._CHBOX_debug.SetToolTipString(_('Check this to run GNUmed client in debugging mode.'))
		self.pboxgrid.Add(self._CHBOX_debug, 0, wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

		# --slave checkbox
		label = wx.StaticText(self, -1, '', wx.DefaultPosition, wx.DefaultSize, 0)
		label.SetForegroundColour(wx.Colour(35, 35, 142))
		self.pboxgrid.Add(label, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
		self._CHBOX_slave = wx.CheckBox(self, -1, _('Enable &remote control'))
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
					(u'explicit', u'extend'),
					(u'user', u'extend'),
					(u'workbase', u'extend')
				]
			),
			['any-doc']
		)
		# FIXME: make unique

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
		# find active profiles
		src_order = [
			(u'explicit', u'extend'),
			(u'system', u'extend'),
			(u'user', u'extend'),
			(u'workbase', u'extend')
		]

		profile_names = gmTools.coalesce (
			_cfg.get(group = u'backend', option = u'profiles', source_order = src_order),
			[]
		)

		# find data for active profiles
		src_order = [
			(u'explicit', u'return'),
			(u'workbase', u'return'),
			(u'user', u'return'),
			(u'system', u'return')
		]

		profiles = {}

		for profile_name in profile_names:
			# FIXME: once the profile has been found always use the corresponding source !
			# FIXME: maybe not or else we cannot override parts of the profile
			profile = cBackendProfile()
			profile_section = 'profile %s' % profile_name

			profile.name = profile_name
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

			label = u'%s (%s@%s)' % (profile_name, profile.database, profile.host)
			profiles[label] = profile

		# sort out profiles with incompatible database versions if not --debug
		# NOTE: this essentially hardcodes the database name in production ...
		if not (_cfg.get(option = 'debug') or current_db_name.endswith('_devel')):
			profiles2remove = []
			for label in profiles:
				if profiles[label].database != current_db_name:
					profiles2remove.append(label)
			for label in profiles2remove:
				del profiles[label]

		if len(profiles) == 0:
			host = u'publicdb.gnumed.de'
			label = u'public GNUmed database (%s@%s)' % (current_db_name, host)
			profiles[label] = cBackendProfile()
			profiles[label].name = label
			profiles[label].host = host
			profiles[label].port = 5432
			profiles[label].database = current_db_name
			profiles[label].encoding = u'UTF8'
			profiles[label].public_db = True
			profiles[label].helpdesk = u'http://wiki.gnumed.de'

		return profiles
	#----------------------------------------------------------
	def __load_state(self):

		src_order = [
			(u'explicit', u'return'),
			(u'user', u'return'),
		]

		self._CBOX_user.SetValue (
			gmTools.coalesce (
				_cfg.get(u'preferences', u'login', src_order),
				self.__previously_used_accounts[0]
			)
		)

		last_used_profile_label = _cfg.get(u'preferences', u'profile', src_order)
		if last_used_profile_label in self.__backend_profiles.keys():
			self._CBOX_profile.SetValue(last_used_profile_label)
		else:
			self._CBOX_profile.SetValue(self.__backend_profiles.keys()[0])

		self._CHBOX_debug.SetValue(_cfg.get(option = 'debug'))
		self._CHBOX_slave.SetValue(_cfg.get(option = 'slave'))
	#----------------------------------------------------
	def save_state(self):
		"""Save parameter settings to standard configuration file"""
		prefs_name = _cfg.get(option = 'user_preferences_file')
		_log.debug(u'saving login preferences in [%s]', prefs_name)

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
			#profile = self.__backend_profiles[self._CBOX_profile.GetValue().encode('latin1').strip()]
			profile = self.__backend_profiles[self._CBOX_profile.GetValue().encode('utf8').strip()]
			_log.info(u'backend profile "%s" selected', profile.name)
			_log.info(u' details: <%s> on %s@%s:%s (%s, %s)',
				self._CBOX_user.GetValue(),
				profile.database,
				profile.host,
				profile.port,
				profile.encoding,
				gmTools.bool2subst(profile.public_db, u'public', u'private')
			)
			_log.info(u' helpdesk: "%s"', profile.helpdesk)
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

Welcome to the GNUmed client. Shown are the current
"Workplace" and (version).

You may select to log into a public database with username
and password {any-doc, any-doc}. Any other database
(including a local one) must first be separately installed
before you can log in.

For assistance on using GNUmed please consult the wiki:

 http://wiki.gnumed.de/bin/view/Gnumed/GnumedManual

and to install a local database see:

 http://wiki.gnumed.de/bin/view/Gnumed/GmManualServerInstall

For more help than the above, please contact:

 GNUmed Development List <gnumed-bugs@gnu.org>

For local assistance please contact:

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

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	# we don't have tests yet
	sys.exit()

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

#================================================================

