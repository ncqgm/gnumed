"""GnuMed demographics object.

This is a patient object intended to let a useful client-side
API crystallize from actual use in true XP fashion.

license: GPL
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/business/gmDemographicRecord.py,v $
# $Id: gmDemographicRecord.py,v 1.47 2004-06-17 11:36:12 ihaywood Exp $
__version__ = "$Revision: 1.47 $"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>, I.Haywood"

# access our modules
import sys, os.path, time

from Gnumed.pycommon import gmLog, gmExceptions, gmPG, gmSignals, gmDispatcher, gmMatchProvider
from Gnumed.business import gmMedDoc
from Gnumed.pycommon.gmPyCompat import *

_log = gmLog.gmDefLog
if __name__ == '__main__':
	_log.SetAllLogLevels(gmLog.lData)
	from Gnumed.pycommon import gmI18N
_log.Log(gmLog.lData, __version__)

# 3rd party
import mx.DateTime as mxDT

#============================================================
# map gender abbreviations in a GnuMed demographic service
# to a meaningful localised string
map_gender_gm2long = {
	'm': _('male'),
	'f': _('female'),
	'tf': _('transsexual, female phenotype'),
	'tm': _('transsexual, male phenotype')
}
#============================================================
# virtual ancestor class, SQL and LDAP descendants
class cDemographicRecord:

	def addName (self, firstname, lastname, activate):
		raise gmExceptions.PureVirtualFunction ()

	def getTitle(self):
		raise gmExceptions.PureVirtualFunction ()

	def setDOB (self, dob):
		raise gmExceptions.PureVirtualFunction ()

	def getDOB(self):
		raise gmExceptions.PureVirtualFunction ()

	def getCOB ():
		raise gmExceptions.PureVirtualFunction ()

	def setCOB (self, cob):
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

	def linkNewAddress (self, addr_type, number, street, urb, postcode, state = None, country = None):
		raise gmExceptions.PureVirtualFunction ()

	def unlinkAddress (self, ID):
		raise gmExceptions.PureVirtualFunction ()

	def setAddress (self, type, number, street, urb, postcode, state, country):
		raise gmExceptions.PureVirtualFunction ()

	def getCommChannel (self, type):
		raise gmExceptions.PureVirtualFunction ()

	def linkCommChannel (self, type, comm):
		raise gmExceptions.PureVirtualFunction ()

	def getMedicalAge(self):
		raise gmExceptions.PureVirtualFunction ()

	def setOccupation(self, occupation):
		raise gmExceptions.PureVirtualFunction ()

	def getOccupation(self):
		raise gmExceptions.PureVirtualFunction ()


#============================================================
# may get preloaded by the waiting list
class cDemographicRecord_SQL(cDemographicRecord):
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
	def export_demographics (self, all = False):
		demographics_data = {}
		demographics_data['id'] = self.getID()
		demographics_data['names'] = []
		names = self.get_names(all)
		if all:
			for name in names:
				demographics_data['names'].append(name)
		else:
			demographics_data['names'].append(names)
		demographics_data['gender'] = self.getGender()
		demographics_data['title'] = self.getTitle()
		demographics_data['dob'] = self.getDOB (aFormat = 'DD.MM.YYYY')
		demographics_data['mage'] =  self.getMedicalAge()
		address_map = {}
		adr_types = getAddressTypes()
		# FIXME: rewrite using the list returned from getAddresses()
		for adr_type in adr_types:
			if not all and adr_type != "home":
				continue
			address_map[adr_type] = self.getAddresses(adr_type)
		demographics_data['addresses'] = address_map
		return demographics_data
	#--------------------------------------------------------
	def get_names(self, all=False):
		if all:
			cmd = """
				select n.firstnames, n.lastnames, i.title
				from names n, identity i
				where n.id_identity=%s and i.id=%s"""
		else:
			cmd = """
				select vbp.firstnames, vbp.lastnames, i.title
				from v_basic_person vbp, identity i
				where vbp.i_id=%s and i.id=%s"""
		rows, idx = gmPG.run_ro_query('personalia', cmd, 1, self.ID, self.ID)
		if rows is None:
			return None
		if len(rows) == 0:
			name = {'first': '**?**', 'last': '**?**', 'title': '**?**'}
			if all:
				return [name]
			return name
		if all:
			names = []
			for row in rows:
				names.append({'first': row[0], 'last': row[1], 'title': row[2]})
			return names
		else:
			return {'first': rows[0][0], 'last': rows[0][1], 'title': rows[0][2]}
	#--------------------------------------------------------
#	def getFullName (self):
#		cmd  = "select title, firstnames, lastnames from v_basic_person where i_id = %s"
#		r = gmPG.run_ro_query ('personalia', cmd, 0, self.ID)
#		if r:
#			return "%s %s %s" % (r[0][0], r[0][1], r[0][2])
#		else:
#			return _("Unknown")
	#--------------------------------------------------------
	def addName(self, firstname, lastname, activate = None):
		"""Add a name and possibly activate it."""
		cmd = "select add_name(%s, %s, %s, %s)"
		if activate:
			activate_str = 'true'
		else:
			activate_str = 'false'
		gmPG.run_commit ('personalia', [(cmd, [self.ID, firstname, lastname, activate_str])])
	#---------------------------------------------------------	
	def getTitle(self):
		cmd = "select title from v_basic_person where i_id = %s"
		data = gmPG.run_ro_query('personalia', cmd, None, self.ID)
		if data is None:
			return ''
		if len(data) == 0:
			return ''
		if data[0][0] == None:
			return ''
		return data[0][0]
	#--------------------------------------------------------
	def setTitle (self, title):
		cmd = "update identity set title=%s where id=%s"
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
	#---------------------------------------------------------------------
	def getCOB (self):
		cmd = "select country.name from country, identity where country.code = identity.cob and identity.id = %s"
		data = gmPG.run_ro_query ('personalia', cmd, None, self.ID)
		return data and data[0][0]
	#--------------------------------------------------------------------
	def setCOB (self, cob):
		cmd = "update identity set cob = country.code from country where identity.id = %s and country.name = %s"
		success, err_msg = gmPG.run_commit('personalia', [(cmd, [self.ID, cob])], return_err_msg=1)
		if not success:
			# user probably gave us invalid country
			msg = '%s (%s)' % ((_('invalid country [%s]') % cob), err_msg)
			print "invalid country!"
			raise gmExceptions.InvalidInputError (msg)
	#----------------------------------------------------------------------
	def getMaritalStatus (self):
		cmd = "select name from marital_status, identity where marital_status.id = identity.id_marital_status and identity.id = %s"
		data = gmPG.run_ro_query ('personalia', cmd, None, self.ID)
		return data and data[0][0]
	#--------------------------------------------------------------------
	def setMaritalStatus (self, cob):
		cmd = "update identity set id_marital_status = (select id from marital_status where name = %s) where id = %s"
		return gmPG.run_commit ('personalia', [(cmd, [cob, self.ID])])
	#---------------------------------------------------------------------
	def getOccupation (self):
		"""
		Currently we do not support more than one occupation
		"""
		cmd = "select o.name from occupation o, lnk_job2person lj2p where o.id = lj2p.id_occupation and lj2p.id_identity = %s"
		data = gmPG.run_ro_query ('personalia', cmd, None, self.ID)
		return data and data[0][0]
	#--------------------------------------------------------------------
	def setOccupation (self, occupation):
		# does occupation already exist ?
		cmd = "select o.id from occupation o where o.name = %s"
		data = gmPG.run_ro_query ('personalia', cmd, None, occupation)
		# error
		if data is None:
			gmLog.gmDefLog.Log(gmLog.lErr, 'cannnot check for occupation')
			return None
		# none found
		if len(data) == 0:
			cmd1 = "insert into occupation (name) values (%s)"
			cmd2 = "select currval('occupation_id_seq')"
			data = gmPG.run_commit ('personalia', [
				(cmd1, [occupation]),
				(cmd2, [])
			])
			if (data is None) or (len(data) == 0):
				_log.Log(gmLog.lErr, 'cannot add occupation details')
				return None

		id_occupation = data[0][0]
		# delete pre-existing link as required
		cmd1 = """
		delete from
			lnk_job2person
		where
			id_identity = %s"""
		# creating new link
		cmd2 = """insert into lnk_job2person (id_identity, id_occupation) values (%s, %s)"""
		return gmPG.run_commit ('personalia', [
			(cmd1, [self.ID]),
			(cmd2, [self.ID, id_occupation])
		])
	#----------------------------------------------------------------------
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
		from Gnumed.business.gmPatient import create_dummy_identity
		# create new relative
		id_new_relative = create_dummy_identity()
		relative = gmPerson(id_new_relative)
		# pre-fill with data from ourselves
		relative_demographics = relative.get_demographic_record()
		relative_demographics.copyAddresses(self)
		relative_demographics.addName( '**?**', self.get_names()['last'], activate = 1)
		# and link the two
		cmd = """
			insert into lnk_person2relative (
				id_identity, id_relative, id_relation_type
			) values (
				%s, %s, (select id from relation_types where description = %s)
			)"""
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
	def getAddresses(self, addr_type = None, firstonly = 0):
		"""Return a patient's addresses. 
			addr_type is the address_type.name, not address_type.id

		- return all types if addr_type is None
		"""
		vals = {'pat_id': self.ID}
		if addr_type is None:
			addr_where = ''
		else:
			addr_where = 'and at.name = %(addr_type)s'
			vals['addr_type'] = addr_type
		if firstonly:
			limit = ' limit 1'
		else:
			limit = ''
		cmd = """select
				vba.addr_id,
				vba.number,
				vba.street,
				vba.city,
				vba.postcode,
				at.name
			from
				v_basic_address vba,
				lnk_person_org_address lpoa,
				address_type at
			where
				lpoa.id_address = vba.addr_id
				and lpoa.id_type = at.id
				and lpoa.id_identity = %%(pat_id)s
				%s %s""" % (addr_where, limit)
		rows, idx = gmPG.run_ro_query('personalia', cmd, 1, vals)
		if rows is None:
			return []
		if len(rows) == 0:
			return []
		ret = [{
			'ID': r[idx['addr_id']],
			'number': r[idx['number']],
			'street': r[idx['street']],
			'urb': r[idx['city']],
			'postcode': r[idx['postcode']],
			'type': r[idx['name']]
		} for r in rows]
		if firstonly:
			return ret[0]
		else:
			return ret
	#--------------------------------------------------------
	def unlinkAddress (self, ID):
		cmd = "delete from lnk_person_org_address where id_identity = %s and id_address = %s"
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
			delete from lnk_person_org_address
			where
				id_identity = %s and
				id_type = (select id from address_type where name = %s)
			"""
		gmPG.run_commit ('personalia', [(cmd, [self.ID, addr_type])])

		# yes, address already there, just add the link
		if len(data) > 0:
			addr_id = data[0][0]
			cmd = """
				insert into lnk_person_org_address (id_identity, id_address, id_type)
				values (%s, %s, (select id from address_type where name = %s))
				"""
			return gmPG.run_commit ("personalia", [(cmd, (self.ID, addr_id, addr_type))])

		# no, insert new address and link it, too
		cmd1 = """
			insert into v_basic_address (number, street, city, postcode, state, country)
			values (%s, %s, %s, %s, %s, %s)
			"""
		cmd2 = """
			insert into lnk_person_org_address (id_identity, id_address, id_type)
			values (%s, currval ('address_id_seq'), (select id from address_type where name = %s))
			"""
		return gmPG.run_commit ("personalia", [
			(cmd1, (number, street, urb, postcode, state, country)),
			(cmd2, (self.ID, addr_type))
			]
		)
	#------------------------------------------------------------
	# FIXME: should we support named channel types, too ?
	def linkCommChannel (self, channel_type, url):
		"""Links a comm channel with a patient. Adds it first if needed.

		(phone no., email, etc.).
		channel_type is an ID as returned from getCommChannelTypeID()
		"""	
		# does channel already exist ?
		cmd = "select cc.id from comm_channel cc where cc.id_type = %s and cc.url = %s"
		data = gmPG.run_ro_query ('personalia', cmd, None, channel_type, url)
		# error
		if data is None:
			_log(gmLog.lErr, 'cannnot check for comm channel details')
			return None
		# none found
		if len(data) == 0:
			cmd1 = "insert into comm_channel (id_type, url) values (%s, %s)"
			cmd2 = "select currval('comm_channel_id_seq')"
			data = gmPG.run_commit ('personalia', [
				(cmd1, [channel_type, url]),
				(cmd2, [])
			])
			if (data is None) or (len(data) == 0):
				_log.Log(gmLog.lErr, 'cannot add communication channel details')
				return None

		id_channel = data[0][0]
		# delete pre-existing link as required
		cmd1 = """
		delete from
			lnk_identity2comm_chan
		where
			id_identity = %s
				and
			exists(
				select 1
				from comm_channel cc
				where cc.id_type = %s and cc.id = id_comm)"""
		# creating new link
		cmd2 = """insert into lnk_identity2comm_chan (id_identity, id_comm) values (%s, %s)"""
		return gmPG.run_commit ('personalia', [
			(cmd1, [self.ID, channel_type]),
			(cmd2, [self.ID, id_channel])
		])
	#-------------------------------------------------------------
	def getCommChannel (self, channel=None):
		"""
		Gets the comm channel url, given its type ID
		If ID default, a mapping of all IDs and urls
		"""
		if channel:
			data = gmPG.run_ro_query ('personalia', """
			select cc.url from comm_channel cc, lnk_identity2comm_chan lp2cc where
			cc.id_type = %s and lp2cc.id_identity = %s and lp2cc.id_comm = cc.id
			""", None, channel, self.ID)
			return data and data[0][0]
		else:
			data = gmPG.run_ro_query ('personalia', """
			select cc.id_type, cc.url
			from
			comm_channel cc,
			lnk_identity2comm_chan lp2cc
			where
			cc.id = lp2cc.id_comm and lp2cc.id_identity = %s
			""", None, self.ID)
			return dict(rows)
	#----------------------------------------------------------------------
	def getMedicalAge(self):
		dob = self.getDOB()
		if dob is None:
			return '??'
		return dob2medical_age(dob)
	#----------------------------------------------------------------------
	def addExternalID(self, external_id = None, origin = 'DEFAULT', comment = None):
		# FIXME: should we support named origins, too ?
		if external_id is None:
			_log.Log(gmLog.lErr, 'must have external ID to add it')
			return None
		args = {
			'ID': self.ID,
			'ext_ID': external_id,
			'origin': origin,
			'comment': comment,
			}
		if comment:
			cmd1 = 'insert into lnk_identity2ext_id (id_identity, external_id, fk_origin, comment) values (%(ID)s, %(ext_ID)s, %(origin)s, %(comment)s)'
		else:
			cmd1 = 'insert into lnk_identity2ext_id (id_identity, external_id, fk_origin) values (%(ID)s, %(ext_ID)s, %(origin)s)'
		cmd2 = "select currval('lnk_identity2ext_id_id_seq')"
		result = gmPG.run_commit('personalia', [
			(cmd1, [args]),
			(cmd2, [])
		])
		if result is None:
			_log.Log(gmLog.lErr, 'cannot link external ID [%s@%s] (%s)' % (external_id, origin, comment))
			return None
		return result[0][0]
	#------------------------------------------------------------
	def removeExternalID(self, pk_external_ID):
		cmd = 'delete from lnk_identity2ext_id where id=%s'
		return gmPG.run_commit('personalia', [(cmd, [pk_external_ID])])
	#---------------------------------------------------------------
	def listExternalIDs (self):
		"""
		Returns a list of dictionaries of external IDs
		Fields:
		- id [the key used to delete ext. IDs
		- origin [the origin code as returned by getExternalIDTypes]
		- comment [a user comment]
		- external_id [the actual external ID]
		"""
		cmd = "select id, fk_origin, comment, external_id from lnk_identity2ext_id where id_identity = %s"
		rows = gmPG.run_ro_query ('personalia', cmd, None, self.ID)
		if rows is None:
			return []
		return [{'id':row[0], 'origin':row[1], 'comment':row[2], 'external_id':row[3]} for row in rows]
	#----------------------------------------------------------------
#================================================================
# convenience functions
#================================================================
def dob2medical_age(dob):
	"""format patient age in a hopefully meaningful way"""

	age = mxDT.Age(mxDT.now(), dob)

	if age.years > 0:
		return "%sy%sm" % (age.years, age.months)
	weeks = age.days / 7
	if weeks > 4:
		return "%sm%sw" % (age.months, age.weeks)
	if weeks > 1:
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
#----------------------------------------------------------------
def getAddressTypes():
	"""Gets a simple list of address types."""
	row_list = gmPG.run_ro_query('personalia', "select name from address_type")
	if row_list is None:
		return []
	if len(row_list) == 0:
		return []
	return [row[0] for row in row_list]
#----------------------------------------------------------------
def getMaritalStatusTypes():
	"""Gets a simple list of types of marital status."""
	row_list = gmPG.run_ro_query('personalia', "select name from marital_status")
	if row_list is None:
		return []
	if len(row_list) == 0:
		return []
	return [row[0] for row in row_list]
#------------------------------------------------------------------
def getExtIDTypes (context = 'p'):
	"""Gets list of [code, ID type] from the backend for the given context
	"""
	# FIXME: error handling
	rl = gmPG.run_ro_query('personalia', "select pk, name from enum_ext_id_types where context = %s", None, context)
	if rl is None:
		return []
	return rl
#----------------------------------------------------------------
def getCommChannelTypes():
	"""Gets the dictionary of ID->comm channels"""
	row_list = gmPG.run_ro_query('personalia', "select id, description from enum_comm_types")
	if row_list is None:
		return None
	if len (row_list) == 0:
		return None
	return dict(row_list)

EMAIL=1
FAX=2
HOME_PHONE=3
WORK_PHONE=4
WEB=5
MOBILE=6
JABBER=7
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
def getPostcodeForUrbId(urb_id):
	# FIXME: get from views
	cmd = "select postcode from urb where id = %s"
	data = gmPG.run_ro_query ('personalia', cmd, None, urb_id)
	if data is None:
		_log.Log(gmLog.lErr, 'cannot get postcode for urb [%s]' % urb_id)
		return None
	if len(data) == 0:
		return ''
	return data[0][0]
#----------------------------------------------------------------
def getUrbsForPostcode(pcode=None):
	cmd = "select name from urb where postcode=%s"
	data = gmPG.run_ro_query('personalia', cmd, None, pcode)
	if data is None:
		_log.Log(gmLog.lErr, 'cannot get urbs from postcode [%s]' % pcode)
		return None
	if len(data) == 0:
		return []
	return [x[0] for x in data]
#----------------------------------------------------------------
class PostcodeMP (gmMatchProvider.cMatchProvider_SQL):
	"""Returns a list of valid postcodes,
	Accepts two contexts : "urb" and "street" being the **IDs** of urb and street
	"""
	def __init__ (self):
		# we search two tables here, as in some jurisdictions (UK, Germany, US)
		# postcodes are tied to streets or small groups of streets,
		# and in others (Australia) postcodes refer to an entire town

		# reviewers' comments:
		# - pk this will be the data return to the id_callback() function passed 
		#   as  gmPhrasewheel.__init__ last parameter , so the event data  will be 
		#   the postcode for urb or street , not the id of those tables.
		#   This is in the cMatchProvider.__findMatches code.

		source = [{
			'column':'postcode',
			'pk':'postcode',
			'limit':10,
			'table':'urb',
			'extra conditions':{'urb':'id = %s', 'default':'postcode is not null'}
			, 'service': 'personalia'
			},{
			'column':'postcode',
			'table':'street',
			'limit':10,
			'pk':'postcode',
			'extra conditions':{'urb':'id_urb = %s', 'street': 'id = %s', 'default':'postcode is not null'}
			, 'service': 'personalia'
			}]
		gmMatchProvider.cMatchProvider_SQL.__init__(self, source)
			
#----------------------------------------------------------------
class StreetMP (gmMatchProvider.cMatchProvider_SQL):
	"""Returns a list of streets

	accepts "urb" and "postcode" contexts  
		e.g.
			using cMatchProvider_SQL's  self.setContext("urb",...) 
					
	"""
	def __init__ (self):
		source = [{
			'service': 'personlia',
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
			'service': 'personalia',
			'table': 'urb',
			'column': 'name',
			'limit': 15,
			'extra conditions': {'postcode': '(postcode = %s or postcode is null)'}
			}]
		gmMatchProvider.cMatchProvider_SQL.__init__(self, source)

class CountryMP (gmMatchProvider.cMatchProvider_SQL):
	"""
	Returns a list of countries
	"""
	def __init__ (self):
		source = [{
			'service':'personalia',
			'table':'country',
			'pk':'code',
			'column':'name',
			'limit':5
			}]
		gmMatchProvider.cMatchProvider_SQL.__init__ (self, source)

class OccupationMP (gmMatchProvider.cMatchProvider_SQL):
	"""
	Returns a list of occupations
	"""
	def __init__ (self):
		source = [{
			'service':'personalia',
			'table':'occupation',
			'pk':'id',
			'column':'name',
			'limit':7
			}]
		gmMatchProvider.cMatchProvider_SQL.__init__ (self, source)

class NameMP (gmMatchProvider.cMatchProvider_SQL):
	"""
	List of names
	"""
	def __init__ (self):
		source =[{
			'service':'personalia',
			'table':'names',
			'pk':'id_identity',
			'column':'lastnames',
			'result':"lastnames || ', ' || firstnames",
			'limit':5,
			'extra conditions':{'occupation':'exists (select 1 from lnk_job2person where id_occupation = %s and lnk_job2person.id_identity = names.id_identity)'}
			}]
		gmMatchProvider.cMatchProvider_SQL.__init__ (self, source)

#------------------------------------------------------------
class OrgCategoryMP (gmMatchProvider.cMatchProvider_SQL):
	"""
	List of org categories.
	"""
	def __init__(self):
		source = [ {
			'service': 'personalia',
			'table'	: 'org_category',
			'pk'	: 'id',
			'column': 'description',
			'result': 'description' ,
			'limit' : 5,
			}]
		gmMatchProvider.cMatchProvider_SQL.__init__(self, source)
#------------------------------------------------------------


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
			myPatient = cDemographicRecord_SQL(aPKey = pID)
		except:
			_log.LogException('Unable to set up patient with ID [%s]' % pID, sys.exc_info())
			print "patient", pID, "can not be set up"
			continue
		print "ID       ", myPatient.getID ()
		print "name     ", myPatient.get_names (1)
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
# Revision 1.47  2004-06-17 11:36:12  ihaywood
# Changes to the forms layer.
# Now forms can have arbitrary Python expressions embedded in @..@ markup.
# A proper forms HOWTO will appear in the wiki soon
#
# Revision 1.46  2004/05/30 03:50:41  sjtan
#
# gmContacts can create/update org, one level of sub-org, org persons, sub-org persons.
# pre-alpha or alpha ? Needs cache tune-up .
#
# Revision 1.45  2004/05/29 12:03:47  sjtan
#
# OrgCategoryMP for gmContact's category field
#
# Revision 1.44  2004/05/28 15:05:10  sjtan
#
# utility functions only called with exactly 2 args in order to fulfill function intent, but do some checking for invalid args.
#
# Revision 1.43  2004/05/26 12:58:14  ncq
# - cleanup, error handling
#
# Revision 1.42  2004/05/25 16:18:13  sjtan
#
# move methods for postcode -> urb interaction to gmDemographics so gmContacts can use it.
#
# Revision 1.41  2004/05/25 16:00:34  sjtan
#
# move common urb/postcode collaboration  to business class.
#
# Revision 1.40  2004/05/19 11:16:08  sjtan
#
# allow selecting the postcode for restricting the urb's picklist, and resetting
# the postcode for unrestricting the urb picklist.
#
# Revision 1.39  2004/04/15 09:46:56  ncq
# - cleanup, get_lab_data -> get_lab_results
#
# Revision 1.38  2004/04/11 10:15:56  ncq
# - load title in get_names() and use it superceding getFullName
#
# Revision 1.37  2004/04/10 01:48:31  ihaywood
# can generate referral letters, output to xdvi at present
#
# Revision 1.36  2004/04/07 18:43:47  ncq
# - more gender mappings
# - *comm_channel -> comm_chan
#
# Revision 1.35  2004/03/27 04:37:01  ihaywood
# lnk_person2address now lnk_person_org_address
# sundry bugfixes
#
# Revision 1.34  2004/03/25 11:01:45  ncq
# - getActiveName -> get_names(all=false)
# - export_demographics()
#
# Revision 1.33  2004/03/20 19:43:16  ncq
# - do import gmI18N, we need it
# - gm2long_gender_map -> map_gender_gm2long
# - gmDemo* -> cDemo*
#
# Revision 1.32  2004/03/20 17:53:15  ncq
# - cleanup
#
# Revision 1.31  2004/03/15 15:35:45  ncq
# - optimize getCommChannel() a bit
#
# Revision 1.30  2004/03/10 12:56:01  ihaywood
# fixed sudden loss of main.shadow
# more work on referrals,
#
# Revision 1.29  2004/03/10 00:09:51  ncq
# - cleanup imports
#
# Revision 1.28  2004/03/09 07:34:51  ihaywood
# reactivating plugins
#
# Revision 1.27  2004/03/04 10:41:21  ncq
# - comments, cleanup, adapt to minor schema changes
#
# Revision 1.26  2004/03/03 23:53:22  ihaywood
# GUI now supports external IDs,
# Demographics GUI now ALPHA (feature-complete w.r.t. version 1.0)
# but happy to consider cosmetic changes
#
# Revision 1.25  2004/03/03 05:24:01  ihaywood
# patient photograph support
#
# Revision 1.24  2004/03/02 10:21:09  ihaywood
# gmDemographics now supports comm channels, occupation,
# country of birth and martial status
#
# Revision 1.23  2004/02/26 17:19:59  ncq
# - setCommChannel: arg channel -> channel_type
# - setCommChannel: we need to read currval() within
#   the same transaction as the insert to get consistent
#   results
#
# Revision 1.22  2004/02/26 02:12:00  ihaywood
# comm channel methods
#
# Revision 1.21  2004/02/25 09:46:20  ncq
# - import from pycommon now, not python-common
#
# Revision 1.20  2004/02/18 15:26:39  ncq
# - fix dob2medical_age()
#
# Revision 1.19  2004/02/18 06:36:04  ihaywood
# bugfixes
#
# Revision 1.18  2004/02/17 10:30:14  ncq
# - enhance GetAddresses() to return all types if addr_type is None
#
# Revision 1.17  2004/02/17 04:04:34  ihaywood
# fixed patient creation refeential integrity error
#
# Revision 1.16  2004/02/14 00:37:10  ihaywood
# Bugfixes
# 	- weeks = days / 7
# 	- create_new_patient to maintain xlnk_identity in historica
#
# Revision 1.15  2003/12/01 01:01:41  ncq
# - get_medical_age -> dob2medical_age
#
# Revision 1.14  2003/11/30 01:06:21  ncq
# - add/remove_external_id()
#
# Revision 1.13  2003/11/23 23:32:01  ncq
# - some cleanup
# - setTitle now works on identity instead of names
#
# Revision 1.12  2003/11/23 14:02:40  sjtan
#
# by setting active=false first, then updating values, side effects from triggers can be avoided; see also
# F_active_name trigger function in server sql script,which fires only if new.active = true .
#
# Revision 1.11  2003/11/22 14:44:17  ncq
# - setTitle now only operates on active names and also doesn't set the name
#   to active which would trigger the trigger
#
# Revision 1.10  2003/11/22 14:40:59  ncq
# - setActiveName -> addName
#
# Revision 1.9  2003/11/22 12:53:48  sjtan
#
# modified the setActiveName and setTitle so it works as intended in the face of insurmountable triggers ;)
#
# Revision 1.8  2003/11/20 07:45:45  ncq
# - update names/identity, not v_basic_person in setTitle et al
#
# Revision 1.7  2003/11/20 02:10:50  sjtan
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
