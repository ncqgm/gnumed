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
# $Id: gmGuiHelpers.py,v 1.14 2004-09-25 13:10:40 ncq Exp $
__version__ = "$Revision: 1.14 $"
__author__  = "K. Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL (details at http://www.gnu.org)"

import sys, string

if __name__ == '__main__':
	sys.exit("This is not intended to be run standalone !")

from wxPython.wx import *

from Gnumed.pycommon import gmLog
_log = gmLog.gmDefLog
_log.Log(gmLog.lData, __version__)

_set_status_text = None
# ========================================================================
def gm_show_error(aMessage = None, aTitle = None, aLogLevel = None):
	if aMessage is None:
		aMessage = _('programmer forgot to specify error message')

	if aLogLevel is not None:
		log_msg = string.replace(aMessage, '\015', ' ')
		log_msg = string.replace(log_msg, '\012', ' ')
		_log.Log(aLogLevel, log_msg)

	aMessage = str(aMessage) + _("\n\nPlease consult the error log for all the gory details !")

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
	return True
#-------------------------------------------------------------------------
def gm_show_info(aMessage = None, aTitle = None, aLogLevel = None):
	if aMessage is None:
		aMessage = _('programmer forgot to specify info message')

	if aLogLevel is not None:
		log_msg = string.replace(aMessage, '\015', ' ')
		log_msg = string.replace(log_msg, '\012', ' ')
		_log.Log(aLogLevel, log_msg)

	if aTitle is None:
		aTitle = _('generic info message dialog')

	dlg = wxMessageDialog (
		parent = NULL,
		message = aMessage,
		caption = aTitle,
		style = wxOK | wxICON_INFORMATION
	)
	dlg.ShowModal()
	dlg.Destroy()
	return True
#-------------------------------------------------------------------------
def gm_show_warning(aMessage = None, aTitle = None, aLogLevel = None):
	if aMessage is None:
		aMessage = _('programmer forgot to specify warning')

	if aLogLevel is not None:
		log_msg = string.replace(aMessage, '\015', ' ')
		log_msg = string.replace(log_msg, '\012', ' ')
		_log.Log(aLogLevel, log_msg)

	if aTitle is None:
		aTitle = _('generic warning message dialog')

	dlg = wxMessageDialog (
		parent = NULL,
		message = aMessage,
		caption = aTitle,
		style = wxOK | wxICON_EXCLAMATION
	)
	dlg.ShowModal()
	dlg.Destroy()
	return True
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
		return True
	else:
		return False
#-------------------------------------------------------------------------
def gm_beep_statustext(aMessage=None, aLogLevel=None):
	if aMessage is None:
		aMessage = _('programmer forgot to specify alert message')

	if aLogLevel is not None:
		log_msg = string.replace(aMessage, '\015', ' ')
		log_msg = string.replace(log_msg, '\012', ' ')
		_log.Log(aLogLevel, log_msg)

	wxBell()

	# only now and here can we assume that wxWindows
	# is sufficiently initialized
	global _set_status_text
	if _set_status_text is None:
		from Gnumed.pycommon import gmGuiBroker
		try:
			_set_status_text = gmGuiBroker.GuiBroker()['main.statustext']
		except KeyError:
			_log.LogException('called too early, cannot set status text')
			raise

	_set_status_text(aMessage)
	return 1
# ========================================================================
# $Log: gmGuiHelpers.py,v $
# Revision 1.14  2004-09-25 13:10:40  ncq
# - in gm_beep_statustext() make aMessage a defaulted keyword argument
#
# Revision 1.13  2004/08/19 13:56:51  ncq
# - added gm_show_warning()
#
# Revision 1.12  2004/08/18 10:18:42  ncq
# - added gm_show_info()
#
# Revision 1.11  2004/05/28 13:30:27  ncq
# - set_status_text -> _set_status_text so nobody
#   gets the idea to use it directly
#
# Revision 1.10  2004/05/26 23:23:35  shilbert
# - import statement fixed
#
# Revision 1.9  2004/04/11 10:10:56  ncq
# - cleanup
#
# Revision 1.8  2004/04/10 01:48:31  ihaywood
# can generate referral letters, output to xdvi at present
#
# Revision 1.7  2004/03/04 19:46:54  ncq
# - switch to package based import: from Gnumed.foo import bar
#
# Revision 1.6  2003/12/29 16:49:18  uid66147
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
