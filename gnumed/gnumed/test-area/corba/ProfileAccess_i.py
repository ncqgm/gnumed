import PersonIdService__POA

import CORBA
import CosNaming
import ResolveIdComponent
from  PersonIdTestUtils import *
from PersonIdService import TraitSpec
import PersonIdTraits
import HL7Version2_3
import threading, thread, traceback, time

#from SequentialAccess_i import SequentialAccess_i
from PlainConnectionProvider import *
from StartIdentificationComponent import StartIdentificationComponent
from SqlTraits import *

global trait_view
trait_view = "select i.id as id, n.lastnames , n.firstnames, n.title , i.dob, i.gender, i.cob, a1.no + ' ' + s1.name + '^' + u1.name + '^' + st1.name  from identity i, names n , lnk_identity2address la1,  address a1, street s1, urb u1, state st1"


class ProfileAccess_i(PersonIdService__POA.ProfileAccess, StartIdentificationComponent):

	def __init__(self, dsn=None, ProviderClass = PlainConnectionProvider ):
		self.connector = ProviderClass(dsn)
		self.call_count = { 'update_and_clear' : 0, 'get_profile': 0 }


	def report(self):
		print self.connector.getConnection().__dict__

	def get_profile( self, id, specTraits) :
		conn = self.connector.getConnection()
		conn.rollback()

		field_list , traits = get_field_list_and_traitname_list(specTraits)

		stmt = "select %s from (%s) as traits  where traits.id = %s" % (','.join(field_list), sql_traits , id)
		cursor = conn.cursor()
		cursor.execute(stmt)
		result = cursor.fetchall()
		tprofiles = get_tagged_profiles_from_cursor_result( result, cursor.description)
		if len(tprofiles) > 1:
			raise PersonIdService.DuplicateIds
		return tprofiles[0].profile

	def get_profile_list(self, idSeq, specTraits):
		if idSeq == []:
			return []
		if debug:
			print "idSeq", idSeq
		field_list , traits = get_field_list_and_traitname_list(specTraits)

		stmt = "select %s from (%s) as traits  where id in ( %s)" % (','.join(field_list), sql_traits , ','.join(idSeq) )
		conn = self.connector.getConnection()
		cursor = conn.cursor()
		cursor.execute(stmt)
		result = cursor.fetchall()
		return  get_tagged_profiles_from_cursor_result( result, cursor.description)

	def update_and_clear_traits(self,  profileUpdateSeq):
		ids = []
		for pu in profileUpdateSeq:
			if pu.id not in ids: ids.append(pu.id)
			else: raise PersonIdService.DuplicateIds
		conn =self.connector.getConnection()
		conn.commit()
		for pu in profileUpdateSeq:
			do_profile_update(pu,conn )
		conn.commit()

	def get_traits_known(self, id):
		global sql_identity
		global sql_address
		if debug:
			print "getting known traits for ", id

		cursor = self.connector.getConnection().cursor()
		cursor.execute("select * from (%s) as i where i.id = %s" % (sql_traits , id))
		resultList = cursor.fetchall()
		to_ix = get_field_index_map(cursor.description)

		traits_known = []
		for res in resultList:
			self.__add_to_traits_known(  traits_known, res, cursor)
		return traits_known

	def __add_to_traits_known(self, traits_known, res, cursor):

		for i  in xrange(0, len(res)):
			f = res[i]
			if f <> None and str(f) <> '':
				(traitSpec, pos) = to_trait_map.get(cursor.description[i][0], (None, 0) )

			if traitSpec == None:
			 		continue

			if traitSpec.trait not in traits_known:
					traits_known.append(traitSpec.trait)
		return traits_known




		#gnumed trait deletion is inserting blanks
		#need to check on trait spec flags first.(not done)

		#from spec: "if a pids component logs an audit trail of profile changes,
		#this operation will cause an event to be logged."


if __name__ == "__main__":

	resolver = ResolveIdComponent.IDComponentResolver()

	poa = resolver.getORB().resolve_initial_references("RootPOA")

	pi = ResolveIdComponent.getStartIdentificationComponent()
	po = pi._this()
	name = [CosNaming.NameComponent("gnumed","")]
	context = resolver.getInitialContext()
	try:
		context.bind(name, po)
	except CosNaming.NamingContext.AlreadyBound:
		context.rebind(name, po)

	poaManager = poa._get_the_POAManager()
	poaManager.activate()
	if '-profile' in sys.argv:
		import profile
		profile.run('resolver.getORB().run()', 'profileAccess.prof')
	else:
		resolver.getORB().run()


