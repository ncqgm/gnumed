# -*- coding: utf8 -*-
"""GNUmed health related business object.

license: GPL
"""
#============================================================
__version__ = "$Revision: 1.157 $"
__author__ = "Carlos Moro <cfmoro1976@yahoo.es>, <karsten.hilbert@gmx.net>"

import types, sys, string, datetime, logging, time


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmPG2
from Gnumed.pycommon import gmI18N
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmDateTime
from Gnumed.pycommon import gmBusinessDBObject
from Gnumed.pycommon import gmNull
from Gnumed.pycommon import gmExceptions

from Gnumed.business import gmClinNarrative
from Gnumed.business import gmCoding


_log = logging.getLogger('gm.emr')
_log.info(__version__)

try: _
except NameError: _ = lambda x:x
#============================================================
# diagnostic certainty classification
#============================================================
__diagnostic_certainty_classification_map = None

def diagnostic_certainty_classification2str(classification):

	global __diagnostic_certainty_classification_map

	if __diagnostic_certainty_classification_map is None:
		__diagnostic_certainty_classification_map = {
			None: u'',
			u'A': _(u'A: Sign'),
			u'B': _(u'B: Cluster of signs'),
			u'C': _(u'C: Syndromic diagnosis'),
			u'D': _(u'D: Scientific diagnosis')
		}

	try:
		return __diagnostic_certainty_classification_map[classification]
	except KeyError:
		return _(u'<%s>: unknown diagnostic certainty classification') % classification
#============================================================
# Health Issues API
#============================================================
laterality2str = {
	None: u'?',
	u'na': u'',
	u'sd': _('bilateral'),
	u'ds': _('bilateral'),
	u's': _('left'),
	u'd': _('right')
}

#============================================================
class cHealthIssue(gmBusinessDBObject.cBusinessDBObject):
	"""Represents one health issue."""

	_cmd_fetch_payload = u"select *, xmin_health_issue from clin.v_health_issues where pk_health_issue=%s"
	_cmds_store_payload = [
		u"""update clin.health_issue set
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
			where
				pk = %(pk_health_issue)s and
				xmin = %(xmin_health_issue)s""",
		u"select xmin as xmin_health_issue from clin.health_issue where pk = %(pk_health_issue)s"
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
			cmd = u"""select *, xmin_health_issue from clin.v_health_issues
					where
						description = %(desc)s
							and
						pk_patient = (select fk_patient from clin.encounter where pk = %(enc)s)"""
		else:
			cmd = u"""select *, xmin_health_issue from clin.v_health_issues
					where
						description = %(desc)s
							and
						pk_patient = %(pat)s"""

		queries = [{'cmd': cmd, 'args': {'enc': encounter, 'desc': name, 'pat': patient}}]
		rows, idx = gmPG2.run_ro_queries(queries = queries,	get_col_idx = True)

		if len(rows) == 0:
			raise gmExceptions.NoSuchBusinessObjectError, 'no health issue for [enc:%s::desc:%s::pat:%s]' % (encounter, name, patient)

		pk = rows[0][0]
		r = {'idx': idx, 'data': rows[0], 'pk_field': 'pk_health_issue'}

		gmBusinessDBObject.cBusinessDBObject.__init__(self, row=r)
	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def rename(self, description=None):
		"""Method for issue renaming.

		@param description
			- the new descriptive name for the issue
		@type description
			- a string instance
		"""
		# sanity check
		if not type(description) in [str, unicode] or description.strip() == '':
			_log.error('<description> must be a non-empty string')
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
	def get_episodes(self):
		cmd = u"SELECT * FROM clin.v_pat_episodes WHERE pk_health_issue = %(pk)s"
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': {'pk': self.pk_obj}}], get_col_idx = True)
		return [ cEpisode(row = {'data': r, 'idx': idx, 'pk_field': 'pk_episode'})  for r in rows ]
	#--------------------------------------------------------
	def close_expired_episode(self, ttl=180):
		"""ttl in days"""
		open_episode = self.get_open_episode()
		if open_episode is None:
			return True
		earliest, latest = open_episode.get_access_range()
		ttl = datetime.timedelta(ttl)
		now = datetime.datetime.now(tz=latest.tzinfo)
		if (latest + ttl) > now:
			return False
		open_episode['episode_open'] = False
		success, data = open_episode.save_payload()
		if success:
			return True
		return False		# should be an exception
	#--------------------------------------------------------
	def close_episode(self):
		open_episode = self.get_open_episode()
		open_episode['episode_open'] = False
		success, data = open_episode.save_payload()
		if success:
			return True
		return False
	#--------------------------------------------------------
	def has_open_episode(self):
		cmd = u"select exists (select 1 from clin.episode where fk_health_issue = %s and is_open is True)"
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': [self.pk_obj]}])
		return rows[0][0]
	#--------------------------------------------------------
	def get_open_episode(self):
		cmd = u"select pk from clin.episode where fk_health_issue = %s and is_open is True"
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': [self.pk_obj]}])
		if len(rows) == 0:
			return None
		return cEpisode(aPK_obj=rows[0][0])
	#--------------------------------------------------------
	def age_noted_human_readable(self):
		if self._payload[self._idx['age_noted']] is None:
			return u'<???>'

		# since we've already got an interval we are bound to use it,
		# further transformation will only introduce more errors,
		# later we can improve this deeper inside
		return gmDateTime.format_interval_medically(self._payload[self._idx['age_noted']])
	#--------------------------------------------------------
	def add_code(self, pk_code=None):
		"""<pk_code> must be a value from ref.coding_system_root.pk_coding_system (clin.lnk_code2item_root.fk_generic_code)"""
		cmd = u"INSERT INTO clin.lnk_code2h_issue (fk_item, fk_generic_code) values (%(item)s, %(code)s)"
		args = {
			'item': self._payload[self._idx['pk_health_issue']],
			'code': pk_code
		}
		rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])
		return True
	#--------------------------------------------------------
	def remove_code(self, pk_code=None):
		"""<pk_code> must be a value from ref.coding_system_root.pk_coding_system (clin.lnk_code2item_root.fk_generic_code)"""
		cmd = u"DELETE FROM clin.lnk_code2h_issue WHERE fk_item = %(item)s AND fk_generic_code = %(code)s"
		args = {
			'item': self._payload[self._idx['pk_health_issue']],
			'code': pk_code
		}
		rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])
		return True
	#--------------------------------------------------------
	def format_as_journal(self, left_margin=0, date_format='%a, %b %d %Y'):
		rows = gmClinNarrative.get_as_journal (
			issues = (self.pk_obj,),
			order_by = u'pk_episode, pk_encounter, clin_when, scr, src_table'
		)

		if len(rows) == 0:
			return u''

		left_margin = u' ' * left_margin

		lines = []
		lines.append(_('Clinical data generated during encounters under this health issue:'))

		prev_epi = None
		for row in rows:
			if row['pk_episode'] != prev_epi:
				lines.append(u'')
				prev_epi = row['pk_episode']

			when = row['clin_when'].strftime(date_format).decode(gmI18N.get_encoding())
			top_row = u'%s%s %s (%s) %s' % (
				gmTools.u_box_top_left_arc,
				gmTools.u_box_horiz_single,
				gmClinNarrative.soap_cat2l10n_str[row['real_soap_cat']],
				when,
				gmTools.u_box_horiz_single * 5
			)
			soap = gmTools.wrap (
				text = row['narrative'],
				width = 60,
				initial_indent = u'  ',
				subsequent_indent = u'  ' + left_margin
			)
			row_ver = u''
			if row['row_version'] > 0:
				row_ver = u'v%s: ' % row['row_version']
			bottom_row = u'%s%s %s, %s%s %s' % (
				u' ' * 40,
				gmTools.u_box_horiz_light_heavy,
				row['modified_by'],
				row_ver,
				row['date_modified'],
				gmTools.u_box_horiz_heavy_light
			)

			lines.append(top_row)
			lines.append(soap)
			lines.append(bottom_row)

		eol_w_margin = u'\n%s' % left_margin
		return left_margin + eol_w_margin.join(lines) + u'\n'
	#--------------------------------------------------------
	def format(self, left_margin=0, patient=None):

		if patient.ID != self._payload[self._idx['pk_patient']]:
			msg = '<patient>.ID = %s but health issue %s belongs to patient %s' % (
				patient.ID,
				self._payload[self._idx['pk_health_issue']],
				self._payload[self._idx['pk_patient']]
			)
			raise ValueError(msg)

		lines = []

		lines.append(_('Health Issue %s%s%s%s   [#%s]') % (
			u'\u00BB',
			self._payload[self._idx['description']],
			u'\u00AB',
			gmTools.coalesce (
				initial = self.laterality_description,
				instead = u'',
				template_initial = u' (%s)',
				none_equivalents = [None, u'', u'?']
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

		lines.append(u' ' + _('Status') + u': %s, %s%s' % (
			gmTools.bool2subst(self._payload[self._idx['is_active']], _('active'), _('inactive')),
			gmTools.bool2subst(self._payload[self._idx['clinically_relevant']], _('clinically relevant'), _('not clinically relevant')),
			gmTools.coalesce (
				initial = diagnostic_certainty_classification2str(self._payload[self._idx['diagnostic_certainty_classification']]),
				instead = u'',
				template_initial = u', %s',
				none_equivalents = [None, u'']
			)
		))

		if self._payload[self._idx['summary']] is not None:
			lines.append(u'')
			lines.append(gmTools.wrap (
				text = self._payload[self._idx['summary']],
				width = 60,
				initial_indent = u'  ',
				subsequent_indent = u'  '
			))

		# codes
		codes = self.generic_codes
		if len(codes) > 0:
			lines.append(u'')
		for c in codes:
			lines.append(u' %s: %s (%s - %s)' % (
				c['code'],
				c['term'],
				c['name_short'],
				c['version']
			))
		del codes

		lines.append(u'')

		emr = patient.get_emr()

		# episodes
		epis = emr.get_episodes(issues = [self._payload[self._idx['pk_health_issue']]])
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
				lines.append(u' \u00BB%s\u00AB (%s)' % (
					epi['description'],
					gmTools.bool2subst(epi['episode_open'], _('ongoing'), _('closed'))
				))

		lines.append('')

		# encounters
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
		meds = emr.get_current_substance_intake (
			issues = [ self._payload[self._idx['pk_health_issue']] ],
			order_by = u'is_currently_active, started, substance'
		)

		if len(meds) > 0:
			lines.append(u'')
			lines.append(_('Active medications: %s') % len(meds))
		for m in meds:
			lines.append(m.format(left_margin = (left_margin + 1)))
		del meds

		# hospital stays
		stays = emr.get_hospital_stays (
			issues = [ self._payload[self._idx['pk_health_issue']] ]
		)

		if len(stays) > 0:
			lines.append(u'')
			lines.append(_('Hospital stays: %s') % len(stays))
		for s in stays:
			lines.append(s.format(left_margin = (left_margin + 1)))
		del stays

		# procedures
		procs = emr.get_performed_procedures (
			issues = [ self._payload[self._idx['pk_health_issue']] ]
		)

		if len(procs) > 0:
			lines.append(u'')
			lines.append(_('Procedures performed: %s') % len(procs))
		for p in procs:
			lines.append(p.format(left_margin = (left_margin + 1)))
		del procs

		epis = self.get_episodes()
		if len(epis) > 0:
			epi_pks = [ e['pk_episode'] for e in epis ]

			# documents
			doc_folder = patient.get_document_folder()
			docs = doc_folder.get_documents(episodes = epi_pks)
			if len(docs) > 0:
				lines.append(u'')
				lines.append(_('Documents: %s') % len(docs))
			del docs

			# test results
			tests = emr.get_test_results_by_date(episodes = epi_pks)
			if len(tests) > 0:
				lines.append(u'')
				lines.append(_('Measurements and Results: %s') % len(tests))
			del tests

			# vaccinations
			vaccs = emr.get_vaccinations(episodes = epi_pks)
			if len(vaccs) > 0:
				lines.append(u'')
				lines.append(_('Vaccinations:'))
			for vacc in vaccs:
				lines.extend(vacc.format(with_reaction = True))
			del vaccs

		del epis

		left_margin = u' ' * left_margin
		eol_w_margin = u'\n%s' % left_margin
		return left_margin + eol_w_margin.join(lines) + u'\n'
	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	episodes = property(get_episodes, lambda x:x)
	#--------------------------------------------------------
	open_episode = property(get_open_episode, lambda x:x)
	#--------------------------------------------------------
	def _get_latest_episode(self):
		cmd = u"""SELECT
			coalesce (
				(SELECT pk FROM clin.episode WHERE fk_health_issue = %(issue)s AND is_open IS TRUE),
				(SELECT pk FROM clin.v_pat_episodes WHERE fk_health_issue = %(issue)s ORDER BY last_affirmed DESC limit 1)
		)"""
		args = {'issue': self.pk_obj}
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = False)
		if len(rows) == 0:
			return None
		return cEpisode(aPK_obj = rows[0][0])

	latest_episode = property(_get_latest_episode, lambda x:x)
	#--------------------------------------------------------
	def _get_laterality_description(self):
		try:
			return laterality2str[self._payload[self._idx['laterality']]]
		except KeyError:
			return u'<???>'

	laterality_description = property(_get_laterality_description, lambda x:x)
	#--------------------------------------------------------
	def _get_diagnostic_certainty_description(self):
		return diagnostic_certainty_classification2str(self._payload[self._idx['diagnostic_certainty_classification']])

	diagnostic_certainty_description = property(_get_diagnostic_certainty_description, lambda x:x)
	#--------------------------------------------------------
	def _get_generic_codes(self):
		if len(self._payload[self._idx['pk_generic_codes']]) == 0:
			return []

		cmd = gmCoding._SQL_get_generic_linked_codes % u'pk_generic_code IN %(pks)s'
		args = {'pks': tuple(self._payload[self._idx['pk_generic_codes']])}
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)
		return [ gmCoding.cGenericLinkedCode(row = {'data': r, 'idx': idx, 'pk_field': 'pk_lnk_code2item'}) for r in rows ]

	def _set_generic_codes(self, pk_codes):
		queries = []
		# remove all codes
		if len(self._payload[self._idx['pk_generic_codes']]) > 0:
			queries.append ({
				'cmd': u'DELETE FROM clin.lnk_code2h_issue WHERE fk_item = %(issue)s AND fk_generic_code IN %(codes)s',
				'args': {
					'issue': self._payload[self._idx['pk_health_issue']],
					'codes': tuple(self._payload[self._idx['pk_generic_codes']])
				}
			})
		# add new codes
		for pk_code in pk_codes:
			queries.append ({
				'cmd': u'INSERT INTO clin.lnk_code2h_issue (fk_item, fk_generic_code) VALUES (%(issue)s, %(pk_code)s)',
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
	cmd = u"insert into clin.health_issue (description, fk_encounter) values (%(desc)s, %(enc)s)"
	queries.append({'cmd': cmd, 'args': {'desc': description, 'enc': encounter}})

	cmd = u"select currval('clin.health_issue_pk_seq')"
	queries.append({'cmd': cmd})

	rows, idx = gmPG2.run_rw_queries(queries = queries, return_data = True)
	h_issue = cHealthIssue(aPK_obj = rows[0][0])

	return h_issue
#-----------------------------------------------------------
def delete_health_issue(health_issue=None):
	if isinstance(health_issue, cHealthIssue):
		pk = health_issue['pk_health_issue']
	else:
		pk = int(health_issue)

	try:
		gmPG2.run_rw_queries(queries = [{'cmd': u'delete from clin.health_issue where pk=%(pk)s', 'args': {'pk': pk}}])
	except gmPG2.dbapi.IntegrityError:
		# should be parsing pgcode/and or error message
		_log.exception('cannot delete health issue')
		raise gmExceptions.DatabaseObjectInUseError('cannot delete health issue, it is in use')
#------------------------------------------------------------
# use as dummy for unassociated episodes
def get_dummy_health_issue():
	issue = {
		'pk_health_issue': None,
		'description': _('Unattributed episodes'),
		'age_noted': None,
		'laterality': u'na',
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
	_cmd_fetch_payload = u"select * from clin.v_pat_episodes where pk_episode=%s"
	_cmds_store_payload = [
		u"""update clin.episode set
				fk_health_issue = %(pk_health_issue)s,
				is_open = %(episode_open)s::boolean,
				description = %(description)s,
				summary = gm.nullify_empty_string(%(summary)s),
				diagnostic_certainty_classification = gm.nullify_empty_string(%(diagnostic_certainty_classification)s)
			where
				pk = %(pk_episode)s and
				xmin = %(xmin_episode)s""",
		u"""select xmin_episode from clin.v_pat_episodes where pk_episode = %(pk_episode)s"""
	]
	_updatable_fields = [
		'pk_health_issue',
		'episode_open',
		'description',
		'summary',
		'diagnostic_certainty_classification'
	]
	#--------------------------------------------------------
	def __init__(self, aPK_obj=None, id_patient=None, name='xxxDEFAULTxxx', health_issue=None, row=None, encounter=None):
		pk = aPK_obj
		if pk is None and row is None:

			where_parts = [u'description = %(desc)s']

			if id_patient is not None:
				where_parts.append(u'pk_patient = %(pat)s')

			if health_issue is not None:
				where_parts.append(u'pk_health_issue = %(issue)s')

			if encounter is not None:
				where_parts.append(u'pk_patient = (select fk_patient from clin.encounter where pk = %(enc)s)')

			args = {
				'pat': id_patient,
				'issue': health_issue,
				'enc': encounter,
				'desc': name
			}

			cmd = u"select * from clin.v_pat_episodes where %s" % u' and '.join(where_parts)

			rows, idx = gmPG2.run_ro_queries(
				queries = [{'cmd': cmd, 'args': args}],
				get_col_idx=True
			)

			if len(rows) == 0:
				raise gmExceptions.NoSuchBusinessObjectError, 'no episode for [%s:%s:%s:%s]' % (id_patient, name, health_issue, encounter)

			r = {'idx': idx, 'data': rows[0], 'pk_field': 'pk_episode'}
			gmBusinessDBObject.cBusinessDBObject.__init__(self, row=r)

		else:
			gmBusinessDBObject.cBusinessDBObject.__init__(self, aPK_obj=pk, row=row)
	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def get_access_range(self):
		"""Get earliest and latest access to this episode.

		Returns a tuple(earliest, latest).
		"""
		cmd = u"""
select
	min(earliest),
	max(latest)
from (
	(select
		(case when clin_when < modified_when
			then clin_when
			else modified_when
		end) as earliest,
		(case when clin_when > modified_when
			then clin_when
			else modified_when
		end) as latest
	from
		clin.clin_root_item
	where
		fk_episode = %(pk)s

	) union all (

	select
		modified_when as earliest,
		modified_when as latest
	from
		clin.episode
	where
		pk = %(pk)s
	)
) as ranges"""
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': {'pk': self.pk_obj}}])
		if len(rows) == 0:
			return (gmNull.cNull(warn=False), gmNull.cNull(warn=False))
		return (rows[0][0], rows[0][1])
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

		cmd = u"""
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
		cmd = u"DELETE FROM clin.lnk_code2episode WHERE fk_item = %(item)s AND fk_generic_code = %(code)s"
		args = {
			'item': self._payload[self._idx['pk_episode']],
			'code': pk_code
		}
		rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])
		return True
	#--------------------------------------------------------
	def format_as_journal(self, left_margin=0, date_format='%a, %b %d %Y'):
		rows = gmClinNarrative.get_as_journal (
			episodes = (self.pk_obj,),
			order_by = u'pk_encounter, clin_when, scr, src_table'
			#order_by = u'pk_encounter, scr, clin_when, src_table'
		)

		if len(rows) == 0:
			return u''

		lines = []

		lines.append(_('Clinical data generated during encounters within this episode:'))

		left_margin = u' ' * left_margin

		prev_enc = None
		for row in rows:
			if row['pk_encounter'] != prev_enc:
				lines.append(u'')
				prev_enc = row['pk_encounter']

			when = row['clin_when'].strftime(date_format).decode(gmI18N.get_encoding())
			top_row = u'%s%s %s (%s) %s' % (
				gmTools.u_box_top_left_arc,
				gmTools.u_box_horiz_single,
				gmClinNarrative.soap_cat2l10n_str[row['real_soap_cat']],
				when,
				gmTools.u_box_horiz_single * 5
			)
			soap = gmTools.wrap (
				text = row['narrative'],
				width = 60,
				initial_indent = u'  ',
				subsequent_indent = u'  ' + left_margin
			)
			row_ver = u''
			if row['row_version'] > 0:
				row_ver = u'v%s: ' % row['row_version']
			bottom_row = u'%s%s %s, %s%s %s' % (
				u' ' * 40,
				gmTools.u_box_horiz_light_heavy,
				row['modified_by'],
				row_ver,
				row['date_modified'],
				gmTools.u_box_horiz_heavy_light
			)

			lines.append(top_row)
			lines.append(soap)
			lines.append(bottom_row)

		eol_w_margin = u'\n%s' % left_margin
		return left_margin + eol_w_margin.join(lines) + u'\n'
	#--------------------------------------------------------
	def format(self, left_margin=0, patient=None):

		if patient.ID != self._payload[self._idx['pk_patient']]:
			msg = '<patient>.ID = %s but episode %s belongs to patient %s' % (
				patient.ID,
				self._payload[self._idx['pk_episode']],
				self._payload[self._idx['pk_patient']]
			)
			raise ValueError(msg)

		lines = []

		# episode details
		lines.append (_('Episode %s%s%s   [#%s]') % (
			gmTools.u_left_double_angle_quote,
			self._payload[self._idx['description']],
			gmTools.u_right_double_angle_quote,
			self._payload[self._idx['pk_episode']]
		))

		enc = cEncounter(aPK_obj = self._payload[self._idx['pk_encounter']])
		lines.append (u' ' + _('Created during encounter: %s (%s - %s)   [#%s]') % (
			enc['l10n_type'],
			enc['started_original_tz'].strftime('%Y-%m-%d %H:%M'),
			enc['last_affirmed_original_tz'].strftime('%H:%M'),
			self._payload[self._idx['pk_encounter']]
		))

		emr = patient.get_emr()
		encs = emr.get_encounters(episodes = [self._payload[self._idx['pk_episode']]])
		first_encounter = None
		last_encounter = None
		if (encs is not None) and (len(encs) > 0):
			first_encounter = emr.get_first_encounter(episode_id = self._payload[self._idx['pk_episode']])
			last_encounter = emr.get_last_encounter(episode_id = self._payload[self._idx['pk_episode']])
			if self._payload[self._idx['episode_open']]:
				end = gmDateTime.pydt_now_here()
				end_str = gmTools.u_ellipsis
			else:
				end = last_encounter['last_affirmed']
				end_str = last_encounter['last_affirmed'].strftime('%m/%Y')
			age = gmDateTime.format_interval_medically(end - first_encounter['started'])
			lines.append(_(' Duration: %s (%s - %s)') % (
				age,
				first_encounter['started'].strftime('%m/%Y'),
				end_str
			))

		lines.append(u' ' + _('Status') + u': %s%s' % (
			gmTools.bool2subst(self._payload[self._idx['episode_open']], _('active'), _('finished')),
			gmTools.coalesce (
				initial = diagnostic_certainty_classification2str(self._payload[self._idx['diagnostic_certainty_classification']]),
				instead = u'',
				template_initial = u', %s',
				none_equivalents = [None, u'']
			)
		))

		if self._payload[self._idx['summary']] is not None:
			lines.append(u'')
			lines.append(gmTools.wrap (
					text = self._payload[self._idx['summary']],
					width = 60,
					initial_indent = u'  ',
					subsequent_indent = u'  '
				)
			)

		# codes
		codes = self.generic_codes
		if len(codes) > 0:
			lines.append(u'')
		for c in codes:
			lines.append(u' %s: %s (%s - %s)' % (
				c['code'],
				c['term'],
				c['name_short'],
				c['version']
			))
		del codes

		lines.append(u'')

		# encounters
		if encs is None:
			lines.append(_('Error retrieving encounters for this episode.'))
		elif len(encs) == 0:
			lines.append(_('There are no encounters for this episode.'))
		else:
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

			lines.append(u' %s - %s (%s):%s' % (
				first_encounter['started_original_tz'].strftime('%Y-%m-%d %H:%M'),
				first_encounter['last_affirmed_original_tz'].strftime('%H:%M'),
				first_encounter['l10n_type'],
				gmTools.coalesce (
					first_encounter['assessment_of_encounter'],
					gmTools.coalesce (
						first_encounter['reason_for_encounter'],
						u'',
						u' \u00BB%s\u00AB' + (u' (%s)' % _('RFE'))
					),
					u' \u00BB%s\u00AB' + (u' (%s)' % _('AOE'))
				)
			))

			if len(encs) > 4:
				lines.append(_(' ... %s skipped ...') % (len(encs) - 4))

			for enc in encs[1:][-3:]:
				lines.append(u' %s - %s (%s):%s' % (
					enc['started_original_tz'].strftime('%Y-%m-%d %H:%M'),
					enc['last_affirmed_original_tz'].strftime('%H:%M'),
					enc['l10n_type'],
					gmTools.coalesce (
						enc['assessment_of_encounter'],
						gmTools.coalesce (
							enc['reason_for_encounter'],
							u'',
							u' \u00BB%s\u00AB' + (u' (%s)' % _('RFE'))
						),
						u' \u00BB%s\u00AB' + (u' (%s)' % _('AOE'))
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
				soap_cats = 'soap',
				emr = emr
			))

		# documents
		doc_folder = patient.get_document_folder()
		docs = doc_folder.get_documents (
			episodes = [ self._payload[self._idx['pk_episode']] ]
		)

		if len(docs) > 0:
			lines.append('')
			lines.append(_('Documents: %s') % len(docs))

		for d in docs:
			lines.append(u' %s %s:%s%s' % (
				d['clin_when'].strftime('%Y-%m-%d'),
				d['l10n_type'],
				gmTools.coalesce(d['comment'], u'', u' "%s"'),
				gmTools.coalesce(d['ext_ref'], u'', u' (%s)')
			))
		del docs

		# hospital stays
		stays = emr.get_hospital_stays (
			episodes = [ self._payload[self._idx['pk_episode']] ]
		)

		if len(stays) > 0:
			lines.append('')
			lines.append(_('Hospital stays: %s') % len(stays))

		for s in stays:
			lines.append(s.format(left_margin = (left_margin + 1)))
		del stays

		# procedures
		procs = emr.get_performed_procedures (
			episodes = [ self._payload[self._idx['pk_episode']] ]
		)

		if len(procs) > 0:
			lines.append(u'')
			lines.append(_('Procedures performed: %s') % len(procs))
		for p in procs:
			lines.append(p.format (
				left_margin = (left_margin + 1),
				include_episode = False,
				include_codes = True
			))
		del procs

		# test results
		tests = emr.get_test_results_by_date(episodes = [ self._payload[self._idx['pk_episode']] ])

		if len(tests) > 0:
			lines.append('')
			lines.append(_('Measurements and Results:'))

		for t in tests:
			lines.extend(t.format (
				with_review = False,
				with_comments = False,
				date_format = '%Y-%m-%d'
			))
		del tests

		# vaccinations
		vaccs = emr.get_vaccinations(episodes = [ self._payload[self._idx['pk_episode']] ])

		if len(vaccs) > 0:
			lines.append(u'')
			lines.append(_('Vaccinations:'))

		for vacc in vaccs:
			lines.extend(vacc.format (
				with_indications = True,
				with_comment = True,
				with_reaction = True,
				date_format = '%Y-%m-%d'
			))
		del vaccs

		left_margin = u' ' * left_margin
		eol_w_margin = u'\n%s' % left_margin
		return left_margin + eol_w_margin.join(lines) + u'\n'
	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def _get_diagnostic_certainty_description(self):
		return diagnostic_certainty_classification2str(self._payload[self._idx['diagnostic_certainty_classification']])

	diagnostic_certainty_description = property(_get_diagnostic_certainty_description, lambda x:x)
	#--------------------------------------------------------
	def _get_generic_codes(self):
		if len(self._payload[self._idx['pk_generic_codes']]) == 0:
			return []

		cmd = gmCoding._SQL_get_generic_linked_codes % u'pk_generic_code IN %(pks)s'
		args = {'pks': tuple(self._payload[self._idx['pk_generic_codes']])}
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)
		return [ gmCoding.cGenericLinkedCode(row = {'data': r, 'idx': idx, 'pk_field': 'pk_lnk_code2item'}) for r in rows ]

	def _set_generic_codes(self, pk_codes):
		queries = []
		# remove all codes
		if len(self._payload[self._idx['pk_generic_codes']]) > 0:
			queries.append ({
				'cmd': u'DELETE FROM clin.lnk_code2episode WHERE fk_item = %(epi)s AND fk_generic_code IN %(codes)s',
				'args': {
					'epi': self._payload[self._idx['pk_episode']],
					'codes': tuple(self._payload[self._idx['pk_generic_codes']])
				}
			})
		# add new codes
		for pk_code in pk_codes:
			queries.append ({
				'cmd': u'INSERT INTO clin.lnk_code2episode (fk_item, fk_generic_code) VALUES (%(epi)s, %(pk_code)s)',
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
		cmd = u"""SELECT EXISTS (
			SELECT 1 FROM clin.clin_narrative
			WHERE
				fk_episode = %(epi)s
					AND
				fk_encounter IN (
					SELECT pk FROM clin.encounter WHERE fk_patient = %(pat)s
				)
		)"""
		args = {
			u'pat': self._payload[self._idx['pk_patient']],
			u'epi': self._payload[self._idx['pk_episode']]
		}
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = False)
		return rows[0][0]

	has_narrative = property(_get_has_narrative, lambda x:x)
#============================================================
def create_episode(pk_health_issue=None, episode_name=None, is_open=False, allow_dupes=False, encounter=None):
	"""Creates a new episode for a given patient's health issue.

	pk_health_issue - given health issue PK
	episode_name - name of episode
	"""
	if not allow_dupes:
		try:
			episode = cEpisode(name=episode_name, health_issue=pk_health_issue, encounter = encounter)
			if episode['episode_open'] != is_open:
				episode['episode_open'] = is_open
				episode.save_payload()
			return episode
		except gmExceptions.ConstructorError:
			pass

	queries = []
	cmd = u"insert into clin.episode (fk_health_issue, description, is_open, fk_encounter) values (%s, %s, %s::boolean, %s)"
	queries.append({'cmd': cmd, 'args': [pk_health_issue, episode_name, is_open, encounter]})
	queries.append({'cmd': cEpisode._cmd_fetch_payload % u"currval('clin.episode_pk_seq')"})
	rows, idx = gmPG2.run_rw_queries(queries = queries, return_data=True, get_col_idx=True)

	episode = cEpisode(row={'data': rows[0], 'idx': idx, 'pk_field': 'pk_episode'})
	return episode
#-----------------------------------------------------------
def delete_episode(episode=None):
	if isinstance(episode, cEpisode):
		pk = episode['pk_episode']
	else:
		pk = int(episode)

	try:
		gmPG2.run_rw_queries(queries = [{'cmd': u'delete from clin.episode where pk=%(pk)s', 'args': {'pk': pk}}])
	except gmPG2.dbapi.IntegrityError:
		# should be parsing pgcode/and or error message
		_log.exception('cannot delete episode')
		raise gmExceptions.DatabaseObjectInUseError('cannot delete episode, it is in use')
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
#============================================================
# encounter API
#============================================================
class cEncounter(gmBusinessDBObject.cBusinessDBObject):
	"""Represents one encounter."""

	_cmd_fetch_payload = u"select * from clin.v_pat_encounters where pk_encounter = %s"
	_cmds_store_payload = [
		u"""update clin.encounter set
				started = %(started)s,
				last_affirmed = %(last_affirmed)s,
				fk_location = %(pk_location)s,
				fk_type = %(pk_type)s,
				reason_for_encounter = gm.nullify_empty_string(%(reason_for_encounter)s),
				assessment_of_encounter = gm.nullify_empty_string(%(assessment_of_encounter)s)
			where
				pk = %(pk_encounter)s and
				xmin = %(xmin_encounter)s""",
		u"""select xmin_encounter from clin.v_pat_encounters where pk_encounter=%(pk_encounter)s"""
	]
	_updatable_fields = [
		'started',
		'last_affirmed',
		'pk_location',
		'pk_type',
		'reason_for_encounter',
		'assessment_of_encounter'
	]
	#--------------------------------------------------------
	def set_active(self):
		"""Set the enconter as the active one.

		"Setting active" means making sure the encounter
		row has the youngest "last_affirmed" timestamp of
		all encounter rows for this patient.
		"""
		self['last_affirmed'] = gmDateTime.pydt_now_here()
		self.save()
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

		queries = []
		cmd = u"""
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
	def same_payload(self, another_object=None):

		relevant_fields = [
			'pk_location',
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
				_log.debug('mismatch on [%s]: "%s" vs. "%s"', field, self._payload[self._idx[field]], another_object[field])
				return False

			if another_object[field] is None:
				return False

			#if self._payload[self._idx[field]].strftime('%Y-%m-%d %H:%M:%S %Z') != another_object[field].strftime('%Y-%m-%d %H:%M:%S %Z'):
			if self._payload[self._idx[field]].strftime('%Y-%m-%d %H:%M') != another_object[field].strftime('%Y-%m-%d %H:%M'):
				_log.debug('mismatch on [%s]: "%s" vs. "%s"', field, self._payload[self._idx[field]], another_object[field])
				return False

		return True
	#--------------------------------------------------------
	def has_clinical_data(self):
		cmd = u"""
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
		cmd = u"""
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
			soap_cats = u'soap '
		else:
			soap_cats = soap_cats.lower()

		cats = []
		for cat in soap_cats:
			if cat in u'soap':
				cats.append(cat)
				continue
			if cat == u' ':
				cats.append(None)

		cmd = u"""
			SELECT EXISTS (
				SELECT 1 FROM clin.clin_narrative
				WHERE
					fk_encounter = %(enc)s
						AND
					soap_cat IN %(cats)s
				LIMIT 1
			)
		"""
		args = {'enc': self._payload[self._idx['pk_encounter']], 'cats': tuple(cats)}
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd,'args': args}])
		return rows[0][0]
	#--------------------------------------------------------
	def has_documents(self):
		cmd = u"""
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
			soap_cat = soap_cat.lower()

		if episode is None:
			epi_part = u'fk_episode is null'
		else:
			epi_part = u'fk_episode = %(epi)s'

		cmd = u"""
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
		cmd = u"""
SELECT * FROM clin.v_pat_episodes
WHERE
	pk_episode IN (

		SELECT DISTINCT fk_episode
		FROM clin.clin_root_item
		WHERE fk_encounter = %%(enc)s

			UNION

		SELECT DISTINCT fk_episode
		FROM blobs.doc_med
		WHERE fk_encounter = %%(enc)s
	)
	%s"""
		args = {'enc': self.pk_obj}
		if exclude is not None:
			cmd = cmd % u'AND pk_episode NOT IN %(excluded)s'
			args['excluded'] = tuple(exclude)
		else:
			cmd = cmd % u''

		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)

		return [ cEpisode(row = {'data': r, 'idx': idx, 'pk_field': 'pk_episode'})  for r in rows ]
	#--------------------------------------------------------
	def add_code(self, pk_code=None, field=None):
		"""<pk_code> must be a value from ref.coding_system_root.pk_coding_system (clin.lnk_code2item_root.fk_generic_code)"""
		if field == u'rfe':
			cmd = u"INSERT INTO clin.lnk_code2rfe (fk_item, fk_generic_code) values (%(item)s, %(code)s)"
		elif field == u'aoe':
			cmd = u"INSERT INTO clin.lnk_code2aoe (fk_item, fk_generic_code) values (%(item)s, %(code)s)"
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
		if field == u'rfe':
			cmd = u"DELETE FROM clin.lnk_code2rfe WHERE fk_item = %(item)s AND fk_generic_code = %(code)s"
		elif field == u'aoe':
			cmd = u"DELETE FROM clin.lnk_code2aoe WHERE fk_item = %(item)s AND fk_generic_code = %(code)s"
		else:
			raise ValueError('<field> must be one of "rfe" or "aoe", not "%s"', field)
		args = {
			'item': self._payload[self._idx['pk_encounter']],
			'code': pk_code
		}
		rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])
		return True
	#--------------------------------------------------------
	def format_soap(self, episodes=None, left_margin=0, soap_cats='soap', emr=None, issues=None):

		lines = []
		for soap_cat in soap_cats:
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

			lines.append(u'-- %s ----------' % gmClinNarrative.soap_cat2l10n_str[soap_cat])
			for soap_entry in soap_cat_narratives:
				txt = gmTools.wrap (
					text = u'%s\n (%.8s %s)' % (
						soap_entry['narrative'],
						soap_entry['provider'],
						soap_entry['date'].strftime('%Y-%m-%d %H:%M')
					),
					width = 75,
					initial_indent = u'',
					subsequent_indent = (u' ' * left_margin)
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
			(self.has_soap_narrative(soap_cats = u'soap') is False)
		)
		if nothing2format:
			return u''

		if date_format is None:
			date_format = '%A, %B %d %Y'

		tex = u'\\multicolumn{2}{l}{%s: %s ({\\footnotesize %s - %s})} \\tabularnewline \n' % (
			gmTools.tex_escape_string(self._payload[self._idx['l10n_type']]),
			self._payload[self._idx['started']].strftime(date_format).decode(gmI18N.get_encoding()),
			self._payload[self._idx['started']].strftime('%H:%M'),
			self._payload[self._idx['last_affirmed']].strftime('%H:%M')
		)
		tex += u'\\hline \\tabularnewline \n'

		for epi in self.get_episodes():
			soaps = epi.get_narrative(soap_cats = soap_cats, encounters = [self.pk_obj], order_by = soap_order)
			if len(soaps) == 0:
				continue
			tex += u'\\multicolumn{2}{l}{\\emph{%s: %s%s}} \\tabularnewline \n' % (
				gmTools.tex_escape_string(_('Problem')),
				gmTools.tex_escape_string(epi['description']),
				gmTools.coalesce (
					initial = diagnostic_certainty_classification2str(epi['diagnostic_certainty_classification']),
					instead = u'',
					template_initial = u' {\\footnotesize [%s]}',
					none_equivalents = [None, u'']
				)
			)
			if epi['pk_health_issue'] is not None:
				tex += u'\\multicolumn{2}{l}{\\emph{%s: %s%s}} \\tabularnewline \n' % (
					gmTools.tex_escape_string(_('Health issue')),
					gmTools.tex_escape_string(epi['health_issue']),
					gmTools.coalesce (
						initial = diagnostic_certainty_classification2str(epi['diagnostic_certainty_classification_issue']),
						instead = u'',
						template_initial = u' {\\footnotesize [%s]}',
						none_equivalents = [None, u'']
					)
				)
			for soap in soaps:
				tex += u'{\\small %s} & {\\small %s} \\tabularnewline \n' % (
					gmClinNarrative.soap_cat2l10n[soap['soap_cat']],
					gmTools.tex_escape_string(soap['narrative'].strip(u'\n'))
				)
			tex += u' & \\tabularnewline \n'

		if self._payload[self._idx['reason_for_encounter']] is not None:
			tex += u'%s & %s \\tabularnewline \n' % (
				gmTools.tex_escape_string(_('RFE')),
				gmTools.tex_escape_string(self._payload[self._idx['reason_for_encounter']])
			)
		if self._payload[self._idx['assessment_of_encounter']] is not None:
			tex += u'%s & %s \\tabularnewline \n' % (
				gmTools.tex_escape_string(_('AOE')),
				gmTools.tex_escape_string(self._payload[self._idx['assessment_of_encounter']])
			)

		tex += u'\\hline \\tabularnewline \n'
		tex += u' & \\tabularnewline \n'

		return tex
	#--------------------------------------------------------
	def format(self, episodes=None, with_soap=False, left_margin=0, patient=None, issues=None, with_docs=True, with_tests=True, fancy_header=True, with_vaccinations=True, with_co_encountlet_hints=False, with_rfe_aoe=False):
		"""Format an encounter.

		with_co_encountlet_hints:
			- whether to include which *other* episodes were discussed during this encounter
			- (only makes sense if episodes != None)
		"""
		lines = []

		if fancy_header:
			lines.append(u'%s%s: %s - %s (@%s)%s [#%s]' % (
				u' ' * left_margin,
				self._payload[self._idx['l10n_type']],
				self._payload[self._idx['started_original_tz']].strftime('%Y-%m-%d %H:%M'),
				self._payload[self._idx['last_affirmed_original_tz']].strftime('%H:%M'),
				self._payload[self._idx['source_time_zone']],
				gmTools.coalesce(self._payload[self._idx['assessment_of_encounter']], u'', u' \u00BB%s\u00AB'),
				self._payload[self._idx['pk_encounter']]
			))

			lines.append(_('  your time: %s - %s  (@%s = %s%s)\n') % (
				self._payload[self._idx['started']].strftime('%Y-%m-%d %H:%M'),
				self._payload[self._idx['last_affirmed']].strftime('%H:%M'),
				gmDateTime.current_local_iso_numeric_timezone_string,
				gmTools.bool2subst (
					gmDateTime.dst_currently_in_effect,
					gmDateTime.py_dst_timezone_name,
					gmDateTime.py_timezone_name
				),
				gmTools.bool2subst(gmDateTime.dst_currently_in_effect, u' - ' + _('daylight savings time in effect'), u'')
			))

			if self._payload[self._idx['reason_for_encounter']] is not None:
				lines.append(u'%s: %s' % (_('RFE'), self._payload[self._idx['reason_for_encounter']]))

			if self._payload[self._idx['assessment_of_encounter']] is not None:
				lines.append(u'%s: %s' % (_('AOE'), self._payload[self._idx['assessment_of_encounter']]))

		else:
			lines.append(u'%s%s: %s - %s%s' % (
				u' ' * left_margin,
				self._payload[self._idx['l10n_type']],
				self._payload[self._idx['started_original_tz']].strftime('%Y-%m-%d %H:%M'),
				self._payload[self._idx['last_affirmed_original_tz']].strftime('%H:%M'),
				gmTools.coalesce(self._payload[self._idx['assessment_of_encounter']], u'', u' \u00BB%s\u00AB')
			))
			if with_rfe_aoe:
				if self._payload[self._idx['reason_for_encounter']] is not None:
					lines.append(u'%s: %s' % (_('RFE'), self._payload[self._idx['reason_for_encounter']]))
				if self._payload[self._idx['assessment_of_encounter']] is not None:
					lines.append(u'%s: %s' % (_('AOE'), self._payload[self._idx['assessment_of_encounter']]))

		if with_soap:
			lines.append(u'')

			if patient.ID != self._payload[self._idx['pk_patient']]:
				msg = '<patient>.ID = %s but encounter %s belongs to patient %s' % (
					patient.ID,
					self._payload[self._idx['pk_encounter']],
					self._payload[self._idx['pk_patient']]
				)
				raise ValueError(msg)

			emr = patient.get_emr()

			lines.extend(self.format_soap (
				episodes = episodes,
				left_margin = left_margin,
				soap_cats = 'soap',
				emr = emr,
				issues = issues
			))

		# test results
		if with_tests:
			tests = emr.get_test_results_by_date (
				episodes = episodes,
				encounter = self._payload[self._idx['pk_encounter']]
			)
			if len(tests) > 0:
				lines.append('')
				lines.append(_('Measurements and Results:'))

			for t in tests:
				lines.extend(t.format())

			del tests

		# vaccinations
		if with_vaccinations:
			vaccs = emr.get_vaccinations (
				episodes = episodes,
				encounters = [ self._payload[self._idx['pk_encounter']] ]
			)

			if len(vaccs) > 0:
				lines.append(u'')
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
				episodes = episodes,
				encounter = self._payload[self._idx['pk_encounter']]
			)

			if len(docs) > 0:
				lines.append(u'')
				lines.append(_('Documents:'))

			for d in docs:
				lines.append(u' %s %s:%s%s' % (
					d['clin_when'].strftime('%Y-%m-%d'),
					d['l10n_type'],
					gmTools.coalesce(d['comment'], u'', u' "%s"'),
					gmTools.coalesce(d['ext_ref'], u'', u' (%s)')
				))

			del docs

		# co-encountlets
		if with_co_encountlet_hints:
			if episodes is not None:
				other_epis = self.get_episodes(exclude = episodes)
				if len(other_epis) > 0:
					lines.append(u'')
					lines.append(_('%s other episodes touched upon during this encounter:') % len(other_epis))
				for epi in other_epis:
					lines.append(u' %s%s%s%s' % (
						gmTools.u_left_double_angle_quote,
						epi['description'],
						gmTools.u_right_double_angle_quote,
						gmTools.coalesce(epi['health_issue'], u'', u' (%s)')
					))

		eol_w_margin = u'\n%s' % (u' ' * left_margin)
		return u'%s\n' % eol_w_margin.join(lines)
	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def _get_rfe_codes(self):
		cmd = u"""
			SELECT * FROM clin.v_linked_codes WHERE
				item_table = 'clin.lnk_code2rfe'::regclass
					AND
				pk_item = %(item)s
		"""
		args = {'item': self._payload[self._idx['pk_encounter']]}
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = False)
		return rows

	rfe_codes = property(_get_rfe_codes, lambda x:x)
	#--------------------------------------------------------
	def _get_aoe_codes(self):
		cmd = u"""
			SELECT * FROM clin.v_linked_codes WHERE
				item_table = 'clin.lnk_code2aoe'::regclass
					AND
				pk_item = %(item)s
		"""
		args = {'item': self._payload[self._idx['pk_encounter']]}
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = False)
		return rows

	aoe_codes = property(_get_aoe_codes, lambda x:x)
#-----------------------------------------------------------
def create_encounter(fk_patient=None, fk_location=-1, enc_type=None):
	"""Creates a new encounter for a patient.

	fk_patient - patient PK
	fk_location - encounter location
	enc_type - type of encounter

	FIXME: we don't deal with location yet
	"""
	if enc_type is None:
		enc_type = u'in surgery'
	# insert new encounter
	queries = []
	try:
		enc_type = int(enc_type)
		cmd = u"""
			INSERT INTO clin.encounter (
				fk_patient, fk_location, fk_type
			) VALUES (
				%(pat)s,
				-1,
				%(typ)s
			) RETURNING pk"""
	except ValueError:
		enc_type = enc_type
		cmd = u"""
			insert into clin.encounter (
				fk_patient, fk_location, fk_type
			) values (
				%(pat)s,
				-1,
				coalesce((select pk from clin.encounter_type where description = %(typ)s), 0)
			) RETURNING pk"""
	args = {'pat': fk_patient, 'typ': enc_type}
	queries.append({'cmd': cmd, 'args': args})
	rows, idx = gmPG2.run_rw_queries(queries = queries, return_data = True, get_col_idx = False)
	encounter = cEncounter(aPK_obj = rows[0]['pk'])

	return encounter
#-----------------------------------------------------------
def update_encounter_type(description=None, l10n_description=None):

	rows, idx = gmPG2.run_rw_queries(
		queries = [{
		'cmd': u"select i18n.upd_tx(%(desc)s, %(l10n_desc)s)",
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
	cmd = u"select description, _(description) from clin.encounter_type where description = %(desc)s"
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}])

	# yes
	if len(rows) > 0:
		# both system and l10n name are the same so all is well
		if (rows[0][0] == description) and (rows[0][1] == l10n_description):
			_log.info('encounter type [%s] already exists with the proper translation')
			return {'description': description, 'l10n_description': l10n_description}

		# or maybe there just wasn't a translation to
		# the current language for this type yet ?
		cmd = u"select exists (select 1 from i18n.translations where orig = %(desc)s and lang = i18n.get_curr_lang())"
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}])

		# there was, so fail
		if rows[0][0]:
			_log.error('encounter type [%s] already exists but with another translation')
			return None

		# else set it
		cmd = u"select i18n.upd_tx(%(desc)s, %(l10n_desc)s)"
		rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])
		return {'description': description, 'l10n_description': l10n_description}

	# no
	queries = [
		{'cmd': u"insert into clin.encounter_type (description) values (%(desc)s)", 'args': args},
		{'cmd': u"select i18n.upd_tx(%(desc)s, %(l10n_desc)s)", 'args': args}
	]
	rows, idx = gmPG2.run_rw_queries(queries = queries)

	return {'description': description, 'l10n_description': l10n_description}
#-----------------------------------------------------------
def get_encounter_types():
	cmd = u"select _(description) as l10n_description, description from clin.encounter_type"
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd}])
	return rows
#-----------------------------------------------------------
def get_encounter_type(description=None):
	cmd = u"SELECT * from clin.encounter_type where description = %s"
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': [description]}])
	return rows
#-----------------------------------------------------------
def delete_encounter_type(description=None):
	cmd = u"delete from clin.encounter_type where description = %(desc)s"
	args = {'desc': description}
	try:
		gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])
	except gmPG2.dbapi.IntegrityError, e:
		if e.pgcode == gmPG2.sql_error_codes.FOREIGN_KEY_VIOLATION:
			return False
		raise

	return True
#============================================================
class cProblem(gmBusinessDBObject.cBusinessDBObject):
	"""Represents one problem.

	problems are the aggregation of
		.clinically_relevant=True issues and
		.is_open=True episodes
	"""
	_cmd_fetch_payload = u''					# will get programmatically defined in __init__
	_cmds_store_payload = [u"select 1"]
	_updatable_fields = []

	#--------------------------------------------------------
	def __init__(self, aPK_obj=None, try_potential_problems=False):
		"""Initialize.

		aPK_obj must contain the keys
			pk_patient
			pk_episode
			pk_health_issue
		"""
		if aPK_obj is None:
			raise gmExceptions.ConstructorError, 'cannot instatiate cProblem for PK: [%s]' % (aPK_obj)

		# As problems are rows from a view of different emr struct items,
		# the PK can't be a single field and, as some of the values of the
		# composed PK may be None, they must be queried using 'is null',
		# so we must programmatically construct the SQL query
		where_parts = []
		pk = {}
		for col_name in aPK_obj.keys():
			val = aPK_obj[col_name]
			if val is None:
				where_parts.append('%s IS NULL' % col_name)
			else:
				where_parts.append('%s = %%(%s)s' % (col_name, col_name))
				pk[col_name] = val

		# try to instantiate from true problem view
		cProblem._cmd_fetch_payload = u"""
			SELECT *, False as is_potential_problem
			FROM clin.v_problem_list
			WHERE %s""" % u' AND '.join(where_parts)

		try:
			gmBusinessDBObject.cBusinessDBObject.__init__(self, aPK_obj=pk)
			return
		except gmExceptions.ConstructorError:
			_log.exception('actual problem not found, trying "potential" problems')
			if try_potential_problems is False:
				raise

		# try to instantiate from potential-problems view
		cProblem._cmd_fetch_payload = u"""
			SELECT *, True as is_potential_problem
			FROM clin.v_potential_problem_list
			WHERE %s""" % u' AND '.join(where_parts)
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

		if self._payload[self._idx['type']] == u'issue':
			episodes = [ cHealthIssue(aPK_obj = self._payload[self._idx['pk_health_issue']]).latest_episode ]
			#xxxxxxxxxxxxx

		emr = patient.get_emr()

		doc_folder = gmDocuments.cDocumentFolder(aPKey = patient.ID)
		return doc_folder.get_visual_progress_notes (
			health_issue = self._payload[self._idx['pk_health_issue']],
			episode = self._payload[self._idx['pk_episode']]
		)
	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	# doubles as 'diagnostic_certainty_description' getter:
	def get_diagnostic_certainty_description(self):
		return diagnostic_certainty_classification2str(self._payload[self._idx['diagnostic_certainty_classification']])

	diagnostic_certainty_description = property(get_diagnostic_certainty_description, lambda x:x)
	#--------------------------------------------------------
	def _get_generic_codes(self):
		if self._payload[self._idx['type']] == u'issue':
			cmd = u"""
				SELECT * FROM clin.v_linked_codes WHERE
					item_table = 'clin.lnk_code2h_issue'::regclass
						AND
					pk_item = %(item)s
			"""
			args = {'item': self._payload[self._idx['pk_health_issue']]}
		else:
			cmd = u"""
				SELECT * FROM clin.v_linked_codes WHERE
					item_table = 'clin.lnk_code2episode'::regclass
						AND
					pk_item = %(item)s
			"""
			args = {'item': self._payload[self._idx['pk_episode']]}

		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)
		return [ gmCoding.cGenericLinkedCode(row = {'data': r, 'idx': idx, 'pk_field': 'pk_lnk_code2item'}) for r in rows ]

	generic_codes = property(_get_generic_codes, lambda x:x)
#-----------------------------------------------------------
def problem2episode(problem=None):
	"""Retrieve the cEpisode instance equivalent to the given problem.

	The problem's type attribute must be 'episode'

	@param problem: The problem to retrieve its related episode for
	@type problem: A gmEMRStructItems.cProblem instance
	"""
	if isinstance(problem, cEpisode):
		return problem

	exc = TypeError('cannot convert [%s] to episode' % problem)

	if not isinstance(problem, cProblem):
		raise exc

	if problem['type'] != 'episode':
		raise exc

	return cEpisode(aPK_obj = problem['pk_episode'])
#-----------------------------------------------------------
def problem2issue(problem=None):
	"""Retrieve the cIssue instance equivalent to the given problem.

	The problem's type attribute must be 'issue'.

	@param problem: The problem to retrieve the corresponding issue for
	@type problem: A gmEMRStructItems.cProblem instance
	"""
	if isinstance(problem, cHealthIssue):
		return problem

	exc = TypeError('cannot convert [%s] to health issue' % problem)

	if not isinstance(problem, cProblem):
		raise exc

	if  problem['type'] != 'issue':
		raise exc

	return cHealthIssue(aPK_obj = problem['pk_health_issue'])
#-----------------------------------------------------------
def reclass_problem(self, problem=None):
	"""Transform given problem into either episode or health issue instance.
	"""
	if isinstance(problem, (cEpisode, cHealthIssue)):
		return problem

	exc = TypeError('cannot reclass [%s] instance to either episode or health issue' % type(problem))

	if not isinstance(problem, cProblem):
		_log.debug(u'%s' % problem)
		raise exc

	if problem['type'] == 'episode':
		return cEpisode(aPK_obj = problem['pk_episode'])

	if problem['type'] == 'issue':
		return cHealthIssue(aPK_obj = problem['pk_health_issue'])

	raise exc
#============================================================
class cHospitalStay(gmBusinessDBObject.cBusinessDBObject):

	_cmd_fetch_payload = u"select * from clin.v_pat_hospital_stays where pk_hospital_stay = %s"
	_cmds_store_payload = [
		u"""update clin.hospital_stay set
				clin_when = %(admission)s,
				discharge = %(discharge)s,
				narrative = gm.nullify_empty_string(%(hospital)s),
				fk_episode = %(pk_episode)s,
				fk_encounter = %(pk_encounter)s
			where
				pk = %(pk_hospital_stay)s and
				xmin = %(xmin_hospital_stay)s""",
		u"""select xmin_hospital_stay from clin.v_pat_hospital_stays where pk_hospital_stay = %(pk_hospital_stay)s"""
	]
	_updatable_fields = [
		'admission',
		'discharge',
		'hospital',
		'pk_episode',
		'pk_encounter'
	]
	#-------------------------------------------------------
	def format(self, left_margin=0, include_procedures=False, include_docs=False):

		if self._payload[self._idx['discharge']] is not None:
			dis = u' - %s' % self._payload[self._idx['discharge']].strftime('%Y %b %d').decode(gmI18N.get_encoding())
		else:
			dis = u''

		line = u'%s%s%s%s: %s%s%s' % (
			u' ' * left_margin,
			self._payload[self._idx['admission']].strftime('%Y %b %d').decode(gmI18N.get_encoding()),
			dis,
			gmTools.coalesce(self._payload[self._idx['hospital']], u'', u' (%s)'),
			gmTools.u_left_double_angle_quote,
			self._payload[self._idx['episode']],
			gmTools.u_right_double_angle_quote
		)

		return line
#-----------------------------------------------------------
def get_patient_hospital_stays(patient=None):

	queries = [{
		'cmd': u'SELECT * FROM clin.v_pat_hospital_stays WHERE pk_patient = %(pat)s ORDER BY admission',
		'args': {'pat': patient}
	}]

	rows, idx = gmPG2.run_ro_queries(queries = queries, get_col_idx = True)

	return [ cHospitalStay(row = {'idx': idx, 'data': r, 'pk_field': 'pk_hospital_stay'})  for r in rows ]
#-----------------------------------------------------------
def create_hospital_stay(encounter=None, episode=None):

	queries = [{
		 'cmd': u'INSERT INTO clin.hospital_stay (fk_encounter, fk_episode) VALUES (%(enc)s, %(epi)s) RETURNING pk',
		 'args': {'enc': encounter, 'epi': episode}
	}]
	rows, idx = gmPG2.run_rw_queries(queries = queries, return_data = True)

	return cHospitalStay(aPK_obj = rows[0][0])
#-----------------------------------------------------------
def delete_hospital_stay(stay=None):
	cmd = u'DELETE FROM clin.hospital_stay WHERE pk = %(pk)s'
	args = {'pk': stay}
	gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])
	return True
#============================================================
class cPerformedProcedure(gmBusinessDBObject.cBusinessDBObject):

	_cmd_fetch_payload = u"select * from clin.v_pat_procedures where pk_procedure = %s"
	_cmds_store_payload = [
		u"""UPDATE clin.procedure SET
				soap_cat = 'p',
				clin_when = %(clin_when)s,
				clin_end = %(clin_end)s,
				is_ongoing = %(is_ongoing)s,
				clin_where = NULLIF (
					COALESCE (
						%(pk_hospital_stay)s::TEXT,
						gm.nullify_empty_string(%(clin_where)s)
					),
					%(pk_hospital_stay)s::TEXT
				),
				narrative = gm.nullify_empty_string(%(performed_procedure)s),
				fk_hospital_stay = %(pk_hospital_stay)s,
				fk_episode = %(pk_episode)s,
				fk_encounter = %(pk_encounter)s
			WHERE
				pk = %(pk_procedure)s AND
				xmin = %(xmin_procedure)s
			RETURNING xmin as xmin_procedure"""
	]
	_updatable_fields = [
		'clin_when',
		'clin_end',
		'is_ongoing',
		'clin_where',
		'performed_procedure',
		'pk_hospital_stay',
		'pk_episode',
		'pk_encounter'
	]
	#-------------------------------------------------------
	def __setitem__(self, attribute, value):

		if (attribute == 'pk_hospital_stay') and (value is not None):
			gmBusinessDBObject.cBusinessDBObject.__setitem__(self, 'clin_where', None)

		if (attribute == 'clin_where') and (value is not None) and (value.strip() != u''):
			gmBusinessDBObject.cBusinessDBObject.__setitem__(self, 'pk_hospital_stay', None)

		gmBusinessDBObject.cBusinessDBObject.__setitem__(self, attribute, value)
	#-------------------------------------------------------
	def format(self, left_margin=0, include_episode=True, include_codes=False):

		if self._payload[self._idx['is_ongoing']]:
			end = _(' (ongoing)')
		else:
			end = self._payload[self._idx['clin_end']]
			if end is None:
				end = u''
			else:
				end = u' - %s' % end.strftime('%Y %b %d').decode(gmI18N.get_encoding())

		line = u'%s%s%s, %s: %s' % (
			(u' ' * left_margin),
			self._payload[self._idx['clin_when']].strftime('%Y %b %d').decode(gmI18N.get_encoding()),
			end,
			self._payload[self._idx['clin_where']],
			self._payload[self._idx['performed_procedure']]
		)
		if include_episode:
			line = u'%s (%s)' % (line, self._payload[self._idx['episode']])

		if include_codes:
			codes = self.generic_codes
			if len(codes) > 0:
				line += u'\n'
			for c in codes:
				line += u'%s  %s: %s (%s - %s)\n' % (
					(u' ' * left_margin),
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
		cmd = u"INSERT INTO clin.lnk_code2procedure (fk_item, fk_generic_code) values (%(issue)s, %(code)s)"
		args = {
			'issue': self._payload[self._idx['pk_procedure']],
			'code': pk_code
		}
		rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])
		return True
	#--------------------------------------------------------
	def remove_code(self, pk_code=None):
		"""<pk_code> must be a value from ref.coding_system_root.pk_coding_system (clin.lnk_code2item_root.fk_generic_code)"""
		cmd = u"DELETE FROM clin.lnk_code2procedure WHERE fk_item = %(issue)s AND fk_generic_code = %(code)s"
		args = {
			'issue': self._payload[self._idx['pk_procedure']],
			'code': pk_code
		}
		rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])
		return True
	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def _get_generic_codes(self):
		if len(self._payload[self._idx['pk_generic_codes']]) == 0:
			return []

		cmd = gmCoding._SQL_get_generic_linked_codes % u'pk_generic_code IN %(pks)s'
		args = {'pks': tuple(self._payload[self._idx['pk_generic_codes']])}
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)
		return [ gmCoding.cGenericLinkedCode(row = {'data': r, 'idx': idx, 'pk_field': 'pk_lnk_code2item'}) for r in rows ]

	def _set_generic_codes(self, pk_codes):
		queries = []
		# remove all codes
		if len(self._payload[self._idx['pk_generic_codes']]) > 0:
			queries.append ({
				'cmd': u'DELETE FROM clin.lnk_code2procedure WHERE fk_item = %(proc)s AND fk_generic_code IN %(codes)s',
				'args': {
					'proc': self._payload[self._idx['pk_procedure']],
					'codes': tuple(self._payload[self._idx['pk_generic_codes']])
				}
			})
		# add new codes
		for pk_code in pk_codes:
			queries.append ({
				'cmd': u'INSERT INTO clin.lnk_code2procedure (fk_item, fk_generic_code) VALUES (%(proc)s, %(pk_code)s)',
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
def get_performed_procedures(patient=None):

	queries = [
		{
		'cmd': u'select * from clin.v_pat_procedures where pk_patient = %(pat)s order by clin_when',
		'args': {'pat': patient}
		}
	]

	rows, idx = gmPG2.run_ro_queries(queries = queries, get_col_idx = True)

	return [ cPerformedProcedure(row = {'idx': idx, 'data': r, 'pk_field': 'pk_procedure'})  for r in rows ]
#-----------------------------------------------------------
def create_performed_procedure(encounter=None, episode=None, location=None, hospital_stay=None, procedure=None):

	queries = [{
		'cmd': u"""
			INSERT INTO clin.procedure (
				fk_encounter,
				fk_episode,
				soap_cat,
				clin_where,
				fk_hospital_stay,
				narrative
			) VALUES (
				%(enc)s,
				%(epi)s,
				'p',
				gm.nullify_empty_string(%(loc)s),
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
	cmd = u'delete from clin.procedure where pk = %(pk)s'
	args = {'pk': procedure}
	gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])
	return True
#============================================================
# main - unit testing
#------------------------------------------------------------
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	#--------------------------------------------------------
	# define tests
	#--------------------------------------------------------
	def test_problem():
		print "\nProblem test"
		print "------------"
		prob = cProblem(aPK_obj={'pk_patient': 12, 'pk_health_issue': 1, 'pk_episode': None})
		print prob
		fields = prob.get_fields()
		for field in fields:
			print field, ':', prob[field]
		print '\nupdatable:', prob.get_updatable_fields()
		epi = prob.get_as_episode()
		print '\nas episode:'
		if epi is not None:
			for field in epi.get_fields():
				print '   .%s : %s' % (field, epi[field])
	#--------------------------------------------------------
	def test_health_issue():
		print "\nhealth issue test"
		print "-----------------"
		h_issue = cHealthIssue(aPK_obj=2)
		print h_issue
		fields = h_issue.get_fields()
		for field in fields:
			print field, ':', h_issue[field]
		print "has open episode:", h_issue.has_open_episode()
		print "open episode:", h_issue.get_open_episode()
		print "updateable:", h_issue.get_updatable_fields()
		h_issue.close_expired_episode(ttl=7300)
		h_issue = cHealthIssue(encounter = 1, name = u'post appendectomy/peritonitis')
		print h_issue
		print h_issue.format_as_journal()
	#--------------------------------------------------------	
	def test_episode():
		print "\nepisode test"
		print "------------"
		episode = cEpisode(aPK_obj=1)
		print episode
		fields = episode.get_fields()
		for field in fields:
			print field, ':', episode[field]
		print "updatable:", episode.get_updatable_fields()
		raw_input('ENTER to continue')

		old_description = episode['description']
		old_enc = cEncounter(aPK_obj = 1)

		desc = '1-%s' % episode['description']
		print "==> renaming to", desc
		successful = episode.rename (
			description = desc
		)
		if not successful:
			print "error"
		else:
			print "success"
			for field in fields:
				print field, ':', episode[field]

		print "episode range:", episode.get_access_range()

		raw_input('ENTER to continue')

	#--------------------------------------------------------
	def test_encounter():
		print "\nencounter test"
		print "--------------"
		encounter = cEncounter(aPK_obj=1)
		print encounter
		fields = encounter.get_fields()
		for field in fields:
			print field, ':', encounter[field]
		print "updatable:", encounter.get_updatable_fields()
	#--------------------------------------------------------
	def test_encounter2latex():
		encounter = cEncounter(aPK_obj=1)
		print encounter
		print ""
		print encounter.format_latex()
	#--------------------------------------------------------
	def test_performed_procedure():
		procs = get_performed_procedures(patient = 12)
		for proc in procs:
			print proc.format(left_margin=2)
	#--------------------------------------------------------
	def test_hospital_stay():
		stay = create_hospital_stay(encounter = 1, episode = 2)
		stay['hospital'] = u'Starfleet Galaxy General Hospital'
		stay.save_payload()
		print stay
		for s in get_patient_hospital_stays(12):
			print s
		delete_hospital_stay(stay['pk_hospital_stay'])
		stay = create_hospital_stay(encounter = 1, episode = 4)
	#--------------------------------------------------------
	def test_diagnostic_certainty_classification_map():
		tests = [None, 'A', 'B', 'C', 'D', 'E']

		for t in tests:
			print type(t), t
			print type(diagnostic_certainty_classification2str(t)), diagnostic_certainty_classification2str(t)
	#--------------------------------------------------------
	def test_episode_codes():
		epi = cEpisode(aPK_obj = 2)
		print epi
		print epi.generic_codes
	#--------------------------------------------------------
	# run them
	#test_episode()
	#test_problem()
	#test_encounter()
	#test_health_issue()
	#test_hospital_stay()
	#test_performed_procedure()
	#test_diagnostic_certainty_classification_map()
	#test_encounter2latex()
	test_episode_codes()
#============================================================

