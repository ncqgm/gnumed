#############################################################################
# gmLogin - Display a login dialog and log onto backend(s)
# ---------------------------------------------------------------------------
#
# @copyright: author
# @license: GPL (details at http://www.gnu.org)
# @dependencies: gmPG, gmLoginInfo
# @change log:
#	29.10.2001 hherb first draft, untested
#
# @TODO: testing
############################################################################
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/Attic/gmLogin.py,v $
# $Id: gmLogin.py,v 1.16 2003-06-26 21:40:29 ncq Exp $
__version__ = "$Revision: 1.16 $"
__author__ = "H.Herb"

from wxPython.wx import *
import os.path
import gmLoginDialog, gmPG, gmGuiBroker, gmLog, gmExceptions

_log = gmLog.gmDefLog
#==============================================================
def Login(max_attempts=3):
	"""Display the login dialog and try to log into the backend.

	- up to max_attempts times
	- returns either a valid backend broker object if connection
	  was succesful, or None.
	"""
	logged_in = false
	attempt = 0
	backend = None
	#display the login dialog
	broker = gmGuiBroker.GuiBroker ()
	dlg = gmLoginDialog.LoginDialog(None, -1)
	dlg.Centre(wxBOTH)
	while not logged_in and attempt < max_attempts:
		dlg.ShowModal()
		#get the login parameters
		login = dlg.panel.GetLoginInfo()
		if login is None:
			#user cancelled
			dlg.Destroy()
			_log.Log(gmLog.lInfo, "user cancelled login dialog")
			return None
		_log.Log(gmLog.lInfo, "login attempt %s of %s" % (attempt, max_attempts))
		#now try to connect to the backend
		try:
			backend = gmPG.ConnectionPool(login)
			logged_in = true
			# save the login settings for next login
			dlg.panel.save_settings()
			_log.Log(gmLog.lInfo, "backend connection successfully established")
		except gmExceptions.ConnectionError, e:
			attempt += 1
			if attempt < max_attempts:
				_log.LogException("backend connection failed", sys.exc_info(), verbose=0)
				wxMessageBox(_("Unable to connect to database.\n(%s)\n\nPlease retry or cancel") % e)
			else:
				_log.LogException("backend connection failed", sys.exc_info(), verbose=1)

	dlg.Close()
	dlg.Destroy()
	return backend
#==============================================================
# main
#==============================================================
if __name__ == "__main__":
	_ = lambda x:x
	_log.Log (gmLog.lWarn, "This module needs a test function!  please write it")
	print "This module needs a test function!  please write it"
#==============================================================
# $Log: gmLogin.py,v $
# Revision 1.16  2003-06-26 21:40:29  ncq
# - fatal->verbose
#
# Revision 1.15  2003/02/07 14:28:05  ncq
# - cleanup, cvs keywords
#
