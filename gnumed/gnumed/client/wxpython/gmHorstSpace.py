"""GnuMed Horst-space inner-frame layout manager.

This implements the simple wx.Notebook based layout as
originally suggested by Horst Herb.

This source code is protected by the GPL licensing scheme.
Details regarding the GPL are available at http://www.gnu.org
You may use and share it as long as you don't deny this right
to anybody else.

copyright: authors
"""
#==============================================================================
__version__ = "$Revision: 1.47 $"
__author__  = "H. Herb <hherb@gnumed.net>,\
			   K. Hilbert <Karsten.Hilbert@gmx.net>,\
			   I. Haywood <i.haywood@ugrad.unimelb.edu.au>"
__license__ = 'GPL (details at http://www.gnu.org)'

import os.path, os, sys, logging


import wx


from Gnumed.pycommon import gmGuiBroker, gmI18N, gmDispatcher, gmCfg
from Gnumed.wxpython import gmPlugin, gmTopPanel, gmGuiHelpers
from Gnumed.business import gmPerson, gmSurgery


_log = logging.getLogger('gm.ui')
_log.info(__version__)
#==============================================================================
# finding the visible page from a notebook page: self.GetParent.GetCurrentPage == self
class cHorstSpaceLayoutMgr(wx.Panel):
	"""GnuMed inner-frame layout manager.

	This implements a Horst-space notebook-only
	"inner-frame" layout manager.
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
			name = 'HorstSpace.LayoutMgrPnl'
		)
		# notebook
		self.nb = wx.Notebook (
			parent=self,
			id = -1,
			size = wx.Size(320,240),
			style = wx.NB_BOTTOM
		)
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
		self.main_szr = wx.BoxSizer(wx.VERTICAL)
		self.main_szr.Add(self.top_panel, 0, wx.EXPAND)
		self.main_szr.Add(self.nb, 1, wx.EXPAND)
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
		self.nb.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self._on_notebook_page_changing)
		# - notebook page has been changed
		self.nb.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self._on_notebook_page_changed)
		# - popup menu on right click in notebook
		wx.EVT_RIGHT_UP(self.nb, self._on_right_click)

		gmDispatcher.connect(self._on_post_patient_selection, u'post_patient_selection')
	#----------------------------------------------
	def __load_plugins(self):
		# get plugin list
		plugin_list = gmPlugin.GetPluginLoadList (
			option = 'horstspace.notebook.plugin_load_order',
			plugin_dir = 'gui',
			defaults = ['gmProviderInboxPlugin']
		)

		nr_plugins = len(plugin_list)
		wx.BeginBusyCursor()

		#  set up a progress bar
		progress_bar = gmPlugin.cLoadProgressBar(nr_plugins)

		#  and load them
		prev_plugin = ""
		first_plugin = None
		plugin = None
		result = -1
		for idx in range(nr_plugins):
			curr_plugin = plugin_list[idx]
			progress_bar.Update(result, curr_plugin)
			try:
				plugin = gmPlugin.instantiate_plugin('gui', curr_plugin)
				if plugin:
					plugin.register()
					result = 1
				else:
					_log.error("plugin [%s] not loaded, see errors above", curr_plugin)
					result = 1
			except:
				_log.exception('failed to load plugin %s', curr_plugin)
				result = 0

			if first_plugin is None:
				first_plugin = plugin
			prev_plugin = curr_plugin

		progress_bar.Destroy()
		wx.EndBusyCursor()

		# force-refresh first notebook page
		page = self.nb.GetPage(0)
		page.Refresh()

		return True
	#----------------------------------------------
	# external callbacks
	#----------------------------------------------
	def _on_post_patient_selection(self, **kwargs):
		db_cfg = gmCfg.cCfgSQL()
		default_plugin = db_cfg.get2 (
			option = u'patient_search.plugin_to_raise_after_search',
			workplace = gmSurgery.gmCurrentPractice().active_workplace,
			bias = u'user',
			default = u'gmEMRBrowserPlugin'
		)
		wx.CallAfter(gmDispatcher.send, signal = 'display_widget', name = default_plugin)
	#----------------------------------------------
	def _on_notebook_page_changing(self, event):
		"""Called before notebook page change is processed."""

		_log.debug('just before switching notebook tabs')

		self.__new_page_already_checked = False

		self.__id_nb_page_before_switch = self.nb.GetSelection()
		self.__id_evt_page_before_switch = event.GetOldSelection()
		__id_evt_page_after_switch = event.GetSelection()

		_log.debug('event.GetOldSelection()=%s* -> event.GetSelection()=%s', self.__id_evt_page_before_switch, __id_evt_page_after_switch)

		if self.__id_evt_page_before_switch != self.__id_nb_page_before_switch:
			_log.debug('the following two should match but do not:')
			_log.debug(' event.GetOldSelection(): %s', self.__id_evt_page_before_switch)
			_log.debug(' notebook.GetSelection(): %s', self.__id_nb_page_before_switch)

		# can we check the target page ?
		if __id_evt_page_after_switch == self.__id_evt_page_before_switch:
			# no, so complain
			# (the docs say that on Windows GetSelection() returns the
			#  old page ID, eg. the same value GetOldSelection() returns)
			_log.debug('this system is: sys: [%s] wx: [%s]', sys.platform, wx.Platform)
			_log.debug('it seems to be one of those platforms that have no clue which notebook page they are switching to')
			_log.debug('(Windows is documented to return the old page from both evt.GetOldSelection() and evt.GetSelection())')
			_log.debug('current notebook page : %s', self.__id_nb_page_before_switch)
			_log.debug('source page from event: %s', self.__id_evt_page_before_switch)
			_log.debug('target page from event: %s', __id_evt_page_after_switch)
			_log.info('cannot check whether notebook page change needs to be vetoed')
			# but let's do a basic check anyways
			pat = gmPerson.gmCurrentPatient()
			if not pat.connected:
				gmDispatcher.send(signal = 'statustext', msg =_('Cannot change notebook tabs. No active patient.'))
				event.Veto()
				return
			# that test passed, so let's hope things are fine
			event.Allow()		# redundant ?
			event.Skip()
			return

		# check target page
		new_page = self.__gb['horstspace.notebook.pages'][__id_evt_page_after_switch]
		if not new_page.can_receive_focus():
			_log.debug('veto()ing page change')
			event.Veto()
			return

		# everything seems fine so switch
		self.__new_page_already_checked = True
		event.Allow()		# redundant ?
		event.Skip()
		return
	#----------------------------------------------
	def _on_notebook_page_changed(self, event):
		"""Called when notebook page changes."""

		_log.debug('just after switching notebook tabs')

		id_evt_page_before_switch = event.GetOldSelection()
		id_evt_page_after_switch = event.GetSelection()
		id_nb_page_after_switch = self.nb.GetSelection()

		_log.debug('event.GetOldSelection()=%s -> event.GetSelection()=%s*', id_evt_page_before_switch, id_evt_page_after_switch)

		if self.__id_nb_page_before_switch != id_evt_page_before_switch:
			_log.debug('those two really *should* match:')
			_log.debug(' wx.Notebook.GetSelection() (before switch) : %s' % self.__id_nb_page_before_switch)
			_log.debug(' EVT_NOTEBOOK_PAGE_CHANGED.GetOldSelection(): %s' % id_evt_page_before_switch)

		new_page = self.__gb['horstspace.notebook.pages'][id_evt_page_after_switch]

		# well-behaving wxPython port ?
		if self.__new_page_already_checked:
			new_page.receive_focus()
			# activate toolbar of new page
#			self.__gb['horstspace.top_panel'].ShowBar(new_page.__class__.__name__)
			self.__new_page_already_checked = False
			event.Skip()
			return

		# no, complain
		_log.debug('target page not checked for focussability yet')
		_log.debug('EVT_NOTEBOOK_PAGE_CHANGED.GetOldSelection(): %s' % id_evt_page_before_switch)
		_log.debug('EVT_NOTEBOOK_PAGE_CHANGED.GetSelection()   : %s' % id_evt_page_after_switch)
		_log.debug('wx.Notebook.GetSelection() (after switch)  : %s' % id_nb_page_after_switch)

		# check the new page just for good measure
		if new_page.can_receive_focus():
			_log.debug('we are lucky: new page *can* receive focus')
			new_page.receive_focus()
			# activate toolbar of new page
#			self.__gb['horstspace.top_panel'].ShowBar(new_page.__class__.__name__)
			event.Skip()
			return

		_log.warning('new page cannot receive focus but too late for veto')
		event.Skip()
		return
	#----------------------------------------------
	def _on_right_click(self, evt):
		evt.Skip()
		return

		load_menu = wx.Menu()
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
			nid = wx.NewId()
			load_menu.AppendItem(wx.MenuItem(load_menu, nid, plugin.name()))
			wx.EVT_MENU(load_menu, nid, plugin.on_load)
			any_loadable = 1
		# make menus
		menu = wx.Menu()
		ID_LOAD = wx.NewId()
		ID_DROP = wx.NewId()
		if any_loadable:
			menu.AppendMenu(ID_LOAD, _('add plugin ...'), load_menu)
		plugins = self.guibroker['horstspace.notebook.gui']
		raised_plugin = plugins[self.nb.GetSelection()].name()
		menu.AppendItem(wx.MenuItem(menu, ID_DROP, "drop [%s]" % raised_plugin))
		wx.EVT_MENU (menu, ID_DROP, self._on_drop_plugin)
		self.PopupMenu(menu, evt.GetPosition())
		menu.Destroy()
		evt.Skip()
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
	wx.InitAllImageHandlers()
	pgbar = gmPluginLoadProgressBar(3)

#==============================================================================
