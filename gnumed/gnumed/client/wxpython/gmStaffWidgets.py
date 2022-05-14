"""GNUmed staff management widgets."""
#=========================================================================
__author__  = "K. Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL v2 or later (details at https://www.gnu.org)"

import logging
import sys


import wx


if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmMatchProvider
from Gnumed.business import gmPerson
from Gnumed.business import gmStaff
from Gnumed.wxpython import gmGuiHelpers
from Gnumed.wxpython import gmAuthWidgets
from Gnumed.wxpython import gmPhraseWheel


_log = logging.getLogger('gm.ui')

#==========================================================================
class cProviderPhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):

		gmPhraseWheel.cPhraseWheel.__init__ (
			self,
			*args,
			**kwargs
		)
		self.matcher = gmPerson.cMatchProvider_Provider()
		self.SetToolTip(_('Select a healthcare provider.'))
		self.selection_only = True

#==========================================================================
class cUserRolePRW(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):

		gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)

		items = [
			{'list_label': _('Public (no clinical or demographic access)'), 'field_label': _('public'), 'data': 'public access', 'weight': 1},
			{'list_label': _('Staff (demographic access only)'), 'field_label': _('staff (clerical)'), 'data': 'non-clinical access', 'weight': 1},
			{'list_label': _('full clinical access'), 'field_label': _('full clinical access'), 'data': 'full clinical access', 'weight': 1}
		]
		mp = gmMatchProvider.cMatchProvider_FixedList(items)
		mp.setThresholds(1, 2, 3)
		mp.word_separators = None
		#mp.ignored_chars = r"[.'\\(){}\[\]<>~#*$%^_=&@\t0123456789]+" + r'"'
		#self.SetToolTip(_('The preparation (form) of the substance or drug.'))
		self.matcher = mp
		self.selection_only = True

#==========================================================================
from Gnumed.wxGladeWidgets import wxgEditStaffListDlg

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
		staff_list = gmStaff.get_staff_list()
		pos = len(staff_list) + 1
		for staff in staff_list:
			row_num = self._LCTRL_staff.InsertItem(pos, label=staff['short_alias'])
			self._LCTRL_staff.SetItem(index = row_num, column = 1, label = staff['db_user'])
			self._LCTRL_staff.SetItem(index = row_num, column = 2, label = staff['l10n_role'])
			title = gmTools.coalesce(staff['title'], '')
			self._LCTRL_staff.SetItem(index = row_num, column = 3, label = '%s %s, %s' % (title, staff['lastnames'], staff['firstnames']))
			self._LCTRL_staff.SetItem(index = row_num, column = 4, label = gmTools.coalesce(staff['comment'], ''))
			self._LCTRL_staff.SetItem(index = row_num, column = 5, label = '%s / %s' % (lbl_active[bool(staff['is_active'])], lbl_login[bool(staff['can_login'])]))
			# color
			if staff['is_active'] and staff['can_login']:
				#self._LCTRL_staff.SetItemTextColour(row_num, wx.Colour('BLUE'))
				pass
			elif not staff['is_active'] and not staff['can_login']:
				self._LCTRL_staff.SetItemTextColour(row_num, wx.LIGHT_GREY)
			else:
				self._LCTRL_staff.SetItemTextColour(row_num, wx.Colour('RED'))
			# data
			self._LCTRL_staff.SetItemData(item = row_num, data = staff['pk_staff'])

		if len(staff_list) > 0:
			self._LCTRL_staff.SetColumnWidth(0, wx.LIST_AUTOSIZE)
			self._LCTRL_staff.SetColumnWidth(1, wx.LIST_AUTOSIZE_USEHEADER)
			self._LCTRL_staff.SetColumnWidth(2, wx.LIST_AUTOSIZE)
			self._LCTRL_staff.SetColumnWidth(3, wx.LIST_AUTOSIZE)
			self._LCTRL_staff.SetColumnWidth(4, wx.LIST_AUTOSIZE)
			self._LCTRL_staff.SetColumnWidth(5, wx.LIST_AUTOSIZE)

		# disable buttons
		self._btn_save.Enable(False)
		self._btn_delete.Enable(False)
		self._btn_deactivate.Enable(False)
		self._btn_activate.Enable(False)
		# clear editor
		self._TCTRL_name.SetValue('')
		self._TCTRL_alias.SetValue('')
		self._TCTRL_account.SetValue('')
		self._PRW_user_role.SetText(value = '', data = None)
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
		staff = gmStaff.cStaff(aPK_obj=pk_staff)
		self._TCTRL_name.SetValue('%s.%s %s' % (staff['title'], staff['firstnames'], staff['lastnames']))
		self._TCTRL_alias.SetValue(staff['short_alias'])
		self._TCTRL_account.SetValue(staff['db_user'])
		self._PRW_user_role.SetText(value = staff['l10n_role'], data = staff['role'], suppress_smarts = True)
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
		self._PRW_user_role.SetText(value = '', data = None)
		self._TCTRL_comment.SetValue('')
	#--------------------------------------------------------
	def _on_activate_button_pressed(self, evt):
		pk_staff = self._LCTRL_staff.GetItemData(self._LCTRL_staff.GetFirstSelected())
		conn = gmAuthWidgets.get_dbowner_connection(procedure = _('Activating GNUmed user.'))
		if conn is None:
			return False
		gmStaff.activate_staff(conn = conn, pk_staff = pk_staff)
		conn.close()
		self.__init_ui_data()
		return True
	#--------------------------------------------------------
	def _on_deactivate_button_pressed(self, evt):
		pk_staff = self._LCTRL_staff.GetItemData(self._LCTRL_staff.GetFirstSelected())
		conn = gmAuthWidgets.get_dbowner_connection(procedure = _('Deactivating GNUmed user.'))
		if conn is None:
			return False
		gmStaff.deactivate_staff(conn = conn, pk_staff = pk_staff)
		conn.close()
		self.__init_ui_data()
		return True
	#--------------------------------------------------------
	def _on_delete_button_pressed(self, event):
		pk_staff = self._LCTRL_staff.GetItemData(self._LCTRL_staff.GetFirstSelected())
		conn = gmAuthWidgets.get_dbowner_connection(procedure = _('Removing GNUmed user.'))
		if conn is None:
			return False
		success, msg = gmStaff.delete_staff(conn = conn, pk_staff = pk_staff)
		conn.close()
		self.__init_ui_data()
		if not success:
			gmGuiHelpers.gm_show_error(aMessage = msg, aTitle = _('Removing GNUmed user'))
			return False
		return True
	#--------------------------------------------------------
	def _on_save_button_pressed(self, event):
		pk_staff = self._LCTRL_staff.GetItemData(self._LCTRL_staff.GetFirstSelected())

		conn = gmAuthWidgets.get_dbowner_connection(procedure = _('Modifying GNUmed user.'))
		if conn is None:
			return False

		staff = gmStaff.cStaff(aPK_obj = pk_staff)
		staff['short_alias'] = self._TCTRL_alias.GetValue()
		staff['db_user'] = self._TCTRL_account.GetValue()
		staff['comment'] = self._TCTRL_comment.GetValue()
		success, data = staff.save_payload(conn = conn)
		if not success:
			conn.close()
			gmGuiHelpers.gm_show_error (
				aMessage = _('Failed to save changes to GNUmed database user.'),
				aTitle = _('Modifying GNUmed user')
			)
			return False

		target_role = self._PRW_user_role.GetData()
		if target_role is not None:
			if not staff.set_role(conn = conn, role = target_role):
				gmGuiHelpers.gm_show_error (
					aMessage = _('Failed to set role [%s] for GNUmed database user.') % self._PRW_user_role.GetValue().strip(),
					aTitle = _('Modifying GNUmed user')
				)

		conn.close()
		self.__init_ui_data()
		return True
#==========================================================================
from Gnumed.wxGladeWidgets import wxgAddPatientAsStaffDlg

class cAddPatientAsStaffDlg(wxgAddPatientAsStaffDlg.wxgAddPatientAsStaffDlg):

	def __init__(self, *args, **kwds):
		wxgAddPatientAsStaffDlg.wxgAddPatientAsStaffDlg.__init__(self, *args, **kwds)
		self.__init_ui_data()
	#--------------------------------------------------------
	# internal API
	#--------------------------------------------------------
	def __init_ui_data(self):
		pat = gmPerson.gmCurrentPatient()
		name = pat.get_active_name()
		txt = _("""
  %s "%s" %s
  born: %s""") % (
			name['firstnames'],
			name['preferred'],
			name['lastnames'],
			pat.get_formatted_dob(format = '%Y %b %d')
		)
		self._TXT_person.SetValue(txt)
		txt = name['firstnames'][:2] + name['lastnames'][:2]
		self._TXT_short_alias.SetValue(txt)
		self._TXT_account.SetValue(txt.casefold())
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
				aTitle = _('Adding GNUmed user')
			)
			self._TXT_password.SetValue('')
			self._TXT_password_again.SetValue('')
			return False

		if self._TXT_password.GetValue().strip() == '':
			really_wants_empty_password = gmGuiHelpers.gm_show_question (
				aMessage = _(
					'Are you positively sure you want to create\n'
					'a user with an empty password ?\n'
					'\n'
					'Think about the record access implications !'
				),
				aTitle = _('Adding GNUmed user')
			)
			if not really_wants_empty_password:
				return False

		# connect as "gm-dbo"
		conn = gmAuthWidgets.get_dbowner_connection (
			procedure = _('Enlisting person as user.'),
			dbo_password = gmTools.none_if(self._TXT_dbo_password.GetValue(), '')
		)
		if conn is None:
			return False

		# create new user
		success, msg = gmStaff.create_staff (
			conn = conn,
			db_account = self._TXT_account.GetValue(),
			password = self._TXT_password.GetValue(),
			identity = gmPerson.gmCurrentPatient().ID,
			short_alias = self._TXT_short_alias.GetValue().strip()
		)
		conn.close()
		if not success:
			gmGuiHelpers.gm_show_error(aMessage = msg, aTitle = _('Adding GNUmed user'))
			return False

		if self.IsModal():
			self.EndModal(wx.ID_OK)
		else:
			self.Close()

#==========================================================================
