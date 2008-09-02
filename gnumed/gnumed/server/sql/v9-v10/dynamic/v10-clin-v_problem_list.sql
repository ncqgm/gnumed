-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v10-clin-v_problem_list.sql,v 1.1 2008-09-02 18:56:39 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view clin.v_problem_list cascade;
\set ON_ERROR_STOP 1


create view clin.v_problem_list as

select	-- all the (open) episodes
	(select fk_patient from clin.encounter where pk = cep.fk_encounter) as pk_patient,
	cep.description as problem,
	'episode' as type,
	_('episode') as l10n_type,
	True as problem_active,
	True as clinically_relevant,
	cep.pk as pk_episode,
	cep.fk_health_issue as pk_health_issue
from
	clin.episode cep
where
	cep.is_open is true

union

select	-- all the (clinically relevant) health issues
	(select fk_patient from clin.encounter where pk = chi.fk_encounter) as pk_patient,
	chi.description as problem,
	'issue' as type,
	_('health issue') as l10n_type,
	chi.is_active as problem_active,
	True as clinically_relevant,
	null as pk_episode,
	chi.pk as pk_health_issue
from
	clin.health_issue chi
where
	chi.clinically_relevant is true
;


grant select on clin.v_problem_list TO GROUP "gm-doctors";
-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v10-clin-v_problem_list.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v10-clin-v_problem_list.sql,v $
-- Revision 1.1  2008-09-02 18:56:39  ncq
-- - new
--
--