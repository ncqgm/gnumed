-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1
set default_transaction_read_only to off;
--set check_function_bodies to on;

-- --------------------------------------------------------------
-- blobs.*
GRANT SELECT (fk_reviewed_row) ON TABLE blobs.reviewed_doc_objs TO "gm-staff";

GRANT SELECT ON TABLE blobs.v_latest_mugshot TO "gm-staff";

GRANT SELECT ON TABLE blobs.v_obj4doc_no_data TO "gm-staff";

-- --------------------------------------------------------------
-- clin.*

GRANT SELECT (pk, fk_health_issue) ON TABLE clin.episode TO "gm-staff";

GRANT SELECT (pk) ON TABLE clin.health_issue TO "gm-staff";

GRANT SELECT ON TABLE clin.meta_test_type TO "gm-staff";

GRANT SELECT (fk_reviewed_row, fk_reviewer, is_technically_abnormal) ON TABLE clin.reviewed_test_results TO "gm-staff";

GRANT SELECT ON TABLE clin.test_org TO "gm-staff";

GRANT SELECT (
	pk,
	abnormality_indicator,
	modified_by,
	fk_intended_reviewer,
	fk_encounter,
	fk_episode,
	fk_type
) ON TABLE clin.test_result TO "gm-staff";

GRANT SELECT ON TABLE clin.test_type TO "gm-staff";

GRANT SELECT (l10n_type) ON TABLE clin.v_most_recent_encounters TO "gm-staff";

--GRANT SELECT ON TABLE clin.v_test_results TO "gm-staff";
GRANT SELECT ON TABLE clin.v_test_results_inbox TO "gm-staff";

GRANT SELECT ON TABLE clin.v_test_types TO "gm-staff";

-- --------------------------------------------------------------
-- dem.*
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE dem.identity_tag TO "gm-staff";

revoke all on dem.gender_label from public, "gm-public", "gm-staff", "gm-doctors";
GRANT SELECT ON TABLE dem.gender_label TO "gm-public";
GRANT INSERT, UPDATE, DELETE ON TABLE dem.gender_label TO "gm-staff";

revoke all on dem.marital_status from public;
revoke all on dem.marital_status from "gm-doctors";
grant select on dem.marital_status to group "gm-public";

GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE dem.message_inbox TO "gm-staff";

GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE dem.org TO "gm-staff";

GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE dem.org_category TO "gm-staff";

GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE dem.org_unit TO "gm-staff";

GRANT SELECT ON TABLE dem.v_gender_defs TO "gm-public";

GRANT SELECT ON TABLE dem.v_message_inbox TO "gm-staff";

GRANT SELECT ON TABLE dem.v_pat_addresses TO "gm-staff";

-- --------------------------------------------------------------
-- ref.*
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE ref.tag_image TO "gm-staff";

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-role-gm_staff-permissions.sql', '23.0');
