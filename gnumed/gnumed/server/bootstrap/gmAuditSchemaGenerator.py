"""Automatic GnuMed audit trail generation.

This module creates SQL DDL commands for the audit
trail triggers and functions.

Theory of operation:

Any table that needs to be audited (all modifications
logged) must be marked as such by inheriting from a given
parent table.

This script finds all descendants of that parent table and
creates the triggers and functions neccessary to establish
the audit trail. The audit trail tables must have been
created previously but need not contain all columns of the
audited table. Do not put any constraints on the audit
trail tables except for "not null" on those columns that
cannot be null in the audited table.
"""
#==================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/bootstrap/gmAuditSchemaGenerator.py,v $
__version__ = "$Revision: 1.6 $"
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
#	format_type(a.atttypid, a.atttypmod)
query_table_attributes = """SELECT
	pga.attname
FROM
	pg_class pgc, pg_attribute pga
WHERE
	pgc.relname = '%s'
		AND
	pga.attnum > 0
		AND
	pga.attrelid = pgc.oid
ORDER BY pga.attnum;"""

query_pkey_name = """SELECT
	pga.attname
FROM
	(pg_attribute pga inner join pg_index pgi on (pga.attrelid=pgi.indrelid))
WHERE
	pga.attnum=pgi.indkey[0]
		and
	pgi.indisprimary is true
		and
	pga.attrelid=(SELECT oid FROM pg_class WHERE relname = '%s');"""


drop_trigger = "DROP TRIGGER %s ON %s;"
drop_function = "DROP FUNCTION %s();"

template_insert_trigger = """CREATE TRIGGER %s
	BEFORE INSERT
	ON %s
	FOR EACH ROW EXECUTE PROCEDURE %s();"""

template_update_trigger = """CREATE TRIGGER %s
	BEFORE UPDATE
	ON %s
	FOR EACH ROW EXECUTE PROCEDURE %s();"""

template_delete_trigger = """CREATE TRIGGER %s
	BEFORE DELETE
	ON %s
	FOR EACH ROW EXECUTE PROCEDURE %s();"""

template_insert_function = """CREATE FUNCTION %s() RETURNS OPAQUE AS '
BEGIN
	NEW.row_version := 0;
	NEW.modify_when := CURRENT_TIMESTAMP;
	NEW.modify_by := CURRENT_USER;
	return NEW;
END;' LANGUAGE 'plpgsql';"""

template_update_function = """CREATE FUNCTION %s() RETURNS OPAQUE AS '
BEGIN
	NEW.row_version := OLD.row_version + 1;
	NEW.modify_when := CURRENT_TIMESTAMP;
	NEW.modify_by := CURRENT_USER;
	INSERT INTO %s (
		orig_version, orig_when, orig_by, orig_tableoid, audit_action,
		%s
	) VALUES (
		OLD.row_version, OLD.modify_when, OLD.modify_by, TG_RELID, TG_OP,
		%s
	);
	return NEW;
END;' LANGUAGE 'plpgsql';"""

template_delete_function = """CREATE FUNCTION %s() RETURNS OPAQUE AS '
BEGIN
	INSERT INTO %s (
		orig_version, orig_when, orig_by, orig_tableoid, audit_action,
		%s
	) VALUES (
		OLD.row_version, OLD.modify_when, OLD.modify_by, TG_RELID, TG_OP,
		%s
	);
	return OLD;
END;' LANGUAGE 'plpgsql';"""

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
def get_columns(aCursor, aTable):
	"""Return column attributes of table
	"""
	cmd = query_table_attributes % aTable
	if not gmPG.run_query(aCursor, cmd):
		_log.Log(gmLog.lErr, 'cannot get columns for table [%s]' % aTable)
		return None
	data = aCursor.fetchall()
	rows = []
	for row in data:
		rows.append(row[0])
	return rows
#------------------------------------------------------------------
def audit_trail_table_exists(aCursor, table2audit, audit_prefix = 'log_'):
	audit_trail_table = '%s%s' % (audit_prefix, table2audit)

	# does the audit trail target table exist ?
	cmd = "SELECT exists(select oid FROM pg_class where relname = '%s');" % audit_trail_table
	if not gmPG.run_query(aCursor, cmd):
		_log.Log(gmLog.lErr, 'cannot check existance of table %s' % audit_trail_table)
		return None
	result = aCursor.fetchone()
	return result[0]
#------------------------------------------------------------------
def trigger_schema(aCursor, audited_table, audit_parent_table = 'audit_log', audit_prefix = 'log_'):
	audit_trail_table = '%s%s' % (audit_prefix, audited_table)

	target_columns = get_columns(aCursor, audit_trail_table)
	columns2skip = get_columns(aCursor, audit_parent_table)
	columns = []
	values = []
	for column in target_columns:
		if column in columns2skip:
			continue
		columns.append(column)
		values.append('OLD.%s' % column)
	columns_clause = string.join(columns, ', ')
	values_clause = string.join(values, ', ')

	schema = []

	# insert
	#  audit triggers are named "zzt_*" to make
	#  reasonably sure they are executed last
	func_name_insert = 'ft_ins_%s' % (audited_table)
	trigger_name_insert = 'zt_ins_%s' % (audited_table)

	schema.append(drop_function % func_name_insert)
	schema.append(template_insert_function % (func_name_insert))
	schema.append('')

	schema.append(drop_trigger % (trigger_name_insert, audited_table))
	schema.append(template_insert_trigger % (trigger_name_insert, audited_table, func_name_insert))
	schema.append('')

	# update
	func_name_update = 'ft_upd_%s' % (audited_table)
	trigger_name_update = 'zt_upd_%s' % (audited_table)

	schema.append(drop_function % func_name_update)
	schema.append(template_update_function % (func_name_update, audit_trail_table, columns_clause, values_clause))
	schema.append('')

	schema.append(drop_trigger % (trigger_name_update, audited_table))
	schema.append(template_update_trigger % (trigger_name_update, audited_table, func_name_update))
	schema.append('')

	# delete
	func_name_delete = 'ft_del_%s' % (audited_table)
	trigger_name_delete = 'zt_del_%s' % (audited_table)

	schema.append(drop_function % func_name_delete)
	schema.append(template_delete_function % (func_name_delete, audit_trail_table, columns_clause, values_clause))
	schema.append('')

	schema.append(drop_trigger % (trigger_name_delete, audited_table))
	schema.append(template_delete_trigger % (trigger_name_delete, audited_table, func_name_delete))
	schema.append('')

	# disallow delete/update on auditing table

	return schema
#------------------------------------------------------------------
def create_audit_schema(aCursor, audit_marker_table = 'audit_mark', audit_parent_table = 'audit_log'):
	# get list of all derived tables
	tables2audit = get_children(aCursor, audit_marker_table)

	# for each derived table
	schema = []
	for audited_table in tables2audit:
		# fail if corresponding audit trail table does not exist
		if not audit_trail_table_exists(aCursor, audited_table[0]):
			return None
		# create corresponding triggers
		schema.extend(trigger_schema(aCursor, audited_table[0], audit_parent_table))
		schema.append('-- ----------------------------------------------')
	return schema
#==================================================================
# main
#------------------------------------------------------------------
if __name__ == "__main__" :
	audit_marker_table = raw_input("name of audit marker table   : ")
	audit_parent_table = raw_input("name of auditing parent table: ")

	dbpool = gmPG.ConnectionPool()
	conn = dbpool.GetConnection('default')
	curs = conn.cursor()

	schema = create_audit_schema(curs, audit_marker_table)

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
# Revision 1.6  2003-05-17 18:43:24  ncq
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
