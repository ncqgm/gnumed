
from __future__ import print_function

__doc__ = """GNUmed worker threads."""
#=====================================================================
__author__ = "K.Hilbert <karsten.hilbert@gmx.net>"
__license__ = "GPL v2 or later"

import sys
import logging
import threading
import datetime as dt

# wx.CallAfter() does not seem to work with multiprocessing !
#import multiprocessing


if __name__ == '__main__':
	sys.path.insert(0, '../../')


_log = logging.getLogger('gm.worker')

#=====================================================================
def execute_in_worker_thread(payload_function=None, payload_kwargs=None, completion_callback=None):
	"""Create a thread and have it execute <payload_function>.

	<completion_callback> - if not None - better be prepared to
	receive the result of <payload_function>.
	"""
	worker = None

	#-------------------------------
	def _run_payload():
		try:
			if payload_kwargs is None:
				payload_result = payload_function()
			else:
				payload_result = payload_function(**payload_kwargs)
		except StandardError:
			_log.exception('error running worker payload: %s', payload_function)
			return
		_log.debug(u'finished running worker payload')
		if completion_callback is None:
			return
		try:
			completion_callback(payload_result)
		except StandardError:
			_log.exception('error running worker completion callback: %s', completion_callback)
		_log.debug(u'finished running worker completion callback')
		return
	#-------------------------------

	if not callable(payload_function):
		raise ValueError(u'<%s> is not callable', payload_function)
	if completion_callback is not None:
		if not callable(completion_callback):
			raise ValueError(u'<%s> is not callable', completion_callback)
	thread_name = dt.datetime.now().strftime('%f-%H:%M:%S-%Y%m%d')
	_log.info(u'creating thread "%s"', thread_name)
	_log.debug(u' "%s" payload function: %s', thread_name, payload_function)
	_log.debug(u' "%s" results callback: %s', thread_name, completion_callback)

	#worker = multiprocessing.Process (
	worker = threading.Thread (
		target = _run_payload,
		name = thread_name
	)
	worker.start()
	_log.debug(' "%s" PID: %s', worker.name, worker.ident)
	# from here on, another thread executes _run_payload()
	# which executes payload_function(), and possibly
	# completion_callback()

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
