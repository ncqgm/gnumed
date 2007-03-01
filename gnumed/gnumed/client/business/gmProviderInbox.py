# -*- coding: latin-1 -*-
"""GNUmed provider inbox middleware.

This should eventually end up in a class cPractice.
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/business/gmProviderInbox.py,v $
# $Id: gmProviderInbox.py,v 1.9 2007-03-01 13:51:13 ncq Exp $
__license__ = "GPL"
__version__ = "$Revision: 1.9 $"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"

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
	def get_messages(self):
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
	pk_provider_inbox
from dem.v_provider_inbox vpi
where pk_staff = %s
order by importance desc"""
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
				None
			]]
		return rows
	#--------------------------------------------------------
	def delete_message(self, pk=None):
		gmPG2.run_rw_queries(queries = [{'cmd': u"delete from dem.provider_inbox where pk=%s", 'args': [pk]}])
		return True
#============================================================
if __name__ == '__main__':
	inbox = cProviderInbox()
	for msg in inbox.get_messages():
		print msg

#============================================================
# $Log: gmProviderInbox.py,v $
# Revision 1.9  2007-03-01 13:51:13  ncq
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