"""Automatic GnuMed scoring tables generation.

This module creates SQL DDL commands for the phrase
wheel usage scoring tables.

Theory of operation:

Any table that should be scored must be recorded in
the table "scored_tables". This script creates the
neccessary scoring tables automatically.
"""
#==================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/bootstrap/Attic/gmScoringSchemaGenerator.py,v $
__version__ = "$Revision: 1.5 $"
__author__ = "Karsten.Hilbert@gmx.net"
__license__ = "GPL"		# (details at http://www.gnu.org)

import sys, os.path, string

from Gnumed.pycommon import gmLog, gmPG
_log = gmLog.gmDefLog
if __name__ == "__main__" :
	_log.SetAllLogLevels(gmLog.lData)

_log.Log(gmLog.lInfo, __version__)

# the scoring tables start with this prefix
scoring_table_prefix = 'score_'
# scored tables inherit the fields used in scoring from this table
scoring_fields_table = 'scoring_fields'

#==================================================================
# SQL statements for scoring setup script
#------------------------------------------------------------------
template_create_scoring_table = """create table %s (
	id serial primary key,
	%s
) inherits (%s);

grant select on %s to group "gm-public" """
#------------------------------------------------------------------
def scoring_table_schema(aCursor, table2score):
	scoring_table = '%s%s' % (scoring_table_prefix, table2score)

	# does the scoring table exist ?
	if gmPG.table_exists(aCursor, scoring_table):
		return []
	# must create scoring table
	_log.Log(gmLog.lInfo, 'no scoring table found for table [%s]' % table2score)
	_log.Log(gmLog.lInfo, 'trying to auto-create scoring table [%s]' % scoring_table)
	# get PK of scored table
	pk = gmPG.get_pkey_name(aCursor, table2score)
	# FIXME: this assumes the PK is always of type INT
	fk_col_def = "fk_%s integer not null references %s(%s)" % (table2score, table2score, pk)
	table_def = template_create_scoring_table % (scoring_table, fk_col_def, scoring_fields_table, scoring_table)
	return [table_def, '']
#------------------------------------------------------------------
def create_scoring_schema(aCursor):
	cmd = "select table_name from scored_tables";
	if gmPG.run_query(aCursor, None, cmd) is None:
		return None
	rows = aCursor.fetchall()
	if len(rows) == 0:
		_log.Log(gmLog.lInfo, 'no tables to score')
		return None
	tables2score = []
	for row in rows:
		tables2score.extend(row)
	_log.Log(gmLog.lData, tables2score)
	# for each table to score
	schema = []
	for scored_table in tables2score:
		scoring_schema = scoring_table_schema(aCursor, scored_table)
		if scoring_schema is None:
			_log.Log(gmLog.lErr, 'cannot generate scoring schema for scored table [%s]' % scored_table)
			return None
		schema.extend(scoring_schema)
		if len(scoring_schema) != 0:
			schema.append('-- ----------------------------------------------')
	return schema
#==================================================================
# main
#------------------------------------------------------------------
if __name__ == "__main__" :
	tmp = ''
	try:
		tmp = raw_input("scoring fields table [%s]: " % scoring_fields_table)
	except KeyboardError:
		pass
	if tmp != '':
		scoring_fields_table = tmp

	dbpool = gmPG.ConnectionPool()
	conn = dbpool.GetConnection('default')
	curs = conn.cursor()

	schema = create_scoring_schema(curs)

	curs.close()
	conn.close()
	dbpool.ReleaseConnection('default')

	if schema is None:
		print "error creating schema"
		sys.exit(-1)

	file = open ('scoring-schema.sql', 'wb')
	for line in schema:
		file.write("%s;\n" % line)
	file.close()
#==================================================================
# $Log: gmScoringSchemaGenerator.py,v $
# Revision 1.5  2004-07-17 21:23:49  ncq
# - run_query now has verbosity argument, so use it
#
# Revision 1.4  2004/06/28 13:31:18  ncq
# - really fix imports, now works again
#
# Revision 1.3  2004/06/28 13:23:20  ncq
# - fix import statements
#
# Revision 1.2  2003/12/29 15:25:07  uid66147
# - auto-add grants on scoring tables
#
# Revision 1.1  2003/10/19 12:57:19  ncq
# - add scoring schema generator and use it
#
