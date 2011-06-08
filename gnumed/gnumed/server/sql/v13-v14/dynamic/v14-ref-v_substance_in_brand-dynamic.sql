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
drop view ref.v_substance_in_brand cascade;
\set ON_ERROR_STOP 1

create view ref.v_substance_in_brand as

select
	rsib.pk
		as pk_substance_in_brand,
	rsib.description
		as substance,
	rsib.atc_code
		as atc_substance,
	rbd.description
		as brand,
	rbd.preparation
		as preparation,
	rbd.atc_code
		as atc_brand,
	rbd.external_code
		as external_code_brand,
	rbd.external_code_type
		as external_code_type_brand,
	rbd.is_fake
		as is_fake_brand,

	rbd.fk_data_source
		as pk_data_source,
	rsib.fk_brand
		as pk_brand
from
	ref.substance_in_brand rsib
		left join ref.branded_drug rbd on (rsib.fk_brand = rbd.pk)
;


grant select on
	ref.v_substance_in_brand
to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v12-ref-substance_in_brand-dynamic.sql,v $', '$Revision: 1.2 $');

-- ==============================================================
