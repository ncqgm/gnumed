-- Projekt GnuMed
-- Impfstoffe (Deutschland)

-- Quellen: Paul-Ehrlich-Institut, Beipackzettel der Hersteller

-- author: Karsten Hilbert <Karsten.Hilbert@gmx.net>
-- license: GPL
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/country.specific/de/Impfstoffe.sql,v $
-- $Revision: 1.1 $
-- =============================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- =============================================
-- Tetanus --
-------------
insert into vaccine (
	id_route,
	trade_name,
	short_name,
	is_live,
	is_licensed,
	min_age,
	comment
) values (
	(select id from vacc_route where abbreviation='i.m.'),
	'Tetasorbat SSW',
	'Tetasorbat',
	false,
	true,
	-- FIXME: check this
	'1 year'::interval,
	'Smith Kline Beecham'
);

-- link to indications
insert into lnk_vaccine2inds (fk_vaccine, fk_indication)
values (currval('vaccine_id_seq'), (select id from vacc_indication where description='tetanus'));

insert into vaccine (
	id_route,
	trade_name,
	short_name,
	is_live,
	is_licensed,
	min_age,
	comment
) values (
	(select id from vacc_route where abbreviation='i.m.'),
	'Td-pur',
	'Td-pur',
	false,
	true,
	'6 years'::interval,
	'Chiron Behring'
);

-- link to indications
insert into lnk_vaccine2inds (fk_vaccine, fk_indication)
values (currval('vaccine_id_seq'), (select id from vacc_indication where description='tetanus'));

insert into lnk_vaccine2inds (fk_vaccine, fk_indication)
values (currval('vaccine_id_seq'), (select id from vacc_indication where description='diphtheria'));

-- =============================================
-- do simple revision tracking
delete from gm_schema_revision where filename = '$RCSfile: Impfstoffe.sql,v $';
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: Impfstoffe.sql,v $', '$Revision: 1.1 $');

-- =============================================
-- $Log: Impfstoffe.sql,v $
-- Revision 1.1  2003-10-31 23:15:06  ncq
-- - first version
--
