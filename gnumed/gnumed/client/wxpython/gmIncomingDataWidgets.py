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

from Gnumed.pycommon import gmCfgDB
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmMimeLib
from Gnumed.pycommon import gmDateTime
from Gnumed.pycommon import gmDispatcher
from Gnumed.pycommon import gmScanBackend
from Gnumed.business import gmPerson
from Gnumed.business import gmPraxis
from Gnumed.business import gmIncomingData
from Gnumed.wxpython import gmRegetMixin
from Gnumed.wxpython import gmGuiHelpers
from Gnumed.wxpython import gmListWidgets


_log = logging.getLogger('gm.auto-in-ui')

#============================================================
class cIncomingDataListCtrl(gmListWidgets.cReportListCtrl):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		if not self.EnableCheckBoxes(enable = True):
			_log.error('cannot enable list item checkboxes')
		self.set_columns(columns = [_('Incoming document'), _('Patient')])
		self.set_column_widths([wx.LIST_AUTOSIZE, wx.LIST_AUTOSIZE])
		#self.set_resize_column()

	#--------------------------------------------------------
	def repopulate(self, pk_patient=None) -> bool:
		list_rows = []
		data = []
		items = gmIncomingData.get_incoming_data()
		if pk_patient:
			items = [ i for i in items if i['pk_identity_disambiguated'] == pk_patient ]
		for i in items:
			if i['comment']:
				comment = i['comment'].strip()
			else:
				comment = '?'
#			parts = i['comment'].split('auto-import/', 1)
#			if len(parts) > 1:
#				if parts[1].strip():
#					comment = parts[1].strip()
#				else:
#					comment = parts[0].strip()
			pat = self._get_patient_column_value(i)
			list_rows.append([comment, pat])
			data.append(i)
		self.set_string_items(items = list_rows)
		self.set_data(data = data)
		self.set_column_widths()
		return True

	#--------------------------------------------------------
	def view_items_externally(self):
		if self.ItemCount == 0:
			return

		# only one page, show that, regardless of whether selected or not
		if self.ItemCount == 1:
			page_fname = self.get_item_data(0).save_to_file()
			(success, msg) = gmMimeLib.call_viewer_on_file(page_fname)
			if success:
				return

			gmGuiHelpers.gm_show_warning (
				aMessage = _('Cannot display item:\n%s') % msg,
				aTitle = _('displaying incoming item')
			)
			return

		items = self.selected_item_data
		if not items:
			return

		# did user select one of multiple pages ?
		page_fnames = [ i.save_to_file() for i in items ]
		if len(page_fnames) == 0:
			gmDispatcher.send(signal = 'statustext', msg = _('Nothing selected for viewing.'), beep = True)
			return

		for page_fname in page_fnames:
			(success, msg) = gmMimeLib.call_viewer_on_file(page_fname)
			if not success:
				gmGuiHelpers.gm_show_warning (
					aMessage = _('Cannot display item:\n%s') % msg,
					aTitle = _('displaying incoming item')
				)

	#--------------------------------------------------------
	def _get_patient_column_value(self, item) -> str:
		if not item['pk_identity_disambiguated']:
			return ''

		return gmPerson.cPatient(item['pk_identity_disambiguated']).description_gender

#============================================================
class cCurrentPatientIncomingDataListCtrl(cIncomingDataListCtrl):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.set_resize_column(0)

	#--------------------------------------------------------
	def repopulate(self, pk_patient=None) -> bool:
		pat = gmPerson.gmCurrentPatient()
		if pat.connected:
			return super().repopulate(pk_patient = gmPerson.gmCurrentPatient().ID)

		return self.remove_items_safely()

	#--------------------------------------------------------
	def _get_patient_column_value(self, item) -> str:
		return _('current')

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
	# reget-on-paint mixin API
	#--------------------------------------------------------
	def _populate_with_data(self):
		return self.__repopulate_incoming_list()

	#--------------------------------------------------------
	# notebook plugin API
	#--------------------------------------------------------
	def repopulate_ui(self):
		self._populate_with_data()

	#--------------------------------------------------------
	# file drop target API
	#--------------------------------------------------------
	def _drop_target_consume_filenames(self, filenames):
		real_filenames = []
		for pathname in filenames:
			try:
				# dive into folders dropped onto us and extract files (one level deep only)
				files = os.listdir(pathname)
				source = _('directory drop')
				gmDispatcher.send(signal = 'statustext', msg = _('Extracting files from folder [%s] ...') % pathname)
				for filename in files:
					fullname = os.path.join(pathname, filename)
					if not os.path.isfile(fullname):
						continue
					real_filenames.append(fullname)
			except OSError:
				source = _('file drop')
				real_filenames.append(pathname)
		self.__import_files_into_incoming(real_filenames, source)

	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def __init_ui(self):
		self._PhWheel_reviewer.matcher = gmPerson.cMatchProvider_Provider()
		self._PhWheel_doc_type.add_callback_on_lose_focus(self._on_doc_type_loses_focus)
		dt = gmGuiHelpers.cFileDropTarget(target = self)
		self.SetDropTarget(dt)
		self._LCTRL_items.select_callback = self.__on_item_selected
		dt = gmGuiHelpers.cFileDropTarget(on_drop_callback = self._drop_target_consume_filenames)
		self._LCTRL_items.SetDropTarget(dt)
		self.__add_from_button_popup_menu = wx.Menu(title = _('Add documents to incoming area:'))
		item = self.__add_from_button_popup_menu.Append(-1, _('from &scanner/camera'))
		self.Bind(wx.EVT_MENU, self._on_add_from_scanner, item)
		item = self.__add_from_button_popup_menu.Append(-1, _('from &disk'))
		self.Bind(wx.EVT_MENU, self._on_add_from_disk, item)
		item = self.__add_from_button_popup_menu.Append(-1, _('from &clipboard'))
		self.Bind(wx.EVT_MENU, self._on_add_from_clipboard, item)
		self._PNL_patient_search_assign.Show()
		self._PNL_document_properties.Hide()

	#--------------------------------------------------------
	def __register_interests(self):
		gmDispatcher.connect(signal = 'gm_table_mod', receiver = self._on_table_mod)

	#--------------------------------------------------------
	def __repopulate_incoming_list(self):
		pk_pat = None
		if self._CHBOX_filter2active_patient.IsChecked():
			pat = gmPerson.gmCurrentPatient()
			if pat.connected:
				pk_pat = pat.ID

		return self._LCTRL_items.repopulate(pk_patient = pk_pat)

	#--------------------------------------------------------
	def __get_imaging_device_to_use(self, reconfigure=False):
		if not reconfigure:
			device = gmCfgDB.get4workplace (
				option =  'external.xsane.default_device',
				workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
				default = ''
			)
			if device.strip() == '':
				device = None
			if device is not None:
				return device

		try:
			devices = gmScanBackend.get_devices()
		except Exception:
			_log.exception('cannot retrieve list of image sources')
			gmDispatcher.send(signal = 'statustext', msg = _('There is no scanner support installed on this machine.'))
			return None

		if devices is None:
			# get_devices() not implemented for TWAIN yet
			# XSane has its own chooser (so does TWAIN)
			return None

		if len(devices) == 0:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot find an active scanner.'))
			return None

		device = gmListWidgets.get_choices_from_list (
			parent = self,
			msg = _('Select an image capture device'),
			caption = _('device selection'),
			choices = [ '%s (%s)' % (d[2], d[0]) for d in devices ],
			columns = [_('Device')],
			data = devices,
			single_selection = True
		)
		if device is None:
			return None

		# FIXME: add support for actually reconfiguring
		return device[0]

	#--------------------------------------------------------
	def __import_file_into_incoming(self, filename, source='', remove_file:bool=False):
		_log.debug('importing [%s]', filename)
		if gmIncomingData.data_exists(filename):
			_log.debug('exists')
			gmDispatcher.send(signal = 'statustext', msg = _('Data from [%s] already exists in incoming.') % filename, beep = True)
			return True

		incoming = gmIncomingData.create_incoming_data(filename = filename, verify_import = True)
		if not incoming:
			gmDispatcher.send(signal = 'statustext', msg = _('Error importing [%s].') % filename, beep = True)
			return False

		incoming['comment'] = '%s (%s) %s, %s' % (
			gmTools.fname_from_path(filename),
			gmDateTime.pydt_now_here().strftime('%c'),
			source,
			gmTools.fname_dir(filename)
		)
		pat = gmPerson.gmCurrentPatient()
		if pat.connected and self._CHBOX_filter2active_patient.IsChecked():
			print('setting patient')
			incoming.patient = pat
		incoming.save()
		if remove_file:
			gmTools.remove_file(filename)
		return True

	#--------------------------------------------------------
	def __import_files_into_incoming(self, filenames, source='', remove_file:bool=False):
		all_imported = True
		for filename in filenames:
			all_imported = self.__import_file_into_incoming (
				filename,
				source = source,
				remove_file = remove_file
			) and all_imported
		return all_imported

	#--------------------------------------------------------
	# event handlers
	#--------------------------------------------------------
	def _on_table_mod(self, *args, **kwargs):
		if kwargs['table'] != 'clin.incoming_data_unmatched':
			return

		if not self._CHBOX_filter2active_patient.IsChecked():
			self._schedule_data_reget()
			return

		pat = gmPerson.gmCurrentPatient()
		if not pat.connected:
			self._schedule_data_reget()
			return

		print('filter [x]ed, active pat connected:', pat.ID, kwargs['pk_identity'])
		if kwargs['pk_identity'] == pat.ID:
			self._schedule_data_reget()
			return

	#--------------------------------------------------------
	def __on_item_selected(self, event):
		event.Skip()
		item = self._LCTRL_items.selected_item_data
		if not item:
			return

		self._PNL_previews.filename = item.save_to_file()

	#--------------------------------------------------------
	def _on_add_parts_button_pressed(self, event):
		self.PopupMenu(self.__add_from_button_popup_menu, wx.DefaultPosition)

	#--------------------------------------------------------
	def _on_remove_part_button_pressed(self, event):
		event.Skip()
		part = self._LCTRL_items.selected_item_data
		if not part:
			return

		do_delete = gmGuiHelpers.gm_show_question (
			question = _('Irrevocably delete the document from the incoming area ?'),
			title = _('Deleting incoming document')
		)
		if not do_delete:
			return

		gmIncomingData.delete_incoming_data(pk_incoming_data = part['pk_incoming_data_unmatched'])
		self._PNL_previews.filename = None

	#--------------------------------------------------------
	def _on_unassign_patient_button_pressed(self, event):
		event.Skip()
		part = self._LCTRL_items.selected_item_data
		if not part:
			return

		part.patient = None
		part.save()

	#--------------------------------------------------------
	def _on_join_parts_button_pressed(self, event):
		pass
#		items = self.__get_items_to_work_on(_('Select items for PDF.'))
#		if items is None:
#			return
#
#		export_dir = self.__export_as_files (
#			_('Creating PDF from selected items'),
#			base_dir = None,
#			encrypt = False,
#			with_metadata = False,
#			items = items,
#			convert2pdf = False
#		)
#		if export_dir is None:
#			gmDispatcher.send(signal = 'statustext', msg = _('Cannot turn into PDF: aborted or error.'))
#			return
#
#		# unite files in export_dir
#		pdf_pages = gmTools.dir_list_files(directory = export_dir, exclude_subdirs = True)
#		if pdf_pages is None:
#			gmDispatcher.send(signal = 'statustext', msg = _('Cannot turn into PDF: aborted or error.'))
#			return
#
#		pdf_pages.sort()
#		# ask for PDF name ?
#		pdf_name = gmMimeLib.join_files_as_pdf(files = pdf_pages)
#		if pdf_name is None:
#			gmDispatcher.send(signal = 'statustext', msg = _('Cannot turn into PDF: aborted or error.'))
#			return

#		item = gmPerson.gmCurrentPatient().export_area.add_file (
#			filename = pdf_name,
#			hint = _('Document generated from selected items (%s)') % gmDateTime.pydt_now_here().strftime('%Y %b %d  %H:%M')
#		)
#		item.display_via_mime(block = False)
		# hint about showing and ask whether to remove items from export area ?

	#--------------------------------------------------------
	def _on_filter2active_patient_checkbox_toggled(self, event):
		event.Skip()
		if self._CHBOX_filter2active_patient.IsChecked():
			pat = gmPerson.gmCurrentPatient()
			if pat.connected:
				self._PNL_patient_search_assign.Hide()
				self._PNL_document_properties.Show()
				self._LCTRL_items.repopulate(pk_patient = pat.ID)
				self.Parent.Layout()
				return

			gmDispatcher.send(signal = 'statustext', msg = _('No active patient.'))
		self._PNL_patient_search_assign.Show()
		self._PNL_document_properties.Hide()
		self._LCTRL_items.repopulate(pk_patient = None)
		self.Parent.Layout()

	#--------------------------------------------------------
	def _on_assign_selected_patient_button_pressed(self, event):
		event.Skip()
		pat = self._TCTRL_search_patient.patient
		if pat is None:
			return

		for incoming_item in self._LCTRL_items.checked_items_data:
			incoming_item.patient = pat
			incoming_item.save()

	#--------------------------------------------------------
	def _on_assign_active_patient_button_pressed(self, event):
		event.Skip()
		pat = gmPerson.gmCurrentPatient()
		if not pat.connected:
			gmDispatcher.send(signal = 'statustext', msg = _('No active patient.'), beep = False)
			return

		for incoming_item in self._LCTRL_items.checked_items_data:
			incoming_item.patient = pat
			incoming_item.save()

	#--------------------------------------------------------
	def _reviewed_box_checked(self, event):
		event.Skip()
		self._ChBOX_abnormal.Enable(enable = self._ChBOX_reviewed.GetValue())
		self._ChBOX_relevant.Enable(enable = self._ChBOX_reviewed.GetValue())

	#--------------------------------------------------------
	def _on_save_button_pressed(self, event):  # wxGlade: wxgIncomingPluginPnl.<event_handler>
		print("Event handler '_on_save_button_pressed' not implemented!")
		event.Skip()

	#--------------------------------------------------------
	def _on_clear_button_pressed(self, event):
		event.Skip()
		#self.__reset_ui_data()
		self.__reset_property_fields()

	#--------------------------------------------------------
	#--------------------------------------------------------



	#--------------------------------------------------------
	def _on_add_from_scanner(self, evt):
		chosen_device = self.__get_imaging_device_to_use()
		# FIXME: configure whether to use XSane or sane directly
		# FIXME: add support for xsane_device_settings argument
		try:
			fnames = gmScanBackend.acquire_pages_into_files (
				device = chosen_device,
				delay = 5,
				calling_window = self
			)
		except OSError:
			_log.exception('problem acquiring image from source')
			gmGuiHelpers.gm_show_error (
				aMessage = _(
					'No pages could be acquired from the source.\n\n'
					'This may mean the scanner driver is not properly installed.\n\n'
					'On Windows you must install the TWAIN Python module\n'
					'while on Linux and MacOSX it is recommended to install\n'
					'the XSane package.'
				),
				aTitle = _('acquiring page')
			)
			return None

		if len(fnames) == 0:		# no pages scanned
			return True

		self.__import_files_into_incoming(fnames, _('imaging device'), remove_file = True)
		return True

	#--------------------------------------------------------
	def _on_add_from_disk(self, evt):
		dlg = wx.FileDialog (
			parent = None,
			message = _('Choose a file'),
			defaultDir = gmTools.gmPaths().user_work_dir,
			defaultFile = '',
			wildcard = "%s (*)|*|TIFFs (*.tif)|*.tif|JPEGs (*.jpg)|*.jpg|%s (*.*)|*.*" % (_('all files'), _('all files (Win)')),
			style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_MULTIPLE
		)
		result = dlg.ShowModal()
		files = dlg.GetPaths()
		if result == wx.ID_CANCEL:
			dlg.DestroyLater()
			return None

		imported = self.__import_files_into_incoming(files, _('file'))
		if not imported:
			return None

		delete_them = gmGuiHelpers.gm_show_question (
			question = (
				'All files have been imported successfully.\n'
				'\n'
				'Delete external source files ?'
			),
			title = _('Imported files.')
		)
		if not delete_them:
			return True

		for fname in files:
			gmTools.remove_file(fname)
		return True

	#--------------------------------------------------------
	def _on_add_from_clipboard(self, event):
		event.Skip()
		clip_file = gmGuiHelpers.clipboard2file()
		if not clip_file:
			return None

		self.__import_file_into_incoming(clip_file, _('clipboard'), remove_file = True)
		return True

	#--------------------------------------------------------
	def _on_doc_type_loses_focus(self):
		pk_doc_type = self._PhWheel_doc_type.GetData()
		if pk_doc_type is None:
			self._PRW_doc_comment.unset_context(context = 'pk_doc_type')
		else:
			self._PRW_doc_comment.set_context(context = 'pk_doc_type', val = pk_doc_type)
		return True

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
