#
# Example script to be run off GNUmed hooks.
#
# It will popup a modal dialog whenever any
# hook is invoked and will wait for user
# interaction before proceeding.
#
#===========================================================================
# $Id: hook_script_example.py,v 1.1 2007-02-19 16:23:08 ncq Exp $
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/doc/hook_script_example.py,v $
__version__ = "$Revision: 1.1 $"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL (details at http://www.gnu.org)"

from Gnumed.wxpython import gmGuiHelpers

def run_script(hook=None):

	if hook is None:
		hook = _('no hook specified, please report bug')

	gmGuiHelpers.gm_show_info (
		_(
		'GNUmed invoked the hook\n\n'
		' [%s]'
		) % hook
	)

	return

#===========================================================================
# $Log: hook_script_example.py,v $
# Revision 1.1  2007-02-19 16:23:08  ncq
# - better name
#
# Revision 1.1  2007/02/19 16:21:07  ncq
# - an example for the hooks framework
#
#
