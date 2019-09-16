# -*- coding: utf-8 -*-
__doc__ = """ This is the EMR Timeline plugin."""

#================================================================
__author__ = "karsten.hilbert@gmx.net"
__license__ = "GPL v2 or later"

import logging


import wx


from Gnumed.wxpython import gmPlugin, gmEMRTimelineWidgets
from Gnumed.wxpython import gmAccessPermissionWidgets

#================================================================
class gmEMRTimelinePlugin(gmPlugin.cNotebookPlugin):

	tab_name = _("EMR Timeline")
	required_minimum_role = 'full clinical access'

	@gmAccessPermissionWidgets.verify_minimum_required_role (
		required_minimum_role,
		activity = _('loading plugin <%s>') % tab_name,
		return_value_on_failure = False,
		fail_silently = False
	)
	def register(self):
		gmPlugin.cNotebookPlugin.register(self)
	#-------------------------------------------------
	def name (self):
		return gmEMRTimelinePlugin.tab_name
	#--------------------------------------------------------
	def GetWidget (self, parent):
		self._widget = gmEMRTimelineWidgets.cEMRTimelinePluginPnl(parent, -1)
		return self._widget
	#--------------------------------------------------------
	def MenuInfo (self):
		return ('emr', _('EMR &Timeline'))
	#--------------------------------------------------------
	def can_receive_focus(self):
		if not self._verify_patient_avail():
			return None
		return 1
	#--------------------------------------------------------
	def _on_raise_by_signal(self, **kwds):
		if not gmPlugin.cNotebookPlugin._on_raise_by_signal(self, **kwds):
			return False
		try:
			pass
		except KeyError:
			pass
		return True
#================================================================
# MAIN
#----------------------------------------------------------------
if __name__ == '__main__':

	# stdlib
	import sys
	sys.path.insert(0, '../../../')

	from Gnumed.pycommon import gmI18N
	gmI18N.activate_locale()
	gmI18N.install_domain()

	# GNUmed
	from Gnumed.business import gmPersonSearch
	from Gnumed.wxpython import gmPatSearchWidgets

	_log.info("starting template plugin...")

	# obtain patient
	patient = gmPersonSearch.ask_for_patient()
	if patient is None:
		print("None patient. Exiting gracefully...")
		sys.exit(0)
	gmPatSearchWidgets.set_active_patient(patient=patient)

	# display the plugin standalone
	application = wx.wx.PyWidgetTester(size = (800,600))
	widgets = gmExamplePluginWidgets.cExamplePluginPnl(application.frame, -1)

	application.frame.Show(True)
	application.MainLoop()

	# clean up
	if patient is not None:
		try:
			patient.cleanup()
		except Exception:
			print("error cleaning up patient")

	_log.info("closing example plugin...")
