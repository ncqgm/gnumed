"""Organization classes

author: Karsten Hilbert et al
"""
#============================================================
__license__ = "GPL"


import sys, logging


if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x
from Gnumed.pycommon import gmPG2
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmBusinessDBObject

from Gnumed.business import gmDemographicRecord


_log = logging.getLogger('gm.org')

#============================================================
def create_org_category(category=None, link_obj=None):
	args = {'cat': category}
	cmd1 = """INSERT INTO dem.org_category (description) SELECT %(cat)s
WHERE NOT EXISTS (
	SELECT 1 FROM dem.org_category WHERE description = %(cat)s or _(description) = %(cat)s
)"""
	cmd2 = """SELECT pk FROM dem.org_category WHERE description = %(cat)s or _(description) = %(cat)s LIMIT 1"""
	queries = [
		{'sql': cmd1, 'args': args},
		{'sql': cmd2, 'args': args}
	]
	rows = gmPG2.run_rw_queries(link_obj = link_obj, queries = queries, return_data = True)
	return rows[0][0]

#============================================================
# organization API
#------------------------------------------------------------
_SQL_get_org = 'SELECT * FROM dem.v_orgs WHERE %s'

class cOrg(gmBusinessDBObject.cBusinessDBObject):

	_cmd_fetch_payload = _SQL_get_org % 'pk_org = %s'
	_cmds_store_payload = [
		"""UPDATE dem.org SET
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
		'organization',
		'pk_category_org'
	]
	#--------------------------------------------------------
	def add_unit(self, unit=None):
		return create_org_unit(pk_organization = self._payload['pk_org'], unit = unit)
	#--------------------------------------------------------
	def format(self):
		lines = []
		lines.append(_('Organization #%s') % self._payload['pk_org'])
		lines.append('')
		lines.append(' %s "%s"' % (
			self._payload['l10n_category'],
			self._payload['organization']
		))
		if self._payload['is_praxis']:
			lines.append('')
			lines.append(' ' + _('This is your praxis !'))
		return '\n'.join(lines)
	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def _get_units(self):
		return get_org_units(order_by = 'unit', org = self._payload['pk_org'])

	units = property(_get_units)

#------------------------------------------------------------
def org_exists(organization:str=None, category=None, link_obj=None) -> cOrg:
	args = {'desc': organization, 'cat': category}

	if category is None:
		cat_part = 'True'
	elif isinstance(category, str):
		cat_part = 'fk_category = (SELECT pk FROM dem.org_category WHERE description = %(cat)s)'
	else:
		cat_part = 'fk_category = %(cat)s'

	cmd = 'SELECT pk FROM dem.org WHERE description = %%(desc)s AND %s' % cat_part
	rows = gmPG2.run_ro_queries(link_obj = link_obj, queries = [{'sql': cmd, 'args': args}])
	if len(rows) > 0:
		return cOrg(aPK_obj = rows[0][0])

	return None

#------------------------------------------------------------
def create_org(organization=None, category=None, link_obj=None):

	org = org_exists(link_obj = link_obj, organization = organization, category = category)
	if org is not None:
		return org

	args = {'desc': organization, 'cat': category}

	if isinstance(category, str):
		cat_part = '(SELECT pk FROM dem.org_category WHERE description = %(cat)s)'
	else:
		cat_part = '%(cat)s'

	cmd = 'INSERT INTO dem.org (description, fk_category) VALUES (%%(desc)s, %s) RETURNING pk' % cat_part
	rows = gmPG2.run_rw_queries(link_obj = link_obj, queries = [{'sql': cmd, 'args': args}], return_data = True)

	return cOrg(aPK_obj = rows[0][0], link_obj = link_obj)

#------------------------------------------------------------
def delete_org(organization=None):
	args = {'pk': organization}
	cmd = """
		DELETE FROM dem.org
		WHERE
			pk = %(pk)s
			AND NOT EXISTS (
				SELECT 1 FROM dem.org_unit WHERE fk_org = %(pk)s
			)
	"""
	gmPG2.run_rw_queries(queries = [{'sql': cmd, 'args': args}])
	return True

#------------------------------------------------------------
def get_orgs(order_by=None, return_pks=False):

	if order_by is None:
		order_by = ''
	else:
		order_by = 'ORDER BY %s' % order_by

	cmd = _SQL_get_org % ('TRUE %s' % order_by)
	rows = gmPG2.run_ro_queries(queries = [{'sql': cmd}])
	if return_pks:
		return [ r['pk_org'] for r in rows ]
	return [ cOrg(row = {'data': r, 'pk_field': 'pk_org'}) for r in rows ]

#============================================================
# organizational units API
#------------------------------------------------------------
_SQL_get_org_unit = 'SELECT * FROM dem.v_org_units WHERE %s'

class cOrgUnit(gmBusinessDBObject.cBusinessDBObject):

	_cmd_fetch_payload = _SQL_get_org_unit % 'pk_org_unit = %s'
	_cmds_store_payload = [
		"""UPDATE dem.org_unit SET
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
		'unit',
		'pk_org',
		'pk_category_unit',
		'pk_address'
	]
	#--------------------------------------------------------
	# comms API
	#--------------------------------------------------------
	def get_comm_channels(self, comm_medium=None):

		args = {'pk': self.pk_obj, 'medium': comm_medium}

		if comm_medium is None:
			cmd = """
				SELECT *
				FROM dem.v_org_unit_comms
				WHERE
					pk_org_unit = %(pk)s
			"""
		else:
			cmd = """
				SELECT *
				FROM dem.v_org_unit_comms
				WHERE
					pk_org_unit = %(pk)s
						AND
					comm_type = %(medium)s
			"""
		rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])

		return [ gmDemographicRecord.cOrgCommChannel(row = {
					'pk_field': 'pk_lnk_org_unit2comm',
					'data': r
				}) for r in rows
			]

	comm_channels = property(get_comm_channels)

	#--------------------------------------------------------
	def link_comm_channel(self, comm_medium=None, url=None, is_confidential=False, pk_channel_type=None):
		"""Link a communication medium with this org unit.

		@param comm_medium The name of the communication medium.
		@param url The communication resource locator.
		@type url A str instance.
		@param is_confidential Whether the data must be treated as confidential.
		@type is_confidential A bool instance.
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
			where_parts.append('name = %(name)s')
			args['name'] = id_type.strip()

		if issuer is not None:
			where_parts.append('issuer = %(issuer)s')
			args['issuer'] = issuer.strip()

		cmd = "SELECT * FROM dem.v_external_ids4org_unit WHERE %s" % ' AND '.join(where_parts)
		rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])

		return rows

	external_ids = property(get_external_ids)
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
			cmd = """
				SELECT * FROM dem.v_external_ids4org_unit WHERE
				pk_org_unit = %(unit)s
					AND
				pk_type = %(pk_type)s
					AND
				value = %(val)s"""
		else:
			# by type/value/issuer
			if issuer is None:
				cmd = """
					SELECT * FROM dem.v_external_ids4org_unit WHERE
					pk_org_unit = %(unit)s
						AND
					name = %(type_name)s
						AND
					value = %(val)s"""
			else:
				cmd = """
					SELECT * FROM dem.v_external_ids4org_unit WHERE
					pk_org_unit = %(unit)s
						AND
					name = %(type_name)s
						AND
					value = %(val)s
						AND
					issuer = %(issuer)s"""
		rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])

		# create new ID if not found
		if len(rows) == 0:
			if pk_type is None:
				cmd = """INSERT INTO dem.lnk_org_unit2ext_id (external_id, fk_type, comment, fk_org_unit) VALUES (
					%(val)s,
					(SELECT dem.add_external_id_type(%(type_name)s, %(issuer)s)),
					%(comment)s,
					%(unit)s
				)"""
			else:
				cmd = """INSERT INTO dem.lnk_org_unit2ext_id (external_id, fk_type, comment, fk_org_unit) VALUES (
					%(val)s,
					%(pk_type)s,
					%(comment)s,
					%(unit)s
				)"""
			rows = gmPG2.run_rw_queries(queries = [{'sql': cmd, 'args': args}])

		# or update comment of existing ID
		else:
			row = rows[0]
			if comment is not None:
				# comment not already there ?
				if gmTools.coalesce(row['comment'], '').find(comment.strip()) == -1:
					comment = '%s%s' % (gmTools.coalesce(row['comment'], '', '%s // '), comment.strip)
					cmd = "UPDATE dem.lnk_org_unit2ext_id SET comment = %(comment)s WHERE pk = %(pk)s"
					args = {'comment': comment, 'pk': row['pk_id']}
					rows = gmPG2.run_rw_queries(queries = [{'sql': cmd, 'args': args}])

	#--------------------------------------------------------
	def update_external_id(self, pk_id=None, type=None, value=None, issuer=None, comment=None):
		"""Edits an existing external ID.

		Creates ID type if necessary.
		"""
		cmd = """
			UPDATE dem.lnk_org_unit2ext_id SET
				fk_type = (SELECT dem.add_external_id_type(%(type)s, %(issuer)s)),
				external_id = %(value)s,
				comment = gm.nullify_empty_string(%(comment)s)
			WHERE
				pk = %(pk)s
		"""
		args = {'pk': pk_id, 'value': value, 'type': type, 'issuer': issuer, 'comment': comment}
		gmPG2.run_rw_queries(queries = [{'sql': cmd, 'args': args}])

	#--------------------------------------------------------
	def delete_external_id(self, pk_ext_id=None):
		cmd = """
			DELETE FROM dem.lnk_org_unit2ext_id
			WHERE fk_org_unit = %(unit)s AND pk = %(pk)s
		"""
		args = {'unit': self.pk_obj, 'pk': pk_ext_id}
		gmPG2.run_rw_queries(queries = [{'sql': cmd, 'args': args}])

	#--------------------------------------------------------
	# address API
	#--------------------------------------------------------
	def link_address(self, id_type=None, address=None):
		self.address = address
		return address
	#--------------------------------------------------------
	def unlink_address(self, address=None, pk_address=None):
		"""Remove an address from the org unit.

		The address itself remains in the database.
		The address can be either cAdress or cPatientAdress.
		"""
		self.address = None
	#--------------------------------------------------------
	def format(self, with_address=False, with_org=True, with_comms=False):
		lines = []
		lines.append(_('Unit%s: %s%s') % (
			gmTools.bool2subst (
				self._payload['is_praxis_branch'],
				_(' (of your praxis)'),
				''
			),
			self._payload['unit'],
			gmTools.coalesce(self._payload['l10n_unit_category'], '', ' (%s)')
		))
		if with_org:
			lines.append(_('Organization: %s (%s)') % (
				self._payload['organization'],
				self._payload['l10n_organization_category']
			))
		if with_address:
			adr = self.address
			if adr is not None:
				lines.extend(adr.format())
		if with_comms:
			for comm in self.comm_channels:
				lines.append('%s: %s%s' % (
					comm['l10n_comm_type'],
					comm['url'],
					gmTools.bool2subst(comm['is_confidential'], _(' (confidential)'), '', '')
				))
		return lines

	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def _get_address(self):
		if self._payload['pk_address'] is None:
			return None
		return gmDemographicRecord.cAddress(aPK_obj = self._payload['pk_address'])

	def _set_address(self, address):
		self['pk_address'] = address['pk_address']
		self.save()

	address = property(_get_address, _set_address)

	#--------------------------------------------------------
	def _get_org(self):
		return cOrg(aPK_obj = self._payload['pk_org'])

	organization = property(_get_org)
	org = property(_get_org)

	comm_channels = property(get_comm_channels)

#------------------------------------------------------------
def create_org_unit(pk_organization:str=None, unit:str=None, link_obj=None) -> cOrgUnit:
	_log.debug('creating org unit [%s:%s]', unit, pk_organization)
	args = {'desc': unit, 'pk_org': pk_organization}
	cmd1 = """
		INSERT INTO dem.org_unit (description, fk_org) SELECT
			%(desc)s,
			%(pk_org)s
		WHERE NOT EXISTS (
			SELECT 1 FROM dem.org_unit WHERE description = %(desc)s AND fk_org = %(pk_org)s
		)"""
	cmd2 = _SQL_get_org_unit % 'unit = %(desc)s AND pk_org = %(pk_org)s'
	queries = [
		{'sql': cmd1, 'args': args},
		{'sql': cmd2, 'args': args}
	]
	rows = gmPG2.run_rw_queries(link_obj = link_obj, queries = queries, return_data = True)
	return cOrgUnit(row = {'data': rows[0], 'pk_field': 'pk_org_unit'})

#------------------------------------------------------------
def delete_org_unit(unit:int=None) -> bool:
	args = {'pk': unit}
	cmd = "DELETE FROM dem.org_unit WHERE pk = %(pk)s"
			#--			AND
			#--		NOT EXISTS (
			#--			SELECT 1 FROM blobs.doc_med where fk_org_unit = %(pk)s
			#--		)	AND
			#--		NOT EXISTS (
			#--			SELECT 1 FROM clin.external_care where fk_org_unit = %(pk)s
			#--		)	AND
			#--		NOT EXISTS (
			#--			SELECT 1 FROM blobs.doc_med where fk_org_unit = %(pk)s
			#--		)	AND
			#--		NOT EXISTS (
			#--			SELECT 1 FROM clin.hospital_stay where fk_org_unit = %(pk)s
			#--		)	AND
			#--		NOT EXISTS (
			#--			SELECT 1 FROM clin.procedure where fk_org_unit = %(pk)s
			#--		)	AND
			#--		NOT EXISTS (
			#--			SELECT 1 FROM clin.test_org where fk_org_unit = %(pk)s
			#--		)	AND
			#--		NOT EXISTS (
			#--			SELECT 1 FROM dem.lnk_org_unit2comm where fk_org_unit = %(pk)s
			#--		)	AND
			#--		NOT EXISTS (
			#--			SELECT 1 FROM dem.lnk_org_unit2ext_id where fk_org_unit = %(pk)s
			#--		)
	try:
		gmPG2.run_rw_queries(queries = [{'sql': cmd, 'args': args}])
	except gmPG2.dbapi.errors.ForeignKeyViolation:
		_log.exception('error deleting org unit')
		return False

	return True

#------------------------------------------------------------
def get_org_units(order_by:str=None, org:int=None, return_pks:bool=False) -> list:
	if order_by is None:
		order_by = ''
	else:
		order_by = ' ORDER BY %s' % order_by

	if org is None:
		where_part = 'TRUE'
	else:
		where_part = 'pk_org = %(org)s'

	args = {'org': org}
	cmd = (_SQL_get_org_unit % where_part) + order_by
	rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
	if return_pks:
		return [ r['pk_org_unit'] for r in rows ]

	return [ cOrgUnit(row = {'data': r, 'pk_field': 'pk_org_unit'}) for r in rows ]

#======================================================================
# main
#----------------------------------------------------------------------
if __name__ == "__main__":

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	gmPG2.request_login_params(setup_pool = True)

	#print(cOrgUnit(aPK_obj = 21825))
	delete_org_unit(2)
	#for unit in get_org_units():
	#	print(unit)
