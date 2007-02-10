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
-- $Id: clin-f_protect_clin_root_item.sql,v 1.1 2007-02-10 23:42:47 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop function clin.f_protect_clin_root_item() cascade;
\set ON_ERROR_STOP 1


create function clin.f_protect_clin_root_item() returns boolean as '
begin
	raise exception ''INSERT/DELETE on <clin_root_item> not allowed.'';
	return False;
end;
' language 'plpgsql';


create rule clin_ritem_no_ins as
	on insert to clin.clin_root_item
	do instead select clin.f_protect_clin_root_item();


create rule clin_ritem_no_del as
	on delete to clin.clin_root_item
	do instead select clin.f_protect_clin_root_item();


comment on function clin.f_protect_clin_root_item() is
	'protect from direct inserts/deletes which the 
	 inheritance system cannot handle properly';

-- --------------------------------------------------------------
select public.log_script_insertion('$RCSfile: clin-f_protect_clin_root_item.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: clin-f_protect_clin_root_item.sql,v $
-- Revision 1.1  2007-02-10 23:42:47  ncq
-- - fix return type on rule function
-- - add date_trunc('day', dob) index
--
--