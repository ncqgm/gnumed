-- all modifications needed by EMRMultiView plugin

-- View: clin.v_pat_encounters

-- DROP VIEW clin.v_pat_encounters;

CREATE OR REPLACE VIEW clin.v_pat_encounters AS 
 SELECT c_enc.pk AS pk_encounter, c_enc.fk_patient AS pk_patient, c_enc.started, et.description AS type, _(et.description) AS l10n_type, c_enc.reason_for_encounter, c_enc.assessment_of_encounter, c_enc.last_affirmed, c_enc.source_time_zone, ( SELECT timezone(( SELECT c_enc1.source_time_zone
                   FROM clin.encounter c_enc1
                  WHERE c_enc1.pk = c_enc.pk), c_enc.started) AS timezone) AS started_original_tz, ( SELECT timezone(( SELECT c_enc1.source_time_zone
                   FROM clin.encounter c_enc1
                  WHERE c_enc1.pk = c_enc.pk), c_enc.last_affirmed) AS timezone) AS last_affirmed_original_tz, c_enc.fk_location AS pk_location, c_enc.fk_type AS pk_type, COALESCE(( SELECT array_agg(c_lc2r.fk_generic_code) AS array_agg
           FROM clin.lnk_code2rfe c_lc2r
          WHERE c_lc2r.fk_item = c_enc.pk), ARRAY[]::integer[]) AS pk_generic_codes_rfe, COALESCE(( SELECT array_agg(c_lc2a.fk_generic_code) AS array_agg
           FROM clin.lnk_code2aoe c_lc2a
          WHERE c_lc2a.fk_item = c_enc.pk), ARRAY[]::integer[]) AS pk_generic_codes_aoe, c_enc.xmin AS xmin_encounter,
      c_enc.row_version, c_enc.pk_audit, c_enc.modified_when, c_enc.modified_by, 
      COALESCE(( SELECT staff.short_alias FROM dem.staff WHERE staff.db_user = c_enc.modified_by),
        ('<'::text || c_enc.modified_by::text) || '>'::text) 
      AS provider
   FROM clin.encounter c_enc, clin.encounter_type et
  WHERE c_enc.fk_type = et.pk;


-- View: clin.v_emr_tree

-- DROP VIEW clin.v_emr_tree;

CREATE OR REPLACE VIEW clin.v_emr_tree AS 
( SELECT DISTINCT enc.pk_patient, epi.pk_health_issue AS pk_issue, epi.health_issue AS issue_description, epi.pk_episode, epi.description AS episode_description, enc.pk_encounter, enc.assessment_of_encounter AS encounter_description, enc.started AS encounter_started, enc.l10n_type AS encounter_l10n_type
   FROM clin.v_pat_encounters enc
   JOIN clin.clin_narrative cn ON enc.pk_encounter = cn.fk_encounter
   JOIN clin.v_pat_episodes epi ON cn.fk_episode = epi.pk_episode
  ORDER BY enc.pk_patient, epi.pk_health_issue, epi.health_issue, epi.pk_episode, epi.description, enc.pk_encounter, enc.assessment_of_encounter, enc.started, enc.l10n_type)
UNION 
 SELECT v_pat_episodes.pk_patient, v_pat_episodes.pk_health_issue AS pk_issue, v_pat_episodes.health_issue AS issue_description, v_pat_episodes.pk_episode, v_pat_episodes.description AS episode_description, NULL::unknown AS pk_encounter, NULL::unknown AS encounter_description, NULL::unknown AS encounter_started, NULL::unknown AS encounter_l10n_type
   FROM clin.v_pat_episodes
  ORDER BY 1, 2, 4, 6;

ALTER TABLE clin.v_emr_tree OWNER TO "gm-dbo";
GRANT SELECT, UPDATE, INSERT, DELETE, REFERENCES, TRIGGER ON TABLE clin.v_emr_tree TO "gm-dbo";
GRANT SELECT ON TABLE clin.v_emr_tree TO "gm-doctors";
COMMENT ON VIEW clin.v_emr_tree IS 'pk_* and descriptions of issues, episodes, encounters for creating an EMR tree. Encounters restricted to having an entry in clin.narrative';


GRANT SELECT ON TABLE audit.log_health_issue TO "gm-doctors";
GRANT SELECT ON TABLE audit.log_episode TO "gm-doctors";
GRANT SELECT ON TABLE audit.log_encounter TO "gm-doctors";
GRANT SELECT ON TABLE audit.log_clin_narrative TO "gm-doctors";
GRANT SELECT ON TABLE audit.log_test_result TO "gm-doctors";
GRANT SELECT ON TABLE audit.log_allergy TO "gm-doctors";
GRANT SELECT ON TABLE audit.log_hospital_stay TO "gm-doctors";
GRANT SELECT ON TABLE audit.log_family_history TO "gm-doctors";
GRANT SELECT ON TABLE audit.log_lab_request TO "gm-doctors";
GRANT SELECT ON TABLE audit.log_vaccination TO "gm-doctors";
GRANT SELECT ON TABLE audit.log_substance_intake TO "gm-doctors";

