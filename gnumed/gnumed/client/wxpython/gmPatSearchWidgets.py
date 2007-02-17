#  coding: latin-1
"""GnuMed quick patient search widget.

This widget allows to search for patients based on the
critera name, date of birth and patient ID. It goes to
considerable lengths to understand the user's intent from
her input. For that to work well we need per-culture
query generators. However, there's always the fallback
generator.
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmPatSearchWidgets.py,v $
# $Id: gmPatSearchWidgets.py,v 1.62 2007-02-17 14:01:26 ncq Exp $
__version__ = "$Revision: 1.62 $"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = 'GPL (for details see http://www.gnu.org/)'

import sys, os.path, time, glob, locale, datetime as pyDT

import wx

from Gnumed.pycommon import gmLog, gmDispatcher, gmSignals, gmPG2, gmI18N, gmCfg, gmTools, gmDateTime
from Gnumed.business import gmPerson, gmKVK
from Gnumed.wxpython import gmGuiHelpers, gmDemographicsWidgets
from Gnumed.wxGladeWidgets import wxgSelectPersonFromListDlg, wxgSelectPersonDTOFromListDlg

_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)

_cfg = gmCfg.gmDefCfgFile

ID_PatPickList = wx.NewId()
ID_BTN_AddNew = wx.NewId()

#============================================================
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
			ident = person.get_identity()

			row_num = self._LCTRL_persons.InsertStringItem(pos, label = gmTools.coalesce(ident['title'], ''))
			self._LCTRL_persons.SetStringItem(index = row_num, col = 1, label = ident['lastnames'])
			self._LCTRL_persons.SetStringItem(index = row_num, col = 2, label = ident['firstnames'])
			self._LCTRL_persons.SetStringItem(index = row_num, col = 3, label = gmTools.coalesce(ident['preferred'], ''))
			self._LCTRL_persons.SetStringItem(index = row_num, col = 4, label = ident['dob'].strftime('%x'))
			self._LCTRL_persons.SetStringItem(index = row_num, col = 5, label = gmTools.coalesce(ident['l10n_gender'], '?'))
			pat = gmPerson.cPatient(identity=ident)
			enc = pat.get_last_encounter()
			if enc is None:
				label = u''
			else:
				label = u'%s (%s)' % (enc['started'].strftime('%x'), enc['l10n_type'])
			self._LCTRL_persons.SetStringItem(index = row_num, col = 6, label = label)
			try: self._LCTRL_persons.SetStringItem(index = row_num, col = 7, label = ident['match_type'])
			except: pass

		for col in range(len(self.__cols)):
			self._LCTRL_persons.SetColumnWidth(col=col, width=wx.LIST_AUTOSIZE)

		self._BTN_select.Enable(False)
		self._LCTRL_persons.SetFocus()

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
			self._LCTRL_persons.SetStringItem(index = row_num, col = 3, label = dto.dob.strftime('%x'))
			self._LCTRL_persons.SetStringItem(index = row_num, col = 4, label = gmTools.coalesce(dto.gender, ''))

		for col in range(len(self.__cols)):
			self._LCTRL_persons.SetColumnWidth(col=col, width=wx.LIST_AUTOSIZE)

		self._BTN_select.Enable(False)
		self._LCTRL_persons.SetFocus()

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
	xdt_profiles = _cfg.get('workplace', 'XDT profiles')
	if xdt_profiles is None:
		return []

	for profile in xdt_profiles:
		name = _cfg.get('XDT profile %s' % profile, 'filename')
		if name is None:
			_log.Log(gmLog.lErr, 'XDT profile [%s] does not define a <filename>' % profile)
			continue
		encoding = _cfg.get('XDT profile %s' % profile, 'encoding')
		if encoding is None:
			_log.Log(gmLog.lWarn, 'xDT source profile [%s] does not specify an <encoding> for BDT file [%s]' % (profile, name))
		source = _cfg.get('XDT profile %s' % profile, 'source')
		if source is None:
			source = _('unknown')
		dob_format = _cfg.get('XDT profile %s' % profile, 'DOB format')
		if dob_format is None:
			_log.Log(gmLog.lErr, 'XDT profile [%s] does not define a date of birth format in <DOB format>' % profile)
			continue
		bdt_files.append({'file': name, 'source': source, 'encoding': encoding, 'dob_format': dob_format})

	dtos = []
	for bdt_file in bdt_files:
		try:
			# FIXME: potentially return several patients per file
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
			_log.LogException('cannot access xDT file [%s]' % bdt_file['file'])
			continue

		except ValueError:
			gmGuiHelpers.gm_show_info (
				_(
				'Cannot load patient from BDT file\n\n'
				' [%s]'
				) % bdt_file,
				_('Activating xDT patient')
			)
			_log.LogException('cannot read patient from xDT file [%s]' % bdt_file['file'])
			continue

		except:
			gmGuiHelpers.gm_show_error (
				_(
				'Cannot load patient from BDT file\n\n'
				' [%s]'
				) % bdt_file,
				_('Activating xDT patient'),
				aLogLevel = None
			)
			_log.LogException('cannot read patient from xDT file [%s]' % bdt_file['file'])
			continue

		dtos.append({'dto': dto, 'source': bdt_file['source']})

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

	# add configured one
	fname = _cfg.get('AU PracSoft PATIENTS.IN', 'filename')
	source = _cfg.get('AU PracSoft PATIENTS.IN', 'source')
	if fname is not None and source is not None:
		pracsoft_files.append({'file': os.path.expanduser(fname), 'source': source})

	# and parse them
	dtos = []
	for pracsoft_file in pracsoft_files:
		try:
			tmp = gmPerson.get_persons_from_pracsoft_file(filename = pracsoft_file['file'])
		except:
			_log.LogException('cannot parse PracSoft file [%s]' % pracsoft_file['file'])
			continue
		for dto in tmp:
			dtos.append({'dto': dto, 'source': pracsoft_file['source']})

	return dtos
#============================================================
def load_persons_from_kvks():

	db_cfg = gmCfg.cCfgSQL()
	kvk_dir = os.path.abspath(os.path.expanduser(db_cfg.get2 (
		option = 'DE.KVK.spool_dir',
		workplace = gmPerson.gmCurrentProvider().workplace,
		bias = 'workplace',
		default = u'/var/spool/kvkd/'
	)))
	dtos = []
	for dto in gmKVK.get_available_kvks_as_dtos(spool_dir = kvk_dir):
		dtos.append({'dto': dto, 'source': 'KVK'})

	return dtos
#============================================================
def load_patient_from_external_sources(parent=None):

	# get DTOs from interfaces
	dtos = []
	dtos.extend(load_persons_from_xdt())
	dtos.extend(load_persons_from_pracsoft_au())
	dtos.extend(load_persons_from_kvks())

	if len(dtos) == 0:
		gmGuiHelpers.gm_statustext(_('No patients found in external sources.'))
		return True
	else:
		if parent is None:
			parent = wx.GetApp().GetTopWindow()
		dlg = cSelectPersonDTOFromListDlg(parent=parent, id=-1)
		dlg.set_dtos(dtos=dtos)
		result = dlg.ShowModal()
		if result == wx.ID_CANCEL:
			return True
		dto = dlg.get_selected_dto()['dto']
		dlg.Destroy()

	# FIXME: config: delete DTO source after selection, eg KVK

	# search
	searcher = gmPerson.cPatientSearcher_SQL()
	persons = searcher.get_persons (dto = dto)

	if len(persons) == 0:
		ident = gmPerson.create_identity (
			firstnames = dto.firstnames,
			lastnames = dto.lastnames,
			gender = dto.gender,
			dob = dto.dob
		)
		if ident is None:
			gmGuiHelpers.gm_show_info (
				_(
				'Cannot create new patient:\n\n'
				' [%s %s (%s), %s]'
				) % (dto.firstnames, dto.lastnames, dto.gender, dto.dob.strftime('%x')),
				_('Activating xDT patient')
			)
			return False
		person = gmPerson.cPerson(identity=ident)

	if len(persons) == 1:
		person = persons[0]

	if len(persons) > 1:
		if parent is None:
			parent = wx.GetApp().GetTopWindow()
		dlg = cSelectPersonFromListDlg(parent=parent, id=-1)
		dlg.set_persons(persons=persons)
		result = dlg.ShowModal()
		if result == wx.ID_CANCEL:
			return True
		person = dlg.get_selected_person()
		dlg.Destroy()

	if not gmPerson.set_active_patient(patient = person.get_identity()):
		gmGuiHelpers.gm_show_info (
			_(
			'Cannot activate patient:\n\n'
			'%s %s (%s)\n'
			'%s'
			) % (dto.firstnames, dto.lastnames, dto.gender, dto.dob.strftime('%x')),
			_('Activating xDT patient')
		)
		return False

	return True
#============================================================
class cPatientSelector(wx.TextCtrl):
	"""Widget for smart search for patients."""
	def __init__ (self, parent, id = -1, pos = wx.DefaultPosition, size = wx.DefaultSize):
		self.curr_pat = gmPerson.gmCurrentPatient()

		# need to explicitely process ENTER events to avoid
		# them being handed over to the next control
		wx.TextCtrl.__init__(
			self,
			parent,
			id,
			'',
			pos,
			size,
			style = wx.TE_PROCESS_ENTER
		)

		selector_tooltip = _(
		'Patient search field.                             \n'
		'\n'
		'To search, type any of:\n'
		' - fragment of last or first name\n'
		" - date of birth (can start with '$' or '*')\n"
		" - patient ID (can start with '#')\n"
		'and hit <ENTER>.\n'
		'\n'
		'<CURSOR-UP>\n'
		' - recall most recently used search term\n'
		'<CURSOR-DOWN>\n'
		' - list 10 most recently activated patients\n'
		'<F2>\n'
		' - scan external sources for patients to import and activate\n'
		)
		self.SetToolTip(wx.ToolTip(selector_tooltip))

		self._display_name()

		# FIXME: set query generator
		self.__pat_searcher = gmPerson.cPatientSearcher_SQL()

		self.__prev_search_term = None
		self.__prev_idents = []
		self.__pat_picklist_col_defs = []

		self._lclick_count = 0

		# get configuration
		cfg = gmCfg.cCfgSQL()

		self.__always_dismiss_after_search = bool ( 
			cfg.get2 (
				option = 'patient_search.always_dismiss_previous_patient',
				workplace = gmPerson.gmCurrentProvider().workplace,
				bias = 'user',
				default = 0
			)
		)

		self.__always_reload_after_search = bool (
			cfg.get2 (
				option = 'patient_search.always_reload_new_patient',
				workplace = gmPerson.gmCurrentProvider().workplace,
				bias = 'user',
				default = 0
			)
		)

		self.__register_events()
	#--------------------------------------------------------
	def SetActivePatient(self, pat):
		if not gmPerson.set_active_patient(patient=pat, forced_reload = self.__always_reload_after_search):
			_log.Log (gmLog.lErr, 'cannot change active patient')
			return None

		ident = pat.get_identity()
		self.__remember_ident(ident)

		dbcfg = gmCfg.cCfgSQL()
		dob_distance = dbcfg.get2 (
			option = u'',
			workplace = gmPerson.gmCurrentProvider().workplace,
			bias = u'user',
			default = u'1 week'
		)

		if ident.dob_in_range(dob_distance, dob_distance):
			now = pyDT.datetime.now(tz = gmDateTime.gmCurrentLocalTimezone)
			enc = locale.getlocale()[1]
			gmGuiHelpers.gm_statustext (
				_('%(pat)s was born on %(dow)s, %(month)s %(day)s ! (today is %(dow_now)s, %(month_now)s %(day_now)s)') % {
					'pat': ident.get_description(),
					'dow': ident['dob'].strftime('%A').decode(enc),
					'month': ident['dob'].strftime('%B').decode(enc),
					'day': ident['dob'].strftime('%d'),
					'dow_now': now.strftime('%A').decode(enc),
					'month_now': now.strftime('%B').decode(enc),
					'day_now': now.strftime('%d')
				}
			)

		return True
	#--------------------------------------------------------
	# utility methods
	#--------------------------------------------------------
	def _display_name(self):
		if self.curr_pat.is_connected():
			ident = self.curr_pat.get_identity()
			self.SetValue(ident['description'])
		else:
			self.SetValue('')
	#--------------------------------------------------------
	def __remember_ident(self, ident=None):

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
		# - process some special chars
		wx.EVT_CHAR(self, self._on_char)
		# - select data in input field upon tabbing in
		wx.EVT_SET_FOCUS (self, self._on_get_focus)
		# - redraw the currently active name upon losing focus
		#   (but see the caveat in the handler)
		# FIXME: causes core dump in one version of wxPython -SJTAN
		#wx.EVT_KILL_FOCUS (self, self._on_loose_focus)

		wx.EVT_TEXT_ENTER (self, self.GetId(), self._on_enter)
		wx.EVT_LEFT_UP (self, self._on_left_mousebutton_up)

		# client internal signals
		gmDispatcher.connect(signal=gmSignals.post_patient_selection(), receiver=self._on_post_patient_selection)
	#----------------------------------------------
	def _on_post_patient_selection(self, **kwargs):
		wx.CallAfter(self._display_name)
	#--------------------------------------------------------
	def _on_left_mousebutton_up(self, evt):
		"""upon left click release

		- select all text in the field so that the next
		  character typed will delete it
		
		- or set cursor to text position in case more left
		  clicks follow
		"""
		# unclicked, not highlighted
		if self._lclick_count == 0:
			self.SetSelection (-1,-1)			# highlight entire text
			self._lclick_count = 1
			evt.Skip()
			return None
			
		# has been clicked before - should be highlighted
		start, end = self.GetSelection()
		self.SetSelection(start, end)
		self._lclick_count = 0
		evt.Skip()
		return None
	#--------------------------------------------------------
	def _on_get_focus(self, evt):
		"""upon tabbing in

		- select all text in the field so that the next
		  character typed will delete it
		"""
		self.SetSelection (-1,-1)
		evt.Skip()
	#--------------------------------------------------------
	def _on_loose_focus(self, evt):
		# if we use wx.EVT_KILL_FOCUS we will also receive this event
		# when closing our application or loosing focus to another
		# application which is NOT what we intend to achieve,
		# however, this is the least ugly way of doing this due to
		# certain vagaries of wxPython (see the Wiki)

		# remember fragment
		curr_search_term = self.GetValue()
		if self.IsModified() and (curr_search_term.strip() != ''):
			self.__prev_search_term = curr_search_term

		# and display currently active patient
		self._display_name()
		# unset highlighting
		self.SetSelection (0,0)
		# reset highlight counter
		self._lclick_count = 0

		evt.Skip()
	#--------------------------------------------------------
	def _on_char(self, evt):
		keycode = evt.GetKeyCode()

		# list of previously active patients
		if keycode == wx.WXK_DOWN:
			evt.Skip()
			if len(self.__prev_idents) == 0:
				return True
			persons = []
			for ident in self.__prev_idents:
				persons.append(gmPerson.cPerson(identity=ident))

			dlg = cSelectPersonFromListDlg(parent=wx.GetTopLevelParent(self), id=-1)
			dlg.set_persons(persons=persons)
			result = dlg.ShowModal()
			if result == wx.ID_OK:
				wx.BeginBusyCursor()
				person = dlg.get_selected_person()
				self.SetActivePatient(person)
			dlg.Destroy()

			wx.EndBusyCursor()
			return True

		# previous search fragment
		if keycode == wx.WXK_UP:
			evt.Skip()
			# FIXME: cycling through previous fragments
			if self.__prev_search_term is not None:
				self.SetValue(self.__prev_search_term)
			return True

		# invoke external patient sources
		if keycode == wx.WXK_F2:
			evt.Skip()
			load_patient_from_external_sources(parent=wx.GetTopLevelParent(self))
			return True

		# FIXME: invoke add new patient
		# FIXME: add popup menu apart from system one

		evt.Skip()
	#--------------------------------------------------------
	def _on_enter(self, evt):

		curr_search_term = self.GetValue().strip()
		if curr_search_term == '':
			return None

		if self.curr_pat.is_connected():
			ident = self.curr_pat.get_identity()
			if curr_search_term == ident['description']:
				return None

		wx.BeginBusyCursor()

		if self.__always_dismiss_after_search:
			print "dismissing patient"
			self.SetActivePatient(-1)

		# remember fragment
		if self.IsModified():
			self.__prev_search_term = curr_search_term

		# get list of matching ids
		start = time.time()
		persons = self.__pat_searcher.get_persons(curr_search_term)
		duration = time.time() - start

		if persons is None:
			wx.EndBusyCursor()
			gmGuiHelpers.gm_show_info (
				_('Error searching for matching patients.\n\n'
				  'Search term: "%s"'
				) % curr_search_term,
				_('selecting patient')
			)
			return None

		_log.Log (gmLog.lInfo, "%s person objects(s) fetched in %3.3f seconds" % (len(persons), duration))

		if len(persons) == 0:
			wx.EndBusyCursor()
			gmGuiHelpers.gm_show_info (
				_('Cannot find any matching patients.\n'
				  'You may want to try a shorter search term.\n\n'
				  'Search term: "%s"\n\n'
				  'You will be taken to the "New Patient" wizard now.'
				) % curr_search_term,
				_('selecting patient')
			)
			wiz = gmDemographicsWidgets.cNewPatientWizard(parent=self.GetParent())
			wiz.RunWizard(activate=True)
			return None

		# only one matching identity
		if len(persons) == 1:
			self.SetActivePatient(persons[0])
			wx.EndBusyCursor()
			return None

		# more than one matching identity: let user select from pick list
		dlg = cSelectPersonFromListDlg(parent=wx.GetTopLevelParent(self), id=-1)
		dlg.set_persons(persons=persons)
		wx.EndBusyCursor()
		result = dlg.ShowModal()
		if result == wx.ID_CANCEL:
			dlg.Destroy()
			return None

		wx.BeginBusyCursor()
		person = dlg.get_selected_person()
		dlg.Destroy()
		self.SetActivePatient(person)
		wx.EndBusyCursor()

		return None
#============================================================
# main
#------------------------------------------------------------
if __name__ == "__main__":
	_log.SetAllLogLevels(gmLog.lData)

	gmI18N.activate_locale()
	gmI18N.install_domain()

	app = wx.PyWidgetTester(size = (200, 40))
	app.SetWidget(cSelectPersonFromListDlg, -1)
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

#============================================================
# $Log: gmPatSearchWidgets.py,v $
# Revision 1.62  2007-02-17 14:01:26  ncq
# - gmCurrentProvider.workplace now property
# - notify about birthday after activating patient
# - remove crufty code/docs
#
# Revision 1.61  2007/02/15 14:58:08  ncq
# - tie KVKs intoi external patient sources framework
#
# Revision 1.60  2007/02/13 17:07:38  ncq
# - tie PracSoft PATIENTS.IN file into external patients framework
# - *always* let user decide on whether to activate an external patient
#   even if only a single source provides a patient
#
# Revision 1.59  2007/01/20 22:52:27  ncq
# - .KeyCode -> GetKeyCode()
#
# Revision 1.58  2007/01/18 22:07:52  ncq
# - (Get)KeyCode() -> KeyCode so 2.8 can do
#
# Revision 1.57  2007/01/10 23:04:12  ncq
# - support explicit DOB format for xDT files
#
# Revision 1.56  2006/12/13 14:57:16  ncq
# - inform about no patients found in external sources
#
# Revision 1.55  2006/11/24 14:23:19  ncq
# - self.Close() does not need wx.ID_*
#
# Revision 1.54  2006/11/24 09:56:03  ncq
# - improved message when error searching patient
#
# Revision 1.53  2006/11/20 19:11:04  ncq
# - improved message when no matching patient found
#
# Revision 1.52  2006/11/20 17:05:55  ncq
# - do not search if supposed search term matches 'description' of current patient
#
# Revision 1.51  2006/11/01 12:54:40  ncq
# - there may not be a previous encounter so don't try to
#   format it's start date if so
#
# Revision 1.50  2006/10/31 12:43:09  ncq
# - out with the crap
# - no more patient expanders
#
# Revision 1.49  2006/10/30 16:46:52  ncq
# - missing encoding in xDT source defs does not *have* to be
#   an error as the file itself may contain the encoding itself
#
# Revision 1.48  2006/10/28 14:57:17  ncq
# - use cPatient.get_last_encounter()
#
# Revision 1.47  2006/10/28 12:34:53  ncq
# - make person and dto selector dialogs handle functionality themselves
# - remove person selector panel class
# - act on ENTER/double-click in person/dto select list
#
# Revision 1.46  2006/10/25 07:46:44  ncq
# - Format() -> strftime() since datetime.datetime does not have .Format()
#
# Revision 1.45  2006/10/24 13:26:43  ncq
# - switch to gmPG2
#
# Revision 1.44  2006/09/13 07:55:11  ncq
# - handle encoding in xDT patient sources
#
# Revision 1.43  2006/09/06 07:22:34  ncq
# - add missing import for glob module
#
# Revision 1.42  2006/09/01 14:46:30  ncq
# - add (untested) MCS/Isynet external patient source
#
# Revision 1.41  2006/08/09 15:00:47  ncq
# - better search widget tooltip
#
# Revision 1.40  2006/07/30 18:48:18  ncq
# - invoke load_external_patient on <F2> in searcher
# - robustify by commenting out shaky KVK code
#
# Revision 1.39  2006/07/30 17:51:00  ncq
# - cleanup
#
# Revision 1.38  2006/07/27 17:07:18  ncq
# - cleanup
# - make Cursor-Down the way to invoke previous patients
#
# Revision 1.37  2006/07/26 13:22:37  ncq
# - degrade non-fatal error messages to info messages
#
# Revision 1.36  2006/07/26 13:15:03  ncq
# - cleanup
#
# Revision 1.35  2006/07/24 19:38:39  ncq
# - fix "prev patients" list (alt-p) in patient selector
# - start obsoleting old (ugly) patient pick list
#
# Revision 1.34  2006/07/24 14:18:31  ncq
# - finish pat/dto selection dialogs
# - use them in loading external patients and selecting among matches in search control
#
# Revision 1.33  2006/07/24 11:31:11  ncq
# - cleanup
# - add dialogs to select person/person-dto from list
# - use dto-selection dialog when loading external patient
#
# Revision 1.32  2006/07/22 15:18:24  ncq
# - better error logging
#
# Revision 1.31  2006/07/21 14:48:39  ncq
# - proper returns from load_patient_from_external_sources()
#
# Revision 1.30  2006/07/19 21:41:13  ncq
# - support list of xdt files
#
# Revision 1.29  2006/07/18 21:18:13  ncq
# - add proper load_patient_from_external_sources()
#
# Revision 1.28  2006/05/15 13:36:00  ncq
# - signal cleanup:
#   - activating_patient -> pre_patient_selection
#   - patient_selected -> post_patient_selection
#
# Revision 1.27  2006/05/12 12:18:11  ncq
# - whoami -> whereami cleanup
# - use gmCurrentProvider()
#
# Revision 1.26  2006/05/04 09:49:20  ncq
# - get_clinical_record() -> get_emr()
# - adjust to changes in set_active_patient()
# - need explicit set_active_patient() after ask_for_patient() if wanted
#
# Revision 1.25  2005/12/14 17:01:51  ncq
# - use improved db cfg option getting
#
# Revision 1.24  2005/09/28 21:27:30  ncq
# - a lot of wx2.6-ification
#
# Revision 1.23  2005/09/27 20:44:59  ncq
# - wx.wx* -> wx.*
#
# Revision 1.22  2005/09/26 18:01:51  ncq
# - use proper way to import wx26 vs wx2.4
# - note: THIS WILL BREAK RUNNING THE CLIENT IN SOME PLACES
# - time for fixup
#
# Revision 1.21  2005/09/24 09:17:29  ncq
# - some wx2.6 compatibility fixes
#
# Revision 1.20  2005/09/12 15:18:05  ncq
# - fix faulty call to SetActivePatient() found by Richard when using
#   always_dismiss_after_search
#
# Revision 1.19  2005/09/11 17:35:05  ncq
# - support "patient_search.always_reload_new_patient"
#
# Revision 1.18  2005/09/04 07:31:14  ncq
# - Richard requested the "no active patient" tag be removed
#   when no patient is active
#
# Revision 1.17  2005/05/05 06:29:22  ncq
# - if patient not found invoke new patient wizard with activate=true
#
# Revision 1.16  2005/03/08 16:54:13  ncq
# - teach patient picklist about cIdentity
#
# Revision 1.15  2005/02/20 10:33:26  sjtan
#
# disable lose focus to prevent core dumping in a wxPython version.
#
# Revision 1.14  2005/02/13 15:28:07  ncq
# - v_basic_person.i_pk -> pk_identity
#
# Revision 1.13  2005/02/12 13:59:11  ncq
# - v_basic_person.i_id -> i_pk
#
# Revision 1.12  2005/02/01 10:16:07  ihaywood
# refactoring of gmDemographicRecord and follow-on changes as discussed.
#
# gmTopPanel moves to gmHorstSpace
# gmRichardSpace added -- example code at present, haven't even run it myself
# (waiting on some icon .pngs from Richard)
#
# Revision 1.11  2005/01/31 10:37:26  ncq
# - gmPatient.py -> gmPerson.py
#
# Revision 1.10  2004/10/20 12:40:55  ncq
# - some cleanup
#
# Revision 1.9  2004/10/20 07:49:45  sjtan
# small forward wxWidget compatibility change.
#
# Revision 1.7  2004/09/06 22:22:15  ncq
# - properly use setDBParam()
#
# Revision 1.6  2004/09/02 00:40:13  ncq
# - store option always_dismiss_previous_patient if not found
#
# Revision 1.5  2004/09/01 22:04:03  ncq
# - cleanup
# - code order change to avoid exception due to None-check after logging
#
# Revision 1.4  2004/08/29 23:15:58  ncq
# - Richard improved the patient picklist popup
# - plus cleanup/fixes etc
#
# Revision 1.3  2004/08/24 15:41:13  ncq
# - eventually force patient pick list to stay on top
#   as suggested by Robin Dunn
#
# Revision 1.2  2004/08/20 13:31:05  ncq
# - cleanup/improve comments/improve naming
# - dismiss patient regardless of search result if so configured
# - don't search on empty search term
#
# Revision 1.1  2004/08/20 06:46:38  ncq
# - used to be gmPatientSelector.py
#
# Revision 1.45  2004/08/19 13:59:14  ncq
# - streamline/cleanup
# - Busy Cursor according to Richard
#
# Revision 1.44  2004/08/18 08:18:35  ncq
# - later wxWidgets version don't support parent=NULL anymore
#
# Revision 1.43  2004/08/02 18:53:36  ncq
# - used wx.Begin/EndBusyCursor() around setting the active patient
#
# Revision 1.42  2004/07/18 19:51:12  ncq
# - cleanup, use True/False, not true/false
# - use run_ro_query(), not run_query()
#
# Revision 1.41  2004/07/15 20:36:11  ncq
# - better default size
#
# Revision 1.40  2004/06/20 16:01:05  ncq
# - please epydoc more carefully
#
# Revision 1.39  2004/06/20 06:49:21  ihaywood
# changes required due to Epydoc's OCD
#
# Revision 1.38  2004/06/04 16:27:12  shilbert
# - giving focus highlights the text and lets you replace it
#
# Revision 1.37  2004/03/27 18:24:11  ncq
# - Ian and I fixed the same bugs again :)
#
# Revision 1.36  2004/03/27 04:37:01  ihaywood
# lnk_person2address now lnk_person_org_address
# sundry bugfixes
#
# Revision 1.35  2004/03/25 11:03:23  ncq
# - getActiveName -> get_names
#
# Revision 1.34  2004/03/20 19:48:07  ncq
# - adapt to flat id list from get_patient_ids
#
# Revision 1.33  2004/03/12 13:23:41  ncq
# - cleanup
#
# Revision 1.32  2004/03/05 11:22:35  ncq
# - import from Gnumed.<pkg>
#
# Revision 1.31  2004/03/04 19:47:06  ncq
# - switch to package based import: from Gnumed.foo import bar
#
# Revision 1.30  2004/02/25 09:46:22  ncq
# - import from pycommon now, not python-common
#
# Revision 1.29  2004/02/05 18:41:31  ncq
# - make _on_patient_selected() thread-safe
# - move SetActivePatient() logic into gmPatient
#
# Revision 1.28  2004/02/04 00:55:02  ncq
# - moved UI-independant patient searching code into business/gmPatient.py where it belongs
#
# Revision 1.27  2003/11/22 14:49:32  ncq
# - fix typo
#
# Revision 1.26  2003/11/22 00:26:10  ihaywood
# Set coding to latin-1 to please python 2.3
#
# Revision 1.25  2003/11/18 23:34:02  ncq
# - don't use reload to force reload of same patient
#
# Revision 1.24  2003/11/17 10:56:38  sjtan
#
# synced and commiting.
#
# Revision 1.23  2003/11/09 17:29:22  shilbert
# - ['demographics'] -> ['demographic record']
#
# Revision 1.22  2003/11/07 20:44:11  ncq
# - some cleanup
# - listen to patient_selected by other widgets
#
# Revision 1.21  2003/11/04 00:22:46  ncq
# - remove unneeded import
#
# Revision 1.20  2003/10/26 17:42:51  ncq
# - cleanup
#
# Revision 1.19  2003/10/26 11:27:10  ihaywood
# gmPatient is now the "patient stub", all demographics stuff in gmDemographics.
#
# Ergregious breakages are fixed, but needs more work
#
# Revision 1.18  2003/10/26 01:36:13  ncq
# - gmTmpPatient -> gmPatient
#
# Revision 1.17  2003/10/19 12:17:57  ncq
# - typo fix
#
# Revision 1.16  2003/09/21 07:52:57  ihaywood
# those bloody umlauts killed by python interpreter!
#
# Revision 1.15  2003/07/07 08:34:31  ihaywood
# bugfixes on gmdrugs.sql for postgres 7.3
#
# Revision 1.14  2003/07/03 15:22:19  ncq
# - removed unused stuff
#
# Revision 1.13  2003/06/29 14:08:02  ncq
# - extra ; removed
# - kvk/incoming/ as default KVK dir
#
# Revision 1.12  2003/04/09 16:20:19  ncq
# - added set selection on get focus -- but we don't tab in yet !!
# - can now set title on pick list
# - added KVK handling :-)
#
# Revision 1.11  2003/04/04 23:54:30  ncq
# - tweaked some parent and style settings here and there, but still
#   not where we want to be with the pick list ...
#
# Revision 1.10  2003/04/04 20:46:45  ncq
# - adapt to new gmCurrentPatient()
# - add (ugly) tooltip
# - break out helper _display_name()
# - fix KeyError on ids[0]
#
# Revision 1.9  2003/04/01 16:01:06  ncq
# - fixed handling of no-patients-found result
#
# Revision 1.8  2003/04/01 15:33:22  ncq
# - and double :: of course, duh
#
# Revision 1.7  2003/04/01 15:32:52  ncq
# - stupid indentation error
#
# Revision 1.6  2003/04/01 12:28:14  ncq
# - factored out _normalize_soundalikes()
#
# Revision 1.5  2003/04/01 09:08:27  ncq
# - better Umlaut replacement
# - safer cursor.close() handling
#
# Revision 1.4  2003/03/31 23:38:16  ncq
# - sensitize() helper for smart names upcasing
# - massively rework queries for speedup
#
# Revision 1.3  2003/03/30 00:24:00  ncq
# - typos
# - (hopefully) less confusing printk()s at startup
#
# Revision 1.2  2003/03/28 15:56:04  ncq
# - adapted to GnuMed CVS structure
#
