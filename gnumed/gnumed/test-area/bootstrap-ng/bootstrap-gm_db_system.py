#!/usr/bin/env python

"""GnuMed user/group installation.

This script installs all the users and groups needed for
proper GnuMed usage. It will also set proper access rights.

Theory of operation:

Rights will be granted to users via groups. Effectively, groups
are granted certain access rights and users are added to the
appropriate groups as needed.

There's a special user called "gmdb-owner" who owns all the
database objects.

Normal users are represented twice in the database:
 1) under their normal user name with read-only rights
 2) under their user name prepended by "_" for write access

For all this to work you must be able to access the database
server as the standard "postgres" superuser.

This script does NOT set up user specific configuration options.

All definitions are loaded from a config file.

Please consult the Developer's Guide in the GnuMed CVS for
further details.
"""
#==================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/test-area/bootstrap-ng/Attic/bootstrap-gm_db_system.py,v $
__version__ = "$Revision: 1.5 $"
__author__ = "Karsten.Hilbert@gmx.net"
__license__ = "GPL"

import sys, string, os.path, fileinput, os, time

# location of our modules
sys.path.append(os.path.join('.', 'modules'))

import gmLog
_log = gmLog.gmDefLog
_log.SetAllLogLevels(gmLog.lData)

import gmCfg
_cfg = gmCfg.gmDefCfgFile

dbapi = None
try:
	from pyPgSQL import PgSQL
	dbapi = PgSQL
	dsn_format = "%s:%s:%s:%s:%s"
except ImportError:
	_log.Log(gmLog.lErr, "Cannot load pyPgSQL.PgSQL database adapter module.")
	try:
		import psycopg
		dbapi = psycopg
		dsn_format = "host=%s port=%s dbname=%s user=%s password=%s"
	except ImportError:
		_log.Log(gmLog.lErr, "Cannot load psycopg database adapter module.")
		try:
			import pgdb
			dbapi = pgdb
			dsn_format = "%s:%s:%s:%s:%s"
		except ImportError:
			print "Cannot find Python module for connecting to the database server. Program halted."
			_log.Log(gmLog.lErr, "Cannot load pgdb database adapter module.")
			raise

from gmExceptions import ConstructorError

_interactive = 0
_bootstrapped_servers = {}
_bootstrapped_dbs = {}
_dbowner = None
#==================================================================
class user:
	def __init__(self, anAlias = None, aPassword = None, aCfg = _cfg):
		self.cfg = aCfg

		if anAlias is None:
			raise ConstructorError, "need user alias"
		self.alias = anAlias
		self.group = "user %s" % self.alias

		self.name = self.cfg.get(self.group, "name")
		if self.name is None:
			raise ConstructorError, "cannot get user name"

		if aPassword is None:
			self.password = self.cfg.get(self.group, "password")
			if self.password is None:
				if _interactive:
					print "I need the password for the GnuMed database user [%s]." % self.name
					self.password = raw_input("Please type password: ")
				else:
					raise ConstructorError, "cannot load database user password from config file"
		else:
			self.password = aPassword
		return None
#==================================================================
class db_server:
	def __init__(self, aSrv_alias, aCfg):
		_log.Log(gmLog.lInfo, "bootstrapping server [%s]" % aSrv_alias)

		global _bootstrapped_servers

		if _bootstrapped_servers.has_key(aSrv_alias):
			_log.Log(gmLog.lInfo, "server [%s] already bootstrapped" % aSrv_alias)
			return None

		self.cfg = aCfg
		self.alias = aSrv_alias
		self.section = "server %s" % self.alias

		if not self.__bootstrap():
			raise ConstructorError, "db_server.__init__(): Cannot bootstrap db server."

		_bootstrapped_servers[self.alias] = self

		return None
	#--------------------------------------------------------------
	def __bootstrap(self):
		self.superuser = user(anAlias = self.cfg.get(self.section, "super user alias"))

		# connect to template
		if not self.__connect_to_template():
			_log.Log(gmLog.lErr, "Cannot connect to template database.")
			return None

		# add users/groups
		if not self.__bootstrap_db_users():
			_log.Log(gmLog.lErr, "Cannot bootstrap database users.")
			return None

		# add languages
		if not self.__bootstrap_proc_langs():
			_log.Log(gmLog.lErr, "Cannot bootstrap procedural languages.")
			return None

		# FIXME: test for features (eg. dblink)

		self.conn.close()
		return 1
	#--------------------------------------------------------------
	def __connect_to_template(self):
		_log.Log(gmLog.lInfo, "connecting to template database")

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

		dsn = dsn_format % (
			self.name,
			self.port,
			self.template_db,
			self.superuser.name,
			self.superuser.password
		)
		try:
			self.conn = dbapi.connect(dsn)
		except:
			_log.LogException("cannot connect with DSN = [%s]" % dsn, sys.exc_info(), fatal=1)
			return None

		_log.Log(gmLog.lInfo, "successfully connected to template database [%s]" % self.template_db)
		return 1
	#--------------------------------------------------------------
	# procedural languages related
	#--------------------------------------------------------------
	def __lang_exists(self, aLanguage):
		cmd = "SELECT lanname FROM pg_language WHERE lanname='%s';" % aLanguage
		aCursor = self.conn.cursor()
		try:
			aCursor.execute(cmd)
		except:
			_log.LogException(">>>[%s]<<< failed." % cmd, sys.exc_info(), fatal=1)
			return None

		res = aCursor.fetchone()
		tmp = aCursor.rowcount
		aCursor.close()
		if tmp == 1:
			_log.Log(gmLog.lInfo, "Language %s exists." % aLanguage)
			return 1

		_log.Log(gmLog.lInfo, "Language %s does not exist." % aLanguage)
		return None
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

		# FIXME: what about *.so.1.3.5 ?
		if self.__lang_exists(lib_name.replace(".so", "", 1)):
			return 1

		if aDirList is None:
			_log.Log(gmLog.lErr, "Need dir list to search for language library !")
			return None

		# FIXME: this logically fails in remote installs !!!
		lib_path = None
		for lib_dir in aDirList:
			tmp = os.path.join(lib_dir, lib_name)
			if os.path.exists(tmp):
				lib_path = tmp
				break

		if lib_path is None:
			_log.Log(gmLog.lErr, "cannot find language library file in any of %s" % aDirList)
			return None

		tmp = self.cfg.get(aLanguage, "call handler")
		if tmp is None:
			_log.Log(gmLog.lErr, "no call handler cmd specified in config file")
			return None
		call_handler_cmd = tmp[0] % lib_path

		tmp = self.cfg.get(aLanguage, "language activation")
		if tmp is None:
			_log.Log(gmLog.lErr, "no language activation cmd specified in config file")
			return None
		activate_lang_cmd = tmp[0]

		cursor = self.conn.cursor()
		try:
			cursor.execute(call_handler_cmd)
			cursor.execute(activate_lang_cmd)
		except:
			_log.LogException("cannot install procedural language [%s]" % aLanguage, sys.exc_info(), fatal=1)
			cursor.close()
			return None

		self.conn.commit()
		cursor.close()

		if not self.__lang_exists(lib_name.replace(".so", "", 1)):
			return None

		_log.Log(gmLog.lInfo, "procedural language [%s] successfully installed" % aLanguage)
		return 1
	#--------------------------------------------------------------
	def __bootstrap_proc_langs(self):
		_log.Log(gmLog.lInfo, "bootstrapping procedural languages")

		lang_aliases = self.cfg.get("GnuMed defaults", "procedural languages")
		# FIXME: better separation
		if (lang_aliases is None) or (len(lang_aliases) == 0):
			_log.Log(gmLog.lWarn, "No procedural languages to activate or error loading language list.")
			return 1

		lib_dirs = _cfg.get("installation", "language library dirs")
		if lib_dirs is None:
			_log.Log(gmLog.lErr, "Error loading procedural language library directories list.")
			return None

		for lang in lang_aliases:
			if not self.__install_lang(lib_dirs, lang):
				_log.Log(gmLog.lErr, "Error installing procedural language [%s]." % lang)
				return None

		return 1
	#--------------------------------------------------------------
	# user and group related
	#--------------------------------------------------------------
	def __bootstrap_db_users(self):
		_log.Log(gmLog.lInfo, "bootstrapping database users and groups")

		# create GnuMed owner
		if self.__create_dbowner() is None:
			_log.Log(gmLog.lErr, "Cannot install GnuMed database owner.")
			return None

		# insert standard groups
		if self.__create_groups() is None:
			_log.Log(gmLog.lErr, "Cannot create GnuMed standard groups.")
			return None

		return 1
	#--------------------------------------------------------------
	def __user_exists(self, aCursor, aUser):
		cmd = "SELECT usename FROM pg_user WHERE usename='%s';" % aUser
		try:
			aCursor.execute(cmd)
		except:
			_log.LogException(">>>[%s]<<< failed." % cmd, sys.exc_info(), fatal=1)
			return None
		res = aCursor.fetchone()
		if aCursor.rowcount == 1:
			_log.Log(gmLog.lInfo, "User [%s] exists." % aUser)
			return 1
		_log.Log(gmLog.lInfo, "User [%s] does not exist." % aUser)
		return None
	#--------------------------------------------------------------
	def __create_dbowner(self):
		global _dbowner

		# get owner
		if _dbowner is None:
			_dbowner = user(anAlias = self.cfg.get("GnuMed defaults", "database owner alias"))

		if _dbowner is None:
			_log.Log(gmLog.lErr, "Cannot load GnuMed database owner name from config file.")
			return None

		cursor = self.conn.cursor()
		# does this user already exist ?
		if self.__user_exists(cursor, _dbowner.name):
			cursor.close()
			return 1

		cmd = "CREATE USER \"%s\" WITH PASSWORD '%s' CREATEDB;" % (_dbowner.name, _dbowner.password)
		try:
			cursor.execute(cmd)
		except:
			_log.Log(gmLog.lErr, ">>>[%s]<<< failed." % cmd)
			_log.LogException("Cannot create GnuMed database owner [%s]." % _dbowner.name, sys.exc_info(), fatal=1)
			cursor.close()
			return None

		# paranoia is good
		if not self.__user_exists(cursor, _dbowner.name):
			cursor.close()
			return None

		self.conn.commit()
		cursor.close()
		return 1
	#--------------------------------------------------------------
	def __group_exists(self, aCursor, aGroup):
		cmd = "SELECT groname FROM pg_group WHERE groname='%s';" % aGroup
		try:
			aCursor.execute(cmd)
		except:
			_log.LogException(">>>[%s]<<< failed." % cmd, sys.exc_info(), fatal=1)
			return None
		res = aCursor.fetchone()
		if aCursor.rowcount == 1:
			_log.Log(gmLog.lInfo, "Group %s exists." % aGroup)
			return 1
		_log.Log(gmLog.lInfo, "Group %s does not exist." % aGroup)
		return None
	#--------------------------------------------------------------
	def __create_group(self, aCursor, aGroup):
		# does this group already exist ?
		if self.__group_exists(aCursor, aGroup):
			return 1

		cmd = "CREATE GROUP \"%s\";" % aGroup
		try:
			aCursor.execute(cmd)
		except:
			_log.LogException(">>>[%s]<<< failed." % cmd, sys.exc_info(), fatal=1)
			return None

		# paranoia is good
		if not self.__group_exists(aCursor, aGroup):
			return None

		return 1
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
			_log.Log(gmLog.lErr, "Cannot load GnuMed group names from config file (section [%s])." % section)
			return None

		cursor = self.conn.cursor()

		for group in groups:
			if not self.__create_group(cursor, group):
				cursor.close()
				return None

		self.conn.commit()
		cursor.close()
		return 1
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

		self.name = self.cfg.get(self.section, 'name')
		if self.name is None:
			_log.Log(gmLog.lErr, "Need to know database name.")
			raise ConstructorError, "database.__init__(): Cannot bootstrap database."

		self.server_alias = self.cfg.get(self.section, "server alias")
		if self.server_alias is None:
			_log.Log(gmLog.lErr, "Server alias missing.")
			raise ConstructorError, "database.__init__(): Cannot bootstrap database."

		# make sure server is bootstrapped
		db_server(self.server_alias, self.cfg)
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
			_log.Log(gmLog.lErr, "Cannot load GnuMed database owner name from config file.")
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

		# reconnect as owner to db
		if not self.__connect_owner_to_db():
			_log.Log(gmLog.lErr, "Cannot connect to database.")
			return None

		# import schema

		return 1
	#--------------------------------------------------------------
	def __connect_owner_to_template(self):
		srv = self.server
		try:
			dsn = dsn_format % (
				srv.name,
				srv.port,
				srv.template_db,
				self.owner.name,
				self.owner.password
			)
		except:
			_log.LogException("Cannot construct DSN !", sys.exc_info(), fatal=1)
			return None

		if self.conn is not None:
			self.conn.close()

		try:
			self.conn = dbapi.connect(dsn)
		except:
			_log.LogException("Cannot connect with DSN = [%s]." % dsn, sys.exc_info(), fatal=1)
			return None
		_log.Log(gmLog.lInfo, "successfully connected to template database [%s]" % srv.template_db)
		return 1
	#--------------------------------------------------------------
	def __connect_owner_to_db(self):
		srv = self.server
		try:
			dsn = dsn_format % (
				srv.name,
				srv.port,
				self.name,
				self.owner.name,
				self.owner.password
			)
		except:
			_log.LogException("Cannot construct DSN !", sys.exc_info(), fatal=1)
			return None

		if self.conn is not None:
			self.conn.close()

		try:
			self.conn = dbapi.connect(dsn)
		except:
			_log.LogException("Cannot connect with DSN = [%s]." % dsn, sys.exc_info(), fatal=1)
			return None
		_log.Log(gmLog.lInfo, "successfully connected to database [%s]" % self.name)
		return 1
	#--------------------------------------------------------------
	def __db_exists(self):
		cmd = "SELECT datname FROM pg_database WHERE datname='%s';" % self.name

		aCursor = self.conn.cursor()
		try:
			aCursor.execute(cmd)
		except:
			_log.LogException(">>>[%s]<<< failed." % cmd, sys.exc_info(), fatal=1)
			return None

		res = aCursor.fetchone()
		tmp = aCursor.rowcount
		aCursor.close()
		if tmp == 1:
			_log.Log(gmLog.lInfo, "Database [%s] exists." % self.name)
			return 1

		_log.Log(gmLog.lInfo, "Database [%s] does not exist." % self.name)
		return None
	#--------------------------------------------------------------
	def __create_db(self):
		if self.__db_exists():
			return 1

		# create database
		# FIXME: we need to pull this nasty trick of ending and restarting
		# the current transaction to work around pgSQL automatically associating
		# cursors with transactions
		cmd = 'commit; create database "%s"; begin' % self.name

		cursor = self.conn.cursor()
		try:
			cursor.execute(cmd)
		except:
			_log.LogException(">>>[%s]<<< failed." % cmd, sys.exc_info(), fatal=1)
			return None
		self.conn.commit()
		cursor.close()

		if not self.__db_exists():
			return None
		_log.Log(gmLog.lInfo, "Successfully created GnuMed database [%s]." % self.name)
		return 1
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
			_log.LogException("Cannot bootstrap service [%s]." % self.alias, sys.exc_info(), fatal = 1)
			return None
		self.db = _bootstrapped_dbs[database_alias]

		# are we imported yet ?
		result = self.__service_exists()
		if result == 1:
			_log.Log(gmLog.lWarn, "service [%s] already exists" % self.alias)
			return 1
		elif result == -1:
			_log.Log(gmLog.lWarn, "error detecting status of service [%s]" % self.alias)
			return None

		# check PostgreSQL version
		if not self.__verify_pg_version():
			_log.Log(gmLog.lErr, "Wrong PostgreSQL version.")
			return None

		# import schema
		if not self.__import_schema():
			_log.Log(gmLog.lErr, "Cannot import schema definition for service [%s] into database [%s]." % (self.alias, database_alias))
			return None

		return 1
	#--------------------------------------------------------------
	def __service_exists(self):
		"""Do we exist in the database already ?

		*  1 = yes, with correct version
		*  0 = no, please import
		* -1 = not sure: error or yes, but different version
		"""
		curs = self.db.conn.cursor()

		# do we have version tracking available ?
		cmd = "select exists(select relname from pg_class where relname='gm_services' limit 1);"
		try:
			curs.execute(cmd)
		except:
			_log.LogException(">>>%s<<< failed" % cmd, sys.exc_info(), fatal=1)
			curs.close()
			return -1
		result = curs.fetchone()
		if not result[0]:
			# FIXME: this is a bit dangerous:
			# if we don't find the gm_services table we assume it's
			# OK to setup our service
			_log.Log(gmLog.lInfo, "didn't find 'gm_services' table")
			_log.Log(gmLog.lInfo, "assuming this is not a GnuMed database")
			_log.Log(gmLog.lInfo, "hence assuming it's OK to install GnuMed services here")
			curs.close()
			return 0

		# check if we got this service already
		name = _cfg.get(self.section, "name")
		if name is None:
			_log.Log(gmLog.lErr, "Need to know service name.")
			curs.close()
			return -1
		cmd = "select exists(select id from gm_services where name = '%s' limit 1);" % name
		try:
			curs.execute(cmd)
		except:
			_log.LogException(">>>%s<<< failed" % cmd, sys.exc_info(), fatal=1)
		result = curs.fetchone()
		if not result[0]:
			_log.Log(gmLog.lInfo, "service [%s] not installed here yet" % name)
			curs.close()
			return 0

		# check version
		required_version = _cfg.get(self.section, "version")
		if name is None:
			_log.Log(gmLog.lErr, "Need to know service version.")
			curs.close()
			return -1
		cmd = "select version, created from gm_services where name = '%s' limit 1);" % name
		try:
			curs.execute(cmd)
		except:
			_log.LogException(">>>%s<<< failed" % cmd, sys.exc_info(), fatal=1)
		result = curs.fetchone()
		existing_version = result[0][0]
		created = result[0][1]
		if existing_version == required_version:
			_log.Log(gmLog.lInfo, "version [%s] of service [%s] already exists (created <%s>)" % (existing_version, name, created))
			curs.close()
			return 1
		_log.Log(gmLog.lErr, "service [%s] exists (created <%s>) but version mismatch" % (name, created))
		_log.Log(gmLog.lErr, "required: [%s]")
		_log.Log(gmLog.lErr, "existing: [%s]")
		curs.close()
		return -1
	#--------------------------------------------------------------
	def __import_schema(self):
		# load schema
		schema_files = _cfg.get(self.section, "schema")
		if schema_files is None:
			_log.Log(gmLog.lErr, "Need to know schema definition to install service [%s]." % self.alias)
			return None
		# and import them
		for file in schema_files:
			if not self.__import_schema_file(file):
				_log.Log(gmLog.lErr, "cannot import SQL schema file [%s]" % file)
				return None
		return 1
	#--------------------------------------------------------------
	def __import_schema_file(self, anSQL_file = None):
		# sanity checks
		if anSQL_file is None:
			_log.Log(gmLog.lErr, "Cannot import schema without schema file.")
			return None
		SQL_file = os.path.abspath(anSQL_file)
		if not os.path.exists(SQL_file):
			_log.Log(gmLog.lErr, "Schema file [%s] does not exist." % SQL_file)
			return None

		# -W = force password prompt
		# -q = quiet
		#cmd = 'psql -a -E -h "%s" -d "%s" -U "%s" -f "%s" >> /tmp/psql-import.log 2>&1' % (aHost, aDB, aUser, SQL_file)
		#cmd = 'psql -q -W -h "%s" -d "%s" -U "%s" -f "%s"' % (aHost, aDB, aUser, SQL_file)
		#cmd = 'psql -a -E -W -h "%s" -d "%s" -U "%s" -f "%s"' % (aHost, aDB, aUser, SQL_file)

		old_path = os.getcwd()
		path = os.path.dirname(SQL_file)
		os.chdir(path)

		cmd = 'psql -q -h "%s" -d "%s" -U "%s" -f "%s"' % (self.db.server.name, self.db.name, _dbowner.name, SQL_file)
		_log.Log(gmLog.lInfo, "running [%s]" % cmd)
		result = os.system(cmd)
		_log.Log(gmLog.lInfo, "raw result: %s" % result)

		os.chdir(old_path)

		if os.WIFEXITED(result):
			exitcode = os.WEXITSTATUS(result)
			_log.Log(gmLog.lInfo, "shell level exit code: %s" % exitcode)
			if exitcode == 0:
				_log.Log(gmLog.lInfo, "success")
				return 1

			if exitcode == 1:
				_log.Log(gmLog.lErr, "failed: psql internal error")
			elif exitcode == 2:
				_log.Log(gmLog.lErr, "failed: database connection error")
			elif exitcode == 3:
				_log.Log(gmLog.lErr, "failed: psql script error")
		else:
			_log.Log(gmLog.lWarn, "aborted by signal")

		return None
	#--------------------------------------------------------------
	def __verify_pg_version(self):
		"""Verify database version information."""

		required_version = _cfg.get(self.section, "postgres version")
		if required_version is None:
			_log.Log(gmLog.lErr, "Cannot load minimum required PostgreSQL version from config file.")
			return None

		existing_version = self.db.conn.version
		if existing_version < required_version:
			_log.Log(gmLog.lErr, "Reported live PostgreSQL version [%s] is smaller than the required minimum version [%s]." % (existing_version, required_version))
			return None

		_log.Log(gmLog.lInfo, "installed PostgreSQL version: [%s] - this is fine with me" % existing_version)
		return 1
	#--------------------------------------------------------------
	def register(self):
		# FIXME - register service
		# a) in its own database
		# b) in the distributed database
		return 1
#==================================================================
def bootstrap_services():
	# get service list
	services = _cfg.get("installation", "services")
	if services is None:
		exit_with_msg("Service list empty. Nothing to do here.")
	# run through services
	for service_alias in services:
		service = gmService(service_alias)
		if not service.bootstrap():
			return None
		if not service.register():
			return None
	return 1
#------------------------------------------------------------------
def exit_with_msg(aMsg = None):
	if aMsg is not None:
		print aMsg
	print "Please see log file for details."
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
#==================================================================
if __name__ == "__main__":
	_log.Log(gmLog.lInfo, "startup (%s)" % __version__)
	_log.Log(gmLog.lInfo, "bootstrapping GnuMed database system from file [%s] (%s)" % (_cfg.get("revision control", "file"), _cfg.get("revision control", "version")))

	print "Bootstrapping GnuMed database system..."

	tmp = _cfg.get("installation", "interactive")
	if tmp == "yes":
		_interactive = 1

	# bootstrap services
	if not bootstrap_services():
		exit_with_msg("Cannot bootstrap services.")

	_log.Log(gmLog.lInfo, "shutdown")
	print "Done bootstrapping."
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
# $Log: bootstrap-gm_db_system.py,v $
# Revision 1.5  2003-01-22 22:46:46  ncq
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
# - now also installs the GnuMed core database "gnumed"
#
# Revision 1.1  2002/10/31 22:59:19  ncq
# - tests environment, bootstraps users, bootstraps procedural languages
# - basically replaces gnumed.sql and setup-users.py
#
