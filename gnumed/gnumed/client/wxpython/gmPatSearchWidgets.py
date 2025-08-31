#  coding: latin-1
"""GNUmed quick person search widgets.

This widget allows to search for persons based on the
criteria name, date of birth and person ID. It goes to
considerable lengths to understand the user's intent from
her input. For that to work well we need per-culture
query generators. However, there's always the fallback
generator.
"""
#============================================================
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = 'GPL v2 or later (for details see https://www.gnu.org/)'

import sys
import os.path
import glob
import logging


import wx


if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x
else:
	try: _		# do we already have _() ?
	except NameError:
		from Gnumed.pycommon import gmI18N
		gmI18N.activate_locale()
		gmI18N.install_domain()
from Gnumed.pycommon import gmDispatcher
from Gnumed.pycommon import gmDateTime
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmCfgDB
from Gnumed.pycommon import gmCfgINI
from Gnumed.pycommon import gmNetworkTools

from Gnumed.business import gmPerson
from Gnumed.business import gmStaff
from Gnumed.business import gmKVK
from Gnumed.business import gmPraxis
from Gnumed.business import gmCA_MSVA
from Gnumed.business import gmPersonSearch
from Gnumed.business import gmProviderInbox

from Gnumed.wxpython import gmGuiHelpers
from Gnumed.wxpython import gmAuthWidgets
from Gnumed.wxpython.gmPersonCreationWidgets import create_new_person


_log = logging.getLogger('gm.person')

_cfg = gmCfgINI.gmCfgData()

ID_PatPickList = wx.NewId()
ID_BTN_AddNew = wx.NewId()

#============================================================
def merge_patients(parent=None):
	dlg = cMergePatientsDlg(parent, -1)
	return dlg.ShowModal()

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
			gmDispatcher.send(signal = 'statustext', msg = _('No patient selected on the left.'), beep = True)
			return

		if self._TCTRL_patient2.person is None:
			gmDispatcher.send(signal = 'statustext', msg = _('No patient selected on the right.'), beep = True)
			return

		if self._RBTN_patient1.GetValue():
			patient2keep = self._TCTRL_patient1.person
			patient2merge = self._TCTRL_patient2.person
		else:
			patient2keep = self._TCTRL_patient2.person
			patient2merge = self._TCTRL_patient1.person

		if patient2merge['lastnames'] == 'Kirk':
			if _cfg.get(option = 'debug'):
				gmNetworkTools.open_url_in_browser(url = 'https://en.wikipedia.org/wiki/File:Picard_as_Locutus.jpg')
				gmGuiHelpers.gm_show_info(_('\n\nYou will be assimilated.\n\n'), _('The Borg'))
				return
			else:
				gmDispatcher.send(signal = 'statustext', msg = _('Cannot merge Kirk into another patient.'), beep = True)
				return

		doit = gmGuiHelpers.gm_show_question (
			question = _(
				'Are you positively sure you want to merge patient\n\n'
				' #%s: %s (%s, %s)\n\n'
				'into patient\n\n'
				' #%s: %s (%s, %s) ?\n\n'
				'Note that this action can ONLY be reversed by a laborious\n'
				'manual process requiring in-depth knowledge about databases\n'
				'and the patients in question !\n'
			) % (
				patient2merge.ID,
				patient2merge.description_gender,
				patient2merge['gender'],
				patient2merge.get_formatted_dob(format = '%Y %b %d'),
				patient2keep.ID,
				patient2keep.description_gender,
				patient2keep['gender'],
				patient2keep.get_formatted_dob(format = '%Y %b %d')
			),
			title = _('Merging patients: confirmation'),
			cancel_button = False
		)
		if not doit:
			return

		conn = gmAuthWidgets.get_dbowner_connection(procedure = _('Merging patients'))
		if conn is None:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot merge patients without admin access.'), beep = True)
			return

		success, msg = patient2keep.assimilate_identity(other_identity = patient2merge, link_obj = conn)
		conn.close()
		if not success:
			gmDispatcher.send(signal = 'statustext', msg = msg, beep = True)
			return

		msg = _(
			'The patient\n'
			'\n'
			' #%s: %s (%s, %s)\n'
			'\n'
			'has successfully been merged into\n'
			'\n'
			' #%s: %s (%s, %s)'
		) % (
			patient2merge.ID,
			patient2merge.description_gender,
			patient2merge['gender'],
			patient2merge.get_formatted_dob(format = '%Y %b %d'),
			patient2keep.ID,
			patient2keep.description_gender,
			patient2keep['gender'],
			patient2keep.get_formatted_dob(format = '%Y %b %d')
		)
		title = _('Merging patients: success')

		curr_pat = gmPerson.gmCurrentPatient()
		# announce success
		if (curr_pat.connected) and (patient2keep.ID == curr_pat.ID):
			gmGuiHelpers.gm_show_info(info = msg, title = title)
		# and offer to activate kept patient if not active
		else:
			msg = msg + (
			'\n\n\n'
			'Do you want to activate that patient\n'
			'now for further modifications ?\n'
			)
			doit = gmGuiHelpers.gm_show_question (
				question = msg,
				title = title,
				cancel_button = False
			)
			if doit:
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
			_('Lastname'),
			_('Firstname'),
			_('DOB'),
			'%s%s' % (gmTools.u_female, gmTools.u_male),
			_('last visit'),
			_('Nickname / Comment'),
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
			row_num = self._LCTRL_persons.InsertItem(pos, gmTools.coalesce(person['title'], person['lastnames'], '%s, %%s' % person['lastnames']))
			self._LCTRL_persons.SetItem(row_num, 1, person['firstnames'])
			self._LCTRL_persons.SetItem(row_num, 2, person.get_formatted_dob(format = '%Y %b %d'))
			self._LCTRL_persons.SetItem(row_num, 3, gmTools.coalesce(person['l10n_gender'], '?'))
			label = ''
			last = person.last_contact
			if last:
				label = '%s (%s)' % (last['last_affirmed'].strftime('%Y %b %d'), last['l10n_type'])
			self._LCTRL_persons.SetItem(row_num, 4, label)
			parts = []
			if person['preferred'] is not None:
				parts.append(person['preferred'])
			if person['comment'] is not None:
				parts.append(person['comment'])
			self._LCTRL_persons.SetItem(row_num, 5, ' / '.join(parts))
			try:
				self._LCTRL_persons.SetItem(row_num, 6, person['match_type'])
			except KeyError:
				_log.warning('cannot set match_type field')
				self._LCTRL_persons.SetItem(row_num, 6, '??')

		for col in range(len(self.__cols)):
			self._LCTRL_persons.SetColumnWidth(col, wx.LIST_AUTOSIZE)

		self._BTN_select.Enable(False)
		self._LCTRL_persons.SetFocus()
		self._LCTRL_persons.Select(0)

		self._LCTRL_persons.set_data(data = persons)

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
	#--------------------------------------------------------
	def _on_new_patient_button_pressed(self, event):
		event.Skip()
		success = create_new_person(activate = True)
		if success:
			self.person = gmPerson.gmCurrentPatient()
		else:
			self.person = None
		if self.IsModal():
			self.EndModal(wx.ID_CANCEL)
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
			row_num = self._LCTRL_persons.InsertItem(pos, rec['source'])
			dto = rec['dto']
			self._LCTRL_persons.SetItem(row_num, 1, dto.lastnames)
			self._LCTRL_persons.SetItem(row_num, 2, dto.firstnames)
			if dto.dob is None:
				self._LCTRL_persons.SetItem(row_num, 3, '')
			else:
				if dto.dob_is_estimated:
					self._LCTRL_persons.SetItem(row_num, 3, gmTools.u_almost_equal_to + gmDateTime.pydt_strftime(dto.dob, '%Y %b %d'), none_str = '?')
				else:
					self._LCTRL_persons.SetItem(row_num, 3, gmDateTime.pydt_strftime(dto.dob, '%Y %b %d', none_str = '?'))
			self._LCTRL_persons.SetItem(row_num, 4, gmTools.coalesce(dto.gender, ''))

		for col in range(len(self.__cols)):
			self._LCTRL_persons.SetColumnWidth(col, wx.LIST_AUTOSIZE)

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

	group = 'CA Medical Manager MSVA'

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
		except Exception:
#			gmGuiHelpers.gm_show_error (
#				_(
#				'Cannot load patient from Medical Manager MSVA file\n\n'
#				' [%s]'
#				) % msva_file,
#				_('Activating MSVA patient')
#			)
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
		except Exception:
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
		except Exception:
			_log.exception('cannot parse PracSoft file [%s]' % pracsoft_file['file'])
			continue
		for dto in tmp:
			dtos.append({'dto': dto, 'source': pracsoft_file['source']})

	return dtos

#============================================================
def load_persons_from_kvks():
	kvk_dir = os.path.abspath(os.path.expanduser(gmCfgDB.get4workplace (
		option = 'DE.KVK.spool_dir',
		workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
		default = '/var/spool/kvkd/'
		#default = u'/home/ncq/gnumed/'
	)))
	dtos = []
	for dto in gmKVK.get_available_kvks_as_dtos(spool_dir = kvk_dir):
		dtos.append({'dto': dto, 'source': 'KVK'})
#	for dto in gmKVK.get_available_CCRdr_files_as_dtos(spool_dir = kvk_dir):
#		dtos.append({'dto': dto, 'source': dto.source})

	return dtos

#============================================================
def load_person_from_vcard_file():

	wildcards = '|'.join ([
		'%s (*.vcf)|*.vcf' % _('vcf files'),
		'%s (*.VCF)|*.VCF' % _('VCF files'),
		'%s (*)|*' % _('all files'),
		'%s (*.*)|*.*' % _('all files (Windows)')
	])

	dlg = wx.FileDialog (
		parent = wx.GetApp().GetTopWindow(),
		message = _('Choose a vCard file:'),
		defaultDir = gmTools.gmPaths().user_work_dir,
		wildcard = wildcards,
		style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
	)
	result = dlg.ShowModal()
	fname = dlg.GetPath()
	dlg.DestroyLater()
	if result == wx.ID_CANCEL:
		return

	from Gnumed.business import gmVCard
	dto = gmVCard.parse_vcard2dto(filename = fname)
	if dto is None:
		gmDispatcher.send(signal='statustext', msg=_('[%s] does not seem to contain a vCard.') % fname)
		return

	idents = dto.get_candidate_identities(can_create = True)
	if len(idents) == 1:
		ident = idents[0]
		if not set_active_patient(patient = ident):
			gmGuiHelpers.gm_show_info (_(
				'Cannot activate patient:\n\n'
				'%s %s (%s)\n'
				'%s'
				) % (
					dto.firstnames,
					dto.lastnames,
					dto.gender,
					gmDateTime.pydt_strftime(dto.dob, '%Y %b %d', none_str = '?')
				),
				_('Activating external patient')
			)
		return

	dlg = cSelectPersonFromListDlg(wx.GetApp().GetTopWindow(), -1)
	dlg.set_persons(persons = idents)
	result = dlg.ShowModal()
	ident = dlg.get_selected_person()
	dlg.DestroyLater()
	if result == wx.ID_CANCEL:
		return
	if not set_active_patient(patient = ident):
		gmGuiHelpers.gm_show_info (_(
			'Cannot activate patient:\n\n'
			'%s %s (%s)\n'
			'%s'
			) % (
				dto.firstnames,
				dto.lastnames,
				dto.gender,
				gmDateTime.pydt_strftime(dto.dob, '%Y %b %d', none_str = '?')
			),
			_('Activating external patient')
		)

#============================================================
def load_person_from_vcard_via_clipboard():

	fname = gmGuiHelpers.clipboard2file()
	if fname in [None, False]:
		gmGuiHelpers.gm_show_info (
			info = _('No patient in clipboard.'),
			title = _('Activating external patient')
		)
		return

	from Gnumed.business import gmVCard
	dto = gmVCard.parse_vcard2dto(filename = fname)
	if dto is None:
		gmDispatcher.send(signal='statustext', msg=_('Clipboard does not seem to contain a vCard.'))
		return

	idents = dto.get_candidate_identities(can_create = True)
	if len(idents) == 1:
		ident = idents[0]
		if not set_active_patient(patient = ident):
			gmGuiHelpers.gm_show_info (_(
				'Cannot activate patient:\n\n'
				'%s %s (%s)\n'
				'%s'
				) % (
					dto.firstnames,
					dto.lastnames,
					dto.gender,
					gmDateTime.pydt_strftime(dto.dob, '%Y %b %d', none_str = '?')
				),
				_('Activating external patient')
			)
		return

	dlg = cSelectPersonFromListDlg(wx.GetApp().GetTopWindow(), -1)
	dlg.set_persons(persons = idents)
	result = dlg.ShowModal()
	ident = dlg.get_selected_person()
	dlg.DestroyLater()
	if result == wx.ID_CANCEL:
		return
	if not set_active_patient(patient = ident):
		gmGuiHelpers.gm_show_info (_(
			'Cannot activate patient:\n\n'
			'%s %s (%s)\n'
			'%s'
			) % (
				dto.firstnames,
				dto.lastnames,
				dto.gender,
				gmDateTime.pydt_strftime(dto.dob, '%Y %b %d', none_str = '?')
			),
			_('Activating external patient')
		)

#============================================================
def load_person_from_xml_linuxmednews_via_clipboard():

	fname = gmGuiHelpers.clipboard2file()
	if fname in [None, False]:
		gmGuiHelpers.gm_show_info (
			info = _('No patient in clipboard.'),
			title = _('Activating external patient')
		)
		return

	from Gnumed.business import gmLinuxMedNewsXML
	dto = gmLinuxMedNewsXML.parse_xml_linuxmednews(filename = fname)
	if dto is None:
		gmDispatcher.send(signal='statustext', msg=_('Clipboard does not seem to contain LinuxMedNews XML.'))
		return

	idents = dto.get_candidate_identities(can_create = True)
	if len(idents) == 1:
		ident = idents[0]
		if not set_active_patient(patient = ident):
			gmGuiHelpers.gm_show_info (_(
				'Cannot activate patient:\n\n'
				'%s %s (%s)\n'
				'%s') % (
					dto.firstnames,
					dto.lastnames,
					dto.gender,
					gmDateTime.pydt_strftime(dto.dob, '%Y %b %d', none_str = '?')
				),
				_('Activating external patient')
			)
		return

	dlg = cSelectPersonFromListDlg(wx.GetApp().GetTopWindow(), -1)
	dlg.set_persons(persons = idents)
	result = dlg.ShowModal()
	ident = dlg.get_selected_person()
	dlg.DestroyLater()
	if result == wx.ID_CANCEL:
		return None
	if not set_active_patient(patient = ident):
		gmGuiHelpers.gm_show_info (_(
			'Cannot activate patient:\n\n'
			'%s %s (%s)\n'
			'%s'
			) % (
				dto.firstnames,
				dto.lastnames,
				dto.gender,
				gmDateTime.pydt_strftime(dto.dob, '%Y %b %d', none_str = '?')
			),
			_('Activating external patient')
		)

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
		dlg.DestroyLater()

	# search
	idents = dto.get_candidate_identities(can_create=True)
	if idents is None:
		gmGuiHelpers.gm_show_info (_(
			'Cannot create new patient:\n\n'
			' [%s %s (%s), %s]'
			) % (
				dto.firstnames,
				dto.lastnames,
				dto.gender,
				gmDateTime.pydt_strftime(dto.dob, '%Y %b %d', none_str = '?')
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
		ident = dlg.get_selected_person()
		dlg.DestroyLater()
		if result == wx.ID_CANCEL:
			return None

	if activate_immediately:
		if not set_active_patient(patient = ident):
			gmGuiHelpers.gm_show_info (_(
				'Cannot activate patient:\n\n'
				'%s %s (%s)\n'
				'%s') % (
					dto.firstnames,
					dto.lastnames,
					dto.gender,
					gmDateTime.pydt_strftime(dto.dob, '%Y %b %d', none_str = '?')
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
		self.SetToolTip(self._tt_search_hints)

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
	def __get_patient(self):
		if not self.__person:
			return None

		return self.__person.as_patient

	patient = property(__get_patient)

	#--------------------------------------------------------
	# utility methods
	#--------------------------------------------------------
	def _display_name(self):
		name = ''
		if self.person:
			name = self.person.description_gender + gmTools.coalesce(self.person.get_formatted_dob(), '', ' %s')
		self.SetValue(name)
		# adjust tooltip
		if self.person is None:
			self.SetToolTip(self._tt_search_hints)
			return

		tt = '%s%s\n%s%s%s\n%s' % (
			self.person.description_gender,
			gmTools.coalesce(self.person.get_formatted_dob(), '', ' (%s)'),
			gmTools.coalesce(self.person['emergency_contact'], '', '%s\n %%s\n' % _('In case of emergency contact:')),
			gmTools.coalesce(self.person['comment'], '', '\n%s\n'),
			gmTools.u_box_horiz_single * 40,
			self._tt_search_hints
		)
		self.SetToolTip(tt)

	#--------------------------------------------------------
	def _remember_ident(self, ident=None):

		if not isinstance(ident, gmPerson.cPerson):
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
		self.Bind(wx.EVT_CHAR, self.__on_char)
		self.Bind(wx.EVT_SET_FOCUS, self._on_get_focus)
		self.Bind(wx.EVT_KILL_FOCUS, self._on_loose_focus)
		self.Bind(wx.EVT_TEXT_ENTER, self.__on_enter)

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
		# when closing our application or losing focus to another
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

			dlg = cSelectPersonFromListDlg(wx.GetTopLevelParent(self), -1)
			dlg.set_persons(persons = self.__prev_idents)
			result = dlg.ShowModal()
			if result == wx.ID_OK:
				wx.BeginBusyCursor()
				self.person = dlg.get_selected_person()
				dlg.DestroyLater()
				wx.EndBusyCursor()
				return True

			dlg.DestroyLater()
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
			search_immediately = gmCfgDB.get4user (
				option = 'patient_search.external_sources.immediately_search_if_single_source',
				workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
				default = False
			)
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

		# same person anyways ?
		if self.person is not None:
			if curr_search_term == self.person.description:
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
			dlg.DestroyLater()
			return None

		wx.BeginBusyCursor()
		self.person = dlg.get_selected_person()
		dlg.DestroyLater()
		wx.EndBusyCursor()

		return None

#============================================================
def _verify_staff_chart_access(patient=None):

	if patient is None:
		return True

	# staff ?
	if patient.ID not in [ s['pk_identity'] for s in gmStaff.get_staff_list() ]:
		return True

	curr_prov = gmStaff.gmCurrentProvider()

	# can view my own chart
	if patient.ID == curr_prov['pk_identity']:
		return True

	# primary provider can view patient
	if patient['pk_primary_provider'] == curr_prov['pk_staff']:
		return True

	proceed = gmGuiHelpers.gm_show_question (
		title = _('Privacy check'),
		question = _(
			'You have selected the chart of a member of staff,\n'
			'for which privacy is particularly important:\n'
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
			gmTools.coalesce(patient['title'], '', '%s '),
			patient['lastnames']
		)
	)

	if proceed:
		prov = '%s (%s%s %s)' % (
			curr_prov['short_alias'],
			gmTools.coalesce(curr_prov['title'], '', '%s '),
			curr_prov['firstnames'],
			curr_prov['lastnames']
		)
		pat = '%s%s %s' % (
			gmTools.coalesce(patient['title'], '', '%s '),
			patient['firstnames'],
			patient['lastnames']
		)
		# notify the staff member
		gmProviderInbox.create_inbox_message (
			staff = patient.staff_id,
			message_type = _('Privacy notice'),
			message_category = 'administrative',
			subject = _('%s: Your chart has been accessed by %s.') % (pat, prov),
			patient = patient.ID
		)
		# notify /me about the staff member notification
		gmProviderInbox.create_inbox_message (
			staff = curr_prov['pk_staff'],
			message_type = _('Privacy notice'),
			message_category = 'administrative',
			subject = _('%s: Staff member %s has been notified of your chart access.') % (prov, pat)
		)

	return proceed

#------------------------------------------------------------
def _check_has_dob(patient=None):

	if patient is None:
		return

	if patient['dob'] is None:
		gmGuiHelpers.gm_show_warning (
			title = _('Checking date of birth'),
			warning = _(
				'\n'
				' %s\n'
				'\n'
				'The date of birth for this patient is not known !\n'
				'\n'
				'You can proceed to work on the patient but\n'
				'GNUmed will be unable to assist you with\n'
				'age-related decisions.\n'
			) % patient.description_gender
		)

#------------------------------------------------------------
def _check_birthday(patient=None):

	if patient['dob'] is None:
		return

	dob_distance = gmCfgDB.get4user (
		option = 'patient_search.dob_warn_interval',
		workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
		default = '1 week'
	)

	if not patient.dob_in_range(dob_distance, dob_distance):
		return

	now = gmDateTime.pydt_now_here()
	msg = _('%(pat)s turns %(age)s on %(month)s %(day)s ! (today is %(month_now)s %(day_now)s)') % {
		'pat': patient.get_description_gender(),
		'age': patient.get_medical_age(at_date = patient.birthday_this_year).strip('y'),
		'month': patient.get_formatted_dob(format = '%B'),
		'day': patient.get_formatted_dob(format = '%d'),
		'month_now': now.strftime('%B'),
		'day_now': now.strftime('%d')
	}
	gmDispatcher.send(signal = 'statustext', msg = msg)

#------------------------------------------------------------
def _do_after_setting_active_patient(patient=None):
	_check_has_dob(patient = patient)
	_check_birthday(patient = patient)

#------------------------------------------------------------
def set_active_patient(patient=None, forced_reload=False):

	# already active ?
	if isinstance(patient, gmPerson.gmCurrentPatient):
		return True

	if isinstance(patient, gmPerson.cPatient):
		if patient['is_deleted']:
			_log.error('patient is disabled, will not use as active patient: %s', patient)
			return False
	elif isinstance(patient, gmPerson.cPerson):
		if patient['is_deleted']:
			_log.error('patient is disabled, will not use as active patient: %s', patient)
			return False
		patient = patient.as_patient
	elif patient == -1:
		pass
	else:
		# maybe integer ?
		success, pk = gmTools.input2int(initial = patient, minval = 1)
		if not success:
			raise ValueError('<patient> must be either -1, >0, or a cPatient, cPerson or gmCurrentPatient instance, is: %s' % patient)
		# but also valid patient ID ?
		try:
			patient = gmPerson.cPatient(aPK_obj = pk)
		except Exception:
			_log.exception('error changing active patient to [%s]' % patient)
			return False

	if not _verify_staff_chart_access(patient = patient):
		return False

	success = gmPerson.set_active_patient(patient = patient, forced_reload = forced_reload)

	if not success:
		return False

	wx.CallAfter(_do_after_setting_active_patient, patient)
	return True

#------------------------------------------------------------
class cActivePatientSelector(cPersonSearchCtrl):

	def __init__ (self, *args, **kwargs):

		cPersonSearchCtrl.__init__(self, *args, **kwargs)

		# get configuration
		self.__always_dismiss_on_search = gmCfgDB.get4user (
			option = 'patient_search.always_dismiss_previous_patient',
			workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
			default = False
		)
		self.__always_reload_after_search = gmCfgDB.get4user (
			option = 'patient_search.always_reload_new_patient',
			workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
			default = False
		)
		self.__register_events()

	#--------------------------------------------------------
	# utility methods
	#--------------------------------------------------------
	def _display_name(self):

		curr_pat = gmPerson.gmCurrentPatient()
		if curr_pat.connected:
			name = curr_pat.description
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
			self.SetToolTip(self._tt_search_hints)
			return

		if (self.person['emergency_contact'] is None) and (self.person['comment'] is None):
			separator = ''
		else:
			separator = '%s\n' % (gmTools.u_box_horiz_single * 40)

		tt = '%s%s%s%s' % (
			gmTools.coalesce(self.person['emergency_contact'], '', '%s\n %%s\n' % _('In case of emergency contact:')),
			gmTools.coalesce(self.person['comment'], '', '\n%s\n'),
			separator,
			self._tt_search_hints
		)
		self.SetToolTip(tt)
	#--------------------------------------------------------
	def _set_person_as_active_patient(self, person):
		if not set_active_patient(patient = person, forced_reload = self.__always_reload_after_search):
			_log.error('cannot change active patient')
			return None

		self._remember_ident(person)
		return True

	#--------------------------------------------------------
	# event handling
	#--------------------------------------------------------
	def __register_events(self):
		# client internal signals
		gmDispatcher.connect(signal = 'post_patient_selection', receiver = self._on_post_patient_selection)
		gmDispatcher.connect(signal = 'dem.names_mod_db', receiver = self._on_name_identity_change)
		gmDispatcher.connect(signal = 'dem.identity_mod_db', receiver = self._on_name_identity_change)

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

		super()._on_enter(search_term=search_term)

		if self.person is None:
			return

		self._set_person_as_active_patient(self.person)
	#----------------------------------------------
	def _on_char(self, evt):

		success = super()._on_char(evt)
		if success:
			self._set_person_as_active_patient(self.person)

#============================================================
# main
#------------------------------------------------------------
if __name__ == "__main__":

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	from Gnumed.pycommon import gmLog2
	gmLog2.print_logfile_name()
	# setup a real translation
	del _
	from Gnumed.pycommon import gmI18N
	gmI18N.activate_locale()
	gmI18N.install_domain()

	from Gnumed.wxpython import gmGuiTest

	#--------------------------------------------------------
	def test_searcher():
		wx.Log.EnableLogging(enable = False)
		gmGuiTest.test_widget(cPersonSearchCtrl, patient = None)

	#--------------------------------------------------------
	test_searcher()

#	app.SetWidget(cSelectPersonFromListDlg, -1)
#	app.SetWidget(cActivePatientSelector, -1)

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

