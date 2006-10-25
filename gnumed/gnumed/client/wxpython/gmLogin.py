#############################################################################
# gmLogin - Display a login dialog and log onto backend(s)
# ---------------------------------------------------------------------------
#
# @copyright: author
# @license: GPL (details at http://www.gnu.org)
############################################################################
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/Attic/gmLogin.py,v $
# $Id: gmLogin.py,v 1.29 2006-10-25 07:46:44 ncq Exp $
__version__ = "$Revision: 1.29 $"
__author__ = "H.Herb"

import wx

from Gnumed.pycommon import gmLog, gmExceptions, gmI18N, gmPG2
from Gnumed.wxpython import gmLoginDialog, gmGuiHelpers

try:
	_('do-not-translate-but-make-epydoc-happy')
except NameError:
	_ = lambda x:x

_log = gmLog.gmDefLog
#==============================================================
def connect_to_database(max_attempts=3):
	"""Display the login dialog and try to log into the backend.

	- up to max_attempts times
	- returns:
		- valid backend broker object if connection successful
		- None otherwise
	"""
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
		#now try to connect to the backend
		dsn = gmPG2.make_psycopg2_dsn (
			database=login.database,
			host=login.host,
			port=login.port,
			user=login.user,
			password=login.password
		)
		try:
			gmPG2.get_connection(dsn=dsn, verbose=True)
			gmPG2.set_default_login(login=login)
			dlg.panel.save_settings()
#			try: gmPG.ConnectionPool(login)
#			except: pass
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

#		try:
#			backend = gmPG.ConnectionPool(login)
			# save the login settings for next login
#			dlg.panel.save_settings()
#			break
#		except gmExceptions.ConnectionError, e:
#			attempt += 1
#			if attempt < max_attempts:
#				msg = _('Unable to connect to database:\n\n%s\n\nPlease retry or cancel !') % e
#				gmGuiHelpers.gm_show_error (
#					msg,
#					_('connecting to backend'),
#					gmLog.lErr
#				)
#			_log.LogException("login attempt %s of %s failed" % (attempt, max_attempts), verbose=0)

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
# Revision 1.29  2006-10-25 07:46:44  ncq
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
