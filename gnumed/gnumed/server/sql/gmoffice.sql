-- DDL structure of 'office' tables: forms, letters, accountings, billing
-- Copyright 2002 by Dr. Horst Herb
-- This is free software in the sense of the General Public License (GPL)
-- For details regarding GPL licensing see http://gnu.org
--
-- usage:
--	log into psql (database gnumed OR drugs)  as administrator
--	run the script from the prompt with "\i gmoffice.sql"
--=====================================================================

-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmoffice.sql,v $
-- $Revision: 1.1 $ $Date: 2002-12-03 02:50:19 $ $Author: ihaywood $
-- ============================================================
-- $Log: gmoffice.sql,v $
-- Revision 1.1  2002-12-03 02:50:19  ihaywood
-- new office schema: tables for printing forms
--
--
--
-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

create table papersizes
(
	id serial,
	name varchar (10),
	length float,
	width float
);

comment on column papersizes.length is '(cm)';
comment on column papersizes.width is '(cm)';


insert into papersizes (name, length, width) values ('A0', 83.9611, 118.816);
insert into papersizes (name, length, width) values ('A1', 59.4078, 83.9611);
insert into papersizes (name, length, width) values ('A2', 41.9806, 59.4078);
insert into papersizes (name, length, width) values ('A3', 29.7039, 41.9806);
insert into papersizes (name, length, width) values ('A4', 20.9903, 29.7039);
insert into papersizes (name, length, width) values ('A5', 14.8519, 20.9903);
insert into papersizes (name, length, width) values ('A6', 10.4775, 14.8519);
insert into papersizes (name, length, width) values ('A7', 7.40833, 10.4775);
insert into papersizes (name, length, width) values ('A8', 5.22111, 7.40833);
insert into papersizes (name, length, width) values ('A9', 3.70417, 5.22111);
insert into papersizes (name, length, width) values ('A10', 2.61056, 3.70417);
insert into papersizes (name, length, width) values ('B0', 100.048, 141.393);
insert into papersizes (name, length, width) values ('B1', 70.6967 ,100.048);
insert into papersizes (name, length, width) values ('B2',  50.0239,70.6967);
insert into papersizes (name, length, width) values ('B3',  35.3483,50.0239);
insert into papersizes (name, length, width) values ('B4',  25.0119,35.3483);
insert into papersizes (name, length, width) values ( 'B5',  17.6742,25.0119);
insert into papersizes (name, length, width) values ('archA', 22.86,30.48);
insert into papersizes (name, length, width) values ('archB', 30.48,45.72);
insert into papersizes (name, length, width) values ('archC', 45.72,60.96);
insert into papersizes (name, length, width) values ('archD', 60.96,91.44);
insert into papersizes (name, length, width) values ('archE', 91.44,121.92);
insert into papersizes (name, length, width) values ('flsa',  21.59,33.02);
insert into papersizes (name, length, width) values ('flse',  21.59,33.02);
insert into papersizes (name, length, width) values ('halfletter',13.97,21.59);
insert into papersizes (name, length, width) values ('note',   19.05,  25.4);
insert into papersizes (name, length, width) values ('letter', 21.59, 27.94);
insert into papersizes (name, length, width) values ('legal',  21.59, 35.56);
insert into papersizes (name, length, width) values ('11x17', 27.94, 43.18);
insert into papersizes (name, length, width) values ('ledger',43.18, 27.94);
-- paper sizes from the GostScript manpages.



create table forms
(
	iso_countrycode char (2),
	type char check (type in ('s', 'p', 'r', 'a', 'w', 'u')),
	name varchar (50),
	id_papersize integer references papersizes (id),
	pages integer,
	fontsize integer check (fontsize > 8 and fontsize < 50)
	font char check (font in ('t', 'g', 'r'),
	bold boolean
);

comment on table forms is 'the various forms used in practive.';
comment on column forms.iso_coutrycode is 
'the two letter counry code of the country in which this form is used.';

comment on column forms.type is '
the type of the form. This determines the variables accessible to
the form queries (see below).
s: script. PATIENTID, SCRIPTID
p: pathology slip. REQUESTID: table in gmclinical, PATIENTID  
r: radiology slip. REQUESTID: table in gmclinical, PATIENTID
a: accounting. BEGIN, END: dates defining accounting period
w: wage. BEGIN, END, PATIENTID: wage period and employee
u: general user-defined form. PATIENTID is patient-id. ';

comment on column forms.name is 
'name of the form, usu. the issuing authority: "PBS", "WorkCover", etc.';

comment on column forms.id_papersize is
'papersize A4, etc.';

comment on column forms.font is
't = typewriter, g = gothic (i.e sans-serif) r=roman';

comment on column forms.bold is
'true if font bold';

create table queries
(
	id serial,
	name varchar (50),
	service varchar (25),
	query varchar (300)
);

comment on table queries is
'SQL queries used to fill form fields';
comment on column queries.name is
'name of quiery to identifiy to user';
comment on column queries.service is
'the service on which to execute query';
comment on column queries.query is
'the SQL SELECT statement to execute. Variables substituted as outlined in forms.type';

insert into queries (name, service, query) values ('begin', 'gmoffice', 'select BEGIN');
insert into queries (name, service, query) values ('end', 'gmoffice', 'select END');
insert into queries (name, service, query) values ('patient_name', 'gmidentity', 
'select firstnames || lastnames from names where active and id_identity = PATIENTID limit 1');
insert into queries (name, service, query) values ('patient_address', 'gmgis', 
'select from v_home_address where id = PATIENTID');
insert into queries (name, service, query) values ('patient_dob', 'gmidentity', 
'select dob from identity where id = PATIENTID');
insert into queries (name, service, query) values ('patient_age', 'gmidentity', 
'select age (dob) from identity where id = PATIENTID');
insert into queries (name, service, query) values ('patient_gender', 'gmidentity', 
'select case when gender in (''m'',''tm'') then ''maennlich'' when gender in (''f'' , ''tf'') 
then ''weiblich'' else ''unbekannt'' from identity where id = PATIENTID');
insert into queries (name, service, query) values ('', '', '');

create table formfield 
(
	id serial,
	id_form integer references forms (id),
	x integer,
	y integer,
	id_query integer references queries (id),
	wraparound integer
);

comment on column formfield.x is 'x-cordinate unit 720/inch';
comment on column formfield.y is 'y-cordinate unit 720/inch';
comment on column formfield.wraparound is 'wraparound for text, unit 720/inch';
