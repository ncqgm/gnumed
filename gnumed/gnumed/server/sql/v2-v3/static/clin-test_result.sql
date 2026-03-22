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
-- $Id: clin-test_result.sql,v 1.2 2006-10-28 23:36:16 ncq Exp $
-- $Revision: 1.2 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
alter table clin.test_result
	drop constraint if exists "$2";
alter table clin.test_result
	drop constraint if exists "test_result_fk_intended_reviewer_fkey";

alter table clin.test_result
	add foreign key(fk_intended_reviewer)
		references dem.identity(pk)
		on update cascade
		on delete restrict;

-- --------------------------------------------------------------
select public.log_script_insertion('$RCSfile: clin-test_result.sql,v $', '$Revision: 1.2 $');
