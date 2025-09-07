"""Automatic GNUmed audit trail generation.

This module creates SQL DDL commands for the audit
trail triggers and functions to be created in the schema "audit".

Theory of operation:

Any table that needs to be audited (all modifications
logged) must be recorded in the table "audit.audited_tables".

This script creates the triggers, functions and tables
necessary to establish the audit trail. Some or all
audit trail tables may have been created previously but
need not contain all columns of the audited table. Do not
put any constraints on the audit trail tables except for
"not null" on those columns that cannot be null in the
audited table.
"""
#==================================================================
__author__ = "Horst Herb, Karsten.Hilbert@gmx.net"
__license__ = "GPL v2 or later"		# (details at https://www.gnu.org)

import sys
import logging


from Gnumed.pycommon import gmPG2


_log = logging.getLogger('gm.bootstrapper')


LOG_TABLE_PREFIX = 'log_'						# the audit trail tables start with this prefix
AUDIT_TRAIL_PARENT_TABLE = 'audit_trail'		# and inherit from this table
AUDIT_FIELDS_TABLE = 'audit_fields'				# audited tables inherit these fields
AUDIT_SCHEMA = 'audit'							# audit stuff lives in this schema

#==================================================================
# SQL statements for auditing setup script
#------------------------------------------------------------------
# audit triggers are named "zt_*_*" to make
# reasonably sure they are executed last

# insert
SQL_TEMPLATE_INSERT = """DROP FUNCTION IF EXISTS audit.ft_ins_%(src_tbl)s() cascade;

CREATE FUNCTION audit.ft_ins_%(src_tbl)s()
	RETURNS trigger
	LANGUAGE 'plpgsql'
	SECURITY DEFINER
	AS '
DECLARE
	_is_allowed_inserter boolean;
BEGIN
	-- is the session user allowed to insert data ?
	SELECT gm.account_is_dbowner_or_staff(SESSION_USER) INTO STRICT _is_allowed_inserter;
	IF _is_allowed_inserter IS FALSE THEN
		RAISE EXCEPTION
			''INSERT: gm.account_is_dbowner_or_staff(NAME): <%%> is neither database owner, nor <postgres>, nor on staff'', SESSION_USER
			USING ERRCODE = ''integrity_constraint_violation''
		;
		return NEW;
	END IF;

	NEW.row_version := 0;
	NEW.modified_when := CURRENT_TIMESTAMP;
	NEW.modified_by := SESSION_USER;
	return NEW;
END;';

CREATE TRIGGER zt_ins_%(src_tbl)s
	BEFORE INSERT ON %(src_schema)s.%(src_tbl)s
	FOR EACH ROW EXECUTE PROCEDURE audit.ft_ins_%(src_tbl)s();
"""

SQL_TEMPLATE_INSERT_NO_INSERTER_CHECK = """DROP FUNCTION IF EXISTS audit.ft_ins_%(src_tbl)s() cascade;

CREATE FUNCTION audit.ft_ins_%(src_tbl)s()
	RETURNS trigger
	LANGUAGE 'plpgsql'
	SECURITY DEFINER
	AS '
BEGIN
	NEW.row_version := 0;
	NEW.modified_when := CURRENT_TIMESTAMP;
	NEW.modified_by := SESSION_USER;
	return NEW;
END;';

CREATE TRIGGER zt_ins_%(src_tbl)s
	BEFORE INSERT ON %(src_schema)s.%(src_tbl)s
	FOR EACH ROW EXECUTE PROCEDURE audit.ft_ins_%(src_tbl)s();
"""

# update
SQL_TEMPLATE_UPDATE = """DROP FUNCTION IF EXISTS audit.ft_upd_%(src_tbl)s() cascade;

CREATE FUNCTION audit.ft_upd_%(src_tbl)s()
	RETURNS trigger
	LANGUAGE 'plpgsql'
	SECURITY DEFINER
	AS '
DECLARE
	_is_allowed_updater boolean;
BEGIN
	-- is the session user allowed to update data ?
	SELECT gm.account_is_dbowner_or_staff(SESSION_USER) INTO STRICT _is_allowed_updater;
	IF _is_allowed_updater IS FALSE THEN
		RAISE EXCEPTION
			''UPDATE: gm.account_is_dbowner_or_staff(NAME): <%%> is neither database owner, nor <postgres>, nor on staff'', SESSION_USER
			USING ERRCODE = ''integrity_constraint_violation''
		;
		return NEW;
	END IF;

	NEW.row_version := OLD.row_version + 1;
	NEW.modified_when := CURRENT_TIMESTAMP;
	NEW.modified_by := SESSION_USER;
	INSERT INTO audit.%(log_tbl)s (
		orig_version, orig_when, orig_by, orig_tableoid, audit_action,
		%(cols_clause)s
	) VALUES (
		OLD.row_version, OLD.modified_when, OLD.modified_by, TG_RELID, TG_OP,
		%(vals_clause)s
	);
	return NEW;
END;';

CREATE TRIGGER zt_upd_%(src_tbl)s
	BEFORE UPDATE ON %(src_schema)s.%(src_tbl)s
	FOR EACH ROW EXECUTE PROCEDURE audit.ft_upd_%(src_tbl)s();
"""

SQL_TEMPLATE_UPDATE_NO_UPDATER_CHECK = """DROP FUNCTION IF EXISTS audit.ft_upd_%(src_tbl)s() cascade;

CREATE FUNCTION audit.ft_upd_%(src_tbl)s()
	RETURNS trigger
	LANGUAGE 'plpgsql'
	SECURITY DEFINER
	AS '
BEGIN
	NEW.row_version := OLD.row_version + 1;
	NEW.modified_when := CURRENT_TIMESTAMP;
	NEW.modified_by := SESSION_USER;
	INSERT INTO audit.%(log_tbl)s (
		orig_version, orig_when, orig_by, orig_tableoid, audit_action,
		%(cols_clause)s
	) VALUES (
		OLD.row_version, OLD.modified_when, OLD.modified_by, TG_RELID, TG_OP,
		%(vals_clause)s
	);
	return NEW;
END;';

CREATE TRIGGER zt_upd_%(src_tbl)s
	BEFORE UPDATE ON %(src_schema)s.%(src_tbl)s
	FOR EACH ROW EXECUTE PROCEDURE audit.ft_upd_%(src_tbl)s();
"""

# delete
SQL_TEMPLATE_DELETE = """DROP FUNCTION IF EXISTS audit.ft_del_%(src_tbl)s() cascade;

CREATE FUNCTION audit.ft_del_%(src_tbl)s()
	RETURNS trigger
	LANGUAGE 'plpgsql'
	SECURITY DEFINER
	AS '
DECLARE
	_is_allowed_deleter boolean;
BEGIN
	-- is the session user allowed to delete data ?
	SELECT gm.account_is_dbowner_or_staff(SESSION_USER) INTO STRICT _is_allowed_deleter;
	IF _is_allowed_deleter IS FALSE THEN
		RAISE EXCEPTION
			''DELETE: gm.account_is_dbowner_or_staff(NAME): <%%> is neither database owner, nor <postgres>, nor on staff'', SESSION_USER
			USING ERRCODE = ''integrity_constraint_violation''
		;
		return OLD;
	END IF;

	INSERT INTO audit.%(log_tbl)s (
		orig_version, orig_when, orig_by, orig_tableoid, audit_action,
		%(cols_clause)s
	) VALUES (
		OLD.row_version, OLD.modified_when, OLD.modified_by, TG_RELID, TG_OP,
		%(vals_clause)s
	);
	return OLD;
END;';

CREATE TRIGGER zt_del_%(src_tbl)s
	BEFORE DELETE ON %(src_schema)s.%(src_tbl)s
	FOR EACH ROW EXECUTE PROCEDURE audit.ft_del_%(src_tbl)s();
"""

SQL_TEMPLATE_DELETE_NO_DELETER_CHECK = """DROP FUNCTION IF EXISTS audit.ft_del_%(src_tbl)s() cascade;

CREATE FUNCTION audit.ft_del_%(src_tbl)s()
	RETURNS trigger
	LANGUAGE 'plpgsql'
	SECURITY DEFINER
	AS '
BEGIN
	INSERT INTO audit.%(log_tbl)s (
		orig_version, orig_when, orig_by, orig_tableoid, audit_action,
		%(cols_clause)s
	) VALUES (
		OLD.row_version, OLD.modified_when, OLD.modified_by, TG_RELID, TG_OP,
		%(vals_clause)s
	);
	return OLD;
END;';

CREATE TRIGGER zt_del_%(src_tbl)s
	BEFORE DELETE ON %(src_schema)s.%(src_tbl)s
	FOR EACH ROW EXECUTE PROCEDURE audit.ft_del_%(src_tbl)s();
"""

# we cannot do this because NOT VALID only applies to the time when
# we add the constraint, the FK would still be enforced during later
# INSERTs/UPDATEs
#SQL_TEMPLATE_FK_MODIFIED_BY = """ALTER TABLE %(src_schema)s.%(src_tbl)s
#	DROP CONSTRAINT IF EXISTS fk_%(src_schema)s_%(src_tbl)s_fk_modified_by CASCADE;
#
#-- this is set NOT VALID because it only serves to tell pg_dump
#-- to dump dem.staff before other tables such that we do not run
#-- into trouble with checking gm.is_dbowner_or_staff(SESSION_USER)
#ALTER TABLE %(src_schema)s.%(src_tbl)s
#	ADD CONSTRAINT fk_%(src_schema)s_%(src_tbl)s_fk_modified_by
#		FOREIGN KEY (modified_by)
#		REFERENCES dem.staff(db_user)
#		ON UPDATE RESTRICT
#		ON DELETE RESTRICT
#	NOT VALID;"""
#
#SQL_TEMPLATE_DEM_STAFF_FK = """
#ALTER TABLE dem.staff
#	DROP CONSTRAINT IF EXISTS fk_dem_staff_fk_modified_by CASCADE;
#"""

SQL_TEMPLATE_CREATE_AUDIT_TRAIL_TABLE = """
create table %(log_schema)s.%(log_tbl)s (
	%(log_cols)s
) inherits (%(log_schema)s.%(log_base_tbl)s);

COMMENT ON COLUMN %(log_schema)s.%(log_tbl)s.orig_version is
	'the .row_version in the original row before the audited action took place, should be equal to .row_version';

COMMENT ON COLUMN %(log_schema)s.%(log_tbl)s.orig_when is
	'the .modified_when in the original row before the audited action took place, should be equal to .modified_when';

COMMENT ON COLUMN %(log_schema)s.%(log_tbl)s.orig_by is
	'the .modified_by in the original row before the audited action took place, should be equal to .modified_by';

COMMENT ON COLUMN %(log_schema)s.%(log_tbl)s.orig_tableoid is
	'the TG_RELID when the audit trigger was run';
"""

#grant insert on %s.%s to group "gm-public"

#------------------------------------------------------------------
#------------------------------------------------------------------
def audit_trail_table_ddl(aCursor=None, schema=None, table2audit=None):

	audit_trail_table = '%s%s' % (LOG_TABLE_PREFIX, table2audit)

	# which columns to potentially audit
	cols2potentially_audit = gmPG2.get_col_defs(link_obj = aCursor, schema = schema, table = table2audit)

	# which to skip
	cols2skip = gmPG2.get_col_names(link_obj = aCursor, schema = AUDIT_SCHEMA, table = AUDIT_FIELDS_TABLE)

	# which ones to really audit
	cols2really_audit = []
	for col in cols2potentially_audit[0]:
		if col in cols2skip:
			continue
		cols2really_audit.append("\t%s %s" % (col, cols2potentially_audit[1][col]))

	# does the audit trail target table exist ?
	exists = gmPG2.table_exists(aCursor, AUDIT_SCHEMA, audit_trail_table)
	if exists is None:
		_log.error('cannot check existence of table [audit.%s]' % audit_trail_table)
		return None

	if exists:
		_log.info('audit trail table [audit.%s] already exists' % audit_trail_table)
		# sanity check table structure
		currently_audited_cols = gmPG2.get_col_defs(link_obj = aCursor, schema = AUDIT_SCHEMA, table = audit_trail_table)
		currently_audited_cols = [ '\t%s %s' % (c, currently_audited_cols[1][c]) for c in currently_audited_cols[0] ]
		for col in cols2really_audit:
			try:
				currently_audited_cols.index(col)
			except ValueError:
				_log.error('table structure incompatible: column ".%s" not found in audit table' % col.strip())
				_log.error('%s.%s:' % (schema, table2audit))
				_log.error('%s' % ','.join(cols2really_audit))
				_log.error('%s.%s:' % (AUDIT_SCHEMA, audit_trail_table))
				_log.error('%s' % ','.join(currently_audited_cols))
				return None
		return []

	# must create audit trail table
	_log.info('no audit trail table found for [%s.%s]' % (schema, table2audit))
	_log.info('creating audit trail table [audit.%s]' % audit_trail_table)

	args = {
		'log_schema': AUDIT_SCHEMA,
		'log_base_tbl': AUDIT_TRAIL_PARENT_TABLE,
		'log_tbl': audit_trail_table,
		'log_cols': ',\n	'.join(cols2really_audit)
	}
	return [SQL_TEMPLATE_CREATE_AUDIT_TRAIL_TABLE % args, '']

#------------------------------------------------------------------
def trigger_ddl(aCursor='default', schema=AUDIT_SCHEMA, audited_table=None):

	target_columns = gmPG2.get_col_names(link_obj = aCursor, schema = schema, table = audited_table)
	columns2skip = gmPG2.get_col_names(link_obj = aCursor, schema = AUDIT_SCHEMA, table =  AUDIT_FIELDS_TABLE)
	columns = []
	values = []
	for column in target_columns:
		if column not in columns2skip:
			columns.append(column)
			values.append('OLD.%s' % column)

	args = {
		'src_tbl': audited_table,
		'src_schema': schema,
		'log_tbl': '%s%s' % (LOG_TABLE_PREFIX, audited_table),
		'cols_clause': ', '.join(columns),
		'vals_clause': ', '.join(values)
	}

	modified_by_func_exists = gmPG2.function_exists(link_obj = aCursor, schema = 'gm', function = 'account_is_dbowner_or_staff')

	ddl = []
	if modified_by_func_exists:
		ddl.append(SQL_TEMPLATE_INSERT % args)
		ddl.append('')
		ddl.append(SQL_TEMPLATE_UPDATE % args)
		ddl.append('')
		ddl.append(SQL_TEMPLATE_DELETE % args)
		#ddl.append('')
		#ddl.append(SQL_TEMPLATE_FK_MODIFIED_BY % args)
	else:
		# the *_NO_*_CHECK variants are needed for pre-v21 databases
		# where gm.account_is_dbowner_or_staff() doesn't exist yet
		ddl.append(SQL_TEMPLATE_INSERT_NO_INSERTER_CHECK % args)
		ddl.append('')
		ddl.append(SQL_TEMPLATE_UPDATE_NO_UPDATER_CHECK % args)
		ddl.append('')
		ddl.append(SQL_TEMPLATE_DELETE_NO_DELETER_CHECK % args)
	ddl.append('')

	return ddl

#------------------------------------------------------------------
def create_audit_ddl(aCursor):
	# get list of all marked tables
	# we could also get the child tables for audit.audit_fields
	# but we would have to potentially parse down several levels
	# of interitance (such as with clin.clin_root_item) to find
	# the actual leaf table to audit
	cmd = "select schema, table_name from audit.audited_tables"
	rows = gmPG2.run_ro_queries(link_obj = aCursor, queries = [{'sql': cmd}])
	if len(rows) == 0:
		_log.info('no tables to audit')
		return None
	_log.debug('the following tables will be audited:')
	_log.debug(rows)
	ddl = []
	ddl.append('\set check_function_bodies 1\n')
	ddl.append('set check_function_bodies to on;\n\n')

	# for each marked table
	for row in rows:

		if not gmPG2.table_exists(link_obj = aCursor, schema = row['schema'], table = row['table_name']):
			_log.error('table to audit (%s) does not exist', row)
			return None

		# create log table if necessary
		audit_trail_ddl = audit_trail_table_ddl(aCursor = aCursor, schema = row['schema'], table2audit = row['table_name'])
		if audit_trail_ddl is None:
			_log.error('cannot generate audit trail DDL for audited table [%s]' % row['table_name'])
			return None
		ddl.extend(audit_trail_ddl)
		if len(audit_trail_ddl) != 0:
			ddl.append('-- ----------------------------------------------')

		# create functions and triggers on log table
		ddl.extend(trigger_ddl(aCursor = aCursor, schema = row['schema'], audited_table = row['table_name']))
		ddl.append('-- ----------------------------------------------')

	#ddl.append(SQL_TEMPLATE_DEM_STAFF_FK)

	return ddl

#==================================================================
# main
#------------------------------------------------------------------
if __name__ == "__main__" :
	tmp = ''
	try:
		tmp = input("audit trail parent table [%s]: " % AUDIT_TRAIL_PARENT_TABLE)
	except KeyboardInterrupt:
		pass
	if tmp != '':
		AUDIT_TRAIL_PARENT_TABLE = tmp

	conn = gmPG2.get_connection(readonly=False, pooled=False)
	curs = conn.cursor()

	schema = create_audit_ddl(curs)

	curs.close()
	conn.close()

	if schema is None:
		print("error creating schema")
		sys.exit(-1)

	f = open('audit-trail-schema.sql', mode = 'wb', encoding = 'utf8')
	for line in schema:
		f.write("%s;\n" % line)
	f.close()
