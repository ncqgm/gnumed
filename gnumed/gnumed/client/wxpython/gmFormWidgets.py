"""GNUmed form/letter handling widgets.
"""
#================================================================
__version__ = "$Revision: 1.16 $"
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"

import os.path, sys, logging


import wx


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmI18N, gmTools, gmDispatcher, gmPrinting
from Gnumed.business import gmForms, gmPerson
from Gnumed.wxpython import gmGuiHelpers, gmListWidgets, gmMacro
from Gnumed.wxGladeWidgets import wxgFormTemplateEditAreaPnl, wxgFormTemplateEditAreaDlg


_log = logging.getLogger('gm.ui')
_log.info(__version__)

#============================================================
# convenience functions
#============================================================
def print_doc_from_template(parent=None, jobtype=None, keep_a_copy=True, episode=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	# 1) get template
	template = manage_form_templates(parent = parent, active_only = True, excluded_types = ['gnuplot script', 'visual progress note'])
	if template is None:
		gmDispatcher.send(signal = 'statustext', msg = _('No document template selected.'))
		return None

	if template['engine'] == u'O':
		return print_doc_from_ooo_template(template = template)

	wx.BeginBusyCursor()

	# 2) process template
	try:
		doc = template.instantiate()
	except KeyError:
		wx.EndBusyCursor()
		gmGuiHelpers.gm_show_error (
			aMessage = _('Error creating printable document.\n\nThere is no engine for this type of template.'),
			aTitle = _('Printing document')
		)
		return False
	ph = gmMacro.gmPlaceholderHandler()
	#ph.debug = True
	doc.substitute_placeholders(data_source = ph)
	doc.edit()
	printable_file = doc.generate_output()
	if printable_file is None:
		wx.EndBusyCursor()
		gmGuiHelpers.gm_show_error (
			aMessage = _('Error creating printable document.'),
			aTitle = _('Printing document')
		)
		return False

	# 3) print template
	if jobtype is None:
		jobtype = 'generic_document'

	printed = gmPrinting.print_file(filename = printable_file, jobtype = jobtype)
	if not printed:
		wx.EndBusyCursor()
		gmGuiHelpers.gm_show_error (
			aMessage = _('Error printing document (%s).') % jobtype,
			aTitle = _('Printing document')
		)
		return False

	pat = gmPerson.gmCurrentPatient()
	emr = pat.get_emr()
	if episode is None:
		episode = emr.add_episode(episode_name = 'administration', is_open = False)
	emr.add_clin_narrative (
		soap_cat = None,
		note = _('%s printed from template [%s - %s]') % (jobtype, template['name_long'], template['external_version']),
		episode = episode
	)

	# 4) keep a copy
	if keep_a_copy:
		# tell UI to import the file
		gmDispatcher.send (
			signal = u'import_document_from_file',
			filename = printable_file,
			document_type = template['instance_type'],
			unlock_patient = True
		)

	wx.EndBusyCursor()

	return True
#------------------------------------------------------------
# eventually this should become superfluous when there's a
# standard engine wrapper around OOo
def print_doc_from_ooo_template(template=None):

	# export template to file
	filename = template.export_to_file()
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
		except: pass
		return False

	doc.show(False)
	ph_handler = gmMacro.gmPlaceholderHandler()
	doc.replace_placeholders(handler = ph_handler)

	filename = filename.replace('.ott', '.odt').replace('-FormTemplate-', '-FormInstance-')
	doc.save_in_ooo(filename = filename)

	doc.show(True)

	return True
#------------------------------------------------------------
def manage_form_templates(parent=None, template_types=None, active_only=False, excluded_types=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	#-------------------------
	def edit(template=None):
		dlg = cFormTemplateEditAreaDlg(parent, -1, template=template)
		result = dlg.ShowModal()
		return (result == wx.ID_OK)
	#-------------------------
	def delete(template):
		delete = gmGuiHelpers.gm_show_question (
			aTitle = _('Deleting form template.'),
			aMessage = _(
				'Are you sure you want to delete\n'
				'the following form template ?\n\n'
				' "%s (%s)"\n\n'
				'You can only delete templates which\n'
				'have not yet been used to generate\n'
				'any forms from.'
			) % (template['name_long'], template['external_version'])
		)
		if delete:
			# FIXME: make this a priviledged operation ?
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
def create_new_letter(parent=None):

	# 1) have user select template
	template = manage_form_templates(parent = parent, active_only = True, excluded_types = ['gnuplot script', 'visual progress note'])
	if template is None:
		return

	wx.BeginBusyCursor()

	# 2) export template to file
	filename = template.export_to_file()
	if filename is None:
		wx.EndBusyCursor()
		gmGuiHelpers.gm_show_error (
			_(	'Error exporting form template\n'
				'\n'
				' "%s" (%s)'
			) % (template['name_long'], template['external_version']),
			_('Letter template export')
		)
		return

	try:
		doc = gmForms.cOOoLetter(template_file = filename, instance_type = template['instance_type'])
	except ImportError:
		wx.EndBusyCursor()
		gmGuiHelpers.gm_show_error (
			_('Cannot connect to OpenOffice.\n\n'
			  'The UNO bridge module for Python\n'
			  'is not installed.'
			),
			_('Letter writer')
		)
		return

	if not doc.open_in_ooo():
		wx.EndBusyCursor()
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
		except: pass
		return

	doc.show(False)
	ph_handler = gmMacro.gmPlaceholderHandler()

	wx.EndBusyCursor()

	doc.replace_placeholders(handler = ph_handler)

	wx.BeginBusyCursor()
	filename = filename.replace('.ott', '.odt').replace('-FormTemplate-', '-FormInstance-')
	doc.save_in_ooo(filename = filename)
	wx.EndBusyCursor()

	doc.show(True)
#============================================================
class cFormTemplateEditAreaPnl(wxgFormTemplateEditAreaPnl.wxgFormTemplateEditAreaPnl):

	def __init__(self, *args, **kwargs):
		try:
			self.__template = kwargs['template']
			del kwargs['template']
		except KeyError:
			self.__template = None

		wxgFormTemplateEditAreaPnl.wxgFormTemplateEditAreaPnl.__init__(self, *args, **kwargs)

		self._PRW_name_long.matcher = gmForms.cFormTemplateNameLong_MatchProvider()
		self._PRW_name_short.matcher = gmForms.cFormTemplateNameShort_MatchProvider()
		self._PRW_template_type.matcher = gmForms.cFormTemplateType_MatchProvider()

		self.refresh()

		self.full_filename = None
	#--------------------------------------------------------
	def refresh(self, template = None):
		if template is not None:
			self.__template = template

		if self.__template is None:
			self._PRW_name_long.SetText(u'')
			self._PRW_name_short.SetText(u'')
			self._TCTRL_external_version.SetValue(u'')
			self._PRW_template_type.SetText(u'')
			self._PRW_instance_type.SetText(u'')
			self._TCTRL_filename.SetValue(u'')
			self._CH_engine.SetSelection(0)
			self._CHBOX_active.SetValue(True)

			self._TCTRL_date_modified.SetValue(u'')
			self._TCTRL_modified_by.SetValue(u'')

			self._BTN_export.Enable(False)
		else:
			self._PRW_name_long.SetText(self.__template['name_long'])
			self._PRW_name_short.SetText(self.__template['name_short'])
			self._TCTRL_external_version.SetValue(self.__template['external_version'])
			self._PRW_template_type.SetText(self.__template['l10n_template_type'], data = self.__template['pk_template_type'])
			self._PRW_instance_type.SetText(self.__template['l10n_instance_type'], data = self.__template['instance_type'])
			self._TCTRL_filename.SetValue(self.__template['filename'])
			self._CH_engine.SetSelection(gmForms.form_engine_abbrevs.index(self.__template['engine']))
			self._CHBOX_active.SetValue(self.__template['in_use'])

			self._TCTRL_date_modified.SetValue(self.__template['last_modified'].strftime('%x'))
			self._TCTRL_modified_by.SetValue(self.__template['modified_by'])

			self._TCTRL_filename.Enable(True)
			self._BTN_load.Enable(not self.__template['has_instances'])

			self._BTN_export.Enable(True)

		self._PRW_name_long.SetFocus()
	#--------------------------------------------------------
	def __valid_for_save(self):
		error = False

		if gmTools.coalesce(self._PRW_name_long.GetValue(), u'').strip() == u'':
			error = True
			self._PRW_name_long.SetBackgroundColour('pink')
		else:
			self._PRW_name_long.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))

		if gmTools.coalesce(self._PRW_name_short.GetValue(), u'').strip() == u'':
			error = True
			self._PRW_name_short.SetBackgroundColour('pink')
		else:
			self._PRW_name_short.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))

		if gmTools.coalesce(self._TCTRL_external_version.GetValue(), u'').strip() == u'':
			error = True
			self._TCTRL_external_version.SetBackgroundColour('pink')
		else:
			self._TCTRL_external_version.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))

		if gmTools.coalesce(self._PRW_template_type.GetValue(), u'').strip() == u'':
			error = True
			self._PRW_template_type.SetBackgroundColour('pink')
		else:
			self._PRW_template_type.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))

		if gmTools.coalesce(self._PRW_instance_type.GetValue(), u'').strip() == u'':
			error = True
			self._PRW_instance_type.SetBackgroundColour('pink')
		else:
			self._PRW_instance_type.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))

		if self.__template is None and self.full_filename is None:
			error = True
			gmDispatcher.send(signal = 'statustext', msg = _('You must select a template file before saving.'), beep = True)

		return not error
	#--------------------------------------------------------
	def save(self):
		if not self.__valid_for_save():
			return False

		if self.__template is None:
			self.__template = gmForms.create_form_template (
				template_type = self._PRW_template_type.GetData(),
				name_short = self._PRW_name_short.GetValue().strip(),
				name_long = self._PRW_name_long.GetValue().strip()
			)
		else:
			self.__template['pk_template_type'] = self._PRW_template_type.GetData()
			self.__template['name_short'] = self._PRW_name_short.GetValue().strip()
			self.__template['name_long'] = self._PRW_name_long.GetValue().strip()

		if not self.__template['has_instances']:
			if self.full_filename is not None:
				self.__template.update_template_from_file(filename = self.full_filename)

		self.__template['external_version'] = self._TCTRL_external_version.GetValue()
		tmp = self._PRW_instance_type.GetValue().strip()
		if tmp not in [self.__template['instance_type'], self.__template['l10n_instance_type']]:
			self.__template['instance_type'] = tmp
		self.__template['filename'] = self._TCTRL_filename.GetValue()
		self.__template['in_use'] = self._CHBOX_active.GetValue()
		self.__template['engine'] = gmForms.form_engine_abbrevs[self._CH_engine.GetSelection()]

		self.__template.save()
		return True
	#--------------------------------------------------------
	# event handlers
	#--------------------------------------------------------
	def _on_load_button_pressed(self, evt):

		engine_abbrev = gmForms.form_engine_abbrevs[self._CH_engine.GetSelection()]

		wildcards = []
		try:
			wildcards.append(u'%s (%s)|%s' % (
				gmForms.form_engine_names[engine_abbrev],
				gmForms.form_engine_template_wildcards[engine_abbrev],
				gmForms.form_engine_template_wildcards[engine_abbrev]
			))
		except KeyError:
			pass

		wildcards.append(u"%s (*)|*" % _('all files'))
		wildcards.append(u"%s (*.*)|*.*" % _('all files (Windows)'))

		dlg = wx.FileDialog (
			parent = self,
			message = _('Choose a form template file'),
			defaultDir = os.path.expanduser(os.path.join('~', 'gnumed')),
			defaultFile = '',
			wildcard = '|'.join(wildcards),
			style = wx.OPEN | wx.HIDE_READONLY | wx.FILE_MUST_EXIST
		)
		result = dlg.ShowModal()
		if result != wx.ID_CANCEL:
			self.full_filename = dlg.GetPath()
			fname = os.path.split(self.full_filename)[1]
			self._TCTRL_filename.SetValue(fname)
		dlg.Destroy()
	#--------------------------------------------------------
	def _on_export_button_pressed(self, event):

		if self.__template is None:
			return

		engine_abbrev = gmForms.form_engine_abbrevs[self._CH_engine.GetSelection()]

		wildcards = []
		try:
			wildcards.append(u'%s (%s)|%s' % (
				gmForms.form_engine_names[engine_abbrev],
				gmForms.form_engine_template_wildcards[engine_abbrev],
				gmForms.form_engine_template_wildcards[engine_abbrev]
			))
		except KeyError:
			pass
		wildcards.append(u"%s (*)|*" % _('all files'))
		wildcards.append(u"%s (*.*)|*.*" % _('all files (Windows)'))

		dlg = wx.FileDialog (
			parent = self,
			message = _('Enter a filename to save the template in'),
			defaultDir = os.path.expanduser(os.path.join('~', 'gnumed')),
			defaultFile = '',
			wildcard = '|'.join(wildcards),
			style = wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT | wx.HIDE_READONLY
		)
		result = dlg.ShowModal()
		if result != wx.ID_CANCEL:
			fname = dlg.GetPath()
			self.__template.export_to_file(filename = fname)

		dlg.Destroy()
#============================================================
class cFormTemplateEditAreaDlg(wxgFormTemplateEditAreaDlg.wxgFormTemplateEditAreaDlg):

	def __init__(self, *args, **kwargs):
		try:
			template = kwargs['template']
			del kwargs['template']
		except KeyError:
			template = None

		wxgFormTemplateEditAreaDlg.wxgFormTemplateEditAreaDlg.__init__(self, *args, **kwargs)

		self._PNL_edit_area.refresh(template=template)
	#--------------------------------------------------------
	def _on_save_button_pressed(self, evt):
		if self._PNL_edit_area.save():
			if self.IsModal():
				self.EndModal(wx.ID_OK)
			else:
				self.Close()
#============================================================
# main
#------------------------------------------------------------
if __name__ == '__main__':

	gmI18N.activate_locale()
	gmI18N.install_domain(domain = 'gnumed')

	#----------------------------------------
	def test_cFormTemplateEditAreaPnl():
		app = wx.PyWidgetTester(size = (400, 300))
		pnl = cFormTemplateEditAreaPnl(app.frame, -1, template = gmForms.cFormTemplate(aPK_obj=4))
		app.frame.Show(True)
		app.MainLoop()
		return
	#----------------------------------------
	if (len(sys.argv) > 1) and (sys.argv[1] == 'test'):
		test_cFormTemplateEditAreaPnl()

#============================================================
