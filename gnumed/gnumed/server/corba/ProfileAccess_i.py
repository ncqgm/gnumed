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


def do_profile_update(pu, conn):
	"""iterates through the traits found in a profileUpdate.modify_list , and
	does the gnumed changes within the tables identity, names, lnk_person2address, lnk_person2comm_channel , address, street, comm_channel  to match the requested trait updates"""

			# the following statements can modify the db , so put inside transaction
	updated = []
	 # used to find duplicate trait updates within the traits held by pu (profileUpdate type)
	statements = []
	# holds statements for a batch call , if any exists
	frags = []
	# reducing the number of sql calls by collecting identity field updates


	cursor = conn.cursor()
	if '-debug' in sys.argv:
		print "do_profile_update()"
		print "the modify list is : "
		for t in pu.modify_list:
			print t.name, t.value.value()

	for trait in pu.modify_list:
		if trait.name in updated:
			conn.rollback()
			raise PersonIdService.ModifyOrDelete

		# ignore blank values
		if trait.value.value().strip() == '':
			continue
		l =trait.value.value().split('^')
		l = [ x.strip() for x in l]
		updated.append(trait.name)
		if trait.name == hl7.PATIENT_NAME:
			if l[0] =='' and l[1] =='':
				continue

			# the clause 'and active=true' reduces the sql execution time
			# by over a half. This can be found by profiling the sql calls.
			cursor.execute("update names set active = false where id_identity = %s and active = true " % pu.id )
			# check for semantic key constraint
			cursor.execute("select id from names where lastnames = '%s' and firstnames = '%s' and preferred = '%s' and id_identity = %s" % tuple(l[0:3] + [pu.id]) )
			res = cursor.fetchone()
			if res <> None:
				n = res[0]

				cursor.execute("update names set active = true where id = %d" % n)
				continue


			statements.append( "insert into names ( lastnames, firstnames, preferred, id_identity, active) values ( '%s','%s','%s', %s, true) " % tuple ( l[0:3]+[pu.id] ) )

			if len(l) >= 4 and l[3] <> '':
				statements.append("update identity set title = '%s' where id = %s" % ( l[4], pu.id))

		elif trait.name == hl7.PATIENT_ADDRESS:
			if l[1] == '' or l[2] =='' or l[3] =='' or (l[4] =='' and l[5] ==''):
				continue
			s1 = "delete from lnk_person2address where id_identity = %s and id_type = 1"
			s2_findUrb = "select urb.id from urb, state where state.id = urb.id_state and urb.name = '%s' and (urb.postcode = '%s' or   state.name='%s' )"

			s3_findStreet = "select street.id, urb.id from street ,urb , state where street.id_urb = urb.id and urb.id_state = state.id and street.name ='%s' and ( street.id_urb = %d or   urb.postcode = '%s' or (street.postcode = '%s' and state.name = '%s' ))"
			s3b1_insertStreet = "insert into street( name, id_urb) values( '%s', %d)"
			s3b2_selectNewStreet = "select curr_val('street_id_seq')"


			s4_selectAddress = "select id from address a where a.number = '%s' and a.id_street = %d"

			s4b1_insertAddress = "insert into address a ( number, id_street) values ( '%s', %d)"
			s4b2_selectNewAddress = "select curr_val('address_id_seq')"

			cursor.execute(s2_findUrb % (l[2] ,l[4] ,l[3]) )
			res = cursor.fetchall()
			if (len(res) == 0):
				urb_id = 0
			else:
				urb_id = res[0][0]

			cursor.execute(s3_findStreet % ( l[1] ,urb_id,l[4], l[4], l[3] ))
			res = cursor.fetchall()



			if len(res) > 0 :
				street_id, urb_id = res[0][0], res[0][1]
			elif urb_id <> 0:
				cursor.execute(s3b1_insertStreet % (l[1], urb_id))
				cursor.execute(s3b2_selectNewStreet)
				[street_id] = cursor.fetchone()

			else:
				print "Unable to find with ", s2_findUrb % (l[2] ,l[4] ,l[3])
				raise PersonIdService.ModifyOrDelete

			cursor.execute(s4_selectAddress % (l[0], street_id))
			res = cursor.fetchall()

			if len(res) > 0:
				address_id = res[0][0]
				if debug:
					print "existing old address id", address_id
				cursor.execute("select count(*) from lnk_person2address where id_identity = %s and id_address = %d" % ( pu. id, address_id))
				[count] = cursor.fetchone()


			else:
				count =0
				cursor.execute(s4b1_insertAddress %(l[0], street_id))
				cursor.execute(s4b2_selectNewAddress)
				[address_id] = cursor.fetchone()
				if debug:
					print "new address id ", address_id

			s5 = "insert into lnk_person2address( id_identity, id_type, id_address) values ( %s, 1, %d)"
			if count == 0:
				cursor.execute(s5 % (pu.id, address_id) )

		elif trait.name in [ hl7.PHONE_NUMBER_HOME , hl7.PHONE_NUMBER_BUSINESS ]:
			# requires comm_type for home and business phone to be known

			if trait.name == hl7.PHONE_NUMBER_HOME: comm_type = HOME_PHONE_TYPE
			else:	 comm_type = BUSINESS_PHONE_TYPE

			cursor.execute("select id_comm from lnk_person2comm_channel l, comm_channel c where  id_identity = %s and l.id_comm = c.id and c.id_type = %d" % (pu.id, comm_type) )
			res = cursor.fetchone()
			if (len(res) > 0):
				id_comm = res[0]
				cursor.execute("delete from lnk_person2comm_channel  where id_identity = %s and id_comm = %d" % (pu.id, id_comm) )
				cursor.execute("select count(id) from lnk_person2comm_channel l where l.id_comm = %d" % id_comm )
				res2 = cursor.fetchone()
				if res2[0] == 0:
					cursor.execute("delete from comm_channel where id = %d" % id_comm)
			cursor.execute("select id from comm_channel where id_type = %d and url = '%s'" % ( comm_type, trait.value.value() ) )
			res = cursor.fetchone()
			if debug:
				print "existing id comm_channel =", res
			if res <> None:
				id_comm = res[0]
			else:
				cursor.execute("insert into comm_channel( id_type, url) values( %d, '%s')" % (comm_type, trait.value.value() ))
				cursor.execute("""select currval('comm_channel_id_seq')""")
				[id_comm] = cursor.fetchone()
			cursor.execute("insert into lnk_person2comm_channel(id_identity, id_comm) values ( %s, %d)" % ( pu.id, id_comm) )



		elif trait.name in [ hl7.DATE_TIME_OF_BIRTH, hl7.PATIENT_DEATH_DATE_AND_TIME ] :
			if l[0] == '':
				continue

			frags.append(" %s = to_timestamp('%s', 'YYYYMMDDHH24MISS')" % ( in_trait_map[trait.name], trait.value.value() ) )

			#statements.append( "update identity set %s = to_timestamp('%s', 'YYYYMMDDHH24MISS') where id = %s" % ( in_trait_map[trait.name], trait.value.value(), pu.id) )
		elif trait.name in [hl7.SEX, hl7.NATIONALITY]:
			if l[0] == '':
				continue
			frags.append( " %s = '%s'" % (in_trait_map[trait.name], trait.value.value() ) )

			#statements.append("update identity set %s = '%s' where id = %s" % (in_trait_map[trait.name], trait.value.value(), pu.id) )

	cursor.execute("update identity set %s where id = %s" % ( ",".join(frags), pu.id) )
	for s in statements:
		cursor.execute(s)






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


