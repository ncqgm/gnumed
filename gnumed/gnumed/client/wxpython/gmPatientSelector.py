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
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/Attic/gmPatientSelector.py,v $
# $Id: gmPatientSelector.py,v 1.30 2004-02-25 09:46:22 ncq Exp $
__version__ = "$Revision: 1.30 $"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"

# access our modules
import sys, os.path, time, string, re
if __name__ == "__main__":
	sys.path.append(os.path.join('..', 'pycommon'))
	sys.path.append(os.path.join('..', 'business'))

import gmLog
_log = gmLog.gmDefLog
if __name__ == "__main__":
	_log.SetAllLogLevels(gmLog.lData)
import gmPatient, gmDispatcher, gmSignals, gmPG, gmI18N, gmKVK, gmGuiHelpers

from wxPython.wx import *

ID_PatPickList = wxNewId()
#============================================================
# country-specific functions
#------------------------------------------------------------
def pat_expand_default(curs = None, ID_list = None):
	if ID_list is None:
		return ([], [])

	if curs is None:
		return ([], [])

	pat_data = []

	# FIXME: add more data here
	# - last visit
	# - appointment
	# - current waiting time
	# - presence
	# - KVK indicator
	# - been here this Quartal
	# ...
	# Note: this query must ALWAYS return the ID in field 0
	cmd = "SELECT i_id, n_id, lastnames, firstnames, to_char(dob, 'DD.MM.YYYY') FROM v_basic_person WHERE i_id in (%s) and n_id in (%s)" % \
		(string.join(map(lambda x:str(x[0]), ID_list), ','), string.join(map(lambda x:str(x[1]), ID_list), ','))

	if not gmPG.run_query(curs, cmd):
		_log.Log(gmLog.lErr, 'Cannot fetch patient data.')
	else:
		pat_data = curs.fetchall()

	col_order = [
		{'label': _('last name'),	'data idx': 2},
		{'label': _('first name'),	'data idx': 3},
		{'label': _('dob'),			'data idx': 4}
	]
	return pat_data, col_order
#------------------------------------------------------------
patient_expander = {
	'default': pat_expand_default,
	'de': pat_expand_default
}
#============================================================
class cPatientPickList(wxDialog):
	def __init__(
		self,
		parent,
		id = -1,
		title = _('please select a patient'),
		pos = (-1, -1),
		size = (600, 400),
	):
		wxDialog.__init__(
			self,
			parent,
			id,
			title,
			pos,
			size,
			style = wxDEFAULT_DIALOG_STYLE | wxRESIZE_BORDER | wxSTAY_ON_TOP
		)

		self._do_layout()
		self.items = []

		# set event handlers
		#EVT_LIST_ITEM_SELECTED(self, ID_PatPickList, self.OnItemCursor)
		EVT_LIST_ITEM_ACTIVATED(self, ID_PatPickList, self._on_item_activated)

		#EVT_BUTTON(self, ID_NEW, self.OnNew)
		#EVT_BUTTON(self, wxID_OK, self.OnOk)
		# FIXME: remove button, add evt char ESC
		EVT_BUTTON(self, wxID_CANCEL, self._on_cancel)
	#--------------------------------------------------------
	def SetItems(self, items = [], col_order = []):
		# TODO: make selectable by 0-9

		self.items = items

		# set up columns
		self.listctrl.ClearAll()
		for order_idx in range(len(col_order)):
			self.listctrl.InsertColumn(order_idx, col_order[order_idx]['label'])

		# now add items
		for row_idx in range(len(self.items)):
			# set up item
			row = self.items[row_idx]
			# first column
			try:
				self.listctrl.InsertStringItem(row_idx, str(row[col_order[0]['data idx']]))
			except KeyError:
				_log.LogException('dict mismatch items <-> labels !', sys.exc_info())
				if self.items != []:
					_log.Log(gmLog.lData, "item keys: %s" % row.keys())
				else:
					_log.Log(gmLog.lData, "item keys: None")
				_log.Log(gmLog.lData, "labels   : %s" % col_order)
			# subsequent columns
			for order_idx in range(1, len(col_order)):
				try:
					self.listctrl.SetStringItem(row_idx, order_idx, str(row[col_order[order_idx]['data idx']]))
				except KeyError:
					_log.LogException('dict mismatch items <-> labels !', sys.exc_info())
					if self.items != []:
						_log.Log(gmLog.lData, "item keys: %s" % row.keys())
					else:
						_log.Log(gmLog.lData, "item keys: None")
					_log.Log(gmLog.lData, "labels   : %s" % col_order)

		# adjust column width
		for order_idx in range(len(col_order)):
			self.listctrl.SetColumnWidth(order_idx, wxLIST_AUTOSIZE)

		# FIXME: and make ourselves just big enough
		self.szrMain.Fit(self)
		self.Fit()
#		self.
	#--------------------------------------------------------
	# event handlers
	#--------------------------------------------------------
	def _on_item_activated(self, evt):
		# item dict must always contain ID to be used for selection later on at index 0
		item = self.items[evt.m_itemIndex]
		try:
			self.EndModal(item[0])
		except KeyError:
			_log.LogException('item [%s] has faulty structure' % item, sys.exc_info())
			self.EndModal(-1)
	#--------------------------------------------------------
	def _on_cancel(self, evt):
		self.EndModal(-1)
	#--------------------------------------------------------
	# utility methods
	#--------------------------------------------------------
	def _do_layout(self):
		self.szrMain = wxBoxSizer(wxVERTICAL)

		# make list
		self.listctrl = wxListCtrl(
			parent = self,
			id = ID_PatPickList,
			style = wxLC_REPORT | wxLC_SINGLE_SEL | wxVSCROLL | wxHSCROLL | wxSUNKEN_BORDER
		)
		# and place it
		self.szrMain.AddWindow(self.listctrl, 1, wxGROW | wxALIGN_CENTER_VERTICAL, 5)

		# make buttons
		self.szrButtons = wxBoxSizer(wxHORIZONTAL)
#		self.btnOK = wxButton (
#			self,
#			wxID_OK,
#			_("&OK"),
#			wxDefaultPosition,
#			wxDefaultSize,
#			0
#		)
#		self.szrButtons.AddWindow(self.btnOK, 1, wxALIGN_CENTRE, 5)

#		self.btnNew = wxButton (
#			self,
#			ID_NEW,
#			_("&New"),
#			wxDefaultPosition,
#			wxDefaultSize,
#			0
#		)
#		self.szrButtons.AddWindow(self.btnNew, 1, wxALIGN_CENTRE, 5)

		self.btnCancel = wxButton (
			self,
			wxID_CANCEL,
			_("&Cancel"),
			wxDefaultPosition,
			wxDefaultSize,
			0
		)
		self.szrButtons.AddWindow(self.btnCancel, 1, wxALIGN_CENTRE, 5)

		# and place them
		self.szrMain.AddSizer(self.szrButtons, 0, wxGROW|wxALIGN_CENTER_VERTICAL, 5)

		self.SetAutoLayout(true)
		self.SetSizer(self.szrMain)
		self.szrMain.Fit(self)
		self.szrMain.SetSizeHints(self)

		# won't work on Windoze otherwise:
		self.listctrl.SetFocus()

#============================================================
class cPatientSelector(wxTextCtrl):
	"""Widget for smart search for patients."""
	def __init__ (self, parent, id = -1, pos = (-1, -1), size = (-1, -1)):
		self.curr_pat = gmPatient.gmCurrentPatient()

		# need to explicitely process ENTER events to avoid
		# them being handed over to the next control
		wxTextCtrl.__init__(
			self,
			parent,
			id,
			'',
			pos,
			size,
			style = wxTE_PROCESS_ENTER
		)
		selector_tooltip = _( \
"""Patient search field.                                   \n
to search, type any of:
 - fragment of last or first name
 - date of birth (can start with '$' or '*')
 - patient ID (can start with '#')
and hit <ENTER>
<ALT-L> or <ALT-P>
 - list of *L*ast/*P*revious patients
<ALT-K> or <ALT-C>
 - list of *K*VKs/*C*hipcards
<CURSOR-UP>
 - recall most recently used search term
""")
		self.SetToolTip(wxToolTip(selector_tooltip))

		self._display_name()

		# FIXME: is this necessary ?
		self.parent = parent

		# FIXME: set query generator
		self.pat_searcher = gmPatient.cPatientSearcher_SQL()

		# - retriever
		try:
			self.pat_expander = patient_expander[gmI18N.system_locale_level['full']]
		except KeyError:
			try:
				self.pat_expander = patient_expander[gmI18N.system_locale_level['country']]
			except KeyError:
				try:
					self.pat_expander = patient_expander[gmI18N.system_locale_level['language']]
				except KeyError:
					self.pat_expander = patient_expander['default']

		# get connection
		self.backend = gmPG.ConnectionPool()
		self.conn = self.backend.GetConnection('personalia')
		# FIXME: error handling

		self.prev_search_term = None
		self.prev_pats = []
		self.prev_col_order = []

		# set event handlers
		self.__register_events()

	#--------------------------------------------------------
	def __register_events(self):
		# - process some special chars
		EVT_CHAR(self, self._on_char)
		# - select data in input field upon tabbing in
		EVT_SET_FOCUS (self, self._on_get_focus)
		# - redraw the currently active name upon losing focus
		#   (but see the caveat in the handler)
		EVT_KILL_FOCUS (self, self._on_loose_focus)
		# - user pressed <enter>
		EVT_TEXT_ENTER (self, self.GetId(), self._on_enter)

		# client internal signals
		gmDispatcher.connect(signal=gmSignals.patient_selected(), receiver=self._on_patient_selected)
	#----------------------------------------------
	def _on_patient_selected(self, **kwargs):
		wxCallAfter(self._display_name)
	#--------------------------------------------------------
	def SetActivePatient(self, anID = None, data = None):
		if not gmPatient.set_active_patient(anID):
			_log.Log (gmLog.lErr, 'cannot change active patient')
			return None

		# remember patient
		if data is not None:
			# only unique patients
			for prev_pat in self.prev_pats:
				if prev_pat[0] == anID:
					return true
			self.prev_pats.append(data)

			# and only 10 of them
			if len(self.prev_pats) > 10:
				self.prev_pats.pop(0)
	#--------------------------------------------------------
	# utility methods
	#--------------------------------------------------------
	def _display_name(self):
		if self.curr_pat.is_connected():
			name = self.curr_pat['demographic record'].getActiveName()
			self.SetValue('%s, %s' % (name['last'], name['first']))
		else:
			self.SetValue(_('no active patient'))
	#--------------------------------------------------------
	# event handlers
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
		# if we use EVT_KILL_FOCUS we will also receive this event
		# when closing our application or loosing focus to another
		# application which is NOT what we intend to achieve,
		# however, this is the least ugly way of doing this due to
		# certain vagaries of wxPython (see the Wiki)

		# remember fragment
		curr_search_term = self.GetValue()
		if self.IsModified() and not re.match("^(\s|\t)*$", curr_search_term):
			self.prev_search_term = curr_search_term

		# and display currently active patient
		self._display_name()
		evt.Skip()
	#--------------------------------------------------------
	def _on_char(self, evt):
		keycode = evt.GetKeyCode()

		if evt.AltDown():
			# ALT-L, ALT-P - list of previously active patients
			if keycode in [ord('l'), ord('p')]:
				if self.prev_pats == []:
					return true
				# show list
				dlg = cPatientPickList(parent = NULL)
				dlg.SetItems(self.prev_pats, self.prev_col_order)
				result = dlg.ShowModal()
				dlg.Destroy()
				# and process selection
				if result > 0:
					# and make our selection known to others
					self.SetActivePatient(result)
				return true

			# ALT-N - enter new patient
			if keycode == ord('n'):
				print "ALT-N not implemented yet"
				print "should immediately jump to entering a new patient"
				return true

			# ALT-K - access chipcards
			if keycode in [ord('k'), ord('c')]:
				# FIXME: make configurable !!
				kvks = gmKVK.get_available_kvks('~/gnumed/kvk/incoming/')
				if kvks is None:
					print "No KVKs available !"
					# show some message here ...
					return true
				picklist, col_order = gmKVK.kvks_extract_picklist(kvks)
				# show list
				dlg = cPatientPickList(parent = NULL, title = _("please select a KVK"))
				dlg.SetItems(picklist, col_order)
				result = dlg.ShowModal()
				dlg.Destroy()
				# and process selection
				if result != -1:
					print "user selected kvkd file %s" % picklist[result][10]
					print picklist[result]
				return true

		# cycling through previous fragments
		elif keycode == WXK_UP:
			if self.prev_search_term is not None:
				self.SetValue(self.prev_search_term)
			return true
		
#		elif keycode == WXK_DOWN:
#			pass

		evt.Skip()
	#--------------------------------------------------------
	def _on_enter(self, evt):
		curr_search_term = self.GetValue()
		# remember fragment
		if self.IsModified() and not re.match("^(\s|\t)*$", curr_search_term):
			self.prev_search_term = curr_search_term

		# get list of matching ids
		start = time.time()
		ids = self.pat_searcher.get_patient_ids(curr_search_term)
		duration = time.time() - start
		print "%s patient ID(s) fetched in %3.3f seconds" % (len(ids), duration)

		if ids is None or len(ids) == 0:
			dlg = wxMessageDialog(
				NULL,
				_('Cannot find ANY matching patients for search term\n"%s" !\nCurrently selected patient stays active.\n\n(We should offer to jump to entering a new patient from here.)' % curr_search_term),
				_('selecting patient'),
				wxOK | wxICON_EXCLAMATION
			)
			dlg.ShowModal()
			dlg.Destroy()
			return true

		curs = self.conn.cursor()
		# only one matching patient
		if len(ids) == 1:
			# and make our selection known to others
			data, self.prev_col_order = self.pat_expander(curs, ids)
			curs.close()
			self.SetActivePatient(ids[0][0], data[0])
		else:
			# get corresponding patient data
			start = time.time()
			pat_list, self.prev_col_order = self.pat_expander(curs, ids)
			duration = time.time() - start
			print "patient data fetched in %3.3f seconds" % duration
			curs.close()

			# and let user select from pick list
			dlg = cPatientPickList(parent = NULL)
			dlg.SetItems(pat_list, self.prev_col_order)
			result = dlg.ShowModal()
			dlg.Destroy()
			for pat in pat_list:
				if pat[0] == result:
					self.SetActivePatient(result, pat)
					break
#============================================================
# main
#------------------------------------------------------------
if __name__ == "__main__":
	app = wxPyWidgetTester(size = (200, 40))
	app.SetWidget(cPatientSelector, -1)
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
# - hitting cursor-up (alt-K = KVK, alt-C = Chipkarte ?)
#   - signal chipcard demon to read card
#   - AND display list of available cards read
#   - scrolling in list
#   - ENTER selects patient and imports card data
#   - ESC cancels selection
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
# >> asiatic countries might be another one).
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
# $Log: gmPatientSelector.py,v $
# Revision 1.30  2004-02-25 09:46:22  ncq
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
