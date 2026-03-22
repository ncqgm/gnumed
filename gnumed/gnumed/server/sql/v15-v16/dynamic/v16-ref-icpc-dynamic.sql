-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
drop trigger if exists tr_upd_ref_code_tbl_check_backlink on ref.icpc;
drop trigger if exists tr_del_ref_code_tbl_check_backlink on ref.icpc;


-- UPDATE
create trigger tr_upd_ref_code_tbl_check_backlink
	before update on ref.icpc
		for each row execute procedure ref.trf_upd_ref_code_tbl_check_backlink();

-- DELETE
create trigger tr_del_ref_code_tbl_check_backlink
	before update on ref.icpc
		for each row execute procedure ref.trf_del_ref_code_tbl_check_backlink();

-- --------------------------------------------------------------
drop index if exists idx_ref_icpc_fk_data_src cascade;
drop index if exists idx_ref_icpc_code_unique_per_system cascade;
drop index if exists idx_ref_icpc_term_unique_per_system cascade;

create index idx_ref_icpc_fk_data_src on ref.icpc(fk_data_source);
create unique index idx_ref_icpc_code_unique_per_system on ref.icpc(fk_data_source, lower(code));
create unique index idx_ref_icpc_term_unique_per_system on ref.icpc(fk_data_source, lower(code), lower(term));

-- --------------------------------------------------------------
alter table ref.icpc drop constraint if exists icpc_fk_data_source_fkey cascade;

alter table ref.icpc
	add foreign key (fk_data_source)
		references ref.data_source(pk)
		on update cascade
		on delete restrict;

-- --------------------------------------------------------------
select gm.log_script_insertion('v16-ref-icpc-dynamic.sql', '1.0');

-- ==============================================================