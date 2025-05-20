# -*- coding: utf-8 -*-
"""LOINC handling code.

http://loinc.org

license: GPL v2 or later
"""
#============================================================
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"

import sys
import logging
import csv
import re as regex


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmPG2
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmMatchProvider


_log = logging.getLogger('gm.loinc')


origin_url = 'http://loinc.org'
file_encoding = 'latin1'			# encoding is empirical
license_delimiter = 'Clip Here for Data'
version_tag = 'LOINC(R) Database Version'
name_long = 'LOINC® (Logical Observation Identifiers Names and Codes)'
name_short = 'LOINC'

loinc_fields = "LOINC_NUM COMPONENT PROPERTY TIME_ASPCT SYSTEM SCALE_TYP METHOD_TYP RELAT_NMS CLASS SOURCE DT_LAST_CH CHNG_TYPE COMMENTS ANSWERLIST STATUS MAP_TO SCOPE NORM_RANGE IPCC_UNITS REFERENCE EXACT_CMP_SY MOLAR_MASS CLASSTYPE FORMULA SPECIES EXMPL_ANSWERS ACSSYM BASE_NAME FINAL NAACCR_ID CODE_TABLE SETROOT PANELELEMENTS SURVEY_QUEST_TEXT SURVEY_QUEST_SRC UNITSREQUIRED SUBMITTED_UNITS RELATEDNAMES2 SHORTNAME ORDER_OBS CDISC_COMMON_TESTS HL7_FIELD_SUBFIELD_ID EXTERNAL_COPYRIGHT_NOTICE EXAMPLE_UNITS INPC_PERCENTAGE LONG_COMMON_NAME".split()

#============================================================

LOINC_creatinine_quantity = ['2160-0', '14682-9', '40264-4', '40248-7']
LOINC_gfr_quantity = ['33914-3', '45066-8', '48642-3', '48643-1', '50044-7', '50210-4', '50384-7', '62238-1', '69405-9', '70969-1']
LOINC_height = ['3137-7', '3138-5', '8301-4', '8302-2', '8305-5', '8306-3', '8307-1', '8308-9']
LOINC_weight = ['18833-4', '29463-7', '3141-9', '3142-7', '8335-2', '8339-4', '8344-4', '8346-9', '8351-9']
LOINC_rr_quantity = ['8478-0', '8448-3', '8449-1', '8456-6', '8457-4', '8458-2', '55284-4', '50403-5', '50402-7', '45372-0']
LOINC_heart_rate_quantity = ['8867-4', '67129-7', '40443-4', '69000-8', '69001-6', '68999-2']
LOINC_inr_quantity = ['34714-6', '46418-0', '6301-6', '38875-1']

#============================================================
# convenience functions
#------------------------------------------------------------
def format_loinc(loinc):
	data = loinc2data(loinc)
	if data is None:
		return None
	return gmTools.format_dict_like (
		dict(data),
		tabular = True,
		value_delimiters = None,
		values2ignore = [None, '']
	)

#------------------------------------------------------------
def loinc2data(loinc):
	cmd = 'SELECT * FROM ref.loinc WHERE code = %(loinc)s'
	args = {'loinc': loinc}
	rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
	if len(rows) == 0:
		return None
	return rows[0]

#------------------------------------------------------------
def loinc2term(loinc=None):

	# NOTE: will return [NULL] on no-match due to the coalesce()
	cmd = """
SELECT coalesce (
	(SELECT term
	FROM ref.v_coded_terms
	WHERE
		coding_system = 'LOINC'
			AND
		code = %(loinc)s
			AND
		lang = i18n.get_curr_lang()
	),
	(SELECT term
	FROM ref.v_coded_terms
	WHERE
		coding_system = 'LOINC'
			AND
		code = %(loinc)s
			AND
		lang = 'en_EN'
	),
	(SELECT term
	FROM ref.v_coded_terms
	WHERE
		coding_system = 'LOINC'
			AND
		code = %(loinc)s
	)
)"""
	args = {'loinc': loinc}
	rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])

	if rows[0][0] is None:
		return []

	return [ r[0] for r in rows ]

#============================================================
# LOINCDBTXT handling
#------------------------------------------------------------
def split_LOINCDBTXT(input_fname=None, data_fname=None, license_fname=None):

	_log.debug('splitting LOINC source file [%s]', input_fname)

	if license_fname is None:
		license_fname = gmTools.get_unique_filename(prefix = 'loinc_license-', suffix = '.txt')
	_log.debug('LOINC header: %s', license_fname)

	if data_fname is None:
		data_fname = gmTools.get_unique_filename(prefix = 'loinc_data-', suffix = '.csv')
	_log.debug('LOINC data: %s', data_fname)

	loinc_file = open(input_fname, mode = 'rt', encoding = file_encoding, errors = 'replace')
	out_file = open(license_fname, mode = 'wt', encoding = 'utf8', errors = 'replace')

	for line in loinc_file:

		if license_delimiter in line:
			out_file.write(line)
			out_file.close()
			out_file = open(data_fname, mode = 'wt', encoding = 'utf8', errors = 'replace')
			continue

		out_file.write(line)

	out_file.close()

	return data_fname, license_fname

#============================================================
def map_field_names(data_fname='loinc_data.csv'):

	csv_file = open(data_fname, mode = 'rt', encoding = 'utf-8-sig', errors = 'replace')
	first_line = csv_file.readline()
	sniffer = csv.Sniffer()
	if sniffer.has_header(first_line):
		pass

#============================================================
def get_version(license_fname='loinc_license.txt'):

	in_file = open(license_fname, mode = 'rt', encoding = 'utf-8-sig', errors = 'replace')

	version = None
	for line in in_file:
		if line.startswith(version_tag):
			version = line[len(version_tag):].strip()
			break

	in_file.close()
	return version

#============================================================
def loinc_import(data_fname=None, license_fname=None, version=None, conn=None, lang='en_EN'):

	if version is None:
		version = get_version(license_fname = license_fname)

	if version is None:
		raise ValueError('cannot detect LOINC version')

	_log.debug('importing LOINC version [%s]', version)

	# clean out staging area
	curs = conn.cursor()
	cmd = """DELETE FROM staging.loinc_staging"""
	gmPG2.run_rw_queries(link_obj = curs, queries = [{'sql': cmd}])
	curs.close()
	conn.commit()
	_log.debug('staging table emptied')

	# import data from csv file into staging table
	csv_file = open(data_fname, mode = 'rt', encoding = 'utf-8-sig', errors = 'replace')
	loinc_reader = gmTools.unicode_csv_reader(csv_file, delimiter = "\t", quotechar = '"')
	curs = conn.cursor()
	cmd = """INSERT INTO staging.loinc_staging values (%s%%s)""" % ('%s, ' * (len(loinc_fields) - 1))
	first = False
	for loinc_line in loinc_reader:
		if not first:
			first = True
			continue
		gmPG2.run_rw_queries(link_obj = curs, queries = [{'sql': cmd, 'args': loinc_line}])
	curs.close()
	conn.commit()
	csv_file.close()
	_log.debug('staging table loaded')

	# create data source record
	in_file = open(license_fname, mode = 'rt', encoding = 'utf-8-sig', errors = 'replace')
	desc = in_file.read()
	in_file.close()
	args = {'ver': version, 'desc': desc, 'url': origin_url, 'name_long': name_long, 'name_short': name_short, 'lang': lang}
	queries = [
		# insert if not existing
		{'args': args, 'sql': """
			INSERT INTO ref.data_source (name_long, name_short, version) SELECT
				%(name_long)s,
				%(name_short)s,
				%(ver)s
			WHERE NOT EXISTS (
				SELECT 1 FROM ref.data_source WHERE
					name_long = %(name_long)s
						AND
					name_short = %(name_short)s
						AND
					version = %(ver)s
			)"""
		},
		# update non-unique fields
		{'args': args, 'sql': """
			UPDATE ref.data_source SET
				description = %(desc)s,
				source = %(url)s,
				lang = %(lang)s
			WHERE
				name_long = %(name_long)s
					AND
				name_short = %(name_short)s
					AND
				version = %(ver)s
			"""
		},
		# retrieve PK of data source
		{'args': args, 'sql': """SELECT pk FROM ref.data_source WHERE name_short = %(name_short)s AND version = %(ver)s"""}
	]
	curs = conn.cursor()
	rows = gmPG2.run_rw_queries(link_obj = curs, queries = queries, return_data = True)
	data_src_pk = rows[0][0]
	curs.close()
	_log.debug('data source record created or updated, pk is #%s', data_src_pk)

	# import from staging table to real table
	args = {'src_pk': data_src_pk}
	queries = []
	queries.append ({
		'args': args,
		'sql': """
			INSERT INTO ref.loinc (
				fk_data_source, term, code
			)
			SELECT
				%(src_pk)s,
				coalesce (
					nullif(long_common_name, ''),
					(
						coalesce(nullif(component, '') || ':', '') ||
						coalesce(nullif(property, '') || ':', '') ||
						coalesce(nullif(time_aspect, '') || ':', '') ||
						coalesce(nullif(system, '') || ':', '') ||
						coalesce(nullif(scale_type, '') || ':', '') ||
						coalesce(nullif(method_type, '') || ':', '')
					)
				),
				nullif(loinc_num, '')
			FROM
				staging.loinc_staging st_ls
			WHERE NOT EXISTS (
				SELECT 1 FROM ref.loinc r_l WHERE
					r_l.fk_data_source = %(src_pk)s
						AND
					r_l.code = nullif(st_ls.loinc_num, '')
						AND
					r_l.term = 	coalesce (
						nullif(st_ls.long_common_name, ''),
						(
							coalesce(nullif(st_ls.component, '') || ':', '') ||
							coalesce(nullif(st_ls.property, '') || ':', '') ||
							coalesce(nullif(st_ls.time_aspect, '') || ':', '') ||
							coalesce(nullif(st_ls.system, '') || ':', '') ||
							coalesce(nullif(st_ls.scale_type, '') || ':', '') ||
							coalesce(nullif(st_ls.method_type, '') || ':', '')
						)
					)
			)"""
	})
	queries.append ({
		'args': args,
		'sql': """
			UPDATE ref.loinc SET
				comment = nullif(st_ls.comments, ''),
				component = nullif(st_ls.component, ''),
				property = nullif(st_ls.property, ''),
				time_aspect = nullif(st_ls.time_aspect, ''),
				system = nullif(st_ls.system, ''),
				scale_type = nullif(st_ls.scale_type, ''),
				method_type = nullif(st_ls.method_type, ''),
				related_names_1_old = nullif(st_ls.related_names_1_old, ''),
				grouping_class = nullif(st_ls.class, ''),
				loinc_internal_source = nullif(st_ls.source, ''),
				dt_last_change = nullif(st_ls.dt_last_change, ''),
				change_type = nullif(st_ls.change_type, ''),
				answer_list = nullif(st_ls.answer_list, ''),
				code_status = nullif(st_ls.status, ''),
				maps_to = nullif(st_ls.map_to, ''),
				scope = nullif(st_ls.scope, ''),
				normal_range = nullif(st_ls.normal_range, ''),
				ipcc_units = nullif(st_ls.ipcc_units, ''),
				reference = nullif(st_ls.reference, ''),
				exact_component_synonym = nullif(st_ls.exact_component_synonym, ''),
				molar_mass = nullif(st_ls.molar_mass, ''),
				grouping_class_type = nullif(st_ls.class_type, '')::smallint,
				formula = nullif(st_ls.formula, ''),
				species = nullif(st_ls.species, ''),
				example_answers = nullif(st_ls.example_answers, ''),
				acs_synonyms = nullif(st_ls.acs_synonyms, ''),
				base_name = nullif(st_ls.base_name, ''),
				final = nullif(st_ls.final, ''),
				naa_ccr_id = nullif(st_ls.naa_ccr_id, ''),
				code_table = nullif(st_ls.code_table, ''),
				is_set_root = nullif(st_ls.is_set_root, '')::boolean,
				panel_elements = nullif(st_ls.panel_elements, ''),
				survey_question_text = nullif(st_ls.survey_question_text, ''),
				survey_question_source = nullif(st_ls.survey_question_source, ''),
				units_required = nullif(st_ls.units_required, ''),
				submitted_units = nullif(st_ls.submitted_units, ''),
				related_names_2 = nullif(st_ls.related_names_2, ''),
				short_name = nullif(st_ls.short_name, ''),
				order_obs = nullif(st_ls.order_obs, ''),
				cdisc_common_tests = nullif(st_ls.cdisc_common_tests, ''),
				hl7_field_subfield_id = nullif(st_ls.hl7_field_subfield_id, ''),
				external_copyright_notice = nullif(st_ls.external_copyright_notice, ''),
				example_units = nullif(st_ls.example_units, ''),
				inpc_percentage = nullif(st_ls.inpc_percentage, ''),
				long_common_name = nullif(st_ls.long_common_name, '')
			FROM
				staging.loinc_staging st_ls
			WHERE
				fk_data_source = %(src_pk)s
					AND
				code = nullif(st_ls.loinc_num, '')
					AND
				term = coalesce (
					nullif(st_ls.long_common_name, ''),
					(
						coalesce(nullif(st_ls.component, '') || ':', '') ||
						coalesce(nullif(st_ls.property, '') || ':', '') ||
						coalesce(nullif(st_ls.time_aspect, '') || ':', '') ||
						coalesce(nullif(st_ls.system, '') || ':', '') ||
						coalesce(nullif(st_ls.scale_type, '') || ':', '') ||
						coalesce(nullif(st_ls.method_type, '') || ':', '')
					)
				)
		"""
	})
	curs = conn.cursor()
	gmPG2.run_rw_queries(link_obj = curs, queries = queries)
	curs.close()
	conn.commit()
	_log.debug('transfer from staging table to real table done')

	# clean out staging area
	curs = conn.cursor()
	cmd = """DELETE FROM staging.loinc_staging"""
	gmPG2.run_rw_queries(link_obj = curs, queries = [{'sql': cmd}])
	curs.close()
	conn.commit()
	_log.debug('staging table emptied')

	return True

#============================================================
_SQL_LOINC_from_test_type = """
	-- from test type
	SELECT
		loinc AS data,
		loinc AS field_label,
		(loinc || ': ' || abbrev || ' (' || name || ')') AS list_label
	FROM clin.test_type
	WHERE loinc %(fragment_condition)s
"""

_SQL_LOINC_from_i18n_coded_term = """
	-- from coded term, in user language
	SELECT
		code AS data,
		code AS field_label,
		(code || ': ' || term) AS list_label
	FROM ref.v_coded_terms
	WHERE
		coding_system = 'LOINC'
			AND
		lang = i18n.get_curr_lang()
			AND
		(code %(fragment_condition)s
			OR
		term %(fragment_condition)s)
"""

_SQL_LOINC_from_en_EN_coded_term = """
	-- from coded term, in English
	SELECT
		code AS data,
		code AS field_label,
		(code || ': ' || term) AS list_label
	FROM ref.v_coded_terms
	WHERE
		coding_system = 'LOINC'
			AND
		lang = 'en_EN'
			AND
		(code %(fragment_condition)s
			OR
		term %(fragment_condition)s)
"""

_SQL_LOINC_from_any_coded_term = """
	-- from coded term, in any language
	SELECT
		code AS data,
		code AS field_label,
		(code || ': ' || term) AS list_label
	FROM ref.v_coded_terms
	WHERE
		coding_system = 'LOINC'
			AND
		(code %(fragment_condition)s
			OR
		term %(fragment_condition)s)
"""

#------------------------------------------------------------
class cLOINCMatchProvider(gmMatchProvider.cMatchProvider_SQL2):

	_pattern = regex.compile(r'^\D+\s+\D+$', regex.UNICODE)

	_normal_query = """
		SELECT DISTINCT ON (list_label)
			data,
			field_label,
			list_label
		FROM (
			(%s) UNION ALL (
			%s)
		) AS all_known_loinc""" % (
			_SQL_LOINC_from_test_type,
			_SQL_LOINC_from_any_coded_term
		)
#--			%s) UNION ALL (
#--			%s) UNION ALL (
#		%
#			_SQL_LOINC_from_i18n_coded_term,
#			_SQL_LOINC_from_en_EN_coded_term,

	#--------------------------------------------------------
	def getMatchesByPhrase(self, aFragment):
		"""Return matches for aFragment at start of phrases."""

		self._queries = [cLOINCMatchProvider._normal_query + '\nORDER BY list_label\nLIMIT 75']
		return gmMatchProvider.cMatchProvider_SQL2.getMatchesByPhrase(self, aFragment)

	#--------------------------------------------------------
	def getMatchesByWord(self, aFragment):
		"""Return matches for aFragment at start of words inside phrases."""

		if cLOINCMatchProvider._pattern.match(aFragment):
			fragmentA, fragmentB = aFragment.split(' ', 1)
			query1 = cLOINCMatchProvider._normal_query % {'fragment_condition': '~* %%(fragmentA)s'}
			self._args['fragmentA'] = "( %s)|(^%s)" % (fragmentA, fragmentA)
			query2 = cLOINCMatchProvider._normal_query % {'fragment_condition': '~* %%(fragmentB)s'}
			self._args['fragmentB'] = "( %s)|(^%s)" % (fragmentB, fragmentB)
			self._queries = ["SELECT * FROM (\n(%s\n) INTERSECT (%s)\n) AS intersected_matches\nORDER BY list_label\nLIMIT 75" % (query1, query2)]
			return self._find_matches('dummy')

		self._queries = [cLOINCMatchProvider._normal_query + '\nORDER BY list_label\nLIMIT 75']
		return gmMatchProvider.cMatchProvider_SQL2.getMatchesByWord(self, aFragment)

	#--------------------------------------------------------
	def getMatchesBySubstr(self, aFragment):
		"""Return matches for aFragment as a true substring."""

		if cLOINCMatchProvider._pattern.match(aFragment):
			fragmentA, fragmentB = aFragment.split(' ', 1)
			query1 = cLOINCMatchProvider._normal_query % {'fragment_condition': "ILIKE %%(fragmentA)s"}
			self._args['fragmentA'] = '%%%s%%' % fragmentA
			query2 = cLOINCMatchProvider._normal_query % {'fragment_condition': "ILIKE %%(fragmentB)s"}
			self._args['fragmentB'] = '%%%s%%' % fragmentB
			self._queries = ["SELECT * FROM (\n(%s\n) INTERSECT (%s)\n) AS intersected_matches\nORDER BY list_label\nLIMIT 75" % (query1, query2)]
			return self._find_matches('dummy')

		self._queries = [cLOINCMatchProvider._normal_query + '\nORDER BY list_label\nLIMIT 75']
		return gmMatchProvider.cMatchProvider_SQL2.getMatchesBySubstr(self, aFragment)

#============================================================
# main
#------------------------------------------------------------
if __name__ == "__main__":

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	from Gnumed.pycommon import gmI18N

	gmI18N.activate_locale()
#	gmDateTime.init()

	#--------------------------------------------------------
	def test_loinc_split():
		print(split_LOINCDBTXT(input_fname = sys.argv[2]))
	#--------------------------------------------------------
	def test_loinc_import():
		loinc_import(version = '2.26')
	#--------------------------------------------------------
	def test_loinc2term():
		term = loinc2term(sys.argv[2])
		print(sys.argv[2], '->', term)

	#--------------------------------------------------------
	def test_format_loinc():
		loinc = sys.argv[2]
		print(loinc)
		print(format_loinc(loinc))

	#--------------------------------------------------------
	#test_loinc_split()
	#test_loinc_import()
	#test_loinc2term()
	test_format_loinc()

#============================================================
