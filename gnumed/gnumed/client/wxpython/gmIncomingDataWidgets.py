# -*- coding: utf-8 -*-
"""GNUmed incoming data widgets."""
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
	try: _
	except NameError:
		from Gnumed.pycommon import gmI18N
		gmI18N.activate_locale()
		gmI18N.install_domain()


from Gnumed.pycommon import gmDispatcher
from Gnumed.pycommon import gmMimeLib
from Gnumed.pycommon import gmWorkerThread
from Gnumed.business import gmIncomingData
from Gnumed.business import gmPerson
from Gnumed.wxpython import gmRegetMixin
from Gnumed.wxpython import gmGuiHelpers


_log = logging.getLogger('gm.auto-in-ui')

#============================================================
from Gnumed.wxGladeWidgets import wxgIncomingPluginPnl

class cIncomingPluginPnl(wxgIncomingPluginPnl.wxgIncomingPluginPnl, gmRegetMixin.cRegetOnPaintMixin):
	"""Panel holding a number of items for assigning to a patient.

	Used as notebook page.
	"""
	def __init__(self, *args, **kwargs):
		wxgIncomingPluginPnl.wxgIncomingPluginPnl.__init__(self, *args, **kwargs)
		gmRegetMixin.cRegetOnPaintMixin.__init__(self)
		self.__init_ui()
		self.__register_interests()

	#--------------------------------------------------------
	# event handling
	#--------------------------------------------------------
	def __register_interests(self):
		gmDispatcher.connect(signal = 'gm_table_mod', receiver = self._on_table_mod)

	#--------------------------------------------------------
	def _on_table_mod(self, *args, **kwargs):
		if kwargs['table'] != 'clin.incoming_data_unmatched':
			return

		self._schedule_data_reget()

	#--------------------------------------------------------
	def __init_ui(self):
		if not self._LCTRL_items.EnableCheckBoxes(enable = True):
			_log.error('cannot enable list item checkboxes')
		self._LCTRL_items.set_columns(columns = [_('Item'), _('Patient')])
		self._LCTRL_items.set_column_widths([wx.LIST_AUTOSIZE, wx.LIST_AUTOSIZE])
		self._LCTRL_items.set_resize_column()
		self._LCTRL_items.select_callback = self.__on_item_selected

	#--------------------------------------------------------
	# reget-on-paint mixin API
	#--------------------------------------------------------
	def _populate_with_data(self):
		list_rows = []
		data = []
		for i in gmIncomingData.get_incoming_data():
			if not i['comment']:
				continue
			parts = i['comment'].split('auto-import/', 1)
			if len(parts) == 1:
				comment = i['comment']
			else:
				if parts[1].strip():
					comment = parts[1].strip()
				else:
					comment = parts[0].strip()
			if not comment:
				continue
			if i['pk_identity_disambiguated']:
				pat = gmPerson.cPatient(i['pk_identity_disambiguated']).description_gender
			else:
				pat = ''
			list_rows.append([comment, pat])
			data.append(i)
		self._LCTRL_items.set_string_items(items = list_rows)
		self._LCTRL_items.set_data(data = data)
		self._LCTRL_items.set_column_widths()
		return True

	#--------------------------------------------------------
	# notebook plugin API
	#--------------------------------------------------------
	def repopulate_ui(self):
		self._populate_with_data()

	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	# text preview
	#--------------------------------------------------------
	def _worker__convert_to_text(self, filename:str=None, cookie=None) -> str:
		return cookie, gmMimeLib.convert_file_to_text(filename)

	#--------------------------------------------------------
	def _forwarder__update_preview_text(self, worker_result):
		cookie, txt_fname = worker_result
		if cookie != self.__worker_cookie4text:
			_log.debug('received results from old worker [%s], I am [%s], ignoring', cookie, self.__worker_cookie4text)
			return

		if not txt_fname:
			return

		wx.CallAfter(self.__update_preview_text, filename = txt_fname)

	#--------------------------------------------------------
	def __update_preview_text(self, filename):
		with open(filename, mode = 'rt', encoding = 'utf-8', errors = 'replace') as txt_file:
			self._TCTRL_preview.Value = txt_file.read()

	#--------------------------------------------------------
	def __show_text_preview(self, filename=None):
		if filename:
			self.__update_preview_text(filename)
		self._TCTRL_metadata.Hide()
		self._PNL_image_viewer.Hide()
		self._TCTRL_preview.Show()
		self._SZR_previews.StaticBox.SetLabel(' ' + _('Text of item'))
		self.Layout()

	#--------------------------------------------------------
	# metadata preview
	#--------------------------------------------------------
	def _forwarder__update_preview_metadata(self, worker_result):
		status, txt, cookie = worker_result
		if cookie != self.__worker_cookie4meta:
			_log.debug('received results from old worker [%s], I am [%s], ignoring', cookie, self.__worker_cookie4meta)
			return

		if not (status and txt):
			return

		wx.CallAfter(self.__update_preview_metadata, metadata = txt)

	#--------------------------------------------------------
	def __update_preview_metadata(self, metadata):
		self._TCTRL_metadata.Value = metadata

	#--------------------------------------------------------
	def __show_metadata_preview(self, metadata=None):
		if metadata:
			self.__update_preview_metadata(metadata)
		self._PNL_image_viewer.Hide()
		self._TCTRL_preview.Hide()
		self._TCTRL_metadata.Show()
		self._SZR_previews.StaticBox.SetLabel(' ' + _('Description of item (metadata)'))
		self.Layout()

	#--------------------------------------------------------
	# image preview
	#--------------------------------------------------------
	def _worker__convert_to_image(self, filename:str=None, cookie=None) -> str:
		return cookie, gmMimeLib.convert_file_to_image(filename)

	#--------------------------------------------------------
	def _forwarder__update_preview_image(self, worker_result):
		cookie, img_fname = worker_result
		if cookie != self.__worker_cookie4img:
			_log.debug('received results from old worker [%s], I am [%s], ignoring', cookie, self.__worker_cookie4img)
			return

		if not img_fname:
			return

		wx.CallAfter(self.__update_preview_image, filename = img_fname)

	#--------------------------------------------------------
	def __update_preview_image(self, filename):
		self._PNL_image_viewer.filename = filename

	#--------------------------------------------------------
	def __show_image_preview(self, filename=None):
		if filename:
			self._PNL_image_viewer.filename = filename
		self._TCTRL_preview.Hide()
		self._TCTRL_metadata.Hide()
		self._PNL_image_viewer.Show()
		self._SZR_previews.StaticBox.SetLabel(' ' + _('Image Preview'))
		self.Layout()

	#--------------------------------------------------------
	# event handlers
	#--------------------------------------------------------
	def _on_switch_preview_button_pressed(self, event):
		if self._PNL_image_viewer.IsShown():
			self.__show_text_preview()
			return

		if self._TCTRL_preview.IsShown():
			self.__show_metadata_preview()
			return

		if self._TCTRL_metadata.IsShown():
			self.__show_image_preview()
			self._PNL_image_viewer._BMP_image.SetFocus()
			return

		self.__show_metadata_preview()

	#--------------------------------------------------------
	def __on_item_selected(self, event):
		event.Skip()
		item = self._LCTRL_items.selected_item_data
		if not item:
			return

		self.__exported_filename = item.save_to_file()
		if not self.__exported_filename:
			return

		self._PNL_image_viewer.filename = None
		self.__worker_cookie4img = '%s-%s4img' % (self.__class__.__name__, self.__exported_filename)
		self.__worker_cookie4text = '%s-%s2txt' % (self.__class__.__name__, self.__exported_filename)
		self.__worker_cookie4meta = '%s-%s2meta' % (self.__class__.__name__, self.__exported_filename)
		self._PNL_image_viewer.Hide()
		self._TCTRL_preview.Value = ''
		self._TCTRL_preview.Hide()
		self._TCTRL_metadata.Value = ''
		self._TCTRL_metadata.Hide()
		is_image = gmMimeLib.is_probably_image(self.__exported_filename)
		if is_image:
			self.__show_image_preview(filename = self.__exported_filename)
		else:
			gmWorkerThread.execute_in_worker_thread (
				payload_function = self._worker__convert_to_image,
				payload_kwargs = {'filename': self.__exported_filename, 'cookie': self.__worker_cookie4img},
				completion_callback = self._forwarder__update_preview_image,
				worker_name = self.__class__.__name__
			)
		is_textfile = gmMimeLib.is_probably_textfile(self.__exported_filename)
		if is_textfile:
			self.__show_text_preview(filename = self.__exported_filename)
		else:
			gmWorkerThread.execute_in_worker_thread (
				payload_function = self._worker__convert_to_text,
				payload_kwargs = {'filename': self.__exported_filename, 'cookie': self.__worker_cookie4text},
				completion_callback = self._forwarder__update_preview_text,
				worker_name = self.__class__.__name__
			)
		if not (is_textfile or is_image):
			self.__show_metadata_preview()
		gmMimeLib.describe_file (
			self.__exported_filename,
			callback = self._forwarder__update_preview_metadata,
			cookie = self.__worker_cookie4meta
		)

	#--------------------------------------------------------
	def _on_view_item_button_pressed(self, event):
		event.Skip()
		item = self._LCTRL_items.selected_item_data
		if not item:
			return

		self.__exported_filename = item.save_to_file()
		if not self.__exported_filename:
			return

		gmMimeLib.call_viewer_on_file(aFile = self.__exported_filename, block = False)

	#--------------------------------------------------------
	def _on_toggle_item_checkbox_button_pressed(self, event):
		event.Skip()
		item_idx = self._LCTRL_items.get_selected_items(only_one = True)
		if item_idx in [None, -1]:
			return

		self._LCTRL_items.CheckItem(item_idx, check = not self._LCTRL_items.IsItemChecked(item_idx))

	#--------------------------------------------------------
	def _on_prev_page_button_pressed(self, event):
		event.Skip()
		self._PNL_image_viewer.show_previous_page()

	#--------------------------------------------------------
	def _on_first_page_button_pressed(self, event):
		event.Skip()
		self._PNL_image_viewer.show_first_page()

	#--------------------------------------------------------
	def _on_next_page_button_pressed(self, event):
		event.Skip()
		self._PNL_image_viewer.show_next_page()

	#--------------------------------------------------------
	def _on_remove_item_button_pressed(self, event):
		event.Skip()
		item = self._LCTRL_items.selected_item_data
		if not item:
			return

		do_delete = gmGuiHelpers.gm_show_question (
			question = _('Irrevocably delete the selected item ?'),
			title = _('Deleting incoming data item')
		)
		if not do_delete:
			return

		gmIncomingData.delete_incoming_data(pk_incoming_data = item['pk_incoming_data_unmatched'])

	#--------------------------------------------------------
	def _on_assign_items2patient_button_pressed(self, event):
		event.Skip()
		pat = self._TCTRL_search_patient.person
		if pat is None:
			return

		for incoming_item in self._LCTRL_items.checked_items_data:
			incoming_item.patient = pat

	#--------------------------------------------------------
	def _on_unassign_patient_button_pressed(self, event):
		event.Skip()
		item = self._LCTRL_items.selected_item_data
		if not item:
			return

		item.patient = None

#============================================================
# main
#------------------------------------------------------------
if __name__ == "__main__":

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	from Gnumed.pycommon import gmLog2
	del _
	from Gnumed.pycommon import gmI18N
	gmI18N.activate_locale()
	gmI18N.install_domain()

	from Gnumed.wxpython import gmGuiTest

	#--------------------------------------------------------
	def test_plugin():
		wx.Log.EnableLogging(enable = False)
		gmGuiTest.test_widget(cIncomingPluginPnl, patient = 12)

	#--------------------------------------------------------
	test_plugin()
