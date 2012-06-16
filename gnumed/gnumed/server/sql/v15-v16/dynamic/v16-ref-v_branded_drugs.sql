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
drop view ref.v_branded_drugs cascade;
\set ON_ERROR_STOP 1

create view ref.v_branded_drugs as

select
	r_bd.pk
		as pk_brand,
	r_bd.description
		as brand,
	r_bd.preparation
		as preparation,
	r_bd.atc_code
		as atc,
	r_bd.external_code
		as external_code,
	r_bd.external_code_type
		as external_code_type,
	r_bd.is_fake
		as is_fake_brand,

	(select array_agg(r_cs.description || '::' || r_cs.amount || '::' || r_cs.unit || '::' || coalesce(r_cs.atc_code, ''))
	 from
	 	ref.lnk_substance2brand r_ls2b
	 		inner join ref.consumable_substance r_cs on (r_ls2b.fk_substance = r_cs.pk)
	 where r_ls2b.fk_brand = r_bd.pk
	) as components,

	(select array_agg(r_ls2b.pk)
	 from ref.lnk_substance2brand r_ls2b
	 where r_ls2b.fk_brand = r_bd.pk
	) as pk_components,

	(select array_agg(r_ls2b.fk_substance)
	 from ref.lnk_substance2brand r_ls2b
	 where r_ls2b.fk_brand = r_bd.pk
	) as pk_substances,

	r_bd.fk_data_source
		as pk_data_source,
	r_bd.xmin
		as xmin_branded_drug
from
	ref.branded_drug r_bd
;


grant select on
	ref.v_branded_drugs
to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v16-ref-v_branded_drugs.sql', '16.0');
