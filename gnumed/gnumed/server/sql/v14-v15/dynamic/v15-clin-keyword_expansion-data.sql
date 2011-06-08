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
delete from clin.keyword_expansion where keyword = 'score-Coronary_Artery_Disease_in_chest_pain';
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

1: Age/sex (female > 64, male > 54)
1: Known clinical vascular disease¹
1: Pain worse on exertion
1: Pain *not* reproducible by palpation
1: Patient assumes pain is of cardiac origin

Sum >2 points: positive for CHD

¹coronary heart disease, occlusive vascular
 disease, cerebrovascular disease

In acute/emergency situations also take into
account vital signs and symptoms !
');

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

    Throat mucosa
0 - (lymphoid) granulations
1 - reddish
2 - deeply red

    Uvula
0 - normal
1 - infected/slightly reddish
2 - deeply red

    Soft palate
0 - normal
1 - infected/slightly reddish
2 - deeply red

    Tonsils
0 - normal/removed
1 - reddish/swollen
2 - exsudate
-------------------------------

Sum < 4: 91% GABHS negative
Sum > 5: 81% GAHBS positive

Sum 4-5 -> near-patient CRP

	CRP < 35mg/L: 89% GABHS negative
	CRP > 35mg/L: 89% GABHS positive

Most accurate if
- onset: 1 day to 1 week ago
- age: 16 to 76 years
');

-- --------------------------------------------------------------
select gm.log_script_insertion('v15-clin-keyword_expansion-data.sql', '1.3');

-- ==============================================================
