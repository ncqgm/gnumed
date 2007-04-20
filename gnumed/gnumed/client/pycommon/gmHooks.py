"""GNUmed hooks framework.

This module provides convenience functions and definitions
for accessing the GNUmed hooks framework.

This framework calls the script

	~/.gnumed/scripts/hook_script.py

at various times during client execution. The script must
contain a function

def run_script(hook=None):
	pass

which accepts a single argument <hook>. That argument will
contain the hook that is being activated.

This source code is protected by the GPL licensing scheme.
Details regarding the GPL are available at http://www.gnu.org
You may use and share it as long as you don't deny this right
to anybody else.
"""
# ========================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/pycommon/gmHooks.py,v $
# $Id: gmHooks.py,v 1.4 2007-04-20 08:21:42 ncq Exp $
__version__ = "$Revision: 1.4 $"
__author__  = "K. Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL (details at http://www.gnu.org)"


# stdlib
import os, sys


# GNUmed libs
if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmSignals, gmDispatcher, gmTools

# ========================================================================
hooks_registry = [
	u'post_patient_activation',
	u'shutdown-post-GUI',
	u'startup-after-GUI-init',
	u'startup-before-GUI'
]

# ========================================================================
def run_hook_script(hook=None):

	# NOTE: this just *might* be a huge security hole

	if hook is None:
		raise ValueError('run_hook_script(): <hook> cannot be <None>')

	if hook not in hooks_registry:
		raise ValueError('run_hook_script(): unknown hook [%s]' % hook)

	# hardcoding path and script name allows us to
	# not need configuration for it, the environment
	# can always be detected at runtime (workplace etc)
	script_name = 'hook_script.py'
	script_path = os.path.expanduser(os.path.join('~', '.gnumed', 'scripts'))
	full_script = os.path.join(script_path, script_name)

	if not os.access(full_script, os.F_OK):
		f = open(full_script, 'w')
		f.write("""
def run_script(hook=None):
	pass
""")
		f.close()
		os.chmod(full_script, 33152)

	if os.path.islink(full_script):
		gmDispatcher.send (
			gmSignals.statustext(),
			msg = _('Script must not be a link: [%s].') % full_script
		)
		return False

	if not os.access(full_script, os.R_OK):
		gmDispatcher.send (
			gmSignals.statustext(),
			msg = _('Script must be readable by the calling user: [%s].') % full_script
		)
		return False

	stat_val = os.stat(full_script)
#	if stat_val.st_mode != 384:				# octal 0600
	if stat_val.st_mode != 33152:			# octal 100600
		gmDispatcher.send (
			gmSignals.statustext(),
			msg = _('Script must have permissions "0600": [%s].') % full_script
		)
		return False

	module = gmTools.import_module_from_directory(script_path, script_name)
	module.run_script(hook = hook)

	return True
# ========================================================================
if __name__ == '__main__':

	run_hook_script(hook = 'shutdown-post-GUI')
	run_hook_script(hook = 'invalid hook')

# ========================================================================
# $Log: gmHooks.py,v $
# Revision 1.4  2007-04-20 08:21:42  ncq
# - improved docs
#
# Revision 1.3  2007/04/01 15:29:22  ncq
# - create hook script on first use if not existant
# - improve test
#
# Revision 1.2  2007/03/26 14:42:27  ncq
# - register startup-after-GUI-init
#
# Revision 1.1  2007/03/18 13:19:13  ncq
# - factor out hooks framework
#
#