# -*- coding: utf-8 -*-
""" This is a template plugin.

This is in line with the blog series on developing a plugin
for GNUmed Read all posts to follow along a step by step
guide The first thirteen parts are a chronical on a plugin I
developed:

Part 1:  http://gnumed.blogspot.com/2009/04/gnumed-plugin-development-part-1.html
Part 2:  http://gnumed.blogspot.com/2009/04/gnumed-plugin-development-part-2.html
Part 3:  http://gnumed.blogspot.com/2009/04/gnumed-plugin-development-part-3.html
Part 4:  http://gnumed.blogspot.com/2009/04/gnumed-plugin-development-part-4.html
Part 5:  http://gnumed.blogspot.com/2009/04/gnumed-plugin-development-part-5.html
Part 6:  http://gnumed.blogspot.com/2009/04/gnumed-plugin-development-part-6.html
Part 7:  http://gnumed.blogspot.com/2009/04/gnumed-plugin-development-part-7.html
Part 8:  http://gnumed.blogspot.com/2009/04/gnumed-plugin-development-part-8.html
Part 9:  http://gnumed.blogspot.com/2009/04/gnumed-plugin-development-part-9.html
Part 10: http://gnumed.blogspot.com/2009/04/gnumed-plugin-development-part-10.html
Part 11: http://gnumed.blogspot.com/2009/05/gnumed-plugin-development-part-11.html
Part 12: http://gnumed.blogspot.com/2009/07/gnumed-plugin-development-part-12.html
Part 13: http://gnumed.blogspot.com/2009/07/gnumed-plugin-development-part-13.html

The second series is  more general and coves second plugin as a starting point
Part 1:  http://gnumed.blogspot.com/2010/04/gnumed-plugin-developement-part-1.html

The third series covers an hands on introduction on how to share your code
and how to test your plugin
Part 1:  http://gnumed.blogspot.com/2010/04/gnumed-plugin-development-how-to-share.html
Part 2:  http://gnumed.blogspot.com/2010/07/gnumed-plugin-development-easy-testing.html

For development information such as database schema, function and classes documentation
and more see https://www.gnumed.de/documentation/
"""

"""
This file is used together with 
../../wxg/wxgExamplePluginPnl.wxg            - this is the UI layout as done with wxglade
../../wxGladeWidgets/wxgExamplePluginPnl.py  - this is the generated python code of the above
../gmExamplePluginWidgets.py                 - holds the widgets of the user interface, it 
                                               imports and manipulates the above generated code 
"""

__author__ = "Sebastian Hilbert <Sebastian.Hilbert@gmx.net>"
__license__ = "GPL"

#================================================================
import os.path, sys, logging
import wx

if __name__ == '__main__':
	# stdlib
	import sys
	sys.path.insert(0, '../../../')

	from Gnumed.pycommon import gmI18N
	gmI18N.activate_locale()
	gmI18N.install_domain()

""" import the widgets from the file referencing the widgets 
for that particualr plugin (e.g. ExamplePlugin.
If you code your own plugin replace Example by something reflecting
what your plugin does. 
"""

from Gnumed.wxpython import gmPlugin, gmExamplePluginWidgets

_log = logging.getLogger('gm.ui')
#================================================================
#The name of the class must match the filename of the plugin
class gmExamplePlugin(gmPlugin.cNotebookPlugin):
	#name of the plugin as it will appear as tab in GNUmed
	tab_name = _("Template Plugin")

	def name (self):
		return gmExamplePlugin.tab_name
	#--------------------------------------------------------
	def GetWidget (self, parent):
		#Sets up the GUI by instanciating the file containing the widget that make up the layout in the plugin
		self._widget = gmExamplePluginWidgets.cExamplePluginPnl(parent, -1)
		return self._widget
	#--------------------------------------------------------
	def MenuInfo (self):
		#This will set the name of the Plugin in the GNUmed menu
		return ('emr', _('Show &ExamplePlugin'))
	#--------------------------------------------------------
	def can_receive_focus(self):
		# need patient
		""" uncomment the next two lines if a patient
		needs to be active before the plugin """
		#if not self._verify_patient_avail():
		#	return None
		return 1
	#--------------------------------------------------------
	def _on_raise_by_signal(self, **kwds):
		if not gmPlugin.cNotebookPlugin._on_raise_by_signal(self, **kwds):
			return False
		try:
			# add here any code you for the plugin executed after
			# raising the pugin
			pass
		except KeyError:
			pass
		return True
#================================================================
# MAIN
#----------------------------------------------------------------
if __name__ == '__main__':

	# GNUmed
	from Gnumed.business import gmPersonSearch
	from Gnumed.wxpython import gmPatSearchWidgets

	_log.info("starting template plugin...")

	# obtain patient
	patient = gmPersonSearch.ask_for_patient()
	if patient is None:
		print("No patient. Exiting gracefully...")
		sys.exit(0)
	gmPatSearchWidgets.set_active_patient(patient=patient)

	# display the plugin standalone
	application = wx.wx.PyWidgetTester(size = (800,600))
	widgets = gmExamplePluginWidgets.cExamplePluginPnl(application.frame, -1)

	application.frame.Show(True)
	application.MainLoop()

	# clean up
	if patient is not None:
		try:
			patient.cleanup()
		except Exception:
			print("error cleaning up patient")

	_log.info("closing example plugin...")
