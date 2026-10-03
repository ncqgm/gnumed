-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1
set default_transaction_read_only to off;

-- --------------------------------------------------------------
drop view if exists ref.v_indications4vaccine cascade;

create view ref.v_indications4vaccine as

	select
		r_v.pk
			as pk_vaccine,

		r_vi.target
			as indication,
		_(r_vi.target)
			as l10n_indication,
		r_vi.pk
			as pk_indication,
		r_vi.atc
			as atc_indication,

		r_v.brandname
			as vaccine,
		r_v.atc
			as atc_vaccine,

		r_v.is_live,
		r_v.min_age,
		r_v.max_age,
		r_v.comment,
		ARRAY (
			select row_to_json(indication_row) from (
				select
					r_vi_2.target
						as indication,
					_(r_vi_2.target)
						as l10n_indication,
					r_vi_2.atc
						as atc_indication
				from
					ref.lnk_indic2vaccine r_li2v_2
						inner join ref.vacc_indication r_vi_2 on (r_vi_2.pk = r_li2v_2.fk_indication)
				where
					r_li2v_2.fk_vaccine = r_v.pk
			) as indication_row
		) as all_indications,
		r_v.xmin
			as xmin_vaccine
	from
		ref.lnk_indic2vaccine r_li2v
			join ref.vaccine r_v on (r_v.pk = r_li2v.fk_vaccine)
			join ref.vacc_indication r_vi on (r_vi.pk = r_li2v.fk_indication)
;


comment on view ref.v_indications4vaccine is
	'Denormalizes indications per vaccine.';

grant select on ref.v_indications4vaccine to group "gm-public";

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-ref-v_indications4vaccine.sql', '23.0');
