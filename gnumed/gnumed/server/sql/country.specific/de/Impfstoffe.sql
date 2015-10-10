-- Projekt GNUmed
-- Impfstoffe (Deutschland)

-- Quellen: Paul-Ehrlich-Institut, Beipackzettel der Hersteller

-- author: Karsten Hilbert <Karsten.Hilbert@gmx.net>
-- license: GPL v2 or later
-- =============================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

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
-- Typhus --
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
	'Typhim Vi',
	'Typhus',
	false,
	'2 years'::interval,
	'unter 2 Jahren bildet sich kein adäquater Titer'
);

-- link to indications
insert into clin.lnk_vaccine2inds (fk_vaccine, fk_indication)
values (currval('clin.vaccine_pk_seq'), (select id from clin.vacc_indication where description='salmonella typhi'));

-- =============================================
-- do simple revision tracking
select log_script_insertion('$RCSfile: Impfstoffe.sql,v $', '$Revision: 1.26 $');
