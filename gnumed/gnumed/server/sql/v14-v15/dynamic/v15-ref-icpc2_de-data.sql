-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;


-- --------------------------------------------------------------
-- translations

-- chapters
select i18n.upd_tx('de', 'General and Unspecified', 'Allgmein und unspezifisch');
select i18n.upd_tx('de', 'Blood, Blood forming organs, Immune mechanism', 'Blut, blutbildende Organe, Immunsystem');
select i18n.upd_tx('de', 'Digestive', 'Darm: Verdauungssystem');
select i18n.upd_tx('de', 'Eye ("Focal")', 'Fokus: Auge');
select i18n.upd_tx('de', 'Ear ("Hearing")', 'Hören: Ohr');
select i18n.upd_tx('de', 'Cardivascular', 'Kreislauf');
select i18n.upd_tx('de', 'Musculoskeletal ("Locomotion")', 'Laufen: Bewegungsapparat');
select i18n.upd_tx('de', 'Neurological', 'Neurologisch');
select i18n.upd_tx('de', 'Psychological', 'Psychologisch');
select i18n.upd_tx('de', 'Respiratory', 'Respiratorisch: Atmungsorgane');
select i18n.upd_tx('de', 'Skin', 'Skin: Haut');
select i18n.upd_tx('de', 'Endocrine/Metabolic and Nutritional ("Thyroid")', 'Thyroidea: Endokrin, metabolisch, Ernährung');
select i18n.upd_tx('de', 'Urological', 'Urologisch');
select i18n.upd_tx('de', 'Pregnancy, Childbearing, Family planning ("Women")', 'Weiblich: Schwangerschaft, Geburt, Familienplanung');
select i18n.upd_tx('de', 'Female genital ("X-chromosome")', 'X-Chromosom: Weibliches Genitale, Brust');
select i18n.upd_tx('de', 'Male genital ("Y-chromosome")', 'Y-Chromosom: Männliches Genitale, Brust');
select i18n.upd_tx('de', 'Social problems', 'SoZiale Probleme');

-- components
select i18n.upd_tx('de', 'Symptoms, complaints', 'Symptome, Beschwerden');
select i18n.upd_tx('de', 'Diagnostic screening, prevention', 'Diagnostik, Screening, Prävention');
select i18n.upd_tx('de', 'Treatment, procedures, medication', 'Behandlung, Prozeduren, Medikation');
select i18n.upd_tx('de', 'Test results', 'Testresultate');
select i18n.upd_tx('de', 'Administrative', 'Administrativ');
select i18n.upd_tx('de', 'Other (referral etc)', 'Anderes');
select i18n.upd_tx('de', 'Diagnosis, disease', 'Diagnosen, Krankheiten');

-- ----------------------------------------------------
select gm.log_script_insertion('v15-ref-icpc2_de-data.sql', 'Revision: 1.1');
