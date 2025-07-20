# -*- coding: utf-8 -*-
"""GNUmed episode related business object.

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
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmDateTime
from Gnumed.pycommon import gmBusinessDBObject
from Gnumed.pycommon import gmExceptions
from Gnumed.pycommon import gmMatchProvider

from Gnumed.business import gmClinNarrative
from Gnumed.business import gmSoapDefs
from Gnumed.business import gmCoding
from Gnumed.business import gmPraxis

_log = logging.getLogger('gm.emr')

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

			rows = gmPG2.run_ro_queries (
				link_obj = link_obj,
				queries = [{'sql': cmd, 'args': args}],
			)

			if len(rows) == 0:
				raise gmExceptions.NoSuchBusinessObjectError('no episode for [%s:%s:%s:%s]' % (id_patient, name, health_issue, encounter))

			r = {'data': rows[0], 'pk_field': 'pk_episode'}
			gmBusinessDBObject.cBusinessDBObject.__init__(self, row=r)

		else:
			gmBusinessDBObject.cBusinessDBObject.__init__(self, aPK_obj=pk, row=row, link_obj = link_obj)

	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	@classmethod
	def from_problem(cls, problem) -> 'cEpisode':
		"""Initialize episode from episody-type problem."""
		if isinstance(problem, cEpisode):
			return problem

		assert problem['type'] == 'episode', 'cannot convert [%s] to episode' % problem
		return cls(aPK_obj = problem['pk_episode'])

	#--------------------------------------------------------
	def get_patient(self):
		return self._payload['pk_patient']

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
		old_description = self._payload['description']
		self._payload['description'] = description.strip()
		self._is_modified = True
		successful, data = self.save_payload()
		if not successful:
			_log.error('cannot rename episode [%s] to [%s]' % (self, description))
			self._payload['description'] = old_description
			return False
		return True

	#--------------------------------------------------------
	def add_code(self, pk_code=None):
		"""<pk_code> must be a value from ref.coding_system_root.pk_coding_system (clin.lnk_code2item_root.fk_generic_code)"""

		if pk_code in self._payload['pk_generic_codes']:
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
			'item': self._payload['pk_episode'],
			'code': pk_code
		}
		gmPG2.run_rw_queries(queries = [{'sql': cmd, 'args': args}])
		return

	#--------------------------------------------------------
	def remove_code(self, pk_code=None):
		"""<pk_code> must be a value from ref.coding_system_root.pk_coding_system (clin.lnk_code2item_root.fk_generic_code)"""
		cmd = "DELETE FROM clin.lnk_code2episode WHERE fk_item = %(item)s AND fk_generic_code = %(code)s"
		args = {
			'item': self._payload['pk_episode'],
			'code': pk_code
		}
		gmPG2.run_rw_queries(queries = [{'sql': cmd, 'args': args}])
		return True

	#--------------------------------------------------------
	def format_as_journal(self, left_margin=0, date_format='%Y %b %d, %a'):
		rows = gmClinNarrative.get_as_journal (
			episodes = [self.pk_obj],
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
				row['modified_when'].strftime(date_format),
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
			from Gnumed.business.gmPerson import gmCurrentPatient, cPatient
			if not gmCurrentPatient().connected:
				patient = cPatient(self._payload['pk_patient'])
			else:
				if self._payload['pk_patient'] == gmCurrentPatient().ID:
					patient = gmCurrentPatient()
				else:
					patient = cPatient(self._payload['pk_patient'])

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
	def __format_encounters(self, left_margin=0, emr=None):
		lines = []

		encs = emr.get_encounters(episodes = [self._payload['pk_episode']])
		if encs is None:
			return [_('Error retrieving encounters for this episode.')]

		if len(encs) == 0:
			#lines.append(_('There are no encounters for this issue.'))
			return []

		first_encounter = emr.get_first_encounter(episode_id = self._payload['pk_episode'])
		last_encounter = emr.get_last_encounter(episode_id = self._payload['pk_episode'])
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
		# spell out last encounter
		if last_encounter:
			lines.append('')
			lines.append(_('Progress notes in most recent encounter:'))
			lines.extend(last_encounter.format_soap (
				episodes = [ self._payload['pk_episode'] ],
				left_margin = left_margin,
				soap_cats = 'soapu',
				emr = emr
			))
		return lines

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
		if patient:
			if patient.ID != self._payload['pk_patient']:
				msg = '<patient>.ID = %s but episode %s belongs to patient %s' % (
					patient.ID,
					self._payload['pk_episode'],
					self._payload['pk_patient']
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
			self._payload['description'],
			gmTools.u_right_double_angle_quote,
			self._payload['pk_episode']
		))

		from Gnumed.business.gmEncounter import cEncounter
		enc = cEncounter(aPK_obj = self._payload['pk_encounter'])
		lines.append (' ' + _('Created during encounter: %s (%s - %s)   [#%s]') % (
			enc['l10n_type'],
			enc['started_original_tz'].strftime('%Y-%m-%d %H:%M'),
			enc['last_affirmed_original_tz'].strftime('%H:%M'),
			self._payload['pk_encounter']
		))

		if patient is not None:
			range_str, range_str_verb, duration_str = self.formatted_clinical_duration
			lines.append(_(' Duration: %s (%s)') % (duration_str, range_str_verb))

		from Gnumed.business.gmHealthIssue import diagnostic_certainty_classification2str
		lines.append(' ' + _('Status') + ': %s%s' % (
			gmTools.bool2subst(self._payload['episode_open'], _('active'), _('finished')),
			gmTools.coalesce (
				value2test = diagnostic_certainty_classification2str(self._payload['diagnostic_certainty_classification']),
				return_instead = '',
				template4value = ', %s',
				none_equivalents = [None, '']
			)
		))

		if with_health_issue:
			lines.append(' ' + _('Health issue') + ': %s' % gmTools.coalesce (
				self._payload['health_issue'],
				_('none associated')
			))

		if with_summary:
			if self._payload['summary'] is not None:
				lines.append(' %s:' % _('Synopsis'))
				lines.append(gmTools.wrap (
						text = self._payload['summary'],
						width = 60,
						initial_indent = '  ',
						subsequent_indent = '  '
					)
				)
		lines.append('')
		# encounters
		if with_encounters:
			lines.extend(self.__format_encounters(left_margin = left_margin, emr = emr))
		# documents
		if with_documents:
			doc_folder = patient.get_document_folder()
			docs = doc_folder.get_documents (
				pk_episodes = [ self._payload['pk_episode'] ]
			)
			if len(docs) > 0:
				lines.append('')
				lines.append(_('Documents: %s') % len(docs))
			for d in docs:
				lines.append(' ' + d.format(single_line = True))
			del docs

		# hospitalizations
		if with_hospital_stays:
			stays = emr.get_hospital_stays(episodes = [ self._payload['pk_episode'] ])
			if len(stays) > 0:
				lines.append('')
				lines.append(_('Hospitalizations: %s') % len(stays))
			for s in stays:
				lines.append(s.format(left_margin = (left_margin + 1)))
			del stays

		# procedures
		if with_procedures:
			procs = emr.get_performed_procedures(episodes = [ self._payload['pk_episode'] ])
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
			fhx = emr.get_family_history(episodes = [ self._payload['pk_episode'] ])
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
			tests = emr.get_test_results_by_date(episodes = [ self._payload['pk_episode'] ])
			if len(tests) > 0:
				lines.append('')
				lines.append(_('Measurements and Results:'))
			for t in tests:
				lines.append(' ' + t.format_concisely(date_format = '%Y %b %d', with_notes = True))
			del tests

		# vaccinations
		if with_vaccinations:
			vaccs = emr.get_vaccinations (
				episodes = [ self._payload['pk_episode'] ],
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
		rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': {'pk': self.pk_obj}}])
		return rows[0][0]

	latest_access_date = property(_get_latest_access_date)

	#--------------------------------------------------------
	def _get_diagnostic_certainty_description(self):
		from Gnumed.business.gmHealthIssue import diagnostic_certainty_classification2str
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
				'sql': 'DELETE FROM clin.lnk_code2episode WHERE fk_item = %(epi)s AND fk_generic_code = ANY(%(codes)s)',
				'args': {
					'epi': self._payload['pk_episode'],
					'codes': self._payload['pk_generic_codes']
				}
			})
		# add new codes
		for pk_code in pk_codes:
			queries.append ({
				'sql': 'INSERT INTO clin.lnk_code2episode (fk_item, fk_generic_code) VALUES (%(epi)s, %(pk_code)s)',
				'args': {
					'epi': self._payload['pk_episode'],
					'pk_code': pk_code
				}
			})
		if len(queries) == 0:
			return
		# run it all in one transaction
		gmPG2.run_rw_queries(queries = queries)
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
			'pat': self._payload['pk_patient'],
			'epi': self._payload['pk_episode']
		}
		rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
		return rows[0][0]

	has_narrative = property(_get_has_narrative)

	#--------------------------------------------------------
	def _get_health_issue(self):
		if self._payload['pk_health_issue'] is None:
			return None

		from Gnumed.business.gmHealthIssue import cHealthIssue
		return cHealthIssue(self._payload['pk_health_issue'])

	health_issue = property(_get_health_issue)

#============================================================
def create_episode(pk_health_issue:int=None, episode_name:str=None, is_open:bool=False, allow_dupes:bool=False, encounter:int=None, link_obj=None):
	"""Creates a new episode for a given patient's health issue.

	pk_health_issue - given health issue PK
	episode_name - name of episode
	is_open - whether a *new* episode is to be open (don't tinker with existing ones)
	"""
	if not allow_dupes:
		try:
			return cEpisode(name = episode_name, health_issue = pk_health_issue, encounter = encounter, link_obj = link_obj)

		except gmExceptions.ConstructorError:
			pass
	queries = []
	SQL = "INSERT INTO clin.episode (fk_health_issue, description, is_open, fk_encounter) VALUES (%(pk_hi)s, %(epi_name)s, %(open)s::boolean, %(pk_enc)s)"
	args = {
		'pk_hi': pk_health_issue,
		'epi_name': episode_name,
		'open': is_open,
		'pk_enc': encounter
	}
	queries.append({'sql': SQL, 'args': args})
	queries.append({'sql': cEpisode._cmd_fetch_payload % "currval('clin.episode_pk_seq')"})
	rows = gmPG2.run_rw_queries(link_obj = link_obj, queries = queries, return_data = True)
	return cEpisode(row = {'data': rows[0], 'pk_field': 'pk_episode'})

#-----------------------------------------------------------
def delete_episode(episode=None):
	if isinstance(episode, cEpisode):
		pk = episode['pk_episode']
	else:
		pk = int(episode)

	cmd = 'DELETE FROM clin.episode WHERE pk = %(pk)s'
	try:
		gmPG2.run_rw_queries(queries = [{'sql': cmd, 'args': {'pk': pk}}])
	except gmPG2.dbapi.IntegrityError:
		# should be parsing pgcode/and or error message
		_log.exception('cannot delete episode, it is in use')
		return False

	return True

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
		'sql': _SQL_best_guess_clinical_start_date_for_episode,
		'args': {'pk': pk_episode}
	}
	rows = gmPG2.run_ro_queries(queries = [query])
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
		'sql': _SQL_best_guess_clinical_end_date_for_episode,
		'args': {'pk': pk_episode}
	}
	rows = gmPG2.run_ro_queries(queries = [query])
	return rows[0][0]

#-----------------------------------------------------------
def format_clinical_duration_of_episode(start=None, end=None):
	assert (start is not None), '<start> must not be None'

	if end is None:
		start_end_str = '%s-%s' % (
			start.strftime("%b'%y"),
			gmTools.u_ellipsis
		)
		start_end_str_long = '%s - %s' % (
			start.strftime('%b %d %Y'),
			gmTools.u_ellipsis
		)
		duration_str = _('%s so far') % gmDateTime.format_interval_medically(gmDateTime.pydt_now_here() - start)
		return (start_end_str, start_end_str_long, duration_str)

	duration_str = gmDateTime.format_interval_medically(end - start)
	# year different:
	if end.year != start.year:
		start_end_str = '%s-%s' % (
			start.strftime("%b'%y"),
			end.strftime("%b'%y")
		)
		start_end_str_long = '%s - %s' % (
			start.strftime('%b %d %Y'),
			end.strftime('%b %d %Y')
		)
		return (start_end_str, start_end_str_long, duration_str)
	# same year:
	if end.month != start.month:
		start_end_str = '%s-%s' % (
			start.strftime('%b'),
			end.strftime("%b'%y")
		)
		start_end_str_long = '%s - %s' % (
			start.strftime('%b %d'),
			end.strftime('%b %d %Y')
		)
		return (start_end_str, start_end_str_long, duration_str)

	# same year and same month
	start_end_str = start.strftime("%b'%y")
	start_end_str_long = start.strftime('%b %d %Y')
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
	def test_episode():
		print("episode test")
		gmPraxis.gmCurrentPraxisBranch.from_first_branch()
		for i in range(1,15):
			print("------------")
			episode = cEpisode(aPK_obj = i)#322) #1674) #1354) #1461) #1299)
			#print(episode['description'])
			#print(' start:', episode.best_guess_clinical_start_date)
			#print(' end  :', episode.best_guess_clinical_end_date)
			#print(' dura :', get_formatted_clinical_duration(pk_episode = i))
			for line in episode.format_maximum_information():
				print(line)
			input('ENTER to continue')
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
	def test_episode_codes():
		epi = cEpisode(aPK_obj = 2)
		print(epi)
		print(epi.generic_codes)
	#--------------------------------------------------------
	def test_episode_encounters():
		epi = cEpisode(aPK_obj = 1638)
		print(epi.format())

	#--------------------------------------------------------
	def test_cEpisodeMatchProvider():
		mp = cEpisodeMatchProvider()
		print(mp._find_matches('no patient'))

	#--------------------------------------------------------
	gmPG2.request_login_params(setup_pool = True)

	test_episode()
	#test_episode_encounters()
	#test_episode_codes()
