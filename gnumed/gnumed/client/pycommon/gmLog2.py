"""GNUmed logging framework setup.

All error logging, user notification and otherwise unhandled 
exception handling should go through classes or functions of 
this module.

Theory of operation:

This module tailors the standard logging framework to
the needs of GNUmed.

By importing gmLog2 into your code you'll get the root
logger send to a unicode file with messages in a format useful
for debugging. The filename is either taken from the
command line (--log-file=...) or derived from the name
of the main application.

The log file will be found in one of the following standard
locations:

1) given on the command line as "--log-file=LOGFILE"
2) ~/.<base_name>/<base_name>.log
3) /dir/of/binary/<base_name>.log		(mainly for DOS/Windows)

where <base_name> is derived from the name
of the main application.

If you want to specify just a directory for the log file you
must end the --log-file definition with a slash.

By importing "logging" and getting a logger your modules
never need to worry about the real message destination or whether
at any given time there's a valid logger available.

Your MAIN module simply imports gmLog2 and all other modules
will merrily and automagically start logging away.


Ad hoc call stack logging recipe:

	call_stack = inspect.stack()
	call_stack.reverse()
	for idx in range(1, len(call_stack)):
		caller = call_stack[idx]
		_log.debug('%s[%s] @ [%s] in [%s]', ' '* idx, caller[3], caller[2], caller[1])
	del call_stack
"""
# TODO:
# - exception()
# - ascii_ctrl2mnemonic()
#========================================================================
__author__  = "K. Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL v2 or later (details at https://www.gnu.org)"


# stdlib
import logging
import sys
import os
import datetime as pydt
import random


_logfile_name = None
_logfile = None


# table used for cooking non-printables
AsciiName = ['<#0-0x00-nul>',
			 '<#1-0x01-soh>',
			 '<#2-0x02-stx>',
			 '<#3-0x03-etx>',
			 '<#4-0x04-eot>',
			 '<#5-0x05-enq>',
			 '<#6-0x06-ack>',
			 '<#7-0x07-bel>',
			 '<#8-0x08-bs>',
			 '<#9-0x09-ht>',
			 '<#10-0x0A-lf>',
			 '<#11-0x0B-vt>',
			 '<#12-0x0C-ff>',
			 '<#13-0x0D-cr>',
			 '<#14-0x0E-so>',
			 '<#15-0x0F-si>',
			 '<#16-0x10-dle>',
			 '<#17-0x11-dc1/xon>',
			 '<#18-0x12-dc2>',
			 '<#19-0x13-dc3/xoff>',
			 '<#20-0x14-dc4>',
			 '<#21-0x15-nak>',
			 '<#22-0x16-syn>',
			 '<#23-0x17-etb>',
			 '<#24-0x18-can>',
			 '<#25-0x19-em>',
			 '<#26-0x1A-sub>',
			 '<#27-0x1B-esc>',
			 '<#28-0x1C-fs>',
			 '<#29-0x1D-gs>',
			 '<#30-0x1E-rs>',
			 '<#31-0x1F-us>'
			]

# msg = reduce(lambda x, y: x+y, (map(self.__char2AsciiName, list(tmp))), '')
#
#	def __char2AsciiName(self, aChar):
#		try:
#			return AsciiName[ord(aChar)]
#		except IndexError:
#			return aChar
#
#	def __tracestack(self):
#		"""extract data from the current execution stack
#
#		this is rather fragile, I guess
#		"""
#		stack = traceback.extract_stack()
#		self.__modulename = stack[-4][0]
#		self.__linenumber = stack[-4][1]
#		self.__functionname = stack[-4][2]
#		if (self.__functionname == "?"):
#			self.__functionname = "Main"

#===============================================================
# external API
#===============================================================
def flush():
	"""Log a <synced> line and flush handlers."""
	logger = logging.getLogger('gm.logging')
	logger.critical('-------- synced log file -------------------------------')
	root_logger = logging.getLogger()
	for handler in root_logger.handlers:
		handler.flush()

#===============================================================
def log_instance_state(instance):
	"""Log the state of a class instance."""
	logger = logging.getLogger('gm.logging')
	logger.debug('state of %s', instance)
	for attr in [ a for a in dir(instance) if not a.startswith('__') ]:
		try:
			val = getattr(instance, attr)
		except AttributeError:
			val = '<cannot access>'
		logger.debug('  %s: %s', attr, val)

#===============================================================
def log_stack_trace(message:str=None, t=None, v=None, tb=None):
	"""Log exception details and stack trace.

	(t,v,tb) are what sys.exc_info() returns.

	If any of (t,v,tb) is None it is attempted to be
	retrieved from sys.exc_info().

	Args:
		message: arbitrary message to add in
		t: an exception type
		v: an exception value
		tb: a traceback object
	"""

	logger = logging.getLogger('gm.logging')

	if t is None:
		t = sys.exc_info()[0]
	if v is None:
		v = sys.exc_info()[1]
	if tb is None:
		tb = sys.exc_info()[2]
	if tb is None:
		logger.debug('sys.exc_info() did not return a traceback object, trying sys.last_traceback')
		try:
			tb = sys.last_traceback
		except AttributeError:
			logger.debug('no stack to trace (no exception information available)')
			return

	# log exception details
	logger.debug('exception: %s', v)
	logger.debug('type: %s', t)
	logger.debug('list of attributes:')
	for attr in [ a for a in dir(v) if not a.startswith('__') ]:
		try:
			val = getattr(v, attr)
		except AttributeError:
			val = '<cannot access>'
		logger.debug('  %s: %s', attr, val)

	# make sure we don't leave behind a binding
	# to the traceback as warned against in
	# sys.exc_info() documentation
	try:
		# recurse back to root caller
		while 1:
			if not tb.tb_next:
				break
			tb = tb.tb_next
		# put the frames on a stack
		stack_of_frames = []
		frame = tb.tb_frame
		while frame:
			stack_of_frames.append(frame)
			frame = frame.f_back
	finally:
		del tb
	stack_of_frames.reverse()

	if message is not None:
		logger.debug(message)
	logger.debug('stack trace follows:')
	logger.debug('(locals by frame, outmost frame first)')
	for frame in stack_of_frames:
		logger.debug (
			'--- frame [%s]: #%s, %s -------------------',
			frame.f_code.co_name,
			frame.f_lineno,
			frame.f_code.co_filename
		)
		for varname, value in frame.f_locals.items():
			if varname == '__doc__':
				continue
			logger.debug('%20s = %s', varname, value)

#---------------------------------------------------------------
def log_multiline(level, message:str=None, line_prefix:str=None, text:str=None):
	"""Log multi-line text in a standard format.

	Args:
		level: a log level
		message: an arbitrary message to add in
		line_prefix: a string to prefix lines with
		text: the multi-line text to log
	"""
	if text is None:
		return

	if message is None:
		message = 'multiline text:'
	if line_prefix is None:
		line_template = '  > %s'
	else:
		line_template = '%s: %%s' % line_prefix
	lines2log = [message]
	lines2log.extend([ line_template % line for line in text.split('\n') ])
	logger = logging.getLogger('gm.logging')
	logger.log(level, '\n'.join(lines2log))

#---------------------------------------------------------------
__current_log_step = 1

def log_step(level:int=logging.DEBUG, message:str=None, restart:bool=False):
	if restart:
		global __current_log_step
		__current_log_step = 1
	logger = logging.getLogger('gm.logging')
	if message:
		logger.log(level, '%s - %s', __current_log_step, message)
	else:
		logger.log(level, '%s', __current_log_step)
	__current_log_step += 1

#===============================================================
# internal API
#===============================================================
__words2hide = []

def add_word2hide(word:str):
	"""Add a string to the list of strings to be scrubbed from logging output.

	Useful for hiding credentials etc.
	"""
	if word is None:
		return

	if word.strip() == '':
		return

	if word not in __words2hide:
		__words2hide.append(str(word))

#---------------------------------------------------------------
__original_logger_write_func = None

def __safe_logger_write_func(s):
	for word in __words2hide:
		# throw away up to 4 bits (plus the randint() cost)
		random.getrandbits(random.randint(1, 4))
		# from there generate a replacement string valid for
		# *this* round of replacements of *this* word,
		# this approach won't mitigate guessing trivial passwords
		# from replacements of known data (a known-plaintext attack)
		# but will make automated searching for replaced strings
		# in the log more difficult
		bummer = hex(random.randint(0, sys.maxsize)).lstrip('0x')
		s = s.replace(word, bummer)
	__original_logger_write_func(s)

#---------------------------------------------------------------
def __setup_logging():

	global _logfile
	if _logfile is not None:
		return True

	if not __get_logfile_name():
		return False

	print("Log file:", _logfile_name)
	_logfile = open(_logfile_name, mode = 'wt', encoding = 'utf8', errors = 'replace')
	global __original_logger_write_func
	__original_logger_write_func = _logfile.write
	_logfile.write = __safe_logger_write_func

	# setup
	fmt = '%(asctime)s  %(levelname)-8s  %(name)-12s  [%(thread)d %(threadName)-10s]  (%(pathname)s::%(funcName)s() #%(lineno)d): %(message)s'
	logging.basicConfig (
		format = fmt,
		datefmt = '%Y-%m-%d %H:%M:%S',
		level = logging.DEBUG,
		stream = _logfile
	)
	logging.captureWarnings(True)
	logger = logging.getLogger()

	# start logging
	#logger = logging.getLogger('gm.logging')
	logger.critical('-------- start of logging ------------------------------')
	logger.info('log file is <%s>', _logfile_name)
	logger.info('log level is [%s]', logging.getLevelName(logger.getEffectiveLevel()))
	logger.info('log file encoding is <utf8>')
	logger.debug('log file .write() patched from original %s to patched %s', __original_logger_write_func, __safe_logger_write_func)

#---------------------------------------------------------------
def __get_logfile_name():

	global _logfile_name
	if _logfile_name is not None:
		return _logfile_name

	def_log_basename = os.path.splitext(os.path.basename(sys.argv[0]))[0]
	default_logfile_name = '%s-%s-%s.log' % (
		def_log_basename,
		pydt.datetime.now().strftime('%Y_%m_%d-%H_%M_%S'),
		os.getpid()
	)

	# given on command line ?
	for option in sys.argv[1:]:
		if option.startswith('--log-file='):
			(opt_name, value) = option.split('=')
			(dir_name, file_name) = os.path.split(value)
			if dir_name == '':
				dir_name = '.'
			if file_name == '':
				file_name = default_logfile_name
			_logfile_name = os.path.abspath(os.path.expanduser(os.path.join(dir_name, file_name)))
			return True

	# else store it in ~/.local/gnumed/logs/def_log_basename/default_logfile_name
	dir_name = os.path.expanduser(os.path.join('~', '.local', 'gnumed', 'logs', def_log_basename))
	try:
		os.makedirs(dir_name)
	except OSError as e:
		if (e.errno == 17) and not os.path.isdir(dir_name):
			raise

	_logfile_name = os.path.join(dir_name, default_logfile_name)

	return True

#===============================================================
# main
#---------------------------------------------------------------
__setup_logging()

if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	#-----------------------------------------------------------
	def test():
		print(_logfile_name)
		log_step(message = 'testing')
		logger = logging.getLogger('gmLog2.test')
		log_step()
		logger.error('test %s', [1,2,3])
		log_step(message = 'still testing')
		logger.error("I expected to see %s::test()" % __file__)
		log_step(message = 'restarting', restart = True)
		add_word2hide('super secret passphrase')
		log_step()
		logger.debug('credentials: super secret passphrase')
		log_step()
		try:
			int(None)
		except Exception:
			logger.exception('unhandled exception')
			log_stack_trace()
		flush()
		log_step(message = 'done')
	#-----------------------------------------------------------
	test()
