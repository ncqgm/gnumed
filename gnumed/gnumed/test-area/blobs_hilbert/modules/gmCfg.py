#!/usr/bin/env python

"""GNUmed configuration handling.

Two sources of configuration information are supported:

 - INI-style configuration files
 - database tables

Just import this module to have access to a default config file.

Theory of operation:

Upon importing this module a basic config file will be parsed. This
file is registered at the default source for configuration information.

The module will look for the config file in the following standard
places:

1) programmer supplied arguments
2) user supplied command line (getopt style):	--conf-file=<a file name>
3) user supplied GNUMED_DIR directory
4) ~/.<aDir>/<aName>.conf
5) ~/.<aName>.conf
6) /etc/<aDir>/<aName>.conf
7) /etc/<aName>.conf
8) ./<aName>.conf		- last resort for DOS/Win

It is helpful to have a solid log target set up before importing this
module in your code. This way you will be able to even see those log
messages generated during module import.

For sample code see bottom of file.

Once your software has established database connectivity it can call
 activateDatabase()
to switch on database access for configuration options.

The default config info source is then switched to database access.

At any time can you force file or database access for a particular
configuration call via a parameter except before database access is
activated in which case the module will always use file access.

@copyright: GPL
"""
#---------------------------------------------------------------
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/test-area/blobs_hilbert/modules/Attic/gmCfg.py,v $
__version__ = "$Revision: 1.1 $"
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>, Ian Haywood <i.haywood@ugrad.unimelb.edu.au>"

# standard modules
import os.path, sys, ConfigParser, types, os, string
#, cPickle

# GNUmed modules
import gmLog, gmPG, gmExceptions, gmCLI
#---------------------------------------------------------------
__log__ = gmLog.gmDefLog

srcFile	= "file"
srcDB	= "db"

global gmDefCfg

# exceptions (really the only way to fail on __init__()s
_NoFileNameExc = "Cannot find a valid config file. Aborting."
_CantParseFileExc = "Cannot open/parse config file. Aborting."
#---------------------------------------------------------------
class cCfg:
	"""GNUmed configuration handling class.

	- transparently handle INI file and database access
	"""
	def __init__(self, aFileName = None):
		"""Set up configuration object.

		- immediately set up file access
		- with aFileName you can override automatic detection of config file
		"""
		# get config file name
		self.__cfg_name = self.__get_conf_name(aName = aFileName)
		if not self.__cfg_name:
			__log__.Log(gmLog.lErr, "Cannot find a valid config file. Aborting.")
			raise _NoFileNameExc

		__log__.Log(gmLog.lInfo, "config file: " + self.__cfg_name)			# please leave this in here so we know which config file we actually end up with

		# actually connect to cfg file
		self.__cfg_file = None
		if not self.loadConfFile(self.__cfg_name):
			__log__.Log(gmLog.lErr, "Cannot open/parse config file. Aborting.")
			raise _CantParseFileExc

		self.deactivateDatabase()		# we don't have db connectivity yet
		self.setContext()				# default context "default"

		# let's do it this way just in case we end up attaching even more sources
		self.__get_handler = {
			srcFile: self.__get_from_file,
			srcDB: self.__get_from_db
		}
	#-------------------------------------
	def loadConfFile(self, aFileName = None):
		# sanity check
		if aFileName == None:
			__log__.Log(gmLog.lErr, "Cannot load config file without filename.")
			return None
		else:
			__log__.Log(gmLog.lInfo, "Loading config file %s." % aFileName)

		# try to open new file
		try:
			tmp = ConfigParser.ConfigParser()
			tmp.read(aFileName)
		except:
			exc = sys.exc_info()
			__log__.LogException("Cannot open/parse config file !", exc)
			return None

		# detach old file
		del self.__cfg_file
		# attach new file
		self.__cfg_file = tmp
		self.__cfg_name = aFileName
		return 1
	#-------------------------------------
	def activateDatabase(self):
		# shortcut
		if self.__db_active:
			return

		# actually get connection to db
		# at this point in time we assume general database connectivity to exist
		# so this is more like setting up a hardlink with little overhead
		pool = gmPG.ConnectionPool()
		self.__db_conn = pool.GetConnection('gmconfiguration')

		self.__db_active = 1
		self.__curr_src = srcDB

		# FIXME: we should retrieve all pertinent options here to prevent slowdown later
		# FIXME: maybe even a callback to a progress indicator would be in order
	#-------------------------------------
	def deactivateDatabase(self):
		self.__db_active = 0
		self.__curr_src = srcFile
		self.__db_conn = None

		# actually release connection to db
		pool = gmPG.ConnectionPool()
		pool.ReleaseConnection('gmconfiguration')
	#-------------------------------------
	def setSource(self, aSource = None):
		"""Set default source of config data."""

		# sanity check
		if aSource == None:
			__log__.Log(gmLog.lErr, 'You must specify a source ("db" or "file") to switch to it !')
			return None

		# shortcut
		if aSource == self.__curr_src:
			return 1

		# set to DB
		if aSource == srcDB:
			if self.__db_active:
				self.__curr_src = srcDB
				return 1
			else:
				__log__.Log(gmLog.lErr, 'Cannot switch to source "database" without a valid database connection !')
				return None

		# set to file
		if aSource == srcFile:
			self.__curr_src = srcFile
			return 1

		# this should not happen
		__log__.Log(gmLog.lErr, 'Invalid source ("%s") ! Valid sources: "db", "file"' % str(aSource))
		return None
	#-------------------------------------
	def setContext(self, aContext = None):
		"""Set the option context.

		- if aContext is None fall back to default default context
		- corresponds to [section]s in INI files
		"""
		if aContext == None:
			self.__curr_context = "default"
		else:
			self.__curr_context = str(aContext)
	#-------------------------------------
	# transparent access methods
	#-------------------------------------
	# actually it would look cleaner to put aSrc in front,
	# but then we would _always_ have to type "<keyword> = ..."
	# since most of the time we won't specify the source but at the
	# same time give arguments by position
	def get(self, aContext = None, anOption = None, aSrc = None):
		"""Retrieve an option.

		- returns a string
		- aContext == [section] in INI files
		- aContext == None -> self.__curr_context
		- aSrc == None -> self.__curr_src
		"""
		# sanity checks
		if anOption == None:
			__log__.Log(gmLog.lErr, "Cannot retrieve option without option name.")
			return None
		if aContext == None:
			aContext = self.__curr_context
		if aSrc == None:
			aSrc = self.__curr_src
		# now actually get the stuff
		return self.__get_handler[aSrc](aContext, anOption)
	#-------------------------------------
	# internal methods
	#-------------------------------------
	def __get_from_file(self, aContext, anOption):
		if self.__cfg_file == None:
			__log__.Log(gmLog.lErr, 'Cannot read data from config file without file being open.')
		try:
			return self.__cfg_file.get(aContext, anOption)
		except:
			exc = sys.exc_info()
			__log__.LogException('Exception: ', exc)
			raise
	#-------------------------------------
	def __get_from_db(self, aContext, anOption):
		pass
	#-------------------------------------
	def __get_conf_name(self, aDir = None, aName = None):
		"""Try to construct a valid config file name."""

		# 1) has the programmer manually specified a config file ?
		if aName != None:
			cfgName = os.path.abspath(aName)
			if os.path.exists(cfgName):
				return cfgName
			else:
				__log__.Log(gmLog.lWarn, 'config file %s (via argument name="%s") not found' % (cfgName, aName))
				if aDir != None:
					cfgName = os.path.abspath(os.path.join(aDir, aName))
					if os.path.exists(cfgName):
						return cfgName
					else:
						__log__.Log(gmLog.lWarn, 'Config file %s (via arguments dir="%s", name="%s") not found. Aborting.' % (cfgName, aDir, aName))
						return None

		# 2) has the user manually supplied a config file on the command line ?
		if gmCLI.has_arg('--conf-file'):
			cfgName = gmCLI.arg['--conf-file']
			# file valid ?
			if os.path.exists(cfgName):
				return cfgName
			else:
				__log__.Log(gmLog.lErr, "Config file %s (given on command line) not found. Aborting." % cfgName)
				return None
		else:
			__log__.Log(gmLog.lWarn, "No config file given on command line. Format: --conf-file=<config file>")

		# now make base path components
		if aName == None:
			# get base name from name of script
			base_name = os.path.splitext(os.path.basename(sys.argv[0]))[0] + ".conf"
		else:
			base_name = aName

		if aDir == None:
			# get base dir from name of script
			base_dir = os.path.splitext(os.path.basename(sys.argv[0]))[0]
		else:
			base_dir = aDir

		# 3) $(<script-name>_DIR)/base_name
		env_key = "%s_DIR" % string.upper(os.path.splitext(os.path.basename(sys.argv[0]))[0])
		if os.environ.has_key(env_key):
			cfgName = os.path.abspath(os.path.expanduser(os.path.join(os.environ(env_key), base_name)))
			if os.path.exists(cfgName):
				return cfgName
			else:
				__log__.Log(gmLog.lErr, "Config file %s (in $%s) not found." % (cfgName, env_key))
		else:
			__log__.Log(gmLog.lInfo, "Environment variable %s is not set." % env_key)

		# 4) ~/.base_dir/base_name
		cfgName = os.path.expanduser(os.path.join('~', '.' + base_dir, base_name))
		if not os.path.exists(cfgName):
			__log__.Log(gmLog.lWarn, "config file %s not found." % cfgName)
		else:
			return cfgName

		# 5) ~/.base_name
		cfgName = os.path.expanduser(os.path.join('~', '.' + base_name))
		if not os.path.exists(cfgName):
			__log__.Log(gmLog.lWarn, "config file %s not found." % cfgName)
		else:
			return cfgName

		# 6) /etc/base_dir/base_name
		cfgName = os.path.join('/etc', base_dir, base_name)
		if not os.path.exists(cfgName):
			__log__.Log(gmLog.lWarn, "config file %s not found." % cfgName)
		else:
			return cfgName

		# 7) /etc/base_name
		cfgName = os.path.join('/etc', base_name)
		if not os.path.exists(cfgName):
			__log__.Log(gmLog.lWarn, "config file %s not found." % cfgName)
		else:
			return cfgName

		# 8) ./base_name
		# last resort for inferior operating systems such as DOS/Windows
		cfgName = os.path.abspath(os.path.join(os.path.split(sys.argv[0])[0], base_name))
		if not os.path.exists(cfgName):
			__log__.Log(gmLog.lWarn, "config file %s not found." % cfgName)
		else:
			return cfgName

		# we still don't have a valid config file name ?!?
		# we can't help it but die
		__log__.Log(gmLog.lPanic, "Cannot run without any configuration file. Aborting.")
		return None
#---------------------------------------------------------------
# stuff below is just for reference
#---------------------------------------------------------------
#config = {}

# HACK FOR NOW
config = {'main.use_notebook':1, 'main.shadow':1, 'main.shadow.colour':(131, 129, 131), 'main.shadow.width':4}

def GetAllConfigs ():
    pool = gmPG.ConnectionPool ()
    conn = pool.GetConnection ('gmconfiguration')
    cur = conn.cursor ()
    cur.execute ("SELECT name, value, string FROM v_my_config")
    result = cur.fetchall ()
    pool.ReleaseConnection ('gmconfiguration')
    for row in result:
        if row[2] is None:
            config[row[0]] = row[1]
        else:
            config[row[0]] = row[2]

def SetConfig (key, value):
    pool = gmPG.ConnectionPool ()
    config[key] = value
    conn = pool.GetConnection ('gmconfiguration')
    cur = conn.cursor ()
    if type (value) == types.IntType:
        cur.execute ("UPDATE v_my_config SET value=%d WHERE name='%s'" % (value, key))
    elif type (value) == types.StringType:
        cur.execute ("UPDATE v_my_config SET string='%s' WHERE name='%s'" % (value, key))
    else:
        raise gmExceptions.ConfigError ('type not supported')
    pool.ReleaseConnection ('gmconfiguration')
#---------------------------------------------------------------
# MAIN
#---------------------------------------------------------------
if __name__ == "__main__":
	__log__.SetAllLogLevels(gmLog.lData)
	print "Testing gmCfg"
	print "============="
	gmDefCfg = cCfg()
else:
	gmDefCfg = cCfg()
#---------------------------------------------------------------
# TODO
#---------------------------------------------------------------
# - ACAP (application configuration access protocol)
# - on store():
# | context | option | value | data type (string, int, float only)
# - is there a way to retrieve stored comments so we can make a smart config manager ?
# - SELECT name, value FROM config WHERE value != default;

#---------------------------------------------------------------
# sample code
#---------------------------------------------------------------
# - do this:
"""
import gmCfg
__cfg__ = gmCfg.gmDefCfg

"""
# just by importing gmCfg will set up a basic default config file
# __cfg__ is just a convenient handle and could have any other name
#---------------------------------------------------------------
	# If the dbase variable is empty, then put the user name of the user
	# running the program into dbase.
#	if dbase == None or dbase == "":
#	    if os.environ.has_key("LOGNAME"):
#		dbase = os.environ["LOGNAME"]
#	    elif os.environ.has_key("USER"):
#		dbase = os.environ["USER"]
#	    elif os.environ.has_key("USERNAME"):
#		dbase = os.environ["USERNAME"]
#	    else:
#		dbase = "*UNKNOWN*"
