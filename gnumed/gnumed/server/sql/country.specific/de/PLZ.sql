-- GnuMed

-- author: Karsten Hilbert <Karsten.Hilbert@gmx.net>
-- license: GPL
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/country.specific/de/PLZ.sql,v $
-- $Revision: 1.2 $

-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

set client_encoding to 'LATIN1';
-- ===================================================================
delete from urb where id_state = (select id from state where code='SAC');
delete from state where country='DE';

-- Sachsen
insert into state (code, country, name) values ('SAC', 'DE', 'Sachsen');

------------------
-- Groﬂ S‰rchen --
------------------
insert into urb (id_state, name, postcode) values (
	(select id from state where code = 'SAC'),
	'Groﬂ S‰rchen',
	'02999'
);

-------------
-- Leipzig --
-------------
-- no street
insert into urb (id_state, postcode, name) values (
	(select id from state where code = 'SAC'),
	'04318',
	'Leipzig'
);

insert into urb (id_state, postcode, name) values (
	(select id from state where code = 'SAC'),
	'04317',
	'Leipzig'
);

-- streets
insert into street (id_urb, name, postcode) values (
	(select id from urb where name='Leipzig' limit 1),
	'Zum Kleingartenpark',
	'04318'
);

insert into street (id_urb, name, postcode) values (
	(select id from urb where name='Leipzig' limit 1),
	'Riebeckstraﬂe',
	'04317'
);

insert into street (id_urb, name, postcode) values (
	(select id from urb where name='Leipzig' limit 1),
	'Lange Reihe',
	'04299'
);

insert into street (id_urb, name, postcode) values (
	(select id from urb where name='Leipzig' limit 1),
	'Ferdinand-Jost-Straﬂe',
	'04299'
);

insert into street (id_urb, name, postcode) values (
	(select id from urb where name='Leipzig' limit 1),
	'Schildberger Weg',
	'04357'
);

insert into street (id_urb, name, postcode) values (
	(select id from urb where name='Leipzig' limit 1),
	'Wurzener Straﬂe',
	'04315'
);

insert into street (id_urb, name, postcode) values (
	(select id from urb where name='Leipzig' limit 1),
	'Wurzener Straﬂe',
	'04318'
);

insert into street (id_urb, name, postcode) values (
	(select id from urb where name='Leipzig' limit 1),
	'Eilenburger Straﬂe',
	'04317'
);

-- ===================================================================
-- do simple revision tracking
delete from gm_schema_revision where filename = '$RCSfile: PLZ.sql,v $';
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: PLZ.sql,v $', '$Revision: 1.2 $');

-- =============================================
-- $Log: PLZ.sql,v $
-- Revision 1.2  2004-04-07 18:16:06  ncq
-- - move grants into re-runnable scripts
-- - update *.conf accordingly
--
-- Revision 1.1  2003/12/29 15:15:01  uid66147
-- - a few German post codes
--
