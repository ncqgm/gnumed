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
delete from ref.keyword_expansion where keyword = 'algo-NSAR';

insert into ref.keyword_expansion (
	fk_staff,
	keyword,
	textual_data
) values (
	null,
	'algo-NSAR',
'NSAR: Risikoadaptierte Wirkstoffwahl
-----------------------------------------------------------
KVH aktuell, 1/2014 "NSAR - Risiken und Kontraindikationen"

Indikation: $[Schmerzursache]$

Gastrointestinales Risiko:

 $[>65 Jahre: 0/1]$ Alter: >65 Jahre = 1 Punkt
 $[GI-Krankheit: 0/1/2]$ Anamnese: Ulkus = 1 Punkt, Blutung/Perforation = 2 Punkt
 $[Hochdosis: 0/1]$ Therapie: hohe Dosis geplant? = 1 Punkt
 $[Nikotin/Alkohol: 0/1]$ Anamnese: starker Nikotin-/Alkoholmißbrauch = 1 Punkt
 $[Begleitmedikation: 0/1]$ Begleitmedikation: ASS/Clopidogrel/Kortikoid/OAK/SSRI = 1 Punkt

Summe: $[Summe]$

Kardiovaskuläres Risiko:

 $[+/-]$ Indikation für Thrombozytenaggregationshemmer vorhanden ?

Auswahl:

 GI  >2 / CV+ : möglichst keine NSAR; falls unbedingt nötig: Naproxen + PPI
 GI  >2 / CV- : bis 1200mg/Tag Ibuprofen + PPI oder Coxib + PPI
 GI 1-2 / CV- : NSAR + PPI
 GI   1 / CV+ : Naproxen (+ PPI)
 GI   0 / CV- : NSAR

Therapieregime: $[Therapieregime]$
');

-- --------------------------------------------------------------
select gm.log_script_insertion('v20-NSAR_Auswahl.sql', '20.0');
