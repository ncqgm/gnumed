-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/country.specific/de/Attic/german-doc_types.sql,v $
-- $Revision: 1.7 $

-- part of GnuMed
-- GPL

-- doc types translated into German
-- run this _after_ gmBlobs.sql !
-- ===================================================================
-- do fixed string i18n()ing
\i gmI18N.sql

-- =============================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- =============================================
INSERT INTO i18n_translations(lang, orig, trans) values('de_DE', 'discharge summary internal', 'Entlassung Interne');
INSERT INTO i18n_translations(lang, orig, trans) values('de_DE', 'discharge summary surgical', 'Entlassung Chirurgie');
INSERT INTO i18n_translations(lang, orig, trans) values('de_DE', 'discharge summary psychiatric', 'Entlassung Psychiatrie');
INSERT INTO i18n_translations(lang, orig, trans) values('de_DE', 'discharge summary neurological', 'Entlassung Neuro');
INSERT INTO i18n_translations(lang, orig, trans) values('de_DE', 'discharge summary orthopaedic', 'Entlassung Ortho');
INSERT INTO i18n_translations(lang, orig, trans) values('de_DE', 'discharge summary other', 'Entlassung sonstige');
INSERT INTO i18n_translations(lang, orig, trans) values('de_DE', 'discharge summary rehabilitation', 'Entlassung Reha');

INSERT INTO i18n_translations(lang, orig, trans) values('de_DE', 'referral report internal', 'Arztbrief Innere');
INSERT INTO i18n_translations(lang, orig, trans) values('de_DE', 'referral report surgical', 'Arztbrief Chirurgie');
INSERT INTO i18n_translations(lang, orig, trans) values('de_DE', 'referral report ENT', 'Arztbrief HNO');
INSERT INTO i18n_translations(lang, orig, trans) values('de_DE', 'referral report eye', 'Arztbrief Augen');
INSERT INTO i18n_translations(lang, orig, trans) values('de_DE', 'referral report urology', 'Arztbrief Uro');
INSERT INTO i18n_translations(lang, orig, trans) values('de_DE', 'referral report orthopaedic', 'Arztbrief Ortho');
INSERT INTO i18n_translations(lang, orig, trans) values('de_DE', 'referral report neuro', 'Arztbrief Neuro');
INSERT INTO i18n_translations(lang, orig, trans) values('de_DE', 'referral report radiology', 'Arztbrief Röntgen');
INSERT INTO i18n_translations(lang, orig, trans) values('de_DE', 'referral report other', 'sonstiger Arztbrief');
INSERT INTO i18n_translations(lang, orig, trans) values('de_DE', 'referral report cardiology', 'Arztbrief Kardio');
INSERT INTO i18n_translations(lang, orig, trans) values('de_DE', 'referral report psychotherapy', 'Arztbrief Psychotherapie');
--INSERT into _doc_type(name) values('Arztbrief Umweltmedizin');
--INSERT into _doc_type(name) values('Arztbrief Mikrobiologie');
--INSERT into _doc_type(name) values('Labor');

-- do simple revision tracking
\i gmSchemaRevision.sql
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: german-doc_types.sql,v $', '$Revision: 1.7 $');

-- =============================================
-- $Log: german-doc_types.sql,v $
-- Revision 1.7  2003-01-20 20:05:41  ncq
-- - a few more doc types
--
-- Revision 1.6  2003/01/05 13:05:53  ncq
-- - schema_revision -> gm_schema_revision
--
-- Revision 1.5  2003/01/01 17:42:59  ncq
-- - changed for new i18n
--
-- Revision 1.4  2002/12/26 15:52:28  ncq
-- - add two types
--
-- Revision 1.3  2002/12/01 13:53:09  ncq
-- - missing ; at end of schema tracking line
--
-- Revision 1.2  2002/11/16 00:21:44  ncq
-- - add simplistic revision tracking
--
