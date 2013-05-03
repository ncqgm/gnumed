
-- modify database to support modified encounter handling

SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;
BEGIN TRANSACTION;

-- ==================================================
-- views
-- ==================================================

-- View: clin.v_emr_tree

-- DROP VIEW clin.v_emr_tree;

CREATE OR REPLACE VIEW clin.v_emr_tree AS
SELECT DISTINCT enc.pk_patient, epi.pk_health_issue AS pk_issue, epi.health_issue AS issue_description, epi.pk_episode, epi.description AS episode_description, enc.pk_encounter, enc.assessment_of_encounter AS encounter_description, enc.started AS encounter_started, enc.l10n_type AS encounter_l10n_type
   FROM clin.v_pat_encounters enc
   JOIN clin.clin_narrative cn ON enc.pk_encounter = cn.fk_encounter
   JOIN clin.v_pat_episodes epi ON cn.fk_episode = epi.pk_episode
UNION 
SELECT v_pat_episodes.pk_patient, v_pat_episodes.pk_health_issue AS pk_issue, v_pat_episodes.health_issue AS issue_description, v_pat_episodes.pk_episode, v_pat_episodes.description AS episode_description, NULL::unknown AS pk_encounter, NULL::unknown AS encounter_description, NULL::unknown AS encounter_started, NULL::unknown AS encounter_l10n_type
   FROM clin.v_pat_episodes
   ORDER BY pk_patient, pk_issue, pk_episode, pk_encounter
;
ALTER TABLE clin.v_emr_tree OWNER TO "gm-dbo";
GRANT SELECT, UPDATE, INSERT, DELETE, REFERENCES, TRIGGER ON TABLE clin.v_emr_tree TO "gm-dbo";
GRANT SELECT ON TABLE clin.v_emr_tree TO "gm-doctors";
COMMENT ON VIEW clin.v_emr_tree IS 'pk_* and descriptions of issues, episodes, encounters for creating an EMR tree. Encounters restricted to having an entry in clin.narrative';

-- View: clin.v_pat_narrative_full

-- DROP VIEW clin.v_pat_narrative_full;

CREATE OR REPLACE VIEW clin.v_pat_narrative_full AS
SELECT vpi.pk_patient, cn.pk AS pk_narrative, cn.row_version, cn.modified_when, cn.modified_by, cn.pk_item, cn.clin_when, cn.soap_cat, cn.narrative, vpi.pk_health_issue, cn.fk_episode AS pk_episode, cn.fk_encounter AS pk_encounter, cn.pk_audit, cn.xmin AS xmin_clin_narrative
   FROM clin.clin_narrative cn, clin.v_pat_items vpi
  WHERE cn.pk_item = vpi.pk_item;

ALTER TABLE clin.v_pat_narrative_full OWNER TO "gm-dbo";
GRANT SELECT, UPDATE, INSERT, DELETE, REFERENCES, TRIGGER ON TABLE clin.v_pat_narrative_full TO "gm-dbo";
GRANT SELECT ON TABLE clin.v_pat_narrative_full TO "gm-doctors";
COMMENT ON VIEW clin.v_pat_narrative_full IS 'All fields from clin.narrative with corresponging pk_patient and pk_issue';

-- Check: ref.paperwork_templates_engine_check

ALTER TABLE ref.paperwork_templates DROP CONSTRAINT engine_range;

ALTER TABLE ref.paperwork_templates
  ADD CONSTRAINT engine_range CHECK (engine = ANY (ARRAY['T'::text, 'L'::text, 'H'::text, 'O'::text, 'I'::text, 'G'::text, 'P'::text, 'A'::text, 'X'::text, 'M'::text, 'S'::text]));
COMMENT ON COLUMN ref.paperwork_templates.engine IS 'the business layer forms engine used to process this form,
	currently:
	- T: plain text (generic postprocessing)
	- L: LaTeX
	- H: Health Layer 7
	- O: OpenOffice
	- I: image editor (visual progress notes)
	- G: gnuplot scripts (test results graphing)
	- P: PDF form (FDF based)
	- A: AbiWord
	- X: Xe(La)TeX
	- M: HTML
	- S: XSLT';

--Add new form types used as context scope for form template

INSERT INTO ref.form_types (name) VALUES ('print.encounter.in hospital - admittance');
INSERT INTO ref.form_types (name) VALUES ('print.encounter.in surgery');
INSERT INTO ref.form_types (name) VALUES ('print.encounter.in hospital - discharge');  
INSERT INTO ref.form_types (name) VALUES ('print.encounter.in clinic - visit.consultation letter');
INSERT INTO ref.form_types (name) VALUES ('print.encounter.in clinic - visit.internal report');
INSERT INTO ref.form_types (name) VALUES ('print.episode.all progress notes');

COMMIT;