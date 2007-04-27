#############################################################################
# gmLogin - Display a login dialog and log onto backend(s)
# ---------------------------------------------------------------------------
#
# @copyright: author
# @license: GPL (details at http://www.gnu.org)
############################################################################
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/Attic/gmLogin.py,v $
# $Id: gmLogin.py,v 1.33 2007-04-27 13:29:31 ncq Exp $
__version__ = "$Revision: 1.33 $"
__author__ = "H.Herb"

import wx

from Gnumed.pycommon import gmLog, gmExceptions, gmI18N, gmPG2
from Gnumed.wxpython import gmLoginDialog, gmGuiHelpers

try:
	_('do-not-translate-but-make-epydoc-happy')
except NameError:
	_ = lambda x:x

_log = gmLog.gmDefLog

msg_generic = _("""
GNUmed database version mismatch.

This database version cannot be used with this client:

 version detected: %s
 version needed: %s

Currently connected to database:

 host: %s
 database: %s
 user: %s
""")

msg_fail = _("""
You must connect to a different database in order
to use the GNUmed client. You may have to contact
your administrator for help."""
)

msg_override = _("""
The client will, however, continue to start up because
you are running a development/test version of GNUmed.

There may be schema related errors. Please report and/or
fix them. Do not rely on this database to work properly
in all cases !"""
)
#==============================================================
def connect_to_database(max_attempts=3, expected_version=None, require_version=True):
	"""Display the login dialog and try to log into the backend.

	- up to max_attempts times
	- returns:
		- valid backend broker object if connection successful
		- None otherwise
	"""
	# force programmer to set a valid expected_version
	expected_hash = gmPG2.known_schema_hashes[expected_version]

	attempt = 0
	connected = False

	dlg = gmLoginDialog.LoginDialog(None, -1)
	dlg.Centre(wx.BOTH)

	while attempt < max_attempts:

		dlg.ShowModal()

		login = dlg.panel.GetLoginInfo()
		if login is None:
			_log.Log(gmLog.lInfo, "user cancelled login dialog")
			break

		# now try to connect to the backend
		dsn = gmPG2.make_psycopg2_dsn (
			database = login.database,
			host = login.host,
			port = login.port,
			user = login.user,
			password = login.password
		)

		try:
			# try getting a connection to verify the DSN works
			gmPG2.get_raw_connection(dsn = dsn, verbose = True)
			gmPG2.set_default_login(login = login)
			gmPG2.set_default_client_encoding(encoding = dlg.panel.backend_profile.encoding)

			compatible = gmPG2.database_schema_compatible(version = expected_version)

			if compatible or not require_version:
				dlg.panel.save_state()

			if not compatible:
				_log.Log(gmLog.lData, 'normalized schema dump follows:')
				for line in gmPG2.get_schema_structure().split():
					_log.Log(gmLog.lData, line)
				connected_db_version = gmPG2.get_schema_version()
				msg = msg_generic % (connected_db_version, expected_version, login.host, login.database, login.user)
				if require_version:
					gmGuiHelpers.gm_show_error(msg + msg_fail, _('Verifying database version'), None)
					continue
				gmGuiHelpers.gm_show_info(msg + msg_override, _('Verifying database version'), None)

			connected = True
			break

		except gmPG2.cAuthenticationError, e:
			attempt += 1
			_log.LogException(u"login attempt %s/%s failed" % (attempt, max_attempts), verbose=0)
			if attempt < max_attempts:
				gmGuiHelpers.gm_show_error (_(
						"Unable to connect to database:\n\n"
						"%s\n\n"
						"Please retry or cancel !"
					) % e,
					_('Connecting to backend'),
					gmLog.lErr
				)
			_log.LogException(u"login attempt %s/%s failed" % (attempt, max_attempts), verbose=0)

		except StandardError:
			_log.LogException(u"login attempt %s/%s failed" % (attempt+1, max_attempts), verbose=0)
			break

	dlg.Close()
	dlg.Destroy()

	return connected
#==============================================================
# main
#==============================================================
if __name__ == "__main__":
	print "This module needs a test function!  please write it"
#==============================================================
# $Log: gmLogin.py,v $
# Revision 1.33  2007-04-27 13:29:31  ncq
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
