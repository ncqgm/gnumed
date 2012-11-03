-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
comment on table ref.coda is
	'Holds CodA/CodZ codes.';


\unset ON_ERROR_STOP
drop trigger tr_upd_ref_code_tbl_check_backlink on ref.coda;
drop trigger tr_del_ref_code_tbl_check_backlink on ref.coda;
\set ON_ERROR_STOP 1


-- UPDATE
create trigger tr_upd_ref_code_tbl_check_backlink
	before update on ref.coda
		for each row execute procedure ref.trf_upd_ref_code_tbl_check_backlink();

-- DELETE
create trigger tr_del_ref_code_tbl_check_backlink
	before update on ref.coda
		for each row execute procedure ref.trf_del_ref_code_tbl_check_backlink();

-- --------------------------------------------------------------
-- .term
comment on column ref.coda.term is
	'The Reason-For-Encounter like meaning of the code.';

-- --------------------------------------------------------------
-- .icd10_text
comment on column ref.coda.icd10_text is
	'The text of the corresponding ICD-10 code.';


\unset ON_ERROR_STOP
alter table ref.coda drop constraint ref_coda_sane_icd10_text cascade;
\set ON_ERROR_STOP 1

alter table ref.coda
	add constraint chk_ref_coda_sane_icd10_text
		check (gm.is_null_or_blank_string(icd10_text) is False);

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop index idx_ref_coda_fk_data_src cascade;
drop index idx_ref_coda_code_unique_per_system cascade;
drop index idx_ref_coda_term_unique_per_system cascade;
\set ON_ERROR_STOP 1

create index idx_ref_coda_fk_data_src on ref.coda(fk_data_source);
create unique index idx_ref_coda_code_unique_per_system on ref.coda(fk_data_source, lower(code));
create unique index idx_ref_coda_term_unique_per_system on ref.coda(fk_data_source, lower(code), lower(term));

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
alter table ref.coda drop constraint coda_fk_data_source_fkey cascade;
\set ON_ERROR_STOP 1

alter table ref.coda
	add foreign key (fk_data_source)
		references ref.data_source(pk)
		on update cascade
		on delete restrict;

-- --------------------------------------------------------------
grant select on ref.coda to group "gm-public";

-- --------------------------------------------------------------
select gm.log_script_insertion('v18-ref-coda-dynamic.sql', '18.0');
