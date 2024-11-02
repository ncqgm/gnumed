-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;
set check_function_bodies to on;

-- --------------------------------------------------------------
-- legacy functions
drop function if exists audit.add_table_for_audit(name, name) cascade;
drop function if exists audit.add_table_for_audit(name) cascade;

create function audit.add_table_for_audit(name, name)
	returns boolean
	language SQL
	as 'select audit.register_table_for_auditing($1, $2);'
;

create function audit.add_table_for_audit(name)
	returns boolean
	language SQL
	as 'select audit.register_table_for_auditing(''public'', $1);'
	-- as E'select audit.register_table_for_auditing(''public'', $1);'
;

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-audit-add_table_for_audit.sql', 'v23');
