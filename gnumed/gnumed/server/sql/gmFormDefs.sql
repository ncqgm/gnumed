-- ===================================================
-- GnuMed form templates related tables

-- author: Karsten Hilbert <Karsten.Hilbert@gmx.net>
-- author: Ian Haywood <>
-- license: GPL
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmFormDefs.sql,v $
-- $Revision: 1.5 $

-- Note: this is office related while gmFormData.sql is clinical content

-- ===================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- ===================================================
create table papersizes (
	id serial primary key,
	name varchar (10),
	size point
);

comment on column papersizes.size is '(cm, cm)';

-- paper sizes taken from the GhostScript man pages
insert into papersizes (name, size) values ('A0', '(83.9611, 118.816)');
insert into papersizes (name, size) values ('A1', '(59.4078, 83.9611)');
insert into papersizes (name, size) values ('A2', '(41.9806, 59.4078)');
insert into papersizes (name, size) values ('A3', '(29.7039, 41.9806)');
insert into papersizes (name, size) values ('A4', '(20.9903, 29.7039)');
insert into papersizes (name, size) values ('A5', '(14.8519, 20.9903)');
insert into papersizes (name, size) values ('A6', '(10.4775, 14.8519)');
insert into papersizes (name, size) values ('A7', '(7.40833, 10.4775)');
insert into papersizes (name, size) values ('A8', '(5.22111, 7.40833)');
insert into papersizes (name, size) values ('A9', '(3.70417, 5.22111)');
insert into papersizes (name, size) values ('A10', '(2.61056, 3.70417)');
insert into papersizes (name, size) values ('B0', '(100.048, 141.393)');
insert into papersizes (name, size) values ('B1', '(70.6967 ,100.048)');
insert into papersizes (name, size) values ('B2', '(50.0239,70.6967)');
insert into papersizes (name, size) values ('B3', '(35.3483,50.0239)');
insert into papersizes (name, size) values ('B4', '(25.0119,35.3483)');
insert into papersizes (name, size) values ('B5', '(17.6742,25.0119)');
insert into papersizes (name, size) values ('archA', '(22.86,30.48)');
insert into papersizes (name, size) values ('archB', '(30.48,45.72)');
insert into papersizes (name, size) values ('archC', '(45.72,60.96)');
insert into papersizes (name, size) values ('archD', '(60.96,91.44)');
insert into papersizes (name, size) values ('archE', '(91.44,121.92)');
insert into papersizes (name, size) values ('flsa', '(21.59,33.02)');
insert into papersizes (name, size) values ('flse', '(21.59,33.02)');
insert into papersizes (name, size) values ('halfletter', '(13.97,21.59)');
insert into papersizes (name, size) values ('note', '(19.05,  25.4)');
insert into papersizes (name, size) values ('letter', '(21.59, 27.94)');
insert into papersizes (name, size) values ('legal', '(21.59, 35.56)');
insert into papersizes (name, size) values ('11x17', '(27.94, 43.18)');
insert into papersizes (name, size) values ('ledger', '(43.18, 27.94)');

-- ===================================================
-- form templates
-- ===================================================
create table form_types (
	id serial primary key,
	name_short varchar(10),
	name_long varchar(60),
	version varchar(30) unique not null,
	in_use bool,
	deprecated date,
	template text,
	electronic bool, 
	engine char default 'T' not null check (engine in ('T', 'L')),
	flags varchar (100) []
);
comment on table form_types is
	'metadata on forms';

comment on column form_types.engine is
'the business layer forms engine class to use for this form.
Currently only T=plain text, and L=LaTeX are defined';

create lnk_form2discipline (
	id_form integer references form_types (id),
	discipline text
);


comment on table lnk_form2discipline is
'the discipline which uses this form. This maps to
gmDemographics.occupation for indivuduals, gmDemographics.category for organisations';

-- ===================================================
create table form_print_defs (
	id serial primary key,
	id_papersize integer references papersizes (id),

	offset_top integer,
	offset_left integer,
	pages integer,
	printer varchar(20),
	tray varchar(10),
	manual_feed bool,
	papertype varchar(30),
	eject_direction character(1),
	orientation character(1)
);

comment on column form_print_defs.offset_top is
	'in mm - and yes, they do change even within one type of form,
	 but we do not want to change the offset for all the fields in that case';
comment on column form_print_defs.papertype is
	'type of paper such as "watermarked rose", mainly for user interaction on manual_feed==true';

-- ===================================================
create table form_field_queries (
	id serial primary key,
	name varchar (50),
	service varchar (25),
	query varchar (300)
);

comment on table form_field_queries is
	'SQL queries used to fill form fields';
comment on column form_field_queries.name is
	'name of query to identify to user';
comment on column form_field_queries.service is
	'the service on which to execute the query';
comment on column form_field_queries.query is
	'The SQL SELECT statement to execute. Variables to be substituted take
	the form of named string formatters such as ''%(identity.id)s'' (table.field).';

insert into form_field_queries (name, service, query) values (
	'patient_full_name', 'gmidentity', 'select firstnames || '' '' || lastnames from names where active and id_identity = ''%(identity.id)s'' limit 1;');
insert into form_field_queries (name, service, query) values (
	'patient_dob', 'gmidentity', 'select dob from identity where id = ''%(identity.id)s'';');
insert into form_field_queries (name, service, query) values (
	'patient_age', 'gmidentity', 'select age (dob) from identity where id = ''%(identity.id)s'';');
insert into form_field_queries (name, service, query) values (
	'patient_address', 'gmgis', 'select from v_home_address where id = ''%(identity.id)s'';');

-- ===================================================
create table form_fields (
	id serial primary key,
	id_form integer references form_types (id),
	id_query integer references form_field_queries (id),

	font varchar(10),
	pitch integer check (pitch > 7 and pitch < 50),
	page integer,
	dimensions box,
	lines integer,
	is_used bool,
	is_visible bool,
	is_stored bool,
	is_editable bool
);

comment on column form_fields.lines is
	'the number of lines that will fit into this field';
comment on column form_fields.is_used is
	'whether this field is printed/transmitted on/with the form';
comment on column form_fields.is_visible is
	'whether this field is visible on screen when filling in this form';
comment on column form_fields.is_stored is
	'whether values in this field will get stored when creating a form instance';
comment on column form_fields.is_editable is
	'whether values in this field can be edited before use of the form;
	if not they probably do not need to be stored either';

-- =============================================
-- do simple schema revision tracking
\i gmSchemaRevision.sql
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmFormDefs.sql,v $', '$Revision: 1.5 $');

-- =============================================
-- * do we need "form_types.iso_countrycode" ?
-- * good/bad decision to use point/box PG data type ?
-- * do we need "form_types.in_use_since date" ?
-- * "form_types.in_use/deprecated" are sort of redundant

-- =============================================
-- $Log: gmFormDefs.sql,v $
-- Revision 1.5  2004-03-07 13:19:18  ihaywood
-- more work on forms
--
-- Revision 1.4  2003/01/05 13:05:51  ncq
-- - schema_revision -> gm_schema_revision
--
-- Revision 1.3  2003/01/01 13:36:56  ncq
-- - in queries: string constants must be quoted by ''s
--
-- Revision 1.2  2003/01/01 00:21:25  ncq
-- - added flag is_editable to form field definition
--
-- Revision 1.1  2003/01/01 00:15:06  ncq
-- - this imports cleanly for me, please comment
--
