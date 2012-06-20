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
\unset ON_ERROR_STOP
drop view clin.v_linked_codes cascade;
\set ON_ERROR_STOP 1


create view clin.v_linked_codes as
select
	c_lc2ir.fk_item
		as pk_item,
	c_lc2ir.tableoid::regclass
		as item_table,

	r_csr.code || coalesce(c_lc2ir.code_modifier, '')
		as code,
	r_csr.code
		as base_code,
	c_lc2ir.code_modifier,
	r_csr.term,
	r_ds.name_long,
	r_ds.name_short,
	r_ds.version,
	r_ds.lang,

	r_csr.tableoid::regclass
		as code_table,
	r_csr.pk_coding_system
		as pk_generic_code,
	r_csr.fk_data_source
		as pk_data_source,
	c_lc2ir.pk_lnk_code2item
from
	clin.lnk_code2item_root c_lc2ir
		join ref.coding_system_root r_csr on r_csr.pk_coding_system = c_lc2ir.fk_generic_code
			join ref.data_source r_ds on r_ds.pk = r_csr.fk_data_source
;


comment on view clin.v_linked_codes is 'Denormalized codes linked to EMR structures.';


grant select on clin.v_linked_codes to group "gm-public";

-- --------------------------------------------------------------
select gm.log_script_insertion('v16-clin-v_linked_codes.sql', 'Revision 1');

-- ==============================================================
