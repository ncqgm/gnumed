# -*- coding: utf-8 -*-
"""GNUmed patient overview plugin"""
#======================================================================
__author__ = "Carlos Moro, Karsten Hilbert"
__license__ = 'GPL v2 or later (details at https://www.gnu.org)'

import logging
import sys

if __name__ == '__main__':
	sys.path.insert(0, '../../../')
	_ = lambda x:x
from Gnumed.wxpython import gmPlugin, gmPatOverviewWidgets
from Gnumed.wxpython import gmAccessPermissionWidgets

_log = logging.getLogger('gm.ui')

#======================================================================
class gmPatientOverviewPlugin(gmPlugin.cNotebookPlugin):

	tab_name = _('Overview')
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
	def name(self):
		return gmPatientOverviewPlugin.tab_name

	def GetWidget(self, parent):
		self._widget = gmPatOverviewWidgets.cPatientOverviewPnl(parent, -1)
		return self._widget

	def MenuInfo(self):
		return ('emr', _('&Overview'))

	def can_receive_focus(self):
		if not self._verify_patient_avail():
			return None
		return True

#======================================================================
# main
#----------------------------------------------------------------------
if __name__ == "__main__":

	# 3rd party
	import wx

	# GNUmed
	from Gnumed.business import gmPersonSearch
	from Gnumed.wxpython import gmSOAPWidgets, gmPatSearchWidgets

	_log.info("starting Notebooked progress notes input plugin...")

	# obtain patient
	patient = gmPersonSearch.ask_for_patient()
	if patient is None:
		print("None patient. Exiting gracefully...")
		sys.exit(0)
	gmPatSearchWidgets.set_active_patient(patient=patient)

	application = wx.wx.PyWidgetTester(size = (800,600))
	multisash_notes = gmSOAPWidgets.cNotebookedProgressNoteInputPanel(application.frame, -1)

	application.frame.Show(True)
	application.MainLoop()

	# clean up
	if patient is not None:
		try:
			patient.cleanup()
		except Exception:
			print("error cleaning up patient")

	_log.info("closing Notebooked progress notes input plugin...")
