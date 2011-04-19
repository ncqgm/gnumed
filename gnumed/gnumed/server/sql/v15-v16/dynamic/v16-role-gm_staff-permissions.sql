-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

set default_transaction_read_only to off;
--set check_function_bodies to on;

-- --------------------------------------------------------------
-- group membership
GRANT "gm-public" TO "gm-staff";

-- schemata
GRANT USAGE ON SCHEMA "gm" to "gm-staff";
GRANT USAGE ON SCHEMA "dem" to "gm-staff";
GRANT USAGE ON SCHEMA "cfg" to "gm-staff";
GRANT USAGE ON SCHEMA "clin" to "gm-staff";
GRANT USAGE ON SCHEMA "blobs" to "gm-staff";

-- functions
GRANT EXECUTE ON FUNCTION gm.log_access2emr(text) to "gm-staff";

-- read-only tables
GRANT SELECT ON TABLE
	-- gm.*
	gm.notifying_tables
	-- cfg.*
	, cfg.cfg_template
	, cfg.cfg_type_enum
	-- dem.*
	, dem.v_gender_labels
	, dem.v_message_inbox
	, dem.v_basic_person
	, dem.v_pat_addresses
	, dem.v_person_comms
	, dem.v_external_ids4identity
	-- clin.* (restricted)
	--, clin.v_waiting_list
to "gm-staff";

-- certain columns of certain tables
GRANT SELECT (pk) ON TABLE blobs.doc_med TO "gm-staff";

-- read/write tables
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE
	cfg.cfg_item
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
	-- dem.*
	, dem.names_id_seq
	, dem.identity_pk_seq
TO "gm-staff";

-- --------------------------------------------------------------
select gm.log_script_insertion('v16-role-gm_staff-permissions.sql', 'Revision: 1');
