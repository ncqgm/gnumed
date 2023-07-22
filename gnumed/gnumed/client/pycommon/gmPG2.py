"""GNUmed PostgreSQL connection handling.

TODO: iterator/generator batch fetching:
	- http://groups-beta.google.com/group/comp.lang.python/msg/7ff516d7d9387dad
	- search Google for "Geneator/Iterator Nesting Problem - Any Ideas? 2.4"

winner:
def resultset_functional_batchgenerator(cursor, size=100):
	for results in iter(lambda: cursor.fetchmany(size), []):
		for rec in results:
			yield rec
"""
# =======================================================================
__author__  = "K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = 'GPL v2 or later (details at http://www.gnu.org)'


# stdlib
import time
import sys
import os
import stat
import codecs
import logging
import datetime as pydt
import re as regex
import threading
import hashlib
import shutil


# GNUmed
if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmLoginInfo
from Gnumed.pycommon import gmExceptions
from Gnumed.pycommon import gmDateTime
from Gnumed.pycommon import gmI18N
from Gnumed.pycommon import gmLog2
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmConnectionPool
from Gnumed.pycommon.gmTools import prompted_input, u_replacement_character, format_dict_like


_log = logging.getLogger('gm.db')


# 3rd party
try:
	import psycopg2 as dbapi
except ImportError:
	_log.exception("Python database adapter psycopg2 not found.")
	print("CRITICAL ERROR: Cannot find module psycopg2 for connecting to the database server.")
	raise

import psycopg2.errorcodes as sql_error_codes
import psycopg2.sql as psysql
#import psycopg2.errors as PG_EXCEPTIONS

PG_ERROR_EXCEPTION = dbapi.Error

# =======================================================================
default_database = 'gnumed_v22'

postgresql_version_string = None

# =======================================================================
# global data
# =======================================================================

known_schema_hashes = {
	0: 'not released, testing only',
	2: 'b09d50d7ed3f91ddf4c4ddb8ea507720',
	3: 'e73718eaf230d8f1d2d01afa8462e176',
	4: '4428ccf2e54c289136819e701bb095ea',
	5: '7e7b093af57aea48c288e76632a382e5',	# ... old (v1) style hashes
	6: '90e2026ac2efd236da9c8608b8685b2d',	# new (v2) style hashes ...
	7: '6c9f6d3981483f8e9433df99d1947b27',
	8: '89b13a7af83337c3aad153b717e52360',
	9: '641a9b2be3c378ffc2bb2f0b1c9f051d',
	10: '7ef42a8fb2bd929a2cdd0c63864b4e8a',
	11: '03042ae24f3f92877d986fb0a6184d76',
	12: '06183a6616db62257e22814007a8ed07',
	13: 'fab7c1ae408a6530c47f9b5111a0841e',
	14: 'e170d543f067d1ea60bfe9076b1560cf',
	15: '70012ff960b77ecdff4981c94b5b55b6',
	16: '0bcf44ca22c479b52976e5eda1de8161',
	17: '161428ee97a00e3bf56168c3a15b7b50',
	18: 'a0f9efcabdecfb4ddb6d8c0b69c02092',
	#19: '419e5225259c53dd36ad80d82066ff02'	# 19.0 only
	#19: '9765373098b03fb208332498f34cd4b5' # until 19.11
	19: '57f009a159f55f77525cc0291e0c8b60', # starting with 19.12
	20: 'baed1901ed4c2f272b56c8cb2c6d88e8',
	21: 'e6a51a89dd22b75b61ead8f7083f251f',
	22: 'bf45f01327fb5feb2f5d3c06ba4a6792'
}

map_schema_hash2version = {
	'b09d50d7ed3f91ddf4c4ddb8ea507720': 2,
	'e73718eaf230d8f1d2d01afa8462e176': 3,
	'4428ccf2e54c289136819e701bb095ea': 4,
	'7e7b093af57aea48c288e76632a382e5': 5,
	'90e2026ac2efd236da9c8608b8685b2d': 6,
	'6c9f6d3981483f8e9433df99d1947b27': 7,
	'89b13a7af83337c3aad153b717e52360': 8,
	'641a9b2be3c378ffc2bb2f0b1c9f051d': 9,
	'7ef42a8fb2bd929a2cdd0c63864b4e8a': 10,
	'03042ae24f3f92877d986fb0a6184d76': 11,
	'06183a6616db62257e22814007a8ed07': 12,
	'fab7c1ae408a6530c47f9b5111a0841e': 13,
	'e170d543f067d1ea60bfe9076b1560cf': 14,
	'70012ff960b77ecdff4981c94b5b55b6': 15,
	'0bcf44ca22c479b52976e5eda1de8161': 16,
	'161428ee97a00e3bf56168c3a15b7b50': 17,
	'a0f9efcabdecfb4ddb6d8c0b69c02092': 18,
	#'419e5225259c53dd36ad80d82066ff02': 19	# 19.0 only
	#'9765373098b03fb208332498f34cd4b5': 19 # until 19.11
	'57f009a159f55f77525cc0291e0c8b60': 19, # starting with 19.12
	'baed1901ed4c2f272b56c8cb2c6d88e8': 20,
	'e6a51a89dd22b75b61ead8f7083f251f': 21,
	'bf45f01327fb5feb2f5d3c06ba4a6792': 22
}

map_client_branch2required_db_version = {
	'GIT tree': 0,
	'0.3': 9,
	'0.4': 10,
	'0.5': 11,
	'0.6': 12,
	'0.7': 13,
	'0.8': 14,
	'0.9': 15,
	'1.0': 16,		# intentional duplicate with 1.1
	'1.1': 16,
	'1.2': 17,
	'1.3': 18,
	'1.4': 19,
	'1.5': 20,
	'1.6': 21,
	'1.7': 22,
	'1.8': 22		# Yes, SAME as 1.7, no DB change.
}

# get columns and data types for a given table
query_table_col_defs = """select
	cols.column_name,
	cols.udt_name
from
	information_schema.columns cols
where
	cols.table_schema = %s
		and
	cols.table_name = %s
order by
	cols.ordinal_position"""

query_table_attributes = """select
	cols.column_name
from
	information_schema.columns cols
where
	cols.table_schema = %s
		and
	cols.table_name = %s
order by
	cols.ordinal_position"""

# only works for single-column FKs but that's fine
# needs gm-dbo, any-doc won't work
SQL_foreign_key_name = """SELECT
	fk_tbl.*,
	(SELECT nspname FROM pg_catalog.pg_namespace WHERE oid = fk_tbl.connamespace) AS constraint_schema,
	fk_tbl.conname AS constraint_name,
	(SELECT nspname FROM pg_catalog.pg_namespace WHERE oid = (SELECT relnamespace FROM pg_class where oid = fk_tbl.conrelid)) AS source_schema,
	(SELECT relname FROM pg_catalog.pg_class where oid = fk_tbl.conrelid) AS source_table,
	(SELECT attname FROM pg_catalog.pg_attribute WHERE attnum = fk_tbl.conkey[1] AND attrelid = (%(src_schema)s || '.' || %(src_tbl)s)::regclass) AS source_column,
	(SELECT nspname FROM pg_catalog.pg_namespace WHERE oid = (SELECT relnamespace FROM pg_class where oid = fk_tbl.confrelid)) AS target_schema,
	(SELECT relname FROM pg_catalog.pg_class where oid = fk_tbl.confrelid) AS target_table,
	(SELECT attname FROM pg_catalog.pg_attribute WHERE attnum = fk_tbl.confkey[1] AND attrelid = (%(target_schema)s || '.' || %(target_tbl)s)::regclass) AS target_column
FROM
	pg_catalog.pg_constraint fk_tbl
WHERE
	fk_tbl.contype = 'f'
		AND
	fk_tbl.conrelid = (%(src_schema)s || '.' || %(src_tbl)s)::regclass
		AND
	fk_tbl.conkey[1] = (
		SELECT
			col_tbl1.attnum
		FROM
			pg_catalog.pg_attribute col_tbl1
		WHERE
			col_tbl1.attname = %(src_col)s
				AND
			col_tbl1.attrelid = (%(src_schema)s || '.' || %(src_tbl)s)::regclass
	)
		AND
	fk_tbl.confrelid = (%(target_schema)s || '.' || %(target_tbl)s)::regclass
		AND
	fk_tbl.confkey[1] = (
		SELECT
			col_tbl2.attnum
		FROM
			pg_catalog.pg_attribute col_tbl2
		WHERE
			col_tbl2.attname = %(target_col)s
				AND
			col_tbl2.attrelid = (%(target_schema)s || '.' || %(target_tbl)s)::regclass
	)
"""

SQL_get_index_name = """
SELECT
	(SELECT nspname FROM pg_namespace WHERE pg_namespace.oid = pg_class.relnamespace)
		AS index_schema,
	pg_class.relname
		AS index_name
FROM
	pg_class
WHERE
	pg_class.oid IN (
		SELECT
			indexrelid
		FROM
			pg_index
		WHERE
			pg_index.indrelid = %(idx_tbl)s::regclass
				AND
			pg_index.indnatts = 1		-- only one column in index
				AND
			pg_index.indkey[0] IN (
				SELECT
					pg_attribute.attnum
				FROM
					pg_attribute
				WHERE
					pg_attribute.attrelid = %(idx_tbl)s::regclass
						AND
					pg_attribute.attname = %(idx_col)s
				)
	)
"""

SQL_get_pk_col_def = """
SELECT
	pg_attribute.attname
		AS pk_col,
	format_type(pg_attribute.atttypid, pg_attribute.atttypmod)
		AS pk_type
FROM pg_index, pg_class, pg_attribute, pg_namespace
WHERE
	pg_class.oid = %(table)s::regclass
		AND
	indrelid = pg_class.oid
		AND
--	nspname = %%(schema)s
--		AND
	pg_class.relnamespace = pg_namespace.oid
		AND
	pg_attribute.attrelid = pg_class.oid
		AND
	pg_attribute.attnum = any(pg_index.indkey)
		AND
	indisprimary
"""

SQL_get_primary_key_name = """
SELECT
	is_kcu.column_name,
	is_kcu.ordinal_position
FROM
	information_schema.key_column_usage AS is_kcu
		LEFT JOIN information_schema.table_constraints AS is_tc ON is_tc.constraint_name = is_kcu.constraint_name
WHERE
	-- constrain to current database
	is_tc.table_catalog = current_database()
		AND
	is_tc.table_schema = %(schema)s
		AND
	is_tc.table_name = %(table)s
		AND
	is_tc.constraint_type = 'PRIMARY KEY';
"""

# =======================================================================
# login API
# =======================================================================
def __request_login_params_tui():
	"""Text mode request of database login parameters"""

	import getpass
	login = gmLoginInfo.LoginInfo()

	print("\nPlease enter the required login parameters:")
	try:
		login.host = prompted_input(prompt = "host ('' = non-TCP/IP)", default = '')
		login.database = prompted_input(prompt = "database", default = default_database)
		login.user = prompted_input(prompt = "user name", default = '')
		tmp = 'password for "%s" (not shown): ' % login.user
		login.password = getpass.getpass(tmp)
		gmLog2.add_word2hide(login.password)
		login.port = prompted_input(prompt = "port", default = 5432)
	except KeyboardInterrupt:
		del login
		_log.warning("user cancelled text mode login dialog")
		print("user cancelled text mode login dialog")
		raise gmExceptions.ConnectionError(_("Cannot connect to database without login information!"))

	creds = gmConnectionPool.cPGCredentials()
	creds.database = login.database
	creds.host = login.host
	creds.port = login.port
	creds.user = login.user
	creds.password = login.password

	return login, creds

#---------------------------------------------------
def __request_login_params_gui_wx():
	"""GUI (wx) input request for database login parameters.

	Returns gmLoginInfo.LoginInfo object
	"""
	import wx
	# OK, wxPython was already loaded. But has the main Application instance
	# been initialized yet ? if not, the exception will kick us out
	if wx.GetApp() is None:
		raise AssertionError(_("The wxPython GUI framework hasn't been initialized yet!"))

	# Let's launch the login dialog
	# if wx was not initialized /no main App loop, an exception should be raised anyway
	import gmAuthWidgets
	dlg = gmAuthWidgets.cLoginDialog(None, -1)
	dlg.ShowModal()
	login = dlg.panel.GetLoginInfo()
	dlg.DestroyLater()
	#if user cancelled or something else went wrong, raise an exception
	if login is None:
		raise gmExceptions.ConnectionError(_("Can't connect to database without login information!"))

	gmLog2.add_word2hide(login.password)
	creds = gmConnectionPool.cPGCredentials()
	creds.database = login.database
	creds.host = login.host
	creds.port = login.port
	creds.user = login.user
	creds.password = login.password
	return login, creds

#---------------------------------------------------
def request_login_params(setup_pool=False):
	"""Request login parameters for database connection."""
	# are we inside X ?
	# if we aren't wxGTK will crash hard at the C-level with "can't open Display"
	if 'DISPLAY' in os.environ:
		# try wxPython GUI
		try:
			login, creds = __request_login_params_gui_wx()
		except Exception:
			pass
		if setup_pool:
			pool = gmConnectionPool.gmConnectionPool()
			pool.credentials = creds
		return login, creds

	# well, either we are on the console or
	# wxPython does not work, use text mode
	login, creds = __request_login_params_tui()
	if setup_pool:
		pool = gmConnectionPool.gmConnectionPool()
		pool.credentials = creds
	return login, creds

# =======================================================================
# netadata API
# =======================================================================
SQL__concat_table_structure_v19_and_up = """
create or replace function gm.concat_table_structure_v19_and_up()
	returns text
	language 'plpgsql'
	security definer
	as '
declare
	_table_desc record;
	_pk_desc record;
	_column_desc record;
	_constraint_def record;
	_total text;
begin
	_total := '''';

	-- find relevant tables
	for _table_desc in
		select * from information_schema.tables tabs where
			tabs.table_schema in (''dem'', ''clin'', ''blobs'', ''cfg'', ''ref'', ''i18n'', ''bill'')
				and
			tabs.table_type = ''BASE TABLE''
		order by
			decode(md5(tabs.table_schema || tabs.table_name), ''hex'')

	-- loop over tables
	loop
		-- where are we at ?
		_total := _total || ''TABLE:'' || _table_desc.table_schema || ''.'' || _table_desc.table_name || E''\\n'';

		-- find PKs of that table
		for _pk_desc in
			select * from (
				select
					pg_class.oid::regclass || ''.'' || pg_attribute.attname || ''::'' || format_type(pg_attribute.atttypid, pg_attribute.atttypmod) AS primary_key_column
				from
					pg_index, pg_class, pg_attribute
				where
					--pg_class.oid = ''TABLENAME''::regclass
					pg_class.oid = (_table_desc.table_schema || ''.'' || _table_desc.table_name)::regclass
						AND 
					indrelid = pg_class.oid
						AND
					pg_attribute.attrelid = pg_class.oid
						AND
					pg_attribute.attnum = any(pg_index.indkey)
						AND
					indisprimary
				) AS PKs
			order by
				decode(md5(PKs.primary_key_column), ''hex'')
		-- and loop over those PK columns
		loop
			_total := _total || ''PK:'' || _pk_desc.primary_key_column	|| E''\\n'';
		end loop;

		-- find columns of that table
		for _column_desc in
			select *
			from information_schema.columns cols
			where
				cols.table_name = _table_desc.table_name
					and
				cols.table_schema = _table_desc.table_schema
			order by
				decode(md5(cols.column_name || cols.data_type), ''hex'')
		-- and loop over those columns
		loop
			-- add columns in the format "schema.table.column::data_type"
			_total := _total || ''COL:''
				|| _column_desc.table_schema || ''.''
				|| _column_desc.table_name || ''.''
				|| _column_desc.column_name || ''::''
				|| _column_desc.udt_name || E''\\n'';

		end loop;

		-- find and loop over CONSTRAINTs of that table
		for _constraint_def in
			select * from
				(select
					tbl.contype,
					''CONSTRAINT:type=''
						|| tbl.contype::TEXT || '':''
						|| replace(pg_catalog.pg_get_constraintdef(tbl.oid, true), '' '', ''_'')
						|| ''::active=''
						|| tbl.convalidated::TEXT
					 as condef
				from pg_catalog.pg_constraint tbl
				where
					tbl.conrelid = (_table_desc.table_schema || ''.'' || _table_desc.table_name)::regclass
					-- include FKs only because we may have to add/remove
					-- other (say, check) constraints in a minor release
					-- for valid reasons which we do not want to affect
					-- the hash, if however we need to modify a foreign
					-- key that would, indeed, warrant a hash change
						AND
					tbl.contype = ''f''
				) as CONSTRAINTs
			order by
				CONSTRAINTs.contype,
				decode(md5(CONSTRAINTs.condef), ''hex'')
		loop
			_total := _total || _constraint_def.condef || E''\\n'';
		end loop;

	end loop;		-- over tables

	return _total;
end;';

select md5(gm.concat_table_structure(%(ver)s::integer)) AS md5;
"""

def database_schema_compatible(link_obj=None, version=None, verbose=True):
	expected_hash = known_schema_hashes[version]
	if version == 0:
		args = {'ver': 9999}
	else:
		args = {'ver': version}
	SQL = 'select md5(gm.concat_table_structure(%(ver)s::integer)) as md5'
	try:
		rows, idx = run_ro_queries(link_obj = link_obj, queries = [{'cmd': SQL, 'args': args}])
	except dbapi.errors.AmbiguousFunction as exc:
		gmConnectionPool.log_pg_exception_details(exc)
		if not hasattr(exc, 'diag'):
			raise
		if 'gm.concat_table_structure_v19_and_up()' not in exc.diag.context:
			raise
		rows = None
	if rows is None:
		_log.error('gm.concat_table_structure_v19_and_up() failed, retrying with updated function')
		rows, idx = run_ro_queries(link_obj = link_obj, queries = [{'cmd': SQL__concat_table_structure_v19_and_up, 'args': args}])
	if rows[0]['md5'] == expected_hash:
		_log.info('detected schema version [%s], hash [%s]' % (map_schema_hash2version[rows[0]['md5']], rows[0]['md5']))
		return True

	_log.error('database schema version mismatch')
	_log.error('expected: %s (%s)' % (version, expected_hash))
	_log.error('detected: %s (%s)' % (get_schema_version(link_obj=link_obj), rows[0]['md5']))
	if verbose:
		_log.debug('schema dump follows:')
		for line in get_schema_structure(link_obj = link_obj).split():
			_log.debug(line)
		_log.debug('schema revision history dump follows:')
		for line in get_schema_revision_history(link_obj = link_obj):
			_log.debug(' - '.join(line))
	return False

#------------------------------------------------------------------------
def get_schema_version(link_obj=None):
	rows, idx = run_ro_queries(link_obj=link_obj, queries = [{'cmd': 'select md5(gm.concat_table_structure()) as md5'}])
	try:
		return map_schema_hash2version[rows[0]['md5']]
	except KeyError:
		return 'unknown database schema version, MD5 hash is [%s]' % rows[0]['md5']

#------------------------------------------------------------------------
def get_schema_structure(link_obj=None):
	rows, idx = run_ro_queries(link_obj=link_obj, queries = [{'cmd': 'select gm.concat_table_structure()'}])
	return rows[0][0]

#------------------------------------------------------------------------
def get_schema_hash(link_obj=None):
	rows, idx = run_ro_queries(link_obj=link_obj, queries = [{'cmd': 'select md5(gm.concat_table_structure()) as md5'}])
	return rows[0]['md5']

#------------------------------------------------------------------------
def get_schema_revision_history(link_obj=None):

	if table_exists(link_obj = link_obj, schema = 'gm', table = 'schema_revision'):
		cmd = """
			SELECT
				imported::text,
				version,
				filename
			FROM gm.schema_revision
			ORDER BY imported"""
	elif table_exists(link_obj = link_obj, schema = 'public', table = 'gm_schema_revision'):
		cmd = """
			SELECT
				imported::text,
				version,
				filename
			FROM public.gm_schema_revision
			ORDER BY imported"""
	else:
		return []

	rows, idx = run_ro_queries(link_obj = link_obj, queries = [{'cmd': cmd}])
	return rows

#------------------------------------------------------------------------
def get_db_fingerprint(conn=None, fname=None, with_dump=False, eol=None):
	queries = [
		("SELECT setting FROM pg_settings WHERE name = 'server_version'", "Version (PG)"),
		("SELECT setting FROM pg_settings WHERE name = 'server_encoding'", "Encoding (PG)"),
		("SELECT setting FROM pg_settings WHERE name = 'lc_collate'", "LC_COLLATE (PG)"),
		("SELECT setting FROM pg_settings WHERE name = 'lc_ctype'", "LC_CTYPE (PG)"),
		("SELECT count(1) FROM dem.identity", "Patients"),
		("SELECT count(1) FROM clin.encounter", "Contacts"),
		("SELECT count(1) FROM clin.episode", "Episodes"),
		("SELECT count(1) FROM clin.health_issue", "Issues"),
		("SELECT count(1) FROM clin.test_result", "Results"),
		("SELECT count(1) FROM clin.vaccination", "Vaccinations"),
		("SELECT count(1) FROM blobs.doc_med", "Documents"),
		("SELECT count(1) FROM blobs.doc_obj", "Objects"),
		("SELECT count(1) FROM dem.org", "Organizations"),
		("SELECT count(1) FROM dem.org_unit", "Organizational units"),
		("SELECT max(modified_when) FROM audit.audit_fields", "Most recent .modified_when"),
		("SELECT max(audit_when) FROM audit.audit_trail", "Most recent .audit_when")
	]
	if conn is None:
		conn = get_connection(readonly = True)
	database = conn.get_dsn_parameters()['dbname']
	lines = [
		'Fingerprinting GNUmed database ...',
		'',
		'%20s: %s' % ('Name (DB)', database)
	]
	curs = conn.cursor()
	# get size
	cmd = "SELECT pg_size_pretty(pg_database_size('%s'))" % database
	curs.execute(cmd)
	rows = curs.fetchall()
	lines.append('%20s: %s' % ('Size (DB)', rows[0][0]))
	# get hash
	cmd = "SELECT md5(gm.concat_table_structure())"
	curs.execute(cmd)
	rows = curs.fetchall()
	md5_sum = rows[0][0]
	try:
		lines.append('%20s: %s (v%s)' % ('Schema hash', md5_sum, map_schema_hash2version[md5_sum]))
	except KeyError:
		lines.append('%20s: %s' % ('Schema hash', md5_sum))
	for cmd, label in queries:
		curs.execute(cmd)
		rows = curs.fetchall()
		lines.append('%20s: %s' % (label, rows[0][0]))
	if with_dump:
		curs.execute('SELECT gm.concat_table_structure()')
		rows = curs.fetchall()
		lines.append('')
		lines.append(rows[0][0])
	curs.close()
	if fname is None:
		if eol is None:
			return lines
		return eol.join(lines)

	outfile = open(fname, mode = 'wt', encoding = 'utf8')
	outfile.write('\n'.join(lines))
	outfile.close()
	return fname

#------------------------------------------------------------------------
def get_current_user():
	rows, idx = run_ro_queries(queries = [{'cmd': 'select CURRENT_USER'}])
	return rows[0][0]

#------------------------------------------------------------------------
def get_foreign_keys2column(schema='public', table=None, column=None, link_obj=None):
	"""Get the foreign keys pointing to schema.table.column.

	Does not properly work with multi-column FKs.
	GNUmed doesn't use any, however.
	"""
	args = {
		'schema': schema,
		'tbl': table,
		'col': column
	}
	cmd = """
SELECT
	%(schema)s AS referenced_schema,
	%(tbl)s AS referenced_table,
	%(col)s AS referenced_column,
	pgc.confkey AS referenced_column_list,

	pgc.conrelid::regclass AS referencing_table,
	pgc.conkey AS referencing_column_list,
	(select attname from pg_attribute where attnum = pgc.conkey[1] and attrelid = pgc.conrelid) AS referencing_column
FROM
	pg_constraint pgc
WHERE
	pgc.contype = 'f'
		AND
	pgc.confrelid = (
		select oid from pg_class where relname = %(tbl)s and relnamespace = (
			select oid from pg_namespace where nspname = %(schema)s
		 )
	)	and
	(
		select attnum
		from pg_attribute
		where
			attrelid = (select oid from pg_class where relname = %(tbl)s and relnamespace = (
				select oid from pg_namespace where nspname = %(schema)s
			))
				and
			attname = %(col)s
	) = any(pgc.confkey)
"""
	rows, idx = run_ro_queries (
		link_obj = link_obj,
		queries = [
			{'cmd': cmd, 'args': args}
		]
	)

	return rows

#------------------------------------------------------------------------
def get_index_name(indexed_table=None, indexed_column=None, link_obj=None):

	args = {
		'idx_tbl': indexed_table,
		'idx_col': indexed_column
	}
	rows, idx = run_ro_queries (
		link_obj = link_obj,
		queries = [{'cmd': SQL_get_index_name, 'args': args}],
		get_col_idx = False
	)

	return rows

#------------------------------------------------------------------------
def get_foreign_key_names(src_schema=None, src_table=None, src_column=None, target_schema=None, target_table=None, target_column=None, link_obj=None):

	args = {
		'src_schema': src_schema,
		'src_tbl': src_table,
		'src_col': src_column,
		'target_schema': target_schema,
		'target_tbl': target_table,
		'target_col': target_column
	}

	rows, idx = run_ro_queries (
		link_obj = link_obj,
		queries = [{'cmd': SQL_foreign_key_name, 'args': args}],
		get_col_idx = False
	)

	return rows

#------------------------------------------------------------------------
def get_child_tables(schema='public', table=None, link_obj=None):
	"""Return child tables of <table>."""
	cmd = """
select
	pgn.nspname as namespace,
	pgc.relname as table
from
	pg_namespace pgn,
	pg_class pgc
where
	pgc.relnamespace = pgn.oid
		and
	pgc.oid in (
		select inhrelid from pg_inherits where inhparent = (
			select oid from pg_class where
				relnamespace = (select oid from pg_namespace where nspname = %(schema)s) and
				relname = %(table)s
		)
	)"""
	rows, idx = run_ro_queries(link_obj = link_obj, queries = [{'cmd': cmd, 'args': {'schema': schema, 'table': table}}])
	return rows

#------------------------------------------------------------------------
def schema_exists(link_obj=None, schema='gm'):
	cmd = """SELECT EXISTS (SELECT 1 FROM pg_namespace WHERE nspname = %(schema)s)"""
	args = {'schema': schema}
	rows, idx = run_ro_queries(link_obj = link_obj, queries = [{'cmd': cmd, 'args': args}])
	return rows[0][0]

#------------------------------------------------------------------------
def table_exists(link_obj=None, schema=None, table=None):
	"""Returns false, true."""
	cmd = """
select exists (
	select 1 from information_schema.tables
	where
		table_schema = %s and
		table_name = %s and
		table_type = 'BASE TABLE'
)"""
	rows, idx = run_ro_queries(link_obj = link_obj, queries = [{'cmd': cmd, 'args': (schema, table)}])
	return rows[0][0]

#------------------------------------------------------------------------
def function_exists(link_obj=None, schema=None, function=None):

	cmd = """
		SELECT EXISTS (
			SELECT 1 FROM pg_proc
			WHERE proname = %(func)s AND pronamespace = (SELECT oid FROM pg_namespace WHERE nspname = %(schema)s)
		)
	"""
	args = {
		'func': function,
		'schema': schema
	}
	rows, idx = run_ro_queries(link_obj = link_obj, queries = [{'cmd': cmd, 'args': args}])
	return rows[0][0]

#------------------------------------------------------------------------
def get_col_indices(cursor = None):
	if cursor.description is None:
		_log.error('no result description available: unused cursor or last query did not select rows')
		return None
	col_indices = {}
	col_index = 0
	for col_desc in cursor.description:
		col_name = col_desc[0]
		# a query like "select 1,2;" will return two columns of the same name !
		# hence adjust to that, note, however, that dict-style access won't work
		# on results of such queries ...
		if col_name in col_indices:
			col_name = '%s_%s' % (col_name, col_index)
		col_indices[col_name] = col_index
		col_index += 1

	return col_indices
#------------------------------------------------------------------------
def get_col_defs(link_obj=None, schema='public', table=None):
	rows, idx = run_ro_queries(link_obj = link_obj, queries = [{'cmd': query_table_col_defs, 'args': (schema, table)}])
	col_names = []
	col_type = {}
	for row in rows:
		col_names.append(row[0])
		# map array types
		if row[1].startswith('_'):
			col_type[row[0]] = row[1][1:] + '[]'
		else:
			col_type[row[0]] = row[1]
	col_defs = []
	col_defs.append(col_names)
	col_defs.append(col_type)
	return col_defs
#------------------------------------------------------------------------
def get_col_names(link_obj=None, schema='public', table=None):
	"""Return column attributes of table"""
	rows, idx = run_ro_queries(link_obj = link_obj, queries = [{'cmd': query_table_attributes, 'args': (schema, table)}])
	cols = []
	for row in rows:
		cols.append(row[0])
	return cols

#------------------------------------------------------------------------
# i18n functions
#------------------------------------------------------------------------
def export_translations_from_database(filename=None):
	tx_file = open(filename, mode = 'wt', encoding = 'utf8')
	tx_file.write('-- GNUmed database string translations exported %s\n' % gmDateTime.pydt_now_here().strftime('%Y-%m-%d %H:%M'))
	tx_file.write('-- - contains translations for each of [%s]\n' % ', '.join(get_translation_languages()))
	tx_file.write('-- - user database language is set to [%s]\n\n' % get_current_user_language())
	tx_file.write('-- Please email this file to <gnumed-devel@gnu.org>.\n')
	tx_file.write('-- ----------------------------------------------------------------------------------------------\n\n')
	tx_file.write('set default_transaction_read_only to off;\n\n')
	tx_file.write("set client_encoding to 'utf-8';\n\n")
	tx_file.write('\\unset ON_ERROR_STOP\n\n')

	cmd = 'SELECT lang, orig, trans FROM i18n.translations ORDER BY lang, orig'
	rows, idx = run_ro_queries(queries = [{'cmd': cmd}], get_col_idx = False)
	for row in rows:
		line = "select i18n.upd_tx(E'%s', E'%s', E'%s');\n" % (
			row['lang'].replace("'", "\\'"),
			row['orig'].replace("'", "\\'"),
			row['trans'].replace("'", "\\'")
		)
		tx_file.write(line)
	tx_file.write('\n')

	tx_file.write('\set ON_ERROR_STOP 1\n')
	tx_file.close()

	return True

#------------------------------------------------------------------------
def delete_translation_from_database(link_obj=None, language=None, original=None):
	cmd = 'DELETE FROM i18n.translations WHERE lang = %(lang)s AND orig = %(orig)s'
	args = {'lang': language, 'orig': original}
	run_rw_queries(link_obj = link_obj, queries = [{'cmd': cmd, 'args': args}], return_data = False, end_tx = True)
	return True

#------------------------------------------------------------------------
def update_translation_in_database(language=None, original=None, translation=None, link_obj=None):
	if language is None:
		cmd = 'SELECT i18n.upd_tx(%(orig)s, %(trans)s)'
	else:
		cmd = 'SELECT i18n.upd_tx(%(lang)s, %(orig)s, %(trans)s)'
	args = {'lang': language, 'orig': original, 'trans': translation}
	run_rw_queries(queries = [{'cmd': cmd, 'args': args}], return_data = False, link_obj = link_obj)
	return args

#------------------------------------------------------------------------
def get_translation_languages():
	rows, idx = run_ro_queries (
		queries = [{'cmd': 'select distinct lang from i18n.translations'}]
	)
	return [ r[0] for r in rows ]

#------------------------------------------------------------------------
def get_database_translations(language=None, order_by=None):

	args = {'lang': language}
	_log.debug('language [%s]', language)

	if order_by is None:
		order_by = 'ORDER BY %s' % order_by
	else:
		order_by = 'ORDER BY lang, orig'

	if language is None:
		cmd = """
		SELECT DISTINCT ON (orig, lang)
			lang, orig, trans
		FROM ((

			-- strings stored as translation keys whether translated or not
			SELECT
				NULL as lang,
				ik.orig,
				NULL AS trans
			FROM
				i18n.keys ik

		) UNION ALL (

			-- already translated strings
			SELECT
				it.lang,
				it.orig,
				it.trans
			FROM
				i18n.translations it

		)) as translatable_strings
		%s""" % order_by
	else:
		cmd = """
		SELECT DISTINCT ON (orig, lang)
			lang, orig, trans
		FROM ((

			-- strings stored as translation keys whether translated or not
			SELECT
				%%(lang)s as lang,
				ik.orig,
				i18n._(ik.orig, %%(lang)s) AS trans
			FROM
				i18n.keys ik

		) UNION ALL (

			-- already translated strings
			SELECT
				%%(lang)s as lang,
				it.orig,
				i18n._(it.orig, %%(lang)s) AS trans
			FROM
				i18n.translations it

		)) AS translatable_strings
		%s""" % order_by

	rows, idx = run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = False)

	if rows is None:
		_log.error('no translatable strings found')
	else:
		_log.debug('%s translatable strings found', len(rows))

	return rows

#------------------------------------------------------------------------
def get_current_user_language():
	cmd = 'select i18n.get_curr_lang()'
	rows, idx = run_ro_queries(queries = [{'cmd': cmd}])
	return rows[0][0]

#------------------------------------------------------------------------
def set_user_language(user=None, language=None):
	"""Set the user language in the database.

	user = None: current db user
	language = None: unset
	"""
	_log.info('setting database language for user [%s] to [%s]', user, language)
	args = {'usr': user, 'lang': language}
	if language is None:
		if user is None:
			queries = [{'cmd': 'select i18n.unset_curr_lang()'}]
		else:
			queries = [{'cmd': 'select i18n.unset_curr_lang(%(usr)s)', 'args': args}]
		queries.append({'cmd': 'select True'})
	else:
		if user is None:
			queries = [{'cmd': 'select i18n.set_curr_lang(%(lang)s)', 'args': args}]
		else:
			queries = [{'cmd': 'select i18n.set_curr_lang(%(lang)s, %(usr)s)', 'args': args}]
	rows, idx = run_rw_queries(queries = queries, return_data = True)
	if not rows[0][0]:
		_log.error('cannot set database language to [%s] for user [%s]', language, user)
	return rows[0][0]

#------------------------------------------------------------------------
def force_user_language(language=None):
	"""Set the user language in the database.

	- regardless of whether there is any translation available.
	- only for the current user
	"""
	_log.info('forcing database language for current db user to [%s]', language)

	run_rw_queries(queries = [{
		'cmd': 'select i18n.force_curr_lang(%(lang)s)',
		'args': {'lang': language}
	}])

# =======================================================================
# query runners and helpers
# =======================================================================
def send_maintenance_notification():
	cmd = 'notify "db_maintenance_warning"'
	run_rw_queries(queries = [{'cmd': cmd}], return_data = False)

#------------------------------------------------------------------------
def send_maintenance_shutdown():
	cmd = 'notify "db_maintenance_disconnect"'
	run_rw_queries(queries = [{'cmd': cmd}], return_data = False)

#------------------------------------------------------------------------
def is_pg_interval(candidate=None):
	cmd = 'SELECT %(candidate)s::interval'
	try:
		rows, idx = run_ro_queries(queries = [{'cmd': cmd, 'args': {'candidate': candidate}}])
		return True
	except Exception:
		cmd = 'SELECT %(candidate)s::text::interval'
		try:
			rows, idx = run_ro_queries(queries = [{'cmd': cmd, 'args': {'candidate': candidate}}])
			return True
		except Exception:
			return False

#------------------------------------------------------------------------
def lock_row(link_obj=None, table=None, pk=None, exclusive=False):
	"""Uses pg_advisory(_shared).

	- locks stack upon each other and need one unlock per lock
	- same connection:
		- all locks succeed
	- different connections:
		- shared + shared succeed
		- shared + exclusive fail
	"""
	_log.debug('locking row: [%s] [%s] (exclusive: %s)', table, pk, exclusive)
	if exclusive:
		cmd = """SELECT pg_try_advisory_lock('%s'::regclass::oid::int, %s)""" % (table, pk)
	else:
		cmd = """SELECT pg_try_advisory_lock_shared('%s'::regclass::oid::int, %s)""" % (table, pk)
	rows, idx = run_ro_queries(link_obj = link_obj, queries = [{'cmd': cmd}], get_col_idx = False)
	if rows[0][0]:
		return True

	_log.warning('cannot lock row: [%s] [%s] (exclusive: %s)', table, pk, exclusive)
	return False

#------------------------------------------------------------------------
def unlock_row(link_obj=None, table=None, pk=None, exclusive=False):
	"""Uses pg_advisory_unlock(_shared).

	- each lock needs one unlock
	"""
	_log.debug('trying to unlock row: [%s] [%s] (exclusive: %s)', table, pk, exclusive)
	if exclusive:
		cmd = "SELECT pg_advisory_unlock('%s'::regclass::oid::int, %s)" % (table, pk)
	else:
		cmd = "SELECT pg_advisory_unlock_shared('%s'::regclass::oid::int, %s)" % (table, pk)
	rows, idx = run_ro_queries(link_obj = link_obj, queries = [{'cmd': cmd}], get_col_idx = False)
	if rows[0][0]:
		return True

	_log.warning('cannot unlock row: [%s] [%s] (exclusive: %s)', table, pk, exclusive)
	return False

#------------------------------------------------------------------------
def row_is_locked(table=None, pk=None):
	"""Looks at pg_locks.

	- does not take into account locks other than 'advisory', however
	"""
	cmd = """SELECT EXISTS (
		SELECT 1 FROM pg_locks WHERE
			classid = '%s'::regclass::oid::int
				AND
			objid = %s
				AND
			locktype = 'advisory'
	)""" % (table, pk)
	rows, idx = run_ro_queries(queries = [{'cmd': cmd}], get_col_idx = False)
	if rows[0][0]:
		_log.debug('row is locked: [%s] [%s]', table, pk)
		return True

	_log.debug('row is NOT locked: [%s] [%s]', table, pk)
	return False

#------------------------------------------------------------------------
# BYTEA cache handling
#------------------------------------------------------------------------
def __generate_cached_filename(cache_key_data):
	md5 = hashlib.md5()
	md5.update(('%s' % cache_key_data).encode('utf8'))
	return os.path.join(gmTools.gmPaths().bytea_cache_dir, md5.hexdigest())

#------------------------------------------------------------------------
def __store_file_in_cache(filename, cache_key_data):
	cached_name = __generate_cached_filename(cache_key_data)
	_log.debug('[%s] -> [%s] -> [%s]', filename, cache_key_data, cached_name)
	if not gmTools.remove_file(cached_name, log_error = True, force = True):
		_log.error('cannot remove existing file [%s] for key [%s] from cache', filename, cached_name)
		return None

	PERMS_owner_only = 0o0660
	try:
		shutil.copyfile(filename, cached_name, follow_symlinks = True)
		os.chmod(cached_name, PERMS_owner_only)
	except shutil.SameFileError:
		_log.exception('file seems to exist in cache, despite having checked and possible removed it just before')
		# don't use that file, it is unsafe, it might have come from
		# a race being exploited to make us use the wrong data, this
		# then constitutes a DOS attack against the cache but that's
		# far less problematic than using the wrong data for care
		return None
	except OSError:
		_log.exception('cannot copy file into cache: [%s] -> [%s]', filename, cached_name)
		return None
	except PermissionError:
		_log.exception('cannot set cache file [%s] permissions to [%s]', cached_name, stat.filemode(PERMS_owner_only))
		return None

	return cached_name

#------------------------------------------------------------------------
def __get_filename_in_cache(cache_key_data=None, data_size=None):
	"""Calculate and verify filename in cache given cache key details."""
	cached_name = __generate_cached_filename(cache_key_data)
	try:
		stat = os.stat(cached_name)
	except FileNotFoundError:
		return None

	_log.debug('cache hit: [%s] -> [%s] (%s)', cache_key_data, cached_name, stat)
	if os.path.islink(cached_name) or (not os.path.isfile(cached_name)):
		_log.error('object in cache is not a regular file: %s', cached_name)
		_log.error('possibly an attack, removing')
		if gmTools.remove_file(cached_name, log_error = True):
			return None

		raise Exception('cannot delete suspicious object in cache dir: %s', cached_name)

	if stat.st_size == data_size:
		return cached_name

	_log.debug('size in cache [%s] <> expected size [%s], removing cached file', stat.st_size, data_size)
	if gmTools.remove_file(cached_name, log_error = True):
		return None

	raise Exception('cannot remove suspicious object from cache dir: %s', cached_name)

#------------------------------------------------------------------------
def __get_file_from_cache(filename, cache_key_data=None, data_size=None, link2cached=True):
	"""Get file from cache if available."""
	cached_filename = __get_filename_in_cache(cache_key_data = cache_key_data, data_size = data_size)
	if cached_filename is None:
		return False

	if link2cached:
		try:
			# (hard)link as desired name, quite a few security
			# and archival tools refuse to handle softlinks
			os.link(cached_filename, filename)
			_log.debug('hardlinked [%s] as [%s]', cached_filename, filename)
			return True

		except Exception:
			pass
	_log.debug('cannot hardlink to cache, trying copy-from-cache')
	try:
		shutil.copyfile(cached_filename, filename, follow_symlinks = True)
		return True

	except shutil.SameFileError:
		# flaky - might be same name but different content
		pass
	except OSError:
		_log.exception('cannot copy cached file [%s] into [%s]', cached_filename, filename)
	# if cache fails entirely -> fall through to new file
	_log.debug('downloading new copy of file, despite found in cache')
	return False

#------------------------------------------------------------------------
def bytea2file(data_query=None, filename=None, chunk_size=0, data_size=None, data_size_query=None, conn=None, link2cached=True):

	if data_size == 0:
		open(filename, 'wb').close()
		return True

	if data_size is None:
		rows, idx = run_ro_queries(link_obj = conn, queries = [data_size_query])
		data_size = rows[0][0]
		if data_size == 0:
			open(filename, 'wb').close()
			return True

		if data_size is None:
			return False

	if conn is None:
		conn = gmConnectionPool.gmConnectionPool().get_connection()
	cache_key_data = '%s::%s' % (conn.dsn, data_query)
	found_in_cache = __get_file_from_cache(filename, cache_key_data = cache_key_data, data_size = data_size, link2cached = link2cached)
	if found_in_cache:
		# FIXME: start thread checking cache staleness on file
		return True

	outfile = open(filename, 'wb')
	result = bytea2file_object (
		data_query = data_query,
		file_obj = outfile,
		chunk_size = chunk_size,
		data_size = data_size,
		data_size_query = data_size_query,
		conn = conn
	)
	outfile.close()
	__store_file_in_cache(filename, cache_key_data)
	return result

#------------------------------------------------------------------------
def bytea2file_object(data_query=None, file_obj=None, chunk_size=0, data_size=None, data_size_query=None, conn=None):
	"""Store data from a bytea field into a file.

	<data_query>
	- dict {'cmd': ..., 'args': ...}
	- 'cmd' must be a string containing "... substring(data from %(start)s for %(size)s) ..."
	- 'args' must be a dict
	- must return one row with one field of type bytea
	<file>
	- must be a file like Python object
	<data_size>
	- integer of the total size of the expected data or None
	<data_size_query>
	- dict {'cmd': ..., 'args': ...}
	- must return one row with one field with the octet_length() of the data field
	- used only when <data_size> is None
	"""
	if data_size == 0:
		return True

	# If the client sets an encoding other than the default we
	# will receive encoding-parsed data which isn't the binary
	# content we want. Hence we need to get our own connection.
	# It must be a read-write one so that we don't affect the
	# encoding for other users of the shared read-only
	# connections.
	# Actually, encodings shouldn't be applied to binary data
	# (eg. bytea types) in the first place but that is only
	# reported to be fixed > v7.4.
	# further tests reveal that at least on PG 8.0 this bug still
	# manifests itself
	if conn is None:
		conn = get_raw_connection(readonly = True)

	if data_size is None:
		rows, idx = run_ro_queries(link_obj = conn, queries = [data_size_query])
		data_size = rows[0][0]
		if data_size in [None, 0]:
			conn.rollback()
			return True

	max_chunk_size = 1024 * 1024 * 20			# 20 MB, works for typical CR DICOMs
	if chunk_size == 0:
		chunk_size = min(data_size, max_chunk_size)

	_log.debug('expecting %s bytes of BYTEA data in chunks of %s bytes', data_size, chunk_size)

	# Windoze sucks: it can't transfer objects of arbitrary size,
	# anyways, we need to split the transfer,
	# however, only possible if postgres >= 7.2
	needed_chunks, remainder = divmod(data_size, chunk_size)
	_log.debug('%s chunk(s), %s byte(s) remainder', needed_chunks, remainder)

	# retrieve chunks, skipped if data size < chunk size,
	# does this not carry the danger of cutting up multi-byte escape sequences ?
	# no, since bytea is binary,
	# yes, since in bytea there are *some* escaped values, still
	# no, since those are only escaped during *transfer*, not on-disk, hence
	# only complete escape sequences are put on the wire
	for chunk_id in range(needed_chunks):
		chunk_start = (chunk_id * chunk_size) + 1
		data_query['args']['start'] = chunk_start
		data_query['args']['size'] = chunk_size
		try:
			rows, idx = run_ro_queries(link_obj=conn, queries=[data_query])
		except Exception:
			_log.error('cannot retrieve chunk [%s/%s], size [%s], try decreasing chunk size' % (chunk_id+1, needed_chunks, chunk_size))
			conn.rollback()
			raise
		# it would be a fatal error to see more than one result as ids are supposed to be unique
		file_obj.write(rows[0][0])

	# retrieve remainder
	if remainder > 0:
		chunk_start = (needed_chunks * chunk_size) + 1
		data_query['args']['start'] = chunk_start
		data_query['args']['size'] = remainder
		try:
			rows, idx = run_ro_queries(link_obj=conn, queries=[data_query])
		except Exception:
			_log.error('cannot retrieve remaining [%s] bytes' % remainder)
			conn.rollback()
			raise
		# it would be a fatal error to see more than one result as ids are supposed to be unique
		file_obj.write(rows[0][0])

	conn.rollback()
	return True

#------------------------------------------------------------------------
def file2bytea(query=None, filename=None, args=None, conn=None, file_md5=None):
	"""Store data from a file into a bytea field.

	The query must:
	- contain a format spec identifying the row (eg a primary key)
	  matching <args> if it is an UPDATE
	- contain a format spec " <field> = %(data)s::bytea"

	The query CAN return the MD5 of the inserted data:
		RETURNING md5(<field>) AS md5
	in which case the returned hash will compared to the md5 of the file.
	"""
	retry_delay = 100		# milliseconds
	attempt = 0
	max_attempts = 3
	while attempt < max_attempts:
		attempt += 1
		try:
			infile = open(filename, "rb")
		except (BlockingIOError, FileNotFoundError, PermissionError):
			_log.exception('#%s: cannot open [%s]', attempt, filename)
			_log.error('retrying after %sms', retry_delay)
			infile = None
			time.sleep(retry_delay / 1000)
	if infile is None:
		return False

	data_as_byte_string = infile.read()
	infile.close()
	if args is None:
		args = {}
	# really still needed for BYTEA input ?
	args['data'] = memoryview(data_as_byte_string)
	del(data_as_byte_string)
	# insert the data
	if conn is None:
		conn = get_raw_connection(readonly = False)
		close_conn = True
	else:
		close_conn = False
	rows, idx = run_rw_queries(link_obj = conn, queries = [{'cmd': query, 'args': args}], end_tx = False, return_data = (file_md5 is not None))
	success_status = True
	if file_md5 is None:
		conn.commit()
	else:
		db_md5 = rows[0]['md5']
		if file_md5 != db_md5:
			conn.rollback()
			success_status = False
			_log.error('MD5 sums of data file and database BYTEA field do not match: [file::%s] <> [DB::%s]', file_md5, db_md5)
		else:
			conn.commit()
			_log.debug('MD5 sums of data file and database BYTEA field match: [file::%s] = [DB::%s]', file_md5, db_md5)
	if close_conn:
		conn.close()
	return success_status

#------------------------------------------------------------------------
def file2lo(filename=None, conn=None, check_md5=False):
	# 1 GB limit unless 64 bit Python build ...
	file_size = os.path.getsize(filename)
	if file_size > (1024 * 1024) * 1024:
		_log.debug('file size of [%s] > 1 GB, supposedly not supported by psycopg2 large objects (but seems to work anyway ?)', file_size)
#		return -1

	if conn is None:
		conn = get_raw_connection(readonly = False)
		close_conn = conn.close
	else:
		close_conn = __noop
	_log.debug('[%s] -> large object', filename)

	# insert the data
	lo = conn.lobject(0, 'w', 0, filename)
	lo_oid = lo.oid
	lo.close()
	_log.debug('large object OID: %s', lo_oid)

	# verify
	if file_md5 is None:
		conn.commit()
		close_conn()
		return lo_oid
	cmd = 'SELECT md5(lo_get(%(loid)s::oid))'
	args = {'loid': lo_oid}
	rows, idx = run_ro_queries(link_obj = conn, queries = [{'cmd': cmd, 'args': args}])
	db_md5 = rows[0][0]
	if file_md5 == db_md5:
		conn.commit()
		close_conn()
		_log.debug('MD5 sums of data file and database large object match: [file::%s] = [DB::%s]', file_md5, db_md5)
		return lo_oid
	conn.rollback()
	close_conn()
	_log.error('MD5 sums of data file and database large object [%s] do not match: [file::%s] <> [DB::%s]', lo_oid, file_md5, db_md5)
	return -1

#------------------------------------------------------------------------
def file2bytea_lo(filename=None, conn=None, file_md5=None):
	# 1 GB limit unless 64 bit Python build ...
	file_size = os.path.getsize(filename)
	if file_size > (1024 * 1024) * 1024:
		_log.debug('file size of [%s] > 1 GB, supposedly not supported by psycopg2 large objects (but seems to work anyway ?)', file_size)
#		return -1

	if conn is None:
		conn = get_raw_connection(readonly = False)
		close_conn = conn.close
	else:
		close_conn = __noop
	_log.debug('[%s] -> large object', filename)

	# insert the data
	lo = conn.lobject(0, 'w', 0, filename)
	lo_oid = lo.oid
	lo.close()
	_log.debug('large object OID: %s', lo_oid)

	# verify
	if file_md5 is None:
		conn.commit()
		close_conn()
		return lo_oid
	cmd = 'SELECT md5(lo_get(%(loid)s::oid))'
	args = {'loid': lo_oid}
	rows, idx = run_ro_queries(link_obj = conn, queries = [{'cmd': cmd, 'args': args}])
	db_md5 = rows[0][0]
	if file_md5 == db_md5:
		conn.commit()
		close_conn()
		_log.debug('MD5 sums of data file and database large object match: [file::%s] = [DB::%s]', file_md5, db_md5)
		return lo_oid
	conn.rollback()
	close_conn()
	_log.error('MD5 sums of data file and database large object [%s] do not match: [file::%s] <> [DB::%s]', lo_oid, file_md5, db_md5)
	return -1

#------------------------------------------------------------------------
def file2bytea_copy_from(table=None, columns=None, filename=None, conn=None, md5_query=None, file_md5=None):
	# md5_query: dict{'cmd': ..., 'args': ...}

	# UNTESTED

	chunk_size = 32 * (1024 * 1024)
	_log.debug('[%s] (%s bytes) --(%s bytes)-> %s(%s)', filename, os.path.getsize(filename), chunk_size, table, columns)
	if conn is None:
		conn = get_raw_connection(readonly = False)
		close_conn = True
	else:
		close_conn = False
	curs = conn.cursor()
	# write
	infile = open(filename, "rb")
	curs.copy_from(infile, table, size = chunk_size, columns = columns)
	infile.close()
	curs.close()
	if None in [file_md5, md5_query]:
		conn.commit()
		close_conn()
		return True
	# verify
	rows, idx = run_ro_queries(link_obj = conn, queries = [md5_query])
	db_md5 = rows[0][0]
	if file_md5 == db_md5:
		conn.commit()
		close_conn()
		_log.debug('MD5 sums of data file and database BYTEA field match: [file::%s] = [DB::%s]', file_md5, db_md5)
		return True
	close_conn()
	_log.error('MD5 sums of data file and database BYTEA field do not match: [file::%s] <> [DB::%s]', file_md5, db_md5)
	return False

#------------------------------------------------------------------------
def file2bytea_overlay(query=None, args=None, filename=None, conn=None, md5_query=None, file_md5=None):
	"""Store data from a file into a bytea field.

	The query must:
	- 'cmd' must be in unicode
	- 'cmd' must contain a format spec identifying the row (eg
	  a primary key) matching <args> if it is an UPDATE
	- 'cmd' must contain "... SET ... <some_bytea_field> = OVERLAY(some_bytea_field PLACING %(data)s::bytea FROM %(start)s FOR %(size)s) ..."
	- 'args' must be a dict matching 'cmd'

	The query CAN return the MD5 of the inserted data:
		RETURNING md5(<field>) AS md5
	in which case it will compare it to the md5
	of the file.

	UPDATE
		the_table
	SET
		bytea_field = OVERLAY (
			coalesce(bytea_field, '':bytea),
			PLACING
				%(data)s::bytea
			FROM
				%(start)s
			FOR
				%(size)s
		)
	WHERE
		primary_key = pk_value

	SELECT md5(bytea_field) FROM the_table WHERE primary_key = pk_value
	"""
	chunk_size = 32 * (1024 * 1024)
	file_size = os.path.getsize(filename)
	if file_size <= chunk_size:
		chunk_size = file_size
	needed_chunks, remainder = divmod(file_size, chunk_size)
	_log.debug('file data: %s bytes, chunks: %s, chunk size: %s bytes, remainder: %s bytes', file_size, needed_chunks, chunk_size, remainder)

	if conn is None:
		conn = get_raw_connection(readonly = False)
		close_conn = conn.close
	else:
		close_conn = __noop

	infile = open(filename, "rb")
	# write chunks
	for chunk_id in range(needed_chunks):
		chunk_start = (chunk_id * chunk_size) + 1
		args['start'] = chunk_start
		args['size'] = chunk_size
		data_as_byte_string = infile.read(chunk_size)
		# really still needed for BYTEA input ?
		args['data'] = memoryview(data_as_byte_string)
		del(data_as_byte_string)
		try:
			rows, idx = run_rw_queries(link_obj = conn, queries = [{'cmd': query, 'args': args}], end_tx = False, return_data = False)
		except Exception:
			_log.exception('cannot write chunk [%s/%s] of size [%s], try decreasing chunk size', chunk_id+1, needed_chunks, chunk_size)
			conn.rollback()
			close_conn()
			infile.close()
			raise
	# write remainder
	if remainder > 0:
		chunk_start = (needed_chunks * chunk_size) + 1
		args['start'] = chunk_start
		args['size'] = remainder
		data_as_byte_string = infile.read(remainder)
		# really still needed for BYTEA input ?
		args['data'] = memoryview(data_as_byte_string)
		del(data_as_byte_string)
		try:
			rows, idx = run_rw_queries(link_obj = conn, queries = [{'cmd': query, 'args': args}], end_tx = False, return_data = False)
		except Exception:
			_log.error('cannot retrieve remaining [%s] bytes' % remainder)
			conn.rollback()
			close_conn()
			infile.close()
			raise
	infile.close()
	if None in [file_md5, md5_query]:
		conn.commit()
		close_conn()
		return True
	# verify
	rows, idx = run_ro_queries(link_obj = conn, queries = [{'cmd': md5_query, 'args': args}])
	db_md5 = rows[0][0]
	if file_md5 == db_md5:
		conn.commit()
		close_conn()
		_log.debug('MD5 sums of data file and database BYTEA field match: [file::%s] = [DB::%s]', file_md5, db_md5)
		return True
	close_conn()
	_log.error('MD5 sums of data file and database BYTEA field do not match: [file::%s] <> [DB::%s]', file_md5, db_md5)
	return False

#------------------------------------------------------------------------
def read_all_rows_of_table(schema=None, table=None):
	if schema is None:
		schema = prompted_input(prompt = 'schema for table to dump', default = None)
		if schema is None:
			_log.debug('aborted by user (no schema entered)')
			return None

	if table is None:
		table = prompted_input(prompt = 'table to dump (in schema %s.)' % schema, default = None)
		if table is None:
			_log.debug('aborted by user (no table entered)')
			return None

	_log.debug('dumping <%s.%s>', schema, table)
	conn = get_connection(readonly=True, verbose = False, pooled = True, connection_name = 'read_all_rows_of_table')
	# get pk column name
	rows, idx = run_ro_queries(link_obj = conn, queries = [{'cmd': SQL_get_primary_key_name, 'args': {'schema': schema, 'table': table}}])
	if rows:
		_log.debug('primary key def: %s', rows)
		if len(rows) > 1:
			_log.error('cannot handle multi-column primary key')
			return False

		pk_name = rows[0][0]
	else:
		_log.debug('cannot determine primary key, asking user')
		pk_name = prompted_input(prompt = 'primary key name for %s.%s' % (schema, table), default = None)
		if pk_name is None:
			_log.debug('aborted by user (no primary key name entered)')
			return None

	# get PK values
	qualified_table = '%s.%s' % (schema, table)
	qualified_pk_name = '%s.%s.%s' % (schema, table, pk_name)
	cmd = psysql.SQL('SELECT {schema_table_pk} FROM {schema_table} ORDER BY 1'.format (
		schema_table_pk = qualified_pk_name,
		schema_table = qualified_table
	))
	rows, idx = run_ro_queries(link_obj = conn, queries = [{'cmd': cmd}])
	if not rows:
		_log.debug('no rows to dump')
		return True

	# dump table rows
	_log.debug('dumping %s rows', len(rows))
	cmd = psysql.SQL('SELECT * FROM {schema_table} WHERE {schema_table_pk} = %(pk_val)s'.format (
		schema_table = qualified_table,
		schema_table_pk = qualified_pk_name
	))
	found_errors = False
	idx = 0
	for row in rows:
		idx += 1
		args = {'pk_val': row[0]}
		_log.debug('dumping row #%s with pk [%s]', idx, row[0])
		try:
			run_ro_queries(link_obj = conn, queries = [{'cmd': cmd, 'args': args}])
		except dbapi.InternalError:
			found_errors = True
			_log.exception('error dumping row')
			print('ERROR: cannot dump row %s of %s with pk %s = %s', idx, len(rows), qualified_pk_name, rows[0])

	return found_errors is False

#------------------------------------------------------------------------
#------------------------------------------------------------------------
def run_sql_script(sql_script, conn=None):

	if conn is None:
		conn = get_connection(readonly = False)

	from Gnumed.pycommon import gmPsql
	psql = gmPsql.Psql(conn)

	if psql.run(sql_script) == 0:
		query = {
			'cmd': 'select gm.log_script_insertion(%(name)s, %(ver)s)',
			'args': {'name': sql_script, 'ver': 'current'}
		}
		run_rw_queries(link_obj = conn, queries = [query])
		conn.commit()
		return True

	_log.error('error running sql script: %s', sql_script)
	return False

#------------------------------------------------------------------------
def sanitize_pg_regex(expression=None, escape_all=False):
	"""Escape input for use in a PostgreSQL regular expression.

	If a fragment comes from user input and is to be used
	as a regular expression we need to make sure it doesn't
	contain invalid regex patterns such as unbalanced ('s.

	<escape_all>
		True: try to escape *all* metacharacters
		False: only escape those which render the regex invalid
	"""
	return expression.replace (
			'(', '\('
		).replace (
			')', '\)'
		).replace (
			'[', '\['
		).replace (
			'+', '\+'
		).replace (
			'.', '\.'
		).replace (
			'*', '\*'
		).replace (
			'?', '\?'
		)
		#']', '\]',			# not needed

#------------------------------------------------------------------------
def run_ro_queries(link_obj=None, queries=None, verbose=False, return_data=True, get_col_idx=False):
	"""Run read-only queries.

	<queries> must be a list of dicts:
		[
			{'cmd': <string>, 'args': <dict> or <tuple>},
			{...},
			...
		]
	"""
	if isinstance(link_obj, dbapi._psycopg.cursor):
		curs = link_obj
		curs_close = lambda *x:None
		tx_rollback = lambda *x:None
		readonly_rollback_just_in_case = lambda *x:None
	elif isinstance(link_obj, dbapi._psycopg.connection):
		curs = link_obj.cursor()
		curs_close = curs.close
		tx_rollback = link_obj.rollback
		if link_obj.autocommit is True:		# readonly connection ?
			readonly_rollback_just_in_case = link_obj.rollback
		else:
			# do not rollback readonly queries on passed-in readwrite
			# connections just in case because they may have already
			# seen fully legitimate write action which would get lost
			readonly_rollback_just_in_case = lambda *x:None
	elif link_obj is None:
		conn = get_connection(readonly = True, verbose = verbose)
		curs = conn.cursor()
		curs_close = curs.close
		tx_rollback = conn.rollback
		readonly_rollback_just_in_case = conn.rollback
	else:
		raise ValueError('link_obj must be cursor, connection or None but not [%s]' % link_obj)

	if verbose:
		_log.debug('cursor: %s', curs)

	for query in queries:
		try:
			args = query['args']
		except KeyError:
			args = None
		try:
			curs.execute(query['cmd'], args)
			if verbose:
				gmConnectionPool.log_cursor_state(curs)
		except PG_ERROR_EXCEPTION as pg_exc:
			_log.error('query failed in RO connection')
			gmConnectionPool.log_pg_exception_details(pg_exc)
			try:
				curs_close()
			except PG_ERROR_EXCEPTION as pg_exc2:
				_log.exception('cannot close cursor')
				gmConnectionPool.log_pg_exception_details(pg_exc2)
			try:
				tx_rollback()		# need to rollback so ABORT state isn't preserved in pooled conns
			except PG_ERROR_EXCEPTION as pg_exc2:
				_log.exception('cannot rollback transaction')
				gmConnectionPool.log_pg_exception_details(pg_exc2)
			if pg_exc.pgcode == sql_error_codes.INSUFFICIENT_PRIVILEGE:
				details = 'Query: [%s]' % curs.query.strip().strip('\n').strip().strip('\n')
				if curs.statusmessage != '':
					details = 'Status: %s\n%s' % (
						curs.statusmessage.strip().strip('\n').strip().strip('\n'),
						details
					)
				if pg_exc.pgerror is None:
					msg = '[%s]' % pg_exc.pgcode
				else:
					msg = '[%s]: %s' % (pg_exc.pgcode, pg_exc.pgerror)
				raise gmExceptions.AccessDenied (
					msg,
					source = 'PostgreSQL',
					code = pg_exc.pgcode,
					details = details
				)
			raise
		except Exception:
			_log.exception('error during query run in RO connection')
			gmConnectionPool.log_cursor_state(curs)
			try:
				curs_close()
			except PG_ERROR_EXCEPTION as pg_exc:
				_log.exception('cannot close cursor')
				gmConnectionPool.log_pg_exception_details(pg_exc)
			try:
				tx_rollback()		# need to rollback so ABORT state isn't preserved in pooled conns
			except PG_ERROR_EXCEPTION as pg_exc:
				_log.exception('cannot rollback transation')
				gmConnectionPool.log_pg_exception_details(pg_exc)
			raise

	data = None
	col_idx = None
	if return_data:
		data = curs.fetchall()
		if verbose:
			_log.debug('last query returned [%s (%s)] rows', curs.rowcount, len(data))
			_log.debug('cursor description: %s', curs.description)
		if get_col_idx:
			col_idx = get_col_indices(curs)

	curs_close()
	# so we can see data committed meanwhile if the
	# link object had been passed in and thusly might
	# be part of a long-running read-only transaction
	readonly_rollback_just_in_case()
	return (data, col_idx)

#------------------------------------------------------------------------
def run_rw_queries(link_obj=None, queries=None, end_tx=False, return_data=None, get_col_idx=False, verbose=False):
	"""Convenience function for running a transaction
	   that is supposed to get committed.

	<link_obj>
		can be either:
		- a cursor
		- a connection

	<queries>
		is a list of dicts [{'cmd': <string>, 'args': <dict> or <tuple>)
		to be executed as a single transaction, the last
		query may usefully return rows (such as a
		"SELECT currval('some_sequence')" statement)

	<end_tx>
		- controls whether the transaction is finalized (eg.
		  COMMITted/ROLLed BACK) or not, this allows the
		  call to run_rw_queries() to be part of a framing
		  transaction
		- if link_obj is a *connection* then <end_tx> will
		  default to False unless it is explicitly set to
		  True which is taken to mean "yes, you do have full
		  control over the transaction" in which case the
		  transaction is properly finalized
		- if link_obj is a *cursor* we CANNOT finalize the
		  transaction because we would need the connection for that
		- if link_obj is *None* <end_tx> will, of course, always be True

	<return_data>
		- if true, the returned data will include the rows
		  the last query selected
		- if false, it returns None instead

	<get_col_idx>
		- if true, the returned data will include a dictionary
		  mapping field names to column positions
		- if false, the returned data returns None instead

	method result:
		- returns a tuple (data, idx)
		- <data>:
			* (None, None) if last query did not return rows
			* ("fetchall() result", <index>) if last query returned any rows
			* for <index> see <get_col_idx>
	"""
	if isinstance(link_obj, dbapi._psycopg.cursor):
		conn_close = lambda *x:None
		conn_commit = lambda *x:None
		tx_rollback = lambda *x:None
		curs = link_obj
		curs_close = lambda *x:None
		notices_accessor = curs.connection
	elif isinstance(link_obj, dbapi._psycopg.connection):
		conn_close = lambda *x:None
		if end_tx:
			conn_commit = link_obj.commit
			tx_rollback = link_obj.rollback
		else:
			conn_commit = lambda *x:None
			tx_rollback = lambda *x:None
		curs = link_obj.cursor()
		curs_close = curs.close
		notices_accessor = link_obj
	elif link_obj is None:
		conn = get_connection(readonly=False)
		conn_close = conn.close
		conn_commit = conn.commit
		tx_rollback = conn.rollback
		curs = conn.cursor()
		curs_close = curs.close
		notices_accessor = conn
	else:
		raise ValueError('link_obj must be cursor, connection or None but not [%s]' % link_obj)

	for query in queries:
		try:
			args = query['args']
		except KeyError:
			args = None
		try:
			curs.execute(query['cmd'], args)
			if verbose:
				gmConnectionPool.log_cursor_state(curs)
			for notice in notices_accessor.notices:
				_log.debug(notice.replace('\n', '/').replace('\n', '/'))
			del notices_accessor.notices[:]
		# DB related exceptions
		except dbapi.Error as pg_exc:
			_log.error('query failed in RW connection')
			gmConnectionPool.log_pg_exception_details(pg_exc)
			for notice in notices_accessor.notices:
				_log.debug(notice.replace('\n', '/').replace('\n', '/'))
			del notices_accessor.notices[:]
			try:
				curs_close()
			except PG_ERROR_EXCEPTION as pg_exc2:
				_log.exception('cannot close cursor')
				gmConnectionPool.log_pg_exception_details(pg_exc2)
			try:
				tx_rollback()		# need to rollback so ABORT state isn't preserved in pooled conns
			except PG_ERROR_EXCEPTION as pg_exc2:
				_log.exception('cannot rollback transaction')
				gmConnectionPool.log_pg_exception_details(pg_exc2)
			# privilege problem
			if pg_exc.pgcode == sql_error_codes.INSUFFICIENT_PRIVILEGE:
				details = 'Query: [%s]' % curs.query.strip().strip('\n').strip().strip('\n')
				if curs.statusmessage != '':
					details = 'Status: %s\n%s' % (
						curs.statusmessage.strip().strip('\n').strip().strip('\n'),
						details
					)
				if pg_exc.pgerror is None:
					msg = '[%s]' % pg_exc.pgcode
				else:
					msg = '[%s]: %s' % (pg_exc.pgcode, pg_exc.pgerror)
				try:
					curs_close()
					tx_rollback()			# just for good measure
					conn_close()
				except dbapi.InterfaceError:
					_log.exception('cannot cleanup')
				raise gmExceptions.AccessDenied (
					msg,
					source = 'PostgreSQL',
					code = pg_exc.pgcode,
					details = details
				)
			# other problem
			gmLog2.log_stack_trace()
			try:
				curs_close()
				tx_rollback()			# just for good measure
				conn_close()
			except dbapi.InterfaceError:
				_log.exception('cannot cleanup')
			raise
		# other exception
		except Exception:
			_log.exception('error running query in RW connection')
			gmConnectionPool.log_cursor_state(curs)
			for notice in notices_accessor.notices:
				_log.debug(notice.replace('\n', '/').replace('\n', '/'))
			del notices_accessor.notices[:]
			gmLog2.log_stack_trace()
			try:
				curs_close()
			except PG_ERROR_EXCEPTION as pg_exc:
				_log.exception('cannot close cursor')
				gmConnectionPool.log_pg_exception_details(pg_exc)
			try:
				tx_rollback()		# need to rollback so ABORT state isn't preserved in pooled conns
				conn_close()
			except PG_ERROR_EXCEPTION as pg_exc:
				_log.exception('cannot rollback transation')
				gmConnectionPool.log_pg_exception_details(pg_exc)
			raise

	data = None
	col_idx = None
	if return_data:
		try:
			data = curs.fetchall()
		except Exception:
			_log.exception('error fetching data from RW query')
			gmLog2.log_stack_trace()
			try:
				curs_close()
				tx_rollback()
				conn_close()
			except dbapi.InterfaceError:
				_log.exception('cannot cleanup')
				raise
			raise
		if get_col_idx:
			col_idx = get_col_indices(curs)

	curs_close()
	conn_commit()
	conn_close()

	return (data, col_idx)

#------------------------------------------------------------------------
def run_insert(link_obj=None, schema=None, table=None, values=None, returning=None, end_tx=False, get_col_idx=False, verbose=False):
	"""Generates SQL for an INSERT query.

	values: dict of values keyed by field to insert them into
	"""
	if schema is None:
		schema = 'public'

	fields = list(values)		# that way val_snippets and fields really should end up in the same order
	val_snippets = []
	for field in fields:
		val_snippets.append('%%(%s)s' % field)

	if returning is None:
		returning = ''
		return_data = False
	else:
		returning = '\n\tRETURNING\n\t\t%s' % ', '.join(returning)
		return_data = True

	cmd = """\nINSERT INTO %s.%s (
		%s
	) VALUES (
		%s
	)%s""" % (
		schema,
		table,
		',\n\t\t'.join(fields),
		',\n\t\t'.join(val_snippets),
		returning
	)

	_log.debug('running SQL: >>>%s<<<', cmd)

	return run_rw_queries (
		link_obj = link_obj,
		queries = [{'cmd': cmd, 'args': values}],
		end_tx = end_tx,
		return_data = return_data,
		get_col_idx = get_col_idx,
		verbose = verbose
	)

# =======================================================================
# connection handling API
# -----------------------------------------------------------------------
def get_raw_connection(verbose=False, readonly=True, connection_name=None, autocommit=False):
	"""Get a raw, unadorned connection.

	- this will not set any parameters such as encoding, timezone, datestyle
	- the only requirement is valid connection parameters having been passed to the connection pool
	- hence it can be used for "service" connections
	  for verifying encodings etc
	"""
	return gmConnectionPool.gmConnectionPool().get_raw_connection (
		readonly = readonly,
		verbose = verbose,
		connection_name = connection_name,
		autocommit = autocommit
	)

# =======================================================================
def get_connection(readonly=True, verbose=False, pooled=True, connection_name=None, autocommit=False):
	return gmConnectionPool.gmConnectionPool().get_connection (
		readonly = readonly,
		verbose = verbose,
		connection_name = connection_name,
		autocommit = autocommit,
		pooled = pooled
	)

#-----------------------------------------------------------------------
def discard_pooled_connection_of_thread():
	gmConnectionPool.gmConnectionPool().discard_pooled_connection_of_thread()

#-----------------------------------------------------------------------
def shutdown():
	gmConnectionPool.gmConnectionPool().shutdown()

# ======================================================================
# internal helpers
#-----------------------------------------------------------------------
def __noop():
	pass

#-----------------------------------------------------------------------
def log_database_access(action=None):
	run_insert (
		schema = 'gm',
		table = 'access_log',
		values = {'user_action': action},
		end_tx = True
	)

#-----------------------------------------------------------------------
def sanity_check_time_skew(tolerance=60):
	"""Check server time and local time to be within
	the given tolerance of each other.

	tolerance: seconds
	"""
	_log.debug('maximum skew tolerance (seconds): %s', tolerance)

	cmd = "SELECT now() at time zone 'UTC'"
	conn = get_raw_connection(readonly=True)
	curs = conn.cursor()

	start = time.time()
	rows, idx = run_ro_queries(link_obj = curs, queries = [{'cmd': cmd}])
	end = time.time()
	client_now_as_utc = pydt.datetime.utcnow()

	curs.close()
	conn.commit()

	server_now_as_utc = rows[0][0]
	query_duration = end - start
	_log.info('server "now" (UTC): %s', server_now_as_utc)
	_log.info('client "now" (UTC): %s', client_now_as_utc)
	_log.debug('wire roundtrip (seconds): %s', query_duration)

	if query_duration > tolerance:
		_log.error('useless to check client/server time skew, wire roundtrip > tolerance')
		return False

	if server_now_as_utc > client_now_as_utc:
		real_skew = server_now_as_utc - client_now_as_utc
	else:
		real_skew = client_now_as_utc - server_now_as_utc

	_log.debug('client/server time skew: %s', real_skew)

	if real_skew > pydt.timedelta(seconds = tolerance):
		_log.error('client/server time skew > tolerance')
		return False

	return True

#-----------------------------------------------------------------------
def sanity_check_database_settings(hipaa:bool=False) -> (int, str):
	"""Checks database settings.

	returns (status, message)
	status:
		0: no problem
		1: non-fatal problem
		2: fatal problem
	"""
	_log.debug('checking database settings')

	conn = get_connection()

	# - version string
	global postgresql_version_string
	if postgresql_version_string is None:
		curs = conn.cursor()
		curs.execute('SELECT version()')
		postgresql_version_string = curs.fetchone()['version']
		curs.close()
		_log.info('PostgreSQL version (string): "%s"' % postgresql_version_string)

	options2check = {
		# setting: [expected value, risk, fatal?]
		'allow_system_table_mods': [['off'], 'system breakage', False],
		'check_function_bodies': [['on'], 'suboptimal error detection', False],
		'datestyle': [['ISO'], 'faulty timestamp parsing', True],
		'default_transaction_isolation': [['read committed'], 'faulty database reads', True],
		'default_transaction_read_only': [['on'], 'accidental database writes', False],
		'fsync': [['on'], 'data loss/corruption', True],
		'full_page_writes': [['on'], 'data loss/corruption', False],
		'lc_messages': [['C'], 'suboptimal error detection', False],
		'password_encryption': [['on', 'md5', 'scram-sha-256'], 'breach of confidentiality', False],
		#u'regex_flavor': [[u'advanced'], u'query breakage', False],					# 9.0 doesn't support this anymore, default now advanced anyway
		'synchronous_commit': [['on'], 'data loss/corruption', False],
		'sql_inheritance': [['on'], 'query breakage, data loss/corruption', True],	# IF returned (<PG10): better be ON, if NOT returned (PG10): hardwired
		'ignore_checksum_failure': [['off'], 'data loss/corruption', False],		# starting with PG 9.3
		'track_commit_timestamp': [['on'], 'suboptimal auditing', False],			# starting with PG 9.3
	}
	if hipaa:
		options2check['log_connections'] = [['on'], 'non-compliance with HIPAA', True]
		options2check['log_disconnections'] = [['on'], 'non-compliance with HIPAA', True]
	else:
		options2check['log_connections'] = [['on'], 'non-compliance with HIPAA', None]
		options2check['log_disconnections'] = [['on'], 'non-compliance with HIPAA', None]

	cmd = "SELECT name, setting from pg_settings where name in %(settings)s"
	rows, idx = run_ro_queries (
		link_obj = conn,
		queries = [{'cmd': cmd, 'args': {'settings': tuple(options2check)}}],
		get_col_idx = False
	)
	found_error = False
	found_problem = False
	msg = []
	for row in rows:
		option = row['name']
		value_found = row['setting']
		values_expected = options2check[option][0]
		risk = options2check[option][1]
		fatal_setting = options2check[option][2]
		if value_found not in values_expected:
			if fatal_setting is True:
				found_error = True
			elif fatal_setting is False:
				found_problem = True
			elif fatal_setting is None:
				pass
			else:
				_log.error(options2check[option])
				raise ValueError('invalid database configuration sanity check')

			msg.append(_(' option [%s]: %s') % (option, value_found))
			msg.append(_('  risk: %s') % risk)
			_log.warning('PG option [%s] set to [%s], expected %s, risk: <%s>' % (option, value_found, values_expected, risk))
#	SQL = "SELECT name, setting from pg_settings where name = 'shared_preload_libraries';"
#	rows, idx = run_ro_queries (link_obj = conn, queries = [{'cmd': SQL, 'args': None}])
#	if rows:
#		value_found = rows[0]['setting']
#	else:
#		value_found = []
#	if 'auto_explain' not in value_found:
#		msg.append(_(' option [shared_preload_libraries]: %s') % value_found)
#		msg.append(_('  risk: suboptimal debugging'))
#		_log.warning('PG option [shared_preload_libraries] set to: %s, expected to include "auto_explain", risk: <suboptimal debugging>', value_found)
#		found_problem = True

	if found_error:
		return 2, '\n'.join(msg)

	if found_problem:
		return 1, '\n'.join(msg)

	return 0, ''

#=======================================================================
#  main
#-----------------------------------------------------------------------
log_pg_exception_details = gmConnectionPool.log_pg_exception_details

exception_is_connection_loss = gmConnectionPool.exception_is_connection_loss

cAuthenticationError = gmConnectionPool.cAuthenticationError

#-----------------------------------------------------------------------
if __name__ == "__main__":

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	from Gnumed.pycommon.gmTools import file2md5

	logging.basicConfig(level=logging.DEBUG)

	#--------------------------------------------------------------------
	def test_file2bytea():
		login, creds = request_login_params()
		pool = gmConnectionPool.gmConnectionPool()
		pool.credentials = creds
		run_rw_queries(queries = [
			{'cmd': 'drop table if exists test_bytea'},
			{'cmd': 'create table test_bytea (data bytea)'}
		])
		try:
			#file2bytea(query = 'insert into test_bytea values (%(data)s::bytea) returning md5(data) as md5', filename = sys.argv[2], file_md5 = file2md5(sys.argv[2], True))
			file2bytea(query = 'insert into test_bytea values (%(data)s::bytea)', filename = sys.argv[2])
		except Exception:
			_log.exception('error')

		run_rw_queries(queries = [
			{'cmd': 'drop table test_bytea'}
		])

	#--------------------------------------------------------------------
	def test_file2bytea_lo():
		login, creds = request_login_params()
		pool = gmConnectionPool.gmConnectionPool()
		pool.credentials = creds

		lo_oid = file2bytea_lo (
			filename = sys.argv[2]
			#, file_md5 = file2md5(sys.argv[2], True)
		)
		print(lo_oid)
#		if lo_oid != -1:
#			run_rw_queries(queries = [
#				{'cmd': u'select lo_unlink(%(loid)s::oid)', 'args': {'loid': lo_oid}}
#			])

	#--------------------------------------------------------------------
	def test_file2bytea_copy_from():
		login, creds = request_login_params()
		pool = gmConnectionPool.gmConnectionPool()
		pool.credentials = creds

		run_rw_queries(queries = [
			{'cmd': 'drop table if exists test_bytea'},
			{'cmd': 'create table test_bytea (pk serial primary key, data bytea)'},
			{'cmd': "insert into test_bytea (data) values (NULL::bytea)"}
		])

		md5_query = {
			'cmd': 'select md5(data) AS md5 FROM test_bytea WHERE pk = %(pk)s',
			'args': {'pk': 1}
		}

		file2bytea_copy_from (
			table = 'test_bytea',
			columns = ['data'],
			filename = sys.argv[2],
			md5_query = md5_query,
			file_md5 = file2md5(sys.argv[2], True)
		)

		run_rw_queries(queries = [
			{'cmd': 'drop table if exists test_bytea'}
		])

	#--------------------------------------------------------------------
	def test_file2bytea_overlay():
		login, creds = request_login_params()
		pool = gmConnectionPool.gmConnectionPool()
		pool.credentials = creds

		run_rw_queries(queries = [
			{'cmd': 'drop table if exists test_bytea'},
			{'cmd': 'create table test_bytea (pk serial primary key, data bytea)'},
			{'cmd': "insert into test_bytea (data) values (NULL::bytea)"}
		])

		cmd = """
		update test_bytea
		set data = overlay (
			coalesce(data, ''::bytea)
			placing %(data)s::bytea
			from %(start)s
			for %(size)s
		)
		where
			pk > %(pk)s
		"""
		md5_cmd = 'select md5(data) from test_bytea'
		args = {'pk': 0}
		file2bytea_overlay (
			query = cmd,
			args = args,
			filename = sys.argv[2],
			conn = None,
			md5_query = md5_cmd,
			file_md5 = file2md5(sys.argv[2], True)
		)

		run_rw_queries(queries = [
			{'cmd': 'drop table test_bytea'}
		])

	#--------------------------------------------------------------------
	def test_get_connection():
		print("testing get_connection()")

		login, creds = request_login_params()
		pool = gmConnectionPool.gmConnectionPool()
		pool.credentials = creds

		print('')
		dsn = 'foo'
		try:
			conn = get_connection(dsn=dsn)
		except dbapi.ProgrammingError as e:
			print("1) SUCCESS: get_connection(%s) failed as expected" % dsn)
			t, v = sys.exc_info()[:2]
			print (' ', t)
			print (' ', v)

		print('')
		dsn = 'dbname=gnumed_v22'
		try:
			conn = get_connection(dsn=dsn)
			print("2) ERROR: get_connection() did not fail")
		except cAuthenticationError:
			print("2) SUCCESS: get_connection(%s) failed as expected" % dsn)
			t, v = sys.exc_info()[:2]
			print(' ', t)
			print(' ', v)

		print('')
		dsn = 'dbname=gnumed_v22 user=abc'
		try:
			conn = get_connection(dsn=dsn)
			print("3) ERROR: get_connection() did not fail")
		except cAuthenticationError:
			print("3) SUCCESS: get_connection(%s) failed as expected" % dsn)
			t, v = sys.exc_info()[:2]
			print(' ', t)
			print(' ', v)

		print('')
		dsn = 'dbname=gnumed_v22 user=any-doc password=abc'
		try:
			conn = get_connection(dsn=dsn)
			print("4) ERROR: get_connection() did not fail")
		except cAuthenticationError:
			print("4) SUCCESS: get_connection(%s) failed as expected" % dsn)
			t, v = sys.exc_info()[:2]
			print(' ', t)
			print(' ', v)

		print('')
		dsn = 'dbname=gnumed_v22 user=any-doc password=any-doc'
		conn = get_connection(dsn=dsn, readonly=True)
		print('5) SUCCESS: get_connection(ro)')

		dsn = 'dbname=gnumed_v22 user=any-doc password=any-doc'
		conn = get_connection(dsn=dsn, readonly=False, verbose=True)
		print('6) SUCCESS: get_connection(rw)')

		print('')
		dsn = 'dbname=gnumed_v22 user=any-doc'
		try:
			conn = get_connection(dsn=dsn)
			print("8) SUCCESS:", dsn)
			print('pid:', conn.get_backend_pid())
		except cAuthenticationError:
			print("4) SUCCESS: get_connection(%s) failed" % dsn)
			t, v = sys.exc_info()[:2]
			print(' ', t)
			print(' ', v)

		try:
			curs = conn.cursor()
			input('hit enter to run query')
			curs.execute('selec 1')
		except Exception as exc:
			print('ERROR')
			_log.exception('exception occurred')
			gmConnectionPool.log_pg_exception_details(exc)
			if gmConnectionPool.exception_is_connection_loss(exc):
				_log.error('lost connection')

	#--------------------------------------------------------------------
	def test_ro_queries():
		login, creds = request_login_params()
		pool = gmConnectionPool.gmConnectionPool()
		pool.credentials = creds

		print("testing run_ro_queries()")

		dsn = 'dbname=gnumed_v22 user=any-doc password=any-doc'
		conn = get_connection(dsn, readonly=True)

		data, idx = run_ro_queries(link_obj=conn, queries=[{'cmd': 'SELECT version()'}], return_data=True, get_col_idx=True, verbose=True)
		print(data)
		print(idx)
		data, idx = run_ro_queries(link_obj=conn, queries=[{'cmd': 'SELECT 1'}], return_data=True, get_col_idx=True)
		print(data)
		print(idx)

		curs = conn.cursor()

		data, idx = run_ro_queries(link_obj=curs, queries=[{'cmd': 'SELECT version()'}], return_data=True, get_col_idx=True, verbose=True)
		print(data)
		print(idx)

		data, idx = run_ro_queries(link_obj=curs, queries=[{'cmd': 'SELECT 1'}], return_data=True, get_col_idx=True, verbose=True)
		print(data)
		print(idx)

		try:
			data, idx = run_ro_queries(link_obj=curs, queries=[{'cmd': 'selec 1'}], return_data=True, get_col_idx=True, verbose=True)
			print(data)
			print(idx)
		except psycopg2.ProgrammingError:
			print('SUCCESS: run_ro_queries("selec 1") failed as expected')
			t, v = sys.exc_info()[:2]
			print(' ', t)
			print(' ', v)

		curs.close()

	#--------------------------------------------------------------------
	def test_connection_pool():
		login, creds = request_login_params()
		pool = gmConnectionPool.gmConnectionPool()
		pool.credentials = creds
		print(pool)
		print(pool.get_connection())
		print(pool.get_connection())
		print(pool.get_connection())
		print(type(pool.get_connection()))

	#--------------------------------------------------------------------
	def test_list_args():
		login, creds = request_login_params()
		pool = gmConnectionPool.gmConnectionPool()
		pool.credentials = creds
		conn = get_connection('', readonly=True)
		curs = conn.cursor()
		curs.execute('SELECT * from clin.clin_narrative where narrative = %s', ['a'])

	#--------------------------------------------------------------------
	def test_sanitize_pg_regex():
		tests = [
			['(', '\\(']
			, ['[', '\\[']
			, [')', '\\)']
		]
		for test in tests:
			result = sanitize_pg_regex(test[0])
			if result != test[1]:
				print('ERROR: sanitize_pg_regex(%s) returned "%s", expected "%s"' % (test[0], result, test[1]))

	#--------------------------------------------------------------------
	def test_is_pg_interval():
		login, creds = request_login_params()
		pool = gmConnectionPool.gmConnectionPool()
		pool.credentials = creds
		status = True
		tests = [
			[None, True],		# None == NULL == succeeds !
			[1, True],
			['1', True],
			['abc', False]
		]

		if not is_pg_interval():
			print('ERROR: is_pg_interval() returned "False", expected "True"')
			status = False

		for test in tests:
			result = is_pg_interval(test[0])
			if result != test[1]:
				print('ERROR: is_pg_interval(%s) returned "%s", expected "%s"' % (test[0], result, test[1]))
				status = False

		return status

	#--------------------------------------------------------------------
	def test_sanity_check_database_settings():
		login, creds = request_login_params()
		pool = gmConnectionPool.gmConnectionPool()
		pool.credentials = creds
		print(sanity_check_database_settings(hipaa = True))

	#--------------------------------------------------------------------
	def test_sanity_check_time_skew():
		login, creds = request_login_params()
		pool = gmConnectionPool.gmConnectionPool()
		pool.credentials = creds
		sanity_check_time_skew()

	#--------------------------------------------------------------------
	def test_get_foreign_key_details():
		login, creds = request_login_params()
		pool = gmConnectionPool.gmConnectionPool()
		pool.credentials = creds
		schema = 'clin'
		table = 'episode'
		col = 'pk'
		print('column %s.%s.%s is referenced by:' % (schema, table, col))
		for row in get_foreign_keys2column (
			schema = schema,
			table = table,
			column = col
		):
			print(' <- %s.%s' % (
				row['referencing_table'],
				row['referencing_column']
			))

	#--------------------------------------------------------------------
	def test_set_user_language():
		login, creds = request_login_params()
		pool = gmConnectionPool.gmConnectionPool()
		pool.credentials = creds
		# (user, language, result, exception type)
		tests = [
			# current user
			[None, 'de_DE', True],
			[None, 'lang_w/o_tx', False],
			[None, None, True],
			# valid user
			['any-doc', 'de_DE', True],
			['any-doc', 'lang_w/o_tx', False],
			['any-doc', None, True],
			# invalid user
			['invalid user', 'de_DE', None],
			['invalid user', 'lang_w/o_tx', False], # lang checking happens before user checking
			['invalid user', None, True]
		]
		for test in tests:
			print('testing: %s', test)
			try:
				result = set_user_language(user = test[0], language = test[1])
				if result != test[2]:
					print("test:", test)
					print("result:", result, "expected:", test[2])
			except psycopg2.IntegrityError as e:
				print(e)
				if test[2] is None:
					continue
				print("test:", test)
				print("expected exception")
				print("result:", e)

	#--------------------------------------------------------------------
	def test_get_schema_revision_history():
		login, creds = request_login_params()
		pool = gmConnectionPool.gmConnectionPool()
		pool.credentials = creds
		for line in get_schema_revision_history():
			print(' - '.join(line))

	#--------------------------------------------------------------------
	def test_run_query():
		login, creds = request_login_params()
		pool = gmConnectionPool.gmConnectionPool()
		pool.credentials = creds
		gmDateTime.init()
		args = {'dt': gmDateTime.pydt_max_here()}
		cmd = "SELECT %(dt)s"

		#cmd = u"SELECT 'infinity'::timestamp with time zone"

		cmd = """
SELECT to_timestamp (foofoo,'YYMMDD.HH24MI') FROM (
	SELECT REGEXP_REPLACE (
		't1.130729.0902.tif',			-- string
		E'(.1)\.([0-9\.]+)(\.tif)',		-- pattern
		E'\\\\2'						-- replacement
	) AS foofoo
) AS foo"""
		rows, idx = run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = False)
		print(rows)
		print(rows[0])
		print(rows[0][0])

	#--------------------------------------------------------------------
	def test_schema_exists():
		login, creds = request_login_params()
		pool = gmConnectionPool.gmConnectionPool()
		pool.credentials = creds
		print(schema_exists())

	#--------------------------------------------------------------------
	def test_row_locks():
		login, creds = request_login_params()
		pool = gmConnectionPool.gmConnectionPool()
		pool.credentials = creds

		row_is_locked(table = 'dem.identity', pk = 12)

		print("on 1st connection:")
		print(" locked:", row_is_locked(table = 'dem.identity', pk = 12))
		print(" 1st shared lock succeeded:", lock_row(table = 'dem.identity', pk = 12, exclusive = False))
		print(" locked:", row_is_locked(table = 'dem.identity', pk = 12))

		print("   2nd shared lock should succeed:", lock_row(table = 'dem.identity', pk = 12, exclusive = False))
		print("   `-> unlock succeeded:", unlock_row(table = 'dem.identity', pk = 12, exclusive = False))
		print(" locked:", row_is_locked(table = 'dem.identity', pk = 12))
		print("   exclusive lock should succeed:", lock_row(table = 'dem.identity', pk = 12, exclusive = True))
		print("   `-> unlock succeeded:", unlock_row(table = 'dem.identity', pk = 12, exclusive = True))
		print(" locked:", row_is_locked(table = 'dem.identity', pk = 12))

		print("on 2nd connection:")
		conn = get_raw_connection(readonly=True)
		print(" shared lock should succeed:", lock_row(link_obj = conn, table = 'dem.identity', pk = 12, exclusive = False))
		print(" `-> unlock succeeded:", unlock_row(link_obj = conn, table = 'dem.identity', pk = 12, exclusive = False))
		print(" locked:", row_is_locked(table = 'dem.identity', pk = 12))
		print(" exclusive lock succeeded:", lock_row(link_obj = conn, table = 'dem.identity', pk = 12, exclusive = True), "(should be False)")
		print(" locked:", row_is_locked(table = 'dem.identity', pk = 12))

		print("on 1st connection again:")
		print(" unlock succeeded:", unlock_row(table = 'dem.identity', pk = 12, exclusive = False))
		print(" locked:", row_is_locked(table = 'dem.identity', pk = 12))

		print("on 2nd connection:")
		print(" exclusive lock should succeed:", lock_row(link_obj = conn, table = 'dem.identity', pk = 12, exclusive = True))
		print(" locked:", row_is_locked(table = 'dem.identity', pk = 12))
		print("  shared lock should succeed:", lock_row(link_obj = conn, table = 'dem.identity', pk = 12, exclusive = False))
		print("  `-> unlock succeeded:", unlock_row(link_obj = conn, table = 'dem.identity', pk = 12, exclusive = False))
		print(" locked:", row_is_locked(table = 'dem.identity', pk = 12))
		print(" unlock succeeded:", unlock_row(link_obj = conn, table = 'dem.identity', pk = 12, exclusive = False))
		print(" locked:", row_is_locked(table = 'dem.identity', pk = 12))

		conn.close()

	#--------------------------------------------------------------------
	def test_get_foreign_key_names():
		login, creds = request_login_params()
		pool = gmConnectionPool.gmConnectionPool()
		pool.credentials = creds
		print(get_foreign_key_names (
			src_schema = 'clin',
			src_table = 'vaccination',
			src_column = 'fk_episode',
			target_schema = 'clin',
			target_table = 'episode',
			target_column = 'pk'
		))
		print(get_foreign_key_names (
			src_schema = 'dem',
			src_table = 'names',
			src_column = 'id_identity',
			target_schema = 'dem',
			target_table = 'identity',
			target_column = 'pk'
		))

	#--------------------------------------------------------------------
	def test_get_index_name():
		login, creds = request_login_params()
		pool = gmConnectionPool.gmConnectionPool()
		pool.credentials = creds
		print(get_index_name(indexed_table = 'clin.vaccination', indexed_column = 'fk_episode'))

	#--------------------------------------------------------------------
	def test_faulty_SQL():
		login, creds = request_login_params()
		pool = gmConnectionPool.gmConnectionPool()
		pool.credentials = creds
		conn = get_connection()
		run_rw_queries(queries = [{'cmd': 'SELEC 1'}])

	#--------------------------------------------------------------------
	def test_log_settings():
		login, creds = request_login_params()
		pool = gmConnectionPool.gmConnectionPool()
		pool.credentials = creds
		conn = get_connection()
		gmConnectionPool.log_pg_settings(curs = conn.cursor())

	#--------------------------------------------------------------------
	def test_get_db_fingerprint():
		login, creds = request_login_params()
		pool = gmConnectionPool.gmConnectionPool()
		pool.credentials = creds
		#conn = get_connection()
		#print(get_db_fingerprint(conn, with_dump = True, eol = '\n'))
		print(get_db_fingerprint(with_dump = True, eol = '\n'))

	#--------------------------------------------------------------------
	# run tests

	# legacy:
	#test_connection_pool()

	# tested:
	#test_file2bytea_lo()
	#test_file2bytea_copy_from()		# not fully implemented
	#test_file2bytea_overlay()
	#test_file2bytea()
	#test_exceptions()
	#test_get_connection()
	#test_ro_queries()
	#test_list_args()
	#test_sanitize_pg_regex()
	#test_is_pg_interval()
	#test_sanity_check_time_skew()
	test_sanity_check_database_settings()
	#test_get_foreign_key_details()
	#test_get_index_name()
	#test_set_user_language()
	#test_get_schema_revision_history()
	#test_run_query()
	#test_schema_exists()
	#test_get_foreign_key_names()
	#test_row_locks()
	#test_faulty_SQL()
	#test_log_settings()
	#test_get_db_fingerprint()

# ======================================================================
