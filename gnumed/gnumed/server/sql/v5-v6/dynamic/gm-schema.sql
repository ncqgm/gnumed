-- =============================================
-- project: GNUmed
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/v5-v6/dynamic/gm-schema.sql,v $
-- $Id: gm-schema.sql,v 1.2 2007-05-07 16:45:54 ncq Exp $
-- license: GPL
-- author: Karsten.Hilbert@gmx.net

-- =============================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- ---------------------------------------------
\unset ON_ERROR_STOP
drop schema gm cascade;
\set ON_ERROR_STOP 1

create schema gm authorization "gm-dbo";

-- ---------------------------------------------
create or replace function gm.concat_table_structure_v1()
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
					tabs.table_schema in (''public'', ''dem'', ''clin'', ''blobs'') and
					tabs.table_type = ''BASE TABLE''
				)
			order by
				md5(cols.table_schema || cols.table_name || cols.column_name || cols.data_type)
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

comment on function gm.concat_table_structure_v1() is
	'copy of gm_concat_table_structure() until gnumed_v5, works on public, dem, clin, blobs';

-- ---------------------------------------------
create or replace function gm.concat_table_structure_v2()
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
				md5(cols.table_schema || cols.table_name || cols.column_name || cols.data_type)
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

comment on function gm.concat_table_structure_v2() is
	'new concat_table_structure() starting with gnumed_v6, works on dem, clin, blobs, cfg, ref, i18n';

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
	select into _struct gm.concat_table_structure_v2();
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
	select into _struct gm.concat_table_structure_v2();
	return _struct;
end;
';

-- ---------------------------------------------
create or replace function gm.log_script_insertion(text, text) returns text as '
declare
	_filename alias for $1;
	_version alias for $2;
	_hash text;
begin
	delete from gm_schema_revision where filename = _filename;
	insert into gm_schema_revision (filename, version) values (
		_filename,
		_version
	);
	select into _hash md5(gm.concat_table_structure());
	return _hash;
end;' language 'plpgsql';

-- ---------------------------------------------
-- cleanup
drop function public.gm_concat_table_structure() cascade;
drop function public.log_script_insertion(text, text) cascade;
drop table public.gm_database_revision cascade;

-- =============================================
select gm.log_script_insertion('$RCSfile: gm-schema.sql,v $', '$Revision: 1.2 $');

-- =============================================
-- $Log: gm-schema.sql,v $
-- Revision 1.2  2007-05-07 16:45:54  ncq
-- - fix missing schema qual
--
-- Revision 1.1  2007/05/07 16:25:45  ncq
-- - start putting a bunch of database maintenance related stuff into
--   its own schema so we come clean of using "public" which will
--   enable us to drop "public" from the identity hash function which
--   in turn will allow us to gracefully deal with pgaccess clobbering
--   "public"
--
--