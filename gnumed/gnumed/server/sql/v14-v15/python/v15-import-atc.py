# -*- coding: utf8 -*-

#==============================================================
# GNUmed database schema change script
#
# License: GPL
# Author: karsten.hilbert@gmx.net
# 
#==============================================================
import os, codecs

from Gnumed.pycommon import gmPG2

#--------------------------------------------------------------
SQL_CREATE_DATA_SOURCE = u"""
delete from ref.data_source
where
	name_short = 'ATC'
		and
	version like '2009-01-%'
		and
	lang in ('en','de','fr');

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
);
"""

SQL_GET_DATA_SOURCES = u"""
select
	(select pk as de from ref.data_source where name_short = 'ATC' and version like '2009-01-%' and lang = 'de'),
	(select pk as fr from ref.data_source where name_short = 'ATC' and version like '2009-01-%' and lang = 'fr'),
	(select pk as en from ref.data_source where name_short = 'ATC' and version like '2009-01-%' and lang = 'en')
;
"""

SQL_INSERT = u"INSERT INTO ref.atc code"

def run(conn=None):

	gmPG2.run_rw_queries(link_obj = conn, queries = [{'cmd': SQL_CREATE_DATA_SOURCE}], end_tx = False)
	rows, idx = gmPG2.run_ro_queries(link_obj = conn, queries = [{'cmd': SQL_GET_DATA_SOURCES}], get_col_idx = False)
	data_sources = rows[0]

	data_fname = os.path.join('..', 'sql', 'v14-v15', 'data', 'atc_only-utf8.csv')
	csv_file = codecs.open(data_fname, 'rU', 'utf8', 'replace')
	atc_reader = gmTools.unicode_csv_reader(csv_file, delimiter = ",", quotechar = '"')

	for atc_line in atc_reader:
		gmPG2.run_rw_queries(link_obj = conn, queries = [{'cmd': , 'args': {}}], end_tx = False)



#================================================================================
import codecs, sys

fname = sys.argv[1]

#================================================================================
SQL_SCRIPT_START = u"""-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
-- create data source



-- --------------------------------------------------------------
"""



SQL_SCRIPT_END = u"""
DELETE FROM ref.icpc_thesaurus rit
WHERE EXISTS (SELECT 1 FROM ref.icpc ri WHERE ri.term = rit.synonym);

-- --------------------------------------------------------------
"""

#================================================================================
outfile = codecs.open('v15-ref-atc_data.sql', 'w', 'utf8')
outfile.write(SQL_SCRIPT_START)

infile = codecs.open(fname, 'rUb', 'cp1252')

for line in infile:
	line = line.strip(u'\n')
	parts = line.split(u'\t')
	outfile.write(SQL_INSERT % (
		parts[0].replace(u"'", u"''"),
		parts[1].replace(u"'", u"''")
	))

infile.close()

outfile.write(SQL_SCRIPT_END)
outfile.close()

#================================================================================
