-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
drop view if exists blobs.v_reviewed_doc_objects cascade;

create view blobs.v_reviewed_doc_objects as
select
	b_rdo.fk_reviewed_row
		as pk_doc_obj,
	coalesce (
		d_s.short_alias,
		'<#' || b_rdo.fk_reviewer || '>'
	)	as reviewer,
	b_rdo.is_technically_abnormal
		as is_technically_abnormal,
	b_rdo.clinically_relevant
		as clinically_relevant,
	(b_rdo.fk_reviewer = b_do.fk_intended_reviewer)
		as is_review_by_responsible_reviewer,
	b_rdo.fk_reviewer = (select pk from dem.staff where db_user = CURRENT_USER)
		as is_your_review,
	b_rdo.comment,
	b_rdo.modified_when
		as reviewed_when,
	b_rdo.modified_by
		as modified_by,
	b_rdo.pk
		as pk_review_root,
	b_rdo.fk_reviewer
		as pk_reviewer,
	c_enc.fk_patient
		as pk_patient,
	b_dm.fk_encounter
		as pk_encounter,
	b_dm.fk_episode
		as pk_episode,
	c_epi.fk_health_issue
		as pk_health_issue
from
	blobs.reviewed_doc_objs b_rdo
		left join dem.staff d_s on d_s.pk = b_rdo.fk_reviewer
		left join blobs.doc_obj b_do on b_do.pk = b_rdo.fk_reviewed_row
			left join blobs.doc_med b_dm on b_do.fk_doc = b_dm.pk
				left join clin.episode c_epi on b_dm.fk_episode = c_epi.pk
					left join clin.encounter c_enc on c_epi.fk_encounter = c_enc.pk
;

grant select on blobs.v_reviewed_doc_objects TO GROUP "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-blobs-v_reviewed_doc_objects-fixup.sql', '22.25');
