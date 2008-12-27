-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v10-clin-episode-dynamic.sql,v 1.3 2008-12-27 15:51:03 ncq Exp $
-- $Revision: 1.3 $

-- --------------------------------------------------------------
--set default_transaction_read_only to off;
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop function clin.trf_ensure_episode_issue_patient_consistency() cascade;
\set ON_ERROR_STOP 1

\unset ON_ERROR_STOP
drop function clin.trf_ensure_episode_encounter_patient_consistency() cascade;
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v10-clin-episode-dynamic.sql,v $', '$Revision: 1.3 $');

-- ==============================================================
-- $Log: v10-clin-episode-dynamic.sql,v $
-- Revision 1.3  2008-12-27 15:51:03  ncq
-- - no more fk_patient so drop consistency check for that
--
-- Revision 1.2  2008/12/01 21:48:46  ncq
-- - no more fk_patient so no more consistency checking
--
-- Revision 1.1  2008/11/24 11:05:32  ncq
-- - fix patient consistency trigger
--
--