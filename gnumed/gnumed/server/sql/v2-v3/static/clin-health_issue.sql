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
-- $Id: clin-health_issue.sql,v 1.2 2006-10-28 12:22:48 ncq Exp $
-- $Revision: 1.2 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
alter table clin.health_issue
	drop constraint "$1";
alter table clin.health_issue
	drop constraint "health_issue_id_patient_fkey";
\set ON_ERROR_STOP 1

alter table clin.health_issue
	rename column id_patient to fk_patient;

alter table clin.health_issue
	add foreign key(fk_patient)
		references dem.identity(pk)
		on update cascade
		on delete restrict;

-- --------------------------------------------------------------
select public.log_script_insertion('$RCSfile: clin-health_issue.sql,v $', '$Revision: 1.2 $');

-- ==============================================================
-- $Log: clin-health_issue.sql,v $
-- Revision 1.2  2006-10-28 12:22:48  ncq
-- - 8.1 prides itself in naming FKs differently -- better -- but makes
--   changing auto-named foreign keys a pain
--
-- Revision 1.1  2006/10/24 13:08:26  ncq
-- - mainly changes due to dropped clin.xlnk_identity
--
--
