# -*- coding: utf-8 -*-
#============================================================


__doc__ = """GNUmed medical document handling widgets."""

__license__ = "GPL v2 or later"
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"

#============================================================
import os.path
import os
import sys
import re as regex
import logging
import datetime as pydt


import wx
import wx.lib.mixins.treemixin as treemixin


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmI18N
if __name__ == '__main__':
	gmI18N.activate_locale()
	gmI18N.install_domain(domain = 'gnumed')
from Gnumed.pycommon import gmCfg
from Gnumed.pycommon import gmCfg2
from Gnumed.pycommon import gmPG2
from Gnumed.pycommon import gmMimeLib
from Gnumed.pycommon import gmMatchProvider
from Gnumed.pycommon import gmDispatcher
from Gnumed.pycommon import gmDateTime
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmShellAPI
from Gnumed.pycommon import gmHooks
from Gnumed.pycommon import gmNetworkTools
from Gnumed.pycommon import gmMimeLib
from Gnumed.pycommon import gmConnectionPool

from Gnumed.business import gmPerson
from Gnumed.business import gmStaff
from Gnumed.business import gmDocuments
from Gnumed.business import gmEMRStructItems
from Gnumed.business import gmPraxis
from Gnumed.business import gmDICOM
from Gnumed.business import gmProviderInbox
from Gnumed.business import gmOrganization

from Gnumed.wxpython import gmGuiHelpers
from Gnumed.wxpython import gmRegetMixin
from Gnumed.wxpython import gmPhraseWheel
from Gnumed.wxpython import gmPlugin
from Gnumed.wxpython import gmEncounterWidgets
from Gnumed.wxpython import gmListWidgets
from Gnumed.wxpython import gmRegetMixin


_log = logging.getLogger('gm.ui')


default_chunksize = 1 * 1024 * 1024		# 1 MB

#============================================================
def manage_document_descriptions(parent=None, document=None):

	#-----------------------------------
	def delete_item(item):
		doit = gmGuiHelpers.gm_show_question (
			_(	'Are you sure you want to delete this\n'
				'description from the document ?\n'
			),
			_('Deleting document description')
		)
		if not doit:
			return True

		document.delete_description(pk = item[0])
		return True
	#-----------------------------------
	def add_item():
		dlg = gmGuiHelpers.cMultilineTextEntryDlg (
			parent,
			-1,
			title = _('Adding document description'),
			msg = _('Below you can add a document description.\n')
		)
		result = dlg.ShowModal()
		if result == wx.ID_SAVE:
			document.add_description(dlg.value)

		dlg.DestroyLater()
		return True
	#-----------------------------------
	def edit_item(item):
		dlg = gmGuiHelpers.cMultilineTextEntryDlg (
			parent,
			-1,
			title = _('Editing document description'),
			msg = _('Below you can edit the document description.\n'),
			text = item[1]
		)
		result = dlg.ShowModal()
		if result == wx.ID_SAVE:
			document.update_description(pk = item[0], description = dlg.value)

		dlg.DestroyLater()
		return True
	#-----------------------------------
	def refresh_list(lctrl):
		descriptions = document.get_descriptions()

		lctrl.set_string_items(items = [
			'%s%s' % ( (' '.join(regex.split(r'\r\n+|\r+|\n+|\t+', desc[1])))[:30], gmTools.u_ellipsis )
			for desc in descriptions
		])
		lctrl.set_data(data = descriptions)
	#-----------------------------------

	gmListWidgets.get_choices_from_list (
		parent = parent,
		msg = _('Select the description you are interested in.\n'),
		caption = _('Managing document descriptions'),
		columns = [_('Description')],
		edit_callback = edit_item,
		new_callback = add_item,
		delete_callback = delete_item,
		refresh_callback = refresh_list,
		single_selection = True,
		can_return_empty = True
	)

	return True

#============================================================
def _save_file_as_new_document(**kwargs):
	try:
		del kwargs['signal']
		del kwargs['sender']
	except KeyError:
		pass
	wx.CallAfter(save_file_as_new_document, **kwargs)

def _save_files_as_new_document(**kwargs):
	try:
		del kwargs['signal']
		del kwargs['sender']
	except KeyError:
		pass
	wx.CallAfter(save_files_as_new_document, **kwargs)

#----------------------
def save_file_as_new_document(parent=None, filename=None, document_type=None, unlock_patient=False, episode=None, review_as_normal=False, pk_org_unit=None, date_generated=None):
	return save_files_as_new_document (
		parent = parent,
		filenames = [filename],
		document_type = document_type,
		unlock_patient = unlock_patient,
		episode = episode,
		review_as_normal = review_as_normal,
		pk_org_unit = pk_org_unit,
		date_generated = date_generated
	)

#----------------------
def save_files_as_new_document(parent=None, filenames=None, document_type=None, unlock_patient=False, episode=None, review_as_normal=False, reference=None, pk_org_unit=None, date_generated=None, comment=None, reviewer=None, pk_document_type=None):
	"""Create document from files.

	Args:
		parent: wxPython parent widget
		filenames: files to read data from, which become document parts
		document_type: the type of document in the archive
		episode: the episode to file the document under
		reference: an (perhaps external) reference ID to be set on the document

	Returns:
		A document, or None on failure.
	"""
	pat = gmPerson.gmCurrentPatient()
	if not pat.connected:
		_log.error('no active patient to file documents under')
		return None

	emr = pat.emr
	if parent is None:
		parent = wx.GetApp().GetTopWindow()
	# FIXME: get connection and use for episode/doc/parts
	if episode is None:
		all_epis = emr.get_episodes()
		if len(all_epis) == 0:
			episode = emr.add_episode(episode_name = _('Documents'), is_open = False)
		else:
			from Gnumed.wxpython.gmEMRStructWidgets import cEpisodeListSelectorDlg
			dlg = cEpisodeListSelectorDlg(parent, -1, episodes = all_epis)
			dlg.SetTitle(_('Select the episode under which to file the document ...'))
			btn_pressed = dlg.ShowModal()
			episode = dlg.get_selected_item_data(only_one = True)
			dlg.DestroyLater()
			if (btn_pressed == wx.ID_CANCEL) or (episode is None):
				if unlock_patient:
					pat.locked = False
				return None

	wx.BeginBusyCursor()
	if pk_document_type is None:
		pk_document_type = gmDocuments.create_document_type(document_type = document_type)['pk_doc_type']
	docs_folder = pat.get_document_folder()
	doc = docs_folder.add_document (
		document_type = pk_document_type,
		encounter = emr.active_encounter['pk_encounter'],
		episode = episode['pk_episode']
	)
	if doc is None:
		wx.EndBusyCursor()
		gmGuiHelpers.gm_show_error (
			aMessage = _('Cannot create new document.'),
			aTitle = _('saving document')
		)
		return None

	doc['ext_ref'] = reference
	doc['pk_org_unit'] = pk_org_unit
	doc['clin_when'] = date_generated
	doc['comment'] = gmTools.none_if(value = comment, none_equivalent = '', strip_string = True)
	doc.save()
	success, msg, filename = doc.add_parts_from_files(files = filenames, reviewer = reviewer)
	if not success:
		wx.EndBusyCursor()
		gmGuiHelpers.gm_show_error (
			aMessage = msg,
			aTitle = _('saving document')
		)
		return None

	if review_as_normal:
		doc.set_reviewed(technically_abnormal = False, clinically_relevant = False)
	if unlock_patient:
		pat.locked = False
	# inform user
	gmDispatcher.send(signal = 'statustext', msg = _('Imported new document from %s.') % filenames, beep = True)
	cfg = gmCfg.cCfgSQL()
	show_id = bool (
		cfg.get2 (
			option = 'horstspace.scan_index.show_doc_id',
			workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
			bias = 'user'
		)
	)
	wx.EndBusyCursor()
	if not show_id:
		gmDispatcher.send(signal = 'statustext', msg = _('Successfully saved new document.'))
	else:
		if reference is None:
			msg = _('Successfully saved the new document.')
		else:
			msg = _('The reference ID for the new document is:\n'
					'\n'
					' <%s>\n'
					'\n'
					'You probably want to write it down on the\n'
					'original documents.\n'
					'\n'
					"If you don't care about the ID you can switch\n"
					'off this message in the GNUmed configuration.\n'
			) % reference
		gmGuiHelpers.gm_show_info (
			aMessage = msg,
			aTitle = _('Saving document')
		)
	# remove non-temp files
	tmp_dir = gmTools.gmPaths().tmp_dir
	files2remove = [ f for f in filenames if not f.startswith(tmp_dir) ]
	if len(files2remove) > 0:
		do_delete = gmGuiHelpers.gm_show_question (
			_(	'Successfully imported files as document.\n'
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

	return doc

#----------------------
gmDispatcher.connect(signal = 'import_document_from_file', receiver = _save_file_as_new_document)
gmDispatcher.connect(signal = 'import_document_from_files', receiver = _save_files_as_new_document)

#============================================================
class cDocumentPhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):

		gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)

		ctxt = {'ctxt_pat': {
			'where_part': '(pk_patient = %(pat)s) AND',
			'placeholder': 'pat'
		}}

		mp = gmMatchProvider.cMatchProvider_SQL2 (
			queries = ["""
SELECT DISTINCT ON (list_label)
	pk_doc AS data,
	l10n_type || ' (' || to_char(clin_when, 'YYYY Mon DD') || ')' || coalesce(': ' || unit || '@' || organization, '') || ' - ' || episode || coalesce(' (' || health_issue || ')', '') AS list_label,
	l10n_type || ' (' || to_char(clin_when, 'YYYY Mon DD') || ')' || coalesce(': ' || organization, '') || ' - ' || coalesce(' (' || health_issue || ')', episode) AS field_label
FROM blobs.v_doc_med
WHERE
		%(ctxt_pat)s
(
	l10n_type %(fragment_condition)s
		OR
	unit %(fragment_condition)s
		OR
	organization %(fragment_condition)s
		OR
	episode %(fragment_condition)s
		OR
	health_issue %(fragment_condition)s
)
ORDER BY list_label
LIMIT 25"""],
			context = ctxt
		)
		mp.setThresholds(1, 3, 5)
		#mp.unset_context('pat')
		pat = gmPerson.gmCurrentPatient()
		mp.set_context('pat', pat.ID)

		self.matcher = mp
		self.picklist_delay = 50
		self.selection_only = True

		self.SetToolTip(_('Select a document.'))

	#--------------------------------------------------------
	def _data2instance(self):
		if len(self._data) == 0:
			return None
		return gmDocuments.cDocument(aPK_obj = self.GetData())

	#--------------------------------------------------------
	def _get_data_tooltip(self):
		if len(self._data) == 0:
			return ''
		return gmDocuments.cDocument(aPK_obj = self.GetData()).format(single_line = False)

#============================================================
class cDocumentCommentPhraseWheel(gmPhraseWheel.cPhraseWheel):
	"""Let user select a document comment from all existing comments."""
	def __init__(self, *args, **kwargs):

		gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)

		context = {
			'ctxt_doc_type': {
				'where_part': 'and fk_type = %(pk_doc_type)s',
				'placeholder': 'pk_doc_type'
			}
		}

		mp = gmMatchProvider.cMatchProvider_SQL2 (
			queries = ["""
SELECT
	data,
	field_label,
	list_label
FROM (
	SELECT DISTINCT ON (field_label) *
	FROM (
		-- constrained by doc type
		SELECT
			comment AS data,
			comment AS field_label,
			comment AS list_label,
			1 AS rank
		FROM blobs.doc_med
		WHERE
			comment %(fragment_condition)s
			%(ctxt_doc_type)s

		UNION ALL

		SELECT
			comment AS data,
			comment AS field_label,
			comment AS list_label,
			2 AS rank
		FROM blobs.doc_med
		WHERE
			comment %(fragment_condition)s
	) AS q_union
) AS q_distinct
ORDER BY rank, list_label
LIMIT 25"""],
			context = context
		)
		mp.setThresholds(3, 5, 7)
		mp.unset_context('pk_doc_type')

		self.matcher = mp
		self.picklist_delay = 50

		self.SetToolTip(_('Enter a comment on the document.'))

#============================================================
# document type widgets
#============================================================
def manage_document_types(parent=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	dlg = cEditDocumentTypesDlg(parent = parent)
	dlg.ShowModal()

#============================================================
from Gnumed.wxGladeWidgets import wxgEditDocumentTypesDlg

class cEditDocumentTypesDlg(wxgEditDocumentTypesDlg.wxgEditDocumentTypesDlg):
	"""A dialog showing a cEditDocumentTypesPnl."""

	def __init__(self, *args, **kwargs):
		wxgEditDocumentTypesDlg.wxgEditDocumentTypesDlg.__init__(self, *args, **kwargs)

#============================================================
from Gnumed.wxGladeWidgets import wxgEditDocumentTypesPnl

class cEditDocumentTypesPnl(wxgEditDocumentTypesPnl.wxgEditDocumentTypesPnl):
	"""A panel grouping together fields to edit the list of document types."""

	def __init__(self, *args, **kwargs):
		wxgEditDocumentTypesPnl.wxgEditDocumentTypesPnl.__init__(self, *args, **kwargs)
		self.__init_ui()
		self.__register_interests()
		self.repopulate_ui()
	#--------------------------------------------------------
	def __init_ui(self):
		self._LCTRL_doc_type.set_columns([_('Type'), _('Translation'), _('User defined'), _('In use')])
		self._LCTRL_doc_type.set_column_widths()
	#--------------------------------------------------------
	def __register_interests(self):
		gmDispatcher.connect(signal = 'blobs.doc_type_mod_db', receiver = self._on_doc_type_mod_db)
	#--------------------------------------------------------
	def _on_doc_type_mod_db(self):
		self.repopulate_ui()
	#--------------------------------------------------------
	def repopulate_ui(self):

		self._LCTRL_doc_type.DeleteAllItems()

		doc_types = gmDocuments.get_document_types()
		pos = len(doc_types) + 1

		for doc_type in doc_types:
			row_num = self._LCTRL_doc_type.InsertItem(pos, label = doc_type['type'])
			self._LCTRL_doc_type.SetItem(index = row_num, column = 1, label = doc_type['l10n_type'])
			if doc_type['is_user_defined']:
				self._LCTRL_doc_type.SetItem(index = row_num, column = 2, label = ' X ')
			if doc_type['is_in_use']:
				self._LCTRL_doc_type.SetItem(index = row_num, column = 3, label = ' X ')

		if len(doc_types) > 0:
			self._LCTRL_doc_type.set_data(data = doc_types)
			self._LCTRL_doc_type.SetColumnWidth(0, wx.LIST_AUTOSIZE)
			self._LCTRL_doc_type.SetColumnWidth(1, wx.LIST_AUTOSIZE)
			self._LCTRL_doc_type.SetColumnWidth(2, wx.LIST_AUTOSIZE_USEHEADER)
			self._LCTRL_doc_type.SetColumnWidth(3, wx.LIST_AUTOSIZE_USEHEADER)

		self._TCTRL_type.SetValue('')
		self._TCTRL_l10n_type.SetValue('')

		self._BTN_set_translation.Enable(False)
		self._BTN_delete.Enable(False)
		self._BTN_add.Enable(False)
		self._BTN_reassign.Enable(False)

		self._LCTRL_doc_type.SetFocus()
	#--------------------------------------------------------
	# event handlers
	#--------------------------------------------------------
	def _on_list_item_selected(self, evt):
		doc_type = self._LCTRL_doc_type.get_selected_item_data()

		self._TCTRL_type.SetValue(doc_type['type'])
		self._TCTRL_l10n_type.SetValue(doc_type['l10n_type'])

		self._BTN_set_translation.Enable(True)
		self._BTN_delete.Enable(not bool(doc_type['is_in_use']))
		self._BTN_add.Enable(False)
		self._BTN_reassign.Enable(True)

		return
	#--------------------------------------------------------
	def _on_type_modified(self, event):
		self._BTN_set_translation.Enable(False)
		self._BTN_delete.Enable(False)
		self._BTN_reassign.Enable(False)

		self._BTN_add.Enable(True)
#		self._LCTRL_doc_type.deselect_selected_item()
		return
	#--------------------------------------------------------
	def _on_set_translation_button_pressed(self, event):
		doc_type = self._LCTRL_doc_type.get_selected_item_data()
		if doc_type.set_translation(translation = self._TCTRL_l10n_type.GetValue().strip()):
			self.repopulate_ui()

		return
	#--------------------------------------------------------
	def _on_delete_button_pressed(self, event):
		doc_type = self._LCTRL_doc_type.get_selected_item_data()
		if doc_type['is_in_use']:
			gmGuiHelpers.gm_show_info (
				_(
					'Cannot delete document type\n'
					' [%s]\n'
					'because it is currently in use.'
				) % doc_type['l10n_type'],
				_('deleting document type')
			)
			return

		gmDocuments.delete_document_type(document_type = doc_type)

		return
	#--------------------------------------------------------
	def _on_add_button_pressed(self, event):
		desc = self._TCTRL_type.GetValue().strip()
		if desc != '':
			doc_type = gmDocuments.create_document_type(document_type = desc)		# does not create dupes
			l10n_desc = self._TCTRL_l10n_type.GetValue().strip()
			if (l10n_desc != '') and (l10n_desc != doc_type['l10n_type']):
				doc_type.set_translation(translation = l10n_desc)

		return
	#--------------------------------------------------------
	def _on_reassign_button_pressed(self, event):

		orig_type = self._LCTRL_doc_type.get_selected_item_data()
		doc_types = gmDocuments.get_document_types()

		new_type = gmListWidgets.get_choices_from_list (
			parent = self,
			msg = _(
				'From the list below select the document type you want\n'
				'all documents currently classified as:\n\n'
				' "%s"\n\n'
				'to be changed to.\n\n'
				'Be aware that this change will be applied to ALL such documents. If there\n'
				'are many documents to change it can take quite a while.\n\n'
				'Make sure this is what you want to happen !\n'
			) % orig_type['l10n_type'],
			caption = _('Reassigning document type'),
			choices = [ [gmTools.bool2subst(dt['is_user_defined'], 'X', ''), dt['type'], dt['l10n_type']] for dt in doc_types ],
			columns = [_('User defined'), _('Type'), _('Translation')],
			data = doc_types,
			single_selection = True
		)

		if new_type is None:
			return

		wx.BeginBusyCursor()
		gmDocuments.reclassify_documents_by_type(original_type = orig_type, target_type = new_type)
		wx.EndBusyCursor()

		return

#============================================================
class cDocumentTypeSelectionPhraseWheel(gmPhraseWheel.cPhraseWheel):
	"""Let user select a document type."""
	def __init__(self, *args, **kwargs):

		gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)

		mp = gmMatchProvider.cMatchProvider_SQL2 (
			queries = [
"""SELECT
	data,
	field_label,
	list_label
FROM ((
	SELECT
		pk_doc_type AS data,
		l10n_type AS field_label,
		l10n_type AS list_label,
		1 AS rank
	FROM blobs.v_doc_type
	WHERE
		is_user_defined IS True
			AND
		l10n_type %(fragment_condition)s
) UNION (
	SELECT
		pk_doc_type AS data,
		l10n_type AS field_label,
		l10n_type AS list_label,
		2 AS rank
	FROM blobs.v_doc_type
	WHERE
		is_user_defined IS False
			AND
		l10n_type %(fragment_condition)s
)) AS q1
ORDER BY q1.rank, q1.list_label"""]
			)
		mp.setThresholds(2, 4, 6)

		self.matcher = mp
		self.picklist_delay = 50

		self.SetToolTip(_('Select the document type.'))
	#--------------------------------------------------------
	def _create_data(self):

		doc_type = self.GetValue().strip()
		if doc_type == '':
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot create document type without name.'), beep = True)
			_log.debug('cannot create document type without name')
			return

		pk = gmDocuments.create_document_type(doc_type)['pk_doc_type']
		if pk is None:
			self.data = {}
		else:
			self.SetText (
				value = doc_type,
				data = pk
			)

#============================================================
# document review widgets
#============================================================
def review_document_part(parent=None, part=None):
	if parent is None:
		parent = wx.GetApp().GetTopWindow()
	dlg = cReviewDocPartDlg (
		parent = parent,
		id = -1,
		part = part
	)
	dlg.ShowModal()
	dlg.DestroyLater()

#------------------------------------------------------------
def review_document(parent=None, document=None):
	return review_document_part(parent = parent, part = document)

#------------------------------------------------------------
def edit_document_or_part(parent=None, document_or_part=None, single_entry=True):
	return review_document_part(parent = parent, part = document_or_part)

#------------------------------------------------------------
from Gnumed.wxGladeWidgets import wxgReviewDocPartDlg

class cReviewDocPartDlg(wxgReviewDocPartDlg.wxgReviewDocPartDlg):
	def __init__(self, *args, **kwds):
		"""Support parts and docs now.
		"""
		part = kwds['part']
		del kwds['part']
		wxgReviewDocPartDlg.wxgReviewDocPartDlg.__init__(self, *args, **kwds)

		if isinstance(part, gmDocuments.cDocumentPart):
			self.__part = part
			self.__doc = self.__part.containing_document
			self.__reviewing_doc = False
		elif isinstance(part, gmDocuments.cDocument):
			self.__doc = part
			if len(self.__doc.parts) == 0:
				self.__part = None
			else:
				self.__part = self.__doc.parts[0]
			self.__reviewing_doc = True
		else:
			raise ValueError('<part> must be gmDocuments.cDocument or gmDocuments.cDocumentPart instance, got <%s>' % type(part))

		self.__init_ui_data()

	#--------------------------------------------------------
	# internal API
	#--------------------------------------------------------
	def __init_ui_data(self):
		# FIXME: fix this
		# associated episode (add " " to avoid popping up pick list)
		self._PhWheel_episode.SetText('%s ' % self.__doc['episode'], self.__doc['pk_episode'])
		self._PhWheel_doc_type.SetText(value = self.__doc['l10n_type'], data = self.__doc['pk_type'])
		self._PhWheel_doc_type.add_callback_on_set_focus(self._on_doc_type_gets_focus)
		self._PhWheel_doc_type.add_callback_on_lose_focus(self._on_doc_type_loses_focus)

		if self.__reviewing_doc:
			self._PRW_doc_comment.SetText(gmTools.coalesce(self.__doc['comment'], ''))
			self._PRW_doc_comment.set_context(context = 'pk_doc_type', val = self.__doc['pk_type'])
		else:
			self._PRW_doc_comment.SetText(gmTools.coalesce(self.__part['obj_comment'], ''))

		if self.__doc['pk_org_unit'] is not None:
			self._PRW_org.SetText(value = '%s @ %s' % (self.__doc['unit'], self.__doc['organization']), data = self.__doc['pk_org_unit'])

		if self.__doc['unit_is_receiver']:
			self._RBTN_org_is_receiver.Value = True
		else:
			self._RBTN_org_is_source.Value = True

		if self.__reviewing_doc:
			self._PRW_org.Enable()
		else:
			self._PRW_org.Disable()

		if self.__doc['pk_hospital_stay'] is not None:
			self._PRW_hospital_stay.SetText(data = self.__doc['pk_hospital_stay'])

		fts = gmDateTime.cFuzzyTimestamp(timestamp = self.__doc['clin_when'])
		self._PhWheel_doc_date.SetText(fts.strftime('%Y-%m-%d'), fts)
		self._TCTRL_reference.SetValue(gmTools.coalesce(self.__doc['ext_ref'], ''))
		if self.__reviewing_doc:
			self._TCTRL_filename.Enable(False)
			self._SPINCTRL_seq_idx.Enable(False)
		else:
			self._TCTRL_filename.SetValue(gmTools.coalesce(self.__part['filename'], ''))
			self._SPINCTRL_seq_idx.SetValue(gmTools.coalesce(self.__part['seq_idx'], 0))

		self._LCTRL_existing_reviews.InsertColumn(0, _('who'))
		self._LCTRL_existing_reviews.InsertColumn(1, _('when'))
		self._LCTRL_existing_reviews.InsertColumn(2, _('+/-'))
		self._LCTRL_existing_reviews.InsertColumn(3, _('!'))
		self._LCTRL_existing_reviews.InsertColumn(4, _('comment'))

		self.__reload_existing_reviews()

		if self._LCTRL_existing_reviews.GetItemCount() > 0:
			self._LCTRL_existing_reviews.SetColumnWidth(0, wx.LIST_AUTOSIZE)
			self._LCTRL_existing_reviews.SetColumnWidth(1, wx.LIST_AUTOSIZE)
			self._LCTRL_existing_reviews.SetColumnWidth(2, wx.LIST_AUTOSIZE_USEHEADER)
			self._LCTRL_existing_reviews.SetColumnWidth(3, wx.LIST_AUTOSIZE_USEHEADER)
			self._LCTRL_existing_reviews.SetColumnWidth(4, wx.LIST_AUTOSIZE)

		if self.__part is None:
			self._ChBOX_review.SetValue(False)
			self._ChBOX_review.Enable(False)
			self._ChBOX_abnormal.Enable(False)
			self._ChBOX_relevant.Enable(False)
			self._ChBOX_sign_all_pages.Enable(False)
		else:
			me = gmStaff.gmCurrentProvider()
			if self.__part['pk_intended_reviewer'] == me['pk_staff']:
				msg = _('(you are the primary reviewer)')
			else:
				other = gmStaff.cStaff(aPK_obj = self.__part['pk_intended_reviewer'])
				msg = _('(someone else is the intended reviewer: %s)') % other['short_alias']
			self._TCTRL_responsible.SetValue(msg)
			# init my review if any
			if self.__part['reviewed_by_you']:
				revs = self.__part.get_reviews()
				for rev in revs:
					if rev['is_your_review']:
						self._ChBOX_abnormal.SetValue(bool(rev[2]))
						self._ChBOX_relevant.SetValue(bool(rev[3]))
						break

			self._ChBOX_sign_all_pages.SetValue(self.__reviewing_doc)

		return True

	#--------------------------------------------------------
	def __reload_existing_reviews(self):
		self._LCTRL_existing_reviews.DeleteAllItems()
		if self.__part is None:
			return True
		revs = self.__part.get_reviews()		# FIXME: this is ugly as sin, it should be dicts, not lists
		if len(revs) == 0:
			return True
		# find special reviews
		review_by_responsible_doc = None
		reviews_by_others = []
		for rev in revs:
			if rev['is_review_by_responsible_reviewer'] and not rev['is_your_review']:
				review_by_responsible_doc = rev
			if not (rev['is_review_by_responsible_reviewer'] or rev['is_your_review']):
				reviews_by_others.append(rev)
		# display them
		if review_by_responsible_doc is not None:
			row_num = self._LCTRL_existing_reviews.InsertItem(sys.maxsize, label=review_by_responsible_doc[0])
			self._LCTRL_existing_reviews.SetItemTextColour(row_num, wx.BLUE)
			self._LCTRL_existing_reviews.SetItem(index = row_num, column=0, label=review_by_responsible_doc[0])
			self._LCTRL_existing_reviews.SetItem(index = row_num, column=1, label=review_by_responsible_doc[1].strftime('%x %H:%M'))
			if review_by_responsible_doc['is_technically_abnormal']:
				self._LCTRL_existing_reviews.SetItem(index = row_num, column=2, label='X')
			if review_by_responsible_doc['clinically_relevant']:
				self._LCTRL_existing_reviews.SetItem(index = row_num, column=3, label='X')
			self._LCTRL_existing_reviews.SetItem(index = row_num, column=4, label=review_by_responsible_doc[6])
			row_num += 1
		for rev in reviews_by_others:
			row_num = self._LCTRL_existing_reviews.InsertItem(sys.maxsize, label=rev[0])
			self._LCTRL_existing_reviews.SetItem(index = row_num, column=0, label=rev[0])
			self._LCTRL_existing_reviews.SetItem(index = row_num, column=1, label=rev[1].strftime('%x %H:%M'))
			if rev['is_technically_abnormal']:
				self._LCTRL_existing_reviews.SetItem(index = row_num, column=2, label='X')
			if rev['clinically_relevant']:
				self._LCTRL_existing_reviews.SetItem(index = row_num, column=3, label='X')
			self._LCTRL_existing_reviews.SetItem(index = row_num, column=4, label=rev[6])
		return True

	#--------------------------------------------------------
	# event handlers
	#--------------------------------------------------------
	def _on_save_button_pressed(self, evt):
		"""Save the metadata to the backend."""

		evt.Skip()

		# 1) handle associated episode
		pk_episode = self._PhWheel_episode.GetData(can_create=True, is_open=True)
		if pk_episode is None:
			gmGuiHelpers.gm_show_error (
				_('Cannot create episode\n [%s]'),
				_('Editing document properties')
			)
			return False

		doc_type = self._PhWheel_doc_type.GetData(can_create = True)
		if doc_type is None:
			gmDispatcher.send(signal='statustext', msg=_('Cannot change document type to [%s].') % self._PhWheel_doc_type.GetValue().strip())
			return False

		# since the phrasewheel operates on the active
		# patient all episodes really should belong
		# to it so we don't check patient change
		self.__doc['pk_episode'] = pk_episode
		self.__doc['pk_type'] = doc_type
		if self.__reviewing_doc:
			self.__doc['comment'] = self._PRW_doc_comment.GetValue().strip()
		# FIXME: a rather crude way of error checking:
		if self._PhWheel_doc_date.GetData() is not None:
			self.__doc['clin_when'] = self._PhWheel_doc_date.GetData().get_pydt()
		self.__doc['ext_ref'] = self._TCTRL_reference.GetValue().strip()
		self.__doc['pk_org_unit'] = self._PRW_org.GetData()
		if self._RBTN_org_is_receiver.Value is True:
			self.__doc['unit_is_receiver'] = True
		else:
			self.__doc['unit_is_receiver'] = False
		self.__doc['pk_hospital_stay'] = self._PRW_hospital_stay.GetData()

		success, data = self.__doc.save()
		if not success:
			gmGuiHelpers.gm_show_error (
				_('Cannot link the document to episode\n\n [%s]') % epi_name,
				_('Editing document properties')
			)
			return False

		# 2) handle review
		if self._ChBOX_review.GetValue():
			provider = gmStaff.gmCurrentProvider()
			abnormal = self._ChBOX_abnormal.GetValue()
			relevant = self._ChBOX_relevant.GetValue()
			msg = None
			if self.__reviewing_doc:		# - on all pages
				if not self.__doc.set_reviewed(technically_abnormal = abnormal, clinically_relevant = relevant):
					msg = _('Error setting "reviewed" status of this document.')
				if self._ChBOX_responsible.GetValue():
					if not self.__doc.set_primary_reviewer(reviewer = provider['pk_staff']):
						msg = _('Error setting responsible clinician for this document.')
			else:								# - just on this page
				if not self.__part.set_reviewed(technically_abnormal = abnormal, clinically_relevant = relevant):
					msg = _('Error setting "reviewed" status of this part.')
				if self._ChBOX_responsible.GetValue():
					self.__part['pk_intended_reviewer'] = provider['pk_staff']
			if msg is not None:
				gmGuiHelpers.gm_show_error(msg, _('Editing document properties'))
				return False

		# 3) handle "page" specific parts
		if not self.__reviewing_doc:
			self.__part['filename'] = gmTools.none_if(self._TCTRL_filename.GetValue().strip(), '')
			new_idx = gmTools.none_if(self._SPINCTRL_seq_idx.GetValue(), 0)
			if self.__part['seq_idx'] != new_idx:
				if new_idx in self.__doc['seq_idx_list']:
					msg = _(
						'Cannot set page number to [%s] because\n'
						'another page with this number exists.\n'
						'\n'
						'Page numbers in use:\n'
						'\n'
						' %s'
					) % (
						new_idx,
						self.__doc['seq_idx_list']
					)
					gmGuiHelpers.gm_show_error(msg, _('Editing document part properties'))
				else:
					self.__part['seq_idx'] = new_idx
			self.__part['obj_comment'] = self._PRW_doc_comment.GetValue().strip()
			success, data = self.__part.save_payload()
			if not success:
				gmGuiHelpers.gm_show_error (
					_('Error saving part properties.'),
					_('Editing document part properties')
				)
				return False

		return True

	#--------------------------------------------------------
	def _on_reviewed_box_checked(self, evt):
		state = self._ChBOX_review.GetValue()
		self._ChBOX_abnormal.Enable(enable = state)
		self._ChBOX_relevant.Enable(enable = state)
		self._ChBOX_responsible.Enable(enable = state)

	#--------------------------------------------------------
	def _on_doc_type_gets_focus(self):
		"""Per Jim: Changing the doc type happens a lot more often
		   then correcting spelling, hence select-all on getting focus.
		"""
		self._PhWheel_doc_type.SetSelection(-1, -1)

	#--------------------------------------------------------
	def _on_doc_type_loses_focus(self):
		pk_doc_type = self._PhWheel_doc_type.GetData()
		if pk_doc_type is None:
			self._PRW_doc_comment.unset_context(context = 'pk_doc_type')
		else:
			self._PRW_doc_comment.set_context(context = 'pk_doc_type', val = pk_doc_type)
		return True

#============================================================
def acquire_images_from_capture_device(device=None, calling_window=None):

	_log.debug('acquiring images from [%s]', device)

	# do not import globally since we might want to use
	# this module without requiring any scanner to be available
	from Gnumed.pycommon import gmScanBackend
	try:
		fnames = gmScanBackend.acquire_pages_into_files (
			device = device,
			delay = 5,
			calling_window = calling_window
		)
	except OSError:
		_log.exception('problem acquiring image from source')
		gmGuiHelpers.gm_show_error (
			aMessage = _(
				'No images could be acquired from the source.\n\n'
				'This may mean the scanner driver is not properly installed.\n\n'
				'On Windows you must install the TWAIN Python module\n'
				'while on Linux and MacOSX it is recommended to install\n'
				'the XSane package.'
			),
			aTitle = _('Acquiring images')
		)
		return None

	_log.debug('acquired %s images', len(fnames))

	return fnames

#------------------------------------------------------------
from Gnumed.wxGladeWidgets import wxgScanIdxPnl

class cScanIdxDocsPnl(wxgScanIdxPnl.wxgScanIdxPnl, gmPlugin.cPatientChange_PluginMixin):

	def __init__(self, *args, **kwds):
		wxgScanIdxPnl.wxgScanIdxPnl.__init__(self, *args, **kwds)
		gmPlugin.cPatientChange_PluginMixin.__init__(self)

		self._PhWheel_reviewer.matcher = gmPerson.cMatchProvider_Provider()

		self.__init_ui_data()
		self._PhWheel_doc_type.add_callback_on_lose_focus(self._on_doc_type_loses_focus)

		# make me and listctrl file drop targets
		dt = gmGuiHelpers.cFileDropTarget(target = self)
		self.SetDropTarget(dt)
		dt = gmGuiHelpers.cFileDropTarget(on_drop_callback = self._drop_target_consume_filenames)
		self._LCTRL_doc_pages.SetDropTarget(dt)

		# do not import globally since we might want to use
		# this module without requiring any scanner to be available
		from Gnumed.pycommon import gmScanBackend
		self.scan_module = gmScanBackend

	#--------------------------------------------------------
	# file drop target API
	#--------------------------------------------------------
	def _drop_target_consume_filenames(self, filenames):
		pat = gmPerson.gmCurrentPatient()
		if not pat.connected:
			gmDispatcher.send(signal='statustext', msg=_('Cannot accept new documents. No active patient.'))
			return

		# dive into folders dropped onto us and extract files (one level deep only)
		real_filenames = []
		for pathname in filenames:
			try:
				files = os.listdir(pathname)
				source = _('directory dropped on client')
				gmDispatcher.send(signal = 'statustext', msg = _('Extracting files from folder [%s] ...') % pathname)
				for filename in files:
					fullname = os.path.join(pathname, filename)
					if not os.path.isfile(fullname):
						continue
					real_filenames.append(fullname)
			except OSError:
				source = _('file dropped on client')
				real_filenames.append(pathname)

		self.add_parts_from_files(real_filenames, source)

	#--------------------------------------------------------
	def repopulate_ui(self):
		pass

	#--------------------------------------------------------
	# patient change plugin API
	#--------------------------------------------------------
	def _pre_patient_unselection(self, **kwds):
		# FIXME: persist pending data from here
		pass

	#--------------------------------------------------------
	def _post_patient_selection(self, **kwds):
		self.__init_ui_data()

	#--------------------------------------------------------
	# internal API
	#--------------------------------------------------------
	def __init_ui_data(self):
		# -----------------------------
		self._PhWheel_episode.SetText(value = _('other documents'), suppress_smarts = True)
		self._PhWheel_doc_type.SetText('')
		# -----------------------------
		# FIXME: make this configurable: either now() or last_date()
		fts = gmDateTime.cFuzzyTimestamp()
		self._PhWheel_doc_date.SetText(fts.strftime('%Y-%m-%d'), fts)
		self._PRW_doc_comment.SetText('')
		self._PhWheel_source.SetText('', None)
		self._RBTN_org_is_source.SetValue(1)
		# FIXME: should be set to patient's primary doc
		self._PhWheel_reviewer.selection_only = True
		me = gmStaff.gmCurrentProvider()
		self._PhWheel_reviewer.SetText (
			value = '%s (%s%s %s)' % (me['short_alias'], gmTools.coalesce(me['title'], ''), me['firstnames'], me['lastnames']),
			data = me['pk_staff']
		)
		# -----------------------------
		# FIXME: set from config item
		self._ChBOX_reviewed.SetValue(False)
		self._ChBOX_abnormal.Disable()
		self._ChBOX_abnormal.SetValue(False)
		self._ChBOX_relevant.Disable()
		self._ChBOX_relevant.SetValue(False)
		# -----------------------------
		self._TBOX_description.SetValue('')
		# -----------------------------
		# the list holding our page files
		self._LCTRL_doc_pages.remove_items_safely()
		self._LCTRL_doc_pages.set_columns([_('file'), _('path')])
		self._LCTRL_doc_pages.set_column_widths()

		self._TCTRL_metadata.SetValue('')

		self._PhWheel_doc_type.SetFocus()

	#--------------------------------------------------------
	def add_parts_from_files(self, filenames, source=''):
		rows = gmTools.coalesce(self._LCTRL_doc_pages.string_items, [])
		data = gmTools.coalesce(self._LCTRL_doc_pages.data, [])
		rows.extend([ [gmTools.fname_from_path(f), gmTools.fname_dir(f)] for f in filenames ])
		data.extend([ [f, source] for f in filenames ])
		self._LCTRL_doc_pages.string_items = rows
		self._LCTRL_doc_pages.data = data
		self._LCTRL_doc_pages.set_column_widths()

	#--------------------------------------------------------
	def __valid_for_save(self):
		title = _('saving document')

		if self._LCTRL_doc_pages.ItemCount == 0:
			dbcfg = gmCfg.cCfgSQL()
			allow_empty = bool(dbcfg.get2 (
				option =  'horstspace.scan_index.allow_partless_documents',
				workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
				bias = 'user',
				default = False
			))
			if allow_empty:
				save_empty = gmGuiHelpers.gm_show_question (
					aMessage = _('No parts to save. Really save an empty document as a reference ?'),
					aTitle = title
				)
				if not save_empty:
					return False
			else:
				gmGuiHelpers.gm_show_error (
					aMessage = _('No parts to save. Aquire some parts first.'),
					aTitle = title
				)
				return False

		if self._LCTRL_doc_pages.ItemCount > 0:
			for fname in [ data[0] for data in self._LCTRL_doc_pages.data ]:
				try:
					open(fname, 'rb').close()
				except OSError:
					_log.exception('cannot access [%s]', fname)
					gmGuiHelpers.gm_show_error(title = title, error = _('Cannot access document part file:\n\n %s') % fname)
					return False

		doc_type_pk = self._PhWheel_doc_type.GetData(can_create = True)
		if doc_type_pk is None:
			gmGuiHelpers.gm_show_error (
				aMessage = _('No document type applied. Choose a document type'),
				aTitle = title
			)
			return False

		# this should be optional, actually
#		if self._PRW_doc_comment.GetValue().strip() == '':
#			gmGuiHelpers.gm_show_error (
#				aMessage = _('No document comment supplied. Add a comment for this document.'),
#				aTitle = title
#			)
#			return False

		if self._PhWheel_episode.GetValue().strip() == '':
			gmGuiHelpers.gm_show_error (
				aMessage = _('You must select an episode to save this document under.'),
				aTitle = title
			)
			return False

		if self._PhWheel_reviewer.GetData() is None:
			gmGuiHelpers.gm_show_error (
				aMessage = _('You need to select from the list of staff members the doctor who is intended to sign the document.'),
				aTitle = title
			)
			return False

		if self._PhWheel_doc_date.is_valid_timestamp(empty_is_valid = True) is False:
			gmGuiHelpers.gm_show_error (
				aMessage = _('Invalid date of generation.'),
				aTitle = title
			)
			return False

		return True

	#--------------------------------------------------------
	def get_device_to_use(self, reconfigure=False):

		if not reconfigure:
			dbcfg = gmCfg.cCfgSQL()
			device = dbcfg.get2 (
				option =  'external.xsane.default_device',
				workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
				bias = 'workplace',
				default = ''
			)
			if device.strip() == '':
				device = None
			if device is not None:
				return device

		try:
			devices = self.scan_module.get_devices()
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

#		device_names = []
#		for device in devices:
#			device_names.append('%s (%s)' % (device[2], device[0]))

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
	# event handling API
	#--------------------------------------------------------
	def _scan_btn_pressed(self, evt):

		chosen_device = self.get_device_to_use()

		# FIXME: configure whether to use XSane or sane directly
		# FIXME: add support for xsane_device_settings argument
		try:
			fnames = self.scan_module.acquire_pages_into_files (
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

		self.add_parts_from_files(fnames, _('captured by imaging device'))
		return True

	#--------------------------------------------------------
	def _load_btn_pressed(self, evt):
		dlg = wx.FileDialog (
			parent = None,
			message = _('Choose a file'),
			defaultDir = os.path.expanduser(os.path.join('~', 'gnumed')),
			defaultFile = '',
			wildcard = "%s (*)|*|TIFFs (*.tif)|*.tif|JPEGs (*.jpg)|*.jpg|%s (*.*)|*.*" % (_('all files'), _('all files (Win)')),
			style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_MULTIPLE
		)
		result = dlg.ShowModal()
		files = dlg.GetPaths()
		if result == wx.ID_CANCEL:
			dlg.DestroyLater()
			return

		self.add_parts_from_files(files, _('picked from storage media'))

	#--------------------------------------------------------
	def _clipboard_btn_pressed(self, event):
		event.Skip()
		clip = gmGuiHelpers.clipboard2file()
		if clip is None:
			return
		if clip is False:
			return
		self.add_parts_from_files([clip], _('pasted from clipboard'))

	#--------------------------------------------------------
	def _show_btn_pressed(self, evt):

		# nothing to do
		if self._LCTRL_doc_pages.ItemCount == 0:
			return

		# only one page, show that, regardless of whether selected or not
		if self._LCTRL_doc_pages.ItemCount == 1:
			page_fnames = [ self._LCTRL_doc_pages.get_item_data(0)[0] ]
		else:
			# did user select one of multiple pages ?
			page_fnames = [ data[0] for data in self._LCTRL_doc_pages.selected_item_data ]
			if len(page_fnames) == 0:
				gmDispatcher.send(signal = 'statustext', msg = _('No part selected for viewing.'), beep = True)
				return

		for page_fname in page_fnames:
			(success, msg) = gmMimeLib.call_viewer_on_file(page_fname)
			if not success:
				gmGuiHelpers.gm_show_warning (
					aMessage = _('Cannot display document part:\n%s') % msg,
					aTitle = _('displaying part')
				)

	#--------------------------------------------------------
	def _del_btn_pressed(self, event):

		if len(self._LCTRL_doc_pages.selected_items) == 0:
			gmDispatcher.send(signal = 'statustext', msg = _('No part selected for removal.'), beep = True)
			return

		sel_idx = self._LCTRL_doc_pages.GetFirstSelected()
		rows = self._LCTRL_doc_pages.string_items
		data = self._LCTRL_doc_pages.data
		del rows[sel_idx]
		del data[sel_idx]
		self._LCTRL_doc_pages.string_items = rows
		self._LCTRL_doc_pages.data = data
		self._LCTRL_doc_pages.set_column_widths()
		self._TCTRL_metadata.SetValue('')

	#--------------------------------------------------------
	def _save_btn_pressed(self, evt):

		if not self.__valid_for_save():
			return False

		# external reference
		cfg = gmCfg.cCfgSQL()
		generate_uuid = bool (
			cfg.get2 (
				option = 'horstspace.scan_index.generate_doc_uuid',
				workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
				bias = 'user',
				default = False
			)
		)
		if generate_uuid:
			ext_ref = gmDocuments.get_ext_ref()
		else:
			ext_ref = None

		# create document
		date = self._PhWheel_doc_date.GetData()
		if date is not None:
			date = date.get_pydt()
		new_doc = save_files_as_new_document (
			parent = self,
			filenames = [ data[0] for data in self._LCTRL_doc_pages.data ],
			document_type = self._PhWheel_doc_type.GetValue().strip(),
			pk_document_type = self._PhWheel_doc_type.GetData(),
			unlock_patient = False,
			episode = self._PhWheel_episode.GetData(can_create = True, is_open = True, as_instance = True),
			review_as_normal = False,
			reference = ext_ref,
			pk_org_unit = self._PhWheel_source.GetData(),
			date_generated = date,
			comment = self._PRW_doc_comment.GetLineText(0).strip(),
			reviewer = self._PhWheel_reviewer.GetData()
		)
		if new_doc is None:
			return False

		if self._RBTN_org_is_receiver.Value is True:
			new_doc['unit_is_receiver'] = True
			new_doc.save()

		# - long description
		description = self._TBOX_description.GetValue().strip()
		if description != '':
			if not new_doc.add_description(description):
				wx.EndBusyCursor()
				gmGuiHelpers.gm_show_error (
					aMessage = _('Cannot add document description.'),
					aTitle = _('saving document')
				)
				return False

		# set reviewed status
		if self._ChBOX_reviewed.GetValue():
			if not new_doc.set_reviewed (
				technically_abnormal = self._ChBOX_abnormal.GetValue(),
				clinically_relevant = self._ChBOX_relevant.GetValue()
			):
				msg = _('Error setting "reviewed" status of new document.')

		self.__init_ui_data()

		gmHooks.run_hook_script(hook = 'after_new_doc_created')

		return True

	#--------------------------------------------------------
	def _startover_btn_pressed(self, evt):
		self.__init_ui_data()

	#--------------------------------------------------------
	def _reviewed_box_checked(self, evt):
		self._ChBOX_abnormal.Enable(enable = self._ChBOX_reviewed.GetValue())
		self._ChBOX_relevant.Enable(enable = self._ChBOX_reviewed.GetValue())

	#--------------------------------------------------------
	def _on_doc_type_loses_focus(self):
		pk_doc_type = self._PhWheel_doc_type.GetData()
		if pk_doc_type is None:
			self._PRW_doc_comment.unset_context(context = 'pk_doc_type')
		else:
			self._PRW_doc_comment.set_context(context = 'pk_doc_type', val = pk_doc_type)
		return True

	#--------------------------------------------------------
	def _on_update_file_description(self, result):
		status, description = result
		fname, source = self._LCTRL_doc_pages.get_selected_item_data(only_one = True)
		txt = _(
			'Source: %s\n'
			'File: %s\n'
			'\n'
			'%s'
		) % (
			source,
			fname,
			description
		)
		wx.CallAfter(self._TCTRL_metadata.SetValue, txt)

	#--------------------------------------------------------
	def _on_part_selected(self, event):
		event.Skip()
		fname, source = self._LCTRL_doc_pages.get_item_data(item_idx = event.Index)
		self._TCTRL_metadata.SetValue('Retrieving details from [%s] ...' % fname)
		gmMimeLib.describe_file(fname, callback = self._on_update_file_description)

#============================================================
def display_document_part(parent=None, part=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	# sanity check
	if part['size'] == 0:
		_log.debug('cannot display part [%s] - 0 bytes', part['pk_obj'])
		gmGuiHelpers.gm_show_error (
			aMessage = _('Document part does not seem to exist in database !'),
			aTitle = _('showing document')
		)
		return None

	wx.BeginBusyCursor()
	cfg = gmCfg.cCfgSQL()

	# determine database export chunk size
	chunksize = int(
	cfg.get2 (
		option = "horstspace.blob_export_chunk_size",
		workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
		bias = 'workplace',
		default = 2048
	))

	# shall we force blocking during view ?
	block_during_view = bool( cfg.get2 (
		option = 'horstspace.document_viewer.block_during_view',
		workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
		bias = 'user',
		default = None
	))

	wx.EndBusyCursor()

	# display it
	successful, msg = part.display_via_mime (
		chunksize = chunksize,
		block = block_during_view
	)
	if not successful:
		gmGuiHelpers.gm_show_error (
			aMessage = _('Cannot display document part:\n%s') % msg,
			aTitle = _('showing document')
		)
		return None

	# handle review after display
	# 0: never
	# 1: always
	# 2: if no review by myself exists yet
	# 3: if no review at all exists yet
	# 4: if no review by responsible reviewer
	review_after_display = int(cfg.get2 (
		option = 'horstspace.document_viewer.review_after_display',
		workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
		bias = 'user',
		default = 3
	))
	if review_after_display == 1:			# always review
		review_document_part(parent = parent, part = part)
	elif review_after_display == 2:			# review if no review by me exists
		review_by_me = [ rev for rev in part.get_reviews() if rev['is_your_review'] ]
		if len(review_by_me) == 0:
			review_document_part(parent = parent, part = part)
	elif review_after_display == 3:
		if len(part.get_reviews()) == 0:
			review_document_part(parent = parent, part = part)
	elif review_after_display == 4:
		reviewed_by_responsible = [ rev for rev in part.get_reviews() if rev['is_review_by_responsible_reviewer'] ]
		if len(reviewed_by_responsible) == 0:
			review_document_part(parent = parent, part = part)

	return True

#============================================================
def manage_documents(parent=None, msg=None, single_selection=True, pk_types=None, pk_episodes=None):

	pat = gmPerson.gmCurrentPatient()

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	#--------------------------------------------------------
	def edit(document=None):
		return
		#return edit_substance(parent = parent, substance = substance, single_entry = (substance is not None))

	#--------------------------------------------------------
	def delete(document):
		return
#		if substance.is_in_use_by_patients:
#			gmDispatcher.send(signal = 'statustext', msg = _('Cannot delete this substance. It is in use.'), beep = True)
#			return False
#
#		return gmMedication.delete_x_substance(substance = substance['pk'])

	#------------------------------------------------------------
	def refresh(lctrl):
		docs = pat.document_folder.get_documents(pk_types = pk_types, pk_episodes = pk_episodes)
		items = [ [
			gmDateTime.pydt_strftime(d['clin_when'], '%Y %b %d', accuracy = gmDateTime.acc_days),
			d['l10n_type'],
			gmTools.coalesce(d['comment'], ''),
			gmTools.coalesce(d['ext_ref'], ''),
			d['pk_doc']
		] for d in docs ]
		lctrl.set_string_items(items)
		lctrl.set_data(docs)

	#--------------------------------------------------------
	def show_doc(doc):
		if doc is None:
			return
		for fname in doc.save_parts_to_files():
			gmMimeLib.call_viewer_on_file(aFile = fname, block = False)

	#------------------------------------------------------------
	return gmListWidgets.get_choices_from_list (
		parent = parent,
		caption = _('Patient document list'),
		columns = [_('Generated'), _('Type'), _('Comment'), _('Ref #'), '#'],
		single_selection = single_selection,
		#new_callback = edit,
		#edit_callback = edit,
		#delete_callback = delete,
		refresh_callback = refresh,
		left_extra_button = (_('Show'), _('Show all parts of this document in external viewer.'), show_doc)
	)

#============================================================
from Gnumed.wxGladeWidgets import wxgSelectablySortedDocTreePnl

class cSelectablySortedDocTreePnl(wxgSelectablySortedDocTreePnl.wxgSelectablySortedDocTreePnl):
	"""A panel with a document tree which can be sorted.

		On the right there's a list ctrl showing
		details of the selected node.
	"""
	def __init__(self, parent, id, *args, **kwds):
		wxgSelectablySortedDocTreePnl.wxgSelectablySortedDocTreePnl.__init__(self, parent, id, *args, **kwds)

		self._LCTRL_details.set_columns(['', ''])

		self.__metainfo4parts = {}
		self.__pk_curr_pat = None
		self.__pk_curr_doc_part = None

		self._doc_tree.show_details_callback = self._update_details

	#--------------------------------------------------------
	# inherited event handlers
	#--------------------------------------------------------
	def _on_sort_by_age_selected(self, evt):
		self._doc_tree.sort_mode = 'age'
		self._doc_tree.SetFocus()
		self._rbtn_sort_by_age.SetValue(True)

	#--------------------------------------------------------
	def _on_sort_by_review_selected(self, evt):
		self._doc_tree.sort_mode = 'review'
		self._doc_tree.SetFocus()
		self._rbtn_sort_by_review.SetValue(True)

	#--------------------------------------------------------
	def _on_sort_by_episode_selected(self, evt):
		self._doc_tree.sort_mode = 'episode'
		self._doc_tree.SetFocus()
		self._rbtn_sort_by_episode.SetValue(True)

	#--------------------------------------------------------
	def _on_sort_by_issue_selected(self, event):
		self._doc_tree.sort_mode = 'issue'
		self._doc_tree.SetFocus()
		self._rbtn_sort_by_issue.SetValue(True)

	#--------------------------------------------------------
	def _on_sort_by_type_selected(self, evt):
		self._doc_tree.sort_mode = 'type'
		self._doc_tree.SetFocus()
		self._rbtn_sort_by_type.SetValue(True)

	#--------------------------------------------------------
	def _on_sort_by_org_selected(self, evt):
		self._doc_tree.sort_mode = 'org'
		self._doc_tree.SetFocus()
		self._rbtn_sort_by_org.SetValue(True)

	#--------------------------------------------------------
	#--------------------------------------------------------
	def _update_details(self, issue=None, episode=None, org_unit=None, document=None, part=None):

		self._LCTRL_details.set_string_items([])
		self._TCTRL_metainfo.Value = ''

		if document is None:
			if part is not None:
				document = part.document

		if issue is None:
			if episode is not None:
				issue = episode.health_issue

		items = []
		items.extend(self.__process_issue(issue))
		items.extend(self.__process_episode(episode))
		items.extend(self.__process_org_unit(org_unit))
		items.extend(self.__process_document(document))
		# keep this last so self.__pk_curr_doc_part stays current
		items.extend(self.__process_document_part(part))
		self._LCTRL_details.set_string_items(items)
		self._LCTRL_details.set_column_widths()
		self._LCTRL_details.set_resize_column(1)

	#--------------------------------------------------------
	# internal helper logic
	#--------------------------------------------------------
	def __check_cache_validity(self, pk_patient):
		if self.__pk_curr_pat == pk_patient:
			return
		self.__metainfo4parts = {}

	#--------------------------------------------------------
	def __receive_metainfo_from_worker(self, result):
		success, desc, pk_obj = result
		self.__metainfo4parts[pk_obj] = desc
		if not success:
			del self.__metainfo4parts[pk_obj]
		# safely cross thread boundaries
		wx.CallAfter(self.__update_metainfo, pk_obj)

	#--------------------------------------------------------
	def __update_metainfo(self, pk_obj, document_part=None):
		if self.__pk_curr_doc_part != pk_obj:
			# worker result arrived too late
			# but don't empty metainfo, might already contain cached value from new doc part node
			#self._TCTRL_metainfo.Value = ''
			return

		try:
			self._TCTRL_metainfo.Value = self.__metainfo4parts[pk_obj]
		except KeyError:
			document_part.format_metainfo(callback = self.__receive_metainfo_from_worker)

	#--------------------------------------------------------
	def __process_issue(self, issue):
		if issue is None:
			return []

		self.__check_cache_validity(issue['pk_patient'])
		self.__pk_curr_doc_part = None

		items = []
		items.append([_('Health issue'), '%s%s [#%s]' % (
			issue['description'],
			gmTools.coalesce (
				value2test = issue['laterality'],
				return_instead = '',
				template4value = ' (%s)',
				none_equivalents = [None, '', '?']
			),
			issue['pk_health_issue']
		)])
		items.append([_('Status'), '%s, %s %s' % (
			gmTools.bool2subst(issue['is_active'], _('active'), _('inactive')),
			gmTools.bool2subst(issue['clinically_relevant'], _('clinically relevant'), _('not clinically relevant')),
			issue.diagnostic_certainty_description
		)])
		items.append([_('Confidential'), issue['is_confidential']])
		items.append([_('Age noted'), issue.age_noted_human_readable()])
		return items

	#--------------------------------------------------------
	def __process_episode(self, episode):
		if episode is None:
			return []

		self.__check_cache_validity(episode['pk_patient'])
		self.__pk_curr_doc_part = None

		items = []
		items.append([_('Episode'), '%s [#%s]' % (
			episode['description'],
			episode['pk_episode']
		)])
		items.append([_('Status'), '%s %s' % (
			gmTools.bool2subst(episode['episode_open'], _('active'), _('finished')),
			episode.diagnostic_certainty_description
		)])
		items.append([_('Health issue'), gmTools.coalesce(episode['health_issue'], '')])
		return items

	#--------------------------------------------------------
	def __process_org_unit(self, org_unit):
		if org_unit is None:
			return []

		# cannot check for cache validity: no patient reference
		# the doc-part-in-context, however, _will_ have changed
		self.__pk_curr_doc_part = None
		self._TCTRL_metainfo.Value = ''

		items = []
		items.append([_('Organization'), '%s (%s) [#%s]' % (
			org_unit['organization'],
			org_unit['l10n_organization_category'],
			org_unit['pk_org']
		)])
		items.append([_('Department'), '%s%s [#%s]' % (
			org_unit['unit'],
			gmTools.coalesce(org_unit['l10n_unit_category'], '', ' (%s)'),
			org_unit['pk_org_unit']
		)])
		adr = org_unit.address
		if adr is not None:
			lines = adr.format()
			items.append([lines[0], lines[1]])
			for line in lines[2:]:
				items.append(['', line])
		for comm in org_unit.comm_channels:
			items.append([comm['l10n_comm_type'], '%s%s' % (
				comm['url'],
				gmTools.bool2subst(comm['is_confidential'], _(' (confidential)'), '', '')
			)])
		return items

	#--------------------------------------------------------
	def __process_document(self, document):
		if document is None:
			return []

		self.__check_cache_validity(document['pk_patient'])
		self.__pk_curr_doc_part = None

		items = []
		items.append([_('Document'), '%s [#%s]' % (document['l10n_type'], document['pk_doc'])])
		items.append([_('Generated'), gmDateTime.pydt_strftime(document['clin_when'], '%Y %b %d')])
		items.append([_('Health issue'), gmTools.coalesce(document['health_issue'], '', '%%s [#%s]' % document['pk_health_issue'])])
		items.append([_('Episode'), '%s (%s) [#%s]' % (
			document['episode'],
			gmTools.bool2subst(document['episode_open'], _('open'), _('closed')),
			document['pk_episode']
		)])
		if document['pk_org_unit'] is not None:
			if document['unit_is_receiver']:
				header = _('Receiver')
			else:
				header = _('Sender')
			items.append([header, '%s @ %s' % (document['unit'], document['organization'])])
		if document['ext_ref'] is not None:
			items.append([_('Reference'), document['ext_ref']])
		if document['comment'] is not None:
			items.append([_('Comment'), ' / '.join(document['comment'].split('\n'))])
		for proc in document.procedures:
			items.append([_('Procedure'), proc.format (
				left_margin = 0,
				include_episode = False,
				include_codes = False,
				include_address = False,
				include_comm = False,
				include_doc = False
			)])
		stay = document.hospital_stay
		if stay is not None:
			items.append([_('Hospital stay'), stay.format(include_episode = False)])
		for bill in document.bills:
			items.append([_('Bill'), bill.format (
				include_receiver = False,
				include_doc = False
			)])
		items.append([_('Modified'), gmDateTime.pydt_strftime(document['modified_when'], '%Y %b %d')])
		items.append([_('... by'), document['modified_by']])
		items.append([_('# encounter'), document['pk_encounter']])
		return items

	#--------------------------------------------------------
	def __process_document_part(self, document_part):
		if document_part is None:
			return []

		self.__check_cache_validity(document_part['pk_patient'])
		self.__pk_curr_doc_part = document_part['pk_obj']
		self.__update_metainfo(document_part['pk_obj'], document_part)
		items = []
		items.append(['', ''])
		if document_part['seq_idx'] is None:
			items.append([_('Part'), '#%s' % document_part['pk_obj']])
		else:
			items.append([_('Part'), '%s [#%s]' % (document_part['seq_idx'], document_part['pk_obj'])])
		if document_part['obj_comment'] is not None:
			items.append([_('Comment'), document_part['obj_comment']])
		if document_part['filename'] is not None:
			items.append([_('Filename'), document_part['filename']])
		items.append([_('Data size'), gmTools.size2str(document_part['size'])])
		review_parts = []
		if document_part['reviewed_by_you']:
			review_parts.append(_('by you'))
		if document_part['reviewed_by_intended_reviewer']:
			review_parts.append(_('by intended reviewer'))
		review = ', '.join(review_parts)
		if review == '':
			review = gmTools.u_diameter
		items.append([_('Reviewed'), review])
		#items.append([_(u'Reviewed'), gmTools.bool2subst(document_part['reviewed'], review, u'', u'?')])
		return items

#============================================================
class cDocTree(wx.TreeCtrl, gmRegetMixin.cRegetOnPaintMixin, treemixin.ExpansionState):
	"""This wx.TreeCtrl derivative displays a tree view of stored medical documents.

	It listens to document and patient changes and updates itself accordingly.

	This acts on the current patient.
	"""
	_sort_modes = ['age', 'review', 'episode', 'type', 'issue', 'org']
	_root_node_labels = None

	#--------------------------------------------------------
	def __init__(self, parent, id, *args, **kwds):
		"""Set up our specialised tree.
		"""
		kwds['style'] = wx.TR_NO_BUTTONS | wx.NO_BORDER | wx.TR_SINGLE
		wx.TreeCtrl.__init__(self, parent, id, *args, **kwds)

		gmRegetMixin.cRegetOnPaintMixin.__init__(self)

		tmp = _('available documents (%s)')
		unsigned = _('unsigned (%s) on top') % '\u270D'
		cDocTree._root_node_labels = {
			'age': tmp % _('most recent on top'),
			'review': tmp % unsigned,
			'episode': tmp % _('sorted by episode'),
			'issue': tmp % _('sorted by health issue'),
			'type': tmp % _('sorted by type'),
			'org': tmp % _('sorted by organization')
		}

		self.root = None
		self.__sort_mode = 'age'

		self.__expanded_nodes = None
		self.__show_details_callback = None

		self.__build_context_menus()
		self.__register_interests()
		self._schedule_data_reget()

	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def display_selected_part(self, *args, **kwargs):

		node = self.GetSelection()
		node_data = self.GetItemData(node)

		if not isinstance(node_data, gmDocuments.cDocumentPart):
			return True

		self.__display_part(part = node_data)
		return True

	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def _get_sort_mode(self):
		return self.__sort_mode

	def _set_sort_mode(self, mode):
		if mode is None:
			mode = 'age'

		if mode == self.__sort_mode:
			return

		if mode not in cDocTree._sort_modes:
			raise ValueError('invalid document tree sort mode [%s], valid modes: %s' % (mode, cDocTree._sort_modes))

		self.__sort_mode = mode
		self.__expanded_nodes = None

		curr_pat = gmPerson.gmCurrentPatient()
		if not curr_pat.connected:
			return

		self._schedule_data_reget()

	sort_mode = property(_get_sort_mode, _set_sort_mode)

	#--------------------------------------------------------
	def _set_show_details_callback(self, callback):
		if callback is not None:
			if not callable(callback):
				raise ValueError('<%s> is not callable')
		self.__show_details_callback = callback

	show_details_callback = property(lambda x:x, _set_show_details_callback)

	#--------------------------------------------------------
	# reget-on-paint API
	#--------------------------------------------------------
	def _populate_with_data(self):
		curr_pat = gmPerson.gmCurrentPatient()
		if not curr_pat.connected:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot load documents. No active patient.'))
			return False

		if not self.__populate_tree():
			return False

		return True

	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def __register_interests(self):
		self.Bind(wx.EVT_TREE_SEL_CHANGED, self._on_tree_item_selected)
		self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self._on_activate)
		self.Bind(wx.EVT_TREE_ITEM_MENU, self._on_tree_item_context_menu)
		self.Bind(wx.EVT_TREE_ITEM_GETTOOLTIP, self._on_tree_item_gettooltip)

		gmDispatcher.connect(signal = 'pre_patient_unselection', receiver = self._on_pre_patient_unselection)
		gmDispatcher.connect(signal = 'post_patient_selection', receiver = self._on_post_patient_selection)
		gmDispatcher.connect(signal = 'blobs.doc_med_mod_db', receiver = self._on_doc_mod_db)
		gmDispatcher.connect(signal = 'blobs.doc_obj_mod_db', receiver = self._on_doc_page_mod_db)

	#--------------------------------------------------------
	def __build_context_menus(self):

		# --- part context menu ---
		self.__part_context_menu = wx.Menu(title = _('Part Actions:'))

		item = self.__part_context_menu.Append(-1, _('Display part'))
		self.Bind(wx.EVT_MENU, self.__display_curr_part, item)
		item = self.__part_context_menu.Append(-1, _('%s Sign/Edit properties') % '\u270D')
		self.Bind(wx.EVT_MENU, self.__review_curr_part, item)

		self.__part_context_menu.AppendSeparator()

		item = self.__part_context_menu.Append(-1, _('Delete part'))
		self.Bind(wx.EVT_MENU, self.__delete_part, item, item)
		item = self.__part_context_menu.Append(-1, _('Move part'))
		self.Bind(wx.EVT_MENU, self.__move_part, item)
		item = self.__part_context_menu.Append(-1, _('Print part'))
		self.Bind(wx.EVT_MENU, self.__print_part, item)
		item = self.__part_context_menu.Append(-1, _('Fax part'))
		self.Bind(wx.EVT_MENU, self.__fax_part, item)
		item = self.__part_context_menu.Append(-1, _('Mail part'))
		self.Bind(wx.EVT_MENU, self.__mail_part, item)
		item = self.__part_context_menu.Append(-1, _('Save part to disk'))
		self.Bind(wx.EVT_MENU, self.__save_part_to_disk, item)

		self.__part_context_menu.AppendSeparator()			# so we can append more items

		# --- doc context menu ---
		self.__doc_context_menu = wx.Menu(title = _('Document Actions:'))

		item = self.__doc_context_menu.Append(-1, _('%s Sign/Edit properties') % '\u270D')
		self.Bind(wx.EVT_MENU, self.__review_curr_part, item)
		item = self.__doc_context_menu.Append(-1, _('Delete document'))
		self.Bind(wx.EVT_MENU, self.__delete_document, item)

		self.__doc_context_menu.AppendSeparator()

		item = self.__doc_context_menu.Append(-1, _('Add parts'))
		self.Bind(wx.EVT_MENU, self.__add_part, item)
		item = self.__doc_context_menu.Append(-1, _('Add part from clipboard'))
		self.Bind(wx.EVT_MENU, self.__add_part_from_clipboard, item, item)
		item = self.__doc_context_menu.Append(-1, _('Print all parts'))
		self.Bind(wx.EVT_MENU, self.__print_doc, item)
		item = self.__doc_context_menu.Append(-1, _('Fax all parts'))
		self.Bind(wx.EVT_MENU, self.__fax_doc, item)
		item = self.__doc_context_menu.Append(-1, _('Mail all parts'))
		self.Bind(wx.EVT_MENU, self.__mail_doc, item)
		item = self.__doc_context_menu.Append(-1, _('Save all parts to disk'))
		self.Bind(wx.EVT_MENU, self.__save_doc_to_disk, item)
		item = self.__doc_context_menu.Append(-1, _('Copy all parts to export area'))
		self.Bind(wx.EVT_MENU, self.__copy_doc_to_export_area, item)

		self.__doc_context_menu.AppendSeparator()

		item = self.__doc_context_menu.Append(-1, _('Access external original'))
		self.Bind(wx.EVT_MENU, self.__access_external_original, item)
		item = self.__doc_context_menu.Append(-1, _('Edit corresponding encounter'))
		self.Bind(wx.EVT_MENU, self.__edit_encounter_details, item)
		item = self.__doc_context_menu.Append(-1, _('Select corresponding encounter'))
		self.Bind(wx.EVT_MENU, self.__select_encounter, item)
		item = self.__doc_context_menu.Append(-1, _('Manage descriptions'))
		self.Bind(wx.EVT_MENU, self.__manage_document_descriptions, item)

		# document / description
#		self.__desc_menu = wx.Menu()
#		item = self.__doc_context_menu.Append(-1, _('Descriptions ...'), self.__desc_menu)
#		item = self.__desc_menu.Append(-1, _('Add new description'))
#		self.Bind(wx.EVT_MENU, self.__desc_menu, self.__add_doc_desc, item)
#		item = self.__desc_menu.Append(-1, _('Delete description'))
#		self.Bind(wx.EVT_MENU, self.__desc_menu, self.__del_doc_desc, item)
#		self.__desc_menu.AppendSeparator()

	#--------------------------------------------------------
	def __populate_tree(self):

		wx.BeginBusyCursor()
		# clean old tree
		if self.root is not None:
			self.DeleteAllItems()
		self.__show_details_callback(document = None, part = None)
		# init new tree
		self.root = self.AddRoot(cDocTree._root_node_labels[self.__sort_mode], -1, -1)
		self.SetItemData(self.root, None)
		self.SetItemHasChildren(self.root, False)
		# read documents from database
		curr_pat = gmPerson.gmCurrentPatient()
		docs_folder = curr_pat.get_document_folder()
		docs = docs_folder.get_documents()
		if docs is None:
			gmGuiHelpers.gm_show_error (
				aMessage = _('Error searching documents.'),
				aTitle = _('loading document list')
			)
			# avoid recursion of GUI updating
			wx.EndBusyCursor()
			return True

		if len(docs) == 0:
			wx.EndBusyCursor()
			return True

		# fill new tree from document list
		self.SetItemHasChildren(self.root, True)
		# add our documents as first level nodes
		intermediate_nodes = {}
		for doc in docs:
			parts = doc.parts
			if len(parts) == 0:
				no_parts = _('no parts')
			elif len(parts) == 1:
				no_parts = _('1 part')
			else:
				no_parts = _('%s parts') % len(parts)

			# need intermediate branch level ?
			if self.__sort_mode == 'episode':
				intermediate_label = '%s%s' % (doc['episode'], gmTools.coalesce(doc['health_issue'], '', ' (%s)'))
				doc_label = _('%s%7s %s:%s (%s)') % (
					gmTools.bool2subst(doc.has_unreviewed_parts, gmTools.u_writing_hand, '', '?'),
					gmDateTime.pydt_strftime(doc['clin_when'], '%m/%Y'),
					doc['l10n_type'][:26],
					gmTools.coalesce(value2test = doc['comment'], return_instead = '', template4value = ' %s'),
					no_parts
				)
				if intermediate_label not in intermediate_nodes:
					intermediate_nodes[intermediate_label] = self.AppendItem(parent = self.root, text = intermediate_label)
					self.SetItemBold(intermediate_nodes[intermediate_label], bold = True)
					self.SetItemData(intermediate_nodes[intermediate_label], {'pk_episode': doc['pk_episode']})
					self.SetItemHasChildren(intermediate_nodes[intermediate_label], True)
				parent = intermediate_nodes[intermediate_label]

			elif self.__sort_mode == 'type':
				intermediate_label = doc['l10n_type']
				doc_label = _('%s%7s (%s):%s') % (
					gmTools.bool2subst(doc.has_unreviewed_parts, gmTools.u_writing_hand, '', '?'),
					gmDateTime.pydt_strftime(doc['clin_when'], '%m/%Y'),
					no_parts,
					gmTools.coalesce(value2test = doc['comment'], return_instead = '', template4value = ' %s')
				)
				if intermediate_label not in intermediate_nodes:
					intermediate_nodes[intermediate_label] = self.AppendItem(parent = self.root, text = intermediate_label)
					self.SetItemBold(intermediate_nodes[intermediate_label], bold = True)
					self.SetItemData(intermediate_nodes[intermediate_label], None)
					self.SetItemHasChildren(intermediate_nodes[intermediate_label], True)
				parent = intermediate_nodes[intermediate_label]

			elif self.__sort_mode == 'issue':
				if doc['health_issue'] is None:
					intermediate_label = _('%s (unattributed episode)') % doc['episode']
				else:
					intermediate_label = doc['health_issue']
				doc_label = _('%s%7s %s:%s (%s)') % (
					gmTools.bool2subst(doc.has_unreviewed_parts, gmTools.u_writing_hand, '', '?'),
					gmDateTime.pydt_strftime(doc['clin_when'], '%m/%Y'),
					doc['l10n_type'][:26],
					gmTools.coalesce(value2test = doc['comment'], return_instead = '', template4value = ' %s'),
					no_parts
				)
				if intermediate_label not in intermediate_nodes:
					intermediate_nodes[intermediate_label] = self.AppendItem(parent = self.root, text = intermediate_label)
					self.SetItemBold(intermediate_nodes[intermediate_label], bold = True)
					self.SetItemData(intermediate_nodes[intermediate_label], {'pk_health_issue': doc['pk_health_issue']})
					self.SetItemHasChildren(intermediate_nodes[intermediate_label], True)
				parent = intermediate_nodes[intermediate_label]

			elif self.__sort_mode == 'org':
				if doc['pk_org'] is None:
					intermediate_label = _('unknown organization')
				else:
					if doc['unit_is_receiver']:
						direction = _('to: %s')
					else:
						direction = _('from: %s')
					# this praxis ?
					if doc['pk_org'] == gmPraxis.gmCurrentPraxisBranch()['pk_org']:
						org_str = _('this praxis')
					else:
						 org_str = doc['organization']
					intermediate_label = direction % org_str
				doc_label = _('%s%7s %s:%s (%s)') % (
					gmTools.bool2subst(doc.has_unreviewed_parts, gmTools.u_writing_hand, '', '?'),
					gmDateTime.pydt_strftime(doc['clin_when'], '%m/%Y'),
					doc['l10n_type'][:26],
					gmTools.coalesce(value2test = doc['comment'], return_instead = '', template4value = ' %s'),
					no_parts
				)
				if intermediate_label not in intermediate_nodes:
					intermediate_nodes[intermediate_label] = self.AppendItem(parent = self.root, text = intermediate_label)
					self.SetItemBold(intermediate_nodes[intermediate_label], bold = True)
					# not quite right: always shows data of the _last_ document of _any_ org unit of this org
					self.SetItemData(intermediate_nodes[intermediate_label], doc.org_unit)
					self.SetItemHasChildren(intermediate_nodes[intermediate_label], True)
				parent = intermediate_nodes[intermediate_label]

			elif self.__sort_mode == 'age':
				intermediate_label = gmDateTime.pydt_strftime(doc['clin_when'], '%Y')
				doc_label = _('%s%7s %s:%s (%s)') % (
					gmTools.bool2subst(doc.has_unreviewed_parts, gmTools.u_writing_hand, '', '?'),
					gmDateTime.pydt_strftime(doc['clin_when'], '%b %d'),
					doc['l10n_type'][:26],
					gmTools.coalesce(value2test = doc['comment'], return_instead = '', template4value = ' %s'),
					no_parts
				)
				if intermediate_label not in intermediate_nodes:
					intermediate_nodes[intermediate_label] = self.AppendItem(parent = self.root, text = intermediate_label)
					self.SetItemBold(intermediate_nodes[intermediate_label], bold = True)
					self.SetItemData(intermediate_nodes[intermediate_label], doc['clin_when'])
					self.SetItemHasChildren(intermediate_nodes[intermediate_label], True)
				parent = intermediate_nodes[intermediate_label]

			else:
				doc_label = _('%s%7s %s:%s (%s)') % (
					gmTools.bool2subst(doc.has_unreviewed_parts, gmTools.u_writing_hand, '', '?'),
					gmDateTime.pydt_strftime(doc['clin_when'], '%Y-%m'),
					doc['l10n_type'][:26],
					gmTools.coalesce(value2test = doc['comment'], return_instead = '', template4value = ' %s'),
					no_parts
				)
				parent = self.root

			doc_node = self.AppendItem(parent = parent, text = doc_label)
			#self.SetItemBold(doc_node, bold = True)
			self.SetItemData(doc_node, doc)
			if len(parts) == 0:
				self.SetItemHasChildren(doc_node, False)
			else:
				self.SetItemHasChildren(doc_node, True)
			# now add parts as child nodes
			for part in parts:
				f_ext = ''
				if part['filename'] is not None:
					f_ext = os.path.splitext(part['filename'])[1].strip('.').strip()
				if f_ext != '':
					f_ext = ' .' + f_ext.upper()
				label = '%s%s (%s%s)%s' % (
					gmTools.bool2str (
						boolean = part['reviewed'] or part['reviewed_by_you'] or part['reviewed_by_intended_reviewer'],
						true_str = '',
						false_str = gmTools.u_writing_hand
					),
					_('part %2s') % part['seq_idx'],
					gmTools.size2str(part['size']),
					f_ext,
					gmTools.coalesce (
						part['obj_comment'],
						'',
						': %s%%s%s' % (gmTools.u_left_double_angle_quote, gmTools.u_right_double_angle_quote)
					)
				)

				part_node = self.AppendItem(parent = doc_node, text = label)
				self.SetItemData(part_node, part)
				self.SetItemHasChildren(part_node, False)

		self.__sort_nodes()
		self.SelectItem(self.root)
		# restore expansion state
		if self.__expanded_nodes is not None:
			self.ExpansionState = self.__expanded_nodes
		# but always expand root node
		self.Expand(self.root)
		# if no expansion state available then
		# expand intermediate nodes as well
		if self.__expanded_nodes is None:
			# but only if there are any
			if self.__sort_mode in ['episode', 'type', 'issue', 'org']:
				for key in intermediate_nodes:
					self.Expand(intermediate_nodes[key])
		wx.EndBusyCursor()
		return True

	#------------------------------------------------------------------------
	def OnCompareItems (self, node1=None, node2=None):
		"""Used in sorting items.

		-1: 1 < 2
		 0: 1 = 2
		 1: 1 > 2
		"""
		# Windows can send bogus events so ignore that
		if not node1:
			_log.debug('invalid node 1')
			return 0
		if not node2:
			_log.debug('invalid node 2')
			return 0
		if not node1.IsOk():
			_log.debug('no data on node 1')
			return 0
		if not node2.IsOk():
			_log.debug('no data on node 2')
			return 0

		data1 = self.GetItemData(node1)
		data2 = self.GetItemData(node2)

		# doc node
		if isinstance(data1, gmDocuments.cDocument):
			date_field = 'clin_when'
			#date_field = 'modified_when'
			if self.__sort_mode == 'age':
				# reverse sort by date
				if data1[date_field] > data2[date_field]:
					return -1
				if data1[date_field] == data2[date_field]:
					return 0
				return 1
			if self.__sort_mode == 'episode':
				if data1['episode'] < data2['episode']:
					return -1
				if data1['episode'] == data2['episode']:
					# inner sort: reverse by date
					if data1[date_field] > data2[date_field]:
						return -1
					if data1[date_field] == data2[date_field]:
						return 0
					return 1
				return 1
			if self.__sort_mode == 'issue':
				if data1['health_issue'] == data2['health_issue']:
					# inner sort: reverse by date
					if data1[date_field] > data2[date_field]:
						return -1
					if data1[date_field] == data2[date_field]:
						return 0
					return 1
				if data1['health_issue'] < data2['health_issue']:
					return -1
				return 1
			if self.__sort_mode == 'review':
				# equality
				if data1.has_unreviewed_parts == data2.has_unreviewed_parts:
					# inner sort: reverse by date
					if data1[date_field] > data2[date_field]:
						return -1
					if data1[date_field] == data2[date_field]:
						return 0
					return 1
				if data1.has_unreviewed_parts:
					return -1
				return 1
			if self.__sort_mode == 'type':
				if data1['l10n_type'] < data2['l10n_type']:
					return -1
				if data1['l10n_type'] == data2['l10n_type']:
					# inner sort: reverse by date
					if data1[date_field] > data2[date_field]:
						return -1
					if data1[date_field] == data2[date_field]:
						return 0
					return 1
				return 1
			if self.__sort_mode == 'org':
				if (data1['organization'] is None) and (data2['organization'] is None):
					return 0
				if (data1['organization'] is None) and (data2['organization'] is not None):
					return 1
				if (data1['organization'] is not None) and (data2['organization'] is None):
					return -1
				txt1 = '%s %s' % (data1['organization'], data1['unit'])
				txt2 = '%s %s' % (data2['organization'], data2['unit'])
				if txt1 < txt2:
					return -1
				if txt1 == txt2:
					# inner sort: reverse by date
					if data1[date_field] > data2[date_field]:
						return -1
					if data1[date_field] == data2[date_field]:
						return 0
					return 1
				return 1

			_log.error('unknown document sort mode [%s], reverse-sorting by age', self.__sort_mode)
			# reverse sort by date
			if data1[date_field] > data2[date_field]:
				return -1
			if data1[date_field] == data2[date_field]:
				return 0
			return 1

		# part node
		if isinstance(data1, gmDocuments.cDocumentPart):
			# compare sequence IDs (= "page" numbers)
			# FIXME: wrong order ?
			if data1['seq_idx'] < data2['seq_idx']:
				return -1
			if data1['seq_idx'] == data2['seq_idx']:
				return 0
			return 1

		# org unit node
		if isinstance(data1, gmOrganization.cOrgUnit):
			l1 = self.GetItemText(node1)
			l2 = self.GetItemText(node2)
			if l1 < l2:
				return -1
			if l1 == l2:
				return 0
			return 1

		# episode or issue node
		if isinstance(data1, dict):
			if ('pk_episode' in data1) or ('pk_health_issue' in data1):
				l1 = self.GetItemText(node1)
				l2 = self.GetItemText(node2)
				if l1 < l2:
					return -1
				if l1 == l2:
					return 0
				return 1
			_log.error('dict but unknown structure: %s', list(data1))
			return 1

		# doc.year node
		if isinstance(data1, pydt.datetime):
			y1 = gmDateTime.pydt_strftime(data1, '%Y')
			y2 = gmDateTime.pydt_strftime(data2, '%Y')
			# reverse chronologically
			if y1 < y2:
				return 1
			if y1 == y2:
				return 0
			return -1

		# type node
		# else sort alphabetically by label
		if None in [data1, data2]:
			l1 = self.GetItemText(node1)
			l2 = self.GetItemText(node2)
			if l1 < l2:
				return -1
			if l1 == l2:
				return 0
		else:
			if data1 < data2:
				return -1
			if data1 == data2:
				return 0
		return 1

	#------------------------------------------------------------------------
	# event handlers
	#------------------------------------------------------------------------
	def _on_doc_mod_db(self, *args, **kwargs):
		self.__expanded_nodes = self.ExpansionState
		self._schedule_data_reget()

	#------------------------------------------------------------------------
	def _on_doc_page_mod_db(self, *args, **kwargs):
		self.__expanded_nodes = self.ExpansionState
		self._schedule_data_reget()

	#------------------------------------------------------------------------
	def _on_pre_patient_unselection(self, *args, **kwargs):
		if self.root is not None:
			self.DeleteAllItems()
		self.root = None

	#------------------------------------------------------------------------
	def _on_post_patient_selection(self, *args, **kwargs):
		# FIXME: self.__load_expansion_history_from_db (but not apply it !)
		self.__expanded_nodes = None
		self._schedule_data_reget()

	#--------------------------------------------------------
	def __update_details_view(self):
		# pseudo root node or "type"
		if self.__curr_node_data is None:
			self.__show_details_callback(document = None, part = None)
			return

		# document node
		if isinstance(self.__curr_node_data, gmDocuments.cDocument):
			self.__show_details_callback(document = self.__curr_node_data, part = None)
			return

		if isinstance(self.__curr_node_data, gmDocuments.cDocumentPart):
			doc = self.GetItemData(self.GetItemParent(self.__curr_node))
			self.__show_details_callback(document = doc, part = self.__curr_node_data)
			return

		if isinstance(self.__curr_node_data, gmOrganization.cOrgUnit):
			self.__show_details_callback(org_unit = self.__curr_node_data)
			return

		if isinstance(self.__curr_node_data, pydt.datetime):
			# could be getting some statistics about the year
			return

		if isinstance(self.__curr_node_data, dict):
			try:
				issue = gmEMRStructItems.cHealthIssue(aPK_obj = self.__curr_node_data['pk_health_issue'])
			except KeyError:
				_log.debug('node data dict holds pseudo-issue for unattributed episodes, ignoring')
				issue = None
			try:
				episode = gmEMRStructItems.cEpisode(aPK_obj = self.__curr_node_data['pk_episode'])
			except KeyError:
				episode = None
			self.__show_details_callback(issue = issue, episode = episode)
			return

#		# string nodes are labels such as episodes which may or may not have children
#		if isinstance(self.__curr_node_data, str):
#			self.__show_details_callback(document = None, part = None)
#			return

		raise ValueError('invalid document tree node data type: %s' % type(self.__curr_node_data))

	#--------------------------------------------------------
	def _on_tree_item_selected(self, event):
		event.Skip()
		self.__curr_node = event.GetItem()
		self.__curr_node_data = self.GetItemData(self.__curr_node)
		self.__update_details_view()

	#------------------------------------------------------------------------
	def _on_activate(self, event):
		node = event.GetItem()
		node_data = self.GetItemData(node)

		# exclude pseudo root node
		if node_data is None:
			return None

		if isinstance(node_data, gmDocuments.cDocumentPart):
			self.__display_part(part = node_data)
			return True

		event.Skip()

	#--------------------------------------------------------
	def _on_tree_item_context_menu(self, evt):

		self.__curr_node_data = self.GetItemData(evt.Item)

		# exclude pseudo root node
		if self.__curr_node_data is None:
			return None

		# documents
		if isinstance(self.__curr_node_data, gmDocuments.cDocument):
			self.__handle_doc_context()

		# parts
		if isinstance(self.__curr_node_data, gmDocuments.cDocumentPart):
			self.__handle_part_context()

		del self.__curr_node_data
		evt.Skip()

	#--------------------------------------------------------
	def __activate_as_current_photo(self, evt):
		self.__curr_node_data.set_as_active_photograph()

	#--------------------------------------------------------
	def __display_curr_part(self, evt):
		self.__display_part(part = self.__curr_node_data)

	#--------------------------------------------------------
	def __review_curr_part(self, evt):
		self.__review_part(part = self.__curr_node_data)

	#--------------------------------------------------------
	def __manage_document_descriptions(self, evt):
		manage_document_descriptions(parent = self, document = self.__curr_node_data)

	#--------------------------------------------------------
	def _on_tree_item_gettooltip(self, event):

		item = event.GetItem()

		if not item.IsOk():
			event.SetToolTip('')
			return

		data = self.GetItemData(item)
		# documents, parts
		if isinstance(data, (gmDocuments.cDocument, gmDocuments.cDocumentPart)):
			tt = data.format()
		elif isinstance(data, gmOrganization.cOrgUnit):
			tt = '\n'.join(data.format(with_address = True, with_org = True, with_comms = True))
		elif isinstance(data, dict):
			try:
				tt = data['tooltip']
			except KeyError:
				tt = ''
#		# explicit tooltip strings
#		elif isinstance(data, str):
#			tt = data
#		# other (root, "None")
		else:
			tt = ''

		event.SetToolTip(tt)

	#--------------------------------------------------------
	# internal API
	#--------------------------------------------------------
	def __sort_nodes(self, start_node=None):

		if start_node is None:
			start_node = self.GetRootItem()

		# protect against empty tree where not even
		# a root node exists
		if not start_node.IsOk():
			return True

		self.SortChildren(start_node)

		child_node, cookie = self.GetFirstChild(start_node)
		while child_node.IsOk():
			self.__sort_nodes(start_node = child_node)
			child_node, cookie = self.GetNextChild(start_node, cookie)

		return

	#--------------------------------------------------------
	def __handle_doc_context(self):
		self.PopupMenu(self.__doc_context_menu, wx.DefaultPosition)

	#--------------------------------------------------------
	def __handle_part_context(self):
		ID = None
		# make active patient photograph
		if self.__curr_node_data['type'] == 'patient photograph':
			item = self.__part_context_menu.Append(-1, _('Activate as current photo'))
			self.Bind(wx.EVT_MENU, self.__activate_as_current_photo, item)
			ID = item.Id

		self.PopupMenu(self.__part_context_menu, wx.DefaultPosition)

		if ID is not None:
			self.__part_context_menu.Delete(ID)

	#--------------------------------------------------------
	# part level context menu handlers
	#--------------------------------------------------------
	def __display_part(self, part):
		"""Display document part."""

		# sanity check
		if part['size'] == 0:
			_log.debug('cannot display part [%s] - 0 bytes', part['pk_obj'])
			gmGuiHelpers.gm_show_error (
				aMessage = _('Document part does not seem to exist in database !'),
				aTitle = _('showing document')
			)
			return None

		wx.BeginBusyCursor()

		cfg = gmCfg.cCfgSQL()

		# determine database export chunk size
		chunksize = int(
		cfg.get2 (
			option = "horstspace.blob_export_chunk_size",
			workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
			bias = 'workplace',
			default = default_chunksize
		))

		# shall we force blocking during view ?
		block_during_view = bool( cfg.get2 (
			option = 'horstspace.document_viewer.block_during_view',
			workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
			bias = 'user',
			default = None
		))

		# display it
		successful, msg = part.display_via_mime (
			chunksize = chunksize,
			block = block_during_view
		)

		wx.EndBusyCursor()

		if not successful:
			gmGuiHelpers.gm_show_error (
				aMessage = _('Cannot display document part:\n%s') % msg,
				aTitle = _('showing document')
			)
			return None

		# handle review after display
		# 0: never
		# 1: always
		# 2: if no review by myself exists yet
		# 3: if no review at all exists yet
		# 4: if no review by responsible reviewer
		review_after_display = int(cfg.get2 (
			option = 'horstspace.document_viewer.review_after_display',
			workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
			bias = 'user',
			default = 3
		))
		if review_after_display == 1:			# always review
			self.__review_part(part=part)
		elif review_after_display == 2:			# review if no review by me exists
			review_by_me = [ rev for rev in part.get_reviews() if rev['is_your_review'] ]
			if len(review_by_me) == 0:
				self.__review_part(part = part)
		elif review_after_display == 3:
			if len(part.get_reviews()) == 0:
				self.__review_part(part = part)
		elif review_after_display == 4:
			reviewed_by_responsible = [ rev for rev in part.get_reviews() if rev['is_review_by_responsible_reviewer'] ]
			if len(reviewed_by_responsible) == 0:
				self.__review_part(part = part)
		return True

	#--------------------------------------------------------
	def __review_part(self, part=None):
		dlg = cReviewDocPartDlg (
			parent = self,
			id = -1,
			part = part
		)
		dlg.ShowModal()
		dlg.DestroyLater()
	#--------------------------------------------------------
	def __move_part(self, evt):
		target_doc = manage_documents (
			parent = self,
			msg = _('\nSelect the document into which to move the selected part !\n')
		)
		if target_doc is None:
			return
		if not self.__curr_node_data.reattach(pk_doc = target_doc['pk_doc']):
			gmGuiHelpers.gm_show_error (
				aMessage = _('Cannot move document part.'),
				aTitle = _('Moving document part')
			)
	#--------------------------------------------------------
	def __delete_part(self, evt):
		delete_it = gmGuiHelpers.gm_show_question (
			cancel_button = True,
			title = _('Deleting document part'),
			question = _(
				'Are you sure you want to delete the %s part #%s\n'
				'\n'
				'%s'
				'from the following document\n'
				'\n'
				' %s (%s)\n'
				'%s'
				'\n'
				'Really delete ?\n'
				'\n'
				'(this action cannot be reversed)'
			) % (
				gmTools.size2str(self.__curr_node_data['size']),
				self.__curr_node_data['seq_idx'],
				gmTools.coalesce(self.__curr_node_data['obj_comment'], '', ' "%s"\n\n'),
				self.__curr_node_data['l10n_type'],
				gmDateTime.pydt_strftime(self.__curr_node_data['date_generated'], format = '%Y-%m-%d', accuracy = gmDateTime.acc_days),
				gmTools.coalesce(self.__curr_node_data['doc_comment'], '', ' "%s"\n')
			)
		)
		if not delete_it:
			return

		gmDocuments.delete_document_part (
			part_pk = self.__curr_node_data['pk_obj'],
			encounter_pk = gmPerson.gmCurrentPatient().emr.active_encounter['pk_encounter']
		)
	#--------------------------------------------------------
	def __process_part(self, action=None, l10n_action=None):

		gmHooks.run_hook_script(hook = 'before_%s_doc_part' % action)

		wx.BeginBusyCursor()

		# detect wrapper
		found, external_cmd = gmShellAPI.detect_external_binary('gm-%s_doc' % action)
		if not found:
			found, external_cmd = gmShellAPI.detect_external_binary('gm-%s_doc.bat' % action)
		if not found:
			_log.error('neither of gm-%s_doc or gm-%s_doc.bat found', action, action)
			wx.EndBusyCursor()
			gmGuiHelpers.gm_show_error (
				_('Cannot %(l10n_action)s document part - %(l10n_action)s command not found.\n'
				  '\n'
				  'Either of gm-%(action)s_doc or gm-%(action)s_doc.bat\n'
				  'must be in the execution path. The command will\n'
				  'be passed the filename to %(l10n_action)s.'
				) % {'action': action, 'l10n_action': l10n_action},
				_('Processing document part: %s') % l10n_action
			)
			return

		cfg = gmCfg.cCfgSQL()

		# determine database export chunk size
		chunksize = int(cfg.get2 (
			option = "horstspace.blob_export_chunk_size",
			workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
			bias = 'workplace',
			default = default_chunksize
		))

		part_file = self.__curr_node_data.save_to_file(aChunkSize = chunksize)

		if action == 'print':
			cmd = '%s generic_document %s' % (external_cmd, part_file)
		else:
			cmd = '%s %s' % (external_cmd, part_file)
		if os.name == 'nt':
			blocking = True
		else:
			blocking = False
		success = gmShellAPI.run_command_in_shell (
			command = cmd,
			blocking = blocking
		)

		wx.EndBusyCursor()

		if not success:
			_log.error('%s command failed: [%s]', action, cmd)
			gmGuiHelpers.gm_show_error (
				_('Cannot %(l10n_action)s document part - %(l10n_action)s command failed.\n'
				  '\n'
				  'You may need to check and fix either of\n'
				  ' gm-%(action)s_doc (Unix/Mac) or\n'
				  ' gm-%(action)s_doc.bat (Windows)\n'
				  '\n'
				  'The command is passed the filename to %(l10n_action)s.'
				) % {'action': action, 'l10n_action': l10n_action},
				_('Processing document part: %s') % l10n_action
			)
		else:
			if action == 'mail':
				curr_pat = gmPerson.gmCurrentPatient()
				emr = curr_pat.emr
				emr.add_clin_narrative (
					soap_cat = None,
					note =  _('document part handed over to email program: %s') % self.__curr_node_data.format(single_line = True),
					episode = self.__curr_node_data['pk_episode']
				)
	#--------------------------------------------------------
	def __print_part(self, evt):
		self.__process_part(action = 'print', l10n_action = _('print'))
	#--------------------------------------------------------
	def __fax_part(self, evt):
		self.__process_part(action = 'fax', l10n_action = _('fax'))
	#--------------------------------------------------------
	def __mail_part(self, evt):
		self.__process_part(action = 'mail', l10n_action = _('mail'))
	#--------------------------------------------------------
	def __save_part_to_disk(self, evt):
		"""Save document part into directory."""
		dlg = wx.DirDialog (
			parent = self,
			message = _('Save document part to directory ...'),
			defaultPath = os.path.expanduser(os.path.join('~', 'gnumed')),
			style = wx.DD_DEFAULT_STYLE
		)
		result = dlg.ShowModal()
		dirname = dlg.GetPath()
		dlg.DestroyLater()

		if result != wx.ID_OK:
			return True

		wx.BeginBusyCursor()

		pat = gmPerson.gmCurrentPatient()
		fname = self.__curr_node_data.get_useful_filename (
			patient = pat,
			make_unique = True,
			directory = dirname
		)

		cfg = gmCfg.cCfgSQL()

		# determine database export chunk size
		chunksize = int(cfg.get2 (
			option = "horstspace.blob_export_chunk_size",
			workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
			bias = 'workplace',
			default = default_chunksize
		))

		fname = self.__curr_node_data.save_to_file (
			aChunkSize = chunksize,
			filename = fname,
			target_mime = None
		)

		wx.EndBusyCursor()

		gmDispatcher.send(signal = 'statustext', msg = _('Successfully saved document part as [%s].') % fname)

		return True

	#--------------------------------------------------------
	# document level context menu handlers
	#--------------------------------------------------------
	def __select_encounter(self, evt):
		enc = gmEncounterWidgets.select_encounters (
			parent = self,
			patient = gmPerson.gmCurrentPatient()
		)
		if not enc:
			return
		self.__curr_node_data['pk_encounter'] = enc['pk_encounter']
		self.__curr_node_data.save()
	#--------------------------------------------------------
	def __edit_encounter_details(self, evt):
		enc = gmEMRStructItems.cEncounter(aPK_obj = self.__curr_node_data['pk_encounter'])
		gmEncounterWidgets.edit_encounter(parent = self, encounter = enc)
	#--------------------------------------------------------
	def __process_doc(self, action=None, l10n_action=None):

		gmHooks.run_hook_script(hook = 'before_%s_doc' % action)

		wx.BeginBusyCursor()

		# detect wrapper
		found, external_cmd = gmShellAPI.detect_external_binary('gm-%s_doc' % action)
		if not found:
			found, external_cmd = gmShellAPI.detect_external_binary('gm-%s_doc.bat' % action)
		if not found:
			_log.error('neither of gm-%s_doc or gm-%s_doc.bat found', action, action)
			wx.EndBusyCursor()
			gmGuiHelpers.gm_show_error (
				_('Cannot %(l10n_action)s document - %(l10n_action)s command not found.\n'
				  '\n'
				  'Either of gm-%(action)s_doc or gm-%(action)s_doc.bat\n'
				  'must be in the execution path. The command will\n'
				  'be passed a list of filenames to %(l10n_action)s.'
				) % {'action': action, 'l10n_action': l10n_action},
				_('Processing document: %s') % l10n_action
			)
			return

		cfg = gmCfg.cCfgSQL()

		# determine database export chunk size
		chunksize = int(cfg.get2 (
			option = "horstspace.blob_export_chunk_size",
			workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
			bias = 'workplace',
			default = default_chunksize
		))

		part_files = self.__curr_node_data.save_parts_to_files(chunksize = chunksize)

		if os.name == 'nt':
			blocking = True
		else:
			blocking = False

		if action == 'print':
			cmd = '%s %s %s' % (
				external_cmd,
				'generic_document',
				' '.join(part_files)
			)
		else:
			cmd = external_cmd + ' ' + ' '.join(part_files)
		success = gmShellAPI.run_command_in_shell (
			command = cmd,
			blocking = blocking
		)

		wx.EndBusyCursor()

		if not success:
			_log.error('%s command failed: [%s]', action, cmd)
			gmGuiHelpers.gm_show_error (
				_('Cannot %(l10n_action)s document - %(l10n_action)s command failed.\n'
				  '\n'
				  'You may need to check and fix either of\n'
				  ' gm-%(action)s_doc (Unix/Mac) or\n'
				  ' gm-%(action)s_doc.bat (Windows)\n'
				  '\n'
				  'The command is passed a list of filenames to %(l10n_action)s.'
				) % {'action': action, 'l10n_action': l10n_action},
				_('Processing document: %s') % l10n_action
			)

	#--------------------------------------------------------
	def __print_doc(self, evt):
		self.__process_doc(action = 'print', l10n_action = _('print'))

	#--------------------------------------------------------
	def __fax_doc(self, evt):
		self.__process_doc(action = 'fax', l10n_action = _('fax'))

	#--------------------------------------------------------
	def __mail_doc(self, evt):
		self.__process_doc(action = 'mail', l10n_action = _('mail'))

	#--------------------------------------------------------
	def __add_part(self, evt):
		dlg = wx.FileDialog (
			parent = self,
			message = _('Choose a file'),
			defaultDir = os.path.expanduser(os.path.join('~', 'gnumed')),
			defaultFile = '',
			wildcard = "%s (*)|*|PNGs (*.png)|*.png|PDFs (*.pdf)|*.pdf|TIFFs (*.tif)|*.tif|JPEGs (*.jpg)|*.jpg|%s (*.*)|*.*" % (_('all files'), _('all files (Win)')),
			style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_MULTIPLE
		)
		result = dlg.ShowModal()
		if result != wx.ID_CANCEL:
			self.__curr_node_data.add_parts_from_files(files = dlg.GetPaths(), reviewer = gmStaff.gmCurrentProvider()['pk_staff'])
		dlg.DestroyLater()

	#--------------------------------------------------------
	def __add_part_from_clipboard(self, evt):
		clip = gmGuiHelpers.clipboard2file()
		if clip is None:
			return
		if clip is False:
			return
		gmMimeLib.call_viewer_on_file(clip, block = False)
		really_add = gmGuiHelpers.gm_show_question (
			question = _('Really add the displayed clipboard item into the document ?'),
			title = _('Document part from clipboard')
		)
		if not really_add:
			return
		self.__curr_node_data.add_parts_from_files(files = [clip], reviewer = gmStaff.gmCurrentProvider()['pk_staff'])
	#--------------------------------------------------------
	def __access_external_original(self, evt):

		gmHooks.run_hook_script(hook = 'before_external_doc_access')

		wx.BeginBusyCursor()

		# detect wrapper
		found, external_cmd = gmShellAPI.detect_external_binary('gm_access_external_doc.sh')
		if not found:
			found, external_cmd = gmShellAPI.detect_external_binary('gm_access_external_doc.bat')
		if not found:
			_log.error('neither of gm_access_external_doc.sh or .bat found')
			wx.EndBusyCursor()
			gmGuiHelpers.gm_show_error (
				_('Cannot access external document - access command not found.\n'
				  '\n'
				  'Either of gm_access_external_doc.sh or *.bat must be\n'
				  'in the execution path. The command will be passed the\n'
				  'document type and the reference URL for processing.'
				),
				_('Accessing external document')
			)
			return

		cmd = '%s "%s" "%s"' % (external_cmd, self.__curr_node_data['type'], self.__curr_node_data['ext_ref'])
		if os.name == 'nt':
			blocking = True
		else:
			blocking = False
		success = gmShellAPI.run_command_in_shell (
			command = cmd,
			blocking = blocking
		)

		wx.EndBusyCursor()

		if not success:
			_log.error('External access command failed: [%s]', cmd)
			gmGuiHelpers.gm_show_error (
				_('Cannot access external document - access command failed.\n'
				  '\n'
				  'You may need to check and fix either of\n'
				  ' gm_access_external_doc.sh (Unix/Mac) or\n'
				  ' gm_access_external_doc.bat (Windows)\n'
				  '\n'
				  'The command is passed the document type and the\n'
				  'external reference URL on the command line.'
				),
				_('Accessing external document')
			)
	#--------------------------------------------------------
	def __save_doc_to_disk(self, evt):
		"""Save document into directory.

		- one file per object
		- into subdirectory named after patient
		"""
		pat = gmPerson.gmCurrentPatient()
		def_dir = os.path.expanduser(os.path.join('~', 'gnumed', pat.subdir_name))
		gmTools.mkdir(def_dir)

		dlg = wx.DirDialog (
			parent = self,
			message = _('Save document into directory ...'),
			defaultPath = def_dir,
			style = wx.DD_DEFAULT_STYLE
		)
		result = dlg.ShowModal()
		dirname = dlg.GetPath()
		dlg.DestroyLater()

		if result != wx.ID_OK:
			return True

		wx.BeginBusyCursor()

		cfg = gmCfg.cCfgSQL()

		# determine database export chunk size
		chunksize = int(cfg.get2 (
			option = "horstspace.blob_export_chunk_size",
			workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
			bias = 'workplace',
			default = default_chunksize
		))

		fnames = self.__curr_node_data.save_parts_to_files(export_dir = dirname, chunksize = chunksize)

		wx.EndBusyCursor()

		gmDispatcher.send(signal='statustext', msg=_('Successfully saved %s parts into the directory [%s].') % (len(fnames), dirname))

		return True

	#--------------------------------------------------------
	def __copy_doc_to_export_area(self, evt):
		gmPerson.gmCurrentPatient().export_area.add_documents(documents = [self.__curr_node_data])

	#--------------------------------------------------------
	def __delete_document(self, evt):
		delete_it = gmGuiHelpers.gm_show_question (
			aMessage = _('Are you sure you want to delete the document ?'),
			aTitle = _('Deleting document')
		)
		if delete_it is True:
			curr_pat = gmPerson.gmCurrentPatient()
			emr = curr_pat.emr
			enc = emr.active_encounter
			gmDocuments.delete_document(document_id = self.__curr_node_data['pk_doc'], encounter_id = enc['pk_encounter'])

#============================================================
#============================================================
# PACS
#============================================================
from Gnumed.wxGladeWidgets.wxgPACSPluginPnl import wxgPACSPluginPnl

class cPACSPluginPnl(wxgPACSPluginPnl, gmRegetMixin.cRegetOnPaintMixin):

	def __init__(self, *args, **kwargs):
		wxgPACSPluginPnl.__init__(self, *args, **kwargs)
		gmRegetMixin.cRegetOnPaintMixin.__init__(self)
		self.__pacs = None
		self.__patient = gmPerson.gmCurrentPatient()
		self.__orthanc_patient = None
		self.__image_data = None

		self.__init_ui()
		self.__register_interests()

	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def __init_ui(self):

		pool = gmConnectionPool.gmConnectionPool()
		self._TCTRL_host.Value = gmTools.coalesce(pool.credentials.host, 'localhost')
		self._TCTRL_port.Value = '8042'

		self._LCTRL_studies.set_columns(columns = [_('Date'), _('Description'), _('Organization'), _('Authority')])
		self._LCTRL_studies.select_callback = self._on_studies_list_item_selected
		self._LCTRL_studies.deselect_callback = self._on_studies_list_item_deselected

		self._LCTRL_series.set_columns(columns = [_('Time'), _('Method'), _('Body part'), _('Description')])
		self._LCTRL_series.select_callback = self._on_series_list_item_selected
		self._LCTRL_series.deselect_callback = self._on_series_list_item_deselected

		self._LCTRL_details.set_columns(columns = [_('DICOM field'), _('Value')])
		self._LCTRL_details.set_column_widths()

		self._BMP_preview.SetBitmap(wx.Bitmap.FromRGBA(50,50, red=0, green=0, blue=0, alpha = wx.ALPHA_TRANSPARENT))

		# pre-make thumbnail context menu
		self.__thumbnail_menu = wx.Menu()
		item = self.__thumbnail_menu.Append(-1, _('Show in DICOM viewer'))
		self.Bind(wx.EVT_MENU, self._on_show_image_as_dcm, item)
		item = self.__thumbnail_menu.Append(-1, _('Show in image viewer'))
		self.Bind(wx.EVT_MENU, self._on_show_image_as_png, item)
		self.__thumbnail_menu.AppendSeparator()
		item = self.__thumbnail_menu.Append(-1, _('Copy to export area'))
		self.Bind(wx.EVT_MENU, self._on_copy_image_to_export_area, item)
		item = self.__thumbnail_menu.Append(-1, _('Save as DICOM file (.dcm)'))
		self.Bind(wx.EVT_MENU, self._on_save_image_as_dcm, item)
		item = self.__thumbnail_menu.Append(-1, _('Save as image file (.png)'))
		self.Bind(wx.EVT_MENU, self._on_save_image_as_png, item)

		# pre-make studies context menu
		self.__studies_menu = wx.Menu('Studies:')
		self.__studies_menu.AppendSeparator()
		item = self.__studies_menu.Append(-1, _('Show in DICOM viewer'))
		self.Bind(wx.EVT_MENU, self._on_studies_show_button_pressed, item)
		self.__studies_menu.AppendSeparator()
		# export
		item = self.__studies_menu.Append(-1, _('Selected into export area'))
		self.Bind(wx.EVT_MENU, self._on_copy_selected_studies_to_export_area, item)
		item = self.__studies_menu.Append(-1, _('ZIP of selected into export area'))
		self.Bind(wx.EVT_MENU, self._on_copy_zip_of_selected_studies_to_export_area, item)
		item = self.__studies_menu.Append(-1, _('All into export area'))
		self.Bind(wx.EVT_MENU, self._on_copy_all_studies_to_export_area, item)
		item = self.__studies_menu.Append(-1, _('ZIP of all into export area'))
		self.Bind(wx.EVT_MENU, self._on_copy_zip_of_all_studies_to_export_area, item)
		self.__studies_menu.AppendSeparator()
		# save
		item = self.__studies_menu.Append(-1, _('Save selected'))
		self.Bind(wx.EVT_MENU, self._on_save_selected_studies, item)
		item = self.__studies_menu.Append(-1, _('Save ZIP of selected'))
		self.Bind(wx.EVT_MENU, self._on_save_zip_of_selected_studies, item)
		item = self.__studies_menu.Append(-1, _('Save all'))
		self.Bind(wx.EVT_MENU, self._on_save_all_studies, item)
		item = self.__studies_menu.Append(-1, _('Save ZIP of all'))
		self.Bind(wx.EVT_MENU, self._on_save_zip_of_all_studies, item)
		self.__studies_menu.AppendSeparator()
		# dicomize
		item = self.__studies_menu.Append(-1, _('Add file to study (PDF/image)'))
		self.Bind(wx.EVT_MENU, self._on_add_file_to_study, item)

	#--------------------------------------------------------
	def __set_button_states(self):
		# disable all buttons
		# server
		self._BTN_browse_pacs.Disable()
		self._BTN_upload.Disable()
		self._BTN_modify_orthanc_content.Disable()
		# patient (= all studies of patient)
		self._BTN_browse_patient.Disable()
		self._BTN_verify_patient_data.Disable()
		# study
		self._BTN_browse_study.Disable()
		self._BTN_studies_show.Disable()
		self._BTN_studies_export.Disable()
		# series
		# image
		self._BTN_image_show.Disable()
		self._BTN_image_export.Disable()
		self._BTN_previous_image.Disable()
		self._BTN_next_image.Disable()

		if self.__pacs is None:
			return

		# server buttons
		self._BTN_browse_pacs.Enable()
		self._BTN_upload.Enable()
		self._BTN_modify_orthanc_content.Enable()

		if not self.__patient.connected:
			return

		# patient buttons (= all studies of patient)
		self._BTN_verify_patient_data.Enable()
		if self.__orthanc_patient is not None:
			self._BTN_browse_patient.Enable()

		if len(self._LCTRL_studies.selected_items) == 0:
			return

		# study buttons
		self._BTN_browse_study.Enable()
		study_data = self._LCTRL_studies.get_selected_item_data(only_one = True)
		self._BTN_studies_show.Enable()
		self._BTN_studies_export.Enable()

		if len(self._LCTRL_series.selected_items) == 0:
			return

		series = self._LCTRL_series.get_selected_item_data(only_one = True)
		if len(series['instances']) == 0:
			return

		# image buttons
		self._BTN_image_show.Enable()
		self._BTN_image_export.Enable()
		if len(series['instances']) > 1:
			self._BTN_previous_image.Enable()
			self._BTN_next_image.Enable()

	#--------------------------------------------------------
	def __reset_patient_data(self):
		self._LBL_patient_identification.SetLabel('')
		self._LCTRL_studies.set_string_items(items = [])
		self._LCTRL_series.set_string_items(items = [])
		self.__refresh_image()
		self.__refresh_details()

	#--------------------------------------------------------
	def __reset_server_identification(self):
		self._LBL_PACS_identification.SetLabel(_('<not connected>'))

	#--------------------------------------------------------
	def __reset_ui_content(self):
		self.__reset_server_identification()
		self.__reset_patient_data()
		self.__set_button_states()

	#-----------------------------------------------------
	def __connect(self):

		self.__pacs = None
		self.__orthanc_patient = None
		self.__set_button_states()
		self.__reset_server_identification()

		host = self._TCTRL_host.Value.strip()
		port = self._TCTRL_port.Value.strip()[:6]
		if port == '':
			self._LBL_PACS_identification.SetLabel(_('Cannot connect without port (try 8042).'))
			return False
		if len(port) < 4:
			return False
		try:
			int(port)
		except ValueError:
			self._LBL_PACS_identification.SetLabel(_('Invalid port (try 8042).'))
			return False

		user = self._TCTRL_user.Value
		if user == '':
			user = None
		self._LBL_PACS_identification.SetLabel(_('Connect to [%s] @ port %s as "%s".') % (host, port, user))
		password = self._TCTRL_password.Value
		if password == '':
			password = None

		pacs = gmDICOM.cOrthancServer()
		if not pacs.connect(host = host, port = port, user = user, password = password):		#, expected_aet = 'another AET'
			self._LBL_PACS_identification.SetLabel(_('Cannot connect to PACS.'))
			_log.error('error connecting to server: %s', pacs.connect_error)
			return False

		#self._LBL_PACS_identification.SetLabel(_('PACS: Orthanc "%s" (AET "%s", Version %s, API v%s, DB v%s)') % (
		self._LBL_PACS_identification.SetLabel(_('PACS: Orthanc "%s" (AET "%s", Version %s, DB v%s)') % (
			pacs.server_identification['Name'],
			pacs.server_identification['DicomAet'],
			pacs.server_identification['Version'],
			#pacs.server_identification['ApiVersion'],
			pacs.server_identification['DatabaseVersion']
		))

		self.__pacs = pacs
		self.__set_button_states()
		return True

	#--------------------------------------------------------
	def __refresh_patient_data(self):

		self.__orthanc_patient = None

		if not self.__patient.connected:
			self.__reset_patient_data()
			self.__set_button_states()
			return True

		if not self.__connect():
			return False

		tt_lines = [_('Known PACS IDs:')]
		for pacs_id in self.__patient.suggest_external_ids(target = 'PACS'):
			tt_lines.append(' ' + _('generic: %s') % pacs_id)
		for pacs_id in self.__patient.get_external_ids(id_type = 'PACS', issuer = self.__pacs.as_external_id_issuer):
			tt_lines.append(' ' + _('stored: "%(value)s" @ [%(issuer)s]') % pacs_id)
		tt_lines.append('')
		tt_lines.append(_('Patients found in PACS:'))

		info_lines = []
		# try to find patient
		matching_pats = self.__pacs.get_matching_patients(person = self.__patient)
		if len(matching_pats) == 0:
			info_lines.append(_('PACS: no patients with matching IDs found'))
		no_of_studies = 0
		for pat in matching_pats:
			info_lines.append('"%s" %s "%s (%s) %s"' % (
				pat['MainDicomTags']['PatientID'],
				gmTools.u_arrow2right,
				gmTools.coalesce(pat['MainDicomTags']['PatientName'], '?'),
				gmTools.coalesce(pat['MainDicomTags']['PatientSex'], '?'),
				gmTools.coalesce(pat['MainDicomTags']['PatientBirthDate'], '?')
			))
			no_of_studies += len(pat['Studies'])
			tt_lines.append('%s [#%s]' % (
				gmTools.format_dict_like (
					pat['MainDicomTags'],
					relevant_keys = ['PatientName', 'PatientSex', 'PatientBirthDate', 'PatientID'],
					template = ' %(PatientID)s = %(PatientName)s (%(PatientSex)s) %(PatientBirthDate)s',
					missing_key_template = '?'
				),
				pat['ID']
			))
		if len(matching_pats) > 1:
			info_lines.append(_('PACS: more than one patient with matching IDs found, carefully check studies'))
		self._LBL_patient_identification.SetLabel('\n'.join(info_lines))
		tt_lines.append('')
		tt_lines.append(_('Studies found: %s') % no_of_studies)
		self._LBL_patient_identification.SetToolTip('\n'.join(tt_lines))

		# get studies
		study_list_items = []
		study_list_data = []
		if len(matching_pats) > 0:
			# we don't at this point really expect more than one patient matching
			self.__orthanc_patient = matching_pats[0]
			for pat in self.__pacs.get_studies_list_by_orthanc_patient_list(orthanc_patients = matching_pats):
				for study in pat['studies']:
					docs = []
					if study['referring_doc'] is not None:
						docs.append(study['referring_doc'])
					if study['requesting_doc'] is None:
						if study['requesting_org'] is not None:
							docs.append(study['requesting_org'])
					else:
						if study['requesting_doc'] in docs:
							if study['requesting_org'] is not None:
								docs.append(study['requesting_org'])
						else:
							docs.append (
								'%s%s' % (
									study['requesting_doc'],
									gmTools.coalesce(study['requesting_org'], '', '@%s')
								)
							)
					if study['performing_doc'] is not None:
						if study['performing_doc'] not in docs:
							docs.append(study['performing_doc'])
					if study['operator_name'] is not None:
						if study['operator_name'] not in docs:
							docs.append(study['operator_name'])
					if study['radiographer_code'] is not None:
						if study['radiographer_code'] not in docs:
							docs.append(study['radiographer_code'])
					org_name = u'@'.join ([
						o for o in [study['radiology_dept'], study['radiology_org']]
						if o is not None
					])
					org = '%s%s%s' % (
						org_name,
						gmTools.coalesce(study['station_name'], '', ' [%s]'),
						gmTools.coalesce(study['radiology_org_addr'], '', ' (%s)').replace('\r\n', ' [CR] ')
					)
					if study['date'] is None:
						study_date = '?'
					else:
						study_date = '%s-%s-%s' % (
							study['date'][:4],
							study['date'][4:6],
							study['date'][6:8]
						)
					study_list_items.append ( [
						study_date,
						_('%s series%s') % (
							len(study['series']),
							gmTools.coalesce(study['description'], '', ': %s')
						),
						org.strip(),
						gmTools.u_arrow2right.join(docs)
					] )
					study_list_data.append(study)

		self._LCTRL_studies.set_string_items(items = study_list_items)
		self._LCTRL_studies.set_data(data = study_list_data)
		self._LCTRL_studies.SortListItems(0, 0)
		self._LCTRL_studies.set_column_widths()

		self.__refresh_image()
		self.__refresh_details()
		self.__set_button_states()

		return True

	#--------------------------------------------------------
	def __refresh_details(self):

		self._LCTRL_details.remove_items_safely()
		if self.__pacs is None:
			return

		# study available ?
		study_data = self._LCTRL_studies.get_selected_item_data(only_one = True)
		if study_data is None:
			return
		items = []
		items = [ [key, study_data['all_tags'][key]] for key in study_data['all_tags'] if ('%s' % study_data['all_tags'][key]).strip() != '' ]

		# series available ?
		series = self._LCTRL_series.get_selected_item_data(only_one = True)
		if series is None:
			self._LCTRL_details.set_string_items(items = items)
			self._LCTRL_details.set_column_widths()
			return
		items.append ([
			' %s ' % (gmTools.u_box_horiz_single * 5),
			'%s %s %s' % (
				gmTools.u_box_horiz_single * 3,
				_('Series'),
				gmTools.u_box_horiz_single * 10
			)
		])
		items.extend([ [key, series['all_tags'][key]] for key in series['all_tags'] if ('%s' % series['all_tags'][key]).strip() != '' ])

		# image available ?
		if self.__image_data is None:
			self._LCTRL_details.set_string_items(items = items)
			self._LCTRL_details.set_column_widths()
			return
		items.append ([
			' %s ' % (gmTools.u_box_horiz_single * 5),
			'%s %s %s' % (
				gmTools.u_box_horiz_single * 3,
				_('Image'),
				gmTools.u_box_horiz_single * 10
			)
		])
		tags = self.__pacs.get_instance_dicom_tags(instance_id = self.__image_data['uuid'])
		if tags is False:
			items.extend(['image', '<tags not found in PACS>'])
		else:
			items.extend([ [key, tags[key]] for key in tags if ('%s' % tags[key]).strip() != '' ])

		self._LCTRL_details.set_string_items(items = items)
		self._LCTRL_details.set_column_widths()

	#--------------------------------------------------------
	def __refresh_image(self, idx=None):

		self.__image_data = None
		self._SZR_image_buttons.StaticBox.SetLabel(_('Image'))
		self._BMP_preview.SetBitmap(wx.Bitmap.FromRGBA(50,50, red=0, green=0, blue=0, alpha = wx.ALPHA_TRANSPARENT))

		if idx is None:
			self._BMP_preview.ContainingSizer.Layout()
			return

		if self.__pacs is None:
			self._BMP_preview.ContainingSizer.Layout()
			return

		series = self._LCTRL_series.get_selected_item_data(only_one = True)
		if series is None:
			self._BMP_preview.ContainingSizer.Layout()
			return

		if idx > len(series['instances']) - 1:
			raise ValueError('trying to go beyond instances in series: %s of %s', idx, len(series['instances']))

		# get image
		uuid = series['instances'][idx]
		img_file = self.__pacs.get_instance_preview(instance_id = uuid)
		if img_file is None:
			self._BMP_preview.ContainingSizer.Layout()
			return

		# scale
		wx_bmp = gmGuiHelpers.file2scaled_image(filename = img_file, height = 100)
		# show
		if wx_bmp is None:
			_log.error('cannot load DICOM instance from PACS: %s', uuid)
		else:
			self.__image_data = {'idx': idx, 'uuid': uuid}
			self._BMP_preview.SetBitmap(wx_bmp)
			self._SZR_image_buttons.StaticBox.SetLabel(_('Image %s/%s') % (idx+1, len(series['instances'])))

		if idx == 0:
			self._BTN_previous_image.Disable()
		else:
			self._BTN_previous_image.Enable()
		if idx == len(series['instances']) - 1:
			self._BTN_next_image.Disable()
		else:
			self._BTN_next_image.Enable()

		self._BMP_preview.ContainingSizer.Layout()

	#--------------------------------------------------------
	def __show_image(self, as_dcm=False, as_png=False):
		if self.__image_data is None:
			return False

		uuid = self.__image_data['uuid']
		img_file = None
		if as_dcm:
			img_file = self.__pacs.get_instance(instance_id = uuid)
		if as_png:
			img_file = self.__pacs.get_instance_preview(instance_id = uuid)
		if img_file is not None:
			(success, msg) = gmMimeLib.call_viewer_on_file(img_file)
			if not success:
				gmGuiHelpers.gm_show_warning (
					aMessage = _('Cannot show image:\n%s') % msg,
					aTitle = _('Previewing DICOM image')
				)
			return success

		# try DCM
		img_file = self.__pacs.get_instance(instance_id = uuid)
		(success, msg) = gmMimeLib.call_viewer_on_file(img_file)
		if success:
			return True

		# try PNG
		img_file = self.__pacs.get_instance_preview(instance_id = uuid)
		if img_file is not None:
			(success, msg) = gmMimeLib.call_viewer_on_file(img_file)
			if success:
				return True

		gmGuiHelpers.gm_show_warning (
			aMessage = _('Cannot show in DICOM or image viewer:\n%s') % msg,
			aTitle = _('Previewing DICOM image')
		)

	#--------------------------------------------------------
	def __save_image(self, as_dcm=False, as_png=False, nice_filename=False):
		if self.__image_data is None:
			return False, None

		fnames = {}
		uuid = self.__image_data['uuid']
		if as_dcm:
			if nice_filename:
				fname = gmTools.get_unique_filename (
					prefix = '%s-orthanc_%s--' % (self.__patient.subdir_name, uuid),
					suffix = '.dcm',
					tmp_dir = os.path.join(gmTools.gmPaths().home_dir, 'gnumed')
				)
			else:
				fname = None
			img_fname = self.__pacs.get_instance(filename = fname, instance_id = uuid)
			if img_fname is None:
				gmGuiHelpers.gm_show_warning (
					aMessage = _('Cannot save image as DICOM file.'),
					aTitle = _('Saving DICOM image')
				)
				return False, fnames

			fnames['dcm'] = img_fname
			gmDispatcher.send(signal = 'statustext', msg = _('Successfully saved as [%s].') % img_fname)

		if as_png:
			if nice_filename:
				fname = gmTools.get_unique_filename (
					prefix = '%s-orthanc_%s--' % (self.__patient.subdir_name, uuid),
					suffix = '.png',
					tmp_dir = os.path.join(gmTools.gmPaths().home_dir, 'gnumed')
				)
			else:
				fname = None
			img_fname = self.__pacs.get_instance_preview(filename = fname, instance_id = uuid)
			if img_fname is None:
				gmGuiHelpers.gm_show_warning (
					aMessage = _('Cannot save image as PNG file.'),
					aTitle = _('Saving DICOM image')
				)
				return False, fnames
			fnames['png'] = img_fname
			gmDispatcher.send(signal = 'statustext', msg = _('Successfully saved as [%s].') % img_fname)

		return True, fnames

	#--------------------------------------------------------
	def __copy_image_to_export_area(self):
		if self.__image_data is None:
			return False

		success, fnames = self.__save_image(as_dcm = True, as_png = True)
		if not success:
			return False

		wx.BeginBusyCursor()
		self.__patient.export_area.add_files (
			filenames = [fnames['png'], fnames['dcm']],
			hint = _('DICOM image of [%s] from Orthanc PACS "%s" (AET "%s")') % (
				self.__orthanc_patient['MainDicomTags']['PatientID'],
				self.__pacs.server_identification['Name'],
				self.__pacs.server_identification['DicomAet']
			)
		)
		wx.EndBusyCursor()

		gmDispatcher.send(signal = 'statustext', msg = _('Successfully stored in export area.'))

	#--------------------------------------------------------
	#--------------------------------------------------------
	def __browse_studies(self):
		if self.__pacs is None:
			return

		study_data = self._LCTRL_studies.get_selected_item_data(only_one = True)
		if len(study_data) == 0:
			return

		gmNetworkTools.open_url_in_browser (
			self.__pacs.get_url_browse_study(study_id = study_data['orthanc_id']),
			new = 2,
			autoraise = True
		)

	#--------------------------------------------------------
	def __show_studies(self):
		if self.__pacs is None:
			return

		study_data = self._LCTRL_studies.get_selected_item_data(only_one = False)
		if len(study_data) == 0:
			return

		wx.BeginBusyCursor()
		target_dir = self.__pacs.get_studies_with_dicomdir(study_ids = [ s['orthanc_id'] for s in study_data ])
		wx.EndBusyCursor()
		if target_dir is False:
			gmGuiHelpers.gm_show_error (
				title = _('Showing DICOM studies'),
				error = _('Unable to show selected studies.')
			)
			return
		DICOMDIR = os.path.join(target_dir, 'DICOMDIR')
		if os.path.isfile(DICOMDIR):
			(success, msg) = gmMimeLib.call_viewer_on_file(DICOMDIR, block = False)
			if success:
				return
		else:
			_log.error('cannot find DICOMDIR in: %s', target_dir)

		gmMimeLib.call_viewer_on_file(target_dir, block = False)

		# FIXME: on failure export as JPG and call dir viewer

	#--------------------------------------------------------
	def __copy_all_studies_to_export_area(self):
		if self.__pacs is None:
			return

		study_data = self._LCTRL_studies.get_item_data()
		if len(study_data) == 0:
			return

		self.__copy_studies_to_export_area(study_data)

	#--------------------------------------------------------
	def __copy_selected_studies_to_export_area(self):
		if self.__pacs is None:
			return

		study_data = self._LCTRL_studies.get_selected_item_data(only_one = False)
		if len(study_data) == 0:
			return

		self.__copy_studies_to_export_area(study_data)

	#--------------------------------------------------------
	def __copy_studies_to_export_area(self, study_data):
		wx.BeginBusyCursor()
		target_dir = gmTools.mk_sandbox_dir (
			prefix = 'dcm-',
			base_dir = os.path.join(gmTools.gmPaths().home_dir, '.gnumed', self.__patient.subdir_name)
		)
		target_dir = self.__pacs.get_studies_with_dicomdir(study_ids = [ s['orthanc_id'] for s in study_data ], target_dir = target_dir)
		if target_dir is False:
			wx.EndBusyCursor()
			gmGuiHelpers.gm_show_error (
				title = _('Copying DICOM studies'),
				error = _('Unable to put studies into export area.')
			)
			return

		comment = _('DICOM studies of [%s] from Orthanc PACS "%s" (AET "%s") [%s/]') % (
			self.__orthanc_patient['MainDicomTags']['PatientID'],
			self.__pacs.server_identification['Name'],
			self.__pacs.server_identification['DicomAet'],
			target_dir
		)
		if self.__patient.export_area.add_path(target_dir, comment):
			wx.EndBusyCursor()
			return

		wx.EndBusyCursor()
		gmGuiHelpers.gm_show_error (
			title = _('Adding DICOM studies to export area'),
			error = _('Cannot add the following path to the export area:\n%s ') % target_dir
		)

	#--------------------------------------------------------
	def __copy_zip_of_all_studies_to_export_area(self):
		if self.__pacs is None:
			return

		study_data = self._LCTRL_studies.get_item_data()
		if len(study_data) == 0:
			return

		self.__copy_zip_of_studies_to_export_area(study_data)

	#--------------------------------------------------------
	def __copy_zip_of_selected_studies_to_export_area(self):
		if self.__pacs is None:
			return

		study_data = self._LCTRL_studies.get_selected_item_data(only_one = False)
		if len(study_data) == 0:
			return

		self.__copy_zip_of_studies_to_export_area(study_data)

	#--------------------------------------------------------
	def __copy_zip_of_studies_to_export_area(self, study_data):
		wx.BeginBusyCursor()
		zip_fname = self.__pacs.get_studies_with_dicomdir (
			study_ids = [ s['orthanc_id'] for s in study_data ],
			create_zip = True
		)
		if zip_fname is False:
			wx.EndBusyCursor()
			gmGuiHelpers.gm_show_error (
				title = _('Adding DICOM studies to export area'),
				error = _('Unable to put ZIP of studies into export area.')
			)
			return

		# check size and confirm if huge
		zip_size = os.path.getsize(zip_fname)
		if zip_size > (300 * gmTools._MB):		# ~ 1/2 CD-ROM
			wx.EndBusyCursor()
			really_export = gmGuiHelpers.gm_show_question (
				title = _('Exporting DICOM studies'),
				question = _('The DICOM studies are %s in compressed size.\n\nReally move into export area ?') % gmTools.size2str(zip_size),
				cancel_button = False
			)
			if not really_export:
				return

		hint = _('DICOM studies of [%s] from Orthanc PACS "%s" (AET "%s")') % (
			self.__orthanc_patient['MainDicomTags']['PatientID'],
			self.__pacs.server_identification['Name'],
			self.__pacs.server_identification['DicomAet']
		)
		if self.__patient.export_area.add_file(filename = zip_fname, hint = hint):
			#gmDispatcher.send(signal = 'statustext', msg = _('Successfully saved as [%s].') % filename)
			wx.EndBusyCursor()
			return

		wx.EndBusyCursor()
		gmGuiHelpers.gm_show_error (
			title = _('Adding DICOM studies to export area'),
			error = _('Cannot add the following archive to the export area:\n%s ') % zip_fname
		)

	#--------------------------------------------------------
	def __save_selected_studies(self):
		if self.__pacs is None:
			return

		study_data = self._LCTRL_studies.get_selected_item_data(only_one = False)
		if len(study_data) == 0:
			return

		self.__save_studies_to_disk(study_data)

	#--------------------------------------------------------
	def __on_save_all_studies(self):
		if self.__pacs is None:
			return

		study_data = self._LCTRL_studies.get_item_data()
		if len(study_data) == 0:
			return

		self.__save_studies_to_disk(study_data)

	#--------------------------------------------------------
	def __save_studies_to_disk(self, study_data):
		default_path = os.path.join(gmTools.gmPaths().home_dir, 'gnumed', self.__patient.subdir_name)
		gmTools.mkdir(default_path)
		dlg = wx.DirDialog (
			self,
			message = _('Select the directory into which to save the DICOM studies.'),
			defaultPath = default_path
		)
		choice = dlg.ShowModal()
		target_dir = dlg.GetPath()
		dlg.DestroyLater()
		if choice != wx.ID_OK:
			return True

		wx.BeginBusyCursor()
		target_dir = self.__pacs.get_studies_with_dicomdir(study_ids = [ s['orthanc_id'] for s in study_data ], target_dir = target_dir)
		wx.EndBusyCursor()

		if target_dir is False:
			gmGuiHelpers.gm_show_error (
				title = _('Saving DICOM studies'),
				error = _('Unable to save DICOM studies.')
			)
			return
		gmDispatcher.send(signal = 'statustext', msg = _('Successfully saved to [%s].') % target_dir)

	#--------------------------------------------------------
	def __save_zip_of_selected_studies(self):
		if self.__pacs is None:
			return

		study_data = self._LCTRL_studies.get_selected_item_data(only_one = False)
		if len(study_data) == 0:
			return

		self.__save_zip_of_studies_to_disk(study_data)

	#--------------------------------------------------------
	def ___on_save_zip_of_all_studies(self):
		if self.__pacs is None:
			return

		study_data = self._LCTRL_studies.get_item_data()
		if len(study_data) == 0:
			return

		self.__save_zip_of_studies_to_disk(study_data)

	#--------------------------------------------------------
	def __save_zip_of_studies_to_disk(self, study_data):
		default_path = os.path.join(gmTools.gmPaths().home_dir, 'gnumed', self.__patient.subdir_name)
		gmTools.mkdir(default_path)
		dlg = wx.DirDialog (
			self,
			message = _('Select the directory into which to save the DICOM studies ZIP.'),
			defaultPath = default_path
		)
		choice = dlg.ShowModal()
		target_dir = dlg.GetPath()
		dlg.DestroyLater()
		if choice != wx.ID_OK:
			return True

		wx.BeginBusyCursor()
		filename = self.__pacs.get_studies_with_dicomdir(study_ids = [ s['orthanc_id'] for s in study_data ], target_dir = target_dir, create_zip = True)
		wx.EndBusyCursor()

		if filename is False:
			gmGuiHelpers.gm_show_error (
				title = _('Saving DICOM studies'),
				error = _('Unable to save DICOM studies as ZIP.')
			)
			return

		gmDispatcher.send(signal = 'statustext', msg = _('Successfully saved as [%s].') % filename)

	#--------------------------------------------------------
	def _on_add_pdf_to_study(self, evt):
		if self.__pacs is None:
			return

		study_data = self._LCTRL_studies.get_selected_item_data(only_one = False)
		if len(study_data) != 1:
			gmGuiHelpers.gm_show_info (
				title = _('Adding PDF to DICOM study'),
				info = _('For adding a PDF file there must be exactly one (1) DICOM study selected.')
			)
			return

		# select PDF
		pdf_name = None
		dlg = wx.FileDialog (
			parent = self,
			message = _('Select PDF to add to DICOM study'),
			defaultDir = os.path.join(gmTools.gmPaths().home_dir, 'gnumed'),
			wildcard = "%s (*.pdf)|*.pdf|%s (*)|*" % (_('PDF files'), _('all files')),
			style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
		)
		choice = dlg.ShowModal()
		pdf_name = dlg.GetPath()
		dlg.DestroyLater()
		if choice != wx.ID_OK:
			return

		_log.debug('dicomize(%s)', pdf_name)
		if pdf_name is None:
			return

		# export one instance as template
		instance_uuid = study_data[0]['series'][0]['instances'][-1]
		dcm_instance_template_fname = self.__pacs.get_instance(instance_id = instance_uuid)
		# dicomize PDF via template
		_cfg = gmCfg2.gmCfgData()
		pdf2dcm_fname = gmDICOM.dicomize_pdf (
			pdf_name = pdf_name,
			dcm_template_file = dcm_instance_template_fname,
			title = 'GNUmed',
			verbose = _cfg.get(option = 'debug')
		)
		if pdf2dcm_fname is None:
			gmGuiHelpers.gm_show_error (
				title = _('Adding PDF to DICOM study'),
				error = _('Cannot turn PDF file\n\n %s\n\n into DICOM file.')
			)
			return

		# upload pdf.dcm
		if self.__pacs.upload_dicom_file(pdf2dcm_fname):
			gmDispatcher.send(signal = 'statustext', msg = _('Successfully uploaded [%s] to Orthanc DICOM server.') % pdf2dcm_fname)
			self._schedule_data_reget()
			return

		gmGuiHelpers.gm_show_error (
			title = _('Adding PDF to DICOM study'),
			error = _('Cannot updload DICOM file\n\n %s\n\n into Orthanc PACS.') % pdf2dcm_fname
		)

	#--------------------------------------------------------
	def _on_add_file_to_study(self, evt):
		if self.__pacs is None:
			return

		study_data = self._LCTRL_studies.get_selected_item_data(only_one = False)
		if len(study_data) != 1:
			gmGuiHelpers.gm_show_info (
				title = _('Adding file to DICOM study'),
				info = _('For adding a file there must be exactly one (1) DICOM study selected.')
			)
			return

		# select file
		filename = None
		dlg = wx.FileDialog (
			parent = self,
			message = _('Select file (image or PDF) to add to DICOM study'),
			defaultDir = os.path.join(gmTools.gmPaths().home_dir, 'gnumed'),
			wildcard = "%s (*)|*|%s (*.pdf)|*.pdf" % (_('all files'), _('PDF files')),
			style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
		)
		choice = dlg.ShowModal()
		filename = dlg.GetPath()
		dlg.DestroyLater()
		if choice != wx.ID_OK:
			return

		if filename is None:
			return

		_log.debug('dicomize(%s)', filename)
		# export one instance as template
		instance_uuid = study_data[0]['series'][0]['instances'][-1]
		dcm_instance_template_fname = self.__pacs.get_instance(instance_id = instance_uuid)
		# dicomize file via template
		_cfg = gmCfg2.gmCfgData()
		dcm_fname = gmDICOM.dicomize_file (
			filename = filename,
			dcm_template_file = dcm_instance_template_fname,
			dcm_transfer_series = False,
			title = 'GNUmed',
			verbose = _cfg.get(option = 'debug')
		)
		if dcm_fname is None:
			gmGuiHelpers.gm_show_error (
				title = _('Adding file to DICOM study'),
				error = _('Cannot turn file\n\n %s\n\n into DICOM file.')
			)
			return

		# upload .dcm
		if self.__pacs.upload_dicom_file(dcm_fname):
			gmDispatcher.send(signal = 'statustext', msg = _('Successfully uploaded [%s] to Orthanc DICOM server.') % dcm_fname)
			self._schedule_data_reget()
			return

		gmGuiHelpers.gm_show_error (
			title = _('Adding file to DICOM study'),
			error = _('Cannot updload DICOM file\n\n %s\n\n into Orthanc PACS.') % dcm_fname
		)

	#--------------------------------------------------------
	#--------------------------------------------------------
	def __browse_patient(self):
		if self.__pacs is None:
			return

		gmNetworkTools.open_url_in_browser (
			self.__pacs.get_url_browse_patient(patient_id = self.__orthanc_patient['ID']),
			new = 2,
			autoraise = True
		)

	#--------------------------------------------------------
	#--------------------------------------------------------
	def __browse_pacs(self):
		if self.__pacs is None:
			return

		gmNetworkTools.open_url_in_browser (
			self.__pacs.url_browse_patients,
			new = 2,
			autoraise = True
		)

	#--------------------------------------------------------
	# reget-on-paint mixin API
	#--------------------------------------------------------
	def _populate_with_data(self):
		if not self.__patient.connected:
			self.__reset_ui_content()
			return True

		if not self.__refresh_patient_data():
			return False

		return True

	#--------------------------------------------------------
	# event handling
	#--------------------------------------------------------
	def __register_interests(self):

		# wxPython signals
		self._BMP_preview.Bind(wx.EVT_LEFT_DCLICK, self._on_preview_image_leftdoubleclicked)
		self._BMP_preview.Bind(wx.EVT_RIGHT_UP, self._on_preview_image_rightclicked)
		self._BTN_browse_study.Bind(wx.EVT_RIGHT_UP, self._on_studies_button_rightclicked)

		# client internal signals
		gmDispatcher.connect(signal = 'pre_patient_unselection', receiver = self._on_pre_patient_unselection)
		gmDispatcher.connect(signal = 'post_patient_selection', receiver = self._on_post_patient_selection)

		# generic database change signal
		gmDispatcher.connect(signal = 'gm_table_mod', receiver = self._on_database_signal)

	#--------------------------------------------------------
	def _on_pre_patient_unselection(self):
		# only empty out here, do NOT access the patient
		# or else we will access the old patient while it
		# may not be valid anymore ...
		self.__reset_patient_data()

	#--------------------------------------------------------
	def _on_post_patient_selection(self):
		self._schedule_data_reget()

	#--------------------------------------------------------
	def _on_database_signal(self, **kwds):

		if not self.__patient.connected:
			# probably not needed:
			#self._schedule_data_reget()
			return True

		if kwds['pk_identity'] != self.__patient.ID:
			return True

		if kwds['table'] == 'dem.lnk_identity2ext_id':
			self._schedule_data_reget()
			return True

		return True

	#--------------------------------------------------------
	# events: lists
	#--------------------------------------------------------
	def _on_series_list_item_selected(self, event):

		event.Skip()
		if self.__pacs is None:
			return

		study_data = self._LCTRL_studies.get_selected_item_data(only_one = True)
		if study_data is None:
			return

		series = self._LCTRL_series.get_selected_item_data(only_one = True)
		if series is None:
			self.__set_button_states()
			return

		if len(series['instances']) == 0:
			self.__refresh_image()
			self.__refresh_details()
			self.__set_button_states()
			return

		# set first image
		self.__refresh_image(0)
		self.__refresh_details()
		self.__set_button_states()
		self._BTN_previous_image.Disable()

	#--------------------------------------------------------
	def _on_series_list_item_deselected(self, event):
		event.Skip()

		self.__refresh_image()
		self.__refresh_details()
		self.__set_button_states()

	#--------------------------------------------------------
	def _on_studies_list_item_selected(self, event):
		event.Skip()
		if self.__pacs is None:
			return

		study_data = self._LCTRL_studies.get_item_data(item_idx = event.Index)
		series_list_items = []
		series_list_data = []
		for series in study_data['series']:

			series_time = ''
			if series['time'] is None:
				series['time'] = study_data['time']
			if series['time'] is None:
				series_time = '?'
			else:
				series_time = '%s:%s:%s' % (
					series['time'][:2],
					series['time'][2:4],
					series['time'][4:6]
				)

			series_desc_parts = []
			if series['description'] is not None:
				if series['protocol'] is None:
					series_desc_parts.append(series['description'].strip())
				else:
					if series['description'].strip() not in series['protocol'].strip():
						series_desc_parts.append(series['description'].strip())
			if series['protocol'] is not None:
				series_desc_parts.append('[%s]' % series['protocol'].strip())
			if series['performed_procedure_step_description'] is not None:
				series_desc_parts.append(series['performed_procedure_step_description'].strip())
			if series['acquisition_device_processing_description'] is not None:
				series_desc_parts.append(series['acquisition_device_processing_description'].strip())
			series_desc = ' / '.join(series_desc_parts)
			if len(series_desc) > 0:
				series_desc = ': ' + series_desc
			series_desc = _('%s image(s)%s') % (len(series['instances']), series_desc)

			series_list_items.append ([
				series_time,
				gmTools.coalesce(series['modality'], ''),
				gmTools.coalesce(series['body_part'], ''),
				series_desc
			])
			series_list_data.append(series)

		self._LCTRL_series.set_string_items(items = series_list_items)
		self._LCTRL_series.set_data(data = series_list_data)
		self._LCTRL_series.SortListItems(0)

		self.__refresh_image()
		self.__refresh_details()
		self.__set_button_states()

	#--------------------------------------------------------
	def _on_studies_list_item_deselected(self, event):
		event.Skip()

		self._LCTRL_series.remove_items_safely()
		self.__refresh_image()
		self.__refresh_details()
		self.__set_button_states()

	#--------------------------------------------------------
	# events: buttons
	#--------------------------------------------------------
	def _on_connect_button_pressed(self, event):
		event.Skip()

		if not self.__connect():
			self.__reset_patient_data()
			self.__set_button_states()
			return False

		if not self.__refresh_patient_data():
			self.__set_button_states()
			return False

		self.__set_button_states()
		return True

	#--------------------------------------------------------
	def _on_upload_button_pressed(self, event):
		event.Skip()
		if self.__pacs is None:
			return

		dlg = wx.DirDialog (
			self,
			message = _('Select the directory from which to recursively upload DICOM files.'),
			defaultPath = os.path.join(gmTools.gmPaths().home_dir, 'gnumed')
		)
		choice = dlg.ShowModal()
		dicom_dir = dlg.GetPath()
		dlg.DestroyLater()
		if choice != wx.ID_OK:
			return True
		wx.BeginBusyCursor()
		try:
			uploaded, not_uploaded = self.__pacs.upload_from_directory (
				directory = dicom_dir,
				recursive = True,
				check_mime_type = False,
				ignore_other_files = True
			)
		finally:
			wx.EndBusyCursor()
		if len(not_uploaded) == 0:
			q = _('Delete the uploaded DICOM files now ?')
		else:
			q = _('Some files have not been uploaded.\n\nDo you want to delete those DICOM files which have been sent to the PACS successfully ?')
			_log.error('not uploaded:')
			for f in not_uploaded:
				_log.error(f)

		delete_uploaded = gmGuiHelpers.gm_show_question (
			title = _('Uploading DICOM files'),
			question = q,
			cancel_button = False
		)
		if not delete_uploaded:
			return
		wx.BeginBusyCursor()
		for f in uploaded:
			gmTools.remove_file(f)
		wx.EndBusyCursor()

	#--------------------------------------------------------
	def _on_modify_orthanc_content_button_pressed(self, event):
		event.Skip()
		if self.__pacs is None:
			return

		title = _('Working on: Orthanc "%s" (AET "%s" @ %s:%s, Version %s)') % (
			self.__pacs.server_identification['Name'],
			self.__pacs.server_identification['DicomAet'],
			self._TCTRL_host.Value.strip(),
			self._TCTRL_port.Value.strip(),
			self.__pacs.server_identification['Version']
		)
		dlg = cModifyOrthancContentDlg(self, -1, server = self.__pacs, title = title)
		dlg.ShowModal()
		dlg.DestroyLater()
		self._schedule_data_reget()

	#--------------------------------------------------------
	# - image menu and image buttons
	#--------------------------------------------------------
	def _on_show_image_as_dcm(self, event):
		self.__show_image(as_dcm = True)

	#--------------------------------------------------------
	def _on_show_image_as_png(self, event):
		self.__show_image(as_png = True)

	#--------------------------------------------------------
	def _on_copy_image_to_export_area(self, event):
		self.__copy_image_to_export_area()

	#--------------------------------------------------------
	def _on_save_image_as_png(self, event):
		self.__save_image(as_png = True, nice_filename = True)

	#--------------------------------------------------------
	def _on_save_image_as_dcm(self, event):
		self.__save_image(as_dcm = True, nice_filename = True)

	#--------------------------------------------------------
	#--------------------------------------------------------
	def _on_preview_image_leftdoubleclicked(self, event):
		self.__show_image()

	#--------------------------------------------------------
	def _on_preview_image_rightclicked(self, event):
		if self.__image_data is None:
			return False

		self.PopupMenu(self.__thumbnail_menu)

	#--------------------------------------------------------
	def _on_next_image_button_pressed(self, event):
		if self.__image_data is None:
			return

		self.__refresh_image(idx = self.__image_data['idx'] + 1)
		self.__refresh_details()

	#--------------------------------------------------------
	def _on_previous_image_button_pressed(self, event):
		if self.__image_data is None:
			return
		self.__refresh_image(idx = self.__image_data['idx'] - 1)
		self.__refresh_details()

	#--------------------------------------------------------
	def _on_button_image_show_pressed(self, event):
		self.__show_image()

	#--------------------------------------------------------
	def _on_button_image_export_pressed(self, event):
		self.__copy_image_to_export_area()

	#--------------------------------------------------------
	# - study menu and buttons
	#--------------------------------------------------------
	def _on_browse_study_button_pressed(self, event):
		self.__browse_studies()

	#--------------------------------------------------------
	def _on_studies_show_button_pressed(self, event):
		self.__show_studies()

	#--------------------------------------------------------
	def _on_studies_export_button_pressed(self, event):
		self.__copy_selected_studies_to_export_area()

	#--------------------------------------------------------
	def _on_studies_button_rightclicked(self, event):
		self.PopupMenu(self.__studies_menu)

	#--------------------------------------------------------
	def _on_copy_selected_studies_to_export_area(self, event):
		self.__copy_selected_studies_to_export_area()

	#--------------------------------------------------------
	def _on_copy_all_studies_to_export_area(self, event):
		self.__copy_all_studies_to_export_area()

	#--------------------------------------------------------
	def _on_copy_zip_of_selected_studies_to_export_area(self, event):
		self.__copy_zip_of_selected_studies_to_export_area()

	#--------------------------------------------------------
	def _on_copy_zip_of_all_studies_to_export_area(self, event):
		self.__copy_zip_of_all_studies_to_export_area()

	#--------------------------------------------------------
	def _on_save_selected_studies(self, event):
		self.__save_selected_studies()

	#--------------------------------------------------------
	def _on_save_zip_of_selected_studies(self, event):
		self.__save_zip_of_selected_studies()

	#--------------------------------------------------------
	def _on_save_all_studies(self, event):
		self.__save_all_studies()

	#--------------------------------------------------------
	def _on_save_zip_of_all_studies(self, event):
		self.__save_zip_of_all_studies()

	#--------------------------------------------------------
	# - patient buttons (= all studies)
	#--------------------------------------------------------
	def _on_browse_patient_button_pressed(self, event):
		self.__browse_patient()

	#--------------------------------------------------------
	def _on_verify_patient_data_button_pressed(self, event):
		if self.__pacs is None:
			return None

		if self.__orthanc_patient is None:
			return None

		patient_id = self.__orthanc_patient['ID']
		wx.BeginBusyCursor()
		try:
			bad_data = self.__pacs.verify_patient_data(patient_id)
		finally:
			wx.EndBusyCursor()
		if len(bad_data) == 0:
			gmDispatcher.send(signal = 'statustext', msg = _('Successfully verified DICOM data of patient.'))
			return

		gmGuiHelpers.gm_show_error (
			title = _('DICOM data error'),
			error = _(
				'There seems to be a data error in the DICOM files\n'
				'stored in the Orthanc server.\n'
				'\n'
				'Please check the inbox.'
			)
		)

		msg = _('Checksum error in DICOM data of this patient.\n\n')
		msg += _('DICOM server: %s\n\n') % bad_data[0]['orthanc']
		for bd in bad_data:
			msg += _('Orthanc patient ID [%s]\n %s: [%s]\n') % (
				bd['patient'],
				bd['type'],
				bd['instance']
			)
		prov = self.__patient.primary_provider
		if prov is None:
			prov = gmStaff.gmCurrentProvider()
		report = gmProviderInbox.create_inbox_message (
			message_type = _('error report'),
			message_category = 'clinical',
			patient = self.__patient.ID,
			staff = prov['pk_staff'],
			subject = _('DICOM data corruption')
		)
		report['data'] = msg
		report.save()

	#--------------------------------------------------------
	def _on_browse_pacs_button_pressed(self, event):
		self.__browse_pacs()

#------------------------------------------------------------
from Gnumed.wxGladeWidgets.wxgModifyOrthancContentDlg import wxgModifyOrthancContentDlg

class cModifyOrthancContentDlg(wxgModifyOrthancContentDlg):
	def __init__(self, *args, **kwds):
		self.__srv = kwds['server']
		del kwds['server']
		title = kwds['title']
		del kwds['title']
		wxgModifyOrthancContentDlg.__init__(self, *args, **kwds)
		self.SetTitle(title)
		self._LCTRL_patients.set_columns( [_('Patient ID'), _('Name'), _('Birth date'), _('Gender'), _('Orthanc')] )

	#--------------------------------------------------------
	def __refresh_patient_list(self):
		self._LCTRL_patients.set_string_items()
		search_term = self._TCTRL_search_term.Value.strip()
		if search_term == '':
			return
		pats = self.__srv.get_patients_by_name(name_parts = search_term.split(), fuzzy = True)
		if len(pats) == 0:
			return
		list_items = []
		list_data = []
		for pat in pats:
			mt = pat['MainDicomTags']
			try:
				gender = mt['PatientSex']
			except KeyError:
				gender = ''
			try:
				dob = mt['PatientBirthDate']
			except KeyError:
				dob = ''
			list_items.append([mt['PatientID'], mt['PatientName'], dob, gender, pat['ID']])
			list_data.append(mt['PatientID'])
		self._LCTRL_patients.set_string_items(list_items)
		self._LCTRL_patients.set_column_widths()
		self._LCTRL_patients.set_data(list_data)

	#--------------------------------------------------------
	def _on_search_patients_button_pressed(self, event):
		event.Skip()
		self.__refresh_patient_list()

	#--------------------------------------------------------
	def _on_suggest_patient_id_button_pressed(self, event):
		event.Skip()
		pat = gmPerson.gmCurrentPatient()
		if not pat.connected:
			return
		self._TCTRL_new_patient_id.Value = pat.suggest_external_id(target = 'PACS')

	#--------------------------------------------------------
	def _on_set_patient_id_button_pressed(self, event):
		event.Skip()
		new_id = self._TCTRL_new_patient_id.Value.strip()
		if new_id == '':
			return
		pats = self._LCTRL_patients.get_selected_item_data(only_one = False)
		if len(pats) == 0:
			return
		really_modify = gmGuiHelpers.gm_show_question (
			title = _('Modifying patient ID'),
			question = _(
				'Really modify %s patient(s) to have the new patient ID\n\n'
				' [%s]\n\n'
				'stored in the Orthanc DICOM server ?'
			) % (
				len(pats),
				new_id
			),
			cancel_button = True
		)
		if not really_modify:
			return
		all_modified = True
		for pat in pats:
			success = self.__srv.modify_patient_id(old_patient_id = pat, new_patient_id = new_id)
			if not success:
				all_modified = False
		self.__refresh_patient_list()

		if not all_modified:
			gmGuiHelpers.gm_show_warning (
				aTitle = _('Modifying patient ID'),
				aMessage = _(
					'I was unable to modify all DICOM patients.\n'
					'\n'
					'Please refer to the log file.'
				)
			)
		return all_modified

#------------------------------------------------------------
# outdated:
def upload_files():
	event.Skip()
	dlg = wx.DirDialog (
		self,
		message = _('Select the directory from which to recursively upload DICOM files.'),
		defaultPath = os.path.join(gmTools.gmPaths().home_dir, 'gnumed')
	)
	choice = dlg.ShowModal()
	dicom_dir = dlg.GetPath()
	dlg.DestroyLater()
	if choice != wx.ID_OK:
		return True
	wx.BeginBusyCursor()
	try:
		uploaded, not_uploaded = self.__pacs.upload_from_directory (
			directory = dicom_dir,
			recursive = True,
			check_mime_type = False,
			ignore_other_files = True
		)
	finally:
		wx.EndBusyCursor()
	if len(not_uploaded) == 0:
		q = _('Delete the uploaded DICOM files now ?')
	else:
		q = _('Some files have not been uploaded.\n\nDo you want to delete those DICOM files which have been sent to the PACS successfully ?')
		_log.error('not uploaded:')
		for f in not_uploaded:
			_log.error(f)
		delete_uploaded = gmGuiHelpers.gm_show_question (
		title = _('Uploading DICOM files'),
		question = q,
		cancel_button = False
	)
	if not delete_uploaded:
		return
	wx.BeginBusyCursor()
	for f in uploaded:
		gmTools.remove_file(f)
	wx.EndBusyCursor()

#============================================================
# main
#------------------------------------------------------------
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	from Gnumed.business import gmPersonSearch
	from Gnumed.wxpython import gmPatSearchWidgets

	#----------------------------------------------------------------
	def test_document_prw():
		app = wx.PyWidgetTester(size = (180, 20))
		#pnl = cEncounterEditAreaPnl(app.frame, -1, encounter=enc)
		prw = cDocumentPhraseWheel(app.frame, -1)
		prw.set_context('pat', 12)
		app.frame.Show(True)
		app.MainLoop()

	#----------------------------------------------------------------
	test_document_prw()
