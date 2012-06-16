-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v11-clin-keyword_expansion-data.sql,v 1.3 2009-08-08 12:18:38 ncq Exp $
-- $Revision: 1.3 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1
set default_transaction_read_only to off;

-- --------------------------------------------------------------
delete from clin.keyword_expansion where keyword = 'score-HNPCC-Risiko';

insert into clin.keyword_expansion (
	fk_staff,
	keyword,
	expansion
) values (
	null,
	'score-HNPCC-Risiko',
'HNPCC-Screening (Hereditary Non-Polyposis Colorectal Cancer/Lynch-Syndrom)
--------------------------------------------------------------------------
alle Kriterien (Amsterdam-II) müssen erfüllt sein:

1) Mind. drei Familienangehörige mit histologisch gesichertem Karzinom
	- kolorektal
	- Endometrium
	- Dünndarm
	- Ureter
	- Nierenbecken
   Einer muß mit den beiden anderen erstgradig verwandt sein.
   Familiäre adenomatöse Polyposis muß ausgeschlossen sein.

2) Mind. zwei aufeinanderfolgende Generationen betroffen.

3) Mind. ein Patient unter 50 Jahre bei Diagnosestellung.
');

-- --------------------------------------------------------------
delete from clin.keyword_expansion where keyword = 'score-BRCA-Risiko';

insert into clin.keyword_expansion (
	fk_staff,
	keyword,
	expansion
) values (
	null,
	'score-BRCA-Risiko',
'Screening auf Brustkrebsrisiko (BRCA1/2-Mutation)
-------------------------------------------------
Ein Kriterium (S3-Leitlinie) muß zutreffen.

In gleicher Familienlinie:

- mindestens 3 Frauen Brustkrebs
- mindestens 2 Frauen Brustkrebs, eine Patientin jünger als 51 Jahre
- mindestens 1 Frau Brustkrebs und 1 Frau Eierstockkrebs
- mindestens 2 Frauen Eierstockkrebs
- ein Mann Brustkrebs und eine Frau/Mann Brust- oder Eierstockkrebs

Unabhängig von Familienanamnese erwägen:

- Frau Brust- *und* Eierstockkrebs
- Frau Brustkrebs beidseits, erstmals vor dem 51. Lebensjahr
- Frau Brustkrebs vor dem 36. Lebensjahr
');

-- --------------------------------------------------------------
delete from clin.keyword_expansion where keyword = 'score-DFS-Wagner_Stadien';

insert into clin.keyword_expansion (
	fk_staff,
	keyword,
	expansion
) values (
	null,
	'score-DFS-Wagner_Stadien',
'Diabetisches Fußsyndrom: Wagnerstadien
--------------------------------------

0	Deformation, Hyperkeratosen
1	oberflächliche Hautläsionen
2	tiefe Ulzeration inklusive Sehnen, Knochen, Gelenkkapseln,
	mäßige Weichteilentzündung
3	tiefe Ulzeration mit Abszedierung oder Osteomyelitis,
	erhebliche Weichteilentzündung
4	Gangrän der Zehen oder von Teilen des Vorfußes
	mit/ohne Weichteilentzündung
		oder
	Osteomyelitis mit/ohne Weichteilentzündung
5	Gangrän mit Übergreifen auf den ganzen Fuß

A: ohne arterielles Verschlußleiden -> Prognose günstiger
B: mit arteriellem Verschlußleiden -> Prognose schlechter
');

-- --------------------------------------------------------------
delete from clin.keyword_expansion where keyword = 'score-CHADS2-Antikoagulation';

insert into clin.keyword_expansion (
	fk_staff,
	keyword,
	expansion
) values (
	null,
	'score-CHADS-Antikoagulation',
'CHADS2: ASS oder Cumarine bei VHF im EKG ?
-------------------------------------------

+1: C-ardiale Dekompensation in letzten 3 Monaten
+1: H-ypertension (derzeit oder behandelt)
+1: A-lter > 75 Jahre
+1: D-iabetes mellitus
+2: S-chlaganfall/TIA anamnestisch

Summe 0: allenfalls ASS 300mg/Tag
Summe 1: Einzelfall abwägen
Summe 2: Cumarine (INR 2-3)
');

-- --------------------------------------------------------------
delete from clin.keyword_expansion where keyword = 'Rauchen-Kurzintervention_AAAAA';

insert into clin.keyword_expansion (
	fk_staff,
	keyword,
	expansion
) values (
	null,
	'Rauchen-Kurzintervention_AAAAA',
'Kurzberatung Tabakentwöhnung
----------------------------

Ask: Abfragen des Rauchstatus

	- bei jeder Konsultation
	- "Haben Sie je versucht, aufzuhören ?"
	- "Wären Sie eventuell daran interessiert, jetzt aufzuhören ?"

Advise: Anraten des Rauchverzichts

	- Empfehlung eines Rauchstops
	- Beratung zu Vorteilen und Nachteilen
	  - 80-90% der chron. Atemwegserkrankungen
	  - 80-85% der Lungenkrebse
	  - 25-40% der KHK
	  - 10 Jahre eher Lebensende
	  - jährlich 140.000 Todesfälle durch Rauchen
	  - häufigste Ursache für vorzeitigen Tod

	  - Rauchstop mit 40: 9 Jahre Leben dazu
	  - rauchfrei 25.-34. Lebensjahr: normale Lebenserwartung

Assess: Ansprechen der Motivation

	- Heute Bereitschaft vorhanden, einen Termin zum Rauchstopp
	  zu vereinbaren ?
	- Nein -> 5 "R"s (Makro "Rauchen-Kurzintervention_ RRRRR")
	- Ja -> Assist / Assistieren

Assist: Assistieren beim Rauchverzicht

	- aktive Unterstützung
	- Festlegen des Ausstiegsdatums
	- Erstellen eines Ausstiegsplans
	- Einbeziehen des sozialen Umfeldes
	- zusätzliche Hilfen wie Selbsthilfebroschüren

Arrange: Arrangieren der Nachbetreuung

	- Vereinbarung von Folgeterminen zur Rückfallprophylaxe
');

-- --------------------------------------------------------------
delete from clin.keyword_expansion where keyword = 'Rauchen-Kurzintervention_RRRRR';

insert into clin.keyword_expansion (
	fk_staff,
	keyword,
	expansion
) values (
	null,
	'Rauchen-Kurzintervention_RRRRR',
'Kurzberatung Tabakentwöhnung
----------------------------

Relevance: Relevanz aufzeigen

	Knüpfen Sie die Motivation des Rauchers an seinen körperlichen Zustand,
	seine familiäre und soziale Situation, an gesundheitliche Bedenken,
	Alter, Geschlecht und andere Merkmale wie frühere Ausstiegsversuche.

Risks: Risiken benennen

	kurzfristig:
	 Kurzatmigkeit und Verstärkung von Asthma,
	 Impotenz und Unfruchtbarkeit,
	 erhöhte CO-Konzentration im Serum,
	 erhöhte Herzfrequenz und erhöhte Blutdruckwerte

	langfristig:
	 Erhöhte Infektanfälligkeit,
	 Herzinfarkt und Schlaganfall,
	 Lungenkrebs und andere Krebsarten (Kehlkopf, Mundhöhle, Rachen
	 Speiseröhre, Bauchspeicheldrüse, Harnblase, Gebärmutter, Leukämie),
	 Chronische obstruktive Atemwegserkrankungen
	 (chronische Bronchitis und Emphysem)

	Risiken für die Umgebung:
	 beeinträchtigtes Wohlbefinden,
	 Krankheiten der Atemwege,
	 Herz-Kreislauf-Erkrankungen und Lungenkrebs.
	 Erhöhung der Infektanfälligkeit für Bronchitis,
	 Lungen- und Mittelohrentzündungen,
	 Erhöhung des Risikos, am plötzlichen Säuglingstod zu sterben,
	 Blutdruckerhöhungen.

Rewards: Reize und Vorteile des Rauchstopps verdeutlichen

	Fragen Sie den Patienten, welche Vorteile das Aufhören hat und
	betonen Sie diejenigen, welche die höchste emotionale Bedeutsamkeit haben

Roadblocks: Riegel (Hindernisse und Schwierigkeiten)

	vor Rauchstopp ansprechen:
	 Entzugssymptome,
	 Angst zu scheitern,
	 Gewichtszunahme,
	 fehlende Unterstützung,
	 Depression,
	 Freude am Rauchen

Repetition:

	Raucher, die nicht ausstiegswillig waren, sollten bei
	jedem Folgekontakt erneut mit diesen motivationsfördernden
	Strategien angesprochen werden.
');

-- --------------------------------------------------------------
delete from clin.keyword_expansion where keyword = 'score-Metabolisches_Syndrom';

insert into clin.keyword_expansion (
	fk_staff,
	keyword,
	expansion
) values (
	null,
	'score-Metabolisches_Syndrom',
'Metabolisches Syndrom - diagnostische Kriterien
-----------------------------------------------
Mindestens 3 Kriterien müssen erfüllt sein:

1) zentrale Adipositas, Taillenumfang:
	Männer: > 102cm
	Frauen: > 88cm

2) Plasmaglukose nüchtern > 110 mg/dl (6.1 mmol/l)

3) Hypertonie > 130/85 mmHg

4) HDL-Cholesterin
	Männer: < 40 mg/dl (2.2 mmol/l)
	Frauen: < 50 mg/dl (2.7 mmol/l)

5) Triglyzeride > 150 mg/dl
');

-- --------------------------------------------------------------
delete from clin.keyword_expansion where keyword = '$checkup-gkv';

insert into clin.keyword_expansion (
	fk_staff,
	keyword,
	expansion
) values (
	null,
	'$checkup-gkv',
'Früherkennungsuntersuchungen Erwachsene Deutschland (3/09)
----------------------------------------------------------------------------------
wann	wer	wie oft	wo		was
----------------------------------------------------------------------------------
ab 18	MF	1/Jahr	Zahnarzt	Prophylaxe

ab 20	F	1/Jahr	Gyn			Anamnese/Abstrich/Untersuchung

ab 30	F	1/Jahr	Gyn			+ Mamma-/Axillapalpation

ab 35	MF	2.Jahr	Hausarzt	UrinStix, BZ, Chol, Anamnese,
							körperliche Untersuchung

ab 35	MF	2.Jahr	Hausarzt	Hautuntersuchung, ggf ad Derma

ab 45	M	1/Jahr	Uro			Prostata, Inspektion Genitale/Haut

50-55	MF	1/Jahr	Hausarzt	Beratung Darmkrebs,
								rektal-digital, HaemOccult

50-69	F	2.Jahr	Gyn		Mammographie

ab 55	MF			Hausarzt	Beratung Darmkrebs, dazu
			2.Jahr	Hausarzt	HaemOccult oder
			10.Jahr	Endo		2x Koloskopie
----------------------------------------------------------
');

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v11-clin-keyword_expansion-data.sql,v $', '$Revision: 1.3 $');

-- ==============================================================
-- $Log: v11-clin-keyword_expansion-data.sql,v $
-- Revision 1.3  2009-08-08 12:18:38  ncq
-- - state of the art CHADS score
--
-- Revision 1.2  2009/04/14 18:32:07  ncq
-- - add more macros
--
-- Revision 1.1  2009/04/01 15:55:40  ncq
-- - new
--
-- Revision 1.2  2009/02/25 09:38:49  ncq
-- - AMUSE score for TVT
--
-- Revision 1.1  2009/02/17 10:49:28  ncq
-- - add Wells and GCS
--
--