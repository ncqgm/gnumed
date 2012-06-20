-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
create schema staging authorization "gm-dbo";

-- --------------------------------------------------------------
create table staging.lab_request (
	like clin.lab_request
		including defaults
		including constraints
		including indexes
);

alter table staging.lab_request
	add column fk_incoming_data_unmatched integer;

--CREATE TABLE staging.lab_request (
--    pk integer primary key,
--    fk_incoming_data_unmatched integer,
--    fk_test_org integer,
--    request_id text,
--    fk_requestor integer,
--    orig_requestor text,
--    lab_request_id text,
--    lab_rxd_when timestamp with time zone,
--    results_reported_when timestamp with time zone,
--    request_status text,
--    is_pending boolean,
--    diagnostic_service_section text,
--    ordered_service text
--) inherits (clin.clin_root_item);

alter table staging.lab_request
	drop column fk_encounter;

-- --------------------------------------------------------------
create table staging.test_result (
	like clin.test_result
		including defaults
		including constraints
		including indexes
);

alter table staging.test_result
	add column orig_intended_reviewer text;

--CREATE TABLE staging.test_result (
--    pk integer primary key,
--    fk_type integer,
--    fk_request integer,
--    val_num numeric,
--    val_alpha text,
--    val_unit text,
--    val_normal_min numeric,
--    val_normal_max numeric,
--    val_normal_range text,
--    val_target_min numeric,
--    val_target_max numeric,
--    val_target_range text,
--    abnormality_indicator text,
--    norm_ref_group text,
--    note_test_org text,
--    material text,
--    material_detail text,
--    fk_intended_reviewer integer,
--    orig_intended_reviewer text
--) inherits (clin.clin_root_item);

alter table staging.test_result
	drop column fk_encounter;

-- --------------------------------------------------------------
select gm.log_script_insertion('v15-staging-hl7-static.sql', 'Revision: 1.1');
