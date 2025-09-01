# -*- coding: utf-8 -*-
"""GNUmed authentication widgets.

This module contains widgets and GUI
functions for authenticating users.
"""
#================================================================
__author__ = "karsten.hilbert@gmx.net, H.Herb, H.Berger, R.Terry"
__license__ = "GPL v2 or later (details at https://www.gnu.org)"


# stdlib
import sys
import os.path
import logging
import re as regex


# 3rd party
import wx


# GNUmed
if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x
else:
	try: _
	except NameError:
		from Gnumed.pycommon import gmI18N
		gmI18N.activate_locale()
		gmI18N.install_domain()
from Gnumed.pycommon import gmLoginInfo
from Gnumed.pycommon import gmPG2
from Gnumed.pycommon import gmConnectionPool
from Gnumed.pycommon import gmBackendListener
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmCfgINI
from Gnumed.pycommon import gmLog2

from Gnumed.business import gmPraxis

from Gnumed.wxpython import gmGuiHelpers
from Gnumed.wxpython import gmExceptionHandlingWidgets


_log = logging.getLogger('gm.ui')
_cfg = gmCfgINI.gmCfgData()


msg_generic = _(
	'GNUmed database version mismatch.\n'
	'\n'
	'This database version cannot be used with this client:\n'
	'\n'
	' client version: %s\n'
	' database version detected: %s\n'
	' database version needed: %s\n'
	'\n'
	'Currently connected to database:\n'
	'\n'
	' host: %s\n'
	' database: %s\n'
	' user: %s'
)

msg_time_skew_fail = _(
	'The server and client clocks are off by more than %s minutes !\n'
	'\n'
	'You must fix the time settings before you can use this database with this client.\n'
	'\n'
	'You may have to contact your administrator for help.'
)

msg_time_skew_warn = _(
	'The server and client clocks are off by more than %s minutes !\n'
	'\n'
	'You should fix the time settings.\n'
	'Otherwise clinical data may appear to have been entered at the wrong time.\n'
	'\n'
	'You may have to contact your administrator for help.'
)

msg_insanity = _(
	"There is a serious problem with the database settings:\n"
	"\n"
	"%s\n"
	"\n"
	"You may have to contact your administrator for help."
)

msg_fail = _(
	"You must connect to a different database in order\n"
	"to use the GNUmed client. You may have to contact\n"
	"your administrator for help."
)

msg_override = _(
	"The client will, however, continue to start up because\n"
	"you are running a development/test version of GNUmed.\n"
	"\n"
	"There may be schema related errors. Please report and/or\n"
	"fix them. Do not rely on this database to work properly\n"
	"in all cases !"
)

msg_auth_error = _(
	"Unable to connect to database:\n\n"
	"%s\n\n"
	"Please retry with proper credentials or cancel.\n"
	"\n"
	"For the public and any new GNUmed databases the\n"
	"default user name and password are {any-doc, any-doc}.\n"
	"\n"
	'You may also need to check the PostgreSQL client\n'
	'authentication configuration in pg_hba.conf. For\n'
	'details see:\n'
	'\n'
	'https://www.gnumed.de/documentation/GNUmedConfigurePostgreSQL.html'
)

msg_auth_error_local = _(
	'Unable to connect to database:\n\n'
	'%s\n\n'
	"Are you sure you have got a local database installed ?\n"
	'\n'
	"Please retry with proper credentials or cancel.\n"
	'\n'
	' (for the public and any new GNUmed data-\n'
	'  bases the default user name and password\n'
	'  are {any-doc, any-doc})\n'
	'\n'
	'You may also need to check the PostgreSQL client\n'
	'authentication configuration in pg_hba.conf. For\n'
	'details see:\n'
	'\n'
	'https://www.gnumed.de/documentation/GNUmedConfigurePostgreSQL.html'
)

msg_login_problem_generic = _(
	"Unable to connect to database:\n\n"
	"%s\n\n"
	"Please retry another backend / user / password combination !\n"
	"\n"
	" (for the public and any new GNUmed databases\n"
	"  the default user name and password are\n"
	"  {any-doc, any-doc})\n"
	"\n"
)

msg_not_bootstrapped = _(
	'The database you connected to does not seem\n'
	'to have been boostrapped properly.\n'
	'\n'
	'Make sure you have run the GNUmed database\n'
	'bootstrapper tool to create a new database.\n'
	'\n'
	'Further help can be found on the website at\n'
	'\n'
	'  https://www.gnumed.de/documentation/\n'
	'\n'
	'or on the GNUmed mailing list.'
)

#================================================================
# convenience functions
#----------------------------------------------------------------
def __database_is_acceptable_for_use(require_version:bool=True, expected_version:int=None, login=None) -> bool:
	if not gmPG2.schema_exists(schema = 'gm'):
		_log.error('schema [gm] does not exist - database not bootstrapped ?')
		gmGuiHelpers.gm_show_error(msg_not_bootstrapped, _('Verifying database'))
		return False

	if not gmPG2.database_schema_compatible(version = expected_version):
		client_version = _cfg.get(option = 'client_version')
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
			gmGuiHelpers.gm_show_error(msg + '\n\n' + msg_fail, _('Verifying database version'))
			return False

		gmGuiHelpers.gm_show_info(msg + '\n\n' + msg_override, _('Verifying database version'))

	max_skew = 10 if _cfg.get(option = 'debug') else 1		# in minutes
	if not gmPG2.sanity_check_time_skew(tolerance = (max_skew * 60)):
		if not _cfg.get(option = 'debug'):
			gmGuiHelpers.gm_show_error(msg_time_skew_fail % max_skew, _('Verifying database settings'))
			return False

		gmGuiHelpers.gm_show_warning(msg_time_skew_warn % max_skew, _('Verifying database settings'))

	insanity_level, message = gmPG2.sanity_check_database_settings()
	if insanity_level > 0:
		gmGuiHelpers.gm_show_error((msg_insanity % message), _('Verifying database settings'))
		if insanity_level == 2:
			return False

	gmLog2.log_multiline (
		logging.DEBUG,
		message = 'DB seems suitable for use, fingerprint:',
		text = gmPG2.get_db_fingerprint(eol = '\n')
	)
	return True

#----------------------------------------------------------------
def connect_to_database(max_attempts=3, expected_version=None, require_version=True):
	"""Display the login dialog and try to log into the backend.

	- up to max_attempts times
	- returns True/False
	"""
	# force programmer to set a valid expected_version
	gmPG2.known_schema_hashes[expected_version]
	client_version = _cfg.get(option = 'client_version')
	global current_db_name
	current_db_name = 'gnumed_v%s' % expected_version
	gmConnectionPool._VERBOSE_PG_LOG = _cfg.get(option = 'debug')
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

		# obscure unconditionally, it could be a valid password
		gmLog2.add_word2hide(login.password)
		# try getting a connection to verify the parameters do work
		creds = gmConnectionPool.cPGCredentials()
		creds.database = login.database
		creds.host = login.host
		creds.port = login.port
		creds.user = login.user
		creds.password = login.password
		pool = gmConnectionPool.gmConnectionPool()
		pool.credentials = creds
		try:
			conn = gmPG2.get_raw_connection(verbose = True, readonly = True)
			_log.info('successfully connected: %s', conn)
			connected = True

		except gmPG2.cAuthenticationError as exc:
			_log.exception('login attempt failed')
			gmPG2.log_pg_exception_details(exc)
			attempt += 1
			if attempt < max_attempts:
				if ('host=127.0.0.1' in ('%s' % exc)) or ('host=' not in ('%s' % exc)):
					msg = msg_auth_error_local
				else:
					msg = msg_auth_error
				msg = msg % exc
				msg = regex.sub(r'password=[^\s]+', 'password=%s' % gmTools.u_replacement_character, msg)
				gmGuiHelpers.gm_show_error(msg, _('Connecting to backend'))
			del exc
			continue

		except gmPG2.dbapi.OperationalError as exc:
			_log.exception('login attempt failed')
			gmPG2.log_pg_exception_details(exc)
			msg = msg_login_problem_generic % exc
			msg = regex.sub(r'password=[^\s]+', 'password=%s' % gmTools.u_replacement_character, msg)
			gmGuiHelpers.gm_show_error(msg, _('Connecting to backend'))
			del exc
			continue

		conn.close()

		if not __database_is_acceptable_for_use(require_version = require_version, expected_version = expected_version, login = login):
			_log.info('database not suitable for use')
			connected = False
			break

		dlg.panel.save_state()
		gmExceptionHandlingWidgets.set_is_public_database(_cfg.get(option = 'is_public_db'))
		gmExceptionHandlingWidgets.set_helpdesk(_cfg.get(option = 'helpdesk'))
		gmLog2.log_multiline (
			logging.DEBUG,
			message = 'fingerprint',
			text = gmPG2.get_db_fingerprint(eol = '\n')
		)
		if 'no_db_listener' in _cfg.get(option = 'special'):
			_log.debug('--special contains "no_db_listener", NOT starting backend listener')
		else:
			_log.debug('establishing DB listener connection')
			conn = gmPG2.get_connection(verbose = True, connection_name = 'GNUmed-[DbListenerThread]', pooled = False)
			gmBackendListener.gmBackendListener(conn = conn)
		break

	dlg.DestroyLater()
	return connected

#================================================================
def get_dbowner_connection(procedure=None, dbo_password=None, dbo_account='gm-dbo'):
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

	gmLog2.add_word2hide(dbo_password)

	# 2) connect as gm-dbo
	pool = gmConnectionPool.gmConnectionPool()
	conn = None
	try:
		conn = pool.get_dbowner_connection (
			readonly = False,
			verbose = True,
			dbo_password = dbo_password,
			dbo_account = dbo_account
		)
	except Exception:
		_log.exception('cannot connect')
		gmGuiHelpers.gm_show_error (
			error = _('Cannot connect as the GNUmed database owner <%s>.') % dbo_account,
			title = procedure
		)
		gmPG2.log_database_access(action = 'failed to connect as database owner for [%s]' % procedure)
	return conn

#================================================================
def change_gmdbowner_password():

	title = _('Changing GNUmed database owner password')

	dbo_account = wx.GetTextFromUser (
		message = _("Enter the account name of the GNUmed database owner:"),
		caption = title,
		default_value = ''
	)

	if dbo_account.strip() == '':
		return False

	dbo_conn = get_dbowner_connection (
		procedure = title,
		dbo_account = dbo_account
	)
	if dbo_conn is None:
		return False

	dbo_pwd_new_1 = wx.GetPasswordFromUser (
		message = _("Enter the NEW password for the GNUmed database owner:"),
		caption = title
	)
	if dbo_pwd_new_1.strip() == '':
		return False

	gmLog2.add_word2hide(dbo_pwd_new_1)

	dbo_pwd_new_2 = wx.GetPasswordFromUser (
		message = _("""Enter the NEW password for the GNUmed database owner, again.

(This will protect you from typos.)
		"""),
		caption = title
	)
	if dbo_pwd_new_2.strip() == '':
		return False

	if dbo_pwd_new_1 != dbo_pwd_new_2:
		return False

	# pwd2 == pwd1 at this point so no need to hide (again)

	"""	On Mon, Mar 13, 2017 at 12:19:22PM -0400, Tom Lane wrote:
		> Date: Mon, 13 Mar 2017 12:19:22 -0400
		> From: Tom Lane <tgl@sss.pgh.pa.us>
		> To: Adrian Klaver <adrian.klaver@aklaver.com>
		> cc: Schmid Andreas <Andreas.Schmid@bd.so.ch>,
		>  "'pgsql-general@postgresql.org'" <pgsql-general@postgresql.org>
		> Subject: Re: [GENERAL] createuser: How to specify a database to connect to
		> 
		> Adrian Klaver <adrian.klaver@aklaver.com> writes:
		> > On 03/13/2017 08:52 AM, Tom Lane wrote:
		> >> If by "history" you're worried about the server-side statement log, this
		> >> is merest fantasy: the createuser program is not magic, it just constructs
		> >> and sends a CREATE USER command for you.  You'd actually be more secure
		> >> using psql, where (if you're superuser) you could shut off log_statement
		> >> for your session first.
		> 
		> > There is a difference though:
		> 
		> > psql> CREATE USER:
		> 
		> > postgres-2017-03-13 09:03:27.147 PDT-0LOG:  statement: create user 
		> > dummy_user with login password '1234';
		> 
		> Well, what you're supposed to do is
		> 
		> postgres=# create user dummy_user;
		> postgres=# \password dummy_user
		> Enter new password: 
		> Enter it again: 
		> postgres=# 
		> 
		> which will result in sending something like
		> 
		> ALTER USER dummy_user PASSWORD 'md5c5e9567bc40082671d02c654260e0e09'
		> 
		> You can additionally protect that by wrapping it into one transaction
		> (if you have a setup where the momentary existence of the role without a
		> password would be problematic) and/or shutting off logging beforehand.
	"""

	# this REALLY should be prefixed with md5 and the md5sum sent rather than the pwd
	cmd = """ALTER ROLE "%s" ENCRYPTED PASSWORD '%s';""" % (
		dbo_account,
		dbo_pwd_new_2
	)
	gmPG2.run_rw_queries(link_obj = dbo_conn, queries = [{'sql': cmd}], end_tx = True)
	return True

#================================================================
class cBackendProfile:
	pass

#================================================================
class cLoginDialog(wx.Dialog):
	"""cLoginDialog - window holding cLoginPanel"""

	def __init__(self, parent, id, title = _("Welcome to"), client_version = '*** unknown ***'):
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
					isDialog = 0, client_version = '*** unknown ***'):
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
		paths = gmTools.gmPaths(app_name = 'gnumed', wx = wx)
		bitmap = os.path.join(paths.system_app_data_dir, 'bitmaps', 'gnumedlogo.png')
		try:
			png = wx.Image(bitmap, wx.BITMAP_TYPE_PNG).ConvertToBitmap()
			bmp = wx.StaticBitmap(self, -1, png, wx.Point(10, 10), wx.Size(png.GetWidth(), png.GetHeight()))
			self.topsizer.Add (
				bmp,
				proportion = 0,
				flag = wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALL,
				border = 10
			)
		except Exception:
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

		paramsbox_caption = _('Workplace "%s" (version %s)') % (gmPraxis.gmCurrentPraxisBranch().active_workplace, client_version)

		# FIXME: why doesn't this align in the centre ?
		self.paramsbox = wx.StaticBox( self, -1, paramsbox_caption, style = wx.ALIGN_CENTRE_HORIZONTAL)
		self.paramsboxsizer = wx.StaticBoxSizer( self.paramsbox, wx.VERTICAL )
		self.__set_label_color(self.paramsbox)  # set color according to background
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
		self.__set_label_color(label)  # set color according to dark/light theme
		self.pboxgrid.Add(label, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
		self.__backend_profiles = self.__get_backend_profiles()
		self._CBOX_profile = wx.ComboBox (
			self,
			-1,
			list(self.__backend_profiles)[0],
			wx.DefaultPosition,
			size = wx.Size(550,-1),
			choices = list(self.__backend_profiles),
			style = wx.CB_READONLY
		)
		self.pboxgrid.Add (self._CBOX_profile, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

		# USER NAME COMBO
		label = wx.StaticText( self, -1, _("Username"), wx.DefaultPosition, wx.DefaultSize, 0 )
		self.__set_label_color(label)  # set color according to dark/light theme
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
		self.__set_label_color(label)  # set color according to dark/light theme
		self.pboxgrid.Add( label, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
		self.pwdentry = wx.TextCtrl( self, 1, '', wx.DefaultPosition, wx.Size(80,-1), wx.TE_PASSWORD )
		# set focus on password entry
		self.pwdentry.SetFocus()
		self.pboxgrid.Add( self.pwdentry, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

		# --debug checkbox
		label = wx.StaticText(self, -1, _('Options'), wx.DefaultPosition, wx.DefaultSize, 0)
		self.__set_label_color(label)  # set color according to dark/light theme
		self.pboxgrid.Add(label, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
		self._CHBOX_debug = wx.CheckBox(self, -1, _('&Debug mode'))
		self._CHBOX_debug.SetToolTip(_('Check this to run GNUmed client in debugging mode.'))
		self.pboxgrid.Add(self._CHBOX_debug, 0, wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

		# --slave checkbox
		label = wx.StaticText(self, -1, '', wx.DefaultPosition, wx.DefaultSize, 0)
		self.__set_label_color(label)  # set color according to dark/light theme
		self.pboxgrid.Add(label, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
		self._CHBOX_slave = wx.CheckBox(self, -1, _('Enable &remote control'))
		self._CHBOX_slave.SetToolTip(_('Check this to run GNUmed client in slave mode for remote control.'))
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
		#1:create login ok button
		#---------------------
		ID_BUTTON_LOGIN = wx.NewId()
		button_login_ok = wx.Button(self, ID_BUTTON_LOGIN, _("&Ok"), wx.DefaultPosition, wx.DefaultSize, 0 )
		button_login_ok.SetToolTip(wx.ToolTip(_("Proceed with login.")) )
		button_login_ok.SetDefault()

		#---------------------
		#2:create cancel button
		#---------------------
		ID_BUTTON_CANCEL = wx.NewId()
		button_cancel = wx.Button(self, ID_BUTTON_CANCEL, _("&Cancel"), wx.DefaultPosition, wx.DefaultSize, 0 )
		button_cancel.SetToolTip(wx.ToolTip(_("Cancel Login.")) )
		#---------------------
		#3:create Help button
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
		self.topsizer.Add( self.button_gridsizer, 0, wx.GROW|wx.ALL, 5)

		self.__load_state()

		self.SetAutoLayout(True)
		self.SetSizer( self.topsizer)
		self.topsizer.Fit( self )
		if self.isDialog:
			self.topsizer.SetSizeHints(parent)

		button_help.Bind(wx.EVT_BUTTON, self.OnHelp)
		button_login_ok.Bind(wx.EVT_BUTTON, self.__on_login_button_pressed)
		button_cancel.Bind(wx.EVT_BUTTON, self.OnCancel)
		#wx.EVT_BUTTON(self, ID_BUTTON_HELP, self.OnHelp)
		#wx.EVT_BUTTON(self, ID_BUTTON_LOGIN, self.__on_login_button_pressed)
		#wx.EVT_BUTTON(self, ID_BUTTON_CANCEL, self.OnCancel)

	#----------------------------------------------------------
	# internal helper methods
	#----------------------------------------------------------
	def __set_label_color(self, label):
		"""Set adaptive label color based on system theme background."""
		if not gmGuiHelpers.is_probably_dark_theme():
			label.SetForegroundColour(wx.Colour(35, 35, 142))  # orig dark blue

	#----------------------------------------------------
	def __get_previously_used_accounts(self):

		accounts = gmTools.coalesce (
			_cfg.get (
				group = 'backend',
				option = 'logins',
				source_order = [
					('explicit', 'extend'),
					('user', 'extend'),
					('workbase', 'extend')
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
			('explicit', 'extend'),
			('system', 'extend'),
			('user', 'extend'),
			('workbase', 'extend')
		]

		profile_names = gmTools.coalesce (
			_cfg.get(group = 'backend', option = 'profiles', source_order = src_order),
			[]
		)

		# find data for active profiles
		src_order = [
			('explicit', 'return'),
			('workbase', 'return'),
			('user', 'return'),
			('system', 'return')
		]

		profiles = {}

		for profile_name in profile_names:
			# FIXME: once the profile has been found always use the corresponding source !
			# FIXME: maybe not or else we cannot override parts of the profile
			profile = cBackendProfile()
			profile_section = 'profile %s' % profile_name

			profile.name = profile_name
			profile.host = gmTools.coalesce(_cfg.get(profile_section, 'host', src_order), '').strip()
			port = gmTools.coalesce(_cfg.get(profile_section, 'port', src_order), 5432)
			try:
				profile.port = int(port)
				if profile.port < 1024:
					raise ValueError('refusing to use privileged port (< 1024)')
			except ValueError:
				_log.warning('invalid port definition: [%s], skipping profile [%s]', port, profile_name)
				continue
			profile.database = gmTools.coalesce(_cfg.get(profile_section, 'database', src_order), '').strip()
			if profile.database == '':
				_log.warning('database name not specified, skipping profile [%s]', profile_name)
				continue
			profile.encoding = gmTools.coalesce(_cfg.get(profile_section, 'encoding', src_order), 'UTF8')
			profile.public_db = bool(_cfg.get(profile_section, 'public/open access', src_order))
			profile.helpdesk = _cfg.get(profile_section, 'help desk', src_order)

			label = '%s (%s@%s)' % (profile_name, profile.database, profile.host)
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
			host = 'publicdb.gnumed.de'
			label = 'public GNUmed database (%s@%s)' % (current_db_name, host)
			profiles[label] = cBackendProfile()
			profiles[label].name = label
			profiles[label].host = host
			profiles[label].port = 5432
			profiles[label].database = current_db_name
			profiles[label].encoding = 'UTF8'
			profiles[label].public_db = True
			profiles[label].helpdesk = 'https://www.gnumed.de'

		return profiles
	#----------------------------------------------------------
	def __load_state(self):

		src_order = [
			('explicit', 'return'),
			('user', 'return'),
		]

		self._CBOX_user.SetValue (
			gmTools.coalesce (
				_cfg.get('preferences', 'login', src_order),
				self.__previously_used_accounts[0]
			)
		)

		last_used_profile_label = _cfg.get('preferences', 'profile', src_order)
		if last_used_profile_label in self.__backend_profiles:
			self._CBOX_profile.SetValue(last_used_profile_label)
		else:
			self._CBOX_profile.SetValue(list(self.__backend_profiles)[0])

		self._CHBOX_debug.SetValue(_cfg.get(option = 'debug'))
		self._CHBOX_slave.SetValue(_cfg.get(option = 'slave'))
	#----------------------------------------------------
	def save_state(self):
		"""Save parameter settings to standard configuration file"""
		prefs_name = _cfg.get(option = 'user_preferences_file')
		_log.debug('saving login preferences in [%s]', prefs_name)

		gmCfgINI.set_option_in_INI_file (
			filename = prefs_name,
			group = 'preferences',
			option = 'login',
			value = self._CBOX_user.GetValue()
		)

		gmCfgINI.set_option_in_INI_file (
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
		if self.cancelled:
			return None

		# FIXME: do not assume conf file is latin1 !
		profile = self.__backend_profiles[self._CBOX_profile.GetValue().strip()]
		_log.info('backend profile "%s" selected', profile.name)
		_log.info(' details: <%s> on %s@%s:%s (%s, %s)',
			self._CBOX_user.GetValue(),
			profile.database,
			profile.host,
			profile.port,
			profile.encoding,
			gmTools.bool2subst(profile.public_db, 'public', 'private')
		)
		_log.info(' helpdesk: "%s"', profile.helpdesk)
		login = gmLoginInfo.LoginInfo (
			user = self._CBOX_user.GetValue(),
			password = self.pwdentry.GetValue(),
			host = profile.host,
			database = profile.database,
			port = profile.port
		)
		_cfg.set_option (
			option = 'is_public_db',
			value = profile.public_db
		)
		_cfg.set_option (
			option = 'helpdesk',
			value = profile.helpdesk
		)
		_cfg.set_option (
			option = 'backend_profile',
			value = profile.name
		)
		return login
	#----------------------------
	# event handlers
	#----------------------------
	def OnHelp(self, event):
		praxis = gmPraxis.gmCurrentPraxisBranch()
		wx.MessageBox(_(
"""Unable to connect to the database ?

 "PostgreSQL: FATAL:  password authentication failed ..."

The default user name and password are {any-doc, any-doc}
for the public and any new GNUmed databases.

 "... could not connect to server ..."

Mostly this is a case of new users who did not yet install
or configure a PostgreSQL server and/or a GNUmed database
of their own, which you must do before you can connect to
anything other than the public demonstration database, see

 https://www.gnumed.de/documentation/GNUmedDatabaseInstallation.html

For assistance on using GNUmed please consult the documentation:

 https://www.gnumed.de/documentation/

For more help than the above, please contact:

 GNUmed Development List <gnumed-bugs@gnu.org>

For local assistance please contact:

 %s""") % praxis.helpdesk,
 		caption = _('HELP for GNUmed main login screen'))

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

		self.backend_profile = self.__backend_profiles[self._CBOX_profile.GetValue().strip()]
#		self.user = self._CBOX_user.GetValue().strip()
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

	logging.basicConfig(level = logging.DEBUG)

	del _
	from Gnumed.pycommon import gmI18N
	gmI18N.activate_locale()
	gmI18N.install_domain('gnumed')

	#-----------------------------------------------
	#-----------------------------------------------
	def test():
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
			wx.MessageBox(_("You tried to log in as [%s] with password [%s].\nHost:%s, DB: %s, Port: %s") % (
				lp.GetUser(),
				lp.GetHost(),
				lp.GetDatabase(),
				lp.GetPort()
			))
		dlg.DestroyLater()
#		app.MainLoop()

#================================================================
