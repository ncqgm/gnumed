-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: 
-- 
-- ==============================================================
-- $Id: v9-clin-keyword_expansion-data.sql,v 1.2 2008-07-22 13:56:29 ncq Exp $
-- $Revision: 1.2 $

-- --------------------------------------------------------------
--set default_transaction_read_only to off;
\set ON_ERROR_STOP 1

set client_encoding to utf8;

-- --------------------------------------------------------------
delete from clin.keyword_expansion where keyword = '$$kuss';

insert into clin.keyword_expansion (
	fk_staff,
	keyword,
	expansion
) values (
	null,
	'$$kuss',
'Kindliche Unbehagen- und Schmerz-Skala
[Dtsch Arztebl 2008; 105(24-29): 511-22]
----------------------------------------------
Weinen
 0 - gar nicht
 1 - stöhnen, jammern, wimmern
 2 - schreien
Gesichtsausdruck
 0 - entspannt, lächelnd
 1 - Mund verzerrt
 2 - Mund und Augen grimassieren
Rumpfhaltung
 0 - neutral
 1 - unstet
 2 - aufbäumen, krümmen
Beinhaltung
 0 - neutral
 1 - strampelnd, tretend
 2 - an den Körper gezogen
Motorische Unruhe
 0 - nicht vorhanden
 1 - mäßig
 2 - ruhelos
----------------------------------------------
Summe:

- bis Ende des 4.Lebensjahres
- Beobachtung 15 Sekunden
- pro Gruppe eine Aussage
- ab 4 Punkte Analgesiebedarf
- schlafendes Kind = kein Analgesiebedarf'
);


delete from clin.keyword_expansion where keyword = '**gnumed';

insert into clin.keyword_expansion (
	fk_staff,
	keyword,
	expansion
) values (
	null,
	'***gnumed',
'Congrats, you found the GNUmed text expansion
Easter egg. You are entitled to one year of free
GNUmed upgrades.

Please refer to
  http://www.catb.org/jargon/html/E/Easter-egg.html
for further enlightenment. '
);

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v9-clin-keyword_expansion-data.sql,v $', '$Revision: 1.2 $');

-- ==============================================================
-- $Log: v9-clin-keyword_expansion-data.sql,v $
-- Revision 1.2  2008-07-22 13:56:29  ncq
-- - typo
--
-- Revision 1.1  2008/07/15 15:23:15  ncq
-- - new
--
--