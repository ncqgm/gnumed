"""GnuMed preliminary clinical patient record.

This is a clinical record object intended to let a useful
client-side API crystallize from actual use in true XP fashion.

license: GPL
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/business/gmClinicalRecord.py,v $
# $Id: gmClinicalRecord.py,v 1.18 2003-06-02 20:58:32 ncq Exp $
__version__ = "$Revision: 1.18 $"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"

# access our modules
import sys, os.path, string
import time
if __name__ == "__main__":
	sys.path.append(os.path.join('..', 'python-common'))

# start logging
import gmLog
_log = gmLog.gmDefLog
if __name__ == "__main__":
	_log.SetAllLogLevels(gmLog.lData)
_log.Log(gmLog.lData, __version__)

import gmExceptions, gmPG, gmSignals, gmDispatcher

# 3rd party
#import mx.DateTime as mxDateTime
#============================================================
class gmClinicalRecord:

	# handlers for __getitem__()
	_get_handler = {}

	def __init__(self, aPKey = None):
		"""Fails if

		- no connection to database possible
		- patient referenced by aPKey does not exist
		"""
		self.transactionCursor = None
		self._backend = gmPG.ConnectionPool()

		# this connection may drop , so need to get fresh one
		# from backend at each usage , IMHO
		self._defconn_ro = self._backend.GetConnection('historica')
		if self._defconn_ro is None:
			raise gmExceptions.ConstructorError, "Cannot connect to database." % aPKey

		self.id_patient = aPKey			# == identity.id == primary key
		if not self._pkey_exists():
			raise gmExceptions.ConstructorError, "No patient with ID [%s] in database." % aPKey

		self.__db_cache = {}

		# register backend notification interests ...
		if not self._register_interests():
			raise gmExceptions.ConstructorError, "cannot register signal interests"

		# make sure we have a __default__ health issue
		self.id_default_health_issue = None
		if not self.__load_default_health_issue():
			raise gmExceptions.ConstructorError, "cannot activate default health issue for patient [%s]" % aPKey

		# what episode did we work on last time we saw this patient ?
		self.id_episode = None
		if not self.__load_most_recent_episode():
			raise gmExceptions.ConstructorError, "cannot activate an episode for patient [%s]" % aPKey

#		self.ensure_current_clinical_encounter()
#		self.init_issue_episodes()

		_log.Log(gmLog.lData, 'Instantiated clinical record for patient [%s].' % self.id_patient)
	#--------------------------------------------------------
	def __del__(self):
		self._backend.Unlisten(service = 'historica', signal = gmSignals.allergy_add_del_db(), callback = self._allergy_added_deleted)
		if self.__dict__.has_key('_backend'):
			self._backend.ReleaseConnection('historica')
	#--------------------------------------------------------
	# FIXME: temporary hack for dropping connections (?)
	def getConnection(self):
		return gmPG.ConnectionPool().GetConnection("historica")
	#--------------------------------------------------------
	def getCursor(self):
		return self.getConnection().cursor()
	#--------------------------------------------------------
	# cache handling
	#--------------------------------------------------------
	def commit(self):
		"""Do cleanups before dying.

		- note that this may be called in a thread
		"""
		# unlisten to signals
		print "unimplemented: committing clinical record data"
	#--------------------------------------------------------
	def invalidate_cache(self):
		"""Called when the cache turns cold.

		"""
		print "unimplemented: invalidating clinical record data cache"
	#--------------------------------------------------------
	# internal helper
	#--------------------------------------------------------
	def _pkey_exists(self):
		"""Does this primary key exist ?

		- true/false/None
		"""
		#curs = self._defconn_ro.cursor()
		#cmd = "select exists(select id from identity where id = %s)" % self.id_patient
		cmd = "select id from identity where id = %s" % self.id_patient
		rows = None
		try:
			rows = self.execute(cmd, "Unable to check existence of id %s in identity" % self.id_patient)
		except:
			_log.LogException("Failed select id from identity", sys.exc_info(), 4)
			pass
		#------------------------------------	
		# still has bug about portal closed.
		# REMOVE when bug sorted out
		if (rows is None or len(rows) == 0):		
			try:
				rows, description = gmPG.quickROQuery( cmd)
			except:
				_log.LogException('>>>%s<<< failed' % cmd , sys.exc_info(), 4)
			#curs.close()
			return None
		#row = curs.fetchone()
		#<DEBUG>
		_log.Data("result of id check = " + str(rows) )
		#</DEBUG>
		res = rows[0][0]
		#curs.close()
		return res
	#--------------------------------------------------------
	# messaging
	#--------------------------------------------------------
	def _register_interests(self):
		# backend
		if not self._backend.Listen(service = 'historica', signal = gmSignals.allergy_add_del_db(), callback = self._allergy_added_deleted):
			return None
		return 1
	#--------------------------------------------------------
	def _allergy_added_deleted(self):
		#curs = self._defconn_ro.cursor()
		curs = self.getCursor()
		# did number of allergies change for our patient ?
		cmd = "select count(id) from v_i18n_patient_allergies where id_patient='%s';" % self.id_patient
		if not gmPG.run_query(curs, cmd):
			curs.close()
			_log.Log(gmLog.lData, 'cannot check for added/deleted allergies, assuming addition/deletion did occurr')
			# error: invalidate cache
			del self.__db_cache['allergies']
			# and tell others
			gmDispatcher.send(signal = gmSignals.allergy_updated(), sender = self.__class__.__name__)
			return 1
		result = curs.fetchone()
		curs.close()
		# not cached yet
		try:
			nr_cached_allergies = len(self.__db_cache['allergies'])
		except KeyError:
			gmDispatcher.send(signal = gmSignals.allergy_updated(), sender = self.__class__.__name__)
			return 1
		# no change for our patient ...
		if result == nr_cached_allergies:
			return 1
		# else invalidate cache
		del self.__db_cache['allergies']
		gmDispatcher.send(signal = gmSignals.allergy_updated(), sender = self.__class__.__name__)
		return 1
	#--------------------------------------------------------
#	def _patient_modified(self):
		# uh, oh, cache may have been modified ...
		# <DEBUG>
#		_log.Log(gmLog.lData, "patient_modified signal received from backend")
		# </DEBUG>
		# this is fraught with problems:
		# can we safely just throw away the cache ?
		# we may have new data in there ...
#		self.invalidate_cache()
	#--------------------------------------------------------
	# __getitem__ handling
	#--------------------------------------------------------
	def __getitem__(self, aVar = None):
		"""Return any attribute if known how to retrieve it.
		"""
		try:
			return gmClinicalRecord._get_handler[aVar](self)
		except KeyError:
			_log.LogException('Missing get handler for [%s]' % aVar, sys.exc_info())
			return None
	#--------------------------------------------------------
	def _get_patient_ID(self):
		return self.id_patient
	#--------------------------------------------------------
	def _get_allergies(self):
		"""Return rows in v_i18n_allergies for this patient"""
		try:
			return self.__db_cache['allergies']
		except:
			pass
		curs = self._defconn_ro.cursor()
		# the connection can become stale
#		curs = self.getCursor()
		cmd = "select * from v_i18n_patient_allergies where id_patient='%s';" % self.id_patient
		if not gmPG.run_query(curs, cmd):
			curs.close()
			_log.Log(gmLog.lErr, 'cannot load allergies for patient [%s]' % self.id_patient)
			return None
		rows = curs.fetchall()
		curs.close()
		self.__db_cache['allergies'] = rows
		#<DEBUG>
		_log.Data("gmClinicalRecord.db_cache['allergies']: %s" % str(rows))
		#</DEBUG>
		return self.__db_cache['allergies']
	#--------------------------------------------------------
	def _get_allergy_names(self):
		data = []
		try:
			self.__db_cache['allergies']
		except KeyError:
			if not self._get_allergies():
				_log.Log(gmLog.lErr, "Could not load allergies")
				return data
		for allergy in self.__db_cache['allergies']:
			tmp = {}
			tmp['id'] = allergy[0]
			# do we know the allergene ?
			if allergy[10] not in [None, '']:
				tmp['name'] = allergy[10]
			# no but the substance
			else:
				tmp['name'] = allergy[6]
			data.append(tmp)
		return data
	#--------------------------------------------------------
	def _get_allergies_list(self):
		"""Return list of IDs in v_i18n_patient_allergies for this patient."""
		try:
			return self.__db_cache['allergy IDs']
		except KeyError:
			pass
		self.__db_cache['allergy IDs'] = []
		cmd = "select id from v_i18n_patient_allergies where id_patient='%s';" % self.id_patient
		curs = self._defconn_ro.cursor()
#		curs = self.getCursor()
		if not gmPG.run_query(curs, cmd):
			curs.close()
			_log.Log(gmLog.lErr, 'cannot load list of allergies for patient [%s]' % self.id_patient)
			return None
		rows = curs.fetchall()
		curs.close()
		for row in rows:
			self.__db_cache['allergy IDs'].extend(row)
		return self.__db_cache['allergy IDs']
	#------------------------------------------------------------------
	# health issue related helpers
	#------------------------------------------------------------------
	def __load_default_health_issue(self):
		self.id_default_health_issue = self._create_health_issue()
		if self.id_default_health_issue is None:
			_log.Log(gmLog.lErr, 'cannot load default health issue for patient [%s]' % self.id_patient)
			return None
		return 1
	#------------------------------------------------------------------
	def _create_health_issue(self, health_issue_name = '__default__'):
		curs = self._defconn_ro.cursor()
		cmd = "select id from clin_health_issue where id_patient='%s' and description='%s';" % (self.id_patient, health_issue_name)
		if not gmPG.run_query(curs, cmd):
			curs.close()
			_log.Log(gmLog.lErr, 'cannot check if health issue [%s] exists for patient [%s]' % (health_issue_name, self.id_patient))
			return None
		row = curs.fetchone()
		curs.close()
		# issue exists already
		if row is not None:
			return row[0]
		# issue does not exist yet so create it
		rw_conn = self._backend.GetConnection('historica', readonly = 0)
		curs = rw_conn.cursor()
		cmd = "insert into clin_health_issue (id_patient, description) values (%d, '%s');" % (self.id_patient, health_issue_name)
		if not gmPG.run_query(curs, cmd):
			curs.close()
			rw_conn.close()
			_log.Log(gmLog.lErr, 'cannot insert health issue [%s] for patient [%s]' % (health_issue_name, self.id_patient))
			return None
		# get id for it
		cmd = "select currval('clin_health_issue_id_seq');"
		if not gmPG.run_query(curs, cmd):
			curs.close()
			rw_conn.close()
			_log.Log(gmLog.lErr, 'cannot obtain id of last health issue insertion')
			return None
		id_issue = curs.fetchone()[0]
		# and commit our work
		rw_conn.commit()
		curs.close()
		rw_conn.close()
		return id_issue
	#------------------------------------------------------------------
	# episode related helpers
	#------------------------------------------------------------------
	def __load_most_recent_episode(self):
		# check if there's an active episode
		curs = self._defconn_ro.cursor()
		cmd = "select id_episode from last_active_episode where id_patient='%s' limit 1;" % self.id_patient
		if not gmPG.run_query(curs, cmd):
			curs.close()
			_log.Log(gmLog.lErr, 'cannot load last active episode for patient [%s]' % self.id_patient)
			return None
		row = curs.fetchone()
		curs.close()
		# no: should only happen in new patients
		if row is None:
			# try to set one to active or create default one
			if not self._set_active_episode():
				_log.Log(gmLog.lErr, 'cannot activate default episode for patient [%s]' % self.id_patient)
				return None
		else:
			self.id_episode = row[0]
		return 1
	#------------------------------------------------------------------
	def _set_active_episode(self, episode_name = '__default__'):
		ro_curs = self._defconn_ro.cursor()
		# does this episode exist at all ?
		# (else we can't activate it in the first place)
		cmd = "select id_episode from v_patient_episodes where id_patient='%s' and episode='%s' limit 1;" % (self.id_patient, episode_name)
		if not gmPG.run_query(ro_curs, cmd):
			ro_curs.close()
			_log.Log(gmLog.lErr, 'cannot load episode [%s] for patient [%s]' % (episode_name, self.id_patient))
			return None
		row = ro_curs.fetchone()
		ro_curs.close()
		# no
		if row is None:
			# if __default__ then create it
			if episode_name == '__default__':
				id_episode = self._create_episode()
				# unless that fails
				if id_episode is None:
					return None
			# else fail
			else:
				_log.Log(gmLog.lErr, 'patient [%s] has no episode [%s]' % (self.id_patient, episode_name))
				return None
		# yes
		else:
			id_episode = row[0]

		# eventually activate it
		rw_conn = self._backend.GetConnection('historica', readonly = 0)
		rw_curs = rw_conn.cursor()
		# delete old entry
		cmd = "delete from last_active_episode where id_patient='%s';" % self.id_patient
		if not gmPG.run_query(rw_curs, cmd):
			_log.Log(gmLog.lWarn, 'cannot delete last active episode entry for patient [%s]' % (self.id_patient))
			# try continuing anyways
		cmd = "insert into last_active_episode (id_episode, id_patient) values (%d, %d);" % (id_episode, self.id_patient)
		if not gmPG.run_query(rw_curs, cmd):
			_log.Log(gmLog.lErr, 'cannot activate episode [%s] for patient [%s]' % (id_episode, self.id_patient))
			rw_curs.close()
			rw_conn.close()
			return None
		# seems we succeeded
		rw_conn.commit()
		rw_curs.close()
		rw_conn.close()
		self.id_episode = id_episode
		return 1
	#------------------------------------------------------------------
	def _create_episode(self, episode_name = '__default__'):
		ro_curs = self._defconn_ro.cursor()
		# anything to do ?
		cmd = "select id_episode from v_patient_episodes where id_patient='%s' and episode='%s' limit 1;" % (self.id_patient, episode_name)
		if not gmPG.run_query(ro_curs, cmd):
			ro_curs.close()
			_log.Log(gmLog.lErr, 'cannot check if episode [%s] exists for patient [%s]' % (episode_name, self.id_patient))
			return None
		row = ro_curs.fetchone()
		ro_curs.close()
		# episode already exists
		if row is not None:
			return row[0]
		# episode does not exist yet so create it
		rw_conn = self._backend.GetConnection('historica', readonly = 0)
		rw_curs = rw_conn.cursor()
		# by default new episodes belong to the __default__ health issue
		# FIXME: finish
#		cmd = "insert into "
	#------------------------------------------------------------------
	#------------------------------------------------------------------
	# trial 
	def create_allergy(self, map):
		"""tries to add allergy to database : Currently id_type is not reading checkbox states (allergy or sensitivity)."""

		self.beginTransaction()
		
		issue_id = self.ensure_health_issue_exists("allergy")
		episode_id = self.get_or_create_episode_for_issue(issue_id)
		
		if episode_id == 0:
			self.execute("rollback", "rolling back because of invalid episode_id = 0")
			return 0

		encounter_id = self.ensure_current_clinical_encounter()
		if encounter_id == 0:
			self.execute("rollback", "rolling back because of invalid encounter_id = 0")
			return 0



		# **** NB DEFINATE IS MISPELLED IN SQL SCRIPT : CHANGE IF THE WRONG SPELLING LATER 
		# try both , depending on which sql script
		
		cmd_part = "insert into allergy(id_type, id_encounter, id_episode,  substance, reaction, %s )"

		value_part = " values (%d, %d, %d,  '%s', '%s', '%s' )" % (1, encounter_id, episode_id, map["substance"], map["reaction"], map["definite"] )
		cmd = cmd_part % "definite"  + value_part
		if self.execute( cmd, "insert allergy failed with definAte ", rollback = 0 ) is None:
			# remove this if really upto date
			cmd = cmd_part % "definate"  + value_part
			self.execute( cmd, "insert allergy failed with definIte as definite", rollback = 1 )
				
			

		#cmd = "insert into allergy(id_type, id_encounter, id_episode,  substance, reaction, definite ) values (%d, %d, %d,  '%s', '%s', '%s' )" % (1, encounter_id, episode_id, map["substance"], map["reaction"], map["definite"] )
		#self.execute( cmd, "unable to create allergy entry ", rollback = 1)

		#idiosyncratic bug.
		#seems like calling commit by sql doesn't commit the
		#the connection properly, prematurely closing it?

		# this may well be true but why not using the conn.commit()
		# provided by the DB-API ?

		#self.execute("commit", "unable to commit ", rollback = 1)

		#_log.Data("after commit")

		self.endTransaction()
		#<DEBUG>
		_log.Data("after end Transaction")
		#</DEBUG>
		


		#need to invalidate cache or add to it.
		#del self.__db_cache("allergies")	
		self._allergy_added_deleted()
		# send signal to update listeners
		#gmDispatcher.send(signal = gmSignals.allergy_updated(), sender = self.__class__.__name__)
		return 1


	def ensure_health_issue_exists(self, issue):
		"""ensure that the  health issue exists for this patient_id"""
		
		cmd = "select id from clin_health_issue where id_patient=%s and description='%s'" % (self.id_patient, issue)

		rows = self.execute(cmd, "Unable to select for %s health issue for id_patient=%s " % (issue, self.id_patient ))

		if (rows <> None and len(rows) == 0):
			cmd2 = "insert into clin_health_issue ( id_patient, description) values ( %s, '%s')" %( self.id_patient, issue)
			self.execute(cmd2, "can't insert issue %s" % issue)
			rows = self.execute(cmd, "not finding clin_issue %s" % issue )
		
		if (rows <> None and len(rows) == 1):
			return rows[0][0]
		
		return 0

#------------ deal with clin episodes for health issues ------------------------	
	def init_issue_episodes(self):
		self.issue_episodes={}
	
	def has_episode_for_issue(self, issue_id):
		return  self.issue_episodes.has_key(issue_id)

	def get_episode_for_issue(self, issue_id):
		if self.has_episode_for_issue(issue_id):
			return self.issue_episodes[issue_id]
		return 0

	def create_episode_for_issue(self, issue_id):
		marker  = time.asctime()
		cmd = "insert into clin_episode( id_health_issue, description ) values ( %d , '%s')" % (issue_id, marker)
		if self.execute(cmd, "unable to create issue") is None:
			return 0
		cmd = "select id from clin_episode where id_health_issue=%d  and description='%s'" %(issue_id, marker)
		rows = self.execute(cmd, "unable to find most recent episode insertion")
		if rows is None or len(rows) > 1:
			_log.Log(gmLog.lErr, "rows not valid. Should be only one row : rows="+str(rows) )
			return 0
		
		episode_id = rows[0][0]
		self.issue_episodes[issue_id]= episode_id
		return episode_id


	def get_or_create_episode_for_issue(self, issue_id):
		if self.has_episode_for_issue(issue_id):
			return self.get_episode_for_issue(issue_id)
		return self.create_episode_for_issue(issue_id)

#---------------------------------------------------------------------------------


#------------ deal with clinical encounter id ---------------------------------
	def ensure_current_clinical_encounter(self):
		if self.__dict__.has_key('clin_encounter'):
			return self.clin_encounter

		marker = time.asctime()
		cmd = "insert into clin_encounter( id_location, id_provider, id_type, description ) values(0 , 0, 1, '%s' ) " % marker
		if self.execute(cmd, "unable to create clin encounter") is None:
			return 0
		cmd = "select id  from clin_encounter where description = '%s'" % marker
		rows = self.execute(cmd, "unable to select recently created encounter")
		if rows is None:
			return 0
		if len (rows) <> 1 :
			_log.Log(gmLog.lErr, "there are %d rows with marker %s. Row should be unique" %(len(rows), marker) )
		self.clin_encounter = rows[0][0]
		return rows[0][0]

#-------------- convenience sql call interface ----------------------------------------
	def execute(self, cmd, error_msg, rollback = 0):
		#<DEBUG>
		_log.Data("Running query : %s" % cmd)
		#</DEBUG>
		curs = self.getTransactionCursor()
		if curs is None:
			curs = self.getCursor()
		if not gmPG.run_query(curs, cmd):
			# this is utterly useless !!
#			if rollback and not gmPG.run_query(curs, "rollback"):
#				_log.Log(gm.lErr, "*****   Unable to rollback", sys.exc_info() )
			# just closing the cursor without a commit rolls back
			# and why would we want to roll back if we don't
			# even check for is_update_command ?!?

			#ok 
			if rollback:
				curs.close()
			_log.Log(gmLog.lErr, error_msg)
			
			return None

		if self.is_update_command(cmd):
			# uhm, wouldn't you want to commit() here ?!?
			return []  # don't fetch from cursor	
		rows = curs.fetchall()
		# I am completely stumped as to what you want to achieve here
		if self.getTransactionCursor() is None:
			curs.close()
		
		return rows

	def beginTransaction(self):
		"""I think the semantics is one connection is one
		transaction context.  Save a connection for 
		the transaction commit by calling connection.commit() """
		self.transactionConnection = self.getConnection()
		self.transactionCursor = self.transactionConnection.cursor()
	
	def endTransaction(self):
		if self.transactionCursor <> None:
			#self.transactionCursor.close()
			self.transactionCursor.close()
			self.transactionConnection.commit()
			self.transactionConnection = None
			self.transactionCursor = None

	def getTransactionCursor(self):
		return self.transactionCursor


	def is_update_command(self, cmd):
		if 	string.find(string.lower(cmd), "insert") >= 0 or \
			string.find(string.lower(cmd), "update") >= 0 or \
			string.find(string.lower(cmd), "delete") >= 0 or \
			string.find(string.lower(cmd), "commit") >= 0 or \
			string.find(string.lower(cmd), "select into") >= 0:
				return 1
	
	#--------------------------------------------------------
	# set up handler map
	_get_handler['patient ID'] = _get_patient_ID
#	_get_handler['allergy IDs'] = _get_allergies_list
	_get_handler['allergy names'] = _get_allergy_names
	_get_handler['allergies'] = _get_allergies
#============================================================
# main
#------------------------------------------------------------
if __name__ == "__main__":
	record = gmClinicalRecord(aPKey = 1)
#	print "clinical transaction IDs:", record['clinical transaction IDs']
#	print "allergy IDs:", record['allergy IDs']
#	while 1:
#		pass
	import time
	time.sleep(5)
	del record
	dbpool = gmPG.ConnectionPool()
	conn = dbpool.GetConnection('default', readonly = 0)
	if conn is not None:
		_log.Log(gmLog.lInfo, 'getting RW connection succeeded')
	conn.close()
#============================================================
# $Log: gmClinicalRecord.py,v $
# Revision 1.18  2003-06-02 20:58:32  ncq
# - nearly finished with default episode/health issue stuff
#
# Revision 1.17  2003/06/01 16:25:51  ncq
# - preliminary code for episode handling
#
# Revision 1.16  2003/06/01 15:00:31  sjtan
#
# works with definite, maybe note definate.
#
# Revision 1.15  2003/06/01 14:45:31  sjtan
#
# definite and definate databases catered for, temporarily.
#
# Revision 1.14  2003/06/01 14:34:47  sjtan
#
# hopefully complies with temporary model; not using setData now ( but that did work).
# Please leave a working and tested substitute (i.e. select a patient , allergy list
# will change; check allergy panel allows update of allergy list), if still
# not satisfied. I need a working model-view connection ; trying to get at least
# a basically database updating version going .
#
# Revision 1.13  2003/06/01 14:15:48  ncq
# - more comments
#
# Revision 1.12  2003/06/01 14:11:52  ncq
# - added some comments
#
# Revision 1.11  2003/06/01 14:07:42  ncq
# - "select into" is an update command, too
#
# Revision 1.10  2003/06/01 13:53:55  ncq
# - typo fixes, cleanup, spelling definate -> definite
# - fix my obsolote handling of patient allergies tables
# - remove obsolete clin_transaction stuff
#
# Revision 1.9  2003/06/01 13:20:32  sjtan
#
# logging to data stream for debugging. Adding DEBUG tags when work out how to use vi
# with regular expression groups (maybe never).
#
# Revision 1.8  2003/06/01 12:55:58  sjtan
#
# sql commit may cause PortalClose, whilst connection.commit() doesnt?
#
# Revision 1.7  2003/06/01 01:47:32  sjtan
#
# starting allergy connections.
#
# Revision 1.6  2003/05/17 17:23:43  ncq
# - a little more testing in main()
#
# Revision 1.5  2003/05/05 00:06:32  ncq
# - make allergies work again after EMR rework
#
# Revision 1.4  2003/05/03 14:11:22  ncq
# - make allergy change signalling work properly
#
# Revision 1.3  2003/05/03 00:41:14  ncq
# - fetchall() returns list, not dict, so handle accordingly in "allergy names"
#
# Revision 1.2  2003/05/01 14:59:24  ncq
# - listen on allergy add/delete in backend, invalidate cache and notify frontend
# - "allergies", "allergy names" getters
#
# Revision 1.1  2003/04/29 12:33:20  ncq
# - first draft
#
