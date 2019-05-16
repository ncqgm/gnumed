"""GNUmed external patient care widgets."""
#================================================================
__author__ = "Karsten.Hilbert@gmx.net"
__license__ = "GPL v2 or later"

# std lib
import sys
import logging


# 3rd party
import wx


# GNUmed libs
if __name__ == '__main__':
	sys.path.insert(0, '../../')

from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmDispatcher

from Gnumed.business import gmExternalCare
from Gnumed.business import gmPerson

from Gnumed.wxpython import gmListWidgets
from Gnumed.wxpython import gmEditArea
from Gnumed.wxpython import gmGuiHelpers


_log = logging.getLogger('gm.ui')

#============================================================
def manage_external_care(parent=None):

	pat = gmPerson.gmCurrentPatient()
	emr = pat.emr

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	#-----------------------------------------
	def edit(external_care_item=None):
		return edit_external_care_item(parent = parent, external_care_item = external_care_item)

	#-----------------------------------------
	def delete(external_care_item=None):
		if gmExternalCare.delete_external_care_item(pk_external_care = external_care_item['pk_external_care']):
			return True

		gmDispatcher.send (
			signal = 'statustext',
			msg = _('Cannot delete external care item.'),
			beep = True
		)
		return False

	#------------------------------------------------------------
	def get_tooltip(data):
		if data is None:
			return None
		return '\n'.join(data.format(with_health_issue = True, with_address = True, with_comms = True))

	#------------------------------------------------------------
	def refresh(lctrl):
		care = emr.get_external_care_items(order_by = 'inactive, issue, provider, unit, organization')
		items = [ [
			'%s @ %s' % (
				c['unit'],
				c['organization']
			),
			gmTools.coalesce(c['provider'], ''),
			c['issue'],
			gmTools.bool2subst(c['inactive'], _('inactive'), '', '<ERROR: .inactive IS NULL>'),
			gmTools.coalesce(c['comment'], '')
		] for c in care ]
		lctrl.set_string_items(items)
		lctrl.set_data(care)

	#------------------------------------------------------------
	return gmListWidgets.get_choices_from_list (
		parent = parent,
		msg = _('External care of this patient.'),
		caption = _('Showing external care network.'),
		columns = [ _('Location'), _('Provider'), _('Reason for care'), _('Status'), _('Comment') ],
		single_selection = False,
		can_return_empty = True,
		ignore_OK_button = False,
		refresh_callback = refresh,
		edit_callback = edit,
		new_callback = edit,
		delete_callback = delete,
		list_tooltip_callback = get_tooltip
#		left_extra_button=None,		# manage orgs
#		middle_extra_button=None,	# manage issues
#		right_extra_button=None
	)

#----------------------------------------------------------------
def edit_external_care_item(parent=None, external_care_item=None, single_entry=True):
	ea = cExternalCareEAPnl(parent, -1)
	ea.data = external_care_item
	ea.mode = gmTools.coalesce(external_care_item, 'new', 'edit')
	dlg = gmEditArea.cGenericEditAreaDlg2(parent, -1, edit_area = ea, single_entry = single_entry)
	dlg.SetTitle(gmTools.coalesce(external_care_item, _('Adding external care'), _('Editing external care')))
	if dlg.ShowModal() == wx.ID_OK:
		dlg.DestroyLater()
		return True
	dlg.DestroyLater()
	return False

#====================================================================
from Gnumed.wxGladeWidgets import wxgExternalCareEAPnl

class cExternalCareEAPnl(wxgExternalCareEAPnl.wxgExternalCareEAPnl, gmEditArea.cGenericEditAreaMixin):

	def __init__(self, *args, **kwargs):

		try:
			data = kwargs['care']
			del kwargs['care']
		except KeyError:
			data = None

		wxgExternalCareEAPnl.wxgExternalCareEAPnl.__init__(self, *args, **kwargs)
		gmEditArea.cGenericEditAreaMixin.__init__(self)

		self.mode = 'new'
		self.data = data
		if data is not None:
			self.mode = 'edit'

		#self.__init_ui()
	#----------------------------------------------------------------
#	def __init_ui(self):
#		# adjust phrasewheels etc
	#----------------------------------------------------------------
	# generic Edit Area mixin API
	#----------------------------------------------------------------
	def _valid_for_save(self):
		validity = True

		if self._PRW_care_location.GetData() is None:
			validity = False
			self._PRW_care_location.display_as_valid(False)
			self.StatusText = _('No entry in field "Care Location".')
			self._PRW_care_location.SetFocus()
		else:
			self._PRW_care_location.display_as_valid(True)

		if self._PRW_issue.GetData() is not None:
			self._PRW_issue.display_as_valid(True)
		else:
			if self._PRW_issue.GetValue().strip() != '':
				self._PRW_issue.display_as_valid(True)
			else:
				validity = False
				self._PRW_issue.display_as_valid(False)
				self.StatusText = _('No entry in field [Care Target].')
				self._PRW_issue.SetFocus()

		return validity

	#----------------------------------------------------------------
	def _save_as_new(self):
		data = gmExternalCare.create_external_care_item (
			pk_encounter = gmPerson.gmCurrentPatient().emr.current_encounter['pk_encounter'],
			pk_health_issue = self._PRW_issue.GetData(),
			issue = self._PRW_issue.GetValue().strip(),
			pk_org_unit = self._PRW_care_location.GetData()
		)
		data['provider'] = self._TCTRL_provider.GetValue().strip()
		data['comment'] = self._TCTRL_comment.GetValue().strip()
		data['inactive'] = self._CHBOX_inactive.IsChecked()
		data.save()
		self.data = data
		return True

	#----------------------------------------------------------------
	def _save_as_update(self):
		self.data['pk_encounter'] = gmPerson.gmCurrentPatient().emr.current_encounter['pk_encounter']
		self.data['pk_health_issue'] = self._PRW_issue.GetData()
		self.data['issue'] = self._PRW_issue.GetValue().strip()
		self.data['pk_org_unit'] = self._PRW_care_location.GetData()
		self.data['provider'] = self._TCTRL_provider.GetValue().strip()
		self.data['comment'] = self._TCTRL_comment.GetValue().strip()
		self.data['inactive'] = self._CHBOX_inactive.IsChecked()
		self.data.save()
		return True

	#----------------------------------------------------------------
	def _refresh_as_new(self):
		self._PRW_issue.SetText('', None)
		self._PRW_care_location.SetText('', None)
		self._TCTRL_provider.SetValue('')
		self._TCTRL_comment.SetValue('')
		self._CHBOX_inactive.Value = False

		self._PRW_issue.SetFocus()

	#----------------------------------------------------------------
	def _refresh_as_new_from_existing(self):
		self._refresh_as_new()

	#----------------------------------------------------------------
	def _refresh_from_existing(self):
		self._PRW_issue.SetText(value = self.data['issue'], data = self.data['pk_health_issue'], suppress_smarts = True)
		self._PRW_care_location.SetText(value = '%s @ %s' % (self.data['unit'], self.data['organization']), data = self.data['pk_org_unit'])
		self._TCTRL_provider.SetValue(gmTools.coalesce(self.data['provider'], ''))
		self._TCTRL_comment.SetValue(gmTools.coalesce(self.data['comment'], ''))
		self._CHBOX_inactive.Value = self.data['inactive']

		self._TCTRL_comment.SetFocus()

#------------------------------------------------------------
class cExternalCareMgrPnl(gmListWidgets.cGenericListManagerPnl):
	"""A list for managing a patient's external care.

	Does NOT act on/listen to the current patient.
	"""
	def __init__(self, *args, **kwargs):

		try:
			self.__identity = kwargs['identity']
			del kwargs['identity']
		except KeyError:
			self.__identity = None

		gmListWidgets.cGenericListManagerPnl.__init__(self, *args, **kwargs)

		self.refresh_callback = self.refresh
		self.new_callback = self._add_care
		self.edit_callback = self._edit_care
		self.delete_callback = self._del_care

		self.__init_ui()
		self.refresh()
	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def refresh(self, *args, **kwargs):
		if self.__identity is None:
			self._LCTRL_items.set_string_items()
			return

		emr = self.__identity.emr
		care = emr.get_external_care_items(order_by = 'inactive, issue, provider, unit, organization')
		items = [ [
			'%s @ %s' % (
				c['unit'],
				c['organization']
			),
			gmTools.coalesce(c['provider'], ''),
			c['issue'],
			gmTools.bool2subst(c['inactive'], _('inactive'), '', '<ERROR: .inactive IS NULL>'),
			gmTools.coalesce(c['comment'], '')
		] for c in care ]
		self._LCTRL_items.set_string_items(items)
		self._LCTRL_items.set_column_widths()
		self._LCTRL_items.set_data(data = care)

	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def __init_ui(self):
		self._LCTRL_items.set_columns(columns = [
			_('Care location'),
			_('Provider'),
			_('Reason for care'),
			_('Status'),
			_('Comment')
		])

	#--------------------------------------------------------
	def _add_care(self):
		return edit_external_care_item(parent = self, external_care_item = None)

	#--------------------------------------------------------
	def _edit_care(self, external_care_item):
		return edit_external_care_item(parent = self, external_care_item = external_care_item)

	#--------------------------------------------------------
	def _del_care(self, external_care_item):
		go_ahead = gmGuiHelpers.gm_show_question (
			_(	'Do you really want to delete this\n'
				'external care entry from the patient ?'),
			_('Deleting external care entry')
		)
		if not go_ahead:
			return False
		if gmExternalCare.delete_external_care_item(pk_external_care = external_care_item['pk_external_care']):
			return True
		gmDispatcher.send (
			signal = 'statustext',
			msg = _('Cannot delete external care item.'),
			beep = True
		)
		return False

	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def _get_identity(self):
		return self.__identity

	def _set_identity(self, identity):
		self.__identity = identity
		self.refresh()

	identity = property(_get_identity, _set_identity)
#------------------------------------------------------------
