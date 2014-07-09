"""Organization classes

author: Karsten Hilbert et al
"""
#============================================================
__license__ = "GPL"


import sys, logging


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmPG2
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmBusinessDBObject

from Gnumed.business import gmDemographicRecord


_log = logging.getLogger('gm.org')

#============================================================
def create_org_category(category=None):
	args = {'cat': category}
	cmd1 = u"""INSERT INTO dem.org_category (description) SELECT %(cat)s
WHERE NOT EXISTS (
	SELECT 1 FROM dem.org_category WHERE description = %(cat)s or _(description) = %(cat)s
)"""
	cmd2 = u"""SELECT pk FROM dem.org_category WHERE description = %(cat)s or _(description) = %(cat)s LIMIT 1"""
	queries = [
		{'cmd': cmd1, 'args': args},
		{'cmd': cmd2, 'args': args}
	]
	rows, idx = gmPG2.run_rw_queries(queries = queries, get_col_idx = False, return_data = True)
	return rows[0][0]

#============================================================
# organization API
#------------------------------------------------------------
_SQL_get_org = u'SELECT * FROM dem.v_orgs WHERE %s'

class cOrg(gmBusinessDBObject.cBusinessDBObject):

	_cmd_fetch_payload = _SQL_get_org % u'pk_org = %s'
	_cmds_store_payload = [
		u"""UPDATE dem.org SET
				description = %(organization)s,
				fk_category = %(pk_category_org)s
			WHERE
				pk = %(pk_org)s
					AND
				xmin = %(xmin_org)s
			RETURNING
				xmin AS xmin_org"""
	]
	_updatable_fields = [
		u'organization',
		u'pk_category_org'
	]
	#--------------------------------------------------------
	def add_unit(self, unit=None):
		return create_org_unit(pk_organization = self._payload[self._idx['pk_org']], unit = unit)
	#--------------------------------------------------------
	def format(self):
		lines = []
		lines.append(_('Organization #%s') % self._payload[self._idx['pk_org']])
		lines.append(u'')
		lines.append(u' %s "%s"' % (
			self._payload[self._idx['l10n_category']],
			self._payload[self._idx['organization']]
		))
		if self._payload[self._idx['is_praxis']]:
			lines.append(u'')
			lines.append(u' ' + _('This is your praxis !'))
		return u'\n'.join(lines)
	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def _get_units(self):
		return get_org_units(order_by = u'unit', org = self._payload[self._idx['pk_org']])

	units = property(_get_units, lambda x:x)
#------------------------------------------------------------
def org_exists(organization=None, category=None):
	args = {'desc': organization, 'cat': category}

	if isinstance(category, basestring):
		cat_part = u'fk_category = (SELECT pk FROM dem.org_category WHERE description = %(cat)s)'
	elif category is None:
		cat_part = u'True'
	else:
		cat_part = u'fk_category = %(cat)s'

	cmd = u'SELECT pk FROM dem.org WHERE description = %%(desc)s AND %s' % cat_part
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = False)
	if len(rows) > 0:
		return cOrg(aPK_obj = rows[0][0])

	return None
#------------------------------------------------------------
def create_org(organization=None, category=None):

	org = org_exists(organization, category)
	if org is not None:
		return org

	args = {'desc': organization, 'cat': category}

	if isinstance(category, basestring):
		cat_part = u'(SELECT pk FROM dem.org_category WHERE description = %(cat)s)'
	else:
		cat_part = u'%(cat)s'

	cmd = u'INSERT INTO dem.org (description, fk_category) VALUES (%%(desc)s, %s) RETURNING pk' % cat_part
	rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = False, return_data = True)

	return cOrg(aPK_obj = rows[0][0])
#------------------------------------------------------------
def delete_org(organization=None):
	args = {'pk': organization}
	cmd = u"""
		DELETE FROM dem.org
		WHERE
			pk = %(pk)s
			AND NOT EXISTS (
				SELECT 1 FROM dem.org_unit WHERE fk_org = %(pk)s
			)
	"""
	rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = False)
	return True
#------------------------------------------------------------
def get_orgs(order_by=None):

	if order_by is None:
		order_by = u''
	else:
		order_by = u'ORDER BY %s' % order_by

	cmd = _SQL_get_org % (u'TRUE %s' % order_by)
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd}], get_col_idx = True)

	return [ cOrg(row = {'data': r, 'idx': idx, 'pk_field': u'pk_org'}) for r in rows ]

#============================================================
# organizational units API
#------------------------------------------------------------
_SQL_get_org_unit = u'SELECT * FROM dem.v_org_units WHERE %s'

class cOrgUnit(gmBusinessDBObject.cBusinessDBObject):

	_cmd_fetch_payload = _SQL_get_org_unit % u'pk_org_unit = %s'
	_cmds_store_payload = [
		u"""UPDATE dem.org_unit SET
				description = %(unit)s,
				fk_org = %(pk_org)s,
				fk_category = %(pk_category_unit)s,
				fk_address = %(pk_address)s
			WHERE
				pk = %(pk_org_unit)s
					AND
				xmin = %(xmin_org_unit)s
			RETURNING
				xmin AS xmin_org_unit"""
	]
	_updatable_fields = [
		u'unit',
		u'pk_org',
		u'pk_category_unit',
		u'pk_address'
	]
	#--------------------------------------------------------
	# comms API
	#--------------------------------------------------------
	def get_comm_channels(self, comm_medium=None):

		args = {'pk': self.pk_obj, 'medium': comm_medium}

		if comm_medium is None:
			cmd = u"""
				SELECT *
				FROM dem.v_org_unit_comms
				WHERE
					pk_org_unit = %(pk)s
			"""
		else:
			cmd = u"""
				SELECT *
				FROM dem.v_org_unit_comms
				WHERE
					pk_org_unit = %(pk)s
						AND
					comm_type = %(medium)s
			"""
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)

		return [ gmDemographicRecord.cOrgCommChannel(row = {
					'pk_field': 'pk_lnk_org_unit2comm',
					'data': r,
					'idx': idx
				}) for r in rows
			]
	#--------------------------------------------------------
	def link_comm_channel(self, comm_medium=None, url=None, is_confidential=False, pk_channel_type=None):
		"""Link a communication medium with this org unit.

		@param comm_medium The name of the communication medium.
		@param url The communication resource locator.
		@type url A types.StringType instance.
		@param is_confidential Wether the data must be treated as confidential.
		@type is_confidential A types.BooleanType instance.
		"""
		return gmDemographicRecord.create_comm_channel (
			comm_medium = comm_medium,
			url = url,
			is_confidential = is_confidential,
			pk_channel_type = pk_channel_type,
			pk_org_unit = self.pk_obj
		)
	#--------------------------------------------------------
	def unlink_comm_channel(self, comm_channel=None):
		gmDemographicRecord.delete_comm_channel (
			pk = comm_channel['pk_lnk_org_unit2comm'],
			pk_org_unit = self.pk_obj
		)
	#--------------------------------------------------------
	# external IDs
	#--------------------------------------------------------
	def get_external_ids(self, id_type=None, issuer=None):
		where_parts = ['pk_org_unit = %(unit)s']
		args = {'unit': self.pk_obj}

		if id_type is not None:
			where_parts.append(u'name = %(name)s')
			args['name'] = id_type.strip()

		if issuer is not None:
			where_parts.append(u'issuer = %(issuer)s')
			args['issuer'] = issuer.strip()

		cmd = u"SELECT * FROM dem.v_external_ids4org_unit WHERE %s" % ' AND '.join(where_parts)
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}])

		return rows

	external_ids = property(get_external_ids, lambda x:x)
	#--------------------------------------------------------
	def add_external_id(self, type_name=None, value=None, issuer=None, comment=None, pk_type=None):
		"""Adds an external ID to an org unit.

		creates ID type if necessary
		"""
		args = {
			'unit': self.pk_obj,
			'val': value,
			'type_name': type_name,
			'pk_type': pk_type,
			'issuer': issuer,
			'comment': comment
		}
		# check for existing ID
		if pk_type is not None:
			cmd = u"""
				SELECT * FROM dem.v_external_ids4org_unit WHERE
				pk_org_unit = %(unit)s
					AND
				pk_type = %(pk_type)s
					AND
				value = %(val)s"""
		else:
			# by type/value/issuer
			if issuer is None:
				cmd = u"""
					SELECT * FROM dem.v_external_ids4org_unit WHERE
					pk_org_unit = %(unit)s
						AND
					name = %(type_name)s
						AND
					value = %(val)s"""
			else:
				cmd = u"""
					SELECT * FROM dem.v_external_ids4org_unit WHERE
					pk_org_unit = %(unit)s
						AND
					name = %(type_name)s
						AND
					value = %(val)s
						AND
					issuer = %(issuer)s"""
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}])

		# create new ID if not found
		if len(rows) == 0:
			if pk_type is None:
				cmd = u"""INSERT INTO dem.lnk_org_unit2ext_id (external_id, fk_type, comment, fk_org_unit) VALUES (
					%(val)s,
					(SELECT dem.add_external_id_type(%(type_name)s, %(issuer)s)),
					%(comment)s,
					%(unit)s
				)"""
			else:
				cmd = u"""INSERT INTO dem.lnk_org_unit2ext_id (external_id, fk_type, comment, fk_org_unit) VALUES (
					%(val)s,
					%(pk_type)s,
					%(comment)s,
					%(unit)s
				)"""
			rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])

		# or update comment of existing ID
		else:
			row = rows[0]
			if comment is not None:
				# comment not already there ?
				if gmTools.coalesce(row['comment'], '').find(comment.strip()) == -1:
					comment = '%s%s' % (gmTools.coalesce(row['comment'], '', '%s // '), comment.strip)
					cmd = u"UPDATE dem.lnk_org_unit2ext_id SET comment = %(comment)s WHERE pk = %(pk)s"
					args = {'comment': comment, 'pk': row['pk_id']}
					rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])
	#--------------------------------------------------------
	def update_external_id(self, pk_id=None, type=None, value=None, issuer=None, comment=None):
		"""Edits an existing external ID.

		Creates ID type if necessary.
		"""
		cmd = u"""
			UPDATE dem.lnk_org_unit2ext_id SET
				fk_type = (SELECT dem.add_external_id_type(%(type)s, %(issuer)s)),
				external_id = %(value)s,
				comment = gm.nullify_empty_string(%(comment)s)
			WHERE
				pk = %(pk)s
		"""
		args = {'pk': pk_id, 'value': value, 'type': type, 'issuer': issuer, 'comment': comment}
		rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])
	#--------------------------------------------------------
	def delete_external_id(self, pk_ext_id=None):
		cmd = u"""
			DELETE FROM dem.lnk_org_unit2ext_id
			WHERE fk_org_unit = %(unit)s AND pk = %(pk)s
		"""
		args = {'unit': self.pk_obj, 'pk': pk_ext_id}
		gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])
	#--------------------------------------------------------
	# address API
	#--------------------------------------------------------
	def link_address(self, id_type=None, address=None):
		self.address = address
		return address
	#--------------------------------------------------------
	def unlink_address(self, address=None, pk_address=None):
		"""Remove an address from the org unit.

		The address itself stays in the database.
		The address can be either cAdress or cPatientAdress.
		"""
		self.address = None
	#--------------------------------------------------------
	def format(self, with_address=False, with_org=True, with_comms=False):
		lines = []
		lines.append(_('Unit%s: %s%s') % (
			gmTools.bool2subst (
				self._payload[self._idx['is_praxis_branch']],
				_(' (of your praxis)'),
				u''
			),
			self._payload[self._idx['unit']],
			gmTools.coalesce(self._payload[self._idx['l10n_unit_category']], u'', u' (%s)')
		))
		if with_org:
			lines.append(_('Organization: %s (%s)') % (
				self._payload[self._idx['organization']],
				self._payload[self._idx['l10n_organization_category']]
			))
		if with_address:
			adr = self.address
			if adr is not None:
				lines.extend(adr.format())
		if with_comms:
			for comm in self.comm_channels:
				lines.append(u'%s: %s%s' % (
					comm['l10n_comm_type'],
					comm['url'],
					gmTools.bool2subst(comm['is_confidential'], _(' (confidential)'), u'', u'')
				))
		return lines
	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def _get_address(self):
		if self._payload[self._idx['pk_address']] is None:
			return None
		return gmDemographicRecord.cAddress(aPK_obj = self._payload[self._idx['pk_address']])

	def _set_address(self, address):
		self['pk_address'] = address['pk_address']
		self.save()

	address = property(_get_address, _set_address)
	#--------------------------------------------------------
	def _get_org(self):
		return cOrg(aPK_obj = self._payload[self._idx['pk_org']])

	organization = property(_get_org, lambda x:x)
	org = property(_get_org, lambda x:x)

	comm_channels = property(get_comm_channels, lambda x:x)
#------------------------------------------------------------
def create_org_unit(pk_organization=None, unit=None):

	args = {'desc': unit, 'pk_org': pk_organization}

	# exists ?
	cmd = u'SELECT pk FROM dem.org_unit WHERE description = %(desc)s AND fk_org = %(pk_org)s'
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = False)
	if len(rows) > 0:
		return cOrgUnit(aPK_obj = rows[0][0])

	# no, create
	cmd = u'INSERT INTO dem.org_unit (description, fk_org) VALUES (%(desc)s, %(pk_org)s) RETURNING pk'
	rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = False, return_data = True)

	return cOrgUnit(aPK_obj = rows[0][0])
#------------------------------------------------------------
def delete_org_unit(unit=None):
	args = {'pk': unit}
	cmd = u"""DELETE FROM dem.org_unit WHERE
		pk = %(pk)s
			AND
		NOT EXISTS (
			SELECT 1 FROM clin.encounter where fk_location = %(pk)s
		)	AND
		NOT EXISTS (
			SELECT 1 FROM clin.hospital_stay where fk_org_unit = %(pk)s
		)	AND
		NOT EXISTS (
			SELECT 1 FROM clin.procedure where fk_org_unit = %(pk)s
		)	AND
		NOT EXISTS (
			SELECT 1 FROM clin.test_org where fk_org_unit = %(pk)s
		)	AND
		NOT EXISTS (
			SELECT 1 FROM dem.lnk_org_unit2comm where fk_org_unit = %(pk)s
		)	AND
		NOT EXISTS (
			SELECT 1 FROM dem.lnk_org_unit2ext_id where fk_org_unit = %(pk)s
		)
	"""
	rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = False)
	return True
#------------------------------------------------------------
def get_org_units(order_by=None, org=None):

	if order_by is None:
		order_by = u''
	else:
		order_by = u' ORDER BY %s' % order_by

	if org is None:
		where_part = u'TRUE'
	else:
		where_part = u'pk_org = %(org)s'

	args = {'org': org}
	cmd = (_SQL_get_org_unit % where_part) + order_by
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)

	return [ cOrgUnit(row = {'data': r, 'idx': idx, 'pk_field': u'pk_org_unit'}) for r in rows ]

#======================================================================
# main
#----------------------------------------------------------------------
if __name__ == "__main__":

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != u'test':
		sys.exit()


	print cOrgUnit(aPK_obj = 21825)


#	for unit in get_org_units():
#		print unit

	sys.exit(0)
#============================================================
#============================================================
# outdated code below =======================================
#============================================================
#============================================================
#============================================================
#============================================================
#============================================================
#============================================================
#============================================================
#============================================================
#============================================================
def get_comm_channels_data_for_org_ids( idList):	
	"""gets comm_channels for a list of org_id. 
	returns a map keyed by org_id with lists of comm_channel data (url, type). 
	this allows a single fetch of comm_channel data for multiple orgs"""

	ids = ", ".join( [ str(x) for x in idList]) 
	cmd = """select l.id_org, id_type, url 
			from dem.comm_channel c, dem.lnk_org2comm_channel l 
			where
				c.id = l.id_comm and
				l.id_org in ( select id from dem.org where id in (%s) )
		""" % ids 
	result = gmPG.run_ro_query("personalia", cmd)
	if result == None:
		_log.error("Unable to load comm channels for org" )
		return None 
	m = {}
	for (id_org, id_type, url) in result:
		if not m.has_key(id_org):
			m[id_org] = []
		m[id_org].append( (id_type, url) )

	return m # is a Map[id_org] = list of comm_channel data 	

def get_address_data_for_org_ids( idList):
	"""gets addresses for a list of valid id values for orgs.
	returns a map keyed by org_id with the address data
	"""

	ids = ", ".join( [ str(x) for x in idList]) 
	cmd = """select l.id_org, number, street, city, postcode, state, country 
			from dem.v_basic_address v , dem.lnk_org2address l 
				where v.addr_id = l.id_address and
				l.id_org in ( select id from dem.org where id in (%s) ) """ % ids 
	result = gmPG.run_ro_query( "personalia", cmd)

	if result == None:
		_log.error("failure in org address load" )
		return None
	m = {}
	for (id_org, n,s,ci,p,st,co) in result:
		m[id_org] =  (n,s,ci,p,st,co) 
	return m  

def get_org_data_for_org_ids(idList):
	""" for a given list of org id values , 
		returns a map of id_org vs. org attributes: description, id_category"""

	ids = ", ".join( [ str(x) for x in idList]) 
	cmd = """select id, description, id_category  from dem.org 
			where id in ( select id from dem.org where id in( %s) )""" % ids 
	#<DEBUG>
	print cmd
	#</DEBUG>
	result = gmPG.run_ro_query("personalia", cmd, )
	if result is None:
		_log.error("Unable to load orgs with ids (%s)" %ids)
		return None
	m = {}
	for (id_org, d, id_cat) in result:
		m[id_org] = (d, id_cat)
	return m
#============================================================
#
#  IGNORE THE FOLLOWING, IF NOT INTERESTED IN TEST CODE
#
#

if __name__ == '__main__':
	print "Please enter a write-enabled user e.g. _test-doc "

	def testListOrgs():
		print "running test listOrg"
		for (f,a) in get_test_data():
			h = cOrgImpl1()
			h.set(*f)
			h.setAddress(*a)
			if not h.save():
				print "did not save ", f

		orgs = cOrgHelperImpl1().findAllOrganizations()

		for org in orgs:
			print "Found org ", org.get(), org.getAddress()
			if not org.shallow_del():
				print "Unable to delete above org"






	def get_test_data():
		"""test org data for unit testing in testOrg()"""
		return [
				( ["Box Hill Hospital", "", "", "Eastern", "hospital", "0398953333", "111-1111","bhh@oz", ""],  ["33", "Nelson Rd", "Box Hill", "3128", None , None] ),
				( ["Frankston Hospital", "", "", "Peninsula", "hospital", "0397847777", "03784-3111","fh@oz", ""],  ["21", "Hastings Rd", "Frankston", "3199", None , None] )
			]

	def get_test_persons():
		return { "Box Hill Hospital":
				[
				['Dr.', 'Bill' , 'Smith', '123-4567', '0417 111 222'],
				['Ms.', 'Anita', 'Jones', '124-5544', '0413 222 444'],
				['Dr.', 'Will', 'Stryker', '999-4444', '0402 333 111']  ],
			"Frankston Hospital":
				[ [ "Dr.", "Jason", "Boathead", "444-5555", "0403 444 2222" ],
				[ "Mr.", "Barnie", "Commuter", "222-1111", "0444 999 3333"],
				[ "Ms.", "Morita", "Traveller", "999-1111", "0222 333 1111"]] }

	def testOrgPersons():
		m = get_test_persons()
		d  = dict(  [  (f[0] , (f, a)) for (f, a) in get_test_data() ] )
		for orgName , personList in m.items():
			f1 , a1 = d[orgName][0], d[orgName][1]
			_testOrgClassPersonRun( f1, a1, personList, cOrgImpl1)
			_testOrgClassPersonRun( f1, a1, personList, cCompositeOrgImpl1)
			_testOrgClassPersonRun( f1, a1, personList, cOrgHelperImpl1().create)
			_testOrgClassPersonRun( f1, a1, personList, cOrgHelperImpl2().create)
			_testOrgClassPersonRun( f1, a1, personList, cOrgHelperImpl3().create)
			_testOrgClassPersonRun( f1, a1, personList, cOrgHelperImpl3().create, getTestIdentityUsing_cOrgDemographicAdapter)


	def _outputPersons( org):
		m = org.getPersonMap()

		if m== []:
			print "NO persons were found unfortunately"

		print """ TestOrgPersonRun got back for """
		a = org.getAddress()
		print org["name"], a["number"], a["street"], a["urb"], a["postcode"] , " phone=", org['phone']

		for id, r in m.items():
			print "\t",", ".join( [ " ".join(r.get_names().values()),
						"work no=", r.getCommChannel(gmDemographicRecord.WORK_PHONE),
						"mobile no=", r.getCommChannel(gmDemographicRecord.MOBILE)
						] )
		

	def _testOrgPersonRun(f1, a1, personList):
		print "Using test data :f1 = ", f1, "and a1 = ", a1 , " and lp = ", personList
		print "-" * 50
		_testOrgClassPersonRun( f1, a1, personList, cOrgImpl1)
		_testOrgClassPersonRun( f1, a1, personList, cCompositeOrgImpl1)
		_testOrgClassPersonRun( f1, a1, personList, cOrgHelperImpl1().create)
		_testOrgClassPersonRun( f1, a1, personList, cOrgHelperImpl2().create)


	def _setIdentityTestData(identity, data):
		identity.addName(data[1], data[2], True)
		identity.setTitle(data[0])
		identity.linkCommChannel( gmDemographicRecord.WORK_PHONE, data[3])
		identity.linkCommChannel( gmDemographicRecord.MOBILE, data[4])

	def getTestIdentityUsingDirectDemographicRecord( data, org):
		id = gmPerson.create_dummy_identity()
		identity = gmDemographicRecord.cDemographicRecord_SQL(id)
		_setIdentityTestData(identity, data)
		return identity

	def getTestIdentityUsing_cOrgDemographicAdapter( data, org):
		helper = cOrgHelperImpl3()
		orgPerson= helper.createOrgPerson()
		orgPerson.setParent(org)
		orgPerson['name'] = ' '.join( [data[0], data[1], data[2]])
		orgPerson['phone'] = data[3]
		orgPerson['mobile'] = data[4]
		orgPerson.save()
		return orgPerson.getDemographicRecord()


	def _testOrgClassPersonRun(f1, a1, personList, orgCreate, identityCreator = getTestIdentityUsingDirectDemographicRecord):
		print "-" * 50
		print "Testing org creator ", orgCreate
		print " and identity creator ", identityCreator
		print "-" * 50
		h = orgCreate()
		h.set(*f1)
		h.setAddress(*a1)
		if not h.save():
			print "Unable to save org for person test"
			h.shallow_del()
			return False
		# use gmDemographicRecord to convert person list
		for lp in personList:
			identity = identityCreator(lp, h)
			result , msg = h.linkPerson(identity)
			print msg

		_outputPersons(h)
		deletePersons(h)

		if h.shallow_del():
			print "Managed to dispose of org"
		else:
			print "unable to dispose of org"

		return True

#	def testOrgPerson(f1, a1, personList):

	def deletePerson(id):
		cmds = [ ( "delete from dem.lnk_identity2comm_chan where fk_identity=%d"%id,[]),
			("delete from dem.names where id_identity=%d"%id,[]),
			("delete from dem.identity where id = %d"%id,[]) ]
		result = gmPG.run_commit("personalia", cmds)
		return result

	def deletePersons( org):
		map = org.getPersonMap()
		for id, r in map.items():	
			org.unlinkPerson(r)

			result = deletePerson(r.getID())
			if result == None:
				_log.error("FAILED TO CLEANUP PERSON %d" %r.getID() )



	def testOrg():
		"""runs a test of load, save , shallow_del  on items in from get_test_data"""
		l = get_test_data()
		results = []
		for (f, a) in l:
			result, obj =	_testOrgRun(f, a)
			results.append( (result, obj) )
		return results



	def _testOrgRun( f1, a1):

		print """testing single level orgs"""
		f = [ "name", "office", "subtype",  "memo", "category", "phone", "fax", "email","mobile"]
		a = ["number", "street", "urb", "postcode", "state", "country"]
		h = cOrgImpl1()

		h.set(*f1)
		h.setAddress(*a1)

		print "testing get, getAddress"
		print h.get()
		print h.getAddressDict()

		import sys
		if not	h.save():
			print "failed to save first time. Is an old test org needing manual removal?"
			return False, h
		print "saved pk =", h.getId()


		pk = h.getId()
		if h.shallow_del():
			print "shallow deleted ", h['name']
		else:
			print "failed shallow delete of ", h['name']



		h2 = cOrgImpl1()

		print "testing load"

		print "should fail"
		if not h2.load(pk):
			print "Failed as expected"

		if h.save():
			print "saved ", h['name'] , "again"
		else:
			print "failed re-save"
			return False, h

		h['fax'] = '222-1111'
		print "using update save"

		if h.save():
			print "saved updated passed"
			print "Test reload next"
		else:
			print "failed save of updated data"
			print "continuing to reload"


		if not h2.load(h.getId()):
			print "failed load"
			return False, h
		print "reloaded values"
		print h2.get()
		print h2.getAddressDict()

		print "** End of Test org"

		if h2.shallow_del():
			print "cleaned up"
		else:
			print "Test org needs to be manually removed"

		return True, h2

	def clean_test_org():
		l = get_test_data()

		names = [ "".join( ["'" ,str(org[0]), "'"] )  for ( org, address) in l]
		names += [ "'John Hunter Hospital'", "'Belmont District Hospital'"]
		nameList = ",".join(names)
		categoryList = "'hospital'"

		cmds = [ ( """create temp table del_org as
				select id  from dem.org
				where description in(%s) or
				id_category in ( select id from dem.org_category c
							where c.description in (%s))
			""" % (nameList, categoryList), [] ),
			("""create temp table del_identity as
			select id  from dem.identity
			where id in
				(
					select id_identity from dem.lnk_person_org_address
					where id_org in ( select id from del_org)
				)""",[] ),
			("""create temp table del_comm as
			(select id_comm from dem.lnk_org2comm_channel where
				id_org in ( select id from del_org)
			) UNION
			(select id_comm from dem.lnk_identity2comm_chan where
				id_identity in ( select id from del_identity)
			)""", [] ),
			("""delete from dem.names where id_identity in
					(select id from del_identity)""",[]),
			("""delete from dem.lnk_person_org_address where
					id_org in (select id from del_org )""",[]),
			("""delete from dem.lnk_person_org_address where
					id_identity in (select id from del_identity)""", []),
			("""delete from dem.lnk_org2comm_channel
			where id_org in (select id from del_org) """,[]),
			("""delete from dem.lnk_identity2comm_chan
					where id_identity in (select id from del_identity)""",[] ),
			("""delete from dem.comm_channel where id in ( select id_comm from del_comm)""",[]),
			("""delete from dem.lnk_job2person where id_identity in (select id from del_identity)""", []),
			("""delete from dem.identity where id in (select id from del_identity)""",[] ),
			("""delete from dem.org where id in ( select id from del_org) """ , [] ),
			("""drop table del_comm""",[]),
			("""drop table del_identity""",[]),
			("""drop table del_org""", [])

			]
		result =  gmPG.run_commit("personalia", cmds) <> None

		return result


	def login_user_and_test(logintest, service = 'personalia', msg = "failed test" , use_prefix_rw= False):
		""" tries to get and verify a read-write connection
		which has permission to write to org tables, so the test case
		can run.
		"""
		login2 = gmPG.request_login_params()

		#login as the RW user
		p = gmPG.ConnectionPool( login2)
		if use_prefix_rw:
			conn = p.GetConnection( service, readonly = 0)
		else:
			conn = p.GetConnection(service)
		result = logintest(conn)

		if result is False:
			print msg

		p.ReleaseConnection(service)
		return result, login2

	def test_rw_user(conn):
		# test it is a RW user, by making a entry and deleting it
		try:
			c.reload("org_category")
			cursor = conn.cursor()

			cursor.execute("select last_value from dem.org_id_seq")
			[org_id_seq] = cursor.fetchone()

			cursor.execute("""
		insert into dem.org ( description, id_category, id)
		values ( 'xxxDEFAULTxxx', %d,
		%d)
			""" % ( c.getId('org_category', 'hospital') , org_id_seq + 1 ) )
			cursor.execute("""
		delete from dem.org where id = %d""" % ( org_id_seq + 1) )
		# make sure this exercise is committed, else a deadlock will occur
			conn.commit()
		except:
			_log.exception("Test of Update Permission failed")
			return False
		return True

	def test_admin_user(conn):
		try:
			cursor = conn.cursor()

			cursor.execute("select last_value from dem.org_category_id_seq")
			[org_cat_id_seq] = cursor.fetchone()

			cursor.execute("""
		insert into dem.org_category ( description, id)
		values ( 'xxxDEFAULTxxx',%d)
			""" %   (org_cat_id_seq + 1 ) )
			cursor.execute("""
		delete from dem.org_category where description like 'xxxDEFAULTxxx' """ )
		# make sure this exercise is committed, else a deadlock will occur
			conn.commit()
		except:
			_log.exception("Test of Update Permission failed")
			return False
		return True

	def login_rw_user():
		return  login_user_and_test( test_rw_user, "login cannot update org", use_prefix_rw = True)


	def login_admin_user():
		return  login_user_and_test( test_admin_user, "login cannot update org_category" )


	def create_temp_categories( categories = ['hospital']):
		print "NEED TO CREATE TEMPORARY ORG_CATEGORY.\n\n ** PLEASE ENTER administrator login  : e.g  user 'gm-dbo' and  his password"
		#get a admin login
		for i in xrange(0, 4):
			result ,tmplogin = login_admin_user()
			if result:
				break
		if i == 4:
			print "Failed to login"
			return categories

		# and save it , for later removal of test categories.
		from Gnumed.pycommon import gmLoginInfo
		adminlogin = gmLoginInfo.LoginInfo(*tmplogin.GetInfo())

		#login as admin
		p = gmPG.ConnectionPool( tmplogin)
		conn = p.GetConnection("personalia")

		# use the last value + 1 of the relevant sequence, but don't increment it
		cursor = conn.cursor()

		failed_categories = []
		n =1
		for cat in categories:
			cursor.execute("select last_value from dem.org_category_id_seq")
			[org_cat_id_seq] = cursor.fetchone()

			cursor.execute( "insert into dem.org_category(description, id) values('%s', %d)" % (cat, org_cat_id_seq + n) )
			cursor.execute("select id from dem.org_category where description in ('%s')" % cat)

			result =  cursor.fetchone()
			if result == None or len(result) == 0:
				failed_categories.append(cat)
				print "Failed insert of category", cat
				conn.rollback()
			else:
				conn.commit()
			n += 1

		conn.commit()
		p.ReleaseConnection('personalia')
		return failed_categories, adminlogin

	def clean_org_categories(adminlogin = None, categories = ['hospital'], service='personalia'):

		print"""

		The temporary category(s) will now
		need to be removed under an administrator login
		e.g. gm-dbo
		Please enter login for administrator:
		"""
		if adminlogin is None:
			for i in xrange(0, 4):
				result, adminlogin = login_admin_user()
				if  result:
					break
			if i == 4:
				print "FAILED TO LOGIN"
				return categories

		p = gmPG.ConnectionPool(adminlogin)
		conn = p.GetConnection(service)
		failed_remove = []
		for cat in categories:
			try:
				cursor = conn.cursor()
				cursor.execute( "delete from  dem.org_category where description in ('%s')"%cat)
				conn.commit()
				cursor.execute("select id from dem.org_category where description in ('%s')"%cat)
				if cursor.fetchone() == None:
					print "Succeeded in removing temporary org_category"
				else:
					print "*** Unable to remove temporary org_category"
					failed_remove .append(cat)
			except:
				import sys
				print sys.exc_info()[0], sys.exc_info()[1]
				import traceback
				traceback.print_tb(sys.exc_info()[2])

				failed_remove.append(cat)

		conn = None
		p.ReleaseConnection(service)
		if failed_remove <> []:
			print "FAILED TO REMOVE ", failed_remove
		return failed_remove

	def test_CatFinder():
		print "TESTING cCatFinder"

		print """c = cCatFinder("org_category")"""
		c = cCatFinder("org_category")

		print c.getCategories("org_category")

		print """c = cCatFinder("enum_comm_types")"""
		c = cCatFinder("enum_comm_types")

		l = c.getCategories("enum_comm_types")
		print "testing getId()"
		l2 = []
		for x in l:
			l2.append((x, c.getId("enum_comm_types", x)))
		print l2

		print """testing borg behaviour of cCatFinder"""

		print c.getCategories("org_category")


	def help():
		print """\nNB If imports not found , try:

		change to gnumed/client directory , then

		export PYTHONPATH=$PYTHONPATH:../;python business/gmOrganization.py

			--clean	, cleans the test data and categories

			--gui 	sets up as for no arguments, then runs the client.
			 	on normal exit of client, normal tests run, and
				then cleanup of entered data.
		
			using the gui,

			the 'list organisations' toolbar button , loads all organisations
			in the database, and display suborgs and persons associated
			with each organisation.

			the 'add organisation' button will add a top-level organisation.
			the 'add branch/division' button will work when the last selected
			org was a top level org.

			the 'add person M|F' button works if an org is selected.
			
			the save button works when entry is finished.

			selecting on an item, will bring it into the editing area.
			
			No test yet for dirtied edit data, to query whether to
			save or discard. (30/5/2004)
		"""
		print
		print "In the connection query, please enter"
		print "a WRITE-ENABLED user e.g. _test-doc (not test-doc), and the right password"
		print
		print "Run the unit test with cmdline argument '--clean'  if trying to clean out test data"
		print

		print """You can get a sermon by running
		export PYTHONPATH=$PYTHONPATH:../;python business/gmOrganization.py --sermon
		"""
		print """
		Pre-requisite data in database is :
		gnumed=# select * from org_category ;
		id | description
		----+-------------
		1 | hospital
		(1 row)

		gnumed=# select * from enum_comm_types ;
		id | description
		----+-------------
		1 | email
		2 | fax
		3 | homephone
		4 | workphone
		5 | mobile
		6 | web
		7 | jabber
		(7 rows)
		"""

	def sermon():
				print"""
		This test case shows how many things can go wrong , even with just a test case.
		Problem areas include:
		- postgres administration :  pg_ctl state, pg_hba.conf, postgres.conf  config files .
		- schema integrity constraints : deletion of table entries which are subject to foreign keys, no input for no default value and no null value columns, input with duplicated values where unique key constraint applies to non-primary key columns, dealing with access control by connection identity management.


		- efficiency trade-offs -e.g. using db objects for localising code with data and easier function call interface ( then hopefully, easier to program with) , vs. need to access many objects at once
		without calling the backend for each object.

		- error and exception handling - at what point in the call stack to handle an error.
		Better to use error return values and log exceptions near where they occur, vs. wrapping inside try: except: blocks and catching typed exceptions.


		- test-case construction:  test data is needed often, and the issue
		is whether it is better to keep the test data volatile in the test-case,
		which handles both its creation and deletion, or to add it to test data
		server configuration files, which may involve running backend scripts
		for loading and removing test data.



		- Database connection problems:
		-Is the problem in :
			- pg_ctl start -D  /...mydata-directory is wrong, and gnumed isn't existing there.

			- ..mydata-directory/pg_hba.conf
				- can psql connect locally and remotely with the username and password.
				- Am I using md5 authenentication and I've forgotten the password.
					- I need to su postgres, alter pg_hba.conf to use trust for
					the gnumed database, pg_ctl restart -D .., su normal_user,  psql gnumed, alter user my_username password 'doh'
					- might be helpful: the default password for _test-doc is test-doc

			- ../mydata-directory/postgres.conf
				- tcp connect  flag isn't set to true

			- remote/local mixup :
			a different set of user passwords on different hosts. e.g the password
			for _test-doc is 'pass' on localhost and 'test-doc' for the serverhost.
			- In the prompts for admin and user login, local host was used for one, and
			remote host for the other



		- test data won't go away :
		- 'hospital' category in org_category : the test case failed in a previous run
		and the test data was left there; now the test case won't try to delete it
		because it exists as a pre-existing category;
			soln : run with  --clean  option

		- test-case failed unexpectedly, or break key was hit in the middle of a test-case run.
			Soln: run with --clean option,


		"""


#============================================================

	import sys
	testgui = False
	if len(sys.argv) > 1:
		if sys.argv[1] == '--clean':
			result = clean_test_org()
			p = gmPG.ConnectionPool()
			p.ReleaseConnection('personalia')
			if result:
				print "probably succeeded in cleaning orgs"
			else: 	print "failed to clean orgs"

			clean_org_categories()
			sys.exit(1)

		if sys.argv[1] == "--sermon":
			sermon()

		if sys.argv[1] == "--help":
			help()

		if sys.argv[1] =="--gui":
			testgui = True

	print "*" * 50
	print "RUNNING UNIT TEST of gmOrganization "


	test_CatFinder()
	tmp_category = False  # tmp_category means test data will need to be added and removed
			# for  org_category .

	c = cCatFinder()
	if not "hospital" in c.getCategories("org_category") :
		print "FAILED in prerequisite for org_category : test categories are not present."

		tmp_category = True

	if tmp_category:
		# test data in a categorical table (restricted access) is needed

		print """You will need to switch login identity to database administrator in order
			to have permission to write to the org_category table,
			and then switch back to the ordinary write-enabled user in order
			to run the test cases.
			Finally you will need to switch back to administrator login to
			remove the temporary org_categories.
			"""
		categories = ['hospital']
		result, adminlogin = create_temp_categories(categories)
		if result == categories:
			print "Unable to create temporary org_category. Test aborted"
			sys.exit(-1)
		if result <> []:
			print "UNABLE TO CREATE THESE CATEGORIES"
			if not raw_input("Continue ?") in ['y', 'Y'] :
				sys.exit(-1)

	try:
		results = []
		if tmp_category:
				print "succeeded in creating temporary org_category"
				print
				print "** Now ** RESUME LOGIN **  of write-enabled user (e.g. _test-doc) "
				while (1):
					# get the RW user for org tables (again)
					if login_rw_user():
						break

		if testgui:
			if cCatFinder().getId('org_category','hospital') == None:
				print "Needed to set up temporary org_category 'hospital"
				sys.exit(-1)
			import os
			print os.environ['PWD']
		 	os.spawnl(os.P_WAIT, "/usr/bin/python", "/usr/bin/python","wxpython/gnumed.py", "--debug")

			#os.popen2('python client/wxpython/gnumed.py --debug')

			# run the test case
		results = testOrg()

			# cleanup after the test case
		for (result , org) in results:
			if not result and org.getId() <> None:
				print "trying cleanup"
				if  org.shallow_del(): print " 	may have succeeded"
				else:
					print "May need manual removal of org id =", org.getId()

		testOrgPersons()

		testListOrgs()

	except:
		import  sys
		print sys.exc_info()[0], sys.exc_info()[1]
		_log.exception( "Fatal exception")

		# clean-up any temporary categories.
	if tmp_category:
		try:
			clean_org_categories(adminlogin)
		except:
			while(not login_rw_user()[0]):
				pass
			clean_test_org()
			clean_org_categories(adminlogin)



def setPostcodeWidgetFromUrbId(postcodeWidget, id_urb):
         """convenience method for urb and postcode phrasewheel interaction.
            never called without both arguments, but need to check that id_urb
            is not invalid"""
         #TODO type checking that the postcodeWidget is a phrasewheel configured
         # with a postcode matcher
         if  postcodeWidget is None or id_urb is None:
                 return False
         postcode = getPostcodeForUrbId(id_urb)
         if postcode is None:
                 return False
         if len(postcode) == 0:
                 return True
         postcodeWidget.SetValue(postcode)
         postcodeWidget.input_was_selected= 1
         return True

 #------------------------------------------------------------

def setUrbPhraseWheelFromPostcode(pwheel, postcode):
         """convenience method for common postcode to urb phrasewheel collaboration.
            there is no default args for these utility functions,
            This function is never called without both arguments, otherwise
            there is no intention (= modify the urb phrasewheel with postcode value).
         """
         # TODO type checking that the pwheel is a urb phrasewheel with a urb matcher
         # clearing post code unsets target
         # phrasewheel's postcode context
         if pwheel is None:
                 return False
         if postcode == '':
                 pwheel.set_context("postcode", "%")
                 return True
         urbs = getUrbsForPostcode(postcode)
         if urbs is None:
                 return False
         if len(urbs) == 0:
                 return True
         pwheel.SetValue(urbs[0])
         pwheel.input_was_selected = 1

         # FIXME: once the postcode context is set,
         # the urb phrasewheel will only return urbs with
         # the same postcode. These can be viewed by clearing
         # the urb widget. ?How to unset the postcode context,
         # some gui gesture ? clearing the postcode
         # (To view all the urbs for a set context,
         # put a "*" in the urb box and activate the picklist.
         # THE PROBLEM WITH THIS IS IF THE USER CLEARS THE BOX AND SET CONTEXT IS RESET,
         # then the "*" will try to pull all thousands of urb names, freezing the app.
         # so needs a fixup (? have SQL select ... LIMIT n in Phrasewheel )

         pwheel.set_context("postcode", postcode)
         return True

#======================================================================
