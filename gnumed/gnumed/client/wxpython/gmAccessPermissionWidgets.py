"""GNUmed access permissions/violations widgets."""
#=========================================================================
__author__  = "K. Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL v2 or later (details at https://www.gnu.org)"

import sys
import logging


import wx


if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x

from Gnumed.business import gmStaff
from Gnumed.wxpython import gmGuiHelpers


_log = logging.getLogger('gm.perms')

#=========================================================================
_known_roles = [
	'public access',
	'non-clinical access',
	'limited clinical access',	# currently not in use
	'full clinical access',
	'admin'						# currently not in use
]

_curr_staff = gmStaff.gmCurrentProvider()

#-------------------------------------------------------------------------
def verify_minimum_required_role(minimum_role:str, activity:str=None, return_value_on_failure=None, fail_silently:bool=False):

	if activity is None:
		activity = _('generic activity')

	#---------
	def _inner_verify_minimum_required_role(original_function):

		#---------
		def _func_decorated_with_required_role_checking(*args, **kwargs):
			if _known_roles.index(minimum_role) > _known_roles.index(_curr_staff['role']):
				_log.info('access denied: %s', activity)
				_log.debug('required role: %s', minimum_role)
				_log.debug('current role: %s (<%s>)', _curr_staff['l10n_role'], _curr_staff['role'])
				_log.debug('current user: %s (<%s>)', _curr_staff['short_alias'], _curr_staff['db_user'])
				wx.EndBusyCursor()
				if fail_silently:
					return return_value_on_failure

				gmGuiHelpers.gm_show_error (
					aTitle = _('Access denied'),
					aMessage = _(
						'Your account is not set up to access this part of GNUmed:\n'
						'\n'
						'  [%s]'
					) % activity
				)
				return return_value_on_failure

			return original_function(*args, **kwargs)
		#---------

		return _func_decorated_with_required_role_checking

	#---------
	return _inner_verify_minimum_required_role

#=========================================================================
