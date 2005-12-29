-- Projekt GnuMed
-- Impfstoffe (Deutschland)

-- Quellen: Paul-Ehrlich-Institut, Beipackzettel der Hersteller

-- author: Karsten Hilbert <Karsten.Hilbert@gmx.net>
-- license: GPL
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/country.specific/de/Impfstoffe.sql,v $
-- $Revision: 1.25 $
-- =============================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

set client_encoding to 'LATIN1';
-- =============================================
-- Tetanus --
-------------
insert into clin.vaccine (
	id_route,
	trade_name,
	short_name,
	is_live,
	min_age,
	comment
) values (
	(select id from clin.vacc_route where abbreviation='i.m.'),
	'Tetasorbat SSW',
	'Tetanus',
	false,
	-- FIXME: check this
	'1 year'::interval,
	'Smith Kline Beecham'
);

-- link to indications
insert into clin.lnk_vaccine2inds (fk_vaccine, fk_indication)
values (currval('clin.vaccine_pk_seq'), (select id from clin.vacc_indication where description='tetanus'));

insert into clin.vaccine (
	id_route,
	trade_name,
	short_name,
	is_live,
	min_age,
	comment
) values (
	(select id from clin.vacc_route where abbreviation='i.m.'),
	'Td-pur',
	'Td',
	false,
	'6 years'::interval,
	'Chiron Behring'
);

-- link to indications
insert into clin.lnk_vaccine2inds (fk_vaccine, fk_indication)
values (currval('clin.vaccine_pk_seq'), (select id from clin.vacc_indication where description='tetanus'));

insert into clin.lnk_vaccine2inds (fk_vaccine, fk_indication)
values (currval('clin.vaccine_pk_seq'), (select id from clin.vacc_indication where description='diphtheria'));

-----------------
-- Hepatitis A --
-----------------
insert into clin.vaccine (
	id_route,
	trade_name,
	short_name,
	is_live,
	min_age,
	max_age,
	comment
) values (
	(select id from clin.vacc_route where abbreviation='i.m.'),
	'Havrix 720 Kinder',
	'HAV',
	false,
	'1 year'::interval,
	'15 years'::interval,
	'GlaxoSmithKline'
);

-- link to indications
insert into clin.lnk_vaccine2inds (fk_vaccine, fk_indication)
values (currval('clin.vaccine_pk_seq'), (select id from clin.vacc_indication where description='hepatitis A'));

insert into clin.vaccine (
	id_route,
	trade_name,
	short_name,
	is_live,
	min_age,
	comment
) values (
	(select id from clin.vacc_route where abbreviation='i.m.'),
	'Havrix 1440',
	'HAV',
	false,
	'15 years'::interval,
	'GlaxoSmithKline'
);

-- link to indications
insert into clin.lnk_vaccine2inds (fk_vaccine, fk_indication)
values (currval('clin.vaccine_pk_seq'), (select id from clin.vacc_indication where description='hepatitis A'));

-----------------
-- Hepatitis B --
-----------------
insert into clin.vaccine (
	id_route,
	trade_name,
	short_name,
	is_live,
	min_age,
	max_age,
	comment
) values (
	(select id from clin.vacc_route where abbreviation='i.m.'),
	'HBVAXPRO',
	'HBVAXPRO',
	false,
	'1 seconds'::interval,
	'15 years'::interval,
	'Aventis'
);

-- link to indications
insert into clin.lnk_vaccine2inds (fk_vaccine, fk_indication)
values (currval('clin.vaccine_pk_seq'), (select id from clin.vacc_indication where description='hepatitis B'));

------------------
-- Pneumokokken --
------------------
insert into clin.vaccine (
	id_route,
	trade_name,
	short_name,
	is_live,
	min_age,
	max_age,
	comment
) values (
	(select id from clin.vacc_route where abbreviation='i.m.'),
	'Prevenar',
	'Prevenar',
	false,
	'1 month'::interval,
	'23 months'::interval,
	'Wyeth Lederle, 7-valent, adsorbiert, Kreuzallergie Diphtherie-Toxoid'
);

-- link to indications
insert into clin.lnk_vaccine2inds (fk_vaccine, fk_indication)
values (currval('clin.vaccine_pk_seq'), (select id from clin.vacc_indication where description='pneumococcus'));

---------------
-- Influenza --
---------------
insert into clin.vaccine (
	id_route,
	trade_name,
	short_name,
	is_live,
	min_age,
	comment
) values (
	(select id from clin.vacc_route where abbreviation='i.m.'),
	'InfectoVac Flu 2003/2004',
	'Flu 03',
	false,
	'6 months'::interval,
	'nur gültig Halbjahr 2003/2004'
);

-- link to indications
insert into clin.lnk_vaccine2inds (fk_vaccine, fk_indication)
values (currval('clin.vaccine_pk_seq'), (select id from clin.vacc_indication where description='influenza'));


insert into clin.vaccine (
	id_route,
	trade_name,
	short_name,
	is_live,
	min_age,
	comment
) values (
	(select id from clin.vacc_route where abbreviation='i.m.'),
	'InfectoVac Flu 2004/2005',
	'Flu 04',
	false,
	'6 months'::interval,
	'- nur gültig Halbjahr 2004/2005,
	 - Kinder zwischen 6 und 35 Monaten mit 0.25ml impfen'
);

-- link to indications
insert into clin.lnk_vaccine2inds (fk_vaccine, fk_indication)
values (currval('clin.vaccine_pk_seq'), (select id from clin.vacc_indication where description='influenza'));

---------------
-- NeisVac C --
---------------
insert into clin.vaccine (
	id_route,
	trade_name,
	short_name,
	is_live,
	min_age,
	comment
) values (
	(select id from clin.vacc_route where abbreviation='i.m.'),
	'NeisVac-C, Meningokokken-C-Konjugat',
	'NeisVac-C',
	false,
	'2 months'::interval,
	'mit Tetanus-Toxoid konjugiert'
);

-- link to indications
insert into clin.lnk_vaccine2inds (fk_vaccine, fk_indication)
values (currval('clin.vaccine_pk_seq'), (select id from clin.vacc_indication where description='meningococcus C'));

---------------
-- Menjugate --
---------------
insert into clin.vaccine (
	id_route,
	trade_name,
	short_name,
	is_live,
	min_age,
	comment
) values (
	(select id from clin.vacc_route where abbreviation='i.m.'),
	'Menjugate, Meningokokken-C-Konjugat',
	'Menjugate',
	false,
	'2 months'::interval,
	'mit Diphtherie-Toxoid konjugiert, Chiron Behring'
);

-- link to indications
insert into clin.lnk_vaccine2inds (fk_vaccine, fk_indication)
values (currval('clin.vaccine_pk_seq'), (select id from clin.vacc_indication where description='meningococcus C'));

----------------
-- Meningitec --
----------------
insert into clin.vaccine (
	id_route,
	trade_name,
	short_name,
	is_live,
	min_age,
	comment
) values (
	(select id from clin.vacc_route where abbreviation='i.m.'),
	'Meningitec',
	'Meningitec',
	false,
	'2 months'::interval,
	'mit Diphtherie-Toxoid konjugiert, Chiron Behring'
);

-- link to indications
insert into clin.lnk_vaccine2inds (fk_vaccine, fk_indication)
values (currval('clin.vaccine_pk_seq'), (select id from clin.vacc_indication where description='meningococcus C'));


-------------
-- Repevax --
-------------
insert into clin.vaccine (
	id_route,
	trade_name,
	short_name,
	is_live,
	min_age,
	comment
) values (
	(select id from clin.vacc_route where abbreviation='i.m.'),
	'REPEVAX',
	'Repevax',
	false,
	'10 years'::interval,
	'nicht zur Grundimmunisierung verwenden, Tetanus-Diphtherie-azellulärer-5-Komponenten-Pertussis-inaktivierter Poliomyelitis-Adsorbat-Impfstoff'
);

-- link to indications
insert into clin.lnk_vaccine2inds (fk_vaccine, fk_indication)
values (currval('clin.vaccine_pk_seq'), (select id from clin.vacc_indication where description='tetanus'));

insert into clin.lnk_vaccine2inds (fk_vaccine, fk_indication)
values (currval('clin.vaccine_pk_seq'), (select id from clin.vacc_indication where description='diphtheria'));

insert into clin.lnk_vaccine2inds (fk_vaccine, fk_indication)
values (currval('clin.vaccine_pk_seq'), (select id from clin.vacc_indication where description='pertussis'));

insert into clin.lnk_vaccine2inds (fk_vaccine, fk_indication)
values (currval('clin.vaccine_pk_seq'), (select id from clin.vacc_indication where description='poliomyelitis'));

-------------
-- Revaxis --
-------------
insert into clin.vaccine (
	id_route,
	trade_name,
	short_name,
	is_live,
	min_age,
	comment
) values (
	(select id from clin.vacc_route where abbreviation='i.m.'),
	'REVAXIS',
	'Revaxis',
	false,
	'6 years'::interval,
	'nicht zur Grundimmunisierung verwenden, Tetanus-Diphtherie-inaktivierter Poliomyelitis-Adsorbat-Impfstoff'
);

-- link to indications
insert into clin.lnk_vaccine2inds (fk_vaccine, fk_indication)
values (currval('clin.vaccine_pk_seq'), (select id from clin.vacc_indication where description='tetanus'));

insert into clin.lnk_vaccine2inds (fk_vaccine, fk_indication)
values (currval('clin.vaccine_pk_seq'), (select id from clin.vacc_indication where description='diphtheria'));

insert into clin.lnk_vaccine2inds (fk_vaccine, fk_indication)
values (currval('clin.vaccine_pk_seq'), (select id from clin.vacc_indication where description='poliomyelitis'));

----------
-- FSME --
----------
insert into clin.vaccine (
	id_route,
	trade_name,
	short_name,
	is_live,
	min_age,
	max_age,
	comment
) values (
	(select id from clin.vacc_route where abbreviation='i.m.'),
	'FSME-IMMUN 0.25ml Junior',
	'FSME',
	false,
	'1 year'::interval,
	'16 years'::interval,
	''
);

-- link to indications
insert into clin.lnk_vaccine2inds (fk_vaccine, fk_indication)
values (currval('clin.vaccine_pk_seq'), (select id from clin.vacc_indication where description='tick-borne meningoencephalitis'));

insert into clin.vaccine (
	id_route,
	trade_name,
	short_name,
	is_live,
	min_age,
	max_age,
	comment
) values (
	(select id from clin.vacc_route where abbreviation='i.m.'),
	'Encepur Kinder',
	'Encepur K',
	false,
	'1 year'::interval,
	'12 years'::interval,
	''
);

-- link to indications
insert into clin.lnk_vaccine2inds (fk_vaccine, fk_indication)
values (currval('clin.vaccine_pk_seq'), (select id from clin.vacc_indication where description='tick-borne meningoencephalitis'));

-------------
-- Priorix --
-------------
insert into clin.vaccine (
	id_route,
	trade_name,
	short_name,
	is_live,
	min_age,
	max_age
) values (
	(select id from clin.vacc_route where abbreviation='i.m.'),
	'PRIORIX',
	'Priorix',
	true,
	'12 months'::interval,
	'23 months'::interval
);

-- link to indications
insert into clin.lnk_vaccine2inds (fk_vaccine, fk_indication)
values (currval('clin.vaccine_pk_seq'), (select id from clin.vacc_indication where description='measles'));

insert into clin.lnk_vaccine2inds (fk_vaccine, fk_indication)
values (currval('clin.vaccine_pk_seq'), (select id from clin.vacc_indication where description='mumps'));

insert into clin.lnk_vaccine2inds (fk_vaccine, fk_indication)
values (currval('clin.vaccine_pk_seq'), (select id from clin.vacc_indication where description='rubella'));

------------
-- Masern --
------------
insert into clin.vaccine (
	id_route,
	trade_name,
	short_name,
	is_live,
	min_age,
	comment
) values (
	(select id from clin.vacc_route where abbreviation='i.m.'),
	'Masern-Impfstoff Mérieux',
	'Masern',
	true,
	'12 months'::interval,
	'Masern-Impfstoff Mérieux'
);

-- link to indications
insert into clin.lnk_vaccine2inds (fk_vaccine, fk_indication)
values (currval('clin.vaccine_pk_seq'), (select id from clin.vacc_indication where description='measles'));

----------------------
-- Infanrix-IPV+Hib --
----------------------
insert into clin.vaccine (
	id_route,
	trade_name,
	short_name,
	is_live,
	min_age,
	max_age
) values (
	(select id from clin.vacc_route where abbreviation='i.m.'),
	'INFANRIX-IPV+HIB',
	'Infanrix',
	false,
	'2 months'::interval,
	'5 years'::interval
);

-- link to indications
insert into clin.lnk_vaccine2inds (fk_vaccine, fk_indication)
values (currval('clin.vaccine_pk_seq'), (select id from clin.vacc_indication where description='tetanus'));

insert into clin.lnk_vaccine2inds (fk_vaccine, fk_indication)
values (currval('clin.vaccine_pk_seq'), (select id from clin.vacc_indication where description='diphtheria'));

insert into clin.lnk_vaccine2inds (fk_vaccine, fk_indication)
values (currval('clin.vaccine_pk_seq'), (select id from clin.vacc_indication where description='pertussis'));

insert into clin.lnk_vaccine2inds (fk_vaccine, fk_indication)
values (currval('clin.vaccine_pk_seq'), (select id from clin.vacc_indication where description='poliomyelitis'));

insert into clin.lnk_vaccine2inds (fk_vaccine, fk_indication)
values (currval('clin.vaccine_pk_seq'), (select id from clin.vacc_indication where description='haemophilus influenzae b'));

-------------
-- Act-HiB --
-------------
insert into clin.vaccine (
	id_route,
	trade_name,
	short_name,
	is_live,
	min_age,
	max_age
) values (
	(select id from clin.vacc_route where abbreviation='i.m.'),
	'Act-HiB',
	'HiB',
	false,
	'2 months'::interval,
	'5 years'::interval
);

-- link to indications
insert into clin.lnk_vaccine2inds (fk_vaccine, fk_indication)
values (currval('clin.vaccine_pk_seq'), (select id from clin.vacc_indication where description='haemophilus influenzae b'));

--------------
-- Pentavac --
--------------
insert into clin.vaccine (
	id_route,
	trade_name,
	short_name,
	is_live,
	min_age,
	max_age
) values (
	(select id from clin.vacc_route where abbreviation='i.m.'),
	'PentaVac',
	'PentaVac',
	false,
	'2 months'::interval,
	'5 years'::interval
);

-- link to indications
insert into clin.lnk_vaccine2inds (fk_vaccine, fk_indication)
values (currval('clin.vaccine_pk_seq'), (select id from clin.vacc_indication where description='tetanus'));

insert into clin.lnk_vaccine2inds (fk_vaccine, fk_indication)
values (currval('clin.vaccine_pk_seq'), (select id from clin.vacc_indication where description='diphtheria'));

insert into clin.lnk_vaccine2inds (fk_vaccine, fk_indication)
values (currval('clin.vaccine_pk_seq'), (select id from clin.vacc_indication where description='pertussis'));

insert into clin.lnk_vaccine2inds (fk_vaccine, fk_indication)
values (currval('clin.vaccine_pk_seq'), (select id from clin.vacc_indication where description='poliomyelitis'));

insert into clin.lnk_vaccine2inds (fk_vaccine, fk_indication)
values (currval('clin.vaccine_pk_seq'), (select id from clin.vacc_indication where description='haemophilus influenzae b'));

-----------------
-- IPV Mérieux --
-----------------
insert into clin.vaccine (
	id_route,
	trade_name,
	short_name,
	is_live,
	min_age
) values (
	(select id from clin.vacc_route where abbreviation='i.m.'),
	'IPV Mérieux',
	'IPV',
	false,
	'2 months'::interval
);

-- link to indication
insert into clin.lnk_vaccine2inds (fk_vaccine, fk_indication)
values (currval('clin.vaccine_pk_seq'), (select id from clin.vacc_indication where description='poliomyelitis'));

-- =============================================
-- do simple revision tracking
delete from gm_schema_revision where filename = '$RCSfile: Impfstoffe.sql,v $';
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: Impfstoffe.sql,v $', '$Revision: 1.25 $');

-- =============================================
-- $Log: Impfstoffe.sql,v $
-- Revision 1.25  2005-12-29 21:48:09  ncq
-- - clin.vaccine.id -> pk
-- - remove clin.vaccine.last_batch_no
-- - add clin.vaccine_batches
-- - adjust test data and country data
--
-- Revision 1.24  2005/11/25 15:07:28  ncq
-- - create schema "clin" and move all things clinical into it
--
-- Revision 1.23  2005/09/19 16:38:52  ncq
-- - adjust to removed is_core from gm_schema_revision
--
-- Revision 1.22  2005/07/14 21:31:43  ncq
-- - partially use improved schema revision tracking
--
-- Revision 1.21  2005/04/03 09:29:57  ncq
-- - when using non-ascii chars must specify encoding ...
--
-- Revision 1.20  2004/12/18 09:56:34  ncq
-- - cleanup
--
-- Revision 1.19  2004/10/01 11:44:51  ncq
-- - InfectoVac Flu 2004/2005
--
-- Revision 1.18  2004/09/10 10:57:45  ncq
-- - IPV Merieux
--
-- Revision 1.17  2004/08/04 10:05:43  ncq
-- - added Meningitec
--
-- Revision 1.16  2004/06/25 10:27:18  ncq
-- - Revaxis/Masern-Impfstoff/Act-HiB
--
-- Revision 1.15  2004/04/30 09:21:54  ncq
-- - min_age must be > 0 years
--
-- Revision 1.14  2004/04/27 17:06:46  ncq
-- - HBVAXPRO
--
-- Revision 1.13  2004/04/19 09:27:34  ncq
-- - add PentaVac
--
-- Revision 1.12  2004/04/14 13:33:04  ncq
-- - need to adjust min_interval for seq_no=1 after tightening interval checks
--
-- Revision 1.11  2004/03/27 18:36:28  ncq
-- - cleanup, added FSME vaccine
--
-- Revision 1.10  2004/02/09 23:57:39  ncq
-- - Priorix (MMR)
--
-- Revision 1.9  2004/01/26 20:18:37  ncq
-- - diphtheria, not diphtherie
--
-- Revision 1.8  2004/01/22 23:45:12  ncq
-- - REPEVAX/FSME Junior
--
-- Revision 1.7  2004/01/18 21:58:22  ncq
-- - remove is_licensed
-- - add Havrix 1440
--
-- Revision 1.6  2004/01/12 13:31:34  ncq
-- - better short_name(s)
-- - add Menjugate
--
-- Revision 1.5  2003/12/29 15:59:24  uid66147
-- - NeisVac C
--
-- Revision 1.4  2003/11/30 10:34:35  ncq
-- - InfectoVac Flu 2003/4
--
-- Revision 1.3  2003/11/26 22:44:46  ncq
-- - added Prvenar
--
-- Revision 1.2  2003/11/22 14:55:51  ncq
-- - Havrix 720 Kinder
--
-- Revision 1.1  2003/10/31 23:15:06  ncq
-- - first version
--
