#!/usr/bin/env python

__version__ = ""
__author__ = "H.Berger, S.Hilbert, K.Hilbert"

import sys, os, string,types
# location of our modules
if __name__ == "__main__":
	sys.path.append(os.path.join('..', '..', 'python-common'))
	#sys.path.append(os.path.join('..', '..', 'business'))
	#sys.path.append(os.path.join('.','modules'))

import gmLog
_log = gmLog.gmDefLog
if __name__ == '__main__':
	_log.SetAllLogLevels(gmLog.lData)

_log.Log(gmLog.lData, __version__)

if __name__ == "__main__":
	import gmI18N

import gmCfg
_cfg = gmCfg.gmDefCfgFile

from wxPython.wx import *

[	ConfigTreeCtrlID,
	ConfigTreeBoxID,
	ParamBoxID,
	ConfigEntryParamCtrlID,
	ButtonParamApplyID,
	ButtonParamRevertID,
	DescriptionBoxID,
	ConfigDescriptionTextID
] = map(lambda _init_ctrls: wxNewId(), range(8))

#================================================================
class cConfTree(wxTreeCtrl):
	"""This wxTreeCtrl derivative displays a tree view of configuration 
	parameter names.
	"""
	def __init__(self, parent, id, aConn = None,size=wxDefaultSize,pos=wxDefaultPosition,
				style=None,configInfo = None,rootLabel = "",paramWidgets=None):
		"""Set up our specialised tree."""

		self.paramTextCtrl = paramWidgets[0]
		self.paramDescription = paramWidgets[1]
		self.mConfData = configInfo[0]
		self.mConfDefinition = configInfo[1]
		self.rootLabel = rootLabel

		wxTreeCtrl.__init__(self, parent, id, pos, size, style)

		self.root = None
		self.param_list = None
		# currently selected parameter/subtree
		self.currSelParam = None
		self.currSelSubtree = None

		# connect handler
		EVT_TREE_ITEM_ACTIVATED (self, self.GetId(), self.OnActivate)
		EVT_RIGHT_DOWN(self,self.OnRightDown)

	#------------------------------------------------------------------------
	def update(self):

		if self.param_list is not None:
			del self.param_list

		if self.__populate_tree() is None:
			return None

		return 1
	#------------------------------------------------------------------------
	def __populate_tree(self):
		# FIXME: TODO ALL !
		
		# clean old tree
		if not self.root is None:
			self.DeleteAllItems()
            
		# init new tree
		self.root = self.AddRoot(self.rootLabel, -1, -1)
		self.SetPyData(self.root, {'type': 'root', 'name': self.rootLabel})
		self.SetItemHasChildren(self.root, FALSE)

		# now get subtrees for four maingroups (see __init__)

		for nodeDescription in (self.mConfData.keys()) :

			# get subtree
			subTree = self.__getSubTree(nodeDescription)
			node = self.AppendItem(self.root, nodeDescription)
			# store node description
			self.SetPyData(node, {'type': 'defaultSubtree', 'name': nodeDescription})
			# don't add empty subtrees, just display their subtree root node
			if subTree is None:
				self.SetItemHasChildren(node, FALSE)
				continue
			else:
				self.__addSubTree(node,subTree)
				self.SortChildren(node)
				self.SetItemHasChildren(node, TRUE)
						
		self.SetItemHasChildren(self.root, TRUE)
		self.SortChildren(self.root)
		# and uncollapse
		self.Expand(self.root)

		return 1
	#------------------------------------------------------------------------
	# this must be reentrant as we will iterate over the tree branches
	def __addSubTree(self,aNode=None, aSubTree=None):
		"""
		adds a subtree of parameter names to an existing tree. 
		return resulting tree.
		"""
#DEBUG
#		_log.Log(gmLog.lInfo, "subTree %s" % str(aSubTree))
		
		# check if subtree is empty
		if aSubTree[1] == {}:
			return None

		# check if subtree has children
		childrenList = aSubTree[1].keys()
		if childrenList is None:
			return None
		self.SetItemHasChildren(aNode, TRUE)

		# add every child as new node, add child-subtrees as subtree
		# reiterating this method
		for subTreeNode in childrenList:
			nodeEntry = aSubTree[1][subTreeNode]
			nodeName = nodeEntry[2]						
#DEBUG
#			_log.Log(gmLog.lInfo, "Node: %s Name: %s" % (str(aNode),nodeName) )
			node = self.AppendItem(aNode, nodeName)
			self.SetPyData(node, nodeEntry[0])
			self.SetItemHasChildren(node, FALSE)
			# now add subTrees
			if not nodeEntry[1] == {}:
				self.__addSubTree(node,nodeEntry)
				self.SortChildren(node)
				
	#------------------------------------------------------------------------
	def __getSubTree(self,nodeDescription):
		"""
		get a subtree from the backend via ConfigData layer.
		the subtree must have a special structure (see addTreeItem).
		"""
		# get all parameter names
		tmpParamList = self.mConfData[nodeDescription].getAllNames()
		if tmpParamList is None:
			return None

#DEBUG
#		_log.Log(gmLog.lInfo, "paramList %s" % str(tmpParamList))
		# convert name list to a tree structure
		currSubTree = [None,{},""]
		# add each item 
		# attach parameter name (= reference for ConfigData) and subtree as object
		for paramName in (tmpParamList):
			self.__addTreeItem(currSubTree,paramName,
				{'type': 'parameter', 'ref': paramName, 'subtree': nodeDescription})

		return currSubTree			

	#------------------------------------------------------------------------
	def __addTreeItem(self,aSubTree, aStructuredName,object=None):
		"""
		adds a name of the form "a.b.c.d" to a dict so that 
		dict['a']['b']['c']['d'] is a valid tree entry
		each subTree entry consists of a 3 element list:
		element [0] is an optional arbitrary object that should be connected 
		with the tree element(ID, etc.), element [1] a dictionary 
		holding the children of this element (again elements of type subTree)
		list element [3] is the branch name
		"""		
		nameParts = string.split(str(aStructuredName), '.')

		tmpFunc = "aSubTree"
		tmpDict = None
		branchName = ""
		# loop through all name parts
		for part in (nameParts):
			#recreate branch name
			if branchName == "":
				branchName = branchName + part
			else:
				branchName = branchName + "." + part			
			# get subtree dict
			tmpDict = eval(tmpFunc)[1]
			if not tmpDict.has_key(part):
				# initialize new branch
				tmpDict[part]=[]
				tmpDict[part].append({ 'type': 'branch', 'name': branchName })
				tmpDict[part].append({})
				tmpDict[part].append(part)
			# set new start for branching nodes
			tmpFunc = tmpFunc + "[1]['%s']" % part
		# set object
		eval(tmpFunc)[0]=object
		return aSubTree
	#------------------------------------------------------------------------

	def SaveCurrParam(self):
		if not (self.currSelParam is None or self.currSelSubtree is None):
			# get new value
			val = self.paramTextCtrl.GetValue()
			newValue = self.__castType(self.currSelSubtree,self.currSelParam,val)
			if newValue is None:
				self.__show_error('Type of entered value is not compatible with type expected.')
				
			# config definition object
			confDefinition = self.mConfDefinition[self.currSelSubtree]
			# if there is no config definition, ask the user if the
			# new value should be stored unchecked
			if confDefinition is None or not confDefinition.hasParameter(self.currSelParam):
				if self.__show_question(
"""There is no config definition for this parameter.
This means that it can't be checked for validity. 
Anyway store parameter ?"""):
					self.mConfData[self.currSelSubtree].SetConfigData(self.currSelParam,newValue)
					# reshow new data to mark it non modified
					self.__show_parameter(self.currSelSubtree,self.currSelParam)
				return 

			# else check parameter for validity
			if confDefinition.isValid(self.currSelParam,newValue):
				self.mConfData[self.currSelSubtree].SetConfigData(self.currSelParam,newValue)
				# reshow new data to mark it non modified
				self.__show_parameter(self.currSelSubtree,self.currSelParam)
			else:
				# TODO: display some hint on what could be wrong
				self.__show_error('Entered value is not valid.')

	#------------------------------------------------------------------------
	def OnActivate (self, event):
		item = event.GetItem()
		data = self.GetPyData(item)
#DEBUG
#		_log.Log(gmLog.lInfo, "ItemData %s" % str(data))

		self.paramDescription.Clear()
		self.paramTextCtrl.SetEditable(0)
		type = data['type']
		if type == 'parameter':
			# ref is the parameter name for use in ConfigData Object
			self.currSelParam = data['ref']
			# Config Data subtree
			self.currSelSubtree = data ['subtree']
			self.__show_parameter(self.currSelSubtree,self.currSelParam)
			return 1
		elif type == 'branch':
			message=_("(Branch)")
		elif type == 'defaultSubtree':
			message=_("(Subtree root)")
		elif type == 'root':
			message=_("(Config parameter tree for current/default user and machine)")
		# show message
		self.paramTextCtrl.ShowMessage(message)
		# expand/unexpand node if it has children
		if self.ItemHasChildren(item):
			if self.IsExpanded(item):
				self.Collapse(item)
			else:
				self.Expand(item)
		return 1

	#--------------------------------------------------------
	def OnRightDown(self,event):
		position = event.GetPosition()
#DEBUG
		_log.Log(gmLog.lInfo, "Right clicked (x:%s y:%s)" % (str(position.x),str(position.y)))
		(item,flags) = self.HitTest(position)
#DEBUG
		_log.Log(gmLog.lInfo, "clicked item (%s %s)" % (str(item),str(flags)))
#		if flags & (wxTREE_HITTEST_ONITEMLABEL) == TRUE:
		self.SelectItem(item)


	#------------------------------------------------------------------------
	def __show_parameter(self,aSubtree=None, aParam=None):	
			# get the parameter value + metadata
			confData = self.mConfData[aSubtree].GetConfigData(aParam)
			# extract description from metadata
			description = confData[1][4]
#DEBUG
#			_log.Log(gmLog.lInfo, "VALUE %s" % str(confData))
			self.paramTextCtrl.ShowParam(confData)
			self.paramTextCtrl.SetEditable(1)
			self.paramDescription.SetValue(description)


	#------------------------------------------------------------------------
	def __show_error(self, aMessage = None, aTitle = ''):
			# sanity checks
			tmp = aMessage
			if aMessage is None:
				tmp = _('programmer forgot to specify error message')

			tmp = tmp + _("\n\nPlease consult the error log for further information !")

			dlg = wxMessageDialog(
				NULL,
				tmp,
				aTitle,
				wxOK | wxICON_ERROR
			)
			dlg.ShowModal()
			dlg.Destroy()
			return 1

	#------------------------------------------------------------------------
	def __show_question(self, aMessage = None, aTitle = ''):
			# sanity checks
			tmp = aMessage
			if aMessage is None:
				tmp = _('programmer forgot to specify question')

			dlg = wxMessageDialog(
				NULL,
				tmp,
				aTitle,
				wxYES_NO | wxICON_EXCLAMATION | wxNO_DEFAULT
			)
			result = dlg.ShowModal()
			dlg.Destroy()
			if result == wxID_YES:
				return 1
			else: 
				return 0

	#------------------------------------------------------------------------
	def __castType(self,aSubtree = None, aParam = None, aValue=None):
		# TODO: get type from definition, more types
		# get last type from config data dict 
		lastType = self.mConfData[aSubtree].mConfigData[aParam][3]
		if lastType == 'str_array':
			castedVal = string.split(aValue,'\n')
			if not type(castedVal) is types.ListType:
				castedVal = [str(castedVal)]
		elif lastType == 'numeric':
			if not type(eval(aValue)) in (types.IntType, types.FloatType, types.LongType):
				castedVal = None
			else:
				castedVal = aValue
		elif lastType == 'string':
			castedVal = str(aValue)

		return castedVal
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
		if queryCfgSource is None:
			_log.Log(gmLog.lWarn, "No configuration definition source specified")
			# we want to return an error here 
			# in that case we'll have to raise an exception... can't return
			# anything else than None from an __init__ method
			raise TypeError, "No configuration definition source specified !"
		else:
			self.__mDefinitionSource = aDefinitionSource
			if not self.__getDefinitions():
				raise IOError, "cannot load definitions"
		
		self.__mParameterDefinitions = {}
		self.__mVersion = None
	#------------------------------------------------------------------------
	def hasParameter(self, aParameterName = None):
		return self.__mParameterDefinitions.has_key(aParameterName)
	#------------------------------------------------------------------------
	def isValid(self,aParameterName=None,aValue=None):
		return 1

	#------------------------------------------------------------------------
	def __getDefinitions(self):
		"""get config definitions"""

		# open configuration source
		try:
			cfgSource = gmCfg.cCfgFile(aFile = self.__mDefinitionSource)
			# handle all exceptions including 'config file not found'
		except:
			exc = sys.exc_info()
			_log.LogException("Unhandled exception while opening config file [%s]" % self.__mDefinitionSource, exc, verbose=1)
			return None

		cfgData = cfgSource.getCfg()
		groups = cfgSource.getGroups()

		if not groups.has_key('_config_version_'):
			_log.Log(gmLog.lWarn, "No configuration definition version defined.")
			_log.Log(gmLog.lWarn, "Matching definitions to config data is unsafe.")
			_log.Log(gmLog.lWarn, "Config data will be read-only by default.")
			self.mVersion = None
		else:
			version = cfgSource.get(groups['_config_version_'], "version")
			# we don't check for type in order to allow for versions like '1.20.1b'			 
			del groups[_config_version_]
			self.__mVersion = version
			_log.Log(gmLog.lInfo, "Found config parameter definition version %s." % version)


		# every group holds one parameter description
		# group name = parameter name
		for paramName in groups:
			paramType = cfgSource.get(entry_group, "type")
			# groups not containing queries are silently ignored
			continue

			# parameter description - might differ from that stored 
			# in backend tables (cfg_template)
			paramDescription = cfgSource.get(entry_group, "description")
			continue

			# if valid value list is supplied, get it
			validValuesRaw = cfgSource.get(entry_group, "validvalues")
			# transform valid values to a list
			if not validValuesRaw is None:
				if type(validValuesRaw) == types.ListType:
					validVals = validValuesRaw
				else:
					validVals = string.split(validValuesRaw,',')
			continue

			# add new entry to parameter definition dictionary
			self.__mParameterDefinitions[paramName] = ParameterDefinition(paramName,paramType,validVals,paramDescription)

###############################################################################
# TODO: 
# -handle backend data modifications using backend notification
# -method to change/add new parameters

class ConfigData:
	""" 
    Base class. Derived classes hold config data for a particular 
	backend user/machine combination, config file etc.	    
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

#--------------------------------------------------------------------------
class ConfigDataDB(ConfigData):
	""" 
	Class that holds config data for a particular user/machine pair 
	"""
	# static class variables that hold links to backend and gmCfg
	# this will be shared by all ConfigDataDB objects
	# this assumes that there will always be only one backend config source
	_backend = None
	_dbcfg = None

	def __init__(self, aType = "DB", aUser = None, aMachine = '__default__'):
		""" Init DB connection"""
		ConfigData.__init__(self,aType)
		
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
		self.mMachine = aMachine

	def GetConfigData(self, aParameterName = None):
		"""
		Gets Config Data for a particular parameter. 
		Returns a tuple consisting of the value and a list of metadata 
		(name,cookie, owner, type and description)
		"""
		name=self.mConfigData[aParameterName][0]
		cookie = self.mConfigData[aParameterName][1]
		try:
			result=ConfigDataDB._dbcfg.get(self.mMachine, self.mUser,cookie,name)
		except:
			_log.Log(gmLog.lErr, "Cannot get parameter value for [%s]" % aParameterName )
		
		return (result,self.mConfigData[aParameterName])
		
	def SetConfigData(self, aParameterName, aValue):
		"""
		Sets Config Data for a particular parameter. 
		"""
		name=self.mConfigData[aParameterName][0]
		cookie = self.mConfigData[aParameterName][1]
		try:
	                rwconn = ConfigDataDB._backend.GetConnection(service = "default", readonly = 0)    

			result=ConfigDataDB._dbcfg.set(	machine = self.mMachine, 
							user = self.mUser,
							cookie = cookie,
							option = name,
							value = aValue,
							aRWConn = rwconn )
			rwconn.close()		
			ConfigDataDB._backend.ReleaseConnection(service = "default")
		except:
			_log.Log(gmLog.lErr, "Cannot set parameter value for [%s]" % aParameterName )

	def getAllNames(self):
		"""
		fetch names and parameter data from backend. Returns list of
		parameter names where cookie and real name are concatenated.
		"""
		try:
			result=ConfigDataDB._dbcfg.getAllParams(self.mUser,self.mMachine)
		except:
			_log.Log(gmLog.lErr, "Cannot get config parameter names.")
			raise
		if not result:
			return None
		else:
			# gmCfg.getAllParams returns name,cookie, owner, type and description 
			# of a parameter. 
			# We combine name + cookie to one single name. If cookie == '__default__'
			# we set the last part of the name to "" (an empty part). This
			# must processed by the ConfigTree so that the empty part is not 
			# displayed. If the cookie is something else, we mark the cookie part
			# by a leading "._"
			mParamNames = []
			# for param in (result): why???
			for param in result:
				name = param[0]
				cookie = param[1]
				if cookie == '__default__':
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

#--------------------------------------------------------------------------
class ConfigDataFile(ConfigData):
	""" 
	Class that holds config data for a particular config file
	"""
	def __init__(self, aType = "FILE", aFilename = None):
		""" Init config file """
		ConfigData.__init__(self,aType)

		self.filename = aFilename
		self.__cfgfile = None
		
		# open config file
		try:
			self.__cfgfile = gmCfg.cCfgFile(aFile = self.filename)
		except:
			_log.LogException("Can't open config file !", sys.exc_info(), verbose=1)

		# this is a little bit ugly, but we need to get the full name of the
		# file because this depends on the installation/system settings
		# if no absolute path was specified, we get the config file gnumed
		# would find first which is what we want usually
		self.fullPath = self.__cfgfile.cfgName

	def GetFullPath(self):
		""" returns the absolute path to the config file in use"""
		return self.fullPath

	def GetConfigData(self, aParameterName = None):
		"""
		Gets Config Data for a particular parameter. 
		Returns a tuple consisting of the value and a list of metadata 
		(name,cookie, owner, type and description)
		"""
		name=self.mConfigData[aParameterName][0]
		group = self.mConfigData[aParameterName][1]
		try:
			result=self.__cfgfile.get(group,name)
		except:
			_log.Log(gmLog.lErr, "Cannot get parameter value for [%s]" % aParameterName )
		
		return (result,self.mConfigData[aParameterName])
		
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
		return 1

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

###############################################################################
class cParamCtrl(wxTextCtrl):
	def __init__(self, parent, id,value,pos,size,style,type ):
		wxTextCtrl.__init__(self, parent, -1, value="",style=style)		
		self.parent = parent

	def ShowParam(self,aParam=None,aSubTree=None):
		self.Clear()
		if aParam is None:
			return
		# store current parameter for later use
		self.currParam = aParam
		# get metadata
		metadata = aParam[1]
		value = aParam[0]
		type = metadata[3]
		name = metadata[0] + '.' + metadata[1]
#		self.parent.configEntryParamBox.SetTitle(_("Parameter") + ": " + name)
		if type == 'string':
			self.SetValue(value)
		elif type == 'str_array':
		# we can't use AppendText here because that would mark the value
		# as modified 
			all = ''
			for line in (value):
				all = all + line + '\n'
			self.SetValue(all)			
		elif type == 'numeric':
			self.SetValue(str(value))
			
	def ShowMessage(self,aMessage=""):
		self.currParam = None
		self.Clear()
		self.SetValue(aMessage)


	def RevertToSaved(self):
		if not self.currParam is None:
			self.ShowParam(self.currParam)

###############################################################################
# TODO: -a MenuBar allowing for import, export and options
# 		-open a connection to backend via gmCfg
class gmConfigEditorPanel(wxPanel):
	def __init__(self, parent, aUser,aMachine):
		wxPanel.__init__(self, parent, -1)

		self.currUser = aUser
		self.currMachine = aMachine
		# init data structures
		# initialize the objects holding data on the subtrees
		# add default subtrees root nodes if possible
		#   default entries in root:
		# 	 -default config file (usually ~/.gnumed/gnumed.conf)
		#	 -current user, current machine
		#	 -current user, default machine
		#	 -default user, current machine
		#	 -default user, default machine
		self.mConfData = {}
		# if we pass no config file name, we get the default cfg file
		cfgFile = ConfigDataFile()
		# now get the absolute path of the default cfg file
		self.mConfData['FILE:%s' % cfgFile.GetFullPath()] = cfgFile
		if not (self.currUser is None or self.currMachine is None) :
			self.mConfData['DB:CURRENT_USER_CURRENT_MACHINE'] = ConfigDataDB(aMachine=self.currMachine)
		if not (self.currUser is None) :
			self.mConfData['DB:CURRENT_USER_DEFAULT_MACHINE'] = ConfigDataDB()
		if not (self.currMachine is None) :
			self.mConfData['DB:DEFAULT_USER_CURRENT_MACHINE'] = ConfigDataDB(aUser='__default__',aMachine=self.currMachine)
		# this should always work
		self.mConfData['DB:DEFAULT_USER_DEFAULT_MACHINE'] = ConfigDataDB(aUser='__default__')
		# setup config definitions 
		self.mConfDefinitions = {}
		for k in self.mConfData.keys():
		# TODO: here we should add some real config source
			self.mConfDefinitions[k]=None
		
# main sizers
		self.mainSizer = wxBoxSizer(wxHORIZONTAL)
		self.rightSizer = wxBoxSizer(wxVERTICAL)

# selected parameter
		self.configEntryParamBox = wxStaticBox( self, ParamBoxID, _("Parameters") )
		self.configEntryParamBoxSizer = wxStaticBoxSizer( self.configEntryParamBox, wxHORIZONTAL )

		self.configEntryParamCtrl = cParamCtrl( parent = self, 
						id = ConfigEntryParamCtrlID, 
						pos = wxDefaultPosition, 
						size = wxSize(250,200),
						value = "" , 
						style = wxLB_SINGLE,
						type = None)
		
		self.paramButtonSizer = wxBoxSizer(wxHORIZONTAL)
		self.paramCtrlSizer = wxBoxSizer(wxVERTICAL)
		self.buttonApply = wxButton(parent=self,
					id = ButtonParamApplyID,
					label = "Apply changes" )
		self.buttonRevert = wxButton(parent=self,
					id = ButtonParamRevertID,
					label = "Revert to saved" )
		
		EVT_BUTTON(self,ButtonParamApplyID,self.ApplyChanges)
		EVT_BUTTON(self,ButtonParamRevertID,self.RevertChanges)


# parameter description
		self.configEntryDescriptionBox = wxStaticBox( self, DescriptionBoxID, _("Parameter Description") )
		self.configEntryDescriptionBoxSizer = wxStaticBoxSizer( self.configEntryDescriptionBox, wxHORIZONTAL )

		self.configEntryDescription = wxTextCtrl(parent = self, 
							id = ConfigDescriptionTextID,
							pos = wxDefaultPosition, 
							size = wxSize(250,100),
							style = wxTE_READONLY | wxLB_SINGLE,
							value ="" )
		self.configEntryDescriptionBoxSizer.AddWindow( self.configEntryDescription, 1, wxALIGN_CENTRE|wxALL|wxEXPAND, 2 )
# static box for config tree
		self.configTreeBox = wxStaticBox( self, ConfigTreeBoxID, _("Config Options") )
		self.configTreeBoxSizer = wxStaticBoxSizer( self.configTreeBox, wxHORIZONTAL )
		
# config tree        
		rootLabel = "%s@%s" % (self.currUser,self.currMachine)
		self.configTree = cConfTree( parent = self,
						id = ConfigTreeCtrlID ,
						pos = wxPoint(0, 0), 
						size = wxSize(200, 300),
						style = wxTR_HAS_BUTTONS|wxTAB_TRAVERSAL,
						configInfo = [self.mConfData,self.mConfDefinitions],
						rootLabel = rootLabel,
						paramWidgets=(self.configEntryParamCtrl,self.configEntryDescription)
						)
		self.configTree.SetFocus()
		self.configTreeBoxSizer.AddWindow( self.configTree, 1, wxALIGN_CENTRE|wxALL|wxEXPAND, 5 )

		self.paramCtrlSizer.AddWindow(self.configEntryParamCtrl,1,wxALIGN_CENTRE|wxALL|wxEXPAND, 2 )
		self.paramButtonSizer.AddWindow(self.buttonApply,1,wxALIGN_LEFT|wxALL|wxEXPAND, 2 )
		self.paramButtonSizer.AddWindow(self.buttonRevert,1,wxALIGN_RIGHT|wxALL|wxEXPAND, 2 )
		self.paramCtrlSizer.Add(self.paramButtonSizer,0,wxALIGN_BOTTOM, 2 )
		self.configEntryParamBoxSizer.Add(self.paramCtrlSizer , 1, wxALIGN_CENTRE|wxALL|wxEXPAND, 2 )

# add right panels to right sizer
		self.rightSizer.Add(self.configEntryParamBoxSizer, 1, wxEXPAND, 0)
		self.rightSizer.Add(self.configEntryDescriptionBoxSizer, 1, wxEXPAND, 0)

# add widgets to main sizer		
		self.mainSizer.Add(self.configTreeBoxSizer, 1, wxEXPAND, 0)
		self.mainSizer.Add(self.rightSizer, 1, wxEXPAND, 0)
		self.SetAutoLayout(1)
		self.SetSizer(self.mainSizer)
		self.mainSizer.Fit(self)
		self.mainSizer.SetSizeHints(self)
		self.Layout()
		self.configTree.update()

	def ApplyChanges(self,event):
		if self.configEntryParamCtrl.IsModified():
			self.configTree.SaveCurrParam()

	def RevertChanges(self,event):
		self.configEntryParamCtrl.RevertToSaved()		

#================================================================
# MAIN
#----------------------------------------------------------------
if __name__ == '__main__':
	import gmPG
	import gmPlugin, gmGuiBroker
	_log.Log (gmLog.lInfo, "starting config browser")

	if _cfg is None:
		_log.Log(gmLog.lErr, "Cannot run without config file.")
		sys.exit("Cannot run without config file.")
	
	workplace = raw_input("Please enter a workplace name: ")
	# catch all remaining exceptions
	try:
		application = wxPyWidgetTester(size=(640,480))
		application.SetWidget(gmConfigEditorPanel,"test-doc",workplace)
		application.MainLoop()
	except:
		_log.LogException("unhandled exception caught !", sys.exc_info(), verbose=1)
		# but re-raise them
		raise

	_log.Log (gmLog.lInfo, "closing config browser")

else:
	import gmPlugin, gmGuiBroker,gmPG


	class gmConfigRegistry(gmPlugin.wxNotebookPlugin):
		def name (self):
			return _("Setup")

		def GetWidget (self, parent):
			# get current workplace name
			self.gb = gmGuiBroker.GuiBroker()
			workplace = self.gb['workplace_name']
			currUser = self.gb['currentUser']

			self.panel = gmConfigEditorPanel(parent,currUser,workplace)
			return self.panel

		def MenuInfo (self):
			return ('tools', _('&ConfigRegistry'))

		def ReceiveFocus(self):
			self.panel.configTree.update()
			return 1

#------------------------------------------------------------                   
# $Log: gmConfigRegistry.py,v $
# Revision 1.4  2003-06-26 21:41:51  ncq
# - fatal->verbose
#
# Revision 1.3  2003/06/26 04:18:40  ihaywood
# Fixes to gmCfg for commas
#
# Revision 1.2  2003/06/10 09:56:31  ncq
# - coding style, comments, tab name
#
# Revision 1.1  2003/06/03 21:50:44  hinnef
# - now we can store changed values to file/backend
#
# Revision 1.7  2003/05/22 21:19:21  ncq
# - some comments and cleanup
#
# Revision 1.6  2003/05/22 16:28:37  hinnef
# - selecting an item now expands/collapses its subtrees
#
# Revision 1.5  2003/05/16 10:51:45  hinnef
# - now subtrees can hold config file data
#
# Revision 1.4  2003/05/11 17:00:26  hinnef
# - removed obsolete code lines
#
# Revision 1.3  2003/05/11 16:56:48  hinnef
# - now shows values of config parameters, too
#
# Revision 1.2  2003/05/10 18:44:02  hinnef
# added revision log keyword
#
