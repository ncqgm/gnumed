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
delete from clin.keyword_expansion where keyword = 'score-Coronary_Artery_Disease_in_chest_pain';

insert into clin.keyword_expansion (
	fk_staff,
	keyword,
	expansion
) values (
	null,
	'score-Coronary_Artery_Disease_in_chest_pain',
'Coronary Artery Disease as reason for chest pain in primary care
----------------------------------------------------------------
CMAJ 2010. DOI:10.1503/cmaj.100212

1: Age/sex (female > 64, male > 54)
1: Known clinical vascular disease¹
1: Pain worse during exercise
1: Pain *not* reproducible by palpation
1: Patient assumes pain of cardiac origin

Sum >2 points: positive for coronary artery disease

¹coronary artery disease, occlusive vascular
 disease, cerebrovascular disease

In acute/emergency situations also take into
account vital signs and symptoms !
');

-- --------------------------------------------------------------
delete from clin.keyword_expansion where keyword = 'score-Naevus_ABCDEF';

insert into clin.keyword_expansion (
	fk_staff,
	keyword,
	expansion
) values (
	null,
	'score-Naevus_ABCDEF',
'ABCDEF rule for identifying atypical naevi
------------------------------------------

A: Asymmetry (any shape other than round or oval)
B: Borders (fading into the surrounding skin)
C: Color (is multi-coloured)
D: Diameter (of 5mm or more)
E: Evolution or Elevation (of formerly flat lesion)
F: Feeling (itching, stinging, burning) or Funny (Ugly Duckling)
');

-- --------------------------------------------------------------
delete from clin.keyword_expansion where keyword = 'score-Naevus-Glasgow_7_points';

insert into clin.keyword_expansion (
	fk_staff,
	keyword,
	expansion
) values (
	null,
	'score-Naevus-Glasgow_7_points',
'Glasgow 7-points checklist for identifying atypical naevi
---------------------------------------------------------

Major points:

Change in

	- size
	- shape
	- colour

Minor points:

	- at least 7mm in diameter
	- inflammation
	- oozing / crusting / bleeding
	- change in sensation
');

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v14-clin-keyword_expansion-data.sql,v $', '$Revision: 1.3 $');

-- ==============================================================
