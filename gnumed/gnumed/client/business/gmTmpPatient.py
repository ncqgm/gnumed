"""GnuMed temporary patient object.

This a patient object intended to let a useful client-side
API crystallize from actual use in true XP fashion.

license: GPL
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/business/Attic/gmTmpPatient.py,v $
# $Id: gmTmpPatient.py,v 1.1 2003-02-01 17:53:12 ncq Exp $
__version__ = "$Revision: 1.1 $"
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

curr_pat = None
#============================================================
# may get preloaded by the waiting list
class cPatient:
	def __init__():
		self.__cache = {}
		self.__query_trees = {}
		self.PUPIC = ""
		self.ID = None
		self.OID = None
		# if true the managed patient can't be changed, this
		# is useful if some other software called us with a
		# specific patient pre-selected
		self.locked = (1==0)
	#--------------------------------------------------------
	def get (self, aVar = None, aQueryTree = None):
		"""Return any attribute if known how to retrieve it.

		Either the built in mapper knows how to access the data in the database
		or you must provide the service and a query. The mapper, of course,
		caches how to access data in the database.

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
			pass
		if aQueryTree is not None:
			# run queries and return result
			pass
	#--------------------------------------------------------
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
# Revision 1.1  2003-02-01 17:53:12  ncq
# - doesn't do anything, just to show people where I am going
#
