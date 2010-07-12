"""GNUmed database backend listener.

This module implements threaded listening for asynchronuous
notifications from the database backend.
"""
#=====================================================================
__version__ = "$Revision: 1.22 $"
__author__ = "H. Herb <hherb@gnumed.net>, K.Hilbert <karsten.hilbert@gmx.net>"

import sys, time, threading, select, logging


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmDispatcher, gmExceptions, gmBorg


_log = logging.getLogger('gm.db')
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
		# thread until it is released in shutdown()
		if not self._quit_lock.acquire(0):
			_log.error('cannot acquire thread-quit lock ! aborting')
			raise gmExceptions.ConstructorError, "cannot acquire thread-quit lock"

		self._conn = conn
		self.backend_pid = self._conn.get_backend_pid()
		_log.debug('connection has backend PID [%s]', self.backend_pid)
		self._conn.set_isolation_level(0)		# autocommit mode
		self._cursor = self._conn.cursor()
		try:
			self._conn_fd = self._conn.fileno()
		except AttributeError:
			self._conn_fd = self._cursor.fileno()
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
	def shutdown(self):
		if self._listener_thread is None:
			self.__shutdown_connection()
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

		try:
			self.__unregister_patient_notifications()
		except:
			_log.exception('unable to unregister patient notifications')
		try:
			self.__unregister_unspecific_notifications()
		except:
			_log.exception('unable to unregister unspecific notifications')

		self.__shutdown_connection()

		return
	#-------------------------------
	# event handlers
	#-------------------------------
	def _on_pre_patient_selection(self, *args, **kwargs):
		self.__unregister_patient_notifications()
		self.curr_patient_pk = None
	#-------------------------------
	def _on_post_patient_selection(self, *args, **kwargs):
		self.curr_patient_pk = kwargs['pk_identity']
		self.__register_patient_notifications()
	#-------------------------------
	# internal helpers
	#-------------------------------
	def __register_interests(self):

		# determine patient-specific notifications
		cmd = u'SELECT DISTINCT ON (signal) signal FROM gm.notifying_tables WHERE carries_identity_pk IS true'
		self._conn_lock.acquire(1)
		try:
			self._cursor.execute(cmd)
		finally:
			self._conn_lock.release()
		rows = self._cursor.fetchall()
		self.patient_specific_notifications = [ '%s_mod_db' % row[0] for row in rows ]
		_log.info('configured patient specific notifications:')
		_log.info('%s' % self.patient_specific_notifications)
		gmDispatcher.known_signals.extend(self.patient_specific_notifications)

		# determine unspecific notifications
		cmd = u'select distinct on (signal) signal from gm.notifying_tables where carries_identity_pk is False'
		self._conn_lock.acquire(1)
		try:
			self._cursor.execute(cmd)
		finally:
			self._conn_lock.release()
		rows = self._cursor.fetchall()
		self.unspecific_notifications = [ '%s_mod_db' % row[0] for row in rows ]
		self.unspecific_notifications.extend(static_signals)
		_log.info('configured unspecific notifications:')
		_log.info('%s' % self.unspecific_notifications)
		gmDispatcher.known_signals.extend(self.unspecific_notifications)

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
			try:
				self._cursor.execute(cmd)
			finally:
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
			try:
				self._cursor.execute(cmd)
			finally:
				self._conn_lock.release()
	#-------------------------------
	def __register_unspecific_notifications(self):
		for sig in self.unspecific_notifications:
			sig = '%s:' % sig
			_log.info('starting to listen for [%s]' % sig)
			cmd = 'LISTEN "%s"' % sig
			self._conn_lock.acquire(1)
			try:
				self._cursor.execute(cmd)
			finally:
				self._conn_lock.release()
	#-------------------------------
	def __unregister_unspecific_notifications(self):
		for sig in self.unspecific_notifications:
			sig = '%s:' % sig
			_log.info('stopping to listen for [%s]' % sig)
			cmd = 'UNLISTEN "%s"' % sig
			self._conn_lock.acquire(1)
			try:
				self._cursor.execute(cmd)
			finally:
				self._conn_lock.release()
	#-------------------------------
	def __shutdown_connection(self):
		_log.debug('shutting down connection with backend PID [%s]', self.backend_pid)
		self._conn_lock.acquire(1)
		try:
			self._conn.rollback()
			self._conn.close()
		finally:
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

		# get a cursor for this thread
		self._conn_lock.acquire(1)
		try:
			self._cursor_in_thread = self._conn.cursor()
		finally:
			self._conn_lock.release()

		# loop until quitting
		_have_quit_lock = None
		while not _have_quit_lock:

			# quitting ?
			if self._quit_lock.acquire(0):
				break

			# wait at most self._poll_interval for new data
			self._conn_lock.acquire(1)
			try:
				ready_input_sockets = select.select([self._conn_fd], [], [], self._poll_interval)[0]
			finally:
				self._conn_lock.release()

			# any input available ?
			if len(ready_input_sockets) == 0:
				# no, select.select() timed out
				# give others a chance to grab the conn lock (eg listen/unlisten)
				time.sleep(0.3)
				continue

			# data available, wait for it to fully arrive
#			while not self._cursor.isready():
#				pass
			# replace by conn.poll() when psycopg2 2.2 becomes standard
			self._conn_lock.acquire(1)
			try:
				self._cursor_in_thread.execute(u'SELECT 1')
				self._cursor_in_thread.fetchall()
			finally:
				self._conn_lock.release()

			# any notifications ?
			while len(self._conn.notifies) > 0:
				# if self._quit_lock can be acquired we may be in
				# __del__ in which case gmDispatcher is not
				# guarantueed to exist anymore
				if self._quit_lock.acquire(0):
					_have_quit_lock = 1
					break

				self._conn_lock.acquire(1)
				try:
					notification = self._conn.notifies.pop()
				finally:
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

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] not in ['test', 'monitor']:
		sys.exit()


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
			while counter < 20:
				counter += 1
				time.sleep(1)
				sys.stdout.flush()
				print '.',
			print "Looping",n,"times through dummy function"
			i = 0
			t1 = time.time()
			while i < n:
				r = dummy(i)
				i += 1
			t2 = time.time()
			t_threaded = t2-t1
			print "With backend thread, it took", t_threaded, "seconds"
			print "Difference:", t_threaded-t_nothreads
		except KeyboardInterrupt:
			print "cancelled by user"

		listener.shutdown()
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
		listener.shutdown()

		print "shutting down backend notifications monitor"

	#-------------------------------
	if sys.argv[1] == 'monitor':
		run_monitor()
	else:
		run_test()

#=====================================================================
