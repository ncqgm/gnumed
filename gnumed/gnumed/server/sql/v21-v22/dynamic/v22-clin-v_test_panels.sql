-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1

set check_function_bodies to on;
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
-- view
drop view if exists clin.v_test_panels cascade;


create view clin.v_test_panels as
select
	c_tp.pk as pk_test_panel,
	c_tp.description,
	c_tp.comment,
	c_tp.modified_when,
	c_tp.modified_by,
	coalesce (
		(select array_agg(c_ll2tp.loinc) from clin.lnk_loinc2test_panel c_ll2tp where c_ll2tp.fk_test_panel = c_tp.pk),
		ARRAY[]::text[]
	)
		as loincs,
	ARRAY (
		select row_to_json(test_type_row) from (
			select
				c_ll2tp.loinc,
				c_tt.pk
					as pk_test_type,
				c_tt.fk_meta_test_type
					as pk_meta_test_type
			from clin.lnk_loinc2test_panel c_ll2tp
				inner join clin.test_type c_tt on (c_ll2tp.loinc = c_tt.loinc)
			where
				c_ll2tp.fk_test_panel = c_tp.pk
		) as test_type_row
	)
		as test_types,
	coalesce (
		(select array_agg(c_lc2tp.fk_generic_code) from clin.lnk_code2tst_pnl c_lc2tp where c_lc2tp.fk_item = c_tp.pk),
		ARRAY[]::integer[]
	)
		as pk_generic_codes,
	c_tp.row_version,
	c_tp.xmin as xmin_test_panel
from
	clin.test_panel c_tp
;


grant select on clin.v_test_panels TO GROUP "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-clin-v_test_panels.sql', '22.0');
