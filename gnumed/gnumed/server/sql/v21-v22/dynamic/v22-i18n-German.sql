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
select i18n.upd_tx('de_DE', 'de facto', '');
select i18n.upd_tx('de_DE', 'single', 'Single');

select i18n.upd_tx('de_DE', 'tuberculosis', 'Tuberkulose');
select i18n.upd_tx('de_DE', 'salmonella typhi (typhoid)', 'Typhus');
select i18n.upd_tx('de_DE', 'influenza (seasonal)', 'saisonale Influenza');
select i18n.upd_tx('de_DE', 'Deletion of', 'Löschung von');
select i18n.upd_tx('de_DE', 'Medication history', 'Medikamentenanamnese');
select i18n.upd_tx('de_DE', 'smokes', 'raucht');
select i18n.upd_tx('de_DE', 'often late', 'oft zu spät');
select i18n.upd_tx('de_DE', 'Ministry of Public Health', 'Gesundheitsministerium');
select i18n.upd_tx('de_DE', 'Hospital', 'Krankenhaus');
select i18n.upd_tx('de_DE', 'Ward', 'Station');
select i18n.upd_tx('de_DE', 'Practice', 'Arztpraxis');
select i18n.upd_tx('de_DE', 'Surgery', 'Arztpraxis');
select i18n.upd_tx('de_DE', 'Medical Practice', 'Arztpraxis');
select i18n.upd_tx('de_DE', 'Physical Therapy Practice', 'Physiotherapie');
select i18n.upd_tx('de_DE', 'Occupational Therapy Practice', 'Ergotherapie');
select i18n.upd_tx('de_DE', 'Laboratory', 'Labor');
select i18n.upd_tx('de_DE', 'until', 'bis');
select i18n.upd_tx('de_DE', 'General and Unspecified', 'Allgemein/Unspezifisch');
select i18n.upd_tx('de_DE', 'Blood, Blood forming organs, Immune mechanism', 'Blut/blutbildene Organe/Immunsystem');
select i18n.upd_tx('de_DE', 'Digestive', 'VerDauung');
select i18n.upd_tx('de_DE', 'Eye ("Focal")', 'Auge ("F"isus)');
select i18n.upd_tx('de_DE', 'Ear ("Hearing")', 'Ohr ("H"ören)');
select i18n.upd_tx('de_DE', 'Cardivascular', 'Kardivaskulär');
select i18n.upd_tx('de_DE', 'Musculoskeletal ("Locomotion")', 'Bewegungsapparat');
select i18n.upd_tx('de_DE', 'Neurological', 'Nervensystem');
select i18n.upd_tx('de_DE', 'Psychological', 'Psyche');
select i18n.upd_tx('de_DE', 'Respiratory', 'Respirationssystem');
select i18n.upd_tx('de_DE', 'Skin', 'Haut');
select i18n.upd_tx('de_DE', 'Endocrine/Metabolic and Nutritional ("Thyroid")', 'Endokrinium/Metabolismus/Ernährung');
select i18n.upd_tx('de_DE', 'Urological', 'Urologie');
select i18n.upd_tx('de_DE', 'Pregnancy, Childbearing, Family planning ("Women")', 'SchWangerschaft/Geburt/Familienplanung');
select i18n.upd_tx('de_DE', 'Female genital ("X-chromosome")', 'X-chromosomales');
select i18n.upd_tx('de_DE', 'Male genital ("Y-chromosome")', 'Y-chromosomales');
select i18n.upd_tx('de_DE', 'Social problems', 'SoZiales');
select i18n.upd_tx('de_DE', 'Symptoms, complaints', 'Symptome, Beschwerden');
select i18n.upd_tx('de_DE', 'Diagnostic screening, prevention', 'Screening, Prävention');
select i18n.upd_tx('de_DE', 'Treatment, procedures, medication', 'Behandlung, Maßnahme, Medikation');
select i18n.upd_tx('de_DE', 'Test results', 'Testergebnis');
select i18n.upd_tx('de_DE', 'Administrative', 'Verwaltung');
select i18n.upd_tx('de_DE', 'Other (referral etc)', 'Anderes (z.B.Überweisung');
select i18n.upd_tx('de_DE', 'Diagnosis, disease', 'Diagnose, Krankheit');
select i18n.upd_tx('de_DE', 'husband', 'Ehemann');
select i18n.upd_tx('de_DE', 'wife', 'Ehefrau');
select i18n.upd_tx('de_DE', 'sister', 'Schwester');
select i18n.upd_tx('de_DE', 'father', 'Vater');
select i18n.upd_tx('de_DE', 'mother', 'Mutter');
select i18n.upd_tx('de_DE', 'brother', 'Bruder');
select i18n.upd_tx('de_DE', 'Privacy notice', 'Privatsphärenhinweis');
select i18n.upd_tx('de_DE', 'open', 'offen');
select i18n.upd_tx('de_DE', 'closed', 'beendet');
select i18n.upd_tx('de_DE', 'Health Issue', 'Grunderkrankung');
select i18n.upd_tx('de_DE', 'active', 'aktiv');
select i18n.upd_tx('de_DE', 'inactive', 'inaktiv');
select i18n.upd_tx('de_DE', 'clinically relevant', 'medizinisch relevant');
select i18n.upd_tx('de_DE', 'clinically not relevant', 'medizinisch nicht relevant');
select i18n.upd_tx('de_DE', 'Laterality', 'Seitenbezug');
select i18n.upd_tx('de_DE', 'confidential', 'vertraulich');
select i18n.upd_tx('de_DE', 'cause of death', 'Todesursache');
select i18n.upd_tx('de_DE', 'Procedure', 'Maßnahme');
select i18n.upd_tx('de_DE', 'ongoing', 'andauernd');
select i18n.upd_tx('de_DE', 'Encounter', 'APK');
select i18n.upd_tx('de_DE', 'AOE', 'BE');
select i18n.upd_tx('de_DE', 'bill receiver', 'Rechnungsempfänger');
select i18n.upd_tx('de_DE', 'invoice', 'Rechnung');
select i18n.upd_tx('de_DE', 'Synopsis', 'Synopse');
select i18n.upd_tx('de_DE', 'consultation', 'APK');
select i18n.upd_tx('de_DE', 'branch', 'Zweigstelle');
select i18n.upd_tx('de_DE', 'of', 'von');
select i18n.upd_tx('de_DE', 'generic praxis', 'generische Praxis');
select i18n.upd_tx('de_DE', 'generic praxis branch', 'generische Zweigstelle');
select i18n.upd_tx('de_DE', 'part(s)', 'Teil(e)');
select i18n.upd_tx('de_DE', 'with', 'mit');
select i18n.upd_tx('de_DE', 'EDC', 'ET');
select i18n.upd_tx('de_DE', 'Clinical reminder', 'Medizinischer Hinweis');
select i18n.upd_tx('de_DE', 'Due today', 'Heute fällig');
select i18n.upd_tx('de_DE', 'Due:', 'Fällig:');
select i18n.upd_tx('de_DE', 'Was due:', 'War fällig:');
select i18n.upd_tx('de_DE', 'Epires today', 'Verfällt heute');
select i18n.upd_tx('de_DE', 'Expires:', 'Verfällt:');
select i18n.upd_tx('de_DE', 'Will expire:', 'Wird verfallen:');
select i18n.upd_tx('de_DE', 'Importance:', 'Wichtigkeit:');
select i18n.upd_tx('de_DE', 'Context:', 'Kontext:');
select i18n.upd_tx('de_DE', 'Data:', 'Daten:');
select i18n.upd_tx('de_DE', 'Provider:', 'Mitarbeiter:');

select i18n.upd_tx('de_DE', 'J07AP03-target', 'Typhus'); -- "en": typhoid
select i18n.upd_tx('de_DE', 'J07AH0Y-target', 'Y-Meningokokken'); -- "en": meningococcus Y
select i18n.upd_tx('de_DE', 'J07AH0W-target', 'W-Meningokokken'); -- "en": meningococcus W
select i18n.upd_tx('de_DE', 'J07AH06-target', 'B-Meningokokken'); -- "en": meningococcus B
select i18n.upd_tx('de_DE', 'J07AH01-target', 'A-Meningokokken'); -- "en": meningococcus A
select i18n.upd_tx('de_DE', 'J07AG01-target', 'HiB'); -- "en": HiB
select i18n.upd_tx('de_DE', 'J07AM01-target', 'Tetanus'); -- "en": tetanus
select i18n.upd_tx('de_DE', 'J07BF03-target', 'Poliomyelitis'); -- "en": poliomyelitis
select i18n.upd_tx('de_DE', 'J07BA01-target', 'FSME'); -- "en": tick-borne encephalitis
select i18n.upd_tx('de_DE', 'J07AXQF-target', 'Q-Fieber'); -- "en": Q fever
select i18n.upd_tx('de_DE', 'J07BE01-target', 'Mumps'); -- "en": mumps
select i18n.upd_tx('de_DE', 'J07AP10-target', 'Typhus, Paratyphus'); -- "en": typhoid, paratyphus
select i18n.upd_tx('de_DE', 'J07BF01-target', 'Poliomyelitis'); -- "en": poliomyelitis
select i18n.upd_tx('de_DE', 'J07AL01-target', 'Pneumokokken'); -- "en": pneumococcus
select i18n.upd_tx('de_DE', 'J07BL01-target', 'Gelbfieber'); -- "en": yellow fever
select i18n.upd_tx('de_DE', 'J07AE01-target', 'Cholera'); -- "en": cholera
select i18n.upd_tx('de_DE', 'J07AH10-target', 'A-Meningokokken'); -- "en": meningococcus A
select i18n.upd_tx('de_DE', 'J07BJ01-target', 'Röteln'); -- "en": rubella
select i18n.upd_tx('de_DE', 'J07BA03-target', 'japanische Enzephalitis'); -- "en": japanese encephalitis
select i18n.upd_tx('de_DE', 'J07AJ02-target', 'Pertussis'); -- "en": pertussis
select i18n.upd_tx('de_DE', 'J07AK01-target', 'Pest'); -- "en": plague
select i18n.upd_tx('de_DE', 'J07AP02-target', 'Typhus'); -- "en": typhoid
select i18n.upd_tx('de_DE', 'J07BC03-target', 'Hepatitis A'); -- "en": hepatitis A
select i18n.upd_tx('de_DE', 'J07BA02-target', 'japanische Enzephalitis'); -- "en": japanese encephalitis
select i18n.upd_tx('de_DE', 'J07AN01-target', 'Tbc'); -- "en": tbc
select i18n.upd_tx('de_DE', 'J07BB02-target', 'Influenza'); -- "en": influenza
select i18n.upd_tx('de_DE', 'J07BH01-target', 'Rotavirus-GE'); -- "en": rotavirus diarrhea
select i18n.upd_tx('de_DE', 'J07BM03-target', 'HPV'); -- "en": HPV
select i18n.upd_tx('de_DE', 'J07AJ01-target', 'Pertussis'); -- "en": pertussis
select i18n.upd_tx('de_DE', 'J07BC01-target', 'Hepatitis B'); -- "en": hepatitis B
select i18n.upd_tx('de_DE', 'J07AJ0-target',  'Pertussis'); -- "en": pertussis
select i18n.upd_tx('de_DE', 'J07BC02-target', 'Hepatitis A'); -- "en": hepatitis A
select i18n.upd_tx('de_DE', 'J07AD01-target', 'Brucellose'); -- "en": brucellosis
select i18n.upd_tx('de_DE', 'J07AP01-target', 'Typhus'); -- "en": typhoid
select i18n.upd_tx('de_DE', 'J07AC01-target', 'Milzbrand'); -- "en": anthrax
select i18n.upd_tx('de_DE', 'J07BX01-target', 'Pocken'); -- "en": variola (smallpox)
select i18n.upd_tx('de_DE', 'J07BK02-target', 'Zoster'); -- "en": zoster (shingles)
select i18n.upd_tx('de_DE', 'J07BB01-target', 'Influenza'); -- "en": influenza
select i18n.upd_tx('de_DE', 'J07AH09-target', 'B-Meningokokken'); -- "en": meningococcus B
select i18n.upd_tx('de_DE', 'J07AH07-target', 'C-Meningokokken'); -- "en": meningococcus C
select i18n.upd_tx('de_DE', 'J07BM0-target',  'HPV'); -- "en": HPV
select i18n.upd_tx('de_DE', 'J07BM01-target', 'HPV'); -- "en": HPV
select i18n.upd_tx('de_DE', 'J07BB03-target', 'Influenza'); -- "en": influenza
select i18n.upd_tx('de_DE', 'J07BG01-target', 'Tollwut'); -- "en": rabies
select i18n.upd_tx('de_DE', 'J07AR01-target', 'Fleckfieber'); -- "en": typhus exanthematicus
select i18n.upd_tx('de_DE', 'J07BH02-target', 'Rotavirus-GE'); -- "en": rotavirus diarrhea
select i18n.upd_tx('de_DE', 'J07AF01-target', 'Diphterie'); -- "en": diphtheria
select i18n.upd_tx('de_DE', 'J07AE02-target', 'Cholera'); -- "en": cholera
select i18n.upd_tx('de_DE', 'J07BM02-target', 'HPV'); -- "en": HPV
select i18n.upd_tx('de_DE', 'J07BK01-target', 'Windpocken'); -- "en": varicella (chickenpox)
select i18n.upd_tx('de_DE', 'J07AL02-target', 'Pneumokokken'); -- "en": pneumococcus
select i18n.upd_tx('de_DE', 'J07BD01-target', 'Masern'); -- "en": measles

select i18n.upd_tx('de_DE', 'sent to', 'gesendet an');

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-i18n-German.sql', '22.0');
