-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v2
-- Target database version: v3
--
-- What it does:
-- - change clin.test_org
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: clin-test_org.sql,v 1.2 2006-10-28 12:22:48 ncq Exp $
-- $Revision: 1.2 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
alter table clin.test_org
	drop constraint if exists "$1";
alter table clin.test_org
	drop constraint if exists "test_org_fk_adm_contact_fkey";

alter table clin.test_org
	add foreign key(fk_adm_contact)
		references dem.identity(pk)
		on update cascade
		on delete restrict;

alter table clin.test_org
	drop constraint if exists "$2";
alter table clin.test_org
	drop constraint if exists "test_org_fk_med_contact_fkey";

alter table clin.test_org
	add foreign key(fk_med_contact)
		references dem.identity(pk)
		on update cascade
		on delete restrict;

-- --------------------------------------------------------------
select public.log_script_insertion('$RCSfile: clin-test_org.sql,v $', '$Revision: 1.2 $');
