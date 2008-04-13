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
"""
# TODO:
# - exception()
# - ascii_ctrl2mnemonic()
#========================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/pycommon/gmLog2.py,v $
# $Id: gmLog2.py,v 1.10 2008-04-13 14:42:13 ncq Exp $
__version__ = "$Revision: 1.10 $"
__author__  = "K. Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL (details at http://www.gnu.org)"


# stdlib
import logging, sys, os, codecs, locale


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
	logger = logging.getLogger('gm.logging')
	logger.critical(u'-------- synced log file -------------------------------')
	root_logger = logging.getLogger()
	for handler in root_logger.handlers:
		handler.flush()
#===============================================================
def log_stack_trace(message=None):

	logger = logging.getLogger('gm.logging')

	tb = sys.exc_info()[2]
	if tb is None:
		try:
			tb = sys.last_traceback
		except AttributeError:
			logger.debug(u'no stack to trace')
			return

	# recurse back to root caller
	while 1:
		if not tb.tb_next:
			break
		tb = tb.tb_next
	# and put the frames on a stack
	stack_of_frames = []
	frame = tb.tb_frame
	while frame:
		stack_of_frames.append(frame)
		frame = frame.f_back
	stack_of_frames.reverse()

	if message is not None:
		logger.debug(message)
	logger.debug(u'stack trace follows:')
	logger.debug(u'(locals by frame, outmost frame first)')
	for frame in stack_of_frames:
		logger.debug (
			u'>>> execution frame [%s] in [%s] at line %s <<<',
			frame.f_code.co_name,
			frame.f_code.co_filename,
			frame.f_lineno
		)
		for varname, value in frame.f_locals.items():
			if varname == u'__doc__':
				continue
			try:
				value = u'%s' % unicode(value)
			except UnicodeDecodeError:
				value = '%s' % str(value)
				value = value.decode(_string_encoding, 'replace')
			logger.debug(u'%20s = %s', varname, value)
#===============================================================
def set_string_encoding(encoding=None):

	logger = logging.getLogger('gm.logging')

	global _string_encoding

	if encoding is not None:
		codecs.lookup(encoding)
		_string_encoding = encoding
		logger.info(u'setting python.str -> python.unicode encoding to <%s>', _string_encoding)
		return True

	enc = sys.getdefaultencoding()
	if enc != 'ascii':
		_string_encoding = enc
		logger.info(u'setting python.str -> python.unicode encoding to <%s>', _string_encoding)
		return True

	enc = locale.getlocale()[1]
	if enc is not None:
		_string_encoding = enc
		logger.info(u'setting python.str -> python.unicode encoding to <%s>', _string_encoding)
		return True

	# FIXME: or rather use utf8 ?
	_string_encoding = locale.getpreferredencoding(do_setlocale=False)
	logger.info(u'setting python.str -> python.unicode encoding to <%s>', _string_encoding)
	return True
#===============================================================
# internal API
#===============================================================
def __setup_logging():

	set_string_encoding()

	global _logfile
	if _logfile is not None:
		return True

	if not __get_logfile_name():
		return False

	if sys.version[:3] < '2.5':
		fmt = '%(asctime)s  %(levelname)-8s  %(name)s (%(pathname)s @ #%(lineno)d): %(message)s'
	else:
		fmt = '%(asctime)s  %(levelname)-8s  %(name)s (%(pathname)s::%(funcName)s() #%(lineno)d): %(message)s'

	_logfile = codecs.open(filename = _logfile_name, mode = 'wb', encoding = 'utf8', errors = 'replace')

	logging.basicConfig (
		format = fmt,
		datefmt = '%Y-%m-%d %H:%M:%S',
		level = logging.DEBUG,
		stream = _logfile
	)

	logger = logging.getLogger('gm.logging')
	logger.critical(u'-------- start of logging ------------------------------')
	logger.info(u'log file is <%s>', _logfile_name)
	logger.info(u'log level is [%s]', logging.getLevelName(logger.getEffectiveLevel()))
	logger.info(u'log file encoding is <utf8>')
	logger.info(u'initial python.str -> python.unicode encoding is <%s>', _string_encoding)
#---------------------------------------------------------------
def __get_logfile_name():

	global _logfile_name
	if _logfile_name is not None:
		return _logfile_name

	def_log_basename = os.path.splitext(os.path.basename(sys.argv[0]))[0]
	def_log_name = '%s-%s.log' % (def_log_basename, os.getpid())

	# given on command line ?
	for option in sys.argv[1:]:
		if option.startswith('--log-file='):
			(name,value) = option.split('=')
			(dir, name) = os.path.split(value)
			if dir == '':
				dir = '.'
			if name == '':
				name = def_log_name
			_logfile_name = os.path.abspath(os.path.expanduser(os.path.join(dir, name)))
			return True

	# else store it in ~/.def_log_basename/def_log_name
	dir = os.path.expanduser(os.path.join('~', '.' + def_log_basename))
	try:
		os.makedirs(dir)
	except OSError, e:
		if (e.errno == 17) and not os.path.isdir(dir):
			raise

	_logfile_name = os.path.join(dir, def_log_name)

	return True
#===============================================================
# main
#---------------------------------------------------------------
__setup_logging()

if __name__ == '__main__':

	#-----------------------------------------------------------
	def test():
		logger = logging.getLogger('gmLog2.test')
		logger.error("I expected to see %s::test()" % __file__)
		try:
			int(None)
		except:
			logger.exception('unhandled exception')
			log_stack_trace()
		flush()
	#-----------------------------------------------------------
	if len(sys.argv) > 1 and sys.argv[1] == u'test':
		test()
#===============================================================
# $Log: gmLog2.py,v $
# Revision 1.10  2008-04-13 14:42:13  ncq
# - saviour the last bits from the old logging code
#
# Revision 1.9  2008/03/06 21:23:22  ncq
# - keep some interesting stuff from the old logging infrastructure
#
# Revision 1.8  2008/03/06 18:46:55  ncq
# - fix docs
#
# Revision 1.7  2008/03/06 18:25:22  ncq
# - fix docs
#
# Revision 1.6  2008/01/30 14:05:09  ncq
# - a bit of cleanup
# - TODO added
#
# Revision 1.5  2008/01/14 20:27:39  ncq
# - set_string_encoding()
# - properly encode values in log_stack_trace()
# - proper test suite
#
# Revision 1.4  2008/01/13 01:15:41  ncq
# - log_stack_trace() and test
# - include PID in default log file name
# - cleanup
#
# Revision 1.3  2008/01/07 19:48:53  ncq
# - add flush()
#
# Revision 1.2  2007/12/12 16:23:21  ncq
# - we want the default to be the default in GNUmed,
#   no need to call it that
#
# Revision 1.1  2007/12/11 10:03:45  ncq
# - eventually start switching to Python standard logging
#
#