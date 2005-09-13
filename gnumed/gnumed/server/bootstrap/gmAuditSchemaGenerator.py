"""Automatic GnuMed audit trail generation.

This module creates SQL DDL commands for the audit
trail triggers and functions.

Theory of operation:

Any table that needs to be audited (all modifications
logged) must be recorded in the table "audited_tables".

This script creates the triggers, functions and tables
neccessary to establish the audit trail. Some or all
audit trail tables may have been created previously but
need not contain all columns of the audited table. Do not
put any constraints on the audit trail tables except for
"not null" on those columns that cannot be null in the
audited table.
"""
#==================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/bootstrap/gmAuditSchemaGenerator.py,v $
__version__ = "$Revision: 1.23 $"
__author__ = "Horst Herb, Karsten.Hilbert@gmx.net"
__license__ = "GPL"		# (details at http://www.gnu.org)

import sys, os.path, string

from Gnumed.pycommon import gmLog, gmPG
_log = gmLog.gmDefLog
if __name__ == "__main__" :
	_log.SetAllLogLevels(gmLog.lData)

_log.Log(gmLog.lInfo, __version__)

# the audit trail tables start with this prefix
audit_trail_table_prefix = 'log_'
# and inherit from this table
audit_trail_parent_table = 'audit_trail'
# audited tables inherit these fields
audit_fields_table = 'audit_fields'

#==================================================================
# convenient queries
#------------------------------------------------------------------
# return all tables inheriting from another table
query_table_descendants = """SELECT relname, oid
FROM pg_class
WHERE pg_class.oid in (
	SELECT inhrelid
	FROM pg_inherits
	WHERE inhparent = (
		SELECT oid
		FROM pg_class
		WHERE relname = %s
	)
)"""

# return all attributes for a given table
query_table_attributes = """SELECT
	pga.attname as attribute
FROM
	pg_class pgc, pg_attribute pga
WHERE
	pgc.relname = %s
		AND
	pga.attnum > 0
		AND
	pga.attrelid = pgc.oid
ORDER BY pga.attnum"""


# return all attributes and their data types for a given table
query_table_col_defs = """SELECT
	pga.attname as attribute,
	format_type(pga.atttypid, pga.atttypmod) as type
FROM
	pg_class pgc, pg_attribute pga
WHERE
	pgc.relname = %s
		AND
	pga.attnum > 0
		AND
	pga.attrelid = pgc.oid
ORDER BY pga.attnum"""

#==================================================================
# SQL statements for auditing setup script
#------------------------------------------------------------------
#drop_trigger = "DROP TRIGGER %s ON %s"
drop_function = "DROP FUNCTION %s() cascade"

# insert
template_insert_trigger = """CREATE TRIGGER %s
	BEFORE INSERT
	ON %s
	FOR EACH ROW EXECUTE PROCEDURE %s()"""

template_insert_function = """CREATE FUNCTION %s() RETURNS OPAQUE AS '
BEGIN
	NEW.row_version := 0;
	NEW.modified_when := CURRENT_TIMESTAMP;
	NEW.modified_by := CURRENT_USER;
	return NEW;
END;' LANGUAGE 'plpgsql'"""

# update
template_update_trigger = """CREATE TRIGGER %s
	BEFORE UPDATE
	ON %s
	FOR EACH ROW EXECUTE PROCEDURE %s()"""

template_update_function = """CREATE FUNCTION %s() RETURNS OPAQUE AS '
BEGIN
	NEW.row_version := OLD.row_version + 1;
	NEW.modified_when := CURRENT_TIMESTAMP;
	NEW.modified_by := CURRENT_USER;
	INSERT INTO %s (
		orig_version, orig_when, orig_by, orig_tableoid, audit_action,
		%s
	) VALUES (
		OLD.row_version, OLD.modified_when, OLD.modified_by, TG_RELID, TG_OP,
		%s
	);
	return NEW;
END;' LANGUAGE 'plpgsql'"""

# delete
template_delete_trigger = """CREATE TRIGGER %s
	BEFORE DELETE
	ON %s
	FOR EACH ROW EXECUTE PROCEDURE %s()"""

template_delete_function = """CREATE FUNCTION %s() RETURNS OPAQUE AS '
BEGIN
	INSERT INTO %s (
		orig_version, orig_when, orig_by, orig_tableoid, audit_action,
		%s
	) VALUES (
		OLD.row_version, OLD.modified_when, OLD.modified_by, TG_RELID, TG_OP,
		%s
	);
	return OLD;
END;' LANGUAGE 'plpgsql'"""

template_create_audit_trail_table = """create table %s (
%s
) inherits (%s);

grant insert on %s to group "gm-public" """
#------------------------------------------------------------------
def get_columns(aCursor, aTable):
	"""Return column attributes of table
	"""
	if not gmPG.run_query(aCursor, None, query_table_attributes, aTable):
		_log.Log(gmLog.lErr, 'cannot get columns for table [%s]' % aTable)
		return None
	data = aCursor.fetchall()
	rows = []
	for row in data:
		rows.append(row[0])
	return rows
#------------------------------------------------------------------
def get_col_defs(aCursor, aTable):
	if not gmPG.run_query(aCursor, None, query_table_col_defs, aTable):
		_log.Log(gmLog.lErr, 'cannot get column definitions for table [%s]' % aTable)
		return None
	data = aCursor.fetchall()
	col_names = []
	col_type = {}
	for row in data:
		col_names.append(row[0])
		col_type[row[0]] = row[1]
	col_defs = []
	col_defs.append(col_names)
	col_defs.append(col_type)
	return col_defs
#------------------------------------------------------------------
def audit_trail_table_schema(aCursor, table2audit):
	audit_trail_table = '%s%s' % (audit_trail_table_prefix, table2audit)

	# does the audit trail target table exist ?
	cmd = "SELECT exists(select oid FROM pg_class where relname = %s)"
	if not gmPG.run_query(aCursor, None, cmd, audit_trail_table):
		_log.Log(gmLog.lErr, 'cannot check existance of table %s' % audit_trail_table)
		return None
	table_exists = aCursor.fetchone()[0]
	if table_exists:
		return []
	# must create audit trail table
	_log.Log(gmLog.lInfo, 'no audit trail table found for table [%s]' % table2audit)
	_log.Log(gmLog.lInfo, 'trying to auto-create audit trail table [%s]' % audit_trail_table)
	# audit those columns
	audited_col_defs = get_col_defs(aCursor, table2audit)
	cols2skip = get_columns(aCursor, audit_fields_table)
	attribute_list = []
	for col in audited_col_defs[0]:
		if col in cols2skip:
			continue
		attribute_list.append("\t%s %s" % (col, audited_col_defs[1][col]))
	attributes = string.join(attribute_list, ',\n')
	table_def = template_create_audit_trail_table % (audit_trail_table, attributes, audit_trail_parent_table, audit_trail_table)
	return [table_def, '']
#------------------------------------------------------------------
def trigger_schema(aCursor, audited_table):
	audit_trail_table = '%s%s' % (audit_trail_table_prefix, audited_table)

	target_columns = get_columns(aCursor, audited_table)
	columns2skip = get_columns(aCursor, audit_fields_table)
	columns = []
	values = []
	for column in target_columns:
		if column not in columns2skip:
			columns.append(column)
			values.append('OLD.%s' % column)
	columns_clause = string.join(columns, ', ')
	values_clause = string.join(values, ', ')

	schema = []

	# insert
	#  audit triggers are named "zt_*" to make
	#  reasonably sure they are executed last
	func_name_insert = 'ft_ins_%s' % (audited_table)
	trigger_name_insert = 'zt_ins_%s' % (audited_table)

	schema.append(drop_function % func_name_insert)
	schema.append(template_insert_function % (func_name_insert))
	schema.append('')

#	schema.append(drop_trigger % (trigger_name_insert, audited_table))
	schema.append(template_insert_trigger % (trigger_name_insert, audited_table, func_name_insert))
	schema.append('')

	# update
	func_name_update = 'ft_upd_%s' % (audited_table)
	trigger_name_update = 'zt_upd_%s' % (audited_table)

	schema.append(drop_function % func_name_update)
	schema.append(template_update_function % (func_name_update, audit_trail_table, columns_clause, values_clause))
	schema.append('')

#	schema.append(drop_trigger % (trigger_name_update, audited_table))
	schema.append(template_update_trigger % (trigger_name_update, audited_table, func_name_update))
	schema.append('')

	# delete
	func_name_delete = 'ft_del_%s' % (audited_table)
	trigger_name_delete = 'zt_del_%s' % (audited_table)

	schema.append(drop_function % func_name_delete)
	schema.append(template_delete_function % (func_name_delete, audit_trail_table, columns_clause, values_clause))
	schema.append('')

#	schema.append(drop_trigger % (trigger_name_delete, audited_table))
	schema.append(template_delete_trigger % (trigger_name_delete, audited_table, func_name_delete))
	schema.append('')

	# disallow delete/update on auditing table

	return schema
#------------------------------------------------------------------
def create_audit_schema(aCursor):
	# get list of all marked tables
	cmd = "select table_name from audited_tables";
	if gmPG.run_query(aCursor, None, cmd) is None:
		return None
	rows = aCursor.fetchall()
	if len(rows) == 0:
		_log.Log(gmLog.lInfo, 'no tables to audit')
		return None
	tables2audit = []
	for row in rows:
		tables2audit.extend(row)
	_log.Log(gmLog.lData, tables2audit)
	# for each marked table
	schema = []
	for audited_table in tables2audit:
		audit_trail_schema = audit_trail_table_schema(aCursor, audited_table)
		if audit_trail_schema is None:
			_log.Log(gmLog.lErr, 'cannot generate audit trail schema for audited table [%s]' % audited_table)
			return None
		schema.extend(audit_trail_schema)
		if len(audit_trail_schema) != 0:
			schema.append('-- ----------------------------------------------')
		# create corresponding triggers
		schema.extend(trigger_schema(aCursor, audited_table))
		schema.append('-- ----------------------------------------------')
	return schema
#==================================================================
# main
#------------------------------------------------------------------
if __name__ == "__main__" :
	tmp = ''
	try:
		tmp = raw_input("audit trail parent table [%s]: " % audit_trail_parent_table)
	except KeyboardError:
		pass
	if tmp != '':
		audit_trail_parent_table = tmp

	dbpool = gmPG.ConnectionPool()
	conn = dbpool.GetConnection('default')
	curs = conn.cursor()

	schema = create_audit_schema(curs)

	curs.close()
	conn.close()
	dbpool.ReleaseConnection('default')

	if schema is None:
		print "error creating schema"
		sys.exit(-1)

	file = open ('audit-trail-schema.sql', 'wb')
	for line in schema:
		file.write("%s;\n" % line)
	file.close()
#==================================================================
# $Log: gmAuditSchemaGenerator.py,v $
# Revision 1.23  2005-09-13 11:51:06  ncq
# - use "drop function ... cascade;"
#
# Revision 1.22  2004/07/17 21:23:49  ncq
# - run_query now has verbosity argument, so use it
#
# Revision 1.21  2004/06/28 13:31:17  ncq
# - really fix imports, now works again
#
# Revision 1.20  2004/06/28 13:23:20  ncq
# - fix import statements
#
# Revision 1.19  2003/11/05 16:03:02  ncq
# - allow gm-public to insert into log tables
#
# Revision 1.18  2003/10/25 16:58:40  ncq
# - fix audit trigger function generation omitting target column names
#
# Revision 1.17  2003/10/19 12:56:27  ncq
# - streamline
#
# Revision 1.16  2003/10/01 15:43:45  ncq
# - use table audited_tables now instead of inheriting from audit_mark
#
# Revision 1.15  2003/08/17 00:09:37  ncq
# - add auto-generation of missing audit trail tables
# - use that
#
# Revision 1.14  2003/07/05 13:45:49  ncq
# - modify -> modified
#
# Revision 1.13  2003/07/05 12:53:29  ncq
# - actually use ";"s correctly (verified)
#
# Revision 1.12  2003/07/05 12:29:57  ncq
# - just a bit of cleanup
#
# Revision 1.11  2003/07/05 12:26:01  ncq
# - need ; at end of chained SQL statements !
#
# Revision 1.10  2003/06/29 12:41:34  ncq
# - remove excessive quoting
# - check fail of get_children
# - check for audit_mark/audit_fields split compliance
#
# Revision 1.9  2003/06/26 21:44:25  ncq
# - %s; quoting bug, cursor(cmd, args) style
#
# Revision 1.8  2003/06/03 13:48:19  ncq
# - clarify log message
#
# Revision 1.7  2003/05/22 12:54:48  ncq
# - update comments
# - make audit prefix configurable
#
# Revision 1.6  2003/05/17 18:43:24  ncq
# - make triggers zt* so other things (like notify triggers) can easier run afterwards as, say zzt*
#
# Revision 1.5  2003/05/15 10:18:32  ncq
# - name triggers "zzt_*" so they are executed last
# - name trigger function "ft_*"
# - better __doc__
#
# Revision 1.4  2003/05/14 22:03:28  ncq
# - better names for template definitions and lots of other items
# - attributes -> columns
# - check whether target table exists, fail if not
#
# Revision 1.3  2003/05/13 14:55:43  ncq
# - take list of columns to be audited from target audit table,
#   not from source table, this implies that the target table MUST exist
#   prior to running this script
#
# Revision 1.2  2003/05/13 14:39:11  ncq
# - separate triggers/functions for insert/update/delete
# - seems to work now
#
# Revision 1.1  2003/05/12 20:57:19  ncq
# - audit schema generator
#
#
# @change log:
#	12.07.2001 hherb first draft, untested
