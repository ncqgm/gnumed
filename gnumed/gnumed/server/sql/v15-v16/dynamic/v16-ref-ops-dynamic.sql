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


-- UPDATE
create trigger tr_upd_ref_code_tbl_check_backlink
	before update on ref.ops
		for each row execute procedure ref.trf_upd_ref_code_tbl_check_backlink();

-- DELETE
create trigger tr_del_ref_code_tbl_check_backlink
	before update on ref.ops
		for each row execute procedure ref.trf_del_ref_code_tbl_check_backlink();

-- --------------------------------------------------------------
grant select on ref.ops to group "gm-public";

-- --------------------------------------------------------------
select gm.log_script_insertion('v16-ref-ops-dynamic.sql', '16.0');
