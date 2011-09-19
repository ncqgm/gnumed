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


\unset ON_ERROR_STOP
drop trigger tr_upd_ref_code_tbl_check_backlink on ref.icd10;
drop trigger tr_del_ref_code_tbl_check_backlink on ref.icd10;
\set ON_ERROR_STOP 1


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


\unset ON_ERROR_STOP
alter table ref.icd10 drop contraint ref_icd10_sane_star_code cascade;
\set ON_ERROR_STOP 1

alter table ref.icd10
	add constraint chk_ref_icd10_sane_star_code
		check (gm.is_null_or_non_empty_string(star_code) is True);

-- --------------------------------------------------------------
-- .aux_code
comment on column ref.icd10.aux_code is
	'The auxiliary code which needs to be combined with the primary code to define the term.';


\unset ON_ERROR_STOP
alter table ref.icd10 drop contraint ref_icd10_sane_aux_code cascade;
\set ON_ERROR_STOP 1

alter table ref.icd10
	add constraint chk_ref_icd10_sane_aux_code
		check (gm.is_null_or_non_empty_string(aux_code) is True);

-- --------------------------------------------------------------
grant select on ref.icd10 to group "gm-public";

-- --------------------------------------------------------------
select gm.log_script_insertion('v16-ref-icd10-dynamic.sql', '16.0');
