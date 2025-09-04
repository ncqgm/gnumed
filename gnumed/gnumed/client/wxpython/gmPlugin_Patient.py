"""gmPlugin_Patient - base classes for GNUMed's patient plugin architecture.

@copyright: author
@license: GPL v2 or later (details at https://www.gnu.org)
"""
############################################################################
__author__ = "H.Herb, I.Haywood, K.Hilbert"

import pickle, zlib

import wx

from Gnumed.pycommon import gmGuiBroker
from Gnumed.wxpython import gmShadow

gmPerson = None

#------------------------------------------------------------------
class BasePlugin:
	"""Base class for all plugins providing wxPython widgets.

	Plugins must have a class descending of this class in
	their file, which MUST HAVE THE SAME NAME AS THE FILE.

	The file must be in a directory which is loaded by
	LoadPluginSet (gui/ for the moment, others may be
	added for different plugin types)
	"""
	# NOTE: I anticipate that all plugins will in fact be derived
	# from this class. Without the brokers a plugin is useless (IH)
	def __init__(self, set='', guibroker=None, callbackbroker=None, params=None):
		self.gb = guibroker
		self.cb = callbackbroker
		if self.gb is None:
			self.gb = gmGuiBroker.GuiBroker()
		self.set = set
	#-----------------------------------------------------
	def GetIcon (self):
		"""Return icon representing page on the toolbar.

		This is the default behaviour. GetIconData should return
		pickled, compressed and escaped string with the icon data.

		If you want to change the behaviour (because you want to load
		plugin icons from overseas via a satellite link or something
		you need to override this function in your plugin (class).

		Using this standard code also allows us to only import cPickle
		and zlib here and not in each and every plugin module which
		should speed up plugin load time :-)
		"""
		# FIXME: load from config which plugin we want
		# which_icon is a cookie stored on the backend by a config manager,
		# it tells the plugin which icon to return data for,
		which_icon = None
		icon_data = self.GetIconData(which_icon)
		if icon_data is None:
			return None
		else:
			return wx.BitmapFromXPMData(pickle.loads(zlib.decompress(icon_data)))
	#-----------------------------------------------------
	def GetIconData(self, anIconID = None):
		# FIXME: in overriding methods need to be very careful about the
		# type of the icon ID since if we read it back from the database we
		# may not know what type it was
		return None
	#-----------------------------------------------------
	def GetWidget (self, parent):
		"""
		Return the widget to display. Usually called from
		register(). The instance returned is the
		active object for event handling purposes.
		"""
		raise AttributeError('no such patient plugin - GetWidget')
	#-----------------------------------------------------
	def MenuInfo (self):
		"""Return tuple of (menuname, menuitem).

		menuname can be
			"tools",
			"view",
			"help",
			"file"

		If you return "None" no entry will be placed
		in any menu.
		"""
		raise AttributeError('no such patient plugin - MenuInfo')
	#-----------------------------------------------------
	def Raise (self):
		"""Raises this plugin to the top level if not visible.
		"""
		raise AttributeError('no such patient plugin - Raise')
	#-----------------------------------------------------
	def ReceiveFocus(self):
		"""Called whenever this module receives focus and is thus shown onscreen.
		"""
		pass
	#-----------------------------------------------------
	def register(self):
		# register ANY type of plugin, regardless of where plugged in
		# we may be able to do away with this once we don't do
		# several types of plugins anymore, as we should
		self.gb['modules.%s' % self.set][self.__class__.__name__] = self		# split/renamed 'horstspace.notebook.%s'
		#_log.Log(gmLog.lInfo, "plugin: [%s] (class: [%s]) set: [%s]" % (self.name(), self.__class__.__name__, self.set))
	#-----------------------------------------------------
	def unregister(self):
		del self.gb['modules.%s' % self.set][self.__class__.__name__]			# split/renamed 'horstspace.notebook.%s'
		#_log.Log(gmLog.lInfo, "plugin: [%s] (class: [%s]) set: [%s]" % (self.name(), self.__class__.__name__, self.set))
	#-----------------------------------------------------
	def name(self):
		return 'plugin %s' % self.__class__.__name__
#------------------------------------------------------------------
class wxPatientPlugin (BasePlugin):
	"""
	A 'small page', sits inside the patient view, with the side visible
	"""
	def register (self):
		BasePlugin.register (self)
		self.mwm = self.gb['clinical.manager']

		# FIXME: do proper config check for shadowing
		# FIXME: do we always want shadows and set it to 0 width via themes ?
		shadow = gmShadow.Shadow (self.mwm, -1)
		widget = self.GetWidget (shadow)
		shadow.SetContents (widget)
		self.mwm.RegisterLeftSide (self.__class__.__name__, shadow)

		icon = self.GetIcon ()
		if icon is not None:
			tb2 = self.gb['toolbar.%s' % 'gmClinicalWindowManager']
			#tb2.AddSeparator()
			self.tool_id = wx.NewId ()
			#tool1 = 
			tb2.AddTool(
				self.tool_id,
				icon,
				shortHelpString = self.name()
			)
			wx.EVT_TOOL (tb2, self.tool_id, self.OnTool)
		menuname = self.name ()
		menu = self.gb['clinical.submenu']
		self.menu_id = wx.NewId ()
		menu.Append (self.menu_id, menuname)
		#wx.EVT_MENU (..., self.menu_id, self.OnTool)
	#-----------------------------------------------------
	def OnTool (self, event):
		self.ReceiveFocus()
		self.mwm.Display (self.__class__.__name__)
		# redundant as cannot access toolbar unless mwm raised
		#self.gb['modules.gui']['Patient'].Raise ()		# split/renamed 'horstspace.notebook.%s'
	#-----------------------------------------------------
	def Raise (self):
		self.gb['modules.gui']['Patient'].Raise()		# split/renamed 'horstspace.notebook.%s'
		self.mwm.Display (self.__class__.__name__)
	#-----------------------------------------------------
	def unregister (self):
		BasePlugin.unregister (self)
		self.mwm.Unregister (self.__class__.__name__)
		#menu = self.gb['main.submenu']
		#menu.Delete (menu_id)
		if self.GetIcon () is not None:
			tb2 = self.gb['toolbar.%s' % 'gmClinicalWindowManager']
			tb2.DeleteTool (self.tool_id)
		del self.gb['modules.patient'][self.__class__.__name__]

#==================================================================
# Main
#------------------------------------------------------------------
if __name__ == '__main__':
	print("please write a unit test")

#==================================================================
