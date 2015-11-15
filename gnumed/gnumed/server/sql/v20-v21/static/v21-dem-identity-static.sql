-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
alter table dem.identity
	drop column pupic cascade;

alter table audit.log_identity
	drop column pupic;

-- --------------------------------------------------------------
select gm.log_script_insertion('v21-dem-identity-static.sql', '21.0');
