-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
--
-- ==============================================================
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
delete from clin.keyword_expansion where keyword = 'score-HEMORR²HAGES';

insert into clin.keyword_expansion (
	fk_staff,
	keyword,
	expansion
) values (
	null,
	'score-HEMORR²HAGES',
'HEMORR²HAGES: Blutungsrisiko unter OAK
--------------------------------------
Am Heart J. 2006 Mar;151(3):713-9.

$<1 oder 0 eingeben>$ H epatische oder Nierenerkrankung
$<1 oder 0 eingeben>$ E thanolabusus
$<1 oder 0 eingeben>$ M alignom
$<1 oder 0 eingeben>$ O ld patient (> 75 Jahre)
$<1 oder 0 eingeben>$ R eduzierte Thrombozytenzahl/-funktion
$<2 oder 0 eingeben>$ R²ekurrente (frühere) große Blutung
$<1 oder 0 eingeben>$ H ypertonie (unkontrolliert)
$<1 oder 0 eingeben>$ A nämie
$<1 oder 0 eingeben>$ G enetische Faktoren
$<1 oder 0 eingeben>$ E xzessives Sturzrisiko
$<1 oder 0 eingeben>$ S Schlaganfall in der Anamnese
--------------------------------------
Summe   Rate großer Blutungen
        pro 100 Patientenjahre
 0          1.9
 1          2.5
 2          5.3
 3          8.4
 4         10.4
>4         12.3

Bewertung: Summe = $<Summe eintragen>$'
);

-- --------------------------------------------------------------
delete from clin.keyword_expansion where keyword = 'score-Gulich-StrepA_Tonsillitis';

insert into clin.keyword_expansion (
	fk_staff,
	keyword,
	expansion
) values (
	null,
	'score-Gulich-StrepA_Tonsillitis',
'Gulich-Score: likelihood of GABHS in sore throat
------------------------------------------------
Gulich M, Triebel T, Zeitler H-P; Eur J Gen Pract 2002;8:58-62.

Most accurate if
- onset: 1 day to 1 week ago
- age: 16 to 76 years

$<0: (lymphoid) granulations | 1: reddish | 2: deeply red>$: throat mucosa (0: (lymphoid) granulations | 1: reddish | 2: deeply red)
$<0: normal | 1: infected/slightly reddish | 2: deeply red>$: uvula (0: normal | 1: infected/slightly reddish | 2: deeply red)
$<0: normal | 1: infected/slightly reddish | 2: deeply red>$: soft palate (0: normal | 1: infected/slightly reddish | 2: deeply red)
$<0: normal/removed | 1: reddish/swollen | 2: exsudate>$: tonsils (0: normal/removed | 1: reddish/swollen | 2: exsudate)
-------------------------------
Sum: $<Enter sum !>$

Sum < 4: 91% GABHS negative
Sum 4-5: near-patient CRP
	CRP < 35mg/L: 89% GABHS negative
	CRP > 35mg/L: 89% GABHS positive
Sum > 5: 81% GAHBS positive
');

-- --------------------------------------------------------------
delete from clin.keyword_expansion where keyword = 'score-Marburg-CHD_in_chest_pain';

insert into clin.keyword_expansion (
	fk_staff,
	keyword,
	expansion
) values (
	null,
	'score-Marburg-CHD_in_chest_pain',
'CHD as reason for chest pain in Primary Care
--------------------------------------------
CMAJ 2010. DOI:10.1503/cmaj.100212

$<Enter 0 or 1 !>$: Age/sex (female > 64, male > 54)
$<Enter 0 or 1 !>$: Known clinical vascular disease¹
$<Enter 0 or 1 !>$: Pain worse on exertion
$<Enter 0 or 1 !>$: Pain *NOT* reproducible by palpation
$<Enter 0 or 1 !>$: Patient assumes pain is of cardiac origin

Sum: $<Enter sum !>$ (>2 points: positive for CHD)

¹coronary heart disease, occlusive vascular
 disease, cerebrovascular disease

In acute/emergency situations also take into
account vital signs and symptoms !
');

-- --------------------------------------------------------------
delete from clin.keyword_expansion where keyword = 'score-CAGE-Alkoholkonsum';

insert into clin.keyword_expansion (
	fk_staff,
	keyword,
	expansion
) values (
	null,
	'score-CAGE-Alkoholkonsum',
'CAGE: Risikobewertung von Alkoholkonsum
---------------------------------------
JAMA 1984. DOI:10.1001/jama.1984.03350140051025 / PMID 6471323
https://en.wikipedia.org/wiki/CAGE_questionnaire

 $<1 oder 0>$ C-onsum: Hatten Sie schon einmal das Gefühl,
   daß Sie Ihren Alkoholkonsum reduzieren sollten ? (C-ut down)
 $<1 oder 0>$ A-ndere: Hat es sie schon aufgeregt, wenn andere
   Leute Ihr Trinkverhalten kritisieren ? (A-nnoyance)
 $<1 oder 0>$ G-ewissen: Hatten Sie wegen Ihres Alkohol-
   konsums schon einmal Gewissensbisse ? (G-uilty)
 $<1 oder 0>$ E-rwachen: Haben Sie morgens nach dem Erwachen
   schon als Erstes Alkohol getrunken, um Ihre Nerven zu
   beruhigen oder den Kater loszuwerden ? (E-ye opener)

Summe: $<Bitte zusammenrechnen !>$

Wahrscheinlichkeit, daß Alkoholmißbrauch vorliegt:
 1: 62%
 2: 89%
>2: 99%
');

-- --------------------------------------------------------------
select gm.log_script_insertion('v17-clin-keyword_expansion-data.sql', '17.0');
