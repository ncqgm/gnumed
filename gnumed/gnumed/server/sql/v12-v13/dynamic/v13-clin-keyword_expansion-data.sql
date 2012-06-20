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
delete from clin.keyword_expansion where keyword = 'score-Centor-StrepA_Tonsillitis';

insert into clin.keyword_expansion (
	fk_staff,
	keyword,
	expansion
) values (
	null,
	'score-Centor-StrepA_Tonsillitis',
'Centor-Score: Antibiose bei Halsschmerz ?
-----------------------------------------
(gültig > 15 Jahre)

1: Fieber in Anamnese (> 38°)
1: fehlender Husten
1: vordere Halslymphknoten geschwollen
1: Tonsillenexsudate

Wahrscheinlichkeit von Strep-A im Rachenabstrich:

4: 50-60%
3: 30-35%
2: 15%
1: 6-7%
0: 2.5%

Antibiose ?

nein: <3 Punkte und KEIN Kontakt zu StrepA-Pharyngitis
ja  : >2 Punkte UND Kontakt zu StrepA-Pharyngitis

Ansonsten Abstrich/Schnelltest je nach Relevanz.
');

-- --------------------------------------------------------------
delete from clin.keyword_expansion where keyword = 'score-McIsaac-StrepA_Tonsillitis';

insert into clin.keyword_expansion (
	fk_staff,
	keyword,
	expansion
) values (
	null,
	'score-McIsaac-StrepA_Tonsillitis',
'McIsaac-Score: Antibiose bei Halsschmerz ?
------------------------------------------
(gültig > 3 Jahre)

1: Fieber in Anamnese (> 38°)
1: fehlender Husten
1: vordere Halslymphknoten geschwollen
1: Tonsillenexsudate oder -schwellung
1: Alter < 15 Jahre
-1: Alter > 45 Jahre

Wahrscheinlichkeit von Strep-A im Rachenabstrich ?

4-5: 50%
  3: 35%
  2: 17%
  1: 10%
 <1:  1%

Antibiose ?

nein: <3 Punkte und KEIN Kontakt zu StrepA-Pharyngitis
ja  : >2 Punkte UND Kontakt zu StrepA-Pharyngitis

Ansonsten Abstrich/Schnelltest je nach Relevanz.
');

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v11-clin-keyword_expansion-data.sql,v $', '$Revision: 1.3 $');

-- ==============================================================
