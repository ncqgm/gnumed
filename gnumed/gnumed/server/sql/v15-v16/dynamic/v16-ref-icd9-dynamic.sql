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


\unset ON_ERROR_STOP
drop trigger tr_upd_ref_code_tbl_check_backlink on ref.icd9;
drop trigger tr_del_ref_code_tbl_check_backlink on ref.icd9;
\set ON_ERROR_STOP 1


-- UPDATE
create trigger tr_upd_ref_code_tbl_check_backlink
	before update on ref.icd9
		for each row execute procedure ref.trf_upd_ref_code_tbl_check_backlink();

-- DELETE
create trigger tr_del_ref_code_tbl_check_backlink
	before update on ref.icd9
		for each row execute procedure ref.trf_del_ref_code_tbl_check_backlink();

-- --------------------------------------------------------------
grant select on ref.icd9 to group "gm-public";

-- --------------------------------------------------------------
select gm.log_script_insertion('v16-ref-icd9-dynamic.sql', '16.0');
