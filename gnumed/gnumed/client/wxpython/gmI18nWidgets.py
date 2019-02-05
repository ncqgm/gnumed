"""GNUmed I18n/L10n related widgets.
"""
#================================================================
__author__ = 'karsten.hilbert@gmx.net'
__license__ = 'GPL v2 or later (details at http://www.gnu.org)'

# stdlib
import logging
import sys


# 3rd party
import wx


# GNUmed
if __name__ == '__main__':
	sys.path.insert(0, '../../')

from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmNetworkTools
from Gnumed.pycommon import gmPG2
from Gnumed.pycommon import gmI18N
from Gnumed.pycommon import gmDispatcher


from Gnumed.wxpython import gmListWidgets
from Gnumed.wxpython import gmEditArea
from Gnumed.wxpython import gmPhraseWheel
from Gnumed.wxpython import gmGuiHelpers
from Gnumed.wxpython import gmAuthWidgets


_log = logging.getLogger('gm.ui')

#==============================================================================
from Gnumed.wxGladeWidgets import wxgDatabaseTranslationEAPnl

class cDatabaseTranslationEAPnl(wxgDatabaseTranslationEAPnl.wxgDatabaseTranslationEAPnl, gmEditArea.cGenericEditAreaMixin):

	def __init__(self, *args, **kwargs):

		try:
			data = kwargs['translation']
			del kwargs['translation']
		except KeyError:
			data = None

		wxgDatabaseTranslationEAPnl.wxgDatabaseTranslationEAPnl.__init__(self, *args, **kwargs)
		gmEditArea.cGenericEditAreaMixin.__init__(self)

		# Code using this mixin should set mode and data
		# after instantiating the class:
		self.mode = 'new'
		self.data = data
		if data is not None:
			self.mode = 'edit'

		#self.__init_ui()
	#----------------------------------------------------------------
#	def __init_ui(self):
#		# adjust phrasewheels etc
	#----------------------------------------------------------------
	# generic Edit Area mixin API
	#----------------------------------------------------------------
	def _valid_for_save(self):

		fields = [self._TCTRL_original, self._TCTRL_translation, self._TCTRL_language]

		has_errors = False
		for field in fields:
			if field.GetValue().strip() == '':
				has_errors = True
				field.SetBackgroundColour(gmPhraseWheel.color_prw_invalid)
				field.SetFocus()
			else:
				field.SetBackgroundColour(gmPhraseWheel.color_prw_valid)

		return (has_errors is False)
	#----------------------------------------------------------------
	def _save_as_new(self):
		self.data = gmPG2.update_translation_in_database (
			language = self._TCTRL_language.GetValue().strip(),
			original = self._TCTRL_original.GetValue().strip(),
			translation = self._TCTRL_translation.GetValue().strip()
		)
		return True
	#----------------------------------------------------------------
	def _save_as_update(self):
		return self._save_as_new()
	#----------------------------------------------------------------
	def _refresh_as_new(self):
		self._TCTRL_original.SetValue('')
		self._TCTRL_original.SetEditable(True)
		self._TCTRL_translation.SetValue('')
		self._TCTRL_language.SetValue('')
		self._TCTRL_original.SetFocus()
	#----------------------------------------------------------------
	def _refresh_from_existing(self):
		self._TCTRL_original.SetValue(self.data['orig'])
		self._TCTRL_original.SetEditable(False)
		self._TCTRL_translation.SetValue(gmTools.coalesce(self.data['trans']))
		self._TCTRL_language.SetValue(gmTools.coalesce(self.data['lang']))
		self._TCTRL_translation.SetFocus()
	#----------------------------------------------------------------
	def _refresh_as_new_from_existing(self):
		self._TCTRL_original.SetValue(self.data['orig'])
		self._TCTRL_original.SetEditable(False)
		self._TCTRL_translation.SetValue('')
		self._TCTRL_language.SetValue('')
		self._TCTRL_translation.SetFocus()
	#----------------------------------------------------------------

#------------------------------------------------------------------------------
def edit_translation(parent=None, translation=None, single_entry=False):
	ea = cDatabaseTranslationEAPnl(parent, -1)
	ea.data = translation
	ea.mode = gmTools.coalesce(translation, 'new', 'edit')
	dlg = gmEditArea.cGenericEditAreaDlg2(parent, -1, edit_area = ea, single_entry = single_entry)
	dlg.SetTitle(gmTools.coalesce(translation, _('Adding new translation'), _('Editing translation')))
	if dlg.ShowModal() == wx.ID_OK:
		dlg.DestroyLater()
		return True
	dlg.DestroyLater()
	return False

#------------------------------------------------------------------------------
def manage_translations(parent=None, language=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	if language is None:
		langs = gmPG2.get_translation_languages()
		for lang in [gmI18N.system_locale_level['language'], gmI18N.system_locale_level['country']]:
			if lang not in langs:
				langs.append(lang)

		curr_lang = gmPG2.get_current_user_language()
		try:
			selections = [langs.index(curr_lang)]
		except ValueError:
			selections = None

		language = gmListWidgets.get_choices_from_list (
			parent = parent,
			caption = _('Selecting language for translation'),
			msg = _('Please select the language the translations for which you want to work on.'),
			single_selection = True,
			can_return_empty = False,
			columns = [_('Language')],
			choices = langs,
			selections = selections
		)
	#---------------------------------------------------------------------
	def refresh(lctrl):
		txs = gmPG2.get_database_translations(language = language, order_by = 'orig, lang')
		items = [ [
			tx['orig'],
			gmTools.coalesce(tx['lang'], ''),
			gmTools.coalesce(tx['trans'], '')
		] for tx in txs ]
		lctrl.set_string_items(items)
		lctrl.set_data(txs)
	#---------------------------------------------------------------------
	def edit(translation=None):
		return edit_translation(parent = parent, translation = translation, single_entry = True)
	#---------------------------------------------------------------------
	def delete(translation=None):
		msg = _(
			'Are you sure you want to delete the translation of:\n'
			'\n'
			'%s\n'
			'\n'
			'into [%s] as:\n'
			'\n'
			'%s\n'
			'\n'
			'?  (Note that you must know the database administrator password !)\n'
		) % (
			gmTools.wrap (
				text = translation['orig'],
				width = 60,
				initial_indent = '  ',
				subsequent_indent = '  '
			),
			translation['lang'],
			gmTools.wrap (
				text = translation['trans'],
				width = 60,
				initial_indent = '  ',
				subsequent_indent = '  '
			)
		)
		delete_it = gmGuiHelpers.gm_show_question (
			aTitle = _('Deleting translation from database'),
			aMessage = msg
		)
		if not delete_it:
			return False

		conn = gmAuthWidgets.get_dbowner_connection(procedure = _('deleting a translation'))
		if conn is None:
			return False

		return gmPG2.delete_translation_from_database(link_obj = conn, language = translation['lang'], original = translation['orig'])
	#---------------------------------------------------------------------
	def contribute_translations(item=None):

		do_it = gmGuiHelpers.gm_show_question (
			aTitle = _('Contributing translations'),
			aMessage = _('Do you want to contribute your translations to the GNUmed project ?')
		)
		if not do_it:
			return False

		fname = gmTools.get_unique_filename(prefix = 'gm-db-translations-', suffix = '.sql')
		gmPG2.export_translations_from_database(filename = fname)

		msg = (
			'These are database string translations contributed by a GNUmed user.\n'
			'\n'
			'\tThe GNUmed "%s" Client'
		) % gmI18N.system_locale

		if not gmNetworkTools.compose_and_send_email (
			auth = {'user': gmNetworkTools.default_mail_sender, 'password': 'gnumed-at-gmx-net'},
			sender = 'GNUmed Client <gnumed@gmx.net>',
			receiver = ['gnumed-bugs@gnu.org'],
			subject = '<contribution>: database translation',
			message = msg,
			attachments = [[fname, 'text/plain', 'quoted-printable']]
		):
			gmDispatcher.send(signal = 'statustext', msg = _('Unable to send mail. Cannot contribute translations to GNUmed community.') % report, beep = True)
			return False

		gmDispatcher.send(signal = 'statustext', msg = _('Thank you for your contribution to the GNUmed community!'), beep = True)
		return True
	#---------------------------------------------------------------------
	if language is None:
		caption = _('Showing translatable database strings for all languages.')
	else:
		caption = _('Showing translatable database strings for target language [%s].') % language
	gmListWidgets.get_choices_from_list (
		parent = parent,
		caption = caption,
		columns = [ _('String'), _('Language'), _('Translation') ],
		single_selection = True,
		can_return_empty = False,
		refresh_callback = refresh,
		edit_callback = edit,
		new_callback = edit,
		delete_callback = delete,
		right_extra_button = (_('Contribute'), _('Contribute translations to GNUmed community by email.'), contribute_translations),
		ignore_OK_button = True
	)

#================================================================
if __name__ == '__main__':

	gmI18N.activate_locale()
	gmI18N.install_domain()

	if (len(sys.argv) > 1):
		if sys.argv[1] == 'test':
			pass

#================================================================
