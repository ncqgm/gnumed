# -*- coding: utf8 -*-
"""GNUmed patient objects.

This is a patient object intended to let a useful client-side
API crystallize from actual use in true XP fashion.
"""
#============================================================
__version__ = "$Revision: 1.198 $"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL"

# std lib
import sys, os.path, time, re as regex, string, types, datetime as pyDT, codecs, threading, logging


# GNUmed
if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmExceptions, gmDispatcher, gmBorg, gmI18N, gmNull, gmBusinessDBObject, gmTools
from Gnumed.pycommon import gmPG2, gmMatchProvider, gmDateTime
from Gnumed.pycommon import gmLog2
from Gnumed.pycommon import gmHooks
from Gnumed.business import gmDocuments, gmDemographicRecord, gmProviderInbox, gmXdtMappings, gmClinicalRecord


_log = logging.getLogger('gm.person')
_log.info(__version__)

__gender_list = None
__gender_idx = None

__gender2salutation_map = None

#============================================================
# FIXME: make this work as a mapping type, too
class cDTO_person(object):

	def __init__(self):
		self.identity = None
		self.external_ids = []
		self.comm_channels = []
		self.addresses = []
	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def keys(self):
		return 'firstnames lastnames dob gender'.split()
	#--------------------------------------------------------
	def delete_from_source(self):
		pass
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

		where_snippets.append(u'firstnames = %(first)s')
		args['first'] = self.firstnames

		where_snippets.append(u'lastnames = %(last)s')
		args['last'] = self.lastnames

		if self.dob is not None:
			where_snippets.append(u"dem.date_trunc_utc('day'::text, dob) = dem.date_trunc_utc('day'::text, %(dob)s)")
			args['dob'] = self.dob.replace(hour = 23, minute = 59, second = 59)

		if self.gender is not None:
			where_snippets.append('gender = %(sex)s')
			args['sex'] = self.gender

		cmd = u"""
SELECT *, '%s' AS match_type
FROM dem.v_basic_person
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
			identities = [ cIdentity(row = {'pk_field': 'pk_identity', 'data': row, 'idx': idx}) for row in rows ]

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

		for ext_id in self.external_ids:
			try:
				self.identity.add_external_id (
					type_name = ext_id['name'],
					value = ext_id['value'],
					issuer = ext_id['issuer'],
					comment = ext_id['comment']
				)
			except StandardError:
				_log.exception('cannot import <external ID> from external data source')
				_log.log_stack_trace()

		for comm in self.comm_channels:
			try:
				self.identity.link_comm_channel (
					comm_medium = comm['channel'],
					url = comm['url']
				)
			except StandardError:
				_log.exception('cannot import <comm channel> from external data source')
				_log.log_stack_trace()

		for adr in self.addresses:
			try:
				self.identity.link_address (
					number = adr['number'],
					street = adr['street'],
					postcode = adr['zip'],
					urb = adr['urb'],
					state = adr['region'],
					country = adr['country']
				)
			except StandardError:
				_log.exception('cannot import <address> from external data source')
				_log.log_stack_trace()

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
	def remember_address(self, number=None, street=None, urb=None, region=None, zip=None, country=None):
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
		country = country.strip()
		if country == u'':
			raise ValueError(_('<country> cannot be empty'))
		region = region.strip()
		if region == u'':
			region = u'??'
		self.addresses.append ({
			u'number': number,
			u'street': street,
			u'zip': zip,
			u'urb': urb,
			u'region': region,
			u'country': country
		})
	#--------------------------------------------------------
	# customizing behaviour
	#--------------------------------------------------------
	def __str__(self):
		return u'<%s @ %s: %s %s (%s) %s>' % (
			self.__class__.__name__,
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
			'nick': gmTools.coalesce(self._payload[self._idx['preferred']], u'', u' "%s"', u'%s')
		}

	description = property(_get_description, lambda x:x)
#============================================================
class cStaff(gmBusinessDBObject.cBusinessDBObject):
	_cmd_fetch_payload = u"SELECT * FROM dem.v_staff WHERE pk_staff = %s"
	_cmds_store_payload = [
		u"""UPDATE dem.staff SET
				fk_role = %(pk_role)s,
				short_alias = %(short_alias)s,
				comment = gm.nullify_empty_string(%(comment)s),
				is_active = %(is_active)s,
				db_user = %(db_user)s
			WHERE
				pk = %(pk_staff)s
					AND
				xmin = %(xmin_staff)s
			RETURNING
				xmin AS xmin_staff"""
#		,u"""select xmin_staff from dem.v_staff where pk_identity=%(pk_identity)s"""
	]
	_updatable_fields = ['pk_role', 'short_alias', 'comment', 'is_active', 'db_user']
	#--------------------------------------------------------
	def __init__(self, aPK_obj=None, row=None):
		# by default get staff corresponding to CURRENT_USER
		if (aPK_obj is None) and (row is None):
			cmd = u"select * from dem.v_staff where db_user = CURRENT_USER"
			try:
				rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd}], get_col_idx=True)
			except:
				_log.exception('cannot instantiate staff instance')
				gmLog2.log_stack_trace()
				raise ValueError('cannot instantiate staff instance for database account CURRENT_USER')
			if len(rows) == 0:
				raise ValueError('no staff record for database account CURRENT_USER')
			row = {
				'pk_field': 'pk_staff',
				'idx': idx,
				'data': rows[0]
			}
			gmBusinessDBObject.cBusinessDBObject.__init__(self, row = row)
		else:
			gmBusinessDBObject.cBusinessDBObject.__init__(self, aPK_obj = aPK_obj, row = row)

		# are we SELF ?
		self.__is_current_user = (gmPG2.get_current_user() == self._payload[self._idx['db_user']])

		self.__inbox = None
	#--------------------------------------------------------
	def __setitem__(self, attribute, value):
		if attribute == 'db_user':
			if self.__is_current_user:
				_log.debug('will not modify database account association of CURRENT_USER staff member')
				return
		gmBusinessDBObject.cBusinessDBObject.__setitem__(self, attribute, value)
	#--------------------------------------------------------
	def _get_db_lang(self):
		rows, idx = gmPG2.run_ro_queries (
			queries = [{
				'cmd': u'select i18n.get_curr_lang(%(usr)s)',
				'args': {'usr': self._payload[self._idx['db_user']]}
			}]
		)
		return rows[0][0]

	def _set_db_lang(self, language):
		if not gmPG2.set_user_language(language = language):
			raise ValueError (
				u'Cannot set database language to [%s] for user [%s].' % (language, self._payload[self._idx['db_user']])
			)
		return

	database_language = property(_get_db_lang, _set_db_lang)
	#--------------------------------------------------------
	def _get_inbox(self):
		if self.__inbox is None:
			self.__inbox = gmProviderInbox.cProviderInbox(provider_id = self._payload[self._idx['pk_staff']])
		return self.__inbox

	def _set_inbox(self, inbox):
		return

	inbox = property(_get_inbox, _set_inbox)
#============================================================
def set_current_provider_to_logged_on_user():
	gmCurrentProvider(provider = cStaff())
#============================================================
class gmCurrentProvider(gmBorg.cBorg):
	"""Staff member Borg to hold currently logged on provider.

	There may be many instances of this but they all share state.
	"""
	def __init__(self, provider=None):
		"""Change or get currently logged on provider.

		provider:
		* None: get copy of current instance
		* cStaff instance: change logged on provider (role)
		"""
		# make sure we do have a provider pointer
		try:
			self.provider
		except AttributeError:
			self.provider = gmNull.cNull()

		# user wants copy of currently logged on provider
		if provider is None:
			return None

		# must be cStaff instance, then
		if not isinstance(provider, cStaff):
			raise ValueError, 'cannot set logged on provider to [%s], must be either None or cStaff instance' % str(provider)

		# same ID, no change needed
		if self.provider['pk_staff'] == provider['pk_staff']:
			return None

		# first invocation
		if isinstance(self.provider, gmNull.cNull):
			self.provider = provider
			return None

		# user wants different provider
		raise ValueError, 'provider change [%s] -> [%s] not yet supported' % (self.provider['pk_staff'], provider['pk_staff'])

	#--------------------------------------------------------
	def get_staff(self):
		return self.provider
	#--------------------------------------------------------
	# __getitem__ handling
	#--------------------------------------------------------
	def __getitem__(self, aVar):
		"""Return any attribute if known how to retrieve it by proxy.
		"""
		return self.provider[aVar]
	#--------------------------------------------------------
	# __s/getattr__ handling
	#--------------------------------------------------------
	def __getattr__(self, attribute):
		if attribute == 'provider':			# so we can __init__ ourselves
			raise AttributeError
		if not isinstance(self.provider, gmNull.cNull):
			return getattr(self.provider, attribute)
#		raise AttributeError
#============================================================
class cIdentity(gmBusinessDBObject.cBusinessDBObject):
	_cmd_fetch_payload = u"select * from dem.v_basic_person where pk_identity = %s"
	_cmds_store_payload = [
		u"""update dem.identity set
				gender = %(gender)s,
				dob = %(dob)s,
				tob = %(tob)s,
				cob = gm.nullify_empty_string(%(cob)s),
				title = gm.nullify_empty_string(%(title)s),
				fk_marital_status = %(pk_marital_status)s,
				karyotype = gm.nullify_empty_string(%(karyotype)s),
				pupic = gm.nullify_empty_string(%(pupic)s),
				deceased = %(deceased)s,
				emergency_contact = gm.nullify_empty_string(%(emergency_contact)s),
				fk_emergency_contact = %(pk_emergency_contact)s,
				fk_primary_provider = %(pk_primary_provider)s,
				comment = gm.nullify_empty_string(%(comment)s)
			where
				pk = %(pk_identity)s and
				xmin = %(xmin_identity)s""",
		u"""select xmin_identity from dem.v_basic_person where pk_identity = %(pk_identity)s"""
	]
	_updatable_fields = [
		"title",
		"dob",
		"tob",
		"cob",
		"gender",
		"pk_marital_status",
		"karyotype",
		"pupic",
		'deceased',
		'emergency_contact',
		'pk_emergency_contact',
		'pk_primary_provider',
		'comment'
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
					old_dob = self._payload[self._idx['dob']].strftime('%Y %m %d %H %M %S')
					new_dob = value.strftime('%Y %m %d %H %M %S')
					if new_dob == old_dob:
						return

		gmBusinessDBObject.cBusinessDBObject.__setitem__(self, attribute, value)
	#--------------------------------------------------------
	def cleanup(self):
		pass
	#--------------------------------------------------------
	def _get_is_patient(self):
		cmd = u"""
select exists (
	select 1
	from clin.v_emr_journal
	where
		pk_patient = %(pat)s
			and
		soap_cat is not null
)"""
		args = {'pat': self._payload[self._idx['pk_identity']]}
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}])
		return rows[0][0]

	def _set_is_patient(self, value):
		raise AttributeError('setting is_patient status of identity is not allowed')

	is_patient = property(_get_is_patient, _set_is_patient)
	#--------------------------------------------------------
	# identity API
	#--------------------------------------------------------
	def get_active_name(self):
		for name in self.get_names():
			if name['active_name'] is True:
				return name

		_log.error('cannot retrieve active name for patient [%s]' % self._payload[self._idx['pk_identity']])
		return None
	#--------------------------------------------------------
	def get_names(self):
		cmd = u"select * from dem.v_person_names where pk_identity = %(pk_pat)s"
		rows, idx = gmPG2.run_ro_queries (
			queries = [{
				'cmd': cmd,
				'args': {'pk_pat': self._payload[self._idx['pk_identity']]}
			}],
			get_col_idx = True
		)

		if len(rows) == 0:
			# no names registered for patient
			return []

		names = [ cPersonName(row = {'idx': idx, 'data': r, 'pk_field': 'pk_name'}) for r in rows ]
		return names
	#--------------------------------------------------------
	def get_formatted_dob(self, format='%x', encoding=None, none_string=None):
		if self._payload[self._idx['dob']] is None:
			if none_string is None:
				return _('** DOB unknown **')
			return none_string

		if encoding is None:
			encoding = gmI18N.get_encoding()

		return self._payload[self._idx['dob']].strftime(format).decode(encoding)
	#--------------------------------------------------------
	def get_description_gender(self):
		return '%(sex)s%(title)s %(last)s, %(first)s%(nick)s' % {
			'last': self._payload[self._idx['lastnames']],
			'first': self._payload[self._idx['firstnames']],
			'nick': gmTools.coalesce(self._payload[self._idx['preferred']], u'', u' (%s)', u'%s'),
			'sex': map_gender2salutation(self._payload[self._idx['gender']]),
			'title': gmTools.coalesce(self._payload[self._idx['title']], u'', u' %s', u'%s')
		}
	#--------------------------------------------------------
	def get_description(self):
		return '%(last)s,%(title)s %(first)s%(nick)s' % {
			'last': self._payload[self._idx['lastnames']],
			'title': gmTools.coalesce(self._payload[self._idx['title']], u'', u' %s', u'%s'),
			'first': self._payload[self._idx['firstnames']],
			'nick': gmTools.coalesce(self._payload[self._idx['preferred']], u'', u' (%s)', u'%s')
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
		rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': u"select dem.set_nickname(%s, %s)", 'args': [self.ID, nickname]}])
		self.refetch_payload()
		return True
	#--------------------------------------------------------
	# external ID API
	#
	# since external IDs are not treated as first class
	# citizens (classes in their own right, that is), we
	# handle them *entirely* within cIdentity, also they
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

		creates ID type if necessary
		"""
		cmd = u"""
update dem.lnk_identity2ext_id set
	fk_origin = (select dem.add_external_id_type(%(type)s, %(issuer)s)),
	external_id = %(value)s,
	comment = %(comment)s
where id = %(pk)s"""
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

		cmd = u"select * from dem.v_external_ids4identity where %s" % ' and '.join(where_parts)
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}])

		return rows
	#--------------------------------------------------------
	def delete_external_id(self, pk_ext_id=None):
		cmd = u"""
delete from dem.lnk_identity2ext_id
where id_identity = %(pat)s and id = %(pk)s"""
		args = {'pat': self.ID, 'pk': pk_ext_id}
		gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])
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
		args = {'old_pat': other_identity.ID, 'new_pat': self.ID}

		# delete old allergy state
		queries.append ({
			'cmd': u'delete from clin.allergy_state where pk = (select pk_allergy_state from clin.v_pat_allergy_state where pk_patient = %(old_pat)s)',
			'args': args
		})
		# FIXME: adjust allergy_state in kept patient

		# deactivate all names of old patient
		queries.append ({
			'cmd': u'update dem.names set active = False where id_identity = %(old_pat)s',
			'args': args
		})

		# find FKs pointing to identity
		FKs = gmPG2.get_foreign_keys2column (
			schema = u'dem',
			table = u'identity',
			column = u'pk'
		)

		# generate UPDATEs
		cmd_template = u'update %s set %s = %%(new_pat)s where %s = %%(old_pat)s'
		for FK in FKs:
			queries.append ({
				'cmd': cmd_template % (FK['referencing_table'], FK['referencing_column'], FK['referencing_column']),
				'args': args
			})

		# remove old identity entry
		queries.append ({
			'cmd': u'delete from dem.identity where pk = %(old_pat)s',
			'args': args
		})

		_log.warning('identity [%s] is about to assimilate identity [%s]', self.ID, other_identity.ID)

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
		gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}], verbose=True)
	#--------------------------------------------------------
	def export_as_gdt(self, filename=None, encoding='iso-8859-15', external_id_type=None):

		template = u'%s%s%s\r\n'

		file = codecs.open (
			filename = filename,
			mode = 'wb',
			encoding = encoding,
			errors = 'strict'
		)

		file.write(template % (u'013', u'8000', u'6301'))
		file.write(template % (u'013', u'9218', u'2.10'))
		if external_id_type is None:
			file.write(template % (u'%03d' % (9 + len(str(self.ID))), u'3000', self.ID))
		else:
			ext_ids = self.get_external_ids(id_type = external_id_type)
			if len(ext_ids) > 0:
				file.write(template % (u'%03d' % (9 + len(ext_ids[0]['value'])), u'3000', ext_ids[0]['value']))
		file.write(template % (u'%03d' % (9 + len(self._payload[self._idx['lastnames']])), u'3101', self._payload[self._idx['lastnames']]))
		file.write(template % (u'%03d' % (9 + len(self._payload[self._idx['firstnames']])), u'3102', self._payload[self._idx['firstnames']]))
		file.write(template % (u'%03d' % (9 + len(self._payload[self._idx['dob']].strftime('%d%m%Y'))), u'3103', self._payload[self._idx['dob']].strftime('%d%m%Y')))
		file.write(template % (u'010', u'3110', gmXdtMappings.map_gender_gm2xdt[self._payload[self._idx['gender']]]))
		file.write(template % (u'025', u'6330', 'GNUmed::9206::encoding'))
		file.write(template % (u'%03d' % (9 + len(encoding)), u'6331', encoding))
		if external_id_type is None:
			file.write(template % (u'029', u'6332', u'GNUmed::3000::source'))
			file.write(template % (u'017', u'6333', u'internal'))
		else:
			if len(ext_ids) > 0:
				file.write(template % (u'029', u'6332', u'GNUmed::3000::source'))
				file.write(template % (u'%03d' % (9 + len(external_id_type)), u'6333', external_id_type))

		file.close()
	#--------------------------------------------------------
	# occupations API
	#--------------------------------------------------------
	def get_occupations(self):
		cmd = u"select * from dem.v_person_jobs where pk_identity=%s"
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': [self.pk_obj]}])
		return rows
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
		cmd = u"select * from dem.v_pat_addresses where pk_identity=%s"
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': [self.pk_obj]}], get_col_idx=True)
		addresses = []
		for r in rows:
			addresses.append(gmDemographicRecord.cPatientAddress(row={'idx': idx, 'data': r, 'pk_field': 'pk_address'}))

		filtered = addresses

		if address_type is not None:
			filtered = []
			for adr in addresses:
				if adr['address_type'] == address_type:
					filtered.append(adr)

		return filtered
	#--------------------------------------------------------
	def link_address(self, number=None, street=None, postcode=None, urb=None, state=None, country=None, subunit=None, suburb=None, id_type=None):
		"""Link an address with a patient, creating the address if it does not exists.

		@param number The number of the address.
		@param street The name of the street.
		@param postcode The postal code of the address.
		@param urb The name of town/city/etc.
		@param state The code of the state.
		@param country The code of the country.
		@param id_type The primary key of the address type.
		"""
		# create/get address
		adr = gmDemographicRecord.create_address (
			country = country,
			state = state,
			urb = urb,
			suburb = suburb,
			postcode = postcode,
			street = street,
			number = number,
			subunit = subunit
		)

		# already linked ?
		cmd = u"select * from dem.lnk_person_org_address where id_identity = %s and id_address = %s"
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': [self.pk_obj, adr['pk_address']]}])
		# no, link to person
		if len(rows) == 0:
			args = {'id': self.pk_obj, 'adr': adr['pk_address'], 'type': id_type}
			if id_type is None:
				cmd = u"""
					insert into dem.lnk_person_org_address(id_identity, id_address)
					values (%(id)s, %(adr)s)"""
			else:
				cmd = u"""
					insert into dem.lnk_person_org_address(id_identity, id_address, id_type)
					values (%(id)s, %(adr)s, %(type)s)"""
			rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])
		else:
			# already linked - but needs to change type ?
			if id_type is not None:
				r = rows[0]
				if r['id_type'] != id_type:
					cmd = "update dem.lnk_person_org_address set id_type = %(type)s where id = %(id)s"
					gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': {'type': id_type, 'id': r['id']}}])

		return adr
	#----------------------------------------------------------------------
	def unlink_address(self, address=None):
		"""Remove an address from the patient.

		The address itself stays in the database.
		The address can be either cAdress or cPatientAdress.
		"""
		cmd = u"delete from dem.lnk_person_org_address where id_identity = %(person)s and id_address = %(adr)s"
		args = {'person': self.pk_obj, 'adr': address['pk_address']}
		gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])
	#----------------------------------------------------------------------
	# relatives API
	#----------------------------------------------------------------------
	def get_relatives(self):
		cmd = u"""
			select
				t.description,
				vbp.pk_identity as id,
				title,
				firstnames,
				lastnames,
				dob,
				cob,
				gender,
				karyotype,
				pupic,
				pk_marital_status,
				marital_status,
				xmin_identity,
				preferred
			from
				dem.v_basic_person vbp, dem.relation_types t, dem.lnk_person2relative l
			where
				(
					l.id_identity = %(pk)s and
					vbp.pk_identity = l.id_relative and
					t.id = l.id_relation_type
				) or (
					l.id_relative = %(pk)s and
					vbp.pk_identity = l.id_identity and
					t.inverse = l.id_relation_type
				)"""
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': {'pk': self.pk_obj}}])
		if len(rows) == 0:
			return []
		return [(row[0], cIdentity(row = {'data': row[1:], 'idx':idx, 'pk_field': 'pk'})) for row in rows]
	#--------------------------------------------------------
	def link_new_relative(self, rel_type = 'parent'):
		# create new relative
		id_new_relative = create_dummy_identity()

		relative = cIdentity(aPK_obj=id_new_relative)
		# pre-fill with data from ourselves
#		relative.copy_addresses(self)
		relative.add_name( '**?**', self.get_names()['lastnames'])
		# and link the two
		if self._ext_cache.has_key('relatives'):
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
		return cIdentity(aPK_obj = self._payload[self._idx['pk_emergency_contact']])

	emergency_contact_in_database = property(_get_emergency_contact_from_database, lambda x:x)
	#----------------------------------------------------------------------
	# age/dob related
	#----------------------------------------------------------------------
	def get_medical_age(self):
		dob = self['dob']

		if dob is None:
			return u'??'

		if self['deceased'] is None:
#			return gmDateTime.format_interval_medically (
#				pyDT.datetime.now(tz = gmDateTime.gmCurrentLocalTimezone) - dob
#			)
			return gmDateTime.format_apparent_age_medically (
				age = gmDateTime.calculate_apparent_age(start = dob)
			)

		return u'%s%s' % (
			gmTools.u_latin_cross,
#			gmDateTime.format_interval_medically(self['deceased'] - dob)
			gmDateTime.format_apparent_age_medically (
				age = gmDateTime.calculate_apparent_age (
					start = dob,
					end = self['deceased']
				)
			)
		)
	#----------------------------------------------------------------------
	def dob_in_range(self, min_distance=u'1 week', max_distance=u'1 week'):
		cmd = u'select dem.dob_is_in_range(%(dob)s, %(min)s, %(max)s)'
		rows, idx = gmPG2.run_ro_queries (
			queries = [{
				'cmd': cmd,
				'args': {'dob': self['dob'], 'min': min_distance, 'max': max_distance}
			}]
		)
		return rows[0][0]
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
	def _get_messages(self):
		return gmProviderInbox.get_inbox_messages(pk_patient = self._payload[self._idx['pk_identity']])

	def _set_messages(self, messages):
		return

	messages = property(_get_messages, _set_messages)
	#--------------------------------------------------------
	def delete_message(self, pk=None):
		return gmProviderInbox.delete_inbox_message(pk = pk)
	#--------------------------------------------------------
	def _get_primary_provider(self):
		if self._payload[self._idx['pk_primary_provider']] is None:
			return None
		return cStaff(aPK_obj = self._payload[self._idx['pk_primary_provider']])

	primary_provider = property(_get_primary_provider, lambda x:x)
	#----------------------------------------------------------------------
	# convenience
	#----------------------------------------------------------------------
	def get_dirname(self):
		"""Format patient demographics into patient specific path name fragment."""
		return '%s-%s%s-%s' % (
			self._payload[self._idx['lastnames']].replace(u' ', u'_'),
			self._payload[self._idx['firstnames']].replace(u' ', u'_'),
			gmTools.coalesce(self._payload[self._idx['preferred']], u'', template_initial = u'-(%s)'),
			self.get_formatted_dob(format = '%Y-%m-%d', encoding = gmI18N.get_encoding())
		)
#============================================================
class cStaffMember(cIdentity):
	"""Represents a staff member which is a person.

	- a specializing subclass of cIdentity turning it into a staff member
	"""
	def __init__(self, identity = None):
		cIdentity.__init__(self, identity=identity)
		self.__db_cache = {}
	#--------------------------------------------------------
	def get_inbox(self):
		return gmProviderInbox.cProviderInbox(provider_id = self.ID)
#============================================================
class cPatient(cIdentity):
	"""Represents a person which is a patient.

	- a specializing subclass of cIdentity turning it into a patient
	- its use is to cache subobjects like EMR and document folder
	"""
	def __init__(self, aPK_obj=None, row=None):
		cIdentity.__init__(self, aPK_obj=aPK_obj, row=row)
		self.__db_cache = {}
		self.__emr_access_lock = threading.Lock()
	#--------------------------------------------------------
	def cleanup(self):
		"""Do cleanups before dying.

		- note that this may be called in a thread
		"""
		if self.__db_cache.has_key('clinical record'):
			self.__db_cache['clinical record'].cleanup()
		if self.__db_cache.has_key('document folder'):
			self.__db_cache['document folder'].cleanup()
		cIdentity.cleanup(self)
	#----------------------------------------------------------
	def get_emr(self):
		if not self.__emr_access_lock.acquire(False):
			raise AttributeError('cannot access EMR')
		try:
			emr = self.__db_cache['clinical record']
			self.__emr_access_lock.release()
			return emr
		except KeyError:
			pass

		self.__db_cache['clinical record'] = gmClinicalRecord.cClinicalRecord(aPKey = self._payload[self._idx['pk_identity']])
		self.__emr_access_lock.release()
		return self.__db_cache['clinical record']
	#--------------------------------------------------------
	def get_document_folder(self):
		try:
			return self.__db_cache['document folder']
		except KeyError:
			pass

		self.__db_cache['document folder'] = gmDocuments.cDocumentFolder(aPKey = self._payload[self._idx['pk_identity']])
		return self.__db_cache['document folder']
#============================================================
class gmCurrentPatient(gmBorg.cBorg):
	"""Patient Borg to hold currently active patient.

	There may be many instances of this but they all share state.
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
			tmp = self.patient
		except AttributeError:
			self.patient = gmNull.cNull()
			self.__register_interests()
			# set initial lock state,
			# this lock protects against activating another patient
			# when we are controlled from a remote application
			self.__lock_depth = 0
			# initialize callback state
			self.__pre_selection_callbacks = []

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
			if not self.__run_pre_selection_callbacks():
				_log.debug('not unsetting current patient')
				return None
			self.__send_pre_selection_notification()
			self.patient.cleanup()
			self.patient = gmNull.cNull()
			self.__send_selection_notification()
			return None

		# must be cPatient instance, then
		if not isinstance(patient, cPatient):
			_log.error('cannot set active patient to [%s], must be either None, -1 or cPatient instance' % str(patient))
			raise TypeError, 'gmPerson.gmCurrentPatient.__init__(): <patient> must be None, -1 or cPatient instance but is: %s' % str(patient)

		# same ID, no change needed
		if (self.patient['pk_identity'] == patient['pk_identity']) and not forced_reload:
			return None

		# user wants different patient
		_log.debug('patient change [%s] -> [%s] requested', self.patient['pk_identity'], patient['pk_identity'])

		# everything seems swell
		if not self.__run_pre_selection_callbacks():
			_log.debug('not changing current patient')
			return None
		self.__send_pre_selection_notification()
		self.patient.cleanup()
		self.patient = patient
		self.patient.get_emr()
		self.__send_selection_notification()

		return None
	#--------------------------------------------------------
	def __register_interests(self):
		gmDispatcher.connect(signal = u'identity_mod_db', receiver = self._on_identity_change)
		gmDispatcher.connect(signal = u'name_mod_db', receiver = self._on_identity_change)
	#--------------------------------------------------------
	def _on_identity_change(self):
		"""Listen for patient *data* change."""
		self.patient.refetch_payload()
	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def register_pre_selection_callback(self, callback=None):
		if not callable(callback):
			raise TypeError(u'callback [%s] not callable' % callback)

		self.__pre_selection_callbacks.append(callback)
	#--------------------------------------------------------
	def _get_connected(self):
		return (not isinstance(self.patient, gmNull.cNull))

	def _set_connected(self):
		raise AttributeError(u'invalid to set <connected> state')

	connected = property(_get_connected, _set_connected)
	#--------------------------------------------------------
	def _get_locked(self):
		return (self.__lock_depth > 0)

	def _set_locked(self, locked):
		if locked:
			self.__lock_depth = self.__lock_depth + 1
			gmDispatcher.send(signal='patient_locked')
		else:
			if self.__lock_depth == 0:
				_log.error('lock/unlock imbalance, trying to refcount lock depth below 0')
				return
			else:
				self.__lock_depth = self.__lock_depth - 1
			gmDispatcher.send(signal='patient_unlocked')

	locked = property(_get_locked, _set_locked)
	#--------------------------------------------------------
	def force_unlock(self):
		_log.info('forced patient unlock at lock depth [%s]' % self.__lock_depth)
		self.__lock_depth = 0
		gmDispatcher.send(signal='patient_unlocked')
	#--------------------------------------------------------
	# patient change handling
	#--------------------------------------------------------
	def __run_pre_selection_callbacks(self):
		if isinstance(self.patient, gmNull.cNull):
			return True

		for call_back in self.__pre_selection_callbacks:
			try:
				successful = call_back()
			except:
				_log.exception('callback [%s] failed', call_back)
				print "*** pre-selection callback failed ***"
				print type(call_back)
				print call_back
				return False

			if not successful:
				_log.debug('callback [%s] returned False', call_back)
				return False

		return True
	#--------------------------------------------------------
	def __send_pre_selection_notification(self):
		"""Sends signal when another patient is about to become active.

		This does NOT wait for signal handlers to complete.
		"""
		kwargs = {
			'signal': u'pre_patient_selection',
			'sender': id(self.__class__),
			'pk_identity': self.patient['pk_identity']
		}
		gmDispatcher.send(**kwargs)
	#--------------------------------------------------------
	def __send_selection_notification(self):
		"""Sends signal when another patient has actually been made active."""
		kwargs = {
			'signal': u'post_patient_selection',
			'sender': id(self.__class__),
			'pk_identity': self.patient['pk_identity']
		}
		gmDispatcher.send(**kwargs)
	#--------------------------------------------------------
	# __getattr__ handling
	#--------------------------------------------------------
	def __getattr__(self, attribute):
		if attribute == 'patient':
			raise AttributeError
		if not isinstance(self.patient, gmNull.cNull):
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
				u"""select
						pk_staff,
						short_alias || ' (' || coalesce(title, '') || firstnames || ' ' || lastnames || ')',
						1
					from dem.v_staff
					where
						is_active and (
							short_alias %(fragment_condition)s or
							firstnames %(fragment_condition)s or
							lastnames %(fragment_condition)s or
							db_user %(fragment_condition)s
						)"""
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
	rows, idx = gmPG2.run_rw_queries (
		queries = [
			{'cmd': cmd1, 'args': [gender, dob]},
			{'cmd': cmd2, 'args': [lastnames, firstnames]}
		],
		return_data = True
	)
	ident = cIdentity(aPK_obj=rows[0][0])
	gmHooks.run_hook_script(hook = u'post_person_creation')
	return ident
#============================================================
def create_dummy_identity():
	cmd = u"INSERT INTO dem.identity(gender) VALUES ('xxxDEFAULTxxx') RETURNING pk"
	rows, idx = gmPG2.run_rw_queries (
		queries = [{'cmd': cmd}],
		return_data = True
	)
	return gmDemographicRecord.cIdentity(aPK_obj = rows[0][0])
#============================================================
def set_active_patient(patient=None, forced_reload=False):
	"""Set active patient.

	If patient is -1 the active patient will be UNset.
	"""
	if isinstance(patient, cPatient):
		pat = patient
	elif isinstance(patient, cIdentity):
		pat = cPatient(aPK_obj=patient['pk_identity'])
	elif isinstance(patient, cStaff):
		pat = cPatient(aPK_obj=patient['pk_identity'])
	elif isinstance(patient, gmCurrentPatient):
		pat = patient.patient
	elif patient == -1:
		pat = patient
	else:
		raise ValueError('<patient> must be either -1, cPatient, cStaff, cIdentity or gmCurrentPatient instance, is: %s' % patient)

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
		cmd = u"select tag, l10n_tag, label, l10n_label, sort_weight from dem.v_gender_labels order by sort_weight desc"
		__gender_list, __gender_idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd}], get_col_idx = True)

	return (__gender_list, __gender_idx)
#------------------------------------------------------------
map_gender2mf = {
	'm': u'm',
	'f': u'f',
	'tf': u'f',
	'tm': u'm',
	'h': u'mf'
}
#------------------------------------------------------------
# Maps GNUmed related i18n-aware gender specifiers to a unicode symbol.
map_gender2symbol = {
	'm': u'\u2642',
	'f': u'\u2640',
	'tf': u'\u26A5\u2640',
	'tm': u'\u26A5\u2642',
	'h': u'\u26A5'
#	'tf': u'\u2642\u2640-\u2640',
#	'tm': u'\u2642\u2640-\u2642',
#	'h': u'\u2642\u2640'
}
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
			'h': u''
		}
		for g in genders:
			__gender2salutation_map[g[idx['l10n_tag']]] = __gender2salutation_map[g[idx['tag']]]
			__gender2salutation_map[g[idx['label']]] = __gender2salutation_map[g[idx['tag']]]
			__gender2salutation_map[g[idx['l10n_label']]] = __gender2salutation_map[g[idx['tag']]]

	return __gender2salutation_map[gender]
#------------------------------------------------------------
def map_firstnames2gender(firstnames=None):
	"""Try getting the gender for the given first name."""

	if firstnames is None:
		return None

	rows, idx = gmPG2.run_ro_queries(queries = [{
		'cmd': u"select gender from dem.name_gender_map where name ilike %(fn)s limit 1",
		'args': {'fn': firstnames}
	}])

	if len(rows) == 0:
		return None

	return rows[0][0]
#============================================================
def get_staff_list(active_only=False):
	if active_only:
		cmd = u"select * from dem.v_staff where is_active order by can_login desc, short_alias asc"
	else:
		cmd = u"select * from dem.v_staff order by can_login desc, is_active desc, short_alias asc"
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd}], get_col_idx=True)
	staff_list = []
	for row in rows:
		obj_row = {
			'idx': idx,
			'data': row,
			'pk_field': 'pk_staff'
		}
		staff_list.append(cStaff(row=obj_row))
	return staff_list
#============================================================
def get_persons_from_pks(pks=None):
	return [ cIdentity(aPK_obj = pk) for pk in pks ]
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

		ident = cIdentity(1)
		print "setting active patient with", ident
		set_active_patient(patient=ident)

		patient = cPatient(12)
		print "setting active patient with", patient
		set_active_patient(patient=patient)

		pat = gmCurrentPatient()
		print pat['dob']
		#pat['dob'] = 'test'

		staff = cStaff()
		print "setting active patient with", staff
		set_active_patient(patient=staff)

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
	def test_staff():
		staff = cStaff()
		print staff
		print staff.inbox
		print staff.inbox.messages
	#--------------------------------------------------------
	def test_current_provider():
		staff = cStaff()
		provider = gmCurrentProvider(provider = staff)
		print provider
		print provider.inbox
		print provider.inbox.messages
		print provider.database_language
		tmp = provider.database_language
		provider.database_language = None
		print provider.database_language
		provider.database_language = tmp
		print provider.database_language
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
		print 'Refetching identity from db: %s' % cIdentity(aPK_obj=new_identity['pk_identity'])

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
			state = 'SN',
			country = 'DE'
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
	#test_dto_person()
	#test_identity()
	#test_set_active_pat()
	#test_search_by_dto()
	#test_staff()
	test_current_provider()
	#test_name()

	#map_gender2salutation('m')
	# module functions
	#genders, idx = get_gender_list()
	#print "\n\nRetrieving gender enum (tag, label, weight):"	
	#for gender in genders:
	#	print "%s, %s, %s" % (gender[idx['tag']], gender[idx['l10n_label']], gender[idx['sort_weight']])

	#comms = get_comm_list()
	#print "\n\nRetrieving communication media enum (id, description): %s" % comms

#============================================================
