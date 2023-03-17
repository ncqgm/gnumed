"""GNUmed worker threads.

wx.CallAfter() does not seem to work with _multiprocessing_ !
"""
#=====================================================================
__author__ = "K.Hilbert <karsten.hilbert@gmx.net>"
__license__ = "GPL v2 or later"

import sys
import logging
import threading
import datetime as dt
import pickle
import copy


if __name__ == '__main__':
	sys.path.insert(0, '../../')


_log = logging.getLogger('gm.worker')

#=====================================================================
def execute_in_worker_thread(payload_function=None, payload_kwargs:dict=None, completion_callback=None, worker_name:str=None) -> int:
	"""Create a thread and have it execute "payload_function".

	Args:
		payload_function: function to actually run in the thread
		payload_kwargs: keyword arguments to pass to "payload_function"
		completion_callback: must be able to consume the results of "payload_function" unless "None"
		worker_name: optional worker thread name

	Returns:
		ID of worker thread
	"""
	assert (callable(payload_function)), 'payload function <%s> is not callable' % payload_function
	assert ((completion_callback is None) or callable(completion_callback)), 'completion callback <%s> is not callable' % completion_callback

	_log.debug('worker [%s]', worker_name)
	# try to decouple from calling thread
	try:
		__payload_kwargs = copy.deepcopy(payload_kwargs)
	except (copy.error, pickle.PickleError):
		_log.exception('failed to copy.deepcopy(payload_kwargs): %s', payload_kwargs)
		_log.error('using shallow copy and hoping for the best')
		__payload_kwargs = copy.copy(payload_kwargs)
	worker_thread = None

	#-------------------------------
	def _run_payload():
		"""Execute the payload function.

		Defined inline so it can locally access arguments and the completion callback.
		"""
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

	def test_print_dots(ident=None):
		"""Tests executing a function in a worker thread.

		The thread slowly prints dots to stdout.
		"""

		def slowly_print_dots(info=None):
			"""This slowly prints dots.

			:param str info: some identifier

			To be run in each thread."""
			for idx in range(5):
				print('* (#%s in %s)' % (idx, info))
				time.sleep(1 + (random.random()*4))
			return '%s' % time.localtime()

		def print_dot_end_time(end_time):
			"""Print the time printing dots ended.

			:param str end_time: end time to print

			Used as completion callback."""
			print('done: %s' % end_time)

		execute_in_worker_thread (
			payload_function = slowly_print_dots,
			payload_kwargs = {'info': ident},
			completion_callback = print_dot_end_time
		)

	test_print_dots('A')
	test_print_dots('B')
