#############################################################################
# gmLogin - Display a login dialog and log onto backend(s)
# ---------------------------------------------------------------------------
#
# @copyright: author
# @license: GPL (details at http://www.gnu.org)
############################################################################
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/Attic/gmLogin.py,v $
# $Id: gmLogin.py,v 1.24 2005-09-27 20:44:59 ncq Exp $
__version__ = "$Revision: 1.24 $"
__author__ = "H.Herb"

import os.path, sys

try:
	import wxversion
	import wx
except ImportError:
	from wxPython import wx

from Gnumed.pycommon import gmPG, gmLog, gmExceptions, gmI18N
from Gnumed.wxpython import gmLoginDialog, gmGuiHelpers

_log = gmLog.gmDefLog
#==============================================================
def Login(max_attempts=3):
	"""Display the login dialog and try to log into the backend.

	- up to max_attempts times
	- returns:
		- valid backend broker object if connection successful
		- None otherwise
	"""
	attempt = 0
	backend = None
	#display the login dialog
	dlg = gmLoginDialog.LoginDialog(None, -1)
	dlg.Centre(wx.BOTH)
	while attempt < max_attempts:
		dlg.ShowModal()
		#get the login parameters
		login = dlg.panel.GetLoginInfo()
		if login is None:
			_log.Log(gmLog.lInfo, "user cancelled login dialog")
			break
		#now try to connect to the backend
		try:
			backend = gmPG.ConnectionPool(login)
			# save the login settings for next login
			dlg.panel.save_settings()
			break
		except gmExceptions.ConnectionError, e:
			attempt += 1
			if attempt < max_attempts:
				msg = _('Unable to connect to database:\n\n%s\n\nPlease retry or cancel !') % e
				gmGuiHelpers.gm_show_error (
					msg,
					_('connecting to backend'),
					gmLog.lErr
				)
			_log.LogException("login attempt %s of %s failed" % (attempt, max_attempts), sys.exc_info(), verbose=0)

	dlg.Close()
	dlg.Destroy()
	return backend
#==============================================================
# main
#==============================================================
if __name__ == "__main__":
	print "This module needs a test function!  please write it"
#==============================================================
# $Log: gmLogin.py,v $
# Revision 1.24  2005-09-27 20:44:59  ncq
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
