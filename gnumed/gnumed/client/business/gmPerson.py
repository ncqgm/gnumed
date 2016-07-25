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
import os.path
import time
import re as regex
import datetime as pyDT
import io
import thread
import threading
import logging
import io
import inspect
from xml.etree import ElementTree as etree


# GNUmed
if __name__ == '__main__':
	logging.basicConfig(level = logging.DEBUG)
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmExceptions
from Gnumed.pycommon import gmDispatcher
from Gnumed.pycommon import gmBorg
from Gnumed.pycommon import gmI18N
if __name__ == '__main__':
	gmI18N.activate_locale()
	gmI18N.install_domain()
from Gnumed.pycommon import gmNull
from Gnumed.pycommon import gmBusinessDBObject
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmPG2
from Gnumed.pycommon import gmDateTime
from Gnumed.pycommon import gmMatchProvider
from Gnumed.pycommon import gmLog2
from Gnumed.pycommon import gmHooks

from Gnumed.business import gmDemographicRecord
from Gnumed.business import gmClinicalRecord
from Gnumed.business import gmXdtMappings
from Gnumed.business import gmProviderInbox
from Gnumed.business import gmExportArea
from Gnumed.business import gmBilling
from Gnumed.business import gmAutoHints
from Gnumed.business.gmDocuments import cDocumentFolder
from Gnumed.business.gmChartPulling import tui_chart_puller


_log = logging.getLogger('gm.person')

__gender_list = None
__gender_idx = None

__gender2salutation_map = None
__gender2string_map = None

#============================================================
_MERGE_SCRIPT_HEADER = u"""-- GNUmed patient merge script
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
def external_id_exists(pk_issuer, value):
	cmd = u'SELECT COUNT(1) FROM dem.lnk_identity2ext_id WHERE fk_origin = %(issuer)s AND external_id = %(val)s'
	args = {'issuer': pk_issuer, 'val': value}
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = False)
	return rows[0][0]

#============================================================
def person_exists(lastnames, dob, firstnames=None, active_only=True):
	args = {
		'last': lastnames,
		'dob': dob
	}
	where_parts = [
		u"lastnames = %(last)s",
		u"dem.date_trunc_utc('day', dob) = dem.date_trunc_utc('day', %(dob)s)"
	]
	if firstnames is not None:
		if firstnames.strip() != u'':
			#where_parts.append(u"position(%(first)s in firstnames) = 1")
			where_parts.append(u"firstnames ~* %(first)s")
			args['first'] = u'\\m' + firstnames
	if active_only:
		cmd = u"""SELECT COUNT(1) FROM dem.v_active_persons WHERE %s""" % u' AND '.join(where_parts)
	else:
		cmd = u"""SELECT COUNT(1) FROM dem.v_all_persons WHERE %s""" % u' AND '.join(where_parts)
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = False)
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
	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def keys(self):
		return 'firstnames lastnames dob gender title'.split()
	#--------------------------------------------------------
	def delete_from_source(self):
		pass
	#--------------------------------------------------------
	def is_unique(self):
		where_snippets = [
			u'firstnames = %(first)s',
			u'lastnames = %(last)s'
		]
		args = {
			'first': self.firstnames,
			'last': self.lastnames
		}
		if self.dob is not None:
			where_snippets.append(u"dem.date_trunc_utc('day'::text, dob) = dem.date_trunc_utc('day'::text, %(dob)s)")
			args['dob'] = self.dob.replace(hour = 23, minute = 59, second = 59)
		if self.gender is not None:
			where_snippets.append('gender = %(sex)s')
			args['sex'] = self.gender
		cmd = u'SELECT count(1) FROM dem.v_person_names WHERE %s' % ' AND '.join(where_snippets)
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = False)

		return rows[0][0] == 1

	is_unique = property(is_unique, lambda x:x)
	#--------------------------------------------------------
	def exists(self):
		where_snippets = [
			u'firstnames = %(first)s',
			u'lastnames = %(last)s'
		]
		args = {
			'first': self.firstnames,
			'last': self.lastnames
		}
		if self.dob is not None:
			where_snippets.append(u"dem.date_trunc_utc('day'::text, dob) = dem.date_trunc_utc('day'::text, %(dob)s)")
			args['dob'] = self.dob.replace(hour = 23, minute = 59, second = 59)
		if self.gender is not None:
			where_snippets.append('gender = %(sex)s')
			args['sex'] = self.gender
		cmd = u'SELECT count(1) FROM dem.v_person_names WHERE %s' % ' AND '.join(where_snippets)
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = False)

		return rows[0][0] > 0

	exists = property(exists, lambda x:x)
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

		where_snippets.append(u'lower(firstnames) = lower(%(first)s)')
		args['first'] = self.firstnames

		where_snippets.append(u'lower(lastnames) = lower(%(last)s)')
		args['last'] = self.lastnames

		if self.dob is not None:
			where_snippets.append(u"dem.date_trunc_utc('day'::text, dob) = dem.date_trunc_utc('day'::text, %(dob)s)")
			args['dob'] = self.dob.replace(hour = 23, minute = 59, second = 59)

		if self.gender is not None:
			where_snippets.append(u'lower(gender) = lower(%(sex)s)')
			args['sex'] = self.gender

		# FIXME: allow disabled persons ?
		cmd = u"""
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
			rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx=True)
		except:
			_log.error(u'cannot get candidate identities for dto "%s"' % self)
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
			identities = [ cPerson(row = {'pk_field': 'pk_identity', 'data': row, 'idx': idx}) for row in rows ]

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

		if self.dob_is_estimated:
			self.identity['dob_is_estimated'] = True
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
		if value == u'':
			return
		name = name.strip()
		if name == u'':
			raise ValueError(_('<name> cannot be empty'))
		issuer = issuer.strip()
		if issuer == u'':
			raise ValueError(_('<issuer> cannot be empty'))
		self.external_ids.append({'name': name, 'value': value, 'issuer': issuer, 'comment': comment})
	#--------------------------------------------------------
	def remember_comm_channel(self, channel=None, url=None):
		url = url.strip()
		if url == u'':
			return
		channel = channel.strip()
		if channel == u'':
			raise ValueError(_('<channel> cannot be empty'))
		self.comm_channels.append({'channel': channel, 'url': url})
	#--------------------------------------------------------
	def remember_address(self, number=None, street=None, urb=None, region_code=None, zip=None, country_code=None, adr_type=None, subunit=None):
		number = number.strip()
		if number == u'':
			raise ValueError(_('<number> cannot be empty'))
		street = street.strip()
		if street == u'':
			raise ValueError(_('<street> cannot be empty'))
		urb = urb.strip()
		if urb == u'':
			raise ValueError(_('<urb> cannot be empty'))
		zip = zip.strip()
		if zip == u'':
			raise ValueError(_('<zip> cannot be empty'))
		country_code = country_code.strip()
		if country_code == u'':
			raise ValueError(_('<country_code> cannot be empty'))
		if region_code is not None:
			region_code = region_code.strip()
		if region_code in [None, u'']:
			region_code = u'??'
		self.addresses.append ({
			u'type': adr_type,
			u'number': number,
			u'subunit': subunit,
			u'street': street,
			u'zip': zip,
			u'urb': urb,
			u'region_code': region_code,
			u'country_code': country_code
		})
	#--------------------------------------------------------
	# customizing behaviour
	#--------------------------------------------------------
	def __str__(self):
		return u'<%s (%s) @ %s: %s %s (%s) %s>' % (
			self.__class__.__name__,
			self.source,
			id(self),
			self.firstnames,
			self.lastnames,
			self.gender,
			self.dob
		)
	#--------------------------------------------------------
	def __setattr__(self, attr, val):
		"""Do some sanity checks on self.* access."""

		if attr == 'gender':
			if val is None:
				object.__setattr__(self, attr, val)
				return
			glist, idx = get_gender_list()
			for gender in glist:
				if str(val) in [gender[0], gender[1], gender[2], gender[3]]:
					val = gender[idx['tag']]
					object.__setattr__(self, attr, val)
					return
			raise ValueError('invalid gender: [%s]' % val)

		if attr == 'dob':
			if val is not None:
				if not isinstance(val, pyDT.datetime):
					raise TypeError('invalid type for DOB (must be datetime.datetime): %s [%s]' % (type(val), val))
				if val.tzinfo is None:
					raise ValueError('datetime.datetime instance is lacking a time zone: [%s]' % val.isoformat())

		object.__setattr__(self, attr, val)
		return
	#--------------------------------------------------------
	def __getitem__(self, attr):
		return getattr(self, attr)

#============================================================
class cPersonName(gmBusinessDBObject.cBusinessDBObject):
	_cmd_fetch_payload = u"SELECT * FROM dem.v_person_names WHERE pk_name = %s"
	_cmds_store_payload = [
		u"""UPDATE dem.names SET
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
		u"""update dem.names set
			active = %(active_name)s,
			preferred = %(preferred)s,
			comment = %(comment)s
		where
			id = %(pk_name)s and
			id_identity = %(pk_identity)s and	-- belt and suspenders
			xmin = %(xmin_name)s""",
		u"""select xmin as xmin_name from dem.names where id = %(pk_name)s"""
	]
	_updatable_fields = ['active_name', 'preferred', 'comment']
	#--------------------------------------------------------
	def __setitem__(self, attribute, value):
		if attribute == 'active_name':
			# cannot *directly* deactivate a name, only indirectly
			# by activating another one
			# FIXME: should be done at DB level
			if self._payload[self._idx['active_name']] is True:
				return
		gmBusinessDBObject.cBusinessDBObject.__setitem__(self, attribute, value)
	#--------------------------------------------------------
	def _get_description(self):
		return '%(last)s, %(title)s %(first)s%(nick)s' % {
			'last': self._payload[self._idx['lastnames']],
			'title': gmTools.coalesce (
				self._payload[self._idx['title']],
				map_gender2salutation(self._payload[self._idx['gender']])
			),
			'first': self._payload[self._idx['firstnames']],
			'nick': gmTools.coalesce(self._payload[self._idx['preferred']], u'', u" '%s'", u'%s')
		}

	description = property(_get_description, lambda x:x)

#============================================================
_SQL_get_active_person = u"SELECT * FROM dem.v_active_persons WHERE pk_identity = %s"
_SQL_get_any_person = u"SELECT * FROM dem.v_all_persons WHERE pk_identity = %s"

class cPerson(gmBusinessDBObject.cBusinessDBObject):
	_cmd_fetch_payload = _SQL_get_any_person
	_cmds_store_payload = [
		u"""UPDATE dem.identity SET
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
		return self._payload[self._idx['pk_identity']]
	def _set_ID(self, value):
		raise AttributeError('setting ID of identity is not allowed')

	ID = property(_get_ID, _set_ID)

	#--------------------------------------------------------
	def __setitem__(self, attribute, value):

		if attribute == 'dob':
			if value is not None:

				if isinstance(value, pyDT.datetime):
					if value.tzinfo is None:
						raise ValueError('datetime.datetime instance is lacking a time zone: [%s]' % dt.isoformat())
				else:
					raise TypeError, '[%s]: type [%s] (%s) invalid for attribute [dob], must be datetime.datetime or None' % (self.__class__.__name__, type(value), value)

				# compare DOB at seconds level
				if self._payload[self._idx['dob']] is not None:
					old_dob = gmDateTime.pydt_strftime (
						self._payload[self._idx['dob']],
						format = '%Y %m %d %H %M %S',
						accuracy = gmDateTime.acc_seconds
					)
					new_dob = gmDateTime.pydt_strftime (
						value,
						format = '%Y %m %d %H %M %S',
						accuracy = gmDateTime.acc_seconds
					)
					if new_dob == old_dob:
						return

		gmBusinessDBObject.cBusinessDBObject.__setitem__(self, attribute, value)

	#--------------------------------------------------------
	def cleanup(self):
		pass

	#--------------------------------------------------------
	def _get_is_patient(self):
		return identity_is_patient(self._payload[self._idx['pk_identity']])

	def _set_is_patient(self, turn_into_patient):
		if turn_into_patient:
			return turn_identity_into_patient(self._payload[self._idx['pk_identity']])
		return False

	is_patient = property(_get_is_patient, _set_is_patient)

	#--------------------------------------------------------
	def _get_as_patient(self):
		return cPatient(self._payload[self._idx['pk_identity']])

	as_patient = property(_get_as_patient, lambda x:x)

	#--------------------------------------------------------
	def _get_staff_id(self):
		cmd = u"SELECT pk FROM dem.staff WHERE fk_identity = %(pk)s"
		args = {'pk': self._payload[self._idx['pk_identity']]}
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = False)
		if len(rows) == 0:
			return None
		return rows[0][0]

	staff_id = property(_get_staff_id, lambda x:x)

	#--------------------------------------------------------
	# identity API
	#--------------------------------------------------------
	def _get_gender_symbol(self):
		return map_gender2symbol[self._payload[self._idx[u'gender']]]

	gender_symbol = property(_get_gender_symbol, lambda x:x)
	#--------------------------------------------------------
	def _get_gender_string(self):
		return map_gender2string(gender = self._payload[self._idx['gender']])

	gender_string = property(_get_gender_string, lambda x:x)
	#--------------------------------------------------------
	def _get_gender_list(self):
		gender_list, tmp = get_gender_list()
		return gender_list

	gender_list = property(_get_gender_list, lambda x:x)
	#--------------------------------------------------------
	def get_active_name(self):
		names = self.get_names(active_only = True)
		if len(names) == 0:
			_log.error('cannot retrieve active name for patient [%s]', self._payload[self._idx['pk_identity']])
			return None
		return names[0]

	active_name = property(get_active_name, lambda x:x)
	#--------------------------------------------------------
	def get_names(self, active_only=False, exclude_active=False):

		args = {'pk_pat': self._payload[self._idx['pk_identity']]}
		where_parts = [u'pk_identity = %(pk_pat)s']
		if active_only:
			where_parts.append(u'active_name is True')
		if exclude_active:
			where_parts.append(u'active_name is False')
		cmd = u"""
			SELECT *
			FROM dem.v_person_names
			WHERE %s
			ORDER BY active_name DESC, lastnames, firstnames
		""" % u' AND '.join(where_parts)
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)

		if len(rows) == 0:
			# no names registered for patient
			return []

		names = [ cPersonName(row = {'idx': idx, 'data': r, 'pk_field': 'pk_name'}) for r in rows ]
		return names
	#--------------------------------------------------------
	def get_description_gender(self, with_nickname=True):
		if with_nickname:
			template = _(u'%(last)s,%(title)s %(first)s%(nick)s (%(sex)s)')
		else:
			template = _(u'%(last)s,%(title)s %(first)s (%(sex)s)')
		return template % {
			'last': self._payload[self._idx['lastnames']],
			'title': gmTools.coalesce(self._payload[self._idx['title']], u'', u' %s'),
			'first': self._payload[self._idx['firstnames']],
			'nick': gmTools.coalesce(self._payload[self._idx['preferred']], u'', u" '%s'"),
			'sex': self.gender_symbol
		}

	#--------------------------------------------------------
	def get_description(self, with_nickname=True):
		if with_nickname:
			template = _(u'%(last)s,%(title)s %(first)s%(nick)s')
		else:
			template = _(u'%(last)s,%(title)s %(first)s')
		return template % {
			'last': self._payload[self._idx['lastnames']],
			'title': gmTools.coalesce(self._payload[self._idx['title']], u'', u' %s'),
			'first': self._payload[self._idx['firstnames']],
			'nick': gmTools.coalesce(self._payload[self._idx['preferred']], u'', u" '%s'")
		}

	#--------------------------------------------------------
	def add_name(self, firstnames, lastnames, active=True):
		"""Add a name.

		@param firstnames The first names.
		@param lastnames The last names.
		@param active When True, the new name will become the active one (hence setting other names to inactive)
		@type active A types.BooleanType instance
		"""
		name = create_name(self.ID, firstnames, lastnames, active)
		if active:
			self.refetch_payload()
		return name

	#--------------------------------------------------------
	def delete_name(self, name=None):
		cmd = u"delete from dem.names where id = %(name)s and id_identity = %(pat)s"
		args = {'name': name['pk_name'], 'pat': self.ID}
		gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])
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
		if self._payload[self._idx['preferred']] == nickname:
			return True
		rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': u"SELECT dem.set_nickname(%s, %s)", 'args': [self.ID, nickname]}])
		# setting nickname doesn't change dem.identity, so other fields
		# of dem.v_active_persons do not get changed as a consequence of
		# setting the nickname, hence locally setting nickname matches
		# in-database reality
		self._payload[self._idx['preferred']] = nickname
		#self.refetch_payload()
		return True

	#--------------------------------------------------------
	def get_tags(self, order_by=None):
		if order_by is None:
			order_by = u''
		else:
			order_by = u'ORDER BY %s' % order_by

		cmd = gmDemographicRecord._SQL_get_person_tags % (u'pk_identity = %%(pat)s %s' % order_by)
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': {u'pat': self.ID}}], get_col_idx = True)

		return [ gmDemographicRecord.cPersonTag(row = {'data': r, 'idx': idx, 'pk_field': 'pk_identity_tag'}) for r in rows ]

	tags = property(get_tags, lambda x:x)

	#--------------------------------------------------------
	def add_tag(self, tag):
		args = {
			u'tag': tag,
			u'identity': self.ID
		}

		# already exists ?
		cmd = u"SELECT pk FROM dem.identity_tag WHERE fk_tag = %(tag)s AND fk_identity = %(identity)s"
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = False)
		if len(rows) > 0:
			return gmDemographicRecord.cPersonTag(aPK_obj = rows[0]['pk'])

		# no, add
		cmd = u"""
			INSERT INTO dem.identity_tag (
				fk_tag,
				fk_identity
			) VALUES (
				%(tag)s,
				%(identity)s
			)
			RETURNING pk
		"""
		rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}], return_data = True, get_col_idx = False)
		return gmDemographicRecord.cPersonTag(aPK_obj = rows[0]['pk'])

	#--------------------------------------------------------
	def remove_tag(self, tag):
		cmd = u"DELETE FROM dem.identity_tag WHERE pk = %(pk)s"
		gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': {'pk': tag}}])

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
			cmd = u"""
				select * from dem.v_external_ids4identity where
				pk_identity = %(pat)s and
				pk_type = %(pk_type)s and
				value = %(val)s"""
		else:
			# by type/value/issuer
			if issuer is None:
				cmd = u"""
					select * from dem.v_external_ids4identity where
					pk_identity = %(pat)s and
					name = %(name)s and
					value = %(val)s"""
			else:
				cmd = u"""
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
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}])

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
				cmd = u"""insert into dem.lnk_identity2ext_id (external_id, fk_origin, comment, id_identity) values (
					%(val)s,
					(select dem.add_external_id_type(%(type_name)s, %(issuer)s)),
					%(comment)s,
					%(pat)s
				)"""
			else:
				cmd = u"""insert into dem.lnk_identity2ext_id (external_id, fk_origin, comment, id_identity) values (
					%(val)s,
					%(pk_type)s,
					%(comment)s,
					%(pat)s
				)"""

			rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])

		# or update comment of existing ID
		else:
			row = rows[0]
			if comment is not None:
				# comment not already there ?
				if gmTools.coalesce(row['comment'], '').find(comment.strip()) == -1:
					comment = '%s%s' % (gmTools.coalesce(row['comment'], '', '%s // '), comment.strip)
					cmd = u"update dem.lnk_identity2ext_id set comment = %(comment)s where id=%(pk)s"
					args = {'comment': comment, 'pk': row['pk_id']}
					rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])

	#--------------------------------------------------------
	def update_external_id(self, pk_id=None, type=None, value=None, issuer=None, comment=None):
		"""Edits an existing external ID.

		Creates ID type if necessary.
		"""
		cmd = u"""
			UPDATE dem.lnk_identity2ext_id SET
				fk_origin = (SELECT dem.add_external_id_type(%(type)s, %(issuer)s)),
				external_id = %(value)s,
				comment = gm.nullify_empty_string(%(comment)s)
			WHERE
				id = %(pk)s
		"""
		args = {'pk': pk_id, 'value': value, 'type': type, 'issuer': issuer, 'comment': comment}
		rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])

	#--------------------------------------------------------
	def get_external_ids(self, id_type=None, issuer=None):
		where_parts = ['pk_identity = %(pat)s']
		args = {'pat': self.ID}

		if id_type is not None:
			where_parts.append(u'name = %(name)s')
			args['name'] = id_type.strip()

		if issuer is not None:
			where_parts.append(u'issuer = %(issuer)s')
			args['issuer'] = issuer.strip()

		cmd = u"SELECT * FROM dem.v_external_ids4identity WHERE %s" % ' AND '.join(where_parts)
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}])

		return rows

	external_ids = property(get_external_ids, lambda x:x)

	#--------------------------------------------------------
	def delete_external_id(self, pk_ext_id=None):
		cmd = u"""
			DELETE FROM dem.lnk_identity2ext_id
			WHERE id_identity = %(pat)s AND id = %(pk)s"""
		args = {'pat': self.ID, 'pk': pk_ext_id}
		gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])

	#--------------------------------------------------------
	def suggest_external_id(self, target=None, encoding=None):
		name = self.active_name
		last = u' '.join(p for p in name['lastnames'].split(u"-"))
		last = u' '.join(p for p in last.split(u"."))
		last = u' '.join(p for p in last.split(u"'"))
		last = u''.join(gmTools.capitalize(text = p, mode = gmTools.CAPS_FIRST_ONLY) for p in last.split(u' '))
		first = u' '.join(p for p in name['firstnames'].split(u"-"))
		first = u' '.join(p for p in first.split(u"."))
		first = u' '.join(p for p in first.split(u"'"))
		first = u''.join(gmTools.capitalize(text = p, mode = gmTools.CAPS_FIRST_ONLY) for p in first.split(u' '))
		suggestion = u'GMd-%s%s%s%s%s' % (
			gmTools.coalesce(target, u'', u'%s-'),
			last,
			first,
			self.get_formatted_dob(format = '-%Y%m%d', none_string = u''),
			gmTools.coalesce(self['gender'], u'', u'-%s')
		)
		try:
			import unidecode
			return unidecode.unidecode(suggestion)
		except ImportError:
			_log.debug('cannot transliterate external ID suggestion, <unidecode> module not installed')
		if encoding is None:
			return suggestion
		return suggestion.encode(encoding)

	external_id_suggestion = property(suggest_external_id, lambda x:x)

	#--------------------------------------------------------
	def suggest_external_ids(self, target=None, encoding=None):
		names2use = [self.active_name]
		names2use.extend(self.get_names(active_only = False, exclude_active = True))
		target = gmTools.coalesce(target, u'', u'%s-')
		dob = self.get_formatted_dob(format = '-%Y%m%d', none_string = u'')
		gender = gmTools.coalesce(self['gender'], u'', u'-%s')
		suggestions = []
		for name in names2use:
			last = u' '.join(p for p in name['lastnames'].split(u"-"))
			last = u' '.join(p for p in last.split(u"."))
			last = u' '.join(p for p in last.split(u"'"))
			last = u''.join(gmTools.capitalize(text = p, mode = gmTools.CAPS_FIRST_ONLY) for p in last.split(u' '))
			first = u' '.join(p for p in name['firstnames'].split(u"-"))
			first = u' '.join(p for p in first.split(u"."))
			first = u' '.join(p for p in first.split(u"'"))
			first = u''.join(gmTools.capitalize(text = p, mode = gmTools.CAPS_FIRST_ONLY) for p in first.split(u' '))
			suggestion = u'GMd-%s%s%s%s%s' % (target, last, first, dob, gender)
			try:
				import unidecode
				suggestions.append(unidecode.unidecode(suggestion))
				continue
			except ImportError:
				_log.debug('cannot transliterate external ID suggestion, <unidecode> module not installed')
			if encoding is None:
				suggestions.append(suggestion)
			else:
				suggestions.append(suggestion.encode(encoding))
		return suggestions

	#--------------------------------------------------------
	#--------------------------------------------------------
	def assimilate_identity(self, other_identity=None, link_obj=None):
		"""Merge another identity into this one.

		Keep this one. Delete other one."""

		if other_identity.ID == self.ID:
			return True, None

		curr_pat = gmCurrentPatient()
		if curr_pat.connected:
			if other_identity.ID == curr_pat.ID:
				return False, _('Cannot merge active patient into another patient.')

		queries = []
		args = {'pat2del': other_identity.ID, 'pat2keep': self.ID}

		# merge allergy state
		queries.append ({
			'cmd': u"""
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
			'cmd': u'delete from clin.allergy_state where pk = (select pk_allergy_state from clin.v_pat_allergy_state where pk_patient = %(pat2del)s)',
			'args': args
		})

		# merge patient proxy
		queries.append ({
			'cmd': u"""
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
		# 1) disambiguate names in old pat
		queries.append ({
			'cmd': u"""
				UPDATE dem.names d_n1 SET
					lastnames = lastnames || ' (%s %s)'
				WHERE
					d_n1.id_identity = %%(pat2del)s
						AND
					EXISTS (
						SELECT 1 FROM dem.names d_n2
						WHERE
							d_n2.id_identity = %%(pat2keep)s
								AND
							d_n2.lastnames = d_n1.lastnames
								AND
							d_n2.firstnames = d_n1.firstnames
					)""" % (_('assimilated'), gmDateTime.pydt_strftime(gmDateTime.pydt_now_here())),
			'args': args
		})
		# 2) move inactive ones (but beware of dupes)
		queries.append ({
			'cmd': u"""
				UPDATE dem.names SET
					id_identity = %(pat2keep)s
				WHERE id_identity = %(pat2del)s AND active IS false""",
			'args': args
		})
		# 3) copy active ones
		queries.append ({
			'cmd': u"""
				INSERT INTO dem.names (
					id_identity, active, lastnames, firstnames, preferred, comment
				)
					SELECT
						%(pat2keep)s, false, lastnames, firstnames, preferred, comment
					FROM dem.names d_n
					WHERE d_n.id_identity = %(pat2del)s AND d_n.active IS true""",
			'args': args
		})

		# disambiguate potential dupes
		# - same-url comm channels
		queries.append ({
			'cmd': u"""
				UPDATE dem.lnk_identity2comm
				SET url = url || ' (%s %s)'
				WHERE
					fk_identity = %%(pat2del)s
						AND
					EXISTS (
						SELECT 1 FROM dem.lnk_identity2comm d_li2c
						WHERE d_li2c.fk_identity = %%(pat2keep)s AND d_li2c.url = url
					)
				""" % (_('merged'),	gmDateTime.pydt_strftime(gmDateTime.pydt_now_here())),
			'args': args
		})
		# - same-value external IDs
		queries.append ({
			'cmd': u"""
				UPDATE dem.lnk_identity2ext_id
				SET external_id = external_id || ' (%s %s)'
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
				""" % (_('merged'),	gmDateTime.pydt_strftime(gmDateTime.pydt_now_here())),
			'args': args
		})
		# - same addresses
		queries.append ({
			'cmd': u"""
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
			schema = u'dem',
			table = u'identity',
			column = u'pk'
		)
		# find FKs pointing to clin.patient.fk_identity
		FKs.extend (gmPG2.get_foreign_keys2column (
			schema = u'clin',
			table = u'patient',
			column = u'fk_identity'
		))

		# generate UPDATEs
		cmd_template = u'UPDATE %s SET %s = %%(pat2keep)s WHERE %s = %%(pat2del)s'
		for FK in FKs:
			if FK['referencing_table'] in [u'dem.names', u'clin.patient']:
				continue
			queries.append ({
				'cmd': cmd_template % (FK['referencing_table'], FK['referencing_column'], FK['referencing_column']),
				'args': args
			})

		# delete old patient proxy
		queries.append ({
			'cmd': u'DELETE FROM clin.patient WHERE fk_identity = %(pat2del)s',
			'args': args
		})

		# remove old identity entry
		queries.append ({
			'cmd': u'delete from dem.identity where pk = %(pat2del)s',
			'args': args
		})

		script_name = gmTools.get_unique_filename(prefix = u'gm-assimilate-%(pat2del)s-into-%(pat2keep)s-' % args, suffix = u'.sql')
		_log.warning('identity [%s] is about to assimilate identity [%s], SQL script [%s]', self.ID, other_identity.ID, script_name)

		script = io.open(script_name, 'wt')
		args['date'] = gmDateTime.pydt_strftime(gmDateTime.pydt_now_here(), '%Y %B %d  %H:%M')
		script.write(_MERGE_SCRIPT_HEADER % args)
		for query in queries:
			script.write((query['cmd'].lstrip()) % args)
			script.write(u';\n')
		script.write(u'\nROLLBACK;\n')
		script.write(u'--COMMIT;\n')
		script.close()

		gmPG2.run_rw_queries(link_obj = link_obj, queries = queries, end_tx = True)

		self.add_external_id (
			type_name = u'merged GNUmed identity primary key',
			value = u'GNUmed::pk::%s' % other_identity.ID,
			issuer = u'GNUmed'
		)

		return True, None

	#--------------------------------------------------------
	#--------------------------------------------------------
	def put_on_waiting_list(self, urgency=0, comment=None, zone=None):
		cmd = u"""
			insert into clin.waiting_list (fk_patient, urgency, comment, area, list_position)
			values (
				%(pat)s,
				%(urg)s,
				%(cmt)s,
				%(area)s,
				(select coalesce((max(list_position) + 1), 1) from clin.waiting_list)
			)"""
		args = {'pat': self.ID, 'urg': urgency, 'cmt': comment, 'area': zone}
		gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}], verbose = True)
	#--------------------------------------------------------
	def get_waiting_list_entry(self):
		cmd = u"""SELECT * FROM clin.v_waiting_list WHERE pk_identity = %(pat)s"""
		args = {'pat': self.ID}
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}])
		return rows

	waiting_list_entries = property(get_waiting_list_entry, lambda x:x)
	#--------------------------------------------------------
	def _get_export_area(self):
		return gmExportArea.cExportArea(self.ID)

	export_area = property(_get_export_area, lambda x:x)
	#--------------------------------------------------------
	def export_as_gdt(self, filename=None, encoding='iso-8859-15', external_id_type=None):

		template = u'%s%s%s\r\n'

		if filename is None:
			filename = gmTools.get_unique_filename (
				prefix = u'gm-patient-',
				suffix = u'.gdt'
			)

		gdt_file = io.open(filename, mode = 'wt', encoding = encoding, errors = 'strict')

		gdt_file.write(template % (u'013', u'8000', u'6301'))
		gdt_file.write(template % (u'013', u'9218', u'2.10'))
		if external_id_type is None:
			gdt_file.write(template % (u'%03d' % (9 + len(str(self.ID))), u'3000', self.ID))
		else:
			ext_ids = self.get_external_ids(id_type = external_id_type)
			if len(ext_ids) > 0:
				gdt_file.write(template % (u'%03d' % (9 + len(ext_ids[0]['value'])), u'3000', ext_ids[0]['value']))
		gdt_file.write(template % (u'%03d' % (9 + len(self._payload[self._idx['lastnames']])), u'3101', self._payload[self._idx['lastnames']]))
		gdt_file.write(template % (u'%03d' % (9 + len(self._payload[self._idx['firstnames']])), u'3102', self._payload[self._idx['firstnames']]))
		gdt_file.write(template % (u'%03d' % (9 + len(self._payload[self._idx['dob']].strftime('%d%m%Y'))), u'3103', self._payload[self._idx['dob']].strftime('%d%m%Y')))
		gdt_file.write(template % (u'010', u'3110', gmXdtMappings.map_gender_gm2xdt[self._payload[self._idx['gender']]]))
		gdt_file.write(template % (u'025', u'6330', 'GNUmed::9206::encoding'))
		gdt_file.write(template % (u'%03d' % (9 + len(encoding)), u'6331', encoding))
		if external_id_type is None:
			gdt_file.write(template % (u'029', u'6332', u'GNUmed::3000::source'))
			gdt_file.write(template % (u'017', u'6333', u'internal'))
		else:
			if len(ext_ids) > 0:
				gdt_file.write(template % (u'029', u'6332', u'GNUmed::3000::source'))
				gdt_file.write(template % (u'%03d' % (9 + len(external_id_type)), u'6333', external_id_type))

		gdt_file.close()

		return filename
	#--------------------------------------------------------
	def export_as_xml_linuxmednews(self, filename=None):

		if filename is None:
			filename = gmTools.get_unique_filename (
				prefix = u'gm-LinuxMedNews_demographics-',
				suffix = u'.xml'
			)

		dob_format = '%Y-%m-%d'
		pat = etree.Element(u'patient')

		first = etree.SubElement(pat, u'firstname')
		first.text = gmTools.coalesce(self._payload[self._idx['firstnames']], u'')

		last = etree.SubElement(pat, u'lastname')
		last.text = gmTools.coalesce(self._payload[self._idx['lastnames']], u'')

		# privacy
		#middle = etree.SubElement(pat, u'middlename')
		#middle.set(u'comment', _('preferred name/call name/...'))
		#middle.text = gmTools.coalesce(self._payload[self._idx['preferred']], u'')

		pref = etree.SubElement(pat, u'name_prefix')
		pref.text = gmTools.coalesce(self._payload[self._idx['title']], u'')

		suff = etree.SubElement(pat, u'name_suffix')
		suff.text = u''

		dob = etree.SubElement(pat, u'DOB')
		dob.set(u'format', dob_format)
		dob.text = gmDateTime.pydt_strftime(self._payload[self._idx['dob']], dob_format, encoding = 'utf8', accuracy = gmDateTime.acc_days, none_str = u'')

		gender = etree.SubElement(pat, u'gender')
		gender.set(u'comment', self.gender_string)
		if self._payload[self._idx['gender']] is None:
			gender.text = u''
		else:
			gender.text = map_gender2mf[self._payload[self._idx['gender']]]

		home = etree.SubElement(pat, u'home_address')
		adrs = self.get_addresses(address_type = u'home')
		if len(adrs) > 0:
			adr = adrs[0]
			city = etree.SubElement(home, u'city')
			city.set(u'comment', gmTools.coalesce(adr['suburb'], u''))
			city.text = gmTools.coalesce(adr['urb'], u'')

			region = etree.SubElement(home, u'region')
			region.set(u'comment', gmTools.coalesce(adr['l10n_region'], u''))
			region.text = gmTools.coalesce(adr['code_region'], u'')

			zipcode = etree.SubElement(home, u'postal_code')
			zipcode.text = gmTools.coalesce(adr['postcode'], u'')

			street = etree.SubElement(home, u'street')
			street.set(u'comment', gmTools.coalesce(adr['notes_street'], u''))
			street.text = gmTools.coalesce(adr['street'], u'')

			no = etree.SubElement(home, u'number')
			no.set(u'subunit', gmTools.coalesce(adr['subunit'], u''))
			no.set(u'comment', gmTools.coalesce(adr['notes_subunit'], u''))
			no.text = gmTools.coalesce(adr['number'], u'')

			country = etree.SubElement(home, u'country')
			country.set(u'comment', adr['l10n_country'])
			country.text = gmTools.coalesce(adr['code_country'], u'')

		phone = etree.SubElement(pat, u'home_phone')
		rec = self.get_comm_channels(comm_medium = u'homephone')
		if len(rec) > 0:
			if not rec[0]['is_confidential']:
				phone.set(u'comment', gmTools.coalesce(rec[0]['comment'], u''))
				phone.text = rec[0]['url']

		phone = etree.SubElement(pat, u'work_phone')
		rec = self.get_comm_channels(comm_medium = u'workphone')
		if len(rec) > 0:
			if not rec[0]['is_confidential']:
				phone.set(u'comment', gmTools.coalesce(rec[0]['comment'], u''))
				phone.text = rec[0]['url']

		phone = etree.SubElement(pat, u'cell_phone')
		rec = self.get_comm_channels(comm_medium = u'mobile')
		if len(rec) > 0:
			if not rec[0]['is_confidential']:
				phone.set(u'comment', gmTools.coalesce(rec[0]['comment'], u''))
				phone.text = rec[0]['url']

		tree = etree.ElementTree(pat)
		tree.write(filename, encoding = u'UTF-8')

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
		vc.add(u'kind')
		vc.kind.value = u'individual'

		vc.add(u'fn')
		vc.fn.value = self.get_description()
		vc.add(u'n')
		vc.n.value = vobject.vcard.Name(family = self._payload[self._idx['lastnames']], given = self._payload[self._idx['firstnames']])
		# privacy
		#vc.add(u'nickname')
		#vc.nickname.value = gmTools.coalesce(self._payload[self._idx['preferred']], u'')
		vc.add(u'title')
		vc.title.value = gmTools.coalesce(self._payload[self._idx['title']], u'')
		vc.add(u'gender')
		# FIXME: dont know how to add gender_string after ';'
		vc.gender.value = map_gender2vcard[self._payload[self._idx['gender']]]#, self.gender_string
		vc.add(u'bday')
		vc.bday.value = gmDateTime.pydt_strftime(self._payload[self._idx['dob']], dob_format, encoding = 'utf8', accuracy = gmDateTime.acc_days, none_str = u'')

		channels = self.get_comm_channels(comm_medium = u'homephone')
		if len(channels) > 0:
			if not channels[0]['is_confidential']:
				vc.add(u'tel')
				vc.tel.value = channels[0]['url']
				vc.tel.type_param = u'HOME'
		channels = self.get_comm_channels(comm_medium = u'workphone')
		if len(channels) > 0:
			if not channels[0]['is_confidential']:
				vc.add(u'tel')
				vc.tel.value = channels[0]['url']
				vc.tel.type_param = u'WORK'
		channels = self.get_comm_channels(comm_medium = u'mobile')
		if len(channels) > 0:
			if not channels[0]['is_confidential']:
				vc.add(u'tel')
				vc.tel.value = channels[0]['url']
				vc.tel.type_param = u'CELL'
		channels = self.get_comm_channels(comm_medium = u'fax')
		if len(channels) > 0:
			if not channels[0]['is_confidential']:
				vc.add(u'tel')
				vc.tel.value = channels[0]['url']
				vc.tel.type_param = u'FAX'
		channels = self.get_comm_channels(comm_medium = u'email')
		if len(channels) > 0:
			if not channels[0]['is_confidential']:
				vc.add(u'email')
				vc.tel.value = channels[0]['url']
				vc.tel.type_param = u'INTERNET'
		channels = self.get_comm_channels(comm_medium = u'web')
		if len(channels) > 0:
			if not channels[0]['is_confidential']:
				vc.add(u'url')
				vc.tel.value = channels[0]['url']
				vc.tel.type_param = u'INTERNET'

		adrs = self.get_addresses(address_type = u'home')
		if len(adrs) > 0:
			home_adr = adrs[0]
			vc.add(u'adr')
			vc.adr.type_param = u'HOME'
			vc.adr.value = vobject.vcard.Address()
			vc_adr = vc.adr.value
			vc_adr.extended = gmTools.coalesce(home_adr['subunit'], u'')
			vc_adr.street = gmTools.coalesce(home_adr['street'], u'', u'%s ') + gmTools.coalesce(home_adr['number'], u'')
			vc_adr.region = gmTools.coalesce(home_adr['l10n_region'], u'')
			vc_adr.code = gmTools.coalesce(home_adr['postcode'], u'')
			vc_adr.city = gmTools.coalesce(home_adr['urb'], u'')
			vc_adr.country = gmTools.coalesce(home_adr['l10n_country'], u'')

		#photo (base64)

		if filename is None:
			filename = gmTools.get_unique_filename (
				prefix = u'gm-patient-',
				suffix = u'.vcf'
			)
		vcf = io.open(filename, mode = 'wt', encoding = 'utf8')
		vcf.write(vc.serialize().decode('utf-8'))
		vcf.close()

		return filename
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

		cmd = u"select activities from dem.v_person_jobs where pk_identity = %(pat_id)s and l10n_occupation = _(%(job)s)"
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}])

		queries = []
		if len(rows) == 0:
			queries.append ({
				'cmd': u"INSERT INTO dem.lnk_job2person (fk_identity, fk_occupation, activities) VALUES (%(pat_id)s, dem.create_occupation(%(job)s), %(act)s)",
				'args': args
			})
		else:
			if rows[0]['activities'] != activities:
				queries.append ({
					'cmd': u"update dem.lnk_job2person set activities=%(act)s where fk_identity=%(pat_id)s and fk_occupation=(select id from dem.occupation where _(name) = _(%(job)s))",
					'args': args
				})

		rows, idx = gmPG2.run_rw_queries(queries = queries)

		return True
	#--------------------------------------------------------
	def unlink_occupation(self, occupation=None):
		if occupation is None:
			return True
		occupation = occupation.strip()
		cmd = u"delete from dem.lnk_job2person where fk_identity=%(pk)s and fk_occupation in (select id from dem.occupation where _(name) = _(%(job)s))"
		rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': {'pk': self.pk_obj, 'job': occupation}}])
		return True
	#--------------------------------------------------------
	# comms API
	#--------------------------------------------------------
	def get_comm_channels(self, comm_medium=None):
		cmd = u"select * from dem.v_person_comms where pk_identity = %s"
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': [self.pk_obj]}], get_col_idx = True)

		filtered = rows

		if comm_medium is not None:
			filtered = []
			for row in rows:
				if row['comm_type'] == comm_medium:
					filtered.append(row)

		return [ gmDemographicRecord.cCommChannel(row = {
					'pk_field': 'pk_lnk_identity2comm',
					'data': r,
					'idx': idx
				}) for r in filtered
			]

	comm_channels = property(get_comm_channels, lambda x:x)
	#--------------------------------------------------------
	def link_comm_channel(self, comm_medium=None, url=None, is_confidential=False, pk_channel_type=None):
		"""Link a communication medium with a patient.

		@param comm_medium The name of the communication medium.
		@param url The communication resource locator.
		@type url A types.StringType instance.
		@param is_confidential Wether the data must be treated as confidential.
		@type is_confidential A types.BooleanType instance.
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

		cmd = u"SELECT * FROM dem.v_pat_addresses WHERE pk_identity = %(pat)s"
		args = {'pat': self.pk_obj}
		if address_type is not None:
			cmd = cmd + u" AND address_type = %(typ)s"
			args['typ'] = address_type

		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)

		return [
			gmDemographicRecord.cPatientAddress(row = {'idx': idx, 'data': r, 'pk_field': 'pk_address'})
			for r in rows
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
		cmd = u"SELECT id_address FROM dem.lnk_person_org_address WHERE id_identity = %(pat)s AND id_address = %(adr)s"
		args = {'pat': self.pk_obj, 'adr': address['pk_address']}
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}])

		# no, link to person
		if len(rows) == 0:
			args = {'id': self.pk_obj, 'adr': address['pk_address'], 'type': id_type}
			cmd = u"""
				INSERT INTO dem.lnk_person_org_address(id_identity, id_address)
				VALUES (%(id)s, %(adr)s)
				RETURNING id_address"""
			rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}], return_data = True)

		linked_adr = gmDemographicRecord.cPatientAddress(aPK_obj = rows[0]['id_address'])

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
		cmd = u"""
			DELETE FROM dem.lnk_person_org_address
			WHERE
				dem.lnk_person_org_address.id_identity = %(person)s
					AND
				dem.lnk_person_org_address.id_address = %(adr)s
					AND
				NOT EXISTS(SELECT 1 FROM bill.bill WHERE fk_receiver_address = dem.lnk_person_org_address.id)
			"""
		gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])
	#----------------------------------------------------------------------
	# bills API
	#----------------------------------------------------------------------
	def get_bills(self, order_by=None, pk_patient=None):
		return gmBilling.get_bills (
			order_by = order_by,
			pk_patient = self.pk_obj
		)

	bills = property(get_bills, lambda x:x)
	#----------------------------------------------------------------------
	# relatives API
	#----------------------------------------------------------------------
	def get_relatives(self):
		cmd = u"""
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
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': {'pk': self.pk_obj}}])
		if len(rows) == 0:
			return []
		return [(row[0], cPerson(row = {'data': row[1:], 'idx':idx, 'pk_field': 'pk_identity'})) for row in rows]
	#--------------------------------------------------------
	def link_new_relative(self, rel_type = 'parent'):
		# create new relative
		id_new_relative = create_dummy_identity()

		relative = cPerson(aPK_obj=id_new_relative)
		# pre-fill with data from ourselves
#		relative.copy_addresses(self)
		relative.add_name( '**?**', self.get_names()['lastnames'])
		# and link the two
		if u'relatives' in self._ext_cache:
			del self._ext_cache['relatives']
		cmd = u"""
			insert into dem.lnk_person2relative (
				id_identity, id_relative, id_relation_type
			) values (
				%s, %s, (select id from dem.relation_types where description = %s)
			)"""
		rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': [self.ID, id_new_relative, rel_type  ]}])
		return True
	#----------------------------------------------------------------------
	def delete_relative(self, relation):
		# unlink only, don't delete relative itself
		self.set_relative(None, relation)
	#--------------------------------------------------------
	def _get_emergency_contact_from_database(self):
		if self._payload[self._idx['pk_emergency_contact']] is None:
			return None
		return cPerson(self._payload[self._idx['pk_emergency_contact']])

	emergency_contact_in_database = property(_get_emergency_contact_from_database, lambda x:x)
	#----------------------------------------------------------------------
	# age/dob related
	#----------------------------------------------------------------------
	def get_formatted_dob(self, format='%Y %b %d', encoding=None, none_string=None):
		return gmDateTime.format_dob (
			self._payload[self._idx['dob']],
			format = format,
			encoding = encoding,
			none_string = none_string,
			dob_is_estimated = self._payload[self._idx['dob_is_estimated']]
		)
	#----------------------------------------------------------------------
	def get_medical_age(self):
		dob = self['dob']

		if dob is None:
			return u'??'

		if dob > gmDateTime.pydt_now_here():
			return _('invalid age: DOB in the future')

		death = self['deceased']

		if death is None:
			return u'%s%s' % (
				gmTools.bool2subst (
					self._payload[self._idx['dob_is_estimated']],
					gmTools.u_almost_equal_to,
					u''
				),
				gmDateTime.format_apparent_age_medically (
					age = gmDateTime.calculate_apparent_age(start = dob)
				)
			)

		if dob > death:
			return _('invalid age: DOB after death')

		return u'%s%s%s' % (
			gmTools.u_latin_cross,
			gmTools.bool2subst (
				self._payload[self._idx['dob_is_estimated']],
				gmTools.u_almost_equal_to,
				u''
			),
			gmDateTime.format_apparent_age_medically (
				age = gmDateTime.calculate_apparent_age (
					start = dob,
					end = self['deceased']
				)
			)
		)
	#----------------------------------------------------------------------
	def dob_in_range(self, min_distance=u'1 week', max_distance=u'1 week'):
		if self['dob'] is None:
			return False
		cmd = u'select dem.dob_is_in_range(%(dob)s, %(min)s, %(max)s)'
		rows, idx = gmPG2.run_ro_queries (
			queries = [{
				'cmd': cmd,
				'args': {'dob': self['dob'], 'min': min_distance, 'max': max_distance}
			}]
		)
		return rows[0][0]
	#----------------------------------------------------------------------
	def current_birthday_passed(self):
		if self['dob'] is None:
			return None
		now = gmDateTime.pydt_now_here()
		if now.month < self['dob'].month:
			return False
		if now.month > self['dob'].month:
			return True
		# DOB is this month
		if now.day < self['dob'].day:
			return False
		if now.day > self['dob'].day:
			return True
		return None
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

	birthday_this_year = property(_get_birthday_this_year, lambda x:x)
	#----------------------------------------------------------------------
	# practice related
	#----------------------------------------------------------------------
	def get_last_encounter(self):
		cmd = u'select * from clin.v_most_recent_encounters where pk_patient=%s'
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': [self._payload[self._idx['pk_identity']]]}])
		if len(rows) > 0:
			return rows[0]
		else:
			return None
	#--------------------------------------------------------
	def get_messages(self, order_by=None):
		return gmProviderInbox.get_inbox_messages(pk_patient = self._payload[self._idx['pk_identity']], order_by = order_by)

	messages = property(get_messages, lambda x:x)
	#--------------------------------------------------------
	def _get_overdue_messages(self):
		return gmProviderInbox.get_overdue_messages(pk_patient = self._payload[self._idx['pk_identity']])

	overdue_messages = property(_get_overdue_messages, lambda x:x)
	#--------------------------------------------------------
	def delete_message(self, pk=None):
		return gmProviderInbox.delete_inbox_message(inbox_message = pk)
	#--------------------------------------------------------
	def _get_dynamic_hints(self, include_suppressed_needing_invalidation=False):
		return gmAutoHints.get_hints_for_patient (
			pk_identity = self._payload[self._idx['pk_identity']],
			include_suppressed_needing_invalidation = include_suppressed_needing_invalidation
		)

	dynamic_hints = property(_get_dynamic_hints, lambda x:x)
	#--------------------------------------------------------
	def _get_suppressed_hints(self):
		return gmAutoHints.get_suppressed_hints(pk_identity = self._payload[self._idx['pk_identity']])

	suppressed_hints = property(_get_suppressed_hints, lambda x:x)

	#--------------------------------------------------------
	def _get_primary_provider_identity(self):
		if self._payload[self._idx['pk_primary_provider']] is None:
			return None
		cmd = u"SELECT * FROM dem.v_all_persons WHERE pk_identity = (SELECT pk_identity FROM dem.v_staff WHERE pk_staff = %(pk_staff)s)"
		args = {'pk_staff': self._payload[self._idx['pk_primary_provider']]}
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)
		if len(rows) == 0:
			return None
		return cPerson(row = {'data': rows[0], 'idx': idx, 'pk_field': 'pk_identity'})

	primary_provider_identity = property(_get_primary_provider_identity, lambda x:x)

	#--------------------------------------------------------
	def _get_primary_provider(self):
		if self._payload[self._idx['pk_primary_provider']] is None:
			return None
		from Gnumed.business import gmStaff
		return gmStaff.cStaff(aPK_obj = self._payload[self._idx['pk_primary_provider']])

	primary_provider = property(_get_primary_provider, lambda x:x)

	#----------------------------------------------------------------------
	# convenience
	#----------------------------------------------------------------------
	def get_dirname(self):
		"""Format patient demographics into patient specific path name fragment."""
		#return (u'%s-%s%s-%s' % (
		return (u'%s-%s-%s' % (
			self._payload[self._idx['lastnames']].replace(u' ', u'_'),
			self._payload[self._idx['firstnames']].replace(u' ', u'_'),
			# privacy
			#gmTools.coalesce(self._payload[self._idx['preferred']], u'', template_initial = u'-(%s)').replace(u' ', u'_'),
			self.get_formatted_dob(format = '%Y-%m-%d', encoding = gmI18N.get_encoding())
		)).replace (
			u"'", u""
		).replace (
			u'"', u''
		).replace (
			u'/', u'_'
		).replace (
			u'\\', u'_'
		).replace (
			u'~', u''
		).replace (
			u'|', u'_'
		).replace (
			u'*', u''
		).replace (
			u'\u2248', u''			# "approximately", having been added by dob_is_estimated
		)

	dirname = property(get_dirname, lambda x:x)

#============================================================
def identity_is_patient(pk_identity):
	cmd = u'SELECT 1 FROM clin.patient WHERE fk_identity = %(pk_pat)s'
	args = {'pk_pat': pk_identity}
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = False)
	if len(rows) == 0:
		return False
	return True

#------------------------------------------------------------
def turn_identity_into_patient(pk_identity):
	cmd = u"""
		INSERT INTO clin.patient (fk_identity)
		SELECT %(pk_ident)s WHERE NOT EXISTS (
			SELECT 1 FROM clin.patient c_p WHERE fk_identity = %(pk_ident)s
		)"""
	args = {u'pk_ident': pk_identity}
	queries = [{'cmd': cmd, 'args': args}]
	gmPG2.run_rw_queries(queries = queries)
	return True

#============================================================
# helper functions
#------------------------------------------------------------
#_spin_on_emr_access = None
#
#def set_emr_access_spinner(func=None):
#	if not callable(func):
#		_log.error('[%] not callable, not setting _spin_on_emr_access', func)
#		return False
#
#	_log.debug('setting _spin_on_emr_access to [%s]', func)
#
#	global _spin_on_emr_access
#	_spin_on_emr_access = func
#

#------------------------------------------------------------
_pull_chart = tui_chart_puller

def set_chart_puller(chart_puller):
	if not callable(chart_puller):
		raise TypeError('chart puller <%s> not callable' % chart_puller)
	global _pull_chart
	_pull_chart = chart_puller
	_log.debug('setting chart puller to <%s>', chart_puller)

_yield = lambda x:x

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
	#----------------------------------------------------------------
	def ensure_has_allergy_state(self, pk_encounter=None):
		from Gnumed.business.gmAllergy import ensure_has_allergy_state
		ensure_has_allergy_state(encounter = pk_encounter)
		return True
	#----------------------------------------------------------
	#----------------------------------------------------------
#	def get_emr(self, allow_user_interaction=True):
#		if not self.__emr_access_lock.acquire(False):
#			# maybe something slow is happening on the machine
#			_log.debug('failed to acquire EMR access lock, sleeping for 500ms')
#			time.sleep(0.5)
#			if not self.__emr_access_lock.acquire(False):
#				_log.error('still failed to acquire EMR access lock, aborting')
#				raise AttributeError('cannot lock access to EMR')
#
#		if self.__emr is None:
#			self.__emr = gmClinicalRecord.cClinicalRecord(aPKey = self._payload[self._idx['pk_identity']], allow_user_interaction = allow_user_interaction)
#			self.__emr.gender = self['gender']
#			self.__emr.dob = self['dob']
#
#		self.__emr_access_lock.release()
#		return self.__emr

	def get_emr(self, allow_user_interaction=True):
		_log.debug('accessing EMR for identity [%s], thread [%s]', self._payload[self._idx['pk_identity']], thread.get_ident())
		stack_logged = False
		if not self.__emr_access_lock.acquire(False):
			got_lock = False
			# do some logging as we failed to get the lock
			call_stack = inspect.stack()
			for idx in range(1, len(call_stack)):
				caller = call_stack[idx]
				_log.debug('%s[%s] @ [%s] in [%s]', u' '* idx, caller[3], caller[2], caller[1])
			del call_stack
			stack_logged = True
			# now loop a bit
			for idx in range(100):
				_yield()
				time.sleep(0.1)
				_yield()
				if self.__emr_access_lock.acquire(False):
					got_lock = True
					break
			if not got_lock:
				_log.error('still failed to acquire EMR access lock, aborting (thread [%s])', thread.get_ident())
				raise AttributeError('cannot lock access to EMR for identity [%s]' % self._payload[self._idx['pk_identity']])

#			# maybe something slow is happening on the machine
#			_log.debug('failed to acquire EMR access lock, sleeping for 500ms (thread %s)', thread.get_ident())
#			time.sleep(0.5)
#			if not self.__emr_access_lock.acquire(False):
#				_log.error('still failed to acquire EMR access lock, aborting (thread %s)', thread.get_ident())
#				raise AttributeError('cannot lock access to EMR')

		if self.__emr is None:
			_log.debug('pulling chart for identity [%s], thread [%s]', self._payload[self._idx['pk_identity']], thread.get_ident())
			if not stack_logged:
				# do some logging as we are pulling the chart for the first time
				call_stack = inspect.stack()
				for idx in range(1, len(call_stack)):
					caller = call_stack[idx]
					_log.debug('%s[%s] @ [%s] in [%s]', u' '* idx, caller[3], caller[2], caller[1])
				del call_stack
				stack_logged = True
			#emr = _pull_chart(self._payload[self._idx['pk_identity']])
			emr = _pull_chart(self)
			if emr is None:		# user aborted pulling chart
				_log.info('user aborted pulling chart, returning None')
				self.__emr_access_lock.release()
				return None
			self.__emr = emr

		_log.debug('returning EMR for identity [%s], thread [%s]', self._payload[self._idx['pk_identity']], thread.get_ident())
		self.__emr_access_lock.release()
		return self.__emr

	emr = property(get_emr, lambda x:x)
	#----------------------------------------------------------
	def get_document_folder(self):
		if self.__doc_folder is None:
			self.__doc_folder = cDocumentFolder(aPKey = self._payload[self._idx['pk_identity']])
		return self.__doc_folder

	document_folder = property(get_document_folder, lambda x:x)

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
			in case the calling code explicitely unset
			the current patient.

		6) Signal "post_patient_selection" is sent.
			Code listening to this signal can
			assume that the new patient is
			already active.
	"""
	def __init__(self, patient=None, forced_reload=False):
		"""Change or get currently active patient.

		patient:
		* None: get currently active patient
		* -1: unset currently active patient
		* cPatient instance: set active patient if possible
		"""
		# make sure we do have a patient pointer
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
			_log.error('patient [%s] is locked, cannot change to [%s]' % (self.patient['pk_identity'], patient))
			return None

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
		if not isinstance(patient, cPatient):
			_log.error('cannot set active patient to [%s], must be either None, -1 or cPatient instance' % str(patient))
			raise TypeError, 'gmPerson.gmCurrentPatient.__init__(): <patient> must be None, -1 or cPatient instance but is: %s' % str(patient)

		# same ID, no change needed
		if (self.patient['pk_identity'] == patient['pk_identity']) and not forced_reload:
			return None

		if patient['is_deleted']:
			_log.error('cannot set active patient to disabled dem.identity row: %s', patient)
			raise ValueError('gmPerson.gmCurrentPatient.__init__(): <patient> is disabled: %s' % patient)

		# user wants different patient
		_log.info('patient change [%s] -> [%s] requested', self.patient['pk_identity'], patient['pk_identity'])

		if not self.__run_callbacks_before_switching_away_from_patient():
			_log.error('not changing current patient, at least one pre-change callback failed')
			return None

		# everything seems swell
		self.__send_pre_unselection_notification()
		self.patient.cleanup()
		self.patient = gmNull.cNull()
		self.__send_unselection_notification()
		# give it some time
		time.sleep(0.5)
		self.patient = patient
		# for good measure ...
		# however, actually we want to get rid of that
		self.patient.get_emr()
		self.__send_selection_notification()

		return None
	#--------------------------------------------------------
	def __register_interests(self):
		gmDispatcher.connect(signal = u'gm_table_mod', receiver = self._on_database_signal)

	#--------------------------------------------------------
	def _on_database_signal(self, **kwds):
		# we don't have a patient: don't process signals
		if isinstance(self.patient, gmNull.cNull):
			return True

		# we only care about identity and name changes
		if kwds['table'] not in [u'dem.identity', u'dem.names']:
			return True

		# signal is not about our patient: ignore signal
		if int(kwds['pk_identity']) != self.patient.ID:
			return True

		if kwds['table'] == u'dem.identity':
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
			raise TypeError(u'callback [%s] not callable' % callback)

		self.__callbacks_before_switching_away_from_patient.append(callback)

	#--------------------------------------------------------
	def _get_connected(self):
		return (not isinstance(self.patient, gmNull.cNull))

	connected = property(_get_connected, lambda x:x)

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
			except:
				_log.exception('callback [%s] failed', call_back)
				print "*** pre-change callback failed ***"
				print type(call_back)
				print call_back
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
			'signal': u'pre_patient_unselection',
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
			'signal': u'current_patient_unset',
			'sender': self.__class__.__name__
		}
		gmDispatcher.send(**kwargs)

	#--------------------------------------------------------
	def __send_selection_notification(self):
		"""Sends signal when another patient has actually been made active."""
		kwargs = {
			'signal': u'post_patient_selection',
			'sender': self.__class__.__name__,
			'pk_identity': self.patient['pk_identity']
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
				u"""SELECT
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
def create_name(pk_person, firstnames, lastnames, active=False):
	queries = [{
		'cmd': u"select dem.add_name(%s, %s, %s, %s)",
		'args': [pk_person, firstnames, lastnames, active]
	}]
	rows, idx = gmPG2.run_rw_queries(queries=queries, return_data=True)
	name = cPersonName(aPK_obj = rows[0][0])
	return name

#============================================================
def create_identity(gender=None, dob=None, lastnames=None, firstnames=None):

	cmd1 = u"""INSERT INTO dem.identity (gender, dob) VALUES (%s, %s)"""
	cmd2 = u"""
INSERT INTO dem.names (
	id_identity, lastnames, firstnames
) VALUES (
	currval('dem.identity_pk_seq'), coalesce(%s, 'xxxDEFAULTxxx'), coalesce(%s, 'xxxDEFAULTxxx')
) RETURNING id_identity"""
#	cmd2 = u"select dem.add_name(currval('dem.identity_pk_seq')::integer, coalesce(%s, 'xxxDEFAULTxxx'), coalesce(%s, 'xxxDEFAULTxxx'), True)"
	rows, idx = gmPG2.run_rw_queries (
		queries = [
			{'cmd': cmd1, 'args': [gender, dob]},
			{'cmd': cmd2, 'args': [lastnames, firstnames]}
			#{'cmd': cmd2, 'args': [firstnames, lastnames]}
		],
		return_data = True
	)
	ident = cPerson(aPK_obj = rows[0][0])
	gmHooks.run_hook_script(hook = u'post_person_creation')
	return ident

#============================================================
def disable_identity(pk_identity):
	_log.info('disabling identity [%s]', pk_identity)
	cmd = u"UPDATE dem.identity SET deleted = true WHERE pk = %(pk)s"
	args = {'pk': identity['pk_identity']}
	gmPG2.run_rw_queries(queries = [
		{'cmd': cmd, 'args': args}
	])
	return True

#============================================================
def create_dummy_identity():
	cmd = u"INSERT INTO dem.identity(gender) VALUES (NULL::text) RETURNING pk"
	rows, idx = gmPG2.run_rw_queries (
		queries = [{'cmd': cmd}],
		return_data = True
	)
	return gmDemographicRecord.cPerson(aPK_obj = rows[0][0])

#============================================================
def identity_exists(pk_identity):
	cmd = u'SELECT EXISTS(SELECT 1 FROM dem.identity where pk = %(pk)s)'
	args = {'pk': pk_identity}
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}])
	return rows[0][0]

#============================================================
def set_active_patient(patient=None, forced_reload=False):
	"""Set active patient.

	If patient is -1 the active patient will be UNset.
	"""
	if isinstance(patient, gmCurrentPatient):
		return True

	if isinstance(patient, cPatient):
		pat = patient
	elif isinstance(patient, cPerson):
		pat = pat.as_patient
	elif patient == -1:
		pat = patient
	else:
		# maybe integer ?
		success, pk = gmTools.input2int(initial = patient, minval = 1)
		if not success:
			raise ValueError('<patient> must be either -1, >0, or a cPatient, cPerson or gmCurrentPatient instance, is: %s' % patient)
		# but also valid patient ID ?
		try:
			pat = cPatient(aPK_obj = pk)
		except:
			_log.exception('identity [%s] not found' % patient)
			return False

	# attempt to switch
	try:
		gmCurrentPatient(patient = pat, forced_reload = forced_reload)
	except:
		_log.exception('error changing active patient to [%s]' % patient)
		return False

	return True

#============================================================
# gender related
#------------------------------------------------------------
def get_gender_list():
	"""Retrieves the list of known genders from the database."""
	global __gender_idx
	global __gender_list

	if __gender_list is None:
		cmd = u"SELECT tag, l10n_tag, label, l10n_label, sort_weight FROM dem.v_gender_labels ORDER BY sort_weight DESC"
		__gender_list, __gender_idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd}], get_col_idx = True)
		_log.debug(u'genders in database: %s' % __gender_list)

	return (__gender_list, __gender_idx)

#------------------------------------------------------------
map_gender2mf = {
	'm': u'm',
	'f': u'f',
	'tf': u'f',
	'tm': u'm',
	'h': u'mf'
}

# https://tools.ietf.org/html/rfc6350#section-6.2.7
# M F O N U
map_gender2vcard = {
	u'm': u'M',
	u'f': u'F',
	u'tf': u'F',
	u'tm': u'M',
	u'h': u'O',
	None: u'U'
}

#------------------------------------------------------------
# maps GNUmed related i18n-aware gender specifiers to a unicode symbol
map_gender2symbol = {
	u'm': u'\u2642',
	u'f': u'\u2640',
	u'tf': u'\u26A5\u2640',
#	'tf': u'\u2642\u2640-\u2640',
	u'tm': u'\u26A5\u2642',
#	'tm': u'\u2642\u2640-\u2642',
	u'h': u'\u26A5',
#	'h': u'\u2642\u2640',
	None: u'?\u26A5?'
}
#------------------------------------------------------------
def map_gender2string(gender=None):
	"""Maps GNUmed related i18n-aware gender specifiers to a human-readable string."""

	global __gender2string_map

	if __gender2string_map is None:
		genders, idx = get_gender_list()
		__gender2string_map = {
			u'm': _(u'male'),
			u'f': _(u'female'),
			u'tf': u'',
			u'tm': u'',
			u'h': u'',
			None: _(u'unknown gender')
		}
		for g in genders:
			__gender2string_map[g[idx['l10n_tag']]] = g[idx['l10n_label']]
			__gender2string_map[g[idx['tag']]] = g[idx['l10n_label']]
		_log.debug(u'gender -> string mapping: %s' % __gender2string_map)

	return __gender2string_map[gender]
#------------------------------------------------------------
def map_gender2salutation(gender=None):
	"""Maps GNUmed related i18n-aware gender specifiers to a human-readable salutation."""

	global __gender2salutation_map

	if __gender2salutation_map is None:
		genders, idx = get_gender_list()
		__gender2salutation_map = {
			'm': _('Mr'),
			'f': _('Mrs'),
			'tf': u'',
			'tm': u'',
			'h': u'',
			None: u''
		}
		for g in genders:
			__gender2salutation_map[g[idx['l10n_tag']]] = __gender2salutation_map[g[idx['tag']]]
			__gender2salutation_map[g[idx['label']]] = __gender2salutation_map[g[idx['tag']]]
			__gender2salutation_map[g[idx['l10n_label']]] = __gender2salutation_map[g[idx['tag']]]
		_log.debug(u'gender -> salutation mapping: %s' % __gender2salutation_map)

	return __gender2salutation_map[gender]
#------------------------------------------------------------
def map_firstnames2gender(firstnames=None):
	"""Try getting the gender for the given first name."""

	if firstnames is None:
		return None

	rows, idx = gmPG2.run_ro_queries(queries = [{
		'cmd': u"SELECT gender FROM dem.name_gender_map WHERE name ILIKE %(fn)s LIMIT 1",
		'args': {'fn': firstnames}
	}])

	if len(rows) == 0:
		return None

	return rows[0][0]
#============================================================
def get_person_IDs():
	cmd = u'SELECT pk FROM dem.identity'
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd}], get_col_idx = False)
	return [ r[0] for r in rows ]

#============================================================
def get_persons_from_pks(pks=None):
	return [ cPerson(aPK_obj = pk) for pk in pks ]
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

	import datetime

	gmI18N.activate_locale()
	gmI18N.install_domain()
	gmDateTime.init()

	#--------------------------------------------------------
	def test_set_active_pat():

		ident = cPerson(1)
		print "setting active patient with", ident
		set_active_patient(patient=ident)

		patient = cPatient(12)
		print "setting active patient with", patient
		set_active_patient(patient=patient)

		pat = gmCurrentPatient()
		print pat['dob']
		#pat['dob'] = 'test'

#		staff = cStaff()
#		print "setting active patient with", staff
#		set_active_patient(patient=staff)

		print "setting active patient with -1"
		set_active_patient(patient=-1)
	#--------------------------------------------------------
	def test_dto_person():
		dto = cDTO_person()
		dto.firstnames = 'Sepp'
		dto.lastnames = 'Herberger'
		dto.gender = 'male'
		dto.dob = pyDT.datetime.now(tz=gmDateTime.gmCurrentLocalTimezone)
		print dto

		print dto['firstnames']
		print dto['lastnames']
		print dto['gender']
		print dto['dob']

		for key in dto.keys():
			print key
	#--------------------------------------------------------
	def test_identity():
		# create patient
		print '\n\nCreating identity...'
		new_identity = create_identity(gender='m', dob='2005-01-01', lastnames='test lastnames', firstnames='test firstnames')
		print 'Identity created: %s' % new_identity

		print '\nSetting title and gender...'
		new_identity['title'] = 'test title';
		new_identity['gender'] = 'f';
		new_identity.save_payload()
		print 'Refetching identity from db: %s' % cPerson(aPK_obj=new_identity['pk_identity'])

		print '\nGetting all names...'
		for a_name in new_identity.get_names():
			print a_name
		print 'Active name: %s' % (new_identity.get_active_name())
		print 'Setting nickname...'
		new_identity.set_nickname(nickname='test nickname')
		print 'Refetching all names...'
		for a_name in new_identity.get_names():
			print a_name
		print 'Active name: %s' % (new_identity.get_active_name())		

		print '\nIdentity occupations: %s' % new_identity['occupations']
		print 'Creating identity occupation...'
		new_identity.link_occupation('test occupation')
		print 'Identity occupations: %s' % new_identity['occupations']

		print '\nIdentity addresses: %s' % new_identity.get_addresses()
		print 'Creating identity address...'
		# make sure the state exists in the backend
		new_identity.link_address (
			number = 'test 1234',
			street = 'test street',
			postcode = 'test postcode',
			urb = 'test urb',
			region_code = u'SN',
			country_code = u'DE'
		)
		print 'Identity addresses: %s' % new_identity.get_addresses()

		print '\nIdentity communications: %s' % new_identity.get_comm_channels()
		print 'Creating identity communication...'
		new_identity.link_comm_channel('homephone', '1234566')
		print 'Identity communications: %s' % new_identity.get_comm_channels()
	#--------------------------------------------------------
	def test_name():
		for pk in range(1,16):
			name = cPersonName(aPK_obj=pk)
			print name.description
			print '  ', name
	#--------------------------------------------------------
	def test_gender_list():
		genders, idx = get_gender_list()
		print "\n\nRetrieving gender enum (tag, label, weight):"
		for gender in genders:
			print "%s, %s, %s" % (gender[idx['tag']], gender[idx['l10n_label']], gender[idx['sort_weight']])
	#--------------------------------------------------------
	def test_export_area():
		person = cPerson(aPK_obj = 12)
		print person
		print person.export_area
		print person.export_area.items
	#--------------------------------------------------------
	def test_ext_id():
		person = cPerson(aPK_obj = 9)
		print person.get_external_ids(id_type=u'Fachgebiet', issuer=u'Ärztekammer')
		#print person.get_external_ids()
	#--------------------------------------------------------
	def test_vcf():
		person = cPerson(aPK_obj = 12)
		print person.export_as_vcard()

	#--------------------------------------------------------
	def test_current_patient():
		pat = gmCurrentPatient()
		print "pat.get_emr()", pat.get_emr()

	#--------------------------------------------------------
	def test_ext_id():
		person = cPerson(aPK_obj = 12)
		print person.suggest_external_id(target = u'Orthanc')
	#--------------------------------------------------------
	#test_dto_person()
	#test_identity()
	#test_set_active_pat()
	#test_search_by_dto()
	#test_name()
	#test_gender_list()

	#map_gender2salutation('m')
	# module functions

	#comms = get_comm_list()
	#print "\n\nRetrieving communication media enum (id, description): %s" % comms
	#test_export_area()
	#test_ext_id()
	#test_vcf()
	test_ext_id()
	test_current_patient()

#============================================================
