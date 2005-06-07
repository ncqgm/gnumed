-- GnuMed

-- author: Karsten Hilbert <Karsten.Hilbert@gmx.net>
-- license: GPL
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/country.specific/de/PLZ.sql,v $
-- $Revision: 1.6 $

-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

set client_encoding to 'LATIN1';
-- ===================================================================
delete from urb where id_state = (select id from state where code='SN');
delete from state where country='DE';

-- Bundesländer
insert into state (code, country, name) values ('BW', 'DE', 'Baden-Württemberg');
insert into state (code, country, name) values ('BY', 'DE', 'Bayern');
insert into state (code, country, name) values ('BE', 'DE', 'Berlin');
insert into state (code, country, name) values ('BB', 'DE', 'Brandenburg');
insert into state (code, country, name) values ('HB', 'DE', 'Bremen');
insert into state (code, country, name) values ('HH', 'DE', 'Hamburg');
insert into state (code, country, name) values ('HE', 'DE', 'Hessen');
insert into state (code, country, name) values ('MV', 'DE', 'Mecklenburg-Vorpommern');
insert into state (code, country, name) values ('NI', 'DE', 'Niedersachsen');
insert into state (code, country, name) values ('NW', 'DE', 'Nordrhein-Westfalen');
insert into state (code, country, name) values ('RP', 'DE', 'Rheinland-Pfalz');
insert into state (code, country, name) values ('SL', 'DE', 'Saarland');
insert into state (code, country, name) values ('SN', 'DE', 'Sachsen');
insert into state (code, country, name) values ('ST', 'DE', 'Sachsen-Anhalt');
insert into state (code, country, name) values ('SH', 'DE', 'Schleswig-Holstein');
insert into state (code, country, name) values ('TH', 'DE', 'Thüringen');

-- Österreich
insert into state (code, country, name) values ('Wien', 'AT', 'Wien');				-- Vienna
insert into state (code, country, name) values ('Tirol', 'AT', 'Tirol');			-- the Tyrol
insert into state (code, country, name) values ('OÖ', 'AT', 'Oberösterreich');		-- Upper Austria
insert into state (code, country, name) values ('NÖ', 'AT', 'Niederösterreich');	-- Lower Austria
insert into state (code, country, name) values ('Stmk', 'AT', 'Steiermark');		-- Styria
insert into state (code, country, name) values ('Sbg', 'AT', 'Salzburg');
insert into state (code, country, name) values ('Vlbg', 'AT', 'Vorarlberg');
insert into state (code, country, name) values ('Bgld', 'AT', 'Burgenland');
insert into state (code, country, name) values ('Ktn', 'AT', 'Kärnten');			-- Carinthia

------------------
-- Groß Särchen --
------------------
insert into urb (id_state, name, postcode) values (
	(select id from state where code = 'SN'),
	'Groß Särchen',
	'02999'
);

-------------
-- Leipzig --
-------------
-- no street
insert into urb (id_state, postcode, name) values (
	(select id from state where code = 'SN'),
	'04318',
	'Leipzig'
);

insert into urb (id_state, postcode, name) values (
	(select id from state where code = 'SN'),
	'04317',
	'Leipzig'
);

-- streets
insert into street (
	id_urb,
	name,
	suburb,
	postcode
) values (
	(select id from urb where name='Leipzig' limit 1),
	'Zum Kleingartenpark',
	'Sellerhausen',
	'04318'
);

insert into street (id_urb, name, postcode) values (
	(select id from urb where name='Leipzig' limit 1),
	'Riebeckstraße',
	'04317'
);

insert into street (id_urb, name, postcode) values (
	(select id from urb where name='Leipzig' limit 1),
	'Lange Reihe',
	'04299'
);

insert into street (id_urb, name, postcode) values (
	(select id from urb where name='Leipzig' limit 1),
	'Ferdinand-Jost-Straße',
	'04299'
);

insert into street (
	id_urb,
	name,
	suburb,
	postcode
) values (
	(select id from urb where name='Leipzig' limit 1),
	'Schildberger Weg',
	'Mockau',
	'04357'
);

insert into street (id_urb, name, postcode) values (
	(select id from urb where name='Leipzig' limit 1),
	'Wurzener Straße',
	'04315'
);

insert into street (
	id_urb,
	name,
	suburb,
	postcode
) values (
	(select id from urb where name='Leipzig' limit 1),
	'Wurzener Straße',
	'Sellerhausen',
	'04318'
);

insert into street (id_urb, name, postcode) values (
	(select id from urb where name='Leipzig' limit 1),
	'Eilenburger Straße',
	'04317'
);

-- ===================================================================
-- do simple revision tracking
delete from gm_schema_revision where filename = '$RCSfile: PLZ.sql,v $';
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: PLZ.sql,v $', '$Revision: 1.6 $');

-- =============================================
-- $Log: PLZ.sql,v $
-- Revision 1.6  2005-06-07 20:59:18  ncq
-- - Austrian states
--
-- Revision 1.5  2005/05/24 19:44:31  ncq
-- - use proper state abbreviations
--
-- Revision 1.4  2005/05/17 08:17:53  ncq
-- - Bundesländer
--
-- Revision 1.3  2004/09/20 21:17:39  ncq
-- - add a few suburbs
--
-- Revision 1.2  2004/04/07 18:16:06  ncq
-- - move grants into re-runnable scripts
-- - update *.conf accordingly
--
-- Revision 1.1  2003/12/29 15:15:01  uid66147
-- - a few German post codes
--
