-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v10-clin-keyword_expansion-data.sql,v 1.2 2009-02-25 09:38:49 ncq Exp $
-- $Revision: 1.2 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
delete from clin.keyword_expansion where keyword = 'score-TVT-Wells';

insert into clin.keyword_expansion (
	fk_staff,
	keyword,
	expansion
) values (
	null,
	'score-TVT-Wells',
'Wells-Score: Wahrscheinlichkeit akute tiefe Beinvenenthrombose
--------------------------------------------------------------
+1: maligne Erkrankung vorhanden oder Therapie in den letzten 6 Monaten;
+1: Lähmung/kürzliche Immobilisation der Beine;
+1: Bettruhe > 3d oder große OP < 12 Wo;
+1: Schmerz/Verhärtung entlang der tiefen Venen;
+1: Schwellung des gesamten Beins;
+1: US-Schwellung > 3cm (10cm unterhalb des Knie):
    li: cm, re: cm;
+1: eindrückbares Ödem des betroffenen Beines;
+1: dilatierte oberflächliche Venen (nicht Varizen);
-2: andere Diagnose (...) wahrscheinlicher;

Summe:
 < 1  niedrige Wahrscheinlichkeit
 1-2  mittlere Wahrscheinlichkeit
 > 3  hohe Wahrscheinlichkeit
--------------------------------------------------------------
D-Dimer-Schnelltest:
D-Dimer quantitativ:

Vd. US-Thrombose links/rechts
');

-- --------------------------------------------------------------
delete from clin.keyword_expansion where keyword = 'score-TVT-AMUSE';

insert into clin.keyword_expansion (
	fk_staff,
	keyword,
	expansion
) values (
	null,
	'score-TVT-AMUSE',
'AMUSE-Score: Wahrscheinlichkeit akute tiefe Beinvenenthrombose

klinischer Verdacht:

	Rötung, Schwellung oder Schmerz

1  männlich
1  hormonelle Kontrazeption
1  Karzinom im zurückliegenden halben Jahr
1  Operation im zurückliegenden Monat
1  kein Trauma der unteren Extremität
1  Dilatation kollateraler Beinvenen
1  Umfangsdifferenz > 2,9 cm (10 cm unter Tibiaplateau)
     re:  cm
     li:  cm
6  erhöhtes D-Dimer:
-------------------
   Summe (> 3 => zur Sonographie)
');

-- --------------------------------------------------------------
delete from clin.keyword_expansion where keyword = 'score-gcs';

insert into clin.keyword_expansion (
	fk_staff,
	keyword,
	expansion
) values (
	null,
	'score-gcs',
'Glasgow Coma Scale
------------------
- ab 3 Jahre
- bei normalerweise orientierten Personen

   Augen öffnen
   ------------
4: spontan
3: auf Aufforderung
2: auf Schmerzreiz
1: keine Reaktion

   Verbale Kommunikation
   ---------------------
5: konversationsfähig, orientiert
4: konversationsfähig, desorientiert
3: unzusammenhängende Worte
2: unverständliche Laute
1: keine verbale Reaktion

   Motorische Reaktion
   -------------------
6: befolgt Aufforderungen
5: gezielte Schmerzabwehr
4: ungezielte Schmerzabwehr
3: auf Schmerzreiz abnormale Beugeabwehr
2: auf Schmerzreiz Strecksynergismen
1: keine Reaktion auf Schmerzreiz

14 - 15 leicht, 9 - 13 mittel, 3 - 8 schwer
');

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v10-clin-keyword_expansion-data.sql,v $', '$Revision: 1.2 $');

-- ==============================================================
-- $Log: v10-clin-keyword_expansion-data.sql,v $
-- Revision 1.2  2009-02-25 09:38:49  ncq
-- - AMUSE score for TVT
--
-- Revision 1.1  2009/02/17 10:49:28  ncq
-- - add Wells and GCS
--
--