#############################################################################
#
# gmPlugin - base classes for GNUMed's plugin architecture
# ---------------------------------------------------------------------------
#
# @author: Dr. Horst Herb
# @copyright: author
# @license: GPL (details at http://www.gnu.org)
# @dependencies: nil
# @change log:
#	08.03.2002 hherb first draft, untested
#
# @TODO: Almost everything
############################################################################
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/python-common/Attic/gmPlugin.py,v $
# $Id: gmPlugin.py,v 1.41 2003-02-09 11:52:28 ncq Exp $
__version__ = "$Revision: 1.41 $"
__author__ = "H.Herb, I.Haywood, K.Hilbert"

import os, sys, re, traceback, cPickle, zlib

from wxPython.wx import *

import gmExceptions, gmGuiBroker, gmPG, gmShadow, gmLog, gmCfg
import EditAreaHandler
_log = gmLog.gmDefLog
_log.Log(gmLog.lData, __version__)
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
		return ''
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
	def Shown (self):
		"""Called whenever this module is shown onscreen.
		"""
		pass
	#-----------------------------------------------------
	def register(self):
		"""call set_widget_reference AFTER the widget is 
		created so it can be gotten from the global 
		guiBroker object later."""
		
		
		self.gb['modules.%s' % self.set][self.name()] = self
		_log.Log(gmLog.lInfo, "loaded plugin %s/%s" % (self.set, self.name() ))
	#-----------------------------------------------------
	def unregister(self):
		del self.gb['modules.%s' % self.set][self.name ()]
		_log.Log(gmLog.lInfo, "unloaded plugin %s/%s" % (self.set, self.name()))

	def set_widget_reference(self, widget):
		"""puts a reference to widget in a map keyed as 'widgets'
		in the guiBroker. The widget's map key is it's class name"""
		_log.Log(gmLog.lInfo, "\n ********** gmBasePlugin.set_widget_reference() for %s\n" % self.__class__.__name__)
		_log.Log(gmLog.lInfo,  " ***** widget class = %s \n" %widget.__class__.__name__ )
		_log.Log(gmLog.lInfo, "attributes = %s \n**** \n"%widget.__dict__ )
		

		if not self.gb.has_key( 'widgets'):
			self.gb['widgets'] = {}
		
		self.gb['widgets'][widget.__class__.__name__] = widget
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
		self.nb.AddPage (widget, self.name ())
		widget.Show (1)

		# place ourselves in the main toolbar
		# FIXED: this should be optional
		# IH: No. Pages that don't want a toolbar must install a blank one
		# otherwise the previous page's toolbar would be visible
		self.tbm = self.gb['main.toolbar']
		tb = self.tbm.AddBar (self.name ())
		self.gb['toolbar.%s' % self.name ()] = tb
		self.DoToolbar (tb, widget)
		tb.Realize ()

		# and put ourselves into the menu structure if so
		if self.MenuInfo ():
			menuset, menuname = self.MenuInfo ()
			menu = self.gb['main.%smenu' % menuset]
			self.menu_id = wxNewId ()
			menu.Append (self.menu_id, menuname, self.name ())
			EVT_MENU (self.gb['main.frame'], self.menu_id, self.OnMenu)
		# so notebook can find this widget
		self.gb['main.notebook.numbers'].append (self)

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
		self.tbm.DeleteBar (self.name ())
		# correct the number-plugin dictionary
		nbns = self.gb['main.notebook.numbers']
		nb_no = nbns.index (self)
		del nbns[nb_no]
		# delete notebook page
		nb = self.gb['main.notebook']
		nb.DeletePage (nb_no)
		
	#-----------------------------------------------------	
	def Raise (self):
		print "self.nb.SetSelection (nb_no)"
		nbns = self.gb['main.notebook.numbers']
		nb_no = nbns.index (self)
		self.nb.SetSelection (nb_no)
		self.tbm.ShowBar (self.name ())
	#-----------------------------------------------------
	def OnMenu (self, event):
		self.Raise ()
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
		self.mwm = self.gb['patient.manager']
		if gmGuiBroker.config['main.shadow']:
			shadow = gmShadow.Shadow (self.mwm, -1)
			widget = self.GetWidget (shadow)
			shadow.SetContents (widget)
			self.mwm.RegisterLeftSide (self.name (), shadow)
		else:
			widget = self.GetWidget (self.mwm)
			self.mwm.RegisterLeftSide (self.name (), self.GetWidget (self.mwm))
		icon = self.GetIcon ()
		if icon is not None:
			tb2 = self.gb['toolbar.Patient']
			#tb2.AddSeparator()
			self.tool_id = wxNewId ()
			tool1 = tb2.AddTool(
				self.tool_id,
				icon,
				shortHelpString = self.name()
			)
			EVT_TOOL (tb2, self.tool_id, self.OnTool)
		menuname = self.name ()
		menu = self.gb['patient.submenu']
		self.menu_id = wxNewId ()
		menu.Append (self.menu_id, menuname)
		EVT_MENU (self.gb['main.frame'], self.menu_id, self.OnTool)
		self.set_widget_reference(widget)
	#-----------------------------------------------------        
	def OnTool (self, event):
		self.Shown ()
		self.mwm.Display (self.name ())
		# reduntant as cannot access toolbar unless mwm raised
		#self.gb['modules.gui']['Patient'].Raise ()
	#-----------------------------------------------------
	def Raise (self):
		self.gb['modules.gui']['Patient'].Raise ()
		self.mwm.Display (self.name ())
	#-----------------------------------------------------
	def unregister (self):
		wxBasePlugin.unregister (self)
		self.mwm.Unregister (self.name ())
		menu = self.gb['main.submenu']
		menu.Delete (menu_id)
		if self.GetIcon () is not None:
			tb2 = self.gb['toolbar.Patient Window']
			tb2.DeleteTool (self.tool_id)
		del self.gb['modules.patient'][self.name ()]
	#-----------------------------------------------------

#------------------------------------------------------------------
def InstPlugin (aPackage, plugin_name, guibroker = None, dbbroker = None):
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
		guibroker = gmGuiBroker.GuiBroker ()
	if dbbroker is None:
		dbbroker = gmPG.ConnectionPool ()

	# bean counting ! -> loaded plugins
	if not ('modules.%s' % aPackage) in guibroker.keylist ():
		guibroker['modules.%s' % aPackage] = {}

	try:
		# use __import__() so we can dynamically calculate the module name
		mod_from_pkg = __import__ ("%s.%s" % (aPackage, plugin_name))
		# find name of class of plugin (must be the same as the plugin module filename)
		# 1) get module name
		plugin_module_name = mod_from_pkg.__dict__[plugin_name]
		# 2) get class name
		plugin_class = plugin_module_name.__dict__[plugin_name]
	except:
		_log.LogException ('Cannot __import__() module "%s.%s".' % (aPackage, plugin_name), sys.exc_info(), fatal=0)
		return None

	if not issubclass (plugin_class, wxBasePlugin):
		_log.Log(gmLog.lErr, "class %s is not a subclass of wxBasePlugin" % plugin_name)
		return None

	_log.Log(gmLog.lInfo, "instantiating plugin %s" % plugin_name)
	try:
		plugin = plugin_class(set = aPackage, guibroker = guibroker, dbbroker = dbbroker)
	except:
		_log.LogException ('Cannot open module "%s.%s".' % (aPackage, plugin_name), sys.exc_info(), fatal=0)
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
	gb = gmGuiBroker.GuiBroker()

	# connect to database
	db = gmPG.ConnectionPool()
	conn = db.GetConnection(service = "default")
	dbcfg = gmCfg.cCfgSQL(
		aConn = conn,
		aDBAPI = gmPG.dbapi
	)


	# search database
	# for this user on this machine	
	p_list = dbcfg.get(
		machine = gb['workplace_name'],
		option = 'plugin load order',
		cookie = str(set)
	)
	if p_list is not None:
		db.ReleaseConnection(service = "default")
		return p_list

	# for this user on default machine
	p_list = dbcfg.get(
		option = 'plugin load order',
		cookie = str(set)
	)
	if p_list is not None:
		rwconn = db.GetConnection(service = "default", readonly = 0)
		dbcfg.set(
			machine = gb['workplace_name'],
			option = 'plugin load order',
			value = p_list,
			cookie = str(set),
			aRWConn = rwconn
		)
		rwconn.close()
		db.ReleaseConnection(service = "default")
		return p_list

	# for default user on this machine
	p_list = dbcfg.get(
		machine = gb['workplace_name'],
		user = '__default__',
		option = 'plugin load order',
		cookie = str(set)
	)
	if p_list is not None:
		rwconn = db.GetConnection(service = "default", readonly = 0)
		dbcfg.set(
			machine = gb['workplace_name'],
			option = 'plugin load order',
			value = p_list,
			cookie = str(set),
			aRWConn = rwconn
		)
		rwconn.close()
		db.ReleaseConnection(service = "default")
		return p_list

	# for default user on default machine
	p_list = dbcfg.get(
		user = '__default__',
		option = 'plugin load order',
		cookie = str(set)
	)
	if p_list is not None:
		rwconn = db.GetConnection(service = "default", readonly = 0)
		dbcfg.set(
			machine = gb['workplace_name'],
			option = 'plugin load order',
			value = p_list,
			cookie = str(set),
			aRWConn = rwconn
		)
		rwconn.close()
		db.ReleaseConnection(service = "default")
		return p_list

	db.ReleaseConnection(service = "default")
	_log.Log(gmLog.lWarn, "No plugin load order stored in database. Trying local config file.")

	# search in plugin directory
	#  FIXME: in the future we might ask the backend where plugins are
	plugin_conf_name = os.path.join(gb['gnumed_dir'], 'wxpython', set, 'plugins.conf')
	fCfg = None
	try:
		fCfg = gmCfg.cCfgFile(aFile = plugin_conf_name)
	except:
		_log.LogException("Can't load plugin load order config file.", sys.exc_info(), fatal=0)

	# load from file
	if fCfg is not None:
		p_list = fCfg.get("plugins", "load order")

	# parse directory directly
	if p_list is None:
		_log.Log(gmLog.lWarn, "Config file [%s] does not contain the plugin load order !" % plugin_conf_name)
		_log.Log(gmLog.lData, "*** Scanning plugin directory directly.")

		files = os.listdir(os.path.join(gb['gnumed_dir'], 'wxpython', set))

		_log.Log(gmLog.lData, "the Path from set=%s parameter gnumed_dir=%s is %s"% ( set, gb['gnumed_dir'], os.path.join(gb['gnumed_dir'], 'wxpython', set) ) )

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
			machine = gb['workplace_name'],
			user = '__default__',
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
# Revision 1.41  2003-02-09 11:52:28  ncq
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
