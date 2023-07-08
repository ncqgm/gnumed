"""gmPlugin - base classes for GNUmed Horst space notebook plugins.

@copyright: author
"""
#==================================================================
__author__ = "H.Herb, I.Haywood, K.Hilbert"
__license__ = 'GPL v2 or later (details at http://www.gnu.org)'

import os
import sys
import glob
import logging


import wx


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmExceptions
from Gnumed.pycommon import gmGuiBroker
from Gnumed.pycommon import gmCfg
from Gnumed.pycommon import gmCfg2
from Gnumed.pycommon import gmDispatcher
from Gnumed.pycommon import gmTools

from Gnumed.business import gmPerson
from Gnumed.business import gmPraxis


_cfg = gmCfg2.gmCfgData()

_log = logging.getLogger('gm.ui')

#==============================================================================
class cLoadProgressBar (wx.ProgressDialog):
	def __init__(self, nr_plugins):
		wx.ProgressDialog.__init__(
			self,
			title = _("GNUmed: configuring [%s] (%s plugins)") % (gmPraxis.gmCurrentPraxisBranch().active_workplace, nr_plugins),
			message = _("loading list of plugins                               "),
			maximum = nr_plugins,
			parent = None,
			style = wx.PD_ELAPSED_TIME
			)
		self.SetIcon(gmTools.get_icon(wx = wx))
		self.idx = 0
		self.nr_plugins = nr_plugins
		self.prev_plugin = ""
	#----------------------------------------------------------
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

		_log.info("set: [%s] class: [%s] name: [%s]" % (self._set, self.__class__.__name__, self.name()))

		# create widget
		nb = self.gb['horstspace.notebook']
		widget = self.GetWidget(nb)

		# add ourselves to the main notebook
		nb.AddPage(widget, self.name())

		# so notebook can find this widget
		self.gb['horstspace.notebook.%s' % self._set][self.__class__.__name__] = self
		self.gb['horstspace.notebook.pages'].append(self)

		# and put ourselves into the menu structure
		menu_info = self.MenuInfo()
		if menu_info is None:
			# register with direct access menu only
			gmDispatcher.send(signal = 'plugin_loaded', plugin_name = self.name(), class_name = self.__class__.__name__)
		else:
			name_of_menu, menu_item_name = menu_info
			gmDispatcher.send (
				signal = 'plugin_loaded',
				plugin_name = menu_item_name,
				class_name = self.__class__.__name__,
				menu_name = name_of_menu,
				menu_item_name = menu_item_name,
				# FIXME: this shouldn't be self.name() but rather self.menu_help_string()
				menu_help_string = self.name()
			)

		return True

	#-----------------------------------------------------
	def unregister(self):
		"""Remove ourselves."""
		del self.gb['horstspace.notebook.%s' % self._set][self.__class__.__name__]
		_log.info("plugin: [%s] (class: [%s]) set: [%s]" % (self.name(), self.__class__.__name__, self._set))

		# delete menu item
		menu_info = self.MenuInfo()
		if menu_info is not None:
			menu = self.gb['main.%smenu' % menu_info[0]]
			menu.Delete(self.menu_id)

		# correct the notebook page list
		nb_pages = self.gb['horstspace.notebook.pages']
		nb_page_num = nb_pages.index(self)
		del nb_pages[nb_page_num]

		# delete notebook page
		nb = self.gb['horstspace.notebook']
		nb.DeletePage(nb_page_num)

	#-----------------------------------------------------
	def name(self):
		return 'plugin <%s>' % self.__class__.__name__

	#-----------------------------------------------------
	def MenuInfo(self):
		"""Return tuple of (menuname, menuitem).

		None: no menu entry wanted
		"""
		return None

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
		if hasattr(self._widget, 'repopulate_ui'):
			self._widget.repopulate_ui()
		# else apparently it doesn't need it
		return True

	#-----------------------------------------------------
	def _verify_patient_avail(self):
		"""Check for patient availability.

		- convenience method for your can_receive_focus() handlers
		"""
		# fail if no patient selected
		pat = gmPerson.gmCurrentPatient()
		if not pat.connected:
			# FIXME: people want an optional red backgound here
			gmDispatcher.send('statustext', msg = _('Cannot switch to [%s]: no patient selected') % self.name())
			return None
		return 1

	#-----------------------------------------------------
	def Raise(self):
		"""Raise ourselves."""
		nb_pages = self.gb['horstspace.notebook.pages']
		try:
			plugin_page = nb_pages.index(self)
		except ValueError:
			# we may not have been loaded properly, so are not in the list ...
			_log.error('plugin not loaded: %s', self)
			return False

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
		if kwds['name'] not in [self.__class__.__name__, self.name()]:
			return False
		return self._on_raise_by_menu(None)

	# -----------------------------------------------------
	# event handlers for the popup window
	def on_load(self, evt):
		# FIXME: talk to the configurator so we're loaded next time
		self.register()
		# FIXME: raise ?

	# -----------------------------------------------------
	def OnShow(self, evt):
		self.register() # register without changing configuration

	# -----------------------------------------------------
	def __register_events(self):
		gmDispatcher.connect(signal = 'display_widget', receiver = self._on_raise_by_signal)

#==================================================================
class cPatientChange_PluginMixin:
	"""This mixin adds listening to patient change signals."""
	def __init__(self):
		gmDispatcher.connect(self._pre_patient_unselection, 'pre_patient_unselection')
		gmDispatcher.connect(self._on_current_patient_unset, 'current_patient_unset')
		gmDispatcher.connect(self._post_patient_selection, 'post_patient_selection')

	# -----------------------------------------------------
	def _pre_patient_unselection(self, **kwds):
#		print "%s._pre_patient_unselection() not implemented" % self.__class__.__name__
#		print "should usually be used to commit unsaved data"
		pass

	# -----------------------------------------------------
	def _on_current_patient_unset(self, **kwds):
#		print "%s._on_current_patient_unset() not implemented" % self.__class__.__name__
#		print "should usually be used to empty the UI"
		pass

	# -----------------------------------------------------
	def _post_patient_selection(self, **kwds):
		print("%s._post_patient_selection() not implemented" % self.__class__.__name__)
		print("should usually be used to schedule reloading the UI")

#==================================================================
# some convenience functions
#------------------------------------------------------------------
def __gm_import(module_name):
	"""Import a module.

	I am not sure *why* we need this. But the docs
	and Google say so. It's got something to do with
	package imports returning the toplevel package name."""
	try:
		mod = __import__(module_name)
	except ImportError:
		_log.exception ('Cannot __import__() module [%s].' % module_name)
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
		_log.error("[%s] not a subclass of cNotebookPlugin" % plugin_name)
		return None

	_log.info(plugin_name)
	try:
		plugin = plugin_class()
	except Exception:
		_log.exception('Cannot open module "%s.%s".' % (aPackage, plugin_name))
		return None

	return plugin

#------------------------------------------------------------------
def get_installed_plugins(plugin_dir=''):
	"""Looks for installed plugins in the filesystem.

	The first directory in sys.path which contains a wxpython/gui/
	is considered the one -- because that's where the import will
	get it from.
	"""
	_log.debug('searching installed plugins')
	search_path = None
	candidates = sys.path[:]
	candidates.append(gmTools.gmPaths().local_base_dir)
	for candidate in candidates:
		candidate = os.path.join(candidate, 'Gnumed', 'wxpython', plugin_dir)
		_log.debug(candidate)
		if os.path.exists(candidate):
			search_path = candidate
			break
		_log.debug('not found')

	if search_path is None:
		_log.error('unable to find any directory matching [%s]', os.path.join('${CANDIDATE}', 'Gnumed', 'wxpython', plugin_dir))
		_log.error('candidates: %s', str(candidates))
		# read from config file
		_log.info('trying to read list of installed plugins from config files')
		plugins = _cfg.get (
			group = 'client',
			option = 'installed plugins',
			source_order = [
				('system', 'extend'),
				('user', 'extend'),
				('workbase', 'extend'),
				('explicit', 'extend')
			]
		)
		if plugins is None:
			_log.debug('no plugins found in config files')
			return []
		_log.debug("plugins found: %s" % str(plugins))
		return plugins

	_log.info("scanning plugin directory [%s]" % search_path)

	files = glob.glob(os.path.join(search_path, 'gm*.py'))
	plugins = []
	for f in files:
		path, fname = os.path.split(f)
		mod_name, ext = os.path.splitext(fname)
		plugins.append(mod_name)

	_log.debug("plugins found: %s" % str(plugins))

	return plugins

#------------------------------------------------------------------
def GetPluginLoadList(option, plugin_dir = '', defaults = None, workplace=None):
	"""Get a list of plugins to load.

	1) from database if option is not None
	2) from list of defaults
	3) if 2 is None, from source directory (then stored in database)

	FIXME: NOT from files in directories (important for py2exe)
	"""
	if workplace == 'System Fallback':
		return ['gmProviderInboxPlugin', 'gmDataMiningPlugin']

	if workplace is None:
		workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace

	p_list = None

	if option is not None:
		dbcfg = gmCfg.cCfgSQL()
		p_list = dbcfg.get2 (
			option = option,
			workplace = workplace,
			bias = 'workplace',
			default = defaults
		)

	if p_list is not None:
		return p_list

	if defaults is None:
		p_list = get_installed_plugins(plugin_dir = plugin_dir)
		if (len(p_list) == 0):
			_log.error('cannot find plugins by scanning plugin directory ?!?')
			return defaults
	else:
		p_list = defaults

	# store for current user/current workplace
	dbcfg.set (
		option = option,
		value = p_list,
		workplace = workplace
	)

	_log.debug("plugin load list stored: %s" % str(p_list))
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

	if len(sys.argv) > 1 and sys.argv[1] == 'test':
		print(get_installed_plugins('gui'))
