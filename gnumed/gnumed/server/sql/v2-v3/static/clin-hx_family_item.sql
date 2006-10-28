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
-- $Id: clin-hx_family_item.sql,v 1.2 2006-10-28 23:39:18 ncq Exp $
-- $Revision: 1.2 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
alter table clin.hx_family_item
	drop constraint "$2";
alter table clin.hx_family_item
	drop constraint "hx_family_item_fk_relative_fkey";
\set ON_ERROR_STOP 1

alter table clin.hx_family_item
	add foreign key(fk_relative)
		references dem.identity(pk)
		on update cascade
		on delete set null;

-- --------------------------------------------------------------
select public.log_script_insertion('$RCSfile: clin-hx_family_item.sql,v $', '$Revision: 1.2 $');

-- ==============================================================
-- $Log: clin-hx_family_item.sql,v $
-- Revision 1.2  2006-10-28 23:39:18  ncq
-- - $2 -> explicit name
--
-- Revision 1.1  2006/10/24 13:08:26  ncq
-- - mainly changes due to dropped clin.xlnk_identity
--
--
