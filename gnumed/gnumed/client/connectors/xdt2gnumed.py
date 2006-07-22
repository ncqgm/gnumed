#!/usr/bin/env python
"""
A connector framework showing how to online drive a slave
GNUmed client via the XML-RPC interface.

The base class simply raises the plugin that is set in
the configuration file. If you want your derivative class
to do smarter things you need to override:

	cBaseConnector.run_script()
"""

#==================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/connectors/Attic/xdt2gnumed.py,v $
# $Id: xdt2gnumed.py,v 1.5 2006-07-22 10:32:35 ncq Exp $
__version__ = '$Revision: 1.5 $'
__author__ = 'Karsten Hilbert <Karsten.Hilbert@gmx.net>'
__license__ = 'GPL'

import sys, time, xmlrpclib, socket, time

from Gnumed.pycommon import gmCfg, gmExceptions, gmI18N, gmLog

_log = gmLog.gmDefLog
_cfg = gmCfg.gmDefCfgFile

_log.Log(gmLog.lInfo, __version__)
#==================================================================
class cBaseConnector:

	def __init__(self):
		# sanity check
		if _cfg is None:
			_log.Log(gmLog.lErr, 'cannot run without config file')
			raise gmExceptions.ConstructorError, _("Cannot find config file. Option syntax: --conf-file=<file>")
		self.__conn_auth = 0
		self.__unlock_auth = 0
	#--------------------------------------------------------------
	def setup(self):
		# connect to GNUmed instance
		# FIXME: wait and retry after force_detach()
		port = _cfg.get('GNUmed instance', 'port')
		self.__gm_server = xmlrpclib.ServerProxy('http://localhost:%s' % int(port))
		try:
			_log.Log(gmLog.lInfo, self.__gm_server.version())
		except socket.error, e:
			_log.LogException('Cannot attach to GNUmed instance at http://localhost:%s: %s' % (port, e), sys.exc_info())
			return False
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
		# load external patient
		success, lock_cookie = self.__gm_server.load_patient_from_external_source(self.__conn_auth)
		if not success:
			_log.Log(gmLog.lErr, 'error loading patient from external source in GNUmed')
			return False
		user_done, can_attach = self.__gm_server.get_user_answer()
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

	gmI18N.activate_locale()
	gmI18N.install_domain('gnumed')

	connector = cBaseConnector()
	if not connector.setup():
		connector.cleanup()
		sys.exit('setup error')
	if not connector.run_script():
		connector.cleanup()
		sys.exit('run_script error')
	connector.cleanup()

#==================================================================
# $Log: xdt2gnumed.py,v $
# Revision 1.5  2006-07-22 10:32:35  ncq
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
