# -*- coding: utf-8 -*-
"""GNUmed visual progress notes handling widgets."""
#================================================================
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL v2 or later (details at https://www.gnu.org)"

import sys
import logging
import os
import os.path
import shutil
import random
import threading


import wx
import wx.lib.agw.supertooltip as agw_stt
import wx.lib.statbmp as wx_genstatbmp


if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x

from Gnumed.pycommon import gmDispatcher
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmDateTime
from Gnumed.pycommon import gmShellAPI
from Gnumed.pycommon import gmCfgDB
from Gnumed.pycommon import gmMatchProvider
from Gnumed.pycommon import gmMimeLib
from Gnumed.pycommon import gmWorkerThread
from Gnumed.pycommon import gmPG2

from Gnumed.business import gmPerson
from Gnumed.business import gmPraxis
from Gnumed.business import gmForms
from Gnumed.business import gmDocuments
from Gnumed.business import gmEpisode

from Gnumed.wxpython import gmPhraseWheel
from Gnumed.wxpython import gmGuiHelpers
from Gnumed.wxpython import gmCfgWidgets
from Gnumed.wxpython import gmDocumentWidgets


_log = logging.getLogger('gm.ui')

#============================================================
# visual progress notes
#============================================================
def configure_visual_progress_note_editor():

	def is_valid(value):

		if value is None:
			gmDispatcher.send (
				signal = 'statustext',
				msg = _('You need to actually set an editor.'),
				beep = True
			)
			return False, value

		if value.strip() == '':
			gmDispatcher.send (
				signal = 'statustext',
				msg = _('You need to actually set an editor.'),
				beep = True
			)
			return False, value

		found, binary = gmShellAPI.detect_external_binary(value)
		if not found:
			gmDispatcher.send (
				signal = 'statustext',
				msg = _('The command [%s] is not found.') % value,
				beep = True
			)
			return True, value

		return True, binary

	#------------------------------------------
	cmd = gmCfgWidgets.configure_string_option (
		message = _(
			'Enter the shell command with which to start\n'
			'the image editor for visual progress notes.\n'
			'\n'
			'Any "%(img)s" included with the arguments\n'
			'will be replaced by the file name of the\n'
			'note template.'
		),
		option = 'external.tools.visual_soap_editor_cmd',
		bias = 'user',
		default_value = None,
		validator = is_valid
	)

	return cmd

#============================================================
def select_file_as_visual_progress_note_template(parent=None):
	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	dlg = wx.FileDialog (
		parent = parent,
		message = _('Choose file to use as template for new visual progress note'),
		defaultDir = os.path.expanduser('~'),
		defaultFile = '',
		#wildcard = "%s (*)|*|%s (*.*)|*.*" % (_('all files'), _('all files (Win)')),
		style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
	)
	result = dlg.ShowModal()

	if result == wx.ID_CANCEL:
		dlg.DestroyLater()
		return None

	full_filename = dlg.GetPath()
	dlg.Hide()
	dlg.DestroyLater()
	return full_filename

#------------------------------------------------------------
def select_visual_progress_note_template(parent=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	dlg = gmGuiHelpers.c3ButtonQuestionDlg (
		parent,
		-1,
		caption = _('Visual progress note source'),
		question = _('From which source do you want to pick the image template ?'),
		button_defs = [
			{'label': _('Database'), 'tooltip': _('List of templates in the database.'), 'default': True},
			{'label': _('File'), 'tooltip': _('Files in the filesystem.'), 'default': False},
			{'label': _('Device'), 'tooltip': _('Image capture devices (scanners, cameras, etc)'), 'default': False}
		]
	)
	result = dlg.ShowModal()
	dlg.DestroyLater()

	# 1) select from template
	if result == wx.ID_YES:
		_log.debug('visual progress note template from: database template')
		from Gnumed.wxpython import gmFormWidgets
		template = gmFormWidgets.manage_form_templates (
			parent = parent,
			template_types = [gmDocuments.DOCUMENT_TYPE_VISUAL_PROGRESS_NOTE],
			active_only = True
		)
		if template is None:
			return (None, None)
		filename = template.save_to_file()
		if filename is None:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot export visual progress note template for [%s].') % template['name_long'])
			return (None, None)
		return (filename, True)

	# 2) select from disk file
	if result == wx.ID_NO:
		_log.debug('visual progress note template from: disk file')
		fname = select_file_as_visual_progress_note_template(parent = parent)
		if fname is None:
			return (None, None)
		# create a copy of the picked file -- don't modify the original
		ext = os.path.splitext(fname)[1]
		tmp_name = gmTools.get_unique_filename(suffix = ext)
		_log.debug('visual progress note from file: [%s] -> [%s]', fname, tmp_name)
		shutil.copy2(fname, tmp_name)
		return (tmp_name, False)

	# 3) acquire from capture device
	if result == wx.ID_CANCEL:
		_log.debug('visual progress note template from: image capture device')
		fnames = gmDocumentWidgets.acquire_images_from_capture_device(device = None, calling_window = parent)
		if fnames is None:
			return (None, None)
		if len(fnames) == 0:
			return (None, None)
		return (fnames[0], False)

	_log.debug('no visual progress note template source selected')
	return (None, None)

#------------------------------------------------------------
def edit_visual_progress_note(filename=None, episode=None, discard_unmodified=False, doc_part=None, health_issue=None):
	"""This assumes <filename> contains an image which can be handled by the configured image editor."""

	if doc_part is not None:
		filename = doc_part.save_to_file()
		if filename is None:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot export visual progress note to file.'))
			return None

	editor = gmCfgDB.get4user (
		option = 'external.tools.visual_soap_editor_cmd',
		workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace
	)

	if editor is None:
		_log.error('no editor for visual progress notes configured, trying mimetype editor')
		gmDispatcher.send(signal = 'statustext', msg = _('Editor for visual progress note not configured.'), beep = False)
		mimetype = gmMimeLib.guess_mimetype(filename = filename)
		editor = gmMimeLib.get_editor_cmd(mimetype = mimetype, filename = filename)
		if editor is None:
			_log.error('no editor for mimetype <%s> configured, trying mimetype viewer', mimetype)
			success, msg = gmMimeLib.call_viewer_on_file(aFile = filename, block = True)
			if not success:
				_log.debug('problem running mimetype <%s> viewer', mimetype)
				gmGuiHelpers.gm_show_error (
					_(	'There is no editor for visual progress notes defined.\n'
						'Also, there is no editor command defined for the file type\n'
						'\n'
						' [%s].\n'
						'\n'
						'Therefor GNUmed attempted to at least *show* this\n'
						'visual progress note. That failed as well, however:\n'
						'\n'
						'%s'
					) % (mimetype, msg),
					_('Editing visual progress note')
				)
				editor = configure_visual_progress_note_editor()
				if editor is None:
					gmDispatcher.send(signal = 'statustext', msg = _('Editor for visual progress note not configured.'), beep = True)
					return None

	if '%(img)s' in editor:
		editor = editor % {'img': filename}
	else:
		editor = '%s %s' % (editor, filename)

	if discard_unmodified:
		original_stat = os.stat(filename)
		original_md5 = gmTools.file2md5(filename)

	success = gmShellAPI.run_command_in_shell(editor, blocking = True)
	if not success:
		success, msg = gmMimeLib.call_viewer_on_file(aFile = filename, block = True)
		if not success:
			_log.debug('problem running mimetype <%s> viewer', mimetype)
			gmGuiHelpers.gm_show_error (
				_(	'There was a problem running the editor\n'
					'\n'
					' [%s] (%s)\n'
					'\n'
					'on the visual progress note.\n'
					'\n'
					'Therefor GNUmed attempted to at least *show* it.\n'
					'That failed as well, however:\n'
					'\n'
					'%s'
				) % (editor, mimetype, msg),
				_('Editing visual progress note')
			)
			editor = configure_visual_progress_note_editor()
			if editor is None:
				gmDispatcher.send(signal = 'statustext', msg = _('Editor for visual progress note not configured.'), beep = True)
		return None

	try:
		open(filename, 'r').close()
	except Exception:
		_log.exception('problem accessing visual progress note file [%s]', filename)
		gmGuiHelpers.gm_show_error (
			_(	'There was a problem reading the visual\n'
				'progress note from the file:\n'
				'\n'
				' [%s]\n'
				'\n'
			) % filename,
			_('Saving visual progress note')
		)
		return None

	if discard_unmodified:
		modified_stat = os.stat(filename)
		# same size ?
		if original_stat.st_size == modified_stat.st_size:
			modified_md5 = gmTools.file2md5(filename)
			# same hash ?
			if original_md5 == modified_md5:
				_log.debug('visual progress note (template) not modified')
				# ask user to decide
				msg = _(
					'You either created a visual progress note from a template\n'
					'in the database (rather than from a file on disk) or you\n'
					'edited an existing visual progress note.\n'
					'\n'
					'The template/original was not modified at all, however.\n'
					'\n'
					'Do you still want to save the unmodified image as a\n'
					'visual progress note into the EMR of the patient ?\n'
				)
				save_unmodified = gmGuiHelpers.gm_show_question (
					msg,
					_('Saving visual progress note')
				)
				if not save_unmodified:
					_log.debug('user discarded unmodified note')
					return

	if doc_part is not None:
		_log.debug('updating visual progress note')
		doc_part.update_data_from_file(fname = filename)
		doc_part.set_reviewed(technically_abnormal = False, clinically_relevant = True)
		return None

	if not isinstance(episode, gmEpisode.cEpisode):
		if episode is None:
			episode = _('visual progress notes')
		pat = gmPerson.gmCurrentPatient()
		emr = pat.emr
		episode = emr.add_episode(episode_name = episode.strip(), pk_health_issue = health_issue, is_open = False)

	doc = gmDocumentWidgets.save_file_as_new_document (
		filename = filename,
		document_type = gmDocuments.DOCUMENT_TYPE_VISUAL_PROGRESS_NOTE,
		episode = episode,
		unlock_patient = False,
		pk_org_unit = gmPraxis.gmCurrentPraxisBranch()['pk_org_unit'],
		date_generated = gmDateTime.pydt_now_here()
	)
	doc.set_reviewed(technically_abnormal = False, clinically_relevant = True)

	return doc

#============================================================
class cVisualSoapTemplatePhraseWheel(gmPhraseWheel.cPhraseWheel):
	"""Phrasewheel to allow selection of visual SOAP template."""

	def __init__(self, *args, **kwargs):

		gmPhraseWheel.cPhraseWheel.__init__ (self, *args, **kwargs)

		query = """
SELECT
	pk AS data,
	name_short AS list_label,
	name_sort AS field_label
FROM
	ref.paperwork_templates
WHERE
	fk_template_type = (SELECT pk FROM ref.form_types WHERE name = '%s') AND (
		name_long %%(fragment_condition)s
			OR
		name_short %%(fragment_condition)s
	)
ORDER BY list_label
LIMIT 15
"""	% gmDocuments.DOCUMENT_TYPE_VISUAL_PROGRESS_NOTE

		mp = gmMatchProvider.cMatchProvider_SQL2(queries = [query])
		mp.setThresholds(2, 3, 5)

		self.matcher = mp
		self.selection_only = True
	#--------------------------------------------------------
	def _data2instance(self, link_obj=None):
		if self.GetData() is None:
			return None

		return gmForms.cFormTemplate(aPK_obj = self.GetData())

#============================================================
from Gnumed.wxGladeWidgets import wxgVisualSoapPresenterPnl

class cVisualSoapPresenterPnl(wxgVisualSoapPresenterPnl.wxgVisualSoapPresenterPnl):
	"""A panel displaying a number of images (visual progress note thumbnails)."""

	def __init__(self, *args, **kwargs):
		wxgVisualSoapPresenterPnl.wxgVisualSoapPresenterPnl.__init__(self, *args, **kwargs)
		self._SZR_soap = self.GetSizer()
		self.__bitmaps = []

	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def refresh(self, document_folder=None, episodes=None, encounter=None, do_async=False):
		if not self:
			# our C/C++ part may be dead already, due to async behaviour
			return

		if document_folder is None:
			self.clear()
			self.GetParent().Layout()
			return

		soap_docs = document_folder.get_visual_progress_notes(episodes = episodes, encounter = encounter)
		if len(soap_docs) == 0:
			self.clear()
			self.GetParent().Layout()
			return

		if not do_async:
			cookie, parts_list = self._worker__export_doc_parts(docs = soap_docs)
			self.__show_exported_parts(parts_list = parts_list)
			return

		self.__worker_cookie = '%sCookie-%s' % (self.__class__.__name__, random.random())
		_log.debug('starting worker thread, cookie: %s', self.__worker_cookie)
		gmWorkerThread.execute_in_worker_thread (
			payload_function = self._worker__export_doc_parts,
			payload_kwargs = {'docs': soap_docs, 'cookie': self.__worker_cookie},
			completion_callback = self._forwarder__show_exported_doc_parts,
			worker_name = self.__class__.__name__
		)

	#--------------------------------------------------------
	def clear(self):
		if self._SZR_soap:
			while len(self._SZR_soap.GetChildren()) > 0:
				self._SZR_soap.Detach(0)
		for bmp in self.__bitmaps:
			bmp.Unbind(wx.EVT_LEFT_UP)
			bmp.DestroyLater()
		self.__bitmaps = []

	#--------------------------------------------------------
	# event handlers
	#--------------------------------------------------------
	def _on_bitmap_leftclicked(self, evt):
		wx.CallAfter (
			edit_visual_progress_note,
			doc_part = evt.GetEventObject().doc_part,
			discard_unmodified = True
		)

	#--------------------------------------------------------
	# internal API
	#--------------------------------------------------------
	def _worker__export_doc_parts(self, docs=None, cookie=None):
		# this is used as the worker thread payload
		_log.debug('cookie [%s]', cookie)
		conn = gmPG2.get_connection(readonly = True, connection_name = threading.current_thread().name, pooled = False)
		parts_list = []
		for soap_doc in docs:
			parts = soap_doc.parts
			if len(parts) == 0:
				continue
			parts_counter = ''
			if len(parts) > 1:
				parts_counter = _(' [part 1 of %s]') % len(parts)
			part = parts[0]
			fname = part.save_to_file(conn = conn)
			if fname is None:
				continue
			tt_header = _('Created: %s%s') % (part['date_generated'].strftime('%Y %b %d'), parts_counter)
			tt_footer = gmTools.coalesce(part['doc_comment'], '').strip()
			parts_list.append([fname, part, tt_header, tt_footer])
		conn.close()
		_log.debug('worker finished')
		return (cookie, parts_list)

	#--------------------------------------------------------
	def _forwarder__show_exported_doc_parts(self, worker_result):
		# this is the worker thread completion callback
		cookie, parts_list = worker_result
		# worker still the one we are interested in ?
		if cookie != self.__worker_cookie:
			_log.debug('received results from old worker [%s], I am [%s], ignoring', cookie, self.__worker_cookie)
			return
		if len(parts_list) == 0:
			return
		wx.CallAfter(self.__show_exported_parts, parts_list = parts_list)

	#--------------------------------------------------------
	def __show_exported_parts(self, parts_list=None):
		self.clear()
		for part_def in parts_list:
			fname, part, tt_header, tt_footer = part_def
			#_log.debug(tt_header)
			#_log.debug(tt_footer)
			img = gmGuiHelpers.file2scaled_image (
				filename = fname,
				height = 30
			)
			bmp = wx_genstatbmp.GenStaticBitmap(self, -1, img, style = wx.NO_BORDER)
			bmp.doc_part = part
			img = gmGuiHelpers.file2scaled_image (
				filename = fname,
				height = 150
			)
			tip = agw_stt.SuperToolTip (
				'',
				bodyImage = img,
				header = tt_header,
				footer = tt_footer
			)
			tip.SetTopGradientColor('white')
			tip.SetMiddleGradientColor('white')
			tip.SetBottomGradientColor('white')
			tip.SetTarget(bmp)
			bmp.Bind(wx.EVT_LEFT_UP, self._on_bitmap_leftclicked)
			# FIXME: add context menu for Delete/Clone/Add/Configure
			self._SZR_soap.Add(bmp, 0, wx.LEFT | wx.RIGHT | wx.TOP | wx.BOTTOM | wx.EXPAND, 3)
			self.__bitmaps.append(bmp)
		self.GetParent().Layout()

#============================================================
# main
#------------------------------------------------------------
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	#----------------------------------------
