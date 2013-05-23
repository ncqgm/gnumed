#  coding: latin-1
"""GNUmed quick person search widgets.

This widget allows to search for persons based on the
critera name, date of birth and person ID. It goes to
considerable lengths to understand the user's intent from
her input. For that to work well we need per-culture
query generators. However, there's always the fallback
generator.
"""
#============================================================
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = 'GPL v2 or later (for details see http://www.gnu.org/)'

import sys, os.path, glob, re as regex, logging


import wx


if __name__ == '__main__':
	sys.path.insert(0, '../../')
	from Gnumed.pycommon import gmLog2
from Gnumed.pycommon import gmDispatcher
from Gnumed.pycommon import gmDateTime
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmPG2
from Gnumed.pycommon import gmI18N
from Gnumed.pycommon import gmCfg
from Gnumed.pycommon import gmMatchProvider
from Gnumed.pycommon import gmCfg2
from Gnumed.pycommon import gmNetworkTools

from Gnumed.business import gmPerson
from Gnumed.business import gmStaff
from Gnumed.business import gmKVK
from Gnumed.business import gmSurgery
from Gnumed.business import gmCA_MSVA
from Gnumed.business import gmPersonSearch
from Gnumed.business import gmProviderInbox

from Gnumed.wxpython import gmGuiHelpers
from Gnumed.wxpython import gmAuthWidgets
from Gnumed.wxpython import gmRegetMixin
from Gnumed.wxpython import gmEditArea
from Gnumed.wxpython import gmPhraseWheel
from Gnumed.wxpython.gmPersonCreationWidgets import create_new_person


_log = logging.getLogger('gm.person')

_cfg = gmCfg2.gmCfgData()

ID_PatPickList = wx.NewId()
ID_BTN_AddNew = wx.NewId()

#============================================================
def merge_patients(parent=None):
	dlg = cMergePatientsDlg(parent, -1)
	result = dlg.ShowModal()
#============================================================
from Gnumed.wxGladeWidgets import wxgMergePatientsDlg

class cMergePatientsDlg(wxgMergePatientsDlg.wxgMergePatientsDlg):

	def __init__(self, *args, **kwargs):
		wxgMergePatientsDlg.wxgMergePatientsDlg.__init__(self, *args, **kwargs)

		curr_pat = gmPerson.gmCurrentPatient()
		if curr_pat.connected:
			self._TCTRL_patient1.person = curr_pat
			self._TCTRL_patient1._display_name()
			self._RBTN_patient1.SetValue(True)
	#--------------------------------------------------------
	def _on_merge_button_pressed(self, event):

		if self._TCTRL_patient1.person is None:
			return

		if self._TCTRL_patient2.person is None:
			return

		if self._RBTN_patient1.GetValue():
			patient2keep = self._TCTRL_patient1.person
			patient2merge = self._TCTRL_patient2.person
		else:
			patient2keep = self._TCTRL_patient2.person
			patient2merge = self._TCTRL_patient1.person

		if patient2merge['lastnames'] == u'Kirk':
			if _cfg.get(option = 'debug'):
				gmNetworkTools.open_url_in_browser(url = 'http://en.wikipedia.org/wiki/File:Picard_as_Locutus.jpg')
				gmGuiHelpers.gm_show_info(_('\n\nYou will be assimilated.\n\n'), _('The Borg'))
				return
			else:
				gmDispatcher.send(signal = 'statustext', msg = _('Cannot merge Kirk into another patient.'), beep = True)
				return

		doit = gmGuiHelpers.gm_show_question (
			aMessage = _(
				'Are you positively sure you want to merge patient\n\n'
				' #%s: %s (%s, %s)\n\n'
				'into patient\n\n'
				' #%s: %s (%s, %s) ?\n\n'
				'Note that this action can ONLY be reversed by a laborious\n'
				'manual process requiring in-depth knowledge about databases\n'
				'and the patients in question !\n'
			) % (
				patient2merge.ID,
				patient2merge['description_gender'],
				patient2merge['gender'],
				patient2merge.get_formatted_dob(format = '%Y %b %d', encoding = gmI18N.get_encoding()),
				patient2keep.ID,
				patient2keep['description_gender'],
				patient2keep['gender'],
				patient2keep.get_formatted_dob(format = '%Y %b %d', encoding = gmI18N.get_encoding())
			),
			aTitle = _('Merging patients: confirmation'),
			cancel_button = False
		)
		if not doit:
			return

		conn = gmAuthWidgets.get_dbowner_connection(procedure = _('Merging patients'))
		if conn is None:
			return

		success, msg = patient2keep.assimilate_identity(other_identity = patient2merge, link_obj = conn)
		conn.close()
		if not success:
			gmDispatcher.send(signal = 'statustext', msg = msg, beep = True)
			return

		# announce success, offer to activate kept patient if not active
		doit = gmGuiHelpers.gm_show_question (
			aMessage = _(
				'The patient\n'
				'\n'
				' #%s: %s (%s, %s)\n'
				'\n'
				'has successfully been merged into\n'
				'\n'
				' #%s: %s (%s, %s)\n'
				'\n'
				'\n'
				'Do you want to activate that patient\n'
				'now for further modifications ?\n'
			) % (
				patient2merge.ID,
				patient2merge['description_gender'],
				patient2merge['gender'],
				patient2merge.get_formatted_dob(format = '%Y %b %d', encoding = gmI18N.get_encoding()),
				patient2keep.ID,
				patient2keep['description_gender'],
				patient2keep['gender'],
				patient2keep.get_formatted_dob(format = '%Y %b %d', encoding = gmI18N.get_encoding())
			),
			aTitle = _('Merging patients: success'),
			cancel_button = False
		)
		if doit:
			if not isinstance(patient2keep, gmPerson.gmCurrentPatient):
				wx.CallAfter(set_active_patient, patient = patient2keep)

		if self.IsModal():
			self.EndModal(wx.ID_OK)
		else:
			self.Close()
#============================================================
from Gnumed.wxGladeWidgets import wxgSelectPersonFromListDlg

class cSelectPersonFromListDlg(wxgSelectPersonFromListDlg.wxgSelectPersonFromListDlg):

	def __init__(self, *args, **kwargs):
		wxgSelectPersonFromListDlg.wxgSelectPersonFromListDlg.__init__(self, *args, **kwargs)

		self.__cols = [
			_('Title'),
			_('Lastname'),
			_('Firstname'),
			_('Nickname'),
			_('DOB'),
			_('Gender'),
			_('last visit'),
			_('found via')
		]
		self.__init_ui()
	#--------------------------------------------------------
	def __init_ui(self):
		for col in range(len(self.__cols)):
			self._LCTRL_persons.InsertColumn(col, self.__cols[col])
	#--------------------------------------------------------
	def set_persons(self, persons=None):
		self._LCTRL_persons.DeleteAllItems()

		pos = len(persons) + 1
		if pos == 1:
			return False

		for person in persons:
			row_num = self._LCTRL_persons.InsertStringItem(pos, label = gmTools.coalesce(person['title'], ''))
			self._LCTRL_persons.SetStringItem(index = row_num, col = 1, label = person['lastnames'])
			self._LCTRL_persons.SetStringItem(index = row_num, col = 2, label = person['firstnames'])
			self._LCTRL_persons.SetStringItem(index = row_num, col = 3, label = gmTools.coalesce(person['preferred'], ''))
			self._LCTRL_persons.SetStringItem(index = row_num, col = 4, label = person.get_formatted_dob(format = '%Y %b %d', encoding = gmI18N.get_encoding()))
			self._LCTRL_persons.SetStringItem(index = row_num, col = 5, label = gmTools.coalesce(person['l10n_gender'], '?'))
			label = u''
			if person.is_patient:
				enc = person.get_last_encounter()
				if enc is not None:
					label = u'%s (%s)' % (gmDateTime.pydt_strftime(enc['started'], '%Y %b %d'), enc['l10n_type'])
			self._LCTRL_persons.SetStringItem(index = row_num, col = 6, label = label)
			try:
				self._LCTRL_persons.SetStringItem(index = row_num, col = 7, label = person['match_type'])
			except KeyError:
				_log.warning('cannot set match_type field')
				self._LCTRL_persons.SetStringItem(index = row_num, col = 7, label = u'??')

		for col in range(len(self.__cols)):
			self._LCTRL_persons.SetColumnWidth(col=col, width=wx.LIST_AUTOSIZE)

		self._BTN_select.Enable(False)
		self._LCTRL_persons.SetFocus()
		self._LCTRL_persons.Select(0)

		self._LCTRL_persons.set_data(data=persons)
	#--------------------------------------------------------
	def get_selected_person(self):
		return self._LCTRL_persons.get_item_data(self._LCTRL_persons.GetFirstSelected())
	#--------------------------------------------------------
	# event handlers
	#--------------------------------------------------------
	def _on_list_item_selected(self, evt):
		self._BTN_select.Enable(True)
		return
	#--------------------------------------------------------
	def _on_list_item_activated(self, evt):
		self._BTN_select.Enable(True)
		if self.IsModal():
			self.EndModal(wx.ID_OK)
		else:
			self.Close()
#============================================================
from Gnumed.wxGladeWidgets import wxgSelectPersonDTOFromListDlg

class cSelectPersonDTOFromListDlg(wxgSelectPersonDTOFromListDlg.wxgSelectPersonDTOFromListDlg):

	def __init__(self, *args, **kwargs):
		wxgSelectPersonDTOFromListDlg.wxgSelectPersonDTOFromListDlg.__init__(self, *args, **kwargs)

		self.__cols = [
			_('Source'),
			_('Lastname'),
			_('Firstname'),
			_('DOB'),
			_('Gender')
		]
		self.__init_ui()
	#--------------------------------------------------------
	def __init_ui(self):
		for col in range(len(self.__cols)):
			self._LCTRL_persons.InsertColumn(col, self.__cols[col])
	#--------------------------------------------------------
	def set_dtos(self, dtos=None):
		self._LCTRL_persons.DeleteAllItems()

		pos = len(dtos) + 1
		if pos == 1:
			return False

		for rec in dtos:
			row_num = self._LCTRL_persons.InsertStringItem(pos, label = rec['source'])
			dto = rec['dto']
			self._LCTRL_persons.SetStringItem(index = row_num, col = 1, label = dto.lastnames)
			self._LCTRL_persons.SetStringItem(index = row_num, col = 2, label = dto.firstnames)
			if dto.dob is None:
				self._LCTRL_persons.SetStringItem(index = row_num, col = 3, label = u'')
			else:
				self._LCTRL_persons.SetStringItem(index = row_num, col = 3, label = gmDateTime.pydt_strftime(dto.dob, '%Y %b %d'))
			self._LCTRL_persons.SetStringItem(index = row_num, col = 4, label = gmTools.coalesce(dto.gender, ''))

		for col in range(len(self.__cols)):
			self._LCTRL_persons.SetColumnWidth(col=col, width=wx.LIST_AUTOSIZE)

		self._BTN_select.Enable(False)
		self._LCTRL_persons.SetFocus()
		self._LCTRL_persons.Select(0)

		self._LCTRL_persons.set_data(data=dtos)
	#--------------------------------------------------------
	def get_selected_dto(self):
		return self._LCTRL_persons.get_item_data(self._LCTRL_persons.GetFirstSelected())
	#--------------------------------------------------------
	# event handlers
	#--------------------------------------------------------
	def _on_list_item_selected(self, evt):
		self._BTN_select.Enable(True)
		return
	#--------------------------------------------------------
	def _on_list_item_activated(self, evt):
		self._BTN_select.Enable(True)
		if self.IsModal():
			self.EndModal(wx.ID_OK)
		else:
			self.Close()

#============================================================
def load_persons_from_ca_msva():

	group = u'CA Medical Manager MSVA'

	src_order = [
		('explicit', 'append'),
		('workbase', 'append'),
		('local', 'append'),
		('user', 'append'),
		('system', 'append')
	]
	msva_files = _cfg.get (
		group = group,
		option = 'filename',
		source_order = src_order
	)
	if msva_files is None:
		return []

	dtos = []
	for msva_file in msva_files:
		try:
			# FIXME: potentially return several persons per file
			msva_dtos = gmCA_MSVA.read_persons_from_msva_file(filename = msva_file)
		except StandardError:
			gmGuiHelpers.gm_show_error (
				_(
				'Cannot load patient from Medical Manager MSVA file\n\n'
				' [%s]'
				) % msva_file,
				_('Activating MSVA patient')
			)
			_log.exception('cannot read patient from MSVA file [%s]' % msva_file)
			continue

		dtos.extend([ {'dto': dto, 'source': dto.source} for dto in msva_dtos ])
		#dtos.extend([ {'dto': dto} for dto in msva_dtos ])

	return dtos

#============================================================

def load_persons_from_xdt():

	bdt_files = []

	# some can be auto-detected
	# MCS/Isynet: $DRIVE:\Winacs\TEMP\BDTxx.tmp where xx is the workplace
	candidates = []
	drives = 'cdefghijklmnopqrstuvwxyz'
	for drive in drives:
		candidate = drive + ':\Winacs\TEMP\BDT*.tmp'
		candidates.extend(glob.glob(candidate))
	for candidate in candidates:
		path, filename = os.path.split(candidate)
		# FIXME: add encoding !
		bdt_files.append({'file': candidate, 'source': 'MCS/Isynet %s' % filename[-6:-4]})

	# some need to be configured
	# aggregate sources
	src_order = [
		('explicit', 'return'),
		('workbase', 'append'),
		('local', 'append'),
		('user', 'append'),
		('system', 'append')
	]
	xdt_profiles = _cfg.get (
		group = 'workplace',
		option = 'XDT profiles',
		source_order = src_order
	)
	if xdt_profiles is None:
		return []

	# first come first serve
	src_order = [
		('explicit', 'return'),
		('workbase', 'return'),
		('local', 'return'),
		('user', 'return'),
		('system', 'return')
	]
	for profile in xdt_profiles:
		name = _cfg.get (
			group = 'XDT profile %s' % profile,
			option = 'filename',
			source_order = src_order
		)
		if name is None:
			_log.error('XDT profile [%s] does not define a <filename>' % profile)
			continue
		encoding = _cfg.get (
			group = 'XDT profile %s' % profile,
			option = 'encoding',
			source_order = src_order
		)
		if encoding is None:
			_log.warning('xDT source profile [%s] does not specify an <encoding> for BDT file [%s]' % (profile, name))
		source = _cfg.get (
			group = 'XDT profile %s' % profile,
			option = 'source',
			source_order = src_order
		)
		dob_format = _cfg.get (
			group = 'XDT profile %s' % profile,
			option = 'DOB format',
			source_order = src_order
		)
		if dob_format is None:
			_log.warning('XDT profile [%s] does not define a date of birth format in <DOB format>' % profile)
		bdt_files.append({'file': name, 'source': source, 'encoding': encoding, 'dob_format': dob_format})

	dtos = []
	for bdt_file in bdt_files:
		try:
			# FIXME: potentially return several persons per file
			dto = gmPerson.get_person_from_xdt (
				filename = bdt_file['file'],
				encoding = bdt_file['encoding'],
				dob_format = bdt_file['dob_format']
			)

		except IOError:
			gmGuiHelpers.gm_show_info (
				_(
				'Cannot access BDT file\n\n'
				' [%s]\n\n'
				'to import patient.\n\n'
				'Please check your configuration.'
				) % bdt_file,
				_('Activating xDT patient')
			)
			_log.exception('cannot access xDT file [%s]' % bdt_file['file'])
			continue
		except:
			gmGuiHelpers.gm_show_error (
				_(
				'Cannot load patient from BDT file\n\n'
				' [%s]'
				) % bdt_file,
				_('Activating xDT patient')
			)
			_log.exception('cannot read patient from xDT file [%s]' % bdt_file['file'])
			continue

		dtos.append({'dto': dto, 'source': gmTools.coalesce(bdt_file['source'], dto.source)})

	return dtos

#============================================================

def load_persons_from_pracsoft_au():

	pracsoft_files = []

	# try detecting PATIENTS.IN files
	candidates = []
	drives = 'cdefghijklmnopqrstuvwxyz'
	for drive in drives:
		candidate = drive + ':\MDW2\PATIENTS.IN'
		candidates.extend(glob.glob(candidate))
	for candidate in candidates:
		drive, filename = os.path.splitdrive(candidate)
		pracsoft_files.append({'file': candidate, 'source': 'PracSoft (AU): drive %s' % drive})

	# add configured one(s)
	src_order = [
		('explicit', 'append'),
		('workbase', 'append'),
		('local', 'append'),
		('user', 'append'),
		('system', 'append')
	]
	fnames = _cfg.get (
		group = 'AU PracSoft PATIENTS.IN',
		option = 'filename',
		source_order = src_order
	)

	src_order = [
		('explicit', 'return'),
		('user', 'return'),
		('system', 'return'),
		('local', 'return'),
		('workbase', 'return')
	]
	source = _cfg.get (
		group = 'AU PracSoft PATIENTS.IN',
		option = 'source',
		source_order = src_order
	)

	if source is not None:
		for fname in fnames:
			fname = os.path.abspath(os.path.expanduser(fname))
			if os.access(fname, os.R_OK):
				pracsoft_files.append({'file': os.path.expanduser(fname), 'source': source})
			else:
				_log.error('cannot read [%s] in AU PracSoft profile' % fname)

	# and parse them
	dtos = []
	for pracsoft_file in pracsoft_files:
		try:
			tmp = gmPerson.get_persons_from_pracsoft_file(filename = pracsoft_file['file'])
		except:
			_log.exception('cannot parse PracSoft file [%s]' % pracsoft_file['file'])
			continue
		for dto in tmp:
			dtos.append({'dto': dto, 'source': pracsoft_file['source']})

	return dtos
#============================================================
def load_persons_from_kvks():

	dbcfg = gmCfg.cCfgSQL()
	kvk_dir = os.path.abspath(os.path.expanduser(dbcfg.get2 (
		option = 'DE.KVK.spool_dir',
		workplace = gmSurgery.gmCurrentPractice().active_workplace,
		bias = 'workplace',
		default = u'/var/spool/kvkd/'
	)))
	dtos = []
	for dto in gmKVK.get_available_kvks_as_dtos(spool_dir = kvk_dir):
		dtos.append({'dto': dto, 'source': 'KVK'})

	return dtos
#============================================================
def get_person_from_external_sources(parent=None, search_immediately=False, activate_immediately=False):
	"""Load patient from external source.

	- scan external sources for candidates
	- let user select source
	  - if > 1 available: always
	  - if only 1 available: depending on search_immediately
	- search for patients matching info from external source
	- if more than one match:
	  - let user select patient
	- if no match:
	  - create patient
	- activate patient
	"""
	# get DTOs from interfaces
	dtos = []
	dtos.extend(load_persons_from_xdt())
	dtos.extend(load_persons_from_pracsoft_au())
	dtos.extend(load_persons_from_kvks())
	dtos.extend(load_persons_from_ca_msva())

	# no external persons
	if len(dtos) == 0:
		gmDispatcher.send(signal='statustext', msg=_('No patients found in external sources.'))
		return None

	# one external patient with DOB - already active ?
	if (len(dtos) == 1) and (dtos[0]['dto'].dob is not None):
		dto = dtos[0]['dto']
		# is it already the current patient ?
		curr_pat = gmPerson.gmCurrentPatient()
		if curr_pat.connected:
			key_dto = dto.firstnames + dto.lastnames + dto.dob.strftime('%Y-%m-%d') + dto.gender
			names = curr_pat.get_active_name()
			key_pat = names['firstnames'] + names['lastnames'] + curr_pat.get_formatted_dob(format = '%Y-%m-%d') + curr_pat['gender']
			_log.debug('current patient: %s' % key_pat)
			_log.debug('dto patient    : %s' % key_dto)
			if key_dto == key_pat:
				gmDispatcher.send(signal='statustext', msg=_('The only external patient is already active in GNUmed.'), beep=False)
				return None

	# one external person - look for internal match immediately ?
	if (len(dtos) == 1) and search_immediately:
		dto = dtos[0]['dto']

	# several external persons
	else:
		if parent is None:
			parent = wx.GetApp().GetTopWindow()
		dlg = cSelectPersonDTOFromListDlg(parent=parent, id=-1)
		dlg.set_dtos(dtos=dtos)
		result = dlg.ShowModal()
		if result == wx.ID_CANCEL:
			return None
		dto = dlg.get_selected_dto()['dto']
		dlg.Destroy()

	# search
	idents = dto.get_candidate_identities(can_create=True)
	if idents is None:
		gmGuiHelpers.gm_show_info (_(
			'Cannot create new patient:\n\n'
			' [%s %s (%s), %s]'
			) % (
				dto.firstnames, dto.lastnames, dto.gender, gmDateTime.pydt_strftime(dto.dob, '%Y %b %d')
			),
			_('Activating external patient')
		)
		return None

	if len(idents) == 1:
		ident = idents[0]

	if len(idents) > 1:
		if parent is None:
			parent = wx.GetApp().GetTopWindow()
		dlg = cSelectPersonFromListDlg(parent=parent, id=-1)
		dlg.set_persons(persons=idents)
		result = dlg.ShowModal()
		if result == wx.ID_CANCEL:
			return None
		ident = dlg.get_selected_person()
		dlg.Destroy()

	if activate_immediately:
		if not set_active_patient(patient = ident):
			gmGuiHelpers.gm_show_info (_(
				'Cannot activate patient:\n\n'
				'%s %s (%s)\n'
				'%s'
				) % (
					dto.firstnames, dto.lastnames, dto.gender, gmDateTime.pydt_strftime(dto.dob, '%Y %b %d')
				),
				_('Activating external patient')
			)
			return None

	dto.import_extra_data(identity = ident)
	dto.delete_from_source()

	return ident
#============================================================
class cPersonSearchCtrl(wx.TextCtrl):
	"""Widget for smart search for persons."""

	def __init__(self, *args, **kwargs):

		try:
			kwargs['style'] = kwargs['style'] | wx.TE_PROCESS_ENTER
		except KeyError:
			kwargs['style'] = wx.TE_PROCESS_ENTER

		# need to explicitly process ENTER events to avoid
		# them being handed over to the next control
		wx.TextCtrl.__init__(self, *args, **kwargs)

		self.person = None

		self._tt_search_hints = _(
			'To search for a person, type any of:                   \n'
			'\n'
			' - fragment(s) of last and/or first name(s)\n'
			" - GNUmed ID of person (can start with '#')\n"
			' - any external ID of person\n'
			" - date of birth (can start with '$' or '*')\n"
			'\n'
			'and hit <ENTER>.\n'
			'\n'
			'Shortcuts:\n'
			' <F2>\n'
			'  - scan external sources for persons\n'
			' <CURSOR-UP>\n'
			'  - recall most recently used search term\n'
			' <CURSOR-DOWN>\n'
			'  - list 10 most recently found persons\n'
		)
		self.SetToolTipString(self._tt_search_hints)

		# FIXME: set query generator
		self.__person_searcher = gmPersonSearch.cPatientSearcher_SQL()

		self._prev_search_term = None
		self.__prev_idents = []
		self._lclick_count = 0

		self.__register_events()
	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def _set_person(self, person):
		self.__person = person
		wx.CallAfter(self._display_name)

	def _get_person(self):
		return self.__person

	person = property(_get_person, _set_person)
	#--------------------------------------------------------
	# utility methods
	#--------------------------------------------------------
	def _display_name(self):
		name = u''

		if self.person is not None:
			name = self.person['description']

		self.SetValue(name)
	#--------------------------------------------------------
	def _remember_ident(self, ident=None):

		if not isinstance(ident, gmPerson.cIdentity):
			return False

		# only unique identities
		for known_ident in self.__prev_idents:
			if known_ident['pk_identity'] == ident['pk_identity']:
				return True

		self.__prev_idents.append(ident)

		# and only 10 of them
		if len(self.__prev_idents) > 10:
			self.__prev_idents.pop(0)

		return True
	#--------------------------------------------------------
	# event handling
	#--------------------------------------------------------
	def __register_events(self):
		wx.EVT_CHAR(self, self.__on_char)
		wx.EVT_SET_FOCUS(self, self._on_get_focus)
		wx.EVT_KILL_FOCUS (self, self._on_loose_focus)
		wx.EVT_TEXT_ENTER (self, self.GetId(), self.__on_enter)
	#--------------------------------------------------------
	def _on_get_focus(self, evt):
		"""upon tabbing in

		- select all text in the field so that the next
		  character typed will delete it
		"""
		wx.CallAfter(self.SetSelection, -1, -1)
		evt.Skip()
	#--------------------------------------------------------
	def _on_loose_focus(self, evt):
		# - redraw the currently active name upon losing focus
		#
		# if we use wx.EVT_KILL_FOCUS we will also receive this event
		# when closing our application or loosing focus to another
		# application which is NOT what we intend to achieve,
		# however, this is the least ugly way of doing this due to
		# certain vagaries of wxPython (see the Wiki)
		evt.Skip()
		wx.CallAfter(self.__on_lost_focus)
	#--------------------------------------------------------
	def __on_lost_focus(self):
		# just for good measure
		self.SetSelection(0, 0)
		self._display_name()
		self._remember_ident(self.person)
	#--------------------------------------------------------
	def __on_char(self, evt):
		self._on_char(evt)

	def _on_char(self, evt):
		"""True: patient was selected.
		   False: no patient was selected.
		"""
		keycode = evt.GetKeyCode()

		# list of previously active patients
		if keycode == wx.WXK_DOWN:
			evt.Skip()
			if len(self.__prev_idents) == 0:
				return False

			dlg = cSelectPersonFromListDlg(parent = wx.GetTopLevelParent(self), id = -1)
			dlg.set_persons(persons = self.__prev_idents)
			result = dlg.ShowModal()
			if result == wx.ID_OK:
				wx.BeginBusyCursor()
				self.person = dlg.get_selected_person()
				dlg.Destroy()
				wx.EndBusyCursor()
				return True

			dlg.Destroy()
			return False

		# recall previous search fragment
		if keycode == wx.WXK_UP:
			evt.Skip()
			# FIXME: cycling through previous fragments
			if self._prev_search_term is not None:
				self.SetValue(self._prev_search_term)
			return False

		# invoke external patient sources
		if keycode == wx.WXK_F2:
			evt.Skip()
			dbcfg = gmCfg.cCfgSQL()
			search_immediately = bool(dbcfg.get2 (
				option = 'patient_search.external_sources.immediately_search_if_single_source',
				workplace = gmSurgery.gmCurrentPractice().active_workplace,
				bias = 'user',
				default = 0
			))
			p = get_person_from_external_sources (
				parent = wx.GetTopLevelParent(self),
				search_immediately = search_immediately
			)
			if p is not None:
				self.person = p
				return True
			return False

		# FIXME: invoke add new person
		# FIXME: add popup menu apart from system one

		evt.Skip()
	#--------------------------------------------------------
	def __on_enter(self, evt):
		"""This is called from the ENTER handler."""

		# ENTER but no search term ?
		curr_search_term = self.GetValue().strip()
		if curr_search_term == '':
			return None

		# same person anywys ?
		if self.person is not None:
			if curr_search_term == self.person['description']:
				return None

		# remember search fragment
		if self.IsModified():
			self._prev_search_term = curr_search_term

		self._on_enter(search_term = curr_search_term)
	#--------------------------------------------------------
	def _on_enter(self, search_term=None):
		"""This can be overridden in child classes."""

		wx.BeginBusyCursor()

		# get list of matching ids
		idents = self.__person_searcher.get_identities(search_term)

		if idents is None:
			wx.EndBusyCursor()
			gmGuiHelpers.gm_show_info (
				_('Error searching for matching persons.\n\n'
				  'Search term: "%s"'
				) % search_term,
				_('selecting person')
			)
			return None

		_log.info("%s matching person(s) found", len(idents))

		if len(idents) == 0:
			wx.EndBusyCursor()

			dlg = gmGuiHelpers.c2ButtonQuestionDlg (
				wx.GetTopLevelParent(self),
				-1,
				caption = _('Selecting patient'),
				question = _(
					'Cannot find any matching patients for the search term\n\n'
					' "%s"\n\n'
					'You may want to try a shorter search term.\n'
				) % search_term,
				button_defs = [
					{'label': _('Go back'), 'tooltip': _('Go back and search again.'), 'default': True},
					{'label': _('Create new'), 'tooltip': _('Create new patient.')}
				]
			)
			if dlg.ShowModal() != wx.ID_NO:
				return

			success = create_new_person(activate = True)
			if success:
				self.person = gmPerson.gmCurrentPatient()
			else:
				self.person = None
			return None

		# only one matching identity
		if len(idents) == 1:
			self.person = idents[0]
			wx.EndBusyCursor()
			return None

		# more than one matching identity: let user select from pick list
		dlg = cSelectPersonFromListDlg(parent=wx.GetTopLevelParent(self), id=-1)
		dlg.set_persons(persons=idents)
		wx.EndBusyCursor()
		result = dlg.ShowModal()
		if result == wx.ID_CANCEL:
			dlg.Destroy()
			return None

		wx.BeginBusyCursor()
		self.person = dlg.get_selected_person()
		dlg.Destroy()
		wx.EndBusyCursor()

		return None
#============================================================
def _check_has_dob(patient=None):

	if patient is None:
		return

	if patient['dob'] is None:
		gmGuiHelpers.gm_show_warning (
			aTitle = _('Checking date of birth'),
			aMessage = _(
				'\n'
				' %s\n'
				'\n'
				'The date of birth for this patient is not known !\n'
				'\n'
				'You can proceed to work on the patient but\n'
				'GNUmed will be unable to assist you with\n'
				'age-related decisions.\n'
			) % patient['description_gender']
		)

	return
#------------------------------------------------------------
def _check_for_provider_chart_access(patient=None):

	if patient is None:
		return True

	curr_prov = gmStaff.gmCurrentProvider()

	# can view my own chart
	if patient.ID == curr_prov['pk_identity']:
		return True

	if patient.ID not in [ s['pk_identity'] for s in gmStaff.get_staff_list() ]:
		return True

	proceed = gmGuiHelpers.gm_show_question (
		aTitle = _('Privacy check'),
		aMessage = _(
			'You have selected the chart of a member of staff,\n'
			'for whom privacy is especially important:\n'
			'\n'
			'  %s, %s\n'
			'\n'
			'This may be OK depending on circumstances.\n'
			'\n'
			'Please be aware that accessing patient charts is\n'
			'logged and that %s%s will be\n'
			'notified of the access if you choose to proceed.\n'
			'\n'
			'Are you sure you want to draw this chart ?'
		) % (
			patient.get_description_gender(),
			patient.get_formatted_dob(),
			gmTools.coalesce(patient['title'], u'', u'%s '),
			patient['lastnames']
		)
	)

	if proceed:
		prov = u'%s (%s%s %s)' % (
			curr_prov['short_alias'],
			gmTools.coalesce(curr_prov['title'], u'', u'%s '),
			curr_prov['firstnames'],
			curr_prov['lastnames']
		)
		pat = u'%s%s %s' % (
			gmTools.coalesce(patient['title'], u'', u'%s '),
			patient['firstnames'],
			patient['lastnames']
		)
		# notify the staff member
		gmProviderInbox.create_inbox_message (
			staff = patient.staff_id,
			message_type = _('Privacy notice'),
			subject = _('Your chart has been accessed by %s.') % prov,
			patient = patient.ID
		)
		# notify /me about the staff member notification
		gmProviderInbox.create_inbox_message (
			staff = curr_prov['pk_staff'],
			message_type = _('Privacy notice'),
			subject = _('Staff member %s has been notified of your chart access.') % pat
		)

	return proceed
#------------------------------------------------------------
def _check_birthday(patient=None):

	if patient['dob'] is None:
		return

	dbcfg = gmCfg.cCfgSQL()
	dob_distance = dbcfg.get2 (
		option = u'patient_search.dob_warn_interval',
		workplace = gmSurgery.gmCurrentPractice().active_workplace,
		bias = u'user',
		default = u'1 week'
	)

	if not patient.dob_in_range(dob_distance, dob_distance):
		return

	now = gmDateTime.pydt_now_here()
	enc = gmI18N.get_encoding()
	msg = _('%(pat)s turns %(age)s on %(month)s %(day)s ! (today is %(month_now)s %(day_now)s)') % {
		'pat': patient.get_description_gender(),
		'age': patient.get_medical_age().strip('y'),
		'month': patient.get_formatted_dob(format = '%B', encoding = enc),
		'day': patient.get_formatted_dob(format = '%d', encoding = enc),
		'month_now': gmDateTime.pydt_strftime(now, '%B', enc, gmDateTime.acc_months),
		'day_now': gmDateTime.pydt_strftime(now, '%d', enc, gmDateTime.acc_days)
	}
	gmDispatcher.send(signal = 'statustext', msg = msg)
#------------------------------------------------------------
def set_active_patient(patient=None, forced_reload=False):

	if isinstance(patient, gmPerson.cPatient):
		pass
	elif isinstance(patient, gmPerson.cIdentity):
		patient = gmPerson.cPatient(aPK_obj = patient['pk_identity'])
#	elif isinstance(patient, cStaff):
#		patient = cPatient(aPK_obj=patient['pk_identity'])
	elif isinstance(patient, gmPerson.gmCurrentPatient):
		patient = patient.patient
	elif patient == -1:
		pass
	else:
		# maybe integer ?
		success, pk = gmTools.input2int(initial = patient, minval = 1)
		if not success:
			raise ValueError('<patient> must be either -1, >0, or a cPatient, cIdentity or gmCurrentPatient instance, is: %s' % patient)
		# but also valid patient ID ?
		try:
			patient = gmPerson.cPatient(aPK_obj = pk)
		except:
			_log.exception('error changing active patient to [%s]' % patient)
			return False

	_check_has_dob(patient = patient)

	if not _check_for_provider_chart_access(patient = patient):
		return False

	success = gmPerson.set_active_patient(patient = patient, forced_reload = forced_reload)

	if not success:
		return False

	_check_birthday(patient = patient)

	return True
#------------------------------------------------------------
class cActivePatientSelector(cPersonSearchCtrl):

	def __init__ (self, *args, **kwargs):

		cPersonSearchCtrl.__init__(self, *args, **kwargs)

		# get configuration
		cfg = gmCfg.cCfgSQL()

		self.__always_dismiss_on_search = bool ( 
			cfg.get2 (
				option = 'patient_search.always_dismiss_previous_patient',
				workplace = gmSurgery.gmCurrentPractice().active_workplace,
				bias = 'user',
				default = 0
			)
		)

		self.__always_reload_after_search = bool (
			cfg.get2 (
				option = 'patient_search.always_reload_new_patient',
				workplace = gmSurgery.gmCurrentPractice().active_workplace,
				bias = 'user',
				default = 0
			)
		)

		self.__register_events()
	#--------------------------------------------------------
	# utility methods
	#--------------------------------------------------------
	def _display_name(self):

		curr_pat = gmPerson.gmCurrentPatient()
		if curr_pat.connected:
			name = curr_pat['description']
			if curr_pat.locked:
				name = _('%(name)s (locked)') % {'name': name}
		else:
			if curr_pat.locked:
				name = _('<patient search locked>')
			else:
				name = _('<type here to search patient>')

		self.SetValue(name)

		# adjust tooltip
		if self.person is None:
			self.SetToolTipString(self._tt_search_hints)
			return

		if (self.person['emergency_contact'] is None) and (self.person['comment'] is None):
			separator = u''
		else:
			separator = u'%s\n' % (gmTools.u_box_horiz_single * 40)

		tt = u'%s%s%s%s' % (
			gmTools.coalesce(self.person['emergency_contact'], u'', u'%s\n %%s\n' % _('In case of emergency contact:')),
			gmTools.coalesce(self.person['comment'], u'', u'\n%s\n'),
			separator,
			self._tt_search_hints
		)
		self.SetToolTipString(tt)
	#--------------------------------------------------------
	def _set_person_as_active_patient(self, pat):
		if not set_active_patient(patient=pat, forced_reload = self.__always_reload_after_search):
			_log.error('cannot change active patient')
			return None

		self._remember_ident(pat)

		return True
	#--------------------------------------------------------
	# event handling
	#--------------------------------------------------------
	def __register_events(self):
		# client internal signals
		gmDispatcher.connect(signal = u'post_patient_selection', receiver = self._on_post_patient_selection)
		gmDispatcher.connect(signal = u'name_mod_db', receiver = self._on_name_identity_change)
		gmDispatcher.connect(signal = u'identity_mod_db', receiver = self._on_name_identity_change)

		gmDispatcher.connect(signal = 'patient_locked', receiver = self._on_post_patient_selection)
		gmDispatcher.connect(signal = 'patient_unlocked', receiver = self._on_post_patient_selection)
	#----------------------------------------------
	def _on_name_identity_change(self, **kwargs):
		wx.CallAfter(self._display_name)
	#----------------------------------------------
	def _on_post_patient_selection(self, **kwargs):
		if gmPerson.gmCurrentPatient().connected:
			self.person = gmPerson.gmCurrentPatient().patient
		else:
			self.person = None
	#----------------------------------------------
	def _on_enter(self, search_term = None):

		if self.__always_dismiss_on_search:
			_log.warning("dismissing patient before patient search")
			self._set_person_as_active_patient(-1)

		super(self.__class__, self)._on_enter(search_term=search_term)

		if self.person is None:
			return

		self._set_person_as_active_patient(self.person)
	#----------------------------------------------
	def _on_char(self, evt):

		success = super(self.__class__, self)._on_char(evt)
		if success:
			self._set_person_as_active_patient(self.person)

#============================================================
# main
#------------------------------------------------------------
if __name__ == "__main__":

	if len(sys.argv) > 1:
		if sys.argv[1] == 'test':
			gmI18N.activate_locale()
			gmI18N.install_domain()

			app = wx.PyWidgetTester(size = (200, 40))
#			app.SetWidget(cSelectPersonFromListDlg, -1)
			app.SetWidget(cPersonSearchCtrl, -1)
#			app.SetWidget(cActivePatientSelector, -1)
			app.MainLoop()

#============================================================
# docs
#------------------------------------------------------------
# functionality
# -------------
# - hitting ENTER on non-empty field (and more than threshold chars)
#   - start search
#   - display results in a list, prefixed with numbers
#   - last name
#   - first name
#   - gender
#   - age
#   - city + street (no ZIP, no number)
#   - last visit (highlighted if within a certain interval)
#   - arbitrary marker (e.g. office attendance this quartal, missing KVK, appointments, due dates)
#   - if none found -> go to entry of new patient
#   - scrolling in this list
#   - ENTER selects patient
#   - ESC cancels selection
#   - number selects patient
#
# - hitting cursor-up/-down
#   - cycle through history of last 10 search fragments
#
# - hitting alt-L = List, alt-P = previous
#   - show list of previous ten patients prefixed with numbers
#   - scrolling in list
#   - ENTER selects patient
#   - ESC cancels selection
#   - number selects patient
#
# - hitting ALT-N
#   - immediately goes to entry of new patient
#
# - hitting cursor-right in a patient selection list
#   - pops up more detail about the patient
#   - ESC/cursor-left goes back to list
#
# - hitting TAB
#   - makes sure the currently active patient is displayed

#------------------------------------------------------------
# samples
# -------
# working:
#  Ian Haywood
#  Haywood Ian
#  Haywood
#  Amador Jimenez (yes, two last names but no hyphen: Spain, for example)
#  Ian Haywood 19/12/1977
#  19/12/1977
#  19-12-1977
#  19.12.1977
#  19771219
#  $dob
#  *dob
#  #ID
#  ID
#  HIlbert, karsten
#  karsten, hilbert
#  kars, hilb
#
# non-working:
#  Haywood, Ian <40
#  ?, Ian 1977
#  Ian Haywood, 19/12/77
#  PUPIC
# "hilb; karsten, 23.10.74"

#------------------------------------------------------------
# notes
# -----
# >> 3. There are countries in which people have more than one
# >> (significant) lastname (spanish-speaking countries are one case :), some
# >> asian countries might be another one).
# -> we need per-country query generators ...

# search case sensitive by default, switch to insensitive if not found ?

# accent insensitive search:
#  select * from * where to_ascii(column, 'encoding') like '%test%';
# may not work with Unicode

# phrase wheel is most likely too slow

# extend search fragment history

# ask user whether to send off level 3 queries - or thread them

# we don't expect patient IDs in complicated patterns, hence any digits signify a date

# FIXME: make list window fit list size ...

# clear search field upon get-focus ?

# F1 -> context help with hotkey listing

# th -> th|t
# v/f/ph -> f|v|ph
# maybe don't do umlaut translation in the first 2-3 letters
# such that not to defeat index use for the first level query ?

# user defined function key to start search

