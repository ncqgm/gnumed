-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
drop view if exists clin.v_test_types4test_panel cascade;

create view clin.v_test_types4test_panel as
select
	c_tp.pk
		as pk_test_panel,
	c_tt.pk
		as pk_test_type,
	c_tp.description
		as test_panel,
	c_tt.name
		as test_type,
	c_tt.abbrev
		as test_abbrev,
	c_tt.loinc
		as loinc,

	c_tp.comment
		as comment_panel,
	c_tt.comment
		as comment_test_type,
	c_tt.reference_unit
		as reference_unit,

	c_tt.fk_meta_test_type
		as pk_meta_test_type,
	c_ll2tp.pk
		as pk_lnk_loinc2test_panel
	-- c_ll2tp.xmin as xmin_lnk_loinc2substance
from
	clin.test_panel c_tp
		inner join clin.lnk_loinc2test_panel c_ll2tp on (c_ll2tp.fk_test_panel = c_tp.pk)
			inner join clin.test_type c_tt on (c_tt.loinc = c_ll2tp.loinc)
;


comment on view clin.v_test_types4test_panel is 'Shows test types linked to test panels via their LOINC code.';


grant select on clin.v_test_types4test_panel to "gm-public";

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-clin-v_test_types4test_panel.sql', '22.0');
