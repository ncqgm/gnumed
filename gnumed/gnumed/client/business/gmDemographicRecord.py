# -*- coding: utf-8 -*-
"""GNUmed demographics object.

This is a patient object intended to let a useful client-side
API crystallize from actual use in true XP fashion.

license: GPL v2 or later
"""
#============================================================
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>, I.Haywood <ihaywood@gnu.org>"

# stdlib
import sys
import os
import os.path
import logging
import urllib.parse


# GNUmed
if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x
from Gnumed.pycommon import gmBusinessDBObject
from Gnumed.pycommon import gmPG2
from Gnumed.pycommon import gmTools


_log = logging.getLogger('gm.business')

#============================================================
# occupation handling
#------------------------------------------------------------
def get_occupations(pk_identity=None):
	cmd = """
		SELECT *
		FROM dem.v_person_jobs
		WHERE pk_identity = %(pk)s
		ORDER BY l10n_occupation
	"""
	rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': {'pk': pk_identity}}])
	return rows
#============================================================
# text+image tags
#------------------------------------------------------------
_SQL_get_tag_image = "SELECT * FROM ref.v_tag_images_no_data WHERE %s"

class cTagImage(gmBusinessDBObject.cBusinessDBObject):

	_cmd_fetch_payload = _SQL_get_tag_image % "pk_tag_image = %s"
	_cmds_store_payload = [
		"""
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
	_updatable_fields = ['description', 'filename']
	#--------------------------------------------------------
	def export_image2file(self, aChunkSize=0, filename=None):

		if self._payload['size'] == 0:
			return None

		if filename is None:
			suffix = None
			# preserve original filename extension if available
			if self._payload['filename'] is not None:
				name, suffix = os.path.splitext(self._payload['filename'])
				suffix = suffix.strip()
				if suffix == '':
					suffix = None
			# get unique filename
			filename = gmTools.get_unique_filename (
				prefix = 'gm-tag_image-',
				suffix = suffix
			)

		success = gmPG2.bytea2file (
			data_query = {
				'sql': 'SELECT substring(image from %(start)s for %(size)s) FROM ref.tag_image WHERE pk = %(pk)s',
				'args': {'pk': self.pk_obj}
			},
			filename = filename,
			chunk_size = aChunkSize,
			data_size = self._payload['size']
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
			query = "UPDATE ref.tag_image SET image = %(data)s::bytea WHERE pk = %(pk)s",
			filename = filename,
			args = {'pk': self.pk_obj}
		)

		# must update XMIN now ...
		self.refetch_payload()
		return True
#------------------------------------------------------------
def get_tag_images(order_by=None, return_pks=False):
	if order_by is None:
		order_by = 'true'
	else:
		order_by = 'true ORDER BY %s' % order_by
	cmd = _SQL_get_tag_image % order_by
	rows = gmPG2.run_ro_queries(queries = [{'sql': cmd}])
	if return_pks:
		return [ r['pk_tag_image'] for r in rows ]
	return [ cTagImage(row = {'data': r, 'pk_field': 'pk_tag_image'}) for r in rows ]

#------------------------------------------------------------
def create_tag_image(description=None, link_obj=None):

	args = {'desc': description, 'img': ''}
	cmd = """
		INSERT INTO ref.tag_image (
			description,
			image
		) VALUES (
			%(desc)s,
			%(img)s::bytea
		)
		RETURNING pk
	"""
	rows = gmPG2.run_rw_queries (
		link_obj = link_obj,
		queries = [{'sql': cmd, 'args': args}],
		end_tx = True,
		return_data = True
	)

	return cTagImage(aPK_obj = rows[0]['pk'])
#------------------------------------------------------------
def delete_tag_image(tag_image=None):
	args = {'pk': tag_image}
	cmd = """
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
	rows = gmPG2.run_rw_queries(queries = [{'sql': cmd, 'args': args}], return_data = True)
	if len(rows) == 0:
		return False
	return True

#============================================================
_SQL_get_person_tags = """SELECT * FROM dem.v_identity_tags WHERE %s"""

class cPersonTag(gmBusinessDBObject.cBusinessDBObject):

	_cmd_fetch_payload = _SQL_get_person_tags % "pk_identity_tag = %s"
	_cmds_store_payload = [
		"""
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
	_updatable_fields = ['fk_tag',	'comment']
	#--------------------------------------------------------
	def export_image2file(self, aChunkSize=0, filename=None):

		if self._payload['image_size'] == 0:
			return None

		if filename is None:
			suffix = None
			# preserve original filename extension if available
			if self._payload['filename'] is not None:
				name, suffix = os.path.splitext(self._payload['filename'])
				suffix = suffix.strip()
				if suffix == '':
					suffix = None
			# get unique filename
			filename = gmTools.get_unique_filename (
				prefix = 'gm-person_tag-',
				suffix = suffix
			)

		exported = gmPG2.bytea2file (
			data_query = {
				'sql': 'SELECT substring(image from %(start)s for %(size)s) FROM ref.tag_image WHERE pk = %(pk)s',
				'args': {'pk': self._payload['pk_tag_image']}
			},
			filename = filename,
			chunk_size = aChunkSize,
			data_size = self._payload['image_size']
		)
		if exported:
			return filename

		return None

#============================================================
# country/region related
#============================================================
def get_countries():
	cmd = """
		SELECT
			_(name) AS l10n_country, name, code, deprecated
		FROM dem.country
		ORDER BY l10n_country"""
	rows = gmPG2.run_ro_queries(queries = [{'sql': cmd}])
	return rows

#------------------------------------------------------------
def get_country_for_region(region=None):
	cmd = """
SELECT code_country, l10n_country FROM dem.v_region WHERE lower(l10n_region) = lower(%(region)s)
	union
SELECT code_country, l10n_country FROM dem.v_region WHERE lower(region) = lower(%(region)s)
"""
	rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': {'region': region}}])
	return rows

#------------------------------------------------------------
def map_country2code(country=None):
	cmd = """
		SELECT code FROM dem.country WHERE lower(_(name)) = lower(%(country)s)
			UNION
		SELECT code FROM dem.country WHERE lower(name) = lower(%(country)s)
	"""
	rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': {'country': country}}])
	if len(rows) == 0:
		return None
	return rows[0][0]

#------------------------------------------------------------
def map_urb_zip_region2country(urb=None, zip=None, region=None):

	args = {'urb': urb, 'zip': zip, 'region': region}
	cmd = """(
		-- find by using all known details
		SELECT
			1 AS rank,
			country,
			l10n_country,
			code_country
		FROM dem.v_urb WHERE
			postcode_urb = %(zip)s
				AND
			lower(urb) = lower(%(urb)s)
				AND
			(
				(lower(region) = lower(coalesce(%(region)s, 'state/territory/province/region not available')))
					OR
				(lower(l10n_region) = lower(coalesce(%(region)s, _('state/territory/province/region not available'))))
			)

		) UNION (

		-- find by using zip/urb
		SELECT
			2 AS rank,
			country,
			l10n_country,
			code_country
		FROM dem.v_urb WHERE
			postcode_urb = %(zip)s
				AND
			lower(urb) = lower(%(urb)s)

		) UNION (

		-- find by using zip/region
		SELECT
			2 AS rank,
			country,
			l10n_country,
			code_country
		FROM dem.v_urb WHERE
			postcode_urb = %(zip)s
				AND
			(
				(lower(region) = lower(%(region)s))
					OR
				(lower(l10n_region) = lower(%(region)s))
			)

		) UNION (

		-- find by using urb/region
		SELECT
			2 AS rank,
			country,
			l10n_country,
			code_country
		FROM dem.v_urb WHERE
			lower(urb) = lower(%(urb)s)
				AND
			((lower(region) = lower(%(region)s))
				OR
			(lower(l10n_region) = lower(%(region)s)))

		) UNION (

		-- find by region
		SELECT
			2 AS rank,
			country,
			l10n_country,
			code_country
		FROM dem.v_region WHERE
			lower(region) = lower(%(region)s)
				OR
			lower(l10n_region) = lower(%(region)s)

		) ORDER BY rank"""

	rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
	if len(rows) == 0:
		_log.debug('zip [%s] / urb [%s] / region [%s] => ??', zip, urb, region)
		return None
	if len(rows) > 2:
		_log.debug('zip [%s] / urb [%s] / region [%s] => [%s]', zip, urb, region, rows)
		return None
	country = rows[0]
	_log.debug('zip [%s] / urb [%s] / region [%s] => [%s]', zip, urb, region, country)
	return country

#------------------------------------------------------------
def map_urb_zip_country2region(urb=None, zip=None, country=None, country_code=None):

	args = {'urb': urb, 'zip': zip, 'country': country, 'country_code': country_code}
	cmd = """(
		-- find by using all known details
		SELECT
			1 AS rank,
			region,
			l10n_region,
			code_region
		FROM dem.v_urb WHERE
			postcode_urb = %(zip)s
				AND
			lower(urb) = lower(%(urb)s)
				AND
			(
				(lower(country) = lower(%(country)s))
					OR
				(lower(l10n_country) = lower(%(country)s))
					OR
				(code_country = %(country_code)s)
			)

		) UNION (

		-- find by zip / urb
		SELECT
			2 AS rank,
			region,
			l10n_region,
			code_region
		FROM dem.v_urb WHERE
			postcode_urb = %(zip)s
				AND
			lower(urb) = lower(%(urb)s)

		) UNION (

		-- find by zip / country
		SELECT
			2 AS rank,
			region,
			l10n_region,
			code_region
		FROM dem.v_urb WHERE
			postcode_urb = %(zip)s
				AND
			(
				(lower(country) = lower(%(country)s))
					OR
				(lower(l10n_country) = lower(%(country)s))
					OR
				(code_country = %(country_code)s)
			)

		) UNION (

		-- find by urb / country
		SELECT
			2 AS rank,
			region,
			l10n_region,
			code_region
		FROM dem.v_urb WHERE
			lower(urb) = lower(%(urb)s)
				AND
			(
				(lower(country) = lower(%(country)s))
					OR
				(lower(l10n_country) = lower(%(country)s))
					OR
				(code_country = %(country_code)s)
			)

		) ORDER BY rank"""

	rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])

	if len(rows) == 0:
		cmd = """
		-- find by country (some countries will only have one region)
		SELECT
			1 AS rank,		-- dummy to conform with function result structure at Python level
			region,
			l10n_region,
			code_region
		FROM dem.v_region WHERE
			(lower(country) = lower(%(country)s))
				OR
			(lower(l10n_country) = lower(%(country)s))
				OR
			(code_country = %(country_code)s)
		"""
		rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
		if len(rows) == 1:
			region = rows[0]
			_log.debug('zip [%s] / urb [%s] / country [%s] (%s) => [%s]', zip, urb, country, country_code, region)
			return region
		_log.debug('zip [%s] / urb [%s] / country [%s] (%s) => [??]', zip, urb, country, country_code)
		return None

	if len(rows) > 2:
		_log.debug('zip [%s] / urb [%s] / country [%s] (%s) => [%s]', zip, urb, country, country_code, rows)
		return None

	region = rows[0]
	_log.debug('zip [%s] / urb [%s] / country [%s] (%s) => [%s]', zip, urb, country, country_code, region)
	return region

#------------------------------------------------------------
def map_region2code(region=None, country_code=None):
	if country_code is None:
		cmd = """
			SELECT code FROM dem.region WHERE lower(_(name)) = lower(%(region)s)
				UNION
			SELECT code FROM dem.region WHERE lower(name) = lower(%(region)s)
		"""
	else:
		cmd = """
			SELECT code FROM dem.region WHERE lower(_(name)) = lower(%(region)s) AND lower(country) = lower(%(country_code)s)
				UNION
			SELECT code FROM dem.region WHERE lower(name) = %(region)s AND lower(country) = lower(%(country_code)s)
		"""
	args = {
		'country_code': country_code,
		'region': region
	}
	rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
	if len(rows) == 0:
		return None
	return rows[0][0]

#------------------------------------------------------------
def delete_region(region=None, delete_urbs=False):

	args = {'region': region}

	queries = []
	if delete_urbs:
		queries.append ({
			'sql': """
				delete from dem.urb du
				where
					du.fk_region = %(region)s
						and
					not exists (select 1 from dem.street ds where ds.id_urb = du.id)""",
			'args': args
		})

	queries.append ({
		'sql': """
			DELETE FROM dem.region d_r
			WHERE
				d_r.pk = %(region)s
					AND
				NOT EXISTS (SELECT 1 FROM dem.urb du WHERE du.fk_region = d_r.pk)""",
		'args': args
	})

	gmPG2.run_rw_queries(queries = queries)

	return True

#------------------------------------------------------------
def create_region(name=None, code=None, country=None):

	args = {'code': code, 'country': country, 'name': name}

	cmd = """SELECT EXISTS (SELECT 1 FROM dem.region WHERE name = %(name)s)"""
	rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])

	if rows[0][0]:
		return

	cmd = """
		INSERT INTO dem.region (
			code, country, name
		) VALUES (
			%(code)s, %(country)s, %(name)s
		)"""
	gmPG2.run_rw_queries(queries = [{'sql': cmd, 'args': args}])
#------------------------------------------------------------
def get_regions():
	cmd = """
		select
			l10n_region, l10n_country, region, code_region, code_country, pk_region, country_deprecated
		from dem.v_region
		order by l10n_country, l10n_region"""
	rows = gmPG2.run_ro_queries(queries = [{'sql': cmd}])
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
	_cmd_fetch_payload = "SELECT * FROM dem.v_address WHERE pk_address = %s"
	_cmds_store_payload = [
		"""UPDATE dem.address SET
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
	def format(self, single_line=False, verbose=False, show_type=False):
		if single_line:
			return format_address_single_line(address = self, show_type = False, verbose = verbose)
		return format_address(address = self, show_type = False)

	#--------------------------------------------------------
	def format_for_failsafe_output(self, max_width:int=80) -> list[str]:
		return format_address_for_failsafe_output(self, max_width)

	#--------------------------------------------------------
	def _get_as_map_url(self):
		"""Format as an openstreetmap location search URL.

		Specs:
			https://nominatim.org/release-docs/develop/api/Search/
		"""
		args = []
		if self['street']:
			street_num = self['street'].strip()
			if self['number']:
				street_num = street_num + ' ' + self['number'].strip()
			args.append('street=%s' % urllib.parse.quote_plus(street_num))
		if self['urb']:
			args.append('city=%s' % urllib.parse.quote_plus(self['urb'].strip()))
		if self['country']:
			args.append('country=%s' % urllib.parse.quote_plus(self['country'].strip()))
		if self['postcode']:
			args.append('postalcode=%s' % urllib.parse.quote_plus(self['postcode'].strip()))
		args.append('limit=3')
		return 'https://nominatim.openstreetmap.org/search?%s' % '&'.join(args)

	as_map_url = property(_get_as_map_url)

#------------------------------------------------------------
def address_exists(country_code=None, region_code=None, urb=None, postcode=None, street=None, number=None, subunit=None):

	cmd = """SELECT dem.address_exists(%(country_code)s, %(region_code)s, %(urb)s, %(postcode)s, %(street)s, %(number)s, %(subunit)s)"""
	args = {
		'country_code': country_code,
		'region_code': region_code,
		'urb': urb,
		'postcode': postcode,
		'street': street,
		'number': number,
		'subunit': subunit
	}

	rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
	if rows[0][0] is None:
		_log.debug('address does not exist')
		for key, val in args.items():
			_log.debug('%s: %s', key, val)
		return None

	return rows[0][0]

#------------------------------------------------------------
def create_address(country_code=None, region_code=None, urb=None, suburb=None, postcode=None, street=None, number=None, subunit=None):

	if suburb is not None:
		suburb = gmTools.none_if(suburb.strip(), '')

	pk_address = address_exists (
		country_code = country_code,
		region_code = region_code,
		urb = urb,
#		suburb = suburb,
		postcode = postcode,
		street = street,
		number = number,
		subunit = subunit
	)
	if pk_address is not None:
		return cAddress(aPK_obj = pk_address)

	cmd = """
SELECT dem.create_address (
	%(number)s,
	%(street)s,
	%(postcode)s,
	%(urb)s,
	%(region_code)s,
	%(country_code)s,
	%(subunit)s
)"""
	args = {
		'number': number,
		'street': street,
		'postcode': postcode,
		'urb': urb,
		'region_code': region_code,
		'country_code': country_code,
		'subunit': subunit
	}
	queries = [{'sql': cmd, 'args': args}]

	rows = gmPG2.run_rw_queries(queries = queries, return_data = True)
	adr = cAddress(aPK_obj = rows[0][0])

	if suburb is not None:
		queries = [{
			# CAVE: suburb will be ignored if there already is one
			'sql': "UPDATE dem.street SET suburb = %(suburb)s WHERE id = %(pk_street)s AND suburb IS NULL",
			'args': {'suburb': suburb, 'pk_street': adr['pk_street']}
		}]
		rows = gmPG2.run_rw_queries(queries = queries)

	return adr
#------------------------------------------------------------
def delete_address(pk_address=None):
	cmd = """
		DELETE FROM dem.address
		WHERE
			id = %(pk)s
				AND
			NOT EXISTS ((
				SELECT 1 FROM dem.org_unit WHERE fk_address = %(pk)s LIMIT 1
					) UNION (
				SELECT 1 FROM dem.lnk_identity2comm WHERE fk_address = %(pk)s LIMIT 1
					) UNION (
				SELECT 1 FROM dem.lnk_person_org_address WHERE id_address = %(pk)s LIMIT 1
			))
		"""
	gmPG2.run_rw_queries(queries = [{'sql': cmd, 'args': {'pk': pk_address}}])
	return True

#------------------------------------------------------------
def format_address_single_line(address=None, verbose=False, show_type=False):
	data = {
		'pk_adr': address['pk_address'],
		'street': address['street'],
		'notes_street': gmTools.coalesce(address['notes_street'], '', ' (%s)'),
		'number': address['number'],
		'subunit': gmTools.coalesce(address['subunit'], '', '/%s'),
		'notes_subunit': gmTools.coalesce(address['notes_subunit'], '', ' (%s)'),
		'zip': address['postcode'],
		'urb': address['urb'],
		'suburb': gmTools.coalesce(address['suburb'], '', ' (%s)'),
		'l10n_region': address['l10n_region'],
		'code_region': address['code_region'],
		'l10n_country': address['l10n_country'],
		'code_country': address['code_country']
	}
	if show_type:
		data['type'] = address['l10n_address_type']

	if verbose:
		if show_type:
			template = _('%(type)s: %(street)s %(number)s%(subunit)s, %(zip)s %(urb)s %(suburb)s, %(code_region)s, %(code_country)s (%(l10n_region)s, %(l10n_country)s)')
		else:
			template = _('%(street)s %(number)s%(subunit)s, %(zip)s %(urb)s %(suburb)s, %(code_region)s, %(code_country)s (%(l10n_region)s, %(l10n_country)s)')
	else:
		if show_type:
			template = _('%(type)s: %(street)s %(number)s%(subunit)s, %(zip)s %(urb)s, %(code_region)s, %(code_country)s (%(l10n_region)s, %(l10n_country)s)')
		else:
			template = _('%(street)s %(number)s%(subunit)s, %(zip)s %(urb)s, %(code_region)s, %(code_country)s (%(l10n_region)s, %(l10n_country)s)')

	return template % data

#------------------------------------------------------------
def format_address(address=None, show_type=False):
	data = {
		'pk_adr': address['pk_address'],
		'street': address['street'],
		'notes_street': gmTools.coalesce(address['notes_street'], '', ' (%s)'),
		'number': address['number'],
		'subunit': gmTools.coalesce(address['subunit'], '', '/%s'),
		'notes_subunit': gmTools.coalesce(address['notes_subunit'], '', ' (%s)'),
		'zip': address['postcode'],
		'urb': address['urb'],
		'suburb': gmTools.coalesce(address['suburb'], '', ' (%s)'),
		'l10n_region': address['l10n_region'],
		'code_region': address['code_region'],
		'l10n_country': address['l10n_country'],
		'code_country': address['code_country']
	}
	if show_type:
		data['type'] = address['l10n_address_type']
		template = _(
			'Address (%(type)s) [#%(pk_adr)s]\n'
			' Street: %(street)s%(notes_street)s\n'
			' Number/Unit: %(number)s%(subunit)s%(notes_subunit)s\n'
			' Location: %(zip)s %(urb)s%(suburb)s\n'
			' Region: %(l10n_region)s, %(code_region)s\n'
			' Country: %(l10n_country)s, %(code_country)s'
		)
	else:
		template = _(
			'Address [#%(pk_adr)s]\n'
			' Street: %(street)s%(notes_street)s\n'
			' Number/Unit: %(number)s%(subunit)s%(notes_subunit)s\n'
			' Location: %(zip)s %(urb)s%(suburb)s\n'
			' Region: %(l10n_region)s, %(code_region)s\n'
			' Country: %(l10n_country)s, %(code_country)s'
		)
	txt = template % data
	return txt.split('\n')

#------------------------------------------------------------
def format_address_for_failsafe_output(address:cAddress=None, max_width:int=80) -> list[str]:
	data = {
		'street': address['street'],
		'notes_street': gmTools.coalesce(address['notes_street'], '', ' (%s)'),
		'number': address['number'],
		'subunit': gmTools.coalesce(address['subunit'], '', '/%s'),
		'notes_subunit': gmTools.coalesce(address['notes_subunit'], '', ' (%s)'),
		'zip': address['postcode'],
		'urb': address['urb'],
		'suburb': gmTools.coalesce(address['suburb'], '', ' (%s)'),
		'l10n_region': address['l10n_region'],
		'code_region': address['code_region'],
		'l10n_country': address['l10n_country'],
		'code_country': address['code_country']
	}
	lines = []
	lines.append(gmTools.shorten_text(_('Street: %(street)s%(notes_street)s') % data, max_width))
	lines.append(gmTools.shorten_text(_('Number/Unit: %(number)s%(subunit)s%(notes_subunit)s') % data, max_width))
	lines.append(gmTools.shorten_text(_('Location: %(zip)s %(urb)s%(suburb)s') % data, max_width))
	lines.append(gmTools.shorten_text(_('Region: %(l10n_region)s, %(code_region)s') % data, max_width))
	lines.append(gmTools.shorten_text(_('Country: %(l10n_country)s, %(code_country)s') % data, max_width))
	return lines

#------------------------------------------------------------
def create_address_type(address_type=None):
	args = {'typ': address_type}
	cmd = 'INSERT INTO dem.address_type (name) SELECT %(typ)s WHERE NOT EXISTS (SELECT 1 FROM dem.address_type WHERE name = %(typ)s OR _(name) = %(typ)s)'
	rows = gmPG2.run_rw_queries(queries = [{'sql': cmd, 'args': args}])
	cmd = 'SELECT id FROM dem.address_type WHERE name = %(typ)s OR _(name) = %(typ)s'
	rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
	return rows[0][0]

#------------------------------------------------------------
def get_address_types(identity=None):
	cmd = 'select id as pk, name, _(name) as l10n_name from dem.address_type'
	rows = gmPG2.run_rw_queries(queries=[{'sql': cmd}])
	return rows

#------------------------------------------------------------
def get_addresses(order_by=None, return_pks=False):

	if order_by is None:
		order_by = ''
	else:
		order_by = 'ORDER BY %s' % order_by

	cmd = "SELECT * FROM dem.v_address %s" % order_by
	rows = gmPG2.run_ro_queries(queries = [{'sql': cmd}])
	if return_pks:
		return [ r['pk_address'] for r in rows ]
	return [ cAddress(row = {'data': r, 'pk_field': 'pk_address'}) for r in rows ]

#------------------------------------------------------------
def get_address_from_patient_address_pk(pk_patient_address=None):
	cmd = """
		SELECT * FROM dem.v_address WHERE
			pk_address = (
				SELECT id_address
				FROM dem.lnk_person_org_address
				WHERE id = %(pk_pat_adr)s
			)
	"""
	args = {'pk_pat_adr': pk_patient_address}
	rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
	if len(rows) == 0:
		return None

	return cAddress(row = {'data': rows[0], 'pk_field': 'pk_address'})

#===================================================================
def get_patient_address(pk_patient_address=None, return_pks=False):
	cmd = 'SELECT pk_address, pk_identity FROM dem.v_pat_addresses WHERE pk_lnk_person_org_address = %(pk)s'
	args = {'pk': pk_patient_address}
	rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
	if not rows:
		return None

	if return_pks:
		return [ r['pk_address'] for r in rows ]

	pk_data = {
		'pk_adr': rows[0]['pk_address'],
		'pk_pat': rows[0]['pk_identity']
	}
	return cPatientAddress(aPK_obj = pk_data)

#-------------------------------------------------------------------
def get_patient_address_by_type(pk_patient=None, adr_type=None):
	cmd = 'SELECT pk_address, pk_identity FROM dem.v_pat_addresses WHERE pk_identity = %(pat)s AND (address_type = %(typ)s OR l10n_address_type = %(typ)s)'
	args = {'pat': pk_patient, 'typ': adr_type}
	rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
	if len(rows) == 0:
		return None

	pk_data = {
		'pk_adr': rows[0]['pk_address'],
		'pk_pat': rows[0]['pk_identity']
	}
	return cPatientAddress(aPK_obj = pk_data)

#-------------------------------------------------------------------
class cPatientAddress(gmBusinessDBObject.cBusinessDBObject):

	_cmd_fetch_payload = 'SELECT * FROM dem.v_pat_addresses WHERE pk_address = %(pk_adr)s AND pk_identity = %(pk_pat)s'
	_cmds_store_payload = [
		"""UPDATE dem.lnk_person_org_address SET
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

	#--------------------------------------------------------
	def format(self, single_line=False, verbose=False, show_type=True):
		if single_line:
			return format_address_single_line(address = self, verbose = verbose, show_type = show_type)
		txt = format_address(address = self, show_type = show_type)
		return txt

	#--------------------------------------------------------
	def _get_address(self):
		return cAddress(aPK_obj = self._payload['pk_address'])

	address = property(_get_address)

	#--------------------------------------------------------
	def _get_as_map_url(self):
		return self.address.as_map_url

	as_map_url = property(_get_as_map_url)

#===================================================================
# communication channels API
#-------------------------------------------------------------------
class cCommChannel(gmBusinessDBObject.cBusinessDBObject):

	_cmd_fetch_payload = "SELECT * FROM dem.v_person_comms WHERE pk_lnk_identity2comm = %s"
	_cmds_store_payload = [
		"""UPDATE dem.lnk_identity2comm SET
				--fk_address = %(pk_address)s,
				fk_type = dem.create_comm_type(%(comm_type)s),
				url = %(url)s,
				is_confidential = %(is_confidential)s,
				comment = gm.nullify_empty_string(%(comment)s)
			WHERE
				pk = %(pk_lnk_identity2comm)s
					AND
				xmin = %(xmin_lnk_identity2comm)s
			RETURNING
				xmin AS xmin_lnk_identity2comm
		"""
	]
	_updatable_fields = [
		'url',
		'comm_type',
		'is_confidential',
		'comment'
	]

#-------------------------------------------------------------------
class cOrgCommChannel(gmBusinessDBObject.cBusinessDBObject):

	_cmd_fetch_payload = "SELECT * FROM dem.v_org_unit_comms WHERE pk_lnk_org_unit2comm = %s"
	_cmds_store_payload = [
		"""UPDATE dem.lnk_org_unit2comm SET
				fk_type = dem.create_comm_type(%(comm_type)s),
				url = %(url)s,
				is_confidential = %(is_confidential)s,
				comment = gm.nullify_empty_string(%(comment)s)
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
		'is_confidential',
		'comment'
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
		tbl = 'dem.lnk_identity2comm'
		col = 'fk_identity'
		view = 'dem.v_person_comms'
		view_pk = 'pk_lnk_identity2comm'
		channel_class = cCommChannel
	if pk_org_unit is not None:
		args['pk_owner'] = pk_org_unit
		tbl = 'dem.lnk_org_unit2comm'
		col = 'fk_org_unit'
		view = 'dem.v_org_unit_comms'
		view_pk = 'pk_lnk_org_unit2comm'
		channel_class = cOrgCommChannel

	if pk_channel_type is None:
		cmd = """INSERT INTO %s (
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
		cmd = """INSERT INTO %s (
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

	queries = [{'sql': cmd, 'args': args}]
	cmd = "SELECT * FROM %s WHERE %s = currval(pg_get_serial_sequence('%s', 'pk'))" % (view, view_pk, tbl)
	queries.append({'sql': cmd})

	rows = gmPG2.run_rw_queries(queries = queries, return_data = True)

	if pk_identity is not None:
		return cCommChannel(row = {'pk_field': view_pk, 'data': rows[0]})

	return channel_class(row = {'pk_field': view_pk, 'data': rows[0]})
#-------------------------------------------------------------------
def delete_comm_channel(pk=None, pk_patient=None, pk_org_unit=None):
	if pk_patient is not None:
		query = {
			'sql': "DELETE FROM dem.lnk_identity2comm WHERE pk = %(pk)s AND fk_identity = %(pat)s",
			'args': {'pk': pk, 'pat': pk_patient}
		}
	if pk_org_unit is not None:
		query = {
			'sql': "DELETE FROM dem.lnk_org_unit2comm WHERE pk = %(pk)s AND fk_org_unit = %(unit)s",
			'args': {'pk': pk, 'unit': pk_org_unit}
		}
	gmPG2.run_rw_queries(queries = [query])
#-------------------------------------------------------------------
def get_comm_channel_types():
	cmd = "SELECT pk, _(description) AS l10n_description, description FROM dem.enum_comm_types"
	rows = gmPG2.run_ro_queries(queries = [{'sql': cmd}])
	return rows
#-------------------------------------------------------------------
def delete_comm_channel_type(pk_channel_type=None):
	cmd = """
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
	gmPG2.run_rw_queries(queries = [{'sql': cmd, 'args': {'pk': pk_channel_type}}])
	return True
#===================================================================
#-------------------------------------------------------------------

#==============================================================================
#----------------------------------------------------------------
#----------------------------------------------------------------
#------------------------------------------------------------------
#----------------------------------------------------------------
#-------------------------------------------------------------------------------
#============================================================
# callbacks
#------------------------------------------------------------
def _post_patient_selection(**kwargs):
	print("received post_patient_selection notification")
	print(kwargs['kwds'])
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
			'country_code': 'Germany',
			'region_code': 'Sachsen',
			'urb': 'Hannover',
			'postcode': '06672',
			'street': 'Rommelsberger Strasse',
			'number': '11'
			},
			{
			'country_code': 'DE',
			'region_code': 'SN',
			'urb': 'Hannover',
			'postcode': '06671',
			'street': 'Tonnenstraße',
			'number': '65',
			'subunit': 'Parterre'
			},
			{
			'country_code': 'DE',
			'region_code': 'SN',
			'urb': 'Hannover',
			'postcode': '06671',
			'street': 'Tonnenstraße',
			'number': '65',
			'subunit': '1. Stock'
			},
			{
			'country_code': 'DE',
			'region_code': 'SN',
			'urb': 'Hannover',
			'postcode': '06671',
			'street': 'Tonnenstraße',
			'number': '65',
			'subunit': '1. Stock'
			},
			{
#			'country': 'DE',
#			'region_code': 'HV',
			'urb': 'Hannover',
			'postcode': '06671',
			'street': 'Tonnenstraße',
			'number': '65',
			'subunit': '1. Stock'
			},
		]

		for adr in addresses:
			print(adr)
			exists = address_exists(**adr)
			if exists is None:
				print("address does not exist")
			else:
				print("address exists, primary key:", exists)

	#--------------------------------------------------------
	def test_create_address():
		address = create_address (
			country_code = 'DE',
			region_code = 'SN',
			urb ='Hannover',
			suburb ='Grabenthal',
			postcode ='06672',
			street = 'Rommelsberger Strasse',
			number = '11'
#			,notes_subunit = '2.Stock oben'
		)
		print("created existing address")
		print(address.format())

		su = str(random.random())

		address = create_address (
			country_code = 'DE',
			region_code = 'SN',
			urb ='Hannover',
			suburb ='Grabenthal',
			postcode ='06672',
			street = 'Rommelsberger Strasse',
			number = '11',
#			notes_subunit = '2.Stock oben',
			subunit = su
		)
		print("created new address with subunit", su)
		print(address)
		print(address.format())
		print(address.as_map_url)
		print("deleted address:", delete_address(pk_address = address['pk_address']))
	#--------------------------------------------------------
	def test_get_countries():
		for c in get_countries():
			print(c)
	#--------------------------------------------------------
	def test_get_country_for_region():
		region = input("Please enter a region: ")
		print("country for region [%s] is: %s" % (region, get_country_for_region(region = region)))
	#--------------------------------------------------------
	def test_delete_tag():
		if delete_tag_image(tag_image = 9999):
			print("deleted tag 9999")
		else:
			print("did not delete tag 9999")
		if delete_tag_image(tag_image = 1):
			print("deleted tag 1")
		else:
			print("did not delete tag 1")
	#--------------------------------------------------------
	def test_tag_images():
		tag = cTagImage(aPK_obj = 1)
		print(tag)
		#print get_tag_images()
	#--------------------------------------------------------
	def test_get_billing_address():
		print(get_patient_address_by_type(pk_patient = 12, adr_type = 'billing'))

	#--------------------------------------------------------
	def test_map_urb_zip_region2country():
		print(map_urb_zip_region2country(urb = 'Kassel', zip = '34119', region = 'Hessen'))
		print(map_urb_zip_region2country(urb = 'Kassel', zip = None, region = 'Hessen'))
		print(map_urb_zip_region2country(urb = None, zip = '34119', region = 'Hessen'))
		print(map_urb_zip_region2country(urb = 'Kassel', zip = '34119', region = None))

	#--------------------------------------------------------
	def test_map_urb_zip_country2region():
		print(map_urb_zip_country2region(urb = 'Kassel', zip = '34119', country = 'Germany', country_code = 'DE'))
		print(map_urb_zip_country2region(urb = 'Kassel', zip = '34119', country = 'Germany', country_code = None))
		print(map_urb_zip_country2region(urb = 'Kassel', zip = '34119', country = 'Deutschland', country_code = 'DE'))
		print(map_urb_zip_country2region(urb = 'Kassel', zip = '34119', country = 'Deutschland', country_code = None))
		print(map_urb_zip_country2region(urb = 'Kassel', zip = '34119', country = None, country_code = 'DE'))
		print(map_urb_zip_country2region(urb = 'Kassel', zip = '34119', country = None, country_code = None))

#		print map_urb_zip_country2region(urb = 'Kassel', zip = '34119', country = u'Deutschland', country_code = 'DE')
#		print map_urb_zip_country2region(urb = 'Kassel', zip = '34119', country = u'Deutschland', country_code = 'DE')
#		print map_urb_zip_country2region(urb = 'Kassel', zip = '34119', country = u'Deutschland', country_code = 'DE')
#		print map_urb_zip_country2region(urb = 'Kassel', zip = '34119', country = u'Deutschland', country_code = 'DE')

	#--------------------------------------------------------
	#gmPG2.get_connection()
	gmPG2.request_login_params(setup_pool = True)

	#test_address_exists()
	#test_create_address()
	#test_get_countries()
	#test_get_country_for_region()
	#test_delete_tag()
	#test_tag_images()
	#test_get_billing_address()
	#test_map_urb_zip_region2country()
	#test_map_urb_zip_country2region()
