"""GnuMed demographics object.

This is a patient object intended to let a useful client-side
API crystallize from actual use in true XP fashion.

license: GPL
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/business/gmDemographicRecord.py,v $
# $Id: gmDemographicRecord.py,v 1.7 2003-11-20 02:10:50 sjtan Exp $
__version__ = "$Revision: 1.7 $"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>, I.Haywood"

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

import gmExceptions, gmPG, gmSignals, gmDispatcher, gmI18N, gmMatchProvider, gmPatient

# 3rd party
import mx.DateTime

#============================================================
gm2long_gender_map = {
	'm': _('male'),
	'f': _('female')
}
#============================================================
# virtual ancestor class, SQL and LDAP descendants
class gmDemographicRecord:
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

	def getGender(self):
		raise gmExceptions.PureVirtualFunction ()

	def setGender(self, gender):
		raise gmExceptions.PureVirtualFunction ()

	def getAddresses (self, type):
		raise gmExceptions.PureVirtualFunction ()

	def unlinkAddress (self, ID):
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
class gmDemographicRecord_SQL (gmDemographicRecord):
	"""Represents the demographic data of a patient.
	"""
	def __init__(self, aPKey = None):
		"""Fails if

		- no connection to database possible
		- patient referenced by aPKey does not exist
		"""
		self.ID = aPKey	# == identity.id == primary key
		if not self._pkey_exists():
			raise gmExceptions.ConstructorError, "no patient with ID [%s] in database" % aPKey

		self.PUPIC = ""
		self.__db_cache = {}

		# register backend notification interests ...
		#if not self._register_interests():
			#raise gmExceptions.ConstructorError, "Cannot register patient modification interests."

		_log.Log(gmLog.lData, 'instantiated demographic record for patient [%s]' % self.ID)
	#--------------------------------------------------------
	def cleanup(self):
		"""Do cleanups before dying.

		- note that this may be called in a thread
		"""
		_log.Log(gmLog.lData, 'cleaning up after patient [%s]' % self.ID)
		# FIXME: unlisten from signals etc.
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
	#--------------------------------------------------------
	# API
	#--------------------------------------------------------
	def getActiveName(self):
		cmd = "select firstnames, lastnames from v_basic_person where i_id = %s"
		data, idx = gmPG.run_ro_query('personalia', cmd, 1, self.ID)
		if data is None:
			return None
		if len(data) == 0:
			return {
				'first': '**?**',
				'last': '**?**'
			}
		return {
			'first': data[0][idx['firstnames']],
			'last': data[0][idx['lastnames']]
		}
	#--------------------------------------------------------
	def setActiveName (self, firstnames, lastnames):
		cmd = "update v_basic_person set firstnames = %s, lastnames = %s where i_id = %s"
		return gmPG.run_commit ('personalia', [(cmd, [firstnames, lastnames, self.ID])])
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
		return gmPG.run_commit ('personalia', [(cmd, [title, self.ID])])
	#--------------------------------------------------------
	def getID(self):
		return self.ID
	#--------------------------------------------------------
	def getDOB(self, aFormat = None):
		if aFormat is None:
			cmd = "select dob from identity where id=%s"
		else:
			cmd = "select to_char(dob, '%s') from identity where %s" % (aFormat, "id=%s")
		data = gmPG.run_ro_query('personalia', cmd, None, self.ID)		
		if data is None:
			if aFormat is None:
				return None
			return ''
		if len(data) == 0:
			if aFormat is None:
				return None
			return ''
		return data[0][0]
	#--------------------------------------------------------
	def setDOB (self, dob):
		cmd = "update identity set dob = %s where id = %s"
		return gmPG.run_commit ('personalia', [(cmd, [dob, self.ID])])
	#--------------------------------------------------------
	def get_relatives(self):
		cmd = """
select
	v.id, t.description , v.firstnames, v.lastnames, v.gender, v.dob
from
	v_basic_person v, relation_types t, lnk_person2relative l
where
	l.id_identity = %s and
	v.id = l.id_relative and
	t.id = l.id_relation_type
"""
		data, idx = gmPG.run_ro_query('personalia', cmd, 1, self.ID)
		if data is None:
			return []
		if len(data) == 0:
			return []
		return [{
			'id': r[idx['id']],
			'firstnames': r[idx['firstnames']],
			'lastnames': r[idx['lastnames']],
			'gender': r[idx['gender']],
			'dob': r[idx['dob']],
			'description': r[idx['description']]
			} for r in data ]
	#--------------------------------------------------------
	def link_new_relative(self, rel_type = 'parent'):
		# create new relative
		id_new_relative = gmPatient.create_dummy_identity()
		relative = gmPerson(id_new_relative)
		# pre-fill with data from ourselves
		relative_demographics = relative.get_demographic_record()
		relative_demographics.copyAddresses(self)
		relative_demographics.setActiveName( "?", self.getActiveName()['last'])
		# and link the two
		cmd = """
insert into lnk_person2relative (
	id_identity, id_relative, id_relation_type
) values (
	%s, %s, (select id from relation_types where description = %s)
)
"""
		success = gmPG.run_commit ("personalia", [(cmd, (id_new_relative, self.ID, rel_type))])
		if success:
			return id_new_relative
		return None
	#--------------------------------------------------------
	def getGender(self):
		cmd = "select gender from v_basic_person where i_id = %s"
		data = gmPG.run_ro_query('personalia', cmd, None, self.ID)
		if data is None:
			return ''
		if len(data) == 0:
			return ''
		return data[0][0]
	#--------------------------------------------------------
	def setGender(self, gender):
		gender = gender.lower()
		cmd = "update identity set gender = %s where id = %s"
		return gmPG.run_commit ('personalia', [(cmd, [gender, self.ID])])
	#--------------------------------------------------------
	def getAddresses(self, addr_type):
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
		rows, idx = gmPG.run_ro_query('personalia', cmd, 1, addr_type, self.ID)
		if rows is None:
			return None
		if len(rows) == 0:
			return None
		return [{
			'ID': r[idx['addr_id']],
			'number': r[idx['number']],
			'street': r[idx['street']],
			'urb': r[idx['city']],
			'postcode': r[idx['postcode']]
		} for r in rows]
	#--------------------------------------------------------
	def unlinkAddress (self, ID):
		cmd = "delete from lnk_person2address where id_identity = %s and id_address = %s"
		return gmPG.run_commit ('personalia', [(cmd, [self.ID, ID])])
	#--------------------------------------------------------
	def copyAddresses(self, a_demographic_record):
		addr_types = getAddressTypes()
		for addr_type in addr_types:
			addresses = a_demographic_record.getAddresses(addr_type)
			if addresses is None:
				continue
			for addr in addresses:
				self.linkNewAddress(addr_type, addr['number'], addr['street'], addr['urb'], addr['postcode'])
	#--------------------------------------------------------
	def linkNewAddress (self, addr_type, number, street, urb, postcode, state = None, country = None):
		"""Adds a new address into this persons list of addresses.
		"""
		if state is None:
			state, country = guess_state_country(urb, postcode)

		# address already in database ?
		cmd = """
select addr_id from v_basic_address
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
			s = " ".join( ( addr_type, number, street, urb, postcode, state, country ) )
			_log.Log(gmLog.lErr, 'cannot check for address existence (%s)' % s)
			return None

		# delete any pre-existing link for this identity and the given address type
		cmd = """
delete from lnk_person2address
where
	id_identity = %s
		and
	id_type = (select id from address_type where name = %s)
"""
		gmPG.run_commit ('personalia', [(cmd, [self.ID, addr_type])])

		# yes, address already there, just add the link
		if len(data) > 0:
			addr_id = data[0][0]
			cmd = """
insert into lnk_person2address (id_identity, id_address, id_type)
values (%s, %s, (select id from address_type where name = %s))
"""
			return gmPG.run_commit ("personalia", [(cmd, (self.ID, addr_id, addr_type))])

		# no, insert new address and link it, too
		cmd1 = """
insert into v_basic_address (number, street, city, postcode, state, country)
values (%s, %s, %s, %s, %s, %s)
"""
		cmd2 = """
insert into lnk_person2address (id_identity, id_address, id_type)
values (%s, currval ('address_id_seq'), (select id from address_type where name = %s))
"""
		return gmPG.run_commit ("personalia", [
			(cmd1, (number, street, urb, postcode, state, country)),
			(cmd2, (self.ID, addr_type))
			]
		)
	#------------------------------------------------------------
	def getMedicalAge(self):
		dob = self.getDOB()
		if dob is None:
			return '??'
		return get_medical_age(dob)
#================================================================
# convenience functions
#================================================================
def get_medical_age(dob):
	"""format patient age in a hopefully meaningful way"""

	age = mx.DateTime.Age(mx.DateTime.now(), dob)

	if age.years > 0:
		return "%sy%sm" % (age.years, age.months)
	try:
		if age.weeks > 4:
			return "%sm%sw" % (age.months, age.weeks)
		if age.weeks > 1:
			return "%sd" % age.days
	except:
		_log.LogException("age.weeks error", sys.exc_info())
	if age.days > 1:
		return "%sd (%sh)" % (age.days, age.hours)
	if age.hours > 3:
		return "%sh" % age.hours
	if age.hours > 0:
		return "%sh%sm" % (age.hours, age.minutes)
	if age.minutes > 5:
		return "%sm" % (age.minutes)
	return "%sm%ss" % (age.minutes, age.seconds)
#----------------------------------------------------------------
def getAddressTypes():
	"""Gets a simple list of address types."""
	row_list = gmPG.run_ro_query('personalia', "select name from address_type")
	if row_list is None:
		return None
	if len(row_list) == 0:
		return None
	return [row[0] for row in row_list]
#----------------------------------------------------------------
def getCommChannelTypes():
	"""Gets the list of comm channels"""
	row_list = gmPG.run_ro_query('personalia', "select description from enum_comm_types")
	if row_list is None:
		return None
	if len (row_list) == 0:
		return None
	return [row[0] for row in row_list]
#----------------------------------------------------------------
def guess_state_country( urb, postcode):
	"""parameters are urb.name, urb.postcode;
	   outputs are urb.id_state,  country.code"""

	cmd = """
select state.code, state.country
from urb, state
where
	lower(urb.name) = lower(%s) and
	upper(urb.postcode) = upper(%s) and
	urb.id_state = state.id
"""
	data = gmPG.run_ro_query ('personalia', cmd, None,  urb, postcode)
	if data is None:
		return "", ""
	if len(data) == 0:
		return '', ''
	return data[0]
#----------------------------------------------------------------
def getPostcodeForUrbId( urb_id):
	cmd = "select postcode from urb where id = %s"
	data = gmPG.run_ro_query ('personalia', cmd, None, urb_id)
	if data is None:
		return ""
	if len(data) == 0:
		return ''
	return data[0][0]
#----------------------------------------------------------------
class PostcodeMP (gmMatchProvider.cMatchProvider_SQL):
	"""Returns a list of valid postcodes,
	Accepts two contexts : "urb" and "street" being the **IDs** of urb and street
	"""
	def __init__ (self):
		# we search two tables here, as in some jurisdictions (UK, Germany, US)
		# postcodes are tied to streets or small groups of streets,
		# and in others (Australia) postcodes refer to an entire town
		source = [{
			'column':'postcode',
			'pk':'postcode',
			'limit':10,
			'table':'urb',
			'extra conditions':{'urb':'id = %s', 'default':'postcode is not null'}
			, 'service': 'demographica'
			},{
			'column':'postcode',
			'table':'street',
			'limit':10,
			'pk':'postcode',
			'extra conditions':{'urb':'id_urb = %s', 'street': 'id = %s', 'default':'postcode is not null'}
			, 'service': 'demographica'
			}]
		gmMatchProvider.cMatchProvider_SQL.__init__(self, source)
			
#----------------------------------------------------------------
class StreetMP (gmMatchProvider.cMatchProvider_SQL):
	"""Returns a list of streets

	accepts "urb" and "postcode" contexts
	"""
	def __init__ (self):
		source = [{
			'service': 'demographica',
			'table': 'street',
			'column': 'name',
			'limit': 10,
			'extra conditions': {
				'urb': 'id_urb = %s',
				'postcode': 'postcode = %s or postcode is null'
				}
			}]
		gmMatchProvider.cMatchProvider_SQL.__init__(self, source)
#------------------------------------------------------------
class MP_urb_by_zip (gmMatchProvider.cMatchProvider_SQL):
	"""Returns a list of urbs

	accepts "postcode" context
	"""
	def __init__ (self):
		source = [{
			'service': 'demographica',
			'table': 'urb',
			'column': 'name',
			'limit': 15,
			'extra conditions': {'postcode': '(postcode = %s or postcode is null)'}
			}]
		gmMatchProvider.cMatchProvider_SQL.__init__(self, source)
#------------------------------------------------------------
def get_time_tuple( faultyMxDateObject):
		list = [0,0,0,   0, 0, 0,   0, 0, 0]
		try:
			i = 0
			l = str(faultyMxDateObject).split(' ')[0].split('-')
			for x in l:
				list[i] = int(x)
				i += 1
		except:
			print "Failed to parse dob"
			_log.LogException("Failed to parse DOB", sys.exc_info(), verbose = 1)
		
		return list
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
			myPatient = gmDemographicRecord_SQL(aPKey = pID)
		except:
			_log.LogException('Unable to set up patient with ID [%s]' % pID, sys.exc_info())
			print "patient", pID, "can not be set up"
			continue
		print "ID       ", myPatient.getID ()
		print "name     ", myPatient.getActiveName ()
		print "title    ", myPatient.getTitle ()
		print "dob      ", myPatient.getDOB (aFormat = 'DD.MM.YYYY')
		print "med age  ", myPatient.getMedicalAge()
		adr_types = getAddressTypes()
		print "adr types", adr_types
		for type_name in adr_types:
			print "adr (%s)" % type_name, myPatient.getAddresses(type_name)
		print "--------------------------------------"
#============================================================
# $Log: gmDemographicRecord.py,v $
# Revision 1.7  2003-11-20 02:10:50  sjtan
#
# remove 'self' parameter from functions moved into global module namespace.
#
# Revision 1.6  2003/11/20 01:52:03  ncq
# - actually, make that **?** for good measure
#
# Revision 1.5  2003/11/20 01:50:52  ncq
# - return '?' for missing names in getActiveName()
#
# Revision 1.4  2003/11/18 16:44:24  ncq
# - getAddress -> getAddresses
# - can't verify mxDateTime bug with missing time tuple
# - remove getBirthYear, do getDOB() -> mxDateTime -> format
# - get_relative_list -> get_relatives
# - create_dummy_relative -> link_new_relative
# - cleanup
#
# Revision 1.3  2003/11/17 10:56:34  sjtan
#
# synced and commiting.
#
# Revision 1.2  2003/11/04 10:35:22  ihaywood
# match providers in gmDemographicRecord
#
# Revision 1.1  2003/11/03 23:59:55  ncq
# - renamed to avoid namespace pollution with plugin widget
#
# Revision 1.6  2003/10/31 23:21:20  ncq
# - remove old history
#
# Revision 1.5  2003/10/27 15:52:41  ncq
# - if aFormat is None in getDOB() return datetime object, else return formatted string
#
# Revision 1.4  2003/10/26 17:35:04  ncq
# - conceptual cleanup
# - IMHO, patient searching and database stub creation is OUTSIDE
#   THE SCOPE OF gmPerson and gmDemographicRecord
#
# Revision 1.3  2003/10/26 16:35:03  ncq
# - clean up as discussed with Ian, merge conflict resolution
#
# Revision 1.2  2003/10/26 11:27:10  ihaywood
# gmPatient is now the "patient stub", all demographics stuff in gmDemographics.
#
# Ergregious breakages are fixed, but needs more work
#
# Revision 1.1  2003/10/25 08:48:06  ihaywood
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
