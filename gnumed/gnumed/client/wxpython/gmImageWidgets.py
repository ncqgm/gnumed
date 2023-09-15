# -*- coding: utf-8 -*-
"""GNUmed image display widgets."""
#============================================================
# SPDX-License-Identifier: GPL-2.0-or-later
__author__ = "Karsten.Hilbert@gmx.net"
__license__ = "GPL v2 or later"


import sys
import logging


import wx
import wx.lib.statbmp


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
class cImageDisplay(wx.lib.statbmp.GenStaticBitmap):
	"""Control showing an image."""
	def __init__(self, parent, ID, bitmap, **kwargs):
		self.__empty_bmp = wx.Bitmap(wx.Image(1, 1, True))
		super().__init__(parent, ID, self.__empty_bmp, **kwargs)
		self.__init_ui()
		self.__filename = None
		self.__target_width = 0
		self.__zoom_count = 0
		self.__min_width = 25
		self.__current_rotation = 0		# in degrees
		self.__callback_on_lclick = None
		self.refresh()

	#--------------------------------------------------------
	def process_char(self, char) -> bool:
		"""Call action based  on character.

		Returns:
			True/False based on whether the character mapped to a command.
		"""
		match char:
			case 'r':
				self.__current_rotation += 90
				if self.__current_rotation == 360:
					self.__current_rotation = 0
				self.refresh()
			case 'l':
				self.__current_rotation -= 90
				if self.__current_rotation == -360:
					self.__current_rotation = 0
				self.refresh()
			case 'o':
				self.__zoom_count = 0
				self.refresh()
			case '+':
				self.__zoom_count += 1
				self.refresh()
			case '-':
				self.__zoom_count -= 1
				self.refresh()
			case _:
				return False

		return True

	#--------------------------------------------------------
	def display_file(self, filename:str, target_width:int=None) -> bool:
		if target_width:
			self.__target_width = target_width
		self.__filename = filename
		return self.refresh()

	#--------------------------------------------------------
	# event handlers
	#--------------------------------------------------------
	def _on_bitmap_leftclicked(self, event):
		self.SetFocus()
		if not self.__callback_on_lclick:
			return

		self.__callback_on_lclick()

	#--------------------------------------------------------
	def _on_char(self, event):
		uk = event.UnicodeKey
		if uk != wx.WXK_NONE:
			if not self.process_char(chr(uk)):
				event.Skip()
			return

#		kc = event.KeyCode
#		if kc != wx.WXK_NONE:
#			if not self.process_keycode(kc):
#				event.Skip()
#			return

		print('unmapped key:', event.RawKeyCode)

	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def __get_filename(self):
		return self.__filename

	def __set_filename(self, filename):
		self.__zoom_count = 0
		self.__current_rotation = 0
		self.display_file(filename)

	filename = property(__get_filename, __set_filename)

	#--------------------------------------------------------
	def __get_target_width(self):
		return self.__target_width

	def __set_target_width(self, width):
		self.__target_width = width

	target_width = property(__get_target_width, __set_target_width)

	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def __init_ui(self):
		self.Bind(wx.EVT_LEFT_UP, self._on_bitmap_leftclicked)
		self.Bind(wx.EVT_CHAR, self._on_char)

	#--------------------------------------------------------
	def __rescale2width(self):
		try:
			img_data = wx.Image(self.__filename, wx.BITMAP_TYPE_ANY)
			orig_width = img_data.GetWidth()
		except Exception:
			_log.exception('cannot load image from [%s]', self.__filename)
			return False

		if self.__target_width:
			target_width = max(self.__target_width, self.__min_width)
		else:
			target_width = max(orig_width, self.__min_width)
		try:
			orig_height = img_data.GetHeight()
			target_height = round(orig_height / orig_width) * target_width
			img_data.Rescale(target_width, target_height, quality = wx.IMAGE_QUALITY_HIGH)
		except Exception:
			_log.exception('cannot resize image from [%s]', self.__filename)
			return False

		try:
			bitmap = wx.Bitmap(img_data)
		except Exception:
			_log.exception('cannot create bitmap from image in [%s]', self.__filename)
			return False

		return bitmap

	#--------------------------------------------------------
	def __adjust_bitmap(self):
		img_data = None
		bitmap = None
		try:
			img_data = wx.Image(self.__filename, wx.BITMAP_TYPE_ANY)
			orig_width = img_data.GetWidth()
		except Exception:
			_log.exception('cannot load image from [%s]', self.__filename)
			return False

		zoom_step = orig_width // 10
		target_width = orig_width + (zoom_step * self.__zoom_count)
		target_width = max(target_width, self.__min_width)
		try:
			orig_height = img_data.GetHeight()
			target_height = round(orig_height / orig_width) * target_width
			img_data.Rescale(target_width, target_height, quality = wx.IMAGE_QUALITY_HIGH)
			for cnt in range(abs(self.__current_rotation) // 90):
				img_data = img_data.Rotate90(clockwise = self.__current_rotation > 0)
		except Exception:
			_log.exception('cannot resize/rotate image from [%s]', self.__filename)
			return False

		try:
			bitmap = wx.Bitmap(img_data)
		except Exception:
			_log.exception('cannot create bitmap from image in [%s]', self.__filename)
			return False

		return bitmap

	#--------------------------------------------------------
	def refresh(self):
		self.SetBitmap(self.__empty_bmp)
		if not self.__filename:
			return None

		#bitmap = self.__rescale2width()
		bitmap = self.__adjust_bitmap()
		if not bitmap:
			return False

		self.SetBitmap(bitmap)
		return True

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
	def test_plugin2():
		main_frame = gmGuiTest.setup_widget_test_env(patient = 12)
		main_pnl = wx.Panel(main_frame)
		img_display = cImageDisplay(main_pnl, ID = -1, bitmap = None)
		img_display.patient = gmPerson.gmCurrentPatient()
		img_display.target_width = 800
		img_display.filename = sys.argv[2]
		main_szr = wx.BoxSizer(wx.VERTICAL)
		main_szr.Add(img_display)
		main_pnl.SetSizer(main_szr)
		main_szr.SetSizeHints(main_frame)
		main_frame.Show()
		wx.GetApp().MainLoop()

	#--------------------------------------------------------
	def test_plugin():
		gmGuiTest.test_widget(cImageDisplay, patient = 12)

	#--------------------------------------------------------
	#test_plugin()
	test_plugin2()
