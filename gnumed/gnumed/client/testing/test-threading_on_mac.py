import threading, time


class ThreadRunner:

	def __init__(self):
		self.lock = threading.Lock()
		self.get_lock()

	def get_lock(self):
		self.lock.acquire(1)
		print "got lock in foreground thread"
		self.lock.release()

	def start_thread(self):
		self._listener_thread = threading.Thread (
			target = self.thread_code,
			name = self.__class__.__name__
		)
		self._listener_thread.setDaemon(True)
		self._listener_thread.start()

	def thread_code(self):
		print "starting to run background thread"
		while True:
			time.sleep(2)
			self.lock.acquire(1)
			print "got lock in background thread"
			self.lock.release()



t = ThreadRunner()
t.get_lock()
t.start_thread()

for idx in range(20):
	time.sleep(1)
	print idx
	t.get_lock()
