-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
create table clin.suppressed_hint (
	pk serial primary key,
	fk_encounter integer,						-- not null
	fk_hint integer,							-- not null
	suppressed_by name,							-- not null default CURRENT_USER
	suppressed_when timestamp with time zone,	-- not null default NOW
	rationale text,								-- not null and not empty
	md5_sum text								-- not null and not empty
) inherits (audit.audit_fields);

-- --------------------------------------------------------------
select gm.log_script_insertion('v20-clin-suppressed_hint-static.sql', '20.0');
