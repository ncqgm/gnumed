-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v2
-- Target database version: v3
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: dem-enum_ext_id_types.sql,v 1.1 2007-02-05 13:10:40 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
-- remember to handle dependant objects possibly dropped by CASCADE
--\unset ON_ERROR_STOP
--drop function forgot_to_edit_drops;
--\set ON_ERROR_STOP 1

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
-- don't forget appropriate grants
--grant select on forgot_to_edit_grants to group "gm-doctors";

-- --------------------------------------------------------------
select public.log_script_insertion('$RCSfile: dem-enum_ext_id_types.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: dem-enum_ext_id_types.sql,v $
-- Revision 1.1  2007-02-05 13:10:40  ncq
-- - add_external_id_type()
--
-- Revision 1.6  2007/01/27 21:16:08  ncq
-- - the begin/commit does not fit into our change script model
--
-- Revision 1.5  2006/10/24 13:09:45  ncq
-- - What it does duplicates the change log so axe it
--
-- Revision 1.4  2006/09/28 14:39:51  ncq
-- - add comment template
--
-- Revision 1.3  2006/09/18 17:32:53  ncq
-- - make more fool-proof
--
-- Revision 1.2  2006/09/16 21:47:37  ncq
-- - improvements
--
-- Revision 1.1  2006/09/16 14:02:36  ncq
-- - use this as a template for change scripts
--
--
