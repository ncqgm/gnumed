-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
comment on table ref.ops is
	'Holds OPS (German ICPM-CM) codes.';


\unset ON_ERROR_STOP
drop trigger tr_upd_ref_code_tbl_check_backlink on ref.ops;
drop trigger tr_del_ref_code_tbl_check_backlink on ref.ops;
\set ON_ERROR_STOP 1


-- UPDATE
create trigger tr_upd_ref_code_tbl_check_backlink
	before update on ref.ops
		for each row execute procedure ref.trf_upd_ref_code_tbl_check_backlink();

-- DELETE
create trigger tr_del_ref_code_tbl_check_backlink
	before update on ref.ops
		for each row execute procedure ref.trf_del_ref_code_tbl_check_backlink();

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop index idx_ref_ops_fk_data_src cascade;
drop index idx_ref_ops_code_unique_per_system cascade;
drop index idx_ref_ops_term_unique_per_system cascade;
\set ON_ERROR_STOP 1

create index idx_ref_ops_fk_data_src on ref.ops(fk_data_source);
create unique index idx_ref_ops_code_unique_per_system on ref.ops(fk_data_source, lower(code));
create unique index idx_ref_ops_term_unique_per_system on ref.ops(fk_data_source, lower(code), lower(term));

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
alter table ref.ops drop constraint ops_fk_data_source_fkey cascade;
\set ON_ERROR_STOP 1

alter table ref.ops
	add foreign key (fk_data_source)
		references ref.data_source(pk)
		on update cascade
		on delete restrict;

-- --------------------------------------------------------------
grant select on ref.ops to group "gm-public";

-- --------------------------------------------------------------
select gm.log_script_insertion('v16-ref-ops-dynamic.sql', '16.0');
