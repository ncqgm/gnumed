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
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/utils/Attic/bootstrap-gm_db_system.py,v $
__version__ = "$Revision: 1.2 $"
__author__ = "Karsten.Hilbert@gmx.net"
__license__ = "GPL"

import sys, string, os.path

# location of our modules
sys.path.append(os.path.join('.', 'modules'))

import gmLog
_log = gmLog.gmDefLog
_log.SetAllLogLevels(gmLog.lData)

import gmCfg
_cfg = gmCfg.gmDefCfgFile

import gmUserSetup

dbapi = None
dbconn = None

core_server = {}
initial_user = {}
initial_database = None
#==================================================================
def connect_to_db():
	print "Connecting to PostgreSQL server as initial user ..."

	# load database adapter
	global dbapi
	dbapi = None
	try:
		from pyPgSQL import PgSQL
	except:
		exc = sys.exc_info()
		_log.LogException("Cannot load pyPgSQL.pgSQL database adapter module.", exc, fatal=1)
		return None
	dbapi = PgSQL

	# load authentication information
	global core_server
	tmp = _cfg.get("core server", "name")
	if not tmp:
		_log.Log(gmLog.lErr, "Cannot load database host name from config file.")
		tmp = "localhost"
	core_server["host name"] = raw_input("host [%s]: " % tmp)
	if core_server["host name"] == "":
		core_server["host name"] = tmp

	tmp = _cfg.get("core server", "port")
	if not tmp.isdigit():
		_log.Log(gmLog.lErr, "Cannot load database API port number from config file.")
		tmp = 5432
	core_server["port"] = raw_input("port [%s]: " % tmp)
	if core_server["port"] == "":
		core_server["port"] = tmp

	global initial_database
	tmp = _cfg.get("core server", "initial database")
	if not tmp:
		_log.Log(gmLog.lErr, "Cannot load initial database name from config file.")
		tmp = "template1"
	initial_database = raw_input("database [%s]: " % tmp)
	if initial_database == "":
		initial_database = tmp

	global initial_user
	tmp = _cfg.get("core server", "initial user")
	if not tmp:
		_log.Log(gmLog.lErr, "Cannot load database super-user from config file.")
		tmp = "postgres"
	initial_user["name"] = raw_input("user [%s]: " % tmp)
	if initial_user["name"] == "":
		initial_user["name"] = tmp

	# get password from user
	print "We still need a password to actually access the database."
	print "(user [%s] in db [%s] on [%s:%s])" % (initial_user["name"], database, core_server["host name"], core_server["port"])
	initial_user["password"] = raw_input("Please type password: ")

	# log in
	dsn = "%s:%s:%s:%s:%s" % (core_server["host name"], core_server["port"], database, initial_user["name"], initial_user["password"])
	try:
		conn = PgSQL.connect(dsn)
	except:
		exc = sys.exc_info()
		_log.LogException("Cannot connect (user [%s] with pwd [%s] in db [%s] on [%s:%s])." % (initial_user["name"], initial_user["password"], database, core_server["host name"], core_server["port"]), exc, fatal=1)
		return None
	_log.Log(gmLog.lInfo, "successfully connected to database (user [%s] in db [%s] on [%s:%s])" % (initial_user["name"], database, core_server["host name"], core_server["port"]))

	print "Successfully connected."
	return conn
#------------------------------------------------------------------
def reconnect_as_gm_owner():
	print "Reconnecting to PostgreSQL server as GnuMed database owner ..."

	global core_server
	global initial_database

	if not gmUserSetup.dbowner.has_key("name"):
		_log.Log(gmLog.lErr, "Cannot connect without GnuMed database owner name.")
		return None

	if not gmUserSetup.dbowner.has_key("password"):
		# get password from user
		print "We need the password for the GnuMed database owner."
		print "(user [%s] in db [%s] on [%s:%s])" % (gmUserSetup.dbowner["name"], initial_database, core_server["host name"], core_server["port"])
		gmUserSetup.dbowner["password"] = raw_input("Please type password: ")

	# log in
	dsn = "%s:%s:%s:%s:%s" % (core_server["host name"], core_server["port"], initial_database, gmUserSetup.dbowner["name"], gmUserSetup.dbowner["password"])
	try:
		conn = PgSQL.connect(dsn)
	except:
		_log.LogException("Cannot connect (user [%s] with pwd [%s] in db [%s] on [%s:%s])." % (gmUserSetup.dbowner["name"], gmUserSetup.dbowner["password"], initial_database, core_server["host name"], core_server["port"]), sys.exc_info(), fatal=1)
		return None
	_log.Log(gmLog.lInfo, "successfully connected to database (user [%s] in db [%s] on [%s:%s])" % (gmUserSetup.dbowner["name"], initial_database, core_server["host name"], core_server["port"]))

	print "Successfully connected."
	return conn
#------------------------------------------------------------------
def verify_db():
	"""Verify database version information."""

	print "Verifying PostgreSQL server version..."

	required_version = _cfg.get("GnuMed defaults", "postgres version")
	if not required_version:
		_log.Log(gmLog.lErr, "Cannot load minimum required PostgreSQL version from config file.")
		return None

	if dbconn.version < required_version:
		_log.Log(gmLog.lErr, "Reported live PostgreSQL version [%s] is smaller than the required minimum version [%s]." % (dbconn.version, required_version))
		print "Installed PostgreSQL does not have minimum required version !"
		return None

	_log.Log(gmLog.lInfo, "installed PostgreSQL version: %s - this is fine with me" % dbconn.version)
	print "PostgreSQL version successfully verified."
	return 1
#==================================================================
def lang_exists(aLanguage):
	cmd = "SELECT lanname FROM pg_language WHERE lanname='%s';" % aLanguage

	aCursor = dbconn.cursor()
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
#------------------------------------------------------------------
def install_lang(aDirList = None, aLanguage = None):
	_log.Log(gmLog.lInfo, "installing procedural language [%s]" % aLanguage)

	if aLanguage is None:
		_log.Log(gmLog.lErr, "Need language name to install it !")
		return None

	lib_name = _cfg.get(aLanguage, "library name")
	if lib_name is None:
		_log.Log(gmLog.lErr, "no language library name specified in config file")
		return None

	if lang_exists(lib_name.replace(".so", "", 1)):
		return 1

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

	tmp = _cfg.get(aLanguage, "call handler")
	if tmp is None:
		_log.Log(gmLog.lErr, "no call handler cmd specified in config file")
		return None
	call_handler_cmd = tmp[0] % lib_path

	tmp = _cfg.get(aLanguage, "language activation")
	if tmp is None:
		_log.Log(gmLog.lErr, "no language activation cmd specified in config file")
		return None
	activate_lang_cmd = tmp[0]

	cursor = dbconn.cursor()
	try:
		cursor.execute(call_handler_cmd)
		cursor.execute(activate_lang_cmd)
	except:
		_log.LogException("cannot install procedural language [%s]" % aLanguage, sys.exc_info(), fatal=1)
		cursor.close()
		return None

	dbconn.commit()
	cursor.close()

	if not lang_exists(lib_name.replace(".so", "", 1)):
		return None

	_log.Log(gmLog.lInfo, "procedural language [%s] successfully installed" % aLanguage)
	return 1
#==================================================================
def bootstrap_user_structure():
	# create users first
	if not gmUserSetup.create_standard_structure(aConn = dbconn, aCfg = _cfg):
		dbconn.close()
		exit_with_msg("Cannot create GnuMed standard user/group structure.")

	# insert test users
	if not gmUserSetup.create_test_structure(dbconn, aCfg = _cfg):
		print "Cannot create GnuMed test users.\nPlease see log file for details."

	# insert site-specific users
	if not gmUserSetup.create_local_structure(dbconn):
		print "Cannot create site-specific GnuMed user/group structure.\nPlease see log file for details."

	return 1
#------------------------------------------------------------------
def bootstrap_procedural_languages():
	print "Activating procedural languages..."

	lang_list = _cfg.get("GnuMed defaults", "procedural languages")
	if lang_list is None:
		print "No procedural languages to activate or error loading language list."

	lib_dirs = _cfg.get("GnuMed defaults", "language library dirs")
	if lang_list is None:
		_log.Log(gmLog.lErr, "Error loading procedural language library directories list.")
		exit_with_msg("Error loading procedural language library directories list.")

	for lang in lang_list:
		if not install_lang(lib_dirs, lang):
			exit_with_msg("Error installing procedural language [%s]." % lang)

	return 1
#------------------------------------------------------------------
def db_exists(aDatabase):
	cmd = "SELECT datname FROM pg_database WHERE datname='%s';" % aDatabase

	aCursor = dbconn.cursor()
	try:
		aCursor.execute(cmd)
	except:
		_log.LogException(">>>[%s]<<< failed." % cmd, sys.exc_info(), fatal=1)
		return None

	res = aCursor.fetchone()
	tmp = aCursor.rowcount
	aCursor.close()
	if tmp == 1:
		_log.Log(gmLog.lInfo, "Database %s exists." % aDatabase)
		return 1

	_log.Log(gmLog.lInfo, "Database %s does not exist." % aDatabase)
	return None
#------------------------------------------------------------------
bootstrap_core_database()
	print "Bootstrapping GnuMed core database..."

	global dbconn

	# reconnect as GnuMed database owner
	dbconn.close()
	tmp = reconnect_as_gm_owner()
	if tmp is None:
		exit_with_msg("Cannot reconnect to database as GnuMed database owner.")
	dbconn = tmp

	database = _cfg.get("GnuMed defaults", "core database name")
	if not database:
		_log.Log(gmLog.lErr, "Cannot load name of core GnuMed database from config file.")
		database = "gnumed"

	# create main database
	if db_exists(database):
		return 1

	cursor = dbconn.cursor()
	cmd = 'create database "%s"' % database
	try:
		cursor.execute(cmd)
	except:
		_log.LogException(">>>[%s]<<< failed." % cmd, sys.exc_info(), fatal=1)
		return None
	dbconn.commit()
	cursor.close()

	# reconnect to main database as database owner

	return 1
#==================================================================
def exit_with_msg(aMsg = None):
	if not (aMsg is None):
		print aMsg
	print "Please see log file for details."
	if not dbconn is None:
		dbconn.close()
	_log.Log(gmLog.lErr, aMsg)
	_log.Log(gmLog.lInfo, "shutdown")
	sys.exit(1)
#------------------------------------------------------------------
def show_msg(aMsg = None):
	if not (aMsg is None):
		print aMsg
	print "Please see log file for details."
#==================================================================
if __name__ == "__main__":
	_log.Log(gmLog.lInfo, "startup (%s)" % __version__)
	_log.Log(gmLog.lInfo, "bootstrapping GnuMed database system from file [%s] (%s)" % (_cfg.get("revision control", "file"), _cfg.get("revision control", "version")))

	print "Bootstrapping GnuMed database system..."

	# connect to template database as superuser
	tmp = connect_to_db()
	if tmp is None:
		exit_with_msg("Cannot connect to database.")
	dbconn = tmp

	if not verify_db():
		dbconn.close()
		exit_with_msg("Cannot verify database version.")

	# create users/groups
	bootstrap_user_structure()

	# insert procedural languages
	bootstrap_procedural_languages()

	# boostrap gnumed core database
	bootstrap_core_database()

	# setup (possibly distributed) services

	dbconn.close()
	_log.Log(gmLog.lInfo, "shutdown")
	print "Done bootstrapping."
else:
	print "This currently isn't intended to be used as a module."
#==================================================================
# $Log: bootstrap-gm_db_system.py,v $
# Revision 1.2  2002-11-01 13:56:05  ncq
# - now also installs the GnuMed core database "gnumed"
#
# Revision 1.1  2002/10/31 22:59:19  ncq
# - tests environment, bootstraps users, bootstraps procedural languages
# - basically replaces gnumed.sql and setup-users.py
#
