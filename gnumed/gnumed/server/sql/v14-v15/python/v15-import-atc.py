# -*- coding: utf8 -*-

#==============================================================
# GNUmed database schema change script
#
# License: GPL v2 or later
# Author: karsten.hilbert@gmx.net
# 
#==============================================================
import os
import csv

from Gnumed.pycommon import gmPG2
from Gnumed.pycommon import gmTools

#--------------------------------------------------------------
SQL_CREATE_DATA_SOURCE = u"""
delete from ref.data_source
where
	name_short = 'ATC'
		and
	version like '2009-01-%'
		and
	lang in ('en','de','fr','de_DE','en_EN','fr_FR');


insert into ref.data_source (
	name_long,
	name_short,
	version,
	description,
	source,
	lang
) values (
	'Anatomical Therapeutic Chemical Classification',
	'ATC',
	'2009-01-EN',
	'ATC codes downloaded from the source of the GPL software FreeDiams',
	'http://freemedforms.googlecode.com/svn/trunk/global_resources/sql/atc_utf8.csv',
	'en'
);


insert into ref.data_source (
	name_long,
	name_short,
	version,
	description,
	source,
	lang
) values (
	'Anatomical Therapeutic Chemical Classification 1/2009 Deutschland',
	'ATC',
	'2009-01-DE',
	'ATC codes downloaded from the source of the GPL software FreeDiams',
	'http://freemedforms.googlecode.com/svn/trunk/global_resources/sql/atc_utf8.csv',
	'de'
);


insert into ref.data_source (
	name_long,
	name_short,
	version,
	description,
	source,
	lang
) values (
	'Anatomical Therapeutic Chemical Classification',
	'ATC',
	'2009-01-FR',
	'ATC codes downloaded from the source of the GPL software FreeDiams',
	'http://freemedforms.googlecode.com/svn/trunk/global_resources/sql/atc_utf8.csv',
	'fr'
);"""


SQL_GET_DATA_SOURCES = u"""
select
	(select pk from ref.data_source where name_short = 'ATC' and version like '2009-01-%' and lang = 'de') as de,
	(select pk from ref.data_source where name_short = 'ATC' and version like '2009-01-%' and lang = 'fr') as fr,
	(select pk from ref.data_source where name_short = 'ATC' and version like '2009-01-%' and lang = 'en') as en
;"""


SQL_INSERT = u"""
INSERT INTO ref.atc (
	fk_data_source,
	code,
	term
) values (
	%(src)s,
	%(code)s,
	%(term)s
)"""


def run(conn=None):

	gmPG2.run_rw_queries(link_obj = conn, queries = [{'sql': SQL_CREATE_DATA_SOURCE}], end_tx = False)
	rows = gmPG2.run_ro_queries(link_obj = conn, queries = [{'sql': SQL_GET_DATA_SOURCES}])
	data_sources = rows[0]

	data_fname = os.path.join('..', 'sql', 'v14-v15', 'data', 'atc_only-utf8.csv')
	with open(data_fname, newline = '', encoding = 'utf8', errors = 'replace') as csv_file:
		atc_reader = csv.DictReader(csv_file, delimiter = ",", quotechar = '"', fieldnames = [u'atc', u'en', u'fr', u'de'], restkey = 'list_of_values_of_unknown_fields')
		for atc_line in atc_reader:
			queries = [
				{'sql': SQL_INSERT, 'args': {u'src': data_sources['en'], u'code': atc_line['atc'], 'term': atc_line['en']}},
				{'sql': SQL_INSERT, 'args': {u'src': data_sources['fr'], u'code': atc_line['atc'], 'term': atc_line['fr']}},
				{'sql': SQL_INSERT, 'args': {u'src': data_sources['de'], u'code': atc_line['atc'], 'term': atc_line['de']}}
			]
			gmPG2.run_rw_queries(link_obj = conn, queries = queries, end_tx = False)

	conn.commit()

#================================================================================
