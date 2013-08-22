-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
--
-- ==============================================================
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
-- needed for Jerzy's enhancements:
GRANT SELECT ON TABLE audit.log_health_issue TO "gm-doctors";
GRANT SELECT ON TABLE audit.log_episode TO "gm-doctors";
GRANT SELECT ON TABLE audit.log_encounter TO "gm-doctors";
GRANT SELECT ON TABLE audit.log_clin_narrative TO "gm-doctors";

-- needed for Jim to research into the medication history
GRANT SELECT ON TABLE audit.log_consumed_substance TO "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v19-audit-grants.sql', '19.0');
