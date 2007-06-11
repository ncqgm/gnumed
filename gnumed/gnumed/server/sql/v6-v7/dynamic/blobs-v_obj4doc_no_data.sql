-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v2
-- Target database version: v3
--
-- What it does:
-- - upgrade blobs.v_obj4doc_no_data
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: blobs-v_obj4doc_no_data.sql,v 1.1 2007-06-11 18:41:31 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view blobs.v_obj4doc_no_data cascade;
\set ON_ERROR_STOP 1


create view blobs.v_obj4doc_no_data as
select
	vdm.pk_patient
		as pk_patient,
	dobj.pk
		as pk_obj,
	dobj.seq_idx
		as seq_idx,
	octet_length(coalesce(dobj.data, ''))
		as size,
	vdm.date
		as date_generated,
	vdm.type
		as type,
	vdm.l10n_type
		as l10n_type,
	vdm.ext_ref
		as ext_ref,
	vdm.episode
		as episode,
	vdm.comment
		as doc_comment,
	dobj.comment
		as obj_comment,
	dobj.filename
		as filename,
	dobj.fk_intended_reviewer
		as pk_intended_reviewer,
	exists(select 1 from blobs.reviewed_doc_objs where fk_reviewed_row=dobj.pk)
		as reviewed,
	exists (
		select 1 from blobs.reviewed_doc_objs
		where
			fk_reviewed_row = dobj.pk and
			fk_reviewer = (select pk from dem.staff where db_user=current_user)
		) as reviewed_by_you,
	exists (
		select 1 from blobs.reviewed_doc_objs
		where
			fk_reviewed_row = dobj.pk and
			fk_reviewer = dobj.fk_intended_reviewer
		) as reviewed_by_intended_reviewer,
	vdm.pk_doc
		as pk_doc,
	vdm.pk_type
		as pk_type,
	vdm.pk_encounter
		as pk_encounter,
	vdm.pk_episode
		as pk_episode,
	vdm.pk_health_issue
		as pk_health_issue,
	dobj.xmin
		as xmin_doc_obj
from
	blobs.v_doc_med vdm,
	blobs.doc_obj dobj
where
	vdm.pk_doc = dobj.fk_doc
;

comment on view blobs.v_obj4doc_no_data is
	'denormalized metadata for blobs.doc_obj but without the data itself';

-- --------------------------------------------------------------
GRANT SELECT ON blobs.v_obj4doc_no_data TO GROUP "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: blobs-v_obj4doc_no_data.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: blobs-v_obj4doc_no_data.sql,v $
-- Revision 1.1  2007-06-11 18:41:31  ncq
-- - new
--
-- Revision 1.1  2007/03/08 15:10:52  ncq
-- - add filename to blobs object view
--
-- Revision 1.2  2006/10/08 09:13:56  ncq
-- - doc_id now fk_doc
--
-- Revision 1.1  2006/09/25 10:55:01  ncq
-- - added here
--
-- Revision 1.1  2006/09/16 21:45:14  ncq
-- - add PKs for narrative search
--
-- Revision 1.1  2006/09/16 14:02:36  ncq
-- - use this as a template for change scripts
--
--
