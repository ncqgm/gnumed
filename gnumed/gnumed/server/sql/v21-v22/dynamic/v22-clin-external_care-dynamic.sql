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
drop function if exists audit.ft_del_external_care() cascade;
drop function if exists audit.ft_ins_external_care() cascade;
drop function if exists audit.ft_upd_external_care() cascade;

-- --------------------------------------------------------------
-- .is_active
comment on column clin.external_care.inactive is 'whether this external care entry is inactive (eg. historic)';

alter table clin.external_care
	alter column inactive
		set default FALSE;

alter table clin.external_care
	alter column inactive
		set not null;

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-clin-external_care-dynamic.sql', '22.0');
