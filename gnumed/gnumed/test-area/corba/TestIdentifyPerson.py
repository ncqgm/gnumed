import PersonIdService
import ResolveIdComponent
import CORBA
import sys, string, random, traceback
from PersonIdTestUtils import *
import SqlTraits
import HL7Version2_3
debug = 0
last_id = 0

def test():
	global debug
	debug = "-debug" in sys.argv

	if "-gnumed" in sys.argv: path = "gnumed"
	else: path = None

	resolver = ResolveIdComponent.IDComponentResolver()
	ic = resolver.getIdentificationComponent(path)

	idPerson = ic._get_identify_person()


	init_trait_spec(ic)

 	_test_find_candidates(idPerson)


def _test_find_candidates(idp):

	global specifiedAllTraits
	specifiedAllTraits =PersonIdService.SpecifiedTraits( PersonIdService.ALL_TRAITS, [] )
	hl7 = HL7Version2_3
	specifiedSomeTraits= PersonIdService.SpecifiedTraits(PersonIdService.SOME_TRAITS, [hl7.PATIENT_NAME, hl7.PATIENT_ADDRESS, hl7.DATE_TIME_OF_BIRTH ])

	for specTraits in [ specifiedSomeTraits, specifiedAllTraits ]:
		_test_find_candidates_spec(idp, specTraits)


def _test_find_candidates_spec(idp , specTraits):
	n = 20
	test_weight = 0.2
	test_weight_change = ( 1 - test_weight) / n
	seqacc = idp._get_sequential_access()

	ids = seqacc.get_first_ids( n, [ PersonIdService.PERMANENT] , specifiedAllTraits )

	if debug:
		print "Using Test data from sequential_access.get_first_ids(",n," ,...)"

	for tprofile in ids:

		if debug:
			print "converting tagged ids", tprofile.id
			for t in tprofile.profile:
				print t.name, t.value.value(), t.value.typecode().kind() == CORBA.tk_string

		traitSelectSeq = getTraitSelectorSeqFromProfile( tprofile.profile, specTraits, test_weight)
		test_weight += test_weight_change
		if debug:
			print "USING TraitSelectSeq:"
			for selector in traitSelectSeq:
				print selector.trait.name, selector.trait.value.value(), selector.weight

		confidence_threshold = 0.9

		candidates, candidateIterator = idp.find_candidates(traitSelectSeq, [PersonIdService.PERMANENT], confidence_threshold, n/2, n/2, specTraits  )

		if debug:
			print "got back candidates :"
			for c in candidates:
				print  c.id, [ t.value.value() for t in c.profile]

		for candidate in candidates:
			if candidate.id == tprofile.id:
				print "PASS, find_candidates() found a matching candidate with the same id ", candidate.id , " using specifiedTraits", specTraits
			if get_unmatched_traits(  candidate, tprofile) == []:
				if debug:
					print "find_candidates() found a candidate profile with matching profile"
				if candidate.id == tprofile.id:
					print "PASS, both profile and id match."
				else:
					if debug:
						print "possibly a DUPLICATE profile, it has a different id =", candidate.id


		if candidateIterator == None:
			continue
		print "The candidate iterator = ", candidateIterator
		n = 1
		hasNext = 1
		while(hasNext) :
			print "candidate iterator has max_left() = ", candidateIterator.max_left()

			hasNext, candidateSeq = candidateIterator.next_n(n)

			print "got back ", len(candidateSeq), "candidates using the candidateIterator.next_n( ",n,")"
			n = n + 1
			for c in candidateSeq:
				if get_unmatched_traits(c, tprofile) ==[] :
					print "PASS: candidateIterator returned a candidate with matching traits"
				else:
					print "FAIL: the candidate returned by the candidateIterator did not match in traits."

		candidateIterator.destroy()


def get_unmatched_traits( candidate, tprofile):
	"""matches the profile attribute of candidate and a tagged profile,
	and returns any unmatched traits in the candidate """
	return	filter(  lambda(t): find_trait_in_profile(t.name, tprofile.profile) == None or find_trait_in_profile(t.name, tprofile.profile).value.value() <> t.value.value() , candidate.profile )



def getTraitSelectorSeqFromProfile( profile, specifiedTraits, defaultWeight = 0.5 ):
	"converts a profile into a traitSelectorSequence based on the SpecifiedTraits"
	if specifiedTraits._d == PersonIdService.ALL_TRAITS:
		traitnames = SqlTraits.get_supported_trait_names()
	else:
		traitnames = specifiedTraits._v

	return [ PersonIdService.TraitSelector( trait, get_weight_for_trait(trait, defaultWeight, SqlTraits.default_weight_map) ) for trait in filter( lambda(t): t.name in traitnames and t.value.typecode().kind() == CORBA.tk_string and t.value.value().strip() <> '' , profile ) ]

def get_weight_for_trait(trait,default_weight, weight_map):
	if trait.value.typecode().kind() <> CORBA.tk_string:
		return 0.0
	if trait.value.value().strip() == '':
		return 0.0
	if weight_map.has_key(trait.name):
		return weight_map[trait.name]
	return default_weight	

if __name__ == "__main__":
	test()
