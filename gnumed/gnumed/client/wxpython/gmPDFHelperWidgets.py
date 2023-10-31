# -*- coding: utf-8 -*-
"""GNUmed PDF display panel."""
#============================================================
# SPDX-License-Identifier: GPL-2.0-or-later
__author__ = "Karsten.Hilbert@gmx.net"
__license__ = "GPL v2 or later"


import sys
import logging


import wx.lib.pdfviewer as pdflib


if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x
else:
	try: _
	except NameError:
		from Gnumed.pycommon import gmI18N
		gmI18N.activate_locale()
		gmI18N.install_domain()


_log = logging.getLogger('gm.pdf_hlpr')

#============================================================
class cPDFButtonPnl(pdflib.pdfButtonPanel):
	"""Panel showing manipulation buttons."""
	def __init__(self, *args, **kwargs):
		pos_args = list(args)
		if len(pos_args) == 1:
			pos_args.append(-1)
		if len(pos_args) == 2:
			pos_args.append((-1, -1))
		if len(pos_args) == 3:
			pos_args.append((-1, -1))
		if len(pos_args) == 4:	# style
			try:
				pos_args.append(kwargs['style'])
				del kwargs['style']
			except KeyError:
				pos_args.append(-1)
		args = tuple(pos_args)
		super().__init__(*args, **kwargs)

#============================================================
class cPDFContentPnl(pdflib.pdfViewer):
	"""Panel showing a PDF."""
	def __init__(self, *args, **kwargs):
		pos_args = list(args)
		if len(pos_args) == 1:
			pos_args.append(-1)
		if len(pos_args) == 2:
			pos_args.append((-1, -1))
		if len(pos_args) == 3:
			pos_args.append((-1, -1))
		if len(pos_args) == 4:	# style
			try:
				pos_args.append(kwargs['style'])
				del kwargs['style']
			except KeyError:
				pos_args.append(-1)
		args = tuple(pos_args)
		try:
			super().__init__(*args, **kwargs)
			self.__stub = False
			self.ShowLoadProgress = True
		except ImportError:
			_log.exception('Cannot import PDF pnl, missing module ?')
			self.__stub = True

	#--------------------------------------------------------
	def LoadFile(self, pdf_file):
		if self.__stub:
			return

		return super().LoadFile(pdf_file)

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
		gmGuiTest.test_widget(cPDFContentPnl)

	#--------------------------------------------------------
	test_plugin()
