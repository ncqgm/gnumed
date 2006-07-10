-- dynamic BLOB structures GNUmed

-- license: GPL
-- author: Karsten Hilbert <Karsten.Hilbert@gmx.net>

-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmBlobViews.sql,v $
-- $Revision: 1.31 $ $Date: 2006-07-10 21:48:44 $ $Author: ncq $

-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- =============================================
select audit.add_table_for_audit('blobs', 'xlnk_identity');

-- -- doc_type --
comment on table blobs.doc_type is
	'this table enumerates the document types known to the system';
comment on column blobs.doc_type.name is
	'the name/label of the document type';
comment on column blobs.doc_type.is_user is
	'Whether this document type was supplied at installation/upgrade time or by the user at runtime.';


-- -- doc_med --
select audit.add_table_for_audit('blobs', 'doc_med');

COMMENT ON TABLE blobs.doc_med IS
	'a medical document object possibly containing several
	 data objects such as several pages of a paper document';
COMMENT ON COLUMN blobs.doc_med.patient_id IS
	'the patient this document belongs to';
comment on COLUMN blobs.doc_med.fk_encounter is
	'the encounter in which this document was entered into the system';
comment on COLUMN blobs.doc_med.fk_episode is
	'the episode this document pertains to, this may not be the only
	 one applicable to the document (think discharge letters), see also
	 lnk_doc_med2episode';
COMMENT ON COLUMN blobs.doc_med.type IS
	'semantic type of document (not type of file or mime
	 type), such as "referral letter", "discharge summary", etc.';
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

\unset ON_ERROR_STOP
drop function blobs.trf_remove_primary_episode_from_link_table() cascade;
\set ON_ERROR_STOP 1

create function blobs.trf_remove_primary_episode_from_link_table()
	returns trigger
	language 'plpgsql'
	as '
BEGIN
	-- if update
	if TG_OP = ''UPDATE'' then
		-- and no change
		if NEW.fk_episode = OLD.fk_episode then
			-- then do nothing
			return NEW;
		end if;
	end if;
	-- if already in link table
	perform 1 from blobs.lnk_doc_med2episode ldm2e where ldm2e.fk_episode = NEW.fk_episode and ldm2e.fk_doc_med = NEW.pk;
	if FOUND then
		-- delete from link table
		delete from blobs.lnk_doc_med2episode where fk_episode = NEW.fk_episode and fk_doc_med = NEW.pk;
	end if;
	return NEW;
END;';

comment on function blobs.trf_remove_primary_episode_from_link_table() is
	'This trigger function is called when a doc_med row
	 is inserted or updated. It makes sure the primary
	 episode listed in doc_med is not duplicated in
	 lnk_doc_med2episode for the same document. If it
	 exists in the latter it is removed from there.';

create trigger tr_remove_primary_episode_from_link_table
	after insert or update on blobs.doc_med
	for each row execute procedure blobs.trf_remove_primary_episode_from_link_table();


-- -- lnk_doc_med2episode --
comment on table blobs.lnk_doc_med2episode is
	'this allows linking documents to episodes,
	 each document can apply to several episodes
	 but only once each';

-- FIXME: trigger on insert: fail silently if already in doc_med.fk_episode	 
\unset ON_ERROR_STOP
drop function blobs.trf_do_not_duplicate_primary_episode_in_link_table() cascade;
\set ON_ERROR_STOP 1

create function blobs.trf_do_not_duplicate_primary_episode_in_link_table()
	returns trigger
	language 'plpgsql'
	as '
BEGIN
	-- if already in doc_med
	perform 1 from blobs.doc_med dm where dm.fk_episode = NEW.fk_episode and dm.pk = NEW.fk_doc_med;
	if FOUND then
		-- skip the insert/update
		return null;
	end if;
	return NEW;
END;';

comment on function blobs.trf_do_not_duplicate_primary_episode_in_link_table() is
	'This trigger function is called before a lnk_doc_med2episode
	 row is inserted or updated. It makes sure the episode does
	 not duplicate the primary episode for this document listed
	 in doc_med. If it does the insert/update is skipped.';

create trigger tr_do_not_duplicate_primary_episode_in_link_table
	before insert or update on blobs.lnk_doc_med2episode
	for each row execute procedure blobs.trf_do_not_duplicate_primary_episode_in_link_table();


-- -- doc_obj --
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
select audit.add_table_for_audit('blobs', 'doc_desc');

COMMENT ON TABLE blobs.doc_desc is
	'A textual description of the content such
	 as a result summary. Several of these may
	 belong to one document object.';

-- reviewed_doc_objs
comment on table blobs.reviewed_doc_objs is
	'review table for documents (per object such as a page)';

-- =============================================
\unset ON_ERROR_STOP
drop function blobs.trf_mark_unreviewed_on_doc_obj_update() cascade;
\set ON_ERROR_STOP 1

create function blobs.trf_mark_unreviewed_on_doc_obj_update()
	returns trigger
	language 'plpgsql'
	as '
BEGIN
	if (NEW.data != OLD.data) or ((NEW.data != OLD.data) is NULL) then
		delete from blobs.reviewed_doc_objs where fk_reviewed_row = OLD.pk;
	end if;
	return NEW;
END;';

create trigger tr_mark_unreviewed_on_doc_obj_update
	after update on blobs.doc_obj
	for each row execute procedure blobs.trf_mark_unreviewed_on_doc_obj_update();

-- =============================================
\unset ON_ERROR_STOP
drop view blobs.v_doc_type cascade;
\set ON_ERROR_STOP 1

create view blobs.v_doc_type as
select
	dt.pk as pk_doc_type,
	dt.name as type,
	_(dt.name) as l10n_type,
	dt.is_user as is_user,
	dt.xmin as xmin_doc_type
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
	cle.description as episode,
	dm.comment as comment,
	cle.is_open as episode_open,
	dm.type as pk_type,
	dm.fk_encounter as pk_encounter,
	dm.fk_episode as pk_episode,
	dm.modified_when as modified_when,
	dm.xmin as xmin_doc_med
from
	blobs.doc_med dm,
	blobs.v_doc_type vdt,
	clin.episode cle
where
	vdt.pk_doc_type = dm.type and
	cle.pk = dm.fk_episode
;

-- =============================================
create view blobs.v_obj4doc_old as
select
	dobj.data as object,
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
	dobj.fk_intended_reviewer as pk_intended_reviewer,
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
	vdm.pk_episode
		as pk_episode,
	dobj.xmin
		as xmin_doc_obj
from
	blobs.v_doc_med vdm,
	blobs.doc_obj dobj
where
	vdm.pk_doc = dobj.doc_id
;

-- =============================================
create view blobs.v_obj4doc as
select
	dobj.data as object,
	vo4dnd.*
from
	blobs.v_obj4doc_no_data vo4dnd,
	blobs.doc_obj dobj
where
	vo4dnd.pk_obj = dobj.pk
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
\unset ON_ERROR_STOP
drop view blobs.v_reviewed_doc_objects cascade;
\set ON_ERROR_STOP 1

create view blobs.v_reviewed_doc_objects as
select
	rdo.fk_reviewed_row as pk_doc_obj,
	(select short_alias from dem.v_staff where pk_staff = rdo.fk_reviewer)
		as reviewer,
	rdo.is_technically_abnormal as is_technically_abnormal,
	rdo.clinically_relevant as clinically_relevant,
	exists(select 1 from blobs.doc_obj where pk=rdo.fk_reviewed_row and fk_intended_reviewer=rdo.fk_reviewer)
		as is_review_by_responsible_reviewer,
	exists(select 1 from dem.v_staff where pk_staff=rdo.fk_reviewer and db_user=CURRENT_USER)
		as is_your_review,
	rdo.comment,
	rdo.modified_when as reviewed_when,
	rdo.modified_by as modified_by,
	rdo.pk as pk_review_root,
	rdo.fk_reviewer as pk_reviewer
from
	blobs.reviewed_doc_objs rdo
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
	, blobs.lnk_doc_med2episode
TO GROUP "gm-doctors";

-- views
GRANT SELECT ON
	blobs.v_doc_type
	, blobs.v_doc_med
	, blobs.v_obj4doc
	, blobs.v_obj4doc_no_data
	, blobs.v_latest_mugshot
	, blobs.v_reviewed_doc_objects
TO GROUP "gm-doctors";

-- =============================================
-- do simple schema revision tracking
select public.log_script_insertion('$RCSfile: gmBlobViews.sql,v $', '$Revision: 1.31 $');

-- =============================================
-- $Log: gmBlobViews.sql,v $
-- Revision 1.31  2006-07-10 21:48:44  ncq
-- - improve blobs.v_doc_type
--
-- Revision 1.30  2006/07/04 21:40:17  ncq
-- - add is_user to blobs.v_doc_type
--
-- Revision 1.29  2006/05/25 22:26:24  ncq
-- - reformat blobs.v_obj4doc_no_data and add episode name and pk
--
-- Revision 1.28  2006/05/09 11:37:52  ncq
-- - properly create blobs.v_obj4doc
--
-- Revision 1.27  2006/05/08 16:38:27  ncq
-- - derive blobs.v_obj4doc from blobs.v_obj4doc_no_data
-- - add modified_when to blobs.v_doc_med for sorting
--
-- Revision 1.26  2006/05/06 20:47:45  ncq
-- - include some episode data in blobs.v_doc_med
--
-- Revision 1.25  2006/05/01 18:51:07  ncq
-- - add v_obj4doc_no_data for denormalized access to object metadata without
--   incurring overhead for BLOB data per object
-- - grants added
--
-- Revision 1.24  2006/04/29 18:19:38  ncq
-- - comment more columns
-- - add fk_encounter/fk_episode to doc_med
-- - trigger to make sure episode is linked to doc in doc_med OR lnk_doc_med2episode only
-- - doc_med.data now TEXT ! not timestamp (needs to be able to be fuzzy)
-- - adjust test BLOBs to new situation
--
-- Revision 1.23  2006/03/06 09:39:31  ncq
-- - lnk_doc_med2episode
--
-- Revision 1.22  2006/02/27 22:39:32  ncq
-- - spell out rfe/aoe
--
-- Revision 1.21  2006/02/13 08:29:51  ncq
-- - add blobs.v_reviewed_doc_objects
--
-- Revision 1.20  2006/02/02 17:54:48  ncq
-- - invalidate reviewed status on update to blobs.doc_obj.data
-- - list status of review by: me/intended reviewer in blobs.v_obj4doc
--
-- Revision 1.19  2006/01/27 22:21:58  ncq
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
