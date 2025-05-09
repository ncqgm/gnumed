"""GNUmed patient export area widgets."""
#================================================================
__author__ = "Karsten.Hilbert@gmx.net"
__license__ = "GPL v2 or later"

# std lib
import sys
import logging
import os.path
import shutil
import platform


# 3rd party
import wx


# GNUmed libs
if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x
from Gnumed.pycommon import gmDispatcher
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmMimeLib
from Gnumed.pycommon import gmDateTime
from Gnumed.pycommon import gmPrinting
from Gnumed.pycommon import gmShellAPI
from Gnumed.pycommon import gmNetworkTools
from Gnumed.pycommon import gmCfgINI
from Gnumed.pycommon import gmLog2

from Gnumed.business import gmPerson
from Gnumed.business import gmExportArea
from Gnumed.business import gmPraxis

from Gnumed.wxpython import gmRegetMixin
from Gnumed.wxpython import gmGuiHelpers
from Gnumed.wxpython import gmDocumentWidgets
from Gnumed.wxpython import gmListWidgets
from Gnumed.wxpython import gmAuthWidgets


_log = logging.getLogger('gm.ui')
_cfg = gmCfgINI.gmCfgData()

#============================================================
def _add_file_to_export_area(**kwargs):
	try:
		del kwargs['signal']
		del kwargs['sender']
	except KeyError:
		pass
	wx.CallAfter(add_file_to_export_area, **kwargs)

def _add_files_to_export_area(**kwargs):
	try:
		del kwargs['signal']
		del kwargs['sender']
	except KeyError:
		pass
	wx.CallAfter(add_files_to_export_area, **kwargs)

#----------------------
def add_file_to_export_area(parent=None, filename=None, hint=None, unlock_patient=False):
	return add_files_to_export_area (
		parent = parent,
		filenames = [filename],
		hint = hint,
		unlock_patient = unlock_patient
	)

#----------------------
def add_files_to_export_area(parent=None, filenames=None, hint=None, unlock_patient=False):
	pat = gmPerson.gmCurrentPatient()
	if not pat.connected:
		gmDispatcher.send(signal = 'statustext', msg = _('Cannot add files to export area. No patient.'), beep = True)
		return False

	wx.BeginBusyCursor()
	if parent is None:
		parent = wx.GetApp().GetTopWindow()
	if not pat.export_area.add_files(filenames = filenames, hint = hint):
		wx.EndBusyCursor()
		gmGuiHelpers.gm_show_error (
			error = _('Cannot import files into export area.'),
			title = _('Export area')
		)
		return False

	wx.EndBusyCursor()
	# remove non-temp files
	tmp_dir = gmTools.gmPaths().tmp_dir
	files2remove = [ f for f in filenames if not f.startswith(tmp_dir) ]
	if len(files2remove) > 0:
		do_delete = gmGuiHelpers.gm_show_question (
			_(	'Successfully imported files into export area.\n'
				'\n'
				'Do you want to delete imported files from the filesystem ?\n'
				'\n'
				' %s'
			) % '\n '.join(files2remove),
			_('Removing files')
		)
		if do_delete:
			for fname in files2remove:
				gmTools.remove_file(fname)
	else:
		gmDispatcher.send(signal = 'statustext', msg = _('Imported files into export area.'), beep = True)
	return True

	#if unlock_patient:
	#	pat.locked = False

#----------------------
gmDispatcher.connect(signal = 'add_file_to_export_area', receiver = _add_file_to_export_area)
gmDispatcher.connect(signal = 'add_files_to_export_area', receiver = _add_files_to_export_area)

#============================================================
def manage_paperwork_passphrases(parent=None, single_selection:bool=True):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

#	#--------------------------------------------------------
#	def edit(document=None):
#		return
#		#return edit_substance(parent = parent, substance = substance, single_entry = (substance is not None))

#	#--------------------------------------------------------
#	def delete(document):
#		return
#		if substance.is_in_use_by_patients:
#			gmDispatcher.send(signal = 'statustext', msg = _('Cannot delete this substance. It is in use.'), beep = True)
#			return False
#
#		return gmMedication.delete_x_substance(substance = substance['pk'])

	#------------------------------------------------------------
	def refresh(lctrl):
		dbo_conn = gmAuthWidgets.get_dbowner_connection(procedure = _('Show list of paperwork passphrases.'))
		if not dbo_conn:
			phrases = []
		else:
			phrases = gmExportArea.get_object_passphrases(link_obj = dbo_conn)
		items = [ [
			p['hash'],
			p['hash_type'],
			str(p['description'])
		] for p in phrases ]
		lctrl.set_string_items(items)
		lctrl.set_data(phrases)

	#--------------------------------------------------------
	def decrypt_passphrase(passphrase_row):
		if not passphrase_row:
			return

		print('saving passphrase', passphrase_row)
		# save to file
		# get master passphrase or trustee public keys
		# decrypt file
		# display decrypted file

	#------------------------------------------------------------
	return gmListWidgets.get_choices_from_list (
		parent = parent,
		caption = _('Paperwork passphrases'),
		columns = [_('Hash'), _('Type'), _('Comment')],
		single_selection = single_selection,
		#new_callback = edit,
		#edit_callback = edit,
		#delete_callback = delete,
		refresh_callback = refresh
		#,left_extra_button = (_('Decrypt'), _('Decrypt selected passphrase.'), decrypt_passphrase)
	)

#============================================================
from Gnumed.wxGladeWidgets import wxgExportAreaExportToMediaDlg

class cExportAreaExportToMediaDlg(wxgExportAreaExportToMediaDlg.wxgExportAreaExportToMediaDlg):

	def __init__(self, *args, **kwargs):
		self.__patient = kwargs['patient']
		del kwargs['patient']
		self.__item_count = kwargs['item_count']
		del kwargs['item_count']
		super().__init__(*args, **kwargs)

		self.__init_ui()

	#--------------------------------------------------------
	# event handling
	#--------------------------------------------------------
	def _on_reload_media_list_button_pressed(self, event):
		event.Skip()
		wx.BeginBusyCursor()
		try:
			self.__update_media_list()
		finally:
			wx.EndBusyCursor()

	#--------------------------------------------------------
	def _on_media_selected(self, event):
		self.__update_ui_state()

	#--------------------------------------------------------
	def _on_media_deselected(self, event):
		self.__update_ui_state()

	#--------------------------------------------------------
	def _on_use_subdirectory_toggled(self, event):
		event.Skip()
		self.__update_ui_state()

	#--------------------------------------------------------
	def _on_open_directory_button_pressed(self, event):
		event.Skip()
		path = self.__calc_path()
		if not os.path.isdir(path):
			return
		gmMimeLib.call_viewer_on_file(path, block = False)

	#--------------------------------------------------------
	def _on_clear_directory_button_pressed(self, event):
		event.Skip()
		path = self.__calc_path()
		if not os.path.isdir(path):
			return

		delete_data = gmGuiHelpers.gm_show_question (
			title = _('Clearing out a directory'),
			question = _(
				'Do you really want to delete all existing data\n'
				'from the following directory ?\n'
				'\n'
				' %s\n'
				'\n'
				'Note, this can NOT be reversed without backups.'
			) % path,
			cancel_button = False
		)
		if delete_data:
			gmTools.rm_dir_content(path)
			self.__update_ui_state()

	#--------------------------------------------------------
	def _on_save2media_button_pressed(self, event):
		event.Skip()

		path = self.__calc_path()
		if path is None:
			return			# no media selected, should not happen
		if path == -2:		# not mounted, should not happen
			return
		if path == -1:		# optical drive
			if self.__burn_script is None:
				return		# no burn script, should not happen

		self.EndModal(wx.ID_SAVE)

	#--------------------------------------------------------
	# internal API
	#--------------------------------------------------------
	def __init_ui(self):
		msg = _(
			'\n'
			'Number of entries to export: %s\n'
			'\n'
			'Patient: %s\n'
			'\n'
			'Select the media to export onto below.\n'
		) % (
			self.__item_count,
			self.__patient.description_gender
		)
		self._LBL_header.Label = msg
		self._LCTRL_removable_media.set_columns([_('Type'), _('Medium'), _('Details')])
		self._LCTRL_removable_media.set_column_widths([wx.LIST_AUTOSIZE, wx.LIST_AUTOSIZE])
		self._LCTRL_removable_media.set_resize_column()
		self._LCTRL_removable_media.select_callback = self._on_media_selected
		self._LCTRL_removable_media.deselect_callback = self._on_media_deselected

		self.__update_media_list()
		self.__update_ui_state()

	#--------------------------------------------------------
	def __calc_path(self):
		media = self._LCTRL_removable_media.get_selected_item_data(only_one = True)
		if media is None:
			return None

		if media['type'] == 'cd':
			return -1

		if media['is_mounted'] is False:
			return -2

		mnt_path = media['mountpoint']
		if self._CHBOX_use_subdirectory.IsChecked():
			return os.path.join(mnt_path, self.__patient.subdir_name)

		return mnt_path

	#--------------------------------------------------------
	def __update_media_list(self):

		self._LCTRL_removable_media.remove_items_safely()
		items = []
		data = []

		found, self.__burn_script = gmShellAPI.detect_external_binary('gm-burn_doc')
		if not found:
			_log.debug('gm-burn_doc(.bat) arguments: "DIRECTORY-TO-BURN-FROM"')
			_log.debug('gm-burn_doc(.bat): call a CD/DVD burning application and pass in DIRECTORY-TO-BURN-FROM')
			_log.debug('gm-burn_doc(.bat): return 0 on success')

		# USB / MMC drives
		removable_partitions = gmTools.enumerate_removable_partitions()
		for key in removable_partitions:
			part = removable_partitions[key]
			if part['is_mounted'] is False:
				continue
			items.append ([
				part['bus'].upper(),
				_('%s (%s %s) - %s free') % (
					part['fs_label'],
					part['vendor'],
					part['model'],
					gmTools.size2str(part['bytes_free'])
				),
				_('%s (%s): %s in %s on %s') % (
					part['mountpoint'],
					gmTools.size2str(part['size_in_bytes']),
					part['fs_type'],
					part['partition'],
					part['device']
				)
			])
			data.append(part)
		for key in removable_partitions:
			part = removable_partitions[key]
			if part['is_mounted'] is True:
				continue
			items.append ([
				part['bus'].upper(),
				'%s (%s %s)' % (
					part['fs_label'],
					part['vendor'],
					part['model']
				),
				_('%s on %s, not mounted') % (
					part['partition'],
					part['device']
				)
			])
			data.append(part)

		# optical drives: CD/DVD/BD
		optical_writers = gmTools.enumerate_optical_writers()
		for cdrw in optical_writers:
			items.append ([
				cdrw['type'].upper(),
				cdrw['model'],
				cdrw['device']
			])
			data.append(cdrw)

		self._LCTRL_removable_media.set_string_items(items)
		self._LCTRL_removable_media.set_data(data)
		self._LCTRL_removable_media.set_column_widths()

		self._BTN_save2media.Disable()

	#--------------------------------------------------------
	def __update_ui_state(self):

		media = self._LCTRL_removable_media.get_selected_item_data(only_one = True)
		if media is None:
			self._BTN_save2media.Disable()
			self._BTN_open_directory.Disable()
			self._BTN_clear_directory.Disable()
			self._CHBOX_encrypt.Disable()
			self._CHBOX_use_subdirectory.Disable()
			self._LBL_directory.Label = ''
			self._LBL_dir_is_empty.Label = ''
			return

		if media['type'] == 'cd':
			self._BTN_open_directory.Disable()
			self._BTN_clear_directory.Disable()
			self._LBL_directory.Label = ''
			if self.__burn_script is None:
				self._BTN_save2media.Disable()
				self._CHBOX_use_subdirectory.Disable()
				self._CHBOX_encrypt.Disable()
				self._LBL_dir_is_empty.Label = _('helper <gm-burn_doc(.bat)> not found')
			else:
				self._BTN_save2media.Enable()
				self._CHBOX_use_subdirectory.Enable()
				self._CHBOX_encrypt.Enable()
				self._LBL_dir_is_empty.Label = ''
			return

		if media['is_mounted'] is False:
			self._BTN_save2media.Disable()
			self._BTN_open_directory.Disable()
			self._BTN_clear_directory.Disable()
			self._CHBOX_use_subdirectory.Disable()
			self._CHBOX_encrypt.Disable()
			self._LBL_directory.Label = ''
			self._LBL_dir_is_empty.Label = _('media not mounted')
			return

		self._BTN_save2media.Enable()
		self._CHBOX_use_subdirectory.Enable()
		self._CHBOX_encrypt.Enable()

		path = self.__calc_path()
		self._LBL_directory.Label = path + os.sep
		is_empty = gmTools.dir_is_empty(directory = path)
		if is_empty is True:
			self._LBL_dir_is_empty.Label = ''
			self._BTN_open_directory.Enable()
			self._BTN_clear_directory.Disable()
		elif is_empty is False:
			self._LBL_dir_is_empty.Label = _('directory contains data')
			self._BTN_open_directory.Enable()
			self._BTN_clear_directory.Enable()
		else:	# we don't know, say, use_subdir and subdir does not yet exist
			self._LBL_dir_is_empty.Label = ''
			self._BTN_open_directory.Disable()
			self._BTN_clear_directory.Disable()

#============================================================
from Gnumed.wxGladeWidgets import wxgExportAreaSaveAsDlg

class cExportAreaSaveAsDlg(wxgExportAreaSaveAsDlg.wxgExportAreaSaveAsDlg):

	def __init__(self, *args, **kwargs):
		self.__patient = kwargs['patient']
		del kwargs['patient']
		self.__item_count = kwargs['item_count']
		del kwargs['item_count']
		super().__init__(*args, **kwargs)

		self.__init_ui()

	#--------------------------------------------------------
	# event handlers
	#--------------------------------------------------------
	def _on_use_subdirectory_toggled(self, event):
		event.Skip()
		self.__update_ui_state()

	#--------------------------------------------------------
	def _on_save_as_encrypted_toggled(self, event):
		event.Skip()
		self.__update_ui_state()

	#--------------------------------------------------------
	def _on_select_directory_button_pressed(self, event):
		event.Skip()
		curr_path = self._LBL_directory.Label.rstrip(os.sep).rstrip('/')
		if not os.path.isdir(curr_path):
			curr_path = gmTools.gmPaths().user_work_dir
		msg = _('Select directory where to save the archive or files.')
		dlg = wx.DirDialog(self, message = msg, defaultPath = curr_path, style = wx.DD_DEFAULT_STYLE)# | wx.DD_DIR_MUST_EXIST)
		choice = dlg.ShowModal()
		selected_path = dlg.GetPath().rstrip(os.sep).rstrip('/')
		dlg.DestroyLater()
		if choice != wx.ID_OK:
			return

		self._LBL_directory.Label = selected_path + os.sep
		self.__update_ui_state()

	#--------------------------------------------------------
	def _on_open_directory_button_pressed(self, event):
		event.Skip()
		path = self._LBL_directory.Label.strip().rstrip(os.sep).rstrip('/')
		if not os.path.isdir(path):
			return
		gmMimeLib.call_viewer_on_file(path, block = False)

	#--------------------------------------------------------
	def _on_clear_directory_button_pressed(self, event):
		event.Skip()
		path = self._LBL_directory.Label.strip().rstrip(os.sep).rstrip('/')
		if not os.path.isdir(path):
			return
		delete_data = gmGuiHelpers.gm_show_question (
			title = _('Clearing out a directory'),
			question = _(
				'Do you really want to delete all existing data\n'
				'from the following directory ?\n'
				'\n'
				' %s\n'
				'\n'
				'Note, this can NOT be reversed without backups.'
			) % path,
			cancel_button = False
		)
		if delete_data:
			gmTools.rm_dir_content(path)
			self.__update_ui_state()

	#--------------------------------------------------------
	def _on_save_archive_button_pressed(self, event):
		event.Skip()
		self.EndModal(wx.ID_SAVE)

	#--------------------------------------------------------
	# internal API
	#--------------------------------------------------------
	def __init_ui(self):
		msg = ('\n' + _('Number of entries to save: %s') + '\n\n' + _('Patient: %s') + '\n') % (
			self.__item_count,
			self.__patient.description_gender
		)
		self._LBL_header.Label = msg
		self._LBL_directory.Label = os.path.join(gmTools.gmPaths().user_work_dir, 'patients', self.__patient.subdir_name) + os.sep
		self.__update_ui_state()

	#--------------------------------------------------------
	def __update_ui_state(self):
		subdir_name = self.__patient.subdir_name
		path = self._LBL_directory.Label.strip().rstrip(os.sep).rstrip('/')
		if self._CHBOX_use_subdirectory.IsChecked():
			# add subdir if needed
			if not path.endswith(subdir_name):
				path = os.path.join(path, subdir_name)
				self._LBL_directory.Label = path + os.sep
		else:
			# remove subdir if there
			if path.endswith(subdir_name):
				path = path[:-len(subdir_name)].rstrip(os.sep).rstrip('/')
				self._LBL_directory.Label = path + os.sep

		if self._CHBOX_encrypt.IsChecked():
			self._CHBOX_convert2pdf.Enable()
		else:
			self._CHBOX_convert2pdf.Disable()

		is_empty = gmTools.dir_is_empty(directory = path)
		if is_empty is True:
			self._LBL_dir_is_empty.Label = ''
			self._BTN_open_directory.Disable()
			self._BTN_clear_directory.Disable()
			self._BTN_save_files.Enable()
			self._BTN_save_archive.Enable()
		elif is_empty is False:
			self._LBL_dir_is_empty.Label = _('directory contains data')
			self._BTN_open_directory.Enable()
			self._BTN_clear_directory.Enable()
			self._BTN_save_files.Disable()
			self._BTN_save_archive.Disable()
		else:	# we don't know, say, use_subdir and subdir does not yet exist
			self._LBL_dir_is_empty.Label = ''
			self._BTN_open_directory.Disable()
			self._BTN_clear_directory.Disable()
			self._BTN_save_files.Enable()
			self._BTN_save_archive.Enable()

		self.Layout()

#============================================================
from Gnumed.wxGladeWidgets import wxgExportAreaPluginPnl

class cExportAreaPluginPnl(wxgExportAreaPluginPnl.wxgExportAreaPluginPnl, gmRegetMixin.cRegetOnPaintMixin):
	"""Panel holding a number of items for further processing.

	Acts on the current patient.

	Used as notebook page."""
	def __init__(self, *args, **kwargs):
		wxgExportAreaPluginPnl.wxgExportAreaPluginPnl.__init__(self, *args, **kwargs)
		gmRegetMixin.cRegetOnPaintMixin.__init__(self)
		self.__init_ui()
		self.__register_interests()

	#--------------------------------------------------------
	# event handling
	#--------------------------------------------------------
	def __register_interests(self):
		gmDispatcher.connect(signal = 'pre_patient_unselection', receiver = self._on_pre_patient_unselection)
#		gmDispatcher.connect(signal = u'post_patient_selection', receiver = self._schedule_data_reget)
		gmDispatcher.connect(signal = 'gm_table_mod', receiver = self._on_table_mod)

	#--------------------------------------------------------
	def _on_pre_patient_unselection(self):
		self._LCTRL_items.set_string_items([])

	#--------------------------------------------------------
	def _on_table_mod(self, *args, **kwargs):
		if kwargs['table'] != 'clin.export_item':
			return
		pat = gmPerson.gmCurrentPatient()
		if not pat.connected:
			return
		if kwargs['pk_identity'] != pat.ID:
			return
		self._schedule_data_reget()

	#--------------------------------------------------------
	def _on_item_up_pressed(self, event):
		event.Skip()
		sort_col_idx, is_ascending = self._LCTRL_items.GetSortState()
		if sort_col_idx != 0:
			gmDispatcher.send(signal = 'statustext', msg = _('Not sorted by list position, cannot move item.'))
			return

		selected = self._LCTRL_items.GetFirstSelected()
		if selected == -1:
			return

		if selected == 0:
			return

		item = self._LCTRL_items.get_item_data(item_idx = selected)
		next_item = self._LCTRL_items.get_item_data(item_idx = selected - 1)
		item['list_position'] = next_item['list_position']
		item.save()

	#--------------------------------------------------------
	def _on_item_down_pressed(self, event):
		event.Skip()
		sort_col_idx, is_ascending = self._LCTRL_items.GetSortState()
		if sort_col_idx != 0:
			gmDispatcher.send(signal = 'statustext', msg = _('Not sorted by list position, cannot move item.'))
			return

		selected = self._LCTRL_items.GetFirstSelected()
		if selected == -1:
			return

		if (selected + 1) == self._LCTRL_items.ItemCount:
			return

		item = self._LCTRL_items.get_item_data(item_idx = selected)
		next_item = self._LCTRL_items.get_item_data(item_idx = selected + 1)
		item['list_position'] = next_item['list_position'] + 1
		item.save()

	#--------------------------------------------------------
	def _on_show_item_button_pressed(self, event):
		event.Skip()
		item = self._LCTRL_items.get_selected_item_data(only_one = True)
		if item is None:
			return
		item.display_via_mime(block = False)

	#--------------------------------------------------------
	def _on_add_items_button_pressed(self, event):
		event.Skip()
		dlg = wx.FileDialog (
			parent = self,
			message = _("Select files to add to the export area"),
			defaultDir = gmTools.gmPaths().user_work_dir,
			style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_MULTIPLE | wx.FD_PREVIEW
		)
		choice = dlg.ShowModal()
		fnames = dlg.GetPaths()
		dlg.DestroyLater()
		if choice != wx.ID_OK:
			return
		if not gmPerson.gmCurrentPatient().export_area.add_files(fnames):
			gmGuiHelpers.gm_show_error (
				title = _('Adding files to export area'),
				error = _('Cannot add (some of) the following files to the export area:\n%s ') % '\n '.join(fnames)
			)

	#--------------------------------------------------------
	def _on_add_directory_button_pressed(self, event):
		event.Skip()
		dlg = wx.DirDialog (
			parent = self,
			message = _("Select directory to add to the export area"),
			defaultPath = gmTools.gmPaths().user_work_dir,
			style = wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST
		)
		choice = dlg.ShowModal()
		path = dlg.GetPath()
		dlg.DestroyLater()
		if choice != wx.ID_OK:
			return
		if not gmPerson.gmCurrentPatient().export_area.add_path(path):
			gmGuiHelpers.gm_show_error (
				title = _('Adding path to export area'),
				error = _('Cannot add the following path to the export area:\n%s ') % path
			)

	#--------------------------------------------------------
	def _on_add_from_archive_button_pressed(self, event):
		event.Skip()
		selected_docs = gmDocumentWidgets.manage_documents (
			parent = self,
			msg = _('Select the documents to be put into the export area:'),
			single_selection = False
		)
		if selected_docs is None:
			return
		gmPerson.gmCurrentPatient().export_area.add_documents(documents = selected_docs)

	#--------------------------------------------------------
	def _on_clipboard_items_button_pressed(self, event):
		event.Skip()
		clip = gmGuiHelpers.clipboard2file(check_for_filename = True)
		if clip is None:
			return
		if clip is False:
			return
		if not gmPerson.gmCurrentPatient().export_area.add_file(filename = clip, hint = _('clipboard')):
			gmGuiHelpers.gm_show_error (
				title = _('Loading clipboard item (saved to file) into export area'),
				error = _('Cannot add the following clip to the export area:\n%s ') % clip
			)

	#--------------------------------------------------------
	def _on_scan_items_button_pressed(self, event):
		event.Skip()
		scans = gmDocumentWidgets.acquire_images_from_capture_device(calling_window = self)
		if scans is None:
			return

		if not gmPerson.gmCurrentPatient().export_area.add_files(scans, _('scan')):
			gmGuiHelpers.gm_show_error (
				title = _('Scanning files into export area'),
				error = _('Cannot add (some of) the following scans to the export area:\n%s ') % '\n '.join(scans)
			)

	#--------------------------------------------------------
	def _on_remove_items_button_pressed(self, event):
		event.Skip()
		items = self._LCTRL_items.get_selected_item_data(only_one = False)
		if len(items) == 0:
			return
		really_delete = gmGuiHelpers.gm_show_question (
			title = _('Deleting document from export area.'),
			question = _('Really remove %s selected document(s)\nfrom the patient export area ?') % len(items)
		)
		if not really_delete:
			return

		for item in items:
			if item.is_DIRENTRY and not item.is_local_DIRENTRY:
				delete_remote = gmGuiHelpers.gm_show_question (
					title = _('Deleting entry from export area.'),
					question = _(
						'Entry points to directory\n'
						'\n'
						' %s\n'
						'\n'
						'on node [%s]\n'
						'(this node: [%s])\n'
						'\n'
						'Remove remote item from the patient export area ?'
					 ) % (item.DIRENTRY_path, item.DIRENTRY_node, platform.node())
				)
				if not delete_remote:
					continue
			gmPerson.gmCurrentPatient().export_area.remove_item(item)

	#--------------------------------------------------------
	def _on_print_items_button_pressed(self, event):
		event.Skip()
		items = self._LCTRL_items.get_selected_item_data(only_one = False)
		if len(items) == 0:
			return

		files2print = []
		for item in items:
			files2print.append(item.save_to_file())

		if len(files2print) == 0:
			return

		jobtype = 'export_area'
		printed = gmPrinting.print_files(filenames = files2print, jobtype = jobtype, verbose = _cfg.get(option = 'debug'))
		if not printed:
			gmGuiHelpers.gm_show_error (
				error = _('Error printing documents.'),
				title = _('Printing [%s]') % jobtype
			)
			return False

		self.__save_soap_note(soap = _('Printed:\n - %s') % '\n - '.join([ i['description'] for i in items ]))
		return True

	#--------------------------------------------------------
	def _on_remote_print_button_pressed(self, event):
		event.Skip()
		items = self._LCTRL_items.get_selected_item_data(only_one = False)
		if len(items) == 0:
			return
		for item in items:
			item.is_print_job = True
		gmDispatcher.send(signal = 'statustext', msg = _('Item(s) moved to Print Center.'))

	#--------------------------------------------------------
	def _on_save_items_button_pressed(self, event):
		event.Skip()

		items = self.__get_items_to_work_on(_('Saving entries'))
		if items is None:
			return

		pat = gmPerson.gmCurrentPatient()
		dlg = cExportAreaSaveAsDlg(self, -1, patient = pat, item_count = len(items))
		choice = dlg.ShowModal()
		path = dlg._LBL_directory.Label
		generate_metadata = dlg._CHBOX_generate_metadata.IsChecked()
		#use_subdir = dlg._CHBOX_use_subdirectory.IsChecked()
		encrypt = dlg._CHBOX_encrypt.IsChecked()
		convert2pdf = dlg._CHBOX_convert2pdf.IsChecked()
		dlg.DestroyLater()
		if choice == wx.ID_CANCEL:
			return

		if choice == wx.ID_SAVE:
			create_archive = True
		elif choice == wx.ID_OK:
			create_archive = False
		else:
			raise Exception('invalid return')

		if create_archive:
			export_dir = path
			zip_file = self.__export_as_zip (
				gmTools.coalesce (
					value2test = encrypt,
					value2return = _('Saving entries as encrypted ZIP archive'),
					return_instead = _('Saving entries as unencrypted ZIP archive')
				),
				items = items,
				encrypt = encrypt
			)
			if zip_file is None:
				gmDispatcher.send(signal = 'statustext', msg = _('Cannot save: aborted or error.'))
				return
			gmTools.mkdir(export_dir)
			final_zip_file = shutil.move(zip_file, export_dir)
			gmDispatcher.send(signal = 'statustext', msg = _('Saved entries into [%s]') % final_zip_file)
			target = final_zip_file
		else:
			export_dir = self.__export_as_files (
				gmTools.coalesce (
					value2test = encrypt,
					value2return = _('Saving entries as encrypted files'),
					return_instead = _('Saving entries as unencrypted files')
				),
				base_dir = path,
				items = items,
				encrypt = encrypt,
				with_metadata = generate_metadata,
				convert2pdf = convert2pdf
			)
			if export_dir is None:
				gmDispatcher.send(signal = 'statustext', msg = _('Cannot save: aborted or error.'))
				return

			gmDispatcher.send(signal = 'statustext', msg = _('Saved entries into [%s]') % export_dir)
			target = export_dir

		self.__save_soap_note(soap = _('Saved from export area to [%s]:\n - %s') % (
			target,
			'\n - '.join([ i['description'] for i in items ])
		))
		self.__browse_patient_data(export_dir)

		# remove_entries ?

		return True

		# cleanup - ask !
		# - files corresponding to DIR/DIR CONTENT entries
		# - entries in export area
#		remove_items = gmGuiHelpers.gm_show_question (
#			title = _('Creating zip archive'),
#			question = _(
#				'Zip archive created as:\n'
#				'\n'
#				' [%s]\n'
#				'\n'
#				'Remove archived entries from export area ?'
#			) % zip_file,
#			cancel_button = False
#		)
#		if remove_items:
#			exp_area.remove_items(items = items)
#		return True

	#--------------------------------------------------------
	def _on_export_items_button_pressed(self, event):
		event.Skip()

		items = self.__get_items_to_work_on(_('Exporting entries'))
		if items is None:
			return

		# export dialog
		pat = gmPerson.gmCurrentPatient()
		dlg = cExportAreaExportToMediaDlg(self, -1, patient = pat, item_count = len(items))
		choice = dlg.ShowModal()
		media = dlg._LCTRL_removable_media.get_selected_item_data(only_one = True)
		use_subdir = dlg._CHBOX_use_subdirectory.IsChecked()
		encrypt = dlg._CHBOX_encrypt.IsChecked()
		dlg.DestroyLater()
		if choice == wx.ID_CANCEL:
			return

		# export the files
		if media['type'] == 'cd':
			base_dir = gmTools.mk_sandbox_dir(prefix = 'iso-')
		else:
			base_dir = media['mountpoint']
		if use_subdir:
			dir2save2 = os.path.join(base_dir, pat.subdir_name)
		else:
			dir2save2 = base_dir
		export_dir = self.__export_as_files (
			gmTools.coalesce(encrypt, _('Exporting encrypted entries'), _('Exporting entries')),
			base_dir = dir2save2,
			items = items,
			encrypt = encrypt,
			with_metadata = True
		)
		if export_dir is None:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot export: aborted or error.'))
			return

		if media['type'] == 'cd':
			if not self.__burn_dir_to_disk(base_dir = base_dir):
				return
			gmDispatcher.send(signal = 'statustext', msg = _('Entries successfully burned to disk.'))
			self.__save_soap_note(soap = _('Burned onto CD/DVD:\n - %s') % '\n - '.join([ i['description'] for i in items ]))
		else:
			gmDispatcher.send(signal = 'statustext', msg = _('Exported entries into [%s]') % export_dir)
			self.__save_soap_note(soap = _('Exported onto removable media:\n - %s') % '\n - '.join([ i['description'] for i in items ]))

		self.__browse_patient_data(dir2save2)

		# remove_entries ?

		return True

	#--------------------------------------------------------
	def _on_pdfjoin_button_pressed(self, event):
		event.Skip()
		self.__join_items_into_pdf()

	#--------------------------------------------------------
	def _on_encrypt_items_button_pressed(self, event):
		event.Skip()
		self.__encrypt_items()

	#--------------------------------------------------------
	def _on_archive_items_button_pressed(self, event):
		print("Event handler '_on_archive_items_button_pressed' not implemented!")
		event.Skip()

	#--------------------------------------------------------
	def _on_mail_items_button_pressed(self, event):
		event.Skip()
		_log.debug('gm-mail_doc(.bat) API: PRAXIS-VCF ZIP-ARCHIVE"')
		_log.debug('gm-mail_doc(.bat) should call an email client and pass in PRAXIS-VCF and ZIP-ARCHIVE as attachments')
		_log.debug('gm-mail_doc(.bat) should return 0 on success')

		found, external_cmd = gmShellAPI.detect_external_binary('gm-mail_doc')
		if not found:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot send e-mail: <gm-mail_doc(.bat)> not found'))
			return False

		zip_file = self.__export_as_zip (
			_('Mailing documents as zip archive'),
			encrypt = True
		)
		if zip_file is None:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot send e-mail: no archive created.'))
			return False

		prax = gmPraxis.gmCurrentPraxisBranch()
		args = [external_cmd, prax.vcf, zip_file]
		success, ret_code, stdout = gmShellAPI.run_process(cmd_line = args, verbose = _cfg.get(option = 'debug'))
		if not success:
			gmGuiHelpers.gm_show_error (
				error = _('Error mailing documents.'),
				title = _('Mailing documents')
			)
			return False

		#self.__save_soap_note(soap = _('Mailed:\n - %s') % '\n - '.join([ i['description'] for i in items ]))
		self.__save_soap_note(soap = _('Mailed export area content.'))
		return True

	#--------------------------------------------------------
	def _on_fax_items_button_pressed(self, event):
		event.Skip()

		found, external_cmd = gmShellAPI.detect_external_binary('gm-fax_doc')
		if not found:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot send fax: <gm-fax_doc(.bat)> not found'))
			return False

		items = self._LCTRL_items.get_selected_item_data(only_one = False)
		if len(items) == 0:
			items = self._LCTRL_items.get_item_data()
			if len(items) == 0:
				gmDispatcher.send(signal = 'statustext', msg = _('Cannot send fax: no items'))
				return None
			if len(items) > 1:
				# ask, might be a lot
				process_all = gmGuiHelpers.gm_show_question (
					title = _('Faxing documents'),
					question = _('You have not selected any entries.\n\nSend fax with all %s entries ?') % len(items),
					cancel_button = False
				)
				if not process_all:
					return None

			return False

		files2fax = []
		for item in items:
			files2fax.append(item.save_to_file())
		fax_number = wx.GetTextFromUser (
			_('Please enter the fax number here !\n\n'
			  'It can be left empty if the external\n'
			  'fax software knows how to get the number.'),
			caption = _('Faxing documents'),
			parent = self,
			centre = True
		)
		if fax_number == '':
			fax_number = 'EMPTY'
		args = [external_cmd, fax_number, ' '.join(files2fax)]
		success, ret_code, stdout = gmShellAPI.run_process(cmd_line = args, verbose = _cfg.get(option = 'debug'))
		if not success:
			gmGuiHelpers.gm_show_error (
				error = _('Error faxing documents to\n\n  %s') % fax_number,
				title = _('Faxing documents')
			)
			return False

		self.__save_soap_note(soap = _('Faxed to [%s]:\n - %s') % (fax_number, '\n - '.join([ i['description'] for i in items ])))
		return True

	#--------------------------------------------------------
	def _get_list_item_identifier(self, idx):
		if idx == -1:
			return None

		if idx >= self._LCTRL_items.ItemCount:
			return None

		data = self._LCTRL_items.get_item_data(item_idx = idx)
		if data is None:
			return None

		return data['pk_export_item']
	#--------------------------------------------------------
	def _get_drag_data(self):
		data = self._LCTRL_items.get_selected_item_data(only_one = True)
		if data is None:
			return None

		if data.is_DIRENTRY:
			return None

		filename = data.save_to_file()
		if filename is None:
			return None

		file_data_obj = wx.FileDataObject()
		file_data_obj.AddFile(filename)
		return file_data_obj

	#--------------------------------------------------------
	def repopulate_ui(self):
		self._populate_with_data()

	#--------------------------------------------------------
	# internal API
	#--------------------------------------------------------
	def __init_ui(self):
		self._LCTRL_items.set_columns(['#', _('By'), _('When'), _('Description')])
		self._LCTRL_items.ItemIdentityCallback = self._get_list_item_identifier
		self._LCTRL_items.dnd_callback = self._get_drag_data

		self._BTN_item_up.Enable()
		self._BTN_item_down.Enable()
		self._BTN_archive_items.Disable()

		self.__mail_script_exists, path = gmShellAPI.detect_external_binary(binary = r'gm-mail_doc')
		if not self.__mail_script_exists:
			_log.debug('gm-mail_doc(.bat) arguments: PRAXIS-VCF ZIP-ARCHIVE"')
			_log.debug('gm-mail_doc(.bat): call an email client and pass in PRAXIS-VCF and ZIP-ARCHIVE as attachments')
			_log.debug('gm-mail_doc(.bat): return 0 on success')
			self._BTN_mail_items.Disable()
			tt = self._BTN_mail_items.GetToolTipText() + '\n\n' + _('<gm-mail_doc(.bat) not found>')
			self._BTN_mail_items.SetToolTip(tt)

		self.__fax_script_exists, path = gmShellAPI.detect_external_binary(binary = r'gm-fax_doc')
		if not self.__fax_script_exists:
			_log.debug('gm-fax_doc(.bat) arguments: "FAXNUMBER-OR-<EMPTY> LIST-OF-FILES-TO-FAX"')
			_log.debug('gm-fax_doc(.bat): call a fax client and pass in FAXNUMBER and LIST-OF-FILES-TO-FAX')
			_log.debug('gm-fax_doc(.bat): return 0 on success')
			_log.debug('gm-fax_doc(.bat): FAXNUMBER is either the receiver number or the string "EMPTY" if unknown number to GNUmed')
			_log.debug('gm-fax_doc(.bat): LIST-OF-FILES-TO-FAX can be of any file type, so may need to be converted to, say, G3 TIFF')
			self._BTN_fax_items.Disable()
			tt = self._BTN_fax_items.GetToolTipText() + '\n\n' + _('<gm-fax_doc(.bat) not found>')
			self._BTN_fax_items.SetToolTip(tt)

		# this is now handled one level down in the UI
#		self.__burn_script_exists, path = gmShellAPI.detect_external_binary(binary = r'gm-burn_doc')
#		if not self.__burn_script_exists:
#			self._BTN_burn_items.Disable()
#			tt = self._BTN_burn_items.GetToolTipText() + '\n\n' + _('<gm-burn_doc(.bat) not found>')
#			self._BTN_burn_items.SetToolTip(tt)

		# make me and listctrl file drop targets
		dt = gmGuiHelpers.cFileDropTarget(target = self)
		self.SetDropTarget(dt)
		dt = gmGuiHelpers.cFileDropTarget(on_drop_callback = self._drop_target_consume_filenames)
		self._LCTRL_items.SetDropTarget(dt)

	#--------------------------------------------------------
	def __save_soap_note(self, soap=None):
		if soap.strip() == '':
			return
		emr = gmPerson.gmCurrentPatient().emr
		epi = emr.add_episode(episode_name = 'administrative', is_open = False)
		emr.add_clin_narrative (
			soap_cat = None,
			note = soap,
			episode = epi
		)

	#--------------------------------------------------------
	def __export_as_files(self, msg_title, base_dir=None, encrypt=False, with_metadata=False, items=None, convert2pdf=False):
		obj_passphrase = None
		master_passphrase = None
		if encrypt:
			obj_passphrase = self.__get_data_password(msg_title)
			if obj_passphrase is None:
				_log.debug('user aborted by not providing the same password twice')
				gmDispatcher.send(signal = 'statustext', msg = _('Password not provided twice. Aborting.'))
				return None

			if not gmExportArea.get_passphrase_trustees_pubkey_files():
				master_passphrase = self.__get_master_passphrase(msg_title)
				if not master_passphrase:
					_log.debug('user aborted by not providing the same master passphrase twice')
					gmDispatcher.send(signal = 'statustext', msg = _('Master passphrase not provided twice. Aborting.'))
					return None

		wx.BeginBusyCursor()
		try:
			exp_area = gmPerson.gmCurrentPatient().export_area
			if with_metadata:
				export_dir = exp_area.export(base_dir = base_dir, items = items, passphrase = obj_passphrase, master_passphrase = master_passphrase)
			else:
				export_dir = exp_area.dump_items_to_disk(base_dir = base_dir, items = items, passphrase = obj_passphrase, convert2pdf = convert2pdf, master_passphrase = master_passphrase)
		finally:
			wx.EndBusyCursor()
		if export_dir is None:
			gmGuiHelpers.gm_show_error (
				error = _('Error exporting entries.'),
				title = msg_title
			)
			return None

		return export_dir

	#--------------------------------------------------------
	def __export_as_zip(self, msg_title, encrypt=True, items=None):
		# get password
		zip_pwd = None
		master_passphrase = None
		if encrypt:
			zip_pwd = self.__get_data_password(msg_title)
			if zip_pwd is None:
				_log.debug('user aborted by not providing the same password twice')
				gmDispatcher.send(signal = 'statustext', msg = _('Password not provided twice. Aborting.'))
				return None

			if not gmExportArea.get_passphrase_trustees_pubkey_files():
				master_passphrase = self.__get_master_passphrase(msg_title)
				if not master_passphrase:
					_log.debug('user aborted by not providing the same master passphrase twice')
					gmDispatcher.send(signal = 'statustext', msg = _('Master passphrase not provided twice. Aborting.'))
					return None

		# create archive
		wx.BeginBusyCursor()
		zip_file = None
		try:
			exp_area = gmPerson.gmCurrentPatient().export_area
			zip_file = exp_area.export_as_zip(passphrase = zip_pwd, items = items, master_passphrase = master_passphrase)
		except Exception:
			_log.exception('cannot create zip file')
		wx.EndBusyCursor()
		if zip_file is None:
			gmGuiHelpers.gm_show_error (
				error = _('Error creating zip file.'),
				title = msg_title
			)
		return zip_file

	#--------------------------------------------------------
	def __get_master_passphrase(self, msg_title:str) -> str:
		msg = _(
			'No public keys available for safekeeping of paperwork passphrases.\n'
			'\n'
			'Enter master passphrase for encryption thereof.\n'
			'\n'
			'(minimum length: 5, trailing blanks will be stripped)'
		)
		q = _(
			'Insufficient passphrase.\n'
			'\n'
			'(minimum length: 5, trailing blanks will be stripped)\n'
			'\n'
			'Enter another passphrase ?'
		)
		while True:
			master_pwd = wx.GetPasswordFromUser(message = msg, caption = msg_title)
			master_pwd = master_pwd.rstrip()
			if len(master_pwd) > 4:				# minimal weakness check
				break
			retry = gmGuiHelpers.gm_show_question(title = msg_title, question = q)
			if not retry:
				return None					# user changed her mind

		gmLog2.add_word2hide(master_pwd)		# confidentiality
		# reget password
		msg = _(
			'Once more enter master passphrase for safekeeping of paperwork passphrases.\n'
			'\n'
			'(this will protect you from typos)\n'
			'\n'
			'Abort by leaving empty.\n'
			'\n'
			'Make sure to safely remember the master passphrase. It is NOT stored in GNUmed at all.'
		)
		err = _(
			'Passphrases do not match.\n'
			'\n'
			'Retry, or abort with an empty passphrase.'
		)
		while True:
			master_pwd4comparison = wx.GetPasswordFromUser(message = msg, caption = msg_title)
			master_pwd4comparison = master_pwd4comparison.rstrip()
			if master_pwd4comparison == '':
				return None					# user changed her mind ...

			if master_pwd == master_pwd4comparison:
				break
			gmGuiHelpers.gm_show_error(error = err, title = msg_title)
		return master_pwd

	#--------------------------------------------------------
	def __get_data_password(self, msg_title:str) -> str:
		msg = _(
			'Enter passphrase to protect the object with.\n'
			'\n'
			'(minimum length: 5, trailing blanks will be stripped)'
		)
		q = _(
			'Insufficient passphrase.\n'
			'\n'
			'(minimum length: 5, trailing blanks will be stripped)\n'
			'\n'
			'Enter another passphrase ?'
		)
		while True:
			obj_passphrase = wx.GetPasswordFromUser(message = msg, caption = msg_title)
			obj_passphrase = obj_passphrase.rstrip()	# minimal weakness check
			if len(obj_passphrase) > 4:
				break
			retry = gmGuiHelpers.gm_show_question(title = msg_title, question = q)
			if not retry:
				return None					# user changed her mind

		gmLog2.add_word2hide(obj_passphrase)		# confidentiality
		# reget password
		msg = _(
			'Once more enter passphrase to protect the object with.\n'
			'\n'
			'(this will protect you from typos)\n'
			'\n'
			'Abort by leaving empty.'
		)
		err = _(
			'Passphrases do not match.\n'
			'\n'
			'Retry, or abort with an empty passphrase.'
		)
		while True:
			obj_passphrase4comparison = wx.GetPasswordFromUser(message = msg, caption = msg_title)
			obj_passphrase4comparison = obj_passphrase4comparison.rstrip()
			if obj_passphrase4comparison == '':
				# user changed her mind ...
				return None

			if obj_passphrase == obj_passphrase4comparison:
				break
			gmGuiHelpers.gm_show_error(error = err, title = msg_title)
		return obj_passphrase

	#--------------------------------------------------------
	def __get_items_to_work_on(self, msg_title):
		items = self._LCTRL_items.get_selected_item_data(only_one = False)
		if len(items) > 0:
			return items

		items = self._LCTRL_items.get_item_data()
		if len(items) == 0:
			gmDispatcher.send(signal = 'statustext', msg = _('Export area empty. Nothing to do.'))
			return None

		if len(items) == 1:
			return items

		process_all = gmGuiHelpers.gm_show_question (
			title = msg_title,
			question = _('You have not selected any entries.\n\nReally use all %s entries ?') % len(items),
			cancel_button = False
		)
		if process_all:
			return items

		return None

	#--------------------------------------------------------
	def __burn_dir_to_disk(self, base_dir):

		_log.debug('gm-burn_doc(.bat) API: "DIRECTORY-TO-BURN-FROM"')

		found, burn_cmd = gmShellAPI.detect_external_binary('gm-burn_doc')
		if not found:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot burn to disk: Helper not found.'))	# should not happen
			return False

		args = [burn_cmd, base_dir]
		wx.BeginBusyCursor()
		try:
			success, ret_code, stdout = gmShellAPI.run_process(cmd_line = args, verbose = _cfg.get(option = 'debug'))
		finally:
			wx.EndBusyCursor()
		if success:
			return True

		gmGuiHelpers.gm_show_error (
			error = _('Error burning documents to CD/DVD.'),
			title = _('Burning documents')
		)
		return False

	#--------------------------------------------------------
	def __encrypt_items(self):
		items = self.__get_items_to_work_on(_('Select items for encryption.'))
		if items is None:
			return

		master_passphrase = None
		obj_passphrase = self.__get_data_password(_('Encrypting items'))
		if obj_passphrase is None:
			_log.debug('user aborted by not providing the same password twice')
			gmDispatcher.send(signal = 'statustext', msg = _('Password not provided twice. Aborting.'))
			return None

			if not gmExportArea.get_passphrase_trustees_pubkey_files():
				master_passphrase = self.__get_master_passphrase(_('Encrypting items'))
				if not master_passphrase:
					_log.debug('user aborted by not providing the same master passphrase twice')
					gmDispatcher.send(signal = 'statustext', msg = _('Master passphrase not provided twice. Aborting.'))
					return None

		wx.BeginBusyCursor()
		converted_item_files = {}
		for item in items:
			if item.is_DIRENTRY:
				_log.error('cannot encrypt DIRENTRY')
				wx.EndBusyCursor()
				return False

			fname = item.save_to_file(passphrase = obj_passphrase, convert2pdf = False)
			if fname is not None:
				converted_item_files[fname] = item
				continue
			fname = item.save_to_file(passphrase = obj_passphrase, convert2pdf = True)
			if fname is not None:
				converted_item_files[fname] = item
				continue
			_log.error('problem encrypting item either directly or when converted to PDF')
			wx.EndBusyCursor()
			return False

		for fname in converted_item_files:
			if item.update_data_from_file(filename = fname, convert_document_part = True):
				gmExportArea.store_passphrase_of_file(filename = fname, passphrase = obj_passphrase, master_passphrase = master_passphrase)
				continue
			_log.error('error updating item data')
			wx.EndBusyCursor()
			return False

		wx.EndBusyCursor()
		return True

	#--------------------------------------------------------
	def __join_items_into_pdf(self):
		items = self.__get_items_to_work_on(_('Select items for PDF.'))
		if items is None:
			return

		export_dir = self.__export_as_files (
			_('Creating PDF from selected items'),
			base_dir = None,
			encrypt = False,
			with_metadata = False,
			items = items,
			convert2pdf = False
		)
		if export_dir is None:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot turn into PDF: aborted or error.'))
			return

		# unite files in export_dir
		pdf_pages = gmTools.dir_list_files(directory = export_dir, exclude_subdirs = True)
		if pdf_pages is None:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot turn into PDF: aborted or error.'))
			return

		pdf_pages.sort()
		# ask for PDF name ?
		pdf_name = gmMimeLib.join_files_as_pdf(files = pdf_pages)
		if pdf_name is None:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot turn into PDF: aborted or error.'))
			return

		item = gmPerson.gmCurrentPatient().export_area.add_file (
			filename = pdf_name,
			hint = _('Document generated from selected items (%s)') % gmDateTime.pydt_now_here().strftime('%Y %b %d  %H:%M')
		)
		item.display_via_mime(block = False)
		# hint about showing and ask whether to remove items from export area ?

	#--------------------------------------------------------
	def __browse_patient_data(self, base_dir):
		msg = _('Documents saved into:\n\n %s') % base_dir
		browse_index = gmGuiHelpers.gm_show_question (
			title = _('Browsing patient data excerpt'),
			question = msg + '\n\n' + _('Browse saved entries ?'),
			cancel_button = False
		)
		if not browse_index:
			return

		if os.path.isfile(os.path.join(base_dir, 'index.html')):
			gmNetworkTools.open_url_in_browser(url = 'file://%s' % os.path.join(base_dir, 'index.html'))
			return

		gmMimeLib.call_viewer_on_file(base_dir, block = False)

	#--------------------------------------------------------
	# file drop target API
	#--------------------------------------------------------
	def _drop_target_consume_filenames(self, filenames):
		pat = gmPerson.gmCurrentPatient()
		if not pat.connected:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot accept new documents. No active patient.'))
			return

		# dive into folders dropped onto us and extract files (one level deep only)
		real_filenames = []
		for pathname in filenames:
			try:
				files = os.listdir(pathname)
				gmDispatcher.send(signal='statustext', msg=_('Extracting files from folder [%s] ...') % pathname)
				for file in files:
					fullname = os.path.join(pathname, file)
					if not os.path.isfile(fullname):
						continue
					real_filenames.append(fullname)
			except OSError:
				real_filenames.append(pathname)

		if not pat.export_area.add_files(real_filenames, hint = _('Drag&Drop')):
			gmGuiHelpers.gm_show_error (
				title = _('Adding files to export area'),
				error = _('Cannot add (some of) the following files to the export area:\n%s ') % '\n '.join(real_filenames)
			)
	#--------------------------------------------------------
	# reget mixin API
	#
	# remember to call
	#	self._schedule_data_reget()
	# whenever you learn of data changes from database
	# listener threads, dispatcher signals etc.
	#--------------------------------------------------------
	def _populate_with_data(self):
		pat = gmPerson.gmCurrentPatient()
		if not pat.connected:
			return True

		items = pat.export_area.items
		self._LCTRL_items.RememberItemSelection()
		self._LCTRL_items.RememberSortState()
		self._LCTRL_items.set_string_items ([
			[	i['list_position'],
				i['created_by'],
				i['created_when'].strftime('%Y %b %d %H:%M'),
				i['description']
			] for i in items
		])
		self._LCTRL_items.set_column_widths([wx.LIST_AUTOSIZE, wx.LIST_AUTOSIZE, wx.LIST_AUTOSIZE])
		self._LCTRL_items.set_data(items)
		self._LCTRL_items.RestoreItemSelection()
		self._LCTRL_items.RestoreSortState()
		self._LCTRL_items.SetFocus()
		return True

#============================================================
from Gnumed.wxGladeWidgets import wxgPrintMgrPluginPnl

class cPrintMgrPluginPnl(wxgPrintMgrPluginPnl.wxgPrintMgrPluginPnl, gmRegetMixin.cRegetOnPaintMixin):
	"""Panel holding print jobs.

	Used as notebook page."""

	def __init__(self, *args, **kwargs):
		wxgPrintMgrPluginPnl.wxgPrintMgrPluginPnl.__init__(self, *args, **kwargs)
		gmRegetMixin.cRegetOnPaintMixin.__init__(self)
		self.__init_ui()
		self.__register_interests()
	#--------------------------------------------------------
	# event handling
	#--------------------------------------------------------
	def __register_interests(self):
		gmDispatcher.connect(signal = 'pre_patient_unselection', receiver = self._on_pre_patient_unselection)
		gmDispatcher.connect(signal = 'post_patient_selection', receiver = self._on_post_patient_selection)
		gmDispatcher.connect(signal = 'gm_table_mod', receiver = self._on_table_mod)
	#--------------------------------------------------------
	def _on_pre_patient_unselection(self):
		self._RBTN_active_patient_only.Enable(False)
		self._RBTN_all_patients.Value = True
		self._BTN_export_printouts.Enable(False)
	#--------------------------------------------------------
	def _on_post_patient_selection(self):
		self._RBTN_active_patient_only.Enable(True)
		self._BTN_export_printouts.Enable(True)
	#--------------------------------------------------------
	def _on_table_mod(self, *args, **kwargs):
		if kwargs['table'] != 'clin.export_item':
			return
		if self._RBTN_all_patients.Value is True:
			self._schedule_data_reget()
			return
		pat = gmPerson.gmCurrentPatient()
		if not pat.connected:
			return
		if kwargs['pk_identity'] != pat.ID:
			return
		self._schedule_data_reget()
	#--------------------------------------------------------
	def _on_all_patients_selected(self, event):
		event.Skip()
		self._schedule_data_reget()
	#--------------------------------------------------------
	def _on_active_patient_only_selected(self, event):
		event.Skip()
		self._schedule_data_reget()
	#--------------------------------------------------------
	def _on_view_button_pressed(self, event):
		event.Skip()
		printout = self._LCTRL_printouts.get_selected_item_data(only_one = True)
		if printout is None:
			return
		printout.display_via_mime(block = False)
	#--------------------------------------------------------
	def _on_print_button_pressed(self, event):
		event.Skip()
		printouts = self._LCTRL_printouts.get_selected_item_data(only_one = False)
		if len(printouts) == 0:
			return

		files2print = []
		for printout in printouts:
			files2print.append(printout.save_to_file())

		if len(files2print) == 0:
			return

		jobtype = 'print_manager'
		printed = gmPrinting.print_files(filenames = files2print, jobtype = jobtype, verbose = _cfg.get(option = 'debug'))
		if not printed:
			gmGuiHelpers.gm_show_error (
				error = _('Error printing documents.'),
				title = _('Printing [%s]') % jobtype
			)
			return False

		return True
	#--------------------------------------------------------
	def _on_export_button_pressed(self, event):
		event.Skip()
		pat = gmPerson.gmCurrentPatient()
		if not pat.connected:
			return
		printouts = self._LCTRL_printouts.get_selected_item_data(only_one = False)
		for printout in printouts:
			printout.is_print_job = False
	#--------------------------------------------------------
	def _on_delete_button_pressed(self, event):
		event.Skip()
		printouts = self._LCTRL_printouts.get_selected_item_data(only_one = False)
		if len(printouts) == 0:
			return
		if len(printouts) > 1:
			really_delete = gmGuiHelpers.gm_show_question (
				title = _('Deleting document from export area.'),
				question = _('Really remove %s selected document(s)\nfrom the patient export area ?') % len(printouts)
			)
			if not really_delete:
				return
		for printout in printouts:
			gmExportArea.delete_export_item(pk_export_item = printout['pk_export_item'])

	#--------------------------------------------------------
	# internal API
	#--------------------------------------------------------
	def __init_ui(self):
		self._BTN_export_printouts.Enable(False)

	#--------------------------------------------------------
	# reget mixin API
	#--------------------------------------------------------
	def _populate_with_data(self):
		if self._RBTN_all_patients.Value is True:
			columns = [_('Patient'), _('Provider'), _('Description')]
			printouts = gmExportArea.get_print_jobs(order_by = 'pk_identity, description')
			items = [[
				'%s, %s (%s)' % (
					p['lastnames'],
					p['firstnames'],
					p['gender']
				),
				p['created_by'],
				p['description']
			] for p in printouts ]
		else:
			pat = gmPerson.gmCurrentPatient()
			if pat.connected:
				columns = [_('Provider'), _('Created'), _('Description')]
				printouts = pat.export_area.get_printouts(order_by = 'created_when, description')
				items = [[
					p['created_by'],
					p['created_when'].strftime('%Y %b %d %H:%M'),
					p['description']
				] for p in printouts ]
			else:
				columns = [_('Patient'), _('Provider'), _('Description')]
				printouts = gmExportArea.get_print_jobs(order_by = 'pk_identity, description')
				items = [[
					'%s, %s (%s)' % (
						p['lastnames'],
						p['firstnames'],
						p['gender']
					),
					p['created_by'],
					p['description']
				] for p in printouts ]
		self._LCTRL_printouts.set_columns(columns)
		self._LCTRL_printouts.set_string_items(items)
		self._LCTRL_printouts.set_column_widths([wx.LIST_AUTOSIZE, wx.LIST_AUTOSIZE, wx.LIST_AUTOSIZE])
		self._LCTRL_printouts.set_data(printouts)
		self._LCTRL_printouts.SetFocus()
		return True
