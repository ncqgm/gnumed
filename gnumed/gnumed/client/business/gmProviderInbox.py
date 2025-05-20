# -*- coding: latin-1 -*-
"""GNUmed provider inbox middleware.

This should eventually end up in a class cPractice.
"""
#============================================================
__license__ = "GPL"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"


import sys
import logging


if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x
from Gnumed.pycommon import gmPG2
from Gnumed.pycommon import gmBusinessDBObject
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmDateTime

from Gnumed.business import gmStaff

_log = logging.getLogger('gm.inbox')

#============================================================
# provider message inbox
#------------------------------------------------------------
_SQL_get_inbox_messages = """SELECT * FROM dem.v_message_inbox d_vi WHERE %s"""

class cInboxMessage(gmBusinessDBObject.cBusinessDBObject):

	_cmd_fetch_payload = _SQL_get_inbox_messages % "pk_inbox_message = %s"
	_cmds_store_payload = [
		"""
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
		'pk_staff',
		'pk_type',
		'comment',
		'data',
		'importance',
		'pk_patient',
		'pk_context',
		'due_date',
		'expiry_date'
	]
	#------------------------------------------------------------
	def format(self, with_patient=True):
		tt = '%s: %s%s\n' % (
			self._payload['received_when'].strftime('%A, %Y %b %d, %H:%M'),
			gmTools.bool2subst(self._payload['is_virtual'], _('virtual message'), _('message')),
			gmTools.coalesce(self._payload['pk_inbox_message'], '', ' #%s ')
		)

		tt += '%s: %s\n' % (
			self._payload['l10n_category'],
			self._payload['l10n_type']
		)

		tt += '%s %s %s\n' % (
			self._payload['modified_by'],
			gmTools.u_arrow2right,
			gmTools.coalesce(self._payload['provider'], _('everyone'))
		)

		tt += '\n%s%s%s\n\n' % (
			gmTools.u_left_double_angle_quote,
			self._payload['comment'],
			gmTools.u_right_double_angle_quote
		)

		if with_patient and self._payload['pk_patient']:
			tt += _('Patient: %s, %s%s %s   #%s\n' % (
				self._payload['lastnames'],
				self._payload['firstnames'],
				gmTools.coalesce(self._payload['l10n_gender'], '', ' (%s)'),
				gmDateTime.pydt_strftime(self._payload['dob'], '%Y %b %d', none_str = ''),
				self._payload['pk_patient']
			))

		if self._payload['due_date']:
			if self._payload['is_overdue']:
				template = _('Due: %s (%s ago)\n')
			else:
				template = _('Due: %s (in %s)\n')
			tt += template % (
				self._payload['due_date'].strftime('%Y %b %d'),
				gmDateTime.format_interval_medically(self._payload['interval_due'])
			)

		if self._payload['expiry_date']:
			if self._payload['is_expired']:
				template = _('Expired: %s\n')
			else:
				template = _('Expires: %s\n')
			tt += template % self._payload['expiry_date'].strftime('%Y %b %d')

		if self._payload['data']:
			tt += self._payload['data'][:150]
			if len(self._payload['data']) > 150:
				tt += gmTools.u_ellipsis

		return tt

#------------------------------------------------------------
def get_reminders(pk_patient=None, order_by=None, return_pks=False):

	if order_by is None:
		order_by = '%s ORDER BY due_date, importance DESC, received_when DESC'
	else:
		order_by = '%%s ORDER BY %s' % order_by

	args = {'pat': pk_patient}
	where_parts = [
		'pk_patient = %(pat)s',
		'due_date IS NOT NULL'
	]

	cmd = "SELECT * FROM dem.v_message_inbox WHERE %s" % (
		order_by % ' AND '.join(where_parts)
	)
	_log.debug('SQL: %s', cmd)
	_log.debug('args: %s', args)
	rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
	if return_pks:
		return [ r['pk_inbox_message'] for r in rows ]
	return [ cInboxMessage(row = {'data': r, 'pk_field': 'pk_inbox_message'}) for r in rows ]

#------------------------------------------------------------
def get_overdue_messages(pk_patient=None, order_by=None, return_pks=False):

	if order_by is None:
		order_by = '%s ORDER BY due_date, importance DESC, received_when DESC'
	else:
		order_by = '%%s ORDER BY %s' % order_by

	args = {'pat': pk_patient}
	where_parts = [
		'pk_patient = %(pat)s',
		'is_overdue IS TRUE'
	]

	cmd = "SELECT * FROM dem.v_message_inbox WHERE %s" % (
		order_by % ' AND '.join(where_parts)
	)
	_log.debug('SQL: %s', cmd)
	_log.debug('args: %s', args)
	rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
	if return_pks:
		return [ r['pk_inbox_message'] for r in rows ]
	return [ cInboxMessage(row = {'data': r, 'pk_field': 'pk_inbox_message'}) for r in rows ]

#------------------------------------------------------------
def get_relevant_messages(pk_staff=None, pk_patient=None, include_without_provider=False, order_by=None, return_pks=False):

	if order_by is None:
		order_by = '%s ORDER BY importance desc, received_when desc'
	else:
		order_by = '%%s ORDER BY %s' % order_by

	args = {}
	where_parts = []

	if pk_staff is not None:
		if include_without_provider:
			where_parts.append('((pk_staff IN (%(staff)s, NULL)) OR (modified_by = (SELECT short_alias FROM dem.staff WHERE pk = %(staff)s)))')
		else:
			where_parts.append('((pk_staff = %(staff)s) OR (modified_by = (SELECT short_alias FROM dem.staff WHERE pk = %(staff)s)))')
		args['staff'] = pk_staff

	if pk_patient is not None:
		where_parts.append('pk_patient = %(pat)s')
		args['pat'] = pk_patient

	where_parts.append("""
		-- messages which have no due date and are not expired
		((due_date IS NULL) AND ((expiry_date IS NULL) OR (expiry_date > now())))
			OR
		-- messages which are due and not expired
		((due_date IS NOT NULL) AND (due_date < now()) AND ((expiry_date IS NULL) OR (expiry_date > now())))
	""")

	cmd = _SQL_get_inbox_messages % (
		order_by % ' AND '.join(where_parts)
	)
	_log.debug('SQL: %s', cmd)
	_log.debug('args: %s', args)
	rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
	if return_pks:
		return [ r['pk_inbox_message'] for r in rows ]
	return [ cInboxMessage(row = {'data': r, 'pk_field': 'pk_inbox_message'}) for r in rows ]

#------------------------------------------------------------
def get_inbox_messages(pk_staff=None, pk_patient=None, include_without_provider=False, exclude_expired=False, expired_only=False, overdue_only=False, unscheduled_only=False, exclude_unscheduled=False, order_by=None, return_pks=False):

	if order_by is None:
		order_by = '%s ORDER BY importance desc, received_when desc'
	else:
		order_by = '%%s ORDER BY %s' % order_by

	args = {}
	where_parts = []

	if pk_staff is not None:
		if include_without_provider:
			where_parts.append('((pk_staff IN (%(staff)s, NULL)) OR (modified_by = (SELECT short_alias FROM dem.staff WHERE pk = %(staff)s)))')
		else:
			where_parts.append('((pk_staff = %(staff)s) OR (modified_by = (SELECT short_alias FROM dem.staff WHERE pk = %(staff)s)))')
		args['staff'] = pk_staff

	if pk_patient is not None:
		where_parts.append('pk_patient = %(pat)s')
		args['pat'] = pk_patient

	if exclude_expired:
		where_parts.append('is_expired IS FALSE')

	if expired_only:
		where_parts.append('is_expired IS TRUE')

	if overdue_only:
		where_parts.append('is_overdue IS TRUE')

	if unscheduled_only:
		where_parts.append('due_date IS NULL')

	if exclude_unscheduled:
		where_parts.append('due_date IS NOT NULL')

	cmd = _SQL_get_inbox_messages % (
		order_by % ' AND '.join(where_parts)
	)
	_log.debug('SQL: %s', cmd)
	_log.debug('args: %s', args)
	rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
	if return_pks:
		return [ r['pk_inbox_message'] for r in rows ]
	return [ cInboxMessage(row = {'data': r, 'pk_field': 'pk_inbox_message'}) for r in rows ]

#------------------------------------------------------------
def create_inbox_message(message_type=None, subject=None, patient=None, staff=None, message_category='clinical'):

	success, pk_type = gmTools.input2int(initial = message_type)
	if not success:
		pk_type = create_inbox_item_type(message_type = message_type, category = message_category)

	cmd = """
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
		'staff': staff,
		'pat': patient,
		'type': pk_type,
		'subject': subject
	}
	rows = gmPG2.run_rw_queries(queries = [{'sql': cmd, 'args': args}], return_data = True)
	return cInboxMessage(aPK_obj = rows[0]['pk'])

#------------------------------------------------------------
def delete_inbox_message(inbox_message=None):
	args = {'pk': inbox_message}
	cmd = "DELETE FROM dem.message_inbox WHERE pk = %(pk)s"
	gmPG2.run_rw_queries(queries = [{'sql': cmd, 'args': args}])
	return True

#------------------------------------------------------------
def create_inbox_item_type(message_type=None, category='clinical'):

	# determine category PK
	success, pk_cat = gmTools.input2int(initial = category)
	if not success:
		args = {'cat': category}
		cmd = """SELECT COALESCE (
			(SELECT pk FROM dem.inbox_item_category WHERE _(description) = %(cat)s),
			(SELECT pk FROM dem.inbox_item_category WHERE description = %(cat)s)
		) AS pk"""
		rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
		if rows[0]['pk'] is None:
			cmd = "INSERT INTO dem.inbox_item_category (description) VALUES (%(cat)s) RETURNING pk"
			rows = gmPG2.run_rw_queries(queries = [{'sql': cmd, 'args': args}], return_data = True)
			pk_cat = rows[0]['pk']
		else:
			pk_cat = rows[0]['pk']

	# find type PK or create type
	args = {'pk_cat': pk_cat, 'type': message_type}
	cmd = """SELECT COALESCE (
		(SELECT pk FROM dem.inbox_item_type where fk_inbox_item_category = %(pk_cat)s AND _(description) = %(type)s),
		(SELECT pk FROM dem.inbox_item_type where fk_inbox_item_category = %(pk_cat)s AND description = %(type)s)
	) AS pk"""
	rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
	if rows[0]['pk'] is None:
		cmd = """
			INSERT INTO dem.inbox_item_type (
				fk_inbox_item_category,
				description,
				is_user
			) VALUES (
				%(pk_cat)s,
				%(type)s,
				TRUE
			) RETURNING pk"""
		rows = gmPG2.run_rw_queries(queries = [{'sql': cmd, 'args': args}], return_data = True)

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
	def add_message(self, message_type=None, subject=None, patient=None):
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

	messages = property(get_messages)

	#--------------------------------------------------------
	def get_relevant_messages(self, pk_patient=None, include_without_provider=True):
		return get_relevant_messages (
			pk_staff = self.__provider_id,
			pk_patient = pk_patient,
			include_without_provider = include_without_provider
		)

#============================================================
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	from Gnumed.pycommon import gmI18N

	gmI18N.activate_locale()
	gmI18N.install_domain()

	from Gnumed.pycommon import gmLog2
	gmLog2.print_logfile_name()

	gmPG2.request_login_params(setup_pool = True)

	#---------------------------------------
	def test_inbox():
		gmStaff.gmCurrentProvider(provider = gmStaff.cStaff())
		inbox = cProviderInbox()
		for msg in inbox.messages:
			print(msg)
	#---------------------------------------
	def test_msg():
		msg = cInboxMessage(aPK_obj = 1)
		print(msg)
	#---------------------------------------
	def test_create_type():
		print(create_inbox_item_type(message_type = 'test'))
	#---------------------------------------
	def test_due():
		for msg in get_overdue_messages(pk_patient = 12):
			print(msg.format())
	#---------------------------------------
	#test_inbox()
	#test_msg()
	#test_create_type()
	test_due()

#============================================================
