"""GnuMed GUI helper classes and functions

This module provides some convenient wxPython GUI
helper thingies that are widely used throughout
GnuMed.

This source code is protected by the GPL licensing scheme.
Details regarding the GPL are available at http://www.gnu.org
You may use and share it as long as you don't deny this right
to anybody else.
"""
# ========================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmGuiHelpers.py,v $
# $Id: gmGuiHelpers.py,v 1.4 2003-08-26 12:35:52 ncq Exp $
__version__ = "$Revision: 1.4 $"
__author__  = "K. Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL (details at http://www.gnu.org)"

import sys, string

if __name__ == '__main__':
	print "This is not intended to be run standalone !"
	sys.exit(-1)

from wxPython.wx import *

import gmLog
_log = gmLog.gmDefLog
_log.Log(gmLog.lData, __version__)
# ========================================================================
def gm_show_error(aMessage = None, aTitle = None, aLogLevel = None):
	if aMessage is None:
		aMessage = _('programmer forgot to specify error message')

	if aLogLevel is not None:
		log_msg = string.replace(aMessage, '\015', ' ')
		log_msg = string.replace(log_msg, '\012', ' ')
		_log.Log(aLogLevel, log_msg)

	aMessage = aMessage + _("\n\nPlease consult the error log for all the gory details !")

	if aTitle is None:
		aTitle = _('generic error message dialog')

	print aMessage
	print aTitle

	dlg = wxMessageDialog (
		parent = NULL,
		message = aMessage,
		caption = aTitle,
		style = wxOK | wxICON_ERROR
	)
	dlg.ShowModal()
	dlg.Destroy()
	return 1
#-------------------------------------------------------------------------
def gm_show_question(aMessage = None, aTitle = None):
	# sanity checks
	if aMessage is None:
		aMessage = _('programmer forgot to specify question')
	if aTitle is None:
		aTitle = _('generic user question dialog')

	dlg = wxMessageDialog(
		NULL,
		aMessage,
		aTitle,
		wxYES_NO | wxICON_QUESTION
	)
	btn_pressed = dlg.ShowModal()
	dlg.Destroy()

	if btn_pressed == wxID_YES:
		return 1
	else:
		return 0
# ========================================================================
# $Log: gmGuiHelpers.py,v $
# Revision 1.4  2003-08-26 12:35:52  ncq
# - properly replace \n\r
#
# Revision 1.3  2003/08/24 09:15:20  ncq
# - remove spurious self's
#
# Revision 1.2  2003/08/24 08:58:07  ncq
# - use gm_show_*
#
# Revision 1.1  2003/08/21 00:11:48  ncq
# - adds some widely used wxPython GUI helper functions
#
