-- BLOB tables for GNUmed

-- license: GPL
-- author: Karsten Hilbert <Karsten.Hilbert@gmx.net>

-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmBlobs.sql,v $
-- $Revision: 1.55 $ $Date: 2005-12-04 09:38:22 $ $Author: ncq $

-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- =============================================
create schema blobs authorization "gm-dbo";

-- =============================================
--\unset ON_ERROR_STOP

create table blobs.xlnk_identity (
	pk serial primary key,
	xfk_identity integer unique not null,
	pupic text unique not null,
	data text unique default null
) inherits (public.audit_fields);

--\set ON_ERROR_STOP 1

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
	id serial primary key,
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

-- =============================================
CREATE TABLE blobs.doc_obj (
	id serial primary key,
	doc_id integer
		not null
		references blobs.doc_med(id)
		on update cascade
		on delete restrict,
	seq_idx integer
		not null,
	comment text,
	fk_intended_reviewer integer
		not null
		references blobs.xlnk_identity(xfk_identity),
	data bytea
);

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
	'actual binary object data;
	 here is why we use bytea:
== --------------------------------------------------
To: leon@oss.minimetria.com
Cc: pgsql-sql@postgresql.org
Subject: Re: [SQL] Recommendation on bytea or blob for binary data like images 
Date: Fri, 02 Sep 2005 16:33:09 -0400
Message-ID: <17794.1125693189@sss.pgh.pa.us>
From: Tom Lane <tgl@sss.pgh.pa.us>
List-Archive: <http://archives.postgresql.org/pgsql-sql>
List-Help: <mailto:majordomo@postgresql.org?body=help>
List-ID: <pgsql-sql.postgresql.org>

leon@oss.minimetria.com writes:
> Hi, I"d like to know what the official recommendation is on which binary
> datatype to use for common small-binary size use.

If bytea will work for you, it"s definitely the thing to use.  The only
real drawback to bytea is that there"s currently no API to read and
write bytea values in a streaming fashion.  If your objects are small
enough that you can load and store them as units, bytea is fine.

BLOBs, on the other hand, have a number of drawbacks --- hard to dump,
impossible to secure, etc.

			regards, tom lane
== --------------------------------------------------
	 ';

-- =============================================
CREATE TABLE blobs.doc_desc (
	id serial primary key,
	doc_id integer
		references blobs.doc_med(id)
		on delete cascade
		on update cascade,
	"text" text,
	unique(doc_id, "text")
);

COMMENT ON TABLE blobs.doc_desc is
	'A textual description of the content such
	 as a result summary. Several of these may
	 belong to one document object.';

-- =============================================
-- do simple schema revision tracking
INSERT INTO public.gm_schema_revision (filename, version) VALUES('$RCSfile: gmBlobs.sql,v $', '$Revision: 1.55 $');

-- =============================================
-- questions:
--  - do we need doc_desc linkeable to doc_obj, too ?
--  IH: no, OCR etc. should span the multiple pages
--  - how do we protect documents from being accessed by unauthorized users ?
--    - on access search for the oid in gmCrypto tables for a matching key/PW hash record ??
--  - should (potentially large) binary objects be moved to audit tables ?!?
-- IH: no, doc_med should be audited, but not doc_obj. doc_obj rows never change anyway.

-- notes:
-- - as this uses BYTEA for storing binary data we have the following limitations
--   - needs postgres >= 7.1
--   - needs proper escaping of NUL, \ and ' (should go away once postgres 7.3 arrives)
--   - has a 1 GB limit for data objects
-- - we explicitely don't store MIME types etc. as selecting an appropriate viewer is a runtime issue
-- - it is helpful to structure text in doc_desc to be able to identify source/content etc.
-- =============================================
-- $Log: gmBlobs.sql,v $
-- Revision 1.55  2005-12-04 09:38:22  ncq
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
