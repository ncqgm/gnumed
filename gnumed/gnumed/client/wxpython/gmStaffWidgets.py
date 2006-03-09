"""GNUmed staff management widgets.

This source code is protected by the GPL licensing scheme.
Details regarding the GPL are available at http://www.gnu.org
You may use and share it as long as you don't deny this right
to anybody else.
"""
#=========================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmStaffWidgets.py,v $
# $Id: gmStaffWidgets.py,v 1.1 2006-03-09 21:10:14 ncq Exp $
__version__ = "$Revision: 1.1 $"
__author__  = "K. Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL (details at http://www.gnu.org)"

try:
	import wxversion
	import wx
except ImportError:
	from wxPython import wx

from Gnumed.pycommon import gmLog
from Gnumed.business import gmPerson
from Gnumed.wxGladeWidgets import wxgAddPatientAsStaffDlg

_log = gmLog.gmDefLog
_log.Log(gmLog.lData, __version__)
#==========================================================================
class cAddPatientAsStaffDlg(wxgAddPatientAsStaffDlg.wxgAddPatientAsStaffDlg):

	def __init__(self, *args, **kwds):
		wxgAddPatientAsStaffDlg.wxgAddPatientAsStaffDlg.__init__(self, *args, **kwds)
		self.__init_ui_data()
	#--------------------------------------------------------
	# internal API
	#--------------------------------------------------------
	def __init_ui_data(self):
		pat = gmPerson.gmCurrentPatient()
		ident = pat.get_identity()
		name = ident.get_active_name()
		txt = _("""
  %s "%s" %s
  born: %s""") % (name['first'], name['preferred'], name['last'], ident['dob'].Format(_('%Y-%m-%d')))
		self._TXT_person.SetValue(txt)
		txt = name['first'][:2] + name['last'][:2]
		self._TXT_short_alias.SetValue(txt)
		self._TXT_account.SetValue(txt.lower())

#==========================================================================
# $Log: gmStaffWidgets.py,v $
# Revision 1.1  2006-03-09 21:10:14  ncq
# - simple wrapper around dialog to add current patient as staff member
#
#
