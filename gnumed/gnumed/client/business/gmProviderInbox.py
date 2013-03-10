# -*- coding: latin-1 -*-
"""GNUmed provider inbox middleware.

This should eventually end up in a class cPractice.
"""
#============================================================
__license__ = "GPL"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"


import sys


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmPG2
from Gnumed.pycommon import gmBusinessDBObject
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmDateTime

from Gnumed.business import gmStaff

#============================================================
# provider message inbox
#------------------------------------------------------------
_SQL_get_inbox_messages = u"SELECT * FROM dem.v_message_inbox WHERE %s"

class cInboxMessage(gmBusinessDBObject.cBusinessDBObject):

	_cmd_fetch_payload = _SQL_get_inbox_messages % u"pk_inbox_message = %s"
	_cmds_store_payload = [
		u"""
			UPDATE dem.message_inbox SET
				fk_staff = %(pk_staff)s,
				fk_inbox_item_type = %(pk_type)s,
				comment = gm.nullify_empty_string(%(comment)s),
				data = gm.nullify_empty_string(%(data)s),
				importance = %(importance)s,
				fk_patient = %(pk_patient)s,
				ufk_context = NULLIF(%(pk_context)s::integer[], ARRAY[NULL::integer]),
				due_date = %(due_date)s,
				expiry_date = %(expiry_date)s
			WHERE
				pk = %(pk_inbox_message)s
					AND
				xmin = %(xmin_message_inbox)s
			RETURNING
				pk as pk_inbox_message,
				xmin as xmin_message_inbox
		"""
	]
	_updatable_fields = [
		u'pk_staff',
		u'pk_type',
		u'comment',
		u'data',
		u'importance',
		u'pk_patient',
		u'pk_context',
		u'due_date',
		u'expiry_date'
	]
	#------------------------------------------------------------
	def format(self):
		tt = u'%s: %s%s\n' % (
			gmDateTime.pydt_strftime (
				self._payload[self._idx['received_when']],
				format = '%A, %Y %B %d, %H:%M',
				accuracy = gmDateTime.acc_minutes
			),
			gmTools.bool2subst(self._payload[self._idx['is_virtual']], _('virtual message'), _('message')),
			gmTools.coalesce(self._payload[self._idx['pk_inbox_message']], u'', u' #%s ')
		)

		tt += u'%s: %s\n' % (
			self._payload[self._idx['l10n_category']],
			self._payload[self._idx['l10n_type']]
		)

		tt += u'%s %s %s\n' % (
			self._payload[self._idx['modified_by']],
			gmTools.u_right_arrow,
			gmTools.coalesce(self._payload[self._idx['provider']], _('everyone'))
		)

		tt += u'\n%s%s%s\n\n' % (
			gmTools.u_left_double_angle_quote,
			self._payload[self._idx['comment']],
			gmTools.u_right_double_angle_quote
		)

		tt += gmTools.coalesce (
			self._payload[self._idx['pk_patient']],
			u'',
			u'%s\n\n' % _('Patient #%s')
		)

		if self._payload[self._idx['due_date']] is not None:
			if self._payload[self._idx['is_overdue']]:
				template = _('Due: %s (%s ago)\n')
			else:
				template = _('Due: %s (in %s)\n')
			tt += template % (
				gmDateTime.pydt_strftime(self._payload[self._idx['due_date']], '%Y %b %d'),
				gmDateTime.format_interval_medically(self._payload[self._idx['interval_due']])
			)

		if self._payload[self._idx['expiry_date']] is not None:
			if self._payload[self._idx['is_expired']]:
				template = _('Expired: %s\n')
			else:
				template = _('Expires: %s\n')
			tt += template % gmDateTime.pydt_strftime(self._payload[self._idx['expiry_date']], '%Y %b %d')

		if self._payload[self._idx['data']] is not None:
			tt += self._payload[self._idx['data']][:150]
			if len(self._payload[self._idx['data']]) > 150:
				tt += gmTools.u_ellipsis

		return tt
#------------------------------------------------------------
def get_reminders(pk_patient=None, order_by=None):

	if order_by is None:
		order_by = u'%s ORDER BY due_date, importance DESC, received_when DESC'
	else:
		order_by = u'%%s ORDER BY %s' % order_by

	args = {'pat': pk_patient}
	where_parts = [
		u'pk_patient = %(pat)s',
		u'due_date IS NOT NULL'
	]

	cmd = u"SELECT * FROM dem.v_message_inbox WHERE %s" % (
		order_by % u' AND '.join(where_parts)
	)
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)

	return [ cInboxMessage(row = {'data': r, 'idx': idx, 'pk_field': 'pk_inbox_message'}) for r in rows ]

#------------------------------------------------------------
def get_overdue_messages(pk_patient=None, order_by=None):

	if order_by is None:
		order_by = u'%s ORDER BY due_date, importance DESC, received_when DESC'
	else:
		order_by = u'%%s ORDER BY %s' % order_by

	args = {'pat': pk_patient}
	where_parts = [
		u'pk_patient = %(pat)s',
		u'is_overdue IS TRUE'
	]

	cmd = u"SELECT * FROM dem.v_message_inbox WHERE %s" % (
		order_by % u' AND '.join(where_parts)
	)
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)

	return [ cInboxMessage(row = {'data': r, 'idx': idx, 'pk_field': 'pk_inbox_message'}) for r in rows ]

#------------------------------------------------------------
def get_inbox_messages(pk_staff=None, pk_patient=None, include_without_provider=False, exclude_expired=False, expired_only=False, overdue_only=False, unscheduled_only=False, exclude_unscheduled=False, order_by=None):

	if order_by is None:
		order_by = u'%s ORDER BY importance desc, received_when desc'
	else:
		order_by = u'%%s ORDER BY %s' % order_by

	args = {}
	where_parts = []

	if pk_staff is not None:
		if include_without_provider:
			where_parts.append(u'((pk_staff IN (%(staff)s, NULL)) OR (modified_by = (SELECT short_alias FROM dem.staff WHERE pk = %(staff)s)))')
		else:
			where_parts.append(u'((pk_staff = %(staff)s) OR (modified_by = (SELECT short_alias FROM dem.staff WHERE pk = %(staff)s)))')
		args['staff'] = pk_staff

	if pk_patient is not None:
		where_parts.append(u'pk_patient = %(pat)s')
		args['pat'] = pk_patient

	if exclude_expired:
		where_parts.append(u'is_expired IS FALSE')

	if expired_only:
		where_parts.append(u'is_expired IS TRUE')

	if overdue_only:
		where_parts.append(u'is_overdue IS TRUE')

	if unscheduled_only:
		where_parts.append(u'due_date IS NULL')

	if exclude_unscheduled:
		where_parts.append(u'due_date IS NOT NULL')

	cmd = _SQL_get_inbox_messages % (
		order_by % u' AND '.join(where_parts)
	)
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)

	return [ cInboxMessage(row = {'data': r, 'idx': idx, 'pk_field': 'pk_inbox_message'}) for r in rows ]
#------------------------------------------------------------
def create_inbox_message(message_type=None, subject=None, patient=None, staff=None):

	success, pk_type = gmTools.input2int(initial = message_type)
	if not success:
		pk_type = create_inbox_item_type(message_type = message_type)

	cmd = u"""
		INSERT INTO dem.message_inbox (
			fk_staff,
			fk_patient,
			fk_inbox_item_type,
			comment
		) VALUES (
			%(staff)s,
			%(pat)s,
			%(type)s,
			gm.nullify_empty_string(%(subject)s)
		)
		RETURNING pk
	"""
	args = {
		u'staff': staff,
		u'pat': patient,
		u'type': pk_type,
		u'subject': subject
	}
	rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}], return_data = True, get_col_idx = False)

	return cInboxMessage(aPK_obj = rows[0]['pk'])
#------------------------------------------------------------
def delete_inbox_message(inbox_message=None):
	args = {'pk': inbox_message}
	cmd = u"DELETE FROM dem.message_inbox WHERE pk = %(pk)s"
	gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])
	return True
#------------------------------------------------------------
def create_inbox_item_type(message_type=None, category=u'clinical'):

	# determine category PK
	success, pk_cat = gmTools.input2int(initial = category)
	if not success:
		args = {u'cat': category}
		cmd = u"""SELECT COALESCE (
			(SELECT pk FROM dem.inbox_item_category WHERE _(description) = %(cat)s),
			(SELECT pk FROM dem.inbox_item_category WHERE description = %(cat)s)
		) AS pk"""
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}])
		if rows[0]['pk'] is None:
			cmd = u"INSERT INTO dem.inbox_item_category (description) VALUES (%(cat)s) RETURNING pk"
			rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}], return_data = True)
			pk_cat = rows[0]['pk']
		else:
			pk_cat = rows[0]['pk']

	# find type PK or create type
	args = {u'cat': pk_cat, u'type': message_type}
	cmd = u"""SELECT COALESCE (
		(SELECT pk FROM dem.inbox_item_type where fk_inbox_item_category = %(cat)s and _(description) = %(type)s),
		(SELECT pk FROM dem.inbox_item_type where fk_inbox_item_category = %(cat)s and description = %(type)s)
	) AS pk"""
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}])
	if rows[0]['pk'] is None:
		cmd = u"""
			INSERT INTO dem.inbox_item_type (
				fk_inbox_item_category,
				description,
				is_user
			) VALUES (
				%(cat)s,
				%(type)s,
				TRUE
			) RETURNING pk"""
		rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}], return_data = True)

	return rows[0]['pk']

#============================================================
class cProviderInbox:
	def __init__(self, provider_id=None):
		if provider_id is None:
			self.__provider_id = gmStaff.gmCurrentProvider()['pk_staff']
		else:
			self.__provider_id = provider_id
	#--------------------------------------------------------
	def delete_message(self, pk=None):
		return delete_inbox_message(inbox_message = pk)
	#--------------------------------------------------------
	def add_message(message_type=None, subject=None, patient=None):
		return create_inbox_message (
			message_type = message_type,
			subject = subject,
			patient = patient,
			staff = self.__provider_id
		)
	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def get_messages(self, pk_patient=None, include_without_provider=False, exclude_expired=False, expired_only=False, overdue_only=False, unscheduled_only=False, exclude_unscheduled=False, order_by=None):
		return get_inbox_messages (
			pk_staff = self.__provider_id,
			pk_patient = pk_patient,
			include_without_provider = include_without_provider,
			exclude_expired = exclude_expired,
			expired_only = expired_only,
			overdue_only = overdue_only,
			unscheduled_only = unscheduled_only,
			exclude_unscheduled = exclude_unscheduled,
			order_by = order_by
		)

	def _set_messages(self, messages):
		return

	messages = property(get_messages, _set_messages)

#============================================================
# dynamic hints API
#------------------------------------------------------------
_SQL_get_dynamic_hints = u"SELECT *, xmin AS xmin_auto_hint FROM ref.auto_hint WHERE %s"

class cDynamicHint(gmBusinessDBObject.cBusinessDBObject):
	"""Represents dynamic hints to be run against the database."""

	_cmd_fetch_payload = _SQL_get_dynamic_hints % u"pk = %s"
	_cmds_store_payload = [
		u"""UPDATE ref.auto_hint SET
				is_active = %(is_active)s
			WHERE
				pk = %(pk)s
					AND
				xmin = %(xmin_auto_hint)s
			RETURNING
				pk,
				xmin AS xmin_auto_hint
		"""
	]
	_updatable_fields = [
		u'is_active'
	]
	#--------------------------------------------------------
	def format(self):
		txt = u'%s               [#%s]\n' % (
			gmTools.bool2subst(self._payload[self._idx['is_active']], _('Active clinical hint'), _('Inactive clinical hint')),
			self._payload[self._idx['pk']]
		)
		txt += u'\n'
		txt += u'%s\n\n' % self._payload[self._idx['title']]
		txt += _('Source: %s\n') % self._payload[self._idx['source']]
		txt += _('Language: %s\n') % self._payload[self._idx['lang']]
		txt += u'\n'
		txt += u'%s\n' % gmTools.wrap(self._payload[self._idx['hint']], width = 50, initial_indent = u' ', subsequent_indent = u' ')
		txt += u'\n'
		txt += u'%s\n' % gmTools.wrap (
			gmTools.coalesce(self._payload[self._idx['url']], u''),
			width = 50,
			initial_indent = u' ',
			subsequent_indent = u' '
		)
		txt += u'\n'
		txt += u'%s\n' % gmTools.wrap(self._payload[self._idx['query']], width = 50, initial_indent = u' ', subsequent_indent = u' ')
		return txt

#------------------------------------------------------------
def get_dynamic_hints(order_by=None):
	if order_by is None:
		order_by = u'true'
	else:
		order_by = u'true ORDER BY %s' % order_by

	cmd = _SQL_get_dynamic_hints % order_by
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd}], get_col_idx = True)
	return [ cDynamicHint(row = {'data': r, 'idx': idx, 'pk_field': 'pk'}) for r in rows ]
#------------------------------------------------------------
#def create_xxx(xxx=None, xxx=None):
#
#	args = {
#		u'xxx': xxx,
#		u'xxx': xxx
#	}
#	cmd = u"""
#		INSERT INTO xxx.xxx (
#			xxx,
#			xxx,
#			xxx
#		) VALUES (
#			%(xxx)s,
#			%(xxx)s,
#			gm.nullify_empty_string(%(xxx)s)
#		)
#		RETURNING pk
#	"""
#	rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}], return_data = True, get_col_idx = False)
#
#	return cDynamicHint(aPK_obj = rows[0]['pk'])
#------------------------------------------------------------
#def delete_xxx(xxx=None):
#	args = {'pk': xxx}
#	cmd = u"DELETE FROM xxx.xxx WHERE pk = %(pk)s"
#	gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])
#	return True
#------------------------------------------------------------

#------------------------------------------------------------
def get_hints_for_patient(pk_identity=None):
	conn = gmPG2.get_connection()
	curs = conn.cursor()
	curs.callproc('clin.get_hints_for_patient', [pk_identity])
	rows = curs.fetchall()
	idx = gmPG2.get_col_indices(curs)
	return [ cDynamicHint(row = {'data': r, 'idx': idx, 'pk_field': 'pk'}) for r in rows ]

#============================================================
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	from Gnumed.pycommon import gmI18N

	gmI18N.activate_locale()
	gmI18N.install_domain()

	#---------------------------------------
	def test_inbox():
		gmStaff.gmCurrentProvider(provider = gmStaff.cStaff())
		inbox = cProviderInbox()
		for msg in inbox.messages:
			print msg
	#---------------------------------------
	def test_msg():
		msg = cInboxMessage(aPK_obj = 1)
		print msg
	#---------------------------------------
	def test_create_type():
		print create_inbox_item_type(message_type = 'test')
	#---------------------------------------
	def test_due():
		for msg in get_overdue_messages(pk_patient = 12):
			print msg.format()
	#---------------------------------------
	def test_auto_hints():
		for row in get_dynamic_hints(pk_identity = 13):
			print row
	#---------------------------------------
	#test_inbox()
	#test_msg()
	#test_create_type()
	#test_due()
	test_auto_hints()

#============================================================
