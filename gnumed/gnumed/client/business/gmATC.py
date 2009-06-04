# -*- coding: utf8 -*-
"""ATC/DDD handling code.

http://who.no

license: GPL
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/business/gmATC.py,v $
# $Id: gmATC.py,v 1.1 2009-06-04 16:42:54 ncq Exp $
__version__ = "$Revision: 1.1 $"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"

import sys, codecs, logging, csv, re as regex


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmPG2, gmTools, gmCfg2


_log = logging.getLogger('gm.atc')
_log.info(__version__)

_cfg = gmCfg2.gmCfgData()

#origin_url = u'http://loinc.org'
#file_encoding = 'latin1'			# encoding is empirical
#license_delimiter = u'Clip Here for Data'
#version_tag = u'LOINC(R) Database Version'
#name_long = u'LOINC® (Logical Observation Identifiers Names and Codes)'
#name_short = u'LOINC'

#loinc_fields = u"LOINC_NUM COMPONENT PROPERTY TIME_ASPCT SYSTEM SCALE_TYP METHOD_TYP RELAT_NMS CLASS SOURCE DT_LAST_CH CHNG_TYPE COMMENTS ANSWERLIST STATUS MAP_TO SCOPE NORM_RANGE IPCC_UNITS REFERENCE EXACT_CMP_SY MOLAR_MASS CLASSTYPE FORMULA SPECIES EXMPL_ANSWERS ACSSYM BASE_NAME FINAL NAACCR_ID CODE_TABLE SETROOT PANELELEMENTS SURVEY_QUEST_TEXT SURVEY_QUEST_SRC UNITSREQUIRED SUBMITTED_UNITS RELATEDNAMES2 SHORTNAME ORDER_OBS CDISC_COMMON_TESTS HL7_FIELD_SUBFIELD_ID EXTERNAL_COPYRIGHT_NOTICE EXAMPLE_UNITS INPC_PERCENTAGE LONG_COMMON_NAME".split()


#============================================================
def atc_import(cfg_fname=None, conn=None):

	_cfg.add_file_source(source = 'atc', file = cfg_fname, encoding = 'utf8')

	data_fname = _cfg.get(group = 'atc', option = 'data file', source_order = [('atc', 'return')])
	version = _cfg.get(group = 'atc', option = 'version', source_order = [('atc', 'return')])
	lang = _cfg.get(group = 'atc', option = 'language', source_order = [('atc', 'return')])
	desc = _cfg.get(group = 'atc', option = 'description', source_order = [('atc', 'return')])
	url = _cfg.get(group = 'atc', option = 'url', source_order = [('atc', 'return')])
	name_long = _cfg.get(group = 'atc', option = 'long name', source_order = [('atc', 'return')])
	name_short = _cfg.get(group = 'atc', option = 'short name', source_order = [('atc', 'return')])

	_log.debug('importing ATC version [%s] (%s) from [%s]', version, lang, data_fname)

	args = {'ver': version, 'desc': desc, 'url': url, 'name_long': name_long, 'name_short': name_short}

	# create data source record
	queries = [
		{
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
		}
	]
	rows, idx = gmPG2.run_rw_queries(queries = queries, return_data = True)
	data_src_pk = rows[0][0]
	_log.debug('ATC data source record created, pk is #%s', data_src_pk)

	# import data
	csv_file = codecs.open(data_fname, 'rU', 'utf8', 'replace')
	loinc_reader = gmTools.unicode_csv_reader(csv_file, delimiter = ",", quotechar = '"')

	# clean out staging area
	curs = conn.cursor()
	cmd = u"""delete from ref.atc_staging"""
	gmPG2.run_rw_queries(link_obj = curs, queries = [{'cmd': cmd}])
	curs.close()
	conn.commit()
	_log.debug('ATC staging table emptied')

	# from file into staging table
	curs = conn.cursor()
	cmd = u"""insert into ref.atc_staging values (%s, %s, %s, %s, %s, %s)"""
	first = False
	for loinc_line in loinc_reader:
		# skip first
		if not first:
			first = True
			continue
		# skip blanks
		if loinc_line[0] + loinc_line[1] + loinc_line[2] + loinc_line[3] + loinc_line[4] == u'':
			continue

		comment = u''
		ddd_val = u''
		unit = u''
		adro = u''

		# "1,1 mg O,P,R,..."
		if regex.match('\d{,3},\d{,3}\s.{1,2}\s.(,.)*$', loinc_line[4]):
			ddd_val, unit, adro = regex.split('\s', loinc_line[4])
		# "1,1 mg O,P,R bezogen auf ..."
		elif regex.match('\d{,3},\d{,3}\s.{1,2}\s.(,.)*\s.+$', loinc_line[4]):
			ddd_val, unit, adro, comment = regex.split('\s', loinc_line[4], 3)
		# "20 mg O"
		elif regex.match('\d{,3}\s.{1,2}\s.(,.)*$', loinc_line[4]):
			ddd_val, unit, adro = regex.split('\s', loinc_line[4])
		# "20 mg O bezogen auf ..."
		elif regex.match('\d{,3}\s.{1,2}\s.(,.)*\s.+$', loinc_line[4]):
			ddd_val, unit, adro, comment = regex.split('\s', loinc_line[4], 3)
		# "Standarddosis: 1 Tablette oder 30 ml Mixtur"
		else:
			comment = loinc_line[4]

		args = [
			loinc_line[0].strip(),
			loinc_line[2],
			ddd_val.replace(',', '.'),
			unit,
			adro,
			comment
		]

		gmPG2.run_rw_queries(link_obj = curs, queries = [{'cmd': cmd, 'args': args}])

	curs.close()
	conn.commit()
	csv_file.close()
	_log.debug('ATC staging table loaded')

	# from staging table to real table
	curs = conn.cursor()
	args = {'src_pk': data_src_pk}
	cmd = u"""
insert into ref.atc (
	fk_data_source,
	code,
	term,
	comment,
	ddd,
	unit,
	administration_route
) select
	%(src_pk)s,
	atc,
	name,
	nullif(comment, ''),
	nullif(ddd, '')::numeric,
	nullif(unit, ''),
	nullif(adro, '')

from
	ref.atc_staging
"""

	gmPG2.run_rw_queries(link_obj = curs, queries = [{'cmd': cmd, 'args': args}])

	curs.close()
	conn.commit()
	_log.debug('transfer from ATC staging table to real ATC table done')

	# clean out staging area
	curs = conn.cursor()
	cmd = u"""delete from ref.atc_staging"""
	gmPG2.run_rw_queries(link_obj = curs, queries = [{'cmd': cmd}])
	curs.close()
	conn.commit()
	_log.debug('ATC staging table emptied')

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
	#--------------------------------------------------------
	def test_atc_import():
		atc_import(cfg_fname = sys.argv[2], conn = gmPG2.get_connection(readonly = False))
	#--------------------------------------------------------
	if (len(sys.argv)) > 1 and (sys.argv[1] == 'test'):
		#test_loinc_split()
		test_atc_import()

#============================================================
# $Log: gmATC.py,v $
# Revision 1.1  2009-06-04 16:42:54  ncq
# - first version
#
#