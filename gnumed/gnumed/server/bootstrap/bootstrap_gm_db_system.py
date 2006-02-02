#!/usr/bin/env python

"""GNUmed schema installation.

This script bootstraps a GNUmed database system. All the
infrastructure is in place to support distributed
services. However, until further notice one should stick
to monolithic database design as cross-database links
are not well supported yet.

This will set up databases, services, database tables,
groups, permissions and possibly users.

There's a special user called "gm-dbo" who owns all the
database objects.

For all this to work you must be able to access the database
server as the standard "postgres" superuser.

This script does NOT set up user specific configuration options.

All definitions are loaded from a config file.

Please consult the User Manual in the GNUmed CVS for
further details.
"""
#==================================================================
# TODO
# - warn if empty password
# - option to drop databases
# - verify that pre-created database is owned by "gm-dbo"
#==================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/bootstrap/bootstrap_gm_db_system.py,v $
__version__ = "$Revision: 1.21 $"
__author__ = "Karsten.Hilbert@gmx.net"
__license__ = "GPL"

# standard library
import sys, string, os.path, fileinput, os, time, getpass, glob, re

# 3rd party imports
dbapi = None
try:
	from pyPgSQL import PgSQL
	from pyPgSQL import libpq
	dbapi = PgSQL
	db_error = libpq.DatabaseError
	dsn_format = "%s:%s:%s:%s:%s"
except ImportError:
	_log.LogException("Cannot load pyPgSQL.PgSQL database adapter module.", sys.exc_info(), verbose=0)
	try:
		import psycopg
		dbapi = psycopg
		db_error = psycopg.DatabaseError
		dsn_format = "host=%s port=%s dbname=%s user=%s password=%s"
	except ImportError:
		_log.LogException("Cannot load psycopg database adapter module.", sys.exc_info(), verbose=0)
		try:
			import pgdb
			dbapi = pgdb
			db_error = pgdb.DatabaseError
			dsn_format = "%s:%s:%s:%s:%s"
		except ImportError:
			print "Cannot find Python module for connecting to the database server. Program halted."
			print "Please check the log file and report to the mailing list."
			_log.LogException("Cannot load pgdb database adapter module.", sys.exc_info(), verbose=0)
			raise

# GNUmed imports
try:
	from Gnumed.pycommon import gmLog
except ImportError:
	print """Please make sure the GNUmed Python modules are in the Python path !"""
	raise
from Gnumed.pycommon import gmCfg, gmPsql
from Gnumed.pycommon.gmExceptions import ConstructorError
from Gnumed.pycommon.gmPyCompat import *

# local imports
import gmAuditSchemaGenerator
aud_gen = gmAuditSchemaGenerator

import gmNotificationSchemaGenerator
notify_gen = gmNotificationSchemaGenerator

_log = gmLog.gmDefLog
_log.SetAllLogLevels(gmLog.lData)
_cfg = gmCfg.gmDefCfgFile

_interactive = 0
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
			port = '' # to allow local connections
	if passwd == 'blank' or passwd is None or len(passwd) == 0:
		if cached_passwd.has_key (user):
			passwd = cached_passwd[user]
		else:
			passwd = ''

	conn = None
	dsn = dsn_format % (host, port, db, user, passwd)
	try:
		_log.Log (gmLog.lInfo, "trying DB connection to %s on %s as %s" % (db, host or 'localhost', user))
		conn = dbapi.connect(dsn)
		cached_host = (host, port) # learn from past successes
		cached_passwd[user] = passwd
		_log.Log (gmLog.lInfo, 'successfully connected')
	except db_error, message:
		_log.LogException('connection failed', sys.exc_info(), verbose = False)
		m = str(message)
		if re.search ("^FATAL:  No pg_hba.conf entry for host.*", m):
			# this pretty much means we're screwed
			if _interactive:
				print pg_hba_sermon
		elif re.search ("no password supplied", m):
			# didn't like blank password trick
			_log.Log (gmLog.lWarn, "attempt w/o password failed, retrying")
			passwd = getpass.getpass ("I need the password for the GNUmed database user [%s].\nPlease type password: " % user)
			conn = connect (host, port, db, user, passwd)
		elif re.search ("^FATAL:.*Password authentication failed.*", m):
			# didn't like supplied password
			_log.Log (gmLog.lWarn, "password not accepted, retrying")
			passwd = getpass.getpass ("I need the correct password for the GNUmed database user [%s].\nPlease type password: " % user)
			conn = connect (host, port, db, user, passwd)
		elif re.search ("could not connect to server", m):
			if len(host) == 0:
				# try again on TCP/IP loopback
				_log.Log (gmLog.lWarn , "UNIX socket connection failed, retrying on 127.0.0.1")
				conn = connect ("127.0.0.1", port, db, user, passwd)
			else:
				_log.Log (gmLog.lWarn, "connection to host %s:%s failed" % (host, port))
				if _interactive:
					print no_server_sermon
					host = raw_input("New host to connect to:")
					if len(host) > 0:
						host.split(':')
						if len(host) > 1:
							port = host[1]
							host = host[0]
						else:
							host = host[0]
							conn = connect (host, port, db, user, password)
		elif re.search ("^FATAL:.*IDENT authentication failed.*", m):
			if _interactive:
				if superuser:
					print superuser_sermon % user
				else:
					print pg_hba_sermon
		else:
			if _interactive:
				print no_clues % (message, sys.platform)
	return conn
#==================================================================
class user:
	def __init__(self, anAlias = None, aPassword = None):
		self.cfg = _cfg

		if anAlias is None:
			raise ConstructorError, "need user alias"
		self.alias = anAlias
		self.group = "user %s" % self.alias

		self.name = self.cfg.get(self.group, "name")
		if self.name is None:
			raise ConstructorError, "cannot get user name"

		self.password = aPassword

		# password not passed in, try to get it from elsewhere
		if self.password is None:
			# look into config file
			self.password = self.cfg.get(self.group, "password")
			# not defined there
			if self.password is None:
				# but we can ask the user
				if _interactive:
					self.password = getpass.getpass("I need the password for the GNUmed database user [%s].\nPlease type password: " % self.name)
				# or we cannot, fail
				else:
					raise ConstructorError, "cannot load database user password from config file"
			# defined but empty: this means the user does not need
			# a password but connects via IDENT or TRUST
			elif self.password == '':
				_log.Log(gmLog.lInfo, 'password explicitely set to be empty, assuming connect via IDENT/TRUST')
				self.password = None
		return None
#==================================================================
class db_server:
	def __init__(self, aSrv_alias, aCfg, auth_group):
		_log.Log(gmLog.lInfo, "bootstrapping server [%s]" % aSrv_alias)

		global _bootstrapped_servers

		if _bootstrapped_servers.has_key(aSrv_alias):
			_log.Log(gmLog.lInfo, "server [%s] already bootstrapped" % aSrv_alias)
			return None

		self.cfg = aCfg
		self.alias = aSrv_alias
		self.section = "server %s" % self.alias
		self.auth_group = auth_group

		if not self.__bootstrap():
			raise ConstructorError, "db_server.__init__(): Cannot bootstrap db server."

		_bootstrapped_servers[self.alias] = self

		return None
	#--------------------------------------------------------------
	def __bootstrap(self):
		self.superuser = user(anAlias = self.cfg.get(self.section, "super user alias"))

		# connect to server level template database
		if not self.__connect_to_srv_template():
			_log.Log(gmLog.lErr, "Cannot connect to server template database.")
			return None

		# add users/groups
		if not self.__bootstrap_db_users():
			_log.Log(gmLog.lErr, "Cannot bootstrap database users.")
			return None

		self.conn.close()
		return True
	#--------------------------------------------------------------
	def __connect_to_srv_template(self):
		_log.Log(gmLog.lInfo, "connecting to server template database")

		# sanity checks
		self.template_db = self.cfg.get(self.section, "template database")
		if self.template_db is None:
			_log.Log(gmLog.lErr, "Need to know the template database name.")
			return None

		self.name = self.cfg.get(self.section, "name")
		if self.name is None:
			_log.Log(gmLog.lErr, "Need to know the server name.")
			return None

		self.port = self.cfg.get(self.section, "port")
		if self.port is None:
			_log.Log(gmLog.lErr, "Need to know the database server port address.")
			return None

		self.conn = connect (self.name, self.port, self.template_db, self.superuser.name, self.superuser.password)

		_log.Log(gmLog.lInfo, "successfully connected to template database [%s]" % self.template_db)
		return True
	#--------------------------------------------------------------
	# user and group related
	#--------------------------------------------------------------
	def __bootstrap_db_users(self):
		_log.Log(gmLog.lInfo, "bootstrapping database users and groups")

		# insert standard groups
		if self.__create_groups() is None:
			_log.Log(gmLog.lErr, "Cannot create GNUmed standard groups.")
			return None

		# create GNUmed owner
		if self.__create_dbowner() is None:
			_log.Log(gmLog.lErr, "Cannot install GNUmed database owner.")
			return None

#		if not _import_schema(group=self.section, schema_opt='schema', conn=self.conn):
#			_log.Log(gmLog.lErr, "Cannot import schema definition for server [%s] into database [%s]." % (self.name, self.template_db))
#			return None

		return True
	#--------------------------------------------------------------
	def __user_exists(self, aCursor, aUser):
		cmd = "SELECT usename FROM pg_user WHERE usename = '%s'" % aUser
		try:
			aCursor.execute(cmd)
		except:
			_log.LogException(">>>[%s]<<< failed." % cmd, sys.exc_info(), verbose=1)
			return None
		res = aCursor.fetchone()
		if aCursor.rowcount == 1:
			_log.Log(gmLog.lInfo, "User [%s] exists." % aUser)
			return True
		_log.Log(gmLog.lInfo, "User [%s] does not exist." % aUser)
		return None
	#--------------------------------------------------------------
	def __create_dbowner(self):
		global _dbowner

		print "We are about to check whether we need to create the"
		print "database user who owns all GNUmed database objects."
		print ""

		dbowner_alias = self.cfg.get("GnuMed defaults", "database owner alias")
		if dbowner_alias is None:
			_log.Log(gmLog.lErr, "Cannot load GNUmed database owner name from config file.")
			return None

		cursor = self.conn.cursor()
		# does this user already exist ?
		name = self.cfg.get('user %s' % dbowner_alias, 'name')
		if self.__user_exists(cursor, name):
			cmd = 'alter group "gm-logins" add user "%s"; alter group "%s" add user "%s"' % (name, self.auth_group, name)
			try:
				cursor.execute(cmd)
			except:
				_log.Log(gmLog.lErr, ">>>[%s]<<< failed." % cmd)
				_log.LogException("Cannot add GNUmed database owner [%s] to groups [gm-logins] and [%s]." % (name, self.auth_group), sys.exc_info(), verbose=1)
				cursor.close()
				return False
			cursor.close()
			print "The database owner already exists."
			print "Please provide the password previously used for it."
			_dbowner = user(anAlias = dbowner_alias)
			return True

		print (
"""The database owner will be created.
You will have to provide a new password for it
unless it is pre-defined in the configuration file.

Make sure to remember the password.
""")
		_dbowner = user(anAlias = dbowner_alias)

		cmd = 'create user "%s" with password \'%s\' createdb in group "%s", "gm-logins"' % (_dbowner.name, _dbowner.password, self.auth_group)
		try:
			cursor.execute(cmd)
		except:
			_log.Log(gmLog.lErr, ">>>[%s]<<< failed." % cmd)
			_log.LogException("Cannot create GNUmed database owner [%s]." % _dbowner.name, sys.exc_info(), verbose=1)
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
			_log.LogException(">>>[%s]<<< failed." % cmd, sys.exc_info(), verbose=1)
			return False
		res = aCursor.fetchone()
		if aCursor.rowcount == 1:
			_log.Log(gmLog.lInfo, "Group %s exists." % aGroup)
			return True
		_log.Log(gmLog.lInfo, "Group %s does not exist." % aGroup)
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
			_log.LogException(">>>[%s]<<< failed." % cmd, sys.exc_info(), verbose=1)
			return False

		# paranoia is good
		if not self.__group_exists(aCursor, aGroup):
			return False

		return True
	#--------------------------------------------------------------
	def __create_groups(self, aCfg = None, aSection = None):
		if aCfg is None:
			cfg = self.cfg
		else:
			cfg = aCfg

		if aSection is None:
			section = "GnuMed defaults"
		else:
			section = aSection

		groups = cfg.get(section, "groups")
		if groups is None:
			_log.Log(gmLog.lErr, "Cannot load GNUmed group names from config file (section [%s])." % section)
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
	def __init__(self, aDB_alias, aCfg):
		_log.Log(gmLog.lInfo, "bootstrapping database [%s]" % aDB_alias)

		global _bootstrapped_dbs

		if _bootstrapped_dbs.has_key(aDB_alias):
			_log.Log(gmLog.lInfo, "database [%s] already bootstrapped" % aDB_alias)
			return None

		self.conn = None
		self.cfg = aCfg
		self.section = "database %s" % aDB_alias

		overrider = self.cfg.get(self.section, 'override name by')
		if overrider is not None:
			_log.Log(gmLog.lInfo, 'if environment variable [%s] exists, it override database name in config file' % overrider)
			self.name = os.getenv(overrider)
			if self.name is None:
				_log.Log(gmLog.lInfo, 'environment variable [%s] is not set, using database name from config file' % overrider)
				self.name = self.cfg.get(self.section, 'name')
		else:
			self.name = self.cfg.get(self.section, 'name')

		if self.name is None or str(self.name).strip() == '':
			_log.Log(gmLog.lErr, "Need to know database name.")
			raise ConstructorError, "database.__init__(): Cannot bootstrap database."

		self.server_alias = self.cfg.get(self.section, "server alias")
		if self.server_alias is None:
			_log.Log(gmLog.lErr, "Server alias missing.")
			raise ConstructorError, "database.__init__(): Cannot bootstrap database."

		self.template_db = self.cfg.get(self.section, "template database")
		if self.template_db is None:
			_log.Log(gmLog.lErr, "Template database name missing.")
			raise ConstructorError, "database.__init__(): Cannot bootstrap database."

		# make sure server is bootstrapped
		db_server(self.server_alias, self.cfg, auth_group = self.name)
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
			_dbowner = user(anAlias = self.cfg.get("GnuMed defaults", "database owner alias"))

		if _dbowner is None:
			_log.Log(gmLog.lErr, "Cannot load GNUmed database owner name from config file.")
			return None

		# get owner
		self.owner = _dbowner

		# connect as owner to template
		if not self.__connect_owner_to_template():
			_log.Log(gmLog.lErr, "Cannot connect to template database.")
			return None
		# make sure db exists
		if not self.__create_db():
			_log.Log(gmLog.lErr, "Cannot create database.")
			return None

		# reconnect as superuser to db
		if not self.__connect_superuser_to_db():
			_log.Log(gmLog.lErr, "Cannot connect to database.")
			return None
		# add languages
		if not self.__bootstrap_proc_langs():
			_log.Log(gmLog.lErr, "Cannot bootstrap procedural languages.")
			return None
		if not _import_schema(group=self.section, schema_opt='superuser schema', conn=self.conn):
			_log.Log(gmLog.lErr, "cannot import schema definition for database [%s]" % (self.name))
			return None

		# reconnect as owner to db
		if not self.__connect_owner_to_db():
			_log.Log(gmLog.lErr, "Cannot connect to database.")
			return None

		# import schema
		if not _import_schema(group=self.section, schema_opt='schema', conn=self.conn):
			_log.Log(gmLog.lErr, "cannot import schema definition for database [%s]" % (self.name))
			return None

		return True
	#--------------------------------------------------------------
	# procedural languages related
	#--------------------------------------------------------------
	def __bootstrap_proc_langs(self):
		_log.Log(gmLog.lInfo, "bootstrapping procedural languages")

		lang_aliases = self.cfg.get("GnuMed defaults", "procedural languages")
		# FIXME: better separation
		if (lang_aliases is None) or (len(lang_aliases) == 0):
			_log.Log(gmLog.lWarn, "No procedural languages to activate or error loading language list.")
			return True

		lib_dirs = _cfg.get("GnuMed defaults", "language library dirs")
		if lib_dirs is None:
			_log.Log(gmLog.lErr, "Error loading procedural language library directories list.")
			return None

		for lang in lang_aliases:
			if not self.__install_lang(lib_dirs, lang):
				_log.Log(gmLog.lErr, "Error installing procedural language [%s]." % lang)
				return None

		return True
	#--------------------------------------------------------------
	def __install_lang(self, aDirList = None, aLanguage = None):
		_log.Log(gmLog.lInfo, "installing procedural language [%s]" % aLanguage)

		if aLanguage is None:
			_log.Log(gmLog.lErr, "Need language name to install it !")
			return None

		lib_name = self.cfg.get(aLanguage, "library name")
		if lib_name is None:
			_log.Log(gmLog.lErr, "no language library name specified in config file")
			return None

#		# FIXME: what about *.so.1.3.5 ?
		if self.__lang_exists(lib_name.replace(".so", "", 1)):
			return True
#			self.__drop_lang(aLanguage)

		# do we check for library file existence ?
		check_for_lib = self.cfg.get(self.section, "procedural language library check")
		if string.lower(check_for_lib) != "no":
			if aDirList is None:
				_log.Log(gmLog.lErr, "Need dir list to search for language library !")
				return None
			lib_path = None
			for lib_dir in aDirList:
				tmp = os.path.join(lib_dir, lib_name)
				if os.path.exists(tmp):
					lib_path = tmp
					break
			if lib_path is None:
				_log.Log(gmLog.lErr, "cannot find language library file in any of %s" % aDirList)
				return None
		else:
			tmp = self.cfg.get(aLanguage, "library dir")
			if tmp is None:
				_log.Log(gmLog.lErr, 'if procedural language library search is disabled, you need to set the library dir option')
				return None
			lib_path = os.path.join(tmp, lib_name)

		tmp = self.cfg.get(aLanguage, "call handler")
		if tmp is None:
			_log.Log(gmLog.lErr, "no call handler cmd specified in config file")
			return None
		call_handler_cmd = ('\r'.join(tmp)) % lib_path

		tmp = self.cfg.get(aLanguage, "language activation")
		if tmp is None:
			_log.Log(gmLog.lErr, "no language activation cmd specified in config file")
			return None
		activate_lang_cmd = '\r'.join(tmp)

		cursor = self.conn.cursor()
		if not _run_query(cursor, call_handler_cmd):
			cursor.close()
			_log.LogException("cannot install procedural language [%s]" % aLanguage, sys.exc_info(), verbose=1)
			return None
		if not _run_query(cursor, activate_lang_cmd):
			cursor.close()
			_log.LogException("cannot install procedural language [%s]" % aLanguage, sys.exc_info(), verbose=1)
			return None

		self.conn.commit()
		cursor.close()

		if not self.__lang_exists(lib_name.replace(".so", "", 1)):
			return None

		_log.Log(gmLog.lInfo, "procedural language [%s] successfully installed" % aLanguage)
		return True
	#--------------------------------------------------------------
	def __drop_lang(self, aLanguage):
		drop_cmd = self.cfg.get(aLanguage, "drop command")
		if drop_cmd is None:
			_log.Log(gmLog.lErr, "no language drop cmd specified in config file")
			return
		drop_cmd = '\r'.join(drop_cmd)
		cursor = self.conn.cursor()
		if not _run_query(cursor, drop_cmd):
			cursor.close()
			_log.LogException("cannot drop procedural language [%s]" % aLanguage, sys.exc_info())
			return
		self.conn.commit()
		cursor.close()
		return
	#--------------------------------------------------------------
	def __lang_exists(self, aLanguage):
		cmd = "SELECT lanname FROM pg_language WHERE lanname='%s'" % aLanguage
		aCursor = self.conn.cursor()
		if not _run_query(aCursor, cmd):
			aCursor.close()
			return None

		res = aCursor.fetchone()
		tmp = aCursor.rowcount
		aCursor.close()
		if tmp == 1:
			_log.Log(gmLog.lInfo, "Language %s exists." % aLanguage)
			return True

		_log.Log(gmLog.lInfo, "Language %s does not exist." % aLanguage)
		return None
	#--------------------------------------------------------------
	def __connect_superuser_to_db(self):
		srv = self.server
		if self.conn is not None:
			self.conn.close()

		self.conn = connect (srv.name, srv.port, self.name, srv.superuser.name, srv.superuser.password)
		return self.conn and 1
	#--------------------------------------------------------------
	def __connect_owner_to_template(self):
		srv = self.server
		if self.conn is not None:
			self.conn.close()

		self.conn = connect (srv.name, srv.port, self.template_db, self.owner.name, self.owner.password)
		return self.conn and 1
	#--------------------------------------------------------------
	def __connect_owner_to_db(self):
		srv = self.server
		if self.conn is not None:
			self.conn.close()

		self.conn = connect (srv.name, srv.port, self.name, self.owner.name, self.owner.password) 
		return self.conn and 1
	#--------------------------------------------------------------
	def __db_exists(self):
		cmd = "BEGIN; SELECT datname FROM pg_database WHERE datname='%s'" % self.name

		aCursor = self.conn.cursor()
		try:
			aCursor.execute(cmd)
		except:
			_log.LogException(">>>[%s]<<< failed." % cmd, sys.exc_info(), verbose=1)
			return None

		res = aCursor.fetchall()
		tmp = aCursor.rowcount
		aCursor.close()
		if tmp == 1:
			_log.Log(gmLog.lInfo, "Database [%s] exists." % self.name)
			return True

		_log.Log(gmLog.lInfo, "Database [%s] does not exist." % self.name)
		return None
	#--------------------------------------------------------------
	def __create_db(self):
		if self.__db_exists():
			# FIXME: verify that database is owned by "gm-dbo"
			return True

		# create database
		# NOTE: we need to pull this nasty trick of ending and restarting
		# the current transaction to work around pgSQL automatically associating
		# cursors with transactions
		cmd = """
commit;
create database \"%s\" with
	owner = \"%s\"
	template = \"%s\"
	encoding = 'unicode';
begin
""" % (self.name, self.owner.name, self.template_db)

		cursor = self.conn.cursor()
		try:
			cursor.execute(cmd)
			self.conn.commit()
		except libpq.Warning, warning:
			_log.Log(gmLog.lWarn, warning)
		except StandardError:
			_log.LogException(">>>[%s]<<< failed" % cmd, sys.exc_info(), verbose=1)
			cursor.close()
			return None
		cursor.close()

		if not self.__db_exists():
			return None
		_log.Log(gmLog.lInfo, "Successfully created GNUmed database [%s]." % self.name)
		return True
	#--------------------------------------------------------------
	def bootstrap_auditing(self):
		# get audit trail configuration
		tmp = _cfg.get(self.section, 'audit disable')
		# if this option is not given, assume we want auditing
		if tmp is not None:
			# if we don't want auditing on these tables, return without error
			if int(tmp) == 1:
				return True

		tmp = _cfg.get(self.section, 'audit trail parent table')
		if tmp is None:
			return None
		aud_gen.audit_trail_parent_table = tmp

		tmp = _cfg.get(self.section, 'audit trail table prefix')
		if tmp is None:
			return None
		aud_gen.audit_trail_table_prefix = tmp
		
		tmp = _cfg.get(self.section, 'audit fields table')
		if tmp is None:
			return None
		aud_gen.audit_fields_table = tmp

		# create auditing schema
		curs = self.conn.cursor()
		audit_schema = gmAuditSchemaGenerator.create_audit_ddl(curs)
		curs.close()
		if audit_schema is None:
			_log.Log(gmLog.lErr, 'cannot generate audit trail schema for GNUmed database [%s]' % self.name)
			return None
		# write schema to file
		file = open('/tmp/audit-trail-schema.sql', 'wb')
		for line in audit_schema:
			file.write("%s;\n" % line)
		file.close()

		# import auditing schema
		psql = gmPsql.Psql (self.conn)
		if psql.run ('/tmp/audit-trail-schema.sql') != 0:
			_log.Log(gmLog.lErr, "cannot import audit schema definition for database [%s]" % (self.name))
			return None

		if _keep_temp_files:
			return True

		try:
			os.remove('/tmp/audit-trail-schema.sql')
			pass
		except StandardError:
			_log.LogException('cannot remove audit trail schema file [/tmp/audit-trail-schema.sql]', sys.exc_info(), verbose = 0)
		return True
	#--------------------------------------------------------------
	def bootstrap_notifications(self):
		# get configuration
		tmp = _cfg.get(self.section, 'notification disable')
		# if this option is not given, assume we want notification
		if tmp is not None:
			# if we don't want notification on these tables, return without error
			if int(tmp) == 1:
				return True

		# create notification schema
		curs = self.conn.cursor()
		notification_schema = notify_gen.create_notification_schema(curs)
		curs.close()
		if notification_schema is None:
			_log.Log(gmLog.lErr, 'cannot generate notification schema for GNUmed database [%s]' % self.name)
			return None

		# write schema to file
		file = open ('/tmp/notification-schema.sql', 'wb')
		for line in notification_schema:
			file.write("%s;\n" % line)
		file.close()

		# import notification schema
		psql = gmPsql.Psql (self.conn)
		if psql.run('/tmp/notification-schema.sql') != 0:
			_log.Log(gmLog.lErr, "cannot import notification schema definition for database [%s]" % (self.name))
			return None

		if _keep_temp_files:
			return True

		try:
			os.remove('/tmp/notification-schema.sql')
		except StandardError:
			_log.LogException('cannot remove notification schema file [/tmp/notification-schema.sql]', sys.exc_info(), verbose = 0)
		return True
#==================================================================
class gmService:
	def __init__(self, aServiceAlias = None):
		# sanity check
		if aServiceAlias is None:
			raise ConstructorError, "Need to know service name to install it."

		self.alias = aServiceAlias
		self.section = "service %s" % aServiceAlias
	#--------------------------------------------------------------
	def bootstrap(self):
		_log.Log(gmLog.lInfo, "bootstrapping service [%s]" % self.alias)

		# load service definition
		database_alias = _cfg.get(self.section, "database alias")
		if database_alias is None:
			_log.Log(gmLog.lErr, "Need to know database name to install service [%s]." % self.alias)
			return None
		# bootstrap database
		try:
			database(aDB_alias = database_alias, aCfg = _cfg)
		except:
			_log.LogException("Cannot bootstrap service [%s]." % self.alias, sys.exc_info(), verbose = 1)
			return None
		self.db = _bootstrapped_dbs[database_alias]

		# are we imported yet ?
		result = self.__service_exists()
		if result == 1:
			_log.Log(gmLog.lWarn, "service [%s] already exists" % self.alias)
			return True
		elif result == -1:
			_log.Log(gmLog.lWarn, "error detecting status of service [%s]" % self.alias)
			return None

		# check PostgreSQL version
		if not self.__verify_pg_version():
			_log.Log(gmLog.lErr, "Wrong PostgreSQL version.")
			return None

		# import schema
		if not _import_schema(group=self.section, schema_opt='schema', conn=self.db.conn):
			_log.Log(gmLog.lErr, "Cannot import schema definition for service [%s] into database [%s]." % (self.alias, database_alias))
			return None

		return True
	#--------------------------------------------------------------
	def __service_exists(self):
		"""Do we exist in the database already ?

		*  1 = yes, with correct version
		*  0 = no, please import
		* -1 = not sure: error or yes, but different version
		"""
		# we need the GNUmed name of the service later, so we store it here
		self.name = _cfg.get(self.section, 'name')

		curs = self.db.conn.cursor()

		# do we have version tracking available ?
		cmd = "select exists(select relname from pg_class where relname='gm_services' limit 1)"
		try:
			curs.execute(cmd)
		except:
			_log.LogException(">>>%s<<< failed" % cmd, sys.exc_info(), verbose=1)
			curs.close()
			return -1
		result = curs.fetchone()
		if not result[0]:
			# FIXME: this is a bit dangerous:
			# if we don't find the gm_services table we assume it's
			# OK to setup our service
			_log.Log(gmLog.lInfo, "didn't find 'gm_services' table")
			_log.Log(gmLog.lInfo, "assuming this is not a GNUmed database")
			_log.Log(gmLog.lInfo, "hence assuming it's OK to install GNUmed services here")
			curs.close()
			return 0

		# check if we got this service already
		if self.name is None:
			_log.Log(gmLog.lErr, "Need to know service name.")
			curs.close()
			return -1
		cmd = "select exists(select id from public.gm_services where name = '%s' limit 1)" % self.name
		try:
			curs.execute(cmd)
		except:
			_log.LogException(">>>%s<<< failed" % cmd, sys.exc_info(), verbose=1)
		result = curs.fetchone()
		if not result[0]:
			_log.Log(gmLog.lInfo, "service [%s] not installed here yet" % self.name)
			curs.close()
			return 0

		# check version
		required_version = _cfg.get(self.section, "version")
		if self.name is None:
			_log.Log(gmLog.lErr, "Need to know service version.")
			curs.close()
			return -1
		cmd = "select version, created from public.gm_services where name = '%s' limit 1)" % self.name
		try:
			curs.execute(cmd)
		except:
			_log.LogException(">>>%s<<< failed" % cmd, sys.exc_info(), verbose=1)
		result = curs.fetchone()
		existing_version = result[0][0]
		created = result[0][1]
		if existing_version == required_version:
			_log.Log(gmLog.lInfo, "version [%s] of service [%s] already exists (created <%s>)" % (existing_version, name, created))
			curs.close()
			return True
		_log.Log(gmLog.lErr, "service [%s] exists (created <%s>) but version mismatch" % (name, created))
		_log.Log(gmLog.lErr, "required: [%s]")
		_log.Log(gmLog.lErr, "existing: [%s]")
		curs.close()
		return -1
	#--------------------------------------------------------------
	def __verify_pg_version(self):
		"""Verify database version information."""

		required_version = _cfg.get(self.section, "minimum postgresql version")
		if required_version is None:
			_log.Log(gmLog.lErr, "Cannot load minimum required PostgreSQL version from config file.")
			return None

		try:
			existing_version = self.db.conn.version
		except:
			existing_version = None

		if existing_version is None:
			_log.Log(gmLog.lWarn, 'DB adapter does not support version checking')
			_log.Log(gmLog.lWarn, 'assuming installed PostgreSQL server is compatible with required version %s' % required_version)
			return True

		if existing_version < required_version:
			_log.Log(gmLog.lErr, "Reported live PostgreSQL version [%s] is smaller than the required minimum version [%s]." % (existing_version, required_version))
			return None

		_log.Log(gmLog.lInfo, "installed PostgreSQL version: [%s] - this is fine with me" % existing_version)
		return True
	#--------------------------------------------------------------
	def register(self):
		# FIXME - register service
		# a) in its own database - TODO
		# FIXME : We don't check for invalid service entries here 
		# (e.g. multiple service aliases linking to the same internal gnumed service)
		_log.Log(gmLog.lInfo, "Registering service [%s] (GNUmed internal name: [%s])." % (self.alias, self.name))

		# note: this is not entirely safe
		core_alias = _cfg.get(self.section, "registration database")
		core_name = _cfg.get("database %s" % core_alias, "name")
		try:
			coreDB =_bootstrapped_dbs[core_alias]
		except KeyError:
			_log.Log(gmLog.lErr, 'Cannot register service. Database [%s] (%s) not bootstrapped.' % (core_alias, core_name))
			return None

		curs = coreDB.conn.cursor()
		# check for presence of service name in core database (service config)
		cmd = "select id from cfg.distributed_db where name='%s' limit 1" % self.name
		try:
			curs.execute(cmd)
		except:
			_log.LogException(">>>%s<<< failed" % cmd, sys.exc_info(), verbose=1)
			curs.close()
			return None
		# fetch distributed database ID
		result = curs.fetchone()

		if result is None:
			# if the servicename is not found there are 2 possibilities:
			# a) don't allow creation of new service names
			# b) create a new service name without further inquiry
			# The latter could lead to creation of new services on spelling
			# errors, so we don't register those services automatically
			_log.Log(gmLog.lInfo, "Service [%s] not defined in GNUmed." % self.name)
			_log.Log(gmLog.lInfo, "Check configuration file or ask GNUmed admins")
			_log.Log(gmLog.lInfo, "for inclusion of new service name.")
			curs.close()
			return None
		ddbID = result[0]

		# the service name has been found, ID is in ddbID
		# now check if the according database is already known to gnumed
		# no need to store the core database definition
		if self.db is coreDB:
			_log.Log(gmLog.lInfo, "Service [%s] resides in core database." % self.name)
			_log.Log(gmLog.lInfo, "It will be automatically recognized by GNUmed.")
			curs.close()
			return True
		# if not, insert database definition in table db
		else:
			cmd = "select id from cfg.db where name='%s' limit 1" % self.db.name
			try:
				curs.execute(cmd)
			except:
				_log.LogException(">>>%s<<< failed" % cmd, sys.exc_info(), verbose=1)
				curs.close()
				return None

			result = curs.fetchone()			
			if result is None:
				# if the database wasn't found, store the database definition in table db
				# FIXME: should this not be handled in cDatabase.bootstrap() ?
				_log.Log(gmLog.lInfo, "Storing database definition for [%s]." % self.db.name)
				_log.Log(gmLog.lInfo, "name=%s, host=%s, port=%s" % (self.db.name,self.db.server.port,self.db.server.name))
	
				cmd = "INSERT INTO cfg.db (name,port,host) VALUES ('%s',%s,'%s')" % (self.db.name,self.db.server.port,self.db.server.name)
				try:
					curs.execute(cmd)
				except:
					_log.LogException(">>>%s<<< failed" % cmd, sys.exc_info(), verbose=1)
					curs.close()
					return None

				coreDB.conn.commit()

				# get the database id for the created entry
				cmd = "select id from cfg.db where name='%s' limit 1" % self.db.name
				try:
					curs.execute(cmd)
				except:
					_log.LogException(">>>%s<<< failed" % cmd, sys.exc_info(), verbose=1)
					curs.close()
					return None
				# this should not return None anymore
				dbID = curs.fetchone()[0]
			else:
				dbID = result[0]

			# now we must link services to databases
			# we can omit this procedure for all services residing on the core database
			_log.Log(gmLog.lInfo, "Linking service [%s] to database [%s]." % (self.name,self.db.name))

			# FIXME: check if username='' is correct
			# in fact, no: this is configuration and thus user dependant,
			# bootstrapping, however, is done by gm-dbo,
			# so, actually, this should not be done here but rather moved
			# over to the generic configuration tables and be done for the
			# xxxDEFAULTxxx user, upon client startup if not "user" config exists
			# the xxxDEFAULTxxx config will be read, confirmed by the current user
			# and stored for her ...
			cmd = "INSERT INTO cfg.config (username, db, ddb) VALUES ('%s',%s,'%s')" % ('',dbID,ddbID)
			try:
				curs.execute(cmd)
			except:
				_log.LogException(">>>%s<<< failed" % cmd, sys.exc_info(), verbose=1)
				curs.close()
				return None
			curs.close()
			coreDB.conn.commit()

		_log.Log(gmLog.lInfo, "Service [%s] has been successfully registered." % self.alias )
		return True
#==================================================================
def bootstrap_services():
	# get service list
	services = _cfg.get("installation", "services")
	if services is None:
		exit_with_msg("Service list empty. Nothing to do here.")
	# run through services
	for service_alias in services:
		print '==> bootstrapping "%s" ...' % service_alias
		service = gmService(service_alias)
		if not service.bootstrap():
			return None
		if not service.register():
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
def _run_query(aCurs, aQuery):
	try:
		aCurs.execute(aQuery)
	except:
		_log.LogException(">>>%s<<< failed" % aQuery, sys.exc_info(), verbose=1)
		return None
	return True
#------------------------------------------------------------------
def ask_for_confirmation():
	services = _cfg.get("installation", "services")
	if services is None:
		return True
	print "You are about to install the following parts of GNUmed:"
	print "-------------------------------------------------------"
	for service in services:
		service_name = _cfg.get("service %s" % service, "name")
		db_alias = _cfg.get("service %s" % service, "database alias")
		db_name = _cfg.get("database %s" % db_alias, "name")
		srv_alias = _cfg.get("database %s" % db_alias, "server alias")
		srv_name = _cfg.get("server %s" % srv_alias, "name")
		print 'part "%s" [service <%s> in <%s> (or overridden) on <%s>]' % (service, service_name, db_name, srv_name)
	print "-------------------------------------------------------"
	desc = _cfg.get("installation", "description")
	if desc is not None:
		for line in desc:
			print line
	if _interactive:
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
	schema_files = _cfg.get(group, schema_opt)
	if schema_files is None:
		_log.Log(gmLog.lErr, "Need to know schema definition to install it.")
		return None

	schema_base_dir = _cfg.get(group, "schema base directory")
	if schema_base_dir is None:
		_log.Log(gmLog.lWarn, "no schema files base directory specified")
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
#		if _import_schema_file(anSQL_file = the_file, aSrv = aSrv_name, aDB = aDB_name, aUser = aUser):
		if psql.run(the_file) == 0:
			_log.Log (gmLog.lInfo, 'successfully imported [%s]' % the_file)
		else:
			_log.Log (gmLog.lErr, 'failed to import [%s]' % the_file)
			return None
	return True
#--------------------------------------------------------------
#def _import_schema_file(anSQL_file = None, aSrv = None, aDB = None, aUser = None):
	# sanity checks
#	if anSQL_file is None:
#		_log.Log(gmLog.lErr, "Cannot import schema without schema file.")
#		return None
#	SQL_file = os.path.abspath(anSQL_file)
#	if not os.path.exists(SQL_file):
#		_log.Log(gmLog.lErr, "Schema file [%s] does not exist." % SQL_file)
#		return None

#	old_path = os.getcwd()
#	path = os.path.dirname(SQL_file)
#	os.chdir(path)

	# (at, 11.6.2003)
	# The following psql call has to be done as user aUser (= gm-dbo)
	# Because we can not ask for a password while non-interactive install
	# authenitification method in /etc/postgresql/pg_hba.conf has to be set
	# to TRUST.  This can be done via the following line:
	#    local   gnumed-test  @gmTemplate1User.list                  trust
	# This requires a file /var/lib/postgres/data/gmTemplate1User.list containing
	# at least gm-dbo
	# From `man psql`: If you omit the host name, psql will connect
	#                  via a Unix domain socket to a server on the
	#                  local host.
	# This seems to be necessary under Debian GNU/Linux because
	# otherwise the authentification fails
	# We have to leave out the -h option here ...
#	if aSrv in ['localhost', '']:
#		srv_arg = ''
#	else:
#		srv_arg = '-h "%s"' % aSrv

#	cmd = 'LC_CTYPE=UTF-8 psql -q %s -d "%s" -U "%s" -f "%s"' % (srv_arg, aDB, aUser, SQL_file)

#	_log.Log(gmLog.lInfo, "running [%s]" % cmd)
#	result = os.system(cmd)
#	_log.Log(gmLog.lInfo, "raw result: %s" % result)

#	os.chdir(old_path)

	# this seems to make trouble under pure Win2k (not CygWin, that is)
#	if os.WIFEXITED(result):
#		exitcode = os.WEXITSTATUS(result)
#		_log.Log(gmLog.lInfo, "shell level exit code: %s" % exitcode)
#		if exitcode == 0:
#			_log.Log(gmLog.lInfo, "success")
#			return True

#		if exitcode == 1:
#			_log.Log(gmLog.lErr, "failed: psql internal error")
#		elif exitcode == 2:
#			_log.Log(gmLog.lErr, "failed: database connection error")
#		elif exitcode == 3:
#			_log.Log(gmLog.lErr, "failed: psql script error")
#	else:
#		_log.Log(gmLog.lWarn, "aborted by signal")

#	return None
#------------------------------------------------------------------
def exit_with_msg(aMsg = None):
	if aMsg is not None:
		print aMsg
	print "Please check the log file for details."
	try:
		dbconn.close()
	except:
		pass
	_log.Log(gmLog.lErr, aMsg)
	_log.Log(gmLog.lInfo, "shutdown")
	sys.exit(1)
#------------------------------------------------------------------
def show_msg(aMsg = None):
	if aMsg is not None:
		print aMsg
	print "Please see log file for details."
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
		_log.Log (gmLog.lWarn, "running on broken OS -- can't import pwd module")
		return None

	try:
		_log.Log(gmLog.lInfo, 'running as user [%s]' % pwd.getpwuid(os.getuid())[0])
	except: pass

	pg_demon_user_passwd_line = None
	if os.getuid() == 0: # we are the super-user
		try:
			pg_demon_user_passwd_line = pwd.getpwnam ('postgres')
			# make sure we actually use this name to log in
			_cfg.set('user postgres', 'name', 'postgres')
		except KeyError:
			try:
				pg_demon_user_passwd_line = pwd.getpwnam ('pgsql')
				_cfg.set('user postgres', 'name', 'pgsql')
			except KeyError:
				_log.Log (gmLog.lWarn, 'cannot find postgres user')
				return None
		_log.Log (gmLog.lInfo, 'switching to UNIX user [%s]' % pg_demon_user_passwd_line[0])
		os.setuid(pg_demon_user_passwd_line[2])
	else:
		_log.Log(gmLog.lWarn, 'not running as root, cannot become postmaster demon user')
		_log.Log(gmLog.lWarn, 'may have trouble connecting as gm-dbo if IDENT auth is forced upon us')
		if _interactive:
			print "WARNING: This script may not work if not running as the system administrator."

#==============================================================================
def get_cfg_in_nice_mode():
	print welcome_sermon
	cfgs = []
	n = 0
	for cfg_file in glob.glob('*.conf'):
		cfg = gmCfg.cCfgFile(None, cfg_file)
		# only offer those conf files that aren't reserved for gurus
		if cfg.get('installation', 'guru_only') == '1':
			continue
		cfgs.append(cfg)
		desc = '\n    '.join(cfg.get('installation', 'description'))	# some indentation
		print  '%2s) %s' % (n, desc)
		n += 1
	choice = int(raw_input ('\n\nYour choice: '))
	if choice == -1:
		return None
	return cfgs[choice]
#==================================================================
def handle_cfg():
	_log.Log(gmLog.lInfo, "bootstrapping GNUmed database system from file [%s] (%s)" % (_cfg.get("revision control", "file"), _cfg.get("revision control", "version")))

	print "Using config file [%s]." % _cfg.cfgName

	become_pg_demon_user()

	tmp = _cfg.get("installation", "interactive")
	if tmp == "yes":
		global _interactive
		_interactive = 1

	tmp = _cfg.get('installation', 'keep temp files')
	if tmp == "yes":
		global _keep_temp_files
		_keep_temp_files = True

	if not ask_for_confirmation():
		print "Bootstrapping aborted by user."
		return

	if not bootstrap_services():
		exit_with_msg("Cannot bootstrap services.")

	if not bootstrap_auditing():
		exit_with_msg("Cannot bootstrap audit trail.")

	if not bootstrap_notifications():
		exit_with_msg("Cannot bootstrap notification tables.")

	print "Done with config file [%s]." % _cfg.cfgName
#==================================================================
if __name__ == "__main__":
	_log.Log(gmLog.lInfo, "startup (%s)" % __version__)
	if _cfg is None:
		_log.Log(gmLog.lInfo, "No config file specified on command line. Switching to nice mode.")
		_cfg = get_cfg_in_nice_mode()
		if _cfg is None:
			print "bye"
			sys.exit(0)

	print "======================================="
	print "Bootstrapping GNUmed database system..."
	print "======================================="

	cfg_files = _cfg.get('installation', 'config files')
	if cfg_files is None:
		handle_cfg()
	else:
		for cfg_file in cfg_files:
			_cfg = gmCfg.cCfgFile(None, cfg_file, flags = gmCfg.cfg_IGNORE_CMD_LINE)
			handle_cfg()

	_log.Log(gmLog.lInfo, "shutdown")
	print "Done bootstrapping: We probably succeeded."
else:
	print "This currently is not intended to be used as a module."

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
#		_log.Log(gmLog.lData, "child stdout: [%s]" % line, gmLog.lCooked)
#	tmp = pipe.childerr.read()
#	lines = tmp.split("\n")
#	for line in lines:
#		_log.Log(gmLog.lErr, "child stderr: [%s]" % line, gmLog.lCooked)

#	pipe.fromchild.close()
#	pipe.childerr.close()
#	del pipe

#==================================================================
# $Log: bootstrap_gm_db_system.py,v $
# Revision 1.21  2006-02-02 16:19:09  ncq
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
