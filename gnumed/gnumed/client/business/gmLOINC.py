# -*- coding: utf8 -*-
"""LOINC handling code.

http://loinc.org

license: GPL
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/business/gmLOINC.py,v $
# $Id: gmLOINC.py,v 1.7 2009-08-11 10:44:15 ncq Exp $
__version__ = "$Revision: 1.7 $"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"

import sys, codecs, logging, csv


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmPG2, gmTools


_log = logging.getLogger('gm.loinc')
_log.info(__version__)

origin_url = u'http://loinc.org'
file_encoding = 'latin1'			# encoding is empirical
license_delimiter = u'Clip Here for Data'
version_tag = u'LOINC(R) Database Version'
name_long = u'LOINC® (Logical Observation Identifiers Names and Codes)'
name_short = u'LOINC'

loinc_fields = u"LOINC_NUM COMPONENT PROPERTY TIME_ASPCT SYSTEM SCALE_TYP METHOD_TYP RELAT_NMS CLASS SOURCE DT_LAST_CH CHNG_TYPE COMMENTS ANSWERLIST STATUS MAP_TO SCOPE NORM_RANGE IPCC_UNITS REFERENCE EXACT_CMP_SY MOLAR_MASS CLASSTYPE FORMULA SPECIES EXMPL_ANSWERS ACSSYM BASE_NAME FINAL NAACCR_ID CODE_TABLE SETROOT PANELELEMENTS SURVEY_QUEST_TEXT SURVEY_QUEST_SRC UNITSREQUIRED SUBMITTED_UNITS RELATEDNAMES2 SHORTNAME ORDER_OBS CDISC_COMMON_TESTS HL7_FIELD_SUBFIELD_ID EXTERNAL_COPYRIGHT_NOTICE EXAMPLE_UNITS INPC_PERCENTAGE LONG_COMMON_NAME".split()

#============================================================
def loinc2info(loinc=None):

	cmd = u"""
select coalesce (
	(select term
	from ref.v_coded_terms
	where
		coding_system = 'LOINC'
			and
		code = %(loinc)s
			and
		lang = i18n.get_curr_lang()
	),
	(select term
	from ref.v_coded_terms
	where
		coding_system = 'LOINC'
			and
		code = %(loinc)s
			and
		lang = 'en_EN'
	),
	(select term
	from ref.v_coded_terms
	where
		coding_system = 'LOINC'
			and
		code = %(loinc)s
	)
)
"""
	args = {'loinc': loinc}
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}])

	return [ r[0] for r in rows ]
#============================================================
def split_LOINCDBTXT(input_fname=None, data_fname=None, license_fname=None):

	_log.debug('splitting LOINC source file [%s]', input_fname)

	if license_fname is None:
		license_fname = gmTools.get_unique_filename(prefix = 'loinc_license', suffix = '.txt')
	_log.debug('LOINC header: %s', license_fname)

	if data_fname is None:
		data_fname = gmTools.get_unique_filename(prefix = 'loinc_data', suffix = '.csv')
	_log.debug('LOINC data: %s', data_fname)

	loinc_file = codecs.open(input_fname, 'rU', encoding = file_encoding, errors = 'replace')
	out_file = codecs.open(license_fname, 'w', encoding = 'utf8', errors = 'replace')

	for line in loinc_file:

		if license_delimiter in line:
			out_file.write(line)
			out_file.close()
			out_file = codecs.open(data_fname, 'w', encoding = 'utf8', errors = 'replace')
			continue

		out_file.write(line)

	out_file.close()

	return data_fname, license_fname
#============================================================
def map_field_names(data_fname='loinc_data.csv'):

	csv_file = codecs.open(data_fname, 'rU', 'utf8', 'replace')
	first_line = csv_file.readline()
	sniffer = csv.Sniffer()
	if sniffer.has_header(first_line):
		pass
#============================================================
def get_version(license_fname='loinc_license.txt'):

	in_file = codecs.open(license_fname, 'rU', encoding = 'utf8', errors = 'replace')

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

	in_file = codecs.open(license_fname, 'rU', encoding = 'utf8', errors = 'replace')
	desc = in_file.read()
	in_file.close()

	args = {'ver': version, 'desc': desc, 'url': origin_url, 'name_long': name_long, 'name_short': name_short, 'lang': lang}

	# create data source record
	queries = [{
		'cmd': u"""delete from ref.data_source where name_short = %(name_short)s and version = %(ver)s""",
		'args': args
	}, {
		'cmd': u"""
insert into ref.data_source (name_long, name_short, version, description, lang, source) values (
	%(name_long)s,
	%(name_short)s,
	%(ver)s,
	%(desc)s,
	%(lang)s,
	%(url)s
)""",
		'args': args
	}, {
		'cmd': u"""select pk from ref.data_source where name_short = %(name_short)s and version = %(ver)s""",
		'args': args
	}]
	rows, idx = gmPG2.run_rw_queries(queries = queries, return_data = True)
	data_src_pk = rows[0][0]
	_log.debug('data source record created, pk is #%s', data_src_pk)

	# import data
	csv_file = codecs.open(data_fname, 'rU', 'utf8', 'replace')
	loinc_reader = gmTools.unicode_csv_reader(csv_file, delimiter = "\t", quotechar = '"')

	# clean out staging area
	curs = conn.cursor()
	cmd = u"""delete from ref.loinc_staging"""
	gmPG2.run_rw_queries(link_obj = curs, queries = [{'cmd': cmd}])
	curs.close()
	conn.commit()
	_log.debug('staging table emptied')

	# from file into staging table
	curs = conn.cursor()
	cmd = u"""insert into ref.loinc_staging values (%s%%s)""" % (u'%s, ' * (len(loinc_fields) - 1))
	first = False
	for loinc_line in loinc_reader:
		if not first:
			first = True
			continue
		gmPG2.run_rw_queries(link_obj = curs, queries = [{'cmd': cmd, 'args': loinc_line}])
	curs.close()
	conn.commit()
	csv_file.close()
	_log.debug('staging table loaded')

	# from staging table to real table
	curs = conn.cursor()
	args = {'src_pk': data_src_pk}
	cmd = u"""
insert into ref.loinc (
	fk_data_source,

	term,

	code,
	comment,
	component,
	property,
	time_aspect,
	system,
	scale_type,
	method_type,
	related_names_1_old,
	grouping_class,
	loinc_internal_source,
	dt_last_change,
	change_type,
	answer_list,
	code_status,
	maps_to,
	scope,
	normal_range,
	ipcc_units,
	reference,
	exact_component_synonym,
	molar_mass,
	grouping_class_type,
	formula,
	species,
	example_answers,
	acs_synonyms,
	base_name,
	final,
	naa_ccr_id,
	code_table,
	is_set_root,
	panel_elements,
	survey_question_text,
	survey_question_source,
	units_required,
	submitted_units,
	related_names_2,
	short_name,
	order_obs,
	cdisc_common_tests,
	hl7_field_subfield_id,
	external_copyright_notice,
	example_units,
	inpc_percentage,
	long_common_name
)

select

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

	nullif(loinc_num, ''),
	nullif(comments, ''),
	nullif(component, ''),
	nullif(property, ''),
	nullif(time_aspect, ''),
	nullif(system, ''),
	nullif(scale_type, ''),
	nullif(method_type, ''),
	nullif(related_names_1_old, ''),
	nullif(class, ''),
	nullif(source, ''),
	nullif(dt_last_change, ''),
	nullif(change_type, ''),
	nullif(answer_list, ''),
	nullif(status, ''),
	nullif(map_to, ''),
	nullif(scope, ''),
	nullif(normal_range, ''),
	nullif(ipcc_units, ''),
	nullif(reference, ''),
	nullif(exact_component_synonym, ''),
	nullif(molar_mass, ''),
	nullif(class_type, '')::smallint,
	nullif(formula, ''),
	nullif(species, ''),
	nullif(example_answers, ''),
	nullif(acs_synonyms, ''),
	nullif(base_name, ''),
	nullif(final, ''),
	nullif(naa_ccr_id, ''),
	nullif(code_table, ''),
	nullif(is_set_root, '')::boolean,
	nullif(panel_elements, ''),
	nullif(survey_question_text, ''),
	nullif(survey_question_source, ''),
	nullif(units_required, ''),
	nullif(submitted_units, ''),
	nullif(related_names_2, ''),
	nullif(short_name, ''),
	nullif(order_obs, ''),
	nullif(cdisc_common_tests, ''),
	nullif(hl7_field_subfield_id, ''),
	nullif(external_copyright_notice, ''),
	nullif(example_units, ''),
	nullif(inpc_percentage, ''),
	nullif(long_common_name, '')

from
	ref.loinc_staging
"""

	gmPG2.run_rw_queries(link_obj = curs, queries = [{'cmd': cmd, 'args': args}])

	curs.close()
	conn.commit()
	_log.debug('transfer from staging table to real table done')

	# clean out staging area
	curs = conn.cursor()
	cmd = u"""delete from ref.loinc_staging"""
	gmPG2.run_rw_queries(link_obj = curs, queries = [{'cmd': cmd}])
	curs.close()
	conn.commit()
	_log.debug('staging table emptied')

	return True
#============================================================
# main
#------------------------------------------------------------
if __name__ == "__main__":

	from Gnumed.pycommon import gmLog2
	from Gnumed.pycommon import gmI18N

	gmI18N.activate_locale()
#	gmDateTime.init()

	#--------------------------------------------------------
	def test_loinc_split():
		split_LOINCDBTXT(input_fname = sys.argv[2])
	#--------------------------------------------------------
	def test_loinc_import():
		loinc_import(version = '2.26')
	#--------------------------------------------------------
	if (len(sys.argv)) > 1 and (sys.argv[1] == 'test'):
		#test_loinc_split()
		test_loinc_import()

#============================================================
