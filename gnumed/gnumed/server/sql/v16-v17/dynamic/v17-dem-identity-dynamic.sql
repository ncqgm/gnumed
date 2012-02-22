-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
-- .dob_is_estimated
comment on column dem.identity.fk_primary_provider is
'Whether the given DOB is estimated or not. The TOB is assumed to be correct if given';


alter table dem.identity
	alter column dob_is_estimated
		set default false;

update dem.identity set dob_is_estimated = false;

alter table dem.identity
	alter column dob_is_estimated
		set not null;

-- --------------------------------------------------------------
select gm.log_script_insertion('v17-dem-identity-dynamic.sql', '17.0');
