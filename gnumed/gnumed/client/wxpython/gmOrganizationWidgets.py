"""GNUmed organization handling widgets.

copyright: authors
"""
#======================================================================
__author__ = "K.Hilbert"
__license__ = "GPL (details at http://www.gnu.org)"

import logging, sys


import wx


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmTools
from Gnumed.business import gmOrganization
from Gnumed.wxpython import gmListWidgets
# gmDispatcher, gmMatchProvider, , gmI18N
#from Gnumed.pycommon import gmCfg, gmDateTime
#from Gnumed.business import gmPerson, gmVaccination, gmSurgery
#from Gnumed.wxpython import gmPhraseWheel, gmTerryGuiParts, gmRegetMixin, gmGuiHelpers
#from Gnumed.wxpython import gmEditArea


_log = logging.getLogger('gm.organization')

#======================================================================
def manage_org_units(parent=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()
	#------------------------------------------------------------
	def refresh(lctrl):
		units = gmOrganization.get_org_units(order_by = 'organization, l10n_unit_category, unit')

		items = [ [
			gmTools.coalesce (
				u['l10n_unit_category'],
				u['l10n_organization_category']
			),
			u'%s (%s)' % (
				u['organization'],
				u['l10n_organization_category']
			),
			u['unit']
		] for u in units ]

		lctrl.set_string_items(items)
		lctrl.set_data(units)
	#------------------------------------------------------------
	gmListWidgets.get_choices_from_list (
		parent = parent,
		msg = _('\nUnits (sites, parts, departments, branches, ...) of organizations registered in GNUmed.\n'),
		caption = _('Showing organizational units.'),
		columns = [ _('Category'), _('Organization'), _('Organizational Unit') ],
		single_selection = True,
		refresh_callback = refresh
	)

#======================================================================
def manage_orgs(parent=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()
	#------------------------------------------------------------
	def refresh(lctrl):
		orgs = gmOrganization.get_orgs(order_by = 'l10n_category, organization')
		items = [ [o['l10n_category'], o['organization']] for o in orgs ]
		lctrl.set_string_items(items)
		lctrl.set_data(orgs)
	#------------------------------------------------------------
	gmListWidgets.get_choices_from_list (
		parent = parent,
		msg = _('\nOrganizations registered in GNUmed.\n'),
		caption = _('Showing organizations.'),
		columns = [ _('Category'), _('Organization') ],
		single_selection = True,
		refresh_callback = refresh
	)

#======================================================================
# main
#----------------------------------------------------------------------
if __name__ == "__main__":

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != u'test':
		sys.exit()

	app = wx.PyWidgetTester(size = (600, 600))
	app.SetWidget(cATCPhraseWheel, -1)
	app.MainLoop()
#======================================================================
