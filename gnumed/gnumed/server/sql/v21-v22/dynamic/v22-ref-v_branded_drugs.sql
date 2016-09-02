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
drop view if exists ref.v_branded_drugs cascade;

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

	(select array_agg(r_s.description || '::' || r_d.amount || '::' || r_d.unit || '::' || coalesce(r_d.dose_unit, _('delivery unit of') || ' ' || r_bd.preparation) || '::' || coalesce(r_s.atc, ''))
	 from
	 	ref.lnk_dose2drug r_ld2d
			inner join ref.dose r_d on (r_ld2d.fk_dose = r_d.pk)
				inner join ref.substance r_s on (r_d.fk_substance = r_s.pk)
	 where
	 	r_ld2d.fk_brand = r_bd.pk
	) as components,

	(select array_agg(r_ld2d.pk)
	 from ref.lnk_dose2drug r_ld2d
	 where r_ld2d.fk_brand = r_bd.pk
	) as pk_components,

	(select array_agg(r_ld2d.fk_dose)
	 from ref.lnk_dose2drug r_ld2d
	 where r_ld2d.fk_brand = r_bd.pk
	) as pk_doses,

	(select array_agg(r_d.fk_substance)
	 from
	 	ref.lnk_dose2drug r_ld2d
			inner join ref.dose r_d on (r_ld2d.fk_dose = r_d.pk)
	 where r_ld2d.fk_brand = r_bd.pk
	) as pk_substances,

	r_bd.fk_data_source
		as pk_data_source,
	r_bd.xmin
		as xmin_branded_drug
from
	ref.branded_drug r_bd
--		inner join ref.lnk_dose2drug r_ld2d on (r_ld2d.fk_brand = r_bd.pk)
--			inner join ref.dose r_d on (r_ld2d.fk_dose = r_d.pk)
--				inner join ref.substance r_s on (r_d.fk_substance = r_s.pk)
;

grant select on ref.v_branded_drugs to group "gm-doctors";


select i18n.upd_tx('de', 'delivery unit of', 'Anwendungsmenge von');

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-ref-v_branded_drugs.sql', '22.0');
