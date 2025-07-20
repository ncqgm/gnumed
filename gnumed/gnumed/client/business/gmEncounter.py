# -*- coding: utf-8 -*-
"""GNUmed clinical encounter handling.

license: GPL v2 or later
"""
#============================================================
__author__ = "Carlos Moro <cfmoro1976@yahoo.es>, <karsten.hilbert@gmx.net>"

import sys
import logging
import inspect


if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x
from Gnumed.pycommon import gmPG2
from Gnumed.pycommon import gmI18N
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmDateTime
from Gnumed.pycommon import gmBusinessDBObject

from Gnumed.business import gmSoapDefs
from Gnumed.business import gmCoding
from Gnumed.business import gmPraxis
from Gnumed.business import gmOrganization


_log = logging.getLogger('gm.emr.enc')
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

		SQL = """
			UPDATE clin.clin_root_item
			SET fk_episode = %(trg)s
 			WHERE
				fk_encounter = %(enc)s AND
				fk_episode = %(src)s
			"""
		args = {
			'trg': target_episode['pk_episode'],
			'enc': self.pk_obj,
			'src': source_episode['pk_episode']
		}
		gmPG2.run_rw_queries(queries = [{'sql': SQL, 'args': args}])
		self.refetch_payload()
		return True

	#--------------------------------------------------------
	def transfer_all_data_to_another_encounter(self, pk_target_encounter=None):
		if pk_target_encounter == self.pk_obj:
			return True

		SQL = "SELECT clin.transfer_all_encounter_data(%(src)s, %(trg)s)"
		args = {
			'src': self.pk_obj,
			'trg': pk_target_encounter
		}
		gmPG2.run_rw_queries(queries = [{'sql': SQL, 'args': args}])
		return True

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
			if self._payload[field] != another_object[field]:
				_log.debug('mismatch on [%s]: "%s" vs. "%s"', field, self._payload[field], another_object[field])
				return False

		relevant_fields = [
			'started',
			'last_affirmed',
		]
		for field in relevant_fields:
			if self._payload[field] is None:
				if another_object[field] is None:
					continue
				_log.debug('mismatch on [%s]: here="%s", other="%s"', field, self._payload[field], another_object[field])
				return False

			if another_object[field] is None:
				return False

			# compares at seconds granularity
			if self._payload[field].strftime('%Y-%m-%d %H:%M:%S') != another_object[field].strftime('%Y-%m-%d %H:%M:%S'):
				_log.debug('mismatch on [%s]: here="%s", other="%s"', field, self._payload[field], another_object[field])
				return False

		# compare codes
		# 1) RFE
		if another_object['pk_generic_codes_rfe'] is None:
			if self._payload['pk_generic_codes_rfe'] is not None:
				return False
		if another_object['pk_generic_codes_rfe'] is not None:
			if self._payload['pk_generic_codes_rfe'] is None:
				return False
		if (
			(another_object['pk_generic_codes_rfe'] is None)
				and
			(self._payload['pk_generic_codes_rfe'] is None)
		) is False:
			if set(another_object['pk_generic_codes_rfe']) != set(self._payload['pk_generic_codes_rfe']):
				return False
		# 2) AOE
		if another_object['pk_generic_codes_aoe'] is None:
			if self._payload['pk_generic_codes_aoe'] is not None:
				return False
		if another_object['pk_generic_codes_aoe'] is not None:
			if self._payload['pk_generic_codes_aoe'] is None:
				return False
		if (
			(another_object['pk_generic_codes_aoe'] is None)
				and
			(self._payload['pk_generic_codes_aoe'] is None)
		) is False:
			if set(another_object['pk_generic_codes_aoe']) != set(self._payload['pk_generic_codes_aoe']):
				return False

		return True

	#--------------------------------------------------------
	def has_clinical_data(self):
		SQL = """SELECT EXISTS (
			SELECT 1 FROM clin.v_pat_items WHERE pk_patient = %(pat)s and pk_encounter = %(enc)s
				UNION ALL
			SELECT 1 FROM blobs.v_doc_med WHERE pk_patient = %(pat)s and pk_encounter = %(enc)s
		)"""
		args = {
			'pat': self._payload['pk_patient'],
			'enc': self.pk_obj
		}
		rows = gmPG2.run_ro_queries(queries = [{'sql': SQL, 'args': args}])
		return rows[0][0]

	#--------------------------------------------------------
	def has_narrative(self):
		SQL = "SELECT EXISTS (SELECT 1 FROM clin.v_pat_items WHERE pk_patient=%(pat)s and pk_encounter=%(enc)s)"
		args = {
			'pat': self._payload['pk_patient'],
			'enc': self.pk_obj
		}
		rows = gmPG2.run_ro_queries(queries = [{'sql': SQL,	'args': args}])
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
		SQL = """SELECT EXISTS (
			SELECT 1 FROM clin.clin_narrative
			WHERE
				fk_encounter = %(enc)s
					AND
				soap_cat = ANY(%(cats)s)
			LIMIT 1
		)"""
		args = {'enc': self._payload['pk_encounter'], 'cats': cats}
		rows = gmPG2.run_ro_queries(queries = [{'sql': SQL, 'args': args}])
		return rows[0][0]

	#--------------------------------------------------------
	def has_documents(self):
		SQL = "SELECT EXISTS (SELECT 1 FROM blobs.v_doc_med WHERE pk_patient = %(pat)s and pk_encounter = %(enc)s)"
		args = {
			'pat': self._payload['pk_patient'],
			'enc': self.pk_obj
		}
		rows = gmPG2.run_ro_queries (queries = [{'sql': SQL,'args': args}])
		return rows[0][0]

	#--------------------------------------------------------
	def get_latest_soap(self, soap_cat=None, episode=None):

		if soap_cat is not None:
			soap_cat = soap_cat.casefold()
		if episode is None:
			epi_part = 'fk_episode is null'
		else:
			epi_part = 'fk_episode = %(epi)s'
		SQL = """
			SELECT narrative
			FROM clin.clin_narrative
			where
				fk_encounter = %%(enc)s
					and
				soap_cat = %%(cat)s
					and
				%s
			order by clin_when desc
			limit 1""" % epi_part
		args = {'enc': self.pk_obj, 'cat': soap_cat, 'epi': episode}
		rows = gmPG2.run_ro_queries(queries = [{'sql': SQL, 'args': args}])
		if len(rows) == 0:
			return None

		return rows[0][0]
	#--------------------------------------------------------
	def get_episodes(self, exclude=None):
		"""exclude: list of episode PKs to exclude"""
		args = {'enc': self.pk_obj}
		extra_where_parts = ''
		if exclude is not None:
			extra_where_parts = 'AND pk_episode <> ALL(%(excluded_pks)s)'
			args['excluded_pks'] = exclude
		SQL = """
			SELECT * FROM clin.v_pat_episodes
			WHERE pk_episode IN (
					SELECT DISTINCT fk_episode
					FROM clin.clin_root_item
					WHERE fk_encounter = %%(enc)s

						UNION

					SELECT DISTINCT fk_episode
					FROM blobs.doc_med
					WHERE fk_encounter = %%(enc)s
			) %s""" % extra_where_parts
		rows = gmPG2.run_ro_queries(queries = [{'sql': SQL, 'args': args}])
		from Gnumed.business.gmEpisode import cEpisode
		return [ cEpisode(row = {'data': r, 'pk_field': 'pk_episode'})  for r in rows ]

	episodes = property(get_episodes)

	#--------------------------------------------------------
	def add_code(self, pk_code=None, field=None):
		"""<pk_code> must be a value FROM ref.coding_system_root.pk_coding_system (clin.lnk_code2item_root.fk_generic_code)"""
		if field == 'rfe':
			cmd = "INSERT INTO clin.lnk_code2rfe (fk_item, fk_generic_code) VALUES (%(item)s, %(code)s)"
		elif field == 'aoe':
			cmd = "INSERT INTO clin.lnk_code2aoe (fk_item, fk_generic_code) VALUES (%(item)s, %(code)s)"
		else:
			raise ValueError('<field> must be one of "rfe" or "aoe", not "%s"', field)
		args = {
			'item': self._payload['pk_encounter'],
			'code': pk_code
		}
		gmPG2.run_rw_queries(queries = [{'sql': cmd, 'args': args}])
		return True

	#--------------------------------------------------------
	def remove_code(self, pk_code=None, field=None):
		"""<pk_code> must be a value FROM ref.coding_system_root.pk_coding_system (clin.lnk_code2item_root.fk_generic_code)"""
		if field == 'rfe':
			cmd = "DELETE FROM clin.lnk_code2rfe WHERE fk_item = %(item)s AND fk_generic_code = %(code)s"
		elif field == 'aoe':
			cmd = "DELETE FROM clin.lnk_code2aoe WHERE fk_item = %(item)s AND fk_generic_code = %(code)s"
		else:
			raise ValueError('<field> must be one of "rfe" or "aoe", not "%s"', field)
		args = {
			'item': self._payload['pk_encounter'],
			'code': pk_code
		}
		gmPG2.run_rw_queries(queries = [{'sql': cmd, 'args': args}])
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
				encounters = [self._payload['pk_encounter']],
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
				txt = '%s%s %.8s, %s %s' % (
					' ' * 40,
					gmTools.u_box_horiz_light_heavy,
					soap_entry['modified_by'],
					soap_entry['date'].strftime('%Y-%m-%d %H:%M'),
					gmTools.u_box_horiz_heavy_light
				)
				lines.append(txt)
				lines.append('')

		return lines

	#--------------------------------------------------------
	def format_latex(self, date_format=None, soap_cats=None, soap_order=None):

		nothing2format = (
			(self._payload['reason_for_encounter'] is None)
				and
			(self._payload['assessment_of_encounter'] is None)
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
			gmTools.tex_escape_string(self._payload['l10n_type']),
			gmTools.tex_escape_string(self._payload['started'].strftime(date_format)),
			gmTools.tex_escape_string(self._payload['started'].strftime('%H:%M')),
			gmTools.tex_escape_string(self._payload['last_affirmed'].strftime('%H:%M'))
		)
		tex += '\\hline \n'

		if self._payload['reason_for_encounter'] is not None:
			tex += '%s & %s \\tabularnewline \n' % (
				gmTools.tex_escape_string(_('RFE')),
				gmTools.tex_escape_string(self._payload['reason_for_encounter'])
			)
		if self._payload['assessment_of_encounter'] is not None:
			tex += '%s & %s \\tabularnewline \n' % (
				gmTools.tex_escape_string(_('AOE')),
				gmTools.tex_escape_string(self._payload['assessment_of_encounter'])
			)

		from Gnumed.business.gmHealthIssue import diagnostic_certainty_classification2str
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
			self._payload['l10n_type'],
			self._payload['started_original_tz'].strftime('%Y-%m-%d %H:%M'),
			self._payload['last_affirmed_original_tz'].strftime('%H:%M'),
			self._payload['source_time_zone'],
			gmTools.coalesce (
				self._payload['assessment_of_encounter'],
				'',
				' %s%%s%s' % (gmTools.u_left_double_angle_quote, gmTools.u_right_double_angle_quote)
			),
			self._payload['pk_encounter']
		))

		lines.append(_('  your time: %s - %s  (@%s = %s%s)\n') % (
			self._payload['started'].strftime('%Y-%m-%d %H:%M'),
			self._payload['last_affirmed'].strftime('%H:%M'),
			gmDateTime.current_local_timezone_name,
			gmTools.bool2subst (
				gmDateTime.dst_currently_in_effect,
				gmDateTime.py_dst_timezone_name,
				gmDateTime.py_timezone_name
			),
			gmTools.bool2subst(gmDateTime.dst_currently_in_effect, ' - ' + _('daylight savings time in effect'), '')
		))

		if self._payload['praxis_branch'] is not None:
			lines.append(_('Location: %s (%s)') % (self._payload['praxis_branch'], self._payload['praxis']))

		if self._payload['reason_for_encounter'] is not None:
			lines.append('%s: %s' % (_('RFE'), self._payload['reason_for_encounter']))
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

		if self._payload['assessment_of_encounter'] is not None:
			lines.append('%s: %s' % (_('AOE'), self._payload['assessment_of_encounter']))
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
		if now.strftime('%Y-%m-%d') == self._payload['started_original_tz'].strftime('%Y-%m-%d'):
			start = '%s %s' % (
				_('today'),
				self._payload['started_original_tz'].strftime('%H:%M')
			)
		else:
			start = self._payload['started_original_tz'].strftime('%Y-%m-%d %H:%M')
		lines.append('%s%s: %s - %s%s%s' % (
			' ' * left_margin,
			self._payload['l10n_type'],
			start,
			self._payload['last_affirmed_original_tz'].strftime('%H:%M'),
			gmTools.coalesce(self._payload['assessment_of_encounter'], '', ' \u00BB%s\u00AB'),
			gmTools.coalesce(self._payload['praxis_branch'], '', ' @%s')
		))
		if with_rfe_aoe:
			if self._payload['reason_for_encounter'] is not None:
				lines.append('%s: %s' % (_('RFE'), self._payload['reason_for_encounter']))
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
			if self._payload['assessment_of_encounter'] is not None:
				lines.append('%s: %s' % (_('AOE'), self._payload['assessment_of_encounter']))
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

		from Gnumed.business.gmEpisode import cEpisode
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
				if patient.ID != self._payload['pk_patient']:
					msg = '<patient>.ID = %s but encounter %s belongs to patient %s' % (
						patient.ID,
						self._payload['pk_encounter'],
						self._payload['pk_patient']
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
					encounter = self._payload['pk_encounter']
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
					encounters = [ self._payload['pk_encounter'] ],
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
					encounter = self._payload['pk_encounter']
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
			if self._payload['pk_patient'] == gmCurrentPatient().ID:
				patient = gmCurrentPatient()
			else:
				patient = cPerson(self._payload['pk_patient'])

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

		Args:
			episode: which episodes, touched upon by this encounter, to include information for
			with_co_encountlet_hints:
				- whether to include which *other* episodes were discussed during this encounter
				- (only makes sense if episodes is not None, since that would preclude information)
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
				if patient.ID != self._payload['pk_patient']:
					msg = '<patient>.ID = %s but encounter %s belongs to patient %s' % (
						patient.ID,
						self._payload['pk_encounter'],
						self._payload['pk_patient']
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
					encounter = self._payload['pk_encounter']
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
					encounters = [ self._payload['pk_encounter'] ],
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
					encounter = self._payload['pk_encounter']
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
		if len(self._payload['pk_generic_codes_rfe']) == 0:
			return []

		cmd = gmCoding._SQL_get_generic_linked_codes % 'pk_generic_code = ANY(%(pks)s)'
		args = {'pks': self._payload['pk_generic_codes_rfe']}
		rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
		return [ gmCoding.cGenericLinkedCode(row = {'data': r, 'pk_field': 'pk_lnk_code2item'}) for r in rows ]

	def _set_generic_codes_rfe(self, pk_codes):
		queries = []
		# remove all codes
		if len(self._payload['pk_generic_codes_rfe']) > 0:
			queries.append ({
				'sql': 'DELETE FROM clin.lnk_code2rfe WHERE fk_item = %(enc)s AND fk_generic_code = ANY(%(codes)s)',
				'args': {
					'enc': self._payload['pk_encounter'],
					'codes': self._payload['pk_generic_codes_rfe']
				}
			})
		# add new codes
		for pk_code in pk_codes:
			queries.append ({
				'sql': 'INSERT INTO clin.lnk_code2rfe (fk_item, fk_generic_code) VALUES (%(enc)s, %(pk_code)s)',
				'args': {
					'enc': self._payload['pk_encounter'],
					'pk_code': pk_code
				}
			})
		if len(queries) == 0:
			return
		# run it all in one transaction
		gmPG2.run_rw_queries(queries = queries)
		self.refetch_payload()
		return

	generic_codes_rfe = property(_get_generic_codes_rfe, _set_generic_codes_rfe)
	#--------------------------------------------------------
	def _get_generic_codes_aoe(self):
		if len(self._payload['pk_generic_codes_aoe']) == 0:
			return []

		cmd = gmCoding._SQL_get_generic_linked_codes % 'pk_generic_code = ANY(%(pks)s)'
		args = {'pks': self._payload['pk_generic_codes_aoe']}
		rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
		return [ gmCoding.cGenericLinkedCode(row = {'data': r, 'pk_field': 'pk_lnk_code2item'}) for r in rows ]

	def _set_generic_codes_aoe(self, pk_codes):
		queries = []
		# remove all codes
		if len(self._payload['pk_generic_codes_aoe']) > 0:
			queries.append ({
				'sql': 'DELETE FROM clin.lnk_code2aoe WHERE fk_item = %(enc)s AND fk_generic_code = ANY(%(codes)s)',
				'args': {
					'enc': self._payload['pk_encounter'],
					'codes': self._payload['pk_generic_codes_aoe']
				}
			})
		# add new codes
		for pk_code in pk_codes:
			queries.append ({
				'sql': 'INSERT INTO clin.lnk_code2aoe (fk_item, fk_generic_code) VALUES (%(enc)s, %(pk_code)s)',
				'args': {
					'enc': self._payload['pk_encounter'],
					'pk_code': pk_code
				}
			})
		if len(queries) == 0:
			return
		# run it all in one transaction
		gmPG2.run_rw_queries(queries = queries)
		self.refetch_payload()
		return

	generic_codes_aoe = property(_get_generic_codes_aoe, _set_generic_codes_aoe)
	#--------------------------------------------------------
	def _get_praxis_branch(self):
		if self._payload['pk_org_unit'] is None:
			return None
		return gmPraxis.get_praxis_branch_by_org_unit(pk_org_unit = self._payload['pk_org_unit'])

	praxis_branch = property(_get_praxis_branch)
	#--------------------------------------------------------
	def _get_org_unit(self):
		if self._payload['pk_org_unit'] is None:
			return None
		return gmOrganization.cOrgUnit(aPK_obj = self._payload['pk_org_unit'])

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
		args = {'pk_encounter': self._payload['pk_encounter']}
		title = _('Encounter: %s%s%s') % (
			gmTools.u_left_double_angle_quote,
			self._payload['l10n_type'],
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
					(SELECT pk FROM clin.encounter_type WHERE description = %(typ)s),
					-- pick the first available
					(SELECT pk FROM clin.encounter_type limit 1)
				)
			) RETURNING pk"""
	praxis = gmPraxis.gmCurrentPraxisBranch()
	args = {'pat': fk_patient, 'typ': enc_type, 'prax': praxis['pk_org_unit']}
	queries.append({'sql': cmd, 'args': args})
	rows = gmPG2.run_rw_queries(queries = queries, return_data = True)
	return cEncounter(aPK_obj = rows[0]['pk'])

#------------------------------------------------------------
def lock_encounter(pk_encounter, exclusive=False, link_obj=None):
	"""Used to protect against deletion of active encounter FROM another client."""
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

	SQL = "DELETE FROM clin.encounter WHERE pk = %(enc)s"
	args = {'enc': pk_encounter}
	try:
		gmPG2.run_rw_queries(queries = [{'sql': SQL, 'args': args}])
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
	SQL = "SELECT i18n.upd_tx(%(desc)s, %(l10n_desc)s)"
	args = {'desc': description, 'l10n_desc': l10n_description}
	rows = gmPG2.run_rw_queries(queries = [{'sql': SQL, 'args': args}], return_data = True)
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
	cmd = "SELECT description, _(description) FROM clin.encounter_type WHERE description = %(desc)s"
	rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])

	# yes
	if len(rows) > 0:
		# both system and l10n name are the same so all is well
		if (rows[0][0] == description) and (rows[0][1] == l10n_description):
			_log.info('encounter type [%s] already exists with the proper translation')
			return {'description': description, 'l10n_description': l10n_description}

		# or maybe there just wasn't a translation to
		# the current language for this type yet ?
		cmd = "SELECT EXISTS (SELECT 1 FROM i18n.translations WHERE orig = %(desc)s and lang = i18n.get_curr_lang())"
		rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])

		# there was, so fail
		if rows[0][0]:
			_log.error('encounter type [%s] already exists but with another translation')
			return None

		# else set it
		cmd = "SELECT i18n.upd_tx(%(desc)s, %(l10n_desc)s)"
		rows = gmPG2.run_rw_queries(queries = [{'sql': cmd, 'args': args}])
		return {'description': description, 'l10n_description': l10n_description}

	# no
	queries = [
		{'sql': "INSERT INTO clin.encounter_type (description) VALUES (%(desc)s)", 'args': args},
		{'sql': "SELECT i18n.upd_tx(%(desc)s, %(l10n_desc)s)", 'args': args}
	]
	rows = gmPG2.run_rw_queries(queries = queries)

	return {'description': description, 'l10n_description': l10n_description}

#-----------------------------------------------------------
def get_most_commonly_used_encounter_type():
	SQL = """
		SELECT
			COUNT(*) AS type_count,
			fk_type
		FROM clin.encounter
		GROUP BY fk_type
		ORDER BY type_count DESC
		LIMIT 1
	"""
	rows = gmPG2.run_ro_queries(queries = [{'sql': SQL}])
	if len(rows) == 0:
		return None

	return rows[0]['fk_type']

#-----------------------------------------------------------
def get_encounter_types():
	SQL = """
		SELECT
			_(description) AS l10n_description,
			description
		FROM
			clin.encounter_type
		ORDER BY
			l10n_description
	"""
	rows = gmPG2.run_ro_queries(queries = [{'sql': SQL}])
	return rows

#-----------------------------------------------------------
def get_encounter_type(description:str=None):
	SQL = 'SELECT * FROM clin.encounter_type WHERE description = %(desc)s'
	args = {'desc': description}
	rows = gmPG2.run_ro_queries(queries = [{'sql': SQL, 'args': args}])
	return rows

#-----------------------------------------------------------
def delete_encounter_type(description:str=None):
	deleted = False
	SQL = "DELETE FROM clin.encounter_type WHERE description = %(desc)s"
	args = {'desc': description}
	try:
		gmPG2.run_rw_queries(queries = [{'sql': SQL, 'args': args}])
		deleted = True
	except gmPG2.dbapi.IntegrityError as e:
		if e.pgcode != gmPG2.PG_error_codes.FOREIGN_KEY_VIOLATION:
			raise

	return deleted

#============================================================

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
	gmPG2.request_login_params(setup_pool = True)

	#test_encounter()
	test_encounter2latex()
