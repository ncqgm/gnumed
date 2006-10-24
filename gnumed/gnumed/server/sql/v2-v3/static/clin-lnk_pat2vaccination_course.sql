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
-- $Id: clin-lnk_pat2vaccination_course.sql,v 1.1 2006-10-24 13:08:26 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
begin;

alter table clin.lnk_pat2vaccination_course
	drop constraint "$1";

alter table clin.lnk_pat2vaccination_course
	add foreign key(fk_patient)
		references dem.identity(pk)
		on update cascade
		on delete cascade;

-- --------------------------------------------------------------
select public.log_script_insertion('$RCSfile: clin-lnk_pat2vaccination_course.sql,v $', '$Revision: 1.1 $');

-- --------------------------------------------------------------
commit;

-- ==============================================================
-- $Log: clin-lnk_pat2vaccination_course.sql,v $
-- Revision 1.1  2006-10-24 13:08:26  ncq
-- - mainly changes due to dropped clin.xlnk_identity
--
--
