#!/usr/bin/python3

"""GNUmed schema installation.

This script bootstraps a GNUmed database system.

This will set up databases, tables, groups, permissions and
possibly users. Most of this will be handled via SQL
scripts, not directly in the bootstrapper itself.

There's a special user called "gm-dbo" who owns all the
database objects.

For all this to work you must be able to access the database
server as the standard "postgres" superuser.

This script does NOT set up user specific configuration options.

All definitions are loaded from a config file.

Please consult the User Manual in the GNUmed CVS for
further details.

--quiet
--log-file=
--conf-file=

Requires psycopg 2.7.4 !
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

# standard library
import sys
if sys.hexversion < 0x3000000:
	sys.exit('This code must be run with Python 3.')

import os.path
import fileinput
import os
import getpass
import glob
import re as regex
import tempfile
import io
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

print("Adjusting PYTHONPATH ...")
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
aud_gen = gmAuditSchemaGenerator


_log = logging.getLogger('gm.bootstrapper')
#faulthandler.enable(file = gmLog2._logfile)


_cfg = gmCfgINI.gmCfgData()


_interactive = None
_bootstrapped_servers = {}
_bootstrapped_dbs = {}
_dbowner = None
cached_host = None
cached_passwd = {}
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

local    template1 postgres                             ident sameuser
local    gnumed    all                                  md5
host     gnumed    all    127.0.0.1 255.255.255.255     md5

For production systems, a different configuration will be
required, but gnumed is not production ready.
There is also a pg_hba.conf.example in this directory.

You must then restart (or SIGHUP) your PostgreSQL server.
"""

no_server_sermon = """
I cannot find a PostgreSQL server running on this machine.

Try (as root):
/etc/init.d/postgresql start

if that fails, you can build a database from scratch:

PGDATA=some directory you can use
initdb
cp pg_hba.conf.example $PGDATA/pg_hba.conf
pg_ctl start 

if none of these commands work, or you don't know what PostgreSQL
is, go to the website to download for your OS at:

http://www.postgresql.org/

On the other hand, if you have a PostgreSQL server
running somewhere strange, type hostname[:port]
below, or press RETURN to quit.
"""

superuser_sermon = """
I can't log on as the PostgreSQL database owner.
Try running this script as the system administrator (user "root")
to get the necessary permissions.

NOTE: I expect the PostgreSQL database owner to be called "%s"
If for some reason it is not, you need to adjust my configuration
script, and run again as that user.
"""

no_clues = """
Logging on to the PostgreSQL database returned this error
%s
on %s

Please contact the GNUmed development team on gnumed-devel@gnu.org.
Make sure you include this error message in your mail.
"""

welcome_sermon = """
Welcome to the GNUmed server instllation script.

You must have a PostgreSQL server running and
administrator access.

Please select a database configuration from the list below.
"""

SQL_add_foreign_key = u"""
ALTER TABLE %(src_schema)s.%(src_tbl)s
	ADD FOREIGN KEY (%(src_col)s)
		REFERENCES %(target_schema)s.%(target_tbl)s(%(target_col)s)
		ON UPDATE CASCADE
		ON DELETE RESTRICT
;"""

SQL_add_index = u"""
-- idempotent:
DROP INDEX IF EXISTS %(idx_schema)s.%(idx_name)s CASCADE;

CREATE INDEX %(idx_name)s ON %(idx_schema)s.%(idx_table)s(%(idx_col)s);
"""


#==================================================================
def user_exists(cursor=None, user=None):
	cmd = "SELECT usename FROM pg_user WHERE usename = %(usr)s"
	args = {'usr': user}
	try:
		cursor.execute(cmd, args)
	except:
		_log.exception(u">>>[%s]<<< failed for user [%s]", cmd, user)
		return None
	res = cursor.fetchone()
	if cursor.rowcount == 1:
		_log.info(u"user [%s] exists", user)
		return True
	_log.info(u"user [%s] does not exist", user)
	return None
#------------------------------------------------------------------
def db_group_exists(cursor=None, group=None):
	cmd = 'SELECT groname FROM pg_group WHERE groname = %(grp)s'
	args = {'grp': group}
	try:
		cursor.execute(cmd, args)
	except:
		_log.exception(u">>>[%s]<<< failed for group [%s]", cmd, group)
		return False
	rows = cursor.fetchall()
	if len(rows) > 0:
		_log.info(u"group [%s] exists" % group)
		return True
	_log.info(u"group [%s] does not exist" % group)
	return False
#------------------------------------------------------------------
def create_db_group(cursor=None, group=None):

	# does this group already exist ?
	if db_group_exists(cursor, group):
		return True

	cmd = 'create group "%s"' % group
	try:
		cursor.execute(cmd)
	except:
		_log.exception(u">>>[%s]<<< failed for group [%s]", cmd, group)
		return False

	# paranoia is good
	if not db_group_exists(cursor, group):
		return False

	return True
#==================================================================
def connect(host, port, db, user, passwd, conn_name=None):
	"""
	This is a wrapper to the database connect function.
	Will try to recover gracefully from connection errors where possible
	"""
	global cached_host
	if len(host) == 0 or host == 'localhost':
		if cached_host:
			host, port = cached_host
		else:
			host = ''
	if passwd == 'blank' or passwd is None or len(passwd) == 0:
		if user in cached_passwd:
			passwd = cached_passwd[user]
		else:
			passwd = ''
	_log.info(u"trying DB connection to %s on %s as %s", db, host or 'localhost', user)
	creds = gmConnectionPool.cPGCredentials()
	creds.database = db
	creds.host = host
	creds.port = port
	creds.user = user
	creds.password = passwd
	pool = gmConnectionPool.gmConnectionPool()
	pool.credentials = creds
	conn = pool.get_connection(readonly=False, pooled=False, verbose=True, connection_name = conn_name)
	cached_host = (host, port) # learn from past successes
	cached_passwd[user] = passwd
	conn_ref_count.append(conn)
	_log.info(u'successfully connected')
	return conn

#==================================================================
class user:
	def __init__(self, anAlias = None, aPassword = None, force_interactive=False):
		if anAlias is None:
			raise ConstructorError("need user alias")
		self.alias = anAlias
		self.group = "user %s" % self.alias

		self.name = cfg_get(self.group, "name")
		if self.name is None:
			raise ConstructorError("cannot get user name")

		self.password = aPassword

		# password not passed in, try to get it from elsewhere
		if self.password is None:
			# look into config file
			self.password = cfg_get(self.group, "password")
			# undefined or commented out:
			# this means the user does not need a password
			# but connects via IDENT or TRUST
			if self.password is None:
				_log.info(u'password not defined, assuming connect via IDENT/TRUST')
			# defined but empty:
			# this means to ask the user if interactive
			elif self.password == '':
				if _interactive or force_interactive:
					_log.info('password for [%s] defined as "", asking user', self.name)
					print("I need the password for the database user [%s]." % self.name)
					self.password = getpass.getpass("Please type the password: ")
					_log.info('got password')
					pwd4check = None
					while pwd4check != self.password:
						_log.info('asking for confirmation')
						pwd2 = getpass.getpass("Please retype the password: ")
						if pwd2 == self.password:
							break
						_log.error('password mismatch, asking again')
						print('Password mismatch. Try again or CTRL-C to abort.')
				else:
					_log.warning('password for [%s] defined as "" (meaning <ask-user>), but running non-interactively, aborting', self.name)
					_log.warning('cannot get password for database user [%s]', self.name)
					raise ValueError('no password for user %s' % self.name)

		return None

#==================================================================
class db_server:
	def __init__(self, aSrv_alias, auth_group):
		_log.info(u"bootstrapping server [%s]" % aSrv_alias)

		global _bootstrapped_servers

		if aSrv_alias in _bootstrapped_servers:
			_log.info(u"server [%s] already bootstrapped" % aSrv_alias)
			return None

		self.alias = aSrv_alias
		self.section = "server %s" % self.alias
		self.auth_group = auth_group
		self.conn = None

		if not self.__bootstrap():
			raise ConstructorError("db_server.__init__(): Cannot bootstrap db server.")

		_bootstrapped_servers[self.alias] = self

		_log.info(u'done bootstrapping server [%s]', aSrv_alias)
	#--------------------------------------------------------------
	def __bootstrap(self):
		self.superuser = user(anAlias = cfg_get(self.section, "super user alias"))

		# connect to server level template database
		if not self.__connect_superuser_to_srv_template():
			_log.error(u"Cannot connect to server template database.")
			return None

		# add users/groups
		if not self.__bootstrap_db_users():
			_log.error(u"Cannot bootstrap database users.")
			return None

		self.conn.close()
		return True
	#--------------------------------------------------------------
	def __connect_superuser_to_srv_template(self):
		_log.info(u"connecting to server template database")

		# sanity checks
		self.template_db = cfg_get(self.section, "template database")
		if self.template_db is None:
			_log.error(u"Need to know the template database name.")
			return None

		self.name = cfg_get(self.section, "name")
		if self.name is None:
			_log.error(u"Need to know the server name.")
			return None

		env_var = 'GM_DB_PORT'
		self.port = os.getenv(env_var)
		if self.port is None:
			_log.info(u'environment variable [%s] is not set, using database port from config file' % env_var)
			self.port = cfg_get(self.section, "port")
		else:
			_log.info(u'using database port [%s] from environment variable [%s]' % (self.port, env_var))
		if self.port is None:
			_log.error(u"Need to know the database server port address.")
			return None

		if self.conn is not None:
			if self.conn.closed == 0:
				self.conn.close()

		self.conn = connect(self.name, self.port, self.template_db, self.superuser.name, self.superuser.password, conn_name = u'root@template.server')
		if self.conn is None:
			_log.error(u'Cannot connect.')
			return None

		self.conn.cookie = 'db_server.__connect_superuser_to_srv_template'

		# verify encoding
		curs = self.conn.cursor()
		curs.execute(u"select setting from pg_settings where name = 'lc_ctype'")
		data = curs.fetchall()
		lc_ctype = data[0][0]
		_log.info(u'template database LC_CTYPE is [%s]', lc_ctype)
		lc_ctype = lc_ctype.lower()
		if lc_ctype in ['c', 'posix']:
			_log.warning('while this cluster setting allows to store databases')
			_log.warning('in any encoding as is it does not allow for locale')
			_log.warning('sorting etc, hence it is not recommended for use')
			_log.warning('(although it will, technically, work)')
		elif not (lc_ctype.endswith('.utf-8') or lc_ctype.endswith('.utf8')):
			_log.error(u'LC_CTYPE does not end in .UTF-8 or .UTF8')
			curs.execute(u"show server_encoding")
			data = curs.fetchall()
			srv_enc = data[0][0]
			_log.info(u'server_encoding is [%s]', srv_enc)
			srv_enc = srv_enc.lower()
			if not srv_enc in ['utf8', 'utf-8']:
				_log.error(u'cluster encoding incompatible with utf8 encoded databases but')
				_log.error(u'for GNUmed installation the cluster must accept this encoding')
				_log.error(u'you may need to re-initdb or create a new cluster')
				return None
			_log.info(u'server encoding seems compatible despite not being reported in LC_CTYPE')

		# make sure we get english messages
		curs.execute(u"set lc_messages to 'C'")
		curs.close()

		_log.info(u"successfully connected to template database [%s]" % self.template_db)
		return True
	#--------------------------------------------------------------
	# user and group related
	#--------------------------------------------------------------
	def __bootstrap_db_users(self):
		_log.info(u"bootstrapping database users and groups")

		# insert standard groups
		if not self.__create_groups():
			_log.error(u"Cannot create GNUmed standard groups.")
			return None

		# create GNUmed owner
		if self.__create_dbowner() is None:
			_log.error(u"Cannot install GNUmed database owner.")
			return None

#		if not _import_schema(group=self.section, schema_opt='schema', conn=self.conn):
#			_log.error(u"Cannot import schema definition for server [%s] into database [%s]." % (self.name, self.template_db))
#			return None

		return True
	#--------------------------------------------------------------
	def __create_dbowner(self):
		global _dbowner

		dbowner_alias = cfg_get("GnuMed defaults", "database owner alias")
		if dbowner_alias is None:
			_log.error(u"Cannot load GNUmed database owner name from config file.")
			return None

		cursor = self.conn.cursor()
		# does this user already exist ?
		name = cfg_get('user %s' % dbowner_alias, 'name')
		if user_exists(cursor, name):
			cmd = (
				'alter group "gm-logins" add user "%s";'	# postgres
				'alter group "gm-logins" add user "%s";'	# gm-dbo
				'alter group "%s" add user "%s";'
				'alter role "%s" createdb createrole;'
			) % (
				self.superuser.name,
				name,
				self.auth_group, name,
				name,
			)
			try:
				cursor.execute(cmd)
			except:
				_log.error(u">>>[%s]<<< failed." % cmd)
				_log.exception(u"Cannot add GNUmed database owner [%s] to groups [gm-logins] and [%s]." % (name, self.auth_group))
				cursor.close()
				return False
			self.conn.commit()
			cursor.close()
			_dbowner = user(anAlias = dbowner_alias, aPassword = 'should not matter')
			return True

		print_msg ((
u"""The database owner [%s] will be created.

You will have to provide a new password for it
unless it is pre-defined in the configuration file.

Make sure to remember the password for later use !
""") % name)
		_dbowner = user(anAlias = dbowner_alias, force_interactive = True)

		cmd = 'create user "%s" with password \'%s\' createdb createrole in group "%s", "gm-logins"' % (_dbowner.name, _dbowner.password, self.auth_group)
		try:
			cursor.execute(cmd)
		except:
			_log.error(u">>>[%s]<<< failed." % cmd)
			_log.exception(u"Cannot create GNUmed database owner [%s]." % _dbowner.name)
			cursor.close()
			return None

		# paranoia is good
		if not user_exists(cursor, _dbowner.name):
			cursor.close()
			return None

		self.conn.commit()
		cursor.close()
		return True
	#--------------------------------------------------------------
	def __create_groups(self, aSection = None):

		if aSection is None:
			section = "GnuMed defaults"
		else:
			section = aSection

		groups = cfg_get(section, "groups")
		if groups is None:
			_log.error(u"Cannot load GNUmed group names from config file (section [%s])." % section)
			groups = [self.auth_group]
		else:
			groups.append(self.auth_group)

		cursor = self.conn.cursor()
		for group in groups:
			if not create_db_group(cursor, group):
				cursor.close()
				return False

		self.conn.commit()
		cursor.close()
		return True
#==================================================================
class database:
	def __init__(self, aDB_alias):
		_log.info(u"bootstrapping database [%s]" % aDB_alias)

		self.section = "database %s" % aDB_alias

		# find database name
		overrider = cfg_get(self.section, 'override name by')
		if overrider is not None:
			self.name = os.getenv(overrider)
			if self.name is None:
				_log.info(u'environment variable [%s] is not set, using database name from config file' % overrider)
				self.name = cfg_get(self.section, 'name')
		else:
			self.name = cfg_get(self.section, 'name')

		if self.name is None or str(self.name).strip() == '':
			_log.error(u"Need to know database name.")
			raise ConstructorError("database.__init__(): Cannot bootstrap database.")

		# already bootstrapped ?
		global _bootstrapped_dbs
		if aDB_alias in _bootstrapped_dbs:
			if _bootstrapped_dbs[aDB_alias].name == self.name:
				_log.info(u"database [%s] already bootstrapped", self.name)
				return None

		# no, so bootstrap from scratch
		_log.info(u'bootstrapping database [%s] alias "%s"', self.name, aDB_alias)

		for db in _bootstrapped_dbs.values():
			if db.conn.closed == 0:
				db.conn.close()
		_bootstrapped_dbs = {}
		self.conn = None

		self.server_alias = cfg_get(self.section, "server alias")
		if self.server_alias is None:
			_log.error(u"Server alias missing.")
			raise ConstructorError("database.__init__(): Cannot bootstrap database.")

		self.template_db = cfg_get(self.section, "template database")
		if self.template_db is None:
			_log.error(u"Template database name missing.")
			raise ConstructorError("database.__init__(): Cannot bootstrap database.")

		# make sure server is bootstrapped
		db_server(self.server_alias, auth_group = self.name)
		self.server = _bootstrapped_servers[self.server_alias]

		if not self.__bootstrap():
			raise ConstructorError("database.__init__(): Cannot bootstrap database.")

		_bootstrapped_dbs[aDB_alias] = self

		return None
	#--------------------------------------------------------------
	def __bootstrap(self):

		global _dbowner

		# get owner
		if _dbowner is None:
			_dbowner = user(anAlias = cfg_get("GnuMed defaults", "database owner alias"))

		if _dbowner is None:
			_log.error(u"Cannot load GNUmed database owner name from config file.")
			return None

		self.owner = _dbowner

		# connect as owner to template
		if not self.__connect_superuser_to_template():
			_log.error(u"Cannot connect to template database.")
			return False

		# fingerprint template db
		try:
			gmLog2.log_multiline (
				logging.INFO,
				message = 'template database fingerprint',
				text = gmPG2.get_db_fingerprint(conn = self.conn, eol = '\n')
			)
		except Exception:
			_log.exception('cannot fingerprint template database')

		self.conn.rollback()

		# make sure db exists
		if not self.__create_db():
			_log.error(u"Cannot create database.")
			return False

		# reconnect as superuser to db
		if not self.__connect_superuser_to_db():
			_log.error(u"Cannot connect to database.")
			return None

		# create authentication group
		_log.info(u'creating database-specific authentication group role')
		curs = self.conn.cursor()
		if not create_db_group(cursor = curs, group = self.name):
			curs.close()
			_log.error(u'cannot create authentication group role')
			return False
		self.conn.commit()
		curs.close()

		# paranoia check
		curs = self.conn.cursor()
		if not db_group_exists(cursor = curs, group = self.name):
			curs.close()
			_log.error(u'cannot find authentication group role')
			return False
		curs.close()

		# reindex db so upgrade doesn't fail on broken index
		llap = []
		reindexed = self.reindex_all()
		llap.append(reindexed)
		if not reindexed:
			_log.error(u'cannot REINDEX cloned target database')
			return False

		revalidated = self.revalidate_constraints()
		llap.append(revalidated)
		if not revalidated:
			_log.error(u'cannot VALIDATE CONSTRAINTs in cloned target database')
			return False

		if not self.validate_collations(use_the_source_luke = llap):
			_log.error(u'cannot validate collations in cloned target database')
			return False

		tmp = cfg_get(self.section, 'superuser schema')
		if tmp is not None:
			if not _import_schema(group=self.section, schema_opt='superuser schema', conn=self.conn):
				_log.error(u"cannot import schema definition for database [%s]" % (self.name))
				return False
		del tmp

		# transfer users
		if not self.transfer_users():
			_log.error(u"Cannot transfer users from old to new database.")
			return False

		# reconnect as owner to db
		if not self.__connect_owner_to_db():
			_log.error(u"Cannot connect to database.")
			return None
		if not _import_schema(group=self.section, schema_opt='schema', conn=self.conn):
			_log.error(u"cannot import schema definition for database [%s]" % (self.name))
			return None

		# don't close this here, the  connection will
		# be reused later by check_data*/import_data etc.
		#self.conn.close()

		return True

	#--------------------------------------------------------------
	def __connect_superuser_to_template(self):
		if self.conn is not None:
			if self.conn.closed == 0:
				self.conn.close()

		self.conn = connect (
			self.server.name,
			self.server.port,
			self.template_db,
			self.server.superuser.name,
			self.server.superuser.password,
			conn_name = u'postgres@template.db'
		)

		self.conn.cookie = 'database.__connect_superuser_to_template'

		curs = self.conn.cursor()
		curs.execute(u"set lc_messages to 'C'")
		curs.close()

		return self.conn and 1

	#--------------------------------------------------------------
	def __connect_superuser_to_db(self):
		if self.conn is not None:
			if self.conn.closed == 0:
				self.conn.close()

		self.conn = connect (
			self.server.name,
			self.server.port,
			self.name,
			self.server.superuser.name,
			self.server.superuser.password,
			conn_name = u'postgres@gnumed_vX'
		)

		self.conn.cookie = 'database.__connect_superuser_to_db'

		curs = self.conn.cursor()
		curs.execute(u'set default_transaction_read_only to off')
		# we need English messages to detect errors
		curs.execute(u"set lc_messages to 'C'")
		curs.execute(u"alter database %s set lc_messages to 'C'" % self.name)
		# we want READ ONLY default transactions for maximum patient data safety
		curs.execute("alter database %s set default_transaction_read_only to on" % self.name)
		# we want checking of function bodies
		curs.execute("alter database %s set check_function_bodies to on" % self.name)
		# we want checking of data checksums if available
		curs.execute("alter database %s set ignore_checksum_failure to off" % self.name)
		# tighten permissions on schema public
		curs.execute("revoke create on schema public from public")
		curs.close()
		self.conn.commit()

		# we need inheritance or else things will fail miserably but:
		# default now ON and PG10.0 hardwired to ON
		# so remove database specific setting
		curs = self.conn.cursor()
		try:
			curs.execute("alter database %s set sql_inheritance to DEFAULT" % self.name)
		except:
			_log.exception('PostgreSQL 10 onwards: <sql_inheritance> hardwired')
		curs.close()
		self.conn.commit()

		# we want to track commit timestamps if available
		# remove exception handler when 9.5 is default
		curs = self.conn.cursor()
		try:
			curs.execute("alter database %s set track_commit_timestamp to on" % self.name)
		except:
			_log.exception(u'PostgreSQL version < 9.5 does not support <track_commit_timestamp> OR <track_commit_timestamp> cannot be set at runtime')
		curs.close()
		self.conn.commit()

		# set owner of schema public to new role "pg_database_owner",
		# as suggested by PG 15 release notes
		curs = self.conn.cursor()
		try:
			curs.execute("alter schema public owner to pg_database_owner")
		except:
			_log.exception(u'PostgreSQL versions < 15 do not yet support role <pg_database_owner>')
		curs.close()
		self.conn.commit()

		curs = self.conn.cursor()
		gmConnectionPool.log_pg_settings(curs = curs)
		curs.close()
		self.conn.commit()

		return self.conn and 1
	#--------------------------------------------------------------
	def __connect_owner_to_db(self):

		_log.debug(u'__connect_owner_to_db')

		# reconnect as superuser to db
		if not self.__connect_superuser_to_db():
			_log.error(u"Cannot connect to database.")
			return False

		self.conn.cookie = 'database.__connect_owner_to_db via database.__connect_superuser_to_db'

		_log.debug(u'setting session authorization to user %s', self.owner.name)

		curs = self.conn.cursor()
		cmd = "set session authorization %(usr)s"
		curs.execute(cmd, {'usr': self.owner.name})
		curs.close()

		return self.conn and 1
	#--------------------------------------------------------------
	def __db_exists(self):
		#cmd = "BEGIN; SELECT datname FROM pg_database WHERE datname='%s'" % self.name
		cmd = "SELECT datname FROM pg_database WHERE datname='%s'" % self.name

		aCursor = self.conn.cursor()
		try:
			aCursor.execute(cmd)
		except:
			_log.exception(u">>>[%s]<<< failed." % cmd)
			return None

		res = aCursor.fetchall()
		tmp = aCursor.rowcount
		aCursor.close()
		if tmp == 1:
			_log.info(u"Database [%s] exists." % self.name)
			return True

		_log.info(u"Database [%s] does not exist." % self.name)
		return None

	#--------------------------------------------------------------
	def __create_db(self):
		_log.info('creating database')
		# verify template database hash
		template_version = cfg_get(self.section, 'template version')
		if template_version is None:
			_log.warning('cannot check template database identity hash, no version specified')
		else:
			converted, version = gmTools.input2int(template_version.lstrip('v'), 0)
			if not converted:
				_log.error(u'invalid template database definition: %s', template_version)
				return False

			if not gmPG2.database_schema_compatible(link_obj = self.conn, version = version):
				_log.error(u'invalid [%s] schema structure in GNUmed template database [%s]', template_version, self.template_db)
				return False

		# check for target database
		if self.__db_exists():
			drop_existing = bool(int(cfg_get(self.section, 'drop target database')))
			if drop_existing:
				print_msg("==> dropping pre-existing target database [%s] ..." % self.name)
				_log.info(u'trying to drop target database')
				cmd = 'DROP DATABASE "%s"' % self.name
				# DROP DATABASE must be run outside transactions
				self.conn.commit()
				self.conn.set_session(readonly = False, autocommit = True)
				cursor = self.conn.cursor()
				try:
					_log.debug(u'running SQL: %s', cmd)
					cursor.execute(cmd)
				except:
					_log.exception(u">>>[%s]<<< failed" % cmd)
					_log.debug(u'conn state after failed DROP: %s', gmConnectionPool.log_conn_state(self.conn))
					return False
				finally:
					cursor.close()
					self.conn.set_session(readonly = False, autocommit = False)
			else:
				use_existing = bool(int(cfg_get(self.section, 'use existing target database')))
				if use_existing:
					# FIXME: verify that database is owned by "gm-dbo"
					print_msg("==> using pre-existing target database [%s] ..." % self.name)
					_log.info(u'using existing database [%s]', self.name)
					return True
				else:
					_log.info(u'not using existing database [%s]', self.name)
					return False

		tablespace = cfg_get(self.section, 'tablespace')
		if tablespace is None:
			create_db_cmd = """
				CREATE DATABASE \"%s\" with
					owner = \"%s\"
					template = \"%s\"
					encoding = 'unicode'
				;""" % (self.name, self.owner.name, self.template_db)
		else:
			create_db_cmd = """
				CREATE DATABASE \"%s\" with
					owner = \"%s\"
					template = \"%s\"
					encoding = 'unicode'
					tablespace = '%s'
				;""" % (self.name, self.owner.name, self.template_db, tablespace)

		# get size
		cursor = self.conn.cursor()
		size_cmd = "SELECT pg_size_pretty(pg_database_size('%s'))" % self.template_db
		cursor.execute(size_cmd)
		size = cursor.fetchone()[0]
		cursor.close()

		# create database by cloning
		print_msg("==> [%s]: cloning (%s) as target database [%s] ..." % (self.template_db, size, self.name))
		# CREATE DATABASE must be run outside transactions
		self.conn.commit()
		self.conn.set_session(readonly = False, autocommit = True)
		cursor = self.conn.cursor()
		try:
			cursor.execute(create_db_cmd)
		except:
			_log.exception(u">>>[%s]<<< failed" % create_db_cmd)
			return False
		finally:
			cursor.close()
			self.conn.set_session(readonly = False, autocommit = False)

		if not self.__db_exists():
			return None
		_log.info(u"Successfully created GNUmed database [%s]." % self.name)

		return True

	#--------------------------------------------------------------
	def check_data_plausibility(self):

		print_msg("==> [%s]: checking migrated data for plausibility ..." % self.template_db)

		plausibility_queries = cfg_get(self.section, 'upgrade plausibility checks')
		if plausibility_queries is None:
			_log.warning('no plausibility checks defined')
			print_msg("    ... skipped (no checks defined)")
			return True

		no_of_queries, remainder = divmod(len(plausibility_queries), 2)
		if remainder != 0:
			_log.error(u'odd number of plausibility queries defined, aborting')
			print_msg("    ... failed (configuration error)")
			return False

		template_conn = connect (
			self.server.name,
			self.server.port,
			self.template_db,
			self.server.superuser.name,
			self.server.superuser.password
		)
		template_conn.cookie = 'check_data_plausibility: template'

		target_conn = connect (
			self.server.name,
			self.server.port,
			self.name,
			self.server.superuser.name,
			self.server.superuser.password
		)
		target_conn.cookie = 'check_data_plausibility: target'

		all_tests_successful = True

		for idx in range(no_of_queries):
			check_def = plausibility_queries[idx*2]
			if check_def.startswith('--'):
				_log.debug(u'skipped: %s', check_def)
				continue

			tag = u'?'
			old_query = u'?'
			try:
				tag, old_query = check_def.split('::::')
			except:
				_log.exception(u'error in plausibility check, aborting')
				_log.error(u'check definition: %s', check_def)
				print_msg("    ... failed (check definition error)")
				all_tests_successful = False
				continue
			new_query = plausibility_queries[(idx*2) + 1]

			try:
				rows, idx = gmPG2.run_ro_queries (
					link_obj = template_conn,
					queries = [{'cmd': old_query}]
				)
				old_val = rows[0][0]
			except:
				_log.exception(u'error in plausibility check [%s] (old), aborting' % tag)
				_log.error(u'SQL: %s', old_query)
				print_msg("    ... failed (SQL error)")
				all_tests_successful = False
				continue

			try:
				rows, idx = gmPG2.run_ro_queries (
					link_obj = target_conn,
					queries = [{'cmd': new_query}]
				)
				new_val = rows[0][0]
			except:
				_log.exception(u'error in plausibility check [%s] (new), aborting' % tag)
				_log.error(u'SQL: %s', new_query)
				print_msg("    ... failed (SQL error)")
				all_tests_successful = False
				continue

			if new_val != old_val:
				_log.error(u'plausibility check [%s] failed, expected: %s (in old DB), found: %s (in new DB)' % (tag, old_val, new_val))
				_log.error(u'SQL (old DB): %s', old_query)
				_log.error(u'SQL (new DB): %s', new_query)
				print_msg("    ... failed (data error, check [%s])" % tag)
				all_tests_successful = False
				continue

			_log.info(u'plausibility check [%s] succeeded' % tag)

		template_conn.close()
		target_conn.close()

		return all_tests_successful

	#--------------------------------------------------------------
	def check_holy_auth_line(self):

		holy_pattern = 'local.*samerole.*\+gm-logins'
		holy_pattern_inactive = '#\s*local.*samerole.*\+gm-logins'

		conn = connect (
			self.server.name,
			self.server.port,
			self.name,
			self.server.superuser.name,
			self.server.superuser.password
		)
		conn.cookie = u'holy auth check connection'

		cmd = u"select setting from pg_settings where name = 'hba_file'"
		rows, idx = gmPG2.run_ro_queries(link_obj = conn, queries = [{'cmd': cmd}])
		conn.close()
		if len(rows) == 0:
			_log.info(u'cannot check pg_hba.conf for authentication information - not detectable in pg_settings')
			return

		hba_file = rows[0][0]
		_log.info(u'hba file: %s', hba_file)

		try:
			f = io.open(hba_file, mode = 'rt').close()
		except Exception:
			_log.exception(u'cannot check pg_hba.conf for authentication information - not readable')
			return

		found_holy_line = False
		for line in fileinput.input(hba_file):
			if regex.match(holy_pattern, line) is not None:
				found_holy_line = True
				_log.info(u'found standard GNUmed authentication directive in pg_hba.conf')
				_log.info(u'[%s]', line)
				_log.info(u'it may still be in the wrong place, though, so double-check if clients cannot connect')
				break

		if not found_holy_line:
			_log.info(u'did not find active standard GNUmed authentication directive in pg_hba.conf')
			_log.info(u'regex: %s' % holy_pattern)

			found_holy_line_inactive = False
			for line in fileinput.input(hba_file):
				if regex.match(holy_pattern_inactive, line) is not None:
					found_holy_line_inactive = True
					_log.info(u'found inactive standard GNUmed authentication directive in pg_hba.conf')
					_log.info(u'[%s]', line)
					_log.info(u'it may still be in the wrong place, though, so double-check if clients cannot connect')
					break
			if not found_holy_line_inactive:
				_log.info(u'did not find inactive standard GNUmed authentication directive in pg_hba.conf either')
				_log.info(u'regex: %s' % holy_pattern_inactive)

			_log.info(u'bootstrapping is likely to have succeeded but clients probably cannot connect yet')
			print_msg('==> sanity checking PostgreSQL authentication settings ...')
			print_msg('')
			print_msg('Note that even after successfully bootstrapping the GNUmed ')
			print_msg('database PostgreSQL may still need to be configured to')
			print_msg('allow GNUmed clients to connect to it.')
			print_msg('')
			print_msg('In many standard PostgreSQL installations this amounts to')
			print_msg('adding (or uncommenting) the authentication directive:')
			print_msg('')
			print_msg('  "local   samerole    +gm-logins   md5"')
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

		print_msg("==> [%s]: upgrading reference data sets ..." % self.name)

		import_scripts = cfg_get(self.section, "data import scripts")
		if (import_scripts is None) or (len(import_scripts) == 0):
			_log.info(u'skipped data import: no scripts to run')
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
				_log.error(u'cannot load data set import script [%s/%s]' % (script_base_dir, import_script))
				return False

			try:
				script.run(conn = self.conn)
			except:
				print_msg("    ... failed (cannot run script [%s])" % import_script)
				_log.exception(u'cannot run import script [%s]' % import_script)
				return False

			if import_script.endswith('.py'):
				import_script = import_script[:-3]
			import gc
			try:
				del sys.modules[import_script]
				del script
				gc.collect()
			except:
				_log.exception(u'cannot remove data import script module [%s], hoping for the best', import_script)

		return True

	#--------------------------------------------------------------
	def verify_result_hash(self):

		print_msg("==> [%s]: verifying target database schema ..." % self.name)

		target_version = cfg_get(self.section, 'target version')
		if target_version == 'devel':
			print_msg("    ... skipped (devel version)")
			_log.info(u'result schema hash: %s', gmPG2.get_schema_hash(link_obj = self.conn))
			_log.warning('testing/development only, not failing due to invalid target database identity hash')
			return True
		converted, version = gmTools.input2int(target_version.lstrip('v'), 2)
		if not converted:
			_log.error(u'cannot convert target database version: %s', target_version)
			print_msg("    ... failed (invalid target version specification)")
			return False
		if gmPG2.database_schema_compatible(link_obj = self.conn, version = version):
			_log.info(u'database identity hash properly verified')
			return True
		_log.error(u'target database identity hash invalid')
		print_msg("    ... failed (hash mismatch)")
		return False

	#--------------------------------------------------------------
	def reindex_all(self):
		print_msg("==> [%s]: reindexing target database (can take a while) ..." % self.name)
		do_reindex = cfg_get(self.section, 'reindex')
		if do_reindex is None:
			do_reindex = True
		else:
			do_reindex = (int(do_reindex) == 1)
		if not do_reindex:
			_log.warning('skipping REINDEXing')
			print_msg("    ... skipped")
			return True

		_log.info(u'REINDEXing cloned target database so upgrade does not fail in case of a broken index')
		_log.info(u'this may potentially take "quite a long time" depending on how much data there is in the database')
		_log.info(u'you may want to monitor the PostgreSQL log for signs of progress')
		reindexed = gmPG2.reindex_database(conn = self.conn)
		if not reindexed:
			print_msg('    ... failed')
			_log.error('REINDEXing database failed')
			return False

		return reindexed

	#--------------------------------------------------------------
	def revalidate_constraints(self):

		print_msg("==> [%s]: revalidating constraints in target database (can take a while) ..." % self.name)

		do_revalidate = cfg_get(self.section, 'revalidate')
		if do_revalidate is None:
			do_revalidate = True		# default: do it
		else:
			do_revalidate = (int(do_revalidate) == 1)
		if not do_revalidate:
			_log.warning('skipping VALIDATE CONSTRAINT')
			print_msg("    ... skipped")
			return True

		_log.info(u'reVALIDATing CONSTRAINTs in cloned target database so upgrade does not fail due to broken data')
		_log.info(u'this may potentially take "quite a long time" depending on how much data there is in the database')
		_log.info(u'you may want to monitor the PostgreSQL log for signs of progress')
		try:
			revalidated = gmPG2.revalidate_constraints(link_obj = self.conn)
		except Exception:
			_log.exception('>>>[VALIDATE CONSTRAINT]<<< failed')
			return False

		return revalidated

	#--------------------------------------------------------------
	def validate_collations(self, use_the_source_luke):
		print_msg('==> [%s]: validating collations ...' % self.name)
		sane_pg_database_collation = gmPG2.sanity_check_database_default_collation_version(conn = self.conn)
		sane_pg_collations = gmPG2.sanity_check_collation_versions(conn = self.conn)
		if sane_pg_database_collation and sane_pg_collations:
			return True

		_log.debug('Kelvin: %s', use_the_source_luke)
		if sane_pg_database_collation is False:
			if not gmPG2.refresh_database_default_collation_version_information(conn = self.conn, use_the_source_luke = use_the_source_luke):
				print_msg('    ... fixing database default collation failed')
				return False

		if sane_pg_collations is False:
			if not gmPG2.refresh_collations_version_information(conn = self.conn, use_the_source_luke = use_the_source_luke):
				print_msg('    ... fixing all other collations failed')
				return False

		return True

	#--------------------------------------------------------------
	def transfer_users(self):
		print_msg("==> [%s]: transferring users ..." % self.name)
		do_user_transfer = cfg_get(self.section, 'transfer users')
		if do_user_transfer is None:
			_log.info(u'user transfer not defined')
			print_msg("    ... skipped (unconfigured)")
			return True
		do_user_transfer = int(do_user_transfer)
		if not do_user_transfer:
			_log.info(u'configured to not transfer users')
			print_msg("    ... skipped (disabled)")
			return True

		cmd = u"select gm.transfer_users('%s'::text)" % self.template_db
		try:
			rows, idx = gmPG2.run_rw_queries(link_obj = self.conn, queries = [{'cmd': cmd}], end_tx = True, return_data = True)
		except gmPG2.dbapi.ProgrammingError:
			# maybe an old database
			_log.info(u'problem running gm.transfer_users(), trying gm_transfer_users()')
			cmd = u"select gm_transfer_users('%s'::text)" % self.template_db
			rows, idx = gmPG2.run_rw_queries(link_obj = self.conn, queries = [{'cmd': cmd}], end_tx = True, return_data = True)

		if rows[0][0]:
			_log.info(u'users properly transferred from [%s] to [%s]' % (self.template_db, self.name))
			return True
		_log.error(u'error transferring user from [%s] to [%s]' % (self.template_db, self.name))
		print_msg("    ... failed")
		return False

	#--------------------------------------------------------------
	def bootstrap_auditing(self):
		print_msg("==> [%s]: setting up auditing ..." % self.name)
		# get audit trail configuration
		tmp = cfg_get(self.section, 'audit disable')
		# if this option is not given, assume we want auditing
		if tmp is not None:
			# if we don't want auditing on these tables, return without error
			if int(tmp) == 1:
				print_msg('    ... skipped (disabled)')
				return True

		tmp = cfg_get(self.section, 'audit trail parent table')
		if tmp is None:
			return None
		aud_gen.audit_trail_parent_table = tmp

		tmp = cfg_get(self.section, 'audit trail table prefix')
		if tmp is None:
			return None
		aud_gen.audit_trail_table_prefix = tmp

		tmp = cfg_get(self.section, 'audit fields table')
		if tmp is None:
			return None
		aud_gen.audit_fields_table = tmp

		# create auditing schema
		curs = self.conn.cursor()
		audit_schema = gmAuditSchemaGenerator.create_audit_ddl(curs)
		curs.close()
		if audit_schema is None:
			_log.error(u'cannot generate audit trail schema for GNUmed database [%s]' % self.name)
			return None
		# write schema to file
		tmpfile = os.path.join(tempfile.gettempdir(), 'audit-trail-schema.sql')
		f = io.open(tmpfile, mode = 'wt', encoding = 'utf8')
		for line in audit_schema:
			f.write(u'%s;\n' % line)
		f.close()

		# import auditing schema
		psql = gmPsql.Psql(self.conn)
		if psql.run(tmpfile) != 0:
			_log.error(u"cannot import audit schema definition for database [%s]" % (self.name))
			return None

		if _keep_temp_files:
			return True

		try:
			os.remove(tmpfile)
		except Exception:
			_log.exception(u'cannot remove audit trail schema file [%s]' % tmpfile)
		return True

	#--------------------------------------------------------------
	def bootstrap_notifications(self):

		# setup clin.clin_root_item child tables FK's
		print_msg("==> [%s]: setting up encounter/episode FKs and IDXs ..." % self.name)
		child_tables = gmPG2.get_child_tables(link_obj = self.conn, schema = 'clin', table = 'clin_root_item')
		_log.info(u'clin.clin_root_item child tables:')
		for child in child_tables:
			_log.info(u'%s.%s', child['namespace'], child['table'])
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
				_log.info(u'%s FK(s) exist:', len(FKs))
				for idx in range(len(FKs)):
					FK = FKs[idx]
					_log.info(u' #%s = %s.%s: %s.%s.%s -> %s.%s.%s', idx + 1, FK['constraint_schema'], FK['constraint_name'], FK['source_schema'], FK['source_table'], FK['source_column'], FK['target_schema'], FK['target_table'], FK['target_column'])
			else:
				_log.info(u'adding FK: %s.%s.fk_episode -> clin.episode.pk', child['namespace'], child['table'])
				cmd = SQL_add_foreign_key % {
					'src_schema': child['namespace'],
					'src_tbl': child['table'],
					'src_col': 'fk_episode',
					'target_schema': 'clin',
					'target_tbl': 'episode',
					'target_col': 'pk'
				}
				gmPG2.run_rw_queries(link_obj = self.conn, queries = [{'cmd': cmd}])
			# index on .fk_episode
			idx_defs = gmPG2.get_index_name(indexed_table = u'%s.%s' % (child['namespace'], child['table']), indexed_column = u'fk_episode', link_obj = self.conn)
			# drop any existing
			for idx_def in idx_defs:
				_log.info(u'dropping index %s.%s', idx_def['index_schema'], idx_def['index_name'])
				cmd = u'DROP INDEX IF EXISTS %s.%s CASCADE' % (idx_def['index_schema'], idx_def['index_name'])
				gmPG2.run_rw_queries(link_obj = self.conn, queries = [{'cmd': cmd}])
			# create
			_log.info(u'creating index idx_%s_%s_fk_episode', child['namespace'], child['table'])
			cmd = SQL_add_index % {
				'idx_schema': child['namespace'],
				'idx_name': u'idx_%s_%s_fk_episode' % (child['namespace'], child['table']),
				'idx_table': child['table'],
				'idx_col': u'fk_episode'
			}
			gmPG2.run_rw_queries(link_obj = self.conn, queries = [{'cmd': cmd}])

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
				_log.info(u'%s FK(s) exist:', len(FKs))
				for idx in range(len(FKs)):
					FK = FKs[idx]
					_log.info(u' #%s = %s.%s: %s.%s.%s -> %s.%s.%s', idx + 1, FK['constraint_schema'], FK['constraint_name'], FK['source_schema'], FK['source_table'], FK['source_column'], FK['target_schema'], FK['target_table'], FK['target_column'])
			else:
				_log.info(u'adding FK: %s.%s.fk_encounter -> clin.encounter.pk', child['namespace'], child['table'])
				cmd = SQL_add_foreign_key % {
					'src_schema': child['namespace'],
					'src_tbl': child['table'],
					'src_col': 'fk_encounter',
					'target_schema': 'clin',
					'target_tbl': 'encounter',
					'target_col': 'pk'
				}
				gmPG2.run_rw_queries(link_obj = self.conn, queries = [{'cmd': cmd}])
			# index on .fk_encounter
			idx_defs = gmPG2.get_index_name(indexed_table = u'%s.%s' % (child['namespace'], child['table']), indexed_column = u'fk_encounter', link_obj = self.conn)
			# drop any existing
			for idx_def in idx_defs:
				_log.info(u'dropping index %s.%s', idx_def['index_schema'], idx_def['index_name'])
				cmd = u'DROP INDEX IF EXISTS %s.%s CASCADE' % (idx_def['index_schema'], idx_def['index_name'])
				gmPG2.run_rw_queries(link_obj = self.conn, queries = [{'cmd': cmd}])
			# create
			_log.info(u'creating index idx_%s_%s_fk_encounter', child['namespace'], child['table'])
			cmd = SQL_add_index % {
				'idx_schema': child['namespace'],
				'idx_name': u'idx_%s_%s_fk_encounter' % (child['namespace'], child['table']),
				'idx_table': child['table'],
				'idx_col': u'fk_encounter'
			}
			gmPG2.run_rw_queries(link_obj = self.conn, queries = [{'cmd': cmd}])

		curs = self.conn.cursor()

		# re-create fk_encounter/fk_episode sanity check triggers on all tables
		if gmPG2.function_exists(link_obj = curs, schema = u'gm', function = u'create_all_enc_epi_sanity_check_triggers'):
			print_msg("==> [%s]: setting up encounter/episode FK sanity check triggers ..." % self.name)
			_log.debug(u'attempting to set up sanity check triggers on all tables linking to encounter AND episode')
			cmd = u'select gm.create_all_enc_epi_sanity_check_triggers()'
			curs.execute(cmd)
			result = curs.fetchone()
			if result[0] is False:
				_log.error(u'error creating sanity check triggers on all tables linking to clin.encounter AND clin.episode')
				curs.close()
				return None

		# always re-create generic super signal (if exists)
		if gmPG2.function_exists(link_obj = curs, schema = u'gm', function = u'create_all_table_mod_triggers'):
			print_msg("==> [%s]: setting up generic notifications ..." % self.name)
			_log.debug(u'attempting to create generic modification announcement triggers on all registered tables')

			cmd = u"SELECT gm.create_all_table_mod_triggers(True::boolean)"
			curs.execute(cmd)
			result = curs.fetchone()
			curs.close()
			if result[0] is False:
				_log.error(u'cannot create generic modification announcement triggers on all tables')
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
		_log.info(u"bootstrapping bundle [%s]" % self.alias)

		# load bundle definition
		database_alias = cfg_get(self.section, "database alias")
		if database_alias is None:
			_log.error(u"Need to know database name to install bundle [%s]." % self.alias)
			return None
		# bootstrap database
		try:
			database(aDB_alias = database_alias)
		except:
			_log.exception(u"Cannot bootstrap bundle [%s].", self.alias)
			return None
		self.db = _bootstrapped_dbs[database_alias]

		# check PostgreSQL version
		if not self.__verify_pg_version():
			_log.error(u"Wrong PostgreSQL version.")
			return None

		# import schema
		if not _import_schema(group=self.section, schema_opt='schema', conn=self.db.conn):
			_log.error(u"Cannot import schema definition for bundle [%s] into database [%s]." % (self.alias, database_alias))
			return None

		return True
	#--------------------------------------------------------------
	def __verify_pg_version(self):
		"""Verify database version information."""

		required_version = cfg_get(self.section, "minimum postgresql version")
		if required_version is None:
			_log.error(u"Cannot load minimum required PostgreSQL version from config file.")
			return None

		_log.info(u"minimum required PostgreSQL version: %s" % required_version)

		converted, pg_ver = gmTools.input2decimal(gmConnectionPool.postgresql_version)

		if not converted:
			_log.error(u'error checking PostgreSQL version')
			return None
		converted, req_version = gmTools.input2decimal(required_version)
		if not converted:
			_log.error(u'error checking PostgreSQL version')
			_log.error(u'required: %s', required_version)
			return None
		if pg_ver < req_version:
			_log.error(u"Reported live PostgreSQL version [%s] is smaller than the required minimum version [%s].", pg_ver, required_version)
			return None

		_log.info(u"installed PostgreSQL version: %s - this is fine with me", pg_ver)
		return True
#==================================================================
def bootstrap_bundles():
	# get bundle list
	bundles = cfg_get("installation", "bundles")
	if bundles is None:
		exit_with_msg("Bundle list empty. Nothing to do here.")
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
def bootstrap_auditing():
	"""bootstrap auditing in all bootstrapped databases"""
	for db_key in _bootstrapped_dbs.keys():
		db = _bootstrapped_dbs[db_key]
		if not db.bootstrap_auditing():
			return None
	return True
#--------------------------------------------------------------
def bootstrap_notifications():
	"""bootstrap notification in all bootstrapped databases"""
	for db_key in _bootstrapped_dbs.keys():
		db = _bootstrapped_dbs[db_key]
		if not db.bootstrap_notifications():
			return None
	return True
#------------------------------------------------------------------
def _run_query(aCurs, aQuery, args=None):
	# FIXME: use gmPG2.run_rw_query()
	if args is None:
		try:
			aCurs.execute(aQuery)
		except:
			_log.exception(u">>>%s<<< failed" % aQuery)
			return False
	else:
		try:
			aCurs.execute(aQuery, args)
		except:
			_log.exception(u">>>%s<<< failed" % aQuery)
			_log.error(str(args))
			return False
	return True

#------------------------------------------------------------------
def ask_for_confirmation():
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
		_log.error(u"Need to know schema definition to install it.")
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
		if filename.strip() == u'':
			continue						# skip empty line
		if filename.startswith(u'# '):
			_log.info(filename)				# log as comment
			continue
		full_path = os.path.join(schema_base_dir, filename)
		if psql.run(full_path) == 0:
			#_log.info(u'success')
			continue
		_log.error(u'failure')
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
	_log.info(u'shutdown')
	sys.exit(1)

#------------------------------------------------------------------
def print_msg(msg=None):
	if quiet:
		return
	print(msg)

#-----------------------------------------------------------------
def become_pg_demon_user():
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
		running_as = pwd.getpwuid(os.getuid())[0]
		_log.info(u'running as user [%s]' % running_as)
	except:
		running_as = None

	pg_demon_user_passwd_line = None
	try:
		pg_demon_user_passwd_line = pwd.getpwnam('postgres')
		# make sure we actually use this name to log in
		_cfg.set_option(group = 'user postgres', option = 'name', value = 'postgres', source = 'file')
	except KeyError:
		try:
			pg_demon_user_passwd_line = pwd.getpwnam ('pgsql')
			_cfg.set_option(group = 'user postgres', option = 'name', value = 'pgsql', source = 'file')
		except KeyError:
			_log.warning('cannot find postgres user')
			return None

	if os.getuid() == 0: # we are the super-user
		_log.info(u'switching to UNIX user [%s]' % pg_demon_user_passwd_line[0])
		os.setuid(pg_demon_user_passwd_line[2])

	elif running_as == pg_demon_user_passwd_line[0]: # we are the postgres user already
		_log.info(u'I already am the UNIX user [%s]' % pg_demon_user_passwd_line[0])

	else:
		_log.warning('not running as root or postgres, cannot become postmaster demon user')
		_log.warning('may have trouble connecting as gm-dbo if IDENT auth is forced upon us')
		if _interactive:
			print_msg("WARNING: This script may not work if not running as the system administrator.")

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

	_log.info(u'config file: %s', _cfg.source_files['file'])

	become_pg_demon_user()

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

	if not ask_for_confirmation():
		exit_with_msg("Bootstrapping aborted by user.")

	if not bootstrap_bundles():
		exit_with_msg("Cannot bootstrap bundles.")

	if not bootstrap_auditing():
		exit_with_msg("Cannot bootstrap audit trail.")

	if not bootstrap_notifications():
		exit_with_msg("Cannot bootstrap notification tables.")

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
def main():

	_cfg.add_cli(long_options = ['conf-file=', 'log-file=', 'quiet'])

	global quiet
	quiet = bool(_cfg.get(option = '--quiet', source_order = [('cli', 'return')]))

	print_msg("=======================================")
	print_msg("Bootstrapping GNUmed database system...")
	print_msg("=======================================")

	# get initial conf file from CLI
	cfg_file = _cfg.get(option = '--conf-file', source_order = [('cli', 'return')])
	if cfg_file is None:
		_log.error(u"no config file specified on command line")
		exit_with_msg('Cannot bootstrap without config file. Use --conf-file=<FILE>.')

	_log.info(u'initial config file: %s', cfg_file)

	# read that conf file
	_cfg.add_file_source (
		source = 'file',
		file = cfg_file
	)

	# does it point to other conf files ?
	cfg_files = _cfg.get (
		group = 'installation',
		option = 'config files',
		source_order = [('file', 'return')]
	)

	if cfg_files is None:
		_log.info(u'single-shot config file')
		handle_cfg()
	else:
		_log.info(u'aggregation of config files')
		tmp = cfg_get("installation", "interactive")
		global _interactive
		if tmp == "no":
			_interactive = False
		else:
			_interactive = True
		for cfg_file in cfg_files:
			# read that conf file
			_cfg.add_file_source (
				source = 'file',
				file = cfg_file
			)
			handle_cfg()

	global _bootstrapped_dbs

	db = next(iter(_bootstrapped_dbs.values()))
	#db = _bootstrapped_dbs[_bootstrapped_dbs.keys()[0]]

	if not db.verify_result_hash():
		exit_with_msg("Bootstrapping failed: wrong result hash")

	if not db.check_data_plausibility():
		exit_with_msg("Bootstrapping failed: plausibility checks inconsistent")

#	if not db.import_data():
#		exit_with_msg("Bootstrapping failed: unable to import data")

	db.check_holy_auth_line()

	_log.info(u"shutdown")
	print("Done bootstrapping GNUmed database: We very likely succeeded.")
	print('log:', gmLog2._logfile_name)

#==================================================================
if __name__ != "__main__":
	print("This currently is not intended to be used as a module.")
	sys.exit(1)


gmI18N.activate_locale()

_log.info(u'startup')

try:
	main()
except Exception:
	_log.exception(u'unhandled exception caught, shutting down connections')
	exit_with_msg(u'Bootstrapping failed: unhandled exception occurred')
finally:
	for conn in conn_ref_count:
		if conn.closed == 0:
			_log.warning(u'open connection detected: %s', conn.cookie)
			_log.warning(u'%s', conn)
			_log.warning(u'closing connection')
			conn.close()

_log.info(u'after main, before sys.exit(0)')

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
#		_log.debug(u"child stdout: [%s]" % line, gmLog.lCooked)
#	tmp = pipe.childerr.read()
#	lines = tmp.split("\n")
#	for line in lines:
#		_log.error(u"child stderr: [%s]" % line, gmLog.lCooked)

#	pipe.fromchild.close()
#	pipe.childerr.close()
#	del pipe

#==================================================================
