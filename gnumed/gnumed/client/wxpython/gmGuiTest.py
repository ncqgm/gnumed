# -*- coding: utf-8 -*-

"""GNUmed GUI widget testing framework."""
#==============================================================================
__author__  = "K. Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = 'GPL v2 or later (details at https://www.gnu.org)'


import sys
import logging


import wx
from wx.lib.mixins import inspection


if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x
else:
	try:
		_
	except NameError:
		from Gnumed.pycommon import gmI18N
		gmI18N.activate_locale()
		gmI18N.install_domain()
from Gnumed.pycommon import gmPG2
from Gnumed.pycommon import gmLog2

from Gnumed.business import gmPraxis
from Gnumed.business import gmPerson
from Gnumed.business import gmPersonSearch
from Gnumed.business import gmStaff


_log = logging.getLogger('gm.guitest')

#==============================================================================
def test_widget(widget_class, *widget_args, patient:int=-1, size=None, setup_db:bool=True, **widget_kwargs):
	if setup_db:
		gmPG2.request_login_params(setup_pool = True, force_tui = True)
	gmPraxis.gmCurrentPraxisBranch.from_first_branch()
	if not __activate_patient(patient = patient):
		sys.exit()

	app = inspection.InspectableApp()
	app.SetAssertMode(wx.APP_ASSERT_EXCEPTION | wx.APP_ASSERT_LOG)
	app.InitInspection()
	if size is None:
		size = (800, 600)
	frame = wx.Frame(None, id = -1, title = _('GNUmed widget test: %s') % widget_class, size = size)
	frame.CentreOnScreen(wx.BOTH)
	app.SetTopWindow(frame)
	widget = widget_class(frame, *widget_args, **widget_kwargs)
	frame.Show(True)
	app.ShowInspectionTool()
	try:
		app.MainLoop()
	except Exception:
		gmLog2.log_stack_trace(message = 'test failure')
	return widget

#==============================================================================
def setup_widget_test_env(patient=-1):
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
	my_widget.whatever_else_is_necessary(...)
	wx.GetApp().MainLoop()

	Returns:
		main frame, which can be used to instantiate widgets
	"""
	gmPG2.request_login_params(setup_pool = True, force_tui = True)
	if not __activate_patient(patient = patient):
		sys.exit()
	gmPraxis.gmCurrentPraxisBranch.from_first_branch()
	gmStaff.set_current_provider_to_logged_on_user()

	app = inspection.InspectableApp()
	app.SetAssertMode(wx.APP_ASSERT_EXCEPTION | wx.APP_ASSERT_LOG)
	app.InitInspection()
	frame = wx.Frame(None, id = -1, title = _('GNUmed widget test'), size = (800, 600))
	frame.CentreOnScreen(wx.BOTH)
	app.SetTopWindow(frame)
	frame.Show(True)
	app.ShowInspectionTool()
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

	# setup a real translation
	del _
	from Gnumed.pycommon import gmI18N
	gmI18N.activate_locale()
	gmI18N.install_domain('gnumed')

	#--------------------------------------------------------------------------
	def test__test_widget():
		ctrl = wx.TextCtrl
		test_widget(ctrl, patient = None)

	#--------------------------------------------------------------------------
	def test__setup_widget_test_env():
		frame = setup_widget_test_env()
		print(frame)
		tctrl = wx.TextCtrl(frame, -1)
		tctrl.Value = 'GNUmed GUI Test test'
		wx.GetApp().MainLoop()

	#--------------------------------------------------------------------------
	#test__test_widget()
	test__setup_widget_test_env()
