"""GnuMed database backend listener.

This module implements threaded listening for asynchronuous
notifications from the database backend.

NOTE !  This is specific to the DB adapter pyPgSQL and
        not DB-API compliant !
"""
#=====================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/pycommon/gmBackendListener.py,v $
__version__ = "$Revision: 1.9 $"
__author__ = "H. Herb <hherb@gnumed.net>, K.Hilbert <karsten.hilbert@gmx.net>"

import sys, time, threading, select

from pyPgSQL import libpq

import gmDispatcher, gmLog, gmExceptions
_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)
#=====================================================================
class BackendListener:
	def __init__(self, service, database, user, password, host, port=5432, poll_interval=3):
		# listener thread will regularly try to acquire this
		# lock, when it succeeds it will quit
		self._quit_lock = threading.Lock()
		if not self._quit_lock.acquire(0):
			_log.Log(gmLog.lErr, 'cannot acquire thread quit lock !?! aborting')
			raise gmExceptions.ConstructorError, "cannot acquire thread quit-lock"
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
		self._listener_thread = None
	#-------------------------------
	def __del__(self):
		if self._listener_thread is None:
			return 1
		try:
			self.__unlisten_notification()
		except: pass
		try:
			self._quit_lock.release()
			# give the thread time to terminate
			self._listener_thread.join(self._poll_interval+2.0)
		except: pass
		try:
			if self._listener_thread.isAlive():
				print '__del__(): listener thread still alive after join()'
				print '__del__(): active threads:', threading.enumerate()
		except:	pass
	#-------------------------------
	# public API
	#-------------------------------
	def register_callback(self, aSignal, aCallback):
		# if not listening to that signal yet, do so now
		if aSignal not in self._intercepted_notifications:
			cmd = 'LISTEN "%s";' % aSignal
			self._conn_lock.acquire(1)
			try:
				res = self._conn.query(cmd)
			except StandardError:
				try:
					self._conn_lock.release()
				except StandardError:
					_log.LogException('this should never happen: we have the lock but cannot release it', verbose=1)
				_log.Log(gmLog.lErr, '>>>%s<<< failed' % cmd)
				_log.LogException('cannot register backend callback', sys.exc_info(), verbose=0)
				return None
			self._conn_lock.release()
			if res.resultType == libpq.RESULT_ERROR:
				_log.Log(gmLog.lErr, 'cannot register backend callback')
				_log.Log(gmLog.lErr, ">>>%s<<< failed" % cmd)
				_log.Log(gmLog.lData, "command status [%s], result status [%s]" % (res.resultStatus, res.cmdStatus))
				_log.Log(gmLog.lData, libpq.Error)
				return None
			self._intercepted_notifications.append(aSignal)
		# connect signal with callback function
		gmDispatcher.connect(receiver = aCallback, signal = aSignal, sender = self._service)
		if self._listener_thread is None:
			if not self.__start_thread():
				return None
		return 1
	#-------------------------------
	def unregister_callback(self, aSignal, aCallback):
		# unlisten to signal
		self.__unlisten_notification([aSignal])
		# don't deliver the backend signal anymore,
		# this isn't strictly required but helps to prevent
		# accumulation of dead receivers in gmDispatcher
		gmDispatcher.disconnect(receiver = aCallback, signal = aSignal, sender = self._service)
		return 1
	#-------------------------------
	def stop_thread(self):
		if self._listener_thread is None:
			return 1
		self.__unlisten_notification()
		self._quit_lock.release()
		# give the thread time to terminate
		self._listener_thread.join(self._poll_interval+2.0)
		try:
			if self._listener_thread.isAlive():
				_log.Log(gmLog.lErr, 'listener thread still alive after join()')
				_log.Log(gmLog.lData, 'active threads: %s' % threading.enumerate())
		except:
			pass
		return 1
	#-------------------------------
	# internal helpers
	#-------------------------------
	def __unlisten_notification(self, notifications=None):
		if notifications is None:
			notifications = self._intercepted_notifications
		for notify in notifications:
			# are we listening at all ?
			if notify not in notifications:
				_log.Log(gmLog.lWarn, 'not listening to [%s]' % notify)
				continue
			# stop listening
			cmd = 'UNLISTEN "%s";' % notify
			try:
				self._conn_lock.acquire(1)
				res = self._conn.query(cmd)
				self._conn_lock.release()
			except StandardError:
				self._conn_lock.release()
				_log.Log(gmLog.lErr, '>>>%s<<< failed' % cmd)
				_log.LogException('cannot unlisten notification [%s]' % notify, sys.exc_info())
				return None
			if res.resultType == libpq.RESULT_ERROR:
				_log.Log(gmLog.lErr, ">>>%s<<< failed" % cmd)
				_log.Log(gmLog.lErr, 'cannot unlisten notification [%s]' % notify)
				_log.Log(gmLog.lData, "command status [%s], result status [%s]" % (res.resultStatus, res.cmdStatus))
				_log.Log(gmLog.lData, libpq.Error)
				return None
			# remove from list of intercepted signals
			try:
				self._intercepted_notifications.remove(notify)
			except ValueError:
				pass
		return 1
	#-------------------------------
	def __connect(self, database, user, password, host, port=5432):
		try:
#			if host in ['', 'localhost']:
#				host = '' # use local connexions for localhost as it is more secure
			auth = "dbname='%s' user='%s' password='%s' host='%s' port=%d" % (database, user, password, host, port)
			cnx = libpq.PQconnectdb(auth)
		except libpq.Error, msg:
			_log.LogException("Connection to database '%s' failed: %s" % (database, msg), sys.exc_info())
			return None
		return cnx
	#-------------------------------
	def __start_thread(self):
		if self._conn is None:
			_log.Log(gmLog.lErr, "no connection to backend available, cannot start thread")
			return None
		try:
			self._listener_thread = threading.Thread(target = self._process_notifications)
			self._listener_thread.start()
		except StandardError:
			_log.LogException("Can't start thread.", sys.exc_info())
			return None
		return 1
	#-------------------------------
	# the actual thread code
	#-------------------------------
	def _process_notifications(self):
		notification = None
		_have_quit_lock = None
		while not _have_quit_lock:
			if self._quit_lock.acquire(0):
				break
			# wait at most self._poll_interval for new data
			self._conn_lock.acquire(1)
			ready_input_sockets = select.select([self._conn.socket], [], [], self._poll_interval)[0]
			self._conn_lock.release()
			# any input available ?
			if len(ready_input_sockets) == 0:
				# no, select.select() timed out
				# give others a chance to grab the conn lock (eg listen/unlisten)
				time.sleep(0.3)
				continue
			# grab what came in
			self._conn_lock.acquire(1)
			self._conn.consumeInput()
			notification = self._conn.notifies()
			self._conn_lock.release()
			# any notifications ?
			while notification is not None:
				# if self._quit_lock can be acquired we may be in
				# __del__ in which case gmDispatcher is not
				# guarantueed to exist anymore
				if self._quit_lock.acquire(0):
					_have_quit_lock = 1
					break
				# try sending intra-client signal
				try:
					results = gmDispatcher.send(signal = notification.relname, sender = self._service, sending_backend_pid = notification.be_pid)
				except:
					print "problem routing notification [%s] from backend [%s] to intra-client dispatcher" % (notification.relname, notification.be_pid)
					print sys.exc_info()
				# there *may* be more pending notifications but do we care ?
				if self._quit_lock.acquire(0):
					_have_quit_lock = 1
					break
				self._conn_lock.acquire(1)
				self._conn.consumeInput()
				notification = self._conn.notifies()
				self._conn_lock.release()

		self._listener_thread = None
#=====================================================================
# main
#=====================================================================
notifies = 0
if __name__ == "__main__":
	_log.SetAllLogLevels(gmLog.lData)

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
	print "Now in a new shell connect psql to the"
	print "database <gnumed> on localhost, return"
	print "here and hit <enter> to continue."
	try:
		raw_input('hit <enter> when done starting psql')
	except:
		pass
	print "You now have about 30 seconds to go"
	print "to the psql shell and type"
	print " notify patient_changed<enter>"
	print "several times."
	print "This should trigger our backend listening callback."
	print "You can also try to stop the demo with Ctrl-C!"

	listener = BackendListener(service='default', database='gnumed', user='gm-dbo', password='')
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
	except KeyboardInterrupt:
		print "cancelled by user"

	listener.stop_thread()
	listener.unregister_callback('patient_changed', OnPatientModified)
#=====================================================================
# $Log: gmBackendListener.py,v $
# Revision 1.9  2006-05-24 12:50:21  ncq
# - now only empty string '' means use local UNIX domain socket connections
#
# Revision 1.8  2005/01/27 17:23:14  ncq
# - just some cleanup
#
# Revision 1.7  2005/01/12 14:47:48  ncq
# - in DB speak the database owner is customarily called dbo, hence use that
#
# Revision 1.6  2004/06/25 12:28:25  ncq
# - just cleanup
#
# Revision 1.5  2004/06/15 19:18:06  ncq
# - _unlisten_notification() now accepts a list of notifications to unlisten from
# - cleanup/enhance __del__
# - slightly untighten notification handling loop so others
#   get a chance to grab the connection lock
#
# Revision 1.4  2004/06/09 14:42:05  ncq
# - cleanup, clarification
# - improve exception handling in __del__
# - tell_thread_to_stop() -> stop_thread(), uses self._listener_thread.join()
#   now, hence may take at max self._poll_interval+2 seconds longer but is
#   considerably cleaner/safer
# - vastly simplify threaded notification handling loop
#
# Revision 1.3  2004/06/01 23:42:53  ncq
# - improve error message from failed notify dispatch attempt
#
# Revision 1.2  2004/04/21 14:27:15  ihaywood
# bug preventing backendlistener working on local socket connections
#
# Revision 1.1  2004/02/25 09:30:13  ncq
# - moved here from python-common
#
# Revision 1.21  2004/01/18 21:45:50  ncq
# - use real lock for thread quit indicator
#
# Revision 1.20  2003/11/17 10:56:35  sjtan
#
# synced and commiting.
#
# Revision 1.1  2003/10/23 06:02:38  sjtan
#
# manual edit areas modelled after r.terry's specs.
#
# Revision 1.19  2003/09/11 10:53:10  ncq
# - fix test code in __main__
#
# Revision 1.18  2003/07/04 20:01:48  ncq
# - remove blocking keyword from acquire() since Python does not like the
#
# Revision 1.17  2003/06/26 04:18:40  ihaywood
# Fixes to gmCfg for commas
#
# Revision 1.16  2003/06/03 13:21:20  ncq
# - still some problems syncing with threads on __del__ when
#   failing in a constructor that sets up threads also
# - slightly better comments in threaded code
#
# Revision 1.15  2003/06/01 12:55:58  sjtan
#
# sql commit may cause PortalClose, whilst connection.commit() doesnt?
#
# Revision 1.14  2003/05/27 15:23:48  ncq
# - Sian found a uncleanliness in releasing the lock
#   during notification registration, clean up his fix
#
# Revision 1.13  2003/05/27 14:38:22  sjtan
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
