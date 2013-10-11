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
delete from ref.keyword_expansion where keyword = 'score-ATRIA-bleeding_risk';

insert into ref.keyword_expansion (
	fk_staff,
	keyword,
	textual_data
) values (
	null,
	'score-ATRIA-bleeding_risk',
'ATRIA - bleeding risk in oral anti-coagulation for atrial fibrillation
----------------------------------------------------------------------
Fang MC et al; A new risk scheme to predict warfarin-associated hemorrhage.
The ATRIA-Study. J Am Coll Cardiol. 2011;58:395-401.

$[0/3]$ anemia
$[0/3]$ severe renal disease (dialysis or eGFR < 30ml/min)
$[0/2]$ age > 74 years
$[0/1]$ any prior hemorrhage diagnosis
$[0/1]$ diagnosed hypertension

Sum: $[calculate sum]$

	< 4: low risk ( <1% hemorrhages/year )
	> 5: high risk
';

-- --------------------------------------------------------------
delete from ref.keyword_expansion where keyword = 'score-AUDIT_alcohol_disorder_screening';

insert into ref.keyword_expansion (
	fk_staff,
	keyword,
	textual_data
) values (
	null,
	'score-AUDIT_alcohol_disorder_screening',
'AUDIT - Alcohol Use Disorders Identification Test
-------------------------------------------------
Alcohol Use Disorders Identification Test, Fragebogen der WHO, Babor, De la Fuente, Saunders & Grant, 1992

1. Wie oft nehmen Sie ein alkoholisches Getränk zu sich?

	$[0-4]$

 0 = Nie
 1 = 1 x im Monat oder weniger
 2 = 2 - 4 x im Monat
 3 = 2 - 4 x in der Woche
 4 = 4 x oder mehr die Woche

2. Wenn Sie alkoholische Getränke zu sich nehmen, wie viel trinken Sie dann
typischerweise an einem Tag? (Ein alkoholhaltiges Getränk ist z.B. ein kleines Glas
oder eine Flasche Bier, ein kleines Glas Wein oder Sekt, ein einfacher Schnaps oder
ein Glas Likör.)

	$[0-4]$

 0 = 1 oder 2
 1 = 3 oder 4
 2 = 5 oder 6
 3 = 7 bis 9
 4 = 10 oder mehr

3. Wie oft trinken Sie 6 oder mehr Gläser Alkohol bei einer Gelegenheit?

	$[0-4]$

 0 = Nie
 1 = Weniger als 1 x im Monat
 2 = 1 x im Monat
 3 = 1 x in der Woche
 4 = Täglich oder fast täglich

4. Wie oft haben Sie in den letzten 12 Monaten erlebt, dass Sie nicht mehr mit dem
Trinken aufhören konnten, nachdem Sie einmal begonnen hatten?

	$[0-4]$

 0 = Nie
 1 = Weniger als 1 x im Monat
 2 = 1 x im Monat
 3 = 1 x in der Woche
 4 = Täglich oder fast täglich

5. Wie oft passierte es in den letzten 12 Monaten, dass Sie wegen des Trinkens
Erwartungen, die man in der Familie, im Freundeskreis und im Berufsleben an Sie
hatte, nicht mehr erfüllen konnten?

	$[0-4]$

 0 = Nie
 1 = Weniger als 1 x im Monat
 2 = 1 x im Monat
 3 = 1 x in der Woche
 4 = Täglich oder fast täglich

6. Wie oft brauchten Sie während der letzten 12 Monate am Morgen ein alkoholisches
Getränk, um sich nach einem Abend mit viel Alkoholgenuss wieder fit zu fühlen?

	$[0-4]$

 0 = Nie
 1 = Weniger als 1 x im Monat
 2 = 1 x im Monat
 3 = 1 x in der Woche
 4 = Täglich oder fast täglich

7. Wie oft hatten Sie während der letzten 12 Monate wegen Ihrer Trinkgewohnheiten
Schuldgefühle oder Gewissensbisse?

	$[0-4]$

 0 = Nie
 1 = Weniger als 1 x im Monat
 2 = 1 x im Monat
 3 = 1 x in der Woche
 4 = Täglich oder fast täglich

8. Wie oft haben Sie sich während der letzten 12 Monate nicht mehr an den
vorangegangenen Abend erinnern können, weil Sie getrunken hatten?

	$[0-4]$

 0 = Nie
 1 = Weniger als 1 x im Monat
 2 = 1 x im Monat
 3 = 1 x in der Woche
 4 = Täglich oder fast täglich

9. Haben Sie sich oder eine andere Person unter Alkoholeinfluss schon einmal
verletzt?

	$[0/2/4]$

 0 = Nein
 2 = Ja, aber nicht im letzten Jahr
 4 = Ja, während des letzten Jahres

10. Hat ein Verwandter, Freund oder auch ein Arzt schon einmal Bedenken wegen Ihres
Trinkverhaltens geäußert oder vorgeschlagen, dass Sie Ihren Alkoholkonsum
einschränken?

	$[0/2/4]$

 0 = Nein
 2 = Ja, aber nicht im letzten Jahr
 4 = Ja, während des letzten Jahres

Summe: $[Summe]$

Eine Punktzahl von 8 (bzw. 5 bei Frauen) oder mehr weist laut
AUDIT auf einen gefährlichen und schädlichen Alkoholkonsum hin.
Auch eine Punktzahl von 5 oder mehr bei Männern kann unter
Umständen mit einem erhöhten Risiko einher gehen.'
);

-- --------------------------------------------------------------
select gm.log_script_insertion('v19-ref-AUDIT_alcohol.sql', '19.0');
