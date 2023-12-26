-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

--set default_transaction_read_only to off;
set check_function_bodies to on;

-- --------------------------------------------------------------
-- a few missing grants on (mostly unused) tables prevented
-- accounts other than the owner (gm-dbo) from seeing them
-- inside information_schema.tables which then throws off
-- getting the database schema structure
--
-- now, this won't matter as long as gm.concat_table_structure()
-- is used since that is owned by gm-dob _and_ also "security definer"
--
-- however, when using an ad-hoc temporary version in pg_temp to
-- overcome other problems (such as missing CASTs) that version is
-- owned and run by other accounts, which in turn won't see some
-- rows in information_schema, making the function return a different
-- table structure than is expected (and in the database)
grant select, insert, update, delete on
	clin.incoming_data_unmatchable,
	clin.lnk_substance2episode,
	ref.atc_staging		-- no PK hence no PK sequence
to group "gm-doctors";

grant usage, select, update on
	clin.incoming_data_unmatchable_pk_seq,
	clin.lnk_substance2episode_pk_seq
to group "gm-doctors";

-- --------------------------------------------------------------
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
		_total := _total || ''TABLE:'' || _table_desc.table_schema || ''.'' || _table_desc.table_name || E''\n'';

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
			_total := _total || ''PK:'' || _pk_desc.primary_key_column	|| E''\n'';
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
				|| _column_desc.udt_name || E''\n'';

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
			_total := _total || _constraint_def.condef || E''\n'';
		end loop;

	end loop;		-- over tables

	return _total;
end;
';

ALTER function gm.concat_table_structure_v19_and_up()
	owner to "gm-dbo";

comment on function gm.concat_table_structure_v19_and_up() is
	'new concat_table_structure() starting with gnumed_v19,
	 works on dem, clin, blobs, cfg, ref, i18n, bill,
	 includes primary keys and constraints,
	 sorts properly by bytea';

-- ==============================================================
select gm.log_script_insertion('v22-gm-concat_table_structure_v19_and_up-fixup.sql', '22.28');
