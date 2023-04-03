"""GNUmed database backend listener.

This module implements threaded listening for asynchronuous
notifications from the database backend.
"""
#=====================================================================
__author__ = "H. Herb <hherb@gnumed.net>, K.Hilbert <karsten.hilbert@gmx.net>"
__license__ = "GPL v2 or later"

import sys
import time
import threading
import select
import logging


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmDispatcher
from Gnumed.pycommon import gmBorg
#from Gnumed.pycommon import gmLog2


_log = logging.getLogger('gm.db')


signals2listen4 = [
	'db_maintenance_warning',		# warns of impending maintenance and asks for disconnect
	'db_maintenance_disconnect',	# announces a forced disconnect and disconnects
	'gm_table_mod'					# sent for any (registered) table modification, payload contains details
]

#=====================================================================
class gmBackendListener(gmBorg.cBorg):
	"""The backend listener singleton class."""
	def __init__(self, conn=None, poll_interval:int=3):
		try:
			# pylint: disable=access-member-before-definition
			self.already_inited:bool
			return

		except AttributeError:
			pass

		#gmLog2.log_step(restart = True)
		assert conn, '<conn> must be given'

		_log.info('setting up backend notifications listener')
		self.debug = False
		self.__notifications_received = 0
		self.__messages_sent = 0
		# the listener thread will regularly try to acquire
		# this lock, when it succeeds the thread will quit
		self._quit_lock = threading.Lock()
		# take the lock now so it cannot be taken by the worker
		# thread until it is released in shutdown()
		#gmLog2.log_step(message = 'getting quit-lock')
		if not self._quit_lock.acquire(blocking = False):
			_log.error('cannot acquire thread-quit lock, aborting')
			raise EnvironmentError("cannot acquire thread-quit lock")

		#gmLog2.log_step(message = 'got quit-lock')
		self._conn = conn
		_log.debug('DB listener connection: %s', self._conn)
		#gmLog2.log_step(message = 'getting backend PID')
		self.backend_pid = self._conn.get_backend_pid()
		_log.debug('notification listener connection has backend PID [%s]', self.backend_pid)
		self._conn.set_isolation_level(0)		# autocommit mode = psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT
		self._cursor = self._conn.cursor()
		try:
			self._conn_fd = self._conn.fileno()
		except AttributeError:
			self._conn_fd = self._cursor.fileno()
		self._conn_lock = threading.Lock()		# lock for access to connection object
		self.__register_interests()

		# check for messages every 'poll_interval' seconds
		self._poll_interval = poll_interval
		self._listener_thread = None
		self.__start_thread()

		self.already_inited = True
		#gmLog2.log_step(message = 'done with backend listener setup')

	#-------------------------------
	# public API
	#-------------------------------
	def shutdown(self):
		"""Cleanly shut down listening.

		Unregister notifications. Rejoin listener thread.
		"""
		_log.debug('received %s notifications', self.__notifications_received)
		_log.debug('sent %s messages', self.__messages_sent)
		if self._listener_thread is None:
			self.__shutdown_connection()
			return

		_log.info('stopping backend notifications listener thread')
		self._quit_lock.release()
		try:
			# give the worker thread time to terminate
			self._listener_thread.join(self._poll_interval+2.0)
			try:
				if self._listener_thread.is_alive():
					_log.error('listener thread still alive after join()')
					_log.debug('active threads: %s' % threading.enumerate())
			except Exception:
				pass
		except Exception:
			print(sys.exc_info())
		self._listener_thread = None
		try:
			self.__unregister_unspecific_notifications()
		except Exception:
			_log.exception('unable to unregister unspecific notifications')

		self.__shutdown_connection()
		return

	#-------------------------------
	# event handlers
	#-------------------------------
	# internal helpers
	#-------------------------------
	def __register_interests(self):
		#gmLog2.log_step(message = 'registering interests')
		# determine unspecific notifications
		self.unspecific_notifications = signals2listen4
		_log.info('configured unspecific notifications:')
		_log.info('%s' % self.unspecific_notifications)
		gmDispatcher.known_signals.extend(self.unspecific_notifications)
		# listen to unspecific notifications
		self.__register_unspecific_notifications()
		#gmLog2.log_step(message = 'done registering interests')

	#-------------------------------
	def __register_unspecific_notifications(self):
		#gmLog2.log_step(message = 'before')
		for sig in self.unspecific_notifications:
			_log.info('starting to listen for [%s]' % sig)
			cmd = 'LISTEN "%s"' % sig
			self._conn_lock.acquire(blocking = True)
			try:
				self._cursor.execute(cmd)
			finally:
				self._conn_lock.release()
		#gmLog2.log_step(message = 'after')

	#-------------------------------
	def __unregister_unspecific_notifications(self):
		for sig in self.unspecific_notifications:
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
		except Exception:
			pass
		finally:
			self._conn_lock.release()

	#-------------------------------
	def __start_thread(self):
		if self._conn is None:
			raise ValueError("no connection to backend available, useless to start thread")

		#gmLog2.log_step(message = 'setting up thread')
		self._listener_thread = threading.Thread (
			target = self._process_notifications,
			name = self.__class__.__name__,
			daemon = True
		)
		_log.info('starting listener thread')
		self._listener_thread.start()
		#gmLog2.log_step(message = 'started thread')

	#-------------------------------
	def __parse_notification(self, notification) -> dict:
		if self.debug:
			print(notification)
		_log.debug('#%s: %s (first param: PID of sending backend; this backend: %s)', self.__notifications_received, notification, self.backend_pid)
		payload = notification.payload.split('::')
		data = {
			'channel': notification.channel,
			'notification_pid': notification.pid,
			'operation': None,
			'table': None,
			'pk_column_name': None,
			'pk_of_row': None,
			'pk_identity': None
		}
		for item in payload:
			if item.startswith('operation='):
				data['operation'] = item.split('=')[1]
			if item.startswith('table='):
				data['table'] = item.split('=')[1]
			if item.startswith('PK name='):
				data['pk_column_name'] = item.split('=')[1]
			if item.startswith('row PK='):
				data['pk_of_row'] = int(item.split('=')[1])
			if item.startswith('person PK='):
				try:
					data['pk_identity'] = int(item.split('=')[1])
				except ValueError:
					_log.error(payload)
					_log.exception('error in change notification trigger')
					data['pk_identity'] = -1
		return data

	#-------------------------------
	def __send_old_style_table_signal(self, data:dict):
		if data['table'] is None:
			return

		self.__messages_sent += 1
		signal = '%s_mod_db' % data['table']
		_log.debug('emulating old-style table specific signal [%s]', signal)
		try:
			gmDispatcher.send (
				signal = signal,
				originated_in_database = True,
				listener_pid = self.backend_pid,
				sending_backend_pid = data['notification_pid'],
				pk_identity = data['pk_identity'],
				operation = data['operation'],
				table = data['table'],
				pk_column_name = data['pk_column_name'],
				pk_of_row = data['pk_of_row'],
				message_index = self.__messages_sent,
				notification_index = self.__notifications_received
			)
		except Exception:
			print("problem routing notification [%s] from backend [%s] to intra-client dispatcher" % (signal, data['notification_pid']))
			print(sys.exc_info())

	#-------------------------------
	def __send_generic_signal(self, data:dict):
		self.__messages_sent += 1
		try:
			gmDispatcher.send (
				signal = data['channel'],
				originated_in_database = True,
				listener_pid = self.backend_pid,
				sending_backend_pid = data['notification_pid'],
				pk_identity = data['pk_identity'],
				operation = data['operation'],
				table = data['table'],
				pk_column_name = data['pk_column_name'],
				pk_of_row = data['pk_of_row'],
				message_index = self.__messages_sent,
				notification_index = self.__notifications_received
			)
		except Exception:
			print("problem routing notification [%s] from backend [%s] to intra-client dispatcher" % (data['channel'], data['notification_pid']))
			print(sys.exc_info())

	#-------------------------------
	# the actual thread code
	#-------------------------------
	def _process_notifications(self):

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
			self._conn_lock.acquire(1)
			try:
				self._conn.poll()
			finally:
				self._conn_lock.release()
			# any notifications ?
			while len(self._conn.notifies) > 0:
				# if self._quit_lock can be acquired we may be in
				# __del__ in which case gmDispatcher is not
				# guaranteed to exist anymore
				if self._quit_lock.acquire(0):
					_have_quit_lock = 1
					break

				self._conn_lock.acquire(1)
				try:
					notification = self._conn.notifies.pop()
				finally:
					self._conn_lock.release()
				self.__notifications_received += 1
				data = self.__parse_notification(notification)
				# try sending intra-client signals:
				self.__send_generic_signal(data)
				self.__send_old_style_table_signal(data)
				if self._quit_lock.acquire(0):
					# there may be more notifications pendings
					# but we don't care when quitting
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

	from Gnumed.pycommon import gmI18N
	gmI18N.activate_locale()
	gmI18N.install_domain(domain='gnumed')
	from Gnumed.pycommon import gmPG2

	from Gnumed.business import gmPerson, gmPersonSearch

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
			print("\nBackend says: patient data has been modified (%s. notification)" % notifies)
		#-------------------------------
		try:
			n = int(sys.argv[2])
		except Exception:
			print("You can set the number of iterations\nwith the second command line argument")
			n = 100000

		# try loop without backend listener
		print("Looping", n, "times through dummy function")
		i = 0
		t1 = time.time()
		while i < n:
			dummy(i)
			i += 1
		t2 = time.time()
		t_nothreads = t2-t1
		print("Without backend thread, it took", t_nothreads, "seconds")

		listener = gmBackendListener(conn = gmPG2.get_raw_connection())

		# now try with listener to measure impact
		print("Now in a new shell connect psql to the")
		print("database <gnumed_vXX> on localhost, return")
		print("here and hit <enter> to continue.")
		input('hit <enter> when done starting psql')
		print("You now have about 30 seconds to go")
		print("to the psql shell and type")
		print(" notify patient_changed<enter>")
		print("several times.")
		print("This should trigger our backend listening callback.")
		print("You can also try to stop the demo with Ctrl-C !")

		#listener.register_callback('patient_changed', OnPatientModified)

		try:
			counter = 0
			while counter < 20:
				counter += 1
				time.sleep(1)
				sys.stdout.flush()
				print('.')
			print("Looping",n,"times through dummy function")
			i = 0
			t1 = time.time()
			while i < n:
				dummy(i)
				i += 1
			t2 = time.time()
			t_threaded = t2-t1
			print("With backend thread, it took", t_threaded, "seconds")
			print("Difference:", t_threaded-t_nothreads)
		except KeyboardInterrupt:
			print("cancelled by user")

		listener.shutdown()

	#-------------------------------
	def run_monitor():

		print("starting up backend notifications monitor")

		def monitoring_callback(*args, **kwargs):
			try:
				kwargs['originated_in_database']
				print('==> got notification from database "%s":' % kwargs['signal'])
			except KeyError:
				print('==> received signal from client: "%s"' % kwargs['signal'])
			del kwargs['signal']
			for key in kwargs:
				print('    [%s]: %s' % (key, kwargs[key]))

		gmDispatcher.connect(receiver = monitoring_callback)

		listener = gmBackendListener(conn = gmPG2.get_raw_connection())
		print("listening for the following notifications:")
		print("1) unspecific:")
		for sig in listener.unspecific_notifications:
			print('   - %s' % sig)

		while True:
			pat = gmPersonSearch.ask_for_patient()
			if pat is None:
				break
			print("found patient", pat)
			gmPerson.set_active_patient(patient=pat)
			print("now waiting for notifications, hit <ENTER> to select another patient")
			input()

		print("cleanup")
		listener.shutdown()

		print("shutting down backend notifications monitor")

	#-------------------------------
	gmPG2.request_login_params(setup_pool = True, force_tui = True)
	if sys.argv[1] == 'monitor':
		run_monitor()
	else:
		run_test()

#=====================================================================
