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
	vo4d.pk_patient as pk_patient,
	vo4d.doc_comment as doc_comment,
	vo4d.date_generated as date_taken,
	vo4d.ext_ref as ext_ref,
	vo4d.seq_idx as obj_seq_idx,
	vo4d.obj_comment as obj_comment,
	vo4d.pk_doc as pk_doc,
	vo4d.pk_obj as pk_obj,
	bdo.data as image
from
	blobs.v_obj4doc_no_data vo4d,
	blobs.doc_obj bdo
where
	vo4d.type = 'patient photograph'
		and
	vo4d.seq_idx = (
		select max(vo4d1.seq_idx)
		from blobs.v_obj4doc_no_data vo4d1
		where
			vo4d1.pk_patient = vo4d.pk_patient
				and
			vo4d1.type = 'patient photograph'
		group by date_generated
		order by date_generated desc limit 1
	)
		and
	bdo.pk = vo4d.pk_obj
;

comment on view blobs.v_latest_mugshot is
	'shows the latest picture of the patient, currently the highest
	 seq_idx of the newest document of type "patient photograph"';

grant select on blobs.v_latest_mugshot to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v21-blobs-v_latest_mugshot.sql', '21.0');
