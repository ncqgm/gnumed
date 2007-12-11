"""GNUmed log framework.

All error logging, user notification and otherwise unhandled 
exception handling should go through classes or functions of 
this module

Theory of operation:

By importing gmLog into your code you'll immediately have
access to a default logger: gmDefLog. Initially, the logger has
a log file as it's default target. The name of the file is
automatically derived from the name of the main application.
The log file will be found in one of the following standard
locations:

1) given on the command line as "--log-file=LOGFILE"
2) ~/.<base_name>/<base_name>.log
3) /dir/of/binary/<base_name>.log	- mainly for DOS/Windows

where <base_name> is derived from the name
of the main application.

If you want to specify just a directory for the log file you
must end the LOGFILE definition with slash.

By importing gmLog and logging to the default log your modules
never need to worry about the real message destination or whether
at any given time there's a valid logger available. Your MAIN
module simply adds real log targets to the default logger and
all other modules will merrily and automagically start logging
there.

You can of course instantiate any number of additional loggers
that log to different targets alltogether if you want to keep
some messages separate from others.
"""
#========================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/pycommon/gmLog2.py,v $
# $Id: gmLog2.py,v 1.1 2007-12-11 10:03:45 ncq Exp $
__version__ = "$Revision: 1.1 $"
__author__  = "K. Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL (details at http://www.gnu.org)"


# stdlib
import logging, sys, os, codecs


_default_logfile_name = None
_default_logfile = None
#===============================================================
def setup_default_logging():

	global _default_logfile
	if _default_logfile is not None:
		return True

	if not __find_default_logfile():
		return False

	if sys.version[:3] < '2.5':
		fmt = '%(asctime)s  [%(levelname)-7s]  %(name)s (%(pathname)s @ #%(lineno)d): %(message)s'
	else:
		fmt = '%(asctime)s  [%(levelname)-7s]  %(name)s (%(pathname)s::%(funcName)s() #%(lineno)d): %(message)s'

	_default_logfile = codecs.open(filename = _default_logfile_name, mode = 'wb', encoding = 'utf8', errors = 'replace')

	logging.basicConfig (
		format = fmt,
		datefmt = '%Y-%m-%d %H:%M:%S',
		level = logging.DEBUG,
		stream = _default_logfile
	)

	# activate things
	# FIXME: really needed ?
	logger = logging.getLogger('GNUmed compat logger')
#---------------------------------------------------------------
def __find_default_logfile():

	global _default_logfile_name
	if _default_logfile_name is not None:
		return _default_logfile_name

	def_log_basename = os.path.splitext(os.path.basename(sys.argv[0]))[0]
	def_log_name = def_log_basename + '.log'

	# given on command line ?
	for option in sys.argv[1:]:
		if option.startswith('--log-file='):
			(name,value) = option.split('=')
			(dir, name) = os.path.split(value)
			if dir == '':
				dir = '.'
			if name == '':
				name = def_log_name
			_default_logfile_name = os.path.abspath(os.path.expanduser(os.path.join(dir, name)))
			return True

	# else store it in ~/.def_log_basename/def_log_name
	dir = os.path.expanduser(os.path.join('~', '.' + def_log_basename))
	try:
		os.makedirs(dir)
	except OSError, e:
		if (e.errno == 17) and not os.path.isdir(dir):
			raise

	_default_logfile_name = os.path.join(dir, def_log_name)

	return True
#===============================================================
# main
#---------------------------------------------------------------
setup_default_logging()

if __name__ == '__main__':

	#-----------------------------------------------------------
	def test():
		my_logger.error("I expected to see %s::test()" % __file__)
	#-----------------------------------------------------------
	if len(sys.argv) > 1 and sys.argv[1] == u'test':
		my_logger = logging.getLogger('logging-test')
		test()
#===============================================================
# $Log: gmLog2.py,v $
# Revision 1.1  2007-12-11 10:03:45  ncq
# - eventually start switching to Python standard logging
#
#