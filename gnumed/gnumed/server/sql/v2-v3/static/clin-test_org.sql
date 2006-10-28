-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v2
-- Target database version: v3
--
-- What it does:
-- - change clin.test_org
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: clin-test_org.sql,v 1.2 2006-10-28 12:22:48 ncq Exp $
-- $Revision: 1.2 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
alter table clin.test_org
	drop constraint "$1";
alter table clin.test_org
	drop constraint "test_org_fk_adm_contact_fkey";
\set ON_ERROR_STOP 1

alter table clin.test_org
	add foreign key(fk_adm_contact)
		references dem.identity(pk)
		on update cascade
		on delete restrict;

\unset ON_ERROR_STOP
alter table clin.test_org
	drop constraint "$2";
alter table clin.test_org
	drop constraint "test_org_fk_med_contact_fkey";
\set ON_ERROR_STOP 1

alter table clin.test_org
	add foreign key(fk_med_contact)
		references dem.identity(pk)
		on update cascade
		on delete restrict;

-- --------------------------------------------------------------
select public.log_script_insertion('$RCSfile: clin-test_org.sql,v $', '$Revision: 1.2 $');

-- ==============================================================
-- $Log: clin-test_org.sql,v $
-- Revision 1.2  2006-10-28 12:22:48  ncq
-- - 8.1 prides itself in naming FKs differently -- better -- but makes
--   changing auto-named foreign keys a pain
--
-- Revision 1.1  2006/10/24 13:08:26  ncq
-- - mainly changes due to dropped clin.xlnk_identity
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
