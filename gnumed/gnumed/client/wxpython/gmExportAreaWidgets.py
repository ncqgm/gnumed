"""GNUmed patient export area widgets."""
#================================================================
__author__ = "Karsten.Hilbert@gmx.net"
__license__ = "GPL v2 or later"

# std lib
import sys
import logging
import os.path
import shutil


# 3rd party
import wx


# GNUmed libs
if __name__ == '__main__':
	sys.path.insert(0, '../../')

from Gnumed.pycommon import gmDispatcher
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmMimeLib
from Gnumed.pycommon import gmDateTime
from Gnumed.pycommon import gmPrinting
from Gnumed.pycommon import gmShellAPI
from Gnumed.pycommon import gmNetworkTools

from Gnumed.business import gmPerson
from Gnumed.business import gmExportArea

from Gnumed.wxpython import gmRegetMixin
from Gnumed.wxpython import gmGuiHelpers
from Gnumed.wxpython import gmDocumentWidgets


_log = logging.getLogger('gm.ui')


#============================================================
from Gnumed.wxGladeWidgets import wxgCreatePatientMediaDlg

class cCreatePatientMediaDlg(wxgCreatePatientMediaDlg.wxgCreatePatientMediaDlg):

	def __init__(self, *args, **kwargs):
		self.__burn2cd = False
		try:
			self.__burn2cd = kwargs['burn2cd']
			del kwargs['burn2cd']
		except KeyError:
			pass
		if self.__burn2cd:
			_log.debug('planning to burn export area items to CD/DVD')
		else:
			_log.debug('planning to save export area items to disk')
		self.__patient = kwargs['patient']
		del kwargs['patient']
		self.__item_count = kwargs['item_count']
		del kwargs['item_count']
		wxgCreatePatientMediaDlg.wxgCreatePatientMediaDlg.__init__(self, *args, **kwargs)

		self.__init_ui()

	#--------------------------------------------------------
	# event handling
	#--------------------------------------------------------
	def _on_select_directory_button_pressed(self, event):
		event.Skip()
		if self.__burn2cd:
			msg = _('Select a directory for inclusion into the patient CD / DVD.')
		else:
			msg = _('Select a directory in which to create the patient media.')
		def_path = self._LBL_directory.Label
		dlg = wx.DirDialog (
			self,
			message = msg,
			defaultPath = def_path
		)
		choice = dlg.ShowModal()
		path = dlg.GetPath()
		dlg.Destroy()
		if choice != wx.ID_OK:
			return
		self._LBL_directory.Label = path
		self.__refresh_dir_is_empty()
		self.__refresh_include_or_remove_existing_data()

	#--------------------------------------------------------
	def _on_use_subdirectory_changed(self, event):
		event.Skip()

		self.__refresh_include_or_remove_existing_data()

		if self._CHBOX_use_subdirectory.IsChecked():
			self._LBL_subdirectory.Label = '%s/%s-###' % (
				self._LBL_directory.Label,
				self.__patient.subdir_name
			)
			return

		self._LBL_subdirectory.Label = ''

	#--------------------------------------------------------
	def _on_save_button_pressed(self, event):
		event.Skip()

		if self.__burn2cd:
			self.EndModal(wx.ID_SAVE)
			return

		if self._CHBOX_use_subdirectory.IsChecked() is True:
			self.EndModal(wx.ID_SAVE)
			return

		path = self._LBL_directory.Label

		if gmTools.dir_is_empty(path) is True:
			self.EndModal(wx.ID_SAVE)
			return

		if self._RBTN_remove_data.Value is True:
			really_remove_existing_data = gmGuiHelpers.gm_show_question (
				title = _('Creating patient media'),
				question = _(
					'Really delete any existing data under\n'
					'\n'
					' [%s]\n'
					'\n'
					'from disk ?\n'
					'\n'
					'(this operation is generally not reversible)'
				) % path
			)
			if really_remove_existing_data is False:
				return

		self.EndModal(wx.ID_SAVE)

	#--------------------------------------------------------
	def _on_browse_directory_button_pressed(self, event):
		event.Skip()
		path = self._LBL_directory.Label.strip()
		if path == '':
			return
		gmMimeLib.call_viewer_on_file(path, block = False)

	#--------------------------------------------------------
	# internal API
	#--------------------------------------------------------
	def __init_ui(self):

		self._LBL_dir_is_empty.Label = ''
		self._LBL_subdirectory.Label = ''

		if self.__burn2cd:
			self._LBL_existing_data.Hide()
			self._BTN_browse_directory.Disable()
			self._RBTN_include_data.Hide()
			self._RBTN_remove_data.Hide()
			self._CHBOX_include_directory.Show()
			self._CHBOX_use_subdirectory.Hide()
			self._LBL_subdirectory.Hide()
			self._CHBOX_generate_metadata.Hide()
			lines = [
				_('Preparing patient media for burning onto CD / DVD'),
				''
			]
			found, external_cmd = gmShellAPI.detect_external_binary('gm-burn_doc')
			if not found:
				lines.append(_('Script <gm-burn_doc(.bat)> not found.'))
				lines.append('')
				lines.append(_('Cannot attempt to burn patient media onto CD/DVD.'))
				self._BTN_save.Disable()
			else:
				lines.append(_('Patient: %s') % self.__patient['description_gender'])
				lines.append('')
				lines.append(_('Number of items to export onto CD/DVD: %s\n') % self.__item_count)
			self._LBL_header.Label = '\n'.join(lines)
			return

		lines = [
			_('Preparing patient media for saving to disk (USB, harddrive).'),
			'',
			_('Patient: %s') % self.__patient['description_gender'],
			'',
			_('Number of items to export to disk: %s\n') % self.__item_count
		]
		self._LBL_header.Label = '\n'.join(lines)
		self._LBL_directory.Label = os.path.join(gmTools.gmPaths().home_dir, 'gnumed')
		self.__refresh_dir_is_empty()

	#--------------------------------------------------------
	def __refresh_dir_is_empty(self):
		path = self._LBL_directory.Label.strip()
		if path == '':
			self._LBL_dir_is_empty.Label = ''
			self._BTN_browse_directory.Disable()
			self._CHBOX_include_directory.Disable()
			return
		is_empty = gmTools.dir_is_empty(directory = path)
		if is_empty is None:
			self._LBL_dir_is_empty.Label = _('(cannot check directory)')
			self._BTN_browse_directory.Disable()
			self._CHBOX_include_directory.Disable()
			return
		if is_empty is True:
			self._LBL_dir_is_empty.Label = _('(directory appears empty)')
			self._BTN_browse_directory.Disable()
			self._CHBOX_include_directory.Disable()
			return

		msg = _('directory already contains data')
		self._BTN_browse_directory.Enable()
		self._CHBOX_include_directory.Enable()

		if os.path.isfile(os.path.join(path, 'DICOMDIR')):
			msg = _('%s\n- DICOM data') % msg

		if os.path.isdir(os.path.join(path, 'documents')):
			if len(os.listdir(os.path.join(path, 'documents'))) > 0:
				msg = _('%s\n- additional documents') % msg

		self._LBL_dir_is_empty.Label = msg
		self.Layout()

	#--------------------------------------------------------
	def __refresh_include_or_remove_existing_data(self):
		if self._CHBOX_use_subdirectory.IsChecked():
			self._RBTN_include_data.Disable()
			self._RBTN_remove_data.Disable()
			return

		path = self._LBL_directory.Label.strip()
		if path == '':
			self._RBTN_include_data.Disable()
			self._RBTN_remove_data.Disable()
			return

		is_empty = gmTools.dir_is_empty(directory = path)
		if is_empty is None:
			self._RBTN_include_data.Disable()
			self._RBTN_remove_data.Disable()
			return

		if is_empty is True:
			self._RBTN_include_data.Disable()
			self._RBTN_remove_data.Disable()
			return

		self._RBTN_include_data.Enable()
		self._RBTN_remove_data.Enable()

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
	def _on_list_item_selected(self, event):
		event.Skip()

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
			defaultDir = os.path.expanduser(os.path.join('~', 'gnumed')),
			style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_MULTIPLE | wx.FD_PREVIEW
		)
		choice = dlg.ShowModal()
		fnames = dlg.GetPaths()
		dlg.Destroy()
		if choice != wx.ID_OK:
			return
		if not gmPerson.gmCurrentPatient().export_area.add_files(fnames):
			gmGuiHelpers.gm_show_error (
				title = _('Adding files to export area'),
				error = _('Cannot add (some of) the following files to the export area:\n%s ') % '\n '.join(fnames)
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
				error = _('Cannot add (some of) the following scans to the export area:\n%s ') % '\n '.join(fnames)
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
			gmExportArea.delete_export_item(pk_export_item = item['pk_export_item'])

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
		printed = gmPrinting.print_files(filenames = files2print, jobtype = jobtype)
		if not printed:
			gmGuiHelpers.gm_show_error (
				aMessage = _('Error printing documents.'),
				aTitle = _('Printing [%s]') % jobtype
			)
			return False

		self.save_soap_note(soap = _('Printed:\n - %s') % '\n - '.join([ i['description'] for i in items ]))
		return True

	#--------------------------------------------------------
	def _on_remote_print_button_pressed(self, event):
		event.Skip()
		items = self._LCTRL_items.get_selected_item_data(only_one = False)
		for item in items:
			item.is_print_job = True

	#--------------------------------------------------------
	def _on_save_items_button_pressed(self, event):
		event.Skip()

		items = self._LCTRL_items.get_selected_item_data(only_one = False)
		if len(items) == 0:
			items = self._LCTRL_items.get_item_data()

		if len(items) == 0:
			return

		pat = gmPerson.gmCurrentPatient()
		dlg = cCreatePatientMediaDlg (self, -1, burn2cd = False, patient = pat, item_count = len(items))
		_log.debug("calling dlg.ShowModal()")
		choice = dlg.ShowModal()
		_log.debug("after returning from dlg.ShowModal()")
		if choice != wx.ID_SAVE:
			dlg.Destroy()
			return

		use_subdir = dlg._CHBOX_use_subdirectory.IsChecked()
		path = dlg._LBL_directory.Label.strip()
		remove_existing_data = dlg._RBTN_remove_data.Value is True
		generate_metadata = dlg._CHBOX_generate_metadata.IsChecked()
		dlg.Destroy()
		if use_subdir:
			path = gmTools.mk_sandbox_dir (
				prefix = '%s-' % pat.subdir_name,
				base_dir = path
			)
		else:
			if remove_existing_data is True:
				if gmTools.rm_dir_content(path) is False:
					gmGuiHelpers.gm_show_error (
						title = _('Creating patient media'),
						error = _('Cannot remove content from\n [%s]') % path
					)
					return False

		exp_area = pat.export_area
		if generate_metadata:
			export_dir = exp_area.export(base_dir = path, items = items)
		else:
			export_dir = exp_area.dump_items_to_disk(base_dir = path, items = items)

		self.save_soap_note(soap = _('Saved to [%s]:\n - %s') % (
			export_dir,
			'\n - '.join([ i['description'] for i in items ])
		))

		msg = _('Saved documents into directory:\n\n %s') % export_dir
		browse_index = gmGuiHelpers.gm_show_question (
			title = _('Creating patient media'),
			question = msg + '\n\n' + _('Browse patient data pack ?'),
			cancel_button = False
		)
		if browse_index:
			if generate_metadata:
				gmNetworkTools.open_url_in_browser(url = 'file://%s' % os.path.join(export_dir, 'index.html'))
			else:
				gmMimeLib.call_viewer_on_file(export_dir, block = False)

		return True

	#--------------------------------------------------------
	def _on_burn_items_button_pressed(self, event):
		event.Skip()

		# anything to do ?
		found, external_cmd = gmShellAPI.detect_external_binary('gm-burn_doc')
		if not found:
			return
		items = self._LCTRL_items.get_selected_item_data(only_one = False)
		if len(items) == 0:
			items = self._LCTRL_items.get_item_data()
		if len(items) == 0:
			return

		pat = gmPerson.gmCurrentPatient()
		dlg = cCreatePatientMediaDlg(self, -1, burn2cd = True, patient = pat, item_count = len(items))
		choice = dlg.ShowModal()
		if choice != wx.ID_SAVE:
			return
		path2include = dlg._LBL_directory.Label.strip()
		include_selected_dir = dlg._CHBOX_include_directory.IsChecked()
		dlg.Destroy()

		# do the export
		base_dir = None
		if include_selected_dir:
			if gmTools.dir_is_empty(path2include) is False:
				base_dir = gmTools.get_unique_filename(suffix = '.iso')
				try:
					shutil.copytree(path2include, base_dir)
				except shutil.Error:
					_log.exception('cannot copy include directory [%s] -> [%s]', path2include, base_dir)
					return

		export_dir = gmPerson.gmCurrentPatient().export_area.export(base_dir = base_dir, items = items)
		if export_dir is None:
			return

		# burn onto media
		cmd = '%s %s' % (external_cmd, export_dir)
		if os.name == 'nt':
			blocking = True
		else:
			blocking = False
		success = gmShellAPI.run_command_in_shell (
			command = cmd,
			blocking = blocking
		)
		if not success:
			gmGuiHelpers.gm_show_error (
				aMessage = _('Error burning documents to CD/DVD.'),
				aTitle = _('Burning documents')
			)
			return

		self.save_soap_note(soap = _('Burned onto CD/DVD:\n - %s') % '\n - '.join([ i['description'] for i in items ]))

		browse_index = gmGuiHelpers.gm_show_question (
			title = _('Creating patient media'),
			question = _('Browse patient data pack ?'),
			cancel_button = False
		)
		if browse_index:
			gmNetworkTools.open_url_in_browser(url = 'file://%s' % os.path.join(export_dir, 'index.html'))

		return True

	#--------------------------------------------------------
	def _on_archive_items_button_pressed(self, event):
		print("Event handler '_on_archive_items_button_pressed' not implemented!")
		event.Skip()

	#--------------------------------------------------------
	def _on_mail_items_button_pressed(self, event):
		event.Skip()

		items = self._LCTRL_items.get_selected_item_data(only_one = False)
		if len(items) == 0:
			return True

		found, external_cmd = gmShellAPI.detect_external_binary('gm-mail_doc')
		if not found:
			return False

		files2mail = []
		for item in items:
			files2mail.append(item.save_to_file())

		cmd = '%s %s' % (external_cmd, ' '.join(files2mail))
		if os.name == 'nt':
			blocking = True
		else:
			blocking = False
		success = gmShellAPI.run_command_in_shell (
			command = cmd,
			blocking = blocking
		)
		if not success:
			gmGuiHelpers.gm_show_error (
				aMessage = _('Error mailing documents.'),
				aTitle = _('Mailing documents')
			)
			return False

		self.save_soap_note(soap = _('Mailed:\n - %s') % '\n - '.join([ i['description'] for i in items ]))
		return True

	#--------------------------------------------------------
	def _on_fax_items_button_pressed(self, event):
		event.Skip()

		items = self._LCTRL_items.get_selected_item_data(only_one = False)
		if len(items) == 0:
			return

		found, external_cmd = gmShellAPI.detect_external_binary('gm-fax_doc')
		if not found:
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

		cmd = '%s "%s" %s' % (external_cmd, fax_number, ' '.join(files2fax))
		if os.name == 'nt':
			blocking = True
		else:
			blocking = False
		success = gmShellAPI.run_command_in_shell (
			command = cmd,
			blocking = blocking
		)
		if not success:
			gmGuiHelpers.gm_show_error (
				aMessage = _('Error faxing documents to\n\n  %s') % fax_number,
				aTitle = _('Faxing documents')
			)
			return False

		self.save_soap_note(soap = _('Faxed to [%s]:\n - %s') % (
			fax_number,
			'\n - '.join([ i['description'] for i in items ])
		))
		return True

	#--------------------------------------------------------
	def repopulate_ui(self):
		self._populate_with_data()

	#--------------------------------------------------------
	# internal API
	#--------------------------------------------------------
	def __init_ui(self):
		self._LCTRL_items.set_columns([_('By'), _('When'), _('Description')])

		self._BTN_archive_items.Disable()

		# there's no GetToolTipText() in wx2.8
		self.__mail_script_exists, path = gmShellAPI.detect_external_binary(binary = r'gm-mail_doc')
		if not self.__mail_script_exists:
			self._BTN_mail_items.Disable()
			tt = self._BTN_mail_items.GetToolTipText() + '\n\n' + _('<gm-mail_doc(.bat) not found>')
			self._BTN_mail_items.SetToolTip(tt)

		self.__fax_script_exists, path = gmShellAPI.detect_external_binary(binary = r'gm-fax_doc')
		if not self.__fax_script_exists:
			self._BTN_fax_items.Disable()
			tt = self._BTN_fax_items.GetToolTipText() + '\n\n' + _('<gm-fax_doc(.bat) not found>')
			self._BTN_fax_items.SetToolTip(tt)

		self.__burn_script_exists, path = gmShellAPI.detect_external_binary(binary = r'gm-burn_doc')
		if not self.__burn_script_exists:
			self._BTN_burn_items.Disable()
			tt = self._BTN_burn_items.GetToolTipText() + '\n\n' + _('<gm-burn_doc(.bat) not found>')
			self._BTN_burn_items.SetToolTip(tt)

		# make me and listctrl file drop targets
		dt = gmGuiHelpers.cFileDropTarget(target = self)
		self.SetDropTarget(dt)
		dt = gmGuiHelpers.cFileDropTarget(on_drop_callback = self._drop_target_consume_filenames)
		self._LCTRL_items.SetDropTarget(dt)

	#--------------------------------------------------------
	def save_soap_note(self, soap=None):
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
		self._LCTRL_items.set_string_items ([
			[	i['created_by'],
				gmDateTime.pydt_strftime(i['created_when'], '%Y %b %d %H:%M'),
				i['description']
			] for i in items
		])
		self._LCTRL_items.set_column_widths([wx.LIST_AUTOSIZE, wx.LIST_AUTOSIZE, wx.LIST_AUTOSIZE])
		self._LCTRL_items.set_data(items)

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
		printed = gmPrinting.print_files(filenames = files2print, jobtype = jobtype)
		if not printed:
			gmGuiHelpers.gm_show_error (
				aMessage = _('Error printing documents.'),
				aTitle = _('Printing [%s]') % jobtype
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
					gmDateTime.pydt_strftime(p['created_when'], '%Y %b %d %H:%M'),
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
