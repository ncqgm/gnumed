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
import gmLoginDialog, gmPG

# text translation function for localization purposes
import gettext
_ = gettext.gettext

def Login(max_attempts=3):
	"""Display the login dialog and try to log into the backend up to max_attempts times
	Returns either a valid backend broker object if connection was succesful, or None."""

	logged_in = false
	attempts = 0
	backend = None
	print "In Login()"
	#display the login dialog
	dlg = gmLoginDialog.LoginDialog(NULL, -1, png_bitmap = 'bitmaps/gnumedlogo.png')
	dlg.CenterOnScreen()
	while not logged_in and attempts< max_attempts:
		dlg.ShowModal()
		#get the login parameters
		login = dlg.panel.GetLoginInfo()
		if login is None:
			#user cancelled
			dlg.Destroy()
			return None
		#now try to connect to the backend
		backend = gmPG.ConnectionPool(login)
		if backend.Connected() is not None:
			logged_in = true
		else:
			attempts+=1
			if attempts < max_attempts:
				wxMessageBox(_("Login failed - please retry or cancel"))
		dlg.Close()
	dlg.Destroy()
	return backend


if __name__ == "__main__":
	print "This module needs a test function!  please write it"