# -*- coding: utf-8 -*-
"""GNUmed health related business object.

license: GPL v2 or later
"""
#============================================================
__author__ = "Carlos Moro <cfmoro1976@yahoo.es>, <karsten.hilbert@gmx.net>"

import sys
import datetime
import logging
import inspect
import io
import os


if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x
from Gnumed.pycommon import gmPG2
from Gnumed.pycommon import gmI18N
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmDateTime
from Gnumed.pycommon import gmBusinessDBObject
from Gnumed.pycommon import gmExceptions
from Gnumed.pycommon import gmMatchProvider

from Gnumed.business import gmClinNarrative
from Gnumed.business import gmSoapDefs
from Gnumed.business import gmCoding
from Gnumed.business import gmPraxis
from Gnumed.business import gmOrganization
from Gnumed.business import gmExternalCare
from Gnumed.business import gmDocuments


_log = logging.getLogger('gm.emr')

#============================================================
# diagnostic certainty classification
#============================================================
__diagnostic_certainty_classification_map = None

def diagnostic_certainty_classification2str(classification):

	global __diagnostic_certainty_classification_map

	if __diagnostic_certainty_classification_map is None:
		__diagnostic_certainty_classification_map = {
			None: '',
			'A': _('A: Sign'),
			'B': _('B: Cluster of signs'),
			'C': _('C: Syndromic diagnosis'),
			'D': _('D: Scientific diagnosis')
		}

	try:
		return __diagnostic_certainty_classification_map[classification]
	except KeyError:
		return _('<%s>: unknown diagnostic certainty classification') % classification

#============================================================
# Health Issues API
#============================================================
laterality2str = {
	None: '?',
	'na': '',
	'sd': _('bilateral'),
	'ds': _('bilateral'),
	's': _('left'),
	'd': _('right')
}

#============================================================
class cHealthIssue(gmBusinessDBObject.cBusinessDBObject):
	"""Represents one health issue."""

	#_cmd_fetch_payload = u"select *, xmin_health_issue from clin.v_health_issues where pk_health_issue=%s"
	_cmd_fetch_payload = "select * from clin.v_health_issues where pk_health_issue = %s"
	_cmds_store_payload = [
		"""update clin.health_issue set
				description = %(description)s,
				summary = gm.nullify_empty_string(%(summary)s),
				age_noted = %(age_noted)s,
				laterality = gm.nullify_empty_string(%(laterality)s),
				grouping = gm.nullify_empty_string(%(grouping)s),
				diagnostic_certainty_classification = gm.nullify_empty_string(%(diagnostic_certainty_classification)s),
				is_active = %(is_active)s,
				clinically_relevant = %(clinically_relevant)s,
				is_confidential = %(is_confidential)s,
				is_cause_of_death = %(is_cause_of_death)s
			WHERE
				pk = %(pk_health_issue)s
					AND
				xmin = %(xmin_health_issue)s""",
		"select xmin as xmin_health_issue from clin.health_issue where pk = %(pk_health_issue)s"
	]
	_updatable_fields = [
		'description',
		'summary',
		'grouping',
		'age_noted',
		'laterality',
		'is_active',
		'clinically_relevant',
		'is_confidential',
		'is_cause_of_death',
		'diagnostic_certainty_classification'
	]

	#--------------------------------------------------------
	def __init__(self, aPK_obj=None, encounter=None, name='xxxDEFAULTxxx', patient=None, row=None):
		pk = aPK_obj

		if (pk is not None) or (row is not None):
			gmBusinessDBObject.cBusinessDBObject.__init__(self, aPK_obj=pk, row=row)
			return

		if patient is None:
			cmd = """select *, xmin_health_issue from clin.v_health_issues
					where
						description = %(desc)s
							and
						pk_patient = (select fk_patient from clin.encounter where pk = %(enc)s)"""
		else:
			cmd = """select *, xmin_health_issue from clin.v_health_issues
					where
						description = %(desc)s
							and
						pk_patient = %(pat)s"""

		queries = [{'cmd': cmd, 'args': {'enc': encounter, 'desc': name, 'pat': patient}}]
		rows, idx = gmPG2.run_ro_queries(queries = queries,	get_col_idx = True)

		if len(rows) == 0:
			raise gmExceptions.NoSuchBusinessObjectError('no health issue for [enc:%s::desc:%s::pat:%s]' % (encounter, name, patient))

		pk = rows[0][0]
		r = {'idx': idx, 'data': rows[0], 'pk_field': 'pk_health_issue'}

		gmBusinessDBObject.cBusinessDBObject.__init__(self, row=r)

	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	@classmethod
	def from_problem(cls, problem:'cProblem') -> 'cHealthIssue':
		"""Initialize health issue from issue-type problem."""
		if isinstance(problem, cHealthIssue):
			return problem

		assert isinstance(problem, cProblem), 'cannot convert [%s] to health issue' % problem
		assert problem['type'] == 'issue', 'cannot convert [%s] to health issue' % problem
		return cls(aPK_obj = problem['pk_health_issue'])

	#--------------------------------------------------------
	def rename(self, description:str=None) -> bool:
		"""Rename health issue.

		Args:
			description: the new descriptive name for the issue
		"""
		if description.strip() == '':
			return False

		# update the issue description
		old_description = self._payload[self._idx['description']]
		self._payload[self._idx['description']] = description.strip()
		self._is_modified = True
		successful, data = self.save_payload()
		if not successful:
			_log.error('cannot rename health issue [%s] with [%s]' % (self, description))
			self._payload[self._idx['description']] = old_description
			return False

		return True

	#--------------------------------------------------------
	def get_episodes(self) -> list['cEpisode']:
		"""The episodes linked to this health issue."""
		cmd = "SELECT * FROM clin.v_pat_episodes WHERE pk_health_issue = %(pk)s"
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': {'pk': self.pk_obj}}], get_col_idx = True)
		return [ cEpisode(row = {'data': r, 'idx': idx, 'pk_field': 'pk_episode'})  for r in rows ]

	episodes = property(get_episodes)

	#--------------------------------------------------------
	def close_expired_episode(self, ttl:int=180) -> bool:
		"""Close open episode if "older" than the Time To Live.

		Args:
			ttl: maximum "age" of episode in days
		"""
		open_episode = self.open_episode
		if open_episode is None:
			return True

		#clinical_end = open_episode.best_guess_clinical_end_date
		clinical_end = open_episode.latest_access_date		# :-/
		ttl = datetime.timedelta(ttl)
		now = datetime.datetime.now(tz = clinical_end.tzinfo)
		if (clinical_end + ttl) > now:
			return False

		open_episode['episode_open'] = False
		success, data = open_episode.save_payload()
		if success:
			return True

		return False

	#--------------------------------------------------------
	def close_episode(self) -> bool:
		"""Unconditionally close the open episode, if any."""
		open_episode = self.get_open_episode()
		open_episode['episode_open'] = False
		success_state, data = open_episode.save_payload()
		return success_state

	#--------------------------------------------------------
	def get_open_episode(self) -> 'cEpisode':
		cmd = "select pk from clin.episode where fk_health_issue = %s and is_open IS True LIMIT 1"
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': [self.pk_obj]}])
		if rows:
			return cEpisode(aPK_obj = rows[0][0])

		return None

	#--------------------------------------------------------
	def age_noted_human_readable(self):
		if self._payload[self._idx['age_noted']] is None:
			return '<???>'

		# since we've already got an interval we are bound to use it,
		# further transformation will only introduce more errors,
		# later we can improve this deeper inside
		return gmDateTime.format_interval_medically(self._payload[self._idx['age_noted']])

	#--------------------------------------------------------
	def add_code(self, pk_code=None):
		"""<pk_code> must be a value from ref.coding_system_root.pk_coding_system (clin.lnk_code2item_root.fk_generic_code)"""
		cmd = "INSERT INTO clin.lnk_code2h_issue (fk_item, fk_generic_code) values (%(item)s, %(code)s)"
		args = {
			'item': self._payload[self._idx['pk_health_issue']],
			'code': pk_code
		}
		rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])
		return True

	#--------------------------------------------------------
	def remove_code(self, pk_code=None):
		"""<pk_code> must be a value from ref.coding_system_root.pk_coding_system (clin.lnk_code2item_root.fk_generic_code)"""
		cmd = "DELETE FROM clin.lnk_code2h_issue WHERE fk_item = %(item)s AND fk_generic_code = %(code)s"
		args = {
			'item': self._payload[self._idx['pk_health_issue']],
			'code': pk_code
		}
		rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])
		return True

	#--------------------------------------------------------
	def format_as_journal(self, left_margin=0, date_format='%Y %b %d, %a'):
		rows = gmClinNarrative.get_as_journal (
			issues = (self.pk_obj,),
			order_by = 'pk_episode, pk_encounter, clin_when, scr, src_table'
		)

		if len(rows) == 0:
			return ''

		left_margin = ' ' * left_margin

		lines = []
		lines.append(_('Clinical data generated during encounters under this health issue:'))

		prev_epi = None
		for row in rows:
			if row['pk_episode'] != prev_epi:
				lines.append('')
				prev_epi = row['pk_episode']

			when = gmDateTime.pydt_strftime(row['clin_when'], date_format)
			top_row = '%s%s %s (%s) %s' % (
				gmTools.u_box_top_left_arc,
				gmTools.u_box_horiz_single,
				gmSoapDefs.soap_cat2l10n_str[row['real_soap_cat']],
				when,
				gmTools.u_box_horiz_single * 5
			)
			soap = gmTools.wrap (
				text = row['narrative'],
				width = 60,
				initial_indent = '  ',
				subsequent_indent = '  ' + left_margin
			)
			row_ver = ''
			if row['row_version'] > 0:
				row_ver = 'v%s: ' % row['row_version']
			bottom_row = '%s%s %s, %s%s %s' % (
				' ' * 40,
				gmTools.u_box_horiz_light_heavy,
				row['modified_by'],
				row_ver,
				gmDateTime.pydt_strftime(row['modified_when'], date_format),
				gmTools.u_box_horiz_heavy_light
			)

			lines.append(top_row)
			lines.append(soap)
			lines.append(bottom_row)

		eol_w_margin = '\n%s' % left_margin
		return left_margin + eol_w_margin.join(lines) + '\n'

	#--------------------------------------------------------
	def format (self, left_margin=0, patient=None,
		with_summary=True,
		with_codes=True,
		with_episodes=True,
		with_encounters=True,
		with_medications=True,
		with_hospital_stays=True,
		with_procedures=True,
		with_family_history=True,
		with_documents=True,
		with_tests=True,
		with_vaccinations=True,
		with_external_care=True
	):

		lines = []

		lines.append(_('Health Issue %s%s%s%s   [#%s]') % (
			'\u00BB',
			self._payload[self._idx['description']],
			'\u00AB',
			gmTools.coalesce (
				value2test = self.laterality_description,
				return_instead = '',
				template4value = ' (%s)',
				none_equivalents = [None, '', '?']
			),
			self._payload[self._idx['pk_health_issue']]
		))

		if self._payload[self._idx['is_confidential']]:
			lines.append('')
			lines.append(_(' ***** CONFIDENTIAL *****'))
			lines.append('')

		if self._payload[self._idx['is_cause_of_death']]:
			lines.append('')
			lines.append(_(' contributed to death of patient'))
			lines.append('')

		enc = cEncounter(aPK_obj = self._payload[self._idx['pk_encounter']])
		lines.append (_(' Created during encounter: %s (%s - %s)   [#%s]') % (
			enc['l10n_type'],
			enc['started_original_tz'].strftime('%Y-%m-%d %H:%M'),
			enc['last_affirmed_original_tz'].strftime('%H:%M'),
			self._payload[self._idx['pk_encounter']]
		))

		if self._payload[self._idx['age_noted']] is not None:
			lines.append(_(' Noted at age: %s') % self.age_noted_human_readable())

		lines.append(' ' + _('Status') + ': %s, %s%s' % (
			gmTools.bool2subst(self._payload[self._idx['is_active']], _('active'), _('inactive')),
			gmTools.bool2subst(self._payload[self._idx['clinically_relevant']], _('clinically relevant'), _('not clinically relevant')),
			gmTools.coalesce (
				value2test = diagnostic_certainty_classification2str(self._payload[self._idx['diagnostic_certainty_classification']]),
				return_instead = '',
				template4value = ', %s',
				none_equivalents = [None, '']
			)
		))

		if with_summary:
			if self._payload[self._idx['summary']] is not None:
				lines.append(' %s:' % _('Synopsis'))
				lines.append(gmTools.wrap (
					text = self._payload[self._idx['summary']],
					width = 60,
					initial_indent = '  ',
					subsequent_indent = '  '
				))

		# codes ?
		if with_codes:
			codes = self.generic_codes
			if len(codes) > 0:
				lines.append('')
			for c in codes:
				lines.append(' %s: %s (%s - %s)' % (
					c['code'],
					c['term'],
					c['name_short'],
					c['version']
				))
			del codes

		lines.append('')

		# patient/emr dependant
		if patient is not None:
			if patient.ID != self._payload[self._idx['pk_patient']]:
				msg = '<patient>.ID = %s but health issue %s belongs to patient %s' % (
					patient.ID,
					self._payload[self._idx['pk_health_issue']],
					self._payload[self._idx['pk_patient']]
				)
				raise ValueError(msg)
			emr = patient.emr

			# episodes
			if with_episodes:
				epis = self.get_episodes()
				if epis is None:
					lines.append(_('Error retrieving episodes for this health issue.'))
				elif len(epis) == 0:
					lines.append(_('There are no episodes for this health issue.'))
				else:
					lines.append (
						_('Episodes: %s (most recent: %s%s%s)') % (
							len(epis),
							gmTools.u_left_double_angle_quote,
							emr.get_most_recent_episode(issue = self._payload[self._idx['pk_health_issue']])['description'],
							gmTools.u_right_double_angle_quote
						)
					)
					for epi in epis:
						lines.append(' \u00BB%s\u00AB (%s)' % (
							epi['description'],
							gmTools.bool2subst(epi['episode_open'], _('ongoing'), _('closed'))
						))
				lines.append('')

			# encounters
			if with_encounters:
				first_encounter = emr.get_first_encounter(issue_id = self._payload[self._idx['pk_health_issue']])
				last_encounter = emr.get_last_encounter(issue_id = self._payload[self._idx['pk_health_issue']])

				if first_encounter is None or last_encounter is None:
					lines.append(_('No encounters found for this health issue.'))
				else:
					encs = emr.get_encounters(issues = [self._payload[self._idx['pk_health_issue']]])
					lines.append(_('Encounters: %s (%s - %s):') % (
						len(encs),
						first_encounter['started_original_tz'].strftime('%m/%Y'),
						last_encounter['last_affirmed_original_tz'].strftime('%m/%Y')
					))
					lines.append(_(' Most recent: %s - %s') % (
						last_encounter['started_original_tz'].strftime('%Y-%m-%d %H:%M'),
						last_encounter['last_affirmed_original_tz'].strftime('%H:%M')
					))

			# medications
			if with_medications:
				meds = emr.get_current_medications (
					issues = [ self._payload[self._idx['pk_health_issue']] ],
					order_by = 'is_currently_active DESC, started, substance'
				)
				if len(meds) > 0:
					lines.append('')
					lines.append(_('Medications and Substances'))
				for m in meds:
					lines.append(m.format(left_margin = (left_margin + 1)))
				del meds

			# hospitalizations
			if with_hospital_stays:
				stays = emr.get_hospital_stays (
					issues = [ self._payload[self._idx['pk_health_issue']] ]
				)
				if len(stays) > 0:
					lines.append('')
					lines.append(_('Hospitalizations: %s') % len(stays))
				for s in stays:
					lines.append(s.format(left_margin = (left_margin + 1)))
				del stays

			# procedures
			if with_procedures:
				procs = emr.get_performed_procedures (
					issues = [ self._payload[self._idx['pk_health_issue']] ]
				)
				if len(procs) > 0:
					lines.append('')
					lines.append(_('Procedures performed: %s') % len(procs))
				for p in procs:
					lines.append(p.format(left_margin = (left_margin + 1)))
				del procs

			# family history
			if with_family_history:
				fhx = emr.get_family_history(issues = [ self._payload[self._idx['pk_health_issue']] ])
				if len(fhx) > 0:
					lines.append('')
					lines.append(_('Family History: %s') % len(fhx))
				for f in fhx:
					lines.append(f.format (
						left_margin = (left_margin + 1),
						include_episode = True,
						include_comment = True,
						include_codes = False
					))
				del fhx

			epis = self.get_episodes()
			if len(epis) > 0:
				epi_pks = [ e['pk_episode'] for e in epis ]

				# documents
				if with_documents:
					doc_folder = patient.get_document_folder()
					docs = doc_folder.get_documents(pk_episodes = epi_pks)
					if len(docs) > 0:
						lines.append('')
						lines.append(_('Documents: %s') % len(docs))
					del docs

				# test results
				if with_tests:
					tests = emr.get_test_results_by_date(episodes = epi_pks)
					if len(tests) > 0:
						lines.append('')
						lines.append(_('Measurements and Results: %s') % len(tests))
					del tests

				# vaccinations
				if with_vaccinations:
					vaccs = emr.get_vaccinations(episodes = epi_pks, order_by = 'date_given, vaccine')
					if len(vaccs) > 0:
						lines.append('')
						lines.append(_('Vaccinations:'))
					for vacc in vaccs:
						lines.extend(vacc.format(with_reaction = True))
					del vaccs

			del epis

		if with_external_care:
			care = self._get_external_care(order_by = 'organization, unit, provider')
			if len(care) > 0:
				lines.append('')
				lines.append(_('External care:'))
			for item in care:
				lines.append(' %s%s@%s%s' % (
					gmTools.coalesce(item['provider'], '', '%s: '),
					item['unit'],
					item['organization'],
					gmTools.coalesce(item['comment'], '', ' (%s)')
				))

		left_margin = ' ' * left_margin
		eol_w_margin = '\n%s' % left_margin
		lines = gmTools.strip_trailing_empty_lines(lines = lines, eol = '\n')
		return left_margin + eol_w_margin.join(lines) + '\n'
	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def _get_external_care(self, order_by=None):
		return gmExternalCare.get_external_care_items(pk_health_issue = self.pk_obj, order_by = order_by)

	external_care = property(_get_external_care)

	#--------------------------------------------------------
	open_episode = property(get_open_episode)

	#--------------------------------------------------------
	def _get_first_episode(self):

		args = {'pk_issue': self.pk_obj}

		cmd = """SELECT
			earliest, pk_episode
		FROM (
				-- .modified_when of all episodes of this issue,
				-- earliest-possible thereof = when created,
				-- should actually go all the way back into audit.log_episode
				(SELECT
					c_epi.modified_when AS earliest,
					c_epi.pk AS pk_episode
				 FROM clin.episode c_epi
				 WHERE c_epi.fk_health_issue = %(pk_issue)s
				)
			UNION ALL

				-- last modification of encounter in which episodes of this issue were created,
				-- earliest-possible thereof = initial creation of that encounter
				(SELECT
					c_enc.modified_when AS earliest,
					c_epi.pk AS pk_episode
				 FROM
					clin.episode c_epi
						INNER JOIN clin.encounter c_enc ON (c_enc.pk = c_epi.fk_encounter)
						INNER JOIN clin.health_issue c_hi ON (c_hi.pk = c_epi.fk_health_issue)
				 WHERE c_hi.pk = %(pk_issue)s
				)
			UNION ALL

				-- start of encounter in which episodes of this issue were created,
				-- earliest-possible thereof = set by user
				(SELECT
					c_enc.started AS earliest,
					c_epi.pk AS pk_episode
				 FROM
					clin.episode c_epi
						INNER JOIN clin.encounter c_enc ON (c_enc.pk = c_epi.fk_encounter)
						INNER JOIN clin.health_issue c_hi ON (c_hi.pk = c_epi.fk_health_issue)
				 WHERE c_hi.pk = %(pk_issue)s
				)
			UNION ALL

				-- start of encounters of clinical items linked to episodes of this issue,
				-- earliest-possible thereof = explicitly set by user
				(SELECT
					c_enc.started AS earliest,
					c_epi.pk AS pk_episode
				 FROM
					clin.clin_root_item c_cri
						INNER JOIN clin.encounter c_enc ON (c_cri.fk_encounter = c_enc.pk)
						INNER JOIN clin.episode c_epi ON (c_cri.fk_episode = c_epi.pk)
							INNER JOIN clin.health_issue c_hi ON (c_epi.fk_health_issue = c_hi.pk)
				 WHERE c_hi.pk = %(pk_issue)s
				)
			UNION ALL

				-- .clin_when of clinical items linked to episodes of this issue,
				-- earliest-possible thereof = explicitly set by user
				(SELECT
					c_cri.clin_when AS earliest,
					c_epi.pk AS pk_episode
				 FROM
					clin.clin_root_item c_cri
						INNER JOIN clin.episode c_epi ON (c_cri.fk_episode = c_epi.pk)
							INNER JOIN clin.health_issue c_hi ON (c_epi.fk_health_issue = c_hi.pk)
				 WHERE c_hi.pk = %(pk_issue)s
				)
			UNION ALL

				-- earliest modification time of clinical items linked to episodes of this issue
				-- this CAN be used since if an item is linked to an episode it can be
				-- assumed the episode (should have) existed at the time of creation
				(SELECT
					c_cri.modified_when AS earliest,
					c_epi.pk AS pk_episode
				 FROM
					clin.clin_root_item c_cri
						INNER JOIN clin.episode c_epi ON (c_cri.fk_episode = c_epi.pk)
							INNER JOIN clin.health_issue c_hi ON (c_epi.fk_health_issue = c_hi.pk)
				 WHERE c_hi.pk = %(pk_issue)s
				)
			UNION ALL

				-- there may not be items, but there may still be documents ...
				(SELECT
					b_dm.clin_when AS earliest,
					c_epi.pk AS pk_episode
				 FROM
					blobs.doc_med b_dm
						INNER JOIN clin.episode c_epi ON (b_dm.fk_episode = c_epi.pk)
							INNER JOIN clin.health_issue c_hi ON (c_epi.fk_health_issue = c_hi.pk)
				  WHERE c_hi.pk = %(pk_issue)s
				)
		) AS candidates
		ORDER BY earliest NULLS LAST
		LIMIT 1"""
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)
		if len(rows) == 0:
			return None
		return cEpisode(aPK_obj = rows[0]['pk_episode'])

	first_episode = property(_get_first_episode)

	#--------------------------------------------------------
	def _get_latest_episode(self):

		# explicit always wins:
		if self._payload[self._idx['has_open_episode']]:
			return self.open_episode

		args = {'pk_issue': self.pk_obj}

		# cheap query first: any episodes at all ?
		cmd = "SELECT 1 FROM clin.episode WHERE fk_health_issue = %(pk_issue)s"
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = False)
		if len(rows) == 0:
			return None

		cmd = """SELECT
			latest, pk_episode
		FROM (
				-- .clin_when of clinical items linked to episodes of this issue,
				-- latest-possible thereof = explicitly set by user
				(SELECT
					c_cri.clin_when AS latest,
					c_epi.pk AS pk_episode,
					1 AS rank
				 FROM
					clin.clin_root_item c_cri
						INNER JOIN clin.episode c_epi ON (c_cri.fk_episode = c_epi.pk)
							INNER JOIN clin.health_issue c_hi ON (c_epi.fk_health_issue = c_hi.pk)
				 WHERE c_hi.pk = %(pk_issue)s
				)
			UNION ALL

				-- .clin_when of documents linked to episodes of this issue
				(SELECT
					b_dm.clin_when AS latest,
					c_epi.pk AS pk_episode,
					1 AS rank
				 FROM
					blobs.doc_med b_dm
						INNER JOIN clin.episode c_epi ON (b_dm.fk_episode = c_epi.pk)
							INNER JOIN clin.health_issue c_hi ON (c_epi.fk_health_issue = c_hi.pk)
				 WHERE c_hi.pk = %(pk_issue)s
				)
			UNION ALL

				-- last_affirmed of encounter in which episodes of this issue were created,
				-- earliest-possible thereof = set by user
				(SELECT
					c_enc.last_affirmed AS latest,
					c_epi.pk AS pk_episode,
					2 AS rank
				 FROM
					clin.episode c_epi
						INNER JOIN clin.encounter c_enc ON (c_enc.pk = c_epi.fk_encounter)
						INNER JOIN clin.health_issue c_hi ON (c_hi.pk = c_epi.fk_health_issue)
				 WHERE c_hi.pk = %(pk_issue)s
				)

		) AS candidates
		WHERE
			-- weed out NULL rows due to episodes w/o clinical items and w/o documents
			latest IS NOT NULL
		ORDER BY
			rank,
			latest DESC
		LIMIT 1
		"""
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)
		if len(rows) == 0:
			# there were no episodes for this issue
			return None
		return cEpisode(aPK_obj = rows[0]['pk_episode'])

	latest_episode = property(_get_latest_episode)

	#--------------------------------------------------------
	# Steffi suggested we divide into safe and assumed (= possible) start dates
	def _get_safe_start_date(self):
		"""This returns the date when we can assume to safely KNOW
		   the health issue existed (because the provider said so)."""

		args = {
			'enc': self._payload[self._idx['pk_encounter']],
			'pk': self._payload[self._idx['pk_health_issue']]
		}
		cmd = """SELECT COALESCE (
			-- this one must override all:
			-- .age_noted if not null and DOB is known
			(CASE
				WHEN c_hi.age_noted IS NULL
				THEN NULL::timestamp with time zone
				WHEN
					(SELECT d_i.dob FROM dem.identity d_i WHERE d_i.pk = (
						SELECT c_enc.fk_patient FROM clin.encounter c_enc WHERE c_enc.pk = %(enc)s
					)) IS NULL
				THEN NULL::timestamp with time zone
				ELSE
					c_hi.age_noted + (
						SELECT d_i.dob FROM dem.identity d_i WHERE d_i.pk = (
							SELECT c_enc.fk_patient FROM clin.encounter c_enc WHERE c_enc.pk = %(enc)s
						)
					)
			END),

			-- look at best_guess_clinical_start_date of all linked episodes

			-- start of encounter in which created, earliest = explicitly set
			(SELECT c_enc.started AS earliest FROM clin.encounter c_enc WHERE c_enc.pk = c_hi.fk_encounter)
		)
		FROM clin.health_issue c_hi
		WHERE c_hi.pk = %(pk)s"""
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}])
		start = rows[0][0]
		# leads to a loop:
		#end = self.clinical_end_date
		#if start > end:
		#	return end
		return start

	safe_start_date = property(_get_safe_start_date)

	#--------------------------------------------------------
	def _get_possible_start_date(self):
		args = {'pk': self._payload[self._idx['pk_health_issue']]}
		cmd = """
SELECT MIN(earliest) FROM (
	-- last modification, earliest = when created in/changed to the current state
	(SELECT modified_when AS earliest FROM clin.health_issue WHERE pk = %(pk)s)

UNION ALL
	-- last modification of encounter in which created, earliest = initial creation of that encounter
	(SELECT c_enc.modified_when AS earliest FROM clin.encounter c_enc WHERE c_enc.pk = (
	 	SELECT c_hi.fk_encounter FROM clin.health_issue c_hi WHERE c_hi.pk = %(pk)s
	))

UNION ALL
	-- earliest explicit .clin_when of clinical items linked to this health_issue
	(SELECT MIN(c_vpi.clin_when) AS earliest FROM clin.v_pat_items c_vpi WHERE c_vpi.pk_health_issue = %(pk)s)

UNION ALL
	-- earliest modification time of clinical items linked to this health issue
	-- this CAN be used since if an item is linked to a health issue it can be
	-- assumed the health issue (should have) existed at the time of creation
	(SELECT MIN(c_vpi.modified_when) AS earliest FROM clin.v_pat_items c_vpi WHERE c_vpi.pk_health_issue = %(pk)s)

UNION ALL
	-- earliest start of encounters of clinical items linked to this episode
	(SELECT MIN(c_enc.started) AS earliest FROM clin.encounter c_enc WHERE c_enc.pk IN (
		SELECT c_vpi.pk_encounter FROM clin.v_pat_items c_vpi WHERE c_vpi.pk_health_issue = %(pk)s
	))

-- here we should be looking at
-- .best_guess_clinical_start_date of all episodes linked to this encounter

) AS candidates"""

		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}])
		return rows[0][0]

	possible_start_date = property(_get_possible_start_date)

	#--------------------------------------------------------
	def _get_clinical_end_date(self):
		if self._payload[self._idx['is_active']]:
			return None
		if self._payload[self._idx['has_open_episode']]:
			return None
		latest_episode = self.latest_episode
		if latest_episode is not None:
			return latest_episode.best_guess_clinical_end_date
		# apparently, there are no episodes for this issue
		# and the issue is not active either
		# so, we simply do not know, the safest assumption is:
		return self.safe_start_date

	clinical_end_date = property(_get_clinical_end_date)

	#--------------------------------------------------------
	def _get_latest_access_date(self):
		cmd = """
SELECT
	MAX(latest)
FROM (
	-- last modification, latest = when last changed to the current state
	-- DO NOT USE: database upgrades may change this field
	(SELECT modified_when AS latest FROM clin.health_issue WHERE pk = %(pk)s)

	--UNION ALL
	-- last modification of encounter in which created, latest = initial creation of that encounter
	-- DO NOT USE: just because one corrects a typo does not mean the issue took any longer
	--(SELECT c_enc.modified_when AS latest FROM clin.encounter c_enc WHERE c_enc.pk = (
	-- 	SELECT fk_encounter FROM clin.episode WHERE pk = %(pk)s
	-- )
	--)

	--UNION ALL
	-- end of encounter in which created, latest = explicitly set
	-- DO NOT USE: we can retrospectively create issues which
	-- DO NOT USE: are long since finished
	--(SELECT c_enc.last_affirmed AS latest FROM clin.encounter c_enc WHERE c_enc.pk = (
	-- 	SELECT fk_encounter FROM clin.episode WHERE pk = %(pk)s
	-- )
	--)

	UNION ALL
	-- latest end of encounters of clinical items linked to this issue
	(SELECT
		MAX(last_affirmed) AS latest
	 FROM clin.encounter
	 WHERE pk IN (
		SELECT pk_encounter FROM clin.v_pat_items WHERE pk_health_issue = %(pk)s
	 )
	)

	UNION ALL
	-- latest explicit .clin_when of clinical items linked to this issue
	(SELECT
		MAX(clin_when) AS latest
	 FROM clin.v_pat_items
	 WHERE pk_health_issue = %(pk)s
	)

	-- latest modification time of clinical items linked to this issue
	-- this CAN be used since if an item is linked to an issue it can be
	-- assumed the issue (should have) existed at the time of modification
	-- DO NOT USE, because typo fixes should not extend the issue
	--(SELECT MIN(modified_when) AS latest FROM clin.clin_root_item WHERE fk_episode = %(pk)s)

) AS candidates"""
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': {'pk': self.pk_obj}}])
		return rows[0][0]

	latest_access_date = property(_get_latest_access_date)

	#--------------------------------------------------------
	def _get_laterality_description(self):
		try:
			return laterality2str[self._payload[self._idx['laterality']]]
		except KeyError:
			return '<?>'

	laterality_description = property(_get_laterality_description)

	#--------------------------------------------------------
	def _get_diagnostic_certainty_description(self):
		return diagnostic_certainty_classification2str(self._payload[self._idx['diagnostic_certainty_classification']])

	diagnostic_certainty_description = property(_get_diagnostic_certainty_description)

	#--------------------------------------------------------
	def _get_formatted_revision_history(self):
		cmd = """SELECT
				'<N/A>'::TEXT as audit__action_applied,
				NULL AS audit__action_when,
				'<N/A>'::TEXT AS audit__action_by,
				pk_audit,
				row_version,
				modified_when,
				modified_by,
				pk,
				description,
				laterality,
				age_noted,
				is_active,
				clinically_relevant,
				is_confidential,
				is_cause_of_death,
				fk_encounter,
				grouping,
				diagnostic_certainty_classification,
				summary
			FROM clin.health_issue
			WHERE pk = %(pk_health_issue)s
		UNION ALL (
			SELECT
				audit_action as audit__action_applied,
				audit_when as audit__action_when,
				audit_by as audit__action_by,
				pk_audit,
				orig_version as row_version,
				orig_when as modified_when,
				orig_by as modified_by,
				pk,
				description,
				laterality,
				age_noted,
				is_active,
				clinically_relevant,
				is_confidential,
				is_cause_of_death,
				fk_encounter,
				grouping,
				diagnostic_certainty_classification,
				summary
			FROM audit.log_health_issue
			WHERE pk = %(pk_health_issue)s
		)
		ORDER BY row_version DESC
		"""
		args = {'pk_health_issue': self.pk_obj}
		title = _('Health issue: %s%s%s') % (
			gmTools.u_left_double_angle_quote,
			self._payload[self._idx['description']],
			gmTools.u_right_double_angle_quote
		)
		return '\n'.join(self._get_revision_history(cmd, args, title))

	formatted_revision_history = property(_get_formatted_revision_history)
	#--------------------------------------------------------
	def _get_generic_codes(self):
		if len(self._payload[self._idx['pk_generic_codes']]) == 0:
			return []

		cmd = gmCoding._SQL_get_generic_linked_codes % 'pk_generic_code = ANY(%(pks)s)'
		args = {'pks': self._payload[self._idx['pk_generic_codes']]}
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)
		return [ gmCoding.cGenericLinkedCode(row = {'data': r, 'idx': idx, 'pk_field': 'pk_lnk_code2item'}) for r in rows ]

	def _set_generic_codes(self, pk_codes):
		queries = []
		# remove all codes
		if len(self._payload[self._idx['pk_generic_codes']]) > 0:
			queries.append ({
				'cmd': 'DELETE FROM clin.lnk_code2h_issue WHERE fk_item = %(issue)s AND fk_generic_code = ANY(%(codes)s)',
				'args': {
					'issue': self._payload[self._idx['pk_health_issue']],
					'codes': self._payload[self._idx['pk_generic_codes']]
				}
			})
		# add new codes
		for pk_code in pk_codes:
			queries.append ({
				'cmd': 'INSERT INTO clin.lnk_code2h_issue (fk_item, fk_generic_code) VALUES (%(issue)s, %(pk_code)s)',
				'args': {
					'issue': self._payload[self._idx['pk_health_issue']],
					'pk_code': pk_code
				}
			})
		if len(queries) == 0:
			return
		# run it all in one transaction
		rows, idx = gmPG2.run_rw_queries(queries = queries)
		return

	generic_codes = property(_get_generic_codes, _set_generic_codes)

#============================================================
def create_health_issue(description=None, encounter=None, patient=None):
	"""Creates a new health issue for a given patient.

	description - health issue name
	"""
	try:
		h_issue = cHealthIssue(name = description, encounter = encounter, patient = patient)
		return h_issue
	except gmExceptions.NoSuchBusinessObjectError:
		pass

	queries = []
	cmd = "insert into clin.health_issue (description, fk_encounter) values (%(desc)s, %(enc)s)"
	queries.append({'cmd': cmd, 'args': {'desc': description, 'enc': encounter}})

	cmd = "select currval('clin.health_issue_pk_seq')"
	queries.append({'cmd': cmd})

	rows, idx = gmPG2.run_rw_queries(queries = queries, return_data = True)
	h_issue = cHealthIssue(aPK_obj = rows[0][0])

	return h_issue

#-----------------------------------------------------------
def delete_health_issue(health_issue=None):
	if isinstance(health_issue, cHealthIssue):
		args = {'pk': health_issue['pk_health_issue']}
	else:
		args = {'pk': int(health_issue)}
	try:
		gmPG2.run_rw_queries(queries = [{'cmd': 'DELETE FROM clin.health_issue WHERE pk = %(pk)s', 'args': args}])
	except gmPG2.dbapi.IntegrityError:
		# should be parsing pgcode/and or error message
		_log.exception('cannot delete health issue')
		return False

	return True

#------------------------------------------------------------
# use as dummy for unassociated episodes
def get_dummy_health_issue():
	issue = {
		'pk_health_issue': None,
		'description': _('Unattributed episodes'),
		'age_noted': None,
		'laterality': 'na',
		'is_active': True,
		'clinically_relevant': True,
		'is_confidential': None,
		'is_cause_of_death': False,
		'is_dummy': True,
		'grouping': None
	}
	return issue

#-----------------------------------------------------------
def health_issue2problem(health_issue=None, allow_irrelevant=False):
	return cProblem (
		aPK_obj = {
			'pk_patient': health_issue['pk_patient'],
			'pk_health_issue': health_issue['pk_health_issue'],
			'pk_episode': None
		},
		try_potential_problems = allow_irrelevant
	)

#============================================================
# episodes API
#============================================================
class cEpisode(gmBusinessDBObject.cBusinessDBObject):
	"""Represents one clinical episode.
	"""
	_cmd_fetch_payload = "select * from clin.v_pat_episodes where pk_episode=%s"
	_cmds_store_payload = [
		"""update clin.episode set
				fk_health_issue = %(pk_health_issue)s,
				is_open = %(episode_open)s::boolean,
				description = %(description)s,
				summary = gm.nullify_empty_string(%(summary)s),
				diagnostic_certainty_classification = gm.nullify_empty_string(%(diagnostic_certainty_classification)s)
			where
				pk = %(pk_episode)s and
				xmin = %(xmin_episode)s""",
		"""select xmin_episode from clin.v_pat_episodes where pk_episode = %(pk_episode)s"""
	]
	_updatable_fields = [
		'pk_health_issue',
		'episode_open',
		'description',
		'summary',
		'diagnostic_certainty_classification'
	]
	#--------------------------------------------------------
	def __init__(self, aPK_obj=None, id_patient=None, name='xxxDEFAULTxxx', health_issue=None, row=None, encounter=None, link_obj=None):
		pk = aPK_obj
		if pk is None and row is None:

			where_parts = ['description = %(desc)s']

			if id_patient is not None:
				where_parts.append('pk_patient = %(pat)s')

			if health_issue is not None:
				where_parts.append('pk_health_issue = %(issue)s')

			if encounter is not None:
				where_parts.append('pk_patient = (SELECT fk_patient FROM clin.encounter WHERE pk = %(enc)s)')

			args = {
				'pat': id_patient,
				'issue': health_issue,
				'enc': encounter,
				'desc': name
			}

			cmd = 'SELECT * FROM clin.v_pat_episodes WHERE %s' % ' AND '.join(where_parts)

			rows, idx = gmPG2.run_ro_queries (
				link_obj = link_obj,
				queries = [{'cmd': cmd, 'args': args}],
				get_col_idx=True
			)

			if len(rows) == 0:
				raise gmExceptions.NoSuchBusinessObjectError('no episode for [%s:%s:%s:%s]' % (id_patient, name, health_issue, encounter))

			r = {'idx': idx, 'data': rows[0], 'pk_field': 'pk_episode'}
			gmBusinessDBObject.cBusinessDBObject.__init__(self, row=r)

		else:
			gmBusinessDBObject.cBusinessDBObject.__init__(self, aPK_obj=pk, row=row, link_obj = link_obj)

	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	@classmethod
	def from_problem(cls, problem:'cProblem') -> 'cEpisode':
		"""Initialize episode from episody-type problem."""
		if isinstance(problem, cEpisode):
			return problem

		assert isinstance(problem, cProblem), 'cannot convert [%s] to episode' % problem
		assert problem['type'] == 'episode', 'cannot convert [%s] to episode' % problem
		return cls(aPK_obj = problem['pk_episode'])

	#--------------------------------------------------------
	def get_patient(self):
		return self._payload[self._idx['pk_patient']]

	#--------------------------------------------------------
	def get_narrative(self, soap_cats=None, encounters=None, order_by = None):
		return gmClinNarrative.get_narrative (
			soap_cats = soap_cats,
			encounters = encounters,
			episodes = [self.pk_obj],
			order_by = order_by
		)

	#--------------------------------------------------------
	def rename(self, description=None):
		"""Method for episode editing, that is, episode renaming.

		@param description
			- the new descriptive name for the encounter
		@type description
			- a string instance
		"""
		# sanity check
		if description.strip() == '':
			_log.error('<description> must be a non-empty string instance')
			return False
		# update the episode description
		old_description = self._payload[self._idx['description']]
		self._payload[self._idx['description']] = description.strip()
		self._is_modified = True
		successful, data = self.save_payload()
		if not successful:
			_log.error('cannot rename episode [%s] to [%s]' % (self, description))
			self._payload[self._idx['description']] = old_description
			return False
		return True

	#--------------------------------------------------------
	def add_code(self, pk_code=None):
		"""<pk_code> must be a value from ref.coding_system_root.pk_coding_system (clin.lnk_code2item_root.fk_generic_code)"""

		if pk_code in self._payload[self._idx['pk_generic_codes']]:
			return

		cmd = """
			INSERT INTO clin.lnk_code2episode
				(fk_item, fk_generic_code)
			SELECT
				%(item)s,
				%(code)s
			WHERE NOT EXISTS (
				SELECT 1 FROM clin.lnk_code2episode
				WHERE
					fk_item = %(item)s
						AND
					fk_generic_code = %(code)s
			)"""
		args = {
			'item': self._payload[self._idx['pk_episode']],
			'code': pk_code
		}
		rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])
		return

	#--------------------------------------------------------
	def remove_code(self, pk_code=None):
		"""<pk_code> must be a value from ref.coding_system_root.pk_coding_system (clin.lnk_code2item_root.fk_generic_code)"""
		cmd = "DELETE FROM clin.lnk_code2episode WHERE fk_item = %(item)s AND fk_generic_code = %(code)s"
		args = {
			'item': self._payload[self._idx['pk_episode']],
			'code': pk_code
		}
		rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])
		return True

	#--------------------------------------------------------
	def format_as_journal(self, left_margin=0, date_format='%Y %b %d, %a'):
		rows = gmClinNarrative.get_as_journal (
			episodes = (self.pk_obj,),
			order_by = 'pk_encounter, clin_when, scr, src_table'
			#order_by = u'pk_encounter, scr, clin_when, src_table'
		)

		if len(rows) == 0:
			return ''

		lines = []

		lines.append(_('Clinical data generated during encounters within this episode:'))

		left_margin = ' ' * left_margin

		prev_enc = None
		for row in rows:
			if row['pk_encounter'] != prev_enc:
				lines.append('')
				prev_enc = row['pk_encounter']

			when = row['clin_when'].strftime(date_format)
			top_row = '%s%s %s (%s) %s' % (
				gmTools.u_box_top_left_arc,
				gmTools.u_box_horiz_single,
				gmSoapDefs.soap_cat2l10n_str[row['real_soap_cat']],
				when,
				gmTools.u_box_horiz_single * 5
			)
			soap = gmTools.wrap (
				text = row['narrative'],
				width = 60,
				initial_indent = '  ',
				subsequent_indent = '  ' + left_margin
			)
			row_ver = ''
			if row['row_version'] > 0:
				row_ver = 'v%s: ' % row['row_version']
			bottom_row = '%s%s %s, %s%s %s' % (
				' ' * 40,
				gmTools.u_box_horiz_light_heavy,
				row['modified_by'],
				row_ver,
				gmDateTime.pydt_strftime(row['modified_when'], date_format),
				gmTools.u_box_horiz_heavy_light
			)

			lines.append(top_row)
			lines.append(soap)
			lines.append(bottom_row)

		eol_w_margin = '\n%s' % left_margin
		return left_margin + eol_w_margin.join(lines) + '\n'

	#--------------------------------------------------------
	def format_maximum_information(self, patient=None):
		if patient is None:
			from Gnumed.business.gmPerson import gmCurrentPatient, cPerson
			if self._payload[self._idx['pk_patient']] == gmCurrentPatient().ID:
				patient = gmCurrentPatient()
			else:
				patient = cPerson(self._payload[self._idx['pk_patient']])

		return self.format (
			patient = patient,
			with_summary = True,
			with_codes = True,
			with_encounters = True,
			with_documents = True,
			with_hospital_stays = True,
			with_procedures = True,
			with_family_history = True,
			with_tests = False,		# does not inform on the episode itself
			with_vaccinations = True,
			with_health_issue = True,
			return_list = True
		)

	#--------------------------------------------------------
	def format(self, left_margin=0, patient=None,
		with_summary=True,
		with_codes=True,
		with_encounters=True,
		with_documents=True,
		with_hospital_stays=True,
		with_procedures=True,
		with_family_history=True,
		with_tests=True,
		with_vaccinations=True,
		with_health_issue=False,
		return_list=False
	):

		if patient is not None:
			if patient.ID != self._payload[self._idx['pk_patient']]:
				msg = '<patient>.ID = %s but episode %s belongs to patient %s' % (
					patient.ID,
					self._payload[self._idx['pk_episode']],
					self._payload[self._idx['pk_patient']]
				)
				raise ValueError(msg)
			emr = patient.emr
		else:
			with_encounters = False
			with_documents = False
			with_hospital_stays = False
			with_procedures = False
			with_family_history = False
			with_tests = False
			with_vaccinations = False

		lines = []

		# episode details
		lines.append (_('Episode %s%s%s   [#%s]') % (
			gmTools.u_left_double_angle_quote,
			self._payload[self._idx['description']],
			gmTools.u_right_double_angle_quote,
			self._payload[self._idx['pk_episode']]
		))

		enc = cEncounter(aPK_obj = self._payload[self._idx['pk_encounter']])
		lines.append (' ' + _('Created during encounter: %s (%s - %s)   [#%s]') % (
			enc['l10n_type'],
			enc['started_original_tz'].strftime('%Y-%m-%d %H:%M'),
			enc['last_affirmed_original_tz'].strftime('%H:%M'),
			self._payload[self._idx['pk_encounter']]
		))

		if patient is not None:
			range_str, range_str_verb, duration_str = self.formatted_clinical_duration
			lines.append(_(' Duration: %s (%s)') % (duration_str, range_str_verb))

		lines.append(' ' + _('Status') + ': %s%s' % (
			gmTools.bool2subst(self._payload[self._idx['episode_open']], _('active'), _('finished')),
			gmTools.coalesce (
				value2test = diagnostic_certainty_classification2str(self._payload[self._idx['diagnostic_certainty_classification']]),
				return_instead = '',
				template4value = ', %s',
				none_equivalents = [None, '']
			)
		))

		if with_health_issue:
			lines.append(' ' + _('Health issue') + ': %s' % gmTools.coalesce (
				self._payload[self._idx['health_issue']],
				_('none associated')
			))

		if with_summary:
			if self._payload[self._idx['summary']] is not None:
				lines.append(' %s:' % _('Synopsis'))
				lines.append(gmTools.wrap (
						text = self._payload[self._idx['summary']],
						width = 60,
						initial_indent = '  ',
						subsequent_indent = '  '
					)
				)

		# codes
		if with_codes:
			codes = self.generic_codes
			if len(codes) > 0:
				lines.append('')
			for c in codes:
				lines.append(' %s: %s (%s - %s)' % (
					c['code'],
					c['term'],
					c['name_short'],
					c['version']
				))
			del codes

		lines.append('')

		# encounters
		if with_encounters:
			encs = emr.get_encounters(episodes = [self._payload[self._idx['pk_episode']]])
			if encs is None:
				lines.append(_('Error retrieving encounters for this episode.'))
			elif len(encs) == 0:
				#lines.append(_('There are no encounters for this issue.'))
				pass
			else:
				first_encounter = emr.get_first_encounter(episode_id = self._payload[self._idx['pk_episode']])
				last_encounter = emr.get_last_encounter(episode_id = self._payload[self._idx['pk_episode']])
				lines.append(_('Last worked on: %s\n') % last_encounter['last_affirmed_original_tz'].strftime('%Y-%m-%d %H:%M'))
				if len(encs) < 4:
					line = _('%s encounter(s) (%s - %s):')
				else:
					line = _('1st and (up to 3) most recent (of %s) encounters (%s - %s):')
				lines.append(line % (
					len(encs),
					first_encounter['started'].strftime('%m/%Y'),
					last_encounter['last_affirmed'].strftime('%m/%Y')
				))
				lines.append(' %s - %s (%s):%s' % (
					first_encounter['started_original_tz'].strftime('%Y-%m-%d %H:%M'),
					first_encounter['last_affirmed_original_tz'].strftime('%H:%M'),
					first_encounter['l10n_type'],
					gmTools.coalesce (
						first_encounter['assessment_of_encounter'],
						gmTools.coalesce (
							first_encounter['reason_for_encounter'],
							'',
							' \u00BB%s\u00AB' + (' (%s)' % _('RFE'))
						),
						' \u00BB%s\u00AB' + (' (%s)' % _('AOE'))
					)
				))
				if len(encs) > 4:
					lines.append(_(' %s %s skipped %s') % (
						gmTools.u_ellipsis,
						(len(encs) - 4),
						gmTools.u_ellipsis
					))
				for enc in encs[1:][-3:]:
					lines.append(' %s - %s (%s):%s' % (
						enc['started_original_tz'].strftime('%Y-%m-%d %H:%M'),
						enc['last_affirmed_original_tz'].strftime('%H:%M'),
						enc['l10n_type'],
						gmTools.coalesce (
							enc['assessment_of_encounter'],
							gmTools.coalesce (
								enc['reason_for_encounter'],
								'',
								' \u00BB%s\u00AB' + (' (%s)' % _('RFE'))
							),
							' \u00BB%s\u00AB' + (' (%s)' % _('AOE'))
						)
					))
				del encs
				# spell out last encounter
				if last_encounter is not None:
					lines.append('')
					lines.append(_('Progress notes in most recent encounter:'))
					lines.extend(last_encounter.format_soap (
						episodes = [ self._payload[self._idx['pk_episode']] ],
						left_margin = left_margin,
						soap_cats = 'soapu',
						emr = emr
					))

		# documents
		if with_documents:
			doc_folder = patient.get_document_folder()
			docs = doc_folder.get_documents (
				pk_episodes = [ self._payload[self._idx['pk_episode']] ]
			)
			if len(docs) > 0:
				lines.append('')
				lines.append(_('Documents: %s') % len(docs))
			for d in docs:
				lines.append(' ' + d.format(single_line = True))
			del docs

		# hospitalizations
		if with_hospital_stays:
			stays = emr.get_hospital_stays(episodes = [ self._payload[self._idx['pk_episode']] ])
			if len(stays) > 0:
				lines.append('')
				lines.append(_('Hospitalizations: %s') % len(stays))
			for s in stays:
				lines.append(s.format(left_margin = (left_margin + 1)))
			del stays

		# procedures
		if with_procedures:
			procs = emr.get_performed_procedures(episodes = [ self._payload[self._idx['pk_episode']] ])
			if len(procs) > 0:
				lines.append('')
				lines.append(_('Procedures performed: %s') % len(procs))
			for p in procs:
				lines.append(p.format (
					left_margin = (left_margin + 1),
					include_episode = False,
					include_codes = True
				))
			del procs

		# family history
		if with_family_history:
			fhx = emr.get_family_history(episodes = [ self._payload[self._idx['pk_episode']] ])
			if len(fhx) > 0:
				lines.append('')
				lines.append(_('Family History: %s') % len(fhx))
			for f in fhx:
				lines.append(f.format (
					left_margin = (left_margin + 1),
					include_episode = False,
					include_comment = True,
					include_codes = True
				))
			del fhx

		# test results
		if with_tests:
			tests = emr.get_test_results_by_date(episodes = [ self._payload[self._idx['pk_episode']] ])
			if len(tests) > 0:
				lines.append('')
				lines.append(_('Measurements and Results:'))
			for t in tests:
				lines.append(' ' + t.format_concisely(date_format = '%Y %b %d', with_notes = True))
			del tests

		# vaccinations
		if with_vaccinations:
			vaccs = emr.get_vaccinations (
				episodes = [ self._payload[self._idx['pk_episode']] ],
				order_by = 'date_given DESC, vaccine'
			)
			if len(vaccs) > 0:
				lines.append('')
				lines.append(_('Vaccinations:'))
			for vacc in vaccs:
				lines.extend(vacc.format (
					with_indications = True,
					with_comment = True,
					with_reaction = True,
					date_format = '%Y-%m-%d'
				))
			del vaccs

		lines = gmTools.strip_trailing_empty_lines(lines = lines, eol = '\n')
		if return_list:
			return lines

		left_margin = ' ' * left_margin
		eol_w_margin = '\n%s' % left_margin
		return left_margin + eol_w_margin.join(lines) + '\n'

	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def _get_best_guess_clinical_start_date(self):
		return get_best_guess_clinical_start_date_for_episode(pk_episode = self.pk_obj)

	best_guess_clinical_start_date = property(_get_best_guess_clinical_start_date)

	#--------------------------------------------------------
	def _get_best_guess_clinical_end_date(self):
		return get_best_guess_clinical_end_date_for_episode(self.pk_obj)

	best_guess_clinical_end_date = property(_get_best_guess_clinical_end_date)

	#--------------------------------------------------------
	def _get_formatted_clinical_duration(self):
		return format_clinical_duration_of_episode (
			start = get_best_guess_clinical_start_date_for_episode(self.pk_obj),
			end = get_best_guess_clinical_end_date_for_episode(self.pk_obj)
		)

	formatted_clinical_duration = property(_get_formatted_clinical_duration)

	#--------------------------------------------------------
	def _get_latest_access_date(self):
		cmd = """SELECT MAX(latest) FROM (
			-- last modification, latest = when last changed to the current state
			(SELECT c_epi.modified_when AS latest, 'clin.episode.modified_when'::text AS candidate FROM clin.episode c_epi WHERE c_epi.pk = %(pk)s)

				UNION ALL

			-- last modification of encounter in which created, latest = initial creation of that encounter
			-- DO NOT USE: just because one corrects a typo does not mean the episode took longer
			--(SELECT c_enc.modified_when AS latest FROM clin.encounter c_enc WHERE c_enc.pk = (
			-- 	SELECT fk_encounter FROM clin.episode WHERE pk = %(pk)s
			--))

			-- end of encounter in which created, latest = explicitly set
			-- DO NOT USE: we can retrospectively create episodes which
			-- DO NOT USE: are long since finished
			--(SELECT c_enc.last_affirmed AS latest FROM clin.encounter c_enc WHERE c_enc.pk = (
			-- 	SELECT fk_encounter FROM clin.episode WHERE pk = %(pk)s
			--))

			-- latest end of encounters of clinical items linked to this episode
			(SELECT
				MAX(last_affirmed) AS latest,
				'clin.episode.pk = clin.clin_root_item,fk_episode -> .fk_encounter.last_affirmed'::text AS candidate
			 FROM clin.encounter
			 WHERE pk IN (
				SELECT fk_encounter FROM clin.clin_root_item WHERE fk_episode = %(pk)s
			))
				UNION ALL

			-- latest explicit .clin_when of clinical items linked to this episode
			(SELECT
				MAX(clin_when) AS latest,
				'clin.episode.pk = clin.clin_root_item,fk_episode -> .clin_when'::text AS candidate
			 FROM clin.clin_root_item
			 WHERE fk_episode = %(pk)s
			)

			-- latest modification time of clinical items linked to this episode
			-- this CAN be used since if an item is linked to an episode it can be
			-- assumed the episode (should have) existed at the time of creation
			-- DO NOT USE, because typo fixes should not extend the episode
			--(SELECT MIN(modified_when) AS latest FROM clin.clin_root_item WHERE fk_episode = %(pk)s)

			-- not sure about this one:
			-- .pk -> clin.clin_root_item.fk_encounter.modified_when

		) AS candidates"""
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': {'pk': self.pk_obj}}])
		return rows[0][0]

	latest_access_date = property(_get_latest_access_date)

	#--------------------------------------------------------
	def _get_diagnostic_certainty_description(self):
		return diagnostic_certainty_classification2str(self._payload[self._idx['diagnostic_certainty_classification']])

	diagnostic_certainty_description = property(_get_diagnostic_certainty_description)

	#--------------------------------------------------------
	def _get_formatted_revision_history(self):
		cmd = """SELECT
				'<N/A>'::TEXT as audit__action_applied,
				NULL AS audit__action_when,
				'<N/A>'::TEXT AS audit__action_by,
				pk_audit,
				row_version,
				modified_when,
				modified_by,
				pk, fk_health_issue, description, is_open, fk_encounter,
				diagnostic_certainty_classification,
				summary
			FROM clin.episode
			WHERE pk = %(pk_episode)s
		UNION ALL (
			SELECT
				audit_action as audit__action_applied,
				audit_when as audit__action_when,
				audit_by as audit__action_by,
				pk_audit,
				orig_version as row_version,
				orig_when as modified_when,
				orig_by as modified_by,
				pk, fk_health_issue, description, is_open, fk_encounter,
				diagnostic_certainty_classification,
				summary
			FROM audit.log_episode
			WHERE pk = %(pk_episode)s
		)
		ORDER BY row_version DESC
		"""
		args = {'pk_episode': self.pk_obj}
		title = _('Episode: %s%s%s') % (
			gmTools.u_left_double_angle_quote,
			self._payload[self._idx['description']],
			gmTools.u_right_double_angle_quote
		)
		return '\n'.join(self._get_revision_history(cmd, args, title))

	formatted_revision_history = property(_get_formatted_revision_history)

	#--------------------------------------------------------
	def _get_generic_codes(self):
		if len(self._payload[self._idx['pk_generic_codes']]) == 0:
			return []

		cmd = gmCoding._SQL_get_generic_linked_codes % 'pk_generic_code = ANY(%(pks)s)'
		args = {'pks': self._payload[self._idx['pk_generic_codes']]}
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)
		return [ gmCoding.cGenericLinkedCode(row = {'data': r, 'idx': idx, 'pk_field': 'pk_lnk_code2item'}) for r in rows ]

	def _set_generic_codes(self, pk_codes):
		queries = []
		# remove all codes
		if len(self._payload[self._idx['pk_generic_codes']]) > 0:
			queries.append ({
				'cmd': 'DELETE FROM clin.lnk_code2episode WHERE fk_item = %(epi)s AND fk_generic_code = ANY(%(codes)s)',
				'args': {
					'epi': self._payload[self._idx['pk_episode']],
					'codes': self._payload[self._idx['pk_generic_codes']]
				}
			})
		# add new codes
		for pk_code in pk_codes:
			queries.append ({
				'cmd': 'INSERT INTO clin.lnk_code2episode (fk_item, fk_generic_code) VALUES (%(epi)s, %(pk_code)s)',
				'args': {
					'epi': self._payload[self._idx['pk_episode']],
					'pk_code': pk_code
				}
			})
		if len(queries) == 0:
			return
		# run it all in one transaction
		rows, idx = gmPG2.run_rw_queries(queries = queries)
		return

	generic_codes = property(_get_generic_codes, _set_generic_codes)

	#--------------------------------------------------------
	def _get_has_narrative(self):
		cmd = """SELECT EXISTS (
			SELECT 1 FROM clin.clin_narrative
			WHERE
				fk_episode = %(epi)s
					AND
				fk_encounter IN (
					SELECT pk FROM clin.encounter WHERE fk_patient = %(pat)s
				)
		)"""
		args = {
			'pat': self._payload[self._idx['pk_patient']],
			'epi': self._payload[self._idx['pk_episode']]
		}
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = False)
		return rows[0][0]

	has_narrative = property(_get_has_narrative)

	#--------------------------------------------------------
	def _get_health_issue(self):
		if self._payload[self._idx['pk_health_issue']] is None:
			return None
		return cHealthIssue(self._payload[self._idx['pk_health_issue']])

	health_issue = property(_get_health_issue)

#============================================================
def create_episode(pk_health_issue=None, episode_name=None, is_open=False, allow_dupes=False, encounter=None, link_obj=None):
	"""Creates a new episode for a given patient's health issue.

	pk_health_issue - given health issue PK
	episode_name - name of episode
	"""
	if not allow_dupes:
		try:
			episode = cEpisode(name = episode_name, health_issue = pk_health_issue, encounter = encounter, link_obj = link_obj)
			if episode['episode_open'] != is_open:
				episode['episode_open'] = is_open
				episode.save_payload()
			return episode
		except gmExceptions.ConstructorError:
			pass

	queries = []
	cmd = "INSERT INTO clin.episode (fk_health_issue, description, is_open, fk_encounter) VALUES (%s, %s, %s::boolean, %s)"
	queries.append({'cmd': cmd, 'args': [pk_health_issue, episode_name, is_open, encounter]})
	queries.append({'cmd': cEpisode._cmd_fetch_payload % "currval('clin.episode_pk_seq')"})
	rows, idx = gmPG2.run_rw_queries(link_obj = link_obj, queries = queries, return_data=True, get_col_idx=True)

	episode = cEpisode(row = {'data': rows[0], 'idx': idx, 'pk_field': 'pk_episode'})
	return episode

#-----------------------------------------------------------
def delete_episode(episode=None):
	if isinstance(episode, cEpisode):
		pk = episode['pk_episode']
	else:
		pk = int(episode)

	cmd = 'DELETE FROM clin.episode WHERE pk = %(pk)s'

	try:
		gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': {'pk': pk}}])
	except gmPG2.dbapi.IntegrityError:
		# should be parsing pgcode/and or error message
		_log.exception('cannot delete episode, it is in use')
		return False

	return True

#-----------------------------------------------------------
def episode2problem(episode=None, allow_closed=False):
	return cProblem (
		aPK_obj = {
			'pk_patient': episode['pk_patient'],
			'pk_episode': episode['pk_episode'],
			'pk_health_issue': episode['pk_health_issue']
		},
		try_potential_problems = allow_closed
	)

#-----------------------------------------------------------
_SQL_best_guess_clinical_start_date_for_episode = """
	SELECT MIN(earliest) FROM (
		-- modified_when of episode,
		-- earliest possible thereof = when created,
		-- should actually go all the way back into audit.log_episode
		(SELECT c_epi.modified_when AS earliest FROM clin.episode c_epi WHERE c_epi.pk = %(pk)s)

			UNION ALL

		-- last modification of encounter in which created,
		-- earliest-possible thereof = initial creation of that encounter
		(SELECT c_enc.modified_when AS earliest FROM clin.encounter c_enc WHERE c_enc.pk = (
			SELECT fk_encounter FROM clin.episode WHERE pk = %(pk)s
		))
			UNION ALL

		-- start of encounter in which created,
		-- earliest-possible thereof = explicitly set by user
		(SELECT c_enc.started AS earliest FROM clin.encounter c_enc WHERE c_enc.pk = (
			SELECT fk_encounter FROM clin.episode WHERE pk = %(pk)s
		))
			UNION ALL

		-- start of encounters of clinical items linked to this episode,
		-- earliest-possible thereof = explicitly set by user
		(SELECT MIN(started) AS earliest FROM clin.encounter WHERE pk IN (
			SELECT fk_encounter FROM clin.clin_root_item WHERE fk_episode = %(pk)s
		))
			UNION ALL

		-- .clin_when of clinical items linked to this episode,
		-- earliest-possible thereof = explicitly set by user
		(SELECT MIN(clin_when) AS earliest FROM clin.clin_root_item WHERE fk_episode = %(pk)s)

			UNION ALL

		-- earliest modification time of clinical items linked to this episode
		-- this CAN be used since if an item is linked to an episode it can be
		-- assumed the episode (should have) existed at the time of creation
		(SELECT MIN(modified_when) AS earliest FROM clin.clin_root_item WHERE fk_episode = %(pk)s)

			UNION ALL

		-- there may not be items, but there may still be documents ...
		(SELECT MIN(clin_when) AS earliest FROM blobs.doc_med WHERE fk_episode = %(pk)s)
	) AS candidates
"""

def get_best_guess_clinical_start_date_for_episode(pk_episode=None):
	assert (pk_episode is not None), '<pk_episode> must not be None'
	query = {
		'cmd': _SQL_best_guess_clinical_start_date_for_episode,
		'args': {'pk': pk_episode}
	}
	rows, idx = gmPG2.run_ro_queries(queries = [query])
	return rows[0][0]

#-----------------------------------------------------------
_SQL_best_guess_clinical_end_date_for_episode = """
	SELECT
		CASE WHEN
			-- if open episode ...
			(SELECT is_open FROM clin.episode WHERE pk = %(pk)s)
		THEN
			-- ... no end date
			NULL::timestamp with time zone
		ELSE (
			SELECT COALESCE (
				(SELECT
					latest --, source_type
				 FROM (
					-- latest explicit .clin_when of clinical items linked to this episode
					(SELECT
						MAX(clin_when) AS latest,
						'clin.episode.pk = clin.clin_root_item.fk_episode -> .clin_when'::text AS source_type
					 FROM clin.clin_root_item
					 WHERE fk_episode = %(pk)s
					)
						UNION ALL
					-- latest explicit .clin_when of documents linked to this episode
					(SELECT
						MAX(clin_when) AS latest,
						'clin.episode.pk = blobs.doc_med.fk_episode -> .clin_when'::text AS source_type
					 FROM blobs.doc_med
					 WHERE fk_episode = %(pk)s
					)
				 ) AS candidates
				 ORDER BY latest DESC NULLS LAST
				 LIMIT 1
				),
				-- last ditch, always exists, only use when no clinical items or documents linked:
				-- last modification, latest = when last changed to the current state
				(SELECT c_epi.modified_when AS latest --, 'clin.episode.modified_when'::text AS source_type
				 FROM clin.episode c_epi WHERE c_epi.pk = %(pk)s
				)
			)
		)
		END
"""

def get_best_guess_clinical_end_date_for_episode(pk_episode=None):
	assert (pk_episode is not None), '<pk_episode> must not be None'
	query = {
		'cmd': _SQL_best_guess_clinical_end_date_for_episode,
		'args': {'pk': pk_episode}
	}
	rows, idx = gmPG2.run_ro_queries(queries = [query], get_col_idx = False)
	return rows[0][0]

#-----------------------------------------------------------
def format_clinical_duration_of_episode(start=None, end=None):
	assert (start is not None), '<start> must not be None'

	if end is None:
		start_end_str = '%s-%s' % (
			gmDateTime.pydt_strftime(start, "%b'%y"),
			gmTools.u_ellipsis
		)
		start_end_str_long = '%s - %s' % (
			gmDateTime.pydt_strftime(start, '%b %d %Y'),
			gmTools.u_ellipsis
		)
		duration_str = _('%s so far') % gmDateTime.format_interval_medically(gmDateTime.pydt_now_here() - start)
		return (start_end_str, start_end_str_long, duration_str)

	duration_str = gmDateTime.format_interval_medically(end - start)
	# year different:
	if end.year != start.year:
		start_end_str = '%s-%s' % (
			gmDateTime.pydt_strftime(start, "%b'%y"),
			gmDateTime.pydt_strftime(end, "%b'%y")
		)
		start_end_str_long = '%s - %s' % (
			gmDateTime.pydt_strftime(start, '%b %d %Y'),
			gmDateTime.pydt_strftime(end, '%b %d %Y')
		)
		return (start_end_str, start_end_str_long, duration_str)
	# same year:
	if end.month != start.month:
		start_end_str = '%s-%s' % (
			gmDateTime.pydt_strftime(start, '%b'),
			gmDateTime.pydt_strftime(end, "%b'%y")
		)
		start_end_str_long = '%s - %s' % (
			gmDateTime.pydt_strftime(start, '%b %d'),
			gmDateTime.pydt_strftime(end, '%b %d %Y')
		)
		return (start_end_str, start_end_str_long, duration_str)

	# same year and same month
	start_end_str = gmDateTime.pydt_strftime(start, "%b'%y")
	start_end_str_long = gmDateTime.pydt_strftime(start, '%b %d %Y')
	return (start_end_str, start_end_str_long, duration_str)

#============================================================
class cEpisodeMatchProvider(gmMatchProvider.cMatchProvider_SQL2):
	"""Find episodes for patient."""

	_SQL_episode_start = _SQL_best_guess_clinical_start_date_for_episode % {'pk': 'c_vpe.pk_episode'}
	_SQL_episode_end = _SQL_best_guess_clinical_end_date_for_episode % {'pk': 'c_vpe.pk_episode'}

	_SQL_open_episodes = """
		SELECT
			c_vpe.pk_episode,
			c_vpe.description
				AS episode,
			c_vpe.health_issue,
			1 AS rank,
			(%s) AS episode_start,
			NULL::timestamp with time zone AS episode_end
		FROM
			clin.v_pat_episodes c_vpe
		WHERE
			c_vpe.episode_open IS TRUE
				AND
			c_vpe.description %%(fragment_condition)s
			%%(ctxt_pat)s
	""" % _SQL_episode_start

	_SQL_closed_episodes = """
		SELECT
			c_vpe.pk_episode,
			c_vpe.description
				AS episode,
			c_vpe.health_issue,
			2 AS rank,
			(%s) AS episode_start,
			(%s) AS episode_end
		FROM
			clin.v_pat_episodes c_vpe
		WHERE
			c_vpe.episode_open IS FALSE
				AND
			c_vpe.description %%(fragment_condition)s
			%%(ctxt_pat)s
	""" % (
		_SQL_episode_start,
		_SQL_episode_end
	)

	#--------------------------------------------------------
	def __init__(self):
		query = """
			(
				%s
			) UNION ALL (
				%s
			)
			ORDER BY rank, episode
			LIMIT 30""" % (
				cEpisodeMatchProvider._SQL_open_episodes,
				cEpisodeMatchProvider._SQL_closed_episodes
			)
		ctxt = {'ctxt_pat': {'where_part': 'AND pk_patient = %(pat)s', 'placeholder': 'pat'}}
		super().__init__(queries = [query], context = ctxt)

	#--------------------------------------------------------
	def _find_matches(self, fragment_condition):
		try:
			pat = self._context_vals['pat']
		except KeyError:
			pat = None
		if not pat:
			# not patient, no search
			return (False, [])

		return super()._find_matches(fragment_condition)

	#--------------------------------------------------------
	def _rows2matches(self, rows):
		matches = []
		for row in rows:
			match = {
				'weight': 0,
				'data': row['pk_episode']
			}
			label = '%s (%s)%s' % (
				row['episode'],
				format_clinical_duration_of_episode (
					start = row['episode_start'],
					end = row['episode_end']
				)[0],
				gmTools.coalesce (
					row['health_issue'],
					'',
					' - %s'
				)
			)
			match['list_label'] = label
			match['field_label'] = label
			matches.append(match)
		return matches

#============================================================
# encounter API
#============================================================
SQL_get_encounters = "SELECT * FROM clin.v_pat_encounters WHERE %s"

class cEncounter(gmBusinessDBObject.cBusinessDBObject):
	"""Represents one encounter."""

	_cmd_fetch_payload = SQL_get_encounters % 'pk_encounter = %s'
	_cmds_store_payload = [
		"""UPDATE clin.encounter SET
				started = %(started)s,
				last_affirmed = %(last_affirmed)s,
				fk_location = %(pk_org_unit)s,
				fk_type = %(pk_type)s,
				reason_for_encounter = gm.nullify_empty_string(%(reason_for_encounter)s),
				assessment_of_encounter = gm.nullify_empty_string(%(assessment_of_encounter)s)
			WHERE
				pk = %(pk_encounter)s AND
				xmin = %(xmin_encounter)s
			""",
		# need to return all fields so we can survive in-place upgrades
		"SELECT * FROM clin.v_pat_encounters WHERE pk_encounter = %(pk_encounter)s"
	]
	_updatable_fields = [
		'started',
		'last_affirmed',
		'pk_org_unit',
		'pk_type',
		'reason_for_encounter',
		'assessment_of_encounter'
	]
	#--------------------------------------------------------
	def set_active(self):
		"""Set the encounter as the active one.

		"Setting active" means making sure the encounter
		row has the youngest "last_affirmed" timestamp of
		all encounter rows for this patient.
		"""
		self['last_affirmed'] = gmDateTime.pydt_now_here()
		self.save()
	#--------------------------------------------------------
	def lock(self, exclusive=False, link_obj=None):
		return lock_encounter(self.pk_obj, exclusive = exclusive, link_obj = link_obj)
	#--------------------------------------------------------
	def unlock(self, exclusive=False, link_obj=None):
		return unlock_encounter(self.pk_obj, exclusive = exclusive, link_obj = link_obj)
	#--------------------------------------------------------
	def transfer_clinical_data(self, source_episode=None, target_episode=None):
		"""
		Moves every element currently linked to the current encounter
		and the source_episode onto target_episode.

		@param source_episode The episode the elements are currently linked to.
		@type target_episode A cEpisode intance.
		@param target_episode The episode the elements will be relinked to.
		@type target_episode A cEpisode intance.
		"""
		if source_episode['pk_episode'] == target_episode['pk_episode']:
			return True

		cmd = """
			UPDATE clin.clin_root_item
			SET fk_episode = %(trg)s
 			WHERE
				fk_encounter = %(enc)s AND
				fk_episode = %(src)s
			"""
		rows, idx = gmPG2.run_rw_queries(queries = [{
			'cmd': cmd,
			'args': {
				'trg': target_episode['pk_episode'],
				'enc': self.pk_obj,
				'src': source_episode['pk_episode']
			}
		}])
		self.refetch_payload()
		return True

	#--------------------------------------------------------
	def transfer_all_data_to_another_encounter(self, pk_target_encounter=None):
		if pk_target_encounter == self.pk_obj:
			return True
		cmd = "SELECT clin.transfer_all_encounter_data(%(src)s, %(trg)s)"
		args = {
			'src': self.pk_obj,
			'trg': pk_target_encounter
		}
		rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])
		return True

#	conn = gmPG2.get_connection()
#	curs = conn.cursor()
#	curs.callproc('clin.get_hints_for_patient', [pk_identity])
#	rows = curs.fetchall()
#	idx = gmPG2.get_col_indices(curs)
#	curs.close()
#	conn.rollback()

	#--------------------------------------------------------
	def same_payload(self, another_object=None):

		relevant_fields = [
			'pk_org_unit',
			'pk_type',
			'pk_patient',
			'reason_for_encounter',
			'assessment_of_encounter'
		]
		for field in relevant_fields:
			if self._payload[self._idx[field]] != another_object[field]:
				_log.debug('mismatch on [%s]: "%s" vs. "%s"', field, self._payload[self._idx[field]], another_object[field])
				return False

		relevant_fields = [
			'started',
			'last_affirmed',
		]
		for field in relevant_fields:
			if self._payload[self._idx[field]] is None:
				if another_object[field] is None:
					continue
				_log.debug('mismatch on [%s]: here="%s", other="%s"', field, self._payload[self._idx[field]], another_object[field])
				return False

			if another_object[field] is None:
				return False

			# compares at seconds granularity
			if self._payload[self._idx[field]].strftime('%Y-%m-%d %H:%M:%S') != another_object[field].strftime('%Y-%m-%d %H:%M:%S'):
				_log.debug('mismatch on [%s]: here="%s", other="%s"', field, self._payload[self._idx[field]], another_object[field])
				return False

		# compare codes
		# 1) RFE
		if another_object['pk_generic_codes_rfe'] is None:
			if self._payload[self._idx['pk_generic_codes_rfe']] is not None:
				return False
		if another_object['pk_generic_codes_rfe'] is not None:
			if self._payload[self._idx['pk_generic_codes_rfe']] is None:
				return False
		if (
			(another_object['pk_generic_codes_rfe'] is None)
				and
			(self._payload[self._idx['pk_generic_codes_rfe']] is None)
		) is False:
			if set(another_object['pk_generic_codes_rfe']) != set(self._payload[self._idx['pk_generic_codes_rfe']]):
				return False
		# 2) AOE
		if another_object['pk_generic_codes_aoe'] is None:
			if self._payload[self._idx['pk_generic_codes_aoe']] is not None:
				return False
		if another_object['pk_generic_codes_aoe'] is not None:
			if self._payload[self._idx['pk_generic_codes_aoe']] is None:
				return False
		if (
			(another_object['pk_generic_codes_aoe'] is None)
				and
			(self._payload[self._idx['pk_generic_codes_aoe']] is None)
		) is False:
			if set(another_object['pk_generic_codes_aoe']) != set(self._payload[self._idx['pk_generic_codes_aoe']]):
				return False

		return True
	#--------------------------------------------------------
	def has_clinical_data(self):
		cmd = """
select exists (
	select 1 from clin.v_pat_items where pk_patient = %(pat)s and pk_encounter = %(enc)s
		union all
	select 1 from blobs.v_doc_med where pk_patient = %(pat)s and pk_encounter = %(enc)s
)"""
		args = {
			'pat': self._payload[self._idx['pk_patient']],
			'enc': self.pk_obj
		}
		rows, idx = gmPG2.run_ro_queries (
			queries = [{
				'cmd': cmd,
				'args': args
			}]
		)
		return rows[0][0]

	#--------------------------------------------------------
	def has_narrative(self):
		cmd = """
select exists (
	select 1 from clin.v_pat_items where pk_patient=%(pat)s and pk_encounter=%(enc)s
)"""
		args = {
			'pat': self._payload[self._idx['pk_patient']],
			'enc': self.pk_obj
		}
		rows, idx = gmPG2.run_ro_queries (
			queries = [{
				'cmd': cmd,
				'args': args
			}]
		)
		return rows[0][0]
	#--------------------------------------------------------
	def has_soap_narrative(self, soap_cats=None):
		"""soap_cats: <space> = admin category"""

		if soap_cats is None:
			soap_cats = 'soap '
		else:
			soap_cats = soap_cats.casefold()

		cats = []
		for cat in soap_cats:
			if cat in 'soapu':
				cats.append(cat)
				continue
			if cat == ' ':
				cats.append(None)

		cmd = """
			SELECT EXISTS (
				SELECT 1 FROM clin.clin_narrative
				WHERE
					fk_encounter = %(enc)s
						AND
					soap_cat = ANY(%(cats)s)
				LIMIT 1
			)
		"""
		args = {'enc': self._payload[self._idx['pk_encounter']], 'cats': cats}
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd,'args': args}])
		return rows[0][0]
	#--------------------------------------------------------
	def has_documents(self):
		cmd = """
select exists (
	select 1 from blobs.v_doc_med where pk_patient = %(pat)s and pk_encounter = %(enc)s
)"""
		args = {
			'pat': self._payload[self._idx['pk_patient']],
			'enc': self.pk_obj
		}
		rows, idx = gmPG2.run_ro_queries (
			queries = [{
				'cmd': cmd,
				'args': args
			}]
		)
		return rows[0][0]
	#--------------------------------------------------------
	def get_latest_soap(self, soap_cat=None, episode=None):

		if soap_cat is not None:
			soap_cat = soap_cat.casefold()

		if episode is None:
			epi_part = 'fk_episode is null'
		else:
			epi_part = 'fk_episode = %(epi)s'

		cmd = """
select narrative
from clin.clin_narrative
where
	fk_encounter = %%(enc)s
		and
	soap_cat = %%(cat)s
		and
	%s
order by clin_when desc
limit 1
		""" % epi_part

		args = {'enc': self.pk_obj, 'cat': soap_cat, 'epi': episode}

		rows, idx = gmPG2.run_ro_queries (
			queries = [{
				'cmd': cmd,
				'args': args
			}]
		)
		if len(rows) == 0:
			return None

		return rows[0][0]
	#--------------------------------------------------------
	def get_episodes(self, exclude=None):
		cmd = """
			SELECT * FROM clin.v_pat_episodes
			WHERE pk_episode IN (
					SELECT DISTINCT fk_episode
					FROM clin.clin_root_item
					WHERE fk_encounter = %%(enc)s

						UNION

					SELECT DISTINCT fk_episode
					FROM blobs.doc_med
					WHERE fk_encounter = %%(enc)s
			) %s"""
		args = {'enc': self.pk_obj}
		if exclude is not None:
			cmd = cmd % 'AND pk_episode <> ALL(%(loincs)s)'
			args['excluded'] = exclude
		else:
			cmd = cmd % ''
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)
		return [ cEpisode(row = {'data': r, 'idx': idx, 'pk_field': 'pk_episode'})  for r in rows ]

	episodes = property(get_episodes)

	#--------------------------------------------------------
	def add_code(self, pk_code=None, field=None):
		"""<pk_code> must be a value from ref.coding_system_root.pk_coding_system (clin.lnk_code2item_root.fk_generic_code)"""
		if field == 'rfe':
			cmd = "INSERT INTO clin.lnk_code2rfe (fk_item, fk_generic_code) values (%(item)s, %(code)s)"
		elif field == 'aoe':
			cmd = "INSERT INTO clin.lnk_code2aoe (fk_item, fk_generic_code) values (%(item)s, %(code)s)"
		else:
			raise ValueError('<field> must be one of "rfe" or "aoe", not "%s"', field)
		args = {
			'item': self._payload[self._idx['pk_encounter']],
			'code': pk_code
		}
		rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])
		return True

	#--------------------------------------------------------
	def remove_code(self, pk_code=None, field=None):
		"""<pk_code> must be a value from ref.coding_system_root.pk_coding_system (clin.lnk_code2item_root.fk_generic_code)"""
		if field == 'rfe':
			cmd = "DELETE FROM clin.lnk_code2rfe WHERE fk_item = %(item)s AND fk_generic_code = %(code)s"
		elif field == 'aoe':
			cmd = "DELETE FROM clin.lnk_code2aoe WHERE fk_item = %(item)s AND fk_generic_code = %(code)s"
		else:
			raise ValueError('<field> must be one of "rfe" or "aoe", not "%s"', field)
		args = {
			'item': self._payload[self._idx['pk_encounter']],
			'code': pk_code
		}
		rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])
		return True

	#--------------------------------------------------------
	# data formatting
	#--------------------------------------------------------
	def format_soap(self, episodes=None, left_margin=0, soap_cats='soapu', emr=None, issues=None):

		lines = []
		for soap_cat in gmSoapDefs.soap_cats_str2list(soap_cats):
			soap_cat_narratives = emr.get_clin_narrative (
				episodes = episodes,
				issues = issues,
				encounters = [self._payload[self._idx['pk_encounter']]],
				soap_cats = [soap_cat]
			)
			if soap_cat_narratives is None:
				continue
			if len(soap_cat_narratives) == 0:
				continue

			lines.append('%s%s %s %s' % (
				gmTools.u_box_top_left_arc,
				gmTools.u_box_horiz_single,
				gmSoapDefs.soap_cat2l10n_str[soap_cat],
				gmTools.u_box_horiz_single * 5
			))
			for soap_entry in soap_cat_narratives:
				txt = gmTools.wrap (
					text = soap_entry['narrative'],
					width = 75,
					initial_indent = '',
					subsequent_indent = (' ' * left_margin)
				)
				lines.append(txt)
				when = gmDateTime.pydt_strftime (
					soap_entry['date'],
					format = '%Y-%m-%d %H:%M',
					accuracy = gmDateTime.acc_minutes
				)
				txt = '%s%s %.8s, %s %s' % (
					' ' * 40,
					gmTools.u_box_horiz_light_heavy,
					soap_entry['modified_by'],
					when,
					gmTools.u_box_horiz_heavy_light
				)
				lines.append(txt)
				lines.append('')

		return lines

	#--------------------------------------------------------
	def format_latex(self, date_format=None, soap_cats=None, soap_order=None):

		nothing2format = (
			(self._payload[self._idx['reason_for_encounter']] is None)
				and
			(self._payload[self._idx['assessment_of_encounter']] is None)
				and
			(self.has_soap_narrative(soap_cats = 'soapu') is False)
		)
		if nothing2format:
			return ''

		if date_format is None:
			date_format = '%A, %b %d %Y'

		tex =  '% -------------------------------------------------------------\n'
		tex += '% much recommended: \\usepackage(tabu)\n'
		tex += '% much recommended: \\usepackage(longtable)\n'
		tex += '% best wrapped in: "\\begin{longtabu} to \\textwidth {lX[,L]}"\n'
		tex += '% -------------------------------------------------------------\n'
		tex += '\\hline \n'
		tex += '\\multicolumn{2}{l}{%s: %s ({\\footnotesize %s - %s})} \\tabularnewline \n' % (
			gmTools.tex_escape_string(self._payload[self._idx['l10n_type']]),
			gmTools.tex_escape_string (
				gmDateTime.pydt_strftime (
					self._payload[self._idx['started']],
					date_format,
					accuracy = gmDateTime.acc_days
				)
			),
			gmTools.tex_escape_string (
				gmDateTime.pydt_strftime (
					self._payload[self._idx['started']],
					'%H:%M',
					accuracy = gmDateTime.acc_minutes
				)
			),
			gmTools.tex_escape_string (
				gmDateTime.pydt_strftime (
					self._payload[self._idx['last_affirmed']],
					'%H:%M',
					accuracy = gmDateTime.acc_minutes
				)
			)
		)
		tex += '\\hline \n'

		if self._payload[self._idx['reason_for_encounter']] is not None:
			tex += '%s & %s \\tabularnewline \n' % (
				gmTools.tex_escape_string(_('RFE')),
				gmTools.tex_escape_string(self._payload[self._idx['reason_for_encounter']])
			)
		if self._payload[self._idx['assessment_of_encounter']] is not None:
			tex += '%s & %s \\tabularnewline \n' % (
				gmTools.tex_escape_string(_('AOE')),
				gmTools.tex_escape_string(self._payload[self._idx['assessment_of_encounter']])
			)

		for epi in self.get_episodes():
			soaps = epi.get_narrative(soap_cats = soap_cats, encounters = [self.pk_obj], order_by = soap_order)
			if len(soaps) == 0:
				continue
			tex += '\\multicolumn{2}{l}{\\emph{%s: %s%s}} \\tabularnewline \n' % (
				gmTools.tex_escape_string(_('Problem')),
				gmTools.tex_escape_string(epi['description']),
				gmTools.tex_escape_string (
					gmTools.coalesce (
						value2test = diagnostic_certainty_classification2str(epi['diagnostic_certainty_classification']),
						return_instead = '',
						template4value = ' {\\footnotesize [%s]}',
						none_equivalents = [None, '']
					)
				)
			)
			if epi['pk_health_issue'] is not None:
				tex += '\\multicolumn{2}{l}{\\emph{%s: %s%s}} \\tabularnewline \n' % (
					gmTools.tex_escape_string(_('Health issue')),
					gmTools.tex_escape_string(epi['health_issue']),
					gmTools.tex_escape_string (
						gmTools.coalesce (
							value2test = diagnostic_certainty_classification2str(epi['diagnostic_certainty_classification_issue']),
							return_instead = '',
							template4value = ' {\\footnotesize [%s]}',
							none_equivalents = [None, '']
						)
					)
				)
			for soap in soaps:
				tex += '{\\small %s} & {\\small %s} \\tabularnewline \n' % (
					gmTools.tex_escape_string(gmSoapDefs.soap_cat2l10n[soap['soap_cat']]),
					gmTools.tex_escape_string(soap['narrative'], replace_eol = True)
				)
			tex += ' & \\tabularnewline \n'

		return tex

	#--------------------------------------------------------
	def __format_header_fancy(self, left_margin=0):
		lines = []

		lines.append('%s%s: %s - %s (@%s)%s [#%s]' % (
			' ' * left_margin,
			self._payload[self._idx['l10n_type']],
			self._payload[self._idx['started_original_tz']].strftime('%Y-%m-%d %H:%M'),
			self._payload[self._idx['last_affirmed_original_tz']].strftime('%H:%M'),
			self._payload[self._idx['source_time_zone']],
			gmTools.coalesce (
				self._payload[self._idx['assessment_of_encounter']],
				'',
				' %s%%s%s' % (gmTools.u_left_double_angle_quote, gmTools.u_right_double_angle_quote)
			),
			self._payload[self._idx['pk_encounter']]
		))

		lines.append(_('  your time: %s - %s  (@%s = %s%s)\n') % (
			self._payload[self._idx['started']].strftime('%Y-%m-%d %H:%M'),
			self._payload[self._idx['last_affirmed']].strftime('%H:%M'),
			gmDateTime.current_local_timezone_name,
			gmTools.bool2subst (
				gmDateTime.dst_currently_in_effect,
				gmDateTime.py_dst_timezone_name,
				gmDateTime.py_timezone_name
			),
			gmTools.bool2subst(gmDateTime.dst_currently_in_effect, ' - ' + _('daylight savings time in effect'), '')
		))

		if self._payload[self._idx['praxis_branch']] is not None:
			lines.append(_('Location: %s (%s)') % (self._payload[self._idx['praxis_branch']], self._payload[self._idx['praxis']]))

		if self._payload[self._idx['reason_for_encounter']] is not None:
			lines.append('%s: %s' % (_('RFE'), self._payload[self._idx['reason_for_encounter']]))
			codes = self.generic_codes_rfe
			for c in codes:
				lines.append(' %s: %s (%s - %s)' % (
					c['code'],
					c['term'],
					c['name_short'],
					c['version']
				))
			if len(codes) > 0:
				lines.append('')

		if self._payload[self._idx['assessment_of_encounter']] is not None:
			lines.append('%s: %s' % (_('AOE'), self._payload[self._idx['assessment_of_encounter']]))
			codes = self.generic_codes_aoe
			for c in codes:
				lines.append(' %s: %s (%s - %s)' % (
					c['code'],
					c['term'],
					c['name_short'],
					c['version']
				))
			if len(codes) > 0:
				lines.append('')
			del codes
		return lines

	#--------------------------------------------------------
	def format_header(self, fancy_header=True, left_margin=0, with_rfe_aoe=False):
		lines = []

		if fancy_header:
			return self.__format_header_fancy(left_margin = left_margin)

		now = gmDateTime.pydt_now_here()
		if now.strftime('%Y-%m-%d') == self._payload[self._idx['started_original_tz']].strftime('%Y-%m-%d'):
			start = '%s %s' % (
				_('today'),
				self._payload[self._idx['started_original_tz']].strftime('%H:%M')
			)
		else:
			start = self._payload[self._idx['started_original_tz']].strftime('%Y-%m-%d %H:%M')
		lines.append('%s%s: %s - %s%s%s' % (
			' ' * left_margin,
			self._payload[self._idx['l10n_type']],
			start,
			self._payload[self._idx['last_affirmed_original_tz']].strftime('%H:%M'),
			gmTools.coalesce(self._payload[self._idx['assessment_of_encounter']], '', ' \u00BB%s\u00AB'),
			gmTools.coalesce(self._payload[self._idx['praxis_branch']], '', ' @%s')
		))
		if with_rfe_aoe:
			if self._payload[self._idx['reason_for_encounter']] is not None:
				lines.append('%s: %s' % (_('RFE'), self._payload[self._idx['reason_for_encounter']]))
			codes = self.generic_codes_rfe
			for c in codes:
				lines.append(' %s: %s (%s - %s)' % (
					c['code'],
					c['term'],
					c['name_short'],
					c['version']
				))
			if len(codes) > 0:
				lines.append('')
			if self._payload[self._idx['assessment_of_encounter']] is not None:
				lines.append('%s: %s' % (_('AOE'), self._payload[self._idx['assessment_of_encounter']]))
			codes = self.generic_codes_aoe
			if len(codes) > 0:
				lines.append('')
			for c in codes:
				lines.append(' %s: %s (%s - %s)' % (
					c['code'],
					c['term'],
					c['name_short'],
					c['version']
				))
			if len(codes) > 0:
				lines.append('')
			del codes

		return lines

	#--------------------------------------------------------
	def format_by_episode(self, episodes=None, issues=None, left_margin=0, patient=None, with_soap=False, with_tests=True, with_docs=True, with_vaccinations=True, with_family_history=True):

		if patient is not None:
			emr = patient.emr

		lines = []
		if episodes is None:
			episodes = [ e['pk_episode'] for e in self.episodes ]

		for pk in episodes:
			epi = cEpisode(aPK_obj = pk)
			lines.append(_('\nEpisode %s%s%s%s:') % (
				gmTools.u_left_double_angle_quote,
				epi['description'],
				gmTools.u_right_double_angle_quote,
				gmTools.coalesce(epi['health_issue'], '', ' (%s)')
			))

			# soap
			if with_soap:
				if patient.ID != self._payload[self._idx['pk_patient']]:
					msg = '<patient>.ID = %s but encounter %s belongs to patient %s' % (
						patient.ID,
						self._payload[self._idx['pk_encounter']],
						self._payload[self._idx['pk_patient']]
					)
					raise ValueError(msg)
				lines.extend(self.format_soap (
					episodes = [pk],
					left_margin = left_margin,
					soap_cats = None,		# meaning: all
					emr = emr,
					issues = issues
				))

			# test results
			if with_tests:
				tests = emr.get_test_results_by_date (
					episodes = [pk],
					encounter = self._payload[self._idx['pk_encounter']]
				)
				if len(tests) > 0:
					lines.append('')
					lines.append(_('Measurements and Results:'))

				for t in tests:
					lines.append(t.format())

				del tests

			# vaccinations
			if with_vaccinations:
				vaccs = emr.get_vaccinations (
					episodes = [pk],
					encounters = [ self._payload[self._idx['pk_encounter']] ],
					order_by = 'date_given DESC, vaccine'
				)
				if len(vaccs) > 0:
					lines.append('')
					lines.append(_('Vaccinations:'))
				for vacc in vaccs:
					lines.extend(vacc.format (
						with_indications = True,
						with_comment = True,
						with_reaction = True,
						date_format = '%Y-%m-%d'
					))
				del vaccs

			# family history
			if with_family_history:
				fhx = emr.get_family_history(episodes = [pk])
				if len(fhx) > 0:
					lines.append('')
					lines.append(_('Family History: %s') % len(fhx))
				for f in fhx:
					lines.append(f.format (
						left_margin = (left_margin + 1),
						include_episode = False,
						include_comment = True
					))
				del fhx

			# documents
			if with_docs:
				doc_folder = patient.get_document_folder()
				docs = doc_folder.get_documents (
					pk_episodes = [pk],
					encounter = self._payload[self._idx['pk_encounter']]
				)
				if len(docs) > 0:
					lines.append('')
					lines.append(_('Documents:'))
				for d in docs:
					lines.append(' ' + d.format(single_line = True))
				del docs

		return lines

	#--------------------------------------------------------
	def format_maximum_information(self, patient=None):
		if patient is None:
			from Gnumed.business.gmPerson import gmCurrentPatient, cPerson
			if self._payload[self._idx['pk_patient']] == gmCurrentPatient().ID:
				patient = gmCurrentPatient()
			else:
				patient = cPerson(self._payload[self._idx['pk_patient']])

		return self.format (
			patient = patient,
			fancy_header = True,
			with_rfe_aoe = True,
			with_soap = True,
			with_docs = True,
			with_tests = False,
			with_vaccinations = True,
			with_co_encountlet_hints = True,
			with_family_history = True,
			by_episode = False,
			return_list = True
		)

	#--------------------------------------------------------
	def format(self, episodes=None, with_soap=False, left_margin=0, patient=None, issues=None, with_docs=True, with_tests=True, fancy_header=True, with_vaccinations=True, with_co_encountlet_hints=False, with_rfe_aoe=False, with_family_history=True, by_episode=False, return_list=False):
		"""Format an encounter.

		with_co_encountlet_hints:
			- whether to include which *other* episodes were discussed during this encounter
			- (only makes sense if episodes != None)
		"""
		lines = self.format_header (
			fancy_header = fancy_header,
			left_margin = left_margin,
			with_rfe_aoe = with_rfe_aoe
		)

		if patient is None:
			_log.debug('no patient, cannot load patient related data')
			with_soap = False
			with_tests = False
			with_vaccinations = False
			with_docs = False

		if by_episode:
			lines.extend(self.format_by_episode (
				episodes = episodes,
				issues = issues,
				left_margin = left_margin,
				patient = patient,
				with_soap = with_soap,
				with_tests = with_tests,
				with_docs = with_docs,
				with_vaccinations = with_vaccinations,
				with_family_history = with_family_history
			))
		else:
			if with_soap:
				lines.append('')
				if patient.ID != self._payload[self._idx['pk_patient']]:
					msg = '<patient>.ID = %s but encounter %s belongs to patient %s' % (
						patient.ID,
						self._payload[self._idx['pk_encounter']],
						self._payload[self._idx['pk_patient']]
					)
					raise ValueError(msg)
				emr = patient.emr
				lines.extend(self.format_soap (
					episodes = episodes,
					left_margin = left_margin,
					soap_cats = None,		# meaning: all
					emr = emr,
					issues = issues
				))

	#		# family history
	#		if with_family_history:
	#			if episodes is not None:
	#				fhx = emr.get_family_history(episodes = episodes)
	#				if len(fhx) > 0:
	#					lines.append(u'')
	#					lines.append(_('Family History: %s') % len(fhx))
	#				for f in fhx:
	#					lines.append(f.format (
	#						left_margin = (left_margin + 1),
	#						include_episode = False,
	#						include_comment = True
	#					))
	#				del fhx

			# test results
			if with_tests:
				emr = patient.emr
				tests = emr.get_test_results_by_date (
					episodes = episodes,
					encounter = self._payload[self._idx['pk_encounter']]
				)
				if len(tests) > 0:
					lines.append('')
					lines.append(_('Measurements and Results:'))
				for t in tests:
					lines.append(t.format())
				del tests

			# vaccinations
			if with_vaccinations:
				emr = patient.emr
				vaccs = emr.get_vaccinations (
					episodes = episodes,
					encounters = [ self._payload[self._idx['pk_encounter']] ],
					order_by = 'date_given DESC, vaccine'
				)
				if len(vaccs) > 0:
					lines.append('')
					lines.append(_('Vaccinations:'))
				for vacc in vaccs:
					lines.extend(vacc.format (
						with_indications = True,
						with_comment = True,
						with_reaction = True,
						date_format = '%Y-%m-%d'
					))
				del vaccs

			# documents
			if with_docs:
				doc_folder = patient.get_document_folder()
				docs = doc_folder.get_documents (
					pk_episodes = episodes,
					encounter = self._payload[self._idx['pk_encounter']]
				)
				if len(docs) > 0:
					lines.append('')
					lines.append(_('Documents:'))
				for d in docs:
					lines.append(' ' + d.format(single_line = True))
				del docs

			# co-encountlets
			if with_co_encountlet_hints:
				if episodes is not None:
					other_epis = self.get_episodes(exclude = episodes)
					if len(other_epis) > 0:
						lines.append('')
						lines.append(_('%s other episodes touched upon during this encounter:') % len(other_epis))
					for epi in other_epis:
						lines.append(' %s%s%s%s' % (
							gmTools.u_left_double_angle_quote,
							epi['description'],
							gmTools.u_right_double_angle_quote,
							gmTools.coalesce(epi['health_issue'], '', ' (%s)')
						))

		if return_list:
			return lines

		eol_w_margin = '\n%s' % (' ' * left_margin)
		return '%s\n' % eol_w_margin.join(lines)

	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def _get_generic_codes_rfe(self):
		if len(self._payload[self._idx['pk_generic_codes_rfe']]) == 0:
			return []

		cmd = gmCoding._SQL_get_generic_linked_codes % 'pk_generic_code = ANY(%(pks)s)'
		args = {'pks': self._payload[self._idx['pk_generic_codes_rfe']]}
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)
		return [ gmCoding.cGenericLinkedCode(row = {'data': r, 'idx': idx, 'pk_field': 'pk_lnk_code2item'}) for r in rows ]

	def _set_generic_codes_rfe(self, pk_codes):
		queries = []
		# remove all codes
		if len(self._payload[self._idx['pk_generic_codes_rfe']]) > 0:
			queries.append ({
				'cmd': 'DELETE FROM clin.lnk_code2rfe WHERE fk_item = %(enc)s AND fk_generic_code = ANY(%(codes)s)',
				'args': {
					'enc': self._payload[self._idx['pk_encounter']],
					'codes': self._payload[self._idx['pk_generic_codes_rfe']]
				}
			})
		# add new codes
		for pk_code in pk_codes:
			queries.append ({
				'cmd': 'INSERT INTO clin.lnk_code2rfe (fk_item, fk_generic_code) VALUES (%(enc)s, %(pk_code)s)',
				'args': {
					'enc': self._payload[self._idx['pk_encounter']],
					'pk_code': pk_code
				}
			})
		if len(queries) == 0:
			return
		# run it all in one transaction
		rows, idx = gmPG2.run_rw_queries(queries = queries)
		self.refetch_payload()
		return

	generic_codes_rfe = property(_get_generic_codes_rfe, _set_generic_codes_rfe)
	#--------------------------------------------------------
	def _get_generic_codes_aoe(self):
		if len(self._payload[self._idx['pk_generic_codes_aoe']]) == 0:
			return []

		cmd = gmCoding._SQL_get_generic_linked_codes % 'pk_generic_code = ANY(%(pks)s)'
		args = {'pks': self._payload[self._idx['pk_generic_codes_aoe']]}
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)
		return [ gmCoding.cGenericLinkedCode(row = {'data': r, 'idx': idx, 'pk_field': 'pk_lnk_code2item'}) for r in rows ]

	def _set_generic_codes_aoe(self, pk_codes):
		queries = []
		# remove all codes
		if len(self._payload[self._idx['pk_generic_codes_aoe']]) > 0:
			queries.append ({
				'cmd': 'DELETE FROM clin.lnk_code2aoe WHERE fk_item = %(enc)s AND fk_generic_code = ANY(%(codes)s)',
				'args': {
					'enc': self._payload[self._idx['pk_encounter']],
					'codes': self._payload[self._idx['pk_generic_codes_aoe']]
				}
			})
		# add new codes
		for pk_code in pk_codes:
			queries.append ({
				'cmd': 'INSERT INTO clin.lnk_code2aoe (fk_item, fk_generic_code) VALUES (%(enc)s, %(pk_code)s)',
				'args': {
					'enc': self._payload[self._idx['pk_encounter']],
					'pk_code': pk_code
				}
			})
		if len(queries) == 0:
			return
		# run it all in one transaction
		rows, idx = gmPG2.run_rw_queries(queries = queries)
		self.refetch_payload()
		return

	generic_codes_aoe = property(_get_generic_codes_aoe, _set_generic_codes_aoe)
	#--------------------------------------------------------
	def _get_praxis_branch(self):
		if self._payload[self._idx['pk_org_unit']] is None:
			return None
		return gmPraxis.get_praxis_branch_by_org_unit(pk_org_unit = self._payload[self._idx['pk_org_unit']])

	praxis_branch = property(_get_praxis_branch)
	#--------------------------------------------------------
	def _get_org_unit(self):
		if self._payload[self._idx['pk_org_unit']] is None:
			return None
		return gmOrganization.cOrgUnit(aPK_obj = self._payload[self._idx['pk_org_unit']])

	org_unit = property(_get_org_unit)
	#--------------------------------------------------------
	def _get_formatted_revision_history(self):
		cmd = """SELECT
				'<N/A>'::TEXT as audit__action_applied,
				NULL AS audit__action_when,
				'<N/A>'::TEXT AS audit__action_by,
				pk_audit,
				row_version,
				modified_when,
				modified_by,
				pk, fk_patient, fk_type, fk_location, source_time_zone, reason_for_encounter, assessment_of_encounter, started, last_affirmed
			FROM clin.encounter
			WHERE pk = %(pk_encounter)s
		UNION ALL (
			SELECT
				audit_action as audit__action_applied,
				audit_when as audit__action_when,
				audit_by as audit__action_by,
				pk_audit,
				orig_version as row_version,
				orig_when as modified_when,
				orig_by as modified_by,
				pk, fk_patient, fk_type, fk_location, source_time_zone, reason_for_encounter, assessment_of_encounter, started, last_affirmed
			FROM audit.log_encounter
			WHERE pk = %(pk_encounter)s
		)
		ORDER BY row_version DESC
		"""
		args = {'pk_encounter': self._payload[self._idx['pk_encounter']]}
		title = _('Encounter: %s%s%s') % (
			gmTools.u_left_double_angle_quote,
			self._payload[self._idx['l10n_type']],
			gmTools.u_right_double_angle_quote
		)
		return '\n'.join(self._get_revision_history(cmd, args, title))

	formatted_revision_history = property(_get_formatted_revision_history)

#-----------------------------------------------------------
def create_encounter(fk_patient=None, enc_type=None):
	"""Creates a new encounter for a patient.

	fk_patient - patient PK
	enc_type - type of encounter
	"""
	if enc_type is None:
		enc_type = 'in surgery'
	# insert new encounter
	queries = []
	try:
		enc_type = int(enc_type)
		cmd = """
			INSERT INTO clin.encounter (fk_patient, fk_type, fk_location)
			VALUES (%(pat)s, %(typ)s, %(prax)s) RETURNING pk"""
	except ValueError:
		enc_type = enc_type
		cmd = """
			INSERT INTO clin.encounter (fk_patient, fk_location, fk_type)
			VALUES (
				%(pat)s,
				%(prax)s,
				coalesce (
					(select pk from clin.encounter_type where description = %(typ)s),
					-- pick the first available
					(select pk from clin.encounter_type limit 1)
				)
			) RETURNING pk"""
	praxis = gmPraxis.gmCurrentPraxisBranch()
	args = {'pat': fk_patient, 'typ': enc_type, 'prax': praxis['pk_org_unit']}
	queries.append({'cmd': cmd, 'args': args})
	rows, idx = gmPG2.run_rw_queries(queries = queries, return_data = True, get_col_idx = False)
	encounter = cEncounter(aPK_obj = rows[0]['pk'])

	return encounter

#------------------------------------------------------------
def lock_encounter(pk_encounter, exclusive=False, link_obj=None):
	"""Used to protect against deletion of active encounter from another client."""
	return gmPG2.lock_row(link_obj = link_obj, table = 'clin.encounter', pk = pk_encounter, exclusive = exclusive)

#------------------------------------------------------------
def unlock_encounter(pk_encounter, exclusive=False, link_obj=None):
	unlocked = gmPG2.unlock_row(link_obj = link_obj, table = 'clin.encounter', pk = pk_encounter, exclusive = exclusive)
	if not unlocked:
		_log.warning('cannot unlock encounter [#%s]', pk_encounter)
		call_stack = inspect.stack()
		call_stack.reverse()
		for idx in range(1, len(call_stack)):
			caller = call_stack[idx]
			_log.error('%s[%s] @ [%s] in [%s]', ' ' * idx, caller[3], caller[2], caller[1])
		del call_stack
	return unlocked

#-----------------------------------------------------------
def delete_encounter(pk_encounter):
	"""Deletes an encounter by PK.

	- attempts to obtain an exclusive lock which should
	  fail if the encounter is the active encounter in
	  this or any other client
	- catches DB exceptions which should mostly be related
	  to clinical data already having been attached to
	  the encounter thus making deletion fail
	"""
	conn = gmPG2.get_connection(readonly = False)
	if not lock_encounter(pk_encounter, exclusive = True, link_obj = conn):
		_log.debug('cannot lock encounter [%s] for deletion, it seems in use', pk_encounter)
		return False
	cmd = """DELETE FROM clin.encounter WHERE pk = %(enc)s"""
	args = {'enc': pk_encounter}
	try:
		rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])
	except gmPG2.PG_ERROR_EXCEPTION as exc:
		_log.exception('cannot delete encounter [%s]', pk_encounter)
		gmPG2.log_pg_exception_details(exc)
		unlock_encounter(pk_encounter, exclusive = True, link_obj = conn)
		return False
	unlock_encounter(pk_encounter, exclusive = True, link_obj = conn)
	return True

#-----------------------------------------------------------
# encounter types handling
#-----------------------------------------------------------
def update_encounter_type(description=None, l10n_description=None):

	rows, idx = gmPG2.run_rw_queries(
		queries = [{
		'cmd': "select i18n.upd_tx(%(desc)s, %(l10n_desc)s)",
		'args': {'desc': description, 'l10n_desc': l10n_description}
		}],
		return_data = True
	)

	success = rows[0][0]
	if not success:
		_log.warning('updating encounter type [%s] to [%s] failed', description, l10n_description)

	return {'description': description, 'l10n_description': l10n_description}
#-----------------------------------------------------------
def create_encounter_type(description=None, l10n_description=None):
	"""This will attempt to create a NEW encounter type."""

	# need a system name, so derive one if necessary
	if description is None:
		description = l10n_description

	args = {
		'desc': description,
		'l10n_desc': l10n_description
	}

	_log.debug('creating encounter type: %s, %s', description, l10n_description)

	# does it exist already ?
	cmd = "select description, _(description) from clin.encounter_type where description = %(desc)s"
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}])

	# yes
	if len(rows) > 0:
		# both system and l10n name are the same so all is well
		if (rows[0][0] == description) and (rows[0][1] == l10n_description):
			_log.info('encounter type [%s] already exists with the proper translation')
			return {'description': description, 'l10n_description': l10n_description}

		# or maybe there just wasn't a translation to
		# the current language for this type yet ?
		cmd = "select exists (select 1 from i18n.translations where orig = %(desc)s and lang = i18n.get_curr_lang())"
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}])

		# there was, so fail
		if rows[0][0]:
			_log.error('encounter type [%s] already exists but with another translation')
			return None

		# else set it
		cmd = "select i18n.upd_tx(%(desc)s, %(l10n_desc)s)"
		rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])
		return {'description': description, 'l10n_description': l10n_description}

	# no
	queries = [
		{'cmd': "insert into clin.encounter_type (description) values (%(desc)s)", 'args': args},
		{'cmd': "select i18n.upd_tx(%(desc)s, %(l10n_desc)s)", 'args': args}
	]
	rows, idx = gmPG2.run_rw_queries(queries = queries)

	return {'description': description, 'l10n_description': l10n_description}

#-----------------------------------------------------------
def get_most_commonly_used_encounter_type():
	cmd = """
		SELECT
			COUNT(*) AS type_count,
			fk_type
		FROM clin.encounter
		GROUP BY fk_type
		ORDER BY type_count DESC
		LIMIT 1
	"""
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd}], get_col_idx = False)
	if len(rows) == 0:
		return None
	return rows[0]['fk_type']

#-----------------------------------------------------------
def get_encounter_types():
	cmd = """
		SELECT
			_(description) AS l10n_description,
			description
		FROM
			clin.encounter_type
		ORDER BY
			l10n_description
	"""
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd}], get_col_idx = False)
	return rows

#-----------------------------------------------------------
def get_encounter_type(description=None):
	cmd = "SELECT * from clin.encounter_type where description = %s"
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': [description]}])
	return rows

#-----------------------------------------------------------
def delete_encounter_type(description=None):
	deleted = False
	cmd = "delete from clin.encounter_type where description = %(desc)s"
	args = {'desc': description}
	try:
		gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])
		deleted = True
	except gmPG2.dbapi.IntegrityError as e:
		if e.pgcode != gmPG2.PG_error_codes.FOREIGN_KEY_VIOLATION:
			raise

	return deleted

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
	def __init__(self, aPK_obj=None, try_potential_problems=False):
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
	def get_as_episode(self):
		"""
		Retrieve the cEpisode instance equivalent to this problem.
		The problem's type attribute must be 'episode'
		"""
		if self._payload[self._idx['type']] != 'episode':
			_log.error('cannot convert problem [%s] of type [%s] to episode' % (self._payload[self._idx['problem']], self._payload[self._idx['type']]))
			return None
		return cEpisode(aPK_obj = self._payload[self._idx['pk_episode']])
	#--------------------------------------------------------
	def get_as_health_issue(self):
		"""
		Retrieve the cHealthIssue instance equivalent to this problem.
		The problem's type attribute must be 'issue'
		"""
		if self._payload[self._idx['type']] != 'issue':
			_log.error('cannot convert problem [%s] of type [%s] to health issue' % (self._payload[self._idx['problem']], self._payload[self._idx['type']]))
			return None
		return cHealthIssue(aPK_obj = self._payload[self._idx['pk_health_issue']])
	#--------------------------------------------------------
	def get_visual_progress_notes(self, encounter_id=None):
		if self._payload[self._idx['type']] == 'issue':
			latest = cHealthIssue(aPK_obj = self._payload[self._idx['pk_health_issue']]).latest_episode
			if latest is None:
				return []

			pk_episode = latest['pk_episode']
		else:
			pk_episode = self._payload[self._idx['pk_episode']]
		doc_folder = gmDocuments.cDocumentFolder(aPKey = self._payload[self._idx['pk_patient']])
		return doc_folder.get_visual_progress_notes(episodes = [pk_episode])

	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	# doubles as 'diagnostic_certainty_description' getter:
	def get_diagnostic_certainty_description(self):
		return diagnostic_certainty_classification2str(self._payload[self._idx['diagnostic_certainty_classification']])

	diagnostic_certainty_description = property(get_diagnostic_certainty_description)
	#--------------------------------------------------------
	def _get_generic_codes(self):
		if self._payload[self._idx['type']] == 'issue':
			cmd = """
				SELECT * FROM clin.v_linked_codes WHERE
					item_table = 'clin.lnk_code2h_issue'::regclass
						AND
					pk_item = %(item)s
			"""
			args = {'item': self._payload[self._idx['pk_health_issue']]}
		else:
			cmd = """
				SELECT * FROM clin.v_linked_codes WHERE
					item_table = 'clin.lnk_code2episode'::regclass
						AND
					pk_item = %(item)s
			"""
			args = {'item': self._payload[self._idx['pk_episode']]}

		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)
		return [ gmCoding.cGenericLinkedCode(row = {'data': r, 'idx': idx, 'pk_field': 'pk_lnk_code2item'}) for r in rows ]

	generic_codes = property(_get_generic_codes)

#-----------------------------------------------------------
#-----------------------------------------------------------
#-----------------------------------------------------------
def reclass_problem(problem=None):
	"""Transform given problem into either episode or health issue instance.
	"""
	if isinstance(problem, (cEpisode, cHealthIssue)):
		return problem

	exc = TypeError('cannot reclass [%s] instance to either episode or health issue' % type(problem))

	if not isinstance(problem, cProblem):
		_log.debug('%s' % problem)
		raise exc

	if problem['type'] == 'episode':
		return cEpisode(aPK_obj = problem['pk_episode'])

	if problem['type'] == 'issue':
		return cHealthIssue(aPK_obj = problem['pk_health_issue'])

	raise exc

#============================================================
_SQL_get_hospital_stays = "select * from clin.v_hospital_stays where %s"

class cHospitalStay(gmBusinessDBObject.cBusinessDBObject):

	_cmd_fetch_payload = _SQL_get_hospital_stays % "pk_hospital_stay = %s"
	_cmds_store_payload = [
		"""UPDATE clin.hospital_stay SET
				clin_when = %(admission)s,
				discharge = %(discharge)s,
				fk_org_unit = %(pk_org_unit)s,
				narrative = gm.nullify_empty_string(%(comment)s),
				fk_episode = %(pk_episode)s,
				fk_encounter = %(pk_encounter)s
			WHERE
				pk = %(pk_hospital_stay)s
					AND
				xmin = %(xmin_hospital_stay)s
			RETURNING
				xmin AS xmin_hospital_stay
			"""
	]
	_updatable_fields = [
		'admission',
		'discharge',
		'pk_org_unit',
		'pk_episode',
		'pk_encounter',
		'comment'
	]

	#--------------------------------------------------------
	def format_maximum_information(self, patient=None):
		return self.format (
			include_procedures = True,
			include_docs = True
		).split('\n')

	#-------------------------------------------------------
	def format(self, left_margin=0, include_procedures=False, include_docs=False, include_episode=True):

		if self._payload[self._idx['discharge']] is not None:
			discharge = ' - %s' % gmDateTime.pydt_strftime(self._payload[self._idx['discharge']], '%Y %b %d')
		else:
			discharge = ''

		episode = ''
		if include_episode:
			episode = ': %s%s%s' % (
				gmTools.u_left_double_angle_quote,
				self._payload[self._idx['episode']],
				gmTools.u_right_double_angle_quote
			)

		lines = ['%s%s%s (%s@%s)%s' % (
			' ' * left_margin,
			gmDateTime.pydt_strftime(self._payload[self._idx['admission']], '%Y %b %d'),
			discharge,
			self._payload[self._idx['ward']],
			self._payload[self._idx['hospital']],
			episode
		)]

		if include_docs:
			for doc in self.documents:
				lines.append('%s%s: %s\n' % (
					' ' * left_margin,
					_('Document'),
					doc.format(single_line = True)
				))

		return '\n'.join(lines)

	#--------------------------------------------------------
	def _get_documents(self):
		return [ gmDocuments.cDocument(aPK_obj = pk_doc) for pk_doc in  self._payload[self._idx['pk_documents']] ]

	documents = property(_get_documents)

#-----------------------------------------------------------
def get_latest_patient_hospital_stay(patient=None):
	cmd = _SQL_get_hospital_stays % "pk_patient = %(pat)s ORDER BY admission DESC LIMIT 1"
	queries = [{
		# this assumes non-overarching stays
		#'cmd': u'SELECT * FROM clin.v_hospital_stays WHERE pk_patient = %(pat)s ORDER BY admission DESC LIMIT 1',
		'cmd': cmd,
		'args': {'pat': patient}
	}]
	rows, idx = gmPG2.run_ro_queries(queries = queries, get_col_idx = True)
	if len(rows) == 0:
		return None
	return cHospitalStay(row = {'idx': idx, 'data': rows[0], 'pk_field': 'pk_hospital_stay'})

#-----------------------------------------------------------
def get_patient_hospital_stays(patient=None, ongoing_only=False, return_pks=False):
	args = {'pat': patient}
	if ongoing_only:
		cmd = _SQL_get_hospital_stays % "pk_patient = %(pat)s AND discharge is NULL ORDER BY admission"
	else:
		cmd = _SQL_get_hospital_stays % "pk_patient = %(pat)s ORDER BY admission"

	queries = [{'cmd': cmd, 'args': args}]
	rows, idx = gmPG2.run_ro_queries(queries = queries, get_col_idx = True)
	if return_pks:
		return [ r['pk_hospital_stay'] for r in rows ]
	return [ cHospitalStay(row = {'idx': idx, 'data': r, 'pk_field': 'pk_hospital_stay'})  for r in rows ]

#-----------------------------------------------------------
def create_hospital_stay(encounter=None, episode=None, fk_org_unit=None):

	queries = [{
		 'cmd': 'INSERT INTO clin.hospital_stay (fk_encounter, fk_episode, fk_org_unit) VALUES (%(enc)s, %(epi)s, %(fk_org_unit)s) RETURNING pk',
		 'args': {'enc': encounter, 'epi': episode, 'fk_org_unit': fk_org_unit}
	}]
	rows, idx = gmPG2.run_rw_queries(queries = queries, return_data = True)

	return cHospitalStay(aPK_obj = rows[0][0])

#-----------------------------------------------------------
def delete_hospital_stay(stay=None):
	cmd = 'DELETE FROM clin.hospital_stay WHERE pk = %(pk)s'
	args = {'pk': stay}
	gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])
	return True

#============================================================
_SQL_get_procedures = "select * from clin.v_procedures where %s"

class cPerformedProcedure(gmBusinessDBObject.cBusinessDBObject):

	_cmd_fetch_payload = _SQL_get_procedures % "pk_procedure = %s"
	_cmds_store_payload = [
		"""UPDATE clin.procedure SET
				soap_cat = 'p',
				clin_when = %(clin_when)s,
				clin_end = %(clin_end)s,
				is_ongoing = %(is_ongoing)s,
				narrative = gm.nullify_empty_string(%(performed_procedure)s),
				fk_hospital_stay = %(pk_hospital_stay)s,
				fk_org_unit = (CASE
					WHEN %(pk_hospital_stay)s IS NULL THEN %(pk_org_unit)s
					ELSE NULL
				END)::integer,
				fk_episode = %(pk_episode)s,
				fk_encounter = %(pk_encounter)s,
				fk_doc = %(pk_doc)s,
				comment = gm.nullify_empty_string(%(comment)s)
			WHERE
				pk = %(pk_procedure)s AND
				xmin = %(xmin_procedure)s
			RETURNING xmin as xmin_procedure"""
	]
	_updatable_fields = [
		'clin_when',
		'clin_end',
		'is_ongoing',
		'performed_procedure',
		'pk_hospital_stay',
		'pk_org_unit',
		'pk_episode',
		'pk_encounter',
		'pk_doc',
		'comment'
	]
	#-------------------------------------------------------
	def __setitem__(self, attribute, value):

		if (attribute == 'pk_hospital_stay') and (value is not None):
			gmBusinessDBObject.cBusinessDBObject.__setitem__(self, 'pk_org_unit', None)

		if (attribute == 'pk_org_unit') and (value is not None):
			gmBusinessDBObject.cBusinessDBObject.__setitem__(self, 'pk_hospital_stay', None)

		gmBusinessDBObject.cBusinessDBObject.__setitem__(self, attribute, value)

	#--------------------------------------------------------
	def format_maximum_information(self, left_margin=0, patient=None):
		return self.format (
			left_margin = left_margin,
			include_episode = True,
			include_codes = True,
			include_address = True,
			include_comm = True,
			include_doc = True
		).split('\n')

	#-------------------------------------------------------
	def format(self, left_margin=0, include_episode=True, include_codes=False, include_address=False, include_comm=False, include_doc=False):

		if self._payload[self._idx['is_ongoing']]:
			end = _(' (ongoing)')
		else:
			end = self._payload[self._idx['clin_end']]
			if end is None:
				end = ''
			else:
				end = ' - %s' % gmDateTime.pydt_strftime(end, '%Y %b %d')

		line = '%s%s%s: %s%s [%s @ %s]' % (
			(' ' * left_margin),
			gmDateTime.pydt_strftime(self._payload[self._idx['clin_when']], '%Y %b %d'),
			end,
			self._payload[self._idx['performed_procedure']],
			gmTools.bool2str(include_episode, ' (%s)' % self._payload[self._idx['episode']], ''),
			self._payload[self._idx['unit']],
			self._payload[self._idx['organization']]
		)

		line += gmTools.coalesce(self._payload[self._idx['comment']], '', '\n' + (' ' * left_margin) + _('Comment: ') + '%s')

		if include_comm:
			for channel in self.org_unit.comm_channels:
				line += ('\n%(comm_type)s: %(url)s' % channel)

		if include_address:
			adr = self.org_unit.address
			if adr is not None:
				line += '\n'
				line += '\n'.join(adr.format(single_line = False, show_type = False))
				line += '\n'

		if include_doc:
			doc = self.doc
			if doc is not None:
				line += '\n'
				line += _('Document') + ': ' + doc.format(single_line = True)
				line += '\n'

		if include_codes:
			codes = self.generic_codes
			if len(codes) > 0:
				line += '\n'
			for c in codes:
				line += '%s  %s: %s (%s - %s)\n' % (
					(' ' * left_margin),
					c['code'],
					c['term'],
					c['name_short'],
					c['version']
				)
			del codes

		return line

	#--------------------------------------------------------
	def add_code(self, pk_code=None):
		"""<pk_code> must be a value from ref.coding_system_root.pk_coding_system (clin.lnk_code2item_root.fk_generic_code)"""
		cmd = "INSERT INTO clin.lnk_code2procedure (fk_item, fk_generic_code) values (%(issue)s, %(code)s)"
		args = {
			'issue': self._payload[self._idx['pk_procedure']],
			'code': pk_code
		}
		rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])
		return True

	#--------------------------------------------------------
	def remove_code(self, pk_code=None):
		"""<pk_code> must be a value from ref.coding_system_root.pk_coding_system (clin.lnk_code2item_root.fk_generic_code)"""
		cmd = "DELETE FROM clin.lnk_code2procedure WHERE fk_item = %(issue)s AND fk_generic_code = %(code)s"
		args = {
			'issue': self._payload[self._idx['pk_procedure']],
			'code': pk_code
		}
		rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])
		return True

	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def _get_stay(self):
		if self._payload[self._idx['pk_hospital_stay']] is None:
			return None
		return cHospitalStay(aPK_obj = self._payload[self._idx['pk_hospital_stay']])

	hospital_stay = property(_get_stay)

	#--------------------------------------------------------
	def _get_org_unit(self):
		return gmOrganization.cOrgUnit(self._payload[self._idx['pk_org_unit']])

	org_unit = property(_get_org_unit)

	#--------------------------------------------------------
	def _get_doc(self):
		if self._payload[self._idx['pk_doc']] is None:
			return None
		return gmDocuments.cDocument(aPK_obj = self._payload[self._idx['pk_doc']])

	doc = property(_get_doc)

	#--------------------------------------------------------
	def _get_generic_codes(self):
		if len(self._payload[self._idx['pk_generic_codes']]) == 0:
			return []

		cmd = gmCoding._SQL_get_generic_linked_codes % 'pk_generic_code = ANY(%(pks)s)'
		args = {'pks': self._payload[self._idx['pk_generic_codes']]}
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)
		return [ gmCoding.cGenericLinkedCode(row = {'data': r, 'idx': idx, 'pk_field': 'pk_lnk_code2item'}) for r in rows ]

	def _set_generic_codes(self, pk_codes):
		queries = []
		# remove all codes
		if len(self._payload[self._idx['pk_generic_codes']]) > 0:
			queries.append ({
				'cmd': 'DELETE FROM clin.lnk_code2procedure WHERE fk_item = %(proc)s AND fk_generic_code = ANY(%(codes)s)',
				'args': {
					'proc': self._payload[self._idx['pk_procedure']],
					'codes': self._payload[self._idx['pk_generic_codes']]
				}
			})
		# add new codes
		for pk_code in pk_codes:
			queries.append ({
				'cmd': 'INSERT INTO clin.lnk_code2procedure (fk_item, fk_generic_code) VALUES (%(proc)s, %(pk_code)s)',
				'args': {
					'proc': self._payload[self._idx['pk_procedure']],
					'pk_code': pk_code
				}
			})
		if len(queries) == 0:
			return
		# run it all in one transaction
		rows, idx = gmPG2.run_rw_queries(queries = queries)
		return

	generic_codes = property(_get_generic_codes, _set_generic_codes)

#-----------------------------------------------------------
def get_performed_procedures(patient=None, return_pks=False):
	queries = [{
		'cmd': 'SELECT * FROM clin.v_procedures WHERE pk_patient = %(pat)s ORDER BY clin_when',
		'args': {'pat': patient}
	}]
	rows, idx = gmPG2.run_ro_queries(queries = queries, get_col_idx = True)
	if return_pks:
		return [ r['pk_procedure'] for r in rows ]
	return [ cPerformedProcedure(row = {'idx': idx, 'data': r, 'pk_field': 'pk_procedure'})  for r in rows ]

#-----------------------------------------------------------
def get_procedures4document(pk_document=None, return_pks=False):
	args = {'pk_doc': pk_document}
	cmd = _SQL_get_procedures % 'pk_doc = %(pk_doc)s'
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)
	if return_pks:
		return [ r['pk_procedure'] for r in rows ]
	return [ cPerformedProcedure(row = {'idx': idx, 'data': r, 'pk_field': 'pk_procedure'})  for r in rows ]

#-----------------------------------------------------------
def get_latest_performed_procedure(patient=None):
	queries = [{
		'cmd': 'select * FROM clin.v_procedures WHERE pk_patient = %(pat)s ORDER BY clin_when DESC LIMIT 1',
		'args': {'pat': patient}
	}]
	rows, idx = gmPG2.run_ro_queries(queries = queries, get_col_idx = True)
	if len(rows) == 0:
		return None
	return cPerformedProcedure(row = {'idx': idx, 'data': rows[0], 'pk_field': 'pk_procedure'})

#-----------------------------------------------------------
def create_performed_procedure(encounter=None, episode=None, location=None, hospital_stay=None, procedure=None):

	queries = [{
		'cmd': """
			INSERT INTO clin.procedure (
				fk_encounter,
				fk_episode,
				soap_cat,
				fk_org_unit,
				fk_hospital_stay,
				narrative
			) VALUES (
				%(enc)s,
				%(epi)s,
				'p',
				%(loc)s,
				%(stay)s,
				gm.nullify_empty_string(%(proc)s)
			)
			RETURNING pk""",
		'args': {'enc': encounter, 'epi': episode, 'loc': location, 'stay': hospital_stay, 'proc': procedure}
	}]

	rows, idx = gmPG2.run_rw_queries(queries = queries, return_data = True)

	return cPerformedProcedure(aPK_obj = rows[0][0])

#-----------------------------------------------------------
def delete_performed_procedure(procedure=None):
	cmd = 'delete from clin.procedure where pk = %(pk)s'
	args = {'pk': procedure}
	gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])
	return True

#============================================================
def export_emr_structure(patient=None, filename=None):

	if filename is None:
		filename = gmTools.get_unique_filename(prefix = 'gm-emr_struct-%s-' % patient.subdir_name, suffix = '.txt')

	f = io.open(filename, 'w+', encoding = 'utf8')

	f.write('patient [%s]\n' % patient.description_gender)
	emr = patient.emr
	for issue in emr.health_issues:
		f.write('\n')
		f.write('\n')
		f.write('issue [%s] #%s\n' % (issue['description'], issue['pk_health_issue']))
		f.write(' is active     : %s\n' % issue['is_active'])
		f.write(' has open epi  : %s\n' % issue['has_open_episode'])
		f.write(' possible start: %s\n' % issue.possible_start_date)
		f.write(' safe start    : %s\n' % issue.safe_start_date)
		end = issue.clinical_end_date
		if end is None:
			f.write(' end           : active and/or open episode\n')
		else:
			f.write(' end           : %s\n' % end)
		f.write(' latest access : %s\n' % issue.latest_access_date)
		first = issue.first_episode
		if first is not None:
			first = first['description']
		f.write(' 1st episode   : %s\n' % first)
		last = issue.latest_episode
		if last is not None:
			last = last['description']
		f.write(' latest episode: %s\n' % last)
		epis = sorted(issue.get_episodes(), key = lambda e: e.best_guess_clinical_start_date)
		for epi in epis:
			f.write('\n')
			f.write(' episode [%s] #%s\n' % (epi['description'], epi['pk_episode']))
			f.write('  is open         : %s\n' % epi['episode_open'])
			f.write('  best guess start: %s\n' % epi.best_guess_clinical_start_date)
			f.write('  best guess end  : %s\n' % epi.best_guess_clinical_end_date)
			f.write('  latest access   : %s\n' % epi.latest_access_date)
			f.write('  start 1st enc   : %s\n' % epi['started_first'])
			f.write('  start last enc  : %s\n' % epi['started_last'])
			f.write('  end last enc    : %s\n' % epi['last_affirmed'])

	f.close()
	return filename

#============================================================
# tools
#------------------------------------------------------------
def check_fk_encounter_fk_episode_x_ref():

	aggregate_result = 0

	fks_linking2enc = gmPG2.get_foreign_keys2column(schema = 'clin', table = 'encounter', column = 'pk')
	tables_linking2enc = set([ r['referencing_table'] for r in fks_linking2enc ])

	fks_linking2epi = gmPG2.get_foreign_keys2column(schema = 'clin', table = 'episode', column = 'pk')
	tables_linking2epi = [ r['referencing_table'] for r in fks_linking2epi ]

	tables_linking2both = tables_linking2enc.intersection(tables_linking2epi)

	tables_linking2enc = {}
	for fk in fks_linking2enc:
		table = fk['referencing_table']
		tables_linking2enc[table] = fk

	tables_linking2epi = {}
	for fk in fks_linking2epi:
		table = fk['referencing_table']
		tables_linking2epi[table] = fk

	for t in tables_linking2both:

		table_file_name = 'x-check_enc_epi_xref-%s.log' % t
		table_file = io.open(table_file_name, 'w+', encoding = 'utf8')

		# get PK column
		args = {'table': t}
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': gmPG2.SQL_get_pk_col_def, 'args': args}])
		pk_col = rows[0][0]
		print("checking table:", t, '- pk col:', pk_col)
		print(' =>', table_file_name)
		table_file.write('table: %s\n' % t)
		table_file.write('PK col: %s\n' % pk_col)

		# get PKs
		cmd = 'select %s from %s' % (pk_col, t)
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd}])
		pks = [ r[0] for r in rows ]
		for pk in pks:
			args = {'pk': pk, 'tbl': t}
			enc_cmd = "select fk_patient from clin.encounter where pk = (select fk_encounter from %s where %s = %%(pk)s)" % (t, pk_col)
			epi_cmd = "select fk_patient from clin.encounter where pk = (select fk_encounter from clin.episode where pk = (select fk_episode from %s where %s = %%(pk)s))" % (t, pk_col)
			enc_rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': enc_cmd, 'args': args}])
			epi_rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': epi_cmd, 'args': args}])
			enc_pat = enc_rows[0][0]
			epi_pat = epi_rows[0][0]
			args['pat_enc'] = enc_pat
			args['pat_epi'] = epi_pat
			if epi_pat != enc_pat:
				print(' mismatch: row pk=%s, enc pat=%s, epi pat=%s' % (pk, enc_pat, epi_pat))
				aggregate_result = -2

				table_file.write('--------------------------------------------------------------------------------\n')
				table_file.write('mismatch on row with pk: %s\n' % pk)
				table_file.write('\n')

				table_file.write('journal entry:\n')
				cmd = 'SELECT * from clin.v_emr_journal where src_table = %(tbl)s AND src_pk = %(pk)s'
				rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}])
				if len(rows) > 0:
					table_file.write(gmTools.format_dict_like(rows[0], left_margin = 1, tabular = False, value_delimiters = None))
				table_file.write('\n\n')

				table_file.write('row data:\n')
				cmd = 'SELECT * from %s where %s = %%(pk)s' % (t, pk_col)
				rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}])
				table_file.write(gmTools.format_dict_like(rows[0], left_margin = 1, tabular = False, value_delimiters = None))
				table_file.write('\n\n')

				table_file.write('episode:\n')
				cmd = 'SELECT * from clin.v_pat_episodes WHERE pk_episode = (select fk_episode from %s where %s = %%(pk)s)' % (t, pk_col)
				rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}])
				table_file.write(gmTools.format_dict_like(rows[0], left_margin = 1, tabular = False, value_delimiters = None))
				table_file.write('\n\n')

				table_file.write('patient of episode:\n')
				cmd = 'SELECT * FROM dem.v_persons WHERE pk_identity = %(pat_epi)s'
				rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}])
				table_file.write(gmTools.format_dict_like(rows[0], left_margin = 1, tabular = False, value_delimiters = None))
				table_file.write('\n\n')

				table_file.write('encounter:\n')
				cmd = 'SELECT * from clin.v_pat_encounters WHERE pk_encounter = (select fk_encounter from %s where %s = %%(pk)s)' % (t, pk_col)
				rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}])
				table_file.write(gmTools.format_dict_like(rows[0], left_margin = 1, tabular = False, value_delimiters = None))
				table_file.write('\n\n')

				table_file.write('patient of encounter:\n')
				cmd = 'SELECT * FROM dem.v_persons WHERE pk_identity = %(pat_enc)s'
				rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}])
				table_file.write(gmTools.format_dict_like(rows[0], left_margin = 1, tabular = False, value_delimiters = None))
				table_file.write('\n')

		table_file.write('done\n')
		table_file.close()

	return aggregate_result

#------------------------------------------------------------
def export_patient_emr_structure():
	from Gnumed.business import gmPersonSearch
	gmPraxis.gmCurrentPraxisBranch(branch = gmPraxis.get_praxis_branches()[0])
	pat = gmPersonSearch.ask_for_patient()
	while pat is not None:
		print('patient:', pat.description_gender)
		fname = os.path.expanduser('~/gnumed/gm-emr_structure-%s.txt' % pat.subdir_name)
		print('exported into:', export_emr_structure(patient = pat, filename = fname))
		pat = gmPersonSearch.ask_for_patient()

	return 0

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
		epi = prob.get_as_episode()
		print('\nas episode:')
		if epi is not None:
			for field in epi.get_fields():
				print('   .%s : %s' % (field, epi[field]))

	#--------------------------------------------------------
	def test_health_issue():
		print("\nhealth issue test")
		print("-----------------")
		#h_issue = cHealthIssue(aPK_obj = 894)
		h_issue = cHealthIssue(aPK_obj = 1)
		print(h_issue)
#		print('possible start:', h_issue.possible_start_date)
#		print('safe start    :', h_issue.safe_start_date)
#		print('end date      :', h_issue.clinical_end_date)

		#print(h_issue.latest_access_date)
#		fields = h_issue.get_fields()
#		for field in fields:
#			print field, ':', h_issue[field]
#		print "has open episode:", h_issue.has_open_episode()
#		print "open episode:", h_issue.get_open_episode()
#		print "updateable:", h_issue.get_updatable_fields()
#		h_issue.close_expired_episode(ttl=7300)
#		h_issue = cHealthIssue(encounter = 1, name = u'post appendectomy/peritonitis')
#		print h_issue
#		print h_issue.format_as_journal()
		print(h_issue.formatted_revision_history)

	#--------------------------------------------------------	
	def test_episode():
		print("episode test")
		for i in range(1,15):
			print("------------")
			episode = cEpisode(aPK_obj = i)#322) #1674) #1354) #1461) #1299)

			print(episode['description'])
			print(' start:', episode.best_guess_clinical_start_date)
			print(' end  :', episode.best_guess_clinical_end_date)
			#print(' dura :', get_formatted_clinical_duration(pk_episode = i))
		return

		print(episode)
		fields = episode.get_fields()
		for field in fields:
			print(field, ':', episode[field])
		print("updatable:", episode.get_updatable_fields())
		input('ENTER to continue')

		desc = '1-%s' % episode['description']
		print("==> renaming to", desc)
		successful = episode.rename (
			description = desc
		)
		if not successful:
			print("error")
		else:
			print("success")
			for field in fields:
				print(field, ':', episode[field])

		print(episode.formatted_revision_history)

		input('ENTER to continue')

	#--------------------------------------------------------
	def test_encounter():
		print("\nencounter test")
		print("--------------")
		encounter = cEncounter(aPK_obj=1)
		print(encounter)
		fields = encounter.get_fields()
		for field in fields:
			print(field, ':', encounter[field])
		print("updatable:", encounter.get_updatable_fields())
		#print encounter.formatted_revision_history
		print(encounter.transfer_all_data_to_another_encounter(pk_target_encounter = 2))

	#--------------------------------------------------------
	def test_encounter2latex():
		encounter = cEncounter(aPK_obj=1)
		print(encounter)
		print("")
		print(encounter.format_latex())
	#--------------------------------------------------------
	def test_performed_procedure():
		procs = get_performed_procedures(patient = 12)
		for proc in procs:
			print(proc.format(left_margin=2))
	#--------------------------------------------------------
	def test_hospital_stay():
		stay = create_hospital_stay(encounter = 1, episode = 2, fk_org_unit = 1)
#		stay['hospital'] = u'Starfleet Galaxy General Hospital'
#		stay.save_payload()
		print(stay)
		for s in get_patient_hospital_stays(12):
			print(s)
		delete_hospital_stay(stay['pk_hospital_stay'])
		stay = create_hospital_stay(encounter = 1, episode = 4, fk_org_unit = 1)
	#--------------------------------------------------------
	def test_diagnostic_certainty_classification_map():
		tests = [None, 'A', 'B', 'C', 'D', 'E']

		for t in tests:
			print(type(t), t)
			print(type(diagnostic_certainty_classification2str(t)), diagnostic_certainty_classification2str(t))
	#--------------------------------------------------------
	def test_episode_codes():
		epi = cEpisode(aPK_obj = 2)
		print(epi)
		print(epi.generic_codes)
	#--------------------------------------------------------
	def test_episode_encounters():
		epi = cEpisode(aPK_obj = 1638)
		print(epi.format())

	#--------------------------------------------------------
	def test_export_emr_structure():
		export_patient_emr_structure()
		#praxis = gmPraxis.gmCurrentPraxisBranch(branch = gmPraxis.get_praxis_branches()[0])
		#from Gnumed.business import gmPerson
		## 12 / 20 / 138 / 58 / 20 / 5 / 14
		#pat = gmPerson.gmCurrentPatient(gmPerson.cPatient(aPK_obj = 138))
		#fname = os.path.expanduser(u'~/gnumed/emr_structure-%s.txt' % pat.subdir_name)
		#print export_emr_structure(patient = pat, filename = fname)

	#--------------------------------------------------------
	def test_cEpisodeMatchProvider():
		mp = cEpisodeMatchProvider()
		print(mp._find_matches('no patient'))

	#--------------------------------------------------------
	# run them
	#test_episode()
	#test_episode_encounters()
	#test_problem()
	#test_encounter()
	#test_health_issue()
	#test_hospital_stay()
	#test_performed_procedure()
	#test_diagnostic_certainty_classification_map()
	#test_encounter2latex()
	#test_episode_codes()

	#test_export_emr_structure()

	test_cEpisodeMatchProvider()

#============================================================
