#====================================================================
# GNUmed Richard style Edit Area
#====================================================================
__license__ = 'GPL'
__author__ = "R.Terry, K.Hilbert"

#======================================================================
import sys
import logging
import datetime as pydt


import wx


if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x
from Gnumed.pycommon import gmDispatcher
from Gnumed.wxpython.gmGuiHelpers import decorate_window_title


_log = logging.getLogger('gm.ui')
#====================================================================
edit_area_modes = ['new', 'edit', 'new_from_existing']

class cGenericEditAreaMixin(object):
	"""Mixin for edit area panels providing generic functionality.

	**************** start of template ****************

#====================================================================
# Class definition:

from Gnumed.wxGladeWidgets import wxgXxxEAPnl

class cXxxEAPnl(wxgXxxEAPnl.wxgXxxEAPnl, gmEditArea.cGenericEditAreaMixin):

	def __init__(self, *args, **kwargs):

		try:
			data = kwargs['xxx']
			del kwargs['xxx']
		except KeyError:
			data = None

		wxgXxxEAPnl.wxgXxxEAPnl.__init__(self, *args, **kwargs)
		gmEditArea.cGenericEditAreaMixin.__init__(self)

		# Code using this mixin should set mode and data
		# after instantiating the class:
		self.mode = 'new'
		self.data = data
		if data is not None:
			self.mode = 'edit'

		#self.__init_ui()

	#----------------------------------------------------------------
#	def __init_ui(self):
#		# adjust phrasewheels etc

	#----------------------------------------------------------------
	# generic Edit Area mixin API
	#----------------------------------------------------------------
	def _valid_for_save(self):

		# its best to validate bottom -> top such that the
		# cursor ends up in the topmost failing field

		# remove when implemented:
		return False

		validity = True

		if self._TCTRL_xxx.GetValue().strip() == u'':
			validity = False
			self.display_tctrl_as_valid(tctrl = self._TCTRL_xxx, valid = False)
			self.StatusText = _('No entry in field xxx.')
			self._TCTRL_xxx.SetFocus()
		else:
			self.display_tctrl_as_valid(tctrl = self._TCTRL_xxx, valid = True)

		if self._PRW_xxx.GetData() is None:
			validity = False
			self._PRW_xxx.display_as_valid(False)
			self.StatusText = _('No entry in field xxx.')
			self._PRW_xxx.SetFocus()
		else:
			self._PRW_xxx.display_as_valid(True)

		return validity

	#----------------------------------------------------------------
	def _save_as_new(self):

		# remove when implemented:
		return False

		# save the data as a new instance
		data = gmXXXX.create_xxxx()

		data[''] = self._
		data[''] = self._

		data.save()

		# must be done very late or else the property access
		# will refresh the display such that later field
		# access will return empty values
		self.data = data
		return False
		return True

	#----------------------------------------------------------------
	def _save_as_update(self):

		# remove when implemented:
		return False

		# update self.data and save the changes
		self.data[''] = self._TCTRL_xxx.GetValue().strip()
		self.data[''] = self._PRW_xxx.GetData()
		self.data[''] = self._CHBOX_xxx.GetValue()
		self.data.save()
		return True

	#----------------------------------------------------------------
	def _refresh_as_new(self):
		pass

	#----------------------------------------------------------------
	def _refresh_as_new_from_existing(self):
		self._refresh_as_new()

	#----------------------------------------------------------------
	def _refresh_from_existing(self):
		pass

	#----------------------------------------------------------------
	def set_fields(self, fields):
		# <fields> must be a dict compatible with the
		# structure of the business object this edit
		# area is for,
		# thusly, the edit area knows how to set its
		# controls from it,
		# <fields> doesn't have to contain all keys, rather:
		# - missing ones are skipped
		# - unknown ones are ignored
		# each key must hold a dict with at least a key 'value'
		# and _can_ contain another key 'data',
		# 'value' and 'data' must be compatible with the
		# control they go into,
		# controls which don't require 'data' (say, RadioButton)
		# will ignore an existing 'data' key
		pass

	#----------------------------------------------------------------

	**************** end of template ****************
	"""
	def __init__(self):
		self.__mode = 'new'
		self.__data = None
		self.successful_save_msg = None
		self.__tctrl_validity_colors = {
			True: wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW),
			False: 'pink'
		}
		self._refresh_as_new()

	#----------------------------------------------------------------
	# properties
	#----------------------------------------------------------------
	def _get_mode(self):
		return self.__mode

	def _set_mode(self, mode=None):
		if mode not in edit_area_modes:
			raise ValueError('[%s] <mode> must be in %s' % (self.__class__.__name__, edit_area_modes))
		if mode == 'edit':
			if self.__data is None:
				raise ValueError('[%s] <mode> "edit" needs data value' % self.__class__.__name__)

		prev_mode = self.__mode
		self.__mode = mode
		if mode != prev_mode:
			self.refresh()

	mode = property(_get_mode, _set_mode)

	#----------------------------------------------------------------
	def _get_data(self):
		return self.__data

	def _set_data(self, data=None):
		if data is None:
			if self.__mode == 'edit':
				raise ValueError('[%s] <mode> "edit" needs data value' % self.__class__.__name__)
		self.__data = data
		self.refresh()

	data = property(_get_data, _set_data)

	#----------------------------------------------------------------
	def _set_status_text(self, msg, beep=False):
		gmDispatcher.send(signal = 'statustext_ea', msg = msg, beep = beep)

	StatusText = property(lambda x:x, _set_status_text)

	#----------------------------------------------------------------
	# generic edit area dialog API
	#----------------------------------------------------------------
	def save(self):
		"""Invoked from the generic edit area dialog.

		Invokes
			_valid_for_save,
			_save_as_new,
			_save_as_update
		on the implementing edit area as needed.

		_save_as_* must set self.__data and return True/False
		"""
		if not self._valid_for_save():
			return False

		# remove messages about previous invalid save attempts
		gmDispatcher.send(signal = 'statustext_ea', msg = '')

		if self.__mode in ['new', 'new_from_existing']:
			if self._save_as_new():
				self.mode = 'edit'
				return True
			return False

		elif self.__mode == 'edit':
			return self._save_as_update()

		else:
			raise ValueError('[%s] <mode> must be in %s' % (self.__class__.__name__, edit_area_modes))

	#----------------------------------------------------------------
	def refresh(self):
		"""Invoked from the generic edit area dialog.

		Invokes
			_refresh_as_new()
			_refresh_from_existing()
			_refresh_as_new_from_existing()
		on the implementing edit area as needed.

		Then calls _valid_for_save().
		"""
		if self.__mode == 'new':
			result = self._refresh_as_new()
			self._valid_for_save()
			return result
		elif self.__mode == 'edit':
			result = self._refresh_from_existing()
			self._valid_for_save()
			return result
		elif self.__mode == 'new_from_existing':
			result = self._refresh_as_new_from_existing()
			self._valid_for_save()
			return result
		else:
			raise ValueError('[%s] <mode> must be in %s' % (self.__class__.__name__, edit_area_modes))

	#----------------------------------------------------------------
	def display_tctrl_as_valid(self, tctrl=None, valid=None):
		self.display_ctrl_as_valid(ctrl = tctrl, valid = valid)

	#----------------------------------------------------------------
	def display_ctrl_as_valid(self, ctrl=None, valid=None):
		ctrl.SetBackgroundColour(self.__tctrl_validity_colors[valid])
		ctrl.Refresh()

#====================================================================
from Gnumed.wxGladeWidgets import wxgGenericEditAreaDlg2

class cGenericEditAreaDlg(wxgGenericEditAreaDlg2.wxgGenericEditAreaDlg2):
	"""Dialog for parenting edit area panels with save/clear/next/cancel"""

	_lucky_day = 1
	_lucky_month = 4
	_today = pydt.date.today()

	def __init__(self, *args, **kwargs):

		new_ea = kwargs['edit_area']
		del kwargs['edit_area']

		if not isinstance(new_ea, cGenericEditAreaMixin):
			raise TypeError('[%s]: edit area instance must be child of cGenericEditAreaMixin')

		try:
			single_entry = kwargs['single_entry']
			del kwargs['single_entry']
		except KeyError:
			single_entry = False

		try:
			title = kwargs['title']
		except KeyError:
			title = self.__class__.__name__
		kwargs['title'] = decorate_window_title(title)

		wxgGenericEditAreaDlg2.wxgGenericEditAreaDlg2.__init__(self, *args, **kwargs)

		self.left_extra_button = None

		if cGenericEditAreaDlg._today.day != cGenericEditAreaDlg._lucky_day:
			self._BTN_lucky.Enable(False)
			self._BTN_lucky.Hide()
		else:
			if cGenericEditAreaDlg._today.month != cGenericEditAreaDlg._lucky_month:
				self._BTN_lucky.Enable(False)
				self._BTN_lucky.Hide()

		# replace dummy panel
		dummy_ea_pnl = self._PNL_ea
		ea_pnl_szr = dummy_ea_pnl.GetContainingSizer()
		ea_pnl_parent = dummy_ea_pnl.GetParent()
		#ea_pnl_szr.Remove(dummy_ea_pnl)						# not available in wxp4 anymore, BUT
		dummy_ea_pnl.DestroyLater()								# in wxp4 .DestroyLater() auto-Remove()s :-)
		del dummy_ea_pnl
		new_ea_min_size = new_ea.GetMinSize()
		new_ea.Reparent(ea_pnl_parent)
		self._PNL_ea = new_ea
		ea_pnl_szr.Add(self._PNL_ea, 1, wx.EXPAND, 0)
		ea_pnl_szr.SetMinSize(new_ea_min_size)					# set minimum size of EA pnl sizer from its new EA item
		ea_pnl_szr.Fit(new_ea)									# resize the new EA to the minimum size of the EA pnl sizer

		# adjust buttons
		if single_entry:
			self._BTN_forward.Enable(False)
			self._BTN_forward.Hide()

		self._adjust_clear_revert_buttons()

		# attach listener
		self._TCTRL_status.SetValue('')
		gmDispatcher.connect(signal = 'statustext_ea', receiver = self._on_set_statustext)

		# redraw layout
		main_szr = self.GetSizer()
		main_szr.Fit(self)
		self.Layout()
		#self.Refresh()				# apparently not needed (27.3.2011)

		self._PNL_ea.refresh()

	#--------------------------------------------------------
	def _on_set_statustext(self, msg=None, loglevel=None, beep=False):
		if msg is None:
			msg = ''
		try:
			self._TCTRL_status.SetValue(msg.strip())
			if beep:
				wx.Bell()
		except RuntimeError:
			# likely we are being deleted but a statustext arrived late via a signal
			pass

	#--------------------------------------------------------
	def _adjust_clear_revert_buttons(self):
		if self._PNL_ea.data is None:
			self._BTN_clear.Enable(True)
			self._BTN_clear.Show()
			self._BTN_revert.Enable(False)
			self._BTN_revert.Hide()
		else:
			self._BTN_clear.Enable(False)
			self._BTN_clear.Hide()
			self._BTN_revert.Enable(True)
			self._BTN_revert.Show()

	#--------------------------------------------------------
	def _on_save_button_pressed(self, evt):
		if self._PNL_ea.save():
			gmDispatcher.disconnect(signal = 'statustext_ea', receiver = self._on_set_statustext)
			if self.IsModal():
				self.EndModal(wx.ID_OK)
			else:
				self.Close()

	#--------------------------------------------------------
	def _on_revert_button_pressed(self, evt):
		self._PNL_ea.refresh()

	#--------------------------------------------------------
	def _on_clear_button_pressed(self, evt):
		self._PNL_ea.refresh()

	#--------------------------------------------------------
	def _on_forward_button_pressed(self, evt):
		if self._PNL_ea.save():
			if self._PNL_ea.successful_save_msg is not None:
				gmDispatcher.send(signal = 'statustext_ea', msg = self._PNL_ea.successful_save_msg)
			self._PNL_ea.mode = 'new_from_existing'

			self._adjust_clear_revert_buttons()

			self.Layout()
			main_szr = self.GetSizer()
			main_szr.Fit(self)
			self.Refresh()

			self._PNL_ea.refresh()
	#--------------------------------------------------------
	def _on_lucky_button_pressed(self, evt):
		from Gnumed.wxpython import gmGuiHelpers
		gmGuiHelpers.gm_show_info (
			_(	'Today is your lucky day !\n'
				'\n'
				'You have won one year of GNUmed\n'
				'updates for free !\n'
			),
			_('GNUmed Lottery')
		)
	#--------------------------------------------------------
	def _on_left_extra_button_pressed(self, event):
		if not self.__left_extra_button_callback(self._PNL_ea.data):
			return

		if self.IsModal():
			self.EndModal(wx.ID_OK)
		else:
			self.Close()

	#------------------------------------------------------------
	def SetTitle(self, title):
		super().SetTitle(decorate_window_title(title))

	#------------------------------------------------------------
	# properties
	#------------------------------------------------------------
	def _set_left_extra_button(self, definition):
		if definition is None:
			self._BTN_extra_left.Enable(False)
			self._BTN_extra_left.Hide()
			self.__left_extra_button_callback = None
			return

		(label, tooltip, callback) = definition
		if not callable(callback):
			raise ValueError('<left extra button> callback is not a callable: %s' % callback)
		self.__left_extra_button_callback = callback
		self._BTN_extra_left.SetLabel(label)
		self._BTN_extra_left.SetToolTip(tooltip)
		self._BTN_extra_left.Enable(True)
		self._BTN_extra_left.Show()

	left_extra_button = property(lambda x:x, _set_left_extra_button)

	#------------------------------------------------------------
	def _get_ea_data(self):
		return self._PNL_ea.data

	data = property(_get_ea_data)

#====================================================================
# main
#--------------------------------------------------------------------
if __name__ == "__main__":

	pass
	#================================================================
	#app = wxPyWidgetTester(size = (400, 200))
	#app.SetWidget(cTestEditArea)
	#app.MainLoop()
#	app = wxPyWidgetTester(size = (400, 200))
#	app.SetWidget(gmFamilyHxEditArea, -1)
#	app.MainLoop()
#	app = wxPyWidgetTester(size = (400, 200))
#	app.SetWidget(gmPastHistoryEditArea, -1)
#	app.MainLoop()

