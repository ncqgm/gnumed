__doc__ = """GNUmed general tools."""

#===========================================================================
__version__ = "$Revision: 1.13 $"
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

	# try "which" to find the full path
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

	# consider "d/m/s/locate" to find the full path

	tmp = binary.lstrip()
	# to be run by wine ?
	if tmp.startswith('wine'):

		tmp = tmp[4:].strip().strip('"')

		# "wine /standard/unix/path/to/binary" ?
		if os.access(tmp, os.R_OK):
			_log.debug('wine call with UNIX path')
			return (True, binary)

		# 'wine "drive:\a\windows\path\to\binary"' ?
		cmd = 'winepath -u "%s"' % tmp
		pipe = os.popen(cmd.encode(sys.getfilesystemencoding()), "r")
		result = pipe.readline()
		ret_code = pipe.close()
		if ret_code is not None:
			_log.debug('winepath failed')
		else:
			result = result.strip('\r\n')
			if os.access(result, os.R_OK):
				_log.debug('wine call with Windows path')
				return (True, binary)
			else:
				_log.warning('"winepath -u %s" returned [%s] but the UNIX path is not verifiable', tmp, result)

	return (False, None)
#===========================================================================
def find_first_binary(binaries=None):

	found = False
	binary = None

	for cmd in binaries:
		_log.debug('looking for [%s]', cmd)

		if cmd is None:
			continue

		found, binary = detect_external_binary(binary = cmd)
		if found:
			break

	return (found, binary)
#===========================================================================
def run_command_in_shell(command=None, blocking=False, acceptable_return_codes=None):
	"""Runs a command in a subshell via standard-C system().

	<command>
		The shell command to run including command line options.
	<blocking>
		This will make the code *block* until the shell command exits.
		It will likely only work on UNIX shells where "cmd &" makes sense.
	"""
	if acceptable_return_codes is None:
		acceptable_return_codes = [0]

	_log.debug('shell command >>>%s<<<', command)
	_log.debug('blocking: %s', blocking)
	_log.debug('acceptable return codes: %s', str(acceptable_return_codes))

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

	_log.info('running shell command >>>%s<<<', command)
	# FIXME: use subprocess.Popen()
	ret_val = os.system(command.encode(sys.getfilesystemencoding()))
	_log.debug('os.system() returned: [%s]', ret_val)

	exited_normally = False

	if not hasattr(os, 'WIFEXITED'):
		_log.debug('platform does not support exit status differentiation')
		return exited_normally

	_log.debug('exited via exit(): %s', os.WIFEXITED(ret_val))
	if os.WIFEXITED(ret_val):
		_log.debug('exit code: [%s]', os.WEXITSTATUS(ret_val))
		exited_normally = (os.WEXITSTATUS(ret_val) in acceptable_return_codes)
		_log.debug('normal exit: %s', exited_normally)
	_log.debug('dumped core: %s', os.WCOREDUMP(ret_val))
	_log.debug('stopped by signal: %s', os.WIFSIGNALED(ret_val))
	if os.WIFSIGNALED(ret_val):
		_log.debug('STOP signal was: [%s]', os.STOPSIG(ret_val))
		_log.debug('TERM signal was: [%s]', os.TERMSIG(ret_val))

	return exited_normally
#===========================================================================
def run_first_available_in_shell(binaries=None, args=None, blocking=False, run_last_one_anyway=False):

	found, binary = find_first_binary(binaries = binaries)

	if not found:
		if run_last_one_anyway:
			binary = binaries[-1]
		else:
			_log.warning('cannot find any of: %s', binaries)
			return False

	return run_command_in_shell(command = '%s %s' % (binary, args), blocking = blocking)
#===========================================================================
# main
#---------------------------------------------------------------------------
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != u'test':
		sys.exit()

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
	test_run_command_in_shell()
	#test_detect_external_binary()

#===========================================================================
