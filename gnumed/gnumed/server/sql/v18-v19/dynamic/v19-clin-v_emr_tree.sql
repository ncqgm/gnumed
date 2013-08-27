-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
--
-- ==============================================================
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
-- needed for Jerzy's enhancements:
drop view if exists clin.v_emr_tree cascade;

CREATE VIEW clin.v_emr_tree AS 

( 
	SELECT DISTINCT
		c_v_enc.pk_patient,
		c_v_epi.pk_health_issue
			AS pk_issue,
		c_v_epi.health_issue
			AS issue_description,
		c_v_epi.pk_episode,
		c_v_epi.description
			AS episode_description,
		c_v_enc.pk_encounter,
		c_v_enc.assessment_of_encounter
			AS encounter_description,
		c_v_enc.started
			AS encounter_started,
		c_v_enc.l10n_type
			AS encounter_l10n_type
	FROM clin.v_pat_encounters c_v_enc
		JOIN clin.clin_narrative c_narr ON c_v_enc.pk_encounter = c_narr.fk_encounter
			JOIN clin.v_pat_episodes c_v_epi ON c_narr.fk_episode = c_v_epi.pk_episode

) UNION (

	SELECT
		c_v_epi.pk_patient,
		c_v_epi.pk_health_issue
			AS pk_issue,
		c_v_epi.health_issue
			AS issue_description,
		c_v_epi.pk_episode,
		c_v_epi.description
			AS episode_description,
		NULL::integer
			AS pk_encounter,
		NULL::text
			AS encounter_description,
		NULL::timestamp with time zone
			AS encounter_started,
		NULL::text AS encounter_l10n_type
	FROM clin.v_pat_episodes c_v_epi

);

COMMENT ON VIEW clin.v_emr_tree IS
'pk_* and descriptions of issues, episodes, encounters for creating an EMR tree. Encounters restricted to those having an entry in clin.narrative';

GRANT SELECT ON TABLE clin.v_emr_tree TO "gm-doctors";
-- --------------------------------------------------------------
select gm.log_script_insertion('v19-clin-v_emr_tree.sql', '19.0');
