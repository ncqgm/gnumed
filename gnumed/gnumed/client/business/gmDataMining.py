"""GNUmed data mining middleware."""
#============================================================
__license__ = "GPL v2 or later"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"


import sys
import logging


# setup translation
if __name__ == '__main__':
	sys.path.insert(0, '../../')
	# we are the main script, setup a fake _() for now,
	# such that it can be used in module level definitions
	_ = lambda x:x
else:
	# we are being imported from elsewhere, say, mypy or some such
	try:
		# do we already have _() ?
		_
	except NameError:
		# no, setup i18n handling
		from Gnumed.pycommon import gmI18N
		gmI18N.activate_locale()
		gmI18N.install_domain()
from Gnumed.pycommon import gmPG2
from Gnumed.pycommon import gmDispatcher

_log = logging.getLogger('gm.reports')

#============================================================
def report_exists(name=None):
	rows = gmPG2.run_ro_queries(queries = [{
		'sql': 'SELECT EXISTS(SELECT 1 FROM cfg.report_query WHERE label = %(name)s)',
		'args': {'name': name}
	}])
	return rows[0][0]

#--------------------------------------------------------
def save_report_definition(name=None, query=None, overwrite=False):
	if not overwrite:
		if report_exists(name=name):
			return False

	args = {'name': name, 'query': query}
	queries = [
		{'sql': 'DELETE FROM cfg.report_query WHERE label = %(name)s', 'args': args},
		{'sql': 'INSERT INTO cfg.report_query (label, cmd) VALUES (%(name)s, %(query)s)', 'args': args}
	]
	gmPG2.run_rw_queries(queries = queries)
	return True

#--------------------------------------------------------
def delete_report_definition(name=None):
	queries = [{
		'sql': 'DELETE FROM cfg.report_query WHERE label = %(name)s',
		'args': {'name': name}
	}]
	gmPG2.run_rw_queries(queries=queries)
	return True

#--------------------------------------------------------
def run_report_query(query=None, limit=None, pk_identity=None):
	"""Returns (status, hint, cols, rows)"""

	PATIENT_ID_TOKEN = '$<ID_ACTIVE_PATIENT>$'
	if limit is None:
		limit = ''
	else:
		limit = 'LIMIT %s' % limit

	# does user want to insert current patient ID ?
	if query.find(PATIENT_ID_TOKEN) == -1:
		wrapper_query = """
			SELECT * FROM (
				%%s
			) AS user_query
			%s
		""" % limit
	else:
		# she does, but is it possible ?
		if pk_identity is None:
			gmDispatcher.send('statustext', msg = _('Query needs active patient.'), beep = True)
			cols = [_('Error')]
			rows = [
				[_('Active patient query')],
				[''],
				[_('This query requires a patient to be active in the client.')],
				[''],
				[_('Please activate the patient you are interested')],
				[_('in and re-run the query.')]
			]
			return (False, 'pk_identity', cols, rows)

		query = query.replace(PATIENT_ID_TOKEN, str(pk_identity))
		wrapper_query = """
			SELECT %s AS pk_patient, * FROM (
				%%s
			) AS user_query
			%s
		""" % (pk_identity, limit)

	wrapped_query = wrapper_query % query
	_log.debug('running report query:')
	_log.debug(wrapped_query)

	try:
		# read-only for safety reasons
		rows = gmPG2.run_ro_queries(queries = [{'sql': wrapped_query}])
	except Exception:
		_log.exception('report query failed')
		gmDispatcher.send('statustext', msg = _('The query failed.'), beep = True)
		cols = [_('Error')]
		t, v = sys.exc_info()[:2]
		rows = [
			[_('The query failed.')],
			[''],
			[str(t)]
		]
		for line in str(v).split('\n'):
			rows.append([line])
		rows.append([''])
		for line in query.split('\n'):
			rows.append([line])
		return (False, 'query failed', cols, rows)

	if rows:
		cols = list(rows[0].keys())
	else:
		cols = [_('No results.')]

	return (True, None, cols, rows)

#============================================================
if __name__ == '__main__':

	if len(sys.argv) > 1 and sys.argv[1] == 'test':

		# setup a real translation
		del _
		from Gnumed.pycommon import gmI18N
		gmI18N.activate_locale()
		gmI18N.install_domain()

		test_report = 'test suite report'
		test_query = 'select 1 as test_suite_report_result'

		print("delete (should work):", delete_report_definition(name = test_report))
		print("check (should return False):", report_exists(name = test_report))
		print("save (should work):", save_report_definition(name = test_report, query = test_query))
		print("save (should fail):", save_report_definition(name = test_report, query = test_query, overwrite = False))
		print("save (should work):", save_report_definition(name = test_report, query = test_query, overwrite = True))
		print("delete (should work):", delete_report_definition(name = test_report))
		print("check (should return False):", report_exists(name = test_report))
#============================================================
