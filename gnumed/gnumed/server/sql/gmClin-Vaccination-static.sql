-- Project: GNUmed - vaccination related tables
-- ===================================================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmClin-Vaccination-static.sql,v $
-- $Id: gmClin-Vaccination-static.sql,v 1.4 2006-03-04 16:14:10 ncq Exp $
-- license: GPL
-- author: Ian Haywood, Karsten Hilbert, Richard Terry

-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- ============================================
-- vaccination tables
-- ============================================
create table clin.vacc_indication (
	id serial primary key,
	description text unique not null
) inherits (audit.audit_fields);

-- --------------------------------------------
create table clin.vacc_route (
	id serial primary key,
	abbreviation text unique not null,
	description text unique not null
) inherits (audit.audit_fields);

-- --------------------------------------------
-- FIXME: this table should eventually point to entries
-- FIXME: in the clin.* drug data cache table
create table clin.vaccine (
	pk serial primary key,
	id_route integer
		not null
		references clin.vacc_route(id)
		default 1,
	trade_name text unique not null,
	short_name text not null,
	is_live boolean
		not null
		default false,
	min_age interval
		not null
		check(min_age between '1 second'::interval and '150 years'::interval),
	max_age interval
		not null
		default '5555 years'::interval
		check (
			(max_age between min_age and '150 years'::interval)
				or
			(max_age = '5555 years'::interval)
		),
	comment text,
	unique (trade_name, short_name)
) inherits (audit.audit_fields);

-- FIXME: this table eventually needs to go into
-- FIXME: stock inventory tracking
create table clin.vaccine_batches (
	pk serial primary key,
	fk_vaccine integer
		not null
		references clin.vaccine(pk)
		on update cascade
		on delete cascade,
	batch_no text
		unique
		not null
) inherits (audit.audit_fields);

-- --------------------------------------------
create table clin.lnk_vaccine2inds (
	id serial primary key,
	fk_vaccine integer
		not null
		references clin.vaccine(pk)
		on delete cascade
		on update cascade,
	fk_indication integer
		not null
		references clin.vacc_indication(id)
		on delete cascade
		on update cascade,
	unique (fk_vaccine, fk_indication)
) inherits (audit.audit_fields);

-- --------------------------------------------
create table clin.vaccination_course (
	pk serial primary key,
	fk_recommended_by integer
		default null,
	fk_indication integer
		not null
		references clin.vacc_indication(id)
		on update cascade
		on delete restrict,
	is_active boolean
		not null
		default true,
	comment text
) inherits (audit.audit_fields);

-- --------------------------------------------
create table clin.vaccination_course_constraint (
	pk serial primary key,
	description text
		unique
		not null
) inherits (audit.audit_fields);

-- --------------------------------------------
create table clin.lnk_constraint2vacc_course (
	pk serial primary key,
	fk_vaccination_course integer
		not null
		references clin.vaccination_course(pk)
		on update cascade
		on delete cascade,
	fk_constraint integer
		not null
		references clin.vaccination_course_constraint(pk)
		on update cascade
		on delete cascade,
	unique (fk_vaccination_course, fk_constraint)
) inherits (audit.audit_fields);

-- --------------------------------------------
create table clin.vaccination_schedule (
	pk serial primary key,
	name text
		unique
		not null,
	comment text
) inherits (audit.audit_fields);

-- --------------------------------------------
create table clin.lnk_vaccination_course2schedule (
	pk serial primary key,
	fk_course integer
		unique
		not null
		references clin.vaccination_course(pk)
		on update cascade
		on delete restrict,
	fk_schedule integer
		not null
		references clin.vaccination_schedule(pk)
		on update cascade
		on delete cascade
) inherits (audit.audit_fields);

-- --------------------------------------------
create table clin.lnk_pat2vacc_course (
	pk serial primary key,
	fk_patient integer
		not null
		references clin.xlnk_identity(xfk_identity)
		on update cascade
		on delete cascade,
	fk_course integer
		not null
		references clin.vaccination_course(pk)
		on update cascade
		on delete restrict,
	unique(fk_patient, fk_course)
) inherits (audit.audit_fields);

-- --------------------------------------------
create table clin.vaccination_definition (
	id serial primary key,
	fk_course integer
		not null
		references clin.vaccination_course(pk)
		on delete cascade
		on update cascade,
	is_booster boolean
		not null
		default false,
	seq_no integer
		default null,
	min_age_due interval
		not null
		check (min_age_due between '1 second'::interval and '150 years'::interval),
	max_age_due interval
		not null
		default '5555'::interval
		check (
			(max_age_due between min_age_due and '150 years'::interval)
				or 
			(max_age_due = '5555'::interval)
		),
	min_interval interval
		default null,
	comment text,
	unique(fk_course, seq_no)
--	,unique(fk_course, is_booster)
) inherits (audit.audit_fields);

-- --------------------------------------------
create table clin.vaccination (
	id serial primary key,
	-- isn't this redundant ?
	fk_patient integer
		not null
		references clin.xlnk_identity(xfk_identity)
		on update cascade
		on delete restrict,
	fk_provider integer
		not null,
	fk_vaccine integer
		not null
		references clin.vaccine(pk)
		on delete restrict
		on update cascade,
	site text
		default 'not recorded',
	batch_no text
		not null
		default 'not recorded',
	unique (fk_patient, fk_vaccine, clin_when)
) inherits (clin.clin_root_item);
-- Richard tells us that "refused" should go into progress note

alter table clin.vaccination add foreign key (fk_encounter)
		references clin.encounter(pk)
		on update cascade
		on delete restrict;
alter table clin.vaccination add foreign key (fk_episode)
		references clin.episode(pk)
		on update cascade
		on delete restrict;
alter table clin.vaccination alter column soap_cat set default 'p';

-- --------------------------------------------
-- this table will be even larger than vaccination ...
--create table clin.lnk_vacc2vacc_def (
--	pk serial primary key,
--	fk_vaccination integer
--		not null
--		references clin.vaccination(id)
--		on delete cascade
--		on update cascade,
--	fk_vacc_def integer
--		not null
--		references clin.vacc_def(id)
--		on delete restrict
--		on update cascade,
--	unique (fk_vaccination, fk_vacc_def)
--) inherits (audit.audit_fields);

--comment on column clin.lnk_vacc2vacc_def.fk_vacc_def is
--	'the vaccination event a particular
--	 vaccination is supposed to cover, allows to
--	 link out-of-band vaccinations into courses,
--	 not currently used';

-- ===================================================================
-- do simple schema revision tracking
select log_script_insertion('$RCSfile: gmClin-Vaccination-static.sql,v $', '$Revision: 1.4 $');

-- ===================================================================
-- $Log: gmClin-Vaccination-static.sql,v $
-- Revision 1.4  2006-03-04 16:14:10  ncq
-- - audit many more tables
-- - rename previous vacc_regime to vaccination_course
-- - add real vaccination_schedule and lnk_vaccination_course2schedule
--
-- Revision 1.3  2006/02/27 11:23:26  ncq
-- - better constrain min_age/max_age in schedule and vaccine
-- - use "5555 years" not NULL to mean infinite age, PG infinite::interval is in the works
--
-- Revision 1.2  2006/02/19 13:45:05  ncq
-- - move the rest of the dynamic vacc stuff from gmClinicalViews.sql
--   into gmClin-Vaccination-dynamic.sql
-- - add vaccination schedule constraint enumeration data
-- - add is_active to clin.vacc_regime
-- - add clin.vacc_regime_constraint
-- - add clin.lnk_constraint2vacc_reg
-- - proper grants
--
-- Revision 1.1  2006/02/08 15:15:39  ncq
-- - factor our vaccination stuff into its own set of files
-- - remove clin.lnk_vacc_ind2code in favour of clin.coded_term usage
-- - improve comments as discussed on the list
--
--
