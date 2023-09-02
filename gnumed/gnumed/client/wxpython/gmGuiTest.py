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
def test_widget(widget_class, *widget_args, patient=None, size=None, **widget_kw_args):
	gmPG2.request_login_params(setup_pool = True, force_tui = True)
	gmPraxis.activate_first_praxis_branch()
	if not __activate_patient(patient = patient):
		sys.exit()

	app = wx.App()
	if size is None:
		size = (800, 600)
	frame = wx.Frame(None, id = -1, title = _('GNUmed widget test: %s') % widget_class, size = size)
	frame.CentreOnScreen(wx.BOTH)
	app.SetTopWindow(frame)
	widget = widget_class(frame, *widget_args, **widget_kw_args)
	#widget.matcher.print_queries = True
	frame.Show(True)
	try:
		app.MainLoop()
	except Exception:
		_log.log_stack_trace(message = 'test failure')
	return widget

#==============================================================================
def setup_widget_test_env(patient=None):
	"""Setup widget test environment.

	- connect to DB
	- setup praxis branch
	- setup active patient, asking for patient if not given
	- setup wx app
	- setup wx frame as topwindow

	Does *not* run app.MainLoop(). You will have to do that
	yourself like so:

	main_frame = setup_widget_test_env(...)
	my_widget = cWidgetClass(main_frame, ...)
	my_widget.whatever(...)
	wx.GetApp().MainLoop()

	Returns:
		main frame, which can be used to instantiate widgets
	"""
	gmPG2.request_login_params(setup_pool = True, force_tui = True)
	gmPraxis.activate_first_praxis_branch()
	if patient is None:
		patient = gmPersonSearch.ask_for_patient()
	if patient is None:
		sys.exit()

	gmPerson.set_active_patient(patient = patient)
	app = wx.App()
	frame = wx.Frame(None, id = -1, title = _('GNUmed widget test'), size = (800, 600))
	frame.CentreOnScreen(wx.BOTH)
	app.SetTopWindow(frame)
	frame.Show(True)
	return frame

#==============================================================================
# helpers
#------------------------------------------------------------------------------
def __activate_patient(patient=None):
	if patient is None:
		return True

	if patient == -1:
		patient = gmPersonSearch.ask_for_patient()
		if patient is None:
			return False

	gmPerson.set_active_patient(patient = patient)
	print('activating patient:', patient)
	return True

#==============================================================================
# main
#==============================================================================
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	#--------------------------------------------------------------------------
	def test__test_widget():
		panel = wx.TextCtrl
		test_widget(panel, patient = None)

	#--------------------------------------------------------------------------
	def test__setup_widget_test_env():
		print(setup_widget_test_env())

	#--------------------------------------------------------------------------
	test__test_widget()
	#test__setup_widget_test_env()
