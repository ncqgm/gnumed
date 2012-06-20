-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
-- .fk_primary_provider
alter table dem.identity
	add column fk_primary_provider integer;

alter table audit.log_identity
	add column fk_primary_provider integer;

-- --------------------------------------------------------------
select gm.log_script_insertion('v15-dem-identity-static.sql', 'Revision: 1.1');
