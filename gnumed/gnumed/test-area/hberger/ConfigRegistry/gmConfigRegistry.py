#!/usr/bin/env python

__version__ = ""
__author__ = "H.Berger, S.Hilbert, K.Hilbert"

import sys, os, string
# location of our modules
if __name__ == "__main__":
	#sys.path.append(os.path.join('..', '..', 'python-common'))
	#sys.path.append(os.path.join('..', '..', 'business'))
	sys.path.append(os.path.join('.','modules'))

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

[
ConfigTreeCtrlID,
ConfigEntryParamCtrlID ,
ConfigDescriptionTextID
] = map(lambda _init_ctrls: wxNewId(), range(3))

# local vars
#configTreeItem = {}

#================================================================
class cConfTree(wxTreeCtrl):
	"""This wxTreeCtrl derivative displays a tree view of configuration 
	parameter names.
	"""
	def __init__(self, parent, id, aConn = None,size=wxDefaultSize,pos=wxDefaultPosition,
				style=None,aUser=None,aMachine=None,paramWidgets=None):
		"""Set up our specialised tree.
		   default entries in root:
			 -current user, current machine
			 -current user, default machine
			 -default user, current machine
			 -default user, default machine

			expects a open connection to service config
		"""

		self.currUser = aUser
		self.currMachine = aMachine
		self.paramTextCtrl = paramWidgets[0]
		self.paramDescription = paramWidgets[1]

		# initialize the objects holding data on the subtrees
		# add default subtrees root nodes if possible
		self.mConfData = {}
		if not (self.currUser is None or self.currMachine is None) :
			self.mConfData['CURRENT_USER_CURRENT_MACHINE'] = ConfigData(aMachine=self.currMachine)
		if not (self.currUser is None) :
			self.mConfData['CURRENT_USER_DEFAULT_MACHINE'] = ConfigData()
		if not (self.currMachine is None) :
			self.mConfData['DEFAULT_USER_CURRENT_MACHINE'] = ConfigData(aUser='__default__',aMachine=self.currMachine)
		# this should always work
		self.mConfData['DEFAULT_USER_DEFAULT_MACHINE'] = ConfigData(aUser='__default__')

		wxTreeCtrl.__init__(self, parent, id, pos, size, style=wxTR_NO_BUTTONS)

		self.root = None
		self.param_list = None

		# connect handler
		EVT_TREE_ITEM_ACTIVATED (self, self.GetId(), self.OnActivate)
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
		rootname = "%s@%s" % (self.currUser,self.currMachine)
		self.root = self.AddRoot(rootname, -1, -1)
		self.SetPyData(self.root, {'type': 'root', 'name': rootname})
		self.SetItemHasChildren(self.root, FALSE)

		# now get subtrees for four maingroups (see __init__)

		for nodeDescription in (self.mConfData.keys()) :

			# get subtree
			subTree = self.__getSubTree(nodeDescription)
			node = self.AppendItem(self.root, nodeDescription)
			# mabe we should store some data (version ?)
			self.SetPyData(node, {'type': 'defaultSubtree', 'name': nodeDescription})
			self.SetItemHasChildren(node, TRUE)
			# we might as well not display whole subtrees, but than we can't
			# add anything, neither
			if subTree is None:
				continue
			else:
				self.__addSubTree(node,subTree)
				self.SortChildren(node)
				self.Expand(node)
						
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

		# add every child as new node, add child-subtrees as subtree
		# reiterating this method
		for subTreeNode in childrenList:
			nodeEntry = aSubTree[1][subTreeNode]
			nodeName = nodeEntry[2]						
#DEBUG
#			_log.Log(gmLog.lInfo, "Node: %s Name: %s" % (str(aNode),nodeName) )
			node = self.AppendItem(aNode, nodeName)
			self.SetPyData(node, nodeEntry[0])
			self.SetItemHasChildren(aNode, TRUE)
			# now add subTrees
			if not nodeEntry[1] == {}:
				self.__addSubTree(node,nodeEntry)
				self.SortChildren(node)
				self.Expand(node)
				
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

	def OnActivate (self, event):
		item = event.GetItem()
		data = self.GetPyData(item)
		_log.Log(gmLog.lInfo, "ItemData %s" % str(data))

		self.paramDescription.Clear()

		type = data['type']
		if type == 'parameter':
			ref = data['ref']
			subtree = data ['subtree']
			confData = self.mConfData[subtree].GetConfigData(ref)
			description = confData[1][4]
			_log.Log(gmLog.lInfo, "VALUE %s" % str(confData))
			self.paramTextCtrl.ShowParam(confData)
			self.paramDescription.SetValue(description)
		elif type == 'branch':
			self.paramTextCtrl.ShowMessage(_("(Branch)"))
		elif type == 'defaultSubtree':
			self.paramTextCtrl.ShowMessage(_("(Subtree root)"))
		elif type == 'root':
			self.paramTextCtrl.ShowMessage(_("(Config parameter tree for current/default user and machine)"))

		return 1

		#--------------------------------------------------------
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


###############################################################################
class ParameterDefinition:
	"""
	describes a gnumed configuration parameter.
	"""
	def __init__(self,aParamName = None,aParamType = None,aValidValsList = None,aParamDescription = None):
		self.mName = aParamName
		self.mType = aParamType
		self.mDescription = aParamDescription
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
			raise TypeError, "No configuration definition source specified"
		else:
			self.__mDefinitionSource = aDefinitionSource
			if not self.__getDefinitions():
				raise IOError, "cannot load definitions"
		
		self.__mParmeterDefinitions = {}


	def __getDefinitions(self):
		"""get config definitions"""

		# open configuration source
		try:
			cfgSource = gmCfg.cCfgFile(aFile = self.__mDefinitionSource)
			# handle all exceptions including 'config file not found'
		except:
			exc = sys.exc_info()
			_log.LogException("Unhandled exception while opening config file [%s]" % self.__mDefinitionSource, exc, fatal=1)
			return None

		cfgData = cfgSource.getCfg()
		groups = cfgSource.getGroups()

		if not groups.has_key('_config_version_'):
			_log.Log(gmLog.lWarn, "No configuration definition version defined.")
			_log.Log(gmLog.lWarn, "Matching definitions to config data is unsafe.")
			_log.Log(gmLog.lWarn, "Config data will be read-only by default.")
			self.__parameterDict['_version_'] = None
		else:
			version = cfgSource.get(groups['_config_version_'], "version")
			# we don't check for type in order to allow for versions like '1.20.1b'			 
			del groups[_config_version_]
			self.__parameterDict['_version_'] = version
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
	""" holds config data for a particular user/machine pair 
    read from backend.
	this will contain: 
		a) config parameter names
		b) config parameter values
		c) config information version (must match the version used in ConfigDefinition)
	"""
	# static class variables that hold links to backend and gmCfg
	# this will be shared by all ConfigData objects
	_backend = None
	_dbcfg = None

	def __init__(self, aUser = None, aMachine = '__default__'):
		# get connection
		if ConfigData._backend is None:
			ConfigData._backend = gmPG.ConnectionPool()

		# connect to config database
		if ConfigData._dbcfg is None:
			ConfigData._dbcfg = gmCfg.cCfgSQL(
				aConn = self._backend.GetConnection('default'),
				aDBAPI = gmPG.dbapi
			)

		if ConfigData._dbcfg is None:
			_log.Log(gmLog.lErr, "Cannot access configuration without database connection !")
			raise ConstructorError, "ConfigData.__init__(): need db conn"

		self.mUser = aUser
		self.mMachine = aMachine
		self.mConfigData = {}

	def GetConfigData(self, aParameterName = None):
		"""
		Gets Config Data for a particular parameter. 
		Returns a tuple consisting of the value and a list of metadata 
		(name,cookie, owner, type and description)
		"""
		name=self.mConfigData[aParameterName][0]
		cookie = self.mConfigData[aParameterName][1]
		try:
			result=ConfigData._dbcfg.get(self.mMachine, self.mUser,cookie,name)
		except:
			_log.Log(gmLog.lErr, "Cannot get parameter value for [%s]" % aParameterName )
		
		return (result,self.mConfigData[aParameterName])
		
	def getAllNames(self):
		"""
		fetch names and parameter data from backend. Returns list of
		parameter names where cookie and real name are concatenated.
		"""
		try:
			result=ConfigData._dbcfg.getAllParams(self.mUser,self.mMachine)
		except:
			_log.Log(gmLog.lErr, "Cannot get config parameter names.")
			raise
		if result == []:
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
			for param in (result):
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

###############################################################################
class cParamCtrl(wxTextCtrl):
	def __init__(self, parent, id,value,pos,size,style,type ):
		wxTextCtrl.__init__(self, parent, -1, value="",style=style)		

	def ShowParam(self,aParam=None):
		self.Clear()
		if aParam is None:
			return
		metadata = aParam[1]
		value = aParam[0]
		type = metadata[3]
		description = metadata[4]
		
		if type == 'string':
			self.SetValue(value)
		elif type == 'str_array':
			for line in (value):
				self.AppendText(line + '\n')
		elif type == 'numeric':
			self.SetValue(str(value))
			
	def ShowMessage(self,aMessage=""):
		self.Clear()
		self.SetValue(aMessage)


###############################################################################
# TODO: -a MenuBar allowing for import, export and options
# 		-open a connection to backend via gmCfg
class gmConfigEditorPanel(wxPanel):
	def __init__(self, parent, aUser,aMachine):
		wxPanel.__init__(self, parent, -1)

# main sizers
		self.mainSizer = wxBoxSizer(wxHORIZONTAL)
		self.rightSizer = wxBoxSizer(wxVERTICAL)

# selected parameter
		self.configEntryParamBox = wxStaticBox( self, -1, _("Parameters") )
		self.configEntryParamBoxSizer = wxStaticBoxSizer( self.configEntryParamBox, wxHORIZONTAL )

		self.configEntryParamCtrl = cParamCtrl( parent = self, 
											id = ConfigEntryParamCtrlID, 
											pos = wxDefaultPosition, 
											size = wxSize(250,100),
											value = "" , 
											style = wxLB_SINGLE,
											type = None)
		self.configEntryParamBoxSizer.AddWindow( self.configEntryParamCtrl, 1, wxALIGN_CENTRE|wxALL|wxEXPAND, 2 )

# parameter description
		self.configEntryDescriptionBox = wxStaticBox( self, -1, _("Parameter Description") )
		self.configEntryDescriptionBoxSizer = wxStaticBoxSizer( self.configEntryDescriptionBox, wxHORIZONTAL )

		self.configEntryDescription = wxTextCtrl(parent = self, 
												id = ConfigDescriptionTextID,
												pos = wxDefaultPosition, 
												size = wxSize(250,100),
												style = wxTE_READONLY | wxLB_SINGLE,
												value ="" )
		self.configEntryDescriptionBoxSizer.AddWindow( self.configEntryDescription, 1, wxALIGN_CENTRE|wxALL|wxEXPAND, 2 )

# static box for config tree
		self.configTreeBox = wxStaticBox( self, -1, _("Config Options") )
		self.configTreeBoxSizer = wxStaticBoxSizer( self.configTreeBox, wxHORIZONTAL )
# config tree        
		self.configTree = cConfTree( 	parent = self,
										id = ConfigTreeCtrlID ,
										pos = wxPoint(0, 0), 
										size = wxSize(200, 300),
										style = wxTR_HAS_BUTTONS,
										aUser = aUser,
										aMachine = aMachine,
										paramWidgets=(self.configEntryParamCtrl,self.configEntryDescription)
										)
#		configTreeItem['root']=self.configTree.AddRoot(localMachineName)
		self.configTreeBoxSizer.AddWindow( self.configTree, 1, wxALIGN_CENTRE|wxALL|wxEXPAND, 5 )


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
###############################################################################


	def __populateTree():
		# here we should 
		# 1.) get the config parameter either from ConfigDefinition or ConfigData
		# 2.) parse the config items and create a hierarchical list from it's names
		# 3.) add each config entry to the treeCtrl
		pass
###############################################################################

#================================================================
# MAIN
#----------------------------------------------------------------
if __name__ == '__main__':
	import gmPG
	import gmPlugin, gmGuiBroker
	_log.Log (gmLog.lInfo, "starting display handler")

	if _cfg == None:
		_log.Log(gmLog.lErr, "Cannot run without config file.")
		sys.exit("Cannot run without config file.")
	
	workplace = raw_input("Please enter a workplace name: ")
	# catch all remaining exceptions
	try:
		application = wxPyWidgetTester(size=(640,480))
		application.SetWidget(gmConfigEditorPanel,"test-doc",workplace)
		application.MainLoop()
	except:
		_log.LogException("unhandled exception caught !", sys.exc_info(), fatal=1)
		# but re-raise them
		raise

	_log.Log (gmLog.lInfo, "closing display handler")

else:
	import gmPlugin, gmGuiBroker,gmPG


	class gmConfigRegistry(gmPlugin.wxNotebookPlugin):
		def name (self):
			return _("ConfigRegistry")

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
# Revision 1.3  2003-05-11 16:56:48  hinnef
# - now shows values of config parameters, too
#
# Revision 1.2  2003/05/10 18:44:02  hinnef
# added revision log keyword
#
