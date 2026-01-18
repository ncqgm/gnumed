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
alter table dem.identity
	add column if not exists aux_info jsonb;

alter table audit.log_identity
	add column aux_info jsonb;

comment on column dem.identity.aux_info is
	'Structured (JSON) auxiliary information on this identity.';

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-dem-identity-dynamic.sql', 'v23');
