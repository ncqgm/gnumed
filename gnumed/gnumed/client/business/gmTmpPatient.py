"""GnuMed temporary patient object.

This a patient object intended to let a useful client-side
API crystallize from actual use in true XP fashion.

license: GPL
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/business/Attic/gmTmpPatient.py,v $
# $Id: gmTmpPatient.py,v 1.4 2003-02-09 23:38:21 ncq Exp $
__version__ = "$Revision: 1.4 $"
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
# may get preloaded by the waiting list
class gmPatient:
	"""Represents a patient that DOES EXIST in the database.

	- searching and creation is done OUTSIDE this object
	"""
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

		self.__cache = {}
		self.__query_trees = {}
		self.PUPIC = ""
		self.OID = None
		# if true the managed patient can't be changed, this
		# is useful if some other software called us with a
		# specific patient pre-selected
		self.locked = (1==0)

		# register backend notification interests ...
		#if not self.__register_interests():
		#	raise gmExceptions.ConstructorError, "Cannot register patient modification interests."

		_log.Log(gmLog.lData, 'Instantiated patient [%s].' % self.ID)
	#--------------------------------------------------------
	def setQueryTree(self, aCol, aQueryTree = None):
		if aQueryTree is None:
			return None
		self.__query_trees[aCol] = aQueryTree
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
	def __getitem__(self, aVar = None):
		"""Return any attribute if known how to retrieve it.

		Either the built in mapper knows how to access the data in the database
		or you must have provided queries. The mapper, of course, caches how to
		access data in the database.

		The values themselves are cached, too, until a backend notification is received
		for this patient.

		We may hand off regetting data after a change notification to a thread.
		"""
		if aVar is None:
			_log.Log(gmLog.lErr, 'Anonymous attributes not supported. Need to supply a name.')
			return None
		try:
			return self.__cache[aVar]
		except KeyError:
			# not cached yet
			try:
				query_tree = self.__query_trees[aVar]
			except StandardError:
				_log.LogException ("No query tree available for [%s]." % aVar, sys.exc_info(), fatal=0)
				return None
			val = self.__run_queries(query_tree)
			if val is None:
				_log.Log(gmLog.lErr, "Cannot retrieve data for attribute [%s] (primary key [%s])." % (aVar, self.ID))
	#--------------------------------------------------------
	# messaging
	#--------------------------------------------------------
	def __register_interests(self):
		# backend
		self.__backend.Listen(
			service = 'personalia',
			signal = "%s.%s" % (gmSignals.patient_modified(), self.ID),
			callback = self.__patient_modified
		)
	#--------------------------------------------------------
	def __patient_modified(self):
		# uh, oh, cache may have been modified ...
		# <DEBUG>
		_log.Log(gmLog.lData, "patient_modified signal received from backend")
		# </DEBUG>
	#--------------------------------------------------------
	def getMedDocsList(self):
		"""Build a complete list of metadata for all documents of our patient.

		"""
		blobs_conn = self.__backend.GetConnection('blobs')

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
		self.__backend.ReleaseConnection('blobs')

		return docs
	#--------------------------------------------------------
	def getActiveName(self, format = None):
		if format is None:
			format = '$first$ $last$'
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
			result = format.replace('$first$', data[0])
			result = result.replace('$last$', data[1])
			return result
	#--------------------------------------------------------
	def commit(self):
		"""Do cleanups before dying.

		- note that this may be called in a thread
		"""
		print "committing patient data"
#============================================================
def get_patient():
	"""Get a patient object.

	This is a factory function.

	None - ambigous
	not None - patient object
	exception - failure
	"""
#------------------------------------------------------------
def _patient_selected(**kwargs):
	global gmDefPatient
	if not gmDefPatient is None:
		gmDefPatient.commit()
	gmDefPatient = None
	try:
		gmDefPatient = gmPatient(aPKey = kwargs['kwds']['ID'])
	except:
		_log.LogException('Cannot change to patient [%s].' % str(kwargs), sys.exc_info())
#============================================================
if __name__ == "__main__":
	while 1:
		pID = raw_input('a patient ID: ')
		try:
			myPatient = gmPatient(aPKey = pID)
		except:
			_log.LogException('Unable to set up patient with ID [%s]' % pID, sys.exc_info())
			print "patient", pID, "does not exist"
			continue
		print "patient", pID, "exists"
		print myPatient.getMedDocsList()
else:
	gmDispatcher.connect(_patient_selected, gmSignals.patient_selected())
#============================================================
# $Log: gmTmpPatient.py,v $
# Revision 1.4  2003-02-09 23:38:21  ncq
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
