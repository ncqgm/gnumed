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

class SequentialAccess_i(PersonIdService__POA.SequentialAccess, StartIdentificationComponent):

	def __init__(self, dsn=None, ProviderClass = PlainConnectionProvider, limit = MAX_TRAITS_RETURNED ):
		self.connector = ProviderClass(dsn)
		self.limit = limit
		self._optimize_calltime_by_sql_prepare()

	def _optimize_calltime_by_sql_prepare(self):
		con = self.connector.getConnection()

		con.execute("prepare find_traits( int, int, int) as select * from (%s) as i where id >= $1 order by id limit  $2 offset $3" % sql_traits)

		con.execute("prepare find_all_traits(int, int) as select * from (%s) as i where id >= $1 order by id limit all offset $2" % sql_traits)

	def id_count_per_state( self, states):
		# gnumed doesn't have the identity state concept ?
		if PersonIdService.PERMANENT not in states:
			return 0
		conn = self.connector.getConnection()
		cursor = conn.cursor()
		cursor.execute("select count(id) from identity")
		[count] = cursor.fetchone()
		if debug:
			print "count = ", count, type(count)
		return int(count)

	def get_all_ids_by_state( self, specifiedTraits, idStateSeq):
		return self._get_id_sequence( specifiedTraits, idStateSeq )

	def get_first_ids( self, n, states_of_interest, specifiedTraits):
		return  self._get_id_sequence( specifiedTraits, states_of_interest,  n )

	def get_last_ids( self, n, states_of_interest, specifiedTraits):
		count = self.id_count_per_state(states_of_interest)
		offset = count - n
		return  self._get_id_sequence( specifiedTraits, states_of_interest, n, offset )

	def get_next_ids(self, id, n, states_of_interest, specifiedTraits):
		_check_id_type(id)

		return  self._get_id_sequence( specifiedTraits, states_of_interest, n, 0,  id )

	def get_previous_ids( self, id, n, states_of_interest, specifiedTraits):
		_check_id_type(id)
		conn = self.connector.getConnection()
		cursor = conn.cursor()
		cursor.execute("select count(id) from identity  where id <= %s" %  id )
		[count] = cursor.fetchone()
		offset = count - n
		if offset < 0:
			n = count
			offset = 0

		return self._get_id_sequence( specifiedTraits, states_of_interest,  n, offset)


	def _get_id_sequence( self, specifiedTraits, idStateSeq,    limit='ALL' , offset = 0,  iid = 0):
		trace_caller()

		if PersonIdService.PERMANENT not in idStateSeq:
			return []

		field_list, traits = get_field_list_and_traitname_list(specifiedTraits)

		if self.id_count_per_state(idStateSeq) * len(traits) > self.limit:
			raise PersonIdService.TooMany(self.limit / len(supported_traits) )


		conn = self.connector.getConnection()
		cursor = conn.cursor()
		#cursor.execute("select %s from (%s ) as traits  where traits.id >= %s order by traits.id limit  %s offset %d " % ( ','.join(field_list), sql_traits , iid,  str(limit), offset  ) )
		if limit == 'ALL':
			cursor.execute("execute find_all_traits(%s, %d)" % (iid, offset) )
		else:
			cursor.execute("execute find_traits(%s, %s, %d)" % (iid, str(limit), offset) )
		result = cursor.fetchall()
		return get_tagged_profiles_from_cursor_result( result, cursor.description)


def _check_id_type(id):
	try:
		id = long(id)
	except:
		raise PersonIdService.InvalidIds( id, [], 0)



#	def get_first_ids( self, n, states, specifiedTraits):
#		"""gets the first n ids found with the given idState and for the specifiedTraits.
#		returns a tagged_profile list"""
#
#		cursor = self.connector.getConnection().cursor()

#		cursor.execute(sql_traits)
#		try:
#			result = cursor.fetchmany(n)
#		except:
			#handle too many exception?
#			traceback.print_tb(sys.exc_info()[2])
#			raise PersonIdService.tooMany
#		return get_tagged_profiles_from_cursor_result( result, cursor.description)







