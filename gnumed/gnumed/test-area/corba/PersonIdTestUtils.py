import PersonIdService
import sys
import string
import CORBA
import HL7Version2_3
import PersonIdTraits
from SqlTraits import *
import SqlTraits
import inspect, traceback
global hl7
hl7 = HL7Version2_3

global spec, specMap
spec = None
specMap = None
global HOME_PHONE_TYPE, BUSINESS_PHONE_TYPE



global debug

debug = "-debug" in sys.argv

def init_trait_spec(idComponent):
	global spec, debug, specMap
	specMap = {}
	spec = idComponent._get_supported_traits()
	for tspec in spec:
		specMap[tspec.trait] = tspec
	if debug:
		for x in spec:
			print x.__dict__


def get_trait_map_nabsp( idComponent, n, a, b, s, p ):
	"""finds the keys that probably match the given attributes, and returns a map.
	"""
	if debug:
		print find_trait_name("PatientName")[0].trait
	map = {}
	traitSpecs = [
		(find_trait_name("PatientName")  , n),
		(find_trait_name("Address") , a),
		(find_trait_name("Birth") , b),
		(find_trait_name("Sex"), s),
		(find_trait_name("Home") , p )
	]
	for (t, v) in traitSpecs:
		if len(t) >= 1:
			name = t[0].trait
			map[name] = v
		else:
			print "failed to find attribute name for ", v

	return map

def trait_map_to_profile(map):
	"""changes a map of trait.name:trait.value  to a Profile (a sequence of PersonIdService.Trait objects).
	 """
	list = []
	for k,v in map.items():
		# N.B. the trait.value is a Any (which requires a typecode)
		if v == None:
			continue
		a = CORBA.Any( CORBA._tc_string, v)
		trait = PersonIdService.Trait(k,a)
		#print trait.__dict__
		list.append(trait)
	return list

def trait_map_to_trait_selector_seq( traitMap, confidence = 1.0):
	"""changes a map of traits to a traitSelector Sequence. TraitSelectors have a trait,
	and a float weight. 1.0 is the highest weight for the trait.
	Any blank trait map values will be removed.
	"""
	for k,v in traitMap.items():
		if v == None:
			del traitMap[k]

	traitSelectorSeq = []
	for k,v in traitMap.items():
		a = CORBA.Any(CORBA._tc_string, v)
		t = PersonIdService.Trait(k,a)
		tSelector = PersonIdService.TraitSelector(t, confidence)
		traitSelectorSeq.append(tSelector)
	return traitSelectorSeq


def find_trait_in_profile(n, profile):
	global debug
	#if debug :
	#	print "looking for ", n
	traitSpec = find_trait_name(n)[0]
	#if debug:
	#	print "Searching for ", traitSpec.trait
	for trait in profile:
		if trait.name == traitSpec.trait:
			return trait
	return None


def find_trait_name(n):
	"""returns a list of traitspec  matching the string name n.
		a traitspec.trait is the string name of a trait
		readonly, mandatory are some attributes.
	"""
	global spec, debug, specMap

	# profiling found find_trait_name() to be used quite a lot , so try to speed up
	# try to find trait in the trait spec map by matching n to a trait.name exactly
	traitSpec =  specMap.get(n, None)
	if traitSpec <> None:
		return [traitSpec]

	# else iterate through specs, and find a traitSpec.name which is superstring of n
	list =  filter( lambda traitSpec: string.find( traitSpec.trait,  n) >= 0 , spec)
	if debug:
		#print "spec is ", spec
		print "found specs for name ", n, " = ",[ x.__dict__ for x in list]
		if list == []:
			print n , " not found for specs", [x.__trait__ for x in spec]

	return list



def find_id_state_like(text):
	"""find a person IdState that matches the text phrase.
	"""

	[state] = filter( lambda(state): str(state).find(text) >= 0, PersonIdService.IdState._items)
	return state

def get_random_profile(idMgr):
	"""creates a random profile.
	"""
	import random
	r = random.Random()
	yr = 1900 + r.randint(0, 99)
	month = r.randint(1, 12)
	day = r.randint(1, 28)
	surname = get_random_surname()
	name = r.choice(["Jane", "Mary", "Susan", "Bob", "Tom", "Dick", "Harry"] )
	street_no = r.randint(1, 120)
	street = get_random_street()
#	city = r.choice(["Sydney", "Hong Kong", "Amsterdam", "Istanbul"])
#	state = r.choice(["Victoria", "Wales", "Yorkshire"])
#	postcode = r.randint(1000, 9000)
#	country = r.choice(["Erewhon", "Ylevol", "Yglu", "Ecarf"])
	city, state, postcode, country = get_random_location()
	phone = r.randint(111111, 999999)
	code = r.randint(10, 90)
	map = SqlTraits.get_trait_map(idMgr, name, '', surname,'',  str(street_no) +' '+ street,  '', city, state, str(postcode), country,
dobDay=day, dobMonth=month, dobYear=yr, sex="?", phoneCountryCode=str(code), phoneNumber=str(phone) )
	profile = trait_map_to_profile(map)
	if debug:
		print "\n\n ** RANDOM PROFILE = \n\t",[ t.value.value() for t in profile], "\n"
	return profile

def get_random_street():
	import random
	r = random.Random()
	street = r.choice(["Bell st", "Red rd", "Blue Ave", "Black Boulevard"])
	return street

def get_random_surname():
	import random
	r = random.Random()
	surname = random.choice(["Smith", "Jones", "Green", "Barnaby", "Williams", "McDonald" ])
	return surname

global test_locations
test_locations = []
def get_random_location():
	import random
	r = random.Random()

	global test_locations
	if test_locations == []:
		test_locations = load_test_locations()
	if debug:
		print "TEST locations are", test_locations

	import random
	r = random.Random()
	return r.choice(test_locations)

def load_test_locations():
	test_data = []
	f = open('testdata.conf')
	reading = 0
	country = 'AU'
	reading_country = 0
	for line in f:
		line = line.strip()

		if line == '[valid urb data]':
			reading = 1
			continue
		if line == '[country]':
			reading_country = 1
			continue

		if reading_country:
			if len(line) > 0:
				country = line
			continue
		if reading :

			if len(line) == 0 or line[0] == '#':
				continue
			toks = line.split(',')
			if len(toks) < 2:
				continue
			city, state, postcode = toks[0].strip(), '', toks[1].strip()
			test_data.append( (city, state, postcode, country) )
	f.close()

	if test_data == []:
		test_data= [
			('JERVIS BAY','NSW', 2540, 'AU'),
			('BARTON','NSW', 2600,'AU'),
			('ACTION', 'NSW',2601,'AU'),
			('AINSLIE','NSW', 2602,'AU'),
			('GARRAN', 'NSW',2605,'AU'),
			('BONDI JUNCTION', 'SA',1355,'AU'),
			('DOUBLE BAY', 'SA',1360,'AU'),
			('STRAWBERRY HILL','SA', 1420,'AU'),
			('ALEXANDRIA', 'SA',1435,'AU') ]

	return test_data

unique = []

def check_unique(val):
	global unique
	if val in unique:
		print  "WARNING: ", val, " has been seen before. FAIL?"
	unique.append(val)




def output_tagged_profile_sequence(result):
	if debug:

		print """
running this query:
	for profile in result:
		print "id = ",profile.id, "; profile = ",
			[ (x.name, x.value.__methods__, x.value.value()) for x in profile.profile]

"""
	for tagged_profile in result:
		output_tagged_profile(tagged_profile)


def output_tagged_profile(tagged_profile):
	print
	print "id = ",tagged_profile.id, "; profile = ", [ ("x.name=",x.name," x.value.__methods__=", x.value.__methods__, " x.value.value()=",x.value.value()) for x in tagged_profile.profile]

def print_brief_profile(profile):
	print "\n PROFILE:", [ t.value.value() for t in filter( lambda(t): t.name in [hl7.PATIENT_NAME, hl7.PATIENT_ADDRESS, hl7.DATE_TIME_OF_BIRTH], profile)],"\n"
	

def get_profile_sequence_trait_count_range(result):
	min = 1000
	max = 0

	for x in result:
		l= len(x.profile)
		if l < min:
			min =  l
		if l > max:
			max = l
	return (min, max)


def get_ALL_TRAITS_SpecifiedTraits():
	"""returns the ALL_TRAITS trait retrieval spec parameter.
	"""
	return get_specified_traits("ALL_TRAITS")

def get_specified_traits(howManyStr, traitNames = []):
	[howMany] = filter( lambda(x): str(x) == howManyStr, PersonIdService.HowManyTraits._items )

	return  PersonIdService.SpecifiedTraits(howMany, traitNames)


def get_specifiedTraits_some_traits( traitNames = [hl7.PATIENT_NAME, hl7.PATIENT_ADDRESS, hl7.DATE_TIME_OF_BIRTH, hl7.PHONE_NUMBER_HOME]):
	if debug:
		print "Using limited traits = ", traitNames
	return PersonIdService.SpecifiedTraits( PersonIdService.HowManyTraits._items[1], traitNames)

def get_specifiedTraits_all_traits():
	howManyTraits = PersonIdService.HowManyTraits._items[2]
	return PersonIdService.SpecifiedTraits(howManyTraits, [])


def getTraitSelectorSeqFromProfile( profile, specifiedTraits =PersonIdService.SpecifiedTraits(PersonIdService.ALL_TRAITS, []), defaultWeight = 0.2 ):
	"converts a profile into a traitSelectorSequence based on the SpecifiedTraits"
	if specifiedTraits._d == PersonIdService.ALL_TRAITS:
		traitnames = SqlTraits.get_supported_trait_names()
	else:
		traitnames = specifiedTraits._v

	tSelSeq = []
	for trait in filter( lambda(t): t.name in traitnames and t.value.typecode().kind() == CORBA.tk_string and t.value.value().strip() <> '' , profile ) :
		tSelSeq.append(PersonIdService.TraitSelector( trait, defaultWeight))

	return tSelSeq

def catchExceptions (method, *params):
	try:
		method(*params)
	except:
		e = sys.exc_info()
		print e[0], e[1]
		traceback.print_tb(e[2])

def trace_caller():
	if '-params' in sys.argv:
		s = inspect.stack()
		f = s[2]
		arginfo = inspect.getargvalues(f[0])

		argmap = {}
		for k,v in arginfo[3].items():
			if k in arginfo[0]:
				argmap[k] = v

		print s[1][3]," ** CALLED FROM", inspect.getframeinfo(f[0])[0:3], argmap
