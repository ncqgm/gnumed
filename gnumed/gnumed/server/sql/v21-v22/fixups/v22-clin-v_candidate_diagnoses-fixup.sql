-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten.Hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
drop view if exists clin.v_candidate_diagnoses cascade ;


create view clin.v_candidate_diagnoses as

	-- health issues
	select
		(select c_enc.fk_patient from clin.encounter c_enc where c_enc.pk = c_hi.fk_encounter) as pk_patient,
		c_hi.description || coalesce(' (' || c_hi.laterality || ')' ,'') as diagnosis,
		c_hi.is_confidential AS explicitely_confidential,
		c_hi.diagnostic_certainty_classification,
		'clin.health_issue' AS source
	from clin.health_issue c_hi

union all

	-- open episodes
	select
		(select c_enc.fk_patient from clin.encounter c_enc where c_enc.pk = c_epi.fk_encounter) as pk_patient,
		c_epi.description as diagnosis,
		coalesce (
			(select c_hi.is_confidential from clin.health_issue c_hi where c_hi.pk = c_epi.fk_health_issue),
			FALSE
		) AS explicitely_confidential,
		c_epi.diagnostic_certainty_classification,
		'clin.episode' AS source
	from clin.episode c_epi
	where c_epi.is_open IS TRUE

union all

	-- AOE from encounters of open episodes
	select
		c_enc.fk_patient as pk_patient,
		c_enc.assessment_of_encounter as diagnosis,
		-- coalesce into issue
		FALSE::bool AS explicitely_confidential,
		NULL::text AS diagnostic_certainty_classification,
		'clin.encounter' AS source
	from clin.encounter c_enc
	where
		c_enc.assessment_of_encounter IS NOT NULL
			and
		c_enc.pk IN (
			select c_cri.fk_encounter from clin.clin_root_item c_cri where c_cri.fk_episode in (
				select c_epi.pk from clin.episode c_epi where c_epi.is_open IS TRUE
			)
		)

union all

	-- soAp from narrative in open episodes
	select
		(select c_enc.fk_patient from clin.encounter c_enc where c_enc.pk = c_cn.fk_encounter) as pk_patient,
		c_cn.narrative as diagnosis,
		-- coalesce into issue
		FALSE::bool AS explicitely_confidential,
		NULL::text as diagnostic_certainty_classification,
		'clin.clin_narrative' as source
	from clin.clin_narrative c_cn
	where
		c_cn.soap_cat = 'a'
			and
		c_cn.fk_episode in (
			select c_epi.pk from clin.episode c_epi where c_epi.is_open IS TRUE
		)

;


comment on view clin.v_candidate_diagnoses is
	'Candidates for diagnoses.';


grant select on clin.v_candidate_diagnoses to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-clin-v_candidate_diagnoses-fixup.sql', '22.9');
