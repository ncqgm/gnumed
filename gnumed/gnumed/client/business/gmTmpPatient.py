"""GnuMed temporary patient object.

This a patient object intended to let a useful client-side
API crystallize from actual use in true XP fashion.

license: GPL
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/business/Attic/gmTmpPatient.py,v $
# $Id: gmTmpPatient.py,v 1.9 2003-02-21 16:42:02 ncq Exp $
__version__ = "$Revision: 1.9 $"
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

gmDefPatient = None
#============================================================
gm2long_gender_map = {
	'm': _('male'),
	'f': _('female')
}

# may get preloaded by the waiting list
class gmPatient:
	"""Represents a patient that DOES EXIST in the database.

	- searching and creation is done OUTSIDE this object
	"""

	# handlers for __getitem__()
	__get_handler = {}

	def __init__(self, aPKey = None):
		"""Fails if

		- no connection to database possible
		- patient referenced by aPKey does not exist.
		"""
		self.__backend = gmPG.ConnectionPool()
		self.__defconn = self.__backend.GetConnection('personalia')

		self.ID = aPKey			# == identity.id == primary key
		if not self.__pkey_exists():
			raise gmExceptions.ConstructorError, "No patient with ID [%s] in database." % aPKey

		self.PUPIC = ""
		self.OID = None
		# if true the managed patient can't be changed, this
		# is useful if some other software called us with a
		# specific patient pre-selected
		self.locked = (1==0)

		# to be used whenever a format string is needed since
		# we cannot pass parameters to __getitem__()
		self.format = None

		# register backend notification interests ...
		#if not self.__register_interests():
			#raise gmExceptions.ConstructorError, "Cannot register patient modification interests."

#		self.__cache = {}
#		self.__query_trees = {}

		_log.Log(gmLog.lData, 'Instantiated patient [%s].' % self.ID)
	#--------------------------------------------------------
	def commit(self):
		"""Do cleanups before dying.

		- note that this may be called in a thread
		"""
		# unlisten to signals
		print "unimplemented: committing patient data"
	#--------------------------------------------------------
	def setQueryTree(self, aCol, aQueryTree = None):
		if aQueryTree is None:
			return None
		self.__query_trees[aCol] = aQueryTree
	#--------------------------------------------------------
	# internal helper
	#--------------------------------------------------------
	def __pkey_exists(self):
		"""Does this primary key exist ?

		- true/false/None
		"""
		curs = self.__defconn.cursor()
		cmd = "select exists(select id from identity where id = %s);"
		try:
			curs.execute(cmd, self.ID)
		except:
			curs.close
			_log.LogException('>>>%s<<< failed' % (cmd % self.ID), sys.exc_info(), fatal=0)
			return None
		res = curs.fetchone()[0]
		curs.close()
		return res
	#--------------------------------------------------------
	# messaging
	#--------------------------------------------------------
	def __register_interests(self):
		# backend
		self.__backend.Listen(
			service = 'personalia',
			signal = '"%s.%s"' % (gmSignals.patient_modified(), self.ID),
			callback = self.__patient_modified
		)
	#--------------------------------------------------------
	def __patient_modified(self):
		# uh, oh, cache may have been modified ...
		# <DEBUG>
		_log.Log(gmLog.lData, "patient_modified signal received from backend")
		# </DEBUG>
	#--------------------------------------------------------
	# object behaviour
	#--------------------------------------------------------
	def __getitem__(self, aVar = None):
		"""Return any attribute if known how to retrieve it.

		Either the built in mapper knows how to access the data in the database
		or you must have provided queries. The mapper, of course, caches how to
		access data in the database.

		The values themselves are cached, too, until a backend notification is received
		for this patient.

		We may hand off regetting data after a change notification to a thread.
		"""
		try:
			return gmPatient.__get_handler[aVar](self)
		except:
			_log.LogException('Missing handler for [%s]' % aVar, sys.exc_info())
			return None

#		if aVar is None:
#			_log.Log(gmLog.lErr, 'Anonymous attributes not supported. Need to supply a name.')
#			return None
#		try:
#			return self.__cache[aVar]
#		except KeyError:
#			# not cached yet
#			try:
#				query_tree = self.__query_trees[aVar]
#			except StandardError:
#				_log.LogException ("No query tree available for [%s]." % aVar, sys.exc_info(), fatal=0)
#				return None
#			val = self.__run_queries(query_tree)
#			if val is None:
#				_log.Log(gmLog.lErr, "Cannot retrieve data for attribute [%s] (primary key [%s])." % (aVar, self.ID))
	#--------------------------------------------------------
	# attribute handlers
	#--------------------------------------------------------
	def __getMedDocsList(self):
		"""Build a complete list of metadata for all documents of our patient.

		"""
		blobs_conn = self.__backend.GetConnection('blobs')

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
		self.__backend.ReleaseConnection('blobs')

		return docs
	#--------------------------------------------------------
	def __getActiveName(self):
		curs = self.__defconn.cursor()
		cmd = "select firstnames, lastnames from v_basic_person where id = %s;"
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
	__get_handler['document id list'] = __getMedDocsList
	__get_handler['active name'] = __getActiveName
	#__get_handler['all names'] = __getNamesList

#============================================================
def get_patient():
	"""Get a patient object.

	This is a factory function.

	None - ambigous
	not None - patient object
	exception - failure
	"""
	pass
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

		# start our transaction (done implicitely by defining a cursor)
		cursor = conn.cursor()
		cmd = "SELECT id FROM v_basic_person WHERE %s;" % where_clause
		try:
			cursor.execute(cmd)
		except:
			_log.LogException('>>>%s<<< failed' % (cmd % where_clause), sys.exc_info())
			cursor.close()
			backend.ReleaseConnection('personalia')
			raise
		pat_ids = cursor.fetchall()
		cursor.close()
		backend.ReleaseConnection('personalia')

		if pat_ids is None:
			_log.Log(gmLog.lInfo, "No matching patients.")
		else:
			_log.Log(gmLog.lData, "matching patient IDs: [%s]" % pat_ids)

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
			where_dob = "dob = (select to_timestamp('%s', 'YYYYMMDD'))" % data['dob']

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
#------------------------------------------------------------
def _patient_selected(**kwargs):
	global gmDefPatient
	if gmDefPatient is not None:
		gmDefPatient.commit()

	try:
		tmp = gmPatient(aPKey = kwargs['kwds']['ID'])
	except:
		_log.Log(gmLog.lPanic, str(kwargs))
		_log.LogException('Cannot change to patient [%s].' % kwargs['kwds']['ID'], sys.exc_info(), fatal=1)
		return None
	gmDefPatient = tmp
#============================================================
if __name__ == "__main__":
	while 1:
		pID = raw_input('a patient ID: ')
		try:
			myPatient = gmPatient(aPKey = pID)
		except:
			_log.LogException('Unable to set up patient with ID [%s]' % pID, sys.exc_info())
			print "patient", pID, "can not be set up"
			continue
		print myPatient.ID, myPatient['active name']
		print myPatient['document id list']
		print myPatient['missing handler']
else:
	gmDispatcher.connect(_patient_selected, gmSignals.patient_selected())
#============================================================
# $Log: gmTmpPatient.py,v $
# Revision 1.9  2003-02-21 16:42:02  ncq
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
