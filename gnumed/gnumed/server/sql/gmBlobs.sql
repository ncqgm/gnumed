-- BLOB tables for GNUmed

-- license: GPL
-- author: Karsten Hilbert <Karsten.Hilbert@gmx.net>

-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmBlobs.sql,v $
-- $Revision: 1.43 $ $Date: 2004-10-10 06:34:12 $ $Author: ihaywood $

-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- =============================================
\unset ON_ERROR_STOP

create table xlnk_identity (
	pk serial primary key,
	xfk_identity integer unique not null,
	pupic text unique not null,
	data text unique default null
) inherits (audit_fields);

select add_x_db_fk_def('xlnk_identity', 'xfk_identity', 'personalia', 'identity', 'id');
select add_table_for_audit('xlnk_identity');

comment on table xlnk_identity is
	'this is the one table with the unresolved identity(id)
	 foreign key, all other tables in this service link to
	 this table, depending upon circumstances one can add
	 dblink() verification or a true FK constraint (if "personalia"
	 is in the same database as "historica")';

\set ON_ERROR_STOP 1
-- =============================================
CREATE TABLE doc_type (
	id serial primary key,
	name text unique
);

CREATE TABLE queues (
	pk serial primary key,
	name text
);

COMMENT ON TABLE queues IS
'the various states a document can be in as it traverses the GNUMed system, 
this allows SQL views of document "queues" for faxing, emailing, doctor''s inboxes, etc.';

-- =============================================
CREATE TABLE doc_med (
	id serial primary key,
	patient_id integer references xlnk_identity(xfk_identity) not null,
	local_id integer references xlnk_identity(xfk_identity),
	remote_id integer references xlnk_identity(xfk_identity),
	fk_queue integer references queues (pk),
	type integer references doc_type(id),
	comment text,
	fk_form_template integer, -- references gmReference.form_template (pk),
	"date" timestamp with time zone default CURRENT_TIMESTAMP,
	ext_ref text,
	has_measure boolean,
	fk_reviewer integer
		default null
		references xlnk_identity(xfk_identity)
);

COMMENT ON TABLE doc_med IS
	'a medical document object possibly containing several
	 data objects such as several pages of a paper document';
COMMENT ON COLUMN doc_med.patient_id IS
	'the patient this document belongs to';
COMMENT ON COLUMN doc_med.type IS
	'semantic type of document (not type of file or mime
	 type), such as >referral letter<, >discharge summary<, etc.';
COMMENT ON COLUMN doc_med.comment IS
	'additional short comment such as "abdominal", "ward 3,
	 Dr. Stein", etc.';
COMMENT ON COLUMN doc_med.remote_id IS
	'the remote entity (the sender for incoming documents, the recipient for outgoing documents)';
COMMENT ON COLUMN doc_med.local_id IS
	'the local entity (the receiver for incoming documents, the sender for outgoing documents)';
COMMENT ON COLUMN doc_med.fk_form_template IS
	'the form template, where this document is a GNUMed form, 
	doc_obj stores the fields, doc_obj.comment is the 
	field name';
COMMENT ON COLUMN doc_med.date IS
	'date of document content creation (such as exam date),
	 NOT date of document creation or date of import; may
	 be imprecise such as "7/99"';
COMMENT ON COLUMN doc_med.ext_ref IS
	'external reference string of physical document,
	 original paper copy can be found with this';
COMMENT ON COLUMN doc_med.has_measure IS 'true if
measurement data (see gmMeasurement.sql) has been generated from this document';

-- =============================================
CREATE TABLE doc_obj (
	id serial primary key,
	doc_id integer references doc_med(id),
	seq_idx integer,
	comment text,
	mime text,
	data bytea
);

COMMENT ON TABLE doc_obj IS
	'possibly several of these form a medical document
	 such as multiple scanned pages/images';
COMMENT ON COLUMN doc_obj.seq_idx IS
	'index of this object in the sequence
	 of objects for this document';
COMMENT ON COLUMN doc_obj.comment IS
	'optional tiny comment for this
	 object, such as "page 1"';
COMMENT ON COLUMN doc_obj.data IS
	'actual binary object data';
COMMENT ON COLUMN doc_obj.mime IS
	'the MIME type of the object. Auto-detection of document types is cool,
but falliable: encrypted PGP data looks a lot like plain text, for example';

-- =============================================
CREATE TABLE doc_desc (
	id serial primary key,
	doc_id integer
		references doc_med(id)
		on delete cascade
		on update cascade,
	"text" text,
	unique(doc_id, "text")
);

COMMENT ON TABLE doc_desc is
	'A textual description of the content such
	 as a result summary. Several of these may
	 belong to one document object.';

-- =============================================
-- do simple schema revision tracking
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmBlobs.sql,v $', '$Revision: 1.43 $');

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
-- Revision 1.43  2004-10-10 06:34:12  ihaywood
-- Extended blobs to support basic document management:
-- keeping track of whose reviewed what, etc.
--
-- This duplicates the same functionality for path. results:
-- how can we integrate?
-- CVS ----------------------------------------------------------------------
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
