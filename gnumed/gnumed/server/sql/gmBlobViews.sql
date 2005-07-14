-- BLOB views for GNUmed

-- license: GPL
-- author: Karsten Hilbert <Karsten.Hilbert@gmx.net>

-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmBlobViews.sql,v $
-- $Revision: 1.9 $ $Date: 2005-07-14 21:31:42 $ $Author: ncq $

-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- =============================================
\unset ON_ERROR_STOP
drop view v_doc_type;
\set ON_ERROR_STOP 1

create view v_doc_type as
select
	dt.pk as pk_doc_type,
	dt.name as type,
	_(dt.name) as l10n_type
from
	doc_type dt
;

-- =============================================
\unset ON_ERROR_STOP
drop view v_doc_med;
\set ON_ERROR_STOP 1

create view v_doc_med as
select
	dm.patient_id as pk_patient,
	dm.id as pk_doc,
	dm.date as date,
	vdt.type as type,
	vdt.l10n_type as l10n_type,
	dm.ext_ref as ext_ref,
	dm.comment as comment,
	dm.type as pk_type,
	dm.xmin as xmin_doc_med
from
	doc_med dm,
	v_doc_type vdt
where
	vdt.pk_doc_type = dm.type
;

-- =============================================
\unset ON_ERROR_STOP
drop view v_obj4doc;
\set ON_ERROR_STOP 1

create view v_obj4doc as
select
	vdm.pk_patient as pk_patient,
	dobj.id as pk_obj,
	dobj.seq_idx as seq_idx,
	vdm.date as date_generated,
	vdm.type as type,
	vdm.l10n_type as l10n_type,
	vdm.ext_ref as ext_ref,
	octet_length(coalesce(dobj.data, '')) as size,
	vdm.comment as doc_comment,
	dobj.comment as obj_comment,
	dobj.data as object,
	vdm.pk_doc as pk_doc,
	vdm.pk_type as pk_type,
	dobj.xmin as xmin_doc_obj
from
	v_doc_med vdm,	
	doc_obj dobj
where
	vdm.pk_doc = dobj.doc_id
;

-- =============================================
\unset ON_ERROR_STOP
drop view v_latest_mugshot;
\set ON_ERROR_STOP 1

create view v_latest_mugshot as
select
	vo4d.pk_patient as pk_patient,
	vo4d.doc_comment as doc_comment,
	vo4d.date_generated as date_taken,
	vo4d.ext_ref as ext_ref,
	vo4d.seq_idx as obj_seq_idx,
	vo4d.obj_comment as obj_comment,
	vo4d.pk_doc as pk_doc,
	vo4d.pk_obj as pk_obj,
	vo4d.object as image
from
	v_obj4doc vo4d
where
	vo4d.type = 'patient photograph'
		and
	vo4d.seq_idx = (
		select max(vo4d1.seq_idx)
		from v_obj4doc vo4d1
		where
			vo4d1.pk_patient = vo4d.pk_patient
				and
			vo4d1.type = 'patient photograph'
	)
;
-- =============================================

-- 
--CREATE VIEW v_lnk_result2lab_req AS SELECT test_result.id AS fk_result, med_doc.id AS fk_request 
--	FROM med_doc, test_result 
--	WHERE med_doc.type = 28 and test_result.fk_doc = med_doc.id;
--
--CREATE VIEW v_incoming_path AS SELECT * FROM med_doc WHERE type = 28;
--CREATE VIEW v_outgoing_path AS SELECT * FROM med_doc WHERE type = 27;
--
--CREATE VIEW v_lab_request AS SELECT DISTINCT ON (outgoing.id)
--	o.id AS pk,
--	o.remote_id AS fk_test_org,
--	o.ext_id AS request_id,
--	o.local_id AS fk_requestor,
--	i.ext_id AS lab_request_id,
--	i.request_rxd_when AS lab_rxd_when,
--	i.date AS results_reported,
--	i.report_status AS request_status,
--	(o.fk_queue = 11) AS is_pending
--FROM v_outgoing_path o LEFT OUTER JOIN v_incoming_path i ON (o.id = i.reply_to)
--ORDER BY i.date; -- always get the latest report


-- tables
GRANT SELECT, INSERT, UPDATE, DELETE ON
	doc_desc
	, doc_desc_id_seq
	, doc_obj
	, doc_obj_id_seq
	, doc_med
	, doc_med_id_seq
	, doc_type
	, doc_type_pk_seq
TO GROUP "gm-doctors";

-- views
GRANT SELECT ON
	v_doc_type
	, v_doc_med
	, v_obj4doc
	, v_latest_mugshot
TO GROUP "gm-doctors";

-- =============================================
-- do simple schema revision tracking
delete from gm_schema_revision where filename='$RCSfile: gmBlobViews.sql,v $';
INSERT INTO gm_schema_revision (filename, version, is_core) VALUES('$RCSfile: gmBlobViews.sql,v $', '$Revision: 1.9 $', True);

-- =============================================
-- $Log: gmBlobViews.sql,v $
-- Revision 1.9  2005-07-14 21:31:42  ncq
-- - partially use improved schema revision tracking
--
-- Revision 1.8  2004/10/29 22:37:02  ncq
-- - propagate xmin to the relevant views to business classes can
--   use it for concurrency conflict detection
-- - fix v_problem_list to properly display a patient's problems
--
-- Revision 1.7  2004/10/11 19:29:13  ncq
-- - v_i18n_doc_type -> v_doc_type
-- - v_doc_med
--
-- Revision 1.6  2004/10/10 13:13:51  ihaywood
-- example of views to emulate the gmMeasurements tables
--
-- Revision 1.5  2004/09/20 21:12:42  ncq
-- - constraint on doc_desc
-- - improve v_obj4doc
-- - fix v_latest_mugshot
--
-- Revision 1.4  2004/07/17 20:57:53  ncq
-- - don't use user/_user workaround anymore as we dropped supporting
--   it (but we did NOT drop supporting readonly connections on > 7.3)
--
-- Revision 1.3  2004/04/16 00:36:23  ncq
-- - cleanup, constraints
--
-- Revision 1.2  2004/04/07 18:16:06  ncq
-- - move grants into re-runnable scripts
-- - update *.conf accordingly
--
-- Revision 1.1  2004/03/03 15:47:32  ncq
-- - collect blob views in their own file
--
