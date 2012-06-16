-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
-- $Id: v11-gm-schema_revision-static.sql,v 1.1 2009-05-22 10:59:01 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
--set default_transaction_read_only to off;
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
alter table public.gm_schema_revision set schema "gm";

alter table gm.gm_schema_revision rename to schema_revision;

-- --------------------------------------------------------------
create or replace function gm.log_script_insertion(text, text) returns text as '
declare
	_filename alias for $1;
	_version alias for $2;
	_hash text;
begin
	delete from gm.schema_revision where filename = _filename;
	insert into gm.schema_revision (filename, version) values (
		_filename,
		_version
	);
	select into _hash md5(gm.concat_table_structure());
	return _hash;
end;' language 'plpgsql';

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v11-gm-schema_revision-static.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v11-gm-schema_revision-static.sql,v $
-- Revision 1.1  2009-05-22 10:59:01  ncq
-- - new
--
--