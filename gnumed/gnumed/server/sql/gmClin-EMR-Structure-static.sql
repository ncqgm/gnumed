-- Project: GNUmed - EMR structure related tables:
--		- health issues
--		- encounters
--		- episodes
-- ===================================================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmClin-EMR-Structure-static.sql,v $
-- $Revision: 1.3 $
-- license: GPL
-- author: Ian Haywood, Karsten Hilbert

-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- ===================================================================
create schema clin authorization "gm-dbo";

-- ===================================================================
create table clin.xlnk_identity (
	pk serial primary key,
	xfk_identity integer unique not null,
	pupic text unique not null,
	data text unique default null
) inherits (audit.audit_fields);

-- ===================================================================
-- generic EMR structure
-- ===================================================================
-- health issue tables
create table clin.health_issue (
	pk serial primary key,
	id_patient integer
		not null
		references clin.xlnk_identity(xfk_identity)
		on update cascade
		on delete restrict,
	description text
		not null
		default null,
	laterality varchar(2)
		default null
		check (laterality in (null, 's', 'd', 'sd', 'na')),
	age_noted interval
		default null,
	is_active boolean
		default true,
	clinically_relevant boolean
		default true,
	is_confidential boolean
		default false,
	is_cause_of_death boolean
		not null
		default false,
	unique (id_patient, description)
) inherits (audit.audit_fields);

-- FIXME: Richard also has is_operation, laterality

-- ===================================================================
-- episode related tables
create table clin.episode (
	pk serial primary key,
	fk_health_issue integer
		default null
		references clin.health_issue(pk)
		on update cascade
		on delete restrict,
	fk_patient integer
		default null
		references clin.xlnk_identity(xfk_identity)
		on update cascade
		on delete restrict,
	description text
		not null
		check (trim(description) != ''),
	is_open boolean
		default true
) inherits (audit.audit_fields);

-- ===================================================================
-- encounter related tables
create table clin.encounter_type (
	pk serial primary key,
	description text
		unique
		not null
);

-- -------------------------------------------------------------------
create table clin.encounter (
	pk serial primary key,
	fk_patient integer
		not null
		references clin.xlnk_identity(xfk_identity)
		on update cascade
		on delete restrict,
	fk_type integer
		not null
		default 1
		references clin.encounter_type(pk)
		on update cascade
		on delete restrict,
	fk_location integer,
	source_time_zone interval,
	reason_for_encounter text
		default null
		check (trim(both from coalesce(reason_for_encounter, 'xxxDEFAULTxxx')) != ''),
	assessment_of_encounter text
		default null
		check (trim(both from coalesce(assessment_of_encounter, 'xxxDEFAULTxxx')) != ''),
	started timestamp with time zone
		not null
		default CURRENT_TIMESTAMP,
	last_affirmed timestamp with time zone
		not null
		default CURRENT_TIMESTAMP
) inherits (audit.audit_fields);

-- ===================================================================
-- do simple schema revision tracking
select log_script_insertion('$RCSfile: gmClin-EMR-Structure-static.sql,v $', '$Revision: 1.3 $');

-- ===================================================================
-- $Log: gmClin-EMR-Structure-static.sql,v $
-- Revision 1.3  2006-02-27 22:39:32  ncq
-- - spell out rfe/aoe
--
-- Revision 1.2  2006/02/27 11:21:31  ncq
-- - add laterality to health issue
--
-- Revision 1.1  2006/02/10 14:08:58  ncq
-- - factor out EMR structure clinical schema into its own set of files
--
--
