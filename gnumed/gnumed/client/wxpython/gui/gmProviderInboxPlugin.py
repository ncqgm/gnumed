# -*- coding: utf-8 -*-
#=====================================================
# GNUmed provider inbox plugin
# later to evolve into a more complete "provider-centric hub"
#=====================================================
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL"

from Gnumed.wxpython import gmPlugin, gmProviderInboxWidgets
from Gnumed.wxpython import gmAccessPermissionWidgets

#======================================================================
class gmProviderInboxPlugin(gmPlugin.cNotebookPlugin):
	"""Plugin to encapsulate the provider inbox window."""

	tab_name = _('Inbox')
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
		gmPlugin.cNotebookPlugin.__init__(self)
	#--------------------------------------------------------
	def name(self):
		return gmProviderInboxPlugin.tab_name
	#--------------------------------------------------------
	def GetWidget(self, parent):
		self._widget = gmProviderInboxWidgets.cProviderInboxPnl(parent, -1)
		return self._widget
	#--------------------------------------------------------
	def MenuInfo(self):
		return ('office', _('Provider &inbox'))
	#--------------------------------------------------------
	def can_receive_focus(self):
		return True
	#--------------------------------------------------------
	def _on_raise_by_signal(self, **kwds):
		if not gmPlugin.cNotebookPlugin._on_raise_by_signal(self, **kwds):
			return False

		try:
			if kwds['filter_by_active_patient'] is True:
				self._widget.filter_by_active_patient()
		except KeyError:
			pass

		return True

#======================================================================
