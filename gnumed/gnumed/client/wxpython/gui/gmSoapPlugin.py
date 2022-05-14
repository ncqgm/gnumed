# -*- coding: utf-8 -*-

"""GNUmed notebook based progress note input plugin

This plugin displays the list of patient problems
together with a notebook container for progress notes.
"""
#======================================================================
__author__ = "Carlos Moro, Karsten Hilbert"
__license__ = 'GPL v2 or later (details at https://www.gnu.org)'

import logging


if __name__ == '__main__':
	import sys
	sys.path.insert(0, '../../../')

from Gnumed.wxpython import gmPlugin, gmNarrativeWidgets
from Gnumed.wxpython import gmAccessPermissionWidgets


_log = logging.getLogger('gm.ui')
if __name__ == '__main__':
	_ = lambda x:x

#======================================================================
class gmSoapPlugin(gmPlugin.cNotebookPlugin):
	"""Plugin to encapsulate notebook based progress note input window."""

	tab_name = _('Notes')
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
		return gmSoapPlugin.tab_name

	def GetWidget (self, parent):
		self._widget = gmNarrativeWidgets.cSoapPluginPnl(parent, -1)
		return self._widget

	def MenuInfo (self):
		return ('emr', _('&Notes'))
		#return None

	def can_receive_focus(self):
		# need patient
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
	from Gnumed.wxpython import gmSOAPWidgets
	from Gnumed.wxpython import gmPatSearchWidgets

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
#======================================================================
