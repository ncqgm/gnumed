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
# $Id: gmHorstSpace.py,v 1.2 2004-08-18 08:17:40 ncq Exp $
__version__ = "$Revision: 1.2 $"
__author__  = "H. Herb <hherb@gnumed.net>,\
			   K. Hilbert <Karsten.Hilbert@gmx.net>,\
			   I. Haywood <i.haywood@ugrad.unimelb.edu.au>"
__license__ = 'GPL (details at http://www.gnu.org)'

import os.path, os

from wxPython import wx
from wxPython.wx import *

from Gnumed.pycommon import gmGuiBroker, gmI18N, gmLog, gmWhoAmI
from Gnumed.wxpython import gmPlugin

_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)
_whoami = gmWhoAmI.cWhoAmI()

#==============================================================================
class gmPluginLoadProgressBar (wx.wxProgressDialog):
	def __init__(self, nr_plugins):
		wx.wxProgressDialog.__init__(
			self,
			title = _("GnuMed: configuring [%s] (%s plugins)") % (_whoami.get_workplace(), nr_plugins),
			message = _("loading list of plugins                               "),
			maximum = nr_plugins,
			parent = None,
			style = wx.wxPD_ELAPSED_TIME
			)
		# set window icon
		gb = gmGuiBroker.GuiBroker()
		png_fname = os.path.join(gb['gnumed_dir'], 'bitmaps', 'serpent.png')
		icon = wxEmptyIcon()
		try:
			icon.LoadFile(png_fname, wxBITMAP_TYPE_PNG)
		except:
			_log.Log(gmLog.lWarn, 'wxIcon.LoadFile() not supported')
		self.SetIcon(icon)

#==============================================================================
class cHorstSpaceLayoutMgr(wx.wxPanel):
	"""GnuMed inner-frame layout manager.

	This implements a Horst-space notebook-only
	"inner-frame" layout manager.
	"""
	def __init__(self, parent, id):
		# main panel
		wx.wxPanel.__init__(
			self,
			parent = parent,
			id = id,
			pos = wx.wxPyDefaultPosition,
			size = wx.wxPyDefaultSize,
			style = wx.wxNO_BORDER,
			name = 'HorstSpace.LayoutMgrPnl'
		)
		# notebook
		self.ID_NOTEBOOK = wx.wxNewId()
		self.nb = wx.wxNotebook (
			parent=self,
			id = self.ID_NOTEBOOK,
			size = wx.wxSize(320,240),
			style = wx.wxNB_BOTTOM
		)
		nb_szr = wx.wxNotebookSizer(self.nb)

		# plugins
		self.__gb = gmGuiBroker.GuiBroker()
		self.__gb['horstspace.notebook'] = self.nb			# FIXME: remove per Ian's API suggestion
		self.__load_plugins()

		# layout handling
		self.main_szr = wx.wxBoxSizer(wx.wxHORIZONTAL)
		self.main_szr.Add(nb_szr, 1, wx.wxEXPAND)
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
		plugin_list = gmPlugin.GetPluginLoadList('gui')
		if plugin_list is None:
			_log.Log(gmLog.lWarn, "no plugins to load")
			return True

		wx.wxBeginBusyCursor()
		nr_plugins = len(plugin_list)

		#  set up a progress bar
		progress_bar = gmPluginLoadProgressBar(nr_plugins)

		#  and load them
		prev_plugin = ""
		result = ""
		for idx in range(len(plugin_list)):
			curr_plugin = plugin_list[idx]

			progress_bar.Update(
				idx,
				_("previous: %s (%s)\ncurrent (%s/%s): %s") % (
					prev_plugin,
					result,
					(idx+1),
					nr_plugins,
					curr_plugin)
			)

			try:
				plugin = gmPlugin.instantiate_plugin('gui', curr_plugin)
				if plugin:
					plugin.register()
					result = _("success")
				else:
					_log.Log (gmLog.lErr, "plugin [%s] not loaded, see errors above" % curr_plugin)
					result = _("failed")
			except:
				_log.LogException('failed to load plugin %s' % curr_plugin, sys.exc_info(), verbose = 0)
				result = _("failed")

			prev_plugin = curr_plugin

		progress_bar.Destroy()
		wx.wxEndBusyCursor()
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
			# page is going to be it
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
			self.__gb['main.top_panel'].ShowBar(new_page.__class__.__name__)
			event.Skip()
			return

		_log.Log(gmLog.lWarn, "new page cannot receive focus but too late for veto (typically happens on Windows and Mac OSX)")
		# let's try a trick
		if id_old_page != id_new_page:
			_log.Log(gmLog.lInfo, 'veto()ing with SetSelection(id_old_page)')
			event.SetSelection(id_old_page)
		# or two
		elif self.__id_prev_page != id_new_page:
			_log.Log(gmLog.lInfo, 'veto()ing with SetSelection(self.__id_prev_page)')
			event.SetSelection(self.__id_prev_page)
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
			if plugin.__class__.__name__ in self.guibroker['horstspace.plugins'].keys():
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
	wx.wxInitAllImageHandlers()
	pgbar = gmPluginLoadProgressBar(3)

#==============================================================================
# $Log: gmHorstSpace.py,v $
# Revision 1.2  2004-08-18 08:17:40  ncq
# - wxMac workaround for missing wxIcon.LoadFile()
#
# Revision 1.1  2004/08/08 23:54:37  ncq
# - factored out Horst space layout manager
#
