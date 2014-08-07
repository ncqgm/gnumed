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
delete from ref.keyword_expansion where keyword = 'score-TVT-Wells';

insert into ref.keyword_expansion (
	fk_staff,
	keyword,
	textual_data
) values (
	null,
	'score-TVT-Wells',
'Wells-Score: Wahrscheinlichkeit akute tiefe Beinvenenthrombose
--------------------------------------------------------------
Geersing GJ, et al.: Exclusion of deep vein thrombosis using the
Wells rule in clinically important subgroups: individual patient
data meta-analysis, BMJ 2014; 348:g1340; DOI: 10.1136/bmj.g1340

Initialverdacht US-Thrombose: $[links/rechts]$

$[ja/nein]$ aktive maligne Erkrankung ?
  ja: apparative Diagnostik einleiten
      (Score<2 & D-Dimer negativ: Falsch-Negativ = 2.2%)

  nein:

$[0/1]$: maligne Erkrankung vorhanden oder Therapie in den letzten 6 Monaten;
$[0/1]$: Paralyse/Parese/kürzliche Immobilisation der Beine;
$[0/1]$: Bettruhe > 3d oder große OP < 12 Wo;
$[0/1]$: Schmerz/Verhärtung entlang der tiefen Venen;
$[0/1]$: Schwellung des gesamten Beins;
$[0/1]$: US-Schwellung > 3cm (10cm unterhalb Tub.tibiae):
    li: $[links in cm]$ cm, re: $[rechts in cm]$ cm;
$[0/1]$: eindrückbares Ödem des betroffenen Beines;
$[0/1]$: dilatierte oberflächliche Kollateralvenen (nicht Varizen);
$[0/-2]$: andere Diagnose ($[Differentialdiagnose]$) genauso wahrscheinlich;

erweiterter Score (bei Z.n.TVT):

$[0/1]$: TVT in der Anamnese

Summe: $[Summe]$

  < 2  niedrige Wahrscheinlichkeit -> D-Dimer
 ab 2  nicht-niedrige Wahrscheinlichkeit -> Sonographie/Angiographie

D-Dimer-Schnelltest: $[D-Dimer-ST negativ ?]$
D-Dimer quantitativ: $[D-Dimer-Wert]$

 einfacher Score<2 & D-Dimer negativ: Ausschluß Thrombose (Falsch-Negativ = 1.2%)

 erweiterter Score<2 & D-Dimer negativ: Ausschluß Thrombose (Falsch-Negativ = 1%)

--------------------------------------------------------------
Beurteilung:

Thromboseausschluß: $[ja/nein]$
');

-- --------------------------------------------------------------
delete from ref.keyword_expansion where keyword = 'score-LE-Wells';

insert into ref.keyword_expansion (
	fk_staff,
	keyword,
	textual_data
) values (
	null,
	'score-LE-Wells',
'Wells-Score: Wahrscheinlichkeit Lungenembolie
--------------------------------------------------------------
http://flexikon.doccheck.com/de/Wells-Score

$[0/3]$: klinische Zeichen für eine TVT;
$[0/3]$: andere Diagnosen sind unwahrscheinlich;
$[0/1,5]$: Tachykardie > 100 Hz
$[0/1,5]$: Bettruhe > 3d oder große OP < 12 Wo;
$[0/1,5]$: TVT oder LE in der Anamnese
$[0/1]$: Hämoptyse
$[0/1]$: Neoplasie

Summe: $[Summe]$

 < 2 Punkte: geringe Wahrscheinlichkeit
 2-6 Punkte: mittlere Wahrscheinlichkeit
 > 6 Punkte: hohe Wahrscheinlichkeit

 Score  < 4  -> D-Dimer
 Score ab 4  -> Bildgebung

D-Dimer-Schnelltest: $[D-Dimer-ST negativ ?]$
D-Dimer quantitativ: $[D-Dimer-Wert]$

 Score<4 & D-Dimer negativ: Ausschluß Thrombose

Beurteilung:

Ausschluß LE: $[ja/nein]$
');

-- --------------------------------------------------------------
select gm.log_script_insertion('v20-Wells_Score', '20.0');
