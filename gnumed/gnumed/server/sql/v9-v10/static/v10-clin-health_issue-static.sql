-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v10-clin-health_issue-static.sql,v 1.1 2008-09-02 15:42:37 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
-- drop function clin.trf_ensure_issue_encounter_patient_consistency() cascade;
alter table clin.health_issue drop column fk_patient cascade;


alter table audit.log_health_issue drop column fk_patient;
-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v10-clin-health_issue-static.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v10-clin-health_issue-static.sql,v $
-- Revision 1.1  2008-09-02 15:42:37  ncq
-- - new
--
--
