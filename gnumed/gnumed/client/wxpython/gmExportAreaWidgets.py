"""GNUmed patient export area widgets."""
#================================================================
__author__ = "Karsten.Hilbert@gmx.net"
__license__ = "GPL v2 or later"

# std lib
import sys
import logging
import os.path


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
		gmDispatcher.connect(signal = u'pre_patient_unselection', receiver = self._on_pre_patient_unselection)
#		gmDispatcher.connect(signal = u'post_patient_selection', receiver = self._schedule_data_reget)
		gmDispatcher.connect(signal = u'gm_table_mod', receiver = self._on_table_mod)
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
				title = _(u'Adding files to export area'),
				error = _(u'Cannot add (some of) the following files to the export area:\n%s ') % u'\n '.join(fnames)
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
				title = _(u'Loading clipboard item (saved to file) into export area'),
				error = _(u'Cannot add the following clip to the export area:\n%s ') % clip
			)

	#--------------------------------------------------------
	def _on_scan_items_button_pressed(self, event):
		event.Skip()
		scans = gmDocumentWidgets.acquire_images_from_capture_device(calling_window = self)
		if scans is None:
			return

		if not gmPerson.gmCurrentPatient().export_area.add_files(scans, _('scan')):
			gmGuiHelpers.gm_show_error (
				title = _(u'Scanning files into export area'),
				error = _(u'Cannot add (some of) the following scans to the export area:\n%s ') % u'\n '.join(fnames)
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
			files2print.append(item.export_to_file())

		if len(files2print) == 0:
			return

		jobtype = u'export_area'
		printed = gmPrinting.print_files(filenames = files2print, jobtype = jobtype)
		if not printed:
			gmGuiHelpers.gm_show_error (
				aMessage = _('Error printing documents.'),
				aTitle = _('Printing [%s]') % jobtype
			)
			return False

		self.save_soap_note(soap = _('Printed:\n - %s') % u'\n - '.join([ i['description'] for i in items ]))
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

		dlg = wx.DirDialog (
			self,
			message = _('Select the directory into which to export the documents.'),
			defaultPath = os.path.join(gmTools.gmPaths().home_dir, 'gnumed')
		)
		choice = dlg.ShowModal()
		path = dlg.GetPath()
		if choice != wx.ID_OK:
			return True

		if not gmTools.dir_is_empty(path):
			reuse_nonempty_dir = gmGuiHelpers.gm_show_question (
				title = _(u'Saving export area documents'),
				question = _(
					u'The chosen export directory\n'
					u'\n'
					u' [%s]\n'
					u'\n'
					u'already contains files. Do you still want to save the\n'
					u'selected export area documents into that directory ?\n'
					u'\n'
					u'(this is useful for including the external documents\n'
					u' already stored in or below this directory)\n'
					u'\n'
					u'[NO] will create a subdirectory for you and use that.'
				) % path,
				cancel_button = True
			)
			if reuse_nonempty_dir is None:
				return True
			if reuse_nonempty_dir is False:
				path = gmTools.mk_sandbox_dir (
					prefix = u'export-%s-' % gmPerson.gmCurrentPatient().dirname,
					base_dir = path
				)

		include_metadata = gmGuiHelpers.gm_show_question (
			title = _(u'Saving export area documents'),
			question = _(
				u'Create descriptive metadata files\n'
				u'and save them alongside the\n'
				u'selected export area documents ?'
			),
			cancel_button = True
		)
		if include_metadata is None:
			return True

		export_dir = gmPerson.gmCurrentPatient().export_area.export(base_dir = path, items = items, with_metadata = include_metadata)

		self.save_soap_note(soap = _('Saved to [%s]:\n - %s') % (
			export_dir,
			u'\n - '.join([ i['description'] for i in items ])
		))

		title = _('Saving export area documents')
		msg = _('Saved documents into directory:\n\n %s') % export_dir
		if include_metadata:
			browse_index = gmGuiHelpers.gm_show_question (
				title = title,
				question = msg + u'\n\n' + _('Browse patient data pack ?'),
				cancel_button = False
			)
			if browse_index:
				gmNetworkTools.open_url_in_browser(url = u'file://%s' % os.path.join(export_dir, u'index.html'))
		else:
			gmGuiHelpers.gm_show_info(title = title, info = msg)

		return True

	#--------------------------------------------------------
	def _on_burn_items_button_pressed(self, event):
		event.Skip()

		found, external_cmd = gmShellAPI.detect_external_binary('gm-burn_doc')
		if not found:
			return False

		items = self._LCTRL_items.get_selected_item_data(only_one = False)
		if len(items) == 0:
			items = self._LCTRL_items.get_item_data()

		base_dir = None
		dlg = wx.DirDialog (
			self,
			message = _('If you wish to include an existing directory select it here:'),
			defaultPath = os.path.join(gmTools.gmPaths().home_dir, 'gnumed'),
			style = wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST
		)
		choice = dlg.ShowModal()
		path2include = dlg.GetPath()
		if choice == wx.ID_OK:
			if not gmTools.dir_is_empty(path2include):
				base_dir = path2include

		export_dir = gmPerson.gmCurrentPatient().export_area.export(base_dir = base_dir, items = items, with_metadata = True)
		if export_dir is None:
			return False

		cmd = u'%s %s' % (external_cmd, export_dir)
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
			return False

		self.save_soap_note(soap = _('Burned onto CD/DVD:\n - %s') % u'\n - '.join([ i['description'] for i in items ]))

		browse_index = gmGuiHelpers.gm_show_question (
			title = title,
			question = _('Browse patient data pack ?'),
			cancel_button = False
		)
		if browse_index:
			gmNetworkTools.open_url_in_browser(url = u'file://%s' % os.path.join(export_dir, u'index.html'))

		return True

	#--------------------------------------------------------
	def _on_archive_items_button_pressed(self, event):
		print "Event handler '_on_archive_items_button_pressed' not implemented!"
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
			files2mail.append(item.export_to_file())

		cmd = u'%s %s' % (external_cmd, u' '.join(files2mail))
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

		self.save_soap_note(soap = _('Mailed:\n - %s') % u'\n - '.join([ i['description'] for i in items ]))
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
			files2fax.append(item.export_to_file())

		fax_number = wx.GetTextFromUser (
			_('Please enter the fax number here !\n\n'
			  'It can be left empty if the external\n'
			  'fax software knows how to get the number.'),
			caption = _('Faxing documents'),
			parent = self,
			centre = True
		)

		cmd = u'%s "%s" %s' % (external_cmd, fax_number, u' '.join(files2fax))
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
			u'\n - '.join([ i['description'] for i in items ])
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

		# there's no GetToolTipString() in wx2.8
		self.__mail_script_exists, path = gmShellAPI.detect_external_binary(binary = r'gm-mail_doc')
		if not self.__mail_script_exists:
			self._BTN_mail_items.Disable()
			try:
				tt = self._BTN_mail_items.GetToolTipString() + u'\n\n' + _('<gm-mail_doc(.bat) not found>')
			except AttributeError:
				tt = _('<gm-mail_doc(.bat) not found>')
			self._BTN_mail_items.SetToolTipString(tt)

		self.__fax_script_exists, path = gmShellAPI.detect_external_binary(binary = r'gm-fax_doc')
		if not self.__fax_script_exists:
			self._BTN_fax_items.Disable()
			try:
				tt = self._BTN_fax_items.GetToolTipString() + u'\n\n' + _('<gm-fax_doc(.bat) not found>')
			except AttributeError:
				tt = _('<gm-fax_doc(.bat) not found>')
			self._BTN_fax_items.SetToolTipString(tt)

		self.__burn_script_exists, path = gmShellAPI.detect_external_binary(binary = r'gm-burn_doc')
		if not self.__burn_script_exists:
			self._BTN_burn_items.Disable()
			try:
				tt = self._BTN_burn_items.GetToolTipString() + u'\n\n' + _('<gm-burn_doc(.bat) not found>')
			except AttributeError:
				tt = _('<gm-burn_doc(.bat) not found>')
			self._BTN_burn_items.SetToolTipString(tt)

		# make me and listctrl a file drop target
		dt = gmGuiHelpers.cFileDropTarget(self)
		self.SetDropTarget(dt)
		dt = gmGuiHelpers.cFileDropTarget(self._LCTRL_items)
		self._LCTRL_items.SetDropTarget(dt)
		self._LCTRL_items.add_filenames = self.add_filenames_to_listctrl

	#--------------------------------------------------------
	def save_soap_note(self, soap=None):
		if soap.strip() == u'':
			return
		emr = gmPerson.gmCurrentPatient().emr
		epi = emr.add_episode(episode_name = u'administrative', is_open = False)
		emr.add_clin_narrative (
			soap_cat = None,
			note = soap,
			episode = epi
		)

	#--------------------------------------------------------
	# file drop target API
	#--------------------------------------------------------
	def add_filenames_to_listctrl(self, filenames):
		self.add_filenames(filenames = filenames)
	#--------------------------------------------------------
	def add_filenames(self, filenames):
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

		if not pat.export_area.add_files(real_filenames, hint = _(u'Drag&Drop')):
			gmGuiHelpers.gm_show_error (
				title = _(u'Adding files to export area'),
				error = _(u'Cannot add (some of) the following files to the export area:\n%s ') % u'\n '.join(real_filenames)
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
		gmDispatcher.connect(signal = u'pre_patient_unselection', receiver = self._on_pre_patient_unselection)
		gmDispatcher.connect(signal = u'post_patient_selection', receiver = self._on_post_patient_selection)
		gmDispatcher.connect(signal = u'gm_table_mod', receiver = self._on_table_mod)
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
			files2print.append(printout.export_to_file())

		if len(files2print) == 0:
			return

		jobtype = u'print_manager'
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
			printouts = gmExportArea.get_print_jobs(order_by = u'pk_identity, description')
			items = [[
				u'%s, %s (%s)' % (
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
				printouts = pat.export_area.get_printouts(order_by = u'created_when, description')
				items = [[
					p['created_by'],
					gmDateTime.pydt_strftime(p['created_when'], '%Y %b %d %H:%M'),
					p['description']
				] for p in printouts ]
			else:
				columns = [_('Patient'), _('Provider'), _('Description')]
				printouts = gmExportArea.get_print_jobs(order_by = u'pk_identity, description')
				items = [[
					u'%s, %s (%s)' % (
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
