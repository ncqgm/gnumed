# -*- coding: utf-8 -*-
"""GNUmed problem related business object.

license: GPL v2 or later
"""
#============================================================
__author__ = "<karsten.hilbert@gmx.net>"

import sys
import logging


if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x
from Gnumed.pycommon import gmPG2
from Gnumed.pycommon import gmI18N
from Gnumed.pycommon import gmBusinessDBObject
from Gnumed.pycommon import gmExceptions

from Gnumed.business import gmCoding
from Gnumed.business import gmDocuments
from Gnumed.business import gmEpisode
from Gnumed.business import gmHealthIssue

_log = logging.getLogger('gm.emr')

#============================================================
# problem API
#============================================================
class cProblem(gmBusinessDBObject.cBusinessDBObject):
	"""Represents one problem.

	problems are the aggregation of
		.clinically_relevant=True issues and
		.is_open=True episodes
	"""
	_cmd_fetch_payload = ''					# will get programmatically defined in __init__
	_cmds_store_payload:list = ["select 1"]
	_updatable_fields:list = []

	#--------------------------------------------------------
	def __init__(self, aPK_obj=None, try_potential_problems:bool=False):
		"""Initialize.

		aPK_obj must contain the keys
			pk_patient
			pk_episode
			pk_health_issue
		"""
		if aPK_obj is None:
			raise gmExceptions.ConstructorError('cannot instatiate cProblem for PK: [%s]' % (aPK_obj))

		# As problems are rows from a view of different emr struct items,
		# the PK can't be a single field and, as some of the values of the
		# composed PK may be None, they must be queried using 'is null',
		# so we must programmatically construct the SQL query
		where_parts = []
		pk = {}
		for col_name in aPK_obj:
			val = aPK_obj[col_name]
			if val is None:
				where_parts.append('%s IS NULL' % col_name)
			else:
				where_parts.append('%s = %%(%s)s' % (col_name, col_name))
				pk[col_name] = val

		# try to instantiate from true problem view
		cProblem._cmd_fetch_payload = """
			SELECT *, False as is_potential_problem
			FROM clin.v_problem_list
			WHERE %s""" % ' AND '.join(where_parts)

		try:
			gmBusinessDBObject.cBusinessDBObject.__init__(self, aPK_obj = pk)
			return

		except gmExceptions.ConstructorError:
			_log.exception('actual problem not found, trying "potential" problems')
			if try_potential_problems is False:
				raise

		# try to instantiate from potential-problems view
		cProblem._cmd_fetch_payload = """
			SELECT *, True as is_potential_problem
			FROM clin.v_potential_problem_list
			WHERE %s""" % ' AND '.join(where_parts)
		gmBusinessDBObject.cBusinessDBObject.__init__(self, aPK_obj=pk)

	#--------------------------------------------------------
	@classmethod
	def from_episode(cls, episode:'gmEpisode.cEpisode', allow_closed:bool=False) -> 'cProblem':
		"""Initialize problem from episode"""
		return cls (
			aPK_obj = {
				'pk_patient': episode['pk_patient'],
				'pk_health_issue': episode['pk_health_issue'],
				'pk_episode': episode['pk_episode']
			},
			try_potential_problems = allow_closed
		)

	#--------------------------------------------------------
	@classmethod
	def from_health_issue(cls, health_issue, allow_irrelevant:bool=False) -> 'cProblem':
		"""Initialize problem from health issue."""
		return cls (
			aPK_obj = {
				'pk_patient': health_issue['pk_patient'],
				'pk_health_issue': health_issue['pk_health_issue'],
				'pk_episode': None
			},
			try_potential_problems = allow_irrelevant
		)

	#--------------------------------------------------------
	@classmethod
	def from_issue_or_episode(cls, issue_or_episode, allow_all:bool=False) -> 'cProblem':
		if isinstance(issue_or_episode, cProblem):
			return issue_or_episode

		pk_obj = {
			'pk_patient': issue_or_episode['pk_patient'],
			'pk_health_issue': issue_or_episode['pk_health_issue']
		}
		try:
			pk_obj['pk_episode'] = issue_or_episode['pk_episode']
		except KeyError:
			pk_obj['pk_episode'] = None
		return cls(aPK_obj = pk_obj, try_potential_problems = allow_all)

	#--------------------------------------------------------
	def __get_as_episode(self):
		"""
		Retrieve the cEpisode instance equivalent to this problem.
		The problem's type attribute must be 'episode'
		"""
		if self._payload['type'] != 'episode':
			_log.error('cannot convert problem [%s] of type [%s] to episode' % (self._payload['problem'], self._payload['type']))
			return None

		return gmEpisode.cEpisode(aPK_obj = self._payload['pk_episode'])

	as_episode = property(__get_as_episode)

	#--------------------------------------------------------
	def __get_as_health_issue(self):
		"""
		Retrieve the cHealthIssue instance equivalent to this problem.
		The problem's type attribute must be 'issue'
		"""
		if self._payload['type'] != 'issue':
			_log.error('cannot convert problem [%s] of type [%s] to health issue' % (self._payload['problem'], self._payload['type']))
			return None

		return gmHealthIssue.cHealthIssue(aPK_obj = self._payload['pk_health_issue'])

	as_health_issue = property(__get_as_health_issue)

	#--------------------------------------------------------
	def get_visual_progress_notes(self, encounter_id:int=None):
		if self._payload['type'] == 'issue':
			latest = gmHealthIssue.cHealthIssue(aPK_obj = self._payload['pk_health_issue']).latest_episode
			if latest is None:
				return []

			pk_episode = latest['pk_episode']
		else:
			pk_episode = self._payload['pk_episode']
		doc_folder = gmDocuments.cDocumentFolder(aPKey = self._payload['pk_patient'])
		return doc_folder.get_visual_progress_notes(episodes = [pk_episode])

	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def get_diagnostic_certainty_description(self):
		from Gnumed.business.gmHealthIssue import diagnostic_certainty_classification2str
		return diagnostic_certainty_classification2str(self._payload['diagnostic_certainty_classification'])

	diagnostic_certainty_description = property(get_diagnostic_certainty_description)

	#--------------------------------------------------------
	def _get_generic_codes(self):
		if self._payload['type'] == 'issue':
			cmd = """
				SELECT * FROM clin.v_linked_codes WHERE
					item_table = 'clin.lnk_code2h_issue'::regclass
						AND
					pk_item = %(item)s
			"""
			args = {'item': self._payload['pk_health_issue']}
		else:
			cmd = """
				SELECT * FROM clin.v_linked_codes WHERE
					item_table = 'clin.lnk_code2episode'::regclass
						AND
					pk_item = %(item)s
			"""
			args = {'item': self._payload['pk_episode']}

		rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
		return [ gmCoding.cGenericLinkedCode(row = {'data': r, 'pk_field': 'pk_lnk_code2item'}) for r in rows ]

	generic_codes = property(_get_generic_codes)

#============================================================
# main - unit testing
#------------------------------------------------------------
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	gmI18N.activate_locale()
	gmI18N.install_domain('gnumed')

	#--------------------------------------------------------
	# define tests
	#--------------------------------------------------------
	def test_problem():
		print("\nProblem test")
		print("------------")
		prob = cProblem(aPK_obj={'pk_patient': 12, 'pk_health_issue': 1, 'pk_episode': None})
		print(prob)
		fields = prob.get_fields()
		for field in fields:
			print(field, ':', prob[field])
		print('\nupdatable:', prob.get_updatable_fields())
		epi = prob.as_episode
		print('\nas episode:')
		if epi is not None:
			for field in epi.get_fields():
				print('   .%s : %s' % (field, epi[field]))

	#--------------------------------------------------------
	gmPG2.request_login_params(setup_pool = True)

	test_problem()
