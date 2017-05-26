-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
update ref.vaccine set
	is_live = True
where
	is_live IS NULL;

alter table ref.vaccine
	alter column is_live
		set not null;

-- --------------------------------------------------------------
drop view if exists ref.v_vaccines cascade;

create view ref.v_vaccines as

	select
		r_v.pk
			as pk_vaccine,

		r_dp.description
			as vaccine,
		r_dp.preparation
			as preparation,
		_(r_dp.preparation)
			as l10n_preparation,
		r_dp.atc_code
			as atc_code,
		r_dp.is_fake
			as is_fake_vaccine,

		r_vr.abbreviation
			as route_abbreviation,
		r_vr.description
			as route_description,

		r_v.is_live,
		r_v.min_age,
		r_v.max_age,
		r_v.comment,

		ARRAY (
			select row_to_json(indication_row) from (
				select
					_(r_s.atc || '-target', 'en')
						as indication,
					case
						when _(r_s.atc || '-target') = (r_s.atc || '-target') then _(r_s.atc || '-target', 'en')
						else _(r_s.atc || '-target')
					end
						as l10n_indication,
					r_s.atc
						as atc_indication
				from
					ref.lnk_dose2drug r_ld2d
						inner join ref.dose r_d on (r_d.pk = r_ld2d.fk_dose)
							inner join ref.substance r_s on (r_d.fk_substance = r_s.pk)
				where
					r_ld2d.fk_drug_product = r_dp.pk
			) as indication_row
		) as indications,

		r_dp.external_code,
		r_dp.external_code_type,

		r_v.id_route
			as pk_route,
		r_v.fk_drug_product
			as pk_drug_product,

		r_dp.fk_data_source
			as pk_data_source,

		r_v.xmin
			as xmin_vaccine

	from
		ref.vaccine r_v
			join ref.drug_product r_dp on (r_v.fk_drug_product = r_dp.pk)
				left outer join ref.vacc_route r_vr on (r_v.id_route = r_vr.id)

;

comment on view ref.v_vaccines is
	'A list of vaccines.';

grant select on ref.v_vaccines to group "gm-public";

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-ref-v_vaccines.sql', '22.0');
