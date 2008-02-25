"""GNUmed medical document handling widgets.
"""
#================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmMedDocWidgets.py,v $
# $Id: gmMedDocWidgets.py,v 1.155 2008-02-25 17:38:05 ncq Exp $
__version__ = "$Revision: 1.155 $"
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"

import os.path, sys, re as regex


import wx


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmLog, gmI18N, gmCfg, gmPG2, gmMimeLib, gmExceptions, gmMatchProvider, gmDispatcher, gmDateTime, gmTools
from Gnumed.business import gmPerson, gmMedDoc, gmEMRStructItems, gmSurgery
from Gnumed.wxpython import gmGuiHelpers, gmRegetMixin, gmPhraseWheel, gmPlugin, gmEMRStructWidgets, gmListWidgets
from Gnumed.wxGladeWidgets import wxgScanIdxPnl, wxgReviewDocPartDlg, wxgSelectablySortedDocTreePnl, wxgEditDocumentTypesPnl, wxgEditDocumentTypesDlg


_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)

#============================================================
def _save_file_as_new_document(**kwargs):
	wx.CallAfter(save_file_as_new_document, **kwargs)
#----------------------
def save_file_as_new_document(parent=None, filename=None, document_type=None, unlock_patient=False, **kwargs):

	pat = gmPerson.gmCurrentPatient()
	if not pat.is_connected():
		return

	emr = pat.get_emr()

	all_epis = emr.get_episodes()
	# FIXME: what to do here ? probably create dummy episode
	if len(all_epis) == 0:
		epi = emr.add_episode(episode_name = _('Documents'), is_open = False)
	else:
		# FIXME: parent=None map to toplevel window
		dlg = gmEMRStructWidgets.cEpisodeListSelectorDlg(parent = parent, id = -1, episodes = all_epis)
		dlg.SetTitle(_('Select the episode under which to file the document ...'))
		btn_pressed = dlg.ShowModal()
		epi = dlg.get_selected_item_data(only_one = True)
		dlg.Destroy()

		if btn_pressed == wx.ID_CANCEL:
			if unlock_patient:
				pat.locked = False
			return

	doc_type = gmMedDoc.create_document_type(document_type = document_type)

	docs_folder = pat.get_document_folder()
	doc = docs_folder.add_document (
		document_type = doc_type['pk_doc_type'],
		encounter = emr.get_active_encounter()['pk_encounter'],
		episode = epi['pk_episode']
	)
	part = doc.add_part(file = filename)
	part['filename'] = filename
	part.save_payload()

	if unlock_patient:
		pat.locked = False

	gmDispatcher.send(signal = 'statustext', msg = _('Imported new document from [%s].' % filename), beep = True)

	return
#----------------------
gmDispatcher.connect(signal = u'import_document_from_file', receiver = _save_file_as_new_document)
#============================================================
class cDocumentCommentPhraseWheel(gmPhraseWheel.cPhraseWheel):
	"""Let user select a document comment from all existing comments."""
	def __init__(self, *args, **kwargs):

		gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)

		context = {
			u'ctxt_doc_type': {
				u'where_part': u'and fk_type = %(pk_doc_type)s',
				u'placeholder': u'pk_doc_type'
			}
		}

		mp = gmMatchProvider.cMatchProvider_SQL2 (
			queries = [u"""
select *
from (
	select distinct on (comment) *
	from (
		-- keyed by doc type
		select comment, comment as pk, 1 as rank
		from blobs.doc_med
		where
			comment %(fragment_condition)s
			%(ctxt_doc_type)s

		union all

		select comment, comment as pk, 2 as rank
		from blobs.doc_med
		where comment %(fragment_condition)s
	) as q_union
) as q_distinct
order by rank, comment
limit 25"""],
			context = context
		)
		mp.setThresholds(3, 5, 7)
		mp.unset_context(u'pk_doc_type')

		self.matcher = mp
		self.picklist_delay = 50
#============================================================
class cEditDocumentTypesDlg(wxgEditDocumentTypesDlg.wxgEditDocumentTypesDlg):
	"""A dialog showing a cEditDocumentTypesPnl."""

	def __init__(self, *args, **kwargs):
		wxgEditDocumentTypesDlg.wxgEditDocumentTypesDlg.__init__(self, *args, **kwargs)

#============================================================
class cEditDocumentTypesPnl(wxgEditDocumentTypesPnl.wxgEditDocumentTypesPnl):
	"""A panel grouping together fields to edit the list of document types."""

	def __init__(self, *args, **kwargs):
		wxgEditDocumentTypesPnl.wxgEditDocumentTypesPnl.__init__(self, *args, **kwargs)
		self.__init_ui()
		self.repopulate_ui()
	#--------------------------------------------------------
	def __init_ui(self):
		# add column headers
		self._LCTRL_doc_type.InsertColumn(0, _('type'))
		self._LCTRL_doc_type.InsertColumn(1, _('description'))
		self._LCTRL_doc_type.InsertColumn(2, _('user defined'))
		self._LCTRL_doc_type.InsertColumn(3, _('in use'))
	#--------------------------------------------------------
	def repopulate_ui(self):

		doc_types = gmMedDoc.get_document_types()
		pos = len(doc_types) + 1
		self._LCTRL_doc_type.DeleteAllItems()

		for doc_type in doc_types:
			row_num = self._LCTRL_doc_type.InsertStringItem(pos, label = doc_type['type'])
			self._LCTRL_doc_type.SetStringItem(index = row_num, col = 1, label = doc_type['l10n_type'])
			if doc_type['is_user_defined']:
				self._LCTRL_doc_type.SetStringItem(index = row_num, col = 2, label = ' X ')
			if doc_type['is_in_use']:
				self._LCTRL_doc_type.SetStringItem(index = row_num, col = 3, label = ' X ')

		if len(doc_types) > 0:
			self._LCTRL_doc_type.set_data(data = doc_types)
			self._LCTRL_doc_type.SetColumnWidth(col=0, width=wx.LIST_AUTOSIZE)
			self._LCTRL_doc_type.SetColumnWidth(col=1, width=wx.LIST_AUTOSIZE)
			self._LCTRL_doc_type.SetColumnWidth(col=2, width=wx.LIST_AUTOSIZE_USEHEADER)
			self._LCTRL_doc_type.SetColumnWidth(col=3, width=wx.LIST_AUTOSIZE_USEHEADER)

		self._BTN_set_translation.Enable(False)
		self._BTN_delete.Enable(False)

		self._TCTRL_type.SetValue('')
		self._TCTRL_l10n_type.SetValue('')

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
		return
	#--------------------------------------------------------
	def _on_set_translation_button_pressed(self, event):
		doc_type = self._LCTRL_doc_type.get_selected_item_data()
		doc_type.set_translation(translation = self._TCTRL_l10n_type.GetValue().strip())

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

		gmMedDoc.delete_document_type(document_type = doc_type)

		self.repopulate_ui()
		return
	#--------------------------------------------------------
	def _on_add_button_pressed(self, event):
		desc = self._TCTRL_type.GetValue().strip()
		if desc != '':
			doc_type = gmMedDoc.create_document_type(document_type = desc)		# does not create dupes
			l10n_desc = self._TCTRL_l10n_type.GetValue().strip()
			if (l10n_desc != '') and (l10n_desc != doc_type['l10n_type']):
				doc_type.set_translation(translation = l10n_desc)
			self.repopulate_ui()

		return
	#--------------------------------------------------------
	def _on_type_modified(self, event):
		self._BTN_set_translation.Enable(False)
		self._BTN_delete.Enable(False)
		self._BTN_add.Enable(True)
#		self._LCTRL_doc_type.deselect_selected_item()
		return
#============================================================
class cDocumentTypeSelectionPhraseWheel(gmPhraseWheel.cPhraseWheel):
	"""Let user select a document type."""
	def __init__(self, *args, **kwargs):

		gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)

		mp = gmMatchProvider.cMatchProvider_SQL2 (
			queries = [
u"""select * from ((
	select pk_doc_type, l10n_type, 1 as rank from blobs.v_doc_type where
		is_user_defined is True and
		l10n_type %(fragment_condition)s
) union (
	select pk_doc_type, l10n_type, 2 from blobs.v_doc_type where
		is_user_defined is False and
		l10n_type %(fragment_condition)s
)) as q1 order by q1.rank, q1.l10n_type
"""]
			)
		mp.setThresholds(2, 4, 6)

		self.matcher = mp
		self.picklist_delay = 50
	#--------------------------------------------------------
	def GetData(self, can_create=False):
		if self.data is None:
			if can_create:
				self.data = gmMedDoc.create_document_type(self.GetValue().strip())['pk_doc_type']	# FIXME: error handling
		return self.data
#============================================================
class cReviewDocPartDlg(wxgReviewDocPartDlg.wxgReviewDocPartDlg):
	def __init__(self, *args, **kwds):
		"""Support parts and docs now.
		"""
		part = kwds['part']
		del kwds['part']
		wxgReviewDocPartDlg.wxgReviewDocPartDlg.__init__(self, *args, **kwds)

		if isinstance(part, gmMedDoc.cMedDocPart):
			self.__part = part
			self.__doc = self.__part.get_containing_document()
			self.__reviewing_doc = False
		elif isinstance(part, gmMedDoc.cMedDoc):
			self.__doc = part
			self.__part = self.__doc.get_parts()[0]
			self.__reviewing_doc = True
		else:
			raise ValueError('<part> must be gmMedDoc.cMedDoc or gmMedDoc.cMedDocPart instance, got <%s>' % type(part))

		self.__init_ui_data()
	#--------------------------------------------------------
	# internal API
	#--------------------------------------------------------
	def __init_ui_data(self):
		# FIXME: fix this
		# associated episode (add " " to avoid popping up pick list)
		self._PhWheel_episode.SetText('%s ' % self.__part['episode'], self.__part['pk_episode'])
		self._PhWheel_doc_type.SetText(value = self.__part['l10n_type'], data = self.__part['pk_type'])
		self._PhWheel_doc_type.add_callback_on_lose_focus(self._on_doc_type_loses_focus)

		self._PRW_doc_comment.SetText(gmTools.coalesce(self.__part['doc_comment'], ''))
		self._PRW_doc_comment.set_context(context = 'pk_doc_type', val = self.__part['pk_type'])

		fts = gmDateTime.cFuzzyTimestamp(timestamp = self.__part['date_generated'])
		self._PhWheel_doc_date.SetText(fts.strftime('%Y-%m-%d'), fts)
		self._TCTRL_reference.SetValue(gmTools.coalesce(self.__part['ext_ref'], ''))
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
			self._LCTRL_existing_reviews.SetColumnWidth(col=0, width=wx.LIST_AUTOSIZE)
			self._LCTRL_existing_reviews.SetColumnWidth(col=1, width=wx.LIST_AUTOSIZE)
			self._LCTRL_existing_reviews.SetColumnWidth(col=2, width=wx.LIST_AUTOSIZE_USEHEADER)
			self._LCTRL_existing_reviews.SetColumnWidth(col=3, width=wx.LIST_AUTOSIZE_USEHEADER)
			self._LCTRL_existing_reviews.SetColumnWidth(col=4, width=wx.LIST_AUTOSIZE)

		me = gmPerson.gmCurrentProvider()
		if self.__part['pk_intended_reviewer'] == me['pk_staff']:
			msg = _('(you are the primary reviewer)')
		else:
			msg = _('(someone else is the primary reviewer)')
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
			row_num = self._LCTRL_existing_reviews.InsertStringItem(sys.maxint, label=review_by_responsible_doc[0])
			self._LCTRL_existing_reviews.SetItemTextColour(row_num, col=wx.BLUE)
			self._LCTRL_existing_reviews.SetStringItem(index = row_num, col=0, label=review_by_responsible_doc[0])
			self._LCTRL_existing_reviews.SetStringItem(index = row_num, col=1, label=review_by_responsible_doc[1].strftime('%Y-%m-%d %H:%M'))
			if review_by_responsible_doc['is_technically_abnormal']:
				self._LCTRL_existing_reviews.SetStringItem(index = row_num, col=2, label=u'X')
			if review_by_responsible_doc['clinically_relevant']:
				self._LCTRL_existing_reviews.SetStringItem(index = row_num, col=3, label=u'X')
			self._LCTRL_existing_reviews.SetStringItem(index = row_num, col=4, label=review_by_responsible_doc[6])
			row_num += 1
		for rev in reviews_by_others:
			row_num = self._LCTRL_existing_reviews.InsertStringItem(sys.maxint, label=rev[0])
			self._LCTRL_existing_reviews.SetStringItem(index = row_num, col=0, label=rev[0])
			self._LCTRL_existing_reviews.SetStringItem(index = row_num, col=1, label=rev[1].strftime('%Y-%m-%d %H:%M'))
			if rev['is_technically_abnormal']:
				self._LCTRL_existing_reviews.SetStringItem(index = row_num, col=2, label=u'X')
			if rev['clinically_relevant']:
				self._LCTRL_existing_reviews.SetStringItem(index = row_num, col=3, label=u'X')
			self._LCTRL_existing_reviews.SetStringItem(index = row_num, col=4, label=rev[6])
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
				_('editing document properties')
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
		self.__doc['comment'] = self._PRW_doc_comment.GetValue().strip()
		self.__doc['date'] = self._PhWheel_doc_date.GetData().get_pydt()
		self.__doc['ext_ref'] = self._TCTRL_reference.GetValue().strip()

		success, data = self.__doc.save_payload()
		if not success:
			gmGuiHelpers.gm_show_error (
				_('Cannot link the document to episode\n\n [%s]') % epi_name,
				_('editing document properties')
			)
			return False

		# 2) handle review
		if self._ChBOX_review.GetValue():
			provider = gmPerson.gmCurrentProvider()
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
				gmGuiHelpers.gm_show_error(msg, _('editing document properties'))
				return False

		# 3) handle page specific parts
		if not self.__reviewing_doc:
			self.__part['filename'] = gmTools.none_if(self._TCTRL_filename.GetValue().strip(), u'')
			self.__part['seq_idx'] = gmTools.none_if(self._SPINCTRL_seq_idx.GetValue(), 0)
			success, data = self.__part.save_payload()
			if not success:
				gmGuiHelpers.gm_show_error (
					_('Error saving part properties.'),
					_('editing document properties')
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
	def _on_doc_type_loses_focus(self):
		pk_doc_type = self._PhWheel_doc_type.GetData()
		if pk_doc_type is None:
			self._PRW_doc_comment.unset_context(context = 'pk_doc_type')
		else:
			self._PRW_doc_comment.set_context(context = 'pk_doc_type', val = pk_doc_type)
		return True
#============================================================
class cScanIdxDocsPnl(wxgScanIdxPnl.wxgScanIdxPnl, gmPlugin.cPatientChange_PluginMixin):
	def __init__(self, *args, **kwds):
		wxgScanIdxPnl.wxgScanIdxPnl.__init__(self, *args, **kwds)
		gmPlugin.cPatientChange_PluginMixin.__init__(self)

		self._PhWheel_reviewer.matcher = gmPerson.cMatchProvider_Provider()

		self.__init_ui_data()
		self._PhWheel_doc_type.add_callback_on_lose_focus(self._on_doc_type_loses_focus)

		# make me and listctrl a file drop target
		dt = gmGuiHelpers.cFileDropTarget(self)
		self.SetDropTarget(dt)
		dt = gmGuiHelpers.cFileDropTarget(self._LBOX_doc_pages)
		self._LBOX_doc_pages.SetDropTarget(dt)
		self._LBOX_doc_pages.add_filenames = self.add_filenames_to_listbox

		# do not import globally since we might want to use
		# this module without requiring any scanner to be available
		from Gnumed.pycommon import gmScanBackend
		self.scan_module = gmScanBackend
	#--------------------------------------------------------
	# file drop target API
	#--------------------------------------------------------
	def add_filenames_to_listbox(self, filenames):
		self.add_filenames(filenames=filenames)
	#--------------------------------------------------------
	def add_filenames(self, filenames):
		pat = gmPerson.gmCurrentPatient()
		if not pat.is_connected():
			gmDispatcher.send(signal='statustext', msg=_('Cannot accept new documents. No active patient.'))
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

		self.acquired_pages.extend(real_filenames)
		self.__reload_LBOX_doc_pages()
	#--------------------------------------------------------
	def repopulate_ui(self):
		pass
	#--------------------------------------------------------
	# patient change plugin API
	#--------------------------------------------------------
	def _pre_patient_selection(self, **kwds):
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
		self._PhWheel_episode.SetText('')
		self._PhWheel_doc_type.SetText('')
		# -----------------------------
		# FIXME: make this configurable: either now() or last_date()
		fts = gmDateTime.cFuzzyTimestamp()
		self._PhWheel_doc_date.SetText(fts.strftime('%Y-%m-%d'), fts)
		self._PRW_doc_comment.SetText('')
		# FIXME: should be set to patient's primary doc
		self._PhWheel_reviewer.selection_only = True
		me = gmPerson.gmCurrentProvider()
		self._PhWheel_reviewer.SetText (
			value = u'%s (%s%s %s)' % (me['short_alias'], me['title'], me['firstnames'], me['lastnames']),
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
		self._LBOX_doc_pages.Clear()
		self.acquired_pages = []
	#--------------------------------------------------------
	def __reload_LBOX_doc_pages(self):
		self._LBOX_doc_pages.Clear()
		if len(self.acquired_pages) > 0:
			for i in range(len(self.acquired_pages)):
				fname = self.acquired_pages[i]
				self._LBOX_doc_pages.Append(_('part %s: %s' % (i+1, fname)), fname)
	#--------------------------------------------------------
	def __valid_for_save(self):
		title = _('saving document')

		if self.acquired_pages is None or len(self.acquired_pages) == 0:
			dbcfg = gmCfg.cCfgSQL()
			allow_empty = bool(dbcfg.get2 (
				option =  u'horstspace.scan_index.allow_partless_documents',
				workplace = gmSurgery.gmCurrentPractice().active_workplace,
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

		doc_type_pk = self._PhWheel_doc_type.GetData(can_create = True)
		if doc_type_pk is None:
			gmGuiHelpers.gm_show_error (
				aMessage = _('No document type applied. Choose a document type'),
				aTitle = title
			)
			return False

		if self._PRW_doc_comment.GetValue().strip() == '':
			gmGuiHelpers.gm_show_error (
				aMessage = _('No document comment supplied. Add a comment for this document.'),
				aTitle = title
			)
			return False

		if self._PhWheel_episode.GetValue().strip() == '':
			gmGuiHelpers.gm_show_error (
				aMessage = _('You must select an episode to save this document under.'),
				aTitle = title
			)
			return False

		if self._PhWheel_reviewer.GetData() is None:
			gmGuiHelpers.gm_show_error (
				aMessage = _('You need to select the doctor who must review the document from the list of staff members.'),
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
				workplace = gmSurgery.gmCurrentPractice().active_workplace,
				bias = 'workplace',
				default = ''
			)
			if device.strip() == u'':
				device = None
			if device is not None:
				return device

		try:
			devices = self.scan_module.get_devices()
		except:
			_log.LogException('cannot retrieve list of image sources')
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

		tmpdir = os.path.expanduser(os.path.join('~', '.gnumed', 'tmp'))
		try:
			gmTools.mkdir(tmpdir)
		except:
			tmpdir = None

		# FIXME: configure whether to use XSane or sane directly
		# FIXME: add support for xsane_device_settings argument
		try:
			fnames = self.scan_module.acquire_pages_into_files (
				device = chosen_device,
				delay = 5,
				tmpdir = tmpdir,
				calling_window = self
			)
		except ImportError:
			gmGuiHelpers.gm_show_error (
				aMessage = _(
					'No pages could be acquired from the source.\n\n'
					'This may mean the scanner driver is not properly installed\n\n'
					'On Windows you must install the TWAIN Python module\n'
					'while on Linux and MacOSX it is recommended to install\n'
					'the XSane package.'
				),
				aTitle = _('acquiring page')
			)
			return None

		if len(fnames) == 0:		# no pages scanned
			return True

		self.acquired_pages.extend(fnames)
		self.__reload_LBOX_doc_pages()

		return True
	#--------------------------------------------------------
	def _load_btn_pressed(self, evt):
		# patient file chooser
		dlg = wx.FileDialog(
			parent = None,
			message = _('Choose a file'),
			defaultDir = os.path.expanduser(os.path.join('~', 'gnumed')),
			defaultFile = '',
			wildcard = "%s (*)|*|TIFFs (*.tif)|*.tif|JPEGs (*.jpg)|*.jpg|%s (*.*)|*.*" % (_('all files'), _('all files (Win)')),
			style = wx.OPEN | wx.HIDE_READONLY | wx.FILE_MUST_EXIST | wx.MULTIPLE
		)
		result = dlg.ShowModal()
		if result != wx.ID_CANCEL:
			files = dlg.GetPaths()
			for file in files:
				self.acquired_pages.append(file)
			self.__reload_LBOX_doc_pages()
		dlg.Destroy()
	#--------------------------------------------------------
	def _show_btn_pressed(self, evt):
		# did user select a page ?
		page_idx = self._LBOX_doc_pages.GetSelection()
		if page_idx == -1:
			gmGuiHelpers.gm_show_info (
				aMessage = _('You must select a part before you can view it.'),
				aTitle = _('displaying part')
			)
			return None
		# now, which file was that again ?
		page_fname = self._LBOX_doc_pages.GetClientData(page_idx)
		(result, msg) = gmMimeLib.call_viewer_on_file(page_fname)
		if not result:
			gmGuiHelpers.gm_show_warning (
				aMessage = _('Cannot display document part:\n%s') % msg,
				aTitle = _('displaying part')
			)
			return None
		return 1
	#--------------------------------------------------------
	def _del_btn_pressed(self, event):
		page_idx = self._LBOX_doc_pages.GetSelection()
		if page_idx == -1:
			gmGuiHelpers.gm_show_info (
				aMessage = _('You must select a part before you can delete it.'),
				aTitle = _('deleting part')
			)
			return None
		page_fname = self._LBOX_doc_pages.GetClientData(page_idx)

		# 1) del item from self.acquired_pages
		self.acquired_pages[page_idx:(page_idx+1)] = []

		# 2) reload list box
		self.__reload_LBOX_doc_pages()

		# 3) kill file in the file system
		do_delete = gmGuiHelpers.gm_show_question (
			_(
"""Do you want to permanently delete the file

 [%s]

from your computer ?

If it is a temporary file for a page you just scanned
in this makes a lot of sense. In other cases you may
not want to lose the file.

Pressing [YES] will permanently remove the file
from your computer.""") % page_fname,
			_('deleting part')
		)
		if do_delete:
			try:
				os.remove(page_fname)
			except:
				_log.LogException('Error deleting file.')
				gmGuiHelpers.gm_show_error (
					aMessage = _('Cannot delete part in file [%s].\n\nYou may not have write access to it.') % page_fname,
					aTitle = _('deleting part')
				)

		return 1
	#--------------------------------------------------------
	def _save_btn_pressed(self, evt):

		if not self.__valid_for_save():
			return False

		wx.BeginBusyCursor()

		pat = gmPerson.gmCurrentPatient()
		doc_folder = pat.get_document_folder()
		emr = pat.get_emr()

		# create new document
		pk_episode = self._PhWheel_episode.GetData()
		if pk_episode is None:
			episode = emr.add_episode (
				episode_name = self._PhWheel_episode.GetValue().strip(),
				is_open = True
			)
			if episode is None:
				wx.EndBusyCursor()
				gmGuiHelpers.gm_show_error (
					aMessage = _('Cannot start episode [%s].') % self._PhWheel_episode.GetValue().strip(),
					aTitle = _('saving document')
				)
				return False
			pk_episode = episode['pk_episode']

		encounter = emr.get_active_encounter()['pk_encounter']
		document_type = self._PhWheel_doc_type.GetData()
		new_doc = doc_folder.add_document(document_type, encounter, pk_episode)
		if new_doc is None:
			wx.EndBusyCursor()
			gmGuiHelpers.gm_show_error (
				aMessage = _('Cannot create new document.'),
				aTitle = _('saving document')
			)
			return False

		# update business object with metadata
		# - date of generation
		new_doc['date'] = self._PhWheel_doc_date.GetData().get_pydt()
		# - external reference
		ref = gmMedDoc.get_ext_ref()
		if ref is not None:
			new_doc['ext_ref'] = ref
		# - comment
		comment = self._PRW_doc_comment.GetLineText(0).strip()
		if comment != '':
			new_doc['comment'] = comment
		# - save it
		if not new_doc.save_payload():
			wx.EndBusyCursor()
			gmGuiHelpers.gm_show_error (
				aMessage = _('Cannot update document metadata.'),
				aTitle = _('saving document')
			)
			return False
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

		# add document parts from files
		success, msg, filename = new_doc.add_parts_from_files(files=self.acquired_pages, reviewer=self._PhWheel_reviewer.GetData())
		if not success:
			wx.EndBusyCursor()
			gmGuiHelpers.gm_show_error (
				aMessage = msg,
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

		cfg = gmCfg.cCfgSQL()
		show_id = bool (
			cfg.get2 (
				option = 'horstspace.scan_index.show_doc_id',
				workplace = gmSurgery.gmCurrentPractice().active_workplace,
				bias = 'user'
			)
		)
		wx.EndBusyCursor()
		if show_id and (ref is not None):
			msg = _(
"""The reference ID for the new document is:

 <%s>

You probably want to write it down on the
original documents.

If you don't care about the ID you can switch
off this message in the GNUmed configuration.""") % ref
			gmGuiHelpers.gm_show_info (
				aMessage = msg,
				aTitle = _('saving document')
			)

		# prepare for next document
		self.__init_ui_data()
		gmDispatcher.send(signal='statustext', msg=_('Successfully saved new document.'))
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
#============================================================
class cSelectablySortedDocTreePnl(wxgSelectablySortedDocTreePnl.wxgSelectablySortedDocTreePnl):
	"""A panel with a document tree which can be sorted."""
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
	def _on_sort_by_type_selected(self, evt):
		self._doc_tree.sort_mode = 'type'
		self._doc_tree.SetFocus()
		self._rbtn_sort_by_type.SetValue(True)
#============================================================
class cDocTree(wx.TreeCtrl, gmRegetMixin.cRegetOnPaintMixin):
	# FIXME: handle expansion state
	"""This wx.TreeCtrl derivative displays a tree view of stored medical documents.

	It listens to document and patient changes and updated itself accordingly.
	"""
	_sort_modes = ['age', 'review', 'episode', 'type']
	_root_node_labels = None
	#--------------------------------------------------------
	def __init__(self, parent, id, *args, **kwds):
		"""Set up our specialised tree.
		"""
		kwds['style'] = wx.TR_NO_BUTTONS | wx.NO_BORDER
		wx.TreeCtrl.__init__(self, parent, id, *args, **kwds)

		gmRegetMixin.cRegetOnPaintMixin.__init__(self)

		tmp = _('available documents (%s)')
		cDocTree._root_node_labels = {
			'age': tmp % _('most recent on top'),
			'review': tmp % _('unreviewed on top'),
			'episode': tmp % _('sorted by episode'),
			'type': tmp % _('sorted by type')
		}

		self.root = None
		self.__sort_mode = 'age'

		self.__register_interests()
		self._schedule_data_reget()
	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def display_selected_part(self, *args, **kwargs):

		node = self.GetSelection()
		node_data = self.GetPyData(node)

		if not isinstance(node_data, gmMedDoc.cMedDocPart):
			return True

		self.__display_part(part = node_data)
		return True
	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def _get_sort_mode(self):
		return self.__sort_mode
	#-----
	def _set_sort_mode(self, mode):
		if mode is None:
			mode = 'age'

		if mode == self.__sort_mode:
			return

		if mode not in cDocTree._sort_modes:
			raise ValueError('invalid document tree sort mode [%s], valid modes: %s' % (mode, cDocTree._sort_modes))

		self.__sort_mode = mode

		curr_pat = gmPerson.gmCurrentPatient()
		if not curr_pat.is_connected():
			return

		self._schedule_data_reget()
	#-----
	sort_mode = property(_get_sort_mode, _set_sort_mode)
	#--------------------------------------------------------
	# reget-on-paint API
	#--------------------------------------------------------
	def _populate_with_data(self):
		curr_pat = gmPerson.gmCurrentPatient()
		if not curr_pat.is_connected():
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot load documents. No active patient.'))
			return False

		if not self.__populate_tree():
			return False

		return True
	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def __register_interests(self):
		# connect handlers
		wx.EVT_TREE_ITEM_ACTIVATED (self, self.GetId(), self._on_activate)
		wx.EVT_TREE_ITEM_RIGHT_CLICK (self, self.GetId(), self.__on_right_click)

#		 wx.EVT_LEFT_DCLICK(self.tree, self.OnLeftDClick)

		gmDispatcher.connect(signal = u'pre_patient_selection', receiver = self._on_pre_patient_selection)
		gmDispatcher.connect(signal = u'post_patient_selection', receiver = self._on_post_patient_selection)
		gmDispatcher.connect(signal = u'doc_mod_db', receiver = self._on_doc_mod_db)
		gmDispatcher.connect(signal = u'doc_page_mod_db', receiver = self._on_doc_page_mod_db)
	#--------------------------------------------------------
	def __populate_tree(self):

		wx.BeginBusyCursor()
		# clean old tree
		if self.root is not None:
			self.DeleteAllItems()

		# init new tree
		self.root = self.AddRoot(cDocTree._root_node_labels[self.__sort_mode], -1, -1)
		self.SetPyData(self.root, None)
		self.SetItemHasChildren(self.root, False)

		# read documents from database
		curr_pat = gmPerson.gmCurrentPatient()
		docs_folder = curr_pat.get_document_folder()
		docs = docs_folder.get_documents()
		if docs is None:
			name = curr_pat.get_names()
			gmGuiHelpers.gm_show_error (
				aMessage = _('Error searching documents for patient\n[%s %s].') % (name['firstnames'], name['lastnames']),
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

			parts = doc.get_parts()

			cmt = gmTools.coalesce(doc['comment'], _('no comment available'))
			page_num = len(parts)
			ref = gmTools.coalesce(initial = doc['ext_ref'], instead = _('no reference ID found'), template_initial = u'>%s<')

			if doc.has_unreviewed_parts():
				review = '!'
			else:
				review = ''

			label = _('%s%7s %s: %s (%s part(s), %s)') % (
				review,
				doc['date'].strftime('%m/%Y'),
				doc['l10n_type'][:26],
				cmt,
				page_num,
				ref
			)

			# need intermediate branch level ?
			if self.__sort_mode == 'episode':
				if not intermediate_nodes.has_key(doc['episode']):
					intermediate_nodes[doc['episode']] = self.AppendItem(parent = self.root, text = doc['episode'])
					self.SetPyData(intermediate_nodes[doc['episode']], None)
				parent = intermediate_nodes[doc['episode']]
			elif self.__sort_mode == 'type':
				if not intermediate_nodes.has_key(doc['l10n_type']):
					intermediate_nodes[doc['l10n_type']] = self.AppendItem(parent = self.root, text = doc['l10n_type'])
					self.SetPyData(intermediate_nodes[doc['l10n_type']], None)
				parent = intermediate_nodes[doc['l10n_type']]
			else:
				parent = self.root

			doc_node = self.AppendItem(parent = parent, text = label)
			self.SetItemBold(doc_node, bold=True)
			self.SetPyData(doc_node, doc)
			if len(parts) > 0:
				self.SetItemHasChildren(doc_node, True)

			# now add parts as child nodes
			for part in parts:

				pg = _('part %2s') % part['seq_idx']
				cmt = gmTools.coalesce(part['obj_comment'], _("no comment available"))
				sz = gmTools.size2str(part['size'])
				rev = gmTools.bool2str (
					bool = part['reviewed'] or part['reviewed_by_you'] or part['reviewed_by_intended_reviewer'],
					true_str = u'',
					false_str = ' [%s]' % _('unreviewed')
				)

#				if part['clinically_relevant']:
#					rel = ' [%s]' % _('Cave')
#				else:
#					rel = ''

				label = '%s%s: "%s" (%s)' % (pg, rev, cmt, sz)

				part_node = self.AppendItem(parent = doc_node, text = label)
				self.SetPyData(part_node, part)

		self.SortChildren(self.root)
		self.SelectItem(self.root)

		# FIXME: apply expansion state if available or else ...
		# FIXME: ... uncollapse to default state
		self.Expand(self.root)
		if self.__sort_mode in ['episode', 'type']:
			for key in intermediate_nodes.keys():
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
		item1 = self.GetPyData(node1)
		item2 = self.GetPyData(node2)

		# doc node
		if isinstance(item1, gmMedDoc.cMedDoc):

			date_field = 'date'
			#date_field = 'modified_when'

			if self.__sort_mode == 'age':
				# reverse sort by date
				if item1[date_field] > item2[date_field]:
					return -1
				if item1[date_field] == item2[date_field]:
					return 0
				return 1

			elif self.__sort_mode == 'episode':
				if item1['episode'] < item2['episode']:
					return -1
				if item1['episode'] == item2['episode']:
					# inner sort: reverse by date
					if item1[date_field] > item2[date_field]:
						return -1
					if item1[date_field] == item2[date_field]:
						return 0
					return 1
				return 1

			elif self.__sort_mode == 'review':
				# equality
				if item1.has_unreviewed_parts() == item2.has_unreviewed_parts():
					# inner sort: reverse by date
					if item1[date_field] > item2[date_field]:
						return -1
					if item1[date_field] == item2[date_field]:
						return 0
					return 1
				if item1.has_unreviewed_parts():
					return -1
				return 1

			elif self.__sort_mode == 'type':
				if item1['l10n_type'] < item2['l10n_type']:
					return -1
				if item1['l10n_type'] == item2['l10n_type']:
					# inner sort: reverse by date
					if item1[date_field] > item2[date_field]:
						return -1
					if item1[date_field] == item2[date_field]:
						return 0
					return 1
				return 1

			else:
				_log.Log(gmLog.lErr, 'unknown document sort mode [%s], reverse-sorting by age' % self.__sort_mode)
				# reverse sort by date
				if item1[date_field] > item2[date_field]:
					return -1
				if item1[date_field] == item2[date_field]:
					return 0
				return 1

		# part node
		if isinstance(item1, gmMedDoc.cMedDocPart):
			# compare sequence IDs (= "page" numbers)
			if item1['seq_idx'] < item2['seq_idx']:
				return -1
			if item1['seq_idx'] == item2['seq_idx']:
				return 0
			return 1

		# else sort alphabetically
		if item1 < item2:
			return -1
		if item1 == item2:
			return 0
		return 1
	#------------------------------------------------------------------------
	# event handlers
	#------------------------------------------------------------------------
	def _on_doc_mod_db(self, *args, **kwargs):
		# FIXME: remember current expansion state
		wx.CallAfter(self._schedule_data_reget)
	#------------------------------------------------------------------------
	def _on_doc_page_mod_db(self, *args, **kwargs):
		# FIXME: remember current expansion state
		wx.CallAfter(self._schedule_data_reget)
	#------------------------------------------------------------------------
	def _on_pre_patient_selection(self, *args, **kwargs):
		# FIXME: self.__store_expansion_history_in_db

		# empty out tree
		if self.root is not None:
			self.DeleteAllItems()
		self.root = None
	#------------------------------------------------------------------------
	def _on_post_patient_selection(self, *args, **kwargs):
		# FIXME: self.__load_expansion_history_from_db (but not apply it !)
		self._schedule_data_reget()
	#------------------------------------------------------------------------
	def _on_activate(self, event):
		node = event.GetItem()
		node_data = self.GetPyData(node)

		# exclude pseudo root node
		if node_data is None:
			return None

		# expand/collapse documents on activation
		if isinstance(node_data, gmMedDoc.cMedDoc):
			self.Toggle(node)
			return True

		# string nodes are labels such as episodes which may or may not have children
		if type(node_data) == type('string'):
			self.Toggle(node)
			return True

		self.__display_part(part = node_data)
		return True
	#--------------------------------------------------------
	def __on_right_click(self, evt):

		node = evt.GetItem()
		self.__curr_node_data = self.GetPyData(node)

		# exclude pseudo root node
		if self.__curr_node_data is None:
			return None

		# documents
		if isinstance(self.__curr_node_data, gmMedDoc.cMedDoc):
			self.__handle_doc_context()

		# parts
		if isinstance(self.__curr_node_data, gmMedDoc.cMedDocPart):
			self.__handle_part_context()

		del self.__curr_node_data
		evt.Skip()
	#--------------------------------------------------------
	def __activate_as_current_photo(self, evt):
		self.__curr_node_data.set_as_active_photograph()
	#--------------------------------------------------------
	def __display_curr_part(self, evt):
		self.__display_part(part=self.__curr_node_data)
	#--------------------------------------------------------
	def __review_curr_part(self, evt):
		self.__review_part(part=self.__curr_node_data)
	#--------------------------------------------------------
	def __show_description(self, evt):
		print "showing description"
	#--------------------------------------------------------
	# internal API
	#--------------------------------------------------------
	def __handle_doc_context(self):

		menu = wx.Menu(title = _('document menu'))

		# edit metadata
		ID = wx.NewId()
		menu.AppendItem(wx.MenuItem(menu, ID, _('Review/Edit properties')))
		wx.EVT_MENU(menu, ID, self.__review_curr_part)

		# export pages
		ID = wx.NewId()
		menu.AppendItem(wx.MenuItem(menu, ID, _('Export to disk')))
		wx.EVT_MENU(menu, ID, self.__export_doc_to_disk)

		# edit encounter
		ID = wx.NewId()
		menu.AppendItem(wx.MenuItem(menu, ID, _('Edit corresponding consultation')))
		wx.EVT_MENU(menu, ID, self.__edit_consultation_details)

		# delete for good
		ID = wx.NewId()
		menu.AppendItem(wx.MenuItem(menu, ID, _('Delete')))
		wx.EVT_MENU(menu, ID, self.__delete_document)

		# show descriptions
		descriptions = self.__curr_node_data.get_descriptions()
		desc_menu = wx.Menu()
		for desc in descriptions:
			d_id = wx.NewId()
			# contract string
			tmp = regex.split('\r\n+|\r+|\n+|\s+|\t+', desc)
			tmp = ' '.join(tmp)
			# but only use first 30 characters
			tmp = "%s ..." % tmp[:30]
			desc_menu.AppendItem(wx.MenuItem(desc_menu, d_id, tmp))
			# connect handler
			wx.EVT_MENU(desc_menu, d_id, self.__show_description)

		menu.AppendMenu(wx.NewId(), _('descriptions ...'), desc_menu)

		# show menu
		self.PopupMenu(menu, wx.DefaultPosition)
		menu.Destroy()
	#--------------------------------------------------------
	def __handle_part_context(self):
		# build menu
		menu = wx.Menu(title = _('part menu'))
		# display file
		ID = wx.NewId()
		menu.AppendItem(wx.MenuItem(menu, ID, _('Display part')))
		wx.EVT_MENU(menu, ID, self.__display_curr_part)
		# edit metadata
		ID = wx.NewId()
		menu.AppendItem(wx.MenuItem(menu, ID, _('Review/Edit properties')))
		wx.EVT_MENU(menu, ID, self.__review_curr_part)
		# make active patient photograph
		if self.__curr_node_data['type'] == 'patient photograph':
			ID = wx.NewId()
			menu.AppendItem(wx.MenuItem(menu, ID, _('Activate as current photo')))
			wx.EVT_MENU(menu, ID, self.__activate_as_current_photo)
		# show menu
		self.PopupMenu(menu, wx.DefaultPosition)
		menu.Destroy()
	#--------------------------------------------------------
	def __display_part(self, part):
		"""Display document part."""

		# sanity check
		if part['size'] == 0:
			_log.Log(gmLog.lErr, 'cannot display part [%s] - 0 bytes' % part['pk_obj'])
			gmGuiHelpers.gm_show_error (
				aMessage = _('Document part does not seem to exist in database !'),
				aTitle = _('showing document')
			)
			return None

		cfg = gmCfg.cCfgSQL()

		# get export directory for temporary files
		tmp_dir = gmTools.coalesce (
			cfg.get2 (
				option = "horstspace.tmp_dir",
				workplace = gmSurgery.gmCurrentPractice().active_workplace,
				bias = 'workplace'
			),
			os.path.expanduser(os.path.join('~', '.gnumed', 'tmp'))
		)
		_log.Log(gmLog.lData, "working into directory [%s]" % tmp_dir)

		# determine database export chunk size
		chunksize = int(cfg.get2 (
			option = "horstspace.blob_export_chunk_size",
			workplace = gmSurgery.gmCurrentPractice().active_workplace,
			bias = 'workplace',
			default = 1 * 1024 * 1024		# 1 MB
		))

		# shall we force blocking during view ?
		block_during_view = bool( cfg.get2 (
			option = 'horstspace.document_viewer.block_during_view',
			workplace = gmSurgery.gmCurrentPractice().active_workplace,
			bias = 'user',
			default = None
		))

		# display it
		successful, msg = part.display_via_mime (
			tmpdir = tmp_dir,
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
		review_after_display = int(cfg.get2 (
			option = 'horstspace.document_viewer.review_after_display',
			workplace = gmSurgery.gmCurrentPractice().active_workplace,
			bias = 'user',
			default = 2
		))
		if review_after_display == 1:			# always review
			self.__review_part(part=part)
		elif review_after_display == 2:			# review if no review by me exists
			review_by_me = filter(lambda rev: rev['is_review_by_you'], part.get_reviews())
			if len(review_by_me) == 0:
				self.__review_part(part=part)

		return True
	#--------------------------------------------------------
	def __review_part(self, part=None):
		dlg = cReviewDocPartDlg (
			parent = self,
			id = -1,
			part = part
		)
		dlg.ShowModal()
	#--------------------------------------------------------
	# document level context menu handlers
	#--------------------------------------------------------
	def __edit_consultation_details(self, evt):
		enc = gmEMRStructItems.cEncounter(aPK_obj=self.__curr_node_data['pk_encounter'])
		dlg = gmEMRStructWidgets.cEncounterEditAreaDlg(parent=self, encounter=enc)
		dlg.ShowModal()
	#--------------------------------------------------------
	def __export_doc_to_disk(self, evt):
		"""Export document into directory.

		- one file per object
		- into subdirectory named after patient
		"""
		pat = gmPerson.gmCurrentPatient()
		dname = '%s-%s%s' % (
			self.__curr_node_data['l10n_type'],
			self.__curr_node_data['date'].strftime('%Y-%m-%d'),
			gmTools.coalesce(self.__curr_node_data['ext_ref'], '', '-%s').replace(' ', '_')
		)
		def_dir = os.path.expanduser(os.path.join('~', 'gnumed', 'export', 'docs', pat['dirname'], dname))
		gmTools.mkdir(def_dir)

		dlg = wx.DirDialog (
			parent = self,
			message = _('Save document into directory ...'),
			defaultPath = def_dir,
			style = wx.DD_DEFAULT_STYLE
		)
		result = dlg.ShowModal()
		dirname = dlg.GetPath()
		dlg.Destroy()

		if result != wx.ID_OK:
			return True

		wx.BeginBusyCursor()
		fnames = self.__curr_node_data.export_parts_to_files(export_dir=dirname)
		wx.EndBusyCursor()

		gmDispatcher.send(signal='statustext', msg=_('Successfully exported %s parts into the directory [%s].') % (len(fnames), dirname))

		return True
	#--------------------------------------------------------
	def __delete_document(self, evt):
		curr_pat = gmPerson.gmCurrentPatient()
		emr = curr_pat.get_emr()
		enc = emr.get_active_encounter()
		gmMedDoc.delete_document(document_id = self.__curr_node_data['pk_doc'], encounter_id = enc['pk_encounter'])
#============================================================
# main
#------------------------------------------------------------
if __name__ == '__main__':
	_log.SetAllLogLevels(gmLog.lData)
	gmI18N.activate_locale()
	gmI18N.install_domain(domain = 'gnumed')

	#----------------------------------------
	#----------------------------------------
	if (len(sys.argv) > 1) and (sys.argv[1] == 'test'):
#		test_*()
		pass

#============================================================
# $Log: gmMedDocWidgets.py,v $
# Revision 1.155  2008-02-25 17:38:05  ncq
# - make parts listbox file drop target, too
#
# Revision 1.154  2008/01/27 21:16:45  ncq
# - label changes per Jim
# - allow partless docs
#
# Revision 1.153  2008/01/11 16:15:33  ncq
# - first/last -> first-/lastnames
#
# Revision 1.152  2007/12/23 20:29:35  ncq
# - store tmp docs in tmp/, not tmp/docs/
#
# Revision 1.151  2007/12/11 12:49:26  ncq
# - explicit signal handling
#
# Revision 1.150  2007/11/05 11:41:46  ncq
# - use blobs.delete_document()
#
# Revision 1.149  2007/10/31 22:07:18  ncq
# - delete document from context menu
#
# Revision 1.148  2007/10/31 11:26:18  ncq
# - hide less exceptions
#
# Revision 1.147  2007/10/29 13:22:32  ncq
# - make cDocTree a lot more self contained:
#   - make it a reget mixin child
#   - make sort_mode a property scheduling reload on set
#   - listen to patient changes
#     - empty tree on pre_sel
# 	- schedule reload on post_sel
#   - listen to doc and page changes and schedule appropriate reloads
#
# Revision 1.146  2007/10/12 07:27:02  ncq
# - check in drop target fix
#
# Revision 1.145  2007/10/07 12:32:41  ncq
# - workplace property now on gmSurgery.gmCurrentPractice() borg
#
# Revision 1.144  2007/09/07 10:57:54  ncq
# - document review_after_display
#
# Revision 1.143  2007/08/29 14:43:06  ncq
# - factor out forms/letters related code
# - fix syntax error re stray, gmLog.L* consts
#
# Revision 1.142  2007/08/28 14:18:13  ncq
# - no more gm_statustext()
#
# Revision 1.141  2007/08/20 22:12:49  ncq
# - support _on_load_button_pressed in form template editor
#
# Revision 1.140  2007/08/20 16:23:52  ncq
# - support editing form templates from create_new_letter
# - cFormTemplateEditAreaDlg
#
# Revision 1.139  2007/08/20 14:29:31  ncq
# - cleanup, start of test suite
# - form template edit area
#
# Revision 1.138  2007/08/15 09:20:43  ncq
# - use cOOoLetter.show()
# - cleanup
# - use gmTools.size2str()
#
# Revision 1.137  2007/08/13 22:11:38  ncq
# - use cFormTemplate
# - pass placeholder handler to form instance handler
#
# Revision 1.136  2007/08/12 00:10:55  ncq
# - improve create_new_letter()
# - (_)save_file_as_new_document() and listen for 'import_document_from_file'
# - no more gmSignals.py
#
# Revision 1.135  2007/08/09 07:59:42  ncq
# - streamline __display_part() with part.display_via_mime()
#
# Revision 1.134  2007/07/22 10:04:23  ncq
# - streamline create_new_letter()
#
# Revision 1.133  2007/07/22 09:27:28  ncq
# - create_new_letter()
# - adjust to get_choice_from_list() changes
# - tmp/ now in .gnumed/
#
# Revision 1.132  2007/07/11 21:10:31  ncq
# - cleanup
#
# Revision 1.131  2007/06/28 12:39:37  ncq
# - make pages listbox in scan/index panel be a drop target itself, too
# - handle preset device = '' as unconfigured
#
# Revision 1.130  2007/06/18 20:38:32  ncq
# - use gmListWidgets.get_choice_from_list()
#
# Revision 1.129  2007/06/12 13:24:48  ncq
# - allow editing of encounter corresponding to a document
#
# Revision 1.128  2007/06/10 10:17:36  ncq
# - gmScanBackend now uses exceptions for error handling
# - improved error message when no sanner driver found
#
# Revision 1.127  2007/05/21 14:49:20  ncq
# - use pat['dirname'] for export
#
# Revision 1.126  2007/05/21 13:05:25  ncq
# - catch-all wildcard on UNIX must be *, not *.*
#
# Revision 1.125  2007/05/20 01:28:09  ncq
# - only repopulate if we actually saved a new doc type
#
# Revision 1.124  2007/05/18 22:02:30  ncq
# - create export/docs/<patient>/<doc>/ *subdir* for document export
#
# Revision 1.123  2007/05/14 13:11:24  ncq
# - use statustext() signal
#
# Revision 1.122  2007/04/23 16:59:35  ncq
# - make cReviewDocPartDlg accept documents as well as document
#   parts and dynamically adjust UI appropriately
#
# Revision 1.121  2007/04/23 01:08:04  ncq
# - add "activate as current photo" to popup menu
#
# Revision 1.120  2007/04/21 19:40:06  ncq
# - handle seq_idx spin ctrl in review doc (part)
#
# Revision 1.119  2007/04/02 18:39:52  ncq
# - gmFuzzyTimestamp -> gmDateTime
#
# Revision 1.118  2007/03/31 21:51:05  ncq
# - add xsane default device option
#
# Revision 1.117  2007/03/08 16:21:11  ncq
# - support blobs.doc_obj.filename
#
# Revision 1.116  2007/02/22 17:41:13  ncq
# - adjust to gmPerson changes
#
# Revision 1.115  2007/02/17 18:28:33  ncq
# - factor out get_device_to_use() and use it in _scan_btn_pressed()
# - support pre-setting device, only directly supported by XSane so far
#
# Revision 1.114  2007/02/17 14:13:11  ncq
# - gmPerson.gmCurrentProvider().workplace now property
#
# Revision 1.113  2007/02/06 13:43:40  ncq
# - no more aDelay in __init__()
#
# Revision 1.112  2007/02/05 12:15:23  ncq
# - no more aMatchProvider/selection_only in cPhraseWheel.__init__()
#
# Revision 1.111  2007/02/04 15:55:14  ncq
# - use SetText()
#
# Revision 1.110  2007/01/18 22:13:37  ncq
# - tell user when we expand a folder to extract files
#
# Revision 1.109  2007/01/17 14:01:56  ncq
# - when folder dropped onto scanidxpnl extract files one level into it
#
# Revision 1.108  2007/01/12 13:10:11  ncq
# - use cFileDropTarget in ScanIdxPnl
#
# Revision 1.107  2007/01/10 23:01:07  ncq
# - properly update document/object metadata
#
# Revision 1.106  2007/01/07 23:08:52  ncq
# - improve cDocumentCommentPhraseWheel query and link it to the doc_type field
# - add "export to disk" to doc tree context menu
#
# Revision 1.105  2007/01/06 23:42:35  ncq
# - cDocumentCommentPhraseWeel and adjust to wxGlade based uses thereof
#
# Revision 1.104  2006/12/27 16:45:42  ncq
# - adjust to acquire_pages_into_files() returning a list
#
# Revision 1.103  2006/12/21 10:55:09  ncq
# - fix inverted is_in_use logic on enabling delete button
#
# Revision 1.102  2006/12/13 22:32:17  ncq
# - need to explicitely check for "is_user_defined is True/False"
#
# Revision 1.101  2006/12/13 20:55:22  ncq
# - is_user -> is_user_defined
#
# Revision 1.100  2006/12/11 21:40:12  ncq
# - support in_use in doc type list ctrl
# - slight improvement of doc type edit dialog logic
#
# Revision 1.99  2006/11/24 10:01:31  ncq
# - gm_beep_statustext() -> gm_statustext()
#
# Revision 1.98  2006/11/06 10:01:17  ncq
# - handle _on_description_modified() in edit-doc-types
#
# Revision 1.97  2006/10/31 17:22:49  ncq
# - unicode()ify queries
# - cleanup
# - PgResult is now dict, so use it instead of index
# - add missing os.path.expanduser()
#
# Revision 1.96  2006/10/25 07:46:44  ncq
# - Format() -> strftime() since datetime.datetime does not have .Format()
#
# Revision 1.95  2006/10/24 13:26:11  ncq
# - no more gmPG.
# - use cMatchProvider_Provider() in scan/index panel
#
# Revision 1.94  2006/10/08 11:05:32  ncq
# - properly use db cfg
#
# Revision 1.93  2006/09/19 12:00:42  ncq
# - clear scan/idx panel on patient change
#
# Revision 1.92  2006/09/12 17:27:35  ncq
# - support horstspace.document_viewer.block_during_view
#
# Revision 1.91  2006/09/01 15:03:26  ncq
# - improve scanner device choice handling
# - better tmp dir handling on document import/export
#
# Revision 1.90  2006/07/24 20:51:26  ncq
# - get_by_user() -> get2()
#
# Revision 1.89  2006/07/10 21:57:43  ncq
# - add bool() where needed
#
# Revision 1.88  2006/07/10 21:48:09  ncq
# - handle cDocumentType
# - implement actions in document type editor
#
# Revision 1.87  2006/07/07 12:08:16  ncq
# - cleanup
# - add document type editing panel and dialog
#
# Revision 1.86  2006/07/04 22:36:27  ncq
# - doc type selector is now phrasewheel in properties editor
#
# Revision 1.85  2006/07/04 21:39:37  ncq
# - add cDocumentTypeSelectionPhraseWheel and use it in scan-index-panel
#
# Revision 1.84  2006/06/26 13:07:57  ncq
# - episode selection phrasewheel knows how to create episodes
#   when told to do so in GetData() so use that
#
# Revision 1.83  2006/06/21 15:54:17  ncq
# - properly set reviewer on cMedDoc
#
# Revision 1.82  2006/06/17 14:10:32  ncq
# - make review-after-display-if-needed the default
#
# Revision 1.81  2006/06/15 21:41:16  ncq
# - episode selector phrasewheel returns PK, not instance
#
# Revision 1.80  2006/06/15 07:13:21  ncq
# - used PK of episode instance in add_document
#
# Revision 1.79  2006/06/09 14:42:19  ncq
# - allow review from document
# - always apply review to all pages
#
# Revision 1.78  2006/06/05 21:36:20  ncq
# - add ext_ref field to properties editor
# - add repopulate_ui() to cScanIdxPnl since it's a notebook plugin
# - add "type" sort mode to doc tree
#
# Revision 1.77  2006/06/04 21:51:43  ncq
# - handle doc type/comment/date in properties editor dialog
#
# Revision 1.76  2006/05/31 12:17:04  ncq
# - cleanup, string improvements
# - review dialog:
#   - init review of current user if any
#   - do not list review of current user under reviews by other people ...
#   - implement save action
#
# Revision 1.75  2006/05/28 16:40:16  ncq
# - add ' ' to initial episode SetValue() to avoid popping up pick list
# - better labels in list of existing reviews
# - handle checkbox for review
# - start save handling
# - use episode selection phrasewheel
#
# Revision 1.74  2006/05/25 22:22:39  ncq
# - adjust to rearranged review dialog
# - nicely resize review columns
# - remove current users review from "other reviews" list
# - let user edit own review below "other reviews" list
# - properly use fuzzy timestamp in scan/index panel
#
# Revision 1.73  2006/05/24 10:34:51  ncq
# - use cFuzzyTimestampInput
#
# Revision 1.72  2006/05/20 18:53:39  ncq
# - cleanup
# - mark closed episodes in phrasewheel
# - add match provider to reviewer selection phrasewheel
# - handle reviewer phrasewheel
# - set reviewer in add_parts_from_files()
# - signal successful document saving
#
# Revision 1.71  2006/05/16 15:54:39  ncq
# - properly handle check boxes
#
# Revision 1.70  2006/05/15 13:36:00  ncq
# - signal cleanup:
#   - activating_patient -> pre_patient_selection
#   - patient_selected -> post_patient_selection
#
# Revision 1.69  2006/05/15 07:02:28  ncq
# - it -> is
#
# Revision 1.68  2006/05/14 21:44:22  ncq
# - add get_workplace() to gmPerson.gmCurrentProvider and make use thereof
# - remove use of gmWhoAmI.py
#
# Revision 1.67  2006/05/14 20:43:38  ncq
# - properly use get_devices() in gmScanBackend
#
# Revision 1.66  2006/05/12 21:59:35  ncq
# - set proper radiobutton in _on_sort_by_*()
#
# Revision 1.65  2006/05/12 12:18:11  ncq
# - whoami -> whereami cleanup
# - use gmCurrentProvider()
#
# Revision 1.64  2006/05/10 13:07:00  ncq
# - set focus to doc tree widget after selecting sort mode
# - collapse/expand doc tree nodes on ENTER/double-click
#
# Revision 1.63  2006/05/08 22:04:23  ncq
# - sigh, doc_med content date must be timestamp after all so use proper formatting
#
# Revision 1.62  2006/05/08 18:21:29  ncq
# - vastly improved document tree when sorting by episode
#
# Revision 1.61  2006/05/08 16:35:32  ncq
# - cleanup
# - add event handlers for sorting
# - make tree really sort - wxPython seems to forget to call
#   SortChildren() so call it ourselves
#
# Revision 1.60  2006/05/07 15:34:01  ncq
# - add cSelectablySortedDocTreePnl
#
# Revision 1.59  2006/05/01 18:49:30  ncq
# - better named variables
# - match provider in ScanIdxPnl
# - episode handling on save
# - as user before deleting files from disc
# - fix node formatting in doc tree
#
# Revision 1.58  2006/04/30 15:52:53  shilbert
# - event handler for document loading was added
#
# Revision 1.57  2006/02/27 15:42:14  ncq
# - implement cancel button in review dialog
# - invoke review after displaying doc part depending on cfg
#
# Revision 1.56  2006/02/13 19:10:14  ncq
# - actually display previous reviews in list
#
# Revision 1.55  2006/02/13 08:29:19  ncq
# - further work on the doc review control
#
# Revision 1.54  2006/02/10 16:33:19  ncq
# - popup review dialog from doc part right-click menu
#
# Revision 1.53  2006/02/05 15:03:22  ncq
# - doc tree:
#   - document part popup menu, stub for review dialog
#   - improved part display in doc tree
# - start handling relevant/abnormal check boxes in scan/index
#
# Revision 1.52  2006/02/05 14:16:29  shilbert
# - more checks for required values before commiting document to database
#
# Revision 1.51  2006/01/27 22:33:44  ncq
# - display reviewed/signed status in document tree
#
# Revision 1.50  2006/01/24 22:32:14  ncq
# - allow multiple files to be selected at once from file selection dialog
#
# Revision 1.49  2006/01/23 22:11:36  ncq
# - improve display
#
# Revision 1.48  2006/01/23 17:36:32  ncq
# - cleanup
# - display/use full path with file name after "load file" in scan&index
# - only add loaded file to file list if not cancelled
#
# Revision 1.47  2006/01/22 18:09:30  ncq
# - improve file name string in scanned pages list
# - force int() on int from db cfg
#
# Revision 1.46  2006/01/21 23:57:18  shilbert
# - acquire file from filesystem has been added
#
# Revision 1.45  2006/01/16 22:10:10  ncq
# - some cleanup
#
# Revision 1.44  2006/01/16 20:03:02  shilbert
# *** empty log message ***
#
# Revision 1.43  2006/01/16 19:37:25  ncq
# - use get_devices()
#
# Revision 1.42  2006/01/15 13:14:12  shilbert
# - support for multiple image source finished
#
# Revision 1.41  2006/01/15 10:02:23  shilbert
# - initial support for multiple image scanner devices
#
# Revision 1.40  2006/01/14 23:21:19  shilbert
# - fix for correct doc type (pk) handling
#
# Revision 1.39  2006/01/14 10:34:53  shilbert
# - fixed some some bugs which prevented document to be saved in DB
#
# Revision 1.38  2006/01/13 11:06:33  ncq
# - properly use gmGuiHelpers
# - properly fall back to default temporary directory
#
# Revision 1.37  2006/01/01 18:14:25  shilbert
# - fixed indentation problem
#
# Revision 1.36  2006/01/01 17:44:43  ncq
# - comment on proper user of emr.add_document()
#
# Revision 1.35  2006/01/01 17:23:29  ncq
# - properly use backend option for temp dir to
#   temporarily export docs into for viewing
#
# Revision 1.34  2005/12/16 12:04:25  ncq
# - fix silly indentation bug
#
# Revision 1.33  2005/12/14 17:01:03  ncq
# - use document_folder class and other gmMedDoc.py goodies
#
# Revision 1.32  2005/12/14 15:54:01  ncq
# - cleanup
#
# Revision 1.31  2005/12/14 15:40:54  ncq
# - add my changes regarding new config handling
#
# Revision 1.30  2005/12/14 14:08:24  shilbert
# - minor cleanup of ncq's changes
#
# Revision 1.29  2005/12/14 10:42:11  ncq
# - use cCfgSQL.get_by_user in scan&index panel on showing document reference ID
#
# Revision 1.28  2005/12/13 21:44:31  ncq
# - start _save_btn_pressed() so people see where we are going
#
# Revision 1.27  2005/12/06 17:59:12  ncq
# - make scan/index panel work more
#
# Revision 1.26  2005/12/02 22:46:21  shilbert
# - fixed inconsistent naming of vaiables which caused a bug
#
# Revision 1.25  2005/12/02 17:31:05  shilbert
# - readd document types as per Ian's suggestion
#
# Revision 1.24  2005/12/02 02:09:02  shilbert
# - quite a few feature updates within the scope of scan&idx panel
#
# Revision 1.23  2005/11/29 19:00:09  ncq
# - some cleanup
#
# Revision 1.22  2005/11/27 12:46:21  ncq
# - cleanup
#
# Revision 1.21  2005/11/27 01:57:28  shilbert
# - moved some of the feature back in
#
# Revision 1.20  2005/11/26 21:08:00  shilbert
# - some more iterations on the road
#
# Revision 1.19  2005/11/26 16:56:04  shilbert
# - initial working version with scan /index documents support
#
# Revision 1.18  2005/11/26 16:38:55  shilbert
# - slowly readding features
#
# Revision 1.17  2005/11/26 08:21:37  ncq
# - scan/index wxGlade child class fleshed out a bit more
#
# Revision 1.16  2005/11/25 23:02:49  ncq
# - start scan/idx panel inheriting from wxGlade base class
#
# Revision 1.15  2005/09/28 21:27:30  ncq
# - a lot of wx2.6-ification
#
# Revision 1.14  2005/09/28 15:57:48  ncq
# - a whole bunch of wx.Foo -> wx.Foo
#
# Revision 1.13  2005/09/26 18:01:51  ncq
# - use proper way to import wx26 vs wx2.4
# - note: THIS WILL BREAK RUNNING THE CLIENT IN SOME PLACES
# - time for fixup
#
# Revision 1.12  2005/09/24 09:17:29  ncq
# - some wx2.6 compatibility fixes
#
# Revision 1.11  2005/03/06 14:54:19  ncq
# - szr.AddWindow() -> Add() such that wx2.5 works
# - 'demographic record' -> get_identity()
#
# Revision 1.10  2005/01/31 10:37:26  ncq
# - gmPatient.py -> gmPerson.py
#
# Revision 1.9  2004/10/17 15:57:36  ncq
# - after pat.get_documents():
#   1) separate len(docs) == 0 from docs is None
#   2) only the second really is an error
#   3) however, return True from it, too, as we
#      informed the user about the error already
#
# Revision 1.8  2004/10/17 00:05:36  sjtan
#
# fixup for paint event re-entry when notification dialog occurs over medDocTree graphics
# area, and triggers another paint event, and another notification dialog , in a loop.
# Fixup is set flag to stop _repopulate_tree, and to only unset this flag when
# patient activating signal gmMedShowDocs to schedule_reget, which is overridden
# to include resetting of flag, before calling mixin schedule_reget.
#
# Revision 1.7  2004/10/14 12:11:50  ncq
# - __on_activate -> _on_activate
#
# Revision 1.6  2004/10/11 19:56:03  ncq
# - cleanup, robustify, attach doc/part VO directly to node
#
# Revision 1.5  2004/10/01 13:34:26  ncq
# - don't fail to display just because some metadata is missing
#
# Revision 1.4  2004/09/19 15:10:44  ncq
# - lots of cleanup
# - use status message instead of error box on missing patient
#   so that we don't get an endless loop
#   -> paint_event -> update_gui -> no-patient message -> paint_event -> ...
#
# Revision 1.3  2004/07/19 11:50:43  ncq
# - cfg: what used to be called "machine" really is "workplace", so fix
#
# Revision 1.2  2004/07/18 20:30:54  ncq
# - wxPython.true/false -> Python.True/False as Python tells us to do
#
# Revision 1.1  2004/06/26 23:39:34  ncq
# - factored out widgets for re-use
#
