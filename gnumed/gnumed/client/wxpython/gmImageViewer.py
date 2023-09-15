# -*- coding: utf-8 -*-
"""GNUmed image display widgets."""
#============================================================
# SPDX-License-Identifier: GPL-2.0-or-later
__author__ = "Karsten.Hilbert@gmx.net"
__license__ = "GPL v2 or later"


import sys
import logging


import wx


if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x
else:
	try: _		# do we already have _() ?
	except NameError:
		from Gnumed.pycommon import gmI18N
		gmI18N.activate_locale()
		gmI18N.install_domain()


_log = logging.getLogger('gm.img_ui')

#============================================================
from Gnumed.wxGladeWidgets.wxgSingleImageViewerPnl import wxgSingleImageViewerPnl

class cSingleImageViewerPnl(wxgSingleImageViewerPnl):
	"""Panel showing an image allowing for manipulation."""
	def __init__(self, *args, **kwargs):
		try:
			fname = kwargs['filename']
			del kwargs['filename']
		except KeyError:
			fname = None
		super().__init__(*args, **kwargs)
		self._BMP_image.filename = fname

#		self.Bind(wx.EVT_CHAR, self._on_char)

	#--------------------------------------------------------
	def process_char(self, char) -> bool:
		return self._BMP_image.process_char(char)

#	#--------------------------------------------------------
#	def process_keycode(self, keycode) -> bool:
#		"""Call action based  on translated key code.
#
#		Returns:
#			True/False based on whether the key code mapped to a command.
#		"""
#		match keycode:
#			case 317:
#				print('scroll down')
#				x_scroll_step, y_scroll_step = self.GetScrollPixelsPerUnit()
#				x_view, y_view = self.GetViewStart()
#				print('going to:', x_view, y_view + y_scroll_step)
#				self.Scroll(x_view, y_view + y_scroll_step)
#			case 315: print('scroll up')
#			case 314: print('scroll left')
#			case 316: print('scroll right')
#			case _:
#				return False
#
#		return True

	#--------------------------------------------------------

	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def __get_filename(self):
		return self._BMP_image.filename

	def __set_filename(self, filename):
		self._BMP_image.filename = filename
		self.Layout()

	filename = property(__get_filename, __set_filename)

	#--------------------------------------------------------
	def __get_target_width(self):
		return self._BMP_image.__target_width

	def __set_target_width(self, width):
		self._BMP_image.__target_width = width

	target_width = property(__get_target_width, __set_target_width)

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

	from Gnumed.business import gmPerson
	from Gnumed.wxpython import gmGuiTest

	#--------------------------------------------------------
	def test_plugin():
		gmGuiTest.test_widget(cSingleImageViewerPnl, patient = None, filename = sys.argv[2])

	#--------------------------------------------------------
	test_plugin()
