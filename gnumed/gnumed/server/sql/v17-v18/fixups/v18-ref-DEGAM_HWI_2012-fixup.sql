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
delete from ref.keyword_expansion where keyword = 'LL-HWI_Anamnese-DEGAM_2012';

insert into ref.keyword_expansion (
	fk_staff,
	keyword,
	textual_data
) values (
	null,
	'LL-HWI_Anamnese-DEGAM_2012',
'LL Brennen beim Wasserlassen (DEGAM 2012)
--------------------------------------------
http://leitlinien.degam.de/index.php?id=73
http://leitlinien.degam.de/uploads/media/Kurzversion_Brennen-002.pdf

- Beginn: $[Seit wann ?]$
- Dysurie: $[Brennen ?]$
- Pollakisurie: $[Pollakisurie ?]$
- vaginaler Ausfluß: $[Ausfluß ?]$ (=> gynäk.Erkrankung ?)
- Fieber: $[Fieber ?]$°C
- Flankenschmerz: $[Flankenschmerz ?]$
- Makrohämaturie: $[Blut im Urin ?]$
- Krankheitsgefühl: $[AZ ?]$

Komplizierende Faktoren:

- Kind / Mann
- Schwangerschaft: $[Schwanger ?]$
- Dauerkatheter: $[Katheter ?]$
- Immunsuppression: $[HIV ? D.m. ? Immunsuppression ?]$
- Harnwegsveränderung: $[Nierenkrankheit ? Abflußstörung ? Z.n.OP ?]$

keine komplizierenden Faktoren/kein Fieber/kein Flankenschmerz:
 nein => Behandlung anbieten

eingeschränkte Kommunikation/Flankenschmerz/Fieber/komplizierende Faktoren
 ja => körperliche Untersuchung
');

-- --------------------------------------------------------------
delete from ref.keyword_expansion where keyword = 'LL-HWI_Befund-DEGAM_2012';

insert into ref.keyword_expansion (
	fk_staff,
	keyword,
	textual_data
) values (
	null,
	'LL-HWI_Befund-DEGAM_2012',
'LL Brennen beim Wasserlassen (DEGAM 2012)
--------------------------------------------

Klopfschmerz Nierenlager:
 links: $[Klopfschmerz links ?]$
 rechts: $[Klopfschmerz rechts ?]$
Fieber:
 axillär/rektal: $[Temperatur ?]$°C
UrinStix:
 Nitrit: $[Nitrit: +/-]$
	+ => Behandlung anbieten
 Leukos: $[Leukos: +/-]$
	+ => Kultur erwägen
	- => Kultur und Konsil erwägen

Optionen:
 - Urinmikroskopie
 -.Abwartendes Offenlassen
 - symptomatische Behandlung
');

-- --------------------------------------------------------------
delete from ref.keyword_expansion where keyword = 'LL-HWI_Bewertung-DEGAM_2012';

insert into ref.keyword_expansion (
	fk_staff,
	keyword,
	textual_data
) values (
	null,
	'LL-HWI_Bewertung-DEGAM_2012',
'unkomplizierter HWI
Rezidiv unkomplizierter HWI
komplizierter HWI
Pyelonephritis
Urethritis
Kolpitis
Prostatitis

AGVs:
- Nierenparenchymschäden (Kinder, fieberhaft):
- Pyelonephritis/Sepsis (Senioren/Schwangere/Obstruktion):
- Fertilitätsstörung:
- chronische Prostatitis
');

-- --------------------------------------------------------------
delete from ref.keyword_expansion where keyword = 'LL-HWI_Plan-DEGAM_2012';

insert into ref.keyword_expansion (
	fk_staff,
	keyword,
	textual_data
) values (
	null,
	'LL-HWI_Plan-DEGAM_2012',
'LL Brennen beim Wasserlassen (DEGAM 2012)
--------------------------------------------

Abwartend Offenlassen:
 Kontrolle in $[Kontrolle wann ?]$ Tagen
Symptomatische Behandlung:
 Paracetamol
 Ibuprofen
 Blasendesinfiziens
 Trinkmenge erhöhen
Kultur: $[Urinkultur ?]$
Konsil Gyn/Uro: $[Überweisung ?]$
Antibiose:
 TMP 2x100-200mg 3 Tage
 Nitrofurantoin ret 2x100mg 3-5 Tage (off label)
 ggf Fosfomycin 1x3000mg
');

-- --------------------------------------------------------------
select gm.log_script_insertion('v18-ref-DEGAM_HWI_2012-fixup.sql', '18.2');
