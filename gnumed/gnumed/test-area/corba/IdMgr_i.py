#IdMgr_i.py implements  IdMgr interface
import PersonIdService__POA

import CORBA
import CosNaming
import ResolveIdComponent
from StartIdentificationComponent import StartIdentificationComponent
import PersonIdTraits
from PlainConnectionProvider import *
import HL7Version2_3

import threading, thread, traceback, time, sys

from  PersonIdTestUtils import *
from SqlTraits import *
global debug
debug = '-debug' in sys.argv

class IdMgr_i (PersonIdService__POA.IdMgr, StartIdentificationComponent):

	def __init__(self, dsn=None, ProviderClass = PlainConnectionProvider, limit = MAX_TRAITS_RETURNED ):
		self.connector = ProviderClass(dsn)
		self.limit = limit
		self._optimize_calltime_by_sql_prepare()

	def _optimize_calltime_by_sql_prepare(self):
		con = self.connector.getConnection()
		self.prep_insert_blank_id ="prepare insert_blank_id as insert into identity( id, gender, dob) values( nextval('identity_id_seq'),'?', now() )"
		self.execute_insert_blank_id = "execute insert_blank_id"
		self.prep_get_last_id = "prepare get_last_id as select currval('identity_id_seq')"
		self.execute_get_last_id = "execute get_last_id"
		self.prep_get_identity = "prepare get_identity(int)  as select id from identity where id= $1"
		self.execute_get_identity = "execute get_identity(%s)"
		self.prep_insert_an_id = "prepare insert_an_id(int) as insert into identity( id, gender, dob) values( $1, '?', now() ) "
		self.execute_insert_an_id = "execute insert_an_id(%s)"

		con.execute(self.prep_insert_blank_id)
		con.execute(self.prep_get_last_id)
		con.execute(self.prep_get_identity)
		con.execute(self.prep_insert_an_id)

	def find_or_register_ids(self, profiles):
		if debug:
			print "find_or_register_ids() got these:"
			for p in profiles:print_brief_profile(p)
		iperson = self._get_identify_person()
		new_profiles = []
		existing_ids = []
		for p in profiles:
			candidateSeq = getExistingCandidateSeq(self, p)
			if candidateSeq ==[]:
				new_profiles.append(p)
			else:
				existing_ids.append(candidateSeq[0].id)
		if debug:
			print "\n\nfind_or_register_ids() found these existing profiles ", existing_ids, "\n\n"
		new_ids = self._do_register_new_ids( new_profiles)

		existing_ids.extend(new_ids)

		return existing_ids

	def register_new_ids(self, new_profiles):
		violating_sequence_indexes = get_existing_profile_seq_indexes( self, new_profiles)
		if violating_sequence_indexes <> [] :
			raise PersonIdService.IdsExist(violating_sequence_indexes)

		return self._do_register_new_ids(new_profiles)

	def _do_register_new_ids(self, new_profiles):
		con = self.connector.getConnection()
		con.commit()
		cursor = con.cursor()
		new_ids = []

		for profile in new_profiles:
			# the strategy (aka hack) is to re-use doProfileUpdate method
			# create a id first.
			cursor.execute("select max(id) from identity")
			[id] = cursor.fetchone()
			id += 1
			cursor.execute("insert into identity(id, dob) values ( %s, now() )" % id)
			id = str(id)


			print "GET LAST ID = ", id

			profileUpdate = PersonIdService.ProfileUpdate(id, [], profile)
			do_profile_update(profileUpdate, self.connector.getConnection() )

			new_ids.append(id)
		con.commit()
		return new_ids

	def register_these_ids(self,  tagged_profiles):
		con = self.connector.getConnection()
		existing_ids_pos = []
		for tp in tagged_profiles:
			con.execute(self.execute_get_identity % tp.id)
			res = con.fetchone()
			if not (res == None or len(res) == 0):
				existing_ids_pos.append( str( res[0]) )
		if existing_ids_pos <> []:
			raise PersonIdService.IdsExist( existing_ids_pos)


		existing_profile_pos = get_existing_profile_seq_indexes(self, [ tp.profile for tp in tagged_profiles])
		if existing_profile_pos <> []:
			if debug:
				print "register_these_ids() returned these ids ", existing_profile_pos , "for the following profiles", output_tagged_profile_sequence(tagged_profiles)
			raise PersonIdService.ProfilesExist(existing_profile_pos)

		con = self.connector.getConnection()
		con.commit()
		new_ids = []
		for tp in tagged_profiles:
			# the strategy (aka hack) is to re-use doProfileUpdate method
			# create a id first.
			cursor = con.cursor()
			cursor.execute(self.execute_insert_an_id % tp.id)
			profileUpdate = PersonIdService.ProfileUpdate(tp.id, [], tp.profile)
			do_profile_update(profileUpdate, self.connector.getConnection() )
		con.commit()




def get_existing_profile_seq_indexes( component, profiles):
	violating_sequence_indexes = []
	i = 0
	for p in profiles:
		if getExistingCandidateSeq( component , p) <> []:
			violating_sequence_indexes.append(i)
		i += 1
	return violating_sequence_indexes

def getExistingCandidateSeq(component, p):
	traitSelectorSeq = getTraitSelectorSeqFromProfile(p, defaultWeight=0.2)
	iperson = component._get_identify_person()
	candidateSeq , iterator = iperson.find_candidates(traitSelectorSeq, [PersonIdService.PERMANENT], 0.5, 100, 10, PersonIdService.SpecifiedTraits(PersonIdService.ALL_TRAITS, [] ) )
	return candidateSeq

