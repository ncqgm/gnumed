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
# $Id: gmPatientSelector.py,v 1.13 2003-06-29 14:08:02 ncq Exp $
__version__ = "$Revision: 1.13 $"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"

# access our modules
import sys, os.path, re, time, string
if __name__ == "__main__":
	sys.path.append(os.path.join('..', 'python-common'))
	sys.path.append(os.path.join('..', 'business'))

import gmLog
_log = gmLog.gmDefLog
if __name__ == "__main__":
	_log.SetAllLogLevels(gmLog.lData)
import gmTmpPatient, gmDispatcher, gmSignals, gmPG, gmI18N, gmKVK

from wxPython.wx import *

ID_PatPickList = wxNewId()
#============================================================
def _sensitize(aName = None):
	"""Make user input suitable for case-sensitive matching.

	- this mostly applies to names
	- it will be correct in "most" cases

	- "beckert"  -> "Beckert"
	- "mcburney" -> "Mcburney" (probably wrong but hard to be smart about it)
	- "mcBurney" -> "McBurney" (try to preserver effort put in by the user)
	- "McBurney" -> "McBurney"
	"""
	if aName is None:
		return None
	else:
		return aName[:1].upper() + aName[1:]
#------------------------------------------------------------
def _normalize_soundalikes(aString = None, aggressive = 0):
	if aString is None:
		return None
	elif len(aString) == 0:
		return aString
	else:
		# umlauts
		normalized =    aString.replace('Ä', '(Ä|AE|Ae|E)')
		normalized = normalized.replace('Ö', '(Ö|OE|Oe)')
		normalized = normalized.replace('Ü', '(Ü|UE|Ue)')
		normalized = normalized.replace('ä', '(ä|ae|e)')
		normalized = normalized.replace('ö', '(ö|oe)')
		normalized = normalized.replace('ü', '(ü|ue|y)')
		normalized = normalized.replace('ß', '(ß|sz|ss)')
		# common soundalikes
		# - René, Desiré, ...
		normalized = normalized.replace('é', '(é|e)')
		# FIXME: how to sanely replace t -> th ?
		normalized = normalized.replace('Th', '(Th|T)')
		normalized = normalized.replace('th', '(th|t)')
		# FIXME: how to prevent replacing (f|v|ph) -> (f|(v|f|ph)|ph) ?
		#normalized = normalized.replace('v','(v|f|ph)')
		#normalized = normalized.replace('f','(f|v|ph)')
		#normalized = normalized.replace('ph','(ph|f|v)')

		if aggressive == 1:
			pass
			# some more here
		return normalized
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
	# - has been in this Quartal
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
# write your own query generator and add it here
#------------------------------------------------------------
# use compile() for speedup
# must escape strings before use !!
# ORDER BY !
# FIXME: what about "< 40" ?

def _make_simple_query(raw):
	queries = {
		1: [],
		2: [],
		3: []
	}
	# "<ZIFFERN>" - patient ID or DOB
	if re.match("^(\s|\t)*\d+(\s|\t)*$", raw):
		tmp = raw.replace(' ', '')
		tmp = tmp.replace('\t', '')
		queries[1].append("SELECT i_id, n_id FROM v_basic_person WHERE i_id LIKE '%s%%'" % tmp)
		queries[1].append("SELECT i_id, n_id FROM v_basic_person WHERE date_trunc('day', dob) LIKE (select timestamp '%s')" % raw)
		return queries

	# "#<ZIFFERN>" - patient ID
	if re.match("^(\s|\t)*#(\d|\s|\t)+$", raw):
		tmp = raw.replace(' ', '')
		tmp = tmp.replace('\t', '')
		tmp = tmp.replace('#', '')
		# this seemingly stupid query ensures the id actually exists
		queries[1].append("SELECT i_id, n_id FROM v_basic_person WHERE i_id LIKE '%s%%'" % tmp)
		return queries

	# "<Z I  FF ERN>" - DOB or patient ID
	if re.match("^(\d|\s|\t)+$", raw):
		queries[1].append("SELECT i_id, n_id FROM v_basic_person WHERE date_trunc('day', dob) LIKE (select timestamp '%s')" % raw)
		tmp = raw.replace(' ', '')
		tmp = tmp.replace('\t', '')
		queries[1].append("SELECT i_id, n_id FROM v_basic_person WHERE i_id LIKE '%s%%'" % tmp)
		return queries

	# "<Z(.|/|-/ )I  FF ERN>" - DOB
	if re.match("^(\s|\t)*\d+(\s|\t|\.|\-|/)*\d+(\s|\t|\.|\-|/)*\d+(\s|\t|\.)*$", raw):
		tmp = raw.replace(' ', '')
		tmp = tmp.replace('\t', '')
		# apparently not needed due to PostgreSQL smarts...
		#tmp = tmp.replace('-', '.')
		#tmp = tmp.replace('/', '.')
		queries[1].append("SELECT i_id, n_id FROM v_basic_person WHERE date_trunc('day', dob) LIKE (select timestamp '%s')" % tmp)
		return queries

	# "*|$<...>" - DOB
	if re.match("^(\s|\t)*(\*|\$).+$", raw):
		tmp = raw.replace('*', '')
		tmp = tmp.replace('$', '')
		queries[1].append("SELECT i_id, n_id FROM v_basic_person WHERE date_trunc('day', dob) LIKE (select timestamp '%s')" % tmp)
		return queries

	return None
#------------------------------------------------------------
def queries_de(raw = None):
	if raw is None:
		return []

	# check to see if we get away with a simple query ...
	queries = _make_simple_query(raw)
	if queries is not None:
		return queries

	# no we don't
	queries = []

	# replace Umlauts
	# (names of months do not contain Umlauts in German, so ...
	# actually this should be done when needed so we can
	# leave out raw[0] for the case-sensitive queries
	no_umlauts = _normalize_soundalikes(raw)
#	no_umlauts =        raw.replace('Ä', '(Ä|AE|Ae|E)')
#	no_umlauts = no_umlauts.replace('Ö', '(Ö|OE|Oe)')
#	no_umlauts = no_umlauts.replace('Ü', '(Ü|UE|Ue)')
#	no_umlauts = no_umlauts.replace('ä', '(ä|ae|e)')
#	no_umlauts = no_umlauts.replace('ö', '(ö|oe)')
#	no_umlauts = no_umlauts.replace('ü', '(ü|ue|y)')
#	no_umlauts = no_umlauts.replace('ß', '(ß|sz|ss)')
	# René, Desiré, ...
#	no_umlauts = no_umlauts.replace('é', '(é|e)')

	# "<CHARS>" - single name part
	# yes, I know, this is culture specific (did you read the docs ?)
	if re.match("^(\s|\t)*[a-zäöüßéáúóçøA-ZÄÖÜÇØ]+(\s|\t)*$", raw):
		# there's no intermediate whitespace due to the regex
		tmp = no_umlauts.strip()
		# assumption: this is a last name
		queries.append(["SELECT i_id, n_id FROM v_basic_person WHERE lastnames  ~ '^%s'" % _sensitize(tmp)])
		queries.append(["SELECT i_id, n_id FROM v_basic_person WHERE lastnames  ~* '^%s'" % tmp])
		# assumption: this is a first name
		queries.append(["SELECT i_id, n_id FROM v_basic_person WHERE firstnames ~ '^%s'" % _sensitize(tmp)])
		queries.append(["SELECT i_id, n_id FROM v_basic_person WHERE firstnames ~* '^%s'" % tmp])
		# name parts anywhere in name
		queries.append(["SELECT i_id, n_id FROM v_basic_person WHERE firstnames || lastnames ~* '%s'" % tmp])
		return queries

	# try to split on (major) part separators
	parts_list = re.split(",|;", no_umlauts)

	# only one "major" part ? (i.e. no ",;" ?)
	if len(parts_list) == 1:
		# re-split on whitespace
		sub_parts_list = re.split("\s*|\t*", no_umlauts)

		# parse into name/date parts
		date_count = 0
		name_parts = []
		for part in sub_parts_list:
			# any digit signifies a date
			# FIXME: what about "<40" ?
			if re.search("\d", part):
				date_count = date_count + 1
				date_part = part
			else:
				name_parts.append(part)

		# exactly 2 words ?
		if len(sub_parts_list) == 2:
			# no date = "first last" or "last first"
			if date_count == 0:
				# assumption: first last
				queries.append(
					[
					 "SELECT i_id, n_id FROM v_basic_person WHERE firstnames ~ '^%s' AND lastnames ~ '^%s'" % (_sensitize(name_parts[0]), _sensitize(name_parts[1]))
					]
				)
				queries.append([
					 "SELECT i_id, n_id FROM v_basic_person WHERE firstnames ~* '^%s' AND lastnames ~* '^%s'" % (name_parts[0], name_parts[1])
				])
				# assumption: last first
				queries.append([
					"SELECT i_id, n_id FROM v_basic_person WHERE firstnames ~ '^%s' AND lastnames ~ '^%s'" % (_sensitize(name_parts[1]), _sensitize(name_parts[0]))
				])
				queries.append([
					"SELECT i_id, n_id FROM v_basic_person WHERE firstnames ~* '^%s' AND lastnames ~* '^%s'" % (name_parts[1], name_parts[0])
				])
				# name parts anywhere in name - third order query ...
				queries.append([
					"SELECT i_id, n_id FROM v_basic_person WHERE firstnames || lastnames ~* '%s' AND firstnames || lastnames ~* '%s'" % (name_parts[0], name_parts[1])
				])
				return queries
			# FIXME: either "name date" or "date date"
			_log.Log(gmLog.lErr, "don't know how to generate queries for [%s]" % raw)
			return queries

		# exactly 3 words ?
		if len(sub_parts_list) == 3:
			# special case: 3 words, exactly 1 of them a date, no ",;"
			if date_count == 1:
				# assumption: first, last, dob - first order
				queries.append([
					"SELECT i_id, n_id FROM v_basic_person WHERE firstnames ~ '^%s' AND lastnames ~ '^%s' AND date_trunc('day', dob) LIKE (select timestamp '%s')" % (_sensitize(name_parts[0]), _sensitize(name_parts[1]), date_part)
				])
				queries.append([
					"SELECT i_id, n_id FROM v_basic_person WHERE firstnames ~* '^%s' AND lastnames ~* '^%s' AND date_trunc('day', dob) LIKE (select timestamp '%s')" % (name_parts[0], name_parts[1], date_part)
				])
				# assumption: last, first, dob - second order query
				queries.append([
					"SELECT i_id, n_id FROM v_basic_person WHERE firstnames ~ '^%s' AND lastnames ~ '^%s' AND date_trunc('day', dob) LIKE (select timestamp '%s')" % (_sensitize(name_parts[1]), _sensitize(name_parts[0]), date_part)
				])
				queries.append([
					"SELECT i_id, n_id FROM v_basic_person WHERE firstnames ~* '^%s' AND lastnames ~* '^%s' AND date_trunc('day', dob) LIKE (select timestamp '%s')" % (name_parts[1], name_parts[0], date_part)
				])
				# name parts anywhere in name - third order query ...
				queries.append([
					"SELECT i_id, n_id FROM v_basic_person WHERE firstnames || lastnames ~* '%s' AND firstnames || lastnames ~* '%s' AND date_trunc('day', dob) LIKE (select timestamp '%s')" % (name_parts[0], name_parts[1], date_part)
				])
				return queries
			# FIXME: "name name name" or "name date date"
			_log.Log(gmLog.lErr, "don't know how to generate queries for [%s]" % raw)
			return queries

		# FIXME: no ',;' but neither "name name" nor "name name date"
		_log.Log(gmLog.lErr, "don't know how to generate queries for [%s]" % raw)
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

		wheres = []
		# first, handle name parts
		# special case: "<date(s)>, <name> <name>, <date(s)>"
		if (len(name_parts) == 1) and (name_count == 2):
			# usually "first last"
			wheres.append([
				"firstnames ~ '^%s'" % _sensitize(name_parts[0][0]),
				"lastnames ~ '^%s'"  % _sensitize(name_parts[0][1])
			])
			wheres.append([
				"firstnames ~* '^%s'" % name_parts[0][0],
				"lastnames ~* '^%s'" % name_parts[0][1]
			])
			# but sometimes "last first""
			wheres.append([
				"firstnames ~ '^%s'" % _sensitize(name_parts[0][1]),
				"lastnames ~ '^%s'"  % _sensitize(name_parts[0][0])
			])
			wheres.append([
				"firstnames ~* '^%s'" % name_parts[0][1],
				"lastnames ~* '^%s'" % name_parts[0][0]
			])
			# or even substrings anywhere in name
			wheres.append([
				"firstnames || lastnames ~* '%s'" % name_parts[0][0],
				"firstnames || lastnames ~* '%s'" % name_parts[0][1]
			])

		# special case: "<date(s)>, <name(s)>, <name(s)>, <date(s)>"
		elif len(name_parts) == 2:
			# usually "last, first"
			wheres.append([
				"firstnames ~ '^%s'" % string.join(map(_sensitize, name_parts[1]), ' '),
				"lastnames ~ '^%s'"  % string.join(map(_sensitize, name_parts[0]), ' ')
			])
			wheres.append([
				"firstnames ~* '^%s'" % string.join(name_parts[1], ' '),
				"lastnames ~* '^%s'" % string.join(name_parts[0], ' ')
			])
			# but sometimes "first, last"
			wheres.append([
				"firstnames ~ '^%s'" % string.join(map(_sensitize, name_parts[0]), ' '),
				"lastnames ~ '^%s'"  % string.join(map(_sensitize, name_parts[1]), ' ')
			])
			wheres.append([
				"firstnames ~* '^%s'" % string.join(name_parts[0], ' '),
				"lastnames ~* '^%s'" % string.join(name_parts[1], ' ')
			])
			# or even substrings anywhere in name
			wheres.append([
				"firstnames || lastnames ~* '%s'" % string.join(name_parts[0], ' '),
				"firstnames || lastnames ~* '%s'" % string.join(name_parts[1], ' ')
			])

		# big trouble - arbitrary number of names
		else:
			# FIXME: deep magic, not sure of rationale ...
			if len(name_parts) == 1:
				for part in name_parts[0]:
					wheres.append([
						"firstnames || lastnames ~* '%s'" % part
					])
					wheres.append([
						"firstnames || lastnames ~* '%s'" % part
					])
			else:
				tmp = []
				for part in name_parts:
					tmp.append(string.join(part, ' '))
				for part in tmp:
					wheres.append([
						"firstnames || lastnames ~* '%s'" % part
					])
					wheres.append([
						"firstnames || lastnames ~* '%s'" % part
					])

		# secondly handle date parts
		# FIXME: this needs a considerable smart-up !
		if len(date_parts) == 1:
			if len(wheres) > 0:
				wheres[0].append("date_trunc('day', dob) LIKE (select timestamp '%s')" % date_parts[0])
			else:
				wheres.append([
					"date_trunc('day', dob) LIKE (select timestamp '%s')" % date_parts[0]
				])
			if len(wheres) > 1:
				wheres[1].append("date_trunc('day', dob) LIKE (select timestamp '%s')" % date_parts[0])
			else:
				wheres.append([
					"date_trunc('day', dob) LIKE (select timestamp '%s')" % date_parts[0]
				])
		elif len(date_parts) > 1:
			if len(wheres) > 0:
				wheres[0].append("date_trunc('day', dob) LIKE (select timestamp '%s')" % date_parts[0])
				wheres[0].append("date_trunc('day', identity.deceased) LIKE (select timestamp '%s'" % date_parts[1])
			else:
				wheres.append([
					"date_trunc('day', dob) LIKE (select timestamp '%s')" % date_parts[0],
					"date_trunc('day', identity.deceased) LIKE (select timestamp '%s'" % date_parts[1]
				])
			if len(wheres) > 1:
				wheres[1].append("date_trunc('day', dob) LIKE (select timestamp '%s')" % date_parts[0])
				wheres[1].append("date_trunc('day', identity.deceased) LIKE (select timestamp '%s')" % date_parts[1])
			else:
				wheres.append([
					"date_trunc('day', dob) LIKE (select timestamp '%s')" % date_parts[0],
					"date_trunc('day', identity.deceased) LIKE (select timestamp '%s')" % date_parts[1]
				])

		# and finally generate the queries ...
		for where_clause in wheres:
			if len(where_clause) > 0:
				queries.append([
					"SELECT i_id, n_id FROM v_basic_person WHERE %s" % string.join(where_clause, ' AND ')
				])
			else:
				queries.append([])
		return queries

	return []
#------------------------------------------------------------
query_generator = {
	'default': queries_de,
	'de': queries_de
}
#============================================================
class cPatientPickList(wxDialog):
	def __init__(
		self,
		parent,
		id = -1,
		title = _('please select a patient'),
		pos = (-1, -1),
		size = (320, 240),
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

		#won't work on Windoze otherwise:
		self.listctrl.SetFocus()

#============================================================
class cPatientSelector(wxTextCtrl):
	"""Widget for smart search for patients."""
	def __init__ (self, parent, id = -1, pos = (-1, -1), size = (-1, -1)):
		self.curr_pat = gmTmpPatient.gmCurrentPatient()

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
to search, type any of:\n - fragment of last or first name\n - date of birth (can start with '$' or '*')\n - patient ID (can start with '#')\nand hit <ENTER>
<ALT-L> or <ALT-P>\n - list of *L*ast/*P*revious patients\n<ALT-K> or <ALT-C>\n - list of *K*VKs/*C*hipcards\n<CURSOR-UP>\n - recall most recently used search term
""")
		self.SetToolTip(wxToolTip(selector_tooltip))

		self._display_name()

		# FIXME: is this necessary ?
		self.parent = parent

		# set locale dependant query handlers
		# - generator
		try:
			self.generate_queries = query_generator[gmI18N.system_locale_level['full']]
		except KeyError:
			try:
				self.generate_queries = query_generator[gmI18N.system_locale_level['country']]
			except KeyError:
				try:
					self.generate_queries = query_generator[gmI18N.system_locale_level['language']]
				except KeyError:
					self.generate_queries = query_generator['default']
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
		# - process some special chars
		EVT_CHAR(self, self._on_char)

		# - select data in input field upon tabbing in
		EVT_SET_FOCUS (self, self._on_get_focus)

		# - redraw the currently active name upon losing focus
		#   (but see the caveat in the handler)
		EVT_KILL_FOCUS (self, self._on_loose_focus)

		# - user pressed <enter>
		EVT_TEXT_ENTER (self, self.GetId(), self._on_enter)

	#--------------------------------------------------------
	def SetActivePatient(self, anID = None, data = None):
		if anID is None:
			return None

		if anID == self.curr_pat['ID']:
			return None

		old_ID = self.curr_pat['ID']
		self.curr_pat = gmTmpPatient.gmCurrentPatient(aPKey = anID)
		if old_ID == self.curr_pat['ID']:
			_log.LogException('cannot change active patient', sys.exc_info())
			# error message ?
			return None

		self._display_name()

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
	def _fetch_pat_ids(self, query_lists = None):
		# anything to do ?
		if query_lists is None:
			_log.Log(gmLog.lErr, 'query tree empty')
			return None
		try:
			if query_lists[0] == []:
				_log.Log(gmLog.lWarn, 'query tree empty ?')
				_log.Log(gmLog.lWarn, query_lists)
				return None
		except KeyError:
			_log.Log(gmLog.lErr, 'query tree syntax wrong')
			_log.Log(gmLog.lErr, query_lists)
			return None

		pat_ids = []

		curs = self.conn.cursor()
		for query_list in query_lists:
			_log.Log(gmLog.lData, "running %s" % query_list)
			# try all queries at this query level
			for cmd in query_list:
				if not gmPG.run_query(curs, cmd):
					_log.Log(gmLog.lErr, 'cannot fetch patient IDs')
				else:
					rows = curs.fetchall()
					pat_ids.extend(rows)
			# if we got patients don't try more query levels
			if len(pat_ids) > 0:
				break
		curs.close()

		return pat_ids
	#--------------------------------------------------------
	def _display_name(self):
		name = self.curr_pat['active name']
		if name is None:
			self.SetValue(_('no active patient'))
		else:
			self.SetValue('%s, %s' % (name['last'], name['first']))
	#--------------------------------------------------------
	# event handlers
	#--------------------------------------------------------
	def _on_get_focus(self, evt):
		"""uponn tabbing in

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

		# generate queries
		queries = self.generate_queries(curr_search_term)

		# get list of matching ids
		start = time.time()
		ids = self._fetch_pat_ids(queries)
		duration = time.time() - start
		print "%s patient IDs fetched in %3.3f seconds" % (len(ids), duration)

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
# Revision 1.13  2003-06-29 14:08:02  ncq
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
