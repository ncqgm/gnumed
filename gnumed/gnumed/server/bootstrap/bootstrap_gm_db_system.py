#!/usr/bin/python3

"""GNUmed schema installation.

This script bootstraps a GNUmed database system.

It will set up databases, tables, groups, permissions and
possibly users. Most of this will be handled via SQL
scripts, not directly in the bootstrapper itself.

Assumptions:

- PostgreSQL running on localhost

- everything happening within one cluster
	* host: defaults to localhost, else $GM_CLUSTER_HOSTNAME
	* port: defaults to 5432, else $GM_CLUSTER_PORT
	* maintenance database: defaults to "template1", else $GM_CLUSTER_MAINTENANCE_DB

- postmaster process demon account
	* read from $GM_POSTMASTER_DEMON_USER or
	* one of "postgres", "pgsql" or "postgresql"
	* verified to exist, in that order, in /etc/passwd
	* if not verifiable: assumed "postgres"

- PostgreSQL superuser
	* assumed identical to postmaster demon account
	* can be overriden by environment variable $GM_CLUSTER_SUPERUSER

- database/objects/... owner: "gm-dbo"

- database name: gnumed_vXX where XX is the current major version

- user running the bootstrapper must be able to become
  (SUID) the postmaster demon account user

- postmaster demon account user must be able to connect
  to the cluster maintenance database without providing a
  password (IOW .pgpass / PGPASSFILE / IDENT / TRUST / PEER)


This script does NOT set up user specific configuration options.

All definitions are loaded from a config file.


--quiet
--log-file=
--conf-file=

Requires psycopg 2.7.4.
"""
#==================================================================
# TODO
# - perhaps create PGPASSFILE
# - warn if empty password
# - verify that pre-created database is owned by "gm-dbo"
# - rework under assumption that there is only one DB
#==================================================================
__author__ = "Karsten.Hilbert@gmx.net"
__license__ = "GPL v2 or later"


_GM_LOGINS_GROUP = 'gm-logins'
_GM_DBO_ROLE = 'gm-dbo'
_PM_DEMON_USER = None
_PM_DEMON_UID = None
_PG_SUPERUSER = None

# standard library
import sys
if sys.hexversion < 0x3000000:
	sys.exit('This code must be run with Python 3.')

import os.path
import fileinput
import os
import getpass
import re as regex
import tempfile
import logging
import faulthandler


faulthandler.enable()


# adjust Python path
local_python_base_dir = os.path.dirname (
	os.path.abspath(os.path.join(sys.argv[0], '..', '..'))
)

# does the GNUmed import path exist at all, physically ?
# (*broken* links are reported as False)
if not os.path.exists(os.path.join(local_python_base_dir, 'Gnumed')):
	real_dir = os.path.join(local_python_base_dir, 'server')
	is_useful_import_dir = (
		os.path.exists(os.path.join(real_dir, 'pycommon'))
			and
		os.path.exists(os.path.join(real_dir, '__init__.py'))
	)
	if not is_useful_import_dir:
		real_dir = os.path.join(local_python_base_dir, 'client')			# CVS tree
	link_name = os.path.join(local_python_base_dir, 'Gnumed')
	print("Creating module import symlink ...")
	print(' real dir:', real_dir)
	print('     link:', link_name)
	os.symlink(real_dir, link_name)

#print("Adjusting PYTHONPATH ...")
sys.path.insert(0, local_python_base_dir)


# GNUmed imports
try:
	from Gnumed.pycommon import gmLog2
except ImportError:
	print("""Please make sure the GNUmed Python modules are in the Python path !""")
	raise

from Gnumed.pycommon import gmCfgINI
from Gnumed.pycommon import gmPsql
from Gnumed.pycommon import gmPG2
from Gnumed.pycommon import gmConnectionPool
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmI18N
from Gnumed.pycommon.gmExceptions import ConstructorError

# local imports
import gmAuditSchemaGenerator


_log = logging.getLogger('gm.bootstrapper')
#faulthandler.enable(file = gmLog2._logfile)
_cfg = gmCfgINI.gmCfgData()
_PG_CLUSTER = None
_interactive = None
_bootstrapped_dbs:dict[str, 'cDatabase'] = {}
_keep_temp_files = False
conn_ref_count = []

#==================================================================
pg_hba_sermon = """
I have found a connection to the database, but I am forbidden
to connect due to the settings in pg_hba.conf. This is a
PostgreSQL configuration file that controls who can connect
to the database.

Depending on your setup, it can be found in
/etc/postgresql/pg_hba.conf (Debian)
/usr/local/pgsql/pgdata/pg_hba.conf (FreeBSD, ?? Mac OS X)
FIXME: where do RedHat & friends put it
 or whichever directory your database files are located.

For gnumed, pg_hba.conf must allow password authentication.
For deveopment systems, I suggest the following

local    template1 postgres                             peer
local    gnumed    all                                  scram-sha-256
host     gnumed    all    127.0.0.1 255.255.255.255     scram-sha-256

For production systems, a different configuration will be
required, but gnumed is not production ready.
There is also a pg_hba.conf.example in this directory.

You must then restart (or SIGHUP) your PostgreSQL server.
"""

SQL_add_foreign_key = """
ALTER TABLE %(src_schema)s.%(src_tbl)s
	ADD FOREIGN KEY (%(src_col)s)
		REFERENCES %(target_schema)s.%(target_tbl)s(%(target_col)s)
		ON UPDATE CASCADE
		ON DELETE RESTRICT
;"""

SQL_add_index = """
-- idempotent:
DROP INDEX IF EXISTS %(idx_schema)s.%(idx_name)s CASCADE;

CREATE INDEX %(idx_name)s ON %(idx_schema)s.%(idx_table)s(%(idx_col)s);
"""

__MSG_create_gm_dbo = """The database owner [%s] must be created.

You will have to provide a new password for it.

MAKE SURE to remember the password for later use !
""" % _GM_DBO_ROLE

#==================================================================
def get_from_os_env(env_var:str, allow_empty:bool=False):
	_log.info('cecking OS environment for [%s]', env_var)
	val = os.getenv(env_var)
	if val is None:
		_log.debug('not set')
		return None

	_log.debug('[%s]: >>>%s<<<', env_var, val)
	if val.strip() != '':
		return val

	if allow_empty:
		_log.debug('empty env var allowed')
		return val

	return None

#==================================================================
def guesstimate_pg_superuser():
	"""Try to find the PG superuser.

	Typically, the PostgreSQL superuser is configured to
	connect via IDENT/TRUST/PEER which is why it is
	typically the same OS level user. Usually, the
	PostgreSQL server also runs as that OS level user.

	So, check /etc/passwd for candidates.

	In case that user does need a password to log in that
	needs to be set up using a .pgpass file or the
	PGPASSWORD environment variable.
	"""
	try:
		import pwd
	except ImportError:
		_log.warning("running on broken OS -- can't import pwd module")
		_log.info('falling back to "postgres" as PG demon user and PG superuser')
		return None

	global _PM_DEMON_USER
	global _PM_DEMON_UID
	global _PG_SUPERUSER
	pm_demon_user_passwd_line = None
	_PM_DEMON_USER = get_from_os_env(env_var = 'GM_POSTMASTER_DEMON_USER')
	if _PM_DEMON_USER is None:
		candidates = ['postgres', 'pgsql', 'postgresql']
	else:
		candidates = [_PM_DEMON_USER]
	for candidate in candidates:
		try:
			pm_demon_user_passwd_line = pwd.getpwnam(candidate)
			_PM_DEMON_USER = pm_demon_user_passwd_line[0]
			_PM_DEMON_UID = pm_demon_user_passwd_line[2]
			_log.debug('assuming PG demon user to be: %s [%s]', _PM_DEMON_USER, _PM_DEMON_UID)
			_PG_SUPERUSER = get_from_os_env(env_var = 'GM_CLUSTER_SUPERUSER')
			if _PG_SUPERUSER is None:
				_PG_SUPERUSER = _PM_DEMON_USER
			return

		except KeyError:
			_log.warning('cannot find user [%s] in passwd file', candidate)
			continue

	_PM_DEMON_USER = 'postgres'
	_PM_DEMON_UID = None
	_PG_SUPERUSER = get_from_os_env(env_var = 'GM_CLUSTER_SUPERUSER')
	if _PG_SUPERUSER is None:
		_PG_SUPERUSER = _PM_DEMON_USER

#-----------------------------------------------------------------
def become_postmaster_demon_user():
	"""Become "postgres" user.

	On UNIX type systems, attempt to use setuid() to
	become the postgres user if possible.

	This is so we can use the IDENT method to get to
	the database (NB by default, at least on Debian and
	postgres source installs, this is the only way,
	as the postgres user has no password [-- and TRUST
	is not allowed -KH])
	"""
	try:
		import pwd
	except ImportError:
		_log.warning("running on broken OS -- can't import pwd module")
		return None

	try:
		running_as_user = pwd.getpwuid(os.getuid())[0]
		_log.info('running as user [%s]' % running_as_user)
	except:
		running_as_user = None
	if os.getuid() == 0: # we are the super-user
		_log.info('switching to UNIX user "%s" [%s]', _PM_DEMON_USER, _PM_DEMON_UID)
		os.setuid(_PM_DEMON_UID)
	elif running_as_user == _PM_DEMON_USER: # we are the postgres user already
		_log.info('I already am the UNIX user "%s" [%s]', _PM_DEMON_USER, _PM_DEMON_UID)
	else:
		_log.warning('not running as root or postgres, cannot become postmaster demon user')
		_log.warning('may have trouble connecting as gm-dbo if IDENT/PEER auth is forced upon us')
		if _interactive:
			print_msg("WARNING: This script may not work if not running as the system administrator.")

#==================================================================
def connect(host:str=None, port:int=5432, db:str=None, user:str=None, conn_name:str=None):
	_log.info("trying DB connection to <%s> on %s:%s as <%s>", db, host or 'localhost', port, user)
	_log.info('assuming passwordless login (IDENT/TRUST/PEER/.pgpass/PGPASSFILE/PGPASSWORD/...)')
	creds = gmConnectionPool.cPGCredentials()
	creds.database = db
	creds.host = host
	creds.port = port
	creds.user = user
	creds.password = ''
	pool = gmConnectionPool.gmConnectionPool()
	pool.credentials = creds
	conn = pool.get_connection (
		readonly = False,
		pooled = False,
		verbose = True,
		connection_name = conn_name
	)
	conn_ref_count.append(conn)
	_log.info('successfully connected')
	return conn

#==================================================================
#==================================================================
#==================================================================
def get_gm_dbo_password() -> str:
	_log.info('getting password for [%s] from user', _GM_DBO_ROLE)
	print("I need the password for the database user [%s]." % _GM_DBO_ROLE)
	password = getpass.getpass("Please type the password: ")
	_log.info('got password')
	pwd4check = None
	while pwd4check != password:
		_log.info('asking for password confirmation')
		pwd2 = getpass.getpass("Please retype the password: ")
		if pwd2 == password:
			break
		_log.error('password mismatch, asking again')
		print('Password mismatch. Try again or CTRL-C to abort.')
	return password

#==================================================================
#==================================================================
class cPostgresqlCluster:
	def __init__(self):
		_log.info('bootstrapping cluster')
		self.section = 'cluster'
		self.conn_superuser_at_maintenance_db = None
		self.hostname = None
		if not self.__bootstrap():
			raise ConstructorError("cPostgresqlCluster.__init__(): Cannot bootstrap db server.")

		_log.info('done bootstrapping cluster')

	#--------------------------------------------------------------
	def __bootstrap(self):
		# connect to server level maintenance database (typically template1 or template0)
		if not self.__connect_superuser_to_maintenance_db():
			_log.error("Cannot connect to cluster maintenance database.")
			return None

		# add users/groups
		if not self.__bootstrap_roles():
			_log.error("Cannot bootstrap database users.")
			return None

		self.conn_superuser_at_maintenance_db.close()
		return True

	#--------------------------------------------------------------
	def __connect_superuser_to_maintenance_db(self):
		_log.info("connecting to cluster maintenance database")

		self.hostname = get_from_os_env('GM_CLUSTER_HOSTNAME', allow_empty = True)
		if self.hostname is None:
			self.hostname = cfg_get(self.section, 'host name')
			if self.hostname is None:
				_log.error("Need to know the hostname.")
				return None

		self.port = get_from_os_env('GM_CLUSTER_PORT')
		if not self.port:
			self.port = cfg_get(self.section, 'port')
			if self.port is None:
				_log.error("Need to know the cluster port.")
				return None

		self.maintenance_db = get_from_os_env('GM_CLUSTER_MAINTENANCE_DB')
		if not self.maintenance_db:
			self.maintenance_db = cfg_get(self.section, 'maintenance database')
			if self.maintenance_db is None:
				_log.error("Need to know the maintenance database name.")
				return None

		if self.conn_superuser_at_maintenance_db is not None:
			if self.conn_superuser_at_maintenance_db.closed == 0:
				self.conn_superuser_at_maintenance_db.close()
		self.conn_superuser_at_maintenance_db = connect (
			host = self.hostname,
			port = self.port,
			db = self.maintenance_db,
			user = _PG_SUPERUSER,
			conn_name = 'pg superuser/root@server maintenance DB'
		)
		if self.conn_superuser_at_maintenance_db is None:
			_log.error('Cannot connect.')
			return None

		self.conn_superuser_at_maintenance_db.cookie = 'cPostgresqlCluster.__connect_superuser_to_maintenance_db'

		# verify encoding
		curs = self.conn_superuser_at_maintenance_db.cursor()
		curs.execute("select setting from pg_settings where name = 'lc_ctype'")
		data = curs.fetchall()
		if data:
			lc_ctype = data[0][0]
			_log.info('maintenance database LC_CTYPE is [%s]', lc_ctype)
		else:
			# PG16+: lc_ctype/lc_collate are per-database attrs, not GUCs
			curs.execute("SELECT datcollate, datctype FROM pg_database WHERE datname = current_database()")
			row = curs.fetchone()
			if not row:
				_log.error('Could not read datcollate/datctype for maintenance DB')
				return None

			lc_collate, lc_ctype = row
			_log.info('maintenance database LC_COLLATE is [%s]', lc_collate)
			_log.info('maintenance database LC_CTYPE   is [%s]', lc_ctype)

		lc_ctype = lc_ctype.lower()
		if lc_ctype in ['c', 'posix']:
			_log.warning('while this cluster setting allows to store databases')
			_log.warning('in any encoding as is it does not allow for locale')
			_log.warning('sorting etc, hence it is not recommended for use')
			_log.warning('(although it will, technically, work)')
		elif not (lc_ctype.endswith('.utf-8') or lc_ctype.endswith('.utf8')):
			_log.error('LC_CTYPE does not end in .UTF-8 or .UTF8')
			curs.execute("show server_encoding")
			data = curs.fetchall()
			srv_enc = data[0][0]
			_log.info('server_encoding is [%s]', srv_enc)
			srv_enc = srv_enc.lower()
			if not srv_enc in ['utf8', 'utf-8']:
				_log.error('cluster encoding incompatible with utf8 encoded databases but')
				_log.error('for GNUmed installation the cluster must accept this encoding')
				_log.error('you may need to re-initdb or create a new cluster')
				return None
			_log.info('server encoding seems compatible despite not being reported in LC_CTYPE')

		# make sure we get english messages
		curs.execute("set lc_messages to 'C'")
		curs.close()

		_log.info("successfully connected to maintenance database [%s]" % self.maintenance_db)
		return True

	#--------------------------------------------------------------
	# user and group related
	#--------------------------------------------------------------
	def __bootstrap_roles(self):
		print_msg("==> ensuring standard database roles ...")
		_log.info("bootstrapping database roles")
		if not self.__create_groups():
			_log.error("Cannot create GNUmed standard groups roles.")
			return None

		if self.__create_gm_dbo() is None:
			_log.error("Cannot install GNUmed database owner.")
			return None

		return True

	#--------------------------------------------------------------
	def __create_groups(self):
		section = "GnuMed defaults"
		groups = cfg_get(section, "groups")
		if groups is None:
			_log.error("Cannot load GNUmed group names from config file (section [%s])." % section)
			return True

		cursor = self.conn_superuser_at_maintenance_db.cursor()
		for group in groups:
			if not gmPG2.create_group_role(group_role = group, link_obj = cursor):
				cursor.close()
				return False

		self.conn_superuser_at_maintenance_db.commit()
		cursor.close()
		return True

	#--------------------------------------------------------------
	def __create_gm_dbo(self):
		if not gmPG2.user_role_exists(user_role = _GM_DBO_ROLE, link_obj = self.conn_superuser_at_maintenance_db):
			print_msg(__MSG_create_gm_dbo)
			_gm_dbo_pwd = get_gm_dbo_password()
			if not gmPG2.create_user_role(user_role = _GM_DBO_ROLE, password = _gm_dbo_pwd, link_obj = self.conn_superuser_at_maintenance_db):
				return False

		SQL = (
			'GRANT "%s" TO "%s";'						# postgres in gm-logins (pg_dump/restore)
			'GRANT "%s" TO "%s" WITH ADMIN OPTION;'		# gm-dbo in gm-logins; in v17 add: ", INHERIT FALSE, SET FALSE"
			'ALTER ROLE "%s" CREATEDB CREATEROLE;'
		) % (
			_GM_LOGINS_GROUP, _PG_SUPERUSER,
			_GM_LOGINS_GROUP, _GM_DBO_ROLE,
			_GM_DBO_ROLE
		)
		cursor = self.conn_superuser_at_maintenance_db.cursor()
		try:
			cursor.execute(SQL)
		except:
			_log.error(">>>[%s]<<< failed." % SQL)
			_log.exception("Cannot add GNUmed database owner [%s] to group [%s]." % (_GM_DBO_ROLE, _GM_LOGINS_GROUP))
			cursor.close()
			return False

		cursor.close()
		self.conn_superuser_at_maintenance_db.commit()
		return True

#==================================================================
class cDatabase:
	def __init__(self, aDB_alias):
		_log.info("bootstrapping database [%s]" % aDB_alias)
		self.section = "database %s" % aDB_alias
		self.target_db_name = cfg_get(self.section, 'name')
		if self.target_db_name is None or str(self.target_db_name).strip() == '':
			_log.error("Need to know database name.")
			raise ConstructorError("database.__init__(): Cannot bootstrap database.")

		# already bootstrapped ?
		global _bootstrapped_dbs
		if aDB_alias in _bootstrapped_dbs:
			if _bootstrapped_dbs[aDB_alias].target_db_name == self.target_db_name:
				_log.info("database [%s] already bootstrapped", self.target_db_name)
				return None

		# no, so bootstrap from scratch
		_log.info('bootstrapping database [%s] alias "%s"', self.target_db_name, aDB_alias)

		for db in _bootstrapped_dbs.values():
			if db.conn.closed == 0:
				db.conn.close()
		_bootstrapped_dbs = {}
		self.conn = None

		self.source_db_name = cfg_get(self.section, 'source database')
		if self.source_db_name is None:
			_log.error("Source database name missing.")
			raise ConstructorError("database.__init__(): Cannot bootstrap database.")

		if not self.__bootstrap():
			raise ConstructorError("database.__init__(): Cannot bootstrap database.")

		_bootstrapped_dbs[aDB_alias] = self

		return None

	#--------------------------------------------------------------
	def __bootstrap(self):

		# connect as superuser to source DB
		if not self.__connect_pg_superuser_to_source_db():
			_log.error("Cannot connect to source database.")
			return False

		# fingerprint source db (previous GNUmed version)
		try:
			gmLog2.log_multiline (
				logging.INFO,
				message = 'source database fingerprint',
				text = gmPG2.get_db_fingerprint(conn = self.conn, eol = '\n')
			)
		except Exception:
			_log.exception('cannot fingerprint source database')

		self.conn.rollback()

		if not self.__create_target_db():
			_log.error("Cannot create database.")
			return False

		if not self.__connect_pg_superuser_to_target_db():
			_log.error("Cannot connect to database.")
			return None

		_log.info('creating database-specific authentication group role "%s"', self.target_db_name)
		created_group = gmPG2.create_group_role (
			group_role = self.target_db_name,
			admin_role = _GM_DBO_ROLE,
			link_obj = self.conn
		)
		if not created_group:
			self.conn.rollback()
			_log.error('cannot create authentication group role')
			return False

		self.conn.commit()

		# reindex db so upgrade doesn't fail on broken index
		llap = []
		reindexed = self.reindex_all()
		llap.append(reindexed)
		if not reindexed:
			_log.error('cannot REINDEX cloned target database')
			return False

		revalidated = self.revalidate_constraints()
		llap.append(revalidated)
		if not revalidated:
			_log.error('cannot VALIDATE CONSTRAINTs in cloned target database')
			return False

		if not self.validate_collations(use_the_source_luke = llap):
			_log.error('cannot validate collations in cloned target database')
			return False

		tmp = cfg_get(self.section, 'superuser schema')
		if tmp is not None:
			if not _import_schema(group=self.section, schema_opt='superuser schema', conn=self.conn):
				_log.error("cannot import schema definition for database [%s]" % (self.target_db_name))
				return False
		del tmp

		# transfer users
		if not self.transfer_users():
			_log.error("Cannot transfer users from old to new database.")
			return False

		# reconnect as owner to db
		if not self.__connect_owner_to_gm_db():
			_log.error("Cannot connect to database.")
			return None

		if not _import_schema(group=self.section, schema_opt='schema', conn=self.conn):
			_log.error("cannot import schema definition for database [%s]" % (self.target_db_name))
			return None

		# don't close this here, the  connection will
		# be reused later by check_data*/import_data etc.
		#self.conn.close()

		return True

	#--------------------------------------------------------------
	def __connect_pg_superuser_to_source_db(self):
		if self.conn is not None:
			if self.conn.closed == 0:
				self.conn.close()

		self.conn = connect (
			host = _PG_CLUSTER.hostname,
			port = _PG_CLUSTER.port,
			db = self.source_db_name,
			user = _PG_SUPERUSER,
			conn_name = 'postgres@old_gnumed_db'
		)
		self.conn.cookie = 'database.__connect_pg_superuser_to_source_db'
		curs = self.conn.cursor()
		curs.execute("set lc_messages to 'C'")
		curs.close()
		return self.conn and 1

	#--------------------------------------------------------------
	def __connect_pg_superuser_to_target_db(self):
		if self.conn is not None:
			if self.conn.closed == 0:
				self.conn.close()

		self.conn = connect (
			host = _PG_CLUSTER.hostname,
			port = _PG_CLUSTER.port,
			db = self.target_db_name,
			user = _PG_SUPERUSER,
			conn_name = 'postgres@gnumed_vX'
		)

		self.conn.cookie = 'database.__connect_pg_superuser_to_target_db'

		curs = self.conn.cursor()
		curs.execute('set default_transaction_read_only to off')
		# we need English messages to detect errors
		curs.execute("set lc_messages to 'C'")
		curs.execute("alter database %s set lc_messages to 'C'" % self.target_db_name)
		# we want READ ONLY default transactions for maximum patient data safety
		curs.execute("alter database %s set default_transaction_read_only to on" % self.target_db_name)
		# we want checking of function bodies
		curs.execute("alter database %s set check_function_bodies to on" % self.target_db_name)
		# we want checking of data checksums if available
		curs.execute("alter database %s set ignore_checksum_failure to off" % self.target_db_name)
		# tighten permissions on schema public
		curs.execute("revoke create on schema public from public")
		curs.close()
		self.conn.commit()

		# we need inheritance or else things will fail miserably but:
		# default now ON and PG10.0 hardwired to ON
		# so remove database specific setting
		curs = self.conn.cursor()
		try:
			curs.execute("alter database %s set sql_inheritance to DEFAULT" % self.target_db_name)
		except:
			_log.exception('PostgreSQL 10 onwards: <sql_inheritance> hardwired')
		curs.close()
		self.conn.commit()

		# we want to track commit timestamps if available
		# remove exception handler when 9.5 is default
		curs = self.conn.cursor()
		try:
			curs.execute("alter database %s set track_commit_timestamp to on" % self.target_db_name)
		except:
			_log.exception('PostgreSQL version < 9.5 does not support <track_commit_timestamp> OR <track_commit_timestamp> cannot be set at runtime')
		curs.close()
		self.conn.commit()

		# set owner of schema public to new role "pg_database_owner",
		# as suggested by PG 15 release notes
		curs = self.conn.cursor()
		try:
			curs.execute("alter schema public owner to pg_database_owner")
		except:
			_log.exception('PostgreSQL versions < 15 do not yet support role <pg_database_owner>')
		curs.close()
		self.conn.commit()

		curs = self.conn.cursor()
		gmConnectionPool.log_pg_settings(curs = curs)
		curs.close()
		self.conn.commit()

		return self.conn and 1

	#--------------------------------------------------------------
	def __connect_owner_to_gm_db(self):

		_log.debug('__connect_owner_to_gm_db')
		# reconnect as superuser to db
		if not self.__connect_pg_superuser_to_target_db():
			_log.error("Cannot connect to database.")
			return False

		self.conn.cookie = 'database.__connect_owner_to_gm_db via database.__connect_pg_superuser_to_target_db'
		_log.debug('setting session authorization to user [%s]', _GM_DBO_ROLE)
		curs = self.conn.cursor()
		SQL = "SET SESSION AUTHORIZATION %(usr)s"
		curs.execute(SQL, {'usr': _GM_DBO_ROLE})
		curs.close()
		return self.conn and 1

	#--------------------------------------------------------------
	def __create_target_db(self):
		_log.info('creating database')
		# verify source database hash
		source_db_version = cfg_get(self.section, 'source version')
		if source_db_version is None:
			_log.warning('cannot check source database identity hash, no version specified')
		else:
			converted, version = gmTools.input2int(source_db_version.lstrip('v'), 0)
			if not converted:
				_log.error('invalid source database definition: %s', source_db_version)
				return False

			if not gmPG2.database_schema_compatible(link_obj = self.conn, version = version):
				_log.error('invalid [%s] schema structure in GNUmed source database [%s]', source_db_version, self.source_db_name)
				return False

		# check for target database
		if gmPG2.database_exists(link_obj = self.conn, database = self.target_db_name):
			drop_existing = bool(int(cfg_get(self.section, 'drop target database')))
			if drop_existing:
				print_msg("==> dropping pre-existing target database [%s] ..." % self.target_db_name)
				_log.info('trying to drop target database')
				SQL = 'DROP DATABASE "%s"' % self.target_db_name
				# DROP DATABASE must be run outside transactions
				self.conn.commit()
				self.conn.set_session(readonly = False, autocommit = True)
				cursor = self.conn.cursor()
				try:
					_log.debug('running SQL: %s', SQL)
					cursor.execute(SQL)
				except:
					_log.exception(">>>[%s]<<< failed" % SQL)
					_log.debug('conn state after failed DROP: %s', gmConnectionPool.log_conn_state(self.conn))
					return False

				finally:
					cursor.close()
					self.conn.set_session(readonly = False, autocommit = False)
			else:
				use_existing = bool(int(cfg_get(self.section, 'use existing target database')))
				if use_existing:
					# FIXME: verify that database is owned by "gm-dbo"
					print_msg("==> using pre-existing target database [%s] ..." % self.target_db_name)
					_log.info('using existing database [%s]', self.target_db_name)
					return True

				else:
					_log.info('not using existing database [%s]', self.target_db_name)
					return False

		tablespace = cfg_get(self.section, 'tablespace')
		# locale_provider = builtin
		# locale = "C.UTF-8" "pg_unicode_fast"
		# builtin_locale = "C.UTF-8" "pg_unicode_fast"
		if tablespace is None:
			create_db_SQL = """
				CREATE DATABASE \"%s\" with
					owner = '%s'
					template = \"%s\"
					encoding = 'unicode'
				;""" % (self.target_db_name, _GM_DBO_ROLE, self.source_db_name)
		else:
			create_db_SQL = """
				CREATE DATABASE \"%s\" with
					owner = '%s'
					template = \"%s\"
					encoding = 'unicode'
					tablespace = '%s'
				;""" % (self.target_db_name, _GM_DBO_ROLE, self.source_db_name, tablespace)

		# get size
		cursor = self.conn.cursor()
		size_SQL = "SELECT pg_size_pretty(pg_database_size('%s'))" % self.source_db_name
		cursor.execute(size_SQL)
		size = cursor.fetchone()[0]
		cursor.close()

		# create database by cloning
		print_msg("==> [%s]: cloning (%s) as target database [%s] ..." % (self.source_db_name, size, self.target_db_name))
		# CREATE DATABASE must be run outside transactions
		self.conn.commit()
		self.conn.set_session(readonly = False, autocommit = True)
		cursor = self.conn.cursor()
		try:
			cursor.execute(create_db_SQL)
		except:
			_log.exception(">>>[%s]<<< failed" % create_db_SQL)
			return False

		finally:
			cursor.close()
			self.conn.set_session(readonly = False, autocommit = False)
		if not gmPG2.database_exists(link_obj = self.conn, database = self.target_db_name):
			return None

		_log.info("Successfully created GNUmed database [%s]." % self.target_db_name)
		return True

	#--------------------------------------------------------------
	def check_data_plausibility(self):

		print_msg("==> [%s]: checking migrated data for plausibility ..." % self.target_db_name)

		plausibility_queries = cfg_get(self.section, 'upgrade plausibility checks')
		if plausibility_queries is None:
			_log.warning('no plausibility checks defined')
			print_msg("    ... skipped (no checks defined)")
			return True

		# sanity check
		actual_queries = [ q for q in plausibility_queries if not q.startswith('--') ]
		no_of_queries, remainder = divmod(len(actual_queries), 2)
		if remainder != 0:
			_log.error('odd number of plausibility queries defined, aborting')
			print_msg("    ... failed (configuration error)")
			return False

		source_db_conn = connect (
			host = _PG_CLUSTER.hostname,
			port = _PG_CLUSTER.port,
			db = self.source_db_name,
			user = _PG_SUPERUSER,
		)
		source_db_conn.cookie = 'check_data_plausibility: source'

		target_conn = connect (
			host = _PG_CLUSTER.hostname,
			port = _PG_CLUSTER.port,
			db = self.target_db_name,
			user = _PG_SUPERUSER,
		)
		target_conn.cookie = 'check_data_plausibility: target'

		all_tests_successful = True
		def_of_check = None
		SQL__old_db = None
		SQL__new_db = None
		for line in plausibility_queries:
			if line.startswith('--'):
				_log.debug(line)
				continue
			# have we found a *first-of-two* non-'--' line ?
			if not def_of_check:
				def_of_check = line
				continue
			# we have found a second non-'--' line
			SQL__new_db = line
			tag_of_check = '?'
			try:
				tag_of_check, SQL__old_db = def_of_check.split('::::')
			except:
				_log.exception('error in plausibility check, aborting')
				_log.erorr('old DB: [%s]', def_of_check)
				_log.error('new DB: [%s]', SQL__new_db)
				print_msg("    ... failed (check definition error)")
				all_tests_successful = False
				def_of_check = None
				continue
			# run checks in old/new DB
			try:
				rows = gmPG2.run_ro_queries (link_obj = source_db_conn, queries = [{'sql': SQL__old_db}])
				val_in_old_db = rows[0][0]
			except:
				_log.exception('error in plausibility check [%s] (old DB), aborting' % tag_of_check)
				_log.error('SQL: %s', SQL__old_db)
				print_msg("    ... failed (SQL error)")
				all_tests_successful = False
				def_of_check = None
				continue
			try:
				rows = gmPG2.run_ro_queries(link_obj = target_conn,	queries = [{'sql': SQL__new_db}])
				val_in_new_db = rows[0][0]
			except:
				_log.exception('error in plausibility check [%s] (new DB), aborting' % tag_of_check)
				_log.error('SQL: %s', SQL__new_db)
				print_msg("    ... failed (SQL error)")
				all_tests_successful = False
				def_of_check = None
				continue
			# evaluate
			if val_in_new_db != val_in_old_db:
				_log.error('plausibility check [%s] failed, expected: [%s] (from old DB), found: [%s] (in new DB)', tag_of_check, val_in_old_db, val_in_new_db)
				_log.error('SQL (old DB): %s', SQL__old_db)
				_log.error('SQL (new DB): %s', SQL__new_db)
				print_msg("    ... failed (data error, check [%s])" % tag_of_check)
				all_tests_successful = False
				def_of_check = None
				continue
			def_of_check = None
			_log.info('plausibility check [%s] succeeded' % tag_of_check)

		source_db_conn.close()
		target_conn.close()

		return all_tests_successful

	#--------------------------------------------------------------
	def check_holy_auth_line(self):

		holy_pattern = 'local.*samerole.*\+gm-logins'
		holy_pattern_inactive = '#\s*local.*samerole.*\+gm-logins'

		conn = connect (
			host = _PG_CLUSTER.hostname,
			port = _PG_CLUSTER.port,
			db = self.target_db_name,
			user = _PG_SUPERUSER,
		)
		conn.cookie = 'holy auth check connection'

		cmd = "select setting from pg_settings where name = 'hba_file'"
		rows = gmPG2.run_ro_queries(link_obj = conn, queries = [{'sql': cmd}])
		conn.close()
		if len(rows) == 0:
			_log.info('cannot check pg_hba.conf for authentication information - not detectable in pg_settings')
			return

		hba_file = rows[0][0]
		_log.info('hba file: %s', hba_file)

		try:
			open(hba_file, mode = 'rt').close()
		except Exception:
			_log.exception('cannot check pg_hba.conf for authentication information - not readable')
			return

		found_holy_line = False
		for line in fileinput.input(hba_file):
			if regex.match(holy_pattern, line) is not None:
				found_holy_line = True
				_log.info('found standard GNUmed authentication directive in pg_hba.conf')
				_log.info('[%s]', line)
				_log.info('it may still be in the wrong place, though, so double-check if clients cannot connect')
				break

		if not found_holy_line:
			_log.info('did not find active standard GNUmed authentication directive in pg_hba.conf')
			_log.info('regex: %s' % holy_pattern)

			found_holy_line_inactive = False
			for line in fileinput.input(hba_file):
				if regex.match(holy_pattern_inactive, line) is not None:
					found_holy_line_inactive = True
					_log.info('found inactive standard GNUmed authentication directive in pg_hba.conf')
					_log.info('[%s]', line)
					_log.info('it may still be in the wrong place, though, so double-check if clients cannot connect')
					break
			if not found_holy_line_inactive:
				_log.info('did not find inactive standard GNUmed authentication directive in pg_hba.conf either')
				_log.info('regex: %s' % holy_pattern_inactive)

			_log.info('bootstrapping is likely to have succeeded but clients probably cannot connect yet')
			print_msg('==> sanity checking PostgreSQL authentication settings ...')
			print_msg('')
			print_msg('Note that even after successfully bootstrapping the GNUmed ')
			print_msg('database PostgreSQL may still need to be configured to')
			print_msg('allow GNUmed clients to connect to it.')
			print_msg('')
			print_msg('In many standard PostgreSQL installations this amounts to')
			print_msg('adding (or uncommenting) the authentication directive:')
			print_msg('')
			print_msg('  "local   samerole    +gm-logins   scram-sha-256"')
			print_msg('')
			print_msg('in the proper place of the file:')
			print_msg('')
			print_msg('  %s' % hba_file)
			print_msg('')
			print_msg('For details refer to the GNUmed documentation at:')
			print_msg('')
			print_msg('  https://www.gnumed.de/bin/view/Gnumed/ConfigurePostgreSQL')
			print_msg('')

	#--------------------------------------------------------------
	def import_data(self):

		print_msg("==> [%s]: upgrading reference data sets ..." % self.target_db_name)

		import_scripts = cfg_get(self.section, "data import scripts")
		if (import_scripts is None) or (len(import_scripts) == 0):
			_log.info('skipped data import: no scripts to run')
			print_msg("    ... skipped (no scripts to run)")
			return True

		script_base_dir = cfg_get(self.section, "script base directory")
		script_base_dir = os.path.expanduser(script_base_dir)
		# doesn't work on MacOSX:
		#script_base_dir = os.path.abspath(os.path.expanduser(script_base_dir))
		script_base_dir = os.path.normcase(os.path.normpath(os.path.join('.', script_base_dir)))

		for import_script in import_scripts:
			try:
				script = gmTools.import_module_from_directory(module_path = script_base_dir, module_name = import_script, always_remove_path = True)
			except ImportError:
				print_msg("    ... failed (cannot load script [%s])" % import_script)
				_log.error('cannot load data set import script [%s/%s]' % (script_base_dir, import_script))
				return False

			try:
				script.run(conn = self.conn)
			except:
				print_msg("    ... failed (cannot run script [%s])" % import_script)
				_log.exception('cannot run import script [%s]' % import_script)
				return False

			if import_script.endswith('.py'):
				import_script = import_script[:-3]
			import gc
			try:
				del sys.modules[import_script]
				del script
				gc.collect()
			except:
				_log.exception('cannot remove data import script module [%s], hoping for the best', import_script)

		return True

	#--------------------------------------------------------------
	def verify_result_hash(self):

		print_msg("==> [%s]: verifying target database schema ..." % self.target_db_name)

		target_version = cfg_get(self.section, 'target version')
		if target_version == 'devel':
			print_msg("    ... skipped (devel version)")
			_log.info('result schema hash: %s', gmPG2.get_schema_hash(link_obj = self.conn))
			_log.warning('testing/development only, not failing due to invalid target database identity hash')
			return True
		converted, version = gmTools.input2int(target_version.lstrip('v'), 2)
		if not converted:
			_log.error('cannot convert target database version: %s', target_version)
			print_msg("    ... failed (invalid target version specification)")
			return False
		if gmPG2.database_schema_compatible(link_obj = self.conn, version = version):
			_log.info('database identity hash properly verified')
			return True
		_log.error('target database identity hash invalid')
		print_msg("    ... failed (hash mismatch)")
		return False

	#--------------------------------------------------------------
	def reindex_all(self):
		print_msg("==> [%s]: reindexing target database (can take a while) ..." % self.target_db_name)
		do_reindex = cfg_get(self.section, 'reindex')
		if do_reindex is None:
			do_reindex = True
		else:
			do_reindex = (int(do_reindex) == 1)
		if not do_reindex:
			_log.warning('skipping REINDEXing')
			print_msg("    ... skipped")
			return True

		_log.info('REINDEXing cloned target database so upgrade does not fail in case of a broken index')
		_log.info('this may potentially take "quite a long time" depending on how much data there is in the database')
		_log.info('you may want to monitor the PostgreSQL log for signs of progress')
		reindexed = gmPG2.reindex_database(conn = self.conn)
		if not reindexed:
			print_msg('    ... failed')
			_log.error('REINDEXing database failed')
			return False

		return reindexed

	#--------------------------------------------------------------
	def revalidate_constraints(self):

		print_msg("==> [%s]: revalidating constraints in target database (can take a while) ..." % self.target_db_name)

		do_revalidate = cfg_get(self.section, 'revalidate')
		if do_revalidate is None:
			do_revalidate = True		# default: do it
		else:
			do_revalidate = (int(do_revalidate) == 1)
		if not do_revalidate:
			_log.warning('skipping VALIDATE CONSTRAINT')
			print_msg('    ... skipped')
			return True

		_log.info('reVALIDATing CONSTRAINTs in cloned target database so upgrade does not fail due to broken data')
		_log.info('this may potentially take "quite a long time" depending on how much data there is in the database')
		_log.info('you may want to monitor the PostgreSQL log for signs of progress')
		try:
			revalidated = gmPG2.revalidate_constraints(link_obj = self.conn)
		except Exception:
			_log.exception('>>>[VALIDATE CONSTRAINT]<<< failed')
			return False

		if revalidated is None:
			_log.error('constraint validation function missing, DO MANUALLY')
			print_msg('    ... unavailable, DO MANUALLY')
			return '_\\//'

		return revalidated

	#--------------------------------------------------------------
	def validate_collations(self, use_the_source_luke):
		print_msg('==> [%s]: validating collations ...' % self.target_db_name)
		sane_pg_database_collation = gmPG2.sanity_check_database_default_collation_version(conn = self.conn)
		sane_pg_collations = gmPG2.sanity_check_collation_versions(conn = self.conn)
		if sane_pg_database_collation and sane_pg_collations:
			return True

		_log.debug('Kelvin: %s', use_the_source_luke)
		if not sane_pg_database_collation:
			if not gmPG2.refresh_database_default_collation_version_information(conn = self.conn, use_the_source_luke = use_the_source_luke):
				print_msg('    ... fixing database default collation failed')
				return False

		if not sane_pg_collations:
			refreshed = gmPG2.refresh_collations_version_information(conn = self.conn, use_the_source_luke = use_the_source_luke)
			if refreshed is False:
				print_msg('    ... fixing all other collations failed')
				return False

			if refreshed is None:
				_log.error('collations validation function missing, DO MANUALLY')
				print_msg('    ... unavailable, DO MANUALLY')
				return True

		return True

	#--------------------------------------------------------------
	def transfer_users(self) -> bool:
		print_msg("==> [%s]: transferring users ..." % self.target_db_name)
		do_user_transfer = cfg_get(self.section, 'transfer users')
		if do_user_transfer is None:
			_log.info('user transfer not defined')
			print_msg("    ... skipped (unconfigured)")
			return True

		do_user_transfer = int(do_user_transfer)
		if not do_user_transfer:
			_log.info('configured to not transfer users')
			print_msg("    ... skipped (disabled)")
			return True

		cmd = "select gm.transfer_users('%s'::text)" % self.source_db_name
		try:
			rows = gmPG2.run_rw_queries(link_obj = self.conn, queries = [{'sql': cmd}], end_tx = True, return_data = True)
		except gmPG2.dbapi.ProgrammingError:
			# maybe an old database
			_log.info('problem running gm.transfer_users(), trying gm_transfer_users()')
			cmd = "select gm_transfer_users('%s'::text)" % self.source_db_name
			rows = gmPG2.run_rw_queries(link_obj = self.conn, queries = [{'sql': cmd}], end_tx = True, return_data = True)
		if rows[0][0]:
			_log.info('users properly transferred from [%s] to [%s]' % (self.source_db_name, self.target_db_name))
			return True

		_log.error('error transferring user from [%s] to [%s]' % (self.source_db_name, self.target_db_name))
		print_msg("    ... failed")
		return False

	#--------------------------------------------------------------
	def ensure_some_security_settings(self) -> bool:
		print_msg("==> [%s]: setting up security settings ..." % self.target_db_name)
		SQL = 'REVOKE create ON SCHEMA public FROM public;'
		gmPG2.run_rw_queries(link_obj = self.conn, queries = [{'sql': SQL}])
		if gmPG2.function_exists(link_obj = self.conn, schema = 'gm', function = 'adjust_view_options'):
			SQL = 'SELECT gm.adjust_view_options();'
			gmPG2.run_rw_queries(link_obj = self.conn, queries = [{'sql': SQL}])
		else:
			print_msg('    ... skipped (unavailable as yet)')
		return True

	#--------------------------------------------------------------
	def setup_auditing(self) -> bool:
		print_msg("==> [%s]: setting up auditing ..." % self.target_db_name)
		# get audit trail configuration
		tmp = cfg_get(self.section, 'audit disable')
		# if this option is not given, assume we want auditing
		if tmp is not None:
			# if we don't want auditing on these tables, return without error
			if int(tmp) == 1:
				print_msg('    ... skipped (disabled)')
				return True

		# create auditing schema
		curs = self.conn.cursor()
		audit_schema = gmAuditSchemaGenerator.create_audit_ddl(curs)
		curs.close()
		if audit_schema is None:
			_log.error('cannot generate audit trail schema for GNUmed database [%s]' % self.target_db_name)
			return None

		# write schema to file
		tmpfile = os.path.join(tempfile.gettempdir(), 'audit-trail-schema.sql')
		f = open(tmpfile, mode = 'wt', encoding = 'utf8')
		for line in audit_schema:
			f.write('%s;\n' % line)
		f.close()
		# import auditing schema
		psql = gmPsql.Psql(self.conn)
		if psql.run(tmpfile) != 0:
			_log.error("cannot import audit schema definition for database [%s]" % (self.target_db_name))
			return None

		if _keep_temp_files:
			return True

		try:
			os.remove(tmpfile)
		except Exception:
			_log.exception('cannot remove audit trail schema file [%s]' % tmpfile)
		return True

	#--------------------------------------------------------------
	def setup_notifications(self):

		# setup clin.clin_root_item child tables FK's
		print_msg("==> [%s]: setting up encounter/episode FKs and IDXs ..." % self.target_db_name)
		child_tables = gmPG2.get_child_tables(link_obj = self.conn, schema = 'clin', table = 'clin_root_item')
		_log.info('clin.clin_root_item child tables:')
		for child in child_tables:
			_log.info('%s.%s', child['namespace'], child['table'])
		for child in child_tables:
			# .fk_episode
			FKs = gmPG2.get_foreign_key_names (
				link_obj = self.conn,
				src_schema = child['namespace'],
				src_table = child['table'],
				src_column = 'fk_episode',
				target_schema = 'clin',
				target_table = 'episode',
				target_column = 'pk',
			)
			if len(FKs) > 0:
				_log.info('%s FK(s) exist:', len(FKs))
				for idx in range(len(FKs)):
					FK = FKs[idx]
					_log.info(' #%s = %s.%s: %s.%s.%s -> %s.%s.%s', idx + 1, FK['constraint_schema'], FK['constraint_name'], FK['source_schema'], FK['source_table'], FK['source_column'], FK['target_schema'], FK['target_table'], FK['target_column'])
			else:
				_log.info('adding FK: %s.%s.fk_episode -> clin.episode.pk', child['namespace'], child['table'])
				cmd = SQL_add_foreign_key % {
					'src_schema': child['namespace'],
					'src_tbl': child['table'],
					'src_col': 'fk_episode',
					'target_schema': 'clin',
					'target_tbl': 'episode',
					'target_col': 'pk'
				}
				gmPG2.run_rw_queries(link_obj = self.conn, queries = [{'sql': cmd}])
			# index on .fk_episode
			idx_defs = gmPG2.get_index_name(indexed_table = '%s.%s' % (child['namespace'], child['table']), indexed_column = 'fk_episode', link_obj = self.conn)
			# drop any existing
			for idx_def in idx_defs:
				_log.info('dropping index %s.%s', idx_def['index_schema'], idx_def['index_name'])
				cmd = 'DROP INDEX IF EXISTS %s.%s CASCADE' % (idx_def['index_schema'], idx_def['index_name'])
				gmPG2.run_rw_queries(link_obj = self.conn, queries = [{'sql': cmd}])
			# create
			_log.info('creating index idx_%s_%s_fk_episode', child['namespace'], child['table'])
			cmd = SQL_add_index % {
				'idx_schema': child['namespace'],
				'idx_name': 'idx_%s_%s_fk_episode' % (child['namespace'], child['table']),
				'idx_table': child['table'],
				'idx_col': 'fk_episode'
			}
			gmPG2.run_rw_queries(link_obj = self.conn, queries = [{'sql': cmd}])

			# .fk_encounter
			FKs = gmPG2.get_foreign_key_names (
				link_obj = self.conn,
				src_schema = child['namespace'],
				src_table = child['table'],
				src_column = 'fk_encounter',
				target_schema = 'clin',
				target_table = 'encounter',
				target_column = 'pk'
			)
			if len(FKs) > 0:
				_log.info('%s FK(s) exist:', len(FKs))
				for idx in range(len(FKs)):
					FK = FKs[idx]
					_log.info(' #%s = %s.%s: %s.%s.%s -> %s.%s.%s', idx + 1, FK['constraint_schema'], FK['constraint_name'], FK['source_schema'], FK['source_table'], FK['source_column'], FK['target_schema'], FK['target_table'], FK['target_column'])
			else:
				_log.info('adding FK: %s.%s.fk_encounter -> clin.encounter.pk', child['namespace'], child['table'])
				cmd = SQL_add_foreign_key % {
					'src_schema': child['namespace'],
					'src_tbl': child['table'],
					'src_col': 'fk_encounter',
					'target_schema': 'clin',
					'target_tbl': 'encounter',
					'target_col': 'pk'
				}
				gmPG2.run_rw_queries(link_obj = self.conn, queries = [{'sql': cmd}])
			# index on .fk_encounter
			idx_defs = gmPG2.get_index_name(indexed_table = '%s.%s' % (child['namespace'], child['table']), indexed_column = 'fk_encounter', link_obj = self.conn)
			# drop any existing
			for idx_def in idx_defs:
				_log.info('dropping index %s.%s', idx_def['index_schema'], idx_def['index_name'])
				cmd = 'DROP INDEX IF EXISTS %s.%s CASCADE' % (idx_def['index_schema'], idx_def['index_name'])
				gmPG2.run_rw_queries(link_obj = self.conn, queries = [{'sql': cmd}])
			# create
			_log.info('creating index idx_%s_%s_fk_encounter', child['namespace'], child['table'])
			cmd = SQL_add_index % {
				'idx_schema': child['namespace'],
				'idx_name': 'idx_%s_%s_fk_encounter' % (child['namespace'], child['table']),
				'idx_table': child['table'],
				'idx_col': 'fk_encounter'
			}
			gmPG2.run_rw_queries(link_obj = self.conn, queries = [{'sql': cmd}])

		curs = self.conn.cursor()

		# re-create fk_encounter/fk_episode sanity check triggers on all tables
		if gmPG2.function_exists(link_obj = curs, schema = 'gm', function = 'create_all_enc_epi_sanity_check_triggers'):
			print_msg("==> [%s]: setting up encounter/episode FK sanity check triggers ..." % self.target_db_name)
			_log.debug('attempting to set up sanity check triggers on all tables linking to encounter AND episode')
			cmd = 'select gm.create_all_enc_epi_sanity_check_triggers()'
			curs.execute(cmd)
			result = curs.fetchone()
			if result[0] is False:
				_log.error('error creating sanity check triggers on all tables linking to clin.encounter AND clin.episode')
				curs.close()
				return None

		# always re-create generic super signal (if exists)
		if gmPG2.function_exists(link_obj = curs, schema = 'gm', function = 'create_all_table_mod_triggers'):
			print_msg("==> [%s]: setting up generic notifications ..." % self.target_db_name)
			_log.debug('attempting to create generic modification announcement triggers on all registered tables')

			cmd = "SELECT gm.create_all_table_mod_triggers(True::boolean)"
			curs.execute(cmd)
			result = curs.fetchone()
			curs.close()
			if result[0] is False:
				_log.error('cannot create generic modification announcement triggers on all tables')
				return None

		self.conn.commit()
		return True

#==================================================================
class gmBundle:
	def __init__(self, aBundleAlias = None):
		# sanity check
		if aBundleAlias is None:
			raise ConstructorError("Need to know bundle name to install it.")

		self.alias = aBundleAlias
		self.section = "bundle %s" % aBundleAlias
	#--------------------------------------------------------------
	def bootstrap(self):
		_log.info("bootstrapping bundle [%s]" % self.alias)

		# load bundle definition
		database_alias = cfg_get(self.section, "database alias")
		if database_alias is None:
			_log.error("Need to know database name to install bundle [%s]." % self.alias)
			return None

		# bootstrap database
		try:
			cDatabase(aDB_alias = database_alias)
		except:
			_log.exception("Cannot bootstrap bundle [%s].", self.alias)
			return None

		self.db = _bootstrapped_dbs[database_alias]
		# check PostgreSQL version
		if not self.__verify_pg_version():
			_log.error("Wrong PostgreSQL version.")
			return None

		# import schema
		if not _import_schema(group=self.section, schema_opt='schema', conn=self.db.conn):
			_log.error("Cannot import schema definition for bundle [%s] into database [%s]." % (self.alias, database_alias))
			return None

		return True
	#--------------------------------------------------------------
	def __verify_pg_version(self):
		"""Verify database version information."""

		required_version = cfg_get(self.section, "minimum postgresql version")
		if required_version is None:
			_log.error("Cannot load minimum required PostgreSQL version from config file.")
			return None

		_log.info("minimum required PostgreSQL version: %s" % required_version)

		converted, pg_ver = gmTools.input2decimal(gmConnectionPool.postgresql_version)

		if not converted:
			_log.error('error checking PostgreSQL version')
			return None
		converted, req_version = gmTools.input2decimal(required_version)
		if not converted:
			_log.error('error checking PostgreSQL version')
			_log.error('required: %s', required_version)
			return None
		if pg_ver < req_version:
			_log.error("Reported live PostgreSQL version [%s] is smaller than the required minimum version [%s].", pg_ver, required_version)
			return None

		_log.info("installed PostgreSQL version: %s - this is fine with me", pg_ver)
		return True

#==================================================================
def bootstrap_bundles():
	# get bundle list
	bundles = cfg_get("installation", "bundles")
	if bundles is None:
		exit_with_msg("Bundle list empty. Nothing to do here.")

	# make sure cluster is bootstrapped
	global _PG_CLUSTER
	if not _PG_CLUSTER:
		_PG_CLUSTER = cPostgresqlCluster()
	# run through bundles
	for bundle_alias in bundles:
		print_msg('==> bootstrapping "%s" ...' % bundle_alias)
		bundle = gmBundle(bundle_alias)
		if not bundle.bootstrap():
			return None

	return True

#--------------------------------------------------------------
def import_data():
	for db_key in _bootstrapped_dbs.keys():
		db = _bootstrapped_dbs[db_key]
		if not db.import_data():
			return None
	return True

#--------------------------------------------------------------
def setup_auditing():
	"""Setting up auditing in all bootstrapped databases"""
	for db_key in _bootstrapped_dbs.keys():
		db = _bootstrapped_dbs[db_key]
		if not db.setup_auditing():
			return None
	return True

#--------------------------------------------------------------
def setup_notifications():
	"""Setting up notifications in all bootstrapped databases"""
	for db_key in _bootstrapped_dbs.keys():
		db = _bootstrapped_dbs[db_key]
		if not db.setup_notifications():
			return None
	return True

#--------------------------------------------------------------
def ensure_some_security_settings():
	"""Making sure some settings related to security are the way they should be."""
	for db_key in _bootstrapped_dbs.keys():
		db = _bootstrapped_dbs[db_key]
		if not db.ensure_some_security_settings():
			return None

	return True

#------------------------------------------------------------------
def _run_query(aCurs, aQuery, args=None):
	# FIXME: use gmPG2.run_rw_query()
	if args is None:
		try:
			aCurs.execute(aQuery)
		except:
			_log.exception(">>>%s<<< failed" % aQuery)
			return False
	else:
		try:
			aCurs.execute(aQuery, args)
		except:
			_log.exception(">>>%s<<< failed" % aQuery)
			_log.error(str(args))
			return False
	return True

#------------------------------------------------------------------
def ask_for_confirmation_to_proceed():
	bundles = cfg_get("installation", "bundles")
	if bundles is None:
		return True
	if len(bundles) == 0:
		return True

	if not _interactive:
		print_msg("You are about to install the following parts of GNUmed:")
		print_msg("-------------------------------------------------------")
		for bundle in bundles:
			db_alias = cfg_get("bundle %s" % bundle, "database alias")
			db_name = cfg_get("database %s" % db_alias, "name")
			srv_alias = cfg_get("database %s" % db_alias, "server alias")
			srv_name = cfg_get("server %s" % srv_alias, "name")
			print_msg('bundle "%s" in <%s> (or overridden) on <%s>' % (bundle, db_name, srv_name))
		print_msg("-------------------------------------------------------")
		desc = cfg_get("installation", "description")
		if desc is not None:
			for line in desc:
				print_msg(line)
		return True

	print("You are about to install the following parts of GNUmed:")
	print("-------------------------------------------------------")
	for bundle in bundles:
		db_alias = cfg_get("bundle %s" % bundle, "database alias")
		db_name = cfg_get("database %s" % db_alias, "name")
		srv_alias = cfg_get("database %s" % db_alias, "server alias")
		srv_name = cfg_get("server %s" % srv_alias, "name")
		print('bundle "%s" in <%s> (or overridden) on <%s>' % (bundle, db_name, srv_name))
	print("-------------------------------------------------------")
	desc = cfg_get("installation", "description")
	if desc is not None:
		for line in desc:
			print(line)

	print("Do you really want to install this database setup ?")
	answer = input("Type yes or no: ")
	if answer == "yes":
		return True
	return None

#--------------------------------------------------------------
def _import_schema (group=None, schema_opt="schema", conn=None):
	# load schema
	schema_files = cfg_get(group, schema_opt)
	if schema_files is None:
		_log.error("Need to know schema definition to install it.")
		return None

	schema_base_dir = cfg_get(group, "schema base directory")
	if schema_base_dir is None:
		_log.warning("no schema files base directory specified")
		# look for base dirs for schema files
		if os.path.exists (os.path.join ('.', 'sql')):
			schema_base_dir = '.'
		if os.path.exists ('../sql'):
			schema_base_dir = '..'
		if os.path.exists ('/usr/share/gnumed/server/sql'):
			schema_base_dir = '/usr/share/gnumed/server'
		if os.path.exists (os.path.expandvars('$GNUMED_DIR/server/sql')):
			schema_base_dir = os.path.expandvars('$GNUMED_DIR/server')

	# and import them
	psql = gmPsql.Psql(conn)
	for filename in schema_files:
		if filename.strip() == '':
			continue						# skip empty line
		if filename.startswith('# '):
			_log.info(filename)				# log as comment
			continue
		full_path = os.path.join(schema_base_dir, filename)
		if psql.run(full_path) == 0:
			#_log.info('success')
			continue
		_log.error('failure')
		return None

	return True

#------------------------------------------------------------------
def exit_with_msg(aMsg = None):
	if aMsg is not None:
		print(aMsg)
	print('')
	print("Please check the log file for details:")
	print('')
	print(' ', gmLog2._logfile_name)
	print('')
	_log.error(aMsg)
	_log.info('shutdown')
	sys.exit(1)

#------------------------------------------------------------------
def print_msg(msg=None):
	if quiet:
		return
	print(msg)

#==============================================================================
def cfg_get(group=None, option=None):
	return _cfg.get (
		group = group,
		option = option,
		source_order = [('file', 'return')]
	)

#==================================================================
def handle_cfg():
	"""Bootstrap the source 'file' in _cfg."""

	_log.info('config file: %s', _cfg.source_files['file'])

	global _interactive
	if _interactive is None:
		tmp = cfg_get("installation", "interactive")
		if tmp == "no":
			_interactive = False
		else:
			_interactive = True

	tmp = cfg_get('installation', 'keep temp files')
	if tmp == "yes":
		global _keep_temp_files
		_keep_temp_files = True
	if not ask_for_confirmation_to_proceed():
		exit_with_msg("Bootstrapping aborted by user.")

	if not bootstrap_bundles():
		exit_with_msg("Cannot bootstrap bundles.")

	if not setup_auditing():
		exit_with_msg("Cannot set up audit trail.")

	if not setup_notifications():
		exit_with_msg("Cannot set up notifications from tables.")

	if not ensure_some_security_settings():
		exit_with_msg("Cannot ensure security settings")

	if not import_data():
		exit_with_msg("Bootstrapping failed: unable to import data")

	# fingerprint target db
	# (the ugliest of hacks)
	db = None
	for db_key in _bootstrapped_dbs.keys():
		db = _bootstrapped_dbs[db_key]
	if db is not None:
		try:
			gmLog2.log_multiline (
				logging.INFO,
				message = 'target database fingerprint',
				text = gmPG2.get_db_fingerprint(conn = db.conn, eol = '\n')
			)
		except Exception:
			_log.error('cannot fingerprint database')
		finally:
			db.conn.rollback()
	return True

#==================================================================
#==================================================================
def main():

	_cfg.add_cli(long_options = ['conf-file=', 'log-file=', 'quiet'])

	global quiet
	quiet = bool(_cfg.get(option = '--quiet', source_order = [('cli', 'return')]))

	print_msg(",=========================================.")
	print_msg("* Bootstrapping GNUmed database system... *")
	print_msg("`========================================='")

	# get initial conf file from CLI
	cfg_file = _cfg.get(option = '--conf-file', source_order = [('cli', 'return')])
	if cfg_file is None:
		_log.error("no config file specified on command line")
		exit_with_msg('Cannot bootstrap without config file. Use --conf-file=<FILE>.')

	_log.info('primary config file: %s', cfg_file)
	_cfg.add_file_source(source = 'file', filename = cfg_file)
	# does it point to other conf files ?
	cfg_files = _cfg.get (
		group = 'installation',
		option = 'config files',
		source_order = [('file', 'return')]
	)
	if cfg_files is None:
		_log.info('single-shot config file')
		guesstimate_pg_superuser()
		become_postmaster_demon_user()
		handle_cfg()
	else:
		_log.info('aggregation of config files')
		tmp = cfg_get("installation", "interactive")
		global _interactive
		if tmp == "no":
			_interactive = False
		else:
			_interactive = True
		guesstimate_pg_superuser()
		become_postmaster_demon_user()
		for cfg_file in cfg_files:
			_cfg.add_file_source(source = 'file', filename = cfg_file)
			handle_cfg()

	global _bootstrapped_dbs
	db = next(iter(_bootstrapped_dbs.values()))
	if not db.verify_result_hash():
		exit_with_msg("Bootstrapping failed: wrong result hash")

	if not db.check_data_plausibility():
		exit_with_msg("Bootstrapping failed: plausibility checks inconsistent")

	db.check_holy_auth_line()
	_log.info("shutdown")
	print("Done bootstrapping GNUmed database: We very likely succeeded.")
	print('log:', gmLog2._logfile_name)

#==================================================================
#==================================================================
if __name__ != "__main__":
	print("This currently is not intended to be used as a module.")
	sys.exit(1)


gmI18N.activate_locale()

_log.info('startup')

try:
	main()
except Exception:
	_log.exception('unhandled exception caught, shutting down connections')
	exit_with_msg('Bootstrapping failed: unhandled exception occurred')
finally:
	for conn in conn_ref_count:
		if conn.closed == 0:
			_log.warning('open connection detected: %s', conn.cookie)
			_log.warning('%s', conn)
			_log.warning('closing connection')
			conn.close()

_log.info('after main, before sys.exit(0)')

sys.exit(0)


#==================================================================
#	pipe = popen2.Popen3(cmd, 1==1)
#	pipe.tochild.write("%s\n" % aPassword)
#	pipe.tochild.flush()
#	pipe.tochild.close()

#	result = pipe.wait()
#	print(result)

	# read any leftovers
#	pipe.fromchild.flush()
#	pipe.childerr.flush()
#	tmp = pipe.fromchild.read()
#	lines = tmp.split("\n")
#	for line in lines:
#		_log.debug("child stdout: [%s]" % line, gmLog.lCooked)
#	tmp = pipe.childerr.read()
#	lines = tmp.split("\n")
#	for line in lines:
#		_log.error("child stderr: [%s]" % line, gmLog.lCooked)

#	pipe.fromchild.close()
#	pipe.childerr.close()
#	del pipe

#==================================================================
