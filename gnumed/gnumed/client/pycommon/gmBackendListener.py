"""GNUmed database backend listener.

This module implements threaded listening for asynchronuous
notifications from the database backend.
"""
#=====================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/pycommon/gmBackendListener.py,v $
__version__ = "$Revision: 1.18 $"
__author__ = "H. Herb <hherb@gnumed.net>, K.Hilbert <karsten.hilbert@gmx.net>"

import sys, time, threading, select, logging


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmDispatcher, gmExceptions, gmBorg


_log = logging.getLogger('gm.database')
_log.info(__version__)


static_signals = [
	u'db_maintenance_warning',		# warns of impending maintenance and asks for disconnect
	u'db_maintenance_disconnect'	# announces a forced disconnect and disconnects
]
#=====================================================================
class gmBackendListener(gmBorg.cBorg):

	def __init__(self, conn=None, poll_interval=3, patient=None):

		try:
			self.already_inited
			return
		except AttributeError:
			pass

		_log.info('starting backend notifications listener thread')

		# the listener thread will regularly try to acquire
		# this lock, when it succeeds it will quit
		self._quit_lock = threading.Lock()
		# take the lock now so it cannot be taken by the worker
		# thread until it is released in stop_thread()
		if not self._quit_lock.acquire(0):
			_log.error('cannot acquire thread quit lock !?! aborting')
			raise gmExceptions.ConstructorError, "cannot acquire thread quit-lock"

		self._conn = conn
		self._conn.set_isolation_level(0)
		self._cursor = self._conn.cursor()
		self._conn_lock = threading.Lock()		# lock for access to connection object

		self.curr_patient_pk = None
		if patient is not None:
			if patient.connected:
				self.curr_patient_pk = patient.ID
		self.__register_interests()

		# check for messages every 'poll_interval' seconds
		self._poll_interval = poll_interval
		self._listener_thread = None
		self.__start_thread()

		self.already_inited = True
	#-------------------------------
	# public API
	#-------------------------------
	def stop_thread(self):
		if self._listener_thread is None:
			return

		_log.info('stopping backend notifications listener thread')
		self._quit_lock.release()
		try:
			# give the worker thread time to terminate
			self._listener_thread.join(self._poll_interval+2.0)
			try:
				if self._listener_thread.isAlive():
					_log.error('listener thread still alive after join()')
					_log.debug('active threads: %s' % threading.enumerate())
			except:
				pass
		except:
			print sys.exc_info()

		self._listener_thread = None

		self.__unregister_patient_notifications()
		self.__unregister_unspecific_notifications()

		return
	#-------------------------------
	# event handlers
	#-------------------------------
	def _on_pre_patient_selection(self, *args, **kwargs):
		self.__unregister_patient_notifications()
		self.curr_patient_pk = None
	#-------------------------------
	def _on_post_patient_selection(self, *args, **kwargs):
		self.curr_patient_pk = kwargs['patient'].ID
		self.__register_patient_notifications()
	#-------------------------------
	# internal helpers
	#-------------------------------
	def __register_interests(self):

		# determine patient-specific notifications
		cmd = u'select distinct on (signal) signal from gm.notifying_tables where carries_identity_pk is True'
		self._conn_lock.acquire(1)
		self._cursor.execute(cmd)
		self._conn_lock.release()
		rows = self._cursor.fetchall()
		self.patient_specific_notifications = [ '%s_mod_db' % row[0] for row in rows ]
		_log.info('configured patient specific notifications:')
		_log.info('%s' % self.patient_specific_notifications)
		gmDispatcher.known_signals.extend(self.patient_specific_notifications)

		# determine unspecific notifications
		cmd = u'select distinct on (signal) signal from gm.notifying_tables where carries_identity_pk is False'
		self._conn_lock.acquire(1)
		self._cursor.execute(cmd)
		self._conn_lock.release()
		rows = self._cursor.fetchall()
		self.unspecific_notifications = [ '%s_mod_db' % row[0] for row in rows ]
		self.unspecific_notifications.extend(static_signals)
		_log.info('configured unspecific notifications:')
		_log.info('%s' % self.unspecific_notifications)
		gmDispatcher.known_signals.extend(self.unspecific_notifications)

		# determine our backend PID
		cmd = u'select pg_backend_pid()'
		self._conn_lock.acquire(1)
		self._cursor.execute(cmd)
		self._conn_lock.release()
		rows = self._cursor.fetchall()
		self.backend_pid = rows[0][0]
		_log.info('listener process PID: [%s]' % self.backend_pid)

		# listen to patient changes inside the local client
		# so we can re-register patient specific notifications
		gmDispatcher.connect(signal = u'pre_patient_selection', receiver = self._on_pre_patient_selection)
		gmDispatcher.connect(signal = u'post_patient_selection', receiver = self._on_post_patient_selection)

		# do we need to start listening to patient specific
		# notifications right away because we missed an
		# earlier patient activation ?
		self.__register_patient_notifications()

		# listen to unspecific (non-patient related) notifications
		self.__register_unspecific_notifications()
	#-------------------------------
	def __register_patient_notifications(self):
		if self.curr_patient_pk is None:
			return
		for notification in self.patient_specific_notifications:
			notification = '%s:%s' % (notification, self.curr_patient_pk)
			_log.debug('starting to listen for [%s]' % notification)
			cmd = 'LISTEN "%s"' % notification
			self._conn_lock.acquire(1)
			self._cursor.execute(cmd)
			self._conn_lock.release()
	#-------------------------------
	def __unregister_patient_notifications(self):
		if self.curr_patient_pk is None:
			return
		for notification in self.patient_specific_notifications:
			notification = '%s:%s' % (notification, self.curr_patient_pk)
			_log.debug('stopping to listen for [%s]' % notification)
			cmd = 'UNLISTEN "%s"' % notification
			self._conn_lock.acquire(1)
			self._cursor.execute(cmd)
			self._conn_lock.release()
	#-------------------------------
	def __register_unspecific_notifications(self):
		for sig in self.unspecific_notifications:
			sig = '%s:' % sig
			_log.info('starting to listen for [%s]' % sig)
			cmd = 'LISTEN "%s"' % sig
			self._conn_lock.acquire(1)
			self._cursor.execute(cmd)
			self._conn_lock.release()
	#-------------------------------
	def __unregister_unspecific_notifications(self):
		for sig in self.unspecific_notifications:
			sig = '%s:' % sig
			_log.info('stopping to listen for [%s]' % sig)
			cmd = 'UNLISTEN "%s"' % sig
			self._conn_lock.acquire(1)
			self._cursor.execute(cmd)
			self._conn_lock.release()
	#-------------------------------
	def __start_thread(self):
		if self._conn is None:
			raise ValueError("no connection to backend available, useless to start thread")

		self._listener_thread = threading.Thread (
			target = self._process_notifications,
			name = self.__class__.__name__
		)
		self._listener_thread.setDaemon(True)
		_log.info('starting listener thread')
		self._listener_thread.start()
	#-------------------------------
	# the actual thread code
	#-------------------------------
	def _process_notifications(self):
		_have_quit_lock = None
		while not _have_quit_lock:
			if self._quit_lock.acquire(0):
				break
			# wait at most self._poll_interval for new data
			self._conn_lock.acquire(1)
			ready_input_sockets = select.select([self._cursor], [], [], self._poll_interval)[0]
			self._conn_lock.release()
			# any input available ?
			if len(ready_input_sockets) == 0:
				# no, select.select() timed out
				# give others a chance to grab the conn lock (eg listen/unlisten)
				time.sleep(0.3)
				continue
			# data available, wait for it to fully arrive
			while not self._cursor.isready():
				pass
			# any notifications ?
			while len(self._conn.notifies) > 0:
				# if self._quit_lock can be acquired we may be in
				# __del__ in which case gmDispatcher is not
				# guarantueed to exist anymore
				if self._quit_lock.acquire(0):
					_have_quit_lock = 1
					break

				self._conn_lock.acquire(1)
				notification = self._conn.notifies.pop()
				self._conn_lock.release()
				# try sending intra-client signal
				pid, full_signal = notification
				signal_name, pk = full_signal.split(':')
				try:
					results = gmDispatcher.send (
						signal = signal_name,
						originated_in_database = True,
						listener_pid = self.backend_pid,
						sending_backend_pid = pid,
						pk_identity = pk
					)
				except:
					print "problem routing notification [%s] from backend [%s] to intra-client dispatcher" % (full_signal, pid)
					print sys.exc_info()

				# there *may* be more pending notifications but do we care ?
				if self._quit_lock.acquire(0):
					_have_quit_lock = 1
					break

		# exit thread activity
		return
#=====================================================================
# main
#=====================================================================
if __name__ == "__main__":

	notifies = 0

	from Gnumed.pycommon import gmPG2, gmI18N
	from Gnumed.business import gmPerson

	gmI18N.activate_locale()
	gmI18N.install_domain(domain='gnumed')
	#-------------------------------
	def run_test():

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
			n = int(sys.argv[2])
		except:
			print "You can set the number of iterations\nwith the second command line argument"
			n = 100000

		# try loop without backend listener
		print "Looping", n, "times through dummy function"
		i = 0
		t1 = time.time()
		while i < n:
			r = dummy(i)
			i += 1
		t2 = time.time()
		t_nothreads = t2-t1
		print "Without backend thread, it took", t_nothreads, "seconds"

		listener = gmBackendListener(conn = gmPG2.get_raw_connection())

		# now try with listener to measure impact
		print "Now in a new shell connect psql to the"
		print "database <gnumed_v9> on localhost, return"
		print "here and hit <enter> to continue."
		raw_input('hit <enter> when done starting psql')
		print "You now have about 30 seconds to go"
		print "to the psql shell and type"
		print " notify patient_changed<enter>"
		print "several times."
		print "This should trigger our backend listening callback."
		print "You can also try to stop the demo with Ctrl-C !"

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
	#-------------------------------
	def run_monitor():

		print "starting up backend notifications monitor"

		def monitoring_callback(*args, **kwargs):
			try:
				kwargs['originated_in_database']
				print '==> got notification from database "%s":' % kwargs['signal']
			except KeyError:
				print '==> received signal from client: "%s"' % kwargs['signal']
			del kwargs['signal']
			for key in kwargs.keys():
				print '    [%s]: %s' % (key, kwargs[key])

		gmDispatcher.connect(receiver = monitoring_callback)

		listener = gmBackendListener(conn = gmPG2.get_raw_connection())
		print "listening for the following notifications:"
		print "1) patient specific (patient #%s):" % listener.curr_patient_pk
		for sig in listener.patient_specific_notifications:
			print '   - %s' % sig
		print "1) unspecific:"
		for sig in listener.unspecific_notifications:
			print '   - %s' % sig

		while True:
			pat = gmPerson.ask_for_patient()
			if pat is None:
				break
			print "found patient", pat
			gmPerson.set_active_patient(patient=pat)
			print "now waiting for notifications, hit <ENTER> to select another patient"
			raw_input()

		print "cleanup"
		listener.stop_thread()

		print "shutting down backend notifications monitor"
	#-------------------------------
	if len(sys.argv) > 1:
		if sys.argv[1] == 'test':
			run_test()
		if sys.argv[1] == 'monitor':
			run_monitor()

#=====================================================================
# $Log: gmBackendListener.py,v $
# Revision 1.18  2008-07-07 13:39:47  ncq
# - current patient .connected
#
# Revision 1.17  2008/06/15 20:17:17  ncq
# - be even more careful rejoining worker threads
#
# Revision 1.16  2008/04/28 13:31:16  ncq
# - now static signals for database maintenance
#
# Revision 1.15  2008/01/07 19:48:22  ncq
# - bump db version
#
# Revision 1.14  2007/12/12 16:17:15  ncq
# - better logger names
#
# Revision 1.13  2007/12/11 14:16:29  ncq
# - cleanup
# - use logging
#
# Revision 1.12  2007/10/30 12:48:17  ncq
# - attach_identity_pk -> carries_identity_pk
#
# Revision 1.11  2007/10/25 12:18:37  ncq
# - cleanup
# - include listener backend pid in signal data
#
# Revision 1.10  2007/10/23 21:22:42  ncq
# - completely redone:
#   - use psycopg2
#   - handle signals based on backend metadata
#   - add monitor to test cases
#
# Revision 1.9  2006/05/24 12:50:21  ncq
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
