-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view clin.v_potential_problem_list cascade;
\set ON_ERROR_STOP 1


create view clin.v_potential_problem_list as

	-- all the (closed) episodes
	select
		(select fk_patient from clin.encounter where pk = cep.fk_encounter)
			as pk_patient,
		cep.description
			as problem,
		cep.summary
			as summary,
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
			as diagnostic_certainty_classification,
		cep.fk_encounter
			as pk_encounter,
		cep.modified_when
			as modified_when
	from
		clin.episode cep
	where
		cep.is_open is false

union

	-- all the (clinically NOT relevant) health issues
	select
		(select fk_patient from clin.encounter where pk = chi.fk_encounter)
			as pk_patient,
		chi.description
			as problem,
		chi.summary
			as summary,
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
			as diagnostic_certainty_classification,
		chi.fk_encounter
			as pk_encounter,
		chi.modified_when
			as modified_when
	from
		clin.health_issue chi
	where
		chi.clinically_relevant is false
;


grant select on clin.v_potential_problem_list TO GROUP "gm-doctors";
-- --------------------------------------------------------------
select gm.log_script_insertion('v16-clin-v_potential_problem_list.sql', 'v16');

-- ==============================================================
