-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
-- $Id: v12-gm-log_script_insertion.sql,v 1.1 2009-08-28 12:44:02 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
--set default_transaction_read_only to off;
\set ON_ERROR_STOP 1

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
	perform gm.log_other_access (
		''database change script inserted: $RCSfile: v12-gm-log_script_insertion.sql,v $ ($Revision: 1.1 $)''
	);
	select into _hash md5(gm.concat_table_structure());
	return _hash;
end;' language 'plpgsql';

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v12-gm-log_script_insertion.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v12-gm-log_script_insertion.sql,v $
-- Revision 1.1  2009-08-28 12:44:02  ncq
-- - log script insertion in access log
--
--
