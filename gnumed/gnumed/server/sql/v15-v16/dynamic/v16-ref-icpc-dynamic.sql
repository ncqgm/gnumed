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
drop trigger tr_upd_ref_code_tbl_check_backlink on ref.icpc;
drop trigger tr_del_ref_code_tbl_check_backlink on ref.icpc;
\set ON_ERROR_STOP 1


-- UPDATE
create trigger tr_upd_ref_code_tbl_check_backlink
	before update on ref.icpc
		for each row execute procedure ref.trf_upd_ref_code_tbl_check_backlink();

-- DELETE
create trigger tr_del_ref_code_tbl_check_backlink
	before update on ref.icpc
		for each row execute procedure ref.trf_del_ref_code_tbl_check_backlink();

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop index idx_ref_icpc_fk_data_src cascade;
drop index idx_ref_icpc_code_unique_per_system cascade;
drop index idx_ref_icpc_term_unique_per_system cascade;
\set ON_ERROR_STOP 1

create index idx_ref_icpc_fk_data_src on ref.icpc(fk_data_source);
create unique index idx_ref_icpc_code_unique_per_system on ref.icpc(fk_data_source, lower(code));
create unique index idx_ref_icpc_term_unique_per_system on ref.icpc(fk_data_source, lower(code), lower(term));

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
alter table ref.icpc drop constraint icpc_fk_data_source_fkey cascade;
\set ON_ERROR_STOP 1

alter table ref.icpc
	add foreign key (fk_data_source)
		references ref.data_source(pk)
		on update cascade
		on delete restrict;

-- --------------------------------------------------------------
select gm.log_script_insertion('v16-ref-icpc-dynamic.sql', '1.0');

-- ==============================================================