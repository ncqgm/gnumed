"""GNUmed staff management widgets.

This source code is protected by the GPL licensing scheme.
Details regarding the GPL are available at http://www.gnu.org
You may use and share it as long as you don't deny this right
to anybody else.
"""
#=========================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmStaffWidgets.py,v $
# $Id: gmStaffWidgets.py,v 1.12 2006-11-24 14:23:41 ncq Exp $
__version__ = "$Revision: 1.12 $"
__author__  = "K. Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL (details at http://www.gnu.org)"

import wx

from Gnumed.pycommon import gmLog, gmPG2, gmTools
from Gnumed.business import gmPerson
from Gnumed.wxpython import gmGuiHelpers
from Gnumed.wxGladeWidgets import wxgAddPatientAsStaffDlg, wxgEditStaffListDlg

_log = gmLog.gmDefLog
_log.Log(gmLog.lData, __version__)
#==========================================================================
class cEditStaffListDlg(wxgEditStaffListDlg.wxgEditStaffListDlg):

	def __init__(self, *args, **kwds):
		wxgEditStaffListDlg.wxgEditStaffListDlg.__init__(self, *args, **kwds)

		self._LCTRL_staff.InsertColumn(0, _('Alias'))
		self._LCTRL_staff.InsertColumn(1, _('DB account'))
		self._LCTRL_staff.InsertColumn(2, _('Role'))
		self._LCTRL_staff.InsertColumn(3, _('Name'))
		self._LCTRL_staff.InsertColumn(4, _('Comment'))
		self._LCTRL_staff.InsertColumn(5, _('Status'))

		self.__init_ui_data()
	#--------------------------------------------------------
	# internal API
	#--------------------------------------------------------
	def __init_ui_data(self):
		lbl_active = {True: _('active'), False: _('inactive')}
		lbl_login = {True: _('can login'), False: _('can not login')}

		self._LCTRL_staff.DeleteAllItems()
		staff_list = gmPerson.get_staff_list()
		pos = len(staff_list) + 1
		for staff in staff_list:
			row_num = self._LCTRL_staff.InsertStringItem(pos, label=staff['short_alias'])
			self._LCTRL_staff.SetStringItem(index = row_num, col = 1, label = staff['db_user'])
			self._LCTRL_staff.SetStringItem(index = row_num, col = 2, label = staff['role'])
			title = gmTools.coalesce(staff['title'], '')
			self._LCTRL_staff.SetStringItem(index = row_num, col = 3, label = '%s %s, %s' % (title, staff['lastnames'], staff['firstnames']))
			self._LCTRL_staff.SetStringItem(index = row_num, col = 4, label = gmTools.coalesce(staff['comment'], ''))
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

		# disable buttons
		self._btn_save.Enable(False)
		self._btn_delete.Enable(False)
		self._btn_deactivate.Enable(False)
		self._btn_activate.Enable(False)
		# clear editor
		self._TCTRL_name.SetValue('')
		self._TCTRL_alias.SetValue('')
		self._TCTRL_account.SetValue('')
		self._TCTRL_comment.SetValue('')
	#--------------------------------------------------------
	# event handlers
	#--------------------------------------------------------
	def _on_listitem_selected(self, evt):
		self._btn_save.Enable(True)
		self._btn_delete.Enable(True)
		self._btn_deactivate.Enable(True)
		self._btn_activate.Enable(True)
		# fill editor
		pk_staff = self._LCTRL_staff.GetItemData(self._LCTRL_staff.GetFirstSelected())
		staff = gmPerson.cStaff(aPK_obj=pk_staff)
		self._TCTRL_name.SetValue('%s.%s %s' % (staff['title'], staff['firstnames'], staff['lastnames']))
		self._TCTRL_alias.SetValue(staff['short_alias'])
		self._TCTRL_account.SetValue(staff['db_user'])
		self._TCTRL_comment.SetValue(gmTools.coalesce(staff['comment'], ''))
	#--------------------------------------------------------
	def _on_listitem_deselected(self, evt):
		self._btn_save.Enable(False)
		self._btn_delete.Enable(False)
		self._btn_deactivate.Enable(False)
		self._btn_activate.Enable(False)
		# clear editor
		self._TCTRL_name.SetValue('')
		self._TCTRL_alias.SetValue('')
		self._TCTRL_account.SetValue('')
		self._TCTRL_comment.SetValue('')
	#--------------------------------------------------------
	def _on_activate_button_pressed(self, evt):
		pk_staff = self._LCTRL_staff.GetItemData(self._LCTRL_staff.GetFirstSelected())

		conn = gmGuiHelpers.get_dbowner_connection(procedure = _('Activating GNUmed staff member.'))
		if conn is None:
			return False

		# 1) activate staff entry
		staff = gmPerson.cStaff(aPK_obj=pk_staff)
		staff['is_active'] = True
		staff.save_payload(conn=conn)				# FIXME: error handling

		# 2) enable database account login
		rowx, idx = gmPG2.run_rw_queries (
			link_obj = conn,
			queries = [{'cmd': u'select gm_create_user(%s, %s)', 'args': [staff['db_user'], 'flying wombat']}],
			end_tx = True
		)
		conn.close()
		self.__init_ui_data()
		return True
	#--------------------------------------------------------
	def _on_deactivate_button_pressed(self, evt):
		pk_staff = self._LCTRL_staff.GetItemData(self._LCTRL_staff.GetFirstSelected())

		conn = gmGuiHelpers.get_dbowner_connection(procedure = _('Deactivating GNUmed staff member.'))
		if conn is None:
			return False

		# 1) inactivate staff entry
		staff = gmPerson.cStaff(aPK_obj=pk_staff)
		staff['is_active'] = False
		staff.save_payload(conn=conn)				# FIXME: error handling

		# 2) disable database account login
		rows, idx = gmPG2.run_rw_queries (
			link_obj = conn,
			queries = [{'cmd': u'select gm_disable_user(%s)', 'args': [staff['db_user']]}],
			end_tx = True
		)
		conn.close()
		self.__init_ui_data()
		return True
	#--------------------------------------------------------
#	def _on_delete_button_pressed(self, event):
	#--------------------------------------------------------
	def _on_save_button_pressed(self, event):
		pk_staff = self._LCTRL_staff.GetItemData(self._LCTRL_staff.GetFirstSelected())

		conn = gmGuiHelpers.get_dbowner_connection(procedure = _('Modifying GNUmed staff member.'))
		if conn is None:
			return False

		staff = gmPerson.cStaff(aPK_obj=pk_staff)
		staff['short_alias'] = self._TCTRL_alias.GetValue()
		staff['db_user'] = self._TCTRL_account.GetValue()
		staff['comment'] = self._TCTRL_comment.GetValue()
		success, data = staff.save_payload(conn=conn)
		conn.close()
		if not success:
			gmGuiHelpers.gm_show_error (
				aMessage = _('Failed to save changes to GNUmed database user.'),
				aTitle = _('Modifying GNUmed staff member'),
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
  born: %s""") % (name['first'], name['preferred'], name['last'], ident['dob'].strftime(_('%Y-%m-%d')))
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
		conn = gmGuiHelpers.get_dbowner_connection(procedure = _('Enlisting Patient as Staff.'))
		if conn is None:
			return False

		# create new user
		pat = gmPerson.gmCurrentPatient()
		queries = [
			# database account
			{'cmd': u'select gm_create_user(%s, %s)', 'args': [self._TXT_account.GetValue(), self._TXT_password.GetValue()]},
			# staff entry
			{'cmd': u"insert into dem.staff (fk_identity, fk_role, db_user, short_alias) values (%s, (select pk from dem.staff_role where name='doctor'), %s, %s)", 'args': [pat.getID(), self._TXT_account.GetValue(), self._TXT_short_alias.GetValue()]}
		]
		rows, idx = gmPG2.run_rw_queries(link_obj = conn, queries = queries, end_tx = True)
		if self.IsModal():
			self.EndModal(wx.ID_OK)
		else:
			self.Close()
#==========================================================================
# $Log: gmStaffWidgets.py,v $
# Revision 1.12  2006-11-24 14:23:41  ncq
# - EndModal() needs wx.ID_*
#
# Revision 1.11  2006/10/31 13:30:27  ncq
# - use gmPG2
#
# Revision 1.10  2006/10/25 07:46:44  ncq
# - Format() -> strftime() since datetime.datetime does not have .Format()
#
# Revision 1.9  2006/10/25 07:21:57  ncq
# - no more gmPG
#
# Revision 1.8  2006/09/03 11:32:10  ncq
# - clean up wx import
# - use gmTools.coalesce()
# - use gmGuiHelpers.get_dbowner_connection instead of local crap copy
#
# Revision 1.7  2006/06/17 16:45:19  ncq
# - only insert column labels once
# - use get_dbowner_connection() in gmGuiHelpers
# - implement activate()/save() on staff details
#
# Revision 1.6  2006/06/15 20:57:49  ncq
# - actually do something with the improved staff list editor
#
# Revision 1.5  2006/06/10 05:13:06  ncq
# - improved "edit staff list"
#
# Revision 1.4  2006/06/09 14:43:02  ncq
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
