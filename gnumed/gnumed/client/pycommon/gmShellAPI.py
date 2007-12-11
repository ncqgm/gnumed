__doc__ = """GNUmed general tools."""

#===========================================================================
# $Id: gmShellAPI.py,v 1.3 2007-12-11 14:33:48 ncq Exp $
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/pycommon/gmShellAPI.py,v $
__version__ = "$Revision: 1.3 $"
__author__ = "K. Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL (details at http://www.gnu.org)"


# stdlib
import os, sys, logging


_log = logging.getLogger('gnumed.shell')
_log.info(__version__)

#===========================================================================
def run_command_in_shell(command=None, blocking=False):
	"""Runs a command in a subshell via standard-C system().

	<command>
		The shell command to run including command line options.
	<blocking>
		This will make the code *block* until the shell command exits.
		It will likely only work on UNIX shells where "cmd &" makes sense.
	"""
	_log.debug('given shell command >>>%s<<<' % command)
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

		sys.path.insert(0, '../../')
		from Gnumed.pycommon import gmLog2

		print "-------------------------------------"
		print "running:", sys.argv[2]
		if run_command_in_shell(command=sys.argv[2], blocking=True):
			print "-------------------------------------"
			print "success"
		else:
			print "-------------------------------------"
			print "failure, consult log"

#===========================================================================
# $Log: gmShellAPI.py,v $
# Revision 1.3  2007-12-11 14:33:48  ncq
# - use standard logging module
#
# Revision 1.2  2007/03/31 21:20:34  ncq
# - os.system() needs encoded commands
#
# Revision 1.1  2006/12/23 13:17:32  ncq
# - new API
#

