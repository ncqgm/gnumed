-- Project: GNUmed - vaccination related tables
-- ===================================================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmClin-Vaccination-static.sql,v $
-- $Revision: 1.2 $
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
		check(min_age > interval '0 seconds'),
	max_age interval
		default null
		check((max_age is null) or (max_age >= min_age)),
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
);

-- --------------------------------------------
create table clin.vacc_regime (
	id serial primary key,
	name text unique not null,
	fk_recommended_by integer,
	fk_indication integer
		not null
		references clin.vacc_indication(id)
		on update cascade
		on delete restrict,
	is_active boolean
		not null
		default true, 
	comment text,
	unique(fk_recommended_by, fk_indication, name)
) inherits (audit.audit_fields);

-- --------------------------------------------
create table clin.vacc_regime_constraint (
	pk serial primary key,
	description text
		unique
		not null
) inherits (audit.audit_fields);

-- --------------------------------------------
create table clin.lnk_constraint2vacc_reg (
	pk serial primary key,
	fk_vacc_regime integer
		not null
		references clin.vacc_regime(id)
		on update cascade
		on delete cascade,
	fk_constraint integer
		not null
		references clin.vacc_regime_constraint(pk)
		on update cascade
		on delete cascade
) inherits (audit.audit_fields);

-- --------------------------------------------
create table clin.lnk_pat2vacc_reg (
	pk serial primary key,
	fk_patient integer
		not null
		references clin.xlnk_identity(xfk_identity)
		on update cascade
		on delete cascade,
	fk_regime integer
		not null
		references clin.vacc_regime(id)
		on update cascade
		on delete restrict,
	unique(fk_patient, fk_regime)
) inherits (audit.audit_fields);

-- --------------------------------------------
create table clin.vacc_def (
	id serial primary key,
	fk_regime integer
		not null
		references clin.vacc_regime(id)
		on delete cascade
		on update cascade,
	is_booster boolean
		not null
		default false,
	seq_no integer
		default null,
	min_age_due interval
		not null
		check (min_age_due > '0 seconds'::interval),
	max_age_due interval
		default null
		check ((max_age_due is null) or (max_age_due >= min_age_due)),
	min_interval interval
		default null,
	comment text,
	unique(fk_regime, seq_no)
--	,unique(fk_regime, is_booster)
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
--	 link out-of-band vaccinations into regimes,
--	 not currently used';

-- ===================================================================
-- do simple schema revision tracking
select log_script_insertion('$RCSfile: gmClin-Vaccination-static.sql,v $', '$Revision: 1.2 $');

-- ===================================================================
-- $Log: gmClin-Vaccination-static.sql,v $
-- Revision 1.2  2006-02-19 13:45:05  ncq
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
