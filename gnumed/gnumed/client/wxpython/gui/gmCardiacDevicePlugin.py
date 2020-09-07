# -*- coding: utf-8 -*-
"""This is a cardiac device interrogation management plugin """
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
#================================================================
import sys, logging


import wx


from Gnumed.wxpython import gmPlugin, gmDeviceWidgets

if __name__ == '__main__':
	sys.path.insert(0, '../../../')
	_ = lambda x:x
	from Gnumed.pycommon import gmI18N
	gmI18N.activate_locale()
	gmI18N.install_domain()



_log = logging.getLogger('gm.ui')
#================================================================
class gmCardiacDevicePlugin(gmPlugin.cNotebookPlugin):
	"""Plugin to encapsulate document tree."""

	tab_name = _("Cardiac Devices")

	def name (self):
		return gmCardiacDevicePlugin.tab_name
	#--------------------------------------------------------
	def GetWidget (self, parent):
		self._widget = gmDeviceWidgets.cCardiacDevicePluginPnl(parent, -1)
		return self._widget
	#--------------------------------------------------------
	def MenuInfo (self):
		return ('emr', _('Show &cardiac devices'))
	#--------------------------------------------------------
	def can_receive_focus(self):
		# need patient
		if not self._verify_patient_avail():
			return None
		return 1
	#--------------------------------------------------------
	def _on_raise_by_signal(self, **kwds):
		if not gmPlugin.cNotebookPlugin._on_raise_by_signal(self, **kwds):
			return False
		try:
			if kwds['sort_mode'] == 'review':
				self._widget._on_sort_by_review_selected(None)
		except KeyError:
			pass
		return True
#================================================================
# MAIN
#----------------------------------------------------------------
if __name__ == '__main__':

	# GNUmed
	from Gnumed.business import gmPersonSearch
	from Gnumed.wxpython import gmMeasurementWidgets,gmPatSearchWidgets

	_log.info("starting Notebooked cardiac device input plugin...")

	# obtain patient
	patient = gmPersonSearch.ask_for_patient()
	if patient is None:
		print("None patient. Exiting gracefully...")
		sys.exit(0)
	gmPatSearchWidgets.set_active_patient(patient=patient)

	application = wx.wx.PyWidgetTester(size = (800,600))
	multisash_notes = gmMeasurementWidgets.cCardiacDeviceMeasurementsPnl(application.frame, -1)

	application.frame.Show(True)
	application.MainLoop()

	# clean up
	if patient is not None:
		try:
			patient.cleanup()
		except Exception:
			print("error cleaning up patient")

	_log.info("closing Notebooked cardiac device input plugin...")
#================================================================
