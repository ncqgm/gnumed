-- BLOB table data for GnuMed

-- license: GPL
-- author: Karsten Hilbert <Karsten.Hilbert@gmx.net>

-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmBlobsData.sql,v $
-- $Revision: 1.12 $ $Date: 2005-10-24 19:09:43 $ $Author: ncq $

-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- =============================================
INSERT into blobs.doc_type(pk, name) values(1, public.i18n('discharge summary internal'));
INSERT into blobs.doc_type(pk, name) values(2, public.i18n('discharge summary surgical'));
INSERT into blobs.doc_type(pk, name) values(3, public.i18n('discharge summary psychiatric'));
INSERT into blobs.doc_type(pk, name) values(4, public.i18n('discharge summary neurological'));
INSERT into blobs.doc_type(pk, name) values(5, public.i18n('discharge summary orthopaedic'));
INSERT into blobs.doc_type(pk, name) values(6, public.i18n('discharge summary other'));
INSERT into blobs.doc_type(pk, name) values(7, public.i18n('discharge summary rehabilitation'));
INSERT into blobs.doc_type(pk, name) values(8, public.i18n('referral report internal'));
INSERT into blobs.doc_type(pk, name) values(9, public.i18n('referral report surgical'));
INSERT into blobs.doc_type(pk, name) values(10, public.i18n('referral report ENT'));
INSERT into blobs.doc_type(pk, name) values(11, public.i18n('referral report eye'));
INSERT into blobs.doc_type(pk, name) values(12, public.i18n('referral report urology'));
INSERT into blobs.doc_type(pk, name) values(13, public.i18n('referral report orthopaedic'));
INSERT into blobs.doc_type(pk, name) values(14, public.i18n('referral report neuro'));
INSERT into blobs.doc_type(pk, name) values(15, public.i18n('referral report radiology'));
INSERT into blobs.doc_type(pk, name) values(16, public.i18n('referral report other'));
INSERT into blobs.doc_type(pk, name) values(17, public.i18n('referral report cardiology'));
INSERT into blobs.doc_type(pk, name) values(18, public.i18n('referral report psychotherapy'));
INSERT into blobs.doc_type(pk, name) values(19, public.i18n('discharge summary urology'));
INSERT into blobs.doc_type(pk, name) values(20, public.i18n('referral report oncology'));
INSERT into blobs.doc_type(pk, name) values(21, public.i18n('discharge summary neurosurgery'));
INSERT into blobs.doc_type(pk, name) values(22, public.i18n('discharge summary ophthalmology'));
INSERT into blobs.doc_type(pk, name) values(23, public.i18n('discharge summary ENT'));
INSERT into blobs.doc_type(pk, name) values(24, public.i18n('referral report pathology'));
INSERT into blobs.doc_type(pk, name) values(25, public.i18n('referral report neurosurgery'));
INSERT into blobs.doc_type(pk, name) values(26, public.i18n('patient photograph'));
--INSERT into blobs.doc_type(pk, name) values(, public.i18n(''));

-- !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
-- your own doc types can only have ids between 100 and 200
-- !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

-- =============================================
-- do simple schema revision tracking
INSERT INTO public.gm_schema_revision (filename, version) VALUES('$RCSfile: gmBlobsData.sql,v $', '$Revision: 1.12 $');

-- =============================================
-- $Log: gmBlobsData.sql,v $
-- Revision 1.12  2005-10-24 19:09:43  ncq
-- - explicit "blobs." qualifying
--
-- Revision 1.11  2005/09/19 16:38:51  ncq
-- - adjust to removed is_core from gm_schema_revision
--
-- Revision 1.10  2005/07/14 21:31:42  ncq
-- - partially use improved schema revision tracking
--
-- Revision 1.9  2004/10/11 19:02:31  ncq
-- - go back to before changes that need more discussion
--
-- Revision 1.6  2004/03/04 19:41:52  ncq
-- - whitespace, comment
--
-- Revision 1.5  2004/03/02 23:59:11  ihaywood
-- New document type 26: patient photograph
--
-- Revision 1.4  2003/07/20 09:39:25  ncq
-- - added some doc types
--
-- Revision 1.3  2003/05/12 12:43:39  ncq
-- - gmI18N, gmServices and gmSchemaRevision are imported globally at the
--   database level now, don't include them in individual schema file anymore
--
-- Revision 1.2  2003/04/18 13:30:35  ncq
-- - add doc types
-- - update comment on allergy.id_substance
--
-- Revision 1.1  2003/04/07 11:09:54  ncq
-- - separated out data inserts from schema definition
--
