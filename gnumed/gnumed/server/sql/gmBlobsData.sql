-- BLOB table data for GnuMed

-- license: GPL
-- author: Karsten Hilbert <Karsten.Hilbert@gmx.net>

-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmBlobsData.sql,v $
-- $Revision: 1.13 $ $Date: 2005-11-11 23:04:40 $ $Author: ncq $

-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- =============================================
INSERT into blobs.doc_type(name, is_user) values(public.i18n('discharge summary internal'), false);
INSERT into blobs.doc_type(name, is_user) values(public.i18n('discharge summary surgical'), false);
INSERT into blobs.doc_type(name, is_user) values(public.i18n('discharge summary psychiatric'), false);
INSERT into blobs.doc_type(name, is_user) values(public.i18n('discharge summary neurological'), false);
INSERT into blobs.doc_type(name, is_user) values(public.i18n('discharge summary orthopaedic'), false);
INSERT into blobs.doc_type(name, is_user) values(public.i18n('discharge summary other'), false);
INSERT into blobs.doc_type(name, is_user) values(public.i18n('discharge summary rehabilitation'), false);
INSERT into blobs.doc_type(name, is_user) values(public.i18n('referral report internal'), false);
INSERT into blobs.doc_type(name, is_user) values(public.i18n('referral report surgical'), false);
INSERT into blobs.doc_type(name, is_user) values(public.i18n('referral report ENT'), false);
INSERT into blobs.doc_type(name, is_user) values(public.i18n('referral report eye'), false);
INSERT into blobs.doc_type(name, is_user) values(public.i18n('referral report urology'), false);
INSERT into blobs.doc_type(name, is_user) values(public.i18n('referral report orthopaedic'), false);
INSERT into blobs.doc_type(name, is_user) values(public.i18n('referral report neuro'), false);
INSERT into blobs.doc_type(name, is_user) values(public.i18n('referral report radiology'), false);
INSERT into blobs.doc_type(name, is_user) values(public.i18n('referral report other'), false);
INSERT into blobs.doc_type(name, is_user) values(public.i18n('referral report cardiology'), false);
INSERT into blobs.doc_type(name, is_user) values(public.i18n('referral report psychotherapy'), false);
INSERT into blobs.doc_type(name, is_user) values(public.i18n('discharge summary urology'), false);
INSERT into blobs.doc_type(name, is_user) values(public.i18n('referral report oncology'), false);
INSERT into blobs.doc_type(name, is_user) values(public.i18n('discharge summary neurosurgery'), false);
INSERT into blobs.doc_type(name, is_user) values(public.i18n('discharge summary ophthalmology'), false);
INSERT into blobs.doc_type(name, is_user) values(public.i18n('discharge summary ENT'), false);
INSERT into blobs.doc_type(name, is_user) values(public.i18n('referral report pathology'), false);
INSERT into blobs.doc_type(name, is_user) values(public.i18n('referral report neurosurgery'), false);
INSERT into blobs.doc_type(name, is_user) values(public.i18n('patient photograph'), false);
--INSERT into blobs.doc_type(name, is_user) values(public.i18n(''), false);

-- !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
-- your own doc types must set is_user to true or else
-- they may get overwritten during database upgrades
-- !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

-- =============================================
-- do simple schema revision tracking
INSERT INTO public.gm_schema_revision (filename, version) VALUES('$RCSfile: gmBlobsData.sql,v $', '$Revision: 1.13 $');

-- =============================================
-- $Log: gmBlobsData.sql,v $
-- Revision 1.13  2005-11-11 23:04:40  ncq
-- - doc_type now has is_user
--
-- Revision 1.12  2005/10/24 19:09:43  ncq
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
