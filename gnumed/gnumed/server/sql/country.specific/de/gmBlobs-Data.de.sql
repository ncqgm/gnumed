-- GnuMed
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/country.specific/de/Attic/gmBlobs-Data.de.sql,v $
-- $Revision: 1.2 $

-- license: GPL
-- author: Karsten Hilbert

-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

set client_encoding to 'LATIN1';
-- =============================================
-- doc types translated into German

-- if you want to insert your own document types follow these rules:
-- * user defined document types can only have IDs between 100 and 200
-- * insert your new type into doc_type:
-- insert into doc_type (pk, name) values (100, i18n('my doc type'));
--   (increase the id value to 101, 102, ... if you want to insert more types)
-- * insert your translation into i18n_translations:
-- insert into i18n_translations(lang, orig, trans) values('de_DE', 'my doc type', 'mein Dokumententyp');

-- Entlassungsbriefe/Epikrisen
INSERT INTO i18n_translations(lang, orig, trans) values
	('de_DE', 'discharge summary internal', 'Entlassung Interne');
INSERT INTO i18n_translations(lang, orig, trans) values
	('de_DE', 'discharge summary surgical', 'Entlassung Chirurgie');
INSERT INTO i18n_translations(lang, orig, trans) values
	('de_DE', 'discharge summary psychiatric', 'Entlassung Psychiatrie');
INSERT INTO i18n_translations(lang, orig, trans) values
	('de_DE', 'discharge summary neurological', 'Entlassung Neuro');
INSERT INTO i18n_translations(lang, orig, trans) values
	('de_DE', 'discharge summary orthopaedic', 'Entlassung Ortho');
INSERT INTO i18n_translations(lang, orig, trans) values
	('de_DE', 'discharge summary other', 'Entlassung sonstige');
INSERT INTO i18n_translations(lang, orig, trans) values
	('de_DE', 'discharge summary rehabilitation', 'Entlassung Reha');
INSERT INTO i18n_translations(lang, orig, trans) values
	('de_DE', 'discharge summary urology', 'Entlassung Uro');
INSERT INTO i18n_translations(lang, orig, trans) values
	('de_DE', 'discharge summary neurosurgery', 'Entlassung Neurochirurgie');
INSERT INTO i18n_translations(lang, orig, trans) values
	('de_DE', 'discharge summary ophthalmology', 'Entlassung Augen');
INSERT INTO i18n_translations(lang, orig, trans) values
	('de_DE', 'discharge summary ENT', 'Entlassung HNO');

-- Arztbriefe
INSERT INTO i18n_translations(lang, orig, trans) values
	('de_DE', 'referral report internal', 'Arztbrief Innere');
INSERT INTO i18n_translations(lang, orig, trans) values
	('de_DE', 'referral report surgical', 'Arztbrief Chirurgie');
INSERT INTO i18n_translations(lang, orig, trans) values
	('de_DE', 'referral report ENT', 'Arztbrief HNO');
INSERT INTO i18n_translations(lang, orig, trans) values
	('de_DE', 'referral report eye', 'Arztbrief Augen');
INSERT INTO i18n_translations(lang, orig, trans) values
	('de_DE', 'referral report urology', 'Arztbrief Uro');
INSERT INTO i18n_translations(lang, orig, trans) values
	('de_DE', 'referral report orthopaedic', 'Arztbrief Ortho');
INSERT INTO i18n_translations(lang, orig, trans) values
	('de_DE', 'referral report neuro', 'Arztbrief Neuro');
INSERT INTO i18n_translations(lang, orig, trans) values
	('de_DE', 'referral report radiology', 'Arztbrief Röntgen');
INSERT INTO i18n_translations(lang, orig, trans) values
	('de_DE', 'referral report other', 'sonstiger Arztbrief');
INSERT INTO i18n_translations(lang, orig, trans) values
	('de_DE', 'referral report cardiology', 'Arztbrief Kardio');
INSERT INTO i18n_translations(lang, orig, trans) values
	('de_DE', 'referral report psychotherapy', 'Arztbrief Psychotherapie');
INSERT INTO i18n_translations(lang, orig, trans) values
	('de_DE', 'referral report oncology', 'Arztbrief Onkologie');
INSERT INTO i18n_translations(lang, orig, trans) values
	('de_DE', 'referral report pathology', 'Arztbrief Patho');
INSERT INTO i18n_translations(lang, orig, trans) values
	('de_DE', 'referral report neurosurgery', 'Arztbrief Neurochirurgie');

--INSERT into _doc_type(name) values('Arztbrief Umweltmedizin');
--INSERT into _doc_type(name) values('Arztbrief Mikrobiologie');
--INSERT into _doc_type(name) values('Labor');

INSERT INTO i18n_translations(lang, orig, trans) values
	('de_DE', 'patient photograph', 'Patientenphoto');

-- =============================================
-- do simple revision tracking
delete from gm_schema_revision where filename='$RCSfile: gmBlobs-Data.de.sql,v $';
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmBlobs-Data.de.sql,v $', '$Revision: 1.2 $');

-- =============================================
-- $Log: gmBlobs-Data.de.sql,v $
-- Revision 1.2  2004-10-11 19:35:58  ncq
-- - translate "patient photograph"
--
-- Revision 1.1  2003/08/05 08:15:59  ncq
-- - cleanup/renaming
--
-- Revision 1.12  2003/07/20 09:39:04  ncq
-- - more translations
--
-- Revision 1.11  2003/06/11 14:03:44  ncq
-- - set encoding
--
-- Revision 1.10  2003/05/12 12:43:40  ncq
-- - gmI18N, gmServices and gmSchemaRevision are imported globally at the
--   database level now, don't include them in individual schema file anymore
--
-- Revision 1.9  2003/04/18 13:30:35  ncq
-- - add doc types
-- - update comment on allergy.id_substance
--
-- Revision 1.8  2003/01/26 16:04:37  ncq
-- - example of how to add your own types
--
-- Revision 1.7  2003/01/20 20:05:41  ncq
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
