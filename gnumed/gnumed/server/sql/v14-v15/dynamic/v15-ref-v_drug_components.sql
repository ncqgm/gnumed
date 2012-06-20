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
drop view ref.v_drug_components cascade;
\set ON_ERROR_STOP 1

create view ref.v_drug_components as

select
	r_ls2b.pk
		as pk_component,
	r_bd.description
		as brand,
	r_cs.description
		as substance,
	r_cs.amount
		as amount,
	r_cs.unit
		as unit,
	r_bd.preparation
		as preparation,
	r_cs.atc_code
		as atc_substance,
	r_bd.atc_code
		as atc_brand,
	r_bd.external_code
		as external_code_brand,
	r_bd.external_code_type
		as external_code_type_brand,
	r_bd.is_fake
		as is_fake_brand,
	exists (
		select 1 from clin.substance_intake c_si
		where c_si.fk_drug_component = r_ls2b.pk
		limit 1
	)	as is_in_use,
	r_ls2b.fk_brand
		as pk_brand,
	r_cs.pk
		as pk_consumable_substance,
	r_bd.fk_data_source
		as pk_data_source,
	r_ls2b.xmin
		as xmin_lnk_substance2brand
from
	ref.consumable_substance r_cs
		inner join ref.lnk_substance2brand r_ls2b on (r_cs.pk = r_ls2b.fk_substance)
			left join ref.branded_drug r_bd on (r_ls2b.fk_brand = r_bd.pk)
;


grant select on
	ref.v_drug_components
to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v15-ref-v_drug_components.sql', 'Revision: 1.1');

-- ==============================================================
