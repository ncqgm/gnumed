"""GNUmed staff management widgets.

This source code is protected by the GPL licensing scheme.
Details regarding the GPL are available at http://www.gnu.org
You may use and share it as long as you don't deny this right
to anybody else.
"""
#=========================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmStaffWidgets.py,v $
# $Id: gmStaffWidgets.py,v 1.2 2006-03-14 21:31:15 ncq Exp $
__version__ = "$Revision: 1.2 $"
__author__  = "K. Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL (details at http://www.gnu.org)"

try:
	import wxversion
	import wx
except ImportError:
	from wxPython import wx

from Gnumed.pycommon import gmLog, gmPG
from Gnumed.business import gmPerson
from Gnumed.wxpython import gmGuiHelpers
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
	#--------------------------------------------------------
	# event handlers
	#--------------------------------------------------------
	def _on_cancel_button_pressed(self, evt):
		self.Close()
	#--------------------------------------------------------
	def _on_enlist_button_pressed(self, evt):
		# sanity checks
		if self._TXT_password.GetValue() != self._TXT_password_again.GetValue():
			gmGuiHelpers.gm_show_error (
				aMessage = _('Password entries do not match. Please type in the passwords again to rule out typos.'),
				aTitle = _('Adding GNUmed staff member')
			)
			self._TXT_password.SetValue('')
			self._TXT_password_again.SetValue('')
			return False
		# connect as "gm-dbo"
		pwd_gm_dbo = wx.GetPasswordFromUser (
			message = _(
"""
To add a new staff member to the database we
need the password of the GNUmed database owner.

Please enter the password for <gm-dbo>:"""),
			caption = _('Adding GNUmed staff member'),
			parent = self
		)
		pool = gmPG.ConnectionPool()
		conn = pool.get_connection_for_user(user='gm-dbo', password=pwd_gm_dbo, extra_verbose=True)
		if conn is None:
			gmGuiHelpers.gm_show_error (
				aMessage = _('Cannot connect as the GNUmed database user <gm-dbo>.\n\nTherefore cannot add new staff member.'),
				aTitle = _('Adding GNUmed staff member'),
				aLogLevel = gmLog.lErr
			)
			return False
		# create new user
		pat = gmPerson.gmCurrentPatient()
		queries = [
			# database account
			('select gm_create_user(%s, %s)', [self._TXT_account.GetValue(), self._TXT_password.GetValue()]),
			# staff entry
			('insert into dem.staff (fk_identity, fk_role, db_user, short_alias) values (%s, (select pk from dem.staff_role where name=\'doctor\'), %s, %s)', [pat.getID(), self._TXT_account.GetValue(), self._TXT_short_alias.GetValue()])
		]
		success, data = gmPG.run_commit2 (
			link_obj = conn,
			queries = queries,
			end_tx = True
		)
		if not success:
			gmGuiHelpers.gm_show_error (
				aMessage = _('Failed to create new GNUmed database user.\n\nTherefore cannot add new staff member.'),
				aTitle = _('Adding GNUmed staff member'),
				aLogLevel = gmLog.lErr
			)
			return False
		self.Close()
#==========================================================================
# $Log: gmStaffWidgets.py,v $
# Revision 1.2  2006-03-14 21:31:15  ncq
# - add event handlers for buttons
# - actually implement adding a new provider
#
# Revision 1.1  2006/03/09 21:10:14  ncq
# - simple wrapper around dialog to add current patient as staff member
#
