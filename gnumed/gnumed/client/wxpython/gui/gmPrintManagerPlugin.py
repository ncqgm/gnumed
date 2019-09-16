# -*- coding: utf-8 -*-
"""A print manager plugin"""

__author__ = "karsten.hilbert@gmx.net"
__license__ = "GPL v2 or later"

#================================================================
import os.path, sys, logging
import wx

if __name__ == '__main__':
	# stdlib
	import sys
	sys.path.insert(0, '../../../')
	from Gnumed.pycommon import gmI18N
	gmI18N.activate_locale()
	gmI18N.install_domain()

from Gnumed.wxpython import gmPlugin
from Gnumed.wxpython import gmExportAreaWidgets


_log = logging.getLogger('gm.ui')
#================================================================
class gmPrintManagerPlugin(gmPlugin.cNotebookPlugin):
	tab_name = _("Print Manager")

	def name (self):
		return gmPrintManagerPlugin.tab_name
	#--------------------------------------------------------
	def GetWidget (self, parent):
		self._widget = gmExportAreaWidgets.cPrintMgrPluginPnl(parent, -1)
		return self._widget
	#--------------------------------------------------------
	def MenuInfo (self):
		return ('paperwork', _('&Print Manager'))
	#--------------------------------------------------------
	def can_receive_focus(self):
		#if not self._verify_patient_avail():
		#	return None
		return 1
	#--------------------------------------------------------
	def _on_raise_by_signal(self, **kwds):
		if not gmPlugin.cNotebookPlugin._on_raise_by_signal(self, **kwds):
			return False
#		try:
#			# add here any code you for the plugin executed after
#			# raising the pugin
#			pass
#		except KeyError:
#			pass
		return True
#================================================================
# MAIN
#----------------------------------------------------------------
if __name__ == '__main__':

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
