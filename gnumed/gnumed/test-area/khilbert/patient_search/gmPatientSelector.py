"""GnuMed quick patient search widget.

This widget allows to search for patients based on the
critera name, date of birth and patient ID. It goes to
considerable length to understand the user's intent from
her input. For that to work well we need per-culture
query generators. However, there's always the fallback
generator.
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/test-area/khilbert/patient_search/Attic/gmPatientSelector.py,v $
# $Id: gmPatientSelector.py,v 1.8 2003-03-27 21:04:58 ncq Exp $
__version__ = "$Revision: 1.8 $"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"

# access our modules
import sys, os.path, re, time, string
if __name__ == "__main__":
	sys.path.append(os.path.join('.', 'modules'))
	sys.path.append(os.path.join('.', 'business'))

import gmLog
_log = gmLog.gmDefLog
if __name__ == "__main__":
	_log.SetAllLogLevels(gmLog.lData)
	import gmI18N

import gmTmpPatient, gmDispatcher, gmSignals, gmPG

from wxPython.wx import *
#------------------------------------------------------------
ID_PatPickList = wxNewId()

#============================================================
# country-specific functions
#------------------------------------------------------------
def pat_expand_default(curs = None, ID_list = None):
	if ID_list is None:
		return {}

	if curs is None:
		return {}

	pat_data = []

	# FIXME: add more data here
	# - last visit
	# - appointment
	# - current waiting time
	# - presence
	# - KVK indicator
	# - has been in this Quartal
	# ...
	# Note: this query must ALWAYS return the ID in field 0
	cmd = "SELECT id, lastnames, firstnames, to_char(dob, 'DD.MM.YYYY') FROM v_basic_person WHERE id in (%s);" % string.join(map(str, ID_list), ',')

	if not gmPG.run_query(curs, cmd):
		_log.Log(gmLog.lErr, 'Cannot fetch patient data.')
	else:
		pat_data = curs.fetchall()

	col_order = [
		{'label': _('last name'),	'data idx': 1},
		{'label': _('first name'),	'data idx': 2},
		{'label': _('dob'),			'data idx': 3}
	]
	return pat_data, col_order
#------------------------------------------------------------
patient_expander = {
	'default': pat_expand_default,
	'de_DE@euro': pat_expand_default
}
#============================================================
# write your own query generator and add it here
#------------------------------------------------------------

# use compile() for speedup
# must escape strings before use !!
# ORDER BY !
# FIXME: what about "< 40" ?

def queries_default(raw = None):
	if raw is None:
		return []

	queries = {
		1: [],
		2: [],
		3: []
	}

	# "<ZIFFERN>" - patient ID or DOB
	if re.match("^(\s|\t)*\d+(\s|\t)*$", raw):
		tmp = raw.replace(' ', '')
		tmp = tmp.replace('\t', '')
		queries[1].append("SELECT id FROM v_basic_person WHERE id LIKE '%s%%';" % tmp)
		queries[1].append("SELECT id FROM v_basic_person WHERE date_trunc('day', dob) LIKE (select timestamp '%s');" % raw)
		return queries

	# "<CHARS>" - single name part
	# yes, I know (did you read the docs carefully ?)
	if re.match("^(\s|\t)*[a-zA-ZäÄöÖüÜß]+(\s|\t)*$", raw):
		tmp = raw.replace(' ', '')
		tmp = tmp.replace('\t', '')
		queries[1].append("SELECT id FROM v_basic_person WHERE lastnames  ILIKE '%s%%';" % tmp)
		queries[2].append("SELECT id FROM v_basic_person WHERE firstnames ILIKE '%s%%';" % tmp)
		# name parts anywhere in name - third order query ...
		queries[3].append("SELECT id FROM v_basic_person WHERE firstnames || lastnames ILIKE '%%%s%%';" % tmp)
		return queries

	# "#<ZIFFERN>" - patient ID
	if re.match("^(\s|\t)*#(\d|\s|\t)+$", raw):
		tmp = raw.replace(' ', '')
		tmp = tmp.replace('\t', '')
		tmp = tmp.replace('#', '')
		# this seemingly stupid query ensures the id actually exists
		queries[1].append("SELECT id FROM v_basic_person WHERE id LIKE '%s%%';" % tmp)
		return queries

	# "<Z I  FF ERN>" - DOB or patient ID
	if re.match("^(\d|\s|\t)+$", raw):
		queries[1].append("SELECT id FROM v_basic_person WHERE date_trunc('day', dob) LIKE (select timestamp '%s');" % raw)
		tmp = raw.replace(' ', '')
		tmp = tmp.replace('\t', '')
		queries[1].append("SELECT id FROM v_basic_person WHERE id LIKE '%s%%';" % tmp)
		return queries

	# "<Z(.|/|-/ )I  FF ERN>" - DOB
	if re.match("^(\s|\t)*\d+(\s|\t|\.|\-|/)*\d+(\s|\t|\.|\-|/)*\d+(\s|\t|\.)*$", raw):
		tmp = raw.replace(' ', '')
		tmp = tmp.replace('\t', '')
		# apparently not needed due to PostgreSQL smarts...
		#tmp = tmp.replace('-', '.')
		#tmp = tmp.replace('/', '.')
		queries[1].append("SELECT id FROM v_basic_person WHERE date_trunc('day', dob) LIKE (select timestamp '%s');" % tmp)
		return queries

	# "*|$<...>" - DOB
	if re.match("^(\s|\t)*(\*|\$).+$", raw):
		tmp = raw.replace('*', '')
		tmp = tmp.replace('$', '')
		queries[1].append("SELECT id FROM v_basic_person WHERE date_trunc('day', dob) LIKE (select timestamp '%s');" % tmp)
		return queries

	# try to split on (major) part separators
	parts_list = re.split(",|;", raw)

	# only one "major" part ? (i.e. no ",;" ?)
	if len(parts_list) == 1:
		# re-split on whitespace
		tmp = re.split("\s*|\t*", raw)

		# parse into name/date parts
		date_count = 0
		name_parts = []
		for part in tmp:
			# any digit signifies a date
			# FIXME: what about "<40" ?
			if re.search("\d", part):
				date_count = date_count + 1
				date_part = part
			else:
				name_parts.append(part)

		# exactly 2 words ?
		if len(tmp) == 2:
			# no date = "first last" or "last first"
			if date_count == 0:
				queries[1].append("SELECT id FROM v_basic_person WHERE firstnames ILIKE '%s%%' AND lastnames ILIKE '%s%%';" % (name_parts[0], name_parts[1]))
				queries[2].append("SELECT id FROM v_basic_person WHERE firstnames ILIKE '%s%%' AND lastnames ILIKE '%s%%';" % (name_parts[1], name_parts[0]))
				# name parts anywhere in name - third order query ...
				queries[3].append("SELECT id FROM v_basic_person WHERE firstnames || lastnames ILIKE '%%%s%%' AND firstnames || lastnames ILIKE '%%%s%%';" % (name_parts[0], name_parts[1]))
				return queries
			# FIXME
			return queries

		# exactly 3 words ?
		if len(tmp) == 3:
			# special case: 3 words, exactly 1 of them a date, no ",;"
			if date_count == 1:
				# first, last, dob - first order
				queries[1].append("SELECT id FROM v_basic_person WHERE firstnames ILIKE '%s%%' AND lastnames ILIKE '%s%%' AND date_trunc('day', dob) LIKE (select timestamp '%s');" % (name_parts[0], name_parts[1], date_part))
				# last, first, dob - second order query
				queries[2].append("SELECT id FROM v_basic_person WHERE firstnames ILIKE '%s%%' AND lastnames ILIKE '%s%%' AND date_trunc('day', dob) LIKE (select timestamp '%s');" % (name_parts[1], name_parts[0], date_part))
				# name parts anywhere in name - third order query ...
				queries[3].append("SELECT id FROM v_basic_person WHERE firstnames || lastnames ILIKE '%%%s%%' AND firstnames || lastnames ILIKE '%%%s%%' AND date_trunc('day', dob) LIKE (select timestamp '%s');" % (name_parts[0], name_parts[1], date_part))
				return queries
			# FIXME
			return queries

		# FIXME
		return queries

	# more than one major part (separated by ';,')
	else:
		# parse into name and date parts
		date_parts = []
		name_parts = []
		name_count = 0
		for part in parts_list:
			# any digits ?
			if re.search("\d+", part):
				# FIXME: parse out whitespace *not* adjacent to a *word*
				date_parts.append(part)
			else:
				tmp = part.strip()
				tmp = re.split("\s*|\t*", tmp)
				name_count = name_count + len(tmp)
				name_parts.append(tmp)

		where1 = []
		where2 = []
		where3 = []

		# handle name parts first
		# special case: "<date(s)>, <name> <name>, <date(s)>"
		if (len(name_parts) == 1) and (name_count == 2):
			# usually "first name  last name"
			# so check this version first
			where1.append("firstnames ILIKE '%s%%'" % name_parts[0][0])
			where1.append("lastnames ILIKE '%s%%'"  % name_parts[0][1])

			where2.append("firstnames ILIKE '%s%%'" % name_parts[0][1])
			where2.append("lastnames ILIKE '%s%%'"  % name_parts[0][0])

			where3.append("firstnames || lastnames ILIKE '%%%s%%'" % name_parts[0][0])
			where3.append("firstnames || lastnames ILIKE '%%%s%%'" % name_parts[0][1])

		# special case: "<date(s)>, <name(s)>, <name(s)>, <date(s)>"
		elif len(name_parts) == 2:
			# usually "last name(s), first name(s)"
			# so check this version first
			where1.append("firstnames ILIKE '%s%%'" % string.join(name_parts[1], ' '))
			where1.append("lastnames ILIKE '%s%%'" % string.join(name_parts[0], ' '))

			where2.append("firstnames ILIKE '%s%%'" % string.join(name_parts[0], ' '))
			where2.append("lastnames ILIKE '%s%%'" % string.join(name_parts[1], ' '))

			where3.append("firstnames || lastnames ILIKE '%%%s%%'" % string.join(name_parts[0], ' '))
			where3.append("firstnames || lastnames ILIKE '%%%s%%'" % string.join(name_parts[1], ' '))

		# big trouble - arbitrary number of names
		else:
			if len(name_parts) == 1:
				for part in name_parts[0]:
					where1.append("firstnames || lastnames ILIKE '%%%s%%'" % part)
					where2.append("firstnames || lastnames ILIKE '%%%s%%'" % part)
			else:
				tmp = []
				for part in name_parts:
					tmp.append(string.join(part, ' '))
				for part in tmp:
					where1.append("firstnames || lastnames ILIKE '%%%s%%'" % part)
					where2.append("firstnames || lastnames ILIKE '%%%s%%'" % part)

		# secondly handle date parts
		# FIXME: this needs a considerable smart-up !
		if len(date_parts) == 1:
			where1.append("date_trunc('day', dob) LIKE (select timestamp '%s')" % date_parts[0])
			where2.append("date_trunc('day', dob) LIKE (select timestamp '%s')" % date_parts[0])
		elif len(date_parts) > 1:
			where1.append("date_trunc('day', dob) LIKE (select timestamp '%s')" % date_parts[0])
			where1.append("date_trunc('day', identity.deceased) LIKE (select timestamp '%s'" % date_parts[1])

			where2.append("date_trunc('day', dob) LIKE (select timestamp '%s')" % date_parts[0])
			where2.append("date_trunc('day', identity.deceased) LIKE (select timestamp '%s')" % date_parts[1])

		if len(where1) > 0:
			queries[1].append("SELECT id FROM v_basic_person WHERE %s" % string.join(where1, ' AND '))
		if len(where2) > 0:
			queries[2].append("SELECT id FROM v_basic_person WHERE %s" % string.join(where2, ' AND '))
		if len(where3) > 0:
			queries[3].append("SELECT id FROM v_basic_person WHERE %s" % string.join(where3, ' AND '))
		return queries

	return queries
#------------------------------------------------------------
query_generator = {
	'default': queries_default,
	'de_DE@euro': queries_default
}
#============================================================
class cPatientPickList(wxDialog):
	def __init__(
		self,
		parent,
		id = -1,
		pos = wxPyDefaultPosition,
		size = wxPyDefaultSize,
	):
		wxDialog.__init__(
			self,
			parent,
			id,
			_('please select a patient'),
			pos,
			size,
			style = wxDEFAULT_DIALOG_STYLE | wxRESIZE_BORDER
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

		# and make ourselves just big enough
		#self.szrMain.Fit(self)
		#self.Fit()
	#--------------------------------------------------------
	# event handlers
	#--------------------------------------------------------
	def _on_item_activated(self, evt):
		item = self.items[evt.m_itemIndex]
		# the key "#" is assumed to always exist
		try:
			self.EndModal(item[0])
		except KeyError:
			_log.LogException('required key "#" missing, item keys: %s' % item.keys(), sys.exc_info())
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
			pos = wxDefaultPosition,
			size = wxSize(160,120),
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

		#won't work on Windoze otherwise:
		self.listctrl.SetFocus()
#============================================================
class cPatientSelector(wxTextCtrl):
	"""Widget for smart search for patients."""
	def __init__ (self, parent, id = -1, pos = wxDefaultPosition, size = wxDefaultSize):

		name = gmTmpPatient.gmDefPatient['active name']
		val = "%s, %s" % (name['last'], name['first'])

		# need to explicitely process ENTER events to avoid
		# them being handed over to the next control
		wxTextCtrl.__init__(
			self,
			parent,
			id,
			val,
			pos,
			size,
			style = wxTE_PROCESS_ENTER
		)
		self.SetBackgroundColour (wxColour (200, 100, 100))
		self.parent = parent

		# FIXME ! -> locale dependant
		self.generate_queries = query_generator['default']
		self.pat_expander = patient_expander['default']

		# get connection
		self.backend = gmPG.ConnectionPool()
		self.conn = self.backend.GetConnection('personalia')
		# FIXME: error handling

		self.prev_search_term = None
		self.prev_pats = []
		self.prev_col_order = []

		# set event handlers
		# ------------------
		# process some special chars
		EVT_CHAR(self, self._on_char)

		# validate upon losing focus but see the caveat in the handler
		EVT_KILL_FOCUS (self, self._on_loose_focus)

		# user pressed <enter>
		EVT_TEXT_ENTER (self, self.GetId(), self._on_enter)

		# evil user wants to resize widget
		#EVT_SIZE (self, self.on_resize)
	#--------------------------------------------------------
	def SetActivePatient(self, anID = None, data = None):
		if anID is None:
			return None

		kwargs = {
			'ID': anID,
			'signal': gmSignals.patient_selected(),
			'sender': 'patient.selector'
		}
		gmDispatcher.send(gmSignals.patient_selected(), kwds=kwargs)
		name = gmTmpPatient.gmDefPatient['active name']
		self.SetValue(value = '%s, %s' % (name['last'], name['first']))

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
	def _fetch_pat_ids(self, query_list = None):
		if query_list is None:
			_log.Log(gmLog.lErr, 'query tree empty')
			return None
		try:
			# anything to do ?
			if query_list[1] == []:
				_log.Log(gmLog.lWarn, 'query tree empty ?')
				_log.Log(gmLog.lWarn, query_list)
				return None
		except KeyError:
			_log.Log(gmLog.lErr, 'query tree syntax wrong')
			_log.Log(gmLog.lErr, query_list)
			return None

		pat_ids = []
		curs = self.conn.cursor()

		_log.Log(gmLog.lData, "level 1: running %s" % query_list[1])
		for cmd in query_list[1]:
			if not gmPG.run_query(curs, cmd):
				_log.Log(gmLog.lErr, 'Cannot fetch patient IDs.')
			else:
				rows = curs.fetchall()
				for pat_id in rows:
					pat_ids.extend(pat_id)

		if len(pat_ids) == 0:
			_log.Log(gmLog.lData, "level 2: running %s" % query_list[2])
			for cmd in query_list[2]:
				if not gmPG.run_query(curs, cmd):
					_log.Log(gmLog.lErr, 'Cannot fetch patient IDs.')
				else:
					rows = curs.fetchall()
					for pat_id in rows:
						pat_ids.extend(pat_id)

		if len(pat_ids) == 0:
			_log.Log(gmLog.lData, "level 3: running %s" % query_list[3])
			for cmd in query_list[3]:
				if not gmPG.run_query(curs, cmd):
					_log.Log(gmLog.lErr, 'Cannot fetch patient IDs.')
				else:
					rows = curs.fetchall()
					for pat_id in rows:
						pat_ids.extend(pat_id)

		curs.close()

		if len(pat_ids) == 0:
			dlg = wxMessageDialog(
				NULL,
				_('Cannot find ANY matching patients !\nCurrently selected patient stays active.\n\n(We should offer to jump to entering a new patient from here.)'),
				_('selecting patient'),
				wxOK | wxICON_EXCLAMATION
			)
			dlg.ShowModal()
			dlg.Destroy()

		return pat_ids
	#--------------------------------------------------------
	# event handlers
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
		if gmTmpPatient.gmDefPatient is None:
			self.SetValue(value = _('no active patient'))
		else:
			name = gmTmpPatient.gmDefPatient['active name']
			self.SetValue(value = '%s, %s' % (name['last'], name['first']))
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
				dlg = cPatientPickList(parent = self)
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
			if keycode == ord('k'):
				print "ALT-K not implemented yet"
				print "should tell chipcard demon to read KVK and display list of cached KVKs"
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

		# generate queries
		queries = self.generate_queries(curr_search_term)

		# get list of matching ids
		start = time.time()
		ids = self._fetch_pat_ids(queries)
		end = time.time()
		print "%s patient IDs fetched in %s seconds" % (len(ids), (end - start))
		if ids is None or len(ids) == 0:
			return true

		curs = self.conn.cursor()
		# only one matching patient
		if len(ids) == 1:
			# and make our selection known to others
			data, self.prev_col_order = self.pat_expander(curs, ids)
			self.SetActivePatient(ids[0], data[0])
		else:
			# generate patient data to display from ID list
			start = time.time()
			pat_list, self.prev_col_order = self.pat_expander(curs, ids)
			duration = time.time() - start
			print "patient data fetched in %s seconds" % duration

			# generate list dialog
			dlg = cPatientPickList(parent = self)
			dlg.SetItems(pat_list, self.prev_col_order)
			# and show it
			result = dlg.ShowModal()
			dlg.Destroy()
			if result in ids:
				# and make our selection known to others
				for pat in pat_list:
					if pat[0] == result:
						self.SetActivePatient(result, pat)
						break
		curs.close()
#============================================================
# main
#------------------------------------------------------------
if __name__ == "__main__":

	kwargs = {}
	kwargs['ID'] = 1
	kwargs['signal']= gmSignals.patient_selected()
	kwargs['sender'] = 'main'
	gmDispatcher.send(gmSignals.patient_selected(), kwds=kwargs)

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

# phrase wheel is most likely too slow

# extend search fragment history

# ask user whether to send off level 3 queries - or thread them

# we don't expect patient IDs in complicated patterns, hence any digits signify a date

# FIXME: make list window fit list size ...

# clear search field upon get-focus ?

# F1 -> context help with hotkey listing
