"""GnuMed temporary patient object.

This is a patient object intended to let a useful client-side
API crystallize from actual use in true XP fashion.

license: GPL
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/test-area/test-client-c/business/Attic/gmPatient.py,v $
# $Id: gmPatient.py,v 1.1 2003-10-27 14:01:26 sjtan Exp $
__version__ = "$Revision: 1.1 $"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"

# access our modules
import sys, os.path, time

if __name__ == "__main__":
	sys.path.append(os.path.join('..', 'python-common'))

# start logging
import gmLog, gmDemographics
_log = gmLog.gmDefLog
if __name__ == "__main__":
	_log.SetAllLogLevels(gmLog.lData)
_log.Log(gmLog.lData, __version__)

import gmExceptions, gmPG, gmSignals, gmDispatcher, gmClinicalRecord, gmI18N

#============================================================
# may get preloaded by the waiting list
class gmPerson:
	"""Represents a person that DOES EXIST in the database.

	Accepting this as a hard and fast rule WILL simplify
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
			emr = self.__db_cache['clinical record']
			emr.cleanup()
		if self.__db_cache.has_key('demographic record'):
			demos = self.__db_cache['demographic record']
			demos.cleanup()
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
	def _get_clinical_record(self):
		if self.__db_cache.has_key('clinical record'):
			return self.__db_cache['clinical record']
		try:
			self.__db_cache['clinical record'] = gmClinicalRecord.gmClinicalRecord(aPKey = self.__ID)
		except StandardError:
			_log.LogException('cannot instantiate clinical record for person [%s]', sys.exc_info())
			return None
		return self.__db_cache['clinical record']


	#--------------------------------------------------------
	def get_demographic_record(self):
		if self.__db_cache.has_key('demographic record'):
			return self.__db_cache['demographic record']
		try:
			# FIXME: we need some way of setting the type of backend such that
			# to instantiate the correct type of demographic record class
			self.__db_cache['demographic record'] = gmDemographics.gmDemographicRecord_SQL(aPKey = self.__ID)
		except StandardError:
			_log.LogException('cannot instantiate demographic record for person [%s]' % self.__ID, sys.exc_info())
			return None
		return self.__db_cache['demographic record']
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
	_get_handler['demographics'] = get_demographic_record
	_get_handler['clinical record'] = _get_clinical_record
	_get_handler['API'] = _get_API
	_get_handler['ID'] = getID
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
			# init, no previous patient
			if self.patient is None:
				_log.Log(gmLog.lData, 'no previous patient')
				try:
					self.patient = gmPerson(aPKey)
					# remote app must lock explicitly
					self.unlock()
					self.__send_selection_notification()
				except:
					_log.LogException('cannot connect with patient [%s]' % aPKey, sys.exc_info())
			# change to another patient
			else:
				_log.Log(gmLog.lData, 'patient change: [%s] -> [%s]' % (self.patient['ID'], aPKey))
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

	def get_clinical_record(self):
		return self.patient._get_clinical_record()

	def get_demographic_record(self):
		return self.patient.get_demographic_record()
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
def create_dummy_identity():
	cmd1 = "insert into identity(gender, dob) values('N/A', CURRENT_TIMESTAMP)"
	cmd2 = "select currval ('identity_id_seq')"
	data = gmPG.run_commit ('personalia', [(cmd1, []), (cmd2, [])])
	if data is None:
		return None
	return data[0][0]
#============================================================
# main/testing
#============================================================
if __name__ == "__main__":
	#gmDispatcher.connect(_patient_selected, gmSignals.patient_selected())
	while 1:
		pID = raw_input('a patient ID: ')
		if pID == '-1':
			break
		try:
			myPatient = gmCurrentPatient(pID)
		except:
			_log.LogException('Unable to set up patient with ID [%s]' % pID, sys.exc_info())
			print "patient", pID, "can not be set up"
			continue
		print "ID       ", myPatient['ID']
		demos = myPatient['demographics']
		print "demogr.  ", demos
		print "name     ", demos.getActiveName()
		print "doc ids  ", myPatient['document id list']
		emr = myPatient['clinical record']
		print "EMR      ", emr
#		print "fails  ", myPatient['missing handler']
		print "--------------------------------------"
#		api = myPatient['API']
#		for call in api:
#			print "API call: %s (internally %s)" % (call['API call name'], call['internal name'])
#			print call['description']
#============================================================
# $Log: gmPatient.py,v $
# Revision 1.1  2003-10-27 14:01:26  sjtan
#
# syncing with main tree.
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
