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
# $Id: gmGuiHelpers.py,v 1.6 2003-12-29 16:49:18 uid66147 Exp $
__version__ = "$Revision: 1.6 $"
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

set_status_text = None
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

	print "-" * len(aTitle)
	print aTitle
	print "-" * len(aTitle)
	print aMessage

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
#-------------------------------------------------------------------------
def gm_beep_statustext(aMessage, aLogLevel = None):
	if aMessage is None:
		aMessage = _('programmer forgot to specify alert message')

	if aLogLevel is not None:
		log_msg = string.replace(aMessage, '\015', ' ')
		log_msg = string.replace(log_msg, '\012', ' ')
		_log.Log(aLogLevel, log_msg)

	wxBell()

	# only now and here can we assume that wxWindows
	# is sufficiently initialized
	global set_status_text
	if set_status_text is None:
		import gmGuiBroker as gb
		try:
			set_status_text = gb.GuiBroker()['main.statustext']
		except KeyError:
			_log.LogException('called too early, cannot set status text')
			raise

	set_status_text(aMessage)
	return 1
# ========================================================================
# $Log: gmGuiHelpers.py,v $
# Revision 1.6  2003-12-29 16:49:18  uid66147
# - cleanup, gm_beep_statustext()
#
# Revision 1.5  2003/11/17 10:56:38  sjtan
#
# synced and commiting.
#
# Revision 1.1  2003/10/23 06:02:39  sjtan
#
# manual edit areas modelled after r.terry's specs.
#
# Revision 1.4  2003/08/26 12:35:52  ncq
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
