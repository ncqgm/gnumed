-- BLOB tables for GNUmed

-- license: GPL
-- author: Karsten Hilbert <Karsten.Hilbert@gmx.net>

-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmBlobs.sql,v $
-- $Revision: 1.28 $ $Date: 2003-01-24 14:21:47 $ $Author: ncq $

-- ===================================================================
-- do fixed string i18n()ing
\i gmI18N.sql

-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- =============================================
CREATE TABLE "doc_type" (
	"id" serial primary key,
	"name" character varying(40) unique
);

INSERT into doc_type(name) values(i18n('discharge summary internal'));
INSERT into doc_type(name) values(i18n('discharge summary surgical'));
INSERT into doc_type(name) values(i18n('discharge summary psychiatric'));
INSERT into doc_type(name) values(i18n('discharge summary neurological'));
INSERT into doc_type(name) values(i18n('discharge summary orthopaedic'));
INSERT into doc_type(name) values(i18n('discharge summary other'));

INSERT into doc_type(name) values(i18n('referral report internal'));
INSERT into doc_type(name) values(i18n('referral report surgical'));
INSERT into doc_type(name) values(i18n('referral report ENT'));
INSERT into doc_type(name) values(i18n('referral report eye'));
INSERT into doc_type(name) values(i18n('referral report urology'));
INSERT into doc_type(name) values(i18n('referral report orthopaedic'));
INSERT into doc_type(name) values(i18n('referral report neuro'));
INSERT into doc_type(name) values(i18n('referral report radiology'));
INSERT into doc_type(name) values(i18n('referral report other'));
INSERT into doc_type(name) values(i18n('referral report cardiology'));
INSERT into doc_type(name) values(i18n('referral report psychotherapy'));

-- add any number of types here, this is just to give you an idea

-- =============================================
create view v_i18n_doc_type (id, name) as
	select
		doc_type.id,
		_(doc_type.name)
	from
		doc_type
	;

-- =============================================
CREATE TABLE "doc_med" (
	"id" serial primary key,
	"patient_id" integer references identity not null,
	"type" integer references doc_type(id) not null,
	"comment" character varying(60) not null,
	"date" timestamp with time zone,
	"ext_ref" character varying (40) not null
);

COMMENT ON TABLE "doc_med" IS
	'a medical document object possibly containing several data objects such as several pages of a paper document';
-- FIXME: this needs to be able to reference external databases
COMMENT ON COLUMN doc_med.patient_id IS
	'the patient this document belongs to';
COMMENT ON COLUMN doc_med.type IS
	'semantic type of document (not type of file or mime type), such as >referral letter<, >discharge summary<, etc.';
COMMENT ON COLUMN doc_med.comment IS
	'additional short comment such as "abdominal", "ward 3, Dr. Stein", etc.';
COMMENT ON COLUMN doc_med.date IS
	'date of document content creation (such as exam date), NOT date of document creation or date of import; may be imprecise such as "7/99"';
COMMENT ON COLUMN doc_med.ext_ref IS
	'external reference string of physical document, original paper copy can be found with this';

-- =============================================
CREATE TABLE "doc_med_external_ref" (
	doc_id int references doc_med(id),
	refcounter int default 0
);

-- =============================================
CREATE TABLE "doc_obj" (
	"doc_id" integer references doc_med(id),
	"seq_idx" integer,
	"comment" character varying(30),
	"data" bytea
);

COMMENT ON TABLE "doc_obj" IS 'possibly several of these form a medical document such as multiple scanned pages/images';
COMMENT ON COLUMN doc_obj.seq_idx IS 'index of this object in the sequence of objects for this document';
COMMENT ON COLUMN doc_obj.comment IS 'optional tiny comment for this object, such as "page 1"';
COMMENT ON COLUMN doc_obj.data IS 'actual binary object data';

-- =============================================
CREATE TABLE "doc_desc" (
	"doc_id" integer references doc_med(id),
	"text" text
);

COMMENT ON TABLE "doc_desc" is 'A textual description of the content such as a result summary. Several of these may belong to one document object.';

-- =============================================
GRANT SELECT ON
	"doc_desc",
	"doc_obj",
	"doc_med",
	"doc_type",
	"v_i18n_doc_type",
	"doc_med_external_ref"
TO GROUP "gm-doctors";

GRANT SELECT, INSERT, UPDATE, DELETE ON
	"doc_desc",
	"doc_obj",
	"doc_med",
	"doc_med_id_seq",
	"doc_type",
	"doc_med_external_ref"
TO GROUP "_gm-doctors";

-- =============================================
-- do simple schema revision tracking
\i gmSchemaRevision.sql
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmBlobs.sql,v $', '$Revision: 1.28 $');

-- =============================================
-- questions:
--  - do we need doc_desc linkeable to doc_obj, too ?
--  - how do we protect documents from being accessed by unauthorized users ?
--    - on access search for the oid in gmCrypto tables for a matching key/PW hash record ??
--  - should (potentially large) binary objects be moved to audit tables ?!?

-- notes:
-- - as this uses BYTEA for storing binary data we have the following limitations
--   - needs postgres >= 7.1
--   - needs proper escaping of NUL, \ and ' (should go away once postgres 7.3 arrives)
--   - has a 1 GB limit for data objects
-- - we explicitely don't store MIME types etc. as selecting an appropriate viewer is a runtime issue
-- - it is helpful to structure text in doc_desc to be able to identify source/content etc.
