#!/usr/bin/env python

"""GnuMed user/group installation.

This script installs all the users and groups needed for
proper GnuMed usage. It will also set proper access rights.

Theory of operation:

Rights will be granted to users via groups. Effectively, groups
are granted certain access rights and users are added to the
appropriate groups as needed.

There's a special user called "gm_db_owner" who owns all the
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
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/utils/Attic/setup-users.py,v $
__version__ = "$Revision: 1.2 $"
__author__ = "Karsten.Hilbert@gmx.net"
__license__ = "GPL"

import sys

import gmLog
_log = gmLog.gmDefLog
_log.SetAllLogLevels(gmLog.lData)

import gmCfg
_cfg = gmCfg.gmDefCfgFile

dbapi = None
conn = None
#==================================================================
def connect_to_db():

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
	host = _cfg.get("server", "name")
	if not host:
		_log.Log(gmLog.lErr, "Cannot load database host name from config file.")
		return None
	port = _cfg.get("server", "port")
	if not port.isdigit():
		_log.Log(gmLog.lErr, "Cannot load database API port number from config file.")
		return None
	database = _cfg.get("server", "database")
	if not database:
		_log.Log(gmLog.lErr, "Cannot load database name from config file.")
		return None
	user = _cfg.get("server", "user")
	if not user:
		_log.Log(gmLog.lErr, "Cannot load database super-user from config file.")
		return None

	# get password from user
	print "We still need a password to actually access the database."
	print "(user [%s] in db [%s] on %s:%s)" % (user, database, host, port)
	password = raw_input("Please type password: ")

	# log in
	global conn
	dsn = "%s:%s:%s:%s:%s" % (host, port, database, user, password)
	try:
		conn = PgSQL.connect(dsn)
	except:
		exc = sys.exc_info()
		_log.LogException("Cannot connect (user [%s] with pwd [%s] in db [%s] on %s:%s)" % (user, password, database, host, port), exc, fatal=1)
		return None
	_log.Log(gmLog.lInfo, "successfully connected to database")
	print "Successfully connected to database."

	return 1
#------------------------------------------------------------------
def verify_db():

	# verify database version information
	required_version = _cfg.get("server", "version")
	if not required_version:
		_log.Log(gmLog.lErr, "Cannot load minimum required PostgreSQL version from config file.")
		return None

	if conn.version < required_version:
		_log.Log(gmLog.lErr, "Reported live PostgreSQL version [%s] is smaller than the required minimum version [%s]." % (conn.version, required_version))
		print "Installed PostgreSQL does not have minimum required version !"
		return None

	_log.Log(gmLog.lInfo, "installed PostgreSQL version: %s - this is OK for us" % conn.version)
	print "PostgreSQL version successfully verified."
	return 1
#==================================================================
if __name__ == "__main__":
	_log.Log(gmLog.lInfo, "startup (%s)" % __version__)
	_log.Log(gmLog.lInfo, "installing GnuMed users/groups from file [%s] (%s)" % (_cfg.get("revision control", "file"), _cfg.get("revision control", "version")))

	# connect to database
	if not connect_to_db():
		sys.exit("Cannot connect to database.\nPlease see log file for details.")

	if not verify_db():
		conn.close()
		sys.exit("Cannot verify database version.\nPlease see log file for details.")

	# create GnuMed superuser "gm_db_owner"
	# insert groups
	# insert users
	#  (pg_user, pg_shadow)

	conn.close()
	_log.Log(gmLog.lInfo, "shutdown")
else:
	print "This currently isn't intended to be used as a module."
#==================================================================
# $Log: setup-users.py,v $
# Revision 1.2  2002-10-03 00:16:20  ncq
# - first real steps: connect and verify database version
#
# Revision 1.1  2002/09/30 23:06:26  ncq
# - first shot so people can see what I am getting at
#
