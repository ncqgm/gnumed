#!/usr/bin/env python

#==================================================================
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

<aDir> and <aName> will be derived automatically from the name of
the main script.

It is helpful to have a solid log target set up before importing this
module in your code. This way you will be able to see even those log
messages generated during module import.

Once your software has established database connectivity it can call
 activateDatabase()
to switch on database access for configuration options.

The default config data source is then switched to database access.

At any time can you force file or database access for a particular
configuration call via a parameter except before database access is
activated in which case the module will always use file access.

NOTE: DATABASE CONFIG DOES NOT WORK YET !

@copyright: GPL
"""
#==================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/python-common/Attic/gmCfg.py,v $
__version__ = "$Revision: 1.12 $"
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"

# standard modules
import os.path, fileinput, string, sys, shutil

# gnumed modules
import gmLog, gmCLI

_log = gmLog.gmDefLog
#================================
class cCfgBase:
	def __init__(self):
		pass

	def get(machine = None, user = None, cookie = None, option = None):
		pass

	def set(machine = None, user = None, cookie = None, option = None, value = None):
		pass

#================================
class cCfgFile:
	"""Handle common INI-style config files.

	The INI file structure follows the common rules. Option values
	can be strings or lists of strings. Lists are handled transparently.
	The list format is as follows:

	listname = $listname$ # comment
	item 1
	item 2
	item 3
	$listname$

	Config data is cached in the following layout:

	self._cfg_data	= {dict}
	|
	|-> 'comment'	= [list of strings]
	`-> 'groups'	= {dict}
	 |
	 |-> group 1	= {dict}
	 | ...
	 `-> group n
	  |
	  |-> 'comment' = [list of strings]
	  `-> 'options'	= {dict}
	   |
	   |-> option 1	= {dict}
	   | ...
	   `-> option n
	    |
		|-> 'comment' [list of strings]
		`-> 'value'
	"""
	_cfg_data = {}
	_modified = None
	#----------------------------
	def __init__(self, aPath = None, aFile = None):
		# get conf file name
		if not self.__get_conf_name(aPath, aFile):
			raise "cannot find config file"
		# load config file
		if not self.__parse_conf_file():
			raise "cannot parse config file"
	#----------------------------
	# API - access config data
	#----------------------------
	def getCfg(self):
		"""Return handle to entire config dict."""
		return self._cfg_data
	#----------------------------
	def get(self, aGroup = None, anOption = None):
		if not self._cfg_data['groups'].has_key(aGroup):
			_log.Log(gmLog.lWarn, 'group [%s] not found' % aGroup)
			return None

		group = self._cfg_data['groups'][aGroup]

		if not group['options'].has_key(anOption):
			_log.Log(gmLog.lWarn, 'option <%s> not found in group [%s]' % (anOption, aGroup))
			return None

		return group['options'][anOption]['value']
	#----------------------------
	def getComment(self, aGroup = None, anOption = None):
		# file level
		if aGroup == None:
			# return file level comment if available
			if self._cfg_data.has_key('comment'):
				return self._cfg_data['comment']
			else:
				_log.Log(gmLog.lWarn, 'file [%s] has no comment' % self.cfgName)
				return None

		# group or option level
		if self._cfg_data['groups'].has_key(aGroup):
			if anOption == None:
				if self._cfg_data['groups'][aGroup].has_key('comment'):
					return self._cfg_data['groups'][aGroup]['comment']
				else:
					_log.Log(gmLog.lWarn, 'group [%s] (in [%s]) has no comment' % (aGroup, self.cfgName))
					return None
			else:
				if self._cfg_data['groups'][aGroup]['options'].has_key(anOption):
					if self._cfg_data['groups'][aGroup]['options'][anOption].has_key('comment'):
						return self._cfg_data['groups'][aGroup]['options'][anOption]['comment']
					else:
						_log.Log(gmLog.lWarn, 'option [%s] in group [%s] (in [%s]) has no comment' % (anOption, aGroup, self.cfgName))
						return None
				else:
					_log.Log(gmLog.lErr, 'option [%s] not in group [%s] in file [%s]' % (anOption, aGroup, self.cfgName))
					return None
		else:
			_log.Log(gmLog.lErr, 'group [%s] not in file [%s]' % (aGroup, self.cfgName))
			return None
	#----------------------------
	# API - setting config items
	#----------------------------
	def set(self, aGroup = None, anOption = None, aValue = None, aComment = None):
		"""Set an option to an arbitrary type.

		This does not write the changed configuration to a file !
		"""
		# setting file level comment ?
		if aGroup == None:
			if aComment == None:
				_log.Log(gmLog.lErr, "don't know what to do with (aGroup = %s, anOption = %s, aValue = %s, aComment = %s)" % (aGroup, anOption, aValue, aComment))
				return None
			self._cfg_data['comment'] = [str(aComment)]
			self._modified = 1
			return 1

		# make sure group is there
		if not self._cfg_data['groups'].has_key(aGroup):
			self._cfg_data['groups'][aGroup] = {'options': {}}

		# setting group level comment ?
		if anOption == None:
			if aComment == None:
				_log.Log(gmLog.lErr, "don't know what to do with (aGroup = %s, anOption = %s, aValue = %s, aComment = %s)" % (aGroup, anOption, aValue, aComment))
				return None
			self._cfg_data['groups'][aGroup]['comment'] = aComment
			self._modified = 1
			return 1

		# setting option
		if aValue == None:
			_log.Log(gmLog.lErr, "don't know what to do with (aGroup = %s, anOption = %s, aValue = %s, aComment = %s)" % (aGroup, anOption, aValue, aComment))
			return None
		# make sure option is there
		if not self._cfg_data['groups'][aGroup]['options'].has_key(anOption):
			self._cfg_data['groups'][aGroup]['options'][anOption] = {}
		# set value
		self._cfg_data['groups'][aGroup]['options'][anOption]['value'] = aValue
		# set comment
		if not aComment == None:
			self._cfg_data['groups'][aGroup]['options'][anOption]['comment'] = aComment
		self._modified = 1
		return 1
	#----------------------------
	def store(self):
		"""Store changed configuration in config file.

		# FIXME: actually we need to reread the config file here before writing
		"""
		if not self._modified:
			_log.Log(gmLog.lInfo, "No changed items: nothing to be stored.")
			return 1

		new_name = "%s.new" % self.cfgName

		# open new file for writing
		new_file = open(new_name, "wb")

		# file level comment
		if self._cfg_data.has_key('comment'):
			if not self._cfg_data['comment'] == []:
				for line in self._cfg_data['comment']:
					new_file.write("# %s\n" % line)
				new_file.write("\n")

		for group in self._cfg_data['groups'].keys():
			gdata = self._cfg_data['groups'][group]
			if gdata.has_key('comment'):
				if not gdata['comment'] == []:
					for line in gdata['comment']:
						new_file.write("# %s\n" % line)

			new_file.write("[%s]\n" % group)
			for opt in gdata['options'].keys():
				odata = gdata['options'][opt]
				if odata.has_key('comment'):
					for line in odata['comment']:
						new_file.write("# %s\n" % line)
				if type(odata['value']) == type([]):
					new_file.write("%s = $%s$\n" % (opt, opt))
					for line in odata['value']:
						new_file.write("%s\n" % line)
					new_file.write("$%s$\n" % opt)
				else:
					new_file.write("%s = %s\n" % (opt, odata['value']))
			new_file.write("\n\n")

		new_file.close
		# rename new file to old file
		shutil.copyfile(new_name, self.cfgName)
		#os.remove(new_name)
		return 1
	#----------------------------
	# internal methods
	#----------------------------
	def __get_conf_name(self, aDir = None, aName = None):
		"""Try to construct a valid config file name."""

		_log.Log(gmLog.lData, '(<aDir=%s>, <aName=%s>)' % (aDir, aName))
		# 1) has the programmer manually specified a config file ?
		if aName != None:
			self.cfgName = os.path.abspath(aName)
			if os.path.exists(self.cfgName):
				_log.Log(gmLog.lData, 'Found config file [%s].' % self.cfgName)
				return 1
			else:
				_log.Log(gmLog.lWarn, 'config file [%s] not found' % self.cfgName)
				if aDir != None:
					self.cfgName = os.path.abspath(os.path.join(aDir, aName))
					if os.path.exists(self.cfgName):
						_log.Log(gmLog.lData, 'Found config file [%s].' % self.cfgName)
						return 1
					else:
						_log.Log(gmLog.lWarn, 'Config file [%s] not found. Aborting.' % self.cfgName)
						return None

		# 2) has the user manually supplied a config file on the command line ?
		if gmCLI.has_arg('--conf-file'):
			self.cfgName = gmCLI.arg['--conf-file']
			_log.Log(gmLog.lData, '--conf-file=%s' % self.cfgName)
			# file valid ?
			if os.path.exists(self.cfgName):
				_log.Log(gmLog.lData, 'Found config file [%s].' % self.cfgName)
				return 1
			else:
				_log.Log(gmLog.lErr, "Config file [%s] not found. Aborting." % self.cfgName)
				return None
		else:
			_log.Log(gmLog.lData, "No config file given on command line. Format: --conf-file=<config file>")

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
			_log.Log(gmLog.lInfo, "$(%s) = %s" % (env_key, os.environ[env_key]))
			self.cfgName = os.path.abspath(os.path.expanduser(os.path.join(os.environ[env_key], base_name)))
			if os.path.exists(self.cfgName):
				_log.Log(gmLog.lData, 'Found config file [%s].' % self.cfgName)
				return 1
			else:
				_log.Log(gmLog.lErr, "config file [%s] (in $%s) not found" % (self.cfgName, env_key))
		else:
			_log.Log(gmLog.lInfo, "$(%s) not set" % env_key)

		# 4) ~/.base_dir/base_name
		self.cfgName = os.path.expanduser(os.path.join('~', '.' + base_dir, base_name))
		if not os.path.exists(self.cfgName):
			_log.Log(gmLog.lWarn, "config file [%s] not found" % self.cfgName)
		else:
			_log.Log(gmLog.lData, 'Found config file [%s].' % self.cfgName)
			return 1

		# 5) ~/.base_name
		self.cfgName = os.path.expanduser(os.path.join('~', '.' + base_name))
		if not os.path.exists(self.cfgName):
			_log.Log(gmLog.lWarn, "config file [%s] not found" % self.cfgName)
		else:
			_log.Log(gmLog.lData, 'Found config file [%s].' % self.cfgName)
			return 1

		# 6) /etc/base_dir/base_name
		self.cfgName = os.path.join('/etc', base_dir, base_name)
		if not os.path.exists(self.cfgName):
			_log.Log(gmLog.lWarn, "config file [%s] not found" % self.cfgName)
		else:
			_log.Log(gmLog.lData, 'Found config file [%s].' % self.cfgName)
			return 1

		# 7) /etc/base_name
		self.cfgName = os.path.join('/etc', base_name)
		if not os.path.exists(self.cfgName):
			_log.Log(gmLog.lWarn, "config file [%s] not found" % self.cfgName)
		else:
			_log.Log(gmLog.lData, 'Found config file [%s].' % self.cfgName)
			return 1

		# 8) ./base_name
		# last resort for inferior operating systems such as DOS/Windows
		self.cfgName = os.path.abspath(os.path.join(os.path.split(sys.argv[0])[0], base_name))
		if not os.path.exists(self.cfgName):
			_log.Log(gmLog.lWarn, "config file [%s] not found" % self.cfgName)
		else:
			_log.Log(gmLog.lData, 'Found config file [%s].' % self.cfgName)
			return 1

		# we still don't have a valid config file name ?!?
		# we can't help it but die
		_log.Log(gmLog.lPanic, "Cannot run without any configuration file. Aborting.")
		return None
	#----------------------------
	def __parse_conf_file(self):
		if not os.path.exists(self.cfgName):
			_log.Log(gmLog.lWarn, "config file [%s] not found" % self.cfgName)

		_log.Log(gmLog.lData, "parsing config file [%s]" % self.cfgName)

		self._cfg_data['groups'] = {}

		curr_group = None
		curr_opt = None
		in_list = None
		comment_buf = []
		file_comment_buf = []
		for line in fileinput.input(self.cfgName):
			# remove trailing CR and/or LF
			line = string.replace(line,'\015','')
			line = string.replace(line,'\012','')
			# remove leading/trailing whitespace
			line = string.strip(line)

			# ignore empty lines
			if line == "":
				# if before first group
				if curr_group == None:
					if self._cfg_data.has_key('comment'):
						self._cfg_data['comment'].append(comment_buf)
					else:
						self._cfg_data['comment'] = comment_buf
					comment_buf = []
				continue

			#_log.Log(gmLog.lData, 'parsing line >>>%s<<<' % line)

			#-----------------------
			# are we inside a list ?
			if in_list:
				# end of list ?
				if line == ("$%s$" % curr_opt):
					in_list = None
					continue
				# else keep unmodified line as list item
				self._cfg_data['groups'][curr_group]['options'][curr_opt]['value'].append(line)
				continue

			#----------
			# comment ?
			if line.startswith('#') or line.startswith(';'):
				comment = string.strip(line[1:])
				if not comment == "":
					comment_buf.append(comment)
				continue

			#----------
			# [group] ?
			if line.startswith('['):
				tmp, comment = line.split(']', 1)
				if tmp == "[":
					_log.Log(gmLog.lErr, 'empty group definition "[]" not allowed')
					continue

				comment = string.strip(comment)
				if not comment == "":
					comment_buf.append(comment)

				curr_group = tmp[1:]
				if self._cfg_data['groups'].has_key(curr_group):
					_log.Log(gmLog.lWarn, 'duplicate group [%s] (file [%s]) - overriding options' % (curr_group, self.cfgName))
				else:
					self._cfg_data['groups'][curr_group] = {'options': {}}

				self._cfg_data['groups'][curr_group]['comment'] = comment_buf
				comment_buf = []
				continue

			#----------
			# option= ?
			if not curr_group:
				_log.Log(gmLog.lErr, 'option found before first group statement')
				continue

			#  normalize
			colon_pos = line.find(":")
			equal_pos = line.find("=")
			if colon_pos == -1 and equal_pos == -1:
				_log.Log(gmLog.lErr, 'option [%s] does not contain a separator ("=" or ":")' % line)
				continue
			if colon_pos < equal_pos:
				line = line.replace(':', '=', 1)

			#  separate <opt_name> = <opt_val # opt_comment>
			name, tmp = line.split('=', 1)
			name = string.strip(name)
			if name == "":
				_log.Log(gmLog.lErr, 'option name must not be empty')
				continue
			curr_opt = name
			if self._cfg_data['groups'][curr_group]['options'].has_key(curr_opt):
				_log.Log(gmLog.lWarn, 'duplicate option [%s] (group [%s], file [%s]) - overriding value' % (curr_opt, curr_group, self.cfgName))
			else:
				self._cfg_data['groups'][curr_group]['options'][curr_opt] = {}

			#  normalize again
			tmp = string.replace(tmp, ';', '#', 1)
			if tmp.find("#") == -1:
				val = tmp
				comment = ""
			else:
				#  separate <opt_val> # <opt_comment>
				val, comment = tmp.split('#', 1)
				comment = string.strip(comment)
			val = string.strip(val)
			if comment != "":
				comment_buf.append(comment)

			self._cfg_data['groups'][curr_group]['options'][curr_opt]['comment'] = comment_buf
			comment_buf = []

			# start of list ?
			if val == ("$%s$" % curr_opt):
				in_list = 1
				self._cfg_data['groups'][curr_group]['options'][curr_opt]['value'] = []
			else:
				self._cfg_data['groups'][curr_group]['options'][curr_opt]['value'] = val

		return 1
#================================
# main
#================================
if __name__ == '__main__':
	_log.SetAllLogLevels(gmLog.lData)
	try:
		myCfg = cCfgFile(aFile = sys.argv[1])
	except:
		exc = sys.exc_info()
		_log.LogException('unhandled exception', exc, fatal=1)

	print myCfg

	if myCfg == None:
		print "cannot open file"

	data = myCfg.getCfg()

	print "file: %s" % myCfg.cfgName
	if data.has_key('comment'):
		print "comment: %s" % data['comment']
	print "groups: %s" % str(data['groups'].keys())

	for group in data['groups'].keys():
		print "GROUP [%s]" % group
		gdata = data['groups'][group]
		if gdata.has_key('comment'):
			print " %s" % gdata['comment']

		for opt in gdata['options'].keys():
			odata = gdata['options'][opt]
			print "OPTION <%s> = %s" % (opt, odata['value'])
			if odata.has_key('comment'):
				print "  %s" % odata['comment']

	print myCfg.get('backend', 'hosts')

	myCfg.set("date", "modified", "jetzt", ["sollte eigentlich immer aktuell sein"])
	myCfg.store()
else:
	gmDefCfgFile = cCfgFile()

#=============================================================
# $Log: gmCfg.py,v $
# Revision 1.12  2002-09-12 10:07:29  ncq
# - properly normalize : -> =
#
# Revision 1.11  2002/09/12 09:17:11  ncq
# - windows unsucked
#
# Revision 1.10  2002/09/10 18:43:02  ncq
# - windows sucks !
#
# Revision 1.9  2002/09/10 18:31:45  ncq
# - windows is strange: os.rename -> shutil.copyfile + os.remove
#
# Revision 1.8  2002/09/10 18:15:28  ncq
# - os.rename() over existing files fails on non-UNIX
#
# Revision 1.7  2002/09/10 17:51:33  ncq
# - more sensible log levels for some data
#
# Revision 1.6  2002/09/08 15:55:47  ncq
# - added log cvs keyword
#
