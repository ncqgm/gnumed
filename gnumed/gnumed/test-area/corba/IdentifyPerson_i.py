import PersonIdService__POA

import CORBA
import CosNaming
import ResolveIdComponent
from StartIdentificationComponent import StartIdentificationComponent
import PersonIdTraits
from PlainConnectionProvider import *
import HL7Version2_3

import threading, thread, traceback, time

from  PersonIdTestUtils import *
from SqlTraits import *
import string
import difflib

class IdentifyPerson_i(PersonIdService__POA.IdentifyPerson, StartIdentificationComponent):
	"""an implementation of identifyPerson , using gnumed for a backend.
	This component has the main searching functionaliy , which uses
	weights for traits, and threshold confidence levels.
	The adhoc algorithm here was to use a default weight map as much
	as possible e.g. home phone > datetimeofbirth > address number > lastnames > firstnames > gender; a weight threshold determines if attributes fall into a grouping of OR substring conditions (meaning these attributes are important ) or into an AND set of conditions ( meaning these attributes are weak selectors and depend on the other conditions being true) ; and for the rows selected,  to  calculate the profile confidence level as the
	weighted  average of length matches ,
	 multiplied by
	the number of exact matches ( as 2 or more EXACT matches are worth quite a lot). """

	def __init__(self, dsn=None, ProviderClass = PlainConnectionProvider, limit = MAX_TRAITS_RETURNED ):
		self.connector = ProviderClass(dsn)
		self.limit = limit
		self._optimize_calltime_by_sql_prepare()

	def _optimize_calltime_by_sql_prepare(self):
		con = self.connector.getConnection()
		self.preparedStatements = {}


	def find_candidates(self,
		traitSelectorSeq ,
		IdStateSeq,
		confidence_threshold,
		sequence_max,
		iterator_max,
		specifiedTraits ):
		"""
	The idl specification is:
	void find_candidates(
           in TraitSelectorSeq profile_selector,
           in IdStateSeq states_of_interest,
           in float confidence_threshold,
           in unsigned long sequence_max,
           in unsigned long iterator_max,
           in SpecifiedTraits traits_requested,
           out CandidateSeq returned_sequence,
           out CandidateIterator returned_iterator )

	parameters:
		TraitSelectorSeq = [traitSelector]
		where	a TraitSelector is
	"
		struct TraitSelector {
		PersonIdService::Trait trait;
		float weight;
	 	};
	"
	as in the spec doc. The spec doc says also:
	"

The `weight' field is a hint from the client on how much preference it thinks the server
should give to each profile passed in for determining matching confidences. It may be
thought of as the confidence the client has in each trait of the profile selector.
The weight must be between 0.0 and 1.0. The weights are relative measures such that an
exact match on a trait with weight = 0.5 results in twice the increase in confidence than an
exact match on a trait with weight = 0.25.
A server implementation can ignore the weight field hint if it chooses. Using it is
considered a Quality of Service (QOS) issue that is not standardized. The semantics here
are just a way to define the measuring stick but does not require implementations to prove
adherence. This is in part because fuzzy semantics cannot be measured.

	" , i.e. 'weight' not specified. So make it string matching , 1 = 100% string match .2 = 20% string match.


	in python idl, the out parameters are returned as a list.
	e.g. returns  [ candidateSeq, candidateIterator ]
	if len (candidates) > sequence_max, then
		candidateIterator = [ rest of candidates upto iterator_max ]

	Implementation issue: uses a map of prepared statement hash names to prepare
	queries and cache their plans. This speeds up the query, once it is first executed.
		"""

		field_weighted_value_map = get_field_weighted_value_map(traitSelectorSeq, confidence_threshold)

		if debug:
			print "field_weighted_value_map = ",field_weighted_value_map
		and_frags = []
		or_frags = []
		i = 1

		# this holds the values of parameters to pass to a prepared statement
		values = []

		#this is to hold those fields in field_list that have non-empty values
		used_fields = []
		for field, (value, weight) in field_weighted_value_map.items():
			if weight < 0.05:
				continue

			frag = "strpos(%s, $%d) > 0" % (field, i )
			if debug:
				print "weight , threshold ", weight, SqlTraits.weight_OR_threshold
			if weight < confidence_threshold:
				and_frags.append(frag)
			else:
				or_frags.append(frag)
			i = i + 1
			funclist = SqlTraits.idPerson_field_filters.get(field,[])
			for f in funclist:
				value = f(value)

			if debug:
				print "field = ", value
			values.append(value)
			used_fields.append(field)

		#filtered_selectProfile =get_tagged_profile_from_row( values, [ (f) for f in used_fields ])
		#print "After filtering ", brief_profile(filtered_selectProfile)
		or_part = ' or '.join(or_frags)
		and_part = ' and '.join(and_frags)
		if or_part == '':
			or_part = 'true'
		if and_part == '':
			and_part = 'true'


		condition = ' '.join( ['(',or_part,') and ', and_part ])
		frag_count = len(or_frags) + len(and_frags)

		field_list, traits = get_field_list_and_traitname_list(specifiedTraits)

		stmt = "select %s from (%s) as i where %s order by id desc" % ( ",".join(field_list), sql_traits, condition  )

		con = self.connector.getConnection()
		cursor = con.cursor()

		#use a hash to make unique a prepared statements name
		h = abs(hash(condition ) )

		# look for the prepared_statement and query for the prep statement in a cache
		prep_stmt, qry_stmt = self.preparedStatements.get(h, (None, None))
		# if not in cache, create the prepares statement and map it by it's prepared statement hash name. the hash name is derived from the non-empty field list.
		if prep_stmt == None:
			abbrev = [ x[0:2] for x in field_list]


			prep_stmt = "prepare find_traits_%d(%s) as %s" % ( h, ','.join( ['text'] * frag_count), stmt)
			qry_stmt ="execute find_traits_%d( %s)" % ( h , ', '.join(["'%s'"] * frag_count) )
			try:
				cursor.execute(prep_stmt)
			except:
				print "This prepared_stmt may exist already", prep_stmt
			self.preparedStatements[h] = (prep_stmt, qry_stmt)

		# execute the predermined query for the prepared statement.
		cursor.execute(qry_stmt % tuple(values) )

		#stmt = "select %s from (%s) as i where %s" % ( ",".join(field_list), sql_traits, " or ".join(frags) )

		result = cursor.fetchall()

		print "number of initial candidates", len(result)
		candidateSeq  , confidences = [], []
		for r in result:
			tprofile = get_tagged_profile_from_row( r, cursor.description )
		#	if confidence_threshold > 0.1:
		#		confidence, full_match_ratio = calculate_confidence( tprofile.profile, traitSelectorSeq)
		#		confidences.append( (confidence, full_match_ratio ))
		#		if confidence < confidence_threshold and full_match_ratio -  confidence_threshold > 0.1:
		#			continue
			confidence = calculate_confidence(tprofile.profile, traitSelectorSeq)
			if confidence < confidence_threshold:
				continue
			candidate = PersonIdService.Candidate(tprofile.id, confidence , tprofile.profile)
			candidateSeq.append(candidate)
			if len(candidateSeq) > sequence_max:
				break
		print "number of screened candidates", len(candidateSeq)

		if '-stats' in sys.argv:
			print "The confidences found were : " ,[ (c,m) for c,m in confidences]

		return candidateSeq, None

global show_confidence
show_confidence = "-debug" in sys.argv or "-confidence" in sys.argv or "-stats" in sys.argv

def calculate_confidence( profile, traitSelectorSeq):

	if len(profile) == 0:
		return 0.0
	map =  dict (  [ (tSel.trait.name, tSel) for tSel in traitSelectorSeq] )
	weightings = []
	full_matches = 0
	total_data_len = 1
	total_weight = 0.0
	for  trait in profile:
		if map.has_key(trait.name):
			tSelector = map[trait.name]
			v1, v2 =  tSelector.trait.value.value().strip('^ ') , trait.value.value().strip('^ ')
			matches =  difflib.get_close_matches(v1,[v2], 1, tSelector.weight)
			print "Matches for ", trait.name,"weight", tSelector.weight, " are ", matches
			if matches <> None and matches <> []:
				if v1 == v2:
					full_matches += 1
				weightings.append(tSelector.weight * len(v1) )
				total_weight += tSelector.weight
			total_data_len += tSelector.weight * len(v2)
	if len(weightings) == 0: return 0.05
	def sum(x,y): return x + y
	tot = reduce( sum, weightings)
	if total_weight < 0.05 :
		total_weight = 1.0
 	confidence = tot /total_data_len #* full_matches ? don't need full_matches because accounted for length ratio .
	if show_confidence:
		print "\n***********\nconfidence for :"
		print "\tSelector=", brief_selector(traitSelectorSeq)
		print "\tCandidate=", brief_profile(profile)
		print "\t\tconfidence = ", confidence,"\n************\n"
	#return full_matches / len(weightings)
	return confidence


	def _find_candidates_1 (self,
		traitSelectorSeq ,
		IdStateSeq,
		confidence_threshold,
		sequence_max,
		iterator_max,
		specifiedTraits ):
		"""This implementation of find candidates does :
		1) match
		"""
		pass


