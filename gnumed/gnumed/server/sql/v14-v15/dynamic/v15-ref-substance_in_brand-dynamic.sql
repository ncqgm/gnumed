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
drop view ref.v_substance_in_brand cascade;
alter table ref.substance_in_brand drop column fk_brand cascade;
alter table ref.substance_in_brand drop column description cascade;
alter table ref.substance_in_brand drop column atc_code cascade;
truncate ref.substance_in_brand cascade;
comment on table ref.substance_in_brand is 'Remove this table in gnumed_v16';
revoke all on ref.substance_in_brand from "gm-doctors", "gm-public";
\set ON_ERROR_STOP 1



delete from audit.audited_tables aat
where
	aat.schema = 'ref'
		and
	aat.table_name = 'substance_in_brand'
;

delete from gm.notifying_tables gnt
where
	gnt.schema_name = 'ref'
		and
	gnt.table_name = 'substance_in_brand'
;



\unset ON_ERROR_STOP
drop table ref.substance_in_brand cascade;
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
select gm.log_script_insertion('v15-ref-substance_in_brand-dynamic.sql', 'Revision: 1.1');
