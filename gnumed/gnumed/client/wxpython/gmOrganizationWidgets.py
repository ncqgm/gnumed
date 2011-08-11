"""GNUmed organization handling widgets.

copyright: authors
"""
#============================================================
__author__ = "K.Hilbert"
__license__ = "GPL v2 or later (details at http://www.gnu.org)"

import logging, sys


import wx


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmTools
from Gnumed.business import gmOrganization
from Gnumed.wxpython import gmListWidgets
from Gnumed.wxpython import gmEditArea
from Gnumed.wxpython import gmPhraseWheel
from Gnumed.wxpython import gmPersonContactWidgets


_log = logging.getLogger('gm.organization')

#============================================================
# organizational units API
#------------------------------------------------------------
def edit_org_unit(parent=None, org_unit=None, single_entry=False):
	ea = cOrgUnitEAPnl(parent = parent, id = -1)
	ea.data = org_unit
	ea.mode = gmTools.coalesce(org_unit, 'new', 'edit')
	dlg = gmEditArea.cGenericEditAreaDlg2(parent = parent, id = -1, edit_area = ea, single_entry = single_entry)
	dlg.SetTitle(gmTools.coalesce(org_unit, _('Adding new organizational unit'), _('Editing organizational unit')))
	if dlg.ShowModal() == wx.ID_OK:
		dlg.Destroy()
		return True
	dlg.Destroy()
	return False
#============================================================
class cOrgUnitPhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):
		gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)

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
		self.new_callback = self._new
		self.edit_callback = self._edit
#		self.delete_callback = self._del_address

		self.__show_none_if_no_org = True
		self.__init_ui()
		self.__refresh()
	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def refresh(self):
		self.__refresh()
	#--------------------------------------------------------
	# event handlers
	#--------------------------------------------------------
	def _edit(self, item):
		return edit_org_unit(parent = self, org_unit = item, single_entry = True)
	#--------------------------------------------------------
	def _new(self):
		return edit_org_unit(parent = self, org_unit = None, single_entry = False)
	#--------------------------------------------------------
	def _on_list_item_focused(self, event):
		pass
	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def __init_ui(self):
		self._LCTRL_items.SetToolTipString(_('Units (sites, parts, departments, branches, ...) of organizations registered in GNUmed.'))
		self._LCTRL_items.set_columns(columns = [ _('Organizational Unit'), _('Unit Category'), u'#' ])
		#self._LCTRL_items.set_column_widths(widths = [wx.LIST_AUTOSIZE, wx.LIST_AUTOSIZE, wx.LIST_AUTOSIZE])
	#--------------------------------------------------------
	def __refresh(self):

		if self.__org is None:
			self.message = None
			if self.__show_none_if_no_org:
				self._LCTRL_items.set_string_items(items = None)
				return
			pk = None
		else:
			pk = self.__org['pk_org']
			self.message = u'%s %s%s%s' % (
				self.__org['l10n_category'],
				gmTools.u_left_double_angle_quote,
				self.__org['organization'],
				gmTools.u_right_double_angle_quote
			)

		units = gmOrganization.get_org_units(order_by = 'unit, l10n_unit_category', org = pk)
		items = [ [
			u['unit'],
			gmTools.coalesce(u['l10n_unit_category'], u''),
			u['pk_org_unit']
		] for u in units ]

		self._LCTRL_items.set_string_items(items)
		self._LCTRL_items.set_data(units)
	#--------------------------------------------------------
	def _edit_org_unit(self, org_unit=None):
		return edit_org_unit(parent = self, org_unit = org_unit, single_entry = True)
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

		if self._PRW_org.GetData() is None:
			validity = False
			self._PRW_org.display_as_valid(False)
			self._PRW_org.SetFocus()
		else:
			self._PRW_org.display_as_valid(True)

		if self._PRW_unit.GetData() is None:
			validity = False
			self._PRW_unit.display_as_valid(False)
			self._PRW_unit.SetFocus()
		else:
			self._PRW_unit.display_as_valid(True)

		if self._PRW_category.GetData() is None:
			validity = False
			self._PRW_category.display_as_valid(False)
			self._PRW_category.SetFocus()
		else:
			self._PRW_category.display_as_valid(True)

		return validity
	#----------------------------------------------------------------
	def _save_as_new(self):
		# save the data as a new instance
		data = gmXXXX.create_xxxx()

		data[''] = self._
		data[''] = self._

		data.save()

		# must be done very late or else the property access
		# will refresh the display such that later field
		# access will return empty values
		self.data = data
		return False
		return True
	#----------------------------------------------------------------
	def _save_as_update(self):
		# update self.data and save the changes
		self.data[''] = self._TCTRL_xxx.GetValue().strip()
		self.data[''] = self._PRW_xxx.GetData()
		self.data[''] = self._CHBOX_xxx.GetValue()
		self.data.save()
		return True
	#----------------------------------------------------------------
	def _refresh_as_new(self):
		self._PRW_org.SetText(value = u'', data = None)
		self._PRW_unit.SetText(value = u'', data = None)
		self._PRW_category.SetText(value = u'', data = None)

		self._PRW_unit.SetFocus()
	#----------------------------------------------------------------
	def _refresh_as_new_from_existing(self):
		self._PRW_org.SetText(value = self.data['organization'], data = self.data['pk_org'])
		self._PRW_unit.SetText(value = u'', data = None)
		self._PRW_category.SetText(value = self.data['unit_category'], data = self.data['pk_category_unit'])

		self._PRW_unit.SetFocus()
	#----------------------------------------------------------------
	def _refresh_from_existing(self):
		self._PRW_org.SetText(value = self.data['organization'], data = self.data['pk_org'])
		self._PRW_unit.SetText(value = self.data['unit'], data = self.data['pk_org_unit'])
		self._PRW_category.SetText(value = self.data['unit_category'], data = self.data['pk_category_unit'])

		self._PRW_unit.SetFocus()
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
			self.message = None
			self._PRW_address_searcher.SetText(u'', None)
			self._PRW_address_searcher.Enable(False)
			self._BTN_save_picked_address.Enable(False)
			self._BTN_add_new_address.Enable(False)
		else:
			self.message = u'%s %s%s%s' % (
				self.__unit['l10n_unit_category'],
				gmTools.u_left_double_angle_quote,
				self.__unit['unit'],
				gmTools.u_right_double_angle_quote
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
		self.__unit['pk_address'] = self._PRW_address_searcher.GetData()
	#--------------------------------------------------------
	def _on_add_new_address_button_pressed(self, event):
		ea = gmPersonContactWidgets.cAddressEditAreaPnl(self, -1)
		ea.address_holder = self.__unit
		dlg = gmEditArea.cGenericEditAreaDlg(self, -1, edit_area = ea)
		dlg.SetTitle(_('Adding new address'))
		if dlg.ShowModal() != wx.ID_OK:
			return False
		self.__refresh()
		return True
	#--------------------------------------------------------
	def _on_manage_addresses_button_pressed(self, event):
		gmPersonContactWidgets.manage_addresses(parent = self)
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
			self._LBL_message.SetLabel(u'')
		else:
			self._LBL_message.SetLabel(msg)
			self._LBL_message.Show()
		self.Layout()

	message = property(_get_message, _set_message)
#============================================================
# organizations API
#------------------------------------------------------------
def manage_orgs(parent=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	dlg = cOrganizationManagerDlg(parent, -1)
	dlg.ShowModal()
#============================================================
class cOrganizationPhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):
		gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)
#============================================================
class cOrgCategoryPhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):
		gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)
#============================================================
class cOrganizationsManagerPnl(gmListWidgets.cGenericListManagerPnl):
	"""A list for managing organizations."""

	def __init__(self, *args, **kwargs):

		gmListWidgets.cGenericListManagerPnl.__init__(self, *args, **kwargs)

		self.refresh_callback = self.refresh
#		self.new_callback = self._add_address
#		self.edit_callback = self._edit_address
#		self.delete_callback = self._del_address

		self.__init_ui()
		self.refresh()
	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def refresh(self):
		orgs = gmOrganization.get_orgs(order_by = 'l10n_category, organization')
		items = [ [o['l10n_category'], o['organization'], o['pk_org']] for o in orgs ]
		self._LCTRL_items.set_string_items(items)
		self._LCTRL_items.set_data(orgs)
	#--------------------------------------------------------
	# event handlers
	#--------------------------------------------------------
	def _on_list_item_focused(self, event):
		pass
	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def __init_ui(self):
		self._LCTRL_items.SetToolTipString(_('Organizations registered in GNUmed.'))
		self._LCTRL_items.set_columns(columns = [_('Category'), _('Organization'), u'#'])
		#self._LCTRL_items.set_column_widths(widths = [wx.LIST_AUTOSIZE, wx.LIST_AUTOSIZE, wx.LIST_AUTOSIZE])
#============================================================
from Gnumed.wxGladeWidgets import wxgOrganizationManagerDlg

class cOrganizationManagerDlg(wxgOrganizationManagerDlg.wxgOrganizationManagerDlg):

	def __init__(self, *args, **kwargs):

		wxgOrganizationManagerDlg.wxgOrganizationManagerDlg.__init__(self, *args, **kwargs)

		self.Centre(direction = wx.BOTH)

		self._PNL_address.type_is_editable = False
		self._PNL_orgs.select_callback = self._on_org_selected
		self._PNL_units.select_callback = self._on_unit_selected

		# FIXME: find proper button
		#self._PNL_units.MoveAfterInTabOrder(self._PNL_orgs._BTN_)

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
#============================================================
# main
#------------------------------------------------------------
if __name__ == "__main__":

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != u'test':
		sys.exit()

	from Gnumed.pycommon import gmI18N
	gmI18N.activate_locale()
	gmI18N.install_domain()

	app = wx.PyWidgetTester(size = (600, 600))
	dlg = cOrganizationManagerDlg(app.frame, -1, size = (600, 600))
	dlg.SetSize((600, 600))
	dlg.ShowModal()
#	app.SetWidget(dlg, -1)
	app.MainLoop()
#======================================================================
