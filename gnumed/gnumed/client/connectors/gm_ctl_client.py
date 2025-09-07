#!/usr/bin/python3
"""
A connector framework showing how to online drive a
slave GNUmed client via the XML-RPC interface.

The base class simply raises the plugin that is set in
the configuration file. If you want your derivative class
to do smarter things you need to override:

	cBaseConnector.run_script()
"""

#==================================================================
__author__ = 'Karsten Hilbert <Karsten.Hilbert@gmx.net>'
__license__ = 'GPL'


import sys, time, socket, time, os, logging
import xmlrpc.client


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmCfgINI, gmI18N
from Gnumed.wxpython import gmGuiHelpers


_log = logging.getLogger('gm_ctl_client')
#==================================================================
class cBaseConnector:

	def __init__(self):
		self.__conn_auth = 0
		self.__unlock_auth = 0
	#--------------------------------------------------------------
	def connect(self):
		# connect to GNUmed instance
		port = _cfg.get(group = 'GNUmed instance', option = 'port', source_order = [('explicit', 'return')])
		self.__gm_server = xmlrpc.client.ServerProxy('https://localhost:%s' % int(port))

		try:
			_log.info('GNUmed slave XML-RPC server version: %s' % self.__gm_server.version())
		except socket.error as e:
			# FIXME: differentiate between already-attached and not-there
			_log.exception('cannot attach to GNUmed instance at https://localhost:%s: %s' % (port, e))
			# try starting GNUmed
			# - no use trying to start GNUmed if wx cannot be imported
			import wx
			startup_cmd = _cfg.get(group = 'GNUmed instance', option = 'startup command', source_order = [('explicit', 'return')])
			if startup_cmd is None:
				_log.error('cannot start GNUmed slave, no startup command defined')
				return False
			os.system(startup_cmd)	# better be non-blocking, use gmShellAPI
			_log.info('trying to start one with [%s]' % startup_cmd)
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

			if not retry:
				return False

			alt_port = _cfg.get(group = 'GNUmed instance', option = 'startup port', source_order = [('explicit', 'return')])
			if alt_port is not None:
				port = alt_port

			try:
				_log.info(self.__gm_server.version())
			except socket.error, e:
				# FIXME: differentiate between already-attached and not-there
				_log.exception('cannot attach to GNUmed instance at https://localhost:%s: %s' % (port, e))
				return False

		_log.info('enslaveable GNUmed client found, testing suitability')

		target_personality = _cfg.get(group = 'GNUmed instance', option = 'personality', source_order = [('explicit', 'return')])
		success, self.__conn_auth = self.__gm_server.attach(target_personality)
		if not success:
			_log.error('cannot attach: %s' % self.__conn_auth)
			self.__gm_server.force_detach()
			user_done, can_attach = self.__gm_server.get_user_answer()
			while not user_done:
				time.sleep(0.75)
				user_done, can_attach = self.__gm_server.get_user_answer()
			if not can_attach:
				_log.error('cannot attach to GNUmed instance [%s]' % target_personality)
				return False
			_log.info('successfully broke other connection, now attached')
			success, self.__conn_auth = self.__gm_server.attach(target_personality)
			if not success:
				_log.error('cannot attach: %s' % self.__conn_auth)
				return False

		return True
	#--------------------------------------------------------------
	def setup(self):
		# load external patient
		success, lock_cookie = self.__gm_server.load_patient_from_external_source(self.__conn_auth)
		if not success:
			_log.error('error loading patient from external source in GNUmed')
			return False
		user_done, patient_loaded = self.__gm_server.get_user_answer()
		# FIXME: this might loop forever
		while not user_done:
			time.sleep(0.75)
			user_done, patient_loaded = self.__gm_server.get_user_answer()
		if not patient_loaded:
			_log.error('cannot load patient from external source in GNUmed')
			return False
		# lock loaded patient
		success, self.__unlock_auth = self.__gm_server.lock_loaded_patient(self.__conn_auth, lock_cookie)
		if not success:
			_log.error('cannot lock patient')
			return False
		self.__gm_server.raise_gnumed(self.__conn_auth)
		return True
	#--------------------------------------------------------------
	def run_script(self):
		"""Override this in derived classes."""
		# run script (eg. raise desired plugin)
		target_plugin = _cfg.get(group = 'script', option = 'target plugin', source_order = [('explicit', 'return')])
		plugins = self.__gm_server.get_loaded_plugins(self.__conn_auth)
		if target_plugin not in plugins:
			_log.error('plugin [%s] not loaded in GNUmed' % target_plugin)
			_log.info(str(plugins))
			return False
		if not self.__gm_server.raise_notebook_plugin(self.__conn_auth, target_plugin):
			_log.error('cannot raise plugin [%s]' % target_plugin)
			return False
		return True
	#--------------------------------------------------------------
	def cleanup(self):
		# cleanup
		self.__gm_server.unlock_patient(self.__conn_auth, self.__unlock_auth)
		self.__gm_server.detach(self.__conn_auth)

#==================================================================
if __name__ == '__main__':

	_cfg = gmCfgINI.gmCfgData()

	_cfg.add_cli(long_options = ['text-domain=', 'lang-gettext=', 'conf-file='])
	td = _cfg.get(option = '--text-domain', source_order = [('cli', 'return')])
	l = _cfg.get(option = '--lang-gettext', source_order = [('cli', 'return')])
	gmI18N.activate_locale()
	gmI18N.install_domain(domain = td, language = l)

	_cfg.add_file_source (
		source = 'explicit',
		filename = _cfg.get(option = '--conf-file', source = [('cli', 'return')]),
		encoding = gmI18N.get_encoding()
	)

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
