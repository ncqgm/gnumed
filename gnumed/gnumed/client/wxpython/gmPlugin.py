"""gmPlugin - base classes for GnuMed Horst space notebook plugins.

@copyright: author
"""
#==================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmPlugin.py,v $
# $Id: gmPlugin.py,v 1.62 2006-05-28 15:59:16 ncq Exp $
__version__ = "$Revision: 1.62 $"
__author__ = "H.Herb, I.Haywood, K.Hilbert"
__license__ = 'GPL (details at http://www.gnu.org)'

import os, sys, re

try:
	import wxversion
	import wx
except ImportError:
	from wxPython import wx

from Gnumed.pycommon import gmExceptions, gmGuiBroker, gmPG, gmLog, gmCfg, gmDispatcher, gmSignals
from Gnumed.wxpython import gmShadow
from Gnumed.pycommon.gmPyCompat import *
from Gnumed.business import gmPerson

_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)

#==============================================================================
class cLoadProgressBar (wx.ProgressDialog):
	def __init__(self, nr_plugins):
		wx.ProgressDialog.__init__(
			self,
			title = _("GNUmed: configuring [%s] (%s plugins)") % (gmPerson.gmCurrentProvider().get_workplace(), nr_plugins),
			message = _("loading list of plugins                               "),
			maximum = nr_plugins,
			parent = None,
			style = wx.PD_ELAPSED_TIME
			)
		# set window icon
		gb = gmGuiBroker.GuiBroker()
		png_fname = os.path.join(gb['gnumed_dir'], 'bitmaps', 'serpent.png')
		icon = wx.EmptyIcon()
		try:
			icon.LoadFile(png_fname, wx.BITMAP_TYPE_PNG)
		except:
			_log.Log(gmLog.lWarn, 'wx.Icon.LoadFile() not supported')
		self.SetIcon(icon)
		self.idx = 0
		self.nr_plugins = nr_plugins
		self.prev_plugin = ""

	def Update (self, result, plugin):
		if result == -1:
			result = ""
		elif result == 0:
			result = _("failed")
		else:
			result = _("success")
		wx.ProgressDialog.Update (self, 
				self.idx,
				_("previous: %s (%s)\ncurrent (%s/%s): %s") % (
					self.prev_plugin,
					result,
					(self.idx+1),
					self.nr_plugins,
					plugin))
		self.prev_plugin = plugin
		self.idx += 1
			
#==================================================================
# This is for NOTEBOOK plugins. Please write other base
# classes for other types of plugins.
#==================================================================
class cNotebookPlugin:
	"""Base class for plugins which provide a full notebook page.
	"""
	def __init__(self):
		self.gb = gmGuiBroker.GuiBroker()
		self._set = 'gui'
		self._widget = None
		self.__register_events()
	#-----------------------------------------------------
	# plugin load API
	#-----------------------------------------------------
	def register(self):
		"""Register ourselves with the main notebook widget."""

		_log.Log(gmLog.lInfo, "set: [%s] class: [%s] name: [%s]" % (self._set, self.__class__.__name__, self.name()))

		# create widget
		nb = self.gb['horstspace.notebook']
		widget = self.GetWidget(nb)
		# create toolbar
		top_panel = self.gb['horstspace.top_panel']
		tb = top_panel.CreateBar()
		self.populate_toolbar(tb, widget)
		tb.Realize()
		# create menu item
		menu_info = self.MenuInfo()

		# place bar in top panel
		# (pages that don't want a toolbar must install a blank one
		#  otherwise the previous page's toolbar would be visible)
		top_panel.AddBar(key=self.__class__.__name__, bar=tb)
		self.gb['toolbar.%s' % self.__class__.__name__] = tb
		# add ourselves to the main notebook
		nb.AddPage(widget, self.name())
		# and put ourselves into the menu structure if so
		if menu_info is not None:
			name_of_menu, menu_item_name = menu_info
			menu = self.gb['main.%smenu' % name_of_menu]
			self.menu_id = wx.NewId()
			# FIXME: this shouldn't be self.name() but rather self.menu_help_string()
			menu.Append (self.menu_id, menu_item_name, self.name())			# (id, item name, help string)
			wx.EVT_MENU (self.gb['main.frame'], self.menu_id, self._on_raise_by_menu)

		# so notebook can find this widget
		self.gb['horstspace.notebook.%s' % self._set][self.__class__.__name__] = self
		self.gb['horstspace.notebook.pages'].append(self)

		return True
	#-----------------------------------------------------
	def unregister(self):
		"""Remove ourselves."""
		del self.gb['horstspace.notebook.%s' % self._set][self.__class__.__name__]
		_log.Log(gmLog.lInfo, "plugin: [%s] (class: [%s]) set: [%s]" % (self.name(), self.__class__.__name__, self._set))

		# delete menu item
		menu_info = self.MenuInfo()
		if menu_info is not None:
			menu = self.gb['main.%smenu' % menu_info[0]]
			menu.Delete(self.menu_id)

		# delete toolbar
		top_panel = self.gb['main.top_panel']
		top_panel.DeleteBar(self.__class__.__name__)

		# correct the notebook page list
		nb_pages = self.gb['horstspace.notebook.pages']
		nb_page_num = nb_pages.index(self)
		del nb_pages[nb_page_num]

		# delete notebook page
		nb = self.gb['horstspace.notebook']
		nb.DeletePage(nb_page_num)
	#-----------------------------------------------------
	def name(self):
		return 'plugin %s' % self.__class__.__name__
	#-----------------------------------------------------
	def MenuInfo(self):
		"""Return tuple of (menuname, menuitem).

		None: no menu entry wanted
		"""
		return None
	#-----------------------------------------------------
	def populate_toolbar (self, tb, widget):
		"""Populates the toolbar for this widget.

		- tb is the toolbar to populate
		- widget is the widget returned by GetWidget()		# FIXME: is this really needed ?
		"""
		pass
	#-----------------------------------------------------
	# activation API
	#-----------------------------------------------------
	def can_receive_focus(self):
		"""Called when this plugin is *about to* receive focus.

		If None returned from here (or from overriders) the
		plugin activation will be veto()ed (if it can be).
		"""
		# FIXME: fail if locked
		return True
	#-----------------------------------------------------
	def receive_focus(self):
		"""We *are* receiving focus via wx.EVT_NotebookPageChanged.

		This can be used to populate the plugin widget on receiving focus.
		"""
		self._widget.repopulate_ui()
		return True
	#-----------------------------------------------------
	def _verify_patient_avail(self):
		"""Check for patient availability.

		- convenience method for your can_receive_focus() handlers
		"""
		# fail if no patient selected
		pat = gmPerson.gmCurrentPatient()
		if not pat.is_connected():
			# FIXME: people want an optional red backgound here
			self._set_status_txt(_('Cannot switch to [%s]: no patient selected') % self.name())
			wx.Bell()
			return None
		return 1
	#-----------------------------------------------------
	def _set_status_txt(self, txt):
		set_statustext = self.gb['main.statustext']
		set_statustext(txt)
		return 1
	#-----------------------------------------------------
	def Raise(self):
		"""Raise ourselves."""
		nb_pages = self.gb['horstspace.notebook.pages']
		plugin_page = nb_pages.index(self)
		nb = self.gb['horstspace.notebook']
		nb.SetSelection(plugin_page)
		return True
	#-----------------------------------------------------
	def _on_raise_by_menu(self, event):
		if not self.can_receive_focus():
			return False
		self.Raise()
		return True
	#-----------------------------------------------------
	def _on_raise_by_signal(self, **kwds):
		# does this signal concern us ?
		if kwds['name'] != self.__class__.__name__:
			return True
		return self._on_raise_by_menu(None)
	# -----------------------------------------------------
	# event handlers for the popup window
	def on_load (self, evt):
		# FIXME: talk to the configurator so we're loaded next time
		self.register()
		# FIXME: raise ?
	# -----------------------------------------------------
	def OnShow (self, evt):
		self.register() # register without changing configuration
	# -----------------------------------------------------
	def __register_events(self):
		gmDispatcher.connect(self._on_raise_by_signal, gmSignals.display_widget())
#==================================================================
class cPatientChange_PluginMixin:
	"""This mixin adds listening to patient change signals."""
	def __init__(self):
		gmDispatcher.connect(self._pre_patient_selection, gmSignals.pre_patient_selection())
		gmDispatcher.connect(self._post_patient_selection, gmSignals.post_patient_selection())
	# -----------------------------------------------------
	def _pre_patient_selection(self, **kwds):
		print "%s._pre_patient_selection() not implemented" % self.__class__.__name__
		print "should usually be used to commit unsaved data"
	# -----------------------------------------------------
	def _post_patient_selection(self, **kwds):
		print "%s._post_patient_selection() not implemented" % self.__class__.__name__
		print "should usually be used to initialize state"
#==================================================================
class cNotebookPluginOld(cNotebookPlugin):
	def __init__(self, set=None):
		print "%s: class cNotebookPluginOld used, please convert" % self.__class__.__name__
		cNotebookPlugin.__init__(self)
		# make sure there's a raised_plugin entry
		try:
			tmp = self.gb['main.notebook.raised_plugin']
		except KeyError:
			self.gb['main.notebook.raised_plugin'] = 'none'
	#-----------------------------------------------------
	def populate_with_data(self):
		_log.Log(gmLog.lInfo, '%s: outdated populate_with_data() missing' % self.__class__.__name__)
	#-----------------------------------------------------
	def receive_focus(self):
		"""We *are* receiving focus now."""
		self.gb['main.notebook.raised_plugin'] = self.__class__.__name__
		self.populate_with_data()
	#-----------------------------------------------------
	def Raise(self):
		"""Raise ourselves."""
		# already raised ?
		if self.gb['main.notebook.raised_plugin'] == self.__class__.__name__:
			return True
		cNotebookPlugin.Raise(self)
		return True

#==================================================================
# some convenience functions
#------------------------------------------------------------------
def raise_notebook_plugin(plugin_name = None):
	"""plugin_name is a plugin internal name"""
	print "gmPlugin.raise_notebook_plugin() deprecated, use <display_widget> signal instead"
	gb = gmGuiBroker.GuiBroker()
	try:
		plugin = gb['horstspace.notebook.gui'][plugin_name]
	except KeyError:
		_log.LogException("cannot raise [%s], plugin not available" % plugin_name, sys.exc_info(), verbose=0)
		return None
	if plugin.can_receive_focus():
		plugin.Raise()
		return True
	return False
#------------------------------------------------------------------
def __gm_import(module_name):
	"""Import a module.

	I am not sure *why* we need this. But the docs
	and Google say so. It's got something to do with
	package imports returning the toplevel package name."""
	try:
		mod = __import__(module_name)
	except ImportError:
		_log.LogException ('Cannot __import__() module [%s].' % module_name, sys.exc_info(), verbose=0)
		return None
	components = module_name.split('.')
	for component in components[1:]:
		mod = getattr(mod, component)
	return mod
#------------------------------------------------------------------
def instantiate_plugin(aPackage='xxxDEFAULTxxx', plugin_name='xxxDEFAULTxxx'):
	"""Instantiates a plugin object from a package directory, returning the object.

	NOTE: it does NOT call register() for you !!!!

	- "set" specifies the subdirectory in which to find the plugin
	- this knows nothing of databases, all it does is instantiate a named plugin

	There will be a general 'gui' directory for large GUI
	components: prescritions, etc., then several others for more
	specific types: export/import filters, crypto algorithms
	guibroker, dbbroker are broker objects provided
	defaults are the default set of plugins to be loaded

	FIXME: we should inform the user about failing plugins
	"""
	# we do need brokers, else we are useless
	gb = gmGuiBroker.GuiBroker()

	# bean counting ! -> loaded plugins
	if not ('horstspace.notebook.%s' % aPackage) in gb.keylist():
		gb['horstspace.notebook.%s' % aPackage] = {}
	if not 'horstspace.notebook.pages' in gb.keylist():
		gb['horstspace.notebook.pages'] = []

	module_from_package = __gm_import('Gnumed.wxpython.%s.%s' % (aPackage, plugin_name))
	# find name of class of plugin (must be the same as the plugin module filename)
	plugin_class = module_from_package.__dict__[plugin_name]

	if not issubclass(plugin_class, cNotebookPlugin):
		_log.Log(gmLog.lErr, "[%s] not a subclass of cNotebookPlugin" % plugin_name)
		return None

	_log.Log(gmLog.lInfo, plugin_name)
	try:
		plugin = plugin_class()
	except:
		_log.LogException ('Cannot open module "%s.%s".' % (aPackage, plugin_name), sys.exc_info(), verbose=0)
		return None

	return plugin
#------------------------------------------------------------------
def GetPluginLoadList(option, plugin_dir = '', defaults = None):
	"""Get a list of plugins to load.

	1) from database
	2) from list of defaults
	3) if 2 is None, from source directory (then stored in database)

	FIXME: look at gmRichardSpace to see how to load plugins
	FIXME: NOT from files in directories (important for py2exe)
	"""
	curr_workplace = gmPerson.gmCurrentProvider().get_workplace()

	p_list, match = gmCfg.getDBParam (
		workplace = curr_workplace,
		option = option
	)

	if p_list is not None:
		# found plugin load list for this user/this workplace
		if match == 'CURRENT_USER_CURRENT_WORKPLACE':
			return p_list
		# all other user/workplace pairings:
		# store plugin list for the current user/current workplace
		gmCfg.setDBParam(
			workplace = curr_workplace,
			option = option,
			value = p_list
		)
		return p_list

	if defaults is None:
		_log.Log(gmLog.lInfo, "plugin load order not found in DB, scanning directory and storing in DB")

		# parse plugin directory
		gb = gmGuiBroker.GuiBroker()
		candidates = []
		# find candidate plugins directories
		for path in sys.path:
			# make sure it's a system path, not a user defined one
			if path.find(sys.prefix) == -1:
				continue
			if path.find('site-packages') == -1:
				continue
			candidates.append(path)
		if len(candidates) == 0:
			_log.Log(gmLog.lErr, 'no candidate directories to scan for plugins found among the following')
			_log.Log(gmLog.lErr, str(sys.path))
			return []
		# among them find (the) one holding plugins
		search_path = None
		for candidate in candidates:
			tmp = os.path.join(candidate, 'Gnumed', 'wxpython', plugin_dir)
			if os.path.exists(tmp):
				search_path = tmp
				break
		if search_path is None:
			_log.Log(gmLog.lErr, 'unable to find any candidate directory matching [$candidate/wxpython/%s/]' % plugin_dir)
			_log.Log(gmLog.lErr, 'candidates: %s' % str(candidates))
			return []
		# now scan it
		files = os.listdir(search_path)
		_log.Log(gmLog.lData, "plugin set: %s, gnumed_dir: %s" % (plugin_dir, gb['gnumed_dir']))
		_log.Log(gmLog.lInfo, "scanning plugin directory [%s]" % search_path)
		_log.Log(gmLog.lData, "files found: %s" % str(files))
		p_list = []
		for file in files:
			if (re.compile ('.+\.py$').match(file)) and (file != '__init__.py'):
				p_list.append(file[:-3])
		if (len(p_list) == 0):
			_log.Log(gmLog.lErr, 'cannot find plugins by scanning plugin directory ?!?')
			return None
	else:
		p_list = defaults

	# store for current user/current workplace
	gmCfg.setDBParam(
		workplace = curr_workplace,
		option = option,
		value = p_list
	)

	_log.Log(gmLog.lData, "plugin load list stored: %s" % str(p_list))
	return p_list
#------------------------------------------------------------------
def UnloadPlugin (set, name):
	"""
	Unloads the named plugin
	"""
	gb = gmGuiBroker.GuiBroker()
	plugin = gb['horstspace.notebook.%s' % set][name]
	plugin.unregister()
#==================================================================
# Main
#------------------------------------------------------------------
if __name__ == '__main__':
	print "please write a unit test"

#==================================================================
# $Log: gmPlugin.py,v $
# Revision 1.62  2006-05-28 15:59:16  ncq
# - cleanup
# - receive_focus() now calls self._widget.repopulate_ui()
#
# Revision 1.61  2006/05/20 18:54:49  ncq
# - provide default receive_focus() and document it
# - remove get_instance()
#
# Revision 1.60  2006/05/15 13:38:52  ncq
# - remove "set" argument from notebook plugin __init__
# - cPatientChange_PluginMixin
# 	- inherit from this to listen to patient change signals
# - add depreciation warning to raise_notebook_plugin()
#
# Revision 1.59  2006/05/15 07:05:07  ncq
# - must import gmPerson now
#
# Revision 1.58  2006/05/14 21:44:22  ncq
# - add get_workplace() to gmPerson.gmCurrentProvider and make use thereof
# - remove use of gmWhoAmI.py
#
# Revision 1.57  2006/05/12 22:01:02  ncq
# - add _on_raise_by_signal()
# - connect to "display_widget" signal
#
# Revision 1.56  2006/05/12 12:18:11  ncq
# - whoami -> whereami cleanup
# - use gmCurrentProvider()
#
# Revision 1.55  2005/12/26 08:57:26  sjtan
#
# repaint may not be signalled on some platforms ( gtk ? ); repaint occurs if 1) the emrbrowser is the selected notebook page AND
# 2) the frame is re-sized.  This suggests repaint is best done on notebook page changed. This workaround goes to
# the demographic page on a new patient select - let's the user confirm they have selected the right patient; then when
# switch to emrbrowser, this signals data_reget. seems to work.
#
# Revision 1.54  2005/11/01 08:51:43  ncq
# - wx.python -> wx.python
#
# Revision 1.53  2005/09/28 21:27:30  ncq
# - a lot of wx2.6-ification
#
# Revision 1.52  2005/09/28 15:57:48  ncq
# - a whole bunch of wx.Foo -> wx.Foo
#
# Revision 1.51  2005/09/26 18:01:51  ncq
# - use proper way to import wx26 vs wx2.4
# - note: THIS WILL BREAK RUNNING THE CLIENT IN SOME PLACES
# - time for fixup
#
# Revision 1.50  2005/08/14 16:20:44  ncq
# - missing "Gnumed" directory
#
# Revision 1.49  2005/08/14 16:03:00  ncq
# - improved logging in case of error
#
# Revision 1.48  2005/08/14 15:00:08  ncq
# - fix plugin directory scanning
#
# Revision 1.47  2005/07/21 16:21:29  ncq
# - remove debugging cruft
#
# Revision 1.46  2005/07/18 17:13:38  ncq
# - improved import works but... better do what the docs tell us to do
#
# Revision 1.45  2005/07/18 16:48:26  ncq
# - hopefully improve __import__ of modules
#
# Revision 1.44  2005/07/16 22:49:52  ncq
# - cleanup
#
# Revision 1.43  2005/06/30 10:11:51  cfmoro
# String corrections
#
# Revision 1.42  2005/06/12 22:17:24  ncq
# - raise by menu only if activatable
#
# Revision 1.41  2005/03/29 07:28:20  ncq
# - add FIXME on plugin scanning
#
# Revision 1.40  2005/02/01 10:16:07  ihaywood
# refactoring of gmDemographicRecord and follow-on changes as discussed.
#
# gmTopPanel moves to gmHorstSpace
# gmRichardSpace added -- example code at present, haven't even run it myself
# (waiting on some icon .pngs from Richard)
#
# Revision 1.39  2005/01/31 10:37:26  ncq
# - gmPatient.py -> gmPerson.py
#
# Revision 1.38  2004/11/21 20:56:14  ncq
# - remove cruft
#
# Revision 1.37  2004/10/14 12:14:51  ncq
# - rearrange register() internally so we won't end up with
#   half-baked but registered plugins
#
# Revision 1.36  2004/09/13 19:27:27  ncq
# - load "horstspace.notebook.plugin_load_order" instead of
#   "plugin load order" with cookie "gui"
#
# Revision 1.35  2004/09/13 09:25:46  ncq
# - fix plugin raise code
#
# Revision 1.34  2004/09/06 22:23:03  ncq
# - properly use setDBParam()
#
# Revision 1.33  2004/08/20 13:34:48  ncq
# - getFirstMatchingDBSet() -> getDBParam()
#
# Revision 1.32  2004/08/04 17:16:02  ncq
# - wxNotebookPlugin -> cNotebookPlugin
# - derive cNotebookPluginOld from cNotebookPlugin
# - make cNotebookPluginOld warn on use and implement old
#   explicit "main.notebook.raised_plugin"/ReceiveFocus behaviour
# - ReceiveFocus() -> receive_focus()
#
# Revision 1.31  2004/07/24 17:21:49  ncq
# - some cleanup, also re from wxPython import wx
# - factored out Horst space layout manager into it's own
#   wx.Panel child class
# - subsequently renamed
# 	'main.notebook.plugins' -> 'horstspace.notebook.pages'
# 	'modules.gui' -> 'horstspace.notebook.gui' (to be renamed horstspace.notebook.plugins later)
# - adapt to said changes
#
# Revision 1.30  2004/07/19 16:17:55  ncq
# - missing GuiBroker reference added
#
# Revision 1.29  2004/07/19 13:54:25  ncq
# - simplify getPluginLoadList()
#
# Revision 1.28  2004/07/19 11:50:43  ncq
# - cfg: what used to be called "machine" really is "workplace", so fix
#
# Revision 1.27  2004/07/18 19:51:42  ncq
# - better logging
#
# Revision 1.26  2004/07/15 20:37:56  ncq
# - I really believe we should keep plugin code nicely separated
# - go back to plain notebook plugins, not super-plugins again
#
# Revision 1.24  2004/07/15 06:15:55  ncq
# - fixed typo patch -> path
#
# Revision 1.23  2004/07/15 05:17:43  ncq
# - better/correct logging in GetPluginLoadList()
#
# Revision 1.22  2004/06/26 23:09:22  ncq
# - better comments
#
# Revision 1.21  2004/06/25 14:39:35  ncq
# - make right-click runtime load/drop of plugins work again
#
# Revision 1.20  2004/06/25 13:28:00  ncq
# - logically separate notebook and clinical window plugins completely
#
# Revision 1.19  2004/06/25 12:51:23  ncq
# - InstPlugin() -> instantiate_plugin()
#
# Revision 1.18  2004/06/13 22:14:39  ncq
# - extensive cleanup/comments
# - deprecate self.internal_name in favour of self.__class__.__name__
# - introduce gb['main.notebook.raised_plugin']
# - add populate_with_data()
# - DoToolbar() -> populate_toolbar()
# - remove set_widget_reference()
#
# Revision 1.17  2004/03/10 13:57:45  ncq
# - unconditionally do shadow
#
# Revision 1.16  2004/03/10 12:56:01  ihaywood
# fixed sudden loss of main.shadow
# more work on referrals,
#
# Revision 1.15  2004/03/04 19:23:24  ncq
# - moved here from pycommon
#
# Revision 1.1  2004/02/25 09:30:13  ncq
# - moved here from python-common
#
# Revision 1.68  2004/02/12 23:54:39  ncq
# - add wx.Bell to can_receive_focus()
# - move raise_plugin out of class gmPlugin
#
# Revision 1.67  2004/01/17 10:37:24  ncq
# - don't ShowBar() in Raise() as GuiMain.OnNotebookPageChanged()
#   takes care of that
#
# Revision 1.66  2004/01/17 09:59:02  ncq
# - enable Raise() to raise arbitrary plugins
#
# Revision 1.65  2004/01/06 23:44:40  ncq
# - __default__ -> xxxDEFAULTxxx
#
# Revision 1.64  2003/12/29 16:33:23  uid66147
# - use whoami.get_workplace()/gmPG.run_commit()
#
# Revision 1.63  2003/11/18 23:29:57  ncq
# - remove duplicate Version line
#
# Revision 1.62  2003/11/18 19:06:26  hinnef
# gmTmpPatient->gmPatient, again
#
# Revision 1.61  2003/11/17 10:56:37  sjtan
#
# synced and commiting.
#
# Revision 1.60  2003/11/09 14:26:41  ncq
# - if we have set_status_txt() do use it, too
#
# Revision 1.59  2003/11/08 10:48:36  shilbert
# - added convenience function _set_status_txt()
#
# Revision 1.58  2003/10/26 01:38:06  ncq
# - gmTmpPatient -> gmPatient, cleanup
#
# Revision 1.57  2003/09/24 10:32:54  ncq
# - whitespace cleanup
#
# Revision 1.56  2003/09/03 17:31:05  hinnef
# cleanup in GetPluginLoadList, make use of gmWhoAmI
#
# Revision 1.55  2003/07/21 20:57:42  ncq
# - cleanup
#
# Revision 1.54  2003/06/29 14:20:45  ncq
# - added TODO item
#
# Revision 1.53  2003/06/26 21:35:23  ncq
# - fatal->verbose
#
# Revision 1.52  2003/06/19 15:26:02  ncq
# - cleanup bits
# - add can_receive_focus() helper to wxNotebookPlugin()
# - in default can_receive_focus() veto() plugin activation on "no patient selected"
#
# Revision 1.51  2003/04/28 12:03:15  ncq
# - introduced internal_name() helper, adapted to use thereof
# - leaner logging
#
# Revision 1.50  2003/04/20 15:38:50  ncq
# - clean out some excessive logging
#
# Revision 1.49  2003/04/09 13:06:03  ncq
# - some cleanup
#
# Revision 1.48  2003/04/05 01:09:03  ncq
# - forgot that one in the big patient -> clinical clean up
#
# Revision 1.47  2003/02/24 12:35:55  ncq
# - renamed some function local variables to further my understanding of the code
#
# Revision 1.46  2003/02/17 16:18:29  ncq
# - fix whitespace on comments
#
# Revision 1.45  2003/02/13 12:58:05  sjtan
#
# remove unneded import.
#
# Revision 1.44  2003/02/11 18:23:39  ncq
# - removed unneeded import
#
# Revision 1.43  2003/02/11 12:27:07  sjtan
#
# suspect this is not the preferred way to get a handle on the plugin. Probably from guiBroker?
#
# Revision 1.42  2003/02/09 20:00:06  ncq
# - on notebook plugins rename Shown() to ReceiveFocus() as that's what this does, not only display itself
#
# Revision 1.41  2003/02/09 11:52:28  ncq
# - just one more silly cvs keyword
#
# Revision 1.40  2003/02/09 09:41:57  sjtan
#
# clean up new code, make it less intrusive.
#
# Revision 1.39  2003/02/07 12:47:15  sjtan
#
# using gmGuiBroker for more dynamic handler loading. (e.g. can use subclassed instances of EditAreaHandler classes).
# ~
#
# Revision 1.38  2003/02/07 08:16:16  ncq
# - some cosmetics
#
# Revision 1.37  2003/02/07 05:08:08  sjtan
#
# added few lines to hook in the handler classes from EditAreaHandler.
# EditAreaHandler was generated with editarea_gen_listener in wxPython directory.
#
# Revision 1.36  2003/01/16 14:45:04  ncq
# - debianized
#
# Revision 1.35  2003/01/16 09:18:11  ncq
# - cleanup
#
# Revision 1.34  2003/01/12 17:30:19  ncq
# - consistently return None if no plugins found by GetPluginLoadList()
#
# Revision 1.33  2003/01/12 01:45:12  ncq
# - typo, "IS None" not "== None"
#
# Revision 1.32  2003/01/11 22:03:30  hinnef
# removed gmConf
#
# Revision 1.31  2003/01/06 12:53:26  ncq
# - some cleanup bits
#
# Revision 1.30  2003/01/06 04:52:55  ihaywood
# resurrected gmDemographics.py
#
# Revision 1.29  2003/01/05 10:00:38  ncq
# - better comments
# - implement database plugin configuration loading/storing
#
# Revision 1.28  2003/01/04 07:43:55  ihaywood
# Popup menus on notebook tabs
#
# Revision 1.27  2002/11/13 09:14:17  ncq
# - document a few more todo's but don't do them before OSHCA
#
# Revision 1.26  2002/11/12 23:03:25  hherb
# further changes towards customization of plugin loading order
#
# Revision 1.25  2002/11/12 20:30:10  hherb
# Uses an optional config file in each plugin directory determining the order plugins are loaded as well as which plugins are loaded
#
# Revision 1.24  2002/09/26 13:10:43  ncq
# - silly ommitance
#
# Revision 1.23  2002/09/26 13:08:51  ncq
# - log version on import
# - TODO -> FIXME
#
# Revision 1.22  2002/09/09 00:50:28  ncq
# - return success or failure on LoadPlugin()
#
# @change log:
#	08.03.2002 hherb first draft, untested
