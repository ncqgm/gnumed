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
--set check_function_bodies to on;

-- --------------------------------------------------------------
create or replace function gm.concat_table_structure_v16_and_up()
	returns text
	language 'plpgsql'
	security definer
	as '
declare
	_row record;
	_total text;
begin
	_total := '''';
	-- schema.table.column.data_type
	for _row in
		select *
		from information_schema.columns cols
		where
			cols.table_name in (
				select tabs.table_name from information_schema.tables tabs where
					-- those which hold clinical data
					tabs.table_schema in (''dem'', ''clin'', ''blobs'', ''cfg'', ''ref'', ''i18n'')
						and
					tabs.table_type = ''BASE TABLE''
			) and
			cols.table_schema in (''dem'', ''clin'', ''blobs'', ''cfg'', ''ref'', ''i18n'')
		order by
			decode(md5(cols.table_schema || cols.table_name || cols.column_name || cols.data_type), ''hex'')
	loop
		_total := _total
			|| _row.table_schema || ''.''
			|| _row.table_name || ''.''
			|| _row.column_name || ''::''
			|| _row.udt_name || E''\n'';
	end loop;
	return _total;
end;
';

comment on function gm.concat_table_structure_v16_and_up() is
	'new concat_table_structure() starting with gnumed_v16,
	 works on dem, clin, blobs, cfg, ref, i18n,
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

	select into _struct gm.concat_table_structure_v16_and_up();
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
	select into _struct gm.concat_table_structure_v16_and_up();
	return _struct;
end;
';

-- ==============================================================
select gm.log_script_insertion('v16-gm-schema_revision_handling.sql', 'v16');
