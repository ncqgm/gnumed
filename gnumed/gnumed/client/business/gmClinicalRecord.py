"""GnuMed preliminary clinical patient record.

This is a clinical record object intended to let a useful
client-side API crystallize from actual use in true XP fashion.

license: GPL
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/business/gmClinicalRecord.py,v $
# $Id: gmClinicalRecord.py,v 1.5 2003-05-05 00:06:32 ncq Exp $
__version__ = "$Revision: 1.5 $"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"

# access our modules
import sys, os.path, string
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
		self._backend = gmPG.ConnectionPool()
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

		_log.Log(gmLog.lData, 'Instantiated clinical record for patient [%s].' % self.id_patient)
	#--------------------------------------------------------
	def __del__(self):
		self._backend.Unlisten(service = 'historica', signal = gmSignals.allergy_add_del_db(), callback = self._allergy_added_deleted)
		if self.__dict__.has_key('_backend'):
			self._backend.ReleaseConnection('historica')
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
		curs = self._defconn_ro.cursor()
		cmd = "select exists(select id from identity where id = %s);"
		try:
			curs.execute(cmd, self.id_patient)
		except:
			curs.close()
			_log.LogException('>>>%s<<< failed' % (cmd % self.id_patient), sys.exc_info(), fatal=0)
			return None
		res = curs.fetchone()[0]
		curs.close()
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
		curs = self._defconn_ro.cursor()
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
		cmd = "select * from v_i18n_patient_allergies where id_patient='%s';" % self.id_patient
		if not gmPG.run_query(curs, cmd):
			curs.close()
			_log.Log(gmLog.lErr, 'cannot load allergies for patient [%s]' % self.id_patient)
			return None
		rows = curs.fetchall()
		curs.close()
		self.__db_cache['allergies'] = rows
		return self.__db_cache['allergies']
	#--------------------------------------------------------
	def _get_allergy_names(self):
		data = []
		try:
			self.__db_cache['allergies']
		except KeyError:
			if not self._get_allergies():
				return data
		for allergy in self.__db_cache['allergies']:
			tmp = {}
			tmp['id'] = allergy[0]
			# do we know the allergene ?
			if allergy[10] not in [None, '']:
				tmp['name'] = allergy[10]
			# not but the substance
			else:
				tmp['name'] = allergy[7]
			data.append(tmp)
		return data
	#--------------------------------------------------------
	def _get_allergies_list(self):
		"""Return list of IDs in v_i18n_allergy for this patient."""
		try:
			return self.__db_cache['allergy IDs']
		except KeyError:
			pass
		self.__db_cache['allergy IDs'] = []
		transactions = string.join(self['clinical transaction IDs'], ',')
		if transactions == '':
			return self.__db_cache['allergy IDs']
		curs = self._defconn_ro.cursor()
		cmd = "select id from v_i18n_allergy where id_clin_transaction in (%s);" % transactions
		if not gmPG.run_query(curs, cmd):
			curs.close()
			_log.Log(gmLog.lErr, 'cannot load list of allergies for patient [%s]' % self.id_patient)
			return None
		rows = curs.fetchall()
		curs.close()
		for row in rows:
			self.__db_cache['allergy IDs'].extend(row)
		return self.__db_cache['allergy IDs']
	#--------------------------------------------------------
	def _get_clinical_transactions_list(self):
		curs = self._defconn_ro.cursor()
		cmd = "select id_transaction from v_patient_transactions where id_patient='%s';" % self.id_patient
		if not gmPG.run_query(curs, cmd):
			curs.close()
			_log.Log(gmLog.lErr, 'cannot load list of transactions for patient [%s]' % self.id_patient)
			return None
		rows = curs.fetchall()
		curs.close()
		tx_list = []
		for row in rows:
			tx_list.extend(row)
		return tx_list
	#--------------------------------------------------------
	# set up handler map
	_get_handler['patient ID'] = _get_patient_ID
#	_get_handler['allergy IDs'] = _get_allergies_list
	_get_handler['allergy names'] = _get_allergy_names
	_get_handler['allergies'] = _get_allergies
	_get_handler['clinical transaction IDs'] = _get_clinical_transactions_list
#============================================================
# main
#------------------------------------------------------------
if __name__ == "__main__":
	record = gmClinicalRecord(aPKey = 1)
#	print "clinical transaction IDs:", record['clinical transaction IDs']
#	print "allergy IDs:", record['allergy IDs']
	while 1:
		pass
	del record
#============================================================
# $Log: gmClinicalRecord.py,v $
# Revision 1.5  2003-05-05 00:06:32  ncq
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
