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

import gmExceptions, os, sys, traceback
from gmLog import *
log = gmDefLog.Log
from wxPython.wx import *

class gmPlugin:
	# these are class variables which provide clues to the
	# configuration tool to make sure the set of plugins installed
	# are valid (plugins have the plugins they rely on installed
	# first, no conflict in installation occurs)

	
	"base class for all gnumed plugins"

	def name(self):
		return None

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

	def GetConfigPanel (self):
		"""
		Returns an instance of wxPluginConfig
		for the configuration tool
		"""
		return None

def LoadPluginSet (set, guibroker, dbbroker, defaults):
	"""
	Loads a set of plugins.
	set is a string specifying the subdirectory in which to
	find the plugins.
	There will be a general 'gui' directory for large GUI
	components: prescritions, etc., then several others for more
	specific types: export/import filters, crypto algorithms
	guibroker, dbbroker are broker objects provided
	defaults are the default set of plugins to be loaded
	(TODO: get plugin list from gmconfiguration for this user).
	"""
	toload = defaults
	# talk to database here instead
	dict = {}
	for name in toload:
		try:
			set_module = __import__ ("%s.%s" % (set, name))
			plugin_module = set_module.__dict__[name]
			plugin_class = plugin_module.__dict__[name]
			if issubclass (plugin_class, wxBasePlugin):
				plugin = plugin_class (guibroker = guibroker, dbbroker = dbbroker)
				plugin.register ()
				dict[plugin.name ()] = plugin
				log (lInfo, "registing plugin %s" % plugin.name ())
			else:
				log (lErr, "class %s is not a subclass of wxBasePlugin" % name)
		except Exception, error:
			frame = traceback.extract_tb (sys.exc_info ()[2])[-1]
			log (lErr, "cannot load module %s/%s:\nException: %s\nFile: %s\nLine: %s\n" % (set, name, error, frame[0], frame[1]))
	guibroker['modules.%s' % set] = dict
	# keep a record of plugins


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





