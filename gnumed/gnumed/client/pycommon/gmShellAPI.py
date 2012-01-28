__doc__ = """GNUmed general tools."""

#===========================================================================
__version__ = "$Revision: 1.13 $"
__author__ = "K. Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL v2 or later (details at http://www.gnu.org)"


# stdlib
import os
import sys
import logging
import subprocess
import shlex


_log = logging.getLogger('gm.shell')
_log.info(__version__)

#===========================================================================
def is_cmd_in_path(cmd=None):

	_log.debug('cmd: [%s]', cmd)
	dirname = os.path.dirname(cmd)
	_log.debug('dir: [%s]', dirname)
	if dirname != u'':
		_log.info('command with full or relative path, not searching in PATH for binary')
		return (None, None)

	env_paths = os.environ['PATH']
	_log.debug('${PATH}: %s', env_paths)
	for path in env_paths.split(os.pathsep):
		candidate = os.path.join(path, cmd).encode(sys.getfilesystemencoding())
		if os.access(candidate, os.X_OK):
			_log.debug('found [%s]', candidate)
			return (True, candidate.decode(sys.getfilesystemencoding()))
		else:
			_log.debug('not found: %s', candidate)

	_log.debug('command not found in PATH')

	return (False, None)
#===========================================================================
def is_executable_by_wine(cmd=None):

	if not cmd.startswith('wine'):
		_log.debug('not a WINE call: %s', cmd)
		return (False, None)

	exe_path = cmd.encode(sys.getfilesystemencoding())

	exe_path = exe_path[4:].strip().strip('"').strip()
	# [wine "/standard/unix/path/to/binary.exe"] ?
	if os.access(exe_path, os.R_OK):
		_log.debug('WINE call with UNIX path: %s', exe_path)
		return (True, cmd)

	# detect [winepath]
	found, full_winepath_path = is_cmd_in_path(cmd = r'winepath')
	if not found:
		_log.error('[winepath] not found, cannot check WINE call for Windows path conformance: %s', exe_path)
		return (False, None)

	# [wine "drive:\a\windows\path\to\binary.exe"] ?
	cmd_line = r'%s -u "%s"' % (
		full_winepath_path.encode(sys.getfilesystemencoding()),
		exe_path
	)
	_log.debug('converting Windows path to UNIX path: %s' % cmd_line)
	cmd_line = shlex.split(cmd_line)
	try:
		winepath = subprocess.Popen (
			cmd_line,
			stdout = subprocess.PIPE,
			stderr = subprocess.PIPE,
			universal_newlines = True
		)
	except OSError:
		_log.exception('cannot run <winepath>')
		return (False, None)

	stdout, stderr = winepath.communicate()
	full_path = stdout.strip('\r\n')
	_log.debug('UNIX path: %s', full_path)

	if winepath.returncode != 0:
		_log.error('<winepath -u> returned [%s], failed to convert path', winepath.returncode)
		return (False, None)

	if os.access(full_path, os.R_OK):
		_log.debug('WINE call with Windows path')
		return (True, cmd)

	_log.warning('Windows path [%s] not verifiable under UNIX: %s', exe_path, full_path)
	return (False, None)
#===========================================================================
def detect_external_binary(binary=None):
	_log.debug('searching for [%s]', binary)

	binary = binary.lstrip()

	# is it a sufficiently qualified, directly usable, explicit path ?
	if os.access(binary, os.X_OK):
		_log.debug('found: executable explicit path')
		return (True, binary)

	# can it be found in PATH ?
	found, full_path = is_cmd_in_path(cmd = binary)
	if found:
		if os.access(full_path, os.X_OK):
			_log.debug('found: executable in ${PATH}')
			return (True, full_path)

	# does it seem to be a call via WINE ?
	is_wine_call, full_path = is_executable_by_wine(cmd = binary)
	if is_wine_call:
		_log.debug('found: is valid WINE call')
		return (True, full_path)

	# maybe we can be a bit smart about Windows ?
	if os.name == 'nt':
		# try .exe (but not if already .bat or .exe)
		if not (binary.endswith('.exe') or binary.endswith('.bat')):
			exe_binary = binary + r'.exe'
			_log.debug('re-testing as %s', exe_binary)
			found_dot_exe_binary, full_path = detect_external_binary(binary = exe_binary)
			if found_dot_exe_binary:
				return (True, full_path)
			# not found with .exe, so try .bat:
			bat_binary = binary + r'.bat'
			_log.debug('re-testing as %s', bat_binary)
			found_bat_binary, full_path = detect_external_binary(binary = bat_binary)
			if found_bat_binary:
				return (True, full_path)
	else:
		_log.debug('not running under Windows, not testing .exe/.bat')

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

	if os.name == 'nt':
		# http://stackoverflow.com/questions/893203/bat-files-nonblocking-run-launch
		if blocking is False:
			if not command.startswith('start '):
				command = 'start /B "%s"' % command
		elif blocking is True:
			if not command.startswith('start '):
				command = 'start /WAIT /B "%s"' % command
	else:
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
		_log.error('platform does not support exit status differentiation')
		if ret_val in acceptable_return_codes:
			_log.info('os.system() return value contained in acceptable return codes')
			_log.info('continuing and hoping for the best')
			return True
		return exited_normally

	_log.debug('exited via exit(): %s', os.WIFEXITED(ret_val))
	if os.WIFEXITED(ret_val):
		_log.debug('exit code: [%s]', os.WEXITSTATUS(ret_val))
		exited_normally = (os.WEXITSTATUS(ret_val) in acceptable_return_codes)
		_log.debug('normal exit: %s', exited_normally)
	_log.debug('dumped core: %s', os.WCOREDUMP(ret_val))
	_log.debug('stopped by signal: %s', os.WIFSIGNALED(ret_val))
	if os.WIFSIGNALED(ret_val):
		try:
			_log.debug('STOP signal was: [%s]', os.WSTOPSIG(ret_val))
		except AttributeError:
			_log.debug('platform does not support os.WSTOPSIG()')
		try:
			_log.debug('TERM signal was: [%s]', os.WTERMSIG(ret_val))
		except AttributeError:
			_log.debug('platform does not support os.WTERMSIG()')

	return exited_normally
#===========================================================================
def run_first_available_in_shell(binaries=None, args=None, blocking=False, run_last_one_anyway=False, acceptable_return_codes=None):

	found, binary = find_first_binary(binaries = binaries)

	if not found:
		_log.warning('cannot find any of: %s', binaries)
		if run_last_one_anyway:
			binary = binaries[-1]
			_log.debug('falling back to trying to run [%s] anyway', binary)
		else:
			return False

	return run_command_in_shell(command = '%s %s' % (binary, args), blocking = blocking, acceptable_return_codes = acceptable_return_codes)
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
		if run_command_in_shell(command=sys.argv[2], blocking=False):
			print "-------------------------------------"
			print "success"
		else:
			print "-------------------------------------"
			print "failure, consult log"
	#---------------------------------------------------------
	def test_is_cmd_in_path():
		print is_cmd_in_path(cmd = sys.argv[2])
	#---------------------------------------------------------
	def test_is_executable_by_wine():
		print is_executable_by_wine(cmd = sys.argv[2])
	#---------------------------------------------------------
	test_run_command_in_shell()
	#test_detect_external_binary()
	#test_is_cmd_in_path()
	#test_is_executable_by_wine()

#===========================================================================
