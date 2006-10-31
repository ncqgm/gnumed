"""GNUmed medical document handling widgets.
"""
#================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmMedDocWidgets.py,v $
# $Id: gmMedDocWidgets.py,v 1.97 2006-10-31 17:22:49 ncq Exp $
__version__ = "$Revision: 1.97 $"
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"

import os.path, sys, re, time

import wx

from Gnumed.pycommon import gmLog, gmI18N, gmCfg, gmPG2, gmMimeLib, gmExceptions, gmMatchProvider, gmDispatcher, gmSignals, gmFuzzyTimestamp
from Gnumed.business import gmPerson, gmMedDoc
from Gnumed.wxpython import gmGuiHelpers, gmRegetMixin, gmPhraseWheel, gmPlugin
from Gnumed.wxGladeWidgets import wxgScanIdxPnl, wxgReviewDocPartDlg, wxgSelectablySortedDocTreePnl, wxgEditDocumentTypesPnl, wxgEditDocumentTypesDlg

_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)

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
	#--------------------------------------------------------
	def repopulate_ui(self):

		self.doc_types = gmMedDoc.get_document_types()
		pos = len(self.doc_types) + 1
		self._LCTRL_doc_type.DeleteAllItems()

		for doc_type in self.doc_types:
			row_num = self._LCTRL_doc_type.InsertStringItem(pos, label = doc_type['type'])
			self._LCTRL_doc_type.SetStringItem(index = row_num, col = 1, label = doc_type['l10n_type'])
			if doc_type['is_user']:
				self._LCTRL_doc_type.SetStringItem(index = row_num, col = 2, label = 'X')
			else:
				self._LCTRL_doc_type.SetItemTextColour(row_num, col=wx.LIGHT_GREY)

		if len(self.doc_types) > 0:
			self._LCTRL_doc_type.SetColumnWidth(col=0, width=wx.LIST_AUTOSIZE)
			self._LCTRL_doc_type.SetColumnWidth(col=1, width=wx.LIST_AUTOSIZE)
			self._LCTRL_doc_type.SetColumnWidth(col=2, width=wx.LIST_AUTOSIZE_USEHEADER)

		self._BTN_rename.Enable(False)
		self._BTN_add.Enable(False)
		self._BTN_delete.Enable(False)

		self._TCTRL_type.SetValue('')
		self._ChBOX_is_user.SetValue(False)
		self._TCTRL_description.SetValue('')

		self._LCTRL_doc_type.SetFocus()
	#--------------------------------------------------------
	# event handlers
	#--------------------------------------------------------
	def _on_list_item_selected(self, evt):
		doc_type = self.doc_types[self._LCTRL_doc_type.GetFirstSelected()]

		self._TCTRL_type.SetValue(doc_type['type'])
		self._TCTRL_type.SetEditable(bool(doc_type['is_user']))
		self._ChBOX_is_user.SetValue(bool(doc_type['is_user']))
		self._TCTRL_description.SetValue(doc_type['l10n_type'])

		self._BTN_rename.Enable(bool(doc_type['is_user']))
		self._BTN_delete.Enable(bool(doc_type['is_user']))
		self._BTN_add.Enable(True)
		return
	#--------------------------------------------------------
	def _on_rename_button_pressed(self, event):
		doc_type = self.doc_types[self._LCTRL_doc_type.GetFirstSelected()]
		doc_type['type'] = self._TCTRL_type.GetValue().strip()
		doc_type.save_payload()			# FIXME: error handling ?
		doc_type.set_translation(translation = self._TCTRL_description.GetValue().strip())

		self.repopulate_ui()
		return
	#--------------------------------------------------------
	def _on_delete_button_pressed(self, event):
		doc_type = self.doc_types[self._LCTRL_doc_type.GetFirstSelected()]
		gmMedDoc.delete_document_type(document_type = doc_type)			# FIXME: error handling

		self.repopulate_ui()
		return
	#--------------------------------------------------------
	def _on_add_button_pressed(self, event):
		if self._TCTRL_type.IsEditable() and self._TCTRL_type.IsModified():
			doc_type = gmMedDoc.create_document_type(document_type = self._TCTRL_type.GetValue().strip())
			doc_type.set_translation(translation = self._TCTRL_description.GetValue().strip())
		else:
			gmMedDoc.create_document_type(document_type = self._TCTRL_description.GetValue().strip())

		self.repopulate_ui()
		return
#============================================================
class cDocumentTypeSelectionPhraseWheel(gmPhraseWheel.cPhraseWheel):
	"""Let user select a document type."""
	def __init__(self, *args, **kwargs):

		mp = gmMatchProvider.cMatchProvider_SQL2 (
			queries = [
u"""select * from ((
	select pk_doc_type, l10n_type, 1 as rank from blobs.v_doc_type where
		is_user is True and
		l10n_type %(fragment_condition)s
) union (
	select pk_doc_type, l10n_type, 2 from blobs.v_doc_type where
		is_user is False and
		l10n_type %(fragment_condition)s
)) as q1 order by q1.rank, q1.l10n_type
"""]
			)
		mp.setThresholds(2, 4, 6)

		kwargs['aMatchProvider'] = mp
		kwargs['aDelay'] = 50
		kwargs['selection_only'] = False
		gmPhraseWheel.cPhraseWheel.__init__ (
			self,
			*args,
			**kwargs
		)
	#--------------------------------------------------------
	def GetData(self, can_create=False):
		if self.data is None:
			if can_create:
				self.data = gmMedDoc.create_document_type(self.GetValue().strip())['pk_doc_type']	# FIXME: error handling
		return self.data
#============================================================
class cReviewDocPartDlg(wxgReviewDocPartDlg.wxgReviewDocPartDlg):
	def __init__(self, *args, **kwds):
		self.__part = kwds['part']
		del kwds['part']
		wxgReviewDocPartDlg.wxgReviewDocPartDlg.__init__(self, *args, **kwds)
		self.__init_ui_data()
	#--------------------------------------------------------
	# internal API
	#--------------------------------------------------------
	def __init_ui_data(self):
		# associated episode (add " " to avoid popping up pick list)
		self._PhWheel_episode.SetValue('%s ' % self.__part['episode'], self.__part['pk_episode'])
		self._PhWheel_doc_type.SetValue(value = self.__part['l10n_type'], data = self.__part['pk_type'])
		self._TCTRL_doc_comment.SetValue(self.__part['doc_comment'])
		fts = gmFuzzyTimestamp.cFuzzyTimestamp(timestamp = self.__part['date_generated'])
		self._PhWheel_doc_date.SetValue(fts.strftime('%Y-%m-%d'), fts)
		if self.__part['ext_ref'] is not None:
			self._TCTRL_reference.SetValue(self.__part['ext_ref'])

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

		doc = self.__part.get_containing_document()

		# 1) handle associated episode
		pk_episode = self._PhWheel_episode.GetData(can_create=True, is_open=True)
		if pk_episode is None:
			# FIXME: allow attaching to health issue
			gmGuiHelpers.gm_show_error (
				_('Cannot create episode\n [%s]'),
				_('editing document properties')
			)
			return False
		if pk_episode != doc['pk_episode']:
			# since the phrasewheel operates on the active
			# patient all episodes really should belong
			# to it so we don't check patient change
			doc['pk_episode'] = pk_episode

		doc_type = self._PhWheel_doc_type.GetData(can_create = True)
		if doc_type is not None:
			if doc_type != doc['pk_type']:
				doc['pk_type'] = doc_type
		else:
			gmGuiHelpers.gm_beep_statustext(_('Cannot change document type to [%s].') % self._PhWheel_doc_type.GetValue().strip())

		if self._TCTRL_doc_comment.IsModified():
			doc['comment'] = self._TCTRL_doc_comment.GetValue().strip()

		if self._PhWheel_doc_date.IsModified():
			doc['date'] = self._PhWheel_doc_date.GetData().timestamp

		if self._TCTRL_reference.IsModified():
			doc['ext_ref'] = self._TCTRL_reference.GetValue().strip()

		# 2) handle review
		if self._ChBOX_review.GetValue():
			provider = gmPerson.gmCurrentProvider()
			abnormal = self._ChBOX_abnormal.GetValue()
			relevant = self._ChBOX_relevant.GetValue()
			msg = None
			# - on all pages
			if self._ChBOX_sign_all_pages.GetValue():
				if not doc.set_reviewed(technically_abnormal = abnormal, clinically_relevant = relevant):
					msg = _('Error setting "reviewed" status of this document.')
				if self._ChBOX_responsible.GetValue():
					if not doc.set_primary_reviewer(reviewer = provider['pk_staff']):
						msg = _('Error setting responsible clinician for this document.')
			# - just on this page
			else:
				if not self.__part.set_reviewed(technically_abnormal = abnormal, clinically_relevant = relevant):
					msg = _('Error setting "reviewed" status of this page.')
				if self._ChBOX_responsible.GetValue():
					self.__part['pk_intended_reviewer'] = provider['pk_staff']

			# FIXME: if msg is not None

		success, data = self.__part.save_payload()
		if not success:
			gmGuiHelpers.gm_show_error (
				_('Error saving document review.'),
				_('editing document properties')
			)
			return False

		success, data = doc.save_payload()
		if not success:
			gmGuiHelpers.gm_show_error (
				_('Cannot link the document to episode\n\n [%s]') % epi_name,
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
		# NOTE: for now *always* apply to all pages so we can
		# NOTE: offer review from document level as well
		#self._ChBOX_sign_all_pages.Enable(enable = state)
#============================================================
# FIXME: this must listen to patient change signals ...
class cScanIdxDocsPnl(wxgScanIdxPnl.wxgScanIdxPnl, gmPlugin.cPatientChange_PluginMixin):
	def __init__(self, *args, **kwds):
		wxgScanIdxPnl.wxgScanIdxPnl.__init__(self, *args, **kwds)
		gmPlugin.cPatientChange_PluginMixin.__init__(self)

		self._PhWheel_reviewer.setMatchProvider(mp = gmPerson.cMatchProvider_Provider())

		self.__init_ui_data()

		# do not import globally since we might want to use
		# this module without requiring any scanner to be available
		from Gnumed.pycommon import gmScanBackend
		self.scan_module = gmScanBackend
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
		self._PhWheel_episode.SetValue('')
		self._PhWheel_doc_type.SetValue('')
		# -----------------------------
		# FIXME: make this configurable: either now() or last_date()
		fts = gmFuzzyTimestamp.cFuzzyTimestamp()
		self._PhWheel_doc_date.SetValue(fts.strftime('%Y-%m-%d'), fts)
		self._TBOX_doc_comment.SetValue('')
		# FIXME: should be set to patient's primary doc
		self._PhWheel_reviewer.selection_only = True
		me = gmPerson.gmCurrentProvider()
		self._PhWheel_reviewer.SetValue (
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
				self._LBOX_doc_pages.Append(_('page %s: %s' % (i+1, fname)), fname)
	#--------------------------------------------------------
	def __valid_for_save(self):
		title = _('saving document')

		if self.acquired_pages is None or len(self.acquired_pages) == 0:
			gmGuiHelpers.gm_show_error (
				aMessage = _('No pages to save. Aquire some pages first.'),
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

		if self._TBOX_doc_comment.GetValue().strip() == '':
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
	# event handling API
	#--------------------------------------------------------
	def _scan_btn_pressed(self, evt):
		devices = self.scan_module.get_devices()

		if devices is False:
			gmGuiHelpers.gm_beep_statustext (
				_('There is no scanner support installed on this machine.'),
				gmLog.lWarn
			)
			return None

		# TWAIN doesn't have get_devices() :-(
		if devices is None:
			chosen_device = None
		else:
			if len(devices) == 0:
				gmGuiHelpers.gm_beep_statustext (
					_('Cannot find an active scanner.'),
					gmLog.lWarn
				)
				return None
			device_names = []
			for device in devices:
				device_names.append('%s (%s)' % (device[2], device[0]))
			# wxpython does not support client data in wxSingleChoiceDialog
			device_idx = gmGuiHelpers.gm_SingleChoiceDialog (
				aMessage = _('Select an image capture device'),
				aTitle = _('device selection'),
				choices = device_names
			)
			if device_idx is False:
				return None
			chosen_device = devices[device_idx][0]

		tmpdir = os.path.expanduser(os.path.join('~', 'gnumed', 'tmp'))
		if not os.path.isdir(tmpdir):
			try:
				os.makedirs(tmpdir)
			except:
				tmpdir = None
		fname = self.scan_module.acquire_page_into_file (
			device = chosen_device,
			delay = 5,
			tmpdir = tmpdir,
			calling_window = self
		)
		if fname is False:
			gmGuiHelpers.gm_show_error (
				aMessage = _('Page could not be acquired from source.'),
				aTitle = _('acquiring page')
			)
			return None
		self.acquired_pages.append(fname)
		# update list of pages in GUI
		self.__reload_LBOX_doc_pages()
	#--------------------------------------------------------
	def _load_btn_pressed(self, evt):
		# patient file chooser
		dlg = wx.FileDialog(
			parent = None,
			message = _('Choose a file'),
			defaultDir = os.path.expanduser(os.path.join('~', 'gnumed')),
			defaultFile = '',
			wildcard = "all (*.*)|*.*|TIFFs (*.tif)|*.tif|JPEGs (*.jpg)|*.jpg",
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
				aMessage = _('You must select a page before you can view it.'),
				aTitle = _('displaying page')
			)
			return None
		# now, which file was that again ?
		page_fname = self._LBOX_doc_pages.GetClientData(page_idx)
		(result, msg) = gmMimeLib.call_viewer_on_file(page_fname)
		if not result:
			gmGuiHelpers.gm_show_warning (
				aMessage = _('Cannot display document part:\n%s') % msg,
				aTitle = _('displaying page')
			)
			return None
		return 1
	#--------------------------------------------------------
	def _del_btn_pressed(self, event):
		page_idx = self._LBOX_doc_pages.GetSelection()
		if page_idx == -1:
			gmGuiHelpers.gm_show_info (
				aMessage = _('You must select a page before you can delete it.'),
				aTitle = _('deleting page')
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
			_('deleting page')
		)
		if do_delete:
			try:
				os.remove(page_fname)
			except:
				_log.LogException('Error deleting file.')
				gmGuiHelpers.gm_show_error (
					aMessage = _('Cannot delete page in file [%s].\n\nYou may not have write access to it.') % page_fname,
					aTitle = _('deleting page')
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
		new_doc['date'] = self._PhWheel_doc_date.GetData().timestamp
		# - external reference
		ref = gmMedDoc.get_ext_ref()
		if ref is not None:
			new_doc['ext_ref'] = ref
		# - comment
		comment = self._TBOX_doc_comment.GetLineText(0).strip()
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
				workplace = gmPerson.gmCurrentProvider().get_workplace(),
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
		gmGuiHelpers.gm_beep_statustext(_('Successfully saved new document.'))
		return True
	#--------------------------------------------------------
	def _startover_btn_pressed(self, evt):
		self.__init_ui_data()
	#--------------------------------------------------------
	def _reviewed_box_checked(self, evt):
		self._ChBOX_abnormal.Enable(enable = self._ChBOX_reviewed.GetValue())
		self._ChBOX_relevant.Enable(enable = self._ChBOX_reviewed.GetValue())
#============================================================
class cSelectablySortedDocTreePnl(wxgSelectablySortedDocTreePnl.wxgSelectablySortedDocTreePnl, gmRegetMixin.cRegetOnPaintMixin):
	"""A document tree that can be sorted."""
	def __init__(self, *args, **kwds):
		wxgSelectablySortedDocTreePnl.wxgSelectablySortedDocTreePnl.__init__(self, *args, **kwds)
		gmRegetMixin.cRegetOnPaintMixin.__init__(self)
		self.__register_interests()
	#-------------------------------------------------------
	# reget mixin API
	#--------------------------------------------------------
	def __register_interests(self):
		gmDispatcher.connect(signal=gmSignals.post_patient_selection(), receiver=self._schedule_data_reget)
	#-------------------------------------------------------
	def _populate_with_data(self):
		"""Fills UI with data."""
		if not self._doc_tree.refresh():
			_log.Log(gmLog.lErr, "cannot update document tree")
			return False
		self._doc_tree.SelectItem(self._doc_tree.root)
		return True
	#--------------------------------------------------------
	# inherited event handlers
	#--------------------------------------------------------
	def _on_sort_by_age_selected(self, evt):
		self._doc_tree.set_sort_mode(mode = 'age')
		self._doc_tree.refresh()
		self._doc_tree.SetFocus()
		self._rbtn_sort_by_age.SetValue(True)
	#--------------------------------------------------------
	def _on_sort_by_review_selected(self, evt):
		self._doc_tree.set_sort_mode(mode = 'review')
		self._doc_tree.refresh()
		self._doc_tree.SetFocus()
		self._rbtn_sort_by_review.SetValue(True)
	#--------------------------------------------------------
	def _on_sort_by_episode_selected(self, evt):
		self._doc_tree.set_sort_mode(mode = 'episode')
		self._doc_tree.refresh()
		self._doc_tree.SetFocus()
		self._rbtn_sort_by_episode.SetValue(True)
	#--------------------------------------------------------
	def _on_sort_by_type_selected(self, evt):
		self._doc_tree.set_sort_mode(mode = 'type')
		self._doc_tree.refresh()
		self._doc_tree.SetFocus()
		self._rbtn_sort_by_type.SetValue(True)
#============================================================
class cDocTree(wx.TreeCtrl):
	"""This wx.TreeCtrl derivative displays a tree view of stored medical documents.
	"""
	_sort_modes = ['age', 'review', 'episode', 'type']
	_root_node_labels = None
	#--------------------------------------------------------
	def __init__(self, parent, id, *args, **kwds):
		"""Set up our specialised tree.
		"""
		kwds['style'] = wx.TR_NO_BUTTONS | wx.NO_BORDER
		wx.TreeCtrl.__init__(self, parent, id, *args, **kwds)

		tmp = _('available documents (%s)')
		cDocTree._root_node_labels = {
			'age': tmp % _('most recent on top'),
			'review': tmp % _('unreviewed on top'),
			'episode': tmp % _('sorted by episode'),
			'type': tmp % _('sorted by type')
		}

		self.root = None
		self.__sort_mode = None
		self.set_sort_mode()
		self.__pat = gmPerson.gmCurrentPatient()

		self.__register_events()
	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def refresh(self):
		if not self.__pat.is_connected():
			gmGuiHelpers.gm_beep_statustext (
				_('Cannot load documents. No active patient.'),
				gmLog.lErr
			)
			return False

		if not self.__populate_tree():
			return False

		return True
	#--------------------------------------------------------
	def set_sort_mode(self, mode='age'):
		if mode not in cDocTree._sort_modes:
			_log.Log(gmLog.Err, 'invalid document tree sort mode [%s], valid modes: %s' % (mode, cDocTree._sort_modes))
		if self.__sort_mode == mode:
			return True
		self.__sort_mode = mode
	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def __register_events(self):
		# connect handlers
		wx.EVT_TREE_ITEM_ACTIVATED (self, self.GetId(), self._on_activate)
		wx.EVT_TREE_ITEM_RIGHT_CLICK (self, self.GetId(), self.__on_right_click)

#		 wx.EVT_TREE_ITEM_EXPANDED	 (self, tID, self.OnItemExpanded)
#		 wx.EVT_TREE_ITEM_COLLAPSED (self, tID, self.OnItemCollapsed)
#		 wx.EVT_TREE_SEL_CHANGED	 (self, tID, self.OnSelChanged)
#		 wx.EVT_TREE_BEGIN_LABEL_EDIT(self, tID, self.OnBeginEdit)
#		 wx.EVT_TREE_END_LABEL_EDIT (self, tID, self.OnEndEdit)

#		 wx.EVT_LEFT_DCLICK(self.tree, self.OnLeftDClick)
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
		docs_folder = self.__pat.get_document_folder()
		docs = docs_folder.get_documents()
		if docs is None:
			name = self.__pat.get_identity().get_names()
			gmGuiHelpers.gm_show_error (
				aMessage = _('Error searching documents for patient\n[%s %s].') % (name['first'], name['last']),
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
			if doc['comment'] is not None:
				cmt = '%s' % doc['comment']
			else:
				cmt = _('no comment available')

			parts = doc.get_parts()
			page_num = len(parts)

			if doc['ext_ref'] is not None:
				ref = '>%s<' % doc['ext_ref']
			else:
				ref = _('no reference ID found')

			if doc.has_unreviewed_parts():
				review = '!'
			else:
				review = ''

			label = _('%s%7s %s: %s (%s page(s), %s)') % (
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

				pg = _('page %2s') % part['seq_idx']

				if part['obj_comment'] is None:
					cmt = _("no comment available")
				else:
					cmt = part['obj_comment']

				if part['size'] == 0:
					sz = _('0 bytes - data missing ?')
				else:
					sz = _('%s bytes') % part['size']

				if part['reviewed'] or part['reviewed_by_you'] or part['reviewed_by_intended_reviewer']:
					rev = ''
				else:
					rev = ' [%s]' % _('unreviewed')

#				if part['clinically_relevant']:
#					rel = ' [%s]' % _('Cave')
#				else:
#					rel = ''

				label = '%s%s: "%s" (%s)' % (pg, rev, cmt, sz)

				part_node = self.AppendItem(parent = doc_node, text = label)
				self.SetPyData(part_node, part)

		self.SortChildren(self.root)
		self.SelectItem(self.root)

		# and uncollapse
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

			# FIXME: should be "date" but have to wait until fuzzy date problem solved
			#date_field = 'date'
			date_field = 'modified_when'

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
	def _on_activate (self, event):
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
	# internal API
	#--------------------------------------------------------
	def __handle_doc_context(self):
		# build menu
		descriptions = self.__curr_node_data.get_descriptions()
		desc_menu = wx.Menu()
		for desc in descriptions:
			d_id = wx.NewId()
			# contract string
			tmp = re.split('\r\n+|\r+|\n+|\s+|\t+', desc)
			tmp = ' '.join(tmp)
			# but only use first 30 characters
			tmp = "%s ..." % tmp[:30]
			desc_menu.AppendItem(wx.MenuItem(desc_menu, d_id, tmp))
			# connect handler
			wx.EVT_MENU(desc_menu, d_id, self.__show_description)
		ID_load_submenu = wx.NewId()
		menu = wx.Menu(title = _('document menu'))
		# FIXME: add item "reorder pages"
		menu.AppendMenu(ID_load_submenu, _('descriptions ...'), desc_menu)
		# edit metadata
		ID = wx.NewId()
		menu.AppendItem(wx.MenuItem(menu, ID, _('Review/Edit properties')))
		wx.EVT_MENU(menu, ID, self.__review_curr_part)
		# show menu
		self.PopupMenu(menu, wx.DefaultPosition)
		menu.Destroy()
	#--------------------------------------------------------
	def __handle_part_context(self):
		# build menu
		menu = wx.Menu(title = _('page menu'))
		# display file
		ID = wx.NewId()
		menu.AppendItem(wx.MenuItem(menu, ID, _('Display page')))
		wx.EVT_MENU(menu, ID, self.__display_curr_part)
		# edit metadata
		ID = wx.NewId()
		menu.AppendItem(wx.MenuItem(menu, ID, _('Review/Edit properties')))
		wx.EVT_MENU(menu, ID, self.__review_curr_part)
		# show menu
		self.PopupMenu(menu, wx.DefaultPosition)
		menu.Destroy()
	#--------------------------------------------------------
	def __display_curr_part(self, evt):
		self.__display_part(part=self.__curr_node_data)
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

		# get export directory for temporary files
		def_tmp_dir = os.path.expanduser(os.path.join('~', 'gnumed', 'tmp'))
		if not os.path.isdir(def_tmp_dir):
			try:
				os.makedirs(def_tmp_dir)
			except:
				def_tmp_dir = None
		cfg = gmCfg.cCfgSQL()
		tmp_dir = cfg.get2 (
			option = "horstspace.tmp_dir",
			workplace = gmPerson.gmCurrentProvider().get_workplace(),
			bias = 'workplace',
			default = def_tmp_dir
		)
		exp_base = os.path.abspath(os.path.expanduser(os.path.join(tmp_dir, 'docs')))
		if not os.path.isdir(exp_base):
			_log.Log(gmLog.lWarn, "The directory [%s] does not exist ! Falling back to default temporary directory." % exp_base) # which is None == tempfile.tempdir == use system defaults
			exp_base = None
		else:
			_log.Log(gmLog.lData, "working into directory [%s]" % exp_base)

		# determine database export chunk size
		chunksize = int(cfg.get2 (
			option = "horstspace.blob_export_chunk_size",
			workplace = gmPerson.gmCurrentProvider().get_workplace(),
			bias = 'workplace',
			default = 1 * 1024 * 1024		# 1 MB
		))

		# retrieve doc part
		fname = part.export_to_file(aTempDir = exp_base, aChunkSize = chunksize)
		if fname is None:
			_log.Log(gmLog.lErr, "cannot export doc part [%s] data from database" % part['pk_obj'])
			gmGuiHelpers.gm_show_error (
				aMessage = _('Cannot export document part from database to file.'),
				aTitle = _('showing document')
			)
			return None

		# display it
		block_during_view = bool( cfg.get2 (
			option = 'horstspace.document_viewer.block_during_view',
			workplace = gmPerson.gmCurrentProvider().get_workplace(),
			bias = 'user',
			default = None
		))
		(result, msg) = gmMimeLib.call_viewer_on_file(fname, block=block_during_view)
		if not result:
			gmGuiHelpers.gm_show_error (
				aMessage = _('Cannot display document part:\n%s') % msg,
				aTitle = _('displaying page')
			)
			return None

		# handle review after display
		review_after_display = cfg.get2 (
			option = 'horstspace.document_viewer.review_after_display',
			workplace = gmPerson.gmCurrentProvider().get_workplace(),
			bias = 'user',
			default = 2
		)
		# always review
		if review_after_display == 1:
			self.__review_part(part=part)
		# review if no review by me exists
		elif review_after_display == 2:
			review_by_me = filter(lambda rev: rev['is_review_by_you'], part.get_reviews())
			if len(review_by_me) == 0:
				self.__review_part(part=part)

		return 1
	#--------------------------------------------------------
	def __review_curr_part(self, evt):
		if isinstance(self.__curr_node_data, gmMedDoc.cMedDocPart):
			self.__review_part(part=self.__curr_node_data)
		else:
			parts = self.__curr_node_data.get_parts()
			self.__review_part(part=parts[0])
	#--------------------------------------------------------
	def __review_part(self, part=None):
		dlg = cReviewDocPartDlg (
			parent = self,
			id = -1,
			part = part
		)
		if dlg.ShowModal() == wx.ID_OK:
			self.__populate_tree()
	#--------------------------------------------------------
	def __show_description(self, evt):
		print "showing description"
#============================================================
# main
#------------------------------------------------------------
if __name__ == '__main__':
	_log.SetAllLogLevels(gmLog.lData)

	print "==> the syntax seems OK"
	print "==> please write a real unit test"

#============================================================
# $Log: gmMedDocWidgets.py,v $
# Revision 1.97  2006-10-31 17:22:49  ncq
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
