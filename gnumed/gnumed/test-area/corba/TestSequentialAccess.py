import PersonIdService
import omniORB
import CosNaming
import sys
from PersonIdTestUtils import *
from PlainConnectionProvider import *

debug = 0

def test():
	global debug
	debug = "-debug" in sys.argv

	if "-gnumed" in sys.argv: path = "gnumed"
	else: path = None

        """Test the methods of the sequential_access identification component"""
	from ResolveIdComponent import IDComponentResolver
        resolver = IDComponentResolver()
        ids = resolver.getIdentificationComponent(path)
        sxs = ids._get_sequential_access()
	print "**************** TESTING SEQUENTIAL ACCESS"
	print "sequential_access methods are:"
        _test_seq_access_id_count_per_state(sxs)

        _test_seq_access_get_all_ids_by_state(sxs)


	_test_seq_access_get_first_ids(sxs)

        _test_seq_access_get_last_ids(sxs)

        _test_seq_access_get_next_ids(sxs)

        _test_seq_access_get_previous_ids(sxs)

def _test_seq_access_id_count_per_state(sxs):
	""" parameter sxs: a sequential_access component.
	This method iterates through the known states as specified by
	PersonIdService.IdState , and counts the identities with that state.
	Then compares with the count when all the states are passed
	in as a complete list.
	Method Tested:
		sxs.id_count_per_state( list of filtering states)
	@see:
	 the enum IdState in the PersonIdService.idl, for the
	possible id states: should be (as str(state) )  UNKNOWN, PERMANENT, TEMPORARY ..."""


	print "Valid IdStates are ", PersonIdService.IdState._items

	print"\nTESTING id_count_per_state( list_of_states)"
	total = 0
	for state in PersonIdService.IdState._items:
		list = [ state ]
		n =  sxs.id_count_per_state(list)
		print "[state] is ", list, " id count per  state is ", n
		total =total + n

	print "\nTESTING id_count_per_state( list_of_all_states)"
	otherTotal = sxs.id_count_per_state(PersonIdService.IdState._items)

	print "individual state total=", total, ", list of states total=", otherTotal
	global total_id_count
	total_id_count = otherTotal

	if total == otherTotal:
		print "PASS: Count Correct"
	else:
		print "FAIL? total count does not balance"

def _test_seq_access_get_all_ids_by_state(sxs):
	"""
	Param:	sxs , a sequential_access component
	Purpose: Test the sequential_access component method
		get_all_ids_by_state( in SpecifiedTraits traits_requested,
				      in IdStateSeq states_of_interest)
	"""
	print "\nTESTING sequential_access.get_all_ids_by_state"
	spec = PersonIdService.SpecifiedTraits(PersonIdService.HowManyTraits._items[2], [])
	spec2 = PersonIdService.SpecifiedTraits("ALL_TRAITS", [])
	print "spec = SpecifiedTraits(HowManyTraits[2], []): ", spec
	print "spec2 = SpecifiedTraits('ALL_TRAITS', []) ", spec2
	print " test spec==spec2 : ? ",spec == spec2
	print "str(spec._d) == str(spec2._d) ? ",str(spec._d) == str(spec2._d)

	allStates = PersonIdService.IdState._items

	result = sxs.get_all_ids_by_state( spec , allStates)

	print "spec got back a sequence of length", len(result), ", the first item is ", result[0]



	if debug:
		output_tagged_profile_sequence( result)

	print "tagged_profiles retrieved = ", len(result)

	global total_id_count
	if len(result) == total_id_count:
		print "PASS: number of ids retrieved is equal to count_id_per_state(all states) "

	if len(result) > 0:
		print "SpecifiedTraits with _d attribute as HowManyTraits[2] succeeded"
	else:
		print "unsure if SpecifiedTraits._d = HowManyTraits[2] succeeded as no tagged_profiles retrieved"

	try:
		result2 = sxs.get_all_ids_by_state(spec2, allStates)
		if len(result2) == len(result) :
			print "spec2 retrieved equivalent number of tagged profiles"
			print "this implies that SpecifiedTraits._d can be a string"

	except:
		print [str(x) for x in sys.exc_info() ]
		print "spec2 failed. Cannot use a string for SpecifiedTraits._d"

	print "\nTESTING HowManyTraits[1] 'SOME_TRAITS'"

	traitNames = ["HL7/PatientName", "HL7/DateTimeofBirth", "HL7/PatientAddress"]
	print "Using limited traits = ", traitNames

	spec3 = PersonIdService.SpecifiedTraits(PersonIdService.HowManyTraits._items[1], traitNames)

	result3 = sxs.get_all_ids_by_state(spec3, allStates)

	print """SpecifiedTrait(HowManyTraits._items[1], ["HL7/PatientName", "HL7/DateTimeofBirth", "HL7/PatientAddress"]) retrieved """, len(result3)

	if len(result) == len(result3):
		print "PASS: spec3 succeeded for number of tagged profiles. Expected result length same for ALL_TRAITS and SOME_TRAITS"



	atLeastOne = 0
	count= 0
	for t_profile in result3:
		traits = t_profile.profile
		if (len (traits) == len(traitNames)):
			atLeastOne = 1
			count = count + 1
		else:
			print
			print "a profile does not have the expected number of traits , with only", len(traits), " traits"
			if debug:
				output_tagged_profile(t_profile)

	print
	if atLeastOne:
		print "At Least one profile had the expected number of traits"

	print count , " profiles had the expected number of traits."

	if count == len(result3):
		print "all retrieved profiles had the required number of traits"

	

	print "\n\t Testing get_all_ids_by_state with specifiedTraits with HowManyTraits[0] 'NONE_TRAITS'"
	spec4 = PersonIdService.SpecifiedTraits(PersonIdService.HowManyTraits._items[0], [])
	try:
		result4 = sxs.get_all_ids_by_state(spec4, allStates)
		if len(result4) == len(result):
			print "NONE_TRAITS returned some number of tagged_profiles"
			if debug :
				output_tagged_profile_sequence(result4)
	except:
		print sys.exc_info()[0]
		print "NONE_TRAITS failed"
	
def _test_seq_access_get_first_ids(sxs):
	_test_seq_access_callback( sxs, sxs.get_first_ids)

def _test_seq_access_get_last_ids(sxs):
	_test_seq_access_callback( sxs, sxs.get_last_ids)

def _test_seq_access_get_next_ids(sxs):
	_test_seq_access_subsequence_ids_callback(sxs, sxs.get_next_ids)

def _test_seq_access_get_previous_ids(sxs):
	""" This detects a bug in the open-emeds implementation,
	in file SequentialAccessImpl.java line 520,
	'
	while (ids.hasMoreElements() && i < Math.min(n, how_many)) {
	                Identity_ tmp_id = (Identity_) ids.nextElement();
				...
	'
	ids is an enumeration of all ids less than the parameter id.
	The enumeration needs to be traversed from last element backwards.
	"""

	_test_seq_access_subsequence_ids_callback(sxs, sxs.get_previous_ids)

def __get_specifiedTraits_some_traits( traitNames = ["HL7/PatientName", "HL7/DateTimeofBirth", "HL7/PatientAddress"]):
	print "Using limited traits = ", traitNames
	return PersonIdService.SpecifiedTraits( PersonIdService.HowManyTraits._items[1], traitNames)

def __get_specifiedTraits_all_traits():
	howManyTraits = PersonIdService.HowManyTraits._items[2]
	return PersonIdService.SpecifiedTraits(howManyTraits, [])

def __get_permanent_state_list():
	states = [y for y in filter( lambda x: str(x) == "PERMANENT", PersonIdService.IdState._items) ]
	print "states", states

	return states

def _test_seq_access_callback(sxs, callback):
	print "** \nTESTING sequential_access with SOME_TRAITS and looking for PERMANENT state in identities", callback.__name__

	states = __get_permanent_state_list() 

	specifiedTraits = __get_specifiedTraits_some_traits()

	__iterate_get_ids(sxs, states, specifiedTraits, callback)

	print "\nTESTING ", callback.__name__, " with ALL_TRAITS in specifiedTraits"

	specifiedTraits = __get_specifiedTraits_all_traits()

	__iterate_get_ids(sxs, states, specifiedTraits, callback)



def __iterate_get_ids(sxs,  states, specifiedTraits, callback):

	total = sxs.id_count_per_state( states)
	iterations = min(5, total / 2)
	step = total / iterations
	for n in xrange( 1, total, step):
		result = callback( n ,  states, specifiedTraits)
		if len(result) == 0:
			print callback.__name__," with ", n , "as first parameter, got back a zero result. ? FAILED"
		else:
			if len(result) == n:
				print "PASS: ", callback.__name__, "got back ", n ,"results, which = n"
			else:
				print callback.__name__, " got back a lesser  len(results)=", len(result), " expected ", n
			print "the trait count range is",get_profile_sequence_trait_count_range(result)
		if debug:
			output_tagged_profile_sequence(result)


def	_test_seq_access_subsequence_ids_callback(sxs, callback):
	print "** \nTESTING sequential_access", callback.__name__

	specifiedTraits = __get_specifiedTraits_some_traits()
	states = __get_permanent_state_list()
	__iterate_get_subseq_ids(sxs, states, specifiedTraits, callback)


def __iterate_get_subseq_ids(sxs, states, specifiedTraits, callback):

	total = sxs.id_count_per_state( states)
	iterations = min(5, total/ 2)
	step = total / iterations
	midstep = step/2 + 1
	for n in xrange( 1, total, step):
		#get the first_ids and use the last element to get start of subsequence
		tagged_profiles = sxs.get_first_ids( min(n   + midstep, total), states, specifiedTraits)
		#assert( len (tagged_profiles ) == 1)
		id = tagged_profiles[-1].id
		if debug:
			print "result of get_first_ids( min(",  n ,"+", midstep, ",", total, "), ", states, ", ", specifiedTraits ,")"
			print "for _iterate_get_subseq_ids: using last tagged profile id from ", [ tp.id for tp in tagged_profiles ]
			print "calling ", callback.__name__, " with parameter , start id =", id,", length=", midstep,",", states, specifiedTraits

		result = callback(id, midstep, states, specifiedTraits)
		if (len(result) == 0):
			print "FAIL:",callback.__name__, " got back a zero result."
		else:
			if len(result) == midstep:
				print "PASS: ", callback.__name__, "got back result = n"
			else:
				print "PASS (?):", callback.__name__, "  with a non-zero result", len(result), " expected ", midstep

			if debug:
				print "id param was ", id , "the ids retrieved were ", [x.id for x in result]
				#__output_tagged_profile_sequence(result)
			check_unique( [x.id for x in result] )


if __name__ == "__main__":
	test()
