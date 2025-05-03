"""GNUmed GUI helper classes and functions.

This module provides some convenient wxPython GUI
helper thingies that are widely used throughout
GNUmed.
"""
# ========================================================================
__author__  = "K. Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL v2 or later (details at http://www.gnu.org)"

import os
import logging
import sys
import io
import time
import datetime as pyDT


import wx


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmMatchProvider
from Gnumed.pycommon import gmExceptions
from Gnumed.pycommon import gmLog2
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmDispatcher
from Gnumed.wxpython import gmPhraseWheel


_log = logging.getLogger('gm.main')
# ========================================================================
class cThreeValuedLogicPhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):

		gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)

		items = [
			{'list_label': _('Yes: + / ! / 1'), 'field_label': _('yes'), 'data': True, 'weight': 0},
			{'list_label': _('No: - / 0'), 'field_label': _('no'), 'data': False, 'weight': 1},
			{'list_label': _('Unknown: ?'), 'field_label': _('unknown'), 'data': None, 'weight': 2},
		]
		mp = gmMatchProvider.cMatchProvider_FixedList(items)
		mp.setThresholds(1, 1, 2)
		mp.word_separators = '[ :/]+'
		mp.word_separators = None
		mp.ignored_chars = r"[.'\\(){}\[\]<>~#*$%^_=&@\t23456]+" + r'"'

		self.matcher = mp
# ========================================================================
from Gnumed.wxGladeWidgets import wxg2ButtonQuestionDlg

class c2ButtonQuestionDlg(wxg2ButtonQuestionDlg.wxg2ButtonQuestionDlg):

	def __init__(self, *args, **kwargs):

		caption = kwargs['caption']
		question = kwargs['question']
		button_defs = kwargs['button_defs'][:2]
		del kwargs['caption']
		del kwargs['question']
		del kwargs['button_defs']

		try:
			show_checkbox = kwargs['show_checkbox']
			del kwargs['show_checkbox']
		except KeyError:
			show_checkbox = False

		try:
			checkbox_msg = kwargs['checkbox_msg']
			del kwargs['checkbox_msg']
		except KeyError:
			checkbox_msg = None

		try:
			checkbox_tooltip = kwargs['checkbox_tooltip']
			del kwargs['checkbox_tooltip']
		except KeyError:
			checkbox_tooltip = None

		wxg2ButtonQuestionDlg.wxg2ButtonQuestionDlg.__init__(self, *args, **kwargs)

		self.SetTitle(title = gmTools.decorate_window_title(caption))
		self._LBL_question.SetLabel(label = question)

		if not show_checkbox:
			self._CHBOX_dont_ask_again.Hide()
		else:
			if checkbox_msg is not None:
				self._CHBOX_dont_ask_again.SetLabel(checkbox_msg)
			if checkbox_tooltip is not None:
				self._CHBOX_dont_ask_again.SetToolTip(checkbox_tooltip)

		buttons = [self._BTN_1, self._BTN_2]
		for idx in range(len(button_defs)):
			buttons[idx].SetLabel(label = button_defs[idx]['label'])
			buttons[idx].SetToolTip(button_defs[idx]['tooltip'])
			try:
				if button_defs[idx]['default'] is True:
					buttons[idx].SetDefault()
					buttons[idx].SetFocus()
			except KeyError:
				pass

		self.Fit()
	#--------------------------------------------------------
	def checkbox_is_checked(self):
		return self._CHBOX_dont_ask_again.IsChecked()
	#--------------------------------------------------------
	# event handlers
	#--------------------------------------------------------
	def _on_BTN_1_pressed(self, evt):
		if self.IsModal():
			self.EndModal(wx.ID_YES)
		else:
			self.Close()
	#--------------------------------------------------------
	def _on_BTN_2_pressed(self, evt):
		if self.IsModal():
			self.EndModal(wx.ID_NO)
		else:
			self.Close()

# ========================================================================
from Gnumed.wxGladeWidgets import wxg3ButtonQuestionDlg

class c3ButtonQuestionDlg(wxg3ButtonQuestionDlg.wxg3ButtonQuestionDlg):

	def __init__(self, *args, **kwargs):
		"""Initialize.

	button_defs = [
		# tooltip and default are optional
		{'label': _(''), 'tooltip': _(''), 'default': True/False},
		{'label': _(''), 'tooltip': _(''), 'default': True/False},
		{'label': _(''), 'tooltip': _(''), 'default': True/False}
	]
		"""
		caption = kwargs['caption']
		question = kwargs['question']
		button_defs = kwargs['button_defs'][:3]
		del kwargs['caption']
		del kwargs['question']
		del kwargs['button_defs']

		try:
			show_checkbox = kwargs['show_checkbox']
			del kwargs['show_checkbox']
		except KeyError:
			show_checkbox = False

		try:
			checkbox_msg = kwargs['checkbox_msg']
			del kwargs['checkbox_msg']
		except KeyError:
			checkbox_msg = None

		try:
			checkbox_tooltip = kwargs['checkbox_tooltip']
			del kwargs['checkbox_tooltip']
		except KeyError:
			checkbox_tooltip = None

		wxg3ButtonQuestionDlg.wxg3ButtonQuestionDlg.__init__(self, *args, **kwargs)

		self.SetTitle(title = gmTools.decorate_window_title(caption))
		self._LBL_question.SetLabel(label = question)

		if not show_checkbox:
			self._CHBOX_dont_ask_again.Hide()
		else:
			if checkbox_msg is not None:
				self._CHBOX_dont_ask_again.SetLabel(checkbox_msg)
			if checkbox_tooltip is not None:
				self._CHBOX_dont_ask_again.SetToolTip(checkbox_tooltip)

		buttons = [self._BTN_1, self._BTN_2, self._BTN_3]
		for idx in range(len(button_defs)):
			buttons[idx].SetLabel(label = button_defs[idx]['label'])
			try:
				buttons[idx].SetToolTip(button_defs[idx]['tooltip'])
			except KeyError:
				pass
			try:
				if button_defs[idx]['default'] is True:
					buttons[idx].SetDefault()
					buttons[idx].SetFocus()
			except KeyError:
				pass

		self.Fit()
	#--------------------------------------------------------
	def checkbox_is_checked(self):
		return self._CHBOX_dont_ask_again.IsChecked()

	#--------------------------------------------------------
	# event handlers
	#--------------------------------------------------------
	def _on_BTN_1_pressed(self, evt):
		if self.IsModal():
			self.EndModal(wx.ID_YES)
		else:
			self.Close()

	#--------------------------------------------------------
	def _on_BTN_2_pressed(self, evt):
		if self.IsModal():
			self.EndModal(wx.ID_NO)
		else:
			self.Close()

# ========================================================================
from Gnumed.wxGladeWidgets import wxgMultilineTextEntryDlg

class cMultilineTextEntryDlg(wxgMultilineTextEntryDlg.wxgMultilineTextEntryDlg):
	"""Editor for a bit of text."""

	def __init__(self, *args, **kwargs):

		try:
			title = kwargs['title']
			del kwargs['title']
		except KeyError:
			title = None

		try:
			msg = kwargs['msg']
			del kwargs['msg']
		except KeyError:
			msg = None

		try:
			data = kwargs['data']
			del kwargs['data']
		except KeyError:
			data = None

		try:
			self.original_text = kwargs['text']
			del kwargs['text']
		except KeyError:
			self.original_text = None

		wxgMultilineTextEntryDlg.wxgMultilineTextEntryDlg.__init__(self, *args, **kwargs)

		if title is not None:
			self.SetTitle(gmTools.decorate_window_title(title))

		if self.original_text is not None:
			self._TCTRL_text.SetValue(self.original_text)
			self._BTN_restore.Enable(True)

		if msg is None:
			self._LBL_msg.Hide()
		else:
			self._LBL_msg.SetLabel(msg)
			self.Layout()
			self.Refresh()

		if data is None:
			self._TCTRL_data.Hide()
		else:
			self._TCTRL_data.SetValue(data)
			self.Layout()
			self.Refresh()

		self._TCTRL_text.SetFocus()
	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def _get_value(self):
		return self._TCTRL_text.GetValue()

	value = property(_get_value, lambda x:x)
	#--------------------------------------------------------
	def _get_is_user_formatted(self):
		return self._CHBOX_is_already_formatted.IsChecked()

	is_user_formatted = property(_get_is_user_formatted, lambda x:x)
	#--------------------------------------------------------
	def _set_enable_user_formatting(self, value):
		self._CHBOX_is_already_formatted.Enable(value)

	enable_user_formatting = property(lambda x:x, _set_enable_user_formatting)
	#--------------------------------------------------------
	# event handlers
	#--------------------------------------------------------
	def _on_save_button_pressed(self, evt):

		if self.IsModal():
			self.EndModal(wx.ID_SAVE)
		else:
			self.Close()
	#--------------------------------------------------------
	def _on_clear_button_pressed(self, evt):
		self._TCTRL_text.SetValue('')
	#--------------------------------------------------------
	def _on_restore_button_pressed(self, evt):
		if self.original_text is not None:
			self._TCTRL_text.SetValue(self.original_text)

# ========================================================================
def clipboard2text():

	if wx.TheClipboard.IsOpened():
		return False

	if not wx.TheClipboard.Open():
		return False

	data_obj = wx.TextDataObject()
	got_it = wx.TheClipboard.GetData(data_obj)
	if got_it:
		txt = data_obj.Text
		wx.TheClipboard.Close()
		return txt

	wx.TheClipboard.Close()
	return None

#-------------------------------------------------------------------------
def clipboard2file(check_for_filename=False):

	if wx.TheClipboard.IsOpened():
		return False

	if not wx.TheClipboard.Open():
		return False

	data_obj = wx.TextDataObject()
	got_it = wx.TheClipboard.GetData(data_obj)
	if got_it:
		clipboard_text_content = data_obj.Text
		wx.TheClipboard.Close()
		if check_for_filename:
			try:
				io.open(clipboard_text_content).close()
				return clipboard_text_content
			except IOError:
				_log.exception('clipboard does not seem to hold filename: %s', clipboard_text_content)
		fname = gmTools.get_unique_filename(prefix = 'gm-clipboard-', suffix = '.txt')
		target_file = io.open(fname, mode = 'wt', encoding = 'utf8')
		target_file.write(clipboard_text_content)
		target_file.close()
		return fname

	data_obj = wx.BitmapDataObject()
	got_it = wx.TheClipboard.GetData(data_obj)
	if got_it:
		fname = gmTools.get_unique_filename(prefix = 'gm-clipboard-', suffix = '.png')
		bmp = data_obj.Bitmap.SaveFile(fname, wx.BITMAP_TYPE_PNG)
		wx.TheClipboard.Close()
		return fname

	wx.TheClipboard.Close()
	return None

#-------------------------------------------------------------------------
def text2clipboard(text=None, announce_result=False):
	if wx.TheClipboard.IsOpened():
		return False
	if not wx.TheClipboard.Open():
		return False
	data_obj = wx.TextDataObject()
	data_obj.SetText(text)
	wx.TheClipboard.SetData(data_obj)
	wx.TheClipboard.Close()
	if announce_result:
		gmDispatcher.send(signal = 'statustext', msg = _('The text has been copied into the clipboard.'), beep = False)
	return True

#-------------------------------------------------------------------------
def file2clipboard(filename=None, announce_result=False):
	f = io.open(filename, mode = 'rt', encoding = 'utf8')
	result = text2clipboard(text = f.read(), announce_result = False)
	f.close()
	if announce_result:
		gm_show_info (
			title = _('file2clipboard'),
			info = _('The file [%s] has been copied into the clipboard.') % filename
		)
	return result

# ========================================================================
class cFileDropTarget(wx.FileDropTarget):
	"""Generic file drop target class.

	Protocol:
		Widgets being declared file drop targets
		must provide the method:

			def _drop_target_consume_filenames(self, filenames)

		or declare a callback during __init__() of this class.
	"""
	#-----------------------------------------------
	def __init__(self, target=None, on_drop_callback=None):
		if target is not None:
			on_drop_callback = getattr(target, '_drop_target_consume_filenames')
		if not callable(on_drop_callback):
			_log.error('[%s] not callable, cannot set as drop target callback', on_drop_callback)
			raise AttributeError('[%s] not callable, cannot set as drop target callback', on_drop_callback)

		self._on_drop_callback = on_drop_callback
		wx.FileDropTarget.__init__(self)
		_log.debug('setting up [%s] as file drop target', self._on_drop_callback)

	#-----------------------------------------------
	def OnDropFiles(self, x, y, filenames):
		self._on_drop_callback(filenames)

# ========================================================================
def file2scaled_image(filename:str=None, height:int=100):
	img_data = None
	bitmap = None
	rescaled_height = height
	try:
		img_data = wx.Image(filename, wx.BITMAP_TYPE_ANY)
		current_width = img_data.GetWidth()
		current_height = img_data.GetHeight()
		rescaled_width = round(current_width / current_height) * rescaled_height
		img_data.Rescale(rescaled_width, rescaled_height, quality = wx.IMAGE_QUALITY_HIGH)		# w, h
		bitmap = wx.Bitmap(img_data)
		del img_data
	except Exception:
		_log.exception('cannot load image from [%s]', filename)
		del img_data
		del bitmap
		return None

	return bitmap

# ========================================================================
def save_screenshot_to_file(filename:str=None, widget=None, settle_time:int=None) -> str:
	"""Take screenshot of widget or screen.

	Args:
		widget: the widget to screenshot (wx.Window descendent) or None for the whole screen
		settle_time: milliseconds to wait before taking screenshot

	Returns:
		Screenshot filename.

	https://github.com/wxWidgets/Phoenix/issues/259#issuecomment-801786528
	"""
	assert (isinstance(widget, wx.Window) or widget is None), '<widget> must be (sub)class of wx.Window, or None'

	if filename is None:
		filename = gmTools.get_unique_filename (
			prefix = 'gm-screenshot-%s-' % pyDT.datetime.now().strftime('%Y-%m-%d_%H-%M-%S'),
			suffix = '.png'
			# for testing:
			#,tmp_dir = os.path.join(gmTools.gmPaths().home_dir, 'gnumed')
		)
	else:
		filename = gmTools.fname_sanitize(filename)
	if settle_time is not None:
		for wait_slice in range(int(settle_time // 100)):
			wx.SafeYield()
			time.sleep(0.1)
	screen_dc = wx.ScreenDC()
	screen_dc_size = screen_dc.GetSize()
	_log.debug('filename: %s', filename)
	_log.debug('widget: %s', widget)
	_log.debug('wx.DisplaySize(): %s', wx.DisplaySize())
	_log.debug('wx.ScreenDC size: %s', screen_dc_size)
	# this line makes multiple screenshots work (perhaps it updates a cached/global screen_dc from a more "hardwary" screen ?)
	screen_dc.Blit(0, 0, screen_dc_size[0], screen_dc_size[1], screen_dc, 0, 0, logicalFunc = wx.OR)
	if widget is None:
		width2snap = screen_dc_size[0]
		height2snap = screen_dc_size[1]
		sane_x2snap_from_on_screen = 0
		sane_y2snap_from_on_screen = 0
	else:
		widget_rect_on_screen = widget.GetScreenRect()
		widget_rect_local = widget.GetRect()
		width2snap = widget_rect_local.width
		height2snap = widget_rect_local.height
		x2snap_from_on_screen = widget_rect_on_screen.x
		y2snap_from_on_screen = widget_rect_on_screen.y
		sane_x2snap_from_on_screen = max(0, x2snap_from_on_screen)
		sane_y2snap_from_on_screen = max(0, y2snap_from_on_screen)
		_log.debug('widget.GetScreenRect(): %s (= widget coords on screen)', widget_rect_on_screen)
		_log.debug('widget.GetRect(): %s (= widget coords on client area)', widget_rect_local)
		_log.debug('x2snap_from_on_screen: %s (neg is off-screen)', x2snap_from_on_screen)
		_log.debug('y2snap_from_on_screen: %s (neg is off-screen)', y2snap_from_on_screen)
	_log.debug('sane x2snap_from_on_screen: %s (on-screen part only)', sane_x2snap_from_on_screen)
	_log.debug('sane y2snap_from_on_screen: %s (on-screen part only)', sane_y2snap_from_on_screen)
	_log.debug('width2snap: %s', width2snap)
	_log.debug('height2snap: %s', height2snap)
	wxbmp = __snapshot_to_bitmap (
		source_dc = screen_dc,
		x2snap_from = sane_x2snap_from_on_screen,
		y2snap_from = sane_y2snap_from_on_screen,
		width2snap = width2snap,
		height2snap = height2snap
	)
	screen_dc.Destroy()
	del screen_dc
	wxbmp.SaveFile(filename, wx.BITMAP_TYPE_PNG)
	del wxbmp
	gmDispatcher.send(signal = 'statustext', msg = _('Saved screenshot to file [%s].') % filename)
	return filename

#-------------------------------------------------------------------------
def __snapshot_to_bitmap(source_dc=None, x2snap_from=0, y2snap_from=0, width2snap=1, height2snap=1):
	_log.debug('taking screenshot from %sx%s for %sx%s on [%s]', x2snap_from, y2snap_from, width2snap, height2snap, source_dc)
	target_dc = wx.MemoryDC()
	_log.debug('target DC: %s', target_dc)
	wxbmp = wx.Bitmap(width2snap, height2snap)
	target_dc.SelectObject(wxbmp)
	target_dc.Clear()						# wipe anything that might have been there in memory ?	taken from wxWidgets source
	target_dc.Blit (						# copy into this memory DC ...
		0, 0,								# ... to here in the memory DC (= target) ...
		width2snap, height2snap,			# ... that much ...
		source_dc,							# ... from the source DC ...
		x2snap_from, y2snap_from			# ... starting here
	)
	target_dc.SelectObject(wx.NullBitmap)	# disassociate wxbmp so it can safely be handled further
	target_dc.Destroy()						# destroy C++ object
	del target_dc
	return wxbmp

# ========================================================================
def gm_show_error(aMessage=None, aTitle = None, error=None, title=None):

	if error is None:
		error = aMessage
	if error is None:
		error = _('programmer forgot to specify error message')
	error += _("\n\nPlease consult the error log for all the gory details !")
	if title is None:
		title = aTitle
	if title is None:
		title = _('generic error message')
	dlg = wx.MessageDialog (
		parent = None,
		message = error,
		caption = gmTools.decorate_window_title(title),
		style = wx.OK | wx.ICON_ERROR | wx.STAY_ON_TOP
	)
	dlg.ShowModal()
	dlg.DestroyLater()
	return True

#-------------------------------------------------------------------------
def gm_show_info(aMessage=None, aTitle=None, info=None, title=None):

	if info is None:
		info = aMessage
	if info is None:
		info = _('programmer forgot to specify info message')
	if title is None:
		title = aTitle
	if title is None:
		title = _('generic info message')
	dlg = wx.MessageDialog (
		parent = None,
		message = info,
		caption = gmTools.decorate_window_title(title),
		style = wx.OK | wx.ICON_INFORMATION | wx.STAY_ON_TOP
	)
	dlg.ShowModal()
	dlg.DestroyLater()
	return True

#-------------------------------------------------------------------------
def gm_show_warning(aMessage=None, aTitle=None):
	if aMessage is None:
		aMessage = _('programmer forgot to specify warning')
	if aTitle is None:
		aTitle = _('generic warning message')

	dlg = wx.MessageDialog (
		parent = None,
		message = aMessage,
		caption = gmTools.decorate_window_title(aTitle),
		style = wx.OK | wx.ICON_EXCLAMATION | wx.STAY_ON_TOP
	)
	dlg.ShowModal()
	dlg.DestroyLater()
	return True

#-------------------------------------------------------------------------
def gm_show_question(aMessage='programmer forgot to specify question', aTitle='generic user question dialog', cancel_button=False, question=None, title=None):
	if cancel_button:
		style = wx.YES_NO | wx.CANCEL | wx.ICON_QUESTION | wx.STAY_ON_TOP
	else:
		style = wx.YES_NO | wx.ICON_QUESTION | wx.STAY_ON_TOP

	if question is None:
		question = aMessage
	if title is None:
		title = aTitle
	title = gmTools.decorate_window_title(title)

	dlg = wx.MessageDialog(None, question, title, style)
	btn_pressed = dlg.ShowModal()
	dlg.DestroyLater()

	if btn_pressed == wx.ID_YES:
		return True
	elif btn_pressed == wx.ID_NO:
		return False
	else:
		return None

#======================================================================
__IS_DARK_THEME:bool=None	# hash calculation, requires client restart for dark/ligth theme change

def is_probably_dark_theme():
	global __IS_DARK_THEME
	if __IS_DARK_THEME is not None:
		return __IS_DARK_THEME

	bg_colour = wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW)
	# detect if light/dark color
	brightness = (bg_colour.Red() * 299 + bg_colour.Green() * 587 + bg_colour.Blue() * 114) / 1000
	__IS_DARK_THEME = (brightness < 128)		# dark background/theme ?
	return __IS_DARK_THEME

#======================================================================
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	from Gnumed.pycommon import gmI18N
	gmI18N.activate_locale()
	gmI18N.install_domain(domain='gnumed')

	#------------------------------------------------------------------
	def test_scale_img():
		app = wx.App()
		img = file2scaled_image(filename = sys.argv[2])
		print(img)
		print(img.Height)
		print(img.Width)
	#------------------------------------------------------------------
	def test_sql_logic_prw():
		app = wx.PyWidgetTester(size = (200, 50))
		prw = cThreeValuedLogicPhraseWheel(app.frame, -1)
		app.frame.Show(True)
		app.MainLoop()

		return True
	#------------------------------------------------------------------
	def test_clipboard():
		app = wx.PyWidgetTester(size = (200, 50))
		result = clipboard2file()
		if result is False:
			print("problem opening clipboard")
			return
		if result is None:
			print("no data in clipboard")
			return
		print("file:", result)

	#------------------------------------------------------------------
	def test_take_screenshot():
		app = wx.App()
		input('enter for next screenshot')
		print(save_screenshot_to_file())
		input('enter for next screenshot')
		print(save_screenshot_to_file())
		input('enter for next screenshot')
		print(save_screenshot_to_file())

	#------------------------------------------------------------------
	#test_scale_img()
	#test_sql_logic_prw()
	#test_clipboard()
	test_take_screenshot()

#======================================================================
