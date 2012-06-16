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
alter table dem.identity
	add column dob_is_estimated boolean;

alter table audit.log_identity
	add column dob_is_estimated boolean;

-- --------------------------------------------------------------
select gm.log_script_insertion('v17-dem-identity-static.sql', '17.0');
