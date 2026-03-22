-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
comment on table ref.icd9 is
	'Holds ICD-9 codes.';


drop trigger if exists tr_upd_ref_code_tbl_check_backlink on ref.icd9;
drop trigger if exists tr_del_ref_code_tbl_check_backlink on ref.icd9;


-- UPDATE
create trigger tr_upd_ref_code_tbl_check_backlink
	before update on ref.icd9
		for each row execute procedure ref.trf_upd_ref_code_tbl_check_backlink();

-- DELETE
create trigger tr_del_ref_code_tbl_check_backlink
	before update on ref.icd9
		for each row execute procedure ref.trf_del_ref_code_tbl_check_backlink();

-- --------------------------------------------------------------
drop index if exists idx_ref_icd9_fk_data_src cascade;
drop index if exists idx_ref_icd9_code_unique_per_system cascade;
drop index if exists idx_ref_icd9_term_unique_per_system cascade;

create index idx_ref_icd9_fk_data_src on ref.icd9(fk_data_source);
create unique index idx_ref_icd9_code_unique_per_system on ref.icd9(fk_data_source, lower(code));
create unique index idx_ref_icd9_term_unique_per_system on ref.icd9(fk_data_source, lower(code), lower(term));

-- --------------------------------------------------------------
alter table ref.icd9 drop constraint if exists icd9_fk_data_source_fkey cascade;

alter table ref.icd9
	add foreign key (fk_data_source)
		references ref.data_source(pk)
		on update cascade
		on delete restrict;

-- --------------------------------------------------------------
grant select on ref.icd9 to group "gm-public";

-- --------------------------------------------------------------
select gm.log_script_insertion('v16-ref-icd9-dynamic.sql', '16.0');
