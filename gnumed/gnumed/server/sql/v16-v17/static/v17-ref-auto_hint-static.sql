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
create table ref.auto_hint (
	pk serial primary key,
	query text,
	title text,
	hint text,
	url text,
	is_active boolean,
	source text,
	lang text
) inherits (audit.audit_fields);

-- --------------------------------------------------------------
select gm.log_script_insertion('v17-ref-auto_hint-static.sql', '17.0');
