
import PersonIdService
import sys
import string
import CORBA
import HL7Version2_3
import PersonIdTraits
from PersonIdService import TraitSpec
from PersonIdTestUtils import *

global HOME_PHONE_TYPE, BUSINESS_PHONE_TYPE
HOME_PHONE_TYPE = 1
BUSINESS_PHONE_TYPE =2

MAX_TRAITS_RETURNED  = 10000

global hl7
hl7 = HL7Version2_3

global pids
pids = PersonIdTraits

global debug
debug = '-debug' in sys.argv


global supported_traits

supported_traits= [
TraitSpec(pids.INTERNAL_ID, 0, 1, 1),
TraitSpec(hl7.PATIENT_NAME, 1, 0, 1),
TraitSpec(hl7.SEX, 0, 0, 1),
TraitSpec(hl7.DATE_TIME_OF_BIRTH, 0, 0, 1),
TraitSpec(hl7.PATIENT_ADDRESS, 0, 0, 1),
TraitSpec(hl7.PHONE_NUMBER_HOME, 0, 0, 1),
TraitSpec(hl7.PHONE_NUMBER_BUSINESS, 1, 0, 1),
TraitSpec(hl7.NATIONALITY, 1, 0, 1),
TraitSpec(hl7.PATIENT_DEATH_DATE_AND_TIME, 0, 0, 1),
#TraitSpec(hl7.MARITAL_STATUS, 1, 0, 1),
#TraitSpec(pids.NATIONAL_HEALTH_IDS, 1, 0, 1),
#TraitSpec(hl7.CITIZENSHIP, 1, 0, 1),
#TraitSpec(hl7.ETHNIC_GROUP, 1, 0, 1),
#TraitSpec(hl7.VETERANS_MILITARY_STATUS, 1, 0, 1),
#TraitSpec(hl7.PRIMARY_LANGUAGE, 1, 0, 1),
#TraitSpec("HL7/PatientAlias", 0, 0, 1)
#, TraitSpec("HL7/CountryCode", 1, 0, 1)
]

s = supported_traits

to_trait_map = { 'id': (s[0], 0),
		'lastnames': (s[1], 0),
		'firstnames':(s[1], 1),
		'preferred':(s[1], 2),
		'title': (s[1], 3),
		'gender': (s[2], 0),
		'datetimeofbirth': (s[3], 0),
		'number': (s[4], 0),
		'street' : (s[4], 1),
		'urb_name': (s[4], 2),
		'postcode': (s[4], 4),
		'state' : (s[4], 3),
		'country_code': (s[4], 5),
		'telephone_home': (s[5], 0),
		'telephone_business': (s[6], 0),
		'cob': (s[7],0),
		'deathdateandtime': (s[8], 0)
	 }

global idPerson_field_filters
idPerson_field_filters = { 'gender': [string.lower] }

in_trait_map = {

hl7.SEX : 'gender',
hl7.DATE_TIME_OF_BIRTH : 'dob',
hl7.NATIONALITY : 'cob',
hl7.PATIENT_DEATH_DATE_AND_TIME : 'deceased'
}

default_weight_map = {
	'gender': 0.1 ,
	'country_code' : 0.1,
	'datetimeofbirth': 0.8,
	'lastnames': 0.6,
	'firstnames': 0.6,
	'number':0.5,
	'street':0.4,
	'urb_name': 0.3,
	'state': 0.1,
	'postcode': 0.3,
	'home_telephone' : 0.8
	}
global weight_OR_threshold
weight_OR_threshold = 0.5

global sql_identity

sql_identity = "select  id,  ni.lastnames , ni.firstnames , ni.preferred  , ni.title, ni.gender,to_char( ni.dob, 'YYYYMMDDHH24MISS') as datetimeofbirth, ni.cob, to_char(ni.deceased, 'YYYYMMDDHH24MISS') as deathdateandtime  from (select * from identity i, (select id_identity , lastnames, preferred , firstnames,   active from names) as na where i.id = na.id_identity and na.active = true ) as ni"


sql_address = "select * from (select  id, id_street, number from address) as a natural left join (select id as id_street,   id_urb, name as street from street) as foo  natural left join (select id as id_urb, name as urb_name , postcode, id_state from urb) as urbfoo natural left join (select id as id_state , name as state, country as country_code from state) as statefoo "

sql_comm = "select cc.id, url, description as type from comm_channel cc left join enum_comm_types ecc on ( cc.id_type = ecc.id)"

sql_traits = """select * from
(
  select i.id ,  lastnames, firstnames, preferred, title,
  gender, cob,
  a.number, s.name as street,
  u.name as urb_name , u.postcode,
  state.code as state, state.country as country_code,
  trim(both ' ' from c.url) as telephone_home,
  trim (both ' ' from c2.url2) as telephone_business,
   to_char( dob, 'YYYYMMDDHH24MISS') as datetimeofbirth,
   to_char(deceased, 'YYYYMMDDHH24MISS') as deathdateandtime
   from
   identity i
   left outer join names na  on ( i.id = na.id_identity and na.active = true )
   left outer join lnk_person2address l1 on (i.id = l1.id_identity)
   left outer join  address a on ( l1.id_address = a.id )
   left outer join street  s on ( a.id_street = s.id)
   left outer join urb u on ( s.id_urb = u.id)
   left outer join state on ( u.id_state = state.id)
   left outer join lnk_person2comm_channel l2 on (l2.id_identity = i.id)
   left outer join (select cc.id, cc.id_type, url  from comm_channel cc ) as c on (c.id = l2.id_comm and c.id_type = 1)
   left outer join  lnk_person2comm_channel l3   on (l3.id_identity = i.id)
   left outer join  ( select cc2.id as id2, cc2.id_type , url as url2   from comm_channel cc2 ) as c2 on (c2.id2 = l3.id_comm and c2.id_type = 2)
   ) as i
where
not exists ( select id from lnk_person2comm_channel l4 where l4.id_identity = i.id)
or ( telephone_business <> '' and telephone_home <> '')
or ( telephone_business <> ''
	and not exists(
		select l5.id from lnk_person2comm_channel l5, comm_channel cc3  		where l5.id_identity  = i.id
			and l5.id_comm = cc3.id
			and cc3.id_type = 1
	)
)
or ( telephone_home <> ''
	and not exists(
		select l6.id from lnk_person2comm_channel l6, comm_channel cc4 				where l6.id_identity = i.id
				and l6.id_comm = cc4.id
				and cc4.id_type=2
		)
)"""


sql_traits_old = "select * from (select i.id ,  lastnames, firstnames, preferred, title, gender, datetimeofbirth, cob, deathdateandtime, a.number, a.street, a.urb_name, a.postcode, a.state, a.country_code, trim(both ' ' from c.url) as telephone_home,  c.type as tel_home_type, trim (both ' ' from c2.url2) as telephone_business,  c2.type2 as tel_bus_type from (  select  id, ni.lastnames , ni.firstnames , ni.preferred  , ni.title, ni.gender,to_char( ni.dob, 'YYYYMMDDHH24MISS') as datetimeofbirth, ni.cob, to_char(ni.deceased, 'YYYYMMDDHH24MISS') as deathdateandtime  from (select * from identity i, (select id_identity , lastnames, preferred , firstnames,   active from names) as na where i.id = na.id_identity and na.active = true ) as ni ) as i  left join lnk_person2address l1 on (i.id = l1.id_identity) left outer join (select * from (select  id, id_street, number from address) as a natural left join (select id as id_street,   id_urb, name as street from street) as foo  natural left join (select id as id_urb, name as urb_name , postcode, id_state from urb) as urbfoo natural left join (select id as id_state , name as state, country as country_code from state) as statefoo) as a on (l1.id_address = a.id) left outer join lnk_person2comm_channel l2 on (l2.id_identity = i.id) left join (select cc.id, cc.id_type, url, description as type from comm_channel cc left join enum_comm_types ecc on ( cc.id_type = ecc.id)) as c on (c.id = l2.id_comm and c.id_type = 1) left join  lnk_person2comm_channel l3 on (l3.id_identity = i.id) left join  ( select cc2.id as id2, cc2.id_type , url as url2 , description as type2 from comm_channel cc2 left join enum_comm_types ecc2 on ( cc2.id_type = ecc2.id)) as c2 on (c2.id2 = l3.id_comm and c2.id_type = 2)) as tr  where not exists ( select id from lnk_person2comm_channel l4 where l4.id_identity = tr.id)  or ( telephone_business <> '' and telephone_home <> '') or ( telephone_business <> '' and not exists( select l5.id from lnk_person2comm_channel l5, comm_channel cc3  where l5.id_identity  = tr.id and l5.id_comm = cc3.id and cc3.id_type = 1)) or ( telephone_home <> '' and not exists( select l6.id from lnk_person2comm_channel l6, comm_channel cc4 where l6.id_identity = tr.id and l6.id_comm = cc4.id and cc4.id_type=2))"

trait_to_sql_trait_field = {
	pids.INTERNAL_ID :['id'],
	hl7.PATIENT_NAME :['lastnames', 'firstnames', 'preferred', 'title'],
	hl7.SEX : ['gender'],
	hl7.DATE_TIME_OF_BIRTH : ['datetimeofbirth'],
	hl7.PATIENT_ADDRESS : [ 'number', 'street', 'urb_name', 'state', 'postcode', 'country_code' ],
	hl7.PHONE_NUMBER_HOME : ['telephone_home'],
	hl7.PHONE_NUMBER_BUSINESS : ['telephone_business'],
	hl7.NATIONALITY : ['cob'],
	hl7.PATIENT_DEATH_DATE_AND_TIME : ['deathdateandtime']
}
"""this maps the HL7Version2_3 names to field positions in the gnumed traits view."""

def get_trait_map(idComponent, firstname, middle, lastname,suffix,  street, otherDesignation, city, state, postcode, country,
	dobDay, dobMonth, dobYear, sex, phoneCountryCode, phoneNumber):
	"""constructs a python map of supported trait names vs. the above data fields.
	"""

	n= '^'.join( [lastname, firstname, middle, suffix,'',''])
	a='^'.join([street, otherDesignation, city, state, postcode, country,' ',' '])
	b=''.join([str(dobYear), str(dobMonth), str(dobDay) ])
	s= sex
	p='^'.join([phoneCountryCode, phoneNumber])
	return get_trait_map_nabsp(idComponent, n,a ,b ,s, p)


def get_field_index_map( description):
	"""gets a map[fieldName] = row item position  , from a dbapi cursor description."""
	ix = {}
	for i in xrange(0, len(description)):
		ix[description[i][0]] = i
	if '-debug2' in sys.argv:
		print "index map is ",ix
	return ix


global expected_hl7_fieldcount

expected_hl7_fieldcount = {
	hl7.PATIENT_ADDRESS: 6,
	hl7.PATIENT_NAME: 6
	}

def get_tagged_profile_from_row(row, desc, traitspec_map = to_trait_map, index_map = None, idName = 'id'	) :

	"""gets a PersonIdService.TaggedProfile from a  row in a select from a traits
	view.
	The traitspec_map maps a traits view field name to a traitSpec and a hl7 field position
	e.g. position = 2 for firstnames in PatientName = 'Smith^John Harold^^^^'

	The traitSpec.trait is the output mapping key,  and is the string name for the trait."""
	if index_map == None:
		index_map = get_field_index_map(desc)
	traitMap = {}
	for i in xrange(0, len(desc)):
		traitspec, pos   = traitspec_map.get(desc[i][0], (None, 0 ) )
		if traitspec == None:
			continue
		n = traitspec.trait
		list = traitMap.get(n, [] )
		if len(list) <= pos:
			list.extend( (pos - len(list) + 1) * [''] )

		if row[i] == None:
			list[pos] = ''
		else:	list[pos] = str(row[i]).strip()

		traitMap[n] = list
	newMap = {}
	global expected_hl7_fieldcount
	for k,v in traitMap.items():
		#check the number of ^ separators is as expected
		n_fields =expected_hl7_fieldcount.get(k, 0)
		if len(v) < n_fields:
			v.extend( [''] * (n_fields - len(v) ))
		#create the trait value e.g. 'Smith^John^Jo^Mr^^^'
		newMap[k] = '^'.join(v)

	return PersonIdService.TaggedProfile( str(row[index_map[idName]]) ,trait_map_to_profile( newMap) )


def merge_tagged_profiles( tprofiles):
	"""merges the tprofiles into a set sequence of unique profiles. Multiple tagged_profiles
	with the same id, will have their traits merged, with the latest overwriting any conflicting traits."""
	tprofile_map = {}
	for tprofile in tprofiles:
		if not tprofile_map.has_key(tprofile.id):
			tprofile_map[tprofile.id] = tprofile.profile
		else:
			merge_tprofile( tprofile_map, tprofile)

	merged_tprofiles = []
	for id, tprofile in tprofile_map.items():
		merged_tprofiles.append(PersonIdService.TaggedProfile( id, tprofile) )
	return merged_tprofiles


def get_tagged_profiles_from_cursor_result( result,desc ):
	"""gets a set sequence of tagged_profiles from a dbapi.cursor.result set.
	The rows in the cursor result may have duplicate ids, in which case
	the values are merged , using merge_tagged_profiles().
	 This feature was obsoleted, because it was found
	to be easier to deal with when an sql select statement selects out redundant
	rows ( e.g. as when left joining a identity with 2 rows in a comm_channel ( one row for business home, and one for home phone).


	"""
	ix = get_field_index_map(desc)
	tprofiles = [  get_tagged_profile_from_row(row, desc, to_trait_map) for row in result ]
	return merge_tagged_profiles(tprofiles)


def merge_tprofile( tprofile_map, tprofile):
	"""Merges the traits in a tagged profile with a tagged profile in a map of tagged profiles mapped by id. The tagged profile is selected by its matching id.
	Usage: called by merge_tagged_profiles to update a map of tagged profiles with a tagged profile"""
	for trait in tprofile.profile:
		v = trait.value.value()
		if v == None:
			continue
		if str(v).strip() == '':
			continue
		#if int(v) == 0:
		#	continue
		otrait=find_trait_in_profile(trait.name, tprofile_map[tprofile.id])
		if otrait == None:
			tprofile_map[tprofile.id].append(trait)
		else:
			otrait.value = CORBA.Any(CORBA._tc_string, str(v) )

def get_field_list_and_traitname_list(specifiedTraits):
	"""gets a sql field name list, and the traits from the specified traits.
	Usage :  for the field list in a select statememt"""
	global supported_traits
	if specifiedTraits._d == PersonIdService.ALL_TRAITS:
		traits = [ ts.trait for ts in supported_traits ]
	else:
		traits = specifiedTraits.traits

	field_list = []
	for t in traits:
		field_list.extend( trait_to_sql_trait_field.get(t,[]) )

	if 'id ' not in field_list:
		field_list.append('id')
	if debug:
		print "field_list is ", field_list
	return field_list, traits

def get_field_weighted_value_map( traitSelectorSeq):
	"""gets a map of sql field name: (value, weight for value) from a traitSelectorSeq, which is a sequence of (trait, weight) """
	field_value_map = {}
	for traitSelector in traitSelectorSeq:
		trait, weight = traitSelector.trait, traitSelector.weight
		v = trait.value

		if v.typecode().kind() <> CORBA.tk_string or v.value().strip() == '':
			continue

		fields = trait_to_sql_trait_field.get(trait.name, [])
		print trait.name, " fields = ", fields
		l = [ x.strip() for x in v.value().split('^') ]
		for i in xrange( 0, min( len(l), len(fields) )):
			if l[i].strip() == '':
				continue
			weight_limit =default_weight_map.get(fields[i], 0.2)

			if weight < weight_limit:
				weight = weight_limit
			print "field ", fields[i], "weight = ", weight, "weight_limit", weight_limit
			field_value_map[fields[i]] = ( l[i], weight)

	return field_value_map


def get_supported_traits():
	"""returns the global supported trait names for this gnumed broker"""
	global supported_traits
	return supported_traits


def get_supported_trait_names():
	return [ traitspec.trait for traitspec in supported_traits]



def do_profile_update(pu, conn):
	"""iterates through the traits found in a profileUpdate.modify_list , and
	does the gnumed changes within the tables identity, names, lnk_person2address, lnk_person2comm_channel , address, street, comm_channel  to match the requested trait updates.
	TODO: cached prepared statement optimization?
	"""

			# the following statements can modify the db , so put inside transaction

	updated = []

	# check for non-blank duplicate traits in  modify list
	for t in pu.modify_list:
		if t.name in updated and t.value.typecode().kind() == CORBA.tk_string and t.value.value().strip(' ^') <> '':
			raise PersonIdService.ModifyOrDelete
		updated.append(t)

	 # used to find duplicate trait updates within the traits held by pu (profileUpdate type)
	statements = []
	# holds statements for a batch call , if any exists
	frags = []
	# reducing the number of sql calls by collecting identity field updates


	cursor = conn.cursor()
	if '-debug' in sys.argv:
		print "do_profile_update()"
		print "the modify list is : "
		for t in pu.modify_list:
			print t.name, t.value.value()
	other_traits_param_pos , other_traits_update_values = 0 , []
	for trait in pu.modify_list:
		# ignore blank values
		if trait.value.value().strip() == '':
			continue
		l =trait.value.value().split('^')
		l = [ x.strip() for x in l]
		updated.append(trait.name)
		if trait.name == hl7.PATIENT_NAME:
			if l[0] =='' and l[1] =='':
				continue

			# the clause 'and active=true' reduces the sql execution time
			# by over a half. This can be found by profiling the sql calls.
			if not conn.__dict__.has_key('exec_inactivate_old_names'):

				cursor.execute("prepare inactivate_old_names(int) as update names set active = false where id_identity = $1 and active = true ")
				conn.exec_inactivate_old_names = "execute inactivate_old_names(%s)"
			cursor.execute(conn.exec_inactivate_old_names % pu.id )
			# check for semantic key constraint
			if not conn.__dict__.has_key('exec_check_name_exists'):

				cursor.execute("prepare check_name_exists( text, text, text, int) as select id from names where lastnames = $1 and firstnames = $2 and preferred = $3 and id_identity = $4")
				conn.exec_check_name_exists = "execute check_name_exists('%s', '%s', '%s', %s)"
			conn.execute(conn.exec_check_name_exists  % tuple(l[0:3] + [pu.id]) )
			res = cursor.fetchone()
			if res <> None:
				n = res[0]

				cursor.execute("update names set active = true where id = %d" % n)
				continue

			if not conn.__dict__.has_key('exec_insert_names'):
				conn.execute("prepare insert_names( text, text, text, int) as insert into names ( lastnames, firstnames, preferred, id_identity, active) values ( $1, $2, $3, $4, true)")
				conn.exec_insert_names ="execute insert_names('%s', '%s', '%s', %s)"
			conn.execute(conn.exec_insert_names % tuple ( l[0:3]+[pu.id] ) )



			if len(l) >= 4 and l[3] <> '':
				statements.append("update identity set title = '%s' where id = %s" % ( l[4], pu.id))

		elif trait.name == hl7.PATIENT_ADDRESS:
			if l[1] == '' or l[2] =='' or l[3] =='' or (l[4] =='' and l[5] ==''):
				continue
			s1 = "delete from lnk_person2address where id_identity = %s and id_type = 1"
			s2_findUrb = "select urb.id from urb, state where state.id = urb.id_state and urb.name = '%s' and (urb.postcode = '%s' or state.code = '%s'  or state.name='%s' )"

			s3_findStreet = "select street.id, urb.id from street ,urb , state where street.id_urb = urb.id and urb.id_state = state.id and street.name ='%s' and ( street.id_urb = %d or   urb.postcode = '%s' or (street.postcode = '%s' and state.name = '%s' ))"
			s3b1_insertStreet = "insert into street( name, id_urb) values( '%s', %d)"
			s3b2_selectNewStreet = "select currval('street_id_seq')"


			s4_selectAddress = "select id from address a where a.number = '%s' and a.id_street = %d"

			s4b1_insertAddress = "insert into address  ( number, id_street) values ( '%s', %d)"
			s4b2_selectNewAddress = "select currval('address_id_seq')"

			cursor.execute(s1 % pu.id)
			cursor.execute(s2_findUrb % (l[2] ,l[4] ,l[3], l[3]) )
			res = cursor.fetchall()
			if (len(res) == 0):
				urb_id = 0
			else:
				urb_id = res[0][0]

			cursor.execute(s3_findStreet % ( l[1] ,urb_id,l[4], l[4], l[3] ))
			res = cursor.fetchall()



			if len(res) > 0 :
				street_id, urb_id = res[0][0], res[0][1]
			elif urb_id <> 0:
				cursor.execute(s3b1_insertStreet % (l[1], urb_id))
				cursor.execute(s3b2_selectNewStreet)
				[street_id] = cursor.fetchone()

			else:
				print "Unable to find with ", s2_findUrb % (l[2] ,l[4] ,l[3])
				raise PersonIdService.ModifyOrDelete

			cursor.execute(s4_selectAddress % (l[0], street_id))
			res = cursor.fetchall()

			if len(res) > 0:
				address_id = res[0][0]
				if debug:
					print "existing old address id", address_id
				cursor.execute("select count(*) from lnk_person2address where id_identity = %s and id_address = %d" % ( pu. id, address_id))
				[count] = cursor.fetchone()


			else:
				count =0
				cursor.execute(s4b1_insertAddress %(l[0], street_id))
				cursor.execute(s4b2_selectNewAddress)
				[address_id] = cursor.fetchone()
				if debug:
					print "new address id ", address_id

			s5 = "insert into lnk_person2address( id_identity, id_type, id_address) values ( %s, 1, %d)"
			if count == 0:
				cursor.execute(s5 % (pu.id, address_id) )

		elif trait.name in [ hl7.PHONE_NUMBER_HOME , hl7.PHONE_NUMBER_BUSINESS ]:
			# requires comm_type for home and business phone to be known

			if trait.name == hl7.PHONE_NUMBER_HOME: comm_type = HOME_PHONE_TYPE
			else:	 comm_type = BUSINESS_PHONE_TYPE

			if not conn.__dict__.has_key('exec_find_comm'):
				cursor.execute("""prepare find_comm(int, int) as
select id_comm from lnk_person2comm_channel l, comm_channel c where  id_identity = $1 and l.id_comm = c.id and c.id_type = $2""")

				conn.exec_find_comm = "execute find_comm(%s,%d)"
				cursor.execute("prepare delete_comm_reference(int, int) as delete from lnk_person2comm_channel  where id_identity = $1 and id_comm = $2")
				conn.exec_delete_comm_ref = "execute delete_comm_reference(%s, %d)"
				cursor.execute("""prepare count_remaining_comm_refs(int) as select count(id) from lnk_person2comm_channel l where l.id_comm = $1""")
				conn.exec_count_remaining_comm_refs = "execute count_remaining_comm_refs(%s)"
				cursor.execute("prepare delete_orphan_comm(int) as delete from comm_channel where id = $1")
				conn.exec_delete_orphan_comm = """execute delete_orphan_comm(%s)"""
				cursor.execute("""prepare find_existing_duplicate_comm(text) as select id from comm_channel where url= $1""")
				conn.exec_find_existing_duplicate_comm = "execute find_existing_duplicate_comm('%s')"

				cursor.execute("prepare create_comm( int, text) as  insert into comm_channel( id_type, url) values( $1 , $2)")
				cursor.execute("""prepare create_comm_lnk(int,int) as insert into lnk_person2comm_channel(id_identity, id_comm) values ( $1, $2)""")

			cursor.execute( conn.exec_find_comm % (pu.id, comm_type) )

			res = cursor.fetchone()
			if (res <> None and len(res) <> 0):
				id_comm = res[0]
				cursor.execute(conn.exec_delete_comm_ref % (pu.id, id_comm) )
				cursor.execute( conn.exec_count_remaining_comm_refs % id_comm)

				res2 = cursor.fetchone()
				if res2[0] == 0:
					cursor.execute(conn.exec_delete_orphan_comm % id_comm)

			cursor.execute( conn.exec_find_existing_duplicate_comm %  trait.value.value()  )

			res = cursor.fetchone()
			if debug:
				print "existing id comm_channel =", res
			if res <> None:
				id_comm = res[0]
			else:
				cursor.execute("execute create_comm( %d, '%s')" % (comm_type, trait.value.value() ))
				cursor.execute("""select currval('comm_channel_id_seq')""")
				[id_comm] = cursor.fetchone()
			cursor.execute("execute create_comm_lnk(%s, %d)" % ( pu.id, id_comm) )



		elif trait.name in [ hl7.DATE_TIME_OF_BIRTH, hl7.PATIENT_DEATH_DATE_AND_TIME ] :
			if l[0] == '':
				continue
			other_traits_param_pos += 1
			frags.append(" %s = to_timestamp($%d, 'YYYYMMDDHH24MISS')" %
			( in_trait_map[trait.name], other_traits_param_pos) )

			other_traits_update_values.append( trait.value.value()  )

			#statements.append( "update identity set %s = to_timestamp('%s', 'YYYYMMDDHH24MISS') where id = %s" % ( in_trait_map[trait.name], trait.value.value(), pu.id) )
		elif trait.name in [hl7.SEX, hl7.NATIONALITY]:
			if l[0] == '':
				continue
			other_traits_param_pos += 1
			frags.append( " %s = $%d" % (in_trait_map[trait.name], other_traits_param_pos))
			other_traits_update_values.append( trait.value.value().lower()  )

			#statements.append("update identity set %s = '%s' where id = %s" % (in_trait_map[trait.name], trait.value.value(), pu.id) )
	if frags <> []:

		stmt = "update identity set %s where id = $%d" % ( ",".join(frags), other_traits_param_pos + 1)
		h =abs( hash(stmt))
		if not conn.__dict__.has_key('other_stmts'):
			conn.other_stmts = {}

		if not conn.other_stmts.has_key(h):
			conn.other_stmts[h] = "execute do_trait_update_%d(%s)" % (h , ", ".join( ["'%s'"] * len(other_traits_update_values) + ["%s"]  ) )

			cursor.execute("""prepare do_trait_update_%d(%s) as %s""" % (h,  ", ".join( ['text'] * len(other_traits_update_values) + ['int'] ) ,  stmt) )

		cursor.execute(conn.other_stmts[h] % tuple(other_traits_update_values + [pu.id]) )



	for s in statements:
		cursor.execute(s)

	return

