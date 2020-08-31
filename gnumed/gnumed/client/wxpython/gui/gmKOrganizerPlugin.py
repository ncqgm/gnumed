# -*- coding: utf-8 -*-

"""GNUmed KOrganizer link"""
#=====================================================
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL v2 or later"

from Gnumed.wxpython import gmPlugin, gmDemographicsWidgets
from Gnumed.pycommon import gmExceptions, gmShellAPI
from Gnumed.wxpython import gmAccessPermissionWidgets

if __name__ == '__main__':
	_ = lambda x:x

#======================================================================
class gmKOrganizerPlugin(gmPlugin.cNotebookPlugin):
	"""Plugin to encapsulate a simple KOrganizer link window."""

	tab_name = _('Appointments')
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
	#--------------------------------------------------------
	def __init__(self):
		# detect KOrganizer
		found, cmd = gmShellAPI.detect_external_binary(binary = 'konsolekalendar')
		if not found:
			raise gmExceptions.ConstructorError('cannot detect "konsolekalendar" via [%s]' % cmd)

		gmPlugin.cNotebookPlugin.__init__(self)
	#--------------------------------------------------------
	def name(self):
		return gmKOrganizerPlugin.tab_name
	#--------------------------------------------------------
	def GetWidget(self, parent):
		self._widget = gmDemographicsWidgets.cKOrganizerSchedulePnl(parent, -1)
		return self._widget
	#--------------------------------------------------------
	def MenuInfo(self):
		return ('office', _('&Appointments'))
	#--------------------------------------------------------
	def can_receive_focus(self):
		return True

#======================================================================
