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

class cGenericEditAreaDlg2(wxgGenericEditAreaDlg2.wxgGenericEditAreaDlg2):
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

		if cGenericEditAreaDlg2._today.day != cGenericEditAreaDlg2._lucky_day:
			self._BTN_lucky.Enable(False)
			self._BTN_lucky.Hide()
		else:
			if cGenericEditAreaDlg2._today.month != cGenericEditAreaDlg2._lucky_month:
				self._BTN_lucky.Enable(False)
				self._BTN_lucky.Hide()

		# replace dummy panel
		dummy_ea_pnl = self._PNL_ea
		ea_pnl_szr = dummy_ea_pnl.GetContainingSizer()
		ea_pnl_parent = dummy_ea_pnl.GetParent()
		#ea_pnl_szr.Remove(dummy_ea_pnl)						# not available in wxp4 anymore, BUT
		dummy_ea_pnl.DestroyLater()									# in wxp4 .DestroyLater() auto-Remove()s :-)
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

	#------------------------------------------------------------

#====================================================================
#====================================================================
#====================================================================
#====================================================================
#====================================================================
#====================================================================
#====================================================================
#====================================================================
#====================================================================
#====================================================================
#====================================================================
#====================================================================
#====================================================================
#====================================================================
#====================================================================
#====================================================================
#import time

#from Gnumed.business import gmPerson, gmDemographicRecord
#from Gnumed.wxpython import gmDateTimeInput, gmPhraseWheel, gmGuiHelpers

gmSECTION_SUMMARY = 1
gmSECTION_DEMOGRAPHICS = 2
gmSECTION_CLINICALNOTES = 3
gmSECTION_FAMILYHISTORY = 4
gmSECTION_PASTHISTORY = 5
gmSECTION_SCRIPT = 8
gmSECTION_REQUESTS = 9
gmSECTION_REFERRALS = 11
gmSECTION_RECALLS = 12

richards_blue = wx.Colour(0,0,131)
richards_aqua = wx.Colour(0,194,197)
richards_dark_gray = wx.Colour(131,129,131)
richards_light_gray = wx.Colour(255,255,255)
richards_coloured_gray = wx.Colour(131,129,131)


CONTROLS_WITHOUT_LABELS =['wxTextCtrl', 'cEditAreaField', 'wx.SpinCtrl', 'gmPhraseWheel', 'wx.ComboBox'] 

def _decorate_editarea_field(widget):
	widget.SetForegroundColour(wx.Colour(255, 0, 0))
	widget.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD, False, ''))
#====================================================================
class cEditAreaPopup(wx.Dialog):
	def __init__ (
		self,
		parent,
		id,
		title = 'edit area popup',
		pos=wx.DefaultPosition,
		size=wx.DefaultSize,
		style=wx.SIMPLE_BORDER,
		name='',
		edit_area = None
	):
		if not isinstance(edit_area, cEditArea2):
			raise TypeError('<edit_area> must be of type cEditArea2 but is <%s>' % type(edit_area))
		wx.Dialog.__init__(self, parent, id, title, pos, size, style, name)
		self.__wxID_BTN_SAVE = wx.NewId()
		self.__wxID_BTN_RESET = wx.NewId()
		self.__editarea = edit_area
		self.__do_layout()
		self.__register_events()
	#--------------------------------------------------------
	# public API
	#--------------------------------------------------------
	def get_summary(self):
		return self.__editarea.get_summary()
	#--------------------------------------------------------
	def __do_layout(self):
		self.__editarea.Reparent(self)

		self.__btn_SAVE = wx.Button(self, self.__wxID_BTN_SAVE, _("Save"))
		self.__btn_SAVE.SetToolTip(_('save entry into medical record'))
		self.__btn_RESET = wx.Button(self, self.__wxID_BTN_RESET, _("Reset"))
		self.__btn_RESET.SetToolTip(_('reset entry'))
		self.__btn_CANCEL = wx.Button(self, wx.ID_CANCEL, _("Cancel"))
		self.__btn_CANCEL.SetToolTip(_('discard entry and cancel'))

		szr_buttons = wx.BoxSizer(wx.HORIZONTAL)
		szr_buttons.Add(self.__btn_SAVE, 1, wx.EXPAND | wx.ALL, 1)
		szr_buttons.Add(self.__btn_RESET, 1, wx.EXPAND | wx.ALL, 1)
		szr_buttons.Add(self.__btn_CANCEL, 1, wx.EXPAND | wx.ALL, 1)

		szr_main = wx.BoxSizer(wx.VERTICAL)
		szr_main.Add(self.__editarea, 1, wx.EXPAND)
		szr_main.Add(szr_buttons, 0, wx.EXPAND)

		self.SetSizerAndFit(szr_main)
	#--------------------------------------------------------
	# event handling
	#--------------------------------------------------------
	def __register_events(self):
		# connect standard buttons
		wx.EVT_BUTTON(self.__btn_SAVE, self.__wxID_BTN_SAVE, self._on_SAVE_btn_pressed)
		wx.EVT_BUTTON(self.__btn_RESET, self.__wxID_BTN_RESET, self._on_RESET_btn_pressed)
		wx.EVT_BUTTON(self.__btn_CANCEL, wx.ID_CANCEL, self._on_CANCEL_btn_pressed)

		wx.EVT_CLOSE(self, self._on_CANCEL_btn_pressed)

		# client internal signals
#		gmDispatcher.connect(signal = gmSignals.pre_patient_unselection(), receiver = self._on_pre_patient_unselection)
#		gmDispatcher.connect(signal = gmSignals.application_closing(), receiver = self._on_application_closing)
#		gmDispatcher.connect(signal = gmSignals.post_patient_selection(), receiver = self.on_post_patient_selection)

		return 1
	#--------------------------------------------------------
	def _on_SAVE_btn_pressed(self, evt):
		if self.__editarea.save_data():
			self.__editarea.Close()
			self.EndModal(wx.ID_OK)
			return
		short_err = self.__editarea.get_short_error()
		long_err = self.__editarea.get_long_error()
		if (short_err is None) and (long_err is None):
			long_err = _(
				'Unspecified error saving data in edit area.\n\n'
				'Programmer forgot to specify proper error\n'
				'message in [%s].'
			) % self.__editarea.__class__.__name__
		if short_err is not None:
			gmDispatcher.send(signal = 'statustext', msg = short_err)
#		if long_err is not None:
#			gmGuiHelpers.gm_show_error(long_err, _('saving clinical data'))
	#--------------------------------------------------------
	def _on_CANCEL_btn_pressed(self, evt):
		self.__editarea.Close()
		self.EndModal(wx.ID_CANCEL)
	#--------------------------------------------------------
	def _on_RESET_btn_pressed(self, evt):
		self.__editarea.reset_ui()
#====================================================================
class cEditArea2(wx.Panel):
	def __init__(self, parent, id, pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.TAB_TRAVERSAL):
		# init main background panel
		wx.Panel.__init__ (
			self,
			parent,
			id,
			pos = pos,
			size = size,
			style = style | wx.TAB_TRAVERSAL
		)
		self.SetBackgroundColour(wx.Colour(222,222,222))

		self.data = None		# a placeholder for opaque data
		self.fields = {}
		self.prompts = {}
		self._short_error = None
		self._long_error = None
		self._summary = None
		self._patient = None #gmPerson.gmCurrentPatient()
		self.__wxID_BTN_OK = wx.NewId()
		self.__wxID_BTN_CLEAR = wx.NewId()
		self.__do_layout()
		self.__register_events()
		self.Show()
	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def save_data(self):
		"""This needs to be overridden by child classes."""
		self._long_error = _(
			'Cannot save data from edit area.\n\n'
			'Programmer forgot to override method:\n'
			'  <%s.save_data>'
		) % self.__class__.__name__
		return False
	#--------------------------------------------------------
	def reset_ui(self):
		msg = _(
			'Cannot reset fields in edit area.\n\n'
			'Programmer forgot to override method:\n'
			'  <%s.reset_ui>'
		) % self.__class__.__name__
		print(msg)
		#gmGuiHelpers.gm_show_error(msg)
	#--------------------------------------------------------
	def get_short_error(self):
		tmp = self._short_error
		self._short_error = None
		return tmp
	#--------------------------------------------------------
	def get_long_error(self):
		tmp = self._long_error
		self._long_error = None
		return tmp
	#--------------------------------------------------------
	def get_summary(self):
		return _('<No embed string for [%s]>') % self.__class__.__name__
	#--------------------------------------------------------
	# event handling
	#--------------------------------------------------------
	def __register_events(self):
		# client internal signals
		if self._patient.connected:
			gmDispatcher.connect(signal = 'pre_patient_unselection', receiver = self._on_pre_patient_unselection)
			gmDispatcher.connect(signal = 'post_patient_selection', receiver = self.on_post_patient_selection)
		gmDispatcher.connect(signal = 'application_closing', receiver = self._on_application_closing)

		# wxPython events
		wx.EVT_CLOSE(self, self._on_close)

		return 1
	#--------------------------------------------------------
	def __deregister_events(self):
		gmDispatcher.disconnect(signal = 'pre_patient_unselection', receiver = self._on_pre_patient_unselection)
		gmDispatcher.disconnect(signal = 'post_patient_selection', receiver = self.on_post_patient_selection)
		gmDispatcher.disconnect(signal = 'application_closing', receiver = self._on_application_closing)
	#--------------------------------------------------------
	# handlers
	#--------------------------------------------------------
	def _on_close(self, event):
		self.__deregister_events()
		event.Skip()
	#--------------------------------------------------------
	def _on_OK_btn_pressed(self, event):
		"""Only active if _make_standard_buttons was called in child class."""
		# FIXME: this try: except Exception: block seems to large
		try:
			event.Skip()
			if self.data is None:
				self._save_new_entry()
				self.reset_ui()
			else:
				self._save_modified_entry()
				self.reset_ui()
#		except Exception as err:
#			# nasty evil popup dialogue box
#			# but for invalid input we want to interrupt user
#			#gmGuiHelpers.gm_show_error (err, _("Invalid Input"))

		except Exception:
			_log.exception( "save data problem in [%s]" % self.__class__.__name__)
	#--------------------------------------------------------
	def _on_clear_btn_pressed(self, event):
		"""Only active if _make_standard_buttons was called in child class."""
		# FIXME: check for unsaved data
		self.reset_ui()
		event.Skip()
	#--------------------------------------------------------
	def _on_application_closing(self, **kwds):
		self.__deregister_events()
		# remember wxCallAfter
		if not self._patient.connected:
			return True
		# FIXME: should do this:
#		if self.user_wants_save():
#			if self.save_data():
#				return True
		return True
		_log.error('[%s] lossage' % self.__class__.__name__)
		return False
	#--------------------------------------------------------
	def _on_pre_patient_unselection(self, **kwds):
		"""Just before new patient becomes active."""
		# remember wxCallAfter
		if not self._patient.connected:
			return True
		# FIXME: should do this:
#		if self.user_wants_save():
#			if self.save_data():
#				return True
		return True
		_log.error('[%s] lossage' % self.__class__.__name__)
		return False
	#--------------------------------------------------------
	def on_post_patient_selection( self, **kwds):
		"""Just after new patient became active."""
		# remember to use wxCallAfter()
		self.reset_ui()
	#----------------------------------------------------------------
	# internal helpers
	#----------------------------------------------------------------
	def __do_layout(self):

		# define prompts and fields
		self._define_prompts()
		self._define_fields(parent = self)
		if len(self.fields) != len(self.prompts):
			_log.error('[%s]: #fields != #prompts' % self.__class__.__name__)
			return None

		# and generate edit area from it
		szr_main_fgrid = wx.FlexGridSizer(rows = len(self.prompts), cols=2)
		color = richards_aqua
		lines = list(self.prompts)
		lines.sort()
		for line in lines:
			# 1) prompt
			label, color, weight = self.prompts[line]
			# FIXME: style for centering in vertical direction ?
			prompt = wx.StaticText (
				parent = self,
				id = -1,
				label = label,
				style = wx.ALIGN_CENTRE
			)
			# FIXME: resolution dependant
			prompt.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD, False, ''))
			prompt.SetForegroundColour(color)
			prompt.SetBackgroundColour(richards_light_gray)
			szr_main_fgrid.Add(prompt, flag=wx.EXPAND | wx.ALIGN_RIGHT)

			# 2) widget(s) for line
			szr_line = wx.BoxSizer(wx.HORIZONTAL)
			positions = list(self.fields[line])
			positions.sort()
			for pos in positions:
				field, weight = self.fields[line][pos]
#				field.SetBackgroundColour(wx.Colour(222,222,222))
				szr_line.Add(field, weight, wx.EXPAND)
			szr_main_fgrid.Add(szr_line, flag=wx.GROW | wx.ALIGN_LEFT)

		# grid can grow column 1 only, not column 0
		szr_main_fgrid.AddGrowableCol(1)

#		# use sizer for border around everything plus a little gap
#		# FIXME: fold into szr_main_panels ?
#		self.szr_central_container = wx.BoxSizer(wxHORIZONTAL)
#		self.szr_central_container.Add(self.szr_main_panels, 1, wx.EXPAND | wxALL, 5)

		# and do the layouting
		self.SetSizerAndFit(szr_main_fgrid)
#		self.FitInside()
	#----------------------------------------------------------------
	# intra-class API
	#----------------------------------------------------------------
	def _define_prompts(self):
		"""Child classes override this to define their prompts using _add_prompt()"""
		_log.error('missing override in [%s]' % self.__class__.__name__)
	#----------------------------------------------------------------
	def _add_prompt(self, line, label='missing label', color=richards_blue, weight=0):
		"""Add a new prompt line.

		To be used from _define_fields in child classes.

		- label, the label text
		- color
		- weight, the weight given in sizing the various rows. 0 means the row
		  always has minimum size 
		"""
		self.prompts[line] = (label, color, weight)
	#----------------------------------------------------------------
	def _define_fields(self, parent):
		"""Defines the fields.

		- override in child classes
		- mostly uses _add_field()
		"""
		_log.error('missing override in [%s]' % self.__class__.__name__)
	#----------------------------------------------------------------
	def _add_field(self, line=None, pos=None, widget=None, weight=0):
		if None in (line, pos, widget):
			_log.error('argument error in [%s]: line=%s, pos=%s, widget=%s' % (self.__class__.__name__, line, pos, widget))
		if line not in self.fields:
			self.fields[line] = {}
		self.fields[line][pos] = (widget, weight)
	#----------------------------------------------------------------
	def _make_standard_buttons(self, parent):
		"""Generates OK/CLEAR buttons for edit area."""
		self.btn_OK = wx.Button(parent, self.__wxID_BTN_OK, _("OK"))
		self.btn_OK.SetToolTip(_('save entry into medical record'))
		self.btn_Clear = wx.Button(parent, self.__wxID_BTN_CLEAR, _("Clear"))
		self.btn_Clear.SetToolTip(_('initialize input fields for new entry'))

		szr_buttons = wx.BoxSizer(wx.HORIZONTAL)
		szr_buttons.Add(self.btn_OK, 1, wx.EXPAND | wx.ALL, 1)
		szr_buttons.Add((5, 0), 0)
		szr_buttons.Add(self.btn_Clear, 1, wx.EXPAND | wx.ALL, 1)

		# connect standard buttons
		wx.EVT_BUTTON(self.btn_OK, self.__wxID_BTN_OK, self._on_OK_btn_pressed)
		wx.EVT_BUTTON(self.btn_Clear, self.__wxID_BTN_CLEAR, self._on_clear_btn_pressed)

		return szr_buttons
#====================================================================
#====================================================================
#text control class to be later replaced by the gmPhraseWheel
#--------------------------------------------------------------------
class cEditAreaField(wx.TextCtrl):
	def __init__ (self, parent, id = -1, pos = wx.DefaultPosition, size=wx.DefaultSize):
		wx.TextCtrl.__init__(self,parent,id,"",pos, size ,wx.SIMPLE_BORDER)
		_decorate_editarea_field(self)
#====================================================================
class cEditArea(wx.Panel):
	def __init__(self, parent, id, pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.SIMPLE_BORDER):

		print("class [%s] is deprecated, use cEditArea2 instead" % self.__class__.__name__)

		# init main background panel
		wx.Panel.__init__(self, parent, id, pos=pos, size=size, style=wx.NO_BORDER | wx.TAB_TRAVERSAL)
		self.SetBackgroundColour(wx.Colour(222,222,222))

		self.data = None
		self.fields = {}
		self.prompts = {}

#		ID_BTN_OK = wx.NewId()
#		ID_BTN_CLEAR = wx.NewId()

		self.__do_layout()

#		self.input_fields = {}

#		self._postInit()
#		self.old_data = {}

		#self._patient = gmPerson.gmCurrentPatient()
		self._patient = None
		self.__register_events()
		self.Show(True)
	#----------------------------------------------------------------
	# internal helpers
	#----------------------------------------------------------------
	def __do_layout(self):
		# define prompts and fields
		self._define_prompts()
		self.fields_pnl = wx.Panel(self, -1, style = wx.RAISED_BORDER | wx.TAB_TRAVERSAL)
		self._define_fields(parent = self.fields_pnl)
		# and generate edit area from it
		szr_prompts = self.__generate_prompts()
		szr_fields = self.__generate_fields()

		# stack prompts and fields horizontally
		self.szr_main_panels = wx.BoxSizer(wx.HORIZONTAL)
		self.szr_main_panels.Add(szr_prompts, 11, wx.EXPAND)
		self.szr_main_panels.Add(5, 0, 0, wx.EXPAND)
		self.szr_main_panels.Add(szr_fields, 90, wx.EXPAND)

		# use sizer for border around everything plus a little gap
		# FIXME: fold into szr_main_panels ?
		self.szr_central_container = wx.BoxSizer(wx.HORIZONTAL)
		self.szr_central_container.Add(self.szr_main_panels, 1, wx.EXPAND | wx.ALL, 5)

		# and do the layouting
		self.SetAutoLayout(True)
		self.SetSizer(self.szr_central_container)
		self.szr_central_container.Fit(self)
	#----------------------------------------------------------------
	def __generate_prompts(self):
		if len(self.fields) != len(self.prompts):
			_log.error('[%s]: #fields != #prompts' % self.__class__.__name__)
			return None
		# prompts live on a panel
		prompt_pnl = wx.Panel(self, -1, wx.DefaultPosition, wx.DefaultSize, wx.SIMPLE_BORDER)
		prompt_pnl.SetBackgroundColour(richards_light_gray)
		# make them
		color = richards_aqua
		lines = list(self.prompts)
		lines.sort()
		self.prompt_widget = {}
		for line in lines:
			label, color, weight = self.prompts[line]
			self.prompt_widget[line] = self.__make_prompt(prompt_pnl, "%s " % label, color)
		# make shadow below prompts in gray
		shadow_below_prompts = wx.Window(self, -1, wx.DefaultPosition, wx.DefaultSize, 0)
		shadow_below_prompts.SetBackgroundColour(richards_dark_gray)
		szr_shadow_below_prompts = wx.BoxSizer (wx.HORIZONTAL)
		szr_shadow_below_prompts.Add(5, 0, 0, wx.EXPAND)
		szr_shadow_below_prompts.Add(shadow_below_prompts, 10, wx.EXPAND)

		# stack prompt panel and shadow vertically
		vszr_prompts = wx.BoxSizer(wx.VERTICAL)
		vszr_prompts.Add(prompt_pnl, 97, wx.EXPAND)
		vszr_prompts.Add(szr_shadow_below_prompts, 5, wx.EXPAND)

		# make shadow to the right of the prompts
		shadow_rightof_prompts = wx.Window(self, -1, wx.DefaultPosition, wx.DefaultSize, 0)
		shadow_rightof_prompts.SetBackgroundColour(richards_dark_gray)
		szr_shadow_rightof_prompts = wx.BoxSizer(wx.VERTICAL)
		szr_shadow_rightof_prompts.Add(0,5,0,wx.EXPAND)
		szr_shadow_rightof_prompts.Add(shadow_rightof_prompts, 1, wx.EXPAND)

		# stack vertical prompt sizer and shadow horizontally
		hszr_prompts = wx.BoxSizer(wx.HORIZONTAL)
		hszr_prompts.Add(vszr_prompts, 10, wx.EXPAND)
		hszr_prompts.Add(szr_shadow_rightof_prompts, 1, wx.EXPAND)

		return hszr_prompts
	#----------------------------------------------------------------
	def __generate_fields(self):
		self.fields_pnl.SetBackgroundColour(wx.Colour(222,222,222))
		# rows, cols, hgap, vgap
		vszr = wx.BoxSizer(wx.VERTICAL)
		lines = list(self.fields)
		lines.sort()
		self.field_line_szr = {}
		for line in lines:
			self.field_line_szr[line] = wx.BoxSizer(wx.HORIZONTAL)
			positions = list(self.fields[line])
			positions.sort()
			for pos in positions:
				field, weight = self.fields[line][pos]
				self.field_line_szr[line].Add(field, weight, wx.EXPAND)
			try:
				vszr.Add(self.field_line_szr[line], self.prompts[line][2], flag = wx.EXPAND) # use same lineweight as prompts
			except KeyError:
				_log.error("Error with line=%s, self.field_line_szr has key:%s; self.prompts has key: %s" % (
					line,
					(line in self.field_line_szr),
					(line in self.prompts)
				))
		# put them on the panel
		self.fields_pnl.SetSizer(vszr)
		vszr.Fit(self.fields_pnl)

		# make shadow below edit fields in gray
		shadow_below_edit_fields = wx.Window(self, -1, wx.DefaultPosition, wx.DefaultSize, 0)
		shadow_below_edit_fields.SetBackgroundColour(richards_coloured_gray)
		szr_shadow_below_edit_fields = wx.BoxSizer(wx.HORIZONTAL)
		szr_shadow_below_edit_fields.Add(5, 0, 0, wx.EXPAND)
		szr_shadow_below_edit_fields.Add(shadow_below_edit_fields, 12, wx.EXPAND)

		# stack edit fields and shadow vertically
		vszr_edit_fields = wx.BoxSizer(wx.VERTICAL)
		vszr_edit_fields.Add(self.fields_pnl, 92, wx.EXPAND)
		vszr_edit_fields.Add(szr_shadow_below_edit_fields, 5, wx.EXPAND)

		# make shadow to the right of the edit area
		shadow_rightof_edit_fields = wx.Window(self, -1, wx.DefaultPosition, wx.DefaultSize, 0)
		shadow_rightof_edit_fields.SetBackgroundColour(richards_coloured_gray)
		szr_shadow_rightof_edit_fields = wx.BoxSizer(wx.VERTICAL)
		szr_shadow_rightof_edit_fields.Add(0, 5, 0, wx.EXPAND)
		szr_shadow_rightof_edit_fields.Add(shadow_rightof_edit_fields, 1, wx.EXPAND)

		# stack vertical edit fields sizer and shadow horizontally
		hszr_edit_fields = wx.BoxSizer(wx.HORIZONTAL)
		hszr_edit_fields.Add(vszr_edit_fields, 89, wx.EXPAND)
		hszr_edit_fields.Add(szr_shadow_rightof_edit_fields, 1, wx.EXPAND)

		return hszr_edit_fields
	#---------------------------------------------------------------
	def __make_prompt(self, parent, aLabel, aColor):
		# FIXME: style for centering in vertical direction ?
		prompt = wx.StaticText(
			parent,
			-1,
			aLabel,
			style = wx.ALIGN_RIGHT
		)
		prompt.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD, False, ''))
		prompt.SetForegroundColour(aColor)
		return prompt
	#----------------------------------------------------------------
	# intra-class API
	#----------------------------------------------------------------
	def _add_prompt(self, line, label='missing label', color=richards_blue, weight=0):
		"""Add a new prompt line.

		To be used from _define_fields in child classes.

		- label, the label text
		- color
		- weight, the weight given in sizing the various rows. 0 means the rwo
		  always has minimum size 
		"""
		self.prompts[line] = (label, color, weight)
	#----------------------------------------------------------------
	def _add_field(self, line=None, pos=None, widget=None, weight=0):
		if None in (line, pos, widget):
			_log.error('argument error in [%s]: line=%s, pos=%s, widget=%s' % (self.__class__.__name__, line, pos, widget))
		if line not in self.fields:
			self.fields[line] = {}
		self.fields[line][pos] = (widget, weight)
	#----------------------------------------------------------------
	def _define_fields(self, parent):
		"""Defines the fields.

		- override in child classes
		- mostly uses _add_field()
		"""
		_log.error('missing override in [%s]' % self.__class__.__name__)
	#----------------------------------------------------------------
	def _define_prompts(self):
		_log.error('missing override in [%s]' % self.__class__.__name__)
	#----------------------------------------------------------------
	def _make_standard_buttons(self, parent):
		"""Generates OK/CLEAR buttons for edit area."""
#		self.btn_OK = wx.Button(parent, ID_BTN_OK, _("OK"))
#		self.btn_OK.SetToolTip(_('save entry into medical record'))
#		self.btn_Clear = wx.Button(parent, ID_BTN_CLEAR, _("Clear"))
#		self.btn_Clear.SetToolTip(_('initialize input fields for new entry'))

		szr_buttons = wx.BoxSizer(wx.HORIZONTAL)
#		szr_buttons.Add(self.btn_OK, 1, wx.EXPAND | wx.ALL, 1)
		szr_buttons.Add(5, 0, 0)
#		szr_buttons.Add(self.btn_Clear, 1, wx.EXPAND | wx.ALL, 1)

		return szr_buttons
	#--------------------------------------------------------
	def _pre_save_data(self):
		pass
	#--------------------------------------------------------
	def _save_data(self):
		_log.error('[%s] programmer forgot to define _save_data()' % self.__class__.__name__)
		_log.info('child classes of cEditArea *must* override this function')
		return False
	#--------------------------------------------------------
	# event handling
	#--------------------------------------------------------
	def __register_events(self):
		# connect standard buttons
#		wx.EVT_BUTTON(self.btn_OK, ID_BTN_OK, self._on_OK_btn_pressed)
#		wx.EVT_BUTTON(self.btn_Clear, ID_BTN_CLEAR, self._on_clear_btn_pressed)

		wx.EVT_SIZE (self.fields_pnl, self._on_resize_fields)

		# client internal signals
		gmDispatcher.connect(signal = 'pre_patient_unselection', receiver = self._on_pre_patient_unselection)
		gmDispatcher.connect(signal = 'application_closing', receiver = self._on_application_closing)
		gmDispatcher.connect(signal = 'post_patient_selection', receiver = self.on_post_patient_selection)

		return 1
	#--------------------------------------------------------
	# handlers
	#--------------------------------------------------------
	def _on_OK_btn_pressed(self, event):
		# FIXME: this try: except Exception: block seems to large
		try:
			event.Skip()
			if self.data is None:
				self._save_new_entry()
				self.set_data()
			else:
				self._save_modified_entry()
				self.set_data()
#		except Exception as err:
#			# nasty evil popup dialogue box
#			# but for invalid input we want to interrupt user
#			gmGuiHelpers.gm_show_error (err, _("Invalid Input"))
		except Exception:
			_log.exception( "save data  problem in [%s]" % self.__class__.__name__)
	#--------------------------------------------------------
	def _on_clear_btn_pressed(self, event):
		# FIXME: check for unsaved data
		self.set_data()
		event.Skip()
	#--------------------------------------------------------
	def on_post_patient_selection( self, **kwds):
		# remember to use wxCallAfter()
		self.set_data()
	#--------------------------------------------------------
	def _on_application_closing(self, **kwds):
		# remember wxCallAfter
		if not self._patient.connected:
			return True
		if self._save_data():
			return True
		_log.error('[%s] lossage' % self.__class__.__name__)
		return False
	#--------------------------------------------------------
	def _on_pre_patient_unselection(self, **kwds):
		# remember wxCallAfter
		if not self._patient.connected:
			return True
		if self._save_data():
			return True
		_log.error('[%s] lossage' % self.__class__.__name__)
		return False
	#--------------------------------------------------------
	def _on_resize_fields (self, event):
		self.fields_pnl.Layout()
		# resize the prompts accordingly
		for i in self.field_line_szr:
			# query the BoxSizer to find where the field line is
			pos = self.field_line_szr[i].GetPosition()
			# and set the prompt lable to the same Y position
			self.prompt_widget[i].SetPosition((0, pos.y))

#====================================================================
#====================================================================
#====================================================================
#====================================================================
#====================================================================
#====================================================================
#====================================================================
# old style stuff below
#====================================================================
#Class which shows a blue bold label left justified
#--------------------------------------------------------------------
class cPrompt_edit_area(wx.StaticText):
	def __init__(self, parent, id, prompt, aColor = richards_blue):
		wx.StaticText.__init__(self, parent, id, prompt, wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_LEFT)
		self.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD, False, ''))
		self.SetForegroundColour(aColor)
#====================================================================
# create the editorprompts class which expects a dictionary of labels
# passed to it with prompts relevant to the editing area.
# remove the if else from this once the edit area labelling is fixed
#--------------------------------------------------------------------
class gmPnlEditAreaPrompts(wx.Panel):
	def __init__(self, parent, id, prompt_labels):
		wx.Panel.__init__(self, parent, id, wx.DefaultPosition, wx.DefaultSize, wx.SIMPLE_BORDER)
		self.SetBackgroundColour(richards_light_gray)
		gszr = wx.GridSizer (len(prompt_labels)+1, 1, 2, 2)
		color = richards_aqua
		for prompt_key in prompt_labels:
			label = cPrompt_edit_area(self, -1, " %s" % prompt_labels[prompt_key], aColor = color)
			gszr.Add(label, 0, wx.EXPAND | wx.ALIGN_RIGHT)
			color = richards_blue
		self.SetSizer(gszr)
		gszr.Fit(self)
		self.SetAutoLayout(True)
#====================================================================
#Class central to gnumed data input
#allows data entry of multiple different types, e.g scripts,
#referrals, measurements, recalls etc
#@TODO : just about everything
#section = calling section eg allergies, script
#----------------------------------------------------------
class EditTextBoxes(wx.Panel):
	def __init__(self, parent, id, editareaprompts, section):
		wx.Panel.__init__(self, parent, id, wx.DefaultPosition, wx.DefaultSize,style = wx.RAISED_BORDER | wx.TAB_TRAVERSAL)
		self.SetBackgroundColour(wx.Colour(222,222,222))
		self.parent = parent
		# rows, cols, hgap, vgap
		self.gszr = wx.GridSizer(len(editareaprompts), 1, 2, 2)

		if section == gmSECTION_SUMMARY:
			pass
		elif section == gmSECTION_DEMOGRAPHICS:
			pass
		elif section == gmSECTION_CLINICALNOTES:
			pass
		elif section == gmSECTION_FAMILYHISTORY:
			pass
		elif section == gmSECTION_PASTHISTORY:
			pass
			# line 1
			
#			self.txt_condition = cEditAreaField(self,PHX_CONDITION,wx.DefaultPosition,wx.DefaultSize)
#			self.rb_sideleft = wx.RadioButton(self,PHX_LEFT, _(" (L) "), wx.DefaultPosition,wx.DefaultSize)
#			self.rb_sideright = wx.RadioButton(self, PHX_RIGHT, _("(R)"), wx.DefaultPosition,wx.DefaultSize,wx.SUNKEN_BORDER)
#			self.rb_sideboth = wx.RadioButton(self, PHX_BOTH, _("Both"), wx.DefaultPosition,wx.DefaultSize)
			rbsizer = wx.BoxSizer(wx.HORIZONTAL)
#			rbsizer.Add(self.rb_sideleft,1,wx.EXPAND)
#			rbsizer.Add(self.rb_sideright,1,wx.EXPAND) 
#			rbsizer.Add(self.rb_sideboth,1,wx.EXPAND)
			szr1 = wx.BoxSizer(wx.HORIZONTAL)
#			szr1.Add(self.txt_condition, 4, wx.EXPAND)
			szr1.Add(rbsizer, 3, wx.EXPAND)
#			self.sizer_line1.Add(self.rb_sideleft,1,wx.EXPAND|wxALL,2)
#			self.sizer_line1.Add(self.rb_sideright,1,wx.EXPAND|wxALL,2)
#			self.sizer_line1.Add(self.rb_sideboth,1,wx.EXPAND|wxALL,2)
			# line 2
#			self.txt_notes1 = cEditAreaField(self,PHX_NOTES,wx.DefaultPosition,wx.DefaultSize)
			# line 3
#			self.txt_notes2= cEditAreaField(self,PHX_NOTES2,wx.DefaultPosition,wx.DefaultSize)
			# line 4
#			self.txt_agenoted = cEditAreaField(self, PHX_AGE, wx.DefaultPosition, wx.DefaultSize)
			szr4 = wx.BoxSizer(wx.HORIZONTAL)
#			szr4.Add(self.txt_agenoted, 1, wx.EXPAND)
			szr4.Add(5, 0, 5)
			# line 5
#			self.txt_yearnoted  = cEditAreaField(self,PHX_YEAR,wx.DefaultPosition,wx.DefaultSize)
			szr5 = wx.BoxSizer(wx.HORIZONTAL)
#			szr5.Add(self.txt_yearnoted, 1, wx.EXPAND)
			szr5.Add(5, 0, 5)
			# line 6
#			self.parent.cb_active = wx.CheckBox(self, PHX_ACTIVE, _("Active"), wx.DefaultPosition,wx.DefaultSize, wx.NO_BORDER)
#			self.parent.cb_operation = wx.CheckBox(self, PHX_OPERATION, _("Operation"), wx.DefaultPosition,wx.DefaultSize, wx.NO_BORDER)
#			self.parent.cb_confidential = wx.CheckBox(self, PHX_CONFIDENTIAL , _("Confidential"), wx.DefaultPosition,wx.DefaultSize, wx.NO_BORDER)
#			self.parent.cb_significant = wx.CheckBox(self, PHX_SIGNIFICANT, _("Significant"), wx.DefaultPosition,wx.DefaultSize, wx.NO_BORDER)
			szr6 = wx.BoxSizer(wx.HORIZONTAL)
#			szr6.Add(self.parent.cb_active, 1, wx.EXPAND)
#			szr6.Add(self.parent.cb_operation, 1, wx.EXPAND)
#			szr6.Add(self.parent.cb_confidential, 1, wx.EXPAND)
#			szr6.Add(self.parent.cb_significant, 1, wx.EXPAND)
			# line 7
#			self.txt_progressnotes  = cEditAreaField(self,PHX_PROGRESSNOTES ,wx.DefaultPosition,wx.DefaultSize)
			# line 8
			szr8 = wx.BoxSizer(wx.HORIZONTAL)
			szr8.Add(5, 0, 6)
			szr8.Add(self._make_standard_buttons(), 0, wx.EXPAND)

			self.gszr.Add(szr1,0,wx.EXPAND)
			self.gszr.Add(self.txt_notes1,0,wx.EXPAND)
			self.gszr.Add(self.txt_notes2,0,wx.EXPAND)
			self.gszr.Add(szr4,0,wx.EXPAND)
			self.gszr.Add(szr5,0,wx.EXPAND)
			self.gszr.Add(szr6,0,wx.EXPAND)
			self.gszr.Add(self.txt_progressnotes,0,wx.EXPAND)
			self.gszr.Add(szr8,0,wx.EXPAND)
			#self.anylist = wx.ListCtrl(self, -1,  wx.DefaultPosition,wx.DefaultSize,wx.LC_REPORT|wx.LC_LIST|wx.SUNKEN_BORDER)

		elif section == gmSECTION_SCRIPT:
			pass
		elif section == gmSECTION_REQUESTS:
			pass
		elif section == gmSECTION_RECALLS:
			pass
		else:
			pass

		self.SetSizer(self.gszr)
		self.gszr.Fit(self)

		self.SetAutoLayout(True)
		self.Show(True)
	#----------------------------------------------------------------
	def _make_standard_buttons(self):
		self.btn_OK = wx.Button(self, -1, _("Ok"))
		self.btn_Clear = wx.Button(self, -1, _("Clear"))
		szr_buttons = wx.BoxSizer(wx.HORIZONTAL)
		szr_buttons.Add(self.btn_OK, 1, wx.EXPAND, wx.ALL, 1)
		szr_buttons.Add(5, 0, 0)
		szr_buttons.Add(self.btn_Clear, 1, wx.EXPAND, wx.ALL, 1)
		return szr_buttons
#====================================================================
class EditArea(wx.Panel):
	def __init__(self, parent, id, line_labels, section):
		_log.warning('***** old style EditArea instantiated, please convert *****')

		wx.Panel.__init__(self, parent, id, wx.DefaultPosition, wx.DefaultSize, style = wx.NO_BORDER)
		self.SetBackgroundColour(wx.Colour(222,222,222))

		# make prompts
		prompts = gmPnlEditAreaPrompts(self, -1, line_labels)
		# and shadow below prompts in ...
		shadow_below_prompts = wx.Window(self, -1, wx.DefaultPosition, wx.DefaultSize, 0)
		# ... gray
		shadow_below_prompts.SetBackgroundColour(richards_dark_gray)
		szr_shadow_below_prompts = wx.BoxSizer (wx.HORIZONTAL)
		szr_shadow_below_prompts.Add(5,0,0,wx.EXPAND)
		szr_shadow_below_prompts.Add(shadow_below_prompts, 10, wx.EXPAND)
		# stack prompts and shadow vertically
		szr_prompts = wx.BoxSizer(wx.VERTICAL)
		szr_prompts.Add(prompts, 97, wx.EXPAND)
		szr_prompts.Add(szr_shadow_below_prompts, 5, wx.EXPAND)

		# make edit fields
		edit_fields = EditTextBoxes(self, -1, line_labels, section)
		# make shadow below edit area ...
		shadow_below_editarea = wx.Window(self, -1, wx.DefaultPosition, wx.DefaultSize, 0)
		# ... gray
		shadow_below_editarea.SetBackgroundColour(richards_coloured_gray)
		szr_shadow_below_editarea = wx.BoxSizer(wx.HORIZONTAL)
		szr_shadow_below_editarea.Add(5,0,0,wx.EXPAND)
		szr_shadow_below_editarea.Add(shadow_below_editarea, 12, wx.EXPAND)
		# stack edit fields and shadow vertically
		szr_editarea = wx.BoxSizer(wx.VERTICAL)
		szr_editarea.Add(edit_fields, 92, wx.EXPAND)
		szr_editarea.Add(szr_shadow_below_editarea, 5, wx.EXPAND)

		# make shadows to the right of ...
		# ... the prompts ...
		shadow_rightof_prompts = wx.Window(self, -1, wx.DefaultPosition, wx.DefaultSize, 0)
		shadow_rightof_prompts.SetBackgroundColour(richards_dark_gray)
		szr_shadow_rightof_prompts = wx.BoxSizer(wx.VERTICAL)
		szr_shadow_rightof_prompts.Add(0,5,0,wx.EXPAND)
		szr_shadow_rightof_prompts.Add(shadow_rightof_prompts,1,wx.EXPAND)
		# ... and the edit area
		shadow_rightof_editarea = wx.Window(self, -1, wx.DefaultPosition, wx.DefaultSize, 0)
		shadow_rightof_editarea.SetBackgroundColour(richards_coloured_gray)
		szr_shadow_rightof_editarea = wx.BoxSizer(wx.VERTICAL)
		szr_shadow_rightof_editarea.Add(0, 5, 0, wx.EXPAND)
		szr_shadow_rightof_editarea.Add(shadow_rightof_editarea, 1, wx.EXPAND)

		# stack prompts, shadows and fields horizontally
		self.szr_main_panels = wx.BoxSizer(wx.HORIZONTAL)
		self.szr_main_panels.Add(szr_prompts, 10, wx.EXPAND)
		self.szr_main_panels.Add(szr_shadow_rightof_prompts, 1, wx.EXPAND)
		self.szr_main_panels.Add(5, 0, 0, wx.EXPAND)
		self.szr_main_panels.Add(szr_editarea, 89, wx.EXPAND)
		self.szr_main_panels.Add(szr_shadow_rightof_editarea, 1, wx.EXPAND)

		# use sizer for border around everything plus a little gap
		# FIXME: fold into szr_main_panels ?
		self.szr_central_container = wx.BoxSizer(wx.HORIZONTAL)
		self.szr_central_container.Add(self.szr_main_panels, 1, wx.EXPAND | wx.ALL, 5)
		self.SetSizer(self.szr_central_container)
		self.szr_central_container.Fit(self)
		self.SetAutoLayout(True)
		self.Show(True)


#====================================================================
# old stuff still needed for conversion
#--------------------------------------------------------------------
#====================================================================

#====================================================================

#		elif section == gmSECTION_SCRIPT:
#		      gmLog.gmDefLog.Log (gmLog.lData, "in script section now")
#		      self.text1_prescription_reason = cEditAreaField(self,-1,wx.DefaultPosition,wx.DefaultSize)
#		      self.text2_drug_class = cEditAreaField(self,-1,wx.DefaultPosition,wx.DefaultSize)
#		      self.text3_generic_drug = cEditAreaField(self,-1,wx.DefaultPosition,wx.DefaultSize)
#		      self.text4_product_drug = cEditAreaField(self,-1,wx.DefaultPosition,wx.DefaultSize)
#		      self.text5_strength = cEditAreaField(self,-1,wx.DefaultPosition,wx.DefaultSize)
#		      self.text6_directions = cEditAreaField(self,-1,wx.DefaultPosition,wx.DefaultSize)
#		      self.text7_for_duration = cEditAreaField(self,-1,wx.DefaultPosition,wx.DefaultSize)
#		      self.text8_prescription_progress_notes = cEditAreaField(self,-1,wx.DefaultPosition,wx.DefaultSize)
#		      self.text9_quantity = cEditAreaField(self,-1,wx.DefaultPosition,wx.DefaultSize)
#		      lbl_veterans = cPrompt_edit_area(self,-1,"  Veteran  ")
#		      lbl_reg24 = cPrompt_edit_area(self,-1,"  Reg 24  ")
#		      lbl_quantity = cPrompt_edit_area(self,-1,"  Quantity  ")
#		      lbl_repeats = cPrompt_edit_area(self,-1,"  Repeats  ")
#		      lbl_usualmed = cPrompt_edit_area(self,-1,"  Usual  ")
#		      self.cb_veteran  = wx.CheckBox(self, -1, " Yes ", wx.DefaultPosition,wx.DefaultSize, wx.NO_BORDER)
#		      self.cb_reg24 = wx.CheckBox(self, -1, " Yes ", wx.DefaultPosition,wx.DefaultSize, wx.NO_BORDER)
#		      self.cb_usualmed = wx.CheckBox(self, -1, " Yes ", wx.DefaultPosition,wx.DefaultSize, wx.NO_BORDER)
#		      self.sizer_auth_PI = wx.BoxSizer(wxHORIZONTAL)
#		      self.btn_authority = wx.Button(self,-1,">Authority")     #create authority script
#		      self.btn_briefPI   = wx.Button(self,-1,"Brief PI")       #show brief drug product information
#		      self.sizer_auth_PI.Add(self.btn_authority,1,wx.EXPAND|wxALL,2)  #put authority button and PI button
#		      self.sizer_auth_PI.Add(self.btn_briefPI,1,wx.EXPAND|wxALL,2)    #on same sizer
#		      self.text10_repeats  = cEditAreaField(self,-1,wx.DefaultPosition,wx.DefaultSize)
#		      self.sizer_line3.Add(self.text3_generic_drug,5,wx.EXPAND)
#		      self.sizer_line3.Add(lbl_veterans,1,wx.EXPAND)
 #       	      self.sizer_line3.Add(self.cb_veteran,1,wx.EXPAND)
#		      self.sizer_line4.Add(self.text4_product_drug,5,wx.EXPAND)
#		      self.sizer_line4.Add(lbl_reg24,1,wx.EXPAND)
 #       	      self.sizer_line4.Add(self.cb_reg24,1,wx.EXPAND)
#		      self.sizer_line5.Add(self.text5_strength,5,wx.EXPAND)
#		      self.sizer_line5.Add(lbl_quantity,1,wx.EXPAND)
 #       	      self.sizer_line5.Add(self.text9_quantity,1,wx.EXPAND)
#		      self.sizer_line6.Add(self.text6_directions,5,wx.EXPAND)
#		      self.sizer_line6.Add(lbl_repeats,1,wx.EXPAND)
 #       	      self.sizer_line6.Add(self.text10_repeats,1,wx.EXPAND)
#		      self.sizer_line7.Add(self.text7_for_duration,5,wx.EXPAND)
#		      self.sizer_line7.Add(lbl_usualmed,1,wx.EXPAND)
 #       	      self.sizer_line7.Add(self.cb_usualmed,1,wx.EXPAND)
#		      self.sizer_line8.Add(5,0,0)
#		      self.sizer_line8.Add(self.sizer_auth_PI,2,wx.EXPAND)
#		      self.sizer_line8.Add(5,0,2)
#		      self.sizer_line8.Add(self.btn_OK,1,wx.EXPAND|wxALL,2)
#		      self.sizer_line8.Add(self.btn_Clear,1,wx.EXPAND|wxALL,2)
#		      self.gszr.Add(self.text1_prescription_reason,1,wx.EXPAND) #prescribe for
#		      self.gszr.Add(self.text2_drug_class,1,wx.EXPAND) #prescribe by class
#		      self.gszr.Add(self.sizer_line3,1,wx.EXPAND) #prescribe by generic, lbl_veterans, cb_veteran
#		      self.gszr.Add(self.sizer_line4,1,wx.EXPAND) #prescribe by product, lbl_reg24, cb_reg24
#		      self.gszr.Add(self.sizer_line5,1,wx.EXPAND) #drug strength, lbl_quantity, text_quantity 
#		      self.gszr.Add(self.sizer_line6,1,wx.EXPAND) #txt_directions, lbl_repeats, text_repeats 
#		      self.gszr.Add(self.sizer_line7,1,wx.EXPAND) #text_for,lbl_usual,chk_usual
#		      self.gszr.Add(self.text8_prescription_progress_notes,1,wx.EXPAND)            #text_progressNotes
#		      self.gszr.Add(self.sizer_line8,1,wx.EXPAND)
		      
		      
#	        elif section == gmSECTION_REQUESTS:
#		      #----------------------------------------------------------------------------- 	
	              #editing area for general requests e.g pathology, radiology, physiotherapy etc
		      #create textboxes, radiobuttons etc
		      #-----------------------------------------------------------------------------
#		      self.txt_request_type = cEditAreaField(self,ID_REQUEST_TYPE,wx.DefaultPosition,wx.DefaultSize)
#		      self.txt_request_company = cEditAreaField(self,ID_REQUEST_COMPANY,wx.DefaultPosition,wx.DefaultSize)
#		      self.txt_request_street = cEditAreaField(self,ID_REQUEST_STREET,wx.DefaultPosition,wx.DefaultSize)
#		      self.txt_request_suburb = cEditAreaField(self,ID_REQUEST_SUBURB,wx.DefaultPosition,wx.DefaultSize)
#		      self.txt_request_phone= cEditAreaField(self,ID_REQUEST_PHONE,wx.DefaultPosition,wx.DefaultSize)
#		      self.txt_request_requests = cEditAreaField(self,ID_REQUEST_REQUESTS,wx.DefaultPosition,wx.DefaultSize)
#		      self.txt_request_notes = cEditAreaField(self,ID_REQUEST_FORMNOTES,wx.DefaultPosition,wx.DefaultSize)
#		      self.txt_request_medications = cEditAreaField(self,ID_REQUEST_MEDICATIONS,wx.DefaultPosition,wx.DefaultSize)
#		      self.txt_request_copyto = cEditAreaField(self,ID_REQUEST_COPYTO,wx.DefaultPosition,wx.DefaultSize)
#		      self.txt_request_progressnotes = cEditAreaField(self,ID_PROGRESSNOTES,wx.DefaultPosition,wx.DefaultSize)
#		      self.lbl_companyphone = cPrompt_edit_area(self,-1,"  Phone  ")
#		      self.cb_includeallmedications = wx.CheckBox(self, -1, " Include all medications ", wx.DefaultPosition,wx.DefaultSize, wx.NO_BORDER)
#		      self.rb_request_bill_bb = wx.RadioButton(self, ID_REQUEST_BILL_BB, "Bulk Bill ", wx.DefaultPosition,wx.DefaultSize)
#	              self.rb_request_bill_private = wx.RadioButton(self, ID_REQUEST_BILL_PRIVATE, "Private", wx.DefaultPosition,wx.DefaultSize,wx.SUNKEN_BORDER)
#		      self.rb_request_bill_rebate = wx.RadioButton(self, ID_REQUEST_BILL_REBATE, "Rebate", wx.DefaultPosition,wx.DefaultSize)
#		      self.rb_request_bill_wcover = wx.RadioButton(self, ID_REQUEST_BILL_wcover, "w/cover", wx.DefaultPosition,wx.DefaultSize)
		      #--------------------------------------------------------------
                     #add controls to sizers where multiple controls per editor line
		      #--------------------------------------------------------------
#                      self.sizer_request_optionbuttons = wx.BoxSizer(wxHORIZONTAL)
#		      self.sizer_request_optionbuttons.Add(self.rb_request_bill_bb,1,wx.EXPAND)
#		      self.sizer_request_optionbuttons.Add(self.rb_request_bill_private ,1,wx.EXPAND)
#                      self.sizer_request_optionbuttons.Add(self.rb_request_bill_rebate  ,1,wx.EXPAND)
#                      self.sizer_request_optionbuttons.Add(self.rb_request_bill_wcover  ,1,wx.EXPAND)
#		      self.sizer_line4.Add(self.txt_request_suburb,4,wx.EXPAND)
#		      self.sizer_line4.Add(self.lbl_companyphone,1,wx.EXPAND)
#		      self.sizer_line4.Add(self.txt_request_phone,2,wx.EXPAND)
#		      self.sizer_line7.Add(self.txt_request_medications, 4,wx.EXPAND)
#		      self.sizer_line7.Add(self.cb_includeallmedications,3,wx.EXPAND)
#		      self.sizer_line10.AddSizer(self.sizer_request_optionbuttons,3,wx.EXPAND)
#		      self.sizer_line10.AddSizer(self.szr_buttons,1,wx.EXPAND)
		      #self.sizer_line10.Add(self.btn_OK,1,wx.EXPAND|wxALL,1)
	              #self.sizer_line10.Add(self.btn_Clear,1,wx.EXPAND|wxALL,1)  
		      #------------------------------------------------------------------
		      #add either controls or sizers with controls to vertical grid sizer
		      #------------------------------------------------------------------
#                      self.gszr.Add(self.txt_request_type,0,wx.EXPAND)                   #e.g Pathology
#		      self.gszr.Add(self.txt_request_company,0,wx.EXPAND)                #e.g Douglas Hanly Moir
#		      self.gszr.Add(self.txt_request_street,0,wx.EXPAND)                 #e.g 120 Big Street  
#		      self.gszr.AddSizer(self.sizer_line4,0,wx.EXPAND)                   #e.g RYDE NSW Phone 02 1800 222 365
#		      self.gszr.Add(self.txt_request_requests,0,wx.EXPAND)               #e.g FBC;ESR;UEC;LFTS
#		      self.gszr.Add(self.txt_request_notes,0,wx.EXPAND)                  #e.g generally tired;weight loss;
#		      self.gszr.AddSizer(self.sizer_line7,0,wx.EXPAND)                   #e.g Lipitor;losec;zyprexa
#		      self.gszr.Add(self.txt_request_copyto,0,wx.EXPAND)                 #e.g Dr I'm All Heart, 120 Big Street Smallville
#		      self.gszr.Add(self.txt_request_progressnotes,0,wx.EXPAND)          #emphasised to patient must return for results 
 #                     self.sizer_line8.Add(5,0,6)
#		      self.sizer_line8.Add(self.btn_OK,1,wx.EXPAND|wxALL,2)
#	              self.sizer_line8.Add(self.btn_Clear,1,wx.EXPAND|wxALL,2)   
#		      self.gszr.Add(self.sizer_line10,0,wx.EXPAND)                       #options:b/bill private, rebate,w/cover btnok,btnclear

		      
#	        elif section == gmSECTION_MEASUREMENTS:
#		      self.combo_measurement_type = wx.ComboBox(self, ID_MEASUREMENT_TYPE, "", wx.DefaultPosition,wx.DefaultSize, ['Blood pressure','INR','Height','Weight','Whatever other measurement you want to put in here'], wx.CB_DROPDOWN)
#		      self.combo_measurement_type.SetFont(wx.Font(12,wx.SWISS,wx.NORMAL, wx.BOLD,False,''))
#		      self.combo_measurement_type.SetForegroundColour(wx.Colour(255,0,0))
#		      self.txt_measurement_value = cEditAreaField(self,ID_MEASUREMENT_VALUE,wx.DefaultPosition,wx.DefaultSize)
#		      self.txt_txt_measurement_date = cEditAreaField(self,ID_MEASUREMENT_DATE,wx.DefaultPosition,wx.DefaultSize)
#		      self.txt_txt_measurement_comment = cEditAreaField(self,ID_MEASUREMENT_COMMENT,wx.DefaultPosition,wx.DefaultSize)
#		      self.txt_txt_measurement_progressnote = cEditAreaField(self,ID_PROGRESSNOTES,wx.DefaultPosition,wx.DefaultSize)
#		      self.sizer_graphnextbtn = wx.BoxSizer(wxHORIZONTAL)
#		      self.btn_nextvalue = wx.Button(self,ID_MEASUREMENT_NEXTVALUE,"   Next Value   ")                 #clear fields except type
#		      self.btn_graph   = wx.Button(self,ID_MEASUREMENT_GRAPH," Graph ")                        #graph all values of this type
#		      self.sizer_graphnextbtn.Add(self.btn_nextvalue,1,wx.EXPAND|wxALL,2)  #put next and graph button
#		      self.sizer_graphnextbtn.Add(self.btn_graph,1,wx.EXPAND|wxALL,2)      #on same sizer	
#		      self.gszr.Add(self.combo_measurement_type,0,wx.EXPAND)              #e.g Blood pressure
#		      self.gszr.Add(self.txt_measurement_value,0,wx.EXPAND)               #e.g 120.70
#		      self.gszr.Add(self.txt_txt_measurement_date,0,wx.EXPAND)            #e.g 10/12/2001
#		      self.gszr.Add(self.txt_txt_measurement_comment,0,wx.EXPAND)         #e.g sitting, right arm
#		      self.gszr.Add(self.txt_txt_measurement_progressnote,0,wx.EXPAND)    #e.g given home BP montitor, see 1 week
#		      self.sizer_line8.Add(5,0,0)
#		      self.sizer_line8.Add(self.sizer_graphnextbtn,2,wx.EXPAND)
#		      self.sizer_line8.Add(5,0,2)
#		      self.sizer_line8.Add(self.btn_OK,1,wx.EXPAND|wxALL,2)
#		      self.sizer_line8.Add(self.btn_Clear,1,wx.EXPAND|wxALL,2)
#		      self.gszr.AddSizer(self.sizer_line8,0,wx.EXPAND)
		      

#	        elif section == gmSECTION_REFERRALS:
#		      self.btnpreview = wx.Button(self,-1,"Preview")
#		      self.sizer_btnpreviewok = wx.BoxSizer(wxHORIZONTAL)
		      #--------------------------------------------------------
	              #editing area for referral letters, insurance letters etc
		      #create textboxes, checkboxes etc
		      #--------------------------------------------------------
#		      self.txt_referralcategory = cEditAreaField(self,ID_REFERRAL_CATEGORY,wx.DefaultPosition,wx.DefaultSize)
#		      self.txt_referralname = cEditAreaField(self,ID_REFERRAL_NAME,wx.DefaultPosition,wx.DefaultSize)
#		      self.txt_referralorganisation = cEditAreaField(self,ID_REFERRAL_ORGANISATION,wx.DefaultPosition,wx.DefaultSize)
#		      self.txt_referralstreet1 = cEditAreaField(self,ID_REFERRAL_STREET1,wx.DefaultPosition,wx.DefaultSize)
#		      self.txt_referralstreet2 = cEditAreaField(self,ID_REFERRAL_STREET2,wx.DefaultPosition,wx.DefaultSize)
#		      self.txt_referralstreet3 = cEditAreaField(self,ID_REFERRAL_STREET3,wx.DefaultPosition,wx.DefaultSize)
#		      self.txt_referralsuburb = cEditAreaField(self,ID_REFERRAL_SUBURB,wx.DefaultPosition,wx.DefaultSize)
#		      self.txt_referralpostcode = cEditAreaField(self,ID_REFERRAL_POSTCODE,wx.DefaultPosition,wx.DefaultSize)
#		      self.txt_referralfor = cEditAreaField(self,ID_REFERRAL_FOR,wx.DefaultPosition,wx.DefaultSize)
#		      self.txt_referralwphone= cEditAreaField(self,ID_REFERRAL_WPHONE,wx.DefaultPosition,wx.DefaultSize)
#		      self.txt_referralwfax= cEditAreaField(self,ID_REFERRAL_WFAX,wx.DefaultPosition,wx.DefaultSize)
#		      self.txt_referralwemail= cEditAreaField(self,ID_REFERRAL_WEMAIL,wx.DefaultPosition,wx.DefaultSize)
		      #self.txt_referralrequests = cEditAreaField(self,ID_REFERRAL_REQUESTS,wx.DefaultPosition,wx.DefaultSize)
		      #self.txt_referralnotes = cEditAreaField(self,ID_REFERRAL_FORMNOTES,wx.DefaultPosition,wx.DefaultSize)
		      #self.txt_referralmedications = cEditAreaField(self,ID_REFERRAL_MEDICATIONS,wx.DefaultPosition,wx.DefaultSize)
#		      self.txt_referralcopyto = cEditAreaField(self,ID_REFERRAL_COPYTO,wx.DefaultPosition,wx.DefaultSize)
#		      self.txt_referralprogressnotes = cEditAreaField(self,ID_PROGRESSNOTES,wx.DefaultPosition,wx.DefaultSize)
#		      self.lbl_referralwphone = cPrompt_edit_area(self,-1,"  W Phone  ")
#		      self.lbl_referralwfax = cPrompt_edit_area(self,-1,"  W Fax  ")
#		      self.lbl_referralwemail = cPrompt_edit_area(self,-1,"  W Email  ")
#		      self.lbl_referralpostcode = cPrompt_edit_area(self,-1,"  Postcode  ")
#		      self.chkbox_referral_usefirstname = wx.CheckBox(self, -1, " Use Firstname ", wx.DefaultPosition,wx.DefaultSize, wx.NO_BORDER)
#		      self.chkbox_referral_headoffice = wx.CheckBox(self, -1, " Head Office ", wx.DefaultPosition,wx.DefaultSize, wx.NO_BORDER)
#		      self.chkbox_referral_medications = wx.CheckBox(self, -1, " Medications ", wx.DefaultPosition,wx.DefaultSize, wx.NO_BORDER)
#		      self.chkbox_referral_socialhistory = wx.CheckBox(self, -1, " Social History ", wx.DefaultPosition,wx.DefaultSize, wx.NO_BORDER)
#		      self.chkbox_referral_familyhistory = wx.CheckBox(self, -1, " Family History ", wx.DefaultPosition,wx.DefaultSize, wx.NO_BORDER)
#		      self.chkbox_referral_pastproblems = wx.CheckBox(self, -1, " Past Problems ", wx.DefaultPosition,wx.DefaultSize, wx.NO_BORDER)
#		      self.chkbox_referral_activeproblems = wx.CheckBox(self, -1, " Active Problems ", wx.DefaultPosition,wx.DefaultSize, wx.NO_BORDER)
#		      self.chkbox_referral_habits = wx.CheckBox(self, -1, " Habits ", wx.DefaultPosition,wx.DefaultSize, wx.NO_BORDER)
		      #self.chkbox_referral_Includeall = wx.CheckBox(self, -1, " Include all of the above ", wx.DefaultPosition,wx.DefaultSize, wx.NO_BORDER)
		      #--------------------------------------------------------------
                      #add controls to sizers where multiple controls per editor line
		      #--------------------------------------------------------------
#		      self.sizer_line2.Add(self.txt_referralname,2,wx.EXPAND) 
#		      self.sizer_line2.Add(self.chkbox_referral_usefirstname,2,wx.EXPAND)
#		      self.sizer_line3.Add(self.txt_referralorganisation,2,wx.EXPAND)
#		      self.sizer_line3.Add(self.chkbox_referral_headoffice,2, wx.EXPAND)
#		      self.sizer_line4.Add(self.txt_referralstreet1,2,wx.EXPAND)
#		      self.sizer_line4.Add(self.lbl_referralwphone,1,wx.EXPAND)
#		      self.sizer_line4.Add(self.txt_referralwphone,1,wx.EXPAND)
#		      self.sizer_line5.Add(self.txt_referralstreet2,2,wx.EXPAND)
#		      self.sizer_line5.Add(self.lbl_referralwfax,1,wx.EXPAND)
#		      self.sizer_line5.Add(self.txt_referralwfax,1,wx.EXPAND)
#		      self.sizer_line6.Add(self.txt_referralstreet3,2,wx.EXPAND)
#		      self.sizer_line6.Add(self.lbl_referralwemail,1,wx.EXPAND)
#		      self.sizer_line6.Add(self.txt_referralwemail,1,wx.EXPAND)
#		      self.sizer_line7.Add(self.txt_referralsuburb,2,wx.EXPAND)
#		      self.sizer_line7.Add(self.lbl_referralpostcode,1,wx.EXPAND)
#		      self.sizer_line7.Add(self.txt_referralpostcode,1,wx.EXPAND)
#		      self.sizer_line10.Add(self.chkbox_referral_medications,1,wx.EXPAND)
#	              self.sizer_line10.Add(self.chkbox_referral_socialhistory,1,wx.EXPAND)
#		      self.sizer_line10.Add(self.chkbox_referral_familyhistory,1,wx.EXPAND)
#		      self.sizer_line11.Add(self.chkbox_referral_pastproblems  ,1,wx.EXPAND)
#		      self.sizer_line11.Add(self.chkbox_referral_activeproblems  ,1,wx.EXPAND)
#		      self.sizer_line11.Add(self.chkbox_referral_habits  ,1,wx.EXPAND)
#		      self.sizer_btnpreviewok.Add(self.btnpreview,0,wx.EXPAND)
#		      self.szr_buttons.Add(self.btn_Clear,0, wx.EXPAND)		      
		      #------------------------------------------------------------------
		      #add either controls or sizers with controls to vertical grid sizer
		      #------------------------------------------------------------------
 #                     self.gszr.Add(self.txt_referralcategory,0,wx.EXPAND)               #e.g Othopaedic surgeon
#		      self.gszr.Add(self.sizer_line2,0,wx.EXPAND)                        #e.g Dr B Breaker
#		      self.gszr.Add(self.sizer_line3,0,wx.EXPAND)                        #e.g General Orthopaedic services
#		      self.gszr.Add(self.sizer_line4,0,wx.EXPAND)                        #e.g street1
#		      self.gszr.Add(self.sizer_line5,0,wx.EXPAND)                        #e.g street2
#		      self.gszr.Add(self.sizer_line6,0,wx.EXPAND)                        #e.g street3
#		      self.gszr.Add(self.sizer_line7,0,wx.EXPAND)                        #e.g suburb and postcode
#		      self.gszr.Add(self.txt_referralfor,0,wx.EXPAND)                    #e.g Referral for an opinion
#		      self.gszr.Add(self.txt_referralcopyto,0,wx.EXPAND)                 #e.g Dr I'm All Heart, 120 Big Street Smallville
#		      self.gszr.Add(self.txt_referralprogressnotes,0,wx.EXPAND)          #emphasised to patient must return for results 
#		      self.gszr.AddSizer(self.sizer_line10,0,wx.EXPAND)                   #e.g check boxes to include medications etc
#		      self.gszr.Add(self.sizer_line11,0,wx.EXPAND)                       #e.g check boxes to include active problems etc
		      #self.spacer = wx.Window(self,-1,wx.DefaultPosition,wx.DefaultSize)
		      #self.spacer.SetBackgroundColour(wx.Colour(255,255,255))
#		      self.sizer_line12.Add(5,0,6)
		      #self.sizer_line12.Add(self.spacer,6,wx.EXPAND)
#		      self.sizer_line12.Add(self.btnpreview,1,wx.EXPAND|wxALL,2)
#	              self.sizer_line12.Add(self.btn_Clear,1,wx.EXPAND|wxALL,2)    
#	              self.gszr.Add(self.sizer_line12,0,wx.EXPAND)                       #btnpreview and btn clear
		      

#		elif section == gmSECTION_RECALLS:
		      #FIXME remove present options in this combo box	  #FIXME defaults need to be loaded from database	  
#		      self.combo_tosee = wx.ComboBox(self, ID_RECALLS_TOSEE, "", wx.DefaultPosition,wx.DefaultSize, ['Doctor1','Doctor2','Nurse1','Dietition'], wx.CB_READONLY ) #wx.CB_DROPDOWN)
#		      self.combo_tosee.SetFont(wx.Font(12,wx.SWISS,wx.NORMAL, wx.BOLD,False,''))
#		      self.combo_tosee.SetForegroundColour(wx.Colour(255,0,0))
		      #FIXME defaults need to be loaded from database
#		      self.combo_recall_method = wx.ComboBox(self, ID_RECALLS_CONTACTMETHOD, "", wx.DefaultPosition,wx.DefaultSize, ['Letter','Telephone','Email','Carrier pigeon'], wx.CB_READONLY )
#		      self.combo_recall_method.SetFont(wx.Font(12,wx.SWISS,wx.NORMAL, wx.BOLD,False,''))
#		      self.combo_recall_method.SetForegroundColour(wx.Colour(255,0,0))
		      #FIXME defaults need to be loaded from database
 #                     self.combo_apptlength = wx.ComboBox(self, ID_RECALLS_APPNTLENGTH, "", wx.DefaultPosition,wx.DefaultSize, ['brief','standard','long','prolonged'], wx.CB_READONLY )
#		      self.combo_apptlength.SetFont(wx.Font(12,wx.SWISS,wx.NORMAL, wx.BOLD,False,''))
#		      self.combo_apptlength.SetForegroundColour(wx.Colour(255,0,0))
#		      self.txt_recall_for = cEditAreaField(self,ID_RECALLS_TXT_FOR, wx.DefaultPosition,wx.DefaultSize)
#		      self.txt_recall_due = cEditAreaField(self,ID_RECALLS_TXT_DATEDUE, wx.DefaultPosition,wx.DefaultSize)
#		      self.txt_recall_addtext = cEditAreaField(self,ID_RECALLS_TXT_ADDTEXT,wx.DefaultPosition,wx.DefaultSize)
#		      self.txt_recall_include = cEditAreaField(self,ID_RECALLS_TXT_INCLUDEFORMS,wx.DefaultPosition,wx.DefaultSize)
#		      self.txt_recall_progressnotes = cEditAreaField(self,ID_PROGRESSNOTES,wx.DefaultPosition,wx.DefaultSize)
#		      self.lbl_recall_consultlength = cPrompt_edit_area(self,-1,"  Appointment length  ")
		      #sizer_lkine1 has the method of recall and the appointment length
#		      self.sizer_line1.Add(self.combo_recall_method,1,wx.EXPAND)
#		      self.sizer_line1.Add(self.lbl_recall_consultlength,1,wx.EXPAND)
#		      self.sizer_line1.Add(self.combo_apptlength,1,wx.EXPAND)
		      #Now add the controls to the grid sizer
 #                     self.gszr.Add(self.combo_tosee,1,wx.EXPAND)                       #list of personel for patient to see
#		      self.gszr.Add(self.txt_recall_for,1,wx.EXPAND)                    #the actual recall may be free text or word wheel  
#		      self.gszr.Add(self.txt_recall_due,1,wx.EXPAND)                    #date of future recall 
#		      self.gszr.Add(self.txt_recall_addtext,1,wx.EXPAND)                #added explanation e.g 'come fasting' 
#		      self.gszr.Add(self.txt_recall_include,1,wx.EXPAND)                #any forms to be sent out first eg FBC
#		      self.gszr.AddSizer(self.sizer_line1,1,wx.EXPAND)                        #the contact method, appointment length
#		      self.gszr.Add(self.txt_recall_progressnotes,1,wx.EXPAND)          #add any progress notes for consultation
#		      self.sizer_line8.Add(5,0,6)
#		      self.sizer_line8.Add(self.btn_OK,1,wx.EXPAND|wxALL,2)
#	              self.sizer_line8.Add(self.btn_Clear,1,wx.EXPAND|wxALL,2)    
#		      self.gszr.Add(self.sizer_line8,1,wx.EXPAND)
#		else:
#		      pass

#====================================================================
# main
#--------------------------------------------------------------------
if __name__ == "__main__":

	#================================================================
	class cTestEditArea(cEditArea):
		def __init__(self, parent):
			cEditArea.__init__(self, parent, -1)
		def _define_prompts(self):
			self._add_prompt(line=1, label='line 1')
			self._add_prompt(line=2, label='buttons')
		def _define_fields(self, parent):
			# line 1
			self.fld_substance = cEditAreaField(parent)
			self._add_field(
				line = 1,
				pos = 1,
				widget = self.fld_substance,
				weight = 1
			)
			# line 2
			self._add_field(
				line = 2,
				pos = 1,
				widget = self._make_standard_buttons(parent),
				weight = 1
			)
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
#====================================================================

