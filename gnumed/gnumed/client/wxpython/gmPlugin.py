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

import gmExceptions

class gmPlugin:
	"base class for all gnumed plugins"
	def __init__(self, name):
		self.__name = name

	def name(self):
		return self.__name

	def register(self, parentwidget=None):
		raise gmExceptions.PureVirtualFunction()

	def unregister(self):
		raise gmExceptions.PureVirtualFunction()



class wxGuiPlugin(gmPlugin):
	"base class for all plugins providing wxPython widgets"
	def __init__(self, name, guibroker=None, callbackbroker=None, dbbroker=None):
		gmPlugin.__init__(name)
		self.__gb = guibroker
		self.__cb = callbackbroker
		self.__db = dbbroker

	def getMainWidget(self):
		raise gmExceptions.PureVirtualFunction()


if __name__ == "__main__":

	plugin = gmPlugin("A plugin")
	print "Plugin installed: ", plugin.name()

	print "This should throw an exception:"
	plugin.register()