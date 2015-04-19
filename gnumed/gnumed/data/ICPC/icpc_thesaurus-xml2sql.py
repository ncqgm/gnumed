# -*- coding: utf8 -*-

import sys
import io

fname = sys.argv[1]

#================================================================================
SQL_SCRIPT_START = u"""-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
"""

SQL_SCRIPT_END = u"""
DELETE FROM ref.icpc_thesaurus rit
WHERE EXISTS (SELECT 1 FROM ref.icpc ri WHERE ri.term = rit.synonym);

-- --------------------------------------------------------------
"""

SQL_INSERT = u"""INSERT INTO ref.icpc_thesaurus (synonym, fk_code) VALUES (
	'%s',
	(SELECT pk_coding_system
	 FROM ref.icpc
	 WHERE
	 	code = '%s'
	 		AND
	 	fk_data_source = (
	 		SELECT pk
	 		FROM ref.data_source
	 		WHERE
	 			name_short = 'ICPC'
	 				AND
	 			version = '2e-3.0-GM-2004'
	 				AND
	 			lang = 'de'
	 	)
	)
);
"""
#================================================================================
outfile = io.open('v15-ref-icpc2_de-thesaurus.sql', mode = 'wt', encoding = 'utf8')
outfile.write(SQL_SCRIPT_START)

infile = io.open(fname, mode = 'rt', encoding = 'cp1252')

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
