__doc__ = """GNUmed general tools."""

#===========================================================================
# $Id: gmShellAPI.py,v 1.2 2007-03-31 21:20:34 ncq Exp $
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/pycommon/gmShellAPI.py,v $
__version__ = "$Revision: 1.2 $"
__author__ = "K. Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL (details at http://www.gnu.org)"


# stdlib
import os, sys


# GNUmed libs
if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmLog


_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)

#===========================================================================
def run_command_in_shell(command=None, blocking=False):
	"""Runs a command in a subshell via standard-C system().

	<command>
		The shell command to run including command line options.
	<blocking>
		This will make the code *block* until the shell command exits.
		It will likely only work on UNIX shells where "cmd &" makes sense.
	"""
	_log.Log(gmLog.lData, 'given shell command >>>%s<<<' % command)
	_log.Log(gmLog.lData, 'blocking: %s' % blocking)

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

	_log.Log(gmLog.lData, 'running shell command >>>%s<<<' % command)
	ret_val = os.system(command.encode(sys.getfilesystemencoding()))
	_log.Log(gmLog.lData, 'os.system() returned: [%s]' % ret_val)

	exited_normally = False
	_log.Log(gmLog.lData, 'exited via exit(): %s' % os.WIFEXITED(ret_val))
	if os.WIFEXITED(ret_val):
		_log.Log(gmLog.lData, 'exit code: [%s]' % os.WEXITSTATUS(ret_val))
		exited_normally = (os.WEXITSTATUS(ret_val) == 0)
	_log.Log(gmLog.lData, 'dumped core: %s' % os.WCOREDUMP(ret_val))
	_log.Log(gmLog.lData, 'stopped by signal: %s' % os.WIFSIGNALED(ret_val))
	if os.WIFSIGNALED(ret_val):
		_log.Log(gmLog.lData, 'STOP signal was: [%s]' % os.STOPSIG(ret_val))
		_log.Log(gmLog.lData, 'TERM signal was: [%s]' % os.TERMSIG(ret_val))

	return exited_normally
#===========================================================================
# main
#---------------------------------------------------------------------------
if __name__ == '__main__':
	_log.SetAllLogLevels(gmLog.lData)
	print "-------------------------------------"
	if run_command_in_shell(command=sys.argv[1], blocking=True):
		print "-------------------------------------"
		print "success"
	else:
		print "-------------------------------------"
		print "failure, consult log"

#===========================================================================
# $Log: gmShellAPI.py,v $
# Revision 1.2  2007-03-31 21:20:34  ncq
# - os.system() needs encoded commands
#
# Revision 1.1  2006/12/23 13:17:32  ncq
# - new API
#
