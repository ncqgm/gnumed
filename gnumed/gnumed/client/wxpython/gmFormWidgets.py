"""GNUmed form/letter handling widgets.
"""
#================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmFormWidgets.py,v $
# $Id: gmFormWidgets.py,v 1.7 2007-11-10 20:57:04 ncq Exp $
__version__ = "$Revision: 1.7 $"
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"

import os.path, sys


import wx


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmLog, gmI18N, gmTools, gmDispatcher
from Gnumed.business import gmForms
from Gnumed.wxpython import gmGuiHelpers, gmListWidgets, gmMacro
from Gnumed.wxGladeWidgets import wxgFormTemplateEditAreaPnl, wxgFormTemplateEditAreaDlg


_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)

#============================================================
# convenience functions
#============================================================
def let_user_select_form_template(parent=None):

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
		templates = gmForms.get_form_templates(engine = gmForms.engine_ooo, active_only = False)
		lctrl.set_string_items(items = [ [t['name_long'], t['external_version'], gmForms.engine_names[t['engine']]] for t in templates ])
		lctrl.set_data(data = templates)
	#-------------------------
	templates = gmForms.get_form_templates(engine = gmForms.engine_ooo, active_only = False)
	template = gmListWidgets.get_choices_from_list (
		parent = parent,
		caption = _('Select letter or form template.'),
		choices = [ [t['name_long'], t['external_version'], gmForms.engine_names[t['engine']]] for t in templates ],
		columns = [_('Template'), _('Version'), _('Type')],
		data = templates,
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
	template = let_user_select_form_template(parent = parent)
	if template is None:
		return

	# 2) export template to file
	filename = template.export_to_file()
	if filename is None:
		gmGuiHelpers.gm_show_error (
			_(	'Error exporting form template\n'
				'\n'
				' "%s" (%s)'
			) % (template['name_long'], template['external_version']),
			_('Letter template export')
		)
		return

	doc = gmForms.cOOoLetter(template_file = filename, instance_type = template['instance_type'])
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
		return

	doc.show(False)
	ph_handler = gmMacro.gmPlaceholderHandler()
	doc.replace_placeholders(handler = ph_handler)
	filename = filename.replace('.ott', '.odt').replace('-FormTemplate-', '-FormInstance-')
	doc.save_in_ooo(filename = filename)
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
			# FIXME: add engine handling
			self._CHBOX_active.SetValue(True)
			
			self._TCTRL_date_modified.SetValue(u'')
			self._TCTRL_modified_by.SetValue(u'')

		else:
			self._PRW_name_long.SetText(self.__template['name_long'])
			self._PRW_name_short.SetText(self.__template['name_short'])
			self._TCTRL_external_version.SetValue(self.__template['external_version'])
			self._PRW_template_type.SetText(self.__template['l10n_template_type'], data = self.__template['pk_template_type'])
			self._PRW_instance_type.SetText(self.__template['l10n_instance_type'], data = self.__template['instance_type'])
			self._TCTRL_filename.SetValue(self.__template['filename'])
			# FIXME: add engine handling
			self._CHBOX_active.SetValue(self.__template['in_use'])
			
			self._TCTRL_date_modified.SetValue(self.__template['last_modified'].strftime('%x'))
			self._TCTRL_modified_by.SetValue(self.__template['modified_by'])

			self._TCTRL_filename.Enable(True)
			self._BTN_load.Enable(not self.__template['has_instances'])

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

		self.__template.save_payload()
		return True
	#--------------------------------------------------------
	# event handlers
	#--------------------------------------------------------
	def _on_load_button_pressed(self, evt):
		dlg = wx.FileDialog (
			parent = self,
			message = _('Choose a form template file'),
			defaultDir = os.path.expanduser(os.path.join('~', 'gnumed')),
			defaultFile = '',
			wildcard = "%s (*.ott)|*.ott|%s (*)|*|%s (*.*)|*.*" % (_('OOo templates'), _('all files'), _('all files (Win)')),
			style = wx.OPEN | wx.HIDE_READONLY | wx.FILE_MUST_EXIST
		)
		result = dlg.ShowModal()
		if result != wx.ID_CANCEL:
			self.full_filename = dlg.GetPath()
			fname = os.path.split(self.full_filename)[1]
			self._TCTRL_filename.SetValue(fname)
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
	_log.SetAllLogLevels(gmLog.lData)
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
# $Log: gmFormWidgets.py,v $
# Revision 1.7  2007-11-10 20:57:04  ncq
# - handle failing OOo connection
# - cleanup leftover templates on failure
#
# Revision 1.6  2007/09/16 22:40:15  ncq
# - allow editing templates when there are no instances
#
# Revision 1.5  2007/09/10 18:40:19  ncq
# - allow setting data on existing templates if it hasn't been set before
#
# Revision 1.4  2007/09/02 20:57:28  ncq
# - improve edit/delete callbacks
# - add refresh callback
#
# Revision 1.3  2007/09/01 23:33:04  ncq
# - implement save()/delete on form templates
#
# Revision 1.2  2007/08/29 14:38:55  ncq
# - remove spurious ,
#
# Revision 1.1  2007/08/28 14:40:12  ncq
# - factored out from gmMedDocWidgets.py
#
#


#============================================================
# Log: gmMedDocWidgets.py
# Revision 1.142  2007/08/28 14:18:13  ncq
# - no more gm_statustext()
