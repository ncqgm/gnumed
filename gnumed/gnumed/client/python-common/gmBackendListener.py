"""GnuMed database backend listener.

This module implements threaded listening for asynchronuous
notifications from the database backend.

NOTE !  This is specific to the DB adapter pyPgSQL and
        not DB-API compliant !
"""
#=====================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/python-common/Attic/gmBackendListener.py,v $
__version__ = "$Revision: 1.11 $"
__author__ = "H. Herb <hherb@gnumed.net>"

import sys, time, threading, select
from pyPgSQL import libpq
import gmDispatcher, gmLog
_log = gmLog.gmDefLog
#=====================================================================
class BackendListener:
	def __init__(self, service, database, user, password, host='localhost', port=5432, poll_interval = 3):
		#when self._quit is true, the thread is stopped
		self._quit = 0
		# remember what signals we are listening for; no need to listen twice to the same signal
		self._intercepted_signals = []
		# remember what service we are representing
		self._service = service
		#check for messages every 'poll_interval' seconds
		self._poll_interval = poll_interval
		#is the thread runnning already?
		self._thread_running = 0
		#connect to the backend
		self._conn = self.__connect(database, user, password, host, port)
		# lock for access to connection object
		self._conn_lock = threading.Lock()
	#-------------------------------
	def __del__(self):
		self._quit = 1
		# give the thread time to terminate
		time.sleep(self._poll_interval+2)
	#-------------------------------
	# public API
	#-------------------------------
	def register_callback(self, aSignal, aCallback):
		# if not listening to that signal yet, do so now
		if aSignal not in self._intercepted_signals:
			cmd = 'LISTEN "%s";' % aSignal
			try:
				self._conn_lock.acquire(blocking = 1)
				res = self._conn.query(cmd)
				self._conn_lock.release()
			except StandardError:
				self._conn_lock.release()
				_log.Log(gmLog.lErr, '>>>%s<<< failed' % cmd)
				_log.LogException('cannot register backend callback', sys.exc_info())
				return None
			if res.resultType == libpq.RESULT_ERROR:
#			if res.resultStatus != libpq.COMMAND_OK:
				_log.Log(gmLog.lErr, 'cannot register backend callback')
				_log.Log(gmLog.lErr, ">>>%s<<< failed" % cmd)
				_log.Log(gmLog.lData, "command status [%s], result status [%s]" % (res.resultStatus, res.cmdStatus))
#				_log.Log(gmLog.lData, self._conn.errorMessage)
				_log.Log(gmLog.lData, libpq.Error)
				return None
			self._intercepted_signals.append(aSignal)
		# connect signal with callback function
		gmDispatcher.connect(receiver = aCallback, signal = aSignal, sender = self._service)
		if not self._thread_running:
			self.__start_thread()
	#-------------------------------
	def unregister_callback(self, aSignal, aCallback):
		# are we listening at all ?
		if aSignal not in self._intercepted_signals:
			_log.Log(gmLog.lWarn, 'not listening to [%s]' % aSignal)
			return 1
		# stop listening now
		cmd = 'UNLISTEN "%s";' % aSignal
		try:
			res = self._conn.query(cmd)
		except StandardError:
			_log.Log(gmLog.lErr, '>>>%s<<< failed' % cmd)
			_log.LogException('cannot unregister backend callback', sys.exc_info())
			return None
		if res.resultType == libpq.RESULT_ERROR:
			_log.Log(gmLog.lErr, 'cannot unregister backend callback')
			_log.Log(gmLog.lErr, ">>>%s<<< failed" % cmd)
			_log.Log(gmLog.lData, "command status [%s], result status [%s]" % (res.resultStatus, res.cmdStatus))
			_log.Log(gmLog.lData, self._conn.errorMessage)
			_log.Log(gmLog.lData, libpq.Error)
			return None
		# don't deliver the backend signal anymore,
		# this isn't strictly required but helps to prevent
		# accumulation of dead receivers in gmDispatcher
		gmDispatcher.disconnect(receiver = aCallback, signal = aSignal, sender = self._service)
		return 1
	#-------------------------------
	def tell_thread_to_stop(self):
		self._quit = 1
	#-------------------------------
	# internal helpers
	#-------------------------------
	def __connect(self, database, user, password, host='localhost', port=5432):
		cnx = None
		try:
			auth = "dbname='%s' user='%s' password='%s' host='%s' port=%d" % (database, user, password, host, port)
			cnx = libpq.PQconnectdb(auth)
		except libpq.Error, msg:
			_log.LogException("Connection to database '%s' failed: %s" % (database, msg), sys.exc_info())
		return cnx
	#-------------------------------
	def __start_thread(self):
		if self._conn is None:
			_log.Log(gmLog.lErr, "Can't start thread. No connection to backend available.")
			return None
#		sys.stdout.flush()
		thread = threading.Thread(target = self._process_notifications)
		self._thread_running = 1
		thread.start()
	#-------------------------------
	# the actual threaded code
	#-------------------------------
	def _process_notifications(self):
		while 1:
			# don't check for input if we plan on quitting anyways
			if self._quit:
				break
			# give others some time to acquire the lock before waiting for input
			time.sleep(0.35)
			self._conn_lock.acquire(blocking = 1)
			ready_input_sockets = select.select([self._conn.socket], [], [], 1.0)[0]
			self._conn_lock.release()

			if len(ready_input_sockets) != 0:
				# grab what came in
				time.sleep(0.2)
				self._conn_lock.acquire(blocking = 1)
				self._conn.consumeInput()
				note = self._conn.notifies()
				self._conn_lock.release()
				# any notifications amongst the data ?
				while note:
#					_log.Log(gmLog.lData, 'backend [%s] sent signal [%s]' % (note.be_pid, note.relname))
					gmDispatcher.send(signal = note.relname, sender = self._service, sending_backend_pid = note.be_pid)
					# don't handle more notifications if we plan on quitting anyways
					if self._quit:
						break
					time.sleep(0.25)
					self._conn_lock.acquire(blocking = 1)
					note = self._conn.notifies()
					self._conn_lock.release()
			else:
				# don't sleep waiting for input if we plan on quitting anyways
				if self._quit:
					break
				# wait at max self.__poll_intervall + 300ms
				time.sleep(0.35)
				self._conn_lock.acquire(blocking = 1)
				select.select([self._conn.socket], [], [], self._poll_interval)
				self._conn_lock.release()

			if self._quit:
				self._thread_running = 0
				break
#=====================================================================
# main
#=====================================================================
notifies = 0
if __name__ == "__main__":
	_log.SetAllLogLevels(gmLog.lData)

_log.Log(gmLog.lData, __version__)

if __name__ == "__main__":
	import time
	#-------------------------------
	def dummy(n):
		return float(n)*n/float(1+n)
	#-------------------------------
	def OnPatientModified():
		global notifies
		notifies += 1
		sys.stdout.flush()
		print "\nBackend says: patient data has been modified (%s. notification)" % notifies
	#-------------------------------
	try:
		n = int(sys.argv[1])
	except:
		print "You can set the number of iterations\nwith the first command line argument"
		n= 100000

	# try loop without backend listener
	print "Looping",n,"times through dummy function"
	i=0
	t1 = time.time()
	while i<n:
		r = dummy(i)
		i+=1
	t2=time.time()
	t_nothreads=t2-t1
	print "Without backend thread, it took", t_nothreads, "seconds"

	# now try with listener to measure impact
	print "Now fire up psql in a new shell, return\nhere and hit <enter> to continue."
	try:
		raw_input('hit <enter> when done starting psql: ')
	except:
		pass
	print "You now have about 30 seconds to go to the psql shell"
	print "and type 'notify patient_changed'<enter> several times."
	print "This should trigger our backend listening callback."
	print "You can also try to stop the demo with Ctrl-C!"
	listener = BackendListener(service='default', database='gnumed', user='gnumed', password='')
	listener.register_callback('patient_changed', OnPatientModified)

	try:
		counter = 0
		while counter<20:
			counter += 1
			time.sleep(1)
			sys.stdout.flush()
			print '.',
		print "Looping",n,"times through dummy function"
		i=0
		t1 = time.time()
		while i<n:
			r = dummy(i)
			i+=1
		t2=time.time()
		t_threaded = t2-t1
		print "With backend thread, it took", t_threaded, "seconds"
		print "Difference:", t_threaded-t_nothreads

		listener.tell_thread_to_stop()
	except KeyboardInterrupt:
		print "cancelled by user"
		listener.Stop()

#=====================================================================
# $Log: gmBackendListener.py,v $
# Revision 1.11  2003-05-03 00:42:11  ncq
# - first shot at syncing thread at __del__ time, non-working
#
# Revision 1.10  2003/04/28 21:38:13  ncq
# - properly lock access to self._conn across threads
# - give others a chance to acquire the lock
#
# Revision 1.9  2003/04/27 11:34:02  ncq
# - rewrite register_callback() to allow for more than one callback per signal
# - add unregister_callback()
# - clean up __connect(), __start_thread()
# - optimize _process_notifications()
#
# Revision 1.8  2003/04/25 13:00:43  ncq
# - more cleanup/renaming on the way to more goodness, eventually
#
# Revision 1.7  2003/02/07 14:22:35  ncq
# - whitespace fix
#
# Revision 1.6  2003/01/16 14:45:03  ncq
# - debianized
#
# Revision 1.5  2002/09/26 13:21:37  ncq
# - log version
#
# Revision 1.4  2002/09/08 21:22:36  ncq
# - removed one debugging level print()
#
# Revision 1.3  2002/09/08 20:58:46  ncq
# - made comments more useful
# - added some more metadata to get in line with GnuMed coding standards
#
