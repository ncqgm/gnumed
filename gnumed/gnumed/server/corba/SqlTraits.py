
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



in_trait_map = {

hl7.SEX : 'gender',
hl7.DATE_TIME_OF_BIRTH : 'dob',
hl7.NATIONALITY : 'cob',
hl7.PATIENT_DEATH_DATE_AND_TIME : 'deceased'
}


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
  state.name as state, state.country as country_code,
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
	if debug:
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
			field_value_map[fields[i]] = ( l[i], weight)

	return field_value_map


def get_supported_traits():
	"""returns the global supported trait names for this gnumed broker"""
	global supported_traits
	return supported_traits


def get_supported_trait_names():
	return [ traitspec.trait for traitspec in supported_traits]
