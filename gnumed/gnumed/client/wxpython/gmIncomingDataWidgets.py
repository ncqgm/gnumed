# -*- coding: utf-8 -*-
"""GNUmed incoming data widgets."""
#============================================================
# SPDX-License-Identifier: GPL-2.0-or-later
__author__ = "Karsten.Hilbert@gmx.net"
__license__ = "GPL v2 or later"


import os
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

from Gnumed.pycommon import gmPG2
from Gnumed.pycommon import gmCfgDB
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmHooks
from Gnumed.pycommon import gmMimeLib
from Gnumed.pycommon import gmDateTime
from Gnumed.pycommon import gmDispatcher
from Gnumed.pycommon import gmScanBackend

from Gnumed.business import gmStaff
from Gnumed.business import gmPerson
from Gnumed.business import gmPraxis
from Gnumed.business import gmIncomingData
from Gnumed.business import gmDocuments

from Gnumed.wxpython import gmRegetMixin
from Gnumed.wxpython import gmGuiHelpers
from Gnumed.wxpython import gmListWidgets
from Gnumed.wxpython.gmPatSearchWidgets import set_active_patient


_log = logging.getLogger('gm.auto-in-ui')

#============================================================
class cIncomingDataListCtrl(gmListWidgets.cReportListCtrl):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		if not self.EnableCheckBoxes(enable = True):
			_log.error('cannot enable list item checkboxes')
		self.set_columns(columns = [_('Incoming document'), _('Patient')])
		self.set_column_widths([wx.LIST_AUTOSIZE, wx.LIST_AUTOSIZE])

	#--------------------------------------------------------
	def repopulate(self, pk_patient=None) -> bool:
		list_rows = []
		data = []
		items = gmIncomingData.get_incoming_data()
		if pk_patient:
			items = [ i for i in items if i['pk_identity'] == pk_patient ]
		for i in items:
			if i['comment']:
				comment = i['comment'].strip()
			else:
				comment = '?'
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
		else:
			item = self.selected_item_data
			if not item:
				gmDispatcher.send(signal = 'statustext', msg = _('Nothing selected for external display.'))
				return

			page_fname = item.save_to_file()
			if not page_fname:
				gmDispatcher.send(signal = 'statustext', msg = _('Cannot display document externally.'))
				return

		(success, msg) = gmMimeLib.call_viewer_on_file(page_fname)
		if success:
			return

		gmGuiHelpers.gm_show_warning (
			aMessage = _('Cannot display document:\n%s') % msg,
			aTitle = _('displaying incoming document')
		)

	#--------------------------------------------------------
	def _get_patient_column_value(self, item) -> str:
		if not item['pk_identity']:
			return ''

		return gmPerson.cPatient(item['pk_identity']).description_gender

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

		self._PhWheel_reviewer.matcher = gmPerson.cMatchProvider_Provider()
		self._PhWheel_reviewer.selection_only = True
		self._PhWheel_doc_type.add_callback_on_lose_focus(self._on_doc_type_loses_focus)
		self.__reset_property_fields()
		self._PNL_document_properties.Hide()

		self.__vetoing_prepare_import_button = False

	#--------------------------------------------------------
	def __register_interests(self):
		gmDispatcher.connect(signal = 'gm_table_mod', receiver = self._on_table_mod)
		gmDispatcher.connect(signal = 'post_patient_selection', receiver = self._post_patient_selection)

	#--------------------------------------------------------
	def _post_patient_selection(self):
		self.__repopulate_incoming_list()
		return True

	#--------------------------------------------------------
	def __repopulate_incoming_list(self):
		pk_pat = None
		if self._BTN_prepare_import.Value:
			pat = gmPerson.gmCurrentPatient()
			if pat.connected:
				pk_pat = pat.ID

		self._PNL_previews.filename = None
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
	def __import_file_into_incoming(self, filename, source='', remove_file:bool=False, comment:str=None):
		_log.debug('importing [%s]', filename)
		if gmIncomingData.data_exists(filename):
			_log.debug('exists')
			gmDispatcher.send(signal = 'statustext', msg = _('Data from [%s] already exists in incoming.') % filename, beep = True)
			return True

		incoming = gmIncomingData.create_incoming_data(filename = filename, verify_import = True)
		if not incoming:
			gmDispatcher.send(signal = 'statustext', msg = _('Error importing [%s].') % filename, beep = True)
			return False

		if not comment:
			comment = '%s (%s) %s, %s' % (
				gmTools.fname_from_path(filename),
				gmDateTime.pydt_now_here().strftime('%a %d %b %Y %H:%M'),
				source,
				gmTools.fname_dir(filename)
			)
		incoming['comment'] = comment
		pat = gmPerson.gmCurrentPatient()
		if pat.connected and self._BTN_prepare_import.Value:
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
	def __assign_person_to_items(self, person=None):
		items = self._LCTRL_items.checked_items_data
		if not items:
			item = self._LCTRL_items.selected_item_data
			if item:
				items = [item]
		if not items:
			gmDispatcher.send(signal = 'statustext', msg = _('No items [x] checked or highlighted.'), beep = False)
			return

		if isinstance(person, gmPerson.cPatient):
			patient = person
		else:
			patient = person.as_patient
		for incoming_item in items:
			incoming_item.patient = patient
			incoming_item.save()

	#--------------------------------------------------------
	def __reset_property_fields(self):
		self._PhWheel_episode.SetText(value = _('other documents'), suppress_smarts = True)
		self._PhWheel_doc_type.SetText('')
		fts = gmDateTime.cFuzzyTimestamp()
		self._PhWheel_doc_date.SetText(fts.strftime('%Y-%m-%d'), fts)
		self._PRW_doc_comment.SetText('')
		self._PhWheel_source.SetText('', None)
		self._RBTN_org_is_source.SetValue(1)
		# FIXME: should be set to patient's primary doc
		me = gmStaff.gmCurrentProvider()
		self._PhWheel_reviewer.SetText (
			value = '%s (%s%s %s)' % (me['short_alias'], gmTools.coalesce(me['title'], ''), me['firstnames'], me['lastnames']),
			data = me['pk_staff']
		)
		self._ChBOX_reviewed.SetValue(False)
		self._ChBOX_abnormal.Disable()
		self._ChBOX_abnormal.SetValue(False)
		self._ChBOX_relevant.Disable()
		self._ChBOX_relevant.SetValue(False)

	#--------------------------------------------------------
	def __items_valid_for_save(self):
		checked_items = self._LCTRL_items.checked_items_data
		if checked_items:
			pat = gmPerson.gmCurrentPatient()
			for item in checked_items:
				if item['pk_identity'] != pat.ID:	# should not happen
					gmDispatcher.send(signal = 'statustext', msg = _('Some [x] checked items not associated with active patient.'), beep = True)
					return False

			return True

		selected_item = self._LCTRL_items.selected_item_data
		if selected_item:
			pat = gmPerson.gmCurrentPatient()
			if selected_item['pk_identity'] == pat.ID:
				return True

			# should not happen
			gmDispatcher.send(signal = 'statustext', msg = _('Highlighted item not associated with active patient.'), beep = True)
			return False

		allow_empty = gmCfgDB.get4user (
			option =  'horstspace.scan_index.allow_partless_documents',
			workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
			default = False
		)
		if not allow_empty:
			gmDispatcher.send(signal = 'statustext', msg = _('Nothing [x] checked or highlighted for saving.'), beep = True)
			return False

		save_empty = gmGuiHelpers.gm_show_question (
			aMessage = _('Nothing [x] checked or highlighted for saving.\n\nReally save an empty document as a reference ?'),
			aTitle = _('saving document')
		)
		if not save_empty:
			return False

		return True

	#--------------------------------------------------------
	def __valid_for_save(self):
		if not self.__items_valid_for_save():
			return False

		doc_type_pk = self._PhWheel_doc_type.GetData(can_create = True)
		if doc_type_pk is None:
			self._PhWheel_doc_type.SetFocus()
			gmDispatcher.send(signal = 'statustext', msg = _('No document type selected.'), beep = True)
			return False

		if self._PhWheel_episode.GetValue().strip() == '':
			gmDispatcher.send(signal = 'statustext', msg = _('No episode selected.'), beep = True)
			return False

		if self._PhWheel_reviewer.GetData() is None:
			gmDispatcher.send(signal = 'statustext', msg = _('No reviewer selected.'), beep = True)
			return False

		if self._PhWheel_doc_date.is_valid_timestamp(empty_is_valid = True) is False:
			gmDispatcher.send(signal = 'statustext', msg = _('Invalid date of generation.'), beep = True)
			return False

		return True

	#--------------------------------------------------------
	# event handlers
	#--------------------------------------------------------
	def _on_table_mod(self, *args, **kwargs):
		if kwargs['table'] != 'clin.incoming_data':
			return

		# regardless of whether we filter to the active patient
		# a table change may still be relevant as a document
		# may have become UNassigned
		self._schedule_data_reget()

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
			question = _('Irrevocably delete document from incoming area ?'),
			title = _('Deleting incoming document')
		)
		if not do_delete:
			return

		gmIncomingData.delete_incoming_data(pk_incoming_data = part['pk_incoming_data'])

	#--------------------------------------------------------
	def _on_unassign_patient_button_pressed(self, event):
		event.Skip()
		item = self._LCTRL_items.selected_item_data
		if not item:
			return

		item.patient = None
		item.save()

	#--------------------------------------------------------
	def _on_goto_item_patient_button_pressed(self, event):
		event.Skip()
		item = self._LCTRL_items.selected_item_data
		if not item:
			items = self._LCTRL_items.checked_items_data
			if items:
				item = items[0]
			else:
				gmDispatcher.send(signal = 'statustext', msg = _('No items [x] checked or highlighted.'), beep = False)
				return

		if not item.patient_pk:
			gmDispatcher.send(signal = 'statustext', msg = _('No patient linked to item.'), beep = False)
			return

		set_active_patient(patient = gmPerson.cPatient(item.patient_pk))

	#--------------------------------------------------------
	def _on_prepare_import_button_toggled(self, event):
		event.Skip()
		if self._BTN_prepare_import.Value:
			pat = gmPerson.gmCurrentPatient()
			if pat.connected:
				self.__vetoing_prepare_import_button = False
				self._PNL_previews.filename = None
				self._PNL_patient_search_assign.Hide()
				self._PNL_document_properties.Show()
				self._LCTRL_items.repopulate(pk_patient = pat.ID)
				self._main_splitter.Layout()
				self.Layout()
				self.Parent.Layout()
			else:
				gmDispatcher.send(signal = 'statustext', msg = _('No active patient.'))
				self.__vetoing_prepare_import_button = True
				self._BTN_prepare_import.Value = False
			return

		if self.__vetoing_prepare_import_button:
			self.__vetoing_prepare_import_button = False
			return

		self.__vetoing_prepare_import_button = False
		self._PNL_previews.filename = None
		self._PNL_patient_search_assign.Show()
		self._PNL_document_properties.Hide()
		self._LCTRL_items.repopulate(pk_patient = None)
		self._main_splitter.Layout()
		self.Layout()
		self.Parent.Layout()

	#--------------------------------------------------------
	def _on_assign_selected_patient_button_pressed(self, event):
		event.Skip()
		person = self._TCTRL_search_person.person
		if person is None:
			gmDispatcher.send(signal = 'statustext', msg = _('No patient in search box.'), beep = False)
			return

		self.__assign_person_to_items(person = person)

	#--------------------------------------------------------
	def _on_assign_active_patient_button_pressed(self, event):
		event.Skip()
		pat = gmPerson.gmCurrentPatient()
		if not pat.connected:
			gmDispatcher.send(signal = 'statustext', msg = _('No active patient.'), beep = False)
			return

		self.__assign_person_to_items(person = pat)

	#--------------------------------------------------------
	def _on_goto_searched_patient_button_pressed(self, event):
		event.Skip()
		person = self._TCTRL_search_person.person
		if person is None:
			gmDispatcher.send(signal = 'statustext', msg = _('No patient in search box.'), beep = False)
			return

		set_active_patient(patient = person)

	#--------------------------------------------------------
	def _reviewed_box_checked(self, event):
		event.Skip()
		self._ChBOX_abnormal.Enable(enable = self._ChBOX_reviewed.GetValue())
		self._ChBOX_relevant.Enable(enable = self._ChBOX_reviewed.GetValue())

	#--------------------------------------------------------
	def _on_save_button_pressed(self, event):
		event.Skip()
		if not self.__valid_for_save():
			return False

		pk_document_type = self._PhWheel_doc_type.GetData()
		if pk_document_type is None:
			pk_document_type = gmDocuments.create_document_type(document_type = self._PhWheel_doc_type.GetValue().strip())['pk_doc_type']
		curr_pat = gmPerson.gmCurrentPatient()
		doc_folder = curr_pat.document_folder
		conn = gmPG2.get_connection(readonly = False)
		new_doc = doc_folder.add_document (
			document_type = pk_document_type,
			encounter = curr_pat.emr.active_encounter,
			episode = self._PhWheel_episode.GetData(can_create = True, is_open = True, as_instance = False),
			link_obj = conn
		)
		if new_doc is None:
			return False

		generate_uuid = gmCfgDB.get4user (
			option = 'horstspace.scan_index.generate_doc_uuid',
			workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
			default = False
		)
		if generate_uuid:
			new_doc['ext_ref'] = gmDocuments.get_ext_ref()
		new_doc['pk_org_unit'] = self._PhWheel_source.GetData()
		date = self._PhWheel_doc_date.GetData()
		if date is not None:
			new_doc['clin_when'] = date.get_pydt()
		comment = self._PRW_doc_comment.GetLineText(0).strip()
		if comment:
			new_doc['comment'] = comment
		if self._RBTN_org_is_receiver.Value is True:
			new_doc['unit_is_receiver'] = True
		incoming_data = self._LCTRL_items.checked_items_data
		if not incoming_data:
			incoming_data = [self._LCTRL_items.selected_item_data]
		success, parts = new_doc.add_parts_from_incoming (
			incoming_data = incoming_data,
			pk_reviewer = self._PhWheel_reviewer.GetData(),
			conn = conn
		)
		if not success:
			conn.rollback()
			return False

		new_doc.save(conn = conn)
		conn.commit()
		if self._ChBOX_reviewed.GetValue():
			new_doc.set_reviewed (
				technically_abnormal = self._ChBOX_abnormal.GetValue(),
				clinically_relevant = self._ChBOX_relevant.GetValue()
			)
		self.__reset_property_fields()
		for incoming in incoming_data:
			gmIncomingData.delete_incoming_data(pk_incoming_data = incoming['pk_incoming_data'])
		gmHooks.run_hook_script(hook = 'after_new_doc_created')
		return True

	#--------------------------------------------------------
	def _on_clear_button_pressed(self, event):
		event.Skip()
		self.__reset_property_fields()

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

		imported = self.__import_files_into_incoming(files)
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

		self.__import_file_into_incoming (
			filename = clip_file,
			comment = '%s (%s)' % (
				_('clipboard'),
				gmDateTime.pydt_now_here().strftime('%a %d %b %Y %H:%M')
			),
			remove_file = True
		)
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
	gmLog2.print_logfile_name()
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
