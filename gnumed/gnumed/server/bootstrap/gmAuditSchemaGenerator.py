"""Automatic GnuMed audit trail generation.

This module creates SQL DDL commands for the "audit trail" tables,
triggers and functions.

Theory of operation:

Any table that needs to be audited (all modifications
logged) must be marked as such by inheriting from a given
parent table.

This script finds all descendants of that parent table and
creates the tables, triggers and functions neccessary to
establish the audit trail. The backup audit tables will
not have any constraints.
"""
#==================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/bootstrap/gmAuditSchemaGenerator.py,v $
__version__ = "$Revision: 1.1 $"
__author__ = "Horst Herb, Karsten.Hilbert@gmx.net"
__license__ = "GPL"		# (details at http://www.gnu.org)

import sys, os.path, string

if __name__ == "__main__" :
	sys.path.append(os.path.join('.', 'modules'))

import gmLog
_log = gmLog.gmDefLog
if __name__ == "__main__" :
	_log.SetAllLogLevels(gmLog.lData)

import gmPG


#==================================================================
# return all tables inheriting from another table
query_table_descendants = """SELECT relname, oid
FROM pg_class
WHERE pg_class.oid in (
	SELECT inhrelid
	FROM pg_inherits
	WHERE inhparent = (
		SELECT oid
		FROM pg_class
		WHERE relname = '%s'
	)
);"""

# return all attributes and their data types for a given table
query_table_attributes = """SELECT
	a.attname,
	format_type(a.atttypid, a.atttypmod)
FROM
	pg_class pgc, pg_attribute a
WHERE
	pgc.relname = '%s'
		AND
	a.attnum > 0
		AND
	a.attrelid = pgc.oid
ORDER BY a.attnum;"""

# drop trigger
drop_trigger = "DROP TRIGGER %s ON %s;"

# create trigger for a given table
create_trigger = """CREATE TRIGGER %s
	BEFORE UPDATE OR DELETE
	ON %s
	FOR EACH ROW EXECUTE PROCEDURE %s;"""

# drop function
drop_function = "DROP FUNCTION %s(text);"

# create function
create_function = """CREATE FUNCTION %s(text) RETURNS OPAQUE AS '
DECLARE
	reason alias for $1;
BEGIN
	-- explicitely increment row version counter
	NEW.row_version := OLD.row_version + 1;
	INSERT INTO %s (
		-- auditing metadata
		orig_version, orig_when, orig_by, orig_tableoid, modify_action, modify_why,
		-- table content
		%s
	) VALUES (
		-- auditing metadata
		OLD.row_version, OLD.modify_when, OLD.modify_by, TG_RELID, TG_OP, reason,
		-- table content
		%s
	);
	return NEW;
END' LANGUAGE 'plpgsql';"""
#------------------------------------------------------------------
def get_children(aCursor, aTable):
	"""Return all descendants of aTable.
	"""
	cmd = query_table_descendants % aTable
	if not gmPG.run_query(aCursor, cmd):
		_log.Log(gmLog.lErr, 'cannot get children of table %s' % aTable)
		return None
	rows = aCursor.fetchall()
	return rows
#------------------------------------------------------------------
def get_attributes(aCursor, aTable):
	"""Return column attributes of table
	"""
	cmd = query_table_attributes % aTable
	if not gmPG.run_query(aCursor, cmd):
		_log.Log(gmLog.lErr, 'cannot get column attributes for table %s' % aTable)
		return None
	rows = aCursor.fetchall()
	return rows
#------------------------------------------------------------------
def create_logging_table(aCursor, aTable):
	logging_table = 'log_%s' % aTable
	schema = []

	#check first whether the audit table exists, and create it if not
	cmd = "SELECT exists(select oid FROM pg_class where relname = '%s');" % logging_table
	if not gmPG.run_query(aCursor, cmd):
		_log.Log(gmLog.lErr, 'cannot check existance of table %s' % logging_table)
		return None
	result = aCursor.fetchone()
	if not result[0]:
		schema.append('DROP TABLE "%s";' % logging_table)
		schema.append('CREATE TABLE "%s" () INHERITS (audit_log);' % logging_table)
		schema.append('')
	return schema
#------------------------------------------------------------------
def create_trigfunc(aCursor, aTable, audit_prefix="log_"):
	logged_table = aTable
	logging_table = 'log_%s' % logged_table
	funcname = 'f_%s%s' % (audit_prefix, logged_table)
	trigname = 'tr_%s%s' % (audit_prefix, logged_table)

	schema = []

	# function
	schema.append(drop_function % funcname)
	attributes = get_attributes(aCursor, logged_table)
	fields = []
	values = []
	for attribute in attributes:
		fields.append(attribute[0])
		values.append('OLD.%s' % attribute[0])
	fields_clause = string.join(fields, ', ')
	values_clause = string.join(values, ', ')
	schema.append(create_function % (funcname, logging_table, fields_clause, values_clause))
	schema.append('')

	# trigger
	schema.append(drop_trigger % (trigname, funcname))
	schema.append(create_trigger % (trigname, logged_table, funcname))

	return schema
#------------------------------------------------------------------
def create_audit_schema(aCursor, aTable):
	# get a list of all derived tables
	children = get_children(aCursor, aTable)

	# for each derived table
	schema = []
	for child_table in children:
		# create logging table
		data = create_logging_table(aCursor, child_table[0])
		if data is None:
			return None
		schema.extend(data)
		# create trigger
		schema.extend(create_trigfunc(aCursor, child_table[0]))
		schema.append('-- ----------------------------------------------')
	return schema
#==================================================================
# main
#------------------------------------------------------------------
if __name__ == "__main__" :
	parent_table = raw_input("name of parent table: ")

	dbpool = gmPG.ConnectionPool()
	conn = dbpool.GetConnection('default')
	curs = conn.cursor()

	schema = create_audit_schema(curs, parent_table)

	curs.close()
	conn.close()
	dbpool.ReleaseConnection('default')

	if schema is None:
		print "error creating schema"
		sys.exit(-1)

	file = open ('audit-triggers.sql', 'wb')
	for line in schema:
		file.write("%s\n" % line)
	file.close()
#==================================================================
# $Log: gmAuditSchemaGenerator.py,v $
# Revision 1.1  2003-05-12 20:57:19  ncq
# - audit schema generator
#
#
# @change log:
#	12.07.2001 hherb first draft, untested
