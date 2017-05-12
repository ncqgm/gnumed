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
delete from ref.keyword_expansion where keyword = 'algo-TVT_OE';

insert into ref.keyword_expansion (
	fk_staff,
	keyword,
	textual_data
) values (
	null,
	'algo-TVT_OE',
'Constans: Diagnostik TVT Obere Extremität
-----------------------------------------------------------
DÄB / 114 / 244-9 / 7.April 2014
DOI 10.3238/artebl.2017.0244

- Schwellung/Schmerz/Venenzeichnung/Zyanose
- Armschwäche/-parästhesie
- ZVK/Schrittmacher/Tumorleiden
- Einengung Thoraxapertur (Rucksack, Anatomie)

Klinischer Verdacht auf TVT-OE ?: $[Verdacht: Ja/Nein]$

 Constans-Kriterien

$[0/1]$ ZVK oder Schrittmacher
$[0/1]$ lokalisierter Schmerz
$[0/1]$ einseitige Schwellung
$[0/-1]$ alternative Diagnose wahrscheinliche Ursache

Summe $[Summe]$

0/1 - TVT-OE unwahrscheinlich
	-> D-Dimer
		< 500µg/l -> TVT-OE weitgehend ausgeschlossen
		> 500µg/l -> Sonographie

2/3 - TVT-OE wahrscheinlich
	-> Sonographie
');

-- --------------------------------------------------------------
select gm.log_script_insertion('v21-Constans-TVT-OE.sql', '21.13');
