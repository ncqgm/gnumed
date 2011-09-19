"""Widgets dealing with patient demographics."""
#============================================================
__version__ = "$Revision: 1.175 $"
__author__ = "R.Terry, SJ Tan, I Haywood, Carlos Moro <cfmoro1976@yahoo.es>"
__license__ = 'GPL v2 or later (details at http://www.gnu.org)'

# standard library
import sys
import sys
import codecs
import re as regex
import logging
import webbrowser
import os


import wx
import wx.wizard
import wx.lib.imagebrowser as wx_imagebrowser
import wx.lib.statbmp as wx_genstatbmp


# GNUmed specific
if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmDispatcher
from Gnumed.pycommon import gmI18N
from Gnumed.pycommon import gmMatchProvider
from Gnumed.pycommon import gmPG2
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmCfg
from Gnumed.pycommon import gmDateTime
from Gnumed.pycommon import gmShellAPI

from Gnumed.business import gmDemographicRecord
from Gnumed.business import gmPersonSearch
from Gnumed.business import gmSurgery
from Gnumed.business import gmPerson

from Gnumed.wxpython import gmPhraseWheel
from Gnumed.wxpython import gmRegetMixin
from Gnumed.wxpython import gmAuthWidgets
from Gnumed.wxpython import gmPersonContactWidgets
from Gnumed.wxpython import gmEditArea
from Gnumed.wxpython import gmListWidgets
from Gnumed.wxpython import gmDateTimeInput
from Gnumed.wxpython import gmDataMiningWidgets
from Gnumed.wxpython import gmGuiHelpers


# constant defs
_log = logging.getLogger('gm.ui')


try:
	_('dummy-no-need-to-translate-but-make-epydoc-happy')
except NameError:
	_ = lambda x:x

#============================================================
# image tags related widgets
#------------------------------------------------------------
def edit_tag_image(parent=None, tag_image=None, single_entry=False):
	if tag_image is not None:
		if tag_image['is_in_use']:
			gmGuiHelpers.gm_show_info (
				aTitle = _('Editing tag'),
				aMessage = _(
					'Cannot edit the image tag\n'
					'\n'
					' "%s"\n'
					'\n'
					'because it is currently in use.\n'
				) % tag_image['l10n_description']
			)
			return False

	ea = cTagImageEAPnl(parent = parent, id = -1)
	ea.data = tag_image
	ea.mode = gmTools.coalesce(tag_image, 'new', 'edit')
	dlg = gmEditArea.cGenericEditAreaDlg2(parent = parent, id = -1, edit_area = ea, single_entry = single_entry)
	dlg.SetTitle(gmTools.coalesce(tag_image, _('Adding new tag'), _('Editing tag')))
	if dlg.ShowModal() == wx.ID_OK:
		dlg.Destroy()
		return True
	dlg.Destroy()
	return False
#------------------------------------------------------------
def manage_tag_images(parent=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()
	#------------------------------------------------------------
	def go_to_openclipart_org(tag_image):
		webbrowser.open (
			url = u'http://www.openclipart.org',
			new = False,
			autoraise = True
		)
		webbrowser.open (
			url = u'http://www.google.com',
			new = False,
			autoraise = True
		)
		return True
	#------------------------------------------------------------
	def edit(tag_image=None):
		return edit_tag_image(parent = parent, tag_image = tag_image, single_entry = (tag_image is not None))
	#------------------------------------------------------------
	def delete(tag):
		if tag['is_in_use']:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot delete this tag. It is in use.'), beep = True)
			return False

		return gmDemographicRecord.delete_tag_image(tag_image = tag['pk_tag_image'])
	#------------------------------------------------------------
	def refresh(lctrl):
		tags = gmDemographicRecord.get_tag_images(order_by = u'l10n_description')
		items = [ [
			t['l10n_description'],
			gmTools.bool2subst(t['is_in_use'], u'X', u''),
			u'%s' % t['size'],
			t['pk_tag_image']
		] for t in tags ]
		lctrl.set_string_items(items)
		lctrl.set_column_widths(widths = [wx.LIST_AUTOSIZE, wx.LIST_AUTOSIZE_USEHEADER, wx.LIST_AUTOSIZE_USEHEADER, wx.LIST_AUTOSIZE])
		lctrl.set_data(tags)
	#------------------------------------------------------------
	msg = _('\nTags with images registered with GNUmed.\n')

	tag = gmListWidgets.get_choices_from_list (
		parent = parent,
		msg = msg,
		caption = _('Showing tags with images.'),
		columns = [_('Tag name'), _('In use'), _('Image size'), u'#'],
		single_selection = True,
		new_callback = edit,
		edit_callback = edit,
		delete_callback = delete,
		refresh_callback = refresh,
		left_extra_button = (_('WWW'), _('Go to www.openclipart.org for images.'), go_to_openclipart_org)
	)

	return tag
#------------------------------------------------------------
from Gnumed.wxGladeWidgets import wxgTagImageEAPnl

class cTagImageEAPnl(wxgTagImageEAPnl.wxgTagImageEAPnl, gmEditArea.cGenericEditAreaMixin):

	def __init__(self, *args, **kwargs):

		try:
			data = kwargs['tag_image']
			del kwargs['tag_image']
		except KeyError:
			data = None

		wxgTagImageEAPnl.wxgTagImageEAPnl.__init__(self, *args, **kwargs)
		gmEditArea.cGenericEditAreaMixin.__init__(self)

		self.mode = 'new'
		self.data = data
		if data is not None:
			self.mode = 'edit'

		self.__selected_image_file = None
	#----------------------------------------------------------------
	# generic Edit Area mixin API
	#----------------------------------------------------------------
	def _valid_for_save(self):

		valid = True

		if self.mode == u'new':
			if self.__selected_image_file is None:
				valid = False
				gmDispatcher.send(signal = 'statustext', msg = _('Must pick an image file for a new tag.'), beep = True)
				self._BTN_pick_image.SetFocus()

		if self.__selected_image_file is not None:
			try:
				open(self.__selected_image_file).close()
			except StandardError:
				valid = False
				self.__selected_image_file = None
				gmDispatcher.send(signal = 'statustext', msg = _('Cannot open the image file [%s].') % self.__selected_image_file, beep = True)
				self._BTN_pick_image.SetFocus()

		if self._TCTRL_description.GetValue().strip() == u'':
			valid = False
			self.display_tctrl_as_valid(self._TCTRL_description, False)
			self._TCTRL_description.SetFocus()
		else:
			self.display_tctrl_as_valid(self._TCTRL_description, True)

		return (valid is True)
	#----------------------------------------------------------------
	def _save_as_new(self):

		dbo_conn = gmAuthWidgets.get_dbowner_connection(procedure = _('Creating tag with image'))
		if dbo_conn is None:
			return False

		data = gmDemographicRecord.create_tag_image(description = self._TCTRL_description.GetValue().strip(), link_obj = dbo_conn)
		dbo_conn.close()

		data['filename'] = self._TCTRL_filename.GetValue().strip()
		data.save()
		data.update_image_from_file(filename = self.__selected_image_file)

		# must be done very late or else the property access
		# will refresh the display such that later field
		# access will return empty values
		self.data = data
		return True
	#----------------------------------------------------------------
	def _save_as_update(self):

		# this is somewhat fake as it never actually uses the gm-dbo conn
		# (although it does verify it)
		dbo_conn = gmAuthWidgets.get_dbowner_connection(procedure = _('Updating tag with image'))
		if dbo_conn is None:
			return False
		dbo_conn.close()

		self.data['description'] = self._TCTRL_description.GetValue().strip()
		self.data['filename'] = self._TCTRL_filename.GetValue().strip()
		self.data.save()

		if self.__selected_image_file is not None:
			open(self.__selected_image_file).close()
			self.data.update_image_from_file(filename = self.__selected_image_file)
			self.__selected_image_file = None

		return True
	#----------------------------------------------------------------
	def _refresh_as_new(self):
		self._TCTRL_description.SetValue(u'')
		self._TCTRL_filename.SetValue(u'')
		self._BMP_image.SetBitmap(bitmap = wx.EmptyBitmap(100, 100))

		self.__selected_image_file = None

		self._TCTRL_description.SetFocus()
	#----------------------------------------------------------------
	def _refresh_as_new_from_existing(self):
		self._refresh_as_new()
	#----------------------------------------------------------------
	def _refresh_from_existing(self):
		self._TCTRL_description.SetValue(self.data['l10n_description'])
		self._TCTRL_filename.SetValue(gmTools.coalesce(self.data['filename'], u''))
		fname = self.data.export_image2file()
		if fname is None:
			self._BMP_image.SetBitmap(bitmap = wx.EmptyBitmap(100, 100))
		else:
			self._BMP_image.SetBitmap(bitmap = gmGuiHelpers.file2scaled_image(filename = fname, height = 100))

		self.__selected_image_file = None

		self._TCTRL_description.SetFocus()
	#----------------------------------------------------------------
	# event handlers
	#----------------------------------------------------------------
	def _on_pick_image_button_pressed(self, event):
		paths = gmTools.gmPaths()
		img_dlg = wx_imagebrowser.ImageDialog(parent = self, set_dir = paths.home_dir)
		img_dlg.Centre()
		if img_dlg.ShowModal() != wx.ID_OK:
			return

		self.__selected_image_file = img_dlg.GetFile()
		self._BMP_image.SetBitmap(bitmap = gmGuiHelpers.file2scaled_image(filename = self.__selected_image_file, height = 100))
		fdir, fname = os.path.split(self.__selected_image_file)
		self._TCTRL_filename.SetValue(fname)

#============================================================
from Gnumed.wxGladeWidgets import wxgVisualSoapPresenterPnl

class cImageTagPresenterPnl(wxgVisualSoapPresenterPnl.wxgVisualSoapPresenterPnl):

	def __init__(self, *args, **kwargs):
		wxgVisualSoapPresenterPnl.wxgVisualSoapPresenterPnl.__init__(self, *args, **kwargs)
		self._SZR_bitmaps = self.GetSizer()
		self.__bitmaps = []

		self.__context_popup = wx.Menu()

		item = self.__context_popup.Append(-1, _('&Edit comment'))
		self.Bind(wx.EVT_MENU, self.__edit_tag, item)

		item = self.__context_popup.Append(-1, _('&Remove tag'))
		self.Bind(wx.EVT_MENU, self.__remove_tag, item)
	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def refresh(self, patient):

		self.clear()

		for tag in patient.get_tags(order_by = u'l10n_description'):
			fname = tag.export_image2file()
			if fname is None:
				_log.warning('cannot export image data of tag [%s]', tag['l10n_description'])
				continue
			img = gmGuiHelpers.file2scaled_image(filename = fname, height = 20)
			bmp = wx_genstatbmp.GenStaticBitmap(self, -1, img, style = wx.NO_BORDER)
			bmp.SetToolTipString(u'%s%s' % (
				tag['l10n_description'],
				gmTools.coalesce(tag['comment'], u'', u'\n\n%s')
			))
			bmp.tag = tag
			bmp.Bind(wx.EVT_RIGHT_UP, self._on_bitmap_rightclicked)
			# FIXME: add context menu for Delete/Clone/Add/Configure
			self._SZR_bitmaps.Add(bmp, 0, wx.LEFT | wx.RIGHT | wx.TOP | wx.BOTTOM, 1)		# | wx.EXPAND
			self.__bitmaps.append(bmp)

		self.GetParent().Layout()
	#--------------------------------------------------------
	def clear(self):
		for child_idx in range(len(self._SZR_bitmaps.GetChildren())):
			self._SZR_bitmaps.Detach(child_idx)
		for bmp in self.__bitmaps:
			bmp.Destroy()
		self.__bitmaps = []
	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def __remove_tag(self, evt):
		if self.__current_tag is None:
			return
		pat = gmPerson.gmCurrentPatient()
		if not pat.connected:
			return
		pat.remove_tag(tag = self.__current_tag['pk_identity_tag'])
	#--------------------------------------------------------
	def __edit_tag(self, evt):
		if self.__current_tag is None:
			return

		msg = _('Edit the comment on tag [%s]') % self.__current_tag['l10n_description']
		comment = wx.GetTextFromUser (
			message = msg,
			caption = _('Editing tag comment'),
			default_value = gmTools.coalesce(self.__current_tag['comment'], u''),
			parent = self
		)

		if comment == u'':
			return

		if comment.strip() == self.__current_tag['comment']:
			return

		if comment == u' ':
			self.__current_tag['comment'] = None
		else:
			self.__current_tag['comment'] = comment.strip()

		self.__current_tag.save()
	#--------------------------------------------------------
	# event handlers
	#--------------------------------------------------------
	def _on_bitmap_rightclicked(self, evt):
		self.__current_tag = evt.GetEventObject().tag
		self.PopupMenu(self.__context_popup, pos = wx.DefaultPosition)
		self.__current_tag = None
#============================================================
#============================================================
class cKOrganizerSchedulePnl(gmDataMiningWidgets.cPatientListingPnl):

	def __init__(self, *args, **kwargs):

		kwargs['message'] = _("Today's KOrganizer appointments ...")
		kwargs['button_defs'] = [
			{'label': _('Reload'), 'tooltip': _('Reload appointments from KOrganizer')},
			{'label': u''},
			{'label': u''},
			{'label': u''},
			{'label': u'KOrganizer', 'tooltip': _('Launch KOrganizer')}
		]
		gmDataMiningWidgets.cPatientListingPnl.__init__(self, *args, **kwargs)

		self.fname = os.path.expanduser(os.path.join('~', '.gnumed', 'tmp', 'korganizer2gnumed.csv'))
		self.reload_cmd = 'konsolekalendar --view --export-type csv --export-file %s' % self.fname

	#--------------------------------------------------------
	def _on_BTN_1_pressed(self, event):
		"""Reload appointments from KOrganizer."""
		self.reload_appointments()
	#--------------------------------------------------------
	def _on_BTN_5_pressed(self, event):
		"""Reload appointments from KOrganizer."""
		found, cmd = gmShellAPI.detect_external_binary(binary = 'korganizer')

		if not found:
			gmDispatcher.send(signal = 'statustext', msg = _('KOrganizer is not installed.'), beep = True)
			return

		gmShellAPI.run_command_in_shell(command = cmd, blocking = False)
	#--------------------------------------------------------
	def reload_appointments(self):
		try: os.remove(self.fname)
		except OSError: pass
		gmShellAPI.run_command_in_shell(command=self.reload_cmd, blocking=True)
		try:
			csv_file = codecs.open(self.fname , mode = 'rU', encoding = 'utf8', errors = 'replace')
		except IOError:
			gmDispatcher.send(signal = u'statustext', msg = _('Cannot access KOrganizer transfer file [%s]') % self.fname, beep = True)
			return

		csv_lines = gmTools.unicode_csv_reader (
			csv_file,
			delimiter = ','
		)
		# start_date, start_time, end_date, end_time, title (patient), ort, comment, UID
		self._LCTRL_items.set_columns ([
			_('Place'),
			_('Start'),
			u'',
			u'',
			_('Patient'),
			_('Comment')
		])
		items = []
		data = []
		for line in csv_lines:
			items.append([line[5], line[0], line[1], line[3], line[4], line[6]])
			data.append([line[4], line[7]])

		self._LCTRL_items.set_string_items(items = items)
		self._LCTRL_items.set_column_widths()
		self._LCTRL_items.set_data(data = data)
		self._LCTRL_items.patient_key = 0
	#--------------------------------------------------------
	# notebook plugins API
	#--------------------------------------------------------
	def repopulate_ui(self):
		self.reload_appointments()
#============================================================
# occupation related widgets / functions
#============================================================
def edit_occupation():

	pat = gmPerson.gmCurrentPatient()
	curr_jobs = pat.get_occupations()
	if len(curr_jobs) > 0:
		old_job = curr_jobs[0]['l10n_occupation']
		update = curr_jobs[0]['modified_when'].strftime('%m/%Y')
	else:
		old_job = u''
		update = u''

	msg = _(
		'Please enter the primary occupation of the patient.\n'
		'\n'
		'Currently recorded:\n'
		'\n'
		' %s (last updated %s)'
	) % (old_job, update)

	new_job = wx.GetTextFromUser (
		message = msg,
		caption = _('Editing primary occupation'),
		default_value = old_job,
		parent = None
	)
	if new_job.strip() == u'':
		return

	for job in curr_jobs:
		# unlink all but the new job
		if job['l10n_occupation'] != new_job:
			pat.unlink_occupation(occupation = job['l10n_occupation'])
	# and link the new one
	pat.link_occupation(occupation = new_job)

#------------------------------------------------------------
class cOccupationPhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):
		query = u"SELECT distinct name, _(name) from dem.occupation where _(name) %(fragment_condition)s"
		mp = gmMatchProvider.cMatchProvider_SQL2(queries=query)
		mp.setThresholds(1, 3, 5)
		gmPhraseWheel.cPhraseWheel.__init__ (
			self,
			*args,
			**kwargs
		)
		self.SetToolTipString(_("Type or select an occupation."))
		self.capitalisation_mode = gmTools.CAPS_FIRST
		self.matcher = mp

#============================================================
# identity widgets / functions
#============================================================
def disable_identity(identity=None):
	# ask user for assurance
	go_ahead = gmGuiHelpers.gm_show_question (
		_('Are you sure you really, positively want\n'
		  'to disable the following person ?\n'
		  '\n'
		  ' %s %s %s\n'
		  ' born %s\n'
		  '\n'
		  '%s\n'
		) % (
			identity['firstnames'],
			identity['lastnames'],
			identity['gender'],
			identity['dob'],
			gmTools.bool2subst (
				identity.is_patient,
				_('This patient DID receive care.'),
				_('This person did NOT receive care.')
			)
		),
		_('Disabling person')
	)
	if not go_ahead:
		return True

	# get admin connection
	conn = gmAuthWidgets.get_dbowner_connection (
		procedure = _('Disabling patient')
	)
	# - user cancelled
	if conn is False:
		return True
	# - error
	if conn is None:
		return False

	# now disable patient
	gmPG2.run_rw_queries(queries = [{'cmd': u"update dem.identity set deleted=True where pk=%s", 'args': [identity['pk_identity']]}])

	return True

#------------------------------------------------------------
# phrasewheels
#------------------------------------------------------------
class cLastnamePhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):
		query = u"SELECT distinct lastnames, lastnames from dem.names where lastnames %(fragment_condition)s order by lastnames limit 25"
		mp = gmMatchProvider.cMatchProvider_SQL2(queries=query)
		mp.setThresholds(3, 5, 9)
		gmPhraseWheel.cPhraseWheel.__init__ (
			self,
			*args,
			**kwargs
		)
		self.SetToolTipString(_("Type or select a last name (family name/surname)."))
		self.capitalisation_mode = gmTools.CAPS_NAMES
		self.matcher = mp
#------------------------------------------------------------
class cFirstnamePhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):
		query = u"""
			(SELECT distinct firstnames, firstnames from dem.names where firstnames %(fragment_condition)s order by firstnames limit 20)
				union
			(SELECT distinct name, name from dem.name_gender_map where name %(fragment_condition)s order by name limit 20)"""
		mp = gmMatchProvider.cMatchProvider_SQL2(queries=query)
		mp.setThresholds(3, 5, 9)
		gmPhraseWheel.cPhraseWheel.__init__ (
			self,
			*args,
			**kwargs
		)
		self.SetToolTipString(_("Type or select a first name (forename/Christian name/given name)."))
		self.capitalisation_mode = gmTools.CAPS_NAMES
		self.matcher = mp
#------------------------------------------------------------
class cNicknamePhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):
		query = u"""
			(SELECT distinct preferred, preferred from dem.names where preferred %(fragment_condition)s order by preferred limit 20)
				union
			(SELECT distinct firstnames, firstnames from dem.names where firstnames %(fragment_condition)s order by firstnames limit 20)
				union
			(SELECT distinct name, name from dem.name_gender_map where name %(fragment_condition)s order by name limit 20)"""
		mp = gmMatchProvider.cMatchProvider_SQL2(queries=query)
		mp.setThresholds(3, 5, 9)
		gmPhraseWheel.cPhraseWheel.__init__ (
			self,
			*args,
			**kwargs
		)
		self.SetToolTipString(_("Type or select an alias (nick name, preferred name, call name, warrior name, artist name)."))
		# nicknames CAN start with lower case !
		#self.capitalisation_mode = gmTools.CAPS_NAMES
		self.matcher = mp
#------------------------------------------------------------
class cTitlePhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):
		query = u"SELECT distinct title, title from dem.identity where title %(fragment_condition)s"
		mp = gmMatchProvider.cMatchProvider_SQL2(queries=query)
		mp.setThresholds(1, 3, 9)
		gmPhraseWheel.cPhraseWheel.__init__ (
			self,
			*args,
			**kwargs
		)
		self.SetToolTipString(_("Type or select a title. Note that the title applies to the person, not to a particular name !"))
		self.matcher = mp
#------------------------------------------------------------
class cGenderSelectionPhraseWheel(gmPhraseWheel.cPhraseWheel):
	"""Let user select a gender."""

	_gender_map = None

	def __init__(self, *args, **kwargs):

		if cGenderSelectionPhraseWheel._gender_map is None:
			cmd = u"""
				SELECT tag, l10n_label, sort_weight
				from dem.v_gender_labels
				order by sort_weight desc"""
			rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd}], get_col_idx=True)
			cGenderSelectionPhraseWheel._gender_map = {}
			for gender in rows:
				cGenderSelectionPhraseWheel._gender_map[gender[idx['tag']]] = {
					'data': gender[idx['tag']],
					'field_label': gender[idx['l10n_label']],
					'list_label': gender[idx['l10n_label']],
					'weight': gender[idx['sort_weight']]
				}

		mp = gmMatchProvider.cMatchProvider_FixedList(aSeq = cGenderSelectionPhraseWheel._gender_map.values())
		mp.setThresholds(1, 1, 3)

		gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)
		self.selection_only = True
		self.matcher = mp
		self.picklist_delay = 50
#------------------------------------------------------------
class cExternalIDTypePhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):
		query = u"""
			SELECT DISTINCT ON (list_label)
				pk AS data,
				name AS field_label,
				name || coalesce(' (' || issuer || ')', '') as list_label
			FROM dem.enum_ext_id_types
			WHERE name %(fragment_condition)s
			ORDER BY list_label
			LIMIT 25
		"""
		mp = gmMatchProvider.cMatchProvider_SQL2(queries=query)
		mp.setThresholds(1, 3, 5)
		gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)
		self.SetToolTipString(_("Enter or select a type for the external ID."))
		self.matcher = mp
	#--------------------------------------------------------
	def _get_data_tooltip(self):
		if self.GetData() is None:
			return None
		return self._data.values()[0]['list_label']
#------------------------------------------------------------
class cExternalIDIssuerPhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):
		query = u"""
SELECT distinct issuer, issuer
from dem.enum_ext_id_types
where issuer %(fragment_condition)s
order by issuer limit 25"""
		mp = gmMatchProvider.cMatchProvider_SQL2(queries=query)
		mp.setThresholds(1, 3, 5)
		gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)
		self.SetToolTipString(_("Type or select an ID issuer."))
		self.capitalisation_mode = gmTools.CAPS_FIRST
		self.matcher = mp
#------------------------------------------------------------
# edit areas
#------------------------------------------------------------
from Gnumed.wxGladeWidgets import wxgExternalIDEditAreaPnl

class cExternalIDEditAreaPnl(wxgExternalIDEditAreaPnl.wxgExternalIDEditAreaPnl, gmEditArea.cGenericEditAreaMixin):
	"""An edit area for editing/creating external IDs.

	Does NOT act on/listen to the current patient.
	"""
	def __init__(self, *args, **kwargs):

		try:
			data = kwargs['external_id']
			del kwargs['external_id']
		except:
			data = None

		wxgExternalIDEditAreaPnl.wxgExternalIDEditAreaPnl.__init__(self, *args, **kwargs)
		gmEditArea.cGenericEditAreaMixin.__init__(self)

		self.identity = None

		self.mode = 'new'
		self.data = data
		if data is not None:
			self.mode = 'edit'

		self.__init_ui()
	#--------------------------------------------------------
	def __init_ui(self):
		self._PRW_type.add_callback_on_lose_focus(self._on_type_set)
	#----------------------------------------------------------------
	# generic Edit Area mixin API
	#----------------------------------------------------------------
	def _valid_for_save(self):
		validity = True

		# do not test .GetData() because adding external
		# IDs will create types as necessary
		#if self._PRW_type.GetData() is None:
		if self._PRW_type.GetValue().strip() == u'':
			validity = False
			self._PRW_type.display_as_valid(False)
			self._PRW_type.SetFocus()
		else:
			self._PRW_type.display_as_valid(True)

		if self._TCTRL_value.GetValue().strip() == u'':
			validity = False
			self.display_tctrl_as_valid(tctrl = self._TCTRL_value, valid = False)
		else:
			self.display_tctrl_as_valid(tctrl = self._TCTRL_value, valid = True)

		return validity
	#----------------------------------------------------------------
	def _save_as_new(self):
		data = {}
		data['pk_type'] = None
		data['name'] = self._PRW_type.GetValue().strip()
		data['value'] = self._TCTRL_value.GetValue().strip()
		data['issuer'] = gmTools.none_if(self._PRW_issuer.GetValue().strip(), u'')
		data['comment'] = gmTools.none_if(self._TCTRL_comment.GetValue().strip(), u'')

		self.identity.add_external_id (
			type_name = data['name'],
			value = data['value'],
			issuer = data['issuer'],
			comment = data['comment']
		)

		self.data = data
		return True
	#----------------------------------------------------------------
	def _save_as_update(self):
		self.data['name'] = self._PRW_type.GetValue().strip()
		self.data['value'] = self._TCTRL_value.GetValue().strip()
		self.data['issuer'] = gmTools.none_if(self._PRW_issuer.GetValue().strip(), u'')
		self.data['comment'] = gmTools.none_if(self._TCTRL_comment.GetValue().strip(), u'')

		self.identity.update_external_id (
			pk_id = self.data['pk_id'],
			type = self.data['name'],
			value = self.data['value'],
			issuer = self.data['issuer'],
			comment = self.data['comment']
		)

		return True
	#----------------------------------------------------------------
	def _refresh_as_new(self):
		self._PRW_type.SetText(value = u'', data = None)
		self._TCTRL_value.SetValue(u'')
		self._PRW_issuer.SetText(value = u'', data = None)
		self._TCTRL_comment.SetValue(u'')
	#----------------------------------------------------------------
	def _refresh_as_new_from_existing(self):
		self._refresh_as_new()
		self._PRW_issuer.SetText(self.data['issuer'])
	#----------------------------------------------------------------
	def _refresh_from_existing(self):
		self._PRW_type.SetText(value = self.data['name'], data = self.data['pk_type'])
		self._TCTRL_value.SetValue(self.data['value'])
		self._PRW_issuer.SetText(self.data['issuer'])
		self._TCTRL_comment.SetValue(gmTools.coalesce(self.data['comment'], u''))
	#----------------------------------------------------------------
	# internal helpers
	#----------------------------------------------------------------
	def _on_type_set(self):
		"""Set the issuer according to the selected type.

		Matches are fetched from existing records in backend.
		"""
		pk_curr_type = self._PRW_type.GetData()
		if pk_curr_type is None:
			return True
		rows, idx = gmPG2.run_ro_queries(queries = [{
			'cmd': u"SELECT issuer from dem.enum_ext_id_types where pk = %s",
			'args': [pk_curr_type]
		}])
		if len(rows) == 0:
			return True
		wx.CallAfter(self._PRW_issuer.SetText, rows[0][0])
		return True

#============================================================
# identity widgets
#------------------------------------------------------------
def _empty_dob_allowed():
	allow_empty_dob = gmGuiHelpers.gm_show_question (
		_(
			'Are you sure you want to leave this person\n'
			'without a valid date of birth ?\n'
			'\n'
			'This can be useful for temporary staff members\n'
			'but will provoke nag screens if this person\n'
			'becomes a patient.\n'
		),
		_('Validating date of birth')
	)
	return allow_empty_dob
#------------------------------------------------------------
def _validate_dob_field(dob_prw):

	# valid timestamp ?
	if dob_prw.is_valid_timestamp(allow_empty = False):			# properly colors the field
		dob = dob_prw.date
		# but year also usable ?
		if (dob.year > 1899) and (dob < gmDateTime.pydt_now_here()):
			return True

		if dob.year < 1900:
			msg = _(
				'DOB: %s\n'
				'\n'
				'While this is a valid point in time Python does\n'
				'not know how to deal with it.\n'
				'\n'
				'We suggest using January 1st 1901 instead and adding\n'
				'the true date of birth to the patient comment.\n'
				'\n'
				'Sorry for the inconvenience %s'
			) % (dob, gmTools.u_frowning_face)
		else:
			msg = _(
				'DOB: %s\n'
				'\n'
				'Date of birth in the future !'
			) % dob
		gmGuiHelpers.gm_show_error (
			msg,
			_('Validating date of birth')
		)
		dob_prw.display_as_valid(False)
		dob_prw.SetFocus()
		return False

	# invalid timestamp but not empty
	if dob_prw.GetValue().strip() != u'':
		dob_prw.display_as_valid(False)
		gmDispatcher.send(signal = u'statustext', msg = _('Invalid date of birth.'))
		dob_prw.SetFocus()
		return False

	# empty DOB field
	dob_prw.display_as_valid(False)
	return True
#------------------------------------------------------------
from Gnumed.wxGladeWidgets import wxgIdentityEAPnl

class cIdentityEAPnl(wxgIdentityEAPnl.wxgIdentityEAPnl, gmEditArea.cGenericEditAreaMixin):
	"""An edit area for editing/creating title/gender/dob/dod etc."""

	def __init__(self, *args, **kwargs):

		try:
			data = kwargs['identity']
			del kwargs['identity']
		except KeyError:
			data = None

		wxgIdentityEAPnl.wxgIdentityEAPnl.__init__(self, *args, **kwargs)
		gmEditArea.cGenericEditAreaMixin.__init__(self)

		self.mode = 'new'
		self.data = data
		if data is not None:
			self.mode = 'edit'

#		self.__init_ui()
	#----------------------------------------------------------------
#	def __init_ui(self):
#		# adjust phrasewheels etc
	#----------------------------------------------------------------
	# generic Edit Area mixin API
	#----------------------------------------------------------------
	def _valid_for_save(self):

		has_error = False

		if self._PRW_gender.GetData() is None:
			self._PRW_gender.SetFocus()
			has_error = True

		if self.data is not None:
			if not _validate_dob_field(self._PRW_dob):
				has_error = True

		if not self._PRW_dod.is_valid_timestamp(allow_empty = True):
			gmDispatcher.send(signal = u'statustext', msg = _('Invalid date of death.'))
			self._PRW_dod.SetFocus()
			has_error = True

		return (has_error is False)
	#----------------------------------------------------------------
	def _save_as_new(self):
		# not used yet
		return False
	#----------------------------------------------------------------
	def _save_as_update(self):

		if self._PRW_dob.GetValue().strip() == u'':
			if not _empty_dob_allowed():
				return False
			self.data['dob'] = None
		else:
			self.data['dob'] = self._PRW_dob.GetData()

		self.data['gender'] = self._PRW_gender.GetData()
		self.data['title'] = gmTools.none_if(self._PRW_title.GetValue().strip(), u'')
		self.data['deceased'] = self._PRW_dod.GetData()
		self.data['comment'] = gmTools.none_if(self._TCTRL_comment.GetValue().strip(), u'')

		self.data.save()
		return True
	#----------------------------------------------------------------
	def _refresh_as_new(self):
		pass
	#----------------------------------------------------------------
	def _refresh_from_existing(self):

		self._LBL_info.SetLabel(u'ID: #%s' % (
			self.data.ID
			# FIXME: add 'deleted' status
		))
		if self.data['dob'] is None:
			val = u''
		else:
			val = gmDateTime.pydt_strftime (
				self.data['dob'],
				format = '%Y-%m-%d %H:%M',
				accuracy = gmDateTime.acc_minutes
			)
		self._PRW_dob.SetText(value = val, data = self.data['dob'])
		if self.data['deceased'] is None:
			val = u''
		else:
			val = gmDateTime.pydt_strftime (
				self.data['deceased'],
				format = '%Y-%m-%d %H:%M',
				accuracy = gmDateTime.acc_minutes
			)
		self._PRW_dod.SetText(value = val, data = self.data['deceased'])
		self._PRW_gender.SetData(self.data['gender'])
		#self._PRW_ethnicity.SetValue()
		self._PRW_title.SetText(gmTools.coalesce(self.data['title'], u''))
		self._TCTRL_comment.SetValue(gmTools.coalesce(self.data['comment'], u''))
	#----------------------------------------------------------------
	def _refresh_as_new_from_existing(self):
		pass
#------------------------------------------------------------
from Gnumed.wxGladeWidgets import wxgPersonNameEAPnl

class cPersonNameEAPnl(wxgPersonNameEAPnl.wxgPersonNameEAPnl, gmEditArea.cGenericEditAreaMixin):
	"""An edit area for editing/creating names of people.

	Does NOT act on/listen to the current patient.
	"""
	def __init__(self, *args, **kwargs):

		try:
			data = kwargs['name']
			identity = gmPerson.cIdentity(aPK_obj = data['pk_identity'])
			del kwargs['name']
		except KeyError:
			data = None
			identity = kwargs['identity']
			del kwargs['identity']

		wxgPersonNameEAPnl.wxgPersonNameEAPnl.__init__(self, *args, **kwargs)
		gmEditArea.cGenericEditAreaMixin.__init__(self)

		self.__identity = identity

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
		validity = True

		if self._PRW_lastname.GetValue().strip() == u'':
			validity = False
			self._PRW_lastname.display_as_valid(False)
			self._PRW_lastname.SetFocus()
		else:
			self._PRW_lastname.display_as_valid(True)

		if self._PRW_firstname.GetValue().strip() == u'':
			validity = False
			self._PRW_firstname.display_as_valid(False)
			self._PRW_firstname.SetFocus()
		else:
			self._PRW_firstname.display_as_valid(True)

		return validity
	#----------------------------------------------------------------
	def _save_as_new(self):

		first = self._PRW_firstname.GetValue().strip()
		last = self._PRW_lastname.GetValue().strip()
		active = self._CHBOX_active.GetValue()

		data = self.__identity.add_name(first, last, active)

		old_nick = self.data['preferred']
		new_nick = gmTools.none_if(self._PRW_nick.GetValue().strip(), u'')
		if active:
			data['preferred'] = gmTools.coalesce(new_nick, old_nick)
		else:
			data['preferred'] = new_nick
		data['comment'] = gmTools.none_if(self._TCTRL_comment.GetValue().strip(), u'')
		data.save()

		self.data = data
		return True
	#----------------------------------------------------------------
	def _save_as_update(self):
		"""The knack here is that we can only update a few fields.

		Otherwise we need to clone the name and update that.
		"""
		first = self._PRW_firstname.GetValue().strip()
		last = self._PRW_lastname.GetValue().strip()
		active = self._CHBOX_active.GetValue()

		current_name = self.data['firstnames'].strip() + self.data['lastnames'].strip()
		new_name = first + last

		# editable fields only ?
		if new_name == current_name:
			self.data['active_name'] = self._CHBOX_active.GetValue()
			self.data['preferred'] = gmTools.none_if(self._PRW_nick.GetValue().strip(), u'')
			self.data['comment'] = gmTools.none_if(self._TCTRL_comment.GetValue().strip(), u'')
			self.data.save()
		# else clone name and update that
		else:
			name = self.__identity.add_name(first, last, active)
			name['preferred'] = gmTools.none_if(self._PRW_nick.GetValue().strip(), u'')
			name['comment'] = gmTools.none_if(self._TCTRL_comment.GetValue().strip(), u'')
			name.save()
			self.data = name

		return True
	#----------------------------------------------------------------
	def _refresh_as_new(self):
		self._PRW_firstname.SetText(value = u'', data = None)
		self._PRW_lastname.SetText(value = u'', data = None)
		self._PRW_nick.SetText(value = u'', data = None)
		self._TCTRL_comment.SetValue(u'')
		self._CHBOX_active.SetValue(False)

		self._PRW_firstname.SetFocus()
	#----------------------------------------------------------------
	def _refresh_as_new_from_existing(self):
		self._refresh_as_new()
		self._PRW_firstname.SetText(value = u'', data = None)
		self._PRW_nick.SetText(gmTools.coalesce(self.data['preferred'], u''))

		self._PRW_lastname.SetFocus()
	#----------------------------------------------------------------
	def _refresh_from_existing(self):
		self._PRW_firstname.SetText(self.data['firstnames'])
		self._PRW_lastname.SetText(self.data['lastnames'])
		self._PRW_nick.SetText(gmTools.coalesce(self.data['preferred'], u''))
		self._TCTRL_comment.SetValue(gmTools.coalesce(self.data['comment'], u''))
		self._CHBOX_active.SetValue(self.data['active_name'])

		self._TCTRL_comment.SetFocus()
#------------------------------------------------------------
# list manager
#------------------------------------------------------------
class cPersonNamesManagerPnl(gmListWidgets.cGenericListManagerPnl):
	"""A list for managing a person's names.

	Does NOT act on/listen to the current patient.
	"""
	def __init__(self, *args, **kwargs):

		try:
			self.__identity = kwargs['identity']
			del kwargs['identity']
		except KeyError:
			self.__identity = None

		gmListWidgets.cGenericListManagerPnl.__init__(self, *args, **kwargs)

		self.new_callback = self._add_name
		self.edit_callback = self._edit_name
		self.delete_callback = self._del_name
		self.refresh_callback = self.refresh

		self.__init_ui()
		self.refresh()
	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def refresh(self, *args, **kwargs):
		if self.__identity is None:
			self._LCTRL_items.set_string_items()
			return

		names = self.__identity.get_names()
		self._LCTRL_items.set_string_items (
			items = [ [
					gmTools.bool2str(n['active_name'], 'X', ''),
					n['lastnames'],
					n['firstnames'],
					gmTools.coalesce(n['preferred'], u''),
					gmTools.coalesce(n['comment'], u'')
				] for n in names ]
		)
		self._LCTRL_items.set_column_widths()
		self._LCTRL_items.set_data(data = names)
	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def __init_ui(self):
		self._LCTRL_items.set_columns(columns = [
			_('Active'),
			_('Lastname'),
			_('Firstname(s)'),
			_('Preferred Name'),
			_('Comment')
		])
		self._BTN_edit.SetLabel(_('Clone and &edit'))
	#--------------------------------------------------------
	def _add_name(self):
		#ea = cPersonNameEAPnl(self, -1, name = self.__identity.get_active_name())
		ea = cPersonNameEAPnl(self, -1, identity = self.__identity)
		dlg = gmEditArea.cGenericEditAreaDlg2(self, -1, edit_area = ea, single_entry = True)
		dlg.SetTitle(_('Adding new name'))
		if dlg.ShowModal() == wx.ID_OK:
			dlg.Destroy()
			return True
		dlg.Destroy()
		return False
	#--------------------------------------------------------
	def _edit_name(self, name):
		ea = cPersonNameEAPnl(self, -1, name = name)
		dlg = gmEditArea.cGenericEditAreaDlg2(self, -1, edit_area = ea, single_entry = True)
		dlg.SetTitle(_('Cloning name'))
		if dlg.ShowModal() == wx.ID_OK:
			dlg.Destroy()
			return True
		dlg.Destroy()
		return False
	#--------------------------------------------------------
	def _del_name(self, name):

		if len(self.__identity.get_names()) == 1:
			gmDispatcher.send(signal = u'statustext', msg = _('Cannot delete the only name of a person.'), beep = True)
			return False

		go_ahead = gmGuiHelpers.gm_show_question (
			_(	'It is often advisable to keep old names around and\n'
				'just create a new "currently active" name.\n'
				'\n'
				'This allows finding the patient by both the old\n'
				'and the new name (think before/after marriage).\n'
				'\n'
				'Do you still want to really delete\n'
				"this name from the patient ?"
			),
			_('Deleting name')
		)
		if not go_ahead:
			return False

		self.__identity.delete_name(name = name)
		return True
	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def _get_identity(self):
		return self.__identity

	def _set_identity(self, identity):
		self.__identity = identity
		self.refresh()

	identity = property(_get_identity, _set_identity)
#------------------------------------------------------------
class cPersonIDsManagerPnl(gmListWidgets.cGenericListManagerPnl):
	"""A list for managing a person's external IDs.

	Does NOT act on/listen to the current patient.
	"""
	def __init__(self, *args, **kwargs):

		try:
			self.__identity = kwargs['identity']
			del kwargs['identity']
		except KeyError:
			self.__identity = None

		gmListWidgets.cGenericListManagerPnl.__init__(self, *args, **kwargs)

		self.new_callback = self._add_id
		self.edit_callback = self._edit_id
		self.delete_callback = self._del_id
		self.refresh_callback = self.refresh

		self.__init_ui()
		self.refresh()
	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def refresh(self, *args, **kwargs):
		if self.__identity is None:
			self._LCTRL_items.set_string_items()
			return

		ids = self.__identity.get_external_ids()
		self._LCTRL_items.set_string_items (
			items = [ [
					i['name'],
					i['value'],
					gmTools.coalesce(i['issuer'], u''),
					gmTools.coalesce(i['comment'], u'')
				] for i in ids
			]
		)
		self._LCTRL_items.set_column_widths()
		self._LCTRL_items.set_data(data = ids)
	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def __init_ui(self):
		self._LCTRL_items.set_columns(columns = [
			_('ID type'),
			_('Value'),
			_('Issuer'),
			_('Comment')
		])
	#--------------------------------------------------------
	def _add_id(self):
		ea = cExternalIDEditAreaPnl(self, -1)
		ea.identity = self.__identity
		dlg = gmEditArea.cGenericEditAreaDlg2(self, -1, edit_area = ea)
		dlg.SetTitle(_('Adding new external ID'))
		if dlg.ShowModal() == wx.ID_OK:
			dlg.Destroy()
			return True
		dlg.Destroy()
		return False
	#--------------------------------------------------------
	def _edit_id(self, ext_id):
		ea = cExternalIDEditAreaPnl(self, -1, external_id = ext_id)
		ea.identity = self.__identity
		dlg = gmEditArea.cGenericEditAreaDlg2(self, -1, edit_area = ea, single_entry = True)
		dlg.SetTitle(_('Editing external ID'))
		if dlg.ShowModal() == wx.ID_OK:
			dlg.Destroy()
			return True
		dlg.Destroy()
		return False
	#--------------------------------------------------------
	def _del_id(self, ext_id):
		go_ahead = gmGuiHelpers.gm_show_question (
			_(	'Do you really want to delete this\n'
				'external ID from the patient ?'),
			_('Deleting external ID')
		)
		if not go_ahead:
			return False
		self.__identity.delete_external_id(pk_ext_id = ext_id['pk_id'])
		return True
	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def _get_identity(self):
		return self.__identity

	def _set_identity(self, identity):
		self.__identity = identity
		self.refresh()

	identity = property(_get_identity, _set_identity)
#------------------------------------------------------------
# integrated panels
#------------------------------------------------------------
from Gnumed.wxGladeWidgets import wxgPersonIdentityManagerPnl

class cPersonIdentityManagerPnl(wxgPersonIdentityManagerPnl.wxgPersonIdentityManagerPnl):
	"""A panel for editing identity data for a person.

	- provides access to:
	  - identity EA
	  - name list manager
	  - external IDs list manager

	Does NOT act on/listen to the current patient.
	"""
	def __init__(self, *args, **kwargs):

		wxgPersonIdentityManagerPnl.wxgPersonIdentityManagerPnl.__init__(self, *args, **kwargs)

		self.__identity = None
		self.refresh()
	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def refresh(self):
		self._PNL_names.identity = self.__identity
		self._PNL_ids.identity = self.__identity
		# this is an Edit Area:
		self._PNL_identity.mode = 'new'
		self._PNL_identity.data = self.__identity
		if self.__identity is not None:
			self._PNL_identity.mode = 'edit'
			self._PNL_identity._refresh_from_existing()
	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def _get_identity(self):
		return self.__identity

	def _set_identity(self, identity):
		self.__identity = identity
		self.refresh()

	identity = property(_get_identity, _set_identity)
	#--------------------------------------------------------
	# event handlers
	#--------------------------------------------------------
	def _on_save_identity_details_button_pressed(self, event):
		if not self._PNL_identity.save():
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot save identity. Incomplete information.'), beep = True)
		#self._PNL_identity.refresh()
	#--------------------------------------------------------
	def _on_reload_identity_button_pressed(self, event):
		self._PNL_identity.refresh()

#============================================================
from Gnumed.wxGladeWidgets import wxgPersonSocialNetworkManagerPnl

class cPersonSocialNetworkManagerPnl(wxgPersonSocialNetworkManagerPnl.wxgPersonSocialNetworkManagerPnl):
	def __init__(self, *args, **kwargs):

		wxgPersonSocialNetworkManagerPnl.wxgPersonSocialNetworkManagerPnl.__init__(self, *args, **kwargs)

		self.__identity = None
		self._PRW_provider.selection_only = False
		self.refresh()
	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def refresh(self):

		tt = _('Link another person in this database as the emergency contact:\n\nEnter person name part or identifier and hit <enter>.')

		if self.__identity is None:
			self._TCTRL_er_contact.SetValue(u'')
			self._TCTRL_person.person = None
			self._TCTRL_person.SetToolTipString(tt)

			self._PRW_provider.SetText(value = u'', data = None)
			return

		self._TCTRL_er_contact.SetValue(gmTools.coalesce(self.__identity['emergency_contact'], u''))
		if self.__identity['pk_emergency_contact'] is not None:
			ident = gmPerson.cIdentity(aPK_obj = self.__identity['pk_emergency_contact'])
			self._TCTRL_person.person = ident
			tt = u'%s\n\n%s\n\n%s' % (
				tt,
				ident['description_gender'],
				u'\n'.join([
					u'%s: %s%s' % (
						c['l10n_comm_type'],
						c['url'],
						gmTools.bool2subst(c['is_confidential'], _(' (confidential !)'), u'', u'')
					)
					for c in ident.get_comm_channels()
				])
			)
		else:
			self._TCTRL_person.person = None

		self._TCTRL_person.SetToolTipString(tt)

		if self.__identity['pk_primary_provider'] is None:
			self._PRW_provider.SetText(value = u'', data = None)
		else:
			self._PRW_provider.SetData(data = self.__identity['pk_primary_provider'])
	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def _get_identity(self):
		return self.__identity

	def _set_identity(self, identity):
		self.__identity = identity
		self.refresh()

	identity = property(_get_identity, _set_identity)
	#--------------------------------------------------------
	# event handlers
	#--------------------------------------------------------
	def _on_save_button_pressed(self, event):
		if self.__identity is not None:
			self.__identity['emergency_contact'] = self._TCTRL_er_contact.GetValue().strip()
			if self._TCTRL_person.person is not None:
				self.__identity['pk_emergency_contact'] = self._TCTRL_person.person.ID
			if self._PRW_provider.GetValue().strip == u'':
				self.__identity['pk_primary_provider'] = None
			else:
				self.__identity['pk_primary_provider'] = self._PRW_provider.GetData()

			self.__identity.save()
			gmDispatcher.send(signal = 'statustext', msg = _('Emergency data and primary provider saved.'), beep = False)

		event.Skip()
	#--------------------------------------------------------
	def _on_reload_button_pressed(self, event):
		self.refresh()
	#--------------------------------------------------------
	def _on_remove_contact_button_pressed(self, event):
		event.Skip()

		if self.__identity is None:
			return

		self._TCTRL_person.person = None

		self.__identity['pk_emergency_contact'] = None
		self.__identity.save()
	#--------------------------------------------------------
	def _on_button_activate_contact_pressed(self, event):
		ident = self._TCTRL_person.person
		if ident is not None:
			from Gnumed.wxpython import gmPatSearchWidgets
			gmPatSearchWidgets.set_active_patient(patient = ident, forced_reload = False)

		event.Skip()
#============================================================
# new-patient widgets
#============================================================
def create_new_person(parent=None, activate=False):

	dbcfg = gmCfg.cCfgSQL()

	def_region = dbcfg.get2 (
		option = u'person.create.default_region',
		workplace = gmSurgery.gmCurrentPractice().active_workplace,
		bias = u'user'
	)
	def_country = None

	if def_region is None:
		def_country = dbcfg.get2 (
			option = u'person.create.default_country',
			workplace = gmSurgery.gmCurrentPractice().active_workplace,
			bias = u'user'
		)
	else:
		countries = gmDemographicRecord.get_country_for_region(region = def_region)
		if len(countries) == 1:
			def_country = countries[0]['code_country']

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	ea = cNewPatientEAPnl(parent = parent, id = -1, country = def_country, region = def_region)
	dlg = gmEditArea.cGenericEditAreaDlg2(parent = parent, id = -1, edit_area = ea, single_entry = True)
	dlg.SetTitle(_('Adding new person'))
	ea._PRW_lastname.SetFocus()
	result = dlg.ShowModal()
	pat = ea.data
	dlg.Destroy()

	if result != wx.ID_OK:
		return False

	_log.debug('created new person [%s]', pat.ID)

	if activate:
		from Gnumed.wxpython import gmPatSearchWidgets
		gmPatSearchWidgets.set_active_patient(patient = pat)

	gmDispatcher.send(signal = 'display_widget', name = 'gmNotebookedPatientEditionPlugin')

	return True
#============================================================
from Gnumed.wxGladeWidgets import wxgNewPatientEAPnl

class cNewPatientEAPnl(wxgNewPatientEAPnl.wxgNewPatientEAPnl, gmEditArea.cGenericEditAreaMixin):

	def __init__(self, *args, **kwargs):

		try:
			self.default_region = kwargs['region']
			del kwargs['region']
		except KeyError:
			self.default_region = None

		try:
			self.default_country = kwargs['country']
			del kwargs['country']
		except KeyError:
			self.default_country = None

		wxgNewPatientEAPnl.wxgNewPatientEAPnl.__init__(self, *args, **kwargs)
		gmEditArea.cGenericEditAreaMixin.__init__(self)

		self.mode = 'new'
		self.data = None
		self._address = None

		self.__init_ui()
		self.__register_interests()
	#----------------------------------------------------------------
	# internal helpers
	#----------------------------------------------------------------
	def __init_ui(self):
		self._PRW_lastname.final_regex = '.+'
		self._PRW_firstnames.final_regex = '.+'
		self._PRW_address_searcher.selection_only = False

		# only if we would support None on selection_only's:
#		self._PRW_external_id_type.selection_only = True

		if self.default_country is not None:
			match = self._PRW_country._data2match(data = self.default_country)
			if match is not None:
				self._PRW_country.SetText(value = match['field_label'], data = match['data'])

		if self.default_region is not None:
			self._PRW_region.SetText(value = self.default_region)
	#----------------------------------------------------------------
	def __perhaps_invalidate_address_searcher(self, ctrl=None, field=None):

		adr = self._PRW_address_searcher.address
		if adr is None:
			return True

		if ctrl.GetValue().strip() != adr[field]:
			wx.CallAfter(self._PRW_address_searcher.SetText, value = u'', data = None)
			return True

		return False
	#----------------------------------------------------------------
	def __set_fields_from_address_searcher(self):
		adr = self._PRW_address_searcher.address
		if adr is None:
			return True

		self._PRW_zip.SetText(value = adr['postcode'], data = adr['postcode'])

		self._PRW_street.SetText(value = adr['street'], data = adr['street'])
		self._PRW_street.set_context(context = u'zip', val = adr['postcode'])

		self._TCTRL_number.SetValue(adr['number'])
		self._TCTRL_unit.SetValue(gmTools.coalesce(adr['subunit'], u''))

		self._PRW_urb.SetText(value = adr['urb'], data = adr['urb'])
		self._PRW_urb.set_context(context = u'zip', val = adr['postcode'])

		self._PRW_region.SetText(value = adr['l10n_state'], data = adr['code_state'])
		self._PRW_region.set_context(context = u'zip', val = adr['postcode'])

		self._PRW_country.SetText(value = adr['l10n_country'], data = adr['code_country'])
		self._PRW_country.set_context(context = u'zip', val = adr['postcode'])
	#----------------------------------------------------------------
	def __identity_valid_for_save(self):
		error = False

		# name fields
		if self._PRW_lastname.GetValue().strip() == u'':
			error = True
			gmDispatcher.send(signal = 'statustext', msg = _('Must enter lastname.'))
			self._PRW_lastname.display_as_valid(False)
		else:
			self._PRW_lastname.display_as_valid(True)

		if self._PRW_firstnames.GetValue().strip() == '':
			error = True
			gmDispatcher.send(signal = 'statustext', msg = _('Must enter first name.'))
			self._PRW_firstnames.display_as_valid(False)
		else:
			self._PRW_firstnames.display_as_valid(True)

		# gender
		if self._PRW_gender.GetData() is None:
			error = True
			gmDispatcher.send(signal = 'statustext', msg = _('Must select gender.'))
			self._PRW_gender.display_as_valid(False)
		else:
			self._PRW_gender.display_as_valid(True)

		# dob validation
		if not _validate_dob_field(self._PRW_dob):
			error = True

		# TOB validation if non-empty
#		if self._TCTRL_tob.GetValue().strip() != u'':

		return (not error)
	#----------------------------------------------------------------
	def __address_valid_for_save(self, empty_address_is_valid=False):

		# existing address ? if so set other fields
		if self._PRW_address_searcher.GetData() is not None:
			wx.CallAfter(self.__set_fields_from_address_searcher)
			return True

		# must either all contain something or none of them
		fields_to_fill = (
			self._TCTRL_number,
			self._PRW_zip,
			self._PRW_street,
			self._PRW_urb,
			self._PRW_type,
			self._PRW_region,
			self._PRW_country
		)
		no_of_filled_fields = 0

		for field in fields_to_fill:
			if field.GetValue().strip() != u'':
				no_of_filled_fields += 1
				field.SetBackgroundColour(gmPhraseWheel.color_prw_valid)
				field.Refresh()

		# empty address ?
		if no_of_filled_fields == 0:
			if empty_address_is_valid:
				return True
			else:
				return None

		# incompletely filled address ?
		if no_of_filled_fields != len(fields_to_fill):
			for field in fields_to_fill:
				if field.GetValue().strip() == u'':
					field.SetBackgroundColour(gmPhraseWheel.color_prw_invalid)
					field.SetFocus()
					field.Refresh()
			msg = _('To properly create an address, all the related fields must be filled in.')
			gmGuiHelpers.gm_show_error(msg, _('Required fields'))
			return False

		# fields which must contain a selected item
		# FIXME: they must also contain an *acceptable combination* which
		# FIXME: can only be tested against the database itself ...
		strict_fields = (
			self._PRW_type,
			self._PRW_region,
			self._PRW_country
		)
		error = False
		for field in strict_fields:
			if field.GetData() is None:
				error = True
				field.SetBackgroundColour(gmPhraseWheel.color_prw_invalid)
				field.SetFocus()
			else:
				field.SetBackgroundColour(gmPhraseWheel.color_prw_valid)
			field.Refresh()

		if error:
			msg = _('This field must contain an item selected from the dropdown list.')
			gmGuiHelpers.gm_show_error(msg, _('Required fields'))
			return False

		return True
	#----------------------------------------------------------------
	def __register_interests(self):

		# identity
		self._PRW_firstnames.add_callback_on_lose_focus(self._on_leaving_firstname)

		# address
		self._PRW_address_searcher.add_callback_on_lose_focus(self._on_leaving_adress_searcher)

		# invalidate address searcher when any field edited
		self._PRW_street.add_callback_on_lose_focus(self._invalidate_address_searcher)
		wx.EVT_KILL_FOCUS(self._TCTRL_number, self._invalidate_address_searcher)
		wx.EVT_KILL_FOCUS(self._TCTRL_unit, self._invalidate_address_searcher)
		self._PRW_urb.add_callback_on_lose_focus(self._invalidate_address_searcher)
		self._PRW_region.add_callback_on_lose_focus(self._invalidate_address_searcher)

		self._PRW_zip.add_callback_on_lose_focus(self._on_leaving_zip)
		self._PRW_country.add_callback_on_lose_focus(self._on_leaving_country)
	#----------------------------------------------------------------
	# event handlers
	#----------------------------------------------------------------
	def _on_leaving_firstname(self):
		"""Set the gender according to entered firstname.

		Matches are fetched from existing records in backend.
		"""
		# only set if not already set so as to not
		# overwrite a change by the user
		if self._PRW_gender.GetData() is not None:
			return True

		firstname = self._PRW_firstnames.GetValue().strip()
		if firstname == u'':
			return True

		gender = gmPerson.map_firstnames2gender(firstnames = firstname)
		if gender is None:
			return True

		wx.CallAfter(self._PRW_gender.SetData, gender)
		return True
	#----------------------------------------------------------------
	def _on_leaving_zip(self):
		self.__perhaps_invalidate_address_searcher(self._PRW_zip, 'postcode')

		zip_code = gmTools.none_if(self._PRW_zip.GetValue().strip(), u'')
		self._PRW_street.set_context(context = u'zip', val = zip_code)
		self._PRW_urb.set_context(context = u'zip', val = zip_code)
		self._PRW_region.set_context(context = u'zip', val = zip_code)
		self._PRW_country.set_context(context = u'zip', val = zip_code)

		return True
	#----------------------------------------------------------------
	def _on_leaving_country(self):
		self.__perhaps_invalidate_address_searcher(self._PRW_country, 'l10n_country')

		country = gmTools.none_if(self._PRW_country.GetValue().strip(), u'')
		self._PRW_region.set_context(context = u'country', val = country)

		return True
	#----------------------------------------------------------------
	def _invalidate_address_searcher(self, *args, **kwargs):
		mapping = [
			(self._PRW_street, 'street'),
			(self._TCTRL_number, 'number'),
			(self._TCTRL_unit, 'subunit'),
			(self._PRW_urb, 'urb'),
			(self._PRW_region, 'l10n_state')
		]
		# loop through fields and invalidate address searcher if different
		for ctrl, field in mapping:
			if self.__perhaps_invalidate_address_searcher(ctrl, field):
				return True

		return True
	#----------------------------------------------------------------
	def _on_leaving_adress_searcher(self):
		if self._PRW_address_searcher.address is None:
			return True

		wx.CallAfter(self.__set_fields_from_address_searcher)
		return True
	#----------------------------------------------------------------
	# generic Edit Area mixin API
	#----------------------------------------------------------------
	def _valid_for_save(self):
		if self._PRW_primary_provider.GetValue().strip() == u'':
			self._PRW_primary_provider.display_as_valid(True)
		else:
			if self._PRW_primary_provider.GetData() is None:
				self._PRW_primary_provider.display_as_valid(False)
			else:
				self._PRW_primary_provider.display_as_valid(True)
		return (self.__identity_valid_for_save() and self.__address_valid_for_save(empty_address_is_valid = True))
	#----------------------------------------------------------------
	def _save_as_new(self):

		if self._PRW_dob.GetValue().strip() == u'':
			if not _empty_dob_allowed():
				self._PRW_dob.display_as_valid(False)
				self._PRW_dob.SetFocus()
				return False

		# identity
		new_identity = gmPerson.create_identity (
			gender = self._PRW_gender.GetData(),
			dob = self._PRW_dob.GetData(),
			lastnames = self._PRW_lastname.GetValue().strip(),
			firstnames = self._PRW_firstnames.GetValue().strip()
		)
		_log.debug('identity created: %s' % new_identity)

		new_identity['title'] = gmTools.none_if(self._PRW_title.GetValue().strip())
		new_identity.set_nickname(nickname = gmTools.none_if(self._PRW_nickname.GetValue().strip(), u''))
		#TOB
		prov = self._PRW_primary_provider.GetData()
		if prov is not None:
			new_identity['pk_primary_provider'] = prov
		new_identity.save()

		name = new_identity.get_active_name()
		name['comment'] = gmTools.none_if(self._TCTRL_comment.GetValue().strip(), u'')
		name.save()

		# address
		# if we reach this the address cannot be completely empty
		is_valid = self.__address_valid_for_save(empty_address_is_valid = False)
		if is_valid is True:
			# because we currently only check for non-emptiness
			# we must still deal with database errors
			try:
				new_identity.link_address (
					number = self._TCTRL_number.GetValue().strip(),
					street = self._PRW_street.GetValue().strip(),
					postcode = self._PRW_zip.GetValue().strip(),
					urb = self._PRW_urb.GetValue().strip(),
					state = self._PRW_region.GetData(),
					country = self._PRW_country.GetData(),
					subunit = gmTools.none_if(self._TCTRL_unit.GetValue().strip(), u''),
					id_type = self._PRW_type.GetData()
				)
			except gmPG2.dbapi.InternalError:
				_log.debug('number: >>%s<<', self._TCTRL_number.GetValue().strip())
				_log.debug('(sub)unit: >>%s<<', self._TCTRL_unit.GetValue().strip())
				_log.debug('street: >>%s<<', self._PRW_street.GetValue().strip())
				_log.debug('postcode: >>%s<<', self._PRW_zip.GetValue().strip())
				_log.debug('urb: >>%s<<', self._PRW_urb.GetValue().strip())
				_log.debug('state: >>%s<<', self._PRW_region.GetData().strip())
				_log.debug('country: >>%s<<', self._PRW_country.GetData().strip())
				_log.exception('cannot link address')
				gmGuiHelpers.gm_show_error (
					aTitle = _('Saving address'),
					aMessage = _(
						'Cannot save this address.\n'
						'\n'
						'You will have to add it via the Demographics plugin.\n'
					)
				)
		elif is_valid is False:
			gmGuiHelpers.gm_show_error (
				aTitle = _('Saving address'),
				aMessage = _(
					'Address not saved.\n'
					'\n'
					'You will have to add it via the Demographics plugin.\n'
				)
			)
		# else it is None which means empty address which we ignore

		# phone
		channel_name = self._PRW_channel_type.GetValue().strip()
		pk_channel_type = self._PRW_channel_type.GetData()
		if pk_channel_type is None:
			if channel_name == u'':
				channel_name = u'homephone'
		new_identity.link_comm_channel (
			comm_medium = channel_name,
			pk_channel_type = pk_channel_type,
			url = gmTools.none_if(self._TCTRL_phone.GetValue().strip(), u''),
			is_confidential = False
		)

		# external ID
		pk_type = self._PRW_external_id_type.GetData()
		id_value = self._TCTRL_external_id_value.GetValue().strip()
		if (pk_type is not None) and (id_value != u''):
			new_identity.add_external_id(value = id_value, pk_type = pk_type)

		# occupation
		new_identity.link_occupation (
			occupation = gmTools.none_if(self._PRW_occupation.GetValue().strip(), u'')
		)

		self.data = new_identity
		return True
	#----------------------------------------------------------------
	def _save_as_update(self):
		raise NotImplementedError('[%s]: not expected to be used' % self.__class__.__name__)
	#----------------------------------------------------------------
	def _refresh_as_new(self):
		# FIXME: button "empty out"
		return
	#----------------------------------------------------------------
	def _refresh_from_existing(self):
		return		# there is no forward button so nothing to do here
	#----------------------------------------------------------------
	def _refresh_as_new_from_existing(self):
		raise NotImplementedError('[%s]: not expected to be used' % self.__class__.__name__)

#============================================================
# patient demographics editing classes
#============================================================
class cPersonDemographicsEditorNb(wx.Notebook):
	"""Notebook displaying demographics editing pages:

		- Contacts (addresses, phone numbers, etc)
		- Identity
		- Social network (significant others, GP, etc)

	Does NOT act on/listen to the current patient.
	"""
	#--------------------------------------------------------
	def __init__(self, parent, id):

		wx.Notebook.__init__ (
			self,
			parent = parent,
			id = id,
			style = wx.NB_TOP | wx.NB_MULTILINE | wx.NO_BORDER,
			name = self.__class__.__name__
		)

		self.__identity = None
		self.__do_layout()
		self.SetSelection(0)
	#--------------------------------------------------------
	# public API
	#--------------------------------------------------------
	def refresh(self):
		"""Populate fields in pages with data from model."""
		for page_idx in range(self.GetPageCount()):
			page = self.GetPage(page_idx)
			page.identity = self.__identity

		return True
	#--------------------------------------------------------
	# internal API
	#--------------------------------------------------------
	def __do_layout(self):
		"""Build patient edition notebook pages."""

		# contacts page
		new_page = gmPersonContactWidgets.cPersonContactsManagerPnl(self, -1)
		new_page.identity = self.__identity
		self.AddPage (
			page = new_page,
			text = _('Contacts'),
			select = True
		)

		# identity page
		new_page = cPersonIdentityManagerPnl(self, -1)
		new_page.identity = self.__identity
		self.AddPage (
			page = new_page,
			text = _('Identity'),
			select = False
		)

		# social network page
		new_page = cPersonSocialNetworkManagerPnl(self, -1)
		new_page.identity = self.__identity
		self.AddPage (
			page = new_page,
			text = _('Social network'),
			select = False
		)
	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def _get_identity(self):
		return self.__identity

	def _set_identity(self, identity):
		self.__identity = identity

	identity = property(_get_identity, _set_identity)
#============================================================
# old occupation widgets
#============================================================
# FIXME: support multiple occupations
# FIXME: redo with wxGlade

class cPatOccupationsPanel(wx.Panel):
	"""Page containing patient occupations edition fields.
	"""
	def __init__(self, parent, id, ident=None):
		"""
		Creates a new instance of BasicPatDetailsPage
		@param parent - The parent widget
		@type parent - A wx.Window instance
		@param id - The widget id
		@type id - An integer
		"""
		wx.Panel.__init__(self, parent, id)
		self.__ident = ident
		self.__do_layout()
	#--------------------------------------------------------
	def __do_layout(self):
		PNL_form = wx.Panel(self, -1)
		# occupation
		STT_occupation = wx.StaticText(PNL_form, -1, _('Occupation'))
		self.PRW_occupation = cOccupationPhraseWheel(parent = PNL_form,	id = -1)
		self.PRW_occupation.SetToolTipString(_("primary occupation of the patient"))
		# known since
		STT_occupation_updated = wx.StaticText(PNL_form, -1, _('Last updated'))
		self.TTC_occupation_updated = wx.TextCtrl(PNL_form, -1, style = wx.TE_READONLY)

		# layout input widgets
		SZR_input = wx.FlexGridSizer(cols = 2, rows = 5, vgap = 4, hgap = 4)
		SZR_input.AddGrowableCol(1)				
		SZR_input.Add(STT_occupation, 0, wx.SHAPED)
		SZR_input.Add(self.PRW_occupation, 1, wx.EXPAND)
		SZR_input.Add(STT_occupation_updated, 0, wx.SHAPED)
		SZR_input.Add(self.TTC_occupation_updated, 1, wx.EXPAND)
		PNL_form.SetSizerAndFit(SZR_input)

		# layout page
		SZR_main = wx.BoxSizer(wx.VERTICAL)
		SZR_main.Add(PNL_form, 1, wx.EXPAND)
		self.SetSizer(SZR_main)
	#--------------------------------------------------------
	def set_identity(self, identity):
		return self.refresh(identity=identity)
	#--------------------------------------------------------
	def refresh(self, identity=None):
		if identity is not None:
			self.__ident = identity
		jobs = self.__ident.get_occupations()
		if len(jobs) > 0:
			self.PRW_occupation.SetText(jobs[0]['l10n_occupation'])
			self.TTC_occupation_updated.SetValue(jobs[0]['modified_when'].strftime('%m/%Y'))
		return True
	#--------------------------------------------------------
	def save(self):
		if self.PRW_occupation.IsModified():
			new_job = self.PRW_occupation.GetValue().strip()
			jobs = self.__ident.get_occupations()
			for job in jobs:
				if job['l10n_occupation'] == new_job:
					continue
				self.__ident.unlink_occupation(occupation = job['l10n_occupation'])
			self.__ident.link_occupation(occupation = new_job)
		return True
#============================================================
class cNotebookedPatEditionPanel(wx.Panel, gmRegetMixin.cRegetOnPaintMixin):
	"""Patient demographics plugin for main notebook.

	Hosts another notebook with pages for Identity, Contacts, etc.

	Acts on/listens to the currently active patient.
	"""
	#--------------------------------------------------------
	def __init__(self, parent, id):
		wx.Panel.__init__ (self, parent = parent, id = id, style = wx.NO_BORDER)
		gmRegetMixin.cRegetOnPaintMixin.__init__(self)
		self.__do_layout()
		self.__register_interests()
	#--------------------------------------------------------
	# public API
	#--------------------------------------------------------
	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def __do_layout(self):
		"""Arrange widgets."""
		self.__patient_notebook = cPersonDemographicsEditorNb(self, -1)

		szr_main = wx.BoxSizer(wx.VERTICAL)
		szr_main.Add(self.__patient_notebook, 1, wx.EXPAND)
		self.SetSizerAndFit(szr_main)
	#--------------------------------------------------------
	# event handling
	#--------------------------------------------------------
	def __register_interests(self):
		gmDispatcher.connect(signal = u'pre_patient_selection', receiver = self._on_pre_patient_selection)
		gmDispatcher.connect(signal = u'post_patient_selection', receiver = self._on_post_patient_selection)
	#--------------------------------------------------------
	def _on_pre_patient_selection(self):
		self._schedule_data_reget()
	#--------------------------------------------------------
	def _on_post_patient_selection(self):
		self._schedule_data_reget()
		print "_on_post_patient_selection: scheduled"
	# reget mixin API
	#--------------------------------------------------------
	def _populate_with_data(self):
		"""Populate fields in pages with data from model."""
		pat = gmPerson.gmCurrentPatient()
		if pat.connected:
			self.__patient_notebook.identity = pat
		else:
			self.__patient_notebook.identity = None
		self.__patient_notebook.refresh()
		return True
#============================================================
#============================================================
if __name__ == "__main__":

	#--------------------------------------------------------
	def test_organizer_pnl():
		app = wx.PyWidgetTester(size = (600, 400))
		app.SetWidget(cKOrganizerSchedulePnl)
		app.MainLoop()
	#--------------------------------------------------------
	def test_person_names_pnl():
		app = wx.PyWidgetTester(size = (600, 400))
		widget = cPersonNamesManagerPnl(app.frame, -1)
		widget.identity = activate_patient()
		app.frame.Show(True)
		app.MainLoop()
	#--------------------------------------------------------
	def test_person_ids_pnl():
		app = wx.PyWidgetTester(size = (600, 400))
		widget = cPersonIDsManagerPnl(app.frame, -1)
		widget.identity = activate_patient()
		app.frame.Show(True)
		app.MainLoop()
	#--------------------------------------------------------
	def test_pat_ids_pnl():
		app = wx.PyWidgetTester(size = (600, 400))
		widget = cPersonIdentityManagerPnl(app.frame, -1)
		widget.identity = activate_patient()
		app.frame.Show(True)
		app.MainLoop()
	#--------------------------------------------------------
	def test_name_ea_pnl():
		app = wx.PyWidgetTester(size = (600, 400))
		app.SetWidget(cPersonNameEAPnl, name = activate_patient().get_active_name())
		app.MainLoop()
	#--------------------------------------------------------
	def test_cPersonDemographicsEditorNb():
		app = wx.PyWidgetTester(size = (600, 400))
		widget = cPersonDemographicsEditorNb(app.frame, -1)
		widget.identity = activate_patient()
		widget.refresh()
		app.frame.Show(True)
		app.MainLoop()
	#--------------------------------------------------------
	def activate_patient():
		patient = gmPersonSearch.ask_for_patient()
		if patient is None:
			print "No patient. Exiting gracefully..."
			sys.exit(0)
		from Gnumed.wxpython import gmPatSearchWidgets
		gmPatSearchWidgets.set_active_patient(patient=patient)
		return patient
	#--------------------------------------------------------
	if len(sys.argv) > 1 and sys.argv[1] == 'test':

		gmI18N.activate_locale()
		gmI18N.install_domain(domain='gnumed')
		gmPG2.get_connection()

#		app = wx.PyWidgetTester(size = (400, 300))
#		app.SetWidget(cNotebookedPatEditionPanel, -1)
#		app.frame.Show(True)
#		app.MainLoop()

		# phrasewheels
#		test_organizer_pnl()

		# identity related widgets
		#test_person_names_pnl()
		test_person_ids_pnl()
		#test_pat_ids_pnl()
		#test_name_ea_pnl()

		#test_cPersonDemographicsEditorNb()

#============================================================
