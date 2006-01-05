-- GnuMed - test/measurement related tables

-- author: Karsten Hilbert <Karsten.Hilbert@gmx.net>
-- author: Christof Meigen <christof@nicht-ich.de>
-- license: GPL
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmMeasurements.sql,v $
-- $Revision: 1.56 $

-- this belongs into the clinical service (historica)
-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- ====================================
create table clin.test_org (
	pk serial primary key,
	fk_org integer unique not null,
	fk_adm_contact integer
		default null
		references clin.xlnk_identity(xfk_identity)
		on update cascade
		on delete restrict,
	fk_med_contact integer
		default null
		references clin.xlnk_identity(xfk_identity)
		on update cascade
		on delete restrict,
	internal_name text unique,
	"comment" text
) inherits (audit.audit_fields);

select public.add_table_for_audit('clin', 'test_org');

-- remote foreign keys
--select add_x_db_fk_def('test_org', 'fk_org', 'personalia', 'org', 'id');

COMMENT ON TABLE clin.test_org IS
	'organisation providing results';
COMMENT ON COLUMN clin.test_org.fk_org IS
	'link to organisation
	 HL7: MSH.sending_facility/sending_application';
COMMENT ON COLUMN clin.test_org.fk_adm_contact IS
	'whom to call for admin questions (modem link, etc.)';
COMMENT ON COLUMN clin.test_org.fk_med_contact IS
	'whom to call for medical questions (result verification,
	 additional test requests)';
comment on column clin.test_org.internal_name is
	'you can store here the name a test org identifies
	 itself with when sending data
	 HL7: MSH.sending_application/OBR.universal_service_id';
comment on column clin.test_org."comment" is
	'useful for, say, dummy records where you want
	 to mark up stuff like "pharmacy such-and-such"
	 if you don''t have it in your contacts';

-- there need to be two pseudo org records
--  1) your own practice
--  2) "non-medical person" (exactly *who* may be in *_result)

-- ====================================
create table clin.test_type (
	pk serial primary key,
	fk_test_org integer references clin.test_org(pk),
	code text not null,
	coding_system text default null,
	name text,
	comment text,
	conversion_unit text,
	unique (fk_test_org, code, coding_system)
) inherits (audit.audit_fields);

select public.add_table_for_audit('clin', 'test_type');

-- remote foreign keys
--select add_x_db_fk_def('test_type', 'coding_system', 'reference', 'ref_source', 'name_short');
--select add_x_db_fk_def('test_type', 'conversion_unit', 'reference', 'basic_unit', 'name_short');

comment on table clin.test_type is
	'measurement type, like a "method" in a lab';
comment on column clin.test_type.fk_test_org is
	'organisation carrying out this type of measurement, eg. a particular lab';
comment on column clin.test_type.code is
	'short name, acronym or code of this type of measurement,
	 may conform to some official list or other such as LOINC,
	 Australian Pathology request codes or German lab-specific ELVs,
	 actually, this column should be checked against the coding system
	 tables, too, the only problem being that we do not know which
	 one ... as it depends on the *value* in "coding_system",
	 HL7: OBX.observation_identifier';
comment on column clin.test_type.coding_system is
	'identifier of coding system that the code of this
	 measurement type is taken from, should be verifiable
	 against the "reference" service of GnuMed';
comment on column clin.test_type.name is
	'descriptive name of this measurement type,
	 HL7: OBX.observation_identifier';
comment on column clin.test_type.comment is
	'arbitrary comment on this type of measurement/test such
	 as "outdated" or "only reliable when ..."';
comment on column clin.test_type.conversion_unit is
	'the basic unit for this test type, preferably SI,
	 used for comparing results delivered in differing
	 units, this does not relate to what unit the test
	 provider delivers results in but rather the unit
	 we think those results need to be converted to in
	 order to be comparable to OTHER results';

-- ====================================
create table clin.test_type_unified (
	pk serial primary key,
	code text
		not null,
	name text
		not null,
	coding_system text
		default null,
	comment text,
	unique (code, name)
);

comment on table clin.test_type_unified is
	'this table merges test types from various test orgs
	 which are intended to measure the same value but have
	 differing names into one logical test type,
	 this is not intended to be used for aggregating
	 semantically different test types into "profiles"';

-- ====================================
create table clin.lnk_ttype2unified_type (
	pk serial primary key,
	fk_test_type integer
		not null
		references clin.test_type(pk)
		on update cascade
		on delete cascade,
	fk_test_type_unified integer
		not null
		references clin.test_type_unified(pk)
		on update cascade
		on delete restrict
);

-- ====================================
create table clin.lnk_tst2norm (
	id serial primary key,
	id_test integer
		not null
		references clin.test_type(pk),
	id_norm integer not null,
	unique (id_test, id_norm)
) inherits (audit.audit_fields);

select public.add_table_for_audit('clin', 'lnk_tst2norm');

--select add_x_db_fk_def ('lnk_tst2norm', 'id_norm', 'reference', 'test_norm', 'id');

comment on table clin.lnk_tst2norm is
	'links test result evaluation norms to tests';
comment on column clin.lnk_tst2norm.id_test is
	'which test does the linked norm apply to';
comment on column clin.lnk_tst2norm.id_norm is
	'the norm to apply to the linked test';

-- ====================================
create table clin.test_result (
	pk serial primary key,
	fk_type integer
		not null
		references clin.test_type(pk),
	val_num numeric		-- consider contrib/seg.sql
		default null
		check (
			((val_num is not null) or (val_alpha is not null))
				or
			((val_num is null) and (val_alpha != '') and (val_alpha is not null))
		),
	val_alpha text
		default null,
	val_unit text
		default null,
	val_normal_min numeric,
	val_normal_max numeric,
	val_normal_range text,
	val_target_min numeric,
	val_target_max numeric,
	val_target_range text,
	abnormality_indicator text
		default null,
	norm_ref_group text,
	note_provider text,
	material text,
	material_detail text,
	fk_intended_reviewer integer
		not null
		references clin.xlnk_identity(xfk_identity)
) inherits (clin.clin_root_item);

alter table clin.test_result add foreign key (fk_encounter)
		references clin.encounter(pk)
		on update cascade
		on delete restrict;
alter table clin.test_result add foreign key (fk_episode)
		references clin.episode(pk)
		on update cascade
		on delete restrict;
alter table clin.test_result alter column soap_cat set default 'o';
alter table clin.test_result add constraint numval_needs_unit
	check (
		((val_num is not null) and (trim(coalesce(val_unit, '')) != ''))
			or
		(val_num is null)
	);

select add_table_for_audit('clin', 'test_result');
--select add_x_db_fk_def('test_result', 'val_unit', 'reference', 'unit', 'name_short');

COMMENT ON TABLE clin.test_result is
	'the results of a single measurement';
-- FIXME: housekeeping sanity script:
comment on column clin.test_result.clin_when is
	'the time when this result was *actually* obtained,
	 if this is a lab result this should be between
	 lab_request.clin_when and lab_request.results_reported_when,
	 HL7: OBR.observation_date_time';
comment on column clin.test_result.narrative is
	'clinical comment, progress note';
comment on column clin.test_result.fk_type is
	'the type of test this result is from';
comment on column clin.test_result.val_num is
	'numeric value if any,
	 HL7: OBX.observation_results if OBX.value_type == NM';
comment on column clin.test_result.val_alpha is
	'alphanumeric value if any,
	 HL7: OBX.observation_results if OBX.value_type == FT';
comment on column clin.test_result.val_unit is
	'the unit this result came in
	 HL7: OBX.units';
comment on column clin.test_result.val_normal_min is
	'lower bound of normal range if numerical as
	 defined by provider for this result';
comment on column clin.test_result.val_normal_max is
	'upper bound of normal range if numerical as
	 defined by provider for this result';
comment on column clin.test_result.val_normal_range is
	'range of normal values if alphanumerical
	 as defined by provider for this result, eg.
	 "less than 0.5 but detectable"
	 HL7: OBX.reference_range';
comment on column clin.test_result.val_target_min is
	'lower bound of target range if numerical as
	 defined by clinician caring this patient';
comment on column clin.test_result.val_target_max is
	'upper bound of target range if numerical as
	 defined by clinician caring for this patient';
comment on column clin.test_result.val_target_range is
	'range of target values if alphanumerical
	 as defined by clinician caring for this patient';
comment on column clin.test_result.abnormality_indicator is
	'how the test provider flagged this result as abnormal,
	 *not* a clinical assessment but rather a technical one
	 LDT: 8422';
comment on column clin.test_result.norm_ref_group is
	'what sample of the population does this normal range
	 applay to, eg what type of patient was assumed when
	 interpreting this result,
	 LDT: 8407';
comment on column clin.test_result.note_provider is
	'any comment the test provider should like to make, such
	 as "may be inaccurate due to haemolyzed sample"
	 LDT: 8470';
comment on column clin.test_result.material is
	'the submitted material, eg. smear, serum, urine, etc.,
	 LDT: 8430';
comment on column clin.test_result.material_detail is
	'details re the material, eg. site taken from, etc.
	 LDT: 8431';
comment on column clin.test_result.fk_intended_reviewer is
	'who is *supposed* to review this item';

-- ====================================
create table clin.lab_request (
	pk serial primary key,
	fk_test_org integer
		not null
		references clin.test_org(pk),
	request_id text
		not null
		check (trim(both from request_id) != ''),
	-- FIXME: references staff(pk)
	fk_requestor integer
		default null
		references clin.xlnk_identity(xfk_identity)
		on update cascade
		on delete restrict,
	lab_request_id text
		default null,
	lab_rxd_when timestamp with time zone
		default null,
	results_reported_when timestamp with time zone
		default null,
	request_status text
		not null
		check (request_status in ('pending', 'preliminary', 'partial', 'final')),
	is_pending boolean
		not null
		default true,
	unique (fk_test_org, request_id)
	-- FIXME: there really ought to be a constraint like this:
--	unique (fk_patient, request_id)
) inherits (clin.clin_root_item);

alter table clin.lab_request add foreign key (fk_encounter)
		references clin.encounter(pk)
		on update cascade
		on delete restrict;
alter table clin.lab_request add foreign key (fk_episode)
		references clin.episode(pk)
		on update cascade
		on delete restrict;
alter table clin.lab_request alter column soap_cat set default 'p';

comment on table clin.lab_request is
	'test request metadata';
comment on column clin.lab_request.clin_when is
	'the time the sample for this request was taken
	 LDT: 8432:8433
	 HL7: OBR.quantity_timing';
comment on column clin.lab_request.narrative is
	'free text comment on request';
comment on column clin.lab_request.request_id IS
	'ID this request had when sent to the lab
	 LDT: 8310
	 HL7: OBR.filler_order_number';
comment on column clin.lab_request.fk_requestor is
	'who requested the test - really needed ?';
comment on column clin.lab_request.lab_request_id is
	'ID this request had internally at the lab
	 LDT: 8311';
comment on column clin.lab_request.lab_rxd_when is
	'when did the lab receive the request+sample
	 LDT: 8301
	 HL7: OBR.requested_date_time';
comment on column clin.lab_request.results_reported_when is
	'when was the report on the result generated,
	LDT: 8302
	HL7: OBR.results_report_status_change';
comment on column clin.lab_request.request_status is
	'pending, final, preliminary, partial
	 LDT: 8401';
comment on column clin.lab_request.is_pending is
	'true if any (even partial) results are still pending';

-- ====================================
create table clin.lnk_result2lab_req (
	pk serial primary key,
	fk_result integer
		unique
		not null
		references clin.test_result(pk)
		on update cascade
		on delete cascade,
	fk_request integer
		not null
		references clin.lab_request(pk)
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

-- =============================================
-- do simple schema revision tracking
select log_script_insertion('$RCSfile: gmMeasurements.sql,v $', '$Revision: 1.56 $');

-- =============================================
-- $Log: gmMeasurements.sql,v $
-- Revision 1.56  2006-01-05 16:04:37  ncq
-- - move auditing to its own schema "audit"
--
-- Revision 1.55  2005/12/06 13:26:55  ncq
-- - clin.clin_encounter -> clin.encounter
-- - also id -> pk
--
-- Revision 1.54  2005/12/05 19:05:59  ncq
-- - clin_episode -> episode
--
-- Revision 1.53  2005/12/04 09:43:54  ncq
-- - add fk_intended_reviewer to test_result
--
-- Revision 1.52  2005/11/29 19:08:10  ncq
-- - cleanup
--
-- Revision 1.51  2005/11/27 13:00:14  ncq
-- - cleanup
--
-- Revision 1.50  2005/11/25 15:07:28  ncq
-- - create schema "clin" and move all things clinical into it
--
-- Revision 1.49  2005/10/30 22:55:09  ncq
-- - factor out unmatched incoming data table
--
-- Revision 1.48  2005/10/26 21:31:09  ncq
-- - review status tracking
--
-- Revision 1.47  2005/10/24 19:10:18  ncq
-- - cleanup, remove 7.1ism
--
-- Revision 1.46  2005/09/19 16:38:51  ncq
-- - adjust to removed is_core from gm_schema_revision
--
-- Revision 1.45  2005/07/14 21:31:42  ncq
-- - partially use improved schema revision tracking
--
-- Revision 1.44  2005/06/19 13:34:42  ncq
-- - properly inherit foreign keys into children of clin_root_item
--
-- Revision 1.43  2005/05/18 15:28:24  ncq
-- - fix misplaced )
--
-- Revision 1.42  2005/05/14 15:04:39  ncq
-- - make conversion unit nullable
-- - numeric test results need a unit
--
-- Revision 1.41  2005/03/31 17:50:45  ncq
-- - improved check constraint on lab_request.request_status
-- - strings moved to gmClinicalData.sql
--
-- Revision 1.40  2005/03/08 16:50:00  ncq
-- - add HL7 mapping docs to field comments
--
-- Revision 1.39  2005/02/15 18:25:14  ncq
-- - test_result.id -> pk
--
-- Revision 1.38  2005/02/13 19:18:40  ncq
-- - Jim wanted test_result_unmatched rather than the other way round
--
-- Revision 1.37  2005/02/08 07:22:42  ncq
-- - missing "," and wrong table name used
--
-- Revision 1.36  2005/02/08 07:07:40  ncq
-- - improve path results staging table
-- - cleanup
--
-- Revision 1.35  2005/02/07 21:42:17  ncq
-- - added unmatched test results staging table
--
-- Revision 1.34  2005/02/07 13:09:48  ncq
-- - test_type_local -> test_type_unified as discussed on list
-- - lnk_ttype2local_type -> lnk_ttype2unified_type
--
-- Revision 1.33  2004/10/17 16:27:15  ncq
-- - val_num: float -> numeric + fix views
-- - clin_when::date in prescribed_after_started constraint
--
-- Revision 1.32  2004/10/10 06:34:13  ihaywood
-- Extended blobs to support basic document management:
-- keeping track of whose reviewed what, etc.
--
-- This duplicates the same functionality for path. results:
-- how can we integrate?
-- CVS ----------------------------------------------------------------------
--
-- Revision 1.31  2004/09/29 10:33:54  ncq
-- - cleanup
-- - normalize test_type_local into lnk_table
-- - basic_unit -> conversion_unit
--
-- Revision 1.30  2004/09/28 12:30:22  ncq
-- - add constraint on test_type_local
--
-- Revision 1.29  2004/09/17 20:15:00  ncq
-- - add val_target_* to test_result
--
-- Revision 1.28  2004/07/17 20:57:53  ncq
-- - don't use user/_user workaround anymore as we dropped supporting
--   it (but we did NOT drop supporting readonly connections on > 7.3)
--
-- Revision 1.27  2004/06/02 00:04:50  ncq
-- - soap_cat defaults
--
-- Revision 1.26  2004/06/01 07:58:13  ncq
-- - improve comments
--
-- Revision 1.25  2004/05/18 20:38:21  ncq
-- - typo fix
--
-- Revision 1.24  2004/05/06 23:29:04  ncq
-- - rename test_type_uni to test_type_local
-- - test_type_local.internal_name/code -> *.local_name/code
-- - test_result.technically_abnormal: bool -> text
--
-- Revision 1.23  2004/05/04 08:14:26  ncq
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
