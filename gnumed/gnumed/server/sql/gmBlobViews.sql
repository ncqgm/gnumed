-- BLOB views for GNUmed

-- license: GPL
-- author: Karsten Hilbert <Karsten.Hilbert@gmx.net>

-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmBlobViews.sql,v $
-- $Revision: 1.3 $ $Date: 2004-04-16 00:36:23 $ $Author: ncq $

-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- =============================================
\unset ON_ERROR_STOP
drop view v_i18n_doc_type;
\set ON_ERROR_STOP 1

create view v_i18n_doc_type as
	select
		doc_type.id,
		_(doc_type.name)
	from
		doc_type
	;

-- this should include: distinct on _(doc_type.name) or some such
-- =============================================
\unset ON_ERROR_STOP
drop view v_obj4doc;
\set ON_ERROR_STOP 1

create view v_obj4doc as
select
	dm.id as pk_doc,
	dobj.id as pk_obj,
	dm.patient_id as pk_patient,
	dm.type as pk_type,
	dt.name as type,
	_(dt.name) as l10n_type,
	dm.comment as doc_comment,
	dm.date as date_generated,
	dm.ext_ref as ext_ref,
	dobj.seq_idx as seq_idx,
	dobj.comment as obj_comment,
	dobj.data as object
from
	doc_med dm,
	doc_obj dobj,
	doc_type dt
where
	dm.type=dt.id and
	dobj.doc_id=dm.id
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
	vo4d.obj_comment as obj_comment,
	vo4d.object as image,
	dd.text as description,
	vo4d.pk_doc as pk_doc,
	vo4d.pk_obj as pk_obj,
	dd.id as pk_desc
from
	v_obj4doc vo4d,
	doc_desc dd
where
	vo4d.type='patient photo' and
	dd.doc_id=vo4d.pk_doc and
	vo4d.seq_idx=(
		select max(seq_idx)
		from v_obj4doc vo4d1
		where vo4d1.pk_patient=vo4d.pk_patient
	)
;
-- =============================================
GRANT SELECT ON
	doc_desc,
	doc_obj,
	doc_med,
	doc_type
TO GROUP "gm-doctors";

GRANT SELECT, INSERT, UPDATE, DELETE ON
	doc_desc,
	"doc_desc_id_seq",
	doc_obj,
	"doc_obj_id_seq",
	doc_med,
	"doc_med_id_seq",
	"doc_type"
TO GROUP "_gm-doctors";

-- views
GRANT SELECT ON
	v_i18n_doc_type
	, v_obj4doc
	, v_latest_mugshot
TO GROUP "gm-doctors";

-- =============================================
-- do simple schema revision tracking
delete from gm_schema_revision where filename='$RCSfile: gmBlobViews.sql,v $';
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmBlobViews.sql,v $', '$Revision: 1.3 $');

-- =============================================
-- $Log: gmBlobViews.sql,v $
-- Revision 1.3  2004-04-16 00:36:23  ncq
-- - cleanup, constraints
--
-- Revision 1.2  2004/04/07 18:16:06  ncq
-- - move grants into re-runnable scripts
-- - update *.conf accordingly
--
-- Revision 1.1  2004/03/03 15:47:32  ncq
-- - collect blob views in their own file
--
