"""gmPlugin - base classes for GNUMed's plugin architecture.

@copyright: author
@license: GPL (details at http://www.gnu.org)
"""
############################################################################
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/python-common/Attic/gmPlugin.py,v $
# $Id: gmPlugin.py,v 1.67 2004-01-17 10:37:24 ncq Exp $
__version__ = "$Revision: 1.67 $"
__author__ = "H.Herb, I.Haywood, K.Hilbert"

import os, sys, re, cPickle, zlib

from wxPython.wx import *

import gmExceptions, gmGuiBroker, gmPG, gmShadow, gmLog, gmCfg, gmPatient
_log = gmLog.gmDefLog
_log.Log(gmLog.lData, __version__)

import gmWhoAmI
_whoami = gmWhoAmI.cWhoAmI()

#------------------------------------------------------------------
class gmPlugin:
	"""base class for all gnumed plugins"""
	#-----------------------------------------------------
	def provides ():
		"""
		Returns a list of services that the plugin provides
		"""
		return []
	#-----------------------------------------------------
	def requires ():
		"""
		Requires a list of services that must be registered
		before this plugin is registered. The configuration
		tool must check these and make sure the load order
		satisfies the plugins' requirements
		"""
		return []
	#-----------------------------------------------------
	def description ():
		"""Returns a brief description of the plugin.
		"""
		pass
	#-----------------------------------------------------
	def name (self):
		return 'plugin %s' % self.__class__.__name__
	#-----------------------------------------------------
	def internal_name (self):
		"""Used for referencing a plugin by name."""
		return self.__class__.__name__
#------------------------------------------------------------------
class wxBasePlugin (gmPlugin):
	"""
	base class for all plugins providing wxPython widgets.
	Plugins must have a class descending of this class in their file, which MUST HAVE THE SAME NAME AS THE FILE.
	The file must be in a directory which is loaded by LoadPluginSet (gui/ for the moment, others may be added for different plugin types)
	
	"""
	# NOTE: I anticipate that all plugins will in fact be derived
	# from this class. Without the brokers a plugin is useless (IH)
	def __init__(self, set='', guibroker=None, callbackbroker=None, dbbroker=None, params=None):
		self.gb = guibroker
		self.cb = callbackbroker
		self.db = dbbroker
		if self.gb is None:
			self.gb = gmGuiBroker.GuiBroker ()
		if self.db is None:
			self.db = gmPG.ConnectionPool ()
		self.set = set
	#-----------------------------------------------------
	def GetIcon (self):
		"""Return icon representing page on the toolbar.

		This is the default behaviour. GetIconData should return
		pickled, compressed and escaped string with the icon data.

		If you want to change the behaviour (because you want to load
		plugin icons from overseas via a satellite link or something
		you need to override this function in your plugin (class).

		Using this standard code also allows us to only import cPickle
		and zlib here and not in each and every plugin module which
		should speed up plugin load time :-)
		"""
		# FIXME: load from config which plugin we want
		# which_icon is a cookie stored on the backend by a config manager,
		# it tells the plugin which icon to return data for,
		which_icon = None
		icon_data = self.GetIconData(which_icon)
		if icon_data is None:
			return None
		else:
			return wxBitmapFromXPMData(cPickle.loads(zlib.decompress(icon_data)))
	#-----------------------------------------------------
	def GetIconData(self, anIconID = None):
		# FIXME: in overriding methods need to be very careful about the
		# type of the icon ID since if we read it back from the database we
		# may not know what type it was
		return None
	#-----------------------------------------------------
	def GetWidget (self, parent):
		"""
		Return the widget to display. Usually called from
		register(). The instance returned is the
		active object for event handling purposes.
		"""
		raise gmExceptions.PureVirtualFunction()
	#-----------------------------------------------------
	def MenuInfo (self):
		"""Return tuple of (menuname, menuitem).

		menuname can be
			"tools",
			"view",
			"help",
			"file"

		If you return "None" no entry will be placed
		in any menu.
		"""
		raise gmExceptions.PureVirtualFunction()
	#-----------------------------------------------------
	def Raise (self):
		"""Raises this plugin to the top level if not visible.
		"""
		raise gmExceptions.PureVirtualFunction ()
	#-----------------------------------------------------
	def ReceiveFocus(self):
		"""Called whenever this module receives focus and is thus shown onscreen.
		"""
		pass
	#-----------------------------------------------------
	def register(self):
		"""call set_widget_reference AFTER the widget is 
		created so it can be gotten from the global 
		guiBroker object later."""
	
		self.gb['modules.%s' % self.set][self.internal_name()] = self
		_log.Log(gmLog.lInfo, "plugin: [%s] (class: [%s]) set: [%s]" % (self.name(), self.internal_name(), self.set))
	#-----------------------------------------------------
	def unregister(self):
		del self.gb['modules.%s' % self.set][self.internal_name()]
		_log.Log(gmLog.lInfo, "plugin: [%s] (class: [%s]) set: [%s]" % (self.name(), self.internal_name(), self.set))
	#-----------------------------------------------------
	def set_widget_reference(self, widget):
		"""puts a reference to widget in a map keyed as 'widgets'
		in the guiBroker. The widget's map key is it's class name"""
		_log.Log(gmLog.lData, "plugin class [%s], widget class [%s]" % (self.__class__.__name__, widget.__class__.__name__))

		if not self.gb.has_key( 'widgets'):
			self.gb['widgets'] = {}
		
		self.gb['widgets'][widget.__class__.__name__] = widget
		widget.plugin = self
		return

#------------------------------------------------------------------
class wxNotebookPlugin (wxBasePlugin):
	"""Base plugin for plugins which provide a 'big page'.

	Either whole screen, or notebook if it exists
	"""	
	def register (self):
		"""Register ourselves with the main notebook widget."""
		wxBasePlugin.register (self)
		# add ourselves to the main notebook
		self.nb = self.gb['main.notebook']
		#nb_no = self.nb.GetPageCount ()
		widget = self.GetWidget (self.nb)
		self.nb.AddPage (widget, self.name())
		widget.Show (1)

		# place ourselves in the main toolbar
		# Pages that don't want a toolbar must install a blank one
		# otherwise the previous page's toolbar would be visible
		self.tb_main = self.gb['main.toolbar']
		tb = self.tb_main.AddBar(self.internal_name())
		self.gb['toolbar.%s' % self.internal_name ()] = tb
		self.DoToolbar (tb, widget)
		tb.Realize()
		
		# and put ourselves into the menu structure if so
		if self.MenuInfo() is not None:
			name_of_menu, menu_item_name = self.MenuInfo()
			menu = self.gb['main.%smenu' % name_of_menu]
			self.menu_id = wxNewId()
			# FIXME: this shouldn't be self.name() but rather self.menu_help_string()
			menu.Append (self.menu_id, menu_item_name, self.name())			# (id, item name, help string)
			EVT_MENU (self.gb['main.frame'], self.menu_id, self.OnMenu)

		# so notebook can find this widget
		self.gb['main.notebook.plugins'].append(self)

		# so event handlers can get at this widget
		self.set_widget_reference(widget)
	#-----------------------------------------------------
	def unregister (self):
		"""Remove ourselves."""
		wxBasePlugin.unregister (self)
		# delete menu item
		if self.MenuInfo ():
			menu = self.gb['main.%smenu' % self.MenuInfo ()[0]]
			menu.Delete (self.menu_id)
		# delete toolbar
		self.tb_main.DeleteBar (self.internal_name())
		# correct the number-plugin dictionary
		nbns = self.gb['main.notebook.plugins']
		nb_no = nbns.index (self)
		del nbns[nb_no]
		# delete notebook page
		nb = self.gb['main.notebook']
		nb.DeletePage (nb_no)
	#-----------------------------------------------------
	def can_receive_focus(self):
		"""Called when this plugin is about to receive focus.

		If None returned from here (or from overriders) the
		plugin activation will be veto()ed.
		"""
		# FIXME: fail if locked
		return 1
	#-----------------------------------------------------
	def _verify_patient_avail(self):
		"""Check for patient availability.

		- convenience method for your can_receive_focus() handlers
		"""
		# fail if no patient selected
		pat = gmPatient.gmCurrentPatient()
		if not pat.is_connected():
			# FIXME: people want an optional beep and an optional red backgound here
			self._set_status_txt(_('Cannot switch to [%s]: no patient selected') % self.name())
			return None
		return 1
	#-----------------------------------------------------
	def _set_status_txt(self, txt):
		set_statustext = self.gb['main.statustext']
		set_statustext(txt)
		return 1
	#-----------------------------------------------------
	def Raise (self, plugin_name = None):
		"""plugin_name is a plugin internal name
		"""
		if plugin_name is None:
			plugin_name = self.internal_name()
		try:
			plugin = self.gb['modules.gui'][plugin_name]
		except KeyError:
			_log.LogException("Cannot raise [%s], plugin not available" % plugin_name(), sys.exc_info(), verbose=0)
			return (None, _('Cannot activate plugin [%s]. It is not loaded.') % plugin.name())
		plugin_list = self.gb['main.notebook.plugins']
		plugin_idx = plugin_list.index(plugin)
		self.nb.SetSelection (plugin_idx)
		return (1, '')
	#-----------------------------------------------------
	def OnMenu (self, event):
		self.Raise()
	#-----------------------------------------------------
	def GetNotebookNumber (self):
		return self.nb_no
	#----------------------------------------------------
	def DoToolbar (self, tb, widget):
		"""
		sets up the toolbar for this widget.
		tb is the toolbar
		widget is the widget returned by GetWidget () for connecting events
		"""
		pass
	# -----------------------------------------------------
	# event handlers for the popup window
	def OnLoad (self, evt):
		# FIXME: talk to the configurator so we're loaded next time
		self.register ()
	# =----------------------------------------------------
	def OnShow (self, evt):
		self.register () # register without changing configuration
		
#------------------------------------------------------------------
class wxPatientPlugin (wxBasePlugin):
	"""
	A 'small page', sits inside the patient view, with the side visible
	"""
	def register (self):
		wxBasePlugin.register (self)
		self.mwm = self.gb['clinical.manager']
		if gmGuiBroker.config['main.shadow']:
			shadow = gmShadow.Shadow (self.mwm, -1)
			widget = self.GetWidget (shadow)
			shadow.SetContents (widget)
			self.mwm.RegisterLeftSide (self.internal_name(), shadow)
		else:
			widget = self.GetWidget (self.mwm)
			self.mwm.RegisterLeftSide (self.internal_name(), self.GetWidget (self.mwm))
		icon = self.GetIcon ()
		if icon is not None:
			tb2 = self.gb['toolbar.%s' % 'gmClinicalWindowManager']
			#tb2.AddSeparator()
			self.tool_id = wxNewId ()
			tool1 = tb2.AddTool(
				self.tool_id,
				icon,
				shortHelpString = self.name()
			)
			EVT_TOOL (tb2, self.tool_id, self.OnTool)
		menuname = self.name ()
		menu = self.gb['clinical.submenu']
		self.menu_id = wxNewId ()
		menu.Append (self.menu_id, menuname)
		EVT_MENU (self.gb['main.frame'], self.menu_id, self.OnTool)
		self.set_widget_reference(widget)
	#-----------------------------------------------------        
	def OnTool (self, event):
		self.ReceiveFocus()
		self.mwm.Display (self.internal_name())
		# redundant as cannot access toolbar unless mwm raised
		#self.gb['modules.gui']['Patient'].Raise ()
	#-----------------------------------------------------
	def Raise (self):
		self.gb['modules.gui']['Patient'].Raise()
		self.mwm.Display (self.internal_name())
	#-----------------------------------------------------
	def unregister (self):
		wxBasePlugin.unregister (self)
		self.mwm.Unregister (self.internal_name())
		menu = self.gb['main.submenu']
		menu.Delete (menu_id)
		if self.GetIcon () is not None:
			tb2 = self.gb['toolbar.%s' % 'gmClinicalWindowManager']
			tb2.DeleteTool (self.tool_id)
		del self.gb['modules.patient'][self.internal_name()]
	#-----------------------------------------------------
	def Shown(self):
		"""Called whenever this module receives focus and is thus shown onscreen.
		"""
		pass
#------------------------------------------------------------------
def InstPlugin (aPackage, plugin_name, guibroker = None):
	"""Instantiates a plugin object from a package directory, returning the object.

	NOTE: it does NOT call register() for you !!!!

	- "set" specifies the subdirectory in which to find the plugin
	- this knows nothing of databases, all it does is load a named plugin

	There will be a general 'gui' directory for large GUI
	components: prescritions, etc., then several others for more
	specific types: export/import filters, crypto algorithms
	guibroker, dbbroker are broker objects provided
	defaults are the default set of plugins to be loaded

	FIXME: we should inform the user about failing plugins
	"""
	# we do need brokers, else we are useless
	if guibroker is None:
		guibroker = gmGuiBroker.GuiBroker()
	dbbroker = gmPG.ConnectionPool()

	# bean counting ! -> loaded plugins
	if not ('modules.%s' % aPackage) in guibroker.keylist():
		guibroker['modules.%s' % aPackage] = {}

	try:
		# use __import__() so we can dynamically calculate the module name
		mod_from_pkg = __import__ ("%s.%s" % (aPackage, plugin_name))
		# find name of class of plugin (must be the same as the plugin module filename)
		# 1) get module name
		plugin_module_name = mod_from_pkg.__dict__[plugin_name]
		# 2) get class name
		plugin_class = plugin_module_name.__dict__[plugin_name]
	except ImportError:
		_log.LogException ('Cannot __import__() module "%s.%s".' % (aPackage, plugin_name), sys.exc_info(), verbose=0)
		return None

	if not issubclass (plugin_class, wxBasePlugin):
		_log.Log(gmLog.lErr, "class %s is not a subclass of wxBasePlugin" % plugin_name)
		return None

	_log.Log(gmLog.lInfo, "instantiating plugin %s" % plugin_name)
	try:
		plugin = plugin_class(set = aPackage, guibroker = guibroker, dbbroker = dbbroker)
	except:
		_log.LogException ('Cannot open module "%s.%s".' % (aPackage, plugin_name), sys.exc_info(), verbose=0)
		return None

	return plugin
#------------------------------------------------------------------
def GetPluginLoadList(set):
	"""Get a list of plugins to load.

	1) look in database
	2) look into source directory
	 a) check for plugins.conf
	 b) scan directly
	 c) store in database
	"""

	currentMachine = _whoami.get_workplace()

	p_list,match = gmCfg.getFirstMatchingDBSet(
		machine = currentMachine,
		cookie = str(set),
		option = 'plugin load order'
	)

	# get connection for possible later use
	gb = gmGuiBroker.GuiBroker()
	db = gmPG.ConnectionPool()
	conn = db.GetConnection(service = "default")
	dbcfg = gmCfg.cCfgSQL(
		aConn = conn,
		aDBAPI = gmPG.dbapi
	)

	# check result
	if p_list is not None:
		# if found for this user on this machine
		if match == 'CURRENT_USER_CURRENT_MACHINE':
			# we have already a plugin list stored for this
			# user/machine combination
			db.ReleaseConnection(service = "default")
			return p_list
		else: # all other cases of user/machine pairing
			# store the plugin list found for the current user
			# on the current machine
			rwconn = db.GetConnection(service = "default", readonly = 0)
			dbcfg.set(
				machine = currentMachine,
				option = 'plugin load order',
				value = p_list,
				cookie = str(set),
				aRWConn = rwconn
			)
			rwconn.close()
			db.ReleaseConnection(service = "default")
			return p_list

	_log.Log(gmLog.lWarn, "No plugin load order stored in database. Trying local config file.")

	# search in plugin directory
	# FIXME: in the future we might ask the backend where plugins are
	plugin_conf_name = os.path.join(gb['gnumed_dir'], 'wxpython', set, 'plugins.conf')
	try:
		fCfg = gmCfg.cCfgFile(aFile = plugin_conf_name)
	except:
		_log.LogException("Can't load plugin load order config file.", sys.exc_info(), verbose=0)
		fCfg = None

	# load from file
	if fCfg is not None:
		p_list = fCfg.get("plugins", "load order")

	# parse directory directly
	if p_list is None:
		_log.Log(gmLog.lWarn, "Config file [%s] does not contain the plugin load order !" % plugin_conf_name)
		_log.Log(gmLog.lData, "*** Scanning plugin directory directly.")

		files = os.listdir(os.path.join(gb['gnumed_dir'], 'wxpython', set))

		_log.Log(gmLog.lData, "the path from set=%s parameter gnumed_dir=%s is %s"% ( set, gb['gnumed_dir'], os.path.join(gb['gnumed_dir'], 'wxpython', set) ) )

		_log.Log(gmLog.lData, "returned this file list %s" % ("\n".join(files)))
		p_list = []
		for file in files:
			if (re.compile ('.+\.py$').match(file)) and (file != '__init__.py'):
				p_list.append (file[:-3])

	if (len(p_list) > 0):
		# set for default user on this machine
		_log.Log(gmLog.lInfo, "Storing default plugin load order in database.")
		rwconn = db.GetConnection(service = "default", readonly = 0)
		dbcfg.set(
			machine = currentMachine,
			user = 'xxxDEFAULTxxx',
			option = 'plugin load order',
			value = p_list,
			cookie = str(set),
			aRWConn = rwconn
		)
		rwconn.close()
	else:
		p_list = None

	_log.Log(gmLog.lData, "*** THESE ARE THE PLUGINS FROM gmPlugin.GetPluginList")
	_log.Log(gmLog.lData, "%s" % "\n *** ".join(p_list))
	db.ReleaseConnection(service = "default")
	return p_list
#------------------------------------------------------------------
def UnloadPlugin (set, name):
	"""
	Unloads the named plugin
	"""
	gb = gmGuiBroker.GuiBroker ()
	plugin = gb['modules.%s' % set][name]
	plugin.unregister ()
#==================================================================
# Main
#------------------------------------------------------------------


#==================================================================
# $Log: gmPlugin.py,v $
# Revision 1.67  2004-01-17 10:37:24  ncq
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
