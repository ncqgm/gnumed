# -*- coding: utf-8 -*-
"""GNUmed file preview widgets."""
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
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmMimeLib
from Gnumed.pycommon import gmWorkerThread


_log = logging.getLogger('gm.preview')

#============================================================
from Gnumed.wxGladeWidgets.wxgFilePreviewPnl import wxgFilePreviewPnl

class cFilePreviewPnl(wxgFilePreviewPnl):
	"""Panel for previewing a file as image or text."""
	def __init__(self, *args, **kwargs):
		self.__filename = None
		try:
			fname = kwargs['filename']
			del kwargs['filename']
		except KeyError:
			fname = None
		super().__init__(*args, **kwargs)
		self.filename = fname

	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def __get_filename(self):
		return self.__filename

	def __set_filename(self, filename):
		if filename == self.__filename:
			return

		self._PNL_image_preview.filename = None
		self._PNL_image_preview.Hide()
		self._TCTRL_text_preview.Value = ''
		self._TCTRL_text_preview.Hide()
		if not filename:
			self.__filename = None
			self.Layout()
			return

		self.__filename = filename
		self.__worker_cookie4img = '%s-%s4img' % (self.__class__.__name__, filename)
		self.__worker_cookie4text = '%s-%s2txt' % (self.__class__.__name__, filename)
		gmWorkerThread.execute_in_worker_thread (
			payload_function = self._worker__convert_to_images,
			payload_kwargs = {'filename': filename, 'cookie': self.__worker_cookie4img},
			completion_callback = self._forwarder__update_image_preview,
			worker_name = self.__class__.__name__
		)
		gmWorkerThread.execute_in_worker_thread (
			payload_function = self._worker__convert_to_text,
			payload_kwargs = {'filename': filename, 'cookie': self.__worker_cookie4text},
			completion_callback = self._forwarder__update_text_preview,
			worker_name = self.__class__.__name__
		)
		if gmMimeLib.is_probably_textfile(filename):
			self.__show_text_preview()
		else:
			self.__show_image_preview()
		self.Layout()

	filename = property(__get_filename, __set_filename)

	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	# image preview
	#--------------------------------------------------------
	def _worker__convert_to_images(self, filename:str=None, cookie=None) -> str:
		return cookie, gmMimeLib.convert_file_to_image(filename)

	#--------------------------------------------------------
	def _forwarder__update_image_preview(self, worker_result):
		cookie, img_fnames = worker_result
		if cookie != self.__worker_cookie4img:
			_log.debug('received results from old worker [%s], I am [%s], ignoring', cookie, self.__worker_cookie4img)
			return

		if not img_fnames:
			return

		wx.CallAfter(self.__update_image_preview, filename = img_fnames[0])

	#--------------------------------------------------------
	def __update_image_preview(self, filename):
		self._PNL_image_preview.filename = filename
		self.__update_page_label()
		self.Layout()

	#--------------------------------------------------------
	def __show_image_preview(self):
		self._TCTRL_text_preview.Hide()
		self._PNL_image_preview.Show()
		self.__update_page_label()
		self._LBL_parts.Show()
		self.Layout()

	#--------------------------------------------------------
	# text preview
	#--------------------------------------------------------
	def _worker__convert_to_text(self, filename:str=None, cookie=None) -> str:
		text_fname = gmMimeLib.convert_file_to_text(filename)
		if text_fname:
			with open(text_fname, mode = 'rt', encoding = 'utf-8', errors = 'replace') as txt_file:
				text = txt_file.read()
		else:
			text = ''
		status, metadata, _cookie = gmMimeLib.describe_file(filename, cookie = cookie)
		if status:
			if text:
				text += ('\n\n%s\n' % (gmTools.u_box_horiz_single * 80))
				text += ' '
				text += _('File description/metadata appended')
				text += ('\n%s\n' % (gmTools.u_box_horiz_single * 80))
			text += metadata
		if not text:
			text = _('No text content found.')
		return cookie, text

	#--------------------------------------------------------
	def _forwarder__update_text_preview(self, worker_result):
		cookie, text = worker_result
		if cookie != self.__worker_cookie4text:
			_log.debug('received results from old worker [%s], I am [%s], ignoring', cookie, self.__worker_cookie4text)
			return

		wx.CallAfter(self.__update_text_preview, text = text)

	#--------------------------------------------------------
	def __update_text_preview(self, text):
		self._TCTRL_text_preview.Value = text

	#--------------------------------------------------------
	def __show_text_preview(self):
		self._PNL_image_preview.Hide()
		self._LBL_parts.Hide()
		self._TCTRL_text_preview.Show()
		self.Layout()

	#--------------------------------------------------------
	def __update_page_label(self):
		self._LBL_parts.Label = _('Page %s/%s') % (self._PNL_image_preview.current_page, self._PNL_image_preview.page_count)
		self._LBL_parts.Refresh()

	#--------------------------------------------------------
	# event handlers
	#--------------------------------------------------------
	def _on_switch_preview_button_pressed(self, event):
		event.Skip()
		if self._PNL_image_preview.IsShown():
			self.__show_text_preview()
		else:
			self.__show_image_preview()
			self._PNL_image_preview._BMP_image.SetFocus()

	#--------------------------------------------------------
	def _on_view_externally_button_pressed(self, event):
		event.Skip()
		if not self.filename:
			return

		gmMimeLib.call_viewer_on_file(self.filename)

	#--------------------------------------------------------
	def _on_prev_page_button_pressed(self, event):
		event.Skip()
		self._PNL_image_preview.show_previous_page()
		self.__update_page_label()
		self.Layout()

	#--------------------------------------------------------
	def _on_first_page_button_pressed(self, event):
		event.Skip()
		self._PNL_image_preview.show_first_page()
		self.__update_page_label()
		self.Layout()

	#--------------------------------------------------------
	def _on_next_page_button_pressed(self, event):
		event.Skip()
		self._PNL_image_preview.show_next_page()
		self.__update_page_label()
		self.Layout()

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
		gmGuiTest.test_widget(cFilePreviewPnl, patient = None, filename = sys.argv[2])

	#--------------------------------------------------------
	test_plugin()
