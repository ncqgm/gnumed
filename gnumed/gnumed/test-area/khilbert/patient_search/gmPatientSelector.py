

#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/test-area/khilbert/patient_search/Attic/gmPatientSelector.py,v $
# $Id: gmPatientSelector.py,v 1.4 2003-03-25 12:29:27 ncq Exp $
__version__ = "$Revision: 1.4 $"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"

# access our modules
import sys, os.path, re
if __name__ == "__main__":
	sys.path.append(os.path.join('.', 'modules'))
	sys.path.append(os.path.join('.', 'business'))

import gmLog
_log = gmLog.gmDefLog
if __name__ == "__main__":
	_log.SetAllLogLevels(gmLog.lData)

import gmTmpPatient, gmDispatcher, gmSignals, gmPG

from wxPython.wx import *
#------------------------------------------------------------
ID_LISTCTRL = wxNewId()

#============================================================
# write your own query generator and add it here
#------------------------------------------------------------

# use compile() for speedup
# must escape strings before use !!
# ORDER BY !

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

	print "- this is a more complicated pattern"

	# try to split on (major) part separators
	parts_list = re.split(",|;", raw)
	print "major parts:", parts_list

	# only one "major" part ? (i.e. no ",;" ?
	if len(parts_list) == 1:
		# re-split on whitespace
		tmp = re.split("\s*|\t*", raw)
		print '"major" parts:', tmp

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
				queries[1].append("SELECT id FROM v_basic_person WHERE firstnames ILIKE '%s%%' AND lastnames ILIKE '%s%%' AND date_trunc('day', dob) like (select timestamp '%s');" % (name_parts[0], name_parts[1], date_part))
				# last, first, dob - second order query
				queries[2].append("SELECT id FROM v_basic_person WHERE firstnames ILIKE '%s%%' AND lastnames ILIKE '%s%%' AND date_trunc('day', dob) like (select timestamp '%s');" % (name_parts[1], name_parts[0], date_part))
				# name parts anywhere in name - third order query ...
				queries[3].append("SELECT id FROM v_basic_person WHERE firstnames || lastnames ILIKE '%%%s%%' AND firstnames || lastnames ILIKE '%%%s%%' AND date_trunc('day', dob) like (select timestamp '%s');" % (name_parts[0], name_parts[1], date_part))
				return queries
			# FIXME
			return queries

		# FIXME
		return queries

	# FIXME: what about "< 40" ?

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
		#EVT_LIST_ITEM_SELECTED(self, ID_LISTCTRL, self.OnItemCursor)
		EVT_LIST_ITEM_ACTIVATED(self, ID_LISTCTRL, self._on_item_activated)

		#EVT_BUTTON(self, ID_NEW, self.OnNew)
		#EVT_BUTTON(self, wxID_OK, self.OnOk)
		# FIXME: remove button, add evt char ESC
		EVT_BUTTON(self, wxID_CANCEL, self._on_cancel)
	#--------------------------------------------------------
	def SetItems(self, items = [], col_labels = []):
		# TODO: make selectable by 0-9

		self.items = items

		# set up columns
		self.listctrl.ClearAll()
		for col_idx in range(len(col_labels)):
			self.listctrl.InsertColumn(col_idx, col_labels[col_idx])
		# now add items
		for row_idx in range(len(self.items)):
			# set up item
			row = self.items[row_idx]
			# first column
			try:
				self.listctrl.InsertStringItem(row_idx, str(row[col_labels[0]]))
			except KeyError:
				_log.LogException('dict mismatch items <-> labels !', sys.exc_info())
				if self.items != []:
					_log.Log(gmLog.lData, "item keys: %s" % row.keys())
				else:
					_log.Log(gmLog.lData, "item keys: None")
				_log.Log(gmLog.lData, "labels   : %s" % col_labels)
			# subsequent columns
			for label in col_labels[1:]:
				try:
					self.listctrl.SetStringItem(row_idx, str(row[label]))
				except KeyError:
					_log.LogException('dict mismatch items <-> labels !', sys.exc_info())
					if self.items != []:
						_log.Log(gmLog.lData, "item keys: %s" % row.keys())
					else:
						_log.Log(gmLog.lData, "item keys: None")
					_log.Log(gmLog.lData, "labels   : %s" % col_labels)

		# adjust column width
		for col_idx in range(len(col_labels)):
			self.listctrl.SetColumnWidth(col_idx, wxLIST_AUTOSIZE)
	#--------------------------------------------------------
	# event handlers
	#--------------------------------------------------------
	def _on_item_activated(self, evt):
		idx = evt.m_itemIndex
		print "user activated item %s (double left-click or enter)" % idx
		item = self.items[idx]
		# the key "patient ID" is assumed to always exist
		try:
			self.EndModal(item['#'])
		except KeyError:
			_log.LogException('required key "#" missing, item keys: %s' % item.keys(), sys.exc_info())
			self.EndModal(-1)
	#--------------------------------------------------------
	def _on_cancel(self, evt):
		print "user cancelled dialog"
		self.EndModal(-1)
	#--------------------------------------------------------
	# utility methods
	#--------------------------------------------------------
	def _do_layout(self):
		self.szrMain = wxBoxSizer(wxVERTICAL)

		# make list
		self.listctrl = wxListCtrl(
			parent = self,
			id = ID_LISTCTRL,
			pos = wxDefaultPosition,
			size = wxSize(160,120),
			style = wxLC_REPORT | wxLC_SINGLE_SEL | wxLC_VRULES | wxVSCROLL | wxHSCROLL | wxSUNKEN_BORDER
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

		# get connection
		self.backend = gmPG.ConnectionPool()
		self.conn = self.backend.GetConnection('personalia')
		# FIXME: error handling

		self.prev_fragment = None
		self.prev_ids = []

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
	def SetActivePatient(self, anID = None):
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

		pat_data = []

		curs = self.conn.cursor()

		for cmd in query_list[1]:
			if not gmPG.run_query(curs, cmd):
				_log.Log(gmLog.lErr, 'Cannot fetch patient IDs.')
			else:
				data = curs.fetchall()
				pat_data.extend(data)

		if len(pat_data) == 0:
			for cmd in query_list[2]:
				if not gmPG.run_query(curs, cmd):
					_log.Log(gmLog.lErr, 'Cannot fetch patient IDs.')
				else:
					data = curs.fetchall()
					pat_data.extend(data)

		if len(pat_data) == 0:
			for cmd in query_list[3]:
				if not gmPG.run_query(curs, cmd):
					_log.Log(gmLog.lErr, 'Cannot fetch patient IDs.')
				else:
					data = curs.fetchall()
					pat_data.extend(data)

		curs.close()

		if len(pat_data) == 0:
			dlg = wxMessageDialog(
				NULL,
				_('Cannot find ANY matching patients !\nCurrently selected patient stays active.\n\n(We should offer to jump to entering a new patient from here.)'),
				_('selecting patient'),
				wxOK | wxICON_INFORMATION
			)
			dlg.ShowModal()
			dlg.Destroy()

		return pat_data
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
		curr_fragment = self.GetValue()
		if self.IsModified() and not re.match("^(\s|\t)*$", curr_fragment):
			self.prev_fragment = curr_fragment

		if gmTmpPatient.gmDefPatient is None:
			self.SetValue(value = _('no active patient'))
		else:
			name = gmTmpPatient.gmDefPatient['active name']
			self.SetValue(value = '%s, %s' % (name['last'], name['first']))
	#--------------------------------------------------------
	def _on_char(self, evt):
		keycode = evt.GetKeyCode()
		if evt.AltDown():

			# ALT-L, ALT-P - list of previously active patients
			if keycode in [ord('l'), ord('p')]:
				if self.prev_ids == []:
					return true
				# generate item list
				items = []
				for ID in self.prev_ids:
					row = {
						'#': ID
					}
					items.append(row)
				dlg = cPatientPickList(parent = self)
				# define order of cols
				labels = []
				labels.append('#')
				# set it
				dlg.SetItems(items, labels)
				# and show it
				result = dlg.ShowModal()
				if result == -1:
					print "user cancelled selection dialog"
				else:
					# and make our selection known to others
					self.SetActivePatient(result)
				return true

			# ALT-N
			if keycode == ord('n'):
				print "ALT-N not implemented yet"
				print "should immediately jump to entering a new patient"
				return true

			# ALT-K
			if keycode == ord('k'):
				print "ALT-K not implemented yet"
				print "should tell chipcard demon to read KVK and display list of cached KVKs"
				return true

		# cycling through previous fragments
		#elif keycode == WXK_DOWN:
			#print "<cursor-down> not implemented yet"
			#print "should cycle through search fragment history"
		elif keycode == WXK_UP:
			#print "<cursor-up> not fully implemented yet"
			#print "should cycle through search fragment history"
			if self.prev_fragment is not None:
				self.SetValue(self.prev_fragment)
			return true

		evt.Skip()
	#--------------------------------------------------------
	def _on_enter(self, evt):
		# remember fragment
		curr_fragment = self.GetValue()
		if self.IsModified() and not re.match("^(\s|\t)*$", curr_fragment):
			self.prev_fragment = curr_fragment

		# generate queries
		queries = self.generate_queries(self.GetValue())
		print queries[1]
		print queries[2]
		print queries[3]

		# get list of names
		ids = self._fetch_pat_ids(queries)
		if ids is None or len(ids) == 0:
			return true

		if len(ids) == 1:
			# and make our selection known to others
			self.SetActivePatient(ids[0][0])

			# remember patient if not yet remembered
			if ids[0][0] not in self.prev_ids:
				self.prev_ids.append(ids[0][0])
			# but only 10 of them
			if len(self.prev_ids) > 10:
				self.prev_ids.pop(0)

		else:
			print "several matching patients:"
			print ids
			print "trying to pop up list for selection"
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
#
#
# non-working:
#  Haywood, Ian <40
#  ?, Ian 1977
#  Ian Haywood, 19/12/77
#  PUPIC

#------------------------------------------------------------
# notes
# -----
# >> 3. There are countries in which people have more than one
# >> (significant) lastname (spanish-speaking countries are one case :), some
# >> asiatic countries might be another one).
# -> we need per-country query generators ...

# search case sensitive by default, switch to insensitive if not found ?

# phrase wheel is most likely too slow

# search fragment history

# ask user whether to send off level 3 queries - or thread them

# "- we don't expect patient IDs in complicated patterns"
# "- hence, any digits signify a date"
