# -*- coding: latin-1 -*-
"""GNUmed provider inbox middleware.

This should eventually end up in a class cPractice.
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/business/gmProviderInbox.py,v $
# $Id: gmProviderInbox.py,v 1.11 2008-09-04 12:52:51 ncq Exp $
__license__ = "GPL"
__version__ = "$Revision: 1.11 $"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"


import sys


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmPG2

#============================================================
class cProviderInbox:
	def __init__(self, provider_id=None):
		if provider_id is None:
			from Gnumed.business import gmPerson
			self.__provider_id = gmPerson.gmCurrentProvider()['pk_staff']
		else:
			self.__provider_id = provider_id
	#--------------------------------------------------------
	def _get_messages(self):
		cmd = u"""
select
	importance,
	l10n_category,
	l10n_type,
	comment,
	category,
	type,
	pk_context,
	data,
	pk_provider_inbox,
	received_when
from dem.v_provider_inbox vpi
where pk_staff = %s
order by importance desc, received_when desc"""
		try:
			rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': [self.__provider_id]}])
		except:
			return [[
				1,
				_('error'),
				_('error'),
				_('unable to get provider inbox messages from database'),
				'error',
				'error',
				None,
				_('An error occurred while retrieving provider inbox messages from the database.'),
				None,
				None
			]]
		return rows

	def _set_messages(self, messages):
		return

	messages = property(_get_messages, _set_messages)
	#--------------------------------------------------------
	def delete_message(self, pk=None):
		gmPG2.run_rw_queries(queries = [{'cmd': u"delete from dem.provider_inbox where pk=%s", 'args': [pk]}])
		return True
#============================================================
if __name__ == '__main__':

	from Gnumed.pycommon import gmI18N
	from Gnumed.business import gmPerson

	gmI18N.activate_locale()
	gmI18N.install_domain()

	if (len(sys.argv) > 1) and (sys.argv[1] == 'test'):
		gmPerson.gmCurrentProvider(provider = gmPerson.cStaff())
		inbox = cProviderInbox()
		for msg in inbox.messages:
			print msg

#============================================================
# $Log: gmProviderInbox.py,v $
# Revision 1.11  2008-09-04 12:52:51  ncq
# - load received_when
#
# Revision 1.10  2007/10/30 12:47:53  ncq
# - fix test suite
# - make messages a property on inbox
#
# Revision 1.9  2007/03/01 13:51:13  ncq
# - remove call to _log
#
# Revision 1.8  2006/10/08 15:10:01  ncq
# - convert to gmPG2
# - return all the fields needed for inbox on error
#
# Revision 1.7  2006/05/20 18:30:09  ncq
# - cleanup
#
# Revision 1.6  2006/05/16 08:20:28  ncq
# - remove field duplication
#
# Revision 1.5  2006/05/15 14:38:43  ncq
# - include message PK in load list
# - add delete_message()
#
# Revision 1.4  2006/05/12 13:53:34  ncq
# - missing ()
#
# Revision 1.3  2006/05/12 13:48:27  ncq
# - properly import gmPerson
#
# Revision 1.2  2006/05/12 12:04:30  ncq
# - use gmCurrentProvider
# - load more fields from inbox for later use
#
# Revision 1.1  2006/01/22 18:10:21  ncq
# - class for provider inbox
#
#