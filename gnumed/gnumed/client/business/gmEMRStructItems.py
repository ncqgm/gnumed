# -*- coding: utf8 -*-
"""GNUmed health related business object.

license: GPL
"""
#============================================================
__version__ = "$Revision: 1.127 $"
__author__ = "Carlos Moro <cfmoro1976@yahoo.es>"

import types, sys, string, datetime, logging, time


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmPG2, gmExceptions, gmNull, gmBusinessDBObject, gmDateTime, gmTools
from Gnumed.business import gmClinNarrative


_log = logging.getLogger('gm.emr')
_log.info(__version__)

#============================================================
# Health Issues API
#============================================================
class cHealthIssue(gmBusinessDBObject.cBusinessDBObject):
	"""Represents one health issue."""

	_cmd_fetch_payload = u"select *, xmin_health_issue from clin.v_health_issues where pk_health_issue=%s"
	_cmds_store_payload = [
		u"""update clin.health_issue set
				description = %(description)s,
				age_noted = %(age_noted)s,
				laterality = %(laterality)s,
				is_active = %(is_active)s,
				clinically_relevant = %(clinically_relevant)s,
				is_confidential = %(is_confidential)s,
				is_cause_of_death = %(is_cause_of_death)s
			where
				pk = %(pk_health_issue)s and
				xmin = %(xmin_health_issue)s""",
		u"select xmin from clin.health_issue where pk = %(pk_health_issue)s"
	]
	_updatable_fields = [
		'description',
		'age_noted',
		'laterality',
		'is_active',
		'clinically_relevant',
		'is_confidential',
		'is_cause_of_death'
	]
	#--------------------------------------------------------
	def __init__(self, aPK_obj=None, encounter=None, name='xxxDEFAULTxxx', row=None):
		pk = aPK_obj
		if pk is None and row is None:
			cmd = u"""select *, xmin_health_issue
					from clin.v_health_issues
					where
						description = %(desc)s
							and
						pk_patient = (select fk_patient from clin.encounter where pk = %(enc)s)
			"""
			rows, idx = gmPG2.run_ro_queries (
				queries = [{'cmd': cmd, 'args': {'enc': encounter, 'desc': name}}],
				get_col_idx = True
			)
			if len(rows) == 0:
				raise gmExceptions.NoSuchBusinessObjectError, 'no health issue for [%s:%s]' % (encounter, name)
			pk = rows[0][0]
			r = {'idx': idx, 'data': rows[0], 'pk_field': 'pk_health_issue'}
			gmBusinessDBObject.cBusinessDBObject.__init__(self, row=r)
		else:
			gmBusinessDBObject.cBusinessDBObject.__init__(self, aPK_obj=pk, row=row)
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

		# seemingly silly but convinces PG to "nicely"
		# format the interval for us
		cmd = u"""select
age (
	(select dob from dem.identity where pk = %(pat)s) + %(issue_age)s,
	(select dob from dem.identity where pk = %(pat)s)
)::text
|| ' (' || age (
	(select dob from dem.identity where pk = %(pat)s) + %(issue_age)s
)::text || ' ago)'
"""
		args = {
			'pat': self._payload[self._idx['pk_patient']],
			'issue_age': self._payload[self._idx['age_noted']]
		}
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}])
		return rows[0][0]
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

		lines.append(_('Health Issue %s%s%s [#%s]') % (
			u'\u00BB',
			self._payload[self._idx['description']],
			u'\u00AB',
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

		lines.append(_(' Noted at age: %s') % self.age_noted_human_readable())
		lines.append(_(' Status: %s, %s') % (
			gmTools.bool2subst(self._payload[self._idx['is_active']], _('active'), _('inactive')),
			gmTools.bool2subst(self._payload[self._idx['clinically_relevant']], _('clinically relevant'), _('not clinically relevant'))
		))
		lines.append('')

		emr = patient.get_emr()

		epis = emr.get_episodes(issues = [self._payload[self._idx['pk_health_issue']]])
		if epis is None:
			lines.append(_('Error retrieving episodes for this health issue.'))
		elif len(epis) == 0:
			lines.append(_('There are no episodes for this health issue.'))
		else:
			lines.append(_('Episodes: %s') % len(epis))
			lines.append(_(' Most recent: %s%s%s') % (
				u'\u00BB',
				emr.get_most_recent_episode(issue = self._payload[self._idx['pk_health_issue']])['description'],
				u'\u00AB'
			))
			lines.append('')
			for epi in epis:
				lines.append(u' \u00BB%s\u00AB (%s)' % (
					epi['description'],
					gmTools.bool2subst(epi['episode_open'], _('ongoing'), _('closed'))
				))

		lines.append('')

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

		left_margin = u' ' * left_margin
		eol_w_margin = u'\n%s' % left_margin
		return left_margin + eol_w_margin.join(lines) + u'\n'
#============================================================
def create_health_issue(description=None, encounter=None):
	"""Creates a new health issue for a given patient.

	description - health issue name
	"""
	try:
		h_issue = cHealthIssue(name=description, encounter=encounter)
		return (True, h_issue)
	except gmExceptions.ConstructorError:
		pass

	queries = []
	cmd = u"insert into clin.health_issue (description, fk_encounter) values (%s, %s, %s)"
	queries.append({'cmd': cmd, 'args': [encounter,]})

	cmd = u"select currval('clin.health_issue_pk_seq')"
	queries.append({'cmd': cmd})

	rows, idx = gmPG2.run_rw_queries(queries=queries, return_data=True)
	h_issue = cHealthIssue(aPK_obj = rows[0][0])

	return (True, h_issue)
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
		'is_cause_of_death': False
	}
	return issue
#-----------------------------------------------------------
def health_issue2problem(health_issue=None):
	return cProblem(aPK_obj = {
		'pk_patient': health_issue['pk_patient'],
		'pk_health_issue': episode['pk_health_issue'],
		'pk_episode': None
	})
#============================================================
# episodes API
#============================================================
class cEpisode(gmBusinessDBObject.cBusinessDBObject):
	"""Represents one clinical episode.
	"""
	_cmd_fetch_payload = u"select * from clin.v_pat_episodes where pk_episode=%s"
	_cmds_store_payload = [
		u"""update clin.episode set
				fk_health_issue=%(pk_health_issue)s,
				is_open=%(episode_open)s::boolean,
				description=%(description)s
			where
				pk=%(pk_episode)s and
				xmin=%(xmin_episode)s""",
		u"""select xmin_episode from clin.v_pat_episodes where pk_episode=%(pk_episode)s"""
	]
	_updatable_fields = [
		'pk_health_issue',
		'episode_open',
		'description'
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
	def format(self, left_margin=0, patient=None):

		left_margin = u' ' * left_margin

		if patient.ID != self._payload[self._idx['pk_patient']]:
			msg = '<patient>.ID = %s but episode %s belongs to patient %s' % (
				patient.ID,
				self._payload[self._idx['pk_episode']],
				self._payload[self._idx['pk_patient']]
			)
			raise ValueError(msg)

		lines = []

		lines.append(_('Episode %s%s%s (%s) [#%s]\n') % (
			u'\u00BB',
			self._payload[self._idx['description']],
			u'\u00AB',
			gmTools.bool2subst(self._payload[self._idx['episode_open']], _('active'), _('finished')),
			self._payload[self._idx['pk_episode']]
		))

		emr = patient.get_emr()
		encs = emr.get_encounters(episodes = [self._payload[self._idx['pk_episode']]])
		first_encounter = None
		last_encounter = None
		if encs is None:
			lines.append(_('Error retrieving encounters for this episode.'))
		elif len(encs) == 0:
			lines.append(_('There are no encounters for this episode.'))
		else:
			first_encounter = emr.get_first_encounter(episode_id = self._payload[self._idx['pk_episode']])
			last_encounter = emr.get_last_encounter(episode_id = self._payload[self._idx['pk_episode']])

			lines.append(_('Last worked on: %s\n') % last_encounter['last_affirmed_original_tz'].strftime('%x %H:%M'))

			lines.append(_('1st and last 3 of %s (%s - %s) encounters:') % (
				len(encs),
				first_encounter['started'].strftime('%m/%Y'),
				last_encounter['last_affirmed'].strftime('%m/%Y')
			))

			lines.append(u' %s - %s (%s):%s' % (
				first_encounter['started_original_tz'].strftime('%x %H:%M'),
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
				lines.append(u' ... %s skipped ...' % (len(encs) - 4))

			for enc in encs[1:][-3:]:
				lines.append(u' %s - %s (%s):%s' % (
					enc['started_original_tz'].strftime('%x %H:%M'),
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
				d['date'].strftime('%x'),
				d['l10n_type'],
				gmTools.coalesce(d['comment'], u'', u' "%s"'),
				gmTools.coalesce(d['ext_ref'], u'', u' (%s)')
			))

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

		eol_w_margin = u'\n%s' % left_margin
		return left_margin + eol_w_margin.join(lines) + u'\n'
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
	cmd = u"insert into clin.episode (fk_health_issue, fk_patient, description, is_open, fk_encounter) values (%s, (select fk_patient from clin.encounter where pk = %s), %s, %s::boolean, %s)"
	queries.append({'cmd': cmd, 'args': [pk_health_issue, encounter, episode_name, is_open, encounter]})
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
def episode2problem(episode=None):
	return cProblem(aPK_obj = {
		'pk_patient': episode['pk_patient'],
		'pk_episode': episode['pk_episode'],
		'pk_health_issue': episode['pk_health_issue']
	})
#============================================================
# encounter API
#============================================================
class cEncounter(gmBusinessDBObject.cBusinessDBObject):
	"""Represents one encounter."""
	_cmd_fetch_payload = u"select * from clin.v_pat_encounters where pk_encounter=%s"
	_cmds_store_payload = [
		u"""update clin.encounter set
				started=%(started)s,
				last_affirmed=%(last_affirmed)s,
				fk_location=%(pk_location)s,
				fk_type=%(pk_type)s,
				reason_for_encounter=%(reason_for_encounter)s,
				assessment_of_encounter=%(assessment_of_encounter)s
			where
				pk=%(pk_encounter)s and
				xmin=%(xmin_encounter)s""",
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
	def set_active(self, staff_id=None):
		"""Set the enconter as the active one.

		"Setting active" means making sure the encounter
		row has the youngest "last_affirmed" timestamp of
		all encounter rows for this patient.

		staff_id - Provider's primary key
		"""
		self._payload[self._idx['last_affirmed']] = datetime.datetime.now(tz = gmDateTime.gmCurrentLocalTimezone)
		success, data = self.save_payload()
		if not success:
			_log.error('cannot reaffirm encounter [%s]' % self.pk_obj)
			_log.error(str(data))
			return False
		return True
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
	def has_clinical_data(self):
		cmd = u"""
select exists (
	select 1 from clin.v_pat_items where pk_patient=%(pat)s and pk_encounter=%(enc)s union all
	select 1 from blobs.doc_med where fk_identity=%(pat)s and fk_encounter=%(enc)s
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
	def has_documents(self):
		cmd = u"""
select exists (
	select 1 from blobs.doc_med where fk_identity=%(pat)s and fk_encounter=%(enc)s
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
	def format_soap(self, episodes=None, left_margin=u'', soap_cats='soap', emr=None, issues=None):

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

			lines.append('-- %s ----------' % gmClinNarrative.soap_cat2l10n_str[soap_cat])
			for soap_entry in soap_cat_narratives:
				txt = gmTools.wrap (
					text = '%s  %.8s\n%s' % (
						soap_entry['date'].strftime('%d.%m. %H:%M'),
						soap_entry['provider'],
						soap_entry['narrative']
					),
					width = 75,
					initial_indent = u'',
					subsequent_indent = left_margin + u'   '
				)
				lines.append(txt)
				lines.append('')

		return lines
	#--------------------------------------------------------
	def format(self, episodes=None, with_soap=False, left_margin=0, patient=None, issues=None, with_docs=True, with_tests=True, fancy_header=True):

		left_margin = u' ' * left_margin

		lines = []

		if fancy_header:
			lines.append(u'%s%s: %s - %s (@%s)%s [#%s]' % (
				left_margin,
				self._payload[self._idx['l10n_type']],
				self._payload[self._idx['started_original_tz']].strftime('%x %H:%M'),
				self._payload[self._idx['last_affirmed_original_tz']].strftime('%H:%M'),
				self._payload[self._idx['source_time_zone']],
				gmTools.coalesce(self._payload[self._idx['assessment_of_encounter']], u'', u' \u00BB%s\u00AB'),
				self._payload[self._idx['pk_encounter']]
			))

			lines.append(_('  your time: %s - %s  (@%s = %s%s)\n') % (
				self._payload[self._idx['started']].strftime('%x %H:%M'),
				self._payload[self._idx['last_affirmed']].strftime('%H:%M'),
				gmDateTime.current_local_iso_numeric_timezone_string,
				gmTools.bool2subst (
					gmDateTime.dst_currently_in_effect,
					gmDateTime.py_dst_timezone_name,
					gmDateTime.py_timezone_name
				),
				gmTools.bool2subst(gmDateTime.dst_currently_in_effect, u' - ' + _('daylight savings time in effect'), u'')
			))

			lines.append(u'%s: %s' % (
				_('RFE'),
				gmTools.coalesce(self._payload[self._idx['reason_for_encounter']], u'')
			))
			lines.append(u'%s: %s' % (
				_('AOE'),
				gmTools.coalesce(self._payload[self._idx['assessment_of_encounter']], u'')
			))

		else:
			lines.append(u'%s%s: %s - %s%s' % (
				left_margin,
				self._payload[self._idx['l10n_type']],
				self._payload[self._idx['started_original_tz']].strftime('%x %H:%M'),
				self._payload[self._idx['last_affirmed_original_tz']].strftime('%H:%M'),
				gmTools.coalesce(self._payload[self._idx['assessment_of_encounter']], u'', u' \u00BB%s\u00AB')
			))

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

		if with_docs:
			doc_folder = patient.get_document_folder()
			docs = doc_folder.get_documents (
				episodes = episodes,
				encounter = self._payload[self._idx['pk_encounter']]
			)

			if len(docs) > 0:
				lines.append('')
				lines.append(_('Documents:'))

			for d in docs:
				lines.append(u' %s %s:%s%s' % (
					d['date'].strftime('%x'),
					d['l10n_type'],
					gmTools.coalesce(d['comment'], u'', u' "%s"'),
					gmTools.coalesce(d['ext_ref'], u'', u' (%s)')
				))

		eol_w_margin = u'\n%s' % left_margin
		return u'%s\n' % eol_w_margin.join(lines)

		# special items (vaccinations, ...)

#        try:
 #               filtered_items.extend(emr.get_vaccinations(
  #                  since=self.__constraints['since'],
   #                 until=self.__constraints['until'],
    #                encounters=self.__constraints['encounters'],
     #               episodes=self.__constraints['episodes'],
      #              issues=self.__constraints['issues']))
       # except:
        #        _log.error("vaccination error? outside regime")

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
			insert into clin.encounter (
				fk_patient, fk_location, fk_type
			) values (
				%s, -1, %s
			)"""
	except ValueError:
		enc_type = enc_type
		cmd = u"""
			insert into clin.encounter (
				fk_patient, fk_location, fk_type
			) values (
				%s, -1,	coalesce((select pk from clin.encounter_type where description=%s), 0)
			)"""
	queries.append({'cmd': cmd, 'args': [fk_patient, enc_type]})
	queries.append({'cmd': cEncounter._cmd_fetch_payload % u"currval('clin.encounter_pk_seq')"})
	rows, idx = gmPG2.run_rw_queries(queries=queries, return_data=True, get_col_idx=True)
	encounter = cEncounter(row={'data': rows[0], 'idx': idx, 'pk_field': 'pk_encounter'})
	return encounter
#-----------------------------------------------------------
def update_encounter_type(description=None, l10n_description=None):

	rows, idx = gmPG2.run_rw_queries(queries = [{
		'cmd': u"select i18n.upd_tx(%(desc)s, %(l10n_desc)s)",
		'args': {'desc': description, 'l10n_desc': l10n_description}
	}])

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
		issues w/o episodes,
		issues w/ episodes and
		episodes w/o issues
	"""
	_cmd_fetch_payload = u''					# will get programmatically defined in __init__
	_cmds_store_payload = [u"select 1"]
	_updatable_fields = []

	#--------------------------------------------------------
	def __init__(self, aPK_obj=None):
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
				where_parts.append('%s is null' % col_name)
			else:
				where_parts.append('%s=%%(%s)s' % (col_name, col_name))
				pk[col_name] = val
		cProblem._cmd_fetch_payload = u"select * from clin.v_problem_list where " + ' and '.join(where_parts)
		# instantiate class
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
		return cEpisode(aPK_obj=self._payload[self._idx['pk_episode']])
#============================================================
# main - unit testing
#------------------------------------------------------------
if __name__ == '__main__':

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
	if (len(sys.argv) > 1) and (sys.argv[1] == 'test'):
		# run them
		#test_episode()
		#test_problem()
		#test_encounter()
		test_health_issue()

#============================================================
# $Log: gmEMRStructItems.py,v $
# Revision 1.127  2008-12-01 12:36:13  ncq
# - much improved formatting
#
# Revision 1.126  2008/11/24 11:09:01  ncq
# - health issues now stem from a view
# - no more fk_patient in clin.health_issue
# - no more patient id in create_episode
#
# Revision 1.125  2008/11/20 18:40:53  ncq
# - health_issue/episode2problem
# - improved formatting
#
# Revision 1.124  2008/10/22 12:04:55  ncq
# - use %x in strftime
#
# Revision 1.123  2008/10/12 15:13:30  ncq
# - no more "foundational" in health issue
#
# Revision 1.122  2008/09/09 19:55:07  ncq
# - Jerzy found a misspelling
#
# Revision 1.121  2008/09/04 11:52:17  ncq
# - append an empty line per soap category
#
# Revision 1.120  2008/09/02 18:58:27  ncq
# - fk_patient dropped from clin.health_issue
#
# Revision 1.119  2008/08/17 18:13:39  ncq
# - add CRLF after date/time/provider in soap formatting as
#   suggested by Rogerio on the list
#
# Revision 1.118  2008/07/24 13:57:51  ncq
# - update/create/delete_encounter_type
#
# Revision 1.117  2008/07/22 13:53:12  ncq
# - cleanup
#
# Revision 1.116  2008/07/14 13:44:38  ncq
# - add .format to episode
# - factor out .format_soap from .format on encounter
# - better visualize soap sections in output as per user request
#
# Revision 1.115  2008/07/12 15:20:30  ncq
# - add format to health issue
#
# Revision 1.114  2008/06/26 21:17:59  ncq
# - episode formatting: include docs
# - encounter formatting: include results and docs
#
# Revision 1.113  2008/06/24 16:53:58  ncq
# - include test results in encounter formatting such
#   as to be included in the EMR tree browser :-)
#
# Revision 1.112  2008/05/19 15:43:45  ncq
# - adapt to TZ code changes
#
# Revision 1.111  2008/05/13 14:06:17  ncq
# - remove superfluous \n
# - add missing .
#
# Revision 1.110  2008/04/11 12:20:52  ncq
# - format() on episode and encounter
#
# Revision 1.109  2008/03/05 22:24:31  ncq
# - support fk_encounter in issue and episode creation
#
# Revision 1.108  2008/02/25 17:29:59  ncq
# - logging cleanup
#
# Revision 1.107  2008/01/30 13:34:49  ncq
# - switch to std lib logging
#
# Revision 1.106  2008/01/22 11:49:14  ncq
# - cleanup
# - free-standing -> Unattributed as per list
#
# Revision 1.105  2008/01/16 19:36:17  ncq
# - improve get_encounter_types()
#
# Revision 1.104  2008/01/13 01:12:53  ncq
# - age_noted_human_readable()
#
# Revision 1.103  2007/10/29 11:04:11  ncq
# - properly handle NULL pk_health_issue in create_apisode() thereby
#   finding dupes in free-standing episodes, too
# - this then asks for an explicit allow_dupes (defaulted to False)
#   in create_episode() as we may, indeed, wish to allow dupes
#   sometimes
#
# Revision 1.102  2007/10/11 12:00:17  ncq
# - add has_narrative() and has_documents()
#
# Revision 1.101  2007/09/07 10:55:55  ncq
# - get_dummy_health_issue()
#
# Revision 1.100  2007/08/15 14:56:30  ncq
# - delete_health_issue()
#
# Revision 1.99  2007/05/18 13:25:56  ncq
# - fix cEncounter.transfer_clinical_data()
#
# Revision 1.98  2007/05/14 10:32:50  ncq
# - raise DatabaseObjectInUseError on psycopg2 integrity error
#
# Revision 1.97  2007/04/27 22:54:13  ncq
# - when checking for existing episodes need to check
#   associated health issue, too, of course
#
# Revision 1.96  2007/04/02 18:35:20  ncq
# - create_encounter now more exception-y
#
# Revision 1.95  2007/03/18 13:01:55  ncq
# - a bit of cleanup
#
# Revision 1.94  2007/01/09 18:01:32  ncq
# - let exceptions report errors
#
# Revision 1.93  2007/01/09 12:56:02  ncq
# - create_episode() now always takes patient fk
#
# Revision 1.92  2007/01/04 22:50:04  ncq
# - allow changing fk_patient in cEpisode
#
# Revision 1.91  2007/01/02 16:14:41  ncq
# - fix close_expired_episode()
#
# Revision 1.90  2006/12/25 22:48:52  ncq
# - add cEncounter.has_clinical_data()
#
# Revision 1.89  2006/12/22 16:53:31  ncq
# - use timezone definition in gmDateTime
#
# Revision 1.88  2006/11/24 09:30:33  ncq
# - make cHealthIssue save more of its members
# - if_patient -> fk_patient
# - do not log i18n()ed message so failure there doesn't stop us from creating a health issue or episode
#
# Revision 1.87  2006/11/05 17:02:25  ncq
# - enable health issue and episode to be inited from row
#
# Revision 1.86  2006/10/28 14:59:38  ncq
# - __ -> _
#
# Revision 1.85  2006/10/28 14:59:20  ncq
# - when reading from views no need to explicitely load xmin_*, it's part of the view anyways
# - reduce query duplication by reuse of _cmd_fetch_payload
#
# Revision 1.84  2006/10/10 07:26:37  ncq
# - no more clinitem exceptions
#
# Revision 1.83  2006/10/09 12:18:18  ncq
# - convert to gmPG2
# - convert to cBusinessDBObject
# - unicode queries
# - robustified test suite
#
# Revision 1.82  2006/09/03 11:27:24  ncq
# - use gmNull.cNull
# - add cHealthIssue.get_open_episode()
# - add cEpisode.get_access_range()
#
# Revision 1.81  2006/07/19 20:25:00  ncq
# - gmPyCompat.py is history
#
# Revision 1.80  2006/06/26 12:27:53  ncq
# - cleanup
# - add close_episode() and has_open_episode() to cHealthIssue
#
# Revision 1.79  2006/06/05 22:00:53  ncq
# - must be "episode_open", not "is_open"
#
# Revision 1.78  2006/05/06 18:53:56  ncq
# - select age(...) <> ...; -> select ... <> now() - ...; as per Syan
#
# Revision 1.77  2006/03/09 21:11:49  ncq
# - spell out rfe/aoe
#
# Revision 1.76  2006/02/27 22:38:36  ncq
# - spell out rfe/aoe as per Richard's request
#
# Revision 1.75  2005/12/26 05:26:38  sjtan
#
# match schema
#
# Revision 1.74  2005/12/25 13:24:30  sjtan
#
# schema changes in names .
#
# Revision 1.73  2005/12/06 17:57:13  ncq
# - more id->pk fixes
#
# Revision 1.72  2005/12/06 14:24:14  ncq
# - clin.clin_health_issue/episode -> clin.health_issue/episode
#
# Revision 1.71  2005/11/27 12:56:19  ncq
# - add get_encounter_types()
#
# Revision 1.70  2005/11/27 12:44:57  ncq
# - clinical tables are in schema "clin" now
#
# Revision 1.69  2005/10/15 18:15:37  ncq
# - cleanup
# - clin_encounter has fk_*, not pk_*
# - remove clin_encounter.pk_provider support
# - fix cEncounter.set_active()
# - comment on that transfer_clinical_data will work but will not
#   notify others about its changes
#
# Revision 1.68  2005/10/12 22:31:13  ncq
# - encounter['rfe'] not mandatory anymore, hence don't need default
# - encounters don't have a provider
#
# Revision 1.67  2005/10/11 21:49:36  ncq
# - make create_encounter oblivious of emr object again
#
# Revision 1.66  2005/10/08 12:33:09  sjtan
# tree can be updated now without refetching entire cache; done by passing emr object to create_xxxx methods and calling emr.update_cache(key,obj);refresh_historical_tree non-destructively checks for changes and removes removed nodes and adds them if cache mismatch.
#
# Revision 1.65  2005/10/04 19:21:31  sjtan
# unicode and str are different but printable types.
#
# Revision 1.64  2005/09/25 01:00:47  ihaywood
# bugfixes
#
# remember 2.6 uses "import wx" not "from wxPython import wx"
# removed not null constraint on clin_encounter.rfe as has no value on instantiation
# client doesn't try to set clin_encounter.description as it doesn't exist anymore
#
# Revision 1.63  2005/09/22 15:45:11  ncq
# - clin_encounter.fk_provider removed
#
# Revision 1.62  2005/09/19 16:32:42  ncq
# - add rfe/aoe support to clin_encounter
# - remove get_aoes()/get_rfes()
#
# Revision 1.61  2005/09/12 15:05:58  ncq
# - improve close_expired_episodes()
#
# Revision 1.60  2005/09/11 17:23:53  ncq
# - close_expired_episodes()
# - support is_open when adding episode
#
# Revision 1.59  2005/08/22 13:02:46  ncq
# - prepare for 0.2
#
# Revision 1.58  2005/07/02 18:16:58  ncq
# - default encounter type "in surgery" for 0.1, to become
#   "in surgery"-on-write later on
#
# Revision 1.57  2005/06/23 14:58:51  ncq
# - clean up transfer_clinical_data()
#
# Revision 1.56  2005/06/20 18:48:51  ncq
# - a little cleanup in transfer_data
#
# Revision 1.55  2005/06/20 13:03:38  cfmoro
# Relink encounter to another episode
#
# Revision 1.54  2005/06/15 22:25:29  ncq
# - issue.rename()
#
# Revision 1.53  2005/06/14 18:53:37  ncq
# - really do rename in rename(), needs to set _is_modified to work
#
# Revision 1.52  2005/06/12 21:40:42  ncq
# - cleanup
#
# Revision 1.51  2005/05/14 15:05:40  ncq
# - show HH:MM in auto-created encounters
#
# Revision 1.50  2005/04/25 08:28:28  ncq
# - episode now has .description
#
# Revision 1.49  2005/04/24 14:42:22  ncq
# - add age_noted as changable
#
# Revision 1.48  2005/04/03 20:05:38  ncq
# - cEpisode.set_active() doesn't make sense no more
#
# Revision 1.47  2005/03/29 07:22:38  ncq
# - improve text for auto generated encounters
#
# Revision 1.46  2005/03/23 18:31:19  ncq
# - v_patient_items -> v_pat_items
#
# Revision 1.45  2005/03/20 16:47:26  ncq
# - cleanup
#
# Revision 1.44  2005/03/17 21:59:35  cfmoro
# Fixed log comment
#
# Revision 1.43  2005/03/17 21:46:23  cfmoro
# Simplified cEpisode.rename function
#
# Revision 1.42  2005/03/17 21:14:45  cfmoro
# Improved exception handling in get_as_episode.
#
# Revision 1.41  2005/03/17 13:35:52  ncq
# - cleanup and streamlining
#
# Revision 1.40  2005/03/16 19:10:06  cfmoro
# Added cProblem.get_as_episode method
#
# Revision 1.39  2005/03/14 14:28:54  ncq
# - id_patient -> pk_patient
# - properly handle simplified episode naming in create_episode()
#
# Revision 1.38  2005/03/08 16:42:47  ncq
# - there are episodes w/ and w/o fk_patient IS NULL so handle that
#   properly in set_active()
#
# Revision 1.37  2005/02/28 18:15:36  ncq
# - proper fix for not being able to fetch unnamed episodes
#   is to require a name in the first place ...
#
# Revision 1.36  2005/02/20 10:30:49  sjtan
#
# unnamed episodes cannot be refetched.
#
# Revision 1.35  2005/01/31 12:58:24  ncq
# - episode.rename() finally works
#
# Revision 1.34  2005/01/31 09:35:28  ncq
# - add episode.get_description() to return clin_narrative row
# - improve episode.rename() - works for adding new narrative now
# - improve create_episode() - revise later
# - improve unit testing
#
# Revision 1.33  2005/01/29 17:53:57  ncq
# - debug/enhance create_episode
#
# Revision 1.32  2005/01/25 17:24:57  ncq
# - streamlined cEpisode.rename()
#
# Revision 1.31  2005/01/25 01:36:19  cfmoro
# Added cEpisode.rename method
#
# Revision 1.30  2005/01/15 20:24:35  ncq
# - streamlined cProblem
#
# Revision 1.29  2005/01/15 19:55:55  cfmoro
# Added problem support to emr
#
# Revision 1.28  2005/01/02 19:55:30  ncq
# - don't need _xmins_refetch_col_pos anymore
#
# Revision 1.27  2004/12/20 16:45:49  ncq
# - gmBusinessDBObject now requires refetching of XMIN after save_payload
#
# Revision 1.26  2004/12/15 10:42:09  ncq
# - cClinEpisode not handles the fields properly
#
# Revision 1.25  2004/12/15 10:28:11  ncq
# - fix create_episode() aka add_episode()
#
# Revision 1.24  2004/11/03 22:32:34  ncq
# - support _cmds_lock_rows_for_update in business object base class
#
# Revision 1.23  2004/09/19 15:02:29  ncq
# - episode: id -> pk, support fk_patient
# - no default name in create_health_issue
#
# Revision 1.22  2004/07/05 10:24:46  ncq
# - use v_pat_rfe/aoe, by Carlos
#
# Revision 1.21  2004/07/04 15:09:40  ncq
# - when refactoring need to fix imports, too
#
# Revision 1.20  2004/07/04 13:24:31  ncq
# - add cRFE/cAOE
# - use in get_rfes(), get_aoes()
#
# Revision 1.19  2004/06/30 20:34:37  ncq
# - cEncounter.get_RFEs()
#
# Revision 1.18  2004/06/26 23:45:50  ncq
# - cleanup, id_* -> fk/pk_*
#
# Revision 1.17  2004/06/26 07:33:55  ncq
# - id_episode -> fk/pk_episode
#
# Revision 1.16  2004/06/08 00:44:41  ncq
# - v_pat_episodes now has description, not episode for name of episode
#
# Revision 1.15  2004/06/02 22:12:48  ncq
# - cleanup
#
# Revision 1.14  2004/06/02 13:45:19  sjtan
#
# episode->description for update statement as well.
#
# Revision 1.13  2004/06/02 13:18:48  sjtan
#
# revert, as backend view definition was changed yesterday to be more consistent.
#
# Revision 1.12  2004/06/02 12:48:56  sjtan
#
# map episode to description in cursor.description, so can find as episode['description']
# and also save.
#
# Revision 1.11  2004/06/01 23:53:56  ncq
# - v_pat_episodes.episode -> *.description
#
# Revision 1.10  2004/06/01 08:20:14  ncq
# - limit in get_lab_results
#
# Revision 1.9  2004/05/30 20:10:31  ncq
# - cleanup
#
# Revision 1.8  2004/05/22 12:42:54  ncq
# - add create_episode()
# - cleanup add_episode()
#
# Revision 1.7  2004/05/18 22:36:52  ncq
# - need mx.DateTime
# - fix fields updatable in episode
# - fix delete action in episode.set_active()
#
# Revision 1.6  2004/05/18 20:35:42  ncq
# - cleanup
#
# Revision 1.5  2004/05/17 19:02:26  ncq
# - encounter.set_active()
# - improve create_encounter()
#
# Revision 1.4  2004/05/16 15:47:51  ncq
# - add episode.set_active()
#
# Revision 1.3  2004/05/16 14:31:27  ncq
# - cleanup
# - allow health issue to be instantiated by name/patient
# - create_health_issue()/create_encounter
# - based on Carlos' work
#
# Revision 1.2  2004/05/12 14:28:53  ncq
# - allow dict style pk definition in __init__ for multicolum primary keys (think views)
# - self.pk -> self.pk_obj
# - __init__(aPKey) -> __init__(aPK_obj)
#
# Revision 1.1  2004/04/17 12:18:50  ncq
# - health issue, episode, encounter classes
#
