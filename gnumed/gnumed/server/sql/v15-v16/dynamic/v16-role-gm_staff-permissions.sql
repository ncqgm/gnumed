-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

--set default_transaction_read_only to off;
--set check_function_bodies to on;

-- --------------------------------------------------------------
-- FIXME: add needed revokes

-- --------------------------------------------------------------
-- group membership
GRANT "gm-public" TO "gm-staff";



-- schemata
GRANT USAGE ON SCHEMA "gm" to "gm-staff";
GRANT USAGE ON SCHEMA "dem" to "gm-staff";
GRANT USAGE ON SCHEMA "cfg" to "gm-staff";
GRANT USAGE ON SCHEMA "clin" to "gm-staff";
GRANT USAGE ON SCHEMA "blobs" to "gm-staff";
GRANT USAGE ON SCHEMA "ref" to "gm-staff";



-- functions
GRANT EXECUTE ON FUNCTION gm.log_access2emr(text) TO "gm-staff";
GRANT EXECUTE ON FUNCTION clin.remove_old_empty_encounters(integer, interval) TO "gm-staff";
GRANT EXECUTE ON FUNCTION clin.remove_old_empty_encounters(integer) TO "gm-staff";



-- read-only tables
GRANT SELECT ON TABLE
	-- gm.*
	gm.notifying_tables
	-- cfg.*
	, cfg.cfg_type_enum
	-- dem.*
	, dem.v_gender_labels
	, dem.v_message_inbox
	, dem.v_basic_person
	, dem.v_pat_addresses
	, dem.v_person_comms
	, dem.v_external_ids4identity
	, dem.enum_ext_id_types
	, dem.v_identity_tags
	-- clin.* (restricted)
	, clin.encounter
	, clin.encounter_type
	, clin.v_pat_encounters
	, clin.allergy_state
	, clin.v_pat_allergy_state
	, clin.v_pat_allergies
	-- blobs.*
	, blobs.v_latest_mugshot
	, blobs.v_obj4doc_no_data
	, blobs.doc_obj
	-- ref.*
	, ref.tag_image
to "gm-staff";



-- certain columns of certain tables
GRANT SELECT (pk_encounter, pk_patient, last_affirmed) ON TABLE clin.v_most_recent_encounters TO "gm-staff";
GRANT INSERT (fk_patient, fk_location, fk_type) ON TABLE clin.encounter TO "gm-staff";
GRANT UPDATE ON TABLE clin.encounter TO "gm-staff";

GRANT INSERT (fk_encounter, has_allergy) ON TABLE clin.allergy_state TO "gm-staff";


-- read/write tables
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE
	cfg.cfg_item
	, cfg.cfg_template
	, cfg.cfg_numeric
	, cfg.cfg_string
	, cfg.cfg_str_array
	, cfg.cfg_data
	-- dem.*
	, dem.identity
	, dem.names
TO "gm-staff";



-- sequences
GRANT USAGE ON SEQUENCE
	cfg.cfg_item_pk_seq
	, cfg.cfg_template_pk_seq
	-- dem.*
	, dem.names_id_seq
	, dem.identity_pk_seq
	-- clin.*
	, clin.encounter_pk_seq
	-- audit.*
	, audit.audit_fields_pk_audit_seq
TO "gm-staff";

-- --------------------------------------------------------------
select gm.log_script_insertion('v16-role-gm_staff-permissions.sql', 'Revision: 1');
