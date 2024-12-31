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
		coalesce(r_v.atc, r_dp.atc_code)
			as atc,

		r_v.is_live,
		r_v.min_age,
		r_v.max_age,
		r_v.comment,

		ARRAY (
			select row_to_json(indication_row) from (
				select
					r_vi.target
						as indication,
					_(r_vi.target)
						as l10n_indication,
					r_vi.atc
						as atc_indication,
					r_vi.pk
						as pk_indication
				from
					ref.lnk_indic2vaccine r_li2v
						inner join ref.vacc_indication r_vi on (r_li2v.fk_indication = r_vi.pk)
				where
					r_li2v.fk_vaccine = r_v.pk
			) as indication_row
		) as indications,

		r_dp.external_code,
		r_dp.external_code_type,

		r_v.fk_drug_product
			as pk_drug_product,

		r_dp.fk_data_source
			as pk_data_source,

		r_v.xmin
			as xmin_vaccine

	from
		ref.vaccine r_v
			left join ref.drug_product r_dp on (r_v.fk_drug_product = r_dp.pk)
;

comment on view ref.v_vaccines is
	'A list of vaccines.';

grant select on ref.v_vaccines to group "gm-public";

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-ref-v_vaccines.sql', '23.0');
