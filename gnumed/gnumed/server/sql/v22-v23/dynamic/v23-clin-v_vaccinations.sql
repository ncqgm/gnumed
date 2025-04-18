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
drop view if exists clin.v_vaccinations cascade;

create view clin.v_vaccinations as
select
	c_enc.fk_patient
		as pk_patient,
	c_shot.pk
		as pk_vaccination,
	c_shot.clin_when
		as date_given,
	now() - c_shot.clin_when
		as interval_since_given,
	r_dp.description
		as vaccine,

	ARRAY (
		select row_to_json(indication_row) from (
			select
				r_vi.target
					as indication,
				_(r_vi.target)
					as l10n_indication,
				r_vi.atc
					as atc_indication
			from
				ref.lnk_indic2vaccine r_li2v
					inner join ref.vacc_indication r_vi on (r_vi.pk = r_li2v.fk_indication)
			where
				r_li2v.fk_vaccine = r_v.pk
		) as indication_row
	) as indications,

	c_shot.site
		as site,
	c_shot.batch_no
		as batch_no,
	c_shot.reaction
		as reaction,
	c_shot.narrative
		as comment,
	c_shot.soap_cat
		as soap_cat,

	c_shot.modified_when
		as modified_when,
	c_shot.modified_by
		as modified_by,
	c_shot.row_version
		as row_version,
	c_shot.fk_vaccine
		as pk_vaccine,
	c_shot.fk_provider
		as pk_provider,
	c_shot.fk_encounter
		as pk_encounter,
	c_shot.fk_episode
		as pk_episode,

	c_shot.xmin
		as xmin_vaccination
from
	clin.vaccination c_shot
		join clin.encounter c_enc on (c_enc.pk = c_shot.fk_encounter)
		join ref.vaccine r_v on (r_v.pk = c_shot.fk_vaccine)
			left join ref.drug_product r_dp on (r_v.fk_drug_product = r_dp.pk)

;

comment on view clin.v_vaccinations is
	'Lists vaccinations for patients';

grant select on clin.v_vaccinations to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-clin-v_vaccinations.sql', '23.0');
