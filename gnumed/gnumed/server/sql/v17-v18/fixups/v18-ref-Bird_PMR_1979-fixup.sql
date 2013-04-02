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
delete from ref.keyword_expansion where keyword = 'score-Bird-Polymyalgia_rheumatica';

insert into ref.keyword_expansion (
	fk_staff,
	keyword,
	textual_data
) values (
	null,
	'score-Bird-Polymyalgia_rheumatica',
'Bird-Score für Polymyalgia rheumatica
-------------------------------------
Bird A, et al. An evaluation of criteria for polymyalgia rheumatica. Ann Rheum Dis 1979 Oct;38(5): 434-9.

$[1/0]$ bilaterale Schulterschmerzen und/oder –steife
$[1/0]$ Oberarm-Druckschmerz bds
$[1/0]$ Morgensteifigkeit >1h
$[1/0]$ Depression und/oder Gewichtsverlust
$[1/0]$ initiale BSG >40 (nach 1h)
$[1/0]$ Alter >65
$[1/0]$ akuter Beginn (in 2 Wochen von Erstsymptomen bis Vollbild)

Summe: $[Summe]$ (>2: PMR wahrscheinlich, Sens ~92%, Spez ~80%)

Anmerkung: bisher keine international akzeptierten
Diagnosekriterien (laut Deutscher Gesellschaft für
Rheumatologie, 2012)'
);

-- --------------------------------------------------------------
select gm.log_script_insertion('v18-ref-Bird_PMR_1979-fixup.sql', '18.2');
