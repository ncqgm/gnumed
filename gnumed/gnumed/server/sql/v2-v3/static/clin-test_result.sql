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
-- $Id: clin-test_result.sql,v 1.2 2006-10-28 23:36:16 ncq Exp $
-- $Revision: 1.2 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
alter table clin.test_result
	drop constraint "$2";
alter table clin.test_result
	drop constraint "test_result_fk_intended_reviewer_fkey";
\set ON_ERROR_STOP 1

alter table clin.test_result
	add foreign key(fk_intended_reviewer)
		references dem.identity(pk)
		on update cascade
		on delete restrict;

-- --------------------------------------------------------------
select public.log_script_insertion('$RCSfile: clin-test_result.sql,v $', '$Revision: 1.2 $');

-- ==============================================================
-- $Log: clin-test_result.sql,v $
-- Revision 1.2  2006-10-28 23:36:16  ncq
-- - $2 is named explicitely in 8.1
--
-- Revision 1.1  2006/10/24 13:08:26  ncq
-- - mainly changes due to dropped clin.xlnk_identity
--
--
