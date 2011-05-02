-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view ref.v_generic_coding_system cascade;
\set ON_ERROR_STOP 1


create view ref.v_generic_coding_system as
select
	r_csr.pk_coding_system
		as pk_coding_system,

	r_csr.code,
	r_csr.term,
	r_ds.name_long,
	r_ds.name_short,
	r_ds.version,
	r_ds.lang,

	r_csr.tableoid::regclass
		as code_table,
	r_csr.fk_data_source
		as pk_data_source
from
	ref.coding_system_root r_csr
		join ref.data_source r_ds on r_ds.pk = r_csr.fk_data_source
;


comment on view dem.v_staff is 'Denormalized generic codes.';


grant select on dem.v_staff to group "gm-public";

-- --------------------------------------------------------------
select gm.log_script_insertion('v16-ref-v_generic_coding_system.sql', 'Revision 1');

-- ==============================================================
