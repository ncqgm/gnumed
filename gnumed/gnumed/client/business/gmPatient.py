# -*- encoding: latin-1 -*-
"""GnuMed patient objects.

This is a patient object intended to let a useful client-side
API crystallize from actual use in true XP fashion.

license: GPL
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/business/Attic/gmPatient.py,v $
# $Id: gmPatient.py,v 1.48 2004-07-20 10:09:44 ncq Exp $
__version__ = "$Revision: 1.48 $"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"

# access our modules
import sys, os.path, time, re, string

from Gnumed.pycommon import gmLog, gmExceptions, gmPG, gmSignals, gmDispatcher, gmBorg, gmPyCompat, gmI18N, gmNull
from Gnumed.business import gmClinicalRecord, gmDemographicRecord, gmMedDoc

_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)

#============================================================
# may get preloaded by the waiting list
class gmPerson:
	"""Represents a person that DOES EXIST in the database.

	Accepting this as a hard-and-fast rule WILL simplify
	internal logic and remove some corner cases, I believe.

	- searching and creation is done OUTSIDE this object
	"""
	# handlers for __getitem__
	_get_handler = {}

	def __init__(self, aPKey = None):
		self.__ID = aPKey			# == identity.id == primary key
		if not self._pkey_exists():
			raise gmExceptions.ConstructorError, "No person with ID [%s] in database." % aPKey

		self.__db_cache = {}

		# register backend notification interests ...
		if not self._register_interests():
			raise gmExceptions.ConstructorError, "Cannot register person modification interests."

		_log.Log(gmLog.lData, 'Instantiated person [%s].' % self.__ID)
	#--------------------------------------------------------
	def cleanup(self):
		"""Do cleanups before dying.

		- note that this may be called in a thread
		"""
		_log.Log(gmLog.lData, 'cleaning up after person [%s]' % self.__ID)
		if self.__db_cache.has_key('clinical record'):
			self.__db_cache['clinical record'].cleanup()
			del self.__db_cache['clinical record']
		if self.__db_cache.has_key('demographic record'):
			self.__db_cache['demographic record'].cleanup()
			del self.__db_cache['demographic record']
		# FIXME: document folder
	#--------------------------------------------------------
	# internal helper
	#--------------------------------------------------------
	def _pkey_exists(self):
		"""Does this primary key exist ?

		- true/false/None
		"""
		cmd = "select exists(select id from identity where id = %s)"
		res = gmPG.run_ro_query('personalia', cmd, None, self.__ID)
		if res is None:
			_log.Log(gmLog.lErr, 'check for person ID [%s] existence failed' % self.__ID)
			return None
		return res[0][0]
	#--------------------------------------------------------
	def _register_interests(self):
		return 1
	#--------------------------------------------------------
	# __getitem__ handling
	#--------------------------------------------------------
	def __getitem__(self, aVar = None):
		"""Return any attribute if known how to retrieve it.
		"""
		try:
			return gmPerson._get_handler[aVar](self)
		except KeyError:
			_log.LogException('Missing get handler for [%s]' % aVar, sys.exc_info())
			return None
	#--------------------------------------------------------
	def getID(self):
		return self.__ID
	#--------------------------------------------------------
	def _getMedDocsList(self):
		"""Build a complete list of metadata for all documents of this person.
		"""
		cmd = "SELECT id from doc_med WHERE patient_id=%s"
		tmp = gmPG.run_ro_query('blobs', cmd, None, self.__ID)
		_log.Log(gmLog.lData, "document IDs: %s" % tmp)
		if tmp is None:
			return []
		docs = []
		for doc_id in tmp:
			if doc_id is not None:
				docs.extend(doc_id)
		if len(docs) == 0:
			_log.Log(gmLog.lInfo, "No documents found for person (ID [%s])." % self.__ID)
			return None
		return docs
	#----------------------------------------------------------
	def get_clinical_record(self):
		try:
			return self.__db_cache['clinical record']
		except KeyError:
			pass
		tstart = time.time()
		try:
			self.__db_cache['clinical record'] = gmClinicalRecord.cClinicalRecord(aPKey = self.__ID)
		except StandardError:
			_log.LogException('cannot instantiate clinical record for person [%s]' % self.__ID, sys.exc_info())
			return None
		duration = time.time() - tstart
		print "get_clinical_record() took %s seconds" % duration
		return self.__db_cache['clinical record']
	#--------------------------------------------------------
	def get_demographic_record(self):
		if self.__db_cache.has_key('demographic record'):
			return self.__db_cache['demographic record']
		tstart = time.time()
		try:
			# FIXME: we need some way of setting the type of backend such that
			# to instantiate the correct type of demographic record class
			self.__db_cache['demographic record'] = gmDemographicRecord.cDemographicRecord_SQL(aPKey = self.__ID)
		except StandardError:
			_log.LogException('cannot instantiate demographic record for person [%s]' % self.__ID, sys.exc_info())
			return None
		duration = time.time() - tstart
		print "get_demographic_record() took %s seconds" % duration
		return self.__db_cache['demographic record']
	#--------------------------------------------------------
	def get_document_folder(self):
		try:
			return self.__db_cache['document folder']
		except KeyError:
			pass
		try:
			# FIXME: we need some way of setting the type of backend such that
			# to instantiate the correct type of document folder class
			self.__db_cache['document folder'] = gmMedDoc.cDocumentFolder(aPKey = self.__ID)
		except StandardError:
			_log.LogException('cannot instantiate document folder for person [%s]' % self.__ID, sys.exc_info())
			return None
		return self.__db_cache['document folder']
	#--------------------------------------------------------
	def export_data(self):
		data = {}
		emr = self.get_clinical_record()
		if emr is None:
			return None
		data['clinical'] = emr.get_text_dump()
		return data
	#--------------------------------------------------------
	def _get_API(self):
		API = []
		for handler in gmPerson._get_handler.keys():
			data = {}
			# FIXME: how do I get an unbound method object ?
			func = self._get_handler[handler]
			data['API call name'] = handler
			data['internal name'] = func.__name__
#			data['reported by'] = method.im_self
#			data['defined by'] = method.im_class
			data['description'] = func.__doc__
			API.append(data)
		return API
	#--------------------------------------------------------
	# set up handler map
	_get_handler['demographic record'] = get_demographic_record
	_get_handler['document folder'] = get_document_folder
	_get_handler['API'] = _get_API
	_get_handler['ID'] = getID

#============================================================
class gmCurrentPatient(gmBorg.cBorg):
	"""Patient Borg to hold currently active patient.

	There may be many instances of this but they all share state.
	"""
	def __init__(self, aPKey = None):
		# share state among all instances ...
		gmBorg.cBorg.__init__(self)

		# make sure we do have a patient pointer
		if not self.__dict__.has_key('_patient'):
			self._patient = gmNull.cNull()

		# set initial lock state,
		# this lock protects against activating another patient
		# when we are controlled from a remote application
		if not self.__dict__.has_key('locked'):
			self.unlock()

		# - user wants copy of current patient
		if aPKey is None:
			# do nothing which will return ourselves
#			if self._patient is None:
#				tmp = 'None'
#			else:
#				tmp = str(self._patient['ID'])
			_log.Log(gmLog.lData, 'current patient (%s) requested' % self._patient['ID'])
			return None

		# possibly change us, depending on PKey
#		_log.Log(gmLog.lData, 'patient [%s] requested' % aPKey)
		# no previous patient
#		if self._patient is None:
#			_log.Log(gmLog.lData, 'no previous patient')
#			try:
#				self._patient = gmPerson(aPKey)
#			except:
#				_log.LogException('cannot connect with patient [%s]' % aPKey, sys.exc_info())
#				return None
			# remote app must lock explicitly
#			self.unlock()
#			self.__send_selection_notification()
#			return None

		# user wants change of current patient
		_log.Log(gmLog.lData, 'patient change [%s] -> [%s] requested' % (self._patient['ID'], aPKey))
		# are we really supposed to become someone else ?
		if self._patient['ID'] == aPKey:
			# no, same patient, do nothing
			_log.Log(gmLog.lData, 'same ID, no change needed')
			return None

		# yes, but CAN we ?
		if self.locked is not None:
			# no
			_log.Log(gmLog.lErr, 'patient [%s] is locked, cannot change to [%s]' % (self._patient['ID'], aPKey))
			return None
		# yes
		try:
			tmp = gmPerson(aPKey)
		except:
			_log.LogException('cannot connect with patient [%s]' % aPKey, sys.exc_info())
			# returning None (and thereby silently staying
			# the same patient) is a design decision
			# FIXME: maybe raise exception here ?
			return None

		# clean up after ourselves
		self.__send_pre_selection_notification()
		self._patient.cleanup()
		# and change to new patient
		self._patient = tmp
		self.unlock()
		self.__send_selection_notification()

		return None
	#--------------------------------------------------------
	def cleanup(self):
		self._patient.cleanup()
	#--------------------------------------------------------
	def get_clinical_record(self):
		return self._patient.get_clinical_record()
	#--------------------------------------------------------
	def get_demographic_record(self):
		return self._patient.get_demographic_record()
	#--------------------------------------------------------
	def get_document_folder(self):
		return self._patient.get_document_folder()
	#--------------------------------------------------------
	def get_ID(self):
#		if self._patient is None:
#			return None
		return self._patient.getID()
	#--------------------------------------------------------
	def export_data(self):
#		if self._patient is None:
#			return None
		return self._patient.export_data()
	#--------------------------------------------------------
# this MAY eventually become useful when we start
# using more threads in the frontend
#	def init_lock(self):
#		"""initializes a pthread lock. Doesn't matter if 
#		race of 2 threads in alock assignment, just use the 
#		last lock created ( unless both threads find no alock,
#		then one thread sleeps before self.alock = .. is completed ,
#		the other thread assigns a new RLock object, 
#		and begins immediately using it on a call to self.lock(),
#		and gets past self.alock.acquire()
#		before the first thread wakes up and assigns to self.alock 
#		, obsoleting
#		the already in use alock by the second thread )."""
#		try:
#			if  not self.__dict__.has_key('alock') :
#				self.alock = threading.RLock()
#		except:
#			_log.LogException("Cannot test/create lock", sys.exc_info()) 
	#--------------------------------------------------------
	# patient change handling
	#--------------------------------------------------------
	def lock(self):
		self.locked = 1
	#--------------------------------------------------------
	def unlock(self):
		self.locked = None
	#--------------------------------------------------------
	def is_locked(self):
		return self.locked
	#--------------------------------------------------------
	def __send_selection_notification(self):
		"""Sends signal when another patient has actually been made active."""
		kwargs = {
			'ID': self._patient['ID'],
			'signal': gmSignals.patient_selected(),
			'sender': id(self.__class__)
		}
		gmDispatcher.send(gmSignals.patient_selected(), kwds=kwargs)
	#--------------------------------------------------------
	def __send_pre_selection_notification(self):
		"""Sends signal when another patient is about to become active."""
		kwargs = {
			'ID': self._patient['ID'],
			'signal': gmSignals.activating_patient(),
			'sender': id(self.__class__)
		}
		gmDispatcher.send(gmSignals.activating_patient(), kwds=kwargs)
	#--------------------------------------------------------
	def is_connected(self):
		if isinstance(self._patient, gmNull.cNull):
			return False
		else:
			return True
	#--------------------------------------------------------
	# __getitem__ handling
	#--------------------------------------------------------
	def __getitem__(self, aVar = None):
		"""Return any attribute if known how to retrieve it by proxy.
		"""
		return self._patient[aVar]
#		if self._patient is not None:
#			return self._patient[aVar]
#		else:
#			return None
#============================================================
class cPatientSearcher_SQL:
	"""UI independant i18n aware patient searcher."""
	def __init__(self):
		# list more generators here once they are written
		self.__query_generators = {
			'default': self.__generate_queries_de,
			'de': self.__generate_queries_de
		}
		# set locale dependant query handlers
		# - generator
		try:
			self.__generate_queries = self.__query_generators[gmI18N.system_locale_level['full']]
		except KeyError:
			try:
				self.__generate_queries = self.__query_generators[gmI18N.system_locale_level['country']]
			except KeyError:
				try:
					self.__generate_queries = self.__query_generators[gmI18N.system_locale_level['language']]
				except KeyError:
					self.__generate_queries = self.__query_generators['default']
		# make a cursor
#		self.conn = gmPG.ConnectionPool().GetConnection('personalia', extra_verbose=gmPyCompat.True)
		self.conn = gmPG.ConnectionPool().GetConnection('personalia')
		self.curs = self.conn.cursor()
	#--------------------------------------------------------
	def __del__(self):
		try:
			self.curs.close()
		except: pass
		try:
			self.conn.close()
		except: pass
	#--------------------------------------------------------
	# public API
	#--------------------------------------------------------
	def get_patient_ids(self, search_term = None, a_locale = None, search_dict = None):
		"""Get patient IDs for given parameters.

		- either search term or search dict
		- search dict contains structured data that doesn't need to be parsed
		- search_dict takes precedence over search_term

		- returns flat list of patient PKs
		"""
		do_parsing = (search_dict is None)
		if not do_parsing:
			query_lists = self.__generate_queries_generic(search_dict)
			if query_lists is None:
				do_parsing = True
			if len(query_lists) == 0:
				do_parsing = True
		if do_parsing:
			# temporary change of locale for selecting query generator
			if a_locale is not None:
				print "temporary change of locale on patient search not implemented"
				_log.Log(gmLog.lWarn, "temporary change of locale on patient search not implemented")
			# generate queries
			if search_term is None:
				_log.Log(gmLog.lErr, 'need search term')
				return None
			query_lists = self.__generate_queries(search_term)

		# anything to do ?
		if query_lists is None:
			_log.Log(gmLog.lErr, 'query tree empty')
			return None
		if len(query_lists) == 0:
			_log.Log(gmLog.lErr, 'query tree empty')
			return None

		# collect IDs here
		pat_ids = []
		# cycle through query levels
		for query_list in query_lists:
			_log.Log(gmLog.lData, "running %s" % query_list)
			# try all queries at this query level
			for cmd in query_list:
				# FIXME: actually, we should pass in the parsed search_term
				if search_dict is None:
					rows = gmPG.run_ro_query(self.curs, cmd)
				else:
					rows = gmPG.run_ro_query(self.curs, cmd, None, search_dict)
				if rows is None:
					_log.Log(gmLog.lErr, 'cannot fetch patient IDs')
				else:
					pat_ids.extend(rows)
			# if we got patients don't try more query levels
			if len(pat_ids) > 0:
				break

		pat_id_list = []
		for row in pat_ids:
			pat_id_list.append(row[0])
		return pat_id_list
	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def __make_sane_caps(self, aName = None):
		"""Make user input suitable for case-sensitive matching.

		- this mostly applies to names
		- it will be correct in "most" cases

		- "beckert"  -> "Beckert"
		- "mcburney" -> "Mcburney" (probably wrong but hard to be smart about it)
		- "mcBurney" -> "McBurney" (try to preserve effort put in by the user)
		- "McBurney" -> "McBurney"
		"""
		if aName is None:
			return None
		else:
			return aName[:1].upper() + aName[1:]
	#--------------------------------------------------------
	def __normalize_soundalikes(self, aString = None, aggressive = 0):
		"""Transform some characters into a regex for their sound-alikes."""
		if aString is None:
			return None
		if len(aString) == 0:
			return aString

		# umlauts
		normalized =    aString.replace(u'Ä', u'(Ä|AE|Ae|E)')
		normalized = normalized.replace(u'Ö', u'(Ö|OE|Oe)')
		normalized = normalized.replace(u'Ü', u'(Ü|UE|Ue)')
		normalized = normalized.replace(u'ä', u'(ä|ae|e)')
		normalized = normalized.replace(u'ö', u'(ö|oe)')
		normalized = normalized.replace(u'ü', u'(ü|ue|y)')
		normalized = normalized.replace(u'ß', u'(ß|sz|ss)')
		# common soundalikes
		# - René, Desiré, ...
		normalized = normalized.replace(u'é', u'(é|e)')
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
	#--------------------------------------------------------
	# write your own query generator and add it here:
	# use compile() for speedup
	# must escape strings before use !!
	# ORDER BY !
	# FIXME: what about "< 40" ?

	def __make_simple_query(self, raw):
		"""Compose queries if search term seems unambigous."""
		queries = []

		# "<ZIFFERN>" - patient ID or DOB
		if re.match("^(\s|\t)*\d+(\s|\t)*$", raw):
			tmp = raw.replace(' ', '')
			tmp = tmp.replace('\t', '')
			queries.append(["SELECT i_id FROM v_basic_person WHERE i_id LIKE '%s%%'" % tmp])
			queries.append(["SELECT i_id FROM v_basic_person WHERE dob='%s'::timestamp" % raw])
			return queries

		# "#<ZIFFERN>" - patient ID
		if re.match("^(\s|\t)*#(\d|\s|\t)+$", raw):
			tmp = raw.replace(' ', '')
			tmp = tmp.replace('\t', '')
			tmp = tmp.replace('#', '')
			# this seemingly stupid query ensures the id actually exists
			queries.append(["SELECT i_id FROM v_basic_person WHERE i_id = '%s'" % tmp])
#			queries.append(["SELECT i_id FROM v_basic_person WHERE i_id LIKE '%s%%'" % tmp])
			return queries

		# "<Z I  FF ERN>" - DOB or patient ID
		if re.match("^(\d|\s|\t)+$", raw):
			queries.append(["SELECT i_id FROM v_basic_person WHERE dob='%s'::timestamp" % raw])
			tmp = raw.replace(' ', '')
			tmp = tmp.replace('\t', '')
			queries.append(["SELECT i_id FROM v_basic_person WHERE i_id LIKE '%s%%'" % tmp])
			return queries

		# "<Z(.|/|-/ )I  FF ERN>" - DOB
		if re.match("^(\s|\t)*\d+(\s|\t|\.|\-|/)*\d+(\s|\t|\.|\-|/)*\d+(\s|\t|\.)*$", raw):
			tmp = raw.replace(' ', '')
			tmp = tmp.replace('\t', '')
			# apparently not needed due to PostgreSQL smarts...
			#tmp = tmp.replace('-', '.')
			#tmp = tmp.replace('/', '.')
			queries.append(["SELECT i_id FROM v_basic_person WHERE dob='%s'::timestamp" % tmp])
			return queries

		# "*|$<...>" - DOB
		if re.match("^(\s|\t)*(\*|\$).+$", raw):
			tmp = raw.replace('*', '')
			tmp = tmp.replace('$', '')
			queries.append(["SELECT i_id FROM v_basic_person WHERE dob='%s'::timestamp" % tmp])
			return queries

		return None
	#--------------------------------------------------------
	# generic, locale independant queries
	#--------------------------------------------------------
	def __generate_queries_generic(self, data = None):
		"""Generate generic queries.

		- not locale dependant
		- data -> firstnames, lastnames, dob, gender
		"""
		if data is None:
			return []

		vals = {}
		where_snippets = []
		try:
			data['firstnames']
			where_snippets.append('firstnames=%(firstnames)s')
		except KeyError:
			pass
		try:
			data['lastnames']
			where_snippets.append('lastnames=%(lastnames)s')
		except KeyError:
			pass
		queries = []
		if where_snippets:
			queries.append(['select id_identity from names where %s' % ' and '.join(where_snippets)])
		where_snippets = []
		try:
			data['dob']
			where_snippets.append("dob=%(dob)s::timestamp")
		except KeyError:
			pass
		try:
			data['gender']
			where_snippets.append('gender=%(gender)s')
		except KeyError:
			pass

		queries.append(['select i_id from v_basic_person where %s' % ' and '.join(where_snippets)])
		# sufficient data ?
		if len(queries) == 0:
			_log.Log(gmLog.lErr, 'invalid search dict structure')
			_log.Log(gmLog.lData, data)
			return []
		# shall we mogrify name parts ? probably not
		
		return queries
	#--------------------------------------------------------
	# queries for DE
	#--------------------------------------------------------
	def __generate_queries_de(self, a_search_term = None):
		if a_search_term is None:
			return []

		# check to see if we get away with a simple query ...
		queries = self.__make_simple_query(a_search_term)
		if queries is not None:
			return queries

		# no we don't
		queries = []

		# replace Umlauts
		no_umlauts = self.__normalize_soundalikes(a_search_term)

		# "<CHARS>" - single name part
		# yes, I know, this is culture specific (did you read the docs ?)
		if re.match("^(\s|\t)*[a-zäöüßéáúóçøA-ZÄÖÜÇØ]+(\s|\t)*$", a_search_term):
			# there's no intermediate whitespace due to the regex
			tmp = no_umlauts.strip()
			# assumption: this is a last name
			queries.append(["SELECT DISTINCT id_identity FROM names WHERE lastnames  ~ '^%s'" % self.__make_sane_caps(tmp)])
			queries.append(["SELECT DISTINCT id_identity FROM names WHERE lastnames  ~* '^%s'" % tmp])
			# assumption: this is a first name
			queries.append(["SELECT DISTINCT id_identity FROM names WHERE firstnames ~ '^%s'" % self.__make_sane_caps(tmp)])
			queries.append(["SELECT DISTINCT id_identity FROM names WHERE firstnames ~* '^%s'" % tmp])
			# name parts anywhere in name
			queries.append(["SELECT DISTINCT id_identity FROM names WHERE firstnames || lastnames ~* '%s'" % tmp])
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
						 "SELECT DISTINCT id_identity FROM names WHERE firstnames ~ '^%s' AND lastnames ~ '^%s'" % (self.__make_sane_caps(name_parts[0]), self.__make_sane_caps(name_parts[1]))
						]
					)
					queries.append([
						 "SELECT DISTINCT id_identity FROM names WHERE firstnames ~* '^%s' AND lastnames ~* '^%s'" % (name_parts[0], name_parts[1])
					])
					# assumption: last first
					queries.append([
						"SELECT DISTINCT id_identity FROM names WHERE firstnames ~ '^%s' AND lastnames ~ '^%s'" % (self.__make_sane_caps(name_parts[1]), self.__make_sane_caps(name_parts[0]))
					])
					queries.append([
						"SELECT DISTINCT id_identity FROM names WHERE firstnames ~* '^%s' AND lastnames ~* '^%s'" % (name_parts[1], name_parts[0])
					])
					# name parts anywhere in name - third order query ...
					queries.append([
						"SELECT DISTINCT id_identity FROM names WHERE firstnames || lastnames ~* '%s' AND firstnames || lastnames ~* '%s'" % (name_parts[0], name_parts[1])
					])
					return queries
				# FIXME: either "name date" or "date date"
				_log.Log(gmLog.lErr, "don't know how to generate queries for [%s]" % a_search_term)
				return queries

			# exactly 3 words ?
			if len(sub_parts_list) == 3:
				# special case: 3 words, exactly 1 of them a date, no ",;"
				if date_count == 1:
					# assumption: first, last, dob - first order
					queries.append([
						"SELECT DISTINCT id_identity FROM names WHERE firstnames ~ '^%s' AND lastnames ~ '^%s' AND dob='%s'::timestamp" % (self.__make_sane_caps(name_parts[0]), self.__make_sane_caps(name_parts[1]), date_part)
					])
					queries.append([
						"SELECT DISTINCT id_identity FROM names WHERE firstnames ~* '^%s' AND lastnames ~* '^%s' AND dob='%s'::timestamp" % (name_parts[0], name_parts[1], date_part)
					])
					# assumption: last, first, dob - second order query
					queries.append([
						"SELECT DISTINCT id_identity FROM names WHERE firstnames ~ '^%s' AND lastnames ~ '^%s' AND dob='%s'::timestamp" % (self.__make_sane_caps(name_parts[1]), self.__make_sane_caps(name_parts[0]), date_part)
					])
					queries.append([
						"SELECT DISTINCT id_identity FROM names WHERE firstnames ~* '^%s' AND lastnames ~* '^%s' AND dob='%s'::timestamp" % (name_parts[1], name_parts[0], date_part)
					])
					# name parts anywhere in name - third order query ...
					queries.append([
						"SELECT DISTINCT id_identity FROM names WHERE firstnames || lastnames ~* '%s' AND firstnames || lastnames ~* '%s' AND dob='%s'::timestamp" % (name_parts[0], name_parts[1], date_part)
					])
					return queries
				# FIXME: "name name name" or "name date date"
				_log.Log(gmLog.lErr, "don't know how to generate queries for [%s]" % a_search_term)
				return queries

			# FIXME: no ',;' but neither "name name" nor "name name date"
			_log.Log(gmLog.lErr, "don't know how to generate queries for [%s]" % a_search_term)
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
					"firstnames ~ '^%s'" % self.__make_sane_caps(name_parts[0][0]),
					"lastnames ~ '^%s'"  % self.__make_sane_caps(name_parts[0][1])
				])
				wheres.append([
					"firstnames ~* '^%s'" % name_parts[0][0],
					"lastnames ~* '^%s'" % name_parts[0][1]
				])
				# but sometimes "last first""
				wheres.append([
					"firstnames ~ '^%s'" % self.__make_sane_caps(name_parts[0][1]),
					"lastnames ~ '^%s'"  % self.__make_sane_caps(name_parts[0][0])
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
					"firstnames ~ '^%s'" % string.join(map(self.__make_sane_caps, name_parts[1]), ' '),
					"lastnames ~ '^%s'"  % string.join(map(self.__make_sane_caps, name_parts[0]), ' ')
				])
				wheres.append([
					"firstnames ~* '^%s'" % string.join(name_parts[1], ' '),
					"lastnames ~* '^%s'" % string.join(name_parts[0], ' ')
				])
				# but sometimes "first, last"
				wheres.append([
					"firstnames ~ '^%s'" % string.join(map(self.__make_sane_caps, name_parts[0]), ' '),
					"lastnames ~ '^%s'"  % string.join(map(self.__make_sane_caps, name_parts[1]), ' ')
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
					wheres[0].append("dob='%s'::timestamp" % date_parts[0])
				else:
					wheres.append([
						"dob='%s'::timestamp" % date_parts[0]
					])
				if len(wheres) > 1:
					wheres[1].append("dob='%s'::timestamp" % date_parts[0])
				else:
					wheres.append([
						"dob='%s'::timestamp" % date_parts[0]
					])
			elif len(date_parts) > 1:
				if len(wheres) > 0:
					wheres[0].append("dob='%s'::timestamp" % date_parts[0])
					wheres[0].append("date_trunc('day', identity.deceased) LIKE (select timestamp '%s'" % date_parts[1])
				else:
					wheres.append([
						"dob='%s'::timestamp" % date_parts[0],
						"date_trunc('day', identity.deceased) LIKE (select timestamp '%s'" % date_parts[1]
					])
				if len(wheres) > 1:
					wheres[1].append("dob='%s'::timestamp" % date_parts[0])
					wheres[1].append("date_trunc('day', identity.deceased) LIKE (select timestamp '%s')" % date_parts[1])
				else:
					wheres.append([
						"dob='%s'::timestamp" % date_parts[0],
						"identity.deceased='%s'::timestamp" % date_parts[1]
					])

			# and finally generate the queries ...
			for where_clause in wheres:
				if len(where_clause) > 0:
					queries.append([
						"SELECT i_id FROM v_basic_person WHERE %s" % string.join(where_clause, ' AND ')
					])
				else:
					queries.append([])
			return queries

		return []
#============================================================
def create_dummy_identity():
	cmd1 = "insert into identity(gender, dob) values('?', CURRENT_TIMESTAMP)"
	cmd2 = "select currval('identity_id_seq')"

	data = gmPG.run_commit('personalia', [(cmd1, []), (cmd2, [])])
	if data is None:
		_log.Log(gmLog.lPanic, 'failed to create dummy identity')
		return None
	return data[0][0]
#============================================================
def set_active_patient(anID = None):
	tstart = time.time()
	# argument error
	if anID is None:
		return None
	pat = gmCurrentPatient()
	# None if not connected
	old_ID = pat.get_ID()
	# nothing to do
	if old_ID == anID:
		return 1
	# attempt to switch
	try:
		pat = gmCurrentPatient(anID)
	except:
		_log.LogException('error changing active patient', sys.exc_info())
		return None
	# who are we now ?
	new_ID = pat.get_ID()
	# nothing happened
	if new_ID == old_ID:
		_log.Log (gmLog.lErr, 'error changing active patient')
		return None
	duration = time.time() - tstart
	print "set_active_patient took %s seconds" % duration
	return 1
#============================================================
# main/testing
#============================================================
if __name__ == "__main__":
	_log.SetAllLogLevels(gmLog.lData)

	searcher = cPatientSearcher_SQL()
	p_data = None
	while 1:
		while 1:
			p_data = raw_input('patient data: ')
			if p_data == '-1':
				break
			p_ids = searcher.get_patient_ids(p_data)
			if p_ids is None:
				print "error searching matching patients"
			else:
				if len(p_ids) == 1:
					break
				if len(p_ids) > 1:
					print "more than one matching patient found:", p_ids
				else:
					print "no matching patient found"
		if p_data == '-1':
			break
		try:
			myPatient = gmCurrentPatient(p_ids[0])
		except:
			_log.LogException('Unable to set up patient with ID [%s]' % p_ids, sys.exc_info())
			print "patient", p_ids, "can not be set up"
			continue
		print "ID       ", myPatient['ID']
		demos = myPatient['demographic record']
		print "demogr.  ", demos
		print "name     ", demos.get_names(1)
		print "doc ids  ", myPatient['document id list']
		emr = myPatient.get_clinical_record()
		print "EMR      ", emr
		print "--------------------------------------"
	gmPG.ConnectionPool().StopListeners()
#============================================================
# $Log: gmPatient.py,v $
# Revision 1.48  2004-07-20 10:09:44  ncq
# - a bit of cleanup here and there
# - use Null design pattern instead of None when no real
#   patient connected to gmCurrentPatient Borg
#
#   this allows us to forego all the tests for None as
#   Null() reliably does nothing no matter what you try,
#   eventually, this will allow us to remove all the
#   is_patient_avail checks in the frontend,
#   it also acts sanely for code forgetting to check
#   for a connected patient
#
# Revision 1.47  2004/07/20 01:01:44  ihaywood
# changing a patients name works again.
# Name searching has been changed to query on names rather than v_basic_person.
# This is so the old (inactive) names are still visible to the search.
# This is so when Mary Smith gets married, we can still find her under Smith.
# [In Australia this odd tradition is still the norm, even female doctors
# have their medical registration documents updated]
#
# SOAPTextCtrl now has popups, but the cursor vanishes (?)
#
# Revision 1.46  2004/07/15 23:30:11  ncq
# - 'clinical_record' -> get_clinical_record()
#
# Revision 1.45  2004/07/05 22:26:24  ncq
# - do some timings to find patient change time sinks
#
# Revision 1.44  2004/06/15 19:14:30  ncq
# - add cleanup() to current patient calling gmPerson.cleanup()
#
# Revision 1.43  2004/06/01 23:58:01  ncq
# - debugged dob handling in _make_queries_generic
#
# Revision 1.42  2004/06/01 07:50:56  ncq
# - typo fix
#
# Revision 1.41  2004/05/18 22:38:19  ncq
# - __patient -> _patient
#
# Revision 1.40  2004/05/18 20:40:11  ncq
# - streamline __init__ significantly
# - check return status of get_clinical_record()
# - self.patient -> self.__patient
#
# Revision 1.39  2004/04/11 10:14:36  ncq
# - fix b0rked dob/dod handling in query generation
# - searching by dob should now work
#
# Revision 1.38  2004/03/25 11:14:48  ncq
# - fix get_document_folder()
#
# Revision 1.37  2004/03/25 11:03:23  ncq
# - getActiveName -> get_names
#
# Revision 1.36  2004/03/25 09:47:56  ncq
# - fix whitespace breakage
#
# Revision 1.35  2004/03/23 15:04:59  ncq
# - merge Carlos' constraints into get_text_dump
# - add gmPatient.export_data()
#
# Revision 1.34  2004/03/20 19:44:50  ncq
# - do import gmI18N
# - only fetch i_id in queries
# - revert to returning flat list of ids from get_patient_ids, must have been Syan fallout, I assume
#
# Revision 1.33  2004/03/20 13:31:18  ncq
# - PostgreSQL has date_trunc, not datetrunc
#
# Revision 1.32  2004/03/20 13:14:36  ncq
# - sync data dict and named substs in __generate_queries_generic
#
# Revision 1.31  2004/03/20 13:05:20  ncq
# - we of course need to return results from __generate_queries_generic
#
# Revision 1.30  2004/03/20 12:49:55  ncq
# - support gender, too, in search_dict in get_patient_ids
#
# Revision 1.29  2004/03/20 12:32:51  ncq
# - check for query_lists is None in get_pat_ids
#
# Revision 1.28  2004/03/20 11:45:41  ncq
# - don't pass search_dict[id] to get_patient_ids()
#
# Revision 1.27  2004/03/20 11:10:46  ncq
# - where_snippets needs to be []
#
# Revision 1.26  2004/03/20 10:48:31  ncq
# - if search_dict given we need to pass it to run_ro_query
#
# Revision 1.25  2004/03/19 11:46:24  ncq
# - add search_term to get_pat_ids()
#
# Revision 1.24  2004/03/10 13:44:33  ncq
# - shouldn't just import gmI18N, needs fix, I guess
#
# Revision 1.23  2004/03/10 12:56:01  ihaywood
# fixed sudden loss of main.shadow
# more work on referrals,
#
# Revision 1.22  2004/03/10 00:09:51  ncq
# - cleanup imports
#
# Revision 1.21  2004/03/09 07:34:51  ihaywood
# reactivating plugins
#
# Revision 1.20  2004/03/07 23:52:32  ncq
# - get_document_folder()
#
# Revision 1.19  2004/03/04 19:46:53  ncq
# - switch to package based import: from Gnumed.foo import bar
#
# Revision 1.18  2004/02/25 09:46:20  ncq
# - import from pycommon now, not python-common
#
# Revision 1.17  2004/02/18 06:36:04  ihaywood
# bugfixes
#
# Revision 1.16  2004/02/17 10:38:27  ncq
# - create_new_patient() -> xlnk_patient_in_clinical()
#
# Revision 1.15  2004/02/14 00:37:10  ihaywood
# Bugfixes
# 	- weeks = days / 7
# 	- create_new_patient to maintain xlnk_identity in historica
#
# Revision 1.14  2004/02/05 18:38:56  ncq
# - add .get_ID(), .is_locked()
# - set_active_patient() convenience function
#
# Revision 1.13  2004/02/04 00:57:24  ncq
# - added UI-independant patient search logic taken from gmPatientSelector
# - we can now have a console patient search field just as powerful as
#   the GUI version due to it running the same business logic code
# - also fixed _make_simple_query() results
#
# Revision 1.12  2004/01/18 21:43:00  ncq
# - speed up get_clinical_record()
#
# Revision 1.11  2004/01/12 16:21:03  ncq
# - _get_clini* -> get_clini*
#
# Revision 1.10  2003/11/20 01:17:14  ncq
# - consensus was that N/A is no good for identity.gender hence
#   don't use it in create_dummy_identity anymore
#
# Revision 1.9  2003/11/18 16:35:17  ncq
# - correct create_dummy_identity()
# - move create_dummy_relative to gmDemographicRecord and rename it to link_new_relative
# - remove reload keyword from gmCurrentPatient.__init__() - if you need it your logic
#   is screwed
#
# Revision 1.8  2003/11/17 10:56:34  sjtan
#
# synced and commiting.
#
# Revision 1.7  2003/11/16 10:58:36  shilbert
# - corrected typo
#
# Revision 1.6  2003/11/09 16:39:34  ncq
# - get handler now 'demographic record', not 'demographics'
#
# Revision 1.5  2003/11/04 00:07:40  ncq
# - renamed gmDemographics
#
# Revision 1.4  2003/10/26 17:35:04  ncq
# - conceptual cleanup
# - IMHO, patient searching and database stub creation is OUTSIDE
#   THE SCOPE OF gmPerson and gmDemographicRecord
#
# Revision 1.3  2003/10/26 11:27:10  ihaywood
# gmPatient is now the "patient stub", all demographics stuff in gmDemographics.
#
# Ergregious breakages are fixed, but needs more work
#
# Revision 1.2  2003/10/26 01:38:06  ncq
# - gmTmpPatient -> gmPatient, cleanup
#
# Revision 1.1  2003/10/26 01:26:45  ncq
# - now go live, this is for real
#
# Revision 1.41  2003/10/19 10:42:57  ihaywood
# extra functions
#
# Revision 1.40  2003/09/24 08:45:40  ihaywood
# NewAddress now functional
#
# Revision 1.39  2003/09/23 19:38:03  ncq
# - cleanup
# - moved GetAddressesType out of patient class - it's a generic function
#
# Revision 1.38  2003/09/23 12:49:56  ncq
# - reformat, %d -> %s
#
# Revision 1.37  2003/09/23 12:09:26  ihaywood
# Karsten, we've been tripping over each other again
#
# Revision 1.36  2003/09/23 11:31:12  ncq
# - properly use ro_run_query()s returns
#
# Revision 1.35  2003/09/22 23:29:30  ncq
# - new style run_ro_query()
#
# Revision 1.34  2003/09/21 12:46:30  ncq
# - switched most ro queries to run_ro_query()
#
# Revision 1.33  2003/09/21 10:37:20  ncq
# - bugfix, cleanup
#
# Revision 1.32  2003/09/21 06:53:40  ihaywood
# bugfixes
#
# Revision 1.31  2003/09/17 11:08:30  ncq
# - cleanup, fix type "personaliaa"
#
# Revision 1.30  2003/09/17 03:00:59  ihaywood
# support for local inet connections
#
# Revision 1.29  2003/07/19 20:18:28  ncq
# - code cleanup
# - explicitely cleanup EMR when cleaning up patient
#
# Revision 1.28  2003/07/09 16:21:22  ncq
# - better comments
#
# Revision 1.27  2003/06/27 16:04:40  ncq
# - no ; in DB-API
#
# Revision 1.26  2003/06/26 21:28:02  ncq
# - fatal->verbose, %s; quoting bug
#
# Revision 1.25  2003/06/22 16:18:34  ncq
# - cleanup, send signal prior to changing the active patient, too
#
# Revision 1.24  2003/06/19 15:24:23  ncq
# - add is_connected check to gmCurrentPatient to find
#   out whether there's a live patient record attached
# - typo fix
#
# Revision 1.23  2003/06/01 14:34:47  sjtan
#
# hopefully complies with temporary model; not using setData now ( but that did work).
# Please leave a working and tested substitute (i.e. select a patient , allergy list
# will change; check allergy panel allows update of allergy list), if still
# not satisfied. I need a working model-view connection ; trying to get at least
# a basically database updating version going .
#
# Revision 1.22  2003/06/01 13:34:38  ncq
# - reinstate remote app locking
# - comment out thread lock for now but keep code
# - setting gmCurrentPatient is not how it is supposed to work (I think)
#
# Revision 1.21  2003/06/01 13:20:32  sjtan
#
# logging to data stream for debugging. Adding DEBUG tags when work out how to use vi
# with regular expression groups (maybe never).
#
# Revision 1.20  2003/06/01 01:47:32  sjtan
#
# starting allergy connections.
#
# Revision 1.19  2003/04/29 15:24:05  ncq
# - add _get_clinical_record handler
# - add _get_API API discovery handler
#
# Revision 1.18  2003/04/28 21:36:33  ncq
# - compactify medical age
#
# Revision 1.17  2003/04/25 12:58:58  ncq
# - dynamically handle supplied data in create_patient but added some sanity checks
#
# Revision 1.16  2003/04/19 22:54:46  ncq
# - cleanup
#
# Revision 1.15  2003/04/19 14:59:04  ncq
# - attribute handler for "medical age"
#
# Revision 1.14  2003/04/09 16:15:44  ncq
# - get handler for age
#
# Revision 1.13  2003/04/04 20:40:51  ncq
# - handle connection errors gracefully
# - let gmCurrentPatient be a borg but let the person object be an attribute thereof
#   instead of an ancestor, this way we can safely do __init__(aPKey) where aPKey may or
#   may not be None
#
# Revision 1.12  2003/03/31 23:36:51  ncq
# - adapt to changed view v_basic_person
#
# Revision 1.11  2003/03/27 21:08:25  ncq
# - catch connection errors
# - create_patient rewritten
# - cleanup on __del__
#
# Revision 1.10  2003/03/25 12:32:31  ncq
# - create_patient helper
# - __getTitle
#
# Revision 1.9  2003/02/21 16:42:02  ncq
# - better error handling on query generation
#
# Revision 1.8  2003/02/18 02:41:54  ncq
# - helper function get_patient_ids, only structured search term search implemented so far
#
# Revision 1.7  2003/02/17 16:16:13  ncq
# - document list -> document id list
#
# Revision 1.6  2003/02/11 18:21:36  ncq
# - move over to __getitem__ invoking handlers
# - self.format to be used as an arbitrary format string
#
# Revision 1.5  2003/02/11 13:03:44  ncq
# - don't change patient on patient not found ...
#
# Revision 1.4  2003/02/09 23:38:21  ncq
# - now actually listens patient selectors, commits old patient and
#   inits the new one if possible
#
# Revision 1.3  2003/02/08 00:09:46  ncq
# - finally starts being useful
#
# Revision 1.2  2003/02/06 15:40:58  ncq
# - hit hard the merge wall
#
# Revision 1.1  2003/02/01 17:53:12  ncq
# - doesn't do anything, just to show people where I am going
#
