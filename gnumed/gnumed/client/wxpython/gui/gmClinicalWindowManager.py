"""Patient window manager class for the main notebook.

Allows plugins to register, and swap in an out of view.

A plugin may elect to be in three modes:

wholescreen
 - the plugin seizes the whole panel
 - should this exist ? IMHO no (kh)

lefthalf
 - the plugin gets the left column onscreen
 - the right column becomes visible.

right column
 - the plugin is added to a vertical sizer on the right-hand
   column (note all of these plugins are visible at once)
"""
#==================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gui/Attic/gmClinicalWindowManager.py,v $
# $Id: gmClinicalWindowManager.py,v 1.1 2003-04-04 23:15:46 ncq Exp $
# license: GPL
__version__ = "$Revision: 1.1 $"
__author__ =	"I.Haywood"

from wxPython.wx import *

import gmLog
_log = gmLog.gmDefLog
_log.Log(gmLog.lData, __version__)

import gmGuiBroker, gmDispatcher, gmShadow, gmPlugin
#==================================================
class gmClinicalPanel (wxPanel):

	def __init__ (self, parent):
		wxPanel.__init__ (self, parent, -1)
		EVT_SIZE (self, self.OnSize)
		self.__gb = gmGuiBroker.GuiBroker ()
		self.wholescreen = {}
		self.lefthalf = {}
		self.visible = '' # plugin currectly visible in left or whole screen
		self.default = '' # set by one plugin!
		self.righthalf = {}
		self.sizer = wxBoxSizer (wxHORIZONTAL)
		self.SetSizer (self.sizer)
		if gmGuiBroker.config['main.shadow']:
			self.righthalfshadow = gmShadow.Shadow (self, -1)
			self.righthalfpanel = wxPanel (self.righthalfshadow, -1)
			self.righthalfshadow.SetContents (self.righthalfpanel)
		else:
			self.righthalfpanel = wxPanel (self, -1)
			self.righthalfshadow = self.righthalfpanel
	#----------------------------------------------
	def OnSize (self, event):
		w,h = self.GetClientSizeTuple ()
		self.sizer.SetDimension (0,0, w, h)
	#----------------------------------------------
	def SetDefault (self, d):
		self.default = d
	#----------------------------------------------
	def DisplayDefault (self):
		self.Display (self.default)
	#----------------------------------------------
	def RegisterWholeScreen (self, name, panel):
		"""Receives a wxPanel which is to fill the whole screen.

		Client must NOT do Show () on the panel!
		"""
		self.wholescreen[name] = panel
		panel.Show (0)
		_log.Log(gmLog.lData, "******* Registering %s as whole screen widget" % name)
	#----------------------------------------------
	def RegisterLeftSide (self, name, panel):
		"""Register for left side.
		"""
		panel.Show (0)
		self.lefthalf[name] = panel
		_log.Log(gmLog.lData, "******* Registering %s as left side widget" % name)
	#----------------------------------------------
	def RegisterRightSide (self, name, panel, position =1):
		"""Register for right column.

		Panel must be self.righthalfpanel
		Note there is no display function for these: they are
		automatically displayed when a left-column plugin is displayed
		"""
		self.righthalf[name] = (panel, position)
		panel.Show (0)
		_log.Log(gmLog.lData, "******* Registering %s as right side widget" % name)
	#----------------------------------------------
	# FIXME: Someone please document what is happening here !!!
	def Unregister (self, name):
		if name == self.default:
			_log.Log(gmLog.lErr, 'Cannot unregister [%s] - it is the default plugin.' % name)
		else:
			if self.visible == name:
				self.Display (self.default)
			_log.Log(gmLog.lInfo, 'Unregistering widget %s' % name)
			if self.righthalf.has_key (name):
				# self.visible is the name of the whole screen widget if any
				if self.lefthalf.has_key (self.visible):
					self.vbox.Remove (self.righthalf[name][0])
					self.vbox.Layout ()
				del self.righthalf[name]
			elif self.lefthalf.has_key (name):
				del self.lefthalf[name]
			elif self.wholescreen.has_key (name):
				del self.wholescreen[name]
			else:
				_log.Log(gmLog.lErr, 'tried to delete non-existant plugin [%s]' % name)
	#----------------------------------------------
	def Display (self, name):
		"""Displays the named widget.
		"""
		if self.wholescreen.has_key (name):
			self.DisplayWhole (name)
		elif self.lefthalf.has_key (name):
			self.DisplayLeft (name)
		else:
			_log.Log(gmLog.lErr, 'Widget %s not registered' % name)
	#----------------------------------------------
	def DisplayWhole (self, name):
		_log.Log(gmLog.lData, 'displaying whole screen widget %s' % name)
		if self.wholescreen.has_key (self.visible):
			# already in full-screen mode
			self.wholescreen[self.visible].Show (0)
			self.sizer.Remove (0)
			self.sizer.Add (self.wholescreen[name])
			self.wholescreen[name].Show (1)
			self.sizer.Layout ()
			self.visible = name
		else:
			if self.lefthalf.has_key (self.visible):
				# remove left half and right column
				self.sizer.Remove (0)
				self.lefthalf[self.visible].Show (0)
				self.righthalfshadow.Show (0)
				self.sizer.Remove (self.righthalfshadow)
			# now put whole screen in
			self.wholescreen[name].Show (1)
			self.sizer.Add (self.wholescreen[name], 1, wxEXPAND, 0)
			self.visible = name
			self.sizer.Layout ()
	#----------------------------------------------
	def DisplayLeft (self, name):
		_log.Log(gmLog.lData, 'displaying left screen widget %s' % name)
		if self.lefthalf.has_key (self.visible):
			self.sizer.Remove (self.lefthalf[self.visible])
			self.lefthalf[self.visible].Show (0)
			self.lefthalf[name].Show (1)
			self.sizer.Prepend (self.lefthalf[name], 2, wxEXPAND, 0)
			self.sizer.Layout ()
			self.visible = name
		else:
			if self.wholescreen.has_key (self.visible):
				self.sizer.Remove (self.wholescreen[self.visible])
				self.wholescreen[self.visible].Show (0)
			self.lefthalf[name].Show (1)
			self.sizer.Add (self.lefthalf[name], 2, wxEXPAND, 0)
			self.vbox = wxBoxSizer (wxVERTICAL)
			pos = 1
			done = 0
			while done < len (self.righthalf.values ()):
				for w, p in self.righthalf.values ():
					if p == pos:
						w.Show (1)
						self.vbox.Add (w, 1, wxEXPAND, 0)
						done += 1
				pos += 1
			self.righthalfpanel.SetSizer (self.vbox)
			self.righthalfpanel.SetAutoLayout (1)
			self.righthalfshadow.Show (1)
			self.sizer.Add (self.righthalfshadow, 1, wxEXPAND, 0) 
			self.sizer.Layout ()
			self.visible = name
	#----------------------------------------------
	def GetVisible (self):
		return self.visible
#==================================================
class gmClinicalWindowManager (gmPlugin.wxNotebookPlugin):

	def name (self):
		return _("Clinical")
	#----------------------------------------------
	def MenuInfo (self):
		return None # we add our own submenu
	#----------------------------------------------
	def GetWidget (self, parent):
		self.panel = gmClinicalPanel (parent)
		self.gb['clinical.manager'] = self.panel
		return self.panel
	#----------------------------------------------
	def register (self):
		gmPlugin.wxNotebookPlugin.register(self)
		# add own submenu, patient plugins add to this
		ourmenu = wxMenu ()
		self.gb['clinical.submenu'] = ourmenu
		menu = self.gb['main.viewmenu']
		self.menu_id = wxNewId ()
		menu.AppendMenu (self.menu_id, '&Clinical', ourmenu, self.name ())
		# "patient" needs fixing
		plugin_list = gmPlugin.GetPluginLoadList('patient')
		# "patient" needs fixing
		for plugin in plugin_list:
			p = gmPlugin.InstPlugin(
				'patient',
				plugin,
				guibroker = self.gb
			)
			try:
				p.register()
			except:
				_log.LogException("file [%s] doesn't seem to be a plugin" % plugin, sys.exc_info(), fatal=0)
		#self.panel.Show (0)
		self.panel.DisplayDefault()
		self.gb['toolbar.%s' % self.name ()].Realize()
	#----------------------------------------------
	def unregister (self):
		# tidy up after ourselves
		gmPlugin.wxNotebookPlugin.unregister (self)
		menu = self.gb['main.viewmenu']
		menu.Destroy (self.menu_id)
		# FIXME: should we unregister () each of our sub-modules?
	#----------------------------------------------
	def ReceiveFocus(self):
		self.gb['modules.patient'][self.panel.GetVisible()].Shown()
#==================================================
# $Log: gmClinicalWindowManager.py,v $
# Revision 1.1  2003-04-04 23:15:46  ncq
# - renamed to clinical* as per Richard's request
# - updated plugins.conf.sample
#
# Revision 1.15  2003/02/09 20:03:43  ncq
# - Shown -> ReceiveFocus
#
# Revision 1.14  2003/02/09 10:30:49  ncq
# - cleanup
#
# Revision 1.13  2003/02/09 01:08:03  sjtan
#
# a patient handler class for the classes in patient directory. Not all controls seem exposed.
#
# Revision 1.12  2003/01/12 16:46:42  ncq
# - catch failing plugins better
#
# Revision 1.11  2003/01/12 01:48:47  ncq
# - massive cleanup, CVS keywords
#
