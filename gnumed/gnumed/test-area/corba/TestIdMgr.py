import PersonIdService
import ResolveIdComponent
import CORBA
import sys, string, random, traceback
from PersonIdTestUtils import *
import SqlTraits

debug = 0
last_id = 0
def test():
	debug = "-debug" in sys.argv

	resolver = ResolveIdComponent.IDComponentResolver()

	if '-gnumed' in sys.argv:
		path = 'gnumed'
	else:
		path = None

	ic = resolver.getIdentificationComponent(path)

	idMgr = ic._get_id_mgr()


	init_trait_spec(idMgr)



	print type(idMgr)
	print PersonIdService._tc_IdMgr.__methods__
	catchExceptions(_test_find_or_register_id, idMgr)
	catchExceptions(_test_register_new_ids,idMgr)
	catchExceptions(_test_register_these_ids,idMgr)
	catchExceptions(_test_merge_ids,idMgr)
	catchExceptions(_test_unmerge_ids,idMgr)

def __getTestProfiles(idMgr):
	# lastName^firstname^middlename^suffix
	n = "Smith^John^Harold^^^"

	# street^otherDesignation^city^state^postcode^country^_^_
	#  ( _ is space)
	a = "123 Black Rd^^BLACKTOWN^NSW^2148^AU^"

	#    yyyymmddhhmmss
	b = "19650227123000"

	s = "M"

	# phoneCountry^phoneNumber

	p = "65^034542222"

	return SqlTraits.get_trait_map_nabsp( idMgr, n, a, b, s, p)


profile = None
profile2 = None
def _test_find_or_register_id(idMgr):
	global profile, profile2
	profile = trait_map_to_profile( __getTestProfiles(idMgr))
	print "\n\nTesting inserting single profile twice"
	idList = idMgr.find_or_register_ids([profile])
	idList2 = idMgr.find_or_register_ids([profile])
	print idList == idList2, " if 1 then find_or_create_ids() twice returns same id"
	if idList == idList2:
		print "PASS: find_or_create_ids() doesn't duplicate id"

	map = SqlTraits.get_trait_map(idMgr, firstname='Paulle', middle='', lastname='Smithy',suffix='',  street='22 Victor Rd', otherDesignation='', city='Vermont South', state='Vic', postcode='3133', country='Au',
	dobDay=20, dobMonth=11, dobYear=1952, sex='M', phoneCountryCode='65', phoneNumber='0394445555')

	profile2 = trait_map_to_profile(map)

	idList3 = idMgr.find_or_register_ids([profile, profile2])
	global profile_id, profile2_id
	profile_id = idList3[0]
	profile2_id = idList3[1]

	idList4 = idMgr.find_or_register_ids([profile, profile2])
	#print idList3
	#print idList4
	idList3.sort()


	idList4.sort()
	for label, list in [ ("first", idList3), ("second", idList4) ]:
		print "id list returned by ", label, " call of find_or_register_ids(profile, profile2) is", list

	if ( idList3==idList4):
		print "PASS: find_or_create_ids() is repeatable for a sequence of 2 profiles, returning the same id set"
	if idList3 > 2:
		print "INTEGRITY problem: there are ", max(len(idList3), len(idList4) ) , " identities with the same traits"
	else:
		if  idList3 <> idList4:
			print "Different id set returned after repeating call to find_or_create_ids()"
			print "idList3 = ", idList3
			print "idList4 = ", idList4
		print "FAIL** repeated operation of find_or_create_ids() failed"
		ask_continue()

def ask_continue():
	if not '-manual' in sys.argv:
		return
	if raw_input("keep going?")[0] in ['n','N','q']:
		sys.exit(0)


def _test_register_new_ids(idMgr):
	"""register_new_ids will register a given sequence of profiles and return
	a corresponding sequence of ids if successful.
	Exceptions include ProfileExists , where a profile is found to already
	match one already registered.
	"""
	global profile , profile2

	try:
		print "\nTESTING register_new_ids() check if existing profiles will be registered as new."
		idList5 = idMgr.register_new_ids( [profile, profile2])
		print "registered these ids", idList5
		print """FAIL: implementation of register_new_ids() does not check for ProfilesExist exception"""
		ask_continue()
	except:
		print "sys.exc_info is "
		for x in sys.exc_info():
			print x

		#print sys.exc_info()[0].__args
		if type(sys.exc_info()[0]) == PersonIdService.ProfilesExist:
			print "PASS: the correct exception ProfileExists was thrown."
		else:
			print sys.exc_info()[0], sys.exc_info()[1]
			print "PASS (?): exception was thrown, expected Exception is ProfileExists."
	try:
		newProfiles = []
		for n in xrange(0, 5):
			newProfiles.append( get_random_profile(idMgr))

		print "\nTESTING register_new_ids() with new random profiles."
		idList6 = idMgr.register_new_ids( newProfiles)
		print "id list returned = ", idList6

		#store last new id for test_register_these_ids to use
		global last_id
		idList6.sort()
		last_id = idList6[-1]

		if len(idList6 ) == len(newProfiles):
			print "PASS: the id count matches newProfiles"
	except:
		print sys.exc_info()[0], sys.exc_info()[1]
		traceback.print_tb(sys.exc_info()[2])
		print "FAIL: register_new_ids() failed to register random ids. "
		ask_continue()
		if 'debug' in sys.argv:
			sys.exit(0)

def _test_register_these_ids(idMgr):
	"""register_these_ids passes in a sequence of TaggedProfile(s) ,
	which already have ids specified.( Useful ? when register_new_ids()
	will register new profiles and return the ids ?)


	Anyway, firstly test that the function checks the ids are new,
	then test if the operation succeeds when ids are new."""
	print "\nTESTING register_these_ids with old profiles"
	global profile, profile2
	#global profile_id, profile2_id
	global profile_id, profile2_id
	global debug

	tp = PersonIdService.TaggedProfile(profile_id, profile)

	tp2 = PersonIdService.TaggedProfile( profile2_id, profile2)

	if debug:
		print tp.__dict__
		print tp2.__dict__

	try:
		idMgr.register_these_ids([tp, tp2])
	except:
		if type(sys.exc_info()[0]) == PersonIdService.IdsExist:
			print "PASS: register_these_ids() throws IdsExist when existing profiles with valid ids are registered"
		else:
			print "?PASS: exception should by IdsExist"
			print type(sys.exc_info()[0])
			print sys.exc_info()[0] , sys.exc_info()[1]
			traceback.print_tb(sys.exc_info()[2])

	print "\nTESTING register_these_ids with new profiles and new ids"
	# use the last_id stored by _test_register_new_ids()
	global last_id
	id = int(last_id)
	id += 1

	#the id is a string,  not an int
	sid = str(id)
	tp = PersonIdService.TaggedProfile(sid, get_random_profile(idMgr))

	id += 1
	sid = str(id)
	tp2 = PersonIdService.TaggedProfile(sid, get_random_profile(idMgr))


	if debug:
		print tp.__dict__
		print tp2.__dict__

	try:
		idMgr.register_these_ids([tp, tp2])
		print "PASS: succeeded in registering random profiles with new ids"
	except:
		print "FAIL: "
		print sys.exc_info()[0], sys.exc_info()[1]
		traceback.print_tb(sys.exc_info()[2])
		ask_continue()
	# for _test_merge_ids to use
	last_id =sid
	print "last_id was set to ", sid

def _test_merge_ids(idMgr):
	print"""\nTESTING pre-requisite setup for testing merge_ids():
	using
		register_these_ids( [tagged_profiles])
	and
		[ids] = find_or_register_ids([profiles] )
	"""
	n_ids = 5

	# create random TaggedProfiles with new ids
	global last_id

	id = int(last_id)
	print "getting last id ", id
	tp_list = [] # holds to new tagged profiles
	p_list = [] # holds the profile info without the id tag.
	for i in xrange(1, n_ids):
		id += 1
		sid = str(id)
		tp = PersonIdService.TaggedProfile(sid, get_random_profile(idMgr))
		tp_list.append(tp)
		p_list.append(tp.profile)


	idMgr.register_these_ids(tp_list)

	idList = idMgr.find_or_register_ids( p_list )
	idList.sort()
	tp_idList = [ tp.id for tp in tp_list]
	if idList == tp_idList:
		print "PASS 1: find_or_register_ids() found profiles registered by register_these_ids()"
	else:
		print "FAIL: reasons? random profile matches another id"
		print "find_or_register_ids() returned", idList
		print "ids of tagged profiles were",  tp_idList

	print"\nTESTING merge_ids() using recently construct tagged_profile sequence: the last tagged_profile's id will be the preferred id for the other profiles."
	global deactivated_ids
	deactivated_ids = []
	ms_list = []
	for tp in tp_list[0:-1]:
		ms = PersonIdService.MergeStruct(tp.id, sid)
		ms_list.append(ms)

	result = idMgr.merge_ids(ms_list)

	print "AFTER MERGE: "
	for idInfo in result:
		print idInfo, idInfo.__dict__

	if filter(lambda(idInfo): idInfo.preferred_id == sid, result) == result:
		print "PASS: all preferred ids refer to ", sid


	deactivated_ids = [ idInfo.id for idInfo in result]
	deactivated_ids.sort()

	requested_merge_ids = [ tp.id for tp in tp_list[0:-1] ]

	requested_merge_ids.sort()

	if deactivated_ids == requested_merge_ids:
		print "PASS: the deactivated ids returned were the requested merge ids"

	# now use sequential_access to verify

	print "\nTESTING using sequential access to verify"

	specTraits = get_ALL_TRAITS_SpecifiedTraits()
	state =find_id_state_like("DEACTIV")

	print "USING state=", state
	all_deactive_tagged_profiles = idMgr._get_sequential_access().get_all_ids_by_state(specTraits, [state])
	all_deactive_ids = [ p.id for p in all_deactive_tagged_profiles]
	all_deactive_ids.sort()
	not_found = 0
	not_found_id = []
	for id in deactivated_ids:
		if id not in all_deactive_ids:
			not_found = 1
			not_found_id.append(id)

	if not_found:
		print "FAIL: the following ids were supposed to be in the deactivated all list", not_found_id
		ask_continue()
		print "THE sequential access list was ", all_deactive_ids
	else:
		print "PASS: merge_ids(", deactivated_ids, ")"
		print "all deactivated ids were found IN id list returned by sequential_access.get_all_ids_by_state( ALL_TRAITS, [DEACTIVATED] )"




def _test_unmerge_ids(idMgr):
	global deactivated_ids
	print "\nTESTING unmerge_ids() : attempting to reactivate", deactivated_ids
	idInfos = idMgr.unmerge_ids(deactivated_ids)
	n = len(deactivated_ids)
	for idInfo in idInfos:
		if str(idInfo.state) == "PERMANENT" and idInfo.id in deactivated_ids:
			n = n -1
	if debug:
		for idInfo in idInfos:
			print idInfo.__dict__
	if n == 0:
		print "PASS: All deactivated ids were found in returned idInfo list, and state was marked as PERMANENT."

	print "TESTING unmerge_ids(): using sequential_access.get_all_ids_by_state()"
	try:
		sxs = idMgr._get_sequential_access()
		specTraits = get_ALL_TRAITS_SpecifiedTraits()
		state =find_id_state_like("PERMANENT")
		permanent_tagged_profiles = sxs.get_all_ids_by_state( specTraits, [state])
		permanent_ids = [ tp.id for tp in permanent_tagged_profiles]

		if filter( lambda(x): x not in permanent_ids, deactivated_ids) == []:
			print "PASS: all previously deactivated ids found in permanent_ids"
		state2 =   find_id_state_like("DEACTIV")
		deactivated_tagged_profiles = sxs.get_all_ids_by_state(specTraits, [state2] )
		current_deactivated_ids = [tp.id for tp in deactivated_tagged_profiles ]
		if  filter( lambda(x): x in current_deactivated_ids, deactivated_ids) == []:
			print "PASS: all previously deactivated ids were not found in current deactivated ids"





	except:
		print "FAILED: "
		print sys.exc_info()[0], sys.exc_info()[1]
		traceback.print_tb(sys.exc_info()[2])
if __name__== "__main__":
	test()
