"""GnuMed database backend listener.

This module implements listening for asynchronuous
notifications from the database backend.

NOTE !  This is specific to the DB adapter pyPgSQL and
        not DB-API compliant !
"""
#=====================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/python-common/Attic/gmBackendListener.py,v $
__version__ = "$Revision: 1.8 $"
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
	#-------------------------------
	#def __del__(self):
	#	self.__quit=1
		#give the thread time to terminate
	#	time.sleep(self._poll_interval+2)

	#-------------------------------
	# public API
	#-------------------------------
	def register_callback(self, aSignal, aCallback):
		if not self._thread_running:
			self.__start_thread()
		# don't listen twice to the same signal
		# FIXME: but we DO want to connect another callback !!
		if aSignal in self._intercepted_signals:
			return
		#tell the backend to notify us on this signal
		res = self._conn.query('LISTEN %s' % signal)
		if res.resultStatus != libpq.COMMAND_OK:
			raise libpq.Error, "ERROR: command failed"

		self._intercepted_signals.append(aSignal)
		# connect the signal with the callback function
		gmDispatcher.connect(receiver = aCallback, signal = aSignal)
	#-------------------------------
	def tell_thread_to_stop(self):
		self._quit = 1
	#-------------------------------
	# internal helpers
	#-------------------------------
	def __connect(self, database, user, password, host='localhost', port=5432):
		cnx=None
		try:
			constr="dbname='%s' user='%s' password='%s' host='%s' port=%d" % (database, user, password, host, port)
			#print constr
			cnx = libpq.PQconnectdb(constr)
		except libpq.Error, msg:
			exc = sys.exc_info()
			_log.LogException("Connection to database '%s' failed: %s" % (database, msg), exc, fatal=0)
		return cnx
	#-------------------------------
	def __start_thread(self):
		if self._conn is None:
			_log.Log(gmLog.lErr, "Can't start thread. No connection to backend available.")
			return None
		sys.stdout.flush()
		t = threading.Thread(target = self._process_signals)
		self._thread_running = 1
		t.start()
	#-------------------------------
	def _process_signals(self):
		while 1:
			ready_sockets = select.select([self._conn.socket], [], [], 1.0)[0]
			if len(ready_sockets):
				self._conn.consumeInput()
				note = self._conn.notifies()
				while note:
					sys.stdout.flush()
					gmDispatcher.send(signal = note.relname, sender = self._service)
					if self._quit:
						break
					note = self._conn.notifies()
			else:
				time.sleep(self._poll_interval)
			if self._quit:
				self._thread_running=0
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
# Revision 1.8  2003-04-25 13:00:43  ncq
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
