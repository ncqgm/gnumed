-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
comment on table ref.icd10 is
	'Holds ICD-10 codes.';


drop trigger if exists tr_upd_ref_code_tbl_check_backlink on ref.icd10;
drop trigger if exists tr_del_ref_code_tbl_check_backlink on ref.icd10;


-- UPDATE
create trigger tr_upd_ref_code_tbl_check_backlink
	before update on ref.icd10
		for each row execute procedure ref.trf_upd_ref_code_tbl_check_backlink();

-- DELETE
create trigger tr_del_ref_code_tbl_check_backlink
	before update on ref.icd10
		for each row execute procedure ref.trf_del_ref_code_tbl_check_backlink();

-- --------------------------------------------------------------
-- .star_code
comment on column ref.icd10.star_code is
	'The star code which needs to be combined with the primary code to define the term.';


alter table ref.icd10 drop constraint if exists ref_icd10_sane_star_code cascade;

alter table ref.icd10
	add constraint chk_ref_icd10_sane_star_code
		check (gm.is_null_or_non_empty_string(star_code) is True);

-- --------------------------------------------------------------
-- .aux_code
comment on column ref.icd10.aux_code is
	'The auxiliary code which needs to be combined with the primary code to define the term.';


alter table ref.icd10 drop constraint if exists ref_icd10_sane_aux_code cascade;

alter table ref.icd10
	add constraint chk_ref_icd10_sane_aux_code
		check (gm.is_null_or_non_empty_string(aux_code) is True);

-- --------------------------------------------------------------
drop index if exists idx_ref_icd10_fk_data_src cascade;
drop index if exists idx_ref_icd10_code_unique_per_system cascade;
drop index if exists idx_ref_icd10_term_unique_per_system cascade;

create index idx_ref_icd10_fk_data_src on ref.icd10(fk_data_source);
create unique index idx_ref_icd10_code_unique_per_system on ref.icd10(fk_data_source, lower(code));
create unique index idx_ref_icd10_term_unique_per_system on ref.icd10(fk_data_source, lower(code), lower(term));

-- --------------------------------------------------------------
alter table ref.icd10 drop constraint if exists icd10_fk_data_source_fkey cascade;

alter table ref.icd10
	add foreign key (fk_data_source)
		references ref.data_source(pk)
		on update cascade
		on delete restrict;

-- --------------------------------------------------------------
grant select on ref.icd10 to group "gm-public";

-- --------------------------------------------------------------
select gm.log_script_insertion('v16-ref-icd10-dynamic.sql', '16.0');
