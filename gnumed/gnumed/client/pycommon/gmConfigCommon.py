"""GnuMed: Mid-level configuration editor object.

Theory of operation:

ConfigSourceDB/File holds config data (read from backend or file) and related
config definitions. Definitions are retrieved automatically from a given config
definition file (if available). See _defaultDefSourceTable below for standard file
names.

First get a list of available config parameters through getAllParamNames (returns
names + metadata), get the values using GetConfigData, change, check for validity
using isValid (if definition data and parameter definition is available) and 
set data using SetConfigData.
License: GNU Public License 
"""
#==================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/pycommon/gmConfigCommon.py,v $
__version__ = "$Revision: 1.7 $"
__author__ = "H.Berger,K.Hilbert"

import sys, os, string, types, pickle

from Gnumed.pycommon import gmLog, gmCfg

_log = gmLog.gmDefLog
if __name__ == '__main__':
	_log.SetAllLogLevels(gmLog.lData)
	_ = lambda x:x

_log.Log(gmLog.lData, __version__)
_cfg = gmCfg.gmDefCfgFile
_defaultDefSourceTable = {
	'DB:CURRENT_USER_CURRENT_WORKPLACE': 'config-definitions/DBDefault.definitions',
	'DB:CURRENT_USER_DEFAULT_WORKPLACE' : 'config-definitions/DBDefault.definitions',
	'DB:DEFAULT_USER_CURRENT_WORKPLACE' : 'config-definitions/DBDefault.definitions',
	'DB:DEFAULT_USER_DEFAULT_WORKPLACE' : 'config-definitions/DBDefault.definitions',
	'gnumed.conf': 'config-definitions/gnumed.conf.definitions'
}

###############################################################################
class ConfigSource:
	"""Base class for interface to access config data and definitions on a single 
	   configuration source (config file, user/workplace specific backend data
	   collection.
	   The source name will be used to retrieve the config definitions from
	   a config definition source (file, DB) automatically.
	"""
	
	_DefinitionSourceTable = None
	
	def __init__(self,aSourceType=None,aSourceName=None,aDataSource=None):
		self.mSourceType = aSourceType
		self.mSourceName = aSourceName
		self.mDataSource = aDataSource

		if ConfigSource._DefinitionSourceTable is None:
			ConfigSource._DefinitionSourceTable=self.__getDefinitionSourceTable()
		
		try:
			DefinitionSource = ConfigSource._DefinitionSourceTable[self.mSourceName]
			self.mDefinitionSource = ConfigDefinition(DefinitionSource)
		except:
			_log.Log(gmLog.lWarn, "No definition source found for %s" % self.mSourceName)
			self.mDefinitionSource = None 

	#---------------------------------------------------------------------
	# TODO : get definition source table from cfg file if available
	def __getDefinitionSourceTable(self):
		return _defaultDefSourceTable
			
	#------------------------------------------------------------------------
	def getParamType(self, aParam = None):
		""" get type of parameter value """

		# try to get the type from config definitions
		# if this fails, get last known type from config data dict 
		definitionType = None

		if not self.mDefinitionSource is None:
			definitionName = self.mDataSource.getRawName(aParam)
			definitionType = self.mDefinitionSource.getParamType(definitionName)

		if not definitionType is None:
			mType = definitionType
		else:
			mType = self.mDataSource.getParamType(aParam)

		return mType

	#------------------------------------------------------------------------
	def castType(self, aParam = None, aValue=None):
		""" cast type of entered parameter value to the previously existing type."""
					
		castType = self.getParamType(aParam)
		if castType == 'str_array':
			castedVal = string.split(aValue,'\n')
			if not type(castedVal) is types.ListType:
				castedVal = [str(castedVal)]
		elif castType == 'numeric':
			if not type(eval(aValue)) in (types.IntType, types.FloatType, types.LongType):
				castedVal = None
			else:
				castedVal = eval(aValue)
		elif castType == 'string':
			castedVal = str(aValue)

		return castedVal

	#----------------------------------------------------------------------
	def getDescription(self, aParam=None):
		"""
		Get parameter description either from config definition or from config data
		"""
		# if no parameter definition is available, get definition from data
		# source
		definitionName = self.mDataSource.getRawName(aParam)
		description = None
		if not self.mDefinitionSource is None:
			description = self.mDefinitionSource.getParamDescription(definitionName)
		
		if  description is None:
			description = self.mDataSource.getParamDescription(aParam)

		return description

	# here come the wrapper functions that link to config data and definition
	# objects
	#---------------------------------------------------------------------
	def getAllParamNames(self):
		"""
		Get all parameter names from backend or a file.
		Returns dict of names + metadata.
		format:
		dict {'name1': [namepart_2,namepart_1,owner,type,description],
		       'name2': [option,group,owner,type,description],...}
		usually the full name is a composition of namepart_1 +_2, 
		but don't rely on the order - it depends on whether you get 
		data from DB or file. type is the type as found in the data 
		(one of 'string', 'string_arr' or 'numeric'). description is the
		description supplied with the data, not the one given in the
		parameter definition file ! Use getDescription() to get the right 
		one.
		"""
		if not self.mDataSource is None:
			return self.mDataSource.getAllNames()
	#---------------------------------------------------------------------
	def setConfigData(self,aParam,aValue):
		"""
		Set config data for a aParam to aValue.
		"""
		return self.mDataSource.SetConfigData(aParam,aValue)
	#---------------------------------------------------------------------
	def getConfigData(self,aParam):
		"""
		Get config data for a aParam.
		"""
		return self.mDataSource.GetConfigData(aParam)

	#---------------------------------------------------------------------
	def addConfigParam(self,aParam,aType,aValue,aDescription):
		"""
		Adds config new config parameter.
		"""
		return self.mDataSource.AddConfigParam(aParam,aType,aValue,aDescription)
	#---------------------------------------------------------------------
	def getRawName(self,aParam):
		"""Get config data for a aParam."""
		return self.mDataSource.getRawName(aParam)
	#---------------------------------------------------------------------
	def hasDefinition(self):
		""" return true if config definition object is available"""
		return ( not self.mDefinitionSource is None)	
		
	#---------------------------------------------------------------------
	def hasParameterDefinition(self,aParam):
		"""
		Returns true if config definition is available for this
		parameter.
		"""
		return self.mDefinitionSource.hasParameter(aParam)

	#---------------------------------------------------------------------
	def isValid(self,aParam,aValue):
		"""
		Returns true if aValue matches config definition for this
		parameter.
		"""
		return self.mDefinitionSource.isValid(aParam,aValue)

		
###############################################################################
class ConfigSourceDB(ConfigSource):
	"""Interface to access config data and definitions in a single 
	   configuration user/workplace specific backend data collection.
	"""
	def __init__(self, aSourceName=None,aUser = None, aWorkplace = 'xxxDEFAULTxxx'):
		try:
			mConfigDataSource = ConfigDataDB(aUser,aWorkplace)
		except:	
			mConfigDataSource = None

		ConfigSource.__init__(self,"DB",aSourceName,mConfigDataSource)


###############################################################################
class ConfigSourceFile(ConfigSource):
	"""
	Interface to access config data and definitions in a config file.
	"""
	def __init__(self, aSourceName=None,aFileName=None):
		try:
			mConfigDataSource = ConfigDataFile(aFileName)		
		except:	
			mConfigDataSource = None

		ConfigSource.__init__(self,"FILE",aSourceName,mConfigDataSource)
			

	def GetFullPath(self):
		if not self.mDataSource is None:
			return self.mDataSource.GetFullPath()
		
###############################################################################
class ParameterDefinition:
	"""Describes a gnumed configuration parameter.
	"""
	def __init__(self,aParamName = None,aParamType = None,aValidValsList = None,aParamDescription = None):
		self.mName = aParamName
		self.mType = aParamType
		self.mDescription = aParamDescription
		# perhaps make this a class <validator>, too ?
		# - one method: bool isValid()
		# - derived classes for:
		#   validator -> string -> font
		#   validator -> string -> color
		#   validator -> numeric -> range
		#   ...
		self.mValidVals = aValidValsList

	#---------------------------------------------------------------------
	def isValid(self,aValue):
		if self.mType == "string":
			return self.__isString(aValue)
		elif self.mType == "str_array":
			return self.__isStringArray(aValue)
		elif self.mType == "numeric":
			return self.__isNumeric(aValue)
		else:
			_log.Log (gmLog.lPanic, "isValid %s - %s %s" % (self.mName, self.mType, aValue))
			return 0
			
	#---------------------------------------------------------------------
	def __isString(self,aValue):
		if type(aValue) == types.StringType or type (s) == types.UnicodeType:
			if self.mValidVals is None:
				return 1
			elif str(aValue) in (self.mValidVals):
				return 1
		return 0
	
	#---------------------------------------------------------------------
	def __isStringArray(self,aValue):
		# value must be a list and all elements must be strings
		if type(aValue) == types.ListType:
			for s in (aValue):
				if not (type(s) == types.StringType or type (s) == types.UnicodeType):
					return 0
			return 1
		return 0

	#---------------------------------------------------------------------
	def __isNumeric(self,aValue):
		if type(aValue) in (types.IntType, types.FloatType, types.LongType):
			if self.mValidVals is None:
				return 1
			elif str(aValue) in (self.mValidVals):
				return 1
		return 0

###############################################################################
# IDEAS: if no config definition is available, we should make the 
# data read-only by default, and only allow change after an explicit warning
# TODO : almost all
class ConfigDefinition:
	""" holds config definitions read from a file/DB.
	this will contain: 
		a) config parameter names
		b) config parameter description (optional)
		c) config parameter type
		d) config parameter valid values (if type is select_from_list)
		e) config information version (must match the version used in ConfigData)
	"""

	def __init__(self, aDefinitionSource=None):
		# get queries from configuration source (currently only files are supported)

		self.__mParameterDefinitions = {}
		self.__mVersion = None

		if aDefinitionSource is None:
			_log.Log(gmLog.lWarn, "No configuration definition source specified")
			# we want to return an error here 
			# in that case we'll have to raise an exception... can't return
			# anything else than None from an __init__ method
			raise TypeError, "No configuration definition source specified !"
		else:
			self.__mDefinitionSource = aDefinitionSource
			if not self.__getDefinitions():
				raise IOError, "cannot load definitions"
		
	#------------------------------------------------------------------------
	def hasParameter(self, aParameterName = None):
		return self.__mParameterDefinitions.has_key(aParameterName)
		
	#------------------------------------------------------------------------
	def isValid(self,aParameterName=None,aValue=None):
		if self.hasParameter(aParameterName):
			return self.__mParameterDefinitions[aParameterName].isValid(aValue)		
		else:
			return 0

	#------------------------------------------------------------------------
	def getParamType(self, aParameterName = None):
		if self.hasParameter(aParameterName):
			return self.__mParameterDefinitions[aParameterName].mType

	#------------------------------------------------------------------------
	def getParamDescription(self, aParameterName = None):
		if self.hasParameter(aParameterName):
			return self.__mParameterDefinitions[aParameterName].mDescription
						
	#------------------------------------------------------------------------
	def __getDefinitions(self):
		"""get config definitions"""

		# open configuration definition source
		try:
			cfgDefSource = gmCfg.cCfgFile(aFile = self.__mDefinitionSource, \
				flags=gmCfg.cfg_SEARCH_STD_DIRS | gmCfg.cfg_IGNORE_CMD_LINE)
			# handle all exceptions including 'config file not found'
		except:
			exc = sys.exc_info()
			_log.LogException("Unhandled exception while opening config file [%s]" % self.__mDefinitionSource, exc,verbose=0)
			return None

		cfgData = cfgDefSource.getCfg()
		groups = cfgDefSource.getGroups()

		if not '_config_version_' in (groups):
			_log.Log(gmLog.lWarn, "No configuration definition version defined.")
			_log.Log(gmLog.lWarn, "Matching definitions to config data is unsafe.")
			_log.Log(gmLog.lWarn, "Config data will be read-only by default.")
			self.mVersion = None
		else:
			version = cfgDefSource.get('_config_version_', "version")
			# we don't check for type in order to allow for versions like '1.20.1b'			 
			self.__mVersion = version
			_log.Log(gmLog.lInfo, "Found config parameter definition version %s in %s" % (version,self.__mDefinitionSource))


		# every group holds one parameter description
		# group name = parameter name
		for paramName in groups:
			# ignore config version group
			if paramName == '_config_version_':
				continue

			paramType = cfgDefSource.get(paramName, "type")			
			if paramType is None:
				continue
			
			# parameter description - might differ from that stored 
			# in backend tables (cfg_template)
			paramDescription = cfgDefSource.get(paramName, "description")
			if paramDescription is None:
				continue

			validValuesRaw = None
			# if valid value list is supplied, get it
			if "validvalue" in (cfgDefSource.getOptions(paramName)):
				validValuesRaw = cfgDefSource.get(paramName, "validvalues")
			# transform valid values to a list
			validVals = None
			if not validValuesRaw is None:
				if type(validValuesRaw) == types.ListType:
					validVals = validValuesRaw
			
			# add new entry to parameter definition dictionary
			self.__mParameterDefinitions
			self.__mParameterDefinitions[paramName] = ParameterDefinition(paramName,paramType,validVals,paramDescription)
		return 1

###############################################################################
# TODO: 
# -handle backend data modifications using backend notification
# -method to change/add new parameters

class ConfigData:
	""" 
    Base class. Derived classes hold config data for a particular 
	backend user/workplace combination, config file etc.	    
	this will contain: 
		a) config parameter names
		b) config parameter values
		c) config information version (must match the version used in ConfigDefinition)
	"""

	def __init__(self, aType = None):
		self.type = aType
		self.mConfigData = {}

# pure virtual methods
	def GetAllNames(self):
		pass

	def GetConfigData(self):
		pass

	def SetConfigData(self):
		pass    	

	def getRawName(self):
		pass

	def AddConfigParam(self):
		pass
		
	#---------------------------------------------------------------------
	def getParamType(self,aParameterName = None):
		"""
		Returns the parameter type as found in the data source.
		"""
		try:
			return self.mConfigData[aParameterName][3]
		except KeyError:
		# is it possible to have a parameter without type ??
		# TODO
			return None

	#---------------------------------------------------------------------
	def getParamDescription(self,aParameterName = None):
		"""
		Returns the parameter type as found in the data source.
		"""
		try:
			return self.mConfigData[aParameterName][4]
		except KeyError:
			return None


#--------------------------------------------------------------------------
class ConfigDataDB(ConfigData):
	""" 
	Class that holds config data for a particular user/workplace pair 
	"""
	# static class variables that hold links to backend and gmCfg
	# this will be shared by all ConfigDataDB objects
	# this assumes that there will always be only one backend config source
	_backend = None
	_dbcfg = None

	def __init__(self, aUser = None, aWorkplace = 'xxxDEFAULTxxx'):
		""" Init DB connection"""
		ConfigData.__init__(self,"DB")
		
		# get connection
		if ConfigDataDB._backend is None:
			ConfigDataDB._backend = gmPG.ConnectionPool()

		# connect to config database
		if ConfigDataDB._dbcfg is None:
			ConfigDataDB._dbcfg = gmCfg.cCfgSQL(
				aConn = self._backend.GetConnection('default'),
				aDBAPI = gmPG.dbapi
			)

		if ConfigDataDB._dbcfg is None:
			_log.Log(gmLog.lErr, "Cannot access configuration without database connection !")
			raise ConstructorError, "ConfigData.__init__(): need db conn"
			
		self.mUser = aUser
		self.mWorkplace = aWorkplace

	#---------------------------------------------------------------------
	def GetConfigData(self, aParameterName = None):
		"""
		Gets Config Data for a particular parameter. 
		Returns parameter value.
		"""
		try:
			name=self.mConfigData[aParameterName][0]
			cookie = self.mConfigData[aParameterName][1]
			result=ConfigDataDB._dbcfg.get(self.mWorkplace, self.mUser,cookie,name)
		except:
			_log.Log(gmLog.lErr, "Cannot get parameter value for [%s]" % aParameterName )
			return None
		return result
		
	#---------------------------------------------------------------------
	def SetConfigData(self, aParameterName, aValue):
		"""
		Sets Config Data for a particular parameter. 
		"""
		try:
			name=self.mConfigData[aParameterName][0]
			cookie = self.mConfigData[aParameterName][1]
	                rwconn = ConfigDataDB._backend.GetConnection(service = "default", readonly = 0)    

			result=ConfigDataDB._dbcfg.set(	workplace = self.mWorkplace, 
							user = self.mUser,
							cookie = cookie,
							option = name,
							value = aValue,
							aRWConn = rwconn )
			rwconn.close()		
			ConfigDataDB._backend.ReleaseConnection(service = "default")
		except:
			_log.Log(gmLog.lErr, "Cannot set parameter value for [%s]" % aParameterName )
			return None
		return 1
	#---------------------------------------------------------------------
	# aType is not used so far. Do we need it ?
	# TODO: maybe we could combine that with SetConfigData (the low level methods in gmCfg do add/update, anyways)
	def AddConfigParam(self, aParameterName, aType = None ,aValue=None,aDescription = None):
		"""
		Adds a new config parameter. 
		Note: You will have to re-read the cache (call GetAllNames())
		in order to change this parameter afterwards.
		"""
		# make sure that the pameter does not exist yet
		if self.mConfigData.has_key(aParameterName):
			return None
		
		# now we have to split the parameter name into 
		# option and cookie part
		
		pNameParts  = string.split(aParameterName,".")
		# check if we have a cookie
		if pNameParts[-1][0] == '_':
			cookie = pNameParts[-1][1:]
			option = string.join(pNameParts[:-1],".")
		else:
			cookie = None
			option = aParameterName
			
#		print "[%s, %s]" % (cookie, option)		
		if option is None:
			return None
		# now actually write the new parameter
		try:
			rwconn = ConfigDataDB._backend.GetConnection(service = "default", readonly = 0)    

			result=ConfigDataDB._dbcfg.set(	workplace = self.mWorkplace, 
							user = self.mUser,
							cookie = cookie,
							option = option,
							value = aValue,
							aRWConn = rwconn )
			rwconn.close()		
			ConfigDataDB._backend.ReleaseConnection(service = "default")
		except:
			_log.Log(gmLog.lErr, "Cannot set parameter value for [%s]" % aParameterName )
			return None
		# now we should re-read the name cache in order to have 
		# consistent data. Since we wont signal the frontend, we will
		# have to do this manually in the fronend 

		return 1
	#---------------------------------------------------------------------
	def getAllNames(self):
		"""
		fetch names and parameter data from backend. Returns list of
		parameter names where cookie and real name are concatenated.
		Refreshes the parameter cache, too.
		"""
		try:
			result=ConfigDataDB._dbcfg.getAllParams(self.mUser,self.mWorkplace)
		except:
			_log.Log(gmLog.lErr, "Cannot get config parameter names.")
			raise
		if not result:
			return None
		else:
			# gmCfg.getAllParams returns name,cookie, owner, type and description 
			# of a parameter. 
			# We combine name + cookie to one single name. If cookie == 'xxxDEFAULTxxx'
			# we set the last part of the name to "" (an empty part). This
			# must processed by the ConfigTree so that the empty part is not 
			# displayed. If the cookie is something else, we mark the cookie part
			# by a leading "._"
			mParamNames = []
			# for param in (result): why???
			for param in result:
				name = param[0]
				cookie = param[1]
				if cookie == 'xxxDEFAULTxxx':
					cookie_part = ""
				else:
					cookie_part = "._%s" % cookie

				newName = name + cookie_part
				# store data for every parameter in mConfigData
				self.mConfigData[newName]=param
				# add new name to list
				mParamNames.append(newName)
#DEBUG		
#		_log.Log (gmLog.lData, "%s" % self.mConfigData)

		return mParamNames

	#---------------------------------------------------------------------
	def getRawName(self,aParameterName = None):
		"""
		Returns the parameter name without possible cookie part(s).
		Needed to indentify matching config definition entry.
		"""
		try:
			return self.mConfigData[aParameterName][0]
		except KeyError:
			return None

#--------------------------------------------------------------------------
class ConfigDataFile(ConfigData):
	""" 
	Class that holds config data for a particular config file
	"""
	def __init__(self, aFilename = None):
		""" Init config file """
		ConfigData.__init__(self,"FILE")

		self.filename = aFilename
		self.__cfgfile = None
		self.fullPath = None
				
		# open config file
		try:
			self.__cfgfile = gmCfg.cCfgFile(aFile = self.filename)
			# this is a little bit ugly, but we need to get the full name of the
			# file because this depends on the installation/system settings
			# if no absolute path was specified, we get the config file gnumed
			# would find first which is what we want usually
			self.fullPath = self.__cfgfile.cfgName

		except:
			_log.LogException("Can't open config file !", sys.exc_info(), verbose=0)
			raise ConstructorError, "ConfigDataFile: couldn't open config file"

	#---------------------------------------------------------------------
	def GetFullPath(self):
		""" returns the absolute path to the config file in use"""
		return self.fullPath

	#---------------------------------------------------------------------
	def GetConfigData(self, aParameterName = None):
		"""
		Gets Config Data for a particular parameter. 
		Returns parameter value.
		"""
		name=self.mConfigData[aParameterName][0]
		group = self.mConfigData[aParameterName][1]
		try:
			result=self.__cfgfile.get(group,name)
		except:
			_log.Log(gmLog.lErr, "Cannot get parameter value for [%s]" % aParameterName )
			return None
		return result
		
	#---------------------------------------------------------------------
	def SetConfigData(self, aParameterName = None, aValue = None):
		"""
		Sets Config Data for a particular parameter. 
		"""
		option = self.mConfigData[aParameterName][0]
		group = self.mConfigData[aParameterName][1]
		try:
			result=self.__cfgfile.set(aGroup = group,
						anOption = option,
						aValue = aValue)
			self.__cfgfile.store()
		except:
			_log.Log(gmLog.lErr, "Cannot set parameter value for [%s]" % aParameterName )
			return None
		return 1

	#---------------------------------------------------------------------
	def AddConfigParam(self, aParameterName, aType = None ,aValue=None, aDescription =None):
		"""
		Adds a new config parameter. 
		"""
		pNameParts  = string.split(aParameterName,".")
		# check if we have a cookie
		option = pNameParts[-1:][1:]
		group = string.join(pNameParts[:-1],".")
		if option is None or group is None:
			return None

		try:
			result=self.__cfgfile.set(aGroup = group,
						anOption = option,
						aValue = aValue,
						aComment = aDescription)
			self.__cfgfile.store()
		except:
			_log.Log(gmLog.lErr, "Cannot set parameter value for [%s]" % aParameterName )
			return None
		return 1

	#---------------------------------------------------------------------
	def getAllNames(self):
		"""
		fetch names and parameter data from config file. Returns list of
		parameter names where group and option name are concatenated.
		"""
		
		# this returns name,cookie, owner (TODO), type and description 
		# of a parameter. 
		# We combine group + option name to one single name. 
		groups = self.__cfgfile.getGroups()
		if len(groups) == 0:
			return None
		mParamNames = []		
		for group in (groups):
			options = self.__cfgfile.getOptions(group)
			if len(options) == 0:
				continue
			else:
				for option in (options):			
					currType=type(self.__cfgfile.get(group,option))
					if currType in (types.IntType, types.FloatType, types.LongType):
						myType = 'numeric'
					elif currType is types.StringType:
						myType = 'string'
					elif currType is types.ListType:
						myType = 'str_array'
					else:
					# FIXME: we should raise an exception here or make the entry
					# read only since we don't know how to handle this entry
						mType = 'string'

					description = self.__cfgfile.getComment(group,option)
					if description is []:
						description = ''
					else:
						myDescription = string.join(description,'\n')
					optionData=[option,group,'',myType,myDescription]

					newName = group + '.' + option
					self.mConfigData[newName] = optionData
					mParamNames.append(newName)
			
#DEBUG		
#		_log.Log (gmLog.lData, "%s" % self.mConfigData)

		return mParamNames

	#---------------------------------------------------------------------
	def getRawName(self,aParameterName = None):
		"""
		Returns the parameter name without possible cookie part(s).
		Needed to indentify matching config definition entry.
		"""
		# since CfgFile does not know about cookies, just return 
		# the parameter name

		return aParameterName


#=========================================================================
def exportDBSet(filename,aUser = None, aWorkplace = 'xxxDEFAULTxxx'):
	"""
	Fetches a backend stored set of config options (defined by user and workplace)
	and returns it as a plain text file.
	NOTE: This will not write "valid value" information, since this is only
	hold in config definition files !
	Returns: 1 for success, 0 if no parameters were found, None on failure.
	"""
	try:
		expConfigSource = ConfigSourceDB("export",aUser,aWorkplace)
	except:
		_log.Log(gmLog.lErr, "Cannot open config set [%s@%s]." % (aUser,aWorkplace))
		return None
		
	try:
		file = open(filename,"w")
	except:
		_log.Log(gmLog.lErr, "Cannot open output file %s." % (filename))
		raise
		
	paramList = expConfigSource.getAllParamNames()
	if paramList is None:
		_log.Log(gmLog.lInfo, "DB-set [%s,%s]contained no data." % (aUser,aWorkplace))
		return 0
	text = ''
	for param in (paramList):
		description = expConfigSource.getDescription(param)
		cType = expConfigSource.getParamType(param)
		value = expConfigSource.getConfigData(param)
		# we try to dump human readable types as text, 
		# all other as a 'pickled' string
		if cType in ['string','numeric','str_array']:
			valuestr = value
		else:
			valuestr = pickle.dumps(value)
			
		file.write( "[%s]\ntype = %s\ndescription = %s\nvalue = %s\n\n" % \
			(param,cType,description,value))
	return len(paramList)
#-------------------------------------------------------------------------
def importDBSet(filename,aUser = None, aWorkplace = 'xxxDEFAULTxxx'):
	"""get config definitions from a file exported with 
	   exportDBSet()."""

	# open configuration definition source
	try:
		importFile = gmCfg.cCfgFile(aFile = filename, \
			flags= gmCfg.cfg_IGNORE_CMD_LINE)
		# handle all exceptions including 'config file not found'
	except:
		exc = sys.exc_info()
		_log.LogException("Unhandled exception while opening input file [%s]" % filename, exc,verbose=0)
		return None

	try:
		importConfigSource = ConfigSourceDB("export",aUser,aWorkplace)
	except:
		_log.Log(gmLog.lErr, "Cannot open config set [%s@%s]." % (aUser,aWorkplace))
		return None

	existingParamList = importConfigSource.getAllParamNames()

	importData = importFile.getCfg()
	groups = importFile.getGroups()
	# every group holds one parameter description
	# group name = parameter name
	successfully_stored = 0
	for paramName in groups:
		# ignore empty parameter names
		if paramName == "":
			continue
		paramType = importFile.get(paramName, "type")			
		if paramType is None:
			continue

		# parameter description - might differ from that stored 
		# in backend tables (cfg_template)
		paramDescription = importFile.get(paramName, "description")
		if paramDescription is None:
			continue


		paramValueStr = importFile.get(paramName, "value")
		if paramDescription is None:
			continue
		else:
			if paramType in ['string','numeric','str_array']:
				paramValue = eval(repr(paramValueStr))
			else:
				paramValue = pickle.loads(paramValueStr)
		# TODO: check if the parameter already exists with different type
		if existingParamList is not None and paramName in (existingParamList):
			if not importConfigSource.getParamType(paramName) == paramType:
				# if yes, print a warning
				# you will have to delete that parameter before
				# storing a different type
				_log.Log(gmLog.lWarn,
				"Cannot store config parameter [%s]: different type stored already." % paramName)
			else:
				# same type -> store new value	
				s=importConfigSource.setConfigData(paramName,paramValue)
				if s is None:
					_log.Log(gmLog.lWarn, 
						"Cannot store config parameter [%s] to set [%s@%s]." % (paramName,aUser,aWorkplace))
				else:
					successfully_stored = successfully_stored + 1
				
		else:
			# add new entry to parameter definition dictionary
			s=importConfigSource.addConfigParam(paramName,paramType,paramValue,paramDescription)
			if s is None:
				_log.Log(gmLog.lWarn, 
					"Cannot store config parameter [%s] to set [%s@%s]." % (paramName,aUser,aWorkplace))
			else:
				successfully_stored = successfully_stored + 1	
	return successfully_stored

#=============================================================
# $Log: gmConfigCommon.py,v $
# Revision 1.7  2006-10-25 07:19:03  ncq
# - no more gmPG
#
# Revision 1.6  2004/07/19 11:50:42  ncq
# - cfg: what used to be called "machine" really is "workplace", so fix
#
# Revision 1.5  2004/03/09 08:37:54  ncq
# - tiny cleanup
#
# Revision 1.4  2004/03/09 07:34:51  ihaywood
# reactivating plugins
#
# Revision 1.3  2004/03/04 01:38:49  ihaywood
# Now correctly validates unicode strings
#
# Revision 1.2  2004/02/25 09:46:21  ncq
# - import from pycommon now, not python-common
#
# Revision 1.1  2004/02/25 09:30:13  ncq
# - moved here from py-common
#
# Revision 1.13  2004/01/06 23:44:40  ncq
# - __default__ -> xxxDEFAULTxxx
#
# Revision 1.12  2003/11/18 18:54:06  hinnef
# rollback of errorneous commit
#
# Revision 1.10  2003/11/07 07:48:27  hinnef
# changed path to configfiles so that they will be found in client/etc/...
#
# Revision 1.9  2003/10/26 21:35:45  hinnef
# -bugfixes in AddConfigParam and importDBSet
#
# Revision 1.8  2003/10/26 01:38:06  ncq
# - gmTmpPatient -> gmPatient, cleanup
#
# Revision 1.7  2003/10/22 21:35:51  hinnef
# - fixed a bug in CastType that prevented numeric values to be written as such
#
# Revision 1.6  2003/10/13 21:02:55  hinnef
# - added GPL statement
#
# Revision 1.5  2003/10/02 20:02:28  hinnef
# small fixes to import/exportDBSet
#
