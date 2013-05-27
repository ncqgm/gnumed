"""GNUmed praxis related widgets.

copyright: authors
"""
#============================================================
__author__ = "K.Hilbert"
__license__ = "GPL v2 or later (details at http://www.gnu.org)"

import logging
import sys
#import datetime as pydt


import wx


if __name__ == '__main__':
	sys.path.insert(0, '../../')
#from Gnumed.pycommon import gmCfg
#from Gnumed.pycommon import gmPG2
#from Gnumed.pycommon import gmTools
#from Gnumed.pycommon import gmDateTime
#from Gnumed.pycommon import gmDispatcher

from Gnumed.business import gmPraxis
#from Gnumed.business import gmPerson
#from Gnumed.business import gmStaff
#from Gnumed.business import gmDemographicRecord

from Gnumed.wxpython import gmOrganizationWidgets
#from Gnumed.wxpython import gmEditArea
#from Gnumed.wxpython import gmGuiHelpers
#from Gnumed.wxpython.gmDemographicsWidgets import _validate_dob_field, _validate_tob_field


_log = logging.getLogger('gm.praxis')

#============================================================
def set_active_praxis_branch(parent=None):

#	if parent is None:
#		parent = wx.GetApp().GetTopWindow()

	branches = gmPraxis.get_praxis_branches()

	if len(branches) == 1:
		_log.debug('only one praxis branch configured')
		gmPraxis.gmCurrentPraxisBranch(branches[0])
		return True

	if len(branches) == 0:
		_log.debug('no praxis branches configured, selecting from organization units')
		unit = gmOrganizationWidgets.select_org_unit(msg = _('You must select one unit of an organization to be the praxis branch you log in from.'))
		if unit is None:
			_log.warning('no organization unit selected, aborting')
			return False
		_log.debug('org unit selected as praxis branch: %s', unit)
		branch = gmPraxis.create_praxis_branch(pk_org_unit = unit['pk_org_unit'])
		_log.debug('created praxis branch: %s', branch)
		gmPraxis.gmCurrentPraxisBranch(branch)
		return True

	#--------------------
	def refresh(lctrl):
		branches = gmPraxis.get_praxis_branches()
		items = [
			[	b['branch'],
				b['l10n_unit_category']
			] for b in branches
		]
		lctrl.set_string_items(items = items)
		lctrl.set_data(data = branches)
	#--------------------
	branch = gmListWidgets.get_choices_from_list (
		parent = parent,
		msg = _("Select branch you are logging in from (of praxis [%s]).\n") % branches[0]['praxis'],
		caption = _('Praxis branch selection ...'),
		columns = [_('Branch'), _('Branch type')],
		can_return_empty = False,
		single_selection = single_selection,
		refresh_callback = refresh
	)
	if branch is None:
		_log.warning('no praxis branch selected, aborting')
		return False
	gmPraxis.gmCurrentPraxisBranch(branch)
	return True

#============================================================
# main
#------------------------------------------------------------
if __name__ == "__main__":

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != u'test':
		sys.exit()

#	from Gnumed.pycommon import gmPG2
#	from Gnumed.pycommon import gmI18N
#	gmI18N.activate_locale()
#	gmI18N.install_domain()

	#--------------------------------------------------------
	#test_org_unit_prw()
