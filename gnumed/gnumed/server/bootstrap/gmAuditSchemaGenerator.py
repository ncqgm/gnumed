"""Automatic GNUmed audit trail generation.

This module creates SQL DDL commands for the audit
trail triggers and functions to be created in the schema "audit".

Theory of operation:

Any table that needs to be audited (all modifications
logged) must be recorded in the table "audit.audited_tables".

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
__version__ = "$Revision: 1.26 $"
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
audit_trail_parent_table = 'audit.audit_trail'
# audited tables inherit these fields
audit_fields_table = 'audit.audit_fields'

#==================================================================
# convenient queries
#------------------------------------------------------------------
# return all tables inheriting from another table
#query_table_descendants = """SELECT relname, oid
#FROM pg_class
#WHERE pg_class.oid in (
#	SELECT inhrelid
#	FROM pg_inherits
#	WHERE inhparent = (
#		SELECT oid
#		FROM pg_class
#		WHERE relname = %s
#	)
#)"""

#==================================================================
# SQL statements for auditing setup script
#------------------------------------------------------------------
# audit triggers are named "zt_*_*" to make
# reasonably sure they are executed last

# insert
tmpl_insert_trigger = """CREATE TRIGGER zt_ins_%s
	BEFORE INSERT ON %s.%s
	FOR EACH ROW EXECUTE PROCEDURE audit.ft_ins_%s()"""

tmpl_insert_function = """
CREATE OR REPLACE FUNCTION audit.ft_ins_%s()
	RETURNS trigger
	LANGUAGE 'plpgsql'
	SECURITY DEFINER
	AS '
BEGIN
	NEW.row_version := 0;
	NEW.modified_when := CURRENT_TIMESTAMP;
	NEW.modified_by := SESSION_USER;
	return NEW;
END;'"""

# update
tmpl_update_trigger = """CREATE TRIGGER zt_upd_%s
	BEFORE UPDATE ON %s.%s
	FOR EACH ROW EXECUTE PROCEDURE audit.ft_upd_%s()"""

tmpl_update_function = """
CREATE OR REPLACE FUNCTION audit.ft_upd_%s()
	RETURNS trigger
	LANGUAGE 'plpgsql'
	SECURITY DEFINER
	AS '
BEGIN
	NEW.row_version := OLD.row_version + 1;
	NEW.modified_when := CURRENT_TIMESTAMP;
	NEW.modified_by := SESSION_USER;
	INSERT INTO audit.%s (
		orig_version, orig_when, orig_by, orig_tableoid, audit_action,
		%s
	) VALUES (
		OLD.row_version, OLD.modified_when, OLD.modified_by, TG_RELID, TG_OP,
		%s
	);
	return NEW;
END;'"""

# delete
tmpl_delete_trigger = """
CREATE TRIGGER zt_del_%s
	BEFORE DELETE ON %s.%s
	FOR EACH ROW EXECUTE PROCEDURE audit.ft_del_%s()"""

tmpl_delete_function = """
CREATE OR REPLACE FUNCTION audit.ft_del_%s()
	RETURNS trigger
	LANGUAGE 'plpgsql'
	SECURITY DEFINER
	AS '
BEGIN
	INSERT INTO audit.%s (
		orig_version, orig_when, orig_by, orig_tableoid, audit_action,
		%s
	) VALUES (
		OLD.row_version, OLD.modified_when, OLD.modified_by, TG_RELID, TG_OP,
		%s
	);
	return OLD;
END;'"""

tmpl_create_audit_trail_table = """
create table audit.%s (
%s
) inherits (%s);"""

#grant insert on %s.%s to group "gm-public"

#------------------------------------------------------------------
#------------------------------------------------------------------
def audit_trail_table_ddl(aCursor='default', schema='audit', table2audit=None):

	audit_trail_table = '%s%s' % (audit_trail_table_prefix, table2audit)

	# does the audit trail target table exist ?
	exists = gmPG.table_exists(aCursor, schema, audit_trail_table)
	if exists is None:
		_log.Log(gmLog.lErr, 'cannot check existance of table %s.%s' % (schema, audit_trail_table))
		return None
	if exists:
		return []
	# must create audit trail table
	_log.Log(gmLog.lInfo, 'no audit trail table found for [%s.%s]' % (schema, table2audit))
	_log.Log(gmLog.lInfo, 'creating audit trail table [%s.%s]' % (schema, audit_trail_table))

	# which columns to potentially audit
	audited_col_defs = gmPG.get_col_defs(source = aCursor, schema = schema, table = table2audit)
	# which to skip
	cols2skip = gmPG.get_col_names(source = aCursor, schema = schema, table = audit_fields_table)
	attribute_list = []
	# which ones to really audit
	for col in audited_col_defs[0]:
		if col in cols2skip:
			continue
		attribute_list.append("\t%s %s" % (col, audited_col_defs[1][col]))
	attributes = string.join(attribute_list, ',\n')

	# create audit table DDL
	table_def = tmpl_create_audit_trail_table % (
		audit_trail_table,
		attributes,
		audit_trail_parent_table
	)
	return [table_def, '']
#		schema,
#		audit_trail_table
#------------------------------------------------------------------
def trigger_ddl(aCursor='default', schema='audit', audited_table=None):
	audit_trail_table = '%s%s' % (audit_trail_table_prefix, audited_table)

	target_columns = gmPG.get_col_names(source = aCursor, schema = schema, table = audited_table)
	columns2skip = gmPG.get_col_names(source = aCursor, schema = schema, table =  audit_fields_table)
	columns = []
	values = []
	for column in target_columns:
		if column not in columns2skip:
			columns.append(column)
			values.append('OLD.%s' % column)
	columns_clause = string.join(columns, ', ')
	values_clause = string.join(values, ', ')

	ddl = []

	# insert
	ddl.append(tmpl_insert_function % audited_table)
	ddl.append('')
	ddl.append(tmpl_insert_trigger % (audited_table, schema, audited_table, audited_table))
	ddl.append('')

	# update
	ddl.append(tmpl_update_function % (audited_table, audit_trail_table, columns_clause, values_clause))
	ddl.append('')
	ddl.append(tmpl_update_trigger % (audited_table, schema, audited_table, audited_table))
	ddl.append('')

	# delete
	ddl.append(tmpl_delete_function % (audited_table, audit_trail_table, columns_clause, values_clause))
	ddl.append('')
	ddl.append(tmpl_delete_trigger % (audited_table, schema, audited_table, audited_table))
	ddl.append('')

	# disallow delete/update on auditing table

	return ddl
#------------------------------------------------------------------
def create_audit_ddl(aCursor):
	# get list of all marked tables
	cmd = "select schema, table_name from audit.audited_tables";
	if gmPG.run_query(aCursor, None, cmd) is None:
		return None
	rows = aCursor.fetchall()
	if len(rows) == 0:
		_log.Log(gmLog.lInfo, 'no tables to audit')
		return None
	_log.Log(gmLog.lData, rows)
	# for each marked table
	ddl = []
	for row in rows:
		audit_trail_ddl = audit_trail_table_ddl(aCursor=aCursor, schema=row[0], table2audit=row[1])
		if audit_trail_ddl is None:
			_log.Log(gmLog.lErr, 'cannot generate audit trail DDL for audited table [%s]' % audited_table)
			return None
		ddl.extend(audit_trail_ddl)
		if len(audit_trail_ddl) != 0:
			ddl.append('-- ----------------------------------------------')
		# create corresponding triggers
		ddl.extend(trigger_ddl(aCursor = aCursor, schema = row[0], audited_table = row[1]))
		ddl.append('-- ----------------------------------------------')
	return ddl
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

	schema = create_audit_ddl(curs)

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
# Revision 1.26  2006-05-24 12:10:46  ncq
# - use session_user
#
# Revision 1.25  2006/01/05 16:07:11  ncq
# - generate audit trail tables and functions in schema "audit"
# - adjust configuration
# - audit trigger functions now "security definer" (== gm-dbo)
# - grant SELECT only to non-gm-dbo users
# - return language_handler not opaque from language call handler functions
#
# Revision 1.24  2005/12/04 09:34:44  ncq
# - make fit for schema support
# - move some queries to gmPG
# - improve DDL templates (use or replace on functions)
#
# Revision 1.23  2005/09/13 11:51:06  ncq
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
