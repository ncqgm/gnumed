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

import gmException

class gmPlugin:
	"base class for all gnumed plugins"
	def register(self, parentwidget=None):
		raise gmException.PureVirtualFunction()

	def unregister(self):
		raise gmException.PureVirtualFunction()



class wxGuiPlugin(gmPlugin)
	"base class for all plugins providing wxPython widgets"
	def __init__(self, guibroker=None, callbackbroker=None, dbbroker=None):
		self.__gb = guibroker
		self.__cb = callbackbroker
		self.__db = dbbroker

	def getMainWidget(self):
		raise gmException.PureVirtualFunction()
