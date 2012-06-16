-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
create table clin.lnk_code2item_root (
	pk_lnk_code2item serial primary key,
	fk_generic_code integer,
	fk_item integer,
	code_modifier text
) inherits (audit.audit_fields);

-- --------------------------------------------------------------
drop table clin.coded_phrase cascade;
drop table audit.log_coded_phrase cascade;

delete from audit.audited_tables where
	schema = 'clin'
		and
	table_name = 'coded_phrase'
;

-- --------------------------------------------------------------
select gm.log_script_insertion('v16-clin-lnk_code2item_root-static.sql', '1.0');
