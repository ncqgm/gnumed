# -*- coding: utf-8 -*-
"""Medication handling code.

license: GPL v2 or later


intake regimen:

	beim Aufstehen / Frühstück / Mittag / abends / zum Schlafengehen

	"19 Uhr"

	"Mittwochs"			(Alendronsäure)

	"1x/Monat"			(Alendronsäure)

	"Mo Di Mi Do Fr Sa So" (Falithrom)

	"Tag 1: 4, Tag 2: 3, Tag 3: 2, Tag 4: 1"	(Prednisonstoß)

	"1T:4, 1T:3, 2T:2, 3T:1, 4T:1/2"			(Prednisonstoß)

	"bei Bedarf"
"""
#============================================================
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"

import sys
import logging
import uuid
import re as regex
import datetime as pydt


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
from Gnumed.pycommon import gmBusinessDBObject
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmPG2
from Gnumed.pycommon import gmDispatcher
from Gnumed.pycommon import gmMatchProvider
from Gnumed.pycommon import gmHooks
from Gnumed.pycommon import gmDateTime

from Gnumed.business import gmATC
from Gnumed.business import gmAllergy
from Gnumed.business import gmEpisode


_log = logging.getLogger('gm.meds')

#============================================================
DEFAULT_MEDICATION_HISTORY_EPISODE = _('Medication history')

URL_long_qt = 'https://www.crediblemeds.org'

# http://www.akdae.de/Arzneimittelsicherheit/UAW-Meldung/UAW-Meldung-online.html
# https://dcgma.org/uaw/meldung.php
URL_drug_ADR_german_default = 'https://nebenwirkungen.pei.de'


(
	USE_TYPE_MEDICATION,
	USE_TYPE_NON_HARMFUL,
	USE_TYPE_PRESENTLY_HARMFUL,
	USE_TYPE_PRESENTLY_ADDICTED,
	USE_TYPE_PREVIOUSLY_ADDICTED
) = (
	None, 0, 1, 2, 3
)

USE_TYPES_ACTIVE_MISUSE:list[int] = [
	USE_TYPE_PRESENTLY_HARMFUL,
	USE_TYPE_PRESENTLY_ADDICTED
]


USE_TYPE_NAMES = {
	USE_TYPE_MEDICATION: _('medication, not abuse'),
	USE_TYPE_NON_HARMFUL: _('non-use or non-harmful use'),
	USE_TYPE_PRESENTLY_HARMFUL: _('presently harmful use'),
	USE_TYPE_PRESENTLY_ADDICTED: _('presently addicted'),
	USE_TYPE_PREVIOUSLY_ADDICTED: _('previously addicted')
}

#============================================================
def _on_substance_intake_modified():
	"""Always relates to the active patient."""
	gmHooks.run_hook_script(hook = 'after_substance_intake_modified')

gmDispatcher.connect(_on_substance_intake_modified, 'clin.intake_mod_db')

#============================================================
URL_lungs = 'https://www.pneumotox.com'
URL_lungs__search_template = 'https://duckduckgo.com?q=site:pneumotox.com+%s'

def generate_pulmonary_information_urls(search_term:str=None) -> list:
	if search_term is None:
		return [URL_lungs]

	if isinstance(search_term, str):
		if search_term.strip() == '':
			return [URL_lungs]

	atcs = []
	names = []

	if isinstance(search_term, cSubstance):
		names.append(search_term['substance'])
		if search_term['atc']:
			atcs.append(search_term['atc'])
	elif isinstance(search_term, cSubstanceDose):
		names.append(search_term['substance'])
		if search_term['atc_substance']:
			atcs.append(search_term['atc_substance'])
	elif isinstance(search_term, cSubstanceIntakeEntry):
		names.append(search_term['substance'])
		if search_term['atc_substance']:
			atcs.append(search_term['atc_substance'])
	elif isinstance(search_term, cIntakeWithRegimen):
		names.append(search_term['substance'])
		if search_term['atc_substance']:
			atcs.append(search_term['atc_substance'])
	elif isinstance(search_term, cIntakeRegimen):
		names.append(search_term['substance'])
		if search_term['atc_substance']:
			atcs.append(search_term['atc_substance'])
	else:
		names.append('%s' % search_term)
		atcs.extend(gmATC.text2atc(text = '%s' % search_term, fuzzy = True))
	terms = []
	for name in names:
		terms.append(name)
		if name.endswith('e'):
			terms.append(name[:-1])
	terms.extend(atcs)
	urls = [ URL_lungs__search_template % t for t in terms ]
	_log.debug('pulmonary information URLs: %s', urls)
	return urls

#------------------------------------------------------------
URL_pregnancy = 'https:://embryotox.de'
URL_pregnancy__search_template = 'https://duckduckgo.com?q=site:embryotox.de+%s'

def generate_pregnancy_information_urls(search_term:str=None) -> list:
	if search_term is None:
		return [URL_pregnancy]

	if isinstance(search_term, str):
		if search_term.strip() == '':
			return [URL_pregnancy]

	atcs = []
	names = []
	if isinstance(search_term, cSubstance):
		names.append(search_term['substance'])
		if search_term['atc']:
			atcs.append(search_term['atc'])
	elif isinstance(search_term, cSubstanceDose):
		names.append(search_term['substance'])
		if search_term['atc_substance']:
			atcs.append(search_term['atc_substance'])
	elif isinstance(search_term, cSubstanceIntakeEntry):
		names.append(search_term['substance'])
		if search_term['atc_substance']:
			atcs.append(search_term['atc_substance'])
	elif isinstance(search_term, cIntakeWithRegimen):
		names.append(search_term['substance'])
		if search_term['atc_substance']:
			atcs.append(search_term['atc_substance'])
	elif isinstance(search_term, cIntakeRegimen):
		names.append(search_term['substance'])
		if search_term['atc_substance']:
			atcs.append(search_term['atc_substance'])
	else:
		names.append('%s' % search_term)
		atcs.extend(gmATC.text2atc(text = '%s' % search_term, fuzzy = True))
	terms = []
	for name in names:
		terms.append(name)
		if name.endswith('e'):
			terms.append(name[:-1])
	terms.extend(atcs)
	urls = [ URL_pregnancy__search_template % t for t in terms ]
	_log.debug('pregnancy information URLs: %s', urls)
	return urls

#------------------------------------------------------------
URL_renal_insufficiency = 'https://www.dosing.de/nierebck.php'
#URL_renal_insufficiency_search_template = 'https://www.google.com/search?q=site:dosing.de+%s'
URL_renal_insufficiency__search_template = 'https://duckduckgo.com?q=site:dosing.de+%s'

def generate_renal_insufficiency_urls(search_term:str=None) -> list:

	if search_term is None:
		return [URL_renal_insufficiency]

	if isinstance(search_term, str):
		if search_term.strip() == '':
			return [URL_renal_insufficiency]

	atcs = []
	names = []
	if isinstance(search_term, cSubstance):
		names.append(search_term['substance'])
		if search_term['atc']:
			atcs.append(search_term['atc'])
	elif isinstance(search_term, cSubstanceDose):
		names.append(search_term['substance'])
		if search_term['atc_substance']:
			atcs.append(search_term['atc_substance'])
	elif isinstance(search_term, cSubstanceIntakeEntry):
		names.append(search_term['substance'])
		if search_term['atc_substance']:
			atcs.append(search_term['atc_substance'])
	elif isinstance(search_term, cIntakeWithRegimen):
		names.append(search_term['substance'])
		if search_term['atc_substance']:
			atcs.append(search_term['atc_substance'])
	elif isinstance(search_term, cIntakeRegimen):
		names.append(search_term['substance'])
		if search_term['atc_substance']:
			atcs.append(search_term['atc_substance'])
	else:
		names.append('%s' % search_term)
		atcs.extend(gmATC.text2atc(text = '%s' % search_term, fuzzy = True))
	terms = []
	for name in names:
		terms.append(name)
		if name.endswith('e'):
			terms.append(name[:-1])
	terms.extend(atcs)
	urls = [ URL_renal_insufficiency__search_template % t for t in terms ]
	_log.debug('renal insufficiency URLs: %s', urls)
	return urls

#------------------------------------------------------------
URL_liver = 'https://www.ncbi.nlm.nih.gov/books/NBK547852/'
#URL_liver__search_template = 'https://www.ncbi.nlm.nih.gov/books/n/livertox/%s/'
URL_liver__search_template = 'https://duckduckgo.com?q=site:nih.gov+livertox+%s'

def generate_liver_information_urls(search_term:str=None) -> list[str]:
	if search_term is None:
		return [URL_liver]

	if isinstance(search_term, str):
		if search_term.strip() == '':
			return [URL_liver]

	names = []
	if isinstance(search_term, cSubstance):
		names.append(search_term['substance'])
	elif isinstance(search_term, cSubstanceDose):
		names.append(search_term['substance'])
	elif isinstance(search_term, cSubstanceIntakeEntry):
		names.append(search_term['substance'])
	elif isinstance(search_term, cIntakeWithRegimen):
		names.append(search_term['substance'])
	elif isinstance(search_term, cIntakeRegimen):
		names.append(search_term['substance'])
	else:
		names.append('%s' % search_term)
	terms = []
	for name in names:
		terms.append(name)
		if name.endswith('e'):
			terms.append(name[:-1])
	urls = [ URL_liver__search_template % t for t in terms ]
	_log.debug('liver information URLs: %s', urls)
	return urls

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
		if len(self._payload['loincs']) == 0:
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
					) for l in self._payload['loincs'] 
				])
			)
		return (' ' * left_margin) + '%s: %s%s%s%s' % (
			_('Substance'),
			self._payload['substance'],
			gmTools.coalesce(self._payload['atc'], '', ' [%s]'),
			gmTools.coalesce(self._payload['intake_instructions'], '', _('\n Instructions: %s')),
			loincs
		)

	#--------------------------------------------------------
	def save_payload(self, conn=None):
		success, data = super().save_payload(conn = conn)
		if not success:
			return (success, data)

		if self._payload['atc'] is not None:
			atc = self._payload['atc'].strip()
			if atc != '':
				gmATC.propagate_atc (
					substance = self._payload['substance'].strip(),
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
	def get_regimens(self, pk_patient:int=None, ongoing_only:bool=False, order_by:str=None) -> list:
		assert pk_patient is not None, '<pk_patient> must be given'
		return get_intake_regimens (
			order_by = order_by,
			pk_patient = pk_patient,
			ongoing_only = ongoing_only
		)

	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def _set_loincs(self, loincs):
		args = {'pk_subst': self.pk_obj, 'loincs': loincs}
		# insert new entries
		for loinc in loincs:
			cmd = """INSERT INTO ref.lnk_loinc2substance (fk_substance, loinc)
			SELECT
				%(pk_subst)s, %(loinc)s
			WHERE NOT EXISTS (
				SELECT 1 from ref.lnk_loinc2substance WHERE fk_substance = %(pk_subst)s AND loinc = %(loinc)s
			)"""
			args['loinc'] = loinc
			gmPG2.run_rw_queries(queries = [{'sql': cmd, 'args': args}])

		# delete old entries
		cmd = 'DELETE FROM ref.lnk_loinc2substance WHERE fk_substance = %(pk_subst)s AND loinc <> ALL(%(loincs)s)'
		gmPG2.run_rw_queries(queries = [{'sql': cmd, 'args': args}])

	loincs = property(lambda x:x, _set_loincs)

	#--------------------------------------------------------
	def _get_is_in_use_by_patients(self):
		cmd = """
			SELECT EXISTS (
				SELECT 1
				FROM clin.v_intakes
				WHERE pk_substance = %(pk)s
				LIMIT 1
			)"""
		args = {'pk': self.pk_obj}

		rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
		return rows[0][0]

	is_in_use_by_patients = property(_get_is_in_use_by_patients)

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

		rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
		return rows[0][0]

	is_drug_component = property(_get_is_drug_component)

#------------------------------------------------------------
def get_substances(order_by:str='', return_pks:bool=False, substance:str=None) -> list[cSubstance] | list[int]:
	args = {}
	where_parts = []
	if substance:
		args['substance'] = substance.strip()
		where_parts.append('substance = %(substance)s')
	if where_parts:
		WHERE = '\nAND '.join(where_parts)
	else:
		WHERE = 'true'
	if order_by:
		order_by = ' ORDER BY %s' % order_by
	SQL = _SQL_get_substance % WHERE
	SQL += order_by
	rows = gmPG2.run_ro_queries(queries = [{'sql': SQL, 'args': args}])
	if return_pks:
		return [ r['pk_substance'] for r in rows ]

	return [ cSubstance(row = {'data': r, 'pk_field': 'pk_substance'}) for r in rows ]

#------------------------------------------------------------
def create_substance(substance=None, atc=None, link_obj=None):
	if atc:
		atc = atc.strip()
	args = {
		'desc': substance.strip(),
		'atc': atc
	}
	cmd = "SELECT pk FROM ref.substance WHERE lower(description) = lower(%(desc)s)"
	rows = gmPG2.run_ro_queries(link_obj = link_obj, queries = [{'sql': cmd, 'args': args}])
	if len(rows) == 0:
		cmd = """
			INSERT INTO ref.substance (description, atc) VALUES (
				%(desc)s,
				coalesce (
					gm.nullify_empty_string(%(atc)s),
					(SELECT code FROM ref.atc WHERE term = %(desc)s LIMIT 1)
				)
			) RETURNING pk"""
		rows = gmPG2.run_rw_queries(queries = [{'sql': cmd, 'args': args}], return_data = True, link_obj = link_obj)
	if atc:
		gmATC.propagate_atc(link_obj = link_obj, substance = substance.strip(), atc = atc)
	return cSubstance(aPK_obj = rows[0]['pk'], link_obj = link_obj)

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
	queries.append({'sql': cmd, 'args': args})
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
	queries.append({'sql': cmd, 'args': args})
	rows = gmPG2.run_rw_queries(link_obj = link_obj, queries = queries, return_data = True)
	if len(rows) == 0:
		cmd = "SELECT pk FROM ref.substance WHERE atc = %(atc)s LIMIT 1"
		rows = gmPG2.run_ro_queries(link_obj = link_obj, queries = [{'sql': cmd, 'args': args}])

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
				SELECT 1 FROM clin.v_intakes
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
	gmPG2.run_rw_queries(queries = [{'sql': cmd, 'args': args}])
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
		if include_loincs and (len(self._payload['loincs']) > 0):
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
					) for l in self._payload['loincs'] 
				])
			)
		return (' ' * left_margin) + '%s: %s %s%s%s%s%s' % (
			_('Substance dose'),
			self._payload['substance'],
			self._payload['amount'],
			self.formatted_units,
			gmTools.coalesce(self._payload['atc_substance'], '', ' [%s]'),
			gmTools.coalesce(self._payload['intake_instructions'], '', '\n' + (' ' * left_margin) + ' ' + _('Instructions: %s')),
			loincs
		)

	#--------------------------------------------------------
	def exists_as_intake(self, pk_patient=None):
		return substance_intake_exists (
			pk_substance = -1,				# FIXME
			pk_identity = pk_patient
		)

	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def _get_is_in_use_by_patients(self):
		cmd = """
			SELECT EXISTS (
				SELECT 1
				FROM clin.v_intakes
				WHERE pk_dose = %(pk)s
				LIMIT 1
			)"""
		args = {'pk': self.pk_obj}

		rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
		return rows[0][0]

	is_in_use_by_patients = property(_get_is_in_use_by_patients)

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
		rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
		return rows[0][0]

	is_drug_component = property(_get_is_drug_component)

	#--------------------------------------------------------
	def _get_formatted_units(self, short=True):
		return format_units (
			self._payload['unit'],
			gmTools.coalesce(self._payload['dose_unit'], _('delivery unit')),
			short = short,
			none_str = ''
		)

	formatted_units = property(_get_formatted_units)

	#--------------------------------------------------------
	def _get_as_substance(self):
		return cSubstance(aPK_obj = self._payload['pk_substance'])

	as_substance = property(_get_as_substance)

#------------------------------------------------------------
def get_substance_doses(order_by=None, return_pks=False):
	if order_by is None:
		order_by = 'true'
	else:
		order_by = 'true ORDER BY %s' % order_by
	cmd = _SQL_get_substance_dose % order_by
	rows = gmPG2.run_ro_queries(queries = [{'sql': cmd}])
	if return_pks:
		return [ r['pk_dose'] for r in rows ]
	return [ cSubstanceDose(row = {'data': r, 'pk_field': 'pk_dose'}) for r in rows ]

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
	rows = gmPG2.run_ro_queries(link_obj = link_obj, queries = [{'sql': cmd, 'args': args}])

	if len(rows) == 0:
		cmd = """
			INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit) VALUES (
				%(pk_subst)s,
				%(amount)s,
				gm.nullify_empty_string(%(unit)s),
				gm.nullify_empty_string(%(dose_unit)s)
			) RETURNING pk"""
		rows = gmPG2.run_rw_queries(link_obj = link_obj, queries = [{'sql': cmd, 'args': args}], return_data = True)

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
				SELECT 1 FROM clin.v_intakes
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
	gmPG2.run_rw_queries(queries = [{'sql': cmd, 'args': args}])
	return True

#------------------------------------------------------------
class cSubstanceDoseMatchProvider(gmMatchProvider.cMatchProvider_SQL2):

	_pattern = regex.compile(r'^\D+\s*\d+$', regex.UNICODE)	# match candidates are subjected to .strip()

	# the "substance query" is run when the search fragment
	# does NOT match the regex ._pattern (which is: "chars SPACE digits")
	# IOW, when a name-only fragment has been entered
	_substance_query = """-- substance dose match provider: search by substance only
		SELECT
			ARRAY[comb.pk_substance, comb.pk_dose]::INTEGER[]
				AS data,
			comb.substance -- || coalesce(' (' || comb.amount || ' ' || comb.unit || coalesce(' / ' || comb.dose_unit, '') || ')', '')
				AS field_label,
			comb.substance || coalesce(' ' || comb.amount || ' ' || comb.unit || coalesce(' / ' || comb.dose_unit, ''), '')
				AS list_label
		FROM ((
			SELECT		-- plain substances w/o any doses available
				pk AS pk_substance,
				NULL AS pk_dose,
				description AS substance,
				NULL AS amount,
				NULL AS unit,
				NULL AS dose_unit
			FROM
				ref.substance
		) UNION ALL (
			SELECT		-- substance doses
				pk_substance,
				pk_dose,
				substance,
				amount,
				unit,
				dose_unit
			FROM
				ref.v_substance_doses
		)) AS comb
		WHERE
			%(fragment_condition)s
		ORDER BY
			list_label
		LIMIT 50"""
	# the "dose query" is run when the search fragment
	# DOES match the regex ._pattern (which is: "chars SPACE digits")
	# which may make it a substance dose
	_dose_query = """-- substance dose match provider: search by substance and strength
		SELECT
			ARRAY[r_vsd.pk_substance, r_vsd.pk_dose]::INTEGER[]
				AS data,
			r_vsd.substance -- || ' (' || r_vsd.amount || ' ' || r_vsd.unit || coalesce(' / ' || r_vsd.dose_unit, '') || ')'
				AS field_label,
			r_vsd.substance || ' ' || r_vsd.amount || ' ' || r_vsd.unit || coalesce(' / ' || r_vsd.dose_unit, '')
				AS list_label
		FROM
			ref.v_substance_doses r_vsd
		WHERE
			%(fragment_condition)s
		ORDER BY
			list_label
		LIMIT 50"""

	#--------------------------------------------------------
	def __init__(self, queries = None, context = None):
		super().__init__()
		#self._SQL_data2match = cSubstanceDoseMatchProvider._dose_query % {'fragment_condition': 'pk_dose = %(pk)s'}

	#--------------------------------------------------------
	def getMatchesByPhrase(self, search_term):
		"""Return matches for search_term at start of phrases."""
		if cSubstanceDoseMatchProvider._pattern.match(search_term):
			self._queries = [cSubstanceDoseMatchProvider._dose_query]
			search_condition = """r_vsd.substance ILIKE %(subst)s
				AND
			r_vsd.amount::text ILIKE %(amount)s"""
			self._args['subst'] = '%s%%' % regex.sub(r'\s*\d+$', '', search_term)
			self._args['amount'] = '%s%%' % regex.sub(r'^\D+\s*', '', search_term)
		else:
			self._queries = [cSubstanceDoseMatchProvider._substance_query]
			search_condition = "comb.substance ILIKE %(fragment)s"
			self._args['fragment'] = "%s%%" % search_term
		return self._find_matches(search_condition)

	#--------------------------------------------------------
	def getMatchesByWord(self, search_term):
		"""Return matches for search_term at start of words inside phrases."""
		if cSubstanceDoseMatchProvider._pattern.match(search_term):
			self._queries = [cSubstanceDoseMatchProvider._dose_query]
			subst = regex.sub(r'\s*\d+$', '', search_term)
			subst = gmPG2.sanitize_pg_regex(expression = subst, escape_all = False)
			search_condition = """r_vsd.substance ~* %(subst)s
				AND
			r_vsd.amount::text ILIKE %(amount)s"""
			self._args['subst'] = '\m%s' % subst
			self._args['amount'] = '%s%%' % regex.sub(r'^\D+\s*', '', search_term)
		else:
			self._queries = [cSubstanceDoseMatchProvider._substance_query]
			search_condition = "comb.substance ~* %(fragment)s"
			search_term = gmPG2.sanitize_pg_regex(expression = search_term, escape_all = False)
			self._args['fragment'] = r'\m%s' % search_term
		return self._find_matches(search_condition)

	#--------------------------------------------------------
	def getMatchesBySubstr(self, search_term):
		"""Return matches for search_term as a true substring."""
		if cSubstanceDoseMatchProvider._pattern.match(search_term):
			self._queries = [cSubstanceDoseMatchProvider._dose_query]
			search_condition = """substance ILIKE %(subst)s
				AND
			amount::text ILIKE %(amount)s"""
			self._args['subst'] = '%%%s%%' % regex.sub(r'\s*\d+$', '', search_term)
			self._args['amount'] = '%s%%' % regex.sub(r'^\D+\s*', '', search_term)
		else:
			self._queries = [cSubstanceDoseMatchProvider._substance_query]
			search_condition = "comb.substance ILIKE %(fragment)s"
			self._args['fragment'] = "%%%s%%" % search_term
		return self._find_matches(search_condition)

#------------------------------------------------------------
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
				FROM clin.v_intakes
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
			self._payload['substance'],
			self._payload['amount'],
			self.formatted_units
		))
		lines.append(_('Component of %s (%s)') % (
			self._payload['drug_product'],
			self._payload['l10n_preparation']
		))
		if self._payload['is_fake_product']:
			lines.append(' ' + _('(not a real drug product)'))

		if self._payload['intake_instructions'] is not None:
			lines.append(_('Instructions: %s') % self._payload['intake_instructions'])
		if self._payload['atc_substance'] is not None:
			lines.append(_('ATC (substance): %s') % self._payload['atc_substance'])
		if self._payload['atc_drug'] is not None:
			lines.append(_('ATC (drug): %s') % self._payload['atc_drug'])
		if self._payload['external_code'] is not None:
			lines.append('%s: %s' % (
				self._payload['external_code_type'],
				self._payload['external_code']
			))

		if include_loincs:
			if len(self._payload['loincs']) > 0:
				lines.append(_('LOINCs to monitor:'))
			lines.extend ([
				' %s%s%s' % (
					loinc['loinc'],
					gmTools.coalesce(loinc['max_age_str'], '', ': ' + _('once within %s')),
					gmTools.coalesce(loinc['comment'], '', ' (%s)')
				) for loinc in self._payload['loincs']
			])

		return (' ' * left_margin) + ('\n' + (' ' * left_margin)).join(lines)

	#--------------------------------------------------------
	def exists_as_intake(self, pk_patient=None):
		return substance_intake_exists (
			pk_substance = -1,				# FIXME
			pk_identity = pk_patient
		)

	#--------------------------------------------------------
	def turn_into_intake(self, emr=None, encounter=None, episode=None):
		return create_substance_intake (
			pk_substance = -1,				# FIXME
			pk_encounter = encounter,
			pk_episode = episode
		)

	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def _get_containing_drug(self):
		return cDrugProduct(aPK_obj = self._payload['pk_drug_product'])

	containing_drug = property(_get_containing_drug)

	#--------------------------------------------------------
	def _get_is_in_use_by_patients(self):
		return self._payload['is_in_use']

	is_in_use_by_patients = property(_get_is_in_use_by_patients)

	#--------------------------------------------------------
	def _get_substance_dose(self):
		return cSubstanceDose(aPK_obj = self._payload['pk_dose'])

	substance_dose =  property(_get_substance_dose)

	#--------------------------------------------------------
	def _get_substance(self):
		return cSubstance(aPK_obj = self._payload['pk_substance'])

	substance =  property(_get_substance)

	#--------------------------------------------------------
	def _get_formatted_units(self, short=True):
		return format_units (
			self._payload['unit'],
			gmTools.coalesce(self._payload['dose_unit'], _('delivery unit')),
			self._payload['l10n_preparation'],
			short = short,
			none_str = ''
		)

	formatted_units = property(_get_formatted_units)

#------------------------------------------------------------
def get_drug_components(return_pks=False):
	cmd = _SQL_get_drug_components % 'true ORDER BY product, substance'
	rows = gmPG2.run_ro_queries(queries = [{'sql': cmd}])
	if return_pks:
		return [ r['pk_component'] for r in rows ]
	return [ cDrugComponent(row = {'data': r, 'pk_field': 'pk_component'}) for r in rows ]

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
			self._payload['drug_product'],
			self._payload['l10n_preparation']
			)
		)
		if self._payload['atc'] is not None:
			lines.append('ATC: %s' % self._payload['atc'])
		if self._payload['external_code'] is not None:
			lines.append('%s: %s' % (self._payload['external_code_type'], self._payload['external_code']))
		if len(self._payload['components']) > 0:
			lines.append(_('Components:'))
			for comp in self._payload['components']:
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

		if self._payload['is_fake_product']:
			lines.append('')
			lines.append(_('this is a fake drug product'))
		if self.is_vaccine:
			lines.append(_('this is a vaccine'))

		return (' ' * left_margin) + ('\n' + (' ' * left_margin)).join(lines)

	#--------------------------------------------------------
	def save_payload(self, conn=None):
		success, data = super().save_payload(conn = conn)

		if not success:
			return (success, data)

		if self._payload['atc'] is not None:
			atc = self._payload['atc'].strip()
			if atc != '':
				gmATC.propagate_atc (
					link_obj = conn,
					substance = self._payload['product'].strip(),
					atc = atc
				)
		return (success, data)

	#--------------------------------------------------------
	def set_substance_doses_as_components(self, substance_doses:list=None, pk_substance_doses:list[int]=None, link_obj=None):
		if self.is_in_use:
			return False

		if pk_substance_doses:
			pk_doses2keep = pk_substance_doses
		else:
			pk_doses2keep = [ s['pk_dose'] for s in substance_doses ]
		_log.debug('setting components of "%s" from doses: %s', self._payload['product'], pk_doses2keep)
		args = {'pk_drug_product': self._payload['pk_drug_product']}
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
			queries.append({'sql': cmd, 'args': args.copy()})

		# DELETE those that don't belong anymore
		args['doses2keep'] = pk_doses2keep
		cmd = """
			DELETE FROM ref.lnk_dose2drug
			WHERE
				fk_drug_product = %(pk_drug_product)s
					AND
				fk_dose <> ALL(%(doses2keep)s)"""
		queries.append({'sql': cmd, 'args': args})
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
		gmPG2.run_rw_queries(queries = [{'sql': cmd, 'args': args}])
		self.refetch_payload()

	#------------------------------------------------------------
	def remove_component(self, pk_dose=None, pk_component=None):
		if len(self._payload['components']) == 1:
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
							SELECT 1 FROM clin.v_intakes
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

		gmPG2.run_rw_queries(queries = [{'sql': cmd, 'args': args}])
		self.refetch_payload()
		return True

	#--------------------------------------------------------
	def exists_as_intake(self, pk_patient=None):
		return substance_intake_exists (
			pk_substance = -1,			# FIXME
			pk_identity = pk_patient
		)

	#--------------------------------------------------------
	def turn_into_intake(self, emr=None, encounter=None, episode=None):
		return create_substance_intake (
			pk_substance = -1,			# FIXME
			pk_encounter = encounter,
			pk_episode = episode
		)

	#--------------------------------------------------------
	def delete_associated_vaccine(self):
		if self._payload['is_vaccine'] is False:
			return True

		args = {'pk_product': self._payload['pk_drug_product']}
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
		rows = gmPG2.run_rw_queries(queries = [{'sql': cmd, 'args': args}], return_data = True)
		if len(rows) == 0:
			_log.debug('cannot delete vaccine on: %s', self)
			return False
		return True

	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def _get_external_code(self):
		return self._payload['external_code']

	external_code = property(_get_external_code)

	#--------------------------------------------------------
	def _get_external_code_type(self):
		# FIXME: maybe evaluate fk_data_source ?
		return self._payload['external_code_type']

	external_code_type = property(_get_external_code_type)

	#--------------------------------------------------------
	def _get_components(self):
		SQL = _SQL_get_drug_components % 'pk_drug_product = %(pk_product)s'
		args = {'pk_product': self._payload['pk_drug_product']}
		rows = gmPG2.run_ro_queries(queries = [{'sql': SQL, 'args': args}])
		return [ cDrugComponent(row = {'data': r, 'pk_field': 'pk_component'}) for r in rows ]

	components = property(_get_components)

	#--------------------------------------------------------
	def _get_components_as_doses(self):
		pk_doses = [ c['pk_dose'] for c in self._payload['components'] ]
		if len(pk_doses) == 0:
			return []
		cmd = _SQL_get_substance_dose % 'pk_dose = ANY(%(pks)s)'
		args = {'pks': pk_doses}
		rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
		return [ cSubstanceDose(row = {'data': r, 'pk_field': 'pk_dose'}) for r in rows ]

	components_as_doses = property(_get_components_as_doses)

	#--------------------------------------------------------
	def _get_components_as_substances(self):
		pk_substances = [ c['pk_substance'] for c in self._payload['components'] ]
		if len(pk_substances) == 0:
			return []
		cmd = _SQL_get_substance % 'pk_substance = ANY(%(pks)s)'
		args = {'pks': pk_substances}
		rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
		return [ cSubstance(row = {'data': r, 'pk_field': 'pk_substance'}) for r in rows ]

	components_as_substances = property(_get_components_as_substances)

	#--------------------------------------------------------
	def _get_is_fake_product(self):
		return self._payload['is_fake_product']

	is_fake_product = property(_get_is_fake_product)

	#--------------------------------------------------------
	def _get_is_vaccine(self):
		return self._payload['is_vaccine']

	is_vaccine = property(_get_is_vaccine)

	#--------------------------------------------------------
	def _get_is_in_use(self):
		# as of v23 drug products are not linked to intakes
		return self.is_in_use_as_vaccine

	is_in_use = property(_get_is_in_use)

	#--------------------------------------------------------
	def _get_is_in_use_as_vaccine(self):
		if self._payload['is_vaccine'] is False:
			return False

		SQL = 'SELECT EXISTS(SELECT 1 FROM clin.vaccination WHERE fk_vaccine = (SELECT pk FROM ref.vaccine WHERE fk_drug_product = %(pk)s))'
		args = {'pk': self.pk_obj}
		rows = gmPG2.run_ro_queries(queries = [{'sql': SQL, 'args': args}])
		return rows[0][0]

	is_in_use_as_vaccine = property(_get_is_in_use_as_vaccine)

#------------------------------------------------------------
def get_drug_products(return_pks=False):
	cmd = _SQL_get_drug_product % 'TRUE ORDER BY product'
	rows = gmPG2.run_ro_queries(queries = [{'sql': cmd}])
	if return_pks:
		return [ r['pk_drug_product'] for r in rows ]
	return [ cDrugProduct(row = {'data': r, 'pk_field': 'pk_drug_product'}) for r in rows ]

#------------------------------------------------------------
def get_drug_by_name(product_name=None, preparation=None, link_obj=None):
	args = {'prod_name': product_name, 'prep': preparation}
	cmd = 'SELECT * FROM ref.v_drug_products WHERE lower(product) = lower(%(prod_name)s) AND lower(preparation) = lower(%(prep)s)'
	rows = gmPG2.run_ro_queries(link_obj = link_obj, queries = [{'sql': cmd, 'args': args}])
	if len(rows) == 0:
		return None
	return cDrugProduct(row = {'data': rows[0], 'pk_field': 'pk_drug_product'})

#------------------------------------------------------------
def get_drug_by_atc(atc=None, preparation=None, link_obj=None):
	args = {'atc': atc, 'prep': preparation}
	cmd = 'SELECT * FROM ref.v_drug_products WHERE lower(atc) = lower(%(atc)s) AND lower(preparation) = lower(%(prep)s)'
	rows = gmPG2.run_ro_queries(link_obj = link_obj, queries = [{'sql': cmd, 'args': args}])
	if len(rows) == 0:
		return None
	return cDrugProduct(row = {'data': rows[0], 'pk_field': 'pk_drug_product'}, link_obj = link_obj)

#------------------------------------------------------------
def create_drug_product(product_name=None, preparation=None, return_existing=False, link_obj=None, doses=None, pk_doses:list[int]=None):
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
		conn_commit = lambda *x: None
		conn_close = lambda *x: None
	cmd = 'INSERT INTO ref.drug_product (description, preparation) VALUES (%(prod_name)s, %(prep)s) RETURNING pk'
	args = {'prod_name': product_name, 'prep': preparation}
	rows = gmPG2.run_rw_queries(link_obj = link_obj, queries = [{'sql': cmd, 'args': args}], return_data = True)
	product = cDrugProduct(aPK_obj = rows[0]['pk'], link_obj = link_obj)
	if doses or pk_doses:
		product.set_substance_doses_as_components (
			link_obj = link_obj,
			substance_doses = doses,
			pk_substance_doses = pk_doses
		)
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
def delete_drug_product(pk_drug_product:int=None) -> bool:
	args = {'pk': pk_drug_product}
	SQL = 'SELECT EXISTS(SELECT 1 FROM clin.vaccination WHERE fk_vaccine = (SELECT pk FROM ref.vaccine WHERE fk_drug_product = %(pk)s))'
	args = {'pk': pk_drug_product}
	rows = gmPG2.run_ro_queries(queries = [{'sql': SQL, 'args': args}])
	if rows and rows[0][0]:
		_log.error('cannot delete drug product [%s], it is used as a vaccine')
		return False

	queries = []
	SQL = 'DELETE FROM ref.lnk_dose2drug WHERE fk_drug_product = %(pk)s'
	queries.append({'sql': SQL, 'args': args})
	SQL = 'DELETE FROM ref.drug_product WHERE pk = %(pk)s'
	queries.append({'sql': SQL, 'args': args})
	gmPG2.run_rw_queries(queries = queries)
	return True

#============================================================
# intakes, denormalized by regimen,
# therefore possibly with pseudo-regimen
#------------------------------------------------------------
_SQL_get_intake_with_regimen = 'SELECT * FROM clin.v_intakes_with_regimens WHERE %s'

class cIntakeWithRegimen(gmBusinessDBObject.cBusinessDBObject):
	"""A substance intake with regimen.

	There may be several concurrent ongoing
	regimens for any given substance intake.

	Intakes without any regimen will show
	empty regimen fields, IOW a pseudo-regimen.

	To be intialized with a dictionary like

		{
			'pk_intake': INT,
			'pk_intake_regimen': INT
		}

	where pk_intake_regimen can be None.
	"""
	_cmd_fetch_payload = _SQL_get_intake_with_regimen % 'pk_intake = %(pk_intake)s AND pk_intake_regimen IS NOT DISTINCT FROM %(pk_intake_regimen)s'
	_cmds_store_payload = [
		"""	-- cIntakeWithRegimen: clin.intake
			UPDATE clin.intake SET
				clin_when = %(last_checked_when)s,
				narrative = gm.nullify_empty_string(%(notes4provider)s),
				notes4patient = gm.nullify_empty_string(%(notes4patient)s),
				notes4us = gm.nullify_empty_string(%(notes4us)s),
				use_type = %(use_type)s,
				-- only update episode when there's no regimen
				fk_episode = CASE
					WHEN %(pk_intake_regimen)s IS DISTINCT FROM NULL THEN fk_episode
					ELSE %(pk_episode)s
				END
			WHERE
				pk = %(pk_intake)s
					AND
				xmin = %(xmin_intake)s
		""",
		""" -- cIntakeWithRegimen: clin.intake_regimen
			UPDATE clin.intake_regimen SET
				narrative = gm.nullify_empty_string(%(schedule)s),
				clin_when = %(started)s,
				start_is_unknown = %(start_is_unknown)s,
				comment_on_start = gm.nullify_empty_string(%(comment_on_start)s),
				discontinued = %(discontinued)s,
				discontinue_reason = gm.nullify_empty_string(%(discontinue_reason)s),
				planned_duration = %(planned_duration)s,
				fk_episode = %(pk_episode)s
				-- , fk_encounter = %(pk_encounter)s
			WHERE
				-- pseudo-regimen will have pk_intake_regimen=NULL while rows in clin.intake_regimen will never do
				pk = %(pk_intake_regimen)s
					AND
				xmin = %(xmin_regimen)s
		""",
		_cmd_fetch_payload
	]
	_updatable_fields = [
		# intake fields:
		'last_checked_when',
		'notes4provider',
		'notes4patient',
		'notes4us',
		'use_type',
		# regimen fields:
		'schedule',
		'started',
		'start_is_unknown',
		'comment_on_start',
		'discontinued',
		'discontinue_reason',
		'planned_duration',
		'pk_encounter',
		'pk_episode'
	]
	#--------------------------------------------------------
	def format_maximum_information(self, allergy=None, left_margin=0, date_format='%Y %b %d'):
		return self.format (
			single_line = False,
			left_margin = left_margin,
			date_format = date_format,
			allergy = allergy,
			include_metadata = True,
			include_instructions = True,
			include_loincs = True,
			eol = None
		)

	#--------------------------------------------------------
	def format(self, left_margin=0, date_format='%Y %b %d', single_line=False, allergy=None, include_instructions=False, include_loincs=False, include_metadata:bool=False, terse:bool=False, eol=None):
		# medication
		if self._payload['use_type'] is None:
			if single_line:
				return '%s%s' % (
					' ' * left_margin,
					format_regimen_like_as_single_line(self, date_format = date_format, terse = terse)
				)

			return self.format_as_multiple_lines (
				left_margin = left_margin,
				date_format = date_format,
				allergy = allergy,
				include_metadata = include_metadata,
				eol = eol
			)

		# misuse
		if self._payload['use_type'] in [0, 1, 2, 3]:
			if single_line:
				return self.format_as_single_line_abuse(left_margin = left_margin, date_format = date_format)

			return self.format_as_multiple_lines_abuse (
				left_margin = left_margin,
				date_format = date_format,
				include_metadata = include_metadata,
				eol = eol
			)

	#--------------------------------------------------------
	def format_as_multiple_lines(self, left_margin:int=0, date_format:str='%Y %b %d', allergy=None, include_loincs:bool=False, include_metadata:bool=False, eol:str=None):
		return format_regimen_like_as_multiple_lines (
			regimen_like = self,
			left_margin = left_margin,
			date_format = date_format,
			allergy = allergy,
			include_loincs = include_loincs,
			include_metadata = include_metadata,
			eol = eol
		)

	#--------------------------------------------------------
	def format_as_single_line_abuse(self, left_margin=0, date_format='%Y %b %d'):
		return '%s%s: %s (%s)' % (
			' ' * left_margin,
			self._payload['substance'],
			self.use_type_string,
			self._payload['last_checked_when'].strftime('%b %Y')
		)

	#--------------------------------------------------------
	def format_as_multiple_lines_abuse(self, left_margin=0, date_format='%Y %b %d', include_metadata:bool=False, eol:str=None):
		return format_regimen_like_as_multiple_lines_abuse (
			regimen_like = self,
			left_margin = left_margin,
			date_format = date_format,
			include_metadata = include_metadata,
			eol = eol
		)

	#--------------------------------------------------------
	def format_for_failsafe_output(self, max_width:int=80) -> list[str]:
		lines = [_('Substance: %s %s') % (
			self['substance'],
			self.formatted_units
		)]
		if self['schedule']:
			lines.append('  ' + _('Regimen: %s') % self['schedule'])
		lines.append('  ' + _('Timerange: %s') % self.medically_formatted_timerange)
		if self['notes4patient']:
			lines.append(gmTools.wrap (
				_('Patient notes: %s') % self['notes4patient'],
				width = max_width,
				initial_indent = '  ',
				subsequent_indent = '    '
			))
		if self['intake_instructions']:
			lines.append(gmTools.wrap (
				_('Instructions: %s') % self['intake_instructions'],
				width = max_width,
				initial_indent = '  ',
				subsequent_indent = '    '
			))
		if self['notes4provider']:
			lines.append(gmTools.wrap (
				_('Provider notes: %s') % self['notes4provider'],
				width = max_width,
				initial_indent = '  ',
				subsequent_indent = '    '
			))
		lines.append('  ' + _('Episode: %s%s') % (
			self['episode'],
			gmTools.coalesce(self['health_issue'], '', ' (%s: %%s)' % _('Issue'))
		))
		return lines

	#--------------------------------------------------------
	def _get_as_amts_data(self, strict=True):
		return format_intake_with_regimen_as_amts_data(intake = self, strict = strict)

	as_amts_data = property(_get_as_amts_data)

	#--------------------------------------------------------
	def _get_use_type_string(self):
		return use_type2str(self._payload['use_type'])

	use_type_string = property(_get_use_type_string)

	#--------------------------------------------------------
	def __get_as_intake_with_regimen(self):
		return self

	as_intake_with_regimen = property(__get_as_intake_with_regimen)

	#--------------------------------------------------------
	def _get_intake(self):
		return cSubstanceIntakeEntry(aPK_obj = self._payload['pk_intake'])

	intake = property(_get_intake)

	#--------------------------------------------------------
	def _get_regimen(self):
		if self._payload['pk_intake_regimen']:
			return cIntakeRegimen(aPK_obj = self._payload['pk_intake_regimen'])

		return None

	regimen = property(_get_regimen)

	#--------------------------------------------------------
	def get_regimens_for_substance(self, ongoing_only:bool=False) -> list:
		return get_intake_regimens (
			pk_substance = self._payload['pk_substance'],
			pk_patient = self._payload['pk_patient'],
			ongoing_only = ongoing_only
		)

	regimens_for_substance = property(get_regimens_for_substance)

	#--------------------------------------------------------
	def _get_containing_drug(self):
		return None

	containing_drug = property(_get_containing_drug)

	#--------------------------------------------------------
	def _get_medically_formatted_start(self):
		return format_regimen_start_medically(self)

	medically_formatted_start = property(_get_medically_formatted_start)

	#--------------------------------------------------------
	def _get_medically_formatted_timerange(self, terse:bool=False):
		return format_regimen_timerange_medically(self, terse = terse)

	medically_formatted_timerange = property(_get_medically_formatted_timerange)

	#--------------------------------------------------------
	def _get_is_ongoing(self):
		if self._payload['discontinued'] is None:
			return True

		now = gmDateTime.pydt_now_here()
		if self._payload['discontinued'] < now:
			return False

		return True

	is_ongoing = property(_get_is_ongoing)

	#--------------------------------------------------------
	def _get_formatted_units(self, short=True):
		return format_units(self._payload['unit'], short = short, none_str = '')

	formatted_units = property(_get_formatted_units)

	#--------------------------------------------------------
	def turn_into_allergy(self, encounter_id=None, allergy_type='allergy'):
		return self.intake.turn_into_allergy (
			encounter_id = encounter_id,
			allergy_type = allergy_type
		)

#------------------------------------------------------------
def delete_intake_with_regimen(pk_intake_regimen:int, pk_intake:int=None, link_obj=None) -> bool:
	"""Delete the given intake regimen.

	If that had been the only regimen, also delete the intake itself, IF the PK for that is known.
	"""
	delete_intake_regimen(pk_intake_regimen = pk_intake_regimen, link_obj = link_obj)
	if not pk_intake:
		return True

	other_regimen4intake = get_intake_regimens(pk_intake = pk_intake, ongoing_only = False, as_instance = False, link_obj = link_obj)
	if not other_regimen4intake:
		delete_substance_intake(pk_intake = pk_intake, delete_regimen = False, link_obj = link_obj)
	return True

#------------------------------------------------------------
def create_intake_with_regimen (
	# intake:
	pk_encounter:int=None,
	pk_episode:int=None,
	pk_substance:int=None,
	# regimen:
	started=None,
	schedule:str=None,
	discontinued=None,
	# other:
	link_obj=None
) -> cIntakeWithRegimen:
	intake = create_substance_intake (
		pk_encounter = pk_encounter,
		pk_episode = pk_episode,
		pk_substance = pk_substance,
		link_obj = link_obj
	)
	regimen = create_intake_regimen (
		pk_intake = intake['pk_intake'],
		started = started,
		pk_encounter = pk_encounter,
		pk_episode = pk_episode,
		schedule = schedule,
		discontinued = discontinued,
		link_obj = link_obj
	)
	return cIntakeWithRegimen (
		aPK_obj = {'pk_intake_regimen': regimen['pk_intake_regimen'], 'pk_intake': regimen['pk_intake']},
		link_obj = link_obj
	)

#------------------------------------------------------------
def get_intakes_with_regimens (
	pk_patient:int=None,
	include_inactive:bool=False,
	order_by:str=None,
	episodes:list[int]=None,
	issues:list[int]=None,
	exclude_potential_abuses:bool=False,
	exclude_medications:bool=False,
	pk_substance:int=None
) -> list[cIntakeWithRegimen]:
	"""Retrieve intake entries for each regimen."""
	where_parts = ['TRUE']
	args:dict[str,int|list[int]] = {}
	if pk_patient:
		where_parts.append('pk_patient = %(pat)s')
		args['pat'] = pk_patient
	if not include_inactive:
		where_parts.append('((discontinued IS NULL) OR (discontinued > clock_timestamp()))')
	if exclude_potential_abuses:
		where_parts.append('use_type IS NULL	-- explicit medications only')
	if exclude_medications:
		where_parts.append('use_type IS NOT NULL	-- no medications')
	if episodes:
		where_parts.append('pk_episode = ANY(%(pk_epis)s)')
		args['pk_epis'] = episodes
	if issues:
		where_parts.append('pk_health_issue = ANY(%(pk_issues)s)')
		args['pk_issues'] = issues
	if pk_substance:
		where_parts.append('pk_substance = %(pk_subst)s')
		args['pk_subst'] = pk_substance
	if order_by:
		order_by = 'ORDER BY %s' % order_by
	else:
		order_by = ''
	cmd = _SQL_get_intake_with_regimen % ('%s %s' % (
		'\nAND '.join(where_parts),
		order_by
	))
	rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
	return [ cIntakeWithRegimen(row = {
		'data': r,
		'pk_obj': {'pk_intake_regimen': r['pk_intake_regimen'], 'pk_intake': r['pk_intake']}
	}) for r in rows ]


#============================================================
# substance intake regimen
#------------------------------------------------------------
_SQL_get_intake_regimens = 'SELECT * FROM clin.v_intake_regimen WHERE %s'

class cIntakeRegimen(gmBusinessDBObject.cBusinessDBObject):
	"""Represents a (real) intake regimen, either active or inactive."""

	_cmd_fetch_payload = _SQL_get_intake_regimens % 'pk_intake_regimen = %s'
	_cmds_store_payload = [
		""" UPDATE clin.intake_regimen SET
				clin_when = %(started)s,
				start_is_unknown = %(start_is_unknown)s,
				comment_on_start = gm.nullify_empty_string(%(comment_on_start)s),
				planned_duration = %(planned_duration)s,
				discontinued = %(discontinued)s,
				discontinue_reason = gm.nullify_empty_string(%(discontinue_reason)s),
				narrative = gm.nullify_empty_string(%(schedule)s),
				fk_encounter = %(pk_encounter)s,
				fk_episode = %(pk_episode)s,
				fk_intake = %(pk_intake)s
			WHERE
				pk = %(pk_intake_regimen)s
					AND
				xmin = %(xmin_intake_regimen)s
			RETURNING
				xmin AS xmin_intake_regimen
				-- also return columns which are calculated in the view used by
				-- the initial SELECT such that they will further on contain their
				-- updated value:
				--, ...
		"""
	]
	# view columns that can be updated:
	_updatable_fields = [
		'started',
		'start_is_unknown',
		'comment_on_start',
		'planned_duration',
		'discontinued',
		'discontinue_reason',
		'pk_encounter',
		'pk_episode',
		'pk_intake',
		'schedule'
	]
	#--------------------------------------------------------
	def format(self, left_margin=0, date_format:str='%Y %b %d', single_line:bool=True, terse:bool=True, eol:str=None, allergy=None):
		if single_line:
			return '%s%s' % (
				' ' * left_margin,
				format_regimen_like_as_single_line(self, date_format = date_format, terse = terse)
			)

		return self.format_as_multiple_lines (
			left_margin = left_margin,
			date_format = date_format,
			allergy = allergy,
			eol = eol
		)

	#--------------------------------------------------------
	def format_as_single_line_abuse(self, left_margin=0, date_format='%Y %b %d'):
		return '%s%s: %s (%s)' % (
			' ' * left_margin,
			self._payload['substance'],
			self.use_type_string,
			self._payload['modified_when'].strftime('%b %Y')
		)

	#--------------------------------------------------------
	def format_as_multiple_lines(self, left_margin:int=0, date_format:str='%Y %b %d', allergy=None, include_loincs:bool=False, eol:str='\n'):
		return format_regimen_like_as_multiple_lines (
			regimen_like = self,
			left_margin = left_margin,
			date_format = date_format,
			allergy = allergy,
			include_loincs = include_loincs,
			eol = eol
		)

	#--------------------------------------------------------
	def _get_is_ongoing(self):
		if self._payload['discontinued'] is None:
			return True

		now = gmDateTime.pydt_now_here()
		if self._payload['discontinued'] < now:
			return False

		return True

	is_ongoing = property(_get_is_ongoing)

	#--------------------------------------------------------
	def __get_as_intake_with_regimen(self):
		return cIntakeWithRegimen(aPK_obj = {'pk_intake_regimen': self['pk_intake_regimen'], 'pk_intake': self['pk_intake']})

	as_intake_with_regimen = property(__get_as_intake_with_regimen)

	#--------------------------------------------------------
	def _get_use_type_string(self):
		return use_type2str(self._payload['use_type'])

	use_type_string = property(_get_use_type_string)

	#--------------------------------------------------------
	def _get_formatted_units(self, short=True):
		return format_units(self._payload['unit'], short = short, none_str = '')

	formatted_units = property(_get_formatted_units)

	#--------------------------------------------------------
	def _get_medically_formatted_start(self):
		return format_regimen_start_medically(self)

	medically_formatted_start = property(_get_medically_formatted_start)

	#--------------------------------------------------------
	def _get_medically_formatted_timerange(self, terse:bool=False):
		return format_regimen_timerange_medically(self, terse = terse)

	medically_formatted_timerange = property(_get_medically_formatted_timerange)

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
def get_intake_regimens(order_by:str=None, pk_intake:int=None, ongoing_only:bool=False, pk_patient:int=None, pk_substance:int=None, as_instance:bool=True, link_obj=None) -> list:
	"""Get intake regimens.

	Args:
		order_by: SQL sort criteria
		pk_intake: constrain by clin.intake PK
		ongoing_only: True -> only return those which are not discontinued
		pk_patient: constrain to this patient
		pk_substance: constrain to this substance
	"""
	assert not(pk_intake and pk_patient), 'must not pass <pk_intake> AND <pk_patient>'
	assert not(pk_intake and pk_substance), 'must not pass <pk_intake> AND <pk_substance>'
	# FIXME: support most_recent
	where_parts = ['true']
	args = {}
	if pk_intake:
		where_parts.append('pk_intake = %(pk_intake)s')
		args['pk_intake'] = pk_intake
	if pk_patient:
		where_parts.append('pk_patient = %(pk_patient)s')
		args['pk_patient'] = pk_patient
	if pk_substance:
		where_parts.append('pk_substance = %(pk_substance)s')
		args['pk_substance'] = pk_substance
	if ongoing_only:
		where_parts.append('discontinued IS NULL')
	SQL = _SQL_get_intake_regimens % '\nAND '.join(where_parts)
	if order_by:
		SQL += ' ORDER BY %s' % order_by
	rows = gmPG2.run_ro_query(sql = SQL, args = args, link_obj = link_obj)
	if as_instance:
		return [ cIntakeRegimen(row = {'data': r, 'pk_field': 'pk_intake_regimen'}, link_obj = link_obj) for r in rows ]

	return [ r['pk_intake_regimen'] for r in rows ]

#------------------------------------------------------------
def create_intake_regimen (
	pk_intake:int=None,
	started=None,
	pk_encounter:int=None,
	pk_episode:int=None,
	schedule:str=None,
	discontinued=None,
	amount=None,
	unit:str=None,
	link_obj=None
) -> cIntakeRegimen:
	query_args = {
		'pk_intake': pk_intake,
		'started': started,
		'pk_encounter': pk_encounter,
		'pk_episode': pk_episode,
		'schedule': schedule,
		'amount': amount,
		'unit': unit
	}
	cols = [
		'fk_intake',
		'clin_when',
		'fk_encounter',
		'fk_episode',
		'narrative',
		'amount',
		'unit',
	]
	placeholders = [
		'%(pk_intake)s',
		'%(started)s',
		'%(pk_encounter)s',
		'%(pk_episode)s',
		'gm.nullify_empty_string(%(schedule)s)',
		'%(amount)s',
		'%(unit)s'
	]
	if discontinued:
		cols.append('discontinued')
		placeholders.append('%(discontinued)s')
		query_args['discontinued'] = discontinued
	SQL = """
		INSERT INTO clin.intake_regimen (
			%s
		) VALUES (
			%s
		)
		RETURNING pk
	""" % (', '.join(cols), ', '.join(placeholders))
	rows = gmPG2.run_rw_query(sql = SQL, args = query_args, return_data = True, link_obj = link_obj)
	return cIntakeRegimen(aPK_obj = rows[0]['pk'], link_obj = link_obj)

#------------------------------------------------------------
def delete_intake_regimen(pk_intake_regimen:int=None, link_obj=None) -> bool:
	SQL = 'DELETE FROM clin.intake_regimen WHERE pk = %(pk)s'
	args = {'pk': pk_intake_regimen}
	gmPG2.run_rw_query(sql = SQL, args = args, link_obj = link_obj)
	return True

#============================================================
# substance intakes
#------------------------------------------------------------
_SQL_get_substance_intake = "SELECT * FROM clin.v_intakes WHERE %s"

class cSubstanceIntakeEntry(gmBusinessDBObject.cBusinessDBObject):
	"""Represents a substance having been/being taken by a patient."""

	_cmd_fetch_payload = _SQL_get_substance_intake % 'pk_intake = %s'
	_cmds_store_payload = [
		"""UPDATE clin.intake SET
				clin_when = %(last_checked_when)s,
				notes4patient = gm.nullify_empty_string(%(notes4patient)s),
				narrative = gm.nullify_empty_string(%(notes4provider)s),
				use_type = %(use_type)s,
				fk_episode = %(pk_episode)s,
				fk_encounter = %(pk_encounter)s
			WHERE
				pk = %(pk_intake)s
					AND
				xmin = %(xmin_intake)s
			RETURNING
				xmin as xmin_intake
		"""
	]
	_updatable_fields = [
		'last_checked_when',
		'notes4patient',
		'notes4provider',
		'notes4us',
		'use_type',
		'pk_episode',
		'pk_encounter'
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
	def format(self, left_margin=0, date_format='%Y %b %d', single_line=True, allergy=None, show_all_product_components=False, include_metadata=True, include_instructions=False, include_loincs=False, eol='\n'):

		# medication
		if self._payload['use_type'] is None:
			if single_line:
				return self.format_as_single_line(left_margin = left_margin, date_format = date_format)

			return self.format_as_multiple_lines (
				left_margin = left_margin,
				date_format = date_format,
				allergy = allergy,
				show_all_product_components = show_all_product_components,
				include_instructions = include_instructions,
				eol = eol
			)

		# abuse
		if single_line:
			return self.format_as_single_line_abuse(left_margin = left_margin, date_format = date_format)

		return self.format_as_multiple_lines_abuse(left_margin = left_margin, date_format = date_format, include_metadata = include_metadata, eol = eol)

	#--------------------------------------------------------
	def format_as_single_line_abuse(self, left_margin=0, date_format='%Y %b %d'):
		return '%s%s: %s (%s)' % (
			' ' * left_margin,
			self._payload['substance'],
			self.use_type_string,
			self._payload['last_checked_when'].strftime('%b %Y')
		)

	#--------------------------------------------------------
	def format_as_single_line(self, left_margin=0, date_format='%Y %b %d'):
		return '%s: %s (%s)' % (
			' ' * left_margin,
			self._payload['substance'],
			self._payload['last_checked_when'].strftime(date_format)
		)

	#--------------------------------------------------------
	def format_as_multiple_lines_abuse(self, left_margin=0, date_format='%Y %b %d', include_metadata=True, eol='\n'):
		lines = []
		if include_metadata:
			lines.append(_('Substance abuse entry                                              [#%s]') % self._payload['pk_intake'])
		lines.append(' ' + _('Substance: %s [#%s]%s') % (
			self._payload['substance'],
			self._payload['pk_substance'],
			gmTools.coalesce(self._payload['atc_substance'], '', ' ATC %s')
		))
		lines.append(' ' + _('Use type: %s') % self.use_type_string)
		lines.append(' ' + _('Last checked: %s') % self._payload['last_checked_when'].strftime('%Y %b %d'))
		if self._payload['discontinued']:
			lines.append(_(' Discontinued %s') % self._payload['discontinued'].strftime(date_format))
		if self._payload['notes4provider']:
			lines.append(_(' Notes: %s') % self._payload['notes4provider'])
		if include_metadata:
			lines.append('')
			lines.append(_('Revision: #%(row_ver)s, %(mod_when)s by %(mod_by)s.') % {
				'row_ver': self._payload['row_version'],
				'mod_when': self._payload['modified_when'].strftime('%Y %b %d  %H:%M.%S'),
				'mod_by': self._payload['modified_by']
			})
		if eol is None:
			return lines

		return eol.join(lines)

	#--------------------------------------------------------
	def format_as_multiple_lines(self, left_margin:int=0, date_format:str='%Y %b %d', allergy=None, show_all_product_components:bool=False, include_instructions:bool=False, include_loincs:bool=False, eol='\n'):# -> list | str:
		lines = []
		# header
		lines.append(_('Substance intake [#%s]                     ') % (
			self._payload['pk_intake']
		))
		# caveat
		if allergy:
			certainty = gmTools.bool2subst(allergy['definite'], _('definite'), _('suspected'))
			lines.append('')
			lines.append(' !! ---- Cave ---- !!')
			lines.append(' %s (%s): %s (%s)' % (
				allergy['l10n_type'],
				certainty,
				allergy['descriptor'],
				gmTools.coalesce(allergy['reaction'], '')[:40]
			))
			lines.append('')
		# what
		lines.append(' ' + _('Substance: %s   [#%s]') % (self._payload['substance'], self._payload['pk_substance']))
		# codes
		if self._payload['atc_substance']:
			lines.append(_(' ATC (substance): %s') % self._payload['atc_substance'])
		if include_loincs and self._payload['loincs']:
			lines.append('%s %s' % (' ' * left_margin, _('LOINCs to monitor:')))
			lines.extend(['%s%s%s%s' % (
				' ' * (left_margin + 1),
				l['loinc'],
				gmTools.coalesce(l['max_age_str'], '', ': ' + _('once within %s')),
				gmTools.coalesce(l['comment'], '', ' (%s)')
			) for l in self._payload['loincs']
		])
		lines.append('')
		lines.append('')
		lines.append(_(' Last checked %s') % self._payload['last_checked_when'].strftime(date_format))
		lines.append('')
		# further notes
		lines.append(_(' Episode: %s')% self._payload['episode'])
		if self._payload['health_issue']:
			lines.append(_(' Health issue: %s') % self._payload['health_issue'])
		if self._payload['notes4provider']:
			lines.append(_(' Provider notes: %s') % self._payload['notes4provider'])
		if self._payload['notes4patient']:
			lines.append(_(' Patient advice: %s') % self._payload['notes4patient'])
		if self._payload['intake_instructions']:
			lines.append(' ' + _('Intake: %s') % self._payload['intake_instructions'])
		lines.append('')
		lines.append(_('Revision: #%(row_ver)s, %(mod_when)s by %(mod_by)s.') % {
			'row_ver': self._payload['row_version'],
			'mod_when': self._payload['modified_when'].strftime('%Y %b %d  %H:%M.%S'),
			'mod_by': self._payload['modified_by']
		})
		if eol is None:
			return lines

		return eol.join(lines)

	#--------------------------------------------------------
	def turn_into_allergy(self, encounter_id=None, allergy_type='allergy'):
		allg = gmAllergy.create_allergy (
			allergene = self._payload['substance'],
			allg_type = allergy_type,
			episode_id = self._payload['pk_episode'],
			encounter_id = encounter_id
		)
		allg['substance'] = self._payload['substance']
		allg['reaction'] = self._payload['discontinue_reason']
		allg['atc_code'] = gmTools.coalesce(self._payload['atc_substance'])
		allg['generics'] = self._payload['substance']
		allg.save()
		return allg

	#--------------------------------------------------------
	def delete(self):
		return delete_substance_intake(pk_intake = self._payload['pk_intake'])

	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def __get_as_intake_with_regimen(self):
		regimens = self.regimens
		if len(regimens) > 1:
			# ambigous, cannot turn into intake with regimen
			return None

		if not regimens:
			pk_regimen = None
		else:
			pk_regimen = regimens[0]['pk_intake_regimen']
		return cIntakeWithRegimen(aPK_obj = {'pk_intake': self['pk_intake'], 'pk_intake_regimen': pk_regimen})

	as_intake_with_regimen = property(__get_as_intake_with_regimen)

	#--------------------------------------------------------
	def _get_regimens(self, ongoing_only=False):
		return get_intake_regimens (
			pk_intake = self._payload['pk_intake'],
			ongoing_only = ongoing_only
		)

	regimens = property(_get_regimens)

	#--------------------------------------------------------
	def _get_ongoing_regimens(self):
		return self._get_regimens(ongoing_only = True)

	ongoing_regimens = property(_get_ongoing_regimens)

	#--------------------------------------------------------
	def _get_use_type_string(self):
		return use_type2str(self._payload['use_type'])

	use_type_string = property(_get_use_type_string)

	#--------------------------------------------------------
	def _get_external_code(self):
		drug = self.containing_drug

		if drug is None:
			return None

		return drug.external_code

	external_code = property(_get_external_code)

	#--------------------------------------------------------
	def _get_external_code_type(self):
		drug = self.containing_drug

		if drug is None:
			return None

		return drug.external_code_type

	external_code_type = property(_get_external_code_type)

	#--------------------------------------------------------
	def _get_containing_drug(self):
		return None

	containing_drug = property(_get_containing_drug)

	#--------------------------------------------------------
	def _get_as_amts_latex(self, strict=True):
		return format_substance_intake_as_amts_latex(intake = self, strict=strict)

	as_amts_latex = property(_get_as_amts_latex)

	#--------------------------------------------------------
	def _get_as_amts_data(self, strict=True):
		return format_substance_intake_as_amts_data(intake = self, strict = strict)

	as_amts_data = property(_get_as_amts_data)

#------------------------------------------------------------
def get_substance_intakes(pk_patient:int=None, return_pks:bool=False, pk_substances:list[int]=None, link_obj=None) -> list[cSubstanceIntakeEntry] | list[int]:
	"""Retrieve substance intakes.

	Args:
		pk_patient: constrain results by patient
		pk_substances: constrain by list of substances
		return_pks: return PKs rather than cSubstanceIntakeEntry's
	"""
	args:dict[str,int|list[int]] = {}
	where_parts = ['true']
	if pk_patient:
		args['pat'] = pk_patient
		where_parts.append('pk_patient = %(pat)s')
	if pk_substances:
		args['pk_substances'] = pk_substances
		where_parts.append('pk_substance = ANY(%(pk_substances)s)')
	SQL = _SQL_get_substance_intake % '\nAND '.join(where_parts)
	rows = gmPG2.run_ro_queries(queries = [{'sql': SQL, 'args': args}], link_obj = link_obj)
	if return_pks:
		return [ r['pk_intake'] for r in rows ]

	return [ cSubstanceIntakeEntry(row = {'data': r, 'pk_field': 'pk_intake'}) for r in rows ]

#------------------------------------------------------------
def substance_intake_exists(pk_identity:int=None, pk_substance:int=None, substance:str=None) -> bool:
	"""Check for existence of substance intakes.

	Args:
		pk_identity: constrain by person
		pk_substance: constrain by substance
	"""
	assert not ((pk_substance is None) and (substance is None)), 'either <pk_substance> or <substance> must be given'
	assert not ((pk_substance is not None) and (substance is not None)), 'only one of <pk_substance> or <substance> may be given'

	where_parts = []
	args:dict[str, int|str] = {}
	if pk_identity:
		args['pk_pat'] = pk_identity
		where_parts.append('fk_encounter IN (SELECT pk FROM clin.encounter WHERE fk_patient = %(pk_pat)s)')
	if pk_substance:
		args['pk_subst'] = pk_substance
		where_parts.append('fk_substance = %(pk_subst)s')
	if substance:
		args['subst'] = substance.strip()
		where_parts.append('fk_substance = (select pk from ref.substance r_s where r_s.description = %(subst)s)')

	cmd = """SELECT EXISTS (
		SELECT 1 FROM clin.intake WHERE
			%s
		LIMIT 1
	)""" % '\nAND\n'.join(where_parts)
	rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
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
			SELECT 1 FROM clin.v_intakes
			WHERE
				%s
			LIMIT 1
		)
	""" % '\nAND\n'.join(where_parts)

	rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
	return rows[0][0]

#------------------------------------------------------------
def create_substance_intake(pk_encounter=None, pk_episode=None, pk_substance=None, link_obj=None):
	args = {
		'pk_enc': pk_encounter,
		'pk_epi': pk_episode,
		'pk_subst': pk_substance
	}
	cmd = """
		INSERT INTO clin.intake (
			fk_encounter,
			fk_episode,
			fk_substance
		) VALUES (
			%(pk_enc)s,
			%(pk_epi)s,
			%(pk_subst)s
		)
		RETURNING pk
	"""
	rows = gmPG2.run_rw_queries(queries = [{'sql': cmd, 'args': args}], return_data = True, link_obj = link_obj)
	return cSubstanceIntakeEntry(aPK_obj = rows[0][0], link_obj = link_obj)

#------------------------------------------------------------
def delete_substance_intake(pk_intake:int=None, delete_regimen:bool=False, link_obj=None) -> bool:
	args = {'pk_intake': pk_intake}
	queries = []
	if delete_regimen:
		queries.append ({
			'sql': 'DELETE FROM clin.intake_regimen c_ir WHERE fk_intake = %(pk_intake)s',
			'args': args
		})
	queries.append ({
		'sql': 'DELETE FROM clin.intake WHERE pk = %(pk_intake)s',
		'args': args
	})
	gmPG2.run_rw_queries(queries = queries, link_obj = link_obj)
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
		cells.append(_esc(intake['drug_product'][:50]))
	else:
		cells.append(_esc(intake['drug_product']))
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
def format_intake_with_regimen_as_amts_data(intake=None, strict=True):
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
	M_fields.append('a="%s"' % intake['substance'])
	M_fields.append('fd="Tabl.o.ä."')
	if intake['schedule']:
		M_fields.append('t="%s"' % intake['schedule'])
	#M_fields.append(u'dud="%s"' % intake['dose unit, like Stück'])
	M_fields.append('r="%s"' % intake['episode'])
	if intake['notes4patient']:
		M_fields.append('i="%s"' % intake['notes4patient'].replace('\n', '//').strip('/'))
	M_line = '<M %s>' % ' '.join(M_fields)
	W_lines = ['<W w="%s" s="%s %s"/>' % (
		intake['substance'],
		intake['amount'],
		format_units(intake['unit'], short = True)
	)]
	return M_line + ''.join(W_lines) + '</M>'

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
	#M_fields.append('a="%s"' % intake['drug_product'])
	M_fields.append('a="%s"' % intake['substance'])
	#M_fields.append('fd="%s"' % intake['l10n_preparation'])
	M_fields.append('fd="EINHEIT"')
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
	amts_template = open(amts_fname, mode = 'wt', encoding = 'utf8')
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
	amts_template = open(amts_fname, mode = 'wt', encoding = 'utf8')
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
	fields.append(intake['drug_product'][:50])
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
		first_chars.append(intake['drug_product'][0])

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
	amts_template = open(amts_fname, mode = 'wt', encoding = 'utf8')
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
	amts_template = open(amts_fname, mode = 'wt', encoding = 'utf8')
	amts_template.write('[form]\n')
	amts_template.write('template = $template$\n')
	amts_template.write('|'.join(amts_fields))
	amts_template.write('\n')
	amts_template.write('$template$\n')
	amts_template.close()

	return amts_fname

#------------------------------------------------------------
# failsafe medication list
#------------------------------------------------------------
def generate_failsafe_medication_list_entries(pk_patient:int=None, max_width:int=80, eol:str=None) -> str|list:
	lines = []
	iwrs = get_intakes_with_regimens (
		pk_patient = pk_patient,
		include_inactive = False,
		order_by = 'discontinued NULLS FIRST, substance',
		exclude_potential_abuses = True,
		exclude_medications = False
	)
	delim = '#' + '-' * (max_width - 1)
	for i in iwrs:
		lines.append(delim)
		lines.extend(i.format_for_failsafe_output(max_width = max_width))
	lines.append(delim)
	if not eol:
		return lines

	return eol.join(lines)

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
			gmTools.tex_escape_string(med['drug_product']),
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
		identifier = med['drug_product']

		try:
			line_data[identifier]
		except KeyError:
			line_data[identifier] = {'drug_product': '', 'l10n_preparation': '', 'schedule': '', 'notes': [], 'strengths': []}

		line_data[identifier]['drug_product'] = identifier
		line_data[identifier]['strengths'].append('%s %s%s' % (med['substance'][:20], med['amount'], med.formatted_units))
		if med['l10n_preparation'] not in identifier:
			line_data[identifier]['l10n_preparation'] = med['l10n_preparation']
		sched_parts = []
		if med['planned_duration'] is not None:
			sched_parts.append(gmDateTime.format_interval(med['planned_duration'], gmDateTime.ACC_DAYS, verbose = True))
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
		identifier = med['drug_product']
		if identifier in already_seen:
			continue
		already_seen.append(identifier)
		lines.append (line1_template % (
			gmTools.tex_escape_string(line_data[identifier]['drug_product']),
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
	return gmEpisode.create_episode (
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
def use_type2str(use_type:int) -> str:
	try:
		return USE_TYPE_NAMES[use_type]

	except KeyError:
		_log.error('unknown medication use type')
		return _('unknown use type [%s]' % use_type)

#------------------------------------------------------------
def format_regimen_like_as_single_line(regimen_like:cIntakeRegimen|cIntakeWithRegimen=None, date_format:str='%Y %b %d', terse:bool=True, include_substance_name:bool=False) -> str:
	"""Format intake regimen into a single line.

	start	duration	end		output
	x		x			x		"planned 14 days, starting 1.3.2020 (cmt), stopped 16.3.2020 (x ago)"
								"14d, (~)1.3.2020 -> 16.3.2020 (x ago)"
	x		x			-		"planned 14 days, starting 1.3.2020 (x ago, cmt)"
								"14d, (~)1.3.2020 (x ago)"
	x		-			x		"starting 1.3.2020 (cmt), for 16 days, until 16.3.2020 (x ago)"
								"(~)1.3.2020 -16d->16.3.2020 (x ago)"
	-		x			x		"planned 14 days, cmt, until 16.3.2020 (x ago)"
								"14d, (...)->16.3.2020 (x ago)"
	x		-			-		"since 1.3.2020 (x ago, cmt)"
								"(~)1.3.2020... (x ago)"
	-		x			-		"for 14d, (since: cmt)"
								"14d (...->)"
	-		-			x		"(since: cmt), until 16.3.2020 (x ago)"
								"14d (...)->16.3.2020 (x ago)"
	-		-			-		"(since: cmt)"
								"?" or "..."

	Args:
		regimen: cIntakeRegimen or cIntakeWithRegimen
	"""
	assert isinstance(regimen_like, (cIntakeRegimen, cIntakeWithRegimen)), '<regimen> must be cIntakeRegimen or cIntakeWithRegimen'

	comment_mark = '¹' if regimen_like['comment_on_start'] else ''
	started = None if regimen_like['start_is_unknown'] else regimen_like['started']
	parts_terse = []
	parts_verbose = []
	if started:
		if gmDateTime.pydt_is_today(started):
			parts_terse.append('[%s%s]' % (_('today'), comment_mark))
			parts_verbose.append(_('started today'))
		elif gmDateTime.pydt_is_yesterday(started):
			parts_terse.append('[%s%s]' % (_('yesterday'), comment_mark))
			parts_verbose.append(_('started yesterday'))
		else:
			parts_terse.append('[%s%s]' % (started.strftime(date_format), comment_mark))
			parts_verbose.append(_('started %s') % started.strftime(date_format))
		if regimen_like['comment_on_start']:
			parts_verbose.append('(%s)' % regimen_like['comment_on_start'])
	else:
		parts_terse.append('?%s' % comment_mark)
		if regimen_like['comment_on_start']:
			parts_verbose.append(_('started "%s"') % regimen_like['comment_on_start'])
	if regimen_like['planned_duration']:
		parts_terse.append('-%s-' % (gmDateTime.format_interval_medically(regimen_like['planned_duration'])))
		parts_verbose.append(_('planned for %s') % gmDateTime.format_interval_medically(regimen_like['planned_duration']))
	if regimen_like['discontinued']:
		if gmDateTime.pydt_is_today(regimen_like['discontinued']):
			parts_terse.append('[%s]' % _('today'))
			parts_verbose.append(_('discontinued today'))
		elif gmDateTime.pydt_is_yesterday(regimen_like['discontinued']):
			parts_terse.append('[%s]' % _('yesterday'))
			parts_verbose.append(_('discontinued yesterday'))
		else:
			now = gmDateTime.pydt_now_here()
			if regimen_like['discontinued'] < now:
				terse_prefix = '-'
				verbose_template = '(%s ago)'
			else:
				terse_prefix = '+'
				verbose_template = '(in %s)'
			parts_terse.append('[%s] (%s%s)' % (
				regimen_like['discontinued'].strftime(date_format),
				terse_prefix,
				gmDateTime.format_apparent_age_medically(gmDateTime.calculate_apparent_age(start = regimen_like['discontinued']))
			))
			parts_verbose.append(_('discontinued %s %s') % (
				regimen_like['discontinued'].strftime(date_format),
				verbose_template % gmDateTime.format_apparent_age_medically(gmDateTime.calculate_apparent_age(start = regimen_like['discontinued']))
			))
		if started:
			parts_verbose.append(_('after %s') % gmDateTime.format_apparent_age_medically(gmDateTime.calculate_apparent_age (
				start = started,
				end = regimen_like['discontinued']
			)))
		if regimen_like['discontinue_reason']:
			parts_verbose.append('"%s"' % regimen_like['discontinue_reason'])
	else:
		parts_terse.append('?')

	if terse:
		return gmTools.u_arrow2right.join(parts_terse)

	subst_prefix = '%s%s%s: ' % (
		regimen_like['substance'],
		gmTools.coalesce(regimen_like['amount'], '', ' %s'),
		format_units(unit = regimen_like['unit'], short = True, none_str = '')
	)
	return subst_prefix + ', '.join(parts_verbose)

#--------------------------------------------------------
def format_regimen_like_as_multiple_lines_abuse(regimen_like:cIntakeRegimen | cIntakeWithRegimen=None, left_margin=0, date_format='%Y %b %d', include_metadata=False, eol='\n'):

	assert isinstance(regimen_like, (cIntakeRegimen, cIntakeWithRegimen)), '<regimen_like> must be cIntakeRegimen or cIntakeWithRegimen'

	lines = []
	if include_metadata:
		lines.append(_('Substance abuse entry                                              [#%s]') % regimen_like['pk_intake'])
	lines.append(' ' + _('Substance: %s [#%s]%s') % (
		regimen_like['substance'],
		regimen_like['pk_substance'],
		gmTools.coalesce(regimen_like['atc_substance'], '', ' ATC %s')
	))
	lines.append(' ' + _('Use type: %s') % regimen_like.use_type_string)
	lines.append(' ' + _('Last checked: %s') % regimen_like['last_checked_when'].strftime('%Y %b %d'))
	if regimen_like['discontinued']:
		lines.append(_(' Discontinued %s') % regimen_like['discontinued'].strftime(date_format))
	if regimen_like['notes4provider']:
		lines.append(_(' Notes: %s') % regimen_like['notes4provider'])
		lines.append('')
	if include_metadata:
		lines.append(_('Intake revision: #%(row_ver)s, %(mod_when)s by %(mod_by)s.') % {
			'row_ver': regimen_like['row_version__intake'],
			'mod_when': regimen_like['modified_when__intake'].strftime('%Y %b %d  %H:%M.%S'),
			'mod_by': regimen_like['modified_by__intake']
		})
		if regimen_like['row_version__regimen']:
			lines.append(_('Regimen revision: #%(row_ver)s, %(mod_when)s by %(mod_by)s.') % {
				'row_ver': regimen_like['row_version__regimen'],
				'mod_when': regimen_like['modified_when__regimen'].strftime('%Y %b %d  %H:%M.%S'),
				'mod_by': regimen_like['modified_by__regimen']
			})
	if eol is None:
		return lines

	return eol.join(lines)

#--------------------------------------------------------
def format_regimen_like_as_multiple_lines (
	regimen_like:cIntakeRegimen | cIntakeWithRegimen=None,
	left_margin:int=0,
	date_format:str='%Y %b %d',
	allergy=None,
	include_loincs:bool=False,
	include_metadata:bool=False,
	eol:str=None
) -> list | str:
	"""Format the intake regimen into multiple lines.

	Args:
		regimen_like: cIntakeRegimen or cIntakeWithRegimen
		left_margin: number of leading spaces added to each line if <eol> is defined
	"""
	assert isinstance(regimen_like, (cIntakeRegimen, cIntakeWithRegimen)), '<regimen_like> must be cIntakeRegimen or cIntakeWithRegimen'

	lines = []
	# header
	status = _('Ongoing')
	if regimen_like['discontinued'] and regimen_like['discontinued'] < gmDateTime.pydt_now_here():
		status = _('Inactive')

	lines.append(_('%s intake of "%s"') % (status, regimen_like['substance']) + '               ')
	# caveat
	if allergy:
		certainty = gmTools.bool2subst(allergy['definite'], _('definite'), _('suspected'))
		lines.append('')
		lines.append(' !! ---- Cave ---- !!')
		lines.append(' %s (%s): %s (%s)' % (
			allergy['l10n_type'],
			certainty,
			allergy['descriptor'],
			gmTools.coalesce(allergy['reaction'], '')[:40]
		))
		lines.append('')
	# use type
	if regimen_like['use_type'] is not None:
		lines.append(' ' + regimen_like.use_type_string)
	if regimen_like['amount']:
		lines.append(' ' + _('Amount: %s %s') % (
			regimen_like['amount'],
			regimen_like._get_formatted_units(short = False)
		))
	if regimen_like['schedule']:
		lines.append(_(' Regimen: %s') % regimen_like['schedule'])
	# codes
	if regimen_like['atc_substance']:
		lines.append(_(' ATC (substance): %s') % regimen_like['atc_substance'])
	if include_loincs and regimen_like['loincs']:
		lines.append('%s %s' % (' ' * left_margin, _('LOINCs to monitor:')))
		lines.extend(['%s%s%s%s' % (
			' ' * (left_margin + 1),
			l['loinc'],
			gmTools.coalesce(l['max_age_str'], '', ': ' + _('once within %s')),
			gmTools.coalesce(l['comment'], '', ' (%s)')
		) for l in regimen_like['loincs']
	])
	lines.append('')
	lines.append('')
	# regimen
	if regimen_like['planned_duration']:
		duration = ' %s %s' % (gmTools.u_arrow2right, gmDateTime.format_interval(regimen_like['planned_duration'], gmDateTime.ACC_DAYS))
	else:
		duration = ''
	lines.append(' ' + _('Started: %s%s') % (regimen_like.medically_formatted_start, duration))
	if regimen_like['discontinued']:
		lines.append(' ' + _('Discontinued %s') % regimen_like['discontinued'].strftime(date_format))
	if regimen_like['discontinue_reason']:
		lines.append(_(' Reason: %s') % regimen_like['discontinue_reason'])
	lines.append('')
	# further notes
	lines.append(_(' Episode: %s')% regimen_like['episode'])
	if regimen_like['health_issue']:
		lines.append(_(' Health issue: %s') % regimen_like['health_issue'])
	if regimen_like['notes4patient']:
		lines.append(_(' Patient advice: %s') % regimen_like['notes4patient'])
	if regimen_like['intake_instructions']:
		lines.append(' ' + _('Intake: %s') % regimen_like['intake_instructions'])
	if regimen_like['notes4provider']:
		lines.append(_(' Provider notes: %s') % regimen_like['notes4provider'])
	if regimen_like['notes4us']:
		lines.append(_(' Own notes: %s') % regimen_like['notes4us'])
	if include_metadata:
		lines.append('')
		lines.append('')
		lines.append('Substance: #%s' % regimen_like['pk_substance'])
		lines.append(_('Intake: #%(pk)s, rev %(row_ver)s, %(mod_when)s by %(mod_by)s.') % {
			'pk': regimen_like['pk_intake'],
			'row_ver': regimen_like['row_version__intake'],
			'mod_when': regimen_like['modified_when__intake'].strftime('%Y %b %d  %H:%M.%S'),
			'mod_by': regimen_like['modified_by__intake']
		})
		if regimen_like['pk_intake_regimen']:
			lines.append(_('Regimen: #%(pk)s, rev %(row_ver)s, %(mod_when)s by %(mod_by)s.') % {
				'pk': regimen_like['pk_intake_regimen'],
				'row_ver': regimen_like['row_version__regimen'],
				'mod_when': regimen_like['modified_when__regimen'].strftime('%Y %b %d  %H:%M.%S'),
				'mod_by': regimen_like['modified_by__regimen']
			})
	if not eol:
		return lines

	eol += (' ' * left_margin)
	return (' ' * left_margin) + eol.join(lines)

#------------------------------------------------------------
def format_units(unit:str=None, dose_unit:str=None, preparation:str=None, short:bool=True, none_str:str=None) -> str:
	"""Format units for display.

	Args:
		unit: the actual unit, say, "mg" (milligrams)
		dose_unit: the "delivery unit", say, "ml" (milliliter)
		preparation: the form factor, say "tablet"
		none_str: what to return if the unit is None

	Returns:
		Formatted unit or None.
	"""
	if unit is None:
		return none_str

	unit = unit.strip()
	dose_unit = dose_unit.strip() if dose_unit else None
	preparation = preparation.strip() if preparation else None
	if short:
		if dose_unit:
			d_u = '/' + dose_unit
		else:
			if preparation:
				d_u = '/' + preparation
			else:
				d_u = ''
		return '%s%s' % (unit, d_u)

	return '%s / %s' % (
		unit,
		gmTools.coalesce (
			dose_unit,
			_('delivery unit%s') % gmTools.coalesce(preparation, '', ' (%s)'),
			'%s'
		)
	)

#------------------------------------------------------------
def format_regimen_start_medically(regimen_like:cIntakeWithRegimen|cIntakeRegimen, terse:bool=False) -> str:
	"""Format start of intake regimen suitable for display.

	Args:
		regimen_like: cIntakeWithRegimen or cIntakeRegimen
	"""
	assert regimen_like, '<regimen_like> must be given'

	if regimen_like['start_is_unknown'] or not regimen_like['started']:
		if not regimen_like['comment_on_start']:
			return '?'

		if terse:
			return '?¹'

		return regimen_like['comment_on_start']

	comment_mark = '¹' if regimen_like['comment_on_start'] else ''
	# starts today
	if gmDateTime.pydt_is_today(regimen_like['started']):
		if terse:
			return _('today') + comment_mark

		return _('today%s (%s)') % (
			comment_mark,
			regimen_like['started'].strftime('%Y %b %d')
		)

	start_prefix = gmTools.u_almost_equal_to if regimen_like['comment_on_start'] else ''
	now = gmDateTime.pydt_now_here()
	# start in the future
	if regimen_like['started'] > now:
		starts_in = regimen_like['started'] - now
		if terse:
			return '%s%s (%s+%s)' % (
				regimen_like['started'].strftime('%Y %b %d'),
				comment_mark,
				gmTools.u_almost_equal_to,
				gmDateTime.format_interval_medically(starts_in, terse = terse)
			)

		return _('%s%s%s (in %s%s)') % (
			start_prefix,
			regimen_like['started'].strftime('%Y %b %d'),
			gmTools.coalesce(regimen_like['comment_on_start'], '', ' [%s]'),
			gmTools.u_almost_equal_to,
			gmDateTime.format_interval_medically(starts_in, terse = terse)
		)

	# started in the past
	started_ago = now - regimen_like['started']
	three_months = pydt.timedelta(weeks = 13, days = 3)
	if started_ago < three_months:
		if terse:
			return '%s%s (%s-%s,%s)' % (
				regimen_like['started'].strftime('%b %d'),
				comment_mark,
				gmTools.u_almost_equal_to,
				gmDateTime.format_interval_medically(started_ago, terse = terse),
				regimen_like['started'].strftime('%Y')
			)

		return _('%s%s%s (%s%s ago, in %s)') % (
			start_prefix,
			regimen_like['started'].strftime('%b %d'),
			gmTools.coalesce(regimen_like['comment_on_start'], '', ' [%s]'),
			gmTools.u_almost_equal_to,
			gmDateTime.format_interval_medically(started_ago, terse = terse),
			regimen_like['started'].strftime('%Y')
		)

	five_years = pydt.timedelta(weeks = 265)
	if started_ago < five_years:
		if terse:
			return '%s%s (%s-%s,%s)' % (
				regimen_like['started'].strftime('%Y %b'),
				comment_mark,
				gmTools.u_almost_equal_to,
				gmDateTime.format_interval_medically(started_ago, terse = terse),
				regimen_like['started'].strftime('%b %d')
			)

		return _('%s%s%s (%s%s ago: %s)') % (
			start_prefix,
			regimen_like['started'].strftime('%Y %b'),
			gmTools.coalesce(regimen_like['comment_on_start'], '', ' [%s]'),
			gmTools.u_almost_equal_to,
			gmDateTime.format_interval_medically(started_ago, terse = terse),
			regimen_like['started'].strftime('%b %d')
		)

	if terse:
		return '%s%s (%s-%s,%s)' % (
			regimen_like['started'].strftime('%Y'),
			comment_mark,
			gmTools.u_almost_equal_to,
			gmDateTime.format_interval_medically(started_ago, terse = terse),
			regimen_like['started'].strftime('%b %d')
		)

	return _('%s%s%s (%s%s ago: %s)') % (
		start_prefix,
		regimen_like['started'].strftime('%Y'),
		gmTools.coalesce(regimen_like['comment_on_start'], '', ' [%s]'),
		gmTools.u_almost_equal_to,
		gmDateTime.format_interval_medically(started_ago, terse = terse),
		regimen_like['started'].strftime('%b %d')
	)

#------------------------------------------------------------
def format_regimen_end_medically(regimen_like:cIntakeWithRegimen|cIntakeRegimen, terse:bool=False) -> str:
	"""Format end of intake regimen suitable for display.

	Args:
		regimen_like: cIntakeWithRegimen or cIntakeRegimen
	"""
	assert regimen_like, '<regimen_like> must be given'

	if gmDateTime.pydt_is_today(regimen_like['discontinued']):
		return _('today')

	if gmDateTime.pydt_is_yesterday(regimen_like['discontinued']):
		return '-1/365' if terse else _('yesterday')

	if not regimen_like['discontinued'] and not regimen_like['planned_duration']:
		return gmTools.u_ellipsis

	if not regimen_like['discontinued'] and not regimen_like['started']:
		return gmTools.u_ellipsis

	now = gmDateTime.pydt_now_here()
	if not regimen_like['discontinued']:
		planned_end = regimen_like['started'] + regimen_like['planned_duration'] - pydt.timedelta(days = 1)
		intv = max(now, planned_end) - min(now, planned_end)
		if planned_end.year == now.year:
			end_template = '%b %d'
			if planned_end < now:
				planned_end_from_now_template = ('-%s,%s' % planned_end.year) if terse else _('%s ago, this year')
			else:
				planned_end_from_now_template = ('+%s,%s' % planned_end.year) if terse else _('in %s, this year')
			planned_end_from_now_str = planned_end_from_now_template % gmDateTime.format_interval_medically(intv, terse = terse)
		else:
			end_template = '%Y'
			if planned_end < now:
				planned_end_from_now_template = '-%s,%s' if terse else _('%s ago: %s')
			else:
				planned_end_from_now_template = '+%s,%s' if terse else _('in %s: %s')
			planned_end_from_now_str = planned_end_from_now_template % (
				gmDateTime.format_interval_medically(intv, terse = terse),
				planned_end.strftime('%b %d')
			)
		return '%s (%s)' % (planned_end.strftime(end_template), planned_end_from_now_str)

	intv = max(now, regimen_like['discontinued']) - min(now, regimen_like['discontinued'])
	if regimen_like['discontinued'].year == now.year:
		end_date_template = '%b %d'
		if regimen_like['discontinued'] < now:
			planned_end_from_now_template = ('-%s,%s' % regimen_like['discontinued'].year) if terse else _('%s ago, this year')
		else:
			planned_end_from_now_template = ('+%s,%s' % regimen_like['discontinued'].year) if terse else _('in %s, this year')
		planned_end_from_now_str = planned_end_from_now_template % gmDateTime.format_interval_medically(intv, terse = terse)
	else:
		end_date_template = '%Y'
		if regimen_like['discontinued'] < now:
			planned_end_from_now_template = '-%s,%s' if terse else _('%s ago: %s')
		else:
			planned_end_from_now_template = '+%s,%s' if terse else _('in %s: %s')
		planned_end_from_now_str = planned_end_from_now_template % (
			gmDateTime.format_interval_medically(intv, terse = terse),
			regimen_like['discontinued'].strftime('%b %d')
		)
	return '%s (%s)' % (regimen_like['discontinued'].strftime(end_date_template), planned_end_from_now_str)

#------------------------------------------------------------
def format_regimen_timerange_of_stopped_medically(regimen_like:cIntakeWithRegimen|cIntakeRegimen, terse:bool=False) -> str:
	"""Format start/end of discontinued regiment suitable for display.

	Args:
		regimen_like: cIntakeWithRegimen or cIntakeRegimen
	"""
	assert regimen_like['discontinued'], '<regimen_like> does not contain discontinued regimen'

	now = gmDateTime.pydt_now_here()
	# format intro
	if gmDateTime.pydt_is_today(regimen_like['discontinued']):
		intro = _('until today')
	else:
		ended_ago = now - regimen_like['discontinued']
		intro = _('until %s%s ago') % (
			gmTools.u_almost_equal_to,
			gmDateTime.format_interval_medically(ended_ago, terse = terse)
		)
	# format start
	if regimen_like['started']:
		comment = '¹' if terse else gmTools.coalesce(regimen_like['comment_on_start'], '', ' [%s]')
		start = '%s%s%s' % (
			gmTools.bool2subst((regimen_like['comment_on_start'] is None), '', gmTools.u_almost_equal_to),
			regimen_like['started'].strftime('%Y %b %d'),
			comment
		)
	else:
		start = gmTools.coalesce(regimen_like['comment_on_start'], '?')
	# format duration taken
	if regimen_like['started']:
		duration_taken = regimen_like['discontinued'] - regimen_like['started'] + pydt.timedelta(days = 1)
		duration_taken_str = gmDateTime.format_interval(duration_taken, gmDateTime.ACC_DAYS)
	else:
		duration_taken_str = '?'
	# format duration planned
	if regimen_like['planned_duration']:
		duration_planned_str = _(' [planned: %s]') % gmDateTime.format_interval(regimen_like['planned_duration'], gmDateTime.ACC_DAYS)
	else:
		duration_planned_str = ''
	# format end
	end = regimen_like['discontinued'].strftime('%Y %b %d')
	# assemble
	return '%s: %s %s %s%s %s %s' % (
		intro,
		start,
		gmTools.u_arrow2right_thick,
		duration_taken_str,
		duration_planned_str,
		gmTools.u_arrow2right_thick,
		end
	)

#------------------------------------------------------------
def format_regimen_timerange_medically(regimen_like:cIntakeWithRegimen|cIntakeRegimen, terse:bool=False) -> str:
	"""Format start/end of intake regimen suitable for display.

	Args:
		regimen_like: cIntakeWithRegimen or cIntakeRegimen
	"""
	now = gmDateTime.pydt_now_here()
	# medications stopped today or before today
	if regimen_like['discontinued']:
		if (regimen_like['discontinued'] < now) or (gmDateTime.pydt_is_today(regimen_like['discontinued'])):
			return format_regimen_timerange_of_stopped_medically(regimen_like, terse = terse)

	arrow_parts = []
	# format start
	arrow_parts.append(format_regimen_start_medically(regimen_like, terse = terse))
	# format durations
	durations = []
	if regimen_like['discontinued']:
		if regimen_like['started']:
			duration_documented = regimen_like['discontinued'] - regimen_like['started']
			durations.append(_('%s (documented)') % gmDateTime.format_interval(duration_documented, gmDateTime.ACC_DAYS))
	if regimen_like['planned_duration'] is not None:
		durations.append(_('%s (plan)') % gmDateTime.format_interval(regimen_like['planned_duration'], gmDateTime.ACC_DAYS))
	spacer = '' if terse else ' '
	if len(durations) == 0:
		duration_str = '' if terse else '?'
	else:
		duration_str = (',%s' % spacer).join(durations)
	arrow_parts.append(duration_str)
	# format end
	arrow_parts.append(format_regimen_end_medically(regimen_like, terse = terse))
	# assemble
	return ('%s%s%s' % (spacer, gmTools.u_arrow2right_thick, spacer)).join(arrow_parts)

#============================================================
# main
#------------------------------------------------------------
if __name__ == "__main__":

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	del _
	from Gnumed.pycommon import gmI18N
	gmI18N.activate_locale()
	gmI18N.install_domain()
	gmDateTime.init()

	#--------------------------------------------------------
	# generic
	#--------------------------------------------------------
	# substance intake
	#--------------------------------------------------------
	def test_create_substance_intake():
		intake = create_substance_intake (
			pk_encounter = 1,
			pk_episode = 1,
			pk_substance = 99
		)
		print(intake)

	#--------------------------------------------------------
	def test_get_intakes():
		for i in get_substance_intakes():
			#print i
			print('------------------------------------------------')
			#print('\n'.join(i.format_maximum_information()))
			print(i['substance'])
			print(i.ongoing_regimens[0].format(single_line = True, terse = True))
			print(i.ongoing_regimens[0].format(single_line = True, terse = False))

	#--------------------------------------------------------
	def test_intake_formatting():
		i = get_substance_intakes()[0]
		print('------------------------------------------------')
		print('\n'.join(i.format_maximum_information()))
		input()
		print('------------------------------------------------')
		print(i.format())
		input()
		print('------------------------------------------------')
		print(i.format_as_single_line())
		input()
		print('------------------------------------------------')
		print(i.format_as_single_line_abuse())
		input()
		print('------------------------------------------------')
		print(i.format_as_multiple_lines())
		input()
		print('------------------------------------------------')
		print(i.format_as_multiple_lines_abuse())

	#--------------------------------------------------------
	def test_format_substance_intake_as_amts_data():
		#print format_substance_intake_as_amts_data(cSubstanceIntakeEntry(1))
		#print(cSubstanceIntakeEntry(1).as_amts_data)
		print(get_intakes_with_regimens()[0].as_amts_data)

	#--------------------------------------------------------
	def test_delete_intake():
		delete_substance_intake(pk_intake = 9, delete_regimen = False)

	#--------------------------------------------------------
	#--------------------------------------------------------
	def test_get_substances():
		for s in get_substances():
			##print s
			print("--------------------------")
			print(s.format())
			print('in use:', s.is_in_use_by_patients)
			print('is component:', s.is_drug_component)

		s = cSubstance(1)
		print(s)
		print(s['loincs'])
		print(s.format())
		print('in use:', s.is_in_use_by_patients)
		print('is component:', s.is_drug_component)

	#--------------------------------------------------------
	def test_get_doses():
		print(create_substance_dose(substance = 'test', amount = 1, unit = 'mg'))
		return
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
			input()

	#--------------------------------------------------------
	def test_intake_regimen():
		conn = gmPG2.get_connection(readonly = False)
#		for reg in get_intake_regimens():
#			#print reg
#			print('------------------------------------------------')
#			#print('\n'.join(reg.format_maximum_information()))
#			print('\n'.join(reg.format()))
#			input()
		start = gmDateTime.pydt_replace(gmDateTime.pydt_now_here(), year = 1965)
		end = gmDateTime.pydt_replace(start, second = start.second + 1)
		reg = create_intake_regimen (
			pk_intake = 1,
			started = start,
			pk_encounter = 1,
			pk_episode = 1,
			schedule = 'test schedule',
			discontinued = end,
			link_obj = conn
		)
		print('\n'.join(reg.format()))
		input()
		reg['schedule'] = 'every now and then'
		reg.save(conn=conn)
		print('\n'.join(reg.format()))
		input()
		reg['pk_drug_product'] = 139
		reg['pk_dose'] = 474
		reg.save(conn=conn)
		print('\n'.join(reg.format()))
		input()
		print(delete_intake_regimen(pk_intake_regimen = reg['pk_intake_regimen'], link_obj = conn))

		conn.rollback()
		conn.close()

	#--------------------------------------------------------
	def test_get_intake_regimens():
		for i in get_intake_regimens():
			print('------------------------------------------------')
			print(i)
			#print('\n'.join(i.format_maximum_information()))
			#print('\n'.join(i.format()))
			#print('\n'.join(i.format_single_line()))
			#print(i.format_single_line(terse = True))
			input()

	#--------------------------------------------------------
	def test_get_intakes_with_regimens():
		for i_w_r in get_intakes_with_regimens():
			print('------------------------------------------------')
			print('-- intake with regimen:')
			#print(i_w_r.format())
			input()
			print(format_regimen_timerange_medically(i_w_r, terse = True))
			print(format_regimen_timerange_medically(i_w_r, terse = False))
			#print('-- intake:')
			#print(i_w_r.intake)
			#input()
			#print('-- regimen:')
			#print(i_w_r.regimen)
			#input()

	#--------------------------------------------------------
	def test_get_habit_drugs():
		print(get_tobacco().format())
		print(get_alcohol().format())
		print(get_other_drug(name = 'LSD').format())

	#--------------------------------------------------------
	def test_generate_renal_insufficiency_urls():
		generate_renal_insufficiency_urls(search_term = 'Metoprolol')

	#--------------------------------------------------------
	def test_generate_liver_information_urls():
		print(generate_liver_information_urls(search_term = 'Metoprolol'))

	#--------------------------------------------------------
	def test_generate_amts_data_template_definition_file(work_dir=None, strict=True):
		print('file:', generate_amts_data_template_definition_file(strict = True))

	#--------------------------------------------------------
	def test_URLs():
		import webbrowser
		import time
		urls = [
			URL_renal_insufficiency,
			URL_long_qt,
			URL_drug_ADR_german_default
		]
		for url in urls:
			print(url)
			webbrowser.open(url, new = 2, autoraise = True)
			input('enter for next')
			time.sleep(0.1)

	#--------------------------------------------------------
	def test_format_units():
		units = ['mg', '', None]
		dose_units = ['ml', '', None]
		preparations = ['liq', '', None]
		for u in units:
			for du in dose_units:
				for prep in preparations:
					kwargs = {'unit': u, 'dose_unit': du, 'preparation': prep}
					none_strs = [None, 'dummy' if u is None else 'error']
					for n in none_strs:
						kwargs['none_str'] = n
						print('%s\n  ==> s: %s ---- l: %s' % (kwargs, format_units(short = True, **kwargs), format_units(short = False, **kwargs)))
			input()

	#--------------------------------------------------------
	def test_can_format():
		input('substance intakes:')
		for si in get_substance_intakes():
			print('.format()')
			si.format()
			print('.format_as_single_line()')
			si.format_as_single_line()
			print('.format_as_single_line_abuse()')
			si.format_as_single_line_abuse()
			print('.format_as_multiple_lines()')
			si.format_as_multiple_lines()

		input('regimens:')
		for ir in get_intake_regimens():
			print('.format()')
			ir.format()
			print('.format_as_single_line()')
			ir.format_as_single_line()
			print('.format_as_single_line_abuse()')
			ir.format_as_single_line_abuse()
			print('.format_as_multiple_lines()')
			ir.format_as_multiple_lines()

		input('intakes with regimens:')
		for iwr in get_intakes_with_regimens():
			print('.format()')
			iwr.format()
			print('.format_as_single_line()')
			iwr.format_as_single_line()
			print('.format_as_single_line_abuse()')
			iwr.format_as_single_line_abuse()
			print('.format_as_multiple_lines()')
			iwr.format_as_multiple_lines()

	#--------------------------------------------------------
	def test_format_regimen_like_as_single_line():
		iwr = None
		for _iwr in get_intakes_with_regimens():
			if _iwr['pk_intake_regimen']:
				iwr = _iwr
				break
		if not iwr:
			print('no intake with regimen')
			return

		print('found intake with regimen')
		print(iwr)
		input()
		now = gmDateTime.pydt_now_here()
		starts = [
			None,
			now,
			now - pydt.timedelta(weeks = 2),
			now - pydt.timedelta(weeks = 3)
			, now + pydt.timedelta(weeks = 1)
		]
		ends = [
			None,
			now,
			now - pydt.timedelta(days = 1),
			now - pydt.timedelta(weeks = 1),
			now + pydt.timedelta(weeks = 1)
		]
		for start in starts:
			for end in ends:
				if end and start:
					if end < start:
						continue
				if start and not end:
					if start > now:
						continue
				print('')
				iwr['started'] = start
				iwr['discontinued'] = end
				input('next start/end: %s -> %s' % (iwr['started'], iwr['discontinued']))

				iwr['start_is_unknown'] = True
				iwr['comment_on_start'] = None
				print(' start unknown:', iwr['start_is_unknown'])
				print(' start comment:', iwr['comment_on_start'])
				print('  =>', format_regimen_like_as_single_line(iwr, terse = True))
				print('  =>', format_regimen_like_as_single_line(iwr, terse = False))
				iwr['start_is_unknown'] = True
				iwr['comment_on_start'] = 'about summer'
				print(' start unknown:', iwr['start_is_unknown'])
				print(' start comment:', iwr['comment_on_start'])
				print('  =>', format_regimen_like_as_single_line(iwr, terse = True))
				print('  =>', format_regimen_like_as_single_line(iwr, terse = False))

				iwr['start_is_unknown'] = False
				iwr['comment_on_start'] = None
				print(' start unknown:', iwr['start_is_unknown'])
				print(' start comment:', iwr['comment_on_start'])
				print('  =>', format_regimen_like_as_single_line(iwr, terse = True))
				print('  =>', format_regimen_like_as_single_line(iwr, terse = False))
				iwr['start_is_unknown'] = False
				iwr['comment_on_start'] = 'about summer'
				print(' start unknown:', iwr['start_is_unknown'])
				print(' start comment:', iwr['comment_on_start'])
				print('  =>', format_regimen_like_as_single_line(iwr, terse = True))
				print('  =>', format_regimen_like_as_single_line(iwr, terse = False))

	#--------------------------------------------------------
	def test_format_regimen_like_as_multiple_lines():
		for iwr in get_intakes_with_regimens():
			print(iwr)
			print(format_regimen_like_as_multiple_lines (
				iwr,
				left_margin = 3,
				allergy = None,
				include_loincs = True,
				eol = '\n'
			))
			input()

		for iwr in get_substance_intakes():
			print(iwr)
			print(format_regimen_like_as_multiple_lines (
				iwr,
				left_margin = 3,
				allergy = None,
				include_loincs = True,
				eol = '\n'
			))
			input()

	#-----------------------------------------------------------------------
	def test_format_medication_list():
		print(generate_failsafe_medication_list_entries(pk_patient = 12, max_width = 80, eol = '\n'))
		return

	#--------------------------------------------------------
	# generic
	#test_URLs()
	#test_generate_renal_insufficiency_urls()
	test_generate_liver_information_urls()
	#test_interaction_check()
	#test_format_units()

	sys.exit()
	gmPG2.request_login_params(setup_pool = True)
	#test_format_medication_list()
	#test_format_regimen_like_as_multiple_lines()
	#test_format_regimen_like_as_single_line()
	#test_get_substances()
	test_get_doses()
	#test_get_components()
	#test_get_drugs()
	#test_get_intakes()
	#test_get_intakes_with_regimens()
	#test_get_intake_regimens()
	#test_intake_formatting()
	#test_intake_regimen()
	#test_create_substance_intake()
	#test_delete_intake()
	#test_get_habit_drugs()
	#test_can_format()

	# AMTS
	#test_generate_amts_data_template_definition_file()
	#test_format_substance_intake_as_amts_data()
