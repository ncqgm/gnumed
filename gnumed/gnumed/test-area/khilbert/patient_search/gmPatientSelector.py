

#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/test-area/khilbert/patient_search/Attic/gmPatientSelector.py,v $
# $Id: gmPatientSelector.py,v 1.2 2003-03-25 01:24:57 ncq Exp $
__version__ = "$Revision: 1.2 $"
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
	if re.match("^(\s|\t)*[a-zA-Z]+(\s|\t)*$", raw):
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
	print "- we don't expect patient IDs in complicated patterns"
	print "- hence, any digits signify a date"

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

		# set event handlers
		# ------------------
		# validate upon losing focus but see the caveat in the handler
		EVT_KILL_FOCUS (self, self._on_loose_focus)

		# user pressed <enter>
		EVT_TEXT_ENTER (self, self.GetId(), self._on_enter)

		# evil user wants to resize widget
		#EVT_SIZE (self, self.on_resize)

	#--------------------------------------------------------
	# utility methods
	#--------------------------------------------------------
	def _fetch_pat_data(self, query_list = None):
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
				_('Cannot find ANY matching patients !\nCurrently selected patient stays active.'),
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
		if gmTmpPatient.gmDefPatient is None:
			self.SetValue(value = _('no active patient'))
		else:
			name = gmTmpPatient.gmDefPatient['active name']
			self.SetValue(value = '%s, %s' % (name['last'], name['first']))
	#--------------------------------------------------------
	def _on_enter(self, evt):
		# generate queries
		queries = self.generate_queries(self.GetValue())
		print queries

		# get list of names
		names = self._fetch_pat_data(queries)
		if names is None or len(names) == 0:
			return true

		if len(names) == 1:
			# and make our selection known to others
			kwargs = {
				'ID': names[0][0],
				'signal': gmSignals.patient_selected(),
				'sender': 'patient.selector'
			}
			gmDispatcher.send(gmSignals.patient_selected(), kwds=kwargs)

			name = gmTmpPatient.gmDefPatient['active name']
			self.SetValue(value = '%s, %s' % (name['last'], name['first']))
		else:
			print "need to implement selection from list"
			print names
#============================================================
# main
#------------------------------------------------------------
if __name__ == "__main__":

	kwargs = {}
	kwargs['ID'] = 1
	kwargs['signal']= gmSignals.patient_selected()
	kwargs['sender'] = 'patient.selector'
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
# - hitting cursor-down (alt-L = List, alt-P = previous ?)
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
