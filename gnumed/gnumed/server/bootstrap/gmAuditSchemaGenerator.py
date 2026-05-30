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


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmPG2
import gmAuditSchemaDefs

_log = logging.getLogger('gm.bootstrapper')

#==================================================================
# SQL statements for auditing setup script
#------------------------------------------------------------------
def audit_trail_table_ddl(aCursor=None, schema=None, table2audit=None):

	audit_trail_table = '%s%s' % (gmAuditSchemaDefs.LOG_TABLE_PREFIX, table2audit)
	# which columns to potentially audit
	cols2potentially_audit = gmPG2.get_col_defs(link_obj = aCursor, schema = schema, table = table2audit)
	# which to skip
	cols2skip = gmPG2.get_col_names(link_obj = aCursor, schema = gmAuditSchemaDefs.AUDIT_SCHEMA, table = gmAuditSchemaDefs.AUDIT_FIELDS_TABLE)
	# which ones to really audit
	cols2really_audit = []
	for col in cols2potentially_audit[0]:
		if col in cols2skip:
			continue
		cols2really_audit.append("\t%s %s" % (col, cols2potentially_audit[1][col]))
	# does the audit trail target table exist ?
	exists = gmPG2.table_exists(aCursor, gmAuditSchemaDefs.AUDIT_SCHEMA, audit_trail_table)
	if exists is None:
		_log.error('cannot check existence of table [audit.%s]' % audit_trail_table)
		return None

	if exists:
		_log.info('audit trail table [audit.%s] already exists' % audit_trail_table)
		# sanity check table structure
		col_defs = gmPG2.get_col_defs(link_obj = aCursor, schema = gmAuditSchemaDefs.AUDIT_SCHEMA, table = audit_trail_table)
		col_names = col_defs[0]
		col_types = col_defs[1]
		currently_audited_cols = [ '\t%s %s' % (col_name, col_types[col_name]) for col_name in col_names ]
		for col in cols2really_audit:
			try:
				currently_audited_cols.index(col)
			except ValueError:
				_log.error('table structure incompatible: column ".%s" not found in audit table' % col.strip())
				_log.error('%s.%s:' % (schema, table2audit))
				_log.error('%s' % ','.join(cols2really_audit))
				_log.error('%s.%s:' % (gmAuditSchemaDefs.AUDIT_SCHEMA, audit_trail_table))
				_log.error('%s' % ','.join(currently_audited_cols))
				return None

		return ''

	# must create audit trail table
	_log.info('no audit trail table found for [%s.%s]' % (schema, table2audit))
	_log.info('creating audit trail table [audit.%s]' % audit_trail_table)
	args = {
		'log_schema': gmAuditSchemaDefs.AUDIT_SCHEMA,
		'log_base_tbl': gmAuditSchemaDefs.AUDIT_TRAIL_PARENT_TABLE,
		'log_tbl': audit_trail_table,
		'log_cols': ',\n	'.join(cols2really_audit)
	}
	return gmAuditSchemaDefs.SQL_TEMPLATE_CREATE_AUDIT_TRAIL_TABLE % args

#------------------------------------------------------------------
def trigger_ddl(aCursor='default', schema=gmAuditSchemaDefs.AUDIT_SCHEMA, audited_table=None):

	target_columns = gmPG2.get_col_names(link_obj = aCursor, schema = schema, table = audited_table)
	columns2skip = gmPG2.get_col_names(link_obj = aCursor, schema = gmAuditSchemaDefs.AUDIT_SCHEMA, table = gmAuditSchemaDefs.AUDIT_FIELDS_TABLE)
	columns = []
	values = []
	for column in target_columns:
		if column not in columns2skip:
			columns.append(column)
			values.append('OLD.%s' % column)
	args = {
		'src_tbl': audited_table,
		'src_schema': schema,
		'log_tbl': '%s%s' % (gmAuditSchemaDefs.LOG_TABLE_PREFIX, audited_table),
		'cols_clause': ', '.join(columns),
		'vals_clause': ', '.join(values)
	}
	columns_in_log_base_table = gmPG2.get_col_names(link_obj = aCursor, schema = gmAuditSchemaDefs.AUDIT_SCHEMA, table = gmAuditSchemaDefs.AUDIT_TRAIL_PARENT_TABLE)
	# added in v23:
	v23 = 'src_row_pk_audit' in columns_in_log_base_table
	v21 = gmPG2.function_exists(link_obj = aCursor, schema = 'gm', function = 'account_is_dbowner_or_staff')
	ddl = []
	if v23:
		_log.info('generating v23 triggers')
		ddl.append('-- creating v23 audit schema script')
		ddl.append(gmAuditSchemaDefs.SQL_TEMPLATE_INSERT_v23 % args)
		ddl.append('')
		ddl.append(gmAuditSchemaDefs.SQL_TEMPLATE_UPDATE_v23 % args)
		ddl.append('')
		ddl.append(gmAuditSchemaDefs.SQL_TEMPLATE_DELETE_v23 % args)
		ddl.append(gmAuditSchemaDefs.SQL_TEMPLATE__index__pk_audit__row_version % args)
	elif v21:
		_log.info('generating v21/22 triggers')
		ddl.append('-- creating v21/v22 audit schema script')
		ddl.append(gmAuditSchemaDefs.SQL_TEMPLATE_INSERT_v21 % args)
		ddl.append('')
		ddl.append(gmAuditSchemaDefs.SQL_TEMPLATE_UPDATE_v21 % args)
		ddl.append('')
		ddl.append(gmAuditSchemaDefs.SQL_TEMPLATE_DELETE_v21 % args)
	else:
		# the *_NO_*_CHECK variants are needed for pre-v21 databases
		# where gm.account_is_dbowner_or_staff() doesn't exist yet
		_log.info('generating pre-21 triggers')
		ddl.append('-- creating pre-v21 audit schema script')
		ddl.append(gmAuditSchemaDefs.SQL_TEMPLATE_INSERT_NO_INSERTER_CHECK % args)
		ddl.append('')
		ddl.append(gmAuditSchemaDefs.SQL_TEMPLATE_UPDATE_NO_UPDATER_CHECK % args)
		ddl.append('')
		ddl.append(gmAuditSchemaDefs.SQL_TEMPLATE_DELETE_NO_DELETER_CHECK % args)
	ddl.append('')
	return ddl

#------------------------------------------------------------------
def create_audit_ddl(aCursor):
	# get list of all marked tables
	# we could also get the child tables for audit.audit_fields
	# but we would have to potentially parse down several levels
	# of interitance (such as with clin.clin_root_item) to find
	# the actual leaf table to audit
	SQL = "select schema, table_name from audit.audited_tables"
	rows = gmPG2.run_ro_query(link_obj = aCursor, sql = SQL)
	if not rows:
		_log.info('no tables to audit')
		return None

	_log.debug('the following tables will be audited:')
	_log.debug(rows)
	ddl = []
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

		ddl.append(audit_trail_ddl)
		# create functions and triggers on log table
		ddl.extend(trigger_ddl(aCursor = aCursor, schema = row['schema'], audited_table = row['table_name']))
		ddl.append('-- ----------------------------------------------')
	return ddl

#==================================================================
# main
#------------------------------------------------------------------
if __name__ == "__main__" :
	tmp = ''
	try:
		tmp = input("audit trail parent table [%s]: " % gmAuditSchemaDefs.AUDIT_TRAIL_PARENT_TABLE)
	except KeyboardInterrupt:
		pass
	if tmp != '':
		gmAuditSchemaDefs.AUDIT_TRAIL_PARENT_TABLE = tmp

	gmPG2.request_login_params(setup_pool = True)#, user =None)
	conn = gmPG2.get_connection(readonly=False, pooled=False)
	curs = conn.cursor()

	schema = create_audit_ddl(curs)

	curs.close()
	conn.close()

	if schema is None:
		print("error creating schema")
		sys.exit(-1)

	f = open('audit-trail-schema.sql', mode = 'wt', encoding = 'utf8')
	for line in schema:
		f.write("%s;\n" % line)
	f.close()
