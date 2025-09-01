"""GNUmed form/letter handling widgets."""

#================================================================
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL v2 or later"


import os
import os.path
import sys
import logging
import shutil


import wx

# setup translation
if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x
else:
	try:
		_
	except NameError:
		from Gnumed.pycommon import gmI18N
		gmI18N.activate_locale()
		gmI18N.install_domain()
from Gnumed.pycommon import gmI18N
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmDispatcher
from Gnumed.pycommon import gmPrinting
from Gnumed.pycommon import gmDateTime
from Gnumed.pycommon import gmMimeLib
from Gnumed.pycommon import gmCfgINI
from Gnumed.pycommon import gmShellAPI

from Gnumed.business import gmForms
from Gnumed.business import gmPerson
from Gnumed.business import gmStaff
from Gnumed.business import gmExternalCare
from Gnumed.business import gmPraxis

from Gnumed.wxpython import gmGuiHelpers
from Gnumed.wxpython import gmListWidgets
from Gnumed.wxpython import gmMacro
from Gnumed.wxpython import gmEditArea
from Gnumed.wxpython.gmDocumentWidgets import save_files_as_new_document


_log = logging.getLogger('gm.ui')
_cfg = gmCfgINI.gmCfgData()


_ID_FORM_DISPOSAL_PRINT, \
_ID_FORM_DISPOSAL_REMOTE_PRINT, \
_ID_FORM_DISPOSAL_EXPORT_ONLY, \
_ID_FORM_DISPOSAL_ARCHIVE_ONLY = range(4)

#============================================================
# generic form generation and handling convenience functions
#------------------------------------------------------------
__ODT_FILE_PREAMBLE = _("""GNUmed generic document template

Some context data has been added below for your copy/paste convenience.

Before entering text you should switch the "paragraph type"
from "Pre-formatted Text" to "Standard".
""")
__ODT_FILE_PREAMBLE += '============================================================================='

def print_generic_document(parent=None, jobtype:str=None, episode=None):
	"""Call LibreOffice Writer with a generated (fake) ODT file.

	Once Writer is closed, the ODT is imported if different from its initial content.

	Note:
		The file passed to LO _must_ reside in a directory the parents of
		which are all R-X by the user or else LO will throw up its arms
		in despair and fall back to the user's home dir upon saving.

		So,

			/tmp/user/$UID/some-file.odt

		will *not* work (because .../user/... is "drwx--x--x root.root") while

			/home/$USER/some/dir/some-file.odt

		will do fine.
	"""
	sandbox = os.path.join(gmTools.gmPaths().user_tmp_dir, 'libreoffice')
	gmTools.mkdir(sandbox)
	fpath = gmTools.get_unique_filename(suffix = '.txt', tmp_dir = sandbox)
	doc_file = open(fpath, mode = 'wt')
	doc_file.write(__ODT_FILE_PREAMBLE)
	doc_file.write(_('Today: %s') % gmDateTime.pydt_now_here().strftime('%c'))
	doc_file.write('\n\n')
	prax = gmPraxis.gmCurrentPraxisBranch()
	doc_file.write('Praxis:\n')
	doc_file.write(prax.format())
	doc_file.write('\n')
	doc_file.write('Praxis branch:\n')
	doc_file.write('\n'.join(prax.org_unit.format (
		with_address = True,
		with_org = True,
		with_comms = True
	)))
	doc_file.write('\n\n')
	pat = gmPerson.gmCurrentPatient(gmPerson.cPatient(12))
	if pat.connected:
		doc_file.write('Patient:\n')
		doc_file.write(pat.get_description_gender())
		doc_file.write('\n\n')
		for adr in pat.get_addresses():
			doc_file.write(adr.format(single_line = False, verbose = True, show_type = True))
		doc_file.write('\n\n')
		for chan in pat.get_comm_channels():
			doc_file.write(chan.format())
		doc_file.write('\n\n')
	doc_file.write('Provider:\n')
	doc_file.write('\n'.join(gmStaff.gmCurrentProvider().get_staff().format()))
	doc_file.write('\n\n-----------------------------------------------------------------------------\n\n')
	doc_file.close()

	# convert txt -> odt
	success, ret_code, stdout = gmShellAPI.run_process (
		cmd_line = [
			'lowriter',
			'--convert-to', 'odt',
			'--outdir', os.path.split(fpath)[0],
			fpath
		],
		verbose = True
	)
	if success:
		fpath = gmTools.fname_stem_with_path(fpath) + '.odt'
	else:
		_log.warning('cannot convert .txt to .odt')
	md5_before = gmTools.file2md5(fpath)
	gmShellAPI.run_process(cmd_line = ['lowriter', fpath], verbose = True)
	md5_after = gmTools.file2md5(fpath)
	if md5_before == md5_after:
		gmDispatcher.send(signal = 'statustext', msg = _('Document not modified. Discarding.'), beep = False)
		return

	if not pat.connected:
		shutil.move(fpath, gmTools.gmPaths().user_work_dir)
		gmDispatcher.send(signal = 'statustext', msg = _('No patient. Moved file into %s') % gmTools.gmPaths().user_work_dir, beep = False)
		return

	pat.export_area.add_file (
		filename = fpath,
		hint = _('Generic letter, written at %s') % gmDateTime.pydt_now_here().strftime('%Y %b %d  %H:%M')
	)
	gmDispatcher.send(signal = 'display_widget', name = 'gmExportAreaPlugin')

#------------------------------------------------------------
def print_doc_from_template(parent=None, jobtype=None, episode=None, edit_form=None):

	form = generate_form_from_template (
		parent = parent,
		excluded_template_types = [
			'gnuplot script',
			'visual progress note',
			'invoice'
		],
		edit = edit_form			# default None = respect template setting
	)
	if form is None:
		return False

	if form in [True, False]:	# returned by special OOo/LO handling
		return form

	if episode is None:
		epi_name = 'administrative'
	else:
		epi_name = episode['description']
	return act_on_generated_forms (
		parent = parent,
		forms = [form],
		jobtype = jobtype,
		episode_name = epi_name,
		review_copy_as_normal = True
	)

#------------------------------------------------------------
# eventually this should become superfluous when there's a
# standard engine wrapper around OOo
def print_doc_from_ooo_template(template=None):

	# export template to file
	filename = template.save_to_file()
	if filename is None:
		gmGuiHelpers.gm_show_error (
			_(	'Error exporting form template\n'
				'\n'
				' "%s" (%s)'
			) % (template['name_long'], template['external_version']),
			_('Letter template export')
		)
		return False

	try:
		doc = gmForms.cOOoLetter(template_file = filename, instance_type = template['instance_type'])
	except ImportError:
		gmGuiHelpers.gm_show_error (
			_('Cannot connect to OpenOffice.\n\n'
			  'The UNO bridge module for Python\n'
			  'is not installed.'
			),
			_('Letter writer')
		)
		return False

	if not doc.open_in_ooo():
		gmGuiHelpers.gm_show_error (
			_('Cannot connect to OpenOffice.\n'
			  '\n'
			  'You may want to increase the option\n'
			  '\n'
			  ' <%s>'
			) % _('OOo startup time'),
			_('Letter writer')
		)
		try: os.remove(filename)
		except Exception: pass
		return False

	doc.show(False)
	ph_handler = gmMacro.gmPlaceholderHandler()
	doc.replace_placeholders(handler = ph_handler)

	filename = filename.replace('.ott', '.odt').replace('-FormTemplate-', '-FormInstance-')
	doc.save_in_ooo(filename = filename)

	doc.show(True)

	return True

#------------------------------------------------------------
def generate_failsafe_form_wrapper(pk_patient:int=None, title:str=None, max_width:int=80) -> list[list[str]]:
	header = []
	header = ['#' + '=' * (max_width - 2) + '#']
	header.append(_('Healthcare provider:'))
	provider = gmStaff.gmCurrentProvider()
	header.append('  %s%s %s' % (
		gmTools.coalesce(provider['title'], '', '%s '),
		provider['firstnames'],
		provider['lastnames']
	))
	praxis = gmPraxis.gmCurrentPraxisBranch()
	for line in praxis.format_for_failsafe_output(max_width = max_width):
		header.append('  ' + line)
	header.append('#' + '-' * (max_width - 2) + '#')
	header.append('')
	patient = gmPerson.cPerson(pk_patient)
	header.append(_('Patient:'))
	header.append('  ' + patient.description_gender)
	header.append('  ' + _('born: %s (%s)') % (
			patient.get_formatted_dob(honor_estimation = True),
			patient.medical_age
		))
	header.append('')
	header.append('#' + '-' * (max_width - 2) + '#')
	if title:
		indent = ' ' * ((max_width - len(title)) // 2)
		header.append('')
		header.append(indent + ('*' * len(title)))
		header.append(indent + title)
		header.append(indent + ('*' * len(title)))
		header.append('')
	footer = []
	footer.append('')
	footer.append('#' + '-' * (max_width - 2) + '#')
	footer.append(_('(GNUmed v%s failsafe form -- https://www.gnumed.de)') % _cfg.get(option = 'client_version'))
	footer.append('#' + '=' * (max_width - 2) + '#')
	return [header, footer]

#------------------------------------------------------------
def generate_form_from_template(parent=None, template_types=None, edit=None, template=None, excluded_template_types=None):
	"""If <edit> is None it will honor the template setting."""

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	# 1) get template to use
	if template is None:
		template = manage_form_templates (
			parent = parent,
			active_only = True,
			template_types = template_types,
			excluded_types = excluded_template_types
		)
		if template is None:
			gmDispatcher.send(signal = 'statustext', msg = _('No document template selected.'), beep = False)
			return None

	if template['engine'] == 'O':
		return print_doc_from_ooo_template(template = template)

	wx.BeginBusyCursor()

	# 2) process template
	form = None
	try:
		form = template.instantiate()
	except KeyError:
		_log.exception('cannot instantiate document template [%s]', template)
	if not form:
		wx.EndBusyCursor()
		gmGuiHelpers.gm_show_error (
			error = _('Invalid document template [%s - %s (%s)]') % (
				template['name_long'],
				template['external_version'],
				template['engine']
			),
			title = _('Generating document from template')
		)
		return None

	ph = gmMacro.gmPlaceholderHandler()
	#ph.debug = True
	form.substitute_placeholders(data_source = ph)
	if edit is None:
		if form.template['edit_after_substitution']:
			edit = True
		else:
			edit = False
	if edit:
		wx.EndBusyCursor()
		form.edit()
		wx.BeginBusyCursor()

	# 3) generate output
	pdf_name = form.generate_output()
	wx.EndBusyCursor()
	if pdf_name is not None:
		return form

	gmGuiHelpers.gm_show_error (
		error = _('Error generating document printout.'),
		title = _('Generating document printout')
	)
	return None

#------------------------------------------------------------
def act_on_generated_forms(parent=None, forms=None, jobtype=None, episode_name=None, progress_note=None, review_copy_as_normal=False):
	"""This function assumes that .generate_output() has already been called on each form.

	It operates on the active patient.
	"""
	if len(forms) == 0:
		return True

	no_of_printables = 0
	for form in forms:
		no_of_printables += len(form.final_output_filenames)

	if no_of_printables == 0:
		return True

	soap_lines = []

	#-----------------------------
	def save_soap(soap=None):
		if episode_name is None:
			return
		if soap.strip() == '':
			return
		pat = gmPerson.gmCurrentPatient()
		emr = pat.emr
		epi = emr.add_episode(episode_name = episode_name, is_open = False)
		emr.add_clin_narrative (
			soap_cat = None,
			note = soap,
			episode = epi
		)

	#-----------------------------
	def archive_forms(episode_name=None, comment=None):
		if episode_name is None:
			epi = None				# will ask for episode further down
		else:
			pat = gmPerson.gmCurrentPatient()
			emr = pat.emr
			epi = emr.add_episode(episode_name = episode_name, is_open = False)
		for form in forms:
			files2import = []
			files2import.extend(form.final_output_filenames)
			files2import.extend(form.re_editable_filenames)
			if len(files2import) == 0:
				continue
			save_files_as_new_document (
				parent = parent,
				filenames = files2import,
				document_type = form.template['instance_type'],
				unlock_patient = False,
				episode = epi,
				review_as_normal = review_copy_as_normal,
				reference = None,
				pk_org_unit = gmPraxis.gmCurrentPraxisBranch()['pk_org_unit'],
				comment = comment,
				date_generated = gmDateTime.pydt_now_here()
			)
		return True

	#-----------------------------
	def print_forms():
		# anything to do ?
		files2print = []
		form_names = []
		for form in forms:
			files2print.extend(form.final_output_filenames)
			form_names.append('%s (%s)' % (form.template['name_long'], form.template['external_version']))
		if len(files2print) == 0:
			return True
		# print
		printed = gmPrinting.print_files(filenames = files2print, jobtype = jobtype, verbose = _cfg.get(option = 'debug'))
		if not printed:
			gmGuiHelpers.gm_show_error (
				error = _('Error printing documents.'),
				title = _('Printing [%s]') % jobtype
			)
			return False
		soap_lines.append(_('Printed: %s') % ', '.join(form_names))
		return True

	#-----------------------------
	def export_forms(remote_print=False):
		pat = gmPerson.gmCurrentPatient()
		return pat.export_area.add_forms(forms = forms, designation = gmTools.bool2subst(remote_print, 'print', None, None))

	#-----------------------------
	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	if jobtype is None:
		jobtype = 'generic_document'

	dlg = cFormDisposalDlg(parent, -1)
	dlg.forms = forms
	dlg.progress_note = progress_note
	dlg.episode_name = episode_name
	action_code = dlg.ShowModal()

	if action_code == wx.ID_CANCEL:
		dlg.DestroyLater()
		return True

	forms = dlg._LCTRL_forms.get_item_data()
	if len(forms) == 0:
		dlg.DestroyLater()
		return True

	progress_note = dlg.progress_note
	episode_name = dlg._PRW_episode.GetValue().strip()
	if episode_name == '':
		episode_name = None
	also_export = dlg._CHBOX_export.GetValue()
	dlg.DestroyLater()

	if action_code == _ID_FORM_DISPOSAL_ARCHIVE_ONLY:
		success = archive_forms(episode_name = episode_name, comment = progress_note)
		if not success:
			return False
		if progress_note != '':
			soap_lines.insert(0, progress_note)
		if len(soap_lines) > 0:
			save_soap(soap = '\n'.join(soap_lines))
		return True

	if action_code == _ID_FORM_DISPOSAL_EXPORT_ONLY:
		success = export_forms()
		if not success:
			return False
		if progress_note != '':
			soap_lines.insert(0, progress_note)
		if len(soap_lines) > 0:
			save_soap(soap = '\n'.join(soap_lines))
		return True

	success = False
	if action_code == _ID_FORM_DISPOSAL_PRINT:
		success = print_forms()
		if episode_name is not None:
			archive_forms(episode_name = episode_name, comment = progress_note)
		if also_export:
			export_forms()

	elif action_code == _ID_FORM_DISPOSAL_REMOTE_PRINT:
		success = export_forms(remote_print = True)
		if episode_name is not None:
			archive_forms(episode_name = episode_name, comment = progress_note)

	if not success:
		return False

	if progress_note != '':
		soap_lines.insert(0, progress_note)
	if len(soap_lines) > 0:
		save_soap(soap = '\n'.join(soap_lines))

	return True

#============================================================
from Gnumed.wxGladeWidgets import wxgFormDisposalDlg

class cFormDisposalDlg(wxgFormDisposalDlg.wxgFormDisposalDlg):

	def __init__(self, *args, **kwargs):

		wxgFormDisposalDlg.wxgFormDisposalDlg.__init__(self, *args, **kwargs)

		self.__init_ui()

	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def _set_msg(self, msg):
		self._LBL_msg.SetLabel(msg)
		self._LBL_msg.Refresh()

	message = property(lambda x:x, _set_msg)

	#--------------------------------------------------------
	def _set_forms(self, forms):
		items = [ f.template['name_long'] for f in forms ]
		self._LCTRL_forms.set_string_items(items)
		self._LCTRL_forms.set_data(forms)

	forms = property(lambda x:x, _set_forms)

	#--------------------------------------------------------
	def _get_note(self):
		return self._TCTRL_soap.GetValue().strip()

	def _set_note(self, note):
		if note is None:
			note = ''
		self._TCTRL_soap.SetValue(note)

	progress_note = property(_get_note, _set_note)

	#--------------------------------------------------------
	def _get_episode_name(self):
		return self._PRW_episode.GetValue().strip()

	def _set_episode_name(self, episode_name):
		if episode_name is None:
			episode_name = ''
		self._PRW_episode.SetValue(episode_name)

	episode_name = property(_get_episode_name, _set_episode_name)

	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def __init_ui(self):
		self._LCTRL_forms.set_columns([_('Form')])
		#self._CHBOX_export.SetValue(False)
	#--------------------------------------------------------
	# event handlers
	#--------------------------------------------------------
	def _on_print_button_pressed(self, event):
		self.EndModal(_ID_FORM_DISPOSAL_PRINT)
	#--------------------------------------------------------
	def _on_remote_print_button_pressed(self, event):
		self.EndModal(_ID_FORM_DISPOSAL_REMOTE_PRINT)
	#--------------------------------------------------------
	def _on_export_button_pressed(self, event):
		self.EndModal(_ID_FORM_DISPOSAL_EXPORT_ONLY)
	#--------------------------------------------------------
	def _on_archive_button_pressed(self, event):
		self.EndModal(_ID_FORM_DISPOSAL_ARCHIVE_ONLY)
	#--------------------------------------------------------
	def _on_show_forms_button_pressed(self, event):
		event.Skip()
		if self._LCTRL_forms.ItemCount == 0:
			return
		forms2show = self._LCTRL_forms.get_selected_item_data()
		if len(forms2show) == 0:
			data = self._LCTRL_forms.get_item_data(item_idx = 0)
			if data is None:
				return
			forms2show = [data]
		if len(forms2show) == 0:
			return
		for form in forms2show:
			for filename in form.final_output_filenames:
				gmMimeLib.call_viewer_on_file(filename, block = True)
	#--------------------------------------------------------
	def _on_delete_forms_button_pressed(self, event):
		print("Event handler '_on_delete_forms_button_pressed' not implemented!")
		event.Skip()

#============================================================
# form template management
#------------------------------------------------------------
def edit_template(parent=None, template=None, single_entry=False):
	ea = cFormTemplateEAPnl(parent, -1)
	ea.data = template
	ea.mode = gmTools.coalesce(template, 'new', 'edit')
	dlg = gmEditArea.cGenericEditAreaDlg2(parent, -1, edit_area = ea, single_entry = single_entry)
	dlg.SetTitle(gmTools.coalesce(template, _('Adding new form template'), _('Editing form template')))
	if dlg.ShowModal() == wx.ID_OK:
		dlg.DestroyLater()
		return True
	dlg.DestroyLater()
	return False

#------------------------------------------------------------
def manage_form_templates(parent=None, template_types=None, active_only=False, excluded_types=None, msg=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	#-------------------------
	def edit(template=None):
		return edit_template(parent = parent, template = template)
	#-------------------------
	def delete(template):
		delete = gmGuiHelpers.gm_show_question (
			title = _('Deleting form template.'),
			question = _(
				'Are you sure you want to delete\n'
				'the following form template ?\n\n'
				' "%s (%s)"\n\n'
				'You can only delete templates which\n'
				'have not yet been used to generate\n'
				'any forms from.'
			) % (template['name_long'], template['external_version'])
		)
		if delete:
			# FIXME: make this a privileged operation ?
			gmForms.delete_form_template(template = template)
			return True
		return False
	#-------------------------
	def refresh(lctrl):
		templates = gmForms.get_form_templates(active_only = active_only, template_types = template_types, excluded_types = excluded_types)
		lctrl.set_string_items(items = [ [t['name_long'], t['external_version'], gmForms.form_engine_names[t['engine']]] for t in templates ])
		lctrl.set_data(data = templates)
	#-------------------------
	template = gmListWidgets.get_choices_from_list (
		parent = parent,
		msg = msg,
		caption = _('Select letter or form template.'),
		columns = [_('Template'), _('Version'), _('Type')],
		edit_callback = edit,
		new_callback = edit,
		delete_callback = delete,
		refresh_callback = refresh,
		single_selection = True
	)

	return template

#------------------------------------------------------------
from Gnumed.wxGladeWidgets import wxgFormTemplateEditAreaPnl

class cFormTemplateEAPnl(wxgFormTemplateEditAreaPnl.wxgFormTemplateEditAreaPnl, gmEditArea.cGenericEditAreaMixin):

	def __init__(self, *args, **kwargs):

		try:
			data = kwargs['template']
			del kwargs['template']
		except KeyError:
			data = None

		wxgFormTemplateEditAreaPnl.wxgFormTemplateEditAreaPnl.__init__(self, *args, **kwargs)
		gmEditArea.cGenericEditAreaMixin.__init__(self)

		self.full_filename = None

		self.mode = 'new'
		self.data = data
		if data is not None:
			self.mode = 'edit'

		self.__init_ui()
	#----------------------------------------------------------------
	def __init_ui(self):
		self._PRW_name_long.matcher = gmForms.cFormTemplateNameLong_MatchProvider()
		self._PRW_name_short.matcher = gmForms.cFormTemplateNameShort_MatchProvider()
		self._PRW_template_type.matcher = gmForms.cFormTemplateType_MatchProvider()
	#----------------------------------------------------------------
	# generic Edit Area mixin API
	#----------------------------------------------------------------
	def _valid_for_save(self):

		validity = True

		# self._TCTRL_filename
		self.display_tctrl_as_valid(tctrl = self._TCTRL_filename, valid = True)
		fname = self._TCTRL_filename.GetValue().strip()
		# 1) new template: file must exist
		if self.data is None:
			try:
				open(fname, 'r').close()
			except Exception:
				validity = False
				self.display_tctrl_as_valid(tctrl = self._TCTRL_filename, valid = False)
				self.StatusText = _('You must select a template file before saving.')
				self._TCTRL_filename.SetFocus()
		# 2) existing template
		# - empty = no change
		# - does not exist: name change in DB field
		# - does exist: reload from filesystem

		# self._PRW_instance_type
		if self._PRW_instance_type.GetValue().strip() == '':
			validity = False
			self._PRW_instance_type.display_as_valid(False)
			self.StatusText = _('You must enter a type for documents created with this template.')
			self._PRW_instance_type.SetFocus()
		else:
			self._PRW_instance_type.display_as_valid(True)

		# self._PRW_template_type
		if self._PRW_template_type.GetData() is None:
			validity = False
			self._PRW_template_type.display_as_valid(False)
			self.StatusText = _('You must enter a type for this template.')
			self._PRW_template_type.SetFocus()
		else:
			self._PRW_template_type.display_as_valid(True)

		# self._TCTRL_external_version
		if self._TCTRL_external_version.GetValue().strip() == '':
			validity = False
			self.display_tctrl_as_valid(tctrl = self._TCTRL_external_version, valid = False)
			self.StatusText = _('You must enter a version for this template.')
			self._TCTRL_external_version.SetFocus()
		else:
			self.display_tctrl_as_valid(tctrl = self._TCTRL_external_version, valid = True)

		# self._PRW_name_short
		if self._PRW_name_short.GetValue().strip() == '':
			validity = False
			self._PRW_name_short.display_as_valid(False)
			self.StatusText = _('Missing short name for template.')
			self._PRW_name_short.SetFocus()
		else:
			self._PRW_name_short.display_as_valid(True)

		# self._PRW_name_long
		if self._PRW_name_long.GetValue().strip() == '':
			validity = False
			self._PRW_name_long.display_as_valid(False)
			self.StatusText = _('Missing long name for template.')
			self._PRW_name_long.SetFocus()
		else:
			self._PRW_name_long.display_as_valid(True)

		return validity
	#----------------------------------------------------------------
	def _save_as_new(self):
		data = gmForms.create_form_template (
			template_type = self._PRW_template_type.GetData(),
			name_short = self._PRW_name_short.GetValue().strip(),
			name_long = self._PRW_name_long.GetValue().strip()
		)
		data['external_version'] = self._TCTRL_external_version.GetValue()
		data['instance_type'] = self._PRW_instance_type.GetValue().strip()
		data['filename'] = os.path.split(self._TCTRL_filename.GetValue().strip())[1]
		data['in_use'] = self._CHBOX_active.GetValue()
		data['edit_after_substitution'] = self._CHBOX_editable.GetValue()
		data['engine'] = gmForms.form_engine_abbrevs[self._CH_engine.GetSelection()]
		data.save()

		data.update_template_from_file(filename = self._TCTRL_filename.GetValue().strip())

		self.data = data
		return True
	#----------------------------------------------------------------
	def _save_as_update(self):
		self.data['pk_template_type'] = self._PRW_template_type.GetData()
		self.data['name_short'] = self._PRW_name_short.GetValue().strip()
		self.data['name_long'] = self._PRW_name_long.GetValue().strip()
		self.data['external_version'] = self._TCTRL_external_version.GetValue()
		tmp = self._PRW_instance_type.GetValue().strip()
		if tmp not in [self.data['instance_type'], self.data['l10n_instance_type']]:
			self.data['instance_type'] = tmp
		tmp = os.path.split(self._TCTRL_filename.GetValue().strip())[1]
		if tmp != '':
			self.data['filename'] = tmp
		self.data['in_use'] = self._CHBOX_active.GetValue()
		self.data['edit_after_substitution'] = self._CHBOX_editable.GetValue()
		self.data['engine'] = gmForms.form_engine_abbrevs[self._CH_engine.GetSelection()]
		self.data.save()

		fname = self._TCTRL_filename.GetValue().strip()
		try:
			open(fname, 'r').close()
			self.data.update_template_from_file(filename = fname)
		except Exception:
			pass # filename column already updated

		return True
	#----------------------------------------------------------------
	def _refresh_as_new(self):
		self._PRW_name_long.SetText('')
		self._PRW_name_short.SetText('')
		self._TCTRL_external_version.SetValue('')
		self._PRW_template_type.SetText('')
		self._PRW_instance_type.SetText('')
		self._TCTRL_filename.SetValue('')
		self._CH_engine.SetSelection(0)
		self._CHBOX_active.SetValue(True)
		self._CHBOX_editable.SetValue(True)
		self._LBL_status.SetLabel('')
		self._BTN_export.Enable(False)

		self._PRW_name_long.SetFocus()
	#----------------------------------------------------------------
	def _refresh_as_new_from_existing(self):
		self._refresh_as_new()
	#----------------------------------------------------------------
	def _refresh_from_existing(self):
		self._PRW_name_long.SetText(self.data['name_long'])
		self._PRW_name_short.SetText(self.data['name_short'])
		self._TCTRL_external_version.SetValue(self.data['external_version'])
		self._PRW_template_type.SetText(self.data['l10n_template_type'], data = self.data['pk_template_type'])
		self._PRW_instance_type.SetText(self.data['l10n_instance_type'], data = self.data['instance_type'])
		self._TCTRL_filename.SetValue(self.data['filename'])
		self._CH_engine.SetSelection(gmForms.form_engine_abbrevs.index(self.data['engine']))
		self._CHBOX_active.SetValue(self.data['in_use'])
		self._CHBOX_editable.SetValue(self.data['edit_after_substitution'])
		self._LBL_status.SetLabel(_('last modified %s by %s, internal revision [%s]') % (
			self.data['last_modified'].strftime('%Y %B %d'),
			self.data['modified_by'],
			gmTools.coalesce(self.data['gnumed_revision'], '?')
		))

		self._TCTRL_filename.Enable(True)
		self._BTN_load.Enable(True)
		self._BTN_export.Enable(True)

		self._BTN_load.SetFocus()
	#----------------------------------------------------------------
	# event handlers
	#----------------------------------------------------------------
	def _on_load_button_pressed(self, event):
		engine_abbrev = gmForms.form_engine_abbrevs[self._CH_engine.GetSelection()]

		wildcards = []
		try:
			wildcards.append('%s (%s)|%s' % (
				gmForms.form_engine_names[engine_abbrev],
				gmForms.form_engine_template_wildcards[engine_abbrev],
				gmForms.form_engine_template_wildcards[engine_abbrev]
			))
		except KeyError:
			pass
		wildcards.append("%s (*)|*" % _('all files'))
		wildcards.append("%s (*.*)|*.*" % _('all files (Windows)'))

		dlg = wx.FileDialog (
			parent = self,
			message = _('Choose a form template file'),
			defaultDir = gmTools.gmPaths().user_work_dir,
			defaultFile = '',
			wildcard = '|'.join(wildcards),
			style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
		)
		result = dlg.ShowModal()
		if result != wx.ID_CANCEL:
			self._TCTRL_filename.SetValue(dlg.GetPath())
		dlg.DestroyLater()

		event.Skip()
	#----------------------------------------------------------------
	def _on_export_button_pressed(self, event):
		if self.data is None:
			return

		engine_abbrev = gmForms.form_engine_abbrevs[self._CH_engine.GetSelection()]

		wildcards = []
		try:
			wildcards.append('%s (%s)|%s' % (
				gmForms.form_engine_names[engine_abbrev],
				gmForms.form_engine_template_wildcards[engine_abbrev],
				gmForms.form_engine_template_wildcards[engine_abbrev]
			))
		except KeyError:
			pass
		wildcards.append("%s (*)|*" % _('all files'))
		wildcards.append("%s (*.*)|*.*" % _('all files (Windows)'))

		dlg = wx.FileDialog (
			parent = self,
			message = _('Enter a filename to save the template to'),
			defaultDir = gmTools.gmPaths().user_work_dir,
			defaultFile = '',
			wildcard = '|'.join(wildcards),
			style = wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT
		)
		result = dlg.ShowModal()
		if result != wx.ID_CANCEL:
			fname = dlg.GetPath()
			self.data.save_to_file(filename = fname)
		dlg.DestroyLater()

		event.Skip()

#============================================================
from Gnumed.wxGladeWidgets import wxgReceiverSelectionDlg

class cReceiverSelectionDlg(wxgReceiverSelectionDlg.wxgReceiverSelectionDlg):

	def __init__(self, *args, **kwargs):
		wxgReceiverSelectionDlg.wxgReceiverSelectionDlg.__init__(self, *args, **kwargs)
		self.__patient = None
		self.__init_ui()
		self.__register_interests()

	#------------------------------------------------------------
	def __init_ui(self):
		if self.__patient is None:
			return

		self._LCTRL_candidates.set_columns([_('Receiver'), _('Details')])
		self._LCTRL_candidates.set_resize_column()
		self._LCTRL_candidates.item_tooltip_callback = self._get_candidate_tooltip
		self.__populate_candidates_list()

		self._LCTRL_addresses.set_resize_column()
		self._LCTRL_addresses.item_tooltip_callback = self._get_address_tooltip
		self._LCTRL_addresses.activate_callback = self._on_address_activated_in_list
		adrs = self.__patient.get_addresses()
		self.__populate_address_list(addresses = adrs)

		self._TCTRL_final_name.SetValue(self.__patient.description.strip())

		self.Layout()

	#------------------------------------------------------------
	def __register_interests(self):
		self._TCTRL_final_name.add_callback_on_modified(callback = self._on_final_name_modified)
		self._PRW_other_address.add_callback_on_selection(self._on_address_selected_in_PRW)
		self._PRW_org_unit.add_callback_on_set_focus(self._on_entering_org_unit_PRW)
		self._PRW_org_unit.add_callback_on_selection(self._on_org_unit_selected_in_PRW)

	#------------------------------------------------------------
	def __populate_candidates_list(self):

		list_items = [[_('Patient'), self.__patient.description_gender.strip()]]
		list_data = [(self.__patient.description.strip(), self.__patient.get_addresses(), '', None)]

		candidate_type = _('Emergency contact')
		if self.__patient['emergency_contact'] is not None:
			name = self.__patient['emergency_contact'].strip()
			list_items.append([candidate_type, name])
			list_data.append((name, [], '', None))
		contact = self.__patient.emergency_contact_in_database
		if contact is not None:
			list_items.append([candidate_type, contact.description_gender])
			list_data.append((contact.description.strip(), contact.get_addresses(), '', None))

		candidate_type = _('Primary doctor')
		prov = self.__patient.primary_provider
		if prov is not None:
			ident = prov.identity
			list_items.append([candidate_type, '%s: %s' % (prov['short_alias'], ident.description_gender)])
			list_data.append((ident.description.strip(), ident.get_addresses(), _('in-praxis primary provider'), None))

		candidate_type = _('This praxis')
		branches = gmPraxis.get_praxis_branches(order_by = 'branch')
		for branch in branches:
			adr = branch.address
			if adr is None:
				continue
			list_items.append([candidate_type, '%s @ %s' % (branch['branch'], branch['praxis'])])
			list_data.append(('%s @ %s' % (branch['branch'], branch['praxis']), [adr], branch.format(), None))
		del branches

		candidate_type = _('External care')
		cares = gmExternalCare.get_external_care_items(pk_identity = self.__patient.ID)
		for care in cares:
			details = '%s%s@%s (%s)' % (
				gmTools.coalesce(care['provider'], '', '%s: '),
				care['unit'],
				care['organization'],
				care['issue']
			)
			name = ('%s%s' % (
				gmTools.coalesce(care['provider'], '', '%s, '),
				'%s @ %s' % (care['unit'], care['organization'])
			)).strip()
			org_unit = care.org_unit
			adr = org_unit.address
			if adr is None:
				addresses = []
			else:
				addresses = [adr]
			list_items.append([candidate_type, details])
			tt = '\n'.join(care.format(with_health_issue = True, with_address = True, with_comms = True))
			list_data.append((name, addresses, tt, org_unit))
		del cares

		emr = self.__patient.emr

		candidate_type = _('Hospital stay')
		depts = emr.get_attended_hospitals_as_org_units()
		for dept in depts:
			adr = dept.address
			if adr is None:
				continue
			list_items.append([candidate_type, '%s @ %s' % (dept['unit'], dept['organization'])])
			list_data.append(('%s @ %s' % (dept['unit'], dept['organization']), [adr], '\n'.join(dept.format(with_comms = True)), dept))
		del depts

		candidate_type = _('Procedure')
		proc_locs = emr.get_procedure_locations_as_org_units()
		for proc_loc in proc_locs:
			adr = proc_loc.address
			if adr is None:
				continue
			list_items.append([candidate_type, '%s @ %s' % (proc_loc['unit'], proc_loc['organization'])])
			list_data.append(('%s @ %s' % (proc_loc['unit'], proc_loc['organization']), [adr], '\n'.join(proc_loc.format(with_comms = True)), proc_loc))
		del proc_locs

		candidate_type = _('Lab')
		labs = emr.get_labs_as_org_units()
		for lab in labs:
			adr = lab.address
			if adr is None:
				continue
			list_items.append([candidate_type, '%s @ %s' % (lab['unit'], lab['organization'])])
			list_data.append(('%s @ %s' % (lab['unit'], lab['organization']), [adr], '\n'.join(lab.format(with_comms = True)), lab))
		del labs

		candidate_type = _('Bill receiver')
		bills = self.__patient.bills
		adrs_seen = []
		for bill in bills:
			if bill['pk_receiver_address'] in adrs_seen:
				continue
			adr = bill.address
			if adr is None:
				continue
			adrs_seen.append(bill['pk_receiver_address'])
			details = '%s%s' % (bill['invoice_id'], gmDateTime.pydt_strftime(dt = bill['close_date'], format = ' (%Y %b %d)', none_str = ''))
			list_items.append([candidate_type, details])
			list_data.append(('', [adr], '\n'.join(adr.format()), None))

		candidate_type = _('Document')
		doc_folder = self.__patient.document_folder
		doc_units = doc_folder.all_document_org_units
		for doc_unit in doc_units:
			adr = doc_unit.address
			if adr is None:
				continue
			list_items.append([candidate_type, '%s @ %s' % (doc_unit['unit'], doc_unit['organization'])])
			list_data.append(('%s @ %s' % (doc_unit['unit'], doc_unit['organization']), [adr], '\n'.join(doc_unit.format(with_comms = True)), doc_unit))
		del doc_units

		self._LCTRL_candidates.set_string_items(list_items)
		self._LCTRL_candidates.set_column_widths()
		self._LCTRL_candidates.set_data(list_data)

	#------------------------------------------------------------
	def _get_candidate_tooltip(self, data):
		if data is None:
			return ''
		name, addresses, tt, unit = data
		return tt

	#------------------------------------------------------------
	def __update_address_info(self, adr):
		if adr is None:
			self._LBL_address_details.SetLabel('')
			self._LBL_final_country.SetLabel('')
			self._LBL_final_region.SetLabel('')
			self._LBL_final_zip.SetLabel('')
			self._LBL_final_location.SetLabel('')
			self._LBL_final_street.SetLabel('')
			self._LBL_final_number.SetLabel('')
			self.Layout()
			return
		self._LBL_address_details.SetLabel('\n'.join(adr.format()))
		self._LBL_final_country.SetLabel(adr['l10n_country'])
		self._LBL_final_region.SetLabel(adr['l10n_region'])
		self._LBL_final_zip.SetLabel(adr['postcode'])
		self._LBL_final_location.SetLabel('%s%s' % (adr['urb'], gmTools.coalesce(adr['suburb'], '', ' - %s')))
		self._LBL_final_street.SetLabel(adr['street'])
		self._LBL_final_number.SetLabel('%s%s' % (adr['number'], gmTools.coalesce(adr['subunit'], '', ' %s')))
		self.Layout()

	#------------------------------------------------------------
	def __populate_address_list(self, addresses=None):
		self._LCTRL_addresses.Enable()
		cols = [_(u'Address')]
		list_items = []
		for a in addresses:
			try:
				list_items.append([a['l10n_address_type'], a.format(single_line = True, verbose = False, show_type = False)])
				cols = [_('Type'), _('Address')]
			except KeyError:
				list_items.append([a.format(single_line = True, verbose = False, show_type = False)])
				cols = [_('Address')]

		self._LCTRL_addresses.set_columns(cols)
		self._LCTRL_addresses.set_string_items(list_items)
		self._LCTRL_candidates.set_column_widths()
		self._LCTRL_addresses.set_data(addresses)
		self._PRW_other_address.SetText(value = '', data = None)
		self.__update_address_info(None)

	#------------------------------------------------------------
	def _get_address_tooltip(self, adr):
		return '\n'.join(adr.format(show_type = True))

	#------------------------------------------------------------
	#------------------------------------------------------------
	def _on_final_name_modified(self):
		self._LBL_final_name.SetLabel(self._TCTRL_final_name.Value)

	#------------------------------------------------------------
	def _on_address_selected_in_PRW(self, address):
		self.__update_address_info(self._PRW_other_address.GetData(as_instance = True))

	#------------------------------------------------------------
	def _on_entering_org_unit_PRW(self):
		self._LCTRL_addresses.Disable()

	#------------------------------------------------------------
	def _on_org_unit_selected_in_PRW(self, unit):
		if unit is None:
			self._LCTRL_addresses.remove_items_safely(max_tries = 3)
			self._PRW_other_address.SetText(value = '', data = None)
			self.__update_address_info(None)
			self._TCTRL_org_unit_details.SetValue('')
			return

		unit = self._PRW_org_unit.GetData(as_instance = True)
		adr = unit.address
		if adr is None:
			self._LCTRL_addresses.remove_items_safely(max_tries = 3)
			self._PRW_other_address.SetText(value = '', data = None)
			self.__update_address_info(None)
		else:
			self.__populate_address_list(addresses = [adr])
			self._PRW_other_address.SetData(data = adr['pk_address'])
			self.__update_address_info(adr)

		name = '%s @ %s' % (unit['unit'], unit['organization'])
		self._TCTRL_final_name.SetValue(name)
		self._TCTRL_org_unit_details.SetValue('\n'.join(unit.format(with_comms = True)))
		self.Layout()

	#------------------------------------------------------------
	#------------------------------------------------------------
	def _on_candidate_selected(self, event):
		event.Skip()
		name, addresses, tt, unit = self._LCTRL_candidates.get_selected_item_data(only_one = True)
		self.__populate_address_list(addresses = addresses)
		if unit is None:
			self._PRW_org_unit.SetText(value = '', data = None)
			self._TCTRL_org_unit_details.SetValue('')
		else:
			self._PRW_org_unit.SetData(data = unit['pk_org_unit'])
			self._TCTRL_org_unit_details.SetValue('\n'.join(unit.format(with_comms = True)))
		self._TCTRL_final_name.SetValue(name.strip())
		self._LBL_final_name.SetLabel(name.strip())

	#------------------------------------------------------------
	def _on_address_activated_in_list(self, evt):
		evt.Skip()
		adr = self._LCTRL_addresses.get_selected_item_data(only_one = True)
		self._PRW_other_address.address = adr
		self.__update_address_info(adr)

	#------------------------------------------------------------
	#------------------------------------------------------------
	def _on_manage_addresses_button_pressed(self, event):
		event.Skip()
		from Gnumed.wxpython.gmAddressWidgets import manage_addresses
		manage_addresses(parent = self)

	#------------------------------------------------------------
	def _on_manage_orgs_button_pressed(self, event):
		event.Skip()
		from Gnumed.wxpython.gmOrganizationWidgets import manage_orgs
		manage_orgs(parent = self, no_parent = False)

	#------------------------------------------------------------
	def _on_ok_button_pressed(self, event):
		if self._TCTRL_final_name.GetValue().strip() == '':
			return False
		if self._PRW_other_address.address is None:
			return False
		event.Skip()
		self.EndModal(wx.ID_OK)

	#------------------------------------------------------------
	def _set_patient(self, patient):
		self.__patient = patient
		self.__init_ui()

	patient = property(lambda x:x, _set_patient)

	#------------------------------------------------------------
	def _get_name(self):
		return self._TCTRL_final_name.GetValue().strip()

	name = property(_get_name)

	#------------------------------------------------------------
	def _get_address(self):
		return self._PRW_other_address.address

	address = property(_get_address)

#============================================================
# main
#------------------------------------------------------------
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	del _
	from Gnumed.pycommon import gmI18N
	gmI18N.activate_locale()
	gmI18N.install_domain('gnumed')

	#----------------------------------------
#	def test_cFormTemplateEAPnl():
#		app = wx.PyWidgetTester(size = (400, 300))
#		cFormTemplateEAPnl(app.frame, -1, template = gmForms.cFormTemplate(aPK_obj=4))
#		app.frame.Show(True)
#		app.MainLoop()
#		return

	#----------------------------------------
	def test_form_template():

		from Gnumed.wxpython import gmGuiTest

		frame = gmGuiTest.setup_widget_test_env()
		print(frame)
		path = os.path.abspath(sys.argv[2])
		form = gmForms.cLaTeXForm(template_file = path)
		ph = gmMacro.gmPlaceholderHandler()
		ph.debug = True

		def handle_form():
			form.substitute_placeholders(data_source = ph)
			pdf_name = form.generate_output()
			print("final PDF file is:", pdf_name)
			return

		wx.CallLater(2000, handle_form)#, parent = frame)
		wx.GetApp().MainLoop()

	#----------------------------------------
	def test_print_generic_document():
		#gmStaff.set_current_provider_to_logged_on_user()
		from Gnumed.pycommon import gmPG2
		gmPG2.request_login_params(setup_pool = True)
		gmPraxis.gmCurrentPraxisBranch.from_first_branch()
		print_generic_document()	#parent=None, jobtype=None, episode=None

	#----------------------------------------
	def test_generate_failsafe_form_wrapper():
		from Gnumed.pycommon import gmPG2
		gmPG2.request_login_params(setup_pool = True)
		gmPraxis.gmCurrentPraxisBranch.from_first_branch()
		header, footer = generate_failsafe_form_wrapper(pk_patient = 12, max_width = 80)
		print('\n'.join(header))
		print('   HERE GOES THE FORM')
		print('\n'.join(footer))

	#----------------------------------------
	#test_cFormTemplateEAPnl()
	#test_print_generic_document()
	#test_generate_failsafe_form_wrapper()
	test_form_template()

#============================================================
