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
revoke all on dem.org from public;
revoke all on dem.org from "gm-public";
grant select on dem.org to group "gm-public";
revoke all on dem.org from "gm-staff";
grant select, insert, update, delete on dem.org to group "gm-staff";
revoke all on dem.org from "gm-doctors";
grant select, insert, update, delete on dem.org to group "gm-doctors";


revoke all on dem.org_unit from public;
revoke all on dem.org_unit from "gm-public";
grant select on dem.org_unit to group "gm-public";
revoke all on dem.org_unit from "gm-staff";
grant select, insert, update, delete on dem.org_unit to group "gm-staff";
revoke all on dem.org_unit from "gm-doctors";
grant select, insert, update, delete on dem.org_unit to group "gm-doctors";


revoke all on dem.org_category from public;
revoke all on dem.org_category from "gm-public";
grant select on dem.org_category to group "gm-public";
revoke all on dem.org_category from "gm-staff";
grant select, insert, update, delete on dem.org_category to group "gm-staff";
revoke all on dem.org_category from "gm-doctors";
grant select, insert, update, delete on dem.org_category to group "gm-doctors";


revoke all on dem.v_org_unit_comms from public;
revoke all on dem.v_org_unit_comms from "gm-public";
revoke all on dem.v_org_unit_comms from "gm-staff";
revoke all on dem.v_org_unit_comms from "gm-doctors";
grant select on dem.v_org_unit_comms to group "gm-public";

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-dem-org-permission-fixups.sql', '22.30');
