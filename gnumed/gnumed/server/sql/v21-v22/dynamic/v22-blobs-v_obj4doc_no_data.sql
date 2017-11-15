-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
--
-- ==============================================================
drop view if exists blobs.v_obj4doc_no_data cascade;

create view blobs.v_obj4doc_no_data as
select
	b_vdm.pk_patient
		as pk_patient,
	b_do.pk
		as pk_obj,
	b_do.seq_idx
		as seq_idx,
	octet_length(coalesce(b_do.data, ''))
		as size,
	b_vdm.clin_when
		as date_generated,
	b_vdm.type
		as type,
	b_vdm.l10n_type
		as l10n_type,
	b_vdm.ext_ref
		as ext_ref,
	b_vdm.episode
		as episode,
	b_vdm.comment
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
	b_vdm.pk_doc
		as pk_doc,
	b_vdm.pk_type
		as pk_type,
	b_vdm.pk_encounter
		as pk_encounter,
	b_vdm.pk_episode
		as pk_episode,
	b_vdm.pk_health_issue
		as pk_health_issue,
	b_vdm.pk_org,
	b_vdm.pk_org_unit,
	b_vdm.pk_hospital_stay,
	b_do.xmin
		as xmin_doc_obj
from
	blobs.v_doc_med b_vdm
		inner join blobs.doc_obj b_do on (b_do.fk_doc = b_vdm.pk_doc)
where
	b_vdm.pk_doc = b_do.fk_doc
;

comment on view blobs.v_obj4doc_no_data is
	'denormalized metadata for blobs.doc_obj but without the data itself';

GRANT SELECT ON blobs.v_obj4doc_no_data TO GROUP "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-blobs-v_obj4doc_no_data.sql', '22.0');
