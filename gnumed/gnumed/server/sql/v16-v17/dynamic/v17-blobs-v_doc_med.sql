-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
--
-- ==============================================================
\unset ON_ERROR_STOP
--drop view blobs.v_doc_med;
\set ON_ERROR_STOP 1


create or replace view blobs.v_doc_med as
select
	(select fk_patient from clin.encounter where pk = dm.fk_encounter) as pk_patient,
	dm.pk as pk_doc,
	dm.clin_when as clin_when,
	dt.name as type,
	_(dt.name) as l10n_type,
	dm.ext_ref as ext_ref,
	cle.description as episode,
	dm.comment as comment,
	cle.is_open as episode_open,
	dm.fk_type as pk_type,
	dm.fk_encounter as pk_encounter,
	dm.fk_episode as pk_episode,
	cle.fk_health_issue as pk_health_issue,
	dm.modified_when as modified_when,
	dm.modified_by as modified_by,
	dm.xmin as xmin_doc_med,
	chi.description as health_issue
from
	blobs.doc_med dm,
	blobs.doc_type dt,
	clin.episode cle
		left join clin.health_issue chi on (chi.pk = cle.fk_health_issue)
where
	dt.pk = dm.fk_type
		and
	cle.pk = dm.fk_episode
;

-- --------------------------------------------------------------
GRANT SELECT ON blobs.v_doc_med TO GROUP "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v17-blobs-v_doc_med.sql', '17.0');
