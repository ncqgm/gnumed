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
delete from clin.keyword_expansion where keyword = 'score-Rom-Obstipation';

insert into clin.keyword_expansion (
	fk_staff,
	keyword,
	expansion
) values (
	null,
	'score-Rom-Obstipation',
'Rom-Kriterien der Obstipation
------------------------------------------------
Mindestens 2 Symptome für mindestens 3 Monate im letzten halben Jahr.

- heftiges Pressen ...
- harte Stühle ...
- Gefühl der inkompletten Entleerung¹ ...
- Gefühl der analen Blockierung¹ ...
- manuelle Manöver zur Stuhlentleerung¹ ...

	(... bei mindestens jeder 3. Defäkation)

- weniger als 3 Entleerungen pro Woche

(¹Hinweis auf Defäkationsstörung)

Obstipation ist UAW bei:

- Ca-Antagonisten, Clonidin
- trizyklische Antidepressiva
- Eisen, Antiepileptika, Opiate
- Parkinsonmedikation (anticholinerg, dopaminerg)
');

-- --------------------------------------------------------------
delete from clin.keyword_expansion where keyword = 'score-stroke-Cincinatti';

insert into clin.keyword_expansion (
	fk_staff,
	keyword,
	expansion
) values (
	null,
	'score-stroke-Cincinatti',
'Cincinatti Stroke Scale (F.A.S.T.)
--------------------------------------

F(ace): Can patient smile symmetrically ?
A(rms): Close eyes, lift arms palms up, hold: asymmetric swaying/sinking ?
S(peech): Can patient repeat "I do not need help" clearly and correctly ?
T(ime): How long ?  (therapeutic window 4-6 hours)
');

-- --------------------------------------------------------------
delete from clin.keyword_expansion where keyword = 'score-UTI';

insert into clin.keyword_expansion (
	fk_staff,
	keyword,
	expansion
) values (
	null,
	'score-UTI',
'Bacterial UTI score
---------------------------------------------
Dtsch Arzteblatt Int 2010; 107(21): 361-7

 2:  Nitrite detected
1½: Leukocytes detected
 1:  Hämaturie
 1:  at least moderately severe dysuria
 ½:  at least moderately severe nocturia

Bacterial UTI:

 3 points: 76% sensitivity, 74% specifity
');

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v14-clin-keyword_expansion-data.sql,v $', '$Revision: 1.3 $');

-- ==============================================================
