# -*- coding: utf-8 -*-
"""GNUmed staff objects."""
#============================================================
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL"

# std lib
import sys
import logging

# GNUmed
if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmBusinessDBObject
from Gnumed.pycommon import gmPG2
from Gnumed.pycommon import gmNull
from Gnumed.pycommon import gmBorg
from Gnumed.pycommon import gmLog2


_log = logging.getLogger('gm.staff')

_map_gm_role2pg_group = {
	'public access': 'gm-public',
	'non-clinical access': 'gm-staff',
	'full clinical access': 'gm-doctors'
}

#============================================================
_SQL_get_staff_fields = 'SELECT *, _(role) AS l10n_role FROM dem.v_staff WHERE %s'

class cStaff(gmBusinessDBObject.cBusinessDBObject):
	_cmd_fetch_payload = _SQL_get_staff_fields % "pk_staff = %s"
	_cmds_store_payload = [
		"""UPDATE dem.staff SET
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
	]
	_updatable_fields = ['short_alias', 'comment', 'is_active', 'db_user']

	#--------------------------------------------------------
	def __init__(self, aPK_obj=None, row=None):
		# by default get staff corresponding to CURRENT_USER
		if (aPK_obj is None) and (row is None):
			cmd = _SQL_get_staff_fields % "db_user = CURRENT_USER"
			try:
				rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd}], get_col_idx=True)
			except Exception:
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
				'cmd': 'select i18n.get_curr_lang(%(usr)s)',
				'args': {'usr': self._payload[self._idx['db_user']]}
			}]
		)
		return rows[0][0]

	def _set_db_lang(self, language):
		if not gmPG2.set_user_language(language = language):
			raise ValueError (
				'Cannot set database language to [%s] for user [%s].' % (language, self._payload[self._idx['db_user']])
			)
		return

	database_language = property(_get_db_lang, _set_db_lang)

	#--------------------------------------------------------
	def _get_inbox(self):
		if self.__inbox is None:
			from Gnumed.business import gmProviderInbox
			self.__inbox = gmProviderInbox.cProviderInbox(provider_id = self._payload[self._idx['pk_staff']])
		return self.__inbox

	def _set_inbox(self, inbox):
		return

	inbox = property(_get_inbox, _set_inbox)

	#--------------------------------------------------------
	def _get_identity(self):
		from Gnumed.business.gmPerson import cPerson
		return cPerson(self._payload[self._idx['pk_identity']])

	identity = property(_get_identity, lambda x:x)

	#--------------------------------------------------------
	def set_role(self, conn=None, role=None):
		if role.strip() == self._payload[self._idx['role']]:
			return True

		cmd = 'SELECT gm.add_user_to_permission_group(%(usr)s::name, %(grp)s::name)'
		args = {
			'usr': self._payload[self._idx['db_user']],
			'grp': _map_gm_role2pg_group[role.strip()]
		}
		rows, idx = gmPG2.run_rw_queries (
			link_obj = conn,
			queries = [{'cmd': cmd, 'args': args}],
			get_col_idx = False,
			return_data = True,
			end_tx = True
		)
		if not rows[0][0]:
			return False
		self.refetch_payload()
		return True

	role = property(lambda x:x, set_role)

#============================================================
def get_staff_list(active_only=False):
	if active_only:
		cmd = _SQL_get_staff_fields % 'is_active ORDER BY can_login DESC, short_alias ASC'
	else:
		cmd = _SQL_get_staff_fields % 'TRUE ORDER BY can_login DESC, is_active DESC, short_alias ASC'
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

#------------------------------------------------------------
def create_staff(conn=None, db_account=None, password=None, identity=None, short_alias=None):
	args = {
		'pg_usr': db_account,
		'pwd': password,
		'person_id': identity,
		'sig': short_alias
	}

	queries = [
		{'cmd': 'SELECT gm.create_user(%(pg_usr)s, %(pwd)s)', 'args': args},
		{'cmd': """
			INSERT INTO dem.staff
				(fk_identity, db_user, short_alias)
			VALUES (
				%(person_id)s,
				%(pg_usr)s,
				%(sig)s
			)""",
		 'args': args
		}
	]

	created = False
	try:
		rows, idx = gmPG2.run_rw_queries(link_obj = conn, queries = queries, end_tx = True)
		created = True
	except gmPG2.dbapi.IntegrityError as e:
		if e.pgcode != gmPG2.sql_error_codes.UNIQUE_VIOLATION:
			raise

	if created:
		return True, None

	msg = _(
		'Cannot add GNUmed user.\n'
		'\n'
		'The database account [%s] is already listed as a\n'
		'GNUmed user. There can only be one GNUmed user\n'
		'for each database account.\n'
	) % db_account
	return False, msg

#------------------------------------------------------------
def delete_staff(conn=None, pk_staff=None):
	deleted = False
	queries = [{'cmd': 'DELETE FROM dem.staff WHERE pk = %(pk)s', 'args': {'pk': pk_staff}}]
	try:
		rows, idx = gmPG2.run_rw_queries(link_obj = conn, queries = queries, end_tx = True)
		deleted = True
	except gmPG2.dbapi.IntegrityError as e:
		if e.pgcode != gmPG2.sql_error_codes.FOREIGN_KEY_VIOLATION:		# 23503  foreign_key_violation
			raise

	if deleted:
		return True, None

	deactivate_staff(conn = conn, pk_staff = pk_staff)
	msg = _(
		'Cannot delete GNUmed staff member because the\n'
		'database still contains data linked to it.\n'
		'\n'
		'The account was deactivated instead.'
	)
	return False, msg

#------------------------------------------------------------
def activate_staff(conn=None, pk_staff=None):
	# 1) activate staff entry
	staff = cStaff(aPK_obj = pk_staff)
	staff['is_active'] = True
	staff.save_payload(conn=conn)				# FIXME: error handling
	# 2) enable database account login
	rowx, idx = gmPG2.run_rw_queries (
		link_obj = conn,
		# password does not matter because PG account must already exist
		queries = [{'cmd': 'select gm.create_user(%s, %s)', 'args': [staff['db_user'], 'flying wombat']}],
		end_tx = True
	)
	return True

#------------------------------------------------------------
def deactivate_staff(conn=None, pk_staff=None):

	# 1) inactivate staff entry
	staff = cStaff(aPK_obj = pk_staff)
	staff['is_active'] = False
	staff.save_payload(conn = conn)				# FIXME: error handling
	# 2) disable database account login
	rows, idx = gmPG2.run_rw_queries (
		link_obj = conn,
		queries = [{'cmd': 'select gm.disable_user(%s)', 'args': [staff['db_user']]}],
		end_tx = True
	)
	return True

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
			raise ValueError('cannot set logged on provider to [%s], must be either None or cStaff instance' % str(provider))

		# first invocation
		if isinstance(self.provider, gmNull.cNull):
			self.provider = provider
			return None

		# same ID, no change needed
		if self.provider['pk_staff'] == provider['pk_staff']:
			return None

		# user wants different provider
		raise ValueError('provider change [%s] -> [%s] not yet supported' % (self.provider['pk_staff'], provider['pk_staff']))

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
# main/testing
#============================================================
if __name__ == '__main__':

	if len(sys.argv) == 1:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	import datetime
	from Gnumed.pycommon import gmI18N
	from Gnumed.pycommon import gmDateTime

	gmI18N.activate_locale()
	gmI18N.install_domain()
	gmDateTime.init()

	#--------------------------------------------------------
	def test_staff():
		staff = cStaff()
		print(staff)
		print(staff.inbox)
		print(staff.inbox.messages)
	#--------------------------------------------------------
	def test_current_provider():
		staff = cStaff()
		provider = gmCurrentProvider(provider = staff)
		print(provider)
		print(provider.inbox)
		print(provider.inbox.messages)
		print(provider.database_language)
		tmp = provider.database_language
		provider.database_language = None
		print(provider.database_language)
		provider.database_language = tmp
		print(provider.database_language)
	#--------------------------------------------------------
	test_staff()
	#test_current_provider()

#============================================================
