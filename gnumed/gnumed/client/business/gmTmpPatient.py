"""GnuMed temporary patient object.

This is a patient object intended to let a useful client-side
API crystallize from actual use in true XP fashion.

license: GPL
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/business/Attic/gmTmpPatient.py,v $
# $Id: gmTmpPatient.py,v 1.29 2003-07-19 20:18:28 ncq Exp $
__version__ = "$Revision: 1.29 $"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"

# access our modules
import sys, os.path, time

if __name__ == "__main__":
	sys.path.append(os.path.join('..', 'python-common'))

# start logging
import gmLog
_log = gmLog.gmDefLog
if __name__ == "__main__":
	_log.SetAllLogLevels(gmLog.lData)
_log.Log(gmLog.lData, __version__)

import gmExceptions, gmPG, gmSignals, gmDispatcher, gmClinicalRecord

# 3rd party
import mx.DateTime

#============================================================
gm2long_gender_map = {
	'm': _('male'),
	'f': _('female')
}
#============================================================
# utility function separate from db access logic
def get_medical_age(dob):
	"""format patient age in a hopefully meaningful way"""

	age = mx.DateTime.Age(mx.DateTime.now(), dob)

	if age.years > 0:
		return "%sy%sm" % (age.years, age.months)
	if age.weeks > 4:
		return "%sm%sw" % (age.months, age.weeks)
	if age.weeks > 1:
		return "%sd" % age.days
	if age.days > 1:
		return "%sd (%sh)" % (age.days, age.hours)
	if age.hours > 3:
		return "%sh" % age.hours
	if age.hours > 0:
		return "%sh%sm" % (age.hours, age.minutes)
	if age.minutes > 5:
		return "%sm" % (age.minutes)
	return "%sm%ss" % (age.minutes, age.seconds)

#============================================================
# may get preloaded by the waiting list
class gmPerson:
	"""Represents a patient that DOES EXIST in the database.

	- searching and creation is done OUTSIDE this object
	"""

	# handlers for __getitem__()
	_get_handler = {}

	def __init__(self, aPKey = None):
		"""Fails if

		- no connection to database possible
		- patient referenced by aPKey does not exist.
		"""
		self._backend = gmPG.ConnectionPool()
		self._defconn_ro = self._backend.GetConnection('personalia')
		if self._defconn_ro is None:
			raise gmExceptions.ConstructorError, "Cannot connect to database." % aPKey

		self.ID = aPKey			# == identity.id == primary key
		if not self._pkey_exists():
			raise gmExceptions.ConstructorError, "No patient with ID [%s] in database." % aPKey

		self.PUPIC = ""
		self.__db_cache = {}

		# register backend notification interests ...
		#if not self._register_interests():
			#raise gmExceptions.ConstructorError, "Cannot register patient modification interests."

		_log.Log(gmLog.lData, 'Instantiated patient [%s].' % self.ID)
	#--------------------------------------------------------
	def cleanup(self):
		"""Do cleanups before dying.

		- note that this may be called in a thread
		"""
		_log.Log(gmLog.lData, 'cleaning up after patient [%s]' % self.ID)
		if self.__db_cache.has_key('clinical record'):
			emr = self.__db_cache['clinical record']
			emr.cleanup()
		self._backend.ReleaseConnection('personalia')
	#--------------------------------------------------------
	# internal helper
	#--------------------------------------------------------
	def _pkey_exists(self):
		"""Does this primary key exist ?

		- true/false/None
		"""
		curs = self._defconn_ro.cursor()
		cmd = "select exists(select id from identity where id = %s)"
		try:
			curs.execute(cmd, self.ID)
		except:
			curs.close()
			_log.LogException('>>>%s<<< failed' % (cmd % self.ID), sys.exc_info(), verbose=0)
			return None
		res = curs.fetchone()[0]
		curs.close()
		return res
	#--------------------------------------------------------
	# messaging
	#--------------------------------------------------------
	def _register_interests(self):
		# backend
		self._backend.Listen(
			service = 'personalia',
			signal = '"%s.%s"' % (gmSignals.patient_modified(), self.ID),
			callback = self._patient_modified
		)
	#--------------------------------------------------------
	def _patient_modified(self):
		# <DEBUG>
		_log.Log(gmLog.lData, "patient_modified signal received from backend")
		# </DEBUG>
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
	def _getMedDocsList(self):
		"""Build a complete list of metadata for all documents of our patient.

		"""
		blobs_conn = self._backend.GetConnection('blobs')
		if blobs_conn is None:
			_log.Log(gmLog.lPanic, "Cannot connect to database.")
			return None

		curs = blobs_conn.cursor()
		cmd = "SELECT id from doc_med WHERE patient_id=%s"
		try:
			curs.execute(cmd, self.ID)
		except:
			curs.close()
			_log.LogException('>>>%s<<< failed' % (cmd % self.ID), sys.exc_info())
			return None

		tmp = curs.fetchall()
		docs = []
		for doc_id in tmp:
			docs.extend(doc_id)
		_log.Log(gmLog.lData, "document IDs: %s" % docs)

		if curs.rowcount == 0:
			curs.close()
			_log.Log(gmLog.lInfo, "No documents found for patient (ID [%s])." % self.ID)
			return None

		curs.close()
		self._backend.ReleaseConnection('blobs')

		return docs
	#--------------------------------------------------------
	def _getActiveName(self):
		curs = self._defconn_ro.cursor()
		cmd = "select firstnames, lastnames from v_basic_person where i_id = %s"
		try:
			curs.execute(cmd, self.ID)
		except:
			curs.close()
			_log.LogException('>>>%s<<< failed' % (cmd % self.ID), sys.exc_info())
			return None
		data = curs.fetchone()
		curs.close()
		if data is None:
			return None
		else:
			result = {
				'first': data[0],
				'last': data[1]
			}
			return result
	#--------------------------------------------------------
	def _getTitle(self):
		curs = self._defconn_ro.cursor()
		cmd = "select title from v_basic_person where i_id = %s"
		try:
			curs.execute(cmd, self.ID)
		except:
			curs.close()
			_log.LogException('>>>%s<<< failed' % (cmd % self.ID), sys.exc_info())
			return ''
		data = curs.fetchone()
		curs.close()
		if data is None:
			return ''
		else:
			if data[0] is None:
				return ''
			else:
				return data[0]
	#--------------------------------------------------------
	def _getID(self):
		return self.ID
	#--------------------------------------------------------
	def _getDOB(self):
		curs = self._defconn_ro.cursor()
		# FIXME: invent a mechanism to set the desired format
		cmd = "select to_char(dob, 'DD.MM.YYYY') from v_basic_person where i_id = %s"
		try:
			curs.execute(cmd, self.ID)
		except:
			curs.close()
			_log.LogException('>>>%s<<< failed' % (cmd % self.ID), sys.exc_info())
			return None
		data = curs.fetchone()
		curs.close()
		if data is None:
			return ''
		else:
			return data[0]
	#--------------------------------------------------------
	def _get_medical_age(self):
		curs = self._defconn_ro.cursor()
		cmd = "select dob from identity where id = %s"
		try:
			curs.execute(cmd, self.ID)
		except:
			curs.close()
			_log.LogException('>>>%s<<< failed' % (cmd % self.ID), sys.exc_info())
			return None
		data = curs.fetchone()
		curs.close()

		if data is None:
			return '??'
		return get_medical_age(data[0])
	#--------------------------------------------------------
	def _get_clinical_record(self):
		if self.__db_cache.has_key('clinical record'):
			return self.__db_cache['clinical record']
		try:
			self.__db_cache['clinical record'] = gmClinicalRecord.gmClinicalRecord(aPKey = self.ID)
		except StandardError:
			_log.LogException('cannot instantiate clinical record for patient [%s]', sys.exc_info())
			return None
		return self.__db_cache['clinical record']
	#--------------------------------------------------------
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
	_get_handler['document id list'] = _getMedDocsList
	_get_handler['active name'] = _getActiveName
	#_get_handler['all names'] = _getNamesList
	_get_handler['title'] = _getTitle
	_get_handler['ID'] = _getID
	_get_handler['dob'] = _getDOB
	_get_handler['medical age'] = _get_medical_age
	_get_handler['clinical record'] = _get_clinical_record
	_get_handler['API'] = _get_API
#============================================================
from gmBorg import cBorg

class gmCurrentPatient(cBorg):
	"""Patient Borg to hold currently active patient.

	There may be many instances of this but they all share state.
	"""
	def __init__(self, aPKey = None):
		_log.Log(gmLog.lData, 'selection of patient [%s] requested' % aPKey)
		# share state among all instances ...
		cBorg.__init__(self)

		# make sure we do have a patient pointer even if it is None
		if not self.__dict__.has_key('patient'):
			self.patient = None

		# set initial lock state,
		# this lock protects against activating another patient
		# when we are controlled from a remote application
		if not self.__dict__.has_key('locked'):
			self.unlock()

		# user wants to init or change us
		# possibly change us, depending on PKey
		if aPKey is not None:
			_log.Log(gmLog.lData, 'patient ID explicitely specified, trying to connect')
			# init, no previous PKEY
			if self.patient is None:
				_log.Log(gmLog.lData, 'no previous patient')
				try:
					self.patient = gmPerson(aPKey)
					# remote app must lock explicitly
					self.unlock()
					self.__send_selection_notification()
				except:
					_log.LogException('cannot connect with patient [%s]' % aPKey, sys.exc_info())
			# change to another PKEY
			else:
				_log.Log(gmLog.lData, 'patient change: [%s] -> [%s]' % (self.patient.ID, aPKey))
				# are we really supposed to become someone else ?
				if self.patient['ID'] != aPKey:
					# yes, but CAN we ?
					if self.locked is None:
						try:
							tmp = gmPerson(aPKey)
							# clean up after ourselves
							self.__send_pre_selection_notification()
							self.patient.cleanup()
							# and change to new patient
							self.patient = tmp
							self.unlock()
							self.__send_selection_notification()
						except:
							_log.LogException('cannot connect with patient [%s]' % aPKey, sys.exc_info())
							# FIXME: maybe raise exception here ?
					else:
						_log.Log(gmLog.lErr, 'patient [%s] is locked, cannot change to [%s]' % (self.patient['ID'], aPKey))
				# no, same patient, so do nothing
				else:
					_log.Log(gmLog.lData, 'same ID, no change needed')
		# else do nothing which will return ourselves
		else:
			_log.Log(gmLog.lData, 'no patient ID specified, returning current patient')

		return None
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
	def __send_selection_notification(self):
		"""Sends signal when another patient has actually been made active."""
		kwargs = {
			'ID': self.patient['ID'],
			'signal': gmSignals.patient_selected(),
			'sender': id(self.__class__)
		}
		gmDispatcher.send(gmSignals.patient_selected(), kwds=kwargs)
	#--------------------------------------------------------
	def __send_pre_selection_notification(self):
		"""Sends signal when another patient is about to become active."""
		kwargs = {
			'ID': self.patient['ID'],
			'signal': gmSignals.activating_patient(),
			'sender': id(self.__class__)
		}
		gmDispatcher.send(gmSignals.activating_patient(), kwds=kwargs)
	#--------------------------------------------------------
	def is_connected(self):
		if self.patient is None:
			return None
		else:
			return 1
	#--------------------------------------------------------
	# __getitem__ handling
	#--------------------------------------------------------
	def __getitem__(self, aVar = None):
		"""Return any attribute if known how to retrieve it by proxy.
		"""
		if self.patient is not None:
			return self.patient[aVar]
		else:
			return None
#============================================================


#------------------------------------------------------------
def get_patient_ids(cooked_search_terms = None, raw_search_terms = None):
	"""Get a list of matching patient IDs.

	None		- no match
	not None	- list of IDs
	exception	- failure
	"""
	if cooked_search_terms is not None:
		where_clause = _make_where_from_cooked(cooked_search_terms)

		if where_clause is None:
			raise ValueError, "Cannot make WHERE clause."

		# get connection
		backend = gmPG.ConnectionPool()
		conn = backend.GetConnection('personalia')
		if conn is None:
			raise ValueError, "Cannot connect to database."

		# start our transaction (done implicitely by defining a cursor)
		cursor = conn.cursor()
		cmd = "SELECT i_id FROM v_basic_person WHERE %s" % where_clause
		if not gmPG.run_query(cursor, cmd):
			cursor.close()
			backend.ReleaseConnection('personalia')
			raise

		tmp = cursor.fetchall()
		cursor.close()
		backend.ReleaseConnection('personalia')

		if tmp is None or len(tmp) == 0:
			_log.Log(gmLog.lInfo, "No matching patients.")
			return None
		pat_ids = []
		for pat_id in tmp:
			pat_ids.extend(pat_id)

		return pat_ids

	if raw_search_terms is not None:
		_log.Log(gmLog.lErr, 'getting patient IDs by raw search terms not implemented yet')
		raise ValueError, "Making WHERE clause from raw input not implemented."

	_log.Log(gmLog.lErr, 'Cannot get patient IDs with neither raw nor cooked search terms !')
	return None
#------------------------------------------------------------
def _make_where_from_cooked(cooked_search_terms = None):
	data = cooked_search_terms
	try:
		if data['case sensitive'] is None:
			like = 'ilike'
		else:
			like = 'like'

		if data['globbing'] is None:
			wildcard = ''
		else:
			wildcard = '%s'

		# set up query
		if data['first name'] is None:
			where_fname = ''
		else:
			where_fname = "firstnames %s '%s%s%s'" % (like, wildcard, data['first name'], wildcard)

		if data['last name'] is None:
			where_lname = ''
		else:
			where_lname = "lastnames %s '%s%s%s'" % (like, wildcard, data['last name'], wildcard)

		if data['dob'] is None:
			where_dob = ''
		else:
			#where_dob = "dob = (select to_timestamp('%s', 'YYYYMMDD'))" % data['dob']
			where_dob = "dob = '%s'" % data['dob']

		if data['gender'] is None:
			where_gender = ''
		else:
			where_gender = "gender = '%s'" % data['gender']
	except KeyError:
		_log.Log(gmLog.lErr, data)
		_log.LogException('invalid argument data structure')
		return None

	return ' AND '.join((where_fname, where_lname, where_dob, where_gender))
#------------------------------------------------------------
def create_patient(data):
	"""Create or load and return gmTmpPatient object.

	- not None: either newly created patient or existing patient
	- None: failure
	"""
	# sanity checks
	try:
		if not data.has_key('lastnames'):
			_log.Log(gmLog.lErr, "need last name")
			return None
	except:
		_log.LogException('wrong data structure: %s' % data, sys.exc_info())
		return None
	if not data.has_key('firstnames'):
		_log.Log(gmLog.lErr, "need first name")
		return None

	backend = gmPG.ConnectionPool()
	roconn = backend.GetConnection('personalia')
	if roconn is None:
		_log.Log(gmLog.lPanic, "Cannot connect to database.")
		return None

	possible_where_fields = (
		'title',
		'firstnames',
		'lastnames',
		'dob',
		'cob',
		'gender'
	)

	rocurs = roconn.cursor()

	# create where clause
	where_fragments = []
	for key in data.keys():
		if key in possible_where_fields:
			where_fragments.append("%s='%s'" % (key, data[key]))
	where_clause = string.join(where_fragments, ' AND ')

	# check for patient
	cmd = "SELECT exists(SELECT i_id FROM v_basic_person WHERE %s)" % where_clause
	if not gmPG.run_query(rocurs, cmd):
		_log.Log(gmLog.lErr, 'Cannot check for patient existence.')
		rocurs.close()
		backend.ReleaseConnection('personalia')
		return None
	pat_exists = rocurs.fetchone()[0]

	# insert new patient
	if not pat_exists:
		rwconn = backend.GetConnection('personalia', readonly = 0)
		if rwconn is None:
			_log.Log(gmLog.lPanic, "Cannot connect to database.")
			rocurs.close()
			backend.ReleaseConnection('personalia')
			return None
		rwcurs = rwconn.cursor()

		field_fragments = []
		value_fragments = []
		for key in data.keys():
			if key in possible_where_fields:
				field_fragments.append("%s" % key)
				value_fragments.append("'%s'" % data[key])
		field_clause = string.join(field_fragments, ',')
		value_clause = string.join(value_fragments, ',')

		cmd =  "INSERT INTO v_basic_person (%s) VALUES (%s)" % (field_clause, value_clause)
		if not gmPG.run_query(rwcurs, cmd):
			_log.Log(gmLog.lErr, 'Cannot insert patient.')
			_log.Log(gmLog.lErr, data)
			rwcurs.close()
			rwconn.close()
			rocurs.close()
			backend.ReleaseConnection('personalia')
			return None

		rwconn.commit()
		rwcurs.close()
		rwconn.close()

		_log.Log(gmLog.lData, 'patient successfully inserted')
	else:
		_log.Log(gmLog.lData, 'patient already in database')

	# get patient ID
	cmd = "SELECT i_id FROM v_basic_person WHERE %s LIMIT 2" % where_clause
	if not gmPG.run_query(rocurs, cmd):
		rocurs.close()
		backend.ReleaseConnection('personalia')
		return None
	result = rocurs.fetchall()
	if len(result) > 1:
		_log.Log(gmLog.lErr, "data matches more than one patient, aborting")
		_log.Log(gmLog.lData, data)
		return None
	pat_id = result[0][0]

	rocurs.close()
	backend.ReleaseConnection('personalia')

	_log.Log(gmLog.lData, 'patient ID [%s]' % pat_id)

	# and init new patient object
	try:
		pat = gmPerson(aPKey = pat_id)
	except:
		_log.LogException('cannot init patient with ID [%s]' % pat_id, sys.exc_info(), verbose=1)
		return None

	return pat
#============================================================
# callbacks
#------------------------------------------------------------
def _patient_selected(**kwargs):
	print "received patient_selected notification"
	print kwargs['kwds']

#============================================================
if __name__ == "__main__":
	gmDispatcher.connect(_patient_selected, gmSignals.patient_selected())
	while 1:
		pID = raw_input('a patient ID: ')
		if pID == '-1':
			break
		try:
			myPatient = gmCurrentPatient(aPKey = pID)
		except:
			_log.LogException('Unable to set up patient with ID [%s]' % pID, sys.exc_info())
			print "patient", pID, "can not be set up"
			continue
		print "ID     ", myPatient['ID']
		print "name   ", myPatient['active name']
		print "doc ids", myPatient['document id list']
		print "title  ", myPatient['title']
		print "dob    ", myPatient['dob']
		print "med age", myPatient['medical age']
		record = myPatient['clinical record']
		print "EPR    ", record
#		print "allergy IDs", record['allergy IDs']
#		print "fails  ", myPatient['missing handler']
		print "--------------------------------------"
#		api = myPatient['API']
#		for call in api:
#			print "API call: %s (internally %s)" % (call['API call name'], call['internal name'])
#			print call['description']
#============================================================
# $Log: gmTmpPatient.py,v $
# Revision 1.29  2003-07-19 20:18:28  ncq
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
