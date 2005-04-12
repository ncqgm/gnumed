-- =============================================
-- GNUmed German translations

-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/country.specific/de/gmUebersetzung.sql,v $
-- $Revision: 1.2 $

-- license: GPL
-- author (of script file): Karsten Hilbert <Karsten.Hilbert@gmx.net>

-- =============================================
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
-- select i18n_upd_tx('de_DE', 'my doc type', 'mein Dokumententyp');

-- Entlassungsbriefe/Epikrisen
select i18n_upd_tx('de_DE', 'discharge summary internal', 'Entlassung Interne');
select i18n_upd_tx('de_DE', 'discharge summary surgical', 'Entlassung Chirurgie');
select i18n_upd_tx
	('de_DE', 'discharge summary psychiatric', 'Entlassung Psychiatrie');
select i18n_upd_tx
	('de_DE', 'discharge summary neurological', 'Entlassung Neuro');
select i18n_upd_tx
	('de_DE', 'discharge summary orthopaedic', 'Entlassung Ortho');
select i18n_upd_tx
	('de_DE', 'discharge summary other', 'Entlassung sonstige');
select i18n_upd_tx
	('de_DE', 'discharge summary rehabilitation', 'Entlassung Reha');
select i18n_upd_tx
	('de_DE', 'discharge summary urology', 'Entlassung Uro');
select i18n_upd_tx
	('de_DE', 'discharge summary neurosurgery', 'Entlassung Neurochirurgie');
select i18n_upd_tx
	('de_DE', 'discharge summary ophthalmology', 'Entlassung Augen');
select i18n_upd_tx
	('de_DE', 'discharge summary ENT', 'Entlassung HNO');

-- Arztbriefe
select i18n_upd_tx
	('de_DE', 'referral report internal', 'Arztbrief Innere');
select i18n_upd_tx
	('de_DE', 'referral report surgical', 'Arztbrief Chirurgie');
select i18n_upd_tx
	('de_DE', 'referral report ENT', 'Arztbrief HNO');
select i18n_upd_tx
	('de_DE', 'referral report eye', 'Arztbrief Augen');
select i18n_upd_tx
	('de_DE', 'referral report urology', 'Arztbrief Uro');
select i18n_upd_tx
	('de_DE', 'referral report orthopaedic', 'Arztbrief Ortho');
select i18n_upd_tx
	('de_DE', 'referral report neuro', 'Arztbrief Neuro');
select i18n_upd_tx
	('de_DE', 'referral report radiology', 'Arztbrief Röntgen');
select i18n_upd_tx
	('de_DE', 'referral report other', 'sonstiger Arztbrief');
select i18n_upd_tx
	('de_DE', 'referral report cardiology', 'Arztbrief Kardio');
select i18n_upd_tx
	('de_DE', 'referral report psychotherapy', 'Arztbrief Psychotherapie');
select i18n_upd_tx
	('de_DE', 'referral report oncology', 'Arztbrief Onkologie');
select i18n_upd_tx
	('de_DE', 'referral report pathology', 'Arztbrief Patho');
select i18n_upd_tx
	('de_DE', 'referral report neurosurgery', 'Arztbrief Neurochirurgie');

--INSERT into _doc_type(name) values('Arztbrief Umweltmedizin');
--INSERT into _doc_type(name) values('Arztbrief Mikrobiologie');
--INSERT into _doc_type(name) values('Labor');

select i18n_upd_tx
	('de_DE', 'patient photograph', 'Patientenphoto');

-- =============================================
-- confidentiality levels
select i18n_upd_tx ('de_DE', 'public', 'öffentlich');
select i18n_upd_tx ('de_DE', 'relatives', 'Angehörige');
select i18n_upd_tx ('de_DE', 'receptionist', 'Personal');
select i18n_upd_tx ('de_DE', 'clinical staff', 'klinisches Personal');
select i18n_upd_tx ('de_DE', 'doctors', 'Ärzte');
select i18n_upd_tx ('de_DE', 'doctors of practice only', 'Ärzte dieser Einrichtung');
select i18n_upd_tx ('de_DE', 'treating doctor', 'behandelnder Arzt');

-- =============================================
-- encounter types
select i18n_upd_tx('de_DE', 'in surgery', 'in Praxis');
select i18n_upd_tx('de_DE', 'phone consultation', 'Anruf');
select i18n_upd_tx('de_DE', 'fax consultation', 'per Fax');
select i18n_upd_tx('de_DE', 'home visit', 'Hausbesuch');
select i18n_upd_tx('de_DE', 'nursing home visit', 'Heimbesuch');
select i18n_upd_tx('de_DE', 'repeat script', 'Wiederholungsrezept');
select i18n_upd_tx('de_DE', 'hospital visit', 'Krankenhausbesuch');
select i18n_upd_tx('de_DE', 'video conference', 'per Video');
select i18n_upd_tx('de_DE', 'proxy encounter', 'indirekt');
select i18n_upd_tx('de_DE', 'emergency encounter', 'Notfall');
select i18n_upd_tx('de_DE', 'chart review', 'Akteneinsicht');
-- such as at the mall :-))
select i18n_upd_tx('de_DE', 'other encounter', 'anderer Kontakt');

-- =============================================
-- patient history types
--select i18n_upd_tx
--	('de_DE', 'presenting complaint', 'jetzige Beschwerden');
--select i18n_upd_tx
--	('de_DE', 'history of present illness', 'Jetzt-Anamnese');
--select i18n_upd_tx
--	('de_DE', 'past', '? Eigenanamnese');
--select i18n_upd_tx
--	('de_DE', 'social', 'Sozialanamnese');
--select i18n_upd_tx
--	('de_DE', 'family', 'Familienanamnese');
--select i18n_upd_tx
--	('de_DE', 'immunisation', 'Impfungen');
--select i18n_upd_tx
--	('de_DE', 'requests', '?? requests');
--select i18n_upd_tx
--	('de_DE', 'allergies', 'Allergien');
--select i18n_upd_tx
--	('de_DE', 'drug', 'Medikamentenanamnese');
--select i18n_upd_tx
--	('de_DE', 'sexual', 'Sexualanamnese');
--select i18n_upd_tx
--	('de_DE', 'psychiatric', 'psychiatrische Anamnese');
--select i18n_upd_tx
--	('de_DE', 'other', 'sonstige Anamnese');

-- =============================================
-- patient history providers
--select i18n_upd_tx
--	('de_DE', 'patient', 'Patient');
--select i18n_upd_tx
--	('de_DE', 'clinician', 'Mediziner');
--select i18n_upd_tx
--	('de_DE', 'relative', 'Angehörige');
--select i18n_upd_tx
--	('de_DE', 'carer', 'Pflegeperson');
--select i18n_upd_tx
--	('de_DE', 'notes', 'Unterlagen');
--select i18n_upd_tx
--	('de_DE', 'correspondence', 'Korrespondenz');

-- =============================================
-- allergy types
select i18n_upd_tx('de_DE', 'allergy', 'Allergie');
select i18n_upd_tx('de_DE', 'sensitivity', 'Unverträglichkeit');

-- =============================================
-- vaccination routes
select i18n_upd_tx('de_DE', 'intramuscular', 'intramuskulär');
select i18n_upd_tx('de_DE', 'subcutaneous', 'subkutan');

-- =============================================
-- Impfindikationen
select i18n_upd_tx 
	('de_DE', 'measles', 'Masern');
select i18n_upd_tx
	('de_DE', 'mumps', 'Mumps');
select i18n_upd_tx 
	('de_DE', 'rubella', 'Röteln');
select i18n_upd_tx 
	('de_DE', 'tetanus', 'Tetanus');
select i18n_upd_tx 
	('de_DE', 'diphtheria', 'Diphtherie');
select i18n_upd_tx
	('de_DE', 'pertussis', 'Pertussis');
select i18n_upd_tx
	('de_DE', 'haemophilus influenzae b', 'Haemophilus Influenzae B');
select i18n_upd_tx
	('de_DE', 'hepatitis B', 'Hepatitis B');
select i18n_upd_tx
	('de_DE', 'poliomyelitis', 'Poliomyelitis');
select i18n_upd_tx
	('de_DE', 'influenza', 'Influenza');
select i18n_upd_tx
	('de_DE', 'hepatitis A', 'Hepatitis A');
select i18n_upd_tx
	('de_DE', 'pneumococcus', 'Pneumokokken');
select i18n_upd_tx
	('de_DE', 'meningococcus C', 'Meningokokken Typ C');
select i18n_upd_tx
	('de_DE', 'tick-borne meningoencephalitis', 'FSME');

-- =============================================
-- Status Laborergebnis
select i18n_upd_tx ('de_DE', 'pending', 'ausstehend');
select i18n_upd_tx ('de_DE', 'final', 'endgültig');
select i18n_upd_tx ('de_DE', 'preliminary', 'vorläufig');
select i18n_upd_tx ('de_DE', 'partial', 'unvollständig');

-- =============================================
-- names of interpersonal relations translated into German
select i18n_upd_tx('de_DE', 'parent', 'Elternteil');
select i18n_upd_tx('de_DE', 'sibling', 'Geschwister');
select i18n_upd_tx('de_DE', 'halfsibling', 'Stiefgeschwister');
select i18n_upd_tx('de_DE', 'stepparent', 'Stiefelter');
select i18n_upd_tx('de_DE', 'married', 'verheiratet');
select i18n_upd_tx('de_DE', 'de facto', 'de facto');
select i18n_upd_tx('de_DE', 'divorced', 'geschieden');
select i18n_upd_tx('de_DE', 'separated', 'getrennt');
select i18n_upd_tx('de_DE', 'legal guardian', 'Vormund');

-- =============================================
-- unordered translations
select i18n_upd_tx('de_DE', 'child', 'Kind');
select i18n_upd_tx('de_DE', 'stepchild', 'Stiefkind');
select i18n_upd_tx('de_DE', 'ward', 'Betreuer');

select i18n_upd_tx('de_DE', 'single', 'single');
select i18n_upd_tx('de_DE', 'widowed', 'verwitwet');
select i18n_upd_tx('de_DE', 'home', 'daheim');
select i18n_upd_tx('de_DE', 'work', 'Arbeit');
select i18n_upd_tx('de_DE', 'parents', 'Eltern');
select i18n_upd_tx('de_DE', 'holidays', 'Urlaub');
select i18n_upd_tx('de_DE', 'temporary', 'zeitweilig');
select i18n_upd_tx('de_DE', 'email', 'e-mail');
select i18n_upd_tx('de_DE', 'fax', 'Fax');
select i18n_upd_tx('de_DE', 'homephone', 'Telefon zu Hause');
select i18n_upd_tx('de_DE', 'workphone', 'Telefon auf Arbeit');
select i18n_upd_tx('de_DE', 'mobile', 'Funktelefon');
select i18n_upd_tx('de_DE', 'web', 'WWW');
select i18n_upd_tx('de_DE', 'jabber', 'Jabber');

select i18n_upd_tx('de_DE', 'health issue', 'Grunderkrankung');
select i18n_upd_tx('de_DE', 'episode', 'Episode');
select i18n_upd_tx('de_DE', 'encounter', 'APK');
select i18n_upd_tx('de_DE', 'vaccine', 'Impfstoff');
select i18n_upd_tx('de_DE', 'batch no', 'Charge');
select i18n_upd_tx('de_DE', 'indication', 'Indikation');
select i18n_upd_tx('de_DE', 'site', 'Ort');
select i18n_upd_tx('de_DE', 'notes', 'Bemerkung');
select i18n_upd_tx('de_DE', 'allergene', 'Allergen');
select i18n_upd_tx('de_DE', 'substance', 'Substanz');
select i18n_upd_tx('de_DE', 'generic', 'Generikum');
select i18n_upd_tx('de_DE', 'ATC code', 'ATC-Code');
select i18n_upd_tx('de_DE', 'type', 'Typ');
select i18n_upd_tx('de_DE', 'reaction', 'Reaktion');
select i18n_upd_tx('de_DE', 'lab', 'Labor');
select i18n_upd_tx('de_DE', 'sample ID', 'Probennummer');
select i18n_upd_tx('de_DE', 'sample taken', 'Probe genommen');
select i18n_upd_tx('de_DE', 'status', 'Status');
select i18n_upd_tx('de_DE', 'code', 'Code');
select i18n_upd_tx('de_DE', 'name', 'Name');
select i18n_upd_tx('de_DE', 'value', 'Wert');

-- =============================================
-- do simple revision tracking
delete from gm_schema_revision where filename = '$RCSfile: gmUebersetzung.sql,v $';
INSERT INTO gm_schema_revision (filename, version) VALUES ('$RCSfile: gmUebersetzung.sql,v $', '$Revision: 1.2 $');

-- =============================================
-- $Log: gmUebersetzung.sql,v $
-- Revision 1.2  2005-04-12 10:08:57  ncq
-- - add some translations
--
-- Revision 1.1  2005/03/31 19:15:41  ncq
-- - consolidate translations
--
