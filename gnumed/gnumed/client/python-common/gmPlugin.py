#!/usr/bin/python
#############################################################################
#
# gmPlugin - base classes for GNUMed's plugin architecture
# ---------------------------------------------------------------------------
#
# @author: Dr. Horst Herb
# @copyright: author
# @license: GPL (details at http://www.gnu.org)
# @dependencies: nil
# @change log:
#	08.03.2002 hherb first draft, untested
#
# @TODO: Almost everything
############################################################################

import gmExceptions, os, sys, re, traceback
from gmLog import *
log = gmDefLog.Log
from wxPython.wx import *
import gmGuiBroker, gmPG, gmConf, gmShadow

class gmPlugin:
	
	"base class for all gnumed plugins"


	def provides ():
		"""
		Returns a list of services that the plugin provides
		"""
		return []
	
	def requires ():
		"""
		Requires a list of services that must be registered
		before this plugin is registered. The configuration
		tool must check these and make sure the load order
		satisfies the plugins' requirements
		"""
		return []

	def description ():
		"""
		Returns a brief description of the plugin
		"""

	def name (self):
		return ''

	def register(self):
		raise gmExceptions.PureVirtualFunction()

	def unregister(self):
		raise gmExceptions.PureVirtualFunction()

class wxBasePlugin (gmPlugin):
	
	"""
	base class for all plugins providing wxPython widgets.
	Plugins must have a class descending of this class in their file, which MUST HAVE THE SAME NAME AS THE FILE.
	The file must be in a directory which is loaded by LoadPluginSet (gui/ for the moment, others may be added for different plugin types)
	
	"""
	# NOTE: I anticipate that all plugins will in fact be derived
	# from this class. Without the brokers a plugin is useless (IH)
	def __init__(self, guibroker=None, callbackbroker=None,
	dbbroker=None, params=None):
		self.gb = guibroker
		self.cb = callbackbroker
		self.db = dbbroker
		if self.gb is None:
			self.gb = gmGuiBroker.GuiBroker ()
		if self.db is None:
			self.db = gmPG.ConnectionPool ()

	def GetIcon (self):
		"""
		Return icon representing page on the toolbar
		"""
		return None

	def GetWidget (self, parent):
		"""
		Return the widget to display
		"""
		raise gmExceptions.PureVirtualFunction()

	def MenuInfo (self):
		"""
		Return tuple of (menuname, menuitem)
		"""
		raise gmExceptions.PureVirtualFunction()

class wxBigPagePlugin (wxBasePlugin):
	"""
	Base plugin for plugins which provide a 'big page'
	Either whole screen, or notebook if it exists
	"""

	
	def register (self):
		if gmConf.config ['main.use_notebook']:
			self.nb = self.gb['main.notebook']
			self.nb_no = self.nb.GetPageCount ()
			self.nb.AddPage (self.GetWidget (self.nb), self.name ())
		else:
			self.mwm = self.gb['main.manager']
			self.mwm.RegisterWholeScreen (self.name (), self.GetWidget (self.mwm))
			icon = self.GetIcon ()
			if icon is not None:
				tb2 = self.gb['main.bottom_toolbar']
				tb2.AddSeparator()
				self.tool_id = wxNewId ()
				tool1 = tb2.AddTool(self.tool_id, icon,
						    shortHelpString=self.name ())
				EVT_TOOL (tb2, tool_id, self.OnTool)
			
		menuset, menuname = self.MenuInfo ()
		menu = self.gb['main.%smenu' % menuset]
		self.menu_id = wxNewId ()
		menu.Append (self.menu_id, menuname, self.name ())
		EVT_MENU (self.gb['main.frame'], self.menu_id, self.OnTool)

	def unregister (self):
		menu = self.gb['main.%smenu' % self.MenuInfo ()[0]]
		menu.Delete (menu_id)
		if gmConf.config['main.use_notebook']:
			nb = gb['main.notebook']
			nb.DeletePage (self.nb_no)
		else:
			self.mwm.Unregister (self.name ())
			if self.GetIcon () is not None:
				tb2 = self.gb['main.bottom_toolbar']
				tb2.DeleteTool (self.tool_id)
		
	def OnTool (self, event):
		if gmConf.Get ('main.use_notebook'):
			self.nb.SetSelection (self.nb_no)
		else:
			self.mwm.Display (self.name ())

#


class wxSmallPagePlugin (wxBasePlugin):
	"""
	A 'small page', sits inside the patient view, with the sider visible
	"""
	def register (self):
		self.mwm = self.gb['main.manager']
		if gmConf.config['main.shadow']:
			shadow = gmShadow.Shadow (self.mwm, -1)
			widget = self.GetWidget (shadow)
			shadow.SetContents (widget)
			self.mwm.RegisterLeftSide (self.name (), shadow)
		else:
			self.mwm.RegisterLeftSide (self.name (), self.GetWidget (self.mwm))
		icon = self.GetIcon ()
		if icon is not None:
			tb2 = self.gb['main.bottom_toolbar']
			tb2.AddSeparator()
			self.tool_id = wxNewId ()
			tool1 = tb2.AddTool(self.tool_id, icon,
					    shortHelpString=self.name ())
			EVT_TOOL (tb2, self.tool_id, self.OnTool)
		menuset, menuname = self.MenuInfo ()
		menu = self.gb['main.%smenu' % menuset]
		self.menu_id = wxNewId ()
		menu.Append (self.menu_id, menuname, self.name ())
		EVT_MENU (self.gb['main.frame'], self.menu_id, self.OnTool)
        
	def OnTool (self, event):
		self.mwm.Display (self.name ())

	def unregister (self):
		self.mwm.Unregister (self.name ())
		menu = self.gb['main.%smenu' % self.MenuInfo ()[0]]
		menu.Delete (menu_id)
		if self.GetIcon () is not None:
			tb2 = self.gb['main.bottom_toolbar']
			tb2.DeleteTool (self.tool_id)
		
	    




def LoadPlugin (set, plugin_name, guibroker = None, dbbroker = None):
	"""
	Loads a plugins.
	set is a string specifying the subdirectory in which to
	find the plugins.
	There will be a general 'gui' directory for large GUI
	components: prescritions, etc., then several others for more
	specific types: export/import filters, crypto algorithms
	guibroker, dbbroker are broker objects provided
	defaults are the default set of plugins to be loaded
	(TODO: get plugin list from gmconfiguration for this user).
	"""
	if guibroker is None:
		guibroker = gmGuiBroker.GuiBroker ()
	if dbbroker is None:
		dbbroker = gmPG.ConnectionPool ()
	# talk to database here instead
	if not 'modules.%s' % set in guibroker.keylist ():
		guibroker['modules.%s' % set] = {}
	# keep a record of plugins
	try:
		set_module = __import__ ("%s.%s" % (set, plugin_name))
		plugin_module = set_module.__dict__[plugin_name]
		plugin_class = plugin_module.__dict__[plugin_name]
		if issubclass (plugin_class, wxBasePlugin):
			plugin = plugin_class (guibroker = guibroker, dbbroker = dbbroker)
			plugin.register ()
			guibroker['modules.%s' % set][plugin_name] = plugin
			log (lInfo, "registing plugin %s" % plugin_name)
		else:
			log (lErr, "class %s is not a subclass of wxBasePlugin" % name)
	except Exception, error:
		frame = traceback.extract_tb (sys.exc_info ()[2])[-1]
		log (lErr, "cannot load module %s/%s:\nException: %s\nFile: %s\nLine: %s\n" % (set, plugin_name, error, frame[0], frame[1]))

def GetAllPlugins (set):
	"""
	Searches the directory for all plugins
	"""
	gb = gmGuiBroker.GuiBroker ()
	dir = gb['gnumed_dir']
	# dir = '%s/wxpython/%s' % (dir, set)
	# HACK:
	dir = '%s/../test-area/terry/%s' % (dir, set)
	
	files = os.listdir (dir)
	ret = []
	for f in files:
		if re.compile ('.+\.py$').match (f) and f != '__init__.py':
			ret.append (f[:-3])
	return ret

	
def UnloadPlugin (set, name):
	"""
	Unloads the named plugin
	"""
	gb = gmGuiBroker.GuiBroker ()
	plugin = gb['modules.%s' % set][name]
	plugin.unregister ()
	del gb['modules.%s' % set][name]
	log (lInfo, "unloaded plugin %s/%s" % (set, name))


#####################################################################
# here is sample code of how to use gmPlugin.py:
#import inspect
#import gmPlugin
#
#try:
#    aPlugin = __import__("foo")
#except:
#    print "cannot import foo"
#    for plugin_class in inspect.getmembers (aPlugin, inspect.isclass):
#	if issubclass (plugin_class, gmPlugin.gmPlugin):
#	    plugin_class.register ()

#This also allows a single source file to define several plugin objects.





