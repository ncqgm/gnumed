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

import gmExceptions, os, inspect
from gmLog import gmDefLog

class gmPlugin:
	# these are class variables which provide clues to the
	# configuration tool to make sure the set of plugins installed
	# are valid (plugins have the plugins they rely on installed
	# first, no conflict in installation occurs)
	"""Requirements for the plugin.
	This is  a list of the plugin classes, an instance of which
	must be installed before this plugin can be installed. Thus, a
	hierarchy of requirements is formed, like Debian packages.
	"""
	requires = []

	"""Set to true if only one instance of this class may be installed"""
	single = 0

	
	"base class for all gnumed plugins"
	def __init__(self, name):
		self.__name = name

	def name(self):
		return self.__name

	def register(self, parentwidget=None):
		raise gmExceptions.PureVirtualFunction()

	def unregister(self):
		raise gmExceptions.PureVirtualFunction()

class wxBasePlugin (gmPlugin):
	
	"base class for all plugins providing wxPython widgets"
	def __init__(self, name, guibroker=None, callbackbroker=None,
	dbbroker=None, params=None):
		gmPlugin.__init__(self, name)
		self.__gb = guibroker
		self.__cb = callbackbroker
		self.__db = dbbroker


"Layout manager creating base windows and placing other plugins"
class wxLayoutManager (wxBasePlugin):
	"""Only one layout manager can be installed"""
	single = 1


	def __init__(self, name, guibroker=None, callbackbroker=None,
	dbbroker=None, params=None):
		wxBasePlugin.__init__ (self, name, guibroker,
	callbackbroker, dbbroker, params)

	def register ():
		__gb['layoutmanager'] = self

	"called by wxGuiPlugin.register to add plugin"
	def AddPlugin (self, plugin):
		gmExceptions.PureVirtualFunction ()

"Base class for gui elements"
class wxGuiPlugin (wxBasePlugin):
	requires = [wxLayoutManager]

	def __init__(self, name, guibroker=None, callbackbroker=None,
	dbbroker=None, params=None):
		wxBasePlugin.__init__ (self, name, guibroker,
	callbackbroker, dbbroker, params)

	def register ():
		self.__gb['layoutmanager'].AddPlugin (self)

	"Returns the wxPanel for display by the layout manager "
	def getMainWidget (self):
		gmExceptions.PureVirtualFunction ()

	"""Returns one of gmPP_SIDE (a small window on the
	side), gmPP_MAIN (the main window), gmPP_POPUP) a popup window)"""
	def PositionPreference (self):
		gmExceptions.PureVirtualFunction ()

	"Returns wxConfiguration for configuration window"
	def GetConfiguration (self):
		return None

	"Returns a wxIcon to represent this widget on a toolbar"
	def GetIcon (self):
		return None

"""Class representing contents of a configuration box for a plugin. Does
not have OK and cancel buttons"""
class wxPluginConfiguration (wxPanel):
	"""Returns config string when OK pressed. Widget destroyed
	for cancel"""
	def GetNewConfigString (self):
		gmExceptions.PureVirtualFunction ()

"A cryptographic algorithm"
class gmCrypto (gmPlugin):
	def __init__ (self, name):
		gmPlugin.__init__(self, name)
	
	def encrypt (self, plaintext, key):
		gmExceptions.PureVirtualFunction ()

	def decrypt (self, cyphertext, key):
		gmExceptions.PureVirtualFunction ()
		
"A plugin which uses crypto algorithms"
class gmCryptoUser ():
	def LoadAlgorithms ():
		self.algorithm = {}
		for file in os.listdir ('crypto'):
			if file[-3:] == '.py':
				# found python file!
				try:
					crypto_name = file[:-3]
					aPlugin = __import__('crypto.' + crypto_name)
					for plugin_class in inspect.getmembers (aPlugin, inspect.isclass):
						if issubclass (plugin_class, gmCrypto):
							self.algorithm[crypto_name] = plugin_class (crypto_name)
			
				except:
					gmDefLog (lErr, "can't load file: %s" % file)
				
			

if __name__ == "__main__":

	plugin = gmPlugin("A plugin")
	print "Plugin installed: ", plugin.name()

	print "This should throw an exception:"
	plugin.register()


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





