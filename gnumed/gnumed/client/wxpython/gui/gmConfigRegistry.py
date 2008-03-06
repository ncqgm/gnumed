"""GnuMed configuration editor.

Works quite similar to the Windows Registry editor (but is
a clean-room implementation).

@license: GPL"""
#================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gui/gmConfigRegistry.py,v $
__version__ = "$Revision: 1.43 $"
__author__ = "H.Berger, S.Hilbert, K.Hilbert"

import sys, os, string, types

_log = gmLog.gmDefLog
if __name__ == '__main__':
	_log.SetAllLogLevels(gmLog.lData)

from Gnumed.pycommon import gmCfg, gmConfigCommon, gmI18N
from Gnumed.wxpython import gmPlugin, gmGuiHelpers, gmRegetMixin
from Gnumed.business import gmPerson, gmSurgery

import wx

_cfg = gmCfg.gmDefCfgFile

_log.Log(gmLog.lInfo, __version__)

[	ConfigTreeCtrlID,
	ConfigTreeBoxID,
	ParamBoxID,
	ConfigEntryParamCtrlID,
	ButtonParamApplyID,
	ButtonParamRevertID,
	DescriptionBoxID,
	ConfigDescriptionTextID
] = map(lambda _init_ctrls: wx.NewId(), range(8))

#================================================================
class cConfTree(wx.TreeCtrl):
	"""This wx.TreeCtrl derivative displays a tree view of configuration 
	parameter names.
	"""
	def __init__(self, parent, id, size=wx.DefaultSize,pos=wx.DefaultPosition,
				style=None,configSources = None,rootLabel = "",paramWidgets=None):
		"""Set up our specialised tree."""

		self.paramTextCtrl = paramWidgets[0]
		self.paramDescription = paramWidgets[1]
		self.mConfSources = configSources
		for src in configSources:
			_log.Log(gmLog.lData, 'config source: [%s]' % str(src))
		self.rootLabel = rootLabel

		wx.TreeCtrl.__init__(self, parent, id, pos, size, style)

		self.root = None
		self.param_list = None
		# currently selected parameter/subtree
		self.currSelParam = None
		self.currSelSubtree = None

		# connect handler
		wx.EVT_TREE_ITEM_ACTIVATED (self, self.GetId(), self.OnActivate)
		wx.EVT_RIGHT_DOWN(self,self.OnRightDown)

	#------------------------------------------------------------------------
	def update(self):

		if self.param_list is not None:
			del self.param_list

		if self.__populate_tree() is None:
			return None

		return True
	#------------------------------------------------------------------------
	def __populate_tree(self):
		# FIXME: TODO ALL !
		
		# clean old tree
		if not self.root is None:
			self.DeleteAllItems()
            
		# init new tree
		self.root = self.AddRoot(self.rootLabel, -1, -1)
		self.SetPyData(self.root, {'type': 'root', 'name': self.rootLabel})
		self.SetItemHasChildren(self.root, False)

		# now get subtrees for four maingroups (see __init__)

		for nodeDescription in (self.mConfSources.keys()):

			_log.Log(gmLog.lData, 'adding first level node: [%s]' % nodeDescription)
			node = self.AppendItem(self.root, nodeDescription)
			self.SetPyData(node, {'type': 'defaultSubtree', 'name': nodeDescription})

			# add subtree if any
			subTree = self.__getSubTree(nodeDescription)
			if subTree is None:
				self.SetItemHasChildren(node, False)
				_log.Log(gmLog.lData, 'node has no children')
				continue
			self.__addSubTree(node, subTree)

			self.SortChildren(node)
			self.SetItemHasChildren(node, True)
						
		self.SetItemHasChildren(self.root, True)
		self.SortChildren(self.root)
		# and uncollapse
		self.Expand(self.root)

		return True
	#------------------------------------------------------------------------
	# this must be reentrant as we will iterate over the tree branches
	def __addSubTree(self,aNode=None, aSubTree=None):
		"""
		Adds a subtree of parameter names to an existing tree. 
		Returns resulting tree.
		"""
		_log.Log(gmLog.lData, 'adding sub tree: [%s]' % str(aSubTree))

		# check if subtree is empty
		if aSubTree[1] == {}:
			return None

		# check if subtree has children
		childrenList = aSubTree[1].keys()
		if childrenList is None:
			return None
		self.SetItemHasChildren(aNode, True)

		# add every child as new node, add child-subtrees as subtree
		# reiterating this method
		for subTreeNode in childrenList:
			nodeEntry = aSubTree[1][subTreeNode]
			nodeName = nodeEntry[2]						
			node = self.AppendItem(aNode, nodeName)
			self.SetPyData(node, nodeEntry[0])
			self.SetItemHasChildren(node, False)
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
		# if the subtree config data source is null, return empty subtree
		if self.mConfSources[nodeDescription] is None:
			return None
			
		# get all parameter names
		tmpParamList = self.mConfSources[nodeDescription].getAllParamNames()
		if tmpParamList is None:
			return None

		# convert name list to a tree structure
		currSubTree = [None,{},""]
		# add each item 
		# attach parameter name (= reference for ConfigData) and subtree as object
		for paramName in tmpParamList:
			self.__addTreeItem (
				currSubTree,
				paramName,
				{'type': 'parameter', 'ref': paramName, 'subtree': nodeDescription}
			)

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
		"""save parameter dialog"""
		# self.currSelParam is the name of the parameter with optional
		# cookie part appended, defParamName the name without cookie part !
		# you must use the latter to access config definitions !

		if not (self.currSelParam is None or self.currSelSubtree is None):

			# get new value
			val = self.paramTextCtrl.GetValue()
			
			currConfSource = self.mConfSources[self.currSelSubtree]
			newValue = currConfSource.castType(self.currSelParam,val)

			if newValue is None:
				gmGuiHelpers.gm_show_error (
					_('Type of entered value is not compatible with type expected.'),
					_('saving configuration')
				)

			# a particular config definition refers to a parameter name
			# without the cookie part. we have to strip the 
			# cookie off get the correct parameter
			defParamName = currConfSource.getRawName(self.currSelParam)

			# config definition object
			confDefinition = currConfSource.hasDefinition()

			# if there is no config definition, ask the user if the
			# new value should be stored unchecked

			if not confDefinition or not currConfSource.hasParameterDefinition(defParamName):
				if gmGuiHelpers.gm_show_question (
					_("There is no config definition for this parameter.\nThus it can't be checked for validity.\n\nSave anyway ?"),
					_('saving configuration')):
					currConfSource.setConfigData( self.currSelParam,newValue)
				
					# reshow new data to mark it non modified
					self.__show_parameter(self.currSelSubtree,self.currSelParam)
				return 

			# else check parameter for validity

			if currConfSource.isValid(defParamName,newValue):
				currConfSource.setConfigData(self.currSelParam,newValue)
				
				# reshow new data to mark it non modified
				self.__show_parameter(self.currSelSubtree,self.currSelParam)
			else:
				# TODO: display some hint on what could be wrong
				gmGuiHelpers.gm_show_error (
					_('Entered value is not valid.'),
					_('saving configuration')
				)

	#------------------------------------------------------------------------
	def OnActivate (self, event):
		item = event.GetItem()
		data = self.GetPyData(item)

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
			message=_("<Options for current/default user and workplace>")
		# show message
		self.paramTextCtrl.ShowMessage(message)
		# expand/unexpand node if it has children
		if self.ItemHasChildren(item):
			if self.IsExpanded(item):
				self.Collapse(item)
			else:
				self.Expand(item)
		return True

	#--------------------------------------------------------
	def OnRightDown(self,event):
		position = event.GetPosition()
		(item,flags) = self.HitTest(position)
#		if flags & (wx.TREE_HITTEST_ONITEMLABEL) == True:
		self.SelectItem(item)
	#------------------------------------------------------------------------
	def __show_parameter(self,aSubtree=None, aParam=None):
			# get the parameter value
			value = self.mConfSources[aSubtree].getConfigData(aParam)
			currType = self.mConfSources[aSubtree].getParamType(aParam)
			# get description
			description = self.mConfSources[aSubtree].getDescription(aParam)
#			print "showing parameter:"
#			print "param:", aParam
#			print "val  :", value
#			print "type :", currType
#			print "desc :", description
			self.paramTextCtrl.ShowParam(aParam,currType,value)
			self.paramTextCtrl.SetEditable(1)
			self.paramDescription.SetValue(description)
###############################################################################
class cParamCtrl(wx.TextCtrl):
	def __init__(self, parent, id,value,pos,size,style,type ):
		wx.TextCtrl.__init__(self, parent, -1, value="",style=style)		
		self.parent = parent

	def ShowParam(self,aParam=None,aType=None,aValue=None):
		self.Clear()
		if aParam is None:
			return
		# store current parameter for later use
		self.currParam = aParam
		self.value = aValue
		self.type = aType
		
		if self.type == 'string':
			self.SetValue(self.value)
		elif self.type == 'str_array':
		# we can't use AppendText here because that would mark the value
		# as modified 
			first = 1
			all = ''
			for line in (self.value):
				if first:
					first = 0
				else:
					all = all + '\n'
				all = all + line
			self.SetValue(all)			
		elif self.type == 'numeric':
			self.SetValue(str(self.value))
			
	def ShowMessage(self,aMessage=""):
		self.currParam = None
		self.Clear()
		self.SetValue(aMessage)


	def RevertToSaved(self):
		if not self.currParam is None:
			self.ShowParam(self.currParam, self.type, self.value)

###############################################################################
# TODO: -a MenuBar allowing for import, export and options
# 		-open a connection to backend via gmCfg
class gmConfigEditorPanel(wx.Panel):
	def __init__(self, parent, aUser,aWorkplace, plugin = 1):
		"""aUser and aWorkplace can be set such that an admin
		   could potentially edit another user ...
		"""
		wx.Panel.__init__(self, parent, -1)
		
		self.currUser = aUser
		self.currWorkplace = aWorkplace
		# init data structures
		# initialize the objects holding data on the subtrees
		# add default subtrees root nodes if possible
		#   default entries in root:
		# 	 -default config file (usually ~/.gnumed/gnumed.conf)
		#	 -current user, current workplace
		#	 -current user, default workplace
		#	 -default user, current workplace
		#	 -default user, default workplace
		self.mConfSources = {}

		# if we pass no config file name, we get the default cfg file
		cfgFileDefault = gmConfigCommon.ConfigSourceFile("gnumed.conf")
		cfgFileName = cfgFileDefault.GetFullPath()
		# if the file was not found, we display some error message
		if cfgFileName is None:
			cfgFileName = "gnumed.conf not found"
		# now get the absolute path of the default cfg file
		self.mConfSources['FILE:%s' % cfgFileName] = cfgFileDefault
		try:
			if not (self.currUser is None or self.currWorkplace is None):
				self.mConfSources['DB:CURRENT_USER_CURRENT_WORKPLACE'] = gmConfigCommon.ConfigSourceDB('DB:CURRENT_USER_CURRENT_WORKPLACE',aWorkplace=self.currWorkplace)
		except: pass
		try:
			if not (self.currUser is None) :
				self.mConfSources['DB:CURRENT_USER_DEFAULT_WORKPLACE'] = gmConfigCommon.ConfigSourceDB('DB:CURRENT_USER_DEFAULT_WORKPLACE')
		except: pass
		try:
			if not (self.currWorkplace is None):
				self.mConfSources['DB:DEFAULT_USER_CURRENT_WORKPLACE'] = gmConfigCommon.ConfigSourceDB('DB:DEFAULT_USER_CURRENT_WORKPLACE',aUser='xxxDEFAULTxxx',aWorkplace=self.currWorkplace)
		except: pass
		try:
			# this should always work
			self.mConfSources['DB:DEFAULT_USER_DEFAULT_WORKPLACE'] = gmConfigCommon.ConfigSourceDB('DB:DEFAULT_USER_DEFAULT_WORKPLACE',aUser='xxxDEFAULTxxx')
		except:
			pass
# main sizers
		self.mainSizer = wx.BoxSizer(wx.HORIZONTAL)
		self.rightSizer = wx.BoxSizer(wx.VERTICAL)

# selected parameter
		self.configEntryParamBox = wx.StaticBox( self, ParamBoxID, _("Parameters") )
		self.configEntryParamBoxSizer = wx.StaticBoxSizer( self.configEntryParamBox, wx.HORIZONTAL )

		self.configEntryParamCtrl = cParamCtrl( parent = self, 
						id = ConfigEntryParamCtrlID, 
						pos = wx.DefaultPosition, 
						size = wx.Size(250,200),
						value = "" , 
						style = wx.LB_SINGLE,
						type = None)
		
		self.paramButtonSizer = wx.BoxSizer(wx.HORIZONTAL)
		self.paramCtrlSizer = wx.BoxSizer(wx.VERTICAL)
		self.buttonApply = wx.Button(parent=self,
					id = ButtonParamApplyID,
					label = "Apply changes" )
		self.buttonRevert = wx.Button(parent=self,
					id = ButtonParamRevertID,
					label = "Revert to saved" )
		
		wx.EVT_BUTTON(self,ButtonParamApplyID,self.ApplyChanges)
		wx.EVT_BUTTON(self,ButtonParamRevertID,self.RevertChanges)


# parameter description
		self.configEntryDescriptionBox = wx.StaticBox( self, DescriptionBoxID, _("Parameter Description") )
		self.configEntryDescriptionBoxSizer = wx.StaticBoxSizer( self.configEntryDescriptionBox, wx.HORIZONTAL )

		self.configEntryDescription = wx.TextCtrl(parent = self, 
							id = ConfigDescriptionTextID,
							pos = wx.DefaultPosition, 
							size = wx.Size(250,100),
							style = wx.TE_READONLY | wx.LB_SINGLE,
							value ="" )
		self.configEntryDescriptionBoxSizer.Add( self.configEntryDescription, 1, wx.ALIGN_CENTRE|wx.ALL|wx.EXPAND, 2 )
# static box for config tree
		self.configTreeBox = wx.StaticBox( self, ConfigTreeBoxID, _("Config Options") )
		self.configTreeBoxSizer = wx.StaticBoxSizer( self.configTreeBox, wx.HORIZONTAL )
		
# config tree        
		rootLabel = "%s@%s" % (self.currUser,self.currWorkplace)
		self.configTree = cConfTree( parent = self,
						id = ConfigTreeCtrlID ,
						pos = wx.Point(0, 0), 
						size = wx.Size(200, 300),
						style = wx.TR_HAS_BUTTONS|wx.TAB_TRAVERSAL,
						configSources = self.mConfSources,
						rootLabel = rootLabel,
						paramWidgets=(self.configEntryParamCtrl,self.configEntryDescription)
						)
		self.configTree.SetFocus()
		self.configTreeBoxSizer.Add( self.configTree, 1, wx.ALIGN_CENTRE|wx.ALL|wx.EXPAND, 5 )

		self.paramCtrlSizer.Add(self.configEntryParamCtrl,1,wx.ALIGN_CENTRE|wx.ALL|wx.EXPAND, 2 )
		self.paramButtonSizer.Add(self.buttonApply,1,wx.ALIGN_LEFT|wx.ALL|wx.EXPAND, 2 )
		self.paramButtonSizer.Add(self.buttonRevert,1,wx.ALIGN_RIGHT|wx.ALL|wx.EXPAND, 2 )
		self.paramCtrlSizer.Add(self.paramButtonSizer,0,wx.ALIGN_BOTTOM, 2 )
		self.configEntryParamBoxSizer.Add(self.paramCtrlSizer , 1, wx.ALIGN_CENTRE|wx.ALL|wx.EXPAND, 2 )

# add right panels to right sizer
		self.rightSizer.Add(self.configEntryParamBoxSizer, 1, wx.EXPAND, 0)
		self.rightSizer.Add(self.configEntryDescriptionBoxSizer, 1, wx.EXPAND, 0)

# add widgets to main sizer		
		self.mainSizer.Add(self.configTreeBoxSizer, 1, wx.EXPAND, 0)
		self.mainSizer.Add(self.rightSizer, 1, wx.EXPAND, 0)
		self.SetAutoLayout(1)
		self.SetSizer(self.mainSizer)
		self.mainSizer.Fit(self)
		self.mainSizer.SetSizeHints(self)
		self.Layout()

	def ApplyChanges(self,event):
		if self.configEntryParamCtrl.IsModified():
			self.configTree.SaveCurrParam()

	def RevertChanges(self,event):
		self.configEntryParamCtrl.RevertToSaved()

	def repopulate_ui(self):
		self.configTree.update()
		
#================================================================
# MAIN
#----------------------------------------------------------------
if __name__ == '__main__':
	from Gnumed.wx.python import gmPlugin
	_log.Log (gmLog.lInfo, "starting config browser")
	
	workplace = raw_input("Please enter a workplace name: ")
	# catch all remaining exceptions
	try:
		application = wx.PyWidgetTester(size=(640,480))
		application.SetWidget(gmConfigEditorPanel,"any-doc",workplace, 0)
		application.MainLoop()
	except:
		_log.LogException("unhandled exception caught !", sys.exc_info(), verbose=0)
		# but re-raise them
		raise

	_log.Log (gmLog.lInfo, "closing config browser")

else:
	class gmConfigRegistry(gmPlugin.cNotebookPlugin):
		"""Class to load this module from an environment that wants a notebook plugin
		"""
		def name (self):
			return _("Setup")

		def GetWidget (self, parent):
			# get current workplace name
			workplace = gmSurgery.gmCurrentPractice().active_workplace
			currUser = gmPerson.gmCurrentProvider()['db_user']
			_log.Log (gmLog.lInfo, "ConfigReg: %s@%s" % (currUser,workplace))
			self._widget = gmConfigEditorPanel(parent,currUser,workplace)
			return self._widget

		def MenuInfo (self):
			return ('tools', _('&ConfigRegistry'))

	def Setup(parent):
		"""Wrapper to load this module from an environment that wants a panel
		"""
		currUser = gmPerson.gmCurrentProvider()['db_user']
		workplace = gmSurgery.gmCurrentPractice().active_workplace
		return gmConfigEditorPanel(parent,currUser,workplace)

#------------------------------------------------------------                   
# $Log: gmConfigRegistry.py,v $
# Revision 1.43  2008-03-06 18:32:30  ncq
# - standard lib logging only
#
# Revision 1.42  2007/10/07 12:33:27  ncq
# - workplace property now on gmSurgery.gmCurrentPractice() borg
#
# Revision 1.41  2007/02/17 14:13:11  ncq
# - gmPerson.gmCurrentProvider().workplace now property
#
# Revision 1.40  2006/12/13 14:58:03  ncq
# - a bit of cleanup
#
# Revision 1.39  2006/12/05 14:02:09  ncq
# - fix wx import
# - add some logging
#
# Revision 1.38  2006/06/28 10:19:28  ncq
# - remove reget mixin
# - fix for receive_focus reload
#
# Revision 1.37  2006/05/20 18:56:03  ncq
# - use receive_focus() interface
#
# Revision 1.36  2006/05/14 21:44:22  ncq
# - add get_workplace() to gmPerson.gmCurrentProvider and make use thereof
# - remove use of gmWhoAmI.py
#
# Revision 1.35  2006/05/12 14:00:15  ncq
# - need to import gmPerson
#
# Revision 1.34  2006/05/12 12:19:09  ncq
# - whoami -> whereami
#
# Revision 1.33  2005/10/12 15:42:17  ncq
# - cleanup
#
# Revision 1.32  2005/10/02 11:38:03  sjtan
# import wx fixup. import wx.html
#
# Revision 1.31  2005/09/28 21:27:30  ncq
# - a lot of wx.2.6-ification
#
# Revision 1.30  2005/09/26 18:01:52  ncq
# - use proper way to import wx.26 vs wx.2.4
# - note: THIS WILL BREAK RUNNING THE CLIENT IN SOME PLACES
# - time for fixup
#
# Revision 1.29  2005/03/29 07:33:06  ncq
# - add comment
#
# Revision 1.28  2005/03/17 20:29:47  hinnef
# added Setup method for Richard-Space
#
# Revision 1.27  2005/03/06 14:54:19  ncq
# - szr.AddWindow() -> Add() such that wx.2.5 works
# - 'demographic record' -> get_identity()
#
# Revision 1.26  2004/09/25 13:11:40  ncq
# - improve tree root node naming
#
# Revision 1.25  2004/08/04 17:16:02  ncq
# - wx.NotebookPlugin -> cNotebookPlugin
# - derive cNotebookPluginOld from cNotebookPlugin
# - make cNotebookPluginOld warn on use and implement old
#   explicit "main.notebook.raised_plugin"/ReceiveFocus behaviour
# - ReceiveFocus() -> receive_focus()
#
# Revision 1.24  2004/08/02 17:48:53  hinnef
# converted to use gmRegetMixin
#
# Revision 1.23  2004/07/24 10:27:22  ncq
# - TRUE/FALSE -> True/False so Python doesn't barf
#
# Revision 1.22  2004/07/19 11:50:43  ncq
# - cfg: what used to be called "machine" really is "workplace", so fix
#
# Revision 1.21  2004/07/15 07:57:20  ihaywood
# This adds function-key bindings to select notebook tabs
# (Okay, it's a bit more than that, I've changed the interaction
# between gmGuiMain and gmPlugin to be event-based.)
#
# Oh, and SOAPTextCtrl allows Ctrl-Enter
#
# Revision 1.20  2004/07/06 20:55:38  hinnef
# fixed bug introduced during testing :(
#
# Revision 1.19  2004/06/28 22:34:09  hinnef
# fixed missing tree population in standalone use
#
# Revision 1.18  2004/06/13 22:31:48  ncq
# - gb['main.toolbar'] -> gb['main.top_panel']
# - self.internal_name() -> self.__class__.__name__
# - remove set_widget_reference()
# - cleanup
# - fix lazy load in _on_patient_selected()
# - fix lazy load in ReceiveFocus()
# - use self._widget in self.GetWidget()
# - override populate_with_data()
# - use gb['main.notebook.raised_plugin']
#
# Revision 1.17  2004/03/12 22:30:12  ncq
# - Hilmar, thanks :-)
# - also some cleanup (hehe, you guessed it)
#
# Revision 1.16  2004/03/12 18:33:02  hinnef
#  - fixed module import
#
# Revision 1.15  2004/03/09 08:59:35  ncq
# - cleanup imports
#
# Revision 1.14  2004/03/09 07:34:51  ihaywood
# reactivating plugins
#
# Revision 1.13  2004/02/25 09:46:22  ncq
# - import from pycommon now, not python-common
#
# Revision 1.12  2004/01/06 23:44:40  ncq
# - __default__ -> xxxDEFAULTxxx
#
# Revision 1.11  2003/12/29 16:59:42  uid66147
# - whoami adjustment
#
# Revision 1.10  2003/11/17 10:56:39  sjtan
#
# synced and commiting.
#
# Revision 1.1  2003/10/23 06:02:40  sjtan
#
# manual edit areas modelled after r.terry's specs.
#
# Revision 1.9  2003/10/13 21:04:00  hinnef
# - added GPL statement
#
# Revision 1.8  2003/10/13 21:01:46  hinnef
# -fixed a bug that would introduce newlines in str_array type values
#
# Revision 1.7  2003/09/03 17:33:22  hinnef
# make use of gmWhoAmI, try to get config info from backend
#
# Revision 1.6  2003/08/24 08:58:18  ncq
# - use gm_show_*
#
# Revision 1.5  2003/08/23 18:40:43  hinnef
# split up in gmConfigRegistry.py and gmConfigCommon.py, debugging, more comments
#
# Revision 1.4  2003/06/26 21:41:51  ncq
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
