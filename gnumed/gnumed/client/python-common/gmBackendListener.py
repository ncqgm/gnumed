"""GnuMed database backend listener.

This module implements threaded listening for asynchronuous
notifications from the database backend.

NOTE !  This is specific to the DB adapter pyPgSQL and
        not DB-API compliant !
"""
#=====================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/python-common/Attic/gmBackendListener.py,v $
__version__ = "$Revision: 1.13 $"
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
		self._intercepted_notifications = []
		# remember what service we are representing
		self._service = service
		#check for messages every 'poll_interval' seconds
		self._poll_interval = poll_interval
		#connect to the backend
		self._conn = self.__connect(database, user, password, host, port)
		# lock for access to connection object
		self._conn_lock = threading.Lock()
		# a pointer to out thread
		self._thread = None
	#-------------------------------
	def __del__(self):
		self._quit = 1
		for notification in self._intercepted_notifications:
			self.__unlisten_notification(notification)
		# give the thread time to terminate
		if self._thread is not None:
			self._thread.join(self._poll_interval+2)
	#-------------------------------
	# public API
	#-------------------------------
	def register_callback(self, aSignal, aCallback):
		# if not listening to that signal yet, do so now
		if aSignal not in self._intercepted_notifications:
			cmd = 'LISTEN "%s";' % aSignal
			try:
				self._conn_lock.acquire(blocking = 1)
				res = self._conn.query(cmd)
				self._conn_lock.release()
			except StandardError:
				_log.Log(gmLog.lErr, '>>>%s<<< failed' % cmd)
				_log.LogException('cannot register backend callback', sys.exc_info())
				try:
					self._conn_lock.release()
				except:
					_log.LogException("must have passed lock release, or not acquired lock at all", sys.exc_info())
				return None
			if res.resultType == libpq.RESULT_ERROR:
				_log.Log(gmLog.lErr, 'cannot register backend callback')
				_log.Log(gmLog.lErr, ">>>%s<<< failed" % cmd)
				_log.Log(gmLog.lData, "command status [%s], result status [%s]" % (res.resultStatus, res.cmdStatus))
				_log.Log(gmLog.lData, libpq.Error)
				return None
			self._intercepted_notifications.append(aSignal)
		# connect signal with callback function
		gmDispatcher.connect(receiver = aCallback, signal = aSignal, sender = self._service)
		if self._thread is None:
			self.__start_thread()
	#-------------------------------
	def unregister_callback(self, aSignal, aCallback):
		# unlisten to signal
		self.__unlisten_notification(aSignal)
		# don't deliver the backend signal anymore,
		# this isn't strictly required but helps to prevent
		# accumulation of dead receivers in gmDispatcher
		gmDispatcher.disconnect(receiver = aCallback, signal = aSignal, sender = self._service)
		return 1
	#-------------------------------
	def tell_thread_to_stop(self):
		if self._thread is None:
			return 1
		self._quit = 1
	#-------------------------------
	# internal helpers
	#-------------------------------
	def __unlisten_notification(self, aNotification):
		# are we listening at all ?
		if aNotification not in self._intercepted_notifications:
			_log.Log(gmLog.lWarn, 'not listening to [%s]' % aNotification)
			return 1
		# stop listening
		cmd = 'UNLISTEN "%s";' % aNotification
		try:
			self._conn_lock.acquire(blocking = 1)
			res = self._conn.query(cmd)
			self._conn_lock.release()
		except StandardError:
			self._conn_lock.release()
			_log.Log(gmLog.lErr, '>>>%s<<< failed' % cmd)
			_log.LogException('cannot unlisten notification [%s]' % aNotification, sys.exc_info())
			return None
		if res.resultType == libpq.RESULT_ERROR:
			_log.Log(gmLog.lErr, ">>>%s<<< failed" % cmd)
			_log.Log(gmLog.lErr, 'cannot unlisten notification [%s]' % aNotification)
			_log.Log(gmLog.lData, "command status [%s], result status [%s]" % (res.resultStatus, res.cmdStatus))
			_log.Log(gmLog.lData, libpq.Error)
			return None
		# remove from list of intercepted signals
		try:
			self._intercepted_notifications.remove(aNotification)
		except ValueError:
			pass
		return 1
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
		try:
			self._thread = threading.Thread(target = self._process_notifications)
			self._thread.start()
		except StandardError:
			_log.LogException("Can't start thread.", sys.exc_info())
			return None
		return 1
	#-------------------------------
	# the actual thread code
	#-------------------------------
	def _process_notifications(self):
		while 1:
			if self._quit:
				break
			time.sleep(0.35)					# give others time to acquire lock
			if self._quit:
				break
			self._conn_lock.acquire(blocking = 1)
			ready_input_sockets = select.select([self._conn.socket], [], [], 1.0)[0]
			self._conn_lock.release()
			if self._quit:
				break
			# any input available ?
			if len(ready_input_sockets) != 0:
				# grab what came in
				self._conn_lock.acquire(blocking = 1)
				self._conn.consumeInput()
				note = self._conn.notifies()
				self._conn_lock.release()
				# any notifications ?
				while note:
					# if self._quit is true we may be in __del__ in which case
					# gmDispatcher isn't guarantueed to exist anymore
					if not self._quit:
						try:
							gmDispatcher.send(signal = note.relname, sender = self._service, sending_backend_pid = note.be_pid)
						except:
							pass
					if self._quit:
						break
					time.sleep(0.25)
					if self._quit:
						break
					self._conn_lock.acquire(blocking = 1)
					note = self._conn.notifies()
					self._conn_lock.release()
			else:
				# don't sleep waiting for input if we plan on quitting anyways
				if self._quit:
					break
				# wait at max self.__poll_intervall + 350ms
				time.sleep(0.35)
				if self._quit:
					break
				self._conn_lock.acquire(blocking = 1)
				select.select([self._conn.socket], [], [], self._poll_interval)
				self._conn_lock.release()

		self._thread = None
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

		listener.exit()
	except KeyboardInterrupt:
		print "cancelled by user"
		listener.exit()

#=====================================================================
# $Log: gmBackendListener.py,v $
# Revision 1.13  2003-05-27 14:38:22  sjtan
#
# looks like was intended to be caught if throws exception here.
#
# Revision 1.12  2003/05/03 14:14:27  ncq
# - slightly better variable names
# - keep reference to thread so we properly rejoin() upon __del__
# - helper __unlisten_signal()
# - remove notification from list of intercepted ones upon unregister_callback
# - be even more careful in thread such that to stop quickly
#
# Revision 1.11  2003/05/03 00:42:11  ncq
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
