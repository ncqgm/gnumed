"""GnuMed temporary patient object.

This a patient object intended to let a useful client-side
API crystallize from actual use in true XP fashion.

license: GPL
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/business/Attic/gmTmpPatient.py,v $
# $Id: gmTmpPatient.py,v 1.2 2003-02-06 15:40:58 ncq Exp $
__version__ = "$Revision: 1.2 $"
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

import gmExceptions, gmBackendListener, gmSignals

curr_pat = None
#============================================================
# may get preloaded by the waiting list
class cPatient:
	"""Represent a patient that DOES EXIST in the database.

	- searching and creation is done OUTSIDE this object
	"""
	def __init__(self, aPKey = None):
		"""Fails if patient referenced by aPKey does not exist.
		"""
		self.ID = aPKey			# == identity.id == primary key
		if self.__pkey_exists() is None:
			raise gmExceptions.ConstructorError, "No patient with ID [%s] in database."

		self.__cache = {}
		self.__query_trees = {}
		self.PUPIC = ""
		self.OID = None
		# if true the managed patient can't be changed, this
		# is useful if some other software called us with a
		# specific patient pre-selected
		self.locked = (1==0)

		# register backend notification interests ...
		# FIXME: this should be a brokered listener object, no ?
		if not self.__register_interests():
			raise gmExceptions.ConstructorError, "Cannot register patient modification interests."
	#--------------------------------------------------------
	def setQueryTree(self, aCol, aQueryTree = None):
		if aQueryTree is None:
			return None
		self.__query_trees[aCol] = aQueryTree
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
		self.db_listener = gmBackendListener.BackendListener(
			service = 'personalia',
			database = ,
			user = ,
			password = ,
			host = 
			)
		self.db_listener.RegisterCallback(
			callback = self.__patient_modified,
			signal = "%s.%s" % (gmSignals.patient_modified(), self.ID)
		)
	#--------------------------------------------------------
	def __patient_modified(self):
		# uh, oh, cache may have been modified ...
#============================================================
def get_patient():
	"""Get a patient object.

	This is a factory function.

	None - ambigous
	not None - patient object
	exception - failure
	"""
#============================================================
# $Log: gmTmpPatient.py,v $
# Revision 1.2  2003-02-06 15:40:58  ncq
# - hit hard the merge wall
#
# Revision 1.1  2003/02/01 17:53:12  ncq
# - doesn't do anything, just to show people where I am going
#
