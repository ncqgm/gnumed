# -*- coding: utf-8 -*-

"""GNUmed notebook based patient edition plugin

This plugin displays a notebook container for patient edition

current pages (0.1): identity, contacts, occupation
"""
#======================================================================
__author__ = "Carlos Moro, Karsten Hilbert"
__license__ = 'GPL v2 or later (details at https://www.gnu.org)'

import logging


if __name__ == '__main__':
	import sys
	sys.path.insert(0, '../../../')
	_ = lambda x:x

# GNUmed
from Gnumed.wxpython import gmPlugin, gmDemographicsWidgets
from Gnumed.wxpython import gmAccessPermissionWidgets


_log = logging.getLogger('gm.ui')

#======================================================================
class gmNotebookedPatientEditionPlugin(gmPlugin.cNotebookPlugin):
	"""Plugin to encapsulate notebooked patient edition window."""

	tab_name = _('Demographics')
	required_minimum_role = 'non-clinical access'

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
		return gmNotebookedPatientEditionPlugin.tab_name

	def GetWidget (self, parent):
		self._widget = gmDemographicsWidgets.cNotebookedPatEditionPanel(parent, -1)
		return self._widget

	def MenuInfo (self):
		return ('patient', _('&Demographics'))

	def can_receive_focus(self):
		# need patient
		if not self._verify_patient_avail():
			return None
		return 1

#======================================================================
# main
#----------------------------------------------------------------------
if __name__ == "__main__":

	# 3rd party
	import wx

	# GNUmed
	from Gnumed.business import gmPersonSearch
	from Gnumed.wxpython import gmPatSearchWidgets

	_log.info("starting Notebooked patient edition plugin...")

	# obtain patient
	patient = gmPersonSearch.ask_for_patient()
	if patient is None:
		print("None patient. Exiting gracefully...")
		sys.exit(0)
	gmPatSearchWidgets.set_active_patient(patient=patient)

	# display standalone notebooked patient editor
	application = wx.PyWidgetTester(size=(800,600))
	application.SetWidget(gmDemographicsWidgets.cNotebookedPatEditionPanel, -1)

	application.frame.Show(True)
	application.MainLoop()

	# clean up
	if patient is not None:
		try:
			patient.cleanup()
		except Exception:
			print("error cleaning up patient")

	_log.info("closing Notebooked progress notes input plugin...")

#======================================================================
