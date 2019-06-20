__doc__ = """GNUmed worker threads."""
#=====================================================================
__author__ = "K.Hilbert <karsten.hilbert@gmx.net>"
__license__ = "GPL v2 or later"

import sys
import logging
import threading
import datetime as dt
import copy

# wx.CallAfter() does not seem to work with multiprocessing !
#import multiprocessing


if __name__ == '__main__':
	sys.path.insert(0, '../../')


_log = logging.getLogger('gm.worker')

#=====================================================================
def execute_in_worker_thread(payload_function=None, payload_kwargs=None, completion_callback=None, worker_name=None):
	"""Create a thread and have it execute <payload_function>.

	<completion_callback> - if not None - better be prepared to
	receive the result of <payload_function>.
	"""
	_log.debug('worker [%s]', worker_name)
	# decouple from calling thread
	__payload_kwargs = copy.deepcopy(payload_kwargs)

	worker_thread = None

	#-------------------------------
	def _run_payload():
		try:
			if payload_kwargs is None:
				payload_result = payload_function()
			else:
				payload_result = payload_function(**__payload_kwargs)
			_log.debug('finished running payload function: %s', payload_function)
		except Exception:
			_log.exception('error running payload function: %s', payload_function)
			return
		if completion_callback is None:
			return
		try:
			completion_callback(payload_result)
			_log.debug('finished running completion callback')
		except Exception:
			_log.exception('error running completion callback: %s', completion_callback)
		_log.info('worker thread [name=%s, PID=%s] shuts down', worker_thread.name, worker_thread.ident)
		return
	#-------------------------------

	if not callable(payload_function):
		raise ValueError('<%s> is not callable', payload_function)
	if completion_callback is not None:
		if not callable(completion_callback):
			raise ValueError('<%s> is not callable', completion_callback)
	if worker_name is None:
		__thread_name = dt.datetime.now().strftime('%f-%S')
	else:
		__thread_name = '%sThread-%s' % (
			worker_name,
			dt.datetime.now().strftime('%f')
		)
	_log.debug('creating thread "%s"', __thread_name)
	_log.debug(' "%s" payload function: %s', __thread_name, payload_function)
	_log.debug(' "%s" results callback: %s', __thread_name, completion_callback)
	#worker_thread = multiprocessing.Process (
	worker_thread = threading.Thread (
		target = _run_payload,
		name = __thread_name
	)
	# we don't want hung workers to prevent us from exiting GNUmed
	worker_thread.daemon = True
	_log.info('starting thread "%s"', __thread_name)
	worker_thread.start()
	_log.debug(' "%s" ident (= PID): %s', worker_thread.name, worker_thread.ident)
	# from here on, another thread executes _run_payload()
	# which executes payload_function() and, eventually,
	# completion_callback() if available,
	# return thread ident so people can join() it if needed
	return worker_thread.ident

#=====================================================================
# main
#=====================================================================
if __name__ == "__main__":

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	import time
	import random

	from Gnumed.pycommon import gmLog2

	def test_print_dots(ident=None):

		def slowly_print_dots(info=None):
			for i in range(5):
				print('* (#%s in %s)' % (i, info))
				time.sleep(1 + (random.random()*4))
			return '%s' % time.localtime()

		def print_dot_end_time(time_str):
			print('done: %s' % time_str)

		execute_in_worker_thread (
			payload_function = slowly_print_dots,
			payload_kwargs = {'info': ident},
			completion_callback = print_dot_end_time
		)

	test_print_dots('A')
	test_print_dots('B')
