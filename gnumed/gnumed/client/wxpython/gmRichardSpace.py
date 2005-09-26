"""GnuMed Richard-space inner-frame layout manager.

This implements a Listbook based layout according to the specifications of Richard Terry
Based on gmHorstSpace manager
Ironically, uses code/concepts from Horst's "gnumed-mini"

This source code is protected by the GPL licensing scheme.
Details regarding the GPL are available at http://www.gnu.org
You may use and share it as long as you don't deny this right
to anybody else.

copyright: authors
"""
#==============================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/Attic/gmRichardSpace.py,v $
# $Id: gmRichardSpace.py,v 1.6 2005-09-26 18:01:51 ncq Exp $
__version__ = "$Revision: 1.6 $"
__author__  = "H. Herb <hherb@gnumed.net>,\
K. Hilbert <Karsten.Hilbert@gmx.net>,\
I. Haywood <ihaywood@gnu.org>>\
R. Terry <rterry@gnumed.net>"
__license__ = 'GPL (details at http://www.gnu.org)'

import os.path, os, sys

try:
	import wxversion
	import wx
except ImportError:
	from wxPython import wx

from Gnumed.pycommon import gmGuiBroker, gmI18N, gmLog, gmWhoAmI
from Gnumed.wxpython import gmPlugin

_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)
_whoami = gmWhoAmI.cWhoAmI()
		  
#==============================================================================
class cLayoutMgr(wx.Panel):
	"""GnuMed inner-frame layout manager.

	This implements a wx.Listbook based layout manager.
	WARNING: ** wxWidgets 2.5 ONLY **
	"""
	def __init__(self, parent, id):
		# main panel
		wx.Panel.__init__(
			self,
			parent = parent,
			id = id,
			pos = wx.DefaultPosition,
			size = wx.DefaultSize,
			style = wx.NO_BORDER,
			name = 'RichardSpace.LayoutMgrPnl'
		)
		# notebook
		self.ID_NOTEBOOK = wx.NewId()
		self.nb = wx.Listbook (
			parent=self,
			id = self.ID_NOTEBOOK,
			size = wx.Size(320,240),
			style = wx.LB_LEFT
		)
		# plugins
		self.__gb = gmGuiBroker.GuiBroker()
		self.__gb['richardspace.notebook'] = self.nb # FIXME: remove per Ian's API suggestion
		self.__load_plugins()
		
		# layout handling
		self.main_szr = wx.BoxSizer(wx.HORIZONTAL)
		self.main_szr.Add(self.nb, 1, wx.EXPAND)
		self.SetSizer(self.main_szr)
#		self.SetSizerAndFit(self.main_szr)
#		self.Layout()
		self.Show(True)

		self.__register_events()
	#----------------------------------------------
	# internal API
	#----------------------------------------------
	def __register_events(self):
		# - popup menu on right click in notebook
		#wx.EVT_RIGHT_UP(self.nb, self._on_right_click)
		pass
	#----------------------------------------------
	def __load_plugins(self):
		# get plugin list
		plugin_list = gmPlugin.GetPluginLoadList('terry_layout.plugins', defaults = ['Gnumed.wxpython.gmDemographics.Demographics'])
		if plugin_list is None:
			_log.Log(gmLog.lWarn, "no plugins to load")
			return True

		wx.BeginBusyCursor()
		nr_plugins = len(plugin_list)

		#  set up a progress bar
		progress_bar = gmPlugin.cLoadProgressBar(nr_plugins)

		#  and load them
		prev_plugin = ""
		result = -1
		self.plugins = []
		self.map_plugins = {}
		for idx in range(len(plugin_list)):
			curr_plugin = plugin_list[idx]
			progress_bar.Update(result, curr_plugin)
			try:
				l = curr_plugin.split (".")
				p = __import__ (".".join (l[:-1]))
				for i in l[1:]:
					p = getattr (p, i)
				inst = p(self.nb)
				self.plugins.append (inst)
				self.map_plugins[curr_plugin] = inst
				result = 1
			except:
				_log.LogException('failed to load plugin %s' % curr_plugin, sys.exc_info(), verbose = 0)
				result = 0
			prev_plugin = curr_plugin
		progress_bar.Destroy()
		imagelist = wx.ImageList (32, 32)
		default_bitmap = None
		for i in self.plugins:
			png_fname = os.path.join(self.__gb['gnumed_dir'], 'bitmaps', '%s.png' % getattr (i, "icon", i.__class__.__name__))
			icon = wx.EmptyIcon()
			if not os.access (png_fname, os.R_OK):
				png_fname = os.path.join(self.__gb['gnumed_dir'], 'bitmaps', 'default.png')
			icon.LoadFile(png_fname, wx.BITMAP_TYPE_PNG)
			imagelist.AddIcon (icon)
		self.nb.AssignImageList (imagelist)
		for i in range (0, len (self.plugins)):
			self.nb.AddPage (self.plugins[i], getattr (self.plugins[i], 'name', self.plugins[i].__class__.__name__), 0, i)
		wx.EndBusyCursor()
		return True

#==============================================================================
	

#==============================================================================
# $Log: gmRichardSpace.py,v $
# Revision 1.6  2005-09-26 18:01:51  ncq
# - use proper way to import wx26 vs wx2.4
# - note: THIS WILL BREAK RUNNING THE CLIENT IN SOME PLACES
# - time for fixup
#
# Revision 1.5  2005/09/25 17:34:11  ncq
# - back to 2.4 import until compatible way for 2.6 is found
#
# Revision 1.4  2005/09/25 01:00:47  ihaywood
# bugfixes
#
# remember 2.6 uses "import wx" not "from wxPython import wx"
# removed not null constraint on clin_encounter.rfe as has no value on instantiation
# client doesn't try to set clin_encounter.description as it doesn't exist anymore
#
# Revision 1.3  2005/09/24 09:17:29  ncq
# - some wx2.6 compatibility fixes
#
# Revision 1.2  2005/02/18 11:16:41  ihaywood
# new demographics UI code won't crash the whole client now ;-)
# still needs much work
# RichardSpace working
#
# Revision 1.1  2005/02/01 10:16:07  ihaywood
# refactoring of gmDemographicRecord and follow-on changes as discussed.
#
# gmTopPanel moves to gmHorstSpace
# gmRichardSpace added -- example code at present, haven't even run it myself
# (waiting on some icon .pngs from Richard)
#



# log carried over from gmHorstSpace.py:
# Revision 1.6  2004/10/17 16:06:30  ncq
# - silly whitespace fix
#
# Revision 1.5  2004/10/16 22:42:12  sjtan
#
# script for unitesting; guard for unit tests where unit uses gmPhraseWheel; fixup where version of wxPython doesn't allow
# a child widget to be multiply inserted (gmDemographics) ; try block for later versions of wxWidgets that might fail
# the Add (.. w,h, ... ) because expecting Add(.. (w,h) ...)
#
# Revision 1.4  2004/10/14 12:11:18  ncq
# - improve comments
#
# Revision 1.3  2004/09/13 08:53:02  ncq
# - gmMacroPrimitives.raise_notebook_plugin() didn't work since
#   cHorstSpaceLayoutMgr used guibroker['horstspace.plugins'] rather
#   than 'horstspace.notebook.gui'
#
# Revision 1.2  2004/08/18 08:17:40  ncq
# - wxMac workaround for missing wxIcon.LoadFile()
#
# Revision 1.1  2004/08/08 23:54:37  ncq
# - factored out Horst space layout manager
#
