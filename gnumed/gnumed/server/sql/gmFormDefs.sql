-- ===================================================
-- GnuMed form templates related tables

-- author: Karsten Hilbert <Karsten.Hilbert@gmx.net>
-- author: Ian Haywood <>
-- license: GPL
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmFormDefs.sql,v $
-- $Revision: 1.7 $

-- Note: this is office related while gmFormData.sql is clinical content
-- ===================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- ===================================================
create table papersizes (
	pk serial primary key,
	name text unique not null,
	size point not null
);

comment on column papersizes.size is '(cm, cm)';

-- paper sizes taken from the GhostScript man pages
-- FIXME: move to some *-data.sql script
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
create table form_defs (
	pk serial primary key,
	name_short text not null,
	name_long text not null,
	revision text not null,
	template text,
	engine char default 'T' not null check (engine in ('T', 'L')),
	in_use boolean not null default true,
	electronic boolean not null default false,
	flags varchar (100) [],
	unique (name_short, name_long),
	unique (name_long, revision)
) inherits (audit_fields);

select add_table_for_audit('form_defs');

comment on table form_defs is
	'form definitions';
comment on column form_defs.name_short is
	'a short name for use in a GUI or some such';
comment on column form_defs.name_long is
	'a long name unambigously describing the form';
comment on column form_defs.revision is
	'GnuMed internal form def version, may
	 occur if we rolled out a faulty form def';
comment on column form_defs.template is
	'the template complete with placeholders in
	 the format accepted by the engine defined in
	 form_defs.engine';
comment on column form_defs.engine is
	'the business layer forms engine used
	 to process this form, currently:
	 - T: plain text
	 - L: LaTeX';
comment on column form_defs.in_use is
	'whether this template is currently actively
	 used in a given practice';
comment on column form_defs.electronic is
	'?: Ian';
comment on column form_defs.flags is
	'?: Ian';

-- ===================================================
create table lnk_form2discipline (
	pk serial primary key,
	fk_form integer references form_defs(pk),
	discipline text
);

comment on table lnk_form2discipline is
	'the discipline which uses this form. This maps to
	 gmDemographics.occupation for individuals,
	 gmDemographics.category for organisations';

-- ===================================================
create table form_print_defs (
	pk serial primary key,
	fk_form integer
		unique
		not null
		references form_defs(pk),
	fk_papersize integer
		not null
		references papersizes (pk),
	offset_top integer not null default 0,
	offset_left integer not null default 0,
	pages integer not null default 1,
	printer text not null,
	tray text not null,
	manual_feed bool not null default false,
	papertype text not null,
	eject_direction character(1) not null,
	orientation character(1) not null
);

comment on column form_print_defs.offset_top is
	'in mm - and yes, they do change even within one type of form,
	 but we do not want to change the offset for all the fields in that case';
comment on column form_print_defs.papertype is
	'type of paper such as "watermarked rose", mainly for user interaction on manual_feed==true';

-- =============================================
-- do simple schema revision tracking
\i gmSchemaRevision.sql
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmFormDefs.sql,v $', '$Revision: 1.7 $');

-- =============================================
-- * do we need "form_defs.iso_countrycode" ?
-- * good/bad decision to use point/box PG data type ?

-- =============================================
-- $Log: gmFormDefs.sql,v $
-- Revision 1.7  2004-03-08 17:04:23  ncq
-- - rewritten after discussion with Ian
--
-- Revision 1.6  2004/03/07 22:42:08  ncq
-- - just some cleanup
--
-- Revision 1.5  2004/03/07 13:19:18  ihaywood
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
