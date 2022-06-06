# -*- coding: utf-8 -*-

"""GNUmed TUI client.

This contains the TUI application framework and main window
of the all signing all dancing GNUmed Python Reference
client. It relies on the <gnumed.py> launcher having set up
the non-GUI-related runtime environment.

copyright: authors
"""
#==============================================================================
__author__  = "K. Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = 'GPL v2 or later (details at https://www.gnu.org)'

# stdlib
import sys
#import time
#import os
#import os.path
#import datetime as pyDT
#import shutil
import logging
#import subprocess
#import glob

_log = logging.getLogger('gm.tui')


# GNUmed libs
#from Gnumed.pycommon import gmCfgINI
#_cfg = gmCfgINI.gmCfgData()


# 3rd party libs: urwid
try:
	import urwid as urw
	_log.info('urwid version: %s', urw.__version__)
except ImportError:
	_log.exception('cannot import urwid')
	print('GNUmed startup: Cannot import urwid library.')
	print('GNUmed startup: Make sure urwid is installed.')
	print('CRITICAL ERROR: Error importing urwid. Halted.')
	raise

# more GNUmed libs
#from Gnumed.pycommon import gmCfgDB
#from Gnumed.pycommon import gmPG2
#from Gnumed.pycommon import gmDispatcher
#from Gnumed.pycommon import gmI18N
#from Gnumed.pycommon import gmExceptions
#from Gnumed.pycommon import gmShellAPI
#from Gnumed.pycommon import gmTools
#from Gnumed.pycommon import gmDateTime
#from Gnumed.pycommon import gmHooks
#from Gnumed.pycommon import gmBackendListener
#from Gnumed.pycommon import gmLog2
#from Gnumed.pycommon import gmNetworkTools
#from Gnumed.pycommon import gmMimeLib
#from Gnumed.pycommon import gmConnectionPool

#from Gnumed.business import gmPerson
#from Gnumed.business import gmClinicalRecord
#from Gnumed.business import gmPraxis
#from Gnumed.business import gmEMRStructItems
#from Gnumed.business import gmArriba
#from Gnumed.business import gmStaff

#from Gnumed.exporters import gmPatientExporter


TUI_TITLE = "GNUmed TUI"

TUI_PALETTE = [
	('body','black','light gray'),#, 'standout'),
	('reverse','light gray','black'),
	('footer','black','dark cyan'),
	('header', 'black', 'dark gray'),
	('important','dark blue','light gray',('standout','underline')),
	('editfc','white', 'dark blue', 'bold'),
	('editbx','light gray', 'dark blue'),
	('editcp','black','light gray', 'standout'),
	('bright','dark gray','light gray', ('bold','standout')),
	('buttn','black','dark cyan'),
	('buttnf','white','dark blue','bold'),
]

#==============================================================================
class gmTuiTopLevelFrame(urw.Frame):

	def __init__(self):
		self.__body = urw.AttrWrap(urw.Filler(urw.Text('A simple test')), 'body')
		self.__caption = urw.AttrWrap(urw.Text(TUI_TITLE, align = 'center'), 'header')
		self.__statusline = urw.AttrWrap(urw.Text('F10:exit - F7:search'), 'footer')
		footer = None
		super().__init__ (
			self.__body,
			header = self.__caption,
			footer = self.__statusline,
			focus_part = 'body'
		)

#==============================================================================
def main():

	def topmost_unhandled_key(key):
		if key == 'f1':
			main_screen.clear()
		if key == 'f10':
			raise urw.ExitMainLoop()

	# use appropriate Screen class
	main_screen = urw.raw_display.Screen()
	main_screen.set_mouse_tracking(False)
	#listbox = urw.ListBox(urw.SimpleListWalker(listbox_content))
	#main_frame = urw.Frame(urw.AttrWrap(listbox, 'body'), header = main_header)
	#main_frame = urw.Frame(main_body, header = main_header)
	mainloop = urw.MainLoop (
		gmTuiTopLevelFrame(),
		palette = TUI_PALETTE,
		unhandled_input = topmost_unhandled_key,
		screen = main_screen
	)
	mainloop.run()
