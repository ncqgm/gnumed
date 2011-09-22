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
delete from clin.keyword_expansion where keyword = 'score-HEMORR²HAGES';

insert into clin.keyword_expansion (
	fk_staff,
	keyword,
	expansion
) values (
	null,
	'score-HEMORR²HAGES',
'HEMORR²HAGES: Blutungsrisiko unter OAK
--------------------------------------
Am Heart J. 2006 Mar;151(3):713-9.

1 H epatische oder Nierenerkrankung
1 E thanolabusus
1 M alignom
1 O ld patient (> 75 Jahre)
1 R eduzierte Thrombozytenzahl/-funktion
2 R²ekurrente (frühere) große Blutung
1 H ypertonie (unkontrolliert)
1 A nämie
1 G enetische Faktoren
1 E xzessives Sturzrisiko
1 S Schlaganfall in der Anamnese
--------------------------------------
Summe   Rate großer Blutungen
        pro 100 Patientenjahre
 0          1.9
 1          2.5
 2          5.3
 3          8.4
 4         10.4
>4         12.3
');

-- --------------------------------------------------------------
select gm.log_script_insertion('v16-clin-keyword_expansion-data.sql', 'v16');

-- ==============================================================
