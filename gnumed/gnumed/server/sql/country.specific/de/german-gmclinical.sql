-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/country.specific/de/Attic/german-gmclinical.sql,v $
-- $Revision: 1.7 $

-- part of GnuMed
-- GPL
-- author: Karsten Hilbert <Karsten.Hilbert@gmx.net>

-- various clinical enumerations translated into German
-- run this _after_ gmclinical.sql !
-- =============================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

set client_encoding to 'LATIN1';
-- =============================================
-- confidentiality levels
insert into i18n_translations(lang, orig, trans) values
	('de_DE', 'public', 'öffentlich');
insert into i18n_translations(lang, orig, trans) values
	('de_DE', 'relatives', 'Angehörige');
insert into i18n_translations(lang, orig, trans) values
	('de_DE', 'receptionist', 'Personal');
insert into i18n_translations(lang, orig, trans) values
	('de_DE', 'clinical staff', 'klinisches Personal');
insert into i18n_translations(lang, orig, trans) values
	('de_DE', 'doctors', 'Ärzte');
insert into i18n_translations(lang, orig, trans) values
	('de_DE', 'doctors of practice only', 'Ärzte dieser Einrichtung');
insert into i18n_translations(lang, orig, trans) values
	('de_DE', 'treating doctor', 'behandelnder Arzt');

-- =============================================
-- encounter types
insert into i18n_translations(lang, orig, trans) values
	('de_DE', 'in surgery', 'in Praxis');
insert into i18n_translations(lang, orig, trans) values
	('de_DE', 'phone consultation', 'Anruf');
insert into i18n_translations(lang, orig, trans) values
	('de_DE', 'fax consultation', 'per Fax');
insert into i18n_translations(lang, orig, trans) values
	('de_DE', 'home visit', 'Hausbesuch');
insert into i18n_translations(lang, orig, trans) values
	('de_DE', 'nursing home visit', 'Heimbesuch');
insert into i18n_translations(lang, orig, trans) values
	('de_DE', 'repeat script', 'Wiederholungsrezept');
insert into i18n_translations(lang, orig, trans) values
	('de_DE', 'hospital visit', 'Krankenhausbesuch');
insert into i18n_translations(lang, orig, trans) values
	('de_DE', 'video conference', 'per Video');
insert into i18n_translations(lang, orig, trans) values
	('de_DE', 'proxy encounter', 'indirekt');
insert into i18n_translations(lang, orig, trans) values
	('de_DE', 'emergency encounter', 'Notfall');
insert into i18n_translations(lang, orig, trans) values
	('de_DE', 'other encounter', 'anderer Kontakt'); -- such as at the mall :-))

-- =============================================
-- patient history types
insert into i18n_translations(lang, orig, trans) values
	('de_DE', 'presenting complaint', 'jetzige Beschwerden');
insert into i18n_translations(lang, orig, trans) values
	('de_DE', 'history of present illness', 'Jetzt-Anamnese');
insert into i18n_translations(lang, orig, trans) values
	('de_DE', 'past', '? Eigenanamnese');
insert into i18n_translations(lang, orig, trans) values
	('de_DE', 'social', 'Sozialanamnese');
insert into i18n_translations(lang, orig, trans) values
	('de_DE', 'family', 'Familienanamnese');
insert into i18n_translations(lang, orig, trans) values
	('de_DE', 'immunisation', 'Impfungen');
insert into i18n_translations(lang, orig, trans) values
	('de_DE', 'requests', '?? requests');
insert into i18n_translations(lang, orig, trans) values
	('de_DE', 'allergies', 'Allergien');
insert into i18n_translations(lang, orig, trans) values
	('de_DE', 'drug', 'Medikamentenanamnese');
insert into i18n_translations(lang, orig, trans) values
	('de_DE', 'sexual', 'Sexualanamnese');
insert into i18n_translations(lang, orig, trans) values
	('de_DE', 'psychiatric', 'psychiatrische Anamnese');
insert into i18n_translations(lang, orig, trans) values
	('de_DE', 'other', 'sonstige Anamnese');

-- =============================================
-- patient history providers
insert into i18n_translations(lang, orig, trans) values
	('de_DE', 'patient', 'Patient');
insert into i18n_translations(lang, orig, trans) values
	('de_DE', 'clinician', 'Mediziner');
insert into i18n_translations(lang, orig, trans) values
	('de_DE', 'relative', 'Angehörige');
insert into i18n_translations(lang, orig, trans) values
	('de_DE', 'carer', 'Pflegeperson');
insert into i18n_translations(lang, orig, trans) values
	('de_DE', 'notes', 'Unterlagen');
insert into i18n_translations(lang, orig, trans) values
	('de_DE', 'correspondence', 'Korrespondenz');

-- =============================================
-- allergy types
insert into i18n_translations(lang, orig, trans) values
	('de_DE', 'allergy', 'Allergie');
insert into i18n_translations(lang, orig, trans) values
	('de_DE', 'sensitivity', 'Unverträglichkeit');

-- =============================================
-- description
--insert into i18n_translations(lang, orig, trans) values
--	('de_DE', '', '');
--insert into i18n_translations(lang, orig, trans) values
--	('de_DE', '', '');
--insert into i18n_translations(lang, orig, trans) values
--	('de_DE', '', '');
--insert into i18n_translations(lang, orig, trans) values
--	('de_DE', '', '');
--insert into i18n_translations(lang, orig, trans) values
--	('de_DE', '', '');

-- =============================================
-- do simple revision tracking
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: german-gmclinical.sql,v $', '$Revision: 1.7 $');

-- =============================================
-- $Log: german-gmclinical.sql,v $
-- Revision 1.7  2003-06-11 14:03:12  ncq
-- - set encoding
--
-- Revision 1.6  2003/05/12 12:43:40  ncq
-- - gmI18N, gmServices and gmSchemaRevision are imported globally at the
--   database level now, don't include them in individual schema file anymore
--
-- Revision 1.5  2003/04/28 20:56:16  ncq
-- - unclash "allergy" in hx type and type of allergic reaction + translations
-- - some useful indices
--
-- Revision 1.4  2003/04/25 12:02:04  ncq
-- - better translation of encounter types
--
-- Revision 1.3  2003/02/09 10:13:25  hinnef
-- set correct path to gmI18N and gmSchemaRevision
--
-- Revision 1.2  2003/01/27 08:50:41  ncq
-- - drug history -> Medikamentenanamnese
--
-- Revision 1.1  2003/01/27 01:36:12  ncq
-- - script consolidation
--
