-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop table clin.consumed_substance cascade;
\set ON_ERROR_STOP 1



delete from audit.audited_tables aat
where
	aat.schema = 'clin'
		and
	aat.table_name = 'consumed_substance'
;

delete from gm.notifying_tables gnt
where
	gnt.schema_name = 'clin'
		and
	gnt.table_name = 'consumed_substance'
;

-- --------------------------------------------------------------
select gm.log_script_insertion('v15-clin-consumed_substance-dynamic.sql', 'Revision: 1.1');
