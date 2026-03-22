-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v2
-- Target database version: v3
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
create or replace function dem.add_external_id_type(text, text, text)
	returns boolean
	language 'plpgsql'
	as '
declare
	_name alias for $1;
	_issuer alias for $2;
	_context alias for $3;
begin
	perform 1 from dem.enum_ext_id_types where name = _name and context = _context;
	if FOUND then
		return true;
	end if;
	insert into dem.enum_ext_id_types(name, issuer, context) values (_name, _issuer, _context);
	return true;
end;';


comment on function dem.add_external_id_type(text, text, text) is
	'Add an external ID type if it does not exist yet.
	 This implementation is prone to concurrency issues.';

-- --------------------------------------------------------------
select public.log_script_insertion('$RCSfile: dem-enum_ext_id_types.sql,v $', '$Revision: 1.1 $');
