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
drop function if exists clin.trf_ins_intake_prevent_duplicate_component_links() cascade;
drop function if exists clin.trf_insert_intake_links_all_drug_components() cascade;

drop function if exists clin.trf_upd_intake_prevent_duplicate_component_links() cascade;
drop function if exists clin.trf_upd_intake_updates_all_drug_components() cascade;
drop function if exists clin.trf_upd_intake_must_link_all_drug_components() cascade;

drop function if exists clin.trf_del_intake_must_unlink_all_drug_components() cascade;
drop function if exists clin.trf_DEL_intake_document_deleted() cascade;

drop table if exists clin.substance_intake cascade;

delete from audit.audited_tables where schema = 'clin' and table_name = 'substance_intake';
delete from gm.notifying_tables where schema_name = 'clin' and table_name = 'substance_intake';

-- --------------------------------------------------------------
-- clin.intake
alter table clin.intake
	drop column if exists
		_fk_s_i cascade;

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-clin-substance_intake-dynamic.sql', '23.0');
