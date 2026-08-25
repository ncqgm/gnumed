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
drop view if exists blobs.v_obj4doc_no_data cascade;

create view blobs.v_obj4doc_no_data as
select
	c_enc.fk_patient
		as pk_patient,
	b_do.pk
		as pk_obj,
	b_do.seq_idx
		as seq_idx,
	octet_length(coalesce(b_do.data, ''))
		as size,
	b_dm.clin_when
		as date_generated,
	b_dt.name
		as type,
	_(b_dt.name)
		as l10n_type,
	b_dm.ext_ref
		as ext_ref,
	c_epi.description
		as episode,
	b_dm.comment
		as doc_comment,
	b_do.comment
		as obj_comment,
	b_do.filename
		as filename,
	b_do.fk_intended_reviewer
		as pk_intended_reviewer,
	exists(select 1 from blobs.reviewed_doc_objs where fk_reviewed_row = b_do.pk)
		as reviewed,
	exists (
		select 1 from blobs.reviewed_doc_objs
		where
			fk_reviewed_row = b_do.pk and
			fk_reviewer = (select pk from dem.staff where db_user = current_user)
		) as reviewed_by_you,
	exists (
		select 1 from blobs.reviewed_doc_objs
		where
			fk_reviewed_row = b_do.pk and
			fk_reviewer = b_do.fk_intended_reviewer
		) as reviewed_by_intended_reviewer,
	b_dm.pk
		as pk_doc,
	b_dm.fk_type
		as pk_type,
	b_dm.fk_encounter
		as pk_encounter,
	b_dm.fk_episode
		as pk_episode,
	c_epi.fk_health_issue
		as pk_health_issue,
	d_ou.fk_org
		as pk_org,
	b_dm.fk_org_unit
		as pk_org_unit,
	b_dm.fk_hospital_stay
		as pk_hospital_stay,
	b_do.xmin
		as xmin_doc_obj
from
	blobs.doc_med b_dm
		inner join blobs.doc_obj b_do on (b_do.fk_doc = b_dm.pk)
		-- from blobs.v_doc_med:
		inner join blobs.doc_type b_dt on (b_dm.fk_type = b_dt.pk)
		inner join clin.encounter c_enc on (b_dm.fk_encounter = c_enc.pk)
		inner join clin.episode c_epi on (b_dm.fk_episode = c_epi.pk)
		left join dem.org_unit d_ou on (b_dm.fk_org_unit = d_ou.pk)
where
	b_dm.pk = b_do.fk_doc
;

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-blobs-v_obj4doc_no_data.sql', 'v23');
