# -*- coding: utf-8 -*-
"""GNUmed image display widgets."""
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
	try: _		# do we already have _() ?
	except NameError:
		from Gnumed.pycommon import gmI18N
		gmI18N.activate_locale()
		gmI18N.install_domain()

from Gnumed.pycommon import gmMimeLib


_log = logging.getLogger('gm.img_ui')

#============================================================
from Gnumed.wxGladeWidgets.wxgSingleFileImageViewerPnl import wxgSingleFileImageViewerPnl

class cSingleFileImageViewerPnl(wxgSingleFileImageViewerPnl):
	"""Panel showing an image allowing for manipulation.

	Knows how to handle multi-page image formats.
	"""
	def __init__(self, *args, **kwargs):
		try:
			fname = kwargs['filename']
			del kwargs['filename']
		except KeyError:
			fname = None
		self.__filename = None
		self.__current_page = 0
		self.__image_pages = 0
		super().__init__(*args, **kwargs)
		self.filename = fname

	#--------------------------------------------------------
	def show_previous_page(self):
		if not self.__image_pages:
			return

		if self.__current_page == 0:
			return

		self.__current_page -= 1
		self._BMP_image.filename = self.__image_pages[self.__current_page]

	#--------------------------------------------------------
	def show_next_page(self):
		if not self.__image_pages:
			return

		if self.__current_page + 1 == len(self.__image_pages):
			return

		self.__current_page += 1
		self._BMP_image.filename = self.__image_pages[self.__current_page]

	#--------------------------------------------------------
	def show_first_page(self):
		if not self.__image_pages:
			return

		self.__current_page = 0
		self._BMP_image.filename = self.__image_pages[0]

	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def __get_filename(self):
		return self.__filename

	def __set_filename(self, filename):
		if filename == self.__filename:
			return

		self.__current_page = 0
		if not filename:
			self.__image_pages = []
			self.__filename = None
			self._BMP_image.filename = None
			self.Layout()
			return

		self.__image_pages = gmMimeLib.split_multipage_image(filename)
		if not self.__image_pages:
			self.__filename = None
			self._BMP_image.filename = None
			self.Layout()
			return

		self.__filename = filename
		self._BMP_image.filename = self.__image_pages[0]
		self.Layout()

	filename = property(__get_filename, __set_filename)

	#--------------------------------------------------------
	def __get_page_count(self):
		if not self.__image_pages:
			return 0

		return len(self.__image_pages)

	page_count = property(__get_page_count)

	#--------------------------------------------------------
	def __get_current_page(self):
		if not self.__image_pages:
			return 0

		return self.__current_page + 1

	current_page = property(__get_current_page)

	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------

	#--------------------------------------------------------
	# event handlers
	#--------------------------------------------------------

#============================================================
# main
#------------------------------------------------------------
if __name__ == "__main__":

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	# setup a real translation
	del _
	from Gnumed.pycommon import gmI18N
	gmI18N.activate_locale()
	gmI18N.install_domain()

	from Gnumed.wxpython import gmGuiTest

	#--------------------------------------------------------
	def test_plugin():
		gmGuiTest.test_widget(cSingleFileImageViewerPnl, patient = None, filename = sys.argv[2])

	#--------------------------------------------------------
	test_plugin()
