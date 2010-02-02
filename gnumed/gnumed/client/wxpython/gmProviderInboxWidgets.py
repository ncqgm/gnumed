"""GNUmed provider inbox handling widgets.
"""
#================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmProviderInboxWidgets.py,v $
# $Id: gmProviderInboxWidgets.py,v 1.48 2010-02-02 13:56:42 ncq Exp $
__version__ = "$Revision: 1.48 $"
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"

import sys, logging


import wx


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmI18N, gmDispatcher, gmTools, gmCfg, gmPG2, gmExceptions
from Gnumed.business import gmPerson, gmSurgery
from Gnumed.wxpython import gmGuiHelpers, gmListWidgets, gmPlugin, gmRegetMixin, gmPhraseWheel, gmEditArea, gmAuthWidgets, gmPatSearchWidgets
from Gnumed.wxGladeWidgets import wxgProviderInboxPnl, wxgTextExpansionEditAreaPnl


_log = logging.getLogger('gm.ui')
_log.info(__version__)

_indicator = {
	-1: '',
	0: '',
	1: '!'
}
#============================================================
class cTextExpansionEditAreaPnl(wxgTextExpansionEditAreaPnl.wxgTextExpansionEditAreaPnl):

	def __init__(self, *args, **kwds):

		try:
			self.__keyword = kwds['keyword']
			del kwds['keyword']
		except KeyError:
			self.__keyword = None

		wxgTextExpansionEditAreaPnl.wxgTextExpansionEditAreaPnl.__init__(self, *args, **kwds)

		self.__init_ui()
		self.__register_interests()
	#--------------------------------------------------------
	def save(self):
		if not self.__valid_for_save():
			return False

		if self.__keyword is None:
			result = gmPG2.add_text_expansion (
				keyword = self._TCTRL_keyword.GetValue().strip(),
				expansion = self._TCTRL_expansion.GetValue(),
				public = self._RBTN_public.GetValue()
			)
		else:
			gmPG2.edit_text_expansion (
				keyword = self._TCTRL_keyword.GetValue().strip(),
				expansion = self._TCTRL_expansion.GetValue()
			)
			result = True

		return result
	#--------------------------------------------------------
	def refresh(self):
		self.__init_ui()
#		if self.__keyword is not None:
#			self._TCTRL_expansion.SetValue(u'')
	#--------------------------------------------------------
	# event handling
	#--------------------------------------------------------
	def __register_interests(self):
		self._TCTRL_keyword.Bind(wx.EVT_TEXT, self._on_keyword_modified)
	#--------------------------------------------------------
	def _on_keyword_modified(self, evt):
		if self._TCTRL_keyword.GetValue().strip() == u'':
			self._TCTRL_expansion.Enable(False)
		else:
			self._TCTRL_expansion.Enable(True)
	#--------------------------------------------------------
	# internal API
	#--------------------------------------------------------
	def __valid_for_save(self):

		kwd = self._TCTRL_keyword.GetValue().strip()
		if kwd == u'':
			self._TCTRL_keyword.SetBackgroundColour('pink')
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot save text expansion without keyword.'), beep = True)
			return False
		self._TCTRL_keyword.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))

		if self._TCTRL_expansion.GetValue().strip() == u'':
			self._TCTRL_expansion.SetBackgroundColour('pink')
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot save text expansion without expansion text.'), beep = True)
			return False
		self._TCTRL_expansion.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))

		return True
	#--------------------------------------------------------
	def __init_ui(self, keyword=None):

		if keyword is not None:
			self.__keyword = keyword

		if self.__keyword is None:
			self._TCTRL_keyword.SetValue(u'')
			self._TCTRL_keyword.Enable(True)
			self._TCTRL_expansion.SetValue(u'')
			self._TCTRL_expansion.Enable(False)
			self._RBTN_public.Enable(True)
			self._RBTN_private.Enable(True)
			self._RBTN_public.SetValue(1)
		else:
			expansion = gmPG2.expand_keyword(keyword = self.__keyword)
			self._TCTRL_keyword.SetValue(self.__keyword)
			self._TCTRL_keyword.Enable(False)
			self._TCTRL_expansion.SetValue(gmTools.coalesce(expansion, u''))
			self._TCTRL_expansion.Enable(True)
			self._RBTN_public.Enable(False)
			self._RBTN_private.Enable(False)
#============================================================
def configure_keyword_text_expansion(parent=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	#----------------------
	def delete(keyword=None):
		gmPG2.delete_text_expansion(keyword = keyword)
		return True
	#----------------------
	def edit(keyword=None):
		# add new keyword
		ea = cTextExpansionEditAreaPnl(parent, -1, keyword=keyword)
		dlg = gmEditArea.cGenericEditAreaDlg(parent, -1, edit_area = ea)
		dlg.SetTitle (
			gmTools.coalesce(keyword, _('Adding text expansion'), _('Editing text expansion "%s"'))
		)
		if dlg.ShowModal() == wx.ID_OK:
			return True

		return False
	#----------------------
	def refresh(lctrl=None):
		kwds = [ [
				r[0],
				gmTools.bool2subst(r[1], gmTools.u_checkmark_thick, u''),
				gmTools.bool2subst(r[2], gmTools.u_checkmark_thick, u''),
				r[3]
			] for r in gmPG2.get_text_expansion_keywords()
		]
		data = [ r[0] for r in gmPG2.get_text_expansion_keywords() ]
		lctrl.set_string_items(kwds)
		lctrl.set_data(data)
	#----------------------

	gmListWidgets.get_choices_from_list (
		parent = parent,
		msg = _('\nSelect the keyword you want to edit !\n'),
		caption = _('Editing keyword-based text expansions ...'),
		columns = [_('Keyword'), _('Public'), _('Private'), _('Owner')],
		single_selection = True,
		edit_callback = edit,
		new_callback = edit,
		delete_callback = delete,
		refresh_callback = refresh
	)
#============================================================
class cProviderPhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):

		gmPhraseWheel.cPhraseWheel.__init__ (
			self,
			*args,
			**kwargs
		)
		self.matcher = gmPerson.cMatchProvider_Provider()
		self.SetToolTipString(_('Select a healthcare provider.'))
		self.selection_only = True
#============================================================
# practice related widgets 
#============================================================
# FIXME: this should be moved elsewhere !
def configure_workplace_plugins(parent=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	#-----------------------------------
	def delete(workplace):

		curr_workplace = gmSurgery.gmCurrentPractice().active_workplace
		if workplace == curr_workplace:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot delete the active workplace.'), beep = True)
			return False

		dlg = gmGuiHelpers.c2ButtonQuestionDlg (
			parent,
			-1,
			caption = _('Deleting workplace ...'),
			question = _('Are you sure you want to delete this workplace ?\n\n "%s"\n') % workplace,
			show_checkbox = True,
			checkbox_msg = _('delete configuration, too'),
			checkbox_tooltip = _(
				'Check this if you want to delete all configuration items\n'
				'for this workplace along with the workplace itself.'
			),
			button_defs = [
				{'label': _('Delete'), 'tooltip': _('Yes, delete this workplace.'), 'default': True},
				{'label': _('Do NOT delete'), 'tooltip': _('No, do NOT delete this workplace'), 'default': False}
			]
		)

		decision = dlg.ShowModal()
		if decision != wx.ID_YES:
			dlg.Destroy()
			return False

		include_cfg = dlg.checkbox_is_checked()
		dlg.Destroy()

		dbo_conn = gmAuthWidgets.get_dbowner_connection(procedure = _('delete workplace'))
		if not dbo_conn:
			return False

		gmSurgery.delete_workplace(workplace = workplace, conn = dbo_conn, delete_config = include_cfg)
		return True
	#-----------------------------------
	def edit(workplace=None):

		available_plugins = gmPlugin.get_installed_plugins(plugin_dir='gui')

		dbcfg = gmCfg.cCfgSQL()

		if workplace is None:
			dlg = wx.TextEntryDialog (
				parent = parent,
				message = _('Enter a descriptive name for the new workplace:'),
				caption = _('Configuring GNUmed workplaces ...'),
				defaultValue = u'',
				style = wx.OK | wx.CENTRE
			)
			dlg.ShowModal()
			workplace = dlg.GetValue().strip()
			if workplace == u'':
				gmGuiHelpers.gm_show_error(_('Cannot save a new workplace without a name.'), _('Configuring GNUmed workplaces ...'))
				return False
			curr_plugins = []
			choices = available_plugins
		else:
			curr_plugins = gmTools.coalesce(dbcfg.get2 (
				option = u'horstspace.notebook.plugin_load_order',
				workplace = workplace,
				bias = 'workplace'
				), []
			)
			choices = curr_plugins[:]
			for p in available_plugins:
				if p not in choices:
					choices.append(p)

		sels = range(len(curr_plugins))
		new_plugins = gmListWidgets.get_choices_from_list (
			parent = parent,
			msg = _(
				'\n'
				'Select the plugin(s) to be loaded the next time\n'
				'the client is restarted under the workplace:\n'
				'\n'
				' [%s]'
				'\n'
			) % workplace,
			caption = _('Configuring GNUmed workplaces ...'),
			choices = choices,
			selections = sels,
			columns = [_('Plugins')],
			single_selection = False
		)

		if new_plugins == curr_plugins:
			return True

		if new_plugins is None:
			return True

		dbcfg.set (
			option = u'horstspace.notebook.plugin_load_order',
			value = new_plugins,
			workplace = workplace
		)

		return True
	#-----------------------------------
	def refresh(lctrl):
		workplaces = gmSurgery.gmCurrentPractice().workplaces
		curr_workplace = gmSurgery.gmCurrentPractice().active_workplace
		try:
			sels = [workplaces.index(curr_workplace)]
		except ValueError:
			sels = []

		lctrl.set_string_items(workplaces)
		lctrl.set_selections(selections = sels)
	#-----------------------------------
	gmListWidgets.get_choices_from_list (
		parent = parent,
		msg = _(
			'\nSelect the workplace to configure below.\n'
			'\n'
			'The currently active workplace is preselected.\n'
		),
		caption = _('Configuring GNUmed workplaces ...'),
		columns = [_('Workplace')],
		single_selection = True,
		refresh_callback = refresh,
		edit_callback = edit,
		new_callback = edit,
		delete_callback = delete
	)
#============================================================
class cProviderInboxPnl(wxgProviderInboxPnl.wxgProviderInboxPnl, gmRegetMixin.cRegetOnPaintMixin):

	_item_handlers = {}
	_patient_msg_types = ['clinical.review docs', 'clinical.review results']
	#--------------------------------------------------------
	def __init__(self, *args, **kwds):

		wxgProviderInboxPnl.wxgProviderInboxPnl.__init__(self, *args, **kwds)
		gmRegetMixin.cRegetOnPaintMixin.__init__(self)

		self.provider = gmPerson.gmCurrentProvider()
		self.filter_mode = 'all'
		self.__init_ui()

		cProviderInboxPnl._item_handlers['clinical.review docs'] = self._goto_doc_review
		cProviderInboxPnl._item_handlers['clinical.review results'] = self._goto_measurements_review

		self.__register_interests()
	#--------------------------------------------------------
	# reget-on-paint API
	#--------------------------------------------------------
	def _populate_with_data(self):
		self.__populate_inbox()
		return True
	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def __register_interests(self):
		gmDispatcher.connect(signal = u'message_inbox_generic_mod_db', receiver = self._on_message_inbox_mod_db)
		gmDispatcher.connect(signal = u'message_inbox_mod_db', receiver = self._on_message_inbox_mod_db)
		# FIXME: listen for results insertion/deletion
		gmDispatcher.connect(signal = u'reviewed_test_results_mod_db', receiver = self._on_message_inbox_mod_db)
		# FIXME: listen for doc insertion/deletion
		# FIXME: listen for doc reviews
		gmDispatcher.connect(signal = u'post_patient_selection', receiver = self._on_post_patient_selection)
	#--------------------------------------------------------
	def __init_ui(self):
		self._LCTRL_provider_inbox.set_columns([u'', _('date'), _('category'), _('type'), _('message')])

		msg = _('\n Inbox of %(title)s %(lname)s.\n') % {
			'title': gmTools.coalesce (
				self.provider['title'],
				gmPerson.map_gender2salutation(self.provider['gender'])
			),
			'lname': self.provider['lastnames']
		}

		self._msg_welcome.SetLabel(msg)

		if gmPerson.gmCurrentPatient().connected:
			self._RBTN_active_patient.Enable()
	#--------------------------------------------------------
	def __populate_inbox(self):

		"""Fill UI with data."""
		self.__msgs = self.provider.inbox.messages

		if self.filter_mode == 'active':
			if gmPerson.gmCurrentPatient().connected:
				curr_pat_id = gmPerson.gmCurrentPatient().ID
				self.__msgs = [ m for m in self.__msgs if m['pk_patient'] == curr_pat_id ]
			else:
				self.__msgs = []

		items = [
			[
				_indicator[m['importance']],
				m['received_when'].strftime('%Y-%m-%d'),
				m['l10n_category'],
				m['l10n_type'],
				m['comment']
			] for m in self.__msgs
		]
		self._LCTRL_provider_inbox.set_string_items(items = items)
		self._LCTRL_provider_inbox.set_data(data = self.__msgs)
		self._LCTRL_provider_inbox.set_column_widths()
	#--------------------------------------------------------
	# event handlers
	#--------------------------------------------------------
	def _on_post_patient_selection(self):
		wx.CallAfter(self._schedule_data_reget)
		wx.CallAfter(self._RBTN_active_patient.Enable)
	#--------------------------------------------------------
	def _on_message_inbox_mod_db(self, *args, **kwargs):
		wx.CallAfter(self._schedule_data_reget)
		gmDispatcher.send(signal = u'request_user_attention', msg = _('Please check your GNUmed Inbox !'))
	#--------------------------------------------------------
	def _lst_item_activated(self, evt):
		msg = self._LCTRL_provider_inbox.get_selected_item_data(only_one = True)
		if msg is None:
			return

		handler_key = '%s.%s' % (msg['category'], msg['type'])
		try:
			handle_item = cProviderInboxPnl._item_handlers[handler_key]
		except KeyError:
			gmGuiHelpers.gm_show_warning (
				_(
"""No double-click action pre-programmed into
GNUmed for message category and type:

 [%s]
"""
) % handler_key,
				_('handling provider inbox item')
			)
			return False

		if not handle_item(pk_context = msg['pk_context'], pk_patient = msg['pk_patient']):
			_log.error('item handler returned "false"')
			_log.error('handler key: [%s]', handler_key)
			_log.error('message: %s', str(msg))
			return False

		return True
	#--------------------------------------------------------
	def _lst_item_focused(self, evt):
		pass
	#--------------------------------------------------------
	def _lst_item_selected(self, evt):
		msg = self._LCTRL_provider_inbox.get_selected_item_data(only_one = True)
		if msg is None:
			return

		if msg['data'] is None:
			tmp = _('Message: %s') % msg['comment']
		else:
			tmp = _('Message: %s\nData: %s') % (msg['comment'], msg['data'])

		self._TXT_inbox_item_comment.SetValue(tmp)
	#--------------------------------------------------------
	def _lst_item_right_clicked(self, evt):
		tmp = self._LCTRL_provider_inbox.get_selected_item_data(only_one = True)
		if tmp is None:
			return
		self.__focussed_msg = tmp

		# build menu
		menu = wx.Menu(title = _('Inbox Message menu'))
		# - delete message
		if not self.__focussed_msg['is_virtual']:
			ID = wx.NewId()
			menu.AppendItem(wx.MenuItem(menu, ID, _('delete message')))
			wx.EVT_MENU(menu, ID, self._on_delete_focussed_msg)

		# show menu
		self.PopupMenu(menu, wx.DefaultPosition)
		menu.Destroy()
	#--------------------------------------------------------
	def _on_all_messages_radiobutton_selected(self, event):
		self.filter_mode = 'all'
		self._TXT_inbox_item_comment.SetValue(u'')
		self.__populate_inbox()
	#--------------------------------------------------------
	def _on_active_patient_radiobutton_selected(self, event):
		self.filter_mode = 'active'
		self._TXT_inbox_item_comment.SetValue(u'')
		self.__populate_inbox()
	#--------------------------------------------------------
	# item handlers
	#--------------------------------------------------------
	def _on_delete_focussed_msg(self, evt):
		if self.__focussed_msg['is_virtual']:
			gmDispatcher.send(signal = 'statustext', msg = _('You must deal with the reason for this message to remove it from your inbox.'), beep = True)
			return False

		if not self.provider.inbox.delete_message(self.__focussed_msg['pk_message_inbox']):
			gmDispatcher.send(signal='statustext', msg=_('Problem removing message from Inbox.'))
			return False
		return True
	#--------------------------------------------------------
	def _goto_doc_review(self, pk_context=None, pk_patient=None):
		wx.BeginBusyCursor()

		try:
			pat = gmPerson.cIdentity(aPK_obj = pk_patient)
		except gmExceptions.ConstructorError:
			wx.EndBusyCursor()
			_log.exception('patient [%s] not found', pk_patient)
			gmGuiHelpers.gm_show_error (
				_('Supposedly there are unreviewed documents\n'
				  'for patient [%s]. However, I cannot find\n'
				  'that patient in the GNUmed database.'
				) % pk_patient,
				_('handling provider inbox item')
			)
			return False

		success = gmPatSearchWidgets.set_active_patient(patient = pat)

		wx.EndBusyCursor()

		if not success:
			gmGuiHelpers.gm_show_error (
				_('Supposedly there are unreviewed documents\n'
				  'for patient [%s]. However, I cannot find\n'
				  'that patient in the GNUmed database.'
				) % pk_patient,
				_('handling provider inbox item')
			)
			return False

		wx.CallAfter(gmDispatcher.send, signal = 'display_widget', name = 'gmShowMedDocs', sort_mode = 'review')
		return True
	#--------------------------------------------------------
	def _goto_measurements_review(self, pk_context=None, pk_patient=None):
		wx.BeginBusyCursor()
		success = gmPatSearchWidgets.set_active_patient(patient=gmPerson.cIdentity(aPK_obj=pk_patient))
		wx.EndBusyCursor()
		if not success:
			gmGuiHelpers.gm_show_error (
				_('Supposedly there are unreviewed results\n'
				  'for patient [%s]. However, I cannot find\n'
				  'that patient in the GNUmed database.'
				) % pk_patient,
				_('handling provider inbox item')
			)
			return False

		wx.CallAfter(gmDispatcher.send, signal = 'display_widget', name = 'gmMeasurementsGridPlugin')
		return True	
#============================================================
if __name__ == '__main__':

	gmI18N.activate_locale()
	gmI18N.install_domain(domain = 'gnumed')

	def test_configure_wp_plugins():
		app = wx.PyWidgetTester(size = (400, 300))
		configure_workplace_plugins()

	def test_message_inbox():
		app = wx.PyWidgetTester(size = (800, 600))
		app.SetWidget(cProviderInboxPnl, -1)
		app.MainLoop()

	if len(sys.argv) > 1 and sys.argv[1] == 'test':
		#test_configure_wp_plugins()
		test_message_inbox()

#============================================================
# $Log: gmProviderInboxWidgets.py,v $
# Revision 1.48  2010-02-02 13:56:42  ncq
# - text expansion management typo fix
#
# Revision 1.47  2010/01/10 17:29:26  ncq
# - slightly postpone plugin raising after message double-clicking
#   to avoid async problems with patient activation plugin raising
#
# Revision 1.46  2010/01/06 14:43:55  ncq
# - inbox title flush left
#
# Revision 1.45  2009/11/30 22:27:57  ncq
# - adjust provider inbox filters
#
# Revision 1.44  2009/11/30 13:16:27  ncq
# - no deletion of .is_virtual messages
# - data update after patient activation
# - enabling active-patient filter on init, too
#
# Revision 1.43  2009/11/29 13:07:15  ncq
# - properly map messages to check boxes as per list
#
# Revision 1.42  2009/11/28 20:07:08  ncq
# - fix message detail display
#
# Revision 1.41  2009/08/24 20:11:27  ncq
# - bump db version
# - fix tag creation
# - provider inbox:
# 	enable filter-to-active-patient,
# 	listen to new signal,
# 	use cInboxMessage class
# - properly constrain LOINC phrasewheel SQL
# - include v12 scripts in release
# - install arriba jar to /usr/local/bin/
# - check for table existence in audit schema generator
# - include dem.message inbox with additional generic signals
#
# Revision 1.40  2009/07/01 17:12:11  ncq
# - better wording
#
# Revision 1.39  2009/06/29 15:10:58  ncq
# - prevent deletion of the active workplace
#
# Revision 1.38  2009/06/22 09:28:21  ncq
# - improved wording as per list
#
# Revision 1.37  2009/06/20 12:47:38  ncq
# - test
#
# Revision 1.36  2009/06/11 12:37:25  ncq
# - much simplified initial setup of list ctrls
#
# Revision 1.35  2009/06/04 16:30:30  ncq
# - use set active patient from pat search widgets
#
# Revision 1.34  2009/05/18 15:32:42  ncq
# - add deleting workplaces
#
# Revision 1.33  2009/02/18 13:47:43  ncq
# - do not throw exception in _goto_doc_review if patient
#   does not exist, rather report error
#
# Revision 1.32  2009/01/17 23:09:30  ncq
# - cleanup
#
# Revision 1.31  2008/10/22 12:21:57  ncq
# - use %x in strftime where appropriate
#
# Revision 1.30  2008/09/04 12:52:23  ncq
# - display received_when for incoming messages
#
# Revision 1.29  2008/07/13 16:14:59  ncq
# - implement keyword based text expansion widgets
#
# Revision 1.28  2008/06/09 15:36:58  ncq
# - provider phrasewheel
#
# Revision 1.27  2008/05/20 16:45:43  ncq
# - add filter for active patient messages
# - fix longstanding bug updating display on *every* PAINT event
#
# Revision 1.26  2008/04/22 21:19:22  ncq
# - signal busy-ness when activating patient
#
# Revision 1.25  2008/03/29 16:21:16  ncq
# - handle unreviewed tests messages
# - listen to review changes
#
# Revision 1.24  2008/03/05 22:30:14  ncq
# - new style logging
#
# Revision 1.23  2008/02/25 17:40:45  ncq
# - establish db cfg instance early enough
#
# Revision 1.22  2008/01/30 14:03:42  ncq
# - use signal names directly
# - switch to std lib logging
#
# Revision 1.21  2008/01/27 21:18:45  ncq
# - don't crash on trying to edit module-less workplace
#
# Revision 1.20  2008/01/05 16:41:27  ncq
# - remove logging from gm_show_*()
#
# Revision 1.19  2007/11/28 11:56:30  ncq
# - better logging
#
# Revision 1.18  2007/11/23 23:36:38  ncq
# - finish configure_workplace_plugins()
#
# Revision 1.17  2007/11/02 13:59:33  ncq
# - request user attention when new item arrives
#
# Revision 1.16  2007/10/30 12:51:45  ncq
# - make it a reget mixin child
# - cleanup
# - listen on backend changes
#
# Revision 1.15  2007/10/08 13:05:10  ncq
# - use gmListWidgets.cReportListCtrl
# - fix right-click on empty message list crashes
# - start test suite
# - start configure_workplace_plugins()
#
# Revision 1.14  2007/08/12 00:12:41  ncq
# - no more gmSignals.py
#
# Revision 1.13  2007/05/14 13:11:25  ncq
# - use statustext() signal
#
# Revision 1.12  2007/01/04 22:52:34  ncq
# - show proper salutation for people without title
#
# Revision 1.11  2006/12/17 20:46:24  ncq
# - cleanup
#
# Revision 1.10  2006/11/24 10:01:31  ncq
# - gm_beep_statustext() -> gm_statustext()
#
# Revision 1.9  2006/05/28 16:19:54  ncq
# - repopulate_ui() needed for receive_focus() from plugin base class
#
# Revision 1.8  2006/05/20 18:55:21  ncq
# - calculate handler via original category/type not i18ned one
#
# Revision 1.7  2006/05/16 15:56:03  ncq
# - properly resize columns
#
# Revision 1.6  2006/05/15 14:46:38  ncq
# - implement message deletion via context menu popup
#
# Revision 1.5  2006/05/15 13:39:31  ncq
# - cleanup
#
# Revision 1.4  2006/05/12 22:04:22  ncq
# - add _populate_with_data()
# - fully implement _goto_doc_review()
#
# Revision 1.3  2006/05/12 12:21:58  ncq
# - implement double-click item handling
# - use gmCurrentProvider
# - show message on item focused
#
# Revision 1.2  2006/01/22 18:10:52  ncq
# - now really display messages from backend
#
# Revision 1.1  2006/01/15 14:30:56  ncq
# - first crude cut at this
#
#