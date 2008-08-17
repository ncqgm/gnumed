-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
-- $Id: v9-i18n-translations.sql,v 1.1 2008-08-17 12:06:52 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

--set default_transaction_read_only to off

-- --------------------------------------------------------------
\unset ON_ERROR_STOP

-- de_DE
select i18n.upd_tx('de_DE', 'Albania', 'Albanien');
select i18n.upd_tx('de_DE', 'Algeria', 'Algerien');
select i18n.upd_tx('de_DE', 'American Samoa', 'Amerikanisch-Samoa');
select i18n.upd_tx('de_DE', 'Antarctica', 'Antarktis');
select i18n.upd_tx('de_DE', 'Antigua and Barbuda', 'Antigua und Barbados');
select i18n.upd_tx('de_DE', 'Argentina', 'Argentinien');
select i18n.upd_tx('de_DE', 'Armenia', 'Armenien');
select i18n.upd_tx('de_DE', 'Belgium', 'Belgien');
select i18n.upd_tx('de_DE', 'Bolivia', 'Bolivien');
select i18n.upd_tx('de_DE', 'Bosnia and Herzegovina', 'Bosnien und Herzegovina');
select i18n.upd_tx('de_DE', 'Brazil', 'Brasilien');
select i18n.upd_tx('de_DE', 'Bulgaria', 'Bulgarien');
select i18n.upd_tx('de_DE', 'Cambodia', 'Kambodscha');
select i18n.upd_tx('de_DE', 'Cameroon', 'Kamerun');
select i18n.upd_tx('de_DE', 'Chad', 'Tschad');
select i18n.upd_tx('de_DE', 'Christmas Island', 'Weihnachtsinseln');
select i18n.upd_tx('de_DE', 'Colombia', 'Kolumbien');
select i18n.upd_tx('de_DE', 'Comoros', 'Komoren');
select i18n.upd_tx('de_DE', 'Congo', 'Kongo');
select i18n.upd_tx('de_DE', 'Congo, The Democratic Republic', 'Demokratische Republik Kongo');
select i18n.upd_tx('de_DE', 'Cote D''Ivoire', 'Elfenbeinküste');
select i18n.upd_tx('de_DE', 'Croatia', 'Kroatien');
select i18n.upd_tx('de_DE', 'Cuba', 'Kuba');
select i18n.upd_tx('de_DE', 'Cyprus', 'Zypern');
select i18n.upd_tx('de_DE', 'Czech Republic', 'Tschechien');
select i18n.upd_tx('de_DE', 'Denmark', 'Dänemark');
select i18n.upd_tx('de_DE', 'Dominican Republic', 'Dominikanische Republik');
select i18n.upd_tx('de_DE', 'East Timor', 'Osttimor');
select i18n.upd_tx('de_DE', 'Ecuador', 'Ekuador');
select i18n.upd_tx('de_DE', 'Egypt', 'Ägypten');
select i18n.upd_tx('de_DE', 'Ethiopia', 'Äthiopien');
select i18n.upd_tx('de_DE', 'Finland', 'Finnland');
select i18n.upd_tx('de_DE', 'France', 'Frankreich');
select i18n.upd_tx('de_DE', 'Georgia', 'Georgien');
select i18n.upd_tx('de_DE', 'Greece', 'Griechenland');
select i18n.upd_tx('de_DE', 'Greenland', 'Grönland');
select i18n.upd_tx('de_DE', 'Holy See (Vatican City State)', 'Vatikanstadt');
select i18n.upd_tx('de_DE', 'Hungary', 'Ungarn');
select i18n.upd_tx('de_DE', 'Iceland', 'Island');
select i18n.upd_tx('de_DE', 'India', 'Indien');
select i18n.upd_tx('de_DE', 'Indonesia', 'Indonesion');
select i18n.upd_tx('de_DE', 'Iran, Islamic Republic Of', 'Islamische Republik Iran');
select i18n.upd_tx('de_DE', 'Iraq', 'Irak');
select i18n.upd_tx('de_DE', 'Ireland', 'Irland');
select i18n.upd_tx('de_DE', 'Italy', 'Italien');
select i18n.upd_tx('de_DE', 'Jamaica', 'Jamaika');
select i18n.upd_tx('de_DE', 'Jordan', 'Jordanien');
select i18n.upd_tx('de_DE', 'Kazakstan', 'Kasachstan');
select i18n.upd_tx('de_DE', 'Kenya', 'Kenia');
select i18n.upd_tx('de_DE', 'Korea, Democratic People''s Republic', 'Nordkorea');
select i18n.upd_tx('de_DE', 'Korea, Republic Of', 'Südkorea');
select i18n.upd_tx('de_DE', 'Kyrgyzstan', 'Kirgisien');
select i18n.upd_tx('de_DE', 'Lao People''s Democratic Republic', 'Laos');
select i18n.upd_tx('de_DE', 'Lebanon', 'Libanon');
select i18n.upd_tx('de_DE', 'Lithuania', 'Litauen');
select i18n.upd_tx('de_DE', 'Mauritania', 'Mauretanien');
select i18n.upd_tx('de_DE', 'Mexico', 'Mexiko');
select i18n.upd_tx('de_DE', 'Mongolia', 'Mongolei');
select i18n.upd_tx('de_DE', 'Morocco', 'Marokko');
select i18n.upd_tx('de_DE', 'Netherlands', 'Niederlanden');
select i18n.upd_tx('de_DE', 'Netherlands Antilles', 'Niederländische Antillen');
select i18n.upd_tx('de_DE', 'New Zealand', 'Neuseeland');
select i18n.upd_tx('de_DE', 'Norway', 'Norwegen');
select i18n.upd_tx('de_DE', 'Philippines', 'Philippinen');
select i18n.upd_tx('de_DE', 'Poland', 'Polen');
select i18n.upd_tx('de_DE', 'Romania', 'Rumänien');
select i18n.upd_tx('de_DE', 'Russian Federation', 'Russische Föderation');
select i18n.upd_tx('de_DE', 'Saudi Arabia', 'Saudi Arabien');
select i18n.upd_tx('de_DE', 'Seychelles', 'Seychellen');
select i18n.upd_tx('de_DE', 'Singapore', 'Singapur');
select i18n.upd_tx('de_DE', 'Slovakia', 'Slowakei');
select i18n.upd_tx('de_DE', 'Slovenia', 'Slowenien');
select i18n.upd_tx('de_DE', 'South Africa', 'Südafrika');
select i18n.upd_tx('de_DE', 'Sweden', 'Schweden');
select i18n.upd_tx('de_DE', 'Switzerland', 'Schweiz');
select i18n.upd_tx('de_DE', 'Syrian Arab Republic', 'Syrien');
select i18n.upd_tx('de_DE', 'Taiwan, Province Of China', 'Taiwan');
select i18n.upd_tx('de_DE', 'Tunisia', 'Tunesien');
select i18n.upd_tx('de_DE', 'Turkey', 'Türkei');
select i18n.upd_tx('de_DE', 'United Arab Emirates', 'Vereinigte Arabische Emirate');
select i18n.upd_tx('de_DE', 'United Kingdom', 'Großbritannien');
select i18n.upd_tx('de_DE', 'United States', 'Vereinigte Staaten von Amerika');
select i18n.upd_tx('de_DE', 'state/territory/province/region not available', 'Bundesland/Provinz/Region nicht verfügbar');
select i18n.upd_tx('de_DE', 'history of presenting complaint', 'Jetztanamnese');
select i18n.upd_tx('de_DE', 'psycho-social history', 'Sozialanamnese');
select i18n.upd_tx('de_DE', 'family history', 'Familienanamnese');
select i18n.upd_tx('de_DE', 'sexual history', 'Sexualanamnese');
select i18n.upd_tx('de_DE', 'diet', 'Ernährung');
select i18n.upd_tx('de_DE', 'housing', 'Unterkunft');
select i18n.upd_tx('de_DE', 'patient', 'Patient');
select i18n.upd_tx('de_DE', 'external org', 'externe Organisation');
select i18n.upd_tx('de_DE', 'your own practice', 'eigene Praxis');
select i18n.upd_tx('de_DE', 'wght', 'KG');
select i18n.upd_tx('de_DE', 'weight (body mass)', 'Gewicht (Masse)');
select i18n.upd_tx('de_DE', 'the patient''s weight (body mass to be accurate)', 'Patientengewicht (Körpermasse, genaugenommen)');
select i18n.upd_tx('de_DE', 'hght', 'Gr.');
select i18n.upd_tx('de_DE', 'height', 'Größe');
select i18n.upd_tx('de_DE', 'lying in infants, else standing, see result notes', 'Säuglinge liegend, sonst stehend, siehe Kommentar');
select i18n.upd_tx('de_DE', 'blood pressure', 'Blutdruck');
select i18n.upd_tx('de_DE', 'specifics attached to result record', 'Einzelheiten im Karteieintrag');
select i18n.upd_tx('de_DE', 'pulse', 'Puls');
select i18n.upd_tx('de_DE', 'pulse, periph.art.', 'Puls, periph.art.');
select i18n.upd_tx('de_DE', 'peripheral arterial pulse', 'peripher-arterieller Puls');
select i18n.upd_tx('de_DE', 'blood oxygen saturation', 'Sauerstoffsättigung (Blut)');
select i18n.upd_tx('de_DE', 'peripheral arterial blood oxygenization level, transduced', 'peripher-arterielle Blutsauerstoffsättigung, transduziert');
select i18n.upd_tx('de_DE', 'orally', 'oral');
select i18n.upd_tx('de_DE', 'cholera', 'Cholera');
select i18n.upd_tx('de_DE', 'rabies', 'Tollwut');
select i18n.upd_tx('de_DE', 'seasonal', 'saisonal');
select i18n.upd_tx('de_DE', 'administrative encounter', 'Verwaltungsakt');

\set ON_ERROR_STOP 1
-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v9-i18n-translations.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v9-i18n-translations.sql,v $
-- Revision 1.1  2008-08-17 12:06:52  ncq
-- - German
--
--