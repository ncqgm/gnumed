-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
drop view if exists clin.v_vaccines cascade;


create view clin.v_vaccines as

	select
		c_v.pk
			as pk_vaccine,

		r_dp.description
			as vaccine,
		r_dp.preparation
			as preparation,
		r_dp.atc_code
			as atc_code,
		r_dp.is_fake
			as is_fake_vaccine,

		c_vr.abbreviation
			as route_abbreviation,
		c_vr.description
			as route_description,

		c_v.is_live,
		c_v.min_age,
		c_v.max_age,
		c_v.comment,

		(select array_agg(description)
		 from
			clin.lnk_vaccine2inds clvi
				join clin.vacc_indication c_vi on (clvi.fk_indication = c_vi.id)
		 where
			clvi.fk_vaccine = c_v.pk
		) as indications,

		(select array_agg(_(description))
		 from
			clin.lnk_vaccine2inds clvi
				join clin.vacc_indication c_vi on (clvi.fk_indication = c_vi.id)
		 where
			clvi.fk_vaccine = c_v.pk
		) as l10n_indications,

		r_dp.external_code,
		r_dp.external_code_type,

		(select array_agg(clvi.fk_indication)
		 from
			clin.lnk_vaccine2inds clvi
				join clin.vacc_indication c_vi on (clvi.fk_indication = c_vi.id)
		 where
			clvi.fk_vaccine = c_v.pk
		) as pk_indications,

		c_v.id_route
			as pk_route,
		c_v.fk_drug_product
			as pk_drug_product,

		r_dp.fk_data_source
			as pk_data_source,

		c_v.xmin
			as xmin_vaccine

	from
		clin.vaccine c_v
			join ref.drug_product r_dp on (c_v.fk_drug_product = r_dp.pk)
				left outer join clin.vacc_route c_vr on (c_v.id_route = c_vr.id)

;

comment on view clin.v_vaccines is
	'A list of vaccines.';

grant select on clin.v_vaccines to group "gm-public";

-- --------------------------------------------------------------
drop view if exists clin.v_indications4vaccine cascade;

create view clin.v_indications4vaccine as

	select
		c_v.pk
			as pk_vaccine,

		r_dp.description
			as vaccine,
		r_dp.preparation
			as preparation,
		r_dp.atc_code
			as atc_code,
		r_dp.is_fake
			as is_fake_vaccine,

		c_vr.abbreviation
			as route_abbreviation,
		c_vr.description
			as route_description,

		c_v.is_live,
		c_v.min_age,
		c_v.max_age,
		c_v.comment,

		c_vi.description
			as indication,
		_(c_vi.description)
			as l10n_indication,
		c_vi.atcs_single_indication
			as atcs_single_indication,
		c_vi.atcs_combi_indication
			as atcs_combi_indication,

		r_dp.external_code,
		r_dp.external_code_type,

		(select array_agg(c_vi2.description)
		 from
			clin.lnk_vaccine2inds clv2i_2
				join clin.vacc_indication c_vi2 on (clv2i_2.fk_indication = c_vi2.id)
		 where
			clv2i_2.fk_vaccine = c_v.pk
		) as indications,

		(select array_agg(_(c_vi2.description))
		 from
			clin.lnk_vaccine2inds clv2i_2
				join clin.vacc_indication c_vi2 on (clv2i_2.fk_indication = c_vi2.id)
		 where
			clv2i_2.fk_vaccine = c_v.pk
		) as l10n_indications,

		(select array_agg(clv2i_2.fk_indication)
		 from
			clin.lnk_vaccine2inds clv2i_2
				join clin.vacc_indication c_vi2 on (clv2i_2.fk_indication = c_vi2.id)
		 where
			clv2i_2.fk_vaccine = c_v.pk
		) as pk_indications,

		c_v.id_route
			as pk_route,
		c_v.fk_drug_product
			as pk_drug_product,
		r_dp.fk_data_source
			as pk_data_source,
		c_vi.id
			as pk_indication,
		c_v.xmin
			as xmin_vaccine

	from
		clin.vaccine c_v
			left outer join clin.vacc_route c_vr on (c_vr.id = c_v.id_route)
				join ref.drug_product r_dp on (r_dp.pk = c_v.fk_drug_product)
					join clin.lnk_vaccine2inds clv2i on (clv2i.fk_vaccine = c_v.pk)
						join clin.vacc_indication c_vi on (c_vi.id = clv2i.fk_indication)

;


comment on view clin.v_indications4vaccine is
	'Denormalizes indications per vaccine.';

grant select on clin.v_indications4vaccine to group "gm-public";

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-clin-v_vaccines.sql', '22.0');
