"""GNUmed GUI helper classes and functions.

This module provides some convenient wxPython GUI
helper thingies that are widely used throughout
GNUmed.
"""
# ========================================================================
__version__ = "$Revision: 1.106 $"
__author__  = "K. Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL v2 or later (details at http://www.gnu.org)"

import os
import logging
import sys


import wx


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmMatchProvider
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

		self.SetTitle(title = caption)
		self._LBL_question.SetLabel(label = question)

		if not show_checkbox:
			self._CHBOX_dont_ask_again.Hide()
		else:
			if checkbox_msg is not None:
				self._CHBOX_dont_ask_again.SetLabel(checkbox_msg)
			if checkbox_tooltip is not None:
				self._CHBOX_dont_ask_again.SetToolTipString(checkbox_tooltip)

		buttons = [self._BTN_1, self._BTN_2]
		for idx in range(len(button_defs)):
			buttons[idx].SetLabel(label = button_defs[idx]['label'])
			buttons[idx].SetToolTipString(button_defs[idx]['tooltip'])
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

		caption = kwargs['caption']
		question = kwargs['question']
		button_defs = kwargs['button_defs'][:3]

		del kwargs['caption']
		del kwargs['question']
		del kwargs['button_defs']

		wxg3ButtonQuestionDlg.wxg3ButtonQuestionDlg.__init__(self, *args, **kwargs)

		self.SetTitle(title = caption)
		self._LBL_question.SetLabel(label = question)

		buttons = [self._BTN_1, self._BTN_2, self._BTN_3]
		for idx in range(len(button_defs)):
			buttons[idx].SetLabel(label = button_defs[idx]['label'])
			buttons[idx].SetToolTipString(button_defs[idx]['tooltip'])
			try:
				if button_defs[idx]['default'] is True:
					buttons[idx].SetDefault()
					buttons[idx].SetFocus()
			except KeyError:
				pass

		self.Fit()
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
			self.SetTitle(title)

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
		self._TCTRL_text.SetValue(u'')
	#--------------------------------------------------------
	def _on_restore_button_pressed(self, evt):
		if self.original_text is not None:
			self._TCTRL_text.SetValue(self.original_text)
# ========================================================================
from Gnumed.business import gmSurgery
from Gnumed.wxGladeWidgets import wxgGreetingEditorDlg

class cGreetingEditorDlg(wxgGreetingEditorDlg.wxgGreetingEditorDlg):

	def __init__(self, *args, **kwargs):
		wxgGreetingEditorDlg.wxgGreetingEditorDlg.__init__(self, *args, **kwargs)

		self.surgery = gmSurgery.gmCurrentPractice()
		self._TCTRL_message.SetValue(self.surgery.db_logon_banner)
	#--------------------------------------------------------
	# event handlers
	#--------------------------------------------------------
	def _on_save_button_pressed(self, evt):
		self.surgery.db_logon_banner = self._TCTRL_message.GetValue().strip()
		if self.IsModal():
			self.EndModal(wx.ID_SAVE)
		else:
			self.Close()
# ========================================================================
class cTreeExpansionHistoryMixin:
	"""TreeCtrl mixin class to record expansion history."""
	def __init__(self):
		if not isinstance(self, wx.TreeCtrl):
			raise TypeError('[%s]: mixin can only be applied to wx.TreeCtrl, not [%s]' % (cTreeExpansionHistoryMixin, self.__class__.__name__))
		self.expansion_state = {}
	#--------------------------------------------------------
	# public API
	#--------------------------------------------------------
	def snapshot_expansion(self):
		self.__record_subtree_expansion(start_node_id = self.GetRootItem())
	#--------------------------------------------------------
	def restore_expansion(self):
		if len(self.expansion_state) == 0:
			return True
		self.__restore_subtree_expansion(start_node_id = self.GetRootItem())
	#--------------------------------------------------------
	def print_expansion(self):
		if len(self.expansion_state) == 0:
			print "currently no expansion snapshot available"
			return True
		print "last snapshot of state of expansion"
		print "-----------------------------------"
		print "listing expanded nodes:"
		for node_id in self.expansion_state.keys():
			print "node ID:", node_id
			print "  selected:", self.expansion_state[node_id]
	#--------------------------------------------------------
	# internal API
	#--------------------------------------------------------
	def __record_subtree_expansion(self, start_node_id=None):
		"""This records node expansion states based on the item label.

		A side effect of this is that identically named items can
		become unduly synchronized in their expand state after a
		snapshot/restore cycle.

		Better choices might be

			id(item.GetPyData()) or
			item.GetPyData().get_tree_uid()

		where get_tree_uid():

			'[%s:%s]' % (self.__class__.__name__, id(self))

		or some such. This would survive renaming of the item.

		For database items it may be useful to include the
		primary key which would - contrary to id() - survive
		reloads from the database.
		"""
		# protect against empty tree where not even
		# a root node exists
		if not start_node_id.IsOk():
			return True

		if not self.IsExpanded(start_node_id):
			return True

		self.expansion_state[self.GetItemText(start_node_id)] = self.IsSelected(start_node_id)

		child_id, cookie = self.GetFirstChild(start_node_id)
		while child_id.IsOk():
			self.__record_subtree_expansion(start_node_id = child_id)
			child_id, cookie = self.GetNextChild(start_node_id, cookie)

		return
	#--------------------------------------------------------
	def __restore_subtree_expansion(self, start_node_id=None):
		start_node_label = self.GetItemText(start_node_id)
		try:
			node_selected = self.expansion_state[start_node_label]
		except KeyError:
			return

		self.Expand(start_node_id)
		if node_selected:
			self.SelectItem(start_node_id)

		child_id, cookie = self.GetFirstChild(start_node_id)
		while child_id.IsOk():
			self.__restore_subtree_expansion(start_node_id = child_id)
			child_id, cookie = self.GetNextChild(start_node_id, cookie)

		return
# ========================================================================
class cFileDropTarget(wx.FileDropTarget):
	"""Generic file drop target class.

	Protocol:
		Widgets being declared file drop targets
		must provide the method:

			add_filenames(filenames)
	"""
	#-----------------------------------------------
	def __init__(self, target):
		wx.FileDropTarget.__init__(self)
		self.target = target
	#-----------------------------------------------
	def OnDropFiles(self, x, y, filenames):
		self.target.add_filenames(filenames)
# ========================================================================
def file2scaled_image(filename=None, height=100):
	img_data = None
	bitmap = None
	rescaled_height = height
	try:
		img_data = wx.Image(filename, wx.BITMAP_TYPE_ANY)
		current_width = img_data.GetWidth()
		current_height = img_data.GetHeight()
#		if current_width == 0:
#			current_width = 1
#		if current_height == 0:
#			current_height = 1
		rescaled_width = (float(current_width) / current_height) * rescaled_height
		img_data.Rescale(rescaled_width, rescaled_height, quality = wx.IMAGE_QUALITY_HIGH)		# w, h
		bitmap = wx.BitmapFromImage(img_data)
		del img_data
	except StandardError:
		_log.exception('cannot load image from [%s]', filename)
		del img_data
		del bitmap
		return None

	return bitmap
# ========================================================================
def gm_show_error(aMessage = None, aTitle = None):
	if aMessage is None:
		aMessage = _('programmer forgot to specify error message')

	aMessage += _("\n\nPlease consult the error log for all the gory details !")

	if aTitle is None:
		aTitle = _('generic error message')

	dlg = wx.MessageDialog (
		parent = None,
		message = aMessage,
		caption = aTitle,
		style = wx.OK | wx.ICON_ERROR | wx.STAY_ON_TOP
	)
	dlg.ShowModal()
	dlg.Destroy()
	return True
#-------------------------------------------------------------------------
def gm_show_info(aMessage = None, aTitle = None):
	if aMessage is None:
		aMessage = _('programmer forgot to specify info message')

	if aTitle is None:
		aTitle = _('generic info message')

	dlg = wx.MessageDialog (
		parent = None,
		message = aMessage,
		caption = aTitle,
		style = wx.OK | wx.ICON_INFORMATION | wx.STAY_ON_TOP
	)
	dlg.ShowModal()
	dlg.Destroy()
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
		caption = aTitle,
		style = wx.OK | wx.ICON_EXCLAMATION | wx.STAY_ON_TOP
	)
	dlg.ShowModal()
	dlg.Destroy()
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

	dlg = wx.MessageDialog(None, question, title, style)
	btn_pressed = dlg.ShowModal()
	dlg.Destroy()

	if btn_pressed == wx.ID_YES:
		return True
	elif btn_pressed == wx.ID_NO:
		return False
	else:
		return None
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
		print img
		print img.Height
		print img.Width
	#------------------------------------------------------------------
	def test_sql_logic_prw():
		app = wx.PyWidgetTester(size = (200, 50))
		prw = cThreeValuedLogicPhraseWheel(parent = app.frame, id = -1)
		app.frame.Show(True)
		app.MainLoop()

		return True
	#------------------------------------------------------------------
	#test_scale_img()
	test_sql_logic_prw()

#======================================================================
