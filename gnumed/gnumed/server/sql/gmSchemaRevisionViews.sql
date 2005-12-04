-- =============================================
-- project: GNUmed
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmSchemaRevisionViews.sql,v $
-- $Id: gmSchemaRevisionViews.sql,v 1.3 2005-12-04 09:45:36 ncq Exp $
-- license: GPL
-- author: Karsten.Hilbert@gmx.net

-- =============================================
-- import this file into any database you create and
-- add the revision of your schema files into the revision table,
-- this will allow for a simplistic manual database schema revision control,
-- that may come in handy when debugging live production databases,

-- for your convenience, just copy/paste the following lines:
-- (don't worry about the filename/revision that's in there, it will
--  be replaced automagically with the proper data by "cvs commit")

-- do simple schema revision tracking
-- select log_script_insertion('$RCSfile: gmSchemaRevisionViews.sql,v $', '$Revision: 1.3 $');

-- =============================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- ---------------------------------------------
create or replace function gm_concat_table_structure()
	returns text
	language 'plpgsql'
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
					tabs.table_schema = ''public'' and
					tabs.table_type = ''BASE TABLE'' and
					tabs.table_name not like ''log\_%''
				)
			order by
				cols.table_schema, cols.table_name, cols.column_name, cols.data_type
	loop
		_total := _total
			|| _row.table_schema || ''.''
			|| _row.table_name || ''.''
			|| _row.column_name || ''::''
			|| _row.data_type || ''\n'';
	end loop;
	return _total;
end;
';

-- ---------------------------------------------
create or replace function log_script_insertion(text, text) returns text as '
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
	select into _hash md5(gm_concat_table_structure());
	delete from gm_database_revision;
	insert into gm_database_revision (identity_hash) values (_hash);
	return _hash;
end;' language 'plpgsql';

-- =============================================
GRANT SELECT on
	gm_schema_revision
	, gm_database_revision
	, gm_client_db_match
TO group "gm-public";

-- =============================================
-- $Log: gmSchemaRevisionViews.sql,v $
-- Revision 1.3  2005-12-04 09:45:36  ncq
-- - just a silly one-line comment
--
-- Revision 1.2  2005/10/24 19:28:37  ncq
-- - move drop function ... to update*.sql
--
-- Revision 1.1  2005/09/19 16:15:28  ncq
-- - factor out re-doable stuff
--
--
