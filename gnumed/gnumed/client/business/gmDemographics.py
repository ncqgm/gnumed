"""GnuMed temporary patient object.

This is a patient object intended to let a useful client-side
API crystallize from actual use in true XP fashion.

license: GPL
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/business/Attic/gmDemographics.py,v $
# $Id: gmDemographics.py,v 1.1 2003-10-25 08:48:06 ihaywood Exp $
__version__ = "$Revision: 1.1 $"
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

import gmExceptions, gmPG, gmSignals, gmDispatcher, gmClinicalRecord, gmI18N

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


# virtual ancestor class, SQL and LDAP descendants
class gmPerson:
	def getActiveName (self):
		raise gmExceptions.PureVirtualFunction()

	def setActiveName (self, firstnames, lastnames):
		raise gmExceptions.PureVirtualFunction ()

	def getTitle(self):
		raise gmExceptions.PureVirtualFunction ()

	def setDOB (self, dob):
		raise gmExceptions.PureVirtualFunction ()

	def getDOB(self):
		raise gmExceptions.PureVirtualFunction ()

	def getID(self):
		raise gmExceptions.PureVirtualFunction ()

	def setTitle (self, title):
		raise gmExceptions.PureVirtualFunction ()

	def getAddress (self, type):
		raise gmExceptions.PureVirtualFunction ()

	def deleteAddress (self, ID):
		raise gmExceptions.PureVirtualFunction ()

	def setAddress (self, type, number, street, urb, postcode, state, country):
		raise gmExceptions.PureVirtualFunction ()

	def getCommChannel (self, type):
		raise gmExceptions.PureVirtualFunction ()

	def setCommChannel (self, type, comm):
		raise gmExceptions.PureVirtualFunction ()

	def getMedicalAge(self):
		raise gmExceptions.PureVirtualFunction ()

		
#============================================================
# may get preloaded by the waiting list
class gmSQLPerson (gmPerson):
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

		if aPKey is None:
			# create a new base patient entry
			cmd = "insert into identity (dob) values (current_time)"
			gmPG.run_commit ('personalia', [(cmd, [])])
			cmd = "select currval (identity_id_seq)"
			data = gmPG.run_ro_query (cmd, None, [])
			self.ID = data[0][0] 
		else:
			self.ID = aPKey	# == identity.id == primary key
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
		cmd = "select exists(select id from identity where id = %s)"
		res = gmPG.run_ro_query('personalia', cmd, None, self.ID)
		if res is None:
			_log.Log(gmLog.lErr, 'check for person ID [%s] existence failed' % self.ID)
			return None
		return res[0][0]
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

	def getActiveName(self):
		cmd = "select firstnames, lastnames from v_basic_person where i_id = %s"
		data, idx = gmPG.run_ro_query('personalia', cmd, 1, self.ID)
		if data is None:
			return None
		result = {
			'first': data[0][idx['firstnames']],
			'last': data[0][idx['lastnames']]
		}
		return result
	#--------------------------------------------------------
	def setActiveName (self, firstnames, lastnames):
		cmd = """
update v_basic_person set firstnames = %s, lastnames = %s where i_id = %s
"""
		gmPG.run_commit ('personalia', [(cmd, [firstnames, lastnames, self.ID])])
	#---------------------------------------------------------	
	def getTitle(self):
		cmd = "select title from v_basic_person where i_id = %s"
		data = gmPG.run_ro_query('personalia', cmd, None, self.ID)
		if data is None:
			return ''
		if len(data) == 0:
			return ''
		return data[0][0]
	#--------------------------------------------------------
	def setTitle (self, title):
		cmd = "update v_basic_person set title = %s where i_id = %s"
		gmPG.run_commit ('personalia', [(cmd, [title, self.ID])])
	#--------------------------------------------------------
	def getID(self):
		return self.ID
	#--------------------------------------------------------
	def getDOB(self):
		# FIXME: invent a mechanism to set the desired format
		cmd = "select to_char(dob, 'DD.MM.YYYY') from identity where id = %s"
		data = gmPG.run_ro_query('personalia', cmd, None, self.ID)
		if data is None:
			return ''
		if len(data) == 0:
			return ''
		return data[0][0]
	#--------------------------------------------------------
	def setDOB (self, dob):
		cmd = "update identity set dob = %s where id = %s"
		gmPG.run_commit ('personalia', [(cmd, [dob, self.ID])])
	#--------------------------------------------------------
	def getAddress (self, type):
		cmd = """
select
	vba.addr_id,
	vba.number,
	vba.street,
	vba.city,
	vba.postcode
from
	v_basic_address vba,
	lnk_person2address lp2a,
	address_type at
where
	lp2a.id_address = vba.addr_id
	        and
	lp2a.id_type = at.id
	        and
	at.name = %s
		and
	lp2a.id_identity = %s
"""
		rows, idx = gmPG.run_ro_query('personalia', cmd, 1, type, self.ID)
		if rows is None:
			return None
		if len(rows) == 0:
			return None
		return [{
			'ID':r[idx['addr_id']],
			'number':r[idx['number']],
			'street':r[idx['street']],
			'urb':r[idx['city']],
			'postcode':r[idx['postcode']]
		} for r in rows]
	#--------------------------------------------------------
	def deleteAddress (self, ID):
		cmd = "delete from lnk_person2address where id_identity = %s and id_address = %s"
		gmPG.run_commit ('personalia', [(cmd, [self.ID, ID])])
		return 1
	#--------------------------------------------------------
	def newAddress (self, type, number, street, urb, postcode, state, country):
		"""Adds a new address into this persons list of addresses.
		"""
		cmd = """
select addr_id
from v_basic_address
where
	number = %s and
	street = %s and
	city = %s and
	postcode = %s and
	state = %s and
	country = %s
"""
		data = gmPG.run_ro_query ('personalia', cmd, None, number, street, urb, postcode, state, country)
		if data is None:
			_log.Log(gmLog.lErr, 'cannot check for address existence')
			return None
		# delete any pre-existing link on this identity and address type
		cmd = """
delete from lnk_person2address where id_identity = %s and id_type = (select id from address_type where name = %s)
"""
		gmPG.run_commit ('personalia', [(cmd, [self.ID, type])]) 
		# we have a matching address, just add the link
		if len(data) > 0:
			addr_id = data[0][0]
			cmd = """
insert into lnk_person2address (id_identity, id_address, id_type)
values (%s, %s, (select id from address_type where name = %s))
"""
			gmPG.run_commit ("personalia", [(cmd, (self.ID, addr_id, type))])
			return 1
		# insert a new address
		cmd1 = """
insert into v_basic_address (number, street, city, postcode, state, country)
values (%s, %s, %s, %s, %s, %s)
"""
		cmd2 = """
insert into lnk_person2address (id_identity, id_address, id_type)
values (%s, currval ('address_id_seq'), (select id from address_type where name = %s))
"""
		gmPG.run_commit ("personalia", [
			(cmd1, (number, street, urb, postcode, state, country)),
			(cmd2, (self.ID, type))
			]
		)
	#------------------------------------------------------------
	def getMedicalAge(self):
		cmd = "select dob from identity where id = %s"
		data = gmPG.run_ro_query('personalia', cmd, None, self.ID)

		if data is None:
			return '??'
		if len(data) == 0:
			return '??'
		return get_medical_age(data[0][0])
#------------------------------------------------------------
def getAddressTypes ():
	"""Gets a simple list of address types."""
	row_list = gmPG.run_ro_query('personalia', "select name from address_type")
	if row_list is None:
		return None
	if len(row_list) == 0:
		return None
	return [row[0] for row in row_list]

def getCommChannels ():
	"""Gets the list of comm channels"""
	row_list = gmPG.run_ro_query ('personalia', "select description from enum_comm_types")
	if row_list is None:
		return None
	if len (row_list) == 0:
		return None
	return [row[0] for row in row_list]
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
			myPatient = gmSQLPerson(aPKey = pID)
		except:
			_log.LogException('Unable to set up patient with ID [%s]' % pID, sys.exc_info())
			print "patient", pID, "can not be set up"
			continue
		print "ID       ", myPatient.getID ()
		print "name     ", myPatient.getActiveName ()
		print "title    ", myPatient.getTitle ()
		print "dob      ", myPatient.getDOB ()
		print "med age  ", myPatient.getMedicalAge ()
		print "adr types", getAddressTypes()
		for i in getAddressTypes ():
			print "adr (%s)" % i, myPatient.getAddress (i)
		print "--------------------------------------"
#		api = myPatient['API']
#		for call in api:
#			print "API call: %s (internally %s)" % (call['API call name'], call['internal name'])
#			print call['description']
#============================================================
# $Log: gmDemographics.py,v $
# Revision 1.1  2003-10-25 08:48:06  ihaywood
# Split from gmTmpPatient
#



# old gmTmpPatient log
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
