"""GNUmed demographics object.

This is a patient object intended to let a useful client-side
API crystallize from actual use in true XP fashion.

license: GPL
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/business/gmDemographicRecord.py,v $
# $Id: gmDemographicRecord.py,v 1.96 2008-02-26 16:24:49 ncq Exp $
__version__ = "$Revision: 1.96 $"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>, I.Haywood <ihaywood@gnu.org>"

# stdlib
import sys, os.path, time, string, logging


# 3rd party
import mx.DateTime as mxDT


# GNUmed
if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmDispatcher, gmBusinessDBObject, gmPG2, gmTools
from Gnumed.business import gmMedDoc


_log = logging.getLogger('gm.business')
_log.info(__version__)
#============================================================
# address related classes
#------------------------------------------------------------
class cAddress(gmBusinessDBObject.cBusinessDBObject):
	"""A class representing an address as an entity in itself.

	We consider addresses to be self-complete "labels" for locations.
	It does not depend on any people potentially living there. Thus
	an address can get attached to as many people as we want to
	signify that that is their place of residence/work/...

	This class acts on the address as an entity. Therefore it can
	modify the address fields. Think carefully about *modifying*
	addresses attached to people, though. Most times when you think
	person.modify_address() what you *really* want is as sequence of
	person.unlink_address(old) and person.link_address(new).

	Modifying an address may or may not be the proper thing to do as
	it will transparently modify the address for *all* the people to
	whom it is attached. In many cases you will want to create a *new*
	address and link it to a person instead of the old address.
	"""
	_cmd_fetch_payload = u"select * from dem.v_address where pk_address=%s"
	_cmds_store_payload = [
		u"""update dem.address set
				aux_street = %(notes_street)s,
				subunit = %(subunit)s,
				addendum = %(notes_subunit)s,
				lat_lon = %(lat_lon_street)s
			where id=%(pk_address)s and xmin=%(xmin_address)s""",
		u"select xmin as xmin_address from dem.address where id=%(pk_address)s"
	]
	_updatable_fields = ['notes_street', 'subunit', 'notes_subunit', 'lat_lon_address']
#------------------------------------------------------------
def address_exists(country=None, state=None, urb=None, suburb=None, postcode=None, street=None, number=None, subunit=None, notes_street=None, notes_subunit=None):

	where_parts = [u"""
		code_country = %(country)s and
		code_state = %(state)s and
		urb = %(urb)s and
		postcode = %(postcode)s and
		street = %(street)s and
		number = %(number)s"""
	]

	if suburb is None:
		where_parts.append(u"suburb is %(suburb)s")
	else:
		where_parts.append(u"suburb = %(suburb)s")

	if notes_street is None:
		where_parts.append(u"notes_street is %(notes_street)s")
	else:
		where_parts.append(u"notes_street = %(notes_street)s")

	if subunit is None:
		where_parts.append(u"subunit is %(subunit)s")
	else:
		where_parts.append(u"subunit = %(subunit)s")

	if notes_subunit is None:
		where_parts.append(u"notes_subunit is %(notes_subunit)s")
	else:
		where_parts.append(u"notes_subunit = %(notes_subunit)s")

	cmd = u"select pk_address from dem.v_address where %s" % u" and ".join(where_parts)
	data = {
		'country': country,
		'state': state,
		'urb': urb,
		'suburb': suburb,
		'postcode': postcode,
		'street': street,
		'notes_street': notes_street,
		'number': number,
		'subunit': subunit,
		'notes_subunit': notes_subunit
	}

	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': data}])

	if len(rows) == 0:
		return None
	return rows[0][0]
#------------------------------------------------------------
def create_address(country=None, state=None, urb=None, suburb=None, postcode=None, street=None, number=None, subunit=None):

	if suburb is not None:
		suburb = gmTools.none_if(suburb.strip(), u'')

	pk_address = address_exists (
		country = country,
		state = state,
		urb = urb,
		suburb = suburb,
		postcode = postcode,
		street = street,
		number = number,
		subunit = subunit
	)
	if pk_address is not None:
		return cAddress(aPK_obj=pk_address)

	cmd = u"""
		select dem.create_address (
			%(number)s,
			%(street)s,
			%(postcode)s,
			%(urb)s,
			%(state)s,
			%(country)s,
			%(subunit)s
		)"""
	args = {
		'number': number,
		'street': street,
		'postcode': postcode,
		'urb': urb,
		'state': state,
		'country': country,
		'subunit': subunit
	}
	queries = [{'cmd': cmd, 'args': args}]

	rows, idx = gmPG2.run_rw_queries(queries = queries, return_data = True)
	adr = cAddress(aPK_obj=rows[0][0])

	if suburb is not None:
		queries = [{
			# CAVE: suburb will be ignored if there already is one
			'cmd': u"update dem.street set suburb = %(suburb)s where id=%(pk_street)s and suburb is Null",
			'args': {'suburb': suburb, 'pk_street': adr['pk_street']}
		}]
		rows, idx = gmPG2.run_rw_queries(queries = queries)

	return adr
#------------------------------------------------------------
def delete_address(address=None):
	cmd = u"delete from dem.address where id=%s"
	rows, idx = gmPG2.run_rw_queries(queries=[{'cmd': cmd, 'args': [address['pk_address']]}])
	return True
#===================================================================
class cPatientAddress(gmBusinessDBObject.cBusinessDBObject):

	_cmd_fetch_payload = u"select * from dem.v_pat_addresses where pk_address=%s"
	_cmds_store_payload = [
		u"""update dem.lnk_person_org_address set id_type=%(pk_address_type)s
			where id=%(pk_lnk_person_org_address)s and xmin=%(xmin_lnk_person_org_address)s""",
		u"""select xmin from dem.lnk_person_org_address where id=%(pk_lnk_person_org_address)s"""
	]
	_updatable_fields = ['pk_address_type']
	#---------------------------------------------------------------
	def get_identities(self, same_lastname=False):
		pass
#===================================================================
# communication channels API
#-------------------------------------------------------------------
class cCommChannel(gmBusinessDBObject.cBusinessDBObject):

	_cmd_fetch_payload = u"select * from dem.v_person_comms where pk_lnk_identity2comm = %s"
	_cmds_store_payload = [
		u"""update dem.lnk_identity2comm set
				fk_address = %(pk_address)s,
				fk_type = dem.create_comm_type(%(comm_type)s),
				url = %(url)s,
				is_confidential = %(is_confidential)s
			where pk = %(pk_lnk_identity2comm)s and xmin = %(xmin_lnk_identity2comm)s
		""",
		u"select xmin as xmin_lnk_identity2comm from dem.lnk_identity2comm where pk = %(pk_lnk_identity2comm)s"
	]
	_updatable_fields = ['pk_address', 'url', 'comm_type', 'is_confidential']
#-------------------------------------------------------------------
def create_comm_channel(comm_medium=None, url=None, is_confidential=False, pk_channel_type=None, pk_identity=None):
	"""Create a communications channel for a patient."""

	# FIXME: create comm type if necessary
	args = {'pat': pk_identity, 'url': url, 'secret': is_confidential}

	if pk_channel_type is None:
		args['type'] = comm_medium
		cmd = u"""insert into dem.lnk_identity2comm (
			fk_identity,
			url,
			fk_type,
			is_confidential
		) values (
			%(pat)s,
			%(url)s,
			dem.create_comm_type(%(type)s),
			%(secret)s
		)"""
	else:
		args['type'] = pk_channel_type
		cmd = u"""insert into dem.lnk_identity2comm (
			fk_identity,
			url,
			fk_type,
			is_confidential
		) values (
			%(pat)s,
			%(url)s,
			%(type)s,
			%(secret)s
		)"""

	rows, idx = gmPG2.run_rw_queries (
		queries = [
			{'cmd': cmd, 'args': args},
			{'cmd': u"select * from dem.v_person_comms where pk_lnk_identity2comm = currval(pg_get_serial_sequence('dem.lnk_identity2comm', 'pk'))"}
		],
		return_data = True,
		get_col_idx = True
	)

	return cCommChannel(row = {'pk_field': 'pk_lnk_identity2comm', 'data': rows[0], 'idx': idx})
#-------------------------------------------------------------------
def delete_comm_channel(pk=None, pk_patient=None):
	cmd = u"delete from dem.lnk_identity2comm where pk = %(pk)s and fk_identity = %(pat)s"
	args = {'pk': pk, 'pat': pk_patient}
	gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])
#-------------------------------------------------------------------
__comm_channel_types = None

def get_comm_channel_types():
	global __comm_channel_types
	if __comm_channel_types is None:
		cmd = u"select pk, _(description) from dem.enum_comm_types"
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd}])
		__comm_channel_types = rows
	return __comm_channel_types
#-------------------------------------------------------------------

#===================================================================
class cOrg (gmBusinessDBObject.cBusinessDBObject):
	"""
	Organisations

	This is also the common ancestor of cIdentity, self._table is used to
	hide the difference.
	The aim is to be able to sanely write code which doesn't care whether
	its talking to an organisation or an individual"""
	_table = "org"

	_cmd_fetch_payload = "select *, xmin from dem.org where id=%s"
	_cmds_lock_rows_for_update = ["select 1 from dem.org where id=%(id)s and xmin=%(xmin)s"]
	_cmds_store_payload = [
		"""update dem.org set
			description=%(description)s,
			id_category=(select id from dem.org_category where description=%(occupation)s)
		where id=%(id)s""",
		"select xmin from dem.org where id=%(id)s"
	]
	_updatable_fields = ["description", "occupation"]
	_service = 'personalia'
	#------------------------------------------------------------------
	def cleanup (self):
		pass
	#------------------------------------------------------------------
	def export_demographics (self):
		if not self.__cache.has_key ('addresses'):
			self['addresses']
		if not self.__cache.has_key ('comms'):
			self['comms']
		return self.__cache
	#--------------------------------------------------------------------
	def get_members (self):
		"""
		Returns a list of (address dict, cIdentity) tuples 
		"""
		cmd = """select
				vba.id,
				vba.number,
				vba.addendum, 
				vba.street,
				vba.urb,
				vba.postcode,
				at.name,
				lpoa.id_type,
				vbp.pk_identity,
				title,
				firstnames,
				lastnames,
				dob,
				cob,
				gender,
				pupic,
				pk_marital_status,
				marital_status,
				karyotype,
				xmin_identity,
				preferred
			from
				dem.v_basic_address vba,
				dem.lnk_person_org_address lpoa,
				dem.address_type at,
				dem.v_basic_person vbp
			where
				lpoa.id_address = vba.id
				and lpoa.id_type = at.id
				and lpoa.id_identity = vbp.pk_identity
				and lpoa.id_org = %%s
				"""

		rows, idx = gmPG.run_ro_query('personalia', cmd, 1, self.getId ())
		if rows is None:
			return []
		elif len(rows) == 0:
			return []
		else:
			return [({'pk':i[0], 'number':i[1], 'addendum':i[2], 'street':i[3], 'city':i[4], 'postcode':i[5], 'type':i[6], 'id_type':i[7]}, cIdentity (row = {'data':i[8:], 'id':idx[8:], 'pk_field':'id'})) for i in rows]	
	#------------------------------------------------------------
	def set_member (self, person, address):
		"""
		Binds a person to this organisation at this address.
		person is a cIdentity object
		address is a dict of {'number', 'street', 'addendum', 'city', 'postcode', 'type'}
		type is one of the IDs returned by getAddressTypes
		"""
		cmd = "insert into dem.lnk_person_org_address (id_type, id_address, id_org, id_identity) values (%(type)s, dem.create_address (%(number)s, %(addendum)s, %(street)s, %(city)s, %(postcode)s), %(org_id)s, %(pk_identity)s)"
		address['pk_identity'] = person['pk_identity']
		address['org_id'] = self.getId()
		if not id_addr:
			return (False, None)
		return gmPG.run_commit2 ('personalia', [(cmd, [address])])
	#------------------------------------------------------------
	def unlink_person (self, person):
		cmd = "delete from dem.lnk_person_org_address where id_org = %s and id_identity = %s"
		return gmPG.run_commit2 ('personalia', [(cmd, [self.getId(), person.ID])])
	#----------------------------------------------------------------------
	def getId (self):
		"""
		Hide the difference between org.id and v_basic_person.pk_identity
		"""
		return self['id']
#==============================================================================
def get_time_tuple (mx):
	"""
	wrap mx.DateTime brokenness
	Returns 9-tuple for use with pyhon time functions
	"""
	return [ int(x) for x in  str(mx).split(' ')[0].split('-') ] + [0,0,0, 0,0,0]
#----------------------------------------------------------------
def getAddressTypes():
	"""Gets a dict matching address types to their ID"""
	row_list = gmPG.run_ro_query('personalia', "select name, id from dem.address_type")
	if row_list is None:
		return {}
	if len(row_list) == 0:
		return {}
	return dict (row_list)
#----------------------------------------------------------------
def getMaritalStatusTypes():
	"""Gets a dictionary matching marital status types to their internal ID"""
	row_list = gmPG.run_ro_query('personalia', "select name, pk from dem.marital_status")
	if row_list is None:
		return {}
	if len(row_list) == 0:
		return {}
	return dict(row_list)
#------------------------------------------------------------------
def getExtIDTypes (context = 'p'):
	"""Gets dictionary mapping ext ID names to internal code from the backend for the given context
	"""
	# FIXME: error handling
	rl = gmPG.run_ro_query('personalia', "select name, pk from dem.enum_ext_id_types where context = %s", None, context)
	if rl is None:
		return {}
	return dict (rl)
#----------------------------------------------------------------
def getRelationshipTypes():
	"""Gets a dictionary of relationship types to internal id"""
	row_list = gmPG.run_ro_query('personalia', "select description, id from dem.relation_types")
	if row_list is None:
		return None
	if len (row_list) == 0:
		return None
	return dict(row_list)

#----------------------------------------------------------------
def getUrb (id_urb):
	cmd = """
select
	dem.state.name,
	dem.urb.postcode
from
	dem.urb,
	dem.state
where
	dem.urb.id = %s and
	dem.urb.id_state = dem.state.id"""
	row_list = gmPG.run_ro_query('personalia', cmd, None, id_urb)
	if not row_list:
		return None
	else:
		return (row_list[0][0], row_list[0][1])

def getStreet (id_street):
	cmd = """
select
	dem.state.name,
	coalesce (dem.street.postcode, dem.urb.postcode),
	dem.urb.name
from
	dem.urb,
	dem.state,
	dem.street
where
	dem.street.id = %s and
	dem.street.id_urb = dem.urb.id and
	dem.urb.id_state = dem.state.id
"""
	row_list = gmPG.run_ro_query('personalia', cmd, None, id_street)
	if not row_list:
		return None
	else:
		return (row_list[0][0], row_list[0][1], row_list[0][2])

def getCountry (country_code):
	row_list = gmPG.run_ro_query('personalia', "select name from dem.country where code = %s", None, country_code)
	if not row_list:
		return None
	else:
		return row_list[0][0]
#-------------------------------------------------------------------------------
def get_town_data (town):
	row_list = gmPG.run_ro_query ('personalia', """
select
	dem.urb.postcode,
	dem.state.code,
	dem.state.name,
	dem.country.code,
	dem.country.name
from
	dem.urb,
	dem.state,
	dem.country
where
	dem.urb.name = %s and
	dem.urb.id_state = dem.state.id and
	dem.state.country = dem.country.code""", None, town)
	if not row_list:
		return (None, None, None, None, None)
	else:
		return tuple (row_list[0])
#============================================================
# callbacks
#------------------------------------------------------------
def _post_patient_selection(**kwargs):
	print "received post_patient_selection notification"
	print kwargs['kwds']
#============================================================

#============================================================
# main
#------------------------------------------------------------
if __name__ == "__main__":

	import random
	#--------------------------------------------------------
	def test_address_exists():
		exists = address_exists (
			country ='Germany',
			state ='Sachsen',
			urb ='Leipzig',
			suburb ='Sellerhausen',
			postcode ='04318',
			street = u'Cunnersdorfer Strasse',
			number = '11',
			notes_subunit = '4.Stock rechts'
		)
		if exists is None:
			print "address does not exist"
		else:
			print "address exists, primary key:", exists
	#--------------------------------------------------------
	def test_create_address():
		address = create_address (
			country ='DE',
			state ='SN',
			urb ='Leipzig',
			suburb ='Sellerhausen',
			postcode ='04318',
			street = u'Cunnersdorfer Strasse',
			number = '11'
#			,notes_subunit = '4.Stock rechts'
		)
		print "created existing address"
		print address

		su = str(random.random())

		address = create_address (
			country ='DE',
			state = 'SN',
			urb ='Leipzig',
			suburb ='Sellerhausen',
			postcode ='04318',
			street = u'Cunnersdorfer Strasse',
			number = '11',
#			notes_subunit = '4.Stock rechts',
			subunit = su
		)
		print "created new address with subunit", su
		print address
		print "deleted address:", delete_address(address)
	#--------------------------------------------------------

	try:
		gmPG2.get_connection()

		test_address_exists()
		test_create_address()
	except:
		_log.exception('test suite failed')
		raise

	sys.exit()

	gmDispatcher.connect(_post_patient_selection, 'post_patient_selection')
	while 1:
		pID = raw_input('a patient: ')
		if pID == '':
			break
		try:
			print pID
			myPatient = gmPerson.cIdentity (aPK_obj = pID)
		except:
			_log.exception('Unable to set up patient with ID [%s]' % pID)
			print "patient", pID, "can not be set up"
			continue
		print "ID       ", myPatient.ID
		print "name     ", myPatient['description']
		print "title    ", myPatient['title']
		print "dob      ", myPatient['dob']
		print "med age  ", myPatient['medical_age']
		for adr in myPatient.get_addresses():
			print "address  ", adr
		print "--------------------------------------"
#============================================================
# $Log: gmDemographicRecord.py,v $
# Revision 1.96  2008-02-26 16:24:49  ncq
# - remove pk_address from create_comm_channel
#
# Revision 1.95  2008/02/25 17:29:40  ncq
# - cleanup
#
# Revision 1.94  2008/01/07 19:32:15  ncq
# - cleanup, rearrange
# - create comm channel API
#
# Revision 1.93  2007/12/03 20:41:07  ncq
# - get_comm_channel_types()
#
# Revision 1.92  2007/12/02 20:56:37  ncq
# - adjust to table changes
#
# Revision 1.91  2007/11/17 16:10:53  ncq
# - improve create_address()
# - cleanup and fixes
#
# Revision 1.90  2007/11/12 22:52:01  ncq
# - create_address() now doesn't care about non-changing fields
#
# Revision 1.89  2007/11/07 22:59:31  ncq
# - don't allow editing number on address
#
# Revision 1.88  2007/03/23 15:01:36  ncq
# - no more person['id']
#
# Revision 1.87  2007/02/22 16:26:54  ncq
# - fix create_address()
#
# Revision 1.86  2006/11/26 15:44:03  ncq
# - do not use es-zet in test suite
#
# Revision 1.85  2006/11/19 10:58:52  ncq
# - fix imports
# - add cAddress
# - add cPatientAddress
# - remove dead match provider code
# - add address_exists(), create_address(), delete_address()
# - improve test suite
#
# Revision 1.84  2006/10/25 07:17:40  ncq
# - no more gmPG
# - no more cClinItem
#
# Revision 1.83  2006/10/24 13:15:48  ncq
# - comment out/remove a bunch of deprecated/unused match providers
#
# Revision 1.82  2006/07/19 20:25:00  ncq
# - gmPyCompat.py is history
#
# Revision 1.81  2006/06/14 10:22:46  ncq
# - create_* stored procs are in schema dem.* now
#
# Revision 1.80  2006/05/15 13:24:13  ncq
# - signal "activating_patient" -> "pre_patient_selection"
# - signal "patient_selected" -> "post_patient_selection"
#
# Revision 1.79  2006/01/07 13:13:46  ncq
# - more schema qualifications
#
# Revision 1.78  2006/01/07 11:23:24  ncq
# - must use """ for multi-line string
#
# Revision 1.77  2006/01/06 10:15:37  ncq
# - lots of small fixes adjusting to "dem" schema
#
# Revision 1.76  2005/10/09 08:11:48  ihaywood
# introducing get_town_data (), a convience method to get info that can be inferred from a town's name (in AU)
#
# Revision 1.75  2005/10/09 02:19:40  ihaywood
# the address widget now has the appropriate widget order and behaviour for australia
# when os.environ["LANG"] == 'en_AU' (is their a more graceful way of doing this?)
#
# Remember our postcodes work very differently.
#
# Revision 1.74  2005/06/07 10:15:47  ncq
# - setContext -> set_context
#
# Revision 1.73  2005/04/25 08:26:48  ncq
# - cleanup
#
# Revision 1.72  2005/04/14 19:14:51  cfmoro
# Gender dict was replaced by get_genders method
#
# Revision 1.71  2005/04/14 18:58:14  cfmoro
# Added create occupation method and minor gender map clean up, to replace later by get_gender_list
#
# Revision 1.70  2005/04/14 08:49:29  ncq
# - move cIdentity and dob2medical_age() to gmPerson.py
#
# Revision 1.69  2005/03/30 21:04:01  cfmoro
# id -> pk_identity
#
# Revision 1.68  2005/03/29 18:55:39  cfmoro
# Var name fix
#
# Revision 1.67  2005/03/20 16:47:26  ncq
# - cleanup
#
# Revision 1.66  2005/03/08 16:41:37  ncq
# - properly handle title
#
# Revision 1.65  2005/03/06 08:17:02  ihaywood
# forms: back to the old way, with support for LaTeX tables
#
# business objects now support generic linked tables, demographics
# uses them to the same functionality as before (loading, no saving)
# They may have no use outside of demographics, but saves much code already.
#
# Revision 1.64  2005/02/20 21:00:20  ihaywood
# getId () is back
#
# Revision 1.63  2005/02/20 09:46:08  ihaywood
# demographics module with load a patient with no exceptions
#
# Revision 1.61  2005/02/19 15:04:55  sjtan
#
# identity.id is now identity.pk_identity, so adapt
#
# Revision 1.60  2005/02/18 11:16:41  ihaywood
# new demographics UI code won't crash the whole client now ;-)
# still needs much work
# RichardSpace working
#
# Revision 1.59  2005/02/13 15:46:46  ncq
# - trying to keep up to date with schema changes but may conflict with Ian
#
# Revision 1.58  2005/02/12 14:00:21  ncq
# - identity.id -> pk
# - v_basic_person.i_id -> i_pk
# - likely missed some places here, though
#
# Revision 1.57  2005/02/03 20:17:18  ncq
# - get_demographic_record() -> get_identity()
#
# Revision 1.56  2005/02/01 10:16:07  ihaywood
# refactoring of gmDemographicRecord and follow-on changes as discussed.
#
# gmTopPanel moves to gmHorstSpace
# gmRichardSpace added -- example code at present, haven't even run it myself
# (waiting on some icon .pngs from Richard)
#
# Revision 1.55  2005/01/31 10:37:26  ncq
# - gmPatient.py -> gmPerson.py
#
# Revision 1.54  2004/08/18 09:05:07  ncq
# - just some cleanup, double-check _ is defined for epydoc
#
# Revision 1.53  2004/07/26 14:34:49  sjtan
#
# numbering correction from labels in gmDemograpics.
#
# Revision 1.52  2004/06/25 12:37:19  ncq
# - eventually fix the import gmI18N issue
#
# Revision 1.51  2004/06/21 16:02:08  ncq
# - cleanup, trying to make epydoc fix do the right thing
#
# Revision 1.50  2004/06/21 14:48:25  sjtan
#
# restored some methods that gmContacts depends on, after they were booted
# out from gmDemographicRecord with no home to go , works again ;
# removed cCatFinder('occupation') instantiating in main module scope
# which was a source of complaint , as it still will lazy load anyway.
#
# Revision 1.49  2004/06/20 15:38:00  ncq
# - remove import gettext/_ = gettext.gettext
# - import gmI18N handles that if __main__
# - else the importer of gmDemographicRecord has
#   to handle setting _
# - this is the Right Way as per the docs !
#
# Revision 1.48  2004/06/20 06:49:21  ihaywood
# changes required due to Epydoc's OCD
#
# Revision 1.47  2004/06/17 11:36:12  ihaywood
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
