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
delete from ref.keyword_expansion where keyword = 'score-bakterielle_Konjunktivitis';

insert into ref.keyword_expansion (
	fk_staff,
	keyword,
	textual_data
) values (
	null,
	'score-bakterielle_Konjunktivitis',
'Score zur bakteriellen Konjunktivitis (2004)
--------------------------------------------
Rietveld R. et al: Predicting bacterial cause in infectious conjunctivitis. BMJ 2004; 329: 206-210.

$[5/0]$ ZWEI verklebte Augen morgens
$[2/0]$ NUR EIN verklebtes Auge morgens
$[ja: -1 / nein: 0]$ juckendes Auge
$[ja: -2 / nein: 0]$ Konjunktivitis in der Anamnese

Summe: $[Summe]$ (>= 2: 67% korrekt positiv und 73% korrekt negativ)

Ausschlußkriterien:

	< 18 Jahre alt
	> 7 Tage Symptome
	Antibiose in den letzten 2 Wochen
	Kontaktlinsen
	Augentrauma/-OP
	akuter Visusverlust

Therapie: Bibrocathol (Antiseptikum), sonst Kanamycin (Arznei-Telegramm 1995)'
);

-- --------------------------------------------------------------
select gm.log_script_insertion('v18-ref-bacterial_conjunctivitis_score-fixup.sql', '18.2');
