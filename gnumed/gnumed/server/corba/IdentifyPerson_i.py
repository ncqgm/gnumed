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



class IdentifyPerson_i(PersonIdService__POA.IdentifyPerson, StartIdentificationComponent):
	"an implementation of identifyPerson , using gnumed for a backend"

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

		field_weighted_value_map = get_field_weighted_value_map(traitSelectorSeq)
		if debug:
			print "field_weighted_value_map = ",field_weighted_value_map
		frags = []
		i = 1

		# this holds the values of parameters to pass to a prepared statement
		values = []

		#this is to hold those fields in field_list that have non-empty values
		used_fields = []
		for field, (value, weight) in field_weighted_value_map.items():
			value = value.strip()
			if value == '':
				continue
			n = weight * len(value)
			value = value[0:1 + int(n)]
			frag = "substring(%s, 1, length($%d)  ) = $%d" % (field, i, i )
			frags.append(frag)
			i = i + 1
			values.append(value)
			used_fields.append(field)

		field_list, traits = get_field_list_and_traitname_list(specifiedTraits)

		stmt = "select %s from (%s) as i where %s" % ( ",".join(field_list), sql_traits, " or ".join(frags)  )

		con = self.connector.getConnection()
		cursor = con.cursor()

		#use a hash to make unique a prepared statements name
		h = str ( abs(hash('_'.join(used_fields) ) ) )

		# look for the prepared_statement and query for the prep statement in a cache
		prep_stmt, qry_stmt = self.preparedStatements.get(h, (None, None))
		# if not in cache, create the prepares statement and map it by it's prepared statement hash name. the hash name is derived from the non-empty field list.
		if prep_stmt == None:
			abbrev = [ x[0:2] for x in field_list]


			prep_stmt = "prepare find_traits_%s(%s) as %s" % ( h, ','.join( ['text'] * len(frags)), stmt)
			qry_stmt ="execute find_traits_%s( %s)" % ( h , ', '.join(["'%s'"] * len(frags) ) )
			try:
				cursor.execute(prep_stmt)
			except:
				print "This prepared_stmt may exist already", prep_stmt
			self.preparedStatements[h] = (prep_stmt, qry_stmt)

		# execute the predermined query for the prepared statement.
		cursor.execute(qry_stmt % tuple(values) )

		#stmt = "select %s from (%s) as i where %s" % ( ",".join(field_list), sql_traits, " or ".join(frags) )

		result = cursor.fetchmany(sequence_max)
		print "number of initial candidates", len(result)
		candidateSeq  = []
		for r in result:
			tprofile = get_tagged_profile_from_row( r, cursor.description )
			if confidence_threshold > 0.1:
				confidence = calculate_confidence( tprofile.profile, traitSelectorSeq)
				if confidence < confidence_threshold:
					continue
			candidate = PersonIdService.Candidate(tprofile.id, confidence, tprofile.profile)
			candidateSeq.append(candidate)

		print "number of screened candidates", len(candidateSeq)
		return candidateSeq, None


def calculate_confidence( profile, traitSelectorSeq):
	 return len(profile)/ len (traitSelectorSeq)







