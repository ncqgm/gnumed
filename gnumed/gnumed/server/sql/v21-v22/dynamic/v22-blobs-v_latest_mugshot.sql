-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
-- remember to handle dependent objects possibly dropped by CASCADE
drop view if exists blobs.v_latest_mugshot cascade;

create view blobs.v_latest_mugshot as
select
	b_vo4d.pk_patient
		as pk_patient,
	b_vo4d.doc_comment
		as doc_comment,
	b_vo4d.date_generated
		as date_taken,
	b_vo4d.ext_ref
		as ext_ref,
	b_vo4d.seq_idx
		as obj_seq_idx,
	b_vo4d.obj_comment
		as obj_comment,
	b_vo4d.pk_doc
		as pk_doc,
	b_vo4d.pk_obj
		as pk_obj,
	b_do.data
		as image
from
	blobs.v_obj4doc_no_data b_vo4d,
	blobs.doc_obj b_do
where
	b_vo4d.type = 'patient photograph'
		and
	b_vo4d.seq_idx = (
		select max(b_vo4d1.seq_idx)
		from blobs.v_obj4doc_no_data b_vo4d1
		where
			b_vo4d1.pk_patient = b_vo4d.pk_patient
				and
			b_vo4d1.type = 'patient photograph'
		group by date_generated
		order by date_generated desc limit 1
	)
		and
	b_do.pk = b_vo4d.pk_obj
;

comment on view blobs.v_latest_mugshot is
	'shows the latest picture of the patient, currently the highest
	 seq_idx of the newest document of type "patient photograph"';

grant select on blobs.v_latest_mugshot to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-blobs-v_latest_mugshot.sql', '22.0');
