-- GnuMed - test/measurement related tables

-- author: Karsten Hilbert <Karsten.Hilbert@gmx.net>
-- author: Christof Meigen <christof@nicht-ich.de>
-- license: GPL
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmMeasurements.sql,v $
-- $Revision: 1.23 $

-- this belongs into the clinical service (historica)
-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- ====================================
create table test_org (
	pk serial primary key,
	fk_org integer unique not null,
	fk_adm_contact integer
		default null
		references xlnk_identity(xfk_identity)
		on update cascade
		on delete restrict,
	fk_med_contact integer
		default null
		references xlnk_identity(xfk_identity)
		on update cascade
		on delete restrict,
	internal_name text unique,
	"comment" text
) inherits (audit_fields);

select add_table_for_audit('test_org');

-- remote foreign keys
select add_x_db_fk_def('test_org', 'fk_org', 'personalia', 'org', 'id');

COMMENT ON TABLE test_org IS
	'organisation providing results';
COMMENT ON COLUMN test_org.fk_org IS
	'link to organisation';
COMMENT ON COLUMN test_org.fk_adm_contact IS
	'whom to call for admin questions (modem link, etc.)';
COMMENT ON COLUMN test_org.fk_med_contact IS
	'whom to call for medical questions (result verification,
	 additional test requests)';
comment on column test_org.internal_name is
	'you can store here the name a test org identifies
	 itself with when sending data';
comment on column test_org."comment" is
	'useful for, say, dummy records where you want
	 to mark up stuff like "pharmacy such-and-such"
	 if you don''t have it in your contacts';

-- there need to be two pseudo org records
--  1) your own practice
--  2) "non-medical person" (exactly *who* may be in *_result)

-- ====================================
create table test_type (
	id serial primary key,
	fk_test_org integer references test_org(pk),
	code text not null,
	coding_system text default null,
	name text,
	comment text,
	basic_unit text not null,
	unique (fk_test_org, code)
) inherits (audit_fields);

select add_table_for_audit('test_type');

-- remote foreign keys
select add_x_db_fk_def('test_type', 'coding_system', 'reference', 'ref_source', 'name_short');
-- column "code" would have to be checked, too, but we don't
-- know against which table in "reference" since that depends
-- on "coding_system" ... unless we invent a mechanism to set
-- a default "coding_system" ...
select add_x_db_fk_def('test_type', 'basic_unit', 'reference', 'basic_unit', 'name_short');

comment on table test_type is
	'measurement type, like a "method" in a lab';
comment on column test_type.fk_test_org is
	'organisation carrying out this type of measurement, eg. a particular lab';
comment on column test_type.code is
	'short name, acronym or code of this type of measurement,
	 may conform to some official list or other such as LOINC,
	 Australian Pathology request codes or German lab-specific ELVs';
comment on column test_type.coding_system is
	'identifier of coding system that the code of this
	 measurement type is taken from, should be verifiable
	 against the "reference" service of GnuMed';
comment on column test_type."name" is
	'descriptive name of this measurement type';
comment on column test_type."comment" is
	'arbitrary comment on this type of measurement/test such
	 as "outdated" or "only reliable when ..."';
comment on column test_type.basic_unit is
	'the basic (SI?) unit for this test type, used for
	 comparing results delivered in differing units';

-- ====================================
-- FIXME: run demon to make sure that internal_code is always
-- associated with the same internal_name
create table test_type_uni (
	pk serial primary key,
	fk_test_type integer
		unique
		not null
		references test_type(id)
		on update cascade
		on delete cascade,
	internal_code text not null,
	internal_name text not null
);

comment on table test_type_uni is
	'this table merges test types from various test orgs
	 into one logical test type (mainly for display)';

-- ====================================
create table lnk_tst2norm (
	id serial primary key,
	id_test integer not null references test_type(id),
	id_norm integer not null,
	unique (id_test, id_norm)
) inherits (audit_fields);

select add_table_for_audit('lnk_tst2norm');

select add_x_db_fk_def ('lnk_tst2norm', 'id_norm', 'reference', 'test_norm', 'id');

comment on table lnk_tst2norm is
	'links test result evaluation norms to tests';
comment on column lnk_tst2norm.id_test is
	'which test does the linked norm apply to';
comment on column lnk_tst2norm.id_norm is
	'the norm to apply to the linked test';

-- ====================================
create table test_result (
	id serial primary key,
	fk_type integer
		not null
		references test_type(id),
	val_num float
		default null
		check (
			((val_num is not null) or (val_alpha is not null))
				or
			((val_num is null) and (val_alpha != '') and (val_alpha is not null))
		),
	val_alpha text
		default null,
	val_unit text,
	val_normal_min float,
	val_normal_max float,
	val_normal_range text,
	technically_abnormal bool not null,
	norm_ref_group text,
	note_provider text,
	material text,
	material_detail text,
	reviewed_by_clinician bool
		not null
		default false,
	fk_reviewer integer
		default null
		references xlnk_identity(xfk_identity)
		check(((reviewed_by_clinician is false) and (fk_reviewer is null)) or (fk_reviewer is not null)),
	clinically_relevant bool
		default null
		check (((reviewed_by_clinician=false) and (clinically_relevant is null)) or (clinically_relevant is not null))
) inherits (clin_root_item);

select add_table_for_audit('test_result');
select add_x_db_fk_def('test_result', 'val_unit', 'reference', 'unit', 'name_short');

COMMENT ON TABLE test_result is
	'the results of a single measurement';
-- FIXME: housekeeping sanity script:
comment on column test_result.clin_when is
	'the time when this result was actually obtained,
	 if this is a lab result this should be between
	 lab_request.clin_when and lab_request.results_reported_when';
comment on column test_result.narrative is
	'clinical comment, progress note';
comment on column test_result.fk_type is
	'the type of test this result is from';
comment on column test_result.val_num is
	'numeric value if any';
comment on column test_result.val_alpha is
	'alphanumeric value if any';
comment on column test_result.val_unit is
	'the unit this result came in';
comment on column test_result.val_normal_min is
	'lower bound of normal range if numerical as
	 defined by provider for this result';
comment on column test_result.val_normal_max is
	'upper bound of normal range if numerical as
	 defined by provider for this result';
comment on column test_result.val_normal_range is
	'range of normal values if alphanumerical
	 as defined by provider for this result, eg.
	 "less than 0.5 but detectable"';
comment on column test_result.technically_abnormal is
	'whether test provider flagged this result as abnormal,
	 *not* a clinical assessment but rather a technical one
	 LDT: 8422';
comment on column test_result.norm_ref_group is
	'what sample of the population does this normal range
	 applay to, eg what type of patient was assumed when
	 interpreting this result,
	 LDT: 8407';
comment on column test_result.note_provider is
	'any comment the test provider should like to make, such
	 as "may be inaccurate due to haemolyzed sample"
	 LDT: 8470';
comment on column test_result.material is
	'the submitted material, eg. smear, serum, urine, etc.,
	 LDT: 8430';
comment on column test_result.material_detail is
	'details re the material, eg. site take from, etc.
	 LDT: 8431';
comment on column test_result.reviewed_by_clinician is
	'whether a clinician has seen this result yet,
	 depending on the use case this need to simply get
	 set by any read access but may follow specific
	 business rules such as "set as SEEN when treating/
	 requesting doctor has reviewed the item"';
comment on column test_result.fk_reviewer is
	'who has reviewed the item';
comment on column test_result.clinically_relevant is
	'whether this result is considered relevant clinically,
	 need not correspond to the value of "techically_abnormal"
	 since abnormal values may be irrelevant while normal
	 ones can be of significance';

-- ====================================
create table lab_request (
	pk serial primary key,
	fk_test_org integer
		not null
		references test_org(pk),
	request_id text
		not null
		check (trim(both from request_id) != ''),
	-- FIXME: references staff(pk)
	fk_requestor integer
		default null
		references xlnk_identity(xfk_identity)
		on update cascade
		on delete restrict,
	lab_request_id text
		default null,
	lab_rxd_when timestamp with time zone
		default null,
	results_reported_when timestamp with time zone
		default null,
	request_status text
		default null
		check (
			(request_status in ('preliminary', 'partial', 'final'))
				or
			((request_status is null) and (is_pending is true))
		),
	is_pending boolean
		not null
		default true,
	unique (fk_test_org, request_id)
	-- FIXME: there really should be a constraint like that
--	unique (fk_patient, request_id)
) inherits (clin_root_item);

-- those are fixed strings, so we can translate them on the way out ...
select i18n('preliminary');
select i18n('partial');
select i18n('final');

comment on column lab_request.clin_when is
	'when where the samples for this request taken';
comment on column lab_request.request_id IS
	'ID this request had when sent to the lab
	 LDT: 8310';
comment on column lab_request.fk_requestor is
	'who requested the test/needed ?';
comment on column lab_request.lab_request_id is
	'ID this request had internally at the lab
	 LDT: 8311';
comment on column lab_request.lab_rxd_when is
	'when did the lab receive the request+request
	 LDT: 8301';
comment on column lab_request.results_reported_when is
	'when was the report on the result generated,
	LDT: 8302';
comment on column lab_request.request_status is
	'final, preliminary, partial
	 LDT: 8401';
comment on column lab_request.is_pending is
	'true if any (even partial) results are still pending';

-- ====================================
create table lnk_result2lab_req (
	pk serial primary key,
	fk_result integer
		unique
		not null
		references test_result(id)
		on update cascade
		on delete cascade,
	fk_request integer
		not null
		references lab_request(pk)
		on update cascade
		on delete cascade
);

-- ====================================
-- ====================================
-- This is just an idea how measurements might be stored. It is far more
-- measurement-centric compared to gmLab, which might be not a good thing
-- for every-day use, but being more normalized and more strict it 
-- is probably better suitable for larger-scale clinical applications.

-- The main differences with gmLab are the following:
--
--     there is an additional table (here: test_action) which
--     normalizes the date/occasion at which several measurements were taken
--     In gmLab it might happen that the same sample is in the database as
--     being taken at different dates, since the date is stored for every
--     result

-- the doctor wants to see types of measurements grouped together
-- even if they come from different labs (maybe because she switched
-- labs at some point),
-- that's what this is for,

--create table test_unified (
--	id serial primary key,
--	short_name CHARACTER VARYING(10),
--	long_name CHARACTER VARYING(60),
--	comment CHARACTER VARYING(60)
--) INHERITS (audit_identity);

--COMMENT ON TABLE lab_test IS 'to unify tests accross lab result providers with different names for the same test';

-- =============================================
-- do simple schema revision tracking
delete from gm_schema_revision where filename = '$RCSfile: gmMeasurements.sql,v $';
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmMeasurements.sql,v $', '$Revision: 1.23 $');

-- =============================================
-- $Log: gmMeasurements.sql,v $
-- Revision 1.23  2004-05-04 08:14:26  ncq
-- - check constraint on lab_request.request_id disallowing empty request ids
--
-- Revision 1.22  2004/05/02 22:52:47  ncq
-- - fix check constraints in lab_request
--
-- Revision 1.21  2004/04/21 15:31:09  ncq
-- - tighten constraints on test_result.val_num/alpha to require one or the other
--
-- Revision 1.20  2004/04/19 12:47:49  ncq
-- - translate request_status
-- - add housekeeping_todo.reported_to
--
-- Revision 1.19  2004/04/16 00:36:23  ncq
-- - cleanup, constraints
--
-- Revision 1.18  2004/04/07 18:16:06  ncq
-- - move grants into re-runnable scripts
-- - update *.conf accordingly
--
-- Revision 1.17  2004/03/23 17:34:49  ncq
-- - support and use optionally cross-provider unified test names
--
-- Revision 1.16  2004/03/23 02:33:13  ncq
-- - comments/constraints/references on test_result, also result_when -> clin_when
-- - v_results4lab_req, v_test_org_profile, grants
--
-- Revision 1.15  2004/03/18 18:30:14  ncq
-- - constraint on test_result.clinically_relevant
--
-- Revision 1.14  2004/03/18 10:01:10  ncq
-- - test_type.id_provider -> fk_test_org
-- - test_org.internal_name
-- - lab_request.result_reported_when -> results_reported_when
-- - lab_request.result_status -> request_status
-- - lnk_result2lab_req
-- - grants
--
-- Revision 1.13  2004/03/12 23:43:34  ncq
-- - did forget a , in test_result
--
-- Revision 1.12  2004/03/12 23:15:42  ncq
-- - more fixes for getting things in line with LDT
--
-- Revision 1.11  2004/01/15 15:15:41  ncq
-- - use xlnk_identity
--
-- Revision 1.10  2003/10/01 15:45:20  ncq
-- - use add_table_for_audit() instead of inheriting from audit_mark
--
-- Revision 1.9  2003/08/17 00:25:38  ncq
-- - remove log_ tables, they are now auto-created
--
-- Revision 1.8  2003/08/13 21:10:21  ncq
-- - add lnk_tst2norm table
--
-- Revision 1.7  2003/08/10 01:01:01  ncq
-- - use x_db_fk helper
-- - test_type needs basic_unit ...
--
-- Revision 1.6  2003/08/03 14:41:01  ncq
-- - clear up column naming confusion in x_db_fk, adapt users
--
-- Revision 1.5  2003/08/03 14:10:27  ncq
-- - add external FK defs
--
-- Revision 1.4  2003/07/27 21:59:47  ncq
-- - better comments/cleanup/renaming
-- - first remote FK defs
-- - auditing
--
-- Revision 1.3  2003/01/05 13:05:51  ncq
-- - schema_revision -> gm_schema_revision
--
-- Revision 1.2  2003/01/01 18:10:23  ncq
-- - changed to new i18n
-- - some field names more precise
--
-- Revision 1.1  2002/12/31 00:03:47  ncq
-- - merged gmLab and gmMeasure by Christof for more generic measurements storage
-- - gmLab deprecated
--
-- Revision 1.5  2002/12/22 01:24:25  ncq
-- - some changes suggested by Christof Meigen
--
-- Revision 1.4  2002/12/01 13:53:09  ncq
-- - missing ; at end of schema tracking line
--
-- Revision 1.3  2002/11/16 01:08:03  ncq
-- - fixup, revision tracking
--
