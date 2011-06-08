-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v12-clin-v_potential_problem_list.sql,v 1.2 2010-01-21 08:48:50 ncq Exp $
-- $Revision: 1.2 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view clin.v_potential_problem_list cascade;
\set ON_ERROR_STOP 1


create view clin.v_potential_problem_list as

select	-- all the (closed) episodes
	(select fk_patient from clin.encounter where pk = cep.fk_encounter)
		as pk_patient,
	cep.description
		as problem,
	'episode'
		as type,
	_('episode')
		as l10n_type,
	False
		as problem_active,
	False
		as clinically_relevant,
	cep.pk
		as pk_episode,
	cep.fk_health_issue
		as pk_health_issue,
	cep.diagnostic_certainty_classification
		as diagnostic_certainty_classification
from
	clin.episode cep
where
	cep.is_open is false

union

select	-- all the (clinically NOT relevant) health issues
	(select fk_patient from clin.encounter where pk = chi.fk_encounter)
		as pk_patient,
	chi.description
		as problem,
	'issue'
		as type,
	_('health issue')
		as l10n_type,
	chi.is_active
		as problem_active,
	False
		as clinically_relevant,
	null
		as pk_episode,
	chi.pk
		as pk_health_issue,
	chi.diagnostic_certainty_classification
		as diagnostic_certainty_classification
from
	clin.health_issue chi
where
	chi.clinically_relevant is false
;


grant select on clin.v_potential_problem_list TO GROUP "gm-doctors";
-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v12-clin-v_potential_problem_list.sql,v $', '$Revision: 1.2 $');

-- ==============================================================
-- $Log: v12-clin-v_potential_problem_list.sql,v $
-- Revision 1.2  2010-01-21 08:48:50  ncq
-- - include Dx certainty
--
-- Revision 1.1  2009/11/28 18:11:29  ncq
-- - new view
--
--