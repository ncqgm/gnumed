# -*- coding: utf-8 -*-
"""ATC handling code.

http://who.no

There is no DDD handling because DDD explicitely
does not carry clinical meaning.
"""
#============================================================
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL v2 or later"

import sys
import io
import logging
import csv
import os.path
import re as regex


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmPG2
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmCfg2


_log = logging.getLogger('gm.atc')
_cfg = gmCfg2.gmCfgData()


ATC_NICOTINE = u'N07BA01'
ATC_ETHANOL  = u'V03AB16'

#============================================================
def propagate_atc(substance=None, atc=None):

	_log.debug('substance <%s>, ATC <%s>', substance, atc)

	if atc is not None:
		if atc.strip() == u'':
			atc = None

	if atc is None:
		atcs = text2atc(text = substance, fuzzy = False)
		if len(atcs) == 0:
			_log.debug(u'no ATC found, aborting')
			return atc
		if len(atcs) > 1:
			_log.debug(u'non-unique ATC mapping, aborting')
			return atc
		atc = atcs[0][0].strip()

	args = {'atc': atc, 'term': substance.strip()}
	queries = [
		{'cmd': u"UPDATE ref.substance SET atc = %(atc)s WHERE lower(description) = lower(%(term)s) AND atc IS NULL",
		 'args': args},
		{'cmd': u"UPDATE ref.branded_drug SET atc_code = %(atc)s WHERE lower(description) = lower(%(term)s) AND atc_code IS NULL",
		 'args': args}
	]
	gmPG2.run_rw_queries(queries = queries)

	return atc

#============================================================
def text2atc(text=None, fuzzy=False):

	text = text.strip()

	if fuzzy:
		args = {'term': u'%%%s%%' % text}
		cmd = u"""
			SELECT DISTINCT ON (atc_code) *
			FROM (
				SELECT atc as atc_code, is_group_code, pk_data_source
				FROM ref.v_atc
				WHERE term ilike %(term)s AND atc IS NOT NULL
					UNION
				SELECT atc as atc_code, null, null
				FROM ref.substance
				WHERE description ilike %(term)s AND atc IS NOT NULL
					UNION
				SELECT atc_code, null, null
				FROM ref.branded_drug
				WHERE description ilike %(term)s AND atc_code IS NOT NULL
			) as tmp
			ORDER BY atc_code
		"""
	else:
		args = {'term': text.lower()}
		cmd = u"""
			SELECT DISTINCT ON (atc_code) *
			FROM (
				SELECT atc as atc_code, is_group_code, pk_data_source
				FROM ref.v_atc
				WHERE lower(term) = lower(%(term)s) AND atc IS NOT NULL
					UNION
				SELECT atc as atc_code, null, null
				FROM ref.substance
				WHERE lower(description) = lower(%(term)s) AND atc IS NOT NULL
					UNION
				SELECT atc_code, null, null
				FROM ref.branded_drug
				WHERE lower(description) = lower(%(term)s) AND atc_code IS NOT NULL
			) as tmp
			ORDER BY atc_code
		"""

	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = False)

	_log.debug(u'term: %s => ATCs: %s (fuzzy: %s)', text, rows, fuzzy)

	return rows

#============================================================
def get_reference_atcs(order_by=u'atc, term, lang'):
	cmd = u'SELECT * FROM ref.v_atc ORDER BY %s' % order_by
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd}], get_col_idx = False)
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
	csv_file = io.open(data_fname, mode = 'rt', encoding = 'utf8', errors = 'replace')
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
	cmd = u"""insert into ref.atc_staging values (%s, %s, %s, %s, %s)"""
	first = False
	for atc_line in atc_reader:
		# skip first
		if not first:
			first = True
			continue

		# skip blanks
		if atc_line[0] + atc_line[1] + atc_line[2] + atc_line[3] + atc_line[4] == u'':
			continue

		comment = u''
		unit = u''
		adro = u''

		# "1,1 mg O,P,R,..."
		if regex.match('\d{,3},\d{,3}\s.{1,2}\s.(,.)*$', atc_line[4]):
			tmp, unit, adro = regex.split('\s', atc_line[4])
		# "1,1 mg O,P,R bezogen auf ..."
		elif regex.match('\d{,3},\d{,3}\s.{1,2}\s.(,.)*\s.+$', atc_line[4]):
			tmp, unit, adro, comment = regex.split('\s', atc_line[4], 3)
		# "20 mg O"
		elif regex.match('\d{,3}\s.{1,2}\s.(,.)*$', atc_line[4]):
			tmp, unit, adro = regex.split('\s', atc_line[4])
		# "20 mg O bezogen auf ..."
		elif regex.match('\d{,3}\s.{1,2}\s.(,.)*\s.+$', atc_line[4]):
			tmp, unit, adro, comment = regex.split('\s', atc_line[4], 3)
		# "Standarddosis: 1 Tablette oder 30 ml Mixtur"
		else:
			comment = atc_line[4]

		args = [
			atc_line[0].strip(),
			atc_line[2],
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
	unit,
	administration_route
) select
	%(src_pk)s,
	atc,
	name,
	nullif(comment, ''),
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

	if len(sys.argv) == 1:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

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
	def test_get_reference_atcs():
		print "reference_of_atc_codes:"
		for atc in get_reference_atcs():
			print atc
	#--------------------------------------------------------
	#test_atc_import()
	#test_text2atc()
	test_get_reference_atcs()

#============================================================
