__doc__ = """GNUmed general tools."""

#===========================================================================
# $Id: gmShellAPI.py,v 1.8 2008-03-06 21:25:41 ncq Exp $
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/pycommon/gmShellAPI.py,v $
__version__ = "$Revision: 1.8 $"
__author__ = "K. Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL (details at http://www.gnu.org)"


# stdlib
import os, sys, logging


_log = logging.getLogger('gm.shell')
_log.info(__version__)

#===========================================================================
def detect_external_binary(binary=None):
	_log.debug('detecting [%s]', binary)

	# is it a sufficiently qualified path ?
	if os.access(binary, os.X_OK):
		return (True, binary)

	# maybe we are on UNIX and should use "which" to find the full path ?
	cmd = 'which %s' % binary
	pipe = os.popen(cmd.encode(sys.getfilesystemencoding()), "r")
	result = pipe.readline()
	ret_code = pipe.close()
	if ret_code is not None:
		_log.debug('[%s] failed, exit code: %s', cmd, ret_code)
	else:
		result = result.strip('\r\n')
		_log.debug('[%s] returned: %s', cmd, result)
		# redundant on Linux but apparently necessary on MacOSX
		if os.access(result, os.X_OK):
			return (True, result)
		else:
			_log.debug('[%s] not detected with "which"', binary)

	# maybe we have wine installed ?
	tmp = binary.lstrip('wine').strip().strip('"')
	cmd = 'winepath -u "%s"' % tmp
	pipe = os.popen(cmd.encode(sys.getfilesystemencoding()), "r")
	result = pipe.readline()
	ret_code = pipe.close()
	if ret_code is not None:
		_log.debug('winepath failed')
	else:
		result = result.strip('\r\n')
		if os.access(result, os.X_OK):
			return (True, binary)
		else:
			_log.warning('"winepath %s" returned [%s] but the path is not verifiable', binary, result)

	return (False, None)
#===========================================================================
def run_command_in_shell(command=None, blocking=False):
	"""Runs a command in a subshell via standard-C system().

	<command>
		The shell command to run including command line options.
	<blocking>
		This will make the code *block* until the shell command exits.
		It will likely only work on UNIX shells where "cmd &" makes sense.
	"""
	_log.debug('shell command >>>%s<<<' % command)
	_log.debug('blocking: %s' % blocking)

	# FIXME: command should be checked for shell exploits

	command = command.strip()

	# what the following hack does is this: the user indicated
	# whether she wants non-blocking external display of files
	# - the real way to go about this is to have a non-blocking command
	#   in the line in the mailcap file for the relevant mime types
	# - as non-blocking may not be desirable when *not* displaying
	#   files from within GNUmed the really right way would be to
	#   add a "test" clause to the non-blocking mailcap entry which
	#   yields true if and only if GNUmed is running
	# - however, this is cumbersome at best and not supported in
	#   some mailcap implementations
	# - so we allow the user to attempt some control over the process
	#   from within GNUmed by setting a configuration option
	# - leaving it None means to use the mailcap default or whatever
	#   was specified in the command itself
	# - True means: tack " &" onto the shell command if necessary
	# - False means: remove " &" from the shell command if its there
	# - all this, of course, only works in shells which support
	#   detaching jobs with " &" (so, most POSIX shells)
	if blocking is True:
		if command[-2:] == ' &':
			command = command[:-2]
	elif blocking is False:
		if command[-2:] != ' &':
			command += ' &'

	_log.debug('running shell command >>>%s<<<' % command)
	ret_val = os.system(command.encode(sys.getfilesystemencoding()))
	_log.debug('os.system() returned: [%s]' % ret_val)

	exited_normally = False
	_log.debug('exited via exit(): %s' % os.WIFEXITED(ret_val))
	if os.WIFEXITED(ret_val):
		_log.debug('exit code: [%s]' % os.WEXITSTATUS(ret_val))
		exited_normally = (os.WEXITSTATUS(ret_val) == 0)
	_log.debug('dumped core: %s' % os.WCOREDUMP(ret_val))
	_log.debug('stopped by signal: %s' % os.WIFSIGNALED(ret_val))
	if os.WIFSIGNALED(ret_val):
		_log.debug('STOP signal was: [%s]' % os.STOPSIG(ret_val))
		_log.debug('TERM signal was: [%s]' % os.TERMSIG(ret_val))

	return exited_normally
#===========================================================================
# main
#---------------------------------------------------------------------------
if __name__ == '__main__':

	if len(sys.argv) > 1 and sys.argv[1] == u'test':

		logging.basicConfig(level = logging.DEBUG)

		#---------------------------------------------------------
		def test_detect_external_binary():
			found, path = detect_external_binary(binary = sys.argv[2])
			if found:
				print "found as:", path
			else:
				print sys.argv[2], "not found"
		#---------------------------------------------------------
		def test_run_command_in_shell():
			print "-------------------------------------"
			print "running:", sys.argv[2]
			if run_command_in_shell(command=sys.argv[2], blocking=True):
				print "-------------------------------------"
				print "success"
			else:
				print "-------------------------------------"
				print "failure, consult log"
		#---------------------------------------------------------

		#test_run_command_in_shell()
		test_detect_external_binary()

#===========================================================================
# $Log: gmShellAPI.py,v $
# Revision 1.8  2008-03-06 21:25:41  ncq
# - optimize detect_external_binary() for the common case
#
# Revision 1.7  2008/03/06 18:48:21  ncq
# - much improved wine-based executable detection
#
# Revision 1.6  2008/03/02 15:09:35  ncq
# - smarten up detect_external_binary about winepath
#
# Revision 1.5  2008/01/14 20:30:11  ncq
# - detect_external_binary()
# - better tests
#
# Revision 1.4  2007/12/12 16:17:16  ncq
# - better logger names
#
# Revision 1.3  2007/12/11 14:33:48  ncq
# - use standard logging module
#
# Revision 1.2  2007/03/31 21:20:34  ncq
# - os.system() needs encoded commands
#
# Revision 1.1  2006/12/23 13:17:32  ncq
# - new API
#

