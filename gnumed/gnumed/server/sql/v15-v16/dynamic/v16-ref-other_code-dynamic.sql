-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
comment on table ref.other_code is
	'Holds codes from "other" coding systems for which no specific tables exist just yet.';


\unset ON_ERROR_STOP
drop trigger tr_upd_ref_code_tbl_check_backlink on ref.other_code;
drop trigger tr_del_ref_code_tbl_check_backlink on ref.other_code;
\set ON_ERROR_STOP 1


-- UPDATE
create trigger tr_upd_ref_code_tbl_check_backlink
	before update on ref.other_code
		for each row execute procedure ref.trf_upd_ref_code_tbl_check_backlink();

-- DELETE
create trigger tr_del_ref_code_tbl_check_backlink
	before update on ref.other_code
		for each row execute procedure ref.trf_del_ref_code_tbl_check_backlink();

-- --------------------------------------------------------------
grant select on ref.other_code to group "gm-public";

-- --------------------------------------------------------------
select gm.log_script_insertion('v16-ref-other_code-dynamic.sql', '16.0');
