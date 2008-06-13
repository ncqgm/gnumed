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
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/bootstrap/bootstrap_gm_db_system.py,v $
__version__ = "$Revision: 1.82 $"
__author__ = "Karsten.Hilbert@gmx.net"
__license__ = "GPL"

# standard library
import sys, string, os.path, fileinput, os, time, getpass, glob, re, tempfile, logging


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
def connect (host, port, db, user, passwd, superuser=0):
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

	conn = None
	dsn = gmPG2.make_psycopg2_dsn(database=db, host=host, port=port, user=user, password=passwd)
	_log.info("trying DB connection to %s on %s as %s", db, host or 'localhost', user)
	try:
		conn = gmPG2.get_connection(dsn=dsn, readonly=False, pooled=False, verbose=True)
		cached_host = (host, port) # learn from past successes
		cached_passwd[user] = passwd
		_log.info('successfully connected')

	except gmPG2.cAuthenticationError:
		_log.critical('authentication error')
		_log.exception("password not accepted, retrying")
		passwd = getpass.getpass("I need the correct password for the GNUmed database user [%s].\nPlease type password: " % user)
		conn = connect (host, port, db, user, passwd)

	except gmPG2.dbapi.OperationalError, e:
		_log.critical('operational error')
		_log.exception('connection failed')

		t, v, tb = sys.exc_info()
		try:
			msg = e.args[0]
		except (AttributeError, IndexError, TypeError):
			raise

		m = unicode(msg, gmI18N.get_encoding(), 'replace')

		if re.search ("^FATAL:  No pg_hba.conf entry for host.*", m):
			# this pretty much means we're screwed
			if _interactive:
				print_msg(pg_hba_sermon)
		elif re.search ("no password supplied", m):
			# didn't like blank password trick
			_log.warning("attempt w/ blank password failed, retrying with password")
			passwd = getpass.getpass ("I need the password for the GNUmed database user [%s].\nPlease type password: " % user)
			conn = connect (host, port, db, user, passwd)
		elif re.search ("could not connect to server", m):
			if len(host) == 0:
				# try again on TCP/IP loopback
				_log.warning("UNIX socket connection failed, retrying on 127.0.0.1")
				conn = connect ("127.0.0.1", port, db, user, passwd)
			else:
				_log.warning("connection to host %s:%s failed" % (host, port))
				if _interactive:
					print_msg(no_server_sermon)
					host = raw_input("New host to connect to:")
					if len(host) > 0:
						host.split(':')
						if len(host) > 1:
							port = host[1]
							host = host[0]
						else:
							host = host[0]
							conn = connect (host, port, db, user, password)
		else:
			if _interactive:
				print_msg(no_clues % (message, sys.platform))

	except:
		_log.critical('other connect-related error')
		_log.exception(u'connection failed')
		raise

#	except gmPG2.dbapi.OperationalError, message:
#		_log.exception('connection failed')
#		m = str(message)
#		if re.search ("^FATAL:  No pg_hba.conf entry for host.*", m):
#			# this pretty much means we're screwed
#			if _interactive:
#				print_msg(pg_hba_sermon)
#		elif re.search ("no password supplied", m):
#			# didn't like blank password trick
#			_log.warning("attempt w/ blank password failed, retrying with password")
#			passwd = getpass.getpass ("I need the password for the GNUmed database user [%s].\nPlease type password: " % user)
#			conn = connect (host, port, db, user, passwd)
#		elif re.search ("^FATAL:.*Password authentication failed.*", m):
#			# didn't like supplied password
#			_log.warning("password not accepted, retrying")
#			passwd = getpass.getpass ("I need the correct password for the GNUmed database user [%s].\nPlease type password: " % user)
#			conn = connect (host, port, db, user, passwd)
#		elif re.search ("could not connect to server", m):
#			if len(host) == 0:
#				# try again on TCP/IP loopback
#				_log.warning("UNIX socket connection failed, retrying on 127.0.0.1")
#				conn = connect ("127.0.0.1", port, db, user, passwd)
#			else:
#				_log.warning("connection to host %s:%s failed" % (host, port))
#				if _interactive:
#					print_msg(no_server_sermon)
#					host = raw_input("New host to connect to:")
#					if len(host) > 0:
#						host.split(':')
#						if len(host) > 1:
#							port = host[1]
#							host = host[0]
#						else:
#							host = host[0]
#							conn = connect (host, port, db, user, password)
#		elif re.search ("^FATAL:.*IDENT authentication failed.*", m):
#			if _interactive:
#				if superuser:
#					print_msg(superuser_sermon % user)
#				else:
#					print_msg(pg_hba_sermon)
#		else:
#			if _interactive:
#				print_msg(no_clues % (message, sys.platform))

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
					self.password = getpass.getpass("I need the password for the GNUmed database user [%s].\nPlease type password: " % self.name)
				else:
					_log.warning('password for database user [%s] set to empty string' % self.name)

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

		self.conn = connect (self.name, self.port, self.template_db, self.superuser.name, self.superuser.password)
		if self.conn is None:
			_log.error('Cannot connect.')
			return None

		curs = self.conn.cursor()
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
		if self.__create_groups() is None:
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
	def __user_exists(self, aCursor, aUser):
		cmd = "SELECT usename FROM pg_user WHERE usename = '%s'" % aUser
		try:
			aCursor.execute(cmd)
		except:
			_log.exception(">>>[%s]<<< failed." % cmd)
			return None
		res = aCursor.fetchone()
		if aCursor.rowcount == 1:
			_log.info("User [%s] exists." % aUser)
			return True
		_log.info("User [%s] does not exist." % aUser)
		return None
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
		if self.__user_exists(cursor, name):
			cmd = 'alter group "gm-logins" add user "%s"; alter group "gm-logins" add user "%s"; alter group "%s" add user "%s"' % (self.superuser.name, name, self.auth_group, name)
			try:
				cursor.execute(cmd)
			except:
				_log.error(">>>[%s]<<< failed." % cmd)
				_log.exception("Cannot add GNUmed database owner [%s] to groups [gm-logins] and [%s]." % (name, self.auth_group))
				cursor.close()
				return False
			self.conn.commit()
			cursor.close()
			print_msg("")
			print_msg("The database owner already exists.")
			print_msg("Please provide the password previously used for it.")
			print_msg("")
			_dbowner = user(anAlias = dbowner_alias)
			return True

		print_msg((
"""The database owner will be created.
You will have to provide a new password for it
unless it is pre-defined in the configuration file.

Make sure to remember the password for later use.
"""))
		_dbowner = user(anAlias = dbowner_alias)

		cmd = 'create user "%s" with password \'%s\' createdb in group "%s", "gm-logins"' % (_dbowner.name, _dbowner.password, self.auth_group)
		try:
			cursor.execute(cmd)
		except:
			_log.error(">>>[%s]<<< failed." % cmd)
			_log.exception("Cannot create GNUmed database owner [%s]." % _dbowner.name)
			cursor.close()
			return None

		# paranoia is good
		if not self.__user_exists(cursor, _dbowner.name):
			cursor.close()
			return None

		self.conn.commit()
		cursor.close()
		return True
	#--------------------------------------------------------------
	def __group_exists(self, aCursor, aGroup):
		cmd = "SELECT groname FROM pg_group WHERE groname = '%s'" % aGroup
		try:
			aCursor.execute(cmd)
		except:
			_log.exception(">>>[%s]<<< failed." % cmd)
			return False
		res = aCursor.fetchone()
		if aCursor.rowcount == 1:
			_log.info("Group %s exists." % aGroup)
			return True
		_log.info("Group %s does not exist." % aGroup)
		return False
	#--------------------------------------------------------------
	def __create_group(self, aCursor, aGroup):
		# does this group already exist ?
		if self.__group_exists(aCursor, aGroup):
			return True

		cmd = 'create group "%s"' % aGroup
		try:
			aCursor.execute(cmd)
		except:
			_log.exception(">>>[%s]<<< failed." % cmd)
			return False

		# paranoia is good
		if not self.__group_exists(aCursor, aGroup):
			return False

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
			return None
		groups.append(self.auth_group)

		cursor = self.conn.cursor()
		for group in groups:
			if not self.__create_group(cursor, group):
				cursor.close()
				return False

		self.conn.commit()
		cursor.close()
		return True
#==================================================================
class database:
	def __init__(self, aDB_alias):
		_log.info("bootstrapping database [%s]" % aDB_alias)

		global _bootstrapped_dbs

		if _bootstrapped_dbs.has_key(aDB_alias):
			_log.info("database [%s] already bootstrapped" % aDB_alias)
			return None

		self.conn = None
		self.section = "database %s" % aDB_alias

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
			return None

		# make sure db exists
		if not self.__create_db():
			_log.error("Cannot create database.")
			return False

		# reconnect as superuser to db
		if not self.__connect_superuser_to_db():
			_log.error("Cannot connect to database.")
			return None
		if not _import_schema(group=self.section, schema_opt='superuser schema', conn=self.conn):
			_log.error("cannot import schema definition for database [%s]" % (self.name))
			return None

		# transfer users
		if not self.tranfer_users():
			_log.error("Cannot transfer users from old to new database.")
			return None

		# reconnect as owner to db
		if not self.__connect_owner_to_db():
			_log.error("Cannot connect to database.")
			return None
		if not _import_schema(group=self.section, schema_opt='schema', conn=self.conn):
			_log.error("cannot import schema definition for database [%s]" % (self.name))
			return None

		return True
	#--------------------------------------------------------------
	def __connect_superuser_to_template(self):
		if self.conn is not None:
			self.conn.close()

		self.conn = connect (
			self.server.name,
			self.server.port,
			self.template_db,
			self.server.superuser.name,
			self.server.superuser.password
		)

		curs = self.conn.cursor()
		curs.execute(u"set lc_messages to 'C'")
		curs.close()

		return self.conn and 1
	#--------------------------------------------------------------
	def __connect_superuser_to_db(self):
		if self.conn is not None:
			self.conn.close()

		self.conn = connect (
			self.server.name,
			self.server.port,
			self.name,
			self.server.superuser.name,
			self.server.superuser.password
		)

		curs = self.conn.cursor()
		# we need English messages to detect errors
		curs.execute(u"set lc_messages to 'C'")
		curs.execute(u"alter database %s set lc_messages to 'C'" % self.name)
		# we need inheritance or else things will fail miserably
		curs.execute("alter database %s set sql_inheritance to on" % self.name)
		# we want READ ONLY default transactions for maximum patient data safety
		curs.execute("alter database %s set default_transaction_read_only to on" % self.name)
		curs.close()

		return self.conn and 1
	#--------------------------------------------------------------
	def __connect_owner_to_db(self):

		# reconnect as superuser to db
		if not self.__connect_superuser_to_db():
			_log.error("Cannot connect to database.")
			return False

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
		if self.__db_exists():
			# FIXME: verify that database is owned by "gm-dbo"
			drop_existing = bool(cfg_get(self.section, 'drop target database'))
			if drop_existing:
				print_msg("==> dropping pre-existing *target* database [%s] ..." % self.name)
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
				return False

		# verify template database hash
		template_version = cfg_get(self.section, 'template version')
		if template_version is None:
			_log.warning('cannot check template database identity hash, no version specified')
		else:
			if not gmPG2.database_schema_compatible(link_obj=self.conn, version=template_version):
				_log.error('invalid template database')
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
		print_msg("==> creating new target database [%s] ..." % self.name)
		print_msg("    (this can take a while if [%s] is large)" % self.template_db)
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
		target_conn = connect (
			self.server.name,
			self.server.port,
			self.name,
			self.server.superuser.name,
			self.server.superuser.password
		)

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

		return True
	#--------------------------------------------------------------
	def import_data(self):
		print_msg("==> upgrading reference data sets ...")

		import_scripts = cfg_get(self.section, "data import scripts")
		if (import_scripts is None) or (len(import_scripts) == 0):
			_log.info('skipped data import: no scripts to run')
			print_msg("    ... skipped (no scripts to run)")
			return True

		script_base_dir = cfg_get(self.section, "script base directory")
		script_base_dir = os.path.abspath(os.path.expanduser(script_base_dir))

		for import_script in import_scripts:
			try:
				script = gmTools.import_module_from_directory(module_path = script_base_dir, module_name = import_script)
			except ImportError:
				print_msg("    ... failed (cannot load script [%s])" % import_script)
				_log.error('cannot load data set import script [%s/%s]' % (script_base_dir, import_script))
				return False

			try:
				script.run(conn=self.conn)
			except:
				print_msg("    ... failed (cannot run script [%s])" % import_script)
				_log.exception('cannot run import script [%s]' % import_script)
				return False

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
	def tranfer_users(self):
		print_msg("==> transferring users ...")
		transfer_users = cfg_get(self.section, 'transfer users')
		if transfer_users is None:
			_log.info('user transfer not defined')
			print_msg("    ... skipped (unconfigured)")
			return True
		transfer_users = int(transfer_users)
		if not transfer_users:
			_log.info('configured to not transfer users')
			print_msg("    ... skipped (disabled)")
			return True
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
	psql = gmPsql.Psql (conn)
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
	print "Please check the log file for details."

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

	# verify result hash
	db = _bootstrapped_dbs[_bootstrapped_dbs.keys()[0]]
	if not db.verify_result_hash():
		exit_with_msg("Bootstrapping failed: wrong result hash")

	if not db.check_data_plausibility():
		exit_with_msg("Bootstrapping failed: plausibility checks inconsistent")

	if not db.import_data():
		exit_with_msg("Bootstrapping failed: unable to import data")

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
# $Log: bootstrap_gm_db_system.py,v $
# Revision 1.82  2008-06-13 10:37:26  ncq
# - fiddle with connect exception logging
#
# Revision 1.81  2008/06/13 10:33:56  ncq
# - log all connect related exceptions
#
# Revision 1.80  2008/06/11 19:13:22  ncq
# - improve exception logging on connect()
# - recall gmLog2.set_string_encoding appropriately
#
# Revision 1.79  2008/05/31 16:30:35  ncq
# - verbose connect
#
# Revision 1.78  2008/04/25 10:45:11  ncq
# - activate_locale() so bootstrapping v2 works on systems
#   with ASCII default encoding
#
# Revision 1.77  2008/04/11 12:31:00  ncq
# - bootstrap notification on clin.clin_root_item children
#
# Revision 1.76  2008/03/11 17:01:14  ncq
# - mention command line options in doc string
#
# Revision 1.75  2008/03/06 23:19:38  ncq
# - support --quiet
#
# Revision 1.74  2008/02/25 19:39:48  ncq
# - better output
#
# Revision 1.73  2008/01/07 14:15:43  ncq
# - port to gmCfg2/gmLog2
# - create database with default transaction mode set to readonly
#
# Revision 1.72  2007/12/26 18:38:56  ncq
# - default lc_messages to C on new databases
#
# Revision 1.71  2007/12/26 12:37:27  ncq
# - force version into float to make comparison work
#
# Revision 1.70  2007/12/11 12:44:11  ncq
# - less console verbosity
#
# Revision 1.69  2007/12/04 15:24:38  ncq
# - set database default sql_inheritance to on
#
# Revision 1.68  2007/12/03 20:48:46  ncq
# - better wording in log
#
# Revision 1.67  2007/11/09 14:42:37  ncq
# - announce disabled notification and auditing DDL generation
# - don't consider sys.exit() a fatal exception though it throws SystemExit
#
# Revision 1.66  2007/11/02 14:01:23  ncq
# - signal non-successful bootstrap on user abort which, after all, it is
# - signal explicit success in exit code on normal shutdown
#
# Revision 1.65  2007/10/22 12:33:48  ncq
# - improve output
#
# Revision 1.64  2007/10/19 12:54:47  ncq
# - add TODO
#
# Revision 1.63  2007/10/09 11:22:48  ncq
# - improved wording
#
# Revision 1.62  2007/10/09 10:26:52  ncq
# - improved wording
# - improved logging
# - improved error handling during data set upgrade
#
# Revision 1.61  2007/10/08 12:57:24  ncq
# - improved info messages
#
# Revision 1.60  2007/09/24 22:04:25  ncq
# - improved logging
#
# Revision 1.59  2007/09/24 21:15:17  ncq
# - cope with missing "data import scripts" option
#
# Revision 1.58  2007/09/18 22:54:00  ncq
# - implement running data import scripts
#
# Revision 1.57  2007/07/13 20:54:05  ncq
# - fix missing %
#
# Revision 1.56  2007/07/03 15:51:47  ncq
# - announce creating of target database and comment that it
#   can take a while if the template (source) database is large
#
# Revision 1.55  2007/06/15 14:37:57  ncq
# - force lc_messages to 'C' so that we don't encounter
#   the dreaded "ERROR_STACK_SIZE exceeded" error
#
# Revision 1.54  2007/04/20 08:31:04  ncq
# - honor GM_DB_PORT environment variable
#
# Revision 1.53  2007/04/11 14:53:49  ncq
# - better console output
#
# Revision 1.52  2007/04/07 22:48:00  ncq
# - improved console output
#
# Revision 1.51  2007/04/02 18:42:14  ncq
# - better console output
#
# Revision 1.50  2007/04/02 15:18:21  ncq
# - transfer users
# - cleanup
# - run plausibility checks on data after upgrade
#
# Revision 1.49  2007/03/26 16:10:17  ncq
# - syntax error fix
#
# Revision 1.48  2007/03/23 12:43:02  ncq
# - don't blank out port on UNIX domain socket conns as it is
#   needed for building the proper socket file name (at least on Debian)
# - don't warn on not running as root if we already are postgres
#
# Revision 1.47  2007/02/18 12:19:52  ncq
# - support dropping target database if so configured
#
# Revision 1.46  2007/02/16 11:08:18  ncq
# - re-implement 7.4 "alternate location" as 8.1+ "tablespace" as
#   it doesn't make sense to support 7.4 on this
#
# Revision 1.45  2007/02/06 12:13:16  ncq
# - properly set _interactive if handling more than one conf
# - show a little more confidence in our result now that we use hashes
#
# Revision 1.44  2007/01/29 13:02:36  ncq
# - avoid the need for gm-dbo to be able to connect to the
#   template and the newly created database so we don't need
#   *pre*-installation changes to pg_hba.conf anymore
# - log the fact when the template database version is not specified
#
# Revision 1.43  2007/01/04 22:53:42  ncq
# - support verifying result hash
#
# Revision 1.42  2007/01/03 11:54:58  ncq
# - add verifying result hash after bootstrapping
#
# Revision 1.41  2007/01/02 19:48:10  ncq
# - cleanup
#
# Revision 1.40  2007/01/02 19:14:39  ncq
# - verify template database hash if so configured (useful for upgrades)
#
# Revision 1.39  2006/12/29 16:30:08  ncq
# - no more "services", only "bundles"
# - fix PG version checking
#
# Revision 1.38  2006/12/29 14:01:42  ncq
# - factor out proc lang bootstrapping into SQL script
#
# Revision 1.37  2006/12/18 13:00:48  ncq
# - remove some gmPG leftovers
#
# Revision 1.36  2006/12/12 13:15:11  ncq
# - support alternate database locations
#
# Revision 1.35  2006/12/06 16:09:34  ncq
# - port to gmPG2
#
# Revision 1.34  2006/11/07 00:37:06  ncq
# - don't use _log before it's set up
#
# Revision 1.33  2006/09/21 19:49:16  ncq
# - add database superuser to "gm-logins"
#
# Revision 1.32  2006/09/17 07:02:00  ncq
# - we don't register services anymore
#
# Revision 1.31  2006/07/27 17:10:06  ncq
# - remove trying to load *other* DB-API adapters
# - remove obsolete import
#
# Revision 1.30  2006/06/14 14:35:01  ncq
# - use 8.1 and post-7.4 language installation features
#
# Revision 1.29  2006/06/09 14:43:35  ncq
# - improve function naming
#
# Revision 1.28  2006/05/08 12:39:30  ncq
# - documented, sane handling of password option in config file
#
# Revision 1.27  2006/04/23 15:12:17  ncq
# - cleanup
# - use os.path.join() to properly join paths on different OSs
#
# Revision 1.26  2006/04/21 15:28:59  shilbert
# - got rid of some surplus '/'
#
# Revision 1.25  2006/04/21 15:25:23  shilbert
# - got rid of some hardcoded path statements
#
# Revision 1.24  2006/04/19 20:48:32  ncq
# - try a better way of running "create database"
#
# Revision 1.23  2006/04/19 20:13:34  ncq
# - improve wording, improve error logging
#
# Revision 1.22  2006/02/02 18:43:43  ncq
# - add missing commit()
#
# Revision 1.21  2006/02/02 16:19:09  ncq
# - improve checking for existing/non-existing gm-dbo
# - enable infrastructure for database-only GNUmed user adding
#
# Revision 1.20  2006/01/03 11:27:52  ncq
# - log user we are actually running as
#
# Revision 1.19  2005/12/27 19:07:11  ncq
# - improve wording
#
# Revision 1.18  2005/12/06 17:33:34  ncq
# - improved question layout
#
# Revision 1.17  2005/12/05 22:21:38  ncq
# - brush up gm-dbo password request text as suggested by Richard
#
# Revision 1.16  2005/12/04 09:32:55  ncq
# - *_schema -> *_ddl
#
# Revision 1.15  2005/11/19 13:25:18  ncq
# - some string cleanup
#
# Revision 1.14  2005/11/18 15:47:16  ncq
# - need to use cfg.* schema now
#
# Revision 1.13  2005/11/09 14:19:01  ncq
# - bootstrap languages per database, not per server
#
# Revision 1.12  2005/10/24 19:36:27  ncq
# - some explicit use of public.* schema qualification
#
# Revision 1.11  2005/10/19 11:23:47  ncq
# - comment on proc lang creation
#
# Revision 1.10  2005/09/24 23:28:41  ihaywood
# make __db_exists () work on my box
# please test this.
#
# Revision 1.9  2005/09/24 23:16:55  ihaywood
# fix for UNIX local socket connections
#
# Revision 1.8  2005/09/13 11:48:59  ncq
# - remove scoring support for good
# - seperate server level template database from database
#   to use as template for creating new database thus enabling
#   great things when updating a database schema :-)
# - return 1 -> return True
#
# Revision 1.7  2005/07/14 21:26:16  ncq
# - cleanup, better logging/strings
#
# Revision 1.6  2005/06/01 23:17:43  ncq
# - support overriding target database name via environment variable
#
# Revision 1.5  2005/04/02 22:08:00  ncq
# - comment out scoring bootstrapping
# - bootstrap several conf files in one go
#
# Revision 1.4  2005/03/31 20:07:58  ncq
# - slightly improved wording
#
# Revision 1.3  2005/01/24 17:22:15  ncq
# - Ian downgraded the severity on libpq warnings on create database
#
# Revision 1.2  2005/01/12 14:47:48  ncq
# - in DB speak the database owner is customarily called dbo, hence use that
#
# Revision 1.1  2004/12/18 13:02:49  ncq
# - as per Ian's request
#
# Revision 1.62  2004/12/18 09:59:11  ncq
# - comments added
#
# Revision 1.61  2004/11/24 16:03:58  ncq
# - need True/False from gmPyCompat, too
#
# Revision 1.60  2004/11/24 15:37:12  ncq
# - honor option "keep temp files"
#
# Revision 1.59  2004/06/28 13:31:17  ncq
# - really fix imports, now works again
#
# Revision 1.58  2004/06/28 13:23:20  ncq
# - fix import statements
#
# Revision 1.57  2004/06/23 21:10:48  ncq
# - cleanup become_demon_user()
#
# Revision 1.56  2004/06/14 18:58:06  ncq
# - cleanup
# - fix "return self.conn and 1" in self.__connect_to_srv_template()
#   which in some Python versions doesn't evaluate to TRUE,
#   bug reported by Michael Bonert
#
# Revision 1.55  2004/05/24 14:07:59  ncq
# - after understanding Ian's clever hack with nice_mode()
#   I renamed some methods and variables so people like me
#   will hopefully stay clued in later on ;-)
#
# Revision 1.54  2004/03/14 22:32:04  ncq
# - postgres version -> minimum postgresql version
#
# Revision 1.53  2004/03/09 10:45:02  ncq
# - typo fix
# - gmFormDefs now merged with gmReference.sql
#
# Revision 1.52  2004/03/09 08:14:06  ncq
# - call helper shell script to regenerate AU postcodes
#
# Revision 1.51  2004/03/04 19:40:50  ncq
# - micro-optimize become_pg_demon_user()
#
# Revision 1.50  2004/03/02 10:22:30  ihaywood
# support for martial status and occupations
# .conf files now use host autoprobing
#
# Revision 1.49  2004/02/25 09:46:36  ncq
# - import from pycommon now, not python-common
#
# Revision 1.48  2004/02/24 11:02:29  ihaywood
# Nice mode added
# If script started with no parameters, scans directory and presents menu of configs
# Tries hard to connect to local database.
#
# Revision 1.47  2004/02/22 11:19:22  ncq
# - set_user() -> become_pg_demon_user()
#
# Revision 1.46  2004/02/13 10:21:39  ihaywood
# Calls setuid () to postgres user if possible
#
# Revision 1.45  2004/01/14 10:47:43  ncq
# - stdout readability
#
# Revision 1.44  2004/01/06 23:44:40  ncq
# - __default__ -> xxxDEFAULTxxx
#
# Revision 1.43  2004/01/05 01:36:42  ncq
# - "commit, create db, begin" is the correct sequence, don't start with an extra begin
#
# Revision 1.42  2004/01/05 00:56:12  ncq
# - fixed typo, better feedback on console
#
# Revision 1.41  2003/12/29 15:20:42  uid66147
# - mini cleanup
#
# Revision 1.40  2003/12/02 00:20:37  ncq
# - deconfuse user on service names
#
# Revision 1.39  2003/12/02 00:10:20  ncq
# - be slightly more talkative on the console
#
# Revision 1.38  2003/11/28 10:00:41  ncq
# - add "notification disable" option
# - update template conf file
# - use notification schema generator in bootstrapper
#
# Revision 1.37  2003/11/02 13:29:49  ncq
# - don't close connections that are gone already in __del__
#
# Revision 1.36  2003/11/02 12:48:55  ncq
# - add schema base directory option to config files
# - hence we don't need the sql link anymore
#
# Revision 1.35  2003/11/02 11:28:43  ncq
# - merge with Ian's changes:
#   - support "schema base directory" in config file
#   - re-add commented out old _import_schema_file code, we can drop it later
#
# Revision 1.34  2003/11/02 10:11:17  ihaywood
# Psql in Python
#
# Revision 1.33  2003/10/26 18:03:28  ncq
# - cleanup temp files
#
# Revision 1.32  2003/10/25 17:07:30  ncq
# - import libpq from pyPgSQL
#
# Revision 1.31  2003/10/25 16:58:40  ncq
# - fix audit trigger function generation omitting target column names
#
# Revision 1.30  2003/10/25 08:13:01  ncq
# - conn.version() is non-standard, fix for non-providers
#
# Revision 1.29  2003/10/19 12:57:19  ncq
# - add scoring schema generator and use it
#
# Revision 1.28  2003/10/19 12:30:02  ncq
# - add score schema generation
# - remove generated schema files after successful import
#
# Revision 1.27  2003/10/09 14:53:09  ncq
# - consolidate localhost and '' to mean UNIX domain socket connection
#
# Revision 1.26  2003/10/01 16:18:17  ncq
# - remove audit_mark reference
#
# Revision 1.25  2003/08/26 14:11:13  ncq
# - add option to disable checking for proc lang library files on remote machines
#
# Revision 1.24  2003/08/26 12:58:55  ncq
# - coding style cleanup
#
# Revision 1.23  2003/08/26 10:52:52  ihaywood
# bugfixes to bootstrap scripts
#
# Revision 1.22  2003/08/24 13:46:32  hinnef
# added audit disable option to omit audit table generation
#
# Revision 1.21  2003/08/17 00:09:37  ncq
# - add auto-generation of missing audit trail tables
# - use that
#
# Revision 1.20  2003/07/05 15:10:20  ncq
# - added comment on Win2k quirk (os.WIFEXITED), thanks to Manfred
# - slightly betterified comments on gm-dbowner creation
#
# Revision 1.19  2003/07/05 12:53:29  ncq
# - actually use ";"s correctly (verified)
#
# Revision 1.18  2003/06/27 08:52:14  ncq
# - remove extra ; in SQL statements
#
# Revision 1.17  2003/06/12 08:43:57  ncq
# - the *shell* psql is running in, must have an encoding
#   compatible with the *database* encoding, I'm not sure I
#   understand why
#
# Revision 1.16  2003/06/11 13:39:47  ncq
# - leave out -h in local connects
# - use blank hostname in DSN for local connects
#
# Revision 1.15  2003/06/10 10:00:09  ncq
# - fatal= -> verbose=
# - some more comments re Debian/auth/FIXMEs
# - don't fail on libpq.Warning as suggested by Andreas Tille
#
# Revision 1.14  2003/06/03 13:47:38  ncq
# - fix grammar
#
# Revision 1.13  2003/05/26 13:53:28  ncq
# - slightly changed semantics for passwords:
#   - no option: ask user or die
#   - option set to empty: assume NONE password for IDENT/TRUST connect
#
# Revision 1.12  2003/05/22 12:53:41  ncq
# - add automatic audit trail generation
# - add options for that
#
# Revision 1.11  2003/05/12 12:47:25  ncq
# - import some schema files at the database level, too
# - add corresponding schema list in the config files
#
# Revision 1.10  2003/05/06 13:05:54  ncq
# - from now on create unicode databases
#
# Revision 1.9  2003/04/09 13:55:51  ncq
# - some whitespace fixup
#
# Revision 1.8  2003/04/09 13:07:19  ncq
# - clarification
#
# Revision 1.7  2003/04/04 11:06:25  ncq
# - explain what gm-dbowner is all about and what to provide for its password
#
# Revision 1.6  2003/04/03 13:24:43  ncq
# - modified message about succeeding
#
# Revision 1.5  2003/03/23 21:04:44  ncq
# - fixed faulty English
#
# Revision 1.4  2003/03/23 03:51:27  ncq
# - fail gracefully on missing config file
#
# Revision 1.3  2003/02/27 09:20:58  ncq
# - added TODO
#
# Revision 1.2  2003/02/25 08:29:25  ncq
# - added one more line so people are urged to check the log on failures
#
# Revision 1.1  2003/02/25 08:26:49  ncq
# - moved here from server/utils/
#
# Revision 1.25  2003/02/23 19:07:06  ncq
# - moved language library dirs to [GNUmed defaults]
#
# Revision 1.24  2003/02/14 00:43:39  ncq
# - fix whitespace
#
# Revision 1.23  2003/02/11 18:16:05  ncq
# - updated comments, added explanation about table config (db, ...)
#
# Revision 1.22  2003/02/11 17:11:41  hinnef
# fixed some bugs in service.register()
#
# Revision 1.21  2003/02/09 11:46:11  ncq
# - added core database option for registering services
# - convenience function _run_query()
#
# Revision 1.20  2003/02/09 10:10:05  hinnef
# - get passwd without writing to the terminal
# - services are now registered in service config (core database)
#
# Revision 1.19  2003/02/04 12:21:19  ncq
# - make server level schema import really work
#
# Revision 1.18  2003/01/30 18:47:04  ncq
# - emit some half-cryptic utterance about the need for "modules"
#   and "sql" links pointing to the appropriate places
#
# Revision 1.17  2003/01/30 16:30:37  ncq
# - updated docstring, added TODO item
#
# Revision 1.16  2003/01/30 09:05:08  ncq
# - it finally works as advertised
#
# Revision 1.15  2003/01/30 07:55:01  ncq
# - yet another spurious self
#
# Revision 1.14  2003/01/30 07:52:02  ncq
# - spurious self from refactoring removed
#
# Revision 1.13  2003/01/28 13:39:14  ncq
# - implemented schema import at the server level (= template database)
# - this is mainly useful for importing users
#
# Revision 1.12  2003/01/26 13:14:36  ncq
# - show a description before installing
# - ask user for confirmation if interactive
#
# Revision 1.11  2003/01/26 12:36:24  ncq
# - next generation
#
# Revision 1.5  2003/01/22 22:46:46  ncq
# - works apart from 3 problems:
#   - psql against remote host may need passwords but
#     there's no clean way to pass them in
#   - since we verify the path of procedural language
#     library files locally we will fail to install them
# 	on a remote host
#   - we don't yet store the imported schema's version
#
# Revision 1.4  2003/01/22 08:43:05  ncq
# - use dsn_formatstring to iron out DB-API incompatibilities
#
# Revision 1.3  2003/01/21 01:11:09  ncq
# - current (non-complete) state of affairs
#
# Revision 1.2  2003/01/14 20:52:46  ncq
# - works "more" :-)
#
# Revision 1.1  2003/01/13 16:55:20  ncq
# - first checkin of next generation
#
# Revision 1.10  2002/11/29 13:02:53  ncq
# - re-added psycopg support (hopefully)
#
# Revision 1.9  2002/11/18 22:41:21  ncq
# - don't really know what changed
#
# Revision 1.8  2002/11/18 12:23:31  ncq
# - make Debian happy by checking for psycopg, too
#
# Revision 1.7  2002/11/16 01:12:09  ncq
# - now finally also imports sql schemata from files
#
# Revision 1.6  2002/11/03 15:03:07  ncq
# - capture a little more info to hopefully catch the bug with DSN setup
#
# Revision 1.5  2002/11/01 15:17:44  ncq
# - need to wrap "create database" in "commit; ...; begin;" to work
#   around auto-transactions in pyPgSQL
#
# Revision 1.4  2002/11/01 14:06:53  ncq
# - another typo
#
# Revision 1.3  2002/11/01 14:05:39  ncq
# - typo
#
# Revision 1.2  2002/11/01 13:56:05  ncq
# - now also installs the GNUmed core database "gnumed"
#
# Revision 1.1  2002/10/31 22:59:19  ncq
# - tests environment, bootstraps users, bootstraps procedural languages
# - basically replaces gnumed.sql and setup-users.py
#
