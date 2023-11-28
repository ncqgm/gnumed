# -*- coding: utf-8 -*-
"""GNUmed PDF viewer.

	Simple rendering only.
"""
#============================================================
# SPDX-License-Identifier: GPL-2.0-or-later
__author__ = "Karsten.Hilbert@gmx.net"
__license__ = "GPL v2 or later"


import sys
import logging


if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x
else:
	try: _
	except NameError:
		from Gnumed.pycommon import gmI18N
		gmI18N.activate_locale()
		gmI18N.install_domain()


_log = logging.getLogger('gm.pdf_vwr')

#============================================================
from Gnumed.wxGladeWidgets.wxgPDFViewerPnl import wxgPDFViewerPnl

class cPDFViewerPnl(wxgPDFViewerPnl):
	"""Panel showing a PDF and manipulation controls."""
	def __init__(self, *args, **kwargs):
		try:
			fname = kwargs['filename']
			del kwargs['filename']
		except KeyError:
			fname = None
		super().__init__(*args, **kwargs)
		self._PDF_control_buttons_pnl.viewer = self._PDF_content_pnl
		self._PDF_content_pnl.buttonpanel = self._PDF_control_buttons_pnl
		if fname:
			self.filename = fname

	#--------------------------------------------------------
	def __get_filename(self):
		return self._PDF_content_pnl.filename

	def __set_filename(self, filename=None):
		self._PDF_content_pnl.filename = filename

	filename = property(__get_filename, __set_filename)

#============================================================
# main
#------------------------------------------------------------
if __name__ == "__main__":

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	del _
	from Gnumed.pycommon import gmI18N
	gmI18N.activate_locale()
	gmI18N.install_domain()

	from Gnumed.wxpython import gmGuiTest

	#--------------------------------------------------------
	def test_plugin():
		gmGuiTest.test_widget(cPDFViewerPnl, filename = sys.argv[2])

	#--------------------------------------------------------
	test_plugin()
