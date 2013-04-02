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
delete from ref.keyword_expansion where keyword = 'score-Epworth_Sleepiness_Scale';

insert into ref.keyword_expansion (
	fk_staff,
	keyword,
	textual_data
) values (
	null,
	'score-Epworth_Sleepiness_Scale',
'Epworth Sleepiness Scale
------------------------
Murray W. Johns: "Daytime sleepiness, snoring, and obstructive sleep apnea. The Epworth Sleepiness Scale." Chest. Vol. 103, Nr. 1, 1993, S. 30-36, doi:10.1378/chest.103.1.30.

Recently, how likely are you to doze off/fall asleep (rather
than "just" feeling tired) during the following situations ?

0 - would never doze
1 - slight chance
2 - moderate chance
3 - high chance

$[0-3]$ Sitting and reading
$[0-3]$ Watching TV
$[0-3]$ Sitting, inactive in public place (meeting, theatre)
$[0-3]$ As passenger in car for 1 hour w/o a break
$[0-3]$ Lying down to rest in after when circumstances permit
$[0-3]$ Sitting and talking to someone
$[0-3]$ Sitting quietly after a lunch without alcohol
$[0-3]$ In a car, while stopped for a few minutes in traffic

Sum: $[Sum]$

	- 85% of healthy patients: <10 points
	- Narcolepsy: Sensitivity ~100%, Specificity ~93%)
');

-- --------------------------------------------------------------
select gm.log_script_insertion('v18-ref-Epworth_Sleepiness_Scale_1997-fixup.sql', '18.2');
