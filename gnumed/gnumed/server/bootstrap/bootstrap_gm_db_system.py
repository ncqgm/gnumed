#!/usr/bin/env python

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
"""
#==================================================================
# TODO
# - perhaps create PGPASSFILE
# - warn if empty password
# - verify that pre-created database is owned by "gm-dbo"
# - rework under assumption that there is only one DB
#==================================================================
__version__ = "$Revision: 1.113 $"
__author__ = "Karsten.Hilbert@gmx.net"
__license__ = "GPL"

# standard library
import sys, string, os.path, fileinput, os, time, getpass, glob, re as regex, tempfile, logging


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
	print "Creating module import symlink ..."
	print ' real dir:', real_dir
	print '     link:', link_name
	os.symlink(real_dir, link_name)

print "Adjusting PYTHONPATH ..."
sys.path.insert(0, local_python_base_dir)


# GNUmed imports
try:
	from Gnumed.pycommon import gmLog2
except ImportError:
	print """Please make sure the GNUmed Python modules are in the Python path !"""
	raise
from Gnumed.pycommon import gmCfg2, gmPsql, gmPG2, gmTools, gmI18N
from Gnumed.pycommon.gmExceptions import ConstructorError


# local imports
import gmAuditSchemaGenerator
aud_gen = gmAuditSchemaGenerator

import gmNotificationSchemaGenerator
notify_gen = gmNotificationSchemaGenerator


_log = logging.getLogger('gm.bootstrapper')
_cfg = gmCfg2.gmCfgData()


_interactive = False
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
to get the neccessary permissions.

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

Please select a database configuation from the list below.
"""
#==================================================================
def user_exists(cursor=None, user=None):
	cmd = "SELECT usename FROM pg_user WHERE usename = %(usr)s"
	args = {'usr': user}
	try:
		cursor.execute(cmd, args)
	except:
		_log.exception(">>>[%s]<<< failed for user [%s]", cmd, user)
		return None
	res = cursor.fetchone()
	if cursor.rowcount == 1:
		_log.info("user [%s] exists", user)
		return True
	_log.info("user [%s] does not exist", user)
	return None
#------------------------------------------------------------------
def db_group_exists(cursor=None, group=None):
	cmd = 'SELECT groname FROM pg_group WHERE groname = %(grp)s'
	args = {'grp': group}
	try:
		cursor.execute(cmd, args)
	except:
		_log.exception(">>>[%s]<<< failed for group [%s]", cmd, group)
		return False
	rows = cursor.fetchall()
	if len(rows) > 0:
		_log.info("group [%s] exists" % group)
		return True
	_log.info("group [%s] does not exist" % group)
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
		_log.exception(">>>[%s]<<< failed for group [%s]", cmd, group)
		return False

	# paranoia is good
	if not db_group_exists(cursor, group):
		return False

	return True
#==================================================================
def connect(host, port, db, user, passwd):
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
		if cached_passwd.has_key (user):
			passwd = cached_passwd[user]
		else:
			passwd = ''

	dsn = gmPG2.make_psycopg2_dsn(database=db, host=host, port=port, user=user, password=passwd)
	_log.info("trying DB connection to %s on %s as %s", db, host or 'localhost', user)
	try:
		conn = gmPG2.get_connection(dsn=dsn, readonly=False, pooled=False, verbose=True)
	except:
		_log.exception(u'connection failed')
		raise

	cached_host = (host, port) # learn from past successes
	cached_passwd[user] = passwd
	conn_ref_count.append(conn)

	_log.info('successfully connected')
	return conn
#==================================================================
class user:
	def __init__(self, anAlias = None, aPassword = None):
		if anAlias is None:
			raise ConstructorError, "need user alias"
		self.alias = anAlias
		self.group = "user %s" % self.alias

		self.name = cfg_get(self.group, "name")
		if self.name is None:
			raise ConstructorError, "cannot get user name"

		self.password = aPassword

		# password not passed in, try to get it from elsewhere
		if self.password is None:
			# look into config file
			self.password = cfg_get(self.group, "password")
			# undefined or commented out:
			# this means the user does not need a password
			# but connects via IDENT or TRUST
			if self.password is None:
				_log.info('password not defined, assuming connect via IDENT/TRUST')
			# defined but empty:
			# this means to ask the user if interactive
			elif self.password == '':
				if _interactive:
					print "I need the password for the GNUmed database user [%s]." % self.name
					self.password = getpass.getpass("Please type the password: ")
				else:
					_log.warning('cannot get password for database user [%s]', self.name)
					raise ValueError('no password for user %s' % self.name)

		return None
#==================================================================
class db_server:
	def __init__(self, aSrv_alias, auth_group):
		_log.info("bootstrapping server [%s]" % aSrv_alias)

		global _bootstrapped_servers

		if _bootstrapped_servers.has_key(aSrv_alias):
			_log.info("server [%s] already bootstrapped" % aSrv_alias)
			return None

		self.alias = aSrv_alias
		self.section = "server %s" % self.alias
		self.auth_group = auth_group
		self.conn = None

		if not self.__bootstrap():
			raise ConstructorError, "db_server.__init__(): Cannot bootstrap db server."

		_bootstrapped_servers[self.alias] = self

		_log.info('done bootstrapping server [%s]', aSrv_alias)
	#--------------------------------------------------------------
	def __bootstrap(self):
		self.superuser = user(anAlias = cfg_get(self.section, "super user alias"))

		# connect to server level template database
		if not self.__connect_superuser_to_srv_template():
			_log.error("Cannot connect to server template database.")
			return None

		# add users/groups
		if not self.__bootstrap_db_users():
			_log.error("Cannot bootstrap database users.")
			return None

		self.conn.close()
		return True
	#--------------------------------------------------------------
	def __connect_superuser_to_srv_template(self):
		_log.info("connecting to server template database")

		# sanity checks
		self.template_db = cfg_get(self.section, "template database")
		if self.template_db is None:
			_log.error("Need to know the template database name.")
			return None

		self.name = cfg_get(self.section, "name")
		if self.name is None:
			_log.error("Need to know the server name.")
			return None

		env_var = 'GM_DB_PORT'
		self.port = os.getenv(env_var)
		if self.port is None:
			_log.info('environment variable [%s] is not set, using database port from config file' % env_var)
			self.port = cfg_get(self.section, "port")
		else:
			_log.info('using database port [%s] from environment variable [%s]' % (self.port, env_var))
		if self.port is None:
			_log.error("Need to know the database server port address.")
			return None

		if self.conn is not None:
			if self.conn.closed == 0:
				self.conn.close()

		self.conn = connect (self.name, self.port, self.template_db, self.superuser.name, self.superuser.password)
		if self.conn is None:
			_log.error('Cannot connect.')
			return None

		self.conn.cookie = 'db_server.__connect_superuser_to_srv_template'

		curs = self.conn.cursor()
		curs.execute(u"select setting from pg_settings where name = 'lc_ctype'")
		data = curs.fetchall()
		lc_ctype = data[0][0]
		_log.info('template database LC_CTYPE is [%s]', lc_ctype)
		lc_ctype = lc_ctype.lower()
		if lc_ctype in ['c', 'posix']:
			_log.warning('while this cluster setting allows to store databases')
			_log.warning('in any encoding as is it does not allow for locale')
			_log.warning('sorting etc, hence it is not recommended for use')
		elif not (lc_ctype.endswith('.utf-8') or lc_ctype.endswith('.utf8')):
			_log.error('LC_CTYPE does not end in .UTF-8 or .UTF8')
			_log.error('cluster encoding incompatible with utf8 encoded databases but')
			_log.error('for GNUmed installation the cluster must accept this encoding')
			_log.error('you may need to re-initdb or create a new cluster')
			return None
		# make sure we get english messages
		curs.execute(u"set lc_messages to 'C'")
		curs.close()

		_log.info("successfully connected to template database [%s]" % self.template_db)
		return True
	#--------------------------------------------------------------
	# user and group related
	#--------------------------------------------------------------
	def __bootstrap_db_users(self):
		_log.info("bootstrapping database users and groups")

		# insert standard groups
		if not self.__create_groups():
			_log.error("Cannot create GNUmed standard groups.")
			return None

		# create GNUmed owner
		if self.__create_dbowner() is None:
			_log.error("Cannot install GNUmed database owner.")
			return None

#		if not _import_schema(group=self.section, schema_opt='schema', conn=self.conn):
#			_log.error("Cannot import schema definition for server [%s] into database [%s]." % (self.name, self.template_db))
#			return None

		return True
	#--------------------------------------------------------------
	def __create_dbowner(self):
		global _dbowner

		dbowner_alias = cfg_get("GnuMed defaults", "database owner alias")
		if dbowner_alias is None:
			_log.error("Cannot load GNUmed database owner name from config file.")
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
				_log.error(">>>[%s]<<< failed." % cmd)
				_log.exception("Cannot add GNUmed database owner [%s] to groups [gm-logins] and [%s]." % (name, self.auth_group))
				cursor.close()
				return False
			self.conn.commit()
			cursor.close()
			_dbowner = user(anAlias = dbowner_alias, aPassword = 'should not matter')
			return True

		print_msg ((
"""The database owner will be created.
You will have to provide a new password for it
unless it is pre-defined in the configuration file.

Make sure to remember the password for later use.
"""))
		_dbowner = user(anAlias = dbowner_alias)

		cmd = 'create user "%s" with password \'%s\' createdb createrole in group "%s", "gm-logins"' % (_dbowner.name, _dbowner.password, self.auth_group)
		try:
			cursor.execute(cmd)
		except:
			_log.error(">>>[%s]<<< failed." % cmd)
			_log.exception("Cannot create GNUmed database owner [%s]." % _dbowner.name)
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
			_log.error("Cannot load GNUmed group names from config file (section [%s])." % section)
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
		_log.info("bootstrapping database [%s]" % aDB_alias)

		self.section = "database %s" % aDB_alias

		# find database name
		overrider = cfg_get(self.section, 'override name by')
		if overrider is not None:
			self.name = os.getenv(overrider)
			if self.name is None:
				_log.info('environment variable [%s] is not set, using database name from config file' % overrider)
				self.name = cfg_get(self.section, 'name')
		else:
			self.name = cfg_get(self.section, 'name')

		if self.name is None or str(self.name).strip() == '':
			_log.error("Need to know database name.")
			raise ConstructorError, "database.__init__(): Cannot bootstrap database."

		# already bootstrapped ?
		global _bootstrapped_dbs
		if _bootstrapped_dbs.has_key(aDB_alias):
			if _bootstrapped_dbs[aDB_alias].name == self.name:
				_log.info("database [%s] already bootstrapped", self.name)
				return None

		# no, so bootstrap from scratch
		_log.info('bootstrapping database [%s] alias "%s"', self.name, aDB_alias)

		for db in _bootstrapped_dbs.values():
			if db.conn.closed == 0:
				db.conn.close()
		_bootstrapped_dbs = {}
		self.conn = None

		self.server_alias = cfg_get(self.section, "server alias")
		if self.server_alias is None:
			_log.error("Server alias missing.")
			raise ConstructorError, "database.__init__(): Cannot bootstrap database."

		self.template_db = cfg_get(self.section, "template database")
		if self.template_db is None:
			_log.error("Template database name missing.")
			raise ConstructorError, "database.__init__(): Cannot bootstrap database."

		# make sure server is bootstrapped
		db_server(self.server_alias, auth_group = self.name)
		self.server = _bootstrapped_servers[self.server_alias]

		if not self.__bootstrap():
			raise ConstructorError, "database.__init__(): Cannot bootstrap database."

		_bootstrapped_dbs[aDB_alias] = self

		return None
	#--------------------------------------------------------------
	def __bootstrap(self):
		global _dbowner

		# get owner
		if _dbowner is None:
			_dbowner = user(anAlias = cfg_get("GnuMed defaults", "database owner alias"))

		if _dbowner is None:
			_log.error("Cannot load GNUmed database owner name from config file.")
			return None

		# get owner
		self.owner = _dbowner

		# connect as owner to template
		if not self.__connect_superuser_to_template():
			_log.error("Cannot connect to template database.")
			return False

		# make sure db exists
		if not self.__create_db():
			_log.error("Cannot create database.")
			return False

		# reconnect as superuser to db
		if not self.__connect_superuser_to_db():
			_log.error("Cannot connect to database.")
			return None

		# create authentication group
		_log.info('creating database-specific authentication group role')
		curs = self.conn.cursor()
		if not create_db_group(cursor = curs, group = self.name):
			curs.close()
			_log.error('cannot create authentication group role')
			return False
		self.conn.commit()
		curs.close()

		# paranoia check
		curs = self.conn.cursor()
		if not db_group_exists(cursor = curs, group = self.name):
			curs.close()
			_log.error('cannot find authentication group role')
			return False
		curs.close()

		tmp = cfg_get(self.section, 'superuser schema')
		if tmp is not None:
			if not _import_schema(group=self.section, schema_opt='superuser schema', conn=self.conn):
				_log.error("cannot import schema definition for database [%s]" % (self.name))
				return False
		del tmp

		# transfer users
		if not self.transfer_users():
			_log.error("Cannot transfer users from old to new database.")
			return False

		# reconnect as owner to db
		if not self.__connect_owner_to_db():
			_log.error("Cannot connect to database.")
			return None
		if not _import_schema(group=self.section, schema_opt='schema', conn=self.conn):
			_log.error("cannot import schema definition for database [%s]" % (self.name))
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
			self.server.superuser.password
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
			self.server.superuser.password
		)

		self.conn.cookie = 'database.__connect_superuser_to_db'

		curs = self.conn.cursor()
		curs.execute(u'set default_transaction_read_only to off')
		# we need English messages to detect errors
		curs.execute(u"set lc_messages to 'C'")
		curs.execute(u"alter database %s set lc_messages to 'C'" % self.name)
		# we need inheritance or else things will fail miserably
		curs.execute("alter database %s set sql_inheritance to on" % self.name)
		# we want READ ONLY default transactions for maximum patient data safety
		curs.execute("alter database %s set default_transaction_read_only to on" % self.name)
		# we want checking of function bodies
		curs.execute("alter database %s set check_function_bodies to on" % self.name)
		curs.close()

		self.conn.commit()

		return self.conn and 1
	#--------------------------------------------------------------
	def __connect_owner_to_db(self):

		# reconnect as superuser to db
		if not self.__connect_superuser_to_db():
			_log.error("Cannot connect to database.")
			return False

		self.conn.cookie = 'database.__connect_owner_to_db via database.__connect_superuser_to_db'

		curs = self.conn.cursor()
		cmd = "set session authorization %(usr)s"
		curs.execute(cmd, {'usr': self.owner.name})
		curs.close()

		return self.conn and 1
	#--------------------------------------------------------------
	def __db_exists(self):
		cmd = "BEGIN; SELECT datname FROM pg_database WHERE datname='%s'" % self.name

		aCursor = self.conn.cursor()
		try:
			aCursor.execute(cmd)
		except:
			_log.exception(">>>[%s]<<< failed." % cmd)
			return None

		res = aCursor.fetchall()
		tmp = aCursor.rowcount
		aCursor.close()
		if tmp == 1:
			_log.info("Database [%s] exists." % self.name)
			return True

		_log.info("Database [%s] does not exist." % self.name)
		return None
	#--------------------------------------------------------------
	def __create_db(self):

		# verify template database hash
		template_version = cfg_get(self.section, 'template version')
		if template_version is None:
			_log.warning('cannot check template database identity hash, no version specified')
		else:
			if not gmPG2.database_schema_compatible(link_obj=self.conn, version=template_version):
				_log.error('invalid template database')
				return False

		# check for target database
		if self.__db_exists():
			drop_existing = bool(int(cfg_get(self.section, 'drop target database')))
			if drop_existing:
				print_msg("==> dropping pre-existing target database [%s] ..." % self.name)
				_log.info('trying to drop target database')
				cmd = 'drop database "%s"' % self.name
				self.conn.set_isolation_level(0)
				cursor = self.conn.cursor()
				try:
					cursor.execute(cmd)
				except:
					_log.exception(">>>[%s]<<< failed" % cmd)
					cursor.close()
					return False
				cursor.close()
				self.conn.commit()
			else:
				use_existing = bool(int(cfg_get(self.section, 'use existing target database')))
				if use_existing:
					# FIXME: verify that database is owned by "gm-dbo"
					print_msg("==> using pre-existing *target* database [%s] ..." % self.name)
					_log.info('using existing database [%s]', self.name)
					return True
				else:
					_log.info('not using existing database [%s]', self.name)
					return False

		tablespace = cfg_get(self.section, 'tablespace')
		if tablespace is None:
			cmd = """
				create database \"%s\" with
					owner = \"%s\"
					template = \"%s\"
					encoding = 'unicode'
				;""" % (self.name, self.owner.name, self.template_db)
		else:
			cmd = """
				create database \"%s\" with
					owner = \"%s\"
					template = \"%s\"
					encoding = 'unicode'
					tablespace = '%s'
				;""" % (self.name, self.owner.name, self.template_db, tablespace)

		# create database
		self.conn.set_isolation_level(0)
		cursor = self.conn.cursor()
		cursor.execute("select pg_size_pretty(pg_database_size('%s'))" % self.template_db)
		size = cursor.fetchone()[0]
		print_msg("==> cloning [%s] (%s) as target database [%s] ..." % (self.template_db, size, self.name))
		try:
			cursor.execute(cmd)
		except:
			_log.exception(">>>[%s]<<< failed" % cmd)
			cursor.close()
			return False
		cursor.close()
		self.conn.commit()

		if not self.__db_exists():
			return None
		_log.info("Successfully created GNUmed database [%s]." % self.name)
		return True
	#--------------------------------------------------------------
	def check_data_plausibility(self):

		print_msg("==> checking migrated data for plausibility ...")

		plausibility_queries = cfg_get(self.section, 'upgrade plausibility checks')
		if plausibility_queries is None:
			_log.warning('no plausibility checks defined')
			print_msg("    ... skipped (no checks defined)")
			return True

		no_of_queries, remainder = divmod(len(plausibility_queries), 2)
		if remainder != 0:
			_log.error('odd number of plausibility queries defined, aborting')
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

		for idx in range(no_of_queries):
			tag, old_query = plausibility_queries[idx*2].split('::::')
			new_query = plausibility_queries[(idx*2) + 1]
			try:
				rows, idx = gmPG2.run_ro_queries (
					link_obj = template_conn,
					queries = [{'cmd': unicode(old_query)}]
				)
				old_val = rows[0][0]
			except:
				_log.exception('error in plausibility check [%s] (old), aborting' % tag)
				print_msg("    ... failed (SQL error)")
				return False
			try:
				rows, idx = gmPG2.run_ro_queries (
					link_obj = target_conn,
					queries = [{'cmd': unicode(new_query)}]
				)
				new_val = rows[0][0]
			except:
				_log.exception('error in plausibility check [%s] (new), aborting' % tag)
				print_msg("    ... failed (SQL error)")
				return False

			if new_val != old_val:
				_log.error('plausibility check [%s] failed, expected [%s], found [%s]' % (tag, old_val, new_val))
				print_msg("    ... failed (check [%s])" % tag)
				return False

			_log.info('plausibility check [%s] succeeded' % tag)

		template_conn.close()
		target_conn.close()

		return True
	#--------------------------------------------------------------
	def check_holy_auth_line(self):

		holy_pattern = 'local.*samegroup.*\+gm-logins'

		conn = connect (
			self.server.name,
			self.server.port,
			self.name,
			self.server.superuser.name,
			self.server.superuser.password
		)
		conn.cookie = 'holy auth check connection'

		cmd = u"select setting from pg_settings where name = 'hba_file'"
		rows, idx = gmPG2.run_ro_queries(link_obj = conn, queries = [{'cmd': cmd}])
		conn.close()
		if len(rows) == 0:
			_log.info('cannot check pg_hba.conf for authentication information - not detectable in pg_settings')
			return

		hba_file = rows[0][0]
		_log.info('hba file: %s', hba_file)

		try:
			f = open(hba_file, 'r')
			f.close()
		except StandardError:
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
			_log.info('did not find standard GNUmed authentication directive in pg_hba.conf')
			_log.info('regex: %s' % holy_pattern)
			print_msg('==> sanity checking PostgreSQL authentication settings ...')
			print_msg('')
			print_msg('Note that even after successfully bootstrapping the GNUmed ')
			print_msg('database PostgreSQL may still need to be configured to')
			print_msg('allow GNUmed clients to connect to it.')
			print_msg('')
			print_msg('In many standard PostgreSQL installations this amounts to')
			print_msg('adding the authentication directive:')
			print_msg('')
			print_msg('  "local   samegroup   +gm-logins   md5"')
			print_msg('')
			print_msg('in the proper place of the file:')
			print_msg('')
			print_msg('  %s' % hba_file)
			print_msg('')
			print_msg('For details refer to the GNUmed documentation at:')
			print_msg('')
			print_msg('  http://wiki.gnumed.de/bin/view/Gnumed/ConfigurePostgreSQL')
			print_msg('')
	#--------------------------------------------------------------
	def import_data(self):
		print_msg("==> upgrading reference data sets ...")

		import_scripts = cfg_get(self.section, "data import scripts")
		if (import_scripts is None) or (len(import_scripts) == 0):
			_log.info('skipped data import: no scripts to run')
			print_msg("    ... skipped (no scripts to run)")
			return True

		script_base_dir = cfg_get(self.section, "script base directory")
		script_base_dir = os.path.expanduser(script_base_dir)
		script_base_dir = os.path.abspath(script_base_dir)

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
		# verify template database hash
		print_msg("==> verifying target database schema ...")
		target_version = cfg_get(self.section, 'target version')
		if gmPG2.database_schema_compatible(link_obj=self.conn, version=target_version):
			_log.info('database identity hash properly verified')
			return True
		_log.error('target database identity hash invalid')
		if target_version == 'devel':
			print_msg("    ... skipped (devel version)")
			_log.warning('testing/development only, not failing due to invalid target database identity hash')
			return True
		print_msg("    ... failed (hash mismatch)")
		return False
	#--------------------------------------------------------------
	def transfer_users(self):
		print_msg("==> transferring users ...")
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

		cmd = u"select gm.transfer_users('%s'::text)" % self.template_db
		try:
			rows, idx = gmPG2.run_rw_queries(link_obj = self.conn, queries = [{'cmd': cmd}], end_tx = True, return_data = True)
		except gmPG2.dbapi.ProgrammingError:
			# maybe an old database
			_log.info('problem running gm.transfer_users(), trying gm_transfer_users()')
			cmd = u"select gm_transfer_users('%s'::text)" % self.template_db
			rows, idx = gmPG2.run_rw_queries(link_obj = self.conn, queries = [{'cmd': cmd}], end_tx = True, return_data = True)

		if rows[0][0]:
			_log.info('users properly transferred from [%s] to [%s]' % (self.template_db, self.name))
			return True
		_log.error('error transferring user from [%s] to [%s]' % (self.template_db, self.name))
		print_msg("    ... failed")
		return False
	#--------------------------------------------------------------
	def bootstrap_auditing(self):
		print_msg("==> setting up auditing ...")
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
			_log.error('cannot generate audit trail schema for GNUmed database [%s]' % self.name)
			return None
		# write schema to file
		tmpfile = os.path.join(tempfile.gettempdir(), 'audit-trail-schema.sql')
		file = open(tmpfile, 'wb')
		for line in audit_schema:
			file.write("%s;\n" % line)
		file.close()

		# import auditing schema
		psql = gmPsql.Psql (self.conn)
		if psql.run (tmpfile) != 0:
			_log.error("cannot import audit schema definition for database [%s]" % (self.name))
			return None

		if _keep_temp_files:
			return True

		try:
			os.remove(tmpfile)
		except StandardError:
			_log.exception('cannot remove audit trail schema file [%s]' % tmpfile)
		return True
	#--------------------------------------------------------------
	def bootstrap_notifications(self):
		print_msg("==> setting up notifications ...")
		# get configuration
		tmp = cfg_get(self.section, 'notification disable')
		# if this option is not given, assume we want notification
		if tmp is not None:
			# if we don't want notification on these tables, return without error
			if int(tmp) == 1:
				print_msg('    ... skipped (disabled)')
				return True

		# create notification schema
		curs = self.conn.cursor()
		notification_schema = notify_gen.create_notification_schema(curs)
		notification_schema.extend(notify_gen.create_narrative_notification_schema(curs))
		curs.close()
		if notification_schema is None:
			_log.error('cannot generate notification schema for GNUmed database [%s]' % self.name)
			return None

		# write schema to file
		tmpfile = os.path.join(tempfile.gettempdir(), 'notification-schema.sql')
		file = open (tmpfile, 'wb')
		for line in notification_schema:
			file.write("%s;\n" % line)
		file.close()

		# import notification schema
		psql = gmPsql.Psql (self.conn)
		if psql.run(tmpfile) != 0:
			_log.error("cannot import notification schema definition for database [%s]" % (self.name))
			return None

		if _keep_temp_files:
			return True

		try:
			os.remove(tmpfile)
		except StandardError:
			_log.exception('cannot remove notification schema file [%s]' % tmpfile)
		return True
#==================================================================
class gmBundle:
	def __init__(self, aBundleAlias = None):
		# sanity check
		if aBundleAlias is None:
			raise ConstructorError, "Need to know bundle name to install it."

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
			database(aDB_alias = database_alias)
		except:
			_log.exception(u"Cannot bootstrap bundle [%s].", self.alias)
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

		if float(gmPG2.postgresql_version) < float(required_version):
			_log.error("Reported live PostgreSQL version [%s] is smaller than the required minimum version [%s]." % (gmPG2.postgresql_version, required_version))
			return None

		_log.info("installed PostgreSQL version: [%s] - this is fine with me" % gmPG2.postgresql_version)
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
	else:
		print "You are about to install the following parts of GNUmed:"
		print "-------------------------------------------------------"
		for bundle in bundles:
			db_alias = cfg_get("bundle %s" % bundle, "database alias")
			db_name = cfg_get("database %s" % db_alias, "name")
			srv_alias = cfg_get("database %s" % db_alias, "server alias")
			srv_name = cfg_get("server %s" % srv_alias, "name")
			print 'bundle "%s" in <%s> (or overridden) on <%s>' % (bundle, db_name, srv_name)
		print "-------------------------------------------------------"
		desc = cfg_get("installation", "description")
		if desc is not None:
			for line in desc:
				print line

		print "Do you really want to install this database setup ?"
		answer = raw_input("Type yes or no: ")
		if answer == "yes":
			return True
		else:
			return None
	return True
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
	for file in schema_files:
		the_file = os.path.join(schema_base_dir, file)
		if psql.run(the_file) == 0:
			_log.info('successfully imported [%s]' % the_file)
		else:
			_log.error('failed to import [%s]' % the_file)
			return None
	return True
#------------------------------------------------------------------
def exit_with_msg(aMsg = None):
	if aMsg is not None:
		print aMsg
	print ''
	print "Please check the log file for details:"
	print ''
	print ' ', gmLog2._logfile_name
	print ''

	_log.error(aMsg)
 	_log.info("shutdown")
	sys.exit(1)
#------------------------------------------------------------------
def print_msg(msg=None):
	if quiet:
		return
	print msg
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
		_log.info('running as user [%s]' % running_as)
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
		_log.info('switching to UNIX user [%s]' % pg_demon_user_passwd_line[0])
		os.setuid(pg_demon_user_passwd_line[2])

	elif running_as == pg_demon_user_passwd_line[0]: # we are the postgres user already
		_log.info('I already am the UNIX user [%s]' % pg_demon_user_passwd_line[0])

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

	_log.info('config file: %s', _cfg.source_files['file'])
	_log.info('SCM path: %s', cfg_get("revision control", "file"))
	_log.info('file version: %s', cfg_get("revision control", "version"))

	become_pg_demon_user()

	tmp = cfg_get("installation", "interactive")
	global _interactive
	if tmp == "yes":
		_interactive = True
	elif tmp == "no":
		_interactive = False

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
		_log.error("no config file specified on command line")
		exit_with_msg('Cannot bootstrap without config file. Use --conf-file=<FILE>.')

	_log.info('initial config file: %s', cfg_file)

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
		_log.info('single-shot config file')
		handle_cfg()
	else:
		_log.info('aggregation of config files')
		for cfg_file in cfg_files:
			# read that conf file
			_cfg.add_file_source (
				source = 'file',
				file = cfg_file
			)
			handle_cfg()

	global _bootstrapped_dbs

	# verify result hash
	db = _bootstrapped_dbs[_bootstrapped_dbs.keys()[0]]
	if not db.verify_result_hash():
		exit_with_msg("Bootstrapping failed: wrong result hash")

	if not db.check_data_plausibility():
		exit_with_msg("Bootstrapping failed: plausibility checks inconsistent")

#	if not db.import_data():
#		exit_with_msg("Bootstrapping failed: unable to import data")

	db.check_holy_auth_line()

	for conn in conn_ref_count:
		if conn.closed == 0:
			_log.warning('open connection detected: %s', conn.cookie)
			_log.warning('%s', conn)
			_log.warning('closing connection')
			conn.close()

	_log.info("shutdown")
	print("Done bootstrapping GNUmed database: We very likely succeeded.")

#==================================================================
if __name__ == "__main__":

	gmI18N.activate_locale()
	gmLog2.set_string_encoding()

	_log.info("startup (%s)" % __version__)

	try:
		main()
	except StandardError:
		for c in conn_ref_count:
			if c.closed == 0:
				print 'closing open connection from:', c.cookie
				print c
				c.close()
		_log.exception('unhandled exception caught')
		exit_with_msg("Bootstrapping failed: unhandled exception occurred")

	sys.exit(0)
else:
	print "This currently is not intended to be used as a module."
	sys.exit(1)

#==================================================================
#	pipe = popen2.Popen3(cmd, 1==1)
#	pipe.tochild.write("%s\n" % aPassword)
#	pipe.tochild.flush()
#	pipe.tochild.close()

#	result = pipe.wait()
#	print result

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

