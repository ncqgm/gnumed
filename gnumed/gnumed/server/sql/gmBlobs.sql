-- BLOB tables for GNUmed

-- license: GPL
-- author: Karsten Hilbert <Karsten.Hilbert@gmx.net>

-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmBlobs.sql,v $
-- $Revision: 1.60 $ $Date: 2006-02-05 14:29:07 $ $Author: ncq $

-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- =============================================
create schema blobs authorization "gm-dbo";

-- =============================================
create table blobs.xlnk_identity (
	pk serial primary key,
	xfk_identity integer unique not null,
	pupic text unique not null,
	data text unique default null
) inherits (audit.audit_fields);

-- =============================================
CREATE TABLE blobs.doc_type (
	pk serial primary key,
	name text
		not null
		unique,
	is_user boolean
		not null
		default true
);

-- FIXME: add comment

-- =============================================
CREATE TABLE blobs.doc_med (
	pk serial primary key,
	patient_id integer
		not null
		references blobs.xlnk_identity(xfk_identity)
		on update cascade
		on delete cascade,
	type integer
		not null
		references blobs.doc_type(pk)
		on update cascade
		on delete restrict,
	comment text,
	"date" timestamp with time zone
		not null
		default CURRENT_TIMESTAMP,
	ext_ref text
);

-- =============================================
-- FIXME: audit trail ?
CREATE TABLE blobs.doc_obj (
	pk serial primary key,
	doc_id integer
		not null
		references blobs.doc_med(pk)
		on update cascade
		on delete restrict,
	seq_idx integer,
	comment text,
	fk_intended_reviewer integer
		not null
		references dem.staff(pk)
		on update cascade
		on delete restrict,
	data bytea
		not null
);

-- =============================================
CREATE TABLE blobs.doc_desc (
	pk serial primary key,
	doc_id integer
		references blobs.doc_med(pk)
		on delete cascade
		on update cascade,
	"text" text,
	unique(doc_id, "text")
);

-- =============================================
create table blobs.reviewed_doc_objs (
	primary key (pk),
	foreign key (fk_reviewed_row)
		references blobs.doc_obj(pk)
		on update cascade
		on delete cascade,
	unique (fk_reviewed_row, fk_reviewer)
) inherits (clin.review_root);

-- =============================================
-- do simple schema revision tracking
select public.log_script_insertion('$RCSfile: gmBlobs.sql,v $', '$Revision: 1.60 $');

-- =============================================
-- questions:
--  - do we need doc_desc linkeable to doc_obj, too ?
--  IH: no, OCR etc. should span the multiple pages
--  - should (potentially large) binary objects be moved to audit tables ?!?
-- IH: no, doc_med should be audited, but not doc_obj. doc_obj rows never change anyway.
-- KH: well, they do get deleted, which ought to be audited

-- notes:
-- - as this uses BYTEA for storing binary data we have the following limitations
--   - needs postgres >= 7.1
--   - needs proper escaping of NUL, \ and ' (should go away once postgres 7.3 arrives)
--   - has a 1 GB limit for data objects
-- - we explicitely don't store MIME types etc. as selecting an appropriate viewer is a runtime issue
-- - it is helpful to structure text in doc_desc to be able to identify source/content etc.
-- =============================================
-- $Log: gmBlobs.sql,v $
-- Revision 1.60  2006-02-05 14:29:07  ncq
-- - proper behaviour for blobs.reviewed_doc_objs foreign keys on update/delete
--
-- Revision 1.59  2006/01/27 22:24:04  ncq
-- - let fk_intended_reviewer reference pk_staff
-- - disallow deletion of any staff that reviewed a document
-- - add reviewed_doc_objs
--
-- Revision 1.58  2006/01/13 13:54:14  ncq
-- - move comments to "-dynamic" file
-- - make doc_obj.seq_idx nullable - there actually may not be a mandatory order to the parts
-- - make doc_obj.data not null - a part without data is meaningless
--
-- Revision 1.57  2006/01/11 13:16:20  ncq
-- - id -> pk
--
-- Revision 1.56  2006/01/05 16:04:37  ncq
-- - move auditing to its own schema "audit"
--
-- Revision 1.55  2005/12/04 09:38:22  ncq
-- - add fk_intended_reviewer to doc_obj
--
-- Revision 1.54  2005/11/27 12:58:19  ncq
-- - factor out dynamic stuff
--
-- Revision 1.53  2005/11/25 15:02:05  ncq
-- - use xlnk_identity in blobs. now
--
-- Revision 1.52  2005/11/11 23:03:55  ncq
-- - add is_user to doc_type
--
-- Revision 1.51  2005/10/26 21:33:25  ncq
-- - review status tracking
--
-- Revision 1.50  2005/10/24 19:09:43  ncq
-- - explicit "blobs." qualifying
--
-- Revision 1.49  2005/09/19 16:38:51  ncq
-- - adjust to removed is_core from gm_schema_revision
--
-- Revision 1.48  2005/09/04 07:27:03  ncq
-- - document rationale for using bytea
--
-- Revision 1.47  2005/07/14 21:31:42  ncq
-- - partially use improved schema revision tracking
--
-- Revision 1.46  2005/02/12 13:49:13  ncq
-- - identity.id -> identity.pk
-- - allow NULL for identity.fk_marital_status
-- - subsequent schema changes
--
-- Revision 1.45  2004/10/11 18:58:45  ncq
-- - rolled back Ian's changes but retained his comments
-- - needs further thought before implementation
--
-- Revision 1.42  2004/09/20 21:12:42  ncq
-- - constraint on doc_desc
-- - improve v_obj4doc
-- - fix v_latest_mugshot
--
-- Revision 1.41  2004/04/07 18:16:06  ncq
-- - move grants into re-runnable scripts
-- - update *.conf accordingly
--
-- Revision 1.40  2004/03/03 15:47:31  ncq
-- - collect blob views in their own file
--
-- Revision 1.39  2004/03/03 05:24:01  ihaywood
-- patient photograph support
--
-- Revision 1.38  2004/01/05 00:58:27  ncq
-- - remove excessive quoting
--
-- Revision 1.37  2004/01/05 00:31:01  ncq
-- - prefer TEXT of VARCHAR
--
-- Revision 1.36  2003/12/29 15:28:03  uid66147
-- - add default current_date to doc_med.date
-- - remove doc_med_external_ref table, we use x_db_fk's now
-- - add on delete/update rules
-- - allow NULL doc_id in doc_obj (think doc object creation)
--
-- Revision 1.35  2003/05/12 12:43:39  ncq
-- - gmI18N, gmServices and gmSchemaRevision are imported globally at the
--   database level now, don't include them in individual schema file anymore
--
-- Revision 1.34  2003/04/07 11:09:54  ncq
-- - separated out data inserts from schema definition
--
