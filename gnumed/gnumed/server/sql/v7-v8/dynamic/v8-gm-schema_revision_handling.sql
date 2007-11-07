-- =============================================
-- project: GNUmed
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/v7-v8/dynamic/v8-gm-schema_revision_handling.sql,v $
-- $Id: v8-gm-schema_revision_handling.sql,v 1.1 2007-11-07 22:50:55 ncq Exp $
-- license: GPL
-- author: Karsten.Hilbert@gmx.net

-- =============================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- ---------------------------------------------
create or replace function gm.concat_table_structure_v3()
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
		select * from information_schema.columns cols
			where cols.table_name in (
				select tabs.table_name from information_schema.tables tabs where
					-- those which hold clinical data
					tabs.table_schema in (''dem'', ''clin'', ''blobs'', ''cfg'', ''ref'', ''i18n'') and
					tabs.table_type = ''BASE TABLE''
				)
			order by
				decode(md5(cols.table_schema || cols.table_name || cols.column_name || cols.data_type), ''hex'')
	loop
		_total := _total
			|| _row.table_schema || ''.''
			|| _row.table_name || ''.''
			|| _row.column_name || ''::''
			|| _row.udt_name || ''\n'';
	end loop;
	return _total;
end;
';

comment on function gm.concat_table_structure_v3() is
	'new concat_table_structure() starting with gnumed_v8,
	 works on dem, clin, blobs, cfg, ref, i18n,
	 sorts properly by bytea';

-- ---------------------------------------------
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
	select into _struct gm.concat_table_structure_v3();
	return _struct;
end;
';

-- ---------------------------------------------
create or replace function gm.concat_table_structure()
	returns text
	language 'plpgsql'
	security definer
	as '
declare
	_struct text;
begin
	select into _struct gm.concat_table_structure_v3();
	return _struct;
end;
';

-- =============================================
select gm.log_script_insertion('$RCSfile: v8-gm-schema_revision_handling.sql,v $', '$Revision: 1.1 $');

-- =============================================
-- $Log: v8-gm-schema_revision_handling.sql,v $
-- Revision 1.1  2007-11-07 22:50:55  ncq
-- - sort concat bei bytea'ed md5
--
--