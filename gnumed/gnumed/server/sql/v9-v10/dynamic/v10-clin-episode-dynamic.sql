-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
-- 
-- ==============================================================
--set default_transaction_read_only to off;
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
drop function if exists clin.trf_ensure_episode_issue_patient_consistency() cascade;

drop function if exists clin.trf_ensure_episode_encounter_patient_consistency() cascade;

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v10-clin-episode-dynamic.sql,v $', '$Revision: 1.3 $');
