# -*- coding: latin-1 -*-
"""GNUmed provider inbox middleware.

This should eventually end up in a class cPractice.
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/business/gmProviderInbox.py,v $
# $Id: gmProviderInbox.py,v 1.14 2009-12-01 21:48:42 ncq Exp $
__license__ = "GPL"
__version__ = "$Revision: 1.14 $"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"


import sys


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmPG2, gmBusinessDBObject

#============================================================
class cInboxMessage(gmBusinessDBObject.cBusinessDBObject):

	_cmd_fetch_payload = u"select * from dem.v_message_inbox where pk_message_inbox = %s"

	_cmds_store_payload = [
	]

	u"""update clin.test_result set
				clin_when = %(clin_when)s,
				narrative = nullif(trim(%(comment)s), ''),
				val_num = %(val_num)s,
				val_alpha = nullif(trim(%(val_alpha)s), ''),
				val_unit = nullif(trim(%(val_unit)s), ''),
				val_normal_min = %(val_normal_min)s,
				val_normal_max = %(val_normal_max)s,
				val_normal_range = nullif(trim(%(val_normal_range)s), ''),
				val_target_min = %(val_target_min)s,
				val_target_max = %(val_target_max)s,
				val_target_range = nullif(trim(%(val_target_range)s), ''),
				abnormality_indicator = nullif(trim(%(abnormality_indicator)s), ''),
				norm_ref_group = nullif(trim(%(norm_ref_group)s), ''),
				note_test_org = nullif(trim(%(note_test_org)s), ''),
				material = nullif(trim(%(material)s), ''),
				material_detail = nullif(trim(%(material_detail)s), ''),
				fk_intended_reviewer = %(pk_intended_reviewer)s,
				fk_encounter = %(pk_encounter)s,
				fk_episode = %(pk_episode)s,
				fk_type = %(pk_test_type)s
			where
				pk = %(pk_test_result)s and
				xmin = %(xmin_test_result)s""",
	u"""select xmin_test_result from clin.v_test_results where pk_test_result = %(pk_test_result)s"""

	_updatable_fields = [
		u'pk_staff',
		u'pk_patient',
		u'pk_type',
		u'comment',
#		u'pk_context',
		u'data',
		u'importance'
	]
#------------------------------------------------------------
def get_inbox_messages(pk_staff=None, pk_patient=None, include_without_provider=False):

	args = {}
	where_parts = []

	if pk_staff is not None:
		if include_without_provider:
			where_parts.append(u'pk_staff in (%(staff)s, NULL)')
		else:
			where_parts.append(u'pk_staff = %(staff)s')
		args['staff'] = pk_staff

	if pk_patient is not None:
		where_parts.append(u'pk_patient = %(pat)s')
		args['pat'] = pk_patient

	cmd = u"""
		SELECT *
		FROM dem.v_message_inbox
		WHERE %s
		ORDER BY importance desc, received_when desc""" % u' AND '.join(where_parts)

	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)
	return [ cInboxMessage(row = {'pk_field': 'pk_message_inbox', 'idx': idx, 'data': r})  for r in rows ]
#------------------------------------------------------------
def delete_inbox_message(pk=None):
	gmPG2.run_rw_queries(queries = [{'cmd': u"delete from dem.message_inbox where pk = %s", 'args': [pk]}])
	return True
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
		return get_inbox_messages(pk_staff = self.__provider_id)

	def _set_messages(self, messages):
		return

	messages = property(_get_messages, _set_messages)
	#--------------------------------------------------------
	def delete_message(self, pk=None):
		return delete_inbox_message(pk = pk)
#============================================================
if __name__ == '__main__':

	from Gnumed.pycommon import gmI18N
	from Gnumed.business import gmPerson

	gmI18N.activate_locale()
	gmI18N.install_domain()

	#---------------------------------------
	def test_inbox():
		gmPerson.gmCurrentProvider(provider = gmPerson.cStaff())
		inbox = cProviderInbox()
		for msg in inbox.messages:
			print msg
	#---------------------------------------
	def test_msg():
		msg = cInboxMessage(aPK_obj = 1)
		print msg
	#---------------------------------------
	if (len(sys.argv) > 1) and (sys.argv[1] == 'test'):
		test_inbox()
		#test_msg()

#============================================================
# $Log: gmProviderInbox.py,v $
# Revision 1.14  2009-12-01 21:48:42  ncq
# - fix typo
#
# Revision 1.13  2009/11/30 22:24:36  ncq
# - add order by
#
# Revision 1.12  2009/08/24 20:03:59  ncq
# - proper cInboxMessage and use it
#
# Revision 1.11  2008/09/04 12:52:51  ncq
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