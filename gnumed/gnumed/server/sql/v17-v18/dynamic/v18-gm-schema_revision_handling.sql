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
create or replace function gm.concat_table_structure_v18_and_up()
	returns text
	language 'plpgsql'
	security definer
	as '
declare
	_table_desc record;
	_pk_desc record;
	_column_desc record;
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

	end loop;

	return _total;
end;
';


comment on function gm.concat_table_structure_v18_and_up() is
	'new concat_table_structure() starting with gnumed_v18,
	 works on dem, clin, blobs, cfg, ref, i18n, bill,
	 includes primary keys,
	 sorts properly by bytea';

-- --------------------------------------------------------------
create or replace function gm.concat_table_structure(integer)
	returns text
	language 'plpgsql'
	security definer
	as '
declare
	_db_ver alias for $1;
	_struct text;
begin
	if _db_ver < 6 then
		select into _struct gm.concat_table_structure_v1();
		return _struct;
	end if;
	if _db_ver < 8 then
		select into _struct gm.concat_table_structure_v2();
		return _struct;
	end if;
	if _db_ver < 16 then
		select into _struct gm.concat_table_structure_v3();
		return _struct;
	end if;
	if _db_ver < 17 then
		select into _struct gm.concat_table_structure_v16_and_up();
		return _struct;
	end if;
	if _db_ver < 18 then
		select into _struct gm.concat_table_structure_v17_and_up();
		return _struct;
	end if;

	select into _struct gm.concat_table_structure_v18_and_up();
	return _struct;
end;
';

-- --------------------------------------------------------------
create or replace function gm.concat_table_structure()
	returns text
	language 'plpgsql'
	security definer
	as '
declare
	_struct text;
begin
	select into _struct gm.concat_table_structure_v18_and_up();
	return _struct;
end;
';

-- ==============================================================
select gm.log_script_insertion('v18-gm-schema_revision_handling.sql', '18.0');
