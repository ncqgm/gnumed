-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
create table dem.praxis_branch (
	pk serial primary key,
	fk_org_unit integer
) inherits (audit.audit_fields);

-- --------------------------------------------------------------
select gm.log_script_insertion('v19-dem-praxis_branch-static.sql', '19.0');
