# -*- coding: utf8 -*-
"""GNUmed demographics object.

This is a patient object intended to let a useful client-side
API crystallize from actual use in true XP fashion.

license: GPL v2 or later
"""
#============================================================
__version__ = "$Revision: 1.106 $"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>, I.Haywood <ihaywood@gnu.org>"

# stdlib
import sys
import os
import os.path
import logging


# GNUmed
if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmDispatcher
from Gnumed.pycommon import gmBusinessDBObject
from Gnumed.pycommon import gmPG2
from Gnumed.pycommon import gmTools


_log = logging.getLogger('gm.business')
_log.info(__version__)

try:
	_
except NameError:
	_ = lambda x:x

#============================================================
# text+image tags
#------------------------------------------------------------
_SQL_get_tag_image = u"SELECT * FROM ref.v_tag_images_no_data WHERE %s"

class cTagImage(gmBusinessDBObject.cBusinessDBObject):

	_cmd_fetch_payload = _SQL_get_tag_image % u"pk_tag_image = %s"
	_cmds_store_payload = [
		u"""
			UPDATE ref.tag_image SET
				description = gm.nullify_empty_string(%(description)s),
				filename = gm.nullify_empty_string(%(filename)s)
			WHERE
				pk = %(pk_tag_image)s
					AND
				xmin = %(xmin_tag_image)s
			RETURNING
				pk as pk_tag_image,
				xmin as xmin_tag_image
		"""
	]
	_updatable_fields = [u'description', u'filename']
	#--------------------------------------------------------
	def export_image2file(self, aChunkSize=0, filename=None):

		if self._payload[self._idx['size']] == 0:
			return None

		if filename is None:
			suffix = None
			# preserve original filename extension if available
			if self._payload[self._idx['filename']] is not None:
				name, suffix = os.path.splitext(self._payload[self._idx['filename']])
				suffix = suffix.strip()
				if suffix == u'':
					suffix = None
			# get unique filename
			filename = gmTools.get_unique_filename (
				prefix = 'gm-tag_image-',
				suffix = suffix
			)

		success = gmPG2.bytea2file (
			data_query = {
				'cmd': u'SELECT substring(image from %(start)s for %(size)s) FROM ref.tag_image WHERE pk = %(pk)s',
				'args': {'pk': self.pk_obj}
			},
			filename = filename,
			chunk_size = aChunkSize,
			data_size = self._payload[self._idx['size']]
		)

		if success:
			return filename

		return None
	#--------------------------------------------------------
	def update_image_from_file(self, filename=None):
		# sanity check
		if not (os.access(filename, os.R_OK) and os.path.isfile(filename)):
			_log.error('[%s] is not a readable file' % filename)
			return False

		gmPG2.file2bytea (
			query = u"UPDATE ref.tag_image SET image = %(data)s::bytea WHERE pk = %(pk)s",
			filename = filename,
			args = {'pk': self.pk_obj}
		)

		# must update XMIN now ...
		self.refetch_payload()
		return True
#------------------------------------------------------------
def get_tag_images(order_by=None):
	if order_by is None:
		order_by = u'true'
	else:
		order_by = 'true ORDER BY %s' % order_by

	cmd = _SQL_get_tag_image % order_by
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd}], get_col_idx = True)
	return [ cTagImage(row = {'data': r, 'idx': idx, 'pk_field': 'pk_tag_image'}) for r in rows ]
#------------------------------------------------------------
def create_tag_image(description=None, link_obj=None):

	args = {u'desc': description, u'img': u''}
	cmd = u"""
		INSERT INTO ref.tag_image (
			description,
			image
		) VALUES (
			%(desc)s,
			%(img)s::bytea
		)
		RETURNING pk
	"""
	rows, idx = gmPG2.run_rw_queries (
		link_obj = link_obj,
		queries = [{'cmd': cmd, 'args': args}],
		end_tx = True,
		return_data = True,
		get_col_idx = False
	)

	return cTagImage(aPK_obj = rows[0]['pk'])
#------------------------------------------------------------
def delete_tag_image(tag_image=None):
	args = {'pk': tag_image}
	cmd = u"""
		DELETE FROM ref.tag_image
		WHERE
			pk = %(pk)s
				AND
			NOT EXISTS (
				SELECT 1
				FROM dem.identity_tag
				WHERE fk_tag = %(pk)s
				LIMIT 1
			)
		RETURNING 1
	"""
	rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}], return_data = True)
	if len(rows) == 0:
		return False
	return True

#============================================================
_SQL_get_identity_tags = u"""SELECT * FROM dem.v_identity_tags WHERE %s"""

class cIdentityTag(gmBusinessDBObject.cBusinessDBObject):

	_cmd_fetch_payload = _SQL_get_identity_tags % u"pk_identity_tag = %s"
	_cmds_store_payload = [
		u"""
			UPDATE dem.identity_tag SET
				fk_tag = %(pk_tag_image)s,
				comment = gm.nullify_empty_string(%(comment)s)
			WHERE
				pk = %(pk_identity_tag)s
					AND
				xmin = %(xmin_identity_tag)s
			RETURNING
				pk as pk_identity_tag,
				xmin as xmin_identity_tag
		"""
	]
	_updatable_fields = [u'fk_tag',	u'comment']
	#--------------------------------------------------------
	def export_image2file(self, aChunkSize=0, filename=None):

		if self._payload[self._idx['image_size']] == 0:
			return None

		if filename is None:
			suffix = None
			# preserve original filename extension if available
			if self._payload[self._idx['filename']] is not None:
				name, suffix = os.path.splitext(self._payload[self._idx['filename']])
				suffix = suffix.strip()
				if suffix == u'':
					suffix = None
			# get unique filename
			filename = gmTools.get_unique_filename (
				prefix = 'gm-identity_tag-',
				suffix = suffix
			)

		exported = gmPG2.bytea2file (
			data_query = {
				'cmd': u'SELECT substring(image from %(start)s for %(size)s) FROM ref.tag_image WHERE pk = %(pk)s',
				'args': {'pk': self._payload[self._idx['pk_tag_image']]}
			},
			filename = filename,
			chunk_size = aChunkSize,
			data_size = self._payload[self._idx['image_size']]
		)
		if exported:
			return filename

		return None
#============================================================
#============================================================
def get_countries():
	cmd = u"""
		select
			_(name) as l10n_country, name, code, deprecated
		from dem.country
		order by l10n_country"""
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd}])
	return rows
#============================================================
def get_country_for_region(region=None):
	cmd = u"""
SELECT code_country, l10n_country FROM dem.v_state WHERE l10n_state = %(region)s
	union
SELECT code_country, l10n_country FROM dem.v_state WHERE state = %(region)s
"""
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': {'region': region}}])
	return rows
#============================================================
def delete_province(province=None, delete_urbs=False):

	args = {'prov': province}

	queries = []
	if delete_urbs:
		queries.append ({
			'cmd': u"""
				delete from dem.urb du
				where
					du.id_state = %(prov)s
						and
					not exists (select 1 from dem.street ds where ds.id_urb = du.id)""",
			'args': args
		})

	queries.append ({
		'cmd': u"""
			delete from dem.state ds
			where
				ds.id = %(prov)s
					and
				not exists (select 1 from dem.urb du where du.id_state = ds.id)""",
		'args': args
	})

	gmPG2.run_rw_queries(queries = queries)

	return True
#------------------------------------------------------------
def create_province(name=None, code=None, country=None):

	args = {'code': code, 'country': country, 'name': name}

	cmd = u"""SELECT EXISTS (SELECT 1 FROM dem.state WHERE name = %(name)s)"""
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = False)

	if rows[0][0]:
		return

	cmd = u"""
		INSERT INTO dem.state (
			code, country, name
		) VALUES (
			%(code)s, %(country)s, %(name)s
		)"""
	gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])
#------------------------------------------------------------
def get_provinces():
	cmd = u"""
		select
			l10n_state, l10n_country, state, code_state, code_country, pk_state, country_deprecated
		from dem.v_state
		order by l10n_country, l10n_state"""
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd}])
	return rows
#============================================================
# address related classes
#------------------------------------------------------------
class cAddress(gmBusinessDBObject.cBusinessDBObject):
	"""A class representing an address as an entity in itself.

	We consider addresses to be self-complete "labels" for locations.
	It does not depend on any people actually living there. Thus
	an address can get attached to as many people as we want to
	signify that that is their place of residence/work/...

	This class acts on the address as an entity. Therefore it can
	modify the address fields. Think carefully about *modifying*
	addresses attached to people, though. Most times when you think
	person.modify_address() what you *really* want is as sequence of
	person.unlink_address(old) and person.link_address(new).

	Modifying an address may or may not be the proper thing to do as
	it will transparently modify the address for *all* the people to
	whom it is attached. In many cases you will want to create a *new*
	address and link it to a person instead of the old address.
	"""
	_cmd_fetch_payload = u"select * from dem.v_address where pk_address = %s"
	_cmds_store_payload = [
		u"""UPDATE dem.address SET
				aux_street = %(notes_street)s,
				subunit = %(subunit)s,
				addendum = %(notes_subunit)s,
				lat_lon = %(lat_lon_street)s
			WHERE
				id = %(pk_address)s
					AND
				xmin = %(xmin_address)s
			RETURNING
				xmin AS xmin_address"""
	]
	_updatable_fields = [
		'notes_street',
		'subunit',
		'notes_subunit',
		'lat_lon_address'
	]
	#--------------------------------------------------------
	def format(self):
		data = {
			'pk_adr': self._payload[self._idx['pk_address']],
			'street': self._payload[self._idx['street']],
			'pk_street': self._payload[self._idx['pk_street']],
			'notes_street': gmTools.coalesce(self._payload[self._idx['notes_street']], u'', u' %s'),
			'number': self._payload[self._idx['number']],
			'subunit': gmTools.coalesce(self._payload[self._idx['subunit']], u'', u' %s'),
			'notes_subunit': gmTools.coalesce(self._payload[self._idx['notes_subunit']], u'', u' (%s)'),
			'zip': self._payload[self._idx['postcode']],
			'urb': self._payload[self._idx['urb']],
			'pk_urb': self._payload[self._idx['pk_urb']],
			'suburb': gmTools.coalesce(self._payload[self._idx['suburb']], u'', u' (%s)'),
			'l10n_state': self._payload[self._idx['l10n_state']],
			'pk_state': self._payload[self._idx['pk_state']],
			'code_state': self._payload[self._idx['code_state']],
			'l10n_country': self._payload[self._idx['l10n_country']],
			'code_country': self._payload[self._idx['code_country']]
		}
		txt = _(
			'Address [#%(pk_adr)s]\n'
			' Street: %(street)s [#%(pk_street)s]%(notes_street)s\n'
			' Number: %(number)s%(subunit)s%(notes_subunit)s\n'
			' Location: %(zip)s %(urb)s%(suburb)s [#%(pk_urb)s]\n'
			' Region: %(l10n_state)s, %(code_state)s [#%(pk_state)s]\n'
			' Country: %(l10n_country)s, %(code_country)s'
		) % data
		return txt.split('\n')
#------------------------------------------------------------
def address_exists(country=None, state=None, urb=None, postcode=None, street=None, number=None, subunit=None):

	cmd = u"""SELECT dem.address_exists(%(country)s, %(state)s, %(urb)s, %(postcode)s, %(street)s, %(number)s, %(subunit)s)"""
	args = {
		'country': country,
		'state': state,
		'urb': urb,
		'postcode': postcode,
		'street': street,
		'number': number,
		'subunit': subunit
	}

	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}])
	if rows[0][0] is None:
		_log.debug('address does not exist')
		for key, val in args.items():
			_log.debug('%s: %s', key, val)
		return None

	return rows[0][0]
#------------------------------------------------------------
def old_address_exists(country=None, state=None, urb=None, suburb=None, postcode=None, street=None, number=None, subunit=None, notes_street=None, notes_subunit=None):
	where_parts = [
		u'code_country = %(country)s',
		u'code_state = %(state)s',
		u'urb = %(urb)s',
		u'postcode = %(postcode)s',
		u'street = %(street)s',
		u'number = %(number)s'
	]

	if suburb is None:
		where_parts.append(u"suburb IS %(suburb)s")
	else:
		where_parts.append(u"suburb = %(suburb)s")

	if notes_street is None:
		where_parts.append(u"notes_street IS %(notes_street)s")
	else:
		where_parts.append(u"notes_street = %(notes_street)s")

	if subunit is None:
		where_parts.append(u"subunit IS %(subunit)s")
	else:
		where_parts.append(u"subunit = %(subunit)s")

	if notes_subunit is None:
		where_parts.append(u"notes_subunit IS %(notes_subunit)s")
	else:
		where_parts.append(u"notes_subunit = %(notes_subunit)s")

	cmd = u"SELECT pk_address FROM dem.v_address WHERE %s" % u" AND ".join(where_parts)
	data = {
		'country': country,
		'state': state,
		'urb': urb,
		'suburb': suburb,
		'postcode': postcode,
		'street': street,
		'notes_street': notes_street,
		'number': number,
		'subunit': subunit,
		'notes_subunit': notes_subunit
	}

	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': data}])

	if len(rows) == 0:
		_log.debug('address does not exist yet')
		for key, val in data.items():
			_log.debug('%s: %s', key, val)
		return None

	return rows[0][0]
#------------------------------------------------------------
def create_address(country=None, state=None, urb=None, suburb=None, postcode=None, street=None, number=None, subunit=None):

	if suburb is not None:
		suburb = gmTools.none_if(suburb.strip(), u'')

	pk_address = address_exists (
		country = country,
		state = state,
		urb = urb,
#		suburb = suburb,
		postcode = postcode,
		street = street,
		number = number,
		subunit = subunit
	)
	if pk_address is not None:
		return cAddress(aPK_obj=pk_address)

	cmd = u"""
SELECT dem.create_address (
	%(number)s,
	%(street)s,
	%(postcode)s,
	%(urb)s,
	%(state)s,
	%(country)s,
	%(subunit)s
)"""
	args = {
		'number': number,
		'street': street,
		'postcode': postcode,
		'urb': urb,
		'state': state,
		'country': country,
		'subunit': subunit
	}
	queries = [{'cmd': cmd, 'args': args}]

	rows, idx = gmPG2.run_rw_queries(queries = queries, return_data = True)
	adr = cAddress(aPK_obj = rows[0][0])

	if suburb is not None:
		queries = [{
			# CAVE: suburb will be ignored if there already is one
			'cmd': u"update dem.street set suburb = %(suburb)s where id=%(pk_street)s and suburb is Null",
			'args': {'suburb': suburb, 'pk_street': adr['pk_street']}
		}]
		rows, idx = gmPG2.run_rw_queries(queries = queries)

	return adr
#------------------------------------------------------------
def delete_address(address=None):
	cmd = u"delete from dem.address where id=%s"
	rows, idx = gmPG2.run_rw_queries(queries=[{'cmd': cmd, 'args': [address['pk_address']]}])
	return True
#------------------------------------------------------------
def get_address_types(identity=None):
	cmd = u'select id as pk, name, _(name) as l10n_name from dem.address_type'
	rows, idx = gmPG2.run_rw_queries(queries=[{'cmd': cmd}])
	return rows
#------------------------------------------------------------
def get_addresses(order_by=None):

	if order_by is None:
		order_by = u''
	else:
		order_by = u'ORDER BY %s' % order_by

	cmd = u"SELECT * FROM dem.v_address %s" % order_by
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd}], get_col_idx = True)
	return [ cAddress(row = {'data': r, 'idx': idx, 'pk_field': u'pk_address'}) for r in rows ]

#===================================================================
class cPatientAddress(gmBusinessDBObject.cBusinessDBObject):

	_cmd_fetch_payload = u"SELECT * FROM dem.v_pat_addresses WHERE pk_address = %s"
	_cmds_store_payload = [
		u"""UPDATE dem.lnk_person_org_address SET
				id_type = %(pk_address_type)s
			WHERE
				id = %(pk_lnk_person_org_address)s
					AND
				xmin = %(xmin_lnk_person_org_address)s
			RETURNING
				xmin AS xmin_lnk_person_org_address
		"""
	]
	_updatable_fields = ['pk_address_type']
	#---------------------------------------------------------------
	def get_identities(self, same_lastname=False):
		pass
#===================================================================
# communication channels API
#-------------------------------------------------------------------
class cCommChannel(gmBusinessDBObject.cBusinessDBObject):

	_cmd_fetch_payload = u"SELECT * FROM dem.v_person_comms WHERE pk_lnk_identity2comm = %s"
	_cmds_store_payload = [
		u"""UPDATE dem.lnk_identity2comm SET
				fk_address = %(pk_address)s,
				fk_type = dem.create_comm_type(%(comm_type)s),
				url = %(url)s,
				is_confidential = %(is_confidential)s
			WHERE
				pk = %(pk_lnk_identity2comm)s
					AND
				xmin = %(xmin_lnk_identity2comm)s
			RETURNING
				xmin AS xmin_lnk_identity2comm
		"""
	]
	_updatable_fields = [
		'pk_address',
		'url',
		'comm_type',
		'is_confidential'
	]
#-------------------------------------------------------------------
class cOrgCommChannel(gmBusinessDBObject.cBusinessDBObject):

	_cmd_fetch_payload = u"SELECT * FROM dem.v_org_unit_comms WHERE pk_lnk_org_unit2comm = %s"
	_cmds_store_payload = [
		u"""UPDATE dem.lnk_org_unit2comm SET
				fk_type = dem.create_comm_type(%(comm_type)s),
				url = %(url)s,
				is_confidential = %(is_confidential)s
			WHERE
				pk = %(pk_lnk_org_unit2comm)s
					AND
				xmin = %(xmin_lnk_org_unit2comm)s
			RETURNING
				xmin AS xmin_lnk_org_unit2comm
		"""
	]
	_updatable_fields = [
		'url',
		'comm_type',
		'is_confidential'
	]
#-------------------------------------------------------------------
def create_comm_channel(comm_medium=None, url=None, is_confidential=False, pk_channel_type=None, pk_identity=None, pk_org_unit=None):
	"""Create a communications channel for a patient."""

	if url is None:
		return None

	args = {
		'url': url,
		'secret': is_confidential,
		'pk_type': pk_channel_type,
		'type': comm_medium
	}

	if pk_identity is not None:
		args['pk_owner'] = pk_identity
		tbl = u'dem.lnk_identity2comm'
		col = u'fk_identity'
		view = u'dem.v_person_comms'
		view_pk = u'pk_lnk_identity2comm'
		channel_class = cCommChannel
	if pk_org_unit is not None:
		args['pk_owner'] = pk_org_unit
		tbl = u'dem.lnk_org_unit2comm'
		col = u'fk_org_unit'
		view = u'dem.v_org_unit_comms'
		view_pk = u'pk_lnk_org_unit2comm'
		channel_class = cOrgCommChannel

	if pk_channel_type is None:
		cmd = u"""INSERT INTO %s (
			%s,
			url,
			fk_type,
			is_confidential
		) VALUES (
			%%(pk_owner)s,
			%%(url)s,
			dem.create_comm_type(%%(type)s),
			%%(secret)s
		)""" % (tbl, col)
	else:
		cmd = u"""INSERT INTO %s (
			%s,
			url,
			fk_type,
			is_confidential
		) VALUES (
			%%(pk_owner)s,
			%%(url)s,
			%%(pk_type)s,
			%%(secret)s
		)""" % (tbl, col)

	queries = [{'cmd': cmd, 'args': args}]
	cmd = u"SELECT * FROM %s WHERE %s = currval(pg_get_serial_sequence('%s', 'pk'))" % (view, view_pk, tbl)
	queries.append({'cmd': cmd})

	rows, idx = gmPG2.run_rw_queries(queries = queries, return_data = True, get_col_idx = True)

	if pk_identity is not None:
		return cCommChannel(row = {'pk_field': view_pk, 'data': rows[0], 'idx': idx})

	return channel_class(row = {'pk_field': view_pk, 'data': rows[0], 'idx': idx})
#-------------------------------------------------------------------
def delete_comm_channel(pk=None, pk_patient=None, pk_org_unit=None):
	if pk_patient is not None:
		query = {
			'cmd': u"DELETE FROM dem.lnk_identity2comm WHERE pk = %(pk)s AND fk_identity = %(pat)s",
			'args': {'pk': pk, 'pat': pk_patient}
		}
	if pk_org_unit is not None:
		query = {
			'cmd': u"DELETE FROM dem.lnk_org_unit2comm WHERE pk = %(pk)s AND fk_org_unit = %(unit)s",
			'args': {'pk': pk, 'unit': pk_org_unit}
		}
	gmPG2.run_rw_queries(queries = [query])
#-------------------------------------------------------------------
def get_comm_channel_types():
	cmd = u"SELECT pk, _(description) AS l10n_description, description FROM dem.enum_comm_types"
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd}], get_col_idx = False)
	return rows
#-------------------------------------------------------------------
def delete_comm_channel_type(pk_channel_type=None):
	cmd = u"""
		DELETE FROM dem.enum_comm_types
		WHERE
			pk = %(pk)s
			AND NOT EXISTS (
				SELECT 1 FROM dem.lnk_identity2comm WHERE fk_type = %(pk)s
			)
			AND NOT EXISTS (
				SELECT 1 FROM dem.lnk_org_unit2comm WHERE fk_type = %(pk)s
			)
	"""
	gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': {'pk': pk_channel_type}}])
	return True
#===================================================================
#-------------------------------------------------------------------

class cOrg (gmBusinessDBObject.cBusinessDBObject):
	"""
	Organisations

	This is also the common ancestor of cIdentity, self._table is used to
	hide the difference.
	The aim is to be able to sanely write code which doesn't care whether
	its talking to an organisation or an individual"""
	_table = "org"

	_cmd_fetch_payload = "select *, xmin from dem.org where id=%s"
	_cmds_lock_rows_for_update = ["select 1 from dem.org where id=%(id)s and xmin=%(xmin)s"]
	_cmds_store_payload = [
		"""update dem.org set
			description=%(description)s,
			id_category=(select id from dem.org_category where description=%(occupation)s)
		where id=%(id)s""",
		"select xmin from dem.org where id=%(id)s"
	]
	_updatable_fields = ["description", "occupation"]
	_service = 'personalia'
	#------------------------------------------------------------------
	def cleanup (self):
		pass
	#------------------------------------------------------------------
	def export_demographics (self):
		if not self.__cache.has_key ('addresses'):
			self['addresses']
		if not self.__cache.has_key ('comms'):
			self['comms']
		return self.__cache
	#--------------------------------------------------------------------
	def get_members (self):
		"""
		Returns a list of (address dict, cIdentity) tuples 
		"""
		cmd = """select
				vba.id,
				vba.number,
				vba.addendum, 
				vba.street,
				vba.urb,
				vba.postcode,
				at.name,
				lpoa.id_type,
				vbp.pk_identity,
				title,
				firstnames,
				lastnames,
				dob,
				cob,
				gender,
				pupic,
				pk_marital_status,
				marital_status,
				karyotype,
				xmin_identity,
				preferred
			from
				dem.v_basic_address vba,
				dem.lnk_person_org_address lpoa,
				dem.address_type at,
				dem.v_basic_person vbp
			where
				lpoa.id_address = vba.id
				and lpoa.id_type = at.id
				and lpoa.id_identity = vbp.pk_identity
				and lpoa.id_org = %%s
				"""

		rows, idx = gmPG.run_ro_query('personalia', cmd, 1, self.getId ())
		if rows is None:
			return []
		elif len(rows) == 0:
			return []
		else:
			return [({'pk':i[0], 'number':i[1], 'addendum':i[2], 'street':i[3], 'city':i[4], 'postcode':i[5], 'type':i[6], 'id_type':i[7]}, cIdentity (row = {'data':i[8:], 'id':idx[8:], 'pk_field':'id'})) for i in rows]	
	#------------------------------------------------------------
	def set_member (self, person, address):
		"""
		Binds a person to this organisation at this address.
		person is a cIdentity object
		address is a dict of {'number', 'street', 'addendum', 'city', 'postcode', 'type'}
		type is one of the IDs returned by getAddressTypes
		"""
		cmd = "insert into dem.lnk_person_org_address (id_type, id_address, id_org, id_identity) values (%(type)s, dem.create_address (%(number)s, %(addendum)s, %(street)s, %(city)s, %(postcode)s), %(org_id)s, %(pk_identity)s)"
		address['pk_identity'] = person['pk_identity']
		address['org_id'] = self.getId()
		if not id_addr:
			return (False, None)
		return gmPG.run_commit2 ('personalia', [(cmd, [address])])
	#------------------------------------------------------------
	def unlink_person (self, person):
		cmd = "delete from dem.lnk_person_org_address where id_org = %s and id_identity = %s"
		return gmPG.run_commit2 ('personalia', [(cmd, [self.getId(), person.ID])])
	#----------------------------------------------------------------------
	def getId (self):
		"""
		Hide the difference between org.id and v_basic_person.pk_identity
		"""
		return self['id']
#==============================================================================
def get_time_tuple (mx):
	"""
	wrap mx.DateTime brokenness
	Returns 9-tuple for use with pyhon time functions
	"""
	return [ int(x) for x in  str(mx).split(' ')[0].split('-') ] + [0,0,0, 0,0,0]
#----------------------------------------------------------------
def getAddressTypes():
	"""Gets a dict matching address types to their ID"""
	row_list = gmPG.run_ro_query('personalia', "select name, id from dem.address_type")
	if row_list is None:
		return {}
	if len(row_list) == 0:
		return {}
	return dict (row_list)
#----------------------------------------------------------------
def getMaritalStatusTypes():
	"""Gets a dictionary matching marital status types to their internal ID"""
	row_list = gmPG.run_ro_query('personalia', "select name, pk from dem.marital_status")
	if row_list is None:
		return {}
	if len(row_list) == 0:
		return {}
	return dict(row_list)
#------------------------------------------------------------------
def getRelationshipTypes():
	"""Gets a dictionary of relationship types to internal id"""
	row_list = gmPG.run_ro_query('personalia', "select description, id from dem.relation_types")
	if row_list is None:
		return None
	if len (row_list) == 0:
		return None
	return dict(row_list)

#----------------------------------------------------------------
def getUrb (id_urb):
	cmd = """
select
	dem.state.name,
	dem.urb.postcode
from
	dem.urb,
	dem.state
where
	dem.urb.id = %s and
	dem.urb.id_state = dem.state.id"""
	row_list = gmPG.run_ro_query('personalia', cmd, None, id_urb)
	if not row_list:
		return None
	else:
		return (row_list[0][0], row_list[0][1])

def getStreet (id_street):
	cmd = """
select
	dem.state.name,
	coalesce (dem.street.postcode, dem.urb.postcode),
	dem.urb.name
from
	dem.urb,
	dem.state,
	dem.street
where
	dem.street.id = %s and
	dem.street.id_urb = dem.urb.id and
	dem.urb.id_state = dem.state.id
"""
	row_list = gmPG.run_ro_query('personalia', cmd, None, id_street)
	if not row_list:
		return None
	else:
		return (row_list[0][0], row_list[0][1], row_list[0][2])

def getCountry (country_code):
	row_list = gmPG.run_ro_query('personalia', "select name from dem.country where code = %s", None, country_code)
	if not row_list:
		return None
	else:
		return row_list[0][0]
#-------------------------------------------------------------------------------
def get_town_data (town):
	row_list = gmPG.run_ro_query ('personalia', """
select
	dem.urb.postcode,
	dem.state.code,
	dem.state.name,
	dem.country.code,
	dem.country.name
from
	dem.urb,
	dem.state,
	dem.country
where
	dem.urb.name = %s and
	dem.urb.id_state = dem.state.id and
	dem.state.country = dem.country.code""", None, town)
	if not row_list:
		return (None, None, None, None, None)
	else:
		return tuple (row_list[0])
#============================================================
# callbacks
#------------------------------------------------------------
def _post_patient_selection(**kwargs):
	print "received post_patient_selection notification"
	print kwargs['kwds']
#============================================================

#============================================================
# main
#------------------------------------------------------------
if __name__ == "__main__":

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	import random
	#--------------------------------------------------------
	def test_address_exists():

		addresses = [
			{
			'country': 'Germany',
			'state': 'Sachsen',
			'urb': 'Leipzig',
			'postcode': '04318',
			'street': u'Cunnersdorfer Strasse',
			'number': '11'
			},
			{
			'country': 'DE',
			'state': 'SN',
			'urb': 'Leipzig',
			'postcode': '04317',
			'street': u'Riebeckstraße',
			'number': '65',
			'subunit': 'Parterre'
			},
			{
			'country': 'DE',
			'state': 'SN',
			'urb': 'Leipzig',
			'postcode': '04317',
			'street': u'Riebeckstraße',
			'number': '65',
			'subunit': '1. Stock'
			},
			{
			'country': 'DE',
			'state': 'SN',
			'urb': 'Leipzig',
			'postcode': '04317',
			'street': u'Riebeckstraße',
			'number': '65',
			'subunit': '1. Stock'
			},
			{
#			'country': 'DE',
#			'state': 'SN',
			'urb': 'Leipzig',
			'postcode': '04317',
			'street': u'Riebeckstraße',
			'number': '65',
			'subunit': '1. Stock'
			},
		]

		for adr in addresses:
			print adr
			exists = address_exists(**adr)
			if exists is None:
				print "address does not exist"
			else:
				print "address exists, primary key:", exists

	#--------------------------------------------------------
	def test_create_address():
		address = create_address (
			country ='DE',
			state ='SN',
			urb ='Leipzig',
			suburb ='Sellerhausen',
			postcode ='04318',
			street = u'Cunnersdorfer Strasse',
			number = '11'
#			,notes_subunit = '4.Stock rechts'
		)
		print "created existing address"
		print address.format()

		su = str(random.random())

		address = create_address (
			country ='DE',
			state = 'SN',
			urb ='Leipzig',
			suburb ='Sellerhausen',
			postcode ='04318',
			street = u'Cunnersdorfer Strasse',
			number = '11',
#			notes_subunit = '4.Stock rechts',
			subunit = su
		)
		print "created new address with subunit", su
		print address
		print address.format()
		print "deleted address:", delete_address(address)
	#--------------------------------------------------------
	def test_get_countries():
		for c in get_countries():
			print c
	#--------------------------------------------------------
	def test_get_country_for_region():
		region = raw_input("Please enter a region: ")
		print "country for region [%s] is: %s" % (region, get_country_for_region(region = region))
	#--------------------------------------------------------
	def test_delete_tag():
		if delete_tag_image(tag_image = 9999):
			print "deleted tag 9999"
		else:
			print "did not delete tag 9999"
		if delete_tag_image(tag_image = 1):
			print "deleted tag 1"
		else:
			print "did not delete tag 1"
	#--------------------------------------------------------
	def test_tag_images():
		tag = cTagImage(aPK_obj = 1)
		print tag
		print get_tag_images()
	#--------------------------------------------------------

	#gmPG2.get_connection()

	#test_address_exists()
	test_create_address()
	#test_get_countries()
	#test_get_country_for_region()
	#test_delete_tag()
	#test_tag_images()

	sys.exit()
#============================================================

