"""GNUmed TextCtrl sbuclass."""
#===================================================
__author__  = "K. Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL v2 or later (details at http://www.gnu.org)"

import logging
import sys


import wx


if __name__ == '__main__':
	sys.path.insert(0, '../../')

from Gnumed.wxpython import gmKeywordExpansionWidgets


_log = logging.getLogger('gm.txtctrl')

#===================================================
class cTextCtrl(wx.TextCtrl, gmKeywordExpansionWidgets.cKeywordExpansion_TextCtrlMixin):

	def __init__(self, *args, **kwargs):

		wx.TextCtrl.__init__(self, *args, **kwargs)
		gmKeywordExpansionWidgets.cKeywordExpansion_TextCtrlMixin.__init__(self)
		self.enable_keyword_expansions()

#===================================================
# main
#---------------------------------------------------
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != u'test':
		sys.exit()

	from Gnumed.pycommon import gmI18N
	gmI18N.activate_locale()
	gmI18N.install_domain(domain='gnumed')

	#-----------------------------------------------
	def test_gm_textctrl():
		app = wx.PyWidgetTester(size = (200, 50))
		tc = cTextCtrl(parent = app.frame, id = -1)
		#tc.enable_keyword_expansions()
		app.frame.Show(True)
		app.MainLoop()
		return True
	#-----------------------------------------------
	test_gm_textctrl()

#---------------------------------------------------
