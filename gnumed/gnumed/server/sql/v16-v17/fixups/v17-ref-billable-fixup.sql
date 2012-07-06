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
-- this was a bug:
--select audit.register_table_for_auditing('ref'::name, 'billable'::name);

delete from audit.audited_tables a_at where
	a_at.schema = 'ref'
		and
	a_at.table_name = 'billable'
;

\unset ON_ERROR_STOP
drop function audit.ft_del_billable() cascade;
drop function audit.ft_ins_billable() cascade;
drop function audit.ft_upd_billable() cascade;
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
select gm.log_script_insertion('v17-ref-billable-fixup.sql', '17.2');
