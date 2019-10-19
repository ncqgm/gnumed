# -*- coding: utf-8 -*-
"""Medication handling code.

license: GPL v2 or later


intake regimen:

	beim Aufstehen / Frühstück / Mittag / abends / zum Schlafengehen / "19 Uhr" / "Mittwochs" / "1x/Monat" / "Mo Di Mi Do Fr Sa So" (Falithrom) / bei Bedarf
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

#============================================================
DEFAULT_MEDICATION_HISTORY_EPISODE = _('Medication history')

URL_renal_insufficiency = 'http://www.dosing.de'
URL_renal_insufficiency_search_template = 'http://www.google.com/search?hl=de&source=hp&q=site%%3Adosing.de+%s&btnG=Google-Suche'

URL_long_qt = 'https://www.crediblemeds.org'

# http://www.akdae.de/Arzneimittelsicherheit/UAW-Meldung/UAW-Meldung-online.html
# https://dcgma.org/uaw/meldung.php
URL_drug_adr_german_default = 'https://nebenwirkungen.pei.de'

#============================================================
def _on_substance_intake_modified():
	"""Always relates to the active patient."""
	gmHooks.run_hook_script(hook = 'after_substance_intake_modified')

gmDispatcher.connect(_on_substance_intake_modified, 'clin.substance_intake_mod_db')

#============================================================
def drug2renal_insufficiency_url(search_term=None):

	if search_term is None:
		return URL_renal_insufficiency

	if isinstance(search_term, str):
		if search_term.strip() == '':
			return URL_renal_insufficiency

	terms = []
	names = []

	if isinstance(search_term, cDrugProduct):
		if search_term['atc'] is not None:
			terms.append(search_term['atc'])

	elif isinstance(search_term, cSubstanceIntakeEntry):
		names.append(search_term['substance'])
		if search_term['atc_drug'] is not None:
			terms.append(search_term['atc_drug'])
		if search_term['atc_substance'] is not None:
			terms.append(search_term['atc_substance'])

	elif isinstance(search_term, cDrugComponent):
		names.append(search_term['substance'])
		if search_term['atc_drug'] is not None:
			terms.append(search_term['atc_drug'])
		if search_term['atc_substance'] is not None:
			terms.append(search_term['atc_substance'])

	elif isinstance(search_term, cSubstance):
		names.append(search_term['substance'])
		if search_term['atc'] is not None:
			terms.append(search_term['atc'])

	elif isinstance(search_term, cSubstanceDose):
		names.append(search_term['substance'])
		if search_term['atc'] is not None:
			terms.append(search_term['atc_substance'])

	elif search_term is not None:
		names.append('%s' % search_term)
		terms.extend(gmATC.text2atc(text = '%s' % search_term, fuzzy = True))

	for name in names:
		if name.endswith('e'):
			terms.append(name[:-1])
		else:
			terms.append(name)

	#url_template = 'http://www.google.de/#q=site%%3Adosing.de+%s'
	#url = url_template % '+OR+'.join(terms)
	url = URL_renal_insufficiency_search_template % '+OR+'.join(terms)

	_log.debug('renal insufficiency URL: %s', url)

	return url

#============================================================
#============================================================
# plain substances
#------------------------------------------------------------
_SQL_get_substance = "SELECT * FROM ref.v_substances WHERE %s"

class cSubstance(gmBusinessDBObject.cBusinessDBObject):

	_cmd_fetch_payload = _SQL_get_substance % "pk_substance = %s"
	_cmds_store_payload = [
		"""UPDATE ref.substance SET
				description = %(substance)s,
				atc = gm.nullify_empty_string(%(atc)s),
				intake_instructions = gm.nullify_empty_string(%(intake_instructions)s)
			WHERE
				pk = %(pk_substance)s
					AND
				xmin = %(xmin_substance)s
			RETURNING
				xmin AS xmin_substance
		"""
	]
	_updatable_fields = [
		'substance',
		'atc',
		'intake_instructions'
	]
	#--------------------------------------------------------
	def format(self, left_margin=0):
		if len(self._payload[self._idx['loincs']]) == 0:
			loincs = ''
		else:
			loincs = """
%s %s
%s  %s""" 	% (
				(' ' * left_margin),
				_('LOINCs to monitor:'),
				(' ' * left_margin),
				('\n' + (' ' * (left_margin + 1))).join ([
					'%s%s%s' % (
						l['loinc'],
						gmTools.coalesce(l['max_age_str'], '', ': ' + _('once within %s')),
						gmTools.coalesce(l['comment'], '', ' (%s)')
					) for l in self._payload[self._idx['loincs']] 
				])
			)
		return (' ' * left_margin) + '%s: %s%s%s%s' % (
			_('Substance'),
			self._payload[self._idx['substance']],
			gmTools.coalesce(self._payload[self._idx['atc']], '', ' [%s]'),
			gmTools.coalesce(self._payload[self._idx['intake_instructions']], '', _('\n Instructions: %s')),
			loincs
		)

	#--------------------------------------------------------
	def save_payload(self, conn=None):
		success, data = super(self.__class__, self).save_payload(conn = conn)

		if not success:
			return (success, data)

		if self._payload[self._idx['atc']] is not None:
			atc = self._payload[self._idx['atc']].strip()
			if atc != '':
				gmATC.propagate_atc (
					substance = self._payload[self._idx['substance']].strip(),
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
	def _set_loincs(self, loincs):
		args = {'pk_subst': self.pk_obj, 'loincs': tuple(loincs)}
		# insert new entries
		for loinc in loincs:
			cmd = """INSERT INTO ref.lnk_loinc2substance (fk_substance, loinc)
			SELECT
				%(pk_subst)s, %(loinc)s
			WHERE NOT EXISTS (
				SELECT 1 from ref.lnk_loinc2substance WHERE fk_substance = %(pk_subst)s AND loinc = %(loinc)s
			)"""
			args['loinc'] = loinc
			gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])

		# delete old entries
		cmd = """DELETE FROM ref.lnk_loinc2substance WHERE fk_substance = %(pk_subst)s AND loinc NOT IN %(loincs)s"""
		gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])

	loincs = property(lambda x:x, _set_loincs)

	#--------------------------------------------------------
	def _get_is_in_use_by_patients(self):
		cmd = """
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
		cmd = """
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
def get_substances(order_by=None, return_pks=False):
	if order_by is None:
		order_by = 'true'
	else:
		order_by = 'true ORDER BY %s' % order_by
	cmd = _SQL_get_substance % order_by
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd}], get_col_idx = True)
	if return_pks:
		return [ r['pk_substance'] for r in rows ]
	return [ cSubstance(row = {'data': r, 'idx': idx, 'pk_field': 'pk_substance'}) for r in rows ]

#------------------------------------------------------------
def create_substance(substance=None, atc=None):
	if atc is not None:
		atc = atc.strip()

	args = {
		'desc': substance.strip(),
		'atc': atc
	}
	cmd = "SELECT pk FROM ref.substance WHERE lower(description) = lower(%(desc)s)"
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}])

	if len(rows) == 0:
		cmd = """
			INSERT INTO ref.substance (description, atc) VALUES (
				%(desc)s,
				coalesce (
					gm.nullify_empty_string(%(atc)s),
					(SELECT code FROM ref.atc WHERE term = %(desc)s LIMIT 1)
				)
			) RETURNING pk"""
		rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}], return_data = True, get_col_idx = False)

	if atc is not None:
		gmATC.propagate_atc(substance = substance.strip(), atc = atc)

	return cSubstance(aPK_obj = rows[0]['pk'])

#------------------------------------------------------------
def create_substance_by_atc(substance=None, atc=None, link_obj=None):

	if atc is None:
		raise ValueError('<atc> must be supplied')
	atc = atc.strip()
	if atc == '':
		raise ValueError('<atc> cannot be empty: [%s]', atc)

	queries = []
	args = {
		'desc': substance.strip(),
		'atc': atc
	}
	# in case the substance already exists: add ATC
	cmd = "UPDATE ref.substance SET atc = %(atc)s WHERE lower(description) = lower(%(desc)s) AND atc IS NULL"
	queries.append({'cmd': cmd, 'args': args})
	# or else INSERT the substance
	cmd = """
		INSERT INTO ref.substance (description, atc)
			SELECT
				%(desc)s,
				%(atc)s
			WHERE NOT EXISTS (
				SELECT 1 FROM ref.substance WHERE atc = %(atc)s
			)
		RETURNING pk"""
	queries.append({'cmd': cmd, 'args': args})
	rows, idx = gmPG2.run_rw_queries(link_obj = link_obj, queries = queries, return_data = True, get_col_idx = False)
	if len(rows) == 0:
		cmd = "SELECT pk FROM ref.substance WHERE atc = %(atc)s LIMIT 1"
		rows, idx = gmPG2.run_ro_queries(link_obj = link_obj, queries = [{'cmd': cmd, 'args': args}])

	return cSubstance(aPK_obj = rows[0]['pk'], link_obj = link_obj)

#------------------------------------------------------------
def delete_substance(pk_substance=None):
	args = {'pk': pk_substance}
	cmd = """
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

#============================================================
# substance doses
#------------------------------------------------------------
_SQL_get_substance_dose = "SELECT * FROM ref.v_substance_doses WHERE %s"

class cSubstanceDose(gmBusinessDBObject.cBusinessDBObject):

	_cmd_fetch_payload = _SQL_get_substance_dose % "pk_dose = %s"
	_cmds_store_payload = [
		"""UPDATE ref.dose SET
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
		'amount',
		'unit',
		'dose_unit'
	]

	#--------------------------------------------------------
	def format(self, left_margin=0, include_loincs=False):
		loincs = ''
		if include_loincs and (len(self._payload[self._idx['loincs']]) > 0):
			loincs = """
%s %s
%s  %s""" 	% (
				(' ' * left_margin),
				_('LOINCs to monitor:'),
				(' ' * left_margin),
				('\n' + (' ' * (left_margin + 1))).join ([
					'%s%s%s' % (
						l['loinc'],
						gmTools.coalesce(l['max_age_str'], '', ': ' + _('once within %s')),
						gmTools.coalesce(l['comment'], '', ' (%s)')
					) for l in self._payload[self._idx['loincs']] 
				])
			)
		return (' ' * left_margin) + '%s: %s %s%s%s%s%s' % (
			_('Substance dose'),
			self._payload[self._idx['substance']],
			self._payload[self._idx['amount']],
			self.formatted_units,
			gmTools.coalesce(self._payload[self._idx['atc_substance']], '', ' [%s]'),
			gmTools.coalesce(self._payload[self._idx['intake_instructions']], '', '\n' + (' ' * left_margin) + ' ' + _('Instructions: %s')),
			loincs
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
		cmd = """
			SELECT EXISTS (
				SELECT 1
				FROM clin.v_substance_intakes
				WHERE pk_dose = %(pk)s
				LIMIT 1
			)"""
		args = {'pk': self.pk_obj}

		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = False)
		return rows[0][0]

	is_in_use_by_patients = property(_get_is_in_use_by_patients, lambda x:x)

	#--------------------------------------------------------
	def _get_is_drug_component(self):
		cmd = """
			SELECT EXISTS (
				SELECT 1
				FROM ref.v_drug_components
				WHERE pk_dose = %(pk)s
				LIMIT 1
			)"""
		args = {'pk': self.pk_obj}
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = False)
		return rows[0][0]

	is_drug_component = property(_get_is_drug_component, lambda x:x)

	#--------------------------------------------------------
	def _get_formatted_units(self, short=True):
		return format_units (
			self._payload[self._idx['unit']],
			gmTools.coalesce(self._payload[self._idx['dose_unit']], _('delivery unit')),
			short = short
		)

	formatted_units = property(_get_formatted_units, lambda x:x)

#------------------------------------------------------------
def get_substance_doses(order_by=None, return_pks=False):
	if order_by is None:
		order_by = 'true'
	else:
		order_by = 'true ORDER BY %s' % order_by
	cmd = _SQL_get_substance_dose % order_by
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd}], get_col_idx = True)
	if return_pks:
		return [ r['pk_dose'] for r in rows ]
	return [ cSubstanceDose(row = {'data': r, 'idx': idx, 'pk_field': 'pk_dose'}) for r in rows ]

#------------------------------------------------------------
def create_substance_dose(link_obj=None, pk_substance=None, substance=None, atc=None, amount=None, unit=None, dose_unit=None):

	if [pk_substance, substance].count(None) != 1:
		raise ValueError('exctly one of <pk_substance> and <substance> must be None')

	converted, amount = gmTools.input2decimal(amount)
	if not converted:
		raise ValueError('<amount> must be a number: %s (is: %s)', amount, type(amount))

	if pk_substance is None:
		pk_substance = create_substance(link_obj = link_obj, substance = substance, atc = atc)['pk_substance']

	args = {
		'pk_subst': pk_substance,
		'amount': amount,
		'unit': unit.strip(),
		'dose_unit': dose_unit
	}
	cmd = """
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
	rows, idx = gmPG2.run_ro_queries(link_obj = link_obj, queries = [{'cmd': cmd, 'args': args}])

	if len(rows) == 0:
		cmd = """
			INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit) VALUES (
				%(pk_subst)s,
				%(amount)s,
				gm.nullify_empty_string(%(unit)s),
				gm.nullify_empty_string(%(dose_unit)s)
			) RETURNING pk"""
		rows, idx = gmPG2.run_rw_queries(link_obj = link_obj, queries = [{'cmd': cmd, 'args': args}], return_data = True, get_col_idx = False)

	return cSubstanceDose(aPK_obj = rows[0]['pk'], link_obj = link_obj)

#------------------------------------------------------------
def create_substance_dose_by_atc(link_obj=None, substance=None, atc=None, amount=None, unit=None, dose_unit=None):
	subst = create_substance_by_atc (
		link_obj = link_obj,
		substance = substance,
		atc = atc
	)
	return create_substance_dose (
		link_obj = link_obj,
		pk_substance = subst['pk_substance'],
		amount = amount,
		unit = unit,
		dose_unit = dose_unit
	)

#------------------------------------------------------------
def delete_substance_dose(pk_dose=None):
	args = {'pk_dose': pk_dose}
	cmd = """
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

#------------------------------------------------------------
class cSubstanceDoseMatchProvider(gmMatchProvider.cMatchProvider_SQL2):

	_pattern = regex.compile(r'^\D+\s*\d+$', regex.UNICODE)

	# the "normal query" is run when the search fragment
	# does NOT match the regex ._pattern (which is: "chars SPACE digits")
	_normal_query = """
		SELECT
			r_vsd.pk_dose
				AS data,
			(r_vsd.substance || ' ' || r_vsd.amount || ' ' || r_vsd.unit || coalesce(' / ' r_vsd.dose_unit ||, ''))
				AS field_label,
			(r_vsd.substance || ' ' || r_vsd.amount || ' ' || r_vsd.unit || coalesce(' / ' r_vsd.dose_unit ||, ''))
				AS list_label
		FROM
			ref.v_substance_doses r_vsd
		WHERE
			r_vsd.substance %%(fragment_condition)s
		ORDER BY
			list_label
		LIMIT 50"""

	# the "regex query" is run when the search fragment
	# DOES match the regex ._pattern (which is: "chars SPACE digits")
	_regex_query = 	"""
		SELECT
			r_vsd.pk_dose
				AS data,
			(r_vsd.substance || ' ' || r_vsd.amount || ' ' || r_vsd.unit || coalesce(' / ' r_vsd.dose_unit ||, ''))
				AS field_label,
			(r_vsd.substance || ' ' || r_vsd.amount || ' ' || r_vsd.unit || coalesce(' / ' r_vsd.dose_unit ||, ''))
				AS list_label
		FROM
			ref.v_substance_doses r_vsd
		WHERE
			%%(fragment_condition)s
		ORDER BY
			list_label
		LIMIT 50"""

	#--------------------------------------------------------
	def getMatchesByPhrase(self, aFragment):
		"""Return matches for aFragment at start of phrases."""

		if cSubstanceMatchProvider._pattern.match(aFragment):
			self._queries = [cSubstanceMatchProvider._regex_query]
			fragment_condition = """substance ILIKE %(subst)s
				AND
			amount::text ILIKE %(amount)s"""
			self._args['subst'] = '%s%%' % regex.sub(r'\s*\d+$', '', aFragment)
			self._args['amount'] = '%s%%' % regex.sub(r'^\D+\s*', '', aFragment)
		else:
			self._queries = [cSubstanceMatchProvider._normal_query]
			fragment_condition = "ILIKE %(fragment)s"
			self._args['fragment'] = "%s%%" % aFragment

		return self._find_matches(fragment_condition)

	#--------------------------------------------------------
	def getMatchesByWord(self, aFragment):
		"""Return matches for aFragment at start of words inside phrases."""

		if cSubstanceMatchProvider._pattern.match(aFragment):
			self._queries = [cSubstanceMatchProvider._regex_query]

			subst = regex.sub(r'\s*\d+$', '', aFragment)
			subst = gmPG2.sanitize_pg_regex(expression = subst, escape_all = False)

			fragment_condition = """substance ~* %(subst)s
				AND
			amount::text ILIKE %(amount)s"""

			self._args['subst'] = "( %s)|(^%s)" % (subst, subst)
			self._args['amount'] = '%s%%' % regex.sub(r'^\D+\s*', '', aFragment)
		else:
			self._queries = [cSubstanceMatchProvider._normal_query]
			fragment_condition = "~* %(fragment)s"
			aFragment = gmPG2.sanitize_pg_regex(expression = aFragment, escape_all = False)
			self._args['fragment'] = "( %s)|(^%s)" % (aFragment, aFragment)

		return self._find_matches(fragment_condition)

	#--------------------------------------------------------
	def getMatchesBySubstr(self, aFragment):
		"""Return matches for aFragment as a true substring."""

		if cSubstanceMatchProvider._pattern.match(aFragment):
			self._queries = [cSubstanceMatchProvider._regex_query]
			fragment_condition = """substance ILIKE %(subst)s
				AND
			amount::text ILIKE %(amount)s"""
			self._args['subst'] = '%%%s%%' % regex.sub(r'\s*\d+$', '', aFragment)
			self._args['amount'] = '%s%%' % regex.sub(r'^\D+\s*', '', aFragment)
		else:
			self._queries = [cSubstanceMatchProvider._normal_query]
			fragment_condition = "ILIKE %(fragment)s"
			self._args['fragment'] = "%%%s%%" % aFragment

		return self._find_matches(fragment_condition)

#------------------------------------------------------------
#------------------------------------------------------------
class cProductOrSubstanceMatchProvider(gmMatchProvider.cMatchProvider_SQL2):

	# by product name
	_query_drug_product_by_name = """
		SELECT
			ARRAY[1, pk]::INTEGER[]
				AS data,
			(description || ' (' || preparation || ')' || coalesce(' [' || atc_code || ']', ''))
				AS list_label,
			(description || ' (' || preparation || ')' || coalesce(' [' || atc_code || ']', ''))
				AS field_label,
			1 AS rank
		FROM ref.drug_product
		WHERE description %(fragment_condition)s
		LIMIT 50
	"""
	_query_drug_product_by_name_and_strength = """
		SELECT
			ARRAY[1, pk_drug_product]::INTEGER[]
				AS data,
			(product || ' (' || preparation || ' %s ' || amount || unit || coalesce('/' || dose_unit, '') || ' ' || substance || ')' || coalesce(' [' || atc_drug || ']', ''))
				AS list_label,
			(product || ' (' || preparation || ' %s ' || amount || unit || coalesce('/' || dose_unit, '') || ' ' || substance || ')' || coalesce(' [' || atc_drug || ']', ''))
				AS field_label,
			1 AS rank
		FROM
			(SELECT *, product AS description FROM ref.v_drug_components) AS _components
		WHERE %%(fragment_condition)s
		LIMIT 50
	""" % (
		_('w/'),
		_('w/')
	)

	# by component
#	_query_component_by_name = u"""
#		SELECT
#			ARRAY[3, r_vdc1.pk_component]::INTEGER[]
#				AS data,
#			(r_vdc1.substance || ' ' || r_vdc1.amount || r_vdc1.unit || ' ' || r_vdc1.preparation || ' ('
#				|| r_vdc1.product || ' ['
#					|| (
#						SELECT array_to_string(array_agg(r_vdc2.amount), ' / ')
#						FROM ref.v_drug_components r_vdc2
#						WHERE r_vdc2.pk_drug_product = r_vdc1.pk_drug_product
#					)
#				|| ']'
#			|| ')'
#			)	AS field_label,
#			(r_vdc1.substance || ' ' || r_vdc1.amount || r_vdc1.unit || ' ' || r_vdc1.preparation || ' ('
#				|| r_vdc1.product || ' ['
#					|| (
#						SELECT array_to_string(array_agg(r_vdc2.amount), ' / ')
#						FROM ref.v_drug_components r_vdc2
#						WHERE r_vdc2.pk_drug_product = r_vdc1.pk_drug_product
#					)
#				|| ']'
#			|| ')'
#			)	AS list_label,
#			1 AS rank
#		FROM
#			(SELECT *, product AS description FROM ref.v_drug_components) AS r_vdc1
#		WHERE
#			r_vdc1.substance %(fragment_condition)s
#		LIMIT 50"""

#	_query_component_by_name_and_strength = u"""
#		SELECT
#			ARRAY[3, r_vdc1.pk_component]::INTEGER[]
#				AS data,
#			(r_vdc1.substance || ' ' || r_vdc1.amount || r_vdc1.unit || ' ' || r_vdc1.preparation || ' ('
#				|| r_vdc1.product || ' ['
#					|| (
#						SELECT array_to_string(array_agg(r_vdc2.amount), ' / ')
#						FROM ref.v_drug_components r_vdc2
#						WHERE r_vdc2.pk_drug_product = r_vdc1.pk_drug_product
#					)
#				|| ']'
#			|| ')'
#			)	AS field_label,
#			(r_vdc1.substance || ' ' || r_vdc1.amount || r_vdc1.unit || ' ' || r_vdc1.preparation || ' ('
#				|| r_vdc1.product || ' ['
#					|| (
#						SELECT array_to_string(array_agg(r_vdc2.amount), ' / ')
#						FROM ref.v_drug_components r_vdc2
#						WHERE r_vdc2.pk_drug_product = r_vdc1.pk_drug_product
#					)
#				|| ']'
#			|| ')'
#			)	AS list_label,
#			1 AS rank
#		FROM (SELECT *, substance AS description FROM ref.v_drug_components) AS r_vdc1
#		WHERE
#			%(fragment_condition)s
#		ORDER BY list_label
#		LIMIT 50"""

	# by substance name in doses
	_query_substance_by_name = """
		SELECT
			data,
			field_label,
			list_label,
			rank
		FROM ((
			-- first: substance intakes which match, because we tend to reuse them often
			SELECT
				ARRAY[2, pk_substance]::INTEGER[] AS data,
				(description || ' ' || amount || unit || coalesce('/' || dose_unit, '')) AS field_label,
				(description || ' ' || amount || unit || coalesce('/' || dose_unit, '') || ' (%s)') AS list_label,
				1 AS rank
			FROM (
				SELECT DISTINCT ON (description, amount, unit, dose_unit)
					pk_substance,
					substance AS description,
					amount,
					unit,
					dose_unit
				FROM clin.v_substance_intakes
			) AS normalized_intakes
			WHERE description %%(fragment_condition)s

		) UNION ALL (
xxxxxxxxxxxxxxxxxxxxxxxxxxxx
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

	_query_substance_by_name_and_strength = 	"""
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
				FROM clin.v_nonbraXXXnd_intakes
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

	_pattern = regex.compile(r'^\D+\s*\d+$', regex.UNICODE)

	_master_query = """
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

		if cProductOrSubstanceMatchProvider._pattern.match(aFragment):
			self._queries = [
				cProductOrSubstanceMatchProvider._master_query % (
					cProductOrSubstanceMatchProvider._query_drug_product_by_name_and_strength,
					cProductOrSubstanceMatchProvider._query_substance_by_name_and_strength,
					cProductOrSubstanceMatchProvider._query_component_by_name_and_strength
				)
			]
			#self._queries = [cProductOrSubstanceMatchProvider._query_substance_by_name_and_strength]
			fragment_condition = """description ILIKE %(desc)s
				AND
			amount::text ILIKE %(amount)s"""
			self._args['desc'] = '%s%%' % regex.sub(r'\s*\d+$', '', aFragment)
			self._args['amount'] = '%s%%' % regex.sub(r'^\D+\s*', '', aFragment)
		else:
			self._queries = [
				cProductOrSubstanceMatchProvider._master_query % (
					cProductOrSubstanceMatchProvider._query_drug_product_by_name,
					cProductOrSubstanceMatchProvider._query_substance_by_name,
					cProductOrSubstanceMatchProvider._query_component_by_name
				)
			]
			#self._queries = [cProductOrSubstanceMatchProvider._query_substance_by_name]
			fragment_condition = "ILIKE %(fragment)s"
			self._args['fragment'] = "%s%%" % aFragment

		return self._find_matches(fragment_condition)

	#--------------------------------------------------------
	def getMatchesByWord(self, aFragment):
		"""Return matches for aFragment at start of words inside phrases."""

		if cProductOrSubstanceMatchProvider._pattern.match(aFragment):
			self._queries = [
				cProductOrSubstanceMatchProvider._master_query % (
					cProductOrSubstanceMatchProvider._query_drug_product_by_name_and_strength,
					cProductOrSubstanceMatchProvider._query_substance_by_name_and_strength,
					cProductOrSubstanceMatchProvider._query_component_by_name_and_strength
				)
			]
			#self._queries = [cProductOrSubstanceMatchProvider._query_substance_by_name_and_strength]

			desc = regex.sub(r'\s*\d+$', '', aFragment)
			desc = gmPG2.sanitize_pg_regex(expression = desc, escape_all = False)

			fragment_condition = """description ~* %(desc)s
				AND
			amount::text ILIKE %(amount)s"""

			self._args['desc'] = "( %s)|(^%s)" % (desc, desc)
			self._args['amount'] = '%s%%' % regex.sub(r'^\D+\s*', '', aFragment)
		else:
			self._queries = [
				cProductOrSubstanceMatchProvider._master_query % (
					cProductOrSubstanceMatchProvider._query_drug_product_by_name,
					cProductOrSubstanceMatchProvider._query_substance_by_name,
					cProductOrSubstanceMatchProvider._query_component_by_name
				)
			]
			#self._queries = [cProductOrSubstanceMatchProvider._query_substance_by_name]
			fragment_condition = "~* %(fragment)s"
			aFragment = gmPG2.sanitize_pg_regex(expression = aFragment, escape_all = False)
			self._args['fragment'] = "( %s)|(^%s)" % (aFragment, aFragment)

		return self._find_matches(fragment_condition)

	#--------------------------------------------------------
	def getMatchesBySubstr(self, aFragment):
		"""Return matches for aFragment as a true substring."""

		if cProductOrSubstanceMatchProvider._pattern.match(aFragment):
			self._queries = [
				cProductOrSubstanceMatchProvider._master_query % (
					cProductOrSubstanceMatchProvider._query_drug_product_by_name_and_strength,
					cProductOrSubstanceMatchProvider._query_substance_by_name_and_strength,
					cProductOrSubstanceMatchProvider._query_component_by_name_and_strength
				)
			]
			#self._queries = [cProductOrSubstanceMatchProvider._query_substance_by_name_and_strength]
			fragment_condition = """description ILIKE %(desc)s
				AND
			amount::text ILIKE %(amount)s"""
			self._args['desc'] = '%%%s%%' % regex.sub(r'\s*\d+$', '', aFragment)
			self._args['amount'] = '%s%%' % regex.sub(r'^\D+\s*', '', aFragment)
		else:
			self._queries = [
				cProductOrSubstanceMatchProvider._master_query % (
					cProductOrSubstanceMatchProvider._query_drug_product_by_name,
					cProductOrSubstanceMatchProvider._query_substance_by_name,
					cProductOrSubstanceMatchProvider._query_component_by_name
				)
			]
			#self._queries = [cProductOrSubstanceMatchProvider._query_substance_by_name]
			fragment_condition = "ILIKE %(fragment)s"
			self._args['fragment'] = "%%%s%%" % aFragment

		return self._find_matches(fragment_condition)

#------------------------------------------------------------
class cSubstanceIntakeObjectMatchProvider(gmMatchProvider.cMatchProvider_SQL2):

	# (product name) -> product
	_SQL_drug_product_by_name = """
		SELECT
			pk_drug_product
				AS data,
			(product || ' (' || preparation || ')' || coalesce(' [' || atc || ']', ''))
				AS list_label,
			(product || ' (' || preparation || ')' || coalesce(' [' || atc || ']', ''))
				AS field_label
		FROM ref.v_drug_products
		WHERE
			is_vaccine IS FALSE
				AND
			product %(fragment_condition)s
		LIMIT 50
	"""
	# (component name) -> product
	_SQL_drug_product_by_component_name = """
		SELECT
			pk_drug_product
				AS data,
			(product || ' (' || preparation || ' %s ' || amount || unit || coalesce('/' || dose_unit, '') || ' ' || substance || ')' || coalesce(' [' || atc_drug || ']', ''))
				AS list_label,
			(product || ' (' || preparation || ' %s ' || amount || unit || coalesce('/' || dose_unit, '') || ' ' || substance || ')' || coalesce(' [' || atc_drug || ']', ''))
				AS field_label
		FROM
			ref.v_drug_components
		WHERE substance %%(fragment_condition)s
		LIMIT 50
	""" % (
		_('w/'),
		_('w/')
	)
	# (product name + component strength) -> product
	_SQL_drug_product_by_name_and_strength = """
		SELECT
			pk_drug_product
				AS data,
			(product || ' (' || preparation || ' %s ' || amount || unit || coalesce('/' || dose_unit, '') || ' ' || substance || ')' || coalesce(' [' || atc_drug || ']', ''))
				AS list_label,
			(product || ' (' || preparation || ' %s ' || amount || unit || coalesce('/' || dose_unit, '') || ' ' || substance || ')' || coalesce(' [' || atc_drug || ']', ''))
				AS field_label
		FROM
			(SELECT *, product AS description FROM ref.v_drug_components) AS _components
		WHERE %%(fragment_condition)s
		LIMIT 50
	""" % (
		_('w/'),
		_('w/')
	)
	# (component name + component strength) -> product
	_SQL_drug_product_by_component_name_and_strength = """
		SELECT
			pk_drug_product
				AS data,
			(product || ' (' || preparation || ' %s ' || amount || unit || coalesce('/' || dose_unit, '') || ' ' || substance || ')' || coalesce(' [' || atc_drug || ']', ''))
				AS list_label,
			(product || ' (' || preparation || ' %s ' || amount || unit || coalesce('/' || dose_unit, '') || ' ' || substance || ')' || coalesce(' [' || atc_drug || ']', ''))
				AS field_label
		FROM
			(SELECT *, substance AS description FROM ref.v_drug_components) AS _components
		WHERE %%(fragment_condition)s
		LIMIT 50
	""" % (
		_('w/'),
		_('w/')
	)
	# non-drug substance name
	_SQL_substance_name = """
		SELECT DISTINCT ON (field_label)
			data, list_label, field_label
		FROM (
			SELECT DISTINCT ON (term)
				NULL::integer
					AS data,
				term || ' (ATC: ' || code || ')'
					AS list_label,
				term
					AS field_label
			FROM
				ref.atc
			WHERE
				lower(term) %(fragment_condition)s

			UNION ALL

			SELECT DISTINCT ON (description)
				NULL::integer
					AS data,
				description || coalesce(' (ATC: ' || atc || ')', '')
					AS list_label,
				description
					AS field_label
			FROM
				ref.substance
			WHERE
				lower(description) %(fragment_condition)s
		) AS nondrug_substances
		WHERE NOT EXISTS (
			SELECT 1 FROM ref.v_drug_components WHERE lower(substance) = lower(nondrug_substances.field_label)
		)
		LIMIT 30
	"""

	# this query UNIONs together individual queries
	_SQL_regex_master_query = """
		SELECT
			data, field_label, list_label
		FROM ((%s) UNION (%s))
			AS _union
		ORDER BY list_label
		LIMIT 50
	""" % (
		_SQL_drug_product_by_name_and_strength,
		_SQL_drug_product_by_component_name_and_strength
	)
	_SQL_nonregex_master_query = """
		SELECT
			data, field_label, list_label
		FROM ((%s) UNION (%s) UNION (%s))
			AS _union
		ORDER BY list_label
		LIMIT 50
	""" % (
		_SQL_drug_product_by_name,
		_SQL_drug_product_by_component_name,
		_SQL_substance_name
	)

	_REGEX_name_and_strength = regex.compile(r'^\D+\s*\d+$', regex.UNICODE)

	#--------------------------------------------------------
	def getMatchesByPhrase(self, aFragment):
		"""Return matches for aFragment at start of phrases."""

		if cSubstanceIntakeObjectMatchProvider._REGEX_name_and_strength.match(aFragment):
			self._queries = [cSubstanceIntakeObjectMatchProvider._SQL_regex_master_query]
			fragment_condition = """description ILIKE %(desc)s
				AND
			amount::text ILIKE %(amount)s"""
			self._args['desc'] = '%s%%' % regex.sub(r'\s*\d+$', '', aFragment)
			self._args['amount'] = '%s%%' % regex.sub(r'^\D+\s*', '', aFragment)
		else:
			self._queries = [ cSubstanceIntakeObjectMatchProvider._SQL_nonregex_master_query ]
			fragment_condition = "ILIKE %(fragment)s"
			self._args['fragment'] = "%s%%" % aFragment

		return self._find_matches(fragment_condition)

	#--------------------------------------------------------
	def getMatchesByWord(self, aFragment):
		"""Return matches for aFragment at start of words inside phrases."""

		if cSubstanceIntakeObjectMatchProvider._REGEX_name_and_strength.match(aFragment):
			self._queries = [cSubstanceIntakeObjectMatchProvider._SQL_regex_master_query]

			desc = regex.sub(r'\s*\d+$', '', aFragment)
			desc = gmPG2.sanitize_pg_regex(expression = desc, escape_all = False)

			fragment_condition = """description ~* %(desc)s
				AND
			amount::text ILIKE %(amount)s"""

			self._args['desc'] = "( %s)|(^%s)" % (desc, desc)
			self._args['amount'] = '%s%%' % regex.sub(r'^\D+\s*', '', aFragment)
		else:
			self._queries = [ cSubstanceIntakeObjectMatchProvider._SQL_nonregex_master_query ]
			fragment_condition = "~* %(fragment)s"
			aFragment = gmPG2.sanitize_pg_regex(expression = aFragment, escape_all = False)
			self._args['fragment'] = "( %s)|(^%s)" % (aFragment, aFragment)

		return self._find_matches(fragment_condition)

	#--------------------------------------------------------
	def getMatchesBySubstr(self, aFragment):
		"""Return matches for aFragment as a true substring."""

		if cSubstanceIntakeObjectMatchProvider._REGEX_name_and_strength.match(aFragment):
			self._queries = [cSubstanceIntakeObjectMatchProvider._SQL_regex_master_query]
			fragment_condition = """description ILIKE %(desc)s
				AND
			amount::text ILIKE %(amount)s"""
			self._args['desc'] = '%%%s%%' % regex.sub(r'\s*\d+$', '', aFragment)
			self._args['amount'] = '%s%%' % regex.sub(r'^\D+\s*', '', aFragment)
		else:
			self._queries = [ cSubstanceIntakeObjectMatchProvider._SQL_nonregex_master_query ]
			fragment_condition = "ILIKE %(fragment)s"
			self._args['fragment'] = "%%%s%%" % aFragment

		return self._find_matches(fragment_condition)

#============================================================
# drug components
#------------------------------------------------------------
_SQL_get_drug_components = 'SELECT * FROM ref.v_drug_components WHERE %s'

class cDrugComponent(gmBusinessDBObject.cBusinessDBObject):

	_cmd_fetch_payload = _SQL_get_drug_components % 'pk_component = %s'
	_cmds_store_payload = [
		"""UPDATE ref.lnk_dose2drug SET
				fk_drug_product = %(pk_drug_product)s,
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
		'pk_drug_product',
		'pk_dose'
	]
	#--------------------------------------------------------
	def format(self, left_margin=0, include_loincs=False):
		lines = []
		lines.append('%s %s%s' % (
			self._payload[self._idx['substance']],
			self._payload[self._idx['amount']],
			self.formatted_units
		))
		lines.append(_('Component of %s (%s)') % (
			self._payload[self._idx['product']],
			self._payload[self._idx['l10n_preparation']]
		))
		if self._payload[self._idx['is_fake_product']]:
			lines.append(' ' + _('(not a real drug product)'))

		if self._payload[self._idx['intake_instructions']] is not None:
			lines.append(_('Instructions: %s') % self._payload[self._idx['intake_instructions']])
		if self._payload[self._idx['atc_substance']] is not None:
			lines.append(_('ATC (substance): %s') % self._payload[self._idx['atc_substance']])
		if self._payload[self._idx['atc_drug']] is not None:
			lines.append(_('ATC (drug): %s') % self._payload[self._idx['atc_drug']])
		if self._payload[self._idx['external_code']] is not None:
			lines.append('%s: %s' % (
				self._payload[self._idx['external_code_type']],
				self._payload[self._idx['external_code']]
			))

		if include_loincs:
			if len(self._payload[self._idx['loincs']]) > 0:
				lines.append(_('LOINCs to monitor:'))
			lines.extend ([
				' %s%s%s' % (
					loinc['loinc'],
					gmTools.coalesce(loinc['max_age_str'], '', ': ' + _('once within %s')),
					gmTools.coalesce(loinc['comment'], '', ' (%s)')
				) for loinc in self._payload[self._idx['loincs']]
			])

		return (' ' * left_margin) + ('\n' + (' ' * left_margin)).join(lines)

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
		return cDrugProduct(aPK_obj = self._payload[self._idx['pk_drug_product']])

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

	#--------------------------------------------------------
	def _get_formatted_units(self, short=True):
		return format_units (
			self._payload[self._idx['unit']],
			self._payload[self._idx['dose_unit']],
			self._payload[self._idx['l10n_preparation']]
		)

	formatted_units = property(_get_formatted_units, lambda x:x)

#------------------------------------------------------------
def get_drug_components(return_pks=False):
	cmd = _SQL_get_drug_components % 'true ORDER BY product, substance'
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd}], get_col_idx = True)
	if return_pks:
		return [ r['pk_component'] for r in rows ]
	return [ cDrugComponent(row = {'data': r, 'idx': idx, 'pk_field': 'pk_component'}) for r in rows ]

#------------------------------------------------------------
class cDrugComponentMatchProvider(gmMatchProvider.cMatchProvider_SQL2):

	_pattern = regex.compile(r'^\D+\s*\d+$', regex.UNICODE)

	_query_desc_only = """
		SELECT DISTINCT ON (list_label)
			r_vdc1.pk_component
				AS data,
			(r_vdc1.substance || ' '
				|| r_vdc1.amount || r_vdc1.unit || ' '
				|| r_vdc1.preparation || ' ('
				|| r_vdc1.product || ' ['
					|| (
						SELECT array_to_string(array_agg(r_vdc2.amount), ' / ')
						FROM ref.v_drug_components r_vdc2
						WHERE r_vdc2.pk_drug_product = r_vdc1.pk_drug_product
					)
				|| ']'
			 || ')'
			)	AS field_label,
			(r_vdc1.substance || ' '
				|| r_vdc1.amount || r_vdc1.unit || ' '
				|| r_vdc1.preparation || ' ('
				|| r_vdc1.product || ' ['
					|| (
						SELECT array_to_string(array_agg(r_vdc2.amount), ' / ')
						FROM ref.v_drug_components r_vdc2
						WHERE r_vdc2.pk_drug_product = r_vdc1.pk_drug_product
					)
				|| ']'
			 || ')'
			)	AS list_label
		FROM ref.v_drug_components r_vdc1
		WHERE
			r_vdc1.substance %(fragment_condition)s
				OR
			r_vdc1.product %(fragment_condition)s
		ORDER BY list_label
		LIMIT 50"""

	_query_desc_and_amount = """
		SELECT DISTINCT ON (list_label)
			pk_component AS data,
			(r_vdc1.substance || ' '
				|| r_vdc1.amount || r_vdc1.unit || ' '
				|| r_vdc1.preparation || ' ('
				|| r_vdc1.product || ' ['
					|| (
						SELECT array_to_string(array_agg(r_vdc2.amount), ' / ')
						FROM ref.v_drug_components r_vdc2
						WHERE r_vdc2.pk_drug_product = r_vdc1.pk_drug_product
					)
				|| ']'
			 || ')'
			)	AS field_label,
			(r_vdc1.substance || ' '
				|| r_vdc1.amount || r_vdc1.unit || ' '
				|| r_vdc1.preparation || ' ('
				|| r_vdc1.product || ' ['
					|| (
						SELECT array_to_string(array_agg(r_vdc2.amount), ' / ')
						FROM ref.v_drug_components r_vdc2
						WHERE r_vdc2.pk_drug_product = r_vdc1.pk_drug_product
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
			fragment_condition = """(substance ILIKE %(desc)s OR product ILIKE %(desc)s)
				AND
			amount::text ILIKE %(amount)s"""
			self._args['desc'] = '%s%%' % regex.sub(r'\s*\d+$', '', aFragment)
			self._args['amount'] = '%s%%' % regex.sub(r'^\D+\s*', '', aFragment)
		else:
			self._queries = [cDrugComponentMatchProvider._query_desc_only]
			fragment_condition = "ILIKE %(fragment)s"
			self._args['fragment'] = "%s%%" % aFragment

		return self._find_matches(fragment_condition)
	#--------------------------------------------------------
	def getMatchesByWord(self, aFragment):
		"""Return matches for aFragment at start of words inside phrases."""

		if cDrugComponentMatchProvider._pattern.match(aFragment):
			self._queries = [cDrugComponentMatchProvider._query_desc_and_amount]

			desc = regex.sub(r'\s*\d+$', '', aFragment)
			desc = gmPG2.sanitize_pg_regex(expression = desc, escape_all = False)

			fragment_condition = """(substance ~* %(desc)s OR product ~* %(desc)s)
				AND
			amount::text ILIKE %(amount)s"""

			self._args['desc'] = "( %s)|(^%s)" % (desc, desc)
			self._args['amount'] = '%s%%' % regex.sub(r'^\D+\s*', '', aFragment)
		else:
			self._queries = [cDrugComponentMatchProvider._query_desc_only]
			fragment_condition = "~* %(fragment)s"
			aFragment = gmPG2.sanitize_pg_regex(expression = aFragment, escape_all = False)
			self._args['fragment'] = "( %s)|(^%s)" % (aFragment, aFragment)

		return self._find_matches(fragment_condition)
	#--------------------------------------------------------
	def getMatchesBySubstr(self, aFragment):
		"""Return matches for aFragment as a true substring."""

		if cDrugComponentMatchProvider._pattern.match(aFragment):
			self._queries = [cDrugComponentMatchProvider._query_desc_and_amount]
			fragment_condition = """(substance ILIKE %(desc)s OR product ILIKE %(desc)s)
				AND
			amount::text ILIKE %(amount)s"""
			self._args['desc'] = '%%%s%%' % regex.sub(r'\s*\d+$', '', aFragment)
			self._args['amount'] = '%s%%' % regex.sub(r'^\D+\s*', '', aFragment)
		else:
			self._queries = [cDrugComponentMatchProvider._query_desc_only]
			fragment_condition = "ILIKE %(fragment)s"
			self._args['fragment'] = "%%%s%%" % aFragment

		return self._find_matches(fragment_condition)

#============================================================
# drug products
#------------------------------------------------------------
_SQL_get_drug_product = "SELECT * FROM ref.v_drug_products WHERE %s"

class cDrugProduct(gmBusinessDBObject.cBusinessDBObject):
	"""Represents a drug as marketed by a manufacturer or a generic drug product."""

	_cmd_fetch_payload = _SQL_get_drug_product % 'pk_drug_product = %s'
	_cmds_store_payload = [
		"""UPDATE ref.drug_product SET
				description = %(product)s,
				preparation = %(preparation)s,
				atc_code = gm.nullify_empty_string(%(atc)s),
				external_code = gm.nullify_empty_string(%(external_code)s),
				external_code_type = gm.nullify_empty_string(%(external_code_type)s),
				is_fake = %(is_fake_product)s,
				fk_data_source = %(pk_data_source)s
			WHERE
				pk = %(pk_drug_product)s
					AND
				xmin = %(xmin_drug_product)s
			RETURNING
				xmin AS xmin_drug_product
		"""
	]
	_updatable_fields = [
		'product',
		'preparation',
		'atc',
		'is_fake_product',
		'external_code',
		'external_code_type',
		'pk_data_source'
	]
	#--------------------------------------------------------
	def format(self, left_margin=0, include_component_details=False):
		lines = []
		lines.append('%s (%s)' % (
			self._payload[self._idx['product']],
			self._payload[self._idx['l10n_preparation']]
			)
		)
		if self._payload[self._idx['atc']] is not None:
			lines.append('ATC: %s' % self._payload[self._idx['atc']])
		if self._payload[self._idx['external_code']] is not None:
			lines.append('%s: %s' % (self._payload[self._idx['external_code_type']], self._payload[self._idx['external_code']]))
		if len(self._payload[self._idx['components']]) > 0:
			lines.append(_('Components:'))
			for comp in self._payload[self._idx['components']]:
				lines.append(' %s %s %s' % (
					comp['substance'],
					comp['amount'],
					format_units(comp['unit'], comp['dose_unit'], short = False)
				))
				if include_component_details:
					if comp['intake_instructions'] is not None:
						lines.append(comp['intake_instructions'])
					lines.extend([ '%s%s%s' % (
						l['loinc'],
						gmTools.coalesce(l['max_age_str'], '', ': ' + _('once within %s')),
						gmTools.coalesce(l['comment'], '', ' (%s)')
					) for l in comp['loincs'] ])

		if self._payload[self._idx['is_fake_product']]:
			lines.append('')
			lines.append(_('this is a fake drug product'))
		if self.is_vaccine:
			lines.append(_('this is a vaccine'))

		return (' ' * left_margin) + ('\n' + (' ' * left_margin)).join(lines)

	#--------------------------------------------------------
	def save_payload(self, conn=None):
		success, data = super(self.__class__, self).save_payload(conn = conn)

		if not success:
			return (success, data)

		if self._payload[self._idx['atc']] is not None:
			atc = self._payload[self._idx['atc']].strip()
			if atc != '':
				gmATC.propagate_atc (
					link_obj = conn,
					substance = self._payload[self._idx['product']].strip(),
					atc = atc
				)

		return (success, data)

	#--------------------------------------------------------
	def set_substance_doses_as_components(self, substance_doses=None, link_obj=None):
		if self.is_in_use_by_patients:
			return False

		pk_doses2keep = [ s['pk_dose'] for s in substance_doses ]
		_log.debug('setting components of "%s" from doses: %s', self._payload[self._idx['product']], pk_doses2keep)

		args = {'pk_drug_product': self._payload[self._idx['pk_drug_product']]}
		queries = []
		# INSERT those which are not there yet
		cmd = """
			INSERT INTO ref.lnk_dose2drug (
				fk_drug_product,
				fk_dose
			)
			SELECT
				%(pk_drug_product)s,
				%(pk_dose)s
			WHERE NOT EXISTS (
				SELECT 1 FROM ref.lnk_dose2drug
				WHERE
					fk_drug_product = %(pk_drug_product)s
						AND
					fk_dose = %(pk_dose)s
			)"""
		for pk_dose in pk_doses2keep:
			args['pk_dose'] = pk_dose
			queries.append({'cmd': cmd, 'args': args.copy()})

		# DELETE those that don't belong anymore
		args['doses2keep'] = tuple(pk_doses2keep)
		cmd = """
			DELETE FROM ref.lnk_dose2drug
			WHERE
				fk_drug_product = %(pk_drug_product)s
					AND
				fk_dose NOT IN %(doses2keep)s"""
		queries.append({'cmd': cmd, 'args': args})
		gmPG2.run_rw_queries(link_obj = link_obj, queries = queries)
		self.refetch_payload(link_obj = link_obj)

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
			'pk_drug_product': self.pk_obj
		}

		cmd = """
			INSERT INTO ref.lnk_dose2drug (fk_drug_product, fk_dose)
			SELECT
				%(pk_drug_product)s,
				%(pk_dose)s
			WHERE NOT EXISTS (
				SELECT 1 FROM ref.lnk_dose2drug
				WHERE
					fk_drug_product = %(pk_drug_product)s
						AND
					fk_dose = %(pk_dose)s
			)"""
		gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])
		self.refetch_payload()

	#------------------------------------------------------------
	def remove_component(self, pk_dose=None, pk_component=None):
		if len(self._payload[self._idx['components']]) == 1:
			_log.error('will not remove the only component of a drug')
			return False

		args = {'pk_drug_product': self.pk_obj, 'pk_dose': pk_dose, 'pk_component': pk_component}

		if pk_component is None:
			cmd = """DELETE FROM ref.lnk_dose2drug WHERE
						fk_drug_product = %(pk_drug_product)s
							AND
						fk_dose = %(pk_dose)s
							AND
						NOT EXISTS (
							SELECT 1 FROM clin.v_substance_intakes
							WHERE pk_dose = %(pk_dose)s
							LIMIT 1
						)"""
		else:
			cmd = """DELETE FROM ref.lnk_dose2drug WHERE
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
			pk_drug_product = self._payload[self._idx['pk_drug_product']],
			pk_identity = pk_patient
		)

	#--------------------------------------------------------
	def turn_into_intake(self, emr=None, encounter=None, episode=None):
		return create_substance_intake (
			pk_drug_product = self._payload[self._idx['pk_drug_product']],
			pk_encounter = encounter,
			pk_episode = episode
		)

	#--------------------------------------------------------
	def delete_associated_vaccine(self):
		if self._payload[self._idx['is_vaccine']] is False:
			return True

		args = {'pk_product': self._payload[self._idx['pk_drug_product']]}
		cmd = """DELETE FROM ref.vaccine
		WHERE
			fk_drug_product = %(pk_product)s
				AND
			-- not in use:
			NOT EXISTS (
				SELECT 1 FROM clin.vaccination WHERE fk_vaccine = (
					select pk from ref.vaccine where fk_drug_product = %(pk_product)s
				)
			)
		RETURNING *"""
		rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = False, return_data = True)
		if len(rows) == 0:
			_log.debug('cannot delete vaccine on: %s', self)
			return False
		return True

	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def _get_external_code(self):
		return self._payload[self._idx['external_code']]

	external_code = property(_get_external_code, lambda x:x)

	#--------------------------------------------------------
	def _get_external_code_type(self):
		# FIXME: maybe evaluate fk_data_source ?
		return self._payload[self._idx['external_code_type']]

	external_code_type = property(_get_external_code_type, lambda x:x)

	#--------------------------------------------------------
	def _get_components(self):
		cmd = _SQL_get_drug_components % 'pk_drug_product = %(product)s'
		args = {'product': self._payload[self._idx['pk_drug_product']]}
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)
		return [ cDrugComponent(row = {'data': r, 'idx': idx, 'pk_field': 'pk_component'}) for r in rows ]

	components = property(_get_components, lambda x:x)

	#--------------------------------------------------------
	def _get_components_as_doses(self):
		pk_doses = [ c['pk_dose'] for c in self._payload[self._idx['components']] ]
		if len(pk_doses) == 0:
			return []
		cmd = _SQL_get_substance_dose % 'pk_dose IN %(pks)s'
		args = {'pks': tuple(pk_doses)}
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)
		return [ cSubstanceDose(row = {'data': r, 'idx': idx, 'pk_field': 'pk_dose'}) for r in rows ]

	components_as_doses = property(_get_components_as_doses, lambda x:x)

	#--------------------------------------------------------
	def _get_components_as_substances(self):
		pk_substances = [ c['pk_substance'] for c in self._payload[self._idx['components']] ]
		if len(pk_substances) == 0:
			return []
		cmd = _SQL_get_substance % 'pk_substance IN %(pks)s'
		args = {'pks': tuple(pk_substances)}
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)
		return [ cSubstance(row = {'data': r, 'idx': idx, 'pk_field': 'pk_substance'}) for r in rows ]

	components_as_substances = property(_get_components_as_substances, lambda x:x)

	#--------------------------------------------------------
	def _get_is_fake_product(self):
		return self._payload[self._idx['is_fake_product']]

	is_fake_product = property(_get_is_fake_product, lambda x:x)

	#--------------------------------------------------------
	def _get_is_vaccine(self):
		return self._payload[self._idx['is_vaccine']]

	is_vaccine = property(_get_is_vaccine, lambda x:x)

	#--------------------------------------------------------
	def _get_is_in_use_by_patients(self):
		cmd = """
			SELECT EXISTS (
				SELECT 1 FROM clin.substance_intake WHERE
					fk_drug_component IN (
						SELECT pk FROM ref.lnk_dose2drug WHERE fk_drug_product = %(pk)s
					)
				LIMIT 1
			)"""
		args = {'pk': self.pk_obj}
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = False)
		return rows[0][0]

	is_in_use_by_patients = property(_get_is_in_use_by_patients, lambda x:x)

	#--------------------------------------------------------
	def _get_is_in_use_as_vaccine(self):
		if self._payload[self._idx['is_vaccine']] is False:
			return False
		cmd = 'SELECT EXISTS(SELECT 1 FROM clin.vaccination WHERE fk_vaccine = (select pk from ref.vaccine where fk_drug_product = %(pk)s))'
		args = {'pk': self.pk_obj}
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = False)
		return rows[0][0]

	is_in_use_as_vaccine = property(_get_is_in_use_as_vaccine, lambda x:x)

#------------------------------------------------------------
def get_drug_products(return_pks=False):
	cmd = _SQL_get_drug_product % 'TRUE ORDER BY product'
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd}], get_col_idx = True)
	if return_pks:
		return [ r['pk_drug_product'] for r in rows ]
	return [ cDrugProduct(row = {'data': r, 'idx': idx, 'pk_field': 'pk_drug_product'}) for r in rows ]

#------------------------------------------------------------
def get_drug_by_name(product_name=None, preparation=None, link_obj=None):
	args = {'prod_name': product_name, 'prep': preparation}
	cmd = 'SELECT * FROM ref.v_drug_products WHERE lower(product) = lower(%(prod_name)s) AND lower(preparation) = lower(%(prep)s)'
	rows, idx = gmPG2.run_ro_queries(link_obj = link_obj, queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)
	if len(rows) == 0:
		return None
	return cDrugProduct(row = {'data': rows[0], 'idx': idx, 'pk_field': 'pk_drug_product'})

#------------------------------------------------------------
def get_drug_by_atc(atc=None, preparation=None, link_obj=None):
	args = {'atc': atc, 'prep': preparation}
	cmd = 'SELECT * FROM ref.v_drug_products WHERE lower(atc) = lower(%(atc)s) AND lower(preparation) = lower(%(prep)s)'
	rows, idx = gmPG2.run_ro_queries(link_obj = link_obj, queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)
	if len(rows) == 0:
		return None
	return cDrugProduct(row = {'data': rows[0], 'idx': idx, 'pk_field': 'pk_drug_product'}, link_obj = link_obj)

#------------------------------------------------------------
def create_drug_product(product_name=None, preparation=None, return_existing=False, link_obj=None, doses=None):
	if preparation is None:
		preparation = _('units')
	if preparation.strip() == '':
		preparation = _('units')
	if return_existing:
		drug = get_drug_by_name(product_name = product_name, preparation = preparation, link_obj = link_obj)
		if drug is not None:
			return drug

	if link_obj is None:
		link_obj = gmPG2.get_connection(readonly = False)
		conn_commit = link_obj.commit
		conn_close = link_obj.close
	else:
		conn_commit = lambda *x:None
		conn_close = lambda *x:None
	cmd = 'INSERT INTO ref.drug_product (description, preparation) VALUES (%(prod_name)s, %(prep)s) RETURNING pk'
	args = {'prod_name': product_name, 'prep': preparation}
	rows, idx = gmPG2.run_rw_queries(link_obj = link_obj, queries = [{'cmd': cmd, 'args': args}], return_data = True, get_col_idx = False)
	product = cDrugProduct(aPK_obj = rows[0]['pk'], link_obj = link_obj)
	if doses is not None:
		product.set_substance_doses_as_components(substance_doses = doses, link_obj = link_obj)
	conn_commit()
	conn_close()
	return product

#------------------------------------------------------------
def create_drug_product_by_atc(atc=None, product_name=None, preparation=None, return_existing=False, link_obj=None):

	if atc is None:
		raise ValueError('cannot create drug product by ATC without ATC')

	if preparation is None:
		preparation = _('units')

	if preparation.strip() == '':
		preparation = _('units')

	if return_existing:
		drug = get_drug_by_atc(atc = atc, preparation = preparation, link_obj = link_obj)
		if drug is not None:
			return drug

	drug = create_drug_product (
		link_obj = link_obj,
		product_name = product_name,
		preparation = preparation,
		return_existing = False
	)
	drug['atc'] = atc
	drug.save(conn = link_obj)
	return drug

#------------------------------------------------------------
def delete_drug_product(pk_drug_product=None):
	args = {'pk': pk_drug_product}
	queries = []
	# delete components
	cmd = """
		DELETE FROM ref.lnk_dose2drug
		WHERE
			fk_drug_product = %(pk)s
				AND
			NOT EXISTS (
				SELECT 1
				FROM clin.v_substance_intakes
				WHERE pk_drug_product = %(pk)s
				LIMIT 1
			)"""
	queries.append({'cmd': cmd, 'args': args})
	# delete drug
	cmd = """
		DELETE FROM ref.drug_product
		WHERE
			pk = %(pk)s
				AND
			NOT EXISTS (
				SELECT 1 FROM clin.v_substance_intakes
				WHERE pk_drug_product = %(pk)s
				LIMIT 1
			)"""
	queries.append({'cmd': cmd, 'args': args})
	gmPG2.run_rw_queries(queries = queries)

#============================================================
# substance intakes
#------------------------------------------------------------
_SQL_get_substance_intake = "SELECT * FROM clin.v_substance_intakes WHERE %s"

class cSubstanceIntakeEntry(gmBusinessDBObject.cBusinessDBObject):
	"""Represents a substance currently taken by a patient."""

	_cmd_fetch_payload = _SQL_get_substance_intake % 'pk_substance_intake = %s'
	_cmds_store_payload = [
		"""UPDATE clin.substance_intake SET
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
		'started',
		'comment_on_start',
		'discontinued',
		'discontinue_reason',
		'intake_is_approved_of',
		'schedule',
		'duration',
		'aim',
		'is_long_term',
		'notes',
		'pk_episode',
		'pk_encounter',
		'harmful_use_type'
	]

	#--------------------------------------------------------
	def format_maximum_information(self, patient=None):
		return self.format (
			single_line = False,
			show_all_product_components = True,
			include_metadata = True,
			date_format = '%Y %b %d',
			include_instructions = True,
			include_loincs = True
		).split('\n')

	#--------------------------------------------------------
	def format(self, left_margin=0, date_format='%Y %b %d', single_line=True, allergy=None, show_all_product_components=False, include_metadata=True, include_instructions=False, include_loincs=False):

		# medication
		if self._payload[self._idx['harmful_use_type']] is None:
			if single_line:
				return self.format_as_single_line(left_margin = left_margin, date_format = date_format)
			return self.format_as_multiple_lines (
				left_margin = left_margin,
				date_format = date_format,
				allergy = allergy,
				show_all_product_components = show_all_product_components,
				include_instructions = include_instructions
			)

		# abuse
		if single_line:
			return self.format_as_single_line_abuse(left_margin = left_margin, date_format = date_format)

		return self.format_as_multiple_lines_abuse(left_margin = left_margin, date_format = date_format, include_metadata = include_metadata)

	#--------------------------------------------------------
	def format_as_single_line_abuse(self, left_margin=0, date_format='%Y %b %d'):
		return '%s%s: %s (%s)' % (
			' ' * left_margin,
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

		line = '%s%s (%s %s): %s %s%s (%s)' % (
			' ' * left_margin,
			self.medically_formatted_start,
			gmTools.u_arrow2right,
			duration,
			self._payload[self._idx['substance']],
			self._payload[self._idx['amount']],
			self.formatted_units,
			gmTools.bool2subst(self._payload[self._idx['is_currently_active']], _('ongoing'), _('inactive'), _('?ongoing'))
		)

		return line

	#--------------------------------------------------------
	def format_as_multiple_lines_abuse(self, left_margin=0, date_format='%Y %b %d', include_metadata=True):

		txt = ''
		if include_metadata:
			txt = _('Substance abuse entry                                              [#%s]\n') % self._payload[self._idx['pk_substance_intake']]
		txt += ' ' + _('Substance: %s [#%s]%s\n') % (
			self._payload[self._idx['substance']],
			self._payload[self._idx['pk_substance']],
			gmTools.coalesce(self._payload[self._idx['atc_substance']], '', ' ATC %s')
		)
		txt += ' ' + _('Use type: %s\n') % self.harmful_use_type_string
		txt += ' ' + _('Last checked: %s\n') % gmDateTime.pydt_strftime(self._payload[self._idx['last_checked_when']], '%Y %b %d')
		if self._payload[self._idx['discontinued']] is not None:
			txt += _(' Discontinued %s\n') % (
				gmDateTime.pydt_strftime (
					self._payload[self._idx['discontinued']],
					format = date_format,
					accuracy = gmDateTime.acc_days
				)
			)
		txt += gmTools.coalesce(self._payload[self._idx['notes']], '', _(' Notes: %s\n'))
		if include_metadata:
			txt += '\n'
			txt += _('Revision: #%(row_ver)s, %(mod_when)s by %(mod_by)s.') % {
				'row_ver': self._payload[self._idx['row_version']],
				'mod_when': gmDateTime.pydt_strftime(self._payload[self._idx['modified_when']]),
				'mod_by': self._payload[self._idx['modified_by']]
			}

		return txt

	#--------------------------------------------------------
	def format_as_multiple_lines(self, left_margin=0, date_format='%Y %b %d', allergy=None, show_all_product_components=False, include_instructions=False, include_loincs=False):

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
			txt += '\n'
			txt += ' !! ---- Cave ---- !!\n'
			txt += ' %s (%s): %s (%s)\n' % (
				allergy['l10n_type'],
				certainty,
				allergy['descriptor'],
				gmTools.coalesce(allergy['reaction'], '')[:40]
			)
			txt += '\n'

		txt += ' ' + _('Substance: %s   [#%s]\n') % (self._payload[self._idx['substance']], self._payload[self._idx['pk_substance']])
		txt += ' ' + _('Preparation: %s\n') % self._payload[self._idx['l10n_preparation']]
		txt += ' ' + _('Amount per dose: %s %s') % (
			self._payload[self._idx['amount']],
			self._get_formatted_units(short = False)
		)
		txt += '\n'
		txt += gmTools.coalesce(self._payload[self._idx['atc_substance']], '', _(' ATC (substance): %s\n'))
		if include_loincs and (len(self._payload[self._idx['loincs']]) > 0):
			loincs = """
%s %s
%s  %s""" 	% (
				(' ' * left_margin),
				_('LOINCs to monitor:'),
				(' ' * left_margin),
				('\n' + (' ' * (left_margin + 1))).join ([
					'%s%s%s' % (
						l['loinc'],
						gmTools.coalesce(l['max_age_str'], '', ': ' + _('once within %s')),
						gmTools.coalesce(l['comment'], '', ' (%s)')
					) for l in self._payload[self._idx['loincs']]
				])
			)
		txt += '\n'

		txt += '\n'

		txt += _(' Product name: %s   [#%s]\n') % (self._payload[self._idx['product']], self._payload[self._idx['pk_drug_product']])
		txt += gmTools.coalesce(self._payload[self._idx['atc_drug']], '', _(' ATC (drug): %s\n'))
		if show_all_product_components:
			product = self.containing_drug
			if len(product['components']) > 1:
				for comp in product['components']:
					if comp['pk_substance'] == self._payload[self._idx['substance']]:
						continue
					txt += ('  ' + _('Other component: %s %s %s\n') % (
						comp['substance'],
						comp['amount'],
						format_units(comp['unit'], comp['dose_unit'])
					))
					txt += gmTools.coalesce(comp['intake_instructions'], '', '   ' + _('Intake: %s') + '\n')
					if include_loincs and (len(comp['loincs']) > 0):
						txt += ('   ' + _('LOINCs to monitor:') + '\n')
						txt += '\n'.join([ '    %s%s%s' % (
							l['loinc'],
							gmTools.coalesce(l['max_age_str'], '', ': %s'),
							gmTools.coalesce(l['comment'], '', ' (%s)')
						) for l in comp['loincs'] ])

		txt += '\n'

		txt += gmTools.coalesce(self._payload[self._idx['schedule']], '', _(' Regimen: %s\n'))

		if self._payload[self._idx['is_long_term']]:
			duration = ' %s %s' % (gmTools.u_arrow2right, gmTools.u_infinity)
		else:
			if self._payload[self._idx['duration']] is None:
				duration = ''
			else:
				duration = ' %s %s' % (gmTools.u_arrow2right, gmDateTime.format_interval(self._payload[self._idx['duration']], gmDateTime.acc_days))

		txt += _(' Started %s%s%s\n') % (
			self.medically_formatted_start,
			duration,
			gmTools.bool2subst(self._payload[self._idx['is_long_term']], _(' (long-term)'), _(' (short-term)'), '')
		)

		if self._payload[self._idx['discontinued']] is not None:
			txt += _(' Discontinued %s\n') % (
				gmDateTime.pydt_strftime (
					self._payload[self._idx['discontinued']],
					format = date_format,
					accuracy = gmDateTime.acc_days
				)
			)
			txt += gmTools.coalesce(self._payload[self._idx['discontinue_reason']], '', _(' Reason: %s\n'))

		txt += '\n'

		txt += gmTools.coalesce(self._payload[self._idx['aim']], '', _(' Aim: %s\n'))
		txt += gmTools.coalesce(self._payload[self._idx['episode']], '', _(' Episode: %s\n'))
		txt += gmTools.coalesce(self._payload[self._idx['health_issue']], '', _(' Health issue: %s\n'))
		txt += gmTools.coalesce(self._payload[self._idx['notes']], '', _(' Advice: %s\n'))
		if self._payload[self._idx['intake_instructions']] is not None:
			txt += (' '+ (_('Intake: %s') % self._payload[self._idx['intake_instructions']]) + '\n')
		if len(self._payload[self._idx['loincs']]) > 0:
			txt += (' ' + _('LOINCs to monitor:') + '\n')
			txt += '\n'.join([ '  %s%s%s' % (
				l['loinc'],
				gmTools.coalesce(l['max_age_str'], '', ': %s'),
				gmTools.coalesce(l['comment'], '', ' (%s)')
			) for l in self._payload[self._idx['loincs']] ])

		txt += '\n'

		txt += _('Revision: #%(row_ver)s, %(mod_when)s by %(mod_by)s.') % {
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
			self._payload[self._idx['product']],
			self._payload[self._idx['substance']]
		)
		allg['reaction'] = self._payload[self._idx['discontinue_reason']]
		allg['atc_code'] = gmTools.coalesce(self._payload[self._idx['atc_substance']], self._payload[self._idx['atc_drug']])
		if self._payload[self._idx['external_code_product']] is not None:
			allg['substance_code'] = '%s::::%s' % (self._payload[self._idx['external_code_type_product']], self._payload[self._idx['external_code_product']])

		if self._payload[self._idx['pk_drug_product']] is None:
			allg['generics'] = self._payload[self._idx['substance']]
		else:
			comps = [ c['substance'] for c in self.containing_drug.components ]
			if len(comps) == 0:
				allg['generics'] = self._payload[self._idx['substance']]
			else:
				allg['generics'] = '; '.join(comps)

		allg.save()
		return allg

	#--------------------------------------------------------
	def delete(self):
		return delete_substance_intake(pk_intake = self._payload[self._idx['pk_substance_intake']])

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
		if self._payload[self._idx['pk_drug_product']] is None:
			return None

		return cDrugProduct(aPK_obj = self._payload[self._idx['pk_drug_product']])

	containing_drug = property(_get_containing_drug, lambda x:x)

	#--------------------------------------------------------
	def _get_formatted_units(self, short=True):
		return format_units (
			self._payload[self._idx['unit']],
			self._payload[self._idx['dose_unit']],
			self._payload[self._idx['l10n_preparation']],
			short = short
		)

	formatted_units = property(_get_formatted_units, lambda x:x)

	#--------------------------------------------------------
	def _get_medically_formatted_start(self):
		if self._payload[self._idx['comment_on_start']] == '?':
			return '?'

		start_prefix = ''
		if self._payload[self._idx['comment_on_start']] is not None:
			start_prefix = gmTools.u_almost_equal_to

		duration_taken = gmDateTime.pydt_now_here() - self._payload[self._idx['started']]

		three_months = pydt.timedelta(weeks = 13, days = 3)
		if duration_taken < three_months:
			return _('%s%s: %s ago%s') % (
				start_prefix,
				gmDateTime.pydt_strftime(self._payload[self._idx['started']], '%Y %b %d', 'utf8', gmDateTime.acc_days),
				gmDateTime.format_interval_medically(duration_taken),
				gmTools.coalesce(self._payload[self._idx['comment_on_start']], '', ' (%s)')
			)

		five_years = pydt.timedelta(weeks = 265)
		if duration_taken < five_years:
			return _('%s%s: %s ago (%s)') % (
				start_prefix,
				gmDateTime.pydt_strftime(self._payload[self._idx['started']], '%Y %b', 'utf8', gmDateTime.acc_months),
				gmDateTime.format_interval_medically(duration_taken),
				gmTools.coalesce (
					self._payload[self._idx['comment_on_start']],
					gmDateTime.pydt_strftime(self._payload[self._idx['started']], '%b %d', 'utf8', gmDateTime.acc_days),
				)
			)

		return _('%s%s: %s ago (%s)') % (
			start_prefix,
			gmDateTime.pydt_strftime(self._payload[self._idx['started']], '%Y', 'utf8', gmDateTime.acc_years),
			gmDateTime.format_interval_medically(duration_taken),
			gmTools.coalesce (
				self._payload[self._idx['comment_on_start']],
				gmDateTime.pydt_strftime(self._payload[self._idx['started']], '%b %d', 'utf8', gmDateTime.acc_days),
			)
		)

	medically_formatted_start = property(_get_medically_formatted_start, lambda x:x)

	#--------------------------------------------------------
	def _get_medically_formatted_start_end_of_stopped(self, now):

		# format intro
		if gmDateTime.pydt_is_today(self._payload[self._idx['discontinued']]):
			intro = _('until today')
		else:
			ended_ago = now - self._payload[self._idx['discontinued']]
			intro = _('until %s%s ago') % (
				gmTools.u_almost_equal_to,
				gmDateTime.format_interval_medically(ended_ago),
			)

		# format start
		if self._payload[self._idx['started']] is None:
			start = gmTools.coalesce(self._payload[self._idx['comment_on_start']], '?')
		else:
			start = '%s%s%s' % (
				gmTools.bool2subst((self._payload[self._idx['comment_on_start']] is None), '', gmTools.u_almost_equal_to),
				gmDateTime.pydt_strftime(self._payload[self._idx['started']], format = '%Y %b %d', accuracy = gmDateTime.acc_days),
				gmTools.coalesce(self._payload[self._idx['comment_on_start']], '', ' [%s]')
			)

		# format duration taken
		if self._payload[self._idx['started']] is None:
			duration_taken_str = '?'
		else:
			duration_taken = self._payload[self._idx['discontinued']] - self._payload[self._idx['started']] + pydt.timedelta(days = 1)
			duration_taken_str = gmDateTime.format_interval (duration_taken, gmDateTime.acc_days)

		# format duration planned
		if self._payload[self._idx['duration']] is None:
			duration_planned_str = ''
		else:
			duration_planned_str = _(' [planned: %s]') % gmDateTime.format_interval(self._payload[self._idx['duration']], gmDateTime.acc_days)

		# format end
		end = gmDateTime.pydt_strftime(self._payload[self._idx['discontinued']], '%Y %b %d', 'utf8', gmDateTime.acc_days)

		# assemble
		txt = '%s (%s %s %s%s %s %s)' % (
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
			start_str = gmTools.coalesce(self._payload[self._idx['comment_on_start']], '?')
		else:
			start_prefix = gmTools.bool2subst((self._payload[self._idx['comment_on_start']] is None), '', gmTools.u_almost_equal_to)
			# starts today
			if gmDateTime.pydt_is_today(self._payload[self._idx['started']]):
				start_str = _('today (%s)') % gmDateTime.pydt_strftime(self._payload[self._idx['started']], format = '%Y %b %d', accuracy = gmDateTime.acc_days)
			# started in the past
			elif self._payload[self._idx['started']] < now:
				started_ago = now - self._payload[self._idx['started']]
				three_months = pydt.timedelta(weeks = 13, days = 3)
				five_years = pydt.timedelta(weeks = 265)
				if started_ago < three_months:
					start_str = _('%s%s%s (%s%s ago, in %s)') % (
						start_prefix,
						gmDateTime.pydt_strftime(self._payload[self._idx['started']], format = '%b %d', accuracy = gmDateTime.acc_days),
						gmTools.coalesce(self._payload[self._idx['comment_on_start']], '', ' [%s]'),
						gmTools.u_almost_equal_to,
						gmDateTime.format_interval_medically(started_ago),
						gmDateTime.pydt_strftime(self._payload[self._idx['started']], format = '%Y', accuracy = gmDateTime.acc_days)
					)
				elif started_ago < five_years:
					start_str = _('%s%s%s (%s%s ago, %s)') % (
						start_prefix,
						gmDateTime.pydt_strftime(self._payload[self._idx['started']], '%Y %b', 'utf8', gmDateTime.acc_months),
						gmTools.coalesce(self._payload[self._idx['comment_on_start']], '', ' [%s]'),
						gmTools.u_almost_equal_to,
						gmDateTime.format_interval_medically(started_ago),
						gmDateTime.pydt_strftime(self._payload[self._idx['started']], '%b %d', 'utf8', gmDateTime.acc_days)
					)
				else:
					start_str = _('%s%s%s (%s%s ago, %s)') % (
						start_prefix,
						gmDateTime.pydt_strftime(self._payload[self._idx['started']], '%Y', 'utf8', gmDateTime.acc_years),
						gmTools.coalesce(self._payload[self._idx['comment_on_start']], '', ' [%s]'),
						gmTools.u_almost_equal_to,
						gmDateTime.format_interval_medically(started_ago),
						gmDateTime.pydt_strftime(self._payload[self._idx['started']], '%b %d', 'utf8', gmDateTime.acc_days),
					)
			# starts in the future
			else:
				starts_in = self._payload[self._idx['started']] - now
				start_str = _('%s%s%s (in %s%s)') % (
					start_prefix,
					gmDateTime.pydt_strftime(self._payload[self._idx['started']], '%Y %b %d', 'utf8', gmDateTime.acc_days),
					gmTools.coalesce(self._payload[self._idx['comment_on_start']], '', ' [%s]'),
					gmTools.u_almost_equal_to,
					gmDateTime.format_interval_medically(starts_in)
				)

		arrow_parts.append(start_str)

		# format durations
		durations = []
		if self._payload[self._idx['discontinued']] is not None:
			if self._payload[self._idx['started']] is not None:
				duration_documented = self._payload[self._idx['discontinued']] - self._payload[self._idx['started']]
				durations.append(_('%s (documented)') % gmDateTime.format_interval(duration_documented, gmDateTime.acc_days))
		if self._payload[self._idx['duration']] is not None:
			durations.append(_('%s (plan)') % gmDateTime.format_interval(self._payload[self._idx['duration']], gmDateTime.acc_days))
		if len(durations) == 0:
			if self._payload[self._idx['is_long_term']]:
				duration_str = gmTools.u_infinity
			else:
				duration_str = '?'
		else:
			duration_str = ', '.join(durations)

		arrow_parts.append(duration_str)

		# format end
		if self._payload[self._idx['discontinued']] is None:
			if self._payload[self._idx['duration']] is None:
				end_str = '?'
			else:
				if self._payload[self._idx['started']] is None:
					end_str = '?'
				else:
					planned_end = self._payload[self._idx['started']] + self._payload[self._idx['duration']] - pydt.timedelta(days = 1)
					if planned_end.year == now.year:
						end_template = '%b %d'
						if planned_end < now:
							planned_end_from_now_str = _('%s ago, in %s') % (gmDateTime.format_interval(now - planned_end, gmDateTime.acc_days), planned_end.year)
						else:
							planned_end_from_now_str = _('in %s, %s') % (gmDateTime.format_interval(planned_end - now, gmDateTime.acc_days), planned_end.year)
					else:
						end_template = '%Y'
						if planned_end < now:
							planned_end_from_now_str = _('%s ago = %s') % (
								gmDateTime.format_interval(now - planned_end, gmDateTime.acc_days),
								gmDateTime.pydt_strftime(planned_end, '%b %d', 'utf8', gmDateTime.acc_days)
							)
						else:
							planned_end_from_now_str = _('in %s = %s') % (
								gmDateTime.format_interval(planned_end - now, gmDateTime.acc_days),
								gmDateTime.pydt_strftime(planned_end, '%b %d', 'utf8', gmDateTime.acc_days)
							)
					end_str = '%s (%s)' % (
						gmDateTime.pydt_strftime(planned_end, end_template, 'utf8', gmDateTime.acc_days),
						planned_end_from_now_str
					)
		else:
			if gmDateTime.is_today(self._payload[self._idx['discontinued']]):
				end_str = _('today')
			elif self._payload[self._idx['discontinued']].year == now.year:
				end_date_template = '%b %d'
				if self._payload[self._idx['discontinued']] < now:
					planned_end_from_now_str = _('%s ago, in %s') % (
						gmDateTime.format_interval(now - self._payload[self._idx['discontinued']], gmDateTime.acc_days),
						self._payload[self._idx['discontinued']].year
					)
				else:
					planned_end_from_now_str = _('in %s, %s') % (
						gmDateTime.format_interval(self._payload[self._idx['discontinued']] - now, gmDateTime.acc_days),
						self._payload[self._idx['discontinued']].year
					)
			else:
				end_date_template = '%Y'
				if self._payload[self._idx['discontinued']] < now:
					planned_end_from_now_str = _('%s ago = %s') % (
						gmDateTime.format_interval(now - self._payload[self._idx['discontinued']], gmDateTime.acc_days),
						gmDateTime.pydt_strftime(self._payload[self._idx['discontinued']], '%b %d', 'utf8', gmDateTime.acc_days)
					)
				else:
					planned_end_from_now_str = _('in %s = %s') % (
						gmDateTime.format_interval(self._payload[self._idx['discontinued']] - now, gmDateTime.acc_days),
						gmDateTime.pydt_strftime(self._payload[self._idx['discontinued']], '%b %d', 'utf8', gmDateTime.acc_days)
					)
			end_str = '%s (%s)' % (
				gmDateTime.pydt_strftime(self._payload[self._idx['discontinued']], end_date_template, 'utf8', gmDateTime.acc_days),
				planned_end_from_now_str
			)

		arrow_parts.append(end_str)

		# assemble
		return (' %s ' % gmTools.u_arrow2right_thick).join(arrow_parts)

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
			print(test.strip(), ":", regex.match(pattern, test.strip()))

#------------------------------------------------------------
def get_substance_intakes(pk_patient=None, return_pks=False):
	args = {'pat': pk_patient}
	if pk_patient is None:
		cmd = _SQL_get_substance_intake % 'true'
	else:
		cmd = _SQL_get_substance_intake % 'pk_patient = %(pat)s'
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd}], get_col_idx = True)
	if return_pks:
		return [ r['pk_substance_intake'] for r in rows ]
	return [ cSubstanceIntakeEntry(row = {'data': r, 'idx': idx, 'pk_field': 'pk_substance_intake'}) for r in rows ]

#------------------------------------------------------------
def substance_intake_exists(pk_component=None, pk_identity=None, pk_drug_product=None, pk_dose=None):

	if [pk_component, pk_drug_product, pk_dose].count(None) != 2:
		raise ValueError('only one of pk_component, pk_dose, and pk_drug_product can be non-NULL')

	args = {
		'pk_comp': pk_component,
		'pk_pat': pk_identity,
		'pk_drug_product': pk_drug_product,
		'pk_dose': pk_dose
	}
	where_parts = ['fk_encounter IN (SELECT pk FROM clin.encounter WHERE fk_patient = %(pk_pat)s)']

	if pk_dose is not None:
		where_parts.append('fk_drug_component IN (SELECT pk FROM ref.lnk_dose2drug WHERE fk_dose = %(pk_dose)s)')
	if pk_component is not None:
		where_parts.append('fk_drug_component = %(pk_comp)s')
	if pk_drug_product is not None:
		where_parts.append('fk_drug_component IN (SELECT pk FROM ref.lnk_dose2drug WHERE fk_drug_product = %(pk_drug_product)s)')

	cmd = """
		SELECT EXISTS (
			SELECT 1 FROM clin.substance_intake
			WHERE
				%s
			LIMIT 1
		)
	""" % '\nAND\n'.join(where_parts)

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
		'pk_patient = %(pat)s',
		'((atc_substance = %(atc)s) OR (atc_drug = %(atc)s))'
	]
	cmd = """
		SELECT EXISTS (
			SELECT 1 FROM clin.v_substance_intakes
			WHERE
				%s
			LIMIT 1
		)
	""" % '\nAND\n'.join(where_parts)

	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}])
	return rows[0][0]

#------------------------------------------------------------
def create_substance_intake(pk_component=None, pk_encounter=None, pk_episode=None, pk_drug_product=None):

	if [pk_component, pk_drug_product].count(None) != 1:
		raise ValueError('only one of pk_component and pk_drug_product can be non-NULL')

	args = {
		'pk_enc': pk_encounter,
		'pk_epi': pk_episode,
		'pk_comp': pk_component,
		'pk_drug_product': pk_drug_product
	}

	if pk_drug_product is not None:
		cmd = """
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
				(SELECT pk FROM ref.lnk_dose2drug WHERE fk_drug_product = %(pk_drug_product)s LIMIT 1)
			)
			RETURNING pk"""

	if pk_component is not None:
		cmd = """
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
	except gmPG2.dbapi.InternalError as exc:
		if exc.pgerror is None:
			raise
		if 'prevent_duplicate_component' in exc.pgerror:
			_log.exception('will not create duplicate substance intake entry')
			gmPG2.log_pg_exception_details(exc)
			return None
		raise

	return cSubstanceIntakeEntry(aPK_obj = rows[0][0])

#------------------------------------------------------------
def delete_substance_intake(pk_intake=None, delete_siblings=False):
	if delete_siblings:
		cmd = """
			DELETE FROM clin.substance_intake c_si
			WHERE
				c_si.fk_drug_component IN (
					SELECT r_ld2d.pk FROM ref.lnk_dose2drug r_ld2d
					WHERE r_ld2d.fk_drug_product = (
						SELECT c_vsi1.pk_drug_product FROM clin.v_substance_intakes c_vsi1 WHERE c_vsi1.pk_substance_intake = %(pk)s
					)
				)
					AND
				c_si.fk_encounter IN (
					SELECT c_e.pk FROM clin.encounter c_e
					WHERE c_e.fk_patient = (
						SELECT c_vsi2.pk_patient FROM clin.v_substance_intakes c_vsi2 WHERE c_vsi2.pk_substance_intake = %(pk)s
					)
				)"""
	else:
		cmd = 'DELETE FROM clin.substance_intake WHERE pk = %(pk)s'

	gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': {'pk': pk_intake}}])
	return True

#------------------------------------------------------------
# AMTS formatting
#------------------------------------------------------------
def format_substance_intake_as_amts_latex(intake=None, strict=True):

	_esc = gmTools.tex_escape_string

	# %(contains)s & %(product)s & %(amount)s%(unit)s & %(preparation)s & \multicolumn{4}{l|}{%(schedule)s} & Einheit & %(notes)s & %(aim)s \tabularnewline{}\hline
	cells = []
	# components
	components = intake.containing_drug['components']
	if len(components) > 3:
		cells.append(_esc('WS-Kombi.'))
	elif len(components) == 1:
		c = components[0]
		if strict:
			cells.append('\\mbox{%s}' % _esc(c['substance'][:80]))
		else:
			cells.append('\\mbox{%s}' % _esc(c['substance']))
	else:
		if strict:
			cells.append('\\fontsize{10pt}{12pt}\selectfont %s ' % '\\newline '.join(['\\mbox{%s}' % _esc(c['substance'][:80]) for c in components]))
		else:
			cells.append('\\fontsize{10pt}{12pt}\selectfont %s ' % '\\newline '.join(['\\mbox{%s}' % _esc(c['substance']) for c in components]))
	# product
	if strict:
		cells.append(_esc(intake['product'][:50]))
	else:
		cells.append(_esc(intake['product']))
	# Wirkstärken
	if len(components) > 3:
		cells.append('')
	elif len(components) == 1:
		c = components[0]
		dose = ('%s%s' % (c['amount'], format_units(c['unit'], c['dose_unit'], short = True))).replace('.', ',')
		if strict:
			dose = dose[:11]
		cells.append(_esc(dose))
	else:		# 2
		if strict:
			doses = '\\fontsize{10pt}{12pt}\selectfont %s ' % '\\newline\\ '.join ([
				_esc(('%s%s' % (
					('%s' % c['amount']).replace('.', ','),
					format_units(c['unit'], c['dose_unit'], short = True)
				))[:11]) for c in components
			])
		else:
			doses = '\\fontsize{10pt}{12pt}\selectfont %s ' % '\\newline\\ '.join ([
				_esc('%s%s' % (
					('%s' % c['amount']).replace('.', ','),
					format_units(c['unit'], c['dose_unit'], short = True)
				)) for c in components
			])
		cells.append(doses)
	# preparation
	if strict:
		cells.append(_esc(intake['l10n_preparation'][:7]))
	else:
		cells.append(_esc(intake['l10n_preparation']))
	# schedule - for now be simple - maybe later parse 1-1-1-1 etc
	if intake['schedule'] is None:
		cells.append('\\multicolumn{4}{p{3.2cm}|}{\\ }')
	else:
		# spec says [:20] but implementation guide says: never trim
		if len(intake['schedule']) > 20:
			cells.append('\\multicolumn{4}{>{\\RaggedRight}p{3.2cm}|}{\\fontsize{10pt}{12pt}\selectfont %s}' % _esc(intake['schedule']))
		else:
			cells.append('\\multicolumn{4}{>{\\RaggedRight}p{3.2cm}|}{%s}' % _esc(intake['schedule']))
	# Einheit to take
	cells.append('')#[:20]
	# notes
	if intake['notes'] is None:
		cells.append(' ')
	else:
		if strict:
			cells.append(_esc(intake['notes'][:80]))
		else:
			cells.append('\\fontsize{10pt}{12pt}\selectfont %s ' % _esc(intake['notes']))
	# aim
	if intake['aim'] is None:
		#cells.append(' ')
		cells.append(_esc(intake['episode'][:50]))
	else:
		if strict:
			cells.append(_esc(intake['aim'][:50]))
		else:
			cells.append('\\fontsize{10pt}{12pt}\selectfont %s ' % _esc(intake['aim']))

	table_row = ' & '.join(cells)
	table_row += '\\tabularnewline{}\n\\hline'

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
	M_fields.append('a="%s"' % intake['product'])
	M_fields.append('fd="%s"' % intake['l10n_preparation'])
	if intake['schedule'] is not None:
		M_fields.append('t="%s"' % intake['schedule'])
	#M_fields.append(u'dud="%s"' % intake['dose unit, like Stück'])
	if intake['aim'] is None:
		M_fields.append('r="%s"' % intake['episode'])
	else:
		M_fields.append('r="%s"' % intake['aim'])
	if intake['notes'] is not None:
		M_fields.append('i="%s"' % intake['notes'])
	M_line = '<M %s>' % ' '.join(M_fields)

	W_lines = []
	for comp in intake.containing_drug['components']:
		W_lines.append('<W w="%s" s="%s %s"/>' % (
			comp['substance'],
			comp['amount'],
			format_units(comp['unit'], comp['dose_unit'], short = True)
		))

	return M_line + ''.join(W_lines) + '</M>'

#------------------------------------------------------------
def generate_amts_data_template_definition_file(work_dir=None, strict=True):

	_log.debug('generating AMTS data template definition file(workdir=%s, strict=%s)', work_dir, strict)

	if not strict:
		return __generate_enhanced_amts_data_template_definition_file(work_dir = work_dir)

	amts_lines = [ l for l in ('<MP v="023" U="%s"' % uuid.uuid4().hex + """ l="de-DE"$<<if_not_empty::$<amts_page_idx::::1>$// a="%s"//::>>$$<<if_not_empty::$<amts_page_idx::::>$// z="$<amts_total_pages::::1>$"//::>>$>
<P g="$<name::%(firstnames)s::45>$" f="$<name::%(lastnames)s::45>$" b="$<date_of_birth::%Y%m%d::8>$"/>
<A
 n="$<<range_of::$<praxis::%(praxis)s,%(branch)s::>$,$<current_provider::::>$::30>>$"
$<praxis_address:: s="%(street)s"::>$
$<praxis_address:: z="%(postcode)s"::>$
$<praxis_address:: c="%(urb)s"::>$
$<praxis_comm::workphone// p="%(url)s"::20>$
$<praxis_comm::email// e="%(url)s"::80>$
 t="$<today::%Y%m%d::8>$"
/>
<O ai="s.S.$<amts_total_pages::::1>$ unten"/>
$<amts_intakes_as_data::::9999999>$
</MP>""").split('\n') ]
#$<<if_not_empty::$<allergy_list::%(descriptor)s//,::>$//<O ai="%s"/>::>>$

	amts_fname = gmTools.get_unique_filename (
		prefix = 'gm2amts_data-',
		suffix = '.txt',
		tmp_dir = work_dir
	)
	amts_template = io.open(amts_fname, mode = 'wt', encoding = 'utf8')
	amts_template.write('[form]\n')
	amts_template.write('template = $template$\n')
	amts_template.write(''.join(amts_lines))
	amts_template.write('\n')
	amts_template.write('$template$\n')
	amts_template.close()

	return amts_fname

#------------------------------------------------------------
def __generate_enhanced_amts_data_template_definition_file(work_dir=None):

	amts_lines = [ l for l in ('<MP v="023" U="%s"' % uuid.uuid4().hex + """ l="de-DE" a="1" z="1">
<P g="$<name::%(firstnames)s::>$" f="$<name::%(lastnames)s::>$" b="$<date_of_birth::%Y%m%d::8>$"/>
<A
 n="$<praxis::%(praxis)s,%(branch)s::>$,$<current_provider::::>$"
$<praxis_address:: s="%(street)s %(number)s %(subunit)s"::>$
$<praxis_address:: z="%(postcode)s"::>$
$<praxis_address:: c="%(urb)s"::>$
$<praxis_comm::workphone// p="%(url)s"::>$
$<praxis_comm::email// e="%(url)s"::>$
 t="$<today::%Y%m%d::8>$"
/>
<O ai="Seite 1 unten"/>
$<amts_intakes_as_data_enhanced::::9999999>$
</MP>""").split('\n') ]
#$<<if_not_empty::$<allergy_list::%(descriptor)s//,::>$//<O ai="%s"/>::>>$

	amts_fname = gmTools.get_unique_filename (
		prefix = 'gm2amts_data-utf8-unabridged-',
		suffix = '.txt',
		tmp_dir = work_dir
	)
	amts_template = io.open(amts_fname, mode = 'wt', encoding = 'utf8')
	amts_template.write('[form]\n')
	amts_template.write('template = $template$\n')
	amts_template.write(''.join(amts_lines))
	amts_template.write('\n')
	amts_template.write('$template$\n')
	amts_template.close()

	return amts_fname

#------------------------------------------------------------
# AMTS v2.0 -- outdated
#------------------------------------------------------------
def format_substance_intake_as_amts_data_v2_0(intake=None, strict=True):

	if not strict:
		pass
		# relax length checks

	fields = []

	# components
	components = [ c.split('::') for c in intake.containing_drug['components'] ]
	if len(components) > 3:
		fields.append('WS-Kombi.')
	elif len(components) == 1:
		c = components[0]
		fields.append(c[0][:80])
	else:
		fields.append('~'.join([c[0][:80] for c in components]))
	# product
	fields.append(intake['product'][:50])
	# Wirkstärken
	if len(components) > 3:
		fields.append('')
	elif len(components) == 1:
		c = components[0]
		fields.append(('%s%s' % (c[1], c[2]))[:11])
	else:
		fields.append('~'.join([('%s%s' % (c[1], c[2]))[:11] for c in components]))
	# preparation
	fields.append(intake['l10n_preparation'][:7])
	# schedule - for now be simple - maybe later parse 1-1-1-1 etc
	fields.append(gmTools.coalesce(intake['schedule'], '')[:20])
	# Einheit to take
	fields.append('')#[:20]
	# notes
	fields.append(gmTools.coalesce(intake['notes'], '')[:80])
	# aim
	fields.append(gmTools.coalesce(intake['aim'], '')[:50])

	return '|'.join(fields)

#------------------------------------------------------------
def calculate_amts_data_check_symbol_v2_0(intakes=None):

	# first char of generic substance or product name
	first_chars = []
	for intake in intakes:
		first_chars.append(intake['product'][0])

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
		return '%s' % remainder
	# 10-35 -> 'A' - 'Z'
	return chr(remainder + 55)

#------------------------------------------------------------
def generate_amts_data_template_definition_file_v2_0(work_dir=None, strict=True):

	if not strict:
		return __generate_enhanced_amts_data_template_definition_file(work_dir = work_dir)

	amts_fields = [
		'MP',
		'020',	# Version
		'DE',	# Land
		'DE',	# Sprache
		'1',	# Zeichensatz 1 = Ext ASCII (fest) = ISO8859-1 = Latin1
		'$<today::%Y%m%d::8>$',
		'$<amts_page_idx::::1>$',				# to be set by code using the template
		'$<amts_total_pages::::1>$',			# to be set by code using the template
		'0',	# Zertifizierungsstatus

		'$<name::%(firstnames)s::45>$',
		'$<name::%(lastnames)s::45>$',
		'',	# Patienten-ID
		'$<date_of_birth::%Y%m%d::8>$',

		'$<<range_of::$<praxis::%(praxis)s,%(branch)s::>$,$<current_provider::::>$::30>>$',
		'$<praxis_address::%(street)s %(number)s %(subunit)s|%(postcode)s|%(urb)s::57>$',		# 55+2 because of 2 embedded "|"s
		'$<praxis_comm::workphone::20>$',
		'$<praxis_comm::email::80>$',

		#u'264 $<allergy_state::::21>$',				# param 1, Allergien 25-4 (4 for "264 ", spec says max of 25)
		'264 Seite $<amts_total_pages::::1>$ unten',	# param 1, Allergien 25-4 (4 for "264 ", spec says max of 25)
		'', # param 2, not used currently
		'', # param 3, not used currently

		# Medikationseinträge
		'$<amts_intakes_as_data::::9999999>$',

		'$<amts_check_symbol::::1>$',	# Prüfzeichen, value to be set by code using the template, *per page* !
		'#@',							# Endesymbol
	]

	amts_fname = gmTools.get_unique_filename (
		prefix = 'gm2amts_data-',
		suffix = '.txt',
		tmp_dir = work_dir
	)
	amts_template = io.open(amts_fname, mode = 'wt', encoding = 'utf8')
	amts_template.write('[form]\n')
	amts_template.write('template = $template$\n')
	amts_template.write('|'.join(amts_fields))
	amts_template.write('\n')
	amts_template.write('$template$\n')
	amts_template.close()

	return amts_fname

#------------------------------------------------------------
def __generate_enhanced_amts_data_template_definition_file_v2_0(work_dir=None):

	amts_fields = [
		'MP',
		'020',	# Version
		'DE',	# Land
		'DE',	# Sprache
		'1',	# Zeichensatz 1 = Ext ASCII (fest) = ISO8859-1 = Latin1
		'$<today::%Y%m%d::8>$',
		'1',	# idx of this page
		'1',	# total pages
		'0',	# Zertifizierungsstatus

		'$<name::%(firstnames)s::>$',
		'$<name::%(lastnames)s::>$',
		'',	# Patienten-ID
		'$<date_of_birth::%Y%m%d::8>$',

		'$<praxis::%(praxis)s,%(branch)s::>$,$<current_provider::::>$',
		'$<praxis_address::%(street)s %(number)s %(subunit)s::>$',
		'$<praxis_address::%(postcode)s::>$',
		'$<praxis_address::%(urb)s::>$',
		'$<praxis_comm::workphone::>$',
		'$<praxis_comm::email::>$',

		#u'264 $<allergy_state::::>$', 					# param 1, Allergien
		'264 Seite 1 unten',							# param 1, Allergien
		'', # param 2, not used currently
		'', # param 3, not used currently

		# Medikationseinträge
		'$<amts_intakes_as_data_enhanced::::>$',

		'$<amts_check_symbol::::1>$',	# Prüfzeichen, value to be set by code using the template, *per page* !
		'#@',							# Endesymbol
	]

	amts_fname = gmTools.get_unique_filename (
		prefix = 'gm2amts_data-utf8-unabridged-',
		suffix = '.txt',
		tmp_dir = work_dir
	)
	amts_template = io.open(amts_fname, mode = 'wt', encoding = 'utf8')
	amts_template.write('[form]\n')
	amts_template.write('template = $template$\n')
	amts_template.write('|'.join(amts_fields))
	amts_template.write('\n')
	amts_template.write('$template$\n')
	amts_template.close()

	return amts_fname

#------------------------------------------------------------
# other formatting
#------------------------------------------------------------
def format_substance_intake_notes(emr=None, output_format='latex', table_type=u'by-product'):

	tex = '%s\n' % _('Additional notes for healthcare professionals')
	tex += '%%%% requires "\\usepackage{longtable}"\n'
	tex += '%%%% requires "\\usepackage{tabu}"\n'
	tex += '\\begin{longtabu} to \\textwidth {|X[,L]|r|X[,L]|}\n'
	tex += '\\hline\n'
	tex += '%s {\\scriptsize (%s)} & %s & %s\\\\\n' % (_('Substance'), _('Drug Product'), _('Strength'), _('Aim'))
	tex += '\\hline\n'
	tex += '%s\n'			# this is where the lines end up
	tex += '\\end{longtabu}\n'

	current_meds = emr.get_current_medications (
		include_inactive = False,
		include_unapproved = False,
		order_by = 'product, substance'
	)
	# create lines
	lines = []
	for med in current_meds:
		if med['aim'] is None:
			aim = ''
		else:
			aim = '{\\scriptsize %s}' % gmTools.tex_escape_string(med['aim'])
		lines.append('%s {\\small (%s: {\\tiny %s})} & %s%s & %s\\\\' % (
			gmTools.tex_escape_string(med['substance']),
			gmTools.tex_escape_string(med['l10n_preparation']),
			gmTools.tex_escape_string(med['product']),
			med['amount'],
			gmTools.tex_escape_string(med.formatted_units),
			aim
		))
		lines.append(u'\\hline')

	return tex % '\n'.join(lines)

#------------------------------------------------------------
def format_substance_intake(emr=None, output_format='latex', table_type='by-product'):

	# FIXME: add intake_instructions

	tex = '%s {\\tiny (%s)}\n' % (
		gmTools.tex_escape_string(_('Medication list')),
		gmTools.tex_escape_string(_('ordered by brand'))
	)
	tex += '%% requires "\\usepackage{longtable}"\n'
	tex += '%% requires "\\usepackage{tabu}"\n'
	tex += u'\\begin{longtabu} to \\textwidth {|X[-1,L]|X[2.5,L]|}\n'
	tex += u'\\hline\n'
	tex += u'%s & %s\\\\\n' % (
		gmTools.tex_escape_string(_('Drug')),
		gmTools.tex_escape_string(_('Regimen / Advice'))
	)
	tex += '\\hline\n'
	tex += '%s\n'
	tex += '\\end{longtabu}\n'

	# aggregate medication data
	current_meds = emr.get_current_medications (
		include_inactive = False,
		include_unapproved = False,
		order_by = 'product, substance'
	)
	line_data = {}
	for med in current_meds:
		identifier = med['product']

		try:
			line_data[identifier]
		except KeyError:
			line_data[identifier] = {'product': '', 'l10n_preparation': '', 'schedule': '', 'notes': [], 'strengths': []}

		line_data[identifier]['product'] = identifier
		line_data[identifier]['strengths'].append('%s %s%s' % (med['substance'][:20], med['amount'], med.formatted_units))
		if med['l10n_preparation'] not in identifier:
			line_data[identifier]['l10n_preparation'] = med['l10n_preparation']
		sched_parts = []
		if med['duration'] is not None:
			sched_parts.append(gmDateTime.format_interval(med['duration'], gmDateTime.acc_days, verbose = True))
		if med['schedule'] is not None:
			sched_parts.append(med['schedule'])
		line_data[identifier]['schedule'] = ': '.join(sched_parts)
		if med['notes'] is not None:
			if med['notes'] not in line_data[identifier]['notes']:
				line_data[identifier]['notes'].append(med['notes'])
	# format aggregated data
	already_seen = []
	lines = []
	#line1_template = u'\\rule{0pt}{3ex}{\\Large %s} %s & %s \\\\'
	line1_template = u'{\\Large %s} %s & %s\\\\'
	line2_template = u'{\\tiny %s}                     & {\\scriptsize %s}\\\\'
	line3_template = u'                                & {\\scriptsize %s}\\\\'
	for med in current_meds:
		identifier = med['product']
		if identifier in already_seen:
			continue
		already_seen.append(identifier)
		lines.append (line1_template % (
			gmTools.tex_escape_string(line_data[identifier]['product']),
			gmTools.tex_escape_string(line_data[identifier]['l10n_preparation']),
			gmTools.tex_escape_string(line_data[identifier]['schedule'])
		))
		strengths = gmTools.tex_escape_string(' / '.join(line_data[identifier]['strengths']))
		if len(line_data[identifier]['notes']) == 0:
			first_note = ''
		else:
			first_note = gmTools.tex_escape_string(line_data[identifier]['notes'][0])
		lines.append(line2_template % (strengths, first_note))
		if len(line_data[identifier]['notes']) > 1:
			for note in line_data[identifier]['notes'][1:]:
				lines.append(line3_template % gmTools.tex_escape_string(note))
		lines.append('\\hline')

	return tex % '\n'.join(lines)

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
	nicotine = create_substance_dose_by_atc (
		substance = _('nicotine'),
		atc = gmATC.ATC_NICOTINE,
		amount = 1,
		unit = 'pack',
		dose_unit = 'year'
	)
	tobacco = create_drug_product (
		product_name = _('nicotine'),
		preparation = _('tobacco'),
		doses = [nicotine],
		return_existing = True
	)
	tobacco['is_fake_product'] = True
	tobacco.save()
	return tobacco

#------------------------------------------------------------
def get_alcohol():
	ethanol = create_substance_dose_by_atc (
		substance = _('ethanol'),
		atc = gmATC.ATC_ETHANOL,
		amount = 1,
		unit = 'g',
		dose_unit = 'ml'
	)
	drink = create_drug_product (
		product_name = _('alcohol'),
		preparation = _('liquid'),
		doses = [ethanol],
		return_existing = True
	)
	drink['is_fake_product'] = True
	drink.save()
	return drink

#------------------------------------------------------------
def get_other_drug(name=None, pk_dose=None):
	if pk_dose is None:
		content = create_substance_dose (
			substance = name,
			amount = 1,
			unit = _('unit'),
			dose_unit = _('unit')
		)
	else:
		content = {'pk_dose': pk_dose}		#cSubstanceDose(aPK_obj = pk_dose)
	drug = create_drug_product (
		product_name = name,
		preparation = _('unit'),
		doses = [content],
		return_existing = True
	)
	drug['is_fake_product'] = True
	drug.save()
	return drug

#------------------------------------------------------------
def format_units(unit, dose_unit, preparation=None, short=True):
	if short:
		return '%s%s' % (unit, gmTools.coalesce(dose_unit, '', '/%s'))

	return '%s / %s' % (
		unit,
		gmTools.coalesce (
			dose_unit,
			_('delivery unit%s') % gmTools.coalesce(preparation, '', ' (%s)'),
			'%s'
		)
	)

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
		print(drug)

	#--------------------------------------------------------
	def test_get_substances():
		for s in get_substances():
			##print s
			print("--------------------------")
			print(s.format())
			print('in use:', s.is_in_use_by_patients)
			print('is component:', s.is_drug_component)

#		s = cSubstance(1)
#		print s
#		print s['loincs']
#		print s.format()
#		print 'in use:', s.is_in_use_by_patients
#		print 'is component:', s.is_drug_component

	#--------------------------------------------------------
	def test_get_doses():
		for d in get_substance_doses():
			#print d
			print("--------------------------")
			print(d.format(left_margin = 1, include_loincs = True))
			print('in use:', d.is_in_use_by_patients)
			print('is component:', d.is_drug_component)

	#--------------------------------------------------------
	def test_get_components():
		for c in get_drug_components():
			#print c
			print('--------------------------------------')
			print(c.format())
			print('dose:', c.substance_dose.format())
			print('substance:', c.substance.format())

	#--------------------------------------------------------
	def test_get_drugs():
		for d in get_drug_products():
			if d['is_fake_product'] or d.is_vaccine:
				continue
			print('--------------------------------------')
			print(d.format())
			for c in d.components:
				print('-------')
				print(c.format())
				print(c.substance_dose.format())
				print(c.substance.format())

	#--------------------------------------------------------
	def test_get_intakes():
		for i in get_substance_intakes():
			#print i
			print('------------------------------------------------')
			print('\n'.join(i.format_maximum_information()))

	#--------------------------------------------------------
	def test_get_habit_drugs():
		print(get_tobacco().format())
		print(get_alcohol().format())
		print(get_other_drug(name = 'LSD').format())

	#--------------------------------------------------------
	def test_drug2renal_insufficiency_url():
		drug2renal_insufficiency_url(search_term = 'Metoprolol')
	#--------------------------------------------------------
	def test_medically_formatted_start_end():
		cmd = "SELECT pk_substance_intake FROM clin.v_substance_intakes"
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd}])
		for row in rows:
			entry = cSubstanceIntakeEntry(row['pk_substance_intake'])
			print('===============================================================')
			print(entry.format(left_margin = 1, single_line = False, show_all_product_components = True))
			print('--------------------------------')
			print(entry.medically_formatted_start_end)
			gmTools.prompted_input()

	#--------------------------------------------------------
	def test_generate_amts_data_template_definition_file(work_dir=None, strict=True):
		print('file:', generate_amts_data_template_definition_file(strict = True))

	#--------------------------------------------------------
	def test_format_substance_intake_as_amts_data():
		#print format_substance_intake_as_amts_data(cSubstanceIntakeEntry(1))
		print(cSubstanceIntakeEntry(1).as_amts_data)

	#--------------------------------------------------------
	def test_delete_intake():
		delete_substance_intake(pk_intake = 1, delete_siblings = True)

	#--------------------------------------------------------
	# generic
	#test_drug2renal_insufficiency_url()
	#test_interaction_check()
	#test_medically_formatted_start_end()

	#test_get_substances()
	#test_get_doses()
	#test_get_components()
	#test_get_drugs()
	#test_get_intakes()
	#test_create_substance_intake()
	test_delete_intake()

	#test_get_habit_drugs()

	# AMTS
	#test_generate_amts_data_template_definition_file()
	#test_format_substance_intake_as_amts_data()
