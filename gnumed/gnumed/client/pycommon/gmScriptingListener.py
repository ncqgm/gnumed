"""GNUmed scripting listener.

This module implements threaded listening for scripting.
"""
#=====================================================================
__author__ = "K.Hilbert <karsten.hilbert@gmx.net>"

import sys
import time
import threading
import select
import logging
import xmlrpc.server


_log = logging.getLogger('gm.scripting')

#=====================================================================
# FIXME: this should use /var/run/gnumed/xml-rpc-port.pid
# FIXME: and store the current port there
class cScriptingListener:
	"""This class handles how GNUmed listens for external requests.

	It starts an XML-RPC server and forks a thread which
	listens for incoming requests. Those requests are then
	handed over to a macro executor and the results handed
	back to the caller.
	"""
	def __init__(self, port=None, macro_executor=None, poll_interval:int=3):
		"""Setup the listener.

		Args:
			port: Port number (int or str) to listen on. Always on <localhost>.
			macro_executor: Class processing GNUmed macros.
			poll_interval: Listening socket select() timeout.
		"""
		# listener thread will regularly try to acquire
		# this lock, when it succeeds it will quit
		self._quit_lock = threading.Lock()
		if not self._quit_lock.acquire(blocking = True, timeout = 2):
			_log.error('cannot acquire thread quit lock !?! aborting')
			raise OSError("cannot acquire thread quit-lock")

		# check for data every 'poll_interval' seconds
		self._poll_interval = poll_interval
		# localhost only for somewhat better security
		self._listener_address = '127.0.0.1'
		self._port = int(port)
		self._macro_executor = macro_executor

		self._server = xmlrpc.server.SimpleXMLRPCServer(addr=(self._listener_address, self._port), logRequests=False)
		self._server.register_instance(self._macro_executor)
		self._server.allow_reuse_address = True

		self._thread = threading.Thread (
			target = self._process_RPCs,
			name = self.__class__.__name__
		)
		self._thread.setDaemon(True)
		self._thread.start()

		_log.info('scripting listener started on [%s:%s]' % (self._listener_address, self._port))
		_log.info('macro executor: %s' % self._macro_executor)
		_log.info('poll interval: %s seconds', self._poll_interval)

	#-------------------------------
	# public API
	#-------------------------------
	def shutdown(self):
		"""Cleanly shut down resources."""
		if self._thread is None:
			return

		_log.info('stopping frontend scripting listener thread')
		self._quit_lock.release()
		try:
			self._thread.join(self._poll_interval+5)
			try:
				if self._thread.is_alive():
					_log.error('listener thread still alive after join()')
					_log.debug('active threads: %s' % threading.enumerate())
			except Exception:
				pass
		except Exception:
			print(sys.exc_info())
		self._thread = None
		try:
			self._server.socket.shutdown(2)
		except Exception:
			_log.exception('cannot cleanly shutdown(2) scripting listener socket')
		try:
			self._server.socket.close()
		except Exception:
			_log.exception('cannot cleanly close() scripting listener socket')

	#-------------------------------
	# internal helpers
	#-------------------------------
	def _process_RPCs(self):
		"""Poll for incoming requests on the XML RPC server socket and invoke the request handler."""
		while 1:
			if self._quit_lock.acquire(blocking = False):
				break
			time.sleep(0.35)					# give others time to acquire lock
			if self._quit_lock.acquire(blocking = False):
				break
			# wait at most self.__poll_interval for new data
			ready_input_sockets = select.select([self._server.socket], [], [], self._poll_interval)[0]
			# any input available ?
			if len(ready_input_sockets) == 0:
				time.sleep(0.35)
				if self._quit_lock.acquire(blocking = False):
					break
				continue
			# we may be in __del__ so we might fail here
			try:
				self._server.handle_request()
			except Exception:
				_log.exception('cannot serve RPC')
				print("ERROR: cannot serve RPC")
				break
			if self._quit_lock.acquire(blocking = False):
				break
			time.sleep(0.25)
			if self._quit_lock.acquire(blocking = False):
				break
		# exit thread activity
		return

#=====================================================================
# main
#=====================================================================
if __name__ == "__main__":

	#-------------------------------
	class runner:
		def tell_time(self):
			return time.asctime()

	#-------------------------------
	if (len(sys.argv) > 1) and (sys.argv[1] == 'test'):
		import xmlrpc.client
		try:
			listener = cScriptingListener(macro_executor=runner(), port=9999)
		except Exception:
			_log.exception('cannot instantiate scripting listener')
			sys.exit(1)

		srv = xmlrpc.client.ServerProxy('http://localhost:9999')
		try:
			t = srv.tell_time()
			print(t)
		except Exception:
			_log.exception('cannot interact with server')
		listener.shutdown()
