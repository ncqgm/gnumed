"""GNUmed staff management widgets.

This source code is protected by the GPL licensing scheme.
Details regarding the GPL are available at http://www.gnu.org
You may use and share it as long as you don't deny this right
to anybody else.
"""
#=========================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmStaffWidgets.py,v $
# $Id: gmStaffWidgets.py,v 1.4 2006-06-09 14:43:02 ncq Exp $
__version__ = "$Revision: 1.4 $"
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
from Gnumed.wxGladeWidgets import wxgAddPatientAsStaffDlg, wxgDelistStaffMemberDlg

_log = gmLog.gmDefLog
_log.Log(gmLog.lData, __version__)
#==========================================================================
class cDelistStaffMemberDlg(wxgDelistStaffMemberDlg.wxgDelistStaffMemberDlg):

	def __init__(self, *args, **kwds):
		wxgDelistStaffMemberDlg.wxgDelistStaffMemberDlg.__init__(self, *args, **kwds)
		self.__init_ui_data()
	#--------------------------------------------------------
	# internal API
	#--------------------------------------------------------
	def __init_ui_data(self):
		lbl_active = {True: _('active'), False: _('inactive')}
		lbl_login = {True: _('can login'), False: _('can not login')}

		self._LCTRL_staff.InsertColumn(0, _('Alias'))
		self._LCTRL_staff.InsertColumn(1, _('DB account'))
		self._LCTRL_staff.InsertColumn(2, _('Role'))
		self._LCTRL_staff.InsertColumn(3, _('Name'))
		self._LCTRL_staff.InsertColumn(4, _('Comment'))
		self._LCTRL_staff.InsertColumn(5, _('Status'))

		self._LCTRL_staff.DeleteAllItems()
		staff_list = gmPerson.get_staff_list()
		pos = len(staff_list) + 1
		for staff in staff_list:
			row_num = self._LCTRL_staff.InsertStringItem(pos, label=staff['short_alias'])
			self._LCTRL_staff.SetStringItem(index = row_num, col = 1, label = staff['db_user'])
			self._LCTRL_staff.SetStringItem(index = row_num, col = 2, label = staff['role'])
			self._LCTRL_staff.SetStringItem(index = row_num, col = 3, label = '%s %s, %s' % (staff['title'], staff['lastnames'], staff['firstnames']))
			self._LCTRL_staff.SetStringItem(index = row_num, col = 4, label = staff['comment'])
			self._LCTRL_staff.SetStringItem(index = row_num, col = 5, label = '%s / %s' % (lbl_active[bool(staff['is_active'])], lbl_login[bool(staff['can_login'])]))
			# color
			if staff['is_active'] and staff['can_login']:
				#self._LCTRL_staff.SetItemTextColour(row_num, col=wx.NamedColour('BLUE'))
				pass
			elif not staff['is_active'] and not staff['can_login']:
				self._LCTRL_staff.SetItemTextColour(row_num, col=wx.LIGHT_GREY)
			else:
				self._LCTRL_staff.SetItemTextColour(row_num, col=wx.NamedColour('RED'))
			# data
			self._LCTRL_staff.SetItemData(item = row_num, data = staff['pk_staff'])

		if len(staff_list) > 0:
			self._LCTRL_staff.SetColumnWidth(col=0, width=wx.LIST_AUTOSIZE)
			self._LCTRL_staff.SetColumnWidth(col=1, width=wx.LIST_AUTOSIZE_USEHEADER)
			self._LCTRL_staff.SetColumnWidth(col=2, width=wx.LIST_AUTOSIZE)
			self._LCTRL_staff.SetColumnWidth(col=3, width=wx.LIST_AUTOSIZE)
			self._LCTRL_staff.SetColumnWidth(col=4, width=wx.LIST_AUTOSIZE)
			self._LCTRL_staff.SetColumnWidth(col=5, width=wx.LIST_AUTOSIZE)

		self._btn_delete_staff.Enable(False)
	#--------------------------------------------------------
	def _on_listitem_selected(self, evt):
		self._btn_delete_staff.Enable(True)
	#--------------------------------------------------------
	def _on_listitem_deselected(self, evt):
		self._btn_delete_staff.Enable(False)
	#--------------------------------------------------------
	def _on_delist_button_pressed(self, evt):
		pk = self._LCTRL_staff.GetItemData(self._LCTRL_staff.GetFirstSelected())

		# 1) inactivate staff entry
		staff = gmPerson.cStaff(aPK_obj=pk)
		staff['is_active'] = False
		staff.save_payload()				# FIXME: error handling

		# 2) disable database account login
		# - get password for gm-dbo
		pwd_gm_dbo = wx.GetPasswordFromUser (
			message = _("""
To add a new staff member to the database we
need the password of the GNUmed database owner.

Please enter the password for <gm-dbo>:"""),
			caption = _('Delisting GNUmed staff member'),
			parent = self
		)
		# - connect as gm-dbo
		pool = gmPG.ConnectionPool()
		conn = pool.get_connection_for_user(user='gm-dbo', password=pwd_gm_dbo, extra_verbose=True)
		if conn is None:
			gmGuiHelpers.gm_show_error (
				aMessage = _('Cannot connect as the GNUmed database user <gm-dbo>.\n\nTherefore cannot disable staff member.'),
				aTitle = _('Disabling GNUmed staff member'),
				aLogLevel = gmLog.lErr
			)
			return False
		# - run disable query
		queries = [('select gm_disable_user(%s)', [staff['db_user']])]
		success, data = gmPG.run_commit2 (
			link_obj = conn,
			queries = queries,
			end_tx = True
		)
		if not success:
			gmGuiHelpers.gm_show_error (
				aMessage = _('Failed to disable GNUmed database user.'),
				aTitle = _('Disabling GNUmed staff member'),
				aLogLevel = gmLog.lErr
			)
			return False

		self.__init_ui_data()
		return True
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
# Revision 1.4  2006-06-09 14:43:02  ncq
# - improve staff member handling
#
# Revision 1.3  2006/06/06 20:54:36  ncq
# - add staff member delisting dialog
#
# Revision 1.2  2006/03/14 21:31:15  ncq
# - add event handlers for buttons
# - actually implement adding a new provider
#
# Revision 1.1  2006/03/09 21:10:14  ncq
# - simple wrapper around dialog to add current patient as staff member
#
