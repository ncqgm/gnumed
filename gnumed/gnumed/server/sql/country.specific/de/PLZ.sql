-- GnuMed

-- author: Karsten Hilbert <Karsten.Hilbert@gmx.net>
-- license: GPL
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/country.specific/de/PLZ.sql,v $
-- $Revision: 1.12 $

-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

set client_encoding to 'LATIN1';
-- ===================================================================
delete from dem.urb where id_state = (select id from dem.state where code='SN' and country='DE');
delete from dem.state where country='DE';

-- Deutschland (Bundesländer)
insert into dem.state (code, country, name) values ('BW', 'DE', 'Baden-Württemberg');
insert into dem.state (code, country, name) values ('BY', 'DE', 'Bayern');
insert into dem.state (code, country, name) values ('BE', 'DE', 'Berlin');
insert into dem.state (code, country, name) values ('BB', 'DE', 'Brandenburg');
insert into dem.state (code, country, name) values ('HB', 'DE', 'Bremen');
insert into dem.state (code, country, name) values ('HH', 'DE', 'Hamburg');
insert into dem.state (code, country, name) values ('HE', 'DE', 'Hessen');
insert into dem.state (code, country, name) values ('MV', 'DE', 'Mecklenburg-Vorpommern');
insert into dem.state (code, country, name) values ('NI', 'DE', 'Niedersachsen');
insert into dem.state (code, country, name) values ('NW', 'DE', 'Nordrhein-Westfalen');
insert into dem.state (code, country, name) values ('RP', 'DE', 'Rheinland-Pfalz');
insert into dem.state (code, country, name) values ('SL', 'DE', 'Saarland');
insert into dem.state (code, country, name) values ('SN', 'DE', 'Sachsen');
insert into dem.state (code, country, name) values ('ST', 'DE', 'Sachsen-Anhalt');
insert into dem.state (code, country, name) values ('SH', 'DE', 'Schleswig-Holstein');
insert into dem.state (code, country, name) values ('TH', 'DE', 'Thüringen');

-- Österreich (Bundesländer)
insert into dem.state (code, country, name) values ('Wien', 'AT', 'Wien');				-- Vienna
insert into dem.state (code, country, name) values ('Tirol', 'AT', 'Tirol');			-- the Tyrol
insert into dem.state (code, country, name) values ('OÖ', 'AT', 'Oberösterreich');		-- Upper Austria
insert into dem.state (code, country, name) values ('NÖ', 'AT', 'Niederösterreich');	-- Lower Austria
insert into dem.state (code, country, name) values ('Stmk', 'AT', 'Steiermark');		-- Styria
insert into dem.state (code, country, name) values ('Sbg', 'AT', 'Salzburg');
insert into dem.state (code, country, name) values ('Vlbg', 'AT', 'Vorarlberg');
insert into dem.state (code, country, name) values ('Bgld', 'AT', 'Burgenland');
insert into dem.state (code, country, name) values ('Ktn', 'AT', 'Kärnten');			-- Carinthia

-- jo, wos is jetz dös ?
--INSERT into dem.state(code, country, name) VALUES ('BU','AT',i18n('Burgenland'));
--INSERT into dem.state(code, country, name) VALUES ('CA','AT',i18n('Carinthia'));
--INSERT into dem.state(code, country, name) VALUES ('NI','AT',i18n('Niederoesterreich'));
--INSERT into dem.state(code, country, name) VALUES ('OB','AT',i18n('Oberoesterreich'));
--INSERT into dem.state(code, country, name) VALUES ('SA','AT',i18n('Salzburg'));
--INSERT into dem.state(code, country, name) VALUES ('ST','AT',i18n('Steiermark'));
--INSERT into dem.state(code, country, name) VALUES ('TI','AT',i18n('Tirol'));
--INSERT into dem.state(code, country, name) VALUES ('VO','AT',i18n('Vorarlberg'));
--INSERT into dem.state(code, country, name) VALUES ('WI','AT',i18n('Wien'));

select dem.gm_upd_default_states();

------------------
-- Groß Särchen --
------------------
insert into dem.urb (id_state, name, postcode) values (
	(select id from dem.state where code = 'SN' and country='DE'),
	'Groß Särchen',
	'02999'
);

-------------
-- Leipzig --
-------------
-- no street
insert into dem.urb (id_state, postcode, name) values (
	(select id from dem.state where code = 'SN' and country = 'DE'),
	'04318',
	'Leipzig'
);

insert into dem.urb (id_state, postcode, name) values (
	(select id from dem.state where code = 'SN' and country = 'DE'),
	'04317',
	'Leipzig'
);

-- streets
insert into dem.street (
	id_urb,
	name,
	suburb,
	postcode
) values (
	(select id from dem.urb where name='Leipzig' limit 1),
	'Zum Kleingartenpark',
	'Sellerhausen',
	'04318'
);

insert into dem.street (id_urb, name, postcode) values (
	(select id from dem.urb where name='Leipzig' limit 1),
	'Riebeckstraße',
	'04317'
);

insert into dem.street (id_urb, name, postcode) values (
	(select id from dem.urb where name='Leipzig' limit 1),
	'Lange Reihe',
	'04299'
);

insert into dem.street (id_urb, name, postcode) values (
	(select id from dem.urb where name='Leipzig' limit 1),
	'Ferdinand-Jost-Straße',
	'04299'
);

insert into dem.street (
	id_urb,
	name,
	suburb,
	postcode
) values (
	(select id from dem.urb where name='Leipzig' limit 1),
	'Schildberger Weg',
	'Mockau',
	'04357'
);

insert into dem.street (id_urb, name, postcode) values (
	(select id from dem.urb where name='Leipzig' limit 1),
	'Wurzener Straße',
	'04315'
);

insert into dem.street (
	id_urb,
	name,
	suburb,
	postcode
) values (
	(select id from dem.urb where name='Leipzig' limit 1),
	'Wurzener Straße',
	'Sellerhausen',
	'04318'
);

insert into dem.street (id_urb, name, postcode) values (
	(select id from dem.urb where name='Leipzig' limit 1),
	'Eilenburger Straße',
	'04317'
);

insert into dem.street (
	id_urb,
	name,
	suburb,
	postcode
) values (
	(select id from dem.urb where name='Leipzig' limit 1),
	'Cunnersdorfer Straße',
	'Sellerhausen',
	'04318'
);

-- ===================================================================
-- do simple revision tracking
delete from gm_schema_revision where filename = '$RCSfile: PLZ.sql,v $';
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: PLZ.sql,v $', '$Revision: 1.12 $');

-- =============================================
-- $Log: PLZ.sql,v $
-- Revision 1.12  2006-01-06 10:12:02  ncq
-- - add missing grants
-- - add_table_for_audit() now in "audit" schema
-- - demographics now in "dem" schema
-- - add view v_inds4vaccine
-- - move staff_role from clinical into demographics
-- - put add_coded_term() into "clin" schema
-- - put German things into "de_de" schema
--
-- Revision 1.11  2005/10/19 11:29:09  ncq
-- - when selecting state pks must give country, too, or else duplicates exist
--
-- Revision 1.10  2005/09/25 17:52:09  ncq
-- - add commented out alternative state information for AT
--
-- Revision 1.9  2005/09/19 16:26:07  ncq
-- - update default states
--
-- Revision 1.8  2005/07/14 21:31:43  ncq
-- - partially use improved schema revision tracking
--
-- Revision 1.7  2005/06/10 07:21:35  ncq
-- - better docs
--
-- Revision 1.6  2005/06/07 20:59:18  ncq
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
