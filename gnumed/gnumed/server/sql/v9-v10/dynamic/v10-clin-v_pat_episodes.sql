-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v10-clin-v_pat_episodes.sql,v 1.1 2008-09-02 15:41:20 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view clin.v_pat_episodes cascade;
\set ON_ERROR_STOP 1


create view clin.v_pat_episodes as
select
	(select fk_patient from clin.encounter where pk = cep.fk_encounter) as pk_patient,
	cep.description as description,
	cep.is_open as episode_open,
	null as health_issue,
	null as issue_active,
	null as issue_clinically_relevant,
	cep.pk as pk_episode,
	null as pk_health_issue,
	cep.modified_when as episode_modified_when,
	cep.modified_by as episode_modified_by,
	cep.xmin as xmin_episode
from
	clin.episode cep
where
	cep.fk_health_issue is null

		UNION ALL

select
	(select fk_patient from clin.encounter where pk = cep.fk_encounter) as pk_patient,
	cep.description as description,
	cep.is_open as episode_open,
	chi.description as health_issue,
	chi.is_active as issue_active,
	chi.clinically_relevant as issue_clinically_relevant,
	cep.pk as pk_episode,
	cep.fk_health_issue as pk_health_issue,
	cep.modified_when as episode_modified_when,
	cep.modified_by as episode_modified_by,
	cep.xmin as xmin_episode
from
	clin.episode cep, clin.health_issue chi
where
	-- this should exclude all (fk_health_issue is Null) ?
	cep.fk_health_issue = chi.pk
;


grant select on clin.v_pat_episodes TO GROUP "gm-doctors";
-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v10-clin-v_pat_episodes.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v10-clin-v_pat_episodes.sql,v $
-- Revision 1.1  2008-09-02 15:41:20  ncq
-- - new
--
--
