#!/usr/bin/env python
"""
A connector framework showing how to online drive a
slave GNUmed client via the XML-RPC interface.

The base class simply raises the plugin that is set in
the configuration file. If you want your derivative class
to do smarter things you need to override:

	cBaseConnector.run_script()
"""

#==================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/connectors/gm_ctl_client.py,v $
# $Id: gm_ctl_client.py,v 1.5 2007-10-09 09:55:44 ncq Exp $
__version__ = '$Revision: 1.5 $'
__author__ = 'Karsten Hilbert <Karsten.Hilbert@gmx.net>'
__license__ = 'GPL'


import sys, time, xmlrpclib, socket, time, os


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmCfg, gmExceptions, gmI18N, gmLog, gmCLI, gmNull
from Gnumed.wxpython import gmGuiHelpers


_log = gmLog.gmDefLog
_cfg = gmCfg.gmDefCfgFile

_log.Log(gmLog.lInfo, __version__)
#==================================================================
class cBaseConnector:

	def __init__(self):
		# sanity check
		if isinstance(_cfg, gmNull.cNull):
			_log.Log(gmLog.lErr, 'cannot run without config file')
			raise gmExceptions.ConstructorError, _("Cannot find config file. Option syntax: --conf-file=<file>")
		self.__conn_auth = 0
		self.__unlock_auth = 0
	#--------------------------------------------------------------
	def connect(self):
		# connect to GNUmed instance
		port = _cfg.get('GNUmed instance', 'port')
		self.__gm_server = xmlrpclib.ServerProxy('http://localhost:%s' % int(port))

		try:
			_log.Log(gmLog.lInfo, 'GNUmed slave XML-RPC server version: %s' % self.__gm_server.version())
		except socket.error, e:
			# FIXME: differentiate between already-attached and not-there
			_log.LogException('cannot attach to GNUmed instance at http://localhost:%s: %s' % (port, e))
			# try starting GNUmed
			# - no use trying to start GNUmed if wx cannot be imported
			import wx
			startup_cmd = _cfg.get('GNUmed instance', 'startup command')
			if startup_cmd is None:
				_log.Log(gmLog.lErr, 'cannot start GNUmed slave, no startup command defined')
				return False
			os.system(startup_cmd)	# better be non-blocking, use gmShellAPI
			_log.Log(gmLog.lInfo, 'trying to start one with [%s]' % startup_cmd)
			app = wx.PySimpleApp()
			dlg = gmGuiHelpers.c2ButtonQuestionDlg (
				caption = _('gm_ctl_client: starting slave GNUmed client'),
				question = _(
					'A GNUmed slave client has been started because\n'
					'no running client could be found. You will now\n'
					'have to enter your user name and password into\n'
					'the login dialog as usual.\n'
					'\n'
					'Switch to the GNUmed login dialog now and proceed\n'
					'with the login procedure. Once GNUmed has started\n'
					'up successfully switch back to this window.\n'
				),
				button_defs = [
					{'label': _('Connect to GNUmed'), 'tooltip': _('Proceed and try to connect to the newly started GNUmed client.'), 'default': True},
					{'label': _('Abort'), 'tooltip': _('Abort and do NOT connect to GNUmed.')}
				]
			)
			retry = (dlg.ShowModal() == wx.ID_YES)

#			retry = gmGuiHelpers.gm_show_question (
#				aMessage = _(
#					'GNUmed has been started with the command:\n'
#					'\n'
#					' [%s]\n'
#					'\n'
#					'Please enter user name and password\n'
#					'into the GNUmed login dialog.\n'
#					'\n'
#					'Has GNUmed started up successfully ?'
#				) % startup_cmd,
#				aTitle = _('GNUmed client controller')
#			)
			if not retry:
				return False

			alt_port = _cfg.get('GNUmed instance', 'startup port')
			if alt_port is not None:
				port = alt_port

			try:
				_log.Log(gmLog.lInfo, self.__gm_server.version())
			except socket.error, e:
				# FIXME: differentiate between already-attached and not-there
				_log.LogException('cannot attach to GNUmed instance at http://localhost:%s: %s' % (port, e))
				return False

		_log.Log(gmLog.lInfo, 'enslaveable GNUmed client found, testing suitability')

		target_personality = _cfg.get('GNUmed instance', 'personality')
		success, self.__conn_auth = self.__gm_server.attach(target_personality)
		if not success:
			_log.Log(gmLog.lErr, 'cannot attach: %s' % self.__conn_auth)
			self.__gm_server.force_detach()
			user_done, can_attach = self.__gm_server.get_user_answer()
			while not user_done:
				time.sleep(0.75)
				user_done, can_attach = self.__gm_server.get_user_answer()
			if not can_attach:
				_log.Log(gmLog.lErr, 'cannot attach to GNUmed instance [%s]' % target_personality)
				return False
			_log.Log(gmLog.lInfo, 'successfully broke other connection, now attached')
			success, self.__conn_auth = self.__gm_server.attach(target_personality)
			if not success:
				_log.Log(gmLog.lErr, 'cannot attach: %s' % self.__conn_auth)
				return False

		return True
	#--------------------------------------------------------------
	def setup(self):
		# load external patient
		success, lock_cookie = self.__gm_server.load_patient_from_external_source(self.__conn_auth)
		if not success:
			_log.Log(gmLog.lErr, 'error loading patient from external source in GNUmed')
			return False
		user_done, patient_loaded = self.__gm_server.get_user_answer()
		# FIXME: this might loop forever
		while not user_done:
			time.sleep(0.75)
			user_done, patient_loaded = self.__gm_server.get_user_answer()
		if not patient_loaded:
			_log.Log(gmLog.lErr, 'cannot load patient from external source in GNUmed')
			return False
		# lock loaded patient
		success, self.__unlock_auth = self.__gm_server.lock_loaded_patient(self.__conn_auth, lock_cookie)
		if not success:
			_log.Log(gmLog.lErr, 'cannot lock patient')
			return False
		self.__gm_server.raise_gnumed(self.__conn_auth)
		return True
	#--------------------------------------------------------------
	def run_script(self):
		"""Override this in derived classes."""
		# run script (eg. raise desired plugin)
		target_plugin = _cfg.get('script', 'target plugin')
		plugins = self.__gm_server.get_loaded_plugins(self.__conn_auth)
		if target_plugin not in plugins:
			_log.Log(gmLog.lErr, 'plugin [%s] not loaded in GNUmed' % target_plugin)
			_log.Log(gmLog.lInfo, str(plugins))
			return False
		if not self.__gm_server.raise_notebook_plugin(self.__conn_auth, target_plugin):
			_log.Log(gmLog.lErr, 'cannot raise plugin [%s]' % target_plugin)
			return False
		return True
	#--------------------------------------------------------------
	def cleanup(self):
		# cleanup
		self.__gm_server.unlock_patient(self.__conn_auth, self.__unlock_auth)
		self.__gm_server.detach(self.__conn_auth)

#==================================================================
if __name__ == '__main__':
	_log.SetAllLogLevels(gmLog.lData)

	td = None
	if gmCLI.has_arg('--text-domain'):
		td = gmCLI.arg['--text-domain']
	l = None
	if gmCLI.has_arg('--lang-gettext'):
		l = gmCLI.arg['--lang-gettext']

	gmI18N.activate_locale()
	gmI18N.install_domain(domain = td, language = l)

	connector = cBaseConnector()
	if not connector.connect():
		sys.exit('connect() error')
	if not connector.setup():
		connector.cleanup()
		sys.exit('setup() error')
	if not connector.run_script():
		connector.cleanup()
		sys.exit('run_script() error')
	connector.cleanup()

#==================================================================
# $Log: gm_ctl_client.py,v $
# Revision 1.5  2007-10-09 09:55:44  ncq
# - better logging
# - fix connect error
#
# Revision 1.4  2007/09/14 11:47:22  ncq
# - support alternate port for started GNUmed slave
# - make alternate port and startup command optional
# - improve docs
#
# Revision 1.3  2007/07/17 13:39:46  ncq
# - support starting up GNUmed client on demand
#
# Revision 1.2  2007/07/10 20:33:41  ncq
# - consolidate domain arg
#
# Revision 1.1  2007/01/29 13:49:39  ncq
# - renamed
#
# Revision 1.10  2006/12/21 10:48:57  ncq
# - properly check config file
#
# Revision 1.9  2006/09/01 15:42:32  ncq
# - no more --unicode-gettext
#
# Revision 1.8  2006/07/24 20:29:23  ncq
# - add gettext options
#
# Revision 1.7  2006/07/22 12:33:11  ncq
# - fix variable naming
#
# Revision 1.6  2006/07/22 12:14:48  ncq
# - cleanup
#
# Revision 1.5  2006/07/22 10:32:35  ncq
# - start removing references to xDT as we ain't limited by that anymore
#
# Revision 1.4  2006/07/22 10:03:17  ncq
# - properly use load_external_patient via macro scripter
#
# Revision 1.3  2006/07/21 21:29:02  ncq
# - properly activate locale
#
# Revision 1.2  2005/11/01 08:51:05  ncq
# - GnuMed -> GNUmed
#
# Revision 1.1  2004/09/13 09:49:06  ncq
# - XDT connector + docs
#
