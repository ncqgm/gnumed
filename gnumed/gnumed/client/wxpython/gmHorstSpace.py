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
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmHorstSpace.py,v $
# $Id: gmHorstSpace.py,v 1.40 2007-10-08 12:50:54 ncq Exp $
__version__ = "$Revision: 1.40 $"
__author__  = "H. Herb <hherb@gnumed.net>,\
			   K. Hilbert <Karsten.Hilbert@gmx.net>,\
			   I. Haywood <i.haywood@ugrad.unimelb.edu.au>"
__license__ = 'GPL (details at http://www.gnu.org)'

import os.path, os, sys


import wx


from Gnumed.pycommon import gmGuiBroker, gmI18N, gmLog, gmDispatcher, gmSignals, gmCfg
from Gnumed.wxpython import gmPlugin, gmTopPanel, gmGuiHelpers
from Gnumed.business import gmPerson, gmSurgery


_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)

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

		gmDispatcher.connect(self._on_post_patient_selection, gmSignals.post_patient_selection())
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
					_log.Log (gmLog.lErr, "plugin [%s] not loaded, see errors above" % curr_plugin)
					result = 1
			except:
				_log.LogException('failed to load plugin %s' % curr_plugin, sys.exc_info(), verbose = 0)
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
		gmDispatcher.send(signal = 'display_widget', name = default_plugin)
	#----------------------------------------------
	def _on_notebook_page_changing(self, event):
		"""Called before notebook page change is processed."""

		_log.Log(gmLog.lData, 'just before switching notebook tabs')

		self.__new_page_already_checked = False

		self.__id_nb_page_before_switch = self.nb.GetSelection()
		self.__id_evt_page_before_switch = event.GetOldSelection()
		__id_evt_page_after_switch = event.GetSelection()

		_log.Log(gmLog.lData, 'event: [%s]* -> [%s]' % (self.__id_evt_page_before_switch, __id_evt_page_after_switch))

		if self.__id_evt_page_before_switch != self.__id_nb_page_before_switch:
			_log.Log(gmLog.lData, 'those two really *should* match:')
			_log.Log(gmLog.lData, 'old page from event  : %s' % self.__id_evt_page_before_switch)
			_log.Log(gmLog.lData, 'current notebook page: %s' % self.__id_nb_page_before_switch)

		# can we check the target page ?
		if __id_evt_page_after_switch == self.__id_evt_page_before_switch:
			# no, so complain
			# (the docs say that on Windows GetSelection() returns the
			#  old page ID, eg. the same value GetOldSelection() returns)
			_log.Log(gmLog.lData, 'Windows is documented to return the old page from both evt.GetOldSelection() and evt.GetSelection()')
			_log.Log(gmLog.lData, 'this system is: sys: [%s] wx: [%s]' % (sys.platform, wx.Platform))
			_log.Log(gmLog.lData, 'it seems to be one of those platforms that have no clue which notebook page they are switching to')
			_log.Log(gmLog.lData, 'current notebook page: %s' % self.__id_nb_page_before_switch)
			_log.Log(gmLog.lData, 'old page from event  : %s' % self.__id_evt_page_before_switch)
			_log.Log(gmLog.lData, 'new page from event  : %s' % __id_evt_page_after_switch)
			_log.Log(gmLog.lInfo, 'cannot check whether notebook page change needs to be vetoed')
			# but let's do a basic check anyways
			pat = gmPerson.gmCurrentPatient()
			if not pat.is_connected():
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
			_log.Log(gmLog.lData, 'veto()ing page change')
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

		_log.Log(gmLog.lData, 'just after switching notebook tabs')

		id_evt_page_before_switch = event.GetOldSelection()
		id_evt_page_after_switch = event.GetSelection()
		id_nb_page_after_switch = self.nb.GetSelection()

		_log.Log(gmLog.lData, 'event: [%s] -> [%s]*' % (id_evt_page_before_switch, id_evt_page_after_switch))

		if self.__id_nb_page_before_switch != id_evt_page_before_switch:
			_log.Log(gmLog.lData, 'those two really *should* match:')
			_log.Log(gmLog.lData, 'notebook page before switch          : %s' % self.__id_nb_page_before_switch)
			_log.Log(gmLog.lData, 'previous page from PAGE_CHANGED event: %s' % id_evt_page_before_switch)

		new_page = self.__gb['horstspace.notebook.pages'][id_evt_page_after_switch]

		# well-behaving wxPython port ?
		if self.__new_page_already_checked:
			new_page.receive_focus()
			# activate toolbar of new page
			self.__gb['horstspace.top_panel'].ShowBar(new_page.__class__.__name__)
			self.__new_page_already_checked = False
			event.Skip()
			return

		# no, complain
		_log.Log(gmLog.lData, 'target page not checked for focussability yet')
		_log.Log(gmLog.lData, 'old page from event  : %s' % id_evt_page_before_switch)
		_log.Log(gmLog.lData, 'new page from event  : %s' % id_evt_page_after_switch)
		_log.Log(gmLog.lData, 'current notebook page: %s' % id_nb_page_after_switch)

		# check the new page just for good measure
		if new_page.can_receive_focus():
			_log.Log(gmLog.lData, 'we are lucky: new page *can* receive focus')
			new_page.receive_focus()
			# activate toolbar of new page
			self.__gb['horstspace.top_panel'].ShowBar(new_page.__class__.__name__)
			event.Skip()
			return

		_log.Log(gmLog.lWarn, 'new page cannot receive focus but too late for veto')
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
# $Log: gmHorstSpace.py,v $
# Revision 1.40  2007-10-08 12:50:54  ncq
# - active_workplace now in gmPractice()
#
# Revision 1.39  2007/08/28 14:18:13  ncq
# - no more gm_statustext()
#
# Revision 1.38  2007/08/12 00:09:07  ncq
# - no more gmSignals.py
#
# Revision 1.37  2007/02/17 14:13:11  ncq
# - gmPerson.gmCurrentProvider().workplace now property
#
# Revision 1.36  2007/02/15 14:57:49  ncq
# - cleanup
#
# Revision 1.35  2006/12/17 20:44:52  ncq
# - cleanup
#
# Revision 1.34  2006/11/24 10:01:31  ncq
# - gm_beep_statustext() -> gm_statustext()
#
# Revision 1.33  2006/11/07 00:34:16  ncq
# - cleanup
# - raise configured plugin after successful patient search
#
# Revision 1.32  2006/10/08 11:04:09  ncq
# - add sensible default for plugin load list
# - robustify __load_plugins() somewhat
#
# Revision 1.31  2006/06/18 21:55:22  ncq
# - better variable naming in page change handlers, again
#
# Revision 1.30  2006/06/18 13:24:27  ncq
# - use Bind() instead of event binding macros
# - improved page change logging, all to no avail
#
# Revision 1.29  2006/05/28 15:45:52  ncq
# - cleanup page activation code and reinit already_checked helper var
#
# Revision 1.28  2006/05/20 18:37:10  ncq
# - cleanup
#
# Revision 1.27  2006/05/15 13:36:49  ncq
# - cleanup
#
# Revision 1.26  2006/05/12 12:18:11  ncq
# - whoami -> whereami cleanup
# - use gmCurrentProvider()
#
# Revision 1.25  2006/05/10 13:09:57  ncq
# - improved error logging in notebook page switching
#
# Revision 1.24  2005/12/27 18:57:29  ncq
# - better document Syan's workaround
#
# Revision 1.23  2005/12/26 08:57:26  sjtan
#
# repaint may not be signalled on some platforms ( gtk ? ); repaint occurs if 1) the emrbrowser is the selected notebook page AND
# 2) the frame is re-sized.  This suggests repaint is best done on notebook page changed. This workaround goes to
# the demographic page on a new patient select - let's the user confirm they have selected the right patient; then when
# switch to emrbrowser, this signals data_reget. seems to work.
#
# Revision 1.22  2005/09/28 21:21:35  ncq
# - non-initialized variable plugin in plugin loading
# - wx2.6 fixing
#
# Revision 1.21  2005/09/28 15:57:48  ncq
# - a whole bunch of wx.Foo -> wx.Foo
#
# Revision 1.20  2005/09/27 20:44:59  ncq
# - wx.wx* -> wx.*
#
# Revision 1.19  2005/09/26 18:01:51  ncq
# - use proper way to import wx26 vs wx2.4
# - note: THIS WILL BREAK RUNNING THE CLIENT IN SOME PLACES
# - time for fixup
#
# Revision 1.18  2005/09/25 17:32:50  ncq
# - revert back to 2.4 wx import until compatible 2.6 method is found
#
# Revision 1.17  2005/09/25 01:00:47  ihaywood
# bugfixes
#
# remember 2.6 uses "import wx" not "from wxPython import wx"
# removed not null constraint on clin_encounter.rfe as has no value on instantiation
# client doesn't try to set clin_encounter.description as it doesn't exist anymore
#
# Revision 1.16  2005/09/24 09:17:29  ncq
# - some wx2.6 compatibility fixes
#
# Revision 1.15  2005/07/31 16:22:57  ncq
# - cleanup
#
# Revision 1.14  2005/07/23 22:03:08  shilbert
# - yet another typo
#
# Revision 1.13  2005/07/23 21:44:21  shilbert
# - silly typo
#
# Revision 1.12  2005/07/23 19:08:36  ncq
# - robust detection of lossy notebook tab switching wxPython code
#
# Revision 1.11  2005/07/21 16:21:01  ncq
# - log everything there is to know about changing notebook tabs,
#   debugging on Windows is in order
#
# Revision 1.10  2005/07/19 17:06:35  ncq
# - try again to make windows behave regarding notebook tab switching
#
# Revision 1.9  2005/07/18 20:47:41  ncq
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
