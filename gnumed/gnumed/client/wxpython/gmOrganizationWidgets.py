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


_log = logging.getLogger('gm.organization')

#============================================================
# organizationial units API
#------------------------------------------------------------
def manage_org_units(parent=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

#	#--------------------------------------------------------
#	def refresh(lctrl):
#		units = gmOrganization.get_org_units(order_by = 'organization, l10n_unit_category, unit')
#
#		items = [ [
#			gmTools.coalesce (
#				u['l10n_unit_category'],
#				u['l10n_organization_category']
#			),
#			u'%s (%s)' % (
#				u['organization'],
#				u['l10n_organization_category']
#			),
#			u['unit']
#		] for u in units ]
#
#		lctrl.set_string_items(items)
#		lctrl.set_data(units)
#	#------------------------------------------------------------
#	gmListWidgets.get_choices_from_list (
#		parent = parent,
#		msg = _('\nUnits (sites, parts, departments, branches, ...) of organizations registered in GNUmed.\n'),
#		caption = _('Showing organizational units.'),
#		columns = [ _('Category'), _('Organization'), _('Organizational Unit') ],
#		single_selection = True,
#		refresh_callback = refresh
#	)
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
#		self.new_callback = self._add_address
#		self.edit_callback = self._edit_address
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
	def _on_list_item_focused(self, event):
		pass
	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def __init_ui(self):
		self._LCTRL_items.SetToolTipString(_('Units (sites, parts, departments, branches, ...) of organizations registered in GNUmed.'))
		self._LCTRL_items.set_columns(columns = [ _('Organizational Unit'), _('Category'), u'#' ])
#		self._LCTRL_items.set_column_widths(widths = [wx.LIST_AUTOSIZE, wx.LIST_AUTOSIZE, wx.LIST_AUTOSIZE_USEHEADER])
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
# organizations API
#------------------------------------------------------------
def manage_orgs(parent=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	dlg = cOrganizationManagerDlg(parent, -1)
	dlg.ShowModal()

#	#--------------------------------------------------------
#	def refresh(lctrl):
#		orgs = gmOrganization.get_orgs(order_by = 'l10n_category, organization')
#		items = [ [o['l10n_category'], o['organization']] for o in orgs ]
#		lctrl.set_string_items(items)
#		lctrl.set_data(orgs)
#	#--------------------------------------------------------
#	gmListWidgets.get_choices_from_list (
#		parent = parent,
#		msg = _('\nOrganizations registered in GNUmed.\n'),
#		caption = _('Showing organizations.'),
#		columns = [ _('Category'), _('Organization') ],
#		single_selection = True,
#		refresh_callback = refresh
#	)

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
#		self._LCTRL_items.set_column_widths(widths = [wx.LIST_AUTOSIZE, wx.LIST_AUTOSIZE, wx.LIST_AUTOSIZE])
#============================================================
from Gnumed.wxGladeWidgets import wxgOrganizationManagerDlg

class cOrganizationManagerDlg(wxgOrganizationManagerDlg.wxgOrganizationManagerDlg):

	def __init__(self, *args, **kwargs):

		wxgOrganizationManagerDlg.wxgOrganizationManagerDlg.__init__(self, *args, **kwargs)

		self.Centre(direction = wx.BOTH)

		self._PNL_adr.type_is_editable = False
		self._PNL_orgs.select_callback = self._on_org_selected
		self._PNL_units.select_callback = self._on_unit_selected

	#--------------------------------------------------------
	# event handlers
	#--------------------------------------------------------
	def _on_org_selected(self, item):
		self._PNL_units.org = item
		self._on_unit_selected(None)
	#--------------------------------------------------------
	def _on_unit_selected(self, item):
		self._PNL_adr.address_holder = item
		if item is None:
			self._PNL_adr.address = None
		else:
			self._PNL_adr.address = item.address
		self._PNL_adr.refresh()
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
