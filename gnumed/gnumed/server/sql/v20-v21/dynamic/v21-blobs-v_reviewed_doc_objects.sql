-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
--
-- ==============================================================
-- remember to handle dependant objects possibly dropped by CASCADE
drop view if exists blobs.v_reviewed_doc_objects cascade;

create view blobs.v_reviewed_doc_objects as
select
	rdo.fk_reviewed_row as pk_doc_obj,
	coalesce (
		(select short_alias from dem.staff where pk=rdo.fk_reviewer),
		'<#' || rdo.fk_reviewer || '>'
	) as reviewer,
	rdo.is_technically_abnormal as is_technically_abnormal,
	rdo.clinically_relevant as clinically_relevant,
	exists(select 1 from blobs.doc_obj where pk=rdo.fk_reviewed_row and fk_intended_reviewer=rdo.fk_reviewer)
		as is_review_by_responsible_reviewer,
	exists(select 1 from dem.staff where pk=rdo.fk_reviewer and db_user=CURRENT_USER)
		as is_your_review,
	rdo.comment,
	rdo.modified_when as reviewed_when,
	rdo.modified_by as modified_by,
	rdo.pk as pk_review_root,
	rdo.fk_reviewer as pk_reviewer,
	(select pk_patient from blobs.v_obj4doc_no_data where pk_obj=rdo.fk_reviewed_row)
		as pk_patient,
	(select pk_encounter from blobs.v_obj4doc_no_data where pk_obj=rdo.fk_reviewed_row)
		as pk_encounter,
	(select pk_episode from blobs.v_obj4doc_no_data where pk_obj=rdo.fk_reviewed_row)
		as pk_episode,
	(select pk_health_issue from blobs.v_obj4doc_no_data where pk_obj=rdo.fk_reviewed_row)
		as pk_health_issue
from
	blobs.reviewed_doc_objs rdo
;


grant select on blobs.v_reviewed_doc_objects to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v21-blobs-v_reviewed_doc_objects.sql', '21.0');
