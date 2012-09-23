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
__author__ = "Horst Herb, Karsten.Hilbert@gmx.net"
__license__ = "GPL v2 or later"		# (details at http://www.gnu.org)

import sys, os.path, string, logging


from Gnumed.pycommon import gmPG2


_log = logging.getLogger('gm.bootstrapper')

# the audit trail tables start with this prefix
audit_trail_table_prefix = u'log_'
# and inherit from this table
audit_trail_parent_table = u'audit_trail'
# audited tables inherit these fields
audit_fields_table = u'audit_fields'
# audit stuff lives in this schema
audit_schema = u'audit'

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
\unset ON_ERROR_STOP
drop function audit.ft_ins_%s() cascade;
\set ON_ERROR_STOP 1

create FUNCTION audit.ft_ins_%s()
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
\unset ON_ERROR_STOP
drop function audit.ft_upd_%s() cascade;
\set ON_ERROR_STOP 1

create FUNCTION audit.ft_upd_%s()
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
\unset ON_ERROR_STOP
drop function audit.ft_del_%s() cascade;
\set ON_ERROR_STOP 1

create FUNCTION audit.ft_del_%s()
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
) inherits (%s);

comment on column audit.%s.orig_version is
	'the .row_version in the original row before the audited action took place, should be equal to .row_version';

comment on column audit.%s.orig_when is
	'the .modified_when in the original row before the audited action took place, should be equal to .modified_when';

comment on column audit.%s.orig_by is
	'the .modified_by in the original row before the audited action took place, should be equal to .modified_by';

comment on column audit.%s.orig_tableoid is
	'the TG_RELID when the audit trigger was run';
"""

#grant insert on %s.%s to group "gm-public"

#------------------------------------------------------------------
#------------------------------------------------------------------
def audit_trail_table_ddl(aCursor=None, schema='audit', table2audit=None):

	audit_trail_table = '%s%s' % (audit_trail_table_prefix, table2audit)

	# which columns to potentially audit
	cols2potentially_audit = gmPG2.get_col_defs(link_obj = aCursor, schema = schema, table = table2audit)

	# which to skip
	cols2skip = gmPG2.get_col_names(link_obj = aCursor, schema = audit_schema, table = audit_fields_table)

	# which ones to really audit
	cols2really_audit = []
	for col in cols2potentially_audit[0]:
		if col in cols2skip:
			continue
		cols2really_audit.append("\t%s %s" % (col, cols2potentially_audit[1][col]))

	# does the audit trail target table exist ?
	exists = gmPG2.table_exists(aCursor, 'audit', audit_trail_table)
	if exists is None:
		_log.error('cannot check existence of table [audit.%s]' % audit_trail_table)
		return None

	if exists:
		_log.info('audit trail table [audit.%s] already exists' % audit_trail_table)
		# sanity check table structure
		currently_audited_cols = gmPG2.get_col_defs(link_obj = aCursor, schema = u'audit', table = audit_trail_table)
		currently_audited_cols = [ '\t%s %s' % (c, currently_audited_cols[1][c]) for c in currently_audited_cols[0] ]
		for col in cols2really_audit:
			try:
				currently_audited_cols.index(col)
			except ValueError:
				_log.error('table structure incompatible: column ".%s" not found in audit table' % col.strip())
				_log.error('%s.%s:' % (schema, table2audit))
				_log.error('%s' % ','.join(cols2really_audit))
				_log.error('%s.%s:' % (audit_schema, audit_trail_table))
				_log.error('%s' % ','.join(currently_audited_cols))
				return None
		return []

	# must create audit trail table
	_log.info('no audit trail table found for [%s.%s]' % (schema, table2audit))
	_log.info('creating audit trail table [audit.%s]' % audit_trail_table)

	# create audit table DDL
	attributes = ',\n'.join(cols2really_audit)
	table_def = tmpl_create_audit_trail_table % (
		audit_trail_table,
		attributes,
		audit_trail_parent_table,			# FIXME: use audit_schema
		audit_trail_table,
		audit_trail_table,
		audit_trail_table,
		audit_trail_table
	)
	return [table_def, '']
#------------------------------------------------------------------
def trigger_ddl(aCursor='default', schema='audit', audited_table=None):
	audit_trail_table = '%s%s' % (audit_trail_table_prefix, audited_table)

	target_columns = gmPG2.get_col_names(link_obj = aCursor, schema = schema, table = audited_table)
	columns2skip = gmPG2.get_col_names(link_obj = aCursor, schema = audit_schema, table =  audit_fields_table)
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
	ddl.append(tmpl_insert_function % (audited_table, audited_table))
	ddl.append('')
	ddl.append(tmpl_insert_trigger % (audited_table, schema, audited_table, audited_table))
	ddl.append('')

	# update
	ddl.append(tmpl_update_function % (audited_table, audited_table, audit_trail_table, columns_clause, values_clause))
	ddl.append('')
	ddl.append(tmpl_update_trigger % (audited_table, schema, audited_table, audited_table))
	ddl.append('')

	# delete
	ddl.append(tmpl_delete_function % (audited_table, audited_table, audit_trail_table, columns_clause, values_clause))
	ddl.append('')
	ddl.append(tmpl_delete_trigger % (audited_table, schema, audited_table, audited_table))
	ddl.append('')

	# disallow delete/update on auditing table

	return ddl
#------------------------------------------------------------------
def create_audit_ddl(aCursor):
	# get list of all marked tables
	# we could also get the child tables for audit.audit_fields
	# but we would have to potentially parse down several levels
	# of interitance (such as with clin.clin_root_item) to find
	# the actual leaf tables to audit
	cmd = u"select schema, table_name from audit.audited_tables"
	rows, idx = gmPG2.run_ro_queries(link_obj=aCursor, queries = [{'cmd': cmd}])
	if len(rows) == 0:
		_log.info('no tables to audit')
		return None
	_log.debug('the following tables will be audited:')
	_log.debug(rows)
	# for each marked table
	ddl = []
	ddl.append('\set check_function_bodies 1\n')
	ddl.append('set check_function_bodies to on;\n\n')
	for row in rows:

		# sanity check: does table exist ?
		if not gmPG2.table_exists(link_obj = aCursor, schema = row['schema'], table = row['table_name']):
			_log.error('table to audit (%s) does not exist', row)
			return None

		audit_trail_ddl = audit_trail_table_ddl(aCursor=aCursor, schema=row['schema'], table2audit=row['table_name'])
		if audit_trail_ddl is None:
			_log.error('cannot generate audit trail DDL for audited table [%s]' % row['table_name'])
			return None
		ddl.extend(audit_trail_ddl)
		if len(audit_trail_ddl) != 0:
			ddl.append('-- ----------------------------------------------')

		ddl.extend(trigger_ddl(aCursor = aCursor, schema = row['schema'], audited_table = row['table_name']))
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

	conn = gmPG2.get_connection(readonly=False, pooled=False)
	curs = conn.cursor()

	schema = create_audit_ddl(curs)

	curs.close()
	conn.close()

	if schema is None:
		print "error creating schema"
		sys.exit(-1)

	file = open ('audit-trail-schema.sql', 'wb')
	for line in schema:
		file.write("%s;\n" % line)
	file.close()
#==================================================================
