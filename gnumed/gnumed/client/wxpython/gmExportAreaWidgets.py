"""GNUmed patient export area widgets."""
#================================================================
__author__ = "Karsten.Hilbert@gmx.net"
__license__ = "GPL v2 or later"

# std lib
import sys
import logging
import os.path
#codecs


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

from Gnumed.business import gmPerson
from Gnumed.business import gmExportArea

from Gnumed.wxpython import gmRegetMixin
from Gnumed.wxpython import gmGuiHelpers
from Gnumed.wxpython import gmDocumentWidgets


_log = logging.getLogger('gm.ui')

#============================================================
from Gnumed.wxGladeWidgets import wxgExportAreaPluginPnl

class cExportAreaPluginPnl(wxgExportAreaPluginPnl.wxgExportAreaPluginPnl, gmRegetMixin.cRegetOnPaintMixin):
	"""Panel holding a number of widgets. Used as notebook page."""
	def __init__(self, *args, **kwargs):
		wxgExportAreaPluginPnl.wxgExportAreaPluginPnl.__init__(self, *args, **kwargs)
		gmRegetMixin.cRegetOnPaintMixin.__init__(self)
		self.__init_ui()
		self.__register_interests()
	#--------------------------------------------------------
	# event handling
	#--------------------------------------------------------
	def __register_interests(self):
		gmDispatcher.connect(signal = u'pre_patient_selection', receiver = self._on_pre_patient_selection)
#		gmDispatcher.connect(signal = u'post_patient_selection', receiver = self._schedule_data_reget)
		gmDispatcher.connect(signal = u'gm_table_mod', receiver = self._on_table_mod)
	#--------------------------------------------------------
	def _on_pre_patient_selection(self):
		wx.CallAfter(self.__on_pre_patient_selection)
	#--------------------------------------------------------
	def __on_pre_patient_selection(self):
		self._LCTRL_items.set_string_items([])
	#--------------------------------------------------------
	def _on_table_mod(self, *args, **kwargs):
		if kwargs['table'] != 'clin.export_item':
			return
		pat = gmPerson.gmCurrentPatient()
		if not pat.connected:
			return
		# no idea why this does not work:
#		print "patient pk in signal:", kwargs['pk_identity']
#		print "current patient ID:", pat.ID
#		if kwargs['pk_identity'] == pat.ID:
#			print "signal is about current patient"
#			wx.CallAfter(self.__on_table_mod)
		wx.CallAfter(self.__on_table_mod)
	#--------------------------------------------------------
	def __on_table_mod(self):
		self._schedule_data_reget()
	#--------------------------------------------------------
	def _on_list_item_selected(self, event):
		event.Skip()
	#--------------------------------------------------------
	def _on_show_item_button_pressed(self, event):
		event.Skip()
		item = self._LCTRL_items.get_selected_item_data(only_one = True)
		item.display_via_mime(block = False)
	#--------------------------------------------------------
	def _on_add_items_button_pressed(self, event):
		event.Skip()
		dlg = wx.FileDialog (
			parent = self,
			message = _("Select files to add to the export area"),
			defaultDir = os.path.expanduser(os.path.join('~', 'gnumed')),
			#defaultFile = u'timeline.svg',
			#wildcard = u'%s (*.*)|*.*' % _('all files'),
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
				error = _(u'Cannot add (some of) the following files to the export area:\n%s ') % u'\n '.join(fname)
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

		jobtype = u'export_area'
		printed = gmPrinting.print_files(filenames = files2print, jobtype = jobtype)
		if not printed:
			gmGuiHelpers.gm_show_error (
				aMessage = _('Error printing documents.'),
				aTitle = _('Printing [%s]') % jobtype
			)
			return False

#		soap_lines.append(_('Printed: %s') % u', '.join(form_names))
		return True
	#--------------------------------------------------------
	def _on_burn_items_button_pressed(self, event):  # wxGlade: wxgExportAreaPluginPnl.<event_handler>
		print "Event handler '_on_burn_items_button_pressed' not implemented!"
		event.Skip()

	def _on_save_items_button_pressed(self, event):  # wxGlade: wxgExportAreaPluginPnl.<event_handler>
		print "Event handler '_on_save_items_button_pressed' not implemented!"
		event.Skip()

	def _on_archive_items_button_pressed(self, event):  # wxGlade: wxgExportAreaPluginPnl.<event_handler>
		print "Event handler '_on_archive_items_button_pressed' not implemented!"
		event.Skip()
	#--------------------------------------------------------
	def _on_mail_items_button_pressed(self, event):
		event.Skip()

		items = self._LCTRL_items.get_selected_item_data(only_one = False)
		if len(items) == 0:
			return

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

#		soap_lines.append(_('Mailed: %s') % u', '.join(form_names))
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

#		soap_lines.append(_('Faxed to %s: %s') % (fax_number, u', '.join(form_names)))
		return True
#	#--------------------------------------------------------
#	def _on_refresh_button_pressed(self, event):
#		#event.Skip()
#		self._populate_with_data()
#	#--------------------------------------------------------
#	def _on_export_button_pressed(self, event):
#		#event.Skip()
#		dlg = wx.FileDialog (
#			parent = self,
#			message = _("Save timeline as SVG image under..."),
#			defaultDir = os.path.expanduser(os.path.join('~', 'gnumed')),
#			defaultFile = u'timeline.svg',
#			wildcard = u'%s (*.svg)|*.svg' % _('SVG files'),
#			style = wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT
#		)
#		choice = dlg.ShowModal()
#		fname = dlg.GetPath()
#		dlg.Destroy()
#		if choice != wx.ID_OK:
#			return False
#		self._PNL_timeline.export_as_svg(filename = fname)
	#--------------------------------------------------------
	def repopulate_ui(self):
		self._populate_with_data()
	#--------------------------------------------------------
	# internal API
	#--------------------------------------------------------
	def __init_ui(self):
		self._LCTRL_items.set_columns([_('By'), _('When'), _('Description')])

		self._BTN_save_items.Disable()
		self._BTN_archive_items.Disable()

		self.__mail_script_exists, path = gmShellAPI.detect_external_binary(binary = r'gm-mail_doc')
		if not self.__mail_script_exists:
			self._BTN_mail_items.Disable()
			self._BTN_mail_items.SetToolTipString (
				self._BTN_mail_items.GetToolTipString() + u'\n\n' + _('<gm-mail_doc(.bat) not found>')
			)

		self.__fax_script_exists, path = gmShellAPI.detect_external_binary(binary = r'gm-fax_doc')
		if not self.__fax_script_exists:
			self._BTN_fax_items.Disable()
			self._BTN_fax_items.SetToolTipString (
				self._BTN_fax_items.GetToolTipString() + u'\n\n' + _('<gm-fax_doc(.bat) not found>')
			)

		self.__burn_script_exists, path = gmShellAPI.detect_external_binary(binary = r'gm-burn_doc')
		if not self.__burn_script_exists:
			self._BTN_burn_items.Disable()
			self._BTN_burn_items.SetToolTipString (
				self._BTN_burn_items.GetToolTipString() + u'\n\n' + _('<gm-burn_doc(.bat) not found>')
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
