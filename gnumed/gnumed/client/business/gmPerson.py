# -*- coding: utf-8 -*-

"""GNUmed patient objects.

This is a patient object intended to let a useful client-side
API crystallize from actual use in true XP fashion.
"""
#============================================================
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL"

# std lib
import sys
import time
import datetime as pyDT
import threading
import logging
import inspect
from xml.etree import ElementTree as etree

# GNUmed
if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmLog2
from Gnumed.pycommon import gmI18N
if __name__ == '__main__':
	_ = lambda x:x
	gmI18N.activate_locale()
	gmI18N.install_domain()
from Gnumed.pycommon import gmDispatcher
from Gnumed.pycommon import gmExceptions
from Gnumed.pycommon import gmBorg
from Gnumed.pycommon import gmNull
from Gnumed.pycommon import gmBusinessDBObject
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmPG2
from Gnumed.pycommon import gmDateTime
from Gnumed.pycommon import gmMatchProvider
from Gnumed.pycommon import gmHooks

from Gnumed.business import gmDemographicRecord
from Gnumed.business import gmProviderInbox
from Gnumed.business import gmExportArea
from Gnumed.business import gmBilling
from Gnumed.business import gmAutoHints
from Gnumed.business import gmGender
from Gnumed.business.gmDocuments import cDocumentFolder
from Gnumed.business.gmClinicalRecord import cClinicalRecord


_log = logging.getLogger('gm.person')

#============================================================
_MERGE_SCRIPT_HEADER = """-- GNUmed patient merge script
-- created: %(date)s
-- patient to keep : #%(pat2keep)s
-- patient to merge: #%(pat2del)s
--
-- You can EASILY cause mangled data by uncritically applying this script, so ...
-- ... BE POSITIVELY SURE YOU UNDERSTAND THE FULL EXTENT OF WHAT IT DOES !


--set default_transaction_read_only to off;

BEGIN;
"""

#============================================================
def external_id_exists(pk_issuer:int, value:str) -> int:
	"""Check whether an external ID exists for a given ID issuer.

	Args:
		pk_issuer: primary key of external ID issuer (say, the Department of Motor Vehicles, DMV)
		value: value of external ID (say, the driver's license ID)

	Returns:
		Count of stored external IDs for the given issuer.
	"""
	cmd = 'SELECT COUNT(*) FROM dem.lnk_identity2ext_id WHERE fk_origin = %(issuer)s AND external_id = %(val)s'
	args = {'issuer': pk_issuer, 'val': value}
	rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
	return rows[0][0]

#============================================================
def get_potential_person_dupes(lastnames:str, dob:pyDT.datetime, firstnames:str=None, active_only:bool=True) -> int:
	"""Get number of potential duplicates of a person.

	Args:
		lastnames: last name(s) to search for
		dob: date of birth to search for, timestamp truncated to days
		firstnames: first name(s) to search for if given
		active_only: search among _all_ patients or among active patients only

	Returns:
		Count of matches (= potential duplicates for the arguments).
	"""
	assert (lastnames is not None), '<lastnames> required'
	assert (dob is not None), '<dob> required'
	args = {
		'last': lastnames,
		'dob': dob
	}
	where_parts = [
		"lastnames = %(last)s",
		"dem.date_trunc_utc('day', dob) = dem.date_trunc_utc('day', %(dob)s)"
	]
	if firstnames is not None:
		if firstnames.strip() != '':
			where_parts.append("firstnames ~* %(first)s")
			# the \m makes "firstnames" match at any word boundary
			args['first'] = '\\m' + firstnames.strip()
	if active_only:
		cmd = """SELECT COUNT(*) FROM dem.v_active_persons WHERE %s""" % ' AND '.join(where_parts)
	else:
		cmd = """SELECT COUNT(*) FROM dem.v_all_persons WHERE %s""" % ' AND '.join(where_parts)
	rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
	return rows[0][0]

#============================================================
def get_person_duplicates(lastnames:str, firstnames:str, dob:pyDT.datetime, gender:str, comment:str) -> list:
	"""Check whether a given person record exists in the database.

	Args:
		lastnames: last names to search form, case insensitive
		firstnames: first names to search for, case insensitive
		dob: date of birth to search for, truncated to days
		gender: gender, case insensitive
		comment: comment to search for, used for de-duplication, case insensitive

	Returns:
		List of primary keys of persons matching the given criteria.
	"""
	args = {
		'last': lastnames.strip(),
		'first': firstnames.strip(),
		'dob': dob,
		'gender': gmTools.none_if (
			value = gender,
			none_equivalent = '',
			strip_string = True
		),
		'cmt': gmTools.none_if (
			value = comment,
			none_equivalent = '',
			strip_string = True
		)
	}
	cmd = 'SELECT dem.get_person_duplicates(%(dob)s, %(last)s, %(first)s, %(gender)s, %(cmt)s)'
	rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
	return rows[0][0]

#============================================================
# FIXME: make this work as a mapping type, too
class cDTO_person(object):

	def __init__(self):
		self.identity = None
		self.external_ids = []
		self.comm_channels = []
		self.addresses = []

		self.firstnames = None
		self.lastnames = None
		self.title = None
		self.gender = None
		self.dob = None
		self.dob_is_estimated = False
		self.source = self.__class__.__name__

		self.dob_formats = []
		self.dob_tz = None

	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def keys(self):
		return 'firstnames lastnames dob gender title'.split()
	#--------------------------------------------------------
	def delete_from_source(self):
		pass
	#--------------------------------------------------------
	def _is_unique(self):
		where_snippets = [
			'firstnames = %(first)s',
			'lastnames = %(last)s'
		]
		args = {
			'first': self.firstnames,
			'last': self.lastnames
		}
		if self.dob is not None:
			where_snippets.append("dem.date_trunc_utc('day'::text, dob) = dem.date_trunc_utc('day'::text, %(dob)s)")
			args['dob'] = self.dob.replace(hour = 23, minute = 59, second = 59)
		if self.gender is not None:
			where_snippets.append('gender = %(sex)s')
			args['sex'] = self.gender
		cmd = 'SELECT COUNT(*) FROM dem.v_person_names WHERE %s' % ' AND '.join(where_snippets)
		rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])

		return rows[0][0] == 1

	is_unique = property(_is_unique)

	#--------------------------------------------------------
	def _exists(self):
		where_snippets = [
			'firstnames = %(first)s',
			'lastnames = %(last)s'
		]
		args = {
			'first': self.firstnames,
			'last': self.lastnames
		}
		if self.dob is not None:
			where_snippets.append("dem.date_trunc_utc('day'::text, dob) = dem.date_trunc_utc('day'::text, %(dob)s)")
			args['dob'] = self.dob.replace(hour = 23, minute = 59, second = 59)
		if self.gender is not None:
			where_snippets.append('gender = %(sex)s')
			args['sex'] = self.gender
		cmd = 'SELECT COUNT(*) FROM dem.v_person_names WHERE %s' % ' AND '.join(where_snippets)
		rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])

		return rows[0][0] > 0

	exists = property(_exists)

	#--------------------------------------------------------
	def get_candidate_identities(self, can_create=False):
		"""Generate generic queries.

		- not locale dependant
		- data -> firstnames, lastnames, dob, gender

		shall we mogrify name parts ? probably not as external
		sources should know what they do

		finds by inactive name, too, but then shows
		the corresponding active name ;-)

		Returns list of matching identities (may be empty)
		or None if it was told to create an identity but couldn't.
		"""
		where_snippets = []
		args = {}

		where_snippets.append('lower(firstnames) = lower(%(first)s)')
		args['first'] = self.firstnames

		where_snippets.append('lower(lastnames) = lower(%(last)s)')
		args['last'] = self.lastnames

		if self.dob is not None:
			where_snippets.append("dem.date_trunc_utc('day'::text, dob) = dem.date_trunc_utc('day'::text, %(dob)s)")
			args['dob'] = self.dob.replace(hour = 23, minute = 59, second = 59)

		if self.gender is not None:
			where_snippets.append('lower(gender) = lower(%(sex)s)')
			args['sex'] = self.gender

		# FIXME: allow disabled persons ?
		cmd = """
			SELECT *, '%s' AS match_type
			FROM dem.v_active_persons
			WHERE
				pk_identity IN (
					SELECT pk_identity FROM dem.v_person_names WHERE %s
				)
			ORDER BY lastnames, firstnames, dob""" % (
		_('external patient source (name, gender, date of birth)'),
		' AND '.join(where_snippets)
		)

		try:
			rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
		except Exception:
			_log.error('cannot get candidate identities for dto "%s"' % self)
			_log.exception('query %s' % cmd)
			rows = []

		if len(rows) == 0:
			_log.debug('no candidate identity matches found')
			if not can_create:
				return []
			ident = self.import_into_database()
			if ident is None:
				return None
			identities = [ident]
		else:
			identities = [ cPerson(row = {'pk_field': 'pk_identity', 'data': row}) for row in rows ]

		return identities
	#--------------------------------------------------------
	def import_into_database(self):
		"""Imports self into the database."""

		self.identity = create_identity (
			firstnames = self.firstnames,
			lastnames = self.lastnames,
			gender = self.gender,
			dob = self.dob
		)

		if self.identity is None:
			return None

		self.identity['dob_is_estimated'] = self.dob_is_estimated is True
		if self.title is not None:
			self.identity['title'] = self.title
		self.identity.save()

		for ext_id in self.external_ids:
			try:
				self.identity.add_external_id (
					type_name = ext_id['name'],
					value = ext_id['value'],
					issuer = ext_id['issuer'],
					comment = ext_id['comment']
				)
			except Exception:
				_log.exception('cannot import <external ID> from external data source')
				gmLog2.log_stack_trace()

		for comm in self.comm_channels:
			try:
				self.identity.link_comm_channel (
					comm_medium = comm['channel'],
					url = comm['url']
				)
			except Exception:
				_log.exception('cannot import <comm channel> from external data source')
				gmLog2.log_stack_trace()

		for adr in self.addresses:
			try:
				self.identity.link_address (
					adr_type = adr['type'],
					number = adr['number'],
					subunit = adr['subunit'],
					street = adr['street'],
					postcode = adr['zip'],
					urb = adr['urb'],
					region_code = adr['region_code'],
					country_code = adr['country_code']
				)
			except Exception:
				_log.exception('cannot import <address> from external data source')
				gmLog2.log_stack_trace()

		return self.identity
	#--------------------------------------------------------
	def import_extra_data(self, *args, **kwargs):
		pass
	#--------------------------------------------------------
	def remember_external_id(self, name=None, value=None, issuer=None, comment=None):
		value = value.strip()
		if value == '':
			return
		name = name.strip()
		if name == '':
			raise ValueError(_('<name> cannot be empty'))
		issuer = issuer.strip()
		if issuer == '':
			raise ValueError(_('<issuer> cannot be empty'))
		self.external_ids.append({'name': name, 'value': value, 'issuer': issuer, 'comment': comment})
	#--------------------------------------------------------
	def remember_comm_channel(self, channel=None, url=None):
		url = url.strip()
		if url == '':
			return
		channel = channel.strip()
		if channel == '':
			raise ValueError(_('<channel> cannot be empty'))
		self.comm_channels.append({'channel': channel, 'url': url})
	#--------------------------------------------------------
	def remember_address(self, number=None, street=None, urb=None, region_code=None, zip=None, country_code=None, adr_type=None, subunit=None):
		number = number.strip()
		if number == '':
			raise ValueError(_('<number> cannot be empty'))
		street = street.strip()
		if street == '':
			raise ValueError(_('<street> cannot be empty'))
		urb = urb.strip()
		if urb == '':
			raise ValueError(_('<urb> cannot be empty'))
		zip = zip.strip()
		if zip == '':
			raise ValueError(_('<zip> cannot be empty'))
		country_code = country_code.strip()
		if country_code == '':
			raise ValueError(_('<country_code> cannot be empty'))
		if region_code is not None:
			region_code = region_code.strip()
		if region_code in [None, '']:
			region_code = '??'
		self.addresses.append ({
			'type': adr_type,
			'number': number,
			'subunit': subunit,
			'street': street,
			'zip': zip,
			'urb': urb,
			'region_code': region_code,
			'country_code': country_code
		})
	#--------------------------------------------------------
	# customizing behaviour
	#--------------------------------------------------------
	def __str__(self):
		return '<%s (%s) @ %s: %s %s (%s) %s%s>' % (
			self.__class__.__name__,
			self.source,
			id(self),
			self.lastnames.upper(),
			self.firstnames,
			self.gender,
			gmTools.bool2subst(self.dob_is_estimated, '~', '', ''),
			self.dob
		)

	#--------------------------------------------------------
	def __setattr__(self, attr, val):
		"""Do some sanity checks on self.* access."""

		if attr == 'gender':
			if val is None:
				object.__setattr__(self, attr, val)
				return

			tag = gmGender.map_gender2tag(val)
			if tag:
				object.__setattr__(self, attr, tag)
				return

			raise ValueError('invalid gender: [%s]' % val)

		if attr == 'dob':
			if val is not None:
				if isinstance(val, str):
					dob = self.__parse_dob_str(val)
					if dob is None:
						raise ValueError('cannot parse DOB [%s]' % val)
					val = dob
				if not isinstance(val, pyDT.datetime):
					raise TypeError('invalid type for DOB (must be datetime.datetime): %s [%s]' % (type(val), val))
				if val.tzinfo is None:
					raise ValueError('datetime.datetime instance is lacking a time zone: [%s]' % val.isoformat())

		object.__setattr__(self, attr, val)
		return

	#--------------------------------------------------------
	def __getitem__(self, attr):
		return getattr(self, attr)

	#--------------------------------------------------------
	def __parse_dob_str(self, dob_str):
		for dob_format in self.dob_formats:
			try:
				dob = pyDT.datetime.strptime(dob_str, dob_format)
			except ValueError:
				_log.exception('cannot parse DOB [%s] with [%s]', dob_str, dob_format)
				continue
			if self.dob_tz is None:
				raise ValueError('lacking TZ information in DOB [%s] and/or format [%s]' % (dob_str, dob_format))

			dob = dob.replace(tzinfo = self.dob_tz)
			return dob

		return None

#============================================================
class cPersonName(gmBusinessDBObject.cBusinessDBObject):
	_cmd_fetch_payload = "SELECT * FROM dem.v_person_names WHERE pk_name = %s"
	_cmds_store_payload = [
		"""UPDATE dem.names SET
			active = FALSE
		WHERE
			%(active_name)s IS TRUE				-- act only when needed and only
				AND
			id_identity = %(pk_identity)s		-- on names of this identity
				AND
			active IS TRUE						-- which are active
				AND
			id != %(pk_name)s					-- but NOT *this* name
			""",
		"""update dem.names set
			active = %(active_name)s,
			preferred = %(preferred)s,
			comment = %(comment)s
		where
			id = %(pk_name)s and
			id_identity = %(pk_identity)s and	-- belt and suspenders
			xmin = %(xmin_name)s""",
		"""select xmin as xmin_name from dem.names where id = %(pk_name)s"""
	]
	_updatable_fields = [
		'active_name',
		'preferred',
		'comment'
	]
	#--------------------------------------------------------
	def __setitem__(self, attribute, value):
		if attribute == 'active_name':
			# cannot *directly* deactivate a name, only indirectly
			# by activating another one
			# FIXME: should be done at DB level
			if self._payload['active_name'] is True:
				return
		gmBusinessDBObject.cBusinessDBObject.__setitem__(self, attribute, value)

	#--------------------------------------------------------
	def _get_description(self):
		return '%(last)s, %(title)s %(first)s%(nick)s' % {
			'last': self._payload['lastnames'],
			'title': gmTools.coalesce (
				self._payload['title'],
				gmGender.map_gender2salutation(self._payload['gender'])
			),
			'first': self._payload['firstnames'],
			'nick': gmTools.coalesce(self._payload['preferred'], '', " '%s'", '%s')
		}

	description = property(_get_description)

#============================================================
_SQL_get_active_person = "SELECT * FROM dem.v_active_persons WHERE pk_identity = %s"
_SQL_get_any_person = "SELECT * FROM dem.v_all_persons WHERE pk_identity = %s"

class cPerson(gmBusinessDBObject.cBusinessDBObject):
	_cmd_fetch_payload = _SQL_get_any_person
	_cmds_store_payload = [
		"""UPDATE dem.identity SET
				gender = %(gender)s,
				dob = %(dob)s,
				dob_is_estimated = %(dob_is_estimated)s,
				tob = %(tob)s,
				title = gm.nullify_empty_string(%(title)s),
				fk_marital_status = %(pk_marital_status)s,
				deceased = %(deceased)s,
				emergency_contact = gm.nullify_empty_string(%(emergency_contact)s),
				fk_emergency_contact = %(pk_emergency_contact)s,
				fk_primary_provider = %(pk_primary_provider)s,
				comment = gm.nullify_empty_string(%(comment)s)
			WHERE
				pk = %(pk_identity)s and
				xmin = %(xmin_identity)s
			RETURNING
				xmin AS xmin_identity"""
	]
	_updatable_fields = [
		"title",
		"dob",
		"tob",
		"gender",
		"pk_marital_status",
		'deceased',
		'emergency_contact',
		'pk_emergency_contact',
		'pk_primary_provider',
		'comment',
		'dob_is_estimated'
	]
	#--------------------------------------------------------
	def _get_ID(self):
		return self._payload['pk_identity']

	ID = property(_get_ID)

	#--------------------------------------------------------
	def __setitem__(self, attribute:str, value):

		if attribute == 'dob':
			if value is None:
				super().__setitem__(attribute, value)
				return

			if not isinstance(value, pyDT.datetime):
				raise TypeError('[%s]: type [%s] (%s) invalid for attribute [dob], must be datetime.datetime or None' % (self.__class__.__name__, type(value), value))

			if value.tzinfo is None:
				raise ValueError('datetime.datetime instance is lacking a time zone: [%s]' % value.isoformat())

			if not self._payload['dob']:
				super().__setitem__(attribute, value)
				return

			# compare DOB at seconds level
			old_dob_str = self._payload['dob'].strftime('%Y %m %d %H %M %S')
			new_dob_str = value.strftime('%Y %m %d %H %M %S')
			if new_dob_str == old_dob_str:
				return

		super().__setitem__(attribute, value)

	#--------------------------------------------------------
	def cleanup(self):
		pass

	#--------------------------------------------------------
	def _get_is_patient(self) -> bool:
		return identity_is_patient(self._payload['pk_identity'])

	def _set_is_patient(self, turn_into_patient:bool):
		if not turn_into_patient:
			return

		SQL = """
			INSERT INTO clin.patient (fk_identity)
			SELECT %(pk_ident)s WHERE NOT EXISTS (
				SELECT 1 FROM clin.patient c_p WHERE fk_identity = %(pk_ident)s
			)"""
		args = {'pk_ident': self._payload['pk_identity']}
		gmPG2.run_rw_queries(queries = [{'sql': SQL, 'args': args}])

	is_patient = property(_get_is_patient, _set_is_patient)

	#--------------------------------------------------------
	def _get_as_patient(self) -> 'cPatient':
		return cPatient(self._payload['pk_identity'])

	as_patient = property(_get_as_patient)

	#--------------------------------------------------------
	def _get_staff_id(self) -> int:
		cmd = "SELECT pk FROM dem.staff WHERE fk_identity = %(pk)s"
		args = {'pk': self._payload['pk_identity']}
		rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
		if rows:
			return rows[0][0]
		return None

	staff_id = property(_get_staff_id)

	#--------------------------------------------------------
	# identity API
	#--------------------------------------------------------
	def _get_gender_symbol(self) -> str:
		return gmGender.map_gender2symbol(self._payload['gender'])

	gender_symbol = property(_get_gender_symbol)

	#--------------------------------------------------------
	def _get_gender_string(self) -> str:
		return gmGender.map_gender2string(gender = self._payload['gender'])

	gender_string = property(_get_gender_string)

	#--------------------------------------------------------
	def get_active_name(self) -> cPersonName:
		names = self.get_names(active_only = True)
		if names:
			return names[0]

		_log.error('cannot retrieve active name for patient [%s]', self._payload['pk_identity'])
		return None

	active_name = property(get_active_name)

	#--------------------------------------------------------
	def get_names(self, active_only:bool=False, exclude_active:bool=False) -> list[cPersonName]:
		args = {'pk_pat': self._payload['pk_identity']}
		where_parts = ['pk_identity = %(pk_pat)s']
		if active_only:
			where_parts.append('active_name is True')
		if exclude_active:
			where_parts.append('active_name is False')
		cmd = """
			SELECT *
			FROM dem.v_person_names
			WHERE %s
			ORDER BY active_name DESC, lastnames, firstnames
		""" % ' AND '.join(where_parts)
		rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
		if rows:
			return [ cPersonName(row = {'data': r, 'pk_field': 'pk_name'}) for r in rows ]

		return []

	#--------------------------------------------------------
	def get_description_gender(self, with_nickname:bool=False) -> str:
		if with_nickname:
			template = _('%(last)s %(first)s%(title)s%(nick)s (%(sex)s)')
		else:
			template = _('%(last)s %(first)s%(title)s (%(sex)s)')
		return template % {
			'last': self._payload['lastnames'].upper(),
			'title': gmTools.coalesce(self._payload['title'], '', ' (%s)'),
			'first': self._payload['firstnames'],
			'nick': gmTools.coalesce(self._payload['preferred'], '', " '%s'"),
			'sex': self.gender_symbol
		}

	description_gender = property(get_description_gender)

	#--------------------------------------------------------
	def get_description(self, with_nickname:bool=True) -> str:
		if with_nickname:
			template = _('%(last)s,%(title)s %(first)s%(nick)s')
		else:
			template = _('%(last)s,%(title)s %(first)s')
		return template % {
			'last': self._payload['lastnames'],
			'title': gmTools.coalesce(self._payload['title'], '', ' %s'),
			'first': self._payload['firstnames'],
			'nick': gmTools.coalesce(self._payload['preferred'], '', " '%s'")
		}

	description = property(get_description)

	#--------------------------------------------------------
	def add_name(self, firstnames:str, lastnames:str, active:bool=True) -> cPersonName:
		"""Add a name.

		@param firstnames The first names.
		@param lastnames The last names.
		@param active When True, the new name will become the active one (hence setting other names to inactive)
		@type active A bool instance
		"""
		name = create_name(self.ID, firstnames, lastnames, active)
		if active:
			self.refetch_payload()
		return name

	#--------------------------------------------------------
	def delete_name(self, name=None):
		cmd = "delete from dem.names where id = %(name)s and id_identity = %(pat)s"
		args = {'name': name['pk_name'], 'pat': self.ID}
		gmPG2.run_rw_queries(queries = [{'sql': cmd, 'args': args}])
		# can't have been the active name as that would raise an
		# exception (since no active name would be left) so no
		# data refetch needed

	#--------------------------------------------------------
	def set_nickname(self, nickname=None):
		"""
		Set the nickname. Setting the nickname only makes sense for the currently
		active name.
		@param nickname The preferred/nick/warrior name to set.
		"""
		if self._payload['preferred'] == nickname:
			return True

		SQL = 'SELECT dem.set_nickname(%(pk_pat)s, %(nick)s)'
		args = {'pk_pat': self.ID, 'nick': nickname}
		gmPG2.run_rw_queries(queries = [{'sql': SQL, 'args': args}])
		# setting nickname doesn't change dem.identity, so other fields
		# of dem.v_active_persons do not get changed as a consequence of
		# setting the nickname, hence locally setting nickname matches
		# in-database reality
		self._payload['preferred'] = nickname
		#self.refetch_payload()
		return True

	#--------------------------------------------------------
	def get_tags(self, order_by:str=None) -> list[gmDemographicRecord.cPersonTag]:
		if order_by is None:
			order_by = ''
		else:
			order_by = 'ORDER BY %s' % order_by

		cmd = gmDemographicRecord._SQL_get_person_tags % ('pk_identity = %%(pat)s %s' % order_by)
		rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': {'pat': self.ID}}])

		return [ gmDemographicRecord.cPersonTag(row = {'data': r, 'pk_field': 'pk_identity_tag'}) for r in rows ]

	tags = property(get_tags)

	#--------------------------------------------------------
	def add_tag(self, tag) -> gmDemographicRecord.cPersonTag:
		args = {
			'tag': tag,
			'identity': self.ID
		}

		# already exists ?
		cmd = "SELECT pk FROM dem.identity_tag WHERE fk_tag = %(tag)s AND fk_identity = %(identity)s"
		rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
		if len(rows) > 0:
			return gmDemographicRecord.cPersonTag(aPK_obj = rows[0]['pk'])

		# no, add
		cmd = """
			INSERT INTO dem.identity_tag (
				fk_tag,
				fk_identity
			) VALUES (
				%(tag)s,
				%(identity)s
			)
			RETURNING pk
		"""
		rows = gmPG2.run_rw_queries(queries = [{'sql': cmd, 'args': args}], return_data = True)
		return gmDemographicRecord.cPersonTag(aPK_obj = rows[0]['pk'])

	#--------------------------------------------------------
	def remove_tag(self, tag):
		cmd = "DELETE FROM dem.identity_tag WHERE pk = %(pk)s"
		gmPG2.run_rw_queries(queries = [{'sql': cmd, 'args': {'pk': tag}}])

	#--------------------------------------------------------
	# external ID API
	#
	# since external IDs are not treated as first class
	# citizens (classes in their own right, that is), we
	# handle them *entirely* within cPerson, also they
	# only make sense with one single person (like names)
	# and are not reused (like addresses), so they are
	# truly added/deleted, not just linked/unlinked
	#--------------------------------------------------------
	def add_external_id(self, type_name=None, value=None, issuer=None, comment=None, pk_type=None):
		"""Adds an external ID to the patient.

		creates ID type if necessary
		"""
		# check for existing ID
		if pk_type is not None:
			cmd = """
				select * from dem.v_external_ids4identity where
				pk_identity = %(pat)s and
				pk_type = %(pk_type)s and
				value = %(val)s"""
		else:
			# by type/value/issuer
			if issuer is None:
				cmd = """
					select * from dem.v_external_ids4identity where
					pk_identity = %(pat)s and
					name = %(name)s and
					value = %(val)s"""
			else:
				cmd = """
					select * from dem.v_external_ids4identity where
						pk_identity = %(pat)s and
						name = %(name)s and
						value = %(val)s and
						issuer = %(issuer)s"""
		args = {
			'pat': self.ID,
			'name': type_name,
			'val': value,
			'issuer': issuer,
			'pk_type': pk_type
		}
		rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])

		# create new ID if not found
		if len(rows) == 0:

			args = {
				'pat': self.ID,
				'val': value,
				'type_name': type_name,
				'pk_type': pk_type,
				'issuer': issuer,
				'comment': comment
			}

			if pk_type is None:
				cmd = """insert into dem.lnk_identity2ext_id (external_id, fk_origin, comment, id_identity) values (
					%(val)s,
					(select dem.add_external_id_type(%(type_name)s, %(issuer)s)),
					%(comment)s,
					%(pat)s
				)"""
			else:
				cmd = """insert into dem.lnk_identity2ext_id (external_id, fk_origin, comment, id_identity) values (
					%(val)s,
					%(pk_type)s,
					%(comment)s,
					%(pat)s
				)"""

			rows = gmPG2.run_rw_queries(queries = [{'sql': cmd, 'args': args}])

		# or update comment of existing ID
		else:
			row = rows[0]
			if comment is not None:
				# comment not already there ?
				if gmTools.coalesce(row['comment'], '').find(comment.strip()) == -1:
					comment = '%s%s' % (gmTools.coalesce(row['comment'], '', '%s // '), comment.strip)
					cmd = "update dem.lnk_identity2ext_id set comment = %(comment)s where id=%(pk)s"
					args = {'comment': comment, 'pk': row['pk_id']}
					rows = gmPG2.run_rw_queries(queries = [{'sql': cmd, 'args': args}])

	#--------------------------------------------------------
	def update_external_id(self, pk_id=None, type=None, value=None, issuer=None, comment=None):
		"""Edits an existing external ID.

		Creates ID type if necessary.
		"""
		cmd = """
			UPDATE dem.lnk_identity2ext_id SET
				fk_origin = (SELECT dem.add_external_id_type(%(type)s, %(issuer)s)),
				external_id = %(value)s,
				comment = gm.nullify_empty_string(%(comment)s)
			WHERE
				id = %(pk)s
		"""
		args = {'pk': pk_id, 'value': value, 'type': type, 'issuer': issuer, 'comment': comment}
		gmPG2.run_rw_queries(queries = [{'sql': cmd, 'args': args}])

	#--------------------------------------------------------
	def get_external_ids(self, id_type=None, issuer:str=None):
		where_parts = ['pk_identity = %(pat)s']
		args = {'pat': self.ID}
		if id_type:
			where_parts.append('name = %(name)s')
			args['name'] = id_type.strip()
		if issuer:
			where_parts.append('issuer = %(issuer)s')
			args['issuer'] = issuer.strip()

		cmd = "SELECT * FROM dem.v_external_ids4identity WHERE %s" % ' AND '.join(where_parts)
		rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
		return rows

	external_ids = property(get_external_ids)

	#--------------------------------------------------------
	def delete_external_id(self, pk_ext_id:int=None):
		cmd = """
			DELETE FROM dem.lnk_identity2ext_id
			WHERE id_identity = %(pat)s AND id = %(pk)s"""
		args = {'pat': self.ID, 'pk': pk_ext_id}
		gmPG2.run_rw_queries(queries = [{'sql': cmd, 'args': args}])

	#--------------------------------------------------------
	def suggest_external_id(self, target:str=None) -> str:
		dob = self.get_formatted_dob(format = '%Y%m%d', none_string = '?dob?')
		gender = gmTools.coalesce(self['gender'], '?gender?')
		pk = '#GMd::PK::%s#' % self.ID
		name = self.active_name
		last = ' '.join(p for p in name['lastnames'].split("-"))
		last = ' '.join(p for p in last.split("."))
		last = ' '.join(p for p in last.split("'"))
		last = ''.join(gmTools.capitalize(text = p, mode = gmTools.CAPS_FIRST_ONLY) for p in last.split(' '))
		first = ' '.join(p for p in name['firstnames'].split("-"))
		first = ' '.join(p for p in first.split("."))
		first = ' '.join(p for p in first.split("'"))
		first = ''.join(gmTools.capitalize(text = p, mode = gmTools.CAPS_FIRST_ONLY) for p in first.split(' '))
		suggestion_parts = ['GMd']
		if target:
			suggestion_parts.append(target)
		suggestion_parts.append(last)
		suggestion_parts.append(first)
		suggestion_parts.append(dob)
		suggestion_parts.append(gender)
		suggestion_parts.append(pk)
		suggestion = '-'.join (suggestion_parts)
		return suggestion

	external_id_suggestion = property(suggest_external_id)

	#--------------------------------------------------------
	def suggest_external_ids(self, target:str=None) -> list[str]:
		"""Suggest external IDs for this person."""
		dob = self.get_formatted_dob(format = '%Y%m%d', none_string = '?dob?')
		gender = gmTools.coalesce(self['gender'], '?gender?')
		pk = '#GMd::PK::%s#' % self.ID
		suggestions = []
		for name in self.get_names(active_only = False, exclude_active = False):
			last = ' '.join(part for part in name['lastnames'].split("-"))
			last = ' '.join(part for part in last.split("."))
			last = ' '.join(part for part in last.split("'"))
			last = ''.join(gmTools.capitalize(text = part, mode = gmTools.CAPS_FIRST_ONLY) for part in last.split(' '))
			first = ' '.join(part for part in name['firstnames'].split("-"))
			first = ' '.join(part for part in first.split("."))
			first = ' '.join(part for part in first.split("'"))
			first = ''.join(gmTools.capitalize(text = part, mode = gmTools.CAPS_FIRST_ONLY) for part in first.split(' '))
			suggestion_parts = ['GMd']
			if target:
				suggestion_parts.append(target)
			suggestion_parts.append(last)
			suggestion_parts.append(first)
			suggestion_parts.append(dob)
			suggestion_parts.append(gender)
			suggestion_parts.append(pk)
			suggestion = '-'.join(suggestion_parts)
			suggestions.append(suggestion)
		return suggestions

	#--------------------------------------------------------
	#--------------------------------------------------------
	def assimilate_identity(self, other_identity:'cPerson'=None, link_obj=None, dry_run:bool=True) -> tuple[bool, str]:
		"""Merge another identity into this one (self).

		Args:
			other_identity: another cPerson instance to be assimilated, and then deleted
			dry_run:

			* True: only create SQL script containing the queries to merge the identities
			* False: create SQL script and perform the assimilation by running the queries

		Returns:
			A tuple of (result state, information):

			* (True, None): nothing to do (say, same identity)
			* (True, SQL script file name)
			* (False, error message)
		"""
		if other_identity.ID == self.ID:
			return True, None

		curr_pat = gmCurrentPatient()
		if curr_pat.connected:
			if other_identity.ID == curr_pat.ID:
				return False, _('Cannot merge active patient into another patient.')

		distinguisher = _('merge of #%s into #%s @ %s') % (other_identity.ID, self.ID, gmDateTime.pydt_now_here().isoformat())
		queries:list[dict] = []
		args = {'pat2del': other_identity.ID, 'pat2keep': self.ID}
		# merge allergy state
		queries.append ({
			'sql': """
				UPDATE clin.allergy_state SET
					has_allergy = greatest (
						(SELECT has_allergy FROM clin.v_pat_allergy_state WHERE pk_patient = %(pat2del)s),
						(SELECT has_allergy FROM clin.v_pat_allergy_state WHERE pk_patient = %(pat2keep)s)
					),
					-- perhaps use least() to play it safe and make it appear longer ago than it might have been, actually ?
					last_confirmed = greatest (
						(SELECT last_confirmed FROM clin.v_pat_allergy_state WHERE pk_patient = %(pat2del)s),
						(SELECT last_confirmed FROM clin.v_pat_allergy_state WHERE pk_patient = %(pat2keep)s)
					)
				WHERE
					pk = (SELECT pk_allergy_state FROM clin.v_pat_allergy_state WHERE pk_patient = %(pat2keep)s)
			""",
			'args': args
		})
		# delete old allergy state
		queries.append ({
			'sql': 'DELETE FROM clin.allergy_state WHERE pk = (SELECT pk_allergy_state FROM clin.v_pat_allergy_state WHERE pk_patient = %(pat2del)s)',
			'args': args
		})
		# merge patient proxy
		queries.append ({
			'sql': """
				UPDATE clin.patient SET
					edc = coalesce (
						edc,
						(SELECT edc FROM clin.patient WHERE fk_identity = %(pat2del)s)
					)
				WHERE
					fk_identity = %(pat2keep)s
			""",
			'args': args
		})
		# transfer names
		# 1) hard-disambiguate all inactive names in old patient
		#    (the active one will be disambiguated upon being moved)
		queries.append ({
			'sql': """
				UPDATE dem.names d_n1 SET
					comment = coalesce (
						comment, ''
					) || coalesce (
						' (from identity: "' || (SELECT comment FROM dem.identity WHERE pk = %%(pat2del)s) || '")',
						''
					) || ' (during: "%s")'
				WHERE
					d_n1.id_identity = %%(pat2del)s
				""" % distinguisher,
			'args': args
		})
		# 2) move inactive ones (dupes are expected to have been eliminated in step 1 above)
		queries.append ({
			'sql': u"""
				UPDATE dem.names d_n SET
					id_identity = %(pat2keep)s,
					lastnames = lastnames || ' [' || random()::TEXT || ']'
				WHERE
					d_n.id_identity = %(pat2del)s
						AND
					d_n.active IS false
				""",
			'args': args
		})
		# 3) copy active name into pat2keep as an inactive name,
		#    because each identity MUST have at LEAST one name,
		#    we can't simply UPDATE over to pat2keep
		#    also, needs de-duplication or else it would conflict with
		#    *itself* on pat2keep
		queries.append ({
			'sql': """
				INSERT INTO dem.names (
					id_identity, active, firstnames, preferred, comment,
					lastnames
				)
					SELECT
						%(pat2keep)s, false, firstnames, preferred, comment,
						lastnames || ' [' || random()::text || ']'
					FROM dem.names d_n
					WHERE
						d_n.id_identity = %(pat2del)s
							AND
						d_n.active IS true
				""",
			'args': args
		})
		# disambiguate potential dupes
		# - same-url comm channels
		queries.append ({
			'sql': """
				UPDATE dem.lnk_identity2comm
				SET url = url || ' (%s)'
				WHERE
					fk_identity = %%(pat2del)s
						AND
					EXISTS (
						SELECT 1 FROM dem.lnk_identity2comm d_li2c
						WHERE d_li2c.fk_identity = %%(pat2keep)s AND d_li2c.url = url
					)
				""" % distinguisher,
			'args': args
		})
		# - same-value external IDs
		queries.append ({
			'sql': """
				UPDATE dem.lnk_identity2ext_id
				SET external_id = external_id || ' (%s)'
				WHERE
					id_identity = %%(pat2del)s
						AND
					EXISTS (
						SELECT 1 FROM dem.lnk_identity2ext_id d_li2e
						WHERE
							d_li2e.id_identity = %%(pat2keep)s
								AND
							d_li2e.external_id = external_id
								AND
							d_li2e.fk_origin = fk_origin
					)
				""" % distinguisher,
			'args': args
		})
		# - same addresses
		queries.append ({
			'sql': """
				DELETE FROM dem.lnk_person_org_address
				WHERE
					id_identity = %(pat2del)s
						AND
					id_address IN (
						SELECT id_address FROM dem.lnk_person_org_address d_lpoa
						WHERE d_lpoa.id_identity = %(pat2keep)s
					)
			""",
			'args': args
		})
		# find FKs pointing to dem.identity.pk
		FKs = gmPG2.get_foreign_keys2column (
			schema = 'dem',
			table = 'identity',
			column = 'pk'
		)
		# find FKs pointing to clin.patient.fk_identity
		FKs.extend (gmPG2.get_foreign_keys2column (
			schema = 'clin',
			table = 'patient',
			column = 'fk_identity'
		))
		# generate UPDATEs
		cmd_template = 'UPDATE %s SET %s = %%(pat2keep)s WHERE %s = %%(pat2del)s'
		for FK in FKs:
			if FK['referencing_table'] in ['dem.names', 'clin.patient']:
				continue
			queries.append ({
				'sql': cmd_template % (FK['referencing_table'], FK['referencing_column'], FK['referencing_column']),
				'args': args
			})
		# delete old patient proxy
		queries.append ({
			'sql': 'DELETE FROM clin.patient WHERE fk_identity = %(pat2del)s',
			'args': args
		})
		# remove old identity entry
		queries.append ({
			'sql': 'delete from dem.identity where pk = %(pat2del)s',
			'args': args
		})
		args['date'] = gmDateTime.pydt_now_here().strftime('%Y %B %d  %H:%M')
		script_name = gmTools.get_unique_filename(prefix = 'gm-assimilate-%(pat2del)s-into-%(pat2keep)s-' % args, suffix = '.sql')
		_log.warning('identity [%s] is about to assimilate identity [%s], SQL script [%s]', self.ID, other_identity.ID, script_name)
		with open(script_name, 'wt', encoding = 'utf8') as script:
			script.write(_MERGE_SCRIPT_HEADER % args)
			for query in queries:
				script.write(query['sql'] % args)
				script.write(';\n')
			script.write('\nROLLBACK;\n')
			script.write('--COMMIT;\n')
		if not dry_run:
			try:
				gmPG2.run_rw_queries(link_obj = link_obj, queries = queries, end_tx = True)
			except Exception:
				return False, _('The merge failed. Check the log and [%s]') % script_name

			self.add_external_id (
				type_name = 'merged GNUmed identity primary key',
				value = 'GNUmed::pk::%s' % other_identity.ID,
				issuer = 'GNUmed'
			)
		return True, script_name

	#--------------------------------------------------------
	#--------------------------------------------------------
	def put_on_waiting_list(self, urgency=0, comment=None, zone=None):
		cmd = """
			insert into clin.waiting_list (fk_patient, urgency, comment, area, list_position)
			values (
				%(pat)s,
				%(urg)s,
				%(cmt)s,
				%(area)s,
				(select coalesce((max(list_position) + 1), 1) from clin.waiting_list)
			)"""
		args = {'pat': self.ID, 'urg': urgency, 'cmt': comment, 'area': zone}
		gmPG2.run_rw_queries(queries = [{'sql': cmd, 'args': args}], verbose = True)
		gmHooks.run_hook_script(hook = 'after_waiting_list_modified')

	#--------------------------------------------------------
	def get_waiting_list_entry(self):
		cmd = """SELECT * FROM clin.v_waiting_list WHERE pk_identity = %(pat)s"""
		args = {'pat': self.ID}
		rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
		return rows

	waiting_list_entries = property(get_waiting_list_entry)

	#--------------------------------------------------------
	def _get_export_area(self):
		return gmExportArea.cExportArea(self.ID)

	export_area = property(_get_export_area)

	#--------------------------------------------------------
	def export_as_gdt(self, filename=None, encoding='iso-8859-15', external_id_type=None):

		from Gnumed.business import gmXdtMappings

		template = '%s%s%s\r\n'

		if filename is None:
			filename = gmTools.get_unique_filename (
				prefix = 'gm-patient-',
				suffix = '.gdt'
			)

		gdt_file = open(filename, mode = 'wt', encoding = encoding, errors = 'strict')

		gdt_file.write(template % ('013', '8000', '6301'))
		gdt_file.write(template % ('013', '9218', '2.10'))
		if external_id_type is None:
			gdt_file.write(template % ('%03d' % (9 + len(str(self.ID))), '3000', self.ID))
		else:
			ext_ids = self.get_external_ids(id_type = external_id_type)
			if len(ext_ids) > 0:
				gdt_file.write(template % ('%03d' % (9 + len(ext_ids[0]['value'])), '3000', ext_ids[0]['value']))
		gdt_file.write(template % ('%03d' % (9 + len(self._payload['lastnames'])), '3101', self._payload['lastnames']))
		gdt_file.write(template % ('%03d' % (9 + len(self._payload['firstnames'])), '3102', self._payload['firstnames']))
		gdt_file.write(template % ('%03d' % (9 + len(self._payload['dob'].strftime('%d%m%Y'))), '3103', self._payload['dob'].strftime('%d%m%Y')))
		gdt_file.write(template % ('010', '3110', gmXdtMappings.map_gender_gm2xdt[self._payload['gender']]))
		gdt_file.write(template % ('025', '6330', 'GNUmed::9206::encoding'))
		gdt_file.write(template % ('%03d' % (9 + len(encoding)), '6331', encoding))
		if external_id_type is None:
			gdt_file.write(template % ('029', '6332', 'GNUmed::3000::source'))
			gdt_file.write(template % ('017', '6333', 'internal'))
		else:
			if len(ext_ids) > 0:
				gdt_file.write(template % ('029', '6332', 'GNUmed::3000::source'))
				gdt_file.write(template % ('%03d' % (9 + len(external_id_type)), '6333', external_id_type))

		gdt_file.close()

		return filename
	#--------------------------------------------------------
	def export_as_xml_linuxmednews(self, filename=None):

		if filename is None:
			filename = gmTools.get_unique_filename (
				prefix = 'gm-LinuxMedNews_demographics-',
				suffix = '.xml'
			)

		dob_format = '%Y-%m-%d'
		pat = etree.Element('patient')

		first = etree.SubElement(pat, 'firstname')
		first.text = gmTools.coalesce(self._payload['firstnames'], '')

		last = etree.SubElement(pat, 'lastname')
		last.text = gmTools.coalesce(self._payload['lastnames'], '')

		# privacy
		#middle = etree.SubElement(pat, u'middlename')
		#middle.set(u'comment', _('preferred name/call name/...'))
		#middle.text = gmTools.coalesce(self._payload['preferred'], u'')

		pref = etree.SubElement(pat, 'name_prefix')
		pref.text = gmTools.coalesce(self._payload['title'], '')

		suff = etree.SubElement(pat, 'name_suffix')
		suff.text = ''

		dob = etree.SubElement(pat, 'DOB')
		dob.set('format', dob_format)
		dob.text = gmDateTime.format_dob(self._payload['dob'], format = dob_format, none_string = '')

		gender = etree.SubElement(pat, 'gender')
		gender.set('comment', self.gender_string)
		if self._payload['gender'] is None:
			gender.text = ''
		else:
			gender.text = gmGender.map_gender2mf[self._payload['gender']]

		home = etree.SubElement(pat, 'home_address')
		adrs = self.get_addresses(address_type = 'home')
		if len(adrs) > 0:
			adr = adrs[0]
			city = etree.SubElement(home, 'city')
			city.set('comment', gmTools.coalesce(adr['suburb'], ''))
			city.text = gmTools.coalesce(adr['urb'], '')

			region = etree.SubElement(home, 'region')
			region.set('comment', gmTools.coalesce(adr['l10n_region'], ''))
			region.text = gmTools.coalesce(adr['code_region'], '')

			zipcode = etree.SubElement(home, 'postal_code')
			zipcode.text = gmTools.coalesce(adr['postcode'], '')

			street = etree.SubElement(home, 'street')
			street.set('comment', gmTools.coalesce(adr['notes_street'], ''))
			street.text = gmTools.coalesce(adr['street'], '')

			no = etree.SubElement(home, 'number')
			no.set('subunit', gmTools.coalesce(adr['subunit'], ''))
			no.set('comment', gmTools.coalesce(adr['notes_subunit'], ''))
			no.text = gmTools.coalesce(adr['number'], '')

			country = etree.SubElement(home, 'country')
			country.set('comment', adr['l10n_country'])
			country.text = gmTools.coalesce(adr['code_country'], '')

		phone = etree.SubElement(pat, 'home_phone')
		rec = self.get_comm_channels(comm_medium = 'homephone')
		if len(rec) > 0:
			if not rec[0]['is_confidential']:
				phone.set('comment', gmTools.coalesce(rec[0]['comment'], ''))
				phone.text = rec[0]['url']

		phone = etree.SubElement(pat, 'work_phone')
		rec = self.get_comm_channels(comm_medium = 'workphone')
		if len(rec) > 0:
			if not rec[0]['is_confidential']:
				phone.set('comment', gmTools.coalesce(rec[0]['comment'], ''))
				phone.text = rec[0]['url']

		phone = etree.SubElement(pat, 'cell_phone')
		rec = self.get_comm_channels(comm_medium = 'mobile')
		if len(rec) > 0:
			if not rec[0]['is_confidential']:
				phone.set('comment', gmTools.coalesce(rec[0]['comment'], ''))
				phone.text = rec[0]['url']

		tree = etree.ElementTree(pat)
		tree.write(filename, encoding = 'UTF-8')

		return filename

	#--------------------------------------------------------
	def export_as_vcard(self, filename=None):
		# http://vobject.skyhouseconsulting.com/usage.html
		# http://en.wikipedia.org/wiki/VCard
		# http://svn.osafoundation.org/vobject/trunk/vobject/vcard.py
		# http://www.ietf.org/rfc/rfc2426.txt

		dob_format = '%Y%m%d'

		import vobject

		vc = vobject.vCard()
		vc.add('kind')
		vc.kind.value = 'individual'

		vc.add('fn')
		vc.fn.value = self.get_description(with_nickname = False)	# privacy
		vc.add('n')
		vc.n.value = vobject.vcard.Name(family = self._payload['lastnames'], given = self._payload['firstnames'])
		# privacy
		#vc.add(u'nickname')
		#vc.nickname.value = gmTools.coalesce(self._payload['preferred'], u'')
		vc.add('title')
		vc.title.value = gmTools.coalesce(self._payload['title'], '')
		vc.add('gender')
		# FIXME: dont know how to add gender_string after ';'
		vc.gender.value = gmGender.map_gender2vcard[self._payload['gender']]#, self.gender_string
		vc.add('bday')
		vc.bday.value = gmDateTime.format_dob(self._payload['dob'], format = dob_format, none_string = '')

		channels = self.get_comm_channels(comm_medium = 'homephone')
		if len(channels) > 0:
			if not channels[0]['is_confidential']:
				vc.add('tel')
				vc.tel.value = channels[0]['url']
				vc.tel.type_param = 'HOME'
		channels = self.get_comm_channels(comm_medium = 'workphone')
		if len(channels) > 0:
			if not channels[0]['is_confidential']:
				vc.add('tel')
				vc.tel.value = channels[0]['url']
				vc.tel.type_param = 'WORK'
		channels = self.get_comm_channels(comm_medium = 'mobile')
		if len(channels) > 0:
			if not channels[0]['is_confidential']:
				vc.add('tel')
				vc.tel.value = channels[0]['url']
				vc.tel.type_param = 'CELL'
		channels = self.get_comm_channels(comm_medium = 'fax')
		if len(channels) > 0:
			if not channels[0]['is_confidential']:
				vc.add('tel')
				vc.tel.value = channels[0]['url']
				vc.tel.type_param = 'FAX'
		channels = self.get_comm_channels(comm_medium = 'email')
		if len(channels) > 0:
			if not channels[0]['is_confidential']:
				vc.add('email')
				vc.tel.value = channels[0]['url']
				vc.tel.type_param = 'INTERNET'
		channels = self.get_comm_channels(comm_medium = 'web')
		if len(channels) > 0:
			if not channels[0]['is_confidential']:
				vc.add('url')
				vc.tel.value = channels[0]['url']
				vc.tel.type_param = 'INTERNET'

		adrs = self.get_addresses(address_type = 'home')
		if len(adrs) > 0:
			home_adr = adrs[0]
			vc.add('adr')
			vc.adr.type_param = 'HOME'
			vc.adr.value = vobject.vcard.Address()
			vc_adr = vc.adr.value
			vc_adr.extended = gmTools.coalesce(home_adr['subunit'], '')
			vc_adr.street = gmTools.coalesce(home_adr['street'], '', '%s ') + gmTools.coalesce(home_adr['number'], '')
			vc_adr.region = gmTools.coalesce(home_adr['l10n_region'], '')
			vc_adr.code = gmTools.coalesce(home_adr['postcode'], '')
			vc_adr.city = gmTools.coalesce(home_adr['urb'], '')
			vc_adr.country = gmTools.coalesce(home_adr['l10n_country'], '')

		#photo (base64)

		if filename is None:
			filename = gmTools.get_unique_filename (
				prefix = 'gm-patient-',
				suffix = '.vcf'
			)
		vcf = open(filename, mode = 'wt', encoding = 'utf8')
		try:
			vcf.write(vc.serialize())
		except UnicodeDecodeError:
			_log.exception('failed to serialize VCF data')
			vcf.close()
			return 'cannot-serialize.vcf'
		vcf.close()

		return filename

	#--------------------------------------------------------
	def export_as_mecard(self, filename=None):
		if filename is None:
			filename = gmTools.get_unique_filename (
				prefix = 'gm-patient-',
				suffix = '.mcf'
			)
		with open(filename, mode = 'wt', encoding = 'utf8') as mecard_file:
			mecard_file.write(self.MECARD)
		return filename

	#--------------------------------------------------------
	def _get_mecard(self):
		"""
		http://blog.thenetimpact.com/2011/07/decoding-qr-codes-how-to-format-data-for-qr-code-generators/
		https://www.nttdocomo.co.jp/english/service/developer/make/content/barcode/function/application/addressbook/index.html

		MECARD:N:NAME;ADR:pobox,subunit,unit,street,ort,region,zip,country;TEL:111111111;FAX:22222222;EMAIL:mail@praxis.org;

		MECARD:N:lastname,firstname;BDAY:YYYYMMDD;ADR:pobox,subunit,number,street,location,region,zip,country;EMAIL:...;TEL:...;FAX:...;URL:...;;
		MECARD:N:$<lastname::::>$,$<firstname::::>$;BDAY:$<date_of_birth::%Y%m%d::>$;ADR:,$<adr_subunit::home::>$,$<adr_number::home::>$,$<adr_street::home::>$,$<adr_location::home::>$,,$<adr_postcode::home::>$,$<adr_country::home::>$;;
		"""
		mecard_fields = [
			'MECARD:N:%s,%s' % (
				self._payload['lastnames'].strip(),
				self._payload['firstnames'].strip()
			)
		]
		if self._payload['dob'] is not None:
			mecard_fields.append('BDAY:%s' % self._payload['dob'].strftime('%Y%m%d'))
		adrs = self.get_addresses(address_type = 'home')
		if len(adrs) > 0:
			mecard_fields.append('ADR:,%(subunit)s,%(number)s,%(street)s,%(urb)s,,%(postcode)s,%(l10n_country)s' % adrs[0])
		comms = self.get_comm_channels(comm_medium = 'homephone')
		if len(comms) > 0:
			if not comms[0]['is_confidential']:
				mecard_fields.append('TEL:%s' % comms[0]['url'].strip())
		comms = self.get_comm_channels(comm_medium = 'fax')
		if len(comms) > 0:
			if not comms[0]['is_confidential']:
				mecard_fields.append('FAX:%s' % comms[0]['url'].strip())
		comms = self.get_comm_channels(comm_medium = 'email')
		if len(comms) > 0:
			if not comms[0]['is_confidential']:
				mecard_fields.append('EMAIL:%s' % comms[0]['url'].strip())
		if len(adrs) > 0:
			mecard_fields.append('URL:%s' % adrs[0].as_map_url)
		MECARD = ';'.join(mecard_fields) + ';'
		return MECARD

	MECARD = property(_get_mecard)

	#--------------------------------------------------------
	# occupations API
	#--------------------------------------------------------
	def get_occupations(self):
		return gmDemographicRecord.get_occupations(pk_identity = self.pk_obj)

	#--------------------------------------------------------
	def link_occupation(self, occupation=None, activities=None):
		"""Link an occupation with a patient, creating the occupation if it does not exists.

			@param occupation The name of the occupation to link the patient to.
		"""
		if (activities is None) and (occupation is None):
			return True

		occupation = occupation.strip()
		if len(occupation) == 0:
			return True

		if activities is not None:
			activities = activities.strip()

		args = {'act': activities, 'pat_id': self.pk_obj, 'job': occupation}

		cmd = "select activities from dem.v_person_jobs where pk_identity = %(pat_id)s and l10n_occupation = _(%(job)s)"
		rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])

		queries = []
		if len(rows) == 0:
			queries.append ({
				'sql': "INSERT INTO dem.lnk_job2person (fk_identity, fk_occupation, activities) VALUES (%(pat_id)s, dem.create_occupation(%(job)s), %(act)s)",
				'args': args
			})
		else:
			if rows[0]['activities'] != activities:
				queries.append ({
					'sql': "update dem.lnk_job2person set activities=%(act)s where fk_identity=%(pat_id)s and fk_occupation=(select id from dem.occupation where _(name) = _(%(job)s))",
					'args': args
				})

		rows = gmPG2.run_rw_queries(queries = queries)

		return True
	#--------------------------------------------------------
	def unlink_occupation(self, occupation=None):
		if occupation is None:
			return True
		occupation = occupation.strip()
		cmd = "delete from dem.lnk_job2person where fk_identity=%(pk)s and fk_occupation in (select id from dem.occupation where _(name) = _(%(job)s))"
		gmPG2.run_rw_queries(queries = [{'sql': cmd, 'args': {'pk': self.pk_obj, 'job': occupation}}])
		return True
	#--------------------------------------------------------
	# comms API
	#--------------------------------------------------------
	def get_comm_channels(self, comm_medium:str=None) -> list:
		SQL = 'select * from dem.v_person_comms where pk_identity = %(pk_pat)s'
		args = {'pk_pat': self.pk_obj}
		rows = gmPG2.run_ro_queries(queries = [{'sql': SQL, 'args': args}])
		if comm_medium:
			rows = [ r for r in rows if r['comm_type'] == comm_medium ]
		return [ gmDemographicRecord.cCommChannel(row = {
					'pk_field': 'pk_lnk_identity2comm',
					'data': r
				}) for r in rows
			]

	comm_channels = property(get_comm_channels)

	#--------------------------------------------------------
	def link_comm_channel(self, comm_medium=None, url=None, is_confidential=False, pk_channel_type=None):
		"""Link a communication medium with a patient.

		@param comm_medium The name of the communication medium.
		@param url The communication resource locator.
		@type url A str instance.
		@param is_confidential Whether the data must be treated as confidential.
		@type is_confidential A bool instance.
		"""
		comm_channel = gmDemographicRecord.create_comm_channel (
			comm_medium = comm_medium,
			url = url,
			is_confidential = is_confidential,
			pk_channel_type = pk_channel_type,
			pk_identity = self.pk_obj
		)
		return comm_channel
	#--------------------------------------------------------
	def unlink_comm_channel(self, comm_channel=None):
		gmDemographicRecord.delete_comm_channel (
			pk = comm_channel['pk_lnk_identity2comm'],
			pk_patient = self.pk_obj
		)
	#--------------------------------------------------------
	# contacts API
	#--------------------------------------------------------
	def get_addresses(self, address_type=None):
		cmd = "SELECT pk_address FROM dem.v_pat_addresses WHERE pk_identity = %(pat)s"
		args = {'pat': self.pk_obj}
		if address_type is not None:
			cmd = cmd + " AND address_type = %(typ)s"
			args['typ'] = address_type

		rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
		return [
			gmDemographicRecord.cPatientAddress(aPK_obj = {
				'pk_adr': r['pk_address'],
				'pk_pat': self.pk_obj
			}) for r in rows
		]

	#--------------------------------------------------------
	def link_address(self, number=None, street=None, postcode=None, urb=None, region_code=None, country_code=None, subunit=None, suburb=None, id_type=None, address=None, adr_type=None):
		"""Link an address with a patient, creating the address if it does not exists.

		@param id_type The primary key of the address type.
		"""
		if address is None:
			address = gmDemographicRecord.create_address (
				country_code = country_code,
				region_code = region_code,
				urb = urb,
				suburb = suburb,
				postcode = postcode,
				street = street,
				number = number,
				subunit = subunit
			)
		if address is None:
			return None

		# already linked ?
		cmd = "SELECT id_address FROM dem.lnk_person_org_address WHERE id_identity = %(pat)s AND id_address = %(adr)s"
		args = {'pat': self.pk_obj, 'adr': address['pk_address']}
		rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
		# no, link to person
		if not rows:
			args = {'pk_person': self.pk_obj, 'adr': address['pk_address'], 'type': id_type}
			cmd = """
				INSERT INTO dem.lnk_person_org_address(id_identity, id_address)
				VALUES (%(pk_person)s, %(adr)s)
				RETURNING id_address"""
			rows = gmPG2.run_rw_queries(queries = [{'sql': cmd, 'args': args}], return_data = True)
		pk_data = {
			'pk_adr': rows[0]['id_address'],
			'pk_pat': self.pk_obj
		}
		linked_adr = gmDemographicRecord.cPatientAddress(aPK_obj = pk_data)
		# possibly change type
		if id_type is None:
			if adr_type is not None:
				id_type = gmDemographicRecord.create_address_type(address_type = adr_type)
		if id_type is not None:
			linked_adr['pk_address_type'] = id_type
			linked_adr.save()
		return linked_adr

	#----------------------------------------------------------------------
	def unlink_address(self, address=None, pk_address=None):
		"""Remove an address from the patient.

		The address itself stays in the database.
		The address can be either cAdress or cPatientAdress.
		"""
		if pk_address is None:
			args = {'person': self.pk_obj, 'adr': address['pk_address']}
		else:
			args = {'person': self.pk_obj, 'adr': pk_address}
		cmd = """
			DELETE FROM dem.lnk_person_org_address
			WHERE
				dem.lnk_person_org_address.id_identity = %(person)s
					AND
				dem.lnk_person_org_address.id_address = %(adr)s
					AND
				NOT EXISTS(SELECT 1 FROM bill.bill WHERE fk_receiver_address = dem.lnk_person_org_address.id)
			"""
		gmPG2.run_rw_queries(queries = [{'sql': cmd, 'args': args}])
	#----------------------------------------------------------------------
	# bills API
	#----------------------------------------------------------------------
	def get_bills(self, order_by=None, pk_patient=None):
		return gmBilling.get_bills (
			order_by = order_by,
			pk_patient = self.pk_obj
		)

	bills = property(get_bills)

	#----------------------------------------------------------------------
	# relatives API
	#----------------------------------------------------------------------
	def get_relatives(self):
		cmd = """
			SELECT
				d_rt.description,
				d_vap.*
			FROM
				dem.v_all_persons d_vap,
				dem.relation_types d_rt,
				dem.lnk_person2relative d_lp2r
			WHERE
				(	d_lp2r.id_identity = %(pk)s
						AND
					d_vap.pk_identity = d_lp2r.id_relative
						AND
					d_rt.id = d_lp2r.id_relation_type
				) or (
					d_lp2r.id_relative = %(pk)s
						AND
					d_vap.pk_identity = d_lp2r.id_identity
						AND
					d_rt.inverse = d_lp2r.id_relation_type
				)"""
		rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': {'pk': self.pk_obj}}])
		if len(rows) == 0:
			return []
		return [(row[0], cPerson(row = {'data': row[1:], 'pk_field': 'pk_identity'})) for row in rows]

	#--------------------------------------------------------
	def link_new_relative(self, rel_type:str='parent') -> bool:
		# create new relative
		id_new_relative = create_dummy_identity()
		relative = cPerson(aPK_obj = id_new_relative)
		# pre-fill with data from ourselves
#		relative.copy_addresses(self)
		relative.add_name( '**?**', self.active_name['lastnames'])
		# and link the two
		SQL = """
			INSERT INTO dem.lnk_person2relative (
				id_identity, id_relative, id_relation_type
			) VALUES (
				%(pk_pat)s,
				%(pk_relative)s,
				(SELECT id FROM dem.relation_types WHERE description = %(relation)s)
			)"""
		args = {
			'pk_pat': self.ID,
			'pk_relative': id_new_relative,
			'relation': rel_type
		}
		gmPG2.run_rw_queries(queries = [{'sql': SQL, 'args': args}])
		return True

	#----------------------------------------------------------------------
	def delete_relative(self, relation):
		# unlink only, don't delete relative itself
		#self.set_relative(None, relation)
		pass

	#--------------------------------------------------------
	def _get_emergency_contact_from_database(self):
		if self._payload['pk_emergency_contact'] is None:
			return None
		return cPerson(self._payload['pk_emergency_contact'])

	emergency_contact_in_database = property(_get_emergency_contact_from_database)

	#----------------------------------------------------------------------
	# age/dob related
	#----------------------------------------------------------------------
	def get_formatted_dob(self, format='%Y %b %d', none_string=None, honor_estimation=False):
		return gmDateTime.format_dob (
			self._payload['dob'],
			format = format,
			none_string = none_string,
			dob_is_estimated = self._payload['dob_is_estimated'] and honor_estimation
		)

	#----------------------------------------------------------------------
	def get_medical_age(self, at_date=None):
		dob = self['dob']
		if dob is None:
			return '??'

		if at_date is None:
			if self['deceased']:
				at_date = self['deceased']
				_at_desc = _('date of death')
			else:
				at_date = gmDateTime.pydt_now_here()
				_at_desc = _('now')
		else:
			_at_desc = _('explicit')
		if dob > at_date:
			return _('invalid age: DOB [%s] after reference date [%s] (%s)') % (dob, at_date, _at_desc)

		return '%s%s' % (
			gmTools.bool2subst (
				self._payload['dob_is_estimated'],
				gmTools.u_almost_equal_to,
				''
			),
			gmDateTime.format_apparent_age_medically (
				age = gmDateTime.calculate_apparent_age (
					start = dob,
					end = at_date
				)
			)
		)

	medical_age = property(get_medical_age)

	#----------------------------------------------------------------------
	def dob_in_range(self, min_distance='1 week', max_distance='1 week'):
		if self['dob'] is None:
			return False

		cmd = 'select dem.dob_is_in_range(%(dob)s, %(min)s, %(max)s)'
		rows = gmPG2.run_ro_queries (
			queries = [{
				'sql': cmd,
				'args': {'dob': self['dob'], 'min': min_distance, 'max': max_distance}
			}]
		)
		return rows[0][0]

	#----------------------------------------------------------------------
	def _get_current_birthday_passed(self):
		if self['dob'] is None:
			return None
		now = gmDateTime.pydt_now_here()
		if now.month < self['dob'].month:
			return False
		if now.month > self['dob'].month:
			return True
		# -> DOB is this month
		if now.day < self['dob'].day:
			return False
		if now.day > self['dob'].day:
			return True
		# -> DOB is today
		return False

	current_birthday_passed = property(_get_current_birthday_passed)

	#----------------------------------------------------------------------
	def _get_birthday_this_year(self):
		if self['dob'] is None:
			return None
		now = gmDateTime.pydt_now_here()
		return gmDateTime.pydt_replace (
			dt = self['dob'],
			year = now.year,
			strict = False
		)

	birthday_this_year = property(_get_birthday_this_year)

	#----------------------------------------------------------------------
	def _get_birthday_next_year(self):
		if self['dob'] is None:
			return None
		now = gmDateTime.pydt_now_here()
		return gmDateTime.pydt_replace (
			dt = self['dob'],
			year = now.year + 1,
			strict = False
		)

	birthday_next_year = property(_get_birthday_next_year)

	#----------------------------------------------------------------------
	def _get_birthday_last_year(self):
		if self['dob'] is None:
			return None

		now = gmDateTime.pydt_now_here()
		return gmDateTime.pydt_replace (
			dt = self['dob'],
			year = now.year - 1,
			strict = False
		)

	birthday_last_year = property(_get_birthday_last_year)

	#----------------------------------------------------------------------
	# practice related
	#----------------------------------------------------------------------
	def get_last_contact(self):
		SQL = 'select pk_encounter, last_affirmed, l10n_type from clin.v_most_recent_encounters where pk_patient = %(pat)s'
		args = {'pat': self._payload['pk_identity']}
		rows = gmPG2.run_ro_queries(queries = [{'sql': SQL, 'args': args}])
		if rows:
			return rows[0]

		return None

	last_contact = property(get_last_contact)

	#----------------------------------------------------------------------
	def get_last_encounter(self):
		SQL = 'select * from clin.v_most_recent_encounters where pk_patient = %(pk_pat)s'
		args = {'pk_pat': self._payload['pk_identity']}
		rows = gmPG2.run_ro_queries(queries = [{'sql': SQL, 'args': args}])
		if rows:
			return rows[0]

		return None

	#--------------------------------------------------------
	def get_messages(self, order_by:str=None):
		return gmProviderInbox.get_inbox_messages(pk_patient = self._payload['pk_identity'], order_by = order_by)

	messages = property(get_messages)

	#--------------------------------------------------------
	def _get_overdue_messages(self):
		return gmProviderInbox.get_overdue_messages(pk_patient = self._payload['pk_identity'])

	overdue_messages = property(_get_overdue_messages)

	#--------------------------------------------------------
	def delete_message(self, pk:int=None):
		return gmProviderInbox.delete_inbox_message(inbox_message = pk)

	#--------------------------------------------------------
	def _get_dynamic_hints(self, pk_encounter:int=None):
		return gmAutoHints.get_hints_for_patient (
			pk_identity = self._payload['pk_identity'],
			pk_encounter = pk_encounter
		)

	dynamic_hints = property(_get_dynamic_hints)

	#--------------------------------------------------------
	def _get_suppressed_hints(self):
		return gmAutoHints.get_suppressed_hints(pk_identity = self._payload['pk_identity'])

	suppressed_hints = property(_get_suppressed_hints)

	#--------------------------------------------------------
	def _get_primary_provider_identity(self):
		if self._payload['pk_primary_provider'] is None:
			return None

		cmd = "SELECT * FROM dem.v_all_persons WHERE pk_identity = (SELECT pk_identity FROM dem.v_staff WHERE pk_staff = %(pk_staff)s)"
		args = {'pk_staff': self._payload['pk_primary_provider']}
		rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
		if len(rows) == 0:
			return None

		return cPerson(row = {'data': rows[0], 'pk_field': 'pk_identity'})

	primary_provider_identity = property(_get_primary_provider_identity)

	#--------------------------------------------------------
	def _get_primary_provider(self):
		if self._payload['pk_primary_provider'] is None:
			return None
		from Gnumed.business import gmStaff
		return gmStaff.cStaff(aPK_obj = self._payload['pk_primary_provider'])

	primary_provider = property(_get_primary_provider)

	#----------------------------------------------------------------------
	# convenience
	#----------------------------------------------------------------------
	def get_subdir_name(self) -> str:
		"""Format patient demographics into patient specific path name fragment."""

		return gmTools.fname_sanitize('%s-%s-%s-ID_%s' % (
			self._payload['lastnames'],
			self._payload['firstnames'],
			self.get_formatted_dob(format = '%Y-%m-%d'),
			self._payload['pk_identity']		# make unique across "same" patients
		))
		#).replace (
		#	u'\u2248', u''			# "approximately", having been added by dob_is_estimated
		#)

	subdir_name = property(get_subdir_name)

#============================================================
def identity_is_patient(pk_identity:int) -> bool | None:
	"""Check for identity to be set up as patient.

	Returns:
		True: is patient
		False: is not patient
		None: you don't have permissions to know
	"""
	SQL = 'SELECT 1 FROM clin.patient WHERE fk_identity = %(pk_pat)s'
	args = {'pk_pat': pk_identity}
	status = False
	try:
		rows = gmPG2.run_ro_queries(queries = [{'sql': SQL, 'args': args}])
		if rows:
			status = True
	except gmExceptions.AccessDenied:
		status = None
	return status

#============================================================
# helper functions
#------------------------------------------------------------
_yield = lambda *x: None

def set_yielder(yielder):
	if not callable(yielder):
		raise TypeError('yielder <%s> is not callable' % yielder)
	global _yield
	_yield = yielder
	_log.debug('setting yielder to <%s>', yielder)

#============================================================
class cPatient(cPerson):
	"""Represents a person which is a patient.

	- a specializing subclass of cPerson turning it into a patient
	- its use is to cache subobjects like EMR and document folder
	"""
	def __init__(self, aPK_obj=None, row=None):
		cPerson.__init__(self, aPK_obj = aPK_obj, row = row)
		self.__emr_access_lock = threading.Lock()
		self.__emr = None
		self.__doc_folder = None

	#--------------------------------------------------------
	def cleanup(self):
		"""Do cleanups before dying.

		- note that this may be called in a thread
		"""
		if self.__emr is not None:
			self.__emr.cleanup()
		if self.__doc_folder is not None:
			self.__doc_folder.cleanup()
		cPerson.cleanup(self)

	#----------------------------------------------------------
	def get_emr(self):
		_log.debug('accessing EMR for identity [%s], thread [%s]', self._payload['pk_identity'], threading.get_native_id())
		if self.is_patient is None:
			_log.error('trying to access EMR without required permissions')
			return None

		# fast path: already set, just return it
		if self.__emr is not None:
			return self.__emr

		stack_logged = False
		got_lock = self.__emr_access_lock.acquire(False)
		if not got_lock:
			# do some logging as we failed to get the lock
			call_stack = inspect.stack()
			call_stack.reverse()
			for idx in range(1, len(call_stack)):
				caller = call_stack[idx]
				_log.debug('%s[%s] @ [%s] in [%s]', ' '* idx, caller[3], caller[2], caller[1])
			del call_stack
			stack_logged = True
			# now loop a bit
			for idx in range(500):
				_yield()
				time.sleep(0.1)
				_yield()
				got_lock = self.__emr_access_lock.acquire(False)
				if got_lock:
					break
			if not got_lock:
				_log.error('still failed to acquire EMR access lock, aborting (thread [%s])', threading.get_native_id())
				self.__emr_access_lock.release()
				raise AttributeError('cannot lock access to EMR for identity [%s]' % self._payload['pk_identity'])

		_log.debug('pulling chart for identity [%s], thread [%s]', self._payload['pk_identity'], threading.get_native_id())
		if not stack_logged:
			# do some logging as we are pulling the chart for the first time
			call_stack = inspect.stack()
			call_stack.reverse()
			for idx in range(1, len(call_stack)):
				caller = call_stack[idx]
				_log.debug('%s[%s] @ [%s] in [%s]', ' '* idx, caller[3], caller[2], caller[1])
			del call_stack
			stack_logged = True

		self.is_patient = True
		emr = cClinicalRecord(aPKey = self._payload['pk_identity'])

		_log.debug('returning EMR for identity [%s], thread [%s]', self._payload['pk_identity'], threading.get_native_id())
		self.__emr = emr
		self.__emr_access_lock.release()
		return self.__emr

	emr = property(get_emr)

	#----------------------------------------------------------
	def get_document_folder(self):
		if self.is_patient is None:
			_log.error('trying to access EMR without required permissions')
			return None

		if self.__doc_folder is None:
			self.__doc_folder = cDocumentFolder(aPKey = self._payload['pk_identity'])
		return self.__doc_folder

	document_folder = property(get_document_folder)

#============================================================
class gmCurrentPatient(gmBorg.cBorg):
	"""Patient Borg to hold the currently active patient.

	There may be many instances of this but they all share state.

	The underlying dem.identity row must have .deleted set to FALSE.

	The sequence of events when changing the active patient:

		1) Registered callbacks are run.
			Those are run synchronously. If a callback
			returns False or throws an exception the
			patient switch is aborted. Callback code
			can rely on the patient still being active
			and to not go away until it returns. It
			is not passed any arguments and must return
			False or True.

		2) Signal "pre_patient_unselection" is sent.
			This does not wait for nor check results.
			The keyword pk_identity contains the
			PK of the person being switched away
			from.

		3) the current patient is unset (gmNull.cNull)

		4) Signal "current_patient_unset" is sent
			At this point resetting GUI fields to
			empty should be done. The active patient
			is not there anymore.

			This does not wait for nor check results.

		5) The current patient is set to the new value.
			The new patient can also remain gmNull.cNull
			in case the calling code explicitly unset
			the current patient.

		6) Signal "post_patient_selection" is sent.
			Code listening to this signal can
			assume that the new patient is
			already active.
	"""
	def __init__(self, patient=None, forced_reload=False):
		"""Initialization.
		Args:
			patient:

			* None: return currently active patient
			* -1: unset currently active patient
			* cPatient/cPerson instance: set active patient if possible
		"""
		try:
			self.patient
		except AttributeError:
			self.patient = gmNull.cNull()
			self.__register_interests()
			# set initial lock state,
			# this lock protects against activating another patient
			# when we are controlled from a remote application
			self.__lock_depth = 0
			# initialize callback state
			self.__callbacks_before_switching_away_from_patient = []

		# user wants copy of current patient
		if patient is None:
			return None

		# do nothing if patient is locked
		if self.locked:
			_log.error('patient [%s] is locked, cannot switch to [%s]' % (self.patient['pk_identity'], patient))
			return None

		_log.info('patient switch [%s] -> [%s] requested', self.patient, patient)

		# user wants to explicitly unset current patient
		if patient == -1:
			_log.debug('explicitly unsetting current patient')
			if not self.__run_callbacks_before_switching_away_from_patient():
				_log.error('not unsetting current patient, at least one pre-change callback failed')
				return None
			self.__send_pre_unselection_notification()
			self.patient.cleanup()
			self.patient = gmNull.cNull()
			self.__send_unselection_notification()
			# give it some time
			time.sleep(0.5)
			self.__send_selection_notification()
			return None

		# must be cPatient instance, then
		if not isinstance(patient, (cPatient, cPerson)):
			_log.error('cannot set active patient to [%s], must be either None, -1, cPatient or cPerson instance' % str(patient))
			raise TypeError('gmPerson.gmCurrentPatient.__init__(): <patient> must be None, -1, cPerson or cPatient instance but is: %s' % str(patient))

		#_log.info('patient switch [%s] -> [%s] requested', self.patient['pk_identity'], patient['pk_identity'])
		_log.info('patient switch [%s] -> [%s] requested', self.patient.ID, patient.ID)

		# same ID, no change needed
		#if (self.patient['pk_identity'] == patient['pk_identity']) and not forced_reload:
		if (self.patient.ID == patient.ID) and not forced_reload:
			return None

		# do not access "deleted" patients
		if patient['is_deleted']:
			_log.error('cannot set active patient to disabled dem.identity row: %s', patient)
			raise ValueError('gmPerson.gmCurrentPatient.__init__(): <person> is disabled: %s' % patient)

		# this blocks
		if not self.__run_callbacks_before_switching_away_from_patient():
			_log.error('at least one pre-change callback failed, not switching current patient')
			return None

		# everything seems swell
		self.__send_pre_unselection_notification()	# does not block
		self.patient.cleanup()
		self.patient = gmNull.cNull()
		self.__send_unselection_notification()		# does not block
		# give it some time
		time.sleep(0.5)
		self.patient = patient
		# for good measure ...
		# however, actually we want to get rid of that
#		self.patient.emr
		self.__send_selection_notification()		# does not block
		return None

	#--------------------------------------------------------
	def __register_interests(self):
		gmDispatcher.connect(signal = 'gm_table_mod', receiver = self._on_database_signal)

	#--------------------------------------------------------
	def _on_database_signal(self, **kwds):
		# we don't have a patient: don't process signals
		if isinstance(self.patient, gmNull.cNull):
			return True

		# we only care about identity and name changes
		if kwds['table'] not in ['dem.identity', 'dem.names']:
			return True

		# signal is not about our patient: ignore signal
		if int(kwds['pk_identity']) != self.patient.ID:
			return True

		if kwds['table'] == 'dem.identity':
			# we don't care about newly INSERTed or DELETEd patients
			if kwds['operation'] != 'UPDATE':
				return True

		self.patient.refetch_payload()
		return True

	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def register_before_switching_from_patient_callback(self, callback=None):
		# callbacks are run synchronously before
		# switching *away* from the current patient,
		# if a callback returns false the current
		# patient will not be switched away from,
		# callbacks will not be passed any arguments
		if not callable(callback):
			raise TypeError('callback [%s] not callable' % callback)

		self.__callbacks_before_switching_away_from_patient.append(callback)

	#--------------------------------------------------------
	def _get_connected(self):
		return (not isinstance(self.patient, gmNull.cNull))

	connected = property(_get_connected)

	#--------------------------------------------------------
	def _get_locked(self):
		return (self.__lock_depth > 0)

	def _set_locked(self, locked):
		if locked:
			self.__lock_depth = self.__lock_depth + 1
			gmDispatcher.send(signal = 'patient_locked', sender = self.__class__.__name__)
		else:
			if self.__lock_depth == 0:
				_log.error('lock/unlock imbalance, tried to refcount lock depth below 0')
				return
			else:
				self.__lock_depth = self.__lock_depth - 1
			gmDispatcher.send(signal = 'patient_unlocked', sender = self.__class__.__name__)

	locked = property(_get_locked, _set_locked)

	#--------------------------------------------------------
	def force_unlock(self):
		_log.info('forced patient unlock at lock depth [%s]' % self.__lock_depth)
		self.__lock_depth = 0
		gmDispatcher.send(signal = 'patient_unlocked', sender = self.__class__.__name__)

	#--------------------------------------------------------
	# patient change handling
	#--------------------------------------------------------
	def __run_callbacks_before_switching_away_from_patient(self):
		if isinstance(self.patient, gmNull.cNull):
			return True

		for call_back in self.__callbacks_before_switching_away_from_patient:
			try:
				successful = call_back()
			except Exception:
				_log.exception('callback [%s] failed', call_back)
				print("*** pre-change callback failed ***")
				print(type(call_back))
				print(call_back)
				return False

			if not successful:
				_log.error('callback [%s] returned False', call_back)
				return False

		return True

	#--------------------------------------------------------
	def __send_pre_unselection_notification(self):
		"""Sends signal when current patient is about to be unset.

		This does NOT wait for signal handlers to complete.
		"""
		kwargs = {
			'signal': 'pre_patient_unselection',
			'sender': self.__class__.__name__,
			'pk_identity': self.patient['pk_identity']
		}
		gmDispatcher.send(**kwargs)

	#--------------------------------------------------------
	def __send_unselection_notification(self):
		"""Sends signal when the previously active patient has
		   been unset during a change of active patient.

		This is the time to initialize GUI fields to empty values.

		This does NOT wait for signal handlers to complete.
		"""
		kwargs = {
			'signal': 'current_patient_unset',
			'sender': self.__class__.__name__
		}
		gmDispatcher.send(**kwargs)

	#--------------------------------------------------------
	def __send_selection_notification(self):
		"""Sends signal when another patient has actually been made active."""
		kwargs = {
			'signal': 'post_patient_selection',
			'sender': self.__class__.__name__,
			'pk_identity': self.patient['pk_identity'],
			'current_patient': self
		}
		gmDispatcher.send(**kwargs)

	#--------------------------------------------------------
	# __getattr__ handling
	#--------------------------------------------------------
	def __getattr__(self, attribute):
		# override __getattr__ here, not __getattribute__ because
		# the former is used _after_ ordinary attribute lookup
		# failed while the latter is applied _before_ ordinary
		# lookup (and is easy to drive into infinite recursion),
		# this is also why subsequent access to self.patient
		# simply returns the .patient member value :-)
		if attribute == 'patient':
			raise AttributeError
		if isinstance(self.patient, gmNull.cNull):
			_log.error("[%s]: cannot getattr(%s, '%s'), patient attribute not connected to a patient", self, self.patient, attribute)
			raise AttributeError("[%s]: cannot getattr(%s, '%s'), patient attribute not connected to a patient" % (self, self.patient, attribute))
		return getattr(self.patient, attribute)

	#--------------------------------------------------------
	# __get/setitem__ handling
	#--------------------------------------------------------
	def __getitem__(self, attribute = None):
		"""Return any attribute if known how to retrieve it by proxy.
		"""
		return self.patient[attribute]

	#--------------------------------------------------------
	def __setitem__(self, attribute, value):
		self.patient[attribute] = value

#============================================================
# match providers
#============================================================
class cMatchProvider_Provider(gmMatchProvider.cMatchProvider_SQL2):
	def __init__(self):
		gmMatchProvider.cMatchProvider_SQL2.__init__(
			self,
			queries = [
				"""SELECT
						pk_staff AS data,
						short_alias || ' (' || coalesce(title, '') || ' ' || firstnames || ' ' || lastnames || ')' AS list_label,
						short_alias || ' (' || coalesce(title, '') || ' ' || firstnames || ' ' || lastnames || ')' AS field_label
					FROM dem.v_staff
					WHERE
						is_active AND (
							short_alias %(fragment_condition)s OR
							firstnames %(fragment_condition)s OR
							lastnames %(fragment_condition)s OR
							db_user %(fragment_condition)s
						)
				"""
			]
		)
		self.setThresholds(1, 2, 3)

#============================================================
# convenience functions
#============================================================
def create_name(pk_person, firstnames, lastnames, active=False) -> cPersonName:
	queries = [{
		'sql': "select dem.add_name(%(pk_pat)s, %(fnames)s, %(lnames)s, %(active)s)",
		'args': {
			'pk_pat': pk_person,
			'fnames': firstnames,
			'lnames': lastnames,
			'active': active
		}
	}]
	rows = gmPG2.run_rw_queries(queries=queries, return_data=True)
	name = cPersonName(aPK_obj = rows[0][0])
	return name

#============================================================
def create_identity(gender=None, dob=None, lastnames:str=None, firstnames:str=None, comment:str=None):

	SQL = "INSERT INTO dem.identity (gender, dob, comment) VALUES (%(gender)s, %(dob)s, %(cmt)s)"
	args = {
		'gender': gender,
		'dob': dob,
		'cmt': comment
	}
	queries = [{'sql': SQL, 'args': args}]
	SQL = """
		INSERT INTO dem.names (
			id_identity,
			lastnames,
			firstnames
		) VALUES (
			currval('dem.identity_pk_seq'),
			coalesce(%(last)s, 'xxxDEFAULTxxx'),
			coalesce(%(first)s, 'xxxDEFAULTxxx')
		) RETURNING id_identity"""
	args = {'last': lastnames, 'first': firstnames}
	queries.append({'sql': SQL, 'args': args})
	try:
		rows = gmPG2.run_rw_queries(queries = queries, return_data = True)
	except Exception:
		_log.exception('cannot create identity')
		gmLog2.log_stack_trace()
		return None

	ident = cPerson(aPK_obj = rows[0][0])
	gmHooks.run_hook_script(hook = 'post_person_creation')
	return ident

#============================================================
def disable_identity(pk_identity):
	_log.info('disabling identity [%s]', pk_identity)
	cmd = "UPDATE dem.identity SET deleted = true WHERE pk = %(pk)s"
	args = {'pk': pk_identity}
	gmPG2.run_rw_queries(queries = [{'sql': cmd, 'args': args}])
	return True

#============================================================
def create_dummy_identity():
	cmd = "INSERT INTO dem.identity(gender) VALUES (NULL::text) RETURNING pk"
	rows = gmPG2.run_rw_queries (
		queries = [{'sql': cmd}],
		return_data = True
	)
	return cPerson(aPK_obj = rows[0][0])

#============================================================
def identity_exists(pk_identity):
	cmd = 'SELECT EXISTS(SELECT 1 FROM dem.identity where pk = %(pk)s)'
	args = {'pk': pk_identity}
	rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
	return rows[0][0]

#============================================================
def set_active_patient(patient=None, forced_reload=False):
	"""Set active patient.

	If patient is -1 the active patient will be UNset.
	"""
	if isinstance(patient, gmCurrentPatient):
		return True

	if isinstance(patient, cPatient):
		patient2activate = patient
	elif isinstance(patient, cPerson):
		patient2activate = patient.as_patient
	elif patient == -1:
		patient2activate = patient
	else:
		# maybe integer ?
		success, pk = gmTools.input2int(initial = patient, minval = 1)
		if not success:
			raise ValueError('<patient> must be either -1, >0, or a cPatient, cPerson or gmCurrentPatient instance, is: %s' % patient)

		# but also valid patient ID ?
		try:
			patient2activate = cPatient(aPK_obj = pk)
		except Exception:
			_log.exception('identity [%s] not found' % patient)
			return False

	# attempt to switch
	try:
		gmCurrentPatient(patient = patient2activate, forced_reload = forced_reload)
	except Exception:
		_log.exception('error changing active patient to [%s]' % patient)
		return False

	return True

#============================================================
def get_person_IDs():
	cmd = 'SELECT pk FROM dem.identity'
	rows = gmPG2.run_ro_queries(queries = [{'sql': cmd}])
	return [ r[0] for r in rows ]

#============================================================
def get_persons_from_pks(pks=None):
	return [ cPerson(aPK_obj = pk) for pk in pks ]

#============================================================
def get_persons_by_external_id(external_id:str=None, external_id_type:str=None, issuer:str=None) -> list:
	raise NotImplementedError

#============================================================
def get_person_from_xdt(filename=None, encoding=None, dob_format=None):
	from Gnumed.business import gmXdtObjects
	return gmXdtObjects.read_person_from_xdt(filename=filename, encoding=encoding, dob_format=dob_format)

#============================================================
def get_persons_from_pracsoft_file(filename=None, encoding='ascii'):
	from Gnumed.business import gmPracSoftAU
	return gmPracSoftAU.read_persons_from_pracsoft_file(filename=filename, encoding=encoding)

#============================================================
# main/testing
#============================================================
if __name__ == '__main__':

	if len(sys.argv) == 1:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	gmLog2.print_logfile_name()

	gmDateTime.init()

	#--------------------------------------------------------
	def test_description_gender():
		ident = cPerson(12)
		print(ident.description_gender)
		print(ident.gender_symbol)

	#--------------------------------------------------------
	def test_set_active_pat():

		ident = cPerson(1)
		print("setting active patient with", ident)
		print(ident.description)
		print(ident.last_contact)
		set_active_patient(patient=ident)
		input()

		patient = cPatient(12)
		print("setting active patient with", patient)
		print(patient.description)
		print(patient.last_contact)
		set_active_patient(patient=patient)
		input()

		pat = gmCurrentPatient()
		print(pat['dob'])
		print(pat.description)
		print(pat.last_contact)
		#pat['dob'] = 'test'

#		staff = cStaff()
#		print("setting active patient with", staff)
#		set_active_patient(patient=staff)

		input()
		print("setting active patient with -1")
		set_active_patient(patient=-1)

	#--------------------------------------------------------
	def test_dto_person():
		dto = cDTO_person()
		dto.firstnames = 'Sepp'
		dto.lastnames = 'Herberger'
		dto.gender = 'male'
		dto.dob = pyDT.datetime.now(tz=gmDateTime.gmCurrentLocalTimezone)
		print(dto)

		print(dto['firstnames'])
		print(dto['lastnames'])
		print(dto['gender'])
		print(dto['dob'])

		for key in dto.keys():
			print(key)
	#--------------------------------------------------------
	def test_identity():
		# create patient
		print('\n\nCreating identity...')
		new_identity = create_identity(gender='m', dob='2005-01-01', lastnames='test lastnames', firstnames='test firstnames')
		print('Identity created: %s' % new_identity)

		print('\nSetting title and gender...')
		new_identity['title'] = 'test title';
		new_identity['gender'] = 'f';
		new_identity.save_payload()
		print('Refetching identity from db: %s' % cPerson(aPK_obj=new_identity['pk_identity']))

		print('\nGetting all names...')
		for a_name in new_identity.get_names():
			print(a_name)
		print('Active name: %s' % (new_identity.get_active_name()))
		print('Setting nickname...')
		new_identity.set_nickname(nickname='test nickname')
		print('Refetching all names...')
		for a_name in new_identity.get_names():
			print(a_name)
		print('Active name: %s' % (new_identity.get_active_name()))

		print('\nIdentity occupations: %s' % new_identity['occupations'])
		print('Creating identity occupation...')
		new_identity.link_occupation('test occupation')
		print('Identity occupations: %s' % new_identity['occupations'])

		print('\nIdentity addresses: %s' % new_identity.get_addresses())
		print('Creating identity address...')
		# make sure the state exists in the backend
		new_identity.link_address (
			number = 'test 1234',
			street = 'test street',
			postcode = 'test postcode',
			urb = 'test urb',
			region_code = 'SN',
			country_code = 'DE'
		)
		print('Identity addresses: %s' % new_identity.get_addresses())

		print('\nIdentity communications: %s' % new_identity.get_comm_channels())
		print('Creating identity communication...')
		new_identity.link_comm_channel('homephone', '1234566')
		print('Identity communications: %s' % new_identity.get_comm_channels())
	#--------------------------------------------------------
	def test_name():
		for pk in range(1,16):
			name = cPersonName(aPK_obj=pk)
			print(name.description)
			print('  ', name)
	#--------------------------------------------------------
	def test_export_area():
		person = cPerson(aPK_obj = 12)
		print(person)
		print(person.export_area)
		print(person.export_area.items)
	#--------------------------------------------------------
	def test_ext_id():
		person = cPerson(aPK_obj = 9)
		print(person.get_external_ids(id_type='Fachgebiet', issuer='Ärztekammer'))
		#print(person.get_external_ids()
		person = cPerson(aPK_obj = 12)
		suggestions = person.suggest_external_ids(target = 'Orthanc')
		print(suggestions)
		print([ (sugg.rsplit('#', 2)[0]).strip('-') for sugg in suggestions ])

	#--------------------------------------------------------
	def test_vcf():
		person = cPerson(aPK_obj = 12)
		print(person.export_as_vcard())

	#--------------------------------------------------------
	def test_mecard():
		person = cPerson(aPK_obj = 12)
		print(person.MECARD)
		mcf = person.export_as_mecard()
		print(mcf)
		#print(gmTools.create_qrcode(filename = mcf, qr_filename = None, verbose = True)
		#print(gmTools.create_qrcode(text = person.MECARD, qr_filename = None, verbose = True))

	#--------------------------------------------------------
	def test_current_patient():
		pat = gmCurrentPatient()
		print(pat)
		input()
		pat = gmCurrentPatient(cPatient(12))
		print(pat.description)
		input()
		pat = gmCurrentPatient()
		print(pat.description)
		input()
		pat_extra = gmCurrentPatient()
		pat = gmCurrentPatient(cPatient(1))
		print('pat:', pat.description)
		print('pat extra:', pat_extra.description)

		#pat = gmCurrentPatient()
		#print("pat.emr", pat.emr)

	#--------------------------------------------------------
	def test_ext_id2():
		person = cPerson(aPK_obj = 12)
		print(person.suggest_external_id(target = 'Orthanc'))

	#--------------------------------------------------------
	def test_assimilate_identity():
		patient = cPatient(12)
		set_active_patient(patient = patient)
		curr_pat = gmCurrentPatient()
		#other_pat = cPerson(1111111)
		curr_pat.assimilate_identity(other_identity=None)

	#--------------------------------------------------------
	def test_get_person_duplicates():
		print(get_person_duplicates (
			lastnames = 'Kirk',
			firstnames = 'James Tiberius',
			dob = '1931-03-21',
			gender = 'm',
			comment = None
		))

	#--------------------------------------------------------
	def test_get_potential_person_dupes():
		print('w/o first name:')
		print(get_potential_person_dupes (
			lastnames = 'Kirk',
			#firstnames = 'James Tiberius',
			dob = '1931-03-21',
			active_only =True
		))
		print('w/ first name:')
		print(get_potential_person_dupes (
			lastnames = 'Kirk',
			firstnames = 'James Tiberius',
			dob = '1931-03-21',
			active_only =True
		))
		print('w/ first name:')
		print(get_potential_person_dupes (
			lastnames = 'Kirk',
			firstnames = ' Tiber',
			dob = '1931-03-21',
			active_only =True
		))

	#--------------------------------------------------------
	#test_dto_person()
	#test_identity()
	#test_search_by_dto()
	#test_name()

	# module functions

	#comms = get_comm_list()
	#print("\n\nRetrieving communication media enum (id, description): %s" % comms)
	#test_export_area()
	#test_ext_id()
	#test_vcf()

	gmPG2.request_login_params(setup_pool = True)
	#test_set_active_pat()
	#test_mecard()
	#test_ext_id()
	#test_current_patient()
	#test_assimilate_identity()
	#test_get_person_duplicates()
	#test_get_potential_person_dupes()
	test_description_gender()

#============================================================
