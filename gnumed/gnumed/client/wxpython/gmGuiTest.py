# -*- coding: utf-8 -*-

"""GNUmed GUI widget testing framework."""
#==============================================================================
__author__  = "K. Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = 'GPL v2 or later (details at https://www.gnu.org)'

import logging
import sys


import wx


if __name__ == '__main__':
	sys.path.insert(0, '../../')

from Gnumed.pycommon import gmI18N
gmI18N.activate_locale()
gmI18N.install_domain()
from Gnumed.pycommon import gmPG2

from Gnumed.business import gmPraxis
from Gnumed.business import gmPerson
from Gnumed.business import gmPersonSearch


_log = logging.getLogger('gm.guitest')

#==============================================================================
def test_widget(widget, patient=None):
	gmPG2.request_login_params(setup_pool = True, force_tui = True)
	gmPraxis.activate_first_praxis_branch()
	if patient is None:
		patient = gmPersonSearch.ask_for_patient()
	if patient is None:
		sys.exit()

	gmPerson.set_active_patient(patient = patient)
	app = wx.App()
	frame = wx.Frame(None, id = -1, title = _('GNUmed widget test: %s') % widget, size = (800, 600))
	frame.CentreOnScreen(wx.BOTH)
	app.SetTopWindow(frame)
	widget(frame)
	frame.Show(True)
	app.MainLoop()

#==============================================================================
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	panel = wx.TextCtrl
	test_widget(panel, patient = None)
