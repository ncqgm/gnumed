# -*- coding: utf8 -*-
"""ATC/DDD handling code.

http://who.no

license: GPL
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/business/gmATC.py,v $
# $Id: gmATC.py,v 1.5 2009-11-29 19:58:36 ncq Exp $
__version__ = "$Revision: 1.5 $"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"

import sys, codecs, logging, csv, re as regex, os.path


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmPG2, gmTools, gmCfg2


_log = logging.getLogger('gm.atc')
_log.info(__version__)

_cfg = gmCfg2.gmCfgData()
#============================================================
def propagate_atc(substance=None, atc=None):

	substance = substance.strip()

	_log.debug('%s: %s', substance, atc)

	if atc is not None:
		if atc.strip() == u'':
			atc = None

	if atc is None:
		atc = text2atc(text = substance, fuzzy = False)[0]
		_log.debug('found ATC: %s', atc)

	if atc is None:
		return

	args = {'atc': atc, 'term': substance}
	queries = [
		{'cmd': u"UPDATE ref.substance_in_brand SET atc_code = %(atc)s WHERE description = %(term)s AND atc_code IS NULL",
		 'args': args},
		{'cmd': u"UPDATE clin.consumed_substance SET atc_code = %(atc)s WHERE description = %(term)s AND atc_code IS NULL",
		 'args': args},
		{'cmd': u"UPDATE ref.branded_drug SET atc_code = %(atc)s WHERE description = %(term)s AND atc_code IS NULL",
		 'args': args}
	]
	gmPG2.run_rw_queries(queries = queries)
#============================================================
def text2atc(text=None, fuzzy=False):

	if fuzzy:
		args = {'term': u'%%%s%%' % text}
		cmd = u"""
			SELECT DISTINCT ON (atc_code) *
			FROM (
				SELECT atc as atc_code, is_group_code, pk_data_source FROM ref.v_atc WHERE term ilike %(term)s
					UNION
				SELECT atc_code, null, null FROM ref.substance_in_brand WHERE description ilike %(term)s
					UNION
				SELECT atc_code, null, null FROM ref.branded_drug WHERE description ilike %(term)s
					UNION
				SELECT atc_code, null, null FROM clin.consumed_substance WHERE description ilike %(term)s
			) as tmp
			ORDER BY atc_code
		"""
	else:
		args = {'term': text.lower()}
		cmd = u"""
			SELECT DISTINCT ON (atc_code) *
			FROM (
				SELECT atc as atc_code, is_group_code, pk_data_source FROM ref.v_atc WHERE lower(term) = %(term)s
					UNION
				SELECT atc_code, null, null FROM ref.substance_in_brand WHERE lower(description) = %(term)s
					UNION
				SELECT atc_code, null, null FROM ref.branded_drug WHERE lower(description) = %(term)s
					UNION
				SELECT atc_code, null, null FROM clin.consumed_substance WHERE lower(description) = %(term)s
			) as tmp
			ORDER BY atc_code
		"""

	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = False)

	return rows
#============================================================
def atc_import(cfg_fname=None, conn=None):

	# read meta data
	_cfg.add_file_source(source = 'atc', file = cfg_fname, encoding = 'utf8')

	data_fname = os.path.join (
		os.path.dirname(cfg_fname),
		_cfg.get(group = 'atc', option = 'data file', source_order = [('atc', 'return')])
	)			# must be in same dir as conf file
	version = _cfg.get(group = 'atc', option = 'version', source_order = [('atc', 'return')])
	lang = _cfg.get(group = 'atc', option = 'language', source_order = [('atc', 'return')])
	desc = _cfg.get(group = 'atc', option = 'description', source_order = [('atc', 'return')])
	url = _cfg.get(group = 'atc', option = 'url', source_order = [('atc', 'return')])
	name_long = _cfg.get(group = 'atc', option = 'long name', source_order = [('atc', 'return')])
	name_short = _cfg.get(group = 'atc', option = 'short name', source_order = [('atc', 'return')])

	_cfg.remove_source(source = 'atc')

	_log.debug('importing ATC version [%s] (%s) from [%s]', version, lang, data_fname)

	args = {'ver': version, 'desc': desc, 'url': url, 'name_long': name_long, 'name_short': name_short, 'lang': lang}

	# create data source record
	queries = [
		{
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
		}
	]
	rows, idx = gmPG2.run_rw_queries(queries = queries, return_data = True)
	data_src_pk = rows[0][0]
	_log.debug('ATC data source record created, pk is #%s', data_src_pk)

	# import data
	csv_file = codecs.open(data_fname, 'rU', 'utf8', 'replace')
	atc_reader = gmTools.unicode_csv_reader(csv_file, delimiter = ",", quotechar = '"')

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
	for loinc_line in atc_reader:
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
	def test_atc_import():
		atc_import(cfg_fname = sys.argv[2], conn = gmPG2.get_connection(readonly = False))
	#--------------------------------------------------------
	def test_text2atc():
		print 'searching ATC code for:', sys.argv[2]
		print ' ', text2atc(sys.argv[2])
		print ' ', text2atc(sys.argv[2], True)
	#--------------------------------------------------------
	if (len(sys.argv)) > 1 and (sys.argv[1] == 'test'):
		#test_atc_import()
		test_text2atc()

#============================================================
# $Log: gmATC.py,v $
# Revision 1.5  2009-11-29 19:58:36  ncq
# - propagate-atc
#
# Revision 1.4  2009/11/28 18:12:02  ncq
# - text2atc() and test
#
# Revision 1.3  2009/10/21 20:32:45  ncq
# - cleanup
#
# Revision 1.2  2009/06/10 20:59:12  ncq
# - data file must be in the same directory as conf file
#
# Revision 1.1  2009/06/04 16:42:54  ncq
# - first version
#
#