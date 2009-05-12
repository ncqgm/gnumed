# -*- coding: utf8 -*-
"""LOINC handling code.

http://loinc.org

license: GPL
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/business/gmLOINC.py,v $
# $Id: gmLOINC.py,v 1.2 2009-05-12 12:05:21 ncq Exp $
__version__ = "$Revision: 1.2 $"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"

import sys, codecs, logging, csv


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmPG2, gmTools


_log = logging.getLogger('gm.loinc')
_log.info(__version__)

download_url = u'http://loinc.org'
file_encoding = 'latin1'			# encoding is empirical
license_delimiter = u'Clip Here for Data'
version_tag = u'LOINC(R) Database Version'
name_long = u'LOINC® (Logical Observation Identifiers Names and Codes)'
name_short = u'LOINC'

loinc_fields = u"LOINC_NUM COMPONENT PROPERTY TIME_ASPCT SYSTEM SCALE_TYP METHOD_TYP RELAT_NMS CLASS SOURCE DT_LAST_CH CHNG_TYPE COMMENTS ANSWERLIST STATUS MAP_TO SCOPE NORM_RANGE IPCC_UNITS REFERENCE EXACT_CMP_SY MOLAR_MASS CLASSTYPE FORMULA SPECIES EXMPL_ANSWERS ACSSYM BASE_NAME FINAL NAACCR_ID CODE_TABLE SETROOT PANELELEMENTS SURVEY_QUEST_TEXT SURVEY_QUEST_SRC UNITSREQUIRED SUBMITTED_UNITS RELATEDNAMES2 SHORTNAME ORDER_OBS CDISC_COMMON_TESTS HL7_FIELD_SUBFIELD_ID EXTERNAL_COPYRIGHT_NOTICE EXAMPLE_UNITS INPC_PERCENTAGE LONG_COMMON_NAME".split()

#============================================================
def split_LOINCDBTXT(input_fname=None, data_fname='loinc_data.csv', license_fname='loinc_license.txt'):

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
def loinc_import(data_fname='loinc_data.csv', license_fname='loinc_license.txt', version=None):

	if version is None:
		version = get_version(license_fname = license_fname)

	if version is None:
		raise ValueError('cannot detect LOINC version')

	in_file = codecs.open(license_fname, 'rU', encoding = 'utf8', errors = 'replace')
	desc = in_file.read()
	in_file.close()

	args = {'ver': version, 'desc': desc, 'url': download_url, 'name_long': name_long, 'name_short': name_short}

	# create data source record
	queries = [{
		'cmd': u"""delete from ref.data_source where name_short = %(name_short)s and version = %(ver)s""",
		'args': args
	}, {
		'cmd': u"""
insert into ref.data_source (name_long, name_short, version, description, source) values (
	%(name_long)s,
	%(name_short)s,
	%(ver)s,
	%(desc)s,
	%(url)s
)""",
		'args': args
	}, {
		'cmd': u"""select pk from ref.data_source where name_short = %(name_short)s and version = %(ver)s""",
		'args': args
	}]
	rows, idx = gmPG2.run_rw_queries(queries = queries, return_data = True)
	data_src_pk = rows[0][0]

	# import data
	csv_file = codecs.open(data_fname, 'rU', 'utf8', 'replace')
	loinc_reader = gmTools.unicode_csv_reader(csv_file, delimiter = "\t", quotechar = '"')

	conn = gmPG2.get_connection(readonly = False)

	curs = conn.cursor()
	cmd = u"""delete from ref.loinc_staging"""
	gmPG2.run_rw_queries(link_obj = curs, queries = [{'cmd': cmd}])
	curs.close()
	conn.commit()

	curs = conn.cursor()
	cmd = u"""insert into ref.loinc_staging values (%s%%s)""" % (u'%s, ' * (len(loinc_fields) - 1))
	first = False
	for loinc_line in loinc_reader:
		if not first:
			first = True
			continue
		#loinc_line = [ gmTools.none_if(cell.strip(), u'') for cell in loinc_line ]
		gmPG2.run_rw_queries(link_obj = curs, queries = [{'cmd': cmd, 'args': loinc_line}])
	curs.close()
	conn.commit()

	csv_file.close()

	cmd = """
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
	grouping_class            | text     |
	loinc_internal_source     | text     |
	dt_last_change            | text     |
	change_type               | text     |
	answer_list               | text     |
	code_status               | text     |
	maps_to                   | text     |
	scope                     | text     |
	normal_range              | text     |
	ipcc_units                | text     |
	reference                 | text     |
	exact_component_synonym   | text     |
	molar_mass                | text     |
	grouping_class_type       | smallint |
	formula                   | text     |
	species                   | text     |
	example_answers           | text     |
	acs_synonyms              | text     |
	base_name                 | text     |
	final                     | text     |
	naa_ccr_id                | text     |
	code_table                | text     |
	is_set_root               | boolean  |
	panel_elements            | text     |
	survey_question_text      | text     |
	survey_question_source    | text     |
	units_required            | text     |
	submitted_units           | text     |
	related_names_2           | text     |
	short_name                | text     |
	order_obs                 | text     |
	cdisc_common_tests        | text     |
	hl7_field_subfield_id     | text     |
	external_copyright_notice | text     |
	example_units,
	inpc_percentage,
	long_common_name
) values (
	%s,

	coalesce (
		long_common_name, (
			coalesce(component || ':', '') ||
			coalesce(property || ':', '') ||
			coalesce(time_aspect || ':', '') ||
			coalesce(system || ':', '') ||
			coalesce(scale_type || ':', '') ||
			coalesce(method_type || ':', '')
		)
	),



)""" % (
	data_src_pk,

)

"""
 loinc_num                 | text |
 component                 | text |
 property                  | text |
 time_aspect               | text |
 system                    | text |
 scale_type                | text |
 method_type               | text |
 related_names_1_old       | text |
 class                     | text |
 source                    | text |
 dt_last_change            | text |
 change_type               | text |
 comments                  | text |
 answer_list               | text |
 status                    | text |
 map_to                    | text |
 scope                     | text |
 normal_range              | text |
 ipcc_units                | text |
 reference                 | text |
 exact_component_synonym   | text |
 molar_mass                | text |
 class_type                | text |
 formula                   | text |
 species                   | text |
 example_answers           | text |
 acs_synonyms              | text |
 base_name                 | text |
 final                     | text |
 naa_ccr_id                | text |
 code_table                | text |
 is_set_root               | text |
 panel_elements            | text |
 survey_question_text      | text |
 survey_question_source    | text |
 units_required            | text |
 submitted_units           | text |
 related_names_2           | text |
 short_name                | text |
 order_obs                 | text |
 cdisc_common_tests        | text |
 hl7_field_subfield_id     | text |
 external_copyright_notice | text |
 example_units             | text |
 inpc_percentage           | text |
 long_common_name          | text |
"""


"""
 (
	fk_data_source           ,
	code                     ,
	component                ,
	property                 ,
	time_aspect              ,
	system                   ,
	scale_type               ,
	method_type              ,
	related_names_1_old      ,
	grouping_class           ,
	loinc_internal_source    ,
	dt_last_change           ,
	change_type              ,
	comment                  ,
	answer_list              ,
	code_status              ,
	maps_to                  ,
	scope                    ,
	normal_range             ,
	ipcc_units               ,
	reference                ,
	exact_component_synonym  ,
	molar_mass               ,
	grouping_class_type      ,
	formula                  ,
	species                  ,
	example_answers          ,
	acs_synonyms             ,
	base_name                ,
	final                    ,
	naa_ccr_id               ,
	code_table               ,
	is_set_root              ,
	panel_elements           ,
	survey_question_text     ,
	survey_question_source   ,
	units_required           ,
	submitted_units          ,
	related_names_2          ,
	short_name               ,
	order_obs                ,
	cdisc_common_tests       ,
	hl7_field_subfield_id    ,
	external_copyright_notice,
	example_units            ,
	inpc_percentage          ,
	term
)
"""

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

#		csv_file = codecs.open('loinc_data.csv', 'rU', 'utf8', 'replace')
#		loinc_reader = gmTools.unicode_csv_reader(csv_file)
#		print dir(loinc_reader)
#		for loinc in loinc_reader:
#			print loinc['LOINC_NUM']
#		csv_file.close()

	#--------------------------------------------------------
	def test_loinc_import():
		loinc_import(version = '2.26')
	#--------------------------------------------------------
	if (len(sys.argv)) > 1 and (sys.argv[1] == 'test'):
		#test_loinc_split()
		test_loinc_import()

#============================================================
# $Log: gmLOINC.py,v $
# Revision 1.2  2009-05-12 12:05:21  ncq
# - some cleanup
#
# Revision 1.1  2009/04/19 22:25:33  ncq
# - new
#
# Revision 1.21  2009/04/03 09:31:37  ncq
# - improved docs
#
# Revision 1.20  2008/08/28 18:30:28  ncq
# - region_code -> urb_region_code
# - support eGK now that libchipcard can read it :-)
# - improved testing
#
# Revision 1.19  2008/02/25 17:31:41  ncq
# - logging cleanup
#
# Revision 1.18  2008/01/30 13:34:50  ncq
# - switch to std lib logging
#
# Revision 1.17  2007/12/26 12:35:30  ncq
# - import_extra_data(..., *args, **kwargs)
#
# Revision 1.16  2007/11/12 22:54:26  ncq
# - fix longstanding semantic bug ! KVK-Nummmer really is VKNR
# - delete KVKd file after importing it
# - improve get_candidate_identities()
# - improve import_extra_data()
# - implement delete_from_source()
# - cleanup, improve docs
#
# Revision 1.15  2007/11/02 10:55:37  ncq
# - syntax error fix
#
# Revision 1.14  2007/10/31 22:06:17  ncq
# - teach about more fields in file
# - start find_me_sql property
#
# Revision 1.13  2007/10/31 11:27:02  ncq
# - fix it again
# - test suite
#
# Revision 1.12  2007/05/11 14:10:19  ncq
# - latin1 -> utf8
#
# Revision 1.11  2007/02/17 13:55:26  ncq
# - consolidate, remove bitrot
#
# Revision 1.10  2007/02/15 14:54:47  ncq
# - fix test suite
# - true_kvk_fields list
# - map_kvkd_tags2dto
# - cDTO_KVK()
# - get_available_kvks_as_dtos()
#
# Revision 1.9  2006/01/01 20:37:22  ncq
# - cleanup
#
# Revision 1.8  2005/11/01 08:49:49  ncq
# - naming fix
#
# Revision 1.7  2005/03/06 14:48:23  ncq
# - patient pick list now works with 'field name' not 'data idx'
#
# Revision 1.6  2004/03/04 19:46:53  ncq
# - switch to package based import: from Gnumed.foo import bar
#
# Revision 1.5  2004/03/02 10:21:10  ihaywood
# gmDemographics now supports comm channels, occupation,
# country of birth and martial status
#
# Revision 1.4  2004/02/25 09:46:20  ncq
# - import from pycommon now, not python-common
#
# Revision 1.3  2003/11/17 10:56:34  sjtan
#
# synced and commiting.
#
# Revision 1.1  2003/10/23 06:02:38  sjtan
#
# manual edit areas modelled after r.terry's specs.
#
# Revision 1.2  2003/04/19 22:53:46  ncq
# - missing parameter for %s
#
# Revision 1.1  2003/04/09 16:15:24  ncq
# - KVK classes and helpers
#
