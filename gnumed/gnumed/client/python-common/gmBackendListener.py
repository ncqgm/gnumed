import sys, time, threading
import select
from pyPgSQL import libpq
import gmDispatcher

class BackendListener:
	def __init__(self, service, database, user, password, host='localhost', port=5432, poll_interval = 3):
		#when self._quit is true, the thread is stopped
		self._quit=0
		#remeber what signals we are listening for; no need to listen twice to the same signal
		self._signals = []
		#remeber what service we are representing
		self._service = service
		#check for messages every 'poll_interval' seconds
		self._poll_interval = poll_interval
		#is the thread runnning already?
		self._thread_running=0
		#connect to the backend
		self._cnx = self.Connect(database, user, password, host, port)
		
		
	#def __del__(self):
	#	self.__quit=1
		#give the thread time to terminate
	#	time.sleep(self._poll_interval+2)

				
	def Stop(self):
		self._quit=1				

				
	def Connect(self, database, user, password, host='localhost', port=5432):
		cnx=None
		try:
			constr="dbname='%s' user='%s' password='%s' host='%s' port=%d" % (database, user, password, host, port)
			#print constr
			cnx = libpq.PQconnectdb(constr)
		except libpq.Error, msg:
			print "Connection to database '%s' failed" % database
			print msg
		return cnx

		
	def ListeningThread(self):
		if self._cnx is None:
			print "Can't start thread - connection to backend failed!"
			return
		sys.stdout.flush()
		t = threading.Thread(target=self.Listen)
		self._thread_running=1
		t.start()


	def Listen(self):
		while 1:
			ready_sockets = select.select([self._cnx.socket], [], [], 1.0)[0]
			if len(ready_sockets):
				self._cnx.consumeInput()
				note = self._cnx.notifies()
				while note:
					sys.stdout.flush()
					print '+'
					gmDispatcher.send(note.relname, sender=self._service)
					note = self._cnx.notifies()
					if self._quit:
						break
			else:
				time.sleep(self._poll_interval)
			if self._quit:
				self._thread_running=0
				break
				
				
	def RegisterCallback(self, callback, signal):
		#start the listener thread if not already started
		if not self._thread_running:
			self.ListeningThread()
		#don't try to listen twice to the same signal
		if signal in self._signals:
			return
		#remember that we are listening to this signal
		self._signals.append(signal)
		#tell the backend to notify us on this signal
		res = self._cnx.query('LISTEN %s' % signal)
		if res.resultStatus != libpq.COMMAND_OK:
			raise libpq.Error, "ERROR: command failed"
		#connect the signal with the callback function
		gmDispatcher.connect(callback, signal)

									
			
if __name__ == "__main__":
	
	import time
	
	def dummy(n):
		return float(n)*n/float(1+n)
	
	try:
		n = int(sys.argv[1])
	except:
		n= 100000
		
	print "Looping",n,"times through dummy function"
	i=0
	t1 = time.time()
	while i<n:
		r = dummy(i)
		i+=1
	t2=time.time()
	t_nothreads=t2-t1
	print "Without backend thread, it took", t_nothreads, "seconds"

	def OnPatientSelected():
		sys.stdout.flush()
		print "\nBackend says: patient data has been modified"

		
	print "this demo will self-terminate in approx. 30 secs."
	print "or you can try to stop it with Ctrl-C!"		
	listener = BackendListener(service='default', database='gnumed', user='hherb', password='')
	listener.RegisterCallback(OnPatientSelected, 'patient_changed')
	print "Now fire up psql in a new shell, and type 'notify patient_changed'"
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

		listener.Stop()
	except KeyboardInterrupt:
		listener.Stop()
