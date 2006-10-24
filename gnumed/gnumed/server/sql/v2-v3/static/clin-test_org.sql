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
-- $Id: clin-test_org.sql,v 1.1 2006-10-24 13:08:26 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
begin;

alter table clin.test_org
	drop constraint "$1";

alter table clin.test_org
	add foreign key(fk_adm_contact)
		references dem.identity(pk)
		on update cascade
		on delete restrict;

alter table clin.test_org
	drop constraint "$2";

alter table clin.test_org
	add foreign key(fk_med_contact)
		references dem.identity(pk)
		on update cascade
		on delete restrict;

-- --------------------------------------------------------------
select public.log_script_insertion('$RCSfile: clin-test_org.sql,v $', '$Revision: 1.1 $');

-- --------------------------------------------------------------
commit;

-- ==============================================================
-- $Log: clin-test_org.sql,v $
-- Revision 1.1  2006-10-24 13:08:26  ncq
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
