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
Mindestens 2 Symptome für mindestes 3 Monat im letzten halbe Jahr.

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
select gm.log_script_insertion('$RCSfile: v14-clin-keyword_expansion-data.sql,v $', '$Revision: 1.3 $');

-- ==============================================================
