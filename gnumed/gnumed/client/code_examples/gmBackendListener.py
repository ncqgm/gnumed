import sys, time, threading
import select
from pyPgSQL import libpq
import gmDispatcher

class BackendListener:
	def __init__(self, database, user, password, host='localhost', port=5432):
		self._cnx = self.Connect(database, user, password, host, port)
		self.listeningfor = []
		self._feedback = {}	
		self.ListeningThread()
		self._quit=0
		
	def Stop(self):
		self._quit=1				
		
	def Connect(self, database, user, password, host='localhost', port=5432):
		try:
			cnx = libpq.PQconnectdb('dbname=%s' % database)
		except libpq.Error, msg:
			print "Connection to database '%s' failed" % database
			print msg
		return cnx

		
	def ListeningThread(self):
		if self._cnx is None:
			return
		sys.stdout.flush()
		print "firing up thread ..."
		t = threading.Thread(target=self.Listen)
		t.start()
		print "thread has been started"		

	def Listen(self):
		while 1:
			sys.stdout.flush()
			print '-',
			ready_sockets = select.select([self._cnx.socket], [], [], 1.0)[0]
			if len(ready_sockets):
				self._cnx.consumeInput()
				note = self._cnx.notifies()
				while note:
					sys.stdout.flush()
					print '+'
					gmDispatcher.send(note.relname, sender=None)
					note = self._cnx.notifies()
					if self._quit:
						break
			if self._quit:
				break
				
					
	def RegisterForFeedback(self, whatfor, callback):
		"""When notification 'whatfor' is received from backend, callback is executed
		   whatfor is a string, callback is a function with no parameters"""
		if self._cnx is None:
			return 0
		#hook up the event handling
		gmDispatcher.connect(callback, whatfor)
		#do not create redundant listeners; one per possible notification is enough
		if whatfor in self.listeningfor:
			return
		self.listeningfor.append(whatfor)
		try:
			res = self._cnx.query('LISTEN %s' % whatfor)
			if res.resultStatus != libpq.COMMAND_OK:
				raise libpq.Error, "ERROR: command failed"
		except libpq.Error, msg:
			print "LISTEN command failed"
		
			
			
if __name__ == "__main__":

	def OnPatientSelected():
		sys.stdout.flush()
		print "\nBackend says: patient data has been modified"

	print "this demo will self-terminate in approx. 30 secs."
	print "or you can try to stop it with Ctrl-C!"		
	listener = BackendListener(database='gnumed', user='hherb', password='')
	print "Now fire up psql in a new shell, and type 'notify patient_changed'"
	try:
		listener.RegisterForFeedback('patient_changed', OnPatientSelected)
		counter = 0
		while counter<30:
			counter += 1
			time.sleep(1)
			sys.stdout.flush()
			print '.',
		listener.Stop()
	except KeyboardInterrupt:
		listener.Stop()
