"""GnuMed scripting listener.

This module implements threaded listening for scripting.
"""
#=====================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/pycommon/gmScriptingListener.py,v $
__version__ = "$Revision: 1.2 $"
__author__ = "K.Hilbert <karsten.hilbert@gmx.net>"

import sys, time, threading, SimpleXMLRPCServer, select
import gmDispatcher, gmLog, gmExceptions
_log = gmLog.gmDefLog

#=====================================================================
class cScriptingListener:
	def __init__(self, port = 9999, macro_executor = None, poll_interval = 3):
		if macro_executor is None:
			raise gmExceptions.ConstructorError, "need macro executor object parameter"
		# listener thread will regularly try to acquire
		# this lock, when it succeeds it will quit
		self._quit_lock = threading.Lock()
		if not self._quit_lock.acquire(0):
			_log.Log(gmLog.lErr, 'cannot acquire thread quit lock !?! aborting')
			raise gmExceptions.ConstructorError, "cannot acquire thread quit-lock"
		# check for data every 'poll_interval' seconds
		self._poll_interval = poll_interval
		# setup XML-RPC server
		if not self.__start_server(port, macro_executor):
			raise gmExceptions.ConstructorError, "cannot start XML-RPC server on port [%s]" % port
		# start thread
		if not self.__start_thread():
			raise gmExceptions.ConstructorError, "cannot start listener thread"
	#-------------------------------
	def __del__(self):
		# allow listener thread to acquire quit lock
		try:
			self._quit_lock.release()
			# give the thread time to terminate
			if self._thread is not None:
				self._thread.join(self._poll_interval+2)
		except:	pass
		# ???
		try:
			self._server.socket.shutdown(2)
		except: pass
		try:
			self._server.socket.close()
		except: pass
		try:
			del self._server
		except: pass
	#-------------------------------
	def __start_server(self, a_port, a_macro_executor):
		self._port = int(a_port)
		self._macro_executor = a_macro_executor
		try:
			self._server = SimpleXMLRPCServer.SimpleXMLRPCServer(addr=('127.0.0.1', self._port), logRequests=False)
			self._server.register_instance(self._macro_executor)
			self._server.allow_reuse_address = True
		except:
			_log.LogException('cannot start XML-RPC server [localhost:%s]' % a_port, sys.exc_info())
			return None
		return 1
	#-------------------------------
	# public API
	#-------------------------------
	def tell_thread_to_stop(self):
		self._quit_lock.release()
	#-------------------------------
	# internal helpers
	#-------------------------------
	def __start_thread(self):
		try:
			self._thread = threading.Thread(target = self._process_RPCs)
			self._thread.start()
		except StandardError:
			_log.LogException("cannot start thread", sys.exc_info(), verbose=1)
			return None
		return 1
	#-------------------------------
	# the actual thread code
	#-------------------------------
	def _process_RPCs(self):
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
	_log.SetAllLogLevels(gmLog.lData)

_log.Log(gmLog.lData, __version__)

if __name__ == "__main__":
	import xmlrpclib
	#-------------------------------
	class runner:
		def tell_time(self):
			return time.asctime()
	#-------------------------------
	listener = cScriptingListener(macro_executor=runner(), port=9999)
	s = xmlrpclib.ServerProxy('http://localhost:9999')
	t = s.tell_time()
	print t
	listener.tell_thread_to_stop()
#=====================================================================
# $Log: gmScriptingListener.py,v $
# Revision 1.2  2004-09-13 08:51:03  ncq
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
