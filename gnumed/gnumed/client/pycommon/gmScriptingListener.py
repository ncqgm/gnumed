"""GNUmed scripting listener.

This module implements threaded listening for scripting.
"""
#=====================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/pycommon/gmScriptingListener.py,v $
__version__ = "$Revision: 1.5 $"
__author__ = "K.Hilbert <karsten.hilbert@gmx.net>"

import sys, time, threading, SimpleXMLRPCServer, select, logging


_log = logging.getLogger('gm.scripting')
_log.info(__version__)
#=====================================================================
class cScriptingListener:

	# FIXME: this should use /var/run/gnumed/xml-rpc-port.pid
	# FIXME: and store the current port there

	"""This class handles how GNUmed listens for external requests.

	It starts an XML-RPC server and forks a thread which
	listens for incoming requests. Those requests are then
	handed over to a macro executor and the results handed
	back to the caller.
	"""
	def __init__(self, port = None, macro_executor = None, poll_interval = 3):
		# listener thread will regularly try to acquire
		# this lock, when it succeeds it will quit
		self._quit_lock = threading.Lock()
		if not self._quit_lock.acquire(0):
			_log.error('cannot acquire thread quit lock !?! aborting')
			import thread
			raise thread.error("cannot acquire thread quit-lock")

		# check for data every 'poll_interval' seconds
		self._poll_interval = poll_interval
		# localhost only for somewhat better security
		self._listener_address = '127.0.0.1'
		self._port = int(port)
		self._macro_executor = macro_executor

		self._server = SimpleXMLRPCServer.SimpleXMLRPCServer(addr=(self._listener_address, self._port), logRequests=False)
		self._server.register_instance(self._macro_executor)
		self._server.allow_reuse_address = True

		self._thread = threading.Thread(target = self._process_RPCs)
		self._thread.start()

		_log.info('scripting listener started on [%s:%s]' % (self._listener_address, self._port))
		_log.info('macro executor is [%s]' % self._macro_executor)
	#-------------------------------
	# public API
	#-------------------------------
	def shutdown(self):
		"""Cleanly shut down. Complement to __init__()."""

		# allow listener thread to acquire quit lock and give it time to terminate
		self._quit_lock.release()
		if self._thread is not None:
			self._thread.join(self._poll_interval+5)

		try:
			self._server.socket.shutdown(2)
		except:
			_log.exception('cannot cleanly shutdown(5) scripting listener socket')

		try:
			self._server.socket.close()
		except:
			_log.exception('cannot cleanly close() scripting listener socket')
	#-------------------------------
	# internal helpers
	#-------------------------------
	def _process_RPCs(self):
		"""The actual thread code."""
		while 1:
			if self._quit_lock.acquire(0):
				break
			time.sleep(0.35)					# give others time to acquire lock
			if self._quit_lock.acquire(0):
				break
			# wait at most self.__poll_interval for new data
			ready_input_sockets = select.select([self._server.socket], [], [], self._poll_interval)[0]
			# any input available ?
			if len(ready_input_sockets) != 0:
				# we may be in __del__ so we might fail here
				try:
					self._server.handle_request()
				except:
					print "cannot serve RPC"
					break
				if self._quit_lock.acquire(0):
					break
				time.sleep(0.25)
				if self._quit_lock.acquire(0):
					break
			else:
				time.sleep(0.35)
				if self._quit_lock.acquire(0):
					break

		self._thread = None
#=====================================================================
# main
#=====================================================================
if __name__ == "__main__":

	#-------------------------------
	class runner:
		def tell_time(self):
			return time.asctime()
	#-------------------------------
	if (len(sys.argv) > 1) and (sys.argv[1] == u'test'):
		import xmlrpclib

		try:
			listener = cScriptingListener(macro_executor=runner(), port=9999)
		except:
			_log.exception('cannot instantiate scripting listener')
			sys.exit(1)

		s = xmlrpclib.ServerProxy('http://localhost:9999')
		try:
			t = s.tell_time()
			print t
		except:
			_log.exception('cannot interact with server')

		listener.shutdown()
#=====================================================================
# $Log: gmScriptingListener.py,v $
# Revision 1.5  2007-12-12 16:17:16  ncq
# - better logger names
#
# Revision 1.4  2007/12/11 15:39:01  ncq
# - use std lib logging
#
# Revision 1.3  2007/12/03 20:43:53  ncq
# - lots of cleanup
# - fix/enhance test suite
#
# Revision 1.2  2004/09/13 08:51:03  ncq
# - make sure port is an integer
# - start XML RPC server with logRequests=False
# - socket allow_reuse_address
#
# Revision 1.1  2004/02/25 09:30:13  ncq
# - moved here from python-common
#
# Revision 1.3  2004/02/05 23:46:21  ncq
# - use serverproxy() instead of server() as is recommended
#
# Revision 1.2  2004/02/05 18:40:01  ncq
# - quit thread if we can't handle_request()
#
# Revision 1.1  2004/02/02 21:58:20  ncq
# - first cut
#
