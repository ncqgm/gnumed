#!/usr/bin/python
#############################################################################
#
# gmLogin - Display a login dialog and log onto backend(s)
# ---------------------------------------------------------------------------
#
# @author: Dr. Horst Herb
# @copyright: author
# @license: GPL (details at http://www.gnu.org)
# @dependencies: gmPG, gmLoginInfo
# @change log:
#	29.10.2001 hherb first draft, untested
#
# @TODO: testing
############################################################################

from wxPython.wx import *
import os.path
import gmLoginDialog, gmPG, gmGuiBroker, gmLog, gmExceptions

def Login(max_attempts=3):
	"""Display the login dialog and try to log into the backend up to max_attempts times
	Returns either a valid backend broker object if connection was succesful, or None."""

	logged_in = false
	attempts = 0
	backend = None
	#display the login dialog
	broker = gmGuiBroker.GuiBroker ()
	dlg = gmLoginDialog.LoginDialog(None, -1)
	dlg.Centre(wxBOTH)
	while not logged_in and attempts < max_attempts:
		dlg.ShowModal()
		#get the login parameters
		login = dlg.panel.GetLoginInfo()
		if login is None:
			#user cancelled
			dlg.Destroy()
			myLog.Log(gmLog.lInfo, "user cancelled login dialog")
			return None
		myLog.Log(gmLog.lInfo, "login attempt %s of %s" % (attempts, max_attempts))
		#now try to connect to the backend
		try:
			backend = gmPG.ConnectionPool(login)
			logged_in = true
			# save the login settings for next login
			dlg.panel.save_settings()
			myLog.Log(gmLog.lInfo, "backend connection successfully established")
		except gmExceptions.ConnectionError, e:
			attempts += 1
			exc = sys.exc_info()
			if attempts < max_attempts:
				myLog.LogException("backend connection failed", exc, fatal=0)
				wxMessageBox(_("Unable to connect to database.\n(%s)\n\nPlease retry or cancel" % e))
			else:
				myLog.LogException("backend connection failed", exc, fatal=1)

	dlg.Close()
	dlg.Destroy()
	return backend

#--------------------------------------------------------------
myLog = gmLog.gmDefLog

if __name__ == "__main__":
	_ = lambda x:x
	myLog.Log (gmLog.lWarn, "This module needs a test function!  please write it")
	print "This module needs a test function!  please write it"
