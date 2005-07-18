"""GnuMed Horst-space inner-frame layout manager.

This implements the simple wxNotebook based layout as
originally suggested by Horst Herb.

This source code is protected by the GPL licensing scheme.
Details regarding the GPL are available at http://www.gnu.org
You may use and share it as long as you don't deny this right
to anybody else.

copyright: authors
"""
#==============================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmHorstSpace.py,v $
# $Id: gmHorstSpace.py,v 1.9 2005-07-18 20:47:41 ncq Exp $
__version__ = "$Revision: 1.9 $"
__author__  = "H. Herb <hherb@gnumed.net>,\
			   K. Hilbert <Karsten.Hilbert@gmx.net>,\
			   I. Haywood <i.haywood@ugrad.unimelb.edu.au>"
__license__ = 'GPL (details at http://www.gnu.org)'

import os.path, os, sys

from wxPython.wx import *
import wx

from Gnumed.pycommon import gmGuiBroker, gmI18N, gmLog, gmWhoAmI
from Gnumed.wxpython import gmPlugin, gmTopPanel

_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)
_whoami = gmWhoAmI.cWhoAmI()
		  
#==============================================================================
class cHorstSpaceLayoutMgr(wxPanel):
	"""GnuMed inner-frame layout manager.

	This implements a Horst-space notebook-only
	"inner-frame" layout manager.
	"""
	def __init__(self, parent, id):
		# main panel
		wxPanel.__init__(
			self,
			parent = parent,
			id = id,
			pos = wxPyDefaultPosition,
			size = wxPyDefaultSize,
			style = wxNO_BORDER,
			name = 'HorstSpace.LayoutMgrPnl'
		)
		# notebook
		self.ID_NOTEBOOK = wxNewId()
		self.nb = wxNotebook (
			parent=self,
			id = self.ID_NOTEBOOK,
			size = wxSize(320,240),
			style = wxNB_BOTTOM
		)
		#nb_szr = wx.wxNotebookSizer(self.nb)
		# plugins
		self.__gb = gmGuiBroker.GuiBroker()
		self.__gb['horstspace.notebook'] = self.nb # FIXME: remove per Ian's API suggestion

		# top panel
		#---------------------
		# create the "top row"
		#---------------------
		# important patient data is always displayed there
		# - top panel with toolbars
		self.top_panel = gmTopPanel.cMainTopPanel(self, -1)
		self.__gb['horstspace.top_panel'] = self.top_panel
		self.__load_plugins()
		
		# layout handling
		self.main_szr = wxBoxSizer(wx.VERTICAL)
		self.main_szr.Add(self.top_panel, 0, wxEXPAND)
		self.main_szr.Add(self.nb, 1, wxEXPAND)
		self.SetSizer(self.main_szr)
#		self.SetSizerAndFit(self.main_szr)
#		self.Layout()
#		self.Show(True)

		self.__register_events()
	#----------------------------------------------
	# internal API
	#----------------------------------------------
	def __register_events(self):
		# - notebook page is about to change
		wx.EVT_NOTEBOOK_PAGE_CHANGING (self.nb, self.ID_NOTEBOOK, self._on_notebook_page_changing)
		# - notebook page has been changed
		wx.EVT_NOTEBOOK_PAGE_CHANGED (self.nb, self.ID_NOTEBOOK, self._on_notebook_page_changed)
		# - popup menu on right click in notebook
		wx.EVT_RIGHT_UP(self.nb, self._on_right_click)
	#----------------------------------------------
	def __load_plugins(self):
		# get plugin list
		plugin_list = gmPlugin.GetPluginLoadList('horstspace.notebook.plugin_load_order', 'gui')
		if plugin_list is None:
			_log.Log(gmLog.lWarn, "no plugins to load")
			return True

		wxBeginBusyCursor()
		nr_plugins = len(plugin_list)

		#  set up a progress bar
		progress_bar = gmPlugin.cLoadProgressBar(nr_plugins)

		#  and load them
		prev_plugin = ""
		result = -1
		for idx in range(len(plugin_list)):
			curr_plugin = plugin_list[idx]
			progress_bar.Update(result, curr_plugin)
			try:
				plugin = gmPlugin.instantiate_plugin('gui', curr_plugin)
				if plugin:
					plugin.register()
					result = 1
				else:
					_log.Log (gmLog.lErr, "plugin [%s] not loaded, see errors above" % curr_plugin)
					result = 1
			except:
				_log.LogException('failed to load plugin %s' % curr_plugin, sys.exc_info(), verbose = 0)
				result = 0

			prev_plugin = curr_plugin

		progress_bar.Destroy()
		wxEndBusyCursor()
		return True
	#----------------------------------------------
	# external callbacks
	#----------------------------------------------
	def _on_notebook_page_changing(self, event):
		"""Called before notebook page change is processed.
		"""
		self.__new_page_is_checked = False
		# FIXME: this is the place to tell the old page to
		# make it's state permanent somehow, in general, call
		# any "validators" for the old page here
		self.__id_prev_page = event.GetOldSelection()
		id_new_page = event.GetSelection()
		_log.Log(gmLog.lData, 'about to switch notebook tabs: %s -> %s' % (self.__id_prev_page, id_new_page))
		if id_new_page == self.__id_prev_page:
			# the docs say that on Windows GetSelection() returns the
			# old page ID, eg. the same value that GetOldSelection()
			# returns, hence we don't have any way of knowing which
			# page is going to be it, so we just return assuming things are fine
			_log.Log(gmLog.lInfo, 'cannot check whether page change needs to be veto()ed')
			event.Skip()
			return
		# check new page
		new_page = self.__gb['horstspace.notebook.pages'][id_new_page]
		if not new_page.can_receive_focus():
			_log.Log(gmLog.lData, 'veto()ing page change')
			event.Veto()
			return
		self.__new_page_is_checked = True
		event.Skip()
	#----------------------------------------------
	def _on_notebook_page_changed(self, event):
		"""Called when notebook changes.

		FIXME: we can maybe change title bar information here
		"""
		id_new_page = event.GetSelection()
		id_old_page = event.GetOldSelection()
		_log.Log(gmLog.lData, 'switching notebook tabs: %s (%s) -> %s' % (id_old_page, self.__id_prev_page, id_new_page))
		# get access to selected page
		new_page = self.__gb['horstspace.notebook.pages'][id_new_page]
		# do we need to check the new page ?
		if self.__new_page_is_checked or new_page.can_receive_focus():
			new_page.receive_focus()
			# activate toolbar of new page
			self.__gb['horstspace.top_panel'].ShowBar(new_page.__class__.__name__)
			event.Skip()
			return

		_log.Log(gmLog.lWarn, "new page cannot receive focus but too late for veto (typically happens on Windows and Mac OSX)")
		# let's try a trick
		if id_old_page != id_new_page:
			_log.Log(gmLog.lInfo, 'faking veto() with SetSelection(id_old_page)')
#			event.SetSelection(id_old_page)
			wx.CallAfter(self.nb.SetSelection, id_old_page)
		# or two
		elif self.__id_prev_page != id_new_page:
			_log.Log(gmLog.lInfo, 'faking veto() with SetSelection(self.__id_prev_page)')
#			event.SetSelection(self.__id_prev_page)
			wx.CallAfter(self.nb.SetSelection, self.__id_prev_page)
		else:
			_log.Log(gmLog.lInfo, 'cannot even veto page change with tricks')
		event.Skip()
	#----------------------------------------------
	def _on_right_click(self, evt):
		load_menu = wxMenu()
		any_loadable = 0
		plugin_list = gmPlugin.GetPluginLoadList('gui')
		plugin = None
		for plugin_name in plugin_list:
			try:
				plugin = gmPlugin.instantiate_plugin('gui', plugin_name)
			except StandardError:
				continue
			# not a plugin
			if not isinstance(plugin, gmPlugin.cNotebookPlugin):
				plugin = None
				continue
			# already loaded ?
			if plugin.__class__.__name__ in self.guibroker['horstspace.notebook.gui'].keys():
				plugin = None
				continue
			# add to load menu
			nid = wxNewId()
			load_menu.AppendItem(wxMenuItem(load_menu, nid, plugin.name()))
			EVT_MENU(load_menu, nid, plugin.on_load)
			any_loadable = 1
		# make menus
		menu = wxMenu()
		ID_LOAD = wxNewId()
		ID_DROP = wxNewId()
		if any_loadable:
			menu.AppendMenu(ID_LOAD, _('add plugin ...'), load_menu)
		plugins = self.guibroker['horstspace.notebook.gui']
		raised_plugin = plugins[self.nb.GetSelection()].name()
		menu.AppendItem(wxMenuItem(menu, ID_DROP, "drop [%s]" % raised_plugin))
		EVT_MENU (menu, ID_DROP, self._on_drop_plugin)
		self.PopupMenu(menu, evt.GetPosition())
		menu.Destroy()
#		evt.Skip()
	#----------------------------------------------		
	def _on_drop_plugin(self, evt):
		"""Unload plugin and drop from load list."""
		pages = self.guibroker['horstspace.notebook.pages']
		page = pages[self.nb.GetSelection()]
		page.unregister()
		self.nb.AdvanceSelection()
		# FIXME:"dropping" means talking to configurator so not reloaded
	#----------------------------------------------
	def _on_hide_plugin (self, evt):
		"""Unload plugin but don't touch configuration."""
		# this dictionary links notebook page numbers to plugin objects
		pages = self.guibroker['horstspace.notebook.pages']
		page = pages[self.nb.GetSelection()]
		page.unregister()
#==============================================================================
if __name__ == '__main__':
	wxInitAllImageHandlers()
	pgbar = gmPluginLoadProgressBar(3)

#==============================================================================
# $Log: gmHorstSpace.py,v $
# Revision 1.9  2005-07-18 20:47:41  ncq
# - try to improve notebook page changing trick
#   needed on Windows
#
# Revision 1.8  2005/02/01 19:20:23  ncq
# - just silly cleanup
#
# Revision 1.7  2005/02/01 10:16:07  ihaywood
# refactoring of gmDemographicRecord and follow-on changes as discussed.
#
# gmTopPanel moves to gmHorstSpace
# gmRichardSpace added -- example code at present, haven't even run it myself
# (waiting on some icon .pngs from Richard)
#
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
