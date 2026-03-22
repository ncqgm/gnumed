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
alter table clin.hx_family_item
	drop constraint if exists "$2";
alter table clin.hx_family_item
	drop constraint if exists "hx_family_item_fk_relative_fkey";

alter table clin.hx_family_item
	add foreign key(fk_relative)
		references dem.identity(pk)
		on update cascade
		on delete set null;

-- --------------------------------------------------------------
select public.log_script_insertion('$RCSfile: clin-hx_family_item.sql,v $', '$Revision: 1.2 $');
