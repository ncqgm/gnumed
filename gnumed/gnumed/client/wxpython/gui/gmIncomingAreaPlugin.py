# -*- coding: utf-8 -*-

"""GNUmed document inbox plugin"""
#======================================================================
__license__ = 'GPL v2 or later (details at https://www.gnu.org)'

import sys
import logging


if __name__ == '__main__':
	sys.path.insert(0, '../../../')
	_ = lambda x:x
else:
	try: _
	except NameError:
		from Gnumed.pycommon import gmI18N
		gmI18N.activate_locale()
		gmI18N.install_domain()


from Gnumed.wxpython import gmPlugin
from Gnumed.wxpython import gmIncomingDataWidgets
from Gnumed.wxpython import gmAccessPermissionWidgets


_log = logging.getLogger('gm.auto-in-ui')

#======================================================================
class gmIncomingAreaPlugin(gmPlugin.cNotebookPlugin):

	tab_name = _('Docs Inbox')
	required_minimum_role = 'full clinical access'

	@gmAccessPermissionWidgets.verify_minimum_required_role (
		required_minimum_role,
		activity = _('loading plugin <%s>') % tab_name,
		return_value_on_failure = False,
		fail_silently = False
	)
	def register(self):
		gmPlugin.cNotebookPlugin.register(self)

	def name(self):
		return type(self).tab_name

	def GetWidget(self, parent):
		self._widget = gmIncomingDataWidgets.cIncomingPluginPnl(parent, -1)
		return self._widget

	def MenuInfo(self):
		return ('emr', _('&Attach documents'))

	def can_receive_focus(self):
		return 1

#============================================================
# main
#------------------------------------------------------------
if __name__ == "__main__":

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	from Gnumed.pycommon import gmLog2
	del _
	from Gnumed.pycommon import gmI18N
	gmI18N.activate_locale()
	gmI18N.install_domain()

	from Gnumed.wxpython import gmGuiTest

	#--------------------------------------------------------
	def test_plugin():
		#wx.Log.EnableLogging(enable = False)
		gmGuiTest.test_widget(gmIncomingAreaPlugin, patient = 12)

	#--------------------------------------------------------
	test_plugin()
