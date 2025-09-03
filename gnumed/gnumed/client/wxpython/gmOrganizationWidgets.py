"""GNUmed organization handling widgets.

copyright: authors
"""
#============================================================
__author__ = "K.Hilbert"
__license__ = "GPL v2 or later (details at https://www.gnu.org)"

import logging
import sys


import wx


if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x

from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmMatchProvider
from Gnumed.pycommon import gmDispatcher

from Gnumed.business import gmOrganization

from Gnumed.wxpython import gmListWidgets
from Gnumed.wxpython import gmEditArea
from Gnumed.wxpython import gmPhraseWheel
from Gnumed.wxpython import gmAddressWidgets
from Gnumed.wxpython import gmGuiHelpers
from Gnumed.wxpython.gmDemographicsWidgets import cExternalIDEditAreaPnl


_log = logging.getLogger('gm.organization')

#============================================================
# organizational units API
#------------------------------------------------------------
def edit_org_unit(parent=None, org_unit=None, single_entry=False, org=None):
	ea = cOrgUnitEAPnl(parent, -1)
	ea.data = org_unit
	ea.mode = gmTools.coalesce(org_unit, 'new', 'edit')
	dlg = gmEditArea.cGenericEditAreaDlg2(parent, -1, edit_area = ea, single_entry = single_entry)
	if org is not None:
		ea.organization = org
	dlg.SetTitle(gmTools.coalesce(org_unit, _('Adding new organizational unit'), _('Editing organizational unit')))
	if dlg.ShowModal() == wx.ID_OK:
		dlg.DestroyLater()
		return True
	dlg.DestroyLater()
	return False

#============================================================
def select_org_unit(parent=None, msg=None, no_parent=False):

	if no_parent:
		parent = None
	else:
		if parent is None:
			parent = wx.GetApp().GetTopWindow()

	#--------------------
	def new():
		manage_orgs(parent = parent, no_parent = no_parent)
		return True
	#--------------------
	def refresh(lctrl):
		units = gmOrganization.get_org_units(order_by = 'organization, unit, l10n_unit_category')
		items = [ [
			u['organization'],
			u['unit'],
			gmTools.coalesce(u['l10n_unit_category'], ''),
			u['pk_org_unit']
		] for u in units ]

		lctrl.set_string_items(items = items)
		lctrl.set_data(data = units)
	#--------------------
	if msg is None:
		msg = _("Organizations and units thereof.\n")

	return gmListWidgets.get_choices_from_list (
		parent = parent,
		msg = msg,
		caption = _('Unit selection ...'),
		columns = [_('Organization'), _('Unit'), _('Unit type'), '#'],
		can_return_empty = False,
		single_selection = True,
		refresh_callback = refresh,
		new_callback = new
	)

#============================================================
class cOrgUnitPhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):
		query = """
	SELECT DISTINCT ON (data) * FROM (
		SELECT * FROM ((

			SELECT
				pk_org_unit
					AS data,
				unit || coalesce(' (' || l10n_unit_category || ')', '') || ': ' || organization || ' (' || l10n_organization_category || ')'
					AS list_label,
				unit || ' (' || organization || ')'
					AS field_label
			FROM
				dem.v_org_units
			WHERE
				unit %(fragment_condition)s

		) UNION ALL (

			SELECT
				pk_org_unit
					AS data,
				coalesce(l10n_unit_category || ' ', '') || '"' || unit || '": ' || organization || ' (' || l10n_organization_category || ')'
					AS list_label,
				unit || ' (' || organization || ')'
					AS field_label
			FROM
				dem.v_org_units
			WHERE
				l10n_unit_category %(fragment_condition)s
					OR
				unit_category %(fragment_condition)s

		) UNION ALL (

			SELECT
				pk_org_unit
					AS data,
				organization || ': ' || unit || coalesce(' (' || l10n_unit_category || ')', '')
					AS list_label,
				unit || ' (' || organization || ')'
					AS field_label
			FROM
				dem.v_org_units
			WHERE
				organization %(fragment_condition)s

		)) AS all_matches
		ORDER BY list_label
	) AS ordered_matches
	LIMIT 50
		"""
		mp = gmMatchProvider.cMatchProvider_SQL2(queries=query)
		mp.setThresholds(1, 3, 5)
		gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)
		self.SetToolTip(_("Select an organizational unit."))
		self.matcher = mp
		self.picklist_delay = 300
	#--------------------------------------------------------
	def _get_data_tooltip(self):
		if self.GetData() is None:
			return None
		unit = self._data2instance()
		if unit is None:
			return None
		return '\n'.join(unit.format(with_address = True))
	#--------------------------------------------------------
	def _data2instance(self, link_obj=None):
		if self.GetData() is None:
			return None
		return gmOrganization.cOrgUnit(aPK_obj = self.GetData())

#============================================================
class cOrgUnitsManagerPnl(gmListWidgets.cGenericListManagerPnl):
	"""A list for managing organizational units."""

	def __init__(self, *args, **kwargs):

		try:
			self.__org = kwargs['org']
			del kwargs['org']
		except KeyError:
			self.__org = None

		gmListWidgets.cGenericListManagerPnl.__init__(self, *args, **kwargs)

		self.refresh_callback = self.refresh
		self.new_callback = self._add
		self.edit_callback = self._edit
		self.delete_callback = self._del

		self.__show_none_if_no_org = True
		self.__init_ui()
		self.__refresh()
	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def refresh(self, lctrl=None):
		self.__refresh()
	#--------------------------------------------------------
	# event handlers
	#--------------------------------------------------------
	def _add(self):
		return edit_org_unit(parent = self, org_unit = None, single_entry = False, org = self.__org)
	#--------------------------------------------------------
	def _edit(self, item):
		return edit_org_unit(parent = self, org_unit = item, single_entry = True)
	#--------------------------------------------------------
	def _del(self, item):
		return gmOrganization.delete_org_unit(unit = item['pk_org_unit'])
	#--------------------------------------------------------
	def _on_list_item_focused(self, event):
		pass
	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def __init_ui(self):
		self._LCTRL_items.set_columns(columns = [ _('Organizational Unit'), _('Unit Category'), '#' ])
		self._LCTRL_items.SetToolTip(_('Units (sites, parts, departments, branches, ...) of organizations registered in GNUmed.'))
		self._LCTRL_items.item_tooltip_callback = self.get_tooltip
		#self._LCTRL_items.set_column_widths(widths = [wx.LIST_AUTOSIZE, wx.LIST_AUTOSIZE, wx.LIST_AUTOSIZE])
	#--------------------------------------------------------
	def get_tooltip(self, unit):
		if unit is None:
			return _('Units (sites, parts, departments, branches, ...) of organizations registered in GNUmed.')
		return '\n'.join(unit.format(with_address = True, with_org = True, with_comms = True))
	#--------------------------------------------------------
	def __refresh(self):

		msg_template = _('Units of: %s')

		if self.__org is None:
			self._BTN_add.Enable(False)
			self._BTN_edit.Enable(False)
			self._BTN_remove.Enable(False)
			pk = None
			self.message = msg_template % _('<no organization selected>')
			if self.__show_none_if_no_org:
				self._LCTRL_items.set_string_items(items = None)
				return
		else:
			self._BTN_add.Enable(True)
			pk = self.__org['pk_org']
			org_str = '%s (%s)' % (
				self.__org['organization'],
				self.__org['l10n_category']
			)
			self.message = msg_template % org_str

		units = gmOrganization.get_org_units(order_by = 'unit, l10n_unit_category', org = pk)
		items = [ [
			u['unit'],
			gmTools.coalesce(u['l10n_unit_category'], ''),
			u['pk_org_unit']
		] for u in units ]

		self._LCTRL_items.set_string_items(items)
		self._LCTRL_items.set_column_widths(widths = [wx.LIST_AUTOSIZE, wx.LIST_AUTOSIZE, wx.LIST_AUTOSIZE])
		self._LCTRL_items.set_data(units)

		for idx in range(len(units)):
			unit = units[idx]
			if unit['is_praxis_branch']:
				self._LCTRL_items.SetItemTextColour(idx, wx.Colour('RED'))
	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def _get_org(self):
		return self.__org

	def _set_org(self, org):
		self.__org = org
		self.__refresh()

	org = property(_get_org, _set_org)
	#--------------------------------------------------------
	def _get_show_none_if_no_org(self):
		return self.__show_none_if_no_org

	def _set_show_none_if_no_org(self, show_none_if_no_org):
		if show_none_if_no_org == self.__show_none_if_no_org:
			return
		if show_none_if_no_org:
			self.__show_none_if_no_org = True
		else:
			self.__show_none_if_no_org = False
		self.__refresh()

	show_none_if_no_org = property(_get_show_none_if_no_org, _set_show_none_if_no_org)

#============================================================
# org unit edit area
from Gnumed.wxGladeWidgets import wxgOrgUnitEAPnl

class cOrgUnitEAPnl(wxgOrgUnitEAPnl.wxgOrgUnitEAPnl, gmEditArea.cGenericEditAreaMixin):

	def __init__(self, *args, **kwargs):

		try:
			data = kwargs['unit']
			del kwargs['unit']
		except KeyError:
			data = None

		wxgOrgUnitEAPnl.wxgOrgUnitEAPnl.__init__(self, *args, **kwargs)
		gmEditArea.cGenericEditAreaMixin.__init__(self)

		self.mode = 'new'
		self.data = data
		if data is not None:
			self.mode = 'edit'

#		self.__init_ui()
	#----------------------------------------------------------------
#	def __init_ui(self):
#		pass
	#----------------------------------------------------------------
	# generic Edit Area mixin API
	#----------------------------------------------------------------
	def _valid_for_save(self):
		validity = True

		if self._PRW_category.GetData() is not None:
			self._PRW_category.display_as_valid(True)
		else:
			if self._PRW_category.GetValue().strip() == '':
				self._PRW_category.display_as_valid(True)
			else:
				validity = False
				self._PRW_category.display_as_valid(False)
				self._PRW_category.SetFocus()

		if self._PRW_unit.GetData() is not None:
			self._PRW_unit.display_as_valid(True)
		else:
			if self._PRW_unit.GetValue().strip() != '':
				self._PRW_unit.display_as_valid(True)
			else:
				validity = False
				self._PRW_unit.display_as_valid(False)
				self._PRW_unit.SetFocus()

		if self._PRW_org.GetData() is None:
			validity = False
			self._PRW_org.display_as_valid(False)
			self._PRW_org.SetFocus()
		else:
			self._PRW_org.display_as_valid(True)

		return validity
	#----------------------------------------------------------------
	def _save_as_new(self):
		data = gmOrganization.create_org_unit (
			pk_organization = self._PRW_org.GetData(),
			unit = self._PRW_unit.GetValue().strip()
		)
		data['pk_category_unit'] = self._PRW_category.GetData()
		data.save()

		self.data = data
		return True
	#----------------------------------------------------------------
	def _save_as_update(self):
		self.data['pk_org'] = self._PRW_org.GetData()
		self.data['unit'] = self._PRW_unit.GetValue().strip()
		self.data['pk_category_unit'] = self._PRW_category.GetData()
		self.data.save()
		return True
	#----------------------------------------------------------------
	def _refresh_as_new(self):
		self._PRW_org.SetText(value = '', data = None)
		self._PRW_unit.SetText(value = '', data = None)
		self._PRW_category.SetText(value = '', data = None)

		self._PRW_unit.SetFocus()
	#----------------------------------------------------------------
	def _refresh_as_new_from_existing(self):
		self._PRW_org.SetText(value = self.data['organization'], data = self.data['pk_org'])
		self._PRW_unit.SetText(value = '', data = None)
		self._PRW_category.SetText(value = self.data['unit_category'], data = self.data['pk_category_unit'])

		self._PRW_unit.SetFocus()
	#----------------------------------------------------------------
	def _refresh_from_existing(self):
		self._PRW_org.SetText(value = self.data['organization'], data = self.data['pk_org'])
		self._PRW_unit.SetText(value = self.data['unit'], data = self.data['pk_org_unit'])
		self._PRW_category.SetText(value = self.data['unit_category'], data = self.data['pk_category_unit'])

		self._PRW_unit.SetFocus()
	#----------------------------------------------------------------
	def _set_org(self, org):
		self._PRW_org.SetText(value = org['organization'], data = org['pk_org'])

	organization = property(lambda x:x, _set_org)

#============================================================
from Gnumed.wxGladeWidgets import wxgOrgUnitAddressPnl

class cOrgUnitAddressPnl(wxgOrgUnitAddressPnl.wxgOrgUnitAddressPnl):

	def __init__(self, *args, **kwargs):

		wxgOrgUnitAddressPnl.wxgOrgUnitAddressPnl.__init__(self, *args, **kwargs)

		self.__unit = None
	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def __refresh(self):
		if self.__unit is None:
			self.message = _('<no unit selected>')
			self._PRW_address_searcher.SetText('', None)
			self._PRW_address_searcher.Enable(False)
			self._BTN_save_picked_address.Enable(False)
			self._BTN_add_new_address.Enable(False)
		else:
			if self.__unit['l10n_unit_category'] is None:
				cat = ''
				left_delim = ''
				right_delim = ''
			else:
				cat = '%s ' % self.__unit['l10n_unit_category']
				left_delim = gmTools.u_left_double_angle_quote
				right_delim = gmTools.u_right_double_angle_quote
			self.message = '%s%s%s%s' % (
				cat,
				left_delim,
				self.__unit['unit'],
				right_delim
			)
			self._PRW_address_searcher.Enable(True)
			self._PRW_address_searcher.address = self.__unit['pk_address']
			self._PRW_address_searcher.Enable(True)
			self._BTN_save_picked_address.Enable(True)
			self._BTN_add_new_address.Enable(True)
	#--------------------------------------------------------
	# event handlers
	#--------------------------------------------------------
	def _on_save_picked_address_button_pressed(self, event):
		if self._PRW_address_searcher.GetData() is None:
			if self._PRW_address_searcher.GetValue().strip() != '':
				gmDispatcher.send(signal = 'statustext', msg = _('Invalid address selection.'))
				self._PRW_address_searcher.display_as_valid(False)
				self._PRW_address_searcher.SetFocus()
				return

		self._PRW_address_searcher.display_as_valid(True)

		self.__unit['pk_address'] = self._PRW_address_searcher.GetData()
		self.__unit.save()
		self.__refresh()
	#--------------------------------------------------------
	def _on_add_new_address_button_pressed(self, event):
		ea = gmAddressWidgets.cAddressEAPnl(self, -1)
		ea.address_holder = self.__unit
		ea.type_is_editable = False
		dlg = gmEditArea.cGenericEditAreaDlg2(self, -1, edit_area = ea)
		dlg.SetTitle(_('Adding new address'))
		if dlg.ShowModal() != wx.ID_OK:
			return False
		self.__refresh()
		return True
	#--------------------------------------------------------
	def _on_manage_addresses_button_pressed(self, event):
		picked_address = gmAddressWidgets.manage_addresses(parent = self)
		if picked_address is None:
			return

		question = '%s\n\n  %s\n' % (
			_('Link the following address to the organizational unit ?'),
			'\n  '.join(picked_address.format())
		)

		link_it = gmGuiHelpers.gm_show_question (
			title = _('Linking selected address'),
			question = question
		)
		if not link_it:
			return

		self._PRW_address_searcher.address = picked_address['pk_address']
		self._PRW_address_searcher.display_as_valid(True)
		self.__unit['pk_address'] = self._PRW_address_searcher.GetData()
		self.__unit.save()
	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def _get_unit(self):
		return self.__unit

	def _set_unit(self, unit):
		self.__unit = unit
		self.__refresh()

	unit = property(_get_unit, _set_unit)
	#--------------------------------------------------------
	def _get_message(self):
		return self._LBL_message.GetLabel()

	def _set_message(self, msg):
		if msg is None:
			self._LBL_message.Hide()
			self._LBL_message.SetLabel('')
		else:
			self._LBL_message.SetLabel(msg)
			self._LBL_message.Show()
		self.Layout()

	message = property(_get_message, _set_message)

#============================================================
class cOrgUnitIDsMgrPnl(gmListWidgets.cGenericListManagerPnl):
	"""A list for managing an org unit's external IDs.

	Does NOT act on/listen to the current patient.
	"""
	def __init__(self, *args, **kwargs):

		try:
			self.__unit = kwargs['unit']
			del kwargs['unit']
		except KeyError:
			self.__unit = None

		gmListWidgets.cGenericListManagerPnl.__init__(self, *args, **kwargs)

		self.refresh_callback = self.refresh
		self.new_callback = self._add_id
		self.edit_callback = self._edit_id
		self.delete_callback = self._del_id

		self.__init_ui()
		self.refresh()
	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def refresh(self, *args, **kwargs):
		if self.__unit is None:
			self._LCTRL_items.set_string_items()
			return

		ids = self.__unit.external_ids
		self._LCTRL_items.set_string_items (
			items = [ [
					i['name'],
					i['value'],
					gmTools.coalesce(i['issuer'], ''),
					gmTools.coalesce(i['comment'], '')
				] for i in ids
			]
		)
		self._LCTRL_items.set_column_widths()
		self._LCTRL_items.set_data(data = ids)
	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def __init_ui(self):
		self._LCTRL_items.set_columns(columns = [
			_('ID Type'),
			_('Value'),
			_('Issuer'),
			_('Comment')
		])
	#--------------------------------------------------------
	def _add_id(self):
		ea = cExternalIDEditAreaPnl(self, -1)
		ea.id_holder = self.__unit
		dlg = gmEditArea.cGenericEditAreaDlg2(self, -1, edit_area = ea)
		dlg.SetTitle(_('Adding new external ID'))
		if dlg.ShowModal() == wx.ID_OK:
			dlg.DestroyLater()
			return True
		dlg.DestroyLater()
		return False
	#--------------------------------------------------------
	def _edit_id(self, ext_id):
		ea = cExternalIDEditAreaPnl(self, -1, external_id = ext_id)
		ea.id_holder = self.__unit
		dlg = gmEditArea.cGenericEditAreaDlg2(self, -1, edit_area = ea, single_entry = True)
		dlg.SetTitle(_('Editing external ID'))
		if dlg.ShowModal() == wx.ID_OK:
			dlg.DestroyLater()
			return True
		dlg.DestroyLater()
		return False
	#--------------------------------------------------------
	def _del_id(self, ext_id):
		go_ahead = gmGuiHelpers.gm_show_question (
			_(	'Do you really want to delete this\n'
				'external ID from the organizational unit ?'),
			_('Deleting external ID')
		)
		if not go_ahead:
			return False
		self.__unit.delete_external_id(pk_ext_id = ext_id['pk_id'])
		return True
	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def _get_org_unit(self):
		return self.__unit

	def _set_org_unit(self, org_unit):
		self.__unit = org_unit
		self.refresh()

	org_unit = property(_get_org_unit, _set_org_unit)

#============================================================
# organizations API
#------------------------------------------------------------
def manage_orgs(parent=None, no_parent=False):

	if no_parent:
		parent = None
	else:
		if parent is None:
			parent = wx.GetApp().GetTopWindow()

	dlg = cOrganizationManagerDlg(parent, -1)
	dlg.ShowModal()
	dlg.DestroyLater()
#============================================================
def edit_org(parent=None, org=None, single_entry=False):
	ea = cOrganizationEAPnl(parent, -1)
	ea.data = org
	ea.mode = gmTools.coalesce(org, 'new', 'edit')
	dlg = gmEditArea.cGenericEditAreaDlg2(parent, -1, edit_area = ea, single_entry = single_entry)
	dlg.SetTitle(gmTools.coalesce(org, _('Adding new organization'), _('Editing organization')))
	if dlg.ShowModal() == wx.ID_OK:
		dlg.DestroyLater()
		return True
	dlg.DestroyLater()
	return False
#============================================================
class cOrganizationPhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):
		query = """
	SELECT DISTINCT ON (data) * FROM (
		SELECT * FROM ((

			SELECT
				pk_org
					AS data,
				organization || ' (' || l10n_category || ')'
					AS list_label,
				organization || ' (' || l10n_category || ')'
					AS field_label
			FROM
				dem.v_orgs
			WHERE
				organization %(fragment_condition)s

		) UNION ALL (

			SELECT
				pk_org
					AS data,
				l10n_category || ': ' || organization
					AS list_label,
				organization || ' (' || l10n_category || ')'
					AS field_label
			FROM
				dem.v_orgs
			WHERE
				l10n_category %(fragment_condition)s
					OR
				category %(fragment_condition)s

		)) AS all_matches
		ORDER BY list_label
	) AS ordered_matches
	LIMIT 50
		"""
		mp = gmMatchProvider.cMatchProvider_SQL2(queries=query)
		mp.setThresholds(1, 3, 5)
		gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)
		self.SetToolTip(_("Select an organization."))
		self.matcher = mp
		self.picklist_delay = 300
		self.selection_only = True

#====================================================================
from Gnumed.wxGladeWidgets import wxgOrganizationEAPnl

class cOrganizationEAPnl(wxgOrganizationEAPnl.wxgOrganizationEAPnl, gmEditArea.cGenericEditAreaMixin):

	def __init__(self, *args, **kwargs):

		try:
			data = kwargs['organization']
			del kwargs['organization']
		except KeyError:
			data = None

		wxgOrganizationEAPnl.wxgOrganizationEAPnl.__init__(self, *args, **kwargs)
		gmEditArea.cGenericEditAreaMixin.__init__(self)

		self.mode = 'new'
		self.data = data
		if data is not None:
			self.mode = 'edit'

		#self.__init_ui()
	#----------------------------------------------------------------
	def __init_ui(self):
		self._PRW_org.selection_only = False
	#----------------------------------------------------------------
	# generic Edit Area mixin API
	#----------------------------------------------------------------
	def _valid_for_save(self):
		validity = True

		if self._PRW_category.GetData() is None:
			validity = False
			self._PRW_category.display_as_valid(False)
			self._PRW_category.SetFocus()
		else:
			self._PRW_category.display_as_valid(True)

		if self._PRW_org.GetValue().strip() == '':
			validity = False
			self._PRW_org.display_as_valid(False)
			self._PRW_org.SetFocus()
		else:
			self._PRW_org.display_as_valid(True)

#		if self.mode == 'edit':
#			if self._PRW_org.GetData() is None:
#				validity = False
#				self._PRW_org.display_as_valid(False)
#				self._PRW_org.SetFocus()
#			else:
#				self._PRW_org.display_as_valid(True)
#		else:
#			if self._PRW_org.GetValue().strip() == u'':
#				validity = False
#				self._PRW_org.display_as_valid(False)
#				self._PRW_org.SetFocus()
#			else:
#				if self._PRW_org.GetData() is not None:
#					validity = False
#					self._PRW_org.display_as_valid(False)
#					self._PRW_org.SetFocus()
#				else:
#					self._PRW_org.display_as_valid(True)

		return validity
	#----------------------------------------------------------------
	def _save_as_new(self):
		self.data = gmOrganization.create_org (
			organization = self._PRW_org.GetValue().strip(),
			category = self._PRW_category.GetData()
		)
		return True
	#----------------------------------------------------------------
	def _save_as_update(self):
		#self.data['pk_org'] = self._PRW_org.GetData()
		self.data['organization'] = self._PRW_org.GetValue().strip()
		self.data['pk_category_org'] = self._PRW_category.GetData()
		self.data.save()
		return True
	#----------------------------------------------------------------
	def _refresh_as_new(self):
		self._PRW_org.SetText(value = '', data = None)
		self._PRW_category.SetText(value = '', data = None)

		self._PRW_org.SetFocus()
	#----------------------------------------------------------------
	def _refresh_as_new_from_existing(self):
		self._PRW_org.SetText(value = '', data = None)
		self._PRW_category.SetText(value = self.data['l10n_category'], data = self.data['pk_category_org'])

		self._PRW_org.SetFocus()
	#----------------------------------------------------------------
	def _refresh_from_existing(self):
		self._PRW_org.SetText(value = self.data['organization'], data = self.data['pk_org'])
		self._PRW_category.SetText(value = self.data['l10n_category'], data = self.data['pk_category_org'])

		self._PRW_category.SetFocus()

#============================================================
class cOrgCategoryPhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):
		query = """
	SELECT DISTINCT ON (data)
		*
	FROM (
		SELECT
			pk
				AS data,
			_(description) || ' (' || description || ')'
				AS list_label,
			_(description)
				AS field_label
		FROM
			dem.org_category
		WHERE
			_(description) %(fragment_condition)s
				OR
			description %(fragment_condition)s
		ORDER BY list_label
		) AS ordered_matches
	LIMIT 50
		"""
		mp = gmMatchProvider.cMatchProvider_SQL2(queries=query)
		mp.setThresholds(1, 3, 5)
		gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)
		self.SetToolTip(_("Select an organizational category."))
		self.matcher = mp
		self.selection_only = True

#============================================================
class cOrganizationsManagerPnl(gmListWidgets.cGenericListManagerPnl):
	"""A list for managing organizations."""

	def __init__(self, *args, **kwargs):

		gmListWidgets.cGenericListManagerPnl.__init__(self, *args, **kwargs)

		self.refresh_callback = self.refresh
		self.new_callback = self._add
		self.edit_callback = self._edit
		self.delete_callback = self._del

		self.__init_ui()
		self.refresh()
	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def refresh(self, lctrl=None):
		orgs = gmOrganization.get_orgs(order_by = 'organization, l10n_category')
		items = [ [o['organization'], o['l10n_category'], o['pk_org']] for o in orgs ]
		self._LCTRL_items.set_string_items(items)
		self._LCTRL_items.set_column_widths(widths = [wx.LIST_AUTOSIZE, wx.LIST_AUTOSIZE, wx.LIST_AUTOSIZE])
		self._LCTRL_items.set_data(orgs)

		for idx in range(len(orgs)):
			org = orgs[idx]
			if org['is_praxis']:
				self._LCTRL_items.SetItemTextColour(idx, wx.Colour('RED'))
				break
	#--------------------------------------------------------
	# event handlers
	#--------------------------------------------------------
	def _add(self):
		return edit_org(parent = self, org = None, single_entry = False)
	#--------------------------------------------------------
	def _edit(self, item):
		return edit_org(parent = self, org = item, single_entry = True)
	#--------------------------------------------------------
	def _del(self, item):
		return gmOrganization.delete_org(organization = item['pk_org'])
	#--------------------------------------------------------
	def _on_list_item_focused(self, event):
		pass
	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def __init_ui(self):
		self._LCTRL_items.set_columns(columns = [_('Organization'), _('Category'), '#'])
		self._LCTRL_items.SetToolTip(_('Organizations registered in GNUmed.'))
		self._LCTRL_items.item_tooltip_callback = self.get_tooltip
		#self._LCTRL_items.set_column_widths(widths = [wx.LIST_AUTOSIZE, wx.LIST_AUTOSIZE, wx.LIST_AUTOSIZE])
	#--------------------------------------------------------
	def get_tooltip(self, org):
		if org is None:
			return _('Organizations registered in GNUmed.')
		return org.format()
#============================================================
from Gnumed.wxGladeWidgets import wxgOrganizationManagerDlg

class cOrganizationManagerDlg(wxgOrganizationManagerDlg.wxgOrganizationManagerDlg):

	def __init__(self, *args, **kwargs):

		wxgOrganizationManagerDlg.wxgOrganizationManagerDlg.__init__(self, *args, **kwargs)

		self.Centre(direction = wx.BOTH)

		self._PNL_address.type_is_editable = False
		self._PNL_orgs.select_callback = self._on_org_selected
		self._PNL_units.select_callback = self._on_unit_selected
		self._PNL_comms.message = _('Communication channels')
		self._PNL_ids.message = _('External IDs')

		# FIXME: find proper button
		#self._PNL_units.MoveAfterInTabOrder(self._PNL_orgs._BTN_)

		self._on_org_selected(None)
		self._PNL_orgs._LCTRL_items.SetFocus()
	#--------------------------------------------------------
	# event handlers
	#--------------------------------------------------------
	def _on_org_selected(self, item):
		self._PNL_units.org = item
		self._on_unit_selected(None)
	#--------------------------------------------------------
	def _on_unit_selected(self, item):
		self._PNL_address.unit = item
		self._PNL_comms.channel_owner = item
		self._PNL_ids.org_unit = item
		if item is None:
			self._PNL_comms._BTN_add.Enable(False)
			self._PNL_ids.Enable(False)
		else:
			self._PNL_comms._BTN_add.Enable(True)
			self._PNL_ids.Enable(True)

#============================================================
# main
#------------------------------------------------------------
if __name__ == "__main__":

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	from Gnumed.pycommon import gmPG2

	#--------------------------------------------------------
#	def test_org_prw():
#		app = wx.PyWidgetTester(size = (200, 50))
		#pw = 
#		cOrganizationPhraseWheel(app.frame, -1)
#		app.frame.Show(True)
#		app.MainLoop()
	#--------------------------------------------------------
#	def test_org_unit_prw():
#		app = wx.PyWidgetTester(size = (200, 50))
		#pw = 
#		cOrgUnitPhraseWheel(app.frame, -1)
#		app.frame.Show(True)
#		app.MainLoop()
	#--------------------------------------------------------
	def test():
		gmPG2.get_connection()
#		app = wx.PyWidgetTester(size = (600, 600))
#		dlg = cOrganizationManagerDlg(app.frame, -1, size = (600, 600))
#		dlg.SetSize((600, 600))
#		dlg.ShowModal()
	#	app.SetWidget(dlg, -1)
#		app.MainLoop()
	#--------------------------------------------------------
	#test_org_unit_prw()
	#test_org_prw()
	test()

#======================================================================
