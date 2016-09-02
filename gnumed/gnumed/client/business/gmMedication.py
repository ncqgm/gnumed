# -*- coding: utf-8 -*-
"""Medication handling code.

license: GPL v2 or later
"""
#============================================================
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"

import sys
import logging
import io
import uuid
import re as regex
import datetime as pydt


if __name__ == '__main__':
	sys.path.insert(0, '../../')
	from Gnumed.pycommon import gmI18N
	gmI18N.activate_locale()
	gmI18N.install_domain('gnumed')
from Gnumed.pycommon import gmBusinessDBObject
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmPG2
from Gnumed.pycommon import gmDispatcher
from Gnumed.pycommon import gmMatchProvider
from Gnumed.pycommon import gmHooks
from Gnumed.pycommon import gmDateTime

from Gnumed.business import gmATC
from Gnumed.business import gmAllergy
from Gnumed.business import gmEMRStructItems


_log = logging.getLogger('gm.meds')

#_ = lambda x:x
DEFAULT_MEDICATION_HISTORY_EPISODE = _('Medication history')

#============================================================
def _on_substance_intake_modified():
	"""Always relates to the active patient."""
	gmHooks.run_hook_script(hook = u'after_substance_intake_modified')

gmDispatcher.connect(_on_substance_intake_modified, u'clin.substance_intake_mod_db')

#============================================================
def drug2renal_insufficiency_url(search_term=None):

	if search_term is None:
		return u'http://www.dosing.de'

	if isinstance(search_term, basestring):
		if search_term.strip() == u'':
			return u'http://www.dosing.de'

	terms = []
	names = []

	if isinstance(search_term, cBrandedDrug):
		if search_term['atc'] is not None:
			terms.append(search_term['atc'])

	elif isinstance(search_term, cSubstanceIntakeEntry):
		names.append(search_term['substance'])
		if search_term['atc_brand'] is not None:
			terms.append(search_term['atc_brand'])
		if search_term['atc_substance'] is not None:
			terms.append(search_term['atc_substance'])

	elif isinstance(search_term, cDrugComponent):
		names.append(search_term['substance'])
		if search_term['atc_brand'] is not None:
			terms.append(search_term['atc_brand'])
		if search_term['atc_substance'] is not None:
			terms.append(search_term['atc_substance'])

	elif isinstance(search_term, cConsumableSubstance):
		names.append(search_term['description'])
		if search_term['atc_code'] is not None:
			terms.append(search_term['atc_code'])

	elif search_term is not None:
		names.append(u'%s' % search_term)
		terms.extend(gmATC.text2atc(text = u'%s' % search_term, fuzzy = True))

	for name in names:
		if name.endswith('e'):
			terms.append(name[:-1])
		else:
			terms.append(name)

	#url_template = u'http://www.google.de/#q=site%%3Adosing.de+%s'
	#url = url_template % u'+OR+'.join(terms)

	url_template = u'http://www.google.com/search?hl=de&source=hp&q=site%%3Adosing.de+%s&btnG=Google-Suche'
	url = url_template % u'+OR+'.join(terms)

	_log.debug(u'renal insufficiency URL: %s', url)

	return url

#============================================================
#============================================================
# substances in use across all patients
#------------------------------------------------------------
_SQL_get_substance = u"SELECT *, xmin FROM ref.substance WHERE %s"

class cSubstance(gmBusinessDBObject.cBusinessDBObject):

	_cmd_fetch_payload = _SQL_get_substance % u"pk = %s"
	_cmds_store_payload = [
		u"""UPDATE ref.substance SET
				description = %(description)s,
				atc = gm.nullify_empty_string(%(atc)s),
				intake_instructions = gm.nullify_empty_string(%(intake_instructions)s)
			WHERE
				pk = %(pk)s
					AND
				xmin = %(xmin)s
			RETURNING
				xmin
		"""
	]
	_updatable_fields = [
		u'description',
		u'atc',
		u'intake_instructions'
	]
	#--------------------------------------------------------
	def format(self, left_margin=0):
		return (u' ' * left_margin) + u'%s: %s%s%s' % (
			_('Substance'),
			self._payload[self._idx['description']],
			gmTools.coalesce(self._payload[self._idx['atc']], u'', u' [%s]'),
			gmTools.coalesce(self._payload[self._idx['intake_instructions']], u'', _(u'\n Instructions: %s'))
		)

	#--------------------------------------------------------
	def save_payload(self, conn=None):
		success, data = super(self.__class__, self).save_payload(conn = conn)

		if not success:
			return (success, data)

		if self._payload[self._idx['atc']] is not None:
			atc = self._payload[self._idx['atc']].strip()
			if atc != u'':
				gmATC.propagate_atc (
					substance = self._payload[self._idx['description']].strip(),
					atc = atc
				)

		return (success, data)
	#--------------------------------------------------------
	def exists_as_intake(self, pk_patient=None):
		return substance_intake_exists (
			pk_substance = self.pk_obj,
			pk_identity = pk_patient
		)

	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def _get_is_in_use_by_patients(self):
		cmd = u"""
			SELECT EXISTS (
				SELECT 1
				FROM clin.v_substance_intakes
				WHERE pk_substance = %(pk)s
				LIMIT 1
			)"""
		args = {'pk': self.pk_obj}

		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = False)
		return rows[0][0]

	is_in_use_by_patients = property(_get_is_in_use_by_patients, lambda x:x)
	#--------------------------------------------------------
	def _get_is_drug_component(self):
		cmd = u"""
			SELECT EXISTS (
				SELECT 1
				FROM ref.v_drug_components
				WHERE pk_substance = %(pk)s
				LIMIT 1
			)"""
		args = {'pk': self.pk_obj}

		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = False)
		return rows[0][0]

	is_drug_component = property(_get_is_drug_component, lambda x:x)

#------------------------------------------------------------
def get_substances(order_by=None):
	if order_by is None:
		order_by = u'true'
	else:
		order_by = u'true ORDER BY %s' % order_by
	cmd = _SQL_get_substance % order_by
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd}], get_col_idx = True)
	return [ cSubstance(row = {'data': r, 'idx': idx, 'pk_field': 'pk'}) for r in rows ]

#------------------------------------------------------------
def create_substance(substance=None, atc=None):
	if atc is not None:
		atc = atc.strip()

	args = {
		'desc': substance.strip(),
		'atc': atc
	}
	cmd = u"SELECT pk FROM ref.substance WHERE lower(description) = lower(%(desc)s)"
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}])

	if len(rows) == 0:
		cmd = u"""
			INSERT INTO ref.substance (description, atc) VALUES (
				%(desc)s,
				gm.nullify_empty_string(%(atc)s)
			) RETURNING pk"""
		rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}], return_data = True, get_col_idx = False)

	gmATC.propagate_atc(substance = substance, atc = atc)

	return cSubstance(aPK_obj = rows[0]['pk'])

#------------------------------------------------------------
def create_substance_by_atc(substance=None, atc=None):

	if atc is None:
		raise ValueError('<atc> must be supplied')
	atc = atc.strip()
	if atc == u'':
		raise ValueError('<atc> cannot be empty: [%s]', atc)
	args = {
		'desc': substance.strip(),
		'atc': atc
	}
	cmd = u"""
		INSERT INTO ref.substance (description, atc)
			SELECT
				%(desc)s,
				%(atc)s
			WHERE NOT EXISTS (
				SELECT 1 FROM ref.substance WHERE atc = %(atc)s
			)
		RETURNING pk"""
	rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}], return_data = True, get_col_idx = False)
	if len(rows) == 0:
		cmd = u"SELECT pk FROM ref.substance WHERE atc = %(atc)s LIMIT 1"
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}])

	return cSubstance(aPK_obj = rows[0]['pk'])

#------------------------------------------------------------
def delete_substance(pk_substance=None):
	args = {'pk': pk_substance}
	cmd = u"""
		DELETE FROM ref.substance WHERE
			pk = %(pk)s
				AND
			-- must not currently be used with a patient
			NOT EXISTS (
				SELECT 1 FROM clin.v_substance_intakes
				WHERE pk_substance = %(pk)s
				LIMIT 1
			)
				AND
			-- must not currently have doses defined for it
			NOT EXISTS (
				SELECT 1 FROM ref.dose
				WHERE fk_substance = %(pk)s
				LIMIT 1
			)
	"""
	gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])
	return True

#------------------------------------------------------------
class cSubstanceDoseMatchProvider(gmMatchProvider.cMatchProvider_SQL2):

	_pattern = regex.compile(r'^\D+\s*\d+$', regex.UNICODE | regex.LOCALE)

	_normal_query = u"""
		SELECT
			data,
			field_label,
			list_label,
			rank
		FROM ((
			-- first: substance intakes which match
			SELECT
				pk_substance AS data,
				(description || ' ' || amount || ' ' || unit) AS field_label,
				(description || ' ' || amount || ' ' || unit || ' (%s)') AS list_label,
				1 AS rank
			FROM (
				SELECT DISTINCT ON (description, amount, unit)
					pk_substance,
					substance AS description,
					amount,
					unit
				FROM clin.v_nonbrand_intakes
			) AS normalized_intakes
			WHERE description %%(fragment_condition)s
		) UNION ALL (
			-- consumable substances which match - but are not intakes - are second
			SELECT
				pk AS data,
				(description || ' ' || amount || ' ' || unit) AS field_label,
				(description || ' ' || amount || ' ' || unit) AS list_label,
				2 AS rank
			FROM ref.consumable_substance
			WHERE
				description %%(fragment_condition)s
					AND
				pk NOT IN (
					SELECT fk_substance
					FROM clin.substance_intake
					WHERE fk_substance IS NOT NULL
				)
		)) AS candidates
		ORDER BY rank, list_label
		LIMIT 50""" % _('in use')

	_regex_query = 	u"""
		SELECT
			data,
			field_label,
			list_label,
			rank
		FROM ((
			SELECT
				pk_substance AS data,
				(description || ' ' || amount || ' ' || unit) AS field_label,
				(description || ' ' || amount || ' ' || unit || ' (%s)') AS list_label,
				1 AS rank
			FROM (
				SELECT DISTINCT ON (description, amount, unit)
					pk_substance,
					substance AS description,
					amount,
					unit
				FROM clin.v_nonbrand_intakes
			) AS normalized_intakes
			WHERE
				%%(fragment_condition)s
		) UNION ALL (
			-- matching substances which are not in intakes
			SELECT
				pk AS data,
				(description || ' ' || amount || ' ' || unit) AS field_label,
				(description || ' ' || amount || ' ' || unit) AS list_label,
				2 AS rank
			FROM ref.consumable_substance
			WHERE
				%%(fragment_condition)s
					AND
				pk NOT IN (
					SELECT fk_substance
					FROM clin.substance_intake
					WHERE fk_substance IS NOT NULL
				)
		)) AS candidates
		ORDER BY rank, list_label
		LIMIT 50""" % _('in use')

	#--------------------------------------------------------
	def getMatchesByPhrase(self, aFragment):
		"""Return matches for aFragment at start of phrases."""

		if cSubstanceMatchProvider._pattern.match(aFragment):
			self._queries = [cSubstanceMatchProvider._regex_query]
			fragment_condition = """description ILIKE %(desc)s
				AND
			amount::text ILIKE %(amount)s"""
			self._args['desc'] = u'%s%%' % regex.sub(r'\s*\d+$', u'', aFragment)
			self._args['amount'] = u'%s%%' % regex.sub(r'^\D+\s*', u'', aFragment)
		else:
			self._queries = [cSubstanceMatchProvider._normal_query]
			fragment_condition = u"ILIKE %(fragment)s"
			self._args['fragment'] = u"%s%%" % aFragment

		return self._find_matches(fragment_condition)
	#--------------------------------------------------------
	def getMatchesByWord(self, aFragment):
		"""Return matches for aFragment at start of words inside phrases."""

		if cSubstanceMatchProvider._pattern.match(aFragment):
			self._queries = [cSubstanceMatchProvider._regex_query]

			desc = regex.sub(r'\s*\d+$', u'', aFragment)
			desc = gmPG2.sanitize_pg_regex(expression = desc, escape_all = False)

			fragment_condition = """description ~* %(desc)s
				AND
			amount::text ILIKE %(amount)s"""

			self._args['desc'] = u"( %s)|(^%s)" % (desc, desc)
			self._args['amount'] = u'%s%%' % regex.sub(r'^\D+\s*', u'', aFragment)
		else:
			self._queries = [cSubstanceMatchProvider._normal_query]
			fragment_condition = u"~* %(fragment)s"
			aFragment = gmPG2.sanitize_pg_regex(expression = aFragment, escape_all = False)
			self._args['fragment'] = u"( %s)|(^%s)" % (aFragment, aFragment)

		return self._find_matches(fragment_condition)
	#--------------------------------------------------------
	def getMatchesBySubstr(self, aFragment):
		"""Return matches for aFragment as a true substring."""

		if cSubstanceMatchProvider._pattern.match(aFragment):
			self._queries = [cSubstanceMatchProvider._regex_query]
			fragment_condition = """description ILIKE %(desc)s
				AND
			amount::text ILIKE %(amount)s"""
			self._args['desc'] = u'%%%s%%' % regex.sub(r'\s*\d+$', u'', aFragment)
			self._args['amount'] = u'%s%%' % regex.sub(r'^\D+\s*', u'', aFragment)
		else:
			self._queries = [cSubstanceMatchProvider._normal_query]
			fragment_condition = u"ILIKE %(fragment)s"
			self._args['fragment'] = u"%%%s%%" % aFragment

		return self._find_matches(fragment_condition)

#------------------------------------------------------------
class cBrandOrSubstanceMatchProvider(gmMatchProvider.cMatchProvider_SQL2):

	# by brand name
	_query_brand_by_name = u"""
		SELECT
			ARRAY[1, pk]::INTEGER[]
				AS data,
			(description || ' (' || preparation || ')' || coalesce(' [' || atc_code || ']', ''))
				AS list_label,
			(description || ' (' || preparation || ')' || coalesce(' [' || atc_code || ']', ''))
				AS field_label,
			1 AS rank
		FROM ref.branded_drug
		WHERE description %(fragment_condition)s
		LIMIT 50
	"""
	_query_brand_by_name_and_strength = u"""
		SELECT
			ARRAY[1, pk_brand]::INTEGER[]
				AS data,
			(brand || ' (' || preparation || %s || amount || unit || ' ' || substance || ')' || coalesce(' [' || atc_brand || ']', ''))
				AS list_label,
			(brand || ' (' || preparation || %s || amount || unit || ' ' || substance || ')' || coalesce(' [' || atc_brand || ']', ''))
				AS field_label,
			1 AS rank
		FROM
			(SELECT *, brand AS description FROM ref.v_drug_components) AS _components
		WHERE %%(fragment_condition)s
		LIMIT 50
	""" % (
		_('w/'),
		_('w/')
	)

	# by component
	_query_component_by_name = u"""
		SELECT
			ARRAY[3, r_vdc1.pk_component]::INTEGER[]
				AS data,
			(r_vdc1.substance || ' ' || r_vdc1.amount || r_vdc1.unit || ' ' || r_vdc1.preparation || ' ('
				|| r_vdc1.brand || ' ['
					|| (
						SELECT array_to_string(array_agg(r_vdc2.amount), ' / ')
						FROM ref.v_drug_components r_vdc2
						WHERE r_vdc2.pk_brand = r_vdc1.pk_brand
					)
				|| ']'
			|| ')'
			)	AS field_label,
			(r_vdc1.substance || ' ' || r_vdc1.amount || r_vdc1.unit || ' ' || r_vdc1.preparation || ' ('
				|| r_vdc1.brand || ' ['
					|| (
						SELECT array_to_string(array_agg(r_vdc2.amount), ' / ')
						FROM ref.v_drug_components r_vdc2
						WHERE r_vdc2.pk_brand = r_vdc1.pk_brand
					)
				|| ']'
			|| ')'
			)	AS list_label,
			1 AS rank
		FROM
			(SELECT *, brand AS description FROM ref.v_drug_components) AS r_vdc1
		WHERE
			r_vdc1.substance %(fragment_condition)s
		LIMIT 50"""
	_query_component_by_name_and_strength = u"""
		SELECT
			ARRAY[3, r_vdc1.pk_component]::INTEGER[]
				AS data,
			(r_vdc1.substance || ' ' || r_vdc1.amount || r_vdc1.unit || ' ' || r_vdc1.preparation || ' ('
				|| r_vdc1.brand || ' ['
					|| (
						SELECT array_to_string(array_agg(r_vdc2.amount), ' / ')
						FROM ref.v_drug_components r_vdc2
						WHERE r_vdc2.pk_brand = r_vdc1.pk_brand
					)
				|| ']'
			|| ')'
			)	AS field_label,
			(r_vdc1.substance || ' ' || r_vdc1.amount || r_vdc1.unit || ' ' || r_vdc1.preparation || ' ('
				|| r_vdc1.brand || ' ['
					|| (
						SELECT array_to_string(array_agg(r_vdc2.amount), ' / ')
						FROM ref.v_drug_components r_vdc2
						WHERE r_vdc2.pk_brand = r_vdc1.pk_brand
					)
				|| ']'
			|| ')'
			)	AS list_label,
			1 AS rank
		FROM (SELECT *, substance AS description FROM ref.v_drug_components) AS r_vdc1
		WHERE
			%(fragment_condition)s
		ORDER BY list_label
		LIMIT 50"""

	# by substance name
	_query_substance_by_name = u"""
		SELECT
			data,
			field_label,
			list_label,
			rank
		FROM ((
			-- first: substance intakes which match, because we tend to reuse them often
			SELECT
				ARRAY[2, pk_substance]::INTEGER[] AS data,
				(description || ' ' || amount || ' ' || unit) AS field_label,
				(description || ' ' || amount || ' ' || unit || ' (%s)') AS list_label,
				1 AS rank
			FROM (
				SELECT DISTINCT ON (description, amount, unit)
					pk_substance,
					substance AS description,
					amount,
					unit
				FROM clin.v_nonbrand_intakes
			) AS normalized_intakes
			WHERE description %%(fragment_condition)s

		) UNION ALL (

			-- second: consumable substances which match but are not intakes
			SELECT
				ARRAY[2, pk]::INTEGER[] AS data,
				(description || ' ' || amount || ' ' || unit) AS field_label,
				(description || ' ' || amount || ' ' || unit) AS list_label,
				2 AS rank
			FROM ref.consumable_substance
			WHERE
				description %%(fragment_condition)s
					AND
				pk NOT IN (
					SELECT fk_substance
					FROM clin.substance_intake
					WHERE fk_substance IS NOT NULL
				)
		)) AS candidates
		--ORDER BY rank, list_label
		LIMIT 50""" % _('in use')
	_query_substance_by_name_and_strength = 	u"""
		SELECT
			data,
			field_label,
			list_label,
			rank
		FROM ((
			SELECT
				ARRAY[2, pk_substance]::INTEGER[] AS data,
				(description || ' ' || amount || ' ' || unit) AS field_label,
				(description || ' ' || amount || ' ' || unit || ' (%s)') AS list_label,
				1 AS rank
			FROM (
				SELECT DISTINCT ON (description, amount, unit)
					pk_substance,
					substance AS description,
					amount,
					unit
				FROM clin.v_nonbrand_intakes
			) AS normalized_intakes
			WHERE
				%%(fragment_condition)s

		) UNION ALL (

			-- matching substances which are not in intakes
			SELECT
				ARRAY[2, pk]::INTEGER[] AS data,
				(description || ' ' || amount || ' ' || unit) AS field_label,
				(description || ' ' || amount || ' ' || unit) AS list_label,
				2 AS rank
			FROM ref.consumable_substance
			WHERE
				%%(fragment_condition)s
					AND
				pk NOT IN (
					SELECT fk_substance
					FROM clin.substance_intake
					WHERE fk_substance IS NOT NULL
				)
		)) AS candidates
		--ORDER BY rank, list_label
		LIMIT 50""" % _('in use')

	_pattern = regex.compile(r'^\D+\s*\d+$', regex.UNICODE | regex.LOCALE)

	_master_query = u"""
		SELECT
			data, field_label, list_label, rank
		FROM ((%s) UNION (%s) UNION (%s))
			AS _union
		ORDER BY rank, list_label
		LIMIT 50
	"""
	#--------------------------------------------------------
	def getMatchesByPhrase(self, aFragment):
		"""Return matches for aFragment at start of phrases."""

		if cBrandOrSubstanceMatchProvider._pattern.match(aFragment):
			self._queries = [
				cBrandOrSubstanceMatchProvider._master_query % (
					cBrandOrSubstanceMatchProvider._query_brand_by_name_and_strength,
					cBrandOrSubstanceMatchProvider._query_substance_by_name_and_strength,
					cBrandOrSubstanceMatchProvider._query_component_by_name_and_strength
				)
			]
			#self._queries = [cBrandOrSubstanceMatchProvider._query_substance_by_name_and_strength]
			fragment_condition = """description ILIKE %(desc)s
				AND
			amount::text ILIKE %(amount)s"""
			self._args['desc'] = u'%s%%' % regex.sub(r'\s*\d+$', u'', aFragment)
			self._args['amount'] = u'%s%%' % regex.sub(r'^\D+\s*', u'', aFragment)
		else:
			self._queries = [
				cBrandOrSubstanceMatchProvider._master_query % (
					cBrandOrSubstanceMatchProvider._query_brand_by_name,
					cBrandOrSubstanceMatchProvider._query_substance_by_name,
					cBrandOrSubstanceMatchProvider._query_component_by_name
				)
			]
			#self._queries = [cBrandOrSubstanceMatchProvider._query_substance_by_name]
			fragment_condition = u"ILIKE %(fragment)s"
			self._args['fragment'] = u"%s%%" % aFragment

		return self._find_matches(fragment_condition)
	#--------------------------------------------------------
	def getMatchesByWord(self, aFragment):
		"""Return matches for aFragment at start of words inside phrases."""

		if cBrandOrSubstanceMatchProvider._pattern.match(aFragment):
			self._queries = [
				cBrandOrSubstanceMatchProvider._master_query % (
					cBrandOrSubstanceMatchProvider._query_brand_by_name_and_strength,
					cBrandOrSubstanceMatchProvider._query_substance_by_name_and_strength,
					cBrandOrSubstanceMatchProvider._query_component_by_name_and_strength
				)
			]
			#self._queries = [cBrandOrSubstanceMatchProvider._query_substance_by_name_and_strength]

			desc = regex.sub(r'\s*\d+$', u'', aFragment)
			desc = gmPG2.sanitize_pg_regex(expression = desc, escape_all = False)

			fragment_condition = """description ~* %(desc)s
				AND
			amount::text ILIKE %(amount)s"""

			self._args['desc'] = u"( %s)|(^%s)" % (desc, desc)
			self._args['amount'] = u'%s%%' % regex.sub(r'^\D+\s*', u'', aFragment)
		else:
			self._queries = [
				cBrandOrSubstanceMatchProvider._master_query % (
					cBrandOrSubstanceMatchProvider._query_brand_by_name,
					cBrandOrSubstanceMatchProvider._query_substance_by_name,
					cBrandOrSubstanceMatchProvider._query_component_by_name
				)
			]
			#self._queries = [cBrandOrSubstanceMatchProvider._query_substance_by_name]
			fragment_condition = u"~* %(fragment)s"
			aFragment = gmPG2.sanitize_pg_regex(expression = aFragment, escape_all = False)
			self._args['fragment'] = u"( %s)|(^%s)" % (aFragment, aFragment)

		return self._find_matches(fragment_condition)
	#--------------------------------------------------------
	def getMatchesBySubstr(self, aFragment):
		"""Return matches for aFragment as a true substring."""

		if cBrandOrSubstanceMatchProvider._pattern.match(aFragment):
			self._queries = [
				cBrandOrSubstanceMatchProvider._master_query % (
					cBrandOrSubstanceMatchProvider._query_brand_by_name_and_strength,
					cBrandOrSubstanceMatchProvider._query_substance_by_name_and_strength,
					cBrandOrSubstanceMatchProvider._query_component_by_name_and_strength
				)
			]
			#self._queries = [cBrandOrSubstanceMatchProvider._query_substance_by_name_and_strength]
			fragment_condition = """description ILIKE %(desc)s
				AND
			amount::text ILIKE %(amount)s"""
			self._args['desc'] = u'%%%s%%' % regex.sub(r'\s*\d+$', u'', aFragment)
			self._args['amount'] = u'%s%%' % regex.sub(r'^\D+\s*', u'', aFragment)
		else:
			self._queries = [
				cBrandOrSubstanceMatchProvider._master_query % (
					cBrandOrSubstanceMatchProvider._query_brand_by_name,
					cBrandOrSubstanceMatchProvider._query_substance_by_name,
					cBrandOrSubstanceMatchProvider._query_component_by_name
				)
			]
			#self._queries = [cBrandOrSubstanceMatchProvider._query_substance_by_name]
			fragment_condition = u"ILIKE %(fragment)s"
			self._args['fragment'] = u"%%%s%%" % aFragment

		return self._find_matches(fragment_condition)

#============================================================
# substance intakes
#------------------------------------------------------------
_SQL_get_substance_intake = u"SELECT * FROM clin.v_substance_intakes WHERE %s"

class cSubstanceIntakeEntry(gmBusinessDBObject.cBusinessDBObject):
	"""Represents a substance currently taken by a patient."""

	_cmd_fetch_payload = _SQL_get_substance_intake % 'pk_substance_intake = %s'
	_cmds_store_payload = [
		u"""UPDATE clin.substance_intake SET
				-- if .comment_on_start = '?' then .started will be mapped to NULL
				-- in the view, also, .started CANNOT be NULL any other way so far,
				-- so do not attempt to set .clin_when if .started is NULL
				clin_when = (
					CASE
						WHEN %(started)s IS NULL THEN clin_when
						ELSE %(started)s
					END
				)::timestamp with time zone,
				comment_on_start = gm.nullify_empty_string(%(comment_on_start)s),
				discontinued = %(discontinued)s,
				discontinue_reason = gm.nullify_empty_string(%(discontinue_reason)s),
				schedule = gm.nullify_empty_string(%(schedule)s),
				aim = gm.nullify_empty_string(%(aim)s),
				narrative = gm.nullify_empty_string(%(notes)s),
				intake_is_approved_of = %(intake_is_approved_of)s,
				harmful_use_type = %(harmful_use_type)s,
				fk_episode = %(pk_episode)s,
				-- only used to document "last checked" such that
				-- .clin_when -> .started does not have to change meaning
				fk_encounter = %(pk_encounter)s,

				is_long_term = (
					case
						when (
							(%(is_long_term)s is False)
								and
							(%(duration)s is NULL)
						) is True then null
						else %(is_long_term)s
					end
				)::boolean,

				duration = (
					case
						when %(is_long_term)s is True then null
						else %(duration)s
					end
				)::interval
			WHERE
				pk = %(pk_substance_intake)s
					AND
				xmin = %(xmin_substance_intake)s
			RETURNING
				xmin as xmin_substance_intake
		"""
	]
	_updatable_fields = [
		u'started',
		u'comment_on_start',
		u'discontinued',
		u'discontinue_reason',
		u'intake_is_approved_of',
		u'schedule',
		u'duration',
		u'aim',
		u'is_long_term',
		u'notes',
		u'pk_episode',
		u'pk_encounter',
		u'harmful_use_type'
	]

	#--------------------------------------------------------
	def format_maximum_information(self, patient=None):
		return self.format (
			single_line = False,
			show_all_brand_components = True,
			include_metadata = True,
			date_format = '%Y %b %d',
			include_instructions = True
		).split(u'\n')

	#--------------------------------------------------------
	def format(self, left_margin=0, date_format='%Y %b %d', single_line=True, allergy=None, show_all_brand_components=False, include_metadata=True, include_instructions=False):

		# medication
		if self._payload[self._idx['harmful_use_type']] is None:
			if single_line:
				return self.format_as_single_line(left_margin = left_margin, date_format = date_format)
			return self.format_as_multiple_lines (
				left_margin = left_margin,
				date_format = date_format,
				allergy = allergy,
				show_all_brand_components = show_all_brand_components,
				include_instructions = include_instructions
			)

		# abuse
		if single_line:
			return self.format_as_single_line_abuse(left_margin = left_margin, date_format = date_format)

		return self.format_as_multiple_lines_abuse(left_margin = left_margin, date_format = date_format, include_metadata = include_metadata)

	#--------------------------------------------------------
	def format_as_single_line_abuse(self, left_margin=0, date_format='%Y %b %d'):
		return u'%s%s: %s (%s)' % (
			u' ' * left_margin,
			self._payload[self._idx['substance']],
			self.harmful_use_type_string,
			gmDateTime.pydt_strftime(self._payload[self._idx['last_checked_when']], '%b %Y')
		)

	#--------------------------------------------------------
	def format_as_single_line(self, left_margin=0, date_format='%Y %b %d'):

		if self._payload[self._idx['is_currently_active']]:
			if self._payload[self._idx['duration']] is None:
				duration = gmTools.bool2subst (
					self._payload[self._idx['is_long_term']],
					_('long-term'),
					_('short-term'),
					_('?short-term')
				)
			else:
				duration = gmDateTime.format_interval (
					self._payload[self._idx['duration']],
					accuracy_wanted = gmDateTime.acc_days
				)
		else:
			duration = gmDateTime.pydt_strftime(self._payload[self._idx['discontinued']], date_format)

		line = u'%s%s (%s %s): %s %s%s %s (%s)' % (
			u' ' * left_margin,
			self.medically_formatted_start,
			gmTools.u_arrow2right,
			duration,
			self._payload[self._idx['substance']],
			self._payload[self._idx['amount']],
			self._payload[self._idx['unit']],
			self._payload[self._idx['preparation']],
			gmTools.bool2subst(self._payload[self._idx['is_currently_active']], _('ongoing'), _('inactive'), _('?ongoing'))
		)

		return line

	#--------------------------------------------------------
	def format_as_multiple_lines_abuse(self, left_margin=0, date_format='%Y %b %d', include_metadata=True):

		txt = u''
		if include_metadata:
			txt = _('Substance abuse entry                                              [#%s]\n') % self._payload[self._idx['pk_substance_intake']]
		txt += u' ' + _('Substance: %s [#%s]%s\n') % (
			self._payload[self._idx['substance']],
			self._payload[self._idx['pk_substance']],
			gmTools.coalesce(self._payload[self._idx['atc_substance']], u'', ' ATC %s')
		)
		txt += u' ' + _('Use type: %s\n') % self.harmful_use_type_string
		txt += u' ' + _('Last checked: %s\n') % gmDateTime.pydt_strftime(self._payload[self._idx['last_checked_when']], '%Y %b %d')
		if self._payload[self._idx['discontinued']] is not None:
			txt += _(' Discontinued %s\n') % (
				gmDateTime.pydt_strftime (
					self._payload[self._idx['discontinued']],
					format = date_format,
					accuracy = gmDateTime.acc_days
				)
			)
		txt += gmTools.coalesce(self._payload[self._idx['notes']], u'', _(' Notes: %s\n'))
		if include_metadata:
			txt += u'\n'
			txt += _(u'Revision: #%(row_ver)s, %(mod_when)s by %(mod_by)s.') % {
				'row_ver': self._payload[self._idx['row_version']],
				'mod_when': gmDateTime.pydt_strftime(self._payload[self._idx['modified_when']]),
				'mod_by': self._payload[self._idx['modified_by']]
			}

		return txt

	#--------------------------------------------------------
	def format_as_multiple_lines(self, left_margin=0, date_format='%Y %b %d', allergy=None, show_all_brand_components=False, include_instructions=False):

		txt = _('Substance intake entry (%s, %s)   [#%s]                     \n') % (
			gmTools.bool2subst (
				boolean = self._payload[self._idx['is_currently_active']],
				true_return = gmTools.bool2subst (
					boolean = self._payload[self._idx['seems_inactive']],
					true_return = _('active, needs check'),
					false_return = _('active'),
					none_return = _('assumed active')
				),
				false_return = _('inactive')
			),
			gmTools.bool2subst (
				boolean = self._payload[self._idx['intake_is_approved_of']],
				true_return = _('approved'),
				false_return = _('unapproved')
			),
			self._payload[self._idx['pk_substance_intake']]
		)

		if allergy is not None:
			certainty = gmTools.bool2subst(allergy['definite'], _('definite'), _('suspected'))
			txt += u'\n'
			txt += u' !! ---- Cave ---- !!\n'
			txt += u' %s (%s): %s (%s)\n' % (
				allergy['l10n_type'],
				certainty,
				allergy['descriptor'],
				gmTools.coalesce(allergy['reaction'], u'')[:40]
			)
			txt += u'\n'

		txt += u' ' + _('Substance: %s   [#%s]\n') % (self._payload[self._idx['substance']], self._payload[self._idx['pk_substance']])
		txt += u' ' + _('Preparation: %s\n') % self._payload[self._idx['preparation']]
		txt += u' ' + _('Amount per dose: %s %s') % (self._payload[self._idx['amount']], self._payload[self._idx['unit']])
		txt += u'\n'
		txt += gmTools.coalesce(self._payload[self._idx['atc_substance']], u'', _(' ATC (substance): %s\n'))

		txt += u'\n'

		txt += gmTools.coalesce (
			self._payload[self._idx['brand']],
			u'',
			_(' Brand name: %%s   [#%s]\n') % self._payload[self._idx['pk_brand']]
		)
		txt += gmTools.coalesce(self._payload[self._idx['atc_brand']], u'', _(' ATC (brand): %s\n'))
		if show_all_brand_components and (self._payload[self._idx['pk_brand']] is not None):
			brand = self.containing_drug
			if len(brand['pk_substances']) > 1:
				for comp in brand['components']:
					if comp.startswith(self._payload[self._idx['substance']] + u'::'):
						continue
					txt += _('  Other component: %s\n') % comp

		txt += u'\n'

		txt += gmTools.coalesce(self._payload[self._idx['schedule']], u'', _(' Regimen: %s\n'))

		if self._payload[self._idx['is_long_term']]:
			duration = u' %s %s' % (gmTools.u_arrow2right, gmTools.u_infinity)
		else:
			if self._payload[self._idx['duration']] is None:
				duration = u''
			else:
				duration = u' %s %s' % (gmTools.u_arrow2right, gmDateTime.format_interval(self._payload[self._idx['duration']], gmDateTime.acc_days))

		txt += _(' Started %s%s%s\n') % (
			self.medically_formatted_start,
			duration,
			gmTools.bool2subst(self._payload[self._idx['is_long_term']], _(' (long-term)'), _(' (short-term)'), u'')
		)

		if self._payload[self._idx['discontinued']] is not None:
			txt += _(' Discontinued %s\n') % (
				gmDateTime.pydt_strftime (
					self._payload[self._idx['discontinued']],
					format = date_format,
					accuracy = gmDateTime.acc_days
				)
			)
			txt += gmTools.coalesce(self._payload[self._idx['discontinue_reason']], u'', _(' Reason: %s\n'))

		txt += u'\n'

		txt += gmTools.coalesce(self._payload[self._idx['aim']], u'', _(' Aim: %s\n'))
		txt += gmTools.coalesce(self._payload[self._idx['episode']], u'', _(' Episode: %s\n'))
		txt += gmTools.coalesce(self._payload[self._idx['health_issue']], u'', _(' Health issue: %s\n'))
		txt += gmTools.coalesce(self._payload[self._idx['notes']], u'', _(' Advice: %s\n'))
		if self._payload[self._idx['intake_instructions']] is not None:
			txt = txt + u' '+ (_('Intake: %s') % self._payload[self._idx['intake_instructions']]) + u'\n'

		txt += u'\n'

		txt += _(u'Revision: #%(row_ver)s, %(mod_when)s by %(mod_by)s.') % {
			'row_ver': self._payload[self._idx['row_version']],
			'mod_when': gmDateTime.pydt_strftime(self._payload[self._idx['modified_when']]),
			'mod_by': self._payload[self._idx['modified_by']]
		}

		return txt

	#--------------------------------------------------------
	def turn_into_allergy(self, encounter_id=None, allergy_type='allergy'):
		allg = gmAllergy.create_allergy (
			allergene = self._payload[self._idx['substance']],
			allg_type = allergy_type,
			episode_id = self._payload[self._idx['pk_episode']],
			encounter_id = encounter_id
		)
		allg['substance'] = gmTools.coalesce (
			self._payload[self._idx['brand']],
			self._payload[self._idx['substance']]
		)
		allg['reaction'] = self._payload[self._idx['discontinue_reason']]
		allg['atc_code'] = gmTools.coalesce(self._payload[self._idx['atc_substance']], self._payload[self._idx['atc_brand']])
		if self._payload[self._idx['external_code_brand']] is not None:
			allg['substance_code'] = u'%s::::%s' % (self._payload[self._idx['external_code_type_brand']], self._payload[self._idx['external_code_brand']])

		if self._payload[self._idx['pk_brand']] is None:
			allg['generics'] = self._payload[self._idx['substance']]
		else:
			comps = [ c['substance'] for c in self.containing_drug.components ]
			if len(comps) == 0:
				allg['generics'] = self._payload[self._idx['substance']]
			else:
				allg['generics'] = u'; '.join(comps)

		allg.save()
		return allg

	#--------------------------------------------------------
	def delete(self):
		return delete_substance_intake(substance = self._payload[self._idx['pk_substance_intake']])

	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def _get_harmful_use_type_string(self):

		if self._payload[self._idx['harmful_use_type']] is None:
			return _('medication, not abuse')
		if self._payload[self._idx['harmful_use_type']] == 0:
			return _('no or non-harmful use')
		if self._payload[self._idx['harmful_use_type']] == 1:
			return _('presently harmful use')
		if self._payload[self._idx['harmful_use_type']] == 2:
			return _('presently addicted')
		if self._payload[self._idx['harmful_use_type']] == 3:
			return _('previously addicted')

	harmful_use_type_string = property(_get_harmful_use_type_string)

	#--------------------------------------------------------
	def _get_external_code(self):
		drug = self.containing_drug

		if drug is None:
			return None

		return drug.external_code

	external_code = property(_get_external_code, lambda x:x)

	#--------------------------------------------------------
	def _get_external_code_type(self):
		drug = self.containing_drug

		if drug is None:
			return None

		return drug.external_code_type

	external_code_type = property(_get_external_code_type, lambda x:x)

	#--------------------------------------------------------
	def _get_containing_drug(self):
		if self._payload[self._idx['pk_brand']] is None:
			return None

		return cBrandedDrug(aPK_obj = self._payload[self._idx['pk_brand']])

	containing_drug = property(_get_containing_drug, lambda x:x)

	#--------------------------------------------------------
	def _get_medically_formatted_start(self):
		if self._payload[self._idx['comment_on_start']] == u'?':
			return u'?'

		start_prefix = u''
		if self._payload[self._idx['comment_on_start']] is not None:
			start_prefix = gmTools.u_almost_equal_to

		duration_taken = gmDateTime.pydt_now_here() - self._payload[self._idx['started']]

		three_months = pydt.timedelta(weeks = 13, days = 3)
		if duration_taken < three_months:
			return _('%s%s: %s ago%s') % (
				start_prefix,
				gmDateTime.pydt_strftime(self._payload[self._idx['started']], '%Y %b %d', u'utf8', gmDateTime.acc_days),
				gmDateTime.format_interval_medically(duration_taken),
				gmTools.coalesce(self._payload[self._idx['comment_on_start']], u'', u' (%s)')
			)

		five_years = pydt.timedelta(weeks = 265)
		if duration_taken < five_years:
			return _('%s%s: %s ago (%s)') % (
				start_prefix,
				gmDateTime.pydt_strftime(self._payload[self._idx['started']], '%Y %b', u'utf8', gmDateTime.acc_months),
				gmDateTime.format_interval_medically(duration_taken),
				gmTools.coalesce (
					self._payload[self._idx['comment_on_start']],
					gmDateTime.pydt_strftime(self._payload[self._idx['started']], '%b %d', u'utf8', gmDateTime.acc_days),
				)
			)

		return _('%s%s: %s ago (%s)') % (
			start_prefix,
			gmDateTime.pydt_strftime(self._payload[self._idx['started']], '%Y', u'utf8', gmDateTime.acc_years),
			gmDateTime.format_interval_medically(duration_taken),
			gmTools.coalesce (
				self._payload[self._idx['comment_on_start']],
				gmDateTime.pydt_strftime(self._payload[self._idx['started']], '%b %d', u'utf8', gmDateTime.acc_days),
			)
		)

	medically_formatted_start = property(_get_medically_formatted_start, lambda x:x)

	#--------------------------------------------------------
	def _get_medically_formatted_start_end_of_stopped(self, now):

		# format intro
		if gmDateTime.pydt_is_today(self._payload[self._idx['discontinued']]):
			intro = _(u'until today')
		else:
			ended_ago = now - self._payload[self._idx['discontinued']]
			intro = _(u'until %s%s ago') % (
				gmTools.u_almost_equal_to,
				gmDateTime.format_interval_medically(ended_ago),
			)

		# format start
		if self._payload[self._idx['started']] is None:
			start = gmTools.coalesce(self._payload[self._idx['comment_on_start']], u'?')
		else:
			start = u'%s%s%s' % (
				gmTools.bool2subst((self._payload[self._idx['comment_on_start']] is None), u'', gmTools.u_almost_equal_to),
				gmDateTime.pydt_strftime(self._payload[self._idx['started']], format = '%Y %b %d', encoding = u'utf8', accuracy = gmDateTime.acc_days),
				gmTools.coalesce(self._payload[self._idx['comment_on_start']], u'', u' [%s]')
			)

		# format duration taken
		if self._payload[self._idx['started']] is None:
			duration_taken_str = u'?'
		else:
			duration_taken = self._payload[self._idx['discontinued']] - self._payload[self._idx['started']] + pydt.timedelta(days = 1)
			duration_taken_str = gmDateTime.format_interval (duration_taken, gmDateTime.acc_days)

		# format duration planned
		if self._payload[self._idx['duration']] is None:
			duration_planned_str = u''
		else:
			duration_planned_str = _(u' [planned: %s]') % gmDateTime.format_interval(self._payload[self._idx['duration']], gmDateTime.acc_days)

		# format end
		end = gmDateTime.pydt_strftime(self._payload[self._idx['discontinued']], '%Y %b %d', u'utf8', gmDateTime.acc_days)

		# assemble
		txt = u'%s (%s %s %s%s %s %s)' % (
			intro,
			start,
			gmTools.u_arrow2right_thick,
			duration_taken_str,
			duration_planned_str,
			gmTools.u_arrow2right_thick,
			end
		)
		return txt

	#--------------------------------------------------------
	def _get_medically_formatted_start_end(self):

		now = gmDateTime.pydt_now_here()

		# medications stopped today or before today
		if self._payload[self._idx['discontinued']] is not None:
			if (self._payload[self._idx['discontinued']] < now) or (gmDateTime.pydt_is_today(self._payload[self._idx['discontinued']])):
				return self._get_medically_formatted_start_end_of_stopped(now)

		# ongoing medications
		arrow_parts = []

		# format start
		if self._payload[self._idx['started']] is None:
			start_str = gmTools.coalesce(self._payload[self._idx['comment_on_start']], u'?')
		else:
			start_prefix = gmTools.bool2subst((self._payload[self._idx['comment_on_start']] is None), u'', gmTools.u_almost_equal_to)
			# starts today
			if gmDateTime.pydt_is_today(self._payload[self._idx['started']]):
				start_str = _(u'today (%s)') % gmDateTime.pydt_strftime(self._payload[self._idx['started']], format = '%Y %b %d', encoding = u'utf8', accuracy = gmDateTime.acc_days)
			# started in the past
			elif self._payload[self._idx['started']] < now:
				started_ago = now - self._payload[self._idx['started']]
				three_months = pydt.timedelta(weeks = 13, days = 3)
				five_years = pydt.timedelta(weeks = 265)
				if started_ago < three_months:
					start_str = _('%s%s%s (%s%s ago, in %s)') % (
						start_prefix,
						gmDateTime.pydt_strftime(self._payload[self._idx['started']], format = '%b %d', encoding = u'utf8', accuracy = gmDateTime.acc_days),
						gmTools.coalesce(self._payload[self._idx['comment_on_start']], u'', u' [%s]'),
						gmTools.u_almost_equal_to,
						gmDateTime.format_interval_medically(started_ago),
						gmDateTime.pydt_strftime(self._payload[self._idx['started']], format = '%Y', encoding = u'utf8', accuracy = gmDateTime.acc_days)
					)
				elif started_ago < five_years:
					start_str = _('%s%s%s (%s%s ago, %s)') % (
						start_prefix,
						gmDateTime.pydt_strftime(self._payload[self._idx['started']], '%Y %b', u'utf8', gmDateTime.acc_months),
						gmTools.coalesce(self._payload[self._idx['comment_on_start']], u'', u' [%s]'),
						gmTools.u_almost_equal_to,
						gmDateTime.format_interval_medically(started_ago),
						gmDateTime.pydt_strftime(self._payload[self._idx['started']], '%b %d', u'utf8', gmDateTime.acc_days)
					)
				else:
					start_str = _('%s%s%s (%s%s ago, %s)') % (
						start_prefix,
						gmDateTime.pydt_strftime(self._payload[self._idx['started']], '%Y', u'utf8', gmDateTime.acc_years),
						gmTools.coalesce(self._payload[self._idx['comment_on_start']], u'', u' [%s]'),
						gmTools.u_almost_equal_to,
						gmDateTime.format_interval_medically(started_ago),
						gmDateTime.pydt_strftime(self._payload[self._idx['started']], '%b %d', u'utf8', gmDateTime.acc_days),
					)
			# starts in the future
			else:
				starts_in = self._payload[self._idx['started']] - now
				start_str = _('%s%s%s (in %s%s)') % (
					start_prefix,
					gmDateTime.pydt_strftime(self._payload[self._idx['started']], '%Y %b %d', u'utf8', gmDateTime.acc_days),
					gmTools.coalesce(self._payload[self._idx['comment_on_start']], u'', u' [%s]'),
					gmTools.u_almost_equal_to,
					gmDateTime.format_interval_medically(starts_in)
				)

		arrow_parts.append(start_str)

		# format durations
		durations = []
		if self._payload[self._idx['discontinued']] is not None:
			if self._payload[self._idx['started']] is not None:
				duration_documented = self._payload[self._idx['discontinued']] - self._payload[self._idx['started']]
				durations.append(_(u'%s (documented)') % gmDateTime.format_interval(duration_documented, gmDateTime.acc_days))
		if self._payload[self._idx['duration']] is not None:
			durations.append(_(u'%s (plan)') % gmDateTime.format_interval(self._payload[self._idx['duration']], gmDateTime.acc_days))
		if len(durations) == 0:
			if self._payload[self._idx['is_long_term']]:
				duration_str = gmTools.u_infinity
			else:
				duration_str = u'?'
		else:
			duration_str = u', '.join(durations)

		arrow_parts.append(duration_str)

		# format end
		if self._payload[self._idx['discontinued']] is None:
			if self._payload[self._idx['duration']] is None:
				end_str = u'?'
			else:
				if self._payload[self._idx['started']] is None:
					end_str = u'?'
				else:
					planned_end = self._payload[self._idx['started']] + self._payload[self._idx['duration']] - pydt.timedelta(days = 1)
					if planned_end.year == now.year:
						end_template = '%b %d'
						if planned_end < now:
							planned_end_from_now_str = _(u'%s ago, in %s') % (gmDateTime.format_interval(now - planned_end, gmDateTime.acc_days), planned_end.year)
						else:
							planned_end_from_now_str = _(u'in %s, %s') % (gmDateTime.format_interval(planned_end - now, gmDateTime.acc_days), planned_end.year)
					else:
						end_template = '%Y'
						if planned_end < now:
							planned_end_from_now_str = _(u'%s ago = %s') % (
								gmDateTime.format_interval(now - planned_end, gmDateTime.acc_days),
								gmDateTime.pydt_strftime(planned_end, '%b %d', u'utf8', gmDateTime.acc_days)
							)
						else:
							planned_end_from_now_str = _(u'in %s = %s') % (
								gmDateTime.format_interval(planned_end - now, gmDateTime.acc_days),
								gmDateTime.pydt_strftime(planned_end, '%b %d', u'utf8', gmDateTime.acc_days)
							)
					end_str = u'%s (%s)' % (
						gmDateTime.pydt_strftime(planned_end, end_template, u'utf8', gmDateTime.acc_days),
						planned_end_from_now_str
					)
		else:
			if gmDateTime.is_today(self._payload[self._idx['discontinued']]):
				end_str = _(u'today')
			elif self._payload[self._idx['discontinued']].year == now.year:
				end_date_template = '%b %d'
				if self._payload[self._idx['discontinued']] < now:
					planned_end_from_now_str = _(u'%s ago, in %s') % (
						gmDateTime.format_interval(now - self._payload[self._idx['discontinued']], gmDateTime.acc_days),
						self._payload[self._idx['discontinued']].year
					)
				else:
					planned_end_from_now_str = _(u'in %s, %s') % (
						gmDateTime.format_interval(self._payload[self._idx['discontinued']] - now, gmDateTime.acc_days),
						self._payload[self._idx['discontinued']].year
					)
			else:
				end_date_template = '%Y'
				if self._payload[self._idx['discontinued']] < now:
					planned_end_from_now_str = _(u'%s ago = %s') % (
						gmDateTime.format_interval(now - self._payload[self._idx['discontinued']], gmDateTime.acc_days),
						gmDateTime.pydt_strftime(self._payload[self._idx['discontinued']], '%b %d', u'utf8', gmDateTime.acc_days)
					)
				else:
					planned_end_from_now_str = _(u'in %s = %s') % (
						gmDateTime.format_interval(self._payload[self._idx['discontinued']] - now, gmDateTime.acc_days),
						gmDateTime.pydt_strftime(self._payload[self._idx['discontinued']], '%b %d', u'utf8', gmDateTime.acc_days)
					)
			end_str = u'%s (%s)' % (
				gmDateTime.pydt_strftime(self._payload[self._idx['discontinued']], end_date_template, u'utf8', gmDateTime.acc_days),
				planned_end_from_now_str
			)

		arrow_parts.append(end_str)

		# assemble
		return (u' %s ' % gmTools.u_arrow2right_thick).join(arrow_parts)

	medically_formatted_start_end = property(_get_medically_formatted_start_end, lambda x:x)

	#--------------------------------------------------------
	def _get_as_amts_latex(self, strict=True):
		return format_substance_intake_as_amts_latex(intake = self, strict=strict)

	as_amts_latex = property(_get_as_amts_latex, lambda x:x)

	#--------------------------------------------------------
	def _get_as_amts_data(self, strict=True):
		return format_substance_intake_as_amts_data(intake = self, strict = strict)

	as_amts_data = property(_get_as_amts_data, lambda x:x)

	#--------------------------------------------------------
	def _get_parsed_schedule(self):
		tests = [
			# lead, trail
			'	1-1-1-1 ',
			# leading dose
			'1-1-1-1',
			'22-1-1-1',
			'1/3-1-1-1',
			'/4-1-1-1'
		]
		pattern = "^(\d\d|/\d|\d/\d|\d)[\s-]{1,5}\d{0,2}[\s-]{1,5}\d{0,2}[\s-]{1,5}\d{0,2}$"
		for test in tests:
			print test.strip(), ":", regex.match(pattern, test.strip())

#------------------------------------------------------------
def get_substance_intakes(pk_patient=None):
	args = {'pat': pk_patient}
	if pk_patient is None:
		cmd = _SQL_get_substance_intake % u'true'
	else:
		cmd = _SQL_get_substance_intake % u'pk_patient = %(pat)s'
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd}], get_col_idx = True)
	return [ cSubstanceIntakeEntry(row = {'data': r, 'idx': idx, 'pk_field': 'pk_substance_intake'}) for r in rows ]

#------------------------------------------------------------
def substance_intake_exists(pk_component=None, pk_substance=None, pk_identity=None, pk_brand=None, pk_dose=None):

	if [pk_substance, pk_component, pk_brand, pk_dose].count(None) != 3:
		raise ValueError('only one of pk_substance, pk_component, pk_dose, and pk_brand can be non-NULL')

	args = {
		'pk_comp': pk_component,
		'pk_subst': pk_substance,
		'pk_pat': pk_identity,
		'pk_brand': pk_brand,
		'pk_dose': pk_dose
	}
	where_parts = [u'fk_encounter IN (SELECT pk FROM clin.encounter WHERE fk_patient = %(pk_pat)s)']

	if pk_substance is not None:
		where_parts.append(u'fk_drug_component IN (SELECT pk FROM ref.lnk_dose2drug WHERE fk_dose IN (SELECT pk FROM ref.dose WHERE fk_substance = %(pk_subst)s))')
	if pk_dose is not None:
		where_parts.append(u'fk_drug_component IN (SELECT pk FROM ref.lnk_dose2drug WHERE fk_dose = %(pk_dose)s)')
	if pk_component is not None:
		where_parts.append(u'fk_drug_component = %(pk_comp)s')
	if pk_brand is not None:
		where_parts.append(u'fk_drug_component IN (SELECT pk FROM ref.lnk_dose2drug WHERE fk_brand = %(pk_brand)s)')

	cmd = u"""
		SELECT EXISTS (
			SELECT 1 FROM clin.substance_intake
			WHERE
				%s
			LIMIT 1
		)
	""" % u'\nAND\n'.join(where_parts)

	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}])
	return rows[0][0]

#------------------------------------------------------------
def substance_intake_exists_by_atc(pk_identity=None, atc=None):

	if (atc is None) or (pk_identity is None):
		raise ValueError('atc and pk_identity cannot be None')

	args = {
		'pat': pk_identity,
		'atc': atc
	}
	where_parts = [
		u'pk_patient = %(pat)s',
		u'((atc_substance = %(atc)s) OR (atc_brand = %(atc)s))'
	]
	cmd = u"""
		SELECT EXISTS (
			SELECT 1 FROM clin.v_substance_intakes
			WHERE
				%s
			LIMIT 1
		)
	""" % u'\nAND\n'.join(where_parts)

	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}])
	return rows[0][0]

#------------------------------------------------------------
def create_substance_intake(pk_component=None, pk_encounter=None, pk_episode=None, pk_brand=None):

	if [pk_component, pk_brand].count(None) != 1:
		raise ValueError('only one of pk_component and pk_brand can be non-NULL')

	args = {
		'pk_enc': pk_encounter,
		'pk_epi': pk_episode,
		'pk_comp': pk_component,
		'pk_brand': pk_brand
	}

	if pk_brand is not None:
		cmd = u"""
			INSERT INTO clin.substance_intake (
				fk_encounter,
				fk_episode,
				intake_is_approved_of,
				fk_drug_component
			) VALUES (
				%(pk_enc)s,
				%(pk_epi)s,
				False,
				-- select one of the components (the others will be added by a trigger)
				(SELECT pk FROM ref.lnk_dose2drug WHERE fk_brand = %(pk_brand)s LIMIT 1)
			)
			RETURNING pk"""

	if pk_component is not None:
		cmd = u"""
			INSERT INTO clin.substance_intake (
				fk_encounter,
				fk_episode,
				intake_is_approved_of,
				fk_drug_component
			) VALUES (
				%(pk_enc)s,
				%(pk_epi)s,
				False,
				%(pk_comp)s
			)
			RETURNING pk"""

	try:
		rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}], return_data = True)
	except gmPG2.dbapi.InternalError, exc:
		if exc.pgerror is None:
			raise
		exc = make_pg_exception_fields_unicode(exc)
		if 'prevent_duplicate_component' in exc.u_pgerror:
			_log.exception('will not create duplicate substance intake entry')
			_log.error(exc.u_pgerror)
			return None
		raise

	return cSubstanceIntakeEntry(aPK_obj = rows[0][0])

#------------------------------------------------------------
def delete_substance_intake(substance=None):
	cmd = u'DELETE FROM clin.substance_intake WHERE pk = %(pk)s'
	gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': {'pk': substance}}])
	return True

#------------------------------------------------------------
# AMTS formatting
#------------------------------------------------------------
def format_substance_intake_as_amts_latex(intake=None, strict=True):

	_esc = gmTools.tex_escape_string

	# %(contains)s & %(brand)s & %(amount)s%(unit)s & %(preparation)s & \multicolumn{4}{l|}{%(schedule)s} & Einheit & %(notes)s & %(aim)s \tabularnewline \hline
	cells = []
	# components
	components = [ c.split('::') for c in intake.containing_drug['components'] ]
	if len(components) > 3:
		cells.append(_esc(u'WS-Kombi.'))
	elif len(components) == 1:
		c = components[0]
		if strict:
			cells.append(u'\\mbox{%s}' % _esc(c[0][:80]))
		else:
			cells.append(u'\\mbox{%s}' % _esc(c[0]))
	else:
		if strict:
			cells.append(u'\\fontsize{10pt}{12pt}\selectfont %s ' % u'\\newline '.join([u'\\mbox{%s}' % _esc(c[0][:80]) for c in components]))
		else:
			cells.append(u'\\fontsize{10pt}{12pt}\selectfont %s ' % u'\\newline '.join([u'\\mbox{%s}' % _esc(c[0]) for c in components]))
	# brand
	if strict:
		cells.append(_esc(intake['brand'][:50]))
	else:
		cells.append(_esc(intake['brand']))
	# Wirkstärken
	if len(components) > 3:
		cells.append(u'')
	elif len(components) == 1:
		c = components[0]
		if strict:
			cells.append(_esc((u'%s%s' % ((u'%s' % c[1]).replace(u'.', u','), c[2]))[:11]))
		else:
			cells.append(_esc(u'%s%s' % ((u'%s' % c[1]).replace(u'.', u','), c[2])))
	else:
		if strict:
			cells.append(u'\\fontsize{10pt}{12pt}\selectfont %s ' % u'\\newline\\ '.join([_esc((u'%s%s' % ((u'%s' % c[1]).replace(u'.', u','), c[2]))[:11]) for c in components]))
		else:
			cells.append(u'\\fontsize{10pt}{12pt}\selectfont %s ' % u'\\newline\\ '.join([_esc(u'%s%s' % ((u'%s' % c[1]).replace(u'.', u','), c[2])) for c in components]))
	# preparation
	if strict:
		cells.append(_esc(intake['preparation'][:7]))
	else:
		cells.append(_esc(intake['preparation']))
	# schedule - for now be simple - maybe later parse 1-1-1-1 etc
	if intake['schedule'] is None:
		cells.append(u'\\multicolumn{4}{p{3.2cm}|}{\\ }')
	else:
		# spec says [:20] but implementation guide says: never trim
		if len(intake['schedule']) > 20:
			cells.append(u'\\multicolumn{4}{>{\\RaggedRight}p{3.2cm}|}{\\fontsize{10pt}{12pt}\selectfont %s}' % _esc(intake['schedule']))
		else:
			cells.append(u'\\multicolumn{4}{>{\\RaggedRight}p{3.2cm}|}{%s}' % _esc(intake['schedule']))
	# Einheit to take
	cells.append(u'')#[:20]
	# notes
	if intake['notes'] is None:
		cells.append(u' ')
	else:
		if strict:
			cells.append(_esc(intake['notes'][:80]))
		else:
			cells.append(u'\\fontsize{10pt}{12pt}\selectfont %s ' % _esc(intake['notes']))
	# aim
	if intake['aim'] is None:
		#cells.append(u' ')
		cells.append(_esc(intake['episode'][:50]))
	else:
		if strict:
			cells.append(_esc(intake['aim'][:50]))
		else:
			cells.append(u'\\fontsize{10pt}{12pt}\selectfont %s ' % _esc(intake['aim']))

	table_row = u' & '.join(cells)
	table_row += u'\\tabularnewline\n\\hline'

	return table_row

#------------------------------------------------------------
def format_substance_intake_as_amts_data(intake=None, strict=True):
	"""
	<M a="Handelsname" fd="freie Formangabe" t="freies Dosierschema" dud="freie Dosiereinheit (Stück Tab)" r="reason" i="info">
		<W w="Metformin" s="500 mg"/>
		<W ...>
	</M>
	"""
	if not strict:
		pass
		# relax length checks

	M_fields = []
	if intake['pk_brand'] is not None:
		M_fields.append(u'a="%s"' % intake['brand'])
	M_fields.append(u'fd="%s"' % intake['preparation'])
	if intake['schedule'] is not None:
		M_fields.append(u't="%s"' % intake['schedule'])
	#M_fields.append(u'dud="%s"' % intake['dose unit, like Stück'])
	if intake['aim'] is None:
		M_fields.append(u'r="%s"' % intake['episode'])
	else:
		M_fields.append(u'r="%s"' % intake['aim'])
	if intake['notes'] is not None:
		M_fields.append(u'i="%s"' % intake['notes'])
	M_line = u'<M %s>' % u' '.join(M_fields)

	if intake['pk_brand'] is None:
		components = [[intake['substance'], intake['amount'], intake['unit'], u'']]
	else:
		components = [ c.split('::') for c in intake.containing_drug['components'] ]
	W_lines = []
	for comp in components:
		W_lines.append(u'<W w="%s" s="%s %s"/>' % (comp[0], comp[1], comp[2]))

	return M_line + u''.join(W_lines) + u'</M>'

#------------------------------------------------------------
def generate_amts_data_template_definition_file(work_dir=None, strict=True):

	_log.debug('generating AMTS data template definition file(workdir=%s, strict=%s)', work_dir, strict)

	if not strict:
		return __generate_enhanced_amts_data_template_definition_file(work_dir = work_dir)

	amts_lines = [ l for l in (u'<MP v="023" U="%s"' % uuid.uuid4().hex + u""" l="de-DE"$<<if_not_empty::$<amts_page_idx::::1>$// a="%s"//::>>$$<<if_not_empty::$<amts_page_idx::::>$// z="$<amts_total_pages::::1>$"//::>>$>
<P g="$<name::%(firstnames)s::45>$" f="$<name::%(lastnames)s::45>$" b="$<date_of_birth::%Y%m%d::8>$"/>
<A
 n="$<<range_of::$<praxis::%(praxis)s,%(branch)s::>$,$<current_provider::::>$::30>>$"
$<praxis_address:: s="%(street)s"::>$
$<praxis_address:: z="%(postcode)s"::>$
$<praxis_address:: c="%(urb)s::>$
$<praxis_comm::workphone// p="%(url)s::20>$
$<praxis_comm::email// e="%(url)s::80>$
 t="$<today::%Y%m%d::8>$"
/>
<O ai="s.S.$<amts_total_pages::::1>$ unten"/>
$<amts_intakes_as_data::::9999999>$
</MP>""").split(u'\n') ]
#$<<if_not_empty::$<allergy_list::%(descriptor)s//,::>$//<O ai="%s"/>::>>$

	amts_fname = gmTools.get_unique_filename (
		prefix = 'gm2amts_data-',
		suffix = '.txt',
		tmp_dir = work_dir
	)
	amts_template = io.open(amts_fname, mode = 'wt', encoding = 'utf8')
	amts_template.write(u'[form]\n')
	amts_template.write(u'template = $template$\n')
	amts_template.write(u''.join(amts_lines))
	amts_template.write(u'\n')
	amts_template.write(u'$template$\n')
	amts_template.close()

	return amts_fname

#------------------------------------------------------------
def __generate_enhanced_amts_data_template_definition_file(work_dir=None):

	amts_lines = [ l for l in (u'<MP v="023" U="%s"' % uuid.uuid4().hex + u""" l="de-DE" a="1" z="1">
<P g="$<name::%(firstnames)s::>$" f="$<name::%(lastnames)s::>$" b="$<date_of_birth::%Y%m%d::8>$"/>
<A
 n="$<praxis::%(praxis)s,%(branch)s::>$,$<current_provider::::>$"
$<praxis_address:: s="%(street)s %(number)s %(subunit)s"::>$
$<praxis_address:: z="%(postcode)s"::>$
$<praxis_address:: c="%(urb)s::>$
$<praxis_comm::workphone// p="%(url)s::>$
$<praxis_comm::email// e="%(url)s::>$
 t="$<today::%Y%m%d::8>$"
/>
<O ai="Seite 1 unten"/>
$<amts_intakes_as_data_enhanced::::9999999>$
</MP>""").split(u'\n') ]
#$<<if_not_empty::$<allergy_list::%(descriptor)s//,::>$//<O ai="%s"/>::>>$

	amts_fname = gmTools.get_unique_filename (
		prefix = 'gm2amts_data-utf8-unabridged-',
		suffix = '.txt',
		tmp_dir = work_dir
	)
	amts_template = io.open(amts_fname, mode = 'wt', encoding = 'utf8')
	amts_template.write(u'[form]\n')
	amts_template.write(u'template = $template$\n')
	amts_template.write(u''.join(amts_lines))
	amts_template.write(u'\n')
	amts_template.write(u'$template$\n')
	amts_template.close()

	return amts_fname

#------------------------------------------------------------
# AMTS v2.0
#------------------------------------------------------------
def format_substance_intake_as_amts_data_v2_0(intake=None, strict=True):

	if not strict:
		pass
		# relax length checks

	fields = []

	# components
	components = [ c.split('::') for c in intake.containing_drug['components'] ]
	if len(components) > 3:
		fields.append(u'WS-Kombi.')
	elif len(components) == 1:
		c = components[0]
		fields.append(c[0][:80])
	else:
		fields.append(u'~'.join([c[0][:80] for c in components]))
	# brand
	fields.append(intake['brand'][:50])
	# Wirkstärken
	if len(components) > 3:
		fields.append(u'')
	elif len(components) == 1:
		c = components[0]
		fields.append((u'%s%s' % (c[1], c[2]))[:11])
	else:
		fields.append(u'~'.join([(u'%s%s' % (c[1], c[2]))[:11] for c in components]))
	# preparation
	fields.append(intake['preparation'][:7])
	# schedule - for now be simple - maybe later parse 1-1-1-1 etc
	fields.append(gmTools.coalesce(intake['schedule'], u'')[:20])
	# Einheit to take
	fields.append(u'')#[:20]
	# notes
	fields.append(gmTools.coalesce(intake['notes'], u'')[:80])
	# aim
	fields.append(gmTools.coalesce(intake['aim'], u'')[:50])

	return u'|'.join(fields)

#------------------------------------------------------------
def calculate_amts_data_check_symbol_v2_0(intakes=None):

	# first char of generic substance or brand name
	first_chars = []
	for intake in intakes:
		first_chars.append(intake['brand'][0])

	# add up_per page
	val_sum = 0
	for first_char in first_chars:
		# ziffer: ascii+7
		if first_char.isdigit():
			val_sum += (ord(first_char) + 7)
		# großbuchstabe: ascii
		# kleinbuchstabe ascii(großbuchstabe)
		if first_char.isalpha():
			val_sum += ord(first_char.upper())
		# other: 0

	# get remainder of sum mod 36
	tmp, remainder = divmod(val_sum, 36)
	# 0-9 -> '0' - '9'
	if remainder < 10:
		return u'%s' % remainder
	# 10-35 -> 'A' - 'Z'
	return chr(remainder + 55)

#------------------------------------------------------------
def generate_amts_data_template_definition_file_v_2_0(work_dir=None, strict=True):

	if not strict:
		return __generate_enhanced_amts_data_template_definition_file(work_dir = work_dir)

	amts_fields = [
		u'MP',
		u'020',	# Version
		u'DE',	# Land
		u'DE',	# Sprache
		u'1',	# Zeichensatz 1 = Ext ASCII (fest) = ISO8859-1 = Latin1
		u'$<today::%Y%m%d::8>$',
		u'$<amts_page_idx::::1>$',				# to be set by code using the template
		u'$<amts_total_pages::::1>$',			# to be set by code using the template
		u'0',	# Zertifizierungsstatus

		u'$<name::%(firstnames)s::45>$',
		u'$<name::%(lastnames)s::45>$',
		u'',	# Patienten-ID
		u'$<date_of_birth::%Y%m%d::8>$',

		u'$<<range_of::$<praxis::%(praxis)s,%(branch)s::>$,$<current_provider::::>$::30>>$',
		u'$<praxis_address::%(street)s %(number)s %(subunit)s|%(postcode)s|%(urb)s::57>$',		# 55+2 because of 2 embedded "|"s
		u'$<praxis_comm::workphone::20>$',
		u'$<praxis_comm::email::80>$',

		#u'264 $<allergy_state::::21>$',				# param 1, Allergien 25-4 (4 for "264 ", spec says max of 25)
		u'264 Seite $<amts_total_pages::::1>$ unten',	# param 1, Allergien 25-4 (4 for "264 ", spec says max of 25)
		u'', # param 2, not used currently
		u'', # param 3, not used currently

		# Medikationseinträge
		u'$<amts_intakes_as_data::::9999999>$',

		u'$<amts_check_symbol::::1>$',	# Prüfzeichen, value to be set by code using the template, *per page* !
		u'#@',							# Endesymbol
	]

	amts_fname = gmTools.get_unique_filename (
		prefix = 'gm2amts_data-',
		suffix = '.txt',
		tmp_dir = work_dir
	)
	amts_template = io.open(amts_fname, mode = 'wt', encoding = 'utf8')
	amts_template.write(u'[form]\n')
	amts_template.write(u'template = $template$\n')
	amts_template.write(u'|'.join(amts_fields))
	amts_template.write(u'\n')
	amts_template.write(u'$template$\n')
	amts_template.close()

	return amts_fname

#------------------------------------------------------------
def __generate_enhanced_amts_data_template_definition_file_v_2_0(work_dir=None):

	amts_fields = [
		u'MP',
		u'020',	# Version
		u'DE',	# Land
		u'DE',	# Sprache
		u'1',	# Zeichensatz 1 = Ext ASCII (fest) = ISO8859-1 = Latin1
		u'$<today::%Y%m%d::8>$',
		u'1',	# idx of this page
		u'1',	# total pages
		u'0',	# Zertifizierungsstatus

		u'$<name::%(firstnames)s::>$',
		u'$<name::%(lastnames)s::>$',
		u'',	# Patienten-ID
		u'$<date_of_birth::%Y%m%d::8>$',

		u'$<praxis::%(praxis)s,%(branch)s::>$,$<current_provider::::>$',
		u'$<praxis_address::%(street)s %(number)s %(subunit)s::>$',
		u'$<praxis_address::%(postcode)s::>$',
		u'$<praxis_address::%(urb)s::>$',
		u'$<praxis_comm::workphone::>$',
		u'$<praxis_comm::email::>$',

		#u'264 $<allergy_state::::>$', 					# param 1, Allergien
		u'264 Seite 1 unten',							# param 1, Allergien
		u'', # param 2, not used currently
		u'', # param 3, not used currently

		# Medikationseinträge
		u'$<amts_intakes_as_data_enhanced::::>$',

		u'$<amts_check_symbol::::1>$',	# Prüfzeichen, value to be set by code using the template, *per page* !
		u'#@',							# Endesymbol
	]

	amts_fname = gmTools.get_unique_filename (
		prefix = 'gm2amts_data-utf8-unabridged-',
		suffix = '.txt',
		tmp_dir = work_dir
	)
	amts_template = io.open(amts_fname, mode = 'wt', encoding = 'utf8')
	amts_template.write(u'[form]\n')
	amts_template.write(u'template = $template$\n')
	amts_template.write(u'|'.join(amts_fields))
	amts_template.write(u'\n')
	amts_template.write(u'$template$\n')
	amts_template.close()

	return amts_fname

#------------------------------------------------------------
# other formatting
#------------------------------------------------------------
def format_substance_intake_notes(emr=None, output_format=u'latex', table_type=u'by-brand'):

	tex = u'\\noindent %s\n' % _('Additional notes')
	tex += u'%%%% requires "\\usepackage{longtable}"\n'
	tex += u'%%%% requires "\\usepackage{tabu}"\n'
	tex += u'\\noindent \\begin{longtabu} to \\textwidth {|X[,L]|r|X[,L]|}\n'
	tex += u'\\hline\n'
	tex += u'%s {\\scriptsize (%s)} & %s & %s \\tabularnewline \n' % (_('Substance'), _('Brand'), _('Strength'), _('Aim'))
	tex += u'\\hline\n'
	tex += u'\\hline\n'
	tex += u'%s\n'
	tex += u'\\end{longtabu}\n'

	current_meds = emr.get_current_medications (
		include_inactive = False,
		include_unapproved = False,
		order_by = u'brand, substance'
	)

	# create lines
	lines = []
	for med in current_meds:
		brand = u'{\\small :} {\\tiny %s}' % gmTools.tex_escape_string(med['brand'])
		if med['aim'] is None:
			aim = u''
		else:
			aim = u'{\\scriptsize %s}' % gmTools.tex_escape_string(med['aim'])
		lines.append(u'%s ({\\small %s}%s) & %s%s & %s \\tabularnewline\n \\hline' % (
			gmTools.tex_escape_string(med['substance']),
			gmTools.tex_escape_string(med['preparation']),
			brand,
			med['amount'],
			gmTools.tex_escape_string(med['unit']),
			aim
		))

	return tex % u'\n'.join(lines)

#------------------------------------------------------------
def format_substance_intake(emr=None, output_format=u'latex', table_type=u'by-brand'):

	# FIXME: add intake_instructions

	tex = u'\\noindent %s {\\tiny (%s)}\n' % (
		gmTools.tex_escape_string(_('Medication list')),
		gmTools.tex_escape_string(_('ordered by brand'))
	)
	tex += u'%% requires "\\usepackage{longtable}"\n'
	tex += u'%% requires "\\usepackage{tabu}"\n'
	tex += u'\\begin{longtabu} to \\textwidth {|X[-1,L]|X[2.5,L]|}\n'
	tex += u'\\hline\n'
	tex += u'%s & %s \\tabularnewline \n' % (
		gmTools.tex_escape_string(_('Drug')),
		gmTools.tex_escape_string(_('Regimen / Advice'))
	)
	tex += u'\\hline\n'
	tex += u'%s\n'
	tex += u'\\end{longtabu}\n'

	current_meds = emr.get_current_medications (
		include_inactive = False,
		include_unapproved = False,
		order_by = u'brand, substance'
	)

	# aggregate data
	line_data = {}
	for med in current_meds:
		identifier = gmTools.coalesce(med['brand'], med['substance'])

		try:
			line_data[identifier]
		except KeyError:
			line_data[identifier] = {'brand': u'', 'preparation': u'', 'schedule': u'', 'notes': [], 'strengths': []}

		line_data[identifier]['brand'] = identifier
		line_data[identifier]['strengths'].append(u'%s %s%s' % (med['substance'][:20], med['amount'], med['unit'].strip()))
		line_data[identifier]['preparation'] = med['preparation']
		if med['duration'] is not None:
			line_data[identifier]['schedule'] = u'%s: ' % gmDateTime.format_interval(med['duration'], gmDateTime.acc_days, verbose = True)
		line_data[identifier]['schedule'] += gmTools.coalesce(med['schedule'], u'')
		if med['notes'] is not None:
			if med['notes'] not in line_data[identifier]['notes']:
				line_data[identifier]['notes'].append(med['notes'])

	# create lines
	already_seen = []
	lines = []
	line1_template = u'\\rule{0pt}{3ex}{\\Large %s} %s & %s \\tabularnewline'
	line2_template = u'{\\tiny %s}                     & {\\scriptsize %s} \\tabularnewline'
	line3_template = u'                                & {\\scriptsize %s} \\tabularnewline'

	for med in current_meds:
		identifier = gmTools.coalesce(med['brand'], med['substance'])

		if identifier in already_seen:
			continue

		already_seen.append(identifier)

		lines.append (line1_template % (
			gmTools.tex_escape_string(line_data[identifier]['brand']),
			gmTools.tex_escape_string(line_data[identifier]['preparation']),
			gmTools.tex_escape_string(line_data[identifier]['schedule'])
		))

		strengths = gmTools.tex_escape_string(u' / '.join(line_data[identifier]['strengths']))
		if len(line_data[identifier]['notes']) == 0:
			first_note = u''
		else:
			first_note = gmTools.tex_escape_string(line_data[identifier]['notes'][0])
		lines.append(line2_template % (strengths, first_note))
		if len(line_data[identifier]['notes']) > 1:
			for note in line_data[identifier]['notes'][1:]:
				lines.append(line3_template % gmTools.tex_escape_string(note))

		lines.append(u'\\hline')

	return tex % u'\n'.join(lines)

#============================================================
# drug components
#------------------------------------------------------------
_SQL_get_drug_components = u'SELECT * FROM ref.v_drug_components WHERE %s'

class cDrugComponent(gmBusinessDBObject.cBusinessDBObject):

	_cmd_fetch_payload = _SQL_get_drug_components % u'pk_component = %s'
	_cmds_store_payload = [
		u"""UPDATE ref.lnk_dose2drug SET
				fk_brand = %(pk_brand)s,
				fk_dose = %(pk_dose)s
			WHERE
				pk = %(pk_component)s
					AND
				NOT EXISTS (
					SELECT 1
					FROM clin.substance_intake
					WHERE fk_drug_component = %(pk_component)s
					LIMIT 1
				)
					AND
				xmin = %(xmin_lnk_dose2drug)s
			RETURNING
				xmin AS xmin_lnk_dose2drug
		"""
	]
	_updatable_fields = [
		u'pk_brand',
		u'pk_dose'
	]
	#--------------------------------------------------------
	def format(self, left_margin=0):
		lines = []
		lines.append(u'%s %s%s/%s' % (
			self._payload[self._idx['substance']],
			self._payload[self._idx['amount']],
			self._payload[self._idx['unit']],
			gmTools.coalesce(gmTools.coalesce(self._payload[self._idx['dose_unit']], _('delivery unit of %s') % self._payload[self._idx['preparation']]))
		))
		lines.append(_('Component of %s (%s)') % (
			self._payload[self._idx['brand']],
			self._payload[self._idx['preparation']]
		))
		if self._payload[self._idx['intake_instructions']] is not None:
			lines.append(_(u'Instructions: %s') % self._payload[self._idx['intake_instructions']])
		if self._payload[self._idx['atc_substance']] is not None:
			lines.append(_('ATC (substance): %s') % self._payload[self._idx['atc_substance']])
		if self._payload[self._idx['atc_brand']] is not None:
			lines.append(_('ATC (brand): %s') % self._payload[self._idx['atc_brand']])
		if self._payload[self._idx['external_code']] is not None:
			lines.append(u'%s: %s' % (
				self._payload[self._idx['external_code_type']],
				self._payload[self._idx['external_code']]
			))
		if self._payload[self._idx['is_fake_brand']]:
			lines.append(_('this is a component of a fake brand'))

		return (u' ' * left_margin) + (u'\n' + (u' ' * left_margin)).join(lines)
	#--------------------------------------------------------
	def exists_as_intake(self, pk_patient=None):
		return substance_intake_exists (
			pk_component = self._payload[self._idx['pk_component']],
			pk_identity = pk_patient
		)

	#--------------------------------------------------------
	def turn_into_intake(self, emr=None, encounter=None, episode=None):
		return create_substance_intake (
			pk_component = self._payload[self._idx['pk_component']],
			pk_encounter = encounter,
			pk_episode = episode
		)

	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def _get_containing_drug(self):
		return cBrandedDrug(aPK_obj = self._payload[self._idx['pk_brand']])

	containing_drug = property(_get_containing_drug, lambda x:x)
	#--------------------------------------------------------
	def _get_is_in_use_by_patients(self):
		return self._payload[self._idx['is_in_use']]

	is_in_use_by_patients = property(_get_is_in_use_by_patients, lambda x:x)
	#--------------------------------------------------------
	def _get_substance_dose(self):
		return cSubstanceDose(aPK_obj = self._payload[self._idx['pk_dose']])

	substance_dose =  property(_get_substance_dose, lambda x:x)

	#--------------------------------------------------------
	def _get_substance(self):
		return cSubstance(aPK_obj = self._payload[self._idx['pk_substance']])

	substance =  property(_get_substance, lambda x:x)

#------------------------------------------------------------
def get_drug_components():
	cmd = _SQL_get_drug_components % u'true ORDER BY brand, substance'
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd}], get_col_idx = True)
	return [ cDrugComponent(row = {'data': r, 'idx': idx, 'pk_field': 'pk_component'}) for r in rows ]

#------------------------------------------------------------
class cDrugComponentMatchProvider(gmMatchProvider.cMatchProvider_SQL2):

	_pattern = regex.compile(r'^\D+\s*\d+$', regex.UNICODE | regex.LOCALE)

	_query_desc_only = u"""
		SELECT DISTINCT ON (list_label)
			r_vdc1.pk_component
				AS data,
			(r_vdc1.substance || ' '
				|| r_vdc1.amount || r_vdc1.unit || ' '
				|| r_vdc1.preparation || ' ('
				|| r_vdc1.brand || ' ['
					|| (
						SELECT array_to_string(array_agg(r_vdc2.amount), ' / ')
						FROM ref.v_drug_components r_vdc2
						WHERE r_vdc2.pk_brand = r_vdc1.pk_brand
					)
				|| ']'
			 || ')'
			)	AS field_label,
			(r_vdc1.substance || ' '
				|| r_vdc1.amount || r_vdc1.unit || ' '
				|| r_vdc1.preparation || ' ('
				|| r_vdc1.brand || ' ['
					|| (
						SELECT array_to_string(array_agg(r_vdc2.amount), ' / ')
						FROM ref.v_drug_components r_vdc2
						WHERE r_vdc2.pk_brand = r_vdc1.pk_brand
					)
				|| ']'
			 || ')'
			)	AS list_label
		FROM ref.v_drug_components r_vdc1
		WHERE
			r_vdc1.substance %(fragment_condition)s
				OR
			r_vdc1.brand %(fragment_condition)s
		ORDER BY list_label
		LIMIT 50"""

	_query_desc_and_amount = u"""
		SELECT DISTINCT ON (list_label)
			pk_component AS data,
			(r_vdc1.substance || ' '
				|| r_vdc1.amount || r_vdc1.unit || ' '
				|| r_vdc1.preparation || ' ('
				|| r_vdc1.brand || ' ['
					|| (
						SELECT array_to_string(array_agg(r_vdc2.amount), ' / ')
						FROM ref.v_drug_components r_vdc2
						WHERE r_vdc2.pk_brand = r_vdc1.pk_brand
					)
				|| ']'
			 || ')'
			)	AS field_label,
			(r_vdc1.substance || ' '
				|| r_vdc1.amount || r_vdc1.unit || ' '
				|| r_vdc1.preparation || ' ('
				|| r_vdc1.brand || ' ['
					|| (
						SELECT array_to_string(array_agg(r_vdc2.amount), ' / ')
						FROM ref.v_drug_components r_vdc2
						WHERE r_vdc2.pk_brand = r_vdc1.pk_brand
					)
				|| ']'
			 || ')'
			)	AS list_label
		FROM ref.v_drug_components
		WHERE
			%(fragment_condition)s
		ORDER BY list_label
		LIMIT 50"""
	#--------------------------------------------------------
	def getMatchesByPhrase(self, aFragment):
		"""Return matches for aFragment at start of phrases."""

		if cDrugComponentMatchProvider._pattern.match(aFragment):
			self._queries = [cDrugComponentMatchProvider._query_desc_and_amount]
			fragment_condition = """(substance ILIKE %(desc)s OR brand ILIKE %(desc)s)
				AND
			amount::text ILIKE %(amount)s"""
			self._args['desc'] = u'%s%%' % regex.sub(r'\s*\d+$', u'', aFragment)
			self._args['amount'] = u'%s%%' % regex.sub(r'^\D+\s*', u'', aFragment)
		else:
			self._queries = [cDrugComponentMatchProvider._query_desc_only]
			fragment_condition = u"ILIKE %(fragment)s"
			self._args['fragment'] = u"%s%%" % aFragment

		return self._find_matches(fragment_condition)
	#--------------------------------------------------------
	def getMatchesByWord(self, aFragment):
		"""Return matches for aFragment at start of words inside phrases."""

		if cDrugComponentMatchProvider._pattern.match(aFragment):
			self._queries = [cDrugComponentMatchProvider._query_desc_and_amount]

			desc = regex.sub(r'\s*\d+$', u'', aFragment)
			desc = gmPG2.sanitize_pg_regex(expression = desc, escape_all = False)

			fragment_condition = """(substance ~* %(desc)s OR brand ~* %(desc)s)
				AND
			amount::text ILIKE %(amount)s"""

			self._args['desc'] = u"( %s)|(^%s)" % (desc, desc)
			self._args['amount'] = u'%s%%' % regex.sub(r'^\D+\s*', u'', aFragment)
		else:
			self._queries = [cDrugComponentMatchProvider._query_desc_only]
			fragment_condition = u"~* %(fragment)s"
			aFragment = gmPG2.sanitize_pg_regex(expression = aFragment, escape_all = False)
			self._args['fragment'] = u"( %s)|(^%s)" % (aFragment, aFragment)

		return self._find_matches(fragment_condition)
	#--------------------------------------------------------
	def getMatchesBySubstr(self, aFragment):
		"""Return matches for aFragment as a true substring."""

		if cDrugComponentMatchProvider._pattern.match(aFragment):
			self._queries = [cDrugComponentMatchProvider._query_desc_and_amount]
			fragment_condition = """(substance ILIKE %(desc)s OR brand ILIKE %(desc)s)
				AND
			amount::text ILIKE %(amount)s"""
			self._args['desc'] = u'%%%s%%' % regex.sub(r'\s*\d+$', u'', aFragment)
			self._args['amount'] = u'%s%%' % regex.sub(r'^\D+\s*', u'', aFragment)
		else:
			self._queries = [cDrugComponentMatchProvider._query_desc_only]
			fragment_condition = u"ILIKE %(fragment)s"
			self._args['fragment'] = u"%%%s%%" % aFragment

		return self._find_matches(fragment_condition)

#============================================================
# branded drugs
#------------------------------------------------------------
_SQL_get_branded_drug = u"SELECT * FROM ref.v_branded_drugs WHERE %s"

class cBrandedDrug(gmBusinessDBObject.cBusinessDBObject):
	"""Represents a drug as marketed by a manufacturer."""

	_cmd_fetch_payload = _SQL_get_branded_drug % u'pk_brand = %s'
	_cmds_store_payload = [
		u"""UPDATE ref.branded_drug SET
				description = %(brand)s,
				preparation = %(preparation)s,
				atc_code = gm.nullify_empty_string(%(atc)s),
				external_code = gm.nullify_empty_string(%(external_code)s),
				external_code_type = gm.nullify_empty_string(%(external_code_type)s),
				is_fake = %(is_fake_brand)s,
				fk_data_source = %(pk_data_source)s
			WHERE
				pk = %(pk_brand)s
					AND
				xmin = %(xmin_branded_drug)s
			RETURNING
				xmin AS xmin_branded_drug
		"""
	]
	_updatable_fields = [
		u'brand',
		u'preparation',
		u'atc',
		u'is_fake_brand',
		u'external_code',
		u'external_code_type',
		u'pk_data_source'
	]
	#--------------------------------------------------------
	def format(self, left_margin=0):
		lines = []
		lines.append(u'%s (%s)' % (
			self._payload[self._idx['brand']],
			self._payload[self._idx['preparation']]
			)
		)
		if self._payload[self._idx['atc']] is not None:
			lines.append(u'ATC: %s' % self._payload[self._idx['atc']])
		if self._payload[self._idx['external_code']] is not None:
			lines.append(u'%s: %s' % (self._payload[self._idx['external_code_type']], self._payload[self._idx['external_code']]))
		if self._payload[self._idx['components']] is not None:
			lines.append(_('Components:'))
			for comp in self._payload[self._idx['components']]:
				lines.append(u' ' + comp)
		if self._payload[self._idx['is_fake_brand']]:
			lines.append(u'')
			lines.append(_('this is a fake brand'))
		if self.is_vaccine:
			lines.append(_('this is a vaccine'))

		return (u' ' * left_margin) + (u'\n' + (u' ' * left_margin)).join(lines)

	#--------------------------------------------------------
	def save_payload(self, conn=None):
		success, data = super(self.__class__, self).save_payload(conn = conn)

		if not success:
			return (success, data)

		if self._payload[self._idx['atc']] is not None:
			atc = self._payload[self._idx['atc']].strip()
			if atc != u'':
				gmATC.propagate_atc (
					substance = self._payload[self._idx['brand']].strip(),
					atc = atc
				)

		return (success, data)

	#--------------------------------------------------------
	def set_substance_doses_as_components(self, substance_doses=None):
		if self.is_in_use_by_patients:
			return False

		pk_doses2keep = [ s['pk_dose'] for s in substance_doses ]
		args = {'pk_brand': self._payload[self._idx['pk_brand']]}
		queries = []

		# INSERT those which are not there yet
		cmd = u"""
			INSERT INTO ref.lnk_dose2drug (
				fk_brand,
				fk_dose
			)
			SELECT
				%(pk_brand)s,
				%(pk_dose)s
			WHERE NOT EXISTS (
				SELECT 1 FROM ref.lnk_dose2drug
				WHERE
					fk_brand = %(pk_brand)s
						AND
					fk_dose = %(pk_dose)s
			)"""
		for pk in pk_doses2keep:
			args['pk_dose'] = pk
			queries.append({'cmd': cmd, 'args': args})

		# DELETE those that don't belong anymore
		args['doses2keep'] = tuple(pk_doses2keep)
		cmd = u"""
			DELETE FROM ref.lnk_dose2drug
			WHERE
				fk_brand = %(pk_brand)s
					AND
				fk_dose NOT IN %(doses2keep)s"""
		queries.append({'cmd': cmd, 'args': args})

		gmPG2.run_rw_queries(queries = queries)
		self.refetch_payload()

		return True

	#--------------------------------------------------------
	def add_component(self, substance=None, atc=None, amount=None, unit=None, dose_unit=None, pk_dose=None, pk_substance=None):

		if pk_dose is None:
			if pk_substance is None:
				pk_dose = create_substance_dose(substance = substance, atc = atc, amount = amount, unit = unit, dose_unit = dose_unit)['pk_dose']
			else:
				pk_dose = create_substance_dose(pk_substance = pk_substance, atc = atc, amount = amount, unit = unit, dose_unit = dose_unit)['pk_dose']

		args = {
			'pk_dose': pk_dose,
			'pk_brand': self.pk_obj
		}

		cmd = u"""
			INSERT INTO ref.lnk_dose2drug (fk_brand, fk_dose)
			SELECT
				%(pk_brand)s,
				%(pk_dose)s
			WHERE NOT EXISTS (
				SELECT 1 FROM ref.lnk_dose2drug
				WHERE
					fk_brand = %(pk_brand)s
						AND
					fk_dose = %(pk_dose)s
			)"""
		gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])
		self.refetch_payload()

	#------------------------------------------------------------
	def remove_component(self, pk_dose=None, pk_substance=None, pk_component=None):
		if len(self._payload[self._idx['components']]) == 1:
			_log.error('will not remove the only component of a drug')
			return False

		args = {'pk_brand': self.pk_obj, 'pk_substance': pk_substance, 'pk_dose': pk_dose, 'pk_component': pk_component}

		if pk_component is None:
			if pk_dose is None:
				cmd = u"SELECT pk FROM ref.dose WHERE fk_substance = %(pk_substance)s"
				rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}])
				pk_dose = rows[0][0]
			cmd = u"""
				DELETE FROM ref.lnk_dose2drug
				WHERE
					fk_brand = %(pk_brand)s
						AND
					fk_dose = %(pk_dose)s
						AND
					NOT EXISTS (
						SELECT 1 FROM clin.v_substance_intakes
						WHERE pk_dose = %(pk_dose)s
						LIMIT 1
					)"""
		else:
			cmd = u"""
				DELETE FROM ref.lnk_dose2drug
				WHERE
					pk = %(pk_component)s
						AND
					NOT EXISTS (
						SELECT 1 FROM clin.substance_intake
						WHERE fk_drug_component = %(pk_component)s
						LIMIT 1
					)"""

		gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])
		self.refetch_payload()
		return True

	#--------------------------------------------------------
	def exists_as_intake(self, pk_patient=None):
		return substance_intake_exists (
			pk_brand = self._payload[self._idx['pk_brand']],
			pk_identity = pk_patient
		)

	#--------------------------------------------------------
	def turn_into_intake(self, emr=None, encounter=None, episode=None):
		return create_substance_intake (
			pk_brand = self._payload[self._idx['pk_brand']],
			pk_encounter = encounter,
			pk_episode = episode
		)

	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def _get_external_code(self):
		if self._payload[self._idx['external_code']] is None:
			return None
		return self._payload[self._idx['external_code']]

	external_code = property(_get_external_code, lambda x:x)

	#--------------------------------------------------------
	def _get_external_code_type(self):
		# FIXME: maybe evaluate fk_data_source ?
		if self._payload[self._idx['external_code_type']] is None:
			return None
		return self._payload[self._idx['external_code_type']]

	external_code_type = property(_get_external_code_type, lambda x:x)

	#--------------------------------------------------------
	def _get_components(self):
		cmd = _SQL_get_drug_components % u'pk_brand = %(brand)s'
		args = {'brand': self._payload[self._idx['pk_brand']]}
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)
		return [ cDrugComponent(row = {'data': r, 'idx': idx, 'pk_field': 'pk_component'}) for r in rows ]

	components = property(_get_components, lambda x:x)

	#--------------------------------------------------------
	def _get_components_as_doses(self):
		if self._payload[self._idx['pk_doses']] is None:
			return []
		cmd = _SQL_get_substance_dose % u'pk_dose IN %(pks)s'
		args = {'pks': tuple(self._payload[self._idx['pk_doses']])}
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)
		return [ cSubstanceDose(row = {'data': r, 'idx': idx, 'pk_field': 'pk_dose'}) for r in rows ]

	components_as_doses = property(_get_components_as_doses, lambda x:x)

	#--------------------------------------------------------
	def _get_components_as_substances(self):
		if self._payload[self._idx['pk_substances']] is None:
			return []
		cmd = _SQL_get_substance % u'pk IN %(pks)s'
		args = {'pks': tuple(self._payload[self._idx['pk_substances']])}
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)
		return [ cConsumableSubstance(row = {'data': r, 'idx': idx, 'pk_field': 'pk'}) for r in rows ]

	components_as_substances = property(_get_components_as_substances, lambda x:x)

	#--------------------------------------------------------
	def _get_is_fake_brand(self):
		return self._payload[self._idx['is_fake_brand']]

	is_fake_brand = property(_get_is_fake_brand, lambda x:x)

	#--------------------------------------------------------
	def _get_is_vaccine(self):
		cmd = u'SELECT EXISTS (SELECT 1 FROM clin.vaccine WHERE fk_brand = %(fk_brand)s)'
		args = {'fk_brand': self._payload[self._idx['pk_brand']]}
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = False)
		return rows[0][0]

	is_vaccine = property(_get_is_vaccine, lambda x:x)

	#--------------------------------------------------------
	def _get_is_in_use_by_patients(self):
		cmd = u"""
			SELECT EXISTS (
				SELECT 1 FROM clin.substance_intake WHERE
					fk_drug_component IN (
						SELECT pk FROM ref.lnk_dose2drug WHERE fk_brand = %(pk)s
					)
				LIMIT 1
			)"""
		args = {'pk': self.pk_obj}
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = False)
		return rows[0][0]

	is_in_use_by_patients = property(_get_is_in_use_by_patients, lambda x:x)

#------------------------------------------------------------
def get_branded_drugs():
	cmd = _SQL_get_branded_drug % u'TRUE ORDER BY brand'
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd}], get_col_idx = True)
	return [ cBrandedDrug(row = {'data': r, 'idx': idx, 'pk_field': 'pk_brand'}) for r in rows ]

#------------------------------------------------------------
def get_drug_by_brand(brand_name=None, preparation=None):
	args = {'brand': brand_name, 'prep': preparation}
	cmd = u'SELECT pk FROM ref.branded_drug WHERE lower(description) = lower(%(brand)s) AND lower(preparation) = lower(%(prep)s)'
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = False)
	if len(rows) == 0:
		return None
	return cBrandedDrug(aPK_obj = rows[0]['pk'])

#------------------------------------------------------------
def create_branded_drug(brand_name=None, preparation=None, return_existing=False):

	if preparation is None:
		preparation = _('units')

	if preparation.strip() == u'':
		preparation = _('units')

	if return_existing:
		drug = get_drug_by_brand(brand_name = brand_name, preparation = preparation)
		if drug is not None:
			return drug

	cmd = u'INSERT INTO ref.branded_drug (description, preparation) VALUES (%(brand)s, %(prep)s) RETURNING pk'
	args = {'brand': brand_name, 'prep': preparation}
	rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}], return_data = True, get_col_idx = False)

	return cBrandedDrug(aPK_obj = rows[0]['pk'])

#------------------------------------------------------------
def delete_branded_drug(pk_brand=None):
	queries = []
	# delete components
	cmd = u"""
		DELETE FROM ref.lnk_dose2drug
		WHERE
			fk_brand = %(pk)s
				AND
			NOT EXISTS (
				SELECT 1
				FROM clin.v_substance_intakes
				WHERE pk_brand = %(pk)s
				LIMIT 1
			)"""
	queries.append({'cmd': cmd, 'args': args})
	# delete drug
	cmd = u"""
		DELETE FROM ref.branded_drug
		WHERE
			pk = %(pk)s
				AND
			NOT EXISTS (
				SELECT 1 FROM clin.v_substance_intakes
				WHERE pk_brand = %(pk)s
				LIMIT 1
			)"""
	args = {'pk': pk_brand}
	queries.append({'cmd': cmd, 'args': args})
	gmPG2.run_rw_queries(queries = queries)

#============================================================
# convenience functions
#------------------------------------------------------------
def create_default_medication_history_episode(pk_health_issue=None, encounter=None, link_obj=None):
	return gmEMRStructItems.create_episode (
		pk_health_issue = pk_health_issue,
		episode_name = DEFAULT_MEDICATION_HISTORY_EPISODE,
		is_open = False,
		allow_dupes = False,
		encounter = encounter,
		link_obj = link_obj
	)

#------------------------------------------------------------
def get_tobacco():
	tobacco = create_branded_drug (
		brand_name = _(u'nicotine'),
		preparation = _(u'tobacco'),
		return_existing = True
	)
	tobacco['is_fake_brand'] = True
	tobacco.save()
	nicotine = create_substance_dose_by_atc (
		substance = _('nicotine'),
		atc = gmATC.ATC_NICOTINE,
		amount = 1,
		unit = u'pack',
		dose_unit = u'year'
	)
	tobacco.set_substance_doses_as_components(substance_doses = [nicotine])
	return tobacco

#------------------------------------------------------------
def get_alcohol():
	drink = create_branded_drug (
		brand_name = _(u'alcohol'),
		preparation = _(u'liquid'),
		return_existing = True
	)
	drink['is_fake_brand'] = True
	drink.save()
	ethanol = create_substance_dose_by_atc (
		substance = _(u'ethanol'),
		atc = gmATC.ATC_ETHANOL,
		amount = 1,
		unit = u'g',
		dose_unit = u'ml'
	)
	drink.set_substance_doses_as_components(substance_doses = [ethanol])
	return drink

#------------------------------------------------------------
def get_other_drug(name=None, pk_dose=None):
	drug = create_branded_drug (
		brand_name = name,
		preparation = _(u'unit'),
		return_existing = True
	)
	drug['is_fake_brand'] = True
	drug.save()
	if pk_dose is None:
		content = create_substance_dose (
			substance = name,
			amount = 1,
			unit = _(u'unit'),
			dose_unit = _(u'unit')
		)
	else:
		content = {'pk_dose': pk_dose}		#cSubstanceDose(aPK_obj = pk_dose)
	drug.set_substance_doses_as_components(substance_doses = [content])
	return drug

#============================================================
# substance doses
#------------------------------------------------------------
_SQL_get_substance_dose = u"SELECT * FROM ref.v_substance_doses WHERE %s"

class cSubstanceDose(gmBusinessDBObject.cBusinessDBObject):

	_cmd_fetch_payload = _SQL_get_substance_dose % u"pk_dose = %s"
	_cmds_store_payload = [
		u"""UPDATE ref.dose SET
				amount = %(amount)s,
				unit = %(unit)s,
				dose_unit = gm.nullify_empty_string(%(dose_unit)s)
			WHERE
				pk = %(pk_dose)s
					AND
				xmin = %(xmin_dose)s
			RETURNING
				xmin as xmin_dose,
				pk as pk_dose
		"""
	]
	_updatable_fields = [
		u'amount',
		u'unit',
		u'dose_unit'
	]
	#--------------------------------------------------------
	def format(self, left_margin=0):
		return (u' ' * left_margin) + u'%s: %s %s%s/%s%s%s' % (
			_('Substance dose'),
			self._payload[self._idx['substance']],
			self._payload[self._idx['amount']],
			self._payload[self._idx['unit']],
			gmTools.coalesce(gmTools.coalesce(self._payload[self._idx['dose_unit']], _('delivery unit'))),
			gmTools.coalesce(self._payload[self._idx['atc_substance']], u'', u' [%s]'),
			gmTools.coalesce(self._payload[self._idx['intake_instructions']], u'', u'\n' + (u' ' * left_margin) + u' ' + _(u'Instructions: %s'))
		)

	#--------------------------------------------------------
	def exists_as_intake(self, pk_patient=None):
		return substance_intake_exists (
			pk_dose = self.pk_obj,
			pk_identity = pk_patient
		)

	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def _get_is_in_use_by_patients(self):
		cmd = u"""
			SELECT EXISTS (
				SELECT 1
				FROM clin.v_substance_intakes
				WHERE pk_substance = %(pk)s
				LIMIT 1
			)"""
		args = {'pk': self.pk_obj}

		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = False)
		return rows[0][0]

	is_in_use_by_patients = property(_get_is_in_use_by_patients, lambda x:x)
	#--------------------------------------------------------
	def _get_is_drug_component(self):
		cmd = u"""
			SELECT EXISTS (
				SELECT 1
				FROM ref.v_drug_components
				WHERE pk_substance = %(pk)s
				LIMIT 1
			)"""
		args = {'pk': self.pk_obj}

		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = False)
		return rows[0][0]

	is_drug_component = property(_get_is_drug_component, lambda x:x)

#------------------------------------------------------------
def get_substance_doses(order_by=None):
	if order_by is None:
		order_by = u'true'
	else:
		order_by = u'true ORDER BY %s' % order_by
	cmd = _SQL_get_substance_dose % order_by
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd}], get_col_idx = True)
	return [ cSubstanceDose(row = {'data': r, 'idx': idx, 'pk_field': 'pk_dose'}) for r in rows ]

#------------------------------------------------------------
def create_substance_dose(pk_substance=None, substance=None, atc=None, amount=None, unit=None, dose_unit=None):

	if [pk_substance, substance].count(None) != 1:
		raise ValueError('exctly one of <pk_substance> and <substance> must be None')

	converted, amount = gmTools.input2decimal(amount)
	if not converted:
		raise ValueError('<amount> must be a number: %s (%s)', amount, type(amount))

	if pk_substance is None:
		pk_substance = create_substance(substance = substance, atc = atc)['pk']

	args = {
		'pk_subst': pk_substance,
		'amount': amount,
		'unit': unit.strip(),
		'dose_unit': dose_unit.strip()
	}
	cmd = u"""
		SELECT pk FROM ref.dose
		WHERE
			fk_substance = %(pk_subst)s
				AND
			amount = %(amount)s
				AND
			unit = %(unit)s
				AND
			dose_unit IS NOT DISTINCT FROM gm.nullify_empty_string(%(dose_unit)s)
		"""
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}])

	if len(rows) == 0:
		cmd = u"""
			INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit) VALUES (
				%(pk_subst)s,
				%(amount)s,
				gm.nullify_empty_string(%(unit)s),
				gm.nullify_empty_string(%(dose_unit)s)
			) RETURNING pk"""
		rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}], return_data = True, get_col_idx = False)

	return cSubstanceDose(aPK_obj = rows[0]['pk'])

#------------------------------------------------------------
def create_substance_dose_by_atc(substance=None, atc=None, amount=None, unit=None, dose_unit=None):
	return create_substance_dose (
		pk_substance = create_substance_by_atc(substance = substance, atc = atc)['pk'],
		amount = amount,
		unit = unit,
		dose_unit = dose_unit
	)

#------------------------------------------------------------
def delete_substance_dose(pk_dose=None):
	args = {'pk': pk_dose}
	cmd = u"""
		DELETE FROM ref.dose WHERE
			pk = %(pk_dose)s
				AND
			-- must not currently be used with a patient
			NOT EXISTS (
				SELECT 1 FROM clin.v_substance_intakes
				WHERE pk_dose = %(pk_dose)s
				LIMIT 1
			)
				AND
			-- must not currently be linked to a drug
			NOT EXISTS (
				SELECT 1 FROM ref.lnk_dose2drug
				WHERE fk_dose = %(pk_dose)s
				LIMIT 1
			)
	"""
	gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])
	return True

#============================================================
# main
#------------------------------------------------------------
if __name__ == "__main__":

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	from Gnumed.pycommon import gmLog2
	#from Gnumed.pycommon import gmI18N

	gmI18N.activate_locale()
#	gmDateTime.init()

	#--------------------------------------------------------
	# generic
	#--------------------------------------------------------
	def test_create_substance_intake():
		drug = create_substance_intake (
			pk_component = 2,
			pk_encounter = 1,
			pk_episode = 1
		)
		print drug

	#--------------------------------------------------------
	def test_get_substances():
		for s in get_substances():
			#print s
			print s.format()

	#--------------------------------------------------------
	def test_get_doses():
		for d in get_substance_doses():
			#print d
			print d.format()

	#--------------------------------------------------------
	def test_get_components():
		for c in get_drug_components():
			#print c
			print '--------------------------------------'
			print c.format()
			print c.substance_dose.format()
			print c.substance.format()

	#--------------------------------------------------------
	def test_get_drugs():
		for d in get_branded_drugs():
			if d['is_fake_brand'] or d.is_vaccine:
				continue
			print '--------------------------------------'
			print d.format()
			for c in d.components:
				print '-------'
				print c.format()
				print c.substance_dose.format()
				print c.substance.format()

	#--------------------------------------------------------
	def test_get_intakes():
		for i in get_substance_intakes():
			#print i
			print u'\n'.join(i.format_maximum_information())

	#--------------------------------------------------------
	def test_get_habit_drugs():
		print get_tobacco().format()
		print get_alcohol().format()
		print get_other_drug(name = u'LSD').format()

	#--------------------------------------------------------
	def test_drug2renal_insufficiency_url():
		drug2renal_insufficiency_url(search_term = 'Metoprolol')
	#--------------------------------------------------------
	def test_medically_formatted_start_end():
		cmd = u"SELECT pk_substance_intake FROM clin.v_substance_intakes"
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd}])
		for row in rows:
			entry = cSubstanceIntakeEntry(row['pk_substance_intake'])
			print u'==============================================================='
			print entry.format(left_margin = 1, single_line = False, show_all_brand_components = True)
			print u'--------------------------------'
			print entry.medically_formatted_start_end
			gmTools.prompted_input()

	#--------------------------------------------------------
	def test_generate_amts_data_template_definition_file(work_dir=None, strict=True):
		print 'file:', generate_amts_data_template_definition_file(strict = True)

	#--------------------------------------------------------
	def test_format_substance_intake_as_amts_data():
		#print format_substance_intake_as_amts_data(cSubstanceIntakeEntry(1))
		print cSubstanceIntakeEntry(1).as_amts_data

	#--------------------------------------------------------
	# generic
	#test_drug2renal_insufficiency_url()
	#test_interaction_check()
	#test_medically_formatted_start_end()

	#test_get_substances()
	#test_get_doses()
	#test_get_components()
	#test_get_drugs()
	#test_create_substance_intake()
	#test_get_intakes()
	test_get_habit_drugs()

	# AMTS
	#test_generate_amts_data_template_definition_file()
	#test_format_substance_intake_as_amts_data()
