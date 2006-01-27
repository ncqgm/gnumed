-- BLOB views for GNUmed

-- license: GPL
-- author: Karsten Hilbert <Karsten.Hilbert@gmx.net>

-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmBlobViews.sql,v $
-- $Revision: 1.19 $ $Date: 2006-01-27 22:21:58 $ $Author: ncq $

-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- =============================================
select audit.add_table_for_audit('blobs', 'xlnk_identity');

-- doc_med --
COMMENT ON TABLE blobs.doc_med IS
	'a medical document object possibly containing several
	 data objects such as several pages of a paper document';
COMMENT ON COLUMN blobs.doc_med.patient_id IS
	'the patient this document belongs to';
COMMENT ON COLUMN blobs.doc_med.type IS
	'semantic type of document (not type of file or mime
	 type), such as >referral letter<, >discharge summary<, etc.';
COMMENT ON COLUMN blobs.doc_med.comment IS
	'additional short comment such as "abdominal", "ward 3,
	 Dr. Stein", etc.';
COMMENT ON COLUMN blobs.doc_med.date IS
	'date of document content creation (such as exam date),
	 NOT date of document creation or date of import; may
	 be imprecise such as "7/99"';
COMMENT ON COLUMN blobs.doc_med.ext_ref IS
	'external reference string of physical document,
	 original paper copy can be found with this';

-- doc_obj --
COMMENT ON TABLE blobs.doc_obj IS
	'possibly several of these form a medical document
	 such as multiple scanned pages/images';
COMMENT ON COLUMN blobs.doc_obj.seq_idx IS
	'index of this object in the sequence
	 of objects for this document';
COMMENT ON COLUMN blobs.doc_obj.comment IS
	'optional tiny comment for this
	 object, such as "page 1"';
comment on column blobs.doc_obj.fk_intended_reviewer is
	'who is *supposed* to review this item';
COMMENT ON COLUMN blobs.doc_obj.data IS
	'actual binary object data;\n
	 here is why we use bytea:\n
== --------------------------------------------------\n
To: leon@oss.minimetria.com\n
Cc: pgsql-sql@postgresql.org\n
Subject: Re: [SQL] Recommendation on bytea or blob for binary data like images \n
Date: Fri, 02 Sep 2005 16:33:09 -0400\n
Message-ID: <17794.1125693189@sss.pgh.pa.us>\n
From: Tom Lane <tgl@sss.pgh.pa.us>\n
List-Archive: <http://archives.postgresql.org/pgsql-sql>\n
List-Help: <mailto:majordomo@postgresql.org?body=help>\n
List-ID: <pgsql-sql.postgresql.org>\n
\n
leon@oss.minimetria.com writes:\n
> Hi, I"d like to know what the official recommendation is on which binary\n
> datatype to use for common small-binary size use.\n
\n
If bytea will work for you, it"s definitely the thing to use.  The only\n
real drawback to bytea is that there"s currently no API to read and\n
write bytea values in a streaming fashion.  If your objects are small\n
enough that you can load and store them as units, bytea is fine.\n
\n
BLOBs, on the other hand, have a number of drawbacks --- hard to dump,\n
impossible to secure, etc.\n
\n
			regards, tom lane\n
== --------------------------------------------------';

-- doc_desc --
COMMENT ON TABLE blobs.doc_desc is
	'A textual description of the content such
	 as a result summary. Several of these may
	 belong to one document object.';

-- reviewed_doc_objs
comment on table blobs.reviewed_doc_objs is
	'review table for documents (per object such as a page)';

-- =============================================
\unset ON_ERROR_STOP
drop view blobs.v_doc_type cascade;
\set ON_ERROR_STOP 1

create view blobs.v_doc_type as
select
	dt.pk as pk_doc_type,
	dt.name as type,
	_(dt.name) as l10n_type
from
	blobs.doc_type dt
;

-- =============================================
create view blobs.v_doc_med as
select
	dm.patient_id as pk_patient,
	dm.pk as pk_doc,
	dm.date as date,
	vdt.type as type,
	vdt.l10n_type as l10n_type,
	dm.ext_ref as ext_ref,
	dm.comment as comment,
	dm.type as pk_type,
	dm.xmin as xmin_doc_med
from
	blobs.doc_med dm,
	blobs.v_doc_type vdt
where
	vdt.pk_doc_type = dm.type
;

-- =============================================
create view blobs.v_obj4doc as
select
	vdm.pk_patient as pk_patient,
	dobj.pk as pk_obj,
	dobj.seq_idx as seq_idx,
	vdm.date as date_generated,
	vdm.type as type,
	vdm.l10n_type as l10n_type,
	vdm.ext_ref as ext_ref,
	octet_length(coalesce(dobj.data, '')) as size,
	vdm.comment as doc_comment,
	dobj.comment as obj_comment,
	exists(select 1 from blobs.reviewed_doc_objs where fk_reviewed_row=dobj.pk)
		as reviewed,
	(select (signature is not null) from blobs.reviewed_doc_objs where fk_reviewed_row=dobj.pk)
		as signed,
	dobj.data as object,
	vdm.pk_doc as pk_doc,
	vdm.pk_type as pk_type,
	dobj.xmin as xmin_doc_obj
from
	blobs.v_doc_med vdm,
	blobs.doc_obj dobj
where
	vdm.pk_doc = dobj.doc_id
;

-- =============================================
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
	vo4d.object as image
from
	blobs.v_obj4doc vo4d
where
	vo4d.type = 'patient photograph'
		and
	vo4d.seq_idx = (
		select max(vo4d1.seq_idx)
		from blobs.v_obj4doc vo4d1
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

-- =============================================
-- schema
grant usage on schema blobs to group "gm-doctors";

-- tables
GRANT SELECT, INSERT, UPDATE, DELETE on
	blobs.xlnk_identity
	, blobs.xlnk_identity_pk_seq
	, blobs.doc_desc
	, blobs.doc_desc_pk_seq
	, blobs.doc_obj
	, blobs.doc_obj_pk_seq
	, blobs.doc_med
	, blobs.doc_med_pk_seq
	, blobs.doc_type
	, blobs.doc_type_pk_seq
	, blobs.reviewed_doc_objs
TO GROUP "gm-doctors";

-- views
GRANT SELECT ON
	blobs.v_doc_type
	, blobs.v_doc_med
	, blobs.v_obj4doc
	, blobs.v_latest_mugshot
TO GROUP "gm-doctors";

-- =============================================
-- do simple schema revision tracking
select public.log_script_insertion('$RCSfile: gmBlobViews.sql,v $', '$Revision: 1.19 $');

-- =============================================
-- $Log: gmBlobViews.sql,v $
-- Revision 1.19  2006-01-27 22:21:58  ncq
-- - add signed/reviewed to v_objs4doc
-- - add grants
--
-- Revision 1.18  2006/01/24 22:55:19  ncq
-- - include reviewed status in v_obj4doc
--
-- Revision 1.17  2006/01/13 13:54:14  ncq
-- - move comments to "-dynamic" file
-- - make doc_obj.seq_idx nullable - there actually may not be a mandatory order to the parts
-- - make doc_obj.data not null - a part without data is meaningless
--
-- Revision 1.16  2006/01/11 13:15:51  ncq
-- - id -> pk
--
-- Revision 1.15  2006/01/06 10:04:16  ncq
-- - move add_table_for_audit() into audit schema
--
-- Revision 1.14  2006/01/01 15:49:10  ncq
-- - grants for blobs.xlnk_identity
--
-- Revision 1.13  2005/11/27 12:58:19  ncq
-- - factor out dynamic stuff
--
-- Revision 1.12  2005/10/24 19:09:43  ncq
-- - explicit "blobs." qualifying
--
-- Revision 1.11  2005/09/19 16:38:51  ncq
-- - adjust to removed is_core from gm_schema_revision
--
-- Revision 1.10  2005/09/13 11:55:46  ncq
-- - properly drop views so re-running/updating works
--
-- Revision 1.9  2005/07/14 21:31:42  ncq
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
