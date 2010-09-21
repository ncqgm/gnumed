-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
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
select gm.log_script_insertion('v15-clin-keyword_expansion-data.sql', '1.3');

-- ==============================================================
