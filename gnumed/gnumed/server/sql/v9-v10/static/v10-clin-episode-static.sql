-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v10-clin-episode-static.sql,v 1.1 2008-12-01 21:47:10 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
drop function clin.trf_ensure_episode_issue_patient_consistency() cascade;


alter table clin.episode drop column fk_patient cascade;


alter table audit.log_episode drop column fk_patient;
-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v10-clin-episode-static.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v10-clin-episode-static.sql,v $
-- Revision 1.1  2008-12-01 21:47:10  ncq
-- - new
--
--