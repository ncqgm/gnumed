# -*- coding: utf-8 -*-
"""GNUmed health issue related business object.

license: GPL v2 or later
"""
#============================================================
__author__ = "<karsten.hilbert@gmx.net>"

import sys
import datetime
import logging


if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x
else:
	try:
		_
	except NameError:
		from Gnumed.pycommon import gmI18N
		gmI18N.activate_locale()
		gmI18N.install_domain()
from Gnumed.pycommon import gmPG2
from Gnumed.pycommon import gmI18N
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmDateTime
from Gnumed.pycommon import gmBusinessDBObject
from Gnumed.pycommon import gmExceptions

from Gnumed.business import gmClinNarrative
from Gnumed.business import gmSoapDefs
from Gnumed.business import gmCoding
from Gnumed.business import gmExternalCare
from Gnumed.business import gmEpisode


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

		queries = [{'sql': cmd, 'args': {'enc': encounter, 'desc': name, 'pat': patient}}]
		rows = gmPG2.run_ro_queries(queries = queries)

		if len(rows) == 0:
			raise gmExceptions.NoSuchBusinessObjectError('no health issue for [enc:%s::desc:%s::pat:%s]' % (encounter, name, patient))

		pk = rows[0][0]
		r = {'data': rows[0], 'pk_field': 'pk_health_issue'}

		gmBusinessDBObject.cBusinessDBObject.__init__(self, row=r)

	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	@classmethod
	def from_problem(cls, problem) -> 'cHealthIssue':
		"""Initialize health issue from issue-type problem."""
		if isinstance(problem, cHealthIssue):
			return problem

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
		old_description = self._payload['description']
		self._payload['description'] = description.strip()
		self._is_modified = True
		successful, data = self.save_payload()
		if not successful:
			_log.error('cannot rename health issue [%s] with [%s]' % (self, description))
			self._payload['description'] = old_description
			return False

		return True

	#--------------------------------------------------------
	def get_episodes(self) -> list[gmEpisode.cEpisode]:
		"""The episodes linked to this health issue."""
		SQL = 'SELECT * FROM clin.v_pat_episodes WHERE pk_health_issue = %(pk)s'
		args = {'pk': self.pk_obj}
		rows = gmPG2.run_ro_queries(queries = [{'sql': SQL, 'args': args}])
		return [ gmEpisode.cEpisode(row = {'data': r, 'pk_field': 'pk_episode'})  for r in rows ]

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
	def get_open_episode(self) -> gmEpisode.cEpisode:
		SQL = "select pk FROM clin.episode WHERE fk_health_issue = %(pk_issue)s AND is_open IS True LIMIT 1"
		args = {'pk_issue': self.pk_obj}
		rows = gmPG2.run_ro_queries(queries = [{'sql': SQL, 'args': args}])
		if rows:
			return gmEpisode.cEpisode(aPK_obj = rows[0][0])

		return None

	open_episode = property(get_open_episode)

	#--------------------------------------------------------
	def age_noted_human_readable(self):
		if self._payload['age_noted'] is None:
			return '<???>'

		# since we've already got an interval we are bound to use it,
		# further transformation will only introduce more errors,
		# later we can improve this deeper inside
		return gmDateTime.format_interval_medically(self._payload['age_noted'])

	#--------------------------------------------------------
	def add_code(self, pk_code=None):
		"""<pk_code> must be a value from ref.coding_system_root.pk_coding_system (clin.lnk_code2item_root.fk_generic_code)"""
		cmd = "INSERT INTO clin.lnk_code2h_issue (fk_item, fk_generic_code) values (%(item)s, %(code)s)"
		args = {
			'item': self._payload['pk_health_issue'],
			'code': pk_code
		}
		gmPG2.run_rw_queries(queries = [{'sql': cmd, 'args': args}])
		return True

	#--------------------------------------------------------
	def remove_code(self, pk_code=None):
		"""<pk_code> must be a value from ref.coding_system_root.pk_coding_system (clin.lnk_code2item_root.fk_generic_code)"""
		cmd = "DELETE FROM clin.lnk_code2h_issue WHERE fk_item = %(item)s AND fk_generic_code = %(code)s"
		args = {
			'item': self._payload['pk_health_issue'],
			'code': pk_code
		}
		gmPG2.run_rw_queries(queries = [{'sql': cmd, 'args': args}])
		return True

	#--------------------------------------------------------
	def format_as_journal(self, left_margin=0, date_format='%Y %b %d, %a'):
		rows = gmClinNarrative.get_as_journal (
			issues = [self.pk_obj],
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

			top_row = '%s%s %s (%s) %s' % (
				gmTools.u_box_top_left_arc,
				gmTools.u_box_horiz_single,
				gmSoapDefs.soap_cat2l10n_str[row['real_soap_cat']],
				row['clin_when'].strftime(date_format),
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
				row['modified_when'].strftime(date_format),
				gmTools.u_box_horiz_heavy_light
			)

			lines.append(top_row)
			lines.append(soap)
			lines.append(bottom_row)

		eol_w_margin = '\n%s' % left_margin
		return left_margin + eol_w_margin.join(lines) + '\n'

	#--------------------------------------------------------
	def __format_episodes_for_clinical_data(self, emr) -> list:
		epis = self.get_episodes()
		if epis is None:
			return [_('Error retrieving episodes for this health issue.')]

		if len(epis) == 0:
			return [_('There are no episodes for this health issue.')]

		line = _('Episodes: %s (most recent: %s%s%s)') % (
			len(epis),
			gmTools.u_left_double_angle_quote,
			emr.get_most_recent_episode(issue = self._payload['pk_health_issue'])['description'],
			gmTools.u_right_double_angle_quote
		)
		lines = [line]
		for epi in epis:
			lines.append(' \u00BB%s\u00AB (%s)' % (
				epi['description'],
				gmTools.bool2subst(epi['episode_open'], _('ongoing'), _('closed'))
			))
		lines.append('')
		return lines

	#--------------------------------------------------------
	def __format_encounters_for_clinical_data(self, emr) -> list:
		first_encounter = emr.get_first_encounter(issue_id = self._payload['pk_health_issue'])
		if not first_encounter:
			return [_('No encounters found for this health issue.')]

		last_encounter = emr.get_last_encounter(issue_id = self._payload['pk_health_issue'])
		encs = emr.get_encounters(issues = [self._payload['pk_health_issue']])
		lines = []
		line = _('Encounters: %s (%s - %s):') % (
			len(encs),
			first_encounter['started_original_tz'].strftime('%m/%Y'),
			last_encounter['last_affirmed_original_tz'].strftime('%m/%Y')
		)
		lines.append(line)
		line = _(' Most recent: %s - %s') % (
			last_encounter['started_original_tz'].strftime('%Y-%m-%d %H:%M'),
			last_encounter['last_affirmed_original_tz'].strftime('%H:%M')
		)
		lines.append(line)
		return lines

	#--------------------------------------------------------
	def __format_clinical_data(self, left_margin=0, patient=None,
		with_episodes=True,
		with_encounters=True,
		with_medications=True,
		with_hospital_stays=True,
		with_procedures=True,
		with_family_history=True,
		with_documents=True,
		with_tests=True,
		with_vaccinations=True
	):
		if not patient:
			return []

		if patient.ID != self._payload['pk_patient']:
			msg = '<patient>.ID = %s but health issue %s belongs to patient %s' % (
				patient.ID,
				self._payload['pk_health_issue'],
				self._payload['pk_patient']
			)
			raise ValueError(msg)

		emr = patient.emr
		lines = []
		# episodes
		if with_episodes:
			lines.extend(self.__format_episodes_for_clinical_data(emr))
		# encounters
		if with_encounters:
			lines.extend(self.__format_encounters_for_clinical_data(emr))

		# medications
		if with_medications:
			meds = emr.get_current_medications (
				issues = [ self._payload['pk_health_issue'] ],
				order_by = 'discontinued DESC NULLS FIRST, started, substance'
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
				issues = [ self._payload['pk_health_issue'] ]
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
				issues = [ self._payload['pk_health_issue'] ]
			)
			if len(procs) > 0:
				lines.append('')
				lines.append(_('Procedures performed: %s') % len(procs))
			for p in procs:
				lines.append(p.format(left_margin = (left_margin + 1)))
			del procs

		# family history
		if with_family_history:
			fhx = emr.get_family_history(issues = [ self._payload['pk_health_issue'] ])
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
		if epis:
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
		return lines

	#--------------------------------------------------------
	def format(self, left_margin=0, patient=None,
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
			self._payload['description'],
			'\u00AB',
			gmTools.coalesce (
				value2test = self.laterality_description,
				return_instead = '',
				template4value = ' (%s)',
				none_equivalents = [None, '', '?']
			),
			self._payload['pk_health_issue']
		))

		if self._payload['is_confidential']:
			lines.append('')
			lines.append(_(' ***** CONFIDENTIAL *****'))
			lines.append('')

		if self._payload['is_cause_of_death']:
			lines.append('')
			lines.append(_(' contributed to death of patient'))
			lines.append('')

		from Gnumed.business.gmEncounter import cEncounter
		enc = cEncounter(aPK_obj = self._payload['pk_encounter'])
		lines.append (_(' Created during encounter: %s (%s - %s)   [#%s]') % (
			enc['l10n_type'],
			enc['started_original_tz'].strftime('%Y-%m-%d %H:%M'),
			enc['last_affirmed_original_tz'].strftime('%H:%M'),
			self._payload['pk_encounter']
		))

		if self._payload['age_noted'] is not None:
			lines.append(_(' Noted at age: %s') % self.age_noted_human_readable())

		lines.append(' ' + _('Status') + ': %s, %s%s' % (
			gmTools.bool2subst(self._payload['is_active'], _('active'), _('inactive')),
			gmTools.bool2subst(self._payload['clinically_relevant'], _('clinically relevant'), _('not clinically relevant')),
			gmTools.coalesce (
				value2test = diagnostic_certainty_classification2str(self._payload['diagnostic_certainty_classification']),
				return_instead = '',
				template4value = ', %s',
				none_equivalents = [None, '']
			)
		))

		if with_summary:
			if self._payload['summary'] is not None:
				lines.append(' %s:' % _('Synopsis'))
				lines.append(gmTools.wrap (
					text = self._payload['summary'],
					width = 60,
					initial_indent = '  ',
					subsequent_indent = '  '
				))
		lines.append('')
		# patient/emr dependant
		lines.extend(self.__format_clinical_data (
			left_margin,
			patient,
			with_episodes = with_episodes,
			with_encounters = with_encounters,
			with_medications = with_medications,
			with_hospital_stays = with_hospital_stays,
			with_procedures = with_procedures,
			with_family_history = with_family_history,
			with_documents = with_documents,
			with_tests = with_tests,
			with_vaccinations = with_vaccinations
		))
		if with_external_care:
			care = self._get_external_care(order_by = 'organization, unit, provider')
			if care:
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
	def _get_encounter(self):
		from Gnumed.business.gmEncounter import cEncounter
		return cEncounter(aPK_obj = self._payload['pk_encounter'])

	encounter = property(_get_encounter)

	#--------------------------------------------------------
	def _get_external_care(self, order_by=None):
		return gmExternalCare.get_external_care_items(pk_health_issue = self.pk_obj, order_by = order_by)

	external_care = property(_get_external_care)

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
		rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
		if len(rows) == 0:
			return None

		return gmEpisode.cEpisode(aPK_obj = rows[0]['pk_episode'])

	first_episode = property(_get_first_episode)

	#--------------------------------------------------------
	def _get_latest_episode(self):

		# explicit always wins:
		if self._payload['has_open_episode']:
			return self.open_episode

		args = {'pk_issue': self.pk_obj}

		# cheap query first: any episodes at all ?
		cmd = "SELECT 1 FROM clin.episode WHERE fk_health_issue = %(pk_issue)s"
		rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
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
		rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
		if len(rows) == 0:
			# there were no episodes for this issue
			return None

		return gmEpisode.cEpisode(aPK_obj = rows[0]['pk_episode'])

	latest_episode = property(_get_latest_episode)

	#--------------------------------------------------------
	# Steffi suggested we divide into safe and assumed (= possible) start dates
	def _get_safe_start_date(self):
		"""This returns the date when we can assume to safely KNOW
		   the health issue existed (because the provider said so)."""

		args = {
			'enc': self._payload['pk_encounter'],
			'pk': self._payload['pk_health_issue']
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
		rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
		start = rows[0][0]
		# leads to a loop:
		#end = self.clinical_end_date
		#if start > end:
		#	return end
		return start

	safe_start_date = property(_get_safe_start_date)

	#--------------------------------------------------------
	def _get_possible_start_date(self):
		args = {'pk': self._payload['pk_health_issue']}
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

		rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
		return rows[0][0]

	possible_start_date = property(_get_possible_start_date)

	#--------------------------------------------------------
	def _get_clinical_end_date(self):
		if self._payload['is_active']:
			return None
		if self._payload['has_open_episode']:
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
		rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': {'pk': self.pk_obj}}])
		return rows[0][0]

	latest_access_date = property(_get_latest_access_date)

	#--------------------------------------------------------
	def _get_laterality_description(self):
		try:
			return laterality2str[self._payload['laterality']]
		except KeyError:
			return '<?>'

	laterality_description = property(_get_laterality_description)

	#--------------------------------------------------------
	def _get_diagnostic_certainty_description(self):
		return diagnostic_certainty_classification2str(self._payload['diagnostic_certainty_classification'])

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
			self._payload['description'],
			gmTools.u_right_double_angle_quote
		)
		return '\n'.join(self._get_revision_history(cmd, args, title))

	formatted_revision_history = property(_get_formatted_revision_history)

	#--------------------------------------------------------
	def _get_generic_codes(self):
		if len(self._payload['pk_generic_codes']) == 0:
			return []

		cmd = gmCoding._SQL_get_generic_linked_codes % 'pk_generic_code = ANY(%(pks)s)'
		args = {'pks': self._payload['pk_generic_codes']}
		rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
		return [ gmCoding.cGenericLinkedCode(row = {'data': r, 'pk_field': 'pk_lnk_code2item'}) for r in rows ]

	def _set_generic_codes(self, pk_codes):
		queries = []
		# remove all codes
		if len(self._payload['pk_generic_codes']) > 0:
			queries.append ({
				'sql': 'DELETE FROM clin.lnk_code2h_issue WHERE fk_item = %(issue)s AND fk_generic_code = ANY(%(codes)s)',
				'args': {
					'issue': self._payload['pk_health_issue'],
					'codes': self._payload['pk_generic_codes']
				}
			})
		# add new codes
		for pk_code in pk_codes:
			queries.append ({
				'sql': 'INSERT INTO clin.lnk_code2h_issue (fk_item, fk_generic_code) VALUES (%(issue)s, %(pk_code)s)',
				'args': {
					'issue': self._payload['pk_health_issue'],
					'pk_code': pk_code
				}
			})
		if len(queries) == 0:
			return
		# run it all in one transaction
		gmPG2.run_rw_queries(queries = queries)
		return

	generic_codes = property(_get_generic_codes, _set_generic_codes)

#============================================================
def create_health_issue(description=None, encounter=None, patient=None, link_obj=None):
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
	queries.append({'sql': cmd, 'args': {'desc': description, 'enc': encounter}})
	cmd = "select currval('clin.health_issue_pk_seq')"
	queries.append({'sql': cmd})
	rows = gmPG2.run_rw_queries(queries = queries, return_data = True, link_obj = link_obj)
	h_issue = cHealthIssue(aPK_obj = rows[0][0])
	return h_issue

#-----------------------------------------------------------
def delete_health_issue(health_issue=None):
	if isinstance(health_issue, cHealthIssue):
		args = {'pk': health_issue['pk_health_issue']}
	else:
		args = {'pk': int(health_issue)}
	try:
		gmPG2.run_rw_queries(queries = [{'sql': 'DELETE FROM clin.health_issue WHERE pk = %(pk)s', 'args': args}])
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

#============================================================
# main - unit testing
#------------------------------------------------------------
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	del _
	from Gnumed.pycommon import gmI18N
	gmI18N.activate_locale()
	gmI18N.install_domain('gnumed')

	#--------------------------------------------------------
	# define tests
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
		#print(h_issue.formatted_revision_history)
		print(h_issue.format())

	#--------------------------------------------------------
	def test_diagnostic_certainty_classification_map():
		tests = [None, 'A', 'B', 'C', 'D', 'E']

		for t in tests:
			print(type(t), t)
			print(type(diagnostic_certainty_classification2str(t)), diagnostic_certainty_classification2str(t))

	#--------------------------------------------------------
	gmPG2.request_login_params(setup_pool = True)

	#test_health_issue()
	test_diagnostic_certainty_classification_map()
