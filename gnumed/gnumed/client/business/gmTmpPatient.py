"""GnuMed temporary patient object.

This is a patient object intended to let a useful client-side
API crystallize from actual use in true XP fashion.

license: GPL
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/business/Attic/gmTmpPatient.py,v $
# $Id: gmTmpPatient.py,v 1.13 2003-04-04 20:40:51 ncq Exp $
__version__ = "$Revision: 1.13 $"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"

# access our modules
import sys, os.path
if __name__ == "__main__":
	sys.path.append(os.path.join('..', 'python-common'))

# start logging
import gmLog
_log = gmLog.gmDefLog
if __name__ == "__main__":
	_log.SetAllLogLevels(gmLog.lData)
_log.Log(gmLog.lData, __version__)

import gmExceptions, gmPG, gmSignals, gmDispatcher

#============================================================
gm2long_gender_map = {
	'm': _('male'),
	'f': _('female')
}
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

		# register backend notification interests ...
		#if not self._register_interests():
			#raise gmExceptions.ConstructorError, "Cannot register patient modification interests."

		_log.Log(gmLog.lData, 'Instantiated patient [%s].' % self.ID)
	#--------------------------------------------------------
	def __del__(self):
		if self.__dict__.has_key('_backend'):
			self._backend.ReleaseConnection('personalia')
	#--------------------------------------------------------
	# cache handling
	#--------------------------------------------------------
	def commit(self):
		"""Do cleanups before dying.

		- note that this may be called in a thread
		"""
		# unlisten to signals
		print "unimplemented: committing patient data"
	#--------------------------------------------------------
	def invalidate_cache(self):
		"""Called when the cache turns cold.

		"""
		print "unimplemented: invalidating patient data cache"
	#--------------------------------------------------------
	#--------------------------------------------------------
	def setQueryTree(self, aCol, aQueryTree = None):
		if aQueryTree is None:
			return None
		self._query_trees[aCol] = aQueryTree
	#--------------------------------------------------------
	# internal helper
	#--------------------------------------------------------
	def _pkey_exists(self):
		"""Does this primary key exist ?

		- true/false/None
		"""
		curs = self._defconn_ro.cursor()
		cmd = "select exists(select id from identity where id = %s);"
		try:
			curs.execute(cmd, self.ID)
		except:
			curs.close()
			_log.LogException('>>>%s<<< failed' % (cmd % self.ID), sys.exc_info(), fatal=0)
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
		# uh, oh, cache may have been modified ...
		# <DEBUG>
		_log.Log(gmLog.lData, "patient_modified signal received from backend")
		# </DEBUG>
		# this is fraught with problems:
		# can we safely just throw away the cache ?
		# we may have new data in there ...
		self.invalidate_cache()
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
		cmd = "SELECT id from doc_med WHERE patient_id=%s;"
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
		cmd = "select firstnames, lastnames from v_basic_person where i_id = %s;"
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
		cmd = "select title from v_basic_person where i_id = %s;"
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
		cmd = "select to_char(dob, 'DD.MM.YYYY') from v_basic_person where i_id = %s;"
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
	# set up handler map
	_get_handler['document id list'] = _getMedDocsList
	_get_handler['active name'] = _getActiveName
	#_get_handler['all names'] = _getNamesList
	_get_handler['title'] = _getTitle
	_get_handler['ID'] = _getID
	_get_handler['dob'] = _getDOB
#============================================================
from gmBorg import cBorg

class gmCurrentPatient(cBorg):
	"""Patient Borg to hold currently active patient.

	There may be many instances of this but they all share state.
	"""
	def __init__(self, aPKey = None):
		# share state among all instances ...
		cBorg.__init__(self)

		# make sure we do have a patient pointer even if it is None
		if not self.__dict__.has_key('patient'):
			self.patient = None

		# set initial lock state
		if not self.__dict__.has_key('locked'):
			self.unlock()

		# set up default data
		if not self.__dict__.has_key('default_data'):
			self.default_data = {}

		# user wants to init or change us
		if aPKey is not None:
			# init
			if self.patient is None:
				try:
					self.patient = gmPerson(aPKey)
					self.unlock()
					self.__send_selection_notification()
				except:
					_log.LogException('cannot connect with patient [%s]' % aPKey, sys.exc_info())
			# change
			else:
				# are we really to become someone else ?
				if self.patient['ID'] != aPKey:
					# yes, but CAN we ?
					if self.locked is None:
						try:
							tmp = gmPerson(aPKey)
							# clean up after ourselves
							self.patient.commit()
							# FIXME: is this needed ?
							del self.patient
							self.patient = tmp
							self.unlock()
							self.__send_selection_notification()
						except:
							_log.LogException('cannot connect with patient [%s]' % aPKey, sys.exc_info())
							# FIXME: maybe raise exception here ?
					else:
						_log.Log(gmLog.lErr, 'patient [%s] is locked, cannot change to [%s]' % (self.patient['ID'], aPKey))

		return None
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
	# __getitem__ handling
	#--------------------------------------------------------
	def __getitem__(self, aVar = None):
		"""Return any attribute if known how to retrieve it by proxy.
		"""
		if self.patient is not None:
			return self.patient[aVar]
		else:
			return None
#			try:
#				return self.default_data[aVar]
#			except KeyError:
#				return None
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
		cmd = "SELECT i_id FROM v_basic_person WHERE %s;" % where_clause
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
	backend = gmPG.ConnectionPool()
	roconn = backend.GetConnection('personalia')
	if roconn is None:
		_log.Log(gmLog.lPanic, "Cannot connect to database.")
		return None

	# patient already in database ?
	try:
		cmd = "SELECT exists(SELECT i_id FROM v_basic_person WHERE firstnames='%s' AND lastnames='%s' AND date_trunc('day', dob)='%s');" % (data['first name'], data['last name'], data['dob'])
	except KeyError:
		_log.LogException('argument structure wrong: %s' % data, sys.exc_info())
		return None

	rocurs = roconn.cursor()

	if not gmPG.run_query(rocurs, cmd):
		_log.Log(gmLog.lErr, 'Cannot check for patient existence.')
		rocurs.close()
		backend.ReleaseConnection('personalia')
		return None
	pat_exists = rocurs.fetchone()[0]

	# insert new patient
	if not pat_exists:
		cmd =  "INSERT INTO v_basic_person (firstnames, lastnames, dob) \
				VALUES ('%s', '%s', '%s');" % (
					data['first name'],
					data['last name'],
					data['dob']
				)
		rwconn = backend.GetConnection('personalia', readonly = 0)
		if rwconn is None:
			_log.Log(gmLog.lPanic, "Cannot connect to database.")
			rocurs.close()
			backend.ReleaseConnection('personalia')
			return None
		rwcurs = rwconn.cursor()

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
	cmd = "SELECT i_id FROM v_basic_person WHERE firstnames='%s' AND lastnames='%s' AND date_trunc('day', dob)='%s';" % (data['first name'], data['last name'], data['dob'])
	if not gmPG.run_query(rocurs, cmd):
		rocurs.close()
		backend.ReleaseConnection('personalia')
		return None
	pat_id = rocurs.fetchone()[0]

	rocurs.close()
	backend.ReleaseConnection('personalia')

	_log.Log(gmLog.lData, 'patient ID: %s' % pat_id)

	# and init new patient object
	try:
		pat = gmPerson(aPKey = pat_id)
	except:
		_log.LogException('cannot init patient with ID [%s]' % pat_id, sys.exc_info(), fatal=1)
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
		print "fails  ", myPatient['missing handler']
#============================================================
# $Log: gmTmpPatient.py,v $
# Revision 1.13  2003-04-04 20:40:51  ncq
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
